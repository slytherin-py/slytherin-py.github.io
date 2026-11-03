"""Builds assets/logos/* from the official logo files saved in a source folder.

    python tools/make_logos.py <folder with the downloaded originals>

Originals (each from the organization's own website):
  isenberg.png      isenberg.umass.edu  (logo-umass-isom-horizontal-white.png)
  fingent.png       fingent.com         (Fingent-Logo-Header-02.png)
  centresource.png  centresource.in     (Centre-Source-Logo.png)
  jecc.png          jecc.ac.in          (jyothilog.png)
  scrum.svg         scrumalliance.org   (navmobile/logo.svg)
  aip.svg           publishing.aip.org  (AIPP-Master-Logo-white-01.svg)
"""
import os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1]
OUT = os.path.join(ROOT, "assets", "logos")
os.makedirs(OUT, exist_ok=True)


def trim(im):
    box = im.getchannel("A").getbbox()
    return im.crop(box) if box else im


def fit(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def recolor(im, rgb):
    a = im.getchannel("A")
    solid = Image.new("RGBA", im.size, rgb + (255,))
    solid.putalpha(a)
    return solid


def save(im, name):
    im.save(os.path.join(OUT, name), optimize=True)
    print(name, im.size)


# Isenberg: white original, plus a maroon version for light backgrounds
isb = trim(Image.open(os.path.join(SRC, "isenberg.png")).convert("RGBA"))
save(fit(isb, 120), "isenberg-white.png")
save(fit(recolor(isb, (136, 28, 28)), 120), "isenberg.png")

# Fingent: keep the red brand tile for cards; lift the white mark out for the dark strip
fg = Image.open(os.path.join(SRC, "fingent.png")).convert("RGBA")
# Only a 212px original exists, so keep native size (sharp at the ~30px it is shown).
save(fg, "fingent.png")
px = fg.load()
mark = Image.new("RGBA", fg.size, (0, 0, 0, 0))
mp = mark.load()
for y in range(fg.height):
    for x in range(fg.width):
        r, g, b, a = px[x, y]
        # the red background has a low min channel; white strokes are near 255, so min() is a soft mask
        alpha = max(0, min(255, round((min(r, g, b) - 45) * 255 / 200)))
        if a and alpha:
            mp[x, y] = (255, 255, 255, alpha)
save(trim(mark), "fingent-white.png")

# Centre Source: color original, plus all-white version
cs = trim(Image.open(os.path.join(SRC, "centresource.png")).convert("RGBA"))
save(fit(cs, 120), "centresource.png")
save(fit(recolor(cs, (255, 255, 255)), 120), "centresource-white.png")

# Holiday World (myholidayworld.com, holiday_world_logo.webp): "WORLD" is white, so make an ink version for light cards
hc = trim(Image.open(os.path.join(SRC, "mhw_holiday_world_logo.webp")).convert("RGBA"))
save(fit(hc, 120), "holiday-world-white.png")
dark = hc.copy()
px = dark.load()
for y in range(dark.height):
    for x in range(dark.width):
        r, g, b, a = px[x, y]
        if a and min(r, g, b) > 200:  # white letterforms -> ink; teal accents untouched
            px[x, y] = (29, 29, 31, a)
save(fit(dark, 120), "holiday-world.png")

# Jyothi Engineering College seal
save(fit(trim(Image.open(os.path.join(SRC, "jecc.png")).convert("RGBA")), 160), "jecc.png")

# Scrum Alliance: drop the white background rect; color + white versions
svg = open(os.path.join(SRC, "scrum.svg"), encoding="utf-8").read()
svg = re.sub(r'<rect width="204" height="80" fill="white"/>', "", svg)
# tighten to the drawn mark (measured with getBBox) so it isn't tiny inside its padding
svg = svg.replace('width="204" height="80" viewBox="0 0 204 80"', 'viewBox="7 24.5 190.5 31"')
open(os.path.join(OUT, "scrum-alliance.svg"), "w", encoding="utf-8").write(svg)
white = re.sub(r'fill="#[0-9A-Fa-f]{3,6}"', 'fill="#FFFFFF"', svg)
open(os.path.join(OUT, "scrum-alliance-white.svg"), "w", encoding="utf-8").write(white)
print("scrum-alliance.svg, scrum-alliance-white.svg")

# AIP Publishing: white original, plus a dark version
aip = open(os.path.join(SRC, "aip.svg"), encoding="utf-8").read()
open(os.path.join(OUT, "aip-white.svg"), "w", encoding="utf-8").write(aip)
open(os.path.join(OUT, "aip.svg"), "w", encoding="utf-8").write(aip.replace(".cls-1{fill:#fff;}", ".cls-1{fill:#1d1d1f;}"))
print("aip.svg, aip-white.svg")
