# NOVA Gear — Frontend Bug Fix Case Study

A high-end editorial e-commerce portfolio case study demonstrating realistic frontend debugging, responsive architectural repair, and production-grade Vanilla JavaScript engineering.

---

## 1. The Project

**NOVA Gear** is a premium direct-to-consumer (DTC) hardware brand specializing in precision mechanical keyboards, ultra-low latency wireless mice, audiophile noise-cancelling headphones, and architecturally considered workstation accessories.

The visual direction is inspired by contemporary editorial commerce (such as [Collider](https://www.drinkcollider.com/)): massive fluid headlines, stark asymmetrical compositions, tactile material palettes, wide color surfaces with WCAG AA compliance, and zero generic startup clutter.

This repository demonstrates two iterations of the exact same product campaign:
- **`BEFORE` (`/before/`):** A client-grade build with 18 realistic HTML, CSS, and JavaScript bugs that degrade usability, break mobile viewports, and cause runtime console exceptions.
- **`AFTER` (`/after/`):** The fully repaired, production-grade implementation engineered with fluid CSS math (`clamp()`), accessible dialog management, persistent state handling, and zero third-party dependencies.

---

## 2. Verified Defect Matrix (18 Client Bugs)

| # | Дефект (Problem) | Как воспроизвести в BEFORE (Reproduction) | Исправление в AFTER (Fix Applied) | Проверка в AFTER (Verification) |
|---|---|---|---|---|
| **01** | **Horizontal Overflow on Mobile** | Открыть на экране 320–390px; страница скроллится вправо до 1250px из-за жесткого `width: 1200px` у контейнера Hero. | Заменено на fluid container с `max-width: var(--container-max)`, `margin: 0 auto` и `padding: clamp(...)`. | `scrollWidth === clientWidth` на 320px, 375px, 390px; горизонтальный скролл полностью отсутствует. |
| **02** | **Hero 3D Product Overlap** | На мобильных экранах клавиатура с `position: absolute; width: 800px;` перекрывает текст заголовка `BETTER GEAR. BETTER DAYS.`. | Разделены позиционирование и параллакс; на экранах `<992px` визуал переходит в естественный поток документа ниже текста. | Текст заголовка и 3D-рендер полностью видимы и не конфликтуют на всех разрешениях. |
| **03** | **Rigid Oversized Headline** | Заголовок имеет жесткий `font-size: 118px;`, из-за чего слова вылезают за границы экрана на планшетах и смартфонах. | Внедрена флюидная типографика `font-size: clamp(3rem, 8.5vw, 8.5rem);` с отрицательным трекингом. | Текст пропорционально сжимается от 320px до 4K без разрыва строк и выпадения за вьюпорт. |
| **04** | **Broken Mobile Navigation** | На мобильных экранах десктопные ссылки сбиваются в кашу; кнопка бургера не открывает меню. | Добавлен медиа-запрос скрытия десктопных ссылок и полноэкранный доступный оверлей с управлением фокусом. | Клик по бургеру открывает оверлей, блокирует скролл body; закрывается по крестику, Escape и клику по ссылкам. |
| **05** | **Rigid Product Grid on Mobile** | Колонки каталога имеют фиксированные доли `65%` и `35%` без `flex-wrap`, превращая карточки на телефонах в сплющенные полосы. | Добавлен `flex-wrap: wrap;` и перестроение колонок в `flex: 0 0 100%` ниже 992px. | Карточки плавно перестраиваются в единую удобную вертикальную ленту на мобильных устройствах. |
| **06** | **Image Width Blowout** | Рендер Flux 100W имеет жесткий `width: 700px` без `max-width: 100%`, ломая соседние карточки. | Установлено глобальное правило `img { max-width: 100%; height: auto; }` и индивидуальные размерные классы. | Картинка масштабируется внутри карточки без распирания родительских флекс-контейнеров. |
| **07** | **Broken Card Baseline Alignment** | Длинное описание в карточке Orbit ANC выталкивает блок цены и кнопки вниз относительно соседней карточки. | Внедрен flexbox-каркас с `display: flex; flex-direction: column;` и `margin-top: auto` у блока цен и кнопок. | Блоки цены и кнопок выровнены по нижнему краю карточек независимо от объема текста. |
| **08** | **Broken "Add to Cart" Selector** | В HTML кнопка имеет `class="add-cart"`, а JS ищет `document.querySelectorAll('.add-to-cart')`. Клик ничего не делает. | Синхронизированы классы, внедрен Event Delegation на документ с чтением `data-id`. | Клик по кнопке любого товара добавляет товар в корзину и вызывает всплывающий toast. |
| **09** | **Console Runtime Crash on Cart** | Клик по иконке корзины ищет `.cart-panel`, а реальный элемент — `.cart-drawer`. В консоли падает `Uncaught TypeError`. | Заменен селектор на `.cart-drawer`, добавлена проверка наличия и ARIA-атрибуты. | Ноль ошибок в консоли; корзина плавно выдвигается справа. |
| **10** | **Newsletter Page Reload Bug** | Отправка формы рассылки перезагружает страницу из-за отсутствия `e.preventDefault()`, принимая пустые строки. | Добавлен `e.preventDefault()`, проверка regex и вывод честного демо-сообщения. | Страница не перезагружается; валидация отсекает пустые и некорректные адреса. |
| **11** | **Fixed Header Content Clipping** | Хедер имеет `position: fixed; height: 80px`, а секция Hero — `padding-top: 30px`. Верхний заголовок заезжает под плашку. | Хедер переведен в `position: sticky; top: 0;`, Hero рассчитан с учетом высоты вьюпорта. | Верхняя строка заголовка не перекрывается хедерами ни в статике, ни при скролле. |
| **12** | **Broken Promo Modal Close Trigger** | В разметке крестик имеет `class="btn-close-modal"`, а скрипт слушает `.modal-close-trigger`. Модалку невозможно закрыть. | Селекторы синхронизированы; добавлено закрытие по клику на оверлей, клавише Escape и копирование кода в буфер. | Модалка надежно закрывается всеми тремя способами; кнопка копирует промокод с визуальным подтверждением. |
| **13** | **Fixed 1000px Footer Grid** | Сетка футера жестко зафиксирована на `width: 1000px; grid-template-columns: 500px 250px 250px;`, ломая мобильный экран. | Переведена на адаптивный CSS Grid (`grid-template-columns: 2fr 1fr 1fr 1fr` на десктопе, 1 колонка на мобильном). | Футер аккуратно перестраивается в компактный столбец на 320–768px без бокового скролла. |
| **14** | **Jump-to-Top Anchor Links** | CTA-ссылки используют пустой `href="#"`, из-за чего клик дергает страницу на самый верх (`scroll(0,0)`). | Заменены на валидные семантические якоря (`#products`, `#statement`, `#journal`, `#support`). | Клик плавно прокручивает страницу к соответствующей секции. |
| **15** | **Runaway Hover Scale Collision** | При наведении на товар изображение масштабируется `scale(1.18)` при `overflow: visible`, наползая на текст и соседние карточки. | Установлен `overflow: hidden;` на карточках и сбалансированный микро-скейл `scale(1.03) rotate(0.8deg)`. | Визуал аккуратно реагирует на курсор, не нарушая границ сетки и читаемости текста. |
| **16** | **Missing Overflow Protection** | В CSS задано `body { overflow-x: visible; }`, из-за чего любой микросдвиг элементов раздувает страницу. | Внедрено `overflow-x: hidden;` для `body` и контейнеров. | Страница защищена от случайных паразитных субпиксельных переполнений. |
| **17** | **Broken Review Slider Previous Button** | Кнопка «Вперед» работает, а для «Назад» скрипт слушает `.slider-prev-btn` вместо `.btn-slider-prev`. | Исправлен селектор кнопки; добавлен единый циклический переключатель с мягким переходом. | Отзывы перелистываются в обе стороны плавно и без сбоев. |
| **18** | **Layout Sizing Breakage on Resize** | Скрипт рассчитывает размеры один раз в `window.onload` и жестко зашивает инлайновые пиксели, ломаясь при ресайзе. | Фиксированные инлайн-размеры удалены; сетка опирается на нативный CSS; параллакс привязан к `requestAnimationFrame`. | Окно можно свободно ресайзить между мобильным и 4K режимами без перезагрузки страницы. |

---

## 3. Новая предметная 3D-графика

Вместо плоских двухмерных векторных схем проект оснащен фотореалистичными рендерами промышленного дизайна:
1. **NovaKeys K75:** Изометрический 3D-рендер 75% клавиатуры в анодированном алюминиевом корпусе CNC 6063 с латунным поворотным энкодером, PBT кейкапами и акцентными клавишами.
2. **Pulse Pro:** Эргономичная беспроводная мышь 8KHz с текстурированным матовым корпусом, оптическими переключателями и кольцевой синей подсветкой колеса.
3. **Orbit ANC:** Беспроводные наушники с оголовьем из шлифованного алюминия, амбушюрами из пены с эффектом памяти и оранжевыми фасками.
4. **Flux 100W:** Компактный GaN III блок питания с акцентной желтой полосой и прецизионными портами (2x USB-C, 1x USB-A).
5. **NovaDesk XL:** Премиальный войлочный коврик 900x400мм с микропрострочкой и кожаным органайзером кабелей.
6. **Beam RGB:** Алюминиевая лампа для монитора с асимметричным отражателем, сенсорным управлением и мягким светораспределением.
7. **Exploded View K75:** Технический послойный чертеж клавиатуры на темном фоне (верхний корпус, плейт FR4, PCB, звукопоглощающий Poron, латунный груз) с доступной легендой.

---

## 4. Интерактивные возможности AFTER

- **Корзина:** по умолчанию пустая, реактивное добавление/удаление, счетчик, сумма, хранение в `localStorage`, кнопка «Reset Demo State».
- **Демо-чекаут:** кнопка оформления заблокирована при пустой корзине; при заполненной открывает модальное окно с перечнем товаров и дисклеймером об отсутствии списания средств.
- **Локальный поиск:** мгновенная фильтрация по каталогу, названиям и характеристикам с возможностью очистки и обработкой пустого результата.
- **Быстрый просмотр (Quick View):** модальное окно с характеристиками, материалами и добавлением товара.
- **Доступность (A11y):** фокус-ловушка (Focus Trap), возврат фокуса на инициатор, блокировка фонового контента через `inert`, поддержка `prefers-reduced-motion`.

---

## 5. Запуск и проверка

Откройте `index.html` в браузере (Chrome / Edge / Firefox / Safari). Интерактивная витрина позволяет переключаться между `AFTER` и `BEFORE`, а также тестировать поведение на эмуляторах разрешений:
- `320px` (iPhone SE)
- `390px` (iPhone 14/15)
- `768px` (iPad Portrait)
- `100%` (Desktop / 1440px / 1920px)
