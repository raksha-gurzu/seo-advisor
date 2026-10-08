import pytest

from seo_advisor.features.inventory.page_types import page_type_of
from seo_advisor.features.sites.service import PageTypeRule

MYPIPIT = [
    PageTypeRule(pattern="/blog", page_type="blog_index"),
    PageTypeRule(pattern="/blog/category/*", page_type="blog_category"),
    PageTypeRule(pattern="/blog/*", page_type="blog_post"),
    PageTypeRule(pattern="/marketplace", page_type="listing_index"),
    PageTypeRule(pattern="/marketplace/*", page_type="listing"),
    PageTypeRule(pattern="/pages/*", page_type="static"),
    PageTypeRule(pattern="/sellers/*", page_type="seller"),
]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("url", "page_type"),
    [
        ("https://m.example/blog", "blog_index"),
        ("https://m.example/blog/", "blog_index"),  # a trailing slash does not matter
        (
            "https://m.example/blog/category/trekking",
            "blog_category",
        ),  # first match wins
        ("https://m.example/blog/nepal-trekking-permits-explained", "blog_post"),
        ("https://m.example/blog/a/b/c", "other"),  # * is exactly one path part
        ("https://m.example/marketplace", "listing_index"),
        ("https://m.example/marketplace/cross-thorong-la-5-416-m", "listing"),
        ("https://m.example/pages/about?ref=x", "static"),  # the query does not matter
        ("https://m.example/sellers/my-pipit", "seller"),
        ("https://m.example/", "other"),
        ("https://m.example/blogs", "other"),  # no prefix match
    ],
)
def test_mypipit_page_types(url: str, page_type: str) -> None:
    assert page_type_of(url, MYPIPIT) == page_type


@pytest.mark.unit
def test_match_names_the_first_rule_that_matches() -> None:
    from seo_advisor.features.inventory.page_types import match_page_type

    found = match_page_type("https://m.example/blog/category/trekking/", MYPIPIT)
    assert (found.path, found.page_type, found.rule_index) == (
        "/blog/category/trekking",
        "blog_category",
        1,
    )
    none = match_page_type("https://m.example/about", MYPIPIT)
    assert (none.page_type, none.rule_index) == ("other", None)
