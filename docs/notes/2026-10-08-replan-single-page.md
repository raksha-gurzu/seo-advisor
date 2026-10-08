# Replan: single page first (8 Oct 2026)

## Why

The owner asked why the tool checks the whole website when the SEO work is on one content page. The plan started from the whole site: an inventory of all pages, a full crawl and scheduled audits. The owner decided to start with one page and to scale up later.

## Owner decisions

1. **Scope:** the tool fetches one page and does SEO on that page. The whole site is Phase 3.
2. **Output:** an audit first (rules, evidence, no AI), then AI fix suggestions that a person reviews.
3. **Page input:** paste a URL of a registered site (MyPipit now). The sitemap list stays only as a page picker.
4. **Keyword:** the person types the target keyword.
5. **First page type:** the MyPipit blog post (30 pages).
6. **AI provider:** DeepSeek. The owner gives the key later. Check its data terms at slice 4.
7. **Order:** in each slice, the backend comes first and its screen comes after. The coding rules in `CLAUDE.md` do not change.
8. **Docs packages:** `playwright` 1.63.0 (Apache-2.0, uv group `docs`) and `@hpcc-js/wasm-graphviz` 1.29.2 (Apache-2.0, root `package.json`). They are only for `mise run docs:pdf`. Note: the question said BSD-3 for the npm package, but its licence is Apache-2.0.

## The page loop

1. Give the page: URL and keyword.
2. Fetch the page.
3. Extract its SEO content.
4. Audit it with evidence.
5. Suggest fixes (DeepSeek).
6. A person reviews the suggestions and copies them into the editor.
7. Check the page again.

## What changed

| File | Change |
|---|---|
| `PLAN.md` | Principle line, current step, "Scope" and "AI provider" decisions, open questions (DeepSeek key and terms), Phase 0 start table, Phase 1 rewritten (slices 2 to 5), new Phases 2 to 6, and a change-log row. |
| `CLAUDE.md` | Project paragraph, and the comments for `inventory`, `audits` and `drafts`. All rules are unchanged. |
| `README.md` | What the tool does, and the status. |
| `requirements/diagrams/build_requirements_pdf.py` | Text and diagrams for the single-page plan. The PDF is rebuilt with `mise run docs:pdf`. |
| `mise.toml` | `docs:pdf` runs with `uv run --group docs`. `audit` now checks all uv groups. |
| `pdfs/2026-10-08-seo-advisor-progress-v2.pdf` | New progress book, 23 pages. Version 1 stays. |

The research files R1 to R4 and the older notes did not change: they are evidence and history.

## Reuse plan (SEOAdvisor, `~/projects/Gurzu/SEOAdvisor/src/seo_engine/`)

- `tools/site_checks.py`: `read_tags`, `says_noindex`, and the `Check` pattern with "unknown" (slice 2, slice 3).
- `tools/snippet_check.py`: title pixel width (slice 3). Its limits are rules of thumb, not Google rules.
- `providers/llm.py`: `DeepSeekLLM`, which validates the output, retries once and computes the cost (slice 4). It logs the cost, but not the token counts.
- Not in SEOAdvisor, so this code is new: images and `alt`, links, Open Graph, `lang`, H1 to H6 with levels, and JSON-LD properties.
- SEOAdvisor uses `trafilatura` for the main text. That is a new package, so ask the owner at slice 2.

## Checks

- `mise run audit`: no known vulnerabilities, including the new docs packages.
- The progress PDF has 23 pages, no em or en dashes, and 6 figures.

## Next

Slice 2, backend: a spike that fetches 1 MyPipit blog post and saves it as a fixture. Then `inventory.fetch_page`, the tables `pages` and `page_snapshots`, and the extractor. Then the "Analyse a page" screen.
