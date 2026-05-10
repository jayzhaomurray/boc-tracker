# StatsCan 6-Table Probe Results
**Date:** 2026-05-10

**Method:** WDS REST API (getCubeMetadata) + CSV bulk download (vectorId extraction) + getDataFromVectorsAndLatestNPeriods verification

**Key finding:** The `getSeriesInfoFromCubePidCoord` endpoint is unavailable (404 for all coords) as of 2026-05-10. The working path is: (1) `getCubeMetadata` with 8-digit product IDs for dimension maps, (2) CSV bulk download from `https://www150.statcan.gc.ca/n1/tbl/csv/{pid}-eng.zip` to extract vectorIds, (3) `getDataFromVectorsAndLatestNPeriods` to verify recent data.

**Product ID format:** `getCubeMetadata` requires 8-digit IDs (strip trailing `-01` and hyphens from table ID, e.g. `34-10-0035-01` -> `34100035`). The original table IDs as provided do NOT always match actual WDS products — correct product IDs were identified via `getAllCubesList`.

---

## Table 1: 34-10-0035-01 — Capacity Utilization, Total Manufacturing, Canada

**Actual WDS product:** 16100109 — "Industrial capacity utilization rates, by industry" (quarterly, SA)

getCubeMetadata pid=16100109: **SUCCESS**
Title: Industrial capacity utilization rates, by industry

**Dimension 1: Geography**
  [1] Canada

**Dimension 2: NAICS**
  [1] Total industrial
  [8] Manufacturing [31-33]
  ... (28 members total)

### Confirmed Vectors

| Series | Vector ID | Latest date | Latest value |
|--------|-----------|-------------|--------------|
| Canada, Total industrial capacity utilization | **4331081** | 2025-10-01 | 78.5% |
| Canada, Manufacturing [31-33] capacity utilization | **4331088** | 2025-10-01 | 77.7% |

Latest 3 (V4331081 — Total industrial): `[('2025-04-01', 78.0), ('2025-07-01', 78.9), ('2025-10-01', 78.5)]`
Latest 3 (V4331088 — Manufacturing): `[('2025-04-01', 76.7), ('2025-07-01', 78.0), ('2025-10-01', 77.7)]`

**STATUS: CONFIRMED** — Quarterly through 2025-Q4.

---

## Table 2: 14-10-0022-01 — EI Regular Beneficiaries, Canada, Monthly SA

**Actual WDS product:** 14100011 — "Employment insurance beneficiaries (regular benefits) by province and territory, monthly, seasonally adjusted"

getCubeMetadata pid=14100011: **SUCCESS**

**Dimensions:**
- Dim1: Geography — [1] Canada, ...
- Dim2: Beneficiary detail — [2] Regular benefits, [16] Regular benefits without declared earnings
- Dim3: Sex — [1] Both sexes, [2] Males, [3] Females
- Dim4: Age group — [1] 15 years and over, [2] 15-24, [5] 25-54, [12] 55+

### Confirmed Vector

| Series | Vector ID | Latest date | Latest value |
|--------|-----------|-------------|--------------|
| Canada, Regular benefits, Both sexes, 15+, SA | **64549350** | 2026-02-01 | 542,110 persons |

Latest 3 (V64549350): `[('2025-12-01', 567620.0), ('2026-01-01', 550840.0), ('2026-02-01', 542110.0)]`

**STATUS: CONFIRMED** — Monthly SA through 2026-02.

---

## Table 3: 12-10-0011-01 — Merchandise Trade, Canada-US Bilateral

**WDS product:** 12100011 — "International merchandise trade for all countries and by Principal Trading Partners, monthly"

getCubeMetadata pid=12100011: **SUCCESS**

**Dimensions:**
- Dim1: Geography — [1] Canada
- Dim2: Trade — [1] Import, [2] Export, [3] Trade Balance
- Dim3: Basis — [1] Customs, [2] Balance of payments
- Dim4: Seasonal adjustment — [1] Unadjusted, [2] Seasonally adjusted
- Dim5: Principal trading partners — [1] All countries, [2] United States, [3] EU, ...

**Note:** Trade Balance rows are only available on Balance of payments basis (not Customs) in this table.

### Confirmed Vectors

