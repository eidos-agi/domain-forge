from domain_forge.check import check_domain, check_many, rdap_url
from domain_forge.tlds import BAKED_RDAP


def test_rdap_url_com() -> None:
    url = rdap_url("google.com", BAKED_RDAP)
    assert url == "https://rdap.verisign.com/com/v1/domain/google.com"


def test_rdap_200_is_taken() -> None:
    def fetch(url: str, timeout: float) -> tuple[int, bytes, str]:
        return 200, b'{"objectClassName":"domain"}', url

    report = check_domain("google.com", fetch=fetch, bootstrap=BAKED_RDAP)
    assert report.status == "taken"
    assert report.source == "rdap"
    assert report.confidence == "registry"


def test_rdap_404_is_available() -> None:
    def fetch(url: str, timeout: float) -> tuple[int, bytes, str]:
        return 404, b'{"errorCode":404}', url

    report = check_domain("zzzznotarealxyz123.com", fetch=fetch, bootstrap=BAKED_RDAP)
    assert report.status == "available"
    assert report.http_status == 404


def test_rdap_500_is_unknown() -> None:
    def fetch(url: str, timeout: float) -> tuple[int, bytes, str]:
        return 500, b"nope", url

    report = check_domain("eidos.com", fetch=fetch, bootstrap=BAKED_RDAP)
    assert report.status == "unknown"


def test_dns_fallback_when_no_rdap() -> None:
    def fetch(url: str, timeout: float) -> tuple[int, bytes, str]:
        if "dns.google" in url:
            return 200, b'{"Status":3,"Answer":null}', url
        raise AssertionError(url)

    report = check_domain("zzzz.gg", fetch=fetch, bootstrap={})
    assert report.source == "dns"
    assert report.status == "available"
    assert report.confidence == "weak"


def test_check_many_pauses_between() -> None:
    slept: list[float] = []

    def fetch(url: str, timeout: float) -> tuple[int, bytes, str]:
        return 404, b"{}", url

    rows = check_many(
        ["aaaaaa.com", "bbbbbb.com"],
        fetch=fetch,
        bootstrap=BAKED_RDAP,
        pause=0.5,
        sleeper=slept.append,
    )
    assert [r.status for r in rows] == ["available", "available"]
    assert slept == [0.5]
