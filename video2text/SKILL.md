---
name: video2text
description: Analyze recorded meeting / online-conference videos to produce a bilingual (Traditional Chinese) markdown report plus a key-frame PDF. Extracts frames every 10s and runs RapidOCR on them, transcribes the audio with faster-whisper large-v3-turbo (CPU int8, recommended) or whisper-large-v3 via OpenVINO (Intel GPU, legacy), converts to Traditional Chinese with OpenCC, then cross-compares OCR slide text vs. speech into a timeline table with summary analysis. Handles speed-changed videos (e.g. 2x) by restoring audio tempo and aligning both timelines. Use when asked to "分析影片", "影片轉文字", "畫面與語音重點摘要", "OCR + whisper 比對", or to analyze a .mp4 recording into markdown/PDF deliverables.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: video-analysis
  languages: zh-TW
---

# video2text — 影片分析（畫面 OCR × 語音 Whisper → Markdown + PDF）

Analyze a recorded meeting / online conference video into two deliverables, placed in the
user's project folder (e.g. `D:\80-Opnecode\Projects\<project>\`):

1. A Traditional Chinese markdown report: 分析方法 / 影片概述 / 時間軸重點摘要（OCR×Whisper 比對表）/ 重點知識點解析 / 外部資料交叉比對 / 幻覺偵測 / 驗證 / 結論 / 附註.
2. A key-frame PDF (screenshots of representative slides with time + caption).

## When to use
- User says 分析影片 / 影片轉文字 / 畫面與語音重點摘要 / OCR 與語音比對 / 會議錄影分析, or hands you a `.mp4` to summarize visually + acoustically.
- The pipeline targets **local offline inference** (no cloud APIs), using **Intel GPU where possible** (OpenVINO).

## Prerequisites (already provisioned)
- Python 3.13: `C:\Users\N000149839\AppData\Local\Programs\Python\Python313\python.exe` (launcher `py`).
- **yt-dlp** installed as a pip package → run as `py -m yt_dlp ...` (NOT `yt-dlp`; the .exe is not on PATH).
- Analysis venv `D:\80-Opnecode\workspace\_maidate_work\venv` (pip `venv\Scripts\python.exe`).
  Alternative: `D:\Downloads\2026-08-10-video2text\_maidate_work\venv` (if it exists).
  Packages: openvino 2026.3.0, openvino-genai 2026.3.0.0, **optimum-intel 1.27.0 (must stay 1.27.x, see gotchas)**, transformers 4.57.x, onnxruntime 1.28, rapidocr-onnxruntime 1.2.3, opencv-python, pillow, numpy, reportlab 5.0, onnx.
- ffmpeg: `C:\Users\N000149839\opencode-tools\ffmpeg.exe` (primary, not on PATH — always use full path).
  - Fallback: `D:\Downloads\2026-08-10-video2text\_maidate_work\ffmpeg_pkg\ffmpeg-9.0-essentials_build\bin\ffmpeg.exe`
  - Fallback binary from `imageio-ffmpeg` package (global Python): `C:\Users\N000149839\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe`; the file is NOT named `ffmpeg.exe`, so **copy it to `C:\Users\N000149839\opencode-tools\ffmpeg.exe`** for tools that require that filename.
- Whisper model exported to OpenVINO IR (stateful, fp16): `D:\80-Opnecode\workspace\_maidate_work\whisper-large-v3-ov2`.
- Whisper processor cache: `D:\80-Opnecode\workspace\_maidate_work\whisper-processor-cache` (downloaded with `verify=False`).
- Source PT checkpoint: `_maidate_work\whisper-large-v3-pt` (pytorch_model.bin, only needed to re-export).
- **ASR venv (RECOMMENDED, used 2026-08)**: `<project>\_v2t_work\venv_fw\Scripts\python.exe`
  - faster-whisper 1.2.1 (CTranslate2), opencc-python-reimplemented (s2twp), pillow, rapidocr-onnxruntime.
  - Models (download once with `huggingface_hub.snapshot_download`, then set `HF_HUB_OFFLINE=1`):
    - `fwhisper-large-v3-turbo` (Systran/faster-whisper-large-v3-turbo, fp16 → run int8 CPU) — **primary, best quality**.
    - `fwhisper-large-v3` (Systran/faster-whisper-large-v3, ~2.9 GB) — alternative if turbo unavailable; slower but same quality.
    - `fwhisper-small` (Systran/faster-whisper-small, ~461 MB) — **unreliable on this machine** (crashes repeatedly).
    - `fwhisper-tiny` (Systran/famer-whisper-tiny, ~72 MB) — **fallback only**; ~88% hallucination rate, prompt echo pervasive.
  - Measured RTF on this machine (CPU int8): **1.4–9.6x** (≈3x average) — a 3-hour class transcribes in ~1 hour of wall time across several batched shell calls.
  - TVDI 2026-07-03 下午 (3h13m, 97 units): RTF 1.6–4.3x, ≈1 unit/min → ~75 min wall as one background process.

