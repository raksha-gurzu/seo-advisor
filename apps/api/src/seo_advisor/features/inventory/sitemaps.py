"""Read sitemap files (sitemaps.org) safely. Reused from SEOAdvisor sitemap.py."""

from lxml import etree

from seo_advisor.features.inventory.schemas import ParsedSitemap, SitemapEntry
from seo_advisor.integrations.http_fetch.client import TooLargeError, gunzip_capped

SITEMAP_MAX_BYTES = 50 * 1024 * 1024  # sitemaps.org: at most 50 MB, uncompressed
SITEMAP_MAX_ENTRIES = 50_000  # sitemaps.org: at most 50,000 URLs (or sitemaps) per file


class InvalidSitemapError(ValueError):
    """The file is not a valid sitemap or sitemap index."""


def _parser() -> etree.XMLParser:
    """A new parser for each call: lxml parsers must not be shared between threads.

    No entities, no DTD, no network (XXE). `recover=False`: broken XML is an error,
    not a silent partial result.
    """
    return etree.XMLParser(
        resolve_entities=False,
        load_dtd=False,
        no_network=True,
        recover=False,
        huge_tree=False,
    )


def parse_sitemap(content: bytes) -> ParsedSitemap:
    """A urlset or a sitemap index. A gzip file is unpacked with a size limit."""
    if content[:2] == b"\x1f\x8b":
        try:
            content = gunzip_capped(content, SITEMAP_MAX_BYTES)
        except TooLargeError as exc:
            raise InvalidSitemapError(f"gzip sitemap is too large: {exc}") from None
        except ValueError as exc:
            raise InvalidSitemapError(str(exc)) from None
    if len(content) > SITEMAP_MAX_BYTES:
        raise InvalidSitemapError("sitemap is too large (over 50 MB)")
    try:
        root = etree.fromstring(content, _parser())
    except etree.XMLSyntaxError as exc:
        raise InvalidSitemapError(f"not valid XML: {exc}") from None
    name = etree.QName(root).localname
    if name not in ("urlset", "sitemapindex"):
        raise InvalidSitemapError(
            f"root element is <{name}>, not urlset or sitemapindex"
        )
    child = "url" if name == "urlset" else "sitemap"
    nodes = root.xpath(f"./*[local-name()='{child}']")
    if len(nodes) > SITEMAP_MAX_ENTRIES:
        raise InvalidSitemapError(
            f"{len(nodes)} entries; sitemaps.org allows at most {SITEMAP_MAX_ENTRIES}"
        )
    entries = []
    for node in nodes:
        loc = "".join(node.xpath("./*[local-name()='loc']/text()")).strip()
        lastmod = "".join(node.xpath("./*[local-name()='lastmod']/text()")).strip()
        if loc:
            entries.append(SitemapEntry(url=loc, lastmod=lastmod))
    return ParsedSitemap(
        kind="urlset" if name == "urlset" else "index", entries=entries
    )
