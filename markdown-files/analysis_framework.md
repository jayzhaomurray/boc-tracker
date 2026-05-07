# Analysis Framework

Internal analytical brief for generating dashboard blurbs. Each section defines the question being answered, the signals to evaluate, the thresholds that matter, and what to surface in the output.

The framework must work in any part of the cycle — high inflation or low, hiking or cutting, tight labour market or slack. Do not assume a direction is desirable or expected. Describe what the data shows and what it implies.

---

## Blurb structure

Each blurb follows this shape:

1. **Sentence 1 — Takeaway.** The bottom-line conclusion. Synthesize, do not just describe. When measures disagree, defer to the BoC's preferred core measures rather than the model's opinion. Never forecast (no "will continue to..."), never prescribe policy (no "the BoC should..."), never call something "transitory" or "persistent" beyond what the current data shows.
2. **Sentence 2 — Anchor.** The most recognized number for the section: headline CPI for inflation, BoC overnight rate for policy, unemployment rate for labour, USD/CAD or oil Y/Y for external conditions.
3. **Sentence 3 (and possibly 4) — Support.** The strongest evidence for the takeaway, in order of importance.
4. **Closing sentence — Nuance or tension.** The most important caveat or contradicting signal. Plain language. No parallel construction unless it earns it.

Length: 3 sentences typically; 4 if there is a real tension that needs the closing slot.

---

## Writing style

Blurbs should read like an analyst writing for an informed reader, not a journalist explaining analysis.

- **Plain verbs.** *Was, is, sits, runs.* Avoid *ran at, has returned to, pulled back, firmed up.* State positions, not journeys.
- **Semicolons for parallel facts of equal weight.** Two independent observations get a semicolon, not a subordinating clause.
- **No explanatory codas.** Do not add *"indicating X"* or *"the read here is Y."* Let the data carry the inference.
- **Conventional shorthand.** *y/y, m/m, q/q, 3-month, pp, bps.* Not *year-over-year, three-month, percentage points, basis points.*
- **Plain hedges.** *Roughly, near, broadly.* Not *broadly returned to, hints at, appears to be.*
- **Embed numbers in analytical sentences.** Do not lead with *"As of March, headline CPI was 2.3%."* Instead: *"Headline CPI was 2.3% y/y in March."* The number is part of a sentence, not the sentence's reason for existing.

---

## Verification, not speculation

If a claim can be verified with available data, verify it before stating it. The framework signals point at likely causes (e.g., *"if headline below core, food or energy is masking pressure"*); these are starting points for analysis, not conclusions to be repeated. When the framework points at a candidate cause, look at the actual food and energy Y/Y numbers and state which is the driver. Never guess at a category attribution when the category-level data is on hand.

Main-page blurbs work from top-level aggregates only — never from individual CPI components or sub-categories. If a question requires component-level decomposition, it belongs on a future deep-dive page, not the main blurb.

---

## Inflation

**Question:** How does inflation compare to the BoC's 2% target, and what is the underlying trend?

**Data:** cpi_all_items (M/M, 3M AR, Y/Y), cpi_trim, cpi_median, cpi_common, cpix, cpixfet, cpi_food (Y/Y), cpi_energy (Y/Y), cpi_goods (Y/Y), cpi_services (Y/Y), cpi_breadth (share above 3%, share below 1%). M/M and 3M AR are computed on the SA cpi_all_items series; Y/Y is identical between SA and NSA.

**Signals to evaluate:**

- Where are core measures relative to 2%? How far above or below, and are they moving toward or away from target?
- Is the band of core measures tight or wide? A tight band means the measures are telling a consistent story. A wide band means the choice of measure matters.
- Is headline CPI above or below core, and what is driving the gap? When headline diverges from core by more than ~0.3pp, look at food Y/Y and energy Y/Y to identify the driver. State the actual food and energy Y/Y numbers; do not guess at attribution. Goods Y/Y vs services Y/Y can also be informative if the gap is not in food or energy.
- CPI breadth: classify the breadth signal into one of four states using the deviations from the 1996–2019 historical averages. Define `tilt = (above-3% share deviation) − (below-1% share deviation)`. The four states are:
  - **Broad-based pressure** — share above 3% elevated *and* share below 1% depressed (positive tilt). Many components running hot, few cold.
  - **Broad-based softening** — share above 3% depressed *and* share below 1% elevated (negative tilt). Many cold, few hot.
  - **Clustered near target** — both shares near their historical norms (small tilt, both deviations near zero). Most components in the 1–3% middle range.
  - **Polarized** — both shares elevated. Rare; some components hot *and* some cold simultaneously, with few in the middle.