## Pipeline (follow in order)

### 0. Video acquisition — download a YouTube video (only when a URL is supplied)
Use yt-dlp through Python. Three hard requirements learned in this environment:
- **Always pass `--no-check-certificates`** — the Fortinet proxy intercepts HTTPS and its CA fails Python's cert
  verification (`SSL: CERTIFICATE_VERIFY_FAILED`), otherwise the very first `-F` call fails.
- **yt-dlp must be able to find `ffmpeg.exe`** to merge separate video/audio streams; point
  `--ffmpeg-location` at the copied binary (prereq above).
- **Put the tools bin dir on `$env:PATH` before calling yt-dlp** (2026-08-25) — otherwise
  `[debug] JS runtimes: none` → `n challenge solving failed` → only storyboards available:
  ```powershell
  $env:PATH = "C:\Users\N00014~1\AppData\Local\Temp\opencode\bin;" + $env:PATH
  py -m yt_dlp --no-check-certificates --cookies $COOKIES `
    --extractor-args "youtube:player_client=web" `
    --ffmpeg-location "<bin>" --js-runtimes deno --remote-components ejs:github `
    -f "best[height<=720]/best" -o $OUT "URL"
  ```
  Success marker in log: `[youtube] [jsc:deno] Solving JS challenges using deno`.
  Fallback if n-challenge still fails: `-f 18` (360p single file, fine for short promo clips).
  Cookies via browser_cookie3 export (see yt-batch-download skill); android client rejects cookies.

**Short-video variant (<3 min promo/Shorts, e.g. 2026_06_playwirght 除霉劑 clip)**: download
`best[height<=720]`, extract frames at `fps=1/2` (~65 frames for 2min), OCR all in one
ProcessPoolExecutor run, and transcribe the whole wav in a single faster-whisper call
(see `<project>\_v2t_work\run_asr.py` pattern — no unit checkpointing needed at this length).
Whole pipeline ≈ 5–8 min including OCR.

```powershell
py -m yt_dlp --no-check-certificates --ffmpeg-location "C:\Users\N000149839\opencode-tools\ffmpeg.exe" `
  -F "URL"                                        # list formats first
py -m yt_dlp --no-check-certificates --ffmpeg-location "C:\Users\N000149839\opencode-tools\ffmpeg.exe" `
  -f "299+140" --merge-output-format mp4 -o "%(title)s [%(id)s].%(ext)s" "URL"   # 1080p60 H.264 + best m4a audio
```
- 1080p60 H.264 stream id is typically **299** (1920x1080/60, ~322 MiB for 32 min); best AAC audio **140** (~129k). Merge with ffmpeg into one `.mp4` (or `-f "bestvideo[height<=1080][fps<=60]+bestaudio/best"`).
- Download into the target folder; deliverable filename comes from `%(title)s`.
- Re-running the same command resumes from existing `.f299.mp4`/`.f140.m4a` parts and re-merges — safe to retry.
- Verify result with ffmpeg `-i`: expect `h264 1920x1080 60 fps` + `aac 44100 Hz`.
- Warn: `No supported JavaScript runtime` is harmless for normal downloads; formats list may be slightly reduced.

**HLS fallback** (when yt-dlp returns m3u8-only formats or proxy blocks direct download):
Fortinet proxy blocks googlevideo.com m3u8 segments (403 Forbidden). Use Python urllib to download:
```powershell
# Step 1: Get m3u8 URL from yt-dlp (use android_vr client for HLS)
py -m yt_dlp --no-check-certificates `
  --extractor-args "youtube:player_client=android_vr" `
  -g "URL"   # returns m3u8 playlist URL

# Step 2: Python script downloads all segments via urllib (works through proxy)
# - Parse m3u8 for segment URLs (lines starting with http after #EXTINF)
# - ThreadPoolExecutor(max_workers=8) parallel download
# - Each segment → seg_XXXXX.ts in segments/ folder
# - Resume-safe: skip existing non-empty .ts files

