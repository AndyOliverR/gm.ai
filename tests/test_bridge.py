import unittest
import sys
sys.path.append(r'C:\gm.ai\src')
from actions.bridge import GMActionBridge

class TestGMActionBridge(unittest.TestCase):
    def setUp(self):
        self.bridge = GMActionBridge()

    def test_whitelist_execution_allowed(self):
        result = self.bridge.execute_app("calc")
        self.assertEqual(result["status"], "LAUNCHED")

    def test_unauthorized_app_blocked(self):
        result = self.bridge.execute_app("powershell.exe")
        self.assertEqual(result["status"], "REJECTED")

    def test_execution_with_arguments(self):
        # Verify opening a specific target filepath structure handles arguments
        result = self.bridge.execute_app("notepad", "C:\\gm.ai\\config.json")
        self.assertEqual(result["status"], "LAUNCHED")
        self.assertEqual(result["args_passed"], "C:\\gm.ai\\config.json")

if __name__ == "__main__":
    unittest.main()
