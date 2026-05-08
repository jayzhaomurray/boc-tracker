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

Write as an analyst would speak to an informed reader. The reader knows the terms (bps, y/y, neutral rate, core CPI, restrictive, accommodative) but shouldn't have to decode the data's shape — signed spreads, percentile rankings, tier labels, and jargon nouns belong in the formatter's output, not in the prose. Translate.

State positions, don't describe journeys. Embed numbers in sentences, don't list them. Use plain words when plain words fit. If a sentence sounds like a Bloomberg terminal output, rewrite it.

**Worked example — same observation, two forms:**

Bad: *"The BoC−Fed spread is −138bps, in the top 10% of observations historically. Canada 2Y−overnight spread is +66bps with hawkish 12-week drift."*

Good: *"The BoC's policy rate sits 138 bps below the Fed's, an unusually wide gap. Canadian 2-year yields have risen over the past quarter and now trade 66 bps above the policy rate."*

The "good" version still uses bps and still references specific numbers. What it drops: the signed-spread shape, the percentile rank, and the jargon noun "hawkish drift." Same information, plainer sentences. Apply the same transformation everywhere: "lower edge" → "bottom"; "settlement balances" → "cash banks keep at the BoC overnight"; "floor-system maintenance" → "running the balance sheet at its target steady-state size."

**When translating technical → plain, check what the technical term encoded.** Technical terms compress structural information that the plain version has to preserve explicitly:
- "Hawkish drift" carried *direction* (yields up). "Gap widening" loses it — the gap could widen because either side moves. Plain translation must state the direction: *"yields have risen."*
- "Settlement balances" carried *which side of the balance sheet* (liability — banks own these deposits, the BoC owes them). "$71B" alone doesn't. Plain translation must make the ownership clear: *"banks keep $71B at the BoC overnight."*
- Signed spreads carry *sign convention* (which leg is which). "+0.66pp" alone doesn't tell you which is above. Plain translation states it: *"X is N bps above Y."*

If a translated sentence becomes more ambiguous than the technical original, the translation lost something. Re-translate to preserve the dropped information explicitly.

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

**Data:** overnight_rate (BoC, monthly aggregate; used by chart), overnight_rate_daily (BoC, daily since 2009-04-21; used by analyze.py), fed_funds (Fed), yield_2yr (Canada), us_2yr (US), bocfed_spread (overnight − fed_funds), can2y_overnight_spread (Canada 2Y − overnight), can_us_2y_spread (Canada 2Y − US 2Y), boc_total_assets, boc_goc_bonds, boc_settlement_balances (all in C$ billions), fad_history (static historical FAD calendar) + fad_calendar (dynamic from BoC iCal feed). Derived from daily rate + FAD calendar: action_state (hold / cutting / hiking), meetings_unchanged, consecutive_same_direction_moves, days_since_last_change, last_change_* (date / direction / magnitude), prior_cycle_* (direction / total bps / start rate / start date / first move date / active duration).

**Rate signals — action and stance (the verb leads):**

The headline read is what the BoC is *doing*, for how long, and following what. Position relative to the neutral band is supporting evidence, not the takeaway. Markets anchor on the Bank's stance; the same market signal means different things depending on whether the Bank is hiking, holding, or cutting.

- **Action state** (`action_state`): is the BoC actively *cutting*, actively *hiking*, or *on hold*? Three states only — determined by the most recent FAD's outcome:
  - Last FAD = no rate change → **on hold**
  - Last FAD = cut → **cutting**
  - Last FAD = hike → **hiking**

  No "transitioning" or other catchall states. Continuity nuance ("just resumed cuts after a 4-meeting hold," "third hike in a row") is carried by the meeting count fields below, not by adding state names. The classification is derived at meeting resolution from the daily overnight rate (V39079, since 2009) cross-referenced with the FAD calendar.
- **Duration of current state.** When `action_state` is "on hold," `meetings_unchanged` counts consecutive no-change FADs back to the last change. When "cutting" or "hiking," `consecutive_same_direction_moves` counts consecutive same-direction FADs. `days_since_last_change` always available, useful as a wall-clock anchor. "On hold for 4 meetings" is a stronger statement than "on hold for 1 meeting"; "third consecutive cut" reads differently from "first cut after a hold" — these distinctions matter for blurb framing.
- **Most recent change** (`last_change_date_str`, `last_change_direction`, `last_change_bps`): a Nbp cut/hike on a specific FAD date. Anchors when the current state began.
- **Prior cycle** (`prior_cycle_*`): what came before this state? E.g., "on hold *after a 275bp cutting cycle from a 5.00% peak (cycle started June 2024) to 2.25% on October 29, 2025*." Computed from the daily rate series so it reaches back further than the FAD calendar (which is shorter).
- **Position vs neutral band** (supporting, not headline). The BoC's official neutral-rate range is **2.25–3.25%**, unchanged since the April 2024 r* update ([Staff Analytical Note 2025-16](https://www.bankofcanada.ca/2025/06/staff-analytical-note-2025-16/); MPR April 2026 Appendix). BoC frames this as a range, not a midpoint — the full 100bp span is the published uncertainty zone. Above 3.25% = restrictive (actively slowing the economy); below 2.25% = accommodative (actively stimulating); inside the band = roughly neutral. "Restrictive" is BoC's own term; "accommodative" appears less often, and at near-neutral levels BoC tends to use positional language ("at the lower end of the neutral range") rather than binary stance labels.
- **BoC vs Fed cycle comparison.** How does the BoC's recent trajectory compare to the Fed's? Did the BoC peak first / cut first / cut more? Divergent paths show up in the BoC−Fed spread.

