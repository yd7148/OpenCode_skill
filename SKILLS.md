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

## 安裝方式

將任一 skill 資料夾複製到 `~/.config/opencode/skills/<skill-name>/`（或 `.opencode/skills/<skill-name>/`），或直接放入本機 `D:\80-Opnecode\.opencode\skills\` 即可由 opencode 自動載入。

## 授權

全部 skill 均為 **MIT License**。詳見儲存庫根目錄的 `LICENSE`。
