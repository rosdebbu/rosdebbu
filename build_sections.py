"""Builds the README section cards (about, building, stack, research, stats) as
self-hosted terminal-style SVGs that match assets/dark_mode.svg. Needs internet
for the stats card (public GitHub API, no token)."""
import html
import json
import textwrap
import urllib.request
from collections import Counter

USER = "rosdebbu"
W = 1150
CW = 9.6  # px per character at 16px (Consolas, size-adjusted like the profile card)
BG, BORDER, TEXT = "#161b22", "#30363d", "#c9d1d9"
KEY, VAL, DIM, GREEN, CHIP = "#ffa657", "#a5d6ff", "#616e7f", "#3fb950", "#21262d"

STYLE = f"""
@font-face {{ src: local('Consolas'), local('Consolas Bold'); font-family: 'ConsolasFallback';
  font-display: swap; -webkit-size-adjust: 109%; size-adjust: 109%; }}
text, tspan {{ white-space: pre; fill: {TEXT}; }}
.key {{ fill: {KEY}; }} .val {{ fill: {VAL}; }} .dim {{ fill: {DIM}; }} .grn {{ fill: {GREEN}; }}
.lg {{ font-size: 18px; }} .b {{ font-weight: bold; }}
.cursor {{ fill: {VAL}; animation: blink 1s steps(2, start) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}"""

BRAND = {
    "TypeScript": "#3178c6", "Python": "#4b8bbe", "C++": "#f34b7d", "Bash": "#89e051",
    "React 19": "#61dafb", "Next.js": "#ffffff", "Tailwind CSS": "#06b6d4", "Vite": "#a78bfa",
    "FastAPI": "#05998b", "Node.js": "#6cc24a", "Express": "#c9d1d9", "PostgreSQL": "#5b8def",
    "MySQL": "#5b9bd1", "Prisma": "#7f8cff", "PyTorch": "#ee4c2c", "Docker": "#2496ed",
    "Linux": "#fcc624", "Vercel": "#ffffff", "Render": "#46e3b7",
}
LANG_COLORS = {
    "Python": "#3572a5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
    "CSS": "#563d7c", "C++": "#f34b7d", "C": "#8b949e", "Java": "#b07219", "Jupyter Notebook": "#da5b0b",
    "Shell": "#89e051", "Dart": "#00b4ab", "Kotlin": "#a97bff", "PHP": "#4f5d95", "Go": "#00add8",
}

esc = lambda s: html.escape(s, quote=False)


def rich(s):
    """'**x**' marks a highlighted value."""
    return "".join(f'<tspan class="val">{esc(p)}</tspan>' if i % 2 else esc(p) for i, p in enumerate(s.split("**")))


def header(title, w=W):
    x = 30 + len(title) * CW + 12
    return (f'<text x="30" y="44">{esc(title)}</text>'
            f'<line x1="{x:.0f}" y1="39" x2="{w - 30}" y2="39" stroke="{DIM}" stroke-dasharray="2 5" stroke-linecap="round"/>')


