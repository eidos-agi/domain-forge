"""Love score: would a person want this as the name, not merely tolerate it.

The v1 rubric (length + 2-3 syllables + .com = 95) was a cleanliness
checklist. It scored goprim.com above prim.com and primax.com next to
primora.com. People do not love template glue. They love punchy brands,
real words, and coinages that could go on a boot screen.

Factors still named and bounded. No model.
"""

from __future__ import annotations

import re

from domain_forge.models import Factor, LoveScore
from domain_forge.parse import split_domain
from domain_forge.tlds import tld_love_points
from domain_forge.words import GENERIC, IMAGE, STOPWORDS, WORDS

VOWELS = set("aeiouy")
STARTUP_PREFIXES = ("get", "try", "use", "go", "hey", "run", "my", "the", "we")
GLUE_SUFFIXES = ("hq", "kit", "app", "lab", "labs", "works", "ly", "ify", "demo")
SOFT_OS_SUFFIXES = ("os", "ux", "sys", "core")
JUNK_TAILS = ("ax", "ex", "xy", "qq")
WEAK_TAILS = ("yn", "ea", "el", "en")
NAME_TAILS = ("us", "um", "is", "or", "elle", "ora", "ara", "ova", "ion", "ia")


def _syllables(sld: str) -> int:
    groups = re.findall(r"[aeiouy]+", sld)
    n = len(groups)
    if sld.endswith("e") and n > 1 and not sld.endswith("le"):
        n -= 1
    return max(1, n)


def _raw_cluster(part: str) -> int:
    runs = re.findall(r"[bcdfghjklmnpqrstvwxz]{2,}", part)
    return max((len(r) for r in runs), default=0)


def _consonant_cluster(sld: str) -> int:
    compact = sld.replace("-", "")
    for a, b in _splits(compact):
        if _is_word(a) and _is_word(b):
            return max(_raw_cluster(a), _raw_cluster(b))
    return _raw_cluster(compact)


def _is_word(s: str) -> bool:
    return s in WORDS or s in IMAGE


def _plausible_stem(s: str) -> bool:
    if not (3 <= len(s) <= 6) or s in GENERIC or s in STARTUP_PREFIXES:
        return False
    if _is_word(s):
        return True
    core = s[:-1] if s.endswith("e") else s
    if not core or all(c not in VOWELS for c in core):
        return False
    return any(c in VOWELS for c in s)


def _splits(sld: str) -> list[tuple[str, str]]:
    compact = sld.replace("-", "")
    out: list[tuple[str, str]] = []
    for i in range(2, len(compact) - 1):
        out.append((compact[:i], compact[i:]))
    return out


def _punch(sld: str, syl: int) -> tuple[int, str]:
    n = len(sld)
    # One syllable of 3-6 letters is Apple/Slack/Prim, not a defect.
    if 4 <= n <= 6 and syl <= 2:
        return 20, f"{n} letters, {syl} syllable" + ("" if syl == 1 else "s") + " - punchy"
    if n == 3 and syl == 1:
        return 15, "3-letter punch; some people will ask you to spell it"
    if 7 <= n <= 8 and syl <= 3:
        return 17, f"{n} letters, still a name"
    if 9 <= n <= 10 and syl <= 3:
        return 12, f"{n} letters: getting long"
    if n <= 2:
        return 6, "too tiny; you will spell it every time"
    return 5, f"{n} letters / {syl} syllables: a URL, not a name"


def _radio(sld: str, syl: int, cluster: int, vowel_count: int) -> tuple[int, bool, str]:
    n = len(sld)
    if vowel_count == 0 or cluster >= 4 or any(ch.isdigit() for ch in sld) or n <= 2:
        return 2, True, "fails the radio test - you will have to spell it"
    if syl >= 5:
        return 4, True, "too many beats to say once"
    if syl <= 2 and n <= 10 and "-" not in sld:
        return 12, False, "say it once, they can type it"
    if syl == 3 and n <= 10:
        return 10, False, "three beats, still sayable"
    return 7, False, "mostly sayable"


def _clean(sld: str) -> tuple[int, str]:
    score = 10
    bits: list[str] = []
    if any(ch.isdigit() for ch in sld):
        score -= 6
        bits.append("digits")
    if "-" in sld:
        score -= 7
        bits.append("hyphen")
    if re.search(r"(.)\1\1", sld):
        score -= 3
        bits.append("triple letter")
    if not bits:
        bits.append("clean")
    return max(0, score), ", ".join(bits)


