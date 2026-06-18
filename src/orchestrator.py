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
        
        # Local shortcut dictionary to bypass cloud provider alignment blocks
        self.local_shortcuts = {
            "open config": ("notepad", "C:\\gm.ai\\config.json"),
            "open database": ("explorer", "C:\\gm.ai\\storage"),
            "open engine logs": ("notepad", "C:\\gm.ai\\storage\\gm_core.db")
        }

    def process_message(self, session_id: str, raw_payload: str):
        """Orchestrate parsing, shortcut processing, history tracking, and fallback cloud inference."""
        parsed = self.parser.parse_payload(raw_payload)
        if parsed["status"] != "CLEAN":
            yield f"[SYSTEM BLOCKED] {parsed.get('error', 'Malformed Input')}"
            return

        user_prompt = parsed["prompt"]
        self.db.log_message(session_id, "bot_sitter", user_prompt)
        
        # Check if the user prompt matches a local system shortcut key phrase
        normalized_prompt = user_prompt.strip().lower()
        if normalized_prompt in self.local_shortcuts:
            app, arg = self.local_shortcuts[normalized_prompt]
            yield f"Acknowledged. Local system shortcut triggered. Launching {app} with argument '{arg}'..."
            action_result = self.action_bridge.execute_app(app, arg)
            self.db.log_action(session_id, app, f"Shortcut Launch: {action_result['status']} ({arg})")
            yield f"\n[SYSTEM STATUS] Execution result: {action_result['status']}"
            return

        # Fallback to local Ollama inference cloud node if no shortcut is matched
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
                
                self.db.log_message(session_id, "gm_ai_engine", assistant_response)
                
                # Check for model-generated trigger structures
                action_match = re.search(r"\[TRIGGER_LAUNCH:\s*([^\]|]+)(?:\|([^\]]+))?\]", assistant_response)
                if action_match:
                    target_app = action_match.group(1).strip()
                    raw_args = action_match.group(2)
                    argument = raw_args.strip() if raw_args else ""
                    
                    yield f"\n\n[SYSTEM] Intercepted automation token. Launching {target_app}..."
                    action_result = self.action_bridge.execute_app(target_app, argument)
                    self.db.log_action(session_id, target_app, f"{action_result['status']} ({argument})")
                    yield f"\n[SYSTEM STATUS] Execution result: {action_result['status']}"
                
        except Exception as e:
            yield f"\n[PIPELINE EXCEPTION] Failed to connect to server: {e}"
