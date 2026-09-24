# OpenCode Skills 說明文件

本文件詳細說明本收藏庫中每支 OpenCode Skill 的功能、適用時機、運作流程與產出。
所有 skill 皆為 **MIT 授權**，適用於 **opencode agents**，作業系統為 **Windows（PowerShell 5.1）**。

> ⚠️ **預設不安裝 Skill（本台專屬）**：**`hcl-notes-forward`**（HCL Notes 公布函自動轉寄 + 信箱匯出分析／讀取加密信件）是**本台專屬電腦的 skill**，僅此台機器需要安裝。GitHub 上**預設不安裝**此 skill；其他台若要使用**必須人工指定安裝**（手動複製 `hcl-notes-forward/` 到 `~/.config/opencode/skills/`），不會隨收藏庫自動部署。詳見 §31。

---

## 目錄

| Skill | 一句話說明 |
|-------|-----------|
| [comsol-analyzer](#1-comsol-analyzer) | Analyze COMSOL Multiphysics .mph model f |
| [comsol-gpu-env](#2-comsol-gpu-env) | COMSOL 6.4 GPU/系統 CUDA 環境設定與驗證（RTX 5080 Blackwell，切換系統 CUDA 12.9.1） |
| [comsol-linsolver-benchmark](#3-comsol-linsolver-benchmark) | A/B benchmark a COMSOL Multiphysics mode |
| [comsol-mcp](#4-comsol-mcp) | Drive COMSOL Multiphysics 6.4 on this ma |
| [cv-job-application](#5-cv-job-application) | Use when 投遞或填寫 中華電信/台積電 線上履歷、要操作 rmis.ch |
| [dwg-to-dxf](#6-dwg-to-dxf) | Convert AutoCAD DWG files to DXF format  |
| [github-skill-sync](#7-github-skill-sync) | 同步本機 OpenCode skills（~/.config/opencode/ |
| [md-to-pdf](#8-md-to-pdf) | 將繁體中文 Markdown 說明檔渲染成排版精美的 A4 多頁 PDF（標題、 |
| [meeting-transcript-summary](#9-meeting-transcript-summary) | 將一場會議的「原始時間戳逐字稿」（*_timestamp.txt，語音辨識輸出） |
| [open-computer-use](#10-open-computer-use) | Platform-neutral guidance for using Open |
| [pdf-exam-extractor](#11-pdf-exam-extractor) | Use when the user asks to extract indivi |
| [pdf-reader](#12-pdf-reader) | 讀取 PDF 檔案的內容並輸出成 Markdown 摘要報告。文字型 PDF 用 |
| [sd-webui-vae-fix](#13-sd-webui-vae-fix) | 修復 AUTOMATIC1111 Stable Diffusion WebUI（ |
| [taipower-exam-solver](#14-taipower-exam-solver) | Use when the user asks to process 國營事業招考 |
| [takeout-exif-merge](#15-takeout-exif-merge) | Use when the user asks to merge Google P |
| [taobao-cost-fill](#16-taobao-cost-fill) | 將「淘寶費用計算明細」Excel（*-taobao-淘寶-R0.xlsx）依訂單 |
| [taobao-order-extract](#17-taobao-order-extract) | 從淘寶導出的「訂單數據.xlsx」Excel 檔案提取訂單資料（商品名稱、實付金 |
| [tts](#18-tts) | 使用 Microsoft Edge 的 edge-tts 將文字轉成高品質語音（ |
| [v2t-report-summary](#19-v2t-report-summary) | Summarize a per-minute video-analysis re |
| [video-2x-speed](#20-video-2x-speed) | Convert a recorded video to 200% playbac |
| [video-class-pipeline](#21-video-class-pipeline) | Use when the user asks to analyze/proces |
| [video2text](#22-video2text) | Analyze recorded meeting / online-confer |
| [web-tools](#23-web-tools) | 紀錄本機 web 工具環境（Crawl4AI 爬蟲、Webwright 瀏覽器  |
| [webwright](#24-webwright) | Solve a user-specified web task code-as- |
| [yt-batch-download](#25-yt-batch-download) | 批次下載 YouTube 影片（1080p 最高畫質），支援自訂檔名、cooki |
| [yt-upload](#26-yt-upload) | 透過 Playwright 操作 YouTube Studio，將本機影片上傳並 |
| [mate-engine-anim-patch](#27-mate-engine-anim-patch) | 擴充已編譯 Unity 的 Mate Engine X 動作數量（改寫 DLL 內 |
| [browser-control](#28-browser-control) | Drive the user's existing Chromium-family browser with determin |
| [taipower-exam-report](#29-taipower-exam-report) | 台電/國營事業考題整份詳細解答（VLM 元件抽取 + SPICE + 官方答案） |
| [mate-engine](#30-mate-engine) | Mate Engine（免費輕量桌面寵物）資訊與檔案下載（https://github.com/shinyflvre/Mate-Engine） |
| [hcl-notes-forward](#31-hcl-notes-forward) ⚠️預設不安裝 | HCL Notes 公布函自動轉寄＋信箱匯出分析／讀取加密信件（僅限本台專屬電腦） |
| [opencode-session-auto-name](#32-opencode-session-auto-name) | 讓 opencode session 標題自動以「第一個 prompt 的總結」命名（plugin 已裝全域、0 Token） |

---

## 1. comsol-analyzer

**名稱**：comsol-analyzer — COMSOL .mph 模型檔案分析

**用途**：Analyze COMSOL Multiphysics .mph model files by extracting and parsing their internal XML/JSON structure. Produces a detailed Traditional Chinese markdown report covering model metadata, parameters, physics interfaces, geometry, materials, studies, and mesh. Use when asked to "分析 COMSOL 模型", "說明 .mph 檔案", "COMSOL 模型結構", "comsol model analysis", or to examine a .mph file.

**摘要**：
- - User says 分析 COMSOL 模型 / 說明 .mph 檔案 / COMSOL 模型結構 / comsol model analysis, or hands you a `.mph` file to document.
- - Also use when the user asks about the physics, geometry, materials, or studies defined in a COMSOL model.
- - **No COMSOL installation required** — the `.mph` file is a standard ZIP archive.
- - **無額外 Python 套件（無依賴）** — 只需標準程式庫 `zipfile` / `xml.etree` / `json`，macOS 與 Windows 內建 Python 3 皆可用。
- - Windows: PowerShell 5.1（內建）。macOS: 任一 Python 3 + `unzip`（內建）。
- - Working temp directory: 任一支暫存目錄（如 `/var/folders/.../tmp` 或 `C:\Users\...\AppData\Local\Temp\opencode`）

---

## 2. comsol-gpu-env

**名稱**：comsol-gpu-env — COMSOL 6.4 GPU / 系統 CUDA 環境設定與驗證

**用途**：COMSOL Multiphysics 6.4 的 GPU/系統 CUDA 環境設定與驗證（RTX 5080 Blackwell）。涵蓋切換到系統 CUDA 12.9.1 的版本限制（官方僅支援至 CUDA 12、cuDSS 0.7.1 只能用 bundled）、comsol.prefs 關鍵參數、以 opencode Computer Use 操作 COMSOL「偏好設定→計算中→GPU 加速」GUI 的 a11y 心得（tree item 用 app_post、對話框按 Return、element index 重開即重置、checkbox 狀態不可見），以及 nvidia-smi/deviceQuery129/bandwidthTest/rtcheck 無 GUI 驗證法與產生 Phase15 報告。Use when asked to "切換 COMSOL CUDA", "COMSOL GPU 加速", "驗證 CUDA 安裝", "cuDSS", "RTX 5080", "COMSOL 計算中 GPU 設定", or to setup/verify COMSOL GPU acceleration environment.

**摘要**：
- 官方版本限制：COMSOL 6.4 支援到 **CUDA 12**（12.4~12.9.x），**不可用 CUDA 13.x**；搭配 12.9.1 需 driver ≥ 576.57（本機 610.88）。
- 為何切系統 CUDA：bundled CUDA 12.4.x 不帶 Blackwell `sm_120` 原生支援 → RTX 5080（CC 12.0）只會報 compute capability error（0）。
- cuDSS 僅能用 COMSOL bundled 0.7.1（`ext\cudss\win64\cudss64_0.dll`）；系統 cuDSS root 留空；**永不覆蓋** bundled lib。
- `comsol.prefs` 終態：`gpu.settings.usecudaroot=on`、`cudaroot=<CUDA\v12.9>`、`usecudssroot=off`、`cudssroot=`（空）、`traindnnongpu=off`。
- Computer Use a11y：tree item 改用 `click_method:"app_post"`；對話框 OK 改按 **Return**；element index 每次重開即重置；成功訊號 = 「已找到一個相容的 CUDA 安裝」。
- 無 GUI 驗證：`nvidia-smi`、`deviceQuery129`（Detected 1 device，CC 12.0）、`bandwidthTest`（D2D PASS）、`rtcheck`（PASS，cudaRuntimeGetVersion=12.9）。
- 產出：`<專案根>\PhaseNN_COMSOL_6.4_GPU_Environment_Report.md`（Summary / Field Values / Verification Evidence / Final Status）。

---

## 3. comsol-linsolver-benchmark

**名稱**：comsol-linsolver-benchmark — COMSOL 線性求解器 A/B 基準測試（MUMPS vs cuDSS）

**用途**：A/B benchmark a COMSOL Multiphysics model's linear solver (MUMPS CPU vs cuDSS GPU vs PARDISO) by directly patching the solver node inside the .mph package's embedded dmodel.xml, then running comsolbatch with a fixed time budget while sampling nvidia-smi. Covers the root cause of "cuDSS never actually used" (solver set on a DISABLED node vs the ACTIVE node referenced by the Fully Coupled solver), the verified patch procedure, the 20-minute benchmark protocol, GPU-utilization monitoring, and the measured FCFC Coil results (cuDSS = 2.5x simulation-time progress). Use when asked to "比較 MUMPS 與 cuDSS", "cuDSS GPU 求解", "GPU 求解器基準測試", "改 mph 內嵌求解器", "linsolver patch", or to benchmark/verify which linear solver a COMSOL model really uses.

**摘要**：
- **COMSOL solver 設定藏在 `.mph` 內建的 `dmodel.xml`，而且設定在「停用的節點」= 沒有效果。**
- - `.mph` 是 ZIP，內含 `dmodel.xml`（通常 5–8 MB）、`smodel.json`、`mesh1.mphbin`、
- 一堆 `solutionblock*.mphbin`（可能幾十 MB 到幾百 MB）等。
- - 求解樹結構範例（`sol1` / Time solver `t1`）：
- - `t1`（Time solver）底下有許多 Feature：`dDef`、`d1`..`d4`（Direct）、
- `iDef`/`i1`..（Iterative）、`se1`（Segregated）、`ss1`..（SegregatedStep）、

---

## 4. comsol-mcp

**名稱**：comsol-mcp — 透過 opencode 操作 COMSOL 6.4

**用途**：Drive COMSOL Multiphysics 6.4 on this machine through the opencode COMSOL MCP server (wjc9011/COMSOL_Multiphysics_MCP, local fork yd7148). Covers the required launcher startup, the verified tool sequence (model -> component -> geometry -> physics -> mesh -> study -> solve -> evaluate), and the client-API gotchas discovered in testing (physics needs a geometry tag, full study step names, HeatTransfer ASHRAE limitation). Use when asked to "用 COMSOL 建模", "跑 COMSOL 仿真", "使用 comsol MCP", or to operate COMSOL via opencode MCP tools.

**摘要**：
- **Never start the server as `python -m src.server`.** JPype's in-process JVM
- startup hangs indefinitely when anyio/FastMCP worker threads are already
- running when `jpype.startJVM` is called (observed: >10 min, CPU ~0).
- `launcher.py` (repo root) pre-starts the COMSOL client on the main thread
- before `mcp.run()`, making startup ~instant. Configured automatically in
- `opencode.jsonc` (command `-m launcher`, env `COMSOL_MCP_CORES=4`). If the

---

## 5. cv-job-application

**名稱**：cv-job-application — 履歷投遞（中華電信 / 台積電）

**用途**：Use when 投遞或填寫 中華電信/台積電 線上履歷、要操作 rmis.cht.com.tw 報名表（自動填表、附件上傳、狀態檢核）、要沿用已保存的 Chrome 登入資訊（.pw-profile）登入、需要把台積電人事資料表 PDF 去識別化改成中華電信版、或要整理 E:\01-Project\2026-09-CV 履歷專案（01-原始資料 / 02-TSMC / 03-中華電信）。Covers Playwright CDP 持久化登入、圖形驗證碼 OCR + Outlook OTP、欄位 Big5 byte 上限、附件格式限制、掃描頁影像去識別化。

**摘要**：
- 專案根目錄：`E:\01-Project\2026-09-CV\`（**三個資料夾，勿再新增同層檔案**）
- | 資料夾 | 用途 | 內容 |
- |--------|------|------|
- | `01-原始資料/` | **主要資料** — 所有履歷原始檔 | 7 個原始附件（保留系統檔頭檔名 `736180_<hash>_0601-劉士禎-NN-...`），**只讀不改** |
- | `02-TSMC/` | **台積電使用** — 上傳／下載檔 + Markdown 說明 | 同批附件改乾淨檔名（`0601-劉士禎-NN-...`）+ `TSMC_Career_Profile.md` |
- | `03-中華電信/` | **中華電信使用** — 自動化程式與產出 | `.pw-profile/`（登入資訊）、`out/`（產出）、`dumps/`、`*.py`、`中華電信履歷填寫紀錄.md`、`README.md` |

---

## 6. dwg-to-dxf

**名稱**：dwg-to-dxf — DWG 轉 DXF 與詳細解析

**用途**：Convert AutoCAD DWG files to DXF format using ODA File Converter, then perform detailed geometric and metadata analysis using Python ezdxf library. Produces a comprehensive Traditional Chinese markdown report covering layers, entities, dimensions, geometry, blocks, hatches, and text content. Use when asked to "轉換 DWG", "DWG 轉 DXF", "分析 DWG 檔案", "dwg to dxf conversion", "DWG 幾何分析", or to examine a .dwg/.dxf engineering drawing file.

**摘要**：
- - User says 轉換 DWG / DWG 轉 DXF / 分析 DWG 檔案 / dwg to dxf conversion / DWG 幾何分析, or hands you a `.dwg` file to analyze.
- - Also use when the user asks about layers, dimensions, geometry, blocks, or any content in an AutoCAD drawing file.
- - **ODA File Converter** — installed at `C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe`
- - If not installed, download from: https://www.opendesign.com/guestfiles/oda_file_converter
- - Windows MSI: `ODAFileConverter_QT6_vc16_amd64dll_27.1.msi`
- - Install silently: `msiexec /i "<path>.msi" /qn`

---

## 7. github-skill-sync

**名稱**：github-skill-sync — 本機 ↔ GitHub Skills 同步

**用途**：同步本機 OpenCode skills（~/.config/opencode/skills/）與 GitHub 上的 OpenCode_skill 收藏庫（yd7148/OpenCode_skill），支援下載（GitHub→本機）與上傳（本機→GitHub）兩個方向。處理排除規則（.venv、__pycache__）、空目錄、commit 與 SSH push，並同步 GitHub 根目錄的 README.md / SKILLS.md 到地端。Use when asked to "同步 skill", "更新 skill 收藏庫", "sync skills", "上傳本機 skill 到 GitHub", "從 GitHub 拉下 skills", or to keep local skills in sync with the OpenCode_skill repo.

**摘要**：
- | 項目 | 路徑 |
- |------|------|
- | 本機 skills 目錄 | `D:\80-Opnecode\.opencode\skills\`（Windows；本次同步的集合） |
- | GitHub repo 本機 clone | `C:\Users\N000149839\OpenCode_skill` |
- | GitHub 遠端 | `https://github.com/yd7148/OpenCode_skill.git`（HTTPS；`gh auth` token / credential manager，**非 SSH**） |
- | 共用說明文件 | `README.md`、`SKILLS.md`（repo 根目錄） |

---

## 8. md-to-pdf

**名稱**：md-to-pdf — 繁中 Markdown → A4 PDF（離線 Pillow 渲染）

**用途**：將繁體中文 Markdown 說明檔渲染成排版精美的 A4 多頁 PDF（標題、表格、代碼區塊、引言、頁碼），使用 Pillow + 微軟正黑體離線產生，不需網路。Use when asked to "寫一個MARKDOWN說明檔案以及PDF格式說明檔案", "把 md 轉成 PDF", "產生中文 PDF 說明檔", or to create paired .md/.pdf deliverables.

**摘要**：
- - User 要求「寫一個 Markdown 說明檔案，以及 PDF 格式的說明檔案」
- - 需要把知識整理/配方/規格/報告輸出成可列印的中文 PDF
- - 環境無法安裝 wkhtmltopdf / pandoc / LaTeX 時的純 Python 方案
- | 工具 | 路徑 | 說明 |
- |------|------|------|
- | Python 3 | venv 或系統 python | 需含 Pillow |

---

## 9. meeting-transcript-summary

**名稱**：meeting-transcript-summary — 原始時間戳會議逐字稿 → 詳盡繁中會議彙總

**用途**：將一場會議的「原始時間戳逐字稿」（*_timestamp.txt，語音辨識輸出）彙總成詳盡繁體中文主管會議紀錄摘要（含各主管問題、部屬答覆、目標與代辦事項），存成 <BASE>_會議彙總.md。Use when asked to "彙總會議紀錄", "會議逐字稿重點", "條列各主管問題與部屬答覆", "指示須完成目標與代辦事項", or handed a *_timestamp.txt file to summarize into a supervisor meeting-minutes deliverable.

**摘要**：
- - User 給你一個 `*_timestamp.txt`（或任一語音辨識逐字稿），要求「彙總會議紀錄」
- - 要求「詳細彙總、條列各主管問題與部屬答覆、指示須完成目標與代辦事項」
- - 需要把長達數小時的半導體／製造業／任何專業會議逐字稿，濃縮成可讀的會議紀錄
- 1. **完整讀完才動筆**：`read` 用 offset 分頁讀完整個檔案；不要只讀開頭。
- 2. **語音辨識會誤聽**：以專業上下文研判「更正常見誤聽詞」，**在摘要中直接改正**，
- 不照抄雜訊。彙總開頭以引言區塊列出已更正之對照表。

---

## 10. open-computer-use

**名稱**：Open Computer Use

**用途**：Platform-neutral guidance for using Open Computer Use, the open-source Computer Use MCP server and CLI for macOS, Linux, and Windows. Use when an agent needs to install, verify, troubleshoot, configure, or operate Open Computer Use through its native CLI, stdio MCP server, or direct Computer Use tool calls.

**摘要**：
- Open Computer Use exposes Computer Use as a local CLI and stdio MCP server. It is not Codex.app-specific; adapt the commands and MCP config to the agent runtime you are operating in.
- The macOS runtime requires macOS 14.0 or later. Windows and Linux use their own platform runtimes and are not subject to this macOS minimum.
- It supports the same core tool surface across macOS, Linux, and Windows:
- `list_apps`, `get_app_state`, `click`, `perform_secondary_action`, `scroll`,
- `drag`, `type_text`, `press_key`, and `set_value`.
- 1. On macOS, run `sw_vers -productVersion` before invoking the CLI and require macOS 14.0 or later. On older versions, explain that the runtime cannot launch; do not recommend `doctor` or permission changes as a fix for binary incompatibility.

---

## 11. pdf-exam-extractor

**名稱**：PDF Exam Extractor (考題PDF擷取與OCR)

**用途**：Use when the user asks to extract individual questions from exam PDF files (考題PDF), perform OCR on each question, crop questions into separate images, or process 國營事業招考 (state-owned enterprise exam) papers. Covers PDF-to-image conversion, text position extraction with pdfplumber, question boundary detection, image cropping, and EasyOCR recognition.

**摘要**：
- ```python
- import pdfplumber
- def extract_text_with_positions(pdf_path):
- """Extract text and bounding boxes from PDF"""
- all_texts = []
- with pdfplumber.open(pdf_path) as pdf:

---

## 12. pdf-reader

**名稱**：pdf-reader — 讀取 PDF 內容並輸出 Markdown 摘要

**用途**：讀取 PDF 檔案的內容並輸出成 Markdown 摘要報告。文字型 PDF 用 PyMuPDF 直接抽取（含中文）；掃描/圖片型 PDF 自動渲染成 PNG 並以 RapidOCR 辨識；輸出以 opencc 轉為繁體中文。Use when asked to "讀取 PDF", "解析 PDF", "PDF 內容是什麼", "把 PDF 轉成文字", "提取 PDF 重點", "read this PDF", "extract PDF content", or handed a .pdf file to summarize or quote.

**摘要**：
- - User 要求「讀取 / 解析 / 看 PDF 內容」並提供 `.pdf` 路徑
- - 需要引用 PDF 內文、整理重點、或作為後續分析（熱量、翻譯、彙整）的輸入
- - 使用者提供掃描版 PDF（無文字層）也要能讀
- | 工具 | 位置 | 用途 |
- |------|------|------|
- | 分析 venv | `D:\80-Opnecode\workspace\_maidate_work\venv\Scripts\python.exe` | PyMuPDF、pypdf、RapidOCR、opencc、Pillow |

---

## 13. sd-webui-vae-fix

**名稱**：sd-webui-vae-fix — A1111 檢查點／VAE 切換失敗修復

**用途**：修復 AUTOMATIC1111 Stable Diffusion WebUI（A1111 / sd.webui）「無法切換」檢查點或 VAE 的錯誤（sd_model_checkpoint / sd_vae 選擇失敗）。覆蓋兩種根因：(1) VAE 檔是 diffusers 格式；(2) 完整檢查點（6~7GB，例如 sd_xl_base_1.0_0.9vae.safetensors）誤放 models\VAE 被當成 VAE 選取，log 出現 Missing/Unexpected key(s) 或 AutoencoderKLInferenceWrapper。診斷 VAE 檔格式、從完整檢查點抽取正確 VAE 並移動檢查點、用 run.bat 正確重啟（CWD/環境變數陷阱）、以 /sdapi 或免 --api 的 in-process 方式驗證。Use when asked to 修復 無法切換 / checkpoint 切換失敗 / VAE 切換失敗 / VAE format / Missing key(s) / Unexpected key(s) / AutoencoderKL / sd_vae / sd_model_checkpoint / AutoencoderKLInferenceWrapper。

**摘要**：
- - 網頁頂部出現 toast「無法切換 <名稱>」或英文同義訊息。
- - VAE 下拉選了某 VAE，或 `sd_model_checkpoint` 切不過去。
- - **VAE 下拉出現一顆「看起來像檢查點」的項目**（例如 `sd_xl_base_1.0_0.9vae.safetensors`，檔名像 VAE 但其實 6~7GB）。
- - WebUI log / console 出現類似：
- changing setting sd_vae to xxx.safetensors: RuntimeError
- Error(s) in loading state_dict for AutoencoderKL:

---

## 14. taipower-exam-solver

**名稱**：Taipower Exam Solver

**用途**：Use when the user asks to process 國營事業招考 (state-owned enterprise exam) PDF files from 台電/中油/台水/台糖, extract questions with pymupdf, solve exam problems (電路學, 電子學, 基本電學, etc.), search for official answer keys from taipower.com.tw, or generate detailed step-by-step solutions for exam papers. Covers PDF text/image extraction, web scraping of answer PDFs, and circuit/electronics problem solving.

**摘要**：
- test-pdf/
- {year}/
- {subject}/
- 提取結果_v4/          # OCR output directory
- q01.md              # Per-question OCR text
- q01.png             # Per-question cropped image

---

## 15. takeout-exif-merge

**名稱**：Google Photos Takeout EXIF Merge

**用途**：Use when the user asks to merge Google Photos Takeout supplemental-metadata.json sidecar files into the same-named image/video files (寫入JSON EXIF到同名影片圖片), process a Takeout Google 相簿 folder, or generate EXIF合併成果報告 style reports. Covers JSON<->media filename pairing (including (N) counter files), content-type vs extension mismatch handling, parallel exiftool -stay_open in-place writes, mtime/EXIF verification, and Markdown summary reports.

**摘要**：
- - **JSON naming**: `foo.jpg.supplemental-metadata.json` ↔ media `foo.jpg`; `foo.jpg.supplemental-metadata(1).json` ↔ `foo(1).jpg` (also form B: `foo(1).jpg.supplemental-metadata.json`).
- - **JSON keys**: `photoTakenTime`/`creationTime` (`timestamp` = UTC epoch string), `geoData{latitude,longitude,altitude}`, `title`, `description`, `people[].name`, `favorited`.
- - **Content ≠ extension** (Google re-encodes but keeps original names): `.heic/.png/.arw/.dng` files whose content is real **JPEG**, and `.mts/.avi` files whose content is real **MOV**. ExifTool REFUSES writes when extension ≠ content. Detect magic bytes (`FF D8 FF`=jpeg, `ftyp` brand) and write via a temp copy with the correct extension, then `os.replace` back.
- - **Structurally damaged files** (Truncated SubIFD / Bad SubIFD format / Truncated mdat / BMP): exiftool refuses to rewrite (it protects the file). Fallback: set file mtime via `os.utime` so at least the timestamp is right.
- - **Environment gotchas**: PowerShell console mangles Chinese (CP950) — set `PYTHONIOENCODING=utf-8` / `sys.stdout.reconfigure(encoding='utf-8')`; `Set-Content` writes UTF-8 BOM (strip it when reading back retry lists).
- - ~1 file/sec/worker throughput; 8 workers ≈ 55 min for ~315k files (plus ~18 min JSON tag-build). Use `-stay_open True -@ -` for writes; sync per-file with the stdout status line.

---

## 16. taobao-cost-fill

**名稱**：taobao-cost-fill — 淘寶費用計算明細填寫

**用途**：將「淘寶費用計算明細」Excel（*-taobao-淘寶-R0.xlsx）依訂單卡片資料依序填入商品名稱（項目）、實付金額（單價RMB）、重量並另存成 *-R1.xlsx。Use when asked to "填寫費用明細", "費用計算明細填寫", "填入訂單資料", "填 R0 存 R1", "淘寶費用明細", "將訂單卡片填入 Excel", or to fill the 淘寶費用計算明細 template with order cards.

**摘要**：
- 把依序編號的訂單卡片（含商品名稱、實付金額、物流、重量）填入既有的「淘寶費用計算明細」Excel 樣板（`*-taobao-淘寶-R0.xlsx`），依序寫入商品列，並另存成 `*-taobao-淘寶-R1.xlsx`。
- - Python 3 + openpyxl，安裝於本 skill 專用 venv：
- ```bash
- cd <skill>/taobao-cost-fill
- python3 -m venv .venv
- .venv/bin/pip install openpyxl

---

## 17. taobao-order-extract

**名稱**：淘寶訂單資料提取與整理

**用途**：從淘寶導出的「訂單數據.xlsx」Excel 檔案提取訂單資料（商品名稱、實付金額、物流公司與單號），並依據一份物流重量清單比對補上各物流單號對應的重量，依序輸出成每筆訂單的 markdown 段落並可存檔成 .md 檔。Use when asked to "整理訂單", "訂單數據提取", "淘寶訂單整理", "訂單資料匯總", or to parse the 訂單數據.xlsx file into numbered order cards.

**摘要**：
- 將淘寶匯出的訂單 Excel（`訂單數據.xlsx`）整理成依序編號的 markdown 訂單卡片，每個卡片包含商品名稱、實付金額、物流公司與單號，並比對物流重量清單補上對應重量。
- 1. **訂單 Excel**：`訂單數據.xlsx`（sheet 名稱通常為「訂單數據」，含表頭）
- 2. **物流重量清單**（選用）：純文字/表格，格式為「物流單號 + 目的地（台灣）+ 重量」，例如 `79027852606958 台灣 1.260`
- - **Python 3 + openpyxl**，安裝於本 skill 專用 venv：
- ```bash
- cd <skill>/taobao-order-extract

---

## 18. tts

**名稱**：tts — 文字轉語音（edge-tts）

**用途**：使用 Microsoft Edge 的 edge-tts 將文字轉成高品質語音（Text-to-Speech），支援繁體中文、簡體中文、粵語與多國語言與多種聲音。可將文字轉成 mp3 語音檔，並可調整速率、音量、音調，亦可輸出字幕（WordBoundary/subtitle）。Use when asked to "文字轉語音", "TTS", "產出語音檔", "文字變成聲音", "text to speech", "生成旁白", "voiceover 音檔", or to convert text into spoken audio.

**摘要**：
- - 使用者要求「文字轉語音」、「TTS」、「產出語音檔」、「把這段文字變成聲音」
- - 需要影片旁白 / voiceover 的語音音檔
- - 需要朗讀文稿、電子報、字幕的語音版本
- - **Python 3**（本機用 `py` launcher）：`py -3 -m pip install edge-tts`
- - **網路連線**：edge-tts 呼叫微軟雲端服務 `speech.platform.bing.com`
- - **需要走 Proxy**（本機環境）：呼叫時**務必**帶 `--proxy $env:HTTPS_PROXY`，否則 `getaddrinfo failed`（DNS 無法解析）

---

## 19. v2t-report-summary

**名稱**：v2t-report-summary — 逐分鐘報告 → 重點彙總 ver2

**用途**：Summarize a per-minute video-analysis report (-3-report.md, OCR × Whisper × GitHub cross-reference) into a clean Traditional-Chinese executive summary saved as <BASE>-3-report-ver2.md. Corrects known ASR mis-hearings (雷神17=lesson17, Open call=OpenCode, …) and applies the 2x-video time-axis convention. Use when asked to "彙總分析", "重點彙總", "產出 ver2 摘要", "report-ver2", or to distill any ClassNN report in the playwright/video-analysis projects.

**摘要**：
- - User hands you a `-3-report.md` (or a class/video name like `Class17-2026_08_12_晚上`) and asks for
- 彙總分析 / 重點 / 精簡摘要 / ver2 報告.
- - **無額外 Python 套件** — 本 skill 僅需 opencode 內建檔案讀寫與 markdown 工具即可完成，
- 不需安裝任何 venv / pip 套件。
- - 輸入前提：來源是 `video2text` skill 產出的 `<BASE>-3-report.md`（逐分鐘報告）。
- - 跨平台可用（macOS / Windows）。

---

## 20. video-2x-speed

**名稱**：video-2x-speed — 影片加速（ffmpeg 200% 速度轉檔）

**用途**：Convert a recorded video to 200% playback speed (or arbitrary 0.5x–100x) with ffmpeg, keeping the same resolution and fps, using Intel GPU (h264_qsv) and audio via atempo. Also supports cropping dead black bands (e.g. lecture captures: keep left white content, drop right black area) combined with the speed change in one pass. Encodes the correct speed without the classic `-t`-placement pitfall that silently produces a non-sped file. Use when asked to "加速影片", "轉成2倍速", "200% 播放速度", "倍速播放", "speed up video", "裁切黑邊", "切除黑色部分", or to produce a 2x/cropped copy of a downloaded .mp4.

**摘要**：
- - User asks 加速影片 / 轉成 2 倍速 / 200% 播放速度 / 倍速播放 / speed up a video.
- - Video is already downloaded (yt-dlp output, or any local .mp4). For standard downloads see the `video2text` skill.
- - **HLS fallback download**: When yt-dlp fails to download (proxy blocks m3u8), use the Python method below.
- Fortinet 代理會封鎖 googlevideo.com 的 m3u8/HLS 串流（403 Forbidden），導致 yt-dlp + ffmpeg
- 無法下載。解法：用 Python `urllib` 自行下載 m3u8 播放清單與分段，再用 ffmpeg 合併。
- ```powershell

---

## 21. video-class-pipeline

**名稱**：Video Class Pipeline (課程影片分析與轉檔)

**用途**：Use when the user asks to analyze/process 課程影片 (course videos), YouTube live-recorded class sessions, screen-recording videos, or any workflow involving video download, frame extraction, OCR, Whisper transcription, per-minute cross-reference, keyframe PDFs, video cropping, or 2x speed conversion. Covers the Python AI course project at E:\01-Project\2026-07-B-python_ai_tvdi and the n8n course project at E:\01-Project\2026_08_n8n_itri.

**摘要**：
- `E:\01-Project\2026-07-B-python_ai_tvdi\`:
- pipeline/          all scripts
- videos.py        VIDEOS list: {name, url, id}; video_by_index(idx) 1-based
- paths.py         BASE/VIDEO_DIR/ANALYSIS_DIR, find_ffmpeg(), workdir_for(idx), video_path_for(idx)
- download_videos.py <start_idx>   yt-dlp sequential download, resume-safe (skips >50MB)
- extract_frames.py <idx>          ffmpeg -> frames/frame_NNNN.jpg every 10s (fps=1/10)

---

## 22. video2text

**名稱**：video2text — 影片分析（畫面 OCR × 語音 Whisper → Markdown + PDF）

**用途**：Analyze recorded meeting / online-conference videos to produce a bilingual (Traditional Chinese) markdown report plus a key-frame PDF. Extracts frames every 10s and runs RapidOCR on them, transcribes the audio with faster-whisper large-v3-turbo (CPU int8) or whisper-large-v3 via OpenVINO GenAI (Intel GPU, RECOMMENDED — RTF ~0.3), converts to Traditional Chinese with OpenCC, then cross-compares OCR slide text vs. speech into a timeline table with summary analysis. Handles speed-changed videos (e.g. 2x) by restoring audio tempo and aligning both timelines. Use when asked to "分析影片", "影片轉文字", "畫面與語音重點摘要", "OCR + whisper 比對", "ASR 轉逐字稿", or to analyze a .mp4/.wav recording into markdown/PDF deliverables.

**摘要**：
- - User says 分析影片 / 影片轉文字 / 畫面與語音重點摘要 / OCR 與語音比對 / 會議錄影分析, or hands you a `.mp4` to summarize visually + acoustically.
- - The pipeline targets **local offline inference** (no cloud APIs), using **Intel GPU where possible** (OpenVINO).
- - Python 3.13: `C:\Users\N000149839\AppData\Local\Programs\Python\Python313\python.exe` (launcher `py`).
- - **yt-dlp** installed as a pip package → run as `py -m yt_dlp ...` (NOT `yt-dlp`; the .exe is not on PATH).
- - Analysis venv `D:\80-Opnecode\workspace\_maidate_work\venv` (pip `venv\Scripts\python.exe`).
- Alternative: `D:\Downloads\2026-08-10-video2text\_maidate_work\venv` (if it exists).

---

## 23. web-tools

**名稱**：web-tools — 本機網頁工具環境

**用途**：紀錄本機 web 工具環境（Crawl4AI 爬蟲、Webwright 瀏覽器 agent）的安裝路徑與使用方式。Crawl4AI 位於 ~/web-tools/crawl4ai/.venv（Python 3.12，抓網頁轉 markdown），Webwright 位於 ~/web-tools/Webwright 且其 skill 已整合於本 skills 目錄（用 Python playwright 開 Firefox）。Use when asked to "抓網頁", "爬蟲", "crawl", "用 Crawl4AI", "網頁轉 markdown", "Webwright", "瀏覽器自動化", "web scraping", or to locate the local web tools environments.

**摘要**：
- - **定位**：Python 套件，抓取網頁並轉成乾淨的 markdown，適合 LLM 處理。
- - **Python 環境**：`~/web-tools/crawl4ai/.venv/bin/python`（Python 3.12.14）
- - **瀏覽器**：Playwright Chromium（位於 `~/Library/Caches/ms-playwright/`）
- **基本用法（async）：**
- ```bash
- ~/web-tools/crawl4ai/.venv/bin/python /tmp/xxx.py

---

## 24. webwright

**名稱**：Webwright (Claude Code adaptation)

**用途**：Solve a user-specified web task code-as-action style by driving a local Playwright browser through one bash command at a time, saving screenshots and an action log into `final_runs/run_<id>/`, and visually verifying the result. Use when the user asks to automate a web task (search, filter, form-fill, multi-step flow, data extraction) and wants reusable scripts plus screenshot evidence rather than a one-shot answer.

**摘要**：
- - **Default (one-shot).** `final_script.py` solves the task for the literal
- values the user provided. Triggered by a plain prompt or by
- `/webwright:run <task>`.
- - **CLI tool (parameterized).** `final_script.py` is a reusable CLI: one
- function with a Google-style `Args:` docstring + an `argparse` wrapper
- whose flags default to the concrete task values, so the user can rerun

---

## 25. yt-batch-download

**名稱**：yt-batch-download — YouTube 批次下載（1080p）

**用途**：批次下載 YouTube 影片（1080p 最高畫質），支援自訂檔名、cookies 匯入、SSL 修復、JS runtime 設定。Use when asked to "下載YouTube影片", "批次下載YT", "download YouTube videos batch", "下載課程影片", or to batch-download a list of YouTube URLs.

**摘要**：
- - User asks 下載 YouTube 影片 / 批次下載 YT / download YouTube videos batch / 下載課程影片
- - 需要從 GitHub README 或其他來源取得 URL 列表並批次下載
- - 需要自訂輸出檔名（依日期、時段等）
- | 工具 | 安裝方式 | 說明 |
- |------|----------|------|
- | Python 3.13+ | `py` launcher | Windows 已安裝 |

---

## 26. yt-upload

**名稱**：yt-upload — YouTube 影片上傳並公開發布

**用途**：透過 Playwright 操作 YouTube Studio，將本機影片上傳並公開發布為 YouTube 影片。支援填寫詳細的標題、說明、標籤、主題標籤，設定目標觀眾（非兒童專屬）、瀏覽權限（公開/不公開/私人），並擷取發布後的影片連結。Use when asked to "上傳YouTube", "上傳影片", "upload to YouTube", "把影片上傳公開", "發布影片", or to upload a local .mp4 to YouTube as a public video.

**摘要**：
- - User 要求把本機影片上傳到 YouTube 並公開給大家觀看
- - 需要填寫影片標題、說明、標籤等詳細資訊
- - 需要設定影片為「公開 / 不公開 / 私人」瀏覽權限
- - 需要取得發布後的影片連結（`https://youtu.be/VIDEO_ID`）
- | 工具 | 說明 |
- |------|------|

---

## 27. mate-engine-anim-patch

**名稱**：mate-engine-anim-patch — Mate Engine X（已編譯 Unity）動作數量擴充

**用途**：把 Mate Engine X 3.3.0（`MateEngineX_Data\Managed\Assembly-CSharp.dll`，Mono 後端、無原始碼）中
`AvatarAnimatorController` 寫死的動作輪播常數提高，讓 BlendTree 內「已存在但沒被輪播」的 Idle / 舞蹈動畫
全部啟用：`totalIdleAnimations` 10→19（19 個 PET_IDLE）、`DANCE_CLIP_COUNT` 5→13（13 支 PET_DANCING）。
流程：dnfile+dncil 反組譯 `.ctor` 定位常數 → UnityPy 驗證 AnimatorController（pathid 554）BlendTree 實際葉子數
→ 判斷可否同長度 hex 修改（`ldc.i4.s 10`→`ldc.i4.s 19` 可直接改 byte `1F 0A`→`1F 13`），
否則用 **Mono.Cecil** 重寫 IL（`ldc.i4.5` 1 byte 換 `ldc.i4.s` 2 byte 會位移後續 method RVA，**不可**手工插 byte）
→ dnfile 全量反組譯驗證後才覆蓋正式檔（`.bak` 為還原點）。
Use when asked to 增加 Mate 動作 / 增加 idle 數量 / 增加舞蹈數量 / 擴充 mate 動作 / mate idle 輪播 /
patch MateEngine 動畫計數 / mate engine anim patch。

**摘要**：
- - **無原始碼**：只改 `Assembly-CSharp.dll`；欄位 token `totalIdleAnimations=0x04000144`、`DANCE_CLIP_COUNT=0x04000147`。
- - **先驗證 BlendTree 再動手**：Idle 樹（State 4）node[1] clipIDs 0..18=19、Dance 樹（State 2）clipIDs 42..54=13。
- - **確認欄位只被 .ctor 寫入**（全 IL stfld 掃描）且場景無序列化覆寫，patch ctor 即生效。
- - **同長度才 hex 改**；會變長度一律 Mono.Cecil（本機已編譯 `PatchField.exe`），改完離線全量驗證。
- - 工具：`matedlltools`（dnfile+dncil）、`unitypy`、`cecil\PatchField.exe`、csc → 皆在
  `C:\Users\USER\AppData\Local\Temp\opencode\` 下（見 SKILL.md）。
- - **Husbando 模式**僅 9 個 HUS_IDLE，IdleIndex≥8 clamp 屬正常；BlendTree 葉子數即為可設定上限。

---

## 28. browser-control

**名稱**：browser-control — 瀏覽器自動化驅動（確定性 Playwright）

**用途**：Drive the user's existing Chromium-family browser with deterministic Playwright. Use when asked to inspect, automate, test, or interact with a visible browser tab; continue an authenticated browser workflow; handle 2FA, passkeys, CAPTCHAs, or payment confirmation; record browser behavior; or capture an authenticated network flow.

**摘要**：
- Browser Control 是 **driver 而非 agent**：由呼叫的 agent 決定做什麼，Browser Control 在使用者可見的瀏覽器中執行確定性 Playwright 程式碼。
- 核心迴圈：**inspect, act, verify** — 先 inspect 真實頁面再選 locator，用最窄的穩定控制元件行動，最後用 URL 或重新讀頁驗證結果。
- 經典驗證流程：採用（adopt）既有已登入分頁 → 註冊 `handoff` 人類提示（WebAuthn / 2FA / CAPTCHA / 付款）→ 完成後獨立驗證已驗證的目的端點。
- 支援 named session 續接、read-only session、`snapshot()` / `screenshotDiff()` 視覺回歸、authenticated network capture（HAR + secrets redaction）、錄影（CDP / tab capture，可含音訊）與 flight-recorder。
- 安全性：阻擋會破壞共享瀏覽器狀態的 CDP 指令（瀏覽器關閉、清 cookie/cache）；破壞性 UI 工作採「read, confirm, verify」兩階段流程。

---

## 29. taipower-exam-report

**名稱**：taipower-exam-report — 台電/國營事業考題整份詳細解答

**用途**：Use when the user asks to generate a complete detailed answer report (整份考題詳細解答) for 國營事業/台電 exam PDFs from OCR-extracted questions, or build 電路學/電子學 circuit-diagram solutions from VLM component extraction + SPICE simulation + official answer matching. Covers the Qwen2.5-VL-7B pipeline (vlm_auto_pipeline.py / vlm_auto_pipeline_113.py), SP topology back-inference (resistor_sp.py), the markdown report generators (build_full_exam.py / build_full_exam_113.py), and two-year support (113/114). Use for naming report files "*- NN 年經濟部所屬事業機構新進職員甄試試題.md" and syncing to GitHub.

**摘要**：
- 端到端流程：OCR 考題 →（電路圖）Qwen2.5-VL-7B 元件抽取 → 由數值+官方答案反推 SP 拓樸 → ngspice/PySpice 模擬 → verdict（PASS/REVIEW/SIM-ERR）→ 併入逐題權威內容產生整份詳細解答 markdown。
- 支援 **113 / 114 兩年度**（電機、電路學/電子學）：`vlm_auto_pipeline.py`（114）／`vlm_auto_pipeline_113.py`（113），`build_full_exam.py`／`build_full_exam_113.py` 報告產生器，`verify_full_exam_113.py` 驗證器。
- 113 舊 `完整解答.md` 有 9 題答案標頭錯誤（Q3/Q4/Q11/Q21/Q22/Q24/Q28/Q33/Q34）；權威來源一律是官方解答 PDF（`answers_113.json`）。
- 環境陷阱：PySpice 需 `os.add_dll_directory('C:\ngspice\Spice64_dll\dll-vs')`；**永不**直接 `ngspice -b`（~60s 後 hang），一律走 PySpice `circuit.simulator()`；先 import torch 再 import HF/PySpice；輸出 stdout 轉 utf-8。
- 已知限制：VLM 拓樸判讀不穩 → 多數題落 REVIEW/NO-CIRCUIT 屬設計；尚未實作 BJT/zener/AC phasor 模型。

---

## 30. mate-engine

**名稱**：mate-engine — Mate Engine（免費輕量桌面寵物）資訊與檔案下載

**用途**：Mate Engine（伙伴引擎）是一款**免費、輕量、開源**的 Windows 桌面寵物（Desktop Pet）軟體，是 **Desktop Mate 的免費替代品**：不綁商業角色模型、支援**自訂 VRM 角色**、可模組化（Mod）、開源（GNU AGPL v3 + MateProv2 License），且比 Desktop Mate **更省資源**。Use when asked to 下載 Mate Engine、Mate Engine 檔案、桌寵、桌面寵物、desktop pet、Desktop Mate 替代、MateEngine 下載、VRM 角色桌面寵物、mate engine download，or to find where to download Mate Engine / how to install and run it。

**檔案來源（本 skill 唯一指定）**：
- 官方 GitHub：https://github.com/shinyflvre/Mate-Engine
- 下載方式：該 repo 右側 **Releases** → 下載最新**公開發行版 ZIP**（非 source code）→ 解壓 → 執行 `MateEngineX.exe`。
- Steam 板（特殊內容 / 自動更新 / Workshop）：https://store.steampowered.com/app/3625270/MateEngine/（GitHub 版終身免費）。

**摘要**：
- 操作：執行 `MateEngineX.exe` 後，對桌寵點**右鍵**或按 `M` 開啟選單（FPS、最前面顯示、迷你模式等）。
- 授權：App 為 GNU AGPL v3 + MateProv2；內建角色版權屬 Yorshka Shop，不得在自建 Build 重新散佈。
- 防毒誤報：Windows Defender 可能誤報 `Trojan:Script/Wacatac.B1ml`（未數位簽章所致），可掃 VirusTotal 驗證後執行。
- 免費 VRM：初音ミク VRM https://booth.pm/en/items/3226395；Linux 非官方移植版 https://github.com/Marksonthegamer/Mate-Engine-Linux-Port。
- 相關 skill：`mate-engine-anim-patch`（擴充已編譯 Mate Engine X 的 Idle/Dance 動畫輪播數量；本 skill 下載後取得 `Assembly-CSharp.dll` 即可套用）。

---

## 附錄：OpenCode 本機環境設定

本機 OpenCode Desktop App 環境設定總覽：**LSP（方案 2 精準開啟）**、**TUI 外掛（oc-plugin-rainbow）**、
**瀏覽器 MCP 固定 profile**。三項修改後皆需**完全重啟** OpenCode 才生效。

---

### LSP（精準開啟 方案 2）

本機已啟用 **LSP 精準開啟（方案 2）**：僅啟用 `typescript`、`pyright`、`yaml-ls`、`bash`
四個語言伺服器。啟用後 agent 可獲得 **`lsp` 工具**（goToDefinition、findReferences、hover、
documentSymbol、workspaceSymbol、goToImplementation、callHierarchy…）與**語言伺服器診斷回饋**
（診斷訊息自動流入 agent loop）。

#### 啟用開關（兩個都要）

| 開關 | 設定 | 位置 |
|------|------|------|
| ① `lsp` 工具 | 使用者層級環境變數 `OPENCODE_EXPERIMENTAL_LSP_TOOL=true`（或 `OPENCODE_EXPERIMENTAL=true`） | 系統內容 → 環境變數 |
| ② LSP server | `"lsp": { ... }`（見下） | `~/.config/opencode/opencode.jsonc` |

#### 設定內容

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "lsp": {
    "typescript": {},
    "pyright": {},
    "yaml-ls": {},
    "bash": {}
  }
}
```

OpenCode 在**讀到對應副檔名的檔案**且**必要條件滿足**時才啟動該伺服器（不會全載）。

| LSP | 副檔名 | 必要條件 | 本機狀態 |
|-----|--------|----------|----------|
| typescript | .ts/.tsx/.js/.jsx/.mjs/.cjs/.mts/.cts | 該專案需有 `typescript` 依賴 | ✅ Node 22 |
| pyright | .py/.pyi | 全域安裝 `pyright` | ✅ `npm i -g pyright`（已裝） |
| yaml-ls | .yaml/.yml | 自動下載 yaml-language-server | ✅ 自動下載 |
| bash | .sh/.bash/.zsh/.ksh | 自動下載 bash-language-server | ✅ 自動下載 |

#### 安裝／維護

```bash
npm i -g pyright                                     # pyright（本機已安裝）
cd <某個 TS/JS 專案> && npm i -D typescript          # typescript LSP 吃「專案自身」的 typescript 依賴
```

改完 `opencode.jsonc` 或環境變數後，需**完全重啟** OpenCode Desktop App 才生效。

#### 其他設定選項（參考）

- `"lsp": true` → 全開（所有內建 server）
- `"lsp": false` → 全關（預設值）
- `"lsp": { "typescript": { "disabled": true } }` → 全開但排除特定 server
- 自訂 server：`command` / `extensions` / `env` / `initialization` / `disabled`

> **未啟用的理由**：`jdtls`（Java）需 JDK 21+，而本機僅有 Java 8（HCL Notes 用）不適用；
> gopls / rust / lua-ls / ruby-lsp / php intelephense / clangd 等對應工具鏈未安裝，用不到就不自動下載，
> 避免浪費記憶體與啟動時間（官方 Best Practices 建議不要無腦全開）。
> `.ps1`（PowerShell）與 `.md` 目前沒有對應內建 LSP。

---

### TUI 外掛：oc-plugin-rainbow（彩虹特效）

TUI 外掛 oc-plugin-rainbow 為 OpenCode 終端介面加入**主題感知彩虹後製**：中性文字前景動畫色帶
+ 可選背景色調 + 內建設定對話框。需 OpenCode `>=1.3.14`。

設定檔：`~/.config/opencode/tui.json`

```jsonc
{
  "$schema": "https://opencode.ai/tui.json",
  "plugin": [
    ["oc-plugin-rainbow", { "enabled": true, "fg": true, "bg": true, "speed": 0.008, "turns": 3, "glow": 0.05 }]
  ]
}
```

常用選項：`enabled`（總開關）、`fg` / `bg`（文字／背景動畫）、`speed`（0–0.03）、`turns`（0.25–8）、
`glow`（0–0.15）、`keybinds.logo_splash`（預設 `ctrl+shift+r`，觸發白閃 logo 畫面）。

**安裝方式（本機已裝，v0.1.1）**，三選一：

```bash
opencode plugin oc-plugin-rainbow                             # CLI 安裝（官方方式）
npm install --prefix ~/.cache/opencode oc-plugin-rainbow@0.1.1 # 直接裝進 TUI 外掛快取（本機用此法）
```

或 TUI 內 `Ctrl+P → Install Plugin` 互動安裝。

微調：對話框輸入 `/rainbow-settings`（或 `Ctrl+P → Rainbow settings`）即時調整，設定存本機。

---

### 瀏覽器 MCP 固定 profile（跨專案共用登入）

Playwright MCP 預設按「工作區 hash」建立 profile
（`%USERPROFILE%\AppData\Local\ms-playwright\mcp-{channel}-{workspace-hash}`），
**不同專案 = 不同 profile = 每次都是未登入／空帳號**。解法：指定固定 `--user-data-dir`。

`~/.config/opencode/opencode.jsonc`：

```jsonc
"mcp": {
  "playwright": {
    "type": "local",
    "command": ["npx", "-y", "@playwright/mcp@latest", "--user-data-dir=C:\\Users\\N000149839\\.cache\\opencode-browser-profiles\\playwright"],
    "enabled": true
  },
  "chrome-devtools": {
    "type": "local",
    "command": ["npx", "-y", "chrome-devtools-mcp@latest", "--autoConnect"],
    "enabled": true
  }
}
```

- **Playwright MCP** → 固定 profile `~/.cache/opencode-browser-profiles/playwright`，**所有專案共用同一份登入狀態**。
- **chrome-devtools MCP** → 維持 `--autoConnect`：自動連到使用者正在執行的 Chrome 預設 profile，
  直接沿用日常 Chrome 的登入（需 Chrome 144+，且已於 `chrome://inspect/#remote-debugging` 啟用遠端除錯）。
- ⚠️ **兩個 MCP 不可共用同一個 profile 目錄**（Chrome profile 一次只能被一個實例鎖定）；
  需多開並行 MCP 客戶端時，Playwright 各自指定不同 `--user-data-dir` 或加 `--isolated`。

---

### 生效與驗證

改完設定都要**完全重啟** OpenCode Desktop App：

- LSP：agent 出現 `lsp` 工具、診斷回饋流入對話
- Rainbow：`Ctrl+P → Rainbow settings`、`Ctrl+Shift+R`（logo flash）
- Playwright profile：登入任一網站 → 換到另一專案 → 仍保持登入

---

## 31. hcl-notes-forward

**名稱**：hcl-notes-forward — HCL Notes 公布函自動轉寄＋信箱匯出分析／讀取加密信件

**⚠️ 安裝狀態：預設不安裝、僅限本台專屬電腦**

- 此 skill 是**本台專屬電腦（Windows，已安裝 HCL Notes client + 截圖/OCR 工具鏈）的專用 skill**，僅此台需要安裝。
- GitHub 上**預設不安裝**此 skill；其他台若要使用**必須人工指定安裝**（手動將 `hcl-notes-forward/` 資料夾複製到 `~/.config/opencode/skills/hcl-notes-forward/`），不會隨收藏庫自動部署。
- 依賴本機環境（HCL Notes 11 client、`C:\lotus\Notes\nlnotes.exe`、特定 ID 檔與 OCR venv），無 Notes client 的機器無法執行。

**用途**：自動化 HCL Notes（本機 Windows client）的兩類工作：
1. **公布函批次直接轉寄**：將信箱依寄件者($BySender)視圖中「公布函系統通知」群組的未讀信件，逐封以「直接轉寄」寄給指定群組（如「工三碳化矽專案組-03-全組(21)」），寄完刪除原信。
2. **信箱匯出分析 + 讀取加密個人機密信件**：將信箱整批匯出為 Structured Text（Big5）解析主旨/日期做年度分類與比例分析（如「主管獎勵金」5 封年度統整）；對 Encrypt:1 的加密信件以 UI 開啟＋OCR 讀取數值（例：2025 年度獎勵金額 360,000、所得稅 18,000、健保補充保費 5,327、合計實發 336,673）。

全程不做 JNI（伺服器路徑在互動式密碼保護下封死），全部用**畫面截圖 + RapidOCR + 螢幕絕對座標點擊**的 UI 自動化。

**摘要**：
- **座標**：Notes 主視窗位置不固定（例 (761,21) 1121x839、(1000,0) 920x940），每次 `GetWindowRect` 現量；OCR/a11y 座標是視窗內座標，點擊前須＋視窗左上角轉螢幕絕對座標。
- **開信**：先單擊選列確認反白，再 dblclick 或 Enter；避免誤開相鄰列（預覽窗格標題魚目混珠）。
- **加密信件**：匯出檔不含欄位值；只能 UI 開啟＋OCR 讀數值（數字欄位可靠，中文欄位名易認錯，靠數字+匯出檔交叉驗證）。
- **雷區**：Ctrl+W/Escape 可能觸發「文件已刪除」對話框；視圖捲動位置每次重排，需重新 OCR 現量列位置；小字(<28px)中文 OCR 幾乎必錯，用 `crop.py ... 4`（LANCZOS 4x）放大改善。
---

## 32. opencode-session-auto-name

**名稱**：opencode-session-auto-name — Session 標題自動命名

**用途**：讓 opencode 的 session 名稱自動取自「第一次使用者 prompt 的總結」或「進行中 todo」，取代泛型 `New session - ...` 標題。

**適用時機**：使用者要求「自動命名 session」、「標題自動取名」、「session 標題總結」、「第一個 prompt 當作標題」、或要設定 opencode 自動命名。

**前置需求**（本機已裝）：
- plugin `opencode-auto-name` v0.1.3，安裝於 `~/.config/opencode/node_modules/`
- 全域 `opencode.jsonc` 已加入：
  `{ "plugin": [["opencode-auto-name", { "template": "{firstMessage}", "maxLength": 50 }]] }`

**摘要**：
- 監聽 `session.created`/`message.updated`/`todo.updated`/`command.executed`，以樣板計算標題；debounce 10s 避免對話中標題狂跳，每 60s 周期重查。
- 「總結」為**純規則式**（去開頭贅詞 → 取首句 → 去尾標點 → 超過 maxLength 截斷加 `…`），**0 Token、不需要 LLM、與模型無關**。
- 樣板變數：`{project}`、`{task}`、`{firstMessage}`、`{messageCount}`、`{model}`、`{date}`、`{time}`；`{a || b}` 表示 a 為空時退回 b。
- **注意**：原生自動命名（`ensureTitle`，small model 總結第一則訊息）在 `opencode/big-pickle` 供應商下有已知 bug（issue #30662、#7523）會默默失敗，故本機改用此 plugin。
- 若要「AI 語意總結」而非首句裁剪：替代方案為 `opencode-session-summary`（LLM、長 session 會消耗數萬 Token）或 `opencode-autotitle`（關鍵字 + 自動挑最便宜模型精煉）。

**產出**：每個新 session 的標題 = 第一個 prompt 的首句總結（或進行中 todo）。

- 完整安裝步驟、樣板變數對照、驗證流程與替代方案比較見本 skill 的 `SKILL.md`。
