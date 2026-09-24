---
name: video-class-pipeline
description: Use when the user asks to analyze/process 課程影片 (course videos), YouTube live-recorded class sessions, screen-recording videos, or any workflow involving video download, frame extraction, OCR, Whisper transcription, per-minute cross-reference, keyframe PDFs, video cropping, or 2x speed conversion. Covers the Python AI course project at E:\01-Project\2026-07-B-python_ai_tvdi, the n8n course project at E:\01-Project\2026_08_n8n_itri, and the TVDI n8n course at D:\80-Opnecode\Projects\2026_08_n8n_tvdi (13 sessions, all encoded + analyzed + reported as of 2026-09-18).
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
- GPU deps installed: `torch` (CUDA), `whisper`, `paddlepaddle-gpu`, `paddleocr`,
  `opencv-python`, `Pillow`, `yt-dlp`.
- **ASR engine = Breeze-ASR-25** (MediaTek: Whisper-large-v2 fine-tune for Taiwanese
  Mandarin + 中英混用 + 字幕級時間戳), switching 2026-09-21 — still evaluating vs
  `whisper`/`sensevoice` via `--engine`. Deps: `faster-whisper` (+ `transformers` HF
  fallback for Blackwell), and `funasr==1.3.29` only for the SenseVoice backup path.
- **OCR engine = PaddleOCR PP-OCRv5 server** (replaced EasyOCR 2026-09-21). Install
  **requires the cu129 wheel** — RTX 5080 is Blackwell (sm_120), the old cu126/cu118
  builds report `Unsupported GPU architecture`:
  ```powershell
  $py -m pip install paddlepaddle-gpu==3.2.2 -i https://www.paddlepaddle.org.cn/packages/stable/cu129/
  $py -m pip install -U "paddleocr"
  ```
  Prereqs: NVIDIA driver supporting CUDA ≥ 12.9, Python 3.8–3.12 (this box is 3.12 ✓).
  First `predict()` auto-downloads the det + rec models (~130 MB); subsequent runs offline.
  Smoke test before use: `$py -c "import paddle; paddle.utils.run_check()"`.
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
  ocr_frames.py <idx>              PaddleOCR PP-OCRv5_server 繁/英 GPU, resumes, writes ocr_results.json
  whisper_transcribe.py <idx>      Breeze-ASR-25 on CUDA (default), --engine whisper|sensevoice -> whisper_results.json + .txt
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
ocr_frames.py <idx>       PaddleOCR PP-OCRv5_server 繁/英 GPU, resume-safe -> ocr_results.json
extract_audio.py <idx>    audio.wav 16k mono
whisper_transcribe.py <idx>  Breeze-ASR-25 on CUDA (--engine whisper|sensevoice) -> whisper_results.json + whisper_transcription.txt
build_github_index.py     verified term index from github_materials/ clones -> github_index.json
gh_match.py               find_matches(text) against the index; extract_urls()
build_crossref.py <idx>   per-minute speech + best OCR frame + URLs + GH matches
make_report.py <idx>      report_<name>.md: timeline table, URL frames, GH hit stats,
                          hallucination filtering, quality notes
