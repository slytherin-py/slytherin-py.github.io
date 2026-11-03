"""Builds certificate-provider logos into assets/logos/.

    python tools/make_cert_logos.py <folder with originals>

Originals:
  p_uol.png, p_ucl.png, p_uci.png, p_jhu.png, p_autodesk.png
      official partner logos hosted by Coursera (coursera.org/partners/...)
  ielts.svg, atlassian.svg   Wikimedia Commons, via each org's Wikidata logo (P154)
  best_paper.jpg             the Best Paper Award certificate (RIST 2021 medal is cropped from it)
"""
import os, shutil, sys
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1]
OUT = os.path.join(ROOT, "assets", "logos")
os.makedirs(OUT, exist_ok=True)


def trim_white(im, pad=4):
    rgb = Image.new("RGB", im.size, (255, 255, 255))
    rgb.paste(im, mask=im.getchannel("A") if im.mode == "RGBA" else None)
    diff = ImageChops.difference(rgb, Image.new("RGB", im.size, (255, 255, 255))).convert("L").point(lambda p: 255 if p > 24 else 0)
    x0, y0, x1, y1 = diff.getbbox()
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def white_to_alpha(im):
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            m = min(r, g, b)
            if m > 225:  # near-white fades out; pure-ish white (>=245) becomes fully transparent
                px[x, y] = (r, g, b, round(a * max(0, 245 - m) / 20))
    return im


for key in ("uol", "ucl", "uci", "jhu", "autodesk"):
    im = white_to_alpha(trim_white(Image.open(os.path.join(SRC, f"p_{key}.png")).convert("RGBA")))
    h = 120
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    im.save(os.path.join(OUT, f"provider-{key}.png"), optimize=True)
    print(f"provider-{key}.png", im.size)

ielts = open(os.path.join(SRC, "wiki", "ielts.svg"), encoding="utf-8").read()
if "viewBox" not in ielts:  # the original has only width/height, so it can't scale
    ielts = ielts.replace('width="777.79852"', 'viewBox="0 0 777.79852 292.63992" width="777.79852"', 1)
open(os.path.join(OUT, "ielts.svg"), "w", encoding="utf-8").write(ielts)
shutil.copy(os.path.join(SRC, "wiki", "atlassian.svg"), os.path.join(OUT, "atlassian.svg"))
print("ielts.svg, atlassian.svg")

# RIST 2021 medal, cropped from the top-center of the award certificate
cert = Image.open(os.path.join(SRC, "best_paper.jpg")).convert("RGB")
s = cert.width / 1000
medal = cert.crop((round(405 * s), round(18 * s), round(595 * s), round(172 * s)))
medal = white_to_alpha(trim_white(medal.convert("RGBA")))
medal = medal.resize((round(medal.width * 120 / medal.height), 120), Image.LANCZOS)
medal.save(os.path.join(OUT, "rist-2021.png"), optimize=True)
print("rist-2021.png", medal.size)

# Neutral Six Sigma mark (no issuer logo, since the issuer isn't known)
open(os.path.join(OUT, "six-sigma.svg"), "w", encoding="utf-8").write(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 48" role="img" aria-label="Six Sigma">'
    '<rect width="48" height="48" rx="12" fill="#1d1d1f"/>'
    '<text x="24" y="33" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="24" font-weight="700" fill="#fff">6σ</text>'
    '<text x="58" y="21" font-family="Helvetica,Arial,sans-serif" font-size="13" font-weight="700" fill="#1d1d1f">SIX</text>'
    '<text x="58" y="37" font-family="Helvetica,Arial,sans-serif" font-size="13" font-weight="700" fill="#1d1d1f">SIGMA</text></svg>')
print("six-sigma.svg")
