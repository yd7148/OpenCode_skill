---
name: pdf-reader
description: 讀取 PDF 檔案的內容並輸出成 Markdown 摘要報告。文字型 PDF 用 PyMuPDF 直接抽取（含中文）；掃描/圖片型 PDF 自動渲染成 PNG 並以 RapidOCR 辨識；輸出以 opencc 轉為繁體中文。Use when asked to "讀取 PDF", "解析 PDF", "PDF 內容是什麼", "把 PDF 轉成文字", "提取 PDF 重點", "read this PDF", "extract PDF content", or handed a .pdf file to summarize or quote.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: pdf-content-extraction
  languages: zh-TW
---

# pdf-reader — 讀取 PDF 內容並輸出 Markdown 摘要

讀取指定的 `.pdf` 檔案，萃取每頁文字（含中文），對掃描/圖片型頁面自動做 OCR，
並把整份內容輸出成一份 Markdown 摘要報告。

## When to use

- User 要求「讀取 / 解析 / 看 PDF 內容」並提供 `.pdf` 路徑
- 需要引用 PDF 內文、整理重點、或作為後續分析（熱量、翻譯、彙整）的輸入
- 使用者提供掃描版 PDF（無文字層）也要能讀

## Prerequisites（已安裝）

| 工具 | 位置 | 用途 |
|------|------|------|
| 分析 venv | `D:\80-Opnecode\workspace\_maidate_work\venv\Scripts\python.exe` | PyMuPDF、pypdf、RapidOCR、opencc、Pillow |
| PyMuPDF 1.28+ | venv 內 | 文字層抽取 + 頁面渲染 |
| rapidocr-onnxruntime | venv 內 | 掃描頁 OCR |
| opencc-python-reimplemented | venv 內 | 簡體 → 繁體 (s2twp) |

## 使用流程

### 1. 確認路徑

先 `Test-Path` 確認 PDF 存在。若檔名含中文或空格，一律用 `-LiteralPath` / `r"..."` 處理。

### 2. 執行提取腳本

本技能資料夾內附**已驗證可跑**的提取器：

```
<skill>\extract_pdf.py
```

```powershell
$py = "D:\80-Opnecode\workspace\_maidate_work\venv\Scripts\python.exe"
& $py "<skill>\extract_pdf.py" "<pdf 路徑>" "<輸出.md>"
```

常用參數：

| 參數 | 用途 | 範例 |
|------|------|------|
| `--pages 1,3-5` | 只處理指定頁（1-based） | `--pages 1,3-8` |
| `--no-ocr` | 略過掃描頁 OCR（更快） | `--no-ocr` |
| `--dpi 200` | OCR 渲染解析度（預設 200） | `--dpi 300` |

輸出檔若不指定，預設寫在 PDF 同目錄 `<檔名>.md`。

### 3. 讀回並整理

用 Read tool 讀回產出的 `.md`，確認：

- 文字型頁面：中文是否完整、斷頁是否合理
- OCR 頁面：結構尚在即可（OCR 本身會有少量錯字，如 蘚→藓；輸出已自動轉繁體）
- 若使用者要求摘要／重點，由 AI 依 `.md` 內容另產出整理，**不要**把 Raw extract 直接當交付物

### 4. 驗證指標

- 文字型 PDF：`pages with text=N` 應接近總頁數
- 掃描 PDF：`OCR=幾頁`、報告內 `(掃描頁 OCR)` 章節有內容
- Markdown 開頭有摘要 meta（來源、頁數、時間）

## 已知限制與解法

| 問題 | 原因 | 解法 |
|------|------|------|
| 整頁空白但其實有字 | 頁面是圖片（掃描/圖表），無文字層 | 正常，會走 OCR 路徑 |
| OCR 判繁體誤轉錯字 | OCR 本身誤判 | 以結構與關鍵詞為準即可 |
| 加密 PDF 無法開啟 | 有密碼保護 | 向使用者索取密碼；PyMuPDF 支援 `fitz.open(src, password=...)` |
| 主控台 cp950 亂碼 | Windows 編碼 | 腳本開頭已 `sys.stdout.reconfigure(encoding="utf-8")` |
| 只抽到一半文字 | 兩欄式排版 | 改用 `page.get_text("blocks")` 或對該頁手動處理 |

## Deliverables checklist

- [ ] 輸出 `<檔名>.md`（UTF-8）已 Read 校對
- [ ] 掃描頁 OCR 已執行且轉為繁體
- [ ] 依需求另產出摘要/重點（非 Raw extract）
- [ ] 暫存 PNG（`_pdf_ocr_*.png`）已被腳本自動清理