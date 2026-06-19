import sys
import os
import subprocess
import time

class GMAIAppBootstrapper:
    def __init__(self):
        # Centralized registry of common application and browser executable paths on Windows
        self.app_registry = {
            "notepad": r"C:\Windows\System32\notepad.exe",
            "calc": r"C:\Windows\System32\calc.exe",
            "cmd": r"C:\Windows\System32\cmd.exe",
            # Standard production paths for Google Chrome on modern Windows builds
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "chrome_x86": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        }
        print("[GM AI Bootstrapper] Web and process registry initialized.")

    def ensure_application_running(self, app_name: str) -> bool:
        """Checks if an application process is active. If not, boots it dynamically."""
        app_key = app_name.lower().strip()
        
        # Handle Chrome resolution mappings elegantly
        search_process = "chrome" if "chrome" in app_key else app_key
        
        try:
            tasklist_check = subprocess.check_output(f'tasklist /FI "IMAGENAME eq {search_process}.exe"', shell=True).decode('utf-8', errors='ignore')
            if f"{search_process}.exe" in tasklist_check.lower():
                print(f"[GM AI Bootstrapper] Active process detected for '{search_process}'. No boot required.")
                return True
        except Exception:
            pass

        # If browser or app process is missing, look up valid binary mappings and spawn it
        if "chrome" in app_key:
            target_exe = self.app_registry["chrome"] if os.path.exists(self.app_registry["chrome"]) else self.app_registry["chrome_x86"]
            if os.path.exists(target_exe):
                print("[GM AI Bootstrapper] Web Browser process missing. Spawning Chrome dynamically...")
                subprocess.Popen(target_exe)
                time.sleep(2.0) # Crucial grace period to let complex browser engines spin up canvas threads
                return True

        if app_key in self.app_registry:
            exe_path = self.app_registry[app_key]
            if os.path.exists(exe_path):
                print(f"[GM AI Bootstrapper] Process '{app_key}' missing. Spawning executable path dynamically...")
                subprocess.Popen(exe_path)
                time.sleep(1.5)
                return True
                
        print(f"[GM AI Bootstrapper] Warning: '{app_key}' is not registered in the system boot list.")
        return False

if __name__ == "__main__":
    bootstrapper = GMAIAppBootstrapper()
    print("[GM AI] Running browser boot validation check...")
    # Run an autonomous local verification pass to ensure Chrome boots safely
    bootstrapper.ensure_application_running("chrome")
