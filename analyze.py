"""
Generate dashboard blurbs from the analysis framework + latest data.

Reads markdown-files/analysis_framework.md, computes the values referenced by
each section, calls Claude Opus to generate a blurb following the framework's
structure and style rules, and writes data/blurbs.json. build.py reads that
JSON and injects each blurb above the corresponding section heading.

Currently only the inflation section is wired up. Add more sections by
extending the SECTIONS dict and writing a compute_*_values + format_*_values
pair for each.

Run:    python analyze.py
        python analyze.py --print-only       (compute + show prompt; no API call)
Output: data/blurbs.json
Env:    ANTHROPIC_API_KEY required for the actual API call
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

DATA = Path("data")
FRAMEWORK = Path("markdown-files/analysis_framework.md")
OUT = DATA / "blurbs.json"

MODEL = "claude-opus-4-7"


# ── Data helpers ─────────────────────────────────────────────────────────────

def load_series(name: str) -> pd.Series:
    df = pd.read_csv(DATA / f"{name}.csv", parse_dates=["date"]).sort_values("date").set_index("date")
    return df["value"]


def asof(s: pd.Series, d: pd.Timestamp) -> float | None:
    sub = s[s.index <= d].dropna()
    return float(sub.iloc[-1]) if not sub.empty else None


# ── Inflation section ────────────────────────────────────────────────────────

def compute_inflation_values() -> dict:
    cpi      = load_series("cpi_all_items")  # SA
    food     = load_series("cpi_food")
    energy   = load_series("cpi_energy")
    goods    = load_series("cpi_goods")
    services = load_series("cpi_services")
    trim     = load_series("cpi_trim")
    median_  = load_series("cpi_median")
    common   = load_series("cpi_common")
    cpix     = load_series("cpix")
    cpixfet  = load_series("cpixfet")

    yoy_h = (cpi.pct_change(12) * 100).dropna()
    mom_h = (cpi.pct_change(1) * 100).dropna()
    ar3_h = (((cpi / cpi.shift(3)) ** 4 - 1) * 100).dropna()

    yoy_food     = (food.pct_change(12) * 100).dropna()
    yoy_energy   = (energy.pct_change(12) * 100).dropna()
    yoy_goods    = (goods.pct_change(12) * 100).dropna()
    yoy_services = (services.pct_change(12) * 100).dropna()

    latest = min(s.index[-1] for s in [
        yoy_h, trim, median_, common, cpix, cpixfet,
        yoy_food, yoy_energy, yoy_goods, yoy_services,
    ])

    cores = {
        "trim":    asof(trim, latest),
        "median":  asof(median_, latest),
        "common":  asof(common, latest),
        "cpix":    asof(cpix, latest),
        "cpixfet": asof(cpixfet, latest),
    }
    core_lo = min(cores.values())
    core_hi = max(cores.values())
    core_avg = sum(cores.values()) / len(cores)

    headline_yoy = asof(yoy_h, latest)

    # CPI breadth from depth-3 components
    mapping = json.loads((DATA / "cpi_breadth_mapping.json").read_text())
    weights = pd.Series({m["name"]: m["wt_value"] for m in mapping if m["wt_value"] is not None})
    comp = pd.read_csv(DATA / "cpi_components.csv", parse_dates=["date"], index_col="date")
    keep = [c for c in comp.columns
            if c in weights.index and comp[c].first_valid_index() <= pd.Timestamp("1995-01-01")]
    comp = comp[keep]
    w = weights.reindex(keep).fillna(0)
    w = w / w.sum()
    yoy_c = comp.pct_change(12) * 100
    above3 = yoy_c.gt(3).multiply(w, axis=1).sum(axis=1) * 100
    below1 = yoy_c.lt(1).multiply(w, axis=1).sum(axis=1) * 100
    valid = yoy_c.notna().all(axis=1)
    above3 = above3[valid]
    below1 = below1[valid]
    ha_above = above3["1996":"2019"].mean()
    ha_below = below1["1996":"2019"].mean()
    above_dev = float(above3.loc[latest] - ha_above)
    below_dev = float(below1.loc[latest] - ha_below)
    tilt = above_dev - below_dev

    return {
        "latest_date":         latest.strftime("%B %Y"),
        "headline_yoy":        headline_yoy,
        "headline_mom_sa":     asof(mom_h, latest),
        "headline_3m_ar_sa":   asof(ar3_h, latest),
        "cores":               cores,
        "core_band_lo":        core_lo,
        "core_band_hi":        core_hi,
        "core_band_width":     core_hi - core_lo,
        "core_avg":            core_avg,
        "headline_minus_core": headline_yoy - core_avg,
        "food_yoy":            asof(yoy_food, latest),
        "energy_yoy":          asof(yoy_energy, latest),
        "goods_yoy":           asof(yoy_goods, latest),
        "services_yoy":        asof(yoy_services, latest),
        "breadth_above3":      float(above3.loc[latest]),
        "breadth_below1":      float(below1.loc[latest]),
        "breadth_above3_dev":  above_dev,
        "breadth_below1_dev":  below_dev,
        "breadth_tilt":        tilt,
    }


def format_inflation_values(v: dict) -> str:
    c = v["cores"]
    return f"""== Latest data: {v['latest_date']} ==

