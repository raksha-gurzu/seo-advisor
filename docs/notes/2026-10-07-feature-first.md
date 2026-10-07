# Change of method: feature-first (7 Oct 2026)

The owner asked for the big picture before more setup. After the discussion, the owner chose to build features first.

## Decisions (owner)

1. **Feature-first.** Phase 1 is done in 5 slices. Each slice is one small pull request that works from end to end. A setup step (0.4 to 0.12) starts only when a slice needs it. The table in `PLAN.md` → Phase 0 says when.
2. **No empty placeholder folders.** A folder is made with its first file. Removed: `.github/`, `apps/web/`, `apps/extension/`, `docs/architecture/`, `docs/decisions/`, `docs/design/`, `evals/`, `infra/`, `packages/api-client/`. `CLAUDE.md`, `README.md` and `docs/README.md` now say this.
3. **First goal confirmed:** add MyPipit and see its pages and SEO problems, with evidence.
4. **Live fetch allowed for slice 1:** only `robots.txt` and the sitemaps of MyPipit, read-only, a few requests, through the SSRF guard. Save them as test fixtures.
5. **SEOAdvisor code:** the owner will give the path. Slice 1 reuses its fetcher, SSRF guard and robots (Protego) code.

## Slices

| Slice | Result | Setup it brings |
|---|---|---|
| 1 | MyPipit URL list with page type and language | Safe fetcher (SSRF guard, robots, rate limit), sitemap reader |
| 2 | Sites and pages in the database | Step 0.4: Compose, SQLAlchemy, Alembic; tables `tenants`, `sites`, `pages` |
| 3 | `GET /api/v1/sites/{id}/pages` | Step 0.5: FastAPI, `main.py` |
| 4 | Snapshots, first rules, findings with evidence | DBOS schedule, rules |
| 5 | Findings screen | Step 0.6: React web app |

## Also changed

- `PLAN.md`: "Current step" line, the Phase 0 table, the slices in Phase 1, a change-log line. The PDF script has the same change-log line. The PDF is not rebuilt, and its setup pages still show the old order.
- `.gitignore`: `.import_linter_cache/` (import-linter also ignores it by itself).

## Next

Slice 1. Before it starts:
1. The owner gives the SEOAdvisor path.
2. The owner approves the packages for slice 1 (an HTTP client and Protego). Read R1 §3.5 and §3.7 first.
