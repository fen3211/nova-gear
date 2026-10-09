/**
 * NOVA GEAR — Master Production Client Script (AFTER)
 * Fully Accessible, Zero-Dependency, State-Driven Vanilla JavaScript
 */

(function () {
  'use strict';

  /* --------------------------------------------------------------------------
     1. PRODUCT CATALOG DATA
     -------------------------------------------------------------------------- */
  const PRODUCTS = [
    {
      id: 'k75',
      name: 'NovaKeys K75',
      category: 'Mechanical Keyboard',
      price: 129,
      image: '../assets/images/keyboard-k75.png',
      theme: 'card-theme-k75',
      badge: '01 // FLAGSHIP',
      desc: '75% gasket-mounted CNC 6063 aluminum chassis with custom lubricated linear switches.',
      specs: 'FR4 GASKET • TTC 45G LINEAR • 1,850G BRASS WEIGHT • 2.4GHZ / BT / TYPE-C',
      details: {
        chassis: '6063 Anodized CNC Aluminum with micro-chamfers',
        mount: 'FR4 flex-cut plate with poron gasket socks',
        switches: 'Custom factory-lubed linear switches (45g operating force)',
        connectivity: 'Tri-mode: 2.4GHz (1000Hz), Bluetooth 5.2, USB-C',
        weight: '1,850g with mirror-polished internal brass bar',
        keycaps: 'Double-shot PBT Cherry profile (1.5mm wall thickness)'
      }
    },
    {
      id: 'pulse',
      name: 'Pulse Pro',
      category: 'Wireless Mouse',
      price: 79,
      image: '../assets/images/mouse-pulse.png',
      theme: 'card-theme-pulse',
      badge: '02 // PRECISION',
      desc: '8,000Hz polling rate ergonomic mouse with optical switches and magnesium wheel.',
      specs: 'PAW3395 26K DPI • 8KHZ POLLING • 58G ULTRA-LIGHT • OPTICAL MICROSWITCHES',
      details: {
        sensor: 'PixArt PAW3395 (26,000 DPI, 650 IPS, 50G acceleration)',
        polling: 'Native 8,000Hz ultra-low latency wireless bridge',
        switches: 'TTC Optical microswitches rated for 70M clicks (zero debounce)',
        scroll: 'Knurled aluminum alloy wheel with tactile optical encoder',
        weight: '58 grams balanced center of gravity without honeycomb holes',
        battery: 'Up to 90 hours continuous usage on single USB-C charge'
      }
    },
    {
      id: 'orbit',
      name: 'Orbit ANC',
      category: 'Wireless Headphones',
      price: 159,
      image: '../assets/images/headphones-orbit.png',
      theme: 'card-theme-orbit',
      badge: '03 // ACOUSTICS',
      desc: 'Hybrid active noise cancellation with 40mm titanium drivers and 48-hour battery.',
      specs: '40MM TITANIUM • -42DB HYBRID ANC • 48H BATTERY • MEMORY FOAM CUSHIONS',
      details: {
        drivers: '40mm custom titanium-coated composite acoustic diaphragms',
        anc: 'Feedforward + Feedback quad-mic hybrid noise reduction (-42dB depth)',
        codecs: 'Sony LDAC 24-bit/96kHz, AAC, SBC with ultra-low latency audio sync',
        materials: 'Spring steel headband, bead-blasted aluminum yokes, protein leather',
        battery: '48 hours playback (ANC off), 36 hours (ANC on)',
        charging: '10-minute fast charge yields 5 hours continuous playback'
      }
    },
    {
      id: 'flux',
      name: 'Flux 100W',
      category: 'GaN Fast Charger',
      price: 69,
      image: '../assets/images/charger-flux.png',
      theme: 'card-theme-flux',
      badge: '04 // POWER',
      desc: 'Triple-port GaN III architecture engineered to charge a laptop and two devices at once.',
      specs: '100W PD 3.0 • DUAL NAVITAS GAN • 2X USB-C + 1X USB-A • THERMALGUARD 3.0',
      details: {
        technology: 'Dual Navitas GaNFast III power semiconductors',
        ports: '2x USB-C (PD 3.0, PPS 100W max), 1x USB-A (QC 3.0 22.5W max)',
        safety: 'ThermalGuard 3.0 sensor monitoring heat dissipation 80 times/sec',
        efficiency: '94.5% power conversion efficiency with minimal idle draw',
        dimensions: '65 x 65 x 32 mm (40% smaller than legacy 96W brick)',
        plug: 'Folding nickel-plated reinforced brass prongs'
      }
    },
    {
      id: 'novadesk',
      name: 'NovaDesk XL',
      category: 'Desk Mat',
      price: 39,
      image: '../assets/images/mat-novadesk.png',
      theme: 'card-theme-mat',
      badge: '05 // SURFACE',
      desc: 'High-density merino-blend felt with micro-stitched borders and magnetic cable catch.',
      specs: '900 × 400 × 4MM • MERINO-BLEND FELT • VEGAN LEATHER BINDING • ANTI-SLIP BASE',
      details: {
        dimensions: '900 x 400 mm (extra-wide setup coverage)',
        thickness: '4mm dual-density acoustic dampening structure',
        surface: 'High-density merino-wool blend with anti-pilling treatment',
        edge: 'Precision micro-stitched reinforced border flush with mat face',
        cableCatch: 'Full-grain vegan leather corner loop with solid copper rivet',
        backing: 'Natural textured cellular rubber non-slip foundation'
      }
    },
    {
      id: 'beam',
      name: 'Beam RGB',
      category: 'Monitor Light',
      price: 89,
      image: '../assets/images/light-beam.png',
      theme: 'card-theme-beam',
      badge: '06 // ILLUMINATION',
      desc: 'Dual-source asymmetric workstation illumination with CRI 97 daylight reproduction.',
      specs: 'RA>97 CRI • ASYMMETRIC OPTICAL LENS • 2700K-6500K CCT • TOUCH ENDCAPS',
      details: {
        optics: 'Patented 45° asymmetric reflector lens with zero screen glare',
        cri: 'Color Rendering Index Ra > 97 (museum & studio grade color accuracy)',
        colorTemp: 'Stepless adjustment from 2700K (warm amber) to 6500K (cool daylight)',
        controls: 'Capacitive touch sensors on knurled aluminum endcaps',
        backlight: 'Independent ambient soft-glow light strip on top edge',
        mount: 'Weighted gravity counterweight clamp fitting curved & flat monitors'
      }
    }
  ];

  /* --------------------------------------------------------------------------
     2. GLOBAL STATE (PERSISTED LOCALSTORAGE)
     -------------------------------------------------------------------------- */
  const state = {
    cart: loadCartFromStorage(),
    reviews: [
      {
        quote: '“THE FIRST KEYBOARD I ACTUALLY WANT ON MY DESK.”',
        author: 'Alex M.',
        title: 'Verified Buyer'
      },
      {
        quote: '“WEIGHT, SWITCHES, KEYCAP PROFILE — EVERYTHING FEELS OBSESSIVELY TUNED.”',
        author: 'Elena R.',
        title: 'Lead Product Designer'
      },
      {
        quote: '“REPLACED THREE DULL ACCESSORIES WITH GEAR THAT ACTUALLY BRINGS JOY.”',
        author: 'Marcus V.',
        title: 'Creative Director'
      }
    ],
    currentReviewIndex: 0,
    activeDialog: null,
    lastActiveTrigger: null
  };

  function loadCartFromStorage() {
    try {
      const saved = localStorage.getItem('nova_gear_cart');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          const validated = [];
          for (const raw of parsed) {
            if (!raw || typeof raw !== 'object') continue;
            const baseId = raw.baseId || raw.id;
            const prod = PRODUCTS.find(p => p.id === baseId || p.id === raw.id);
            if (!prod) continue;
            const qty = Number(raw.quantity);
            if (!Number.isFinite(qty) || !Number.isInteger(qty) || qty <= 0) continue;
            validated.push({
              id: String(raw.id),
              baseId: prod.id,
              name: prod.name,
              configSummary: raw.configSummary ? String(raw.configSummary) : null,
              customConfig: raw.customConfig && typeof raw.customConfig === 'object' ? raw.customConfig : null,
              price: prod.price,
              image: prod.image,
              quantity: Math.min(qty, 99)
            });
          }
          return validated;
        }
      }
    } catch (e) {
      // Storage unavailable or blocked
    }
    return []; // Cart defaults to empty
  }

  function saveCartToStorage() {
    try {
      localStorage.setItem('nova_gear_cart', JSON.stringify(state.cart));
    } catch (e) {
      // Storage error or quota exceeded ignored
    }
  }

  /* --------------------------------------------------------------------------
     3. DOM SELECTORS
     -------------------------------------------------------------------------- */
  const header = document.querySelector('.site-header');
  const mainContent = document.getElementById('main-content');
  const siteFooter = document.querySelector('.site-footer');

  // Cart
  const cartDrawer = document.querySelector('.cart-drawer');
  const cartBackdrop = document.querySelector('.cart-backdrop');
  const cartToggleBtns = document.querySelectorAll('[data-action="open-cart"]');
  const closeCartBtn = document.querySelector('.btn-close-cart');
  const cartCounter = document.querySelector('.cart-counter');
  const cartItemsContainer = document.querySelector('.cart-body');
  const subtotalEl = document.querySelector('.subtotal-amount');
  const checkoutBtn = document.querySelector('.btn-checkout');
  const resetDemoBtn = document.querySelector('.btn-reset-demo');

  // Mobile Menu
  const mobileMenuBtn = document.querySelector('.btn-mobile-menu');
  const mobileNavOverlay = document.querySelector('.mobile-nav-overlay');
  const closeMobileNavBtn = document.querySelector('.btn-close-mobile-nav');
  const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');

  // Search
  const searchToggleBtns = document.querySelectorAll('[data-action="open-search"]');
  const searchBackdrop = document.querySelector('.search-modal-backdrop');
  const searchInput = document.querySelector('.search-field');
  const searchResultsContainer = document.querySelector('.search-results-list');
  const closeSearchBtn = document.querySelector('.btn-close-search');

  // Quick View Modal
  const quickViewBackdrop = document.querySelector('.quick-view-backdrop');
  const quickViewVisual = document.querySelector('.quick-view-visual');
  const quickViewTitle = document.querySelector('.quick-view-title');
  const quickViewPrice = document.querySelector('.quick-view-price');
  const quickViewDesc = document.querySelector('.quick-view-desc');
  const quickViewSpecsTable = document.querySelector('.quick-view-specs-table');
  const quickViewAddBtn = document.querySelector('.quick-view-add-btn');
  const closeQuickViewBtn = document.querySelector('.btn-close-quick-view');

  // Checkout Demo Modal
  const checkoutModalBackdrop = document.querySelector('.checkout-modal-backdrop');
  const checkoutSummaryList = document.querySelector('.checkout-summary-list');
  const checkoutTotalEl = document.querySelector('.checkout-total-val');
  const closeCheckoutBtn = document.querySelector('.btn-close-checkout');

  // Configurator Modal
  const configuratorBackdrop = document.querySelector('.configurator-modal-backdrop');
  const closeConfiguratorBtn = document.querySelector('.btn-close-configurator');
  const configuratorAddBtn = document.querySelector('.btn-configurator-add-cart');

  // Warranty Policy Modal
  const warrantyBackdrop = document.querySelector('.warranty-modal-backdrop');
  const closeWarrantyBtn = document.querySelector('.btn-close-warranty');

  // Promo Modal
  const promoModalBackdrop = document.querySelector('.modal-backdrop');
  const closeModalBtn = document.querySelector('.btn-close-promo') || (promoModalBackdrop ? promoModalBackdrop.querySelector('.btn-close-modal') : null);
  const copyCodeBtn = document.querySelector('.btn-copy-code');
  const promoCodeText = document.querySelector('.promo-code-text');

  // Newsletter
  const newsletterForm = document.querySelector('.newsletter-form');
  const newsletterInput = document.querySelector('.newsletter-input');
  const newsletterFeedback = document.querySelector('.form-feedback-message');

  // Reviews
  const reviewQuoteEl = document.querySelector('.review-quote');
  const reviewAuthorEl = document.querySelector('.review-author');
  const reviewTitleEl = document.querySelector('.review-title');
  const prevReviewBtn = document.querySelector('.btn-slider-prev');
  const nextReviewBtn = document.querySelector('.btn-slider-next');

  // Toast & Parallax
  const toastContainer = document.querySelector('.toast-container');
  const heroStage = document.querySelector('.hero-parallax-wrapper');

  /* --------------------------------------------------------------------------
     4. ACCESSIBLE DIALOG & FOCUS TRAP ENGINE
     -------------------------------------------------------------------------- */
  function openDialog(dialogWrapper, triggerElement) {
    if (!dialogWrapper) return;
    state.activeDialog = dialogWrapper;
    state.lastActiveTrigger = triggerElement || document.activeElement;

    dialogWrapper.classList.add('open');
    dialogWrapper.setAttribute('aria-hidden', 'false');

    // Make rest of document inert
    if (mainContent) mainContent.setAttribute('inert', '');
    if (header) header.setAttribute('inert', '');
    if (siteFooter) siteFooter.setAttribute('inert', '');

    document.body.style.overflow = 'hidden';
    if (window.__lenis) {
      window.__lenis.stop();
    }

    // Move focus to first focusable element inside dialog
    const focusable = dialogWrapper.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusable.length > 0) {
      setTimeout(() => focusable[0].focus(), 50);
    }
  }

  function closeDialog(dialogWrapper) {
    if (!dialogWrapper) return;
    dialogWrapper.classList.remove('open');
    dialogWrapper.setAttribute('aria-hidden', 'true');

    // Ensure mobile menu button state is synchronized whenever mobile nav closes
    if (dialogWrapper === mobileNavOverlay && mobileMenuBtn) {
      mobileMenuBtn.setAttribute('aria-expanded', 'false');
    }

    // Release inert
    if (mainContent) mainContent.removeAttribute('inert');
    if (header) header.removeAttribute('inert');
    if (siteFooter) siteFooter.removeAttribute('inert');

    document.body.style.overflow = '';
    if (window.__lenis) {
      window.__lenis.start();
    }
    const closingDialog = dialogWrapper;
    state.activeDialog = null;

    // Special case for checkout modal: return focus to visible header cart trigger,
    // not to checkout button inside the closed cart drawer
    if (closingDialog === checkoutModalBackdrop) {
      const headerCartTrigger = document.querySelector('.site-header [data-action="open-cart"]') || document.querySelector('[data-action="open-cart"]');
      if (headerCartTrigger && typeof headerCartTrigger.focus === 'function') {
        headerCartTrigger.focus();
        return;
      }
    }

    // Restore focus to initiator if visible and valid
    if (state.lastActiveTrigger && typeof state.lastActiveTrigger.focus === 'function') {
      const isHidden = state.lastActiveTrigger.offsetParent === null || state.lastActiveTrigger.closest('[aria-hidden="true"]');
      if (!isHidden) {
        state.lastActiveTrigger.focus();
        return;
      }
    }

    // Fallback focus target to maintain accessibility
    const fallback = document.querySelector('.site-header [data-action="open-cart"]') || document.querySelector('.brand-logo');
    if (fallback && typeof fallback.focus === 'function') {
      fallback.focus();
    }
  }

  function handleTrapFocus(e) {
    if (!state.activeDialog || e.key !== 'Tab') return;

    const focusable = state.activeDialog.querySelectorAll('button:not(:disabled), [href], input:not(:disabled), select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusable.length === 0) return;

    const firstEl = focusable[0];
    const lastEl = focusable[focusable.length - 1];

    if (e.shiftKey) {
      if (document.activeElement === firstEl) {
        lastEl.focus();
        e.preventDefault();
      }
    } else {
      if (document.activeElement === lastEl) {
        firstEl.focus();
        e.preventDefault();
      }
    }
  }

  window.addEventListener('keydown', handleTrapFocus);

  /* --------------------------------------------------------------------------
     5. TOAST NOTIFICATION
     -------------------------------------------------------------------------- */
  function showToast(message) {
    if (!toastContainer) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    toast.innerHTML = `
      <span class="toast-dot" aria-hidden="true"></span>
      <span>${message}</span>
    `;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, 3100);
  }

  /* --------------------------------------------------------------------------
     6. CART MANAGEMENT & CHECKOUT FLOW
     -------------------------------------------------------------------------- */
  function updateCartUI() {
    const totalCount = state.cart.reduce((sum, item) => sum + item.quantity, 0);
    const subtotal = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    // Update Counter
    if (cartCounter) {
      cartCounter.textContent = totalCount;
      cartCounter.classList.remove('bump');
      void cartCounter.offsetWidth; // Trigger reflow for snappy animation
      cartCounter.classList.add('bump');
    }

    // Update Subtotal
    if (subtotalEl) {
      subtotalEl.textContent = `$${subtotal.toLocaleString()}`;
    }

    // Update Checkout Button State
    if (checkoutBtn) {
      checkoutBtn.disabled = state.cart.length === 0;
    }

    // Save to storage
    saveCartToStorage();

    // Render Items
    if (!cartItemsContainer) return;

    if (state.cart.length === 0) {
      cartItemsContainer.innerHTML = `
        <div class="cart-empty-state" tabindex="-1">
          <p class="cart-empty-title">YOUR CART IS EMPTY</p>
          <p class="cart-empty-text">Add precision tactile tools to your workspace and experience refined everyday input.</p>
          <button type="button" class="btn-empty-browse" style="margin-top: 1.25rem; font-family: var(--font-heading); font-size: 0.8rem; font-weight: 700; padding: 0.75rem 1.4rem; border-radius: 999px; background: var(--text); color: var(--bg); border: none; cursor: pointer;">EXPLORE PRODUCTS ↗</button>
        </div>
      `;
      const browseBtn = cartItemsContainer.querySelector('.btn-empty-browse');
      if (browseBtn) {
        browseBtn.addEventListener('click', () => {
          closeDialog(cartDrawer);
          if (cartBackdrop) cartBackdrop.classList.remove('open');
          const cat = document.getElementById('products');
          if (cat) cat.scrollIntoView({ behavior: 'smooth' });
        });
      }
      // Guarantee keyboard focus stays inside open cart drawer when last item is removed
      if (cartDrawer && cartDrawer.classList.contains('open')) {
        if (closeCartBtn && typeof closeCartBtn.focus === 'function') {
          closeCartBtn.focus();
        } else if (browseBtn && typeof browseBtn.focus === 'function') {
          browseBtn.focus();
        }
      }
      return;
    }

    // Preserve focused element ID if user clicked + or -
    const activeEl = document.activeElement;
    const activeAction = activeEl ? activeEl.getAttribute('data-action') : null;
    const activeId = activeEl ? activeEl.getAttribute('data-id') : null;

    const itemsHTML = state.cart.map(item => `
      <div class="cart-item" data-id="${item.id}">
        <div class="cart-item-thumb">
          <img src="${item.image}" alt="${item.name}" loading="lazy" />
        </div>
        <div class="cart-item-details">
          <div class="cart-item-name">${item.name}</div>
          ${item.configSummary ? `<div class="cart-item-config" style="font-size: 0.76rem; color: var(--text-muted); margin-top: 0.2rem; font-weight: 500;">${item.configSummary}</div>` : ''}
          <div class="cart-item-price">$${item.price}</div>
          <div class="cart-item-controls">
            <div class="qty-stepper">
              <button type="button" class="btn-qty" data-action="decrease-qty" data-id="${item.id}" aria-label="Decrease quantity for ${item.name}">−</button>
              <span class="qty-val" aria-label="Current quantity ${item.quantity}">${item.quantity}</span>
              <button type="button" class="btn-qty" data-action="increase-qty" data-id="${item.id}" aria-label="Increase quantity for ${item.name}">+</button>
            </div>
            <button type="button" class="btn-remove-item" data-action="remove-item" data-id="${item.id}" aria-label="Remove ${item.name} from cart">Remove</button>
          </div>
        </div>
      </div>
    `).join('');

    cartItemsContainer.innerHTML = `<div class="cart-items-list">${itemsHTML}</div>`;

    // Restore focus so keyboard users don't get kicked out to document body
    if (activeAction && activeId) {
      const nextBtn = cartItemsContainer.querySelector(`[data-action="${activeAction}"][data-id="${activeId}"]`);
      if (nextBtn) nextBtn.focus();
    }
  }

  function addToCart(productId, customConfig = null) {
    const prod = PRODUCTS.find(p => p.id === productId);
    if (!prod) return;

    const cartItemId = customConfig 
      ? `${productId}-${customConfig.os}-${customConfig.switchType}`
      : productId;

    const configSummary = customConfig
      ? `${customConfig.os === 'win' ? 'Windows' : 'macOS'} • ${customConfig.switchLabel || customConfig.switchType}`
      : null;

    const existing = state.cart.find(i => i.id === cartItemId);
    if (existing) {
      existing.quantity += 1;
    } else {
      state.cart.push({
        id: cartItemId,
        baseId: prod.id,
        name: prod.name,
        configSummary: configSummary,
        customConfig: customConfig || null,
        price: prod.price,
        image: prod.image,
        quantity: 1
      });
    }

    updateCartUI();
    const toastLabel = configSummary ? `${prod.name} (${configSummary})` : prod.name;
    showToast(`${toastLabel} added to cart`);
  }

  function initCartListeners() {
    cartToggleBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        openDialog(cartDrawer, btn);
        cartBackdrop.classList.add('open');
      });
    });

    if (closeCartBtn) {
      closeCartBtn.addEventListener('click', () => {
        closeDialog(cartDrawer);
        cartBackdrop.classList.remove('open');
      });
    }

    if (cartBackdrop) {
      cartBackdrop.addEventListener('click', () => {
        closeDialog(cartDrawer);
        cartBackdrop.classList.remove('open');
      });
    }

    if (cartItemsContainer) {
      cartItemsContainer.addEventListener('click', (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;

        const action = btn.getAttribute('data-action');
        const id = btn.getAttribute('data-id');
        if (!id) return;

        const item = state.cart.find(i => i.id === id);
        if (!item) return;

        if (action === 'increase-qty') {
          item.quantity += 1;
          updateCartUI();
        } else if (action === 'decrease-qty') {
          if (item.quantity > 1) {
            item.quantity -= 1;
          } else {
            state.cart = state.cart.filter(i => i.id !== id);
          }
          updateCartUI();
        } else if (action === 'remove-item') {
          state.cart = state.cart.filter(i => i.id !== id);
          updateCartUI();
        }
      });
    }

    // Reset Demo State Button (safely guarded against blocked storage)
    if (resetDemoBtn) {
      resetDemoBtn.addEventListener('click', (e) => {
        e.preventDefault();
        state.cart = [];
        try {
          localStorage.removeItem('nova_gear_cart');
        } catch (storageErr) {
          // Storage blocked or unavailable
        }
        updateCartUI();
        showToast('Cart demo reset to empty state');
      });
    }

    // Add to Cart buttons across the site
    document.addEventListener('click', (e) => {
      const addBtn = e.target.closest('.btn-add-cart');
      if (addBtn) {
        e.preventDefault();
        const id = addBtn.getAttribute('data-id');
        if (id) addToCart(id);
      }
    });

    // Checkout Flow Button
    if (checkoutBtn) {
      checkoutBtn.addEventListener('click', () => {
        if (state.cart.length === 0) return;
        closeDialog(cartDrawer);
        cartBackdrop.classList.remove('open');
        openCheckoutDemoModal();
      });
    }

    updateCartUI();
  }

  function openCheckoutDemoModal() {
    if (!checkoutModalBackdrop) return;
    const subtotal = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    if (checkoutSummaryList) {
      checkoutSummaryList.innerHTML = state.cart.map(i => `
        <li style="display: flex; justify-content: space-between; padding: 0.4rem 0; font-size: 0.9rem; border-bottom: 1px dashed rgba(0,0,0,0.08);">
          <div>
            <div style="font-weight: 600;">${i.name} × ${i.quantity}</div>
            ${i.configSummary ? `<div style="font-size: 0.76rem; color: var(--text-muted);">${i.configSummary}</div>` : ''}
          </div>
          <span style="font-weight: 700;">$${i.price * i.quantity}</span>
        </li>
      `).join('');
    }

    if (checkoutTotalEl) {
      checkoutTotalEl.textContent = `$${subtotal.toLocaleString()}`;
    }

    // Pass visible accessible header cart button so focus never targets closed drawer
    const visibleCartTrigger = document.querySelector('.site-header [data-action="open-cart"]') || document.querySelector('[data-action="open-cart"]');
    openDialog(checkoutModalBackdrop, visibleCartTrigger);
  }

  document.querySelectorAll('.btn-close-checkout').forEach(btn => {
    btn.addEventListener('click', () => closeDialog(checkoutModalBackdrop));
  });

  /* --------------------------------------------------------------------------
     7. PRODUCT DETAIL / QUICK VIEW MODAL
     -------------------------------------------------------------------------- */
  function openQuickView(productId, triggerBtn) {
    const prod = PRODUCTS.find(p => p.id === productId);
    if (!prod || !quickViewBackdrop) return;

    if (quickViewVisual) {
      quickViewVisual.innerHTML = `<img src="${prod.image}" alt="${prod.name}" style="max-height: 280px; width: auto;" />`;
    }
    if (quickViewTitle) quickViewTitle.textContent = prod.name;
    if (quickViewPrice) quickViewPrice.textContent = `$${prod.price}`;
    if (quickViewDesc) quickViewDesc.textContent = prod.desc;

    if (quickViewSpecsTable && prod.details) {
      quickViewSpecsTable.innerHTML = Object.entries(prod.details).map(([key, val]) => `
        <tr>
          <td>${key.toUpperCase()}</td>
          <td>${val}</td>
        </tr>
      `).join('');
    }

    if (quickViewAddBtn) {
      quickViewAddBtn.setAttribute('data-id', prod.id);
      quickViewAddBtn.onclick = () => {
        addToCart(prod.id);
        closeDialog(quickViewBackdrop);
      };
    }

    openDialog(quickViewBackdrop, triggerBtn);
  }

  document.addEventListener('click', (e) => {
    const viewBtn = e.target.closest('.btn-quick-view');
    if (viewBtn) {
      e.preventDefault();
      const id = viewBtn.getAttribute('data-id');
      if (id) openQuickView(id, viewBtn);
    }
  });

  if (closeQuickViewBtn) {
    closeQuickViewBtn.addEventListener('click', () => closeDialog(quickViewBackdrop));
  }

  /* --------------------------------------------------------------------------
     8. INSTANT LOCAL PRODUCT SEARCH
     -------------------------------------------------------------------------- */
  function renderSearchResults(query) {
    if (!searchResultsContainer) return;
    const cleanQuery = query.toLowerCase().trim();

    if (!cleanQuery) {
      searchResultsContainer.innerHTML = `
        <p style="color: var(--text-muted); font-size: 0.9rem; padding: 1rem 0;">
          Start typing to explore mechanical keyboards, audio, and desk accessories.
        </p>
      `;
      return;
    }

    const matches = PRODUCTS.filter(p => 
      p.name.toLowerCase().includes(cleanQuery) ||
      p.category.toLowerCase().includes(cleanQuery) ||
      p.specs.toLowerCase().includes(cleanQuery)
    );

    if (matches.length === 0) {
      searchResultsContainer.innerHTML = '';
      const emptyWrap = document.createElement('div');
      emptyWrap.style.padding = '1.5rem 0';
      emptyWrap.style.textAlign = 'center';

      const emptyTitle = document.createElement('p');
      emptyTitle.style.fontWeight = '700';
      emptyTitle.style.fontFamily = 'var(--font-heading)';
      emptyTitle.style.fontSize = '1.1rem';
      emptyTitle.textContent = `NO GEAR FOUND MATCHING "${query.toUpperCase()}"`;

      const emptyHint = document.createElement('p');
      emptyHint.style.color = 'var(--text-muted)';
      emptyHint.style.fontSize = '0.85rem';
      emptyHint.style.marginTop = '0.35rem';
      emptyHint.textContent = 'Try searching for "Keyboard", "Mouse", "GaN", or "8KHz".';

      emptyWrap.appendChild(emptyTitle);
      emptyWrap.appendChild(emptyHint);
      searchResultsContainer.appendChild(emptyWrap);
      return;
    }

    searchResultsContainer.innerHTML = matches.map(p => `
      <div class="search-result-card">
        <div class="search-result-info">
          <img src="${p.image}" alt="${p.name}" class="search-result-thumb" />
          <div>
            <h4 style="font-family: var(--font-heading); font-size: 1rem; font-weight: 700;">${p.name}</h4>
            <p style="font-size: 0.8rem; color: var(--text-muted);">${p.category} • $${p.price}</p>
          </div>
        </div>
        <button type="button" class="btn-add-cart" data-id="${p.id}" style="padding: 0.5rem 0.95rem; font-size: 0.72rem;">
          ADD TO CART ↗
        </button>
      </div>
    `).join('');
  }

  document.querySelectorAll('[data-action="open-search"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (mobileNavOverlay && mobileNavOverlay.classList.contains('open')) {
        closeDialog(mobileNavOverlay);
        if (mobileMenuBtn) mobileMenuBtn.setAttribute('aria-expanded', 'false');
      }
      openDialog(searchBackdrop, btn);
      if (searchInput) {
        searchInput.value = '';
        renderSearchResults('');
        setTimeout(() => searchInput.focus(), 80);
      }
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      renderSearchResults(e.target.value);
    });
  }

  if (closeSearchBtn) {
    closeSearchBtn.addEventListener('click', () => closeDialog(searchBackdrop));
  }

  /* --------------------------------------------------------------------------
     9. MOBILE MENU
     -------------------------------------------------------------------------- */
  function initMobileMenu() {
    if (mobileMenuBtn) {
      mobileMenuBtn.addEventListener('click', () => {
        openDialog(mobileNavOverlay, mobileMenuBtn);
        mobileMenuBtn.setAttribute('aria-expanded', 'true');
      });
    }

    if (closeMobileNavBtn) {
      closeMobileNavBtn.addEventListener('click', () => {
        closeDialog(mobileNavOverlay);
        if (mobileMenuBtn) mobileMenuBtn.setAttribute('aria-expanded', 'false');
      });
    }

    mobileNavLinks.forEach(link => {
      link.addEventListener('click', () => {
        closeDialog(mobileNavOverlay);
        if (mobileMenuBtn) mobileMenuBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* --------------------------------------------------------------------------
     10. PROMO CODE MODAL & CLIPBOARD API
     -------------------------------------------------------------------------- */
  function initPromoModal() {
    try {
      const seen = sessionStorage.getItem('nova_promo_dismissed');
      if (!seen) {
        setTimeout(() => {
          // Open promo modal after 3.5 seconds if no other modal is currently active
          if (!state.activeDialog) {
            openDialog(promoModalBackdrop, document.body);
          }
        }, 3500);
      }
    } catch (e) {
      // Storage blocked
    }

    if (closeModalBtn) {
      closeModalBtn.addEventListener('click', () => {
        closeDialog(promoModalBackdrop);
        try { sessionStorage.setItem('nova_promo_dismissed', 'true'); } catch (e) {}
      });
    }

    if (promoModalBackdrop) {
      promoModalBackdrop.addEventListener('click', (e) => {
        if (e.target === promoModalBackdrop) {
          closeDialog(promoModalBackdrop);
          try { sessionStorage.setItem('nova_promo_dismissed', 'true'); } catch (e) {}
        }
      });
    }

    if (copyCodeBtn && promoCodeText) {
      copyCodeBtn.addEventListener('click', async () => {
        const code = promoCodeText.textContent.trim();
        let copied = false;
        try {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(code);
            copied = true;
          }
        } catch (err) {
          // Fallback
        }

        if (!copied) {
          try {
            const temp = document.createElement('textarea');
            temp.value = code;
            temp.style.position = 'fixed';
            temp.style.opacity = '0';
            document.body.appendChild(temp);
            temp.select();
            copied = document.execCommand('copy');
            temp.remove();
          } catch (e) {}
        }

        if (copied) {
          copyCodeBtn.textContent = 'CODE COPIED!';
          copyCodeBtn.classList.add('copied');
          showToast('Promo code "WELCOME10" copied to clipboard');
          setTimeout(() => {
            copyCodeBtn.textContent = 'COPY CODE';
            copyCodeBtn.classList.remove('copied');
          }, 2400);
        } else {
          copyCodeBtn.textContent = 'SELECT CODE';
          window.prompt('Copy code manually:', code);
        }
      });
    }
  }

  /* --------------------------------------------------------------------------
     11. REVIEWS SLIDER (BIDIRECTIONAL TRANSITION)
     -------------------------------------------------------------------------- */
  function renderReview() {
    const r = state.reviews[state.currentReviewIndex];
    if (!r || !reviewQuoteEl) return;

    reviewQuoteEl.style.opacity = '0';
    reviewQuoteEl.style.transform = 'translateY(8px)';

    setTimeout(() => {
      reviewQuoteEl.textContent = r.quote;
      if (reviewAuthorEl) reviewAuthorEl.textContent = r.author;
      if (reviewTitleEl) reviewTitleEl.textContent = r.title;
      reviewQuoteEl.style.opacity = '1';
      reviewQuoteEl.style.transform = 'translateY(0)';
    }, 140);
  }

  function initReviewsSlider() {
    if (prevReviewBtn) {
      prevReviewBtn.addEventListener('click', () => {
        state.currentReviewIndex = (state.currentReviewIndex - 1 + state.reviews.length) % state.reviews.length;
        renderReview();
      });
    }

    if (nextReviewBtn) {
      nextReviewBtn.addEventListener('click', () => {
        state.currentReviewIndex = (state.currentReviewIndex + 1) % state.reviews.length;
        renderReview();
      });
    }

    renderReview();
  }

  /* --------------------------------------------------------------------------
     12. NEWSLETTER VALIDATION (HONEST DEMO FEEDBACK)
     -------------------------------------------------------------------------- */
  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function initNewsletter() {
    if (!newsletterForm) return;

    newsletterForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = newsletterInput ? newsletterInput.value.trim() : '';

      if (!val) {
        newsletterFeedback.textContent = 'Please enter your email address.';
        newsletterFeedback.className = 'form-feedback-message error';
        return;
      }

      if (!isValidEmail(val)) {
        newsletterFeedback.textContent = 'Please enter a valid email address.';
        newsletterFeedback.className = 'form-feedback-message error';
        return;
      }

      newsletterFeedback.textContent = "Thanks for testing! (Demo mode: no data stored).";
      newsletterFeedback.className = 'form-feedback-message success';
      if (newsletterInput) newsletterInput.value = '';
    });
  }

  /* --------------------------------------------------------------------------
     13. SMOOTH PARALLAX VIA REQUESTANIMATIONFRAME
     -------------------------------------------------------------------------- */
  function initParallax() {
    // Parallax and perspective tilt are unified into initHeroCinematicInteraction
    // to eliminate conflicting transforms on hero elements.
  }

  /* --------------------------------------------------------------------------
     14. HEADER SCROLL EFFECT
     -------------------------------------------------------------------------- */
  function initHeaderScroll() {
    if (!header) return;
    const handleScroll = () => {
      if (window.scrollY > 30) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
  }

  /* --------------------------------------------------------------------------
     15. GLOBAL ESCAPE KEY LISTENER
     -------------------------------------------------------------------------- */
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && state.activeDialog) {
      const closing = state.activeDialog;
      closeDialog(closing);
      if (cartBackdrop) cartBackdrop.classList.remove('open');
      if (closing === mobileNavOverlay && mobileMenuBtn) {
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
      }
    }
  });

  /* --------------------------------------------------------------------------
     16. INTERACTIVE K75 CONFIGURATOR & WARRANTY MODALS
     -------------------------------------------------------------------------- */
  function playKeyClickSound(switchType) {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      if (ctx.state === 'suspended') ctx.resume();

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();

      let freq = 160;
      let decay = 0.06;
      let filterFreq = 950;
      let filterQ = 2.5;

      if (switchType === 'tactile') {
        freq = 280;
        decay = 0.07;
        filterFreq = 1900;
        filterQ = 4.0;
        // Tactile bump high click
        const clickOsc = ctx.createOscillator();
        const clickGain = ctx.createGain();
        clickOsc.type = 'triangle';
        clickOsc.frequency.setValueAtTime(2400, ctx.currentTime);
        clickOsc.frequency.exponentialRampToValueAtTime(800, ctx.currentTime + 0.015);
        clickGain.gain.setValueAtTime(0.12, ctx.currentTime);
        clickGain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.015);
        clickOsc.connect(clickGain);
        clickGain.connect(ctx.destination);
        clickOsc.start();
        clickOsc.stop(ctx.currentTime + 0.02);
      } else if (switchType === 'silent') {
        freq = 95;
        decay = 0.04;
        filterFreq = 450;
        filterQ = 1.2;
      }

      osc.type = switchType === 'silent' ? 'sine' : 'triangle';
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(45, ctx.currentTime + decay);

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(filterFreq, ctx.currentTime);
      filter.Q.setValueAtTime(filterQ, ctx.currentTime);

      gain.gain.setValueAtTime(0.22, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + decay);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + decay + 0.01);
    } catch (e) {
      // AudioContext unavailable in headless environments
    }
  }

  function initConfiguratorModal() {
    const configuratorTriggers = document.querySelectorAll('[data-action="open-configurator"]');
    let selectedOS = 'mac';
    let selectedSwitch = 'linear';
    let selectedLayer = '0';
    let selectedKeyCode = 'Escape';
    let keyRemaps = {};

    const switchPrices = {
      linear: 129,
      tactile: 144,
      silent: 149
    };

    const switchLabels = {
      linear: 'TTC Linear 45g',
      tactile: 'Baby Kangaroo 45g Tactile',
      silent: 'Silent White 38g'
    };

    // Restore saved settings from localStorage if available
    try {
      const savedConfig = localStorage.getItem('nova_k75_studio_config');
      if (savedConfig) {
        const parsed = JSON.parse(savedConfig);
        if (parsed.os) selectedOS = parsed.os;
        if (parsed.switchType) selectedSwitch = parsed.switchType;
        if (parsed.layer) selectedLayer = parsed.layer;
        if (parsed.remaps && typeof parsed.remaps === 'object') keyRemaps = parsed.remaps;
      }
    } catch (e) {
      // Storage unavailable
    }

    configuratorTriggers.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        openDialog(configuratorBackdrop, btn);
        updateStudioUI();
      });
    });

    if (closeConfiguratorBtn) {
      closeConfiguratorBtn.addEventListener('click', () => closeDialog(configuratorBackdrop));
    }

    if (!configuratorBackdrop) return;

    configuratorBackdrop.addEventListener('click', (e) => {
      if (e.target === configuratorBackdrop) closeDialog(configuratorBackdrop);
    });

    function saveStudioConfig() {
      try {
        localStorage.setItem('nova_k75_studio_config', JSON.stringify({
          os: selectedOS,
          switchType: selectedSwitch,
          layer: selectedLayer,
          remaps: keyRemaps
        }));
      } catch (e) {
        // Storage unavailable
      }
    }

    function updateStudioUI() {
      // 1. OS Controls
      configuratorBackdrop.querySelectorAll('.btn-cfg-os').forEach(b => {
        const isAct = (b.getAttribute('data-os') === selectedOS);
        b.classList.toggle('active', isAct);
        b.setAttribute('aria-pressed', isAct ? 'true' : 'false');
        b.setAttribute('aria-checked', isAct ? 'true' : 'false');
      });

      const optKey = configuratorBackdrop.querySelector('.cfg-key-opt');
      const cmdKey = configuratorBackdrop.querySelector('.cfg-key-cmd');
      if (optKey) optKey.textContent = selectedOS === 'mac' ? 'OPT' : 'WIN';
      if (cmdKey) cmdKey.textContent = selectedOS === 'mac' ? 'CMD' : 'ALT';

      // 2. Switch Controls & Pricing
      configuratorBackdrop.querySelectorAll('.btn-cfg-switch').forEach(b => {
        const isAct = (b.getAttribute('data-switch') === selectedSwitch);
        b.classList.toggle('active', isAct);
        b.setAttribute('aria-pressed', isAct ? 'true' : 'false');
        b.setAttribute('aria-checked', isAct ? 'true' : 'false');
      });

      const priceTag = document.getElementById('studioPriceTag');
      const buildSummary = document.getElementById('studioBuildSummary');
      const curPrice = switchPrices[selectedSwitch] || 129;
      if (priceTag) priceTag.textContent = `$${curPrice}`;
      if (buildSummary) {
        buildSummary.textContent = `75% • ${switchLabels[selectedSwitch] || selectedSwitch} • ${selectedOS === 'mac' ? 'macOS' : 'Windows'}`;
      }

      // 3. Layer Controls & Legend Swapping
      configuratorBackdrop.querySelectorAll('.btn-cfg-layer').forEach(b => {
        const isAct = (b.getAttribute('data-layer') === selectedLayer);
        b.classList.toggle('active', isAct);
        b.setAttribute('aria-pressed', isAct ? 'true' : 'false');
        b.setAttribute('aria-selected', isAct ? 'true' : 'false');
      });

      const layerDesc = configuratorBackdrop.querySelector('.cfg-layer-desc');
      if (layerDesc) {
        if (selectedLayer === '0') {
          layerDesc.textContent = 'LAYER 0: Primary QWERTY & Alpha Navigation (Standard)';
        } else if (selectedLayer === '1') {
          layerDesc.textContent = 'LAYER 1: Media Shortcuts, Volume Knob, Function Keys';
        } else {
          layerDesc.textContent = 'LAYER 2: Bluetooth Devices (1-3), LED Backlight Hue & Macro Trigger';
        }
      }

      // Update layer legends on keyboard
      updateLayerKeyLabels();
    }

    function updateLayerKeyLabels() {
      const allKeyButtons = configuratorBackdrop.querySelectorAll('.keycap, .cfg-key');
      allKeyButtons.forEach(btn => {
        const code = btn.getAttribute('data-code');
        const defaultLabel = btn.getAttribute('data-label') || btn.textContent.trim();

        // Check if explicitly remapped by user
        if (keyRemaps[code]) {
          btn.textContent = keyRemaps[code];
          return;
        }

        // Layer 0: Default layout
        if (selectedLayer === '0') {
          if (code === 'AltLeft') btn.textContent = selectedOS === 'mac' ? 'OPT' : 'WIN';
          else if (code === 'MetaLeft') btn.textContent = selectedOS === 'mac' ? 'CMD' : 'ALT';
          else btn.textContent = defaultLabel;
          return;
        }

        // Layer 1: Media & Navigation
        if (selectedLayer === '1') {
          const layer1Map = {
            'F1': 'DIM-', 'F2': 'DIM+', 'F3': 'EXP', 'F4': 'SRCH',
            'F7': 'PREV', 'F8': 'PLAY', 'F9': 'NEXT',
            'F10': 'MUTE', 'F11': 'VOL-', 'F12': 'VOL+',
            'ArrowUp': 'PGUP', 'ArrowDown': 'PGDN', 'ArrowLeft': 'HOME', 'ArrowRight': 'END'
          };
          if (layer1Map[code]) {
            btn.textContent = layer1Map[code];
            return;
          }
        }

        // Layer 2: Connectivity & RGB
        if (selectedLayer === '2') {
          const layer2Map = {
            'Digit1': 'BT1', 'Digit2': 'BT2', 'Digit3': 'BT3', 'Digit4': '2.4G', 'Digit5': 'USB',
            'KeyQ': 'RGB+', 'KeyW': 'SPD+', 'KeyE': 'HUE+',
            'KeyA': 'RGB-', 'KeyS': 'SPD-', 'KeyD': 'HUE-'
          };
          if (layer2Map[code]) {
            btn.textContent = layer2Map[code];
            return;
          }
        }

        btn.textContent = defaultLabel;
      });
    }

    // OS Toggle Click
    configuratorBackdrop.querySelectorAll('.btn-cfg-os').forEach(btn => {
      btn.addEventListener('click', () => {
        selectedOS = btn.getAttribute('data-os') || 'mac';
        updateStudioUI();
        saveStudioConfig();
      });
    });

    // Switch Selector Click
    configuratorBackdrop.querySelectorAll('.btn-cfg-switch').forEach(btn => {
      btn.addEventListener('click', () => {
        selectedSwitch = btn.getAttribute('data-switch') || 'linear';
        playKeyClickSound(selectedSwitch);
        updateStudioUI();
        saveStudioConfig();
      });
    });

    // Layer Selector Click
    configuratorBackdrop.querySelectorAll('.btn-cfg-layer').forEach(btn => {
      btn.addEventListener('click', () => {
        selectedLayer = btn.getAttribute('data-layer') || '0';
        updateStudioUI();
        saveStudioConfig();
      });
    });

    // Audition Sound Button Click
    const soundDemoBtn = configuratorBackdrop.querySelector('.btn-cfg-sound-demo');
    if (soundDemoBtn) {
      soundDemoBtn.addEventListener('click', () => playKeyClickSound(selectedSwitch));
    }

    // Keycap Click Selection
    const keyButtons = configuratorBackdrop.querySelectorAll('.keycap, .cfg-key, .k75-rotary-knob');
    keyButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        keyButtons.forEach(b => b.classList.remove('key-selected'));
        btn.classList.add('key-selected');

        selectedKeyCode = btn.getAttribute('data-code') || 'Escape';
        const label = btn.getAttribute('data-label') || btn.textContent.trim();

        playKeyClickSound(selectedSwitch);

        // Update Inspector
        const badge = document.getElementById('inspectorKeyBadge');
        const nameEl = document.getElementById('inspectorKeyName');
        const coordEl = document.getElementById('inspectorKeyCoord');
        const statusBadge = document.getElementById('inspectorStatusBadge');
        const selectEl = document.getElementById('inspectorActionSelect');

        if (badge) badge.textContent = label;
        if (nameEl) nameEl.textContent = `${label} Key`;
        if (coordEl) coordEl.textContent = `HID ID: ${selectedKeyCode}`;

        if (keyRemaps[selectedKeyCode]) {
          if (statusBadge) statusBadge.textContent = 'REMAPPED';
          if (selectEl) selectEl.value = keyRemaps[selectedKeyCode];
        } else {
          if (statusBadge) statusBadge.textContent = 'DEFAULT';
          if (selectEl) selectEl.value = 'DEFAULT';
        }
      });
    });

    // Remap Select Action
    const remapSelect = document.getElementById('inspectorActionSelect');
    if (remapSelect) {
      remapSelect.addEventListener('change', () => {
        const val = remapSelect.value;
        const statusBadge = document.getElementById('inspectorStatusBadge');
        const activeBtn = configuratorBackdrop.querySelector(`.keycap[data-code="${selectedKeyCode}"], .cfg-key[data-code="${selectedKeyCode}"], .k75-rotary-knob[data-code="${selectedKeyCode}"]`);

        if (val === 'DEFAULT') {
          delete keyRemaps[selectedKeyCode];
          if (statusBadge) statusBadge.textContent = 'DEFAULT';
          if (activeBtn) activeBtn.textContent = activeBtn.getAttribute('data-label') || selectedKeyCode;
        } else {
          const actionLabels = {
            'MUTE': 'MUTE',
            'PLAY_PAUSE': 'PLAY',
            'VOL_UP': 'VOL+',
            'VOL_DOWN': 'VOL-',
            'SCREENSHOT': 'SHOT',
            'CALCULATOR': 'CALC',
            'MACRO_CLEAR': 'CLEAR'
          };
          const displayLabel = actionLabels[val] || val;
          keyRemaps[selectedKeyCode] = displayLabel;
          if (statusBadge) statusBadge.textContent = 'REMAPPED';
          if (activeBtn) activeBtn.textContent = displayLabel;
        }
        saveStudioConfig();
      });
    }

    // Physical Keyboard Listener
    window.addEventListener('keydown', (e) => {
      if (!configuratorBackdrop.classList.contains('open')) return;
      if (e.key === 'Escape') return; // Handled by global escape modal close

      const matchingKey = configuratorBackdrop.querySelector(`[data-code="${e.code}"]`);
      if (matchingKey) {
        matchingKey.classList.add('key-active');
        playKeyClickSound(selectedSwitch);
        setTimeout(() => matchingKey.classList.remove('key-active'), 120);
      }
    });

    // Reset Defaults Button
    const resetBtn = document.getElementById('btnStudioReset');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        selectedOS = 'mac';
        selectedSwitch = 'linear';
        selectedLayer = '0';
        keyRemaps = {};
        try {
          localStorage.removeItem('nova_k75_studio_config');
        } catch (e) {}
        updateStudioUI();
      });
    }

    // Add to Cart Action
    if (configuratorAddBtn) {
      configuratorAddBtn.addEventListener('click', () => {
        saveStudioConfig();
        addToCart('k75', {
          os: selectedOS,
          switchType: selectedSwitch,
          switchLabel: switchLabels[selectedSwitch] || selectedSwitch,
          layer: selectedLayer,
          remapCount: Object.keys(keyRemaps).length
        });
        closeDialog(configuratorBackdrop);
      });
    }

    // Initialize initial state
    updateStudioUI();
  }

  function initWarrantyModal() {
    const warrantyTriggers = document.querySelectorAll('[data-action="open-warranty"]');
    warrantyTriggers.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        openDialog(warrantyBackdrop, btn);
      });
    });

    document.querySelectorAll('.btn-close-warranty').forEach(btn => {
      btn.addEventListener('click', () => closeDialog(warrantyBackdrop));
    });

    if (warrantyBackdrop) {
      warrantyBackdrop.addEventListener('click', (e) => {
        if (e.target === warrantyBackdrop || e.target.closest('.btn-close-warranty')) {
          closeDialog(warrantyBackdrop);
        }
      });
    }
  }

  /* --------------------------------------------------------------------------
     11. LENIS INERTIAL SMOOTH SCROLL
     -------------------------------------------------------------------------- */
  function initLenisScroll() {
    const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion || typeof window.Lenis !== 'function') return;

    try {
      const lenis = new window.Lenis({
        duration: 1.15,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        orientation: 'vertical',
        gestureOrientation: 'vertical',
        smoothWheel: true,
        wheelMultiplier: 1.0,
        touchMultiplier: 1.5
      });

      window.__lenis = lenis;

      function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
      }
      requestAnimationFrame(raf);
    } catch (e) {
      // Lenis fallback to native scroll
    }
  }

  /* --------------------------------------------------------------------------
     12. CINEMATIC HERO PRESENTATION & INTERACTION
     -------------------------------------------------------------------------- */
  function initHeroCinematicInteraction() {
    const stage = document.getElementById('heroVisualStage');
    const wrapper = document.getElementById('heroParallaxWrapper');
    const heroAddBtn = document.querySelector('.btn-hero-add-cart');
    const scrollIndicator = document.querySelector('.hero-scroll-indicator');
    const heroSection = document.getElementById('hero') || document.querySelector('.hero-section');

    // Quick Add button for NovaKeys K75
    if (heroAddBtn) {
      heroAddBtn.addEventListener('click', () => {
        addToCart('k75', null);
        const cartDrawer = document.querySelector('.cart-drawer');
        if (cartDrawer) openDialog(cartDrawer, heroAddBtn);
      });
    }

    // Scroll indicator click
    if (scrollIndicator) {
      scrollIndicator.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.getElementById('story');
        if (target) {
          if (window.__lenis) {
            window.__lenis.scrollTo(target);
          } else {
            target.scrollIntoView({ behavior: 'smooth' });
          }
        }
      });
    }

    if (!heroSection || !wrapper) return;
    const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    let targetRotX = 0, targetRotY = 0;
    let currentRotX = 0, currentRotY = 0;
    let targetTransX = 0, targetTransY = 0;
    let currentTransX = 0, currentTransY = 0;
    let isTracking = false;

    function renderHeroSpringLoop() {
      currentRotX += (targetRotX - currentRotX) * 0.1;
      currentRotY += (targetRotY - currentRotY) * 0.1;
      currentTransX += (targetTransX - currentTransX) * 0.1;
      currentTransY += (targetTransY - currentTransY) * 0.1;

      wrapper.style.transform = `perspective(1000px) translate3d(${currentTransX.toFixed(2)}px, ${currentTransY.toFixed(2)}px, 0) rotateX(${currentRotX.toFixed(2)}deg) rotateY(${currentRotY.toFixed(2)}deg) translateZ(8px)`;

      const delta = Math.abs(targetRotX - currentRotX) + Math.abs(targetRotY - currentRotY) + Math.abs(targetTransX - currentTransX) + Math.abs(targetTransY - currentTransY);
      if (delta > 0.04) {
        requestAnimationFrame(renderHeroSpringLoop);
      } else {
        isTracking = false;
      }
    }

    const heroTrackTarget = stage || heroSection;
    heroTrackTarget.addEventListener('mousemove', (e) => {
      if (window.innerWidth <= 992) return;
      const rect = heroTrackTarget.getBoundingClientRect();
      const normX = (e.clientX - rect.left) / rect.width - 0.5;
      const normY = (e.clientY - rect.top) / rect.height - 0.5;
      targetRotY = normX * 10;
      targetRotX = -normY * 10;
      targetTransX = normX * 14;
      targetTransY = normY * 14;

      if (!isTracking) {
        isTracking = true;
        requestAnimationFrame(renderHeroSpringLoop);
      }
    });

    heroTrackTarget.addEventListener('mouseleave', () => {
      targetRotX = 0;
      targetRotY = 0;
      targetTransX = 0;
      targetTransY = 0;
      if (!isTracking) {
        isTracking = true;
        requestAnimationFrame(renderHeroSpringLoop);
      }
    });
  }

  /* --------------------------------------------------------------------------
     13. UNIFIED MOTION: CARD SCROLL REVEALS
     -------------------------------------------------------------------------- */
  function initCardScrollReveals() {
    const cards = document.querySelectorAll('.product-card');
    if (!cards.length) return;
    const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      cards.forEach(c => c.classList.add('card-revealed'));
      return;
    }

    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('card-revealed');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

      cards.forEach((card, idx) => {
        card.style.transitionDelay = `${(idx % 2) * 80}ms`;
        observer.observe(card);
      });
    } else {
      cards.forEach(c => c.classList.add('card-revealed'));
    }
  }

  /* --------------------------------------------------------------------------
     14. NOVA KEYS K75 SCROLL-DRIVEN 3D BREAKDOWN PIPELINE
     -------------------------------------------------------------------------- */
  function initK75ScrollBreakdown() {
    const canvas = document.getElementById('k75ScrollCanvas');
    const track = document.getElementById('k75ScrollTrack');
    const phaseTextEl = document.getElementById('k75PhaseText');
    const phaseProgressFillEl = document.getElementById('k75ProgressFill');
    const phasePercentEl = document.getElementById('k75PhasePercent');

    if (!canvas || !track) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const TOTAL_FRAMES = 57;
    const frames = [];
    let currentFrameIndex = -1;
    let targetFrameIndex = 0;
    let ticking = false;

    // Check prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      return; // Static fallback image is rendered via CSS
    }

    function getNearestLoadedFrameIndex(targetIdx) {
      if (frames[targetIdx] && frames[targetIdx].complete && frames[targetIdx].naturalWidth > 0) {
        return targetIdx;
      }
      for (let offset = 1; offset < TOTAL_FRAMES; offset++) {
        const left = targetIdx - offset;
        if (left >= 0 && frames[left] && frames[left].complete && frames[left].naturalWidth > 0) {
          return left;
        }
        const right = targetIdx + offset;
        if (right < TOTAL_FRAMES && frames[right] && frames[right].complete && frames[right].naturalWidth > 0) {
          return right;
        }
      }
      return -1;
    }

    function renderFrame(index) {
      if (index < 0 || index >= TOTAL_FRAMES) return;
      targetFrameIndex = index;
      const frameToDraw = getNearestLoadedFrameIndex(index);
      if (frameToDraw >= 0) {
        const img = frames[frameToDraw];
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        currentFrameIndex = frameToDraw;
        canvas.dataset.frameIndex = String(frameToDraw);
      }
    }

    function updatePhaseBadge(progress) {
      let phase = 'ASSEMBLED CHASSIS // CNC 6063';
      if (progress > 0.85) {
        phase = 'FULL EXPLODED ARCHITECTURE // 1,850G BRASS WEIGHT';
      } else if (progress > 0.60) {
        phase = 'ENIG PCB & PORON FOAM // SOUTH-FACING RGB';
      } else if (progress > 0.35) {
        phase = 'SWITCHES & FR4 PLATE // CUSTOM LUBED LINEAR';
      } else if (progress > 0.15) {
        phase = 'KEYCAP MATRIX // CHERRY PROFILE PBT';
      }

      if (phaseTextEl && phaseTextEl.textContent !== phase) {
        phaseTextEl.textContent = phase;
      }
      if (phaseProgressFillEl) {
        phaseProgressFillEl.style.width = `${(progress * 100).toFixed(1)}%`;
      }
      if (phasePercentEl) {
        phasePercentEl.textContent = `${Math.round(progress * 100)}%`;
      }
    }

    // Preload all 57 optimized WebP scrub frames
    for (let i = 0; i < TOTAL_FRAMES; i++) {
      const img = new Image();
      const padIndex = String(i).padStart(2, '0');
      img.src = `../assets/frames_scrub/k75_scrub_${padIndex}.webp`;
      img.onload = () => {
        if (i === 0 && currentFrameIndex === -1) {
          renderFrame(0);
        } else if (i === targetFrameIndex && currentFrameIndex !== targetFrameIndex) {
          renderFrame(targetFrameIndex);
        }
      };
      frames.push(img);
    }

    function updateScrollBreakdown() {
      const trackRect = track.getBoundingClientRect();
      const scrollHeight = trackRect.height - window.innerHeight;
      if (scrollHeight <= 0) return;

      // Calculate progress: 0 when track top reaches top of viewport, 1 when scroll reaches end
      const rawProgress = -trackRect.top / scrollHeight;
      const progress = Math.max(0, Math.min(1, rawProgress));
      canvas.dataset.progress = progress.toFixed(3);

      updatePhaseBadge(progress);

      // Calculate target frame: 0 (fully assembled) to 56 (fully exploded)
      const targetFrame = Math.min(TOTAL_FRAMES - 1, Math.max(0, Math.round(progress * (TOTAL_FRAMES - 1))));

      if (targetFrame !== currentFrameIndex) {
        renderFrame(targetFrame);
      }
    }

    function onScrollOrResize() {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          updateScrollBreakdown();
          ticking = false;
        });
        ticking = true;
      }
    }

    window.addEventListener('scroll', onScrollOrResize, { passive: true });
    window.addEventListener('resize', onScrollOrResize, { passive: true });

    if (window.__lenis) {
      window.__lenis.on('scroll', onScrollOrResize);
    }

    // Initial render
    renderFrame(0);
    updateScrollBreakdown();
  }

  /* --------------------------------------------------------------------------
     BOOTSTRAP
     -------------------------------------------------------------------------- */
  document.addEventListener('DOMContentLoaded', () => {
    initLenisScroll();
    initHeaderScroll();
    initCartListeners();
    initMobileMenu();
    initConfiguratorModal();
    initWarrantyModal();
    initPromoModal();
    initReviewsSlider();
    initNewsletter();
    initParallax();
    initHeroCinematicInteraction();
    initCardScrollReveals();
    initK75ScrollBreakdown();
  });
})();
