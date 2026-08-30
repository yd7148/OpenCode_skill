#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge Google Photos Takeout supplemental-metadata.json into media files in place.

build : scan root, match JSON <-> media (same-dir first, then global), write pairs TSV
run   : write metadata via exiftool -stay_open (parallel workers, ack-synced, resumable)
verify: check every pair's mtime vs expected photoTakenTime + sampled exiftool reads
"""
import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
sys.__stdout__.reconfigure(encoding="utf-8", errors="replace")

SUP_RE = re.compile(r"^(.+?)\.supplemental-metadata(?:\((\d+)\))?\.json$", re.I)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".avif", ".tif", ".tiff",
              ".bmp", ".dng", ".gif", ".webp",
              ".cr2", ".nef", ".orf", ".rw2", ".raf", ".sr2", ".srw", ".pef", ".x3f", ".arw"}
EXIF_EXTS = IMAGE_EXTS - {".gif", ".webp", ".bmp"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".wmv", ".flv", ".3gp", ".3g2",
              ".webm", ".mts", ".m2ts", ".mod", ".mpg", ".mpeg", ".ts", ".vob"}
MEDIA_EXTS = IMAGE_EXTS | VIDEO_EXTS

CONTENT_EXT = {"jpeg": ".jpg", "png": ".png", "gif": ".gif", "webp": ".webp",
               "tiff": ".tif", "heic": ".heic", "avif": ".avif", "bmp": ".bmp",
               "video": ".mp4", "mov": ".mov", "mp4": ".mp4"}
VIDEO_CONTENT = {"video", "mov", "mp4"}


def norm(p):
    return os.path.normcase(os.path.abspath(p))


def fmt_utc(ts):
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y:%m:%d %H:%M:%S")
    except (ValueError, OSError, OverflowError):
        return None


def json_time(data):
    t = data.get("photoTakenTime") or data.get("creationTime") or data.get("editedTime")
    if not t:
        return None
    return fmt_utc(t.get("timestamp"))


def media_candidates(jfn):
    m = SUP_RE.match(jfn)
    if not m:
        return []
    media, n = m.group(1), m.group(2)
    if n:
        stem, ext = os.path.splitext(media)
        return [stem + "(" + n + ")" + ext, media]
    return [media]


def detect_content(path):
    """Return coarse content family: jpeg,png,gif,webp,tiff,heic,avif,video,bmp,other."""
    try:
        with open(path, "rb") as fh:
            b = fh.read(32)
    except OSError:
        return "other"
    if b[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if b[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        return "webp"
    if b[:2] in (b"II", b"MM"):
        return "tiff"
    if b[4:8] == b"ftyp":
        brand = b[8:12]
        if brand in (b"heic", b"heix", b"hevc", b"hevx", b"mif1", b"msf1", b"heif",
                     b"heim", b"heis", b"hevm", b"hevs"):
            return "heic"
        if brand == b"avif":
            return "avif"
        if brand == b"qt  ":
            return "mov"
        if brand[:3] in (b"iso", b"mp4", b"avc"):
            return "mp4"
        return "other"
    return "other"


def ext_family(ext):
    low = ext.lower()
    if low in (".jpg", ".jpeg"):
        return "jpeg"
    if low == ".png":
        return "png"
    if low == ".gif":
        return "gif"
    if low == ".webp":
        return "webp"
    if low in (".tif", ".tiff", ".dng", ".arw", ".cr2", ".nef", ".orf", ".rw2", ".raf",
               ".sr2", ".srw", ".pef", ".x3f"):
        return "tiff"
    if low in (".heic", ".heif"):
        return "heic"
    if low == ".avif":
        return "avif"
    if low == ".bmp":
        return "bmp"
    if low == ".mov":
        return "mov"
    if low == ".mp4":
        return "mp4"
    if low in VIDEO_EXTS:
        return "video"
    return None


VIDEO_CONTENT = {"video", "mov", "mp4"}


def build_tags(data, content):
    """content: coarse family string. Returns list of exiftool args or None."""
    T = json_time(data)
    if T is None:
        return None
    dateonly = T.split(" ")[0]
    timeonly = T.split(" ")[1]
    zulu = T + "+00:00"
    tags = []
    if content in VIDEO_CONTENT:
        tags += [
            "-QuickTime:CreateDate=" + T,
            "-QuickTime:ModifyDate=" + T,
            "-QuickTime:TrackCreateDate=" + T,
            "-QuickTime:TrackModifyDate=" + T,
            "-QuickTime:MediaCreateDate=" + T,
            "-QuickTime:MediaModifyDate=" + T,
            "-XMP:CreateDate=" + T,
            "-XMP:ModifyDate=" + T,
            "-FileModifyDate=" + zulu,
            "-FileCreateDate=" + zulu,
        ]
    elif content in ("jpeg", "png", "tiff", "heic", "avif"):
        tags += [
            "-EXIF:DateTimeOriginal=" + T,
            "-EXIF:CreateDate=" + T,
            "-EXIF:ModifyDate=" + T,
            "-EXIF:OffsetTime=+00:00",
            "-EXIF:OffsetTimeOriginal=+00:00",
            "-EXIF:OffsetTimeDigitized=+00:00",
            "-XMP:CreateDate=" + T,
            "-XMP:ModifyDate=" + T,
            "-FileModifyDate=" + zulu,
            "-FileCreateDate=" + zulu,
        ]
    else:  # gif/webp/bmp
        tags += [
            "-XMP:CreateDate=" + T,
            "-XMP:ModifyDate=" + T,
            "-FileModifyDate=" + zulu,
            "-FileCreateDate=" + zulu,
        ]

    geo = data.get("geoData") or {}
    lat = geo.get("latitude") or 0
    lon = geo.get("longitude") or 0
    alt = geo.get("altitude") or 0
    if lat and lon:
        if content in VIDEO_CONTENT:
            tags += [
                "-XMP:GPSLatitude=" + str(lat),
                "-XMP:GPSLongitude=" + str(lon),
                "-XMP:GPSAltitude=" + str(alt),
                "-XMP:GPSDateTime=" + zulu,
            ]
        elif content in ("jpeg", "png", "tiff", "heic", "avif"):
            latref = "N" if lat >= 0 else "S"
            lonref = "E" if lon >= 0 else "W"
            tags += [
                "-GPSLatitude=" + str(abs(lat)),
                "-GPSLatitudeRef=" + latref,
                "-GPSLongitude=" + str(abs(lon)),
                "-GPSLongitudeRef=" + lonref,
                "-GPSAltitude=" + str(alt),
                "-GPSAltitudeRef=0",
                "-GPSDateStamp=" + dateonly,
                "-GPSTimeStamp=" + timeonly,
                "-GPSMapDatum=WGS-84",
                "-XMP:GPSLatitude=" + str(lat),
                "-XMP:GPSLongitude=" + str(lon),
                "-XMP:GPSAltitude=" + str(alt),
            ]

    title = (data.get("title") or "").strip()
    desc = (data.get("description") or "").strip()
    people = [p.get("name").strip() for p in (data.get("people") or []) if (p.get("name") or "").strip()]
    if title:
        tags.append("-XMP:Title=" + title)
    if desc:
        tags.append("-XMP:Description=" + desc)
    if content in ("jpeg", "png", "tiff", "heic", "avif") and desc:
        tags.append("-EXIF:ImageDescription=" + desc)
    for p in people:
        tags.append("-XMP:PersonInImage+=" + p)
    return tags


def scan(root):
    media_by_dir = {}
    json_by_dir = {}
    media_by_name = {}
    all_jsons = []
    nmedia = 0
    t0 = time.time()
    for dp, dirs, fns in os.walk(root):
        ndp = norm(dp)
        mdict = {}
        jdict = {}
        for fn in fns:
            if SUP_RE.match(fn):
                jdict[fn.lower()] = norm(os.path.join(dp, fn))
                all_jsons.append(norm(os.path.join(dp, fn)))
                continue
            ext = os.path.splitext(fn)[1].lower()
            if ext in MEDIA_EXTS:
                full = norm(os.path.join(dp, fn))
                mdict.setdefault(fn.lower(), []).append(full)
                media_by_name.setdefault(fn.lower(), []).append(full)
                nmedia += 1
        if mdict:
            media_by_dir[ndp] = mdict
        if jdict:
            json_by_dir[ndp] = jdict
        if nmedia % 80000 == 0 and nmedia:
            print(f"  scan ... {nmedia} media ({time.time()-t0:.0f}s)", flush=True)
    print(f"scan done: {nmedia} media, {len(all_jsons)} jsons, {time.time()-t0:.1f}s", flush=True)
    return media_by_dir, media_by_name, all_jsons, nmedia


def pair_scan(root):
    media_by_dir, media_by_name, all_jsons, nmedia = scan(root)
    used = set()
    pairs = []
    leftover = Counter()
    for jp in sorted(all_jsons, key=lambda p: p.lower()):
        jdir = os.path.dirname(jp)
        cands = media_candidates(os.path.basename(jp))
        picked = None
        md = media_by_dir.get(norm(jdir))
        if md:
            for c in cands:
                for p in md.get(c, ()):
                    if p not in used:
                        picked = p
                        break
                if picked:
                    break
        if not picked:
            for c in cands:
                for p in media_by_name.get(c, ()):
                    if p not in used:
                        picked = p
                        break
                if picked:
                    break
        if picked:
            used.add(picked)
            src = "dir" if (md and picked in {x for c in cands for x in md.get(c, ())}) else "global"
            pairs.append([picked, jp, src])
        else:
            leftover["no_media"] += 1
    return pairs, len(all_jsons), sum(leftover.values()), nmedia, len(used)


# ---------------- run ----------------

def spawn_worker(exe, errf, common_args):
    return subprocess.Popen(
        [exe, "-stay_open", "True", "-@", "-", "-common_args"] + common_args,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errf,
        text=True, encoding="utf-8", errors="replace", bufsize=1, close_fds=True)


def worker_loop(exe, jobs, progress_path, wid, common_args):
    errf = open(progress_path + f".w{wid}.log", "a", encoding="utf-8", errors="replace")
    ok = fail = fallback = 0
    try:
        with open(progress_path, "a", encoding="utf-8") as pf:
            i = 0
            while i < len(jobs):
                tmp = None
                proc = spawn_worker(exe, errf, common_args)
                try:
                    for media_path, tags, ets in jobs[i:]:
                        if not tags:
                            i += 1
                            continue
                        if tags[0] == "__BMP__":
                            if ets:
                                os.utime(media_path, (ets, ets))
                            ok += 1
                            pf.write(media_path + "\n")
                            pf.flush()
                            i += 1
                            continue
                        target = media_path
                        content_fam = detect_content(media_path)
                        fam = ext_family(os.path.splitext(media_path)[1])
                        mism = (fam != content_fam and content_fam != "other"
                                and fam is not None and content_fam in CONTENT_EXT)
                        if mism:
                            tmp = media_path + ".merge" + CONTENT_EXT[content_fam]
                            shutil.copy2(media_path, tmp)
                            target = tmp
                        lines = [target] + tags + ["-execute"]
                        proc.stdin.write("\n".join(lines) + "\n")
                        proc.stdin.flush()
                        ack = ""
                        while True:
                            ln = proc.stdout.readline()
                            if not ln:
                                break
                            ack += ln
                            if "image files updated" in ln or "had errors" in ln:
                                break
                        if "0 image files updated" in ack or "had errors" in ack:
                            fail += 1
                            if ets:
                                os.utime(media_path, (ets, ets))
                                fallback += 1
                            if tmp and os.path.exists(tmp):
                                os.unlink(tmp)
                        else:
                            ok += 1
                            if tmp:
                                os.replace(tmp, media_path)
                                tmp = None
                        pf.write(media_path + "\n")
                        pf.flush()
                        i += 1
                        if tmp and os.path.exists(tmp):
                            os.unlink(tmp)
                            tmp = None
                except Exception:
                    pass
                finally:
                    try:
                        proc.stdin.write("-stay_open\nFalse\n")
                        proc.stdin.flush()
                        proc.stdin.close()
                        proc.wait(timeout=8)
                    except Exception:
                        try:
                            proc.kill()
                        except Exception:
                            pass
        print(f"worker{wid}: ok={ok} fail={fail} mtime_fallback={fallback}", flush=True)
    finally:
        errf.close()


def run(exe, pairs_path, progress_path, workers, retry_from=None):
    pairs = {}
    with open(pairs_path, "r", encoding="utf-8") as f:
        for line in f:
            media, jsonp, src = line.rstrip("\n").split("\t")
            pairs.setdefault(norm(media).lower(), []).append((media, jsonp))
    done = set()
    if os.path.exists(progress_path):
        with open(progress_path, "r", encoding="utf-8", errors="replace") as f:
            done = {ln.rstrip("\n").lower() for ln in f}
    if retry_from:
        force = {norm(l.strip()).lower() for l in open(retry_from, "r", encoding="utf-8") if l.strip()}
        todo = [p for mk in force for p in pairs.get(mk, [])]
        print(f"retry list: {len(force)} paths", flush=True)
    else:
        todo = [p for lst in pairs.values() for p in lst if p[0].lower() not in done]
    print(f"pairs: {len(pairs)}, already done: {len(done)}, todo: {len(todo)}", flush=True)

    t0 = time.time()
    jobs = []
    failed_read = 0
    for m, j in todo:
        try:
            with open(j, "r", encoding="utf-8") as f:
                data = json.load(f)
            ts = json_time(data)
            ets = None
            if ts:
                ets = int(datetime.strptime(ts, "%Y:%m:%d %H:%M:%S")
                          .replace(tzinfo=timezone.utc).timestamp())
            cont = detect_content(m)
            if cont == "bmp":
                jobs.append((m, ["__BMP__", str(ets)], ets))
            else:
                tags = build_tags(data, cont)
                jobs.append((m, tags, ets))
        except Exception:
            failed_read += 1
    ok_tags = sum(1 for _, t, _ in jobs if t is not None)
    print(f"tag build done in {time.time()-t0:.1f}s; with_tags={ok_tags} no_time={len(jobs)-ok_tags} json_err={failed_read}", flush=True)

    chunks = [[] for _ in range(workers)]
    k = 0
    for m, t, e in jobs:
        if t is not None:
            chunks[k % workers].append((m, t, e))
            k += 1

    common_args = ["-overwrite_original", "-api", "QuickTimeUTC=1",
                   "-api", "largefilesupport=1", "-e", "-api", "duplicates=1"]
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(worker_loop, exe, chunks[i], progress_path, i, common_args)
                for i in range(workers)]
        for f in futs:
            f.result()
    print(f"run finished in {time.time()-t0:.1f}s", flush=True)


# ---------------- verify ----------------

def verify(exe, pairs_path, out_csv, sample):
    exp = {}   # norm(media).lower() -> (expected ts int or None, mediapath)
    with open(pairs_path, "r", encoding="utf-8") as f:
        for line in f:
            media, jsonp, _ = line.rstrip("\n").split("\t")
            try:
                with open(jsonp, "r", encoding="utf-8") as jf:
                    ts = json_time(json.load(jf))
                exp[norm(media).lower()] = (ts, media)
            except Exception:
                exp[norm(media).lower()] = (None, media)
    nok = nfail = nnone = 0
    issues = []
    out_f = open(out_csv, "w", encoding="utf-8-sig", newline="")
    out_f.write("media\texpected\tmtime_utc\tstatus\n")
    count = 0
    for mk, (T, media) in exp.items():
        try:
            mtime = round(os.stat(media).st_mtime)
        except OSError:
            mtime = None
        if T is None:
            nnone += 1
            status = "no_time_in_json"
            ets = None
        else:
            try:
                ets = int(datetime.strptime(T, "%Y:%m:%d %H:%M:%S")
                          .replace(tzinfo=timezone.utc).timestamp())
            except ValueError:
                ets = None
            if ets is not None and mtime is not None and abs(mtime - ets) <= 1:
                nok += 1
                status = "ok"
            else:
                nfail += 1
                status = "fail"
                issues.append((media, T, mtime))
        out_f.write(f"{media}\t{T or ''}\t{str(mtime) if mtime is not None else ''}\t{status}\n")
        count += 1
        if count % 50000 == 0:
            print(f"  verify ... {count}/{len(exp)} (ok={nok} fail={nfail})", flush=True)

    out_f.close()

    tot = nok + nfail
    print(f"verify(mtime): ok={nok} fail={nfail} json_no_time={nnone} total={tot}", flush=True)

    if sample and tot:
        picks = random.sample(range(tot), min(sample, tot))
        for idx in picks:
            mk = list(exp.keys())[idx]
            T, media = exp[mk]
            if T is None:
                continue
            r = subprocess.run([exe, "-j", "-n", "-DateTimeOriginal", "-GPSTimestamp",
                                "-GPSLatitude", "-GPSLongitude", "-CreateDate",
                                "-FileModifyDate", "-s", media],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
            print(f"  [sample] {os.path.basename(media)} | expected={T}")
            print(f"    exiftool out: {(r.stdout or r.stderr).replace(chr(10),' ')[:300]}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("build")
    p.add_argument("root")
    p.add_argument("out")
    p = sub.add_parser("run")
    p.add_argument("--exe", required=True)
    p.add_argument("--pairs", required=True)
    p.add_argument("--progress", required=True)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--retry-from")
    p = sub.add_parser("verify")
    p.add_argument("--exe", required=True)
    p.add_argument("--pairs", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--sample", type=int, default=0)
    a = ap.parse_args()
    if a.cmd == "build":
        pairs, njson, leftover, nmedia, npaired = pair_scan(a.root)
        with open(a.out, "w", encoding="utf-8") as f:
            for m, j, s in pairs:
                f.write(f"{m}\t{j}\t{s}\n")
        print(f"pairs={len(pairs)} jsons={njson} leftover_json={leftover} "
              f"media_total={nmedia} media_paired={npaired}")
    elif a.cmd == "run":
        run(a.exe, a.pairs, a.progress, a.workers, a.retry_from)
    elif a.cmd == "verify":
        verify(a.exe, a.pairs, a.out, a.sample)


if __name__ == "__main__":
    main()