import urllib.request
import json
import re
from ingestion.parser import GMInputParser
from storage.db_manager import GMDatabaseManager
from actions.bridge import GMActionBridge

class GMAIEngine:
    def __init__(self, model_name="gpt-oss:120b-cloud", host="127.0.0.1", port=11434):
        self.model_name = model_name
        self.url = f"http://{host}:{port}/api/generate"
        self.parser = GMInputParser(max_chars=4000)
        self.db = GMDatabaseManager()
        self.action_bridge = GMActionBridge()

    def process_message(self, session_id: str, raw_payload: str):
        """Orchestrate parsing, database storage, context retrieval, and actions."""
        parsed = self.parser.parse_payload(raw_payload)
        if parsed["status"] != "CLEAN":
            yield f"[SYSTEM BLOCKED] {parsed.get('error', 'Malformed Input')}"
            return

        user_prompt = parsed["prompt"]
        
        # Step 1: Log incoming message turn directly into the SQL database
        self.db.log_message(session_id, "bot_sitter", user_prompt)
        
        # Step 2: Fetch last historical log context entries from the database
        history = self.db.get_session_history(session_id, limit=6)
        
        context_string = ""
        for turn in history[:-1]:
            context_string += f"{turn['role'].upper()}: {turn['content']}\n"
        context_string += f"BOT_SITTER: {user_prompt}\nGM_AI_ENGINE:"

        payload = {
            "model": self.model_name,
            "prompt": context_string.strip(),
            "stream": True
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(self.url, data=data, headers={'Content-Type': 'application/json'})
        
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
                
                # Step 3: Log engine text response back to the SQL database
                self.db.log_message(session_id, "gm_ai_engine", assistant_response)
                
                # Step 4: Scan and execute automation action triggers
                action_match = re.search(r"\[TRIGGER_LAUNCH:\s*(\w+)\]", assistant_response)
                if action_match:
                    target_app = action_match.group(1)
                    yield f"\n\n[SYSTEM] Intercepted automation token. Launching {target_app}..."
                    action_result = self.action_bridge.execute_app(target_app)
                    
                    # Step 5: Log automation launch execution status to the database logs
                    self.db.log_action(session_id, target_app, action_result['status'])
                    yield f"\n[SYSTEM STATUS] Execution result: {action_result['status']}"
                
        except Exception as e:
            yield f"\n[PIPELINE EXCEPTION] Failed to connect to server: {e}"
