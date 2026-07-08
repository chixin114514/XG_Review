from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_BANK = Path("/Users/jiaqiaosu/Downloads/question_bank_combined_en_schema.json")
OUTPUT = ROOT / "index.html"
CORE = ROOT / "src" / "app-core.mjs"
LOCAL_BANK_JSON = ROOT / "question_bank_combined_en_schema.json"
LOCAL_BANK_JS = ROOT / "question_bank_combined_en_schema.js"
SERIES_BANK_JSON = ROOT / "x_same_series_selected_renamed.json"
SERIES_BANK_JS = ROOT / "x_same_series_selected_renamed.js"


def load_questions() -> list[dict]:
    return json.loads(SOURCE_BANK.read_text(encoding="utf-8"))


def write_question_bank_files(questions: list[dict]) -> None:
    LOCAL_BANK_JSON.write_text(
        json.dumps(questions, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    LOCAL_BANK_JS.write_text(
        "window.QUESTION_BANK = "
        + json.dumps(questions, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def load_series_bank() -> list[dict]:
    return json.loads(SERIES_BANK_JSON.read_text(encoding="utf-8"))


def write_series_bank_file(series_bank: list[dict]) -> None:
    SERIES_BANK_JS.write_text(
        "window.SAME_SERIES_BANK = "
        + json.dumps(series_bank, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def browser_core() -> str:
    source = CORE.read_text(encoding="utf-8")
    source = source.replace("export const ", "const ")
    source = source.replace("export function ", "function ")
    return f"""
const Core = (() => {{
{source}
  return {{
    getSubjectLabel,
    getQuestionType,
    getQuestionTypeLabel,
    normalizeAnswer,
    shuffleOptionEntries,
    shuffleOptionValues,
    getDisplayedCorrectAnswer,
    isCorrectAnswer,
    canSubmitAnswer,
    getQuestionStats,
    getQuestionWeight,
    buildWeightedPool,
    pickUniformQuestion,
    pickWeightedQuestion,
    selectPaperQuestions,
    searchQuestionBank,
    rememberQuestion,
    takePreviousQuestion,
    updateProgressAfterAnswer,
  }};
}})();
"""


def build_html() -> str:
    core_js = browser_core()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>习概毛概高效刷题工具</title>
  <style>
    :root {{
      --paper: #f8f3e7;
      --paper-strong: #fffaf0;
      --ink: #23201b;
      --muted: #756f64;
      --line: #d8cdbb;
      --red: #b61f2b;
      --red-dark: #7e1420;
      --teal: #176f73;
      --teal-soft: #d8f0ee;
      --gold: #a86d16;
      --green: #276738;
      --wrong: #a62922;
      --shadow: 0 22px 55px rgba(67, 45, 17, 0.14);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        radial-gradient(circle at 12% 14%, rgba(182, 31, 43, 0.12), transparent 30%),
        linear-gradient(135deg, #f8f3e7 0%, #f4e7d2 45%, #e8f0ec 100%);
      font-family: "Iowan Old Style", "Songti SC", "STSong", "Noto Serif CJK SC", Georgia, serif;
    }}

    button,
    input,
    select {{
      font: inherit;
    }}

    button {{
      cursor: pointer;
    }}

    .shell {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 26px 0 34px;
    }}

    .topbar {{
      display: grid;
      grid-template-columns: minmax(260px, 1fr) auto;
      gap: 18px;
      align-items: end;
      padding-bottom: 18px;
      border-bottom: 2px solid rgba(35, 32, 27, 0.12);
    }}

    .brand h1 {{
      margin: 0;
      font-size: clamp(28px, 4vw, 48px);
      line-height: 1.02;
      letter-spacing: 0;
    }}

    .brand p {{
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 15px;
    }}

    .stats-strip {{
      display: grid;
      grid-template-columns: repeat(4, minmax(92px, 1fr));
      gap: 8px;
      min-width: min(520px, 100%);
    }}

    .stat {{
      padding: 10px 12px;
      border: 1px solid var(--line);
      background: rgba(255, 250, 240, 0.72);
      box-shadow: 0 10px 26px rgba(67, 45, 17, 0.08);
    }}

    .stat span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
    }}

    .stat strong {{
      display: block;
      margin-top: 3px;
      font-size: 22px;
      line-height: 1;
    }}

    .layout {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 330px;
      gap: 18px;
      margin-top: 20px;
    }}

    .view-nav {{
      display: inline-flex;
      gap: 8px;
      margin-top: 16px;
      padding: 5px;
      border: 1px solid var(--line);
      background: rgba(255, 250, 240, 0.72);
      box-shadow: 0 12px 26px rgba(67, 45, 17, 0.08);
    }}

    .view-tab {{
      min-height: 38px;
      padding: 8px 16px;
      border: 1px solid transparent;
      background: transparent;
      color: var(--muted);
      font-weight: 800;
    }}

    .view-tab.active {{
      border-color: var(--red);
      background: var(--red);
      color: #fff;
    }}

    .app-view {{
      margin-top: 20px;
    }}

    .panel {{
      border: 1px solid var(--line);
      background: rgba(255, 250, 240, 0.82);
      box-shadow: var(--shadow);
    }}

    .toolbar {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 10px;
      padding: 14px;
      border-bottom: 1px solid var(--line);
    }}

    .field label {{
      display: block;
      margin-bottom: 5px;
      color: var(--muted);
      font-size: 12px;
    }}

    .field select,
    .field input {{
      width: 100%;
      min-height: 40px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 0;
      color: var(--ink);
      background: var(--paper-strong);
    }}

    .checkbox-field {{
      display: flex;
      align-items: end;
      min-height: 62px;
    }}

    .checkbox-field label {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 40px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      background: var(--paper-strong);
      color: var(--ink);
      font-weight: 700;
    }}

    .checkbox-field input {{
      width: 18px;
      height: 18px;
      accent-color: var(--red);
    }}

    .toggle-line {{
      display: flex;
      align-items: end;
      gap: 8px;
    }}

    .toggle-button,
    .ghost-button,
    .primary-button,
    .danger-button {{
      min-height: 40px;
      padding: 9px 13px;
      border: 1px solid var(--line);
      border-radius: 0;
      color: var(--ink);
      background: var(--paper-strong);
      transition: transform 140ms ease, box-shadow 140ms ease, background 140ms ease;
    }}

    .toggle-button.active,
    .primary-button {{
      border-color: var(--red);
      color: #fff;
      background: var(--red);
    }}

    .danger-button {{
      border-color: rgba(166, 41, 34, 0.45);
      color: var(--wrong);
    }}

    .ghost-button:hover,
    .toggle-button:hover,
    .primary-button:hover,
    .danger-button:hover {{
      transform: translateY(-1px);
      box-shadow: 0 12px 24px rgba(67, 45, 17, 0.14);
    }}

    .question-area {{
      padding: 22px;
    }}

    .meta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin-bottom: 18px;
    }}

    .pill {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 5px 9px;
      border: 1px solid var(--line);
      color: var(--muted);
      background: rgba(248, 243, 231, 0.7);
      font-size: 13px;
    }}

    .pill.subject {{
      border-color: rgba(182, 31, 43, 0.38);
      color: var(--red-dark);
      background: rgba(182, 31, 43, 0.08);
      font-weight: 700;
    }}

    .pill.type-badge {{
      min-height: 42px;
      padding: 7px 14px;
      border: 2px solid var(--teal);
      color: #fff;
      background: var(--teal);
      font-size: 20px;
      font-weight: 900;
      line-height: 1;
      box-shadow: 0 10px 22px rgba(23, 111, 115, 0.18);
    }}

    .question-text {{
      margin: 0 0 18px;
      font-size: clamp(21px, 2.3vw, 30px);
      line-height: 1.45;
      letter-spacing: 0;
    }}

    .options {{
      display: grid;
      gap: 10px;
    }}

    .option {{
      display: grid;
      grid-template-columns: 42px minmax(0, 1fr);
      gap: 12px;
      align-items: center;
      width: 100%;
      min-height: 58px;
      padding: 10px 14px 10px 10px;
      border: 1px solid var(--line);
      color: var(--ink);
      text-align: left;
      background: rgba(255, 250, 240, 0.88);
      transition: border-color 140ms ease, background 140ms ease, transform 140ms ease;
    }}

    .option:hover {{
      border-color: rgba(23, 111, 115, 0.5);
      transform: translateX(2px);
    }}

    .option.selected {{
      border-color: var(--teal);
      background: var(--teal-soft);
    }}

    .option.correct {{
      border-color: var(--green);
      background: rgba(39, 103, 56, 0.13);
    }}

    .option.wrong {{
      border-color: var(--wrong);
      background: rgba(166, 41, 34, 0.12);
    }}

    .option[disabled] {{
      cursor: default;
      transform: none;
    }}

    .option-key {{
      display: inline-grid;
      place-items: center;
      width: 34px;
      height: 34px;
      border: 1px solid rgba(35, 32, 27, 0.18);
      background: #fffaf0;
      font-weight: 800;
    }}

    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      margin-top: 18px;
    }}

    .actions select {{
      min-height: 40px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      background: var(--paper-strong);
      color: var(--ink);
    }}

    .feedback {{
      min-height: 34px;
      margin-top: 14px;
      color: var(--muted);
      line-height: 1.55;
    }}

    .feedback.good {{
      color: var(--green);
      font-weight: 700;
    }}

    .feedback.bad {{
      color: var(--wrong);
      font-weight: 700;
    }}

    .side {{
      display: grid;
      gap: 14px;
      align-content: start;
    }}

    .side-section {{
      padding: 14px;
      border: 1px solid var(--line);
      background: rgba(255, 250, 240, 0.82);
      box-shadow: 0 16px 34px rgba(67, 45, 17, 0.11);
    }}

    .side-section h2 {{
      margin: 0 0 10px;
      font-size: 18px;
      line-height: 1.2;
    }}

    .note-box {{
      display: grid;
      gap: 8px;
    }}

    .note-box h2 {{
      cursor: pointer;
      user-select: none;
    }}

    .note-box textarea {{
      width: 100%;
      min-height: 140px;
      resize: vertical;
      padding: 9px 10px;
      border: 1px solid var(--line);
      background: var(--paper-strong);
      color: var(--ink);
      line-height: 1.55;
    }}

    .note-box textarea:disabled {{
      color: var(--muted);
      background: rgba(248, 243, 231, 0.62);
      cursor: not-allowed;
    }}

    .note-box:not(.note-revealed) textarea {{
      display: none;
    }}

    .note-box.note-revealed textarea {{
      display: block;
    }}

    .meter {{
      height: 12px;
      overflow: hidden;
      border: 1px solid var(--line);
      background: rgba(35, 32, 27, 0.08);
    }}

    .meter > div {{
      height: 100%;
      width: 0;
      background: linear-gradient(90deg, var(--red), var(--teal));
      transition: width 200ms ease;
    }}

    .wrong-book-view {{
      border: 1px solid var(--line);
      background: rgba(255, 250, 240, 0.82);
      box-shadow: var(--shadow);
    }}

    .wrong-book-header {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 14px;
      align-items: end;
      padding: 18px;
      border-bottom: 1px solid var(--line);
    }}

    .wrong-book-header h2 {{
      margin: 0;
      font-size: 28px;
      line-height: 1.1;
    }}

    .wrong-book-header p {{
      margin: 6px 0 0;
      color: var(--muted);
      line-height: 1.5;
    }}

    .wrong-filters {{
      display: grid;
      grid-template-columns: repeat(2, minmax(150px, 1fr));
      gap: 10px;
      min-width: min(360px, 100%);
    }}

    .wrong-book-list {{
      display: grid;
      gap: 10px;
      padding: 16px;
    }}

    .search-controls {{
      display: grid;
      grid-template-columns: minmax(260px, 1fr) minmax(140px, 180px) minmax(140px, 180px) auto;
      gap: 10px;
      align-items: end;
      padding: 18px;
      border-bottom: 1px solid var(--line);
    }}

    .list-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: end;
      align-items: end;
    }}

    .list-pager {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      padding: 0 16px 16px;
    }}

    .paper-controls {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 10px;
      padding: 18px;
      border-bottom: 1px solid var(--line);
    }}

    .paper-actions {{
      display: flex;
      gap: 10px;
      align-items: end;
    }}

    .paper-list {{
      display: grid;
      gap: 14px;
      padding: 16px;
    }}

    .paper-item {{
      display: grid;
      gap: 10px;
      padding: 14px;
      border: 1px solid rgba(216, 205, 187, 0.9);
      background: rgba(248, 243, 231, 0.7);
    }}

    .paper-question {{
      margin: 0;
      font-size: 18px;
      line-height: 1.55;
      font-weight: 800;
    }}

    .paper-answer {{
      margin: 0;
      line-height: 1.55;
    }}

    .series-controls {{
      display: grid;
      grid-template-columns: minmax(240px, 1fr) minmax(160px, 220px) auto;
      gap: 10px;
      align-items: end;
      padding: 18px;
      border-bottom: 1px solid var(--line);
    }}

    .series-question-area {{
      padding: 22px;
    }}

    .series-builder {{
      display: grid;
      gap: 12px;
      padding: 18px;
      border-bottom: 1px solid var(--line);
      background: rgba(248, 243, 231, 0.42);
    }}

    .series-builder-grid {{
      display: grid;
      grid-template-columns: minmax(160px, 0.8fr) minmax(240px, 1.4fr) auto;
      gap: 10px;
      align-items: end;
    }}

    .series-builder-lists {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }}

    .series-list-panel {{
      display: grid;
      gap: 8px;
      align-content: start;
      min-height: 112px;
      padding: 10px;
      border: 1px solid rgba(216, 205, 187, 0.9);
      background: rgba(255, 250, 240, 0.72);
    }}

    .series-list-panel h3 {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.2;
    }}

    .series-search-results,
    .custom-series-selected-list {{
      display: grid;
      gap: 8px;
    }}

    .wrong-item {{
      display: grid;
      gap: 6px;
      padding: 12px;
      border: 1px solid rgba(216, 205, 187, 0.9);
      background: rgba(248, 243, 231, 0.7);
    }}

    .wrong-item p {{
      margin: 0;
      font-size: 13px;
      line-height: 1.45;
    }}

    .compact-options {{
      display: grid;
      gap: 4px;
      margin-top: 2px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
    }}

    .compact-option {{
      display: grid;
      grid-template-columns: 24px minmax(0, 1fr);
      gap: 6px;
      align-items: start;
    }}

    .compact-option-key {{
      color: var(--red-dark);
      font-weight: 800;
    }}

    .answer-line {{
      color: var(--green);
      font-weight: 800;
    }}

    .wrong-item button {{
      justify-self: start;
      min-height: 30px;
      padding: 5px 9px;
      border: 1px solid var(--line);
      background: #fffaf0;
      color: var(--ink);
    }}

    .wrong-item button.danger-button {{
      border-color: rgba(166, 41, 34, 0.45);
      color: var(--wrong);
    }}

    .series-add-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}

    .series-add-row select {{
      min-height: 30px;
      padding: 5px 8px;
      border: 1px solid var(--line);
      background: #fffaf0;
      color: var(--ink);
      font-size: 13px;
    }}

    .wrong-item-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}

    .storage-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}

    .storage-row select {{
      width: 100%;
      min-height: 40px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      background: var(--paper-strong);
      color: var(--ink);
    }}

    .empty {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }}

    .hidden {{
      display: none !important;
    }}

    @media (max-width: 900px) {{
      .topbar,
      .wrong-book-header,
      .layout {{
        grid-template-columns: 1fr;
      }}

      .stats-strip,
      .toolbar,
      .paper-controls,
      .series-builder-grid,
      .series-builder-lists,
      .series-controls,
      .search-controls,
      .wrong-filters {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 560px) {{
      .shell {{
        width: min(100% - 20px, 1180px);
        padding-top: 14px;
      }}

      .stats-strip,
      .toolbar,
      .paper-controls,
      .series-builder-grid,
      .series-builder-lists,
      .series-controls,
      .search-controls,
      .wrong-filters,
      .storage-row {{
        grid-template-columns: 1fr;
      }}

      .question-area {{
        padding: 16px;
      }}

      .option {{
        grid-template-columns: 36px minmax(0, 1fr);
        padding-right: 10px;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="topbar">
      <div class="brand">
        <h1>习概毛概刷题</h1>
        <p>错题加权随机，所有题保留基础出现机会。</p>
      </div>
      <section class="stats-strip" aria-label="刷题统计">
        <div class="stat"><span>今日</span><strong id="today-count">0</strong></div>
        <div class="stat"><span>总正确率</span><strong id="accuracy">0%</strong></div>
        <div class="stat"><span>错题</span><strong id="wrong-total">0</strong></div>
        <div class="stat"><span>题库</span><strong id="bank-total">458</strong></div>
      </section>
    </header>

    <nav class="view-nav" aria-label="视图切换">
      <button class="view-tab active" data-view="practice" type="button">刷题</button>
      <button class="view-tab" data-view="paper" type="button">组卷</button>
      <button class="view-tab" data-view="series" type="button">专题复习</button>
      <button class="view-tab" data-view="search" type="button">搜题</button>
      <button class="view-tab" data-view="wrongBook" type="button">错题本</button>
      <button class="view-tab" data-view="favorite" type="button">收藏</button>
    </nav>

    <section class="layout app-view" id="practice-view">
      <section class="panel" aria-label="刷题区">
        <div class="toolbar">
          <div class="field">
            <label for="subject-filter">科目</label>
            <select id="subject-filter">
              <option value="all">全部</option>
              <option value="X">习概</option>
              <option value="M">毛概</option>
            </select>
          </div>
          <div class="field">
            <label for="type-filter">题型</label>
            <select id="type-filter">
              <option value="all">全部</option>
              <option value="single">单选</option>
              <option value="multiple">多选</option>
              <option value="truefalse">判断</option>
            </select>
          </div>
          <div class="field">
            <label for="scope-filter">范围</label>
            <select id="scope-filter">
              <option value="all">全题库</option>
              <option value="wrong">只刷错题</option>
              <option value="favorite">只刷收藏</option>
            </select>
          </div>
          <div class="field">
            <label for="weight-mode-filter">抽题</label>
            <select id="weight-mode-filter">
              <option value="weighted">错题加权</option>
              <option value="uniform">不加权</option>
            </select>
          </div>
          <div class="checkbox-field">
            <label for="shuffle-options">
              <input id="shuffle-options" type="checkbox">
              打乱内容
            </label>
          </div>
          <div class="toggle-line">
            <button class="toggle-button" id="favorite-current" type="button">收藏本题</button>
          </div>
        </div>

        <div class="question-area">
          <div class="meta-row" id="meta-row"></div>
          <h2 class="question-text" id="question-text"></h2>
          <div class="options" id="options"></div>
          <div class="actions">
            <button class="primary-button" id="submit-answer" type="button">提交</button>
            <button class="ghost-button" id="previous-question" type="button">上一题</button>
            <button class="ghost-button" id="skip-question" type="button">跳过</button>
            <button class="ghost-button" id="mark-mastered" type="button">标记掌握</button>
            <select id="current-series-target" aria-label="选择专题系列"></select>
            <button class="ghost-button" id="add-current-to-series" type="button">加入专题</button>
          </div>
          <div class="feedback" id="feedback"></div>
        </div>
      </section>

      <aside class="side" aria-label="刷题数据">
        <section class="side-section">
          <h2>当前题</h2>
          <p class="empty" id="current-stats">尚未选择题目。</p>
          <div class="meter" aria-hidden="true"><div id="current-weight-bar"></div></div>
        </section>

        <section class="side-section note-box" id="question-note-box">
          <h2>笔记</h2>
          <p class="empty" id="note-status">提交答案后才能查看或修改笔记。</p>
          <textarea id="question-note" placeholder="提交答案后记录这道题的易错点。"></textarea>
        </section>

        <section class="side-section">
          <h2>进度</h2>
          <div class="storage-row">
            <button class="ghost-button" id="export-progress" type="button">导出</button>
            <button class="ghost-button" id="import-progress-button" type="button">导入</button>
            <select id="import-mode" aria-label="导入模式">
              <option value="merge">合并导入</option>
              <option value="replace">覆盖导入</option>
            </select>
            <button class="danger-button" id="reset-progress" type="button">重置</button>
            <input class="hidden" id="import-progress" type="file" accept="application/json">
          </div>
          <p class="empty" id="storage-status">导出会包含进度、笔记、收藏和专题配置。</p>
        </section>
      </aside>
    </section>

    <section class="app-view wrong-book-view hidden" id="search-view" aria-label="搜题">
      <header class="wrong-book-header">
        <div>
          <h2>搜题</h2>
          <p id="question-search-summary">输入题干或选项关键词后搜索题库。</p>
        </div>
      </header>
      <div class="search-controls">
        <div class="field">
          <label for="question-search-query">关键词</label>
          <input id="question-search-query" type="search" placeholder="输入题干或选项关键词">
        </div>
        <div class="field">
          <label for="question-search-subject">科目</label>
          <select id="question-search-subject">
            <option value="all">全部</option>
            <option value="X">习概</option>
            <option value="M">毛概</option>
          </select>
        </div>
        <div class="field">
          <label for="question-search-type">题型</label>
          <select id="question-search-type">
            <option value="all">全部</option>
            <option value="single">单选</option>
            <option value="multiple">多选</option>
            <option value="truefalse">判断</option>
          </select>
        </div>
        <button class="primary-button" id="question-search-button" type="button">搜索</button>
      </div>
      <div class="wrong-book-list" id="question-search-results"></div>
    </section>

    <section class="app-view wrong-book-view hidden" id="series-view" aria-label="专题复习">
      <header class="wrong-book-header">
        <div>
          <h2>专题复习</h2>
          <p id="series-summary">选择一个同系列专题开始复习。</p>
        </div>
      </header>
      <div class="series-controls">
        <div class="field">
          <label for="series-select">系列</label>
          <select id="series-select"></select>
        </div>
        <div class="checkbox-field">
          <label for="series-shuffle-options">
            <input id="series-shuffle-options" type="checkbox">
            打乱内容
          </label>
        </div>
        <button class="primary-button" id="start-series" type="button">开始专题</button>
      </div>
      <section class="series-builder" aria-label="自定义系列">
        <div class="series-builder-grid">
          <div class="field">
            <label for="custom-series-name">自定义系列名</label>
            <input id="custom-series-name" type="text" placeholder="例如：六个必须坚持">
          </div>
          <div class="field">
            <label for="series-search-query">搜索题库</label>
            <input id="series-search-query" type="search" placeholder="输入题干或选项关键词">
          </div>
          <div class="paper-actions">
            <button class="ghost-button" id="series-search-button" type="button">搜索</button>
            <button class="primary-button" id="save-custom-series" type="button">保存系列</button>
          </div>
        </div>
        <p class="empty" id="custom-series-status">搜索题库后，把相似题加入自定义系列。</p>
        <div class="series-builder-lists">
          <div class="series-list-panel">
            <h3>搜索结果</h3>
            <div class="series-search-results" id="series-search-results"></div>
          </div>
          <div class="series-list-panel">
            <h3>已选题目</h3>
            <div class="custom-series-selected-list" id="custom-series-selected-list"></div>
          </div>
        </div>
      </section>
      <div class="series-question-area">
        <div class="meta-row" id="series-meta-row"></div>
        <h2 class="question-text" id="series-question-text">请选择系列。</h2>
        <div class="options" id="series-options"></div>
        <div class="actions">
          <button class="primary-button" id="series-submit-answer" type="button" disabled>提交</button>
          <button class="ghost-button" id="series-skip-question" type="button" disabled>跳过</button>
        </div>
        <div class="feedback" id="series-feedback"></div>
      </div>
    </section>

    <section class="app-view wrong-book-view hidden" id="paper-view" aria-label="组卷">
      <header class="wrong-book-header">
        <div>
          <h2>组卷</h2>
          <p id="paper-summary">选择条件后生成试卷。</p>
        </div>
      </header>
      <div class="paper-controls">
        <div class="field">
          <label for="paper-subject-filter">科目</label>
          <select id="paper-subject-filter">
            <option value="all">全部</option>
            <option value="X">习概</option>
            <option value="M">毛概</option>
          </select>
        </div>
        <div class="field">
          <label for="paper-type-filter">题型</label>
          <select id="paper-type-filter">
            <option value="all">全部</option>
            <option value="single">单选</option>
            <option value="multiple">多选</option>
            <option value="truefalse">判断</option>
          </select>
        </div>
        <div class="field">
          <label for="paper-weight-mode-filter">抽题</label>
          <select id="paper-weight-mode-filter">
            <option value="weighted">错题加权</option>
            <option value="uniform">不加权</option>
          </select>
        </div>
        <div class="field">
          <label for="paper-count">题量</label>
          <input id="paper-count" type="number" min="1" max="100" value="20">
        </div>
        <div class="paper-actions">
          <button class="primary-button" id="generate-paper" type="button">生成试卷</button>
          <button class="ghost-button" id="submit-paper" type="button" disabled>交卷看答案</button>
        </div>
      </div>
      <div class="paper-list" id="paper-list"></div>
    </section>

    <section class="app-view wrong-book-view hidden" id="wrong-book-view" aria-label="错题本">
      <header class="wrong-book-header">
        <div>
          <h2>错题本</h2>
          <p id="wrong-book-summary">还没有错题。</p>
        </div>
        <div class="wrong-filters">
          <div class="field">
            <label for="wrong-subject-filter">科目</label>
            <select id="wrong-subject-filter">
              <option value="all">全部</option>
              <option value="X">习概</option>
              <option value="M">毛概</option>
            </select>
          </div>
          <div class="field">
            <label for="wrong-type-filter">题型</label>
            <select id="wrong-type-filter">
              <option value="all">全部</option>
              <option value="single">单选</option>
              <option value="multiple">多选</option>
              <option value="truefalse">判断</option>
            </select>
          </div>
        </div>
        <div class="list-actions">
          <button class="primary-button" id="start-wrong-review" type="button">复习错题</button>
        </div>
      </header>
      <div class="wrong-book-list" id="wrong-book-list"></div>
      <div class="list-pager">
        <button class="ghost-button" id="wrong-prev-page" type="button">上一页</button>
        <span class="pill" id="wrong-page-status">第 1 页</span>
        <button class="ghost-button" id="wrong-next-page" type="button">下一页</button>
      </div>
    </section>

    <section class="app-view wrong-book-view hidden" id="favorite-view" aria-label="收藏">
      <header class="wrong-book-header">
        <div>
          <h2>收藏</h2>
          <p id="favorite-summary">还没有收藏题。</p>
        </div>
        <div class="wrong-filters">
          <div class="field">
            <label for="favorite-subject-filter">科目</label>
            <select id="favorite-subject-filter">
              <option value="all">全部</option>
              <option value="X">习概</option>
              <option value="M">毛概</option>
            </select>
          </div>
          <div class="field">
            <label for="favorite-type-filter">题型</label>
            <select id="favorite-type-filter">
              <option value="all">全部</option>
              <option value="single">单选</option>
              <option value="multiple">多选</option>
              <option value="truefalse">判断</option>
            </select>
          </div>
        </div>
        <div class="list-actions">
          <button class="primary-button" id="start-favorite-review" type="button">复习收藏</button>
        </div>
      </header>
      <div class="wrong-book-list" id="favorite-list"></div>
      <div class="list-pager">
        <button class="ghost-button" id="favorite-prev-page" type="button">上一页</button>
        <span class="pill" id="favorite-page-status">第 1 页</span>
        <button class="ghost-button" id="favorite-next-page" type="button">下一页</button>
      </div>
    </section>
  </main>

  <script src="question_bank_combined_en_schema.js"></script>
  <script src="x_same_series_selected_renamed.js"></script>
  <script>
{core_js}

const STORAGE_KEY = 'xi-mao-review-progress-v1';
const TODAY_KEY = 'xi-mao-review-today-v1';
const CUSTOM_SERIES_KEY = 'xi-mao-review-custom-series-v1';
const SERIES_ADDITIONS_KEY = 'xi-mao-review-series-additions-v1';
const LIST_PAGE_SIZE = 20;
const questions = (window.QUESTION_BANK || []).map((question, index) => ({{
  ...question,
  id: index,
}}));
const seriesBank = (window.SAME_SERIES_BANK || []).map((series, seriesIndex) => {{
  const name = series.SERIES || `SERIES_${{seriesIndex + 1}}`;
  return {{
    ...series,
    name,
    questions: (series.questions || []).map((question, questionIndex) => ({{
      ...question,
      id: `${{name}}-${{questionIndex}}`,
    }})),
  }};
}});

const state = {{
  progress: loadProgress(),
  today: loadToday(),
  current: null,
  history: [],
  selected: new Set(),
  displayCorrectAnswer: [],
  answered: false,
  noteRevealed: false,
  paperQuestions: [],
  paperSelections: {{}},
  paperSubmitted: false,
  seriesQuestions: [],
  seriesCurrent: null,
  seriesSelected: new Set(),
  seriesAnswered: false,
  seriesDisplayCorrectAnswer: [],
  customSeries: loadCustomSeries(),
  seriesAdditions: loadSeriesAdditions(),
  customSeriesDraft: [],
  questionSearchResults: [],
  wrongPage: 0,
  favoritePage: 0,
}};

const elements = {{
  viewButtons: document.querySelectorAll('[data-view]'),
  practiceView: document.getElementById('practice-view'),
  paperView: document.getElementById('paper-view'),
  seriesView: document.getElementById('series-view'),
  searchView: document.getElementById('search-view'),
  wrongBookView: document.getElementById('wrong-book-view'),
  favoriteView: document.getElementById('favorite-view'),
  subjectFilter: document.getElementById('subject-filter'),
  typeFilter: document.getElementById('type-filter'),
  scopeFilter: document.getElementById('scope-filter'),
  weightModeFilter: document.getElementById('weight-mode-filter'),
  shuffleOptions: document.getElementById('shuffle-options'),
  paperSubjectFilter: document.getElementById('paper-subject-filter'),
  paperTypeFilter: document.getElementById('paper-type-filter'),
  paperWeightModeFilter: document.getElementById('paper-weight-mode-filter'),
  paperCount: document.getElementById('paper-count'),
  generatePaper: document.getElementById('generate-paper'),
  submitPaper: document.getElementById('submit-paper'),
  paperSummary: document.getElementById('paper-summary'),
  paperList: document.getElementById('paper-list'),
  seriesSelect: document.getElementById('series-select'),
  seriesShuffleOptions: document.getElementById('series-shuffle-options'),
  startSeries: document.getElementById('start-series'),
  seriesSummary: document.getElementById('series-summary'),
  seriesMetaRow: document.getElementById('series-meta-row'),
  seriesQuestionText: document.getElementById('series-question-text'),
  seriesOptions: document.getElementById('series-options'),
  seriesSubmitAnswer: document.getElementById('series-submit-answer'),
  seriesSkipQuestion: document.getElementById('series-skip-question'),
  seriesFeedback: document.getElementById('series-feedback'),
  customSeriesName: document.getElementById('custom-series-name'),
  seriesSearchQuery: document.getElementById('series-search-query'),
  seriesSearchButton: document.getElementById('series-search-button'),
  seriesSearchResults: document.getElementById('series-search-results'),
  customSeriesSelectedList: document.getElementById('custom-series-selected-list'),
  saveCustomSeries: document.getElementById('save-custom-series'),
  customSeriesStatus: document.getElementById('custom-series-status'),
  questionSearchQuery: document.getElementById('question-search-query'),
  questionSearchSubject: document.getElementById('question-search-subject'),
  questionSearchType: document.getElementById('question-search-type'),
  questionSearchButton: document.getElementById('question-search-button'),
  questionSearchResults: document.getElementById('question-search-results'),
  questionSearchSummary: document.getElementById('question-search-summary'),
  wrongSubjectFilter: document.getElementById('wrong-subject-filter'),
  wrongTypeFilter: document.getElementById('wrong-type-filter'),
  startWrongReview: document.getElementById('start-wrong-review'),
  wrongPrevPage: document.getElementById('wrong-prev-page'),
  wrongNextPage: document.getElementById('wrong-next-page'),
  wrongPageStatus: document.getElementById('wrong-page-status'),
  wrongBookSummary: document.getElementById('wrong-book-summary'),
  wrongBookList: document.getElementById('wrong-book-list'),
  favoriteSubjectFilter: document.getElementById('favorite-subject-filter'),
  favoriteTypeFilter: document.getElementById('favorite-type-filter'),
  startFavoriteReview: document.getElementById('start-favorite-review'),
  favoritePrevPage: document.getElementById('favorite-prev-page'),
  favoriteNextPage: document.getElementById('favorite-next-page'),
  favoritePageStatus: document.getElementById('favorite-page-status'),
  favoriteSummary: document.getElementById('favorite-summary'),
  favoriteList: document.getElementById('favorite-list'),
  favoriteCurrent: document.getElementById('favorite-current'),
  metaRow: document.getElementById('meta-row'),
  questionText: document.getElementById('question-text'),
  options: document.getElementById('options'),
  submitAnswer: document.getElementById('submit-answer'),
  previousQuestion: document.getElementById('previous-question'),
  skipQuestion: document.getElementById('skip-question'),
  markMastered: document.getElementById('mark-mastered'),
  currentSeriesTarget: document.getElementById('current-series-target'),
  addCurrentToSeries: document.getElementById('add-current-to-series'),
  feedback: document.getElementById('feedback'),
  currentStats: document.getElementById('current-stats'),
  currentWeightBar: document.getElementById('current-weight-bar'),
  questionNoteBox: document.getElementById('question-note-box'),
  noteStatus: document.getElementById('note-status'),
  questionNote: document.getElementById('question-note'),
  todayCount: document.getElementById('today-count'),
  accuracy: document.getElementById('accuracy'),
  wrongTotal: document.getElementById('wrong-total'),
  bankTotal: document.getElementById('bank-total'),
  exportProgress: document.getElementById('export-progress'),
  importProgressButton: document.getElementById('import-progress-button'),
  importMode: document.getElementById('import-mode'),
  importProgress: document.getElementById('import-progress'),
  resetProgress: document.getElementById('reset-progress'),
  storageStatus: document.getElementById('storage-status'),
}};

function loadProgress() {{
  try {{
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {{}};
  }} catch {{
    return {{}};
  }}
}}

function saveProgress() {{
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.progress));
}}

function loadToday() {{
  const today = new Date().toISOString().slice(0, 10);
  try {{
    const data = JSON.parse(localStorage.getItem(TODAY_KEY)) || {{}};
    return data.date === today ? data : {{ date: today, count: 0 }};
  }} catch {{
    return {{ date: today, count: 0 }};
  }}
}}

function saveToday() {{
  localStorage.setItem(TODAY_KEY, JSON.stringify(state.today));
}}

function normalizeCustomSeries(rawSeries) {{
  if (!rawSeries || !Array.isArray(rawSeries.questions)) return null;
  const name = String(rawSeries.name || `CUSTOM_${{Date.now()}}`);
  const title = String(rawSeries.title || name);
  const questions = rawSeries.questions
    .filter((question) => question && question.question && question.options)
    .map((question, questionIndex) => ({{
      category: question.category,
      question: question.question,
      options: question.options,
      correct_answer: question.correct_answer || [],
      id: `${{name}}-${{questionIndex}}`,
    }}));

  if (!questions.length) return null;
  return {{ name, title, custom: true, questions }};
}}

function loadCustomSeries() {{
  try {{
    const raw = JSON.parse(localStorage.getItem(CUSTOM_SERIES_KEY)) || [];
    return raw.map(normalizeCustomSeries).filter(Boolean);
  }} catch {{
    return [];
  }}
}}

function saveCustomSeries() {{
  localStorage.setItem(CUSTOM_SERIES_KEY, JSON.stringify(state.customSeries));
}}

function loadSeriesAdditions() {{
  try {{
    const raw = JSON.parse(localStorage.getItem(SERIES_ADDITIONS_KEY)) || {{}};
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return {{}};
    return Object.fromEntries(
      Object.entries(raw)
        .filter(([, questionsForSeries]) => Array.isArray(questionsForSeries))
        .map(([seriesName, questionsForSeries]) => [
          seriesName,
          questionsForSeries
            .filter((question) => question && question.question && question.options)
            .map((question, questionIndex) => cloneQuestionForSeries(question, seriesName, questionIndex)),
        ])
    );
  }} catch {{
    return {{}};
  }}
}}

function saveSeriesAdditions() {{
  localStorage.setItem(SERIES_ADDITIONS_KEY, JSON.stringify(state.seriesAdditions));
}}

function switchView(view) {{
  const isPractice = view === 'practice';
  const isPaper = view === 'paper';
  const isSeries = view === 'series';
  const isSearch = view === 'search';
  const isWrongBook = view === 'wrongBook';
  const isFavorite = view === 'favorite';
  elements.practiceView.classList.toggle('hidden', !isPractice);
  elements.paperView.classList.toggle('hidden', !isPaper);
  elements.seriesView.classList.toggle('hidden', !isSeries);
  elements.searchView.classList.toggle('hidden', !isSearch);
  elements.wrongBookView.classList.toggle('hidden', !isWrongBook);
  elements.favoriteView.classList.toggle('hidden', !isFavorite);
  elements.viewButtons.forEach((button) => {{
    button.classList.toggle('active', button.dataset.view === view);
  }});
  if (isPaper) renderPaper();
  if (isSeries) renderSeriesQuestion();
  if (isSearch) renderQuestionSearchResults();
  if (isWrongBook) renderWrongBook();
  if (isFavorite) renderFavoriteBook();
}}

function getFilteredQuestions() {{
  const subject = elements.subjectFilter.value;
  const type = elements.typeFilter.value;
  const scope = elements.scopeFilter.value;

  return questions.filter((question) => {{
    const stats = Core.getQuestionStats(state.progress, question.id);
    const questionType = Core.getQuestionType(question);
    if (subject !== 'all' && question.category !== subject) return false;
    if (type !== 'all' && questionType !== type) return false;
    if (scope === 'wrong' && stats.wrongCount === 0) return false;
    if (scope === 'favorite' && !stats.favorite) return false;
    return true;
  }});
}}

function chooseNextQuestion() {{
  const candidates = getFilteredQuestions();
  if (!candidates.length) {{
    state.current = null;
    renderEmptyState();
    return;
  }}

  const usable = candidates.length > 1 && state.current
    ? candidates.filter((question) => question.id !== state.current.id)
    : candidates;
  const previousId = state.current ? state.current.id : null;
  const nextQuestion = elements.weightModeFilter.value === 'uniform'
    ? Core.pickUniformQuestion(usable)
    : Core.pickWeightedQuestion(usable, state.progress);
  state.history = Core.rememberQuestion(state.history, previousId, nextQuestion.id);
  state.current = nextQuestion;
  state.selected = new Set();
  state.displayCorrectAnswer = [];
  state.answered = false;
  state.noteRevealed = false;
  renderQuestion();
}}

function showPreviousQuestion() {{
  const restored = Core.takePreviousQuestion(questions, state.history);
  if (!restored.question) {{
    elements.feedback.textContent = '没有上一题。';
    elements.feedback.className = 'feedback bad';
    return;
  }}

  state.history = restored.history;
  state.current = restored.question;
  state.selected = new Set();
  state.displayCorrectAnswer = [];
  state.answered = false;
  state.noteRevealed = false;
  renderQuestion();
}}

function renderEmptyState() {{
  elements.metaRow.innerHTML = '<span class="pill">当前筛选下没有题目</span>';
  elements.questionText.textContent = '请调整科目、题型或范围。';
  elements.options.innerHTML = '';
  elements.feedback.textContent = '';
  elements.feedback.className = 'feedback';
  elements.currentStats.textContent = '当前筛选下没有可刷题目。';
  elements.currentWeightBar.style.width = '0%';
  state.noteRevealed = false;
  elements.questionNoteBox.classList.remove('note-revealed');
  elements.questionNote.value = '';
  elements.questionNote.disabled = true;
  elements.noteStatus.textContent = '提交答案后才能查看或修改笔记。';
  elements.submitAnswer.disabled = true;
  elements.submitAnswer.textContent = '提交';
  elements.previousQuestion.disabled = state.history.length === 0;
  elements.favoriteCurrent.disabled = true;
  elements.markMastered.disabled = true;
  elements.addCurrentToSeries.disabled = true;
  renderGlobalStats();
  renderWrongBook();
  renderFavoriteBook();
}}

function renderQuestion() {{
  const question = state.current;
  const type = Core.getQuestionType(question);
  const displayEntries = getDisplayOptionEntries(question);
  state.displayCorrectAnswer = Core.getDisplayedCorrectAnswer(displayEntries, question.correct_answer);

  elements.submitAnswer.disabled = false;
  elements.favoriteCurrent.disabled = false;
  elements.markMastered.disabled = false;
  elements.addCurrentToSeries.disabled = false;
  elements.questionText.textContent = question.question;
  elements.options.innerHTML = '';
  renderQuestionMeta();

  displayEntries.forEach(([key, value, originalKey]) => {{
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'option';
    button.dataset.key = key;
    button.dataset.originalKey = originalKey;
    button.innerHTML = `<span class="option-key">${{key}}</span><span>${{value}}</span>`;
    button.addEventListener('click', () => toggleOption(key));
    elements.options.appendChild(button);
  }});
  syncSelectedOptions();

  elements.feedback.textContent = type === 'multiple' ? '多选题需要选全，少选或多选都算错。' : '';
  elements.feedback.className = 'feedback';
  renderQuestionNote();
  renderCurrentStats();
  renderGlobalStats();
  renderWrongBook();
  renderFavoriteBook();
}}

function getDisplayOptionEntries(question) {{
  const entries = Object.entries(question.options);
  return elements.shuffleOptions.checked
    ? Core.shuffleOptionValues(entries)
    : entries.map(([key, value]) => [key, value, key]);
}}

function renderQuestionMeta() {{
  if (!state.current) return;
  const question = state.current;
  const stats = Core.getQuestionStats(state.progress, question.id);
  const type = Core.getQuestionType(question);
  const weight = Core.getQuestionWeight(stats);
  const weightLabel = elements.weightModeFilter.value === 'uniform' ? '不加权' : `权重 ${{weight}}`;

  elements.submitAnswer.textContent = state.answered ? '下一题' : '提交';
  elements.previousQuestion.disabled = state.history.length === 0;
  elements.favoriteCurrent.classList.toggle('active', stats.favorite);
  elements.favoriteCurrent.textContent = stats.favorite ? '已收藏' : '收藏本题';
  elements.markMastered.textContent = stats.mastered ? '取消掌握' : '标记掌握';
  elements.metaRow.innerHTML = [
    `<span class="pill subject">${{Core.getSubjectLabel(question.category)}}</span>`,
    `<span class="pill type-badge">${{Core.getQuestionTypeLabel(type)}}</span>`,
    `<span class="pill">错误 ${{stats.wrongCount}} 次</span>`,
    `<span class="pill">${{weightLabel}}</span>`,
  ].join('');
}}

function renderQuestionNote() {{
  if (!state.current) {{
    state.noteRevealed = false;
    elements.questionNoteBox.classList.remove('note-revealed');
    elements.questionNote.value = '';
    elements.questionNote.disabled = true;
    elements.noteStatus.textContent = '提交答案后才能查看或修改笔记。';
    return;
  }}

  const stats = Core.getQuestionStats(state.progress, state.current.id);
  elements.questionNoteBox.classList.toggle('note-revealed', state.answered && state.noteRevealed);
  elements.questionNote.disabled = !state.answered;
  elements.questionNote.value = state.answered && state.noteRevealed ? stats.note || '' : '';
  elements.noteStatus.textContent = state.answered
    ? '双击“笔记”标题或本卡片空白处查看和修改笔记。'
    : '提交答案后才能查看或修改笔记。';
}}

function revealQuestionNote() {{
  if (!state.answered) return;
  state.noteRevealed = true;
  renderQuestionNote();
  elements.questionNote.focus();
  elements.noteStatus.textContent = '已显示当前题笔记。';
}}

function toggleOption(key) {{
  if (!state.current || state.answered) return;
  const type = Core.getQuestionType(state.current);

  if (type === 'multiple') {{
    if (state.selected.has(key)) state.selected.delete(key);
    else state.selected.add(key);
  }} else {{
    state.selected = new Set([key]);
  }}

  syncSelectedOptions();
}}

function syncSelectedOptions() {{
  [...elements.options.children].forEach((button) => {{
    button.classList.toggle('selected', state.selected.has(button.dataset.key));
  }});
}}

function reshuffleCurrentOptions() {{
  if (!state.current || state.answered) return;
  renderQuestion();
}}

function submitAnswer() {{
  if (!state.current) return;
  if (state.answered) {{
    chooseNextQuestion();
    return;
  }}

  const validation = Core.canSubmitAnswer(state.current, [...state.selected]);
  if (!validation.ok) {{
    elements.feedback.textContent = validation.message;
    elements.feedback.className = 'feedback bad';
    return;
  }}

  const selected = [...state.selected];
  const correctAnswer = state.displayCorrectAnswer.length
    ? state.displayCorrectAnswer
    : state.current.correct_answer;
  const wasCorrect = Core.isCorrectAnswer(selected, correctAnswer);
  state.progress = Core.updateProgressAfterAnswer(state.progress, state.current.id, wasCorrect);
  state.today.count += 1;
  state.answered = true;
  saveProgress();
  saveToday();

  [...elements.options.children].forEach((button) => {{
    const key = button.dataset.key;
    button.disabled = true;
    if (correctAnswer.includes(key)) button.classList.add('correct');
    if (state.selected.has(key) && !correctAnswer.includes(key)) button.classList.add('wrong');
  }});

  const correctText = Core.normalizeAnswer(correctAnswer).join('、');
  if (wasCorrect) {{
    elements.feedback.textContent = `正确。标准答案：${{correctText}}。`;
    elements.feedback.className = 'feedback good';
  }} else {{
    elements.feedback.textContent = `错误。标准答案：${{correctText}}。`;
    elements.feedback.className = 'feedback bad';
  }}

  renderQuestionMeta();
  renderQuestionNote();
  renderCurrentStats();
  renderGlobalStats();
  renderWrongBook();
  renderFavoriteBook();
}}

function renderCurrentStats() {{
  if (!state.current) return;
  const stats = Core.getQuestionStats(state.progress, state.current.id);
  const weight = Core.getQuestionWeight(stats);
  elements.currentStats.textContent = `已做 ${{stats.seenCount}} 次，答错 ${{stats.wrongCount}} 次，连续答对 ${{stats.streak}} 次。`;
  elements.currentWeightBar.style.width = `${{Math.min(100, Math.round((weight / 11) * 100))}}%`;
}}

function saveQuestionNote() {{
  if (!state.current || !state.answered || !state.noteRevealed) return;
  const id = String(state.current.id);
  const stats = Core.getQuestionStats(state.progress, id);
  state.progress = {{
    ...state.progress,
    [id]: {{
      ...stats,
      note: elements.questionNote.value,
    }},
  }};
  saveProgress();
}}

function renderGlobalStats() {{
  let seen = 0;
  let correct = 0;
  let wrongQuestions = 0;

  for (const question of questions) {{
    const stats = Core.getQuestionStats(state.progress, question.id);
    seen += stats.seenCount;
    correct += stats.correctCount;
    if (stats.wrongCount > 0) wrongQuestions += 1;
  }}

  elements.todayCount.textContent = String(state.today.count);
  elements.accuracy.textContent = seen ? `${{Math.round((correct / seen) * 100)}}%` : '0%';
  elements.wrongTotal.textContent = String(wrongQuestions);
  elements.bankTotal.textContent = String(questions.length);
}}

function getPaperCandidates() {{
  const subject = elements.paperSubjectFilter.value;
  const type = elements.paperTypeFilter.value;

  return questions.filter((question) => {{
    if (subject !== 'all' && question.category !== subject) return false;
    if (type !== 'all' && Core.getQuestionType(question) !== type) return false;
    return true;
  }});
}}

function generatePaper() {{
  const candidates = getPaperCandidates();
  if (!candidates.length) {{
    state.paperQuestions = [];
    state.paperSelections = {{}};
    state.paperSubmitted = false;
    renderPaper();
    return;
  }}

  const requestedCount = Math.max(1, Number.parseInt(elements.paperCount.value, 10) || 20);
  const count = Math.min(requestedCount, candidates.length);
  state.paperQuestions = Core.selectPaperQuestions(
    candidates,
    state.progress,
    count,
    elements.paperWeightModeFilter.value
  );
  state.paperSelections = {{}};
  state.paperSubmitted = false;
  renderPaper();
}}

function getPaperSelection(questionId) {{
  const id = String(questionId);
  if (!state.paperSelections[id]) state.paperSelections[id] = new Set();
  return state.paperSelections[id];
}}

function isPaperComplete() {{
  return state.paperQuestions.length > 0 && state.paperQuestions.every((question) => {{
    const validation = Core.canSubmitAnswer(question, [...getPaperSelection(question.id)]);
    return validation.ok;
  }});
}}

function togglePaperOption(question, key) {{
  if (state.paperSubmitted) return;
  const selection = getPaperSelection(question.id);
  const type = Core.getQuestionType(question);

  if (type === 'multiple') {{
    if (selection.has(key)) selection.delete(key);
    else selection.add(key);
  }} else {{
    selection.clear();
    selection.add(key);
  }}

  renderPaper();
}}

function renderPaper() {{
  const answeredCount = state.paperQuestions.filter((question) => {{
    return Core.canSubmitAnswer(question, [...getPaperSelection(question.id)]).ok;
  }}).length;
  const total = state.paperQuestions.length;
  const complete = isPaperComplete();

  elements.submitPaper.disabled = !complete || state.paperSubmitted;
  elements.submitPaper.textContent = state.paperSubmitted ? '已交卷' : '交卷看答案';

  if (!total) {{
    elements.paperSummary.textContent = '选择条件后生成试卷。';
    elements.paperList.innerHTML = '<p class="empty">还没有生成试卷。</p>';
    return;
  }}

  elements.paperSummary.textContent = state.paperSubmitted
    ? `已交卷，共 ${{total}} 题。`
    : `已完成 ${{answeredCount}} / ${{total}} 题，全部完成后才能看答案。`;
  elements.paperList.innerHTML = '';

  state.paperQuestions.forEach((question, index) => {{
    const row = document.createElement('section');
    row.className = 'paper-item';
    const type = Core.getQuestionType(question);
    const selection = getPaperSelection(question.id);
    const selected = [...selection];
    const correctAnswer = Core.normalizeAnswer(question.correct_answer);
    const isCorrect = state.paperSubmitted && Core.isCorrectAnswer(selected, correctAnswer);
    row.innerHTML = `
      <div class="wrong-item-meta">
        <span class="pill">${{index + 1}}</span>
        <span class="pill subject">${{Core.getSubjectLabel(question.category)}}</span>
        <span class="pill type-badge">${{Core.getQuestionTypeLabel(type)}}</span>
      </div>
      <p class="paper-question">${{question.question}}</p>
      <div class="options"></div>
    `;

    const optionWrap = row.querySelector('.options');
    Object.entries(question.options).forEach(([key, value]) => {{
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'option';
      button.dataset.key = key;
      button.disabled = state.paperSubmitted;
      button.innerHTML = `<span class="option-key">${{key}}</span><span>${{value}}</span>`;
      button.classList.toggle('selected', selection.has(key));
      if (state.paperSubmitted) {{
        if (correctAnswer.includes(key)) button.classList.add('correct');
        if (selection.has(key) && !correctAnswer.includes(key)) button.classList.add('wrong');
      }}
      button.addEventListener('click', () => togglePaperOption(question, key));
      optionWrap.appendChild(button);
    }});

    if (state.paperSubmitted) {{
      const answer = document.createElement('p');
      answer.className = `paper-answer feedback ${{isCorrect ? 'good' : 'bad'}}`;
      answer.textContent = `${{isCorrect ? '正确' : '错误'}}。标准答案：${{correctAnswer.join('、')}}。`;
      row.appendChild(answer);
    }}

    elements.paperList.appendChild(row);
  }});
}}

function submitPaper() {{
  if (state.paperSubmitted) return;
  if (!isPaperComplete()) {{
    elements.paperSummary.textContent = '还有题目没有作答完整，全部完成后才能看答案。';
    return;
  }}

  for (const question of state.paperQuestions) {{
    const selected = [...getPaperSelection(question.id)];
    const wasCorrect = Core.isCorrectAnswer(selected, question.correct_answer);
    state.progress = Core.updateProgressAfterAnswer(state.progress, question.id, wasCorrect);
    state.today.count += 1;
  }}
  state.paperSubmitted = true;
  saveProgress();
  saveToday();
  renderPaper();
  renderGlobalStats();
  renderWrongBook();
  renderFavoriteBook();
}}

function populateSeriesSelect() {{
  const allSeries = getAllSeries();
  const previousValue = elements.seriesSelect.value;
  elements.seriesSelect.innerHTML = '';
  if (!allSeries.length) {{
    const option = document.createElement('option');
    option.value = '';
    option.textContent = '没有专题数据';
    elements.seriesSelect.appendChild(option);
    elements.startSeries.disabled = true;
    return;
  }}

  elements.startSeries.disabled = false;
  allSeries.forEach((series) => {{
    const option = document.createElement('option');
    option.value = series.name;
    const label = series.custom ? `自定义：${{series.title}}` : series.name;
    option.textContent = `${{label}}（${{series.questions.length}} 题）`;
    elements.seriesSelect.appendChild(option);
  }});
  if (previousValue && allSeries.some((series) => series.name === previousValue)) {{
    elements.seriesSelect.value = previousValue;
  }}
}}

function populatePracticeSeriesSelect() {{
  const previousValue = elements.currentSeriesTarget.value;
  elements.currentSeriesTarget.innerHTML = getSeriesTargetOptions();
  if (previousValue && getAllSeries().some((series) => series.name === previousValue)) {{
    elements.currentSeriesTarget.value = previousValue;
  }}
}}

function getSelectedSeries() {{
  return getAllSeries().find((series) => series.name === elements.seriesSelect.value) || null;
}}

function getAllSeries() {{
  const builtInSeries = seriesBank.map((series) => {{
    const additions = state.seriesAdditions[series.name] || [];
    return {{
      ...series,
      questions: [...series.questions, ...additions],
    }};
  }});

  return [
    ...builtInSeries,
    ...state.customSeries.map((series) => {{
      const additions = state.seriesAdditions[series.name] || [];
      return {{
        ...series,
        questions: [...series.questions, ...additions],
      }};
    }}),
  ];
}}

function cloneQuestionForSeries(question, seriesName, index) {{
  return {{
    category: question.category,
    question: question.question,
    options: question.options,
    correct_answer: question.correct_answer || [],
    id: `${{seriesName}}-added-${{index}}`,
  }};
}}

function getSeriesTargetOptions() {{
  return getAllSeries()
    .map((series) => {{
      const label = series.custom ? `自定义：${{series.title}}` : series.name;
      return `<option value="${{series.name}}">${{label}}</option>`;
    }})
    .join('');
}}

function isSameSeriesQuestion(left, right) {{
  return left.category === right.category && left.question === right.question;
}}

function addQuestionToSeries(question, seriesName) {{
  if (!question || !seriesName) return false;
  const currentSeries = getAllSeries().find((series) => series.name === seriesName);
  if (!currentSeries || currentSeries.questions.some((item) => isSameSeriesQuestion(item, question))) {{
    return false;
  }}

  const customIndex = state.customSeries.findIndex((series) => series.name === seriesName);
  if (customIndex >= 0) {{
    const target = state.customSeries[customIndex];
    const nextQuestion = cloneQuestionForSeries(question, seriesName, target.questions.length);
    state.customSeries = state.customSeries.map((series, index) => index === customIndex
      ? {{ ...series, questions: [...series.questions, nextQuestion] }}
      : series);
  }} else {{
    const additions = state.seriesAdditions[seriesName] || [];
    state.seriesAdditions = {{
      ...state.seriesAdditions,
      [seriesName]: [
        ...additions,
        cloneQuestionForSeries(question, seriesName, currentSeries.questions.length),
      ],
    }};
  }}

  saveCustomSeries();
  saveSeriesAdditions();
  populateSeriesSelect();
  populatePracticeSeriesSelect();
  renderSeriesQuestion();
  return true;
}}

function renderQuestionOptionList(question) {{
  return Object.entries(question.options || {{}})
    .map(([key, value]) => `
      <div class="compact-option">
        <span class="compact-option-key">${{key}}</span>
        <span>${{value}}</span>
      </div>
    `)
    .join('');
}}

function renderQuestionAnswerLine(question) {{
  const answerKeys = Core.normalizeAnswer(question.correct_answer || []).join('、') || '无';
  const answerValues = Core.normalizeAnswer(question.correct_answer || [])
    .map((key) => `${{key}}. ${{question.options?.[key] || ''}}`)
    .join('；') || '无';
  return `标准答案：${{answerKeys}}。答案内容：${{answerValues}}`;
}}

function renderCustomSeriesDraft(searchResults = null) {{
  elements.customSeriesSelectedList.innerHTML = '';
  elements.seriesSearchResults.innerHTML = '';

  const selectedIds = new Set(state.customSeriesDraft.map((question) => question.id));
  const results = Array.isArray(searchResults) ? searchResults : [];
  if (results.length) {{
    results.forEach((question) => {{
      const item = document.createElement('div');
      item.className = 'wrong-item';
      const type = Core.getQuestionType(question);
      const buttonLabel = selectedIds.has(question.id) ? '已加入' : '加入';
      item.innerHTML = `
        <div class="wrong-item-meta">
          <span class="pill subject">${{Core.getSubjectLabel(question.category)}}</span>
          <span class="pill">${{Core.getQuestionTypeLabel(type)}}</span>
        </div>
        <p>${{question.question}}</p>
        <div class="compact-options">${{renderQuestionOptionList(question)}}</div>
      `;
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = buttonLabel;
      button.disabled = selectedIds.has(question.id);
      button.addEventListener('click', () => addQuestionToCustomSeries(question.id));
      item.appendChild(button);
      elements.seriesSearchResults.appendChild(item);
    }});
  }} else {{
    elements.seriesSearchResults.innerHTML = '<p class="empty">输入关键词后搜索题库。</p>';
  }}

  if (!state.customSeriesDraft.length) {{
    elements.customSeriesSelectedList.innerHTML = '<p class="empty">还没有加入题目。</p>';
  }} else {{
    state.customSeriesDraft.forEach((question, index) => {{
      const item = document.createElement('div');
      item.className = 'wrong-item';
      const type = Core.getQuestionType(question);
      item.innerHTML = `
        <div class="wrong-item-meta">
          <span class="pill">${{index + 1}}</span>
          <span class="pill subject">${{Core.getSubjectLabel(question.category)}}</span>
          <span class="pill">${{Core.getQuestionTypeLabel(type)}}</span>
        </div>
        <p>${{question.question}}</p>
        <div class="compact-options">${{renderQuestionOptionList(question)}}</div>
      `;
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = '移除';
      button.addEventListener('click', () => removeQuestionFromCustomSeries(question.id));
      item.appendChild(button);
      elements.customSeriesSelectedList.appendChild(item);
    }});
  }}

  elements.customSeriesStatus.textContent = `当前已选 ${{state.customSeriesDraft.length}} 题。`;
}}

function searchSeriesQuestions() {{
  const results = Core.searchQuestionBank(questions, elements.seriesSearchQuery.value, 30);
  renderCustomSeriesDraft(results);
  elements.customSeriesStatus.textContent = results.length
    ? `找到 ${{results.length}} 道候选题，点击加入后再保存系列。`
    : '没有匹配题目，换一个关键词。';
}}

function addQuestionToCustomSeries(questionId) {{
  const question = questions.find((item) => item.id === Number(questionId));
  if (!question) return;
  if (state.customSeriesDraft.some((item) => item.id === question.id)) {{
    renderCustomSeriesDraft(Core.searchQuestionBank(questions, elements.seriesSearchQuery.value, 30));
    return;
  }}

  state.customSeriesDraft = [...state.customSeriesDraft, question];
  renderCustomSeriesDraft(Core.searchQuestionBank(questions, elements.seriesSearchQuery.value, 30));
}}

function removeQuestionFromCustomSeries(questionId) {{
  state.customSeriesDraft = state.customSeriesDraft.filter((question) => question.id !== Number(questionId));
  renderCustomSeriesDraft(Core.searchQuestionBank(questions, elements.seriesSearchQuery.value, 30));
}}

function saveCustomSeriesDraft() {{
  const title = elements.customSeriesName.value.trim();
  if (!title) {{
    elements.customSeriesStatus.textContent = '先填写自定义系列名。';
    return;
  }}
  if (!state.customSeriesDraft.length) {{
    elements.customSeriesStatus.textContent = '至少加入一道题才能保存系列。';
    return;
  }}

  const name = `CUSTOM_${{Date.now()}}`;
  const savedSeries = {{
    name,
    title,
    custom: true,
    questions: state.customSeriesDraft.map((question, questionIndex) => ({{
      category: question.category,
      question: question.question,
      options: question.options,
      correct_answer: question.correct_answer || [],
      id: `${{name}}-${{questionIndex}}`,
    }})),
  }};

  state.customSeries = [...state.customSeries, savedSeries];
  state.customSeriesDraft = [];
  elements.customSeriesName.value = '';
  saveCustomSeries();
  populateSeriesSelect();
  populatePracticeSeriesSelect();
  elements.seriesSelect.value = name;
  state.seriesCurrent = null;
  state.seriesQuestions = [];
  renderCustomSeriesDraft();
  renderSeriesQuestion();
  elements.customSeriesStatus.textContent = `已保存自定义系列：${{title}}。`;
}}

function startSeriesReview() {{
  const series = getSelectedSeries();
  state.seriesQuestions = series ? series.questions.slice() : [];
  state.seriesCurrent = null;
  state.seriesSelected = new Set();
  state.seriesAnswered = false;
  state.seriesDisplayCorrectAnswer = [];
  chooseNextSeriesQuestion();
}}

function chooseNextSeriesQuestion() {{
  if (!state.seriesQuestions.length) {{
    state.seriesCurrent = null;
    renderSeriesQuestion();
    return;
  }}

  const usable = state.seriesQuestions.length > 1 && state.seriesCurrent
    ? state.seriesQuestions.filter((question) => question.id !== state.seriesCurrent.id)
    : state.seriesQuestions;
  state.seriesCurrent = Core.pickUniformQuestion(usable);
  state.seriesSelected = new Set();
  state.seriesAnswered = false;
  state.seriesDisplayCorrectAnswer = [];
  renderSeriesQuestion();
}}

function getSeriesDisplayOptionEntries(question) {{
  const entries = Object.entries(question.options);
  return elements.seriesShuffleOptions.checked
    ? Core.shuffleOptionValues(entries)
    : entries.map(([key, value]) => [key, value, key]);
}}

function renderSeriesQuestion() {{
  const series = getSelectedSeries();
  if (!getAllSeries().length) {{
    elements.seriesSummary.textContent = '没有专题数据。';
    elements.seriesMetaRow.innerHTML = '';
    elements.seriesQuestionText.textContent = '未找到同系列专题文件。';
    elements.seriesOptions.innerHTML = '';
    elements.seriesSubmitAnswer.disabled = true;
    elements.seriesSkipQuestion.disabled = true;
    elements.seriesFeedback.textContent = '';
    return;
  }}

  if (!state.seriesCurrent) {{
    elements.seriesSummary.textContent = series
      ? `${{series.custom ? `自定义：${{series.title}}` : series.name}}，共 ${{series.questions.length}} 题。`
      : '选择一个同系列专题开始复习。';
    elements.seriesMetaRow.innerHTML = '';
    elements.seriesQuestionText.textContent = '请选择系列后开始专题。';
    elements.seriesOptions.innerHTML = '';
    elements.seriesSubmitAnswer.disabled = true;
    elements.seriesSkipQuestion.disabled = true;
    elements.seriesFeedback.textContent = '';
    elements.seriesFeedback.className = 'feedback';
    return;
  }}

  const question = state.seriesCurrent;
  const displayEntries = getSeriesDisplayOptionEntries(question);
  state.seriesDisplayCorrectAnswer = Core.getDisplayedCorrectAnswer(displayEntries, question.correct_answer);
  const type = Core.getQuestionType(question);
  const seriesLabel = series ? (series.custom ? `自定义：${{series.title}}` : series.name) : elements.seriesSelect.value;
  elements.seriesSummary.textContent = `${{seriesLabel}}，专题复习不计入全局统计。`;
  elements.seriesMetaRow.innerHTML = [
    `<span class="pill subject">${{Core.getSubjectLabel(question.category)}}</span>`,
    `<span class="pill type-badge">${{Core.getQuestionTypeLabel(type)}}</span>`,
    `<span class="pill">${{elements.seriesShuffleOptions.checked ? '打乱内容' : '原始内容'}}</span>`,
  ].join('');
  elements.seriesQuestionText.textContent = question.question;
  elements.seriesOptions.innerHTML = '';
  elements.seriesSubmitAnswer.disabled = false;
  elements.seriesSubmitAnswer.textContent = state.seriesAnswered ? '下一题' : '提交';
  elements.seriesSkipQuestion.disabled = false;

  displayEntries.forEach(([key, value, originalKey]) => {{
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'option';
    button.dataset.key = key;
    button.dataset.originalKey = originalKey;
    button.innerHTML = `<span class="option-key">${{key}}</span><span>${{value}}</span>`;
    button.disabled = state.seriesAnswered;
    button.classList.toggle('selected', state.seriesSelected.has(key));
    if (state.seriesAnswered) {{
      if (state.seriesDisplayCorrectAnswer.includes(key)) button.classList.add('correct');
      if (state.seriesSelected.has(key) && !state.seriesDisplayCorrectAnswer.includes(key)) {{
        button.classList.add('wrong');
      }}
    }}
    button.addEventListener('click', () => toggleSeriesOption(key));
    elements.seriesOptions.appendChild(button);
  }});

  if (!state.seriesAnswered) {{
    elements.seriesFeedback.textContent = type === 'multiple' ? '多选题至少选择两个选项。' : '';
    elements.seriesFeedback.className = 'feedback';
  }}
}}

function toggleSeriesOption(key) {{
  if (!state.seriesCurrent || state.seriesAnswered) return;
  const type = Core.getQuestionType(state.seriesCurrent);
  if (type === 'multiple') {{
    if (state.seriesSelected.has(key)) state.seriesSelected.delete(key);
    else state.seriesSelected.add(key);
  }} else {{
    state.seriesSelected = new Set([key]);
  }}

  [...elements.seriesOptions.children].forEach((button) => {{
    button.classList.toggle('selected', state.seriesSelected.has(button.dataset.key));
  }});
}}

function reshuffleSeriesQuestion() {{
  if (!state.seriesCurrent || state.seriesAnswered) return;
  renderSeriesQuestion();
}}

function submitSeriesAnswer() {{
  if (!state.seriesCurrent) return;
  if (state.seriesAnswered) {{
    chooseNextSeriesQuestion();
    return;
  }}

  const validation = Core.canSubmitAnswer(state.seriesCurrent, [...state.seriesSelected]);
  if (!validation.ok) {{
    elements.seriesFeedback.textContent = validation.message;
    elements.seriesFeedback.className = 'feedback bad';
    return;
  }}

  const selected = [...state.seriesSelected];
  const correctAnswer = state.seriesDisplayCorrectAnswer.length
    ? state.seriesDisplayCorrectAnswer
    : state.seriesCurrent.correct_answer;
  const wasCorrect = Core.isCorrectAnswer(selected, correctAnswer);
  const correctText = Core.normalizeAnswer(correctAnswer).join('、');
  state.seriesAnswered = true;
  elements.seriesFeedback.textContent = `${{wasCorrect ? '正确' : '错误'}}。标准答案：${{correctText}}。`;
  elements.seriesFeedback.className = `feedback ${{wasCorrect ? 'good' : 'bad'}}`;
  renderSeriesQuestion();
}}

function renderListPager(totalItems, currentPage, statusElement, prevButton, nextButton) {{
  const totalPages = Math.max(1, Math.ceil(totalItems / LIST_PAGE_SIZE));
  statusElement.textContent = `第 ${{currentPage + 1}} / ${{totalPages}} 页`;
  prevButton.disabled = currentPage <= 0;
  nextButton.disabled = currentPage >= totalPages - 1 || totalItems === 0;
}}

function filterSearchResults(results) {{
  const subject = elements.questionSearchSubject.value;
  const type = elements.questionSearchType.value;
  return results.filter((question) => {{
    if (subject !== 'all' && question.category !== subject) return false;
    if (type !== 'all' && Core.getQuestionType(question) !== type) return false;
    return true;
  }});
}}

function renderQuestionSearchResults(results = state.questionSearchResults) {{
  const filteredResults = filterSearchResults(results);
  elements.questionSearchResults.innerHTML = '';
  if (!elements.questionSearchQuery.value.trim()) {{
    elements.questionSearchSummary.textContent = '输入题干或选项关键词后搜索题库。';
    elements.questionSearchResults.innerHTML = '<p class="empty">还没有搜索结果。</p>';
    return;
  }}

  elements.questionSearchSummary.textContent = filteredResults.length
    ? `找到 ${{filteredResults.length}} 道题，可直接加入专题。`
    : '没有匹配的题目。';

  if (!filteredResults.length) {{
    elements.questionSearchResults.innerHTML = '<p class="empty">换一个关键词，或放宽科目和题型筛选。</p>';
    return;
  }}

  filteredResults.forEach((question) => {{
    const row = document.createElement('div');
    row.className = 'wrong-item';
    const stats = Core.getQuestionStats(state.progress, question.id);
    const questionType = Core.getQuestionType(question);
    row.innerHTML = `
      <div class="wrong-item-meta">
        <span class="pill subject">${{Core.getSubjectLabel(question.category)}}</span>
        <span class="pill type-badge">${{Core.getQuestionTypeLabel(questionType)}}</span>
        <span class="pill">错误 ${{stats.wrongCount}} 次</span>
        <span class="pill">${{stats.favorite ? '已收藏' : '未收藏'}}</span>
      </div>
      <p>${{question.question}}</p>
      <div class="compact-options">${{renderQuestionOptionList(question)}}</div>
      <p class="answer-line">${{renderQuestionAnswerLine(question)}}</p>
    `;
    const practiceButton = document.createElement('button');
    practiceButton.type = 'button';
    practiceButton.textContent = '练这题';
    practiceButton.addEventListener('click', () => openQuestionFromList(question));
    row.appendChild(practiceButton);
    appendSeriesAddControls(row, question);
    elements.questionSearchResults.appendChild(row);
  }});
}}

function runQuestionSearch() {{
  state.questionSearchResults = Core.searchQuestionBank(questions, elements.questionSearchQuery.value, 80);
  renderQuestionSearchResults();
}}

function appendSeriesAddControls(row, question) {{
  const wrap = document.createElement('div');
  wrap.className = 'series-add-row';
  wrap.innerHTML = `
    <select class="series-target" aria-label="选择专题系列">
      ${{getSeriesTargetOptions()}}
    </select>
  `;
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = '加入专题';
  button.addEventListener('click', () => {{
    const seriesName = wrap.querySelector('.series-target').value;
    const added = addQuestionToSeries(question, seriesName);
    button.textContent = added ? '已加入' : '已存在';
  }});
  wrap.appendChild(button);
  row.appendChild(wrap);
}}

function renderWrongBook() {{
  const subject = elements.wrongSubjectFilter.value;
  const type = elements.wrongTypeFilter.value;
  const allWrongItems = questions
    .map((question) => ({{ question, stats: Core.getQuestionStats(state.progress, question.id) }}))
    .filter((item) => item.stats.wrongCount > 0)
    .sort((a, b) => b.stats.wrongCount - a.stats.wrongCount || a.question.id - b.question.id);

  const wrongItems = allWrongItems.filter((item) => {{
    if (subject !== 'all' && item.question.category !== subject) return false;
    if (type !== 'all' && Core.getQuestionType(item.question) !== type) return false;
    return true;
  }});

  elements.wrongBookSummary.textContent = allWrongItems.length
    ? `共 ${{allWrongItems.length}} 道错题，当前筛选显示 ${{wrongItems.length}} 道。`
    : '还没有错题。';

  if (!wrongItems.length) {{
    elements.wrongBookList.innerHTML = '<p class="empty">当前筛选下没有错题。</p>';
    state.wrongPage = 0;
    renderListPager(0, state.wrongPage, elements.wrongPageStatus, elements.wrongPrevPage, elements.wrongNextPage);
    elements.startWrongReview.disabled = true;
    return;
  }}

  const totalPages = Math.max(1, Math.ceil(wrongItems.length / LIST_PAGE_SIZE));
  state.wrongPage = Math.min(state.wrongPage, totalPages - 1);
  const start = state.wrongPage * LIST_PAGE_SIZE;
  const pageItems = wrongItems.slice(start, start + LIST_PAGE_SIZE);
  renderListPager(wrongItems.length, state.wrongPage, elements.wrongPageStatus, elements.wrongPrevPage, elements.wrongNextPage);
  elements.startWrongReview.disabled = false;
  elements.wrongBookList.innerHTML = '';
  pageItems.forEach((item) => {{
    const row = document.createElement('div');
    row.className = 'wrong-item';
    const questionType = Core.getQuestionType(item.question);
    row.innerHTML = `
      <div class="wrong-item-meta">
        <span class="pill subject">${{Core.getSubjectLabel(item.question.category)}}</span>
        <span class="pill type-badge">${{Core.getQuestionTypeLabel(questionType)}}</span>
        <span class="pill">错误 ${{item.stats.wrongCount}} 次</span>
        <span class="pill">连续答对 ${{item.stats.streak}} 次</span>
        <span class="pill">${{item.stats.mastered ? '已掌握' : '未掌握'}}</span>
      </div>
      <p>${{item.question.question}}</p>
      <div class="compact-options">${{renderQuestionOptionList(item.question)}}</div>
      <p class="answer-line">${{renderQuestionAnswerLine(item.question)}}</p>
    `;
    const practiceButton = document.createElement('button');
    practiceButton.type = 'button';
    practiceButton.textContent = '练这题';
    practiceButton.addEventListener('click', () => openQuestionFromList(item.question));
    row.appendChild(practiceButton);
    appendSeriesAddControls(row, item.question);
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'danger-button';
    button.textContent = '移出错题';
    button.addEventListener('click', () => removeWrongQuestion(item.question.id));
    row.appendChild(button);
    elements.wrongBookList.appendChild(row);
  }});
}}

function renderFavoriteBook() {{
  const subject = elements.favoriteSubjectFilter.value;
  const type = elements.favoriteTypeFilter.value;
  const allFavoriteItems = questions
    .map((question) => ({{ question, stats: Core.getQuestionStats(state.progress, question.id) }}))
    .filter((item) => item.stats.favorite)
    .sort((a, b) => b.stats.wrongCount - a.stats.wrongCount || a.question.id - b.question.id);

  const favoriteItems = allFavoriteItems.filter((item) => {{
    if (subject !== 'all' && item.question.category !== subject) return false;
    if (type !== 'all' && Core.getQuestionType(item.question) !== type) return false;
    return true;
  }});

  elements.favoriteSummary.textContent = allFavoriteItems.length
    ? `共 ${{allFavoriteItems.length}} 道收藏题，当前筛选显示 ${{favoriteItems.length}} 道。`
    : '还没有收藏题。';

  if (!favoriteItems.length) {{
    elements.favoriteList.innerHTML = '<p class="empty">当前筛选下没有收藏题。</p>';
    state.favoritePage = 0;
    renderListPager(0, state.favoritePage, elements.favoritePageStatus, elements.favoritePrevPage, elements.favoriteNextPage);
    elements.startFavoriteReview.disabled = true;
    return;
  }}

  const totalPages = Math.max(1, Math.ceil(favoriteItems.length / LIST_PAGE_SIZE));
  state.favoritePage = Math.min(state.favoritePage, totalPages - 1);
  const start = state.favoritePage * LIST_PAGE_SIZE;
  const pageItems = favoriteItems.slice(start, start + LIST_PAGE_SIZE);
  renderListPager(favoriteItems.length, state.favoritePage, elements.favoritePageStatus, elements.favoritePrevPage, elements.favoriteNextPage);
  elements.startFavoriteReview.disabled = false;
  elements.favoriteList.innerHTML = '';
  pageItems.forEach((item) => {{
    const row = document.createElement('div');
    row.className = 'wrong-item';
    const questionType = Core.getQuestionType(item.question);
    row.innerHTML = `
      <div class="wrong-item-meta">
        <span class="pill subject">${{Core.getSubjectLabel(item.question.category)}}</span>
        <span class="pill type-badge">${{Core.getQuestionTypeLabel(questionType)}}</span>
        <span class="pill">错误 ${{item.stats.wrongCount}} 次</span>
        <span class="pill">连续答对 ${{item.stats.streak}} 次</span>
        <span class="pill">${{item.stats.mastered ? '已掌握' : '未掌握'}}</span>
      </div>
      <p>${{item.question.question}}</p>
      <div class="compact-options">${{renderQuestionOptionList(item.question)}}</div>
      <p class="answer-line">${{renderQuestionAnswerLine(item.question)}}</p>
    `;
    const practiceButton = document.createElement('button');
    practiceButton.type = 'button';
    practiceButton.textContent = '练这题';
    practiceButton.addEventListener('click', () => openQuestionFromList(item.question));
    row.appendChild(practiceButton);
    appendSeriesAddControls(row, item.question);
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'danger-button';
    button.textContent = '取消收藏';
    button.addEventListener('click', () => removeFavoriteQuestion(item.question.id));
    row.appendChild(button);
    elements.favoriteList.appendChild(row);
  }});
}}

function startScopedReview(scope) {{
  elements.scopeFilter.value = scope;
  elements.subjectFilter.value = 'all';
  elements.typeFilter.value = 'all';
  switchView('practice');
  chooseNextQuestion();
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

function removeWrongQuestion(questionId) {{
  const id = String(questionId);
  const stats = Core.getQuestionStats(state.progress, id);
  state.progress = {{
    ...state.progress,
    [id]: {{
      ...stats,
      wrongCount: 0,
      streak: 0,
      mastered: false,
    }},
  }};
  saveProgress();
  renderGlobalStats();
  renderCurrentStats();
  renderQuestionMeta();
  renderWrongBook();
  renderFavoriteBook();
}}

function removeFavoriteQuestion(questionId) {{
  const id = String(questionId);
  const stats = Core.getQuestionStats(state.progress, id);
  state.progress = {{
    ...state.progress,
    [id]: {{
      ...stats,
      favorite: false,
    }},
  }};
  saveProgress();
  renderQuestionMeta();
  renderWrongBook();
  renderFavoriteBook();
}}

function openQuestionFromList(question) {{
  state.history = Core.rememberQuestion(
    state.history,
    state.current ? state.current.id : null,
    question.id
  );
  state.current = question;
  state.selected = new Set();
  state.displayCorrectAnswer = [];
  state.answered = false;
  switchView('practice');
  renderQuestion();
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

function toggleFavorite() {{
  if (!state.current) return;
  const id = String(state.current.id);
  const stats = Core.getQuestionStats(state.progress, id);
  state.progress = {{
    ...state.progress,
    [id]: {{
      ...stats,
      favorite: !stats.favorite,
    }},
  }};
  saveProgress();
  renderQuestionMeta();
  renderGlobalStats();
  renderWrongBook();
  renderFavoriteBook();
}}

function toggleMastered() {{
  if (!state.current) return;
  const id = String(state.current.id);
  const stats = Core.getQuestionStats(state.progress, id);
  state.progress = {{
    ...state.progress,
    [id]: {{
      ...stats,
      mastered: !stats.mastered,
      streak: stats.mastered ? stats.streak : Math.max(stats.streak, 2),
    }},
  }};
  saveProgress();
  renderQuestionMeta();
  renderCurrentStats();
  renderGlobalStats();
  renderWrongBook();
  renderFavoriteBook();
}}

function exportProgress() {{
  const payload = {{
    version: 2,
    exportedAt: new Date().toISOString(),
    progress: state.progress,
    today: state.today,
    customSeries: state.customSeries,
    seriesAdditions: state.seriesAdditions,
  }};
  const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'xi-mao-review-progress.json';
  link.click();
  URL.revokeObjectURL(url);
  elements.storageStatus.textContent = '已导出完整备份。';
}}

function normalizeBackupPayload(payload) {{
  if (!payload || typeof payload !== 'object') {{
    throw new Error('invalid payload');
  }}

  const progress = payload.progress && typeof payload.progress === 'object'
    ? payload.progress
    : payload;
  return {{
    progress,
    today: payload.today && typeof payload.today === 'object' ? payload.today : null,
    customSeries: Array.isArray(payload.customSeries) ? payload.customSeries : [],
    seriesAdditions: payload.seriesAdditions && typeof payload.seriesAdditions === 'object' ? payload.seriesAdditions : {{}},
  }};
}}

function mergeProgress(currentProgress, incomingProgress) {{
  const merged = {{ ...currentProgress }};
  Object.entries(incomingProgress || {{}}).forEach(([id, incomingStats]) => {{
    if (!incomingStats || typeof incomingStats !== 'object') return;
    const currentStats = Core.getQuestionStats(merged, id);
    merged[id] = {{
      ...currentStats,
      ...incomingStats,
      seenCount: Math.max(currentStats.seenCount || 0, incomingStats.seenCount || 0),
      correctCount: Math.max(currentStats.correctCount || 0, incomingStats.correctCount || 0),
      wrongCount: Math.max(currentStats.wrongCount || 0, incomingStats.wrongCount || 0),
      streak: Math.max(currentStats.streak || 0, incomingStats.streak || 0),
      mastered: Boolean(currentStats.mastered || incomingStats.mastered),
      favorite: Boolean(currentStats.favorite || incomingStats.favorite),
      note: incomingStats.note || currentStats.note || '',
      lastAnsweredAt: [currentStats.lastAnsweredAt, incomingStats.lastAnsweredAt].filter(Boolean).sort().pop() || null,
    }};
  }});
  return merged;
}}

function mergeCustomSeries(currentSeries, incomingSeries) {{
  const byName = new Map(currentSeries.map((series) => [series.name, series]));
  incomingSeries.forEach((series) => {{
    if (!series || !series.name || !Array.isArray(series.questions)) return;
    if (!byName.has(series.name)) {{
      byName.set(series.name, normalizeCustomSeries(series));
      return;
    }}
    const current = byName.get(series.name);
    const existingKeys = new Set(current.questions.map((question) => `${{question.category}}::${{question.question}}`));
    const additions = series.questions
      .filter((question) => question && question.question && !existingKeys.has(`${{question.category}}::${{question.question}}`))
      .map((question, index) => cloneQuestionForSeries(question, series.name, current.questions.length + index));
    byName.set(series.name, {{ ...current, questions: [...current.questions, ...additions] }});
  }});
  return [...byName.values()].filter(Boolean);
}}

function mergeSeriesAdditions(currentAdditions, incomingAdditions) {{
  const merged = {{ ...currentAdditions }};
  Object.entries(incomingAdditions || {{}}).forEach(([seriesName, questionsForSeries]) => {{
    if (!Array.isArray(questionsForSeries)) return;
    const currentQuestions = merged[seriesName] || [];
    const existingKeys = new Set(currentQuestions.map((question) => `${{question.category}}::${{question.question}}`));
    const additions = questionsForSeries
      .filter((question) => question && question.question && !existingKeys.has(`${{question.category}}::${{question.question}}`))
      .map((question, index) => cloneQuestionForSeries(question, seriesName, currentQuestions.length + index));
    merged[seriesName] = [...currentQuestions, ...additions];
  }});
  return merged;
}}

function applyBackup(backup, mode) {{
  state.progress = mode === 'replace'
    ? backup.progress
    : mergeProgress(state.progress, backup.progress);
  state.today = mode === 'replace' && backup.today ? backup.today : state.today;
  state.customSeries = mode === 'replace'
    ? backup.customSeries.map(normalizeCustomSeries).filter(Boolean)
    : mergeCustomSeries(state.customSeries, backup.customSeries);
  state.seriesAdditions = mode === 'replace'
    ? backup.seriesAdditions
    : mergeSeriesAdditions(state.seriesAdditions, backup.seriesAdditions);
  state.history = [];
  saveProgress();
  saveToday();
  saveCustomSeries();
  saveSeriesAdditions();
  populateSeriesSelect();
  populatePracticeSeriesSelect();
  renderCustomSeriesDraft();
  chooseNextQuestion();
}}

function importProgress(file) {{
  const reader = new FileReader();
  reader.onload = () => {{
    try {{
      const payload = JSON.parse(reader.result);
      const backup = normalizeBackupPayload(payload);
      const mode = elements.importMode.value;
      applyBackup(backup, mode);
      elements.storageStatus.textContent = mode === 'replace' ? '已覆盖导入完整备份。' : '已合并导入完整备份。';
    }} catch {{
      elements.feedback.textContent = '导入失败，文件不是有效的进度 JSON。';
      elements.feedback.className = 'feedback bad';
      elements.storageStatus.textContent = '导入失败，文件格式不正确。';
    }}
  }};
  reader.readAsText(file);
}}

function resetProgress() {{
  if (!confirm('确定清空所有刷题记录和错题本吗？')) return;
  state.progress = {{}};
  state.today = {{ date: new Date().toISOString().slice(0, 10), count: 0 }};
  state.history = [];
  saveProgress();
  saveToday();
  chooseNextQuestion();
}}

elements.subjectFilter.addEventListener('change', chooseNextQuestion);
elements.typeFilter.addEventListener('change', chooseNextQuestion);
elements.scopeFilter.addEventListener('change', chooseNextQuestion);
elements.weightModeFilter.addEventListener('change', chooseNextQuestion);
elements.shuffleOptions.addEventListener('change', reshuffleCurrentOptions);
elements.generatePaper.addEventListener('click', generatePaper);
elements.submitPaper.addEventListener('click', submitPaper);
elements.startSeries.addEventListener('click', startSeriesReview);
elements.seriesSelect.addEventListener('change', () => {{
  state.seriesCurrent = null;
  state.seriesQuestions = [];
  renderSeriesQuestion();
}});
elements.seriesShuffleOptions.addEventListener('change', reshuffleSeriesQuestion);
elements.seriesSubmitAnswer.addEventListener('click', submitSeriesAnswer);
elements.seriesSkipQuestion.addEventListener('click', chooseNextSeriesQuestion);
elements.seriesSearchButton.addEventListener('click', searchSeriesQuestions);
elements.seriesSearchQuery.addEventListener('keydown', (event) => {{
  if (event.key === 'Enter') searchSeriesQuestions();
}});
elements.saveCustomSeries.addEventListener('click', saveCustomSeriesDraft);
elements.questionSearchButton.addEventListener('click', runQuestionSearch);
elements.questionSearchQuery.addEventListener('keydown', (event) => {{
  if (event.key === 'Enter') runQuestionSearch();
}});
elements.questionSearchSubject.addEventListener('change', () => renderQuestionSearchResults());
elements.questionSearchType.addEventListener('change', () => renderQuestionSearchResults());
elements.wrongSubjectFilter.addEventListener('change', () => {{
  state.wrongPage = 0;
  renderWrongBook();
}});
elements.wrongTypeFilter.addEventListener('change', () => {{
  state.wrongPage = 0;
  renderWrongBook();
}});
elements.startWrongReview.addEventListener('click', () => startScopedReview('wrong'));
elements.wrongPrevPage.addEventListener('click', () => {{
  state.wrongPage = Math.max(0, state.wrongPage - 1);
  renderWrongBook();
}});
elements.wrongNextPage.addEventListener('click', () => {{
  state.wrongPage += 1;
  renderWrongBook();
}});
elements.favoriteSubjectFilter.addEventListener('change', () => {{
  state.favoritePage = 0;
  renderFavoriteBook();
}});
elements.favoriteTypeFilter.addEventListener('change', () => {{
  state.favoritePage = 0;
  renderFavoriteBook();
}});
elements.startFavoriteReview.addEventListener('click', () => startScopedReview('favorite'));
elements.favoritePrevPage.addEventListener('click', () => {{
  state.favoritePage = Math.max(0, state.favoritePage - 1);
  renderFavoriteBook();
}});
elements.favoriteNextPage.addEventListener('click', () => {{
  state.favoritePage += 1;
  renderFavoriteBook();
}});
elements.viewButtons.forEach((button) => {{
  button.addEventListener('click', () => switchView(button.dataset.view));
}});
elements.submitAnswer.addEventListener('click', submitAnswer);
elements.previousQuestion.addEventListener('click', showPreviousQuestion);
elements.skipQuestion.addEventListener('click', chooseNextQuestion);
elements.favoriteCurrent.addEventListener('click', toggleFavorite);
elements.markMastered.addEventListener('click', toggleMastered);
elements.questionNote.addEventListener('input', saveQuestionNote);
elements.questionNoteBox.addEventListener('dblclick', revealQuestionNote);
elements.addCurrentToSeries.addEventListener('click', () => {{
  if (!state.current) return;
  const added = addQuestionToSeries(state.current, elements.currentSeriesTarget.value);
  elements.feedback.textContent = added ? '已加入专题复习系列。' : '这道题已在该系列中。';
  elements.feedback.className = `feedback ${{added ? 'good' : 'bad'}}`;
}});
elements.exportProgress.addEventListener('click', exportProgress);
elements.importProgressButton.addEventListener('click', () => elements.importProgress.click());
elements.importProgress.addEventListener('change', (event) => {{
  const [file] = event.target.files;
  if (file) importProgress(file);
  event.target.value = '';
}});
elements.resetProgress.addEventListener('click', resetProgress);

populateSeriesSelect();
populatePracticeSeriesSelect();
renderCustomSeriesDraft();
chooseNextQuestion();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    write_question_bank_files(load_questions())
    write_series_bank_file(load_series_bank())
    OUTPUT.write_text(build_html(), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print(f"Wrote {LOCAL_BANK_JSON}")
    print(f"Wrote {LOCAL_BANK_JS}")
    print(f"Wrote {SERIES_BANK_JS}")
