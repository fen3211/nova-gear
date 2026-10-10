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

  // Hero Section Phase A (Top / Frame 14 after intro fly-in)
  const heroViewport = page.locator('.hero-sticky-viewport');
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.locator('body.hero-intro-ready').waitFor({ timeout: 4000 });
  await page.waitForTimeout(400);

  // 1. Initial Hero after intro animation
  await heroViewport.screenshot({
    path: path.join(REVIEW_DIR, 'hero_desktop_initial.png')
  });
  await heroViewport.screenshot({
    path: path.join(REVIEW_DIR, '02_hero_phase_a_intro.png')
  });

  // 2. Collision check (headline vs 3D stage)
  const heroGrid = page.locator('.hero-asymmetric-grid');
  await heroGrid.screenshot({
    path: path.join(REVIEW_DIR, 'hero_collision_check_1440.png')
  });

  // 3. Telemetry contrast closeup with SVG leader lines
  const visualStage = page.locator('.hero-visual-stage');
  await visualStage.screenshot({
    path: path.join(REVIEW_DIR, 'hero_telemetry_contrast.png')
  });

  // Hero Section Phase B/C (Mid scrub 50%)
  const heroTrack = page.locator('#heroScrollTrack');
  const trackBox = await heroTrack.boundingBox();
  if (trackBox) {
    const scrollTravel = trackBox.height - 900;
    await page.evaluate((y) => window.scrollTo(0, y), scrollTravel * 0.50);
    await page.waitForTimeout(450);
    await heroViewport.screenshot({
      path: path.join(REVIEW_DIR, 'hero_desktop_scrub_mid.png')
    });
    await heroViewport.screenshot({
      path: path.join(REVIEW_DIR, '02_hero_phase_bc_orbit.png')
    });

    // Hero Section Phase D (Final reveal)
    await page.evaluate((y) => window.scrollTo(0, y), scrollTravel * 0.95);
    await page.waitForTimeout(450);
    await heroViewport.screenshot({
      path: path.join(REVIEW_DIR, '02_hero_phase_d_reveal.png')
    });
  }

  // All 6 Cards individually at Desktop 1440px
  const cards = [
    { id: 'k75', selector: '.card-theme-k75', name: '03_card_01_k75_desktop.png' },
    { id: 'pulse', selector: '.card-theme-pulse', name: '04_card_02_pulse_desktop.png' },
    { id: 'orbit', selector: '.card-theme-orbit', name: '05_card_03_orbit_desktop.png' },
    { id: 'flux', selector: '.card-theme-flux', name: '06_card_04_flux_desktop.png' },
    { id: 'beam', selector: '.card-theme-beam', name: '07_card_05_beam_desktop.png' },
    { id: 'novadesk', selector: '.card-theme-mat', name: '08_card_06_novadesk_desktop.png' },
  ];

  for (const c of cards) {
    const cardEl = page.locator(c.selector);
    await cardEl.scrollIntoViewIfNeeded();
    await page.waitForTimeout(200);
    await cardEl.screenshot({
      path: path.join(REVIEW_DIR, c.name)
    });
  }

  // Full Catalog Section Desktop
  const productsSection = page.locator('#products');
  await productsSection.scrollIntoViewIfNeeded();
  await page.waitForTimeout(300);
  await productsSection.screenshot({
    path: path.join(REVIEW_DIR, '08_catalog_desktop_1440.png')
  });

  // Light Keyboard Studio Desktop Modal
  const studioBtn = page.locator('.btn-hero-studio-cta');
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(200);
  await studioBtn.click();
  await page.waitForTimeout(400);

  const studioWindow = page.locator('.studio-window');
  await studioWindow.screenshot({
    path: path.join(REVIEW_DIR, '09_studio_light_desktop_1440.png')
  });
  await page.locator('.studio-topbar .btn-close-configurator').click();
  await page.waitForTimeout(200);

  // 2. Mobile 390px
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(AFTER_URL);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);

  // Full page mobile
  await page.screenshot({
    path: path.join(REVIEW_DIR, '10_mobile_390_fullpage.png'),
    fullPage: true
  });

  // Hero mobile 390px
  await heroViewport.screenshot({
    path: path.join(REVIEW_DIR, 'hero_mobile_390.png')
  });
  await heroViewport.screenshot({
    path: path.join(REVIEW_DIR, '11_hero_mobile_390.png')
  });

  // Cards mobile
  for (const c of cards) {
    const cardEl = page.locator(c.selector);
    await cardEl.scrollIntoViewIfNeeded();
    await page.waitForTimeout(200);
    await cardEl.screenshot({
      path: path.join(REVIEW_DIR, `12_mobile_${c.id}.png`)
    });
  }

  // Light Studio Mobile 390px (Settings Tab & Preview Tab)
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(200);
  await page.locator('.btn-hero-studio-cta').click();
  await page.waitForTimeout(350);

  await studioWindow.screenshot({
    path: path.join(REVIEW_DIR, '13_studio_mobile_390_settings.png')
  });

  await page.locator('.studio-mob-tab[data-tab="preview"]').click();
  await page.waitForTimeout(300);
  await studioWindow.screenshot({
    path: path.join(REVIEW_DIR, '14_studio_mobile_390_keymap.png')
  });
  await page.locator('.studio-topbar .btn-close-configurator').click();
  await page.waitForTimeout(200);

  // 3. Mobile 320px
  await page.setViewportSize({ width: 320, height: 700 });
  await page.goto(AFTER_URL);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(400);

  // Hero mobile 320px
  await heroViewport.screenshot({
    path: path.join(REVIEW_DIR, 'hero_mobile_320.png')
  });

  await page.screenshot({
    path: path.join(REVIEW_DIR, '15_mobile_320_fullpage.png'),
    fullPage: true
  });

  await page.locator('.btn-hero-studio-cta').click();
  await page.waitForTimeout(300);
  await page.locator('.studio-mob-tab[data-tab="preview"]').click();
  await page.waitForTimeout(250);
  await studioWindow.screenshot({
    path: path.join(REVIEW_DIR, '16_studio_mobile_320_keymap.png')
  });
  await page.locator('.studio-topbar .btn-close-configurator').click();
  await page.waitForTimeout(200);

  // 4. Viewport Checks (768px, 1024px, 1920px)
  for (const vpWidth of [768, 1024, 1920]) {
    await page.setViewportSize({ width: vpWidth, height: 900 });
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(350);

    const prods = page.locator('#products');
    await prods.scrollIntoViewIfNeeded();
    await page.waitForTimeout(250);
    await page.screenshot({
      path: path.join(REVIEW_DIR, `17_viewport_${vpWidth}_catalog.png`)
    });
  }
});
