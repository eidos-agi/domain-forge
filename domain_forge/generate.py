"""Deterministic alternative-domain generation.

The point is not volume. The point is names a human might actually say out
loud. Prefixes/suffixes are capped so we don't emit geteidoshqstudio.com.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain_forge.parse import is_valid_sld, join_domain, tokens_from_seed
from domain_forge.tlds import DEFAULT_TLDS

PREFIXES = ("get", "try", "use", "go", "hey", "run")
SUFFIXES = ("hq", "lab", "labs", "app", "kit", "run", "os", "works")
MAX_SLD_LEN = 18


@dataclass(frozen=True)
class Generated:
    domain: str
    sld: str
    tld: str
    strategy: str


def _devowel(sld: str) -> str:
    if not sld:
        return sld
    rest = "".join(ch for ch in sld[1:] if ch not in "aeiou")
    out = sld[0] + rest
    return out if out != sld else ""


def _sld_candidates(tokens: list[str]) -> list[tuple[str, str]]:
    """Return (sld, strategy) pairs, first-wins order, later filtered."""
    out: list[tuple[str, str]] = []
    seen: set[str] = set()

    def add(sld: str, strategy: str) -> None:
        sld = sld.lower()
        if not sld or sld in seen:
            return
        if len(sld) > MAX_SLD_LEN or len(sld) < 2:
            return
        if not is_valid_sld(sld):
            return
        seen.add(sld)
        out.append((sld, strategy))

    joined = "".join(tokens)
    add(joined, "join")
    if len(tokens) > 1:
        add("-".join(tokens), "hyphen")
        add(tokens[0], "first")
        add(tokens[-1], "last")
        add("".join(t[0] for t in tokens[:-1]) + tokens[-1], "initials")
        add(tokens[-1] + tokens[0], "swap")
        a, b = tokens[0], tokens[-1]
        add(a[:4] + b, "blend")
        add(a + b[:4], "blend")
        add(a[:3] + b[:3], "blend")

    first = tokens[0]
    add(first, "exact")
    dropped = _devowel(joined)
    if dropped:
        add(dropped, "devowel")
    dropped_first = _devowel(first)
    if dropped_first:
        add(dropped_first, "devowel")

    # Prefix/suffix only on the shortest honest stems.
    stems = [joined, first]
    if len(tokens) > 1:
        stems.append(tokens[-1])
    for stem in stems:
        if 3 <= len(stem) <= 10:
            for prefix in PREFIXES:
                add(prefix + stem, "prefix")
            for suffix in SUFFIXES:
                add(stem + suffix, "suffix")

    return out


def generate(
    seed: str,
    tlds: tuple[str, ...] | list[str] = DEFAULT_TLDS,
    limit: int | None = None,
) -> list[Generated]:
    tokens = tokens_from_seed(seed)
    tld_list = tuple(t.lower().lstrip(".") for t in tlds if t.strip())
    if not tld_list:
        raise ValueError("no TLDs")

    rows: list[Generated] = []
    seen: set[str] = set()
    for sld, strategy in _sld_candidates(tokens):
        for tld in tld_list:
            domain = join_domain(sld, tld)
            if domain in seen:
                continue
            seen.add(domain)
            rows.append(Generated(domain=domain, sld=sld, tld=tld, strategy=strategy))

    if limit is not None:
        return rows[: max(0, limit)]
    return rows
