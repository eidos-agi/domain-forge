from pathlib import Path

from domain_forge.cli import _subcommand_names, build_parser, cmd_doctor
from domain_forge.tlds import BAKED_RDAP, DEFAULT_TLDS


def test_parser_has_no_register_command() -> None:
    names = _subcommand_names(build_parser())
    assert "register" not in names
    assert "buy" not in names
    assert names == {"suggest", "score", "check", "run", "doctor"}


def test_doctor_inspects_parser_surface() -> None:
    class Args:
        pass

    payload = cmd_doctor(Args())
    row = next(c for c in payload["checks"] if c["name"] == "registers_domains")
    assert row["ok"] is True
    assert "suggest" in row["detail"]


def test_check_module_is_get_only() -> None:
    text = Path("domain_forge/check.py").read_text()
    assert 'method="GET"' in text
    assert "POST" not in text


def test_default_tlds_have_baked_rdap() -> None:
    missing = [t for t in DEFAULT_TLDS if t not in BAKED_RDAP]
    assert missing == []
