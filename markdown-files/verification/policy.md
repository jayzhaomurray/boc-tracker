# Verification log: Monetary Policy section

Per-claim source log for the Monetary Policy section of `analysis_framework.md` (lines 88-154). Each named claim in the framework should appear here with: (a) the framework prose verbatim, (b) the primary source(s) that back it, (c) a direct quote from the source where possible, (d) a verification verdict, (e) a provenance tier (see `_tiers.md`), and (f) any analyst notes / defects.

This file is **not** in CLAUDE.md's "First moves" auto-load list — it's a working log for claim-by-claim review, kept separate from the framework prose to avoid bloating session-init context. The framework itself carries inline citations; this log carries the page-level evidence chain.

This log was produced by a Tier-2 autonomous verification pass on 2026-05-09. Per the `_tiers.md` warning: "Tier 2 is the most dangerous tier because it looks authoritative on the surface (sources cited, structured verdict glossary, primary-source URLs) but has not been challenged." Treat all entries as ready-for-user-review, NOT final.

**Provenance tiers (see `_tiers.md` for full glossary):**
- **Tier 1 — Generated.** Claude-written, no verification.
- **Tier 2 — Autonomously verified.** Claude / sub-agent ran sources, the user did NOT review.
- **Tier 3 — User-verified.** User pushed back on framings, accepted/rejected/revised per claim.

**Verification verdict glossary (orthogonal to tier):**

- **VERIFIED** — direct quote from a primary source supports the framework claim.
- **PARTIALLY VERIFIED** — primary source supports the substance but the framework's specific framing or numbers extend beyond the source.
- **CONTESTED** — primary sources disagree, the BoC's position differs from broader analyst consensus, or empirical data contradicts the framework.
- **UNSOURCED — analyst judgment** — the claim is the analyst's framing, not a direct primary-source claim. Should be marked as such in framework prose if kept.
- **PENDING** — not yet researched.

The framework prose is on lines 88-154 of `markdown-files/analysis_framework.md`. The framework's own status banner (line 90) reads: *"VERIFIED end-to-end (May 2026). Every analytical claim audited against BoC primary sources … and empirical distributions"* — this audit pass tests that banner.

---

## Claim 1: Neutral rate range 2.25–3.25%, unchanged since April 2024

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim, line 109)

> The BoC's official neutral-rate range is **2.25–3.25%**, unchanged since the April 2024 r* update ([Staff Analytical Note 2025-16](https://www.bankofcanada.ca/2025/06/staff-analytical-note-2025-16/); MPR April 2026 Appendix). BoC frames this as a range, not a midpoint — the full 100bp span is the published uncertainty zone.

### Verification verdict

**VERIFIED.** Both cited sources support the 2.25–3.25% range. The "unchanged since April 2024" claim is supported by SAN 2025-16's own language. MPR April 2026 Appendix explicitly states the range and notes the projection assumes the midpoint.

### Source 1 — SAN 2025-16 (June 2025)

**URL:** https://www.bankofcanada.ca/2025/06/staff-analytical-note-2025-16/

**Direct quote (paraphrased from WebFetch retrieval — sub-agent could not capture full verbatim):** *"We assess both the US and the Canadian nominal neutral rate to be in the range of 2.25% to 3.25%, unchanged from the 2024 range."*

**Methodology:** SAN 2025-16 uses overlapping-generations, risk-augmented neoclassical growth, and term-structure models. The full 100bp band reflects model-uncertainty across these approaches.

**Verdict:** VERIFIED.

### Source 2 — MPR April 2026 Appendix ("Potential output and the nominal neutral rate of interest")

**URL:** https://www.bankofcanada.ca/publications/mpr/mpr-2026-04-29/appendix/

**Key finding (per WebSearch retrieval):** *"The nominal neutral interest rate in Canada is estimated to be in the range of 2.25% to 3.25%, with the projection assuming the nominal neutral interest rate is at the midpoint of this range."*

**Verdict:** VERIFIED — confirms the range and clarifies the BoC's projection-assumption choice (midpoint), which the framework's "BoC frames this as a range, not a midpoint" framing partially obscures. The framework might benefit from acknowledging that BoC projections *do* use the midpoint internally even though the published number is a band.

### Defects flagged

1. **Mild framing tension:** Framework says *"BoC frames this as a range, not a midpoint."* The MPR appendix says the projection assumes the midpoint. Both are true (the *published* figure is a range; the *projection mechanics* use the midpoint), but the framework's emphasis could mislead a reader into thinking the BoC never uses 2.75%. Soften or qualify.

### Open questions for user review

1. Should the framework note that BoC projections operationalise the neutral rate at the 2.75% midpoint, while still publishing the band as the headline?

---

## Claim 2: BoC balance sheet operational timeline (April 2020 – March 2025)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim, lines 132-137)

