import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image, ImageDraw, ImageFont

SRC = r"D:\80-Opnecode\Projects\2026_06_playwirght\除苔蘚藥劑配方說明.md"
OUT = r"D:\80-Opnecode\Projects\2026_06_playwirght\除苔蘚藥劑配方說明.pdf"

W, H = 1240, 1754
M_L, M_R, M_T, M_B = 100, 100, 110, 110
CW = W - M_L - M_R

FONT_R = r"C:\Windows\Fonts\msjh.ttc"
FONT_B = r"C:\Windows\Fonts\msjhbd.ttc"

def font(path, size):
    return ImageFont.truetype(path, size)

F_H1 = font(FONT_B, 40)
F_H2 = font(FONT_B, 32)
F_H3 = font(FONT_B, 26)
F_BODY = font(FONT_R, 22)
F_SMALL = font(FONT_R, 19)
F_CODE = font(r"C:\Windows\Fonts\consola.ttf", 21)
F_CODE_CJK = font(FONT_R, 20)
F_TITLE = font(FONT_B, 52)

INK = (35, 38, 42)
BLUE = (16, 82, 143)
GRAY = (120, 126, 134)
CODE_BG = (240, 243, 247)
RULE = (190, 198, 206)
THEAD_BG = (222, 232, 242)
ZEBRA = (248, 250, 252)

def is_cjk(ch):
    o = ord(ch)
    return (0x2E80 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF or
            0xFF00 <= o <= 0xFFEF or 0x3000 <= o <= 0x303F)

def text_width(t, f):
    return f.getlength(t)

def wrap_text(text, f, maxw, bold_f=None):
    lines = []
    cur = ""
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        trial = cur + ch
        if text_width(trial, f) <= maxw:
            cur = trial
            i += 1
        else:
            if not cur:
                cur = ch
                i += 1
            lines.append(cur)
            cur = ""
    if cur:
        lines.append(cur)
    return lines or [""]

