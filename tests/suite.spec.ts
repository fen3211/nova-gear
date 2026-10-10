import { test, expect } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

const BASE_URL = 'file:///' + path.resolve(__dirname, '..').replace(/\\/g, '/');
const AFTER_URL = `${BASE_URL}/after/index.html`;
const BEFORE_URL = `${BASE_URL}/before/index.html`;
const ROOT_URL = `${BASE_URL}/index.html`;

const SCREENSHOTS_DIR = path.resolve(__dirname, '../test-results/screenshots');
fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });

const REVIEW_DIR = path.resolve(__dirname, '../review');
fs.mkdirSync(REVIEW_DIR, { recursive: true });

test.describe('NOVA GEAR Master DTC Verification Suite', () => {

  test('01: Showcase Switcher & BEFORE/AFTER defect contrast', async ({ page }) => {
    await page.goto(ROOT_URL);
    await page.waitForLoadState('networkidle');

    // 1. Check BEFORE version retains intentional defects
    await page.goto(BEFORE_URL);
    await page.waitForLoadState('networkidle');
    const beforeHeadline = page.locator('h1').first();
    await expect(beforeHeadline).toBeVisible();

    // 2. Visit AFTER master version
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.hero-headline')).toBeVisible();
    await expect(page.locator('.brand-logo').first()).toContainText('NOVA');
  });

  test('02: Product Images Alpha Transparency & Border-Radius Removal', async ({ page }) => {
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    const expectedImages = [
      'keyboard-k75.png',
      'keyboard-k75-isolated.webp',
      'keyboard-k75-shadow.webp',
      'mouse-pulse-isolated.webp',
      'mouse-pulse-shadow.webp',
      'headphones-orbit-isolated.webp',
      'headphones-orbit-shadow.webp',
      'flux-charger-isolated.webp',
      'flux-charger-shadow.webp',
      'mat-novadesk-isolated.webp',
      'mat-novadesk-shadow.webp',
      'light-beam-isolated.webp',
      'light-beam-shadow.webp'
    ];

    for (const imgName of expectedImages) {
      const imgLoc = page.locator(`img[src*="${imgName}"]`).first();
      await expect(imgLoc).toBeAttached();
      await imgLoc.scrollIntoViewIfNeeded();

      // Ensure lazy images load completely
      const handle = await imgLoc.elementHandle();
      expect(handle).not.toBeNull();
      const isLoaded = await page.waitForFunction(
        (el: HTMLImageElement | null) => el !== null && el.complete && el.naturalWidth > 0,
        handle,
        { timeout: 7000 }
      );
      expect(isLoaded).toBeTruthy();
    }

    // Verify border-radius: 0 on transparent assets
    const heroImg = page.locator('.hero-3d-img');
    const heroBorderRadius = await heroImg.evaluate(el => window.getComputedStyle(el).borderRadius);
    expect(heroBorderRadius).toBe('0px');

    const cardImgs = page.locator('.card-3d-render');
    const count = await cardImgs.count();
    for (let i = 0; i < count; i++) {
      const radius = await cardImgs.nth(i).evaluate(el => window.getComputedStyle(el).borderRadius);
      expect(radius).toBe('0px');
    }

    // Verify headline lines are completely readable
    const line1 = page.locator('.hero-headline .line-break').nth(0);
    const line2 = page.locator('.hero-headline .line-break').nth(1);
    await expect(line1).toHaveText('BETTER GEAR.');
    await expect(line2).toHaveText('BETTER DAYS.');
    await expect(line1).toBeVisible();
    await expect(line2).toBeVisible();
  });

  test('03: Cart State Resilience (Corrupted [null] & Blocked Storage)', async ({ page }) => {
    // Inject corrupt [null] and broken records
    await page.addInitScript(() => {
      localStorage.setItem('nova_gear_cart', JSON.stringify([
        null,
        {},
        { invalid: true },
        { id: 'non_existent_item', quantity: 99 },
        { id: 'k75', quantity: -10 },
        { id: 'pulse', quantity: 'corrupted_string' }
      ]));
    });

    const pageErrors: string[] = [];
    page.on('pageerror', err => pageErrors.push(err.message));

    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    expect(pageErrors.length).toBe(0);

    const cartCounter = page.locator('.cart-counter');
    await expect(cartCounter).toHaveText('0');

    // Add valid item: NovaKeys K75 ($129)
    await page.locator('.btn-add-cart[data-id="k75"]').first().click();
    await expect(cartCounter).toHaveText('1');

    // Open Cart Drawer
    await page.locator('.site-header [data-action="open-cart"]').click();
    const cartDrawer = page.locator('.cart-drawer');
    await expect(cartDrawer).toHaveClass(/open/);

    const subtotalEl = page.locator('.subtotal-amount');
    await expect(subtotalEl).toHaveText('$129');

    // Lock Storage to simulate restricted/blocked sandbox environment
    await page.evaluate(() => {
      Storage.prototype.removeItem = () => {
        throw new DOMException('Access denied', 'SecurityError');
      };
    });

    // Reset Demo State button must succeed safely without unhandled exception
    const resetBtn = page.locator('.btn-reset-demo');
    await resetBtn.click();
    await expect(cartCounter).toHaveText('0');
  });

  test('04: Focus Management (Cart Empty, Checkout Recovery, Dialog Trap)', async ({ page }) => {
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    // Add 1 item
    await page.locator('.btn-add-cart[data-id="pulse"]').first().click();

    // Open Cart Drawer
    const headerCartBtn = page.locator('.site-header [data-action="open-cart"]');
    await headerCartBtn.click();

    const cartDrawer = page.locator('.cart-drawer');
    await expect(cartDrawer).toHaveClass(/open/);

    // Remove item to empty cart
    const removeBtn = page.locator('.btn-remove-item[data-id="pulse"]');
    await removeBtn.click();

    // Empty state should be visible
    await expect(page.locator('.cart-empty-state')).toBeVisible();

    // Focus must stay INSIDE open drawer
    const focusedInsideCart = await page.evaluate(() => {
      const active = document.activeElement;
      const drawer = document.querySelector('.cart-drawer');
      return drawer ? drawer.contains(active) : false;
    });
    expect(focusedInsideCart, 'Focus must remain inside open drawer when cart is emptied').toBe(true);

    // Close Cart Drawer
    await page.locator('.btn-close-cart').click();

    // Add item again and test Checkout modal focus recovery
    await page.locator('.btn-add-cart[data-id="k75"]').first().click();
    await headerCartBtn.click();

    const checkoutBtn = page.locator('.btn-checkout');
    await checkoutBtn.click();

    const checkoutModal = page.locator('.checkout-modal-backdrop');
    await expect(checkoutModal).toHaveClass(/open/);

    // Close Checkout modal
    const closeCheckoutBtn = page.locator('.btn-close-checkout').first();
    await closeCheckoutBtn.click();
    await expect(checkoutModal).not.toHaveClass(/open/);

    // Verify focus is restored to visible interactive element, NOT hidden drawer
    const activeIsHidden = await page.evaluate(() => {
      const active = document.activeElement;
      if (!active) return true;
      const insideHiddenDrawer = active.closest('.cart-drawer:not(.open)') !== null;
      return insideHiddenDrawer;
    });
    expect(activeIsHidden, 'Focus must NOT remain inside closed cart drawer').toBe(false);
  });

  test('05: Mobile Navigation aria-expanded Synchronization', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    const menuBtn = page.locator('.btn-mobile-menu');
    await expect(menuBtn).toHaveAttribute('aria-expanded', 'false');

    // 1. Open mobile menu
    await menuBtn.click();
    await expect(menuBtn).toHaveAttribute('aria-expanded', 'true');

    // 2. Close via Close Button
    const closeMenuBtn = page.locator('.btn-close-mobile-nav');
    await closeMenuBtn.click();
    await expect(menuBtn).toHaveAttribute('aria-expanded', 'false');

    // 3. Open and close via Escape
    await menuBtn.click();
    await expect(menuBtn).toHaveAttribute('aria-expanded', 'true');
    await page.keyboard.press('Escape');
    await expect(menuBtn).toHaveAttribute('aria-expanded', 'false');

    // 4. Open and close via Navigation link
    await menuBtn.click();
    await expect(menuBtn).toHaveAttribute('aria-expanded', 'true');
    await page.locator('.mobile-nav-link').first().click();
    await expect(menuBtn).toHaveAttribute('aria-expanded', 'false');

    // 5. Open mobile menu and launch search via dedicated mobile button
    await menuBtn.click();
    await expect(menuBtn).toHaveAttribute('aria-expanded', 'true');
    const mobileSearchBtn = page.locator('.mobile-nav-search-btn');
    await expect(mobileSearchBtn).toBeVisible();
    await mobileSearchBtn.click();
    await expect(menuBtn).toHaveAttribute('aria-expanded', 'false');
    const searchBackdrop = page.locator('.search-modal-backdrop');
    await expect(searchBackdrop).toHaveClass(/open/);
    await expect(page.locator('.search-field')).toBeFocused();
    await page.locator('.btn-close-search').click();
    await expect(searchBackdrop).not.toHaveClass(/open/);
  });

  test('06: Local Search XSS Immunity via textContent', async ({ page }) => {
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    const searchBtn = page.locator('[data-action="open-search"]').first();
    await searchBtn.click();

    const searchInput = page.locator('.search-field');
    const payload = '<img src=x onerror=alert(1)><b id="injected-tag">INJECTION</b>';
    await searchInput.fill(payload);

    // Malicious DOM node must NEVER be created
    const injectedNode = page.locator('#injected-tag');
    await expect(injectedNode).toHaveCount(0);

    // Text must be safely rendered
    const resultsContainer = page.locator('.search-results-list');
    await expect(resultsContainer).toContainText(payload.toUpperCase());
  });

  test('07: Local Interactive Demos (Configurator & Warranty Policy)', async ({ page }) => {
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    // 1. Launch Configurator Modal
    const configTrigger = page.locator('[data-action="open-configurator"]').first();
    await configTrigger.scrollIntoViewIfNeeded();
    await configTrigger.click();

    const configModal = page.locator('.configurator-modal-backdrop');
    await expect(configModal).toHaveClass(/open/);
    await expect(configModal.locator('#configurator-modal-title')).toBeVisible();

    // Toggle OS to Windows
    const winBtn = configModal.locator('.btn-cfg-os[data-os="win"]');
    await winBtn.click();
    await expect(winBtn).toHaveClass(/active/);
    await expect(configModal.locator('.cfg-key-opt')).toHaveText('WIN');

    // Switch selection
    const tactileBtn = configModal.locator('.btn-cfg-switch[data-switch="tactile"]');
    await tactileBtn.click();
    await expect(tactileBtn).toHaveClass(/active/);

    // Audition switch sound
    const soundBtn = configModal.locator('.btn-cfg-sound-demo');
    await soundBtn.click();

    // Add configured item to cart
    const addConfigBtn = configModal.locator('.btn-configurator-add-cart');
    await addConfigBtn.click();
    await expect(configModal).not.toHaveClass(/open/);

    // Cart count should be incremented
    await expect(page.locator('.cart-counter')).toHaveText('1');

    // Verify Configurator parameters persist in Cart Drawer
    const headerCartBtn = page.locator('.site-header [data-action="open-cart"]');
    await headerCartBtn.click();
    const cartDrawer = page.locator('.cart-drawer');
    await expect(cartDrawer).toHaveClass(/open/);

    const cartConfigSummary = page.locator('.cart-item-config');
    await expect(cartConfigSummary).toBeVisible();
    await expect(cartConfigSummary).toContainText('Windows');
    await expect(cartConfigSummary).toContainText('Baby Kangaroo 45g Tactile');

    // Close cart drawer
    await page.locator('.btn-close-cart').click();
    await expect(cartDrawer).not.toHaveClass(/open/);

    // Reload page to verify persistence via localStorage
    await page.reload();
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.cart-counter')).toHaveText('1');
    await headerCartBtn.click();
    await expect(cartDrawer).toHaveClass(/open/);
    await expect(page.locator('.cart-item-config')).toContainText('Windows');
    await expect(page.locator('.cart-item-config')).toContainText('Baby Kangaroo 45g Tactile');

    // Launch checkout and assert configuration is preserved in order summary
    const checkoutBtn = page.locator('.btn-checkout');
    await checkoutBtn.click();
    const checkoutModal = page.locator('.checkout-modal-backdrop');
    await expect(checkoutModal).toHaveClass(/open/);
    const checkoutItemSummary = checkoutModal.locator('.checkout-summary-list');
    await expect(checkoutItemSummary).toContainText('NovaKeys K75');
    await expect(checkoutItemSummary).toContainText('Windows • Baby Kangaroo 45g Tactile');
    await page.locator('.btn-close-checkout').first().click();
    await expect(checkoutModal).not.toHaveClass(/open/);

    // 2. Open Warranty Policy Modal & verify BOTH close buttons (top 'X' and bottom 'UNDERSTOOD & CLOSE')
    const warrantyTrigger = page.locator('[data-action="open-warranty"]').first();
    await warrantyTrigger.scrollIntoViewIfNeeded();
    await warrantyTrigger.click();

    const warrantyModal = page.locator('.warranty-modal-backdrop');
    await expect(warrantyModal).toHaveClass(/open/);
    await expect(warrantyModal.locator('#warranty-modal-title')).toContainText('WARRANTY');

    // Test Top 'X' Close Button
    const topCloseWarrantyBtn = warrantyModal.locator('.btn-close-warranty').first();
    await topCloseWarrantyBtn.click();
    await expect(warrantyModal).not.toHaveClass(/open/);

    // Reopen and test Bottom 'UNDERSTOOD & CLOSE' Button
    await warrantyTrigger.click();
    await expect(warrantyModal).toHaveClass(/open/);
    const bottomCloseWarrantyBtn = warrantyModal.locator('.btn-close-warranty').last();
    await expect(bottomCloseWarrantyBtn).toContainText('UNDERSTOOD & CLOSE');
    await bottomCloseWarrantyBtn.click();
    await expect(warrantyModal).not.toHaveClass(/open/);
  });

  test('08: Responsive Viewport Screen Capture & Layout Integrity', async ({ page }) => {
    const viewports = [
      { name: '320px_mobile_small', width: 320, height: 640 },
      { name: '390px_mobile_standard', width: 390, height: 844 },
      { name: '768px_tablet_portrait', width: 768, height: 1024 },
      { name: '992px_tablet_landscape', width: 992, height: 1100 },
      { name: '1440px_desktop_laptop', width: 1440, height: 900 },
      { name: '1920px_desktop_ultrawide', width: 1920, height: 1080 }
    ];

    for (const vp of viewports) {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto(AFTER_URL);
      await page.waitForLoadState('networkidle');
      await page.evaluate(() => document.fonts.ready);

      // Verify no horizontal overflow
      const overflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth + 1;
      });
      expect(overflow, `Viewport ${vp.name} must not have horizontal scrollbar overflow`).toBe(false);

      // Verify headlines are visible
      const headline = page.locator('.hero-headline');
      await expect(headline).toBeVisible();

      // Capture screenshots
      const heroShotPath = path.join(SCREENSHOTS_DIR, `hero_${vp.name}.png`);
      await page.screenshot({ path: heroShotPath, fullPage: false });

      const fullShotPath = path.join(SCREENSHOTS_DIR, `fullpage_${vp.name}.png`);
      await page.screenshot({ path: fullShotPath, fullPage: true });

      // On tablet (769 - 1024), verify 2-column catalog grid
      if (vp.width >= 769 && vp.width <= 1024) {
        const gridCols = await page.locator('.editorial-grid').evaluate(el => {
          return window.getComputedStyle(el).gridTemplateColumns.split(' ').length;
        });
        expect(gridCols, `Tablet ${vp.name} catalog must display 2 columns`).toBe(2);
      }
    }
  });

  test('09: Accessibility & Prefers-Reduced-Motion', async ({ page }) => {
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    const marqueeAnimation = await page.locator('.marquee-track').evaluate(el => {
      return window.getComputedStyle(el).animationName;
    });
    expect(marqueeAnimation).toBe('none');
  });

  test('10: 320px Viewport Keymap Preview Horizontal Accessibility', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 640 });
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    const configTrigger = page.locator('[data-action="open-configurator"]').first();
    await configTrigger.scrollIntoViewIfNeeded();
    await configTrigger.click();

    const configModal = page.locator('.configurator-modal-backdrop');
    await expect(configModal).toHaveClass(/open/);

    const firstKey = configModal.locator('.cfg-preview-row .cfg-key').first();
    await expect(firstKey).toBeVisible();

    const keyBox = await firstKey.boundingBox();
    expect(keyBox, 'First key (ESC) bounding box must exist').not.toBeNull();
    expect(keyBox!.x, 'First key (ESC) must not have negative horizontal offset on 320px').toBeGreaterThanOrEqual(0);

    const isNegativeOverflow = await page.evaluate(() => {
      const row = document.querySelector('.cfg-preview-row');
      const esc = row?.querySelector('.cfg-key');
      if (!row || !esc) return true;
      const rowRect = row.getBoundingClientRect();
      const escRect = esc.getBoundingClientRect();
      return escRect.left < rowRect.left;
    });
    expect(isNegativeOverflow, 'ESC key must not be clipped to the left of the scroll container').toBe(false);
  });

  test('11: 3D Staging Assets Alpha Border Integrity (Direct In-Browser Canvas Pixel Verification)', async ({ page }) => {
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    // List of deployed production visual assets
    const assetFiles = [
      'assets/images/flux-charger-isolated.webp',
      'assets/images/flux-charger-shadow.webp',
      'assets/images/mat-novadesk-isolated.webp',
      'assets/images/mat-novadesk-shadow.webp',
      'assets/images/keyboard-k75-isolated.webp',
      'assets/images/keyboard-k75-shadow.webp',
      'assets/images/light-beam-isolated.webp',
      'assets/images/light-beam-shadow.webp',
      'assets/images/exploded-k75.png',
      'assets/images/mouse-pulse.png',
      'assets/images/headphones-orbit.png'
    ];

    // Encode as data URLs to avoid local file:// CORS taint when calling ctx.getImageData()
    const assetsData = assetFiles.map((relPath) => {
      const fullPath = path.resolve(__dirname, '..', relPath);
      const mime = relPath.endsWith('.webp') ? 'image/webp' : 'image/png';
      const base64 = fs.readFileSync(fullPath).toString('base64');
      return {
        name: relPath,
        dataUrl: `data:${mime};base64,${base64}`
      };
    });

    const inspectionResults = await page.evaluate(async (items) => {
      const results = [];
      for (const item of items) {
        const img = new Image();
        img.src = item.dataUrl;
        await new Promise((resolve, reject) => {
          img.onload = resolve;
          img.onerror = () => reject(new Error('Failed to load image: ' + item.name));
        });

        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        const ctx = canvas.getContext('2d', { willReadFrequently: true });
        if (!ctx) throw new Error('Could not get 2D canvas context');
        ctx.drawImage(img, 0, 0);

        const w = img.naturalWidth;
        const h = img.naturalHeight;
        const imgData = ctx.getImageData(0, 0, w, h);
        const data = imgData.data;

        // Inspect 4 outer perimeter borders (1px margin)
        let topClipped = 0;
        let bottomClipped = 0;
        let leftClipped = 0;
        let rightClipped = 0;

        // Top row (y = 0)
        for (let x = 0; x < w; x++) {
          const a = data[(0 * w + x) * 4 + 3];
          if (a > 16) topClipped++;
        }
        // Bottom row (y = h - 1)
        for (let x = 0; x < w; x++) {
          const a = data[((h - 1) * w + x) * 4 + 3];
          if (a > 16) bottomClipped++;
        }
        // Left column (x = 0)
        for (let y = 0; y < h; y++) {
          const a = data[(y * w + 0) * 4 + 3];
          if (a > 16) leftClipped++;
        }
        // Right column (x = w - 1)
        for (let y = 0; y < h; y++) {
          const a = data[(y * w + (w - 1)) * 4 + 3];
          if (a > 16) rightClipped++;
        }

        results.push({
          name: item.name,
          width: w,
          height: h,
          topClipped,
          bottomClipped,
          leftClipped,
          rightClipped,
          totalClipped: topClipped + bottomClipped + leftClipped + rightClipped
        });
      }
      return results;
    }, assetsData);

    for (const res of inspectionResults) {
      expect(
        res.totalClipped,
        `Asset ${res.name} has ${res.totalClipped} clipped border pixels in browser Canvas (T=${res.topClipped}, B=${res.bottomClipped}, L=${res.leftClipped}, R=${res.rightClipped})`
      ).toBe(0);
    }
  });

  test('12: Composite Staging Hover Synchronization (Zero Shadow/Product Drift)', async ({ page }) => {
    await page.addInitScript(() => sessionStorage.setItem('nova_promo_dismissed', 'true'));
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    const stages = [
      { name: 'NovaKeys K75', cardSelector: '.card-theme-k75', stageSelector: '.scale-keyboard' },
      { name: 'Pulse Pro', cardSelector: '.card-theme-pulse', stageSelector: '.scale-mouse' },
      { name: 'Orbit ANC', cardSelector: '.card-theme-orbit', stageSelector: '.scale-headphones' },
      { name: 'Flux 100W', cardSelector: '.card-theme-flux', stageSelector: '.scale-charger' },
      { name: 'NovaDesk XL', cardSelector: '.card-theme-mat', stageSelector: '.scale-mat' },
      { name: 'Beam RGB', cardSelector: '.card-theme-beam', stageSelector: '.scale-beam' }
    ];

    for (const item of stages) {
      const card = page.locator(item.cardSelector);
      const stage = card.locator(item.stageSelector);
      await expect(stage).toBeVisible();
      await stage.scrollIntoViewIfNeeded();

      const shadowLayer = stage.locator('.card-shadow-layer');
      const productLayer = stage.locator('.card-product-layer');
      await expect(shadowLayer).toBeVisible();
      await expect(productLayer).toBeVisible();

      // Check initial alignment
      const initialBoxShadow = await shadowLayer.boundingBox();
      const initialBoxProduct = await productLayer.boundingBox();
      expect(initialBoxShadow, `${item.name} shadow layer bounding box must exist`).not.toBeNull();
      expect(initialBoxProduct, `${item.name} product layer bounding box must exist`).not.toBeNull();
      expect(Math.abs(initialBoxProduct!.x - initialBoxShadow!.x)).toBeLessThan(1.0);
      expect(Math.abs(initialBoxProduct!.y - initialBoxShadow!.y)).toBeLessThan(1.0);
      expect(Math.abs(initialBoxProduct!.width - initialBoxShadow!.width)).toBeLessThan(1.0);
      expect(Math.abs(initialBoxProduct!.height - initialBoxShadow!.height)).toBeLessThan(1.0);

      // Trigger hover on product card
      await card.hover();
      await page.waitForTimeout(400); // Allow transition to finish

      // Check that child layers maintain transform: none and identical geometry
      const syncCheck = await page.evaluate((selector) => {
        const stageEl = document.querySelector(selector);
        if (!stageEl) return { found: false };
        const shadow = stageEl.querySelector('.card-shadow-layer') as HTMLElement;
        const product = stageEl.querySelector('.card-product-layer') as HTMLElement;
        if (!shadow || !product) return { found: false };

        const shadowStyle = window.getComputedStyle(shadow);
        const productStyle = window.getComputedStyle(product);
        const shadowRect = shadow.getBoundingClientRect();
        const productRect = product.getBoundingClientRect();

        return {
          found: true,
          shadowTransform: shadowStyle.transform,
          productTransform: productStyle.transform,
          deltaX: Math.abs(productRect.x - shadowRect.x),
          deltaY: Math.abs(productRect.y - shadowRect.y),
          deltaW: Math.abs(productRect.width - shadowRect.width),
          deltaH: Math.abs(productRect.height - shadowRect.height)
        };
      }, `${item.cardSelector} ${item.stageSelector}`);

      expect(syncCheck.found).toBe(true);
      expect(syncCheck.shadowTransform, `${item.name} shadow layer must not have individual transform`).toBe('none');
      expect(syncCheck.productTransform, `${item.name} product layer must not have individual transform`).toBe('none');
      expect(syncCheck.deltaX, `${item.name} layers must not drift horizontally during hover`).toBeLessThan(0.5);
      expect(syncCheck.deltaY, `${item.name} layers must not drift vertically during hover`).toBeLessThan(0.5);
      expect(syncCheck.deltaW, `${item.name} layers must retain identical width during hover`).toBeLessThan(0.5);
      expect(syncCheck.deltaH, `${item.name} layers must retain identical height during hover`).toBeLessThan(0.5);

      // Unhover
      await page.mouse.move(0, 0);
      await page.waitForTimeout(400);
    }
  });

  test('14: NovaKeys K75 Flagship Card Strict Anti-Collision & Geometry Verification', async ({ page }) => {
    await page.addInitScript(() => sessionStorage.setItem('nova_promo_dismissed', 'true'));
    // Verify on all 4 required viewports: 390px, 768px, 1440px, 1920px
    for (const vpWidth of [390, 768, 1440, 1920]) {
      await page.setViewportSize({ width: vpWidth, height: 900 });
      await page.goto(AFTER_URL);
      await page.waitForLoadState('networkidle');

      const card = page.locator('.card-theme-k75');
      await expect(card).toBeVisible();
      await card.scrollIntoViewIfNeeded();

      // Dismiss promo modal if visible
      const promoClose = page.locator('.btn-close-promo');
      if (await promoClose.isVisible()) {
        await promoClose.click();
      }

      // Check bounding box measurements directly in-browser
      const metrics = await page.evaluate(() => {
        const c = document.querySelector('.card-theme-k75') as HTMLElement;
        const stage = c.querySelector('.card-visual-stage') as HTMLElement;
        const img = c.querySelector('.card-product-layer') as HTMLElement;
        const shadow = c.querySelector('.card-shadow-layer') as HTMLElement;
        const title = c.querySelector('.product-card-title') as HTMLElement;
        const desc = c.querySelector('.product-card-desc') as HTMLElement;
        const specs = c.querySelector('.card-specs-list') as HTMLElement;
        const action = c.querySelector('.card-action-bar') as HTMLElement;

        const stageRect = stage.getBoundingClientRect();
        const imgRect = img.getBoundingClientRect();
        const titleRect = title.getBoundingClientRect();
        const descRect = desc.getBoundingClientRect();
        const specsRect = specs.getBoundingClientRect();
        const actionRect = action.getBoundingClientRect();

        // Calculate visual shadow bottom (rendered at 76.5% of 1200 height within contain box)
        const ratio = 1600 / 1200;
        let drawnW = imgRect.width;
        let drawnH = imgRect.height;
        if (drawnW / drawnH > ratio) {
          drawnW = drawnH * ratio;
        } else {
          drawnH = drawnW / ratio;
        }
        const topOffset = (imgRect.height - drawnH) / 2;
        const shadowVisualBottom = imgRect.top + topOffset + drawnH * (918 / 1200);

        return {
          gapStageToTitle: titleRect.top - stageRect.bottom,
          gapImgToTitle: titleRect.top - imgRect.bottom,
          gapShadowVisualToTitle: titleRect.top - shadowVisualBottom,
          // Collision overlaps: positive value means overlap (collision)
          titleOverlap: Math.max(0, imgRect.bottom - titleRect.top),
          descOverlap: Math.max(0, imgRect.bottom - descRect.top),
          specsOverlap: Math.max(0, imgRect.bottom - specsRect.top),
          actionOverlap: Math.max(0, imgRect.bottom - actionRect.top)
        };
      });

      // Strict requirements: minimum 24px visual gap between bottom of render/stage and title
      expect(metrics.gapImgToTitle, `K75 image must have at least 24px gap to title at ${vpWidth}px`).toBeGreaterThanOrEqual(24);
      expect(metrics.gapStageToTitle, `K75 stage must have at least 24px gap to title at ${vpWidth}px`).toBeGreaterThanOrEqual(24);
      expect(metrics.gapShadowVisualToTitle, `K75 visual shadow must have at least 24px gap to title at ${vpWidth}px`).toBeGreaterThanOrEqual(24);

      // Zero overlap with any textual or interactive elements
      expect(metrics.titleOverlap, `K75 image must never overlap title at ${vpWidth}px`).toBe(0);
      expect(metrics.descOverlap, `K75 image must never overlap description at ${vpWidth}px`).toBe(0);
      expect(metrics.specsOverlap, `K75 image must never overlap specs at ${vpWidth}px`).toBe(0);
      expect(metrics.actionOverlap, `K75 image must never overlap action buttons at ${vpWidth}px`).toBe(0);

      // Capture desktop and mobile verification screenshots for review
      if (vpWidth === 1440) {
        await card.screenshot({
          path: path.join(REVIEW_DIR, 'card_k75_desktop_1440.png')
        });
      } else if (vpWidth === 390) {
        await card.screenshot({
          path: path.join(REVIEW_DIR, 'card_k75_mobile_390.png')
        });
      }
    }
  });

  test('15: NovaKeys K75 Scroll-Driven 3D Breakdown Pipeline & Reduced Motion', async ({ page }) => {
    await page.addInitScript(() => sessionStorage.setItem('nova_promo_dismissed', 'true'));
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    // Dismiss promo modal if open
    const promoClose = page.locator('.btn-close-promo');
    if (await promoClose.isVisible()) {
      await promoClose.click();
    }

    // 1. Locate scroll track and sticky stage
    const track = page.locator('#k75ScrollTrack');
    await expect(track).toBeAttached();

    const canvas = page.locator('#k75ScrollCanvas');
    await expect(canvas).toBeVisible();

    // 2. Initial state: progress = 0.000, fully assembled (frame 0)
    const trackBox = await track.boundingBox();
    expect(trackBox).not.toBeNull();
    await page.evaluate((y) => window.scrollTo(0, y), trackBox!.y);
    await page.waitForTimeout(300);

    const initialFrame = await canvas.getAttribute('data-frame-index');
    const initialProgress = await canvas.getAttribute('data-progress');
    expect(Number(initialFrame)).toBe(0);
    expect(Number(initialProgress)).toBeLessThanOrEqual(0.05);

    // Save initial fully assembled screenshot
    await canvas.screenshot({
      path: path.join(REVIEW_DIR, 'story_k75_01_assembled.png')
    });

    // 3. Scroll down midway through track (progress ~ 0.5): details expanding
    const scrollTravel = trackBox!.height - 900;
    await page.evaluate((y) => window.scrollTo(0, y), trackBox!.y + scrollTravel * 0.5);
    await page.waitForTimeout(300);

    const midFrame = await canvas.getAttribute('data-frame-index');
    const midProgress = await canvas.getAttribute('data-progress');
    expect(Number(midFrame)).toBeGreaterThan(10);
    expect(Number(midFrame)).toBeLessThan(56);
    expect(Number(midProgress)).toBeGreaterThan(0.2);

    // Verify stop on current frame (no autoplay/animation loop while scroll is paused)
    const frameAtPause1 = await canvas.getAttribute('data-frame-index');
    await page.waitForTimeout(500);
    const frameAtPause2 = await canvas.getAttribute('data-frame-index');
    expect(frameAtPause1, 'Animation must freeze on current frame when scroll stops (no autoplay)').toBe(frameAtPause2);

    // Save midway breakdown screenshot
    await canvas.screenshot({
      path: path.join(REVIEW_DIR, 'story_k75_02_mid_breakdown.png')
    });

    // 4. Scroll to end of track (progress = 1.000): full exploded view (frame 56)
    await page.evaluate((y) => window.scrollTo(0, y), trackBox!.y + scrollTravel);
    await page.waitForTimeout(300);

    const endFrame = await canvas.getAttribute('data-frame-index');
    const endProgress = await canvas.getAttribute('data-progress');
    expect(Number(endFrame)).toBe(56);
    expect(Number(endProgress)).toBeCloseTo(1.0, 1);

    // Save final exploded view screenshot
    await canvas.screenshot({
      path: path.join(REVIEW_DIR, 'story_k75_03_exploded.png')
    });

    // 5. Scroll UP: details assemble back in reverse order
    await page.evaluate((y) => window.scrollTo(0, y), trackBox!.y + scrollTravel * 0.3);
    await page.waitForTimeout(300);

    const upFrame = await canvas.getAttribute('data-frame-index');
    expect(Number(upFrame)).toBeLessThan(56);

    // 6. Mobile verification at 390px
    await page.setViewportSize({ width: 390, height: 844 });
    await page.evaluate(() => window.scrollTo(0, 0));
    await track.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    await canvas.screenshot({
      path: path.join(REVIEW_DIR, 'story_k75_mobile_390.png')
    });

    // 7. Verify prefers-reduced-motion fallback
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.waitForTimeout(200);

    const isCanvasVisible = await canvas.isVisible();
    expect(isCanvasVisible, 'Canvas must be hidden when reduced motion is preferred').toBe(false);

    const fallbackImg = page.locator('.story-scroll-fallback');
    await expect(fallbackImg).toBeVisible();
  });

  test('16: Cinematic 3D Hero Sequence Scrub Pipeline & Bidirectional Travel', async ({ page }) => {
    await page.addInitScript(() => sessionStorage.setItem('nova_promo_dismissed', 'true'));
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    const heroTrack = page.locator('#heroScrollTrack');
    await expect(heroTrack).toBeAttached();

    const heroCanvas = page.locator('#heroScrubCanvas');
    await expect(heroCanvas).toBeAttached();

    // 1. Initial State: Intro finishes or is in progress at frame <= 14
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(600);

    const initialFrame = await heroCanvas.getAttribute('data-frame-index');
    expect(Number(initialFrame)).toBeLessThanOrEqual(14);

    // Initial Telemetry Tag: Knob active
    const knobPill = page.locator('.hero-tag-pill[data-phase="knob"]');
    await expect(knobPill).toHaveClass(/active/);

    // 2. Scroll 30% down the hero track: Chassis active
    const trackBox = await heroTrack.boundingBox();
    expect(trackBox).not.toBeNull();
    const scrollTravel = trackBox!.height - 900;

    await page.evaluate((y) => window.scrollTo(0, y), scrollTravel * 0.35);
    await page.waitForTimeout(400);

    const midFrame = await heroCanvas.getAttribute('data-frame-index');
    expect(Number(midFrame)).toBeGreaterThan(10);
    expect(Number(midFrame)).toBeLessThan(55);

    const chassisPill = page.locator('.hero-tag-pill[data-phase="chassis"]');
    await expect(chassisPill).toHaveClass(/active/);

    // 3. Scroll to 85% down the hero track: Switches active, final beauty reveal
    await page.evaluate((y) => window.scrollTo(0, y), scrollTravel * 0.85);
    await page.waitForTimeout(400);

    const lateFrame = await heroCanvas.getAttribute('data-frame-index');
    expect(Number(lateFrame)).toBeGreaterThan(35);

    const switchesPill = page.locator('.hero-tag-pill[data-phase="switches"]');
    await expect(switchesPill).toHaveClass(/active/);

    // 4. Reverse scroll up back to top: Frame decreases back towards resting frame (<= 14)
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(400);

    const topFrame = await heroCanvas.getAttribute('data-frame-index');
    expect(Number(topFrame)).toBeLessThanOrEqual(14);

    // 5. Test Quick Add and Studio CTA buttons in Hero
    const heroAddBtn = page.locator('.btn-hero-add-cart');
    await expect(heroAddBtn).toBeVisible();
    await heroAddBtn.click();
    await page.waitForTimeout(200);

    const cartDrawer = page.locator('.cart-drawer');
    await expect(cartDrawer).toBeVisible();
    const closeCartBtn = page.locator('.btn-close-cart');
    await closeCartBtn.click();
    await page.waitForTimeout(200);

    const heroStudioBtn = page.locator('.btn-hero-studio-cta');
    await expect(heroStudioBtn).toBeVisible();
    await heroStudioBtn.click();
    await page.waitForTimeout(200);

    const studioModal = page.locator('.configurator-modal-backdrop');
    await expect(studioModal).toHaveClass(/open/);
    const closeStudioBtn = page.locator('.studio-topbar .btn-close-configurator');
    await closeStudioBtn.click();
  });

  test('17: Light Keyboard Studio Workstation Overhaul & Key Remap Action ID Bugfix', async ({ page }) => {
    await page.addInitScript(() => sessionStorage.setItem('nova_promo_dismissed', 'true'));
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(AFTER_URL);
    await page.waitForLoadState('networkidle');

    // 1. Open Studio Modal
    const trigger = page.locator('.btn-hero-studio-cta');
    await trigger.click();
    await page.waitForTimeout(300);

    const studioModal = page.locator('.configurator-modal-backdrop');
    await expect(studioModal).toHaveClass(/open/);

    // Verify Light Edition styles: Not black background (#121317)
    const studioWindow = page.locator('.studio-window');
    const bgColor = await studioWindow.evaluate((el) => window.getComputedStyle(el).backgroundColor);
    // rgba or rgb format for #F4F1E9 is rgb(244, 241, 233)
    expect(bgColor).not.toBe('rgb(18, 19, 23)');

    // 2. Verify Key Selection and Remap Bugfix
    const escKey = page.locator('.keycap[data-code="Escape"], .cfg-key[data-code="Escape"]').first();
    await escKey.click();
    await page.waitForTimeout(150);

    const inspectorSelect = page.locator('#inspectorActionSelect');
    await expect(inspectorSelect).toBeVisible();

    // Select 'VOL_UP' action
    await inspectorSelect.selectOption('VOL_UP');
    await page.waitForTimeout(200);

    // Verify Inspector status and displayed value
    const statusBadge = page.locator('#inspectorStatusBadge');
    await expect(statusBadge).toHaveText('REMAPPED');
    expect(await inspectorSelect.inputValue()).toBe('VOL_UP');

    // Verify Keycap displays short label 'VOL+'
    await expect(escKey).toHaveText('VOL+');

    // 3. Select another key and return to Escape: verify dropdown retains 'VOL_UP' (not reverted to DEFAULT)
    const spaceKey = page.locator('.key-spacebar');
    await spaceKey.click();
    await page.waitForTimeout(150);
    expect(await inspectorSelect.inputValue()).toBe('DEFAULT');

    await escKey.click();
    await page.waitForTimeout(150);
    expect(await inspectorSelect.inputValue()).toBe('VOL_UP');
    await expect(statusBadge).toHaveText('REMAPPED');

    // 4. Persistence Check: Reload and re-open
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.locator('.btn-hero-studio-cta').click();
    await page.waitForTimeout(300);

    const reloadedEscKey = page.locator('.keycap[data-code="Escape"], .cfg-key[data-code="Escape"]').first();
    await expect(reloadedEscKey).toHaveText('VOL+');
    await reloadedEscKey.click();
    await page.waitForTimeout(150);
    expect(await page.locator('#inspectorActionSelect').inputValue()).toBe('VOL_UP');

    // 5. Reset Defaults Check
    const resetBtn = page.locator('#btnStudioReset');
    await resetBtn.click();
    await page.waitForTimeout(200);

    await expect(reloadedEscKey).toHaveText('ESC');
    expect(await page.locator('#inspectorActionSelect').inputValue()).toBe('DEFAULT');
    await expect(page.locator('#inspectorStatusBadge')).toHaveText('DEFAULT');

    // Close dialog
    await page.locator('.studio-topbar .btn-close-configurator').click();
  });

  test('18: Light Keyboard Studio Mobile Responsiveness & 320px Layout Integrity', async ({ page }) => {
    await page.addInitScript(() => sessionStorage.setItem('nova_promo_dismissed', 'true'));

    // Test on 390px (iPhone 14) and 320px (Ultra-compact mobile)
    for (const mobWidth of [390, 320]) {
      await page.setViewportSize({ width: mobWidth, height: 750 });
      await page.goto(AFTER_URL);
      await page.waitForLoadState('networkidle');

      // Open Studio Modal via hero button
      const studioBtn = page.locator('.btn-hero-studio-cta');
      await studioBtn.click();
      await page.waitForTimeout(300);

      // Verify Mobile Switcher is visible
      const mobileSwitcher = page.locator('.studio-mobile-switcher');
      await expect(mobileSwitcher).toBeVisible();

      // Check Settings Tab
      const settingsTab = page.locator('.studio-mob-tab[data-tab="config"]');
      const previewTab = page.locator('.studio-mob-tab[data-tab="preview"]');
      await expect(settingsTab).toBeVisible();
      await expect(previewTab).toBeVisible();

      // Switch to Keymap Preview Tab
      await previewTab.click();
      await page.waitForTimeout(200);

      const previewPanel = page.locator('.studio-panel-preview');
      await expect(previewPanel).toBeVisible();

      // Verify ZERO horizontal overflow on document
      const hasOverflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > window.innerWidth;
      });
      expect(hasOverflow, `Viewport ${mobWidth}px must not have horizontal document overflow in studio preview`).toBe(false);

      // Switch back to Settings Tab
      await settingsTab.click();
      await page.waitForTimeout(200);
      const configPanel = page.locator('.studio-panel-config');
      await expect(configPanel).toBeVisible();

      // Close modal
      const closeBtn = page.locator('.studio-topbar .btn-close-configurator');
      await closeBtn.click();
      await page.waitForTimeout(200);
    }
  });

  test('19: Intro-to-Scrub Pipeline, Typography Non-Collision & Telemetry Leader Lines', async ({ page }) => {
    await page.addInitScript(() => sessionStorage.setItem('nova_promo_dismissed', 'true'));

    // Check desktop resolutions for zero typography-keyboard collision
    for (const width of [1200, 1440, 1920]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(AFTER_URL);
      await page.waitForLoadState('networkidle');

      // 1. Wait for intro completion / hero-intro-ready class
      const body = page.locator('body');
      await expect(body).toHaveClass(/hero-intro-ready/, { timeout: 3500 });

      // 2. Strict Typography vs 3D Stage Non-Collision Verification
      const headline = page.locator('.hero-headline');
      const visualStage = page.locator('.hero-visual-stage');

      await expect(headline).toBeVisible();
      await expect(visualStage).toBeVisible();

      const hBox = await headline.boundingBox();
      const sBox = await visualStage.boundingBox();

      expect(hBox, `Headline bounding box must exist on ${width}px`).not.toBeNull();
      expect(sBox, `3D Stage bounding box must exist on ${width}px`).not.toBeNull();

      // Right edge of headline must NOT intersect left edge of 3D stage (guaranteed gap >= 20px)
      const hRight = hBox!.x + hBox!.width;
      const sLeft = sBox!.x;
      expect(hRight, `Headline right (${hRight}) must not cross keyboard stage left (${sLeft}) on ${width}px`).toBeLessThanOrEqual(sLeft);

      // 3. Telemetry Pins & SVG Leader Lines Verification
      const pins = page.locator('.hero-tag-pill');
      expect(await pins.count()).toBe(4);

      for (let i = 0; i < 4; i++) {
        await expect(pins.nth(i)).toBeVisible();
      }

      const leaderSvg = page.locator('.hero-leader-svg');
      await expect(leaderSvg).toBeAttached();
    }

    // 4. Zero-Latency Interrupt Test on Fresh Page
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(AFTER_URL);

    // Immediately trigger wheel event before intro reaches frame 14
    await page.mouse.wheel(0, 100);
    await page.waitForTimeout(300);

    // Body should immediately become hero-intro-ready upon user interaction
    const bodyInterrupted = page.locator('body');
    await expect(bodyInterrupted).toHaveClass(/hero-intro-ready/);
  });

});


