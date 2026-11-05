// Fizz koi pond. Every moving thing is periodic in t in [0,1), so the GIF loops with no visible seam.
const W = 960, H = 320, SS = 2, TAU = Math.PI * 2;
const out = document.getElementById('out'); out.width = W; out.height = H;
const octx = out.getContext('2d');
const stage = document.createElement('canvas'); stage.width = W * SS; stage.height = H * SS;
const c = stage.getContext('2d');
const layer = () => { const k = document.createElement('canvas'); k.width = W * SS; k.height = H * SS; const x = k.getContext('2d'); x.scale(SS, SS); return [k, x]; };
c.scale(SS, SS);

function rng(seed) { return () => (seed = (seed * 16807) % 2147483647) / 2147483647; }

// Closed swim path, sampled by arc length so a fish never speeds up or stalls.
function makePath(fn, n = 3000) {
  const pts = [], cum = [0]; let len = 0;
  for (let i = 0; i <= n; i++) { const p = fn(i / n); pts.push(p); if (i) { len += Math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1]); cum.push(len); } }
  return { len, at(f) {
    f = ((f % 1) + 1) % 1; const d = f * len; let a = 0, b = n;
    while (b - a > 1) { const m = (a + b) >> 1; if (cum[m] <= d) a = m; else b = m; }
    const r = (d - cum[a]) / Math.max(1e-6, cum[b] - cum[a]);
    return [pts[a][0] + (pts[b][0] - pts[a][0]) * r, pts[a][1] + (pts[b][1] - pts[a][1]) * r];
  } };
}

const INK = '#16181f', CREAM = '#f6ecd9', RED = '#e2451f', DEEP = '#b92c12', GOLD = '#efb23c', AMBER = '#d98a1f', WHITE = '#fbf4e6';

const fish = [
  { name: 'kohaku', len: 150, wide: .135, laps: 1, beats: 13, base: WHITE, edge: '#c9b79c', fin: '#fff3e0',
    path: makePath(u => [480 + 415 * Math.sin(TAU * u), 160 - 124 * Math.cos(TAU * u) + 10 * Math.sin(TAU * 3 * u)]),
    patches: [[.085, .1, .062, .72, RED], [.27, .42, .1, .62, RED], [.34, -.38, .06, .42, RED], [.5, -.3, .1, .72, RED], [.57, .55, .035, .4, RED], [.76, .1, .07, 1, DEEP]] },
  { name: 'ogon', len: 128, wide: .13, laps: 1, beats: 15, offset: .37, base: GOLD, edge: '#a86a12', fin: '#ffd884',
    path: makePath(u => [480 - 405 * Math.sin(TAU * u), 165 + 112 * Math.sin(TAU * 2 * u + .5)]),
    patches: [[.25, 0, .22, .35, '#ffd777'], [.55, 0, .2, .3, '#ffd777'], [.05, 0, .05, .5, '#ffe3a0']] },
  { name: 'tancho', len: 92, wide: .135, laps: 2, beats: 22, offset: .15, base: WHITE, edge: '#c8bcaa', fin: '#fff6ea',
    path: makePath(u => [812 + 104 * Math.cos(TAU * u), 94 + 56 * Math.sin(TAU * u)]),
    patches: [[.09, 0, .045, .62, RED]] },
  { name: 'showa', len: 106, wide: .135, laps: 2, beats: 20, offset: .62, base: INK, edge: '#050608', fin: '#3c3f49',
    path: makePath(u => [150 + 112 * Math.cos(-TAU * u), 226 + 62 * Math.sin(-TAU * u)]),
    patches: [[.1, .1, .07, .85, RED], [.36, -.3, .09, .7, RED], [.5, .45, .05, .5, CREAM], [.66, -.1, .07, .8, RED]] },
  { name: 'sanke', len: 78, wide: .135, laps: 2, beats: 24, offset: .8, base: '#f5efe2', edge: '#c7b9a2', fin: '#fff6ea',
    path: makePath(u => [650 + 150 * Math.cos(-TAU * u), 268 + 30 * Math.sin(-TAU * u)]),
    patches: [[.14, -.15, .07, .7, '#ee6a2c'], [.42, .2, .1, .8, '#ee6a2c'], [.3, -.4, .025, .28, INK], [.58, -.2, .03, .3, INK], [.7, .25, .025, .3, INK]] },
];

