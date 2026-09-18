---
name: yt-batch-download
description: 批次下載 YouTube 影片（1080p 最高畫質），支援自訂檔名、cookies 匯入、SSL 修復、JS runtime 設定。Use when asked to "下載YouTube影片", "批次下載YT", "download YouTube videos batch", "下載課程影片", or to batch-download a list of YouTube URLs.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: youtube-batch-download
  languages: zh-TW
---

# yt-batch-download — YouTube 批次下載（1080p）

批次下載多支 YouTube 影片，1080p 最高畫質，自訂檔名，支援 livestream (`youtube.com/live/ID`) 與一般影片 (`youtube.com/watch?v=ID`)。

## When to use
- User asks 下載 YouTube 影片 / 批次下載 YT / download YouTube videos batch / 下載課程影片
- 需要從 GitHub README 或其他來源取得 URL 列表並批次下載
- 需要自訂輸出檔名（依日期、時段等）

## 前置需求

| 工具 | 安裝方式 | 說明 |
|------|----------|------|
| Python 3.13+ | `py` launcher | Windows 已安裝 |
| yt-dlp | `py -m pip install yt-dlp` | YouTube 下載核心 |
| ffmpeg + ffprobe | 下載 essentials build 並放到 `bin/` 目錄 | 合併 video+audio |
| deno | 下載 `deno-x86_64-pc-windows-msvc.zip` 並放到 `bin/` 目錄 | JS runtime，解決 YouTube n challenge |
| browser_cookie3 | `py -m pip install browser_cookie3` | 從 Chrome 匯出 cookies（繞過 403） |

### 工具目錄結構
```
bin/
  deno.exe
  ffmpeg.exe
  ffprobe.exe
```
放在固定路徑（如 `C:\Users\<user>\AppData\Local\Temp\opencode\bin\`），腳本透過 `--ffmpeg-location` 和 `--js-runtimes deno` 指定。

## 關鍵設定（缺一不可）

YouTube 2025 年後加強反爬蟲，以下參數 **全部都需要**：

```powershell
py -m yt_dlp `
  --no-check-certificates `
  --no-cache-dir `
  --cookies "$COOKIES_FILE" `
  -f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]" `
  --merge-output-format mp4 `
  --ffmpeg-location "$BIN_DIR" `
  --js-runtimes deno `
  --remote-components ejs:github `
  -o "$OUTPUT_PATH" `
  "$YOUTUBE_URL"
```

### 參數說明
| 參數 | 作用 | 為什麼需要 |
|------|------|-----------|
| `--no-check-certificates` | 跳過 SSL 驗證 | Windows Python SSL 憑證問題 |
| `--cookies` | 使用瀏覽器 cookies | YouTube 需要登入狀態才能下載高畫質 |
| `-f bestvideo[height<=1080]...` | 選擇 1080p mp4 + m4a audio | 確保最高畫質 |
| `--merge-output-format mp4` | 合併為 mp4 | ffmpeg 分離下載 video+audio 後合併 |
| `--ffmpeg-location` | 指定 ffmpeg 路徑 | ffmpeg 不在 PATH 上 |
| `--js-runtimes deno` | 使用 deno 解決 n challenge | YouTube 需要 JS runtime |
| `--remote-components ejs:github` | 從 GitHub 下載 challenge solver | deno 本身不夠，還需要 solver script |

### ⚠️ deno 必須在 PATH 上（2026-08-25 實測）

只給 `--js-runtimes deno` 而 bin 目錄不在 `$env:PATH` 時，
verbose log 會顯示 `[debug] JS runtimes: none`、
`n challenge solving failed`、最後只剩 storyboard（Only images are available）。
**每次呼叫前先注入 PATH**：

```powershell
$env:PATH = "C:\Users\<user>\AppData\Local\Temp\opencode\bin;" + $env:PATH
py -m yt_dlp ... --js-runtimes deno --remote-components ejs:github ...
```

成功的訊號：log 出現 `[youtube] [jsc:deno] Solving JS challenges using deno`
與 `Downloading challenge solver lib script from https://github.com/yt-dlp/ejs/...`。
驗證方式：先跑 `--list-formats`，看到 video format ID（如 18/22/137）而非只有 sb0-sb3。

降級備援：n-challenge 若仍失敗，改抓 `-f 18`（360p mp4 單檔）通常不受影響；
短片分析用途足夠。

