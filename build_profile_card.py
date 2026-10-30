import os
import html
import colorsys
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

# -------------------------------------------------------------
# Portrait: turn assets/profile.jpg into a coloured ASCII portrait
# -------------------------------------------------------------
PHOTO = os.path.join("assets", "profile.jpg")
CROP = (860, 300, 1410, 985)   # head, neck and shoulders, in original photo pixels
COLS = 128                      # characters per row
CELL_W, CELL_H = 4.0, 8.0       # px per character cell (font-size 7px)
RAMP = " .`'^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"  # light -> dense
PALETTE_SIZE = 64
CARD_W, CARD_H = 1150, 672      # card size in px
RX = 550                        # left edge of the info column


def load_portrait():
    """Return (rows, cells) where each cell is (density 0..1, (r, g, b))."""
    img = Image.open(PHOTO).convert("RGB").crop(CROP)
    w, h = img.size
    rows = round(COLS * (h / w) * (CELL_W / CELL_H))

    # work at 4x the target grid, then average down so each char gets real detail
    big = img.resize((COLS * 4, rows * 4), Image.LANCZOS)

    # background mask: the foliage is green/yellow and saturated, skin/hair/shirt are not
    hsv = np.asarray(big.convert("HSV"), dtype=float)
    hue, sat, val = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    foliage = (hue > 44) & (hue < 180) & (sat > 0.14) & (val > 0.10)
    mask = Image.fromarray(np.where(foliage, 0, 255).astype("uint8"))
    # drop specks, then keep only the region connected to the face
    mask = mask.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
    mask = mask.filter(ImageFilter.MedianFilter(9))
    ImageDraw.floodfill(mask, (mask.width // 2, int(mask.height * 0.5)), 128, thresh=0)
    mask = Image.fromarray(np.where(np.asarray(mask) == 128, 255, 0).astype("uint8"))
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    cover = np.asarray(mask.resize((COLS, rows), Image.BOX), dtype=float) / 255.0
    cover = np.clip((cover - 0.25) / 0.5, 0, 1)
    # cells that are mostly leaf pixels fade out even if they touch the hair
    leaf = foliage.reshape(rows, 4, COLS, 4).mean(axis=(1, 3))
    cover *= 1 - np.clip((leaf - 0.08) / 0.30, 0, 1)
    cover = cover * cover * (3 - 2 * cover)  # smoothstep

    big = ImageEnhance.Color(big).enhance(1.05)
    big = big.filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=2))
    small = big.resize((COLS, rows), Image.BOX)

    # stretch luminance over the subject only, so eyes, nose and moustache stand out
    lum = np.asarray(small.convert("L"), dtype=float) / 255.0
    lo, hi = np.percentile(lum[cover > 0.5], [2, 98])
    lum = np.clip((lum - lo) / (hi - lo), 0, 1)

    # unsharp-mask the cell grid so facial features separate from the skin
    lum_img = Image.fromarray((lum * 255).astype("uint8"))
    blur = np.asarray(lum_img.filter(ImageFilter.GaussianBlur(4)), dtype=float) / 255.0
    lum = np.clip(lum + 0.9 * (lum - blur), 0, 1)

    cells = []
    for y in range(rows):
        row = []
        for x in range(COLS):
            # gentle fade at the bottom edge so the crop doesn't end abruptly
            edge = min(1.0, (rows - y) / 6.0)
            dx, dy = (x + 0.5) / COLS - 0.5, (y + 0.5) / rows - 0.45
            oval = np.exp(-((dx / 0.72) ** 2 + (dy / 0.95) ** 2) ** 2)
            row.append((lum[y, x], small.getpixel((x, y)), cover[y, x] * edge * oval))
        cells.append(row)
    return rows, cells


ROWS, CELLS = load_portrait()


