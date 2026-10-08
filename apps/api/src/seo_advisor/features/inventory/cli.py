"""Print the inventory of one site.

Run: `mise run inventory:discover -- infra/sites/<site>.toml`.

Read-only: it reads robots.txt and the sitemaps through the safe fetcher.
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

from seo_advisor.core.config import SettingsError, load_settings
from seo_advisor.features.inventory.service import discover_pages
from seo_advisor.features.sites.service import load_site_spec
from seo_advisor.integrations.http_fetch import FetchConfig, SafeFetcher


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="inventory:discover", description=__doc__)
    parser.add_argument(
        "site_file", type=Path, help="site file, for example infra/sites/mypipit.toml"
    )
    parser.add_argument("--list", action="store_true", help="print every page")
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
    except SettingsError as exc:
        # The message names the missing settings; a traceback adds nothing.
        print(exc, file=sys.stderr)
        return 2
    config = FetchConfig.from_settings(settings)
    site = load_site_spec(args.site_file)
    with SafeFetcher(config) as fetcher:
        inventory = discover_pages(fetcher, site)

    print(f"Site: {inventory.base_url}")
    print(f"Sitemaps read: {len(inventory.sitemaps_read)}")
    for url in inventory.sitemaps_read:
        print(f"  {url}")
    print(f"Pages: {len(inventory.pages)}")
    for page_type, count in Counter(p.page_type for p in inventory.pages).most_common():
        print(f"  {page_type:<16} {count:>5}")
    print(f"Problems: {len(inventory.problems)}")
    for problem in inventory.problems:
        print(f"  {problem.kind:<22} {problem.url} {problem.detail}".rstrip())
    if args.list:
        print("All pages:")
        for page in inventory.pages:
            print(f"  {page.page_type:<16} {page.language}  {page.url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