def card(h, body, label, w=W, head=True):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-size="16px" font-family="ConsolasFallback,Consolas,monospace" role="img" aria-label="{esc(label)}">
<style>{STYLE}</style>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="15" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>
{header(label.split(' — ')[0], w) if head else ''}
{body}
</svg>"""


PORTFOLIO = "debjitttt-ross.vercel.app"


def portfolio():
    body = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#a78bfa"/>'
            f'<stop offset="1" stop-color="#22d3ee"/></linearGradient></defs>'
            f'<text x="30" y="86" class="dim">$ open portfolio</text>'
            f'<text x="30" y="136" class="val b" font-size="36px">{PORTFOLIO}</text>'
            f'<text x="30" y="170" class="lg">Debjit Das — Portfolio · <tspan class="key">projects</tspan>, '
            f'<tspan class="key">research</tspan> and <tspan class="key">experiments</tspan></text>'
            f'<rect x="{W - 290}" y="96" width="260" height="56" rx="12" fill="url(#g)"/>'
            f'<text x="{W - 160}" y="131" text-anchor="middle" class="b lg" style="fill:#0d1117">Visit portfolio -&gt;</text>')
    return card(206, body, "portfolio — Debjit Das")


def tile(kind, handle, accent, hint):
    body = (f'<rect x="24" y="26" width="4" height="64" rx="2" fill="{accent}"/>'
            f'<text x="44" y="42" class="dim">// {kind}</text>'
            f'<text x="44" y="70" class="val b lg">{esc(handle)}</text>'
            f'<text x="44" y="94" class="dim">{hint} -&gt;</text>')
    return card(116, body, f"{kind} — {handle}", w=366, head=False)


def chips(items, x, y):
    out = ""
    for name in items:
        w = 26 + len(name) * 8.4 + 14
        out += (f'<rect x="{x:.0f}" y="{y - 20}" width="{w:.0f}" height="30" rx="8" fill="{CHIP}" stroke="{BORDER}"/>'
                f'<circle cx="{x + 14:.0f}" cy="{y - 5}" r="4.5" fill="{BRAND[name]}"/>'
                f'<text x="{x + 26:.0f}" y="{y}" font-size="14px">{esc(name)}</text>')
        x += w + 10
    return out


def about():
    lines = ["B.Tech CSE (**Data Science**) student at **SRMIST**, batch of '28",
             "**Full-stack developer** building production systems",
             "Researching **Graph Neural Networks (GNNs)**",
             "Always **building • learning • shipping**"]
    body = '<text x="30" y="86" class="dim">$ whoami</text>'
    for i, line in enumerate(lines):
        body += f'<text x="30" y="{124 + i * 34}" class="lg"><tspan class="key">&gt; </tspan>{rich(line)}</text>'
    end = 124 + len(lines) * 34 + 6
    body += f'<text x="30" y="{end}" class="dim">$ <tspan class="cursor">█</tspan></text>'
    return card(end + 34, body, "about")


def building():
    desc = textwrap.wrap("A production-grade full-stack system with a React dashboard, FastAPI backend, PostgreSQL (Neon) "
                         "with connection pooling, a WebSocket matrix viewer, automated cron reporting, and codebase "
                         "knowledge graph analysis.", 100)
    body = (f'<text x="30" y="92" class="val b" font-size="28px">Openzess</text>'
            f'<text x="{W - 30}" y="90" text-anchor="end"><tspan class="grn">● </tspan>in development</text>'
            f'<text x="30" y="124" class="key lg">Autonomous Agent Platform &amp; Open Hardware Toolkit</text>')
    for i, line in enumerate(desc):
        body += f'<text x="30" y="{160 + i * 28}" class="lg">{esc(line)}</text>'
    y = 160 + len(desc) * 28 + 26
    body += chips(["TypeScript", "React 19", "Python", "FastAPI", "PostgreSQL", "Docker"], 30, y)
    body += f'<text x="{W - 30}" y="{y}" text-anchor="end" class="dim">github.com/{USER}/openzess -&gt;</text>'
    return card(y + 36, body, "currently.building — Openzess")


def stack():
    groups = {"languages": ["TypeScript", "Python", "C++", "Bash"],
              "frontend": ["React 19", "Next.js", "Tailwind CSS", "Vite"],
              "backend/data": ["FastAPI", "Node.js", "Express", "PostgreSQL", "MySQL", "Prisma"],
              "ai-ml/infra": ["PyTorch", "Docker", "Linux", "Vercel", "Render"]}
    body = ""
    for i, (name, items) in enumerate(groups.items()):
        y = 96 + i * 54
        body += f'<text x="30" y="{y}" class="key">{name}</text>' + chips(items, 220, y)
    return card(96 + len(groups) * 54 - 8, body, "stack")


def research():
    items = [("Graph Neural Networks", "Spectral graph theory, message-passing neural networks, and graph-based representations for structured data."),
             ("ESP32 Smart Sensing", "Embedded hardware/software system for real-time environmental monitoring with sensor fusion and wireless telemetry."),
             ("Fluid Dynamics (CFD)", "OpenFOAM wave simulations in Linux with custom mesh generation and ParaView post-processing.")]
    col = (W - 60) / 3
    body = ""
    for i, (title, desc) in enumerate(items):
        x = 30 + i * col + (24 if i else 0)
        if i:
            body += f'<line x1="{30 + i * col:.0f}" y1="70" x2="{30 + i * col:.0f}" y2="250" stroke="{BORDER}"/>'
        body += f'<text x="{x:.0f}" y="84" class="dim">[0{i + 1}]</text><text x="{x:.0f}" y="112" class="key lg b">{esc(title)}</text>'
        for j, line in enumerate(textwrap.wrap(desc, 31)):
            body += f'<text x="{x:.0f}" y="{146 + j * 26}">{esc(line)}</text>'
    return card(284, body, "research.systems")


def get(path):
    req = urllib.request.Request(f"https://api.github.com/{path}", headers={"User-Agent": "profile-cards"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def stats():
    user = get(f"users/{USER}")
    repos = get(f"users/{USER}/repos?per_page=100")
    langs = Counter(r["language"] for r in repos if r["language"] and not r["fork"]).most_common(6)
    total = sum(n for _, n in langs)
    rows = [("Repos", user["public_repos"]), ("Stars", sum(r["stargazers_count"] for r in repos)),
            ("Followers", user["followers"]), ("Following", user["following"]),
            ("Member.since", user["created_at"][:4])]
    body = '<text x="30" y="86" class="dim">$ gh stats --user ' + USER + '</text>'
    for i, (k, v) in enumerate(rows):
        dots = "." * (34 - len(k) - len(str(v)) - 4)
        body += (f'<text x="30" y="{128 + i * 36}" class="lg"><tspan class="dim">. </tspan><tspan class="key">{k}</tspan>'
                 f'<tspan class="dim"> {dots} </tspan><tspan class="val b">{v}</tspan></text>')
    body += f'<line x1="540" y1="70" x2="540" y2="{128 + len(rows) * 36 - 20}" stroke="{BORDER}"/>'
    body += '<text x="570" y="86" class="dim">$ top languages (by repo)</text>'
    for i, (lang, n) in enumerate(langs):
        y = 128 + i * 36
        w = max(8, 300 * n / total)
        body += (f'<text x="570" y="{y}" class="lg">{esc(lang)}</text>'
                 f'<rect x="760" y="{y - 14}" width="300" height="14" rx="7" fill="{CHIP}"/>'
                 f'<rect x="760" y="{y - 14}" width="{w:.0f}" height="14" rx="7" fill="{LANG_COLORS.get(lang, "#8b949e")}"/>'
                 f'<text x="1072" y="{y}" class="dim">{round(100 * n / total)}%</text>')
    return card(128 + max(len(rows), len(langs)) * 36 + 4, body, "github.stats")


if __name__ == "__main__":
    for kind, handle, accent, hint in [("linkedin", "debjit-das-6b0452327", "#58a6ff", "connect"),
                                       ("leetcode", "debbjitttt", "#ffa116", "see my solves"),
                                       ("email", "debjitsince90908@gmail.com", "#ea4335", "get in touch")]:
        with open(f"assets/link_{kind}.svg", "w", encoding="utf-8") as f:
            f.write(tile(kind, handle, accent, hint))
        print(f"assets/link_{kind}.svg created!")
    for name, fn in [("portfolio", portfolio), ("about", about), ("building", building), ("stack", stack), ("research", research), ("stats", stats)]:
        with open(f"assets/{name}.svg", "w", encoding="utf-8") as f:
            f.write(fn())
        print(f"assets/{name}.svg created!")
