"""Builds assets/og.jpg, the 1200x630 link-preview card for LinkedIn, Slack, etc.

    python tools/make_og.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
FONTS = "C:/Windows/Fonts"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


card = Image.new("RGB", (W, H), (0, 0, 0))

# Portrait on the right, faded into black on its left edge.
p = Image.open(os.path.join(ROOT, "assets", "portrait.jpg")).convert("RGB")
ph = H + 40
p = p.resize((round(p.width * ph / p.height), ph), Image.LANCZOS)
p = p.crop((0, 10, p.width, 10 + H))
x0 = W - p.width + 60
mask = Image.new("L", p.size, 255)
md = ImageDraw.Draw(mask)
for i in range(220):
    md.line([(i, 0), (i, p.height)], fill=round(255 * i / 220))
card.paste(p, (x0, 0), mask)

d = ImageDraw.Draw(card)
d.text((72, 92), "Mohammed Saleeq Sunil", font=font("segoeuib.ttf", 30), fill=(161, 161, 166))
d.text((68, 150), "Data in.", font=font("segoeuib.ttf", 84), fill=(245, 245, 247))
d.text((68, 246), "Decisions out.", font=font("segoeuib.ttf", 84), fill=(41, 151, 255))
d.text((72, 372), "Business Analyst · Project Leader", font=font("segoeui.ttf", 32), fill=(210, 210, 215))
d.text((72, 416), "Analytics · Agile delivery · AI", font=font("segoeui.ttf", 32), fill=(210, 210, 215))
d.rounded_rectangle((72, 500, 470, 552), radius=26, fill=(0, 113, 227))
d.text((96, 508), "slytherin-py.github.io", font=font("segoeuib.ttf", 28), fill=(255, 255, 255))

card.save(os.path.join(ROOT, "assets", "og.jpg"), quality=88)
print("wrote assets/og.jpg")
