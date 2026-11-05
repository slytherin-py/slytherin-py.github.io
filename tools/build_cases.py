"""Builds work/<slug>.html case-study pages and the homepage work grid from tools/cases.py.

    python tools/build_cases.py
"""
import html, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cases import CASES  # noqa: E402

e = html.escape
SITE = "https://slytherin-py.github.io/"

# ---------------------------------------------------------------- graphics
HUB_SVG = """<svg class="hub-map" viewBox="0 0 640 420" role="img" aria-labelledby="hub-t">
  <title id="hub-t">Schematic: seven hubs with 15-minute coverage areas over a population map</title>
  <defs>
    <radialGradient id="hubFill"><stop offset="0" stop-color="#2997ff" stop-opacity=".32"/><stop offset="1" stop-color="#2997ff" stop-opacity=".05"/></radialGradient>
    <clipPath id="region"><path d="M70 92 C130 30 260 40 340 52 C430 64 520 40 584 104 C626 148 600 222 612 284 C622 350 552 392 470 380 C390 368 320 398 236 384 C150 372 66 360 48 286 C34 226 22 142 70 92Z"/></clipPath>
  </defs>
  <path d="M70 92 C130 30 260 40 340 52 C430 64 520 40 584 104 C626 148 600 222 612 284 C622 350 552 392 470 380 C390 368 320 398 236 384 C150 372 66 360 48 286 C34 226 22 142 70 92Z" fill="#121215" stroke="#2c2c30" stroke-width="1.5"/>
  <g class="pop" clip-path="url(#region)"></g><g class="hubs"></g>
  <g font-size="11" fill="#86868b" font-family="-apple-system, Inter, sans-serif">
    <circle cx="28" cy="404" r="3" fill="#6e6e73"/><text x="38" y="408">Population</text>
    <circle cx="118" cy="404" r="5" fill="#fff" stroke="#2997ff" stroke-width="2"/><text x="130" y="408">Hub</text>
    <circle cx="176" cy="404" r="7" fill="url(#hubFill)" stroke="#2997ff" stroke-opacity=".6"/><text x="190" y="408">15-min coverage</text>
  </g>
</svg>"""

TRIALS_SVG = """<svg class="viz" viewBox="0 0 640 400" role="img" aria-labelledby="tr-t">
  <title id="tr-t">143,266 registry rows narrowed to 3,446 Phase III oncology trials; industry trials enroll 1.83 times the academic median</title>
  <rect width="640" height="400" rx="20" fill="#0b0b0d"/>
  <g font-family="-apple-system, Inter, sans-serif">
    <text x="40" y="58" fill="#86868b" font-size="14">ClinicalTrials.gov export</text>
    <text x="600" y="58" fill="#f5f5f7" font-size="14" font-weight="600" text-anchor="end">143,266 rows</text>
    <rect x="40" y="70" width="560" height="14" rx="7" fill="#3a3a3e"/>
    <text x="40" y="118" fill="#86868b" font-size="14">Phase III oncology</text>
    <text x="600" y="118" fill="#f5f5f7" font-size="14" font-weight="600" text-anchor="end">3,446 trials</text>
    <rect x="40" y="130" width="560" height="14" rx="7" fill="#1f1f22"/><rect x="40" y="130" width="14" height="14" rx="7" fill="#f5f5f7"/>
    <text x="40" y="196" fill="#f5f5f7" font-size="15" font-weight="600">Median enrollment, indexed to academic = 1.00</text>
    <text x="40" y="240" fill="#86868b" font-size="14">Academic</text>
    <rect x="140" y="226" width="250" height="22" rx="11" fill="#6e6e73"/><text x="400" y="243" fill="#f5f5f7" font-size="15" font-weight="600">1.00x</text>
    <text x="40" y="286" fill="#86868b" font-size="14">Industry</text>
    <defs><linearGradient id="trg" x1="0" x2="1"><stop offset="0" stop-color="#2997ff"/><stop offset="1" stop-color="#a88bff"/></linearGradient></defs>
    <rect x="140" y="272" width="458" height="22" rx="11" fill="url(#trg)"/>
    <text x="598" y="350" fill="#f5f5f7" font-size="56" font-weight="700" text-anchor="end" letter-spacing="-2">1.83x</text>
  </g>
</svg>"""

