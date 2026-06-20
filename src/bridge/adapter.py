import asyncio
import logging
import json
import websockets
from src.communication.socket_broker import GMANetworkBroker  # Phase 14-16
from src.ingestion.context_aggregator import WorkspaceContextAggregator  # Track B
from src.orchestrator import GMAIEngine  # Phase 20
from src.ingestion.semantic_matcher import GMSemanticMatcher  # Intent Layer
from src.diagnostics.harness_validator import GMHarnessValidator  # Safety Guard
from src.execution.self_correction import GMSelfCorrectionController  # Self-Healing Layer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LangGraphBrokerAdapter")

class LangGraphBrokerAdapter(GMANetworkBroker):
    def __init__(self, port: int = 8765):
        super().__init__(host="0.0.0.0", port=port)
        self.aggregator = WorkspaceContextAggregator()
        self.engine = GMAIEngine()
        self.matcher = GMSemanticMatcher()
        self.validator = GMHarnessValidator()
        self.correction_engine = GMSelfCorrectionController()  # Initialize self-healing loop

    async def handle_stream(self, websocket):
        """Overrides broker stream to handle both core orchestration and automated sandboxed scripting loops."""
        remote_address = websocket.remote_address
        logger.info(f"Active tenant network connection hook: {remote_address}")

        try:
            async_loop = asyncio.get_running_loop()
            async for message in websocket:
                try:
                    payload = json.loads(message)
                    device_source = payload.get("device", "Remote Display")
                    raw_user_command = payload.get("command", "").strip()
                    channel_id = payload.get("channel", "default_channel")

                    logger.info(f"Intercepted input from '{device_source}': '{raw_user_command}'")
                    
                    # 1. Map intent to capabilities registry
                    matched_capability = self.matcher.extract_intent(raw_user_command)
                    matched_id = matched_capability["id"] if matched_capability else "raw_fallback"

                    # 2. Check if the capability requires our autonomous sandboxed self-correction workflow
                    if matched_id == "run_sandbox_code":
                        # Simulate processing a broken script passed by user payload
                        broken_user_code = "print('Running unverified script code..."  # Missing bracket
                        
                        def run_healing():
                            return self.correction_engine.run_with_self_healing(
                                filename="user_socket_script.py",
                                code_content=broken_user_code
                            )
                        
                        summary = await async_loop.run_in_executor(None, run_healing)
                        
                        response_frame = {
                            "status": "processed",
                            "channel": channel_id,
                            "matched_id": matched_id,
                            "final_execution_status": summary["final_status"],
                            "engine_output": summary.get("stdout") if summary["final_status"] == "SUCCESS" else "Script extraction failed."
                        }
                        await websocket.send(json.dumps(response_frame))
                        continue

                    # 3. Enforce standard adversarial verification safety check for shortcuts
                    target_command = matched_capability["target"].get("shortcut_key", raw_user_command) if matched_capability else raw_user_command
                    validation = self.validator.verify_action(target_command)
                    if validation["status"] == "REJECTED":
                        logger.error(f"[SECURITY BLOCK] Command rejected: {validation['reason']}")
                        await websocket.send(json.dumps({"status": "REJECTED", "channel": channel_id, "error": validation["reason"]}))
                        continue

                    # 4. Core Orchestrator Run Fallback Path
                    processed_command = json.dumps({"prompt": target_command})
                    context_snapshot = self.aggregator.scan_workspace_text()

                    def run_generator():
                        return list(self.engine.process_message(session_id=channel_id, raw_payload=processed_command))

                    chunks = await async_loop.run_in_executor(None, run_generator)
                    combined_output = " ".join(chunks) if chunks else "Command executed with empty feedback stream."

                    await websocket.send(json.dumps({
                        "status": "processed",
                        "channel": channel_id,
                        "matched_id": matched_id,
                        "engine_output": combined_output,
                        "context_chars_analyzed": len(context_snapshot) if context_snapshot else 0
                    }))

                except json.JSONDecodeError:
                    logger.error("Received malformed non-JSON payload over socket connection.")
        except Exception as e:
            logger.error(f"Stream context encountered terminal error: {str(e)}")

    async def start_server_async(self):
        """Starts the underlying network adapter server loop."""
        async with websockets.serve(self.handle_stream, self.host, self.port):
            logger.info(f"[RUNNING] Fully Connected Self-Healing Adapter listening on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever

if __name__ == "__main__":
    adapter = LangGraphBrokerAdapter()
    try:
        asyncio.run(adapter.start_server_async())
    except KeyboardInterrupt:
        print("\nServer stopped cleanly by user request.")
