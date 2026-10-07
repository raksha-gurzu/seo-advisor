# seo-advisor: plan

What to build and in which order. How to work: `CLAUDE.md` (repo root).

- General multi-site SEO tool. MyPipit and extendmy.life are test sites, not design targets.
- Full version for people: `requirements/seo-advisor-requirements.pdf` (same plan, with reasons and diagrams). Keep it in sync with this file.
- Evidence: `requirements/research/` · R1 platform · R2 content SEO · R3 MyPipit · R4 project setup (`§` = section).
- Work on the current step only, in small parts. Tick a task only when its "Done when" is true.
- Plan changes: strike the old task (`~~task~~ — why`), add a change-log line, update the PDF and the ADR.

## Session habits (for you)

- One task per Claude session. `/clear` before the next task; `/compact <focus>` to continue a long task.
- Start with: "Read PLAN.md step X and the latest note in docs/notes/."
- Smaller model for routine edits; larger model for planning and hard bugs. Switch off unused MCP servers (`/mcp`).
- Read every line before a merge. Log time in Emitii on the matching card.

## Decisions

Each decision gets an ADR in `docs/decisions/` (step 0.10).

| Topic | Decision |
|---|---|
| Product | Read-only on client sites. The extension fills the site editor; a person saves. Never publish. |
| Reviews | Gurzu 2i review, then client approval. Expert review for health; native review for German. |
| Structure | Modular monolith grouped by feature; features talk only through `service.py` (layout in `CLAUDE.md`). |
| Stack | Python, uv, FastAPI, Pydantic, SQLAlchemy (sync), Alembic, DBOS · PostgreSQL + pgvector · React, TypeScript, Vite, pnpm, TanStack Router + Query + Table, Tailwind CSS + shadcn/ui · WXT · mise · Docker Compose. |
| Frontend | React single-page app; no Next.js, no global store. TanStack Router, Query, Table; Tailwind CSS + shadcn/ui (code in the repo). React Hook Form + Zod from Phase 2; Recharts from Phase 5. |
| Tenancy | Shared schema, `tenant_id` + `site_id` on every row; row-level security later. |
| Git and CI | Protected `main`, squash merge, Conventional Commits PR titles, Dependabot, gitleaks. 0 approvals while one engineer; 1 when a second joins. |
| Repo | Package `seo_advisor`. Reuse from SEOAdvisor: fetcher + SSRF guard, robots (Protego), title pixel check, AI wrapper. |

## Open questions

- [ ] extendmy.life editor/CMS · [ ] Search Console access for extendmy.life · [ ] Health content rule
- [ ] Native German reviewer · [ ] HWG §11 legal check · [ ] Review cycle for health pages
- [ ] Code owner (Gurzu or client), sets the NOTICE · [ ] AI provider data terms before client pages are sent (R4 §11.7)

## Tool versions (for setup only; afterwards the lock files decide)

Checked 6 Oct 2026; re-check on setup day. Python 3.14.8 · uv 0.12.23 · ruff 0.16.10 · mypy 2.4.0 · pytest 9.1.1 · testcontainers 4.15.0 · FastAPI 0.142.2 · Pydantic 2.13.5 · pydantic-settings 2.15.0 · SQLAlchemy 2.1.3 · psycopg 3.3.6 · Alembic 1.20.0 · DBOS 3.2.0 · structlog 26.1.0 · pytest-recording 0.14.0 · pip-audit 2.10.1 · import-linter 2.15 · Node 24 LTS (26 LTS from 28 Oct) · pnpm 12.9 · Vite 8.3.3 · React 19.3.0 · TypeScript 6.0.3 · oxlint 1.87.0 · Prettier 3.9.9 · Vitest 5.0.3 · Playwright 1.63.0 · WXT 0.21.4 · openapi-typescript 7.13.0 + openapi-fetch 0.17.0 · mise 2026.10.3 · prek 0.5.5 · gitleaks 8.30.1 · `pgvector/pgvector:0.8.7-pg18-trixie`

---

## Phase 0: Set up the repo (about 1 to 1.5 weeks)

**0.1 Machine**
- [x] Install mise, Docker, gh CLI, Claude Code. Git identity `raksha-gurzu`; push via `github.com-gurzu`. Done when: all four report versions and `gh auth status` passes.

**0.2 Skeleton** (R4 §4, §9.5, §18)
- [x] Folders as in `CLAUDE.md` → Structure, plus `packages/api-client`, `docs/{decisions,architecture,design,notes}`, `evals`, `experiments`, `infra`, `.github`, and this `requirements/` folder. `PLAN.md` and `CLAUDE.md` stay at the repo root, not in `requirements/`. Done when: the tree matches.
- [x] README (5-minute setup), `.gitignore`, `.gitattributes`, `.editorconfig`, `.env.example` (fake values), NOTICE (proprietary), CONTRIBUTING.md, SECURITY.md; a short README in folders that have rules (`docs`, `experiments`, `packages/api-client`). Done when: a new person can follow the README.
- [x] `mise.toml`: tool pins + tasks `setup dev test lint typecheck check audit db:up db:down db:migrate db:seed gen-client evals docs:pdf` (`docs:pdf` rebuilds the requirements PDF; needs Node + `@hpcc-js/wasm-graphviz` and Chromium). Done when: `mise run setup` works on a fresh clone.