IMPACT_ROWS = [("Manual reporting effort", -40), ("Errors, AI content pipeline", -40), ("Reporting discrepancies", -30), ("Scope creep", -25), ("Delivery velocity", 22), ("Efficiency", 15)]


def impact_svg():
    rows = []
    for i, (label, v) in enumerate(IMPACT_ROWS):
        y = 70 + i * 52
        w = abs(v) / 50 * 360
        col = "url(#imp-dn)" if v < 0 else "url(#imp-up)"
        rows.append(f'<text x="40" y="{y}" fill="#a1a1a6" font-size="14">{label}</text>'
                    f'<rect x="40" y="{y + 9}" width="360" height="12" rx="6" fill="#1f1f22"/>'
                    f'<rect x="40" y="{y + 9}" width="{w:.0f}" height="12" rx="6" fill="{col}"/>'
                    f'<text x="600" y="{y + 20}" fill="#f5f5f7" font-size="26" font-weight="700" text-anchor="end" letter-spacing="-1">{"+" if v > 0 else "−"}{abs(v)}%</text>')
    return f"""<svg class="viz" viewBox="0 0 640 400" role="img" aria-labelledby="imp-t">
  <title id="imp-t">Impact at Fingent: 40% less manual reporting, 40% fewer pipeline errors, 30% fewer discrepancies, 25% less scope creep, 22% faster delivery, 15% more efficient</title>
  <defs><linearGradient id="imp-up" x1="0" x2="1"><stop offset="0" stop-color="#2997ff"/><stop offset="1" stop-color="#a88bff"/></linearGradient>
  <linearGradient id="imp-dn" x1="0" x2="1"><stop offset="0" stop-color="#a88bff"/><stop offset="1" stop-color="#ff8a5c"/></linearGradient></defs>
  <rect width="640" height="400" rx="20" fill="#0b0b0d"/>
  <g font-family="-apple-system, Inter, sans-serif">{''.join(rows)}</g>
  <text x="40" y="384" fill="#6e6e73" font-size="11" font-family="-apple-system, Inter, sans-serif">Bar length on a 0 to 50% scale</text>
</svg>"""


FLOOD_SVG = """<svg class="viz" viewBox="0 0 640 400" role="img" aria-labelledby="fl-t">
  <title id="fl-t">The problem: floodwater rises above an ambulance's exhaust outlet, back-pressure pushes water toward the engine and it stalls</title>
  <defs>
    <linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2997ff" stop-opacity=".55"/><stop offset="1" stop-color="#0b3a6b" stop-opacity=".9"/></linearGradient>
    <marker id="fa" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#ff8a5c"/></marker>
  </defs>
  <rect width="640" height="400" rx="20" fill="#0b0b0d"/>
  <g font-family="-apple-system, Inter, sans-serif">
    <rect x="150" y="120" width="330" height="150" rx="16" fill="#f5f5f7"/>
    <path d="M480 160 h70 a20 20 0 0 1 20 20 v90 h-90z" fill="#e8e8ed"/>
    <rect x="500" y="172" width="50" height="40" rx="6" fill="#86868b"/>
    <rect x="290" y="160" width="16" height="56" rx="3" fill="#ff3b30"/><rect x="270" y="180" width="56" height="16" rx="3" fill="#ff3b30"/>
    <rect x="150" y="146" width="330" height="8" fill="#ff3b30" opacity=".85"/>
    <circle cx="220" cy="282" r="30" fill="#1d1d1f" stroke="#48484a" stroke-width="6"/>
    <circle cx="500" cy="282" r="30" fill="#1d1d1f" stroke="#48484a" stroke-width="6"/>
    <rect x="96" y="250" width="62" height="12" rx="6" fill="#86868b"/>
    <path d="M0 236 C40 226 80 246 120 236 S200 226 240 236 S320 246 360 236 S440 226 480 236 S560 246 640 236 V380 a20 20 0 0 1 -20 20 H20 a20 20 0 0 1 -20 -20Z" fill="url(#water)"/>
    <path d="M70 256 H150" stroke="#ff8a5c" stroke-width="2.5" marker-end="url(#fa)"/>
    <path d="M170 256 C250 256 300 230 360 214" stroke="#ff8a5c" stroke-width="2.5" stroke-dasharray="6 5" fill="none" marker-end="url(#fa)"/>
    <text x="20" y="226" fill="#9cc9ff" font-size="13" font-weight="600">Water level</text>
    <text x="40" y="300" fill="#f5f5f7" font-size="13" font-weight="600">Exhaust outlet</text>
    <text x="40" y="318" fill="#d2d2d7" font-size="12">underwater</text>
    <text x="372" y="102" fill="#ff8a5c" font-size="13" font-weight="600">Back-pressure</text>
    <text x="372" y="118" fill="#ffb899" font-size="12">pushes water toward the engine</text><path d="M392 124 V200" stroke="#ff8a5c" stroke-width="1.2" stroke-dasharray="3 3"/>
    <text x="320" y="60" fill="#f5f5f7" font-size="22" font-weight="700" text-anchor="middle" letter-spacing="-.5">Why vehicles stall in floods</text>
    <text x="320" y="84" fill="#86868b" font-size="13" text-anchor="middle">Problem illustration. The paper covers the modified design.</text>
  </g>
</svg>"""

