import os
import time
import ctypes
from typing import Dict, Any, Tuple

# Force strict hardware coordinate tracking across high-DPI magnified displays
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2) # Per-Monitor DPI Aware profile
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware() # Classic Windows fallback hook
    except Exception:
        print("[GM AI Scaling Warning] Failed to initialize hardware DPI awareness loops.")

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
        """Captures the active screen layout, saves it, and runs a cache cleanup."""
        self._purge_old_cache_frames(max_age_seconds=60)
        
        timestamp = int(time.time())
        filepath = os.path.join(self.output_dir, f"raw_surface_{timestamp}.png")
        screenshot = ImageGrab.grab(all_screens=False)
        screenshot.save(filepath, "PNG")
        return filepath

    def _purge_old_cache_frames(self, max_age_seconds: int = 60):
        try:
            now = time.time()
            for filename in os.listdir(self.output_dir):
                if filename.startswith("raw_surface_") and filename.endswith(".png"):
                    file_path = os.path.join(self.output_dir, filename)
                    if os.path.getmtime(file_path) < (now - max_age_seconds):
                        os.remove(file_path)
        except Exception as e:
            print(f"[GM AI Cache Warning] Failed to clean workspace artifacts: {e}")

    def extract_window_bounds(self, target_title: str = "ActiveWindow") -> Tuple[int, int, int, int]:
        """Dynamically grabs the precise screen bounds of whichever window is currently in focus."""
        hwnd = win32gui.GetForegroundWindow()
        
        if hwnd != 0:
            title = win32gui.GetWindowText(hwnd)
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            if left >= -10000 and top >= -10000:
                print(f"[GM AI] Intercepted Focused Window: '{title}'")
                return (left, top, right, bottom)
            
        print("[GM AI] Warning: No active focused window tracked. Using sandbox bounds.")
        return (100, 100, 900, 700)

if __name__ == "__main__":
    parser = ScreenContextLayer()
    print("[GM AI] Running DPI-Aware Screen Context Layer validation test...")
    path = parser.capture_full_display()
    print(f"[GM AI] Active Context Frame isolated at: {path}")
    bounds = parser.extract_window_bounds()
    print(f"[GM AI] Dynamic Window Boundaries: {bounds}")
