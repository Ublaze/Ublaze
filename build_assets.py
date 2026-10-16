"""Generate the "Ledger" profile assets (light + dark SVG pairs).

    python build_assets.py

Every SVG in assets/ (except the legacy avatar) is produced here -- never hand-edit them.
Fonts are instanced from the variable sources in fonts/, subset to exactly the glyphs
each SVG uses, and embedded as base64 WOFF so GitHub's <img> sandbox renders them
identically on every OS.
"""
import base64
import io
import math
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).parent
FONTS = ROOT / "fonts"
OUT = ROOT / "assets"

# ── tokens ────────────────────────────────────────────────────────────────
THEMES = {
    "light": dict(paper="#F7F4EC", ink="#1B1F24", ink2="#3A3F45", rule="#D9D2C0",
                  faint="#E7E1D2", muted="#6B6558", red="#A3362A", gold="#B08A3E"),
    "dark": dict(paper="#12161C", ink="#ECE6D8", ink2="#C9C2B3", rule="#2E3640",
                 faint="#1E242C", muted="#8D8676", red="#D9705F", gold="#D7A94B"),
}

FACES = {
    "display": ("Fraunces.ttf", {"wght": 600, "opsz": 144, "SOFT": 0, "WONK": 0}),
    "serif": ("Fraunces.ttf", {"wght": 560, "opsz": 48, "SOFT": 0, "WONK": 0}),
    "serif-it": ("Fraunces-Italic.ttf", {"wght": 400, "opsz": 24, "SOFT": 0, "WONK": 0}),
    "sans": ("IBMPlexSans.ttf", {"wght": 400, "wdth": 100}),
    "sans-md": ("IBMPlexSans.ttf", {"wght": 500, "wdth": 100}),
    "mono": ("IBMPlexMono-Regular.ttf", None),
    "mono-md": ("IBMPlexMono-Medium.ttf", None),
}

W = 1280          # every full-width page is 1280 wide
X0 = 124          # text column start (right of the red margin)
X1 = W - 64       # right edge for right-aligned figures
MARGIN = (96, 102)  # double red margin line, like real ledger paper


# ── fonts ─────────────────────────────────────────────────────────────────
@lru_cache(maxsize=None)
def font_bytes(face):
    src, axes = FACES[face]
    f = TTFont(FONTS / src)
    if axes:
        f = instantiateVariableFont(f, axes)
    buf = io.BytesIO()
    f.save(buf)
    return buf.getvalue()


@lru_cache(maxsize=None)
def metrics(face):
    f = TTFont(io.BytesIO(font_bytes(face)))
    return f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm


def measure(text, face, size, ls=0.0):
    cmap, hmtx, upem = metrics(face)
    units = sum(hmtx[cmap[ord(c)]][0] if ord(c) in cmap else upem * 0.5 for c in text)
    return units * size / upem + ls * len(text)


def wrap(text, face, size, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and measure(trial, face, size) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur] if cur else lines


def subset_woff(face, chars):
    f = TTFont(io.BytesIO(font_bytes(face)))
    opts = Options()
    opts.flavor = "woff"
    opts.hinting = False
    opts.desubroutinize = True
    opts.layout_features = ["kern", "liga", "lnum", "tnum"]
    sub = Subsetter(opts)
    sub.populate(text="".join(sorted(chars)) + " ")
    sub.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff"
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


