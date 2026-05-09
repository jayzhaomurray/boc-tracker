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

---

## Second-pass probe (2026-05-09)

### 1. SAN 2024-8 methodology

SAN 2024-8 ("Benchmarks for assessing labour market health: 2024 update") does not contain the flows decomposition methodology. It cites "Statistics Canada and Bank of Canada calculations" with no table numbers and no formula for converting flows to pp contributions. Its reference chain leads to SDP 2021-15 as the root document.

### 2. MPR October 2024 In Focus footnotes

Extracted directly from the MPR PDF. Chart 23 source line: "Statistics Canada and Bank of Canada calculations." The two In Focus endnotes cover only labour hoarding (fn 1) and the newcomers definition (fn 2). No data attribution or methodology footnote exists for the flow decomposition. The chart legend names four series: job-finding rate (green), entry from outside the labour force into unemployment (red), layoff rate (yellow), Other.

### 3. Root methodology: SDP 2021-15

Staff Discussion Paper 2021-15 (Ens, Savoie-Chabot, See, Wee, 2021) is the origin document. Appendix B defines:

- **Job-finding rate:** share of unemployed workers in period t-1 who found employment in period t (U→E)
- **Separation rate:** share of employed workers in period t-1 who entered unemployment in period t (E→U)
- **Job-changing rate:** workers who remain employed month-to-month but change jobs — confirming individual-level LFS rotation-panel linking is in use

Data source cited: "Statistics Canada and Bank of Canada calculations" — no StatsCan table number, no PUMF reference, no Shimer (2012) decomposition cited. The paper includes a simpler ER/LFPR decomposition in Box B-1 but not a full flow-to-Deltaur accounting identity.

The NLF inflow bar in Chart 23 (red) is not in SDP 2021-15's two-rate framework; BoC extended it to a 4-component decomposition (job-finding, layoff, NLF entry, Other) for the MPR — methodology undocumented in any public paper found.

### 4. Additional StatsCan tables tested

Scanned 14100001–14100619 via WDS getCubeMetadata API (>600 table IDs checked). No table with "flow," "transition," "gross worker," or equivalent in the title was found. Closest proxies:
- **14100123** "Activity prior to unemployment, monthly, unadjusted" — captures inflow composition (temporary layoff / job leavers / from NLF) but is a stock classification of current unemployed by prior activity, not a transition rate matrix
- **14100452** "Interprovincial labour mobility" — geographic mobility, not E/U/NLF flows

Confirmed absence: no published StatsCan table contains the 3x3 E/U/NLF gross flows matrix.

### 5. LFS PUMF status

The LFS uses a 6-month rotating panel (~100,000 individuals; 1/6 of dwellings replaced each month), meaning ~5/6 of respondents overlap between consecutive months. StatsCan survey documentation confirms the rotating design. The BoC's job-changing rate definition ("workers who remain employed from one month to the next but change jobs") directly confirms they link LFS records across months.

PUMF availability: Statistics Canada offers microdata through Research Data Centres (RDC) under a subscription/application model. The PUMF (public version) does not include a respondent ID that persists across monthly files — Statistics Canada strips linking keys from the public release to protect respondent confidentiality. Month-to-month transition reconstruction requires either (a) RDC access to the confidential LFS microdata files, which include dwelling/household identifiers, or (b) a custom tabulation request from StatsCan.

### 6. Verdict

**HIGH confidence on source; LOW feasibility for replication without RDC access.**

The flow decomposition behind Chart 23 is computed from confidential LFS microdata (not a published table) by linking consecutive monthly files via dwelling/household identifiers available only through Statistics Canada's RDC network or custom tabulation service. The BoC cites "Statistics Canada and Bank of Canada calculations" throughout and has never published the linking code or a technical note describing the 4-component pp-contribution accounting identity used in Chart 23.

**Viable paths ranked:**
1. **StatsCan custom tabulation (most direct):** Request a 3x3 monthly flow matrix (E/U/NLF x E/U/NLF, Canada total, SA) — StatsCan has produced these before for researchers. Cost and turnaround variable.
2. **RDC application:** Academic/government researchers can apply. Multi-month lag; not suitable for a live dashboard.
3. **Approximate replication via published proxies:** Table 14100123 supplies the NLF→U inflow decomposition (distinguishing new entrants by prior activity). The U→E flow can be approximated as U_t-1 * (1 - long-term-unemployed-share) using duration tables (14100056). E→U is not directly in any public table but can be constructed residually from changes in U and inflow data. This is the most tractable route for the dashboard without institutional access.

**Concrete next step if pursuing option 3:** Draft the residual accounting identity using published LFS stocks and the "activity prior to unemployment" monthly series (14100123), verify it tracks the BoC's layoff-rate chart visually, and document deviation from the BoC series as a known limitation.
