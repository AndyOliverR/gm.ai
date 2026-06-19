import os
import time
from typing import Dict, Any, Tuple

try:
    from PIL import ImageGrab
    import numpy as np
    import win32gui
except ImportError:
    raise ImportError("Dependencies missing. Please run: pip install pillow numpy pywin32")

class ScreenContextLayer:
    def __init__(self, output_dir: str = "src/ingestion/cache/"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def capture_full_display(self) -> str:
        """Captures the active screen layout and saves a local matrix copy."""
        timestamp = int(time.time())
        filepath = os.path.join(self.output_dir, f"raw_surface_{timestamp}.png")
        screenshot = ImageGrab.grab(all_screens=False)
        screenshot.save(filepath, "PNG")
        return filepath

    def extract_window_bounds(self, target_title: str = "ActiveWindow") -> Tuple[int, int, int, int]:
        """Dynamically grabs the precise screen bounds of whichever window is currently in focus."""
        hwnd = win32gui.GetForegroundWindow()
        
        if hwnd != 0:
            title = win32gui.GetWindowText(hwnd)
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            # Filter out minimized window anomalies
            if left >= -10000 and top >= -10000:
                print(f"[GM AI] Intercepted Focused Window: '{title}'")
                return (left, top, right, bottom)
            
        print("[GM AI] Warning: No active focused window tracked. Using sandbox bounds.")
        return (100, 100, 900, 700)

if __name__ == "__main__":
    parser = ScreenContextLayer()
    print("[GM AI] Initializing Live Screen Context Layer capture test...")
    path = parser.capture_full_display()
    print(f"[GM AI] Context Frame saved successfully to: {path}")
    
    # Track whatever window is active right now
    bounds = parser.extract_window_bounds()
    print(f"[GM AI] Extracted Window Bounds Target: {bounds}")
