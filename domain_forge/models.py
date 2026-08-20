"""Wire types for domain-forge. Keep JSON keys stable — agents parse these."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


def _strip_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _strip_none(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [_strip_none(v) for v in value]
    return value


@dataclass(frozen=True)
class Factor:
    name: str
    score: int
    max: int
    why: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LoveScore:
    domain: str
    sld: str
    tld: str
    love: int
    grade: str
    factors: tuple[Factor, ...]
    must_spell: bool
    say_on_a_call: bool
    why: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["factors"] = [f.to_dict() for f in self.factors]
        return payload


@dataclass(frozen=True)
class Availability:
    domain: str
    status: str
    source: str
    confidence: str
    http_status: int | None = None
    rdap_url: str | None = None
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return _strip_none(asdict(self))


@dataclass(frozen=True)
class Candidate:
    domain: str
    sld: str
    tld: str
    strategy: str
    love: LoveScore
    availability: Availability | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "domain": self.domain,
            "sld": self.sld,
            "tld": self.tld,
            "strategy": self.strategy,
            "love": self.love.love,
            "grade": self.love.grade,
            "must_spell": self.love.must_spell,
            "say_on_a_call": self.love.say_on_a_call,
            "why": self.love.why,
            "factors": [f.to_dict() for f in self.love.factors],
        }
        if self.availability is not None:
            payload["availability"] = self.availability.to_dict()
        return payload


@dataclass
class RunResult:
    seed: str
    generated: int
    returned: int
    checked: bool
    candidates: list[Candidate] = field(default_factory=list)
    unknown: int = 0
    filtered_out: int = 0
    pivot: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "pivot": self.pivot,
            "generated": self.generated,
            "returned": self.returned,
            "checked": self.checked,
            "unknown": self.unknown,
            "filtered_out": self.filtered_out,
            "candidates": [c.to_dict() for c in self.candidates],
        }
