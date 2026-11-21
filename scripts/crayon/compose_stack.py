"""Stack sheet: crayon-drawn card + labels, with hand-drawn badge images pasted on top.
Badges are transparent PNGs in scripts/crayon/badges/<name>.png (cropped to content)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out")
sys.argv = [sys.argv[0], OUT]
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image
import build, crayon
from build import HEAD, INK, CREAM, YELLOW, SKY, PINK, GREEN, poly, wave, dash_burst, shell

ROWS = [
    ("Languages", ["typescript", "javascript", "python", "go"]),
    ("Frontend", ["nextjs", "react", "tailwind"]),
    ("Backend & AI", ["nestjs", "fastapi", "prisma", "langchain", "langgraph"]),
    ("Data & infra", ["postgresql", "redis", "rabbitmq", "docker"]),
]
W, H, S = 1400, 470, 2
CY = [78 + i * 98 for i in range(4)]
BX, BH, GAP = 318, 54, 12


def background(seed=31):
    labels = "".join(
        f'<div class="box txt" style="left:70px;top:{cy-26}px;font-size:31px;font-weight:700;line-height:52px;white-space:nowrap">{lab}</div>'
        for (lab, _), cy in zip(ROWS, CY))
    dots = "".join(f'<circle cx="46" cy="{cy}" r="8" fill="{c}" stroke="{INK}" stroke-width="3"/>'
                   for cy, c in zip(CY, [YELLOW, SKY, PINK, GREEN]))
    sep = "".join(f'<path d="{poly(wave(40, 1350, cy+49, 2.5, 160, i))}" fill="none" stroke="{INK}" stroke-opacity=".35" stroke-width="2.4" stroke-dasharray="14 12"/>'
                  for i, cy in enumerate(CY[:3]))
    svg = f'''<svg width="{W}" height="{H}">
<rect x="18" y="16" width="1370" height="440" rx="36" fill="#e8c57c"/>
<rect x="10" y="8" width="1370" height="440" rx="36" fill="{CREAM}" stroke="{INK}" stroke-width="5.5"/>
{sep}{dots}{dash_burst(1300, 34, 0.9)}{shell(1332, 412, 1.0)}</svg>{labels}'''
    path = os.path.join(HERE, "html", "stack-bg.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(HEAD + f'<body style="width:{W}px;height:{H}px">' + svg + "</body></html>")
    layers = [crayon.shoot(path, W, H, m, f"/tmp/stackbg.{m}.png") for m in ("fill", "ink", "text")]
    img = crayon.crayonify(*layers, seed=seed)
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGBA")


def main():
    bg = background()
    for (lab, names), cy in zip(ROWS, CY):
        x = BX
        for n in names:
            b = Image.open(os.path.join(HERE, "badges", n + ".png")).convert("RGBA")
            h = BH * S; w = round(h * b.width / b.height)
            b = b.resize((w, h), Image.LANCZOS)
            bg.alpha_composite(b, (x * S, cy * S - h // 2))
            x += w // S + GAP
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "stack.png")
    bg.quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG).save(out, optimize=True)
    print("wrote", out, bg.size, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main()