- Is M/M momentum consistent with 2% annualized? ~0.17%/month is the neutral threshold (precisely 0.165%). Sustained prints above 0.3% signal acceleration; sustained prints below 0.1% signal deceleration.
- Is the 3-month annualized rate above or below 2%? This is the cleanest read on current momentum independent of base effects.

**Thresholds:**
- 2% = BoC target
- 1–3% = BoC control range
- ~0.17%/month ≈ 2% annualized
- Tight band = all core measures within ~0.5pp of each other
- Headline-core gap > 0.3pp = look at food/energy/services for the driver

**What to surface:** Open with a takeaway that synthesizes the picture (sentence 1). Anchor on headline CPI Y/Y (sentence 2), with core context if it changes the read. Bring in supporting evidence — breadth, M/M, 3M AR — in order of importance. When headline and core diverge, name the driver using the verified food or energy Y/Y figure rather than the framework's hypothetical "energy or food is masking" language. Defer to core measures over headline as the more representative read on persistent inflation, since this is the BoC's own convention.

When citing breadth in the blurb, lead with the state name (*broad-based pressure*, *broad-based softening*, *clustered near target*, or *polarized*). The two-threshold comparison is for evaluating the signal internally; the blurb output uses the synthesis. When both threshold signals point the same way, cite one of them as evidence and drop the other — the second is redundant. When the two signals disagree (polarized state, or a transition where one has normalized but the other has not), cite both since they are telling different stories. Phrase the components as "running well above target" / "running well below target" rather than "above 3%" / "below 1%" — the precise threshold belongs on the chart, not in the prose.

---

## Monetary Policy

**Question:** What is the BoC doing across its policy tools — rate and balance sheet — and what is the market pricing for the rate path?

**Data:** overnight_rate (BoC), fed_funds (Fed), yield_2yr (Canada), us_2yr (US), bocfed_spread (overnight − fed_funds), can2y_overnight_spread (Canada 2Y − overnight), can_us_2y_spread (Canada 2Y − US 2Y), boc_total_assets, boc_goc_bonds, boc_settlement_balances (all in C$ billions).

**Rate signals:**

