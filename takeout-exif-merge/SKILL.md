---
name: takeout-exif-merge
description: Use when the user asks to merge Google Photos Takeout supplemental-metadata.json sidecar files into the same-named image/video files (寫入JSON EXIF到同名影片圖片), process a Takeout Google 相簿 folder, or generate EXIF合併成果報告 style reports. Covers JSON<->media filename pairing (including (N) counter files), content-type vs extension mismatch handling, parallel exiftool -stay_open in-place writes, mtime/EXIF verification, and Markdown summary reports.
---

# Google Photos Takeout EXIF Merge

Merge `*.jpg.supplemental-metadata.json` (and `(N)` counter variants) sidecar metadata into the media files in place, using ExifTool. Proven pipeline: `scripts/merge_exif.py` (Python 3 + ExifTool via winget/`OliverBetz.ExifTool`).

## Key Facts

- **JSON naming**: `foo.jpg.supplemental-metadata.json` ↔ media `foo.jpg`; `foo.jpg.supplemental-metadata(1).json` ↔ `foo(1).jpg` (also form B: `foo(1).jpg.supplemental-metadata.json`).
- **JSON keys**: `photoTakenTime`/`creationTime` (`timestamp` = UTC epoch string), `geoData{latitude,longitude,altitude}`, `title`, `description`, `people[].name`, `favorited`.
- **Content ≠ extension** (Google re-encodes but keeps original names): `.heic/.png/.arw/.dng` files whose content is real **JPEG**, and `.mts/.avi` files whose content is real **MOV**. ExifTool REFUSES writes when extension ≠ content. Detect magic bytes (`FF D8 FF`=jpeg, `ftyp` brand) and write via a temp copy with the correct extension, then `os.replace` back.
- **Structurally damaged files** (Truncated SubIFD / Bad SubIFD format / Truncated mdat / BMP): exiftool refuses to rewrite (it protects the file). Fallback: set file mtime via `os.utime` so at least the timestamp is right.
- **Environment gotchas**: PowerShell console mangles Chinese (CP950) — set `PYTHONIOENCODING=utf-8` / `sys.stdout.reconfigure(encoding='utf-8')`; `Set-Content` writes UTF-8 BOM (strip it when reading back retry lists).
- ~1 file/sec/worker throughput; 8 workers ≈ 55 min for ~315k files (plus ~18 min JSON tag-build). Use `-stay_open True -@ -` for writes; sync per-file with the stdout status line.

## Script Usage

```bash
python merge_exif.py build "D:\...\Google 相簿" pairs.tsv            # scan + pair JSON<->media
python merge_exif.py run --exe "C:\Users\4pins\AppData\Local\Programs\ExifTool\ExifTool.exe" --pairs pairs.tsv --progress progress.txt --workers 8
python merge_exif.py run --exe <exe> --pairs pairs.tsv --progress progress.txt --workers 4 --retry-from fail_list.txt
python merge_exif.py verify --exe <exe> --pairs pairs.tsv --out verify.csv --sample 20
```

- Pairs TSV columns: `media_path  JSON_path  dir|global` (matching is same-dir first, then global name fallback).
- `--retry-from`: force re-process a list of media paths (skip progress set). Verify CSV statuses: `ok` (mtime == photoTakenTime ±1s) / `fail` / `no_time_in_json`.
- Progress file makes the run resumable (skip already-done). Worker stderr logs: `<progress>.w{0..N}.log`.

## Tag Mapping

- Time = `photoTakenTime` (UTC), formatted `YYYY:MM:DD HH:MM:SS`, declared `+00:00`.
- Images (EXIF-capable jpeg/png/tiff-family/heic/avif): `EXIF:DateTimeOriginal/CreateDate/ModifyDate`, `OffsetTime* = +00:00`, `XMP:CreateDate/ModifyDate`, `FileModifyDate`/`FileCreateDate` (with `+00:00` suffix so mtime = UTC epoch exactly → verifiable via `os.stat`).
- Videos (mov/mp4): `QuickTime:CreateDate/ModifyDate`, `TrackCreateDate/TrackModifyDate`, `MediaCreateDate/MediaModifyDate`, XMP dates, file dates, with `-api QuickTimeUTC=1`.
- GIF/WebP/BMP: XMP dates + file dates only (no EXIF support).
- GPS (only if lat/lon non-zero): EXIF GPS (`GPSLatitude/Longitude` + Ref, `GPSAltitude`, `GPSDateStamp`, `GPSTimeStamp`, `GPSMapDatum=WGS-84`) + XMP GPS; videos get XMP GPS only.
- `title`→`XMP:Title`; `description`→`XMP:Description` + `EXIF:ImageDescription`; people→`XMP:PersonInImage+=` (one arg per person).
- Common args: `-overwrite_original -api QuickTimeUTC=1 -api largefilesupport=1 -e -api duplicates=1`.

## Workflow Checklist

1. Run `build` on the album root (`...\Google 相簿`). Note: leftover JSONs = duplicate sidecars (same photo in album + year folder); unpaired media keep original state.
2. Run `run` (8 workers). Check worker logs for real `Error:` lines (not `[minor]`).
3. `verify` → mtime pass is authoritative; sample exiftool readbacks prove tags are physically present.
4. Extract `fail` rows → `--retry-from` → re-verify.
5. Write Markdown report (`EXIF合併成果報告.md`-style): totals, paired/unpaired/leftover counts, fully-written vs mtime-only counts, the ~86-file corruption categories, verification results.

## Report Numbers (accounts can differ; recompute per dataset)

- Total media vs JSON; paired (usually ~96% of media); leftover JSON ~10k (duplicate sidecars); unpaired media (no usable JSON).
- Fully-written via exiftool ≈ pairs − mtime-only count; mtime-only ≈ 86 on the 830 GB dataset (41 Truncated SubIFD, 25 Bad SubIFD format, 3 Truncated mdat, 3 read errors, 1 BMP; 9 MTS/AVI-as-MOV fixed on retry).