| Series | Vector ID | Latest date | Latest value |
|--------|-----------|-------------|--------------|
| Canada, Exports, Customs, SA, United States | **87008898** | 2026-03-01 | C$45,495.8M |
| Canada, Imports, Customs, SA, United States | **87008782** | 2026-03-01 | C$30,237.6M |
| Canada, Trade Balance, BOP, SA, United States | **87008985** | 2026-03-01 | C$7,071.2M |
| Canada, Exports, Customs, SA, All countries | **87008897** | 2026-03-01 | C$68,793.6M |
| Canada, Imports, Customs, SA, All countries | **87008781** | 2026-03-01 | C$66,751.6M |
| Canada, Trade Balance, BOP, SA, All countries | **87008984** | 2026-03-01 | C$1,779.3M |

Latest 3 (V87008898 — Exports SA US): `[('2026-01-01', 41567.8), ('2026-02-01', 45050.0), ('2026-03-01', 45495.8)]`
Latest 3 (V87008782 — Imports SA US): `[('2026-01-01', 28711.5), ('2026-02-01', 31339.4), ('2026-03-01', 30237.6)]`
Latest 3 (V87008985 — Balance BOP SA US): `[('2026-01-01', 5799.5), ('2026-02-01', 2858.0), ('2026-03-01', 7071.2)]`

**STATUS: CONFIRMED** — Monthly SA through 2026-03.

---

## Table 4: 17-10-0040-01 — Population Components (International Migration), Quarterly

**WDS product:** 17100040 — "Estimates of the components of international migration, quarterly"

**Important scope note:** This table covers international migration components only. Natural increase (births minus deaths) is NOT in this table — it is available only annually (table 17100008). The task description says "natural increase, net immigration" but 17-10-0040-01 does not contain natural increase.

getCubeMetadata pid=17100040: **SUCCESS**
Title: Estimates of the components of international migration, quarterly

**Dimensions:**
- Dim1: Geography — [1] Canada, ...
- Dim2: Components — [1] Immigrants, [6] Net emigration, [2] Emigrants, [3] Returning emigrants, [4] Net temporary emigration, [5] Net non-permanent residents, [7] NPR inflows, [8] NPR outflows

### Confirmed Vectors

| Series | Vector ID | Latest date | Latest value |
|--------|-----------|-------------|--------------|
| Canada, Immigrants | **29850342** | 2025-10-01 | 83,168 persons |
| Canada, Emigrants | **29850343** | 2025-10-01 | 24,907 persons |
| Canada, Net emigration | **1566834788** | 2025-10-01 | 14,595 persons |
| Canada, Net non-permanent residents | **29850346** | 2025-10-01 | -171,296 persons |
| Canada, NPR inflows | **1566834758** | 2025-10-01 | 77,084 persons |

Latest 3 (V29850342 — Immigrants): `[('2025-04-01', 103507.0), ('2025-07-01', 102867.0), ('2025-10-01', 83168.0)]`
Latest 3 (V29850346 — Net NPR): `[('2025-04-01', -58719.0), ('2025-07-01', -176479.0), ('2025-10-01', -171296.0)]`

**STATUS: CONFIRMED** — Quarterly through 2025-Q4.

---

## Table 5: 17-10-0009-01 — Population Stock, Canada, Quarterly

**WDS product:** 17100009 — "Population estimates, quarterly"

getCubeMetadata pid=17100009: **SUCCESS**
Title: Population estimates, quarterly
Dimensions: Geography only (no age breakdown in this table)

**Scope note:** This table has only a Geography dimension — no age groups. The task asks for "population stock by age group" but 17-10-0009-01 contains total population by geography only. Age-disaggregated population is available annually in table 17100005 (July 1 estimates).

### Confirmed Vector

| Series | Vector ID | Latest date | Latest value |
|--------|-----------|-------------|--------------|
| Canada, Population total | **1** | 2026-01-01 | 41,472,081 |

Latest 3 (V1): `[('2025-07-01', 41651653.0), ('2025-10-01', 41575585.0), ('2026-01-01', 41472081.0)]`

**STATUS: CONFIRMED (total only)** — Quarterly through 2026-Q1. Age breakdown not in this table.

---

## Table 6: 14-10-0027-01 — Labour Force, Participation + Employment Rate, Monthly SA

**Actual WDS product:** 14100287 — "Labour force characteristics, monthly, seasonally adjusted and trend-cycle"

getCubeMetadata pid=14100287: **SUCCESS**
Title: Labour force characteristics, monthly, seasonally adjusted and trend-cycle

