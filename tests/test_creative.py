from domain_forge.creative import invent


def test_prim_invents_real_sounding_names() -> None:
    names = {sld for sld, _strategy in invent("prim", pivot="os")}
    assert "prism" in names
    assert "primus" in names
    assert "prima" in names
    assert "primora" in names
    assert "imprimis" in names
    assert "prym" in names
    assert "primnova" in names
    assert "goprim" not in names
    assert "primkit" not in names


def test_invent_is_deterministic() -> None:
    assert invent("prim", pivot="os") == invent("prim", pivot="os")
