# -*- coding: utf-8 -*-
"""
Breeze-ASR-25 engine-aware transcriber (schema-preserving replacement for the
Whisper-medium call site in the RTX 5080 video-class pipeline).

Run:
    python whisper_transcribe.py <idx> [--engine breeze] [--audio <wav>] [--out <json>]

Engines (see SKILL.md > "ASR engine migration"):
    breeze     Breeze-ASR-25 via faster-whisper (CTranslate2); falls back to the
               HF bf16 path when CT2 has no sm_120 (Blackwell) kernels
    sensevoice SenseVoice-Small via funasr>=1.3.29, 简中 -> OpenCC s2twp 繁中
    whisper    original Whisper "medium" zh on CUDA

Schema preservation (CRITICAL): read an existing whisper_results.json first and
mirror its container shape (list, or dict with a `segments` key) and segment
keys. Downstream build_crossref.py buckets by start//60; make_report.py reads
{start, end, text}.
"""

import argparse
import io
import json
import os
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def audio_duration(path):
    try:
        import soundfile as sf
        return sf.info(path).duration
    except Exception:
        pass
    try:
        import torchaudio
        info = torchaudio.info(path)
        return info.num_frames / info.sample_rate
    except Exception:
        pass
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True)
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def resolve_audio(idx, audio_arg):
    if audio_arg:
        return os.path.abspath(audio_arg)
    try:
        import paths
        return os.path.join(paths.workdir_for(idx), "audio.wav")
    except Exception:
        pass
    for cand in (os.path.join("analysis", str(idx), "audio.wav"), "audio.wav"):
        if os.path.exists(cand):
            return os.path.abspath(cand)
    raise SystemExit("audio.wav not found; pass --audio <wav>")


def resolve_out(idx, out_arg):
    if out_arg:
        return os.path.abspath(out_arg)
    try:
        import paths
        return os.path.join(paths.workdir_for(idx), "whisper_results.json")
    except Exception:
        return os.path.abspath("whisper_results.json")


def segment_keys(existing):
    if isinstance(existing, list) and existing and isinstance(existing[0], dict):
        return set(existing[0].keys())
    if isinstance(existing, dict):
        segs = existing.get("segments")
        if isinstance(segs, list) and segs and isinstance(segs[0], dict):
            return set(segs[0].keys())
    return {"start", "end", "text"}


def write_results(segments, out_json):
    segs = [{"start": float(s), "end": float(e), "text": str(t)}
            for s, e, t in segments if str(t).strip()]
    existing = {}
    if os.path.exists(out_json):
        try:
            with open(out_json, encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = {}
    keys = segment_keys(existing)
    kept = []
    for s in segs:
        row = {}
        for k in keys:
            if k in s:
                row[k] = s[k]
            elif k == "text":
                row[k] = ""
            else:
                row[k] = 0
        kept.append(row)
    payload = dict(existing) if isinstance(existing, dict) else []
    if isinstance(payload, dict):
        payload["segments"] = kept
    else:
        payload = kept
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    txt = out_json.rsplit(".", 1)[0]
    if txt.endswith("whisper_results"):
        txt = txt.replace("whisper_results", "whisper_transcription")
    txt += ".txt"
    with open(txt, "w", encoding="utf-8") as f:
        for s in segs:
            f.write("[%.1f - %.1f] %s\n" % (s["start"], s["end"], s["text"]))
    return out_json, txt


def engine_whisper(audio_path):
    import whisper
    model = whisper.load_model("medium", device="cuda")
    out = model.transcribe(audio_path, language="zh")
    return [(s["start"], s["end"], (s.get("text") or "").strip())
            for s in out.get("segments", [])]


def engine_breeze(audio_path):
    try:
        from faster_whisper import WhisperModel
        m = WhisperModel("SoybeanMilk/faster-whisper-Breeze-ASR-25",
                         device="cuda", compute_type="float16")
        segs, _ = m.transcribe(audio_path, language="zh", beam_size=5)
        return [(s.start, s.end, (s.text or "").strip()) for s in segs]
    except Exception:
        pass
    import torch
    from transformers import (AutomaticSpeechRecognitionPipeline,
                              AutoModelForSpeechSeq2Seq, AutoProcessor)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        "MediaTek-Research/Breeze-ASR-25", torch_dtype=torch.bfloat16,
        attn_implementation="sdpa", low_cpu_mem_usage=True).to("cuda")
    proc = AutoProcessor.from_pretrained("MediaTek-Research/Breeze-ASR-25")
    pipe = AutomaticSpeechRecognitionPipeline(
        model=model, tokenizer=proc.tokenizer,
        feature_extractor=proc.feature_extractor, torch_dtype=torch.bfloat16,
        device="cuda", return_timestamps=True, chunk_length_s=0)
    out = pipe(audio_path, generate_kwargs={"language": "zh",
                                            "task": "transcribe"})
    dur = audio_duration(audio_path)
    chunks = out.get("chunks") or []
    segs = []
    for c in chunks:
        ts = c.get("timestamp") or (0, dur)
        start = ts[0] or 0.0
        end = ts[1] if ts[1] is not None else dur
        segs.append((start, end if end > start else start + 1.0,
                     (c.get("text") or "").strip()))
    return segs


