import unittest
import urllib.request
import json

class TestGMAIPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = "127.0.0.1"
        cls.port = 11434
        cls.model_name = "gpt-oss:120b-cloud"
        cls.base_url = f"http://{cls.host}:{cls.port}"

    def test_01_server_alive(self):
        """Verify the local Ollama daemon endpoint responds."""
        url = f"{self.base_url}/api/tags"
        try:
            response = urllib.request.urlopen(url, timeout=5)
            self.assertEqual(response.getcode(), 200)
        except Exception as e:
            self.fail(f"Ollama server is unreachable: {e}")

    def test_02_model_presence(self):
        """Verify gpt-oss:120b-cloud is present in local inventory."""
        url = f"{self.base_url}/api/tags"
        response = urllib.request.urlopen(url, timeout=5)
        data = json.loads(response.read().decode('utf-8'))
        models = [m['name'] for m in data.get('models', [])]
        self.assertIn(self.model_name, models, f"Model {self.model_name} not found in inventory.")

    def test_03_streaming_response(self):
        """Verify pipeline streams valid JSON chunks."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": "Ping",
            "stream": True
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            first_line = response.readline().decode('utf-8').strip()
            self.assertTrue(first_line, "Pipeline returned an empty stream.")
            line_data = json.loads(first_line)
            self.assertIn("response", line_data, "Stream chunk missing 'response' key.")

if __name__ == "__main__":
    unittest.main()
