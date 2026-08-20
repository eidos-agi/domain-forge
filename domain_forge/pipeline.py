"""Generate → score → (optional) availability. The whole harness in one call."""

from __future__ import annotations

from domain_forge.check import Fetcher, check_many
from domain_forge.generate import generate, resolve_pivot
from domain_forge.models import Availability, Candidate, RunResult
from domain_forge.parse import tokens_from_seed
from domain_forge.score import score_domain
from domain_forge.tlds import DEFAULT_TLDS

OS_PRODUCT_STRATEGIES = frozenset(
    {"os", "os-hyphen", "os-prefix", "ux", "ix", "core", "sys", "os-prefix-brand", "join"}
)


def seed_fit(sld: str, tokens: list[str], strategy: str, pivot: str | None) -> int:
    """Prefer the product the human named over get-/try- spam.

    Does not change the 0-100 love number. Tie-break only.
    """
    stem = tokens[0]
    if pivot == "os":
        products = {
            stem + "os",
            stem + "ux",
            stem + "ix",
            stem + "core",
            stem + "sys",
            "os" + stem,
        }
        if sld in products:
            return 5
        if sld == stem + "-os":
            return 3
        if sld == stem:
            return 4
        if strategy in OS_PRODUCT_STRATEGIES:
            return 3
        if strategy == "prefix":
            return 0
        return 1
    joined = "".join(tokens)
    if sld == joined:
        return 4
    if sld == stem:
        return 3
    if strategy == "prefix":
        return 0
    return 1


def is_registry_available(avail: Availability | None) -> bool:
    """RDAP 404 only. DNS NXDOMAIN is labelled available/weak and must not pass."""
    return (
        avail is not None
        and avail.status == "available"
        and avail.source == "rdap"
        and avail.confidence == "registry"
    )


def rank_candidates(
    seed: str,
    *,
    tlds: tuple[str, ...] | list[str] = DEFAULT_TLDS,
    limit: int = 20,
    pivot: str | None = None,
) -> tuple[int, list[Candidate]]:
    tokens = tokens_from_seed(seed)
    resolved = resolve_pivot(tokens, pivot)
    generated = generate(seed, tlds=tlds, limit=None, pivot=resolved)
    scored = [
        Candidate(
            domain=row.domain,
            sld=row.sld,
            tld=row.tld,
            strategy=row.strategy,
            love=score_domain(row.domain),
        )
        for row in generated
    ]
    scored.sort(
        key=lambda c: (
            -c.love.love,
            -seed_fit(c.sld, tokens, c.strategy, resolved),
            len(c.sld),
            c.domain,
        )
    )
    return len(generated), scored[: max(0, limit)]


def run(
    seed: str,
    *,
    tlds: tuple[str, ...] | list[str] = DEFAULT_TLDS,
    limit: int = 20,
    check: bool = True,
    available_only: bool = False,
    fetch: Fetcher | None = None,
    timeout: float = 8.0,
    pause: float = 0.12,
    pivot: str | None = None,
) -> RunResult:
    if available_only and not check:
        raise ValueError("--available-only requires a registry check; drop --no-check")
    generated_n, ranked = rank_candidates(seed, tlds=tlds, limit=limit, pivot=pivot)
    unknown = 0
    filtered_out = 0
    if check and ranked:
        reports = check_many(
            [c.domain for c in ranked],
            fetch=fetch,
            timeout=timeout,
            pause=pause,
        )
        by_name = {r.domain: r for r in reports}
        ranked = [
            Candidate(
                domain=c.domain,
                sld=c.sld,
                tld=c.tld,
                strategy=c.strategy,
                love=c.love,
                availability=by_name.get(c.domain),
            )
            for c in ranked
        ]
        unknown = sum(
            1 for c in ranked if c.availability is None or c.availability.status == "unknown"
        )
        if available_only:
            kept = [c for c in ranked if is_registry_available(c.availability)]
            filtered_out = len(ranked) - len(kept)
            ranked = kept
    return RunResult(
        seed=seed,
        generated=generated_n,
        returned=len(ranked),
        checked=check,
        candidates=ranked,
        unknown=unknown,
        filtered_out=filtered_out,
        pivot=resolve_pivot(tokens_from_seed(seed), pivot),
    )
