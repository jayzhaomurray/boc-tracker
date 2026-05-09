"""
Blurb experiment runner.

Runs one or more (config x section) combinations, calls the LLM via
`claude --print` subprocess (uses Claude Code auth — no ANTHROPIC_API_KEY
required), and writes timestamped result files to experiments/results/.

Usage:
    python experiments/run.py --config experiments/configs/baseline.yml
    python experiments/run.py --config experiments/configs/obs_inf_rule.yml --sections labour
    python experiments/run.py --smoke-test
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Project root is one level above this file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR  = Path(__file__).resolve().parent / "results"

# Ensure analyze.py is importable from the project root.
sys.path.insert(0, str(PROJECT_ROOT))

VALID_SECTIONS = ["labour", "gdp", "inflation", "policy", "housing", "financial"]


# ── Subprocess LLM call ──────────────────────────────────────────────────────

def call_claude_cli(prompt: str) -> str:
    """
    Call `claude --print` via subprocess, passing the prompt on stdin.

    Stdin is used (not argv) because long prompts exceed Windows' ~32KB
    CreateProcess argv limit — a real labour-section prompt is ~50KB+ once
    the full framework prose is included. Stdin has no length limit.

    Returns the stripped stdout. Raises RuntimeError on non-zero exit.
    """
    result = subprocess.run(
        ["claude", "--print"],
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:
        stderr_snippet = (result.stderr or "")[:500]
        raise RuntimeError(
            f"`claude --print` exited with code {result.returncode}.\n"
            f"stderr: {stderr_snippet}"
        )

    return result.stdout.strip()


# ── Framework override logic ─────────────────────────────────────────────────

# Matches the ## Output instructions section heading and captures everything
# after it until the next ## heading (or end of file).
_OUTPUT_SECTION_RE = re.compile(
    r"(## Output instructions\s*\n)(.*?)(?=\n## |\Z)",
    re.DOTALL,
)


def apply_framework_overrides(framework_text: str, overrides: dict) -> str:
    """
    Apply output_rules_append / output_rules_replace to the framework text
    in memory. Does NOT write back to disk.
    """
    if not overrides:
        return framework_text

    append_text  = overrides.get("output_rules_append")
    replace_text = overrides.get("output_rules_replace")

    # Both null → nothing to do.
    if not append_text and not replace_text:
        return framework_text

    match = _OUTPUT_SECTION_RE.search(framework_text)
    if not match:
        # Framework doesn't have a ## Output instructions section.
        # Warn and proceed without modification.
        print(
            "  WARNING: '## Output instructions' section not found in framework; "
            "overrides not applied.",
            file=sys.stderr,
        )
        return framework_text

    heading   = match.group(1)   # "## Output instructions\n"
    body      = match.group(2)   # existing body text

    if replace_text:
        new_body = replace_text.rstrip() + "\n"
    elif append_text:
        new_body = body.rstrip() + "\n" + append_text.rstrip() + "\n"
    else:
        new_body = body

    return framework_text[: match.start()] + heading + new_body + framework_text[match.end() :]


# ── Result file writer ───────────────────────────────────────────────────────

def write_result(
    run_dir: Path,
    config_name: str,
    section_id: str,
    blurb: str,
    prompt: str,
    review: str | None,
    model: str,
    timestamp: str,
) -> Path:
    """Write <run_dir>/<config_name>.<section_id>.md and return the path."""
    run_dir.mkdir(parents=True, exist_ok=True)

    frontmatter_lines = [
        "---",
        f"config: {config_name}",
        f"model: {model}",
        f"section: {section_id}",
        f"timestamp: {timestamp}",
    ]
    if review is not None:
        verdict = "PASS" if review.strip().upper().startswith("PASS") else "FLAGGED"
        frontmatter_lines.append(f"self_review: {verdict}")
    frontmatter_lines.append("---")

    parts = ["\n".join(frontmatter_lines), ""]
    parts.append("## Blurb\n")
    parts.append(blurb)
    parts.append("")

    if review is not None:
        parts.append("## Self-review\n")
        parts.append(review)
        parts.append("")

    parts.append("## Prompt\n")
    parts.append(prompt)
    parts.append("")

    out_path = run_dir / f"{config_name}.{section_id}.md"
    out_path.write_text("\n".join(parts), encoding="utf-8")
    return out_path


# ── em-dash normaliser (mirrors analyze.py) ─────────────────────────────────

def _normalize_dashes(text: str) -> str:
    text = text.replace(" -- ", "—").replace(" - ", "—")
    text = re.sub(r"\s*—\s*", "—", text)
    return text


# ── Naive prompt (no framework scaffolding) ─────────────────────────────────

def build_naive_prompt(section_name: str, values_str: str) -> str:
    """
    Minimal prompt: just task + data. No framework prose, no thresholds, no
    "what to surface" guidance. Used to test how much the analytical framework
    is actually contributing vs. what the model produces from training alone.

    Self-review (which still uses the framework as the rubric) is run on the
    output of this prompt the same way it's run on framework-mode output, so
    naive blurbs get judged by the same standard.
    """
    return f"""You are writing a short analytical blurb for an economics dashboard about Canada's {section_name} for an informed reader. Write 2-4 sentences capturing what the data below shows. Output only the blurb prose — no preamble, no markdown headers, no quotation marks.

