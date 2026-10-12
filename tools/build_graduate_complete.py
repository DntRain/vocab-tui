from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lemminflect import getAllInflections


ROOT = Path(__file__).resolve().parents[1]
GRADUATE = ROOT / "dictionaries" / "graduate-core.json"
CET6 = ROOT / "dictionaries" / "cet6.json"
BASE_WORDS = ROOT / "resources" / "graduate-base-words.txt"

FORM_LABELS = {
    "NNS": "复数",
    "VBD": "过去式",
    "VBN": "过去分词",
    "VBG": "现在分词",
    "VBZ": "第三人称单数",
    "JJR": "比较级",
    "JJS": "最高级",
}


def load_words(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["words"]


def build_forms(word: str) -> dict[str, list[str]]:
    if not word.isascii() or not word.replace("-", "").isalpha():
        return {}
    forms: dict[str, list[str]] = {}
    for tag, values in getAllInflections(word).items():
        label = FORM_LABELS.get(tag)
        if not label:
            continue
        cleaned = list(
            dict.fromkeys(
                value
                for value in values
                if value.casefold() != word.casefold() and value.isascii()
            )
        )
        if cleaned:
            forms[label] = cleaned[:3]
    return forms


def main() -> None:
    available_graduate_words = load_words(GRADUATE)
    graduate_index = {
        item["word"].casefold(): item for item in available_graduate_words
    }
    base_keys = [
        line.strip().casefold()
        for line in BASE_WORDS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    missing = [key for key in base_keys if key not in graduate_index]
    if missing:
        raise ValueError(f"Graduate base manifest is missing {len(missing)} entries")
    graduate_words = [graduate_index[key] for key in base_keys]
    cet6_words = load_words(CET6)

    merged: dict[str, dict[str, Any]] = {}
    for item in graduate_words:
        merged[item["word"].casefold()] = dict(item)
    for item in cet6_words:
        merged.setdefault(item["word"].casefold(), dict(item))

    words = sorted(merged.values(), key=lambda item: item["word"].casefold())
    for item in words:
        item["forms"] = build_forms(str(item["word"]))

    payload = {
        "id": "graduate-core",
        "name": "Graduate Complete",
        "description": "考研英语完整扩展词库 · 大纲核心词、六级补充词、词形变化与多义释义",
        "source": "ECDICT ky + CET-6 union; morphology generated with LemmInflect",
        "coverage": {
            "graduate_source": len(graduate_words),
            "cet6_source": len(cet6_words),
            "merged_unique": len(words),
        },
        "words": words,
    }
    GRADUATE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(words):,} expanded graduate entries to {GRADUATE}")


if __name__ == "__main__":
    main()
