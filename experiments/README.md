# experiments/

A/B test blurb generation: framework changes, model swaps, prompt overrides — against the same input data, without touching the production `analyze.py` pipeline.

## Quick start

```powershell
# 1. Verify auth/subprocess plumbing (do this first)
python experiments/run.py --smoke-test

# 2. Run a config against all its sections
python experiments/run.py --config experiments/configs/baseline.yml

# 3. Run a single section only
python experiments/run.py --config experiments/configs/obs_inf_rule.yml --sections labour

# 4. Compare two configs side-by-side
python experiments/compare.py experiments/results/<timestamp> baseline obs_inf_rule labour
```

## File layout

```
experiments/
├── run.py              Main runner (CLI entry point)
├── compare.py          Side-by-side renderer
├── configs/            YAML experiment configs (committed)
│   ├── baseline.yml    Current framework, claude-opus-4-7, all six sections
│   ├── obs_inf_rule.yml  Baseline + observation/inference rule appended
│   └── sonnet_swap.yml   Baseline but model=claude-sonnet-4-6
└── results/            Timestamped run output (gitignored)
```

## Config schema

```yaml
name: <string>
model: claude-opus-4-7 | claude-sonnet-4-6 | claude-haiku-4-5-20251001
framework: markdown-files/analysis_framework.md
sections: [labour, gdp, inflation, policy, housing, financial]
self_review: true | false
overrides:
  output_rules_append: ~   # text appended to ## Output instructions in-memory
  output_rules_replace: ~  # text that fully replaces ## Output instructions body
```

## Authentication

The runner calls `claude --print <prompt>` via subprocess. This uses your existing Claude Code subscription — no `ANTHROPIC_API_KEY` needed. Run `--smoke-test` to confirm it works before a real run.

## Result format

Each run produces `experiments/results/<ISO-timestamp>/<config>.<section>.md` with YAML frontmatter, a `## Blurb` section, optional `## Self-review`, and the full `## Prompt` for reproducibility.
