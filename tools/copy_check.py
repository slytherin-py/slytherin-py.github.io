"""Dump all case-study copy to a text file so li-human's detect.py can score it.
Usage: python tools/copy_check.py out.txt
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import cases

out = []
for c in cases.CASES:
    out += [c["tagline"], c["card_line"], c["problem"]["text"], *c["problem"]["points"]]
    out += [f"{t}. {d}" for t, d in c["steps"]]
    out += [*c["learned"], *c["next"], c.get("metrics_note", "")]
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(x for x in out if x))
