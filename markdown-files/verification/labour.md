# Verification log: Labour Market section

Per-claim source log for the Labour section of `analysis_framework.md`. Each claim in the framework should appear here with: (a) the framework prose verbatim, (b) the primary source(s) that back it, (c) a direct quote from the source where possible, (d) a verification verdict, and (e) any analyst notes.

This file is **not** in CLAUDE.md's "First moves" auto-load list — it's a working log for claim-by-claim review, kept separate from the framework prose to avoid bloating session-init context. The framework itself carries inline citations; this log carries the page-level evidence chain.

**Verification verdict glossary:**

- **VERIFIED** — direct quote from a primary source supports the framework claim.
- **PARTIALLY VERIFIED** — primary source supports the substance but the framework's specific framing or numbers extend beyond the source.
- **CONTESTED** — primary sources disagree, or the BoC's position differs from broader analyst consensus.
- **UNSOURCED — analyst judgment** — the claim is the analyst's framing, not a direct primary-source claim. Should be marked as such in framework prose if kept.
- **PENDING** — not yet researched.

---

## Claim 1: Unemployment rate level and direction (estimated NAIRU ~6%)

### Verification verdict

REVISED 2026-05-09. Original framework text contained two fabricated quotes attributed to the BoC ("accelerationist Phillips curves are no longer in its main models" and "the NAIRU concept is not applicable to a wider set of labour market measures"). Neither could be located in any BoC primary source. Framework rewritten to drop the fabrications, anchor on a verified Macklem quote, and explicitly adopt a peer-institution NAIRU anchor (IMF) with the BoC's stance noted as caveat.

### Final framework text (post-revision)

> The dashboard tracks unemployment against an estimated NAIRU of about 6%, anchored to the IMF's July 2024 Article IV Consultation for Canada. NAIRU is a concept, not an observable — estimated, slow-moving, and uncertain at the decimal. The BoC itself does not publish a NAIRU; Governor Macklem (Nov 2022) characterised maximum sustainable employment as "not directly measurable... more of a concept than a number," and SAN 2025-17 (June 2025) operationalises labour-market state through a multi-indicator benchmark range rather than a single number. The dashboard adopts a peer-institution anchor because the concept remains analytically useful — OECD publishes NAIRU explicitly in annex tables, ECB uses it as a named input to staff wage Phillips curves, the US Fed uses the term with active hedging (Kugler Feb 2025). CIBC (Jan 2026) flags that post-pandemic NAIRU may have moved structurally higher per the 2022–2024 immigration surge's skill-mismatch effects.

### Source 1 — IMF Canada 2024 Article IV Consultation (July 16, 2024)

**URL:** https://www.imf.org/en/publications/cr/issues/2024/07/16/canada-2024-article-iv-consultation-press-release-and-staff-report-551903

**Direct quote:** *"The unemployment rate has risen to 6.2 percent, slightly above the NAIRU, estimated at 6 percent... unemployment is expected to continue rising slowly, peaking at 6.4 percent toward the middle of the year before normalizing at the estimated NAIRU of 6 percent."*

**Methodology note:** IMF uses a Phillips curve / output-gap framework for NAIRU estimation in Article IV consultations. The 6% figure is post-pandemic and incorporates conditions through mid-2024. Whether the immigration-surge skill-mismatch effects are fully captured is not transparent in the published methodology.

**Verdict:** VERIFIED — primary source supports the 6% anchor.

### Source 2 — BoC Governor Macklem speech, Nov 10, 2022

**URL:** https://www.bankofcanada.ca/2022/11/restoring-labour-market-balance-and-price-stability/

**Direct quote on why no point estimate:** *"Maximum sustainable employment is not directly measurable and is determined largely by non-monetary factors that can change through time."* Macklem describes maximum sustainable employment as *"more of a concept than a number"* and uses Beveridge curve framings rather than NAIRU-based unemployment-gap analysis.

**Verdict:** VERIFIED — supports the framework's "BoC does not publish a NAIRU" framing and the verified Macklem quote in the revised prose.

### Source 3 — BoC SAN 2025-17 (June 2025)

**URL:** https://www.bankofcanada.ca/2025/06/staff-analytical-note-2025-17/

