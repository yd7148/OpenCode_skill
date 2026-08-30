---
name: taipower-exam-solver
description: Use when the user asks to process 國營事業招考 (state-owned enterprise exam) PDF files from 台電/中油/台水/台糖, extract questions with pymupdf, solve exam problems (電路學, 電子學, 基本電學, etc.), search for official answer keys from taipower.com.tw, or generate detailed step-by-step solutions for exam papers. Covers PDF text/image extraction, web scraping of answer PDFs, and circuit/electronics problem solving.
---

# Taipower Exam Solver

End-to-end workflow for processing 國營事業 (state-owned enterprise) exam PDFs: extract questions, find official answers, and produce detailed solutions.

## Directory Structure

```
test-pdf/
  {year}/
    {subject}/
      提取結果_v4/          # OCR output directory
        q01.md              # Per-question OCR text
        q01.png             # Per-question cropped image
        完整解答.md          # Full solutions document
        exam_page1.png      # Rendered exam pages
        answer_page1.png    # Rendered answer pages
      *.pdf                 # Source exam/answer PDFs
```

## Key Files & Scripts

- `extract_questions.py` — Splits exam PDF into per-question images + OCR text
- `E:\01-Project\2026-07-B-python_ai_tvdi\extract_text_from_image.py` — General OCR utility

## Workflow

### Step 1: Extract Questions from PDF

Use `pymupdf` (fitz) to render PDF pages as images and extract text:

```python
import fitz  # pymupdf
doc = fitz.open("path/to/exam.pdf")

# Extract text per page
for page in doc:
    text = page.get_text()
    print(text)

# Render pages as images
mat = fitz.Matrix(3, 3)  # 3x zoom for clarity
page = doc[0]
pix = page.get_pixmap(matrix=mat)
pix.save("output.png")
```

**Important:** pymupdf text extraction often CANNOT capture circuit diagrams or vector graphics. Always render pages as images as a backup.

### Step 2: Find Official Answer Keys

**Taipower official answer PDFs:**
```
https://www.taipower.com.tw/2289/2544/2554/2556/simpleList
```

Direct PDF URL pattern:
```
https://www.taipower.com.tw/media/{hash}/{filename}?mediaDL=true
```

**Known 114年度 URLs:**
- 試題: `https://www.taipower.com.tw/media/yz3ciujc/114年度新進職員甄試試題科目A_電機_電路學電子學.pdf?mediaDL=true`
- 解答: `https://www.taipower.com.tw/media/mxkce0zb/114年度新進職員甄試試題解答A_電機_電路學電子學.pdf?mediaDL=true`

**Other sources:**
- Scribd: search `"年度新進職員甄試試題解答" site:scribd.com`
- 阿摩線上測驗: `https://yamol.tw/` (has question text, sometimes answers)
- 百官網公職: `https://byone.tkb.com.tw/downloads/` (has topic/answer downloads)
- 公職王: `https://www.public.com.tw/exampoint/`

### Step 3: Extract Answer from PDF

```python
import fitz, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

doc = fitz.open("path/to/answer.pdf")
for page in doc:
    text = page.get_text()
    print(text)
```

Answer format: Each question starts with `[X]` where X is the letter answer (A/B/C/D).

### Step 4: Solve Each Question

For **circuit diagram questions**: reconstruct circuit from component labels in PDF text. The labels appear near the diagram but connections (wires) are in vector graphics that text extraction misses. Use rendered images as reference.

For **text-based questions** (theory, calculations): solve directly using domain knowledge.

## Common Exam Types

| 科目 | Topics |
|------|--------|
| 電路學 | DC circuits, AC circuits, transient analysis, 3-phase, Laplace, two-port networks |
| 電子學 | BJT, FET, op-amp, digital logic, oscillators, power amplifiers |
| 基本電學 | Ohm's law, power, capacitors, inductors, basic AC, transformers |
| 電力系統 | Power generation, transmission, distribution, protection |
| 電機機械 | Transformers, motors, generators, equivalent circuits |

## Circuit Analysis Methods

1. **KVL/KCL** — Kirchhoff's voltage/current laws
2. **Nodal analysis** — Node voltage method
3. **Mesh analysis** — Loop current method
4. **Superposition** — Handle multiple sources separately
5. **Thevenin/Norton** — Equivalent circuits
6. **Source transformation** — Voltage ↔ current source
7. **Delta-Wye** — Δ-Y transformation for bridge circuits

## Electronics Formulas

**BJT:**
- $I_C = \beta I_B$, $I_E = (1+\beta)I_B$
- $g_m = I_C / V_T$ ($V_T ≈ 25$mV at room temp)
- Cutoff: $V_{BE} < 0.7$V; Saturation: $V_{CE} ≈ 0.2$V

**FET:**
- $I_D = K(V_{GS} - V_T)^2$ (saturation region)
- $g_m = 2K(V_{GS} - V_T) = 2\sqrt{K \cdot I_D}$

**Op-Amp (ideal):**
- Virtual short: $V_+ = V_-$
- Virtual open: input current = 0

**AC Power:**
- $P = V_{rms} I_{rms} \cos\phi$
- $S = V_{rms} I_{rms}$
- $Q = V_{rms} I_{rms} \sin\phi$

**Three-phase:**
- Y-connection: $V_L = \sqrt{3} V_P$, $I_L = I_P$
- Delta: $V_L = V_P$, $I_L = \sqrt{3} I_P$
- $P = \sqrt{3} V_L I_L \cos\phi$

## Limitations

- **pymupdf cannot read encrypted PDFs** — Taipower PDFs are sometimes password-protected
- **Circuit diagrams are vector graphics** — text extraction loses wiring topology; must render as images
- **Image input not supported by this model** — cannot directly "see" circuit diagrams from images
- **OCR quality varies** — Chinese + math symbols often garbled; cross-reference with web sources
