import { test } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

const BASE_URL = 'file:///' + path.resolve(__dirname, '..').replace(/\\/g, '/');
const AFTER_URL = `${BASE_URL}/after/index.html`;
const REVIEW_DIR = path.resolve(__dirname, '../review');

fs.mkdirSync(REVIEW_DIR, { recursive: true });

test('Capture Master DTC Editorial Screenshots', async ({ page }) => {
  await page.addInitScript(() => sessionStorage.setItem('nova_promo_dismissed', 'true'));

  // 1. Desktop 1440px
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(AFTER_URL);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(600);

  // Full page desktop
  await page.screenshot({
    path: path.join(REVIEW_DIR, '01_desktop_1440_fullpage.png'),
    fullPage: true
  });

  // Hero section desktop
  const heroSection = page.locator('#hero');
  await heroSection.screenshot({
    path: path.join(REVIEW_DIR, '02_hero_desktop_1440.png')
  });

  // All 6 Cards individually at Desktop 1440px
  const cards = [
    { id: 'k75', selector: '.card-theme-k75', name: '03_card_01_k75_desktop.png' },
    { id: 'pulse', selector: '.card-theme-pulse', name: '04_card_02_pulse_desktop.png' },
    { id: 'orbit', selector: '.card-theme-orbit', name: '05_card_03_orbit_desktop.png' },
    { id: 'flux', selector: '.card-theme-flux', name: '06_card_04_flux_desktop.png' },
    { id: 'novadesk', selector: '.card-theme-mat', name: '07_card_05_novadesk_desktop.png' },
    { id: 'beam', selector: '.card-theme-beam', name: '08_card_06_beam_desktop.png' },
  ];

  for (const c of cards) {
    const cardEl = page.locator(c.selector);
    await cardEl.scrollIntoViewIfNeeded();
    await page.waitForTimeout(200);
    await cardEl.screenshot({
      path: path.join(REVIEW_DIR, c.name)
    });
  }

  // 2. Mobile 390px
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(AFTER_URL);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(600);

  // Full page mobile
  await page.screenshot({
    path: path.join(REVIEW_DIR, '09_mobile_390_fullpage.png'),
    fullPage: true
  });

  // Hero mobile
  await page.locator('#hero').screenshot({
    path: path.join(REVIEW_DIR, '10_hero_mobile_390.png')
  });

  // Cards mobile
  for (const c of cards) {
    const cardEl = page.locator(c.selector);
    await cardEl.scrollIntoViewIfNeeded();
    await page.waitForTimeout(200);
    await cardEl.screenshot({
      path: path.join(REVIEW_DIR, `11_mobile_${c.id}.png`)
    });
  }

  // 3. Viewport Responsive Checks (320px, 768px, 1024px, 1920px)
  for (const vpWidth of [320, 768, 1024, 1920]) {
    await page.setViewportSize({ width: vpWidth, height: 900 });
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(400);

    // Products catalog viewport screenshot
    const productsSection = page.locator('#products');
    await productsSection.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    await page.screenshot({
      path: path.join(REVIEW_DIR, `12_viewport_${vpWidth}_catalog.png`)
    });
  }
});
