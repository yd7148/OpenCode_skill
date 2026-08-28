---
name: tts
description: 使用 Microsoft Edge 的 edge-tts 將文字轉成高品質語音（Text-to-Speech），支援繁體中文、簡體中文、粵語與多國語言與多種聲音。可將文字轉成 mp3 語音檔，並可調整速率、音量、音調，亦可輸出字幕（WordBoundary/subtitle）。Use when asked to "文字轉語音", "TTS", "產出語音檔", "文字變成聲音", "text to speech", "生成旁白", "voiceover 音檔", or to convert text into spoken audio.
---

# tts — 文字轉語音（edge-tts）

將文字內容轉成語音檔案（.mp3），使用 **Microsoft Edge 的雲端神經語音**（edge-tts）。
不需本機模型，語音品質高，支援繁體中文（正體）等多語系。

## 適用時機
- 使用者要求「文字轉語音」、「TTS」、「產出語音檔」、「把這段文字變成聲音」
- 需要影片旁白 / voiceover 的語音音檔
- 需要朗讀文稿、電子報、字幕的語音版本

## 前置需求
- **Python 3**（本機用 `py` launcher）：`py -3 -m pip install edge-tts`
- **網路連線**：edge-tts 呼叫微軟雲端服務 `speech.platform.bing.com`
- **需要走 Proxy**（本機環境）：呼叫時**務必**帶 `--proxy $env:HTTPS_PROXY`，否則 `getaddrinfo failed`（DNS 無法解析）

## 可用的繁體中文聲音（zh-TW）
| Voice | 性別 | 特色 |
|-------|------|------|
| `zh-TW-HsiaoChenNeural` | 女 | 一般、溫暖 |
| `zh-TW-HsiaoYuNeural` | 女 | 一般、友善（推薦 女聲） |
| `zh-TW-YunJheNeural` | 男 | 一般、友善（推薦 男聲） |

其他語系（節錄）：
- 簡中：`zh-CN-XiaoxiaoNeural`（女）、`zh-CN-YunyangNeural`（男/新聞）
- 粵語：`zh-HK-HiuGaaiNeural`（女）、`zh-HK-WanLungNeural`（男）
- 英語：`en-US-AriaNeural`（女）、`en-US-GuyNeural`（男）

列出全部聲音：
```
py -m edge_tts --list-voices
```

## 基本用法（本機必須帶 --proxy）
將文字轉成 mp3：
```
py -m edge_tts --voice "zh-TW-HsiaoYuNeural" --text "你好，這是語音合成。" --write-media "output.mp3" --proxy $env:HTTPS_PROXY
```

### 從文字檔讀入（長篇文稿）
先將文字存成 UTF-8 純文字檔（例如 `text.txt`）：
```
Get-Content -LiteralPath "text.txt" -Encoding UTF8 -Raw |
  py -m edge_tts --voice "zh-TW-HsiaoYuNeural" --write-media "output.mp3" --proxy $env:HTTPS_PROXY
```
或直接以 file 輸入（edge-tts 支援 `--file`）：
```
py -m edge_tts --voice "zh-TW-HsiaoYuNeural" --file "text.txt" --write-media "output.mp3" --proxy $env:HTTPS_PROXY
```

## 調整語速 / 音量 / 音調
| 參數 | 說明 | 範圍 |
|------|------|------|
| `--rate` | 語速 | `+0%`（預設）、`+10%`（加快）、`-10%`（放慢），範圍約 `-50%` ～ `+50%` |
| `--volume` | 音量 | `+0%`（預設），可 `+50%` / `-50%` |
| `--pitch` | 音調 | `+0Hz`（預設），可 `+50Hz` / `-20Hz` |

例：放慢並加低音調的男聲旁白
```
py -m edge_tts --voice "zh-TW-YunJheNeural" --text "旁白內容。" `
  --rate=-10% --pitch=-10Hz --write-media "narr.mp3" --proxy $env:HTTPS_PROXY
```
> ⚠️ **負值要用 `=` 形式**：`--rate=-10%` / `--pitch=-10Hz`（不要寫 `--rate "-10%"`）。
> 負號開頭的值會被 argparse 誤判成選項 → 報 `argument --rate: expected one argument`。
> 在 PowerShell 中請用 `--rate=-10%`（等號形式）或整個用單引號包起來。

## 同時輸出字幕（WordBoundary）
```
py -m edge_tts --voice "zh-TW-HsiaoYuNeural" --text "字幕測試。" `
  --write-media "a.mp3" --write-subtitles "a.srt" --proxy $env:HTTPS_PROXY
```

## 進階：合併旁白
- 若需把多段文字合成一支音檔，可對多個 mp3 用 ffmpeg concat：
```
ffmpeg -f concat -safe 0 -i "list.txt" -c copy "merged.mp3"
```
（`list.txt` 每列一行 `file 'seg.mp3'`）
- 若需字幕（.srt）與語音對齊，使用 `--write-subtitles` 產出 WordBoundary 字幕，再以 ffmpeg 燒錄
- 若主要是做 HyperFrames 影片配音，可改走 `media-use` skill（HeyGen / 本機 Kokoro），本 skill 純做「文字→語音檔」的快速方案

## 重要陷阱
- **一定要帶 `--proxy $env:HTTPS_PROXY`**：本機在 Fortinet proxy 之後，edge-tts 的 WebSocket 合成端點 `speech.platform.bing.com` 無法直接解析（`socket.gaierror: [Errno 11001] getaddrinfo failed`）。帶 proxy 即可正常合成。（`--list-voices` 不受影響，但合成必失敗。）
- **負值參數要用 `=` 形式**：`--rate=-10%`、`--pitch=-10Hz`。負號開頭會被 argparse 當成選項而報錯（見上節）。
- **中文編碼**：`--text` 直接傳中文在 PowerShell 有時會破碼，長文稿**建議用 `--file`** 讀 UTF-8 檔案較穩。
- **需網路**：edge-tts 是雲端服務，離線不可用。
- **輸出格式**：目前 `--write-media` 輸出的預設封裝是 mp3（audio-24khz-48kbitrate-mono-mp3）。

## 產出
- `<名稱>.mp3`（語音檔）
- 選用 `<名稱>.srt`（WordBoundary 字幕）
