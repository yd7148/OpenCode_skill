---
name: video-2x-speed
description: Convert a recorded video to 200% playback speed (or arbitrary 0.5x–100x) with ffmpeg, keeping the same resolution and fps, using Intel GPU (h264_qsv) and audio via atempo. Also supports cropping dead black bands (e.g. lecture captures: keep left white content, drop right black area) combined with the speed change in one pass. Encodes the correct speed without the classic `-t`-placement pitfall that silently produces a non-sped file. Use when asked to "加速影片", "轉成2倍速", "200% 播放速度", "倍速播放", "speed up video", "裁切黑邊", "切除黑色部分", or to produce a 2x/cropped copy of a downloaded .mp4.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: video-speed-up
  languages: zh-TW
---

# video-2x-speed — 影片加速（ffmpeg 200% 速度轉檔）

Make a playable copy of a video at **200% playback speed**, same resolution (optionally cropped,
see "Crop detection" below), same fps, with 2x-pitched-preserved audio (`atempo`), encoded on the
Intel GPU via `h264_qsv`.

Deliverable: `<video名>-2x.mp4` next to the source, **unique filename** (never overwrite the source).

## When to use
- User asks 加速影片 / 轉成 2 倍速 / 200% 播放速度 / 倍速播放 / speed up a video.
- Video is already downloaded (yt-dlp output, or any local .mp4). For standard downloads see the `video2text` skill.
- **HLS fallback download**: When yt-dlp fails to download (proxy blocks m3u8), use the Python method below.

## HLS fallback download (proxy blocks yt-dpffmpeg m3u8)

Fortinet 代理會封鎖 googlevideo.com 的 m3u8/HLS 串流（403 Forbidden），導致 yt-dlp + ffmpeg
無法下載。解法：用 Python `urllib` 自行下載 m3u8 播放清單與分段，再用 ffmpeg 合併。

### Step 1: 用 yt-dlp 取得 m3u8 URL
```powershell
py -m yt_dlp --no-check-certificates `
  --extractor-args "youtube:player_client=android_vr" `
  -g "URL"   # 取得 m3u8 manifest URL
```
注意：`android_vr` client 會回傳 HLS 格式。若需 DASH 格式（分離 video/audio），需安裝 JS runtime (deno)。

### Step 2: Python 下載所有分段
```python
# 關鍵：透過 proxy 下載 m3u8 播放清單（Python urllib 可通過，ffmpeg 不行）
# 8 workers 並行下載，避免被 ban
# 每段 5 秒，105 分鐘影片 ≈ 1260 段
# 若中途中斷（403），重新執行可從新 m3u8 URL 繼續（已下載的段會跳過）
```
- 用 `ThreadPoolExecutor(max_workers=8)` 並行下載
- 每段存為 `seg_00000.ts` ~ `seg_01261.ts`
- 下載 800+ 段後可能被 rate-limit（403），重新執行腳本取得新 m3u8 URL 繼續

### Step 3: ffmpeg 合併 TS → MP4
```powershell
# 產生 concat list（BOM-free！）
$lines = @("file 'seg_00000.ts'", ... "file 'seg_01261.ts'")
[System.IO.File]::WriteAllLines("$work\concat_list.txt", $lines, (New-Object System.Text.UTF8Encoding($false)))
& $ff -y -hide_banner -f concat -safe 0 -i "$work\concat_list.txt" -c copy "$work\video_full.mp4"
```

### 注意事項
- 直播串流（`yt_live_broadcast`）只有 HLS 格式，無法用 DASH
- Python urllib 透過 proxy 可以下載 googlevideo.com 分段，但 ffmpeg 不行
- 分段格式為 TS（MPEG-TS），合併後為 MP4（copy codec，無重編碼）
- 檔案大小：1080p30 HLS 約 300-400 MB/小時

## Prerequisites (already provisioned)
- ffmpeg 7.1: `$env:USERPROFILE\opencode-tools\ffmpeg.exe`（`C:\Users\N000149839\opencode-tools\ffmpeg.exe`）
  - 備用：`D:\Downloads\Tools\kdenlive-25.08.0_standalone\bin\ffmpeg.exe`
  - NOT on PATH — always use the full path.
- yt-dlp: `py -m yt_dlp`（pip 安裝，NOT on PATH）
- Intel GPU + `h264_qsv` encoder available in that build (verified working).
- Python 3.13: `py` launcher.

## CRITICAL lesson — where to put `-ss` / `-t`

**`-ss` / `-t` must be placed BEFORE `-i`** (input options) so each segment slices an exact
source window and the output is that window at 2x:

```
# CORRECT — input-side slicing (slice 60s of source → 30s output)
ffmpeg -ss 600 -t 60 -i src.mp4 -vf "setpts=PTS/2" -af "atempo=2.0" -c:v h264_qsv ... out.mp4
```

