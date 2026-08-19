# GOAL-001 — Generate, score, check

A seed goes in. Ranked alternatives come out. Each row has a love score with named factors. The top rows can be checked against RDAP without registering anything.

Done when `domain-forge run "<seed>" --json` returns candidates with `love`, `grade`, and `availability.status`.
