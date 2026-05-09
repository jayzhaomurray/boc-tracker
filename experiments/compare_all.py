"""
Batch comparison: pair up matching sections across two run directories and
generate one comparison markdown file per section, plus a summary.

Useful for full-section A/B sweeps (e.g. baseline vs obs_inf_rule across all
six sections at once).

Usage:
    python experiments/compare_all.py <run-dir-a> <run-dir-b> [--out-dir <path>]

Example:
    python experiments/compare_all.py \\
        experiments/results/20260509T030523Z \\
        experiments/results/20260509T030655Z

Default output directory: experiments/results/comparisons/<config_a>-vs-<config_b>/
so test artifacts stay inside experiments/ rather than littering the project root.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from compare import render_comparison, extract_frontmatter_field

DEFAULT_COMPARE_DIR = Path(__file__).resolve().parent / "results" / "comparisons"


def parse_filename(name: str) -> tuple[str, str] | None:
    """Parse '<config>.<section>.md' into (config, section). None if format doesn't match."""
    if not name.endswith(".md"):
        return None
    stem = name[:-3]
    parts = stem.split(".")
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


def index_run_dir(run_dir: Path) -> tuple[str | None, dict[str, Path]]:
    """Return (inferred_config_name, {section: filepath}) for a run directory."""
    files: dict[str, Path] = {}
    config_name: str | None = None
    for f in sorted(run_dir.glob("*.md")):
        parsed = parse_filename(f.name)
        if parsed is None:
            continue
        config, section = parsed
        # Skip any compare.<section>.md files that may already be in the dir.
        if config == "compare":
            continue
        files[section] = f
        if config_name is None:
            config_name = config
        elif config_name != config:
            print(
                f"WARNING: directory {run_dir} contains files from multiple configs "
                f"({config_name} and {config}); using {config_name} as the label.",
                file=sys.stderr,
            )
    return config_name, files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate side-by-side comparisons for all common sections "
                    "across two run directories."
    )
    parser.add_argument("dir_a", type=Path, help="First run directory.")
    parser.add_argument("dir_b", type=Path, help="Second run directory.")
    parser.add_argument(
        "--out-dir", type=Path, default=None,
        help="Output directory. Default: experiments/results/comparisons/<config_a>-vs-<config_b>/",
    )
    args = parser.parse_args()

    for d in (args.dir_a, args.dir_b):
        if not d.exists() or not d.is_dir():
            print(f"ERROR: directory not found: {d}", file=sys.stderr)
            sys.exit(1)

    config_a, files_a = index_run_dir(args.dir_a)
    config_b, files_b = index_run_dir(args.dir_b)

    if not files_a:
        print(f"ERROR: no result files found in {args.dir_a}", file=sys.stderr)
        sys.exit(1)
    if not files_b:
        print(f"ERROR: no result files found in {args.dir_b}", file=sys.stderr)
        sys.exit(1)

    out_dir = (
        args.out_dir
        if args.out_dir is not None
        else DEFAULT_COMPARE_DIR / f"{config_a}-vs-{config_b}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    common = sorted(set(files_a.keys()) & set(files_b.keys()))
    only_a = sorted(set(files_a.keys()) - set(files_b.keys()))
    only_b = sorted(set(files_b.keys()) - set(files_a.keys()))

    if only_a:
        print(f"Sections only in A ({config_a}): {only_a}", file=sys.stderr)
    if only_b:
        print(f"Sections only in B ({config_b}): {only_b}", file=sys.stderr)

    if not common:
        print("ERROR: no common sections found between the two directories.", file=sys.stderr)
        sys.exit(1)

    print(f"Comparing {len(common)} section(s) between '{config_a}' and '{config_b}'...")
    print(f"Output directory: {out_dir}")
    print()

    summary_rows: list[tuple[str, str, str]] = []
    for section in common:
        _, markdown = render_comparison(files_a[section], files_b[section])
        out_path = out_dir / f"compare.{section}.md"
        out_path.write_text(markdown, encoding="utf-8")

        review_a = extract_frontmatter_field(files_a[section], "self_review")
        review_b = extract_frontmatter_field(files_b[section], "self_review")
        summary_rows.append((section, review_a, review_b))

        print(f"  [{section}] Written: {out_path}")

    # Summary table
    print()
    print("Summary (self-review verdicts):")
    print(f"  {'section':<12} | {f'A: {config_a}':<25} | {f'B: {config_b}':<25}")
    print(f"  {'-'*12}-+-{'-'*25}-+-{'-'*25}")
    for section, ra, rb in summary_rows:
        print(f"  {section:<12} | {ra:<25} | {rb:<25}")

    a_passes = sum(1 for _, ra, _ in summary_rows if ra == "PASS")
    b_passes = sum(1 for _, _, rb in summary_rows if rb == "PASS")
    print()
    print(f"PASS counts: A={a_passes}/{len(common)}, B={b_passes}/{len(common)}")
    print(f"Done. {len(common)} comparison(s) written to {out_dir}")


if __name__ == "__main__":
    main()