CONFUSION = """<div class="cm-wrap"><svg class="viz" viewBox="0 0 400 330" role="img" aria-labelledby="cm-t">
  <title id="cm-t">Confusion matrix on 1,271 held-out videos: 425 true negatives, 61 false positives, 85 false negatives, 700 true positives</title>
  <g font-family="-apple-system, Inter, sans-serif" text-anchor="middle">
    <text x="250" y="20" font-size="12" fill="#86868b">Predicted</text>
    <text x="180" y="44" font-size="12" fill="#a1a1a6">Not viral</text><text x="320" y="44" font-size="12" fill="#a1a1a6">Viral</text>
    <text x="20" y="175" font-size="12" fill="#86868b" transform="rotate(-90 20 175)">Actual</text>
    <text x="96" y="122" font-size="12" fill="#a1a1a6" text-anchor="end">Not viral</text><text x="96" y="246" font-size="12" fill="#a1a1a6" text-anchor="end">Viral</text>
    <rect x="112" y="56" width="136" height="120" rx="14" fill="#2997ff" fill-opacity=".55"/><rect x="252" y="56" width="136" height="120" rx="14" fill="#2997ff" fill-opacity=".1"/>
    <rect x="112" y="180" width="136" height="120" rx="14" fill="#2997ff" fill-opacity=".13"/><rect x="252" y="180" width="136" height="120" rx="14" fill="#2997ff" fill-opacity=".85"/>
    <g font-size="34" font-weight="700" fill="#f5f5f7"><text x="180" y="126">425</text><text x="320" y="126">61</text><text x="180" y="250">85</text><text x="320" y="250">700</text></g>
    <g font-size="11" fill="#d2d2d7"><text x="180" y="148">true negative</text><text x="320" y="148">false positive</text><text x="180" y="272">false negative</text><text x="320" y="272">true positive</text></g>
  </g></svg></div>"""

