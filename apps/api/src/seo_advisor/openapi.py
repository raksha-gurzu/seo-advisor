"""Write the API's OpenAPI document to a file. Used by `mise run gen-client`.

Run: `python -m seo_advisor.openapi packages/api-client/openapi.json`.
"""

import json
import sys
from pathlib import Path

from seo_advisor.main import LOCAL_HOSTS, build_app


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m seo_advisor.openapi <output.json>", file=sys.stderr)
        return 2
    document = build_app(LOCAL_HOSTS).openapi()
    Path(argv[0]).write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
