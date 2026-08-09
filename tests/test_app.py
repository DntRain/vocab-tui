import tempfile
import unittest
from pathlib import Path

from textual.widgets import ContentSwitcher, Input, Markdown, Static

from app import VocabApp
from deepseek_client import DeepSeekClient


ROOT = Path(__file__).resolve().parents[1]


class FakeDeepSeek(DeepSeekClient):
    def __init__(self):
        super().__init__(api_key="test")

    def explain(self, query, history, dictionary_name):
        return f"## Explanation\n\n**{query}** from {dictionary_name}\n\n- first point\n- second point"


class AppSmokeTests(unittest.IsolatedAsyncioTestCase):
    async def test_dictionary_quiz_settings_flow(self):
        with tempfile.TemporaryDirectory() as temporary:
            app = VocabApp(
                dictionary_dir=ROOT / "dictionaries",
                state_path=Path(temporary) / "state.json",
                deepseek_client=FakeDeepSeek(),
                show_startup=False,
            )
            async with app.run_test(size=(100, 32)) as pilot:
                pages = app.query_one("#pages", ContentSwitcher)
                self.assertEqual(pages.current, "dic-page")
                self.assertNotIn("left", app.query_one("#nav", Static).render().plain)
                initial_left = app.progress.unmastered_count

                await pilot.press("plus")
                self.assertEqual(app.progress.unmastered_count, initial_left - 1)

                await pilot.press("s")
                self.assertEqual(pages.current, "quiz-page")
                self.assertEqual(app.quiz_effective_mode, "meaning")

                await pilot.press("down")
                self.assertEqual(app.quiz_effective_mode, "spelling")
                spelling_word = app.quiz_word
                spelling_input = app.query_one("#quiz-input", Input)
                self.assertTrue(spelling_input.display)
                spelling_input.value = spelling_word.word
                await pilot.press("enter")
                await pilot.pause()
                self.assertTrue(app.progress.is_mastered(spelling_word))
                self.assertIsNotNone(app.quiz_feedback)

                await pilot.press("d")
                self.assertEqual(pages.current, "chat-page")
                chat_menu = app.query_one("#chat-menu-copy", Static).render().plain
                self.assertIn("VocaBot", chat_menu)
                self.assertNotIn("DeepSeek", chat_menu)
                chat_input = app.query_one("#chat-input", Input)
                chat_input.value = app.dictionary.words[0].word
                await pilot.press("enter")
                await pilot.pause()
                self.assertGreaterEqual(len(app.chat_messages), 3)
                self.assertIn("## Explanation", app.chat_messages[-1][1])
                self.assertIn("## Explanation", app.query(".chat-ai-body").last(Markdown).source)
                self.assertEqual(len(app.query(".user-message")), 1)
                self.assertGreaterEqual(len(app.query(".ai-message")), 2)

                await pilot.press("escape", "g")
                self.assertEqual(pages.current, "settings-page")
                old_model = app.deepseek.preset_id
                await pilot.press("m")
                self.assertNotEqual(app.deepseek.preset_id, old_model)
                self.assertTrue((Path(temporary) / "config.json").exists())

                old_dictionary = app.progress.current_dictionary_id
                await pilot.press("down", "enter")
                self.assertNotEqual(app.progress.current_dictionary_id, old_dictionary)
                self.assertEqual(pages.current, "dic-page")


if __name__ == "__main__":
    unittest.main()
