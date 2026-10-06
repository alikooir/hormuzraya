// Crops the dark logo square out of site/tools/logo-source.png and writes logo PNGs to site/assets.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const A = path.join(__dirname, '..', 'assets');
const src = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, 'logo-source.png')).toString('base64');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const out = await p.evaluate(async (src) => {
    const img = new Image(); img.src = src; await img.decode();
    const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
    const x = c.getContext('2d'); x.drawImage(img, 0, 0);
    const d = x.getImageData(0, 0, c.width, c.height).data;
    let minX = 1e9, minY = 1e9, maxX = -1, maxY = -1;
    for (let y = 0; y < c.height; y++) for (let i = 0; i < c.width; i++) {
      const k = (y * c.width + i) * 4;
      if (d[k] < 40 && d[k + 1] < 40 && d[k + 2] < 40) { minX = Math.min(minX, i); maxX = Math.max(maxX, i); minY = Math.min(minY, y); maxY = Math.max(maxY, y); }
    }
    const side = Math.min(maxX - minX, maxY - minY) + 1;
    const res = {};
    for (const s of [32, 180, 192, 512]) {
      const o = document.createElement('canvas'); o.width = o.height = s;
      const ox = o.getContext('2d'); ox.imageSmoothingQuality = 'high';
      ox.drawImage(img, minX, minY, side, side, 0, 0, s, s);
      res[s] = o.toDataURL('image/png');
    }
    res.box = [minX, minY, maxX, maxY];
    return res;
  }, src);
  console.log('box', out.box);
  const save = (n, s) => fs.writeFileSync(path.join(A, n), Buffer.from(out[s].split(',')[1], 'base64'));
  save('favicon-32.png', 32); save('apple-touch-icon.png', 180); save('logo-192.png', 192); save('logo-512.png', 512);
  await b.close();
})();
