---
name: boc-tracker-design
description: Use this skill to generate well-branded interfaces and assets for BoC Tracker, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping a practitioner-grade Bank of Canada / Canadian macro dashboard.
user-invocable: true
---

Read the `README.md` file at the root of this skill, and explore the other available files (`colors_and_type.css`, `assets/`, `preview/`, `ui_kits/dashboard/`).

Key conventions:
- The brand voice is "central-bank dispatch": British-Canadian spelling, declarative, no hedging, no emoji, no first person. Always cite the source agency and vintage.
- The visual system is paper + ink + iridescent foil — warm cream background, deep ink-navy text, hairline rules, no drop-shadows. A subtle holographic foil gradient is the one decorative motif; use it sparingly (eyebrow dots, 1px section rules, hover underlines).
- Type pairing: Newsreader (italic display serif for headlines and chart titles) + Instrument Sans (body) + JetBrains Mono (all numerals, units, source stamps).
- Always render numerals with `font-variant-numeric: tabular-nums`. Deltas carry units (`pp`, `bp`, `%`). The 2% inflation target is a dotted reference line, never solid. Neutral-band rectangles are translucent fills, never solid blocks.
- Two themes: `paper` (default) and `vault` (dark, applied via `data-theme="vault"` on any ancestor).

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out of `assets/` and `ui_kits/dashboard/` and create static HTML files for the user to view; load `colors_and_type.css` for the tokens. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions (Are they extending the splash? Adding a new deep-dive? Building a one-off chart card? Light or dark?), and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.
