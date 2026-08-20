"""TLD love weights and baked RDAP bases.

IANA bootstrap is the live source. These tables are the offline floor so
`suggest`/`score` work with no network, and so a missing bootstrap fetch
does not invent a .com checker.
"""

from __future__ import annotations

# How much people still treat the TLD as a real address, not a punchline.
# .com remains the one you can say on a podcast without explaining it.
# Max 10. A .com must not rescue a glue name.
TLD_LOVE: dict[str, int] = {
    "com": 10,
    "ai": 9,
    "io": 7,
    "dev": 7,
    "app": 7,
    "org": 6,
    "co": 5,
    "net": 5,
    "me": 5,
    "so": 4,
    "gg": 4,
    "sh": 4,
    "xyz": 2,
    "info": 1,
    "biz": 1,
}

# Default TLDs must be a subset of BAKED_RDAP. .co has no working baked
# RDAP base (rdap.nic.co does not resolve); do not invent a DNS checker.
DEFAULT_TLDS: tuple[str, ...] = ("com", "ai", "io", "dev", "app", "org")

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