# Step 3: Create concat list (BOM-free!) and merge with ffmpeg
[System.IO.File]::WriteAllLines("$work\concat_list.txt", $lines, (New-Object System.Text.UTF8Encoding($false)))
& $ff -y -f concat -safe 0 -i "$work\concat_list.txt" -c copy "$work\video_full.mp4"
```
- Segments format: TS (MPEG-TS), merged to MP4 (copy codec, no re-encoding).
- ~300-400 MB/hour for 1080p30 HLS.
- If rate-limited (403 after 800+ segments), re-run script with fresh m3u8 URL.

### 0b. Work location — CRITICAL
Do NOT use the OS temp dir (`C:\Users\N000149839\AppData\Local\Temp\opencode`); it gets wiped periodically,
and long-running bash commands there may be killed (you saw a full rebuild needed once). Put ALL working files
under `D:\Downloads\2026-08-10-video2text\_<video>_work\` (or `<project>\_<video>_work\`). Deliverables go directly into
the project folder.

**Single-video project layout (I4.0 class pattern, 2026-08-25)**: when one video is analyzed with PDF cross-referencing:
```
<project>\_v2t_work\
├─ frames\<BASE>\frame_%05d.png       # every 20s (or 10s)
├─ ocr\<BASE>\frame_%05d.json         # per-frame OCR checkpoint
├─ audio\<BASE>_1x.wav                # extracted audio (16kHz mono)
├─ transcript_zh_<BASE>.txt           # merged ASR output
├─ pdf02_<name>.txt                   # extracted PDF text
├─ pdf03_<name>.txt                   # extracted PDF text
├─ ocr_summary_<BASE>.txt             # grouped OCR summary for cross-comparison
└─ venv_fw\                           # Python venv with faster-whisper + rapidocr
```
- OCR can run sequentially (~5s/frame) if parallel workers cause issues; 524 frames ≈ 44 min.
- PDF extraction uses `pdfplumber` — simple `page.extract_text()` per page.

**Multi-session course project layout (TVDI pattern, proven 2026-07/08)**: when one project folder holds MANY class
recordings, use ONE shared `_v2t_work\` keyed by a BASE name (`<date>_<上午|下午>`), not one workdir per video:

```
<project>\_v2t_work\
├─ frames\<BASE>\f_%05d.jpg      # 每 10 秒 1 張（2x 影片時間軸）
├─ ocr\<BASE>\f_XXXXX.json       # per-frame OCR checkpoint（可續跑）
├─ asr\<BASE>\u_XXXX.json        # per-unit ASR checkpoint（可續跑）
├─ audio\<BASE>_1x.wav           # atempo 還速後音訊
├─ transcript_zh_<BASE>.txt / slide_groups_<BASE>.txt / merged_timeline_<BASE>.txt   # ← 加 BASE 後綴，避免互相覆蓋
└─ venv_fw\ \ fwhisper-large-v3-turbo\ \ run_ocr.py \ run_asr.py \ build_merge*.py \ make_pdf*.py
```
- `run_asr.py <BASE> <budget>` 已參數化；`build_merge.py` 原為硬編碼 → 複製成 `build_merge_pm.py` 接受 `argv[1]=BASE`，
  輸出檔名加 `_<BASE>` 後綴。中介檔一律帶 BASE，只有最終 .md/.pdf 放專案根目錄。
- `frames\<BASE>.done` 空白標記檔表示該堂已完成，供快速盤點進度。

### 0c. Crop black bars (if present)
Some videos (especially Google Meet recordings) have black bars on the right side (e.g. participant panel).
Crop BEFORE OCR to improve accuracy and PDF readability.

**Detect black bars** (Python PIL + numpy):
```python
from PIL import Image
import numpy as np
img = Image.open("frame.png")
arr = np.array(img)
mid_y = img.height // 2
brightness = arr[mid_y, :, :].mean(axis=1)
dark_cols = np.where(brightness < 30)[0]
if len(dark_cols) > 0:
    content_width = dark_cols[0]
    print(f"Content: 0-{content_width-1} ({content_width}px), Black bar: {content_width}-{img.width-1}")
```

**Crop with ffmpeg**:
```powershell
$ff = "C:\Users\N000149839\opencode-tools\ffmpeg.exe"
# crop=w:h:x:y — e.g. 1440x1080 from left edge
& $ff -y -i "<video>.mp4" -vf "crop=1440:1080:0:0" `
    -c:v h264_qsv -global_quality 28 -c:a copy "<video>-cropped.mp4"
```
- Audio is stream-copied (`-c:a copy`), no re-encoding.
- Verify: `& $ff -i <cropped>.mp4` → confirm resolution (e.g. 1440x1080).
- Use cropped video for all subsequent steps (audio extraction, frame extraction).

### 1. Extract audio + frames
```powershell
$ff = "<work>\ffmpeg_pkg\ffmpeg-9.0-essentials_build\bin\ffmpeg.exe"
& $ff -y -i "<video>.mp4" -vn -ac 1 -ar 16000 -c:a pcm_s16le "<work>\audio.wav"
& $ff -y -i "<video>.mp4" -vf "fps=1/10" "<work>\frames\frame_%05d.png"
```
- Frame `frame_i` (1-based) ≈ time `t=(i-1)*10` seconds. 359 frames for a 60-min video.
- **Speed-changed source videos (e.g. `-2x.mp4`)**: restore audio to 1x BEFORE ASR, otherwise
  whisper output is garbage:
  ```powershell
  & $ff -y -i "<video>-2x.mp4" -vn -filter:a "atempo=0.5" -ac 1 -ar 16000 -c:a pcm_s16le "<work>\audio_1x.wav"
  ```
  (for an Nx video use `atempo=1/N`; for N>2 chain two atempo filters).
  **TIME-AXIS RULE**: OCR frame times are on the *video* timeline; ASR segment times are on the
  *original* timeline. When merging, divide ASR times by the speed factor (2x video → ASR_t / 2),
  and state both conventions in the report ("本文時間軸以 2x 影片時間標示，原始課堂時間 = ×2").

