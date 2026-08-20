"""Name invention. Not get/try/kit glue.

A person does not fall in love with goprim.com. They fall in love with
something that could go on a boot screen: Prism, Primora, Imprimis.
Deterministic. No model.
"""

from __future__ import annotations

# Latin first-ness, clipped to what still sounds like a product.
LATIN_ENDS = ("us", "a", "o", "um", "is", "al")

# Soft tails that turn a 3-4 letter stem into a coined word.
COINED_TAILS = (
    "ora",
    "ion",
    "elle",
    "ara",
    "ia",
    "eve",
    "ova",
    "en",
    "ex",
    "ax",
    "yn",
    "ea",
    "el",
)

# OS-as-place, not OS-as-suffix. Keep the stem audible.
OS_METAPHORS = ("dawn", "nova", "lumen", "seed", "root", "vera", "nona", "aether")


def invent(stem: str, *, pivot: str | None = None) -> list[tuple[str, str]]:
    """Return (sld, strategy) coined from stem. First-wins order."""
    stem = stem.lower()
    out: list[tuple[str, str]] = []
    if len(stem) < 3 or len(stem) > 8:
        return out

    def add(sld: str, strategy: str) -> None:
        if not sld or sld == stem:
            return
        out.append((sld, strategy))

    if 3 <= len(stem) <= 5 and stem[-1].isalpha() and stem[-1] not in "aeiou":
        for end in LATIN_ENDS:
            add(stem + end, "latin")
        add("im" + stem, "im")
        add("im" + stem + "is", "im")

    # prim → prism (insert s before the last consonant). Reads as a real word.
    if 3 <= len(stem) <= 4 and stem[-1] in "mnrlp" and stem[-2] in "aeiou":
        add(stem[:-1] + "s" + stem[-1], "near")

    # prim → prym (the y-for-i mutation English already uses in pyre/tyre).
    if stem.count("i") == 1 and 3 <= len(stem) <= 5:
        add(stem.replace("i", "y", 1), "mutate")
        y = stem.replace("i", "y", 1)
        if not y.endswith("e"):
            add(y + "e", "mutate")

    if 3 <= len(stem) <= 4:
        add(stem + stem[-1], "mutate")

    if 3 <= len(stem) <= 5:
        for tail in COINED_TAILS:
            if stem.endswith(tail[:1]) and tail[:1] not in "aeiou":
                continue
            add(stem + tail, "coined")

    if pivot == "os":
        near = stem[:-1] + "s" + stem[-1] if 3 <= len(stem) <= 4 else ""
        if near:
            add(near + "os", "near")
        add(stem + "a" + "os", "os")
        add("os" + stem + "a", "os")
        for word in OS_METAPHORS:
            add(stem + word, "metaphor")
            add(word + stem, "metaphor")
        add(stem + "igen", "latin")
        add(stem + "ordia", "latin")

    # Dedup preserving order.
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for sld, strategy in out:
        if sld in seen:
            continue
        seen.add(sld)
        unique.append((sld, strategy))
    return unique