FLOWS = """<div class="flow-pair">
<figure class="flow-card dark-card"><svg class="viz" viewBox="0 0 420 220" role="img" aria-labelledby="ab-t">
  <title id="ab-t">Experimentation loop: hypothesis, test, measure, prioritize</title>
  <defs><marker id="arw" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#48484a"/></marker></defs>
  <ellipse cx="210" cy="110" rx="150" ry="78" fill="none" stroke="#2c2c30" stroke-width="1.5"/>
  <g fill="none" stroke="#48484a" stroke-width="1.5" marker-end="url(#arw)"><path d="M150 36 Q200 26 262 34"/><path d="M340 62 Q362 100 340 156"/><path d="M268 186 Q210 196 150 186"/><path d="M80 158 Q58 110 80 62"/></g>
  <g font-family="-apple-system, Inter, sans-serif" font-size="13" font-weight="600" text-anchor="middle">
    <rect x="40" y="22" width="110" height="36" rx="18" fill="#1f1f22" stroke="#333336"/><text x="95" y="45" fill="#f5f5f7">Hypothesis</text>
    <rect x="268" y="22" width="110" height="36" rx="18" fill="#1f1f22" stroke="#333336"/><text x="323" y="45" fill="#f5f5f7">Test</text>
    <rect x="268" y="162" width="110" height="36" rx="18" fill="#1f1f22" stroke="#333336"/><text x="323" y="185" fill="#f5f5f7">Measure</text>
    <rect x="40" y="162" width="110" height="36" rx="18" fill="#2997ff"/><text x="95" y="185" fill="#fff">Prioritize</text>
  </g></svg><figcaption><b>+22% delivery velocity.</b> Backlog calls made on test results, not urgency.</figcaption></figure>
<figure class="flow-card"><svg class="viz" viewBox="0 0 440 170" role="img" aria-labelledby="gv-t">
  <title id="gv-t">Change governance: change, assess, approve, release, monitor, with an escalation path back to assessment</title>
  <defs><marker id="arw2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#86868b"/></marker></defs>
  <g fill="none" stroke="#86868b" stroke-width="1.5" marker-end="url(#arw2)"><path d="M78 96 H96"/><path d="M164 96 H182"/><path d="M250 96 H268"/><path d="M336 96 H354"/></g>
  <path d="M390 76 C390 20 130 20 130 74" fill="none" stroke="#ff8a5c" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#arw2)"/>
  <text x="260" y="26" text-anchor="middle" font-family="-apple-system, Inter, sans-serif" font-size="11.5" fill="#ff8a5c" font-weight="600">Escalation path</text>
  <g font-family="-apple-system, Inter, sans-serif" font-size="12.5" font-weight="600" text-anchor="middle">
    <rect x="10" y="78" width="68" height="36" rx="10" fill="#f5f5f7" stroke="#d2d2d7"/><text x="44" y="100" fill="#1d1d1f">Change</text>
    <rect x="96" y="78" width="68" height="36" rx="10" fill="#f5f5f7" stroke="#d2d2d7"/><text x="130" y="100" fill="#1d1d1f">Assess</text>
    <rect x="182" y="78" width="68" height="36" rx="10" fill="#f5f5f7" stroke="#d2d2d7"/><text x="216" y="100" fill="#1d1d1f">Approve</text>
    <rect x="268" y="78" width="68" height="36" rx="10" fill="#f5f5f7" stroke="#d2d2d7"/><text x="302" y="100" fill="#1d1d1f">Release</text>
    <rect x="354" y="78" width="72" height="36" rx="10" fill="#1d1d1f"/><text x="390" y="100" fill="#fff">Monitor</text>
  </g></svg><figcaption><b>−40% errors.</b> Clear escalation on a Fortune-class client's AI content pipeline.</figcaption></figure>
</div>"""

SVGS = {"hub": HUB_SVG, "trials": TRIALS_SVG, "impact": impact_svg(), "flood": FLOOD_SVG}


def picture(name, alt, prefix, cls="", zoom=True, lazy=True):
    z = f' data-zoom="{prefix}assets/work/{name}.webp"' if zoom else ""
    ld = ' loading="lazy" decoding="async"' if lazy else ""
    return (f'<picture><source srcset="{prefix}assets/work/{name}.webp" type="image/webp">'
            f'<img class="{cls}" src="{prefix}assets/work/{name}-sm.jpg" alt="{e(alt)}"{ld}{z}></picture>')


def browser(inner, url):
    return (f'<div class="browser"><div class="browser-bar"><i></i><i></i><i></i>'
            f'<span>{e(url)}</span></div>{inner}</div>')


