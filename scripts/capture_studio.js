const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const url = 'file:///' + path.resolve('after/index.html').replace(/\\/g, '/');
  await page.goto(url);
  await page.waitForLoadState('networkidle');

  // Open NOVA Keyboard Studio
  const studioBtn = page.locator('[data-action="open-configurator"]').first();
  await studioBtn.click();
  await page.waitForTimeout(600);
  await page.screenshot({ path: path.resolve('review/13_studio_modal_desktop.png') });

  // Mobile
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.resolve('review/14_studio_modal_mobile.png') });

  await browser.close();
  console.log('Successfully captured studio screenshots');
})();
