# BoC Tracker — Design System

> *A practitioner's terminal in editorial dress.*
> For a reader who would rather read the FT than a fintech app, but still wants their dashboard to feel like 2026 — not 2014.

This design system establishes the brand identity, type, color, spacing, components, and screen recreations for **BoC Tracker** — a personal dashboard tracking Bank of Canada policy and Canadian macro conditions between Monetary Policy Reports. Live site (current, pre-redesign): https://jayzhaomurray.github.io/boc-tracker/

---

## What the product is

A static HTML site on GitHub Pages with one splash page (a 5-chart status board across goods, labour, and monetary stance) plus six deep-dive pages: **monetary policy**, **inflation**, **GDP & activity**, **labour**, **housing**, **financial conditions**, and **trade**. Built by a Python pipeline (`fetch → analyze → build`), refreshed nightly via GitHub Actions.

The reader is a practitioner — comfortable with dense data, allergic to dashboards that look like consumer apps. Imagine a BoC research economist, an FT macro reader, or a fixed-income desk analyst. The dashboard must reward a 5-second scan *and* a 5-minute drill-down.

## Design north star — "Iridian Ledger"

The brand sits at the intersection of three references:

1. **The Financial Times print edition** — warm paper, ink-on-cream, an italic serif for editorial voice, ruthless density.
2. **The Bank of Canada's published research and polymer banknotes** — engraved precision, hairline rules, monospace numerals, and the *one* decorative flourish: the iridescent security-foil shimmer found on a $20 bill, used here as the brand's signature.
3. **Modern fintech terminals** (Linear, Mercury, Causal, the better corners of Bloomberg) — flat, dense, restrained colour, opinionated keyboard interaction.

The result is **subtle**, **professional**, and **literate** — with one small piece of visible weirdness (the iridian foil) that signals: *this is a thinking person's tool, not a generic chart farm.*

---

## Index

| File / folder                | What's in it |
|------------------------------|---------------|
| `README.md`                  | This file — brand context, content fundamentals, visual foundations, iconography. |
| `colors_and_type.css`        | All design tokens (color, type, spacing, radii, motion) and base element styles. |
| `fonts/`                     | (Optional offline copies — currently loaded from Google Fonts CDN; see Type below.) |
| `assets/`                    | Logos, marks, illustrations. |
| `preview/`                   | Design-system cards (rendered in the **Design System** tab). |
| `ui_kits/dashboard/`         | Hi-fi recreation of the live product (splash + deep-dive) with reusable JSX components. |
| `SKILL.md`                   | Agent-skill manifest so this folder can be downloaded and used in Claude Code. |

---

## Content fundamentals

The voice of BoC Tracker is **plain-language analytical**. It's downstream of the `markdown-files/analysis_framework.md` in the source repo, which is the load-bearing document for every blurb. Every analytical claim is anchored to a Bank of Canada primary source (MPRs, Staff Analytical Notes, FSRs) or empirically verified against the dashboard's own data.

### Voice attributes

| Attribute        | How it shows up |
|------------------|-----------------|
| **Practitioner-direct** | Reads like a sell-side morning note, not a consumer-finance app. "Headline CPI sits at 2.3% Y/Y; trim and median are 2.1% and 2.2%" — not "Inflation is doing OK 👍". |
| **What over why** | Lead with the observable read. Causation is rationed and tagged. |
| **Synthesises, doesn't summarise** | Each blurb says what the data implies for the section's sub-question. It does not narrate the chart. |
| **Plain-language technical** | Uses BoC's own framings (neutral band 2.25–3.25%, the C.D. Howe recession definition, breadth thresholds). Doesn't dumb them down; doesn't explain them inline either. |
| **Verification-anchored** | Tier tags (Tier 1 / 2 / 3 — from `_tiers.md`) govern claim provenance. Tier 1 is generated; Tier 3 is user-verified. |

### Casing & person

- **Person:** Third-person, observational. *"The Bank is on hold"*, *"the 2Y has rallied 20bp this month"*. Avoid *we*, *you*, *I* unless explicitly an editorial aside.
- **Headlines:** Sentence case. *"What the Bank is doing right now"* — never *"What The Bank Is Doing Right Now"*. Bank-related proper nouns stay capitalised: **Bank of Canada**, **the Bank**, **Governing Council**, **the Fed**, **Statistics Canada**.
- **Section heads:** Small-caps eyebrow + sentence-case heading. (`MONETARY POLICY` → *Is the Bank tightening, holding, or easing?*)
- **Numbers, dates, units:** Always tabular monospace. Two decimals for daily series (rates, FX, oil); one for monthlies (CPI Y/Y, unemployment). Dates: `Apr 2026` for monthly, `Apr 30, 2026` for daily. Percentages: `%`. Basis points: `bp`. Percentage points: `pp`.
- **Negative numbers:** A real minus glyph (−), not a hyphen. Magnitudes use `M` / `B` only when the digit count gets uncomfortable.

