---
name: pdf-exam-extractor
description: Use when the user asks to extract individual questions from exam PDF files (考題PDF), perform OCR on each question, crop questions into separate images, or process 國營事業招考 (state-owned enterprise exam) papers. Covers PDF-to-image conversion, text position extraction with pdfplumber, question boundary detection, image cropping, and EasyOCR recognition.
---

# PDF Exam Extractor (考題PDF擷取與OCR)

Proven workflow for extracting individual exam questions from PDF files,
cropping each question into a separate image, performing OCR, and outputting
Markdown files for each question.

## Environment (Windows)

- Python: `C:\Users\4pins\AppData\Local\Programs\Python\Python312\python.exe`
- Required packages: `pymupdf`, `pdfplumber`, `easyocr`, `opencv-python`, `Pillow`
- GPU deps: `torch` (CUDA) for EasyOCR acceleration
- Chinese/non-ASCII paths break `cv2.imread` → always decode via
  `np.fromfile(path)` + `cv2.imdecode(data, cv2.IMREAD_COLOR)`
  or use PIL `Image.open()` / `cv2.imencode` + PIL save.
- Run Python scripts from PowerShell: write a temp `.py` file under
  `C:\Users\4pins\AppData\Local\Temp\opencode` instead of inline `-c`.
- Wrap stdout with `io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")`
  when printing Chinese to avoid console codepage garbling.

## Core Workflow

### Step 1: Extract text positions with pdfplumber

```python
import pdfplumber

def extract_text_with_positions(pdf_path):
    """Extract text and bounding boxes from PDF"""
    all_texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            words = page.extract_words(x_tolerance=3, y_tolerance=3)
            for word in words:
                all_texts.append({
                    'page': page_num,
                    'text': word['text'],
                    'x0': word['x0'],
                    'y0': word['top'],
                    'x1': word['x1'],
                    'y1': word['bottom'],
                })
    return all_texts
```

### Step 2: Find question markers

```python
import re

def find_question_starts(texts):
    """Find all question number positions (1. 2. ... 50.)"""
    questions = []
    for item in texts:
        text = item['text'].strip()
        match = re.match(r'^(\d{1,2})[.、．]$', text)
        if match:
            q_num = int(match.group(1))
            if 1 <= q_num <= 50:
                questions.append({
                    'num': q_num,
                    'page': item['page'],
                    'y0': item['y0'],
                    'y1': item['y1'],
                })
    return questions
```

### Step 3: Convert PDF to images

```python
import fitz  # PyMuPDF

def pdf_to_images(pdf_path, output_dir):
    """Convert each PDF page to PNG image (2x scale for OCR)"""
    doc = fitz.open(pdf_path)
    image_paths = {}
    for page_num in range(len(doc)):
        page = doc[doc.page_count - 1 - page_num]  # reverse order if needed
        mat = fitz.Matrix(2, 2)  # 2x upscale
        pix = page.get_pixmap(matrix=mat)
        img_path = os.path.join(output_dir, f"page_{page_num+1:03d}.png")
        pix.save(img_path)
        image_paths[page_num + 1] = img_path
    doc.close()
    return image_paths
```

### Step 4: Compute crop boundaries

```python
def compute_question_bounds(questions_on_page, page_height):
    """Calculate y-start and y-end for each question"""
    bounds = []
    questions_on_page.sort(key=lambda q: q['y0'])
    for i, q in enumerate(questions_on_page):
        y_start = q['y0'] - 10  # padding above
        if i < len(questions_on_page) - 1:
            y_end = questions_on_page[i + 1]['y0']
        else:
            y_end = page_height
        bounds.append({
            'num': q['num'],
            'page': q['page'],
            'y_start': max(0, y_start),
            'y_end': min(page_height, y_end),
        })
    return bounds
```

### Step 5: Crop and OCR

```python
import cv2
import numpy as np
from PIL import Image as PILImage

def crop_image(image_path, y_start, y_end, output_path):
    """Crop image at given y-range (PDF coords → pixels at 2x)"""
    data = np.fromfile(image_path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    y_start_px = int(y_start * 2)
    y_end_px = int(y_end * 2)
    cropped = img[y_start_px:y_end_px, :]
    cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    PILImage.fromarray(cropped_rgb).save(output_path)

def ocr_image(reader, image_path):
    """OCR a cropped image with EasyOCR"""
    data = np.fromfile(image_path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return reader.readtext(img, detail=1)
```

## Output Structure

```
提取結果/
├── pages/              # Original page images
├── q01.png ~ q50.png   # Cropped question images
├── q01.md ~ q50.md     # OCR Markdown per question
└── summary.md          # Question index table
```

## Key Gotchas

1. **Chinese paths break cv2**: Always use `np.fromfile()` + `cv2.imdecode()`
   or PIL for reading/writing images with non-ASCII paths.

2. **Question number detection**: Match `"1."` `"2."` etc. as standalone tokens.
   Filter out page numbers (`第 X 頁`), option labels (`(A)` `(B)`), and
   other numeric noise. Only accept numbers 1-50 (typical exam range).

3. **PDF coordinate system**: pdfplumber uses 72 DPI coordinates. When cropping
   the 2x-scaled image, multiply y-coordinates by 2.

4. **Duplicate question numbers**: Track seen question numbers across pages
   to avoid overwriting files from later pages.

5. **OCR accuracy**: EasyOCR works well for printed Chinese + English mixed text.
   For better accuracy on circuit diagrams, the images are essential — OCR
   alone cannot capture graphical content.

6. **Encoding**: Always wrap stdout with `io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")`
   when printing Chinese characters from Python on Windows.

## Example: Complete Script

See the working script at:
`C:\Users\4pins\AppData\Local\Temp\opencode\crop_ocr_v3.py`

Or the project output at:
`E:\01-Project\2026-08-Taipower-test\test-pdf\114-2025\電機\提取結果_v4\`
