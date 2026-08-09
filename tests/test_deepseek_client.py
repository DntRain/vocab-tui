import unittest
from unittest.mock import patch

from deepseek_client import DeepSeekClient


class DeepSeekClientTests(unittest.TestCase):
    def test_requires_api_key(self):
        client = DeepSeekClient(api_key="")
        with self.assertRaisesRegex(RuntimeError, "API key"):
            client.explain("Explain ambiguous", [], "Graduate Core")

    def test_switches_provider_model(self):
        client = DeepSeekClient(api_key="deepseek-test")
        with patch("deepseek_client.resolve_api_key", return_value="openai-test"):
            client.select_preset("gpt-4o-mini")
        self.assertEqual(client.provider, "openai")
        self.assertEqual(client.model, "gpt-4o-mini")
        self.assertEqual(client.api_key, "openai-test")


if __name__ == "__main__":
    unittest.main()
