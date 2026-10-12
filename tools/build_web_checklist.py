from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dictionaries" / "graduate-core.json"
EXTRAS = ROOT / "resources" / "graduate-wordnet.json"
OUTPUT = ROOT / "web" / "graduate-vocab-checklist.html"


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    extras = json.loads(EXTRAS.read_text(encoding="utf-8")) if EXTRAS.exists() else {}
    words = [
        {
            "n": index,
            "w": item["word"],
            "p": item.get("phonetic", ""),
            "pos": item.get("part", "word"),
            "d": item.get("definition", ""),
            "t": item.get("translation", ""),
            "e": item.get("example", ""),
            "forms": item.get("forms", {}),
            "syn": extras.get(item["word"].casefold(), {}).get("synonyms", []),
            "ant": extras.get(item["word"].casefold(), {}).get("antonyms", []),
            "rel": extras.get(item["word"].casefold(), {}).get("related", []),
            "phr": extras.get(item["word"].casefold(), {}).get("phrases", []),
            "wx": extras.get(item["word"].casefold(), {}).get("examples", []),
        }
        for index, item in enumerate(payload["words"], start=1)
    ]
    word_data = json.dumps(words, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    document = TEMPLATE.replace("__WORD_COUNT__", f"{len(words):,}").replace("__WORD_DATA__", word_data)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(document, encoding="utf-8")
    print(f"Wrote {len(words):,} words to {OUTPUT}")


TEMPLATE = r'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>考研词汇清单</title>
  <style>
    :root {
      --bg: #f3f6f5;
      --paper: #ffffff;
      --ink: #14201d;
      --muted: #74807c;
      --line: rgba(41, 65, 59, .11);
      --accent: #12b99a;
      --accent-soft: #e7f8f3;
      --purple: #aa8fd2;
      --danger: #b34c54;
      --shadow: 0 18px 55px rgba(28, 50, 44, .075);
      --shadow-hover: 0 24px 65px rgba(28, 50, 44, .11);
    }

    * { box-sizing: border-box; }

    html { scroll-behavior: smooth; }

    body {
      min-height: 100vh;
      margin: 0;
      background:
        radial-gradient(circle at 12% 0%, rgba(18, 185, 154, .10), transparent 28rem),
        radial-gradient(circle at 92% 14%, rgba(170, 143, 210, .11), transparent 27rem),
        var(--bg);
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
      -webkit-font-smoothing: antialiased;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      z-index: -1;
      opacity: .28;
      pointer-events: none;
      background-image: radial-gradient(rgba(40, 64, 58, .16) .55px, transparent .55px);
      background-size: 18px 18px;
      mask-image: linear-gradient(to bottom, black, transparent 65%);
    }

    button, input { font: inherit; }

    .app {
      width: min(980px, calc(100% - 28px));
      margin: 34px auto 64px;
      animation: app-in .65s cubic-bezier(.2, .75, .25, 1) both;
    }

    .hero {
      position: relative;
      isolation: isolate;
      overflow: hidden;
      margin-bottom: 18px;
      padding: 25px 27px 24px;
      border: 1px solid rgba(255, 255, 255, .8);
      border-radius: 20px;
      background: rgba(255, 255, 255, .86);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
      transition: box-shadow .3s ease, translate .3s ease;
    }

    .hero:hover { box-shadow: var(--shadow-hover); translate: 0 -1px; }

    .hero::before {
      content: "";
      position: absolute;
      inset: 0;
      z-index: -2;
      padding: 1px;
      border-radius: inherit;
      background: linear-gradient(115deg, rgba(18, 185, 154, .48), rgba(255, 255, 255, .6) 38%, rgba(170, 143, 210, .5));
      mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
      mask-composite: exclude;
    }

    .hero::after {
      content: "";
      position: absolute;
      right: -58px;
      top: -95px;
      z-index: -1;
      width: 250px;
      height: 250px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(170, 143, 210, .15), rgba(18, 185, 154, .05) 48%, transparent 70%);
      animation: breathe 7s ease-in-out infinite;
    }

    .hero-top,
    .toolbar,
    .summary,
    .empty-state,
    .footer {
      display: flex;
      align-items: center;
    }

    .hero-top { justify-content: space-between; gap: 16px; }

    .eyebrow {
      margin: 0 0 6px;
      color: #82908c;
      font-size: 10px;
      font-weight: 750;
      letter-spacing: .18em;
    }

    h1 {
      margin: 0;
      font-size: clamp(26px, 4vw, 36px);
      font-weight: 760;
      letter-spacing: -.055em;
      line-height: 1.12;
    }

    .brand-accent {
      background: linear-gradient(100deg, var(--accent), var(--purple), var(--accent));
      background-size: 220% 100%;
      color: transparent;
      background-clip: text;
      -webkit-background-clip: text;
      animation: gradient-flow 5s ease-in-out infinite;
    }

    .subtitle {
      margin: 7px 0 0;
      color: var(--muted);
      font-size: 14px;
    }

    .summary {
      flex: 0 0 auto;
      gap: 5px;
      padding: 9px 12px;
      border: 1px solid rgba(41, 65, 59, .08);
      border-radius: 999px;
      background: rgba(247, 250, 249, .82);
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, .8);
    }

    .summary strong {
      color: var(--ink);
      font-size: 18px;
      font-variant-numeric: tabular-nums;
    }

    .progress-track {
      height: 6px;
      margin-top: 22px;
      overflow: hidden;
      border-radius: 999px;
      background: rgba(28, 58, 50, .075);
      box-shadow: inset 0 1px 2px rgba(28, 58, 50, .05);
    }

    .progress-bar {
      position: relative;
      width: 0;
      height: 100%;
      overflow: hidden;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--accent), var(--purple));
      transition: width .45s cubic-bezier(.2, .75, .25, 1);
    }

    .progress-bar::after {
      content: "";
      position: absolute;
      inset: 0;
      translate: -120% 0;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, .7), transparent);
      animation: progress-shine 3.4s ease-in-out infinite;
    }

    .toolbar {
      position: sticky;
      top: 10px;
      z-index: 10;
      gap: 10px;
      margin-bottom: 12px;
      padding: 10px;
      border: 1px solid rgba(255, 255, 255, .78);
      border-radius: 15px;
      background: rgba(255, 255, 255, .82);
      box-shadow: 0 12px 35px rgba(25, 52, 45, .075);
      backdrop-filter: blur(20px) saturate(135%);
      animation: surface-in .6s .08s cubic-bezier(.2, .75, .25, 1) both;
    }

    .search-wrap { position: relative; flex: 1 1 320px; }

    .search-icon {
      position: absolute;
      left: 13px;
      top: 50%;
      width: 16px;
      height: 16px;
      translate: 0 -50%;
      color: #8a9491;
      pointer-events: none;
    }

    .search {
      width: 100%;
      height: 42px;
      padding: 0 14px 0 39px;
      border: 1px solid var(--line);
      border-radius: 10px;
      outline: none;
      background: rgba(248, 251, 250, .9);
      color: var(--ink);
      transition: border-color .2s, box-shadow .2s, background .2s;
    }

    .search:hover { background: #fff; }

    .search:focus {
      border-color: var(--purple);
      box-shadow: 0 0 0 3px rgba(170, 143, 210, .16);
    }

    .filters { display: flex; gap: 5px; }

    .filter,
    .text-button {
      min-height: 38px;
      border: 0;
      border-radius: 9px;
      background: transparent;
      color: var(--muted);
      cursor: pointer;
    }

    .filter {
      padding: 0 13px;
      transition: color .18s, background .18s, transform .18s, box-shadow .18s;
    }

    .filter:hover,
    .text-button:hover { color: var(--ink); background: #f1f4f3; }

    .filter:active { transform: scale(.97); }

    .filter.active {
      background: linear-gradient(135deg, #e3f8f2, #f0ebf8);
      color: #087b68;
      font-weight: 680;
      box-shadow: inset 0 0 0 1px rgba(18, 185, 154, .08), 0 4px 12px rgba(61, 104, 93, .07);
    }

    .list-card {
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, .82);
      border-radius: 18px;
      background: rgba(255, 255, 255, .92);
      box-shadow: var(--shadow);
      animation: surface-in .65s .16s cubic-bezier(.2, .75, .25, 1) both;
    }

    .list-head,
    .word-row {
      display: grid;
      grid-template-columns: 50px minmax(170px, .75fr) minmax(110px, .65fr) minmax(250px, 1.7fr);
      align-items: center;
    }

    .list-head {
      min-height: 42px;
      padding: 0 18px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(90deg, rgba(247, 250, 249, .96), rgba(251, 249, 253, .96));
      color: #929b98;
      font-size: 12px;
      font-weight: 650;
      letter-spacing: .08em;
      text-transform: uppercase;
    }

    .word-row {
      min-height: 62px;
      padding: 9px 18px;
      border-bottom: 1px solid var(--line);
      animation: row-in .42s calc(var(--row-delay, 0) * 1ms) cubic-bezier(.2, .75, .25, 1) both;
      transition: opacity .22s, translate .22s, background .18s, box-shadow .18s;
    }

    .word-row:last-child { border-bottom: 0; }
    .word-row:hover {
      z-index: 1;
      background: linear-gradient(90deg, rgba(235, 249, 245, .58), rgba(247, 243, 251, .38));
      box-shadow: inset 3px 0 var(--accent);
      translate: 2px 0;
    }
    .word-row.completing { opacity: 0; translate: 15px 0; }
    .word-row.mastered { opacity: .58; }

    .check {
      display: inline-grid;
      width: 23px;
      height: 23px;
      margin: 0;
      appearance: none;
      place-items: center;
      border: 1.5px solid #c4cecb;
      border-radius: 7px;
      background: white;
      cursor: pointer;
      transition: border-color .18s, background .18s, transform .18s, box-shadow .18s;
    }

    .check:hover {
      border-color: var(--accent);
      transform: scale(1.07);
      box-shadow: 0 0 0 4px rgba(18, 185, 154, .08);
    }

    .check:checked {
      border-color: var(--accent);
      background: linear-gradient(135deg, var(--accent), #55cbb5);
      box-shadow: 0 5px 13px rgba(18, 185, 154, .24);
      animation: check-pop .26s ease-out;
    }

    .check:checked::after {
      content: "";
      width: 9px;
      height: 5px;
      translate: 0 -1px;
      rotate: -45deg;
      border-left: 2px solid white;
      border-bottom: 2px solid white;
    }

    .word {
      padding-right: 14px;
      font-size: 17px;
      font-weight: 720;
      letter-spacing: -.015em;
      overflow-wrap: anywhere;
      transition: color .18s;
    }

    .word-row:hover .word { color: #078a73; }

    .phonetic {
      padding-right: 14px;
      color: var(--muted);
      font-size: 14px;
      overflow-wrap: anywhere;
    }

    .translation {
      color: #49524f;
      font-size: 14px;
      line-height: 1.55;
      white-space: pre-line;
    }

    mark {
      border-radius: 3px;
      background: #fff1ad;
      color: inherit;
    }

    .empty-state {
      min-height: 260px;
      flex-direction: column;
      justify-content: center;
      padding: 40px;
      color: var(--muted);
      text-align: center;
    }

    .empty-icon {
      margin-bottom: 12px;
      color: var(--accent);
      font-size: 32px;
    }

    .empty-state strong { color: var(--ink); font-size: 18px; }
    .empty-state p { margin: 7px 0 0; }

    .footer {
      justify-content: space-between;
      gap: 12px;
      padding: 14px 4px 0;
      color: var(--muted);
      font-size: 12px;
    }

    .text-button { padding: 5px 8px; font-size: 12px; }
    .text-button.danger:hover { color: var(--danger); background: #fff0f1; }

    @keyframes app-in {
      from { opacity: 0; translate: 0 12px; }
      to { opacity: 1; translate: 0 0; }
    }

    @keyframes surface-in {
      from { opacity: 0; translate: 0 10px; scale: .995; }
      to { opacity: 1; translate: 0 0; scale: 1; }
    }

    @keyframes row-in {
      from { opacity: 0; translate: 0 7px; }
      to { opacity: 1; translate: 0 0; }
    }

    @keyframes gradient-flow {
      0%, 100% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
    }

    @keyframes progress-shine {
      0%, 55% { translate: -120% 0; }
      85%, 100% { translate: 120% 0; }
    }

    @keyframes check-pop {
      0% { transform: scale(.82); }
      65% { transform: scale(1.12); }
      100% { transform: scale(1); }
    }

    @keyframes breathe {
      0%, 100% { transform: translate3d(0, 0, 0) scale(1); opacity: .8; }
      50% { transform: translate3d(-12px, 13px, 0) scale(1.08); opacity: 1; }
    }

    .toast {
      position: fixed;
      left: 50%;
      bottom: 24px;
      z-index: 30;
      display: flex;
      align-items: center;
      gap: 18px;
      padding: 11px 14px;
      border-radius: 11px;
      background: #202725;
      color: white;
      box-shadow: 0 10px 28px rgba(0, 0, 0, .2);
      opacity: 0;
      translate: -50% 16px;
      pointer-events: none;
      transition: .2s ease;
    }

    .toast.show { opacity: 1; translate: -50% 0; pointer-events: auto; }
    .toast button { border: 0; background: none; color: #73e1cc; font-weight: 700; cursor: pointer; }

    @media (max-width: 720px) {
      .app { width: min(100% - 16px, 980px); margin-top: 8px; }
      .hero { padding: 18px; border-radius: 14px; }
      .hero-top { align-items: flex-start; }
      .toolbar { top: 6px; flex-wrap: wrap; }
      .search-wrap { flex-basis: 100%; }
      .filters { width: 100%; }
      .filter { flex: 1; padding-inline: 7px; }
      .list-head { display: none; }
      .word-row {
        grid-template-columns: 38px minmax(105px, .8fr) 1.5fr;
        grid-template-areas:
          "check word meaning"
          "check phonetic meaning";
        align-items: start;
        min-height: 70px;
        padding: 11px 12px;
      }
      .check-cell { grid-area: check; padding-top: 4px; }
      .word { grid-area: word; padding-right: 8px; }
      .phonetic { grid-area: phonetic; padding-right: 8px; }
      .translation { grid-area: meaning; }
      .footer { align-items: flex-start; flex-direction: column; }
    }

    /* Editorial Study Ledger — restrained, print-inspired visual system */
    :root {
      --bg: #f1f0ec;
      --paper: #faf9f6;
      --ink: #181a18;
      --muted: #747873;
      --line: #dcded8;
      --accent: #247a68;
      --accent-soft: #e8f0ed;
      --purple: #247a68;
      --shadow: none;
      --shadow-hover: none;
    }

    body {
      background: var(--bg);
    }

    body::before { content: none; }

    .app {
      width: min(1040px, calc(100% - 40px));
      margin: 42px auto 72px;
      animation: ledger-in .24s ease-out both;
    }

    .hero {
      overflow: visible;
      margin: 0;
      padding: 12px 0 26px;
      border: 0;
      border-bottom: 1px solid var(--ink);
      border-radius: 0;
      background: transparent;
      box-shadow: none;
      backdrop-filter: none;
      transition: none;
    }

    .hero:hover { box-shadow: none; translate: none; }
    .hero::before, .hero::after { content: none; }

    .eyebrow {
      margin-bottom: 9px;
      color: var(--accent);
      font-size: 10px;
      letter-spacing: .2em;
    }

    h1 {
      font-size: clamp(30px, 5vw, 46px);
      font-weight: 680;
      letter-spacing: -.065em;
    }

    .brand-accent {
      background: none;
      color: var(--ink);
      animation: none;
    }

    .subtitle {
      margin-top: 10px;
      color: var(--muted);
      font-size: 13px;
    }

    .summary {
      display: flex;
      align-items: baseline;
      gap: 7px;
      padding: 0;
      border: 0;
      border-radius: 0;
      background: transparent;
      box-shadow: none;
      font-size: 12px;
      letter-spacing: .04em;
    }

    .summary strong {
      color: var(--accent);
      font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
      font-size: 26px;
      font-weight: 520;
      letter-spacing: -.06em;
    }

    .progress-track {
      height: 2px;
      margin-top: 27px;
      border-radius: 0;
      background: #d9dcd6;
      box-shadow: none;
    }

    .progress-bar {
      border-radius: 0;
      background: var(--accent);
      transition: width .28s ease;
    }

    .progress-bar::after { content: none; }

    .toolbar {
      top: 0;
      gap: 24px;
      margin: 0;
      padding: 18px 0 14px;
      border: 0;
      border-bottom: 1px solid var(--line);
      border-radius: 0;
      background: rgba(241, 240, 236, .94);
      box-shadow: none;
      backdrop-filter: blur(10px);
      animation: none;
    }

    .search-wrap { flex-basis: 360px; }

    .search-icon {
      left: 0;
      width: 15px;
      color: #858984;
    }

    .search {
      height: 40px;
      padding: 0 8px 0 27px;
      border: 0;
      border-bottom: 1px solid #bfc3bd;
      border-radius: 0;
      background: transparent;
      transition: border-color .16s ease;
    }

    .search:hover { background: transparent; border-color: #929892; }

    .search:focus {
      border-color: var(--accent);
      box-shadow: none;
    }

    .filters { gap: 22px; }

    .filter {
      position: relative;
      padding: 0;
      border-radius: 0;
      font-size: 13px;
      transition: color .16s ease;
    }

    .filter::after {
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      bottom: 1px;
      height: 1px;
      background: var(--accent);
      scale: 0 1;
      transform-origin: right;
      transition: scale .16s ease;
    }

    .filter:hover, .text-button:hover { background: transparent; }
    .filter:active { transform: none; }

    .filter.active {
      background: transparent;
      color: var(--ink);
      font-weight: 620;
      box-shadow: none;
    }

    .filter.active::after {
      scale: 1 1;
      transform-origin: left;
    }

    .list-card {
      overflow: visible;
      border: 0;
      border-radius: 0;
      background: transparent;
      box-shadow: none;
      animation: none;
    }

    .list-head, .word-row {
      grid-template-columns: 66px 48px minmax(170px, .78fr) minmax(125px, .7fr) minmax(280px, 1.8fr);
    }

    .list-head {
      min-height: 48px;
      padding: 0 4px;
      border-bottom: 1px solid #b9bdb7;
      background: transparent;
      color: #7e837d;
      font-size: 10px;
      font-weight: 650;
      letter-spacing: .14em;
    }

    .word-row {
      min-height: 66px;
      padding: 10px 4px;
      animation: none;
      transition: opacity .18s ease, background .14s ease, padding .18s ease;
    }

    .word-row:hover {
      background: rgba(36, 122, 104, .035);
      box-shadow: none;
      translate: none;
    }

    .word-row.completing {
      opacity: 0;
      translate: none;
    }

    .word-row.mastered { opacity: .5; }

    .row-number {
      color: #9a9e98;
      font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
      font-size: 11px;
      letter-spacing: .04em;
      font-variant-numeric: tabular-nums;
    }

    .check {
      width: 20px;
      height: 20px;
      border: 1px solid #aeb4ad;
      border-radius: 2px;
      background: transparent;
      transition: border-color .14s ease, background .14s ease;
    }

    .check:hover {
      border-color: var(--accent);
      transform: none;
      box-shadow: none;
    }

    .check:checked {
      border-color: var(--accent);
      border-radius: 2px;
      background: var(--accent);
      box-shadow: none;
      animation: none;
    }

    .check:checked::after {
      width: 8px;
      height: 4px;
    }

    .word {
      font-size: 16px;
      font-weight: 650;
      letter-spacing: -.01em;
    }

    .word-row:hover .word { color: var(--ink); }

    .phonetic {
      color: #777d77;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 14px;
    }

    .translation {
      color: #404540;
      font-size: 14px;
      line-height: 1.6;
    }

    mark {
      border-radius: 0;
      background: #dfece7;
    }

    .empty-state { min-height: 300px; }
    .empty-icon { color: var(--accent); font-size: 24px; }

    .footer {
      padding: 18px 0 0;
      border-top: 1px solid var(--line);
      color: #858984;
    }

    .text-button { border-radius: 0; }

    .toast {
      bottom: 26px;
      padding: 10px 13px;
      border: 1px solid #313632;
      border-radius: 2px;
      background: #1d211e;
      box-shadow: 0 8px 24px rgba(0, 0, 0, .12);
      transition: opacity .16s ease, translate .16s ease;
    }

    .toast button { color: #86cfbf; }

    @keyframes ledger-in {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @media (max-width: 720px) {
      .app { width: calc(100% - 24px); margin: 20px auto 48px; }
      .hero { padding: 8px 0 22px; }
      .hero-top { align-items: flex-start; flex-direction: column; gap: 12px; }
      .summary { gap: 4px; font-size: 10px; white-space: nowrap; }
      .summary strong { font-size: 21px; }
      .toolbar { top: 0; gap: 8px; padding: 13px 0 10px; }
      .filters { gap: 0; justify-content: space-between; }
      .filter { flex: 0 0 auto; }
      .word-row {
        grid-template-columns: 34px minmax(94px, .72fr) minmax(0, 1.45fr);
        grid-template-areas:
          "check word meaning"
          "number phonetic meaning";
        min-height: 72px;
        padding: 12px 0;
      }
      .row-number { grid-area: number; padding-top: 3px; font-size: 9px; }
      .check-cell { grid-area: check; padding-top: 2px; }
      .word { grid-area: word; min-width: 0; }
      .phonetic { grid-area: phonetic; min-width: 0; }
      .translation { grid-area: meaning; min-width: 0; overflow-wrap: anywhere; }
      .footer { padding-top: 14px; }
    }

    /* Dictionary edition */
    :root {
      --bg: #e9e5dc;
      --paper: #f8f5ed;
      --ink: #201d19;
      --muted: #777168;
      --line: #d7d0c4;
      --accent: #88362f;
      --accent-soft: #f0e4df;
    }

    body { background: var(--bg); }

    .app {
      width: min(1120px, calc(100% - 44px));
      min-height: calc(100vh - 48px);
      margin: 24px auto;
      padding: 42px 52px 34px;
      border: 1px solid rgba(77, 65, 51, .14);
      background: var(--paper);
      box-shadow: 0 18px 50px rgba(65, 53, 40, .09);
    }

    .hero { padding: 0 0 28px; border-bottom-color: #37312a; }

    .eyebrow {
      margin-bottom: 11px;
      color: var(--accent);
      font-family: Georgia, "Times New Roman", serif;
      font-size: 11px;
      letter-spacing: .18em;
    }

    h1 {
      font-family: "Songti SC", STSong, "Noto Serif CJK SC", Georgia, serif;
      font-size: clamp(34px, 5vw, 52px);
      font-weight: 600;
      letter-spacing: -.055em;
    }

    .subtitle { color: #726c63; }
    .summary strong { color: var(--accent); }
    .progress-bar { background: var(--accent); }

    .toolbar {
      background: rgba(248, 245, 237, .95);
      border-bottom-color: var(--line);
    }

    .search:focus { border-color: var(--accent); }
    .filter::after { background: var(--accent); }

    .list-head, .word-row {
      grid-template-columns: 62px 46px minmax(165px, .72fr) minmax(125px, .62fr) minmax(280px, 1.65fr) 28px;
    }

    .list-head {
      color: #81796e;
      border-bottom-color: #aaa296;
    }

    .word-row {
      cursor: pointer;
      outline: none;
    }

    .word-row:hover,
    .word-row:focus-visible {
      background: rgba(136, 54, 47, .035);
    }

    .word-row:focus-visible { box-shadow: inset 2px 0 var(--accent); }

    .word {
      font-family: Georgia, "Times New Roman", serif;
      font-size: 18px;
      font-weight: 600;
    }

    .translation {
      font-family: "Songti SC", STSong, "Noto Serif CJK SC", serif;
      color: #49433c;
    }

    .check:hover { border-color: var(--accent); }
    .check:checked { border-color: var(--accent); background: var(--accent); }

    .row-open {
      color: #aaa297;
      font-family: Georgia, serif;
      font-size: 18px;
      text-align: right;
      transition: color .14s ease, translate .14s ease;
    }

    .word-row:hover .row-open {
      color: var(--accent);
      translate: 3px 0;
    }

    mark { background: #ead8ce; }
    .toast button { color: #e1b0a8; }

    [hidden] { display: none !important; }

    .entry-view { animation: entry-in .2s ease-out both; }

    .entry-masthead {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 18px;
      border-bottom: 1px solid #38322b;
    }

    .entry-back,
    .entry-navigation button {
      border: 0;
      background: transparent;
      color: var(--ink);
      cursor: pointer;
    }

    .entry-back {
      padding: 4px 0;
      color: var(--accent);
      font-size: 13px;
    }

    .entry-back:hover { text-decoration: underline; text-underline-offset: 4px; }

    .entry-publication {
      color: #777067;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 10px;
      letter-spacing: .18em;
    }

    .entry-layout {
      display: grid;
      grid-template-columns: minmax(230px, .72fr) minmax(0, 1.55fr);
      gap: clamp(48px, 8vw, 100px);
      padding: 66px 0 76px;
    }

    .entry-identity {
      position: sticky;
      top: 36px;
      align-self: start;
    }

    .entry-number,
    .definition-label {
      color: var(--accent);
      font-size: 10px;
      font-weight: 700;
      letter-spacing: .16em;
      text-transform: uppercase;
    }

    .entry-identity h2 {
      margin: 16px 0 10px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(46px, 7vw, 76px);
      font-weight: 500;
      letter-spacing: -.055em;
      line-height: .98;
      overflow-wrap: anywhere;
    }

    .entry-phonetic {
      color: #69635b;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 19px;
    }

    .entry-part {
      margin-top: 14px;
      color: var(--accent);
      font-family: Georgia, "Times New Roman", serif;
      font-size: 13px;
      font-style: italic;
    }

    .entry-mastered-control {
      display: flex;
      align-items: center;
      gap: 10px;
      width: fit-content;
      margin-top: 38px;
      color: #5f5952;
      font-size: 13px;
      cursor: pointer;
    }

    .definition-section {
      padding: 0 0 34px;
      margin-bottom: 34px;
      border-bottom: 1px solid var(--line);
    }

    .definition-section:last-child { margin-bottom: 0; }

    .definition-label { margin-bottom: 17px; }

    .definition-zh,
    .definition-en,
    .entry-example {
      white-space: pre-line;
    }

    .definition-zh {
      font-family: "Songti SC", STSong, "Noto Serif CJK SC", serif;
      font-size: clamp(20px, 2.4vw, 25px);
      line-height: 1.72;
    }

    .definition-en {
      font-family: Georgia, "Times New Roman", serif;
      font-size: 18px;
      line-height: 1.72;
    }

    .entry-example {
      margin: 0;
      padding-left: 22px;
      border-left: 2px solid var(--accent);
      color: #5b554e;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 18px;
      font-style: italic;
      line-height: 1.7;
    }

    .entry-navigation {
      display: grid;
      grid-template-columns: 1fr 1fr;
      border-top: 1px solid #aaa296;
      border-bottom: 1px solid #aaa296;
    }

    .entry-navigation button {
      min-height: 94px;
      padding: 18px 0;
      text-align: left;
    }

    .entry-navigation button + button {
      padding-left: 28px;
      border-left: 1px solid var(--line);
      text-align: right;
    }

    .entry-navigation button:disabled {
      opacity: .3;
      cursor: default;
    }

    .entry-navigation span {
      display: block;
      margin-bottom: 8px;
      color: #888076;
      font-size: 9px;
      font-weight: 700;
      letter-spacing: .15em;
      text-transform: uppercase;
    }

    .entry-navigation strong {
      font-family: Georgia, "Times New Roman", serif;
      font-size: 18px;
      font-weight: 500;
    }

    @keyframes entry-in {
      from { opacity: 0; translate: 0 5px; }
      to { opacity: 1; translate: 0 0; }
    }

    @media (max-width: 720px) {
      .app {
        width: 100%;
        min-height: 100vh;
        margin: 0;
        padding: 25px 16px 34px;
        border: 0;
        box-shadow: none;
      }

      .list-head { display: none; }

      .word-row {
        grid-template-columns: 34px minmax(94px, .72fr) minmax(0, 1.45fr) 18px;
        grid-template-areas:
          "check word meaning open"
          "number phonetic meaning open";
      }

      .row-open { grid-area: open; align-self: center; }

      .entry-masthead { align-items: flex-start; }
      .entry-publication { max-width: 140px; text-align: right; line-height: 1.5; }

      .entry-layout {
        grid-template-columns: 1fr;
        gap: 42px;
        padding: 44px 0 54px;
      }

      .entry-identity { position: static; }
      .entry-identity h2 { font-size: clamp(46px, 15vw, 64px); }
      .entry-mastered-control { margin-top: 27px; }
      .definition-section { padding-bottom: 27px; margin-bottom: 27px; }
      .definition-zh { font-size: 20px; }
      .definition-en, .entry-example { font-size: 16px; }
      .entry-navigation button { min-height: 82px; }
      .entry-navigation button + button { padding-left: 16px; }
    }

    /* Paper strip edition */
    body {
      background: #d8d3c9;
      background-image: radial-gradient(rgba(64, 56, 46, .055) .6px, transparent .6px);
      background-size: 5px 5px;
    }

    .app {
      position: relative;
      width: min(900px, calc(100% - 40px));
      min-height: calc(100vh - 64px);
      margin: 32px auto;
      padding: 28px 34px 24px;
      border: 0;
      background: #faf8f1;
      box-shadow: 0 16px 40px rgba(55, 47, 38, .13);
    }

    .app::before,
    .app::after {
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      z-index: 2;
      height: 9px;
      pointer-events: none;
      background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='9' viewBox='0 0 24 9'%3E%3Cpath d='M0 9 L6 2 L12 9 L18 2 L24 9' fill='%23faf8f1'/%3E%3C/svg%3E") repeat-x;
      background-size: 24px 9px;
    }

    .app::before { top: -8px; }
    .app::after { bottom: -8px; rotate: 180deg; }

    .toolbar {
      position: static;
      display: grid;
      grid-template-columns: minmax(220px, 1fr) auto auto;
      gap: 24px;
      margin: 0;
      padding: 0 0 17px;
      border: 0;
      background: transparent;
      backdrop-filter: none;
    }

    .search-wrap { min-width: 0; }

    .search {
      height: 36px;
      border-bottom-color: #b9b2a7;
      font-family: "Songti SC", STSong, serif;
      font-size: 14px;
    }

    .summary {
      align-self: center;
      gap: 5px;
      color: #888176;
      font-family: ui-monospace, Consolas, monospace;
      font-size: 11px;
    }

    .summary strong {
      color: #595249;
      font-size: 13px;
      font-weight: 500;
    }

    .filters {
      align-self: center;
      gap: 18px;
    }

    .filter {
      min-height: 32px;
      font-family: "Songti SC", STSong, serif;
      font-size: 12px;
    }

    .progress-track {
      height: 1px;
      margin: 0 0 11px;
      background: #d2ccc1;
    }

    .progress-bar { background: #756d63; }

    .list-head { display: none; }

    .list-card {
      overflow: visible;
      margin: 0 -10px;
    }

    .word-row {
      position: relative;
      grid-template-columns: 54px 46px minmax(150px, .72fr) minmax(120px, .6fr) minmax(240px, 1.5fr) 22px;
      min-height: 74px;
      padding: 16px 10px 18px;
      border: 0;
      background: #faf8f1;
      cursor: pointer;
      transition: background .14s ease;
    }

    .word-row::after {
      content: "";
      position: absolute;
      left: 8px;
      right: 8px;
      bottom: -3px;
      height: 7px;
      z-index: 1;
      pointer-events: none;
      background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='7' viewBox='0 0 24 7'%3E%3Cpath d='M0 4 L6 1 L12 6 L18 1 L24 4' fill='none' stroke='%23c9c1b4' stroke-width='0.8'/%3E%3C/svg%3E") repeat-x;
      background-size: 24px 7px;
      opacity: .82;
    }

    .word-row:hover,
    .word-row:focus-visible {
      background: #fffdf7;
      box-shadow: none;
    }

    .word-row.completing {
      z-index: 3;
      opacity: 1;
      animation: tear-right-to-left .56s cubic-bezier(.55, .06, .68, .19) forwards;
      pointer-events: none;
    }

    .word-row.completing::after { opacity: 1; }

    .row-number {
      color: #aaa397;
      font-size: 9px;
    }

    .check {
      width: 19px;
      height: 19px;
      border-color: #aaa398;
      background: #faf8f1;
    }

    .check:checked {
      border-color: #5d574f;
      background: #5d574f;
    }

    .word {
      color: #27231f;
      font-size: 18px;
    }

    .phonetic { color: #837c72; }

    .translation {
      color: #4d4740;
      font-size: 13px;
      line-height: 1.55;
    }

    .row-open { color: #b2aa9e; }
    .word-row:hover .row-open { color: #6b6359; }

    .footer {
      justify-content: flex-end;
      padding: 18px 0 0;
      border: 0;
    }

    .footer .text-button {
      color: #9a9287;
      font-family: "Songti SC", STSong, serif;
    }

    .entry-view { min-height: calc(100vh - 120px); }
    .entry-publication { color: #91897e; }

    @keyframes tear-right-to-left {
      0% {
        clip-path: inset(-8px 0 -8px 0);
        translate: 0 0;
        rotate: 0deg;
        opacity: 1;
      }
      18% {
        translate: -3px 0;
        rotate: -.18deg;
      }
      62% {
        opacity: .82;
      }
      100% {
        clip-path: inset(-8px 100% -8px 0);
        translate: -18px 1px;
        rotate: -.7deg;
        opacity: .18;
      }
    }

    @media (max-width: 720px) {
      body { background: #d8d3c9; }

      .app {
        width: calc(100% - 18px);
        min-height: calc(100vh - 28px);
        margin: 14px auto;
        padding: 22px 15px 25px;
      }

      .toolbar {
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 9px 15px;
      }

      .search-wrap { grid-column: 1; }
      .summary { grid-column: 2; }
      .filters {
        grid-column: 1 / -1;
        width: 100%;
        justify-content: space-between;
      }

      .list-card { margin: 0 -5px; }

      .word-row {
        grid-template-columns: 32px minmax(92px, .72fr) minmax(0, 1.45fr) 16px;
        grid-template-areas:
          "check word meaning open"
          "number phonetic meaning open";
        min-height: 78px;
        padding: 15px 5px 18px;
      }

      .word-row::after { left: 3px; right: 3px; }
      .word { font-size: 17px; }
      .translation { font-size: 13px; }
    }

    /* Mobile-first paper entry */
    .entry-view {
      width: min(760px, 100%);
      min-height: calc(100vh - 120px);
      margin: 0 auto;
    }

    .entry-masthead {
      min-height: 54px;
      padding: 0 4px 10px;
      border-bottom: 1px solid #cfc8bc;
    }

    .entry-back {
      min-width: 72px;
      min-height: 44px;
      color: #615a51;
      font-family: "Songti SC", STSong, serif;
      font-size: 13px;
      text-align: left;
    }

    .entry-number {
      color: #9c9488;
      font-family: ui-monospace, Consolas, monospace;
      font-size: 9px;
      font-weight: 500;
      letter-spacing: .12em;
    }

    .entry-layout {
      display: block;
      padding: 0;
    }

    .entry-identity,
    .definition-section {
      position: relative;
      padding: 38px 8px 43px;
      margin: 0;
      border: 0;
    }

    .entry-identity {
      position: relative;
      top: auto;
      text-align: left;
    }

    .entry-identity::after,
    .definition-section::after {
      content: "";
      position: absolute;
      left: 4px;
      right: 4px;
      bottom: -3px;
      height: 7px;
      background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='7' viewBox='0 0 24 7'%3E%3Cpath d='M0 4 L6 1 L12 6 L18 1 L24 4' fill='none' stroke='%23c9c1b4' stroke-width='0.8'/%3E%3C/svg%3E") repeat-x;
      background-size: 24px 7px;
    }

    .entry-identity h2 {
      margin: 0 0 12px;
      color: #26221e;
      font-size: clamp(52px, 9vw, 78px);
      font-weight: 500;
      line-height: 1;
    }

    .entry-phonetic,
    .entry-part {
      display: inline-block;
      margin: 0 12px 0 0;
      vertical-align: baseline;
    }

    .entry-phonetic {
      color: #746d64;
      font-size: 18px;
    }

    .entry-part {
      color: #8b443d;
      font-size: 13px;
    }

    .entry-mastered-control {
      min-height: 44px;
      margin-top: 28px;
      color: #655e55;
      touch-action: manipulation;
    }

    .entry-mastered-control .check {
      width: 22px;
      height: 22px;
    }

    .definition-label {
      margin-bottom: 14px;
      color: #938b80;
      font-family: ui-monospace, Consolas, monospace;
      font-size: 9px;
      font-weight: 500;
      letter-spacing: .14em;
    }

    .definition-zh {
      color: #2f2a25;
      font-size: clamp(20px, 3vw, 25px);
      line-height: 1.75;
    }

    .definition-en {
      color: #3f3933;
      font-size: 17px;
      line-height: 1.75;
    }

    .entry-example {
      padding-left: 18px;
      border-left: 1px solid #827a70;
      color: #625b53;
      font-size: 17px;
      line-height: 1.75;
    }

    .entry-navigation {
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      margin-top: 7px;
      border: 0;
    }

    .entry-navigation button {
      min-width: 0;
      min-height: 82px;
      padding: 17px 8px;
      touch-action: manipulation;
    }

    .entry-navigation button + button {
      padding-left: 18px;
      border-left-color: #d3ccc0;
    }

    .entry-navigation strong {
      display: block;
      overflow: hidden;
      font-size: 17px;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    @media (max-width: 720px) {
      .app {
        width: calc(100% - 14px);
        min-height: calc(100dvh - 20px);
        margin: 10px auto;
        padding: 20px 12px calc(25px + env(safe-area-inset-bottom));
      }

      .toolbar {
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 8px 12px;
      }

      .search { min-height: 44px; font-size: 16px; }
      .summary { padding-inline: 3px; }
      .filter { min-height: 44px; min-width: 64px; }

      .word-row {
        grid-template-columns: 42px minmax(88px, .7fr) minmax(0, 1.45fr) 15px;
        min-height: 82px;
        padding: 15px 2px 19px;
      }

      .check-cell {
        display: flex;
        align-items: flex-start;
        justify-content: flex-start;
        min-width: 42px;
        min-height: 44px;
        padding-top: 1px;
      }

      .check-cell .check { width: 21px; height: 21px; }
      .row-number { padding-top: 1px; }
      .phonetic { padding-right: 6px; font-size: 12px; }
      .translation { line-height: 1.6; }
      .row-open { font-size: 16px; }
      .footer .text-button { min-width: 54px; min-height: 44px; }

      .entry-masthead { min-height: 50px; padding-bottom: 6px; }
      .entry-identity, .definition-section { padding: 32px 5px 38px; }
      .entry-identity h2 { font-size: clamp(45px, 15vw, 62px); }
      .entry-phonetic { font-size: 16px; }
      .entry-mastered-control { margin-top: 22px; }
      .definition-zh { font-size: 20px; }
      .definition-en, .entry-example { font-size: 16px; }
      .entry-navigation button { min-height: 78px; padding-inline: 5px; }
      .entry-navigation button + button { padding-left: 12px; }
      .entry-navigation strong { font-size: 15px; }
    }

    @media (max-width: 390px) {
      .app { width: calc(100% - 8px); padding-inline: 9px; }
      .filters { gap: 4px; }
      .filter { min-width: 58px; }
      .word-row {
        grid-template-columns: 38px minmax(82px, .68fr) minmax(0, 1.4fr) 13px;
      }
      .word { font-size: 16px; }
      .translation { font-size: 12.5px; }
    }

    @media (hover: none) {
      .word-row:hover { background: #faf8f1; }
      .word-row:hover .row-open { color: #b2aa9e; translate: 0; }
    }

    /* Direct manipulation: single-click details, double-click tear */
    .toolbar {
      grid-template-columns: minmax(200px, 1fr) auto auto auto;
      gap: 20px;
    }

    .search {
      border-bottom: 0;
      box-shadow: none;
    }

    .search:hover,
    .search:focus {
      border-bottom: 0;
      box-shadow: none;
    }

    .shuffle-button {
      min-width: 52px;
      min-height: 36px;
      padding: 0 5px;
      border: 0;
      border-radius: 0;
      background: transparent;
      color: #756e64;
      font-family: "Songti SC", STSong, serif;
      font-size: 12px;
      cursor: pointer;
      transition: color .14s ease;
      touch-action: manipulation;
    }

    .shuffle-button:hover,
    .shuffle-button[aria-pressed="true"] {
      color: #2f2a25;
      text-decoration: underline;
      text-decoration-color: #8a8175;
      text-underline-offset: 5px;
    }

    .word-row {
      grid-template-columns: minmax(170px, .72fr) minmax(130px, .62fr) minmax(280px, 1.6fr) 22px;
      user-select: none;
      touch-action: manipulation;
    }

    .word-row.completing::before {
      content: "";
      position: absolute;
      top: 1px;
      right: 0;
      bottom: 1px;
      z-index: 5;
      width: 10px;
      background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='24' viewBox='0 0 10 24'%3E%3Cpath d='M9 0 L2 4 L9 8 L2 12 L9 16 L2 20 L9 24' fill='%23faf8f1' stroke='%23bdb4a7' stroke-width='0.7'/%3E%3C/svg%3E") repeat-y;
      background-size: 10px 24px;
      filter: drop-shadow(2px 0 1px rgba(70, 60, 48, .13));
      animation: moving-tear-edge .56s cubic-bezier(.55, .06, .68, .19) forwards;
    }

    @keyframes moving-tear-edge {
      from { right: 0; }
      to { right: calc(100% - 10px); }
    }

    @media (max-width: 720px) {
      .toolbar {
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 7px 10px;
      }

      .search-wrap { grid-column: 1; grid-row: 1; }
      .summary { grid-column: 2; grid-row: 1; }
      .filters {
        grid-column: 1;
        grid-row: 2;
        width: auto;
        justify-content: flex-start;
        gap: 13px;
      }
      .shuffle-button {
        grid-column: 2;
        grid-row: 2;
        min-width: 52px;
        min-height: 44px;
      }

      .word-row {
        grid-template-columns: minmax(90px, .7fr) minmax(0, 1.5fr) 15px;
        grid-template-areas:
          "word meaning open"
          "phonetic meaning open";
        min-height: 80px;
        padding-left: 7px;
      }

      .word { grid-area: word; }
      .phonetic { grid-area: phonetic; }
      .translation { grid-area: meaning; }
      .row-open { grid-area: open; }
    }

    @media (max-width: 390px) {
      .filters { gap: 8px; }
      .filter { min-width: 52px; }
      .word-row {
        grid-template-columns: minmax(82px, .67fr) minmax(0, 1.45fr) 13px;
      }
    }

    /* Compact printed-dictionary entry */
    .entry-view { width: min(820px, 100%); }

    .entry-masthead {
      padding-bottom: 8px;
      border-bottom: 1px solid #bdb5a9;
    }

    .entry-layout { padding: 0; }

    .entry-identity {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      grid-template-areas:
        "headword mastered"
        "meta mastered";
      align-items: center;
      gap: 5px 24px;
      padding: 38px 6px 30px;
      text-align: left;
    }

    .entry-identity::after,
    .definition-section::after { content: none; }

    .entry-identity h2 {
      grid-area: headword;
      margin: 0;
      font-size: clamp(46px, 7vw, 64px);
      line-height: 1;
    }

    .entry-meta {
      grid-area: meta;
      display: flex;
      align-items: baseline;
      gap: 12px;
      margin-top: 7px;
    }

    .entry-phonetic,
    .entry-part {
      display: block;
      margin: 0;
    }

    .entry-phonetic { font-size: 17px; }

    .entry-part {
      padding-left: 12px;
      border-left: 1px solid #c5bdb1;
      color: #793b35;
      font-size: 13px;
    }

    .entry-mastered-control {
      grid-area: mastered;
      align-self: center;
      min-height: 46px;
      margin: 0;
      padding: 0 4px;
    }

    .entry-content {
      border-top: 2px solid #4a433a;
    }

    .definition-section {
      display: grid;
      grid-template-columns: 105px minmax(0, 1fr);
      gap: 24px;
      padding: 25px 6px 27px;
      border-bottom: 1px solid #d0c8bc;
    }

    .definition-label {
      display: flex;
      flex-direction: column;
      gap: 7px;
      margin: 0;
      color: #8c8479;
      font-family: ui-sans-serif, system-ui, sans-serif;
      font-size: 9px;
      letter-spacing: .1em;
    }

    .definition-label span {
      color: #39332d;
      font-family: "Songti SC", STSong, Georgia, serif;
      font-size: 17px;
      font-weight: 600;
      letter-spacing: 0;
      line-height: 1;
    }

    .definition-zh,
    .definition-en {
      display: grid;
      gap: 11px;
      font-size: 18px;
      line-height: 1.6;
    }

    .definition-en {
      color: #423c36;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 17px;
    }

    .sense-row {
      display: grid;
      grid-template-columns: 25px minmax(0, 1fr);
      gap: 8px;
      align-items: start;
    }

    .sense-number {
      padding-top: .2em;
      color: #928a7f;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 11px;
      font-style: italic;
    }

    .sense-text { min-width: 0; white-space: pre-line; }

    .entry-example {
      margin: 0;
      padding: 0;
      border: 0;
      color: #575048;
      font-size: 17px;
    }

    .entry-example::before { content: "“"; }
    .entry-example::after { content: "”"; }

    .entry-navigation {
      margin-top: 22px;
      border-top: 1px solid #a9a094;
      border-bottom: 1px solid #a9a094;
    }

    @media (max-width: 720px) {
      .entry-identity {
        display: block;
        padding: 30px 4px 27px;
      }

      .entry-identity h2 { font-size: clamp(43px, 14vw, 58px); }
      .entry-meta { margin-top: 12px; }

      .entry-mastered-control {
        width: fit-content;
        margin-top: 21px;
        padding: 0;
      }

      .definition-section {
        display: block;
        padding: 23px 4px 25px;
      }

      .definition-label {
        flex-direction: row;
        align-items: baseline;
        gap: 8px;
        margin-bottom: 17px;
      }

      .definition-label span { font-size: 15px; }
      .definition-zh, .definition-en { gap: 10px; font-size: 16px; }
      .sense-row { grid-template-columns: 21px minmax(0, 1fr); gap: 6px; }
      .entry-example { font-size: 16px; line-height: 1.75; }
      .entry-navigation { margin-top: 17px; }
    }

    /* Full-width perforations and pull-away tear */
    .list-card { margin: 0 -34px; }

    .word-row {
      grid-template-columns: minmax(180px, .72fr) minmax(135px, .62fr) minmax(280px, 1.6fr);
      padding-left: 34px;
      padding-right: 34px;
    }

    .word-row::after {
      left: 0;
      right: 0;
    }

    .word-row.completing::before { content: none; }

    .tear-source {
      min-height: 0 !important;
      overflow: hidden;
      opacity: 0;
      pointer-events: none;
      animation: close-paper-gap .72s .08s ease-in-out forwards;
    }

    .tear-flying {
      z-index: 9999;
      min-height: 0;
      overflow: visible;
      background: #faf8f1;
      box-shadow: none;
      pointer-events: none;
      transform-origin: 8% 50%;
      will-change: transform, opacity;
    }

    .tear-flying::before {
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      top: -4px;
      height: 7px;
      background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='7' viewBox='0 0 24 7'%3E%3Cpath d='M0 4 L6 1 L12 6 L18 1 L24 4' fill='none' stroke='%23c9c1b4' stroke-width='0.8'/%3E%3C/svg%3E") repeat-x;
      background-size: 24px 7px;
    }

    .tear-flying-active {
      animation: pull-away-strip .72s cubic-bezier(.2, .72, .25, 1) forwards;
    }

    @keyframes pull-away-strip {
      0% {
        transform: translate3d(0, 0, 0) rotate(0deg);
        box-shadow: 0 0 0 rgba(48, 40, 31, 0);
        opacity: 1;
      }
      18% {
        transform: translate3d(10px, -3px, 0) rotate(.35deg);
        box-shadow: -5px 7px 12px rgba(48, 40, 31, .08);
      }
      48% {
        transform: translate3d(46px, -12px, 0) rotate(1.4deg);
        box-shadow: -12px 16px 22px rgba(48, 40, 31, .12);
        opacity: .98;
      }
      100% {
        transform: translate3d(210px, -64px, 0) rotate(6deg);
        box-shadow: -18px 22px 30px rgba(48, 40, 31, .08);
        opacity: 0;
      }
    }

    @keyframes close-paper-gap {
      0%, 16% {
        height: var(--tear-height, auto);
        padding-top: 16px;
        padding-bottom: 18px;
      }
      100% {
        height: 0;
        padding-top: 0;
        padding-bottom: 0;
      }
    }

    .relation-content {
      display: grid;
      gap: 17px;
    }

    .relation-group {
      display: grid;
      grid-template-columns: 64px minmax(0, 1fr);
      gap: 12px;
      align-items: baseline;
    }

    .relation-title {
      color: #8d857a;
      font-size: 11px;
    }

    .relation-words {
      display: flex;
      flex-wrap: wrap;
      gap: 7px 16px;
    }

    .form-item {
      display: inline-flex;
      align-items: baseline;
      gap: 5px;
      color: #4d463f;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 15px;
    }

    .form-item small {
      color: #999186;
      font-family: "Songti SC", STSong, sans-serif;
      font-size: 9px;
    }

    .relation-word {
      padding: 0;
      border: 0;
      border-bottom: 1px solid transparent;
      background: transparent;
      color: #4d463f;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 15px;
      line-height: 1.55;
    }

    button.relation-word { cursor: pointer; }

    button.relation-word:hover,
    .relation-word.linked {
      color: #783b35;
      border-bottom-color: #bca39e;
    }

    .entry-examples {
      display: grid;
      gap: 16px;
    }

    .example-row {
      display: grid;
      grid-template-columns: 22px minmax(0, 1fr);
      gap: 8px;
      color: #575048;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 16px;
      font-style: italic;
      line-height: 1.7;
    }

    .example-row > span {
      color: #958d82;
      font-size: 10px;
    }

    .example-row q { quotes: "“" "”"; }

    @media (max-width: 720px) {
      .list-card { margin: 0 -12px; }
      .word-row {
        grid-template-columns: minmax(95px, .72fr) minmax(0, 1.5fr);
        grid-template-areas:
          "word meaning"
          "phonetic meaning";
        padding-left: 18px;
        padding-right: 18px;
      }

      .relation-group {
        grid-template-columns: 55px minmax(0, 1fr);
        gap: 9px;
      }

      .relation-words { gap: 6px 13px; }
      .relation-word { font-size: 14px; }
    }

    @media (max-width: 390px) {
      .list-card { margin-left: -9px; margin-right: -9px; }
      .word-row {
        grid-template-columns: minmax(86px, .68fr) minmax(0, 1.42fr);
        padding-left: 14px;
        padding-right: 14px;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        scroll-behavior: auto !important;
        animation: none !important;
        transition: none !important;
      }
    }
  </style>
</head>
<body>
  <main class="app">
    <div id="list-view">
    <section class="toolbar" aria-label="词汇筛选">
      <label class="search-wrap">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.5-3.5"></path></svg>
        <input class="search" id="search" type="search" placeholder="查词" autocomplete="off">
      </label>
      <div class="summary" aria-live="polite">
        <strong id="mastered-count">0</strong><span>/</span><span id="total-count">__WORD_COUNT__</span>
      </div>
      <div class="filters" role="group" aria-label="显示范围">
        <button class="filter active" type="button" data-view="learning">未掌握</button>
        <button class="filter" type="button" data-view="mastered">已掌握</button>
        <button class="filter" type="button" data-view="all">全部</button>
      </div>
      <button class="shuffle-button" id="shuffle-button" type="button" aria-pressed="false">随机</button>
    </section>
    <div class="progress-track" aria-hidden="true"><div class="progress-bar" id="progress-bar"></div></div>

    <section class="list-card" aria-label="考研词汇表">
      <div class="list-head" aria-hidden="true">
        <span>词条</span><span>音标</span><span>释义摘要</span>
      </div>
      <div id="word-list"></div>
    </section>

    <footer class="footer">
      <button class="text-button danger" id="reset-button" type="button">重置</button>
    </footer>
    </div>

    <article class="entry-view" id="entry-view" hidden aria-labelledby="entry-word">
      <header class="entry-masthead">
        <button class="entry-back" id="entry-back" type="button" aria-label="返回">← 返回</button>
        <span class="entry-number" id="entry-number">ENTRY 0001</span>
      </header>

      <div class="entry-layout">
        <aside class="entry-identity">
          <h2 id="entry-word">abandon</h2>
          <div class="entry-meta">
            <div class="entry-phonetic" id="entry-phonetic">/əˈbændən/</div>
            <div class="entry-part" id="entry-part">verb</div>
          </div>
          <label class="entry-mastered-control">
            <input class="check" id="entry-mastered" type="checkbox">
            <span>已掌握</span>
          </label>
        </aside>

        <div class="entry-content">
          <section class="definition-section">
            <div class="definition-label"><span>中</span>中文释义</div>
            <div class="definition-zh" id="entry-translation"></div>
          </section>
          <section class="definition-section">
            <div class="definition-label"><span>EN</span>Definition</div>
            <div class="definition-en" id="entry-definition"></div>
          </section>
          <section class="definition-section" id="entry-relations-section">
            <div class="definition-label"><span>词</span>Related</div>
            <div class="relation-content">
              <div class="relation-group" id="form-group"><div class="relation-title">词形</div><div class="relation-words" id="entry-forms"></div></div>
              <div class="relation-group" id="phrase-group"><div class="relation-title">短语</div><div class="relation-words" id="entry-phrases"></div></div>
              <div class="relation-group" id="synonym-group"><div class="relation-title">近义词</div><div class="relation-words" id="entry-synonyms"></div></div>
              <div class="relation-group" id="antonym-group"><div class="relation-title">反义词</div><div class="relation-words" id="entry-antonyms"></div></div>
              <div class="relation-group" id="related-group"><div class="relation-title">派生词</div><div class="relation-words" id="entry-related"></div></div>
            </div>
          </section>
          <section class="definition-section" id="entry-example-section">
            <div class="definition-label"><span>例</span>Examples</div>
            <div class="entry-examples" id="entry-example"></div>
          </section>
        </div>
      </div>

      <nav class="entry-navigation" aria-label="相邻词条">
        <button id="previous-entry" type="button"><span>上一个</span><strong></strong></button>
        <button id="next-entry" type="button"><span>下一个</span><strong></strong></button>
      </nav>
    </article>
  </main>

  <div class="toast" id="toast" role="status">
    <span id="toast-text">已标记为掌握</span>
    <button id="undo-button" type="button">撤销</button>
  </div>

  <script id="word-data" type="application/json">__WORD_DATA__</script>
  <script>
    (() => {
      "use strict";

      const WORDS = JSON.parse(document.getElementById("word-data").textContent);
      const STORAGE_KEY = "graduate-vocab-checklist:v1";
      const BATCH_SIZE = 180;
      const DOUBLE_TAP_DELAY = 300;
      const TEAR_DURATION = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 720;
      const list = document.getElementById("word-list");
      const search = document.getElementById("search");
      const filters = [...document.querySelectorAll(".filter")];
      const masteredCount = document.getElementById("mastered-count");
      const progressBar = document.getElementById("progress-bar");
      const resetButton = document.getElementById("reset-button");
      const shuffleButton = document.getElementById("shuffle-button");
      const toast = document.getElementById("toast");
      const toastText = document.getElementById("toast-text");
      const undoButton = document.getElementById("undo-button");
      const listView = document.getElementById("list-view");
      const entryView = document.getElementById("entry-view");
      const entryBack = document.getElementById("entry-back");
      const entryNumber = document.getElementById("entry-number");
      const entryWord = document.getElementById("entry-word");
      const entryPhonetic = document.getElementById("entry-phonetic");
      const entryPart = document.getElementById("entry-part");
      const entryTranslation = document.getElementById("entry-translation");
      const entryDefinition = document.getElementById("entry-definition");
      const entryRelationsSection = document.getElementById("entry-relations-section");
      const formGroup = document.getElementById("form-group");
      const phraseGroup = document.getElementById("phrase-group");
      const synonymGroup = document.getElementById("synonym-group");
      const antonymGroup = document.getElementById("antonym-group");
      const relatedGroup = document.getElementById("related-group");
      const entryForms = document.getElementById("entry-forms");
      const entryPhrases = document.getElementById("entry-phrases");
      const entrySynonyms = document.getElementById("entry-synonyms");
      const entryAntonyms = document.getElementById("entry-antonyms");
      const entryRelated = document.getElementById("entry-related");
      const entryExample = document.getElementById("entry-example");
      const entryExampleSection = document.getElementById("entry-example-section");
      const entryMastered = document.getElementById("entry-mastered");
      const previousEntry = document.getElementById("previous-entry");
      const nextEntry = document.getElementById("next-entry");
      const wordIndex = new Map(WORDS.map(word => [word.w.toLocaleLowerCase(), word]));

      let mastered = loadProgress();
      let view = "learning";
      let query = "";
      let visibleWords = [];
      let randomizedWords = [];
      let randomized = false;
      let renderedCount = 0;
      let lastChanged = null;
      let toastTimer = null;
      let currentEntry = null;

      function loadProgress() {
        try {
          const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
          return new Set(Array.isArray(stored) ? stored : []);
        } catch (_) {
          return new Set();
        }
      }

      function saveProgress() {
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify([...mastered]));
        } catch (_) {
          // The checklist still works when local storage is unavailable.
        }
      }

      function normalize(value) {
        return value.toLocaleLowerCase().trim();
      }

      function matches(word) {
        const learned = mastered.has(word.w.toLocaleLowerCase());
        if (view === "learning" && learned) return false;
        if (view === "mastered" && !learned) return false;
        if (!query) return true;
        const forms = Object.values(word.forms || {}).flat().join(" ");
        return normalize(`${word.w} ${word.p} ${word.pos} ${word.d} ${word.t} ${word.e} ${forms} ${(word.phr || []).join(" ")}`).includes(query);
      }

      function escapeHtml(value) {
        return value.replace(/[&<>'"]/g, character => ({
          "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
        })[character]);
      }

      function highlighted(value) {
        const safe = escapeHtml(value);
        if (!query) return safe;
        const safeQuery = escapeHtml(query).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        return safe.replace(new RegExp(`(${safeQuery})`, "ig"), "<mark>$1</mark>");
      }

      function updateSummary() {
        masteredCount.textContent = mastered.size.toLocaleString("zh-CN");
        progressBar.style.width = `${(mastered.size / WORDS.length) * 100}%`;
      }

      function emptyMessage() {
        if (query) return ["没有找到匹配的词汇", "试试其他英文单词或中文关键词。"]; 
        if (view === "learning") return ["这一组已经全部掌握", "可以切换到“已掌握”查看，或清空进度重新开始。"]; 
        return ["这里还没有单词", "勾选会的单词后，它们会出现在这里。"]; 
      }

      function render(reset = true) {
        if (reset) {
          const source = randomized ? randomizedWords : WORDS;
          visibleWords = source.filter(matches);
          renderedCount = 0;
          list.replaceChildren();
        }
        const next = visibleWords.slice(renderedCount, renderedCount + BATCH_SIZE);
        if (!next.length && renderedCount === 0) {
          const [title, detail] = emptyMessage();
          list.innerHTML = `<div class="empty-state"><div class="empty-icon">✓</div><strong>${title}</strong><p>${detail}</p></div>`;
          updateSummary();
          return;
        }
        const fragment = document.createDocumentFragment();
        next.forEach((word, index) => fragment.appendChild(createRow(word, index)));
        list.appendChild(fragment);
        renderedCount += next.length;
        updateSummary();
      }

      function createRow(word, index) {
        const key = word.w.toLocaleLowerCase();
        const rowPosition = (renderedCount + index) % BATCH_SIZE;
        const learned = mastered.has(key);
        const row = document.createElement("div");
        row.className = `word-row${learned ? " mastered" : ""}`;
        row.dataset.word = key;
        row.style.setProperty("--row-delay", Math.min(rowPosition * 8, 240));
        row.innerHTML = `
          <div class="word">${highlighted(word.w)}</div>
          <div class="phonetic">${highlighted(word.p)}</div>
          <div class="translation">${highlighted(word.t)}</div>`;
        row.tabIndex = 0;
        row.setAttribute("role", "link");
        row.setAttribute("aria-label", `单击查看 ${word.w}，双击标记掌握`);

        let clickTimer = null;
        let lastTapAt = 0;
        let tearing = false;
        const tear = event => {
          event.preventDefault();
          clearTimeout(clickTimer);
          if (tearing || mastered.has(key)) return;
          tearing = true;
          changeMastery(word, true, row);
        };

        row.addEventListener("click", event => {
          const now = performance.now();
          if (lastTapAt && now - lastTapAt <= DOUBLE_TAP_DELAY) {
            lastTapAt = 0;
            tear(event);
            return;
          }
          lastTapAt = now;
          clearTimeout(clickTimer);
          clickTimer = window.setTimeout(() => {
            lastTapAt = 0;
            navigateToEntry(word);
          }, DOUBLE_TAP_DELAY);
        });
        row.addEventListener("dblclick", tear);
        row.addEventListener("keydown", event => {
          if (event.key === "Enter") navigateToEntry(word);
          if (event.key === " " && !mastered.has(key)) {
            event.preventDefault();
            tear(event);
          }
        });
        return row;
      }

      function animateTearOff(row, onFinished) {
        if (!TEAR_DURATION) {
          onFinished();
          return;
        }
        const rectangle = row.getBoundingClientRect();
        const fragment = row.cloneNode(true);
        fragment.classList.remove("mastered", "completing");
        fragment.classList.add("tear-flying");
        Object.assign(fragment.style, {
          position: "fixed",
          left: `${rectangle.left}px`,
          top: `${rectangle.top}px`,
          width: `${rectangle.width}px`,
          height: `${rectangle.height}px`,
          margin: "0",
        });
        document.body.appendChild(fragment);

        row.style.height = `${rectangle.height}px`;
        row.style.setProperty("--tear-height", `${rectangle.height}px`);
        row.classList.add("tear-source");
        window.requestAnimationFrame(() => fragment.classList.add("tear-flying-active"));
        window.setTimeout(() => {
          fragment.remove();
          onFinished();
        }, TEAR_DURATION);
      }

      function changeMastery(word, learned, row) {
        const key = word.w.toLocaleLowerCase();
        if (learned) mastered.add(key); else mastered.delete(key);
        lastChanged = { key, learned };
        saveProgress();
        updateSummary();
        showToast(learned ? `已掌握 ${word.w}` : `已恢复 ${word.w}`);

        const shouldDisappear = (view === "learning" && learned) || (view === "mastered" && !learned);
        if (row && shouldDisappear) {
          animateTearOff(row, () => render(true));
        } else if (row) {
          row.classList.toggle("mastered", learned);
        } else {
          render(true);
        }
        if (currentEntry && currentEntry.w.toLocaleLowerCase() === key) {
          entryMastered.checked = learned;
        }
      }

      function navigateToEntry(word, replace = false) {
        const hash = `#entry=${encodeURIComponent(word.w)}`;
        const state = { entry: word.w.toLocaleLowerCase() };
        if (replace) history.replaceState(state, "", hash);
        else history.pushState(state, "", hash);
        showEntry(word);
      }

      function renderSenses(container, text, fallback) {
        const lines = String(text || "")
          .split(/\n+/)
          .map(line => line.trim())
          .filter(Boolean);
        const senses = lines.length ? lines : [fallback];
        container.replaceChildren();
        senses.forEach((sense, index) => {
          const row = document.createElement("div");
          row.className = "sense-row";
          const number = document.createElement("span");
          number.className = "sense-number";
          number.textContent = String(index + 1);
          const content = document.createElement("span");
          content.className = "sense-text";
          content.textContent = sense;
          row.append(number, content);
          container.appendChild(row);
        });
      }

      function renderForms(forms) {
        const entries = Object.entries(forms || {});
        formGroup.hidden = !entries.length;
        entryForms.replaceChildren();
        entries.forEach(([label, values]) => {
          values.forEach(value => {
            const item = document.createElement("span");
            item.className = "form-item";
            const caption = document.createElement("small");
            caption.textContent = label;
            const form = document.createElement("span");
            form.textContent = value;
            item.append(caption, form);
            entryForms.appendChild(item);
          });
        });
      }

      function renderWordLinks(group, container, words) {
        group.hidden = !words.length;
        container.replaceChildren();
        words.forEach(value => {
          const key = value.toLocaleLowerCase();
          const linkedWord = wordIndex.get(key);
          const element = document.createElement(linkedWord ? "button" : "span");
          element.className = linkedWord ? "relation-word linked" : "relation-word";
          element.textContent = value;
          if (linkedWord) {
            element.type = "button";
            element.addEventListener("click", () => navigateToEntry(linkedWord));
          }
          container.appendChild(element);
        });
      }

      function renderExamples(word) {
        const examples = [word.e, ...(word.wx || [])]
          .map(value => String(value || "").trim())
          .filter((value, index, values) => value && values.indexOf(value) === index)
          .slice(0, 3);
        entryExampleSection.hidden = !examples.length;
        entryExample.replaceChildren();
        examples.forEach((example, index) => {
          const row = document.createElement("div");
          row.className = "example-row";
          const number = document.createElement("span");
          number.textContent = String(index + 1);
          const text = document.createElement("q");
          text.textContent = example;
          row.append(number, text);
          entryExample.appendChild(row);
        });
      }

      function showEntry(word) {
        currentEntry = word;
        listView.hidden = true;
        entryView.hidden = false;
        entryNumber.textContent = `ENTRY ${String(word.n).padStart(4, "0")}`;
        entryWord.textContent = word.w;
        entryPhonetic.textContent = word.p;
        entryPart.textContent = word.pos || "word";
        renderSenses(entryTranslation, word.t, "暂无中文释义");
        renderSenses(entryDefinition, word.d, "No English definition available.");
        renderForms(word.forms || {});
        renderWordLinks(phraseGroup, entryPhrases, word.phr || []);
        renderWordLinks(synonymGroup, entrySynonyms, word.syn || []);
        renderWordLinks(antonymGroup, entryAntonyms, word.ant || []);
        renderWordLinks(relatedGroup, entryRelated, word.rel || []);
        entryRelationsSection.hidden = !(
          Object.keys(word.forms || {}).length
          || word.phr?.length
          || word.syn?.length
          || word.ant?.length
          || word.rel?.length
        );
        renderExamples(word);
        entryMastered.checked = mastered.has(word.w.toLocaleLowerCase());

        const previous = WORDS[word.n - 2];
        const next = WORDS[word.n];
        configureEntryNavigation(previousEntry, previous);
        configureEntryNavigation(nextEntry, next);
        document.title = `${word.w} · 考研英汉词典`;
        window.scrollTo({ top: 0, behavior: "auto" });
      }

      function configureEntryNavigation(button, word) {
        button.disabled = !word;
        button.querySelector("strong").textContent = word ? word.w : "—";
        button.onclick = word ? () => navigateToEntry(word) : null;
      }

      function showList() {
        currentEntry = null;
        entryView.hidden = true;
        listView.hidden = false;
        document.title = "考研英汉词典";
        render(true);
        window.scrollTo({ top: 0, behavior: "auto" });
      }

      function syncRoute() {
        const match = location.hash.match(/^#entry=(.+)$/);
        if (match) {
          const key = decodeURIComponent(match[1]).toLocaleLowerCase();
          const word = wordIndex.get(key);
          if (word) {
            showEntry(word);
            return;
          }
        }
        showList();
      }

      function showToast(message) {
        toastText.textContent = message;
        toast.classList.add("show");
        clearTimeout(toastTimer);
        toastTimer = window.setTimeout(() => toast.classList.remove("show"), 3200);
      }

      undoButton.addEventListener("click", () => {
        if (!lastChanged) return;
        if (lastChanged.learned) mastered.delete(lastChanged.key); else mastered.add(lastChanged.key);
        saveProgress();
        render(true);
        if (currentEntry) entryMastered.checked = mastered.has(currentEntry.w.toLocaleLowerCase());
        toast.classList.remove("show");
        lastChanged = null;
      });

      search.addEventListener("input", () => {
        query = normalize(search.value);
        render(true);
      });

      filters.forEach(button => button.addEventListener("click", () => {
        view = button.dataset.view;
        filters.forEach(item => item.classList.toggle("active", item === button));
        render(true);
      }));

      function shuffledCopy(items) {
        const result = [...items];
        for (let index = result.length - 1; index > 0; index -= 1) {
          const swapIndex = Math.floor(Math.random() * (index + 1));
          [result[index], result[swapIndex]] = [result[swapIndex], result[index]];
        }
        return result;
      }

      shuffleButton.addEventListener("click", () => {
        randomized = !randomized;
        if (randomized) randomizedWords = shuffledCopy(WORDS);
        shuffleButton.textContent = randomized ? "A–Z" : "随机";
        shuffleButton.setAttribute("aria-pressed", String(randomized));
        render(true);
      });

      entryMastered.addEventListener("change", event => {
        if (currentEntry) changeMastery(currentEntry, event.target.checked, null);
      });

      entryBack.addEventListener("click", () => {
        if (history.state && history.state.entry) {
          history.back();
        } else {
          history.replaceState({ view: "list" }, "", location.href.split("#")[0]);
          showList();
        }
      });

      window.addEventListener("popstate", syncRoute);

      resetButton.addEventListener("click", () => {
        if (!mastered.size) return;
        if (!window.confirm("确定清空全部学习进度吗？")) return;
        mastered.clear();
        saveProgress();
        render(true);
      });

      window.addEventListener("scroll", () => {
        const nearBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 700;
        if (nearBottom && renderedCount < visibleWords.length) render(false);
      }, { passive: true });

      if (!location.hash) history.replaceState({ view: "list" }, "", location.href);
      syncRoute();
    })();
  </script>
</body>
</html>
'''


if __name__ == "__main__":
    main()
