# domain-forge

Generate alternative domains, score how much people will love them, then see if they are available.

`eidos-domains` is the same CLI.

This is a **check harness**, not a registrar. It will not buy a name.

## Why

Picking a domain by staring at Namecheap is a slot machine. domain-forge makes the three questions an agent (or a human) can actually answer in order:

1. What else could this be called?
2. Would a person like saying it?
3. Is the registry empty?

## Install

```bash
git clone https://github.com/eidos-agi/domain-forge.git ~/repos-eidos-agi/domain-forge
cd ~/repos-eidos-agi/domain-forge
pip install -e .
```

## Commands

```bash
domain-forge suggest "eidos" --json
domain-forge score eidos.com eidos.ai --json
domain-forge check eidos.com zzzznotarealxyz123.com --json
domain-forge run "eidos agi" --json
domain-forge run "eidos" --no-check --json          # offline: generate + score only
domain-forge run "eidos" --available-only --json    # RDAP 404s in the top --limit window
domain-forge doctor --json
```

`--help` is the schema. `--json` is the agent default. `--quiet` prints one domain per line.

## Love score

`love` is 0–100, summed from named factors (not a model vibe):

| Factor | Max | What it captures |
|---|---|---|
| length | 20 | 4–8 character SLD sweet spot |
| pronounce | 18 | syllables, vowel presence, consonant piles |
| spell | 15 | digits, hyphens, lookalikes |
| tld | 15 | `.com` still wins; `.xyz` is a joke to civilians |
| clean | 12 | business-card test |
| radio | 10 | say it once, can they type it? |
| wordness | 10 | real word or clear blend vs noise |

Generic SLDs (`cloud`, `app`, `data`) are penalized. Stopwords are capped. The JSON includes `factors[]`, `grade`, `must_spell`, `say_on_a_call`, and a one-line `why`.

## Availability

RDAP is the registry signal:

- HTTP 200 → `taken`
- HTTP 404 → `available` (not in the registry — not a purchase guarantee)
- anything else → `unknown`

Default TLDs (`.com` `.ai` `.io` `.dev` `.app` `.org`) all have baked RDAP bases plus the IANA bootstrap cache. `.co` is not a default — its nic RDAP host does not resolve, and we will not fall back to DNS on the default path. Other TLDs with no RDAP server fall back to DNS-over-HTTPS and come back `confidence: weak`. `--available-only` keeps only `source=rdap` / `confidence=registry` rows.

Premium, reserved, and trademark-blocked names can 404 and still refuse to sell. Treat `available` as “worth trying at a registrar,” not “yours.”

## Safety

All commands are read-only. There is no `register` command. Buying a domain is a human + registrar + Knox step, not an agent loop.

## Skill

Copy `.claude/skills/domain-forge.md` into an agent project when you want agents to reach for this CLI instead of improvising WHOIS.

## License

MIT — [Eidos AGI](https://github.com/eidos-agi)
