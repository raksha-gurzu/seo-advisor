# seo-advisor

A multi-site SEO platform. It starts with **one page**: you give a page URL and a target keyword. The tool fetches that page, reads its SEO content and audits it. Each finding shows its evidence. Then an AI suggests fixes, and a person reviews them. Later the tool scales to the whole site: all pages, scheduled audits, Search Console data and measured results.

The tool is read-only on client sites. It never publishes. A person approves and saves each change.

## Status

Phase 1, single page first (see `PLAN.md`).

- Works now: the safe fetcher, sites in the database, the MyPipit sitemap list, the API and the web app (`make dev`).
- Next: fetch one MyPipit blog post and extract its SEO content (slice 2), then the audit (slice 3) and AI suggestions (slice 4).

> **Note:** Each command starts to work at the step in the "Works from" column. Before that step, the command stops with an error. See `PLAN.md` for the current step.

## Setup (5 minutes)

You need these tools:
- [mise](https://mise.jdx.dev/) (it installs Python, Node, uv and pnpm for you)
- Docker
- git

Do these steps:
1. Clone the repository.
2. Go into the repository folder.
3. Run `mise trust` to let mise read `mise.toml`.
4. Run `mise run setup` to install the tools and the Python packages, and to make your `.env` file.
5. Run `mise run check` to make sure that everything works (from step 0.3).
6. Run `make dev` (or `mise run dev`) to start the database, the API and the web app. Then open http://127.0.0.1:5173.

## Commands

| Command | What it does | Works from |
|---|---|---|
| `mise run setup` | Installs the tools, the Python and web packages, makes `.env`, starts the database and saves the sites. | Now |
| `make dev` / `mise run dev` | Starts the database, the API (port 8000) and the web app (port 5173). `make` lists all short names. | Now |
| `mise run check` | Runs lint, type checks and tests. Shows only failures. | Step 0.3 |
| `mise run test -- apps/api/tests/<feature>` | Runs the tests for one feature. | Step 0.3 |
| `mise run audit` | Checks dependencies for known vulnerabilities. | Step 0.3 |
| `mise run inventory:discover -- infra/sites/mypipit.toml` | Reads the site's robots.txt and sitemaps (read-only) and prints its pages by type. Add `--list` for every page. | Now |
| `mise run db:up` / `db:down` | Starts or stops PostgreSQL. The data stays in a volume. | Step 0.4 |
| `mise run db:migrate` | Applies database migrations. | Step 0.4 |
| `mise run db:seed` | Saves the sites in `infra/sites/*.toml`. An unchanged file changes no rows. | Now |
| `mise run gen-client` | Exports the OpenAPI file and makes the TypeScript client again. Run it after an API change. | Now |
| `mise run evals` | Runs the LLM evals on recorded data. | Step 0.11 |
| `mise run docs:pdf` | Builds the requirements PDF again. | When its build tools are added |

## Repository layout

This is the target layout. A folder is made when its first file is written.

| Folder | Contents |
|---|---|
| `apps/api` | Python API (FastAPI). Code is grouped by feature. |
| `apps/web` | Web app (React, TypeScript, Vite). |
| `apps/extension` | Browser extension (WXT). A thin client with no logic and no keys. |
| `packages/api-client` | TypeScript client, made from the API's OpenAPI file. |
| `docs` | Decisions (ADRs), architecture, design documents and session notes. |
| `evals` | LLM eval cases and graders. |
| `experiments` | Short spikes. Production code never imports them. |
| `infra` | Docker Compose and seed scripts. |
| `requirements` | Requirements PDF, research files and diagrams. |

## Documents

- `PLAN.md`: what to build and in which order.
- `CLAUDE.md`: how to work in this repository. Read the rules before your first change.
- `CONTRIBUTING.md`: branches, commits and pull requests.
- `SECURITY.md`: how to report a problem, and which data the system touches.
- `requirements/seo-advisor-requirements.pdf`: the full requirements, with reasons and diagrams.
- `docs/notes/`: a short note after each task. Read the latest note first.

## Licence

Proprietary. See `NOTICE`.
