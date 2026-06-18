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
        # Enforce file operations strictly within the workspace directory root
        self.workspace_root = r"C:\gm.ai"

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
        
        if argument:
            clean_arg = argument.replace("&", "").replace("|", "").replace(";", "").strip()
            if clean_arg:
                command_list.append(clean_arg)
        
        try:
            subprocess.Popen(command_list, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {
                "status": "LAUNCHED", 
                "target": executable, 
                "args_passed": argument if argument else "None"
            }
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    def write_to_file(self, relative_path: str, content: str, mode: str = "w") -> dict:
        """Programmatically create or update a file strictly within the C:\gm.ai workspace boundaries."""
        try:
            # Resolve absolute target path and verify it stays inside the workspace root
            target_path = os.path.abspath(os.path.join(self.workspace_root, relative_path.strip().lstrip("\\/")))
            if not target_path.startswith(self.workspace_root):
                return {"status": "REJECTED", "error": "Security Boundary Violated: Directory escape blocked."}
            
            # Auto-create directory sub-paths if they don't exist
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            with open(target_path, mode, encoding="utf-8") as f:
                f.write(content)
                
            action_type = "CREATED/UPDATED" if mode == "w" else "APPENDED"
            return {"status": "SUCCESS", "action": action_type, "file_path": target_path}
            
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
