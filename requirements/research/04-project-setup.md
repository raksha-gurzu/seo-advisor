# Set up everything before feature code: research for "seo-advisor"

Research date: 6 October 2026. Web research only. No repo files changed.

## How to read this file

- Each item has: **Practice**, **Tool + version**, **Why**, **Source** (title, URL, date shown), **Trust**.
- Version numbers come from live registry queries on 2026-10-06 (PyPI JSON API, npm registry, GitHub Releases API, Docker Hub, endoflife.date). The date in brackets is the release date of that version.
- Trust labels:
  - **STANDARD**: standards body or language spec (IETF RFC, NIST, OWASP, PEP, W3C-style spec).
  - **OFFICIAL**: the project's own docs or release notes (uv docs, pytest docs, Playwright docs).
  - **VENDOR**: a company writing about its own paid product or platform (GitHub, Anthropic, Sentry, Thoughtworks Radar is a consultancy opinion, also marked VENDOR-OPINION).
  - **SECONDARY**: blogs, news, comparisons, personal sites (Simon Willison, InfoQ, dev.to).
  - **UNVERIFIED**: I could not confirm it from a primary source. Treat as a lead, not a fact.
- "Not re-fetched" means I cite a well-known stable page from memory and did not open it today.

## Big news since 2025 that changes the defaults (read first)