# ── svg builder ───────────────────────────────────────────────────────────
class Svg:
    def __init__(self, w, h, theme):
        self.w, self.h, self.c = w, h, THEMES[theme]
        self.parts, self.used = [], {}

    def add(self, s):
        self.parts.append(s)

    def col(self, key):
        return self.c.get(key, key)

    def text(self, x, y, s, face, size, fill="ink", anchor="start", ls=0, attrs=""):
        self.used.setdefault(face, set()).update(s)
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        l = f' letter-spacing="{ls}"' if ls else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" class="{face}" font-size="{size}" '
                 f'fill="{self.col(fill)}"{a}{l}{attrs}>{escape(s)}</text>')

    def line(self, x1, y1, x2, y2, stroke="rule", w=1, attrs=""):
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{self.col(stroke)}" '
                 f'stroke-width="{w}"{attrs}/>')

    def double_rule(self, x1, x2, y, stroke="gold"):
        self.line(x1, y, x2, y, stroke, 1.5)
        self.line(x1, y + 5, x2, y + 5, stroke, 1.5)

    def paper(self, margin=True):
        """Card background + red ledger margin."""
        self.add(f'<rect x="0.5" y="0.5" width="{self.w - 1}" height="{self.h - 1}" rx="14" '
                 f'fill="{self.c["paper"]}" stroke="{self.c["rule"]}"/>')
        if margin:
            for x in MARGIN:
                self.line(x, 1, x, self.h - 1, "red", 1, ' stroke-opacity="0.55"')

    def render(self, title):
        css = []
        for face, chars in self.used.items():
            css.append(f"@font-face{{font-family:'L-{face}';src:url(data:font/woff;base64,"
                       f"{subset_woff(face, chars)}) format('woff');}}")
            css.append(f".{face}{{font-family:'L-{face}',serif;}}")
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" role="img"><title>{escape(title)}</title>'
                f'<style>{"".join(css)}</style>\n' + "\n".join(self.parts) + "\n</svg>\n")


def schedule_header(s, label, title, note=None):
    """Shared top block for every page after the hero: SCHEDULE X + serif title + rule."""
    s.text(X0, 58, label, "mono-md", 15, "muted", ls=3)
    s.text(X0, 112, title, "serif", 42)
    if note:
        for i, ln in enumerate(note):
            s.text(X1, 112 - (len(note) - 1 - i) * 26, ln, "serif-it", 19, "muted", "end")
    s.line(X0, 136, X1, 136, "ink", 1.2)


# ── folio 01: hero / journal ──────────────────────────────────────────────
JOURNAL = [  # date, particulars, ref, term
    ("2012", "Zillione — ERP implementation & delivery", "DYNAMICS NAV · NETSUITE", "5 yrs"),
    ("2017", "RFR Group, Dubai — enterprise delivery lead", "SAGE 300 · SAGE X3", "9 yrs"),
    ("", "Sage X3 Certified Financial Application Consultant", "WWSX3FC200", "cert."),
    ("", "BTEC HND Computing — Gold Medal, batch top", "EDEXCEL", "award"),
    ("", "Delivery across UAE · Sri Lanka · Maldives · Fiji", "ON-SITE & REMOTE", "4"),
]
BALANCE = [("15+", "years"), ("100+", "projects"), ("4", "countries")]
STATEMENT = ("Enterprise delivery lead based in Dubai. I take ERP projects from discovery "
             "to go-live, then build the integrations, reporting and infrastructure that "
             "keep them running.")


def stamp(s, cx, cy):
    """Rubber 'POSTED' stamp -- the one red flourish on the page."""
    r_text = 71
    ring = "ENTERPRISE DELIVERY · DUBAI · UAE · "
    s.add(f'<g transform="rotate(-9 {cx} {cy})" opacity="0.9">')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="92" fill="none" stroke="{s.c["red"]}" stroke-width="3"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="58" fill="none" stroke="{s.c["red"]}" stroke-width="1.5"/>')
    s.add(f'<path id="ring" fill="none" d="M {cx - r_text} {cy} a {r_text} {r_text} 0 1 1 '
          f'{2 * r_text} 0 a {r_text} {r_text} 0 1 1 {-2 * r_text} 0"/>')
    # stretch letter-spacing so the ring text closes on itself
    circ = 2 * math.pi * r_text
    ls = (circ - measure(ring, "mono-md", 15)) / len(ring)
    s.used.setdefault("mono-md", set()).update(ring)
    s.add(f'<text class="mono-md" font-size="15" fill="{s.c["red"]}" letter-spacing="{ls:.2f}">'
          f'<textPath href="#ring">{escape(ring)}</textPath></text>')
    s.text(cx, cy + 4, "POSTED", "mono-md", 21, "red", "middle", ls=3)
    s.text(cx, cy + 26, "SINCE 2012", "mono", 13, "red", "middle", ls=2)
    s.add("</g>")


