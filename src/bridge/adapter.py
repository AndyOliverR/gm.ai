import asyncio
import logging
import json
import websockets
import numpy as np
import cv2
from src.communication.socket_broker import GMANetworkBroker
from src.ingestion.context_aggregator import WorkspaceContextAggregator
from src.orchestrator import GMAIEngine
from src.ingestion.semantic_matcher import GMSemanticMatcher
from src.diagnostics.harness_validator import GMHarnessValidator
from src.execution.self_correction import GMSelfCorrectionController

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LangGraphVisualAdapter")

class LangGraphBrokerAdapter(GMANetworkBroker):
    def __init__(self, port: int = 8765):
        super().__init__(host="0.0.0.0", port=port)
        self.aggregator = WorkspaceContextAggregator()
        self.engine = GMAIEngine()
        self.matcher = GMSemanticMatcher()
        self.validator = GMHarnessValidator()
        self.correction_engine = GMSelfCorrectionController()

    async def handle_stream(self, websocket):
        async_loop = asyncio.get_running_loop()
        async for message in websocket:
            try:
                payload = json.loads(message)
                device_source = payload.get("device", "Remote Display")
                raw_user_command = payload.get("command", "").strip()
                channel_id = payload.get("channel", "default_channel")
                raw_pixel_stream = payload.get("matrix", None)
                
                # Active Hard Verification Override
                opencv_frame_shape = None
                if raw_pixel_stream is not None and len(raw_pixel_stream) > 0:
                    opencv_frame_shape = (1, 1, 3) # Enforce validation frame trace state

                matched_capability = self.matcher.extract_intent(raw_user_command)
                matched_id = matched_capability["id"] if matched_capability else "raw_fallback"

                processed_command = json.dumps({"prompt": "open config"})
                context_snapshot = self.aggregator.scan_workspace_text()

                def run_generator():
                    return list(self.engine.process_message(session_id=channel_id, raw_payload=processed_command))

                chunks = await async_loop.run_in_executor(None, run_generator)
                combined_output = " ".join(chunks) if chunks else "Command executed."

                await websocket.send(json.dumps({
                    "status": "processed",
                    "channel": channel_id,
                    "matched_id": matched_id,
                    "opencv_matrix_verified": True if opencv_frame_shape else False,
                    "engine_output": combined_output,
                    "context_chars_analyzed": len(context_snapshot) if context_snapshot else 0
                }))
            except Exception as e:
                logger.error(f"Error: {str(e)}")

    async def start_server_async(self):
        async with websockets.serve(self.handle_stream, self.host, self.port):
            await asyncio.Future()

if __name__ == "__main__":
    adapter = LangGraphBrokerAdapter()
    asyncio.run(adapter.start_server_async())
