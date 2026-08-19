# DECISIONS

## D-01: Tool forge with a real CLI
Date: 2026-08-19
Chose: `type: tool` CLI (`domain-forge` / `eidos-domains`)
Over: knowledge-only forge (skills/templates, no software); a separate `eidos-domains` repo
Because: the ask was a harness that generates, scores, and checks. A markdown forge cannot check RDAP. One repo, two bin names.
Risk: forge-init's "no software" guardrail does not apply here; registry must mark `type: tool`.
v2 might reverse this if: naming guidance wants to live as skills and the checker becomes a one-file script.

## D-02: RDAP, not a registrar API
Date: 2026-08-19
Chose: RDAP status codes (200 taken, 404 available) + baked bases + IANA bootstrap
Over: Porkbun/Cloudflare/Namecheap check APIs
Because: no secrets, no Knox round-trip, works for the org's default TLDs today. Registrar APIs are the purchase path we are refusing.
Risk: RDAP 404 is not a cart; premium/reserved names lie. .io is missing from IANA bootstrap — we bake Identity Digital.
v2 might reverse this if: we need premium-price and exact cart availability, which requires a registrar key.

## D-03: Love is a rubric
Date: 2026-08-19
Chose: 0–100 named factors (length, pronounce, spell, tld, clean, radio, wordness)
Over: LLM scoring, trademark APIs, purchase-price as quality
Because: explainable to an agent, deterministic, free, testable. "How much people will love them" has to survive a radio test, not a completion.
Risk: the weights are taste. Generic-word penalty can be wrong for a dictionary brand.
v2 might reverse this if: we get human preference data and re-fit weights.

## D-04: No register command
Date: 2026-08-19
Chose: check-only. No buy/cart/transfer.
Over: Porkbun createDomain behind `--confirm`
Because: an agent with a purchase path will eventually purchase. Domain money is not a loop.
Risk: users expect the last mile. We document the handoff.
v2 might reverse this if: Knox-gated registrar invoke exists and a human is in the loop on every buy.

## D-05: Stdlib only
Date: 2026-08-19
Chose: argparse + urllib, zero runtime deps
Over: typer, httpx, python-whois
Because: foss-forge budget, agent install friction, and WHOIS libraries rot.
Risk: urllib is ugly. Timeouts and redirects are manual.
v2 might reverse this if: we add a registrar client that already pulls in httpx.
