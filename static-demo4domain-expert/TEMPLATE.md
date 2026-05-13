# TEMPLATE — Project Scaffold

Exact file structure, configs, and starter components to generate after the interview is confirmed.

## File tree

```
<company>-demo/
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── README.md                       ← Claude-readable project guide (also has run steps)
├── CONTEXT.md                      ← domain language + positioning (single-context default)
├── public/
│   └── favicon.svg
└── src/
    ├── main.js
    ├── App.vue
    ├── style.css                   ← Tailwind directives + base layer
    ├── router/
    │   └── index.js
    ├── data/
    │   └── site.js                 ← ALL branding + content from interview
    ├── components/
    │   ├── NavBar.vue
    │   ├── Footer.vue
    │   ├── Hero.vue
    │   ├── FeatureGrid.vue
    │   ├── CTASection.vue
    │   ├── PricingTable.vue        ← only if Pricing page chosen
    │   ├── TestimonialList.vue     ← only if Testimonials page chosen
    │   ├── FAQAccordion.vue        ← only if FAQ page chosen
    │   └── CodeBlock.vue           ← only if audience = developer
    └── views/
        ├── HomeView.vue            ← always
        ├── FeaturesView.vue        ← if chosen
        ├── HowItWorksView.vue      ← if chosen
        ├── PricingView.vue         ← if chosen
        ├── UseCasesView.vue        ← if chosen
        ├── TestimonialsView.vue    ← if chosen
        ├── FAQView.vue             ← if chosen
        ├── AboutView.vue           ← if chosen
        └── ContactView.vue         ← if chosen
```

Only generate views/components for pages the user actually picked. Don't ship dead files.

**Multi-context variant** — only if the demo legitimately covers two or more product areas with distinct terminology (rare). Then the layout becomes:

```
<company>-demo/
├── CONTEXT-MAP.md                  ← lists the areas + cross-area relationships
└── src/
    ├── <area-a>/
    │   └── CONTEXT.md
    └── <area-b>/
        └── CONTEXT.md
```

Default to single-context. Do not split unless the salesperson described separate areas. Do not create `docs/adr/` in either layout — this skill produces context, not decision records.

## package.json

```json
{
  "name": "<company-kebab>-demo",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "vite": "^5.2.0"
  }
}
```

## vite.config.js

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
})
```

## tailwind.config.js

Inject the user's primary brand color as the `brand` palette so all components reference it semantically.

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '<tint-95>',
          100: '<tint-90>',
          500: '<USER_PRIMARY_HEX>',
          600: '<shade-10>',
          700: '<shade-20>',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

Compute the tint/shade values from the user's hex; if unsure, use a reasonable lighten/darken (e.g. 95% white-mix and 10–20% black-mix).

## postcss.config.js

```js
export default {
  plugins: { tailwindcss: {}, autoprefixer: {} },
}
```

## index.html

Set `<html lang>` to the BCP-47 code from Q0 (e.g. `en`, `zh-CN`, `ja`, `fr-CA`). Set `<title>` using the company name and headline **in the chosen language** — never English boilerplate when the demo is non-English.

```html
<!doctype html>
<html lang="<HTML_LANG>">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title><Company> — <Hero headline in chosen language></title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

For CJK languages, also preload a CJK-capable font (e.g. `Noto Sans SC`, `Noto Sans JP`) alongside Inter, and extend `tailwind.config.js → theme.extend.fontFamily.sans` to include it before the system fallbacks. Inter alone will render CJK glyphs in the OS fallback — usable but not elegant.

## src/data/site.js

This is the **single source of truth** for everything the user customised. Components import from here — never hardcode brand strings inside components.

```js
export const site = {
  company: '<Company Name>',
  logo: { type: 'text', text: '<Company Name>' }, // or { type: 'image', src: '/logo.svg' }
  primaryColor: '<#hex>',
  style: '<minimal | bold | corporate | playful>',
  audience: '<customer | developer>',
  language: '<human-readable name from Q0, e.g. "English" | "中文（简体）" | "日本語">',
  htmlLang: '<BCP-47 code, e.g. "en" | "zh-CN" | "ja" | "fr-CA">',

  hero: {
    headline: '<USER_HEADLINE>',
    subheadline: '<USER_SUBHEADLINE>',
    primaryCta: { label: '<CTA_TEXT>', href: '<CTA_TARGET>' },
    secondaryCta: { label: 'Learn more', href: '/features' },
  },

  features: [
    { title: '<F1 title>', description: '<F1 desc>', icon: 'sparkles' },
    // …user's 3–5 features
  ],

  pricing: [/* optional, if Pricing page */],
  testimonials: [/* optional */],
  faq: [/* optional */],

  contact: {
    email: '<email or null>',
    phone: '<phone or null>',
    address: '<address or null>',
  },

  nav: [
    { label: 'Home', to: '/' },
    // …only pages the user picked
  ],
}
```

