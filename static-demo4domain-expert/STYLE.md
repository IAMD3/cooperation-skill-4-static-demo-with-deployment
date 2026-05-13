# STYLE — Visual design rules

These rules are non-negotiable. Without them, the output looks like a bootstrap template and fails the "elegant" bar. With them, the demo looks like it cost a designer a week.

## Type scale

Use a clear, restrained scale. Inter (loaded from Google Fonts) for everything.

| Use                 | Tailwind                          |
|---------------------|-----------------------------------|
| Hero headline       | `text-5xl md:text-6xl font-bold tracking-tight` |
| Section heading     | `text-3xl md:text-4xl font-semibold tracking-tight` |
| Card title          | `text-lg font-semibold`           |
| Hero subheadline    | `text-lg md:text-xl text-slate-600` |
| Body                | `text-base text-slate-700 leading-relaxed` |
| Eyebrow / label     | `text-sm font-medium uppercase tracking-wider text-brand-600` |

Never use more than 3 font sizes within one section. Never use italic body text.

## Spacing

Sections are vertical breathing room. Be generous.

- Section padding: `py-20 md:py-28` (hero may be `py-24 md:py-32`)
- Section horizontal: wrap content in `max-w-6xl mx-auto px-6`
- Gap between feature cards: `gap-8` (grid) or `gap-6` (tighter for 4-col)
- Card internal padding: `p-8`
- Button padding: `px-6 py-3` (primary), `px-5 py-2.5` (secondary)

## Color usage

- **White** is the dominant background. Most sections are white.
- **`bg-slate-50`** alternates one or two sections to create rhythm — never two slate sections in a row.
- **Brand color** appears in: primary CTA fills, eyebrow labels, link hovers, highlighted pricing tier, footer accent. Use sparingly — when everything is brand, nothing is brand.
- **`text-slate-900`** for headings, **`text-slate-700`** for body, **`text-slate-500`** for muted/secondary.
- Borders: `border-slate-200`. Never use `border-black` or pure-black text.

## Buttons

Primary:
```html
<a class="inline-flex items-center justify-center rounded-lg bg-brand-500 px-6 py-3 text-base font-semibold text-white shadow-sm hover:bg-brand-600 transition">
  {{ label }}
</a>
```

Secondary:
```html
<a class="inline-flex items-center justify-center rounded-lg bg-white px-5 py-2.5 text-base font-semibold text-slate-900 ring-1 ring-slate-200 hover:ring-slate-300 transition">
  {{ label }}
</a>
```

Never use a third button style. Never use pure-black or gradient buttons (unless `style = bold`, see below).

## Cards

```html
<div class="rounded-2xl border border-slate-200 bg-white p-8 transition hover:-translate-y-0.5 hover:shadow-lg">
  …
</div>
```

Rounded corners: `rounded-2xl` for cards, `rounded-lg` for buttons/inputs, `rounded-full` for avatars/pills only. Pick one card radius and stick to it across the whole site.

## Hero patterns

Pick **one** layout — don't mix:

1. **Centered** (default): everything center-aligned, max-width ~3xl. Best when the headline is the star.
2. **Split**: headline + CTAs on the left, illustration/screenshot placeholder on the right. Use a soft `bg-gradient-to-br from-brand-50 to-white` background.

Always include a subtle visual flourish — a soft radial gradient blob behind the headline, OR a thin brand-colored eyebrow label above it. Not both.

## Feature grid

- 3 features → 3 columns on desktop (`md:grid-cols-3`)
- 4 features → 2x2 on desktop (`md:grid-cols-2`) — never 4 across, too cramped
- 5 features → 3 on top row, 2 centered below, OR list layout

Each card: small brand-colored icon square (40px, `bg-brand-50 text-brand-600 rounded-lg`), title, one-line description. Icons can be simple inline SVGs (heroicons-style) or unicode symbols — never emoji.

## CTA section (bottom of pages)

Full-width band, brand-colored or dark slate:

```html
<section class="bg-brand-500">
  <div class="max-w-4xl mx-auto px-6 py-20 text-center">
    <h2 class="text-3xl md:text-4xl font-semibold text-white">{{ headline }}</h2>
    <p class="mt-4 text-lg text-brand-50">{{ sub }}</p>
    <a class="mt-8 inline-flex … bg-white text-brand-600 …">{{ cta }}</a>
  </div>
</section>
```

## Style-variant adjustments

The user picks one of four visual styles in the interview. Tweak the defaults above accordingly:

| Style                     | Adjustments                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| **Minimal & clean**       | Default rules. Generous whitespace, almost no decoration, subtle borders.   |
| **Bold & modern**         | Bigger headlines (`text-6xl md:text-7xl`). Gradient backgrounds on hero. Slightly tighter line-height. Bolder weights (`font-extrabold` on hero). |
| **Corporate & trustworthy** | Tighter spacing (`py-16` not `py-20`). Squarer corners (`rounded-lg` not `rounded-2xl`). Navy/slate dominant, brand color used very sparingly. Add small trust signals (logos row under hero). |
| **Playful & friendly**    | Softer radii (`rounded-3xl`). Hand-drawn-feel iconography (rotated squares, dots). Brand color used more liberally. Slightly larger body text. |

## Responsive

Mobile is not optional — salespeople will demo on iPads and the prospect may open the link on a phone.

- All grids collapse to single column under `md` (768px)
- Hero headline scales down (`text-4xl` mobile)
- NavBar collapses to hamburger drawer under `md`
- Section padding shrinks to `py-12` on mobile

## What NOT to do

- ❌ Drop shadows everywhere — use one shadow, on hover only
- ❌ Multiple competing accent colors — one brand color, period
- ❌ Stock photo placeholders (`https://via.placeholder.com/…`) — use solid brand-tinted blocks with the company initial instead
- ❌ Emoji in headings or feature titles
- ❌ Centered body paragraphs longer than one line — center only short hero/CTA copy
- ❌ More than one font family
- ❌ `text-justify` anywhere
- ❌ Animated entrances that delay content — instant render, transitions only on hover/interaction
