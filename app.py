from __future__ import annotations

import asyncio
import json
import math
import random
from pathlib import Path

from rich.markup import escape
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import ContentSwitcher, Input, Markdown, Static

from deepseek_client import MODEL_PRESETS, DeepSeekClient
from vocab_store import DictionaryData, ProgressStore, WordEntry, load_dictionaries


NAV_WIDTHS = (15, 15, 14, 14, 14)  # 72 cells + six borders = 78
ACCENT = "#42f5c8"
QUIZ_MODES = (
    ("meaning", "Meaning choice", "English → 中文"),
    ("spelling", "Spelling", "中文 → type English"),
    ("definition", "Definition choice", "definition → word"),
    ("mixed", "Mixed practice", "random rotation"),
)


class StartupScreen(Screen[None]):
    """Short animated brand screen displayed while entering the application."""

    CSS = """
    StartupScreen {
        background: #101010;
        align: center middle;
    }

    #startup-mark {
        width: auto;
        height: 1;
        text-align: center;
    }
    """

    BINDINGS = [
        ("enter", "skip", "skip"),
        ("escape", "skip", "skip"),
    ]

    RING = ("◜", "◠", "◝", "◞", "◡", "◟")
    TEAL = (66, 245, 200)
    PURPLE = (196, 167, 231)

    def __init__(self, duration: float = 1.8) -> None:
        super().__init__()
        self.duration = duration
        self.frame = 0

    def compose(self) -> ComposeResult:
        yield Static(id="startup-mark", markup=True)

    @staticmethod
    def blend(start: tuple[int, int, int], end: tuple[int, int, int], amount: float) -> str:
        red, green, blue = (
            round(left + (right - left) * amount)
            for left, right in zip(start, end)
        )
        return f"#{red:02x}{green:02x}{blue:02x}"

    def on_mount(self) -> None:
        self.animate_brand()
        self.set_interval(0.075, self.animate_brand)
        self.set_timer(self.duration, self.finish)

    def animate_brand(self) -> None:
        letters: list[str] = []
        for index, letter in enumerate("Vocab"):
            amount = (math.sin(self.frame * 0.34 - index * 0.72) + 1) / 2
            color = self.blend(self.TEAL, self.PURPLE, amount)
            letters.append(f"[bold {color}]{letter}[/]")
        ring_color = self.blend(
            self.TEAL,
            self.PURPLE,
            (math.sin(self.frame * 0.34 + 1.4) + 1) / 2,
        )
        ring = self.RING[self.frame % len(self.RING)]
        self.query_one("#startup-mark", Static).update(
            "".join(letters) + f"  [{ring_color}]{ring}[/]"
        )
        self.frame += 1

    def finish(self) -> None:
        if self.app.screen is self:
            self.dismiss()

    def action_skip(self) -> None:
        self.finish()


class ChatMessage(Vertical):
    """A compact, visually distinct chat turn."""

    def __init__(self, role: str, message: str) -> None:
        message_class = "user-message" if role == "you" else "ai-message"
        super().__init__(classes=f"chat-message {message_class}")
        self.role = role
        self.message = message

    def compose(self) -> ComposeResult:
        if self.role == "you":
            yield Static("YOU", classes="chat-role")
            yield Static(self.message, markup=False, classes="chat-user-body")
        else:
            yield Static("VOCABOT", classes="chat-role")
            yield Markdown(self.message, classes="chat-ai-body")