### 2. OCR all frames (CPU parallel — faster than DirectML on this machine)
- Use `run_ocr.py` pattern: `ProcessPoolExecutor(max_workers=8)`, checkpointed JSON per frame in `ocr\frame_%05d.json`.
- Each worker lazily builds its own `RapidOCR()`; skip frames whose output JSON already exists (resume-safe).
- Apply a watermark filter: drop low-score boxes at screen edges, the meeting-clock labels (`03PM...`, `03P8...`, `03SS...`, `03HM...`, `03HB...`, `0350...`), chat `+N`, truncated name badges (end with `..`/`/..`), brand watermarks (`漢達特/達特/MetaAge`).
- Measured: CPU ~5s/frame vs DirectML ~10s/frame → use CPU. 359 frames ≈ 4–5 min; if killed mid-run, re-run to resume.
- **TVDI project measured pace (1440x1080 frames, 12 workers)**: ~2.1 s/frame effective (≈108–144 frames per
  165 s session) — budget ~5 foreground sessions for a 579-frame 96-min video.
- **`remaining` counter in run_ocr.py is misleading** in multi-session projects: it sums (frames−JSONs) over ALL
  `frames\*` subdirs, including other classes whose OCR intermediates were cleaned up. Trust only the target
  BASE dir's own frame/JSON counts.
- **Output format**: Each `frame_NNNNN.json` contains `{"frame": N, "texts": [...], "boxes": [...]}` where:
  - `texts`: list of recognized text strings
  - `boxes`: list of bounding box coordinates `[[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], ...]`
  - This is the **wrapped format** from `run_ocr.py`; the raw RapidOCR output is `[{"box":[[x,y],...],"text":"...","score":0.9}, ...]`.

### 3. Whisper transcription — Option A: faster-whisper (RECOMMENDED, CPU int8)
- Use venv_fw (see Prerequisites). Pattern `run_asr.py`:
  ```python
  import os, json, glob
  os.environ["HF_HUB_OFFLINE"] = "1"
  from faster_whisper import WhisperModel
  UNIT = 120  # seconds per checkpoint unit
  model = WhisperModel(model_path=r"<work>\fwhisper-large-v3-turbo", device="cpu", compute_type="int8")
  segments, info = model.transcribe(wav_path, language="zh", vad_filter=True,
      beam_size=5, vad_parameters={"min_silence_duration_ms": 500},
      initial_prompt="機器學習教學課程，請以繁體中文輸出。")
  ```
- **Model size vs quality tradeoff (measured 2026-08-25, I4.0 class 2h54m)**:
  | Model | Size | Speed (RTF) | Hallucination Rate | Notes |
  |-------|------|-------------|-------------------|-------|
  | `large-v3-turbo` | ~1.5 GB | ~2 min/unit (too slow) | Low | RECOMMENDED if time permits; best quality |
  | `small` | ~461 MB | moderate | Medium | Crashes repeatedly on this machine; unreliable |
  | `tiny` | ~72 MB | ~5s/frame (fastest) | **~88%** | Usable as fallback; prompt echo + gibberish dominate |
  - **Lesson learned**: `large-v3-turbo` is ideal but too slow for long videos without dedicated GPU. `small` model crashed repeatedly (possibly memory). `tiny` model works but produces massive hallucinations — prompt text leaks into output, gibberish on silent stretches, repeated CTA fragments. **Always document which model was used and its limitations in the report.**
  - **initial_prompt caution**: the prompt text itself (e.g. "工業4.0智慧製造課程，請以繁體中文輸出。") frequently appears as verbatim ASR output during silence — mark these segments as prompt-echo hallucinations.
- **Checkpointing**: read the wav with `wave`, slice `UNIT`-second units, transcribe each unit in its own
  process invocation; write one JSON per unit (`u_%04d.json`: start/end/segments). Re-running skips finished
  units → survives the ~4–5 min external watchdog. Budget ≤215 s of work per shell call, timeout ≤260 s.
