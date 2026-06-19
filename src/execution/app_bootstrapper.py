import sys
import os
import subprocess
import time

class GMAIAppBootstrapper:
    def __init__(self):
        # Centralized registry of common application executable paths on Windows
        self.app_registry = {
            "notepad": r"C:\Windows\System32\notepad.exe",
            "calc": r"C:\Windows\System32\calc.exe",
            "cmd": r"C:\Windows\System32\cmd.exe"
        }
        print("[GM AI Bootstrapper] Process registry initialized.")

    def ensure_application_running(self, app_name: str) -> bool:
        """Checks if an application process is active. If not, boots it dynamically."""
        app_key = app_name.lower().strip()
        
        # Check if the process is already running via Windows tasklist query
        try:
            tasklist_check = subprocess.check_output(f'tasklist /FI "IMAGENAME eq {app_key}.exe"', shell=True).decode('utf-8', errors='ignore')
            if f"{app_key}.exe" in tasklist_check.lower():
                print(f"[GM AI Bootstrapper] Active process detected for '{app_key}'. No boot required.")
                return True
        except Exception:
            pass

        # If it's not running, look up the path in our registry and spawn it
        if app_key in self.app_registry:
            exe_path = self.app_registry[app_key]
            if os.path.exists(exe_path):
                print(f"[GM AI Bootstrapper] Process '{app_key}' missing. Spawning executable path dynamically...")
                subprocess.Popen(exe_path)
                time.sleep(1.5) # Crucial grace period to let the window render completely
                return True
            else:
                print(f"[GM AI Bootstrapper] Error: Registered path for '{app_key}' does not exist on disk.")
                return False
                
        print(f"[GM AI Bootstrapper] Warning: '{app_key}' is not registered in the system boot list.")
        return False

if __name__ == "__main__":
    bootstrapper = GMAIAppBootstrapper()
    print("[GM AI] Running local process bootstrapper validation check...")
    # Test it by ensuring Notepad is booted safely
    bootstrapper.ensure_application_running("notepad")
