# OBSERVATIONS

## 2026-08-19 — Discipline started day 1
At stake: v2 being able to tell whether the love rubric and RDAP mapping were guesses or measured.
Noted: `.io` is not in the IANA RDAP DNS bootstrap; `rdap.identitydigital.services` answers `github.io` with a real domain object and 404s a fake. `.com` Verisign 200/404 behaves as advertised. `rdap.org` timed out on a missing .io name and is not a reliable client bootstrap.

## 2026-08-19 — Google registry path
`https://pubapi.registry.google/rdap/domain/{name}` returns 200 for `pages.dev` / `google.dev` and 404 for a fake `.dev`. The older `rdap.nic.google` guess is unnecessary.
