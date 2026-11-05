"""Draws the MS monogram (nav mark and favicon) as outlined SVG paths from Bodoni Moda
(SIL Open Font License, tools/fonts/BodoniModa-OFL.txt): a high-contrast Didone with the
letters set tight enough to touch. No font loads at runtime.
Run: python tools/make_mark.py [tighten]"""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "tools/fonts/BodoniModa-Variable.ttf"


def outline(text, wght, tighten, opsz):
    # a smaller optical size thickens the hairlines, so the mark holds up at icon sizes
    f = instantiateVariableFont(TTFont(FONT), {"wght": wght, "opsz": opsz})
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


def mark(tighten):
    d, (x0, y0, x1, y1) = outline("MS", 600, tighten, 28)
    p = (y1 - y0) * 0.04
    vb = f"{x0 - p:.0f} {y0 - p:.0f} {x1 - x0 + 2 * p:.0f} {y1 - y0 + 2 * p:.0f}"
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><path fill="#fff" d="{d}"/></svg>\n'


def favicon(tighten):
    # heavier weight so the hairlines survive at 16px; white on a near-black tile
    d, (x0, y0, x1, y1) = outline("MS", 800, tighten, 11)
    w, h = x1 - x0, y1 - y0
    s = max(w, h) * 1.2
    x, y = x0 - (s - w) / 2, y0 - (s - h) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.0f} {y:.0f} {s:.0f} {s:.0f}">'
            f'<rect x="{x:.0f}" y="{y:.0f}" width="{s:.0f}" height="{s:.0f}" rx="{s * .22:.0f}" fill="#0b0b0d"/>'
            f'<path fill="#fff" d="{d}"/></svg>\n')


if __name__ == "__main__":
    t = float(sys.argv[1]) if len(sys.argv) > 1 else 0.12
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "assets"
    (out / "mark.svg").write_text(mark(t), encoding="utf-8")
    (out / "favicon.svg").write_text(favicon(t), encoding="utf-8")
    print("wrote", out / "mark.svg", out / "favicon.svg")
