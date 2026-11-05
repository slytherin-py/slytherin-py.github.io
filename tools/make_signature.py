"""Draws the signature logo and the MS favicon as outlined SVG paths from Great Vibes
(SIL Open Font License, tools/fonts/GreatVibes-OFL.txt), so no font loads at runtime.
Run: python tools/make_signature.py"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "tools/fonts/GreatVibes-Regular.ttf"


def outline(text, tighten=0.0):
    f = TTFont(FONT)
    gs, cmap, hmtx, upm = f.getGlyphSet(), f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    x, d, bp = 0, [], BoundsPen(gs)
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
        gs[g].draw(TransformPen(bp, (1, 0, 0, -1, x, 0)))
        d.append(pen.getCommands())
        x += hmtx[g][0] - upm * tighten
    return " ".join(d), bp.bounds


def signature():
    d, (x0, y0, x1, y1) = outline("Mohammed Saleeq Sunil")
    p = (y1 - y0) * 0.05
    vb = f"{x0 - p:.0f} {y0 - p:.0f} {x1 - x0 + 2 * p:.0f} {y1 - y0 + 2 * p:.0f}"
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><path fill="#fff" d="{d}"/></svg>\n'


def favicon():
    # white MS on a near-black tile; a hairline stroke thickens the script so it survives 16px
    d, (x0, y0, x1, y1) = outline("MS", 0.12)
    w, h = x1 - x0, y1 - y0
    s = max(w, h) * 1.14
    x, y = x0 - (s - w) / 2, y0 - (s - h) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.0f} {y:.0f} {s:.0f} {s:.0f}">'
            f'<rect x="{x:.0f}" y="{y:.0f}" width="{s:.0f}" height="{s:.0f}" rx="{s * .24:.0f}" fill="#0b0b0d"/>'
            f'<path fill="#fff" stroke="#fff" stroke-width="{s * .018:.0f}" stroke-linejoin="round" d="{d}"/></svg>\n')


if __name__ == "__main__":
    (ROOT / "assets/signature.svg").write_text(signature(), encoding="utf-8")
    (ROOT / "assets/favicon.svg").write_text(favicon(), encoding="utf-8")
    print("wrote assets/signature.svg, assets/favicon.svg")
