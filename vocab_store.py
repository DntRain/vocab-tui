from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class WordEntry:
    word: str
    phonetic: str
    part: str
    definition: str
    translation: str
    example: str


@dataclass(frozen=True, slots=True)
class DictionaryData:
    id: str
    name: str
    description: str
    words: tuple[WordEntry, ...]
    path: Path


def load_dictionaries(directory: Path) -> list[DictionaryData]:
    dictionaries: list[DictionaryData] = []
    for path in sorted(directory.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        required = {"id", "name", "description", "words"}
        missing = required - payload.keys()
        if missing:
            raise ValueError(f"{path.name}: missing {', '.join(sorted(missing))}")

        words = tuple(
            WordEntry(
                word=str(item["word"]).strip(),
                phonetic=str(item.get("phonetic", "")).strip(),
                part=str(item.get("part", "word")).strip(),
                definition=str(item["definition"]).strip(),
                translation=str(item.get("translation", item.get("definition_zh", ""))).strip(),
                example=str(item.get("example", "")).strip(),
            )
            for item in payload["words"]
        )
        if not words:
            raise ValueError(f"{path.name}: dictionary contains no words")
        if len({word.word.casefold() for word in words}) != len(words):
            raise ValueError(f"{path.name}: duplicate words")

        dictionaries.append(
            DictionaryData(
                id=str(payload["id"]).strip(),
                name=str(payload["name"]).strip(),
                description=str(payload["description"]).strip(),
                words=words,
                path=path,
            )
        )

    if not dictionaries:
        raise ValueError(f"no dictionary JSON files found in {directory}")
    if len({dictionary.id for dictionary in dictionaries}) != len(dictionaries):
        raise ValueError("dictionary ids must be unique")

    preferred_order = {"graduate-core": 0, "ai-cs": 1, "cet6": 2}
    dictionaries.sort(key=lambda item: (preferred_order.get(item.id, 100), item.name.casefold()))
    return dictionaries


class ProgressStore:
    def __init__(self, path: Path, dictionaries: list[DictionaryData]) -> None:
        self.path = path
        self.dictionaries = dictionaries
        self.current_dictionary_id = dictionaries[0].id
        self.mastered: dict[str, set[str]] = {dictionary.id: set() for dictionary in dictionaries}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        valid_ids = {dictionary.id for dictionary in self.dictionaries}
        selected = payload.get("current_dictionary")
        if selected in valid_ids:
            self.current_dictionary_id = selected

        stored = payload.get("mastered", {})
        if isinstance(stored, dict):
            for dictionary in self.dictionaries:
                values = stored.get(dictionary.id, [])
                valid_words = {word.word.casefold() for word in dictionary.words}
                if isinstance(values, list):
                    self.mastered[dictionary.id] = {
                        str(value).casefold() for value in values if str(value).casefold() in valid_words
                    }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "current_dictionary": self.current_dictionary_id,
            "mastered": {key: sorted(values) for key, values in self.mastered.items()},
        }
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary.replace(self.path)

    @property
    def current(self) -> DictionaryData:
        return next(dictionary for dictionary in self.dictionaries if dictionary.id == self.current_dictionary_id)

    def select_dictionary(self, dictionary_id: str) -> None:
        if dictionary_id not in {dictionary.id for dictionary in self.dictionaries}:
            raise KeyError(dictionary_id)
        self.current_dictionary_id = dictionary_id
        self.mastered.setdefault(dictionary_id, set())
        self.save()

    def is_mastered(self, word: WordEntry, dictionary_id: str | None = None) -> bool:
        key = dictionary_id or self.current_dictionary_id
        return word.word.casefold() in self.mastered.setdefault(key, set())

    def mark_mastered(self, word: WordEntry) -> None:
        self.mastered.setdefault(self.current_dictionary_id, set()).add(word.word.casefold())
        self.save()

    def mark_unmastered(self, word: WordEntry) -> None:
        self.mastered.setdefault(self.current_dictionary_id, set()).discard(word.word.casefold())
        self.save()

    @property
    def unmastered_words(self) -> list[WordEntry]:
        return [word for word in self.current.words if not self.is_mastered(word)]

    @property
    def unmastered_count(self) -> int:
        return len(self.unmastered_words)
