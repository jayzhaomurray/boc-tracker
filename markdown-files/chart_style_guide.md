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

## 5. Chrome

The structural elements around the chart proper. Goal: enough to navigate, no more.

**Title:**
Short. Says what the chart is about, not how it's computed. *"CPI Components"* not *"Canada CPI All-Items by Major Category, Year-over-Year."* Methodology and units belong elsewhere — footnote, axis label. Bold, ~0.8rem, dark gray.

**Footnote:**
Below the chart, small (~0.72rem), gray. Methodology, source caveats, the things specific to interpreting this chart correctly (e.g. WTI's April 2020 negative print). One sentence in most cases; two if a real caveat exists. Footnotes that don't say something specific shouldn't exist.

**Controls (transform + range buttons):**
In the chart header, right-aligned, opposite the title. Two button groups with a small gap between:
- Transform group (Level / M/M / 3M AR / Y/Y or analogous)
- Range group (2Y / 5Y / 10Y / Max)

Active button has a blue-tinted background. Buttons inline with the title row, never a second row.

**Legend:**
Below the chart, not inside it. Each item is a clickable button with a small color swatch and a label. Active items at full opacity; inactive items faded (~0.35) so the reader sees what's available without the chart looking cluttered. Thin top border separates legend from chart.

**Hover tooltip:**
Decimals chosen per-series — match what's conventionally informative for that series, and whether the additional decimal earns its place or is false precision.

| Series type | Decimals |
|---|---|
| Y/Y inflation, 3M AR, unemployment rate, wage growth, breadth deviations, CPI levels | 1 |
| M/M inflation, policy rates, 2Y yields, oil prices, USD/CAD | 2 |

For USD/CAD specifically: financial-market participants with positions watch four decimals, but for economic significance two is enough — the BoC rounds to two for analytical purposes.

Date format: `%b %Y` for monthly series; `%b %d, %Y` for daily. Series name appears in the small box on the right (Plotly's `extra` slot).

**Section heading + blurb:**
Above the first chart of a section. Heading is small uppercase (~0.72rem), letter-spaced, gray, with a thin gray underline. The blurb sits directly under it as ~0.9rem regular paragraph text. Generated by the framework pipeline; updates each fetch.

**Global controls (top of page):**
A single button group in the page header that overrides the date window across all charts simultaneously (2Y / 5Y / 10Y / Max). For the reader who wants to compare all charts at the same scale.

**About section:**
Bottom of the page. Project description, data sources cited, link to the GitHub repo for raw CSVs.

## 6. Chart treatment principles

Beyond the universal rules in sections 2–5, a few principles govern what kind of treatment to give a chart in the first place.

**Render the data the way it actually behaves.** Continuous values use straight lines; discrete-step values use step lines (`line_shape="hv"`). Policy rates step — central banks set rates in 25bp increments and hold between meetings. Yields and prices move continuously, so straight lines. The chart shouldn't imply behavior the data doesn't have.

**Smoothing exists to read trend through noise.** When a series is volatile enough that the level view obscures the trend a reader is looking for, provide a smoothing toggle. Raw shows by default; smooth is opt-in. So far this has only been applied to daily series (20-trading-day moving average), since daily data is where the use case has come up — but the trigger is volatility, not frequency, and the principle could extend to lower-frequency series that are also volatile (some commodity or financial series). Frequency-to-transforms mapping for ChartSpec lives in HANDOFF.md.

**When multiple measures span the same underlying concept, show the span.** A range band conveys *"here's where this family sits"* more clearly than five overlapping lines. Individual lines stay available as toggles for the reader who wants specifics. Used on Core Inflation (five core measures) and Wage Growth (four wage measures). Don't use on conceptually independent series — the span across food, energy, goods, services means nothing.

**Editorial overlays are sparing, use the editorial color, and are visually distinct from the chart's native lines.** When a chart's analytical question depends on a comparison series that doesn't naturally belong on the chart, the overlay sits in red (the anchor color for editorial overlays) and is rendered as a dotted line (`dash="dot"`) so the reader sees at a glance that it's a comparison, not a peer of the chart's other lines. Currently only on Wage Growth (Services CPI alongside the wage measures, because the wage-vs-services-CPI relationship is the central question). Every additional line costs reader attention.

**Controls only advertise meaningful interactions.** If a series has only one meaningful read, don't expose toggles that suggest otherwise. Currently on Unemployment Rate (`static=True`) — the level is the news; M/M change of unemployment isn't what people watch. Better to hide a control than to give the reader a button that produces nothing useful.

**Horizontal reference bands for known thresholds.** When a chart has a meaningful threshold range that helps the reader interpret the data (the BoC's neutral rate range of 2.25–3.25% on Policy Rates, in principle a NAIRU range on Unemployment, etc.), draw it as a translucent gray horizontal band (`rgba(180, 180, 180, 0.35)`) across the chart, layered below the data lines. Same fill as the range-band overlay convention; different role — this band is a *static reference value*, not a synthesis of multiple measures. Use sparingly: the threshold has to be widely accepted, citable, and stable. Document the source in the footnote.

## 7. Default-selection conventions

Cross-cutting rules I keep coming back to when adding or revising a chart. Sections 2–6 cover the universal aesthetics; this section is about the per-chart calls.

- **Defaults match how practitioners conventionally read the indicator.** Starts as 3M / 12M moving average (CMHC, BoC MPR), permits as level, prices as Y/Y for headlines. If the convention says "nobody looks at growth rates of this," don't expose growth-rate toggles.
- **Toggle placement follows what the toggle controls.** When the toggle decides which lines are visible, put it in the legend (the legend *is* the toggle bar). When the toggle changes y-axis units or transformation globally for every line, put it as a button-bar above the chart. Don't mix idioms on the same chart.
- **Right unit for the data range.** Pick the scale that yields clean 2–4-digit numbers across the visible range. Use $M or $B instead of $k when values are in the millions/billions; use bp instead of % when values are sub-1pp; use % instead of decimal ratio when values are <1. Avoid leading zeros and trailing-zero strings ("$8,132,058k").
- **Default date range matches data availability.** When the series starts late (e.g. Jan 2018 for the current residential permits table), default to Max — a 10Y window wastes space showing pre-data emptiness. The standard 10Y default applies when the series is genuinely longer.
- **Re-index to a common base when overlaying two index series.** NHPI (Dec 2016 = 100) and CREA MLS HPI (2019 = 100) only make sense on the same axis if both are rebased to the same date. Compute the rebase at build time in `_add_derived_series`, never modify the source CSV — and pick a base date both series cover (Jan 2020 is the current convention; pick the most-recent common date that's a sensible economic anchor).
- **Hide controls that don't add a meaningful read.** §6 already says this for transforms; the same applies to growth rates on noisy SAAR series, smooth toggles on already-smooth series, and Y/Y on series that don't have 12 months of history yet.

## 8. How this guide is used

This guide codifies what's been learned from nine charts. It will be wrong for the tenth chart in some way that isn't yet visible — that's fine. The guide is meant to evolve.

**The workflow:**
- Routine decisions that fit a principle: just follow it.
- Decisions the guide doesn't cover: pick a sensible default in the spirit of section 1, note the choice in the commit message.
- A new decision conflicts with a principle: stop, surface the case, propose either revising the principle (if it'll recur across charts) or documenting an exception in this section (if it's genuinely one-off).
- Multiple recent decisions are pulling against a principle: flag that as a candidate for revision; don't accumulate exceptions.

Never silently break a principle. Never silently rewrite one. Both require explicit sign-off.

**Things to avoid:**
- Quietly breaking a principle for one chart and leaving the rest of the dashboard inconsistent
- Adding optional fields to spec dataclasses to encode every per-chart variation; restructure rather than crowd
- Generalizing from a single chart's behavior; verify against multiple charts before codifying

**Known one-off exceptions:**
- **Oil chart's `ymin=0`.** WTI briefly traded negative in April 2020 due to a futures-contract anomaly. Including that one observation distorts the y-axis for every other period in the chart, so the chart floors at zero and the footnote calls out the omission. Most "below-zero" states are real and should be shown; this is the rare case where excluding is right.
- **WCS on oil (`smooth=False`).** WCS data is monthly while WTI and Brent are daily. When the user clicks the smooth toggle, WTI and Brent smooth to a 20-day moving average; WCS stays raw because there's nothing to smooth. The per-line `smooth=False` flag exists for this case.