def strip_sv(text):
    import re
    t = re.sub(r"<\|[^|]*\|>", "", text)
    for tag in ("[微笑]", "[笑]", "[掌声]", "[音乐]", "[犹豫]",
                "[惊讶]", "[咳嗽]", "[欢呼]", "[NOISE]", "[LAUGH]",
                "[MUSIC]", "<pad>", "</s>"):
        t = t.replace(tag, "")
    return t.strip()


def engine_sensevoice(audio_path):
    from funasr import AutoModel
    from funasr.utils.postprocess_utils import rich_transcription_postprocess

    model = AutoModel(model="iic/SenseVoiceSmall", vad_model="fsmn-vad",
                      vad_kwargs={"max_single_segment_time": 30000},
                      device="cuda:0")
    res = model.generate(input=audio_path, cache={}, language="auto",
                         use_itn=True, batch_size_s=60, merge_vad=True,
                         sentence_timestamp=True)
    info = res[0].get("sentence_info") or []
    segs = []
    for s in info:
        raw = strip_sv(
            rich_transcription_postprocess(
                str(s.get("sentence", "") or s.get("text", ""))))
        if not raw:
            continue
        try:
            import opencc
            raw = opencc.OpenCC("s2twp").convert(raw)
        except Exception:
            pass
        start = int(s.get("start", 0)) / 1000.0
        end = int(s.get("end", 0)) / 1000.0
        segs.append((start, end if end > start else start + 1.0, raw))
    return segs


ENGINES = {"whisper": engine_whisper, "breeze": engine_breeze,
           "sensevoice": engine_sensevoice}


def main():
    ap = argparse.ArgumentParser(description="Engine-aware transcription")
    ap.add_argument("idx", type=int, nargs="?", default=0)
    ap.add_argument("--engine", choices=list(ENGINES), default="breeze")
    ap.add_argument("--audio", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    audio = resolve_audio(a.idx, a.audio)
    out_json = resolve_out(a.idx, a.out)
    t0 = time.time()
    segs = ENGINES[a.engine](audio)
    elapsed = time.time() - t0
    dur = audio_duration(audio)
    json_path, txt_path = write_results(segs, out_json)
    print("engine=%s audio=%s" % (a.engine, audio))
    print("segments=%d duration=%.0fs wall=%.0fs rtf=%.2fx"
          % (len(segs), dur, elapsed, elapsed / dur if dur else 0))
    print("wrote %s + %s" % (json_path, txt_path))


if __name__ == "__main__":
    main()