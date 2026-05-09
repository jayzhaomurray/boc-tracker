"""
Side-by-side blurb comparison renderer.

Reads two result files (from any directory) and writes a comparison markdown
file showing both blurbs labeled with their config + model.

Usage:
    python experiments/compare.py <file-a> <file-b> [--out <path>]

Example:
    python experiments/compare.py \\
        experiments/results/20260508T120000Z/baseline.labour.md \\
        experiments/results/20260508T122000Z/obs_inf_rule.labour.md

If --out is not supplied, writes to the current working directory as
compare.<section>.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def extract_blurb(result_file: Path) -> str:
    """Extract the text between '## Blurb' and the next '##' heading."""
    text = result_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"## Blurb\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not match:
        return f"[ERROR: '## Blurb' section not found in {result_file.name}]"
    return match.group(1).strip()


def extract_review(result_file: Path) -> str | None:
    """Extract the text between '## Self-review' and the next '##' heading, or None if not present."""
    text = result_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"## Self-review\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    return match.group(1).strip() if match else None


def extract_frontmatter_field(result_file: Path, field: str) -> str:
    """Extract a single YAML frontmatter field value (simple key: value lines only)."""
    text = result_file.read_text(encoding="utf-8", errors="replace")
    m = re.search(rf"^{re.escape(field)}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else "unknown"


def render_comparison(file_a: Path, file_b: Path) -> tuple[str, str]:
    """Render a comparison markdown document from two result files. Returns (section, markdown)."""
    config_a = extract_frontmatter_field(file_a, "config")
    config_b = extract_frontmatter_field(file_b, "config")
    model_a  = extract_frontmatter_field(file_a, "model")
    model_b  = extract_frontmatter_field(file_b, "model")
    section_a = extract_frontmatter_field(file_a, "section")
    section_b = extract_frontmatter_field(file_b, "section")

    if section_a != section_b:
        print(
            f"WARNING: comparing across different sections ({section_a} vs {section_b}). "
            "Side-by-side may not be meaningful.",
            file=sys.stderr,
        )

    section = section_a if section_a == section_b else f"{section_a}-vs-{section_b}"

    blurb_a  = extract_blurb(file_a)
    blurb_b  = extract_blurb(file_b)
    review_a = extract_review(file_a)
    review_b = extract_review(file_b)

    lines = [
        f"# Comparison — {section}",
        "",
        f"- **A:** `{config_a}` ({model_a}) — `{file_a}`",
        f"- **B:** `{config_b}` ({model_b}) — `{file_b}`",
        "",
        "---",
        "",
        f"## A — {config_a} ({model_a})",
        "",
        blurb_a,
        "",
    ]
    if review_a:
        lines += ["**Self-review:**", "", review_a, ""]

    lines += [
        "---",
        "",
        f"## B — {config_b} ({model_b})",
        "",
        blurb_b,
        "",
    ]
    if review_b:
        lines += ["**Self-review:**", "", review_b, ""]

    return section, "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a side-by-side comparison of two blurb result files."
    )
    parser.add_argument("file_a", type=Path, help="First result file (.md from a run).")
    parser.add_argument("file_b", type=Path, help="Second result file (.md from a run).")
    parser.add_argument(
        "--out", type=Path, default=None,
        help="Output path. Default: compare.<section>.md in the current directory.",
    )
    args = parser.parse_args()

    for f in (args.file_a, args.file_b):
        if not f.exists():
            print(f"ERROR: result file not found: {f}", file=sys.stderr)
            sys.exit(1)

    section, markdown = render_comparison(args.file_a, args.file_b)

    out_path = args.out if args.out is not None else Path.cwd() / f"compare.{section}.md"
    out_path.write_text(markdown, encoding="utf-8")
    print(f"Written: {out_path}")
    print()
    print(markdown)


if __name__ == "__main__":
    main()
