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
terminal_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" role="img" aria-label="Debjit Das - full stack developer - animated profile banner">
  <title>Debjit (Ross) Das — profile.sh --live</title>
  <defs>
    <linearGradient id="pillGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#A78BFA"/>
      <stop offset="100%" stop-color="#22D3EE"/>
    </linearGradient>
    <style>
      .term-title {{ font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 13px; fill: #8FA3C8; }}
      .term-section {{ font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 12px; letter-spacing: 3px; font-weight: bold; }}
      .code-key {{ font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 12px; fill: #6B7C9E; }}
      .code-dots {{ font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 12px; fill: #223052; }}
      .code-val {{ font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 12px; fill: #E2E8F0; }}
      .code-val-cyan {{ font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 12px; fill: #22D3EE; font-weight: bold; }}
      .code-val-purple {{ font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 12px; fill: #A78BFA; font-weight: bold; }}
      .prompt-line {{ font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 12.5px; fill: #44537A; }}
      .cursor-blink {{ fill: #22D3EE; animation: cursorBlink 1s infinite steps(2, start); }}
      @keyframes cursorBlink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
    </style>
  </defs>

  <!-- Terminal Window -->
  <rect x="8" y="8" width="1164" height="34" rx="10" fill="#0C1322"/>
  <rect x="8" y="42" width="1164" height="560" fill="#0A101F"/>
  <rect x="8" y="8" width="1164" height="594" rx="10" fill="none" stroke="#223052" stroke-width="1.5"/>
  <rect x="8" y="42" width="1164" height="1" fill="#1E2C4C"/>

  <!-- Window Controls -->
  <circle cx="24" cy="25" r="4.5" fill="#FF5F57"/>
  <circle cx="42" cy="25" r="4.5" fill="#FEBC2E"/>
  <circle cx="60" cy="25" r="4.5" fill="#28C840"/>

  <!-- Window Title -->
  <text x="590" y="28.5" text-anchor="middle" class="term-title">rosdebbu / README.md --live</text>

  <!-- Top-Right User Pill -->
  <rect x="1010" y="14" width="145" height="22" rx="11" fill="url(#pillGrad)"/>
  <text x="1082" y="29" text-anchor="middle" font-family="Consolas, monospace" font-size="11" font-weight="bold" fill="#0A101F">@rosdebbu</text>

  <!-- Left: VISUAL.MAP -->
  <text x="40" y="68" class="term-section" fill="#A78BFA">VISUAL.MAP</text>
  <rect x="40" y="80" width="450" height="490" rx="6" fill="#0D1428" stroke="#A78BFA" stroke-opacity="0.35"/>
  <g transform="translate(55, 95) scale(1.5)" shape-rendering="crispEdges" fill="#A78BFA">
    <path d="{full_path}"/>
  </g>

  <!-- Right: SYSTEM.INFO -->
  <text x="525" y="68" class="term-section" fill="#22D3EE">SYSTEM.INFO</text>

  <g transform="translate(525, 105)">
    <!-- Row 1 -->
    <text y="0">
      <tspan class="code-key">Subject</tspan>
      <tspan class="code-dots"> ................... </tspan>
      <tspan class="code-val-purple">Debjit (Ross) Das</tspan>
    </text>

    <!-- Row 2 -->
    <text y="26">
      <tspan class="code-key">Role</tspan>
      <tspan class="code-dots"> ...................... </tspan>
      <tspan class="code-val">Full Stack Developer &amp; Systems</tspan>
    </text>

    <!-- Row 3 -->
    <text y="52">
      <tspan class="code-key">Origin</tspan>
      <tspan class="code-dots"> .................... </tspan>
      <tspan class="code-val">SRMIST, India</tspan>
    </text>

    <!-- Row 4 -->
    <text y="78">
      <tspan class="code-key">Education</tspan>
      <tspan class="code-dots"> ................. </tspan>
      <tspan class="code-val">B.Tech CSE (Data Science) '28</tspan>
    </text>

    <!-- Row 5 -->
    <text y="104">
      <tspan class="code-key">Status</tspan>
      <tspan class="code-dots"> .................... </tspan>
      <tspan class="code-val-cyan">Building • Learning • Shipping</tspan>
    </text>

    <!-- Row 6 -->
    <text y="130">
      <tspan class="code-key">Toolchain</tspan>
      <tspan class="code-dots"> ................. </tspan>
      <tspan class="code-val">TypeScript • Python • C++ • Docker • Linux</tspan>
    </text>

    <!-- Row 7 -->
    <text y="156">
      <tspan class="code-key">Core.Lang</tspan>
      <tspan class="code-dots"> ................. </tspan>
      <tspan class="code-val">TypeScript • Python • C/C++ • SQL • Bash</tspan>
    </text>

    <!-- Row 8 -->
    <text y="182">
      <tspan class="code-key">Core.Frontend</tspan>
      <tspan class="code-dots"> ............. </tspan>
      <tspan class="code-val">React 19 • Next.js 14 • Tailwind CSS • Vite</tspan>
    </text>

    <!-- Row 9 -->
    <text y="208">
      <tspan class="code-key">Core.Backend</tspan>
      <tspan class="code-dots"> .............. </tspan>
      <tspan class="code-val">FastAPI • Node.js • Express • WebSockets</tspan>
    </text>

    <!-- Row 10 -->
    <text y="234">
      <tspan class="code-key">Core.Database</tspan>
      <tspan class="code-dots"> ............. </tspan>
      <tspan class="code-val">PostgreSQL (Neon) • MySQL • Prisma ORM</tspan>
    </text>

    <!-- Row 11 -->
    <text y="260">
      <tspan class="code-key">Core.AI/ML</tspan>
      <tspan class="code-dots"> ................ </tspan>
      <tspan class="code-val-cyan">PyTorch • Graph Neural Networks (GNN)</tspan>
    </text>

    <!-- Row 12 -->
    <text y="286">
      <tspan class="code-key">Core.Infra</tspan>
      <tspan class="code-dots"> ................ </tspan>
      <tspan class="code-val">Docker • WSL2 • Linux • Vercel • Render</tspan>
    </text>

    <!-- Row 13 -->
    <text y="322">
      <tspan class="code-key">Grid.Mail</tspan>
      <tspan class="code-dots"> ................. </tspan>
      <tspan class="code-val">debjitsince90908@gmail.com</tspan>
    </text>

    <!-- Row 14 -->
    <text y="348">
      <tspan class="code-key">Grid.Portfolio</tspan>
      <tspan class="code-dots"> ............ </tspan>
      <tspan class="code-val-cyan">debjitttt-ross.vercel.app</tspan>
    </text>

    <!-- Row 15 -->
    <text y="374">
      <tspan class="code-key">Grid.LinkedIn</tspan>
      <tspan class="code-dots"> ............. </tspan>
      <tspan class="code-val">linkedin.com/in/debjit-das-6b0452327</tspan>
    </text>

    <!-- Row 16 -->
    <text y="400">
      <tspan class="code-key">Grid.GitHub</tspan>
      <tspan class="code-dots"> ............... </tspan>
      <tspan class="code-val-purple">github.com/rosdebbu</tspan>
    </text>

    <!-- Bottom Prompt Line -->
    <text y="445" class="prompt-line">
      $ ./profile.sh --live <tspan class="cursor-blink">█</tspan>
    </text>
  </g>
</svg>"""

with open(r"assets\terminal.svg", "w", encoding="utf-8") as f:
    f.write(terminal_svg)

print("assets/terminal.svg successfully created!")

# -------------------------------------------------------------
# 3. Build assets/connect.svg
# -------------------------------------------------------------
connect_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="260" viewBox="0 0 1000 260" role="img" aria-label="connect.sh --links">
  <title>connect.sh --links</title>
  <defs>
    <style>
      .hdr-title { font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 13px; fill: #8FA3C8; }
      .prompt { font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 13px; fill: #44537A; }
      .link-label { font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 12px; fill: #6B7C9E; }
      .link-val { font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 13px; fill: #22D3EE; font-weight: bold; }
      .link-val-purple { font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 13px; fill: #A78BFA; font-weight: bold; }
      .link-desc { font-family: Consolas, 'Cascadia Mono', Menlo, monospace; font-size: 11px; fill: #8FA3C8; }
    </style>
  </defs>

  <rect x="8" y="8" width="984" height="34" rx="10" fill="#0C1322"/>
  <rect x="8" y="42" width="984" height="210" fill="#0A101F"/>
  <rect x="8" y="8" width="984" height="244" rx="10" fill="none" stroke="#223052" stroke-width="1.5"/>
  <rect x="8" y="42" width="984" height="1" fill="#1E2C4C"/>

  <circle cx="24" cy="25" r="4.5" fill="#FF5F57"/>
  <circle cx="42" cy="25" r="4.5" fill="#FEBC2E"/>
  <circle cx="60" cy="25" r="4.5" fill="#28C840"/>

  <text x="500" y="28.5" text-anchor="middle" class="hdr-title">connect.sh --links</text>

  <text x="40" y="72" class="prompt">$ ./connect.sh --links</text>

  <!-- 4 Clickable/Connect Cards -->
  <!-- 1. Portfolio -->
  <g transform="translate(40, 95)">
    <rect width="210" height="120" rx="8" fill="#0D1428" stroke="#223052" stroke-width="1"/>
    <text x="18" y="32" class="link-label">// 01. WEB</text>
    <text x="18" y="60" class="link-val-purple">Portfolio ↗</text>
    <text x="18" y="85" class="link-desc">debjitttt-ross.vercel.app</text>
  </g>

  <!-- 2. LinkedIn -->
  <g transform="translate(275, 95)">
    <rect width="210" height="120" rx="8" fill="#0D1428" stroke="#223052" stroke-width="1"/>
    <text x="18" y="32" class="link-label">// 02. NETWORK</text>
    <text x="18" y="60" class="link-val">LinkedIn ↗</text>
    <text x="18" y="85" class="link-desc">in/debjit-das-6b0452327</text>
  </g>

  <!-- 3. LeetCode -->
  <g transform="translate(510, 95)">
    <rect width="210" height="120" rx="8" fill="#0D1428" stroke="#223052" stroke-width="1"/>
    <text x="18" y="32" class="link-label">// 03. CODE</text>
    <text x="18" y="60" class="link-val-purple">LeetCode ↗</text>
    <text x="18" y="85" class="link-desc">u/debbjitttt</text>
  </g>

  <!-- 4. Email -->
  <g transform="translate(745, 95)">
    <rect width="215" height="120" rx="8" fill="#0D1428" stroke="#223052" stroke-width="1"/>
    <text x="18" y="32" class="link-label">// 04. MAIL</text>
    <text x="18" y="60" class="link-val">Email ↗</text>
    <text x="18" y="85" class="link-desc">debjitsince90908@gmail</text>
  </g>
</svg>"""

with open(r"assets\connect.svg", "w", encoding="utf-8") as f:
    f.write(connect_svg)

print("assets/connect.svg successfully created!")
