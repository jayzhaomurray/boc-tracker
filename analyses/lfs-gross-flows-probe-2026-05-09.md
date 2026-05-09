# StatsCan LFS Gross Flows Probe — 2026-05-09

## Query Result

Attempted to locate StatsCan Table 14-10-0124 "Labour force status flows, monthly."

## Findings

**Table 14-10-0124 exists**, but metadata reveals:
- **Title:** "Activity prior to unemployment, annual" (NOT monthly)
- **Frequency:** Annual (frequencyCode 12, data points 138,600)
- **Range:** 1976–2025
- **Geography:** Canada + provinces/territories
- **Disaggregation:** By gender (Total / Men+ / Women+), age group (15+, 15–24, 25+, etc.)
- **Series count:** 2,772 vectors in the cube
- **ISSUE:** This table classifies unemployed by prior activity (worked / laid off / never worked / in school). It does NOT contain the 3x3 transition matrix (E→U, U→E, NLF→E, etc.) needed for flow decomposition.

**Monthly flows table not located.** Candidates searched:
- 14-10-0125, 14-10-0126, 14-10-0127, 14-10-0128, 14-10-0122, 14-10-0123 — all exist but cover different labour concepts (reason for leaving job, reason for not job-seeking), none provide gross flows by state transition.

## BoC Methodology

Bank of Canada October 2024 MPR Chart 23 (unemployment decomposition) methodology:
- **Data source:** Not explicitly cited in MPR or in-focus article.
- **Candidate SANs:** SAN 2024-8 ("Benchmarks for assessing labour market health") mentions job finding rates and job separation rates as key labour flow indicators, but does not detail the calculation method.
- **Likely source:** Statistics Canada Labour Force Survey microdata (referenced in SAN 2024-23), not a pre-built table.

## Verdict

**LOW feasibility.** The monthly gross flows 3x3 matrix does not appear to exist as a published StatsCan table. The BoC likely computes flows via LFS microdata analysis (custom cross-tabulation of prior/current state). Would need:
1. Direct access to LFS microdata, OR
2. Contact StatsCan labour team for custom cross-tab, OR
3. Reverse-engineer BoC's methodology from their working papers (none located in casual search).

**Recommendation:** Verify the table reference with BoC directly or check their working paper archive for the flows methodology before committing development time.
