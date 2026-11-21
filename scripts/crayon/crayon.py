"""Render an HTML/SVG drawing in two layers (fill + ink) with headless Chrome,
then give it a hand-drawn crayon look with numpy: wobbly edges, diagonal wax
streaks in the fills, broken grainy outlines."""
import subprocess, sys, os, numpy as np
from PIL import Image
from scipy import ndimage as ndi

CHROME = "/usr/bin/google-chrome"
SCALE = 2


def shoot(html_path, w, h, mode, out):
    url = f"file://{html_path}?mode={mode}"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--force-device-scale-factor={SCALE}", f"--window-size={w},{h}",
                    "--default-background-color=00000000", "--virtual-time-budget=1500",
                    f"--screenshot={out}", url], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return np.asarray(Image.open(out).convert("RGBA")).astype(np.float32) / 255.0


def smooth_noise(shape, sigma, rng):
    n = ndi.gaussian_filter(rng.standard_normal(shape), sigma)
    return n / (n.std() + 1e-6)


def streaks(shape, rng, angle=-28, along=14, across=0.7):
    big = int(max(shape) * 1.5)
    n = rng.standard_normal((big, big))
    n = ndi.gaussian_filter(n, (across, along))
    n = ndi.rotate(n, angle, reshape=False, order=1)
    y0, x0 = (big - shape[0]) // 2, (big - shape[1]) // 2
    n = n[y0:y0 + shape[0], x0:x0 + shape[1]]
    return n / (n.std() + 1e-6)


def displace(img, dx, dy):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    coords = [yy + dy, xx + dx]
    return np.stack([ndi.map_coordinates(img[..., c], coords, order=1, mode="nearest")
                     for c in range(img.shape[2])], -1)


PAPER = np.array([1.0, 0.985, 0.95], np.float32)


def crayonify(fill, ink, text, seed=1, wobble=3.2, ink_wobble=1.6):
    rng = np.random.default_rng(seed)
    shape = fill.shape[:2]
    # shared low-frequency wobble, ink gets its own extra offset
    dx = smooth_noise(shape, 22, rng) * wobble
    dy = smooth_noise(shape, 22, rng) * wobble
    fill = displace(fill, dx, dy)
    ink = displace(ink, dx + smooth_noise(shape, 14, rng) * ink_wobble,
                   dy + smooth_noise(shape, 14, rng) * ink_wobble)
    text = displace(text, dx * 0.35 + smooth_noise(shape, 30, rng) * 0.8,
                    dy * 0.35 + smooth_noise(shape, 30, rng) * 0.8)

    # fills: diagonal wax streaks + paper tooth showing through
    s = streaks(shape, rng)
    tooth = smooth_noise(shape, 0.8, rng)
    a = np.clip(0.72 + 0.26 * s + 0.08 * tooth + 0.05 * smooth_noise(shape, 40, rng), 0.3, 1.0)
    a = np.where(tooth > 2.2, a * 0.45, a)             # little paper flecks
    # crayon laid over paper: colour mixes toward paper where the wax is thin
    fill_rgb = PAPER * (1 - a[..., None]) + fill[..., :3] * a[..., None]
    fill_a = fill[..., 3]

    # ink: grainy, slightly broken wax line
    g = smooth_noise(shape, 0.7, rng)
    s2 = streaks(shape, rng, angle=35, along=5, across=0.6)
    ia = np.clip(0.86 + 0.14 * g + 0.10 * s2, 0.35, 1.0)
    ink_a = ink[..., 3] * ia
    ink_rgb = ink[..., :3]
    ta = text[..., 3] * np.clip(0.92 + 0.10 * g, 0.6, 1.0)
    ink_rgb = (text[..., :3] * ta[..., None] + ink_rgb * (ink_a * (1 - ta))[..., None]) / np.maximum(ta + ink_a * (1 - ta), 1e-6)[..., None]
    ink_a = ta + ink_a * (1 - ta)

    out_a = ink_a + fill_a * (1 - ink_a)
    out_rgb = (ink_rgb * ink_a[..., None] + fill_rgb * (fill_a * (1 - ink_a))[..., None]) / np.maximum(out_a, 1e-6)[..., None]
    out = np.dstack([out_rgb, out_a])
    return out


def render(html_path, w, h, out_png, seed=1, **kw):
    tmp = "/tmp/crayon_" + os.path.basename(out_png)
    fill = shoot(html_path, w, h, "fill", tmp + ".fill.png")
    ink = shoot(html_path, w, h, "ink", tmp + ".ink.png")
    text = shoot(html_path, w, h, "text", tmp + ".text.png")
    img = crayonify(fill, ink, text, seed=seed, **kw)
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGBA")
    im = im.resize((w, h), Image.LANCZOS)
    im.save(out_png, optimize=True)
    return out_png


if __name__ == "__main__":
    render(os.path.abspath(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