**Rate signals — comparison and market expectations:**

- BoC−Fed spread (`bocfed_spread`): level and direction. Negative spread (BoC below Fed) is broadly CAD-negative; positive supports CAD. Empirical distribution since 1996 (median |spread| 38bp): **±50bp = notable** (top half); **±100bp = unusual** (top 10%, flag prominently); **±150bp = rare** (top 5%, reserved for cycle-defining episodes — 1995–98, late-2024-onward).
- Canada 2Y − Overnight spread (`can2y_overnight_spread`): a *directional* signal of the market-implied policy path, not a precise basis-point forecast. The 2Y embeds a term premium — BoC ACM-model estimates suggest roughly 0–40 bp in normal regimes (2003–2019) and 20–60 bp in the elevated post-2023 regime (see BoC's [Financial Stability Indicators](https://www.bankofcanada.ca/rates/indicators/financial-stability-indicators/) for the published decomposition). The spread is materially distorted during QE/QT episodes (the 2020–2022 GBPP suppressed 2Y GoC ~20 bp below OIS-equivalent through scarcity), flight-to-quality stress, fiscal-supply shocks, and stretches of elevated inflation uncertainty — in those windows the level moves as much from premium repricing as from expectations. Empirical distribution since 2001 (median |spread| 30bp): **within ±25bp = near-zero** (44%, market broadly aligned with current stance, no clear directional story); **±50bp = notable** (top third); **±100bp = unusual** (top 10%).
- **Direction of `can2y_overnight_spread` drift — interpretation depends on the BoC's `action_state`.** Track both a 4-week window (tactical repricing around meetings) and a 12-week window (trend confirmation); the signal is strongest when both agree. The same drift means very different things based on what the BoC has been doing:

  | BoC `action_state` | Hawkish drift (spread rising) means | Dovish drift (spread falling) means |
  |---|---|---|
  | Active *cutting* cycle | Market doubting more cuts will happen | Market expects deeper cuts than already priced |
  | *On hold* | Market starting to price *hike* risk | Market starting to price resumption of cuts |
  | Active *hiking* cycle | Market expects more hikes | Market doubting more hikes will happen |

  **Always frame the read as "market vs. Bank's current stance,"** never as if the cycle is always cutting. A naive read ("hawkish drift = market sees fewer cuts coming") silently assumes the Bank is in a cutting cycle and breaks the moment that's not true.

- **Defensible reads** of `can2y_overnight_spread`: direction of shift; large inversions (more negative than -0.75pp) clearly signaling cut expectations regardless of premium uncertainty; broad qualitative bands ("modest cuts priced," "meaningful cuts priced"). **Not defensible:** specific basis-point counts ("X bps of cuts by year-end"); reading the level as pure expectations during distorted regimes; mechanically dividing the spread by 25 bp to count meeting moves.
- Canada 2Y − US 2Y spread (`can_us_2y_spread`): a cross-country yield differential. Both legs carry their own term premiums and convenience-yield effects. Negative = Canadian rates expected lower than US (broadly CAD-negative; often reflects weaker Canadian growth/inflation outlook relative to the US). Positive = Canada expected tighter — historically rare. Empirically correlated with `bocfed_spread` at **0.88 since 2001**, so the two should usually move together. When they diverge meaningfully, the market is pricing either a future change in stance *or* relative-premium movements (fiscal supply, convenience-yield shifts, asymmetric balance-sheet operations). Flag both interpretations rather than asserting one.

**Balance sheet signals:**

- Direction of `boc_total_assets` and `boc_goc_bonds` over the last 6–12 months: rising = QE; falling = QT (passive runoff via maturities); flat = steady state. The slope tells you the pace.
- BoC balance sheet operational timeline (per BoC press releases):
  - **April 1, 2020 – October 27, 2021:** Government of Canada Bond Purchase Program (GBPP), QE phase.
  - **October 27, 2021 – April 25, 2022:** reinvestment phase (maturing bonds replaced; balance sheet roughly flat).
  - **April 25, 2022 – January 29, 2025:** passive QT (no active selling; bonds rolled off as they matured).
  - **[January 29, 2025](https://www.bankofcanada.ca/2025/01/fad-press-release-2025-01-29/):** BoC announces end of QT and plan to restore normal-course asset purchases.
  - **March 5, 2025 onwards:** term repos restarted (bi-weekly, $2–5B per operation) as routine balance-sheet management; T-bill purchases resume Q4 2025; secondary-market GoC bond purchases earliest end-2026.
- Distance from anchors: pre-COVID baseline of total assets was **~$120B** (early 2020; max $121.5B in early Feb 2020, verified from data); peak QE was **~$575B in March 2021** ($575.4B on 2021-03-10, verified from data — note this is March 2021, not April 2022 as sometimes loosely characterized; April 2022 is when QT *started*). Where is the balance sheet now relative to these reference points?
- Alignment between `boc_total_assets` and `boc_goc_bonds`: routine divergence is normal — pre-COVID, ~$37B of total assets was non-GoC (T-bills, bi-weekly term repos, etc.). **Stress signals are *rapid* divergence driven by emergency facilities:** Contingent Term Repo Facility (CTRF) surges, Fed swap-line drawings (US dollar liquidity needs), Emergency Lending Assistance / advances (overnight or longer to specific institutions), or outright purchases of non-GoC securities (provincial bonds, corporate bonds, CMBs). Canonical benchmark: March–June 2020, total assets jumped from ~$120B to ~$385B in 6–7 weeks via CTRF-style term repos (~$140B), the Fed USD swap line, and various market-functioning programs. Modest divergence from T-bill fluctuations or routine bi-weekly term repos is operationally normal and not a signal.
- `boc_settlement_balances` level: the operating regime indicator. The BoC adopted the floor system as its **permanent operating regime in [April 2022](https://www.bankofcanada.ca/2022/04/bank-of-canada-provides-operational-details-for-quantitative-tightening-and-announces-that-it-will-continue-to-implement-monetary-policy-using-a-floor-system/)** ("the floor system will remain in place even after QT has run its course"). The post-QT steady-state target range is **$20–60B** (Deputy Governor Gravelle, [March 2024 speech](https://www.bankofcanada.ca/2024/03/going-back-normal-bank-canadas-balance-sheet/)). Pre-COVID corridor system held balances near zero. Current level relative to the $20–60B target is the relevant read; significant deviation signals transition (e.g. ~$130B in early 2025 was the QT-runoff transitional level).

**Thresholds (verified May 2026):**
- **2.25–3.25%** = BoC's official neutral-rate range (Staff Note 2025-16; MPR April 2026; unchanged since April 2024)
- **`bocfed_spread`:** ±50bp notable; ±100bp unusual (top 10% of observations since 1996); ±150bp rare (top 5%)
- **`can2y_overnight_spread`:** within ±25bp = near-zero (44%); ±50bp notable (top third); ±100bp unusual (top 10%)
- **Canada 2Y term premium** ≈ 0–40 bp in normal regimes (2003–2019), 20–60 bp post-2023; materially distorted during QE/QT and stress
- **~$120B** = pre-COVID balance sheet baseline (early 2020, verified from data)
- **~$575B** = peak QE balance sheet (**March 2021**, verified from data)
- **$20–60B** = post-QT steady-state target for settlement balances (Gravelle, March 2024)
- **Floor system permanent since April 2022; QT ran April 25, 2022 – January 29, 2025**

**What to surface:** Lead with the verb — what is the BoC *doing*. "On hold for N meetings," "in the N-th consecutive cut," "actively hiking." Ground that with the duration of the current state and the cycle it followed: "on hold for 4 meetings after a 275bp cutting cycle from May 2024." The position vs. the neutral band is supporting evidence for the verb, not the takeaway. Bring in the balance sheet trajectory (QE / QT / steady state / floor-system maintenance) as the second tool; the BoC operates two levers and an overview that omits the second is incomplete. Note when the two tools send aligned signals ("BoC on hold AND balance sheet at floor steady state") or different signals ("BoC cutting but still running QT" — the BoC has explicitly said the rate and the balance sheet are independent levers, but the contrast is worth flagging). Note the BoC−Fed gap relative to its tier (notable / unusual / rare) and whether it is changing direction, since this has direct implications for CAD. **Interpret market expectations relative to the Bank's stance, not in absolute terms.** A hawkish drift in the 2Y−overnight spread means "market doubting more cuts" if the BoC is cutting, but "market starting to price hike risk" if the BoC is on hold — use the conditional table above. Do not state precise basis-point counts ("X bps priced by date Y"); use directional language ("market broadly aligned with the Bank's stance," "betting against the Bank's signal," "starting to reprice toward hikes"). The directional read is robust in normal regimes; in QE/QT transitions or stress windows, lean on qualitative direction and explicitly flag that the spread carries premium noise. Bring in `can_us_2y_spread` when it is diverging meaningfully from `bocfed_spread`, allowing that the divergence may reflect either expected-policy-stance changes or relative term-premium movements — name the ambiguity rather than asserting one interpretation.

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
