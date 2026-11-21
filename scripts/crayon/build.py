import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from crayon import render

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(HERE, "html"), exist_ok=True)

INK = "#2b2622"
CREAM = "#fdf0d3"
TITLE = "#fbe3a8"
SKY = "#9fd3f2"
SEA = "#5fb3e4"
SAND = "#f0d18a"
PINK = "#f5b3ab"
YELLOW = "#f4cb4c"
GREEN = "#b9e0a5"
FONT = "/usr/share/fonts/truetype/google-fonts/ofl/comicrelief"

HEAD = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:CR;src:url(file://{FONT}/ComicRelief-Bold.ttf);font-weight:700}}
@font-face{{font-family:CR;src:url(file://{FONT}/ComicRelief-Regular.ttf);font-weight:400}}
html,body{{margin:0;background:transparent}}
body{{position:relative;overflow:hidden;font-family:CR;color:{INK}}}
svg{{position:absolute;left:0;top:0;overflow:visible}}
.box{{position:absolute;box-sizing:border-box}}
.chip{{display:inline-block;border:3px solid {INK};border-radius:999px;font-weight:700}}
.mode-fill *{{stroke:transparent!important}}
.mode-fill .txt,.mode-fill .ink{{color:transparent!important;fill:transparent!important}}
.mode-fill .chip{{border-color:transparent!important}}
.mode-ink svg *:not(.ink),.mode-text svg *:not(.ink){{fill:none!important}}
.mode-ink .chip,.mode-text .chip{{background:transparent!important}}
.mode-ink .txt{{color:transparent!important}}
.mode-text svg{{display:none}}
.mode-text .chip{{border-color:transparent!important}}
</style><script>document.documentElement.className='mode-'+new URLSearchParams(location.search).get('mode')</script></head>"""


def page(name, w, h, inner, seed=1, **kw):
    path = os.path.join(HERE, "html", name + ".html")
    with open(path, "w") as f:
        f.write(HEAD + f'<body style="width:{w}px;height:{h}px">' + inner + "</body></html>")
    out = os.path.join(OUT, name + ".png")
    render(path, w, h, out, seed=seed, **kw)
    print("wrote", out)


def wave(x0, x1, y, amp, period, phase=0.0):
    import math
    n = max(2, int(abs(x1 - x0) / 6) + 1)
    return [(x0 + (x1 - x0) * i / (n - 1),
             y + amp * math.sin(((x0 + (x1 - x0) * i / (n - 1)) / period) * 2 * math.pi + phase))
            for i in range(n)]


def poly(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def heart(x, y, s, color):
    return (f'<path transform="translate({x},{y}) scale({s})" d="M0,6 C-8,-4 -16,4 0,16 C16,4 8,-4 0,6 Z" '
            f'fill="{color}" stroke="{INK}" stroke-width="{2.4/s:.2f}" stroke-linejoin="round"/>')


def dash_burst(x, y, s=1.0):
    # the little yellow "pop" marks next to the title in the banner
    return "".join(
        f'<path d="M{x+dx*s},{y+dy*s} l{lx*s},{ly*s}" stroke="{INK}" stroke-width="{9*s}" stroke-linecap="round"/>'
        f'<path class="ink" d="M{x+dx*s},{y+dy*s} l{lx*s},{ly*s}" stroke="{YELLOW}" stroke-width="{5*s}" stroke-linecap="round" fill="none"/>'
        for dx, dy, lx, ly in [(0, 0, 4, -16), (14, 6, 12, -12), (24, 20, 16, -4)])


def sparkle(x, y, r, color):
    k = r * 0.28
    d = f"M{x},{y-r} Q{x+k},{y-k} {x+r},{y} Q{x+k},{y+k} {x},{y+r} Q{x-k},{y+k} {x-r},{y} Q{x-k},{y-k} {x},{y-r} Z"
    return f'<path d="{d}" fill="{color}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'


def shell(x, y, s, color=PINK):
    ribs = "".join(f'<path d="M0,10 L{dx},-6" stroke="{INK}" stroke-width="1.8" />' for dx in (-9, -3, 3, 9))
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M-14,8 Q-16,-14 0,-14 Q16,-14 14,8 Q0,14 -14,8 Z" '
            f'fill="{color}" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>{ribs}</g>')


def starfish(x, y, r):
    import math
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return f'<path d="{poly(pts)} Z" fill="#f6a96b" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>'


# ---------------------------------------------------------------- headers
def icon_code(cx, cy):
    return (f'<path d="M{cx-14},{cy-16} L{cx-30},{cy} L{cx-14},{cy+16} M{cx+14},{cy-16} L{cx+30},{cy} L{cx+14},{cy+16} '
            f'M{cx+6},{cy-20} L{cx-6},{cy+20}" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{cx}" cy="{cy}" r="27" fill="{SKY}" />')


def icon_ai(cx, cy):
    return sparkle(cx, cy, 26, PINK) + sparkle(cx + 22, cy - 18, 9, YELLOW)


def icon_stack(cx, cy):
    out = ""
    for i, c in enumerate([PINK, YELLOW, SKY]):
        yy = cy + 12 - i * 12
        out += (f'<path d="M{cx-26},{yy} L{cx},{yy-12} L{cx+26},{yy} L{cx},{yy+12} Z" fill="{c}" '
                f'stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    return out


def header(name, label, icon, pill_w, seed):
    W, H = 1400, 112
    x0 = 10 + pill_w
    top = wave(x0 + 4, 1395, 50, 6, 120)
    bot = wave(1395, x0 + 4, 84, 5, 150, 1.3)
    band = poly(top) + " L" + poly(bot)[1:] + " Z"
    foam = poly(wave(x0 + 20, 1200, 68, 3, 90, 0.6))
    deco = (dash_burst(x0 + 230, 30, 0.8) + heart(x0 + 520, 26, 1.0, PINK) + heart(x0 + 548, 16, 0.7, PINK)
            + sparkle(x0 + 820, 30, 10, YELLOW) + sparkle(x0 + 1080, 22, 7, SKY)
            + f'<circle cx="{x0+380}" cy="22" r="6" fill="#fff" stroke="{INK}" stroke-width="2.4"/>'
            + f'<circle cx="{x0+960}" cy="30" r="5" fill="#fff" stroke="{INK}" stroke-width="2.4"/>')
    svg = f'''<svg width="{W}" height="{H}">
<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{SEA}"/><stop offset=".65" stop-color="{SKY}"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/></linearGradient>
<linearGradient id="fadeInk" x1="0" x2="1"><stop offset="0" stop-color="{INK}"/><stop offset=".7" stop-color="{INK}" stop-opacity=".8"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></linearGradient></defs>
<path d="{band}" fill="url(#fade)"/>
<path d="{poly(top)}" fill="none" stroke="url(#fadeInk)" stroke-width="4" stroke-linecap="round"/>
<path class="ink" d="{foam}" fill="none" stroke="#ffffff" stroke-opacity=".9" stroke-width="3" stroke-linecap="round" stroke-dasharray="34 26"/>
<path d="{poly(bot)}" fill="none" stroke="url(#fadeInk)" stroke-width="3" stroke-linecap="round"/>
{deco}
<rect x="14" y="20" width="{pill_w}" height="80" rx="40" fill="#e9c67a"/>
<rect x="8" y="10" width="{pill_w}" height="80" rx="40" fill="{TITLE}" stroke="{INK}" stroke-width="5"/>
{icon(58, 50)}
</svg>
<div class="box txt" style="left:100px;top:16px;font-size:46px;font-weight:700;line-height:66px">{label}</div>'''
    page(name, W, H, svg, seed=seed)


# ---------------------------------------------------------------- cards
def card(name, title, tag, tag_color, desc, chips, seed, doodle=""):
    W, H = 680, 488
    clip = '<clipPath id="c"><rect x="14" y="14" width="652" height="460" rx="34"/></clipPath>'
    sea_top = wave(0, 690, 412, 7, 170, 0.4)
    sand_top = wave(0, 690, 446, 5, 210, 2.0)
    sea = poly(sea_top) + " L690,490 L0,490 Z"
    sand = poly(sand_top) + " L690,490 L0,490 Z"
    chips_html = "".join(
        f'<span class="chip txt" style="background:{SKY};padding:4px 18px;margin:0 10px 12px 0;font-size:22px">{c}</span>'
        for c in chips)
    svg = f'''<svg width="{W}" height="{H}"><defs>{clip}</defs>
<rect x="20" y="22" width="652" height="460" rx="34" fill="#e8c57c"/>
<rect x="14" y="14" width="652" height="460" rx="34" fill="{CREAM}"/>
<g clip-path="url(#c)">
<path d="{sea}" fill="{SEA}"/>
<path d="{poly(wave(0, 690, 428, 4, 120, 1.0))}" fill="none" stroke="#ffffff" class="ink" stroke-width="3" stroke-dasharray="30 26" stroke-linecap="round"/>
<path d="{sand}" fill="{SAND}"/>
<path d="{poly(sea_top)}" fill="none" stroke="{INK}" stroke-width="3.4"/>
<path d="{poly(sand_top)}" fill="none" stroke="{INK}" stroke-width="3"/>
{shell(560, 462, 0.9)}{shell(600, 466, 0.6, "#fbe0c0")}{starfish(90, 462, 13)}
</g>
<rect x="14" y="14" width="652" height="460" rx="34" fill="none" stroke="{INK}" stroke-width="5.5"/>
{doodle}
</svg>
<div class="box txt" style="left:46px;top:30px;font-size:50px;font-weight:700">{title}</div>
<div class="box" style="right:44px;top:44px"><span class="chip txt" style="background:{tag_color};padding:4px 18px;font-size:22px">{tag}</span></div>
<div class="box txt" style="left:48px;top:118px;width:590px;font-size:23px;line-height:1.55">{desc}</div>
<div class="box" style="left:48px;bottom:84px;width:600px;display:flex;flex-wrap:wrap">{chips_html}</div>'''
    page(name, W, H, svg, seed=seed)


# ---------------------------------------------------------------- stack sheet
def stack(seed):
    rows = [
        ("Languages", YELLOW, ["TypeScript", "JavaScript", "Python", "Go"]),
        ("Frontend", SKY, ["Next.js", "React", "Tailwind CSS"]),
        ("Backend & AI", PINK, ["NestJS", "FastAPI", "Prisma", "LangGraph"]),
        ("Data & infra", GREEN, ["PostgreSQL", "Redis", "RabbitMQ", "Docker"]),
    ]
    W, H = 1400, 470
    inner = ""
    for i, (lab, col, items) in enumerate(rows):
        y = 44 + i * 98
        chips = "".join(f'<span class="chip txt" style="background:{col};padding:6px 26px;margin-right:16px;font-size:30px">{t}</span>' for t in items)
        inner += (f'<div class="box txt" style="left:70px;top:{y+8}px;font-size:34px;font-weight:700">{lab}</div>'
                  f'<div class="box" style="left:360px;top:{y}px;white-space:nowrap">{chips}</div>')
    dots = "".join(f'<circle cx="52" cy="{44+i*98+34}" r="8" fill="{c}" stroke="{INK}" stroke-width="3"/>'
                   for i, c in enumerate([YELLOW, SKY, PINK, GREEN]))
    sep = "".join(f'<path d="{poly(wave(40, 1350, 44+i*98-6, 2.5, 160, i))}" fill="none" stroke="{INK}" stroke-opacity=".35" stroke-width="2.4" stroke-dasharray="14 12"/>' for i in (1, 2, 3))
    svg = f'''<svg width="{W}" height="{H}">
<rect x="18" y="16" width="1370" height="440" rx="36" fill="#e8c57c"/>
<rect x="10" y="8" width="1370" height="440" rx="36" fill="{CREAM}" stroke="{INK}" stroke-width="5.5"/>
{sep}{dots}{dash_burst(1290, 40, 0.9)}{shell(1330, 410, 1.0)}
</svg>''' + inner
    page("stack", W, H, svg, seed=seed)


# ---------------------------------------------------------------- buttons
def button(name, label, icon_svg, seed):
    W, H = 600, 128
    svg = f'''<svg width="{W}" height="{H}">
<rect x="16" y="20" width="572" height="98" rx="49" fill="#e8c57c"/>
<rect x="8" y="8" width="572" height="98" rx="49" fill="{TITLE}" stroke="{INK}" stroke-width="5.5"/>
{icon_svg}</svg>
<div class="box txt" style="left:130px;top:24px;font-size:38px;font-weight:700;line-height:64px">{label}</div>'''
    page(name, W, H, svg, seed=seed)


FB = (f'<circle cx="84" cy="57" r="30" fill="#4b8fe2" stroke="{INK}" stroke-width="4.5"/>'
      f'<text class="ink" x="84" y="74" text-anchor="middle" font-family="CR" font-weight="700" font-size="46" fill="#fff">f</text>')
LI = (f'<rect x="54" y="27" width="60" height="60" rx="14" fill="#3f7fc4" stroke="{INK}" stroke-width="4.5"/>'
      f'<text class="ink" x="84" y="72" text-anchor="middle" font-family="CR" font-weight="700" font-size="36" fill="#fff">in</text>')

if __name__ == "__main__":
    which = sys.argv[2:] or ["headers", "cards", "stack", "buttons"]
    if "headers" in which:
        header("h-software", "Software", icon_code, 336, 11)
        header("h-ai", "AI", icon_ai, 192, 12)
        header("h-stack", "Stack", icon_stack, 262, 13)
    if "cards" in which:
        card("card-fiurozz", "Fiurozz", "Web platform", SKY,
             "A portfolio and project showcase platform that tells the story behind the code: architecture, technical decisions and engineering process.",
             ["Next.js", "NestJS", "Go", "RabbitMQ", "PostgreSQL"], 21)
        card("card-finsights", "Finsights", "Finance web", SKY,
             "A Vietnamese finance website with a stock market board, company news, a watchlist and an AI chatbot. I build the frontend and chatbot UI.",
             ["Next.js", "React", "TypeScript"], 22)
        card("card-boa", "BOA", "Multi-agent", SKY,
             "A multi-agent system for phone retail operations. A coordinator plans the work, specialist agents carry it out, and a person approves every action.",
             ["Go", "Python", "LangGraph", "FastAPI", "Next.js"], 23)
        card("card-catronaut", "Catronaut", "In planning", PINK,
             "An agent harness that will turn a request like \"build an e-commerce site\" into a Next.js project running live in the browser.",
             ["Python", "FastAPI", "MCP", "vLLM"], 24)
    if "stack" in which:
        stack(31)
    if "buttons" in which:
        button("btn-facebook", "Connect on Facebook", FB, 41)
        button("btn-linkedin", "Connect on LinkedIn", LI, 42)
