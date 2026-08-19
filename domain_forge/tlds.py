"""TLD love weights and baked RDAP bases.

IANA bootstrap is the live source. These tables are the offline floor so
`suggest`/`score` work with no network, and so a missing bootstrap fetch
does not invent a .com checker.
"""

from __future__ import annotations

# How much people still treat the TLD as a real address, not a punchline.
# .com remains the one you can say on a podcast without explaining it.
TLD_LOVE: dict[str, int] = {
    "com": 15,
    "ai": 13,
    "io": 11,
    "dev": 10,
    "app": 10,
    "org": 9,
    "co": 8,
    "net": 7,
    "me": 7,
    "so": 6,
    "gg": 6,
    "sh": 5,
    "xyz": 3,
    "info": 2,
    "biz": 1,
}

DEFAULT_TLDS: tuple[str, ...] = ("com", "ai", "io", "dev", "app", "co", "org")

# Baked RDAP bases (trailing slash). Overlay IANA bootstrap when fetched.
# .io is not in the IANA DNS bootstrap as of 2026-08; Identity Digital answers it.
BAKED_RDAP: dict[str, str] = {
    "com": "https://rdap.verisign.com/com/v1/",
    "net": "https://rdap.verisign.com/net/v1/",
    "org": "https://rdap.publicinterestregistry.org/rdap/",
    "ai": "https://rdap.identitydigital.services/rdap/",
    "info": "https://rdap.identitydigital.services/rdap/",
    "io": "https://rdap.identitydigital.services/rdap/",
    "app": "https://pubapi.registry.google/rdap/",
    "dev": "https://pubapi.registry.google/rdap/",
    "xyz": "https://rdap.centralnic.com/xyz/",
}

IANA_RDAP_DNS = "https://data.iana.org/rdap/dns.json"


def tld_love_points(tld: str) -> int:
    return TLD_LOVE.get(tld.lower(), 5)