- **RECOMMENDED since 2026-08-24: run the whole ASR as ONE detached background process** instead of ~20 budgeted
  foreground calls. `run_asr.py` already loops units with checkpoints, so a huge budget is safe:
  ```powershell
  $w = "<project>\_v2t_work"
  $p = Start-Process -FilePath "$w\venv_fw\Scripts\python.exe" `
      -ArgumentList "`"$w\run_asr.py`"","`"<BASE>`"","`"20000`"" `
      -WindowStyle Hidden -RedirectStandardOutput "$w\asr_<BASE>.log" `
      -RedirectStandardError "$w\asr_<BASE>.err.log" -PassThru
  "started PID=$($p.Id)"
  ```
  - The tool wrapper may print `Unknown: ChildProcess.kill` right after — ignore; verify with
    `Get-Process python*` and by tailing the log (`Get-Content ...asr_pm.log -Tail 1`). The detached process
    survives tool-call teardown because it was spawned via Start-Process.
  - **If the Start-Process child gets reaped anyway** (observed once: died silently at unit ~30 after ~50 min),
    relaunch fully detached via WMI — and note `Win32_Process.Create` does NOT understand `>>` redirection
    (CreateProcess passes them as literal argv), so wrap in cmd.exe:
    ```powershell
    $cmd = "cmd.exe /c `"`"$w\venv_fw\Scripts\python.exe`" `"$w\run_asr.py`" `"<BASE>`" 20000 >> `"$w\asr_<BASE>.log`" 2>> `"$w\asr_<BASE>.err.log`"`""
    $r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd }
    "return=$($r.ReturnValue) PID=$($r.ProcessId)"   # 0 = OK
    ```
    This survives everything; monitor via the log or `Get-ChildItem asr\<BASE>\u_*.json | Measure-Object`.
  - Poll while doing other work: `Start-Sleep -Seconds 230; Get-Content <log> -Tail 1`. Observed throughput
    ≈1 unit/min (RTF 1.6–4.3x) → a 97-unit 3h13m class finishes in ~75 min unattended.
  - Same pattern works for OCR if you prefer not to babysit foreground sessions.
- **NEVER use `BatchedInferencePipeline`** — it reliably HANGS on a middle block on this machine
  (verified twice: non-batched finishes the same audio in ~102 s while batched sits at 0% CPU).
  Plain `model.transcribe()` only.
- **Checkpoint loader must filter the exact filename pattern** (`u_*.json`). Mixing patterns from an
  older run (e.g. `block_*.json`) silently duplicates segments — delete stale files or filter strictly.
- After all units finish: convert to Traditional Chinese with OpenCC:
  ```python
  from opencc import OpenCC
  cc = OpenCC("s2twp")   # 簡→繁台灣用語
  text = cc.convert(text)
  ```
- **Hallucination detection (large-v3-turbo)**: mark as artifacts and exclude from analysis:
  - YouTube CTA on silence: 「請不吝點贊 訂閱 轉發 打賞支援明鏡與點點欄目」
  - 「優優獨播劇場——YoYo Television Series Exclusive」、片尾「字幕志願者 ○○○」
  - initial_prompt echo (the prompt text itself appears verbatim during silence)
  - Russian/English fragments on silent stretches; repeated 口頭禪 runs（「聽得懂嗎」×N）
  - First ~20 min of classes are chit-chat → fragmented ASR is normal, not a bug.
- **Hallucination detection (tiny model, ~88% rate measured 2026-08-25)**: the tiny model is severely degraded — document these patterns specifically:
  - **Prompt echo**: the `initial_prompt` text (e.g. "工業4.0智慧製造課程，請以繁體中文輸出。") appears verbatim as ASR output during silent segments. Mark ALL segments that exactly match or closely echo the prompt.
  - **Gibberish runs**: long stretches of meaningless syllables (e.g. "把互相剪開罵用 指示放出來冷靜 而散 Live,還未必能大"). These often have no corresponding OCR text and occur during silent/non-speech segments.
  - **YouTube CTA echo**: "明鏡需要您的支援 歡迎訂閱明鏡與點點欄目" repeated verbatim.
  - **Number sequences**: random number runs ("3.0 1.0 7.0 2.0 3.0...") with no semantic content.
  - **Mixed-language fragments**: Russian/English words scattered in Chinese output.
  - **Repeated partial phrases**: a short phrase repeated 3-5 times consecutively.
  - **Detection heuristic**: segments where >50% of characters are non-CJK or where the segment length is <5 chars after removing punctuation — likely hallucination.
  - **Report requirement**: always state the hallucination rate and which model produced it. When using tiny model, caveat that "ASR 品質受限，僅供參考，以 OCR 畫面文字為主要依據".

### 3b. Option B (legacy): OpenVINO whisper-large-v3 on Intel GPU
- Model: `whisper-large-v3-ov2` loaded as `OVModelForSpeechSeq2Seq` (not `WhisperPipeline` — API changed in newer optimum-intel).
  ```python
  from optimum.intel import OVModelForSpeechSeq2Seq
  import transformers
  model = OVModelForSpeechSeq2Seq.from_pretrained(model_dir, device='GPU')
  processor = transformers.WhisperProcessor.from_pretrained(processor_cache_dir)
  ```
- Processor cache: Download `preprocessor_config.json`, `tokenizer_config.json`, `vocab.json`, `merges.txt`, `added_tokens.json` from HuggingFace with `requests.get(url, verify=False)` (SSL fails through proxy). Set `os.environ['HF_HUB_OFFLINE'] = '1'` when loading.
- Do NOT feed the whole 60-min wav in one `generate()` call (it gets killed). Split externally into 30s chunks:
  `raw = raw_all[i*30*16000 : (i+1)*30*16000]` (int16 wav → `float32/32768`).
- Process in batches (e.g. `limit=30` per invocation) writing one JSON per chunk to `whisper_chunks\chunk_%04d.json`; re-run to skip finished chunks.
- Call signature:
  ```python
  inputs = processor(chunk_audio, sampling_rate=16000, return_tensors="pt")
  with torch.no_grad():
      outputs = model.generate(inputs.input_features, max_length=448, language="<|zh|>", task="transcribe")
  text = processor.batch_decode(outputs, skip_special_tokens=True)[0]
  ```
  - `language="<|zh|>"` is REQUIRED.
- ~5 min per chunk on GPU ⇒ 60-min video ≈ 3+ hours total (need multiple batch runs).
- **Hallucination detection**: Whisper injects repeated text ("好好好…", "謝謝大家") and YouTube CTA ("請不吝點讚 訂閱…") on silent segments. Mark these as artifacts in the final report.

### 4. Slide grouping (OCR) + alignment (speech)
- Merge consecutive frames into slide groups when cleaned-text similarity (`difflib.SequenceMatcher` ratio on stripped text) ≥ ~0.45; merge groups with identical titles.
- Representative frame = frame with most OCR items; title = most frequent cleaned line of length ≥ 6 across the group.
- For each group, collect whisper segments overlapping `[start,end]` (absolute seconds) as the speech column.
- **Respect the time-axis rule from step 1** when matching ASR segments to frame groups
  (2x video: `asr_start/2 <= group_end and asr_end/2 >= group_start`).
- Output `merged_timeline.txt` (`=== G<nnn> <start>-<end> | <title> | frame_<id>` + OCR lines + ASR lines),
  `slide_groups.txt`, `transcript_zh.txt` — these three files are the raw material for the report.

### 4b. PDF document cross-referencing (when reference PDFs are provided)
If the user provides PDF reference materials (e.g. lecture slides, technical guides), extract text and cross-reference with OCR + ASR:

1. **Extract PDF text** with `pdfplumber`:
   ```python
   import pdfplumber
   with pdfplumber.open(pdf_path) as pdf:
       for i, page in enumerate(pdf.pages):
           text = page.extract_text() or ""
           # Save per-page or full dump
   ```
   Save as `<work>\pdf<NN>_<name>.txt` for each PDF.

2. **Cross-reference** OCR timeline + ASR transcript against PDF content:
   - For each major video segment, check if OCR-detected slide text matches PDF page content
   - Check if ASR-explained concepts appear in PDF material
   - Note which PDF pages/sections were actually covered in the lecture vs. skipped
   - Identify ASR mis-hearings by comparing technical terms against PDF text

3. **Add to report**: include a "與PDF教材交叉比對" section with a table showing:
   - PDF section/page → Video time range → OCR match status → ASR mention status

- **Known pattern (I4.0 class)**: PDF-02 (16 pages) had 6/16 pages matched in video; PDF-03 (44 pages) had 4/7 sections confirmed. The cross-reference helps validate ASR accuracy and identify hallucinated content.

### 5. Build the markdown report
Mirror `分析影片-畫面與語音重點摘要.md` format: sections — 分析方法 / 影片概述 / 時間軸重點摘要（OCR×ASR 比對表，含代表影格欄）/
重點知識點解析 / 外部資料交叉比對（講師 GitHub repo、官方文件、PDF教材）/ ASR 幻覺偵測 / 驗證（幀數、單元數、RTF、時間軸基準）/ 結論 / 附註檔案清單.
- The OCR/ASR data is generated programmatically (`build_merge.py` → `merged_timeline.txt`); the narrative
  sections are written by the agent from that data, in Traditional Chinese.
- **PDF cross-reference** (when PDFs provided): add a "與PDF教材交叉比對" section with a table mapping PDF sections to video time ranges, OCR match status, and ASR mention status. This validates ASR accuracy and identifies hallucinated content.
- If the video is a course, fetch the instructor's public repos (e.g. GitHub) and cross-check commands/terms
  against them — this catches ASR mis-hearings of technical terms.
- **Reference report structure** (from `Class01-20260825-18ot0-nbHtM-分析影片-畫面與語音重點摘要.md`):
  ```
  # Class01-20260825 工業4.0概論 課程分析報告
  ## 一、分析方法 (methodology: OCR × ASR × PDF)
  ## 二、影片概述 (duration, resolution, frame count, model used)
  ## 三、時間軸重點摘要 (10 major segments, each with OCR/ASR/PDF columns)
  ## 四、重點知識點解析 (7 topics: I4.0, ISA95, MES/ERP, OEE/TEEP, etc.)
  ## 五、與PDF教材交叉比對 (PDF page → video time → match status)
  ## 六、ASR 幻覺偵測 (~88% hallucination rate documented)
  ## 七、結論 (course structure + key learning outcomes)
  ## 八、附註 (file naming, PDF inventory, model limitations)
  ```
- Save as `<video名>-分析影片-畫面與語音重點摘要.md` in the project folder.
- **FILENAME RULE (CRITICAL)**: the report extension is always plain **`.md`**. NEVER save as
  `<name>.md.docx` (double extension). This bug occurred on a real batch (`Class01..17-*-report.md.docx`,
  fixed 2026-08-24 by bulk-renaming). If the user supplies an exact target filename (e.g.
  `Class01-2026_06_17_週一-3-report.md`), use it verbatim; if a Word version is also wanted,
  export a separate `<name>.docx` — do not concatenate extensions.
- **`.md` MUST be real text — verify magic bytes (learned 2026-08-25)**: an external GPU pipeline
  (E:\01-Project generator, EasyOCR+Whisper-medium) had written **docx (ZIP/OOXML) files named `*.md`**
  for all 17 classes of `D:\80-Opnecode\Projects\2026_06_playwirght` (magic bytes `50 4B 03 04`, contains
  `word/document.xml`). The Read tool reports "Cannot read binary file" and grep finds nothing.
  Detection + fix:
  ```powershell
  # detect: read first 4 bytes of each *.md; PK\x03\x04 = docx masquerading as md
  Get-ChildItem "<proj>\*-3-report.md" | ForEach-Object {
    $b = [System.IO.File]::ReadAllBytes($_.FullName)[0..3]
    "{0}  {1}" -f (($b | ForEach-Object { $_.ToString("X2") }) -join " "), $_.Name }
  ```
  Convert with `_v2t_work\convert_docx_md.py` (ElementTree over document.xml):
  Heading1→`#`, Heading2→`##`, body tables → GFM pipe tables (escape `|`, join multi-paragraph cells
  with `<br>`), skip empty paragraphs. Script is idempotent (skips files whose first 4 bytes ≠ PK),
  backs up originals to `_v2t_work\backup_docx_md\<name>.md.docx` before overwriting in place,
  writes UTF-8 no BOM via temp file + `os.replace`.
  These legacy reports are per-minute tables (時間/語音重點/畫面OCR重點/GitHub 對照) with heavy ASR noise;
  known mis-hearings to correct when summarizing: 雷神NN=lessonNN, Open call=OpenCode, Power share=
  PowerShell, Greema/Grimmer=Gemma, Ghfome/Ghrome=Chrome, Agy=Antigravity, POTY/pyy=.py.
  Times are on the **2x video** timeline (original class time = ×2).

