import sys
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()
img = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else img + ".txt"
result, _ = ocr(img)
lines = []
if result:
    for box, text, score in result:
        xs = [p[0] for p in box]; ys = [p[1] for p in box]
        x0, y0 = int(min(xs)), int(min(ys))
        x1, y1 = int(max(xs)), int(max(ys))
        lines.append(f"[x{x0}-{x1},y{y0}-{y1}] {text}")
else:
    lines.append("(no text)")
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("wrote", out, len(lines), "lines")