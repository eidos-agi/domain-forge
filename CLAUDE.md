# CLAUDE.md — domain-forge

Generate alternative domains, score how much people will love them, check RDAP availability.

`eidos-domains` is an alias for the same CLI.

## What this is

A **tool forge** (CLI + skill). Not a knowledge-only forge. Not a registrar.

Commands: `suggest`, `score`, `check`, `run`, `doctor`. `--json` on all of them.

## Guardrails

- **Never register a domain.** There is no purchase path. Availability is a signal.
- **Love is a named rubric, not a model call.** If you want to change scoring, change `score.py` factors and tests — do not hide it behind an LLM.
- **RDAP 404 is not a cart.** Reserved/premium names can 404 and still refuse to sell.
- **Stdlib only.** No `anthropic`, no registrar SDKs, no API keys required.

## Layout

- `domain_forge/generate.py` — alternative SLDs × TLDs
- `domain_forge/score.py` — love 0–100
- `domain_forge/check.py` — RDAP + weak DNS fallback
- `domain_forge/pipeline.py` — `run` harness
- `domain_forge/cli.py` — argparse, agent-first

## Related

- brand-forge — identity, not names
- cli-forge — the CLI contract this follows
- foss-forge — publish standards