### 6. Build the key-frame PDF
- `make_pdf.py` (Pillow — no reportlab needed): pick ~19–30 representative frames (cover/agenda, each major
  slide, demos, comparison tables), one per page, dark caption bar at TOP with `MM:SS` time + Traditional-Chinese
  caption; compose with PIL and save via `pages[0].save(out, save_all=True, append_images=pages[1:], resolution=120)`.
- Chinese font: `C:\Windows\Fonts\msjh.ttc` (Microsoft JhengHei). `ImageFont.truetype(font, 34)` at 1600px page width.
- Pillow may be missing in venv_fw → `python -m pip install --quiet pillow` first.
- Save as `<video名>-畫面重點.pdf` in the project folder.
- **Frame selection is OCR-driven**: the current model CANNOT read images (Read on a .jpg returns
  "this model does not support image input"). Pick frames from slide-group representative indices + OCR text only —
  don't attempt visual inspection of frames.
- Keep one `make_pdf_<BASE>.py` per class (CAPTIONS differ per video); reuse the same layout code.
- **OCR JSON format**: when reading `ocr/frame_NNNNN.json`, handle both formats:
  - Wrapped format: `{"frame": N, "texts": [...], "boxes": [...]}` → use `data["texts"]`
  - Raw format: `[{"box":..., "text":..., "score":...}, ...]` → use `[item["text"] for item in data]`
  - Always check `isinstance(data, dict)` first to avoid `string indices must be integers` errors.