1. **TypeScript 7.0 (Go native compiler) is GA since 8 July 2026 (7.0.2)**, but it has **no programmatic API until 7.1** (beta planned October 2026). typescript-eslint 8.71.1 has peer range `typescript >=4.8.4 <6.1.0`. The official `create-vite` react-ts template still pins `typescript ~6.0.2` and uses **oxlint** as its linter. So: use TypeScript 6.0.x as the main `typescript` package now. (Sources in topic 2.)
2. **OpenAI acquired Astral (uv, ruff, ty) in March 2026** and **Promptfoo in March 2026**. Both say the tools stay open source (MIT / Apache-2.0). Low risk, but note it. (SECONDARY: Simon Willison, https://simonw.substack.com/p/thoughts-on-openai-acquiring-astral ; Promptfoo blog https://www.promptfoo.dev/blog/promptfoo-joining-openai/ , 2026-03-09.)
3. **Supply-chain "cooldown" is now a default**: pnpm 11 defaults `minimumReleaseAge` to 1 day; Dependabot defaults to a 3-day cooldown (2026-07-14); uv supports `exclude-newer = "7 days"`.
4. **Private repo cost trap**: GitHub secret scanning push protection and CodeQL code scanning on **private** repos need paid add-ons (Secret Protection USD 19, Code Security USD 30 per active committer per month). Free alternatives exist (gitleaks, Semgrep CE, zizmor). See topic 6.
5. **PostgreSQL 18 Docker image moved its data directory.** Mount the volume at `/var/lib/postgresql`, not `/var/lib/postgresql/data`. See topic 5.
6. **Python 3.15.0 final is scheduled for Friday 2026-10-09** (rc3 is out 2026-10-02). Most libraries list 3.14 support; some (DBOS, FastAPI, Pydantic) do not list 3.15 yet. Pin **3.14** now.
7. **Claude Code reads AGENTS.md** (since v2.1.277) when there is no CLAUDE.md. Thoughtworks Radar Vol 34 (April 2026) puts **Claude Code**, **curated shared instructions** and **context engineering** in **Adopt**.

---

## 1. Python project tooling

**1.1 Package and project manager: uv**
- Practice: One `pyproject.toml` (PEP 621 metadata), one committed `uv.lock`, `uv sync --locked` in CI (fails if the lock is stale), dev tools in PEP 735 `[dependency-groups]` (for example `dev`, `test`, `lint`), `required-version` set in `[tool.uv]`.
- Tool + version: uv **0.12.23** (2026-10-03). Still 0.x, but de facto standard.
- Why: one fast tool replaces pip, pip-tools, virtualenv, pyenv; the lockfile makes every machine and CI install the same thing.
- Sources:
  - uv docs, "Managing dependencies" (dependency groups, `default-groups`, special `dev` group): https://docs.astral.sh/uv/concepts/projects/dependencies/ (no date shown; accessed 2026-10-06). OFFICIAL.
  - uv docs, "Locking and syncing" (`--locked` "will raise an error instead of updating the lockfile"; `--frozen` skips the check): https://docs.astral.sh/uv/concepts/projects/sync/ (accessed 2026-10-06). OFFICIAL.
  - uv settings reference (`exclude-newer` accepts "30 days" or ISO 8601 durations; `required-version`): https://docs.astral.sh/uv/reference/settings/ (accessed 2026-10-06). OFFICIAL.
  - PEP 735 "Dependency Groups in pyproject.toml", status **Final**: https://peps.python.org/pep-0735/ . STANDARD.
  - PEP 621 "Storing project metadata in pyproject.toml", status **Final**: https://peps.python.org/pep-0621/ . STANDARD.
  - PEP 751 lock file format (`pylock.toml`), status **Final**; uv can export to it if a tool needs a standard lock: https://peps.python.org/pep-0751/ . STANDARD.
  - Thoughtworks Radar: uv in **Adopt** (April 2025, still referenced in Vol 34): https://www.thoughtworks.com/radar/tools . VENDOR-OPINION.

**1.2 src layout**
- Practice: `apps/api/src/seo_advisor/...` with tests outside the package. Use a build backend (`uv_build` or hatchling) so the package is installed, not imported from the working directory.
- Why: tests run against the installed package, which catches missing files and wrong imports.
- Source: Python Packaging User Guide, "src layout vs flat layout": https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/ (not re-fetched). OFFICIAL (PyPA).

**1.3 Python version pin**
- Practice: `.python-version` = `3.14`; `requires-python = ">=3.14,<3.15"` until 3.15 is supported by DBOS, FastAPI, Pydantic. CI reads the same file.
- Tool + version: CPython **3.14.8** (2026-09-30). 3.15.0 final planned **2026-10-09** (rc3 on 2026-10-02).
- Why: 3.14 is current stable with full library support; 3.15 is days old and DBOS 3.2.0, FastAPI 0.142.2, Pydantic 2.13.5 list classifiers only up to 3.14 (PyPI metadata, checked 2026-10-06).
- Sources: PEP 790 "Python 3.15 Release Schedule": https://peps.python.org/pep-0790/ (accessed 2026-10-06). STANDARD. python.org release API (accessed 2026-10-06). OFFICIAL.
- Note: the brief says "Python 3.12+". 3.12 is in security-only mode until 2028-10; starting a new project on it gives up two years. Recommend 3.14.

**1.4 Lint and format: ruff**
- Practice: `ruff check` and `ruff format` in pre-commit and CI. Start with a broad rule set (`E,F,W,I,UP,B,SIM,S,ASYNC,PT,RUF,DTZ,N`), add more later; never disable rules globally without a comment.
- Tool + version: ruff **0.16.10** (2026-10-01).
- Why: one fast tool replaces flake8, isort, black, pyupgrade, bandit-lite rules (`S`).
- Source: Ruff docs: https://docs.astral.sh/ruff/ (not re-fetched). OFFICIAL.

**1.5 Type checking**
- Practice: **One** checker is the CI gate, in strict mode from day 1. Recommended gate: **mypy --strict with the Pydantic plugin**, or **pyright strict**. Use pyrefly or ty in the editor if you like the speed, but do not gate CI on ty yet.
- Tool + version and status:
  - mypy **2.4.0** (2026-10-01). 2.0 (May 2026) added parallel checking (`-n N`), dropped Python 3.9 targets. Mature, has the Pydantic plugin. Source: mypy blog "Mypy 2.0 Released" https://mypy-lang.blogspot.com/2026/05/mypy-20-relased.html (May 2026). OFFICIAL.
  - pyright **1.1.414** (2026-09-10). Mature, used by Pylance. Source: https://github.com/microsoft/pyright (not re-fetched). OFFICIAL.
  - pyrefly **1.3.2** (2026-09-28). **Stable 1.0 since 12 May 2026**; default checker for Instagram, used by PyTorch. Source: "Pyrefly v1.0 is here!" https://pyrefly.org/blog/v1.0/ (May 2026). OFFICIAL (Meta project).
  - ty **0.0.84** (2026-09-24). **Beta**, stable "targeted for 2026" but not reached. A use-after-free security fix landed in 0.0.84. Thoughtworks Radar Vol 34: **Assess**. Sources: Astral blog https://astral.sh/blog/ty (OFFICIAL); Radar https://www.thoughtworks.com/radar/tools (April 2026, VENDOR-OPINION).
- Why: Pydantic + SQLAlchemy 2 typed models give real value only if a checker enforces them; with AI-written code, the type checker is a cheap reviewer.

**1.6 Tests: pytest family**
- Practice: pytest with **native TOML config** (`[tool.pytest]`, new in pytest 9) and `strict = true`; pytest-xdist for parallel runs; pytest-cov with a coverage floor; markers `unit`, `integration`, `e2e`, `live`.
- Tool + version: pytest **9.1.1** (2026-06-19); pytest-cov **7.1.0** (2026-03-21); pytest-xdist **3.8.0** (2025-07-01); pytest-asyncio **1.4.0**; hypothesis **6.168.5** (2026-10-05).
- Why: strict mode catches typos in markers and config; xdist keeps the suite fast as it grows; hypothesis finds edge cases in pure scoring and parsing code (good fit for SEO scoring functions).
- Sources: pytest docs "Configuration" https://docs.pytest.org/en/stable/reference/customize.html (accessed 2026-10-06), LWN "Pytest 9.0.0 released" https://lwn.net/Articles/1045923/ (SECONDARY). Hypothesis docs https://hypothesis.readthedocs.io/ (not re-fetched). OFFICIAL.
- Caution: `strict = true` turns on future strictness options too; that is fine because pytest is locked in `uv.lock`.

**1.7 Real Postgres in tests: Testcontainers**
- Practice: a session-scoped fixture starts `pgvector/pgvector:0.8.7-pg18-trixie` once; each test runs inside a transaction that is rolled back (see topic 13). CI may use the same Testcontainers path or a GitHub service container.
- Tool + version: testcontainers (Python) **4.15.0** (2026-07-24).
- Why: pgvector, `uuidv7()`, JSONB and DBOS need the real database; SQLite fakes hide bugs.
- Source: "Getting started with Testcontainers for Python" https://testcontainers.com/guides/getting-started-with-testcontainers-for-python/ (not re-fetched). VENDOR (Docker-owned project).

---

## 2. Frontend tooling (web app)

**2.1 Package manager: pnpm**
- Practice: pnpm workspace (`pnpm-workspace.yaml`), `packageManager` field in root `package.json` (Corepack or mise pins it), `pnpm install --frozen-lockfile` in CI, keep the `minimumReleaseAge` default (1 day) or raise it.
- Tool + version: pnpm **12.9.1** (2026-10-03). pnpm 12.0 (late August 2026) is a **Rust rewrite**; lockfiles stay compatible. pnpm 11 (April 2026) added supply-chain defaults: `minimumReleaseAge` 1440 minutes, blocks exotic sub-dependencies, "allow builds" model for install scripts.
- Why: strict `node_modules` stops phantom dependencies; workspaces fit web + extension + shared client; safer install defaults than npm.
- Sources: "pnpm 11.0" https://pnpm.io/blog/releases/11.0 (2026-04); "pnpm 12.0" https://pnpm.io/blog/releases/12.0 (no exact date on page; ~2026-08-26 per secondary sources). OFFICIAL. Socket.dev "pnpm 11 Adds Supply Chain Protection Defaults" (SECONDARY).
- Choice note: pnpm 12 is two months old. If you want maximum safety, pin the latest 11.x; if you accept a new major, 12.9.x is fine. **Unverified**: whether all pnpm 11 security defaults carry over unchanged in 12 (the 12.0 notes do not restate them). Check `pnpm config get minimum-release-age` after install.
- npm alternative: npm **12.2.0**. Works, but no workspace strictness and no default cooldown.

**2.2 Node.js runtime**
- Practice: pin Node in `.node-version` / mise. Use **Node 24 LTS (24.21.0)** now; Node **26 becomes LTS on 2026-10-28**, move then.
- Source: endoflife.date Node.js (accessed 2026-10-06), nodejs.org release schedule. SECONDARY (endoflife) / OFFICIAL (nodejs.org, not re-fetched).
- Note: Vite 8 needs Node `^20.19.0 || >=22.12.0` (npm `engines`), Vitest 5 needs Node 22.12+.

**2.3 Build tool: Vite**
- Tool + version: vite **8.3.3**; @vitejs/plugin-react **6.1.2**; create-vite **9.2.1**.
- Practice: start from `pnpm create vite --template react-ts`, keep its config, add only what you need.
- Why: Vite 8 (March 2026) uses **Rolldown** as its single bundler (dev and build), fewer "works in dev, breaks in prod" cases.
- Source: "Vite 8.0 is out!" https://vite.dev/blog/announcing-vite8 (March 2026). OFFICIAL.

**2.4 React**
- Tool + version: react / react-dom **19.3.0** (2026-09-09). React Compiler (`babel-plugin-react-compiler`) **1.0.0**.
- Practice: React 19 + TanStack Query **5.104.1** for server state. Turn on React Compiler later, once the app works (optional).
- Source: https://react.dev/blog (not re-fetched). OFFICIAL.

**2.5 TypeScript and strict settings**
- Practice: `typescript ~6.0.3` as the project compiler (what create-vite ships). `strict: true` plus `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`, `noFallthroughCasesInSwitch`, `verbatimModuleSyntax`, `noUncheckedSideEffectImports`, `erasableSyntaxOnly`, `moduleResolution: "bundler"`. Optional: run TypeScript 7 (`tsgo`) as a fast extra check in CI.
- Tool + version: typescript **6.0.3** (2026-04-16) for tooling; typescript **7.0.2** (2026-07-08, Go native, 8-12x faster) has **no programmatic API until 7.1**; `@typescript/typescript6` 6.0.2 lets both live side by side.
- Why: typescript-eslint, Vite plugins and editors that use the TS API break on 7.0; strict flags catch the `undefined` bugs AI code often makes.
- Sources: "Announcing TypeScript 7.0" https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/ (July 2026), OFFICIAL; InfoQ https://www.infoq.com/news/2026/08/typescript-7-released/ (2026-08, SECONDARY); typescript-eslint npm `peerDependencies` (checked 2026-10-06), OFFICIAL; create-vite react-ts template `package.json` on GitHub main (checked 2026-10-06), OFFICIAL; TSConfig reference https://www.typescriptlang.org/tsconfig (not re-fetched), OFFICIAL.

**2.6 Lint and format**
- Options (2026):
  - **oxlint 1.87.0** (2026-10-05): stable since v1.0 (June 2025), type-aware rules stable since July 2026 (via tsgo), and it is now the **default linter in the official create-vite React template**. Includes react and react-hooks rules natively.
  - **ESLint 10.12.0**: v10.0.0 (Feb 2026) **removed eslintrc completely**; flat config (`eslint.config.js`) only. Largest plugin ecosystem; slower.
  - **Biome 2.5.15**: lint + format in one tool; type-aware rules approximated without tsc.
- Recommendation: **oxlint** (lint) + **Prettier 3.9.9** (format), or **Biome** alone if you want one tool. Add ESLint 10 flat config only if you need a plugin oxlint lacks.
- Why: fast enough to run on every save and in a Claude Code hook; matches the template so less config drift.
- Sources: ESLint "v10.0.0 released" https://eslint.org/blog/2026/02/eslint-v10.0.0-released/ (Feb 2026), OFFICIAL; InfoQ "oxlint v1 released" https://www.infoq.com/news/2025/08/oxlint-v1-released (Aug 2025), SECONDARY; oxc docs https://oxc.rs/ (not re-fetched), OFFICIAL; Biome https://biomejs.dev/ (not re-fetched), OFFICIAL. Claim "oxlint type-aware rules stable 22 July 2026" comes from a secondary comparison: **unverified**.

**2.7 Unit tests: Vitest**
- Tool + version: vitest **5.0.3** (5.0.0 on 2026-09-03). Breaking changes: mocks cleared before each test by default, un-awaited async assertions fail.
- Practice: Vitest + Testing Library for components; MSW **3.0.2** to mock the API from the generated OpenAPI types.
- Source: Vitest v5.0.0 release https://github.com/vitest-dev/vitest/releases/tag/v5.0.0 (2026-09-03). OFFICIAL.

**2.8 End-to-end tests: Playwright**
- Tool + version: @playwright/test **1.63.0** (2026-09-04).
- Practice: a few critical user journeys only (log in later, run a brief, view a snapshot), run in CI against the built app + real API + Postgres.
- Source: https://playwright.dev/docs/intro (not re-fetched). OFFICIAL.

**2.9 OpenAPI to TypeScript client**
- Practice: **code-first FastAPI** emits OpenAPI 3.1 -> commit `openapi.json` -> generate the TS client into `packages/api-client` -> CI fails if regenerating changes anything (drift check, topic 7).
- Options and versions:
  - **openapi-typescript 7.13.0 + openapi-fetch 0.17.0** (2026-02-11): types only, ~6 kB runtime, 1.0-level stability. Pairs with `openapi-react-query` for TanStack Query.
  - **@hey-api/openapi-ts 0.99.0** (2026-06-22): full SDK, plugins for Zod and TanStack Query; FastAPI docs list it. Still 0.x, breaking changes between minors.
  - **orval 8.40.0** (2026-10-04): hooks + MSW mocks; large output.
- Recommendation: **openapi-typescript + openapi-fetch** (smallest, most stable). Choose hey-api if you want generated TanStack Query hooks and Zod.
- Sources: FastAPI "Generating SDKs" https://fastapi.tiangolo.com/advanced/generate-clients/ (accessed via search 2026-10-06), OFFICIAL; openapi-ts.dev (not re-fetched), OFFICIAL; comparison posts (dev.to, pkgpulse), SECONDARY.

---

## 3. Chrome extension tooling (Manifest V3)

**3.1 Framework**
- Options:
  - **WXT 0.21.4** (2026-08-11): full framework on Vite; file-based entrypoints, auto manifest, Chrome + Firefox + Edge + Safari builds, typed storage and messaging, zip for store. Peer: Vite 6-8, TS >=5.4. Still 0.x.
  - **@crxjs/vite-plugin 3.0.0** (2026-09-24): a Vite plugin, not a framework; you write `manifest.config.ts`; great HMR; Chrome/Edge only; 3.0 is two weeks old.
  - Plain Vite with multiple inputs: possible, but you rebuild what WXT gives (manifest, reload, zips).
- Recommendation: **WXT** for a small team. Pin the exact version (0.x).
- Why: less custom build code; cross-browser later for free; shares Vite, TS and React with the web app.
- Sources: https://wxt.dev/ (not re-fetched), OFFICIAL; comparisons (dev.to "Plasmo vs CRXJS vs WXT 2026", extensionbooster.net), SECONDARY.

**3.2 Testing extensions**
- Practice: Vitest for pure logic (parsers, message handlers with a fake `chrome` API); Playwright E2E with `chromium.launchPersistentContext` using `--disable-extensions-except` and `--load-extension`, using Playwright's **bundled Chromium** (branded Chrome and Edge removed the side-loading flags). Read the extension ID from the service worker URL each run. Expect MV3 service workers to suspend after ~30 s idle.
- Sources: Playwright "Chrome extensions" https://playwright.dev/docs/chrome-extensions (accessed 2026-10-06), OFFICIAL; Chrome for Developers "End-to-end testing for Chrome Extensions" https://developer.chrome.com/docs/extensions/mv3/end-to-end-testing/ (not re-fetched), OFFICIAL.
- Security note: keep extension permissions minimal (`activeTab`, specific host permissions), no remote code (MV3 rule), and treat page content read by the extension as untrusted input to the LLM (topic 11).

---

## 4. Monorepo layout, task runner, tool versions

**4.1 Layout (recommended)**
```text
seo-advisor/
  apps/api/            Python package (src layout), Alembic, DBOS workflows
  apps/web/            React + Vite
  apps/extension/      WXT
  packages/api-client/ generated TS client from openapi.json (no hand edits)
  packages/ui/         (later) shared React components
  docs/                ADRs, C4 diagrams, design docs (Diataxis folders)
  evals/               LLM eval cases + runner
  infra/               docker-compose.yml, seed scripts (no deploy files yet)
  .github/             workflows, templates, CODEOWNERS, dependabot.yml
  pyproject.toml uv.lock pnpm-workspace.yaml package.json mise.toml
  CLAUDE.md (or AGENTS.md + CLAUDE.md that imports it)
```
- Why: one repo keeps the API contract, client and callers in one PR; the generated client is the "shared types" package. Python has one project (a uv workspace only if you later split packages).
- Source: pnpm workspaces https://pnpm.io/workspaces ; uv workspaces https://docs.astral.sh/uv/concepts/projects/workspaces/ (not re-fetched). OFFICIAL.

**4.2 Tool versions + tasks: mise**
- Practice: `mise.toml` pins Python 3.14, Node 24, pnpm, uv; defines tasks (`mise run dev`, `test`, `lint`, `gen-client`, `db:migrate`); loads `.env` for local only. A thin `Makefile` can forward to mise for people who type `make`.
- Tool + version: mise **v2026.10.3** (2026-10-05). Alternatives: just **1.58.0**, Task **v3.54.0**, Make (built in), asdf.
- Why: one file gives every developer and CI the same tool versions and the same commands; Thoughtworks Radar Vol 34 (April 2026) moved mise to **Adopt**.
- Sources: https://mise.jdx.dev/ (not re-fetched), OFFICIAL; Thoughtworks Radar tools https://www.thoughtworks.com/radar/tools (April 2026), VENDOR-OPINION.

---

## 5. Local development environment

**5.1 Docker Compose for PostgreSQL 18 + pgvector**
- Practice: `infra/docker-compose.yml` with `pgvector/pgvector:0.8.7-pg18-trixie` (pin the full tag), health check, named volume **mounted at `/var/lib/postgresql`**, init script that runs `CREATE EXTENSION vector;`. A second database (or schema) for tests if you do not use Testcontainers.
- Versions: PostgreSQL **18.6** (current minor; 18.0 released 2025-09-25); pgvector **0.8.7**.
- Why: same DB version as production will use; PG18 gives native `uuidv7()`.
- PG18 gotcha: from 18 the image sets `PGDATA=/var/lib/postgresql/18/docker` and declares the volume at `/var/lib/postgresql`; mounting the old `/var/lib/postgresql/data` path makes the container refuse to start or lose data.
  - Source: docker-library docs PR https://github.com/docker-library/docs/pull/2582 (OFFICIAL, not re-fetched); postgresql.org mailing list thread (OFFICIAL); several blogs (SECONDARY).
- Sources: PostgreSQL 18 release notes https://www.postgresql.org/docs/release/18.0/ (2025-09-25), OFFICIAL; pgvector Docker Hub tags (checked 2026-10-06), OFFICIAL.

**5.2 Dev containers (optional)**
- Practice: add `.devcontainer/devcontainer.json` later if a new person struggles with setup or you want Claude Code cloud sessions to match local. Not required on day 1 if mise + Compose work.
- Source: Development Container Specification https://containers.dev/ (no version shown; accessed 2026-10-06). STANDARD (open spec, Microsoft-led).

**5.3 Config: 12-factor + pydantic-settings**
- Practice: all config from environment variables, read once by a typed `Settings(BaseSettings)` class (pydantic-settings), validated at start-up (fail fast). Commit `.env.example` with every key and safe dummy values; `.env` is git-ignored. Secrets are `SecretStr`. Different values per environment, same code.
- Tool + version: pydantic-settings **2.15.0** (2026-08-07); pydantic **2.13.5**.
- Why: no secrets in git; same build runs anywhere; typos in config fail at start, not mid-run.
- Sources: The Twelve-Factor App, "III. Config" https://12factor.net/config (not re-fetched; now open source under twelve-factor GitHub org since Nov 2024, https://12factor.net/blog/open-source-announcement), STANDARD-ish (community methodology); pydantic-settings docs https://docs.pydantic.dev/latest/concepts/pydantic_settings/ (not re-fetched), OFFICIAL.

**5.4 Seed data**
- Practice: `mise run db:seed` loads a small fixed data set (2 sites, a few pages, fake keyword rows) through the app's own code or SQL; no real client data in the repo. Use factories (polyfactory **3.3.0** for Pydantic/SQLAlchemy models) in tests.
- Why: every developer and every Claude session starts from the same known state.
- Source: practice; polyfactory https://polyfactory.litestar.dev/ (not re-fetched). OFFICIAL.

---

## 6. Git and GitHub

**6.1 Trunk-based development, short-lived branches**
- Practice: `main` is always releasable; branches live hours to a day or two; three or fewer active branches; merge at least daily; no code freeze; unfinished work hidden behind a flag.
- Sources: DORA "Trunk-based development" https://dora.dev/capabilities/trunk-based-development/ (no date shown; accessed 2026-10-06), OFFICIAL (Google DORA research); https://trunkbaseddevelopment.com/ (not re-fetched), SECONDARY (Paul Hammant).
- Why: DORA links it to higher delivery performance; with AI writing code fast, small batches keep review possible (DORA 2025 AI Capabilities Model lists "working in small batches" and "strong version control practices").

**6.2 Commit messages: Conventional Commits 1.0.0**
- Practice: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `ci:`; scope = app (`feat(api): ...`). With squash merge, enforce the format on the **PR title** (it becomes the commit), for example with a small CI check.
- Version: spec **1.0.0** (stable since 2019). commitlint **21.2.3** if you want local enforcement.
- Why: readable history; enables automatic changelogs later.
- Source: https://www.conventionalcommits.org/en/v1.0.0/ (not re-fetched). STANDARD (community spec).

**6.3 Repository rules (rulesets)**
- Practice on `main`: require PR; require status checks (lint, types, tests, build, migrations, OpenAPI drift); block force push and delete; **require linear history**; allow **squash merge only**; auto-delete head branches; require conversation resolution. For a 1-2 person team, require 0 or 1 approval (an approval rule with one engineer blocks all work); use Claude review + self-review checklist instead.
- Signed commits: **should**. Use SSH signing (`gpg.format ssh`) and upload the key as a signing key; turn on the "require signed commits" rule once both engineers sign. Note: Claude Code commits made on your machine are signed with your key, so this does not block AI work.
- Sources: GitHub Docs "Available rules for rulesets" https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets (accessed 2026-10-06), VENDOR; GitHub Docs "About commit signature verification" / SSH signing (not re-fetched), VENDOR.
- Merge queue: later (needs more traffic to pay off).

**6.4 PR template, CODEOWNERS, issue forms**
- Practice: `.github/pull_request_template.md` (what, why, how tested, screenshots, risk, "AI-assisted: yes/no, reviewed by"); `.github/CODEOWNERS` (both engineers own everything; later split by `apps/`); issue forms in `.github/ISSUE_TEMPLATE/*.yml` (bug, feature, task, spike).
- Source: GitHub Docs on PR templates, CODEOWNERS, issue forms (not re-fetched). VENDOR.

**6.5 Dependency updates: Dependabot or Renovate**
- Dependabot: native, free on private repos; supports **uv** (GA 2025-03-13) and pnpm; **3-day cooldown default since 2026-07-14**; groups to cut PR noise.
- Renovate **44.138.0**: more flexible (`minimumReleaseAge`, auto-merge of patch updates, one dashboard issue); needs the Mend app or self-hosting.
- Recommendation: **Dependabot** (zero setup), weekly schedule, grouped minor+patch per ecosystem (`uv`, `npm` for pnpm, `github-actions`, `docker`). Set its cooldown to match uv `exclude-newer` if you use both.
- Sources: GitHub Changelog "Dependabot version updates now support uv in GA" https://github.blog/changelog/2025-03-13-dependabot-version-updates-now-support-uv-in-general-availability/ (2025-03-13); "Dependabot version updates introduce default package cooldown" https://github.blog/changelog/2026-07-14-dependabot-version-updates-introduce-default-package-cooldown/ (2026-07-14); uv docs "Using uv with Dependabot" https://docs.astral.sh/uv/guides/integration/dependabot/ . VENDOR / OFFICIAL.

**6.6 Secret scanning and push protection**
- Fact: on **private** repos, GitHub secret scanning + push protection need **GitHub Secret Protection** (USD 19 per active committer per month); CodeQL code scanning needs **GitHub Code Security** (USD 30). Both sold to Team plans since 2025-04-01.
- Free practice: **gitleaks v8.30.1** as a pre-commit hook and a CI job (or TruffleHog **v3.98.0**). Turn on GitHub's personal push protection for your user account (free; it covers pushes to public repos only).
- Recommendation: gitleaks now (**must**); buy Secret Protection when Gurzu's budget allows or before external users (**should/later**).
- Sources: GitHub Changelog "Introducing GitHub Secret Protection and GitHub Code Security" https://github.blog/changelog/2025-03-04-introducing-github-secret-protection-and-github-code-security/ (2025-03-04), VENDOR; prices from https://github.com/security/plans (VENDOR) and secondary pricing guides. Exact current prices: re-check on the GitHub page (**prices unverified on the primary page today**).

**6.7 Code scanning (SAST)**
- Options: CodeQL default setup (needs Code Security on private repos); free: **Semgrep CE 1.179.0** in CI with `p/python`, `p/typescript`, `p/owasp-top-ten`; ruff `S` rules (Bandit port) already cover basic Python issues.
- Recommendation: ruff `S` now; Semgrep CE as a **should**; CodeQL **later** (paid on private).
- Source: Semgrep docs https://semgrep.dev/docs/ (not re-fetched), VENDOR.

**6.8 OpenSSF Scorecard**
- Fact: scorecard-action **v2.4.4** supports private repos only with GitHub Advanced Security, otherwise run the CLI with a PAT.
- Recommendation: **later**. Use its checklist by hand: pinned actions, token permissions, branch protection, dependency updates, no dangerous workflows.
- Sources: https://github.com/ossf/scorecard-action (accessed via search 2026-10-06), OFFICIAL; https://scorecard.dev/ (not re-fetched), OFFICIAL.

**6.9 Releases and versioning**
- Practice now: none needed, there is no deployment and no external consumer. Tag milestones by hand if useful.
- Later (when there is a deploy or the extension is published): SemVer 2.0.0 for the extension (Chrome Web Store needs increasing versions), release-please **v17.11.2** (works from Conventional Commits, good for a mixed Python + TS repo) or changesets **3.0.3** (JS-centric).
- Sources: https://semver.org/ (not re-fetched), STANDARD; https://github.com/googleapis/release-please (OFFICIAL).

---

## 7. CI (GitHub Actions)

**7.1 Job layout**
- Practice: one workflow `ci.yml` on `pull_request` and `push` to main, with `concurrency` to cancel old runs, path filters so web-only changes skip Python jobs (but keep required checks green with a final "all checks" job). Jobs:
  1. `lint` (prek/pre-commit run --all-files: ruff, oxlint, prettier, gitleaks, actionlint, zizmor)
  2. `py-types` (mypy or pyright)
  3. `py-test` (pytest -n auto with Postgres service container, coverage report)
  4. `migrations` (alembic upgrade head on empty DB, `alembic check`, downgrade -1 + upgrade on the newest revision)
  5. `openapi-drift` (export OpenAPI from the app, regenerate TS client, `git diff --exit-code`)
  6. `web` (pnpm install --frozen-lockfile, tsc, vitest, vite build)
  7. `extension` (wxt build, vitest)
  8. `e2e` (Playwright; can be nightly at first)
  9. `required` (needs all above; the single required check in the ruleset)
- Why: fast feedback, one required check name that never changes.

**7.2 Caching**
- Practice: `astral-sh/setup-uv` (**v10.2.0**) with `enable-cache: true`; Python version from `.python-version`; `uv sync --locked`. `pnpm/action-setup` (**v6.1.0**) + `actions/setup-node` (**v7.0.0**) with `cache: pnpm`. Playwright browsers cached by version.
- Source: uv docs "Using uv in GitHub Actions" https://docs.astral.sh/uv/guides/integration/github/ (accessed 2026-10-06; its example still shows setup-uv v9.0.0 pinned by SHA), OFFICIAL.

**7.3 Pin actions to full commit SHAs, least-privilege token**
- Practice: every `uses:` pinned to a 40-char SHA with a `# vX.Y.Z` comment (Dependabot updates both); top-level `permissions: contents: read`, raise per job only when needed; `persist-credentials: false` on checkout; never use `pull_request_target` with checkout of PR code; turn on the repo/org policy **"require actions to be pinned to a full-length commit SHA"** (available since 2025-08-15). Lint workflows with **zizmor 1.30.1** and **actionlint 1.7.12**; `pinact` **v5.0.0** can pin existing files.
- Why: tags can be moved by an attacker; SHA pinning is "currently the only way to use an action as an immutable release".
- Sources: GitHub Docs "Secure use reference" https://docs.github.com/en/actions/reference/security/secure-use (accessed 2026-10-06), VENDOR; GitHub Changelog "GitHub Actions policy now supports blocking and SHA pinning actions" https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/ (2025-08-15), VENDOR; zizmor https://docs.zizmor.sh/ (not re-fetched), OFFICIAL.

**7.4 Postgres in CI**
- Practice: `services: postgres: image: pgvector/pgvector:0.8.7-pg18-trixie` with health-check options and `POSTGRES_*` env; tests read `DATABASE_URL`. Or use Testcontainers (Docker is available on ubuntu runners). Pick one path and use it locally too.
- Source: GitHub Docs "Creating PostgreSQL service containers" https://docs.github.com/en/actions/use-cases-and-examples/using-containerized-services/creating-postgresql-service-containers (not re-fetched), VENDOR.

**7.5 Coverage gate**
- Practice: `--cov-fail-under` starting at a modest floor (for example 80 % on `apps/api/src`) and a "no drop" rule; never chase 100 %. Exclude generated code.
- Why: catches untested AI-written code; a floor that rises is easier than a big target.
- Source: pytest-cov docs https://pytest-cov.readthedocs.io/ (not re-fetched), OFFICIAL. Threshold is a judgment call, not a standard.

**7.6 Migrations check**
- Practice: on an empty DB: `alembic upgrade head` -> `alembic check` (fails if models and migrations differ; command exists since Alembic 1.9) -> optional `pytest-alembic` (**0.13.1**) tests for single head, up/down round trip.
- Source: Alembic docs "Autogenerate" and `alembic check` https://alembic.sqlalchemy.org/en/latest/autogenerate.html (not re-fetched), OFFICIAL.

**7.7 pre-commit in CI**
- Practice: run the same hooks in CI (`prek run --all-files` or `pre-commit run --all-files`), so a developer who skipped local hooks still fails. Alternative: pre-commit.ci service (free for open source; paid for private).

---

## 8. Git hooks: pre-commit / prek / lefthook

- Options:
  - **pre-commit 4.6.2** (2026-08-10): the standard; Python based; `.pre-commit-config.yaml`.
  - **prek 0.5.5** (2026-10-05): Rust drop-in that reads the same `.pre-commit-config.yaml`; single binary, faster, built-in monorepo support; used by CPython, FastAPI, Airflow, Ruff, Home Assistant, Django (per project docs and secondary posts). Still 0.x.
  - **lefthook 2.1.17** (2026-10-05): Go, own YAML format, popular in JS teams.
- Recommendation: write a standard `.pre-commit-config.yaml` and run it with **prek** (install via mise); you can switch back to pre-commit with zero file changes.
- Hooks (fast only, under ~5 s): trailing whitespace / end-of-file / check-yaml / check-toml / check-merge-conflict / check-added-large-files; **gitleaks**; **ruff check --fix** + **ruff format**; **oxlint** + **prettier** on changed web files; **uv lock --check** when `pyproject.toml` changes; **actionlint** + **zizmor** on workflow files; optional `commit-msg` hook for Conventional Commits. Keep type checks and tests out of the commit hook (CI and Claude Code hooks run them).
- Sources: https://pre-commit.com/ (not re-fetched), OFFICIAL; https://github.com/j178/prek (OFFICIAL); prek adoption claims from secondary posts (arifsolmaz.github.io, 2026-02) - **adoption list partly unverified**.

---

## 9. Architecture documentation before coding

**9.1 ADRs**
- Practice: `docs/decisions/NNNN-title-with-dashes.md` using **MADR 4.0.0** (sections: Context and Problem Statement, Decision Drivers, Considered Options, Decision Outcome, Consequences, Confirmation, Pros and Cons). Write the first 8-10 ADRs before code: monorepo layout; Python 3.14 + uv; Postgres 18 + pgvector as the only store; DBOS for durable jobs (vs Celery/RQ); code-first OpenAPI + generated client; LLM providers (DeepSeek + checker) behind one interface; read-only rule (engine never publishes); auth approach (deferred); extension framework (WXT); logging/telemetry standard.
- Why: AI assistants and new people read the "why"; stops re-arguing settled choices; Claude Code can be told "follow ADRs".
- Sources: MADR https://adr.github.io/madr/ (4.0.0 released 2024-09-17; accessed 2026-10-06), OFFICIAL; Michael Nygard "Documenting Architecture Decisions" (2011) https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions (not re-fetched), SECONDARY (original author); https://adr.github.io/ (OFFICIAL, community).

**9.2 C4 diagrams**
- Practice: draw **Level 1 System Context** and **Level 2 Container** diagrams now (API, DBOS workers, Postgres, web, extension, LLM providers, Google/SERP data sources, crawler); Level 3 only for complex parts (pipeline); skip Level 4. Keep them as code (Mermaid C4 or Structurizr DSL) in `docs/architecture/` so they are diffed in PRs.
- Source: https://c4model.com/ (no date shown; accessed 2026-10-06), OFFICIAL (Simon Brown).

**9.3 Design docs / RFCs**
- Practice: for each big feature, a 1-3 page design doc in `docs/design/` (context, goals and non-goals, design, alternatives, cross-cutting concerns: security, privacy, cost, observability). Review it in a PR before code. Claude Code's "interview me, then write SPEC.md" workflow fits here.
- Sources: Malte Ubl, "Design Docs at Google" https://www.industrialempathy.com/posts/design-docs-at-google/ (2020; not re-fetched), SECONDARY (ex-Google engineer, not an official Google page); Claude Code best practices "Let Claude interview you" https://code.claude.com/docs/en/best-practices (accessed 2026-10-06), VENDOR.

**9.4 Diataxis for the docs folder**
- Practice: split docs into tutorials (first-run guide), how-to guides (add a provider, run evals), reference (API, settings, schema), explanation (architecture, scoring formulas). Keep it small; generated reference beats hand-written.
- Source: https://diataxis.fr/ (accessed 2026-10-06), OFFICIAL (Daniele Procida).

**9.5 Standard repo files (private repo)**
- README.md: **must** (what it is, 5-minute setup, commands, links to docs).
- CONTRIBUTING.md: **should** (branch, commit, PR, test rules; AI-use rules). Short; CLAUDE.md links to it.
- SECURITY.md: **should** (how to report, secrets handling, what data the system touches). Cheap and helps a later product launch.
- CODE_OF_CONDUCT.md: **later / optional** for a private 2-person repo; Gurzu company policy already covers conduct. Add if the repo becomes public or gets outside contributors.
- Source: GitHub Docs "Setting up your project for healthy contributions" (not re-fetched), VENDOR.

---

## 10. Code quality, review, testing strategy, metrics

**10.1 Code review**
- Practice: Google's reviewer standard: approve when the change "definitely improves the overall code health", even if not perfect; review design, function, complexity, tests, naming, comments, docs. Small CLs: "100 lines is usually a reasonable size ... 1000 lines is usually too large"; separate refactors from features; tests in the same CL.
- Sources: Google Engineering Practices, "Small CLs" https://google.github.io/eng-practices/review/developer/small-cls.html (accessed 2026-10-06) and "The Standard of Code Review" https://google.github.io/eng-practices/review/reviewer/standard.html (not re-fetched). OFFICIAL (Google).

**10.2 Definition of Done (team-level)**
- Suggested DoD: code + tests merged to main via PR; CI green; types strict-clean; migrations reversible or ADR explains why not; OpenAPI and TS client regenerated; docs/ADR updated if a decision changed; no new secrets or TODOs without an issue; AI-written code read line by line by a human; feature behind a flag if incomplete.
- Source: Scrum Guide 2020 (DoD concept) https://scrumguides.org/ (not re-fetched), SECONDARY.

**10.3 Testing strategy**
- Practice: a "trophy-shaped" mix fits this stack: static checks (types, lint) as the base; many fast **unit tests** for pure code (scoring, parsing, rules); a solid layer of **integration tests** against real Postgres (repositories, DBOS workflows, API endpoints via `httpx.AsyncClient`); a few **E2E** Playwright journeys; **contract test** = OpenAPI drift check + generated client type check (no Pact needed while one team owns both sides); **LLM evals** as their own layer (topic 15).
- Sources: Martin Fowler / Ham Vocke "The Practical Test Pyramid" https://martinfowler.com/articles/practical-test-pyramid.html (2018; not re-fetched), SECONDARY; Kent C. Dodds "The Testing Trophy and Testing Classifications" https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications (2021; not re-fetched), SECONDARY; Google Testing Blog "Just Say No to More End-to-End Tests" (2015; not re-fetched), OFFICIAL (Google).

**10.4 DORA metrics**
- Current model (5 metrics): **Throughput**: change lead time, deployment frequency, failed deployment recovery time. **Instability**: change fail rate, **deployment rework rate** (the fifth, added 2024).
- Practice now: you cannot measure deploy metrics without deployment. Track **PR lead time** (open to merge) and **PR size** from GitHub; add the five when DevOps sets up deploys.
- Sources: DORA "DORA's software delivery performance metrics" https://dora.dev/guides/dora-metrics/ (last updated 2026-01-05), OFFICIAL; DORA 2025 "State of AI-assisted Software Development" and "AI Capabilities Model" (seven capabilities) https://dora.dev/research/publications/ (2025), OFFICIAL; Thoughtworks Radar: DORA metrics **Adopt** (April 2026), VENDOR-OPINION. A 2026 DORA report was **not found** as of today.

**10.5 Feature flags**
- Practice: start with **settings-based flags** (pydantic-settings booleans + a `/api/v1/config` endpoint the web app reads); no flag service yet. Name, owner, and removal date for each flag. Consider OpenFeature (CNCF) SDKs later if you need per-site or per-user targeting.
- Source: Pete Hodgson, "Feature Toggles" on martinfowler.com https://martinfowler.com/articles/feature-toggles.html (2017; not re-fetched), SECONDARY; https://openfeature.dev/ (not re-fetched), OFFICIAL (CNCF).

---

## 11. Security baseline

**11.1 OWASP ASVS 5.0, Level 1**
- Fact: ASVS **5.0.0 released May 2025**; ~350 requirements in 17 chapters; Level 1 slimmed down as the minimum for any app.
- Practice: copy the L1 items for these chapters into a checklist issue: encoding and injection (parameterized queries via SQLAlchemy only, no f-string SQL), validation (Pydantic at every boundary), web frontend security (CSP, no `dangerouslySetInnerHTML` on page content), API and web service, authentication and session (when auth lands), secure communication (TLS, later at deploy), configuration (no debug in prod, secrets from env), data protection, logging (no secrets/PII in logs), error handling (no stack traces to clients).
- Source: OWASP ASVS project https://owasp.org/www-project-application-security-verification-standard/ and https://github.com/OWASP/ASVS (not re-fetched); release date from secondary sources (softwaremill.com). STANDARD.

**11.2 NIST SSDF (SP 800-218)**
- Fact: SSDF **v1.1 (SP 800-218, Feb 2022) is the current final**. **SP 800-218 Rev. 1 (SSDF v1.2) is still an Initial Public Draft** (published 2025-12-17, comments closed 2026-01-30); it adds PO.6 continuous improvement and PW.10 robust updates.
- Practices that fit a 2-person team: PO.1 write down security requirements (this checklist); PO.3 secure toolchain (pinned tools, SHA-pinned actions); PO.5 secure environments (no prod secrets on laptops, least-privilege tokens); PS.1 protect code (rulesets, signed commits, 2FA); PS.2 integrity (lockfiles with hashes); PW.4 reuse vetted components (lockfiles, cooldowns, audit); PW.7 code review + SAST; PW.8 test executable code (CI); RV.1 vulnerability intake (Dependabot alerts, `pip-audit`, `osv-scanner`).
- Sources: NIST SP 800-218 https://csrc.nist.gov/pubs/sp/800/218/final (2022-02; not re-fetched), STANDARD; SP 800-218 Rev. 1 IPD https://csrc.nist.gov/pubs/sp/800/218/r1/ipd (2025-12-17; accessed 2026-10-06), STANDARD.

**11.3 SBOM (CycloneDX / SPDX)**
- Recommendation: **later** (when you ship to a client or publish the extension). It costs little to add one CI job then: `cyclonedx-py` (cyclonedx-bom **7.5.0**) for Python, `cdxgen`/`@cyclonedx/cyclonedx-npm` for pnpm. Lockfiles already hold the data.
- Why later: no deployment and no customer asking yet; SSDF draft v1.2 references SBOM emission, so a product launch will need it.
- Sources: https://cyclonedx.org/ and https://spdx.dev/ (not re-fetched), STANDARD (ECMA-424 / ISO/IEC 5962).

**11.4 Dependency pinning, hashes, audit**
- Practice: `uv.lock` and `pnpm-lock.yaml` committed (both record hashes/integrity); CI installs with `--locked` / `--frozen-lockfile`; cooldown on new releases (pnpm default 1 day, uv `exclude-newer = "7 days"`, Dependabot 3-day default); pnpm "allow builds" list for packages that need install scripts; `pip-audit` **2.10.1** or `osv-scanner` **v2.6.0** in CI weekly; Dependabot security alerts on.
- Sources: pnpm 11 release notes (above); uv settings (above); Dependabot cooldown changelog (above). OFFICIAL/VENDOR.

**11.5 Secret management**
- Practice now: secrets only in local `.env` (git-ignored) and GitHub Actions secrets; one key per person per provider (DeepSeek, Gemini, Serper) so you can revoke one; spend limits set at each provider; gitleaks in hooks and CI; Claude Code deny rules for `.env*` reads (topic 16). Later, DevOps picks a secret store (cloud secret manager, Vault, SOPS).
- Source: OWASP Secrets Management Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html (not re-fetched). STANDARD.

**11.6 SSRF guard for the crawler (critical for this product)**
- Practice: the crawler fetches user-supplied and sitemap URLs, so: allow only `http`/`https`; resolve DNS yourself, reject if **any** A/AAAA answer is private, loopback, link-local, multicast, CGNAT or cloud metadata (`127.0.0.0/8`, `10/8`, `172.16/12`, `192.168/16`, `169.254/16` incl. `169.254.169.254`, `100.64/10`, `::1`, `fc00::/7`, `fe80::/10`); **connect to the validated IP** (pin it; re-resolving allows DNS rebinding); handle redirects manually and re-check each hop; cap redirects, size, time; block non-standard ports unless needed; run crawler workers with no access to internal networks once deployed. Put this in one `providers/` module with unit tests for each blocked range and a rebinding test.
- Source: OWASP "Server-Side Request Forgery Prevention Cheat Sheet" https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html (accessed 2026-10-06; quote: "Bind the connection to a validated address ... checking DNS answers separately does not prevent DNS rebinding"). STANDARD.

**11.7 LLM security**
- OWASP Top 10 for LLM Applications **2025**: LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM03 Supply Chain, LLM04 Data and Model Poisoning, LLM05 Improper Output Handling, LLM06 Excessive Agency, LLM07 System Prompt Leakage, LLM08 Vector and Embedding Weaknesses, LLM09 Misinformation, LLM10 Unbounded Consumption. Also **OWASP Top 10 for Agentic Applications 2026** (ASI01-ASI10, released 2025-12-09).
- Practice for seo-advisor:
  - Prompt injection (LLM01): crawled pages and competitor pages are **untrusted data**. Wrap them in clear delimiters, tell the model they are data, give the model **no tools that write or send** while it reads page text, and validate every output with Pydantic.
  - Sensitive info (LLM02): never send API keys, client credentials or other clients' data in prompts; log prompts with redaction; check DeepSeek data-retention terms before sending client pages (**unverified**: DeepSeek's current retention and training policy; read their terms).
  - Improper output handling (LLM05): render LLM text as text in React (no raw HTML); never execute or SQL-interpolate LLM output.
  - Excessive agency (LLM06): the engine never publishes (already a product rule); human approves drafts.
  - Misinformation (LLM09): the existing "no invented facts" rule + checker model + `[ADD: ...]` placeholders.
  - Unbounded consumption (LLM10): per-run and per-day cost caps, token limits, timeouts, retries with backoff.
  - Vector weaknesses (LLM08): tenant/site ID on every embedding row and every similarity query.
