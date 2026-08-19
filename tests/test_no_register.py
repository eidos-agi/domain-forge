from domain_forge.cli import build_parser, cmd_doctor


def test_parser_has_no_register_command() -> None:
    parser = build_parser()
    names = []
    for action in parser._subparsers._group_actions:  # noqa: SLF001 — argparse has no public map
        if getattr(action, "choices", None):
            names.extend(action.choices.keys())
    assert "register" not in names
    assert "buy" not in names
    assert set(names) == {"suggest", "score", "check", "run", "doctor"}


def test_doctor_states_check_only() -> None:
    class Args:
        pass

    payload = cmd_doctor(Args())
    row = next(c for c in payload["checks"] if c["name"] == "registers_domains")
    assert row["ok"] is True
    assert "no" in row["detail"].lower()