make_keyframes_pdf.py <idx>  keyframes_<name>.pdf — ONE frame per page
```

Observed timings (**pre-PaddleOCR**, EasyOCR era — re-measure after migration):
OCR 0.76–0.82 f/s → 460 frames ≈ 9.5 min, 790 frames ≈ 17 min;
Whisper medium zh CUDA: 77-min audio → ~6.5 min (2412 segs), 131-min audio →
~7.5 min (3069 segs) — **also pre-Breeze-ASR**, re-measure after the engine switch. PP-OCRv5 server predicts in ~8 ms/frame; expect the whole
OCR stage to drop well below the EasyOCR figure (dominated by startup + per-frame
det/rec scheduling, not inference). The Whisper tqdm bar can
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

Whisper zh invents stock phrases on silence/noise (Breeze-ASR-25, still Whisper-based,
reduces but does not remove this; SenseVoice mostly removes it). Filter with a HALLU regex:
`点赞|打赏|明镜与点点|Amara\.org|谢谢观看|謝謝觀看|訂閱.{0,6}轉發|字幕.{0,4}提供`.
In make_report.py such segments are excluded from the timeline and counted in a
「資料品質備註」 section. Observed counts vary a lot per video: 63 segments in one
114-min video, 1 in another, and **0 in both 08_20 videos** — always run the
filter, never assume.
Also note browser-menu garbled Chinese (楢案=檔案 style errors) occurred under
EasyOCR; PP-OCRv5 (繁中準確率 93.29%) is expected to reduce these — still spot-check
a few frames per video and never attribute a garble to content.

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

## Third project: n8n course (tvdi) — Intel-only machine (2026-09-17) ✓ COMPLETE

A different machine/project from the RTX 5080 setup above. Windows, **Intel UHD 770 (no NVIDIA)**,
Python 3.13 (`py`), user `N000149839`. Both encoding (Workflow B) AND full analysis
(ASR + OCR + reports + keyframe PDFs) are now COMPLETE for all 13 sessions.

### Environment / project facts
- Project dir: `D:\80-Opnecode\Projects\2026_08_n8n_tvdi\` (downloads + `<name>_裁切2倍速.mp4`).
- ffmpeg/ffprobe: **v9.0 essentials** at `C:\Users\N000149839\AppData\Local\Temp\opencode\bin\`
  (copied from `D:\80-Opnecode\Workspace\_maidate_work\ffmpeg_pkg\ffmpeg-9.0-essentials_build\bin\`);
  `deno.exe` alongside (copied from `C:\Users\N000149839\.lmstudio\.internal\utils\deno.exe`).
- Encoder is **`h264_qsv`** (Intel QSV), **not NVENC**, but the same two-pass + `-c copy` mux recipe
  applies (video pass → crop + `setpts=PTS/2` + `fps=30`; audio pass → `atempo=2.0` + AAC; mux).
  Set via `-c:v h264_qsv -preset veryfast -global_quality 24`.
- ASR engine on this machine: **`whisper-large-v3-ov2`** (OpenVINO GenAI, Intel GPU) — see the
  `video2text` skill; transcription of all 13 sessions finished in one background batch
  (log `_v2t_work\logs\asr_all.log`, ~47684s audio total; per-session `asr\...\transcript_zh.json`).

### Workflow B (encoding) results
- 13 videos (`2026_08_25_上午` … `2026_09_17_上午`). 12 downloaded with the `yt-batch-download`
  skill; the 13th was still LIVE and recorded with `--live-from-start`, then processed identically.
- All 1920x1080 30fps; crop boundary identical on every sampled frame:
  **`crop=1440:1080:0:0`** (right content edge x=1440; dark top rows y<67 and bottom y>1006 kept).
- Output `<name>_裁切2倍速.mp4` = 1440x1080 h264+aac; every file's video and audio durations match
  and equal source/2.
- Throughput ≈ **11–12x realtime** (video pass), audio pass ≈ 100–150x; the whole ~37 h source batch
  took ≈ 2.5 h wall clock, run sequentially, launched in the background.
- Full recipe / resumable Python batch driver: see the `video-2x-speed` skill
  ("Full-file QSV batch variant").

### Workflow C — tvdi analysis (reports + keyframe PDFs) — per-session loop that completed all 13
Analysis of the 2x videos is done under `_v2t_work\` in the project dir (NOT the RTX `pipeline/`
layout). Per BASE (`2026_MM_DD_上午|下午`) the loop is:
1. Frame extraction + RapidOCR every **15 s (2x) = 30 s orig** → `slides_text_<BASE>_非空.txt`
   (frames with ratio < 0.35 merged into slides groups; `S###` group / `f000##` frame / 2x + orig times).
2. Whisper ASR already complete for all 13 sessions → `transcript_zh_<BASE>.txt` + `kws_<BASE>.txt`
   (keyword line extracts: openrouter/model/llm/ai/key/api/credential/base url/DataTable/... via
   keyword list; a fixed `kws_` script run per session). Use `json.load(...transcript_zh.json)`
   and slice `segments[].start/end` windows to re-verify any segment.
3. Write `2026_<BASE>_重點整理.md` at project ROOT with the standard report sections:
   一、課程資訊（meet.google.com/xrj-wzhn-yrv、Youtube id from `github_materials\__2026_08_25_n8n_tvdi__\link\README.md`、
   教材 paths）｜ 二、課程時軸（2x時間|原片時間|主題）｜ 三、課程重點內容｜ 四、GitHub 教材對照表
   ｜ 五、今日收穫總結｜ 六、附註。
