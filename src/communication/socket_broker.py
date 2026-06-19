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

# Import the core LangGraph state engine and our audit tracker
from app import gm_engine
from src.execution.audit_ledger import GMANetworkAuditLedger

class GMANetworkBroker:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.ledger = GMANetworkAuditLedger()
        print(f"[GM AI Broker] Initialized Audited Network Broker on {self.host}:{self.port}")

    async def handle_stream(self, websocket):
        """Intercepts remote wireless telemetry, passes it to LangGraph, and records results."""
        remote_address = websocket.remote_address
        print(f"\n[GM AI Broker] Active network connection hook: {remote_address}")
        
        try:
            async for message in websocket:
                try:
                    payload = json.loads(message)
                    device_source = payload.get("device", "Remote Display")
                    remote_intent = payload.get("command", "").strip()
                    
                    print(f"\n[GM AI Network Task] Received via {device_source}: '{remote_intent}'")
                    
                    if remote_intent:
                        print(f"[GM AI Broker] Initializing state graph pipeline loop...")
                        thread_config = {"configurable": {"thread_id": f"network_{device_source.replace(' ', '_')}"}}
                        initial_state = {"raw_user_input": remote_intent, "approval_status": "pending"}
                        
                        for event in gm_engine.stream(initial_state, thread_config):
                            pass
                            
                        current_state = gm_engine.get_state(thread_config).values
                        
                        print("\n=========== 🛡️ WIRELESS REMOTE BOT-SITTER CONFIRMATION ===========")
                        print(f"Origin Device: {device_source}")
                        print(f"Captured Text Context: '{current_state.get('captured_context', '')}'")
                        print("\nGenerated Remote Automation Steps Blueprint:")
                        for idx, step in enumerate(current_state.get('proposed_actions', []), 1):
                            print(f" [{idx}] Action Mode: {step['type']} -> Context: {step['payload']}")
                        print("====================================================================")
                        
                        response = {
                            "status": "AWAITING_HUMAN_CONFIRMATION",
                            "msg": "Automation blueprint generated. Awaiting physical operator confirmation on host machine."
                        }
                        await websocket.send(json.dumps(response))
                        
                        user_approval = input("\n[Bot-Sitter Authorization] Approve this wireless remote plan? (y/n): ")
                        if user_approval.lower() == 'y':
                            gm_engine.update_state(thread_config, {"approval_status": "approved"}, as_node="parse_intent")
                            for event in gm_engine.stream(None, thread_config):
                                pass
                            
                            # Log the successful deployment to our local audit trail
                            self.ledger.log_action(device_source, remote_intent, status="EXECUTED")
                            print("[GM AI Broker] Remote task executed successfully.")
                        else:
                            # Log the rejection for user auditing visibility
                            self.ledger.log_action(device_source, remote_intent, status="REJECTED_BY_USER")
                            print("[GM AI Broker] Remote deployment blocked by host user.")
                    
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"status": "ERROR", "msg": "Invalid JSON structural format"}))
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"[GM AI Broker] Closed network connection loop for: {remote_address}")

    async def main_loop(self):
        async with websockets.serve(self.handle_stream, self.host, self.port):
            print("[GM AI Broker] Audited Cross-Device Gateway Online. Ready...")
            await asyncio.Future()

    def start_server(self):
        try:
            asyncio.run(self.main_loop())
        except KeyboardInterrupt:
            print("\n[GM AI Broker] Shutting down network listeners cleanly.")

if __name__ == "__main__":
    broker = GMANetworkBroker()
    broker.start_server()