### 6b. Build the report PDF (from markdown, alternative approach)
When the deliverable is a rendered PDF of the markdown report (not key-frame screenshots), use the
`md-to-pdf` skill's Pillow renderer:
1. Copy `D:\80-Opnecode\.opencode\skills\md-to-pdf\make_md_pdf.py` to `<project>\make_<name>_pdf.py`
2. Modify three values at top: `SRC` (markdown path), `OUT` (pdf output path), `FOOTER` (page footer text)
3. Run with Pillow venv: `venv_fw\Scripts\python.exe make_<name>_pdf.py`
4. Verify first page OCR for Chinese readability; clean up temp `_pdf_page1.png`
- This produces an A4 multi-page PDF with H1/H2/H3 headings, tables (auto-width + zebra stripes), code blocks, quotes, and page numbers.
- Save as `<video名>-分析影片-畫面與語音重點摘要.pdf` alongside the `.md`.

## Environment gotchas (learned the hard way — respect these)
- **Network sits behind a Fortinet proxy** (`HTTP(S)_PROXY=http://n000149839:...@10.3.159.1:80`).
  - Python/yt-dlp HTTPS calls fail cert verification → always use `--no-check-certificates`.
  - **GitHub large-file downloads (yt-dlp.exe ~20 MiB, ffmpeg builds) stall at 0 bytes through the proxy**
    → install tools via pip instead of downloading exes; curl direct (`--noproxy "*"`) fails too (no route).
  - **winget source is broken** (`0x8a15000f Data required by the source is missing`) — do not rely on winget;
    install yt-dlp with `py -m pip install -U yt-dlp`.
