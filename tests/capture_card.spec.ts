import { test, expect } from '@playwright/test';
import * as path from 'path';

const AFTER_URL = 'file:///' + path.resolve(__dirname, '../after/index.html').replace(/\\/g, '/');
const OUTPUT_DIR = path.resolve(__dirname, '../assets/previews');

test('Capture real browser screenshots of Flux charger and NovaDesk mat on Desktop and Mobile', async ({ page }) => {
  // Prevent automated promo popup from opening and intercepting pointer events
  await page.addInitScript(() => {
    sessionStorage.setItem('nova_promo_dismissed', 'true');
  });

  // 1. Desktop 1440px
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto(AFTER_URL);
  await page.waitForLoadState('networkidle');

  // Flux Charger Desktop Card
  const cardFlux = page.locator('.card-theme-flux');
  await cardFlux.scrollIntoViewIfNeeded();
  await page.waitForTimeout(500);
  await cardFlux.screenshot({
    path: path.join(OUTPUT_DIR, 'card_flux_browser_desktop.png'),
  });

  // Flux Charger Catalog Row
  const rowFlux = page.locator('.editorial-row').nth(1);
  await rowFlux.screenshot({
    path: path.join(OUTPUT_DIR, 'catalog_row_browser_desktop.png'),
  });

  // Flux Charger Hover State (demonstrating synchronized scale & rotation without drift)
  await cardFlux.hover();
  await page.waitForTimeout(400);
  await cardFlux.screenshot({
    path: path.join(OUTPUT_DIR, 'card_flux_hover_desktop.png'),
  });
  await page.mouse.move(0, 0);
  await page.waitForTimeout(300);

  // NovaDesk Mat Desktop Card
  const cardMat = page.locator('.card-theme-mat');
  await cardMat.scrollIntoViewIfNeeded();
  await page.waitForTimeout(500);
  await cardMat.screenshot({
    path: path.join(OUTPUT_DIR, 'card_mat_browser_desktop.png'),
  });

  // NovaDesk Mat Catalog Row (NovaDesk + Beam)
  const rowMat = page.locator('.editorial-row').nth(2);
  await rowMat.screenshot({
    path: path.join(OUTPUT_DIR, 'catalog_row_mat_browser_desktop.png'),
  });

  // NovaDesk Mat Hover State
  await cardMat.hover();
  await page.waitForTimeout(400);
  await cardMat.screenshot({
    path: path.join(OUTPUT_DIR, 'card_mat_hover_desktop.png'),
  });
  await page.mouse.move(0, 0);
  await page.waitForTimeout(300);

  // 2. Mobile 390px
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(AFTER_URL);
  await page.waitForLoadState('networkidle');

  const cardFluxMobile = page.locator('.card-theme-flux');
  await cardFluxMobile.scrollIntoViewIfNeeded();
  await page.waitForTimeout(500);
  await cardFluxMobile.screenshot({
    path: path.join(OUTPUT_DIR, 'card_flux_browser_mobile.png'),
  });

  const cardMatMobile = page.locator('.card-theme-mat');
  await cardMatMobile.scrollIntoViewIfNeeded();
  await page.waitForTimeout(500);
  await cardMatMobile.screenshot({
    path: path.join(OUTPUT_DIR, 'card_mat_browser_mobile.png'),
  });
});
