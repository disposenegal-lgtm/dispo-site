const { chromium } = require('playwright');
const files = process.argv.slice(2);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: +(process.env.DSF || 3.125) });
  for (const f of files) {
    await p.goto('file://' + __dirname + '/' + f + '.html', { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
    await p.screenshot({ path: (process.env.OUT || __dirname + '/export') + '/' + f + '.png' });
    if (!process.env.OUT) await p.pdf({ path: __dirname + '/export/' + f + '.pdf', width: '210mm', height: '297mm', printBackground: true });
  }
  await b.close();
})();