- Sources: OWASP Top 10 for LLM Applications 2025 PDF https://owasp.github.io/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf (Nov 2024), STANDARD; OWASP GenAI "Top 10 for Agentic Applications" https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ (2025-12-09), STANDARD.

---

## 12. Observability from day 1

**12.1 Structured logging**
- Practice: **structlog 26.1.0** on top of stdlib `logging` (so library logs flow through the same pipeline); JSON to stdout in non-dev, pretty console in dev; `contextvars` to bind `request_id`, `run_id`, `site_id`, `workflow_id` once per request/job; one "canonical" summary line per request and per pipeline step. Never log secrets or full page bodies.
- Why: logs you can query from day 1; same code works when DevOps adds a log store.
- Source: structlog "Logging Best Practices" https://www.structlog.org/en/stable/logging-best-practices.html (accessed 2026-10-06; "log to unbuffered standard out and let other tools take care of the rest"), OFFICIAL.
- stdlib-only alternative: `logging` + a JSON formatter (`python-json-logger`). Works, more boilerplate for context binding.

**12.2 Request IDs**
- Practice: middleware reads `X-Request-ID` (or creates a UUIDv7), binds it to log context, returns it in the response and in Problem Details errors; the web app shows it in error toasts; DBOS workflow IDs logged with the request ID that started them.

