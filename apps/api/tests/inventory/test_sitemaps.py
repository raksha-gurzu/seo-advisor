import gzip
from pathlib import Path

import pytest

from seo_advisor.features.inventory.sitemaps import InvalidSitemapError, parse_sitemap

FIXTURES = Path(__file__).parent / "fixtures"
NS = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'


@pytest.mark.unit
def test_parse_the_real_mypipit_sitemap() -> None:
    parsed = parse_sitemap((FIXTURES / "mypipit-sitemap.xml").read_bytes())
    assert parsed.kind == "urlset"
    assert len(parsed.entries) == 58
    assert parsed.entries[0].url.startswith("https://marketplace.mypipit.com/")
    assert sum(1 for e in parsed.entries if e.lastmod) == 51


@pytest.mark.unit
def test_parse_an_index() -> None:
    xml = (
        f"<sitemapindex {NS}><sitemap><loc>https://s.example/a.xml</loc>"
        "<lastmod>2026-10-01</lastmod></sitemap></sitemapindex>"
    )
    parsed = parse_sitemap(xml.encode())
    assert parsed.kind == "index"
    assert [(e.url, e.lastmod) for e in parsed.entries] == [
        ("https://s.example/a.xml", "2026-10-01")
    ]


@pytest.mark.unit
def test_parse_a_gzip_file_and_skip_empty_locations() -> None:
    xml = (
        f"<urlset {NS}><url><loc> https://s.example/a </loc></url>"
        "<url><loc/></url></urlset>"
    )
    parsed = parse_sitemap(gzip.compress(xml.encode()))
    assert [e.url for e in parsed.entries] == ["https://s.example/a"]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("content", "message"),
    [
        (
            b"<urlset><url><loc>https://s.example/a</loc></url>",
            "not valid XML",
        ),  # unclosed
        (b"<html><body>Not found</body></html>", "root element"),
        (b"", "not valid XML"),
        (b"\x1f\x8bnot gzip", "not valid gzip"),
    ],
)
def test_broken_sitemaps_are_errors_not_partial_results(
    content: bytes, message: str
) -> None:
    with pytest.raises(InvalidSitemapError, match=message):
        parse_sitemap(content)


@pytest.mark.unit
def test_a_gzip_bomb_sitemap_is_refused() -> None:
    with pytest.raises(InvalidSitemapError, match="too large"):
        parse_sitemap(gzip.compress(b"<urlset>" + b" " * 60_000_000 + b"</urlset>"))


@pytest.mark.unit
def test_entities_are_not_expanded(tmp_path: Path) -> None:
    secret = tmp_path / "secret.txt"
    secret.write_text("TOP-SECRET")
    xml = (
        f'<?xml version="1.0"?><!DOCTYPE urlset [<!ENTITY x SYSTEM "file://{secret}">'
        '<!ENTITY y "https://s.example/expanded">]>'
        f"<urlset {NS}><url><loc>&x;</loc></url><url><loc>&y;</loc></url></urlset>"
    )
    parsed = parse_sitemap(xml.encode())
    assert all("TOP-SECRET" not in e.url for e in parsed.entries)
    assert all("expanded" not in e.url for e in parsed.entries)


@pytest.mark.unit
def test_more_than_50000_entries_is_not_valid() -> None:
    from seo_advisor.features.inventory.sitemaps import (
        SITEMAP_MAX_ENTRIES,
        InvalidSitemapError,
        parse_sitemap,
    )

    ns = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
    one = "<url><loc>https://s.example/p</loc></url>"
    body = f"<urlset {ns}>{one * (SITEMAP_MAX_ENTRIES + 1)}</urlset>".encode()
    with pytest.raises(InvalidSitemapError, match="50000"):
        parse_sitemap(body)
