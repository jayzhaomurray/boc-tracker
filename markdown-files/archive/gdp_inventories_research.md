# GDP Growth Contributions — Research Notes

*Working note. Not reader-facing. Covers: StatsCan methodology, empirical reconciliation, chart errors, design recommendations.*

---

## 1. StatsCan methodology: how inventories are treated in Table 36-10-0104

**Inventories are a separate, explicitly measured line item — not a sub-category of gross fixed capital formation and not a residual.**

In the System of National Accounts as implemented by StatsCan, the expenditure-based GDP identity is:

> GDP = Final consumption expenditure + Gross fixed capital formation + **Investment in inventories** + Exports – Imports + **Statistical discrepancy**

"Investment in inventories" (a.k.a. change in inventories) is distinct from "gross fixed capital formation." Gross fixed capital formation covers assets with a useful life exceeding one year. Inventory change covers net additions to stocks held for future sale or use: they are separate rows in the table, separate vectors, and separate conceptual categories.

However, StatsCan's user guide (Chapter 5, Catalogue 13-606-G) notes this important caveat:

> *"Inventory change is considered to be among the most difficult components to measure in the national accounts. Unlike other items in the income and expenditure accounts, investment in inventories is not formally reconciled with the estimates of inventory change in the supply and use accounts."*

It adds that inventories function as *"the gap between aggregate production plus imports and final demand during the accounting period."* In practice this gives it a residual-like quality — it is directly measured but absorbs timing and measurement noise in a way the other categories do not.

The **statistical discrepancy** is a separate sixth term added to expenditure-based GDP to reconcile it with the income-based measure. StatsCan splits the total discrepancy equally between the two measures. In the contribution-to-growth vectors (Table 36-10-0104, dimension-2 type = 4), the statistical discrepancy appears as its own member (coordinate 1.4.1.29 = v79448579) and is included in the total GDP contribution aggregate (coordinate 1.4.1.30 = v79448580).

**In the National Accounts hierarchy:** the broadest "gross capital formation" aggregate = GFCF + inventories. At the detailed level they are always listed separately. At the BoC summary level they are also listed separately (see Section 4).

