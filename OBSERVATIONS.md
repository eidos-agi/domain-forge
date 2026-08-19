# OBSERVATIONS

## 2026-08-19 — Discipline started day 1
At stake: v2 being able to tell whether the love rubric and RDAP mapping were guesses or measured.
Noted: `.io` is not in the IANA RDAP DNS bootstrap; `rdap.identitydigital.services` answers `github.io` with a real domain object and 404s a fake. `.com` Verisign 200/404 behaves as advertised. `rdap.org` timed out on a missing .io name and is not a reliable client bootstrap.

## 2026-08-19 — Google registry path
`https://pubapi.registry.google/rdap/domain/{name}` returns 200 for `pages.dev` / `google.dev` and 404 for a fake `.dev`. The older `rdap.nic.google` guess is unnecessary.

## 2026-08-19 — secondlook LOOK-0001: available-only was not an RDAP filter
At stake: an agent treating DNS NXDOMAIN as "the name is free."
`--available-only` kept `status == "available"` including `source: dns / confidence: weak`. `.co` was a default TLD with no baked RDAP floor (`rdap.nic.co` does not resolve). Debate (claude, codex, cursor-agent, grok) converged on: filter must require `source=rdap` and `confidence=registry`; drop `.co` from defaults rather than bake a dead host; `--no-check --available-only` must error; doctor must AND `baked_rdap` into `ok`. PREFIXES/SUFFIXES stay — GENERIC is an exact-SLD penalty, not an affix ban.