### Punctuation & rhythm

- En-dashes for ranges (`2.25–3.25%`), em-dashes for asides — like this — set tight.
- Oxford commas, always.
- Short sentences are fine. *Two* short sentences in a row are better than one long one when the reader is skimming.
- Footnotes go below the chart in italic; never inside a tooltip; never inside a heading.

### Vibe & no-no list

- **No emoji.** The dashboard never uses them. Status is conveyed by a small foil dot, a coloured pill, or a tabular value.
- **No exclamation points.** Ever.
- **No "AI-narrator" phrases.** No *"Let's break it down"*, no *"It's worth noting that…"*, no *"As we can see"*. State the read.
- **No marketing copy.** This is a single-user dashboard. There is no funnel.
- **No conversational hedging in blurbs.** *"It seems like maybe"* is wrong. Either *"the data shows X"* or *"the read is ambiguous because X and Y point opposite directions."*

### Example copy (do)

> **MONETARY POLICY · Apr 2026**
>
> *The Bank is on hold at 2.75%, the upper edge of the 2.25–3.25% neutral band.*
> Three consecutive meetings without action. The 2Y GoC is trading 30bp below the policy rate — markets price one cut over the next 12 months, no more.

### Example copy (don't)

> **🇨🇦 Bank of Canada Update! 🏦**
>
> Hey there! The Bank of Canada is currently holding rates steady at 2.75% — that's right in the neutral zone. Markets are signalling that a cut might be on the way. Let's dig in! 👇

---

## Visual foundations

The foundations live in [`colors_and_type.css`](colors_and_type.css). Open it for the canonical token names; below is the **why**.

### Surface & ink

The page background is **warm paper cream** (`--paper: oklch(96.5% 0.012 85)`), borrowed from the FT salmon family but pulled greyer so charts read cleanly on it. Ink is a **deep navy** (`--ink: oklch(20% 0.025 265)`) rather than pure black — softer on cream, holds its weight, doesn't fight the foil. Three steps of subdued ink (`--ink-sub`, `--ink-quiet`, `--ink-faint`) handle hierarchy. Cards are *barely* lighter than paper (`--card: oklch(98% 0.008 85)`); the elevation comes from a hairline border, not a drop shadow.

There is also a **Vault** dark mode (`[data-theme="vault"]`): deep midnight ink as the surface, cream-toned text. Intended for late-night reading sessions and for screenshot-into-Substack. The accents shift up in lightness to match.

### Accents

The two anchor accents promote directly from the existing `chart_style_guide.md`:

- **Cobalt** (`--cobalt`) — *Canada, BoC, the primary domestic series.* Evolved from the guide's `#1565c0` into OKLCH so it stays perceptually consistent in both modes.
- **Vermillion** (`--vermillion`) — *US, Fed, editorial overlay.* Evolved from `#c62828`.

The categorical four (`--cat-amber`, `--cat-teal`, `--cat-plum`, `--cat-pine`) keep their roles for conceptually-independent series — food, energy, goods, services on CPI Components and the like. Walnut is the fifth, used sparingly. Semantic aliases (`--above-target`, `--on-target`, `--easing`, `--tightening`) point at the same hues for non-chart UI (badges, status dots).

### The Iridian foil — the one decorative motif

The brand has exactly one piece of visible decoration: a **soft-iridescent gradient** (`--foil`) that runs from coral → magenta → violet → cobalt → teal → chartreuse over ~120°. It exists to evoke the security-foil engraving on a Bank of Canada polymer banknote, and to give the design language a small piece of organic shimmer without descending into AI-deck gradient mush.

**Rules for the foil:**

- Used as a **1–2px strip** at the top of the masthead, beneath section heads, or as a hover-state underline.
- Used as the **foil dot** (`<span class="foil-dot">`) for status accents — e.g. next to the live "data refreshed" timestamp.
- Used as **`background-clip: text`** for the wordmark glyph (and *only* the wordmark) — never for full headlines.
- **Never** as a fill behind text. Never as a card background. Never animated faster than ~4s. Never used twice in the same eyefield.
- The `--foil-soft` variant (lower-alpha) is for hover-glow on data cells and active chart-control buttons.

