import os
import sqlite3
import time

class GMAIAuditLedger:
    def __init__(self, db_path: str = "gm_memory.db"):
        self.db_path = db_path
        self._initialize_audit_table()

    def _initialize_audit_table(self):
        """Creates the critical system action audit ledger schema table if missing."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_action_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER NOT NULL,
                    device_source TEXT NOT NULL,
                    command_intent TEXT NOT NULL,
                    execution_status TEXT NOT NULL
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[GM AI Ledger Error] Failed to initialize table structures: {e}")

    def commit_transaction(self, intent: str, status: str = "success_completed", device: str = "local_desktop"):
        """Commits a high-frequency automation summary transaction row directly into history records."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            timestamp = int(time.time())
            
            cursor.execute('''
                INSERT INTO system_action_audit (timestamp, device_source, command_intent, execution_status)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, device, intent, status))
            
            conn.commit()
            conn.close()
            print(f"[GM AI Ledger] Successfully committed transaction line for intent: '{intent}'")
            return True
        except Exception as e:
            print(f"[GM AI Ledger Error] Failed to write historical row artifact: {e}")
            return False

if __name__ == "__main__":
    print("[INIT] Testing GMAIAuditLedger data engine pipelines...")
    ledger = GMAIAuditLedger()
    ledger.commit_transaction(intent="open notepad and type operational sync clear", status="success_completed")
