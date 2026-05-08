# Long-term vision

Beyond the tactical todo list in HANDOFF — what this project could realistically grow into if work continues. Captured May 2026 during a planning conversation. Not a commitment, not a roadmap with dates; a set of capability trajectories the current architecture can reach without fundamental rework.

The thread connecting all of these: the current architecture (verified framework, structured formatter, plain-language voice with documented principles, daily auto-refresh, archive-able blurb output, public-data-only) was built primarily to produce a daily dashboard. Each direction below uses that same infrastructure to produce something *more* than a daily dashboard.

---

## 1. The blurb corpus becomes its own asset

A year of nightly blurbs across four sections is roughly 1,500 paragraphs of practitioner-grade analytical commentary in a consistent voice, each anchored to a specific dated data snapshot. That's a unique dataset — practitioner-voice commentary at daily granularity, with citations, doesn't exist publicly anywhere else.

What the corpus enables:

- **Semantic search over analytical reads.** "Show me every period the inflation read was tilted broad-based-pressure" / "every blurb where the BoC was on hold and the 2Y drift turned hawkish" / "every read where the BoC−Fed gap hit unusual." Embed every blurb; query in natural language.
- **Retrospective scorecards.** The framework explicitly bans forecasts in the prose, but the analytical *implications* are forecasts in disguise. "On day X, the blurb said markets were pricing hike risk. Did that play out?" Quietly tracking implications-vs-outcomes turns the corpus into a calibration record for the framework itself.
- **Pattern recognition by analogy.** "Show me every period that looked like today" — pulled from the corpus, not from chart shapes. A different way to answer "what does the past tell us about now."
- **Training data, eventually.** If you ever want a model that writes in this exact voice for adjacent domains or deeper analysis, the corpus is the seed.

## 2. The framework + voice become forkable infrastructure

The architecture is general. Verified framework, conditional interpretation tables, plain-language translation rules, structured formatter, blurb pipeline — none of it is Canada-specific.

A clone of the pattern for the Fed, ECB, BoE, RBA, RBNZ would produce, side-by-side, *practitioner-grade comparable analytical commentary across central banks, in one voice, on one site*. That artifact doesn't exist publicly. Commercial providers have data; central banks have hedged commentary in their own voices; nobody has consistent-voice plain-language analytical commentary across multiple central banks anchored to primary sources.

Forking is realistic because the architecture's already pointed at it: framework section per domain, compute/format pair per section, audit cycle per section. The work is the verification + calibration, not the infrastructure.

## 3. The dashboard becomes a thinking partner, not a publication

The user is not just a reader of this dashboard — they're its calibrator. Every pushback on a phrasing, flagged factual error, refined threshold sharpens the framework. Over time the framework reflects *the user's* analytical voice better than anyone else's, and reading the daily blurbs becomes a kind of conversation with their past analytical self.

There's a quantified-self analog: people track sleep or workouts to learn about themselves. This is tracking macro reads to learn about your own analytical instincts. The framework_writing_principles memory is already this in seed form — user preferences getting baked into infrastructure session by session.

If extended deliberately, the dashboard could surface "your read on April 7 said X; outcome Y; what does that say about your framework?" — not as a public scorecard, but as a personal calibration tool.

## 4. The "boring" capability that's rare: free, plain-language, sourced, daily commentary

Most public economic commentary is one of: bank-speak (hedged), news-speak (sensationalized), social-media-speak (hot-take), or paywalled (Bloomberg, Refinitiv, terminal-only). Free, plain-language, primary-source-grounded daily commentary on Canadian economic indicators is *missing* from the public web.

The project may not have set out to fill that gap, but it's structured to. The architecture is already publication-grade — public URL, daily refresh, archive-able, citation-grounded. The audience question — does anyone read this besides the author? — is downstream of the author *deciding* whether they want readers. If yes, distribution mechanisms (RSS, newsletter, social) are simple bolt-ons. If no, the value sits in (1) and (3) above instead.

This is a genuinely realistic public-good outcome: the free reference for someone who wants to know what's actually going on with the BoC and Canadian macro, in plain language, without paying for a terminal or wading through bank-speak.

## 5. The interactive layer, eventually

The current dashboard is a daily snapshot. The natural extension is query mode:
- "What does the inflation read look like with energy stripped out?"
- "Show me the policy read if the BoC had cut twice more by Q4."
- "What would the Monetary Policy blurb say if the spread closes to neutral?"

These are slight extensions of the `compute_*_values` functions: same code path, different parameter inputs, run on demand, explained in the same blurb voice. Conversational economic analysis grounded in real data, in the project's voice.

Not a chatbot. Not a dashboard. Something in between — and it's a genuinely new product format that the current architecture is unusually well-positioned to produce, because the framework + voice + verified compute pipeline already exist.

---

## What this could really be — in one phrase

*The public, plain-language, primary-source-grounded analytical commentary on the Canadian economy — daily, dated, archived, queryable, in one consistent voice.*

Right now it's a personal dashboard. Fully realized, it's the free reference for the macro-curious reader who wants to know what's actually happening, without paying for a terminal or translating bank-speak.

---

## What's NOT realistic without external inputs

- **Real-time / intraday alerts** — would require different data infrastructure than the daily-cron public-API model.
- **Forecast-tracking scorecards published under the project's name** — manageable as a private calibration tool (point 1 above); legally and reputationally complex once the project has a public audience.
- **Non-public datasets** — terminal data, proprietary surveys, paid feeds. Stays out of scope as long as "free public data only" is the operating constraint.
- **A practitioner-grade Canadian implied rate path chart** — blocked on free CRA-futures or CORRA-OIS access (already documented in HANDOFF Parked Items).

Each of these unblocks the moment a single external constraint changes (paid feed accepted, BoC publishes a feed, audience grows past tolerable threshold). They're not infrastructure problems; they're scope/access problems.
