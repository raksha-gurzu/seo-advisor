"""Save sites from site files into the database. Unchanged files change no rows.

Run: `mise run db:seed` (all files in infra/sites/).
"""

import argparse
import sys
from pathlib import Path

from seo_advisor.core.config import SettingsError, load_settings
from seo_advisor.core.db import make_engine, make_session_factory
from seo_advisor.features.sites.service import load_site_spec, register_site


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sites:register", description=__doc__)
    parser.add_argument("site_files", type=Path, nargs="+", help="infra/sites/*.toml")
    args = parser.parse_args(argv)
    try:
        settings = load_settings()
    except SettingsError as exc:
        # The message names the missing settings; a traceback adds nothing.
        print(exc, file=sys.stderr)
        return 2
    specs = [load_site_spec(path) for path in args.site_files]
    engine = make_engine(settings.database_url)
    with make_session_factory(engine)() as session:
        for spec in specs:
            site = register_site(session, spec)
            print(f"{site.tenant_name:<16} {site.base_url}  {site.id}")
    engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
