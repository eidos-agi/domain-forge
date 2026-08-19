"""Agent-first CLI. --json everywhere, no prompts, no registration."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from typing import Any

from domain_forge import __version__
from domain_forge.check import check_many
from domain_forge.parse import split_domain
from domain_forge.pipeline import rank_candidates
from domain_forge.pipeline import run as run_pipeline
from domain_forge.score import score_domain
from domain_forge.tlds import BAKED_RDAP, DEFAULT_TLDS


def _emit(payload: Any, *, json_flag: bool, quiet: bool, tty: bool | None = None) -> None:
    is_tty = sys.stdout.isatty() if tty is None else tty
    if quiet:
        rows = payload
        if isinstance(payload, dict) and "candidates" in payload:
            rows = payload["candidates"]
        if isinstance(rows, list):
            for item in rows:
                if isinstance(item, dict):
                    sys.stdout.write(str(item.get("domain", item)) + "\n")
                else:
                    sys.stdout.write(str(item) + "\n")
        else:
            sys.stdout.write(json.dumps(payload, sort_keys=True, default=str) + "\n")
        return
    if json_flag or not is_tty:
        sys.stdout.write(json.dumps(payload, sort_keys=True, default=str) + "\n")
        return
    _print_human(payload)


def _row_avail(row: dict[str, Any]) -> str:
    avail = row.get("availability")
    if isinstance(avail, dict):
        return str(avail.get("status", ""))
    return ""


def _print_table(rows: list[dict[str, Any]]) -> None:
    sys.stdout.write(f"{'LOVE':>4}  {'GRD':<3}  {'AVAIL':<10}  DOMAIN\n")
    for row in rows:
        love = row.get("love", "")
        grade = str(row.get("grade", ""))
        domain = row.get("domain")
        sys.stdout.write(f"{str(love):>4}  {grade:<3}  {_row_avail(row):<10}  {domain}\n")


def _print_human(payload: Any) -> None:
    if isinstance(payload, dict) and "candidates" in payload:
        sys.stdout.write(
            f"seed={payload.get('seed')} generated={payload.get('generated')} "
            f"returned={payload.get('returned')} checked={payload.get('checked')}\n"
        )
        _print_table(list(payload["candidates"]))
        return
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        if "domain" in payload[0]:
            _print_table(payload)
            return
    sys.stdout.write(json.dumps(payload, sort_keys=True, indent=2, default=str) + "\n")


def _parse_tlds(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return DEFAULT_TLDS
    parts = tuple(p.strip().lower().lstrip(".") for p in raw.split(",") if p.strip())
    if not parts:
        raise ValueError("no TLDs in --tlds")
    return parts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="domain-forge",
        description=(
            "Generate alternative domains, score how much people will love them, "
            "and check registry availability via RDAP. Does not register domains."
        ),
    )
    parser.add_argument("--version", action="version", version=f"domain-forge {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_out(p: argparse.ArgumentParser) -> None:
        p.add_argument("--json", action="store_true", help="JSON output (default when piped)")
        p.add_argument("--quiet", action="store_true", help="One domain per line")

    suggest = sub.add_parser("suggest", help="Generate alternative domains for a seed name")
    suggest.add_argument("seed", help="Brand, words, or an existing domain")
    suggest.add_argument("--tlds", default=",".join(DEFAULT_TLDS), help="Comma-separated TLDs")
    suggest.add_argument("--limit", type=int, default=40, help="Max candidates after scoring")
    add_out(suggest)

    score = sub.add_parser("score", help="Score domains for how much people will love them")
    score.add_argument("domains", nargs="+", help="Fully qualified domains")
    add_out(score)

    check = sub.add_parser("check", help="Check RDAP availability (never registers)")
    check.add_argument("domains", nargs="+", help="Fully qualified domains")
    check.add_argument("--timeout", type=float, default=8.0)
    add_out(check)

    run = sub.add_parser("run", help="Generate, score, then check availability")
    run.add_argument("seed", help="Brand, words, or an existing domain")
    run.add_argument("--tlds", default=",".join(DEFAULT_TLDS))
    run.add_argument("--limit", type=int, default=15, help="Max candidates to score/check")
    run.add_argument("--no-check", action="store_true", help="Skip RDAP (offline)")
    run.add_argument(
        "--available-only",
        action="store_true",
        help="After checking, keep only RDAP-available names",
    )
    run.add_argument("--timeout", type=float, default=8.0)
    add_out(run)

    doctor = sub.add_parser("doctor", help="Runtime health")
    add_out(doctor)
    return parser


def cmd_suggest(args: argparse.Namespace) -> dict[str, Any]:
    tlds = _parse_tlds(args.tlds)
    generated_n, ranked = rank_candidates(args.seed, tlds=tlds, limit=args.limit)
    return {
        "seed": args.seed,
        "generated": generated_n,
        "returned": len(ranked),
        "checked": False,
        "candidates": [c.to_dict() for c in ranked],
    }


def cmd_score(args: argparse.Namespace) -> list[dict[str, Any]]:
    rows = []
    for name in args.domains:
        love = score_domain(name)
        rows.append(love.to_dict())
    return rows


def cmd_check(args: argparse.Namespace) -> list[dict[str, Any]]:
    for name in args.domains:
        split_domain(name)  # fail fast on junk
    reports = check_many(list(args.domains), timeout=args.timeout)
    return [r.to_dict() for r in reports]


def cmd_run(args: argparse.Namespace) -> dict[str, Any]:
    tlds = _parse_tlds(args.tlds)
    result = run_pipeline(
        args.seed,
        tlds=tlds,
        limit=args.limit,
        check=not args.no_check,
        available_only=args.available_only,
        timeout=args.timeout,
    )
    return result.to_dict()


def cmd_doctor(_args: argparse.Namespace) -> dict[str, Any]:
    from domain_forge.generate import generate
    from domain_forge.score import score_domain as sc

    checks = []
    ok = True
    try:
        rows = generate("eidos", tlds=("com", "ai"))
        has = {r.domain for r in rows}
        good = "eidos.com" in has and "eidos.ai" in has
        checks.append({"name": "generate_eidos", "ok": good, "detail": f"{len(rows)} names"})
        ok = ok and good
    except Exception as exc:  # noqa: BLE001 — doctor must not crash
        checks.append({"name": "generate_eidos", "ok": False, "detail": str(exc)})
        ok = False
    try:
        love = sc("eidos.com")
        good = love.love >= 70
        checks.append({"name": "score_eidos_com", "ok": good, "detail": f"love={love.love}"})
        ok = ok and good
    except Exception as exc:  # noqa: BLE001
        checks.append({"name": "score_eidos_com", "ok": False, "detail": str(exc)})
        ok = False
    checks.append(
        {
            "name": "baked_rdap",
            "ok": "com" in BAKED_RDAP and "ai" in BAKED_RDAP,
            "detail": ",".join(sorted(BAKED_RDAP)),
        }
    )
    checks.append({"name": "registers_domains", "ok": True, "detail": "no - check only"})
    return {"ok": ok, "version": __version__, "checks": checks}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    try:
        if args.command == "suggest":
            payload = cmd_suggest(args)
        elif args.command == "score":
            payload = cmd_score(args)
        elif args.command == "check":
            payload = cmd_check(args)
        elif args.command == "run":
            payload = cmd_run(args)
        elif args.command == "doctor":
            payload = cmd_doctor(args)
        else:
            parser.error(f"unknown command {args.command}")
            return 2
    except ValueError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.stderr.write("Hint: pass a seed or a fully-qualified domain like eidos.ai\n")
        return 2

    json_flag = bool(getattr(args, "json", False))
    quiet = bool(getattr(args, "quiet", False))
    _emit(payload, json_flag=json_flag, quiet=quiet)
    if args.command == "doctor" and isinstance(payload, dict) and not payload.get("ok"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
