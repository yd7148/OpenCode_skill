---
name: on24-video-download
description: 下載 ON24 線上研討會活動（event.on24.com）的影片、投影片與字幕，並從下載的主影片自動提取「投影片 PDF / 投影片影片 / 時間軸摘要」。涵蓋公開媒體組態 API、download/CDN URL 構造、Fortinet Proxy + curl 下載要點、分段並連加速（含 2.7GB > Int32 溢位的關鍵 bug）、M3U8/VTT 字幕、驗證流程，以及以 ffmpeg 抽幀 + perceptual hash + RapidOCR 製作投影片交付物。Use when asked to "下載 ON24 影片", "下載研討會影片", "on24 video download", "從 ON24 下載", "ON24 投影片提取", "analyze/look at this event.on24.com console URL", or to fetch media/subtitles from an ON24 event console.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: on24-media-download-and-slide-extraction
  languages: zh-TW
---

# ON24 活動影片下載與投影片提取

將 ON24 研討會（例如 Microsoft Agent-a-thon / Frontier Transformation Week 的 simulive 活動）的
影片、投影片、字幕全部抓到本機，並可從主影片自動抽出「投影片 PDF / 投影片影片 / 時間軸摘要」。

## WHEN TO USE

- 使用者提供 `https://event.on24.com/event/view/...?eventid=XXXXXXX&key=YYYY...&eventuserid=ZZZ` 的 console URL，要求下載「MEDIA PLAYER 影片」或「Slide 投影影片」。
- 使用者要求「從主影片抓投影片頁面」、「做投影片 PDF / 投影片影片」。

## 環境特性（本機已驗證）

- 所有外網連線走 Fortinet 代理 `http://tpisa:80`，為 MITM 代理解密。
  - shell (`powershell`) 的 DNS 解析不到 `event.on24.com`/`wccdownload.on24.com` → 不能用 PowerShell 的 `Invoke-WebRequest` / .NET HttpClient 直連。
  - **必須用 curl.exe 並加 `--proxy http://tpisa:80 --ssl-no-revoke`**（不加 `--ssl-no-revoke` 會因 schannel 憑證撤銷檢查失敗）。
  - Python 直連 HTTPS 同樣會 SSL 驗證失敗；一律走 curl，或給 Python 環境 `verify=False` / 公司 CA。
- 重要檔案/工具：
  - ffmpeg / ffprobe：`C:\Users\N000149839\ffmpeg\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe`（另有 `C:\Users\N000149839\opencode-tools\ffmpeg.exe`）
  - Python 環境（含 RapidOCR、Pillow、reportlab、PIL）：
    - `D:\80-Opnecode\workspace\_maidate_work\venv\Scripts\python.exe`（reportlab 5.0、rapidocr-onnxruntime 1.2.3）
  - 別用 `C:\Users\N000149839\AppData\Local\Temp\opencode` 存重要中介檔（會被清掉）；工作檔放專案下 `slides_work\` 或 `_v2t_work\`（見 video2text skill）。

## STEP 0 ─ 解析 console URL → eventId / key / eventuserid

範例：
`.../event/view/71/platform/console/index.htm?eventid=5413047&key=1F4E1D1468756AE7AE3D0718E217244B&sid=...&eventuserid=848596397`
只需 `eventid` 與 `key`（eventuserid 選用）。

## STEP 1 ─ 抓公開媒體組態 JSON（不必登入）

```powershell
curl.exe --ssl-no-revoke -s --proxy http://tpisa:80 `
  "https://event.on24.com/apic/utilApp/EventConsoleCachedServlet?eventId=5413047&displayProfile=player&key=1F4E1D1468756AE7AE3D0718E217244B&contentType=A" `
  -o on24_event5413047.json    # ~706 KB
```
JSON 重點欄位（id=5413047 範例）：`mediaUrlInfo[]`
- **主影片地址**：`mediaUrlInfo[].href`（有時是相對路徑），記錄 `bytes`（必須與 Content-Length 一致）、`width/height`、`duration`（毫秒）、`iscmaf`。
- `vtt[]`：各語言字幕相對路徑（含 `English`、`Chinese_Simplified`、`Chinese_Traditional`…）。
- `slide[]` / `documents/slidepdf[]`：實體投影片檔（通常只有 housekeeping 開場頁）。
- `chapter[]`：smart chapters（章節時間點）。
- `images[]`：UI 圖示，不是投影片。