Headline CPI Y/Y:         {v['headline_yoy']:+.2f}%
Headline M/M (SA):        {v['headline_mom_sa']:+.3f}%
Headline 3M AR (SA):      {v['headline_3m_ar_sa']:+.2f}%

Core measures (Y/Y):
  CPI-trim:               {c['trim']:+.2f}%
  CPI-median:             {c['median']:+.2f}%
  CPI-common:             {c['common']:+.2f}%
  CPIX:                   {c['cpix']:+.2f}%
  CPIXFET:                {c['cpixfet']:+.2f}%

Core band:                low {v['core_band_lo']:.2f}%, high {v['core_band_hi']:.2f}%, width {v['core_band_width']:.2f}pp
Core average:             {v['core_avg']:+.2f}%
Headline minus core avg:  {v['headline_minus_core']:+.2f}pp

Category breakdown (Y/Y):
  Food:                   {v['food_yoy']:+.2f}%
  Energy:                 {v['energy_yoy']:+.2f}%
  Goods:                  {v['goods_yoy']:+.2f}%
  Services:               {v['services_yoy']:+.2f}%

CPI Breadth:
  Share above 3%:         {v['breadth_above3']:.1f}%   (1996-2019 avg deviation: {v['breadth_above3_dev']:+.1f}pp)
  Share below 1%:         {v['breadth_below1']:.1f}%   (1996-2019 avg deviation: {v['breadth_below1_dev']:+.1f}pp)
  Breadth tilt:           {v['breadth_tilt']:+.1f}pp   (positive = broad-based pressure; negative = broad-based softening)
"""


# ── Section registry ─────────────────────────────────────────────────────────

SECTIONS = {
    "inflation": {
        "name":     "Inflation",
        "compute":  compute_inflation_values,
        "format":   format_inflation_values,
    },
    # Future: "policy", "labour", "external"
}


# ── Prompt + API call ────────────────────────────────────────────────────────

def build_prompt(section_id: str, framework: str, values_str: str,
                 prior_blurb: str | None = None) -> str:
    section_name = SECTIONS[section_id]["name"]
    prior = ""
    if prior_blurb:
        prior = (
            "\n== Prior month's blurb for this section (reference only; "
            "if signals have materially changed, surface what changed) ==\n\n"
            + prior_blurb + "\n"
        )
    return f"""You are generating a short analytical blurb for a public economic dashboard tracking Bank of Canada indicators. Read the analytical framework below, then read the latest computed data, then generate the blurb for the **{section_name}** section.

Output only the blurb prose. No preamble, no markdown headers, no quotation marks. Follow the framework's structure (takeaway -> anchor -> support -> closing nuance) and the writing-style rules (plain verbs, semicolons for parallel facts, conventional shorthand, plain hedges, no explanatory codas, no forecasts, no policy prescription). 3 sentences typically; 4 if there is a real tension worth surfacing in a closing slot.
{prior}
== Analytical Framework ==

{framework}

{values_str}

Now generate the {section_name} section blurb."""


def call_claude(prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-only", action="store_true",
                        help="Compute values and print the prompt; do not call API.")
    parser.add_argument("--section", default="inflation",
                        help="Section to generate (default: inflation).")
    args = parser.parse_args()

    section_id = args.section
    if section_id not in SECTIONS:
        print(f"Unknown section: {section_id}. Known: {list(SECTIONS)}", file=sys.stderr)
        sys.exit(2)

    framework = FRAMEWORK.read_text(encoding="utf-8")
    section = SECTIONS[section_id]
    values = section["compute"]()
    values_str = section["format"](values)

    print(f"=== {section['name']} — values for {values['latest_date']} ===\n")
    print(values_str)

    # Load any prior blurb for this section
    prior = None
    if OUT.exists():
        try:
            prior_data = json.loads(OUT.read_text())
            prior = prior_data.get(section_id, {}).get("text")
        except Exception:
            pass

    prompt = build_prompt(section_id, framework, values_str, prior_blurb=prior)

    if args.print_only:
        print("\n=== Prompt (not sent) ===\n")
        print(prompt[:1500] + ("\n... (truncated)" if len(prompt) > 1500 else ""))
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set.", file=sys.stderr)
        print("Set the env var and rerun. The prompt is ready and the data is computed; "
              "only the API call is missing.", file=sys.stderr)
        sys.exit(1)

    print(f"\nCalling Claude ({MODEL})...")
    blurb = call_claude(prompt)

    print("\n=== Generated blurb ===\n")
    print(blurb)

    out: dict = {}
    if OUT.exists():
        try:
            out = json.loads(OUT.read_text())
        except Exception:
            out = {}
    out[section_id] = {
        "as_of": values["latest_date"],
        "model": MODEL,
        "text":  blurb,
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nWrote: {OUT}")


if __name__ == "__main__":
    main()
