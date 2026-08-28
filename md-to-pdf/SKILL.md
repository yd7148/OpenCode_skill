---
name: md-to-pdf
description: 將繁體中文 Markdown 說明檔渲染成排版精美的 A4 多頁 PDF（標題、表格、代碼區塊、引言、頁碼），使用 Pillow + 微軟正黑體離線產生，不需網路。Use when asked to "寫一個MARKDOWN說明檔案以及PDF格式說明檔案", "把 md 轉成 PDF", "產生中文 PDF 說明檔", or to create paired .md/.pdf deliverables.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: chinese-markdown-to-pdf
  languages: zh-TW
---

# md-to-pdf — 繁中 Markdown → A4 PDF（離線 Pillow 渲染）

把一份繁體中文 `.md` 說明檔同時交付為 **Markdown + 排版 PDF** 兩個檔案。
PDF 由 Pillow 直接繪製文字（非圖片截圖、非 reportlab），中文以微軟正黑體呈現，
支援 H1/H2/H3 標題、表格（自動欄寬＋斑馬紋）、圍欄代碼區塊、引言區塊、
有序／無序清單、分隔線與頁尾頁碼。

## When to use

- User 要求「寫一個 Markdown 說明檔案，以及 PDF 格式的說明檔案」
- 需要把知識整理/配方/規格/報告輸出成可列印的中文 PDF
- 環境無法安裝 wkhtmltopdf / pandoc / LaTeX 時的純 Python 方案

## 前置需求（已就緒）

| 工具 | 路徑 | 說明 |
|------|------|------|
| 分析 venv | `D:\80-Opnecode\workspace\_maidate_work\venv\Scripts\python.exe` | 已含 Pillow |
| 中文字體 | `C:\Windows\Fonts\msjh.ttc`（細明）/ `msjhbd.ttc`（粗體） | Windows 內建 |
| 英數字體 | `C:\Windows\Fonts\consola.ttf` | 代碼區塊用 |

## 使用流程

### 1. 先寫好 Markdown 原稿（Write tool）

存到使用者指定的專案資料夾，例如 `<project>\主題名稱.md`。
語法僅需支援：`#`/`##`/`###`、段落、`- 清單`、`1. 有序`、`> 引言`、
``` 圍欄代碼區塊、`| 表格 |`、`---` 分隔線。**不要用巢狀清單或行內語法**（粗斜體不解析）。

注意：Write tool 的 content 若含特殊字元偶發 JSON 截斷錯誤 → 重試一次即可；
寫完後務必 Read 回來檢查是否有亂碼或斷句。

### 2. 複製渲染腳本並改路徑

本技能資料夾內附**已驗證可跑**的完整渲染器：

```
<skill>\make_md_pdf.py   # 來源：2026_06_playwirght\_v2t_work\make_moss_pdf.py
```

複製到工作目錄（如 `<project>\_v2t_work\make_<主題>_pdf.py`），
只改開頭兩行：

```python
SRC = r"<project>\主題名稱.md"
OUT = r"<project>\主題名稱.pdf"
```

版面常數（可不動）：A4 @144dpi `W,H = 1240,1754`；邊界 100/110px。

### 3. 執行並驗證

```powershell
& "D:\80-Opnecode\workspace\_maidate_work\venv\Scripts\python.exe" "<work>\make_<主題>_pdf.py"
# 成功輸出: PDF saved: ... (N pages)
```

**驗證（強烈建議）**：腳本會順手把第 1 頁存成 `_pdf_page1.png`，
用 RapidOCR 回讀確認中文未變亂碼、表格有渲染：

```powershell
& $py -c "from rapidocr_onnxruntime import RapidOCR; res,_ = RapidOCR()(r'<project>\_pdf_page1.png'); print(' | '.join(t for _,t,s in res if float(s)>=0.75))"
```

> OCR 本身會有辨識錯字（蘚→藓、臺→台），屬正常；只要結構與關鍵詞在即算通過。
> 驗證完刪除 `_pdf_page1.png`。

## 版面設計慣例（腳本已內建）

- 首頁頂部：H1 大標題（52pt 粗體）+ 藍色粗分隔線；H2 藍色＋左側色條＋底線
- 表格：表頭淺藍底粗體、偶數列斑馬紋、細格線、依內容自適應欄寬
- 代碼區塊：圓角淺灰底，中英混排（Consolas + 正黑體分段繪製）
- 頁尾：左側文件名、右側「N / total」，上方灰線
- 中文換行：逐字斷行（CJK 可任意斷），英數單字不切半

## 環境問題與解法

| 問題 | 原因 | 解法 |
|------|------|------|
| `UnicodeEncodeError: 'cp950' codec` | 主控台編碼 | 腳本開頭 `sys.stdout.reconfigure(encoding="utf-8")`（模板已有） |
| Write tool 寫 .md 時 JSON unterminated | 特殊字元組合偶發 | 原封重送一次；或改兩段寫入再合併 |
| PDF 打不開/0KB | venv 路徑錯或字體缺 | 確認用 maidate venv；`Test-Path C:\Windows\Fonts\msjh.ttc` |
| 內容超出頁面被切 | 單一元素高於可用高度 | 表格過長拆成多個小表；代碼區塊 ≤20 行 |
| PIL 無法重新開啟 .pdf 驗證 | Pillow 只能寫不能讀 PDF | 一律用上方的 PNG+OCR 法驗證 |

## Deliverables checklist

- [ ] `<主題>.md`（UTF-8，內容經 Read 校對）
- [ ] `<主題>.pdf`（A4 多頁，OCR 抽查通過）
- [ ] 暫存 PNG 已清理