# ---------------------------------------------------------------- shared chrome
def nav(prefix):
    links = "".join(f'<a href="{prefix}index.html#{a}">{b}</a>' for a, b in
                    [("about", "About"), ("experience", "Experience"), ("work", "Work"), ("recognition", "Recognition"), ("skills", "Skills"), ("contact", "Contact")])
    return f"""<header class="nav" id="nav">
  <div class="wrap-wide nav-inner">
    <a class="brand" href="{prefix}index.html" aria-label="Mohammed Saleeq Sunil, home"><span class="brand-mark" aria-hidden="true">MS</span><span>Mohammed Saleeq Sunil</span></a>
    <nav aria-label="Primary"><div class="nav-links" id="nav-links">{links}</div></nav>
    <div class="nav-actions">
      <a class="btn btn-primary btn-sm" href="{prefix}index.html#contact">Hire me</a>
      <button class="menu-btn" id="menu-btn" aria-controls="nav-links" aria-expanded="false" aria-label="Open menu"><span></span><span></span></button>
    </div>
  </div>
</header>"""


def footer(prefix):
    return f"""<footer class="footer"><div class="wrap-wide footer-inner">
  <p>© <span id="year">2026</span> Mohammed Saleeq Sunil</p>
  <nav aria-label="Footer"><a href="mailto:mohammedsaleeqs@gmail.com">Email</a><a href="https://www.linkedin.com/in/mohammed-saleeq-sunil" target="_blank" rel="noopener">LinkedIn</a><a href="https://github.com/slytherin-py" target="_blank" rel="noopener">GitHub</a><a href="{prefix}assets/Mohammed_Saleeq_Sunil_Resume.pdf" download>Resume</a></nav>
</div></footer>"""


