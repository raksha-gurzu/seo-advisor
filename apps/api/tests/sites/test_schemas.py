from pathlib import Path

import pytest
from pydantic import ValidationError

from seo_advisor.features.sites.service import PageTypeRule, SiteSpec, load_site_spec

REPO = Path(__file__).parents[4]


@pytest.mark.unit
def test_the_mypipit_site_file_loads() -> None:
    site = load_site_spec(REPO / "infra" / "sites" / "mypipit.toml")
    assert site.tenant == "MyPipit"
    assert site.base_url == "https://marketplace.mypipit.com"
    assert site.language == "en"
    assert site.page_types[0] == PageTypeRule(pattern="/blog", page_type="blog_index")


@pytest.mark.unit
@pytest.mark.parametrize(
    "base_url", ["ftp://s.example", "https://s.example/path", "s.example", "http://"]
)
def test_a_site_needs_a_plain_web_origin(base_url: str) -> None:
    with pytest.raises(ValidationError, match="base_url"):
        SiteSpec(tenant="T", base_url=base_url, language="en", page_types=[])


@pytest.mark.unit
def test_a_trailing_slash_is_removed_from_the_origin() -> None:
    site = SiteSpec(
        tenant="T", base_url="https://s.example/", language="en", page_types=[]
    )
    assert site.base_url == "https://s.example"


@pytest.mark.unit
@pytest.mark.parametrize("pattern", ["blog/*", "", "/blog/**", "/blog/x*"])
def test_bad_patterns_are_refused(pattern: str) -> None:
    with pytest.raises(ValidationError):
        PageTypeRule(pattern=pattern, page_type="x")