**Sources:** Statistics Canada Catalogue 13-606-G, Chapter 5 (https://www150.statcan.gc.ca/n1/pub/13-606-g/2016001/article/14620-eng.htm); confirmed empirically via Table 36-10-0104 WDS API coordinate structure.

---

## 2. Empirical reconciliation: do the six categories sum to headline?

### Short answer

With the **correct sign on imports**, the six components sum to the annualized Q/Q AR headline within a mean absolute residual of **0.57 pp** across 259 quarters (1961–2025 Q4). In the modern era (2021–2025) the mean abs residual is **0.11 pp** — essentially rounding noise. The residual is not a systematic bias; it averages -0.065 pp (near zero). The planned reconciliation test will close to well within 1 pp in normal times.

### Critical finding: imports sign is wrong in the current code

The raw StatsCan vector v79448576 uses this convention:
- **Positive value** = imports grew (a drag on GDP)
- **Negative value** = imports fell (a boost to GDP)

This is the *inverse* of how a GDP contributions chart should display imports. For the bars to read correctly (positive = adds to growth), the imports series needs to be negated: contribution = -v79448576.

Empirical proof from the table structure: the algebraic identity that closes to near-zero is:

```
c + g + GFCF + inv + ex + (-im_raw) + NPISH + stat_disc = GDP Q/Q AR
```

Not:
```
c + g + GFCF + inv + ex + im_raw = GDP Q/Q AR  ← wrong sign
```

The fetch.py comment says `"sign-flipped: positive = imports fell"` — but **no `scale_factor = -1` tuple is present** in `STATSCAN_SERIES` for that vector. The raw API value is stored and plotted directly. The comment describes the *intended* convention; the *actual* code does not apply it.

Concrete example — Q1 2025 (tariff front-running quarter, imports surged):
- v79448576 = +1.314 (positive = imports grew, drag on GDP)
- Correct contribution to show in chart = -1.314 pp (negative bar)
- Current chart shows = +1.314 pp (positive bar — inverted, incorrectly implies boost)

Q3 2025 (imports fell):
- v79448576 = -3.765 (negative = imports fell, boost)
- Correct contribution = +3.765 pp (positive bar)
- Current chart shows = -3.765 pp (negative bar — inverted)

### What explains the residual (~0.57 pp mean abs)?

Two components are missing from the six-series set:
1. **NPISH** (non-profit institutions serving households) — member 8 in the table, coordinate 1.4.1.8. Q3 2025 = +0.032 pp; Q4 2025 = +0.028 pp. Always small (< 0.15 pp typically).
2. **Statistical discrepancy** — member 29, coordinate 1.4.1.29. Q3 2025 = +0.153 pp; Q4 2025 = -0.216 pp. Usually < 0.3 pp in the modern era.

Together these explain the full residual. The residual shrank over time: mean abs 1.16 pp in the 1960s vs 0.11 pp in 2021–2025, consistent with improvements in national accounts measurement.

The total GDP contribution is v79448580 (coordinate 1.4.1.30), not v1594571783. The headline CSV series v1594571783 is the simple Q/Q % (non-annualized), rounded to one decimal. The contribution vectors are in annualized percentage points (pp AR). Comparing contribution sums to the Q/Q AR computed from the level series (v62305752) is the correct benchmark.

---

## 3. Conceptual errors in the current stacked bar chart

### (a) Imports sign — material error

As documented above, the imports bars are displayed with inverted sign. In Q1 2025 (tariff rush), the current chart shows imports as a +1.3 pp positive bar, implying it boosted GDP — when in fact imports surged and dragged GDP. This is the opposite of the intended "Less: imports (sign-flipped)" labeling and is economically misleading. This needs to be fixed.

Fix is one line: change `STATSCAN_SERIES["gdp_contrib_imports"]` from `79448576` to `(79448576, -1)` in fetch.py, which applies the scale factor on fetch so the CSV stores the correctly signed contribution. Alternatively apply `y = -df["value"]` in `_build_stackedbar_panel` specifically for the imports trace — but the fetch.py fix is cleaner (source-of-truth in the data, not the chart builder).

### (b) Sign-flipped imports as a presentation choice — sound in principle

Showing imports as a "positive contribution when imports fell" is the standard BoC and StatsCan convention. The April 2026 MPR uses it. The issue is the sign is currently applied backwards, not that the convention is wrong. Once the sign is corrected, this is fine.

### (c) Inventories as a stacked component — not misleading, but needs labeling context

Inventories are not a residual in the strict sense — they are directly measured. But they behave residual-like (high noise, mean near zero, occasionally large) and are conceptually different from the demand-driven categories. The concern is valid but the appropriate response is footnote/labeling clarity, not removing inventories from the chart. The current footnote does not flag their volatile nature.

The BoC's own MPR framing separates inventories from "final domestic demand" precisely because they are volatile and cycle-mean-reverting, so showing them as a distinct color in the stacked bar is the right treatment — users should just understand what they are. Recommended footnote addition: note that inventories are the most volatile component and average near zero over full cycles.

### (d) Reconciliation test soundness

The user's planned test — sum subcategories, compare to headline — is sound **with two caveats**:
1. Use the annualized Q/Q AR (computed from level series), not the rounded Q/Q % in the headline CSV.
2. The sum will miss NPISH (~0.03 pp) and statistical discrepancy (~0.05–0.15 pp in the modern era). Set the tolerance at ±0.5 pp for a pass; flag anything over ±1 pp as potentially a data-vintage issue.

The stat discrepancy does not make the math "not close" — it is genuinely small in modern data. But the imports sign bug does make the math very wrong (multiple pp off) and must be fixed first.

---

## 4. Simple-vs-detailed view: where inventories go

### BoC convention

The BoC MPR presents GDP contributions in three buckets:
1. **Final domestic demand** (consumption + government + gross fixed capital formation — no inventories)
2. **Net exports and inventories** (exports – imports + inventories + statistical discrepancy bundled together)

Source: April 2026 MPR footnote: *"Net exports and inventories includes Statistics Canada's statistical discrepancy."* The July 2025 MPR text: *"Final domestic demand, exports and imports are calculated as contributions to GDP growth. These components do not add up to total GDP growth because inventories are not included."*

So the BoC bundles inventories with net trade in the simple view, explicitly because inventories are the "swing factor" that can't easily be assigned to domestic demand or trade.

### Recommendation for the simple/detailed toggle

**Simple view (two + one stacks):**
- Stack 1: **Final domestic demand** = consumption + government + GFCF (no inventories)
- Stack 2: **Net exports** = exports – imports
- Separate bar / third bucket: **Inventories + residual** = inventories + NPISH + stat disc (or just inventories labeled clearly)

Rationale: bundling inventories into net exports (the BoC's actual practice) is justifiable from a "this is what's left" standpoint, but it obscures the trade picture. Showing inventories as a third explicit bucket is more transparent and matches how practitioners read GDP reports: "domestic demand did X, trade contributed Y, inventories swung Z." Option (b) — show as a distinct third bucket — is the best design for a practitioner dashboard.

Do **not** drop inventories from the simple view (option c). They are too large in volatile quarters (Q1 2025: +4.1 pp, Q4 2025: -4.2 pp) to ignore; dropping them would make the stacks not sum to headline in those quarters and confuse the user more.

Do **not** bundle inventories into fixed investment (option a). Conceptually wrong — inventories are in the GDP identity for a different reason from GFCF, and practitioners distinguish them.

**Detailed view (current six-component breakdown):** keep as-is, after fixing the imports sign.

---

## 5. Recommendations

### 5.1 Headline GDP line overlay on the stacked bars — Yes, add it

Add a thin black line (or dark grey) trace showing the annualized Q/Q AR headline on top of the stacked bars. The rationale:
- The bars are supposed to sum to headline, but with NPISH and stat disc missing they don't perfectly. A headline line makes the visual reconciliation direct — users can see whether the bars track the line closely.
- It adds a natural anchor for quarters where one component dominates (e.g., Q3 2025: inventories -2.1 pp, imports +3.8 pp; the line shows the net result was +2.4%).
- Clutter concern is low: a single thin overlay line on a stacked bar doesn't compete with the colored bars. Use a dashed or semi-transparent style.

The correct data source for the overlay is the annualized Q/Q AR, computed from v62305752 (which is already in `data/gdp_quarterly.csv`) — not the rounded Q/Q % in v1594571783. Or fetch v79448580 (the total GDP contribution vector in the same contribution-type series), which is the cleanest match.

### 5.2 Automated reconciliation test at fetch time — Yes, add it

A fetch-time sanity check in `fetch.py` is worthwhile, specifically:
- Sum the six contributions (with `-imports` correction) and compare to Q/Q AR for the latest two quarters.
- Tolerance: ±0.5 pp passes, ±1.0 pp warns, >±1.5 pp errors.
- Print a one-line result. Do not gate the fetch on this; it is diagnostic, not blocking.

This catches data-vintage mismatches (StatsCan sometimes releases a revision that updates the level series before the contribution vectors update), sign errors on re-fetch, and any future vector ID changes.

### 5.3 Fix the imports sign — required before any other GDP chart work

Change `STATSCAN_SERIES["gdp_contrib_imports"]` from `79448576` to `(79448576, -1)` in `fetch.py`. Also update the footnote in `build.py` from *"Less: imports is sign-flipped"* to *"Imports contribution: positive = imports fell, boosted growth; negative = imports rose, dragged growth."* Re-run `fetch.py` to regenerate the CSV with corrected values, then rebuild.

### 5.4 Framework writeup note for GDP section

When writing or updating `analysis_framework.md` for the GDP section:
- Inventories: flag as high-volatility (std ~3 pp, comparable to consumption), mean near zero over cycles (~0.05 pp long-run); large swings are often inventory correction/rebuilding cycles, not demand signals.
- Statistical discrepancy: typically < 0.3 pp in modern data; included in the BoC's net-exports-and-inventories bucket; too small to call out independently in blurbs.
- The headline Q/Q AR for blurb generation should use the level series (gdp_quarterly.csv), not the rounded v1594571783. Compute `((gdp_q / gdp_q.shift(1))**4 - 1) * 100` directly.
- Simple framing: final domestic demand (C + G + GFCF) vs net exports (X – M) vs inventories (swing factor). This maps directly to how the MPR discusses GDP.

---

*Primary sources:*
- *Statistics Canada Catalogue 13-606-G, Chapter 5 (Income and Expenditure Accounts):* https://www150.statcan.gc.ca/n1/pub/13-606-g/2016001/article/14620-eng.htm
- *Bank of Canada MPR April 2026:* https://static.bankofcanada.ca/uploads/pdf/mpr-2026-04-29.pdf
- *Bank of Canada MPR July 2025 (Canadian Conditions):* https://www.bankofcanada.ca/publications/mpr/mpr-2025-07-30/canadian-conditions/
- *StatsCan Table 36-10-0104 WDS API — contribution-type vectors (dim2=4):* empirically mapped via getDataFromVectorsAndLatestNPeriods endpoint