If you take only one thing from this system, take this: the foil is a *garnish*, not a sauce.

### Type

Three families, all currently loaded via the Google Fonts CDN:

| Role     | Family            | Why |
|----------|-------------------|-----|
| Display  | **Newsreader**     | Variable serif with optical sizes and a beautiful italic. Reads as editorial without being precious. |
| Body     | **Instrument Sans**| Modern grotesque with the slightly narrower proportions practitioners read in (closer to Söhne than to Inter). |
| Mono     | **JetBrains Mono** | Tabular figures, clean zero, generous monospaced width that makes numerical readouts breathe. |

> ⚠ **Substitution flag:** No font files were shipped by the user. These three are stand-ins chosen for free + open-source + the right feel. If the project ever ships a paid family (e.g. **GT Sectra** for display, **Söhne** for body), drop the files into `fonts/`, swap the `@import`, and the tokens propagate. The CSS already references `Söhne` and `Source Serif 4` as next-in-line fallbacks.

**Type rules:**

- Display headings default to *italic Newsreader, weight 500*. This is the editorial voice signature. Roman Newsreader is reserved for stress-set inline runs.
- Every numerical readout (KPI tile, chart axis, table cell, status pill, footer timestamp) is **JetBrains Mono with `font-variant-numeric: tabular-nums`** — non-negotiable. Numbers must line up across rows.
- Eyebrows above section heads are **Instrument Sans 11px, semibold, uppercase, tracking 0.14em**, in `--ink-quiet`. Matches what the existing dashboard already does, but tighter.
- Body copy is 15/22 Instrument Sans. Captions are 11/16. Footnotes are 11px italic in `--ink-quiet`.
- The full scale lives in `--t-*` and `--lh-*` tokens.

### Spacing & rhythm

A 4-based scale (`--s-1` = 4px through `--s-12` = 96px). The dashboard is **dense** — most card-internal padding is `--s-4` (16px), most section gaps are `--s-7` (32px), full page rhythm is `--s-9` (48px). Don't reach for `--s-10` and above unless the content has earned the breathing room.

Layouts use a **12-column grid** at 1200/1440px, but the splash page is **5 + 1**: five status tiles across the top, then a single full-width hero panel. Deep-dive pages run as a single column of charts with a sticky table-of-contents rail on the left.

### Radii

Small. *Document-small.* `--r-sm: 3px` for inputs and pills, `--r-md: 4px` for cards, `--r-lg: 6px` for the focused chart panel. A 16px-rounded card would feel like an iOS widget; we want it to feel like a printed table.

### Borders, shadows, elevation

- **Borders carry the structure.** Every card is `1px solid var(--rule)`. The hairline reads cleanly against the cream paper.
- **Shadows are rare.** A card uses `--shadow-card` (a 1px-line shadow + a 1px-tinted ring, ~6% opacity). Popovers use `--shadow-pop` (one 12–28px soft drop). There is no third elevation level.
- **No inner shadows.** No glassmorphic blur. No coloured glows. The one exception: the active chart-control pill carries a `--foil-soft` hairline underline.

### Backgrounds & textures

The page is plain `--paper` with **no texture** by default. Optional: a very low-opacity guilloché pattern (the curlicue line work on a banknote) as an empty-state illustration only. **No** stock photography, **no** illustrated 3D objects, **no** abstract gradient blobs. A heroless dashboard is a feature, not a bug.

### Animation

- **Fast, restrained, no bounce.** All UI motion runs `--dur-1` (80ms) for hover swaps, `--dur-2` (140ms) for button press, `--dur-3` (220ms) for theme switch and drawer open, `--dur-4` (400ms) for chart redraw on transform-toggle.
- **Easing:** `cubic-bezier(0.2, 0.6, 0.2, 1)` — gentle decel, no overshoot. *No springs.* This is not a consumer app.
- **One signature loop:** the foil hairline at the top of the masthead drifts its gradient horizontally over ~8s on page load, then stops. Respects `prefers-reduced-motion`.

### Hover & press states

- **Buttons:** background steps one notch warmer (`--vellum` → `--rule`), text stays put, no opacity change.
- **Chart-toolbar pills:** the active pill carries the `--foil-soft` underline; hovering an inactive pill lifts its text from `--ink-sub` to `--ink`.
- **Table rows:** hover adds `--vellum` background, no transform.
- **Links:** underline-color animates from `--rule-strong` to `--ink` in 80ms. Featured `.link-foil` swaps the underline to the foil gradient on hover.
- **Press:** 1px translate-down on buttons (`transform: translateY(1px)`), no colour change. *No* shrink — shrinking communicates "I'm a touch target on a phone," which is not what this is.

