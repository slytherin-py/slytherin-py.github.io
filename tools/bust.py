"""Stamps a content hash on every local CSS/JS link (styles.css?v=1a2b3c4d), so browsers
fetch the new file as soon as it changes instead of a cached copy (GitHub Pages caches 10 min).

    python tools/bust.py        (build_cases.py runs it at the end)
"""
import glob, hashlib, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = ["styles.css", "main.js"]


def stamp(name):
    path = os.path.join(ROOT, name)
    return hashlib.md5(open(path, "rb").read()).hexdigest()[:8] if os.path.exists(path) else None


def main():
    stamps = {n: stamp(n) for n in ASSETS}
    for page in [os.path.join(ROOT, "index.html")] + glob.glob(os.path.join(ROOT, "work", "*.html")):
        s = open(page, encoding="utf-8").read()
        for name, h in stamps.items():
            if h:
                s = re.sub(r'((?:href|src)="(?:\.\./)?%s)(?:\?v=[0-9a-f]+)?"' % re.escape(name), r'\1?v=%s"' % h, s)
        open(page, "w", encoding="utf-8").write(s)
    print("stamped", ", ".join(f"{n}={h}" for n, h in stamps.items() if h))


if __name__ == "__main__":
    main()
