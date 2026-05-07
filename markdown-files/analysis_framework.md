# Analysis Framework

Internal analytical brief for generating dashboard blurbs. Each section defines the question being answered, the signals to evaluate, the thresholds that matter, and what to surface in the output.

Blurbs should read as a thoughtful analyst writing for an informed reader — not a data reporter listing numbers. Embed numbers in analytical sentences. Prioritize the most important signal or tension in the data, not a comprehensive tour of every indicator. When two indicators are telling different stories, say so. 2–4 sentences per section. Write in present tense based on the latest available data.

The framework must work in any part of the cycle — high inflation or low, hiking or cutting, tight labour market or slack. Do not assume a direction is desirable or expected. Describe what the data shows and what it implies; let the reader draw conclusions.

---

## Inflation

**Question:** How does inflation compare to the BoC's 2% target, and what is the underlying trend?

**Data:** cpi_all_items (M/M, 3M AR, Y/Y), cpi_trim, cpi_median, cpi_common, cpix, cpixfet, cpi_breadth (share above 3%, share below 1%)

**Signals to evaluate:**

- Where are core measures relative to 2%? How far above or below, and are they moving toward or away from target?
- Is the band of core measures tight or wide? A tight band means the measures are telling a consistent story. A wide band means the choice of measure matters — note which are highest and lowest and what that implies.
- Is headline CPI above or below core? If headline > core, energy or food is adding to the headline number. If headline < core, energy or food is masking underlying pressure. Note which reading is more representative.
- CPI breadth: is the share of basket components above 3% elevated or depressed relative to the 1996–2019 historical average? Is the share below 1% elevated or depressed? Elevated breadth above 3% means price pressure is broad. Elevated breadth below 1% means disinflation is broad.
- Is M/M momentum consistent with 2% annualized? ~0.17%/month is the neutral threshold. Sustained prints above 0.3% signal acceleration; sustained prints below 0.1% signal deceleration.
- Is the 3-month annualized rate above or below 2%? This is the cleanest read on current momentum independent of base effects.

**Thresholds:**
- 2% = BoC target
- 1–3% = BoC control range
- ~0.17%/month ≈ 2% annualized
- Tight band = all core measures within ~0.5pp of each other

**What to surface:** Lead with where core measures sit relative to 2% and whether they are moving toward or away from target. Note whether the convergence or divergence is genuine (tight band) or an artefact of averaging wide dispersion. Mention breadth if it adds something the core level does not (confirming or contradicting the direction). Use M/M or 3M AR if they diverge materially from the Y/Y read.

---

## Policy Rates

**Question:** Where does the BoC stand in the rate cycle, and what is the market pricing relative to the current rate?

**Data:** overnight_rate (BoC), fed_funds (Fed), yield_2yr (Canada), us_2yr (US)

**Signals to evaluate:**

- Where is the BoC overnight rate relative to the neutral rate? ~2.5–3% is the commonly cited neutral range for Canada. Above neutral means policy is restrictive — it is actively slowing the economy. Below neutral means policy is accommodative — it is actively stimulating. At neutral means policy is neither adding to nor subtracting from economic momentum.
- How far has the BoC moved from its most recent peak or trough, and in which direction? How does the magnitude compare to the Fed's move over the same period?
- Which central bank has moved more in the current direction, and which moved first?
- What is the current BoC–Fed rate spread? Is it widening or narrowing? A wider spread where the BoC is below the Fed puts downward pressure on CAD; a spread where the BoC is above the Fed supports CAD.
- Is the Canada 2Y yield above or below the BoC overnight rate? If the 2Y is below the overnight rate, the market broadly expects net rate reductions over the next two years. If the 2Y is above the overnight rate, the market broadly expects rates to hold or rise. The size of this gap indicates the degree of conviction.
- Has the Canada 2Y been rising or falling over the last 1–3 months? A falling 2Y means market expectations are shifting toward lower rates, even if the BoC has not moved. A rising 2Y means expectations are shifting toward higher rates or a longer hold.
- Is the Canada–US 2Y spread widening or narrowing, and in which direction? Canada 2Y falling relative to US 2Y implies markets expect Canada's rate path to be lower than the US path — typically reflecting a weaker Canadian growth or inflation outlook relative to the US.

**Thresholds:**
- ~2.5–3% = neutral rate for Canada (BoC's r* estimate)
- 2Y below overnight = market pricing net reductions
- 2Y above overnight = market pricing hold or increases
- BoC–Fed spread outside ±100bp = historically unusual

**What to surface:** Lead with where the BoC rate sits relative to neutral — this is the foundational policy positioning read. Note the BoC–Fed gap and whether it is at an extreme or changing direction, since this has direct implications for the exchange rate. Characterize market expectations using the 2Y–overnight spread directionally ("the market is broadly pricing further reductions" or "the market expects rates to hold") rather than as a precise basis-point figure. Note the Canada–US 2Y spread only if it is moving materially and implies a diverging outlook.

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

## External Conditions

**Question:** How are commodity prices and the exchange rate affecting the Canadian price picture?

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