def hero(theme):
    H = 800
    s = Svg(W, H, theme)
    s.paper()
    # folio strip
    s.text(X0, 46, "GENERAL LEDGER · UWAIS SALAM", "mono-md", 15, "muted", ls=3)
    s.text(X1, 46, "FOLIO 01 · FY 2026", "mono-md", 15, "muted", "end", ls=3)
    s.line(0, 66, W, 66, "rule")
    # name + statement
    s.text(X0 - 4, 192, "Uwais Salam", "display", 108)
    for i, ln in enumerate(wrap(STATEMENT, "sans", 24, 800)):
        s.text(X0, 250 + i * 34, ln, "sans", 24, "ink2")
    stamp(s, 1086, 186)

    # journal
    top, head_h, row_h = 360, 44, 48
    cols = {"date": X0, "part": 232, "ref": 846, "term": X1}
    rules_x = [214, 828, 1104]
    body_top = top + head_h
    body_bot = body_top + row_h * len(JOURNAL)
    for x in rules_x:
        s.line(x, top, x, body_bot, "faint", 1)
    s.line(X0, top, X1, top, "rule")
    for key, label, anchor in (("date", "DATE", "start"), ("part", "PARTICULARS", "start"),
                               ("ref", "REF", "start"), ("term", "TERM", "end")):
        s.text(cols[key], top + 29, label, "mono-md", 14, "muted", anchor, ls=2.5)
    s.line(X0, body_top, X1, body_top, "ink", 1.2)
    for i, (date, part, ref, term) in enumerate(JOURNAL):
        y = body_top + row_h * i + 31
        if date:
            s.text(cols["date"], y, date, "mono", 18, "ink")
        s.text(cols["part"], y, part, "sans", 20, "ink")
        s.text(cols["ref"], y, ref, "mono", 15, "muted", ls=1)
        s.text(cols["term"], y, term, "mono-md", 18, "ink", "end")
        if i < len(JOURNAL) - 1:
            s.line(X0, body_top + row_h * (i + 1), X1, body_top + row_h * (i + 1), "faint")
    # balance carried forward: single rule above, double rule below
    s.line(X0, body_bot, X1, body_bot, "ink", 1.2)
    by = body_bot + 74
    s.text(X0, by - 8, "BALANCE", "mono-md", 14, "muted", ls=2.5)
    s.text(X0, by + 14, "C/F", "mono-md", 14, "muted", ls=2.5)
    x = cols["part"]
    for fig, label in BALANCE:
        s.text(x, by + 4, fig, "serif", 52)
        fw = measure(fig, "serif", 52)
        s.text(x + fw + 12, by + 4, label, "serif-it", 24, "ink2")
        x += fw + 12 + measure(label, "serif-it", 24) + 84
    s.double_rule(X0, X1, by + 40)
    return s.render("Uwais Salam — general ledger: enterprise delivery lead, Dubai")


# ── schedule A: chart of accounts (what I do) ─────────────────────────────
ACCOUNTS = [
    ("1000", "ERP Delivery", "SAGE 300 \u00b7 SAGE X3",
     "Discovery to go-live, fit-gap and execution planning, recovery of at-risk projects, health checks."),
    ("2000", "Integrations & APIs", "LAMBDA \u00b7 API GATEWAY \u00b7 DYNAMODB",
     "REST APIs and sync engines that put ERP data in front of portals, marketplaces and partners."),
    ("3000", "Reporting & Data", "SQL SERVER \u00b7 SSRS",
     "SQL Server reporting layers, branded SSRS portals, and dashboards leadership actually reads."),
    ("4000", "Infrastructure & Automation", "POWERSHELL \u00b7 PYTHON",
     "Windows Server, IIS, VPN and backup pipelines, automated end to end and monitored."),
]


