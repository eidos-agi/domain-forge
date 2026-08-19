"""Love score: how much a person will like saying, typing, and keeping this name.

This is not an LLM vibe. Factors are named, bounded, and summed to 0–100 so
an agent can explain the number. Grounding:

- Radio test (classic brand naming): say it once, can the other person type it?
- Length: 4–8 character SLDs are the ones people actually remember.
- .com is still the TLD you don't have to explain. Novelty TLDs cost trust.
- Hyphens and digits fail the business-card test.

Distinctiveness is a penalty, not a bonus. "cloud.com" is pronounceable and
still a name nobody falls in love with.
"""

from __future__ import annotations

import re

from domain_forge.models import Factor, LoveScore
from domain_forge.parse import split_domain
from domain_forge.tlds import tld_love_points
from domain_forge.words import GENERIC, STOPWORDS, WORDS

VOWELS = set("aeiouy")


def _syllables(sld: str) -> int:
    groups = re.findall(r"[aeiouy]+", sld)
    n = len(groups)
    if sld.endswith("e") and n > 1 and not sld.endswith("le"):
        n -= 1
    return max(1, n)


def _consonant_cluster(sld: str) -> int:
    runs = re.findall(r"[bcdfghjklmnpqrstvwxz]{2,}", sld)
    return max((len(r) for r in runs), default=0)


def _looks_like_words(sld: str) -> tuple[int, str]:
    compact = sld.replace("-", "")
    if compact in WORDS and compact not in STOPWORDS and compact not in GENERIC:
        return 8, f"{compact!r} is a real word"
    if "-" in sld:
        parts = [p for p in sld.split("-") if p]
        if parts and all(p in WORDS for p in parts):
            return 9, "hyphenated real words"
    for i in range(3, len(compact) - 2):
        a, b = compact[:i], compact[i:]
        if a in WORDS and b in WORDS:
            return 10, f"reads as {a}+{b}"
    return 5, "pronounceable stem, not a dictionary pair"


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
    factors: list[Factor] = []

    n = len(sld)
    if 4 <= n <= 8:
        length_score, length_why = 20, f"{n}-character SLD (sweet spot 4-8)"
    elif n == 3:
        length_score, length_why = 14, "3 characters: short, often needs spelling"
    elif n == 9 or n == 10:
        length_score, length_why = 14, f"{n} characters: still sayable"
    elif 11 <= n <= 13:
        length_score, length_why = 8, f"{n} characters: long for a domain"
    elif n <= 2:
        length_score, length_why = 8, "tiny SLD — people will ask you to spell it"
    else:
        length_score, length_why = 3, f"{n} characters: too long to love"
    factors.append(Factor("length", length_score, 20, length_why))

    syl = _syllables(sld)
    cluster = _consonant_cluster(sld)
    vowel_count = sum(ch in VOWELS for ch in sld)
    pronounce = 18
    pronounce_bits: list[str] = []
    if syl in (2, 3):
        pronounce_bits.append(f"{syl} syllables")
    elif syl == 1:
        pronounce -= 3
        pronounce_bits.append("one syllable")
    elif syl == 4:
        pronounce -= 6
        pronounce_bits.append("four syllables")
    else:
        pronounce -= 12
        pronounce_bits.append(f"{syl} syllables")
    if cluster >= 4:
        pronounce -= 8
        pronounce_bits.append(f"{cluster}-letter consonant pile")
    elif cluster == 3:
        pronounce -= 4
        pronounce_bits.append("awkward consonant cluster")
    if vowel_count == 0:
        pronounce = 0
        pronounce_bits.append("no vowels")
    pronounce = max(0, min(18, pronounce))
    factors.append(Factor("pronounce", pronounce, 18, ", ".join(pronounce_bits)))

    spell = 15
    spell_bits: list[str] = []
    if any(ch.isdigit() for ch in sld):
        spell -= 8
        spell_bits.append("digits")
    if "-" in sld:
        spell -= 5
        spell_bits.append("hyphen")
    if any(ch in sld for ch in "0") or (sld.count("l") and sld.count("1")):
        spell -= 3
        spell_bits.append("lookalike characters")
    if re.search(r"(.)\1\1", sld):
        spell -= 4
        spell_bits.append("triple letter")
    if not spell_bits:
        spell_bits.append("letters only, no hyphen")
    spell = max(0, min(15, spell))
    factors.append(Factor("spell", spell, 15, ", ".join(spell_bits)))

    tld_pts = tld_love_points(tld)
    tld_why = {
        "com": ".com - still the one people trust",
        "ai": ".ai - fits an AI product without explaining",
        "io": ".io - startup-coded, some people still pause",
        "xyz": ".xyz - cheap, reads as a joke to civilians",
        "info": ".info - spam TLD",
        "biz": ".biz - nobody loves this",
    }.get(tld, f".{tld}")
    factors.append(Factor("tld", tld_pts, 15, tld_why))

    clean = 12
    clean_bits: list[str] = []
    if "-" in sld:
        clean -= 7
        clean_bits.append("hyphen")
    if any(ch.isdigit() for ch in sld):
        clean -= 6
        clean_bits.append("digit")
    if not clean_bits:
        clean_bits.append("clean label")
    clean = max(0, min(12, clean))
    factors.append(Factor("clean", clean, 12, ", ".join(clean_bits)))

    radio = 10
    must_spell = False
    if vowel_count == 0 or cluster >= 4 or any(ch.isdigit() for ch in sld) or n <= 2:
        must_spell = True
        radio = 2
        radio_why = "fails the radio test - you will have to spell it"
    elif spell < 10 or syl >= 5:
        must_spell = True
        radio = 4
        radio_why = "sayable but people will still ask you to spell it"
    elif syl in (2, 3) and spell >= 12 and n <= 10:
        radio = 10
        radio_why = "say it once, they can type it"
    else:
        radio = 7
        radio_why = "mostly sayable"
    factors.append(Factor("radio", radio, 10, radio_why))

    word_pts, word_why = _looks_like_words(sld)
    factors.append(Factor("wordness", word_pts, 10, word_why))

    love = sum(f.score for f in factors)
    compact = sld.replace("-", "")
    if compact in STOPWORDS or sld in STOPWORDS:
        love = min(love, 40)
        why_pen = "stopword SLD - nobody loves this as a brand"
    elif compact in GENERIC or sld in GENERIC:
        love = max(0, love - 18)
        why_pen = "generic tech SLD - forgettable"
    else:
        why_pen = None
    love = max(0, min(100, love))

    say_on_a_call = (not must_spell) and syl <= 3 and n <= 12
    why = why_pen or factors[0].why
    # Prefer a human sentence: tld + radio, unless penalized.
    if why_pen is None:
        why = f"{tld_why}; {radio_why}"

    return LoveScore(
        domain=domain,
        sld=sld,
        tld=tld,
        love=love,
        grade=_grade(love),
        factors=tuple(factors),
        must_spell=must_spell,
        say_on_a_call=say_on_a_call,
        why=why,
    )
