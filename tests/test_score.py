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
    assert names == {"punch", "radio", "clean", "tld", "template", "soul"}


def test_short_clean_ai_is_strong() -> None:
    love = score_domain("eidos.ai")
    assert love.love >= 68
    assert love.tld == "ai"


def test_brand_beats_startup_prefix() -> None:
    brand = score_domain("prim.com")
    glue = score_domain("goprim.com")
    assert brand.love > glue.love
    assert brand.love >= 80
    assert glue.love < 75


def test_one_syllable_is_punchy_not_a_defect() -> None:
    love = score_domain("prim.com")
    punch = next(f for f in love.factors if f.name == "punch")
    assert punch.score == 20
    assert love.say_on_a_call is True


def test_invented_name_beats_kit_glue() -> None:
    invented = score_domain("primora.com")
    kit = score_domain("primkit.com")
    assert invented.love > kit.love
    assert kit.love < 70


def test_picture_beats_pharma_tail() -> None:
    dawn = score_domain("primdawn.com")
    ax = score_domain("primax.com")
    assert dawn.love > ax.love


def test_elle_is_coinage_not_a_false_split() -> None:
    soul = next(f for f in score_domain("primelle.com").factors if f.name == "soul")
    assert "lle" not in soul.why
    assert soul.score >= 18


def test_imprimis_beats_getprim() -> None:
    latin = score_domain("imprimis.io")
    prefix = score_domain("getprim.com")
    assert latin.love > prefix.love
