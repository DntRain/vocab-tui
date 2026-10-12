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
            "w": item["word"],
            "p": item.get("phonetic", ""),
            "t": item.get("translation", ""),
        }
        for item in payload["words"]
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
      --bg: #f5f7f8;
      --paper: #ffffff;
      --ink: #17201e;
      --muted: #77817e;
      --line: #e4e9e7;
      --accent: #14b89a;
      --accent-soft: #e8f8f4;
      --purple: #aa8fd2;
      --danger: #b34c54;
      --shadow: 0 12px 36px rgba(25, 52, 45, .08);
    }

    * { box-sizing: border-box; }

    html { scroll-behavior: smooth; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
      -webkit-font-smoothing: antialiased;
    }

    button, input { font: inherit; }

    .app {
      width: min(980px, calc(100% - 28px));
      margin: 28px auto 64px;
    }

    .hero {
      margin-bottom: 18px;
      padding: 22px 24px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--paper);
      box-shadow: var(--shadow);
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

    h1 {
      margin: 0;
      font-size: clamp(24px, 4vw, 34px);
      letter-spacing: -.04em;
    }

    .brand-accent {
      background: linear-gradient(90deg, var(--accent), var(--purple));
      color: transparent;
      background-clip: text;
      -webkit-background-clip: text;
    }

    .subtitle {
      margin: 7px 0 0;
      color: var(--muted);
      font-size: 14px;
    }

    .summary {
      flex: 0 0 auto;
      gap: 5px;
      color: var(--muted);
      font-size: 14px;
      white-space: nowrap;
    }

    .summary strong {
      color: var(--ink);
      font-size: 19px;
    }

    .progress-track {
      height: 5px;
      margin-top: 20px;
      overflow: hidden;
      border-radius: 999px;
      background: #edf1ef;
    }

    .progress-bar {
      width: 0;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--accent), var(--purple));
      transition: width .25s ease;
    }

    .toolbar {
      position: sticky;
      top: 10px;
      z-index: 10;
      gap: 10px;
      margin-bottom: 12px;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(255, 255, 255, .94);
      box-shadow: 0 8px 28px rgba(25, 52, 45, .07);
      backdrop-filter: blur(12px);
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
      background: #fafcfb;
      color: var(--ink);
      transition: border-color .15s, box-shadow .15s;
    }

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

    .filter { padding: 0 13px; }

    .filter:hover,
    .text-button:hover { color: var(--ink); background: #f1f4f3; }

    .filter.active {
      background: var(--accent-soft);
      color: #087b68;
      font-weight: 650;
    }

    .list-card {
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: var(--paper);
      box-shadow: var(--shadow);
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
      transition: opacity .2s, translate .2s, background .15s;
    }

    .word-row:last-child { border-bottom: 0; }
    .word-row:hover { background: #fafcfb; }
    .word-row.completing { opacity: 0; translate: 12px 0; }
    .word-row.mastered { opacity: .62; }

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
      transition: .15s ease;
    }

    .check:hover { border-color: var(--accent); }

    .check:checked {
      border-color: var(--accent);
      background: var(--accent);
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
      font-weight: 700;
      overflow-wrap: anywhere;
    }

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

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
    }
  </style>
</head>
<body>
  <main class="app">
    <section class="hero" aria-labelledby="page-title">
      <div class="hero-top">
        <div>
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
        <span>会了</span><span>单词</span><span>音标</span><span>中文释义</span>
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
        next.forEach(word => fragment.appendChild(createRow(word)));
        list.appendChild(fragment);
        renderedCount += next.length;
        updateSummary();
      }

      function createRow(word) {
        const key = word.w.toLocaleLowerCase();
        const learned = mastered.has(key);
        const row = document.createElement("div");
        row.className = `word-row${learned ? " mastered" : ""}`;
        row.dataset.word = key;
        row.innerHTML = `
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
