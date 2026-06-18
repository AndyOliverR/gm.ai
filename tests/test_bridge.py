import unittest
import sys
sys.path.append(r'C:\gm.ai\src')
from actions.bridge import GMActionBridge

class TestGMActionBridge(unittest.TestCase):
    def setUp(self):
        self.bridge = GMActionBridge()

    def test_whitelist_execution_allowed(self):
        # Verify a valid whitelisted entry returns a LAUNCHED state status
        result = self.bridge.execute_app("calc")
        self.assertEqual(result["status"], "LAUNCHED")
        self.assertEqual(result["target"], "calc.exe")

    def test_unauthorized_app_blocked(self):
        # Verify dangerous or non-whitelisted items are dropped instantly
        result = self.bridge.execute_app("cmd.exe")
        self.assertEqual(result["status"], "REJECTED")
        self.assertIn("Security Volatility Check", result["error"])

if __name__ == "__main__":
    unittest.main()
