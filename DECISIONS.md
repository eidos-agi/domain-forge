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

## D-09: Love is punch + soul, not cleanliness
Date: 2026-08-19
Chose: rewrite `score.py` — punch, radio, clean, tld(10), template(24), soul(24)
Over: length+pronounce+spell+tld(15)+clean+radio+wordness, which scored goprim.com 95 and prim.com 89
Because: Daniel said the scoring method was poor. A checklist of "not ugly" is not "people will love this." One-syllable 4-letter brands are the ones people remember. Template glue is the opposite of love. `.com` must not paper over `kit`/`get`/`-ax`.
Risk: weights are still taste. Tests pin the comparisons that were wrong: prim>goprim, primora>primkit, primdawn>primax, imprimis>getprim.
v2 might reverse this if: a preference study says people actually like get- names.

## D-08: Invent names, do not glue prefixes
Date: 2026-08-19
Chose: `creative.invent` — Latin inflections, prism-style near-words, coined tails, OS metaphors. On `--pivot os`, skip get/try/kit entirely.
Over: more suffixes (hq, kit, run) and more prefixes (goprim)
Because: Daniel said the OS run was still not right and to be more creative. goprim.com is not a name. Primora / Prism / Imprimis / Primdawn could go on a boot screen.
Risk: many 7-letter coined .coms are already taken; the invention still earns its keep on .ai/.io/.dev and a few .coms (osprima, primdawn, lumenprim).
v2 might reverse this if: a true namer model is allowed in-process without breaking stdlib-only.

## D-07: OS pivot is an explicit morph family
Date: 2026-08-19
Chose: `--pivot os` (also auto if the seed contains the token `os`)
Over: always emitting primux-style names; an LLM name dump
Because: pivoting prim into a Prim OS is a product decision, not a generic prefix. Morphs: `{stem}os`, `{stem}-os`, `os{stem}`, `{stem}ux`, `{stem}ix`, `{stem}core`, `{stem}sys`. Rank those above get-/try- without changing the 0-100 love number.
Risk: more names, still not a cart. `primos.*` may all be taken; the morphs exist so the run is not just `goprim.com`.
v2 might reverse this if: more pivots (cloud, lab) want the same gate.

## D-06: Default TLDs are a subset of baked RDAP
Date: 2026-08-19
Chose: drop `.co` from `DEFAULT_TLDS`
Over: baking `https://rdap.nic.co/` (does not resolve); leaving `.co` on the default list and hoping IANA bootstrap is up
Because: LOOK-0001 showed `--available-only` plus a default TLD without a baked floor turns DNS NXDOMAIN into "available." The baked table exists for the down case.
Risk: people who want `.co` must pass `--tlds co` and accept weak DNS unless IANA is reachable.
v2 might reverse this if: `.co` gets a working RDAP base we can bake.

## D-05: Stdlib only
Date: 2026-08-19
Chose: argparse + urllib, zero runtime deps
Over: typer, httpx, python-whois
Because: foss-forge budget, agent install friction, and WHOIS libraries rot.
Risk: urllib is ugly. Timeouts and redirects are manual.
v2 might reverse this if: we add a registrar client that already pulls in httpx.