const halfWidth = s => {
  // Blunt rounded head, widest behind the gills, long taper into the tail.
  if (s < .17) return Math.sqrt(1 - Math.pow(1 - s / .17, 2)) * .92;
  if (s < .34) return .92 + .08 * Math.sin((s - .17) / .17 * Math.PI / 2);
  return Math.max(.09, Math.pow(1 - (s - .34) / .66, 1.15));
};

function spineOf(f, t) {
  const pts = [], n = 30, head = f.laps * t + (f.offset || 0);
  for (let i = 0; i <= n; i++) {
    const s = i / n;
    const p = f.path.at(head - s * f.len / f.path.len);
    pts.push({ s, x: p[0], y: p[1] });
  }
  for (let i = 0; i <= n; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n, i + 1)];
    const dx = a.x - b.x, dy = a.y - b.y, d = Math.hypot(dx, dy) || 1;
    pts[i].tx = dx / d; pts[i].ty = dy / d; pts[i].nx = -dy / d; pts[i].ny = dx / d;
  }
  // Swim wave: grows toward the tail and is whole-number periodic across the loop.
  for (const p of pts) {
    const amp = f.len * .085 * Math.pow(p.s, 1.7);
    const w = amp * Math.sin(TAU * (f.beats * t - p.s * 1.15));
    p.x += p.nx * w; p.y += p.ny * w;
  }
  return pts;
}

function bodyPath(x, pts, f, grow = 1) {
  const R = f.len * f.wide * grow;
  x.beginPath();
  pts.forEach((p, i) => { const w = halfWidth(p.s) * R; const a = p.x + p.nx * w, b = p.y + p.ny * w; i ? x.lineTo(a, b) : x.moveTo(a, b); });
  for (let i = pts.length - 1; i >= 0; i--) { const p = pts[i]; const w = halfWidth(p.s) * R; x.lineTo(p.x - p.nx * w, p.y - p.ny * w); }
  x.closePath();
}
const at = (pts, s) => pts[Math.min(pts.length - 1, Math.round(s * (pts.length - 1)))];

function fin(x, p, side, length, breadth, angle, color, edge = 0) {
  const dir = Math.atan2(p.ty, p.tx) + Math.PI - side * angle;
  const sx = p.x + p.nx * side * edge, sy = p.y + p.ny * side * edge;
  x.save(); x.translate(sx, sy); x.rotate(dir);
  x.beginPath(); x.moveTo(0, 0);
  x.quadraticCurveTo(length * .55, -side * breadth * 1.1, length, -side * breadth * .35);
  x.quadraticCurveTo(length * .72, side * breadth * .32, 0, side * breadth * .05);
  x.closePath(); x.fillStyle = color; x.globalAlpha = .8; x.fill();
  x.globalAlpha = .3; x.strokeStyle = '#000'; x.lineWidth = .4;
  for (const k of [.3, .6, .9]) { x.beginPath(); x.moveTo(0, 0); x.lineTo(length * (.75 + k * .2), -side * breadth * (k - .25)); x.stroke(); }
  x.restore();
}

function tailFin(x, f, pts, t) {
  const p = pts[pts.length - 1], L = f.len * .24, B = f.len * .135;
  const sw = Math.sin(TAU * (f.beats * t - 1.5)) * .55;
  const dir = Math.atan2(p.ty, p.tx) + Math.PI + sw;
  x.save(); x.translate(p.x, p.y); x.rotate(dir);
  x.beginPath(); x.moveTo(-3, 0);
  x.bezierCurveTo(L * .4, -B * .4, L * .75, -B * 1.05, L * 1.08, -B * .85);
  x.quadraticCurveTo(L * .72, -B * .25, L * .6, 0);
  x.quadraticCurveTo(L * .72, B * .25, L * 1.08, B * .85);
  x.bezierCurveTo(L * .75, B * 1.05, L * .4, B * .4, -3, 0);
  x.closePath(); x.fillStyle = f.fin; x.globalAlpha = .88; x.fill();
  x.globalAlpha = .28; x.strokeStyle = '#000'; x.lineWidth = .5;
  for (const k of [-.75, -.42, .42, .75]) { x.beginPath(); x.moveTo(0, 0); x.quadraticCurveTo(L * .5, B * k * .55, L * .98, B * k); x.stroke(); }
  x.restore();
}

