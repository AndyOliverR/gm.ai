import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from orchestrator import GMAIEngine
from telemetry.sensor import GMTelemetrySensor

def start_sandbox():
    engine = GMAIEngine()
    sensor = GMTelemetrySensor()
    session_id = "sandbox_developer_session"
    
    print("====================================================")
    print("GM AI Core Engine Workspace Initialized")
    print("Operator: Bot-Sitter (Human in the loop)")
    print("Shortcut command: Type 'status' to poll telemetry.")
    print("Type 'exit' or 'quit' to terminate the session.")
    print("====================================================\n")
    
    while True:
        try:
            user_input = input("\nBot-Sitter: ")
            if user_input.strip().lower() in ['exit', 'quit']:
                print("Closing engine session.")
                break
                
            if user_input.strip().lower() == 'status':
                print("\n" + sensor.format_telemetry_report())
                continue
                
            if not user_input.strip():
                continue
                
            raw_payload = f'{{"prompt": "{user_input}"}}'
            
            print("GM AI Engine: ", end="", flush=True)
            for token in engine.process_message(session_id, raw_payload):
                print(token, end="", flush=True)
            print()
            
        except KeyboardInterrupt:
            print("\nSession aborted.")
            break

if __name__ == "__main__":
    start_sandbox()
