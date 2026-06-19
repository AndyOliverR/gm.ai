import sys
import os
import time
import json
from typing import Dict, List

# Dynamically ensure top-level project module access
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

class GMAIDataExtractor:
    def __init__(self, target_dir: str = "storage/extracted_data/"):
        self.target_dir = target_dir
        os.makedirs(self.target_dir, exist_ok=True)
        print("[GM AI Extractor] Data Extraction Manager initialized.")

    def export_scraped_entities(self, entity_map: Dict[str, List[str]], session_id: str = "global_session") -> str:
        """Parses token lists out of the active graph state and writes organized text logs."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        log_filepath = os.path.join(self.target_dir, f"session_intel_dump.txt")
        
        has_data = False
        output_buffer = f"\n=== GM AI INTEL SCANNED RECORD | {timestamp} | Session: {session_id} ===\n"

        # Dynamically loop and format discovered strings into separate target categories
        for entity_type, tokens in entity_map.items():
            if tokens:
                has_data = True
                output_buffer += f" [{entity_type.upper()}]\n"
                for token in tokens:
                    output_buffer += f"  -> {token}\n"

        if not has_data:
            return "NO_DATA_FOUND"

        output_buffer += "========================================================================\n"

        # Append data to physical desktop file logs safely
        try:
            with open(log_filepath, "a", encoding="utf-8") as f:
                f.write(output_buffer)
            print(f"[GM AI Extractor] Successfully logged screen metadata variables to disk.")
            return log_filepath
        except Exception as e:
            print(f"[GM AI Extractor Error] Failed to commit structured ledger: {e}")
            return "WRITE_FAILURE"

if __name__ == "__main__":
    extractor = GMAIDataExtractor()
    print("[GM AI] Running local relational data extraction validation pass...")
    
    # Generate mock environment entity map data for testing
    mock_entities = {
        "urls": ["https://github.com"],
        "emails": ["core_dev@gm.ai"],
        "windows_paths": ["C:\\gm.ai"],
        "numerical_ledgers": ["2026.06"]
    }
    
    result_path = extractor.export_scraped_entities(mock_entities, session_id="sandbox_test")
    print(f"[GM AI] Data Extraction output verification target: {result_path}")