== Data ==

{values_str}
"""


# ── Smoke test ───────────────────────────────────────────────────────────────

def smoke_test() -> None:
    """Send a trivial prompt and print the response. Verifies auth/subprocess plumbing."""
    print("Running smoke test: sending trivial prompt to `claude --print`...")
    try:
        response = call_claude_cli("respond with the word OK and nothing else")
        print(f"Response: {response!r}")
        if "ok" in response.lower():
            print("Smoke test PASSED.")
        else:
            print(
                "Smoke test UNCERTAIN: got a response, but it doesn't contain 'OK'. "
                "Check the output above — may still be working."
            )
    except RuntimeError as e:
        print(f"Smoke test FAILED: {e}", file=sys.stderr)
        sys.exit(1)


# ── Main runner ───────────────────────────────────────────────────────────────

def run_config(config_path: Path, section_override: list[str] | None = None) -> None:
    with config_path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    config_name = cfg["name"]
    model       = cfg["model"]
    framework_rel = cfg.get("framework", "markdown-files/analysis_framework.md")
    sections    = cfg.get("sections", VALID_SECTIONS)
    self_review = cfg.get("self_review", False)
    overrides   = cfg.get("overrides") or {}
    prompt_mode = cfg.get("prompt_mode", "framework")  # "framework" | "naive"

    if prompt_mode not in ("framework", "naive"):
        print(f"ERROR: prompt_mode must be 'framework' or 'naive'; got '{prompt_mode}'", file=sys.stderr)
        sys.exit(2)

    if section_override:
        for s in section_override:
            if s not in VALID_SECTIONS:
                print(f"ERROR: unknown section '{s}'. Valid: {VALID_SECTIONS}", file=sys.stderr)
                sys.exit(2)
        sections = section_override

    # Validate sections against the config's declared list.
    for s in sections:
        if s not in VALID_SECTIONS:
            print(f"ERROR: unknown section '{s}'. Valid: {VALID_SECTIONS}", file=sys.stderr)
            sys.exit(2)

    framework_path = PROJECT_ROOT / framework_rel
    if not framework_path.exists():
        print(f"ERROR: framework file not found: {framework_path}", file=sys.stderr)
        sys.exit(1)

    framework_text = framework_path.read_text(encoding="utf-8")
    framework_text = apply_framework_overrides(framework_text, overrides)

    # Import analyze.py functions from the project root.
    import analyze  # noqa: PLC0415
    from analyze import SECTIONS, build_prompt  # noqa: PLC0415

    # Shared timestamp directory for this run invocation.
    now        = datetime.now(timezone.utc)
    ts_str     = now.strftime("%Y%m%dT%H%M%SZ")
    run_dir    = RESULTS_DIR / ts_str

    print(f"Config: {config_name}  |  Model: {model}  |  Mode: {prompt_mode}  |  Sections: {sections}")
    print(f"Results directory: {run_dir}")

    for section_id in sections:
        if section_id not in SECTIONS:
            print(f"  ERROR: section '{section_id}' not registered in analyze.SECTIONS; skipping.", file=sys.stderr)
            continue

        print(f"\n  [{section_id}] Computing values...", end=" ", flush=True)
        section_def = SECTIONS[section_id]
        values      = section_def["compute"]()
        values_str  = section_def["format"](values)
        print("done.")

        if prompt_mode == "naive":
            prompt = build_naive_prompt(section_def["name"], values_str)
        else:
            prompt = build_prompt(section_id, framework_text, values_str)

        print(f"  [{section_id}] Calling LLM ({model})...", end=" ", flush=True)
        try:
            raw = call_claude_cli(prompt)
        except RuntimeError as e:
            print(f"\n  ERROR calling LLM for section '{section_id}': {e}", file=sys.stderr)
            continue
        blurb = _normalize_dashes(raw)
        print("done.")

        review_text: str | None = None
        if self_review:
            print(f"  [{section_id}] Running self-review...", end=" ", flush=True)
            review_prompt = _build_review_prompt(section_def["name"], framework_text, values_str, blurb)
            try:
                review_text = call_claude_cli(review_prompt)
            except RuntimeError as e:
                review_text = f"ERROR: self-review call failed: {e}"
            print("done.")

        out_path = write_result(
            run_dir=run_dir,
            config_name=config_name,
            section_id=section_id,
            blurb=blurb,
            prompt=prompt,
            review=review_text,
            model=model,
            timestamp=now.isoformat(),
        )
        print(f"  [{section_id}] Written: {out_path.relative_to(PROJECT_ROOT)}")

    print(f"\nRun complete. Results in: {run_dir}")


def _build_review_prompt(section_name: str, framework: str, values_str: str, blurb: str) -> str:
    """Mirror of analyze.review_blurb's prompt, adapted for the subprocess flow."""
    return f"""You are reviewing an AI-generated analytical blurb for a Bank of Canada economics dashboard. The blurb was just generated against the framework section and computed data values below. Your job: check for factual or interpretive errors against those inputs.

== Framework section the blurb was generated against ==

{framework}

== Computed data values it should reflect ==

{values_str}

== Generated blurb ==

{blurb}

== Review checklist ==

For each, state PASS or describe the specific issue:

1. **Direction / sign correctness.** Every claim about something rising / falling / being above-or-below something else must match the data.

2. **Asset / liability / structural correctness.** Does the blurb correctly distinguish things on opposite sides of a balance sheet, opposite signs of a spread, different categorical buckets?

3. **Attribution.** Does the blurb attribute moves to the right entity?

4. **Dates and timeframes.** Do dates referenced match what the data shows?

5. **Action-state verb correctness.** If action_state is "on hold", verbs should reflect holding, not cutting/hiking.

6. **Magnitude / threshold correctness.** If the blurb cites a percentile, threshold, or magnitude, does it match the data?

== Output ==

Respond with EXACTLY one of:
- The single word "PASS" if the blurb has no factual errors against the framework and data.
- Otherwise, a bulleted list of specific factual issues. Each bullet: name the exact phrase, what's wrong, what the data actually shows.

Do NOT comment on writing style, voice, length, or word choice. Only factual / interpretive correctness against the inputs above."""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Blurb experiment runner for boc-tracker."
    )
    parser.add_argument(
        "--config", metavar="PATH",
        help="Path to a YAML config file (e.g. experiments/configs/baseline.yml).",
    )
    parser.add_argument(
        "--sections", nargs="+", metavar="SECTION",
        help="Override which sections to run (space-separated). Must be a subset of the config's sections.",
    )
    parser.add_argument(
        "--smoke-test", action="store_true",
        help="Send a trivial prompt to verify `claude --print` auth/subprocess plumbing.",
    )
    args = parser.parse_args()

    if args.smoke_test:
        smoke_test()
        return

    if not args.config:
        parser.error("--config is required unless --smoke-test is set.")

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"ERROR: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    run_config(config_path, section_override=args.sections)


if __name__ == "__main__":
    main()