## Cookies 匯入（繞過 403）

YouTube 會對無 cookies 的請求回傳 403 Forbidden。需要用 `browser_cookie3` 從已登入的 Chrome 匯出：

### 匯出腳本
```python
import browser_cookie3
import http.cookiejar
import os

cookies_path = os.path.join(os.environ["TEMP"], "yt_cookies.txt")
cj = http.cookiejar.MozillaCookieJar(cookies_path)
chrome_cj = browser_cookie3.chrome(domain_name=".youtube.com")
for cookie in chrome_cj:
    cj.set_cookie(cookie)
cj.save(ignore_discard=True, ignore_expires=True)
```

### 注意事項
- Chrome 必須在執行中（cookies 才有解密金鑰）
- 匯出的 cookies 檔為 Netscape 格式（`yt_cookies.txt`）
- 若 Chrome cookie DB 被鎖定（`Could not copy Chrome cookie database`），用 `browser_cookie3` 的 shadowcopy 功能可繞過
- cookies 有時效，過期需重新匯出

### ⚠️ 403 的兩種情況（2026-09-17 實測，務必分辨）

| 症狀 | 原因 | 解法 |
|------|------|------|
| `--list-formats` **成功**列出 137/140，但下載時才 `HTTP Error 403` | **cookies 已過期**（最常見） | 重新執行 cookies 匯出腳本再下載 |
| 剛下載完數支、接著連線失敗/403 | YouTube 暫時性反爬蟲（大量連續下載） | 等待數分鐘後重試同一個 URL 即可 |

判準：**「清單成功、下載 403」= cookies 問題**，先重匯 cookies；重匯後仍失敗才當作暫時性限制。
補下失敗檔用獨立小腳本（只含缺的那幾支）比重跑整批快；skip-if-exists 邏輯讓同一個腳本可安全重跑。

## 直播（LIVE）進行中的影片：`--live-from-start`

課程當天若影片仍在直播（`is_live=True`），一般 `-f 137+140` 會失敗或只抓到極短片段。
改用 `--live-from-start` 從頭錄到直播結束，yt-dlp 會邊抓邊寫 `.part-Frag*`，結束後**自動合併**成
完整的 `.mp4`（log 出現 `[Merger] Merging formats into "....mp4"` → `OK` → `ALL_DONE`）。

```powershell
py -m yt_dlp ... --live-from-start --wait-for-video 60 -o "$OUT" "$LIVE_URL"
```

- 進行中：目錄只有 `"<name>.f137.mp4.ytdl"`、`"<name>.f140.mp4.ytdl"` 與大量 `*-Frag*` 暫存；
  **尚無** `<name>.mp4`，此時不要拿去後處理。
- 已結束：出現最終 `<name>.mp4`（用 ffprobe 確認時長/解析度），`.part`/`-Frag` 清空。
- 因此**批次流程要把 LIVE 影片排除**（跳過仍在直播者），另外用這支腳本錄；錄完再併入後處理。
- `WARNING: Unknown codec unknown` 可忽略。

## 批次下載腳本模板

```python
import subprocess
import os

DOWNLOAD_DIR = r"<下載目錄>"
BIN_DIR = r"<bin目錄>"
COOKIES = r"<cookies檔案路徑>"

env = os.environ.copy()
env["PATH"] = BIN_DIR + os.pathsep + env.get("PATH", "")

videos = [
    ("檔名1", "https://youtube.com/live/VIDEO_ID1"),
    ("檔名2", "https://www.youtube.com/watch?v=VIDEO_ID2"),
    # ... 更多
]

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

for i, (name, url) in enumerate(videos, 1):
    output_path = os.path.join(DOWNLOAD_DIR, f"{name}.mp4")
    if os.path.exists(output_path) and os.path.getsize(output_path) > 1024*1024:
        print(f"[{i}/{len(videos)}] SKIP: {name} (already exists)")
        continue

    print(f"[{i}/{len(videos)}] Downloading: {name}")

    cmd = [
        "py", "-m", "yt_dlp",
        "--no-check-certificates",
        "--no-cache-dir",
        "--cookies", COOKIES,
        "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "--merge-output-format", "mp4",
        "--ffmpeg-location", BIN_DIR,
        "--js-runtimes", "deno",
        "--remote-components", "ejs:github",
        "-o", output_path,
        url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode == 0:
        print(f"  OK: {name}.mp4")
    else:
        print(f"  FAILED: {result.stderr[-200:]}")
```

