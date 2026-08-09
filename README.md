# Vocab terminal

A 78-column, keyboard-first vocabulary TUI modeled on the public layout of `ssh terminal.shop`: segmented navigation, a two-column workspace, centered progress text, and a compact shortcut footer.

## Run

```powershell
cd "C:\Users\xjwQZ\Documents\PI for learning\vocab-tui"
.\run.cmd
```

## Navigation

- `a` — dictionary
- `s` — quiz
- `d` — dictionary chat
- `g` — settings
- `q` — quit
- `↑` / `↓` or `j` / `k` — move selection

## Dictionary

- `+` — mark the selected word as mastered
- `-` — mark it as unmastered
- `Enter` — toggle mastery
- English definitions and Chinese translations are shown together
- Large dictionaries use a windowed word list for responsive navigation

Progress is persisted in `data/state.json`.

## Quiz

Use `↑` / `↓` to switch between four test modes:

- **Meaning choice** — English word → choose its Chinese meaning with `1`–`4`
- **Spelling** — Chinese meaning → type the English word and press `Enter`
- **Definition choice** — English definition → choose the matching word with `1`–`4`
- **Mixed practice** — randomly rotates through the three modes

Correct answers are marked as mastered, questions prioritize unmastered words, and `Enter` advances after feedback.

## VocaBot chat

Open Chat with `d`. The interface always identifies the tutor as **VocaBot**, independently of the provider selected in Settings.

Available models:

- DeepSeek Chat
- DeepSeek Reasoner
- OpenAI GPT-4o mini
- OpenAI GPT-4.1 mini

Open Settings with `g` and press `m` to switch models. The selection is saved in `data/config.json`.

Credential resolution order for the selected provider:

1. `DEEPSEEK_API_KEY` or `OPENAI_API_KEY`
2. A matching credential previously stored through pi's `/login`
3. A session-only key entered in Settings with `p`

Keys entered in Settings are masked, kept only in memory, and never written to the project.

Examples:

```text
explain ambiguous
compare implicit and explicit
give me examples of undermine
```

## Change or add dictionaries

Open settings with `g`, select a dictionary with `↑` / `↓`, then press `Enter`.

Built-in bilingual dictionaries:

- Graduate Core — 4,801 words
- AI & CS — 172 curated terms
- CET-6 — 5,407 words

To add another dictionary, place a JSON file in `dictionaries/`, open settings, and press `r` to rescan. Schema:

```json
{
  "id": "my-dictionary",
  "name": "My Dictionary",
  "description": "Description",
  "words": [
    {
      "word": "example",
      "phonetic": "/ɪɡˈzɑːmpl/",
      "part": "noun",
      "definition": "something used to illustrate a rule",
      "translation": "例子；实例；范例",
      "example": "This sentence is an example."
    }
  ]
}
```

## Dictionary data

Graduate Core and CET-6, plus most AI & CS definitions, are extracted from the MIT-licensed [ECDICT](https://github.com/skywind3000/ECDICT) project. See `dictionaries/ECDICT-LICENSE.txt`.

To rebuild from an ECDICT CSV export:

```powershell
.\.venv\Scripts\python.exe tools\build_dictionaries.py path\to\ecdict.csv
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