# ---------------------------------------------------------------- case page
def case_page(c, nxt):
    P = "../"
    hero = c["hero"]
    if "img" in hero:
        media = browser(picture(hero["img"], hero["alt"], P, lazy=False), hero["frame"])
    else:
        media = f'<div class="viz-frame">{SVGS[hero["svg"]]}</div>'

    links = "".join(
        f'<a class="{"btn btn-primary" if primary else "more"}" href="{u}" target="_blank" rel="noopener">{e(t)}</a>'
        for t, u, primary in c["links"])

    facts = "".join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in c["facts"])
    metrics = "".join(f'<div class="m reveal" style="--d:{i * .06:.2f}s"><b>{e(v)}</b><span>{e(l)}</span></div>' for i, (v, l) in enumerate(c["metrics"]))
    mnote = f'<p class="note center-note">{e(c["metrics_note"])}</p>' if c.get("metrics_note") else ""
    points = "".join(f"<li>{e(p)}</li>" for p in c["problem"]["points"])
    steps = "".join(
        f'<li class="step reveal" style="--d:{(i % 3) * .06:.2f}s"><span class="step-n">{i + 1:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></li>'
        for i, (t, d) in enumerate(c["steps"]))

    arch = ""
    if c.get("arch"):
        nodes = '<span class="arch-arrow" aria-hidden="true"></span>'.join(
            f'<div class="arch-node"><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in c["arch"])
        arch = f"""<section class="section-tight dark" aria-labelledby="arch-h"><div class="wrap-wide">
  <h2 class="title reveal" id="arch-h">Under the hood.</h2>
  <div class="arch reveal">{nodes}</div></div></section>"""

    gallery = ""
    if c.get("gallery"):
        figs = "".join(
            f'<figure class="shot shot-{tone} reveal" style="--d:{(i % 2) * .08:.2f}s">'
            + (browser(picture(img, alt, P), c["title"]) if tone == "dark" else f'<div class="chart-card">{picture(img, alt, P)}</div>')
            + f'<figcaption>{e(cap)}</figcaption></figure>'
            for i, (img, cap, alt, tone) in enumerate(c["gallery"]))
        gallery = f"""<section class="section-tight gray" aria-labelledby="gal-h"><div class="wrap-wide">
  <h2 class="title reveal" id="gal-h">{"Inside the model." if c["slug"] == "youtube-oracle" else "Inside the product."}</h2>
  <p class="hint reveal">Click any image to enlarge.</p>
  <div class="gallery">{figs}</div></div></section>"""

    extra = ""
    if c.get("extra") == "confusion":
        extra = f"""<section class="section-tight dark" aria-labelledby="cm-h"><div class="wrap-wide split">
  <div class="reveal"><h2 class="title" id="cm-h">How often it's right.</h2>
  <p class="lede" style="margin-top:16px">On 1,271 newer videos it never saw, the model caught <strong>700 of 785</strong> viral videos and was right <strong>92%</strong> of the times it said viral.</p></div>
  <div class="reveal" style="--d:.08s">{CONFUSION}</div></div></section>"""
    elif c.get("extra") == "flows":
        extra = f"""<section class="section-tight gray" aria-labelledby="fl-h"><div class="wrap-wide">
  <h2 class="title reveal" id="fl-h">Two systems that moved the numbers.</h2>
  <div class="reveal" style="margin-top:32px">{FLOWS}</div></div></section>"""

    reflect = ""
    blocks = []
    if c["learned"]:
        blocks.append(("What I learned", c["learned"]))
    if c["next"]:
        blocks.append(("What's next", c["next"]))
    if blocks:
        cards = "".join(f'<div class="reflect-card reveal"><h3>{t}</h3><ul>{"".join(f"<li>{e(x)}</li>" for x in xs)}</ul></div>' for t, xs in blocks)
        single = " single" if len(blocks) == 1 else ""
        reflect = f'<section class="section-tight"><div class="wrap-wide reflect{single}">{cards}</div></section>'

    note = f'<p class="note case-note">{e(c["note"])}</p>' if c.get("note") else ""
    nthumb = card_media(nxt, P)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(c["title"])} · Case study · Mohammed Saleeq Sunil</title>
  <meta name="description" content="{e(c["tagline"])} A case study by Mohammed Saleeq Sunil.">
  <meta name="theme-color" content="#000">
  <link rel="canonical" href="{SITE}work/{c["slug"]}.html">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{SITE}work/{c["slug"]}.html">
  <meta property="og:site_name" content="Mohammed Saleeq Sunil">
  <meta property="og:title" content="{e(c["title"])} · Mohammed Saleeq Sunil">
  <meta property="og:description" content="{e(c["tagline"])}">
  <meta property="og:image" content="{SITE}assets/{"work/" + hero["img"] + "-sm.jpg" if "img" in hero else "og.jpg"}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="{P}assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&display=swap">
  <link rel="stylesheet" href="{P}styles.css">
  <script>document.documentElement.classList.add('js')</script>
</head>
<body class="case">
<a class="skip-link" href="#main">Skip to content</a>
{nav(P)}
<main id="main">
<section class="case-hero dark" aria-labelledby="case-title">
  <div class="wrap-wide case-hero-copy">
    <a class="crumb" href="{P}index.html#work">All work</a>
    {f'<img class="case-logo" src="{P}assets/logos/{c["logo"][0]}" alt="{e(c["logo"][1])}" height="{30 if c["logo"][0].endswith(".svg") else 36}"{' width="116"' if c["logo"][0].endswith(".svg") else ""}>' if c.get("logo") else ""}
    <p class="eyebrow">{e(c["kicker"])}</p>
    <h1 class="headline" id="case-title">{e(c["title"])}</h1>
    <p class="lede">{e(c["tagline"])}</p>
    {f'<div class="cta-row">{links}</div>' if links else ""}
  </div>
  <div class="wrap-wide case-hero-media reveal">{media}</div>
</section>

<section class="facts" aria-label="Project facts"><div class="wrap-wide"><dl>{facts}</dl></div></section>

<section class="section-tight" aria-labelledby="res-h"><div class="wrap-wide">
  <h2 class="sr-only" id="res-h">Results</h2>
  <div class="metrics">{metrics}</div>{mnote}
</div></section>