4. Edit `_v2t_work\make_pdf_v2.py` KEYFRAMES (overwrite the previous session's list; ~15 anchors,
   titles + OCR snippet; pick OCR frames that carry the session's key teaching points) → run
   `python make_pdf_v2.py <BASE> <BASE>` → `2026_<BASE>_關鍵幀-v2.pdf` (A4 landscape full-frame +
   right caption column, CJK font `C:\Windows\Fonts\msjh.ttc`, pages=~13-16).
5. Update the session todo (one `in_progress` at a time); verify file exists + PDF page count.

Deliverable set now present (project root): **13 × `2026_*.md` + 13 × `2026_*_關鍵幀-v2.pdf`**.

### ASR hallucination filter (tvdi)
Whisper `請以繁體中文輸出。` repeats at every 30-min window boundary plus stock phrases
(`請不吝點贊 訂閱 轉發 打賞支援明鏡與點點欄目`, `我是一個很好的人`, ...). Filter them out of the
report content and keyword hits (skip segments starting `请` / containing `明鏡`, `點贊`, `我是一個很好`).
Report convention: filter them without mentioning; keep 附註 to note they were filtered.

### Session archive
- Prior sessions 08_25 上午/下午, 08_27 上午/下午, 09_01 上午/下午, 09_03 上午 already had
  report+PDF in the "Third project" flow iterations; the current pass added
  09_03下午, 09_08上午/下午, 09_10上午/下午, 09_17上午 and closed the set.
- Course repo `github_materials\__2026_08_25_n8n_tvdi__\`: folders `08_27`, `0908` (NOT `09_08`),
  `09_01`, `09_03`, `09_10`, `n8n-ngrok`, `n8n-cloudflare`, `link`, `學員作品`. Main materai in
  `github_materials\n8n\` (openrouter, line設定, AI_Agent\段一|段二, DataTable, Google雲端設定).
- Each 2x frame index i → 2x time=(i-1)*15s, orig time=(i-1)*30s.

### PaddleOCR PP-OCRv5 server — ocr_frames.py 設計

Replace the old EasyOCR call site in `pipeline/ocr_frames.py` with the PaddleOCR 3.x API
(PaddleOCR 3.x + PP-OCRv5 server models; `lang="ch"` covers 繁中+簡中+英+日 in ONE model,
繁中準確率 93.29%):

```python
import json, glob, io, sys
import numpy as np, cv2
from paddleocr import PaddleOCR

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ocr = PaddleOCR(
    lang="ch",                       # uses PP-OCRv5_server_det + PP-OCRv5_server_rec
    use_doc_orientation_classify=False,   # no card/scan doctor needed for screen frames
    use_doc_unwarping=False,
    use_textline_orientation=False,
    device="gpu",                    # RTX 5080; omit -> auto (gpu if available)
)

def ocr_frame(path):
    res = ocr.predict(path)          # accept str path (cv2.imread chinese-path bug also
    r = res[0]                       #  affects paddle? -> pass np.ndarray via np.fromfile+imdecode)
    texts = [t for t, s in zip(r.rec_texts, r.rec_scores) if float(s) >= 0.75]
    boxes = [[[int(x), int(y)] for x, y in p] for p in r.rec_polys]
    return texts, boxes
```

- **Schema preservation (CRITICAL)**: `make_report.py` reads the item dict via
  `item["ocr_text"]`. Before overwriting, read one existing `ocr_results.json` and copy the
  exact item keys (frame/ocr_text/score/box…) into the PaddleOCR writer — keep `ocr_text`
  unchanged, `boxes` as `[[[x,y]…4pt], …]`. Wrong keys silently blank the report.
- **Resume-safe**: skip frames whose `ocr_results.json` entry already exists (same as EasyOCR
  era) — re-running after a timeout just continues.
- **Score cutoff 0.75** mirrors the old filter; drop the meeting-clock / chat `+N` / truncated
  name-badge / brand-watermark noise the same way as before.
- Loading is one-time ~1–2 s; first call downloads models (~130 MB). PaddleOCR 3.x prints loud
  inference logs — ignore or route to stderr.
- Chinese/non-ASCII paths: pass the frame as `np.ndarray` (`np.fromfile` + `cv2.imdecode`) to
  `ocr.predict` to dodge filesystem path bugs.

### ASR engine migration — Breeze-ASR-25 (whisper_transcribe.py 設計)

Swap the Whisper "medium" zh call site in `pipeline/whisper_transcribe.py` to
**Breeze-ASR-25** (MediaTek: Whisper-large-v2 (1.55B) fine-tune for Taiwanese Mandarin +
中英句內/句外混用 + 強化時間戳對齊; CommonVoice zh-TW WER 7.97 vs Whisper-large-v2 9.84 /
large-v3 8.95; ML-lecture-long 4.98 vs 6.13). Native 繁體 output — no OpenCC needed on this
path. Status: switching 2026-09-21; the old engine stays behind `--engine` until the A/B eval.

**One script, three engines (`--engine {whisper|breeze|sensevoice}`, default `breeze`):**

- `breeze` (primary) — load a CTranslate2 port with faster-whisper:
  `WhisperModel("SoybeanMilk/faster-whisper-Breeze-ASR-25", device="cuda",
  compute_type="float16")` (or `phate334/Breeze-ASR-25-ct2`); segments natively carry
  `start/end/text`.
  ⚠️ **Blackwell smoke test first**: CTranslate2 may not have sm_120 kernels yet (a known
  Breeze guide falls back to HF on Blackwell). If CT2 load/run fails, use the HF path from
  the model card: `WhisperForConditionalGeneration` + `WhisperProcessor` +
  `AutomaticSpeechRecognitionPipeline(..., chunk_length_s=0, return_timestamps=True)`,
  bf16 + `attn_implementation="sdpa"`. Same segment schema either way.
- `sensevoice` (backup, fastest ≈ 170x realtime, zh CER 7.81%) — `funasr==1.3.29`:
  ```python
  from funasr import AutoModel
  model = AutoModel(model="iic/SenseVoiceSmall", vad_model="fsmn-vad",
                    vad_kwargs={"max_single_segment_time": 30000}, device="cuda:0")
  res = model.generate(input="audio.wav", cache={}, language="auto", use_itn=True,
                       batch_size_s=60, merge_vad=True, sentence_timestamp=True)
  # segs = [(s["start"]/1000, s["end"]/1000, clean(s["text"]))
  #          for s in res[0]["sentence_info"]]
  ```
  **輸出是簡中 → `OpenCC("s2twp")` 先轉繁體**; strip `<|...|>`/emotion/event tags with
  `rich_transcription_postprocess`. Needs funasr ≥ 1.3.29 for VAD segment timestamps.
- `whisper` (original fallback) — keep the existing `Whisper("medium", device="cuda",
  language="zh")` path untouched.

- **Schema preservation (CRITICAL)**: `build_crossref.py` buckets by `start//60`;
  `make_report.py` reads `{start, end, text}`. Before overwriting, read one existing
  `whisper_results.json` and copy the exact keys; write segments as
  `[{"start": s, "end": e, "text": t}, ...]`. Wrong keys silently blank the timeline.
- **繁中策略**: `breeze` outputs 繁體 natively (keep as-is); `sensevoice` emits 簡中 —
  `OpenCC("s2twp")` only on that path. Do NOT apply OpenCC to breeze output (double
  conversion corrupts code-mixed text).
- **Hallucination**: keep the HALLU regex — breeze (Whisper-based) still echoes stock
  phrases on silence occasionally; sensevoice (non-autoregressive + VAD) largely removes them.
- **A/B eval first (Phase 3), no silent default flip**: on one existing
  `analysis/<name>/audio.wav`, run all three engines and record RTF (medium-zh CUDA
  baseline: 77-min audio → ~6.5 min ≈ 12x), segment count, last-segment end vs ffprobe
  duration, HALLU-regex hit count, and a proper-noun spot-check for the session (model
  names / API terms / `楢案→檔案`-style garble). Only switch the default once breeze wins
  or ties on those.
- **Reference code (this skill folder)**: `asr/whisper_transcribe.py` (engine-aware,
  schema-preserving drop-in for `pipeline/whisper_transcribe.py`) and
  `asr/asr_ab_eval.py` (A/B benchmark printing RTF/segs/last_end/hallu/preview per
  engine; one failing engine never stops the run). On the RTX host: `git pull`, copy
  both into `pipeline/`, then run the Blackwell smoke test + A/B eval.

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

Observed timings (RTX 5080, ~3h video, 1090 frames; OCR figure is pre-PaddleOCR,
whisper figure is pre-Breeze-ASR — re-measure both):
- frame extraction ~2-4 min, OCR ~24 min (0.77 f/s, EasyOCR — re-measure), whisper ~8 min,
  NVENC transcode ~6.5 min at ~413 fps (13.8x realtime).

## Workflow B — crop black bar + 2x speed (GPU)

> On an **Intel-only** machine there is no NVENC — substitute `h264_qsv`
> (`-c:v h264_qsv -preset veryfast -global_quality 24`); the two-pass + mux recipe is otherwise
> identical. See the `video-2x-speed` skill ("Full-file QSV batch variant") and the
> "Third project: n8n course (tvdi)" section above.

1. Find the crop boundary programmatically (do NOT guess or eyeball if image
   input is unavailable). Probe `ffprobe` for width/height, then use OpenCV:
   column-mean profile to find the rightmost bright column (`colmean > 30`),
   and PaddleOCR (PP-OCRv5) detect on the top-right quadrant crop to
   confirm the time/date text (e.g. "上午8:55") sits inside the white region —
   the date/time text is the box whose `rec_texts` matches a `\d+月\d+日` /
   `上午|下午\s*\d+:\d+` pattern; check its `dt_polys` stays left of the boundary.
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
- OCR text is noisy for browser/screen UI text (some garbled Chinese remains even
  under PaddleOCR) — use keyword regex hits and URL extraction, not exact matching.
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
