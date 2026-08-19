"""Generate → score → (optional) availability. The whole harness in one call."""

from __future__ import annotations

from domain_forge.check import Fetcher, check_many
from domain_forge.generate import generate
from domain_forge.models import Candidate, RunResult
from domain_forge.score import score_domain
from domain_forge.tlds import DEFAULT_TLDS


def rank_candidates(
    seed: str,
    *,
    tlds: tuple[str, ...] | list[str] = DEFAULT_TLDS,
    limit: int = 20,
) -> tuple[int, list[Candidate]]:
    generated = generate(seed, tlds=tlds, limit=None)
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
    # Among equal love, shorter SLD first: eidos.com before eidoskit.com.
    scored.sort(key=lambda c: (-c.love.love, len(c.sld), c.domain))
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
) -> RunResult:
    generated_n, ranked = rank_candidates(seed, tlds=tlds, limit=limit)
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
        if available_only:
            ranked = [
                c
                for c in ranked
                if c.availability is not None and c.availability.status == "available"
            ]
    return RunResult(
        seed=seed,
        generated=generated_n,
        returned=len(ranked),
        checked=check,
        candidates=ranked,
    )
