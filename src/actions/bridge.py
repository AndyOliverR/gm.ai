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
            return {"status": "LAUNCHED", "target": executable, "args_passed": argument if argument else "None"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    def write_to_file(self, relative_path: str, content: str, mode: str = "w") -> dict:
        """Programmatically create or update a file strictly within the workspace boundaries."""
        try:
            target_path = os.path.abspath(os.path.join(self.workspace_root, relative_path.strip().lstrip("\\/")))
            if not target_path.startswith(self.workspace_root):
                return {"status": "REJECTED", "error": "Security Boundary Violated: Directory escape blocked."}
            
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, mode, encoding="utf-8") as f:
                f.write(content)
            return {"status": "SUCCESS", "action": "CREATED/UPDATED" if mode == "w" else "APPENDED", "file_path": target_path}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    def list_directory_contents(self, relative_path: str = "") -> str:
        """List file trees strictly inside the workspace root container bounds."""
        try:
            target_path = os.path.abspath(os.path.join(self.workspace_root, relative_path.strip().lstrip("\\/")))
            if not target_path.startswith(self.workspace_root):
                return "[SECURITY BLOCKED] Cannot list directories outside workspace boundary paths."
            
            if not os.path.exists(target_path):
                return f"[PATH ERROR] Directory path '{relative_path}' does not exist."
                
            files = os.listdir(target_path)
            if not files:
                return f"Directory '{relative_path}' is completely empty."
                
            report = f"=== FILE SYSTEM SCAN: {relative_path if relative_path else 'ROOT'} ===\n"
            for index, item in enumerate(files, 1):
                item_path = os.path.join(target_path, item)
                marker = "[DIR]" if os.path.isdir(item_path) else "[FILE]"
                report += f" {index}. {marker} {item}\n"
            return report
            
        except Exception as e:
            return f"[MACRO CRASH] Directory extraction anomaly: {str(e)}"

    def kill_whitelisted_process(self, app_key: str) -> dict:
        """Securely terminate an active task loop from the whitelisted keys array."""
        app_name = app_key.strip().lower()
        if app_name not in self.allowed_applications:
            return {"status": "REJECTED", "error": f"Task closing access denied for process '{app_key}'."}
            
        executable = self.allowed_applications[app_name]
        try:
            # Force close a task silently using standard Windows taskkill tools
            subprocess.run(["taskkill", "/F", "/IM", executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"status": "TERMINATED", "target_process": executable}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
