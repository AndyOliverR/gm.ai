import sqlite3
import os
import time

class GMANetworkAuditLedger:
    def __init__(self, db_path: str = "gm_memory.db"):
        self.db_path = db_path
        self._initialize_audit_table()

    def _initialize_audit_table(self):
        """Creates the relational action log grid if it does not exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_action_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                device_source TEXT,
                command_intent TEXT,
                execution_status TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log_action(self, device: str, command: str, status: str = "EXECUTED"):
        """Appends a new structural interaction node item into the SQLite ledger."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO system_action_audit (timestamp, device_source, command_intent, execution_status)
            VALUES (?, ?, ?, ?)
        """, (int(time.time()), device, command, status))
        conn.commit()
        conn.close()
        print(f"[GM AI Ledger] Action successfully appended to persistent database audit track.")

    def print_runtime_report(self):
        """Fetches and displays the complete historical macro sequence list."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, device_source, command_intent, execution_status FROM system_action_audit ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        print("\n=========== 📊 GM AI LOCAL AUDIT LEDGER TIMELINE ===========")
        if not rows:
            print(" No execution history recorded inside the data stream table yet.")
        for row in rows:
            tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[1]))
            print(f" [{row[0]}] {tm} | From: {row[2]} | Intent: '{row[3]}' | Status: {row[4]}")
        print("============================================================\n")

if __name__ == "__main__":
    ledger = GMANetworkAuditLedger()
    print("[GM AI] Running local relational trace validation test...")
    ledger.log_action("Local Sandbox Profile", "Test tracking sequence layout calibration")
    ledger.print_runtime_report()
