from PIL import Image
import sys, os

src = sys.argv[1]
dst = sys.argv[2]
box = (int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]))
scale = int(sys.argv[7]) if len(sys.argv) > 7 else 3

im = Image.open(src)
crop = im.crop(box)
w, h = crop.size
crop = crop.resize((w*scale, h*scale), Image.LANCZOS)
crop.save(dst)
print("saved %s from box %s scaled x%d (%dx%d)" % (dst, box, scale, crop.size[0], crop.size[1]))