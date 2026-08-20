from domain_forge.generate import generate
from domain_forge.parse import tokens_from_seed


def test_eidos_includes_core_names() -> None:
    rows = generate("eidos", tlds=("com", "ai"))
    names = {r.domain for r in rows}
    assert "eidos.com" in names
    assert "eidos.ai" in names
    assert "geteidos.com" in names
    assert "eidoshq.com" in names


def test_two_word_seed_joins_and_hyphenates() -> None:
    rows = generate("north star", tlds=("com",))
    names = {r.domain for r in rows}
    assert "northstar.com" in names
    assert "north-star.com" in names


def test_domain_seed_uses_sld() -> None:
    assert tokens_from_seed("eidos.ai") == ["eidos"]
    names = {r.domain for r in generate("eidos.ai", tlds=("com",))}
    assert "eidos.com" in names


def test_generate_is_deterministic() -> None:
    a = [r.domain for r in generate("eidos agi", tlds=("com", "ai"))]
    b = [r.domain for r in generate("eidos agi", tlds=("com", "ai"))]
    assert a == b


def test_no_invalid_labels() -> None:
    for row in generate("eidos agi!!", tlds=("com", "io")):
        assert row.domain == f"{row.sld}.{row.tld}"
        assert "--" not in row.sld
        assert not row.sld.startswith("-")
        assert not row.sld.endswith("-")


def test_os_pivot_adds_morphs() -> None:
    names = {r.domain for r in generate("prim", tlds=("com",), pivot="os")}
    assert "primos.com" in names
    assert "prim-os.com" in names
    assert "osprim.com" in names
    assert "primux.com" in names
    assert "primix.com" in names
    assert "primcore.com" in names
    assert "primsys.com" in names
    assert "goprim.com" in names


def test_os_token_auto_pivots() -> None:
    names = {r.domain for r in generate("prim os", tlds=("com",))}
    assert "primos.com" in names
    assert "primux.com" in names


def test_no_os_morphs_without_pivot() -> None:
    names = {r.domain for r in generate("eidos", tlds=("com",))}
    assert "eidosux.com" not in names
    assert "eidoscore.com" not in names
