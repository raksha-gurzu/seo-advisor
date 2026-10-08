# seo-advisor: plan

What to build and in which order. How to work: `CLAUDE.md` (repo root).

- General multi-site SEO tool. MyPipit and extendmy.life are test sites, not design targets.
- **Single page first (8 Oct 2026).** The tool fetches one page and does SEO on that page: audit with evidence, then AI suggestions that a person reviews. The whole site comes later (Phase 3).
- Full version for people: `requirements/seo-advisor-requirements.pdf` (same plan, with reasons and diagrams). Keep it in sync with this file.
- Evidence: `requirements/research/` · R1 platform · R2 content SEO · R3 MyPipit · R4 project setup (`§` = section).
- Work on the current step only, in small parts. Tick a task only when its "Done when" is true.
- Plan changes: strike the old task (`~~task~~ — why`), add a change-log line, update the PDF and the ADR.

**Current step:** Phase 1, slice 2: fetch one MyPipit blog post and extract its SEO content (backend), then its screen. Open: slice 1 stages 3-4 (owner walk-through, plan review).

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
| Scope | Single page first: a person pastes a URL of a registered site and a target keyword; the tool fetches that page, audits it, and later suggests fixes. The sitemap list is only a page picker. Whole site in Phase 3. |
| AI provider | DeepSeek (owner decision, 8 Oct 2026), through `integrations/llm`; key in `Settings`. The AI writes text only; code counts and scores. |
| Reviews | Gurzu 2i review, then client approval. Expert review for health; native review for German. |
| Structure | Modular monolith grouped by feature; features talk only through `service.py` (layout in `CLAUDE.md`). |
| Stack | Python, uv, FastAPI, Pydantic, SQLAlchemy (sync), Alembic, DBOS · PostgreSQL + pgvector · React, TypeScript, Vite, pnpm, TanStack Router + Query + Table, Tailwind CSS + shadcn/ui · WXT · mise · Docker Compose. |
| Frontend | React single-page app; no Next.js, no global store. TanStack Router, Query, Table; Tailwind CSS + shadcn/ui (code in the repo). React Hook Form + Zod when the first real form needs them (slice 3 or 4); Recharts from Phase 6. |
| Tenancy | Shared schema, `tenant_id` + `site_id` on every row; row-level security later. |
| Git and CI | Protected `main`, squash merge, Conventional Commits PR titles, Dependabot, gitleaks. 0 approvals while one engineer; 1 when a second joins. |
| Repo | Package `seo_advisor`. Reuse from SEOAdvisor: fetcher + SSRF guard, robots (Protego), title pixel check, AI wrapper. |

## Open questions

- [ ] extendmy.life editor/CMS · [ ] Search Console access for extendmy.life · [ ] Health content rule
- [ ] Native German reviewer · [ ] HWG §11 legal check · [ ] Review cycle for health pages
- [ ] Code owner (Gurzu or client), sets the NOTICE · [ ] AI provider data terms before client pages are sent (R4 §11.7): DeepSeek chosen; check its terms at slice 4 · [ ] DeepSeek API key (owner gives it before slice 4)

## Tool versions (for setup only; afterwards the lock files decide)

Checked 6 Oct 2026; re-check on setup day. Python 3.14.8 · uv 0.12.23 · ruff 0.16.10 · mypy 2.4.0 · pytest 9.1.1 · testcontainers 4.15.0 · FastAPI 0.142.2 · Pydantic 2.13.5 · pydantic-settings 2.15.0 · SQLAlchemy 2.1.3 · psycopg 3.3.6 · Alembic 1.20.0 · DBOS 3.2.0 · structlog 26.1.0 · pytest-recording 0.14.0 · pip-audit 2.10.1 · import-linter 2.15 · Node 24 LTS (26 LTS from 28 Oct) · pnpm 12.9 · Vite 8.3.3 · React 19.3.0 · TypeScript 6.0.3 · oxlint 1.87.0 · Prettier 3.9.9 · Vitest 5.0.3 · Playwright 1.63.0 · WXT 0.21.4 · openapi-typescript 7.13.0 + openapi-fetch 0.17.0 · mise 2026.10.3 · prek 0.5.5 · gitleaks 8.30.1 · `pgvector/pgvector:0.8.7-pg18-trixie`

---

## Phase 0: Set up the repo (about 1 to 1.5 weeks)