- Where is the BoC overnight rate relative to the neutral-rate band? The BoC's official neutral-rate range is **2.25–3.25%** (annual r* update). Above 3.25% = restrictive (actively slowing the economy); below 2.25% = accommodative (actively stimulating); inside the band = roughly neutral.
- How far has the BoC moved from its most recent peak or trough, and in which direction? How does the magnitude compare to the Fed's move over the same period? Which central bank moved first.
- BoC−Fed spread (`bocfed_spread`): level and direction. Negative spread (BoC below Fed) puts downward pressure on CAD via interest rate parity; positive spread supports CAD. Sustained spreads outside ±100bp are historically unusual.
- Canada 2Y − Overnight spread (`can2y_overnight_spread`): a *directional* signal of the market-implied policy path, not a precise basis-point forecast. The 2Y embeds a term premium — BoC ACM-model estimates suggest roughly 0–40 bp in normal regimes (2003–2019) and 20–60 bp in the elevated post-2023 regime (see BoC's [Financial Stability Indicators](https://www.bankofcanada.ca/rates/indicators/financial-stability-indicators/) for the published decomposition). The spread is materially distorted during QE/QT episodes (the 2020–2022 GBPP suppressed 2Y GoC ~20 bp below OIS-equivalent through scarcity), flight-to-quality stress, fiscal-supply shocks, and stretches of elevated inflation uncertainty — in those windows the level moves as much from premium repricing as from expectations. **Defensible reads:** direction of shift over weeks to months; large inversions (more negative than -0.75pp) clearly signaling cut expectations regardless of premium uncertainty; broad qualitative magnitude bands ("modest cuts priced," "meaningful cuts priced"). **Not defensible:** specific basis-point counts ("X bps of cuts by year-end"); reading the level as pure expectations during distorted regimes; mechanically dividing the spread by 25 bp to count meeting moves. Spreads outside ±0.5pp are notable in normal regimes; treat with extra caution in distorted ones.
- Direction of `can2y_overnight_spread` over the last 1–3 months: falling = market expectations shifting dovishly even if the BoC has not moved; rising = shifting hawkishly.
- Canada 2Y − US 2Y spread (`can_us_2y_spread`): a cross-country yield differential, *not* a clean read of relative policy expectations — both legs carry their own term premiums and convenience-yield effects, which can move independently of expectations. Negative = Canadian rates expected lower than US (broadly CAD-negative; often reflects weaker Canadian growth/inflation outlook relative to the US). Positive = Canada expected tighter — historically rare. Most useful read alongside `bocfed_spread`: when the two move together, both reflect a coherent shift in relative policy stance; when they diverge meaningfully, the market is pricing either a future change in stance *or* relative-premium movements (e.g. fiscal supply, convenience-yield shifts, balance-sheet operations affecting one country more than the other). Flag both interpretations rather than asserting one.

**Balance sheet signals:**

- Direction of `boc_total_assets` and `boc_goc_bonds` over the last 6–12 months: rising = QE; falling = QT (currently passive, GoC bonds rolling off as they mature); flat = steady state. The slope tells you the pace.
- Distance from anchors: pre-COVID baseline of total assets was ~$120B (early 2020); peak QE was ~$575B (April 2022). Where is the balance sheet now relative to those two reference points? "QT is done when the balance sheet is normal" turns on this.
- Alignment between `boc_total_assets` and `boc_goc_bonds`: when they move together, the change is pure QE/QT. When total assets diverges from GoC bonds (typically rises faster), something non-policy is happening — FX swap line activity, term repos, advances/lender-of-last-resort facility — that should be flagged as a stress signal rather than a policy signal.
- `boc_settlement_balances` level: the operating regime indicator. The BoC declared the floor system permanent in 2025, so steady-state settlement balances will sit well above the pre-COVID corridor-system level (which was near zero). The current level relative to the BoC's stated steady-state target is the relevant read; deviations signal stress or transition.

**Thresholds:**
- 2.25–3.25% = BoC's official neutral-rate range
- `can2y_overnight_spread` outside ±0.5pp = market pricing meaningful path (in normal regimes; treat with caution during QE/QT or stress)
- Canadian 2Y term premium ≈ 0–40 bp in normal regimes (2003–2019), 20–60 bp post-2023; materially distorted during QE/QT and stress episodes
- `bocfed_spread` outside ±100bp = historically unusual
- ~$120B = pre-COVID balance sheet baseline (early 2020)
- ~$575B = peak QE balance sheet (April 2022)
- Floor system permanent (BoC announced 2025): settlement balances anchored at floor-system steady state, not pre-COVID corridor levels

**What to surface:** Lead with where the BoC rate sits relative to the neutral band — this is the foundational policy positioning read. Bring in the balance sheet trajectory (QE / QT / steady state) as the second movement; the BoC operates two tools and an overview that omits the second is incomplete. Note when the two tools send aligned signals ("BoC is restrictive on rate AND running QT") or different signals ("BoC is cutting rate but still running QT" — the BoC has explicitly said the rate and the balance sheet are independent levers, but the contrast is worth flagging). Note the BoC−Fed gap and whether it is at an extreme or changing direction, since this has direct implications for CAD. Characterize market expectations using `can2y_overnight_spread` directionally — "market is broadly pricing further reductions," "expects rates to hold," "moving toward a hawkish repricing." Do not state precise basis-point counts ("X bps priced by date Y"). The directional read is robust in normal regimes; in QE/QT transitions or stress windows, lean harder on qualitative direction and explicitly flag that the spread carries premium noise. Bring in `can_us_2y_spread` when it is diverging meaningfully from `bocfed_spread`, but allow that the divergence may reflect either expected-policy-stance changes or relative term-premium movements — name the ambiguity rather than asserting one interpretation.

---

## Labour Market

**Question:** How tight is the labour market, and what does wage growth imply for the inflation outlook?

**Data:** unemployment_rate, lfs_wages_all (Y/Y), lfs_wages_permanent (Y/Y), seph_earnings (Y/Y), lfs_micro (Y/Y, BoC composition-adjusted), cpi_services (Y/Y)

**Signals to evaluate:**

- Where is the unemployment rate relative to ~5–5.5%? This is the commonly cited NAIRU range for Canada — the level consistent with stable inflation. Below it suggests a tight labour market with upward wage pressure. Above it suggests slack with downward wage pressure.
- Is unemployment rising or falling, and at what pace? A rapidly rising unemployment rate signals slack opening quickly. A gradually falling rate signals tightening. The direction and pace matter as much as the level.
- Across the wage measures, which are highest and which are lowest? Is the dispersion between them wide or narrow? Wide dispersion means the choice of measure matters and the signal is ambiguous.
- Is LFS-Micro (BoC's composition-adjusted measure) running above or below raw LFS? If LFS-Micro < raw LFS, composition effects are flattering the headline wage number — higher-paid workers are a larger share of employment than usual, pushing up the average without reflecting genuine wage pressure. If LFS-Micro > raw LFS, the underlying wage dynamic is stronger than the headline implies.
- Are wage measures above or below ~3%? This is the threshold roughly consistent with 2% inflation (approximated as ~1% trend productivity growth + 2% target). Above 3% means wage growth is adding to inflation pressure on its own terms. Below 3% means wage growth is consistent with or below target-consistent inflation.
- Is wage growth above or below services CPI? If wages > services CPI, firms are currently absorbing the gap — pricing pressure from labour costs is not yet fully passing through. If wages ≈ services CPI and both are elevated, the pass-through is active. If wages < services CPI, labour costs are not the primary driver of services inflation.
- Are real wages positive or negative? Latest wage growth minus latest headline CPI Y/Y. Positive means workers are gaining purchasing power. Negative means they are falling behind inflation.

**Thresholds:**
- ~5–5.5% = NAIRU for Canada
- ~3% = wage growth consistent with 2% inflation
- Wages > services CPI = margin absorption (pass-through not complete)
- Wages ≈ services CPI and both elevated = active pass-through

**What to surface:** Lead with the unemployment level relative to NAIRU and whether it is rising or falling. Then characterize wage growth — above or below the 3% threshold, and whether the measures are telling a consistent story. Surface the wage-vs-services-CPI relationship if it is informative (either confirming or contradicting the wage picture). Note LFS-Micro vs. raw LFS only if there is a meaningful gap, as it affects how to read the headline wage number. Real wages are worth mentioning if the gap is large in either direction.

---

## Financial Conditions

**Question:** How are commodity prices, the exchange rate, and (in the future) other market signals affecting the Canadian economic picture?

**Data:** wti (daily), brent (daily), wcs (monthly), usdcad (daily, CAD per USD — higher = weaker CAD)

**Signals to evaluate:**

- Is WTI year-over-year positive or negative? Rising oil adds to headline CPI directly (gasoline, transport costs, energy inputs). Falling oil subtracts. The sign is the primary read.
- Is WCS trading at a normal or unusual discount to WTI? A wider-than-normal WCS discount reflects pipeline constraints and Alberta-specific supply conditions — relevant for Canadian fiscal revenues and energy-sector investment.
- Is CAD appreciating or depreciating against the USD? Higher USD/CAD = weaker CAD. The direction over the past 3–6 months is the primary read.
- How large is the cumulative CAD move? A sustained 10% depreciation adds approximately 1–2% to goods CPI over 12–18 months through import price pass-through. A sustained 10% appreciation subtracts a similar amount.
- Is CAD moving in the same direction as oil? This is the normal petrocurrency relationship for Canada. When CAD and oil diverge — oil rising while CAD weakens, or oil falling while CAD strengthens — a non-commodity driver (rate differentials, risk sentiment, trade policy uncertainty) is dominating. Name it if visible.
- Is the CAD move consistent with the BoC–Fed rate differential? A widening spread where the BoC is below the Fed puts natural downward pressure on CAD through interest rate parity. If CAD is weakening beyond what the rate differential would imply, other factors are at work.
- How does the current CAD level compare to recent historical extremes? The 2015–2016 oil crash lows (~1.45–1.46) are a useful reference for extreme weakness.

**Thresholds:**
- WTI Y/Y < 0 = disinflationary impulse on headline CPI
- ~10% sustained CAD move ≈ ~1–2% goods CPI pass-through over 12–18 months
- ~1.45–1.46 = 2015–2016 CAD lows (historical reference)

**What to surface:** Lead with whether oil is adding to or subtracting from inflation pressure, and state the direction clearly. Then characterize the CAD — direction, magnitude, and whether it is amplifying or cushioning the oil move. If oil and CAD are moving in opposite directions (one inflationary, one disinflationary), name that tension explicitly — these two forces are partially offsetting and the net effect is ambiguous. Note the petrocurrency relationship only when it has broken down, since normal co-movement is not itself informative.

---

## Output instructions

- 2–4 sentences per section. Prioritize insight over completeness.
- Do not open with "As of [month], [indicator] was [X%]." Lead with the analytical point; embed the number in it.
- Use plain language. Avoid jargon that would not appear in a quality financial newspaper.
- When two indicators are in tension, name the tension explicitly rather than resolving it artificially.
- Do not editorialize about BoC decisions ("the BoC should cut"). Describe what the data implies; let the reader draw the policy conclusion.
- Reference specific numbers where they anchor the analysis. Vague directional language without a number is less useful than a number in context.
- Do not assume a direction is good or bad. Tight labour markets are not inherently good; falling inflation is not inherently good. Describe conditions; do not evaluate them.
- The four blurbs appear together on the same page. Do not repeat the same observation across sections unless the cross-section connection is the specific point being made.
