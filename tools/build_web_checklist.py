from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dictionaries" / "graduate-core.json"
OUTPUT = ROOT / "web" / "graduate-vocab-checklist.html"


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    words = [
        {
            "n": index,
            "w": item["word"],
            "p": item.get("phonetic", ""),
            "t": item.get("translation", ""),
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
    <section class="hero" aria-labelledby="page-title">
      <div class="hero-top">
        <div>
          <p class="eyebrow">GRADUATE VOCABULARY</p>
          <h1 id="page-title">考研词汇<span class="brand-accent">清单</span></h1>
          <p class="subtitle">会的直接勾选，单词会自动从未掌握清单中隐藏。</p>
        </div>
        <div class="summary" aria-live="polite">
          已掌握 <strong id="mastered-count">0</strong> / <span id="total-count">__WORD_COUNT__</span>
        </div>
      </div>
      <div class="progress-track" aria-hidden="true"><div class="progress-bar" id="progress-bar"></div></div>
    </section>

    <section class="toolbar" aria-label="词汇筛选">
      <label class="search-wrap">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.5-3.5"></path></svg>
        <input class="search" id="search" type="search" placeholder="搜索英文或中文释义" autocomplete="off">
      </label>
      <div class="filters" role="group" aria-label="显示范围">
        <button class="filter active" type="button" data-view="learning">未掌握</button>
        <button class="filter" type="button" data-view="mastered">已掌握</button>
        <button class="filter" type="button" data-view="all">全部</button>
      </div>
    </section>

    <section class="list-card" aria-label="考研词汇表">
      <div class="list-head" aria-hidden="true">
        <span>序号</span><span>会了</span><span>单词</span><span>音标</span><span>中文释义</span>
      </div>
      <div id="word-list"></div>
    </section>

    <footer class="footer">
      <span>共 __WORD_COUNT__ 个考研词汇 · 学习进度仅保存在当前浏览器</span>
      <button class="text-button danger" id="reset-button" type="button">清空学习进度</button>
    </footer>
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
      const list = document.getElementById("word-list");
      const search = document.getElementById("search");
      const filters = [...document.querySelectorAll(".filter")];
      const masteredCount = document.getElementById("mastered-count");
      const progressBar = document.getElementById("progress-bar");
      const resetButton = document.getElementById("reset-button");
      const toast = document.getElementById("toast");
      const toastText = document.getElementById("toast-text");
      const undoButton = document.getElementById("undo-button");

      let mastered = loadProgress();
      let view = "learning";
      let query = "";
      let visibleWords = [];
      let renderedCount = 0;
      let lastChanged = null;
      let toastTimer = null;

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
        return normalize(`${word.w} ${word.p} ${word.t}`).includes(query);
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
          visibleWords = WORDS.filter(matches);
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
          <div class="row-number">${String(word.n).padStart(4, "0")}</div>
          <div class="check-cell"><input class="check" type="checkbox" ${learned ? "checked" : ""} aria-label="${escapeHtml(word.w)} 已掌握"></div>
          <div class="word">${highlighted(word.w)}</div>
          <div class="phonetic">${highlighted(word.p)}</div>
          <div class="translation">${highlighted(word.t)}</div>`;
        row.querySelector(".check").addEventListener("change", event => changeMastery(word, event.target.checked, row));
        return row;
      }

      function changeMastery(word, learned, row) {
        const key = word.w.toLocaleLowerCase();
        if (learned) mastered.add(key); else mastered.delete(key);
        lastChanged = { key, learned };
        saveProgress();
        updateSummary();
        showToast(learned ? `已掌握 ${word.w}` : `已恢复 ${word.w}`);

        const shouldDisappear = (view === "learning" && learned) || (view === "mastered" && !learned);
        if (shouldDisappear) {
          row.classList.add("completing");
          window.setTimeout(() => render(true), 190);
        } else {
          row.classList.toggle("mastered", learned);
        }
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

      render(true);
    })();
  </script>
</body>
</html>
'''


if __name__ == "__main__":
    main()
