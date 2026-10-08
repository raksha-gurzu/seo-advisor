# API and web app for slice 1 (8 Oct 2026)

## Owner decisions

- Backend and frontend go in parallel. Each slice ends with its screen.
- Packages approved:
  - API: `fastapi` 0.142.2 and `uvicorn[standard]` 0.54.0. Not `fastapi[standard]`, because it adds about 15 extras.
  - Web: the full list in `apps/web/package.json`, plus `jsdom` (the test DOM).
  - Not used: `@testing-library/jest-dom`, `user-event`, and shadcn's new `cn` package.
- `make dev` starts everything. The Makefile only calls the mise tasks.
- Discovery from the screen is live and read-only, through the safe fetcher. Results stay in the browser tab. (Replan, same day: the sitemap list is now only a page picker.)
- The Activity screen shows each request of a run.

## What exists now

| Part | Contents |
|---|---|
| `main.py` | `build_app(allowed_hosts)`: routes, `/health`, `/api/v1`. `create_app(settings)` adds the database and one shared `SafeFetcher`. `app_from_env` is the uvicorn factory. |
| `core/api.py`, `core/errors.py` | RFC 9457 errors with `request_id`, a request-ID middleware, a Host check (`TrustedHostMiddleware`), and the `SessionDep` and `FetcherDep` dependencies. `NotFoundError` gives 404; `InvalidInputError` gives 422. |
| `features/sites/api.py` | `GET /api/v1/sites`, `GET /api/v1/sites/{id}`. `SiteRecord` now has `tenant_name`. |
| `features/sites/cli.py` | `mise run db:seed`: saves `infra/sites/*.toml`. An unchanged file changes no rows. |
| `features/inventory/api.py` | `POST /api/v1/sites/{id}/discoveries` gives a `DiscoveryRun` (inventory and requests). `GET /api/v1/sites/{id}/page-type?url=` gives the matching rule. |
| `integrations/http_fetch/trace.py` | `trace_scope()` records one `FetchEvent` per hop: kind, URL without query or user info, outcome, status, bytes and times. It never records bodies or headers. |
| `packages/api-client` | `openapi.json` and the generated `schema.d.ts` (`mise run gen-client`). The web app calls the API only through it. |
| `apps/web` | Screens: Sites, Inventory (counts, page types, problems, pages table), Rules (with the URL tester), Activity (request list). |
| `Makefile`, `mise.toml` | `make dev`, `make check`, `make seed` and the other short names. `check` now also runs oxlint, Prettier, tsc and Vitest. `audit` also runs `pnpm audit`. |

## Security review (general agent; the `security-reviewer` subagent does not exist yet)

The review found 0 high, 2 medium and 4 low findings. All are fixed, with tests:
1. A sitemap on another host (in robots.txt or in an index) is now a problem, and it is never requested. Before the fix, a hostile site could make one run fetch thousands of hosts.
2. A Host check stops DNS rebinding against the API on 127.0.0.1.
3. The discovery closes its database session before the network part.
4. A malformed URL in the URL tester gives 422, not 500.
5. A page URL that is not http or https, or that cannot be parsed, is a problem (`url_not_http`). Before the fix, an unparseable URL stopped the run.
6. A sitemap network error shows only its type.

Also fixed: a 405 answer keeps its `Allow` header. Also added: a sitemap with more than 50,000 entries is not valid (sitemaps.org).

## Checks

1. `mise run check`: 175 Python tests and 11 web tests pass. ruff, mypy, oxlint, Prettier and tsc pass. All 5 import contracts are kept.
2. `mise run audit`: no known vulnerabilities (pnpm and uv).
3. Live run through `make dev`: MyPipit gives 58 pages and 0 problems. robots.txt gives 404; `sitemap.xml` gives 200 with 12,025 bytes.
4. Host check probes: `Host: evil.example` gives 400. A malformed URL gives 422.

## Open

- There is no limit on the total number of sitemaps or pages in one run. This needs a `Settings` value, so the owner must choose it.
- There is no login or tenancy filter yet. The API is local only (127.0.0.1).
- structlog (step 0.5) is not added yet.
- The tests give a warning from Starlette: "Using `httpx` with `starlette.testclient` is deprecated; install `httpx2`". Adding `httpx2` is a new package, so the owner must decide.
- Next: the plan changed the same day to single page first. See `2026-10-08-replan-single-page.md`.