**重要認知（finetuning 時查證過）**：這類 simulive 事件通常**只有一個影片串流**（代號如 `fhvideo1`），
它本身就是「投影片＋螢幕分享」的完整錄影。Console 的 Media Player 與 Slides 窗格來源是同一支影片，
**沒有第二支獨立「投影片影片」**。可用 ffmpeg 抽幀 + OCR 驗證（見 STEP 4）。若使用者堅持投影片是另外的內容，
先抽幀證明／或說明後再決定是否做 STEP 4 的提取。

## STEP 2 ─ 構造下載 URL（三者皆可，皆回 206 + Accept-Ranges）

主影片相對路徑範例：`54/13/04/7/rt/1_fhvideo1_1788354760449.mp4`
```powershell
# 正式來源（推薦）
https://event.on24.com/media/news/corporatevideo/events/54/13/04/7/rt/1_fhvideo1_1788354760449.mp4
# 其他可用主機（成效相同，都受同樣快取/限速）
https://event.on24.com/media/cv/events/54/13/04/7/rt/1_fhvideo1_1788354760449.mp4
https://wccdownload.on24.com/media/cv/events/54/13/04/7/rt/1_fhvideo1_1788354760449.mp4
```
小資源（字幕/投影片）放在 `https://event.on24.com/event/54/13/04/7/rt/1/...`（相對路徑前綴拼接），例如：
```powershell
https://event.on24.com/event/54/13/04/7/rt/1/vtt/mediaplayer/5413047_English_1F4E1D1468756AE7AE3D0718E217244B.vtt
https://event.on24.com/event/54/13/04/7/rt/1/slide/slide/1_AAE547AA20C43E6CE72FCD59FF44AF3E.jpg
https://event.on24.com/event/54/13/04/7/rt/1/documents/slidepdf/on24_housekeeping_slide_level_1.pdf
```
字幕的其他語言：檔名中的 `English` 換成 `Arabic`、`Chinese_Simplified`、`Chinese_Traditional`、`Korean`、`Japanese`…（以 JSON `vtt[]` 的檔名為準）。

## STEP 3 ─ 下載主影片（分段並連 + 續傳）── 內含關鍵 Bug 教訓

### 3.1 不要用單一連線
- 單一連線被 CDN 限速到 ~0.3 MB/s（≈影片實況位元率 2.0 Mbps），3 小時 / 2.7GB 要 2 小時以上。
- 並連測試結論：8 條連線 ≈ 1.2 MB/s；4 條 ≈ 1.3–1.4 MB/s；24 條掉到 ~0.9 MB/s
  → **有 per-IP 上限 ~1.2–1.4 MB/s，最佳併連數約 4–8**。

### 3.2 分段下載器（可續傳，已驗證跑完 2.7GB）
腳本：`C:\Users\N000149839\AppData\Local\Temp\opencode\dl_seg.ps1`（結束時會 `copy /b` 併檔 + 驗證大小）。
要點（每一版都請注意）：
- 64 段、4–8 個 worker；worker w 依序拿 segment `w, w+n, w+2n, …`（不需共享佇列）。
- 每段單獨 `curl.exe --ssl-no-revoke -sS --proxy http://tpisa:80 -r <start>-<end> -o part_XXX.tmp`，
  完成後長度比對（`$expect = $end - $start + 1`）再改名 `part_XXX.bin`；`.bin` 已存在且大小正確就 skip（=續傳）。
- 併檔：`cmd /c copy /b part_001.bin+part_002.bin+... out.mp4`，再驗 `Length -eq $total`。

