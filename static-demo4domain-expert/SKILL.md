---
name: static-demo4domain-expert
description: Interview a non-technical business user (typically a salesperson) with grilling-style questions, then scaffold an elegant, runnable static Vue 3 + Vite demo project for them to show customers or developers. Use when the user wants to build a sales demo, product demo page, marketing landing site, customer-facing showcase, or says "build a demo", "make a demo page", "Vue demo project", "sales demo site".
---

# Vue Demo Builder

Guide a non-technical salesperson to produce a polished, runnable Vue 3 demo they can show to customers or developers.

## Quick start

Two strictly-ordered phases — never skip phase 1:

1. **Interview** the salesperson using the question batches below.
2. **Generate** per [TEMPLATE.md](TEMPLATE.md), apply [STYLE.md](STYLE.md), generate `README.md`, run `npm install`, then print the run-instructions block from [TEMPLATE.md](TEMPLATE.md) verbatim.

A demo built without the interview will look generic and embarrass the salesperson in front of a prospect.

## Audience

The user is a salesperson, not a developer. They care how the demo *looks* and *reads*, not the code. Run-time instructions must be plain-language. The salesperson may later ask an AI to modify the project, so the generated `README.md` is written for both audiences.

## Phase 1: Interview (grilling-style)

Run the grilling script in [INTERVIEW.md](INTERVIEW.md). **Question 0 first**: ask the salesperson which language to use — the answer governs both the language of every subsequent question *and* the language of all generated copy (headlines, buttons, nav, footer, README user-facing sections). Then run the 5 question batches one at a time in that language, push back on vague answers, end with a numbered-summary confirmation gate that requires an explicit "yes" (in that language) before any files are written.

## Phase 2: Generate

Scaffold with **Vue 3 + Vite + Vue Router 4 + Tailwind CSS 3**. Tailwind is the default for both audiences — elegant for marketing, adaptable to a docs feel.

- Files, configs, components, `site.js` schema, README template: [TEMPLATE.md](TEMPLATE.md).
- Visual rules (typography, spacing, color, hero/feature/CTA patterns, style-variant tweaks): [STYLE.md](STYLE.md). Apply rigorously — visual polish is what closes the demo.

**Content rule:** Use the salesperson's actual answers everywhere. Never lorem ipsum. If a section needs filler, derive a sentence from their value prop.

**After scaffolding — every step, every time, in order:**

1. Generate `README.md` per [TEMPLATE.md](TEMPLATE.md) → "README.md" as a Claude-readable project guide. Non-negotiable.
2. Generate `CONTEXT.md` at the project root per [TEMPLATE.md](TEMPLATE.md) → "CONTEXT.md". This mirrors the convention used by the `grill-with-docs` skill so a future AI agent has a domain map to work from.
3. Run `npm install`. If it fails, fix the cause and rerun before continuing.
4. **Always** print the run-instructions block to the salesperson verbatim — use [TEMPLATE.md](TEMPLATE.md) → "Run instructions block", with the absolute project path filled in. Never skip, even if the user looks technical.
5. Offer: "Want me to start the demo server now so you can preview it?"

### Domain documentation layout

Default to a single **root `CONTEXT.md`**. Use the multi-context layout (`CONTEXT-MAP.md` at root + a `CONTEXT.md` inside each `src/<area>/` folder) only if the demo covers two or more product areas with distinct terminology. Both trees and the bounded-context check are in [TEMPLATE.md](TEMPLATE.md) → "File tree" and [INTERVIEW.md](INTERVIEW.md) → "Bounded-context check". Do not create `docs/adr/` — this skill records context, not decisions.

## Workflow checklist

- [ ] Asked question 0 (language) first, then conducted every following question in that language
- [ ] Asked all 5 batches, one question at a time
- [ ] Pushed back on at least one vague answer
- [ ] Confirmed full numbered summary with explicit "yes"
- [ ] Scaffolded per [TEMPLATE.md](TEMPLATE.md), applied [STYLE.md](STYLE.md)
- [ ] All generated copy is in the chosen language (headlines, nav, buttons, footer, README user-facing sections)
- [ ] Every section filled with the salesperson's actual messaging — zero lorem ipsum
- [ ] Centralized branding in `src/data/site.js`, including `site.language` and matching `<html lang>` in `index.html`
- [ ] Generated `README.md` as the Claude-readable project guide
- [ ] Generated `CONTEXT.md` (or `CONTEXT-MAP.md` + per-area `CONTEXT.md` files for multi-context demos)
- [ ] Ran `npm install` successfully (or fixed errors and reran)
- [ ] Printed the run-instructions block verbatim, with absolute path
- [ ] Offered to start the dev server for preview

## Anti-patterns

- Skipping the interview because the salesperson seems decisive — regenerating costs them a meeting
- Lorem ipsum, "Feature 1 / Feature 2" placeholders, stock headlines
- Admin UI kits (Element Plus, Ant Design Vue) for marketing demos — they look like dashboards, not pitches
- Hardcoding brand color/name in components instead of `src/data/site.js`
- Skipping the printed run-instructions block, or assuming the salesperson remembers
- Skipping `CONTEXT.md` — the next AI agent the salesperson talks to will reinvent their terminology
- Creating `docs/adr/` — not this skill's job; if the salesperson later needs decision records, the `grill-with-docs` skill seeds them
- Inventing multiple bounded contexts for a single-product demo just to mimic the multi-context layout
- Asking question 0 in English and then switching mid-interview, or generating English copy after the salesperson chose another language
