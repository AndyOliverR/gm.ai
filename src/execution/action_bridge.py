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
        """Resolves target app window boundaries and scales input coordinates responsively."""
        bounds = self.capturer.extract_window_bounds()
        left, top, right, bottom = bounds
        win_w = right - left
        win_h = bottom - top

        screen_width, screen_height = pyautogui.size()
        print(f"[GM AI Scaler] Live hardware display matrix: {screen_width}x{screen_height}")

        if app_key in self.layouts and element_key in self.layouts[app_key]:
            rel = self.layouts[app_key][element_key]
            
            target_x = left + int(win_w * rel["rel_x"])
            target_y = top + int(win_h * rel["rel_y"])
            
            target_x = max(0, min(target_x, screen_width - 1))
            target_y = max(0, min(target_y, screen_height - 1))
            
            print(f"[GM AI Operator] Dynamic target scaled safely to point: ({target_x}, {target_y})")
            pyautogui.moveTo(target_x, target_y, duration=0.5)
            pyautogui.click()
            print("[GM AI Operator] Cross-display scaled action deployed.")
            return True
            
        print(f"[GM AI Operator] Target mapping mismatch: {app_key}.{element_key}")
        return False

    def execute_text_input(self, text: str, press_enter: bool = True):
        """Simulates human typing entry strings."""
        print(f"[GM AI Operator] Emulating text entry sequencing: '{text}'")
        pyautogui.write(text, interval=0.05)
        if press_enter:
            pyautogui.press('enter')

    def execute_system_hotkey(self, hotkey_combination: str):
        """
        Parses and executes compound systemic hotkey hot-swaps safely.
        Example payloads: 'alt+tab', 'ctrl+c', 'ctrl+v', 'alt+f4'
        """
        print(f"[GM AI Operator] Dispatched system key combo sequence: [{hotkey_combination}]")
        keys = [k.strip().lower() for k in hotkey_combination.split("+")]
        
        try:
            # Emulate physical multi-key press combination holding sequence
            pyautogui.hotkey(*keys)
            time.sleep(0.5) # Allow display thread window context swap delay time to resolve
            return True
        except Exception as e:
            print(f"[GM AI Operator Error] Hotkey macro injection mismatch: {e}")
            return False

if __name__ == "__main__":
    operator = SystemOperatorBridge()
    print("[GM AI] Initializing Keyboard Combinator Macro Test...")
    time.sleep(2)
    
    # Run a non-destructive system hotkey test to verify keys activate cleanly
    operator.execute_system_hotkey("ctrl+shift+esc") # Spins up Task Manager to verify execution