def parse_md(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read().splitlines()
    blocks = []
    in_code = False
    code_buf = []
    para_buf = []
    def flush_para():
        if para_buf:
            blocks.append(("para", " ".join(para_buf)))
            para_buf.clear()
    for line in raw:
        s = line.rstrip()
        if s.strip().startswith("```"):
            flush_para()
            if in_code:
                blocks.append(("code", code_buf))
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        if not s.strip():
            flush_para()
            continue
        if s.startswith("### "):
            flush_para(); blocks.append(("h3", s[4:].strip())); continue
        if s.startswith("## "):
            flush_para(); blocks.append(("h2", s[3:].strip())); continue
        if s.startswith("# "):
            flush_para(); blocks.append(("h1", s[2:].strip())); continue
        if s.strip() == "---":
            flush_para(); blocks.append(("hr", None)); continue
        m = re.match(r"^>\s?(.*)", s)
        if m:
            flush_para(); blocks.append(("quote", m.group(1))); continue
        m = re.match(r"^\d+\.\s+(.*)", s)
        if m:
            flush_para()
            if blocks and blocks[-1][0] == "olist":
                blocks[-1][1].append(m.group(1))
            else:
                blocks.append(("olist", [m.group(1)]))
            continue
        m = re.match(r"^-\s+(.*)", s)
        if m:
            flush_para(); blocks.append(("li", m.group(1))); continue
        if s.lstrip().startswith("|"):
            flush_para()
            cells = [c.strip() for c in s.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            if blocks and blocks[-1][0] == "table":
                blocks[-1][1].append(cells)
            else:
                blocks.append(("table", [cells]))
            continue
        para_buf.append(s.strip())
    flush_para()
    return blocks

class Page:
    def __init__(self):
        self.img = Image.new("RGB", (W, H), "white")
        self.d = ImageDraw.Draw(self.img)
        self.y = M_T
    def ensure(self, need):
        return self.y + need <= H - M_B
    def footer(self, num, total):
        self.d.line([(M_L, H - 70), (W - M_R, H - 70)], fill=RULE, width=2)
        self.d.text((M_L, H - 58), "除苔蘚藥劑配方說明", font=F_SMALL, fill=GRAY)
        t = f"{num} / {total}"
        self.d.text((W - M_R - text_width(t, F_SMALL), H - 58), t, font=F_SMALL, fill=GRAY)

def draw_mixed(d, x, y, text, latin_f, cjk_f, fill):
    cx = x
    buf = ""
    buf_is_cjk = None
    for ch in text:
        this_cjk = is_cjk(ch)
        if buf and this_cjk != buf_is_cjk:
            f = cjk_f if buf_is_cjk else latin_f
            d.text((cx, y), buf, font=f, fill=fill)
            cx += d.textlength(buf, font=f)
            buf = ""
        buf += ch
        buf_is_cjk = this_cjk
    if buf:
        f = cjk_f if buf_is_cjk else latin_f
        d.text((cx, y), buf, font=f, fill=fill)

def render(blocks):
    pages = []
    pg = Page()

    title = next((b[1] for b in blocks if b[0] == "h1"), "")
    body = [b for b in blocks if b[0] != "h1"]

    def newpage():
        nonlocal pg
        pages.append(pg)
        pg = Page()

    def draw_h(level, text, first=False):
        sizes = {2: (F_H2, 14, 10), 3: (F_H3, 10, 6)}
        f, before, after = sizes[level]
        h = f.size + after
        if not first and not pg.ensure(h + before):
            newpage()
        elif not first:
            pg.y += before
        if level == 2:
            pg.d.rectangle([M_L - 12, pg.y + 4, M_L - 4, pg.y + f.size], fill=BLUE)
        pg.d.text((M_L, pg.y), text, font=f, fill=BLUE)
        pg.y += f.size + after
        if level == 2:
            pg.d.line([(M_L, pg.y), (W - M_R, pg.y)], fill=RULE, width=2)
            pg.y += 8

    for bi, (typ, content) in enumerate(body):
        if typ == "h2":
            draw_h(2, content, first=(bi == 0))
        elif typ == "h3":
            draw_h(3, content)
        elif typ == "hr":
            if pg.ensure(20):
                pg.d.line([(M_L, pg.y + 8), (W - M_R, pg.y + 8)], fill=RULE, width=2)
                pg.y += 20
        elif typ == "quote":
            lines = wrap_text(content, F_BODY, CW - 30)
            bh = len(lines) * 32 + 16
            if not pg.ensure(bh):
                newpage()
            pg.d.rectangle([M_L, pg.y, M_L + 5, pg.y + bh], fill=BLUE)
            for ln in lines:
                pg.d.text((M_L + 20, pg.y + 4), ln, font=F_BODY, fill=GRAY)
                pg.y += 32
            pg.y += 12
        elif typ == "para":
            lines = wrap_text(content, F_BODY, CW)
            for ln in lines:
                if not pg.ensure(34):
                    newpage()
                pg.d.text((M_L, pg.y), ln, font=F_BODY, fill=INK)
                pg.y += 34
            pg.y += 6
        elif typ == "li":
            lines = wrap_text(content, F_BODY, CW - 34)
            for j, ln in enumerate(lines):
                if not pg.ensure(33):
                    newpage()
                if j == 0:
                    pg.d.ellipse([M_L + 6, pg.y + 11, M_L + 14, pg.y + 19], fill=BLUE)
                pg.d.text((M_L + 28, pg.y), ln, font=F_BODY, fill=INK)
                pg.y += 33
            pg.y += 4
        elif typ == "olist":
            for k, item in enumerate(content, 1):
                lines = wrap_text(item, F_BODY, CW - 44)
                for j, ln in enumerate(lines):
                    if not pg.ensure(33):
                        newpage()
                    if j == 0:
                        pg.d.text((M_L, pg.y), f"{k}.", font=F_BODY, fill=BLUE)
                    pg.d.text((M_L + 38, pg.y), ln, font=F_BODY, fill=INK)
                    pg.y += 33
            pg.y += 4
        elif typ == "code":
            lh = 30
            pad = 14
            bh = len(content) * lh + pad * 2
            if not pg.ensure(bh):
                newpage()
            pg.d.rounded_rectangle([M_L, pg.y, W - M_R, pg.y + bh], radius=10, fill=CODE_BG)
            yy = pg.y + pad
            for cl in content:
                draw_mixed(pg.d, M_L + 22, yy, cl, F_CODE, F_CODE_CJK, INK)
                yy += lh
            pg.y += bh + 12
        elif typ == "table":
            rows = content
            ncols = max(len(r) for r in rows)
            col_w = [CW / ncols] * ncols
            weights = []
            for c in range(ncols):
                mx = max(text_width(r[c] if c < len(r) else "", F_BODY) for r in rows)
                weights.append(max(mx + 24, 140))
            tot = sum(weights)
            col_w = [max(w / tot * CW, 130) for w in weights]
            scale = CW / sum(col_w)
            col_w = [w * scale for w in col_w]
            xs = [M_L]
            for wd in col_w:
                xs.append(xs[-1] + wd)
            rh = 36
            row_heights = []
            for r in rows:
                mxlines = 1
                for c in range(ncols):
                    cell = r[c] if c < len(r) else ""
                    mxlines = max(mxlines, len(wrap_text(cell, F_SMALL, col_w[c] - 20)))
                row_heights.append(mxlines * 27 + 12)
            for ri, r in enumerate(rows):
                rh_i = row_heights[ri]
                if not pg.ensure(rh_i + 4):
                    newpage()
                    if ri == 0:
                        pass
                if ri == 0:
                    pg.d.rectangle([xs[0], pg.y, xs[-1], pg.y + rh_i], fill=THEAD_BG)
                elif ri % 2 == 0:
                    pg.d.rectangle([xs[0], pg.y, xs[-1], pg.y + rh_i], fill=ZEBRA)
                for c in range(ncols):
                    cell = r[c] if c < len(r) else ""
                    lines = wrap_text(cell, F_SMALL, col_w[c] - 20)
                    yy = pg.y + 6
                    ff = FONT_B if ri == 0 else FONT_R
                    fcell = font(ff, 19)
                    for ln in lines:
                        pg.d.text((xs[c] + 10, yy), ln, font=fcell, fill=INK)
                        yy += 27
                pg.d.line([(xs[0], pg.y + rh_i), (xs[-1], pg.y + rh_i)], fill=RULE, width=1)
                pg.y += rh_i
            pg.d.line([(xs[0], pg.y - sum(row_heights)), (xs[0], pg.y)], fill=RULE, width=1)
            for x in xs:
                pg.d.line([(x, pg.y - sum(row_heights)), (x, pg.y)], fill=RULE, width=1)
            pg.y += 14

    pages.append(pg)

    total = len(pages)
    out_pages = []
    for i, p in enumerate(pages, 1):
        if i == 1:
            p.d.text((M_L, 46), title, font=F_TITLE, fill=INK)
            p.d.line([(M_L, 108), (W - M_R, 108)], fill=BLUE, width=3)
        p.footer(i, total)
        out_pages.append(p.img)
    out_pages[0].save(OUT, save_all=True, append_images=out_pages[1:], resolution=144)
    for i, p in enumerate(out_pages[:1], 1):
        p.save(os.path.join(os.path.dirname(OUT), f"_pdf_page{i}.png"))
    print(f"PDF saved: {OUT} ({total} pages)")

blocks = parse_md(SRC)
render(blocks)