<section class="section-tight gray" aria-labelledby="prob-h"><div class="wrap-wide split">
  <div class="reveal"><p class="eyebrow">The problem</p><h2 class="problem-text" id="prob-h" style="margin-top:10px">{e(c["problem"]["text"])}</h2></div>
  <ul class="checks reveal" style="--d:.08s">{points}</ul>
</div></section>

<section class="section-tight" aria-labelledby="how-h"><div class="wrap-wide">
  <h2 class="title reveal" id="how-h">How I built it.</h2>
  <ol class="steps">{steps}</ol>
</div></section>
{arch}{gallery}{extra}{reflect}
<div class="wrap-wide">{note}</div>

<section class="section-tight" aria-label="Next case study"><div class="wrap-wide">
  <a class="next-case reveal" href="{nxt["slug"]}.html">
    <div><p class="eyebrow">Next case study</p><h2 class="title">{e(nxt["title"])}</h2><p>{e(nxt["card_line"])}</p><span class="more">Read it</span></div>
    <div class="next-media work-media{" light" if nxt["thumb"].startswith("yo-nb") else ""}">{nthumb}</div>
  </a>
</div></section>

<section class="section-tight dark cta-band" aria-labelledby="cta-h"><div class="wrap">
  <h2 class="headline reveal" id="cta-h">Let's build what's <span class="gradient-text">next.</span></h2>
  <div class="cta-row reveal" style="--d:.08s">
    <a class="btn btn-primary" href="{P}index.html#contact">Hire me</a>
    <a class="btn btn-ghost" href="mailto:mohammedsaleeqs@gmail.com?subject=Opportunity%20for%20Mohammed">Email me</a>
    <a class="more" href="{P}assets/Mohammed_Saleeq_Sunil_Resume.pdf" download>Download resume</a>
  </div>
</div></section>
</main>
{footer(P)}
<script src="{P}main.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- homepage grid
def card_media(c, prefix):
    t = c["thumb"]
    if t.startswith("svg:"):
        key = t[4:]
        svg = SVGS[key]
        return f'<div class="card-viz">{svg}</div>'
    return picture(t, f'{c["title"]} screenshot', prefix, zoom=False)


def work_grid():
    cards = []
    for i, c in enumerate(CASES):
        big = " work-card-lg" if c.get("featured") else ""
        cards.append(f"""<a class="work-card{big} reveal" style="--d:{(i % 3) * .06:.2f}s" href="work/{c["slug"]}.html">
  <div class="work-media{" light" if c["thumb"].startswith("yo-nb") else ""}">{card_media(c, "")}</div>
  <div class="work-body">
    <p class="tile-kicker">{e(c["kicker"])}</p>
    <h3>{e(c["title"])}</h3>
    <p>{e(c["card_line"])}</p>
    <div class="work-foot"><span class="pill">{e(c["card_metric"])}</span><span class="more">Case study</span></div>
  </div>
</a>""")
    return '<div class="work-grid">\n' + "\n".join(cards) + "\n</div>"


def main():
    os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
    for i, c in enumerate(CASES):
        nxt = CASES[(i + 1) % len(CASES)]
        with open(os.path.join(ROOT, "work", c["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(case_page(c, nxt))
        print("wrote work/%s.html" % c["slug"])
    idx = os.path.join(ROOT, "index.html")
    s = open(idx, encoding="utf-8").read()
    s2 = re.sub(r"(<!-- WORK:START -->).*?(<!-- WORK:END -->)", lambda m: m.group(1) + "\n" + work_grid() + "\n" + m.group(2), s, flags=re.S)
    if s2 == s and "<!-- WORK:START -->" not in s:
        print("index.html has no WORK markers; skipped")
    else:
        open(idx, "w", encoding="utf-8").write(s2)
        print("updated index.html work grid")
    urls = [SITE] + [f"{SITE}work/{c['slug']}.html" for c in CASES]
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        f.writelines(f"  <url><loc>{u}</loc></url>\n" for u in urls)
        f.write("</urlset>\n")
    print("wrote sitemap.xml")


if __name__ == "__main__":
    main()