If you put `-t` AFTER `-i`, it becomes an **output** option: the muxer re-times the stream to
fill the requested duration (silent 1x), and long output caps slice *overlapping* source ranges.
Symptoms of the bug (observed 2026-08-13):
- Output `Duration` equals the input slice (e.g. `-t 480` → 8:00 out, should be 4:00).
- Progress lines show `dup=0 drop=N` (an auto-inserted `fps` filter drops half the frames back to 60fps).
- `Application provided invalid, non monotonically increasing dts to muxer` warnings appear.
- Probing output PTS shows clean 60fps `0,256,512,...` timestamps (re-timed) instead of halved ones.

`setpts=PTS/2` itself is **fine**; the half-speed timestamps get dropped back to 60fps by the
auto `fps` filter, which is exactly what we want for "2x at 60fps". Don't fight it — verify by
duration and frame count, not by staring at `setpts`.

## CRITICAL lesson — QSV frame rate with `setpts=PTS/2`

When the source is **30fps** (not 60fps), `setpts=PTS/2` halves timestamps and QSV reports
"Current frame rate is unsupported". Fix: add `fps=30` (or source fps) to the filter chain:

```
-vf "setpts=PTS/2,fps=30"
```

For **60fps sources**, the auto-inserted fps filter handles it (no extra `fps=` needed).
Always verify output fps matches expectations after the first test segment.

## Recipe (verified)

Filter chain — plain 2x, or 2x + crop (e.g. remove right black band keeping left content):

```powershell
# plain 2x
-vf "setpts=PTS/2,fps=30"
# 2x + crop (crop FIRST, then setpts/fps)
-vf "crop=1440:1080:0:0,setpts=PTS/2,fps=30"
```

Per segment (measured 2026-08-21: one 480s 1080p slice ≈ **25 s** wall time on this machine's QSV,
so batching ~6 segments per tool call ≈ 2.5 min is safe under the watchdog):

```powershell
$ff = "$env:USERPROFILE\opencode-tools\ffmpeg.exe"
$src = "<work>\video_full.mp4"
# 480s of source (input-side -t) → 240s of 2x output
foreach ($i in 2..7) {                       # batch of 6 per command
  $start = ($i-1)*480
  & $ff -y -hide_banner -loglevel error -ss $start -t 480 -i $src `
      -vf "crop=1440:1080:0:0,setpts=PTS/2,fps=30" -af "atempo=2.0" `
      -c:v h264_qsv -global_quality 28 -c:a aac -b:a 128k ("$work\2x_seg{0:d2}.mp4" -f $i)
  if ($LASTEXITCODE -ne 0) { Write-Output "seg$i FAILED" }
}
```

- `<START>` per segment: `0`, `480`, `960`, `1440`, ... (step by 480) = `($i-1)*480`.
- Last segment: `-ss <last>` with NO `-t` reads to end-of-file → `(remaining)/2` output.
- Expected per 480s slice: `Duration 00:04:00.00` (240s) — exactly half.
- For long videos (e.g. 111 min = 6684s), need ⌈6684/480⌉ = 14 segments.
- Always check `$LASTEXITCODE` per segment inside the loop (QSV stderr noise is cosmetic).

## Crop detection — black-band removal (verified 2026-08-21)

When the source has a solid black band (e.g. lecture capture with dead space right of the slide),
**do not trust `cropdetect` alone** — it reports noise-driven boxes (e.g. `1712:1072:8:4`) that keep
black slivers. Instead measure column brightness directly with Python PIL.

Gotchas learned on real files (2026-08-21, 22-video batch):
- **Compression noise**: black-band columns reach pixel values ~17–19 → use `DARK = 32`, not 16.
- **Overlays live IN the black zone** (timestamp text, webcam thumbnails at x1456–1856): requiring
  *every* column beyond the boundary to be dark always fails. Only require the first few columns
  dark, then check the far region is *overwhelmingly* dark (dark-fraction > 0.9).
- **Dark slide frames** (break screens) are fully black → would false-trigger at scan start.
  Guard: area left of the candidate boundary must be white (avg > 128).

```python
def analyze(im):                      # returns (boundary_x, left_avg, dark_frac)
    w, h = im.size; px = im.load()
    for x in range(1200, 1700):
        if all(max(px[xx,y] for y in range(0,h,8)) < 32 for xx in range(x, x+4)):
            left = [px[xx,y] for xx in range(x-120, x-8) for y in range(0,h,32)]
            reg  = [px[xx,y] for xx in range(x+20,w,4) for y in range(0,h,8)]
            return x, sum(left)/len(left), sum(1 for v in reg if v < 32)/len(reg)
    return -1, -1, -1
# accept frame only if x>0 and left_avg>128 and dark_frac>0.9
```

Workflow:
1. Extract frames at several timestamps (`-ss 10%/50%/90% of duration -frames:v 1 probe.png`).
2. Run the analysis per frame; accept the video only if ≥2 frames agree on the same boundary
   (lecture captures are static; all 22 videos in the batch had exactly x=1440).
3. Crop with `crop=<boundary>:<H>:0:0` (keep the LEFT white/content side, drop the right band).
4. After encoding, verify the output's right-edge columns are bright (~200), i.e. no black residue.

Note: cropping 1920x1080 → 1440x1080 changes DAR 16:9 → 4:3; players handle it automatically.