> **Changed 7 Oct 2026: feature-first.** ~~Do steps 0.4 to 0.12 before Phase 1.~~ — The owner wants a real feature first, and each setup part when a slice needs it. Steps 0.1 to 0.3 are done. Steps 0.4 to 0.12 keep their tasks and "Done when"; this table says when each one starts.
>
> | Step | Starts with |
> |---|---|
> | 0.4 Database | Slice 2. Only the tables that each slice needs: `tenants`, `sites` (done); `pages`, `page_snapshots` (slice 2); `audit_runs`, `findings` (slice 3); `suggestions`, `llm_calls` (slice 4). |
> | 0.5 API | ~~Slice 3~~ Started 8 Oct 2026 with the web app; structlog is still open |
> | 0.6 Web app | ~~Slice 5~~ Started 8 Oct 2026: each slice now ends with its screen. The extension starts in Phase 4. |
> | 0.7 Hooks, 0.8 CI | Before the first pull request into `dev`, or when the owner decides |
> | 0.9 Claude Code settings | When the owner decides. Recommended soon: deny reads of `.env`. |
> | 0.10 ADRs | Write each ADR when its decision is made or first used. |
> | 0.11 SSRF guard | Slice 1 (the first outbound fetch) |
> | 0.11 AI layer, evals | Slice 4 (AI suggestions, DeepSeek) |
> | 0.12 Final check | Before a second person joins |

**0.1 Machine**
- [x] Install mise, Docker, gh CLI, Claude Code. Git identity `raksha-gurzu`; push via `github.com-gurzu`. Done when: all four report versions and `gh auth status` passes.

**0.2 Skeleton** (R4 §4, §9.5, §18)
- [x] Folders as in `CLAUDE.md` → Structure, plus `packages/api-client`, `docs/{decisions,architecture,design,notes}`, `evals`, `experiments`, `infra`, `.github`, and this `requirements/` folder. `PLAN.md` and `CLAUDE.md` stay at the repo root, not in `requirements/`. Done when: the tree matches. Changed 7 Oct: empty placeholder folders removed; each folder is made with its first file.
- [x] README (5-minute setup), `.gitignore`, `.gitattributes`, `.editorconfig`, `.env.example` (fake values), NOTICE (proprietary), CONTRIBUTING.md, SECURITY.md; a short README in folders that have rules (`docs`, `experiments`, `packages/api-client`). Done when: a new person can follow the README.
- [x] `mise.toml`: tool pins + tasks `setup dev test lint typecheck check audit db:up db:down db:migrate db:seed gen-client evals docs:pdf` (`docs:pdf` rebuilds the requirements PDF; needs Node + `@hpcc-js/wasm-graphviz` and Chromium). Done when: `mise run setup` works on a fresh clone.

