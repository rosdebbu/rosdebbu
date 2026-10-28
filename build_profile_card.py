import os
import html
import subprocess

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
    
    # 25 lines of Debjit's custom ASCII portrait
    ascii_lines = [
        "           g@M%@%%@N%Nw,,                   ",
        "        ,M*|`||*%gNM=]mM%g||%N,             ",
        "       p!``  '! |''` '''|||jhlj%w           ",
        "     ,@L `    ,,        ''!`|j%M]%M         ",
        "    ]j'` .,wp@pw,    `.     ''''|%Wg        ",
        "  /{||]@@@@@@@@@pp.             |||||       ",
        " '` ']@@@@@@@@@@@@@@p     , ,'''` `         ",
        "  , :]%%@@@@@%%%%%%k%h '*||mkr   *|%h       ",
        "  '  j%M` (@@)   (@@)  ~nrn=|i  j%%k%       ",
        "   !  jrr*^`   ..        `\"!  L'k%%%%,      ",
        "    j  lp;,.   /\\      ,;\\nmy \" j%%k%%      ",
        "   i r @@@@   w==w   `^****M*,p j%%%%%      ",
        "   | ]@@@@H  {====}  ,jmgpmb% [__]%%%H      ",
        "    ;;%%%%%k%@[\\__/.;j%%k|%k%%',[  ]%%%     ",
        "     H|%%k%%%j%k||,;;j;!!'|%ij}===@%%H      ",
        "     \"djjmkL,\"]][,,,,wwxw;|#kjk` %%%%M      ",
        "       %;%km%%%%M%M|%%jkkii|||[   %%%%      ",
        "        kjj%%kkkl|!||||||j|||\"    %%%%      ",
        "         |jm%H@@@b%%kkmk%i|!,[   '%%kH      ",
        "         @p|j%%%%jkk|||j*'`;j[    |k%h      ",
        "        ]@@@g|'''`'''  ` ,;j%k              ",
        "        @@@@ [KEEP YOUR] ;jj%%k%            ",
        "       @@@@@@@@%%kgki!|jjjj%k%@ .           ",
        ". ^['' %@@@@HH%b%k{illljkjj%%%% ; `,.       ",
        "=[' ` . %HH%%%%%H@gkilljjj%kk%\".   `'i      "
    ]
    
    # ASCII text elements
    ascii_tspans = []
    for i, line in enumerate(ascii_lines):
        y = 30 + i * 20
        safe_line = html.escape(line)
        ascii_tspans.append(f'<tspan x="15" y="{y}">{safe_line}</tspan>')
    ascii_block = "\n".join(ascii_tspans)
    
    def build_kv(y, key, val, target_cols=58):
        # Target total columns on right side = target_cols
        # Structure: ". " (2) + key + ": " (2) + dots + val
        # len = 2 + len(key) + 2 + len(dots) + len(val)
        used = 2 + len(key) + 2 + len(val)
        dot_count = max(3, target_cols - used)
        dots = " " + ("." * (dot_count - 2)) + " "
        safe_key = html.escape(key)
        safe_val = html.escape(val)
        return (f'<tspan x="390" y="{y}" class="cc">. </tspan>'
                f'<tspan class="key">{safe_key}</tspan>:'
                f'<tspan class="cc">{dots}</tspan>'
                f'<tspan class="value">{safe_val}</tspan>')

    def build_header(y, title, char="-", target_cols=58):
        rem = target_cols - len(title) - 1
        dashes = " " + (char * max(4, rem))
        safe_title = html.escape(title)
        return f'<tspan x="390" y="{y}">{safe_title}</tspan><tspan class="cc">{dashes}</tspan>'

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
        '<tspan x="390" y="150" class="cc">. </tspan>',
        # 7 (y=170)
        build_kv(170, "Languages.Programming", "TypeScript, Python, C++, Bash"),
        # 8 (y=190)
        build_kv(190, "Languages.Computer", "HTML5, CSS3, SQL, JSON, LaTeX"),
        # 9 (y=210)
        build_kv(210, "Languages.Real", "English, Bengali, Hindi"),
        # 10 (y=230)
        '<tspan x="390" y="230" class="cc">. </tspan>',
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
        build_kv(390, "Portfolio", "vib3withsimran"),
        # 19 (y=410)
        build_kv(410, "GitHub", "rosdebbu"),
        # 20 (y=430)
        '<tspan x="390" y="430" class="cc">. </tspan>',
        # 21 (y=450)
        build_header(450, "- GitHub Stats", "-"),
        # 22 (y=470)
        f'<tspan x="390" y="470" class="cc">. </tspan><tspan class="key">Repos</tspan>:<tspan class="cc"> .... </tspan><tspan class="value">48</tspan> {{<tspan class="key">Contributed</tspan>: <tspan class="value">56</tspan>}} | <tspan class="key">Stars</tspan>:<tspan class="cc"> ........... </tspan><tspan class="value">5</tspan>',
        # 23 (y=490)
        f'<tspan x="390" y="490" class="cc">. </tspan><tspan class="key">Commits</tspan>:<tspan class="cc"> ................. </tspan><tspan class="value">680+</tspan> | <tspan class="key">Followers</tspan>:<tspan class="cc"> ....... </tspan><tspan class="value">9</tspan>',
        # 24 (y=510)
        f'<tspan x="390" y="510" class="cc">. </tspan><tspan class="key">Lines of Code on GitHub</tspan>:<tspan class="cc">. </tspan><tspan class="value">184,320</tspan> ( <tspan class="addColor">212,450</tspan><tspan class="addColor">++</tspan>, <tspan class="delColor">28,130</tspan><tspan class="delColor">--</tspan> )'
    ]
    right_block = "\n".join(right_tspans)
    
    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="530px" font-size="16px">
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
</style>
<rect width="985px" height="530px" fill="{bg_color}" stroke="{border_color}" stroke-width="1.5" rx="15"/>
<text x="15" y="30" fill="{text_color}" class="ascii">
{ascii_block}
</text>
<text x="390" y="30" fill="{text_color}">
{right_block}
</text>
</svg>"""
    return svg

def main():
    os.makedirs("assets", exist_ok=True)
    
    dark_svg = create_svg("dark")
    with open("assets/dark_mode.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print("assets/dark_mode.svg created!")
    
    light_svg = create_svg("light")
    with open("assets/light_mode.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    print("assets/light_mode.svg created!")

    # Render preview image
    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    if os.path.exists(edge_path):
        cwd = os.getcwd()
        svg_url = f'file:///{cwd}/assets/dark_mode.svg'.replace('\\', '/')
        out_png = f'--screenshot={cwd}\\assets\\preview.png'
        cmd = [edge_path, '--headless', '--disable-gpu', out_png, '--window-size=1020,580', svg_url]
        subprocess.run(cmd, capture_output=True, text=True)
        print("assets/preview.png generated!")

if __name__ == "__main__":
    main()
