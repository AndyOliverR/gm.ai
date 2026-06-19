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

class GMANetworkBroker:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        print(f"[GM AI Broker] Initialized Broker profile on {self.host}:{self.port}")

    async def handle_stream(self, websocket):
        """Listens for remote device payloads (mobile/laptop) and routes them into the engine."""
        remote_address = websocket.remote_address
        print(f"\n[GM AI Broker] Connected to remote device: {remote_address}")
        
        try:
            async for message in websocket:
                try:
                    payload = json.loads(message)
                    print(f"[GM AI Broker] Incoming Cross-Device Command: {payload}")
                    
                    device_source = payload.get("device", "Unknown Screen")
                    
                    # Formulate structured receipt payload back to client
                    response = {
                        "status": "QUEUED",
                        "msg": f"Host successfully accepted task from {device_source}"
                    }
                    await websocket.send(json.dumps(response))
                    
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"status": "ERROR", "msg": "Invalid JSON data"}))
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"[GM AI Broker] Disconnected from device: {remote_address}")

    async def main_loop(self):
        """Unified asynchronous context server listener entry point."""
        async with websockets.serve(self.handle_stream, self.host, self.port):
            print("[GM AI Broker] Server online. Waiting for cross-device socket connections...")
            await asyncio.Future()  # Keeps the server running indefinitely safely

    def start_server(self):
        """Launches the persistent network socket wrapper cleanly."""
        try:
            asyncio.run(self.main_loop())
        except KeyboardInterrupt:
            print("\n[GM AI Broker] Shutting down network listeners cleanly.")

if __name__ == "__main__":
    broker = GMANetworkBroker()
    broker.start_server()