**Dimensions:**
- Dim1: Geography — [1] Canada, provinces
- Dim2: LF characteristics — [7] Unemployment rate, [8] Participation rate, [9] Employment rate (+ others)
- Dim3: Gender — [1] Total - Gender, [2] Men+, [3] Women+
- Dim4: Age group — [1] 15+, [2] 15-24, [6] 25-54, [7] 55+, etc.
- Dim5: Statistics — [1] Estimate
- Dim6: Data type — [1] Seasonally adjusted

### Confirmed Vectors

| Series | Vector ID | Latest date | Latest value |
|--------|-----------|-------------|--------------|
| Participation rate, Canada, Total, 15+, SA | **2062816** | 2026-04-01 | 65.0% |
| Employment rate, Canada, Total, 15+, SA | **2062817** | 2026-04-01 | 60.5% |
| Unemployment rate, Canada, Total, 15+, SA | **2062815** | 2026-04-01 | 6.9% |
| Participation rate, Canada, Total, 25-54 (prime-age), SA | **2062951** | 2026-04-01 | 88.5% |
| Employment rate, Canada, Total, 25-54 (prime-age), SA | **2062952** | 2026-04-01 | 83.2% |
| Unemployment rate, Canada, Total, 25-54 (prime-age), SA | **2062950** | 2026-04-01 | 6.0% |
| Participation rate, Canada, Total, 15-24 (youth), SA | **2062843** | 2026-04-01 | 62.9% |
| Employment rate, Canada, Total, 15-24 (youth), SA | **2062844** | 2026-04-01 | 53.9% |
| Unemployment rate, Canada, Total, 15-24 (youth), SA | **2062842** | 2026-04-01 | 14.3% |

**STATUS: CONFIRMED** — Monthly SA through 2026-04.

---

## CONFIRMED VECTORS — Summary Table

| Series | Table | Vector ID | Frequency | Latest date | Latest value | CSV name |
|--------|-------|-----------|-----------|-------------|--------------|----------|
| Industrial cap util, Canada, Total industrial | 34-10-0035-01 (pid 16100109) | **4331081** | Quarterly | 2025-10-01 | 78.5% | capacity_util_total_industrial |
| Manufacturing cap util, Canada, [31-33] | 34-10-0035-01 (pid 16100109) | **4331088** | Quarterly | 2025-10-01 | 77.7% | capacity_util_mfg_sa |
| EI regular benefits, Canada, Both sexes, 15+, SA | 14-10-0022-01 (pid 14100011) | **64549350** | Monthly | 2026-02-01 | 542,110 | ei_regular_beneficiaries_sa |
| Merchandise exports, Customs, SA, United States | 12-10-0011-01 (pid 12100011) | **87008898** | Monthly | 2026-03-01 | C$45,495.8M | trade_exports_sa_us |
| Merchandise imports, Customs, SA, United States | 12-10-0011-01 (pid 12100011) | **87008782** | Monthly | 2026-03-01 | C$30,237.6M | trade_imports_sa_us |
| Trade balance, BOP basis, SA, United States | 12-10-0011-01 (pid 12100011) | **87008985** | Monthly | 2026-03-01 | C$7,071.2M | trade_balance_bop_sa_us |
| Merchandise exports, Customs, SA, All countries | 12-10-0011-01 (pid 12100011) | **87008897** | Monthly | 2026-03-01 | C$68,793.6M | trade_exports_sa_all |
| Merchandise imports, Customs, SA, All countries | 12-10-0011-01 (pid 12100011) | **87008781** | Monthly | 2026-03-01 | C$66,751.6M | trade_imports_sa_all |
| Trade balance, BOP basis, SA, All countries | 12-10-0011-01 (pid 12100011) | **87008984** | Monthly | 2026-03-01 | C$1,779.3M | trade_balance_bop_sa_all |
| International immigrants, Canada | 17-10-0040-01 (pid 17100040) | **29850342** | Quarterly | 2025-10-01 | 83,168 | pop_immigrants_qtly |
| Emigrants, Canada | 17-10-0040-01 (pid 17100040) | **29850343** | Quarterly | 2025-10-01 | 24,907 | pop_emigrants_qtly |
| Net emigration, Canada | 17-10-0040-01 (pid 17100040) | **1566834788** | Quarterly | 2025-10-01 | 14,595 | pop_net_emigration_qtly |
| Net non-permanent residents, Canada | 17-10-0040-01 (pid 17100040) | **29850346** | Quarterly | 2025-10-01 | -171,296 | pop_net_npr_qtly |
| NPR inflows, Canada | 17-10-0040-01 (pid 17100040) | **1566834758** | Quarterly | 2025-10-01 | 77,084 | pop_npr_inflows_qtly |
| Population total, Canada | 17-10-0009-01 (pid 17100009) | **1** | Quarterly | 2026-01-01 | 41,472,081 | pop_total_qtly |
| Participation rate, Canada, Total, 15+, SA | 14-10-0027-01 (pid 14100287) | **2062816** | Monthly | 2026-04-01 | 65.0% | lf_participation_rate_15plus_sa |
| Employment rate, Canada, Total, 15+, SA | 14-10-0027-01 (pid 14100287) | **2062817** | Monthly | 2026-04-01 | 60.5% | lf_employment_rate_15plus_sa |
| Unemployment rate, Canada, Total, 15+, SA | 14-10-0027-01 (pid 14100287) | **2062815** | Monthly | 2026-04-01 | 6.9% | lf_unemployment_rate_15plus_sa |
| Participation rate, Canada, Total, 25-54, SA | 14-10-0027-01 (pid 14100287) | **2062951** | Monthly | 2026-04-01 | 88.5% | lf_participation_rate_prime_sa |
| Employment rate, Canada, Total, 25-54, SA | 14-10-0027-01 (pid 14100287) | **2062952** | Monthly | 2026-04-01 | 83.2% | lf_employment_rate_prime_sa |
| Unemployment rate, Canada, Total, 25-54, SA | 14-10-0027-01 (pid 14100287) | **2062950** | Monthly | 2026-04-01 | 6.0% | lf_unemployment_rate_prime_sa |
| Participation rate, Canada, Total, 15-24, SA | 14-10-0027-01 (pid 14100287) | **2062843** | Monthly | 2026-04-01 | 62.9% | lf_participation_rate_youth_sa |
| Employment rate, Canada, Total, 15-24, SA | 14-10-0027-01 (pid 14100287) | **2062844** | Monthly | 2026-04-01 | 53.9% | lf_employment_rate_youth_sa |
| Unemployment rate, Canada, Total, 15-24, SA | 14-10-0027-01 (pid 14100287) | **2062842** | Monthly | 2026-04-01 | 14.3% | lf_unemployment_rate_youth_sa |

