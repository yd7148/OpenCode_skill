---
name: video-class-pipeline
description: Use when the user asks to analyze/process 課程影片 (course videos), YouTube live-recorded class sessions, screen-recording videos, or any workflow involving video download, frame extraction, OCR, Whisper transcription, per-minute cross-reference, keyframe PDFs, video cropping, or 2x speed conversion. Covers the Python AI course project at E:\01-Project\2026-07-B-python_ai_tvdi and the n8n course project at E:\01-Project\2026_08_n8n_itri.
---

# Video Class Pipeline (課程影片分析與轉檔)

Proven workflow for batch-processing a series of recorded class videos
(Google Meet / YouTube live screen captures) into analyzable artifacts
(OCR of on-screen text, Whisper speech transcription, per-minute crossref,
keyframe PDFs) and for one-off video edits (crop black bars, 2x speed)
with GPU encoding on an RTX 5080.

## Environment (Windows, RTX 5080)

- Python: `C:\Users\4pins\AppData\Local\Programs\Python\Python312\python.exe`
- ffmpeg/ffprobe: `C:\Users\4pins\AppData\Local\Microsoft\WinGet\Packages\yt-dlp.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-N-125875-g5d4d3bdc61-win64-gpl\bin\`
- GPU deps installed: `torch` (CUDA), `whisper`, `easyocr`, `opencv-python`, `Pillow`, `yt-dlp`.
- NVENC encoders available: `h264_nvenc`, `hevc_nvenc`, `av1_nvenc`.
- Chinese/non-ASCII paths break `cv2.imread` → always decode via
  `np.fromfile(path)` + `cv2.imdecode(data, cv2.IMREAD_COLOR)`.
- Run Python one-liners from PowerShell carefully: inline `-c` quoting breaks;
  write a temp `.py` file under `C:\Users\4pins\AppData\Local\Temp\opencode` instead.
- Wrap stdout with `io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")`
  when printing Chinese to avoid console codepage garbling.

## Reference project layout

`E:\01-Project\2026-07-B-python_ai_tvdi\`:

```
pipeline/          all scripts
  videos.py        VIDEOS list: {name, url, id}; video_by_index(idx) 1-based
  paths.py         BASE/VIDEO_DIR/ANALYSIS_DIR, find_ffmpeg(), workdir_for(idx), video_path_for(idx)
  download_videos.py <start_idx>   yt-dlp sequential download, resume-safe (skips >50MB)
  extract_frames.py <idx>          ffmpeg -> frames/frame_NNNN.jpg every 10s (fps=1/10)
  extract_audio.py <idx>           ffmpeg -> audio.wav (16k mono)
  ocr_frames.py <idx>              EasyOCR ch_tra+en GPU, resumes, writes ocr_results.json
  whisper_transcribe.py <idx>      Whisper "medium" zh on CUDA -> whisper_results.json + .txt
  build_crossref.py <idx>          per-minute speech+best OCR frame+URLs -> crossref_per_minute.txt
  make_report.py <idx>             keyword-tagged timeline Markdown -> report_<name>.md
  make_keyframes_pdf.py <idx>      contact-sheet PDF of important frames -> keyframes_<name>.pdf
  build_all_frames_pdf.py          combined ALL_KEYFRAMES.pdf (top frames, all videos)
  build_summary.py                 SUMMARY.md overview table
  process_video.py <idx>           end-to-end driver: frames->OCR->audio->whisper->crossref->report->pdf
videos/            downloads + converted outputs
analysis/<name>/   per-video outputs (frames/, ocr_results.json, whisper_results.json,
                   crossref_per_minute.txt, report_*.md, keyframes_*.pdf, audio.wav)
