import urllib.request
import json
import re
from ingestion.parser import GMInputParser
from tracking.session import GMSessionTracker
from actions.bridge import GMActionBridge

class GMAIEngine:
    def __init__(self, model_name="gpt-oss:120b-cloud", host="127.0.0.1", port=11434):
        self.model_name = model_name
        self.url = f"http://{host}:{port}/api/generate"
        self.parser = GMInputParser(max_chars=4000)
        self.tracker = GMSessionTracker()
        self.action_bridge = GMActionBridge()

    def process_message(self, session_id: str, raw_payload: str):
        """Orchestrate parsing, context merging, text stream generation, and actions."""
        # Step 1: Parse and Clean Raw Payloads
        parsed = self.parser.parse_payload(raw_payload)
        if parsed["status"] != "CLEAN":
            yield f"[SYSTEM BLOCKED] {parsed.get('error', 'Malformed Input')}"
            return

        user_prompt = parsed["prompt"]
        
        # Step 2: Append user input and load conversational history context
        self.tracker.append_turn(session_id, "user", user_prompt)
        history = self.tracker.load_history(session_id)
        
        context_string = ""
        for turn in history[:-1]:
            context_string += f"{turn['role'].upper()}: {turn['content']}\n"
        context_string += f"BOT_SITTER: {user_prompt}\nGM_AI_ENGINE:"

        # Step 3: Package full contextual payload for the Ollama node
        payload = {
            "model": self.model_name,
            "prompt": context_string.strip(),
            "stream": True
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            self.url, 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        
        # Step 4: Establish the stream and yield incoming message tokens
        try:
            with urllib.request.urlopen(req) as response:
                assistant_response = ""
                for line in response:
                    if line:
                        try:
                            line_data = json.loads(line.decode('utf-8').strip())
                            token = line_data.get("response", "")
                            assistant_response += token
                            yield token
                        except json.JSONDecodeError:
                            pass
                
                # Save the complete structural model output response back to session storage
                self.tracker.append_turn(session_id, "gm_ai_engine", assistant_response)
                
                # Step 5: Post-processing Action Scan
                # Look for patterns like [TRIGGER_LAUNCH: app_name]
                action_match = re.search(r"\[TRIGGER_LAUNCH:\s*(\w+)\]", assistant_response)
                if action_match:
                    target_app = action_match.group(1)
                    yield f"\n\n[SYSTEM] Intercepted automation token. Launching {target_app}..."
                    action_result = self.action_bridge.execute_app(target_app)
                    yield f"\n[SYSTEM STATUS] Execution result: {action_result['status']}"
                
        except Exception as e:
            yield f"\n[PIPELINE EXCEPTION] Failed to connect to server: {e}"