## src/main.js

```js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

createApp(App).use(router).mount('#app')
```

## src/style.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html { scroll-behavior: smooth; }
  body { @apply font-sans text-slate-900 antialiased; }
  h1, h2, h3 { @apply font-display tracking-tight; }
}
```

## src/router/index.js

Generate routes only for the pages the user picked. Always include `/`.

```js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  { path: '/', component: HomeView },
  // …user's chosen pages, lazy-imported
]

export default createRouter({ history: createWebHistory(), routes })
```

## src/App.vue

```vue
<script setup>
import NavBar from './components/NavBar.vue'
import Footer from './components/Footer.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <NavBar />
    <main class="flex-1"><router-view /></main>
    <Footer />
  </div>
</template>
```

## Starter components

For each component, follow [STYLE.md](STYLE.md) for visual rules. Pull all text/branding from `site.js` — components are presentational only.

- **NavBar.vue** — sticky top, logo left, nav links right, primary CTA button on the far right. White background with a subtle bottom border. Mobile: hamburger that opens a full-height drawer.
- **Footer.vue** — three columns (company tagline + logo, nav links, contact). Slate-50 background. Copyright row at the bottom.
- **Hero.vue** — full-width section, ~80vh, generous vertical padding. Headline (4xl–6xl), subheadline (lg–xl, muted), two CTA buttons (primary + secondary). Optional right-side illustration or product screenshot placeholder.
- **FeatureGrid.vue** — 2- or 3-column grid (1 col on mobile). Each card: icon, title, description. Hover lift on cards.
- **CTASection.vue** — single full-width band, brand-colored or dark, centered headline + CTA button. Used at the bottom of most views.
- **PricingTable.vue** *(if Pricing chosen)* — 3 tiers side by side, middle tier highlighted with brand color. Each tier: name, price, feature list with checkmarks, CTA button.
- **TestimonialList.vue** *(if Testimonials chosen)* — quote cards with avatar circle (initials), name, role/company.
- **FAQAccordion.vue** *(if FAQ chosen)* — expand/collapse with smooth height transition.
- **CodeBlock.vue** *(if audience = developer)* — dark-themed `<pre>` with copy-to-clipboard button. Used inside HowItWorks / Features for developer audiences.

## Run instructions block

After `npm install` completes, print this block to the salesperson in chat. Fill in `<ABSOLUTE_PROJECT_PATH>` with the actual absolute path. Do not skip even if the user seems technical — they will not remember the commands tomorrow.

**Translate the prose into the chosen language from Q0.** Keep all command names literal (`npm install`, `npm run dev`, `cd`, `Ctrl + C`, URLs, file paths) — never translate code. The English template below is the canonical version; render the same content in the chosen language and preserve line structure.

```
Your demo is ready! Here is exactly how to open it.

First-time setup on this computer (only once ever):
  • Install Node.js LTS from https://nodejs.org (the green button).
  • I have already run `npm install` for you in this folder.

