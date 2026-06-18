import urllib.request
import json
import re
from ingestion.parser import GMInputParser
from ingestion.document_reader import GMDocumentReader
from network.scraper import GMNetworkScraper
from storage.db_manager import GMDatabaseManager
from actions.bridge import GMActionBridge

class GMAIEngine:
    def __init__(self, model_name="gpt-oss:120b-cloud", host="127.0.0.1", port=11434):
        self.model_name = model_name
        self.url = f"http://{host}:{port}/api/generate"
        self.parser = GMInputParser(max_chars=4000)
        self.doc_reader = GMDocumentReader()
        self.web_scraper = GMNetworkScraper()
        self.db = GMDatabaseManager()
        self.action_bridge = GMActionBridge()
        
        self.local_shortcuts = {
            "open config": ("notepad", "C:\\gm.ai\\config.json"),
            "open database": ("explorer", "C:\\gm.ai\\storage"),
            "open engine logs": ("notepad", "C:\\gm.ai\\storage\\gm_core.db")
        }

    def process_message(self, session_id: str, raw_payload: str):
        """Orchestrate parsing, shortcut processing, local RAG checks, web scraping, and inference."""
        parsed = self.parser.parse_payload(raw_payload)
        if parsed["status"] != "CLEAN":
            yield f"[SYSTEM BLOCKED] {parsed.get('error', 'Malformed Input')}"
            return

        user_prompt = parsed["prompt"].strip()
        self.db.log_message(session_id, "bot_sitter", user_prompt)
        normalized_prompt = user_prompt.lower()
        
        # 1. Check for application shortcut triggers
        if normalized_prompt in self.local_shortcuts:
            app, arg = self.local_shortcuts[normalized_prompt]
            yield f"Acknowledged. Local system shortcut triggered. Launching {app} with argument '{arg}'..."
            action_result = self.action_bridge.execute_app(app, arg)
            self.db.log_action(session_id, app, f"Shortcut Launch: {action_result['status']} ({arg})")
            yield f"\n[SYSTEM STATUS] Execution result: {action_result['status']}"
            return

        # 2. Upgraded Network Check: Explicitly match 'fetch' followed by a clean URL token string boundary
        if user_prompt.lower().startswith("fetch "):
            target_url = user_prompt[6:].strip()
            # Basic validation check to verify it contains a protocol header hook
            if target_url.startswith(("http://", "https://")):
                yield f"[SYSTEM] Intercepted network scraping command. Querying target URL: '{target_url}'...\n\n"
                live_web_data = self.web_scraper.fetch_live_text(target_url)
                yield live_web_data
                yield "\n[SYSTEM] Network extraction complete. Live content ingested safely."
                return

        # 3. Check for local RAG document requests
        if any(keyword in normalized_prompt for keyword in ["document", "knowledge", "file", "budget"]):
            yield "[SYSTEM] Intercepted knowledge request. Querying local storage structures...\n\n"
            local_knowledge = self.doc_reader.read_all_documents()
            if not local_knowledge or "EXTRACTED" not in local_knowledge:
                yield "The local knowledge base folder is currently empty or unreadable."
            else:
                yield local_knowledge
                yield "\n[SYSTEM] Knowledge retrieval complete. Data processed 100% locally."
            return

        # 4. Fallback to conversation loop context
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
                
        except Exception as e:
            yield f"\n[PIPELINE EXCEPTION] Failed to connect to server: {e}"