- **imageio-ffmpeg's binary is named `ffmpeg-win-x86_64-v7.1.exe`, not `ffmpeg.exe`** — copy it if a tool needs the standard name.
- **Stateful whisper export requires the `-with-past` task.** `optimum-cli export openvino --task automatic-speech-recognition` produces a decoder WITHOUT `beam_idx` → runtime error `Port for tensor name beam_idx was not found`. Must export with:
  `optimum-cli export openvino --model <pt_dir> --task automatic-speech-recognition-with-past --weight-format fp16 <ov_dir>`
  Verify decoder XML has parameters `input_ids`, `encoder_hidden_states`, `beam_idx` and a single `logits` output.
- **optimum-intel must be 1.27.0** (with optimum 2.1.0 / transformers 4.57.x). Newer optimum-intel 2.1.0 exports a static (unrolled, no KV state, no beam_idx) decoder incompatible with openvino-genai 2026.3.0.0. It also downgrades nothing critical, but keep the known-good combo.
- **HuggingFace / hf-mirror TLS fails** in this environment; download model files with `requests.get(url, verify=False)` direct file download (see `dl_model.py`). `pytorch_model.bin` is ~3.09 GB.
- **Long single commands get killed** by an external watchdog (~4–5 min). Mitigate: checkpoint every unit of work
  (per-frame JSON, per-unit JSON) and run in batches; re-run to resume. Practical budgets: **≤215 s of work per
  shell call, timeout ≤260 s**; OCR with `ProcessPoolExecutor(max_workers=12)` ≈ 5 s/frame → ~40 frames per call.
- **Python console codepage (cp950) crashes on CJK/Korean output**: start scripts with
  `import sys; sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.
- PowerShell native-command stderr is rendered as errors by `2>&1 | Select-Object -Last n`; check exit code via `$LASTEXITCODE` and verify output files exist rather than trusting the last lines.
- Optional DirectML OCR patch: monkeypatch `rapidocr_onnxruntime.utils.OrtInferSession.__init__` to add `DmlExecutionProvider`; on this Intel iGPU it was 2x SLOWER than CPU, so don't bother.

## Deliverables checklist
- [ ] `<video名>.mp4` (1080p60, from yt-dlp step 0) in project folder
- [ ] `<video名>-2x.mp4` (2x speed, if requested) in project folder
- [ ] `<video名>-cropped.mp4` (black bars removed, if present) in project folder
- [ ] `<video名>-分析影片-畫面與語音重點摘要.md` in project folder (plain `.md`, NEVER `.md.docx`)
      — after writing, verify first 4 bytes are NOT `PK\x03\x04` (real text, not docx)
      — if PDF reference materials exist, include "與PDF教材交叉比對" section
- [ ] `<video名>-分析影片-畫面與語音重點摘要.pdf` in project folder (rendered from .md via Pillow+msjh)
      — use `md-to-pdf` skill's `make_md_pdf.py` with modified SRC/OUT/FOOTER paths
      — verify first page OCR for Chinese readability before delivery
- [ ] `<video名>-畫面重點.pdf` in project folder (use cropped frames if cropped)
- [ ] `README-影片分析管線與檔案說明.md` (folder/pipeline documentation, if user asks for a 說明檔;
      written 2026-08-25 for the playwright batch: naming rules `-1 mp4 / -2-keyframes.pdf /
      -3-report.md`, per-class table with durations + YouTube IDs extracted from report headers,
      pipeline description, time-axis convention, ASR mis-hearing table)
- [ ] Intermediates in the shared `_v2t_work\`: `frames\<BASE>\`, `ocr\<BASE>\`, `asr\<BASE>\u_*.json`,
      `audio\<BASE>_1x.wav`, and BASE-suffixed `transcript_zh_<BASE>.txt` / `slide_groups_<BASE>.txt` /
      `merged_timeline_<BASE>.txt` / `make_pdf_<BASE>.py` / per-run logs (`asr_<BASE>.log`) — all persistent
- [ ] **Stale-workdir caution**: a project's `_v2t_work\` may contain leftovers from an OLDER/different
      pipeline (e.g. flat layout `audio.wav`, `ocr\f_00001.json`, only ~65 frames, ASR full of ad
      hallucinations) that match NO class. Don't trust or cite such intermediates; check frame/JSON
      counts against the actual video duration before reusing anything.