---

## Per-Table Status

- **34-10-0035-01** (Capacity utilization, total manufacturing, SA): **CONFIRMED** — 2 vectors (Total industrial V4331081, Manufacturing V4331088); quarterly through 2025-Q4
- **14-10-0022-01** (EI regular beneficiaries, Canada, monthly SA): **CONFIRMED** — 1 core vector (V64549350); monthly through 2026-02
- **12-10-0011-01** (Merchandise trade, Canada-US bilateral): **CONFIRMED** — 6 vectors (exports/imports SA Customs + BOP balance, US and All countries); monthly through 2026-03
- **17-10-0040-01** (Population components, international migration): **CONFIRMED** — 5 vectors (immigrants, emigrants, net emigration, net NPR, NPR inflows); quarterly through 2025-Q4. Natural increase NOT in this table.
- **17-10-0009-01** (Population stock quarterly): **CONFIRMED (total only)** — V1 = Canada total (41.5M); quarterly through 2026-Q1. Age breakdown NOT in this table.
- **14-10-0027-01** (Labour force by age/sex, participation + employment rate, monthly SA): **CONFIRMED** — 9 vectors covering 15+, prime-age (25-54), and youth (15-24); monthly through 2026-04

---

## API Notes for Pipeline

- **getCubeMetadata:** POST to `/getCubeMetadata` with 8-digit product ID. Working as of 2026-05-10. Required format: e.g. `16100109` (not `34100035` which resolves to a different table).
- **getSeriesInfoFromCubePidCoord:** 404 for all inputs as of 2026-05-10. Not usable.
- **getDataFromVectorsAndLatestNPeriods:** POST with `[{"vectorId": N, "latestN": K}]`. Working.
- **CSV bulk download:** `https://www150.statcan.gc.ca/n1/tbl/csv/{8-digit-pid}-eng.zip` — most reliable path to discover vector IDs. Contains VECTOR column with `vNNNNNNN` format. Use this for any new table.
- **getAllCubesList:** GET endpoint returns all 8,167 tables with product IDs and titles. Use to map table name to correct 8-digit product ID.
- **Table ID to WDS product ID mapping:** The table numbers in StatsCan URLs (e.g. `34-10-0035-01`) do NOT directly translate to WDS product IDs. Use `getAllCubesList` and filter by title keywords to find the correct 8-digit product ID.