**Key finding:** The note contains zero mention of NAIRU. The word does not appear. The methodology uses HP filter, modified Hamilton filter, and model-based potential-output estimates. The single Phillips curve mention is contextual ("a flatter wage Phillips curve... for minimum wage workers") and does not constitute a framework-wide repudiation.

**Verdict:** VERIFIED — supports "BoC operationalises through multi-indicator benchmark" framing. Original framework's "Bank explicitly states accelerationist Phillips curves are no longer in its main models" wording is NOT verified by this paper.

### Source 4 — CIBC Economics, Andrew Grantham (Jan 15, 2026)

**URL:** https://thoughtleadership.cibc.com/article/canadian-labour-market-could-we-really-run-out-of-room-before-year-end/

**Direct quote — pre-pandemic baseline:** *"Our prior study into a labour-market based output gap placed NAIRU at a bit below 6% prior just ahead of the pandemic."*

**Direct quote — post-pandemic:** *"NAIRU likely moved higher subsequently, as structural changes caused by the pandemic as well as a big surge in the population resulted in a weaker relationship between skills and job availability."*

**Direct quote — current stance:** *"In reality, we will only really know where NAIRU lies when we see it — when broad wage inflation starts to accelerate again."* Grantham notes the 2024–2025 immigration policy pivot toward more-employable permanent residents *"should help reduce structural unemployment and lower the NAIRU rate over time."*

**Verdict:** VERIFIED — supports the framework's CIBC caveat language. CIBC explicitly declines to give a post-pandemic point estimate, so the framework should not invent one.

### Other-institution usage (justification for keeping NAIRU as a tracked concept)

- **OECD (Economic Outlook Statistical Annex):** Publishes NAIRU explicitly per country. Latest publicly accessible Canadian figure (CEIC mirror): 6.243% (2022 vintage). December 2025 annex paywalled.
- **ECB (Economic Bulletin Jan 2025):** *"the unemployment gap (calculated as a difference between the actual unemployment rate and the NAIRU estimate in the Eurosystem / ECB Staff projections)"* — used in augmented wage Phillips curves.
- **US Fed (Governor Kugler, Feb 20 2025 speech):** *"NAIRU (non-accelerating inflation rate of unemployment), which is thought to be the normal level of unemployment absent cyclical forces"*; *"the weight on the unemployment gap in the Phillips curve for the more recent period is very small."* URL: https://www.federalreserve.gov/newsevents/speech/kugler20250220a.htm

### Canadian private-sector context

- **RBC, BMO, TD, Scotia, NBF, Desjardins:** No publicly accessible quantitative NAIRU estimates. Pivot to "breakeven employment" (RBC framing) or qualitative slack discussion. Verified by web survey 2026-05-09.

### Open follow-ups (not blocking this claim's verdict)

- Direct read of Pierre Fortin (UQAM), CLEF Working Paper 070-2024 (May 2024) on regional Beveridge curves — relevant Canadian academic content, PDF couldn't be parsed by the sub-agent. URL: https://clef.uwaterloo.ca/wp-content/uploads/2024/05/CLEF-070-2024-EN.pdf
- A future labour-deep-dive page could re-estimate Canadian NAIRU using post-2022 data (Beveridge-curve or Phillips-curve regression), giving the dashboard a self-grounded estimate rather than a borrowed one. The 2024–2025 immigration policy pullback should reduce structural distortion in the data over time, making a re-estimate increasingly tractable.

---

## Subsequent claims

To be added as we work through the framework:

- Claim 2: Utilization (employment rate + participation rate together)
- Claim 3: Tightness (vacancy rate 12M MA + V/U ratio + V/U as BoC's preferred composite + V/U threshold bands)
- Claim 4: Cost pressure (ULC Y/Y; LFS-Micro + ULC pairing; implied productivity ≈ 1% rule)
- Claim 5: Wage growth across measures (LFS-Micro vs raw LFS pattern)
- Claim 6: Wage growth vs ~3% soft threshold
- Claim 7: Wage growth vs services CPI (BoC framing vs older "margin absorption" shorthand)
- Claim 8: Real wages = wage Y/Y minus headline CPI Y/Y
- Claim 9: What this framework doesn't track (avg hours, involuntary PT, demographic decomposition, regional)

Plus the seven threshold bullets and the "What to surface" synthesis paragraph.