def practice(theme):
    row_h = 92
    H = 136 + row_h * len(ACCOUNTS) + 40
    s = Svg(W, H, theme)
    s.paper()
    schedule_header(s, "SCHEDULE A", "Chart of Accounts",
                    ["Most of the work sits in private client systems;", "these are the books it is kept in."])
    for i, (code, name, tag, desc) in enumerate(ACCOUNTS):
        top = 136 + row_h * i
        s.text(X0, top + 42, code, "mono-md", 19, "gold", ls=1)
        s.text(232, top + 42, name, "serif", 29)
        s.text(X1, top + 40, tag, "mono", 15, "muted", "end", ls=1)
        s.text(232, top + 72, desc, "sans", 19, "ink2")
        s.line(X0, top + row_h, X1, top + row_h, "faint" if i < len(ACCOUNTS) - 1 else "ink",
               1 if i < len(ACCOUNTS) - 1 else 1.2)
    s.line(214, 136, 214, 136 + row_h * len(ACCOUNTS), "faint")
    return s.render("Schedule A \u2014 chart of accounts: ERP delivery, integrations, reporting, infrastructure")


# ── schedule D: trial balance (toolbox) ───────────────────────────────────
TOOLS = [
    ("ERP", ["Sage 300", "Sage X3", "NetSuite OneWorld", "Dynamics NAV", "OpenAir", "MS Project Server"]),
    ("DATA & REPORTING", ["SQL Server", "SSRS", "Crystal Reports", "Python", "PowerShell"]),
    ("CLOUD & INFRA", ["AWS Lambda", "API Gateway", "DynamoDB", "S3 \u00b7 CloudFront", "Windows Server", "IIS"]),
    ("BUILD", ["Git \u00b7 GitHub Actions", "Kotlin \u00b7 Android", "Postman", "VS Code", "Claude Code"]),
]


def toolbox(theme):
    rows = max(len(items) for _, items in TOOLS)
    line_h, top = 38, 136
    list_top = top + 70
    total_y = list_top + rows * line_h + 30
    H = total_y + 64
    s = Svg(W, H, theme)
    s.paper()
    schedule_header(s, "SCHEDULE D", "Trial Balance", ["Tools carried on the books,", "by account."])
    col_w = (X1 - X0) / len(TOOLS)
    for i, (head, items) in enumerate(TOOLS):
        x = X0 + col_w * i
        right = x + col_w - 36
        s.text(x, top + 42, head, "mono-md", 14, "muted", ls=2.5)
        s.text(right, top + 42, f"{len(items):02d}", "mono-md", 14, "gold", "end", ls=1)
        s.line(x, top + 58, right, top + 58, "rule")
        for j, item in enumerate(items):
            s.text(x, list_top + 22 + j * line_h, item, "sans", 20, "ink")
    total = sum(len(items) for _, items in TOOLS)
    s.line(X0, total_y - 20, X1, total_y - 20, "ink", 1.2)
    s.text(X0, total_y + 10, "TOTAL ENTRIES", "mono-md", 14, "muted", ls=2.5)
    s.text(X1, total_y + 12, str(total), "serif", 30, "ink", "end")
    s.double_rule(X0, X1, total_y + 28)
    return s.render("Schedule D \u2014 trial balance: " + "; ".join(
        f"{h.title()}: {', '.join(i)}" for h, i in TOOLS))


# ── section strips (headings for the markdown-driven sections) ───────────
def strip(label, title, note):
    def build(theme):
        s = Svg(W, 160, theme)
        s.paper()
        schedule_header(s, label, title, note)
        return s.render(f"{label.title()} \u2014 {title}")
    return build


# ── schedule B: project vouchers ──────────────────────────────────────────
PROJECTS = [  # repo, one-liner, account (language)
    ("Quran-FlipBoard-TV", "Quran verses on a retro split-flap board for LG webOS TVs, an ambient display.", "JavaScript"),
    ("Caffeinator", "Process-aware Windows sleep prevention with per-app rules and a tray UI.", "Python"),
    ("Windows11-Optimizer", "One safe PowerShell script to strip bloat and tune Windows 11.", "PowerShell"),
    ("YTune", "An Android YouTube Music client with Google Sign-In and playlist sync.", "Kotlin"),
    ("github-readme-generator", "Claude Code skill: polished READMEs with banners, badges and diagrams.", "Claude skill"),
    ("github-showcase", "Claude Code skill: turns any repo into styled LinkedIn and Facebook posts.", "Python"),
    ("VHD2Wasabi", "Live server disks to Wasabi S3: VSS capture streamed through 7-Zip, no local staging.", "Python"),
]
VW, VH, STUB = 600, 200, 150


