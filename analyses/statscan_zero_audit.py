"""
StatsCan zero-audit. Tier 2 audit run 2026-05-09.

Re-fetches every StatsCan vector via the NaN-preserving fetch_statscan and
diffs against the saved CSV. Looks for the same defect class that the JVWS
COVID-gap bug exposed: saved zero values where the live API returns null
(meaning data is structurally missing but the saved CSV records it as 0.0).

Output: analyses/statscan_zero_audit.md — markdown report listing per-series
findings. Don't auto-fix; user reviews and decides per-series.

Run from project root:  python analyses/statscan_zero_audit.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fetch import fetch_statscan, STATSCAN_SERIES  # noqa: E402

DATA_DIR = PROJECT_ROOT / "data"
OUT_PATH = Path(__file__).resolve().parent / "statscan_zero_audit.md"


def audit_series(name: str, vector_id: int, scale: float) -> dict:
    """Compare the live API response (NaN-preserving) against the saved CSV."""
    saved_path = DATA_DIR / f"{name}.csv"
    findings: dict = {
        "name": name,
        "vector_id": vector_id,
        "scale": scale,
        "saved_exists": saved_path.exists(),
        "ok": True,
        "notes": [],
    }

    try:
        live_df = fetch_statscan(vector_id)
    except Exception as exc:
        findings["ok"] = False
        findings["notes"].append(f"Live fetch FAILED: {exc}")
        return findings

    # Apply scale to live just like fetch.py would before saving
    live_df = live_df.copy()
    if scale != 1.0:
        live_df["value"] = live_df["value"] * scale

    findings["live_rows"] = len(live_df)
    findings["live_nan_rows"] = int(live_df["value"].isna().sum())
    findings["live_zero_rows"] = int((live_df["value"] == 0).sum())

    if not saved_path.exists():
        findings["ok"] = False
        findings["notes"].append("Saved CSV does not exist.")
        return findings

    saved_df = pd.read_csv(saved_path, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    findings["saved_rows"] = len(saved_df)
    findings["saved_nan_rows"] = int(saved_df["value"].isna().sum())
    findings["saved_zero_rows"] = int((saved_df["value"] == 0).sum())

    # Date-aligned comparison: build dict keyed by date, compare values
    saved_by_date = dict(zip(saved_df["date"], saved_df["value"]))
    live_by_date = dict(zip(live_df["date"], live_df["value"]))

    saved_dates = set(saved_by_date.keys())
    live_dates = set(live_by_date.keys())

    findings["dates_in_saved_only"] = sorted(saved_dates - live_dates)
    findings["dates_in_live_only"] = sorted(live_dates - saved_dates)

    # The signature defect: saved has 0 where live has NaN (structural-missing)
    stale_zero_dates = []
    for d in saved_dates & live_dates:
        sv = saved_by_date[d]
        lv = live_by_date[d]
        if pd.notna(sv) and sv == 0 and pd.isna(lv):
            stale_zero_dates.append(d)

    findings["stale_zero_dates"] = sorted(stale_zero_dates)

    # Other value disagreements (small float drift is fine; flag only if material)
    disagreements = []
    for d in saved_dates & live_dates:
        sv = saved_by_date[d]
        lv = live_by_date[d]
        if pd.isna(sv) and pd.isna(lv):
            continue
        if pd.isna(sv) or pd.isna(lv):
            disagreements.append((d, sv, lv, "one is NaN"))
            continue
        if abs(sv - lv) > max(1e-6, abs(sv) * 1e-4):  # 0.01% relative tol
            disagreements.append((d, sv, lv, f"diff {sv - lv:+.6g}"))

    findings["material_disagreements"] = disagreements[:10]  # cap noise
    findings["material_disagreement_count"] = len(disagreements)

    # Verdict
    if stale_zero_dates:
        findings["ok"] = False
        findings["notes"].append(
            f"STALE-ZERO BUG: {len(stale_zero_dates)} dates have saved=0 but live=NaN."
        )
    if findings["dates_in_saved_only"]:
        findings["notes"].append(
            f"{len(findings['dates_in_saved_only'])} dates in saved CSV are not in live API "
            f"(deprecated periods or fetcher anomaly)."
        )
    if findings["dates_in_live_only"]:
        findings["notes"].append(
            f"{len(findings['dates_in_live_only'])} dates in live API are not in saved CSV "
            f"(saved CSV is stale; re-fetch would add them)."
        )
    if findings["material_disagreement_count"]:
        findings["notes"].append(
            f"{findings['material_disagreement_count']} material value disagreements "
            f"(beyond 0.01% relative tolerance; first 10 listed below)."
        )

    return findings


def render_report(all_findings: list[dict]) -> str:
    """Render the audit findings as a markdown report."""
    n_total = len(all_findings)
    n_clean = sum(1 for f in all_findings if f["ok"] and not f["notes"])
    n_stale_zero = sum(1 for f in all_findings if f.get("stale_zero_dates"))
    n_failed = sum(1 for f in all_findings if not f["ok"])

    lines: list[str] = []
    lines.append("# StatsCan zero-audit report")
    lines.append("")
    lines.append("**Audit date:** 2026-05-09")
    lines.append("**Provenance tier:** Tier 2 (autonomous audit; not user-reviewed). See `markdown-files/verification/_tiers.md`.")
    lines.append("")
    lines.append(
        "Re-fetches every StatsCan vector with the NaN-preserving fetch_statscan "
        "and diffs against the saved CSV. Looks for the same defect class that the "
        "JVWS COVID-gap bug exposed (saved 0.0 where live API returns null), plus "
        "any other date-coverage mismatches."
    )
    lines.append("")
    lines.append("**Summary:**")
    lines.append(f"- {n_total} StatsCan series audited.")
    lines.append(f"- {n_clean} series clean (no findings).")
    lines.append(f"- {n_stale_zero} series with stale-zero-bug occurrences.")
    lines.append(f"- {n_failed} series failed audit (live fetch failed or saved CSV missing).")
    lines.append("")
    lines.append("**How to fix a stale-zero finding:** re-fetch the affected series via `python fetch.py` (the NaN-preserving fetcher will overwrite the saved CSV with NaN rows where the API returns null). For a one-off targeted fix, see the JVWS pattern in commit `529ce45` for the inline Python snippet.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Group: series with findings first, then clean ones (counted only)
    findings_with_issues = [f for f in all_findings if f["notes"] or not f["ok"]]
    clean_findings = [f for f in all_findings if not (f["notes"] or not f["ok"])]

    if findings_with_issues:
        lines.append("## Series with findings")
        lines.append("")
        for f in findings_with_issues:
            lines.append(f"### `{f['name']}` (vector {f['vector_id']})")
            lines.append("")
            if "saved_rows" in f:
                lines.append(f"- Saved CSV: {f['saved_rows']} rows (NaN: {f['saved_nan_rows']}, zero: {f['saved_zero_rows']})")
            if "live_rows" in f:
                lines.append(f"- Live API: {f['live_rows']} rows (NaN: {f['live_nan_rows']}, zero: {f['live_zero_rows']})")
            for note in f["notes"]:
                lines.append(f"- **Finding:** {note}")
            if f.get("stale_zero_dates"):
                lines.append("")
                lines.append("  Stale-zero dates (saved=0, live=NaN):")
                for d in f["stale_zero_dates"][:50]:
                    lines.append(f"    - {pd.Timestamp(d).date()}")
                if len(f["stale_zero_dates"]) > 50:
                    lines.append(f"    - ... ({len(f['stale_zero_dates']) - 50} more)")
            if f.get("dates_in_saved_only"):
                lines.append("")
                lines.append("  Dates in saved-only (sample):")
                for d in f["dates_in_saved_only"][:10]:
                    lines.append(f"    - {pd.Timestamp(d).date()}")
            if f.get("dates_in_live_only"):
                lines.append("")
                lines.append("  Dates in live-only (sample; would be added by re-fetch):")
                for d in f["dates_in_live_only"][:10]:
                    lines.append(f"    - {pd.Timestamp(d).date()}")
            if f.get("material_disagreements"):
                lines.append("")
                lines.append("  Material value disagreements (date | saved | live | note):")
                for d, sv, lv, note in f["material_disagreements"]:
                    lines.append(f"    - {pd.Timestamp(d).date()} | {sv} | {lv} | {note}")
            lines.append("")
    else:
        lines.append("## No findings")
        lines.append("")
        lines.append("All audited series are clean.")
        lines.append("")

    if clean_findings:
        lines.append("## Clean series (no findings)")
        lines.append("")
        for f in clean_findings:
            lines.append(f"- `{f['name']}` (vector {f['vector_id']}; {f['saved_rows']} rows)")
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    print("StatsCan zero-audit starting...")
    all_findings = []
    for name, entry in STATSCAN_SERIES.items():
        if isinstance(entry, tuple):
            vector_id, scale = entry
        else:
            vector_id, scale = entry, 1.0
        print(f"  Auditing {name} (vector {vector_id})...")
        f = audit_series(name, vector_id, float(scale))
        all_findings.append(f)
        if f["notes"]:
            print(f"    -> {len(f['notes'])} finding(s)")
        else:
            print("    -> clean")

    report = render_report(all_findings)
    OUT_PATH.write_text(report, encoding="utf-8")
    print(f"\nReport written: {OUT_PATH}")

    n_stale_zero = sum(1 for f in all_findings if f.get("stale_zero_dates"))
    n_dirty = sum(1 for f in all_findings if f["notes"] or not f["ok"])
    n_total = len(all_findings)
    print(f"Summary: {n_total} audited; {n_dirty} with findings; {n_stale_zero} with stale-zero bug.")


if __name__ == "__main__":
    main()
