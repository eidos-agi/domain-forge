"""Availability via RDAP, with DNS-over-HTTPS as a weak fallback.

RDAP 200 = registered. RDAP 404 = not in the registry (treat as available).
That is the industry signal, not a purchase guarantee — reserved/premium
names can 404 and still refuse to sell.

DNS NXDOMAIN is weaker: a registered name with no records looks empty.
We only use DNS when there is no RDAP server, and we mark confidence=weak.

This module never registers anything.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path

from domain_forge import __version__
from domain_forge.models import Availability
from domain_forge.parse import split_domain
from domain_forge.tlds import BAKED_RDAP, IANA_RDAP_DNS

USER_AGENT = f"domain-forge/{__version__} (+https://github.com/eidos-agi/domain-forge)"
DNS_GOOGLE = "https://dns.google/resolve"
DEFAULT_TIMEOUT = 8.0
DEFAULT_PAUSE = 0.12

Fetcher = Callable[[str, float], tuple[int, bytes, str]]


def _default_fetch(url: str, timeout: float) -> tuple[int, bytes, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/rdap+json, application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            final = str(resp.geturl())
            return int(resp.status), body, final
    except urllib.error.HTTPError as exc:
        body = exc.read() if exc.fp else b""
        return int(exc.code), body, url


def cache_path() -> Path:
    override = os.environ.get("DOMAIN_FORGE_CACHE")
    if override:
        return Path(override) / "rdap-dns.json"
    return Path.home() / ".cache" / "domain-forge" / "rdap-dns.json"


def load_bootstrap(
    fetch: Fetcher | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    now: float | None = None,
) -> dict[str, str]:
    """TLD -> RDAP base URL. Baked first, IANA overlay when fresh/fetchable."""
    mapping = dict(BAKED_RDAP)
    path = cache_path()
    data: dict | None = None
    stamp = now if now is not None else time.time()
    if path.is_file():
        try:
            cached = json.loads(path.read_text())
            age = stamp - float(cached.get("fetched_at", 0))
            if age < 86400:
                data = cached
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            data = None
    if data is None:
        getter = fetch or _default_fetch
        try:
            status, body, _url = getter(IANA_RDAP_DNS, timeout)
        except (OSError, TimeoutError, urllib.error.URLError):
            return mapping
        if status != 200:
            return mapping
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return mapping
        data = {"fetched_at": stamp, "services": payload.get("services", [])}
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data))
        except OSError:
            pass
    for service in data.get("services", []):
        if not isinstance(service, list) or len(service) < 2:
            continue
        tlds, urls = service[0], service[1]
        if not tlds or not urls:
            continue
        base = str(urls[0])
        if not base.endswith("/"):
            base += "/"
        for tld in tlds:
            key = str(tld).lower()
            if key:
                mapping[key] = base
    # Re-apply baked so known working .io etc. win over a missing IANA row.
    mapping.update(BAKED_RDAP)
    return mapping


def rdap_url(domain: str, bootstrap: dict[str, str]) -> str | None:
    _sld, tld = split_domain(domain)
    base = bootstrap.get(tld)
    if not base:
        return None
    return base.rstrip("/") + "/domain/" + domain


def _dns_status(domain: str, fetch: Fetcher, timeout: float) -> str:
    """Return taken|available|unknown from Google DoH NS lookup."""
    url = f"{DNS_GOOGLE}?name={urllib.request.quote(domain)}&type=NS"
    try:
        status, body, _final = fetch(url, timeout)
    except (OSError, TimeoutError, urllib.error.URLError):
        return "unknown"
    if status != 200:
        return "unknown"
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "unknown"
    # DNS RCODE: 0 NOERROR, 3 NXDOMAIN
    rcode = int(payload.get("Status", -1))
    answers = payload.get("Answer") or []
    if rcode == 3:
        return "available"
    if rcode == 0 and answers:
        return "taken"
    return "unknown"


def check_domain(
    raw: str,
    *,
    fetch: Fetcher | None = None,
    bootstrap: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Availability:
    sld, tld = split_domain(raw)
    domain = f"{sld}.{tld}"
    getter = fetch or _default_fetch
    boot = bootstrap if bootstrap is not None else load_bootstrap(fetch=getter, timeout=timeout)
    url = rdap_url(domain, boot)
    if url:
        try:
            status, _body, final = getter(url, timeout)
        except (OSError, TimeoutError, urllib.error.URLError) as exc:
            return Availability(
                domain=domain,
                status="unknown",
                source="rdap",
                confidence="none",
                rdap_url=url,
                detail=f"rdap transport error: {exc}",
            )
        if status == 200:
            return Availability(
                domain=domain,
                status="taken",
                source="rdap",
                confidence="registry",
                http_status=status,
                rdap_url=final or url,
                detail="RDAP 200 - registered",
            )
        if status == 404:
            return Availability(
                domain=domain,
                status="available",
                source="rdap",
                confidence="registry",
                http_status=status,
                rdap_url=final or url,
                detail="RDAP 404 - not in the registry",
            )
        return Availability(
            domain=domain,
            status="unknown",
            source="rdap",
            confidence="none",
            http_status=status,
            rdap_url=final or url,
            detail=f"RDAP HTTP {status}",
        )

    dns = _dns_status(domain, getter, timeout)
    return Availability(
        domain=domain,
        status=dns,
        source="dns",
        confidence="weak" if dns != "unknown" else "none",
        detail="no RDAP server for this TLD; DNS NXDOMAIN is not a registry answer",
    )


def check_many(
    domains: list[str],
    *,
    fetch: Fetcher | None = None,
    bootstrap: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    pause: float = DEFAULT_PAUSE,
    sleeper: Callable[[float], None] = time.sleep,
) -> list[Availability]:
    getter = fetch or _default_fetch
    boot = bootstrap if bootstrap is not None else load_bootstrap(fetch=getter, timeout=timeout)
    rows: list[Availability] = []
    for i, name in enumerate(domains):
        if i:
            sleeper(pause)
        rows.append(check_domain(name, fetch=getter, bootstrap=boot, timeout=timeout))
    return rows
