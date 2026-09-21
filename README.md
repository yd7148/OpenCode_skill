# OpenCode_skill

OpenCode 本機 Skills 收藏庫。所有 skill 皆為 MIT 授權，適用於 opencode agents。

> 📖 每支 skill 的完整功能、適用時機、運作流程與產出，請參閱 **[SKILLS.md](SKILLS.md)**。

## 目錄

| Skill | 用途 | 依賴／平台 |
|-------|------|-----------|
| `comsol-analyzer` | 分析 COMSOL Multiphysics .mph 模型檔案 | 無額外依賴（`.mph` 為 ZIP，免裝 COMSOL） |
| `dwg-to-dxf` | 將 DWG 轉成 DXF 並進行幾何/圖層分析 | ODA File Converter + Python `ezdxf`（Windows） |
| `taobao-order-extract` | 從淘寶訂單 Excel 提取訂單資料並比對物流重量 | Python + `openpyxl` |
| `taobao-cost-fill` | 依訂單卡片填寫「淘寶費用計算明細」R0 樣板並存成 R1 | Python + `openpyxl` |
| `md-to-pdf` | 將繁體中文 Markdown 渲染成排版精美的 A4 PDF | Python + Pillow + 中文字體（macOS/Windows 自動偵測） |
| `v2t-report-summary` | 彙總影片分析報告（OCR × Whisper × GitHub）成繁體中文摘要 | 無（opencode 內建工具） |
| `video-2x-speed` | 倍速影片處理（時間軸慣例） | ffmpeg + `yt-dlp` |
| `video2text` | 分析錄影影片 → 雙語 Markdown 報告 + 關鍵幀 PDF | Python venv：optimum-intel、faster-whisper、rapidocr-onnxruntime 等 |
| `yt-batch-download` | 批次下載 YouTube 影片（1080p） | Python 3.13+、`yt-dlp`、`browser_cookie3`、ffmpeg、deno |
| `yt-upload` | 透過 Playwright 上傳並公開發布 YouTube 影片 | Playwright |
| `tts` | 用 edge-tts 將文字轉成繁體中文等語音檔（mp3） | Python + `edge-tts` |
| `github-skill-sync` | 同步本機 skills 與本 GitHub 收藏庫（雙向） | 無（git/rsync/ssh） |
| `webwright` | 瀏覽器 agent（code-as-action，Playwright 開 Firefox） | Python playwright + Firefox（無 API key） |
| `web-tools` | 本機網頁工具環境筆記（Crawl4AI / Webwright） | 參考用 |
| `pdf-exam-extractor` | 考題 PDF 逐題裁剪成圖 + EasyOCR 轉 Markdown | Python：pymupdf、pdfplumber、easyocr、opencv-python |
| `taipower-exam-solver` | 國營事業招考 PDF 考題、官方解答與逐步解題 | Python `pymupdf` + 台電官網解答 PDF |
| `takeout-exif-merge` | 將 Google 相簿 Takeout JSON EXIF 合併回同名媒體檔 | Python 3 + ExifTool |
| `video-class-pipeline` | 課程影片批式分析（OCR × Whisper × 關鍵幀 PDF）與裁切/2倍速 | Python venv：paddleocr（PP-OCRv5，cu129）、whisper、opencv + ffmpeg（NVENC） |
| `sd-webui-vae-fix` | 修復 A1111 檢查點/VAE「無法切換」（diffusers→LDM VAE 格式修復） | WebUI 內建 python（torch + safetensors） |
| `open-computer-use` | Open Computer Use（macOS/Linux/Windows 的開源 Computer Use MCP）安裝、設定與操作 | `open-computer-use` / `ocu` CLI（npm，macOS 14+） |
| `comsol-mcp` | 透過 opencode 操作 COMSOL 6.4（啟動規則、建模→求解→評估序列與 API 陷阱） | Python venv（mph + jpype1）+ COMSOL MCP server（Windows） |
| `comsol-linsolver-benchmark` | COMSOL 線性求解器 A/B 基準測試（MUMPS vs cuDSS vs PARDISO）：改 `.mph` 內嵌 `dmodel.xml` 求解器節點 + comsolbatch 固定預算求解 + nvidia-smi GPU 監控 | Python（zipfile）+ COMSOL 6.4 comsolbatch（Windows） |
| `comsol-gpu-env` | COMSOL 6.4 GPU/系統 CUDA 環境設定與驗證（RTX 5080 Blackwell，切換系統 CUDA 12.9.1、comsol.prefs、Computer Use GUI 操作與無 GUI 驗證） | COMSOL 6.4 + 系統 CUDA 12.9.1（Windows）；GUI 操作用 opencode Computer Use |
| `hcl-notes-forward` | HCL Notes 公布函「直接轉寄」給群組（UI 自動化：GDI 截圖 + RapidOCR + 座標點擊） | Windows：HCL Notes client + RapidOCR venv |
| `cv-job-application` | 中華電信／台積電線上履歷自動投遞（rmis.cht.com.tw 報名表填寫、附件上傳、狀態檢核、沿用保存的 Chrome 登入） | Playwright CDP + ddddocr + EasyOCR + pymupdf + fpdf2 + python-pptx（Windows） |
| `meeting-transcript-summary` | 原始時間戳會議逐字稿彙總成詳盡繁中主管會議紀錄 | 無（opencode 內建工具） |
| `pdf-reader` | 讀取 PDF（文字抽取 / 掃描 OCR）輸出繁中 Markdown 摘要 | Python venv：PyMuPDF、RapidOCR、opencc |