To open the demo (every time you want to show it):
  1. Open Terminal.
  2. Go to the project folder:
       cd "<ABSOLUTE_PROJECT_PATH>"
  3. Start the demo:
       npm run dev
  4. Open the link it prints (usually http://localhost:5173) in your browser.

To stop the demo: press Ctrl + C in the terminal window.
To share with a teammate: send them the whole folder. They install Node.js,
  run `npm install` once, then `npm run dev`.
To change wording, colors, or the call-to-action: open src/data/site.js in
  any text editor — everything lives there.
```

## README.md (Claude-readable project guide)

This README is the canonical reference for editing or extending the demo. It is written to be readable by **both** the non-technical salesperson and by any AI coding agent (e.g. Claude) the salesperson later asks for help. Generate it for every demo, filling in `<…>` placeholders with the interview answers.

**Language rule for the generated README:**

- **Translate** into the chosen language from Q0: the intro paragraph, the entire `## Quick start (for the salesperson)` section body, and all human prose under `## Demo configuration` and `## Recipes`.
- **Keep in English**: every `## section heading` (agents grep for them), `## Stack`, `## Commands` table body, `## Project shape` table body, `## Conventions`, `## Visual style rules (summary)`, `## Non-goals`, and `## For AI agents asked to modify this project`. These are technical references that downstream AI agents and developers expect in English.
- Commands (`npm run dev`, etc.) stay literal — never translate command names or code.

Structure the README in this exact order so agents can grep for stable section headings.

```md
# <Company> Demo — Project Guide

This is a static Vue 3 + Vite sales demo for <Company>. It was generated from a non-technical interview; everything customer-facing is centralised in `src/data/site.js`.

## Quick start (for the salesperson)

First time on this computer (once):
1. Install Node.js LTS from https://nodejs.org.
2. In Terminal, from this folder: `npm install`

To open the demo (every time):
\`\`\`bash
npm run dev
\`\`\`
Open the link it prints (usually http://localhost:5173). Press **Ctrl + C** to stop.

To share: send the whole folder. The recipient installs Node.js, runs `npm install` once, then `npm run dev`.

To change wording, colors, or the call-to-action: open `src/data/site.js` in any text editor.

---

## Stack

- Vue 3 (Composition API, `<script setup>`)
- Vite 5
- Vue Router 4 (history mode)
- Tailwind CSS 3 (utilities only — no extracted component layer)
- Inter font, loaded from Google Fonts in `index.html`
- No backend. Static output.
- Node 18+ recommended.

## Commands

| Command           | What it does                                       |
|-------------------|----------------------------------------------------|
| `npm install`     | Install dependencies (run once after download).    |
| `npm run dev`     | Start dev server with hot reload.                  |
| `npm run build`   | Build static output to `dist/`.                    |
| `npm run preview` | Serve the built `dist/` locally to sanity-check.   |

Deploy: `npm run build`, then upload `dist/` to any static host (Netlify, Vercel, S3, GitHub Pages).

## Project shape

\`\`\`
<paste the actual generated file tree here>
\`\`\`

| Path                  | Purpose                                                                                  |
|-----------------------|------------------------------------------------------------------------------------------|
| `src/data/site.js`    | **Single source of truth** for all branding and copy. Edit here, never inside components. |
| `src/router/index.js` | Route table. Adding a page = one entry here + one view file.                              |
| `src/components/`     | Reusable presentational components. Read data from `site.js` via props or imports.        |
| `src/views/`          | One file per page. Compose components; do not embed copy strings directly.                |
| `tailwind.config.js`  | Brand palette injected as `brand.50…brand.700`. Components reference `bg-brand-500`, etc. |
| `src/style.css`       | Tailwind directives + minimal base layer (font, smoothing).                               |
| `index.html`          | `<title>`, favicon, Inter font preload.                                                   |

## Demo configuration (captured from the interview)

| Setting          | Value                                              |
|------------------|----------------------------------------------------|
| Audience         | `<customer | developer>`                           |
| Visual style     | `<minimal | bold | corporate | playful>`           |
| Primary brand    | `<#hex>` (mapped to Tailwind `brand-500`)          |
| Logo             | `<text "<Company>" | image at /logo.svg>`         |
| Pages enabled    | Home, <…the other chosen pages…>                   |
| Primary CTA      | `"<label>"` → `<href>`                             |
| Headline         | `"<hero headline>"`                                |
| Subheadline      | `"<hero subheadline>"`                             |

## Conventions

1. **All customer-facing strings live in `src/data/site.js`.** Components must not contain hardcoded copy, brand names, or CTA labels. If new copy is needed, add a key to `site.js` and reference it.
2. **Brand color is referenced via the Tailwind `brand` palette only** (`bg-brand-500`, `text-brand-600`, etc.). Never inline a hex code in a component — change `tailwind.config.js` if the brand changes.
3. **Two button styles, no third.** Primary = filled brand. Secondary = white with slate ring. See existing components for the exact classes.
4. **No emoji in product copy** unless the user explicitly asked for it.
5. **No lorem ipsum.** Every section ships with real copy derived from the value prop.
6. **Mobile-first.** All grids collapse to one column under `md` (768px). NavBar collapses to a drawer.

## Recipes

### Change a headline, feature, CTA label, or contact info
Edit `src/data/site.js`. Save. Dev server hot-reloads.

### Change the brand color
Edit `tailwind.config.js` → `theme.extend.colors.brand`. Replace `500` with the new hex; recompute `50/100/600/700` (lighter tints / darker shades). Restart `npm run dev` if Tailwind doesn't pick up the change.

### Add a new page
1. Create `src/views/<Name>View.vue`. Compose existing components; follow the style of `HomeView.vue`.
2. Register the route in `src/router/index.js`:
   \`\`\`js
   { path: '/<slug>', component: () => import('../views/<Name>View.vue') }
   \`\`\`
3. Add `{ label: '<Name>', to: '/<slug>' }` to `site.nav` in `src/data/site.js`.

### Add or remove a feature card
Edit the `site.features` array in `src/data/site.js`. The grid renders whatever is in the array.

### Swap the logo from text to image
Drop the file into `public/logo.svg` (or any image format). In `src/data/site.js`, set `site.logo = { type: 'image', src: '/logo.svg' }`.

### Wire the contact form to a real backend
This demo is static. Integrate Formspree / Basin / Netlify Forms / a Vercel serverless function — none of that ships here.

## Visual style rules (summary)

- **Font:** Inter only.
- **Section padding:** `py-20 md:py-28`. Content wrapper: `max-w-6xl mx-auto px-6`.
- **Cards:** `rounded-2xl border border-slate-200 bg-white p-8`, hover lift only.
- **Brand color:** sparingly — primary CTAs, eyebrow labels, hover states, CTA section, highlighted pricing tier.
- **Shadows:** one shadow, on hover only. No stacked drop shadows.
- **No animated entrances** that delay content; transitions only on hover/interaction.

## Non-goals

- Not production. No analytics, no SEO beyond basics, no i18n, no auth.
- No CMS — all copy lives in `site.js`.
- No tests — visual review is the verification path.

## For AI agents asked to modify this project

Read this README first; it defines the conventions above. Useful prompts a salesperson might give you:

- "Edit `src/data/site.js` to change the headline to '…'."
- "Add a new page called Roadmap. Register the route and add it to the nav."
- "Switch the brand color to `#10b981` and update the Tailwind palette."
- "Tighten hero spacing on mobile."

When in doubt: prefer editing `src/data/site.js` over touching components, and prefer Tailwind utility classes over new CSS.
```

**Notes when generating this README:**

- Replace every `<…>` placeholder with the actual interview answer or generated value.
- Paste the real file tree (the generated subset, not the full superset) into the `Project shape` code block.
- Keep section headings *exactly* as listed — agents grep for them.
- Do not add emoji, marketing fluff, or invented features. Only document what was actually generated.
- The fenced code blocks inside the markdown use escaped backticks (`\`\`\``) above only because this is itself a markdown template; in the generated `README.md`, write plain triple-backticks.

