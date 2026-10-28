import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# -------------------------------------------------------------
# 1. Generate High-Density Phosphor Dot Matrix Portrait
# -------------------------------------------------------------
W, H = 280, 310
img = Image.new('L', (W, H), 0)
draw = ImageDraw.Draw(img)

# Background Radar / Cyber Circles
for r in [130, 95, 60]:
    draw.arc([140-r, 145-r, 140+r, 145+r], start=0, end=360, fill=45, width=1)
for angle in range(0, 360, 45):
    rad = np.radians(angle)
    x2, y2 = int(140 + 130 * np.cos(rad)), int(145 + 130 * np.sin(rad))
    draw.line([(140, 145), (x2, y2)], fill=30, width=1)

# Tech Hoodie & Shoulders
draw.polygon([(10, 310), (55, 230), (95, 200), (140, 195), (185, 200), (225, 230), (270, 310)], fill=175)
draw.polygon([(95, 200), (140, 250), (185, 200), (140, 195)], fill=95)
draw.polygon([(110, 200), (140, 235), (170, 200)], fill=35)
draw.line([(125, 220), (125, 270)], fill=230, width=2)
draw.line([(155, 220), (155, 270)], fill=230, width=2)
draw.line([(55, 230), (110, 310)], fill=210, width=1)
draw.line([(225, 230), (170, 310)], fill=210, width=1)

# Neck & Jawline
draw.polygon([(115, 160), (165, 160), (160, 205), (120, 205)], fill=135)
draw.polygon([(100, 100), (180, 100), (175, 145), (155, 175), (125, 175), (105, 145)], fill=195)

# Facial Shading & Glasses
draw.rounded_rectangle([(105, 112), (136, 130)], radius=4, outline=255, fill=45, width=3)
draw.rounded_rectangle([(144, 112), (175, 130)], radius=4, outline=255, fill=45, width=3)
draw.line([(136, 120), (144, 120)], fill=255, width=3)
draw.line([(110, 116), (122, 126)], fill=255, width=2)
draw.line([(149, 116), (161, 126)], fill=255, width=2)
# Nose & Mouth
draw.line([(140, 125), (138, 145), (143, 147)], fill=110, width=2)
draw.line([(130, 158), (150, 158)], fill=85, width=2)

# Over-Ear Headphones
draw.arc([(75, 50), (205, 150)], start=180, end=0, fill=220, width=8)
draw.arc([(80, 55), (200, 145)], start=180, end=0, fill=255, width=2)
draw.rounded_rectangle([(70, 105), (90, 155)], radius=7, outline=255, fill=110, width=3)
draw.ellipse([(75, 120), (85, 140)], fill=255)
draw.rounded_rectangle([(190, 105), (210, 155)], radius=7, outline=255, fill=110, width=3)
draw.ellipse([(195, 120), (205, 140)], fill=255)

# Detailed Anime / Messy Hair
hair_layers = [
    [(85, 105), (100, 65), (125, 55), (155, 55), (180, 65), (195, 105), (185, 90), (175, 75), (140, 70), (105, 75), (95, 90)],
    [(95, 80), (110, 45), (135, 50), (125, 70)],
    [(130, 40), (150, 43), (145, 65)],
    [(145, 45), (170, 47), (185, 80), (165, 70)],
    [(105, 75), (120, 107), (125, 85)],
    [(130, 75), (140, 110), (145, 85)],
    [(150, 75), (160, 107), (165, 85)]
]
for h in hair_layers:
    draw.polygon(h, fill=235)

# Circuit nodes
circuit_nodes = [(30, 65), (50, 35), (230, 40), (250, 75), (35, 255), (245, 250)]
for cx, cy in circuit_nodes:
    draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill=255)
draw.line([(30, 65), (60, 95)], fill=150, width=1)
draw.line([(250, 75), (220, 105)], fill=150, width=1)

img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
arr = np.array(img, dtype=float)

for y in range(H - 1):
    for x in range(1, W - 1):
        old_val = arr[y, x]
        new_val = 255 if old_val > 115 else 0
        arr[y, x] = new_val
        err = old_val - new_val
        arr[y, x + 1] += err * 7 / 16
        arr[y + 1, x - 1] += err * 3 / 16
        arr[y + 1, x] += err * 5 / 16
        arr[y + 1, x + 1] += err * 1 / 16

dithered = (arr > 128).astype(bool)

path_chunks = []
for y in range(H):
    in_run = False
    run_start = 0
    for x in range(W):
        if dithered[y, x]:
            if not in_run:
                in_run = True
                run_start = x
        else:
            if in_run:
                run_len = x - run_start
                path_chunks.append(f"M{run_start},{y}h{run_len}v1h-{run_len}z")
                in_run = False
    if in_run:
        run_len = W - run_start
        path_chunks.append(f"M{run_start},{y}h{run_len}v1h-{run_len}z")

