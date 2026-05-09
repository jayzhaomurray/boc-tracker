# Blurb quality — open questions and trial log

*Working notes, last updated 2026-05-09. Kept here so the trial-and-error from the May 2026 testing session doesn't get lost.*

## The headline uncertainty

We don't yet know how to reliably get blurbs that are simultaneously good prose, good insight, and free of factual errors. The current pipeline (`compute_*_values` → framework prompt → blurb → self-review) produces competent output most of the time, but our attempts to measure marginal improvements have run into two methodological walls.

## What we tried during the May 2026 testing session

1. **Built `experiments/`**, a parallel testing harness that calls Claude via `claude --print` (Max subscription path) instead of the production Anthropic SDK path. Lets us A/B test framework changes, model swaps, and prompt-rule overrides against production data without touching `analyze.py`.

2. **Added an `obs_inf_rule` bullet to `analysis_framework.md` Output instructions** (commit `31ae5ae`). Rule: state direct observations as facts, hedge interpretive claims, forecasts forbidden. Motivated by an autonomous blurb draft that asserted unsupported facts (*"as employers slowed hiring and cut hours"*) without backing in the data.

3. **Ran a six-section A/B sweep**: baseline (current framework) vs `obs_inf_rule` (current framework + new rule). Both scored 6/6 on self-review. Subjective prose differences were small and not consistently in either direction.

4. **Ran a third sweep in `naive` mode** (no framework prose during generation, just task + data, but framework still used as the self-review rubric). Naive scored 4/6 — failures on labour and policy with substantive analytical errors. Naive *passes* on inflation and GDP arguably had richer prose than baseline did.

5. **Ran a baseline-vs-baseline noise check** (two draws of the same config + data). One draw of labour failed self-review with a sign error; the other passed. One draw of GDP failed with a magnitude error; the other passed. Same config, same data, different draws.

## Concrete blurb errors observed in testing

These are kept as a reference for what kinds of errors actually slip through, so a future session can recognise the patterns rather than rediscover them.

- **Baseline labour, probe run, sign error.** Wrote *"the 1.3pp gap below LFS-Micro"* — phrasing implies raw LFS is 1.3pp below LFS-Micro, but the actual relationship is LFS-Micro (2.60%) sitting 1.3pp *below* raw LFS (3.93%). Self-review caught it. A second baseline draw of the same data did not make this mistake.

- **Baseline GDP, probe run, magnitude error.** Wrote *"Consumption, investment, and government each added between 0.7 and 0.9pp."* Government was 0.66pp, outside that range. Self-review caught it. A second baseline draw of the same data did not make this claim at all.

- **Naive labour, interpretive error.** Applied the framework's *layoffs pattern* interpretation (employment falling while participation holds) to both the 3M and 12M timeframes. Participation was only stable over 3M. Over 12M, both employment and participation fell, which the framework labels as *slack opening on both margins*, not the *layoffs pattern* the blurb assigned to both windows.

- **Naive policy, three structural errors.** (a) Labelled the 69bp Canada-2Y-vs-overnight *spread* as *term premium*; the framework explicitly distinguishes the two (spread = market policy-path expectations + term premium combined). (b) Asserted *"the Fed continues to ease"*; the data shows only the Fed's current level, no ongoing-action signal — the inference was fabricated. (c) Captured the *no more cuts* half of the framework's hawkish-drift conditional but missed the framework's specific *BoC on hold + hawkish drift = market pricing hike risk* mapping.

## What we learned

**Variance dominates signal at n=1.** Within-config draw-to-draw variation produces failures and prose differences as wide as anything we'd attributed to rule changes. The labour-and-GDP probe runs that originally seemed to validate `obs_inf_rule` were almost certainly noise, not signal. Single-draw A/B comparisons cannot distinguish a rule's effect from stochastic model variation.

**The framework's authorship matters for what self-review actually measures.** Self-review uses the framework as the correctness rubric. Most of the framework prose was generated and verified autonomously — only inflation and policy were user-iterated. For autonomously-written sections, *"blurb fails self-review"* reduces to *"Claude-the-writer disagrees with Claude-the-framework-author."* That's a coherence measurement, not a quality measurement.

**The framework's load-bearing parts are the section-specific interpretive rules,** not the meta-style rules. The naive labour failure was a missed framework-specific decoder. The naive policy failures included a conceptual conflation (spread vs term premium) that the framework explicitly draws apart. For sections where the data narrates itself (inflation, GDP), naive sometimes produced richer prose than framework-mode did.

**The pipeline reads as competent but we cannot yet measure marginal improvements.** The infrastructure works; the methodology needs more.

## Status of the `obs_inf_rule`

**Kept for now**, with the explicit understanding that we have no evidence it improves blurb quality. Reverting later is on the table. Reasons to keep: the principle (distinguish observation from inference) is sound writing advice independent of empirical measurement. Reasons to revert: every line in the framework prose distorts model attention, and carrying rules we can't validate is net-negative under uncertainty.

## What we'd need to test this rigorously

- **Multi-draw experiments.** 5+ independent draws per (config, section) so failure rates are estimable rather than single coin flips. Probably needs an `--n-draws` flag in `experiments/run.py`.
- **User-verified frameworks for all six sections.** The four currently-autonomous sections (GDP, labour, housing, financial) need user iteration before self-review verdicts on those sections are trustworthy.
- **Or: substitute user-judgment for self-review on prose quality.** Let the user read blurbs and judge directly, bypassing the framework-as-rubric circularity. Slower but unbiased.

## Open questions

- Is the framework over-constraining for sections where the data narrates itself? Could lighter framework prose for inflation/GDP produce more analytical blurbs?
- Should framework intensity be per-section — heavy for labour and policy where the analytical rules matter, lighter elsewhere?
- How do we measure "good prose" in a way that's independent of the framework prose the blurb is being judged against?
- At what draw count does our current methodology actually stabilize? n=5? n=10?
