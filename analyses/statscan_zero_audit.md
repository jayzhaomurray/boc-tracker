# StatsCan zero-audit report

**Audit date:** 2026-05-09
**Provenance tier:** Tier 2 (autonomous audit; not user-reviewed). See `markdown-files/verification/_tiers.md`.

Re-fetches every StatsCan vector with the NaN-preserving fetch_statscan and diffs against the saved CSV. Looks for the same defect class that the JVWS COVID-gap bug exposed (saved 0.0 where live API returns null), plus any other date-coverage mismatches.

**Summary:**
- 33 StatsCan series audited.
- 21 series clean (no findings).
- **0 series with stale-zero-bug occurrences.** (The JVWS COVID-gap defect was unique to that series.)
- 0 series failed audit (live fetch failed or saved CSV missing).
- 12 series have benign leading-NaN-padding mismatches (see Verdict below).

## Verdict

**No critical issues found.** The 12 findings below are all the same benign class: the saved CSV has fewer rows than the live API because an older vintage of `fetch_statscan` called `.dropna()`, which stripped leading NaN rows. The new NaN-preserving fetcher (commit `529ce45`) returns those leading rows. Re-fetching would add the leading-NaN padding back to the saved CSVs.

**Specific patterns:**
- **CPI components (cpi_food, cpi_services, cpi_energy, cpi_goods, cpi_shelter):** the live API returns the full 18-10-0004 table from 1914 onward; each component has actual values starting later (e.g. food from 1949, shelter much later). The old fetcher dropped the pre-data NaN; the new one keeps it. ~400–750 leading-NaN rows per series.
- **GDP contributions (gdp_total_contribution, gdp_contrib_*):** missing 1961-Q1 row. The live API returns NaN for that quarter (Q/Q growth needs a prior quarter that doesn't exist in the table); the old fetcher dropped it.

**Downstream impact:** none. Rolling means use `min_periods` (skip leading NaN naturally); `asof()` calls `.dropna()` internally; Plotly auto-skips NaN. The audit is purely cosmetic data-coverage truth-telling.

**Two options to resolve:**
- **A. Re-fetch and accept the new row counts.** Run `python fetch.py` (or per-series targeted fetches). Saved CSVs gain the leading-NaN rows. Storage cost is trivial (~50 KB across all 12 series). Saved data matches live API exactly.
- **B. Tighten `fetch_statscan` to strip *leading* NaN while preserving *interior* NaN.** Keeps the JVWS-class fix but doesn't bloat saved CSVs with empty padding. Slightly more code; one boolean. Recommended only if option A produces visible CSV-bloat in any consumer.

User to choose. Option A is the simpler and more honest move; option B is the lower-noise long-term answer.

**How to fix a stale-zero finding:** re-fetch the affected series via `python fetch.py` (the NaN-preserving fetcher will overwrite the saved CSV with NaN rows where the API returns null). For a one-off targeted fix, see the JVWS pattern in commit `529ce45` for the inline Python snippet.

---

## Series with findings

### `cpi_services` (vector 41691230)

- Saved CSV: 783 rows (NaN: 0, zero: 0)
- Live API: 1347 rows (NaN: 564, zero: 0)
- **Finding:** 564 dates in live API are not in saved CSV (saved CSV is stale; re-fetch would add them).

  Dates in live-only (sample; would be added by re-fetch):
    - 1914-01-01
    - 1914-02-01
    - 1914-03-01
    - 1914-04-01
    - 1914-05-01
    - 1914-06-01
    - 1914-07-01
    - 1914-08-01
    - 1914-09-01
    - 1914-10-01

### `cpi_food` (vector 41690974)

- Saved CSV: 927 rows (NaN: 0, zero: 0)
- Live API: 1347 rows (NaN: 420, zero: 0)
- **Finding:** 420 dates in live API are not in saved CSV (saved CSV is stale; re-fetch would add them).

  Dates in live-only (sample; would be added by re-fetch):
    - 1914-01-01
    - 1914-02-01
    - 1914-03-01
    - 1914-04-01
    - 1914-05-01
    - 1914-06-01
    - 1914-07-01
    - 1914-08-01
    - 1914-09-01
    - 1914-10-01

### `cpi_energy` (vector 41691239)

- Saved CSV: 783 rows (NaN: 0, zero: 0)
- Live API: 1347 rows (NaN: 564, zero: 0)
- **Finding:** 564 dates in live API are not in saved CSV (saved CSV is stale; re-fetch would add them).

  Dates in live-only (sample; would be added by re-fetch):
    - 1914-01-01
    - 1914-02-01
    - 1914-03-01
    - 1914-04-01
    - 1914-05-01
    - 1914-06-01
    - 1914-07-01
    - 1914-08-01
    - 1914-09-01
    - 1914-10-01

### `cpi_goods` (vector 41691222)

- Saved CSV: 783 rows (NaN: 0, zero: 0)
- Live API: 1347 rows (NaN: 564, zero: 0)
- **Finding:** 564 dates in live API are not in saved CSV (saved CSV is stale; re-fetch would add them).

  Dates in live-only (sample; would be added by re-fetch):
    - 1914-01-01
    - 1914-02-01
    - 1914-03-01
    - 1914-04-01
    - 1914-05-01
    - 1914-06-01
    - 1914-07-01
    - 1914-08-01
    - 1914-09-01
    - 1914-10-01

### `cpi_shelter` (vector 41691050)

- Saved CSV: 600 rows (NaN: 29, zero: 0)
- Live API: 1347 rows (NaN: 776, zero: 0)
- **Finding:** 747 dates in live API are not in saved CSV (saved CSV is stale; re-fetch would add them).

  Dates in live-only (sample; would be added by re-fetch):
    - 1914-01-01
    - 1914-02-01
    - 1914-03-01
    - 1914-04-01
    - 1914-05-01
    - 1914-06-01
    - 1914-07-01
    - 1914-08-01
    - 1914-09-01
    - 1914-10-01

### `gdp_total_contribution` (vector 79448580)

- Saved CSV: 259 rows (NaN: 0, zero: 0)
- Live API: 260 rows (NaN: 1, zero: 0)
- **Finding:** 1 dates in live API are not in saved CSV (saved CSV is stale; re-fetch would add them).

  Dates in live-only (sample; would be added by re-fetch):
    - 1961-01-01

### `gdp_contrib_consumption` (vector 79448555)

- Saved CSV: 259 rows (NaN: 0, zero: 1)
- Live API: 260 rows (NaN: 1, zero: 1)
- **Finding:** 1 dates in live API are not in saved CSV (saved CSV is stale; re-fetch would add them).

  Dates in live-only (sample; would be added by re-fetch):
    - 1961-01-01

### `gdp_contrib_govt` (vector 79448562)

- Saved CSV: 259 rows (NaN: 0, zero: 0)
- Live API: 260 rows (NaN: 1, zero: 0)
- **Finding:** 1 dates in live API are not in saved CSV (saved CSV is stale; re-fetch would add them).

  Dates in live-only (sample; would be added by re-fetch):
    - 1961-01-01

### `gdp_contrib_investment` (vector 79448563)

- Saved CSV: 259 rows (NaN: 0, zero: 0)
- Live API: 260 rows (NaN: 1, zero: 0)
- **Finding:** 1 dates in live API are not in saved CSV (saved CSV is stale; re-fetch would add them).

  Dates in live-only (sample; would be added by re-fetch):
    - 1961-01-01

### `gdp_contrib_inventories` (vector 79448572)

- Saved CSV: 259 rows (NaN: 0, zero: 0)
- Live API: 260 rows (NaN: 1, zero: 0)
- **Finding:** 1 dates in live API are not in saved CSV (saved CSV is stale; re-fetch would add them).

  Dates in live-only (sample; would be added by re-fetch):
    - 1961-01-01

### `gdp_contrib_exports` (vector 79448573)

- Saved CSV: 259 rows (NaN: 0, zero: 0)
- Live API: 260 rows (NaN: 1, zero: 0)
- **Finding:** 1 dates in live API are not in saved CSV (saved CSV is stale; re-fetch would add them).

  Dates in live-only (sample; would be added by re-fetch):
    - 1961-01-01

### `gdp_contrib_imports` (vector 79448576)

- Saved CSV: 259 rows (NaN: 0, zero: 0)
- Live API: 260 rows (NaN: 1, zero: 0)
- **Finding:** 1 dates in live API are not in saved CSV (saved CSV is stale; re-fetch would add them).

  Dates in live-only (sample; would be added by re-fetch):
    - 1961-01-01

## Clean series (no findings)

- `cpi_all_items` (vector 41690914; 411 rows)
- `cpi_all_items_nsa` (vector 41690973; 1347 rows)
- `unemployment_rate` (vector 2062815; 604 rows)
- `lfs_wages_all` (vector 105812645; 304 rows)
- `lfs_wages_permanent` (vector 105812715; 304 rows)
- `seph_earnings` (vector 79311153; 302 rows)
- `gdp_monthly` (vector 65201210; 350 rows)
- `gdp_industry_goods` (vector 65201211; 350 rows)
- `gdp_industry_services` (vector 65201212; 350 rows)
- `gdp_industry_manufacturing` (vector 65201263; 350 rows)
- `gdp_industry_mining_oil` (vector 65201236; 350 rows)
- `gdp_quarterly` (vector 62305752; 260 rows)
- `employment_rate` (vector 2062817; 604 rows)
- `participation_rate` (vector 2062816; 604 rows)
- `job_vacancy_rate` (vector 1212389365; 131 rows)
- `unemployment_level` (vector 2062814; 604 rows)
- `job_vacancy_level` (vector 1212389364; 131 rows)
- `unit_labour_cost` (vector 1409159; 180 rows)
- `housing_starts` (vector 52300157; 435 rows)
- `new_housing_price_index` (vector 111955442; 543 rows)
- `residential_permits` (vector 1675119646; 98 rows)

