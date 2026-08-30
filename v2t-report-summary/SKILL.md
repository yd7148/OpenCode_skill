---
name: v2t-report-summary
description: Summarize a per-minute video-analysis report (-3-report.md, OCR × Whisper × GitHub cross-reference) into a clean Traditional-Chinese executive summary saved as <BASE>-3-report-ver2.md. Corrects known ASR mis-hearings (雷神17=lesson17, Open call=OpenCode, …) and applies the 2x-video time-axis convention. Use when asked to "彙總分析", "重點彙總", "產出 ver2 摘要", "report-ver2", or to distill any ClassNN report in the playwright/video-analysis projects.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: report-summarization
  languages: zh-TW
---

# v2t-report-summary — 逐分鐘報告 → 重點彙總 ver2

Distill a verbose per-minute analysis report (`<BASE>-3-report.md`: 時間｜語音重點｜畫面OCR重點｜GitHub 對照)
into a compact, corrected executive summary `<BASE>-3-report-ver2.md` in the same project folder.
Reference output (template): `D:\80-Opnecode\Projects\2026_06_playwirght\Class17-2026_08_12_晚上-3-report-ver2.md`.

## When to use
- User hands you a `-3-report.md` (or a class/video name like `Class17-2026_08_12_晚上`) and asks for
  彙總分析 / 重點 / 精簡摘要 / ver2 報告.

## Prerequisites（依賴）
- **無額外 Python 套件** — 本 skill 僅需 opencode 內建檔案讀寫與 markdown 工具即可完成，
  不需安裝任何 venv / pip 套件。
- 輸入前提：來源是 `video2text` skill 產出的 `<BASE>-3-report.md`（逐分鐘報告）。
- 跨平台可用（macOS / Windows）。

## Workflow

### 1. Locate + verify source
- Source lives in the project folder next to its `-1` mp4 / `-2-keyframes.pdf`.
- **Verify it is real text first**: read magic bytes; if they are `50 4B 03 04` it is docx-as-md →
  convert with the recipe in the `video2text` skill (FILENAME RULE section,
  `_v2t_work\convert_docx_md.py`) before reading.

### 2. Read everything before writing anything
- Read the full report: metadata header (日期/YouTube ID/影片長度/影格數), the per-minute table,
  資料品質備註, GitHub 命中統計, 產出檔案 list.
- The narrative must be derived ONLY from this data — never invent repo paths; cite only paths that
  appear in the GitHub 對照 column.

### 3. Apply corrections while reading (do NOT copy noise verbatim)
- **ASR mis-hearings** (correct silently in your summary): 雷神NN→lessonNN, Open call/Opencode→OpenCode,
  Power share→PowerShell, Greema/Grimmer→Gemma, Ghfome/Ghrome→Chrome, Agy/anti gravity→Antigravity,
  POTY/pyy→.py, Fidma/Fille→Figma/File, 卡密的→commit, Rainy.mb→README.md, DHUB/EHUB/GeeHub→GitHub,
  9V特Lab→JupyterLab, 扣可能→token, Report儲存庫→repository, Jetup Rain/Janeplain→JetBrains,
  Rate→Zed, Zad/Lad/7ad File→Zed (editor; instructor runs macOS+Zed — "Finder 檔索" menu OCR confirms),
  REN→OpenRouter (transparent pricing + sign-up credit context), pastkey→Passkey,
  UVCONVINIT/VND→uv init/.venv, Eve→if, AOS/EOS/EVO→elif, 觸/Bose→True/False, 布林質→布林值,
  小魚/大魚→小於/大於, 槽狀→巢狀, jubyter/jpydr→JupyterLab, TWY→try, Reiss→raise, IPYMV→.ipynb,
  web write→webwright (MCP skill), pui→TUI, Skyloss→/skills, open call/ocal→OpenCode, 雀GPT→ChatGPT, UbEat→uv,
  壞耳迴圈→while迴圈, 行為迴圈→for迴圈, 圍圈→迴圈, 活風式→駝峰式, 中瓜號→中括號, petroliZe→capitalize,
  PlayLine/PryWrite/playlite→Playwright, columnian→屬性, 黑的類似/Black LANS→headless, 麻酒→module, WebRide→webwright.
  New classes will surface new ones — append them here after each run.
- **Hallucinations**: ad-reads on silence (「KC安全認證…產後護理之家」購物台詞), 「請不吝點贊訂閱…」,
  repeated 口頭禪 runs — exclude from analysis. Long stretches of「OK OK OK…」(seen Class04 00:50–01:01)
  = instructor walking around during student hands-on time; compress into one note like
  （MM:SS–MM:SS 為同學實作等待段，非授課內容）instead of a timeline section.
- **OCR menu-bar garbage** (檔案/編輯/顯示方式…, Ghfome, 柘泵) — ignore unless content-bearing.
- **Time axis**: report times are on the **2x-speed video**; original class time = ×2.
  State the convention in the summary ("時間軸以 2 倍速影片為準，原始課程時間 = ×2").
- Segment durations: 影片長度(2x) × 2 ≈ original class length for the header line.

### 4. Output structure (mirror the Class17 template)
1. H1 title `<BASE>重點彙總`
2. Metadata table: 日期 / YouTube URL / 影片長度(2x＋原始換算) / 主軸一句話 / 資料來源 / 產出日期
   + blockquote time-axis convention
3. Numbered H2 sections `## N. <主題>（MM:SS–MM:SS）` in chronological order — each is 3–4 bullets:
   tools/concepts taught, code artifacts produced (real file names from OCR/GitHub columns),
   instructor's workflow takeaways
4. `## 附註`: format-fix history of the batch, noise-correction note ("本彙總已校正後再引用"),
   companion deliverables (`-2-keyframes.pdf`, README)
- Length target: ~40–60 lines total. Keep bullets dense; no filler prose.

### 5. Save + verify
- Filename: exactly `<BASE>-3-report-ver2.md` (plain `.md`, UTF-8 no BOM, NEVER double extensions).
- After writing, verify first bytes are not `PK\x03\x04` and re-read the head to confirm encoding.
