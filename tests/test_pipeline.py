from domain_forge.pipeline import rank_candidates, run


def test_rank_orders_by_love() -> None:
    n, rows = rank_candidates("eidos", tlds=("com", "xyz"), limit=12)
    assert n > 12
    loves = [c.love.love for c in rows]
    assert loves == sorted(loves, reverse=True)


def test_shorter_sld_wins_love_ties() -> None:
    _n, rows = rank_candidates("eidos", tlds=("com",), limit=8)
    assert rows[0].domain == "eidos.com"
    lengths = [len(c.sld) for c in rows]
    assert lengths == sorted(lengths) or rows[0].love.love > rows[-1].love.love


def test_available_only_filters() -> None:
    def fetch(url: str, timeout: float) -> tuple[int, bytes, str]:
        return 404, b"{}", url

    result = run(
        "eidos",
        tlds=("com",),
        limit=4,
        check=True,
        available_only=True,
        fetch=fetch,
        pause=0,
    )
    assert result.returned == 4
    assert all(c.availability and c.availability.status == "available" for c in result.candidates)
