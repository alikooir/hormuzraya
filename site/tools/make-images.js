// Regenerates the link-preview (Open Graph) images in site/assets. Run make-logo.js first.
// Run from the repo root: node site/tools/make-images.js   (needs the `playwright` package)
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const A = path.join(__dirname, '..', 'assets');
const font = 'data:font/woff2;base64,' + fs.readFileSync(path.join(A, 'fonts', 'vazirmatn-var.woff2')).toString('base64');
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(A, 'logo-192.png')).toString('base64');
const base = `<style>@font-face{font-family:V;src:url(${font});font-weight:100 900}*{margin:0;box-sizing:border-box}body{font-family:V,sans-serif}</style>`;

function og(lang) {
  const fa = lang === 'fa';
  const contours = Array.from({ length: 7 }, (_, k) => `<ellipse cx="${fa ? 170 : 1030}" cy="560" rx="${90 + k * 70}" ry="${70 + k * 55}" fill="none" stroke="#4fb6bb" stroke-opacity=".14"/>`).join('');
  return `${base}<body style="width:1200px;height:630px;background:#08181b;color:#e2eded;position:relative;overflow:hidden" dir="${fa ? 'rtl' : 'ltr'}">
<svg width="1200" height="630" style="position:absolute;inset:0">${contours}</svg>
<div style="position:absolute;inset:0;padding:80px 90px;display:flex;flex-direction:column;gap:28px">
<div style="display:flex;align-items:center;gap:18px"><img src="${logo}" width="72" height="72" style="border-radius:6px">
<div style="font-size:40px;font-weight:800">${fa ? 'هرمز رایا' : 'Hormoz Raya'}</div></div>
<div style="font-size:${fa ? 62 : 64}px;font-weight:900;line-height:1.35;max-width:900px">${fa ? 'برای مسائل و مشکلات کسب‌وکارها، <span style="color:#4fb6bb">راهکارهای هوشمند</span> می‌سازیم.' : 'We build <span style="color:#4fb6bb">intelligent solutions</span> to the problems and challenges businesses face.'}</div>
<div style="margin-top:auto;font-size:26px;color:#93abad;display:flex;gap:14px;align-items:center"><span style="width:12px;height:12px;border-radius:50%;background:#e2694c;display:inline-block"></span>${fa ? 'راهکارهای هوشمند هرمز رایا · پارک علم و فناوری هرمزگان' : 'Hormoz Raya Smart Solutions · Hormozgan Science & Technology Park'}</div>
</div></body>`;
}

(async () => {
  const b = await chromium.launch();
  const shot = async (html, w, h, file) => {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.setContent(html); await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(A, file) }); await p.close();
  };
  await shot(og('fa'), 1200, 630, 'og-fa.png');
  await shot(og('en'), 1200, 630, 'og-en.png');
  await b.close();
})();
