# DOMAIN_RULES

World-facts about naming and the domain name system, not choices we made.

- id: DR-001
  world_fact: A domain is registered or it is not, at a registry, independent of whether DNS answers.
  rule: Availability must come from a registry protocol (RDAP) when one exists. DNS is a weak fallback and must be labelled weak.
  provenance:
    established: 2026-08-19
    by: grok
    reason: NXDOMAIN on a registered-but-dark name would lie and say available.
  blast_radius: check.py, CLI `check`/`run`, any agent that prints "available"
  current_encoding: domain_forge/check.py
  failure_signature: Report `available` for a name that WHOIS/RDAP shows as registered because it has no NS records.
  enforcement: tests/test_check.py mocks RDAP 200/404; DNS path asserts confidence=weak; tests/test_pipeline.py drops DNS-weak and unknown from --available-only; DEFAULT_TLDS subset of BAKED_RDAP
  last_validated:
    date: 2026-08-19
    by: grok
    method: live Verisign google.com=200, fake .com=404
  status: active

- id: DR-002
  world_fact: People remember short, sayable, spellable names ending in a TLD they already understand.
  rule: Love is a radio test plus TLD trust, not uniqueness in a trademark database and not token-probability from a model.
  provenance:
    established: 2026-08-19
    by: grok
    reason: The product question was "how much people will love them."
  blast_radius: score.py, CLI `score`/`suggest`/`run`
  current_encoding: domain_forge/score.py
  failure_signature: `cloud.com` outranks `eidos.com`, or `eidos.xyz` outranks `eidos.com`.
  enforcement: tests/test_score.py
  last_validated:
    date: 2026-08-19
    by: grok
    method: unit tests on hyphen, xyz, generic, eidos.com floor
  status: active

- id: DR-003
  world_fact: Registering a domain spends money and is hard to undo.
  rule: This tool must not register, cart, or transfer names.
  provenance:
    established: 2026-08-19
    by: grok
    reason: Agent loops with purchase paths eventually purchase.
  blast_radius: CLI surface, README, skill safety section
  current_encoding: no register subcommand in cli.py; GUARD-001
  failure_signature: A `register` command or registrar POST exists in the tree.
  enforcement: grep for register/purchase in CLI help tests via doctor detail "no — check only"
  last_validated:
    date: 2026-08-19
    by: grok
    method: CLI parser has no register command
  status: active