### Blur & transparency

Sparingly. The fixed masthead uses `backdrop-filter: blur(8px)` over a 90%-alpha paper colour so charts scrolling underneath are *implied* but not legible. Modal overlays use a 60%-alpha paper scrim, no blur. **No** frosted-glass cards.

### Layout fixity

- **Masthead** is sticky at the top, 56px tall, with the foil hairline bottom border.
- **Section eyebrows** are sticky-on-scroll inside their section — they pin to the top of the viewport while their charts scroll past, then release.
- **Tooltips and chart-toolbar pills** are NOT sticky; they live with their chart.

### Imagery vibe

If imagery is ever introduced (it should be rare): **monochrome, slightly warm, lightly grained**. Print-style halftone over a single accent colour, not full-colour photography. The dashboard is text-and-chart-first; an image must earn its place by being *editorial*, not decorative.

### Cards

A card on this system is: `--card` background, `1px solid var(--rule)` border, `--r-md` (4px) radius, `--s-4` (16px) interior padding, `--shadow-card`. The eyebrow is sticky to the top edge, the data sits in the middle, the footnote sits flush to the bottom edge. No top-only colour stripe. No left-only colour border. No coloured background fills.

---

## Iconography

The dashboard uses **two icon traditions, no more**:

1. **Lucide** (`https://unpkg.com/lucide@latest`) for general UI — chevrons, info, external-link, settings, theme toggle, search, share. 1.5px stroke, 20px nominal. Loaded from CDN, restyled to inherit `currentColor`.
2. **Custom 1.5px-stroke marks** (in `assets/`) for the four economic concepts the framework cares about and Lucide doesn't quite cover: a *neutral band* glyph, a *target dot*, a *pass-through arrow*, and the *foil dot* status indicator.

> ⚠ **Substitution flag:** Lucide is a substitute, not a found asset. The original repo has no icon system — Plotly handles its own chart icons internally. If the project picks up its own custom set, replace the Lucide reference and update this section.

**Iconography rules:**

- **No emoji.** Anywhere. Ever. This was explicit in the brand brief.
- **No Unicode chars used as icons** (no `→`, `↑`, `✓` standing in for an icon). Use the SVG.
- **Real arrows for trend direction:** `↑` and `↓` *are* fine inline within numeric readouts (`CPI 2.3% ↑ 0.1pp`), but only inline with a number; never standalone.
- **Status uses the foil dot**, not an icon. (`<span class="foil-dot">`)
- **Stroke + fill consistency:** all icons are stroke-only, 1.5px, `currentColor`. No two-tone icons. No filled icons.
- **Logos at scale:** the wordmark (`assets/wordmark.svg`) renders at 16/20/24/32px; the standalone monogram (`assets/monogram.svg`) at 16/24/32/48. Both keep the foil-clipped accent dot.

---

## Tools & files this system gives you

If you're a designer or agent building inside this brand:

- **Start with `colors_and_type.css`** — `@import` it, and every token you need is there.
- **Reach for the JSX components in `ui_kits/dashboard/`** — `<Masthead>`, `<KPITile>`, `<ChartCard>`, `<ChartToolbar>`, `<RangePill>`, `<LegendChip>`, `<SectionEyebrow>`, `<DataReadout>`, `<FoilDot>`, `<Tooltip>`. Each is small, self-contained, and visually matches what `build.py` would produce on the live site.
- **Use the preview cards** in `preview/` as a reference — they're the same components in isolation, registered in the Design System tab.
- **Bring your own data.** The components are visual-fidelity recreations; they accept props and don't fetch.

---

## What's deliberately *not* in here

- A full re-implementation of the Python pipeline (fetch/analyze/build). That's the live product; this is the visual layer.
- Production-ready Plotly theming. (A future step — the chart-style guide already nails the structural rules; this system would generate the colour + type config for Plotly.)
- A logo lockup variant for print, social, or favicon. Stub assets are in `assets/`; refine when the wordmark settles.
- A marketing site. There is no marketing site. This is one person's tool.

---

## Caveats / open asks

See bottom of the project — the assistant has explicit caveats and asks for the user to iterate on font selection, the strength of the foil motif, and Vault-mode contrast.
