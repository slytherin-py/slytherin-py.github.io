"""Builds assets/og.jpg, the 1200x630 link-preview card for LinkedIn, Slack, etc.

    python tools/make_og.py

Matches the site: true-black ground, the portrait fading in from the right, the Bodoni MS mark,
Instrument Sans for type and the accent phrase in Instrument Serif italic blue, plus three
proof figures from the resume. Fonts live in tools/fonts (all SIL OFL).
LinkedIn shows this small, so every line is set large enough to read at ~400px wide.
"""
import os
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "tools", "fonts")
W, H = 1200, 630
BLACK, WHITE, SOFT, MUTED = (0, 0, 0), (245, 245, 247), (210, 210, 215), (134, 134, 139)
BLUE, PILL, TILE, LINE = (41, 151, 255), (0, 113, 227), (18, 18, 22), (44, 44, 50)
PAD = 64


def sans(size, wght=600):
    f = ImageFont.truetype(os.path.join(FONTS, "InstrumentSans-Variable.ttf"), size)
    f.set_variation_by_axes([100, wght])
    return f


def bodoni(size):
    f = ImageFont.truetype(os.path.join(FONTS, "BodoniModa-Variable.ttf"), size)
    f.set_variation_by_axes([600, 28])
    return f


card = Image.new("RGB", (W, H), BLACK)

# Portrait on the right, faded into the black on its left edge (its backdrop is already true black).
p = Image.open(os.path.join(ROOT, "assets", "portrait.jpg")).convert("RGB")
ph = H + 60
p = p.resize((round(p.width * ph / p.height), ph), Image.LANCZOS)
p = p.crop((0, 20, p.width, 20 + H))
x0 = W - p.width + 40
mask = Image.new("L", p.size, 255)
md = ImageDraw.Draw(mask)
for i in range(260):
    md.line([(i, 0), (i, p.height)], fill=round(255 * (i / 260) ** 1.6))
card.paste(ImageChops.lighter(card.crop((x0, 0, x0 + p.width, H)), p), (x0, 0), mask)

d = ImageDraw.Draw(card)

# MS mark, set tight so the letters touch, then the name beside it
mf = bodoni(46)
d.text((PAD, 52), "M", font=mf, fill=WHITE)
d.text((PAD + d.textlength("M", font=mf) - 7, 52), "S", font=mf, fill=WHITE)
d.line([(PAD + 88, 60), (PAD + 88, 96)], fill=LINE, width=2)
d.text((PAD + 106, 58), "Mohammed Saleeq Sunil", font=sans(30, 600), fill=WHITE)

# Headline
d.text((PAD - 4, 128), "Data in.", font=sans(96, 700), fill=WHITE)
d.text((PAD - 2, 222), "Decisions out.", font=ImageFont.truetype(os.path.join(FONTS, "InstrumentSerif-Italic.ttf"), 112), fill=BLUE)
d.text((PAD, 360), "Product & Project Leader · Business & Data Analytics", font=sans(27, 500), fill=SOFT)

# Three proof figures, each in a quiet tile
proof = [("22%", "faster delivery"), ("40%", "fewer AI errors"), ("3.97/4", "GPA · CSM · CSPO")]
tx, ty, tw, th, gap = PAD, 420, 196, 98, 14
for i, (num, label) in enumerate(proof):
    x = tx + i * (tw + gap)
    d.rounded_rectangle((x, ty, x + tw, ty + th), radius=18, fill=TILE, outline=LINE, width=1)
    d.text((x + 18, ty + 14), num, font=sans(40, 700), fill=BLUE if i < 2 else WHITE)
    d.text((x + 18, ty + 64), label, font=sans(17, 500), fill=MUTED)

# Call to action: the whole preview is the link, so the pill names what a click does
cta = sans(26, 600)
label = "View portfolio"
lw = d.textlength(label, font=cta)
x1 = PAD + 26 + lw + 18 + 22 + 24
d.rounded_rectangle((PAD, 542, x1, 594), radius=26, fill=PILL)
d.text((PAD + 26, 551), label, font=cta, fill=(255, 255, 255))
ax, ay = PAD + 26 + lw + 18, 568
d.line([(ax, ay), (ax + 22, ay)], fill=(255, 255, 255), width=3)
d.line([(ax + 13, ay - 9), (ax + 22, ay), (ax + 13, ay + 9)], fill=(255, 255, 255), width=3, joint="curve")
d.text((x1 + 20, 556), "slytherin-py.github.io", font=sans(20, 500), fill=MUTED)

card.save(os.path.join(ROOT, "assets", "og.jpg"), quality=90, optimize=True)
print("wrote assets/og.jpg")
