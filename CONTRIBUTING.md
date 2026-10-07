# Contributing

Read `CLAUDE.md` → Rules before your first change. The rules in `CLAUDE.md` apply to people and to Claude Code.

## Before you start

1. Read the current step in `PLAN.md`.
2. Read the latest note in `docs/notes/`.
3. Do one small part at a time: research, experiment, implement, understand, review the plan.

## Branches

1. Make a short branch from `dev`.
2. Open the pull request into `dev`.
3. The owner moves `dev` to `main`.

Only the owner merges and deletes branches.

## Commits

- One subject line in the imperative, 50 characters or less. Example: `Add sitemap parser`.
- Write a body only if the reason is not clear from the subject.
- Do not add "Generated with" or "Co-Authored-By" lines for AI tools.

## Pull requests

- Title in Conventional Commits form, for example `feat(audits): add title length rule`.
- Keep a pull request small: 400 changed lines or less.
- `mise run check` must pass.
- Each change has tests. Write the failing test first.
- If a decision changed, update `PLAN.md`, the PDF (`mise run docs:pdf`) and the ADR.
- Write a short note in `docs/notes/`.
- If AI helped, say so in the description, and say who reviewed it. A person reads every line before the merge.

## Packages and services

1. Ask the owner before you add a package, tool or outside service.
2. Check its maintenance, licence and known advisories (`mise run audit`).
3. Add packages only through the lock file (`uv add`, `pnpm add`).

## Writing

Write all documents in ASD-STE100 (see `CLAUDE.md` → Writing).