def voucher(no, repo, desc, lang):
    def build(theme):
        s = Svg(VW, VH, theme)
        perf = VW - STUB
        c = s.c
        # paper with two semicircle notches at the perforation
        s.add(f'<mask id="m"><rect width="{VW}" height="{VH}" fill="#fff"/>'
              f'<circle cx="{perf}" cy="0" r="11" fill="#000"/><circle cx="{perf}" cy="{VH}" r="11" fill="#000"/></mask>')
        s.add(f'<g mask="url(#m)"><rect x="0.5" y="0.5" width="{VW - 1}" height="{VH - 1}" rx="12" '
              f'fill="{c["paper"]}" stroke="{c["rule"]}"/>'
              f'<circle cx="{perf}" cy="0" r="11.5" fill="none" stroke="{c["rule"]}"/>'
              f'<circle cx="{perf}" cy="{VH}" r="11.5" fill="none" stroke="{c["rule"]}"/></g>')
        s.line(perf, 16, perf, VH - 16, "rule", 1.5, ' stroke-dasharray="2 6" stroke-linecap="round"')
        # body
        x, wmax = 32, perf - 64
        s.text(x, 40, "VOUCHER \u00b7 PUBLIC BUILD", "mono-md", 14, "muted", ls=2.5)
        size = 34
        while measure(repo, "serif", size) > wmax and size > 22:
            size -= 1
        s.text(x, 86, repo, "serif", size)
        for i, ln in enumerate(wrap(desc, "sans", 18, wmax)[:2]):
            s.text(x, 120 + i * 26, ln, "sans", 18, "ink2")
        s.text(x, VH - 22, f"github.com/Ublaze/{repo}", "mono", 14, "muted")
        # stub
        cx = perf + STUB / 2
        s.text(cx, 52, "No.", "serif-it", 18, "muted", "middle")
        s.text(cx, 116, f"{no:02d}", "serif", 58, "gold", "middle")
        s.line(perf + 28, 140, VW - 28, 140, "rule")
        s.text(cx, 166, lang.upper(), "mono-md", 13, "muted", "middle", ls=1.5)
        return s.render(f"Voucher {no:02d} \u2014 {repo}: {desc}")
    return build


VOUCHERS = {f"v-{r.lower()}": voucher(i + 1, r, d, l) for i, (r, d, l) in enumerate(PROJECTS)}


# ── avatar: monogram for the GitHub profile picture (cropped to a circle) ─
def avatar(theme):
    A = 1024
    s = Svg(A, A, theme)
    s.add(f'<rect width="{A}" height="{A}" fill="{s.c["paper"]}"/>')
    for x in (282, 296):
        s.line(x, 190, x, 834, "red", 4, ' stroke-opacity="0.65"')
    s.text(560, 700, "U", "display", 640, "ink", "middle")
    s.line(360, 752, 760, 752, "gold", 7)
    s.line(360, 772, 760, 772, "gold", 7)
    return s.render("Uwais Salam monogram")


PAGES = {"hero": hero, "practice": practice, "toolbox": toolbox,
         "head-builds": strip("SCHEDULE B", "Vouchers", ["Public builds \u2014", "the side projects, open source."]),
         "head-private": strip("SCHEDULE C", "Client Engagements", ["Names withheld;", "the shape of the work, not the client."]),
         "avatar": avatar, **VOUCHERS}


def main():
    OUT.mkdir(exist_ok=True)
    for name, fn in PAGES.items():
        for theme in THEMES:
            svg = fn(theme)
            path = OUT / f"{name}-{theme}.svg"
            path.write_text(svg, encoding="utf-8")
            print(f"{path.relative_to(ROOT)}  {len(svg) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
