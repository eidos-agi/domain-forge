---
name: domain-forge
description: Generate alternative domains, score how much people will love them, and check RDAP availability. Use instead of improvising WHOIS. Does not register domains.
user_invocable: true
---

# domain-forge — name it, score the love, see if it's free

Agent-first CLI. `--json` on every command. `--help` is the schema.
`eidos-domains` is the same binary.

## Trigger

Use this when the user wants another domain, a better domain, a love ranking, or an availability check. Do not invent WHOIS by hand.

## Setup

```
pip install -e ~/repos-eidos-agi/domain-forge
```

No API keys. No env vars required. Optional: `DOMAIN_FORGE_CACHE` to relocate the IANA RDAP bootstrap cache.

## Commands

| Command | Purpose | Canonical |
|---|---|---|
| `run` | Generate + score + RDAP | `domain-forge run "eidos" --json` |
| `suggest` | Generate + score, no network | `domain-forge suggest "eidos" --json` |
| `score` | Love-score known names | `domain-forge score eidos.com eidos.ai --json` |
| `check` | RDAP availability | `domain-forge check eidos.com --json` |
| `doctor` | Runtime health | `domain-forge doctor --json` |

## Canonical workflows

Generate, rank, and see what's free:

```bash
domain-forge run "eidos agi" --limit 15 --json
```

Offline (airplane, CI):

```bash
domain-forge run "eidos" --no-check --json
```

Keep RDAP-empty names in the top `--limit` love window (not a cart, not DNS):

```bash
domain-forge run "eidos" --available-only --json
```

Inspect `availability.source` and `availability.confidence` before treating a row as empty. Do not pipe to domain-only `jq` and call that list free. `--available-only` cannot be combined with `--no-check`.

Score a shortlist the human already has:

```bash
domain-forge score northstar.com north-star.com northstar.ai --json
```

## Safety

All commands are read-only. There is no register/buy/cart path. `available` means RDAP 404, not "purchase will succeed." Premium and reserved names can still refuse.

Do not call registrar APIs from a loop. Hand the shortlist to a human.

## Rules for agents

- Always `--json` unless `--quiet` for a domain list.
- Trust `--help` over this file.
- Failures: exit 2 = usage; exit 1 = doctor failed.
- Do not "improve" the love score with an LLM. The rubric is the product.
- Glue names (`getX`, `Xkit`) must score below the brand. If they don't, the scorer is wrong.
