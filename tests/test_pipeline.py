from domain_forge.pipeline import rank_candidates, run, seed_fit


def test_rank_orders_by_love() -> None:
    n, rows = rank_candidates("eidos", tlds=("com", "xyz"), limit=12)
    assert n > 12
    loves = [c.love.love for c in rows]
    assert loves == sorted(loves, reverse=True)


def test_shorter_sld_wins_love_ties() -> None:
    _n, rows = rank_candidates("eidos", tlds=("com",), limit=8)
    assert rows[0].domain == "eidos.com"


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
    assert result.filtered_out == 0
    assert all(
        c.availability
        and c.availability.status == "available"
        and c.availability.source == "rdap"
        and c.availability.confidence == "registry"
        for c in result.candidates
    )


def test_available_only_drops_dns_weak() -> None:
    def fetch(url: str, timeout: float) -> tuple[int, bytes, str]:
        if "iana.org" in url:
            return 500, b"nope", url
        if "dns.google" in url:
            return 200, b'{"Status":3,"Answer":null}', url
        raise AssertionError(url)

    result = run(
        "eidos",
        tlds=("gg",),
        limit=3,
        check=True,
        available_only=True,
        fetch=fetch,
        pause=0,
    )
    assert result.returned == 0
    assert result.filtered_out == 3


def test_available_only_drops_unknown() -> None:
    def fetch(url: str, timeout: float) -> tuple[int, bytes, str]:
        raise OSError("down")

    result = run(
        "eidos",
        tlds=("com",),
        limit=3,
        check=True,
        available_only=True,
        fetch=fetch,
        pause=0,
    )
    assert result.returned == 0
    assert result.unknown == 3
    assert result.filtered_out == 3


def test_os_pivot_ranks_product_above_get_prefix() -> None:
    _n, rows = rank_candidates("prim", tlds=("com",), limit=40, pivot="os")
    domains = [c.domain for c in rows]
    assert "primos.com" in domains
    assert domains.index("primos.com") < domains.index("goprim.com")


def test_seed_fit_os_product() -> None:
    assert seed_fit("primos", ["prim"], "os", "os") > seed_fit("goprim", ["prim"], "prefix", "os")


def test_available_only_without_check_raises() -> None:
    try:
        run("eidos", tlds=("com",), limit=2, check=False, available_only=True)
    except ValueError as exc:
        assert "no-check" in str(exc)
    else:
        raise AssertionError("expected ValueError")
