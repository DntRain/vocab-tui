import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WebChecklistTests(unittest.TestCase):
    def test_standalone_html_contains_all_graduate_words(self):
        dictionary = json.loads(
            (ROOT / "dictionaries" / "graduate-core.json").read_text(encoding="utf-8")
        )
        document = (ROOT / "web" / "graduate-vocab-checklist.html").read_text(encoding="utf-8")
        match = re.search(
            r'<script id="word-data" type="application/json">(.*?)</script>',
            document,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        embedded_words = json.loads(match.group(1))
        self.assertEqual(len(embedded_words), len(dictionary["words"]))
        self.assertEqual(len(embedded_words), 4801)
        self.assertTrue(all(item["w"] and item["t"] for item in embedded_words))


if __name__ == "__main__":
    unittest.main()