class VocabApp(App[None]):
    TITLE = "Vocab"
    SUB_TITLE = "dictionary · quiz · VocaBot"

    CSS = """
    Screen {
        background: #101010;
        color: #f4f4f4;
    }

    #stage {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #shell {
        width: 78;
        height: 96%;
        max-height: 40;
        background: #101010;
    }

    #nav {
        height: 3;
        color: #666666;
    }

    #pages {
        height: 1fr;
        margin-top: 1;
    }

    .page {
        height: 1fr;
        background: #101010;
    }

    .menu {
        width: 25;
        height: 1fr;
        padding: 0 2 0 1;
        color: #797979;
        scrollbar-size: 0 0;
    }

    .detail {
        width: 1fr;
        height: 1fr;
        padding: 0 1;
        color: #eeeeee;
        scrollbar-size: 0 0;
        scrollbar-color: #8c8c8c;
        scrollbar-color-hover: #bbbbbb;
        scrollbar-color-active: #42f5c8;
        scrollbar-background: #303030;
    }

    #dic-menu-copy, #dic-detail-copy,
    #quiz-menu-copy, #quiz-detail-copy,
    #chat-menu-copy, #chat-copy,
    #settings-menu-copy, #settings-detail-copy {
        width: 100%;
        height: auto;
    }

    #chat-log {
        width: 100%;
        height: auto;
    }

    .chat-message {
        width: 100%;
        height: auto;
        margin-bottom: 1;
        padding: 0 1;
    }

    .user-message {
        width: 88%;
        margin-left: 6;
        margin-bottom: 1;
        background: #191919;
        border-right: solid #666666;
    }

    .ai-message {
        width: 96%;
        margin-right: 2;
        background: #101010;
        border-left: solid #42f5c8;
    }

    .chat-role {
        width: 100%;
        height: 1;
        text-style: bold;
    }

    .user-message .chat-role {
        color: #a0a0a0;
        text-align: right;
    }

    .ai-message .chat-role {
        color: #42f5c8;
    }

    .chat-user-body {
        width: 100%;
        height: auto;
        color: #eeeeee;
    }

    .chat-ai-body {
        width: 100%;
        height: auto;
        padding: 0;
        color: #e8e8e8;
        background: #101010;
    }

    .chat-ai-body MarkdownBlock {
        margin: 0 0 1 0;
    }

    .chat-ai-body MarkdownHeader {
        color: #f2f2f2;
        background: #101010;
        text-style: bold;
        content-align: left middle;
        margin: 0 0 1 0;
    }

    .chat-ai-body MarkdownHorizontalRule {
        height: 1;
        padding-top: 0;
        margin-bottom: 1;
        border-bottom: solid #454545;
    }

    .chat-ai-body MarkdownBullet {
        color: #42f5c8;
    }

    .chat-ai-body MarkdownBlockQuote {
        color: #d8d8d8;
        background: #181818;
        border-left: solid #555555;
    }

    .chat-ai-body MarkdownTableContent > .header {
        color: #42f5c8;
    }

    #quiz-main {
        width: 1fr;
        height: 1fr;
        padding: 0 1;
    }

    #quiz-detail {
        width: 100%;
        height: 1fr;
        padding: 0;
        scrollbar-size: 0 0;
    }

    #quiz-input {
        display: none;
    }

    #chat-menu {
        width: 21;
    }

    #chat-main {
        width: 1fr;
        height: 1fr;
        padding: 0 1;
    }

    #chat-scroll {
        height: 1fr;
        scrollbar-size: 0 0;
        scrollbar-color: #8c8c8c;
        scrollbar-color-active: #42f5c8;
        scrollbar-background: #303030;
    }

    Input {
        height: 2;
        padding: 0;
        background: #101010;
        color: #ffffff;
        border: none;
        border-top: solid #4b4b4b;
    }

    Input:focus {
        border-top: solid #42f5c8;
    }

    #chat-input:focus {
        border-top: solid #c4a7e7;
    }

    Input:disabled {
        color: #737373;
    }

    #api-key-input {
        margin-top: 2;
    }

    #statusline {
        height: 2;
        margin-top: 1;
        color: #878787;
        text-align: center;
        content-align: center middle;
    }

    #footer {
        height: 2;
        color: #6f6f6f;
        text-align: center;
    }
    """

    BINDINGS = [
        ("a", "show_dic", "dictionary"),
        ("s", "show_quiz", "quiz"),
        ("d", "show_chat", "chat"),
        ("g", "show_settings", "settings"),
        ("q", "quit", "quit"),
        ("j", "next_item", "next"),
        ("k", "previous_item", "previous"),
        ("down", "next_item", "next"),
        ("up", "previous_item", "previous"),
        ("plus", "mark_mastered", "mastered"),
        ("minus", "mark_unmastered", "unmastered"),
        ("enter", "confirm", "confirm"),
        ("1", "answer(0)", "answer 1"),
        ("2", "answer(1)", "answer 2"),
        ("3", "answer(2)", "answer 3"),
        ("4", "answer(3)", "answer 4"),
        ("p", "focus_api_key", "API key"),
        ("m", "cycle_model", "chat model"),
        ("r", "reload_dictionaries", "reload dictionaries"),
        ("escape", "back", "back"),
    ]

    def __init__(
        self,
        dictionary_dir: Path | None = None,
        state_path: Path | None = None,
        deepseek_client: DeepSeekClient | None = None,
        show_startup: bool = True,
    ) -> None:
        super().__init__()
        root = Path(__file__).resolve().parent
        self.dictionary_dir = dictionary_dir or root / "dictionaries"
        self.state_path = state_path or root / "data" / "state.json"
        self.show_startup = show_startup
        self.dictionaries = load_dictionaries(self.dictionary_dir)
        self.progress = ProgressStore(self.state_path, self.dictionaries)
        self.config_path = self.state_path.parent / "config.json"
        if deepseek_client is not None:
            self.deepseek = deepseek_client
        else:
            self.deepseek = DeepSeekClient()
            self.deepseek.select_preset(self.load_model_id())

        self.page = "dic"
        self.word_index = 0
        self.settings_index = self.dictionary_index(self.progress.current_dictionary_id)
        self.quiz_mode_index = 0
        self.quiz_effective_mode = "meaning"
        self.quiz_word: WordEntry | None = None
        self.quiz_options: list[str] = []
        self.quiz_correct_index = -1
        self.quiz_feedback: str | None = None
        self.chat_messages: list[tuple[str, str]] = [
            ("VocaBot", "Ask me to explain, compare, or use any English word.")
        ]

    @property
    def dictionary(self) -> DictionaryData:
        return self.progress.current

    def dictionary_index(self, dictionary_id: str) -> int:
        return next(
            (index for index, dictionary in enumerate(self.dictionaries) if dictionary.id == dictionary_id),
            0,
        )

    def load_model_id(self) -> str:
        if not self.config_path.exists():
            return MODEL_PRESETS[0].id
        try:
            payload = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return MODEL_PRESETS[0].id
        selected = str(payload.get("chat_model", ""))
        valid_ids = {preset.id for preset in MODEL_PRESETS}
        return selected if selected in valid_ids else MODEL_PRESETS[0].id

    def save_model_id(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.config_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({"chat_model": self.deepseek.preset_id}, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.config_path)

    def compose(self) -> ComposeResult:
        with Center(id="stage"):
            with Vertical(id="shell"):
                yield Static(id="nav", markup=True)
                with ContentSwitcher(initial="dic-page", id="pages"):
                    with Horizontal(id="dic-page", classes="page"):
                        with VerticalScroll(id="dic-menu", classes="menu"):
                            yield Static(id="dic-menu-copy", markup=True)
                        with VerticalScroll(id="dic-detail", classes="detail"):
                            yield Static(id="dic-detail-copy", markup=True)
                    with Horizontal(id="quiz-page", classes="page"):
                        with VerticalScroll(id="quiz-menu", classes="menu"):
                            yield Static(id="quiz-menu-copy", markup=True)
                        with Vertical(id="quiz-main"):
                            with VerticalScroll(id="quiz-detail"):
                                yield Static(id="quiz-detail-copy", markup=True)
                            yield Input(placeholder="type the English word...", id="quiz-input")
                    with Horizontal(id="chat-page", classes="page"):
                        with Vertical(id="chat-menu", classes="menu"):
                            yield Static(id="chat-menu-copy", markup=True)
                        with Vertical(id="chat-main"):
                            with VerticalScroll(id="chat-scroll"):
                                yield Vertical(id="chat-log")
                            yield Input(placeholder="message VocaBot...", id="chat-input")
                    with Horizontal(id="settings-page", classes="page"):
                        with VerticalScroll(id="settings-menu", classes="menu"):
                            yield Static(id="settings-menu-copy", markup=True)
                        with VerticalScroll(id="settings-detail", classes="detail"):
                            yield Static(id="settings-detail-copy", markup=True)
                            yield Input(
                                placeholder="current model API key (session only)",
                                password=True,
                                id="api-key-input",
                            )
                yield Static(id="statusline", markup=True)
                yield Static(id="footer", markup=True)

    def on_mount(self) -> None:
        self.render_dic()
        self.start_quiz()
        self.render_chat()
        self.render_settings()
        self.render_chrome()
        if self.show_startup:
            self.push_screen(StartupScreen())

    # ── Shared rendering ───────────────────────────────────────────────────

    @staticmethod
    def nav_cell(text: str, width: int, active: bool, *, logo: bool = False) -> str:
        padded = text.center(width)
        if logo:
            return f"[bold {ACCENT}]{padded}[/]"
        return f"[bold white]{padded}[/]" if active else f"[#666666]{padded}[/]"

    @staticmethod
    def footer_hint(key: str, label: str) -> str:
        return f"[bold white]{escape(key)}[/] [#777777]{escape(label)}[/]"

    def render_chrome(self) -> None:
        labels = ("Vocab", "a dic", "s quiz", "d chat", "g settings")
        active_names = ("logo", "dic", "quiz", "chat", "settings")
        top = "┌" + "┬".join("─" * width for width in NAV_WIDTHS) + "┐"
        middle = "│" + "│".join(
            self.nav_cell(
                label,
                width,
                self.page == active_names[index],
                logo=index == 0,
            )
            for index, (label, width) in enumerate(zip(labels, NAV_WIDTHS))
        ) + "│"
        bottom = "└" + "┴".join("─" * width for width in NAV_WIDTHS) + "┘"
        self.query_one("#nav", Static).update(f"[#555555]{top}[/]\n{middle}\n[#555555]{bottom}[/]")

        mastered = len(self.dictionary.words) - self.progress.unmastered_count
        api = "VocaBot ready" if self.deepseek.configured else "VocaBot key missing"
        self.query_one("#statusline", Static).update(
            f"[#878787]{escape(self.dictionary.name)} · {mastered}/{len(self.dictionary.words)} mastered · {api}[/]"
        )

        hints = {
            "dic": [(",".join(("↑", "↓")), "words"), ("+/−", "mastery"), ("s", "quiz"), ("d", "chat"), ("q", "quit")],
            "quiz": [("↑/↓", "tests"), ("1-4", "choose"), ("enter", "submit/next"), ("q", "quit")],
            "chat": [("enter", "send"), ("g", "settings"), ("a", "dictionary"), ("q", "quit")],
            "settings": [("↑/↓", "dictionary"), ("m", "model"), ("p", "API key"), ("r", "rescan"), ("q", "quit")],
        }[self.page]
        hint_line = "   ".join(self.footer_hint(key, label) for key, label in hints)
        self.query_one("#footer", Static).update(f"[#777777]{'─' * 78}[/]\n{hint_line}")

    def show_page(self, page: str, *, focus_chat: bool = False) -> None:
        self.page = page
        self.query_one("#pages", ContentSwitcher).current = f"{page}-page"
        self.render_chrome()
        if focus_chat:
            self.query_one("#chat-input", Input).focus()
        else:
            self.set_focus(None)

    # ── Dictionary ─────────────────────────────────────────────────────────

    def render_dic(self) -> None:
        total = len(self.dictionary.words)
        window_size = 16
        start = min(
            max(self.word_index - window_size // 2, 0),
            max(total - window_size, 0),
        )
        end = min(start + window_size, total)
        menu_lines = [
            f"[#777777]~ {escape(self.dictionary.name.lower())} ~[/]",
            f"[#555555]{self.word_index + 1} / {total}[/]",
            "",
        ]
        for index in range(start, end):
            word = self.dictionary.words[index]
            mastered = self.progress.is_mastered(word)
            status = "[#42f5c8]✓[/]" if mastered else " "
            color = "bold white" if index == self.word_index else "#777777"
            label = word.word if len(word.word) <= 20 else word.word[:19] + "…"
            menu_lines.append(f"[{color}]{escape(label)}[/] {status}")
        self.query_one("#dic-menu-copy", Static).update("\n".join(menu_lines))

        word = self.selected_word()
        status = "mastered" if self.progress.is_mastered(word) else "unmastered"
        detail_lines = [
            f"[bold white]{escape(word.word)}[/]",
            f"[#777777]{escape(word.phonetic)}[/]",
            "",
            f"[#777777]{escape(word.part)}[/]",
            "",
            escape(word.definition),
        ]
        if word.translation:
            detail_lines.extend(
                ["", f"[{ACCENT}]中文[/]", f"[#d0d0d0]{escape(word.translation)}[/]"]
            )
        if word.example:
            detail_lines.extend(["", f"[#777777]“{escape(word.example)}”[/]"])
        detail_lines.extend(
            ["", f"[{ACCENT}]{status}[/]", "", "[#777777]+ mastered    - unmastered[/]"]
        )
        self.query_one("#dic-detail-copy", Static).update("\n".join(detail_lines))

    def selected_word(self) -> WordEntry:
        self.word_index = min(self.word_index, len(self.dictionary.words) - 1)
        return self.dictionary.words[self.word_index]

    def action_show_dic(self) -> None:
        self.render_dic()
        self.show_page("dic")

    def action_mark_mastered(self) -> None:
        if self.page != "dic":
            return
        self.progress.mark_mastered(self.selected_word())
        self.render_dic()
        self.render_chrome()

    def action_mark_unmastered(self) -> None:
        if self.page != "dic":
            return
        self.progress.mark_unmastered(self.selected_word())
        self.render_dic()
        self.render_chrome()

    # ── Quiz ───────────────────────────────────────────────────────────────

    @staticmethod
    def quiz_meaning(word: WordEntry) -> str:
        text = word.translation or word.definition
        compact = " / ".join(line.strip() for line in text.splitlines() if line.strip())
        return compact[:117] + "…" if len(compact) > 118 else compact

    @staticmethod
    def quiz_definition(word: WordEntry) -> str:
        compact = " ".join(line.strip() for line in word.definition.splitlines() if line.strip())
        return compact[:237] + "…" if len(compact) > 238 else compact

    @staticmethod
    def normalize_spelling(value: str) -> str:
        return " ".join(value.casefold().strip().split())

    def build_quiz_choices(self, correct: str, candidates: list[str]) -> None:
        distractors = list(dict.fromkeys(value for value in candidates if value != correct))
        choices = random.sample(distractors, k=min(3, len(distractors))) + [correct]
        random.shuffle(choices)
        self.quiz_options = choices
        self.quiz_correct_index = choices.index(correct)

    def start_quiz(self) -> None:
        pool = self.progress.unmastered_words or list(self.dictionary.words)
        self.quiz_word = random.choice(pool)
        selected_mode = QUIZ_MODES[self.quiz_mode_index][0]
        self.quiz_effective_mode = (
            random.choice(("meaning", "spelling", "definition"))
            if selected_mode == "mixed"
            else selected_mode
        )

        if self.quiz_effective_mode == "meaning":
            correct = self.quiz_meaning(self.quiz_word)
            self.build_quiz_choices(
                correct,
                [self.quiz_meaning(word) for word in self.dictionary.words],
            )
        elif self.quiz_effective_mode == "definition":
            self.build_quiz_choices(
                self.quiz_word.word,
                [word.word for word in self.dictionary.words],
            )
        else:
            self.quiz_options = []
            self.quiz_correct_index = -1

        self.quiz_feedback = None
        if self.is_mounted:
            self.render_quiz()

    def render_quiz_menu(self) -> None:
        lines = ["[#777777]~ tests ~[/]", ""]
        for index, (_, name, description) in enumerate(QUIZ_MODES):
            color = "bold white" if index == self.quiz_mode_index else "#777777"
            lines.extend(
                [
                    f"[{color}]{escape(name)}[/]",
                    f"[#555555]{escape(description)}[/]",
                    "",
                ]
            )
        self.query_one("#quiz-menu-copy", Static).update("\n".join(lines))

    def render_quiz(self) -> None:
        if not self.quiz_word:
            return
        self.render_quiz_menu()
        quiz_input = self.query_one("#quiz-input", Input)
        spelling = self.quiz_effective_mode == "spelling"
        quiz_input.display = spelling
        quiz_input.disabled = self.quiz_feedback is not None
        if not spelling:
            quiz_input.value = ""

        selected_mode = QUIZ_MODES[self.quiz_mode_index][0]
        mode_note = (
            f" · mixed: {self.quiz_effective_mode}"
            if selected_mode == "mixed"
            else ""
        )
        if self.quiz_effective_mode == "meaning":
            lines = [
                f"[#777777]meaning choice{mode_note}[/]",
                "",
                f"[bold white]{escape(self.quiz_word.word)}[/]  [#777777]{escape(self.quiz_word.phonetic)}[/]",
                "",
            ]
            for index, option in enumerate(self.quiz_options):
                color = ACCENT if self.quiz_feedback is not None and index == self.quiz_correct_index else "#b8b8b8"
                lines.extend([f"[{color}]{index + 1}. {escape(option)}[/]", ""])
        elif self.quiz_effective_mode == "definition":
            lines = [
                f"[#777777]definition choice{mode_note}[/]",
                "",
                escape(self.quiz_definition(self.quiz_word)),
                "",
            ]
            for index, option in enumerate(self.quiz_options):
                color = ACCENT if self.quiz_feedback is not None and index == self.quiz_correct_index else "#b8b8b8"
                lines.extend([f"[{color}]{index + 1}. {escape(option)}[/]", ""])
        else:
            lines = [
                f"[#777777]spelling{mode_note}[/]",
                "",
                f"[{ACCENT}]中文释义[/]",
                escape(self.quiz_word.translation or self.quiz_word.definition),
                "",
                "[#777777]type the English word below and press enter[/]",
            ]

        if self.quiz_feedback:
            lines.extend(
                [
                    "",
                    "[#555555]" + "─" * 50 + "[/]",
                    self.quiz_feedback,
                    "",
                    f"[bold white]{escape(self.quiz_word.word)}[/]  [#777777]{escape(self.quiz_word.phonetic)}[/]",
                    f"[{ACCENT}]中文[/]  {escape(self.quiz_word.translation)}",
                    "",
                    "[#777777]enter next question[/]",
                ]
            )
        self.query_one("#quiz-detail-copy", Static).update("\n".join(lines))
        if spelling and self.quiz_feedback is None and self.page == "quiz":
            self.call_after_refresh(quiz_input.focus)

    def finish_quiz_answer(self, correct: bool) -> None:
        assert self.quiz_word is not None
        if correct:
            self.progress.mark_mastered(self.quiz_word)
            self.quiz_feedback = f"[{ACCENT}]correct[/]  [#777777]marked as mastered[/]"
        else:
            self.quiz_feedback = f"[#ff6b5f]not quite[/]  [#777777]answer shown below[/]"
        self.render_quiz()
        self.render_dic()
        self.render_chrome()

    def action_show_quiz(self) -> None:
        self.show_page("quiz")
        self.render_quiz()

    def action_answer(self, index: int) -> None:
        if (
            self.page != "quiz"
            or self.quiz_effective_mode == "spelling"
            or self.quiz_feedback is not None
            or index >= len(self.quiz_options)
        ):
            return
        self.finish_quiz_answer(index == self.quiz_correct_index)

    @on(Input.Submitted, "#quiz-input")
    def submit_spelling(self, event: Input.Submitted) -> None:
        if self.page != "quiz" or self.quiz_effective_mode != "spelling" or self.quiz_feedback is not None:
            return
        assert self.quiz_word is not None
        answer = self.normalize_spelling(event.value)
        if not answer:
            return
        event.stop()
        self.finish_quiz_answer(answer == self.normalize_spelling(self.quiz_word.word))

    # ── VocaBot chat ───────────────────────────────────────────────────────

    def render_chat(self) -> None:
        self.query_one("#chat-menu-copy", Static).update(
            "[#777777]~ VocaBot ~[/]\n\n"
            "[white]explain[/]\n"
            "[#777777]a word[/]\n\n"
            "[white]compare[/]\n"
            "[#777777]two words[/]\n\n"
            "[white]examples[/]\n"
            "[#777777]in context[/]"
        )
        chat_log = self.query_one("#chat-log", Vertical)
        chat_log.remove_children()
        chat_log.mount(
            *(ChatMessage(role, message) for role, message in self.chat_messages[-20:])
        )
        if self.is_mounted:
            self.call_after_refresh(self.query_one("#chat-scroll", VerticalScroll).scroll_end, animate=False)

    @on(Input.Submitted, "#chat-input")
    def submit_chat(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return
        event.input.value = ""
        event.input.disabled = True
        history = list(self.chat_messages)
        self.chat_messages.extend([("you", query), ("VocaBot", "thinking...")])
        self.render_chat()
        self.ask_vocabot(query, history)

    @work(exclusive=True, group="vocabot-chat")
    async def ask_vocabot(self, query: str, history: list[tuple[str, str]]) -> None:
        try:
            response = await asyncio.to_thread(
                self.deepseek.explain,
                query,
                history,
                self.dictionary.name,
            )
        except Exception:
            response = "VocaBot error: request failed. Check the selected model and API key in Settings."
        self.chat_messages[-1] = ("VocaBot", response)
        chat_input = self.query_one("#chat-input", Input)
        chat_input.disabled = False
        chat_input.focus()
        self.render_chat()
        self.render_chrome()

    def action_show_chat(self) -> None:
        self.render_chat()
        self.show_page("chat", focus_chat=True)

    # ── Settings ───────────────────────────────────────────────────────────

    def render_settings(self) -> None:
        menu = ["[#777777]~ dictionaries ~[/]", ""]
        for index, dictionary in enumerate(self.dictionaries):
            color = "bold white" if index == self.settings_index else "#777777"
            active = f" [{ACCENT}]●[/]" if dictionary.id == self.progress.current_dictionary_id else ""
            menu.append(f"[{color}]{escape(dictionary.name)}[/]{active}")
        self.query_one("#settings-menu-copy", Static).update("\n".join(menu))

        selected = self.dictionaries[self.settings_index]
        api_status = f"[{ACCENT}]ready[/]" if self.deepseek.configured else "[#ff8a65]key missing[/]"
        lines = [
            f"[bold white]{escape(selected.name)}[/]",
            "",
            escape(selected.description),
            "",
            f"[#777777]{len(selected.words)} words\n{escape(selected.path.name)}[/]",
            "",
            "[#555555]" + "─" * 50 + "[/]",
            "",
            "[white]VocaBot model[/]",
        ]
        for preset in MODEL_PRESETS:
            if preset.id == self.deepseek.preset_id:
                lines.append(f"[{ACCENT}]●[/] [bold white]{escape(preset.name)}[/]")
            else:
                lines.append(f"  [#666666]{escape(preset.name)}[/]")
        lines.extend(
            [
                "",
                f"status: {api_status}",
                f"[#777777]provider: {escape(self.deepseek.provider)}[/]",
                "",
                "[#777777]press m to switch model\n"
                "press p to enter this provider's API key\n"
                "the key remains in memory for this session only[/]",
            ]
        )
        self.query_one("#settings-detail-copy", Static).update("\n".join(lines))
        self.query_one("#api-key-input", Input).placeholder = (
            f"{self.deepseek.display_name} API key (session only)"
        )

    def action_show_settings(self) -> None:
        self.settings_index = self.dictionary_index(self.progress.current_dictionary_id)
        self.render_settings()
        self.show_page("settings")

    def action_cycle_model(self) -> None:
        if self.page != "settings":
            return
        current = next(
            (
                index
                for index, preset in enumerate(MODEL_PRESETS)
                if preset.id == self.deepseek.preset_id
            ),
            0,
        )
        selected = MODEL_PRESETS[(current + 1) % len(MODEL_PRESETS)]
        self.deepseek.select_preset(selected.id)
        self.save_model_id()
        self.render_settings()
        self.render_chrome()

    def action_focus_api_key(self) -> None:
        if self.page == "settings":
            self.query_one("#api-key-input", Input).focus()

    @on(Input.Submitted, "#api-key-input")
    def save_api_key(self, event: Input.Submitted) -> None:
        key = event.value.strip()
        if key:
            self.deepseek.set_api_key(key)
            event.input.value = ""
            self.render_settings()
            self.render_chat()
            self.render_chrome()
        event.stop()

    def apply_dictionary(self) -> None:
        dictionary = self.dictionaries[self.settings_index]
        self.progress.select_dictionary(dictionary.id)
        self.word_index = 0
        self.quiz_word = None
        self.start_quiz()
        self.render_dic()
        self.render_settings()
        self.render_chrome()

    def action_reload_dictionaries(self) -> None:
        if self.page != "settings":
            return
        try:
            dictionaries = load_dictionaries(self.dictionary_dir)
        except (OSError, ValueError) as error:
            self.notify(str(error), severity="error")
            return
        self.dictionaries = dictionaries
        self.progress = ProgressStore(self.state_path, dictionaries)
        self.settings_index = self.dictionary_index(self.progress.current_dictionary_id)
        self.word_index = 0
        self.quiz_word = None
        self.start_quiz()
        self.render_dic()
        self.render_settings()
        self.render_chrome()

    # ── Shared actions ─────────────────────────────────────────────────────

    def action_next_item(self) -> None:
        if self.page == "dic":
            self.word_index = (self.word_index + 1) % len(self.dictionary.words)
            self.render_dic()
        elif self.page == "quiz":
            self.quiz_mode_index = (self.quiz_mode_index + 1) % len(QUIZ_MODES)
            self.start_quiz()
        elif self.page == "settings":
            self.settings_index = (self.settings_index + 1) % len(self.dictionaries)
            self.render_settings()

    def action_previous_item(self) -> None:
        if self.page == "dic":
            self.word_index = (self.word_index - 1) % len(self.dictionary.words)
            self.render_dic()
        elif self.page == "quiz":
            self.quiz_mode_index = (self.quiz_mode_index - 1) % len(QUIZ_MODES)
            self.start_quiz()
        elif self.page == "settings":
            self.settings_index = (self.settings_index - 1) % len(self.dictionaries)
            self.render_settings()

    def action_confirm(self) -> None:
        if self.page == "dic":
            word = self.selected_word()
            if self.progress.is_mastered(word):
                self.progress.mark_unmastered(word)
            else:
                self.progress.mark_mastered(word)
            self.render_dic()
            self.render_chrome()
        elif self.page == "quiz" and self.quiz_feedback is not None:
            self.start_quiz()
        elif self.page == "settings":
            self.apply_dictionary()
            self.action_show_dic()

    def action_back(self) -> None:
        if self.page != "dic":
            self.action_show_dic()


if __name__ == "__main__":
    VocabApp().run()