def build_ascii(is_dark):
    """Coloured <text> rows plus the CSS classes that colour them."""
    # per-cell colour tuned for the background
    colours = Image.new("RGB", (COLS, ROWS))
    dens = []
    for y in range(ROWS):
        drow = []
        for x in range(COLS):
            lum, (r, g, b), fade = CELLS[y][x]
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if is_dark:
                v = 0.55 + 0.45 * lum ** 0.8
                d = (0.18 + 0.82 * lum ** 0.85) * fade
                s *= 0.7
            else:
                v = 0.10 + 0.55 * lum ** 0.8
                d = (0.1 + 0.9 * (1 - lum) ** 0.9) * fade
                s *= 0.9
            colours.putpixel((x, y), tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, min(1, s), v)))
            drow.append(d)
        dens.append(drow)

    quant = colours.quantize(colors=PALETTE_SIZE, method=Image.MEDIANCUT)
    pal = quant.getpalette()
    css = "\n".join(
        f".c{i}{{fill:#{pal[i*3]:02x}{pal[i*3+1]:02x}{pal[i*3+2]:02x};}}" for i in range(PALETTE_SIZE)
    )

    top = (CARD_H - ROWS * CELL_H) / 2 + CELL_H - 2
    width = COLS * CELL_W
    lines = []
    for y in range(ROWS):
        runs = []
        cur_cls, cur_txt = None, ""
        for x in range(COLS):
            idx = min(len(RAMP) - 1, int(dens[y][x] * (len(RAMP) - 1) + 0.5))
            ch = RAMP[idx]
            cls = quant.getpixel((x, y))
            if ch == " " or cls == cur_cls:
                cur_txt += ch
                continue
            if cur_cls is not None:
                runs.append((cur_cls, cur_txt))
            cur_cls, cur_txt = cls, ch
        if cur_cls is not None:
            runs.append((cur_cls, cur_txt))
        elif cur_txt:
            runs.append((0, cur_txt))
        spans = "".join(f'<tspan class="c{c}">{html.escape(t)}</tspan>' for c, t in runs)
        lines.append(
            f'<text x="15" y="{top + y * CELL_H:.1f}" font-size="7px" '
            f'textLength="{width:.0f}" lengthAdjust="spacing">{spans}</text>'
        )
    return css, "\n".join(lines)


