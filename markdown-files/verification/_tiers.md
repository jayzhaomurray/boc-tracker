# Content provenance tiers

A claim, blurb, framework signal, threshold band, code comment, or doc statement in this project carries one of three provenance tiers. The tier records *who* verified the content and *how rigorously*, separately from any verification verdict (VERIFIED / PARTIALLY VERIFIED / CONTESTED / UNSOURCED / PENDING) that captures *the result* of verification.

Two claims can both be VERIFIED but at different tiers. A Tier-3 VERIFIED claim has higher epistemic weight than a Tier-2 VERIFIED claim, because the user has actively challenged it.

## The three tiers

### Tier 1 — Generated

Claude produced the content with no verification step. The default tier for any new content unless explicitly upgraded.

**Examples:**
- The autonomous-draft section blurbs in `data/blurbs.json` for Labour Market, Financial Conditions, GDP, and Housing (generated May 8, 2026 against verified frameworks but with no user iteration).
- Any analytical framing or threshold value introduced in framework prose without source-grounding.
- Code comments that assert behaviour beyond what the line of code itself proves.

**Use Tier 1 content with caution.** Suitable for first-draft material that the user is expected to iterate. Not suitable for citing-as-fact in downstream work.

### Tier 2 — Autonomously verified

Claude (or a sub-agent acting on Claude's behalf) ran a structured verification pass: located primary sources, captured direct quotes, identified methodology gaps, compared claims against external evidence. The user did NOT review the verification process or conclusions.

**Higher confidence than Tier 1**, but susceptible to:
- Cherry-picked sources (the agent sourced what it expected to find, not what's most relevant)
- Sub-agent hallucinations or fabrications (e.g. invented quotes attributed to real people — the original Labour Claim 1 had two such fabrications that survived a Tier-2 pass)
- Confirmation-bias source selection (sources chosen for agreement, not breadth)
- Transferred-from-elsewhere heuristics not flagged as such (e.g. US JOLTS thresholds applied to Canadian JVWS — the original Labour Claim 3 did this)
- Stale or out-of-date sources

**Examples:**
- The "verified May 8, 2026" entries for the Inflation, Monetary Policy, GDP & Activity, Financial Conditions, and Housing sections in `markdown-files/HANDOFF.md` are Tier 2 — verified by Claude against sources, but never claim-by-claim reviewed by the user. (Inflation and Monetary Policy section *blurbs* did go through user iteration and are Tier 3 in their voice / wording, but the framework prose underneath is Tier 2 unless explicitly noted.)
- PENDING entries in section verification logs that come from autonomous research passes.
- The Beveridge curve chart at `analyses/beveridge_curve_canada.html` and its period-bucket boundaries.

**Tier 2 is the most dangerous tier** because it looks authoritative on the surface (sources cited, structured verdict glossary, primary-source URLs) but has not been challenged. Treat it as "ready for the user's review pass" — not as final.

### Tier 3 — User-verified

The user actively engaged with the content: pushed back on framings, challenged sources, requested re-checks, and gave explicit accept / reject / revise feedback per claim. The verification log captures the round trip.

**Examples:**
- Labour framework Claims 1, 2, and 3 (Claim 3 carries a re-review flag for 2026-05-10 but the structure of the verification — sources, direct quotes, decisions — is Tier 3 in process).
- Inflation and Monetary Policy section blurbs (went through multiple user-iterated voice cycles).
- The chart_style_guide.md principles (codified through user iteration).

**Highest confidence tier.** Still not infallible — the user might miss something — but the active challenge process catches the failure modes that Tier 2 doesn't.

## Tier degradation

A Tier-3 claim can drop to Tier 2 (or lower) if:
- New information surfaces that contradicts the original claim (re-verification needed)
- The underlying source is updated or retracted
- The framework around the claim changes meaningfully (the claim may still be true but the user's prior verification was against a different context)

When degrading, mark the claim's tier explicitly in its verification log entry with a dated note explaining why.

## How to mark tier

In verification logs, add a **Provenance tier** line near the top of each claim entry:

```markdown
**Provenance tier:** Tier 3 — user-verified 2026-05-09.
```

In framework prose (`markdown-files/analysis_framework.md`), tier markers are usually unnecessary — the verification log entry is the source of truth. But for high-stakes thresholds or named-source claims, an inline parenthetical can help: *"(Tier 2 source claim; not user-reviewed.)"*

In `HANDOFF.md`, "verified" language should specify the tier. Replace bare "verified" with "Tier-2 verified" or "Tier-3 verified" so a fresh session reading HANDOFF can calibrate weight.

In `data/blurbs.json`, no tier marker is currently stored — the per-section provenance is tracked in HANDOFF's "Verification status" block. If we ever add a tier field to the JSON, the contract is: `tier: 1 | 2 | 3`, with `as_of` capturing when the tier was assigned.

## When to upgrade

Tier 1 → Tier 2 happens when an autonomous verification pass runs against the content (write a verification log entry, mark Tier 2).

Tier 2 → Tier 3 happens when the user reviews the Tier-2 entry claim-by-claim and signs off (or revises). Mark the entry with a dated user-verification note.

Don't auto-upgrade tiers. The user's explicit engagement is the signal.
