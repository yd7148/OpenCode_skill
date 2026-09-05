# OpenCode Skills 技能說明

本文件詳細說明本儲存庫中每支 OpenCode Skill 的功能、適用時機、運作流程與產出。
所有 skill 皆為 **MIT 授權**，適用於 **opencode agents**，作業系統為 **Windows（PowerShell 5.1）**。

---

## 目錄

| Skill | 一句話說明 |
|-------|-----------|
| [comsol-analyzer](#1-comsol-analyzer--comsol-multiphysics-mph-模型分析) | 解析 COMSOL .mph 模型，產出繁體中文分析報告 |
| [dwg-to-dxf](#2-dwg-to-dxf--dwg-轉-dxf-與詳細解析) | DWG 轉 DXF 並進行幾何/圖層/尺寸詳細分析 |
| [md-to-pdf](#3-md-to-pdf--繁中-markdown--a4-pdf) | 將繁體中文 Markdown 離線渲染成精美 A4 PDF |
| [v2t-report-summary](#4-v2t-report-summary--重點彙總-ver2) | 將逐分鐘影片報告濃縮成乾淨的繁體中文重點摘要 |
| [video-2x-speed](#5-video-2x-speed--影片加速轉檔) | 以 ffmpeg 將影片加速為 200% 播放速度 |
| [video2text](#6-video2text--影片分析管線) | 影片畫面 OCR × 語音 Whisper → Markdown + 關鍵幀 PDF |
| [yt-batch-download](#7-yt-batch-download--youtube-批次下載) | 批次下載 1080p YouTube 影片 |
| [yt-upload](#8-yt-upload--youtube-影片上傳發布) | 透過 Playwright 上傳並公開發布 YouTube 影片 |
| [tts](#9-tts--文字轉語音) | 用 edge-tts 將文字轉成繁體中文等語音檔 |
| [taobao-order-extract](#10-taobao-order-extract--淘寶訂單資料提取整理) | 從淘寶訂單 Excel 提取訂單資料並比對物流重量 |
| [taobao-cost-fill](#18-taobao-cost-fill--淘寶費用計算明細填寫) | 依訂單卡片填寫淘寶費用計算明細 R0 樣板並存成 R1 |
| [github-skill-sync](#11-github-skill-sync--本機-github-skills-同步) | 雙向同步本機 skills 與本 GitHub 收藏庫 |
| [webwright](#12-webwright--瀏覽器-agent) | code-as-action 瀏覽器 agent（Playwright 開 Firefox） |
| [web-tools](#13-web-tools--本機網頁工具環境) | 本機 Crawl4AI / Webwright 環境筆記 |
| [pdf-exam-extractor](#14-pdf-exam-extractor--考題pdf擷取與ocr) | 考題 PDF 逐題裁剪成圖 + EasyOCR 轉 Markdown |
| [taipower-exam-solver](#15-taipower-exam-solver--國營事業考題解題) | 國營事業招考 PDF 考題、官方解答與逐步解題 |
| [takeout-exif-merge](#16-takeout-exif-merge--google-相簿-exif-合併) | 將 Takeout JSON EXIF 合併回同名媒體檔 |
| [video-class-pipeline](#17-video-class-pipeline--課程影片分析管線) | 課程影片批式分析（OCR × Whisper × 關鍵幀 PDF）與編輯 |

---

## 1. comsol-analyzer — COMSOL Multiphysics .mph 模型分析

**用途**：剖析 COMSOL Multiphysics 的 `.mph` 模型檔案，產出詳細的繁體中文 Markdown 分析報告，涵蓋模型詮釋資料、參數、物理場、幾何、材料、研究與網格。

**適用時機**：使用者要求「分析 COMSOL 模型」、「說明 .mph 檔案」、「COMSOL 模型結構」，或想了解模型中的物理/幾何/材料/研究設定。

**前置需求**：
- PowerShell 5.1（Windows 內建）
- **不需安裝 COMSOL**——`.mph` 其實是 ZIP 壓縮檔，可直接解壓解析

**運作流程**：
1. 將 `.mph` 複製並改名成 `.zip`，用 `Expand-Archive` 解壓
2. 依序解析內部 XML/JSON 檔（`modelinfo.xml`、`dmodel.xml`、`smodel.json` 等）
3. 萃取：全域參數、物理場（線圈定義、材料模型、邊界條件、多物理耦合）、幾何序列、材料性質、研究類型（CCC/頻率/暫態/穩態）、網格設定、結果繪圖
4. 產出涵蓋 14 大節的詳細 Markdown 報告
5. 清理暫存檔

**產出**：`<model_name>-模型詳細說明.md`

**注意**：`dmodel.xml` 可達 5–60 MB 需分段讀取；`.mphbin` 為二進位檔無法直接讀取。

**[回到目錄](#目錄)**

---

## 2. dwg-to-dxf — DWG 轉 DXF 與詳細解析

**用途**：將 AutoCAD `.dwg` 檔轉成 `.dxf`（使用 ODA File Converter），再用 Python `ezdxf` 進行完整的幾何與詮釋資料解析，產出繁體中文分析報告。

**適用時機**：使用者要求「轉換 DWG」、「DWG 轉 DXF」、「分析 DWG 檔案」、「DWG 幾何分析」，或想查看 AutoCAD 圖面的圖層/尺寸/幾何/圖塊內容。

**前置需求**：
- ODA File Converter（`C:\Program Files\ODA\ODAFileConverter 27.1.0\`）
- Python `ezdxf`（`py -3 -m pip install ezdxf`）
- PowerShell 5.1

**運作流程**：
1. 確認/安裝 ODA File Converter
2. 準備輸入/輸出目錄並複製 DWG
3. 以命令列轉檔（`ODAFileConverter.exe <in> <out> ACAD2018 DXF 0 1`）
4. 撰寫 ezdxf 分析腳本，分析：
   - 檔案基本資訊（版本、單位、範圍）
   - 圖層結構（顏色、線型、可見性、實體數）
   - 實體統計（LWPOLYLINE、LINE、CIRCLE、HATCH、DIMENSION、TEXT…）
   - 尺寸標註、幾何結構、填充圖案、文字物件、圖塊、版面配置
5. 產出詳細 Markdown 報告並清理暫存

**產出**：`<drawing_name>-圖面詳細說明.md`

**注意**：ezdxf 無法直接讀 DWG，須先轉 DXF；ODA 需以目錄為單位處理。

**[回到目錄](#目錄)**

---

## 3. md-to-pdf — 繁中 Markdown → A4 PDF

**用途**：將繁體中文 Markdown 說明檔渲染成排版精美的 A4 多頁 PDF。使用 Pillow + 微軟正黑體**離線產生**，不需網路或 wkhtmltopdf/pandoc/LaTeX。

**適用時機**：使用者要求「寫一個 Markdown 說明檔案以及 PDF 格式說明檔案」、「把 md 轉成 PDF」或產出成對的 `.md`/`.pdf`。

**前置需求**：
- Python venv 含 Pillow
- 中文字體：`C:\Windows\Fonts\msjh.ttc`（正黑體）/ `msjhbd.ttc`（粗體）
- 英數字體：`C:\Windows\Fonts\consola.ttf`

**支援語法**：`#`/`##`/`###` 標題、段落、清單、引言、圍欄代碼區塊、表格（自動欄寬＋斑馬紋）、分隔線、頁尾頁碼。

**運作流程**：
1. 先寫好 Markdown 原稿
2. 複製 `make_md_pdf.py` 渲染腳本並改開頭 `SRC`/`OUT` 路徑
3. 執行並以 RapidOCR 回讀首頁 PNG 驗證中文未亂碼

**產出**：`<主題>.md` + `<主題>.pdf`（A4 多頁）

**注意**：本 skill 無法加入巢狀清單或行內粗斜體語法；表格過長需拆分。

**[回到目錄](#目錄)**

---

## 4. v2t-report-summary — 重點彙總 ver2

**用途**：將逐分鐘的詳細影片分析報告（`-3-report.md`：時間｜語音重點｜畫面OCR重點｜GitHub 對照）濃縮成乾淨、校正過的繁體中文重點摘要（`-3-report-ver2.md`）。

**適用時機**：使用者提供 `-3-report.md`（或課程/影片名稱如 `Class17-2026_08_12_晚上`）並要求「彙總分析」、「重點彙總」、「產出 ver2 摘要」。

**運作流程**：
1. 找到並驗證來源檔（確認是真文字，非 docx 偽裝的 .md）
2. **完整讀取後才撰寫**——僅依報告資料衍生，不臆造
3. 讀取時靜默校正常見 ASR 誤聽（雷神NN→lessonNN、Open call→OpenCode、Power share→PowerShell、Greema→Gemma、Ghfome→Chrome、DHUB→GitHub 等）
4. 套用 2x 影片時間軸慣例（原始課程時間 = ×2）
5. 產出結構化摘要（詮釋資料表 + 依時間排序的編號章節 + 附註）

**產出**：`<BASE>-3-report-ver2.md`（約 40–60 行，UTF-8 無 BOM）

**[回到目錄](#目錄)**

---

## 5. video-2x-speed — 影片加速轉檔

**用途**：以 ffmpeg 將錄影影片轉成 **200% 播放速度**（或任意 0.5x–100x），維持相同解析度與 fps，並用 Intel GPU（`h264_qsv`）編碼、`atempo` 保留音調。也可結合裁切黑色區塊與加速一次完成。

**適用時機**：使用者要求「加速影片」、「轉成 2 倍速」、「200% 播放速度」、「裁切黑邊」，或要產出已下載 .mp4 的 2x/裁切版本。

**前置需求**：
- ffmpeg 7.1（`C:\Users\N000149839\opencode-tools\ffmpeg.exe`）
- Intel GPU + `h264_qsv` encoder
- yt-dlp（pip 安裝）

**關鍵經驗（重要陷阱）**：
- `-ss`/`-t` 必須放在 `-i` **之前**（輸入端裁切），否則會產出非真正加速的檔案
- 30fps 來源＋`setpts=PTS/2` 會導致 QSV「unsupported frame rate」，需加 `fps=30`
- 裁黑邊不可只信 `cropdetect`，需用 PIL 逐欄量測亮度（黑值門檻 32 非 16）
- 批次模式下段檔案被中斷會無 moov atom，續跑需先 probe 再跳過

**產出**：`<video名>-2x.mp4`（來源旁，唯一檔名）

**[回到目錄](#目錄)**

---

## 6. video2text — 影片分析管線

**用途**：將錄製的會議/線上課程影片分析成**繁體中文 Markdown 報告 + 關鍵幀 PDF**。每 10 秒擷取畫面跑 RapidOCR，以 faster-whisper large-v3-turbo（CPU int8，建議）或 OpenVINO whisper-large-v3（Intel GPU，舊版）轉錄語音，OpenCC 轉繁體，再將 OCR 幻燈片文字與語音交叉比對成時間軸表格與重點分析。

**適用時機**：使用者要求「分析影片」、「影片轉文字」、「畫面與語音重點摘要」、「OCR + whisper 比對」。目標是**本機離線推論**（不依賴雲端 API）。

**完整管線**：
1. 影片取得（yt-dlp / HLS fallback）
2. 音訊＋畫面擷取（處理 2x 影片的還速與時間軸對齊）
3. OCR 全部畫面（CPU 並行，續跑安全）
4. Whisper 轉錄（faster-whisper，checkpoint 續跑）
5. 幻燈片分群＋語音對齊
6. 產出 Markdown 報告（分析方法/概述/時間軸摘要/知識點/外部比對/幻覺偵測/驗證/結論）
7. 產出關鍵幀 PDF

**注意**：
- 報告檔名一律純 `.md`（不可 `.md.docx`），需驗證 magic bytes 非 `PK\x03\x04`
- 需記錄所用模型與幻覺率（tiny 高達 ~88%，僅供參考）
- `BatchedInferencePipeline` 會 hang，禁用以外的 `model.transcribe()` 只適用

**產出**：
- `<video名>-分析影片-畫面與語音重點摘要.md`
- `<video名>-分析影片-畫面與語音重點摘要.pdf`
- `<video名>-畫面重點.pdf`（關鍵幀）

**[回到目錄](#目錄)**

---

## 7. yt-batch-download — YouTube 批次下載

**用途**：批次下載多支 YouTube 影片，**1080p 最高畫質**，支援自訂檔名、cookies 匯入、SSL 修復、JS runtime 設定。

**適用時機**：使用者要求「下載 YouTube 影片」、「批次下載 YT」、「下載課程影片」，或要從 URL 列表批次下載。

**前置需求**：
- Python 3.13+（`py` launcher）
- yt-dlp（pip 安裝）
- ffmpeg + ffprobe
- deno（JS runtime，解決 n challenge）
- browser_cookie3（從 Chrome 匯出 cookies 繞 403）

**關鍵參數（缺一不可）**：`--no-check-certificates`、`--cookies`、格式選擇 `bestvideo[height<=1080]...`、`--merge-output-format mp4`、`--ffmpeg-location`、`--js-runtimes deno`、`--remote-components ejs:github`。

**重要經驗**：
- deno **必須在 PATH 上**，否則 `JS runtimes: none`、n challenge 失敗只剩 storyboard
- 成功訊號：log 出現 `[jsc:deno] Solving JS challenges using deno`
- cookies 有詐欺有效期限，過期需重新匯出
- 支援直播重播（`youtube.com/live/ID`）與一般影片

**產出**：依來源 README 標題命名的 1080p `.mp4` 檔

**[回到目錄](#目錄)**

---

## 8. yt-upload — YouTube 影片上傳發布

**用途**：透過 Playwright 操作 YouTube Studio，將本機影片（.mp4）上傳並**公開發布**為 YouTube 影片。支援填寫詳細的標題、說明、標籤、主題標籤，設定目標觀眾（非兒童專屬）與瀏覽權限（公開/不公開/私人），並擷取發布後的影片連結。

**適用時機**：使用者要求「上傳 YouTube」、「上傳影片」、「把影片上傳公開」、「發布影片」。

**前置需求**：
- Playwright 瀏覽器（chrome）
- 已登入的 YouTube/Google 帳戶 session
- 本機 .mp4 影片檔

**運作流程**：
1. 開啟 `studio.youtube.com`（未登入需先引導登入）
2. 點「上傳影片」→「選取檔案」→ 提供本機 .mp4
3. 填寫標題、說明（含主題標籤）、標記、目標觀眾
4. 設定瀏覽權限（預設公開）
5. 點「發布」
6. 擷取並驗證影片連結（`https://youtu.be/VIDEO_ID`）

**產出**：公開可觀看的 YouTube 影片連結，含詳細的標題/說明/標籤設定

**[回到目錄](#目錄)**

---

## 9. tts — 文字轉語音

**用途**：使用 **Microsoft Edge 的雲端神經語音**（`edge-tts`）將文字轉成高品質語音檔（.mp3）。不需本機語音模型，支援繁體中文（正體）、簡體中文、粵語與多國語言與多種聲音，可調整語速/音量/音調，並可輸出字幕。

**適用時機**：使用者要求「文字轉語音」、「TTS」、「產出語音檔」、「文字變成聲音」、「生成旁白 / voiceover 音檔」。

**前置需求**：
- Python 3 `edge-tts`（`py -3 -m pip install edge-tts`）
- 網路連線（呼叫微軟雲端 `speech.platform.bing.com`）
- **本機需帶 proxy**：`--proxy $env:HTTPS_PROXY`

**繁體中文聲音**：`zh-TW-HsiaoYuNeural`（女）、`zh-TW-HsiaoChenNeural`（女）、`zh-TW-YunJheNeural`（男）；另有簡中 `zh-CN-*`、粵語 `zh-HK-*`、英語 `en-US-*` 等。

**基本用法**：
```
py -m edge_tts --voice "zh-TW-HsiaoYuNeural" --text "你好。" --write-media "out.mp3" --proxy $env:HTTPS_PROXY
```
長文稿用 `--file "text.txt"`（UTF-8）。語速/音調負值需用 `--rate=-10%`、`--pitch=-10Hz` 等號形式。

**重要陷阱**：
- **一定要帶 `--proxy`**，否則 `socket.gaierror: getaddrinfo failed`（Fortinet proxy 環境）
- 負值參數用 `=` 形式，否則 argparse 報 `expected one argument`
- 需網路，離線不可用
- 專為 HyperFrames 影片配音可改走 `media-use` skill

**產出**：`<名稱>.mp3`（語音檔），選用 `<名稱>.srt`（字幕）

**[回到目錄](#目錄)**

---

## 10. taobao-order-extract — 淘寶訂單資料提取整理

**用途**：從淘寶導出的 `訂單數據.xlsx` Excel 檔案提取訂單資料（商品名稱、實付金額、物流公司與單號），並依一份物流重量清單比對補上各物流單號對應的重量，依序輸出成每筆訂單的 markdown 段落，可存檔成 `.md` 檔。

**適用時機**：使用者要求「整理訂單」、「訂單數據提取」、「淘寶訂單整理」、「訂單資料匯總」，或需把 `訂單數據.xlsx` 解析成依序編號的訂單卡片。

**前置需求**：
- Python 3 + `openpyxl`（安裝於專用 venv）

**輸入**：
1. **訂單 Excel**：`訂單數據.xlsx`（sheet 名稱通常為「訂單數據」，含表頭）
2. **物流重量清單**（選用）：純文字/表格，格式「物流單號 + 目的地（台灣）+ 重量」，如 `79027852606958 台灣 1.260`

**訂單 Excel 欄位**（每列依序）：
`訂單號, 訂單提交時間, 訂單狀態, 店鋪名稱, 商品名稱, 商品連結, 型號款式, 商品數量, 商品金額, 實付金額, 運費, 物流公司, 物流單號`

**重要處理規則**：
- **分組**：同筆訂單可能有多列。若「訂單號」欄為空 `None`，該列屬於上一筆有訂單號的訂單；每個「訂單號」視為一筆獨立訂單。
- **商品名稱**：取該訂單第一列（訂單號那列）的「商品名稱」。
- **實付金額**：取該訂單第一列的「實付金額」（訂單號所在列），非子列。
- **物流**：使用「物流公司」與「物流單號」欄位。
- **交易關閉**：若訂單狀態為「交易關閉」，則無物流公司與單號，標記為 `(交易關閉)`。

**重量比對**：若提供物流重量清單，建立 `{物流單號: 重量}` 對照，在每個訂單的物流單號後追加 `物流單號 台灣 重量`；查無資料不追加；重量清單中無對應訂單的單號在輸出時提示使用者。

**產出**：依序編號（`#01`、`#02`…）的 markdown 訂單卡片，存檔如 `訂單數據整理.md`。

**注意**：若結果筆數與使用者預期不符，主動說明實際筆數；商品名稱與金額保留簡體原文，標題與重量「台灣」用繁體，金額保留 `￥` 符號。

**[回到目錄](#目錄)**

---

## 11. github-skill-sync — 本機 ↔ GitHub Skills 同步

**用途**：同步本機 OpenCode skills 目錄與 GitHub 上的 `yd7148/OpenCode_skill` 收藏庫，支援下載（GitHub→本機）與上傳（本機→GitHub）雙向，並維持兩邊說明文件一致。

**適用時機**：使用者要求「同步 skill」、「更新 skill 收藏庫」、「sync skills」、「上傳本機 skill 到 GitHub」、「從 GitHub 拉下 skills」。

**前置需求**：
- SSH key 已加至 GitHub，repo 以 SSH remote 同步到 `~/OpenCode_skill`
- 本機 skills 目錄 `~/.config/opencode/skills/`

**運作流程**（雙向）：
1. 先 `git pull`/`git fetch` 確保 clone 最新。
2. 用 `rsync`（排除 `.venv/`、`__pycache__/`）把 repo↔本機各 skill 同步。
3. 同步根目錄 `README.md` / `SKILLS.md` 保持一致。
4. 上傳方向：`git add -A` → 檢視 `git status` → commit（`yd7148@hotmail.com.tw`）→ `git push origin main`。
5. 空目錄不追蹤、跳過並提醒；`.venv` 永不提交。

**產出**：本機與 GitHub 兩處 skills 與說明文件一致。

**注意**：push 走 SSH（不需 token）；新增 skill 時記得同步更新 `README.md` 目錄表與 `SKILLS.md` 章節。

**[回到目錄](#目錄)**

---

## 12. webwright — 瀏覽器 agent

**用途**：Microsoft 開源的 SWE-style 瀏覽器 agent 框架。agent 透過 bash 逐命令執行 Python/Playwright script 操作瀏覽器（code-as-action），留下可重跑的 `final_script.py` 與截圖證據。

**適用時機**：自動化網頁任務（搜尋、篩選、填表、多步驟流程、資料抽取），且使用者想要可重用 script + 截圖證據，而非一次性答案。

**前置需求**：
- Python 3.12 venv：`~/web-tools/webwright-python/.venv`（含 playwright、httpx、pydantic）
- Playwright Firefox：`~/Library/Caches/ms-playwright/firefox-1538`
- 無需 API key（借用 host model）

**運作流程**（參考 `reference/workflow.md`）：
1. 建立 `plan.md` 列出關鍵檢查點（CP）。
2. 用 scratch Playwright script 探索穩定的 selector。
3. 寫 `final_script.py`（含步驟 log 與截圖）。
4. 執行並自我驗證（讀 PNG 對照 plan.md），逐項打勾。
5. 全部通過才回報最終資料。

**重要**：進度 log 為 `final_runs/run_<id>/final_script_log.txt`；瀏覽器用 Firefox（某些站用 Chromium 會 `ERR_HTTP2_PROTOCOL_ERROR`）。

## 13. web-tools — 本機網頁工具環境

**用途**：紀錄本機已安裝的網頁工具環境路徑與用法，供 agent 在需要爬蟲或瀏覽器自動化時引用對應 venv。

**內容**：
- **Crawl4AI**：`~/web-tools/crawl4ai/.venv/bin/python`（Python 3.12），抓網頁轉乾淨 markdown。用 `AsyncWebCrawler`/`SyncWebCrawler`。
- **Webwright**：`~/web-tools/Webwright`，python env `~/web-tools/webwright-python/.venv`。
- Playwright 瀏覽器路徑須設 `PLAYWRIGHT_BROWSERS_PATH=/Users/4pins/Library/Caches/ms-playwright`。

**[回到目錄](#目錄)**

---

## 14. pdf-exam-extractor — 考題 PDF 擷取與 OCR

**用途**：從考題 PDF（如國營事業招考）中逐一擷取每道題目，把每題裁剪成獨立圖片、執行 OCR，並輸出每題的 Markdown 檔。

**適用時機**：使用者要求「擷取考題 PDF」、「逐題 OCR」、「把每題裁剪成圖片」、處理國營事業招考考卷（台電/中油/台水/台糖）。

**前置需求**（Windows）：
- Python：pymupdf、pdfplumber、easyocr、opencv-python、Pillow
- GPU 加速：`torch`（CUDA）
- 中文/非 ASCII 路徑會破壞 `cv2.imread` → 一律用 `np.fromfile` + `cv2.imdecode` 或 PIL

**運作流程**：
1. 用 pdfplumber 擷取文字座標（`x_tolerance`/`y_tolerance` 因版面調整）
2. 以正則比對題號（`1.`～`50.`）定位每題起點，過濾頁碼、選項標籤等雜訊
3. 用 PyMuPDF 將每頁轉成 2x 縮放 PNG
4. 依題號排序計算裁剪邊界（含上方 padding），換頁時避免題號重複覆寫
5. 用 EasyOCR 逐題辨識並輸出 Markdown（以 UTF-8 包裝 stdout 避免中文亂碼）

**產出**：`提取結果/` 下 `q01.md ~ q50.md`、`q01.png ~ q50.png`、`summary.md` 題目索引表

**注意**：pdfplumber 為 72 DPI 座標，裁剪 2x 圖時 y 座標需乘 2；電路圖需保留圖檔，OCR 無法還原圖形內容。

**[回到目錄](#目錄)**

---

## 15. taipower-exam-solver — 國營事業考題解題

**用途**：端對端處理國營事業招考（台電/中油/台水/台糖）考題 PDF：用 pymupdf 擷取題目、從台電官網搜尋官方解答、並產出逐步詳解（電路學、電子學、基本電學等）。

**適用時機**：使用者要求「處理台電考題 PDF」、「解電路學/電子學題目」、「查官方答案」、「產出完整解答文件」。

**前置需求**：
- Python `pymupdf`（fitz）
- 網路（存取台電官方解答 PDF）

**運作流程**：
1. 以 pymupdf 渲染 PDF 頁面為圖片並擷取文字（`Matrix(3,3)` 提高清晰度）
2. 到台電官網 `https://www.taipower.com.tw/2289/2544/2554/2556/simpleList` 搜尋官方試題/解答 PDF
3. 讀取解答 PDF（格式：每題以 `[X]` 開頭，X 為 A/B/C/D）
4. 以領域知識逐步解題；電路圖題目先從元件標籤重建電路，再搭配渲染圖片
5. 輸出完整解答文件

**產出**：`提取結果_v4/完整解答.md`（含題目、選項、答案與詳解）

**注意**：pymupdf 無法讀加密 PDF；電路圖為向量圖形，文字擷取會遺漏接線拓撲，需以渲染圖為參考；中文＋數學符號的 OCR 品質不穩，建議與網路來源交叉比對。

**[回到目錄](#目錄)**

---

## 16. takeout-exif-merge — Google 相簿 EXIF 合併

**用途**：將 Google 相簿 Takeout 的 `*.jpg.supplemental-metadata.json`（含 `(N)` 計數變體）側車 JSON 的 EXIF 資訊就地（in-place）寫回對應的圖片/影片檔，使用 ExifTool。同步腳本見 `scripts/merge_exif.py`。

**適用時機**：使用者要求「把 Takeout JSON EXIF 寫入同名影片圖片」、「處理 Google 相簿 Takeout 資料夾」、「產出 EXIF 合併成果報告」。

**前置需求**：
- Python 3 + ExifTool（winget `OliverBetz.ExifTool`）
- PowerShell 需設 `PYTHONIOENCODING=utf-8`，避免 CP950 中文亂碼；`Set-Content` 會寫 UTF-8 BOM，回讀時需去除

**關鍵要點**：
- 檔名配對：`foo.jpg.supplemental-metadata.json` ↔ `foo.jpg`；`(1)` 計數變體亦有兩種命名形式
- JSON 鍵：`photoTakenTime`/`creationTime`、`geoData`、`title`、`description`、`people[]`、`favorited`
- 內容 ≠ 副檔名：`.heic/.png/.arw/.dng` 內實為 JPEG、`.mts/.avi` 內實為 MOV 時，ExifTool 拒絕寫入 → 先偵測 magic bytes，用正確副檔名的暫存複本寫入後再 `os.replace`
- 結構損壞檔（Truncated SubIFD / Bad SubIFD / Truncated mdat / BMP）：改以 `os.utime` 設定 mtime 保留時間戳
- 效能：`-stay_open True -@ -` 平行寫入，8 workers 於 ~315k 檔案約 55 分鐘

**運作流程**：
1. `merge_exif.py build <資料夾> pairs.tsv` 掃描並配對 JSON↔媒體
2. `merge_exif.py run --exe <ExifTool> --pairs pairs.tsv --workers 8` 平行寫入（progress 檔可續跑）
3. `merge_exif.py verify` 以 mtime 驗證（mtime == photoTakenTime ±1s 為 `ok`）
4. 取出 `fail` 清單 → `--retry-from` 重試 → 再驗證
5. 輸出 Markdown 成果報告（配對/未配對/殘留計數、完整寫入 vs 僅 mtime、損壞類別統計）

**產出**：媒體檔含正確 EXIF/時間/GPS 資訊 + `EXIF合併成果報告.md`

**注意**：時間寫入 `+00:00`，mtime 即 UTC epoch 可用 `os.stat` 驗證；報告統計數字因帳戶而異，需重新計算。

**[回到目錄](#目錄)**

---

## 17. video-class-pipeline — 課程影片分析管線

**用途**：批式處理一系列課程錄影（Google Meet / YouTube 直播畫面），產出可分析的成品（畫面 OCR、Whisper 語音轉錄、逐分鐘交叉比對、關鍵幀 PDF），並支援單次影片編輯（裁黑邊、2 倍速），以 RTX 5080 GPU 編碼。

**適用時機**：使用者要求「分析課程影片」、「處理 YouTube 課程直播錄影」、「畫面 OCR + Whisper 轉錄 + 逐分鐘對照」、「關鍵幀 PDF」、「影片裁切 + 2 倍速」。

**前置需求**（Windows、RTX 5080）：
- Python venv：torch（CUDA）、whisper、easyocr、opencv-python、Pillow、yt-dlp
- ffmpeg/ffprobe（winget `yt-dlp.FFmpeg`）
- NVENC 編碼器：`h264_nvenc`、`hevc_nvenc`、`av1_nvenc`

**運作流程**（Workflow A 批式分析）：
1. 編輯 `pipeline/videos.py` 填入 `{name, url, id}`
2. `download_videos.py <idx>` 依序下載（可續跑）；`verify_downloads.py` 驗證
3. 每支影片 `process_video.py <idx>`：每 10 秒擷幀 → EasyOCR（GPU）→ 音訊 16k → Whisper medium zh（CUDA）→ 逐分鐘 crossref → 關鍵字時間軸報告 → 關鍵幀 PDF
4. 彙整 `build_summary.py` + `build_all_frames_pdf.py`

**運作流程**（Workflow B 裁黑邊 + 2 倍速）：
1. 以 ffprobe/OpenCV 量測亮度計算裁切邊界（不可用 `cropdetect` 或不目測）；樣本多時點取多數決
2. **兩 pass 分開編碼再 mux**：pass 1 僅影片（crop + `setpts=PTS/2` + `fps=30` + NVENC），pass 2 僅音訊（`atempo=2.0` + AAC），再 `-c copy -shortest` 合併——單一 pass 同時含音訊會截斷 AAC 串流
3. 用 ffprobe 確認兩串流時長皆 ≈ 來源/2，並以影格比對驗證 2x 時序

**關鍵檔案**：`E:\01-Project\2026-07-B-python_ai_tvdi\`（tvdi 課程）與 `E:\01-Project\2026_08_n8n_itri\`（n8n 課程）

**注意**：
- 中文路徑破壞 `cv2.imread` → 用 `np.fromfile` + `cv2.imdecode`
- Whisper zh 會對靜音/雜訊以常見套話幻覺 → 用 HALLU 正則過濾（`点赞|打賞|明镜与点点|Amara\.org|谢谢观看|謝謝觀看|訂閱…|字幕…`）
- GitHub 交叉比對要「零幻覺」：只索引 repo clone 中真實存在的路徑，引用格式 `` `term` → `repo:path` ``
- 關鍵幀 PDF 為每頁一張圖（使用者偏好），以 raw bytes 數 `/Type /Page` 驗證頁數
- **絕不** `git add` videos/analysis 輸出（數百 GB），只提交 `pipeline/`、文件與小成品
- 長時間 GPU 階段（OCR 再接 Whisper）依序執行，勿併行；以 `timeout 7200000` 保護 shell 呼叫

**[回到目錄](#目錄)**

---

## 18. taobao-cost-fill — 淘寶費用計算明細填寫

**用途**：把依序編號的訂單卡片（含商品名稱、實付金額、物流、重量）依序填入既有的「淘寶費用計算明細」Excel 樣板（`*-taobao-淘寶-R0.xlsx`，目標分頁名即日期如 `2026-09-05`），並另存成 `*-R1.xlsx`。

**適用時機**：使用者要求「填寫費用明細」、「費用計算明細填寫」、「填入訂單資料」、「填 R0 存 R1」，或要將訂單卡片（markdown，#01..#NN）寫入 R0 樣板的商品列。

**前置需求**：
- Python 3 + `openpyxl`（安裝於本 skill 專用 venv）

**樣板欄位**（row4 起為商品列）：
- B=項次、C=項目（商品名稱）、D=單價 RMB（實付金額）、H=重量
- E=單價 NTD、G=成本者 **不填**（維持樣板原樣）；F=匯率、I/J/K=分攤/關稅/總費用為公式
- 商品區下方有「達飛運費」行（G=『運費』）與「賴政府關稅」行、合計行（公式勿動）

**填入規則**：
- 依序把卡片 #01..#NN 對應到 row4 起的每一列，同步填 B 項次。
- C=商品名稱、D=實付金額（RMB 數值）、H=重量；卡片有 `台灣 數字` 才填重量，無則留空。
- 樣板可能殘留**上一期的幽靈項次**，填入後清除商品區與運費行之間的殘留項次。
- 存檔為 `*-R1.xlsx`，**不覆蓋 R0**。

**執行**：套用內附 `fill_cost_sheet.py`（`--in`/`--out`/`--sheet`/`--cards`；`--cards` 省略時由 stdin 讀取）。

**產出**：`*-taobao-淘寶-R1.xlsx`（商品區已填妥之明細表）。

**注意**：若樣板分頁眾多（歷史各期），務必指定 `--sheet` 或在檔名含日期以自動辨識；商品筆數須與卡片數一致，並以回讀驗證 C/D/H 與項次對應。

**[回到目錄](#目錄)**

---

## 安裝方式

將任一 skill 資料夾複製到 `~/.config/opencode/skills/<skill-name>/`（或 `.opencode/skills/<skill-name>/`），或直接放入本機 `D:\80-Opnecode\.opencode\skills\` 即可由 opencode 自動載入。

## 授權

全部 skill 均為 **MIT License**。詳見儲存庫根目錄的 `LICENSE`。
