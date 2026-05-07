# Dashboard Reading Guide

How to read each chart to answer the underlying policy question. Written for use as analysis scaffolding.

---

## Currently answerable

### Is inflation coming down, and how broad is the retreat?

Look at the core inflation panel and the breadth chart together. The core panel tells you the *level* — are trim, median, and common all below 3%? Are they converging toward each other (healthy disinflation) or diverging (one measure is being distorted)? The breadth chart tells you *texture* — a falling headline with breadth still elevated means a few categories are cooling but most of the basket is still running hot, which is a false signal. You want to see both the level falling *and* the deviation from historical average narrowing from the top. The 2022–2023 period is the reference: breadth peaked at +46pp, inflation was broad and self-reinforcing. Coming back toward zero on both measures simultaneously is the "all clear."

### Which core measures are converging back to 2%?

Toggle on trim and median individually and compare to the range band. If trim is at 2.8% but median is at 2.2%, the distribution of price changes is still skewed upward — there are outliers pulling trim up. If both are near 2% and the band is tight, that's genuine convergence. Divergence between measures is itself informative: CPIXFET (ex food and energy) running above trim suggests services inflation is the remaining problem. That's the reading that tells you whether the last mile will be easy or hard.

### Are markets pricing in rate cuts, and how fast?

The 2Y yield is the key. It's roughly the market's expectation of where the overnight rate will average over the next two years. If the BoC overnight is at 2.75% and the Canada 2Y is at 2.3%, markets are pricing in roughly 45bp of cuts over two years. The slope matters too — if the 2Y has been falling for three months, market expectations are shifting dovishly even if the BoC hasn't moved. The Level/20d Avg toggle is useful here: the raw daily series is noisy; the smoothed line shows the trend in expectations. The Canada–US spread is the second read — if Canada 2Y is falling relative to US 2Y, markets think the BoC will ease more aggressively than the Fed, which usually reflects a weaker growth or inflation outlook for Canada.

### How out of sync are BoC and Fed policy, and has that gap changed?

The policy rates chart shows the actual gap directly. Read the spread between the two lines. The step-function rendering makes the gap easy to see visually. A widening gap matters because it puts downward pressure on CAD (inflationary for Canada via import prices) and reflects fundamentally different economic conditions. The historical 10Y view shows how unusual the current gap is relative to the pre-pandemic norm, when the two rates tracked each other closely.

### How tight is the labour market?

The current unemployment chart barely answers this — a single line tells you the level but little about momentum. Read the level (is it above or below NAIRU, roughly 5–5.5% for Canada?) and the direction over the last 6–12 months. Without wage growth alongside it, you cannot distinguish "unemployment rising because workers are re-entering" from "unemployment rising because layoffs are happening." This chart is a placeholder until wage growth is added.

### Is month-to-month CPI accelerating or decelerating right now?

The M/M view with a 2Y window is designed for this. Watch for: is M/M running consistently above or below 0.2% (roughly the pace consistent with 2% annualized)? A few months at 0.5%+ M/M is a re-acceleration signal. A string of 0.1% or negative prints is disinflation gaining traction. The 3M AR transform smooths out one-month noise while staying current — it's the number the BoC's Governing Council actually watches most closely in the monthly release.

---

## Not yet answerable — data gaps

### Is growth slowing enough to bring inflation down sustainably?

*Needs: quarterly real GDP*

Is growth running below potential (roughly 1.5–2% annualized for Canada)? Below-potential growth closes the output gap, which reduces pricing power economy-wide. Look at the level and trend over 4–6 quarters — a single bad quarter doesn't answer the question. Without this, you cannot assess whether inflation is falling because the economy has genuinely cooled or just because of base effects and energy prices.

### Are wages driving services inflation?

*Needs: wage growth (LFS or SEPH average hourly earnings, Y/Y)*

If wages are running at 4–5% and services CPI is at 3.5–4%, that's a cost-push story — firms are passing labour costs through to prices. If wages are cooling toward 3% and services CPI is following with a 3–6 month lag, that's the lag structure the BoC expects to see on the way down. Without the wage line, you can see services inflation but not diagnose its cause.

### Is the exchange rate amplifying or absorbing the tariff shock?

*Needs: CAD/USD exchange rate*

CAD depreciation makes imports more expensive in Canadian dollar terms, which is directly inflationary for goods. If CAD fell 8% because of tariff uncertainty and goods CPI is rising 4%, part of that goods inflation is currency pass-through — not a sign of domestic demand strength. Without the exchange rate, you cannot decompose goods inflation into tariff, currency, and demand components. This is probably the most important missing piece for the 2025–2026 tariff context specifically.

### What are businesses actually expecting to do with prices?

*Needs: BoC Business Outlook Survey (BOS) price expectations net balance*

The BOS asks firms directly whether they expect to raise prices. It's a leading indicator — it moves before CPI because it's measuring intent. Read the net balance (% expecting higher prices minus % expecting lower). A high positive net balance not yet in CPI tells you inflation is coming. A net balance that has been falling for 3 quarters tells you pass-through pressure is easing. This is quarterly, published by the BoC as a free CSV.

### Is the tariff impact hitting goods prices yet?

*Needs: goods CPI component breakdown or import price index*

Watch goods CPI components (durable goods, clothing, household items) for acceleration after tariff announcements. The timing signal matters: tariffs announced in February, goods CPI starts rising in April — that's a 2-month pass-through lag. The breadth chart gives a partial read: if breadth lifts because goods components go above 3% while services components stay anchored, that's a tariff signature.

### Where is oil, and how is that feeding through?

*Needs: Brent or WTI price (EIA API)*

Oil affects CPI directly (gasoline) and indirectly (transport costs throughout the supply chain). Read Brent or WTI level and trend, then cross-reference with energy CPI. If oil is falling but energy CPI is still high, there's either a lag or a currency effect. If oil is stable but CPI ex-energy is rising, the oil story is not the driver. Without an oil chart, you are blind to one of the most reliable leading indicators of headline CPI.

---

## Meta-conclusion

The dashboard right now can tell you *where inflation is* but not *why it's there or where it's going*. Adding wages, GDP, the exchange rate, and BOS expectations would let you build a full causal chain — the difference between a data display and something you can write an informed view from.

**The central question every chart should trace back to:** Should the BoC cut at the next decision, and by how much? Every indicator is relevant only insofar as it shifts the probability on that question.