def _template(sld: str) -> tuple[int, str]:
    compact = sld.replace("-", "")
    for prefix in STARTUP_PREFIXES:
        if compact.startswith(prefix) and len(compact) - len(prefix) >= 3:
            return 4, f"startup prefix {prefix}- ; people do not love this"
    for suffix in GLUE_SUFFIXES:
        if compact.endswith(suffix) and compact != suffix and len(compact) > len(suffix) + 2:
            return 6, f"product-suffix -{suffix} ; kit/hq/app is not a name"
    if compact.endswith(JUNK_TAILS):
        return 10, "generator tail (-ax/-ex) - reads as a pharma dump"
    if compact.endswith(WEAK_TAILS) and len(compact) <= 8:
        return 14, "thin coined tail"
    for suffix in SOFT_OS_SUFFIXES:
        # Prefix must be at least 4 letters so "eidos" is not eid+os.
        if compact.endswith(suffix) and len(compact) - len(suffix) >= 4:
            return 16, f"-{suffix} is on-brief for an OS, still a little glue"
    if compact.startswith("os") and len(compact) > 4:
        return 16, "os- prefix; readable, slightly mechanical"
    return 24, "not a template"


def _soul(sld: str) -> tuple[int, str]:
    compact = sld.replace("-", "")
    real = compact in WORDS and compact not in GENERIC and compact not in STOPWORDS
    if compact in IMAGE or real:
        return 24, f"{compact!r} is a word people already have a picture for"
    for a, b in _splits(compact):
        a_img = a in IMAGE or (a in WORDS and a not in GENERIC)
        b_img = b in IMAGE or (b in WORDS and b not in GENERIC)
        a_pref = a in STARTUP_PREFIXES
        b_glue = b in GLUE_SUFFIXES
        if a_pref and (b_img or 3 <= len(b) <= 6):
            return 8, f"prefix glue {a}+{b}"
        if b_glue:
            return 8, f"suffix glue {a}+{b}"
        if (a_img or b_img) and (a_img or _plausible_stem(a)) and (b_img or _plausible_stem(b)):
            if a_img and b_img:
                return 22, f"imageable compound {a}+{b}"
            return 20, f"stem+picture {a}+{b}"
    if compact.startswith("im") and compact.endswith("is") and 6 <= len(compact) <= 10:
        return 20, "latin phrase-shape (imprimis)"
    if any(compact.endswith(tail) for tail in NAME_TAILS) and 5 <= len(compact) <= 10:
        return 18, "name-shaped coinage"
    if compact.endswith(JUNK_TAILS):
        return 5, "looks generated"
    if compact.endswith(WEAK_TAILS):
        return 8, "thin coinage"
    if 4 <= len(compact) <= 6:
        return 16, "short invented brand"
    return 9, "pronounceable, no picture"


def _grade(love: int) -> str:
    if love >= 90:
        return "A"
    if love >= 82:
        return "A-"
    if love >= 75:
        return "B+"
    if love >= 68:
        return "B"
    if love >= 58:
        return "C"
    if love >= 45:
        return "D"
    return "F"


def score_domain(raw: str) -> LoveScore:
    sld, tld = split_domain(raw)
    domain = f"{sld}.{tld}"
    syl = _syllables(sld)
    cluster = _consonant_cluster(sld)
    vowel_count = sum(ch in VOWELS for ch in sld)

    punch, punch_why = _punch(sld, syl)
    radio, must_spell, radio_why = _radio(sld, syl, cluster, vowel_count)
    clean, clean_why = _clean(sld)
    tld_pts = min(10, tld_love_points(tld))
    tld_why = {
        "com": ".com - still the one people trust",
        "ai": ".ai - fits an AI product without explaining",
        "io": ".io - startup-coded, some people still pause",
        "xyz": ".xyz - cheap, reads as a joke to civilians",
        "info": ".info - spam TLD",
        "biz": ".biz - nobody loves this",
    }.get(tld, f".{tld}")
    template, template_why = _template(sld)
    soul, soul_why = _soul(sld)

    factors = (
        Factor("punch", punch, 20, punch_why),
        Factor("radio", radio, 12, radio_why),
        Factor("clean", clean, 10, clean_why),
        Factor("tld", tld_pts, 10, tld_why),
        Factor("template", template, 24, template_why),
        Factor("soul", soul, 24, soul_why),
    )
    love = sum(f.score for f in factors)
    compact = sld.replace("-", "")
    why_pen = None
    if compact in STOPWORDS or sld in STOPWORDS:
        love = min(love, 40)
        why_pen = "stopword SLD - nobody loves this as a brand"
    elif compact in GENERIC or sld in GENERIC:
        love = max(0, love - 20)
        why_pen = "generic tech SLD - forgettable"
    love = max(0, min(100, love))
    why = why_pen or f"{soul_why}; {template_why}"
    n = len(sld)
    say_on_a_call = (not must_spell) and syl <= 3 and n <= 12
    return LoveScore(
        domain=domain,
        sld=sld,
        tld=tld,
        love=love,
        grade=_grade(love),
        factors=factors,
        must_spell=must_spell,
        say_on_a_call=say_on_a_call,
        why=why,
    )
