/**
 * NOVA GEAR — BEFORE (BUGGY CLIENT SCRIPT)
 * Contains 18 realistic, demonstrable bugs for portfolio comparison.
 */

window.onload = function () {
  // DEFECT 18: Layout sizing statically set on window.onload, breaking dynamically on resize
  const heroCanvas = document.querySelector('.hero-poster-canvas');
  if (heroCanvas) {
    const staticW = heroCanvas.offsetWidth;
    // Forcing static inline pixel width on child container
    heroCanvas.style.minWidth = staticW + 'px';
  }

  // DEFECT 9: Looking for non-existent '.cart-panel' instead of '.cart-drawer'
  // Causes Uncaught TypeError: Cannot read properties of null (reading 'style') in console!
  const cartIcon = document.querySelector('[data-action="open-cart"]');
  if (cartIcon) {
    cartIcon.addEventListener('click', function () {
      const panel = document.querySelector('.cart-panel');
      panel.style.display = 'block'; // Throws TypeError!
      document.querySelector('.cart-backdrop').style.display = 'block';
    });
  }

  // DEFECT 8: Query selector mismatch (queries '.add-to-cart', HTML has class 'add-cart')
  const addButtons = document.querySelectorAll('.add-to-cart');
  addButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      alert('Added to cart!');
    });
  });

  // DEFECT 10: Missing e.preventDefault() on newsletter form submit
  const newsletterForm = document.querySelector('.newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function () {
      // Missing e.preventDefault() -> instantly reloads page, accepts empty emails!
    });
  }

  // DEFECT 12: Manual trigger for Bug 12 promo modal demo
  const triggerModalBtn = document.querySelector('.btn-trigger-promo-demo');
  if (triggerModalBtn) {
    triggerModalBtn.addEventListener('click', function () {
      const modal = document.querySelector('.modal-backdrop');
      if (modal) modal.style.display = 'flex';
    });
  }

  // DEFECT 12: Broken close button selector (queries '.modal-close-trigger', HTML has '.btn-close-modal')
  const closeModalBtn = document.querySelector('.modal-close-trigger');
  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', function () {
      document.querySelector('.modal-backdrop').style.display = 'none';
    });
  }

  // DEFECT 17: Review slider Next works, but Previous button selector is broken
  const reviews = [
    { quote: '“THE FIRST KEYBOARD I ACTUALLY WANT ON MY DESK.”', author: 'Alex M.' },
    { quote: '“WEIGHT, SWITCHES, KEYCAP PROFILE — EVERYTHING FEELS OBSESSIVELY TUNED.”', author: 'Elena R.' },
    { quote: '“REPLACED THREE DULL ACCESSORIES WITH GEAR THAT ACTUALLY BRINGS JOY.”', author: 'Marcus V.' }
  ];
  let currentIdx = 0;

  const nextBtn = document.querySelector('.btn-slider-next');
  if (nextBtn) {
    nextBtn.addEventListener('click', function () {
      currentIdx = (currentIdx + 1) % reviews.length;
      document.querySelector('.review-quote').textContent = reviews[currentIdx].quote;
      document.querySelector('.review-author').textContent = reviews[currentIdx].author;
    });
  }

  // Broken selector: looking for '.slider-prev-btn' instead of '.btn-slider-prev'
  const prevBtn = document.querySelector('.slider-prev-btn');
  if (prevBtn) {
    prevBtn.addEventListener('click', function () {
      currentIdx = (currentIdx - 1 + reviews.length) % reviews.length;
      document.querySelector('.review-quote').textContent = reviews[currentIdx].quote;
      document.querySelector('.review-author').textContent = reviews[currentIdx].author;
    });
  }
};
