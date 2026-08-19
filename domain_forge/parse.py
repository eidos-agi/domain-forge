"""ASCII domain parsing. v1 does not do IDN / punycode / multi-label TLDs."""

from __future__ import annotations

import re

LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
TOKEN_RE = re.compile(r"[a-z0-9]+")


def normalize_domain(raw: str) -> str:
    name = raw.strip().lower().rstrip(".")
    if name.startswith("http://") or name.startswith("https://"):
        name = name.split("://", 1)[1]
    if "/" in name:
        name = name.split("/", 1)[0]
    if name.startswith("www."):
        name = name[4:]
    return name


def split_domain(raw: str) -> tuple[str, str]:
    name = normalize_domain(raw)
    if "." not in name:
        raise ValueError(f"not a domain (missing TLD): {raw!r}")
    sld, tld = name.rsplit(".", 1)
    if not sld or not tld:
        raise ValueError(f"not a domain: {raw!r}")
    if not LABEL_RE.match(sld):
        raise ValueError(f"invalid SLD: {sld!r}")
    if not re.fullmatch(r"[a-z]{2,24}", tld):
        raise ValueError(f"invalid TLD: {tld!r}")
    return sld, tld


def is_valid_sld(sld: str) -> bool:
    return bool(LABEL_RE.match(sld)) and "--" not in sld


def tokens_from_seed(seed: str) -> list[str]:
    text = seed.strip().lower()
    if not text:
        raise ValueError("seed is empty")
    # If the seed is already a domain, prefer its SLD tokens.
    if "." in text and " " not in text:
        try:
            sld, _tld = split_domain(text)
            text = sld.replace("-", " ")
        except ValueError:
            pass
    tokens = TOKEN_RE.findall(text)
    tokens = [t for t in tokens if t]
    if not tokens:
        raise ValueError(f"seed has no usable tokens: {seed!r}")
    return tokens


def join_domain(sld: str, tld: str) -> str:
    return f"{sld}.{tld}"
