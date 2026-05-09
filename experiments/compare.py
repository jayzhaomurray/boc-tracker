"""
Side-by-side blurb comparison renderer.

Reads two result files from the same run directory and writes a two-column
markdown table to compare/<section>.md in that directory.

Usage:
    python experiments/compare.py <result-dir> <config-a> <config-b> <section>

Example:
    python experiments/compare.py experiments/results/20260508T120000Z baseline obs_inf_rule labour
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def extract_blurb(result_file: Path) -> str:
    """
    Extract the text between the ## Blurb heading and the next ## heading.
    Returns stripped blurb prose, or an error string if not found.
    """
    text = result_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(
        r"## Blurb\s*\n(.*?)(?=\n## |\Z)",
        text,
        re.DOTALL,
    )
    if not match:
        return f"[ERROR: '## Blurb' section not found in {result_file.name}]"
    return match.group(1).strip()


def extract_frontmatter_field(result_file: Path, field: str) -> str:
    """Extract a single YAML frontmatter field value (simple key: value lines only)."""
    text = result_file.read_text(encoding="utf-8", errors="replace")
    m = re.search(rf"^{re.escape(field)}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else "unknown"


def make_compare_table(
    config_a: str,
    config_b: str,
    section: str,
    blurb_a: str,
    blurb_b: str,
    model_a: str,
    model_b: str,
) -> str:
    """Render a two-column markdown comparison table."""
    header = (
        f"# Comparison: {section}\n\n"
        f"| **{config_a}** (`{model_a}`) | **{config_b}** (`{model_b}`) |\n"
        f"|---|---|\n"
    )

    # Escape pipe characters inside blurb text so they don't break the table.
    def md_escape(s: str) -> str:
        return s.replace("|", "\\|").replace("\n", " ")

    row = f"| {md_escape(blurb_a)} | {md_escape(blurb_b)} |\n"
    return header + row


def main() -> None:
    if len(sys.argv) != 5:
        print(
            "Usage: python experiments/compare.py <result-dir> <config-a> <config-b> <section>",
            file=sys.stderr,
        )
        print(
            "Example: python experiments/compare.py experiments/results/20260508T120000Z baseline obs_inf_rule labour",
            file=sys.stderr,
        )
        sys.exit(1)

    result_dir_str, config_a, config_b, section = sys.argv[1:]
    result_dir = Path(result_dir_str)

    if not result_dir.exists() or not result_dir.is_dir():
        print(f"ERROR: result directory not found: {result_dir}", file=sys.stderr)
        sys.exit(1)

    file_a = result_dir / f"{config_a}.{section}.md"
    file_b = result_dir / f"{config_b}.{section}.md"

    for f in (file_a, file_b):
        if not f.exists():
            print(f"ERROR: result file not found: {f}", file=sys.stderr)
            sys.exit(1)

    blurb_a = extract_blurb(file_a)
    blurb_b = extract_blurb(file_b)
    model_a = extract_frontmatter_field(file_a, "model")
    model_b = extract_frontmatter_field(file_b, "model")

    table = make_compare_table(config_a, config_b, section, blurb_a, blurb_b, model_a, model_b)

    out_path = result_dir / f"compare.{section}.md"
    out_path.write_text(table, encoding="utf-8")
    print(f"Written: {out_path}")
    print()
    print(table)


if __name__ == "__main__":
    main()
