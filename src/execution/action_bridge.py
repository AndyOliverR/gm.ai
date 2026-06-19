import sys
import os
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

try:
    import pyautogui
    pyautogui.FAILSAFE = True
except ImportError:
    raise ImportError("Dependency missing. Please run: pip install pyautogui")

from src.ingestion.screen_capture import ScreenContextLayer

class SystemOperatorBridge:
    def __init__(self):
        self.capturer = ScreenContextLayer()
        self.layout_path = os.path.join("src", "ingestion", "window_layouts.json")
        self.layouts = self._load_layouts()

    def _load_layouts(self):
        try:
            with open(self.layout_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def execute_targeted_click(self, app_key: str, element_key: str):
        """Resolves active window boundaries and clicks the exact relative layout zone."""
        bounds = self.capturer.extract_window_bounds()
        left, top, right, bottom = bounds
        win_w = right - left
        win_h = bottom - top

        if app_key in self.layouts and element_key in self.layouts[app_key]:
            rel = self.layouts[app_key][element_key]
            target_x = left + int(win_w * rel["rel_x"])
            target_y = top + int(win_h * rel["rel_y"])
            
            print(f"[GM AI Operator] Moving to coordinate: ({target_x}, {target_y})")
            pyautogui.moveTo(target_x, target_y, duration=0.5)
            pyautogui.click()
            print("[GM AI Operator] Click executed.")
            return True
        return False

    def execute_text_input(self, text: str, press_enter: bool = True):
        """Simulates human typing string entry with uniform character delays."""
        print(f"[GM AI Operator] Emulating text entry sequencing: '{text}'")
        # 0.05 seconds delay between keys mimics natural human timing patterns
        pyautogui.write(text, interval=0.05)
        
        if press_enter:
            pyautogui.press('enter')
            print("[GM AI Operator] Enter key command dispatched.")

if __name__ == "__main__":
    operator = SystemOperatorBridge()
    print("[GM AI] Initializing Macro Test Layer with Keystroke Automation...")
    print("[GM AI] Safety Reminder: Jerk your mouse cursor to the top-left corner to abort instantly.")
    time.sleep(2)
    
    # Run a test click on our active workspace window canvas boundary zone
    operator.execute_targeted_click("notepad", "edit_field")
    
    # Immediately type a diagnostic print command string safely on screen
    operator.execute_text_input("echo [GM AI] Human Operator Extension Active!", press_enter=False)
