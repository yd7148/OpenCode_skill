# -*- coding: utf-8 -*-
"""
A/B benchmark: Whisper "medium" zh vs Breeze-ASR-25 vs SenseVoice-Small on one wav.

Run (on the RTX host, next to whisper_transcribe.py):
    python asr_ab_eval.py --audio <audio.wav> [--engines whisper,breeze,sensevoice]

Prints per-engine: status, wall time, RTF, segment count, last-segment end vs
ffprobe duration, HALLU-regex hit count, and a preview. One engine failing does
not stop the run. See SKILL.md > "ASR engine migration A/B eval" for the pass
criteria before switching the pipeline default.
"""

import argparse
import io
import re
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from whisper_transcribe import (ENGINES, audio_duration)

HALLU = re.compile(
    r"点赞|打赏|明镜与点点|Amara\.org|谢谢观看|謝謝觀看|"
    r"訂閱.{0,6}轉發|字幕.{0,4}提供")


def main():
    ap = argparse.ArgumentParser(description="ASR A/B benchmark")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--engines", default="whisper,breeze,sensevoice")
    a = ap.parse_args()

    names = [e for e in a.engines.split(",") if e in ENGINES]
    dur = audio_duration(a.audio)
    print("audio=%s duration=%.0fs" % (a.audio, dur))
    print("%-10s%-8s%8s%7s%6s%10s%6s"
          % ("engine", "status", "wall", "rtf", "segs", "last_end", "hallu"))
    for name in names:
        t0 = time.time()
        try:
            segs = ENGINES[name](a.audio)
            wall = time.time() - t0
            last_end = segs[-1][1] if segs else 0.0
            hallu = sum(1 for _, _, t in segs if HALLU.search(t))
            print("%-10s%-8s%8.0f%7.2f%6d%10.1f%6d"
                  % (name, "ok", wall, wall / dur if dur else 0,
                     len(segs), last_end, hallu))
            print("  preview:")
            for s, e, t in segs[:5] + segs[-3:]:
                print("    [%8.2f - %8.2f] %s" % (s, e, t))
        except Exception as ex:
            wall = time.time() - t0
            print("%-10s%-8s%8.0f  %s: %s"
                  % (name, "FAILED", wall, type(ex).__name__, ex))


if __name__ == "__main__":
    main()