def create_svg(mode="dark"):
    is_dark = (mode == "dark")

    bg_color = "#161b22" if is_dark else "#f6f8fa"
    border_color = "#30363d" if is_dark else "#d0d7de"
    text_color = "#c9d1d9" if is_dark else "#24292f"
    key_color = "#ffa657" if is_dark else "#cf222e"
    val_color = "#a5d6ff" if is_dark else "#0969da"
    dot_color = "#616e7f" if is_dark else "#8c959f"
    add_color = "#3fb950" if is_dark else "#1a7f37"
    del_color = "#f85149" if is_dark else "#cf222e"

    ascii_css, ascii_block = build_ascii(is_dark)

    def build_kv(y, key, val, target_cols=58):
        # Target total columns on right side = target_cols
        # Structure: ". " (2) + key + ": " (2) + dots + val
        # len = 2 + len(key) + 2 + len(dots) + len(val)
        used = 2 + len(key) + 2 + len(val)
        dot_count = max(3, target_cols - used)
        dots = " " + ("." * (dot_count - 2)) + " "
        safe_key = html.escape(key)
        safe_val = html.escape(val)
        return (f'<tspan x="550" y="{y}" class="cc">. </tspan>'
                f'<tspan class="key">{safe_key}</tspan>:'
                f'<tspan class="cc">{dots}</tspan>'
                f'<tspan class="value">{safe_val}</tspan>')

    def build_header(y, title, char="-", target_cols=58):
        rem = target_cols - len(title) - 1
        dashes = " " + (char * max(4, rem))
        safe_title = html.escape(title)
        return f'<tspan x="550" y="{y}">{safe_title}</tspan><tspan class="cc">{dashes}</tspan>'

    right_tspans = [
        # 0 (y=30)
        build_header(30, "debjit@srmist", "-"),
        # 1 (y=50)
        build_kv(50, "OS", "Linux (Ubuntu / Arch), Windows 11"),
        # 2 (y=70)
        build_kv(70, "Uptime", "B.Tech 2nd Year (Batch of '28)"),
        # 3 (y=90)
        build_kv(90, "Host", "SRM Institute of Science & Tech"),
        # 4 (y=110)
        build_kv(110, "Kernel", "Full Stack Dev & GNN Researcher"),
        # 5 (y=130)
        build_kv(130, "IDE", "VS Code, Neovim, Cursor"),
        # 6 (y=150)
        '<tspan x="550" y="150" class="cc">. </tspan>',
        # 7 (y=170)
        build_kv(170, "Languages.Programming", "TypeScript, Python, C++, Bash"),
        # 8 (y=190)
        build_kv(190, "Languages.Computer", "HTML5, CSS3, SQL, JSON, LaTeX"),
        # 9 (y=210)
        build_kv(210, "Languages.Real", "English, Bengali, Hindi"),
        # 10 (y=230)
        '<tspan x="550" y="230" class="cc">. </tspan>',
        # 11 (y=250)
        build_kv(250, "Frameworks.FullStack", "React 19, Next.js, FastAPI, Node.js"),
        # 12 (y=270)
        build_kv(270, "Systems.Data & Cloud", "PostgreSQL, Neon, Docker, Prisma"),
        # 13 (y=290)
        build_kv(290, "Research.Focus", "Graph Neural Networks, CFD"),
        # 14 (y=310)
        build_header(310, "- Contact", "-"),
        # 15 (y=330)
        build_kv(330, "Email", "debjitsince90908@gmail.com"),
        # 16 (y=350)
        build_kv(350, "LinkedIn", "debjit-das-6b0452327"),
        # 17 (y=370)
        build_kv(370, "LeetCode", "debbjitttt"),
        # 18 (y=390)
        build_kv(390, "Portfolio", "debjitttt-ross.vercel.app"),
        # 19 (y=410)
        build_kv(410, "GitHub", "rosdebbu"),
        # 20 (y=430)
        '<tspan x="550" y="430" class="cc">. </tspan>',
        # 21 (y=450)
        build_header(450, "- GitHub Stats", "-"),
        # 22 (y=470)
        f'<tspan x="550" y="470" class="cc">. </tspan><tspan class="key">Repos</tspan>:<tspan class="cc"> .... </tspan><tspan class="value">48</tspan> {{<tspan class="key">Contributed</tspan>: <tspan class="value">56</tspan>}} | <tspan class="key">Stars</tspan>:<tspan class="cc"> ........... </tspan><tspan class="value">5</tspan>',
        # 23 (y=490)
        f'<tspan x="550" y="490" class="cc">. </tspan><tspan class="key">Commits</tspan>:<tspan class="cc"> ................. </tspan><tspan class="value">680+</tspan> | <tspan class="key">Followers</tspan>:<tspan class="cc"> ....... </tspan><tspan class="value">9</tspan>',
        # 24 (y=510)
        f'<tspan x="550" y="510" class="cc">. </tspan><tspan class="key">Lines of Code on GitHub</tspan>:<tspan class="cc">. </tspan><tspan class="value">184,320</tspan> ( <tspan class="addColor">212,450</tspan><tspan class="addColor">++</tspan>, <tspan class="delColor">28,130</tspan><tspan class="delColor">--</tspan> )'
    ]
    right_block = "\n".join(right_tspans)

    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{CARD_W}px" height="{CARD_H}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {key_color};}}
