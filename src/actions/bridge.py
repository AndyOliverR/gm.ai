import subprocess
import sys
import os

class GMActionBridge:
    def __init__(self):
        # Whitelisted core executables
        self.allowed_applications = {
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "taskmgr": "taskmgr.exe",
            "explorer": "explorer.exe"
        }

    def execute_app(self, app_key: str, argument: str = "") -> dict:
        """Securely launch an application, optionally piping parameters or arguments."""
        app_name = app_key.strip().lower()
        if app_name not in self.allowed_applications:
            return {
                "status": "REJECTED",
                "error": f"Security Volatility Check: Application '{app_key}' is blocked."
            }
        
        executable = self.allowed_applications[app_name]
        command_list = [executable]
        
        # Clean and append arguments safely if provided
        if argument:
            # Simple sanitization: prevent argument command-chaining injections (no & or | flags)
            clean_arg = argument.replace("&", "").replace("|", "").replace(";", "").strip()
            if clean_arg:
                command_list.append(clean_arg)
        
        try:
            # Launch without blocking the main engine orchestrator thread
            subprocess.Popen(command_list, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {
                "status": "LAUNCHED", 
                "target": executable, 
                "args_passed": argument if argument else "None"
            }
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