github_materials/  cloned repos used for cross-referencing course content
```

## Second project: n8n course

`E:\01-Project\2026_08_n8n_itri\videos\` holds Google Meet recordings named
`YYYY_MM_DD_上午.mp4` / `YYYY_MM_DD_下午.mp4` (1920x1080 30fps, h264+opus,
~2.5-3h each). Workflow B (crop black bar + 2x speed) is applied first;
output naming convention: `<name>_裁切2倍速.mp4` next to the source.
The `_裁切2倍速.mp4` files are then analyzed with the full pipeline below.

Proven values for this Meet layout (1920-wide):
- crop width = **1440** (`crop=1440:1080:0:0`) — white content region ends there.
- The date/time stamp ("8月20日週四 上午9:38") sits at x≈1277-1427, y≈77-97 →
  inside the crop; the "Google Meet" watermark at x≈1698+ is in the black
  region and gets dropped, which is fine.
- ALWAYS re-run boundary detection per video anyway (layout may differ).
- After crop+2x the file is 1440x1080 h264+aac; observed 2x durations range
  ~76-132 min per video (460/790 frames at 1-per-10s). Don't assume a fixed
  length — ffprobe each file.

### n8n analysis pipeline (`pipeline/`, mirrors tvdi layout)

```
videos.py              VIDEOS list {name, file, id, url}; video_by_index(idx) 1-based
                       ALL FOUR ANALYZED (as of 2026-08-22):
                       idx 1 = 2026_08_20_上午 (e1D1cA5qEsE), idx 2 = 2026_08_20_下午 (d837e9MWcEI)
                       idx 3 = 2026_08_21_上午 (PMVQaNTi_zg), idx 4 = 2026_08_21_下午 (1i39KP64Kt4)
extract_frames.py <idx>   frames/frame_NNNN.jpg every 10s
ocr_frames.py <idx>       EasyOCR ch_tra+en GPU, resume-safe -> ocr_results.json
extract_audio.py <idx>    audio.wav 16k mono
whisper_transcribe.py <idx>  Whisper medium zh CUDA -> whisper_results.json + whisper_transcription.txt
build_github_index.py     verified term index from github_materials/ clones -> github_index.json
gh_match.py               find_matches(text) against the index; extract_urls()
build_crossref.py <idx>   per-minute speech + best OCR frame + URLs + GH matches
make_report.py <idx>      report_<name>.md: timeline table, URL frames, GH hit stats,
                          hallucination filtering, quality notes
make_keyframes_pdf.py <idx>  keyframes_<name>.pdf — ONE frame per page
```

Observed timings (RTX 5080): OCR 0.76–0.82 f/s → 460 frames ≈ 9.5 min,
790 frames ≈ 17 min; Whisper medium zh CUDA: 77-min audio → ~6.5 min
(2412 segs), 131-min audio → ~7.5 min (3069 segs). The Whisper tqdm bar can
stall/dip wildly mid-run (e.g. 300→9000 frames/s) — cosmetic, it finishes fine.

User's preferred run pattern (stated explicitly): process videos ONE at a time,
verify each fully (report content spot-check + raw-byte PDF page count +
JSON item counts) BEFORE starting the next, then continue automatically
("請自動連續完成"). Deliverables requested every time: GPU OCR every-10s frames,
GPU Whisper transcript, 幻覺-free GitHub cross-ref, Markdown tables, keyframe PDF.
The user's general tooling reference doc is
`E:\01-Project\2026-07-chihlee_gemini\01-# YouTube 影片下載與編輯-README.md`.

### No-hallucination GitHub cross-reference (user requirement)

The user explicitly demands 幻覺-free cross-referencing against
https://github.com/roberthsu2003/n8n and https://github.com/roberthsu2003/.
Method that works:
1. Course repos are cloned under `github_materials/`: `n8n-main` (= roberthsu2003/n8n
   n8n實戰教學講義), `__2026_08_20_n8n_itri__-main` (current 工研院 course, has
   `0821/*.json` workflows), plus older course repos and `workflow-productivity-main`.
2. `build_github_index.py` walks the clones and indexes ONLY real dir names,
   file names/stems, n8n workflow `name` fields from export JSON, and README
   headings -> `pipeline/github_index.json`.