function shadow(x, f, pts) {
  x.save(); x.translate(11, 15); x.filter = 'blur(7px)'; x.fillStyle = 'rgba(0,4,10,.55)';
  bodyPath(x, pts, f, 1.05); x.fill(); x.restore();
}

function drawFish(x, f, t) {
  const pts = spineOf(f, t), R = f.len * f.wide;
  const flap = Math.sin(TAU * (Math.round(f.beats * .5) * t)) * .17;

  tailFin(x, f, pts, t);
  const pe = halfWidth(.19) * R * .72, ve = halfWidth(.56) * R * .6;
  fin(x, at(pts, .19), 1, f.len * .2, f.len * .075, 1.05 + flap, f.fin, pe);
  fin(x, at(pts, .19), -1, f.len * .2, f.len * .075, 1.05 - flap, f.fin, pe);
  fin(x, at(pts, .56), 1, f.len * .11, f.len * .04, .8 - flap, f.fin, ve);
  fin(x, at(pts, .56), -1, f.len * .11, f.len * .04, .8 + flap, f.fin, ve);

  x.save(); bodyPath(x, pts, f); x.fillStyle = f.base; x.fill(); x.clip();
  for (const [s, o, rl, rw, col] of f.patches) {
    const p = at(pts, s), w = halfWidth(s) * R;
    x.fillStyle = col; x.beginPath();
    x.ellipse(p.x + p.nx * o * w, p.y + p.ny * o * w, rl * f.len, rw * R, Math.atan2(p.ty, p.tx), 0, TAU); x.fill();
  }
  // Scale rows, then a soft rounded-body shade from both flanks toward the spine.
  x.globalAlpha = .17; x.strokeStyle = '#3a1c10'; x.lineWidth = .35;
  for (let i = 7; i < 26; i++) {
    const p = pts[i], w = halfWidth(p.s) * R;
    for (let k = -2; k <= 2; k++) {
      const o = (k + (i % 2 ? .5 : 0)) * .34 * w;
      x.beginPath(); x.arc(p.x + p.nx * o, p.y + p.ny * o, 1.6, Math.atan2(p.ty, p.tx) - 1.2, Math.atan2(p.ty, p.tx) + 1.2); x.stroke();
    }
  }
  x.globalAlpha = 1;
  bodyPath(x, pts, f); x.strokeStyle = f.edge; x.globalAlpha = .55; x.lineWidth = R * .34; x.filter = 'blur(1.6px)'; x.stroke(); x.filter = 'none'; x.globalAlpha = 1;
  x.beginPath(); pts.slice(2, 22).forEach((p, i) => i ? x.lineTo(p.x, p.y) : x.moveTo(p.x, p.y));
  x.strokeStyle = 'rgba(255,255,255,.26)'; x.lineWidth = R * .34; x.lineCap = 'round'; x.filter = 'blur(1.4px)'; x.stroke(); x.filter = 'none';
  x.restore();

  // Dorsal fin, a thin ridge that shows the body bending.
  x.beginPath(); pts.slice(8, 21).forEach((p, i) => i ? x.lineTo(p.x, p.y) : x.moveTo(p.x, p.y));
  x.strokeStyle = f.base === INK ? '#55586a' : 'rgba(92,40,16,.5)'; x.lineWidth = 1.1; x.stroke();

  // Eyes, seen from above on both sides of the head.
  const e = at(pts, .065), ew = halfWidth(.065) * R * .82;
  for (const d of [1, -1]) {
    x.fillStyle = '#0a0a0d'; x.beginPath(); x.arc(e.x + e.nx * d * ew, e.y + e.ny * d * ew, Math.max(1.2, f.len * .0135), 0, TAU); x.fill();
    x.fillStyle = 'rgba(255,255,255,.85)'; x.beginPath(); x.arc(e.x + e.nx * d * ew - .4, e.y + e.ny * d * ew - .4, .5, 0, TAU); x.fill();
  }
  // Barbels at the mouth.
  const h = pts[0]; x.strokeStyle = f.base === INK ? '#6d7080' : 'rgba(110,60,30,.8)'; x.lineWidth = .6;
  for (const d of [1, -1]) { x.beginPath(); x.moveTo(h.x, h.y); x.quadraticCurveTo(h.x + h.tx * 4 + h.nx * d * 3, h.y + h.ty * 4 + h.ny * d * 3, h.x + h.tx * 3 + h.nx * d * 7, h.y + h.ty * 3 + h.ny * d * 7); x.stroke(); }
}