**0.3 Python** (R4 §1, §5.3, §11.4)
- [ ] `pyproject.toml`, `uv.lock`, groups `dev test lint`, `exclude-newer = "7 days"`, src layout with `core/`, `integrations/`, empty `features/`. Done when: `uv sync --locked` passes.
- [ ] ruff (E F W I UP B SIM S ASYNC PT RUF DTZ N), mypy --strict + Pydantic plugin, pytest strict + markers `unit integration e2e live`, import-linter `protected` + `forbidden` contracts (a feature's models and repository are private; not `independence`, which would also block `service.py`), pip-audit. Done when: `mise run check` passes and a forbidden import fails it.
- [ ] `Settings` from env, `SecretStr` keys, fail fast. Done when: a missing key stops start-up with a clear message.

**0.4 Database** (R4 §5.1, §13)
- [ ] Compose: pgvector image, volume at `/var/lib/postgresql`, health check, `CREATE EXTENSION vector`. Done when: `mise run db:up` is healthy.
- [ ] SQLAlchemy `Base` + Alembic naming convention and `date_rev_slug` file template. First migration: `uuidv7()` keys, `timestamptz`, tables tenants, users, sites, pages, page_snapshots, audit_runs, findings, rules. Done when: `alembic upgrade head` + `alembic check` pass on an empty DB.
- [ ] Fixtures: testcontainers per session, rollback per test, DBOS reset. Seed: 2 fake sites. Done when: an integration test passes twice in a row.

**0.5 API** (R4 §12, §14)
- [ ] FastAPI `/api/v1` + `/health`, RFC 9457 error handler (write it), request-ID middleware, structlog, `operation_id` per route. Done when: an error returns `application/problem+json` with `request_id`.
- [ ] `gen-client`: `openapi.json` → `packages/api-client`. Done when: the web app calls `/health` through it.

**0.6 Web and extension** (R4 §2, §3)
- [ ] Vite react-ts, strict TS flags (R4 §2.5), oxlint + Prettier, Vitest + Testing Library + MSW, TanStack Router + Query + Table, Tailwind CSS + shadcn/ui (components in `src/shared/ui`); folders as in `CLAUDE.md` → Structure; keep pnpm `minimumReleaseAge`, no install scripts allowed. Check the version, licence and advisories of each library that R4 does not cover. Done when: lint, types, tests and build pass.
- [ ] WXT skeleton (exact version), minimal permissions, no remote code. Done when: it loads in Chromium and calls `/health`.

**0.7 Hooks** (R4 §8)
- [ ] `.pre-commit-config.yaml` run by prek: hygiene, gitleaks, ruff, oxlint + Prettier, `uv lock --check`, actionlint, zizmor. Done when: under 5 s and a planted fake key is blocked.

**0.8 CI and GitHub** (R4 §6, §7)
- [ ] `ci.yml`: SHA-pinned actions, read-only token, jobs lint, types, tests, migrations, openapi-drift, web, extension, gitleaks, one `required` job. Done when: a failing test blocks the merge.
- [ ] Ruleset on `main` (PR, `required` check, squash only, linear history, no force push, auto-delete branches, 0 approvals), PR-title check, Dependabot (uv, npm, actions, docker; weekly, grouped), "require SHA-pinned actions" policy, PR template ("AI-assisted, reviewed by"). Done when: a direct push is refused and the first Dependabot PR passes CI.

**0.9 Claude Code** (R4 §16)
- [ ] ~~Copy `requirements/CLAUDE.template.md` to the repo root as `CLAUDE.md`.~~ — `CLAUDE.md` is at the repo root from the start. Done when: Claude runs `mise run check` from `CLAUDE.md` alone.
- [ ] `.claude/settings.json`: deny reads of `.env*`, `*.pem`, `*.lock`, `pnpm-lock.yaml`, `dist/`, `node_modules/`, `packages/api-client/`, `*.pdf`; deny `git push --force`; allow `mise run *`, `uv run pytest*`, `pnpm test*`; format hook after edits; fast tests on Stop; sandbox on; `CLAUDE.local.md` git-ignored. Done when: Claude cannot read `.env`.
- [ ] Skills `new-endpoint`, `new-migration`, `run-evals`; subagent `security-reviewer`. Done when: each is used once on a real task.

**0.10 Decisions** (R4 §9)
- [ ] ADRs (MADR 4.0) for each row of the Decisions table, plus DBOS, code-first OpenAPI, AI providers, WXT, logging. C4 level 1 and 2 diagrams. Design-doc template. Done when: each ADR has context, options, decision, consequences.

**0.11 Security and AI base** (R4 §11, §15)
- [ ] SSRF guard + tests for each blocked range and DNS rebinding. Done when: tests pass before any crawler code exists.
- [ ] AI layer: provider interface, model and price settings, `llm_calls` table, versioned prompts, recorded fixtures (keys filtered), cost caps per run and day; one key per person and a spend limit per provider. Done when: a recorded call replays in CI with no network.
- [ ] `evals/` with 20 cases and code-based graders. Done when: `mise run evals` prints a score table.

**0.12 Final check**
- [ ] Fresh clone → `mise run setup` → `mise run check` in ≤ 15 min; CI green; planted secret blocked; direct push refused. Done when: a second person or a fresh Claude session does it from the README only.

**Should (weeks 2 to 4):** SSH commit signing · issue forms, labels, milestones · Semgrep + weekly pip-audit job · rising coverage floor · hypothesis tests for scoring · Playwright E2E (2-3 journeys + extension) · OpenTelemetry + local traces · nightly evals with model graders · settings-based feature flags.

---

## Phase 1: Inventory and audit (test site MyPipit, 2 to 3 weeks)
- [ ] `sites`, `inventory`: onboarding, robots.txt, sitemap index, page types. Done when: inventory = sitemap URLs.
- [ ] `inventory`: crawler (robots, rate limit per host, snapshots). Done when: a full crawl is stored.
- [ ] `audits`: rule engine; rules per page type and language, each with a source (PDF §12). Done when: each finding has evidence.
- [ ] `audits`: DBOS schedules (daily, weekly, monthly); compare runs. Done when: 2 weeks without a manual start.
- [ ] `search_data`: Search Console sync (R1 §5). Done when: 16 months stored, daily rows added.
- [ ] Web: findings view. Done when: the SEO team reviews findings there.
- [ ] **Check:** ≥ 90% of findings correct; else fix the rules first.

## Phase 2: Content workflow (2 weeks)
- [ ] `content`: items, immutable versions, state events, reviews (R1 §2.4). Done when: every change has a version and an event.
- [ ] `content`: states and roles (PDF §4). Done when: nobody approves own item; every transition tested.
- [ ] `content`: work queue (impact × confidence ÷ effort; template vs page fixes; batches of 5-10). Done when: top 10 with reasons.
- [ ] `search_data`: keyword-to-page map, one primary per page and language. Done when: duplicates blocked.

## Phase 3: AI drafts and extension (2 to 3 weeks)
- [ ] `drafts`: facts only from the page, `[ADD: ...]`, versioned prompts. Done when: 10 drafts, all calls logged.
- [ ] `drafts`: checks (no invented numbers or names, no copied 8-word runs, second-model check). Done when: no invented fact reaches review.
- [ ] Extension for the test site editor: show, fill on Accept, never save. Done when: a person applies and saves one approved draft.
- [ ] `inventory`: verify after publish by crawl. Done when: Live only after the crawl confirms.
- [ ] **Check:** 7 of 10 drafts approved with small edits.

## Phase 4: Second site and languages (test site extendmy.life, 2 to 3 weeks)
- [ ] EN + DE inventory, hreflang groups, page types. Done when: matches the 12 sitemaps.
- [ ] `audits`: language rules (R2 §3) and health rules (R2 §1-2). Done when: the known issues show as findings.
- [ ] `content`: native review for German; health rule in code. Done when: neither can be skipped.

## Phase 5: Measure and report (1 to 2 weeks)
- [ ] `reports`: outcomes at 4, 8, 12 weeks vs unchanged pages of the same type. Done when: shown for every change older than 4 weeks.
- [ ] `reports`: weekly report and alerts (email or Emitii). Done when: each site owner gets one a week.

## Later
Deployment (DevOps) · competitor analysis · paid keyword data · RLS + outside accounts · GitHub Secret Protection / CodeQL · Sentry · SBOM · release automation · TypeScript 7 · Python 3.15 · more sites.

## Change log

| Date | Change | Why |
|---|---|---|
| 2026-10-05 | Plan created: phases 0-5, PostgreSQL, DBOS, read-only + extension | Requirements research (R1-R3) |
| 2026-10-06 | Setup phase: uv, pnpm, mise, strict checks, light process rules | Setup research (R4) |
| 2026-10-06 | General tool; small parts; research → experiment → implement | Owner decision |
| 2026-10-06 | Modular monolith by feature; security rules in `CLAUDE.md` | Owner decision |
| 2026-10-06 | Review: removed repeats; session habits moved here from `CLAUDE.md` | Keep both files small |
| 2026-10-06 | `CLAUDE.md` kept as `CLAUDE.template.md` until copied; PDF rebuilt with every plan change (`mise run docs:pdf`); import-linter uses `protected`/`forbidden` contracts | Owner decision; contract check |
| 2026-10-06 | `PLAN.md` and `CLAUDE.md` stay at the repo root; no `CLAUDE.template.md` | Owner decision |
| 2026-10-07 | Frontend: TanStack Router + Table, Tailwind CSS + shadcn/ui; React Hook Form + Zod (Phase 2); Recharts (Phase 5); web folder layout | Owner decision |
| 2026-10-07 | Add `.gitattributes` (LF endings, generated files) and folder READMEs to step 0.2 | Senior review of the repo layout |
| 2026-10-07 | CONTRIBUTING.md and SECURITY.md moved from Should to step 0.2; `db:down` task added; each mise task names the step that makes its input | Owner decision |
