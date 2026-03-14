# MzansiWins Style Guide

A single reference for all formatting, design, and editorial rules across the site.

---

## Colour Palette

| Token                 | Light Mode           | Dark Mode                          |
|-----------------------|----------------------|------------------------------------|
| `--accent`            | `#1641B4`            | same                               |
| `--accent-hover`      | `#1233A0`            | same                               |
| `--accent-light`      | `#EEF2FF`            | `rgba(22,65,180,0.2)`              |
| `--surface`           | `#ffffff`            | `#1c1c1c`                          |
| `--surface-2`         | `#F0F0F2`            | `#1a1f2e`                          |
| `--border`            | `#e5e5e5`            | `rgba(255,255,255,0.12)`           |
| `--text-primary`      | `#111111`            | `#f5f5f5`                          |
| `--text-secondary`    | `#555555`            | `#b0b0b0`                          |
| `--text-muted`        | `#888888`            | `#888888`                          |
| `--bonus`             | `#16a34a`            | `#34d399`                          |
| `--bonus-light`       | `#f0fdf4`            | `rgba(22,163,74,0.15)`             |
| `--danger`            | `#ef4444`            | same                               |
| `--bg`                | `#F9FAFC`            | `#111111`                          |
| `--card-bg`           | `#ffffff`            | `#1c1c1c`                          |

### Hero Gradient
```css
linear-gradient(135deg, #0c1a4a 0%, #1641B4 50%, #0f2d7a 100%)
```
Dark mode hero: `linear-gradient(135deg, #080f2e 0%, #0e2670 50%, #0a1d5a 100%)`

---

## Typography

**Font:** Inter (Google Fonts) -- never use any other font.  
**Weights used:** 400 (regular), 500 (medium), 600 (semi-bold), 700 (bold), 800 (extra-bold).

### Sizing Scale

| Class               | Size         | Weight | Use For                    |
|---------------------|-------------|--------|----------------------------|
| `.font-page-title`  | clamp(1.75rem, 4vw, 2.5rem) | 800 | Page/hero titles |
| `.font-heading`     | 18px        | 700    | Section headings           |
| `.font-heading-sm`  | 16px        | 700    | Sub-section headings       |
| `.font-heading-xs`  | 14px        | 700    | Card headings, labels      |
| `.font-body`        | 15px        | 400    | Body copy                  |
| `.font-body-sm`     | 14px        | 400    | Secondary body copy        |
| `.font-body-xs`     | 13px        | 400    | Compact descriptions       |
| `.font-label`       | 13px        | 700    | Uppercase labels           |
| `.font-label-sm`    | 11px        | 600    | Small uppercase labels     |
| `.font-meta`        | 12px        | 400    | Dates, metadata            |
| `.font-tcs`         | 10px        | 400    | T&Cs and compliance text   |
| `.font-tcs-sm`      | 9px         | 400    | Extra-small T&Cs           |
| `.font-bonus`       | inherit     | 700    | Bonus amounts              |
| `.font-bonus-lg`    | 20px        | 800    | Large bonus display        |
| `.font-rating`      | 14px        | 800    | Rating numbers             |
| `.font-rating-lg`   | 18px        | 800    | Large rating display       |
| `.font-lede`        | 17px        | 600    | Article opening paragraph  |
| `.font-article`     | 16px        | 400    | Article body text          |
| `.font-btn`         | 14px        | 600    | Button text                |
| `.font-btn-sm`      | 12px        | 600    | Small button text          |
| `.font-promo-code`  | 13px        | 700    | Promo code display (mono)  |

### Line Heights

| Context     | Line Height |
|-------------|-------------|
| Body text   | 1.75        |
| Headings    | 1.25        |
| Paragraphs  | 1.75        |
| Cards       | 1.3 - 1.5   |
| T&Cs        | 1.3 - 1.4   |

### Rules
- Body line-height is always `1.75` -- never tighter.
- Heading letter-spacing: `-0.02em` to `-0.03em`.
- Never use `em-dash` (--). Use a normal dash `-` or reword. `post_build.py` enforces this.

---

## Ratings

- All ratings are out of 5.0 (never out of 10).
- Always show one decimal place: `4.9/5.0`, not `4.9/5` or `4.9 out of 5`.
- High ratings (4.5+): blue accent badge.
- Mid ratings (3.5 - 4.4): purple badge.
- Low ratings (below 3.5): green badge.

---

## Brand Card Formatting

### Sidebar (Top 5 Betting Sites)

- Title: `.sidebar-section-title` (16px, bold, left-aligned)
- Subtitle: `.sidebar-section-sub` (12px, muted)
- Brand name: `.sidebar-brand-name` (14px, bold, links to review)
- Bonus amount: `.sidebar-brand-bonus` (12px, green/bonus colour)
- T&Cs: `.sidebar-tcs` (10px, muted, max 2 lines with ellipsis via CSS clamp)
- Logo: 36x36px with border-radius 6px
- Visit button: `.btn-primary` with 12px font, pill shape

### Listing Table / Cards

- Desktop: table with sortable headers
- Mobile: cards with rounded corners (12px radius), 16px padding
- Rank badge: 24px circle, accent blue, white text
- CTA buttons: rounded pill (28px radius), accent gradient, min-height 48px

---

## Buttons

| Class          | Style                                                  |
|----------------|--------------------------------------------------------|
| `.btn-primary` | Gradient blue, white text, rounded pill, box-shadow    |
| `.btn-outline` | Light blue bg, accent text/border, rounded pill        |
| `.btn-sm`      | Compact padding (8px 18px), 13px font                  |
| `.btn-full`    | Full width                                              |

