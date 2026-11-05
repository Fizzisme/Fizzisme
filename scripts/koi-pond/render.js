// Needs: npm i playwright && npx playwright install chromium, plus ffmpeg.
// 1) mkdir frames && node render.js frames 200
// 2) ffmpeg -framerate 20 -i frames/%04d.png -vf "palettegen=max_colors=200:stats_mode=full" pal.png
// 3) ffmpeg -framerate 20 -i frames/%04d.png -i pal.png -lavfi "paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" -loop 0 ../../assets/koi-pond.gif
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const dir = process.argv[2], N = +(process.argv[3] || 200), only = process.argv[4]?.split(',').map(Number);
  const b = await chromium.launch(); const p = await b.newPage();
  p.on('pageerror', e => console.error('PAGE', e.message));
  await p.goto('file://' + path.join(__dirname, 'pond.html')); await p.evaluate(() => window.ready);
  for (const i of only || [...Array(N).keys()]) {
    const d = await p.evaluate(t => window.renderFrame(t), i / N);
    fs.writeFileSync(path.join(dir, String(i).padStart(4, '0') + '.png'), Buffer.from(d.split(',')[1], 'base64'));
  }
  await b.close();
})();