// Static floor of the pond, with the name lying on it so koi swim across the title.
const [floor, fx] = layer();
function paintFloor() {
  const g = fx.createRadialGradient(480, 150, 40, 480, 160, 620);
  g.addColorStop(0, '#16424c'); g.addColorStop(.5, '#0d2a35'); g.addColorStop(1, '#061119');
  fx.fillStyle = g; fx.fillRect(0, 0, W, H);
  const r = rng(77);
  for (let i = 0; i < 26; i++) {   // pale pebbles, barely visible
    const x = r() * W, y = r() * H, s = 14 + r() * 46;
    fx.fillStyle = `rgba(150,205,205,${.012 + r() * .022})`;
    fx.beginPath(); fx.ellipse(x, y, s, s * (.45 + r() * .4), r() * 3, 0, TAU); fx.fill();
  }
  fx.save(); fx.filter = 'blur(1.1px)'; fx.lineCap = 'round';
  for (let i = 0; i < 30; i++) { // caustic filaments
    let x = r() * W, y = r() * H; const a = r() * TAU;
    fx.beginPath(); fx.moveTo(x, y);
    for (let k = 0; k < 4; k++) { x += Math.cos(a + r() - .5) * 34; y += Math.sin(a + r() - .5) * 20; fx.lineTo(x, y); }
    fx.strokeStyle = `rgba(128,215,210,${.018 + r() * .03})`; fx.lineWidth = .7 + r(); fx.stroke();
  }
  fx.restore();

  fx.textAlign = 'center'; fx.textBaseline = 'alphabetic';
  fx.font = 'italic 700 132px Lora';
  fx.save(); fx.filter = 'blur(10px)'; fx.fillStyle = 'rgba(0,8,14,.7)'; fx.fillText('Fizz', 484, 180); fx.restore();
  fx.fillStyle = CREAM; fx.fillText('Fizz', 480, 174);

  // Vermilion seal reading "cá", Vietnamese for fish.
  const sx = 594, sy = 86, ss = 38;
  fx.fillStyle = '#d13a1a'; fx.beginPath(); fx.roundRect(sx, sy, ss, ss, 6); fx.fill();
  fx.fillStyle = CREAM; fx.font = 'italic 700 25px Lora'; fx.fillText('cá', sx + ss / 2, sy + 26);

  fx.font = '13.5px Mono'; fx.fillStyle = 'rgba(214,232,225,.86)';
  if ('letterSpacing' in fx) fx.letterSpacing = '2.6px';
  fx.fillText('SOFTWARE ENGINEER  ~  AI ENGINEER', 480, 214);
  if ('letterSpacing' in fx) fx.letterSpacing = '0px';
}

