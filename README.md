# Vocab terminal

A 78-column, keyboard-first vocabulary TUI modeled on the public layout of `ssh terminal.shop`: segmented navigation, a two-column workspace, centered progress text, and a compact shortcut footer.

## Standalone web checklist

`web/graduate-vocab-checklist.html` is a single-file, offline checklist containing 6,096 expanded graduate-exam entries. It can be sent directly to a learner and opened by double-clicking it.

Features:

- single-sheet paper interface with 6,096 connected vocabulary strips
- full-width serrated separators and a lifted paper strip that tears away toward the upper right
- single-click/tap opens details; double-click/tap tears off and masters a word
- random shuffle with one-click return to A–Z order
- each word opens a compact printed-dictionary page with numbered Chinese and English senses, inflections, phrases, synonyms, antonyms, derivatives, and examples
- paper-section separators, thumb-sized controls, previous/next navigation, and shareable URL hashes
- checking a known word immediately hides it from the learning list
- local browser progress storage
- English and Chinese search
- unmastered, mastered, and all-word filters
- responsive mobile layout and undo support

Rebuild it after updating the source dictionary:

```powershell
.\.venv\Scripts\python.exe tools\build_web_checklist.py
```

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

- Graduate Complete — 6,096 words
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

Graduate Complete is the deduplicated union of 4,801 ECDICT graduate-tagged headwords and 5,407 CET-6 headwords: 6,096 unique entries, all with Chinese and English definitions. LemmInflect adds morphology to 4,864 entries; Princeton WordNet adds semantic data to 5,928 entries, including phrases for 3,044 and examples for 4,879. Most AI & CS definitions also come from ECDICT. See `dictionaries/ECDICT-LICENSE.txt` and `dictionaries/WORDNET-LICENSE.txt`.

To rebuild from an ECDICT CSV export:

```powershell
.\.venv\Scripts\python.exe tools\build_dictionaries.py path\to\ecdict.csv
```

To rebuild the expanded graduate dictionary, WordNet enrichment, and standalone HTML:

```powershell
.\.venv\Scripts\python.exe tools\build_graduate_complete.py
.\.venv\Scripts\python.exe -m nltk.downloader wordnet
.\.venv\Scripts\python.exe tools\build_wordnet_extras.py
.\.venv\Scripts\python.exe tools\build_web_checklist.py
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
