# Slice 2, part 2a: database base, tenants and sites (7 Oct 2026)

## Owner decisions

- Slice 1 stages 3-4 (walk-through, plan review) wait: the owner will look at slice 1 later and asked to continue.
- Packages approved: SQLAlchemy 2.1.1 (MIT), psycopg[binary] 3.3.6 (LGPL-3.0, used as an unchanged library), Alembic 1.20.0 (MIT), testcontainers 4.15.0 (Apache-2.0, test group). `mise run audit`: no known vulnerabilities. SQLAlchemy is 2.1.1, not 2.1.3: the 7-day delay.
- Decided for the owner (tell if not OK): no pgvector extension yet (no vector column needs it); `mise run check` needs Docker (real PostgreSQL in tests).

## Files

| File | Contents |
|---|---|
| `infra/docker-compose.yml` | `pgvector/pgvector:0.8.7-pg18-trixie`, health check, volume at `/var/lib/postgresql` (PG18 rule), port on 127.0.0.1 only, values from `.env`. |
| `core/db.py` | `Base` with the name rules (unique rule names have all their columns), `IdMixin` (`uuidv7()`), `TimestampMixin` (`timestamptz`), `make_engine`, `make_session_factory`. |
| `features/sites/` | `models.py` (`tenants`, `sites`; site page types as JSONB), `repository.py`, `schemas.py` (`PageTypeRule`, `SiteSpec` with `tenant`, `SiteRecord`), `service.py` (`load_site_spec`, `register_site`, `get_site`). |
| `alembic.ini`, `apps/api/migrations/` | `env.py` (URL from Settings, or from the config in tests), template, first migration `77d78514aaf7` "create tenants and sites" (read and edited). |
| `infra/sites/mypipit.toml` | Now has `tenant = "MyPipit"`. |
| `tests/conftest.py` | Session PostgreSQL container (testcontainers), migrated once; `db` fixture rolls back after each test (`join_transaction_mode="create_savepoint"`). |
| `tests/sites/`, `tests/test_migrations.py` | Site file and schema tests; register tests (create, no change on repeat, update, two tenants); `alembic check`. |

## Decisions

- `SiteSpec`, `PageTypeRule` and `load_site_spec` moved from `inventory` to `sites` (CLAUDE.md: sites = tenants, sites, onboarding). `inventory` imports them from `sites.service` only. `discover_pages` accepts any object with `base_url`, `language`, `page_types` (`SiteRules` protocol).
- `register_site` writes only if a value changed. An update sets `updated_at = clock_timestamp()`: `now()` is the transaction start.
- First migration edits: unique rule name `uq_sites_tenant_id_base_url` (name rule `column_0_N_name`); no extra index on `sites.tenant_id` (the unique rule starts with it).
- New import contract: "sites: internals are private".

## Checks

1. Experiment: Compose database healthy; PostgreSQL 18.6; `uuidv7()` gives version 7; time zone UTC.
2. On the Compose database: `alembic upgrade head`, `check`, `downgrade base`, `upgrade head`: no errors; current = `77d78514aaf7 (head)`.
3. Tests first: collection failed before the code. `mise run check`: 149 tests (with integration tests on a real PostgreSQL 18 container, about 6-12 s), mypy strict, 3 contracts kept. No warnings.

## Next

Part 2b: `pages` table (feature `inventory`), save the inventory (insert new, update changed, mark missing pages `not_listed`, no write when nothing changed), command `mise run inventory:sync -- infra/sites/mypipit.toml`. Done when: a second run changes no rows, and an integration test passes twice.