3. Reports cite matches as `` `term` → `repo:path` `` — every path is guaranteed
   to exist because it came from walking the filesystem. Never invent paths.
4. Verify repo identity by fetching the GitHub profile page once
   (?tab=repositories&q=n8n) rather than assuming repo↔clone mappings.

### Whisper hallucination filtering

Whisper zh invents stock phrases on silence/noise. Filter with a HALLU regex:
`点赞|打赏|明镜与点点|Amara\.org|谢谢观看|謝謝觀看|訂閱.{0,6}轉發|字幕.{0,4}提供`.
In make_report.py such segments are excluded from the timeline and counted in a
「資料品質備註」 section. Observed counts vary a lot per video: 63 segments in one
114-min video, 1 in another, and **0 in both 08_20 videos** — always run the
filter, never assume.
Also note OCR browser-menu garbled Chinese there (楢案=檔案 class errors) as a
known EasyOCR limitation so users don't attribute it to content.

Verification recipe used after each video (all green on 08_20 batch):
- `ocr_results.json` item count == frame count, 0 empty ocr_text
- whisper last segment end ≈ ffprobe duration (4586s/7906s vs 4602s/7922s)
- PDF: `%PDF` header + `%%EOF` + page count via raw-byte `/Type /Page` diff
- report spot-check first/last rows for sane speech/OCR/GH cells

### Keyframe PDF format (user preference)

