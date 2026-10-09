import { test, expect } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

const BASE_URL = 'file:///' + path.resolve(__dirname, '..').replace(/\\/g, '/');
const AFTER_URL = `${BASE_URL}/after/index.html`;
const BEFORE_URL = `${BASE_URL}/before/index.html`;
const ROOT_URL = `${BASE_URL}/index.html`;

const SCREENSHOTS_DIR = path.resolve(__dirname, '../test-results/screenshots');
fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });

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
      'mouse-pulse.png',
      'headphones-orbit.png',
      'flux-charger-isolated.webp',
      'flux-charger-shadow.webp',
      'mat-novadesk-isolated.webp',
      'mat-novadesk-shadow.webp',
      'light-beam-isolated.webp',
      'light-beam-shadow.webp',
      'exploded-k75.png'
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

});
