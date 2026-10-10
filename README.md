# NOVA Gear — Architectural Hardware & Interactive 3D Showcase

[![Live Demo](https://img.shields.io/badge/LIVE%20DEMO-fen3211.github.io%2Fnova--gear-critical?style=for-the-badge&logo=githubpages&logoColor=white&color=C7FF3D&labelColor=151515)](https://fen3211.github.io/nova-gear/)
[![Vanilla JS](https://img.shields.io/badge/JavaScript-Vanilla%20ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Canvas 60 FPS](https://img.shields.io/badge/Canvas-60%2F120%20FPS%20Scrub-blueviolet?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
[![Lenis Scroll](https://img.shields.io/badge/Scroll-Lenis%20Smooth%20Momentum-black?style=for-the-badge)](https://github.com/darkroomengineering/lenis)
[![Blender Cycles](https://img.shields.io/badge/3D%20Pipeline-Blender%20Cycles-EA7600?style=for-the-badge&logo=blender&logoColor=white)](https://www.blender.org/)
[![Playwright 100% Pass](https://img.shields.io/badge/E2E%20Tests-20%2F20%20PASS%20(100%25)-brightgreen?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)

> **🔴 [LAUNCH LIVE DEMO IN BROWSER](https://fen3211.github.io/nova-gear/)**

A cinematic, editorial direct-to-consumer (DTC) showcase crafted for premium tactile hardware. Inspired by cutting-edge digital ateliers and modern spatial commerce (e.g. *Collider*), NOVA Gear unifies an ultra-smooth 56-frame interactive 3D rotation, real-time hardware telemetry leader lines, bespoke editorial product staging, and an in-browser interactive mechanical keyboard studio.

---

## English Overview

### 1. Key Features & Creative Highlights

- **Cinematic Hero Orbit (Unified Momentum Physics)**
  - 56-frame photorealistic 3D sequence rendered in Blender Cycles, optimized to **2.17 MB total** via compressed modern WebP.
  - Zero Canvas Clipping guarantee: scaled via `SAFE_SCALE = 0.82` (18% margin) ensuring the keyboard geometry never collides with canvas edges at any rotation angle.
  - Unified momentum loop driven by continuous damping lerp:
    $$\text{currentFrame} += (\text{targetFrame} - \text{currentFrame}) \times 0.08$$
  - Seamless fly-in intro (frames 0–14) with `easeOutQuart` impulse (1100ms) with zero-latency interruption on wheel, touch, scroll, or keyboard navigation.
  - Clean separation: editorial headline *BETTER GEAR. BETTER DAYS.* is constrained within the left column with an air gap of over 40px to eliminate visual collisions.

- **Anatomical Telemetry Callouts**
  - Frame-synchronized hardware callouts with dynamic 1px SVG leader lines and 4px contact target dots (`#C7FF3D`):
    - **CNC 6063 ANODIZED**: active on frames `0–18`.
    - **BRASS ROTARY ENCODER**: active on frames `10–26`.
    - **LINEAR 45G // 3.8MM**: active on frames `12–30`.
    - **FR4 GASKET ACOUSTICS**: active on frames `24–42`.
  - Smooth fade-in/fade-out transitions (`cubic-bezier(0.16, 1, 0.3, 1)`) with zero layout clutter during beauty product reveals.

- **Light Keyboard Studio v2.4 (Workstation Simulator)**
  - Interactive tactile keyboard workstation featuring Mac/Windows layouts, switch audio synthesizer (TTC Linear, Baby Kangaroo Tactile, Silent White), and per-key layer remapping.
  - Built-in Web Audio API mechanical sound synthesis with realistic high-frequency contact clicks and low-frequency case resonance.
  - Persistent state management via `localStorage` with full keyboard accessibility (focus traps, Esc handling, aria-expanded sync).
  - Responsive layout down to ultra-compact 320px mobile viewports with dedicated tab switches and zero horizontal document overflow.

- **Editorial Product Catalog**
  - Bespoke product cards custom-proportioned for each piece of hardware (NovaKeys K75, Pulse Pro 8KHz Mouse, Orbit ANC Headphones, Flux 100W GaN Charger, NovaDesk XL Felt Mat, Beam RGB Monitor Light).
  - Dual-layer composite staging with synchronized hover perspective transitions and independent soft shadow occlusion.

### 2. Performance & Architecture

- **Zero-Dependency Core:** Pure Vanilla JavaScript (ES6+), semantic HTML5, and native CSS3 Grid/Flexbox with fluid math (`clamp()`).
- **Featherweight Asset Footprint:** Hero 3D assets total only **2.17 MB**; full website assets under **18 MB**.
- **High-DPI Retina Rendering:** Adaptive `devicePixelRatio` scaling with offscreen memory cleanup and progressive batch preloading.
- **Automated QA Coverage:** 20 comprehensive Playwright E2E tests validating layout integrity, accessibility, touch/keyboard interactions, and alpha border integrity.

---

## Русская версия (Russian Overview)

### 1. Архитектурные и визуальные особенности

- **Кинематографичный 3D Hero с единым импульсом (Unified Momentum)**
  - 56-кадровая фотореалистичная последовательность вращения K75, отрендеренная в Blender Cycles и оптимизированная в WebP (**2.17 МБ на все кадры**).
  - Безопасное масштабирование `SAFE_SCALE = 0.82` (18% поля), полностью исключающее обрезание граней клавиатуры при любых углах вращения.
  - Единая математическая модель физики с фактором демпфирования `0.08` — плавный скраббинг без ступенек и рывков.
  - Мягкий стартовый запуск (кадры 0–14, 1100 мс `easeOutQuart`) с мгновенным подхватом управления при любом действии пользователя (колесо мыши, свайп, клавиши).
  - Типографическая чистота: крупный заголовок *BETTER GEAR. BETTER DAYS.* гарантированно отделен воздушным зазором от 3D-модели.

- **Анатомическая аппаратная телеметрия**
  - Динамические аппаратные выноски, появляющиеся и исчезающие строго в своих диапазонах кадров:
    - **CNC 6063 ANODIZED**: кадры `0–18`.
    - **BRASS ROTARY ENCODER**: кадры `10–26`.
    - **LINEAR 45G // 3.8MM**: кадры `12–30`.
    - **FR4 GASKET ACOUSTICS**: кадры `24–42`.
  - Компактные 1px SVG-линии указателей, контактные точки 4px `#C7FF3D`, минималистичные бейджи `#151515` и мягкие переходы прозрачности `0.35s cubic-bezier(0.16, 1, 0.3, 1)`.

- **NOVA Keyboard Studio v2.4 (Светлая рабочая станция)**
  - Полнофункциональный конфигуратор 75% клавиатуры: переключение раскладок macOS / Windows, выбор свитчей, переназначение клавиш (Layer 0–3) с сохранением в `localStorage`.
  - Встроенный синтезатор акустики свитчей через Web Audio API (реалистичный звук механики без внешних MP3/WAV файлов).
  - Безупречная адаптивность: на экранах 320–390px интерфейс переключается в режим вкладок (Preview / Settings) с нулевым горизонтальным скроллом.

- **Редакторский каталог девайсов**
  - Индивидуальная сетка карточек под геометрию каждого устройства (мышь Pulse Pro, наушники Orbit ANC, зарядка Flux 100W, коврик NovaDesk XL, лампа Beam RGB).
  - Раздельные слои теней и предметов с плавной синхронизацией при ховере.

### 2. Технические показатели

| Показатель | Значение |
|---|---|
| **Стек** | Vanilla JS (ES6+), CSS3 Grid/Flexbox, HTML5, Lenis Scroll |
| **Вес 3D Hero последовательности** | **2.17 МБ** (56 кадров WebP) |
| **Общий вес ассетов сайта** | **~17.8 МБ** (оптимизировано с 261 МБ) |
| **FPS Canvas Scrub** | Стабильные 60 / 120 FPS |
| **Тестовое покрытие** | 20 E2E-тестов Playwright (100% Pass) |
| **Доступность** | WCAG AA контраст, WAI-ARIA диалоги, поддержка `prefers-reduced-motion` |

---

## Quickstart & Local Installation (Локальный запуск)

### Требования
- Node.js 18+
- Современный браузер (Chrome, Firefox, Safari, Edge)

### 1. Клонирование и установка зависимостей
```bash
git clone https://github.com/fen3211/nova-gear.git
cd nova-gear
npm install
```

### 2. Запуск локального сервера
```bash
npx serve
# или откройте index.html напрямую в браузере / через расширение Live Server в VS Code
```

### 3. Запуск автоматизированных E2E тестов Playwright
```bash
npx playwright test
```

### 4. Запись демонстрационного видео Hero
```bash
node scripts/record_hero_cinematic.js
```

---

## Structure (Структура проекта)

```text
nova-gear/
├── assets/
│   ├── frames_hero/     # 56 WebP кадров 3D последовательности Hero (2.17 MB)
│   ├── frames_scrub/    # 57 WebP кадров послойной разборки K75 (1.46 MB)
│   ├── icons/           # Векторный фавикон и пиктограммы
│   └── images/          # Высокодетализированные продуктовые рендеры и тени
├── review/              # Верификационные скриншоты и MP4 демонстрации
├── scripts/             # Скрипты генерации видео (Playwright + FFmpeg)
├── tests/               # 20 автоматизированных тестов Playwright
├── index.html           # Продакшен разметка сайта
├── script.js            # Основная бизнес-логика, физический движок и Studio
├── style.css            # Токены, сетки, типографика и анимации
├── lenis.min.js         # Инерционный плавный скроллинг
├── package.json         # Зависимости тестирования
└── README.md            # Презентация проекта
```

---

## License & Credits

Designed and developed by **fen3211**. Released under the [MIT License](LICENSE).
Live deployment: [https://fen3211.github.io/nova-gear/](https://fen3211.github.io/nova-gear/)
