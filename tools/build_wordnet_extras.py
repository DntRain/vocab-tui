from __future__ import annotations

import json
from pathlib import Path

from nltk.corpus import wordnet as wn


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dictionaries" / "graduate-core.json"
OUTPUT = ROOT / "resources" / "graduate-wordnet.json"


def clean_lemma(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").strip()


def unique(values: list[str], *, exclude: str = "", limit: int = 8) -> list[str]:
    result: list[str] = []
    seen = {exclude.casefold()}
    for value in values:
        cleaned = clean_lemma(value)
        key = cleaned.casefold()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
        if len(result) >= limit:
            break
    return result


def main() -> None:
    words = json.loads(SOURCE.read_text(encoding="utf-8"))["words"]
    extras: dict[str, dict[str, list[str]]] = {}

    for item in words:
        word = str(item["word"])
        lookup = word.replace(" ", "_")
        synonyms: list[str] = []
        antonyms: list[str] = []
        examples: list[str] = []
        related: list[str] = []

        for synset in wn.synsets(lookup):
            examples.extend(synset.examples())
            for lemma in synset.lemmas():
                synonyms.append(lemma.name())
                antonyms.extend(antonym.name() for antonym in lemma.antonyms())
                related.extend(form.name() for form in lemma.derivationally_related_forms())

        entry = {
            "synonyms": unique(synonyms, exclude=word, limit=8),
            "antonyms": unique(antonyms, exclude=word, limit=6),
            "related": unique(related, exclude=word, limit=8),
            "examples": unique(examples, limit=3),
        }
        if any(entry.values()):
            extras[word.casefold()] = entry

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(extras, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote WordNet extras for {len(extras):,} of {len(words):,} words to {OUTPUT}")


if __name__ == "__main__":
    main()