**0.3 Python** (R4 §1, §5.3, §11.4)
- [x] `pyproject.toml`, `uv.lock`, groups `dev test lint`, `exclude-newer = "7 days"`, src layout with `core/`, `integrations/`, empty `features/`. Done when: `uv sync --locked` passes.
- [x] ruff (E F W I UP B SIM S ASYNC PT RUF DTZ N), mypy --strict + Pydantic plugin, pytest strict + markers `unit integration e2e live`, import-linter `protected` + `forbidden` contracts (a feature's models and repository are private; not `independence`, which would also block `service.py`), pip-audit. Done when: `mise run check` passes and a forbidden import fails it.
- [x] `Settings` from env, `SecretStr` keys, fail fast. Done when: a missing key stops start-up with a clear message.

**0.4 Database** (R4 §5.1, §13)
- [ ] Compose: pgvector image, volume at `/var/lib/postgresql`, health check, `CREATE EXTENSION vector`. Done when: `mise run db:up` is healthy.
- [ ] SQLAlchemy `Base` + Alembic naming convention and `date_rev_slug` file template. First migration: `uuidv7()` keys, `timestamptz`, tables tenants, ~~users~~, sites, pages, page_snapshots, audit_runs, findings, ~~rules~~ (8 Oct 2026: rules live in code, each with a source; `users` comes with login). Done when: `alembic upgrade head` + `alembic check` pass on an empty DB.
- [ ] Fixtures: testcontainers per session, rollback per test, DBOS reset. Seed: 2 fake sites. Done when: an integration test passes twice in a row.

**0.5 API** (R4 §12, §14)
- [ ] FastAPI `/api/v1` + `/health`, RFC 9457 error handler (write it), request-ID middleware, structlog, `operation_id` per route. Done when: an error returns `application/problem+json` with `request_id`. (8 Oct 2026: all except structlog.)
- [x] `gen-client`: `openapi.json` → `packages/api-client`. Done when: the web app calls `/health` through it.

**0.6 Web and extension** (R4 §2, §3)
- [x] Vite react-ts, strict TS flags (R4 §2.5), oxlint + Prettier, Vitest + Testing Library + MSW, TanStack Router + Query + Table, Tailwind CSS + shadcn/ui (components in `src/shared/ui`); folders as in `CLAUDE.md` → Structure; keep pnpm `minimumReleaseAge`, no install scripts allowed. Check the version, licence and advisories of each library that R4 does not cover. Done when: lint, types, tests and build pass.
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
- [ ] AI layer (slice 4, DeepSeek; reuse SEOAdvisor `providers/llm.py`): provider interface, model and price settings, `llm_calls` table, versioned prompts, recorded fixtures (keys filtered), cost caps per run and day; one key per person and a spend limit per provider. Done when: a recorded call replays in CI with no network.
- [ ] `evals/` with 20 cases and code-based graders. Done when: `mise run evals` prints a score table.

**0.12 Final check**
- [ ] Fresh clone → `mise run setup` → `mise run check` in ≤ 15 min; CI green; planted secret blocked; direct push refused. Done when: a second person or a fresh Claude session does it from the README only.

**Should (weeks 2 to 4):** SSH commit signing · issue forms, labels, milestones · Semgrep + weekly pip-audit job · rising coverage floor · hypothesis tests for scoring · Playwright E2E (2-3 journeys + extension) · OpenTelemetry + local traces · nightly evals with model graders · settings-based feature flags.

---

## Phase 1: One page, end to end (MyPipit blog post, 2 to 3 weeks)

> **Changed 8 Oct 2026: single page first.** ~~Phase 1 = inventory of the whole site, full crawl, scheduled audits, Search Console sync.~~ — The owner wants SEO on one page first. Whole-site tasks move to Phase 3.

**The page loop.** (1) A person pastes a URL of a registered site and types the target keyword. (2) The tool fetches that one page through the safe fetcher. (3) It extracts the SEO content. (4) It audits the page with rules; each finding has evidence. (5) The AI suggests fixes. (6) A person reviews them and copies them into the site editor. (7) The tool checks the page again.

**Slices (order of work).** Each slice is one small pull request that works from end to end. In each slice, build and check the backend first, then its screen in the web app (`make dev`). The coding rules in `CLAUDE.md` do not change.
- [x] Slice 1: spike, then `inventory`: safe fetcher (SSRF guard, robots.txt with Protego, rate limit per host; reuse from SEOAdvisor), sitemap reader, page type and language for each URL. Done when: the MyPipit URL list = its sitemap URLs, and the tests use only the fixtures. The sitemap list is now the page picker.
- [x] Slice 2a: database base, tables `tenants` and `sites`, `make seed` (step 0.4).
- [x] Web app and API for slice 1 (8 Oct 2026): sites list, sitemap list, request trace, page-type rules and URL tester; `make dev`. These screens change in slice 2.
- [ ] ~~Slice 2b: save all sitemap pages (`inventory:sync`).~~ — Single page first: only analysed pages are saved.
- [ ] Slice 2: fetch and extract one page. Spike: fetch 1 MyPipit blog post, save it as a fixture. Backend: `inventory.fetch_page` (URL must be on a registered site), tables `pages` and `page_snapshots` (HTML with a size limit, hash, final URL, status), extractor (title, meta description, canonical, meta robots, `lang`, H1-H6 with levels, images and `alt`, links with anchor text, Open Graph, JSON-LD with properties, main text and word count). Reuse SEOAdvisor `tools/site_checks.py` (`read_tags`, `says_noindex`). Frontend: "Analyse a page" (paste a URL, or pick one from the sitemap list; see the extracted content). Done when: the extracted fields of the fixture page are correct in tests, and the screen shows them for a live MyPipit post.
- [ ] Slice 3: audit one page. Backend: `audits` with rules for blog posts, each with a source (R3), severity and evidence (selector, found, expected); tables `audit_runs`, `findings`; the target keyword is part of the run. First rules: title present, pixel width (reuse SEOAdvisor `tools/snippet_check.py`), keyword in title; meta description present and length (rule of thumb); one H1, keyword in H1, heading order; image `alt` present and not stuffed, stable image URLs; `og:image` present (1200 x 630); canonical present and self; no `noindex`; BlogPosting with author, datePublished, dateModified, headline, image; internal links in `<a href>` with descriptive anchors; readable slug; `lang`; word count (information only). A check that cannot see its data says "unknown", not pass. Frontend: findings with evidence, filter by severity, check the page again. Done when: each finding has evidence and a source, and 2 runs of the same page can be compared.
- [ ] Slice 4: AI suggestions. Backend: step 0.11 AI layer with DeepSeek (reuse SEOAdvisor `providers/llm.py`); `drafts`: suggestions for title, meta description, H1, `alt` text and content notes; facts only from the page, else `[ADD: ...]`; output checked with Pydantic, retry once, then fail; tables `suggestions`, `llm_calls` (model, prompt version, tokens, cost); checks: no invented numbers or names, no copied 8-word runs. Frontend: review each suggestion (accept, edit, reject), copy to the clipboard; never publish. Done when: every AI call is logged, and no invented fact reaches review.
- [ ] Slice 5: run the loop on 5 MyPipit blog posts with the SEO team. Done when: ≥ 90% of findings are correct, and 7 of 10 suggestions are accepted with small edits; else fix the rules or prompts first.

## Phase 2: More page types on MyPipit (1 to 2 weeks)
- [ ] Rules for listings (treks and tours: travel structured data, R3 §5), blog categories and static pages. Done when: each type has its rule set with sources.
- [ ] Page type from the content (title, structured data), not only the URL (spike note: `/marketplace/*` mixes treks, tours and guides). Done when: the fixture pages get the correct type.

## Phase 3: Whole site (scale-up, 2 to 3 weeks)
- [ ] `inventory`: save all sitemap pages; crawler (robots, rate limit per host, snapshots). Done when: a full crawl is stored. (Was Phase 1.)
- [ ] `audits`: DBOS schedules (daily, weekly, monthly); compare runs. Done when: 2 weeks without a manual start. (Was Phase 1.)
- [ ] `search_data`: Search Console sync (R1 §5), keyword-to-page map, one primary keyword per page and language, cannibalisation check. Done when: duplicates are blocked.
- [ ] `content`: items, immutable versions, states and roles, work queue (impact × confidence ÷ effort). Done when: top 10 with reasons. (Was Phase 2.)

## Phase 4: Extension (1 to 2 weeks)
- [ ] Extension for the test site editor: show approved suggestions, fill on Accept, never save. Done when: a person applies and saves one approved suggestion.
- [ ] `inventory`: verify after publish by fetching the page again. Done when: "Live" only after the check confirms.

## Phase 5: Second site and languages (test site extendmy.life, 2 to 3 weeks)
- [ ] EN + DE pages, hreflang groups, page types. Done when: matches the 12 sitemaps.
- [ ] `audits`: language rules (R2 §3) and health rules (R2 §1-2). Done when: the known issues show as findings.
- [ ] `content`: native review for German; health rule in code. Done when: neither can be skipped.

## Phase 6: Measure and report (1 to 2 weeks)
- [ ] `reports`: outcomes at 4, 8, 12 weeks; per page first, then vs unchanged pages of the same type (needs Phase 3). Done when: shown for every change older than 4 weeks.
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
| 2026-10-07 | Step 0.3: `protected` contracts are added per feature (template in `pyproject.toml`); pip-audit checks `uv.lock`; pnpm checks join `check` in step 0.6; the 7-day delay gives ruff 0.16.9 and mypy 2.3.1 | One wildcard contract cannot limit a feature to its own internals; owner decision |
| 2026-10-07 | Feature-first: Phase 1 in 5 slices; steps 0.4 to 0.12 start when a slice needs them; empty placeholder folders removed | Owner decision: see a real feature first and understand why each part exists |
| 2026-10-08 | Backend and frontend in parallel: every slice ends with its screen. API (step 0.5, without structlog) and web app (step 0.6) started early; `make` wraps the mise tasks; the fetcher records each request for the Activity screen; jsdom added for web tests; TypeScript 6.0.3 (openapi-typescript needs the TS API) | Owner decision: see what each feature does |
| 2026-10-08 | Single page first: Phase 1 = one MyPipit blog post end to end (fetch, extract, audit with evidence, DeepSeek suggestions, review). Sitemap list = page picker. Whole site moves to Phase 3; extension Phase 4; extendmy.life Phase 5; reports Phase 6. Backend first, then its screen, in each slice. Docs packages `playwright` and `@hpcc-js/wasm-graphviz` for `mise run docs:pdf` | Owner decision: do SEO on one page before the whole site |
