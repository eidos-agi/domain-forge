# AGENTS.md — domain-forge

Agent-first domain naming harness for the eidos-agi org.

## Have / want / don't want

- Have: a seed (brand, words, or an existing domain).
- Want: ranked alternatives with a love score and a registry availability signal.
- Don't want: auto-registration, WHOIS scraping, LLM-scored names, secrets in env.

## Canonical calls

```bash
domain-forge run "<seed>" --json
domain-forge suggest "<seed>" --json
domain-forge score example.com --json
domain-forge check example.com --json
domain-forge doctor --json
```

`--help` wins over this file. Always pass `--json` unless piping `--quiet`.

## Safety

Read-only. No `register`. `--available-only` filters after RDAP; it does not buy.

## Proof

`pytest` is the test command. `domain-forge doctor --json` is the slim health check.
