import subprocess
import shlex

class GMActionBridge:
    def __init__(self):
        # Explicitly whitelist programs to prevent loose terminal attacks
        self.allowed_applications = {
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "taskmgr": "taskmgr.exe"
        }

    def execute_app(self, app_key: str) -> dict:
        """Securely launch an application from the approved system whitelist."""
        app_name = app_key.strip().lower()
        if app_name not in self.allowed_applications:
            return {
                "status": "REJECTED",
                "error": f"Security Volatility Check: Application '{app_key}' is not in your system whitelist."
            }
        
        try:
            # Non-blocking launch to keep the engine conversational loop running
            subprocess.Popen([self.allowed_applications[app_name]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"status": "LAUNCHED", "target": self.allowed_applications[app_name]}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