full_path = "".join(path_chunks)

# -------------------------------------------------------------
# 2. Build assets/terminal.svg
# -------------------------------------------------------------
FONT = "Consolas, 'Cascadia Mono', Menlo, monospace"

# (key, value, value class) shown on the right-hand side of the banner
rows = [
    ("education", "B.Tech CSE (Data Science) '28 · SRMIST", "val"),
    ("stack", "TypeScript · Python · C++ · SQL", "val"),
    ("building", "React · FastAPI · PostgreSQL · Docker", "val"),
    ("research", "Graph Neural Networks (GNN)", "cyan"),
    ("status", "Building • Learning • Shipping", "purple"),
]

row_svg = []
for i, (key, value, cls) in enumerate(rows):
    y = 214 + i * 36
    row_svg.append(
        f'  <g class="row" style="animation-delay:{0.25 + i * 0.18:.2f}s">\n'
        f'    <text x="340" y="{y}" class="key">{key}</text>\n'
        f'    <text x="470" y="{y}" class="{cls}">{value}</text>\n'
        f'  </g>'
    )
rows_markup = "\n".join(row_svg)

terminal_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="380" viewBox="0 0 1000 380" role="img" aria-label="Debjit Das - full stack developer - animated profile banner">
  <title>Debjit (Ross) Das — profile.sh --live</title>
  <defs>
    <linearGradient id="pillGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#A78BFA"/>
      <stop offset="100%" stop-color="#22D3EE"/>
    </linearGradient>
    <linearGradient id="nameGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#A78BFA"/>
      <stop offset="100%" stop-color="#22D3EE"/>
    </linearGradient>
    <style>
      text {{ font-family: {FONT}; }}
      .term-title {{ font-size: 13px; fill: #8FA3C8; }}
      .section {{ font-size: 12px; letter-spacing: 3px; font-weight: bold; }}
      .name {{ font-size: 32px; font-weight: bold; fill: url(#nameGrad); }}
      .role {{ font-size: 17px; fill: #E2E8F0; }}
      .key {{ font-size: 15px; fill: #6B7C9E; }}
      .val {{ font-size: 15px; fill: #E2E8F0; }}
      .cyan {{ font-size: 15px; fill: #22D3EE; font-weight: bold; }}
      .purple {{ font-size: 15px; fill: #A78BFA; font-weight: bold; }}
      .prompt {{ font-size: 14px; fill: #44537A; }}
      .cursor-blink {{ fill: #22D3EE; animation: cursorBlink 1s infinite steps(2, start); }}
      .row {{ opacity: 0; animation: fadeIn 0.5s ease-out forwards; }}
      @keyframes cursorBlink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
      @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    </style>
  </defs>

  <!-- Terminal Window -->
  <rect x="8" y="8" width="984" height="34" rx="10" fill="#0C1322"/>
  <rect x="8" y="42" width="984" height="330" fill="#0A101F"/>
  <rect x="8" y="8" width="984" height="364" rx="10" fill="none" stroke="#223052" stroke-width="1.5"/>
  <rect x="8" y="42" width="984" height="1" fill="#1E2C4C"/>

  <!-- Window Controls -->
  <circle cx="24" cy="25" r="4.5" fill="#FF5F57"/>
  <circle cx="42" cy="25" r="4.5" fill="#FEBC2E"/>
  <circle cx="60" cy="25" r="4.5" fill="#28C840"/>

  <text x="500" y="28.5" text-anchor="middle" class="term-title">rosdebbu / README.md --live</text>

  <!-- Top-Right User Pill -->
  <rect x="835" y="14" width="145" height="22" rx="11" fill="url(#pillGrad)"/>
  <text x="907" y="29" text-anchor="middle" font-size="11" font-weight="bold" fill="#0A101F">@rosdebbu</text>

  <!-- Left: portrait -->
  <rect x="32" y="62" width="270" height="290" rx="6" fill="#0D1428" stroke="#A78BFA" stroke-opacity="0.35"/>
  <g transform="translate(41, 67) scale(0.9)" shape-rendering="crispEdges" fill="#A78BFA">
    <path d="{full_path}"/>
  </g>

  <!-- Right: identity -->
  <text x="340" y="82" class="section" fill="#22D3EE">SYSTEM.INFO</text>
  <text x="340" y="126" class="name">Debjit (Ross) Das</text>
  <text x="340" y="156" class="role">Full Stack Developer &amp; GNN Researcher</text>
  <rect x="340" y="176" width="620" height="1" fill="#1E2C4C"/>

{rows_markup}

  <text x="340" y="346" class="prompt">$ ./profile.sh --live <tspan class="cursor-blink">█</tspan></text>
</svg>"""

with open(r"assets\terminal.svg", "w", encoding="utf-8") as f:
    f.write(terminal_svg)

print("assets/terminal.svg successfully created!")