User explicitly wants **one frame per page** (rejected the 3-per-page contact
sheet). Layout: full-res frame (1440x1080) pasted at top margin 30px, caption
zone ~150px below with name/index/timestamp/frame-file line (font 22) + up to
3 lines of OCR snippet (font 18). Save with `resolution=120.0`. Captions need
a CJK font: try `C:\Windows\Fonts\msyh.ttc` → `simhei.ttf` fallback.
Verify PDFs without pypdf/PIL (neither installed / PIL can't reread): count
`data.count(b'/Type /Page') - data.count(b'/Type /Pages')` on raw bytes and
check header `%PDF` + trailing `%%EOF`.

Gotcha: in make_report.py `ocr_by_min[m]` stores the whole item dict — compare
with `item["ocr_text"]`, not `["text"]` (KeyError otherwise).

## Workflow A — batch analysis

1. Edit `pipeline/videos.py` so each entry has `name` (e.g. `2026_07_03_上午`),
   `url`, `id` (YouTube ID). Output filenames are `<name>_<id>.mp4`.
2. Download: `python pipeline/download_videos.py <start_index>`. Sequential is
   safe; network drops happen — the script retries and skips existing files,
   so just re-run. Verify with `python pipeline/verify_downloads.py`.
3. Process each video: `python pipeline/process_video.py <idx>` (~40 min each;
   run 2-3 per shell call with `timeout` 7200000 ms; OCR has resume support so
   a timeout mid-way is fine — re-run the same command).
4. Build the combined deliverables: `build_summary.py` then
   `build_all_frames_pdf.py`.

Observed timings (RTX 5080, ~3h video, 1090 frames):
- frame extraction ~2-4 min, OCR ~24 min (0.77 f/s), whisper ~8 min,
  NVENC transcode ~6.5 min at ~413 fps (13.8x realtime).

## Workflow B — crop black bar + 2x speed (GPU)

1. Find the crop boundary programmatically (do NOT guess or eyeball if image
   input is unavailable). Probe `ffprobe` for width/height, then use OpenCV:
   column-mean profile to find the rightmost bright column (`colmean > 30`),
   and EasyOCR with `detail=1` bounding boxes on the top-right quadrant to
   confirm the time/date text (e.g. "上午8:55") sits inside the white region.
   Confirm the boundary is stable by sampling several timestamps.
   - Sample at t = [60, 600, 1800, 3600, 5400, 7200, near-end]; take the
     majority value. Early samples can disagree: an intro/loading screen has a
     different layout (e.g. boundary 1034 at t=60 vs 1440 elsewhere) — trust
     the consistent value from the body of the video.
2. Transcode with NVENC in TWO passes, then mux. A single-pass
   `-filter_complex` command encoding video (NVENC) + audio (AAC) together
   **truncates the AAC audio stream** (~500-600s instead of full length) on
   this ffmpeg/NVENC build, even though each pass alone works. Always split:
   ```bash
   # pass 1: video only (crop + 2x + NVENC)
   ffmpeg -y -hide_banner -loglevel warning -stats -i in.mp4 -an \
     -vf "crop=W:H:0:0,setpts=PTS/2,fps=30" \
     -c:v h264_nvenc -preset p5 -rc vbr -cq 21 -spatial-aq 1 -temporal-aq 1 -b:v 0 \
     pass1_video.mp4
   # pass 2: audio only (2x + AAC)
   ffmpeg -y -hide_banner -loglevel warning -stats -i in.mp4 -vn \
     -af atempo=2.0 -c:a aac -b:a 128k pass2_audio.m4a
   # mux (copy, no re-encode)
   ffmpeg -y -i pass1_video.mp4 -i pass2_audio.m4a -map 0:v -map 1:a \
     -c copy -shortest out.mp4
   ```
   - Put pass1/pass2 intermediates under `C:\Users\4pins\AppData\Local\Temp\opencode`
     and delete them after muxing (~400MB each).
   - 2x speed = `setpts=PTS/2` + `atempo=2.0`; `atempo` only supports 0.5–2.0.
   - NVENC option names use hyphens: `-spatial-aq`, `-temporal-aq` (underscores
     are rejected). Source is decoded by CPU; encoding runs on the GPU.
   - "Late SEI is not implemented" h264 decoder warnings during pass 1 are
     harmless; ignore them.
   - Always verify with `ffprobe` that BOTH streams have the same duration
     (video and audio should both be ≈ source/2); a shorter audio duration means
     the one-pass truncation bug hit. Also verify 2x timing by comparing an
     output frame at t against the source frame at 2t cropped to W (mean abs
     diff should be < ~1); remember to crop the source frame before diffing,
     otherwise shapes mismatch (1440 vs 1920).

## Key gotchas

- The 5th YouTube downloader build path above is winget-specific; use
  `Get-ChildItem`/`where.exe ffmpeg` if it changes.
- `whisper_results.json` segments: `[{start, end, text}]`; build crossref by
  bucketing `start//60`.
- OCR text is noisy for browser UI text (garbled Chinese) — use keyword regex
  hits and URL extraction, not exact matching.
- ffmpeg one-pass combined video+audio transcode truncates the AAC track; use
  the two-pass + `-c copy` mux from Workflow B. Verify both stream durations.
- Never `git add` the videos/analysis output (hundreds of GB). Only commit
  `pipeline/`, docs, and small artifacts.
- Batch crop+2x jobs: run boundary detection for ALL videos in one Python
  script first (fast), then transcode sequentially. Pass 1 ≈ 5.5 min per
  ~2.6h video at 13.7x realtime; audio pass ≈ 45s at ~105x.
- `pypdf` is NOT installed; PIL cannot reopen saved PDFs — verify PDF page
  counts by raw-byte counting (see Keyframe PDF section).
- When a task spans several long GPU stages (OCR then Whisper), run them
  sequentially, not concurrently: each works fine alone on the 16GB card and
  sequencing keeps ETA predictable.
- Project README for the n8n pipeline lives at
  `E:\01-Project\2026_08_n8n_itri\README.md` — keep it in sync when scripts change.
- n8n course status (2026-08-22): all 4 videos fully analyzed; reports + keyframe
  PDFs under `analysis/<name>/`. Re-running any stage is safe — frame extraction
  wipes frames/ first, OCR resumes from ocr_results.json, whisper overwrites.
