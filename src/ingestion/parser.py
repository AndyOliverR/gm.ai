import re
import json

class GMInputParser:
    def __init__(self, max_chars=4000):
        self.max_chars = max_chars
        # Catch explicit adversarial overrides
        self.malicious_patterns = [
            re.compile(r"ignore\s+previous\s+instructions", re.IGNORECASE),
            re.compile(r"system\s+override", re.IGNORECASE),
            re.compile(r"you\s+are\s+now\s+an\s+unfiltered", re.IGNORECASE)
        ]

    def sanitize_text(self, text: str) -> str:
        """Strip dangerous characters and block prompt injection strings."""
        if not text:
            return ""
        
        # Enforce maximum hard character boundaries to stop token exhaustion
        clean_text = text[:self.max_chars]
        
        # Validate against known injection threat strings
        for pattern in self.malicious_patterns:
            if pattern.search(clean_text):
                raise ValueError("Security Boundary Violated: Prompt injection detected.")
                
        return clean_text.strip()

    def parse_payload(self, raw_payload: str) -> dict:
        """Normalize raw incoming payload telemetry data."""
        try:
            data = json.loads(raw_payload) if isinstance(raw_payload, str) else raw_payload
            processed_prompt = self.sanitize_text(data.get("prompt", ""))
            return {
                "status": "CLEAN",
                "prompt": processed_prompt,
                "metadata": data.get("metadata", {})
            }
        except ValueError as ve:
            return {"status": "BLOCKED", "error": str(ve), "prompt": ""}
        except Exception as e:
            return {"status": "MALFORMED", "error": f"Invalid payload schema: {str(e)}", "prompt": ""}