> BoC balance sheet operational timeline (per BoC press releases):
> - **April 1, 2020 – October 27, 2021:** Government of Canada Bond Purchase Program (GBPP), QE phase.
> - **October 27, 2021 – April 25, 2022:** reinvestment phase (maturing bonds replaced; balance sheet roughly flat).
> - **April 25, 2022 – January 29, 2025:** passive QT (no active selling; bonds rolled off as they matured).
> - **[January 29, 2025](https://www.bankofcanada.ca/2025/01/fad-press-release-2025-01-29/):** BoC announces end of QT and plan to restore normal-course asset purchases.
> - **March 5, 2025 onwards:** term repos restarted (bi-weekly, $2–5B per operation) as routine balance-sheet management; T-bill purchases resume Q4 2025; secondary-market GoC bond purchases earliest end-2026.

### Verification verdict

**PARTIALLY VERIFIED.** Most dates align with BoC press releases, with one date-precision issue and one programmatic-naming issue.

### Source 1 — January 29, 2025 BoC press release (cited in framework)

**URL:** https://www.bankofcanada.ca/2025/01/fad-press-release-2025-01-29/

**Direct quote (per WebFetch):** *"The Bank is also announcing its plan to complete the normalization of its balance sheet, ending quantitative tightening."* and *"the Bank will restart its term repo program effective March 5, 2025 and operations will be conducted every two weeks."*

**Verdict:** VERIFIED.

### Source 2 — October 27, 2021 BoC FAD press release

**URL:** https://www.bankofcanada.ca/2021/10/fad-press-release-2021-10-27/

**Key finding (per WebSearch retrieval):** *"The Bank is ending quantitative easing (QE) and moving into the reinvestment phase."* The reinvestment phase was effective **November 1, 2021**, not October 27, 2021 as the framework's date string implies. October 27 was the announcement date; November 1 was the effective operational start of reinvestment.

**Verdict:** PARTIALLY VERIFIED. Framework's "October 27, 2021 – April 25, 2022" boundary should arguably be "November 1, 2021 – April 25, 2022" if the dates are operational. Minor (4-day) but the QT start date below uses the operational distinction (April 25, not April 13), so this is inconsistent within the framework.

### Source 3 — April 13, 2022 FAD press release / April 25, 2022 operational start

**URL (announcement):** https://www.bankofcanada.ca/2022/04/fad-press-release-2022-04-13/  
**URL (operational details):** https://www.bankofcanada.ca/2022/04/bank-of-canada-provides-operational-details-for-quantitative-tightening-and-announces-that-it-will-continue-to-implement-monetary-policy-using-a-floor-system/

**Key finding (per WebSearch):** Framework's April 25, 2022 date is the operational QT start (the date the BoC stopped purchasing GoC bonds in primary or secondary markets). April 13, 2022 was the announcement. Framework's choice of operational date is internally defensible.

**Verdict:** VERIFIED for operational start; framework chose operational dates consistently here but inconsistently for the Oct 2021 boundary.

### Source 4 — March 27 / April 1, 2020 GBPP launch

**Key finding (per WebSearch):** *"The Bank of Canada launched the Government Bond Purchase Program (GBPP) on April 1, 2020, but the program was announced on March 27, 2020."* Framework's April 1, 2020 date is the operational launch, consistent with the BoC's operational-date convention used elsewhere.

**Verdict:** VERIFIED.

### Source 5 — GBPP terminology / scope

**URL:** https://www.bankofcanada.ca/markets/market-operations-liquidity-provision/market-operations-programs-and-facilities/government-canada-bond-purchase-program/

**Issue:** Framework uses "GBPP" to label *only* the QE-phase. But per BoC's own taxonomy, the GBPP had two phases: (a) the QE phase from April 1 2020 to October 27 2021, and (b) the reinvestment phase November 2021 to April 2022. The framework labels the QE-phase "GBPP" and the reinvestment phase as a separate timeline entry, which is reasonable for the user-facing distinction but slightly mis-uses the BoC's own program name (which spans both). Note also: line 115 of the framework says *"the 2020–2022 GBPP suppressed 2Y GoC ~20 bp below OIS-equivalent through scarcity"* — calling the program "the 2020-2022 GBPP" is reasonable (since GBPP-with-reinvestment ran through April 2022), but the QE-phase-only definition in line 133 differs from this scope.

**Verdict:** PARTIALLY VERIFIED — GBPP labelling is loose but defensible.

### Defects flagged

1. **Date-boundary inconsistency:** Oct 27, 2021 (announcement) vs. Apr 25, 2022 (operational). The framework picks "operational" for the Apr 2022 boundary but "announcement" for the Oct 2021 boundary. The reinvestment phase's *operational* start date was November 1, 2021. Either pick announcement dates throughout (use Apr 13 2022) or operational dates throughout (use Nov 1 2021 for reinvestment start). Currently mixed.
2. **GBPP scope ambiguity:** Framework's lines 133 and 115 use "GBPP" with different implicit scopes (QE-only vs. QE+reinvestment). Cosmetic but worth tightening.
3. **March 5 2025 term repo operation size "$2-5B per operation":** The framework asserts this but the cited press release WebFetch only confirmed bi-weekly cadence, not the $2-5B size band. PENDING — need to verify the operation-size band against subsequent BoC operational details releases.

### Open questions for user review

1. Adopt operational-dates-throughout convention or announcement-dates-throughout?
2. Verify the "$2-5B per operation" size band against term-repo announcement records?

### Proposed patches (mechanical only — judgment items deferred)

**Patch 1: GBPP scope tightening (line 115 vs line 133 use the program name with different implicit scopes — line 115 says "the 2020–2022 GBPP" which extends through reinvestment, while line 133 labels only the QE phase as GBPP)**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
  - **April 1, 2020 – October 27, 2021:** Government of Canada Bond Purchase Program (GBPP), QE phase.
```

`new_string`:
```
  - **April 1, 2020 – October 27, 2021:** Government of Canada Bond Purchase Program (GBPP) QE phase (the GBPP itself ran through April 2022 including the reinvestment phase below).
```

*Reason:* Reconciles the QE-phase-only labelling on line 133 with the broader "2020-2022 GBPP" usage on line 115; both reference the same BoC program, which had a QE phase and a reinvestment phase per the BoC's own taxonomy.
*Source:* https://www.bankofcanada.ca/markets/market-operations-liquidity-provision/market-operations-programs-and-facilities/government-canada-bond-purchase-program/ — BoC's own GBPP page describes the program as spanning both phases.
*Verification log change*: mark Defect 2 (GBPP scope ambiguity) with "(patch proposed 2026-05-09; awaiting user accept/reject)".

---

## Claim 3: $20-60B post-QT settlement-balance target (Gravelle, March 2024)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim, line 140)

> The post-QT steady-state target range is **$20–60B** (Deputy Governor Gravelle, [March 2024 speech](https://www.bankofcanada.ca/2024/03/going-back-normal-bank-canadas-balance-sheet/)).

### Verification verdict

**VERIFIED.**

### Source — Gravelle speech "Going back to normal" (March 21, 2024)

**URL:** https://www.bankofcanada.ca/2024/03/going-back-normal-bank-canadas-balance-sheet/

**Direct quotes (per WebFetch):**
- *"we expect settlement balances to land in a range of $20 billion to $60 billion."*
- *"A floor system makes it easier to keep that market rate close to our target rate."*
- *"we will be back to normal balance sheet management. That is, we will buy assets simply to match the amount of liabilities on our balance sheet."*
- *"Right now, we have roughly $100 billion in settlement balances."*

**Verdict:** VERIFIED. Speech, speaker, date, and target range all align with the framework's citation.

### Defects flagged

None on this specific claim. The framework's parenthetical citation is accurate. The "current level relative to the $20–60B target is the relevant read" framing is the analyst's; consistent with the source.

### Open questions

1. Framework cites Gravelle once (March 2024) — has there been a more recent BoC speech that updates or reaffirms the band? Worth a check before next update cycle.

---

## Claim 4: Floor system permanent since April 2022

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim, line 140)

> The BoC adopted the floor system as its **permanent operating regime in [April 2022](https://www.bankofcanada.ca/2022/04/bank-of-canada-provides-operational-details-for-quantitative-tightening-and-announces-that-it-will-continue-to-implement-monetary-policy-using-a-floor-system/)** ("the floor system will remain in place even after QT has run its course").

### Verification verdict

**VERIFIED.**

### Source — BoC "Operational details for quantitative tightening" announcement (April 13, 2022)

**URL:** https://www.bankofcanada.ca/2022/04/bank-of-canada-provides-operational-details-for-quantitative-tightening-and-announces-that-it-will-continue-to-implement-monetary-policy-using-a-floor-system/

**Direct quote (per WebFetch):** *"The floor system will remain in place even after quantitative tightening has run its course and the balance sheet has diminished in size to the point where the Bank needs to start acquiring assets again for normal balance sheet management purposes."*

**Verdict:** VERIFIED. Framework's quoted language ("the floor system will remain in place even after QT has run its course") is verbatim from the source. The "permanent operating regime" framing is supported.

### Defects flagged

1. **Date precision:** Framework says "April 2022" (no day). The actual press release is dated April 13, 2022. Not a defect, but for consistency with the day-precise dates elsewhere in the timeline, could be tightened.

### Open questions

None.

### Proposed patches (mechanical only — judgment items deferred)

**Patch 1: Floor-system April 2022 date precision (tighten "April 2022" to "April 13, 2022" for consistency with day-precise dates elsewhere in the timeline)**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
- `boc_settlement_balances` level: the operating regime indicator. The BoC adopted the floor system as its **permanent operating regime in [April 2022](https://www.bankofcanada.ca/2022/04/bank-of-canada-provides-operational-details-for-quantitative-tightening-and-announces-that-it-will-continue-to-implement-monetary-policy-using-a-floor-system/)** ("the floor system will remain in place even after QT has run its course").
```

`new_string`:
```
- `boc_settlement_balances` level: the operating regime indicator. The BoC adopted the floor system as its **permanent operating regime on [April 13, 2022](https://www.bankofcanada.ca/2022/04/bank-of-canada-provides-operational-details-for-quantitative-tightening-and-announces-that-it-will-continue-to-implement-monetary-policy-using-a-floor-system/)** ("the floor system will remain in place even after QT has run its course").
```

*Reason:* Day-precise dates appear throughout the surrounding timeline (April 1 2020, October 27 2021, April 25 2022, January 29 2025, March 5 2025); aligning April 2022 to April 13 2022 closes the precision gap.
*Source:* https://www.bankofcanada.ca/2022/04/bank-of-canada-provides-operational-details-for-quantitative-tightening-and-announces-that-it-will-continue-to-implement-monetary-policy-using-a-floor-system/ — press release is dated April 13, 2022.
*Verification log change*: mark Defect 1 (date precision) with "(patch proposed 2026-05-09; awaiting user accept/reject)".

**Patch 2: Same date precision in line 150 thresholds banner**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
- **Floor system permanent since April 2022; QT ran April 25, 2022 – January 29, 2025**
```

`new_string`:
```
- **Floor system permanent since April 13, 2022; QT ran April 25, 2022 – January 29, 2025**
```

*Reason:* Same date-precision tightening; the threshold banner already uses day-precise dates for the QT window, so April 2022 should match.
*Source:* https://www.bankofcanada.ca/2022/04/bank-of-canada-provides-operational-details-for-quantitative-tightening-and-announces-that-it-will-continue-to-implement-monetary-policy-using-a-floor-system/ — press release is dated April 13, 2022.
*Verification log change*: same — mark Defect 1 with "(patch proposed 2026-05-09; awaiting user accept/reject)".

---

## Claim 5: bocfed_spread empirical-distribution thresholds since 1996

### Provenance tier

**Tier 3 — resolved 2026-05-09 via convention adoption.** The 2026-05-09 audit surfaced a critical defect (framework prose claimed median |spread| 38bp; project data gives 62.5bp at monthly resolution; the 38bp value reproduces only at daily 2009+ resolution — silent methodology drift). User decided to address the underlying problem at the framework level by introducing `markdown-files/distribution_conventions.md` (a five-tier ladder typical/uncommon/pronounced/rare/extreme at central 50/80/95/99% boundaries, with mandatory tail-axis + window/resolution/N citation), and applied it to bocfed_spread as the worked example. The mechanical patches drafted below (Patches 1-4, dated 2026-05-09) are SUPERSEDED by the convention application — bocfed_spread thresholds are now retuned to P50=62.5bp / P80=100.0bp / P95=187.5bp / P99=231.0bp at monthly month-start resolution since 1996, documented in `analysis_framework.md` line ~114, line ~144, and `analyze.py` `_classify_bocfed` (line ~200) and the line ~589 banner. Source script: `analyses/bocfed_spread_distribution.py`. The 38bp daily-resolution baseline is documented in `analyses/bocfed_spread_38bp_test.md` for reference.

The historical Tier 2 audit details below are retained for the audit trail; the patch proposals are no longer applicable.

**Original Tier 2 status (superseded):** Autonomously verified 2026-05-09. Not user-reviewed.

### Framework prose (verbatim, line 114)

> Empirical distribution since 1996 (median |spread| 38bp): **±50bp = notable** (top half); **±100bp = unusual** (top 10%, flag prominently); **±150bp = rare** (top 5%, reserved for cycle-defining episodes — 1995–98, late-2024-onward).

### Verification verdict

**CONTESTED — empirical distribution as computed from project data does not match the framework's stated thresholds.** This is a critical defect.

### Source — Project data (`data/overnight_rate.csv` × `data/fed_funds.csv`)

**Methodology:** Monthly overnight rate (1996-01 onwards) joined to monthly fed_funds, |spread| computed in basis points. N=364, range 1996-01 to 2026-04. (Both series are monthly at the resolution available in the project — daily overnight only starts 2009-04-21, so a 1996-onward distribution must use the monthly resolution.)

**Computed values:**
- Median |spread|: **62.5 bp** (framework claims 38 bp — off by 65%)
- Mean |spread|: 71.4 bp
- |spread| ≤ 50 bp: 41.8% within (so ±50bp marks roughly **top 58%, not "top half"**)
- |spread| ≤ 100 bp: 82.1% within (so ±100bp marks **top 18%, not "top 10%"**)
- |spread| ≤ 150 bp: 89.8% within (so ±150bp marks **top 10%, not "top 5%"**)
- 90th percentile of |spread|: ~150 bp
- 95th percentile of |spread|: ~187 bp

**Verdict:** CONTESTED. Three of the four numerical anchors in the framework's bocfed_spread distribution claim are materially incorrect:

| Framework claim | Computed reality | Defect |
|---|---|---|
| Median |spread| 38 bp | 62.5 bp | Off by ~25bp / 65% |
| ±50bp = top half | top 58% | Roughly directionally OK — close to "around half" |
| ±100bp = top 10% | top 18% | Off — should be ~150bp for top 10% |
| ±150bp = top 5% | top 10% | Off — should be ~190bp for top 5% |

The tier ladder (notable / unusual / rare) is roughly correct in spirit but the *thresholds* should shift up by ~50 bp to actually match a "top 10% / top 5%" classification:
- ±100bp = unusual (top ~18%, not top 10%) — should be **~150bp = top 10%**
- ±150bp = rare (top ~10%, not top 5%) — should be **~190bp = top 5%**

### Cross-check — `_classify_bocfed` thresholds in `analyze.py`

`analyze.py` line 581 banner says: `(typ <+/-0.5pp; notable >=+/-0.5pp; unusual >=+/-1.0pp; rare >=+/-1.5pp)`. This matches the framework's stated thresholds, so the *code* and the *framework* agree with each other — but **both disagree with the data they purport to summarize**. The "verified May 2026" banner in line 90 of the framework explicitly claims "BoC-Fed spread tiers" were verified empirically; this audit could not reproduce that verification.

### Defects flagged

1. **CRITICAL: Threshold-vs-data mismatch.** The numerical claims (median 38bp; ±50/100/150bp = top 50%/10%/5%) do not match the empirical distribution at monthly resolution. Either the framework's percentile claims are wrong, or the methodology used to compute them differs from the natural one and is not documented. **This is exactly the failure mode (threshold values asserted without primary-source backing) the audit was tasked to find.**
2. **Methodology not documented.** Framework asserts thresholds empirically but does not document the data resolution, alignment method, or window. Code in `analyze.py` does not contain a percentile-computation script. Without methodology, the claim cannot be replicated or cross-checked — fails the project's "verification, not speculation" rule.
3. **Possible alternative explanations the user should weigh:**
   - The original computation used a different period (e.g., 1996-2024 ending before recent Fed-BoC divergence widened the distribution).
   - The original computation used target-rate change windows rather than month-end snapshots.
   - The original computation excluded the 2008-2009 crisis period or the 2020-2022 COVID period.
   - The framework's "since 1996" anchor is aspirational, and the actual thresholds were calibrated against a shorter / different window that wasn't documented.

None of these alternatives are documented in `analysis_framework.md` or the verification log.

### Open questions for user review

1. **What window / resolution / alignment was originally used to compute the bocfed_spread thresholds?** Without that, this audit cannot reconcile the framework's numbers with the data.
2. **If the empirical thresholds need updating to ~150bp = top 10%, ~190bp = top 5%, recompute the tier banner in `analyze.py` and the framework prose together.** The framework's late-2024-onward "rare" episode characterization may also need revisiting — under the corrected thresholds, was 2024-onward actually "rare" or merely "unusual"?

### Proposed patches (mechanical only — judgment items deferred)

These patches correct the **fact errors** (the median value and the percentile labels) at the existing ±50/100/150 anchors, *without* shifting the anchors themselves. Whether to retune the anchors to ~150bp/~190bp so the "top 10% / top 5%" language reattaches cleanly is a JUDGMENT call deferred to the user.

**Patch 1: Correct median and percentile labels in the framework's per-spread paragraph (line 114)**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
- BoC−Fed spread (`bocfed_spread`): level and direction. Negative spread (BoC below Fed) is broadly CAD-negative; positive supports CAD. Empirical distribution since 1996 (median |spread| 38bp): **±50bp = notable** (top half); **±100bp = unusual** (top 10%, flag prominently); **±150bp = rare** (top 5%, reserved for cycle-defining episodes — 1995–98, late-2024-onward).
```

`new_string`:
```
- BoC−Fed spread (`bocfed_spread`): level and direction. Negative spread (BoC below Fed) is broadly CAD-negative; positive supports CAD. Empirical distribution since 1996 (median |spread| 62.5bp, monthly resolution): **±50bp = notable** (top ~58%); **±100bp = unusual** (top ~18%, flag prominently); **±150bp = rare** (top ~10%, reserved for cycle-defining episodes — 1996–98, late-2024-onward).
```

*Reason:* The cited percentile labels ("top half", "top 10%", "top 5%") are factually wrong against the project data and the median value (38bp) is wrong by ~25bp. Correcting both leaves the tier ladder (notable / unusual / rare) intact and lets the user separately decide whether to shift the threshold anchors so the percentile language reattaches at "top 10% / top 5%". 1995-98 is also tightened to 1996-98 to match the data window.
*Source:* Project data — `data/overnight_rate.csv` × `data/fed_funds.csv`, monthly N=364, 1996-01 to 2026-04. Quoted directly from this verification log: median |spread| 62.5 bp; |spread| ≤ 50 bp = 41.8% (so ±50bp = top 58%); |spread| ≤ 100 bp = 82.1% (so ±100bp = top 18%); |spread| ≤ 150 bp = 89.8% (so ±150bp = top 10%).
*Verification log change*: mark Defect 1 (CRITICAL: Threshold-vs-data mismatch) with "(partial mechanical patch proposed 2026-05-09 — corrects median and percentile labels; threshold-anchor shift deferred as judgment; awaiting user accept/reject)".

**Patch 2: Correct percentile labels in the line-144 threshold banner**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
- **`bocfed_spread`:** ±50bp notable; ±100bp unusual (top 10% of observations since 1996); ±150bp rare (top 5%)
```

`new_string`:
```
- **`bocfed_spread`:** ±50bp notable (top ~58%); ±100bp unusual (top ~18% of observations since 1996, monthly resolution); ±150bp rare (top ~10%)
```

*Reason:* Same factual correction as Patch 1; the threshold banner duplicates the percentile labels and must move in lockstep.
*Source:* Same project-data computation as Patch 1.
*Verification log change*: same — mark Defect 1 (CRITICAL) with the partial-mechanical-patch note.

**Patch 3 (code patch): Remove the "verified May 2026" claim from the line-90 status banner where it covers `bocfed_spread`**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
> **VERIFICATION STATUS: verified end-to-end (May 2026).** Every analytical claim audited against BoC primary sources (r* update, floor system announcement, settlement-balance target, QT operational timeline) and empirical distributions (BoC-Fed spread tiers, Canada 2Y-overnight tiers, correlation with `bocfed_spread`); 2Y term-premium magnitudes and regime distortions sourced from BoC ACM literature; balance-sheet anchors (~$120B baseline, ~$575B March 2021 peak) verified directly from `boc_total_assets`. Compute and format functions in `analyze.py`; blurb in `data/blurbs.json` under `policy`.
```

`new_string`:
```
> **VERIFICATION STATUS: Tier 2 audit 2026-05-09 — not user-reviewed.** Most BoC primary-source claims (r* update, floor system announcement, settlement-balance target, QT operational timeline) and the Canada 2Y-overnight empirical distribution and the bocfed-vs-can_us_2y correlation reproduce against project data. **Open defects** (see `markdown-files/verification/policy.md`): bocfed_spread tier percentile labels do not match project data; 2Y term-premium magnitudes (0–40 bp / 20–60 bp) not surfaced by the cited Financial Stability Indicators page; the 3×2 conditional grid for `can2y_overnight_spread × action_state` is analyst synthesis presented as canonical. Balance-sheet anchors (~$120B baseline, ~$575B March 2021 peak) verified directly from `boc_total_assets`. Compute and format functions in `analyze.py`; blurb in `data/blurbs.json` under `policy`.
```

*Reason:* The line-90 banner asserts "verified end-to-end" coverage that the audit could not reproduce for at least Claims 5, 7, 10, and 11. Replacing it with a Tier-2-with-defects banner is a mechanical fix (the existing banner's specific claim is contradicted by the verification log itself). This also brings the banner in line with the tier glossary in `_tiers.md`.
*Source:* This verification log file — `markdown-files/verification/policy.md`, lines 7 and 562, plus the per-claim audit findings.
*Verification log change*: mark this as part of the same partial-mechanical-patch tracking note (Patches 1-3 hang together).

**Patch 4 (code patch): Update the `bocfed_spread` tier banner in `analyze.py` line ~581 to mark percentile labels as approximate**

*Code patch* — File: `analyze.py`, approximate line: `~581`.

`old_string`:
```
BoC - Fed spread:                {v['bocfed_spread']:+.2f}pp   tier: {v['bocfed_tier']}  (typ <+/-0.5pp; notable >=+/-0.5pp; unusual >=+/-1.0pp; rare >=+/-1.5pp)
```

`new_string`:
```
BoC - Fed spread:                {v['bocfed_spread']:+.2f}pp   tier: {v['bocfed_tier']}  (typ <+/-0.5pp; notable >=+/-0.5pp ~top 58%; unusual >=+/-1.0pp ~top 18%; rare >=+/-1.5pp ~top 10%; monthly 1996-onward)
```

*Reason:* The tier-classification anchors (`_classify_bocfed`) themselves are not changed in this mechanical pass; only the descriptive percentile labels in the banner are corrected to match the data. Whether to shift the underlying anchors so the labels round to top-10% / top-5% is the judgment call deferred to the user.
*Source:* Same project-data computation as Patch 1 — `data/overnight_rate.csv` × `data/fed_funds.csv`, monthly 1996-01 to 2026-04.
*Verification log change*: mark Cross-check note "Code (`analyze.py`) and prose agree with each other but disagree with data" with "(partial mechanical patch proposed 2026-05-09 — banner percentile labels updated; anchor-shift deferred; awaiting user accept/reject)".

---

## Claim 6: can2y_overnight_spread empirical-distribution thresholds since 2001

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim, line 115)

> Empirical distribution since 2001 (median |spread| 30bp): **within ±25bp = near-zero** (44%, market broadly aligned with current stance, no clear directional story); **±50bp = notable** (top third); **±100bp = unusual** (top 10%).

### Verification verdict

**VERIFIED.** Computed from project data, all four numerical claims line up.

### Source — Project data (`data/yield_2yr.csv` × `data/overnight_rate_daily.csv`/`overnight_rate.csv`)

**Methodology:** Daily Canada 2Y yield (2001-01 onwards) joined to overnight rate (daily where available, forward-filled monthly elsewhere). N=6,338 daily observations, range 2001-01-02 to 2026-05-07. |spread| computed in basis points.

**Computed values:**
- Median |spread|: **30.0 bp** (matches framework's 30bp exactly)
- |spread| ≤ 25 bp: **44.9% within** (matches framework's 44% near-zero)
- |spread| ≤ 50 bp: 64.9% within (so ±50bp marks **top 35%, framework says "top third"** — close enough)
- |spread| ≤ 100 bp: 89.8% within (so ±100bp marks **top 10.2%**, matches framework's "top 10%")

**Verdict:** VERIFIED. The empirical distribution claims for `can2y_overnight_spread` are accurate at daily resolution since 2001-01-02.

### Defects flagged

None on the numerical thresholds themselves. The methodology, however, remains undocumented in framework prose — the user should still be able to verify these without re-deriving the methodology from scratch.

### Open questions

1. Should the methodology (daily resolution; overnight forward-filled from monthly pre-2009) be documented in framework prose or in this verification log?

---

## Claim 7: 2Y term premium ranges (0-40 bp normal regimes 2003-2019; 20-60 bp post-2023)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim, line 115)

> The 2Y embeds a term premium — BoC ACM-model estimates suggest roughly 0–40 bp in normal regimes (2003–2019) and 20–60 bp in the elevated post-2023 regime (see BoC's [Financial Stability Indicators](https://www.bankofcanada.ca/rates/indicators/financial-stability-indicators/) for the published decomposition).

### Verification verdict

**CONTESTED — citations do not directly support the specific 2Y bp ranges asserted.**

### Source 1 — Financial Stability Indicators page (cited in framework)

**URL:** https://www.bankofcanada.ca/rates/indicators/financial-stability-indicators/

**Key finding (per WebFetch):** *"The Canadian version of the Adrian, Crump and Moench model uses information from the yield curve to decompose bond yields into expected future short-term interest rates and a term premium."*

The page **describes** the methodology but **does not publish specific 2-year term-premium values, ranges, or magnitudes** in the content captured. The page references the methodology and points to downloadable data but the WebFetch retrieval did not surface a published 2Y bp range that maps to "0-40 bp" or "20-60 bp" by regime.

### Source 2 — BoC "The rise in the Canadian term premium in a global context" (March 2026)

**URL:** https://www.bankofcanada.ca/2026/03/sparks-at-bank-article-2026-9/

**Key finding (per WebFetch):** *"the term premium has increased since 2023 and is now at levels not seen in over a decade."* But this article focuses on the **10-year** Government of Canada bond term premium, NOT the 2-year. No specific basis-point ranges for the 2-year term premium were retrieved; no 2003-2019 vs. post-2023 numerical comparison was found at 2Y resolution.

**Verdict:** PARTIALLY VERIFIED that the term premium has risen post-2023 in directional terms; **NOT VERIFIED** that the magnitudes are "0-40 bp" pre-2019 and "20-60 bp" post-2023 at the 2-year tenor. The framework cites the Financial Stability Indicators page as backing for both ranges; the page description does not include the numerical anchors as specified.

### Defects flagged

1. **CRITICAL: Specific basis-point ranges (0-40 bp / 20-60 bp) for the 2Y term premium are not surfaced by the cited source.** This is the failure mode "threshold values asserted without primary-source backing." The directional claim (term premium has risen post-2023) IS verified; the magnitudes are not.
2. **Tenor mismatch in cited evidence.** The BoC's published material on the recent term-premium rise (Sparks at the Bank article, March 2026) discusses the 10Y, not the 2Y. The framework asserts 2Y values, which are different in magnitude.
3. **Possible underlying issue:** The framework's specific bp ranges may have been computed from BoC ACM data files (the FSI page links to downloadable data), but the methodology / source file is not documented in framework prose.

### Open questions for user review

1. **Are the 0-40 bp and 20-60 bp ranges sourced from BoC-published 2Y ACM data, or from a calculation against the FSI downloads?** If the latter, document the methodology and dataset path. If the framework cannot point to an authoritative published source for these specific 2Y bp ranges, soften to directional language ("modest pre-2019, elevated post-2023") or remove the numerical bands.
2. **GBPP "~20 bp below OIS-equivalent through scarcity" claim** (framework line 115): not backed by SDP 2024-5 (the most relevant BoC paper on GBPP yield impact). SDP 2024-5 reports announcement-window cumulative yield changes (15bp 2Y, 11bp 5Y, 11bp 10Y) using event-study methodology, not a scarcity-vs-OIS framing. Either re-attribute or soften.

---

## Claim 8: Pre-COVID balance-sheet baseline ~$120B; peak QE ~$575B March 2021

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim, line 138)

> Distance from anchors: pre-COVID baseline of total assets was **~$120B** (early 2020; max $121.5B in early Feb 2020, verified from data); peak QE was **~$575B in March 2021** ($575.4B on 2021-03-10, verified from data — note this is March 2021, not April 2022 as sometimes loosely characterized; April 2022 is when QT *started*).

### Verification verdict

**VERIFIED.** Both anchors are exactly correct against `data/boc_total_assets.csv`.

### Source — `data/boc_total_assets.csv`

**Computed values (Pandas, weekly series):**
- Pre-COVID (Jan-Feb 2020) max: **$121.543B on 2020-02-26** — matches framework's $121.5B
- Peak (2021-01 to 2021-06): **$575.36B on 2021-03-10** — matches framework's $575.4B exactly
- All-time max in series: $575.36B on 2021-03-10 — confirms peak QE date

**Verdict:** VERIFIED.

### Defects flagged

None. This is the cleanest-verified empirical claim in the section. The framework even calls out a common misattribution ("not April 2022 as sometimes loosely characterized; April 2022 is when QT *started*"), which is correct and useful.

---

## Claim 9: 0.88 correlation between bocfed_spread and can_us_2y_spread since 2001

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim, line 127)

> Empirically correlated with `bocfed_spread` at **0.88 since 2001**, so the two should usually move together.

### Verification verdict

**VERIFIED.**

### Source — Project data (`data/overnight_rate.csv` × `data/fed_funds.csv` × `data/yield_2yr.csv` × `data/us_2yr.csv`)

**Methodology:** Monthly aligned series since 2001-01. bocfed_spread = overnight - fed_funds; can_us_2y_spread = Canada 2Y - US 2Y. Pearson correlation.

**Computed values:**
- Monthly correlation since 2001: **0.883** (matches framework 0.88)
- Daily correlation since 2001 (with forward-filled monthly anchors): **0.894**

**Verdict:** VERIFIED. The framework's "0.88 since 2001" rounds correctly at monthly resolution.

### Defects flagged

None. Methodology is undocumented in framework prose but the result reproduces.

### Open questions

1. Document monthly vs. daily resolution choice for the correlation in framework prose or this log? Both round to 0.88 / 0.89.

---

## Claim 10: Conditional table for can2y_overnight_spread × action_state

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim, lines 116-124)

> **Direction of `can2y_overnight_spread` drift — interpretation depends on the BoC's `action_state`.** Track both a 4-week window (tactical repricing around meetings) and a 12-week window (trend confirmation); the signal is strongest when both agree. The same drift means very different things based on what the BoC has been doing:
>
> | BoC `action_state` | Hawkish drift (spread rising) means | Dovish drift (spread falling) means |
> |---|---|---|
> | Active *cutting* cycle | Market doubting more cuts will happen | Market expects deeper cuts than already priced |
> | *On hold* | Market starting to price *hike* risk | Market starting to price resumption of cuts |
> | Active *hiking* cycle | Market expects more hikes | Market doubting more hikes will happen |
>
> **Always frame the read as "market vs. Bank's current stance,"** never as if the cycle is always cutting.

### Verification verdict

**UNSOURCED — analyst synthesis.** This is the same failure mode flagged in labour Claim 2 (rigid n×n decoder presented as canonical when the source is silent).

### Source check

WebSearch for BoC publications mapping spread direction × action state to interpretive labels: no result. The BoC publishes neither (a) this 3×2 grid as a canonical decoder, nor (b) the underlying "interpret market expectations relative to Bank's stance" rule as a named heuristic.

The underlying logic ("a hawkish drift in 2Y vs. overnight means different things depending on whether the BoC is cutting, holding, or hiking") is sound finance reasoning — directionally analogous to the standard read of OIS-vs-policy spreads in any central-bank context. But the specific 3×2 grid is the analyst's own synthesis. **It is the same construct class as the 2×2 decoder in labour Claim 2** — the user explicitly flagged that pattern as a failure mode.

### Defects flagged

1. **Rigid n×2 decoder presented as canonical when it is analyst synthesis.** The 3×2 grid maps `action_state` × `drift_direction` to six labelled interpretations. While the underlying economics is reasonable, the specific mapping is the analyst's own framing, not a BoC publication. Framework should label as analyst synthesis.
2. **Same combinatorial-incompleteness risk as labour Claim 2.** Six combinations (3×2). Edge cases:
   - What if `action_state` = "on hold" but the prior cycle was cutting and ended very recently — should "hawkish drift = pricing hike risk" hold, or should the recency of the cut cycle attenuate it?
   - What if spread is *flat* (no drift)? The grid has no "no-drift" cell.
   - What if drift is large enough that the level interpretation dominates the directional one (e.g., drift moves spread from -100bp to -50bp during a cutting cycle — the market is still pricing cuts, just fewer)?
   - What if drift is in the same direction in both windows but at sharply different magnitudes? Grid treats "agreement" as binary.
3. **Recommendation** (parallel to labour Claim 2's revision): retain the underlying analytical move ("interpret drift relative to current stance, not in absolute terms") as a paragraph framing; demote the 3×2 grid to a "sample interpretive frame for the typical case" with explicit labelling that edge cases break the grid. This is more conservative and matches the precedent set in labour.

### Open questions for user review

1. **Demote the grid to non-canonical sample-frame status** (analogous to labour Claim 2's revision)?
2. Is the "4-week + 12-week window agreement" rule analyst synthesis or sourced? It is presented as definitive; no source is given. If analyst synthesis, mark as such.

---

## Claim 11: bocfed_spread tier interpretation language ("notable / unusual / rare")

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim, line 114, plus tier banner from `analyze.py`)

Framework: *"±50bp = notable (top half); ±100bp = unusual (top 10%, flag prominently); ±150bp = rare (top 5%, reserved for cycle-defining episodes — 1995–98, late-2024-onward)."*

`analyze.py` line 581: *"(typ <+/-0.5pp; notable >=+/-0.5pp; unusual >=+/-1.0pp; rare >=+/-1.5pp)"*.

### Verification verdict

**CONTESTED — internal-consistency and data-distribution mismatch.** See Claim 5 above for full empirical distribution. Framework prose, code-banner language, and project data do not all agree.

### Defects flagged

1. **Code and framework prose agree with each other but not with the data.** As shown in Claim 5, the framework's percentile claims do not reproduce against `data/overnight_rate.csv` × `data/fed_funds.csv`. The propagation defect is identical in code and prose, suggesting both were written from the same un-documented source and not separately re-verified.
2. **"1995-98, late-2024-onward" historical anchor for the rare tier:** The data starts 1996-01 (the first overlapping month with both series), so "1995-98" is loose terminology — actual coverage is 1996-98. Minor.
3. **Late-2024-onward characterization may need recalibration.** Under the corrected thresholds (±150bp = top 10%, not top 5%), late-2024-onward may be "unusual" rather than "rare." Worth re-classifying.

### Open questions

1. Same as Claim 5: what was the original methodology for these thresholds, and should they be recomputed and updated in both prose and code?

### Proposed patches (mechanical only — judgment items deferred)

**Patch 1: "1995–98" historical anchor → "1996–98" (data starts 1996-01, so 1995 is not in the underlying series)**

This patch is **already folded into Claim 5 Patch 1** above (the 1995-98 → 1996-98 change is part of the same line-114 edit that corrects the median and percentile labels). Recording it here as Claim 11's mechanical defect for traceability — accepting Claim 5 Patch 1 also resolves this defect.

*Verification log change*: mark Defect 2 ("1995-98 historical anchor") with "(patch proposed 2026-05-09 via Claim 5 Patch 1; awaiting user accept/reject)".

The other Claim 11 defects (code-and-prose-disagree-with-data; late-2024 recharacterization) are addressed by Claim 5's patches and Claim 5's deferred judgment items respectively.

---

## Claim 12: Pre-COVID emergency-facility benchmark ($120B → $385B in 6-7 weeks)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim, line 139)

> Canonical benchmark: March–June 2020, total assets jumped from ~$120B to ~$385B in 6–7 weeks via CTRF-style term repos (~$140B), the Fed USD swap line, and various market-functioning programs.

### Verification verdict

**PARTIALLY VERIFIED.** The headline numbers (~$120B → ~$385B) are reproducible against `boc_total_assets.csv`. The component decomposition (CTRF ~$140B specifically) was not verified against a primary source in this audit pass and should be checked.

### Source — `data/boc_total_assets.csv`

Pre-COVID baseline ~$120B verified in Claim 8. Peak around mid-2020 in the data:

(spot-check: framework asserts $385B in 6-7 weeks from late Feb 2020. Need to confirm the timing precisely. Per the BoC's emergency facility timeline, the COVID-response peak balance occurred roughly mid-May 2020 before falling back ahead of QE-driven re-expansion.)

**Verdict:** PARTIALLY VERIFIED — headline numbers plausible against data but the "$140B CTRF" component and the "6-7 weeks" duration claim were not fully verified against primary sources in this pass.

### Defects flagged

1. **CTRF $140B figure unverified.** The framework asserts a specific component magnitude that should have a primary-source citation (e.g., a BoC operational details release or weekly market notice). PENDING verification.

### Open questions

1. Source for "CTRF ~$140B" component — needs primary citation.
2. Verify the "6-7 weeks" timing window precisely against the data (the speed of the Mar-Apr 2020 ramp-up).

---

## Cross-claim defects index (Tier 2 audit, Claims 1-12)

| # | Defect class | Where found | Severity |
|---|---|---|---|
| 1 | **Threshold-vs-data mismatch (CRITICAL)** | Claim 5: bocfed_spread median 38bp / ±50/100/150bp tiers do not match project data (actual median 62.5bp; ±100bp = top 18% not top 10%; ±150bp = top 10% not top 5%). Code (`analyze.py`) and prose agree with each other but disagree with data. | **CRITICAL** |
| 2 | **Threshold values asserted without primary-source backing** | Claim 7: "0-40 bp normal regimes / 20-60 bp post-2023" 2Y term-premium ranges. Cited Financial Stability Indicators page describes ACM methodology but does not publish these specific 2Y bp ranges; cited Sparks-at-the-Bank article discusses the 10Y, not 2Y. | **CRITICAL** |
| 3 | **Rigid n×n decoder presented as canonical when it is analyst synthesis** | Claim 10: 3×2 grid for can2y_overnight_spread × action_state. Same failure mode the user identified in labour Claim 2's 2×2 decoder. | **high** |
| 4 | **Internal-consistency mismatch** | Claim 11: framework prose, `analyze.py` tier-banner code comment, and project data are mutually inconsistent (prose and code agree; data disagrees with both). | **high** (subset of #1) |
| 5 | **Mis-attributed source / claim not in cited paper** | Claim 7: "GBPP suppressed 2Y GoC ~20 bp below OIS-equivalent through scarcity" — SDP 2024-5 (the most relevant BoC paper on GBPP impact) reports event-study announcement-window changes, not OIS-equivalent scarcity-effect framing. | **medium-high** |
| 6 | **Date-boundary inconsistency** | Claim 2: Oct 27 2021 (announcement) vs. Apr 25 2022 (operational). Framework picks operational date for QT start but announcement date for reinvestment start. Reinvestment effective date was Nov 1 2021. | **medium** |
| 7 | **Methodology not documented** | Claims 5, 6, 9: empirical-distribution and correlation claims have no methodology paragraph. Without methodology, claims cannot be replicated — fails the "verification, not speculation" rule. | **medium** |
| 8 | **Component figure unverified** | Claim 12: "CTRF ~$140B" component magnitude has no primary-source citation. | **medium** |
| 9 | **Mild framing tension** | Claim 1: "BoC frames this as a range, not a midpoint" elides the fact that BoC projections operationalise the midpoint. | **low** |
| 10 | **Date precision** | Claim 4: "April 2022" should be "April 13, 2022" for consistency with day-precision elsewhere. | **low** |
| 11 | **Operation-size band unverified** | Claim 2: "$2-5B per operation" for term repos — verified bi-weekly cadence but not the size band. | **low (PENDING)** |

### Failure-mode pattern analysis

The audit task brief flagged five failure modes. Coverage in this section:

1. **Fabricated quotes attributed to real BoC speakers / publications.** **NONE FOUND** in the Monetary Policy section. The Macklem-style quotes in this section that were checked (Gravelle "settlement balances $20-60B", April 2022 floor system "remain in place even after QT", end-of-QT January 2025) all reproduced exactly. This is a meaningful contrast with labour Claim 1's two fabrications.

2. **US-economic heuristics transferred to Canada without empirical recalibration.** **NONE FOUND** at the level seen in labour (V/U > 1 = tight). The framework explicitly Canadianizes its empirical distributions (1996-onward bocfed; 2001-onward can2y_overnight). The bocfed_spread numerical errors in Claim 5 are calibration mistakes, not transfer defects.

3. **Threshold values asserted without primary-source backing.** **TWO FOUND** — the most prominent are Claim 5 (bocfed_spread tiers — values disagree with data) and Claim 7 (2Y term-premium bp ranges — not surfaced by the cited source). The framework's status-banner claim of "verified end-to-end" cannot be reconciled with these.

4. **Naming un-fetched indicators in framework prose.** **NONE FOUND.** All indicators named in the prose are present in `data/`. Distinct from labour Claim 9's "involuntary PT / avg hours" naming-leak.

5. **Rigid n×n decoders presented as canonical when they're analyst synthesis.** **ONE FOUND** — Claim 10's 3×2 grid for spread-drift × action_state. The framework explicitly notes the underlying logic is the analyst's framing ("Always frame the read as 'market vs. Bank's current stance'"), but the rigid grid is presented as definitive. Same construct class as labour's 2×2 decoder.

### Top three defects (for caller)

1. **bocfed_spread tier thresholds disagree with project data.** Median |spread| is 62.5bp (framework: 38bp); ±100bp is top 18% (framework: top 10%); ±150bp is top 10% (framework: top 5%). Code-banner in `analyze.py` shares the same defect. Either methodology was different from the natural one and is not documented, or the thresholds need recalibration in both prose and code.

2. **2Y term premium "0-40 bp / 20-60 bp" ranges have no surfaced primary-source backing.** Cited Financial Stability Indicators page describes ACM methodology but does not publish the specific 2Y bp magnitudes; cited Sparks-at-the-Bank (March 2026) covers the 10Y, not 2Y. Same failure-mode class as labour's "1.6% real wage gains" fabricated-quote, but here the issue is mis-cited rather than fabricated.

3. **3×2 conditional grid for can2y_overnight_spread × action_state is analyst synthesis, presented as canonical.** Same construct class the user explicitly rejected in labour Claim 2 (the 2×2 decoder). Recommend demoting the grid to a sample interpretive frame and keeping the prose-level rule ("interpret drift relative to stance, never as if the cycle is always cutting") as the canonical guidance.

### Items needing immediate attention before the next blurb regen

- **Claim 5:** decide whether to recompute bocfed thresholds against data and update both `analysis_framework.md` line 114 / 144 and the `analyze.py` line 581 banner, or document the alternative methodology that justifies the original numbers.
- **Claim 7:** soften the 2Y term-premium bp ranges to directional language unless an authoritative published source can be located.
- **Claim 10:** label the 3×2 grid as analyst synthesis or demote to sample interpretive frame, parallel to labour Claim 2's revision.

The framework's line-90 "verified end-to-end (May 2026)" banner is **not currently accurate** for at least Claims 5, 7, 10, and 11; recommend revising the banner to reference this Tier-2 audit with specific defect items remaining open.
