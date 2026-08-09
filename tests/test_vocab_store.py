import tempfile
import unittest
from pathlib import Path

from vocab_store import ProgressStore, load_dictionaries


ROOT = Path(__file__).resolve().parents[1]


class VocabStoreTests(unittest.TestCase):
    def test_loads_builtin_dictionaries(self):
        dictionaries = load_dictionaries(ROOT / "dictionaries")
        self.assertEqual({item.id for item in dictionaries}, {"graduate-core", "ai-cs", "cet6"})
        counts = {item.id: len(item.words) for item in dictionaries}
        self.assertEqual(counts, {"graduate-core": 4801, "ai-cs": 172, "cet6": 5407})
        self.assertTrue(all(word.translation for item in dictionaries for word in item.words))

    def test_progress_persists_dictionary_and_mastery(self):
        dictionaries = load_dictionaries(ROOT / "dictionaries")
        with tempfile.TemporaryDirectory() as temporary:
            state_path = Path(temporary) / "state.json"
            progress = ProgressStore(state_path, dictionaries)
            progress.select_dictionary("graduate-core")
            word = progress.current.words[0]
            progress.mark_mastered(word)

            restored = ProgressStore(state_path, dictionaries)
            self.assertEqual(restored.current_dictionary_id, "graduate-core")
            self.assertTrue(restored.is_mastered(word))
            self.assertEqual(restored.unmastered_count, len(restored.current.words) - 1)


if __name__ == "__main__":
    unittest.main()