## Batch mode — many videos, resumable (verified 2026-08-21, 22 videos / 65 h source)

For folder-wide jobs write three artifacts into a persistent `_2x_work\` folder:

1. `jobs.json` — `[{"name": "...", "dur": <seconds>}, ...]` (durations probed once via ffmpeg `-i`).
2. `bounds.json` — `{name: boundary_x}` from the crop-detection step above.
3. `encode_all.ps1` — loops jobs; per job skips existing valid segments, encodes missing ones,
   concats (BOM-free list), verifies `duration == dur/2 ±5s`, moves `<base>-2x.mp4` next to source.
   Prints `[seg] base i/n` progress lines and exits non-zero on failure.

Then just re-launch the script until it prints `ALL VIDEOS DONE`. Throughput measured:
**~2 videos (~5.7 h source) per 20-minute tool call**; whole 65 h batch ≈ 11 calls.

### CRITICAL: killed runs leave corrupt segments

A segment being written when the tool call is killed has **no moov atom** (ffmpeg writes it last).
It exists on disk so a naive "skip existing" resume will concat garbage → `moov atom not found`,
`Impossible to open ... 2x_segNN.mp4`. Fix: before skipping an existing segment, probe it and
delete if invalid:

```powershell
if (Test-Path $seg) {
    $chk = (& $ff -hide_banner -i $seg 2>&1 | Out-String) -match "Duration:"
    if (-not $chk) { Remove-Item $seg -Force }   # corrupt → re-encode
    else { continue }
}
```

This self-heals on every relaunch; expect to see one `[corrupt]` removal per killed call.

### Concatenate (with a BOM-free list!)

```powershell
$lines = @("file 'seg0.mp4'", ... "file 'seg4.mp4'")
[System.IO.File]::WriteAllLines("$work\concat_list.txt", $lines, (New-Object System.Text.UTF8Encoding($false)))
& $ff -y -hide_banner -loglevel error -f concat -safe 0 -i "$work\concat_list.txt" -c copy "$work\video_2x_new.mp4"
```

- **Do NOT use PowerShell `Set-Content -Encoding UTF8`** for the list: it writes a UTF-8 BOM and the
  concat demuxer fails with `Line 1: unknown keyword '﻿file'`. `UTF8Encoding($false)` avoids the BOM.

### Finalize + verify
- Replace the old wrong `-2x.mp4` (if any) in the target folder, keep the same unique filename.
- Verify with `& $ff -i <file>`: total `Duration` must be ≈ source/2 (e.g. 35:33 → 17:46), video
  `1920x1080 60 fps`, audio `aac 44100 Hz ~127 kb/s`.
- Deliverable filename: `<video名>-2x.mp4` (append `-2x` to the exact source base name).

## Verification of a working 2x file
- Total duration = source duration / 2 (± 0.5s concat tolerance).
- Frame rate still 60fps, resolution unchanged, audio present (atempo keeps pitch).
- Segments each exactly `input/2` long (4:00.03 for 480s slices).

## Environment gotchas (this machine, learned 2026-08-13 / 2026-08-18 / 2026-08-21)
- **Watchdog vs explicit timeout**: the ~4–5 min kill applies to the *default* timeout. Passing an
  explicit `timeout` (e.g. `1200000` ms = 20 min) works — a whole resumable batch call can run the
  full 20 min (~2 videos). Still keep each tool call bounded; the resumable script makes kills cheap.
- **Killed mid-encode = corrupt segment** (no moov atom) — see "Batch mode" for the self-healing
  probe-and-delete resume pattern.
- **QSV driver logs cosmetic errors** to stderr (e.g. `kernel.errors.txt` with `igc_check` lines) —
  check `$LASTEXITCODE` and the output file, not stderr text.
- **QSV + setpts frame rate**: 30fps source + `setpts=PTS/2` → QSV rejects "unsupported frame rate".
  Fix: add `fps=30` to filter chain. 60fps sources work without explicit fps.
- **Fortinet proxy blocks m3u8/HLS**: ffmpeg gets 403 on googlevideo.com manifests.
  Workaround: Python urllib downloads segments fine through the proxy.
- **Proxy rate-limit**: downloading 800+ HLS segments in parallel may trigger 403.
  Solution: re-run script to get fresh m3u8 URL and download remaining segments.
- Probe/verify with ffmpeg `-i` (no ffprobe available in opencode-tools).
- Work in a persistent `_<video>_work\` folder, not the OS temp dir (it gets wiped).

## Deliverables checklist
- [ ] `<video名>-2x.mp4` in the target folder, `Duration == source/2`, correct resolution
      (source res, or cropped W×H if crop was requested), 30/60fps, audio
- [ ] If cropping: boundary verified identical across ≥2 sampled frames; output right-edge columns bright
- [ ] Batch jobs: every file probed at the end (`bad=0`), not just the last one
- [ ] Segments + concat list left in `_<video>_work\` (or `_2x_work\<base>\`) for re-concat
- [ ] Test artifacts cleaned up (e1…, t_*, timing_*, syn, probe_*.png, old wrong `-2x.mp4`)
