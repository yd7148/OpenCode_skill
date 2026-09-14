import sys
from PIL import Image

im = Image.open(sys.argv[1]).convert("RGB")
W, H = im.size
px = im.load()

def classify(y0, y1, x0=303, x1=790):
    red = 0; black = 0; blue = 0; total = 0
    for y in range(y0, y1):
        for x in range(x0, x1, 2):
            r,g,b = px[x,y]
            if r < 240 or g < 240 or b < 240:
                total += 1
                if r > 120 and g < 90 and b < 90 and (r-g) > 60: red += 1
                elif r < 90 and g < 90 and b < 90: black += 1
                elif abs(r-b) < 40 and abs(g-b) < 60 and g > 60 and b > 90: blue += 1
    return red, black, blue, total

# group entries y bands (from OCR of bysender3)
bands = [
    ("G1 FOOTDISC", 325,345),
    ("G2 富立金",   363,383),
    ("G3 台塑台朔", 399,422),
    ("G4 南亞臨床", 439,458),
    ("G5 ?健康網",  478,496),
    ("G6 閒置設備", 514,535),
    ("G7 台塑網旅", 554,573),
    ("G8 金典酒店", 590,611),
    ("G9 文物館",  629,649),
    ("G10 2EH汰除",666,688),
    ("G11 彰化電氣",693,712),
    ("G12 膳食菜單",716,737),
    ("G13 環氧樹脂",755,775),
]
for name,y0,y1 in bands:
    red,black,blue,total = classify(y0,y1)
    verdict = "UNREAD(red)" if red > 8 else ("READ(black)" if black > red and black > 8 else "blue/mixed")
    print("%s y%03d-%03d red=%-4d black=%-4d blue=%-4d -> %s" % (name,y0,y1,red,black,blue,verdict))