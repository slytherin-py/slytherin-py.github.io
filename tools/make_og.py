"""Builds assets/og.jpg, the 1200x630 link-preview card for LinkedIn, Slack, etc.

    python tools/make_og.py

Navy ground, cream type, the accent phrase in Instrument Serif italic (tools/fonts, OFL).
"""
import os
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
FONTS = "C:/Windows/Fonts"
NAVY, CREAM, MUTED = (15, 26, 53), (246, 239, 227), (167, 174, 196)
ORANGE, PILL = (255, 147, 84), (194, 65, 12)


def font(name, size):
    path = os.path.join(ROOT, "tools", "fonts", name) if name.startswith("Instrument") else os.path.join(FONTS, name)
    return ImageFont.truetype(path, size)


card = Image.new("RGB", (W, H), NAVY)

# Portrait on the right. Its black studio ground is lightened into the navy (as on the site),
# and its left edge fades out.
p = Image.open(os.path.join(ROOT, "assets", "portrait.jpg")).convert("RGB")
ph = H + 40
p = p.resize((round(p.width * ph / p.height), ph), Image.LANCZOS)
p = p.crop((0, 10, p.width, 10 + H))
x0 = W - p.width + 60
region = card.crop((x0, 0, x0 + p.width, H))
blended = ImageChops.lighter(region, p)
mask = Image.new("L", p.size, 255)
md = ImageDraw.Draw(mask)
for i in range(220):
    md.line([(i, 0), (i, p.height)], fill=round(255 * i / 220))
card.paste(blended, (x0, 0), mask)

d = ImageDraw.Draw(card)
d.text((72, 92), "Mohammed Saleeq Sunil", font=font("segoeuib.ttf", 30), fill=MUTED)
d.text((68, 150), "Data in.", font=font("segoeuib.ttf", 84), fill=CREAM)
d.text((70, 232), "Decisions out.", font=font("InstrumentSerif-Italic.ttf", 104), fill=ORANGE)
d.text((72, 372), "BA Lead · Analytics & Operations", font=font("segoeui.ttf", 32), fill=(216, 219, 230))
d.text((72, 416), "MS Business Analytics · Isenberg", font=font("segoeui.ttf", 32), fill=(216, 219, 230))
d.rounded_rectangle((72, 500, 470, 552), radius=26, fill=PILL)
d.text((96, 508), "slytherin-py.github.io", font=font("segoeuib.ttf", 28), fill=(255, 255, 255))

card.save(os.path.join(ROOT, "assets", "og.jpg"), quality=88)
print("wrote assets/og.jpg")
