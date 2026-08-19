import json

from domain_forge.cli import main
from domain_forge.pipeline import run
from domain_forge.tlds import BAKED_RDAP


def test_suggest_json(capsys) -> None:
    code = main(["suggest", "eidos", "--tlds", "com,ai", "--limit", "8", "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["seed"] == "eidos"
    assert payload["returned"] <= 8
    domains = [c["domain"] for c in payload["candidates"]]
    assert any(d.endswith(".com") or d.endswith(".ai") for d in domains)
    assert payload["candidates"][0]["love"] >= payload["candidates"][-1]["love"]


def test_score_json(capsys) -> None:
    code = main(["score", "eidos.com", "eidos.xyz", "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["domain"] == "eidos.com"
    assert payload[0]["love"] > payload[1]["love"]


def test_run_offline(capsys) -> None:
    code = main(["run", "eidos", "--no-check", "--limit", "5", "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["checked"] is False
    assert len(payload["candidates"]) == 5
    assert "availability" not in payload["candidates"][0]


def test_bad_domain_exits_2(capsys) -> None:
    code = main(["score", "not a domain", "--json"])
    assert code == 2
    err = capsys.readouterr().err
    assert "Error:" in err


def test_doctor_ok(capsys) -> None:
    code = main(["doctor", "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    by_name = {c["name"]: c for c in payload["checks"]}
    assert by_name["baked_rdap"]["ok"] is True
    assert by_name["registers_domains"]["ok"] is True


def test_doctor_fails_when_baked_rdap_missing(monkeypatch, capsys) -> None:
    monkeypatch.setattr("domain_forge.cli.BAKED_RDAP", {})
    monkeypatch.setattr("domain_forge.cli.DEFAULT_TLDS", ("com",))
    code = main(["doctor", "--json"])
    assert code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    baked = next(c for c in payload["checks"] if c["name"] == "baked_rdap")
    assert baked["ok"] is False


def test_no_check_available_only_exits_2(capsys) -> None:
    code = main(["run", "eidos", "--no-check", "--available-only", "--json"])
    assert code == 2
    err = capsys.readouterr().err
    assert "available-only" in err.lower()


def test_pipeline_check_uses_fetcher() -> None:
    def fetch(url: str, timeout: float) -> tuple[int, bytes, str]:
        if url.endswith("eidos.com"):
            return 200, b"{}", url
        return 404, b"{}", url

    result = run(
        "eidos",
        tlds=("com",),
        limit=5,
        check=True,
        fetch=fetch,
        pause=0,
    )
    assert result.checked is True
    assert result.candidates
    statuses = {c.availability.status for c in result.candidates if c.availability}
    assert "taken" in statuses or "available" in statuses
    assert BAKED_RDAP["com"]