#### ⚠️ 最重要的坑：2.7GB 超過 Int32！
- `[math]::Min($start+$sg-1, $tot-1)` 在 $tot≈2.7×10⁹ 時會 **Int32 溢位拋錯**，`$end` 變空，
  實際 curl 參數變成 `-r 0-`（開區間）→ curl 從 byte 0 一路下載到檔尾（等於整檔再抓一遍）→ 看似卡住不長。
- **修正**：全部用 `[int64]` 計算：
  ```powershell
  $start = [int64]$idx * $sg
  $rawEnd = $start + [int64]$sg - 1
  $top    = [int64]$tot - 1
  $end    = if ($rawEnd -gt $top) { $top } else { $rawEnd }
  ```
- 驗證監看：`-r` 必須是完整閉區間（如 `-r 42805489-85610977`），不要出現 `-r xxx-`。

### 3.3 驗證成品
```powershell
ffprobe -v error -show_entries format=duration,size,bit_rate -show_entries stream=codec_type,codec_name,width,height out.mp4
# 2026-09-18 實例：h264 1280x720 + aac，duration 10800.000 s，size = 2739551292（與 Content-Length/JSON bytes 一致）2.03 Mbps
```
抽末段一幀 OCR 看是否能解碼到底。

## STEP 4 ─ 從主影片自動提取投影片（PDF / 影片 / 時間軸）

前置工具：ffmpeg + venv python（RapidOCR + reportlab）。全程只在本機跑。

### 4.1 抽幀
```powershell
ffmpeg -y -i <影片>.mp4 -vf fps=1/5 -q:v 4 -threads 4 "slides_work\frames\f_%06d.jpg"   # 每5秒1張；3h→2160張
```
背景跑（約 15–25 分鐘）。frame i → 時間 (i-1)×5 秒。

### 4.2 Perceptual hash 找「換頁」與去重
- 每張縮到 9×8 灰階算 dHash(64bit)；相鄰 frame 的漢明距離當變化量。
- 連續相似的穩態畫面會被併成同一「內容段落」；每段落選代表幀（建議段首+1 幀或最清晰幀）。
- 門檻試值：dHash 距離 ≥ 8–10 視為換頁；小範圍滑鼠游標抖動會被 hash 吃掉。

### 4.3 OCR 每張代表幀（RapidOCR，venv）
```python
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR(); result, _ = ocr("slide.jpg")
# result = [[box, text, score], ...]  ← 3 個元素，text 是元素2、score 是元素3，注意與舊版順序相反
```
- 產出每張投影片的 OCR 文字 → 當 PDF/時間軸的標題與內容。
- 使用 `ProcessPoolExecutor(max_workers=8)` 並把結果存 json checkpoint（沿用 video2text `run_ocr.py` 的寫法）。

### 4.4 交付物
- **投影片 PDF**：reportlab（venv reportlab 5.0）A4 橫式，1 張/頁，含 編號、開始/結束時間、持續秒數、OCR 文字。
- **投影片影片**：用 ffmpeg concat demuxer 依「每張投影片實際停留秒數」把代表幀連成 slideshow：
  ```
  file 'f_000042.jpg'
  duration 35
  file 'f_000119.jpg'
  duration 48
  ...
  file 'f_002160.jpg'
  ```
  （每筆 `duration` 後接 `file`，最後一張不必 duration）再 `-f concat -safe 0 -i list.txt -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p out_slides.mp4`
- **時間軸摘要 md**：表格（編號｜開始｜持續｜OCR 文字前段｜代表幀檔名）。

## NOTES / LIMITS

- 沒有使用者 session cookie 時，console 的 `console/init` API 回 `418 (Access Restricted)`（Akamai 擋）→ 無法從前端觀察 console 實際 network calls。
- Chrome 執行中時 `...\Default\Network\Cookies` 被獨佔鎖定（`FileShare`/sqlite 都無法讀），別在 Chrome 使用中嘗試取 cookie。
- ON24 CDN 對單一 IP 限速約 1.2–1.4 MB/s，再多併連不會更快（反而變慢）。
- 分公司 CA / 代理環境下，`curl --ssl-no-revoke` 是標配；換機器時要改代理位址與憑證處理。