## URL 格式支援

| 格式 | 範例 | 說明 |
|------|------|------|
| 直播/重播 | `https://youtube.com/live/VIDEO_ID` | livestream 回放 |
| 一般影片 | `https://www.youtube.com/watch?v=VIDEO_ID` | 標準 YouTube 影片 |
| 短連結 | `https://youtu.be/VIDEO_ID` | 短網址 |

## 檔名命名慣例

根據來源 README 的標題命名，例如：
- `2026_07_03_上午.mp4`
- `2026_07_03_下午.mp4`
- `2026_07_24_早上.mp4`（注意：有些用「早上」有些用「上午」，保留原始命名）

## 環境問題與解法

| 問題 | 原因 | 解法 |
|------|------|------|
| `SSL: CERTIFICATE_VERIFY_FAILED` | Windows Python SSL 憑證鏈不完整 | `--no-check-certificates` |
| `Unable to download API page` | 同上 | `--no-check-certificates` |
| `HTTP Error 403: Forbidden` | YouTube 反爬蟲，無 cookies | `--cookies` + `browser_cookie3` |
| `No supported JavaScript runtime` | 缺少 JS runtime | `--js-runtimes deno` |
| `n challenge solving failed`（log: `JS runtimes: none`） | deno 不在 PATH 上 | 呼叫前 `$env:PATH = "<bin>;" + $env:PATH`，詳見上方「deno 必須在 PATH 上」 |
| `Only images are available` | n-challenge 未解，只剩 storyboard | 先修 PATH 重跑；或降級 `-f 18`（360p 單檔） |
| `Requested format is not available` | 格式不可用 | 改用 `bestvideo+bestaudio` 或不指定格式 |
| `Could not copy Chrome cookie database` | Chrome 鎖定 cookie DB | 用 `browser_cookie3` 的 shadowcopy，或重試 |
| ffmpeg not found | ffmpeg 不在 PATH | `--ffmpeg-location` 指定完整路徑 |
| 清單 OK 但下載 403 | cookies 過期 | 重跑 cookies 匯出腳本（見「403 的兩種情況」） |
| 直播影片下載失敗/只抓到片段 | 影片仍在直播（`is_live=True`） | 用 `--live-from-start` 錄到結束，不要混進 VOD 批次 |

## 批次系列實測筆記（2026-09-17）

一支 13 集課程系列（12 支 VOD + 1 支當天 LIVE）的實務結論：

- **每支一支腳本、循序下載**，內建 `skip-if-exists`（檔案 >1MB 就跳過）→ 中斷可直接重跑。
- 檔名主控台顯示為 mojibake 是**顯示層**問題，實際檔名是正確 UTF-8；用 Python `os.listdir`
  傾印 `_names.txt` 或直接 `ffprobe` 該檔即可確認，不必改檔名。
- 用 **Python 子程序**（`subprocess.run(..., env=env)`）比 PowerShell 字串拼命令可靠，
  尤其檔名/路徑含中文時；`env["PATH"] = BIN_DIR + os.pathsep + env["PATH"]` 一次注入 deno。
- 下載完成後以 ffprobe 逐支驗證 `1920x1080` 與時長（非 0、非片段）。
- **背景啟動**：`Start-Process -RedirectStandardOutput` 啟動長時間下載時，工具可能回報
  `Unknown: ChildProcess.kill`，但程序其實已啟動；重複下指令會誤啟**第二個**平行程序，
  請先 `Get-CimInstance Win32_Process -Filter "Name='python.exe'"` 確認只有一個。
- 下載成品驗證通過後，才進入裁切/2 倍速後處理（見 `video-2x-speed`、`video-class-pipeline`）。

## 估算下載時間與大小

- 1080p30 影片：約 **300-700 MB/小時**（依內容複雜度）
- 下載速度：視網路，一般 **5-30 MB/s**
- 22 支課程影片（各約 2-3 小時）：合計約 **10-15 GB**

## Deliverables checklist
- [ ] 所有影片皆為 1080p mp4 格式
- [ ] 檔名與來源 README 標題一致
- [ ] 無 .part / .temp 殘留檔案
- [ ] 在下載目錄放置 README.md 說明檔案
