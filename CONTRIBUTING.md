# Contributing to domain-forge

## Quick start

```bash
git clone https://github.com/eidos-agi/domain-forge.git
cd domain-forge
pip install -e ".[dev]"
pytest
ruff check .
ruff format .
```

## Rules

- Keep runtime dependencies at zero unless the alternative is a lie.
- Do not add a register/buy command.
- If you change love weights, change the tests that pin ordering (`.com` > `.xyz`, concat > hyphen, generic penalty).
- `--help` is the schema. Update the skill only after `--help` is true.

## Pull requests

One change per PR. Include tests. No secrets.
