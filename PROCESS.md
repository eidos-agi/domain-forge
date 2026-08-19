# PROCESS

## 2026-08-19 — From harness to domain-forge

Started as "eidos-agi org needs a domain registration harness that calculates alternative domains, scores them on how much people will love them, and then sees if they are available."

Daniel named the repo twice: `eidos-domains`, then `domain-forge`. Both names shipped as entry points; the GitHub repo is `eidos-agi/domain-forge` so it sits with the other forges.

Rejected path: knowledge-only forge (forge-init's default). A skill cannot check a registry. brand-forge already showed the org will put software in a `*-forge` when the work is a tool.

Rejected path: Porkbun/Cloudflare purchase API as v1. That needs Knox, spends money, and turns an agent into a registrar. Availability via RDAP is the honest v1.

Rejected path: LLM love scores. The user asked how much people will love the names — that is a radio test and a TLD-trust test, which we can name and test. A completion would not be replayable.

Kept: cli-forge contract (`--json`, no prompts, `--help` is schema), foss community files, testr/shipr product models.

## 2026-08-19 — LOOK-0001 pushed the keep-key

socratic/cursor-agent found `--available-only` using the status enum alone. Debate reproduced DNS-weak rows surviving the filter with a cold cache, and `--no-check --available-only` as a silent no-op. Rejected baking `https://rdap.nic.co/` — that host does not resolve. Dropped `.co` from `DEFAULT_TLDS` so the default path stays on baked RDAP. Rejected deleting get-/hq- affixes: existing generate tests require them and GENERIC only punishes exact SLDs.
