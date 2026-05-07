# Chart Style Guide

This document defines the formatting conventions all charts on the BoC tracker follow. It exists so fixes don't drift across chart types and so a future agent (or me, weeks from now) doesn't re-derive what's already been decided.

## 1. Principles

The dashboard is for an informed reader scanning quickly. Every aesthetic choice serves that reader.

- **Signal over chrome.** If a visual element doesn't directly help the reader read the data, drop it. Short titles, no decorative borders, no captions that restate the obvious. Methodology and caveats go in the footnote, not the title.

- **Charts adjust to what's visible, not to what could be visible.** When a series is toggled off, the y-axis fits what remains. Build-time pre-computation of axis ranges across all possible series is wrong by construction; the axis must respond to the current view.

- **Defaults are cycle-agnostic.** A chart should look right in any part of the cycle. Defaults shouldn't assume inflation is high or low, rates are rising or falling, or that any particular year is the reference. The data tells the story; the chart shows the data.

- **Consistency across chart types.** Two charts with similar shape (e.g., both multi-line with legend toggles) behave identically — same color palette, same legend behavior, same y-axis logic, same tick density. Special-cases only when the data genuinely demands it (step rendering for rate decisions; y-floor for oil after April 2020).

- **Compactness.** The reader should be able to see all charts on the page without excessive scrolling. Each panel is ~260px tall; chrome around it is minimal.

## 2. Y-axis

The y-axis is the most consequential aesthetic decision on a chart.

**Zoom in as far as possible without cropping.** Whitespace above and below the data is wasted space — it shrinks the visible variation and makes the chart less useful. The axis fits the data tightly.

**Enough gridlines that a reader can eyeball any value, but not so many they clutter.** Aim for 5 labelled ticks; never fewer than 4. The reader looking at any point on a line should be able to roughly read off a number.

**Familiar round increments only.** Tick intervals come from the set {1, 2, 2.5, 5} × 10^k — so 0.05, 0.5, 1, 2, 2.5, 5, 10, 25, 50, … These are the increments the human brain naturally uses. Ticks anchor at zero, so they land on meaningful round numbers (0, 1, 2…) rather than offsetting from the data minimum.

**Decimals consistent across all ticks on an axis.** The format follows the tick interval — dtick of 1 → integers, dtick of 0.5 → one decimal, dtick of 0.05 → two decimals. Never "1.3" alongside "1.35" on the same axis.

**Recomputes whenever visibility changes.** Toggling a series, switching transforms, changing the date window all recompute the range, tick interval, and tick format from currently visible data. The axis follows what's actually being shown.

**Unit label sits inside the plot area, top-left, small and gray.** The numbers down the side are bare; the unit shows once, overlaying the top-left corner of the plot — the convention used by Bloomberg, the FT, and most financial publications.

| Use | Label |
|---|---|
| Y/Y, M/M, 3M AR, rates, unemployment | `%` |
| Breadth deviations | `pp` |
| CPI level series | `Index` (base year in footnote) |
| Oil prices | `USD/barrel` |
| USD/CAD | `CAD per USD` |

For charts whose transforms switch units (CPI: `%` for Y/Y / M/M / 3M AR, `Index` for Level), the label updates with the transform.

## 3. Defaults

The first thing the reader sees should be the most informative view of each chart, and the same defaults should apply across charts of the same type so the dashboard feels consistent.

**Date window:** 10 years for every chart. Long enough to show a full cycle (a stable pre-pandemic period, the 2020 COVID disruption, the 2021–2023 inflation cycle, the 2024–2026 resolution) but tight enough that recent moves are legible. The 10Y window is the same regardless of how far back the underlying series goes.

**Transform:**
- For derived series (Y/Y / M/M / 3M AR available): default to **Y/Y**. It cancels seasonality, is the number news cites, and is the most-comparable read across series.
- For raw series with no transform options (rate levels, unemployment, FX): default to the level.
- For daily series with a smooth toggle: default to the raw level (not the smoothed line). Raw is the truth; smooth is a reading aid.

**Multi-line visibility:**
- Primary line on, secondaries off. The "primary" is whatever a reader scanning quickly would expect to anchor on.
  - SA over NSA (NSA is for comparison in M/M view)
  - Canada over US (BoC over Fed; Canada 2Y over US 2Y; WTI over Brent and WCS)
- Range bands stay on (they're the synthesis, not a competing line).
- Editorial overlays (e.g. Services CPI on the wage chart) stay on by default since they exist specifically to add the comparison the reader needs.

**Smooth toggle defaults to off.** When a chart offers a Level / 20d Avg toggle, the raw series shows by default. The smoothed view exists for the reader who wants to see the trend without daily noise; it's not the default story.

**Exceptions are made when two adjacent charts would otherwise tell the same default story.** When two charts have overlapping primary content, change one chart's defaults so each tells a distinct story at first glance. The CPI Components chart is the precedent: it sits next to Core Inflation, both naturally lead with headline Y/Y, so CPI Components defaults to headline + food + energy (the volatile decomposition) while Core Inflation defaults to headline + range band (the underlying-trend view).

## 4. Color palette

Color carries information when it can; otherwise it's just aesthetics. Two principles:

1. **Consistent identity.** When a concept appears on multiple charts (Canada, US, BoC, Fed), it gets the same color on every chart. The reader builds an instant association: "blue is Canada in this dashboard."
2. **Color earns its place.** Use color deliberately when it encodes identity, category, or hierarchy. When it's just visual texture, pick something that looks good in context and doesn't compete with where information is encoded.

**Anchor colors (consistent everywhere):**
- `#1565c0` (blue) — Canada, BoC, the primary domestic series
- `#c62828` (red) — US, Fed, or editorial overlay when no foreign comparison applies (e.g. Services CPI on the wage chart)

**Hierarchy on a single chart:**
- The primary line (visible by default) gets a saturated anchor color.
- Variants of the primary (NSA next to SA; LFS Permanent and SEPH next to LFS All; CPI-trim and CPI-median as overlays on Core Inflation) use cool grays: `#546e7a`, `#78909c`, `#90a4ae`. They recede.

**Categorical palette (for conceptually independent series):**
When lines represent independent categories rather than variants of one thing — Food, Energy, Goods, Services on CPI Components — pick from this four-color set, chosen to be visually distinct and colorblind-friendly:
- `#ef6c00` (orange)
- `#00897b` (teal)
- `#7b1fa2` (purple)
- `#388e3c` (green)

If a fifth is needed, `#5d4037` (dark brown). Beyond five, restructure rather than crowd more colors in.

**Range bands:**
- `rgba(180, 180, 180, 0.35)` — translucent gray fill, no border. Always gray, never colored. The band is a synthesis, not a line.
