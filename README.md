# seo-advisor

A multi-site SEO platform. It keeps a page inventory for each site and audits the pages on a schedule. It ranks the work that has the most effect. It writes drafts that people review, and it measures the results in Search Console.

The tool is read-only on client sites. It never publishes. A person approves and saves each change.

## Status

Phase 0: repository setup. There is no application code yet.

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
6. Run `mise run dev` to start the API and the web app (from step 0.6).

## Commands

| Command | What it does | Works from |
|---|---|---|
| `mise run setup` | Installs the tools and the Python packages, and makes `.env`. Later steps add the database and the web app. | Now |
| `mise run dev` | Starts the API and the web app. | Step 0.6 |
| `mise run check` | Runs lint, type checks and tests. Shows only failures. | Step 0.3 |
| `mise run test -- apps/api/tests/<feature>` | Runs the tests for one feature. | Step 0.3 |
| `mise run audit` | Checks dependencies for known vulnerabilities. | Step 0.3 |
| `mise run db:up` / `db:down` | Starts or stops PostgreSQL. The data stays in a volume. | Step 0.4 |
| `mise run db:migrate` | Applies database migrations. | Step 0.4 |
| `mise run db:seed` | Adds 2 fake sites. | Step 0.4 |
| `mise run gen-client` | Exports the OpenAPI file and makes the TypeScript client again. | Step 0.5 |
| `mise run evals` | Runs the LLM evals on recorded data. | Step 0.11 |
| `mise run docs:pdf` | Builds the requirements PDF again. | When its build tools are added |

## Repository layout

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