### Rules
- Buttons always rounded: `border-radius: 28px` (primary), `24px` (small).
- Shading used as accent -- gradient backgrounds, subtle box-shadows.
- In dark mode, buttons must have visible text (never white on white).
- CTA buttons on cards: full-width, min-height 48px.

---

## Promo Codes

- Display font: monospace, bold, letter-spacing 0.05em.
- Box: dashed border (2px), rounded corners (8px).
- Default code: `NEWBONUS` unless a brand has a specific code.
- Copy button: green background, white icon/text.
- In dark mode: increased border opacity for visibility.

---

## Article Formatting

1. **Lede**: First paragraph in bold (`.lede` class), 1.125rem, weight 600.
2. **Headings**: `h2` at 1.375rem, `h3` at 1.125rem, both weight 700.
3. **Body paragraphs**: `margin-bottom: 20px`, colour `--text-secondary`.
4. **Lists**: left padding 24px, bullet items spaced 8px apart.
5. **Author byline**: linked to author page with `.author-link` class.
6. **Related Articles**: use `.news-badge` for category tags (consistent sizing: 11px, 3px 10px padding, 4px radius).

### Article Voice
- South African English throughout.
- No em-dashes. Use hyphens or reword.
- Human, conversational tone -- not AI-generated sounding.
- Use "punt", "okes", "lekker", "R" for Rand, "SA" for South Africa where natural.

---

## Spacing

- `.section` padding: 80px top/bottom (48px on mobile).
- `.container` max-width: 1200px. Padding: 20px (mobile), 32px (tablet), 48px (desktop).
- Card gap: 24px (grid-3), 16px (grid-6).
- Between sections: 80px (48px mobile).
- Line spacing: 1.75 for body, 1.25 for headings.

---

## Dark Mode

| Element               | Rule                                                  |
|-----------------------|-------------------------------------------------------|
| Page background       | `#111111`                                             |
| Cards                 | `#1c1c1c` bg, `rgba(255,255,255,0.1)` border          |
| Text primary          | `#f5f5f5`                                             |
| Buttons               | Must have contrast -- never white text on white bg     |
| Bonus text            | `#34d399` (brighter emerald green)                     |
| Promo code borders    | Increased opacity (0.55 - 0.65)                        |
| RG banner             | Gradient purple-dark bg instead of flat black           |
| Subcat pills          | `--surface` background, visible border                  |
| Betting Sites CTA     | Blue tint bg, `#93b4ff` text                           |

---

## SEO

- Descriptive URL slugs (e.g. `/betting/best-betting-apps-south-africa`).
- Every page has unique `<title>` and `<meta description>`.
- Target keyword: "South African betting sites".
- OG images: category-specific (1200x630), stored in `/assets/og-*.png`.
- BreadcrumbList JSON-LD on every page.
- Schema.org Review markup on review pages.
- Canonical URLs always set.

---

## Mobile

- Breakpoints: 480px, 639px, 767px, 899px, 991px, 1023px.
- Mobile menu: slide-down with overlay, 52px nav items.
- Tables switch to card layout below 768px.
- Filter pills: horizontal scroll on mobile.
- Tap targets: minimum 44px height.

---

## Logos

- Standard size: 36x36px (sidebar), 48x48px (cards), 64-72px (review hero).
- Always `object-fit: contain` with brand background colour.
- SVG logos use `basecolour` background.
- 10Bet logo: white background specifically.
- Border-radius: 6px (small), 8px (medium), 14px (large).

---

## Star / Favourite System

- Uses cookie persistence (not localStorage -- blocked in deploy sandbox).
- Starred items show filled star icon in bonus colour.
- Starred items float to top of tables/lists.
- Header star badge shows count; hover reveals dropdown with starred brands linking to their promo code pages.
- Stars persist across all pages site-wide.

---

## Files and Build

| File                    | Purpose                                         |
|-------------------------|-------------------------------------------------|
| `build_site.py`         | Main build script (~3980 lines)                  |
| `build_expansion.py`    | Subcategory/expansion pages (~1250 lines)        |
| `post_build.py`         | Em-dash removal, final cleanup                   |
| `style.css.bak`         | Unminified CSS source of truth                   |
| `style.css`             | Live CSS (copy from .bak after build)            |
| `main.js`               | Client-side JS (dark mode, stars, sort, FAQ)     |
| `data.json`             | Brand data (36 brands)                           |
| `news-articles.json`    | News articles (26 articles)                      |

### Build Process
```bash
cd /home/user/workspace
python3 build_site.py
cp mzansiwins-html/assets/style.css.bak mzansiwins-html/assets/style.css
python3 post_build.py
```

---

## Change Log

| Date       | Change                                                    |
|------------|----------------------------------------------------------|
| 2026-03-14 | Style guide created                                       |
| 2026-03-14 | Hero watermark opacity reduced 0.08 -> 0.04               |
| 2026-03-14 | Green bonus text on hero cards brightened for contrast     |
| 2026-03-14 | Dark mode Betting Sites CTA button fixed                   |
| 2026-03-14 | Active nav link gets accent background highlight           |
| 2026-03-14 | Promo code borders strengthened in dark mode                |
| 2026-03-14 | Payment card mobile padding improved                       |
| 2026-03-14 | Bet Responsibly banner gets distinct dark mode treatment    |
| 2026-03-14 | Category-specific OG images added                          |
| 2026-03-14 | Sidebar T&Cs: CSS 2-line clamp instead of 60-char truncate |
| 2026-03-14 | Global font utility classes added to CSS                   |
