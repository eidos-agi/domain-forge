from domain_forge.score import score_domain


def test_com_beats_xyz_for_same_sld() -> None:
    com = score_domain("eidos.com")
    xyz = score_domain("eidos.xyz")
    assert com.love > xyz.love


def test_hyphen_loses_to_concat() -> None:
    concat = score_domain("northstar.com")
    hyphen = score_domain("north-star.com")
    assert concat.love > hyphen.love


def test_digits_and_junk_score_low() -> None:
    junk = score_domain("xqztpvqqq.xyz")
    digits = score_domain("eidos123.com")
    good = score_domain("eidos.com")
    assert junk.love < good.love
    assert digits.love < good.love
    assert junk.grade in {"D", "F", "C"}


def test_generic_sld_is_penalized() -> None:
    generic = score_domain("cloud.com")
    brand = score_domain("eidos.com")
    assert generic.love < brand.love


def test_eidos_com_is_lovable() -> None:
    love = score_domain("eidos.com")
    assert love.love >= 70
    assert love.say_on_a_call is True
    assert love.must_spell is False
    names = {f.name for f in love.factors}
    assert names == {"length", "pronounce", "spell", "tld", "clean", "radio", "wordness"}


def test_short_clean_ai_is_strong() -> None:
    love = score_domain("eidos.ai")
    assert love.love >= 68
    assert love.tld == "ai"