// Lily pads float above the koi and stay perfectly still, which also keeps the GIF small.
const [surface, sx] = layer();
function pad(x, cx, cy, r, rot, tone) {
  x.save(); x.translate(cx, cy); x.rotate(rot);
  x.save(); x.translate(6, 9); x.filter = 'blur(5px)'; x.fillStyle = 'rgba(0,5,10,.55)'; x.beginPath(); x.arc(0, 0, r, .16, TAU - .16); x.lineTo(0, 0); x.closePath(); x.fill(); x.restore();
  const g = x.createRadialGradient(-r * .2, -r * .2, 2, 0, 0, r);
  g.addColorStop(0, tone[0]); g.addColorStop(1, tone[1]);
  x.fillStyle = g; x.beginPath(); x.arc(0, 0, r, .16, TAU - .16); x.lineTo(0, 0); x.closePath(); x.fill();
  x.strokeStyle = 'rgba(205,240,175,.17)'; x.lineWidth = .8;
  for (let a = .42; a < TAU - .3; a += .52) { x.beginPath(); x.moveTo(0, 0); x.lineTo(Math.cos(a) * r * .93, Math.sin(a) * r * .93); x.stroke(); }
  x.restore();
}
function lotus(x, cx, cy, r) {
  x.save(); x.translate(cx, cy);
  for (const [n, rad, col] of [[9, r, '#ef9cae'], [7, r * .72, '#f7bfc8'], [5, r * .46, '#fde0e0']]) {
    for (let i = 0; i < n; i++) {
      x.save(); x.rotate(i / n * TAU + rad);
      x.fillStyle = col; x.strokeStyle = 'rgba(150,40,75,.4)'; x.lineWidth = .5;
      x.beginPath(); x.moveTo(0, 0); x.quadraticCurveTo(rad * .55, -rad * .46, rad, 0); x.quadraticCurveTo(rad * .55, rad * .46, 0, 0); x.fill(); x.stroke();
      x.restore();
    }
  }
  x.fillStyle = '#f2c94c'; x.beginPath(); x.arc(0, 0, r * .17, 0, TAU); x.fill();
  x.restore();
}
function paintSurface() {
  const G1 = ['#3f7d4c', '#1c4a31'], G2 = ['#346f46', '#16402c'], G3 = ['#4a8a55', '#225638'];
  pad(sx, 38, 32, 52, .7, G2); pad(sx, 112, 18, 30, 2.5, G3); pad(sx, 26, 106, 26, 4.1, G1);
  pad(sx, 925, 276, 58, 3.6, G2); pad(sx, 842, 304, 32, 5.2, G3); pad(sx, 938, 186, 24, 1.3, G1);
  lotus(sx, 64, 50, 24); lotus(sx, 906, 262, 27);
}

const drops = [[300, 70, 0, 1], [705, 216, 1 / 3, 1], [120, 150, 2 / 3, 1], [560, 290, .15, 2], [850, 165, .5, 2], [420, 36, .82, 2]];
function ripples(x, t) {
  for (const [cx, cy, ph, rate] of drops) {
    const p = (t * rate + ph) % 1; if (p > .42) continue;
    const q = p / .42;
    for (const [k, a] of [[1, .34], [.62, .22]]) {
      x.strokeStyle = `rgba(190,238,235,${a * Math.pow(1 - q, 1.4)})`; x.lineWidth = 1.05;
      x.beginPath(); x.ellipse(cx, cy, 46 * q * k + 1, 24 * q * k + .6, 0, 0, TAU); x.stroke();
    }
  }
}

window.ready = (async () => {
  await Promise.all([document.fonts.load('italic 700 132px Lora', 'Fizzcá'), document.fonts.load('14px Mono', 'S')]);
  paintFloor(); paintSurface();
})();

window.renderFrame = t => {
  c.setTransform(SS, 0, 0, SS, 0, 0);
  c.drawImage(floor, 0, 0, W, H);
  ripples(c, t);
  const spines = fish.map(f => spineOf(f, t));
  fish.forEach((f, i) => shadow(c, f, spines[i]));
  fish.forEach(f => drawFish(c, f, t));
  c.drawImage(surface, 0, 0, W, H);
  octx.imageSmoothingQuality = 'high';
  octx.drawImage(stage, 0, 0, W, H);
  return out.toDataURL('image/png');
};