## 安裝

將任一 skill 資料夾複製到 `~/.config/opencode/skills/<skill-name>/`（或 `.opencode/skills/<skill-name>/`）即可使用。

各 skill 的 Python 依賴建議安裝於**各 skill 資料夾專用 venv**（`<skill>/.venv`），不會影響系統全域 Python：

```bash
cd ~/.config/opencode/skills/<skill-name>
python3 -m venv .venv
.venv/bin/pip install <所需套件>
```

> 註：repo 內容同時適用 Windows（PowerShell 5.1，`py` launcher）與 macOS。`md-to-pdf` 已內建中文字體自動偵測，macOS 使用 STHeiti、Windows 使用微軟正黑體（msjh.ttc）。

## 依賴／平台總覽

- **無依賴**：`comsol-analyzer`、`v2t-report-summary`、`meeting-transcript-summary`
- **純 Python（跨平台）**：`taobao-order-extract`（openpyxl）、`taobao-cost-fill`（openpyxl）、`md-to-pdf`（Pillow）、`tts`（edge-tts）、`taipower-exam-solver`（pymupdf）、`pdf-reader`（PyMuPDF + RapidOCR + opencc）
- **需額外系統工具**：`dwg-to-dxf`（ODA Converter）、`video-2x-speed`（ffmpeg）、`yt-batch-download`（ffmpeg + deno）、`yt-upload`（Playwright）、`takeout-exif-merge`（ExifTool）、`hcl-notes-forward`（HCL Notes client + RapidOCR，Windows）
- **需 COMSOL 環境**：`comsol-mcp`（本機 COMSOL 6.4 + COMSOL MCP server，Windows）、`comsol-linsolver-benchmark`（COMSOL 6.4 comsolbatch + nvidia-smi，Windows）、`comsol-gpu-env`（COMSOL 6.4 + 系統 CUDA 12.9.1，RTX 5080；GUI 操作用 opencode Computer Use）
- **重型機器學習（每個 skill 有專用 venv）**：`video2text`、`pdf-exam-extractor`、`video-class-pipeline`
- **需 WebUI 環境**：`sd-webui-vae-fix`（用 webui 內建 Python：torch + safetensors，抽取本機大檢查點的 VAE 並以 `/sdapi/v1` API 驗證）
- **需 npm 全域工具**：`open-computer-use`（`npm i -g open-computer-use`，macOS 14+ 需授權 Accessibility + Screen Recording）
- **瀏覽器自動化 + OCR**：`cv-job-application`（Playwright CDP + ddddocr + EasyOCR，沿用 Chromium 設定檔保存登入，Windows）