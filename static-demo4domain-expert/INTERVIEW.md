# INTERVIEW — Grilling-style discovery

Ask questions **one at a time**, waiting for each answer. Propose a recommended default for every question so the salesperson can say "yes". Use `AskUserQuestion` with concrete options where possible. Push back on vague answers ("looks professional" → which site?), resolve ambiguity ("a few pages" → which?), use plain language (no "SPA"/"component" — say "page"/"section"), and confirm with an explicit "yes" before generating.

## Question 0 — Language (ask first, in English)

Ask exactly this, before anything else, using `AskUserQuestion`:

> Which language should we use? Your choice applies to **both**:
> (a) the language I'll ask all the following questions in, and
> (b) the language of every word in the finished demo (headlines, buttons, navigation, footer, README).

Suggested options (the agent should adapt this list to the obvious locale signals — e.g. if the salesperson opened the conversation in Japanese, lead with Japanese):

- English
- 中文（简体）
- 日本語
- Other (the salesperson types the language and any locale tag, e.g. `fr-CA`)

Record the answer as `language` (a human-readable name) and `htmlLang` (a BCP-47 code, e.g. `en`, `zh-CN`, `ja`, `fr-CA`). These map straight into `site.language`, `site.htmlLang`, and `<html lang="…">` in [TEMPLATE.md](TEMPLATE.md).

**From this point on, conduct every question and every confirmation in the chosen language.** Do not silently fall back to English — even when the salesperson types in English mid-interview, keep asking in the chosen language unless they explicitly say "switch to English".

## Question batches

**Batch 1 — Demo context**
1. What product or feature is this demo for? (Reject one-word answers — get one full sentence.)
2. Who will see it: a non-technical buyer (*customer*) or a technical evaluator (*developer*)? — affects whether the project leans marketing-site or product/docs-site.
3. Will the salesperson walk through it live, or will the prospect open it alone? — affects how self-explanatory the content must be.

**Batch 2 — Content & structure**
4. In one sentence, what does this save / solve / enable for the audience? (Becomes the hero subheadline.)
5. What's the headline — the single bold sentence on the first screen?
6. Which pages? Offer: Home, Features, How it works, Pricing, Use cases, Testimonials, FAQ, About, Contact. (Recommended minimum: Home + Features + Contact.)
7. Give 3–5 key features — short title + one-line description each. Push until at least three.

**Batch 3 — Branding & style**
8. Company name (appears in nav and footer).
9. Logo: file path to an image, or text logo with the company name?
10. Primary brand color: hex code, color name, or "pick something tasteful for [their industry]".
11. Visual style: **Minimal & clean** / **Bold & modern** / **Corporate & trustworthy** / **Playful & friendly**.
12. Optional: a reference website URL whose feel they want to match.

**Batch 4 — CTAs & contact**
13. Primary call-to-action button text (e.g. "Book a Demo", "Start Free Trial").
14. Where does it go: a real URL, a `mailto:` link, or `#` placeholder?
15. Contact info for the footer: email, phone, address — or "leave placeholder".

**Batch 5 — Output**
16. Where should the project folder live? (Default: subfolder of cwd named `<company>-demo`.)

## Confirmation gate

Present a numbered summary of all 17 answers (Q0 language + Q1–Q16) and ask, **in the chosen language**, the equivalent of:

> Generate the demo with these settings? Reply **yes**, or tell me what to change.

Do not proceed without an explicit yes (in any language — accept "yes", "好的", "はい", "oui", etc.).

## Bounded-context check (optional, asked silently)

While reviewing Batch 1–2 answers, ask yourself: did the salesperson describe **two or more product areas with distinct terminology** (e.g. "Ordering and Billing", "Patient app and Clinician dashboard")?

- If **no** (the default): generate a single root `CONTEXT.md`.
- If **yes**: use the multi-context layout — `CONTEXT-MAP.md` at root plus a `CONTEXT.md` inside each `src/<area>/` folder. See [TEMPLATE.md](TEMPLATE.md) → "Multi-context variant".

If unsure, pick single-context. Do not invent bounded contexts that don't exist in the demo brief. Do not generate `docs/adr/` — that's the `grill-with-docs` skill's job, not this one.
