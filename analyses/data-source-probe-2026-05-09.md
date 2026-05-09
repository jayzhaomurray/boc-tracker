# Data Source Probe — Deep-Dive Design Questions
**Date:** 2026-05-09  
**Purpose:** Verify five open data-source questions for deep-dive page architecture.

---

## 1. Output Gap / Potential Output Series

**Question:** Does BoC Valet expose the output gap range published in each MPR Appendix?

**Finding:** YES — Series `INDINF_OUTGAPMPR_Q` exists.

| Key | Label | Source | Frequency | Confidence |
|-----|-------|--------|-----------|------------|
| `INDINF_OUTGAPMPR_Q` | Current MPR output gap (%) | BoC Valet | Quarterly | HIGH |

**Alternative candidates:** `INDINF_OUTGAPM_Q` (output gap midpoint), `INDINF_OUTGAPI_Q` (other inflation indicator variant).

**Recommendation:** Use `INDINF_OUTGAPMPR_Q` directly from Valet — it is the MPR's own published estimate and updates on MPR release cadence. No fallback needed.

---

## 2. CPI Excluding Indirect Taxes

**Question:** Does StatsCan Table 18-10-0004 expose a vector for CPI excluding indirect taxes?

**Finding:** INCONCLUSIVE — Valet has no CPI ex-indirect-taxes series. StatsCan API endpoints (metadata, series summary) returned 404/405 errors; cannot verify vectors directly.

**Recommendation:** Manual fallback required. Contact StatsCan support or check the web table directly at https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata for Table 18-10-0004. Alternatively, use headline CPI (available) and note in framework that ex-tax decomposition is not yet sourced. Mark as **Tier 1, unverified** until vector is confirmed.

---

## 3. CORRA (Overnight Repo Rate)

**Question:** What is the canonical BoC Valet key for the daily CORRA?

**Finding:** YES — `CORRA_WEIGHTED_MEAN_RATE` confirmed.

| Key | Label | Source | Frequency | Confidence |
|-----|-------|--------|-----------|------------|
| `CORRA_WEIGHTED_MEAN_RATE` | Mean | BoC Valet | Daily | HIGH |

Hypothesis that `AVG.INTWO` is the key is incorrect; the actual key is `CORRA_WEIGHTED_MEAN_RATE`. This is the published CORRA average rate used in market operations.

**Recommendation:** Use `CORRA_WEIGHTED_MEAN_RATE`. No fallback needed.

---

## 4. Canadian IG Corporate Credit Spreads

**Question:** Does BoC Valet expose Canadian-specific investment-grade corporate credit spreads?

**Finding:** NO direct Canadian IG spread series in Valet. Only metadata entry found: `FVI_ECML_CORP` (label: "ECML") — unclear if this is IG-specific or what the unit/frequency are.

**Recommendation:** Assume not available. **Fallback:** Use US ICE BofA IG spread `BAMLC0A0CM` on FRED (daily, free, 1997-present) as a proxy. This is a standard market benchmark and covers the relevant period. Document in blurb that Canadian-specific IG spread is unavailable and US IG is used as proxy.

---

## 5. TSX Composite Index

**Question:** Is TSX Composite available in a queryable data source?

**Finding:** PARTIAL — BoC Valet has `SAN_LEBM180118_CHART2D_A_TSX` (label: "TSX") but purpose/frequency unclear. FRED series `SPTSXINL` (TSX Composite, daily, 1979-present) is canonical but API endpoint returned 404 (likely requires authentication or is geographically restricted).

**Recommendation:** Try `SAN_LEBM180118_CHART2D_A_TSX` from Valet first. If unavailable or inadequate, confirm whether FRED `SPTSXINL` is accessible from the pipeline environment. If both fail, note that TSX Composite is obtainable from Yahoo Finance (`^GSPTSE`) or Canadian financial data vendors as a third fallback.

---

## Summary

| Question | Status | Recommendation |
|----------|--------|-----------------|
| Output gap | **FOUND** | Use `INDINF_OUTGAPMPR_Q` |
| CPI ex-taxes | **UNRESOLVED** | Manual vector lookup required; mark Tier 1 for now |
| CORRA | **FOUND** | Use `CORRA_WEIGHTED_MEAN_RATE` |
| IG spreads | **NOT FOUND** | Fallback to US `BAMLC0A0CM` on FRED |
| TSX | **PARTIAL** | Try Valet first; FRED endpoint may be blocked |

**Next step:** Before charting, confirm StatsCan vector ID for CPI ex-indirect-taxes and test FRED access for TSX from pipeline environment.

---

## Follow-up Probes (2026-05-09)

### 1. CPI ex-indirect-taxes vector — RESOLVED

**Method:** Queried BoC Valet series list for "indirect" and "tax" keywords.

**Finding:** YES — BoC Valet series `MPR_2025M04_CPI_TAX_S1` (label: "Total CPI excluding indirect taxes") confirmed working.

| Key | Label | Source | Frequency | Confidence |
|-----|-------|--------|-----------|------------|
| `MPR_2025M04_CPI_TAX_S1` | Total CPI excluding indirect taxes | BoC Valet | Monthly | HIGH |

**Notes:** Series from April 2025 MPR chart spec. Data validates (returns 2.1% for 2025-03, 2.9% for 2025-02). Alternative series also exist for later MPRs (`MPR_2025M07_CPI_*`, `MPR_2026M04_CPI_*`). Use most recent MPR release's series for current data.

**Recommendation:** Use `MPR_2025M04_CPI_TAX_S1` or later-dated variant depending on publication date. No fallback needed; data path confirmed.

---

### 2. TSX Composite — PARTIAL RESOLUTION

**Method:** Tested BoC Valet series, FRED endpoint, and FRED search.

**Finding — BoC Valet:** Series `SAN_LEBM180118_CHART2D_A_TSX` exists but is **NOT suitable**. Label is "TSX" but description is "Impulse response for S&P/TSX" — this is a model artifact (impulse response coefficients), not raw index data. Data spans 2002–present but values (e.g., 1.469, 1.348, 1.222) are normalized responses, not index levels.

**Finding — FRED:** Series `SPTSXINL` (previously noted) returns **404 Not Found** consistently. FRED search API and search page both unreachable / return no TSX results.

**Finding — Yahoo Finance:** Ticker `^GSPTSE` is the canonical TSX Composite ticker and is available via `yfinance` package (free, no key required, daily data, full history). Would require adding `yfinance` as a dependency.

| Endpoint | Series | Data | Recommendation |
|----------|--------|------|-----------------|
| BoC Valet | `SAN_LEBM180118_CHART2D_A_TSX` | Impulse response (not usable) | **NO** |
| FRED | `SPTSXINL` | 404 Not Found | **NO** |
| Yahoo Finance | `^GSPTSE` | Daily index levels, full history | **YES** |

**Recommendation:** Implement TSX via `yfinance` and `^GSPTSE` ticker. This is the only viable open data path with production-grade frequency and history. Note the dependency requirement in code comments.