## CONTEXT.md

A short domain map written *for the next AI agent* the salesperson talks to. Mirrors the format used by the `grill-with-docs` skill so a future grilling/refactor session has the right starting point. Place this at the project root.

```md
# <Company> Demo

A static Vue 3 sales demo for <Company>. The product being demoed is <one-sentence description from interview Q1>. The audience is a <customer | developer> who will <walk through it live | open it alone>.

## Positioning

**Headline:** "<hero headline from Q5>"
**Value prop:** <hero subheadline from Q4>
**Primary call-to-action:** "<CTA label>" → `<CTA href>`

## Language

Use these exact terms in any new copy. Reject the listed aliases.

**<Feature 1 title>**:
<one-line description from interview>
_Avoid_: <obvious synonym the salesperson did NOT use, if any>

**<Feature 2 title>**:
<one-line description>
_Avoid_: <synonym to avoid, if any>

**<Feature 3 title>**:
<one-line description>

**<Company>**:
The product is referred to as "<Company>" — never as "the platform", "the tool", "the app" in customer-facing copy unless the salesperson explicitly used that phrasing.

## Visual identity

- Style: **<minimal | bold | corporate | playful>**
- Primary brand color: `<#hex>`, exposed in Tailwind as `brand.500`
- Typography: Inter only

## Non-goals

- Not a product. No backend, no auth, no analytics, no real form submission.
- Not for SEO. The hero copy is for in-room demos and short links, not search.
- Not exhaustive. Only the pages chosen in the interview exist: <list pages>.

## Flagged ambiguities

<Only include this section if the interview surfaced a synonym the salesperson and prospects might use differently. Otherwise omit. Example:>

- "<term A>" vs "<term B>" was used interchangeably — resolved to **<term A>** because <reason>.
```

**Rules when generating CONTEXT.md:**

- Write `CONTEXT.md` **in the chosen language** from Q0, except: keys/labels that are universal markers (`Avoid`, `Headline`, `Value prop`) may stay in English so future agents can grep them. Term names, descriptions, and the narrative prose are in the chosen language.
- Pull every concrete value from the interview answers. Do not invent terminology that wasn't said.
- The "Language" section (vocabulary) is the most important part — it stops future agents from drifting from the salesperson's vocabulary.
- Keep it under one page. If you cannot fit it on one page, you are documenting implementation; cut.
- For the multi-context variant, replace this with a `CONTEXT-MAP.md` at the root listing each area, plus a `CONTEXT.md` inside each `src/<area>/` folder following this same shape.
- **Do not generate `docs/adr/` or any ADR files.** If the salesperson later needs decision records, point them at the `grill-with-docs` skill.