**12.3 OpenTelemetry traces**
- Tool + version: opentelemetry-api / -sdk **1.45.0** (2026-09-25). Traces and metrics are **stable** in Python; logs signal still in development.
- Practice: install the SDK + FastAPI, httpx, SQLAlchemy/psycopg instrumentations now, export to console or a local Jaeger/Grafana LGTM container in Compose; leave the real backend to DevOps (OTLP endpoint is just an env var). Add spans around each pipeline step and each LLM call (attributes: model, tokens, cost, latency) following the OpenTelemetry **GenAI semantic conventions** (status: development - **check before relying on attribute names**).
- Sources: OpenTelemetry Python https://opentelemetry.io/docs/languages/python/ (accessed via search 2026-10-06), OFFICIAL (CNCF); FastAPI "OpenTelemetry" https://fastapi.tiangolo.com/advanced/opentelemetry/ (**unverified** that this page exists in official FastAPI docs; it appeared in search results only).

**12.4 LLM call logging**
- Practice: one table `llm_calls` (run_id, step, provider, model, prompt_version, input_tokens, output_tokens, cost_usd, latency_ms, status, error, prompt_hash, response JSON, created_at). This gives cost tracking, debugging and eval data in one place, inside Postgres you already run. Optional later: Langfuse (**4.17.0**, self-hostable, OSS) or Logfire (**5.1.1**, Pydantic's hosted service, VENDOR).
- Why: Anthropic's eval guidance says "reading transcripts is how you verify that your eval is measuring what actually matters"; you need the transcripts stored.

**12.5 Error tracking (Sentry)**
- Recommendation: **later** (with deployment). Before deployment, errors show in your terminal and logs. When you deploy, sentry-sdk **2.71.0**; free Developer plan is 1 user, 5k errors/month (VENDOR pricing via secondary sources, **unverified on sentry.io today**). Self-hosted GlitchTip or Sentry are options DevOps may prefer.

---

## 13. Database practices

**13.1 SQLAlchemy 2.x typed ORM**
- Tool + version: SQLAlchemy **2.1.3** (2.1.0 final 2026-09-24). Changes: psycopg (v3) is the default PostgreSQL driver; `greenlet` (asyncio) is no longer installed by default, use `sqlalchemy[asyncio]`.
- Practice: `DeclarativeBase` + `Mapped[...]` + `mapped_column()`; a `MetaData(naming_convention=...)`; repositories return Pydantic models to the API layer (do not leak ORM objects into responses); psycopg **3.3.6** driver; pgvector **0.5.0** Python package for the `Vector` type.
- Choice: sync vs async. DBOS workflows are sync-friendly; FastAPI works with both. **Pick one per process** and write an ADR. Async (`create_async_engine` + psycopg async) suits I/O-heavy API; sync is simpler with DBOS steps.
- Sources: "SQLAlchemy 2.1.0 Released" https://www.sqlalchemy.org/blog/2026/09/24/sqlalchemy-2.1.0-released/ (2026-09-24), OFFICIAL; "What's New in SQLAlchemy 2.1" https://www.sqlalchemy.org/docs/21/changelog/migration_21.html, OFFICIAL.

**13.2 Alembic conventions**
- Tool + version: alembic **1.20.0** (2026-09-11).
- Practice:
  - Naming convention on `MetaData` (from Alembic docs): `ix_%(column_0_label)s`, `uq_%(table_name)s_%(column_0_name)s`, `ck_%(table_name)s_%(constraint_name)s`, `fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s`, `pk_%(table_name)s`. Set it **before the first migration**.
  - File template with date + slug: `file_template = %%(year)d%%(month).2d%%(day).2d_%%(rev)s_%%(slug)s`.
  - Autogenerate, then **read and edit** every migration (autogenerate misses renames, some type changes, server defaults, extensions, pgvector indexes).
  - One migration per PR where possible; never edit a merged migration.
  - Downgrade policy: write `downgrade()` for schema changes while there is no production data; for data-destroying changes, the ADR/PR states "forward-only" and why.
  - Enable `CREATE EXTENSION IF NOT EXISTS vector` in the first migration.
  - CI: upgrade on empty DB + `alembic check` (topic 7.6).
- Source: Alembic "The Importance of Naming Constraints" https://alembic.sqlalchemy.org/en/latest/naming.html (accessed 2026-10-06), OFFICIAL.

**13.3 Connection pooling**
- Practice: SQLAlchemy `QueuePool` defaults with `pool_pre_ping=True`; set `pool_size`/`max_overflow` from settings; remember DBOS keeps its own system-database connections, count both against Postgres `max_connections`. PgBouncer is DevOps's choice later (transaction mode needs care with prepared statements in psycopg).
- Source: SQLAlchemy "Connection Pooling" https://docs.sqlalchemy.org/en/21/core/pooling.html (not re-fetched), OFFICIAL.

**13.4 Test database strategy**
- Practice: one container per test session; schema built once with `alembic upgrade head` (tests the migrations too); each test runs in a **connection-level transaction with SAVEPOINTs, rolled back at the end** ("join the session into an external transaction" recipe); DBOS tests use their own fixture that calls `DBOS.destroy()` then `DBOS.reset_system_database(truncate=True)` before each test (DBOS also allows SQLite for its system DB in tests).
- Sources: SQLAlchemy "Joining a Session into an External Transaction (such as for test suites)" https://docs.sqlalchemy.org/en/21/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites (not re-fetched), OFFICIAL; DBOS "Testing Your App" https://docs.dbos.dev/python/tutorials/testing (accessed 2026-10-06), OFFICIAL. DBOS **3.2.0** (2026-09-29).

**13.5 IDs and time**
- Practice: primary keys `uuid` with server default **`uuidv7()`** (native in PostgreSQL 18; time-ordered, good for B-tree indexes, RFC 9562); `timestamptz` everywhere (`created_at`, `updated_at` default `now()`), store UTC, convert in the UI; ruff `DTZ` rules ban naive datetimes in Python.
- Sources: PostgreSQL 18 release notes https://www.postgresql.org/docs/release/18.0/ (2025-09-25), OFFICIAL; RFC 9562 "Universally Unique IDentifiers (UUIDs)" https://www.rfc-editor.org/rfc/rfc9562 (May 2024; not re-fetched), STANDARD.

---

## 14. API practices

**14.1 Code-first with FastAPI**
- Practice: **code-first** (Pydantic models are the source of truth), export `openapi.json` in CI and commit it, generate the TS client, fail on drift. Give every route an explicit `operation_id` (clean client function names) and `response_model`; tag routes by area.
- Why: one team owns both ends; Pydantic is already the contract (CLAUDE.md rule "Pydantic everywhere"); OpenAPI-first adds a second source of truth for little gain here.
- Tool + version: fastapi **0.142.2** (2026-09-30).
- Source: FastAPI docs "Generating SDKs" (above), OFFICIAL.

**14.2 Versioning**
- Practice: prefix `/api/v1` from day 1; additive changes only within v1; the extension (installed copies lag behind) is the main reason to keep old fields working.
- Source: Google AIP-185 "API Versioning" https://google.aip.dev/185 (not re-fetched), OFFICIAL (Google).

**14.3 Error format: RFC 9457 Problem Details**
- Practice: all errors as `application/problem+json` with `type`, `title`, `status`, `detail`, `instance`, plus extensions `request_id` and `errors` (field errors from Pydantic). Write one exception handler set; document the schema in OpenAPI.
- Note: **FastAPI does not have built-in Problem Details**. PR #15951 ("Add RFC 9457 Problem Details ... opt-in via problem_details=True", opened 2026-07-07) was **closed without merge** (GitHub API, checked 2026-10-06). A search-result claim that it shipped is wrong. Write your own small handler (about 50 lines) or use a library such as `fastapi-rfc9457` (SECONDARY, check maintenance before use).
- Source: RFC 9457 "Problem Details for HTTP APIs" https://www.rfc-editor.org/rfc/rfc9457 (July 2023, Proposed Standard, obsoletes RFC 7807; accessed 2026-10-06). STANDARD.

**14.4 Pagination**
- Practice: **cursor (keyset) pagination** for growing lists (pages, keywords, runs), using `(created_at, id)` or the UUIDv7 id as the cursor; response `{items, next_cursor}`; limit with a max. Offset only for small admin tables.
- Source: Google AIP-158 "Pagination" https://google.aip.dev/158 (not re-fetched), OFFICIAL (Google).

**14.5 Auth plan (later)**
- Practice now: write the ADR and leave a seam (a `current_user` dependency that returns a fixed local user). Later options: OIDC with Google Workspace (Gurzu staff), session cookies for the web app, scoped tokens for the extension. Follow OWASP ASVS chapter on authentication when it lands.
- Source: OWASP Authentication Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html (not re-fetched), STANDARD.

---

## 15. LLM engineering setup

**15.1 Prompts as versioned files**
- Practice: `apps/api/src/seo_advisor/prompts/<name>/v3.md` (or Jinja) with a header (version, model, expected output model); code loads by name + version; `prompt_version` stored on every `llm_calls` row. Changing a prompt = PR + eval run.
- Why: you can compare versions, roll back, and tie eval scores to a prompt version.

**15.2 Model config in settings**
- Practice: provider, model ID, temperature, max tokens, price per 1M tokens, timeout, retries all in `Settings`; no model name in code. Provider interface (`LLMClient.complete(schema=...)`) so DeepSeek and the checker model swap in one file. Structured output validated by Pydantic; retry once then raise (your existing rule).
- Source: Anthropic "Building effective agents" https://www.anthropic.com/engineering/building-effective-agents (2024-12-19): start with direct API calls, add frameworks only when you understand them; "Success ... isn't about building the most sophisticated system. It's about building the right system". VENDOR (Anthropic engineering).

**15.3 Eval harness in repo from day 1**
- Practice: `evals/` with 20-50 real cases to start (pages + expected properties), **code-based graders first** (schema valid, no invented numbers, required topics present, placeholders used), then **model-based graders** with a rubric for fuzzy qualities, plus occasional **human review**; separate **regression evals** (should stay ~100 %) from **capability evals** (hard, start low); run on every prompt or model change and nightly; store transcripts and scores.
- Tool options: plain **pytest**-based runner (simplest, same tooling; recommended to start); **DeepEval 4.2.8** (pytest-style, many metrics); **promptfoo 0.124.0** (YAML configs, red-teaming; now owned by OpenAI, stays OSS).
- Sources: Anthropic "Demystifying evals for AI agents" https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents (2026-01-09): "Start with 20-50 tasks", grader types, capability vs regression, pass@k / pass^k, "Reading transcripts ...". VENDOR (Anthropic engineering). Anthropic docs "Define success criteria and build evaluations" https://docs.claude.com/en/docs/test-and-evaluate/develop-tests (not re-fetched), VENDOR.

**15.4 Recorded fixtures**
- Practice: **pytest-recording 0.14.0** (wraps **vcrpy 8.3.0**) to record HTTP calls to LLM and data providers once, then replay in CI (`--record-mode=none` in CI); filter `Authorization` and API-key headers and query params; re-record on purpose. For pure HTTP mocking use **respx 0.23.1** (httpx).
- Why: tests are free, fast and deterministic; your CLAUDE.md already says "tests must not hit paid APIs".
- Source: https://github.com/kiwicom/pytest-recording (not re-fetched), OFFICIAL.

**15.5 Cost tracking**
- Practice: compute cost from token counts x price table in settings on every call; sum to `run.cost_usd`; daily cap and per-run cap that stop the run; weekly cost report query.

**15.6 Context engineering for the product's own LLM calls**
- Practice: give each call only the needed page text and facts; keep tool lists small and well documented; structured outputs.
- Sources: Anthropic "Effective context engineering for AI agents" https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (2025-09-29), VENDOR; Anthropic "Writing effective tools for AI agents" https://www.anthropic.com/engineering/writing-tools-for-agents (2025; not re-fetched), VENDOR.

---

## 16. AI-assisted development (Claude Code) practices

**16.1 Instruction files**
- Practice: one root `CLAUDE.md` under ~200 lines (Anthropic's stated target) with: commands Claude cannot guess, rules that differ from defaults, architecture pointers (link ADRs), gotchas. Use `.claude/rules/` (path-scoped) or nested `CLAUDE.md` in `apps/web`, `apps/extension`, `apps/api` for area rules. Personal notes in `CLAUDE.local.md` (git-ignored). Prune it like code; run `/doctor` audit.
- AGENTS.md: if you want Copilot, Codex, Cursor etc. to share rules, put content in `AGENTS.md` and have `CLAUDE.md` contain `@AGENTS.md` (Claude Code reads AGENTS.md directly only when no CLAUDE.md exists; supported since v2.1.277). AGENTS.md is now stewarded by the Agentic AI Foundation (Linux Foundation).
- Sources: Claude Code docs "How Claude remembers your project" https://code.claude.com/docs/en/memory (accessed 2026-10-06; "target under 200 lines per CLAUDE.md file"), VENDOR; "Best practices for Claude Code" https://code.claude.com/docs/en/best-practices (accessed 2026-10-06; "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!"), VENDOR; https://agents.md/ (accessed 2026-10-06), OFFICIAL (open format); Thoughtworks Radar: **Curated shared instructions for software teams - Adopt**, **Context engineering - Adopt** (April 2026), **AGENTS.md - Trial** (Nov 2025), VENDOR-OPINION.

**16.2 Verification loop (the most important practice)**
- Practice: give Claude a check it can run (tests, type check, build, screenshot). Enforce with a **Stop hook** or `/goal`; run a **fresh-context reviewer subagent** or `/code-review` before calling work done; ask for evidence (command + output), not claims.
- Source: Claude Code best practices (above): "Give Claude a check it can run ... It's the difference between a session you watch and one you walk away from." VENDOR.

**16.3 Explore -> plan -> implement -> commit; specs**
- Practice: plan mode for multi-file or unclear work; skip it for one-line diffs. For big features, have Claude interview you and write a spec, then implement in a fresh session.
- Source: Claude Code best practices (above). VENDOR. Thoughtworks Radar: spec-driven development **Assess** (Nov 2025), VENDOR-OPINION.

**16.4 Hooks, permissions, sandbox, skills, subagents (set up before feature code)**
- `.claude/settings.json` (committed):
  - **permissions.deny**: `Read(./.env)`, `Read(./.env.*)`, `Read(**/*.pem)`, `Bash(curl:*)` to unknown hosts, `Bash(git push --force:*)`; **allow**: `uv run pytest`, `pnpm test`, `ruff`, `mise run *`.
  - **sandbox** on (filesystem + network isolation; Anthropic reports 84 % fewer permission prompts internally).
  - **hooks**: PostToolUse on Edit/Write -> `ruff format` + `ruff check --fix` for `.py`, `prettier`/`oxlint --fix` for `.ts/.tsx`; PreToolUse -> block edits to merged migrations and `uv.lock`/`pnpm-lock.yaml` by hand; Stop -> fast test subset.
  - **skills** (`.claude/skills/*/SKILL.md`): `new-endpoint`, `new-migration`, `new-provider`, `run-evals`, `add-adr`.
  - **subagents** (`.claude/agents/*.md`): `security-reviewer`, `test-writer`, `migration-reviewer`.
- Security of AI agents: no secrets in context (deny rules, `.env` never opened, keys only via env), treat fetched web pages and issue text as untrusted (prompt injection), use `/sandbox`, review every command that touches the network or git remote.
- Sources: Claude Code docs: best practices (above), "Security" https://code.claude.com/docs/en/security (not re-fetched), hooks guide https://code.claude.com/docs/en/hooks-guide (not re-fetched), skills https://code.claude.com/docs/en/skills (not re-fetched), sub-agents https://code.claude.com/docs/en/sub-agents (not re-fetched). VENDOR. Anthropic engineering "Claude Code sandboxing" (2025; 84 % figure from a mirror of the post, **original not re-fetched**).

**16.5 Test-first with AI and reviewing AI code**
- Practice: red/green TDD: write or have Claude write failing tests, **confirm they fail**, then implement; keep PRs small; a human reads every line before merge; watch for "complacency with AI-generated code" (Thoughtworks **Hold**, Nov 2025) and "cognitive debt" (Radar Vol 34 theme); DORA 2025: AI is an amplifier of existing practices, both good and bad.
- Sources: Simon Willison, "Agentic Engineering Patterns" https://simonwillison.net/2026/Feb/23/agentic-engineering-patterns/ (2026-02-23) and its "Red/green TDD" chapter, SECONDARY (respected practitioner); Thoughtworks Radar Vol 34 PDF https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2026/04/tr_technology_radar_vol_34_en.pdf (April 2026), VENDOR-OPINION; DORA 2025 report (above), OFFICIAL.

**16.6 Other assistants (brief)**
- GitHub Copilot reads `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` (with `applyTo`), and `AGENTS.md`; Cursor uses `.cursor/rules/`. If someone uses them, keep the real content in AGENTS.md and point others at it, to avoid four copies.
- Source: GitHub Changelog "Copilot coding agent now supports AGENTS.md custom instructions" https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/ (2025-08-28), VENDOR.

---

## 17. Project management

- **Issue forms** (`.github/ISSUE_TEMPLATE/`): bug, feature, task, spike, ADR-proposal. Each feature issue has acceptance criteria and a "how we verify" line (doubles as Claude's verification target).
- **Labels** (small set): `type:feature|bug|chore|docs|spike`, `area:api|web|extension|db|llm|infra`, `priority:p1|p2|p3`, `status:blocked`, `ai-assisted`, `good-first-task`. Manage labels as code (a small script or `gh label` commands) so they are reproducible.
- **Milestones** = phases (Phase 0 Setup, Phase 1 MyPipit pilot MVP, ...), each with a goal and a date.
- **GitHub Projects** (v2): one board with fields Status, Area, Phase, Size (S/M/L), Iteration (2 weeks). Use built-in workflows (auto-add issues, move to Done on close).
- **Definition of Ready**: problem stated, acceptance criteria, verification step, dependencies known, size S or M (split L), design doc/ADR linked if needed.
- **Definition of Done**: see 10.2.
- **Estimating**: T-shirt sizes or "fits in one PR / one day" rule; track throughput (issues closed per week) instead of story points for a 2-person team. Re-plan each iteration.
- Sources: GitHub Docs "About Projects" https://docs.github.com/en/issues/planning-and-tracking-with-projects (not re-fetched), "Syntax for issue forms" (not re-fetched). VENDOR. DoR/DoD and sizing are common Agile practice (Scrum Guide 2020, SECONDARY); no single authority.
- Note: the team also logs time in Emitii; link each GitHub milestone/issue to the Emitii feature card so the two do not drift.

---

## 18. Licensing for a private repo

- Practice: no open-source license file. Add a short `LICENSE` or `NOTICE` that says "Copyright (c) 2026 Gurzu. All rights reserved. Proprietary and confidential." and confirm with Gurzu/client contract who owns the code (Gurzu vs MyPipit client) before the repo grows. Check third-party licenses of dependencies (all chosen tools are MIT/Apache/BSD; pgvector is PostgreSQL license). A license checker (for example `pip-licenses`, `license-checker` for npm) is a **later** CI job.
- Source: GitHub Docs "Licensing a repository" https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository (accessed 2026-10-06): "Without a license, the default copyright laws apply, meaning that you retain all rights to your source code and no one may reproduce, distribute, or create derivative works from your work." VENDOR. Not legal advice; client contract terms override.

---

## Minimum setup before feature code (ranked)

### MUST (do before the first feature PR; about 3-5 days for 1-2 engineers)

1. **Repo skeleton**: monorepo folders (4.1), README, `.gitignore`, `.env.example`, proprietary notice (18).
2. **Tool pins**: `mise.toml` with Python 3.14, Node 24, uv 0.12.x, pnpm; `.python-version`; `packageManager` field (1.3, 2.1, 4.2).
3. **Python base**: `pyproject.toml` + `uv.lock`, src layout, dependency groups, ruff config, strict type checker (mypy or pyright), pytest 9 `[tool.pytest]` strict, pydantic-settings `Settings` that fails fast (1.1-1.6, 5.3).
4. **Database base**: Compose with `pgvector/pgvector:0.8.7-pg18-trixie` mounted at `/var/lib/postgresql`; SQLAlchemy 2.1 `Base` with naming convention; Alembic with date-slug file template; first migration (extension `vector`, `uuidv7()` PKs, `timestamptz`); test fixtures (container + rollback per test, DBOS reset) (5.1, 13).
5. **API base**: FastAPI app with `/api/v1`, health endpoint, RFC 9457 error handler, request-ID middleware, structlog JSON/pretty config (12.1, 12.2, 14).
6. **Web + extension base**: create-vite react-ts (TS 6.0.x strict flags), oxlint + Prettier, Vitest; WXT extension skeleton; generated `packages/api-client` from `openapi.json` (2, 3).
7. **Hooks**: `.pre-commit-config.yaml` run by prek: hygiene, gitleaks, ruff, oxlint/prettier, `uv lock --check`, actionlint, zizmor (8).
8. **CI**: one workflow, SHA-pinned actions, `permissions: contents: read`, jobs for lint, types, tests with Postgres, migrations check, OpenAPI drift, web build, extension build, one `required` gate job (7).
9. **GitHub settings**: ruleset on main (PR, required `required` check, linear history, squash-only, no force push), Dependabot for uv, npm(pnpm), github-actions, docker with grouping (6.3, 6.5); turn on the "require SHA-pinned actions" policy.
10. **Claude Code setup**: short CLAUDE.md (or AGENTS.md + `@AGENTS.md`), `.claude/settings.json` with deny rules for `.env*`, format hooks, sandbox; 2-3 skills (new-endpoint, new-migration, run-evals); a security-reviewer subagent (16).
11. **Decisions written down**: 8-10 ADRs (MADR 4.0.0) + C4 context and container diagrams (9.1, 9.2).
12. **Security basics**: SSRF guard module with tests before any crawler code; LLM input/output rules (untrusted page text, Pydantic-validated outputs, cost caps) (11.6, 11.7).
13. **LLM base**: provider interface + model settings + `llm_calls` table + pytest-recording fixtures + an `evals/` folder with the first 20 cases and code-based graders (15).

### SHOULD (first 2-4 weeks, alongside early features)

1. SSH commit signing for both engineers, then the "require signed commits" rule (6.3).
2. PR template, CODEOWNERS, issue forms, labels, milestones, GitHub Project board, written DoR/DoD (6.4, 10.2, 17).
3. Semgrep CE job; `pip-audit`/`osv-scanner` weekly job; uv `exclude-newer` cooldown (6.7, 11.4).
4. Coverage floor in CI and rising (7.5); hypothesis tests for scoring functions (1.6).
5. Playwright E2E for 2-3 journeys, plus one extension E2E (2.8, 3.2).
6. OpenTelemetry SDK + local trace viewer in Compose; spans on pipeline steps and LLM calls (12.3).
7. Model-based graders and nightly eval run with stored scores (15.3).
8. CONTRIBUTING.md and SECURITY.md (9.5); ASVS L1 checklist issue (11.1); design-doc template (9.3).
9. Settings-based feature flags (10.5); track PR lead time and PR size (10.4).

### LATER (when deployment, clients or a product launch make them pay off)

1. Sentry or another error tracker; log store and alerts (DevOps) (12.5).
2. GitHub Secret Protection / Code Security (CodeQL) if budget allows; OpenSSF Scorecard (6.6-6.8).
3. SBOM generation (CycloneDX) and license checks in CI (11.3, 18).
4. Release automation (release-please), SemVer tags for the extension, changelog (6.9).
5. Full DORA five metrics once there are deployments (10.4).
6. Dev container, merge queue, CODE_OF_CONDUCT, OpenFeature, Langfuse/Logfire, React Compiler, TypeScript 7 as the main compiler (after 7.1 ships its API and typescript-eslint supports it), Python 3.15 (after DBOS/FastAPI/Pydantic list support).

---

## Open items marked unverified

- pnpm 12: whether every pnpm 11 security default (minimumReleaseAge 1 day, exotic sub-deps block) stays the default in 12.x.
- oxlint type-aware rules "stable on 2026-07-22" (secondary source only).
- GitHub Secret Protection / Code Security current prices (from 2025 changelog + secondary pricing pages).
- Sentry free plan limits (secondary pricing pages).
- FastAPI official "OpenTelemetry" docs page (seen in search only).
- DeepSeek data retention / training terms for API inputs (must read before sending client pages).
- prek adoption list (CPython, FastAPI, Django ...) from secondary posts.
- OpenTelemetry GenAI semantic conventions status (development; attribute names may change).
- A DORA 2026 report: not found as of 2026-10-06; latest verified is the 2025 report.