.value {{fill: {val_color};}}
.addColor {{fill: {add_color};}}
.delColor {{fill: {del_color};}}
.cc {{fill: {dot_color};}}
text, tspan {{white-space: pre;}}
{ascii_css}
</style>
<rect width="{CARD_W}px" height="{CARD_H}px" fill="{bg_color}" stroke="{border_color}" stroke-width="1.5" rx="15"/>
{ascii_block}
<text x="550" y="30" fill="{text_color}" transform="translate(0,{(CARD_H - 540) // 2})">
{right_block}
</text>
</svg>"""
    return svg


TYPING_LINES = ["Full Stack Developer", "Systems & Data Science", "GNN Researcher", "Building & Shipping"]


def build_typing_svg():
    """Self-hosted typing animation (SMIL), so the profile has no external dependency."""
    w, h, fs = 700, 60, 26
    cw = fs * 0.6                      # monospace advance
    n = len(TYPING_LINES)
    typing, hold, erase = 0.40 / n, 0.45 / n, 0.10 / n   # fractions of the whole cycle
    dur = 3.6 * n

    parts = []
    for i, line in enumerate(TYPING_LINES):
        tw = len(line) * cw
        x0 = (w - tw) / 2
        a = i / n
        t1, t2, t3 = a + typing, a + typing + hold, a + typing + hold + erase
        times = ([0.0] if a == 0 else [0.0, a]) + [t1, t2, t3, 1.0]
        widths = ([0] if a == 0 else [0, 0]) + [tw, tw, 0, 0]
        xs = ([x0] if a == 0 else [x0, x0]) + [x0 + tw, x0 + tw, x0, x0]
        fmt = lambda seq: ";".join(f"{v:.4f}".rstrip("0").rstrip(".") for v in seq)
        # cursor is visible from the slot start until the line has been erased
        ctimes = ([0.0, t3] if a == 0 else [0.0, a, t3])
        cvals = ([1, 0] if a == 0 else [0, 1, 0])
        parts.append(f"""  <clipPath id="clip{i}">
    <rect x="{x0:.1f}" y="0" width="0" height="{h}">
      <animate attributeName="width" dur="{dur}s" repeatCount="indefinite" keyTimes="{fmt(times)}" values="{fmt(widths)}"/>
    </rect>
  </clipPath>
  <text x="{x0:.1f}" y="{h / 2 + fs * 0.35:.1f}" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs" class="t" clip-path="url(#clip{i})">{html.escape(line)}</text>
  <rect y="{h / 2 - fs * 0.62:.1f}" width="3" height="{fs * 1.2:.1f}" rx="1" class="cur" opacity="0">
    <animate attributeName="x" dur="{dur}s" repeatCount="indefinite" keyTimes="{fmt(times)}" values="{fmt(xs)}"/>
    <animate attributeName="opacity" dur="{dur}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{fmt(ctimes)}" values="{fmt(cvals)}"/>
  </rect>""")

    body = "\n".join(parts)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(', '.join(TYPING_LINES))}">
  <title>{html.escape(' · '.join(TYPING_LINES))}</title>
  <style>
    text {{ font-family: 'Fira Code', Consolas, 'Cascadia Mono', Menlo, monospace; font-size: {fs}px; font-weight: 500; }}
    .t {{ fill: #0969da; }}
    .cur {{ fill: #8250df; }}
    @media (prefers-color-scheme: dark) {{ .t {{ fill: #22d3ee; }} .cur {{ fill: #a78bfa; }} }}
  </style>
{body}
</svg>"""


def render_preview(svg_name, png_name):
    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    if not os.path.exists(edge_path):
        return
    cwd = os.getcwd()
    svg_url = f'file:///{cwd}/assets/{svg_name}'.replace('\\', '/')
    out_png = f'--screenshot={cwd}\\assets\\{png_name}'
    profile = os.path.join(os.environ.get("TEMP", "."), "edge_preview_profile")
    cmd = [edge_path, '--headless', '--disable-gpu', f'--user-data-dir={profile}', out_png,
           '--window-size=1190,720', svg_url]
    subprocess.run(cmd, capture_output=True, text=True)
    print(f"assets/{png_name} generated!")


def main():
    os.makedirs("assets", exist_ok=True)

    for mode in ("dark",):  # one dark terminal card looks right on light and dark pages
        with open(f"assets/{mode}_mode.svg", "w", encoding="utf-8") as f:
            f.write(create_svg(mode))
        print(f"assets/{mode}_mode.svg created!")

    with open("assets/typing.svg", "w", encoding="utf-8") as f:
        f.write(build_typing_svg())
    print("assets/typing.svg created!")

    render_preview("dark_mode.svg", "preview.png")


if __name__ == "__main__":
    main()
