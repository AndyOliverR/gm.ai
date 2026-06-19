import sys
import os
import asyncio
import json

# Dynamically ensure top-level project module access
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

try:
    import websockets
except ImportError:
    raise ImportError("Dependency missing. Please run: pip install websockets")

from app import gm_engine
from src.execution.audit_ledger import GMAIAuditLedger
# Import the newly verified Phase 17 Background Daemon module
from src.execution.background_scheduler import GMAIBackgroundDaemon

class GMANetworkBroker:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.ledger = GMAIAuditLedger()
        # Spin up a daemon worker thread instance set to audit on a 10 second interval
        self.daemon_guard = GMAIBackgroundDaemon(check_interval_sec=10.0)
        print(f"[GM AI Broker] Initialized Isolated Channel Network Broker on {self.host}:{self.port}")

    async def handle_stream(self, websocket):
        """Intercepts telemetry, extracts channel partition IDs, and runs isolated workflows."""
        remote_address = websocket.remote_address
        print(f"\n[GM AI Broker] Active network connection hook: {remote_address}")

        try:
            async for message in websocket:
                try:
                    payload = json.loads(message)
                    device_source = payload.get("device", "Remote Display")
                    remote_intent = payload.get("command", "").strip()
                    channel_id = payload.get("channel", f"channel_{device_source.replace(' ', '_').lower()}")

                    print(f"\n[GM AI Network Task] Received via Channel '{channel_id}' [{device_source}]: '{remote_intent}'")

                    if remote_intent:
                        print(f"[GM AI Broker] Initializing state graph pipeline loop...")
                        thread_config = {"configurable": {"thread_id": f"session_{channel_id}"}}
                        initial_state = {"raw_user_input": remote_intent, "approval_status": "pending"}

                        for event in gm_engine.stream(initial_state, thread_config):
                            pass

                        current_state = gm_engine.get_state(thread_config).values

                        print(f"\n=========== 🛡️ WIRELESS CONFIRMATION: CHANNEL [{channel_id.upper()}] ===========")
                        print(f"Origin Device: {device_source}")
                        print(f"Captured Text Context: '{current_state.get('captured_context', '')}'")
                        print("\nGenerated Remote Automation Steps Blueprint:")
                        for idx, step in enumerate(current_state.get('proposed_actions', []), 1):
                            print(f" [{idx}] Action Mode: {step['type']} -> Context: {step['payload']}")
                        print("====================================================================")

                        response = {
                            "id": "NEW",
                            "device": device_source,
                            "channel": channel_id,
                            "command": remote_intent,
                            "status": "AWAITING_HUMAN_CONFIRMATION"
                        }
                        await websocket.send(json.dumps(response))

                        user_approval = input("\n[Bot-Sitter Authorization] Approve this wireless remote plan? (y/n): ")
                        if user_approval.lower() == 'y':
                            gm_engine.update_state(thread_config, {"approval_status": "approved"}, as_node="parse_intent")
                            for event in gm_engine.stream(None, thread_config):
                                pass

                            self.ledger.commit_transaction(intent=remote_intent, status="success_completed", device=device_source, channel=channel_id)
                            print(f"[GM AI Broker] Task successfully executed on channel: {channel_id}")
                        else:
                            self.ledger.commit_transaction(intent=remote_intent, status="rejected_by_user", device=device_source, channel=channel_id)
                            print(f"[GM AI Broker] Task rejected on channel: {channel_id}")

                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"status": "ERROR", "msg": "Invalid JSON structural format"}))

        except websockets.exceptions.ConnectionClosed:
            print(f"[GM AI Broker] Closed network connection loop for: {remote_address}")

    async def main_loop(self):
        async with websockets.serve(self.handle_stream, self.host, self.port):
            print("[GM AI Broker] Multi-Tenant Gateway Online. Ready...")
            # Automatically activate the background diagnostic runner thread alongside network start
            self.daemon_guard.start()
            await asyncio.Future()

    def start_server(self):
        try:
            asyncio.run(self.main_loop())
        except KeyboardInterrupt:
            print("\n[GM AI Broker] Shutting down network listeners cleanly.")
            # Ensure the worker daemon stops running if the user terminates the execution loop
            self.daemon_guard.stop()

if __name__ == "__main__":
    broker = GMANetworkBroker()
    broker.start_server()
