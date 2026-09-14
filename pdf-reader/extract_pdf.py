# -*- coding: utf-8 -*-
"""
extract_pdf.py — PDF 內容提取工具
- 文字型 PDF：PyMuPDF 直接抽取文本（支援中文）
- 掃描/圖片型 PDF：頁面渲染為 PNG → RapidOCR 辨識
- 繁簡轉換：OCR/文本輸出統一轉為繁體中文（opencc s2twp）
用法: python extract_pdf.py <input.pdf> [output.md] [--pages 1,3-5] [--no-ocr] [--dpi 200]
"""
import sys, os, argparse, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def log(msg):
    print(msg)

def main():
    ap = argparse.ArgumentParser(description="Extract text (and OCR) from a PDF into markdown.")
    ap.add_argument("pdf", help="input PDF path")
    ap.add_argument("out", nargs="?", default=None, help="output .md path (default: <pdf name>.md)")
    ap.add_argument("--pages", default=None, help="e.g. 1,3-5 (1-based, inclusive)")
    ap.add_argument("--no-ocr", action="store_true", help="skip OCR for empty pages")
    ap.add_argument("--dpi", type=int, default=200, help="OCR render DPI")
    args = ap.parse_args()

    src = os.path.abspath(args.pdf)
    if not os.path.isfile(src):
        log(f"[ERROR] PDF not found: {src}")
        sys.exit(1)
    dest = args.out or os.path.splitext(src)[0] + ".md"
    if not dest.lower().endswith(".md"):
        dest += ".md"
    dest = os.path.abspath(dest)

    # parse page selection
    wanted = set()
    pages_spec = args.pages
    if pages_spec:
        for chunk in pages_spec.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if "-" in chunk:
                a, b = chunk.split("-", 1)
                wanted.update(range(int(a), int(b) + 1))
            else:
                wanted.add(int(chunk))

    try:
        import pymupdf as fitz  # PyMuPDF >= 1.28
    except ImportError:
        try:
            import fitz
        except ImportError:
            log("[ERROR] PyMuPDF not installed. Run: pip install PyMuPDF")
            sys.exit(1)

    ocr = None
    if not args.no_ocr:
        try:
            from rapidocr_onnxruntime import RapidOCR
            ocr = RapidOCR()
        except Exception as e:
            log(f"[WARN] RapidOCR unavailable, empty pages will stay empty: {e}")

    cc = None
    try:
        from opencc import OpenCC
        cc = OpenCC("s2twp")
    except Exception:
        log("[INFO] opencc not available; keeping original script orientation.")

    t0 = time.time()
    doc = fitz.open(src)
    total = doc.page_count
    log(f"[INFO] {os.path.basename(src)}: {total} pages")

    def conv(txt):
        return cc.convert(txt) if cc else txt

    sections = []
    ocr_pages = []
    text_pages = []
    empty_pages = []
    for idx in range(total):
        num = idx + 1
        if wanted and num not in wanted:
            continue
        page = doc.load_page(idx)
        raw = page.get_text("text").strip()
        if len(raw.strip()) >= 40:
            sections.append(f"## 第 {num} 頁\n\n{raw.strip()}\n")
            text_pages.append(num)
        else:
            empty_pages.append(num)
            if ocr is None:
                sections.append(f"## 第 {num} 頁\n\n*([無文字層，OCR 未啟用]*)*\n")
                continue
            pix = page.get_pixmap(dpi=args.dpi)
            tmp = os.path.join(os.path.dirname(dest), f"_pdf_ocr_{os.path.splitext(os.path.basename(dest))[0]}_p{num}.png")
            pix.save(tmp)
            try:
                res, _ = ocr(tmp)
                lines = []
                if res:
                    for box, txt, score in res:
                        if score is None or float(score) >= 0.5:
                            lines.append(str(txt))
                body = conv("\n".join(lines))
                sections.append(f"## 第 {num} 頁 {chr(0x300A)}掃描頁 OCR{chr(0x300B)}\n\n{body}\n")
                ocr_pages.append(num)
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)
    doc.close()

    # summary
    meta = (f"# PDF 內容摘要\n\n"
            f"- **來源檔案**: `{os.path.basename(src)}`\n"
            f"- **總頁數**: {total}\n"
            f"- **處理頁數**: {len(text_pages) + len(ocr_pages)}\n"
            f"- **文字層頁面**: {len(text_pages)} | **OCR 頁面**: {len(ocr_pages)}\n"
            f"- **產生時間**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"---\n\n")
    full = meta + "\n".join(sections)

    with open(dest, "w", encoding="utf-8") as f:
        f.write(full)
    elapsed = time.time() - t0
    log(f"[OK] saved: {dest}  (pages with text={len(text_pages)}, OCR={len(ocr_pages)}, time={elapsed:.1f}s)")

    if ocr_pages:
        log(f"[INFO] OCR was used on pages: {ocr_pages}")

if __name__ == "__main__":
    main()