# Research: platform choices for the multi-site "SEO checker"

Date of research: 5 October 2026. Web pages read with GET requests only. No repo files changed. No website changed.

Trust labels:
- **primary**: the organisation that owns the thing (postgresql.org, sqlite.org, Google, Microsoft, IETF, the project's own repo or docs, PyPI metadata).
- **vendor**: a company writing about its own paid product.
- **secondary**: a blog, a third party, or a well-known book or article that is not a standard.
- **unverified**: I could not confirm it from a primary source.

This file does not repeat the facts in `docs/rethink/02-research-data-sources.md`, `docs/rethink/04-research-pathways-and-design.md` or `docs/mypipit/research-evidence.md`. Where a fact here changes something in those files, it says so.

---

## 0. Live check of the two client sites (5 Oct 2026, GET only)

These are my own observations, not a source. They help answer "do we need a headless browser?".

| Check | extendmy.life | marketplace.mypipit.com |
|---|---|---|
| Home page status, size | 200, 369 KB | 200, 83 KB |
| Content in raw HTML (no JavaScript run) | Yes. Home page: about 276 visible words. German article `/de/article/healthspan-vs-lifespan`: about 2,174 words, full `<h1>`, `<html lang="de">` | Yes. Home page: about 948 visible words |
| Framework signs | Next.js App Router (`self.__next_f` stream; no `__NEXT_DATA__`) | Rails (server HTML) |
| Canonical and hreflang | Article page: canonical present; `hrefLang` alternates for `en`, `de`, `x-default`. **Home page: no canonical and no hreflang tags found** | None on home page |
| x-default target | `/article/<slug>` returns **307** to `/en/article/<slug>` | n/a |
| Structured data (`application/ld+json`) | 2 blocks on home page | 0 on home page |
| robots.txt | Disallows tracking and filter query strings; also has a non-standard `Host:` line; `Sitemap: /sitemap.xml` | (read in earlier research) |
| Sitemap | Sitemap index with 12 child sitemaps (articles, categories, products, regroupings, static, subcategories × de/en). In `sitemap-articles-de.xml` every `<lastmod>` was the same time (`2026-10-05T01:44:54.552Z`) and `changefreq` is `daily` | (read in earlier research) |

**What this means:** both sites send their main content in the first HTML response. A plain HTTP fetch (httpx) is enough for the normal audit. Keep a headless browser only as an occasional "rendered vs raw" check for Next.js pages. The identical `lastmod` values matter: Google says it uses `lastmod` only "if it's consistently and verifiably ... accurate" (see 3.6), so the audit should flag this.

---

## 1. Database choice

### 1.1 PostgreSQL current version
- **Finding:** The current stable major version is **PostgreSQL 18** (released 25 Sep 2025). Latest minor releases on 13 Aug 2026: 18.6, 17.11, 16.15, 15.19, 14.24. **PostgreSQL 19 is in beta** (Beta 4 on 24 Sep 2026); the project says GA "may also occur in October" 2026. PostgreSQL 14 stops getting fixes on 12 Nov 2026.
- **Sources:** postgresql.org home page (read 5 Oct 2026) https://www.postgresql.org/ ; "PostgreSQL 18 Released!" (25 Sep 2025) https://www.postgresql.org/about/news/postgresql-18-released-3142/ ; "PostgreSQL 19 Beta 4 Released!" (24 Sep 2026) https://www.postgresql.org/about/news/postgresql-19-beta-4-released-3386/
- **Quote:** "Based on testing and evaluation, this means that the PostgreSQL 19 GA may also occur in October."
- **PG 18 features that matter here:** `uuidv7()` (time-ordered IDs, good for history rows); virtual generated columns; temporal constraints (`WITHOUT OVERLAPS`, `PERIOD`); asynchronous I/O; skip scan on multi-column B-tree indexes; OAuth 2.0 login; page checksums on by default.
- **PG 19 Beta 4 reverted:** `FOR PORTION OF` temporal UPDATE/DELETE, SQL/PGQ graph queries, `MERGE/SPLIT PARTITIONS`, online data-checksum switching. So **do not plan on these features in PG 19**.
- **Trust:** primary.
- **Advice:** start on PostgreSQL 18. Upgrade to 19 later; nothing in 19 is needed.

### 1.2 JSONB
- **Finding:** `jsonb` stores JSON in a binary form. Input is a little slower, processing is much faster, and it supports indexes. Docs: use `jsonb` for most applications. Two GIN index classes: `jsonb_ops` (default; supports key-exists operators `?`, `?|`, `?&` and `@>`) and `jsonb_path_ops` (smaller and faster for `@>`, but no key-exists operators). You can also index one path, for example `GIN ((jdoc -> 'tags'))`.
- **Source:** PostgreSQL 18 docs, "8.14 JSON Types" https://www.postgresql.org/docs/current/datatype-json.html (read 5 Oct 2026)
- **Trust:** primary.
- **Use here:** store raw audit results, Search Console row extras and LLM outputs as `jsonb`. Keep fields you filter or join on (site_id, url, status, dates) as normal columns.

### 1.3 Full-text search in English and German
- **Finding:** Each text search configuration is a parser plus dictionaries. PostgreSQL ships Snowball stemmers for 31 languages. The list includes **english, german and nepali**.
- **Sources:** PostgreSQL 18 docs, "12.7 Configuration Example" https://www.postgresql.org/docs/current/textsearch-configuration.html ; "12.6 Dictionaries" https://www.postgresql.org/docs/current/textsearch-dictionaries.html ; PostgreSQL source, `src/backend/snowball/snowball_create.pl` (master) https://github.com/postgres/postgres/blob/master/src/backend/snowball/snowball_create.pl
- **Quote (source list):** "arabic, armenian, basque, catalan, danish, dutch, english, ... french, german, greek, hindi, ... nepali, ..."
- **Caveat:** The docs mention compound-word splitting (important for German, for example "Langlebigkeitsklinik") only for **Ispell** dictionaries. The Snowball `german` stemmer does not split compounds. Splitting needs an Ispell/Hunspell German dictionary installed by you.
- **Trust:** primary (docs plus source code).
- **Use here:** add a `language` column per content item. Build `tsvector` with `to_tsvector(language::regconfig, text)`. This makes keyword-presence checks and site search work in both languages.

### 1.4 Partitioning for time series (Search Console rows, ranks, audits)
- **Finding:** Built-in declarative partitioning supports range, list and hash. Benefits: queries that touch few partitions are faster; dropping a partition is much faster than a bulk DELETE and needs no VACUUM. Docs rule of thumb: partitioning is worthwhile "only when a table would otherwise be very large ... the size of the table should exceed the physical memory of the database server." The planner copes with "a few thousand partitions" when pruning removes most of them. "Never just assume that more partitions are better than fewer partitions, nor vice-versa."
- **Source:** PostgreSQL 18 docs, "5.12 Table Partitioning" https://www.postgresql.org/docs/current/ddl-partitioning.html
- **Trust:** primary.
- **Sizing for this platform (my estimate, not a source):** 2 sites. extendmy.life has about 474 URLs. If Search Console gives about 50k page-and-query rows per day per site, a year is about 36M rows, roughly 3 to 6 GB. That is close to the "exceeds memory" line only after a year or more. **Advice:** make one table per fact type with a `date` column and a (site_id, date) index from day one. Add monthly range partitions only when the table becomes larger than server memory. A BRIN index on `date` is a cheap alternative.

### 1.5 Row-level security (RLS)
- **Finding:** RLS policies limit, for each user, which rows queries can see or change. When RLS is on and no policy exists, the result is **default deny**. Superusers and `BYPASSRLS` roles always bypass RLS. **Table owners also bypass it** unless you run `ALTER TABLE ... FORCE ROW LEVEL SECURITY`.
- **Source:** PostgreSQL 18 docs, "5.9 Row Security Policies" https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- **Quote:** "If no policy exists for the table, a default-deny policy is used, meaning that no rows are visible or can be modified." / "Table owners normally bypass row security as well, though a table owner can choose to be subject to row security with ALTER TABLE ... FORCE ROW LEVEL SECURITY."
- **Trust:** primary.
- **Trap:** if the app connects as the user that owns the tables (common with Alembic), RLS does nothing unless you add FORCE or use a separate, non-owner app role.

### 1.6 pgvector
- **Finding:** Current version **0.8.7** (latest git tag). Supports Postgres 13 and later. Licence: **PostgreSQL License** (permissive). Index types:
  - **HNSW:** better query speed-to-recall, slower build, more memory; no training step, so you can create it on an empty table.
  - **IVFFlat:** faster build, less memory, worse query speed-to-recall; needs data in the table before you build it.
  - Index limits: `vector` up to 2,000 dimensions, `halfvec` up to 4,000, `bit` up to 64,000, `sparsevec` up to 1,000 non-zero elements. Storage without an index goes up to 16,000 dimensions.
  - **Iterative index scans** (since 0.8.0) fix the "filtered search returns too few rows" problem. This matters when you filter by `site_id` or language.
- **Sources:** pgvector README and tags https://github.com/pgvector/pgvector (read 5 Oct 2026; tag v0.8.7); LICENSE https://github.com/pgvector/pgvector/blob/master/LICENSE ; Python client `pgvector` 0.5.0 (MIT, 6 Jul 2026) https://pypi.org/project/pgvector/
- **Trust:** primary.
- **Note for Gemini embeddings:** `gemini-embedding-001` outputs 3,072 dimensions by default. That is above the 2,000 limit for indexed `vector`. Either request 768 or 1,536 output dimensions, or store as `halfvec` (4,000 limit). (The model's default size comes from Google's docs and is **unverified in this session**.)

### 1.7 SQLite
- **Finding (Appropriate Uses):** "SQLite does not compete with client/server databases. SQLite competes with fopen()." Websites: "Any site that gets fewer than 100K hits/day should work fine with SQLite." Choose client/server when (1) the data is on a different machine over a network, (2) there are many concurrent writers, or (3) the data is very large (terabytes). "Otherwise → choose SQLite!" SQLite "allows only one writer at a time per database file".
- **Finding (WAL):** In WAL mode, readers do not block writers and writers do not block readers, but there is still **only one writer at a time**. WAL "does not work over a network filesystem", because all processes must be on the same host. WAL is poor for transactions above about 100 MB.
- **Current version:** SQLite **3.53.4** (24 Jul 2026).
- **Sources:** "Appropriate Uses For SQLite" (last updated 2025-05-31) https://www.sqlite.org/whentouse.html ; "Write-Ahead Logging" https://www.sqlite.org/wal.html ; home page https://www.sqlite.org/index.html
- **Trust:** primary.
- **For this platform:** the platform will have a scheduler, background workers and the API all writing at the same time, plus multi-tenant isolation later. That is "many concurrent writers" and needs RLS, which SQLite lacks. **PostgreSQL is the better fit for the new platform.** This differs from `04-research-pathways-and-design.md`, which said "SQLite now". That advice was for the single-user SEOAdvisor tool. Use SQLite only for tests or a local demo mode, if at all.

### 1.8 Document database (MongoDB) as the alternative
- **Finding:** MongoDB Community Server (versions after 16 Oct 2018) is under the **Server Side Public License (SSPL) v1.0**. This is not an OSI-approved open-source licence. It adds conditions if you offer MongoDB itself as a service.
- **Source:** MongoDB, "Community Edition licensing" https://www.mongodb.com/legal/licensing/community-edition
- **Quote:** "MongoDB, Inc.'s Server Side Public License (for all versions released after October 16, 2018 ...)"
- **Trust:** vendor (about its own licence).
- **Assessment (mine):** the data here is relational: sites → pages → content items → versions → suggestions → approvals, joined to Search Console rows. Postgres `jsonb` already covers the flexible parts (audit results, LLM outputs). A document DB adds a second store and gives up RLS, temporal constraints and pgvector-next-to-data. **Not recommended.**

### 1.9 TimescaleDB vs plain Postgres partitioning
- **Finding:** TimescaleDB has two editions. The **Apache 2 Edition** has only basic hypertables, chunking and core hyperfunctions such as `time_bucket`. **Compression/columnstore (Hypercore), continuous aggregates, retention policies and automated jobs are Community Edition only, under the Tiger Data License (TSL).** The TSL allows free use on your own servers but: "You cannot sell TimescaleDB Community Edition as a service." Latest release: 2.30.2 (29 Sep 2026). The docs moved from docs.timescale.com to tigerdata.com (the company renamed itself Tiger Data).
- **Sources:** Tiger Data docs, "TimescaleDB editions" (no date shown) https://www.tigerdata.com/docs/about/latest/timescaledb-editions ; GitHub releases https://github.com/timescale/timescaledb/releases
- **Trust:** vendor (about its own product and licence).
- **Assessment:** an SEO platform that stores its own clients' data is a normal application, not "TimescaleDB as a service". So TSL use is very likely allowed, but have a lawyer confirm before sale as a product (**unverified legal reading**). At this data size (1.4), plain Postgres with a date index (and partitions later) is enough. Many managed Postgres hosts do not offer the TSL edition. **Advice: plain Postgres; revisit Timescale only if aggregate queries become slow.**

---

## 2. Content versioning and audit trail

### 2.1 Fowler's temporal patterns
- **Finding:** Fowler lists five patterns: **Audit Log**, **Effectivity** (valid-from/to), **Temporal Property**, **Temporal Object** (explicit versions), **Snapshot**. Audit Log is the simplest: "The simplest way to solve this problem is to use an Audit Log. Here you are concerned with keeping a record of changes, but you don't expect to go back and use it very often." He also separates **actual time** (when a thing happened) from **record time** (when we learned it). This is bitemporal data.
- **Source:** Martin Fowler, "Temporal Patterns" (16 Feb 2005) https://martinfowler.com/eaaDev/timeNarrative.html
- **Trust:** secondary (well-known reference, not a standard).

### 2.2 Event Sourcing
- **Finding:** "Capture all changes to an application state as a sequence of events." It allows a complete rebuild, temporal queries and event replay. Fowler warns that it adds a lot of complexity, especially with external systems (replay can send duplicate external calls, and old external data may be gone). It should not be a default choice.
- **Source:** Martin Fowler, "Event Sourcing" (12 Dec 2005) https://martinfowler.com/eaaDev/EventSourcing.html
- **Trust:** secondary.
- **Assessment:** this platform calls many external systems (crawls, Search Console, LLMs), so full event sourcing is a poor fit.

### 2.3 PostgreSQL building blocks
- **Audit trigger (docs Example 41.4):** "any insert, update or delete of a row in the `emp` table is recorded (i.e., audited) in the `emp_audit` table. The current time and user name are stamped into the row, together with the type of operation". **Example 41.7** does the same with statement-level triggers and **transition tables**. The docs say this is "significantly faster" when one statement changes many rows. Source: PostgreSQL 18 docs, "41.10 Trigger Functions" https://www.postgresql.org/docs/current/plpgsql-trigger.html — primary.
- **Temporal keys (PG 18):** `PRIMARY KEY (id, valid_at WITHOUT OVERLAPS)` stops two versions of one item from covering overlapping time. `FOREIGN KEY (..., PERIOD valid_at)` checks that a referenced row covers the period. The column must be a range type. For scalar columns, add the `btree_gist` extension ("the expected way to use this feature"). Source: PostgreSQL 18 docs, "CREATE TABLE" https://www.postgresql.org/docs/current/sql-createtable.html — primary.
- **No SQL:2011 system-versioned tables:** PostgreSQL has no `SYSTEM VERSIONING` / `FOR SYSTEM_TIME AS OF`, and the temporal `FOR PORTION OF` UPDATE was pulled from PG 19 (1.1). — I did not find system versioning in the PG 18 docs; absence **unverified** beyond that.

### 2.4 Recommended pattern for this platform (my synthesis)
- `content_items` (one row per page or listing per site; current pointer) plus an **append-only `content_versions`** table. Each version row is immutable and holds: `version_no`, `source` (crawled / ai_draft / human_edit), `body_jsonb`, `created_by`, `created_at`, `parent_version_id`.
- **Workflow state** goes in its own append-only `content_state_events` table (draft → in_review → approved → published / rejected). The current state is the latest event (or a cached column). This is Fowler's Audit Log, with explicit version rows (Temporal Object). It is not full event sourcing.
- Add a generic trigger-based `audit_log` (Example 41.4 style, `jsonb` of old and new) for settings and permissions tables.
- Use `uuidv7()` IDs (PG 18) so that history rows sort by time.

---

## 3. Crawling and rendering

### 3.1 Google JavaScript SEO
- **Finding:** Google works in three phases: crawl, render, index. Pages wait in a render queue: "The page may stay on this queue for a few seconds, but it can take longer than that." Googlebot uses "an evergreen version of Chromium". "Server-side or pre-rendering is still a great idea because it makes your website faster for users and crawlers, and not all bots can run JavaScript." Use the History API, not URL fragments. If Google sees `noindex` in the first HTML, it may skip rendering, so JavaScript cannot reliably remove `noindex`. Put the canonical in the first HTML when possible.
- **Source:** Google Search Central, "Understand the JavaScript SEO basics" (last updated 2026-03-04) https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
- **Trust:** primary.

### 3.2 Dynamic rendering is deprecated
- **Quote:** "Dynamic rendering was a workaround and not a long-term solution for problems with JavaScript-generated content in search engines." Use server-side rendering, static rendering or hydration instead.
- **Source:** Google Search Central, "Dynamic rendering as a workaround" (last updated 2025-12-10) https://developers.google.com/search/docs/crawling-indexing/javascript/dynamic-rendering
- **Trust:** primary.

### 3.3 Next.js default rendering
- **Finding:** "Next.js uses Server Components by default", and "Next.js prerenders Server and Client Components on the server at build time". Request-time APIs (`cookies`, `searchParams`) switch a route to dynamic rendering, but it is still rendered on the server. Next.js docs version 16.3.8.
- **Source:** Next.js docs, "Production checklist" (lastUpdated 2026-03-10) https://nextjs.org/docs/app/guides/production-checklist
- **Trust:** primary (framework owner).
- **Matches section 0:** extendmy.life sends full article text in its HTML.

### 3.4 Google crawlers and limits
- **Finding:** Common crawlers: Googlebot (smartphone and desktop), Googlebot-Image, -Video, -News, Google StoreBot, Google-InspectionTool, GoogleOther, Google-CloudVertexBot, and **Google-Extended** (a robots.txt token that controls use for Gemini training; it is not a separate fetcher). User-agent strings can be faked, so check real Googlebot traffic by reverse DNS plus Google's published IP-range JSON files. Google crawlers read the first 15 MB of a file; **Googlebot reads only the first 2 MB of HTML**. Both HTTP/1.1 and HTTP/2 are used, with no ranking difference.
- **Sources:** "Google's common crawlers" https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers ; "Overview of Google crawlers and fetchers" (last updated 2026-06-12) https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers
- **Trust:** primary.
- **Audit rule:** flag HTML larger than 2 MB. The extendmy.life article was 467 KB, which is fine.

### 3.5 RFC 9309 (robots.txt) and polite crawling
- **RFC 9309** (Proposed Standard, Sep 2022): parse at least **500 KiB**; follow at least **5 redirects**; **4xx** → the crawler "MAY access any resources"; **5xx/unreachable** → "MUST assume complete disallow"; the longest (most specific) match wins, and on a tie "the allow rule SHOULD be used"; do not use a cached copy for more than 24 hours. **`Crawl-delay` is not in the standard**, and neither is `Host:` (extendmy.life uses `Host:`; it is harmless). Source: https://www.rfc-editor.org/rfc/rfc9309.html — primary.
- **Google's signals for "slow down":** a site under load can return **500, 503 or 429**. If Googlebot sees these "on the same URL for multiple days, the URL may be dropped from Google's index". Source: Google, "Reduce the Googlebot crawl rate" (last updated 2025-12-18) https://developers.google.com/search/docs/crawling-indexing/reduce-crawl-rate — primary. **For our crawler:** treat 429/503 as "back off" (honour `Retry-After`) and record repeated 5xx as an audit error, because Google can de-index those pages.
- **Polite defaults (Scrapy AutoThrottle, as a reference):** the goal is to "be nicer to sites instead of using default download delay of zero". Delay follows server latency. The default target is **1 concurrent request per site** (`AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0`). Source: Scrapy docs https://docs.scrapy.org/en/latest/topics/autothrottle.html — primary for Scrapy. Scrapy's default robots parser **Protego** is described as compliant with Google's robots.txt spec (Google's spec is the basis of RFC 9309). https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
- **Suggested settings (mine):** 1 request at a time per host; about 1 second minimum delay; identify with a clear User-Agent and contact URL; obey robots.txt even on client sites; crawl from the sitemaps first (474 + 53 URLs are small).

### 3.6 Sitemaps: lastmod
- **Quote:** "Google uses the `<lastmod>` value if it's consistently and verifiably (for example by comparing to the last modification of the page) accurate." "Google ignores `<priority>` and `<changefreq>` values." A sitemap is "merely a hint".
- **Source:** Google, "Build and submit a sitemap" https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap — primary.
- **Relevance:** extendmy.life sets the same `lastmod` (sitemap build time) on every URL. Add an audit rule for this.

### 3.7 Tools (versions from PyPI, 5 Oct 2026)

| Tool | Version (date) | Licence | Role here |
|---|---|---|---|
| Playwright (Python) | 1.63.0 (15 Sep 2026) | Apache-2.0 | Headless Chromium for "rendered vs raw" checks and Core Web Vitals lab checks; use rarely |
| Scrapy | 2.19.0 (10 Sep 2026) | BSD-3-Clause | Full crawler framework (Twisted-based); AutoThrottle, robots, retries built in |
| Crawlee (Python) | 1.10.3 (29 Sep 2026) | Apache-2.0 | asyncio crawler from Apify; httpx/BeautifulSoup and Playwright crawlers behind one API; request queue |

- **Trust:** primary (PyPI metadata).
- **Advice (mine):** for 2 sites and about 530 URLs, the existing httpx + trafilatura + robots code with a small per-host rate limiter is enough. Scrapy's Twisted reactor fits awkwardly inside a FastAPI/asyncio worker. If a framework is wanted later, Crawlee for Python is the closer fit (asyncio, built-in Playwright switch). Keep Playwright as an optional extra.

---

## 4. Page experience data

### 4.1 Core Web Vitals thresholds (75th percentile, mobile and desktop separately)

| Metric | Good | Needs improvement | Poor |
|---|---|---|---|
| LCP | ≤ 2.5 s | 2.5–4.0 s | > 4.0 s |
| INP | ≤ 200 ms | 200–500 ms | > 500 ms |
| CLS | ≤ 0.1 | 0.1–0.25 | > 0.25 |

- All three metrics are **Stable**. Measure at the "75th percentile of page loads, segmented across mobile and desktop devices".
- **Sources:** web.dev "Web Vitals" (updated 2024-10-31) https://web.dev/articles/vitals ; "LCP" (2025-09-04) https://web.dev/articles/lcp ; "INP" (2025-09-02) https://web.dev/articles/inp ; "CLS" (2023-04-12) https://web.dev/articles/cls
- **Trust:** primary (Google Chrome team).

### 4.2 CrUX API and CrUX History API
- **Finding:** Needs a Google Cloud API key with "Chrome UX Report API" turned on. It is **free, 150 queries per minute per Cloud project**, with no paid tier. Metrics: LCP, INP, CLS, FCP, TTFB, round-trip time, navigation types, form factors (PHONE / TABLET / DESKTOP). You can query by **origin or by URL**. Data is a 28-day rolling window, updated daily at about 04:00 UTC with about a 2-day lag. If there is not enough traffic, the API returns **404**. The **History API** gives **40 weekly periods** (about 10 months) and updates on Mondays. It shares the same key and quota.
- **Sources:** "CrUX API" https://developer.chrome.com/docs/crux/api ; "CrUX History API" (updated 2025-04-11) https://developer.chrome.com/docs/crux/history-api
- **Trust:** primary.
- **Expectation:** small sites like these will probably get 404 for most single URLs. Origin-level data may exist for extendmy.life (**unverified**).

### 4.3 PageSpeed Insights (PSI) API
- **Finding:** Returns Lighthouse **lab** data (mobile or desktop strategy). A key is optional but recommended for automated use. **New:** Google says "We plan to discontinue including real-world data from the Chrome User Experience Report in this API", and points users to the CrUX API. No date was given.
- **Source:** "Get Started with the PageSpeed Insights API" (last updated 2025-08-28) https://developers.google.com/speed/docs/insights/v5/get-started
- **Quota:** commonly reported as 25,000 queries per day, with a per-100-second limit (reports say 100 or 400). **Secondary, unverified** (e.g., https://groups.google.com/g/pagespeed-insights-discuss/c/dB7hWmGAGsw ). Check the real figure in the Cloud console when the key is created.
- **Advice:** field data comes from the CrUX API (plus History). Lab data comes from PSI (or local Lighthouse/Playwright) on a weekly or monthly schedule, a few key templates per site, not every URL every day.

---

## 5. Search Console, Bing Webmaster, IndexNow

### 5.1 Search Console API with many sites
- **Scopes:** `https://www.googleapis.com/auth/webmasters.readonly` (read) and `.../auth/webmasters` (read/write, needed to submit sitemaps). Source: "Authorize requests" https://developers.google.com/webmaster-tools/v1/how-tos/authorizing — primary.
- **Properties:** `siteUrl` is either a URL-prefix property `"http://www.example.com/"` (with the trailing slash) or a domain property `"sc-domain:example.com"`. `sites.list` returns each property with `permissionLevel` ∈ `siteOwner`, `siteFullUser`, `siteRestrictedUser`, `siteUnverifiedUser`. Source: "Sites" resource (updated 2024-07-23) https://developers.google.com/webmaster-tools/v1/sites — primary.
- **Users per property:** at most **100 non-owner users** per property; restricted users can read Performance data. Source: Search Console Help, "Manage owners, users, and permissions" https://support.google.com/webmasters/answer/7687615 — primary.
- **Service accounts:** the Search Console API pages I read (prereqs, updated 2025-08-28) mention only OAuth and a Google Account with permission on the property. Google's **Indexing API** setup explicitly says to add the service account's `client_email` as an owner in Search Console (https://developers.google.com/search/apis/indexing-api/v3/prereqs). Adding a service account email as a **user** (not owner) on a property and calling the Search Console API with it is widely used. However, **it is not stated in the Search Console API docs: unverified as an official, documented path.**
- **Design (mine):** two auth modes per site. (a) **Service account added as Restricted/Full user**: best for client sites that Gurzu manages, with no token expiry; the client adds one email. (b) **OAuth user consent** with offline refresh token, for product users later. Store `siteUrl` exactly as `sites.list` returns it. Domain vs URL-prefix properties give different data.

### 5.2 Google Indexing API is not for these sites
- **Quote:** "The Indexing API can only be used to crawl pages with either `JobPosting` or `BroadcastEvent embedded in a VideoObject`." Misuse "may result in access being revoked".
- **Source:** Indexing API quickstart (updated 2026-07-16) https://developers.google.com/search/apis/indexing-api/v3/quickstart — primary.
- **So for Google:** the only update signals are an accurate sitemap `lastmod`, sitemap (re)submission through the API (`webmasters` scope), and internal links.

### 5.3 Bing Webmaster API
- **Finding:** Two access methods: **OAuth 2.0 (recommended)** or an API key. "The API key is generated for a user and not a site", so one key works for all verified sites of that user. Only one key per user.
- **Source:** Microsoft Learn, "Getting Access to the Bing Webmaster Tools API" (updated 2022-10-13) https://learn.microsoft.com/en-us/bingwebmaster/getting-access — primary.

### 5.4 IndexNow
- **Finding:** Participants listed in the official FAQ: **Bing, Yandex, Naver, Seznam.cz, Yep, Amazon**. **Google is not listed.** Submitting to one endpoint is "shared across all IndexNow-enabled search engines". Up to **10,000 URLs per POST**. The key is 8–128 characters (letters, digits, dashes), hosted at `/{key}.txt` or at a `keyLocation` (which limits submissions to that path). Responses: 200 OK, 202 received/pending, 400, 403 bad key, 422 URL/host mismatch, **429 too many (potential spam)**. Bing: send only URLs "added, updated, or deleted" since you started using IndexNow; IndexNow "does not guarantee that web pages will be crawled or indexed".
- **Sources:** IndexNow FAQ https://www.indexnow.org/faq ; IndexNow documentation https://www.indexnow.org/documentation ; Bing "IndexNow – Get started" https://www.bing.com/indexnow/getstarted (no dates shown).
- **Trust:** primary (protocol site and Bing).
- **Google and IndexNow:** I found no Google statement of support as of 5 Oct 2026. "Google does not support IndexNow" is based on its absence from the participant list. The absence is **unverified** beyond that.
- **Practical limit:** the platform cannot publish to the client sites (read-only rule). IndexNow needs a key file on each client domain, so the **client site's own CMS** must host the key file and send pings when an approved change goes live. The platform can only *recommend* or prepare the ping list. One option: the platform holds the key and the site serves the key file. This needs a decision with each client.

---

## 6. Background jobs and scheduling in Python

Versions from PyPI (5 Oct 2026):

| Library | Version (date) | Licence | Broker / store |
|---|---|---|---|
| DBOS | 3.2.0 (29 Sep 2026) | MIT | Postgres (prod) or SQLite (dev) |
| Procrastinate | 3.10.0 (23 Sep 2026) | MIT | Postgres only |
| pgqueuer | 1.5.0 (4 Oct 2026) | MIT | Postgres only |
| Celery | 5.6.3 (26 Mar 2026) | BSD-3-Clause | Redis/RabbitMQ + separate `beat` process |
| APScheduler | 3.11.3 (28 Jun 2026); 4.0 still alpha (4.0.0a6) | MIT | In-process scheduler |

### 6.1 DBOS
- **Scheduling:** cron syntax with 5 or 6 fields, UTC by default, `cron_timezone` optional. Each run gets an idempotency key (schedule name + time), so "each scheduled invocation occurs exactly once while your application is active". Missed runs: `DBOS.backfill_schedule()` or `automatic_backfill=True`. **Schedules can be created at runtime**, for example one per customer: `DBOS.create_schedule(schedule_name=f"customer-{customer_id}-sync", ...)`. Source: https://docs.dbos.dev/python/tutorials/scheduled-workflows — primary.
- **Retries:** `@DBOS.step(retries_allowed=True, interval_seconds=1.0, max_attempts=3, backoff_rate=2.0)`, plus a `should_retry` filter. Steps run **at least once**, so make them idempotent. Source: https://docs.dbos.dev/python/tutorials/step-tutorial — primary.
- **Database:** "for production, we recommend using Postgres". SQLite "can't be used in a distributed setting". Source: https://docs.dbos.dev/python/tutorials/database-connection — primary.
- **Changed since earlier research:** DBOS is now on the **3.x** major line, and runtime schedule creation (per site) is documented. Per-site daily/weekly/monthly schedules match this feature directly.

### 6.2 Procrastinate
- **Periodic tasks:** `@app.periodic(cron=...)`. Each worker defers due tasks, and "the database is responsible for making sure deferring only happens once per period". Several schedules for one task need a `periodic_id`. Tasks more than **10 minutes overdue** at worker start are skipped by default (configurable). Source: https://procrastinate.readthedocs.io/en/stable/howto/advanced/cron.html — primary.
- **Retries:** `retry=5` or `RetryStrategy(max_attempts, wait, linear_wait, exponential_wait, retry_exceptions)`. Source: https://procrastinate.readthedocs.io/en/stable/howto/advanced/retry.html — primary.
- **Limit:** schedules are declared in code, so per-site schedules from the database need your own "dispatcher" periodic task that reads a `schedules` table (**my reading**).

### 6.3 Celery
- **Beat:** "you have to ensure only a single scheduler is running for a schedule at a time, otherwise you'd end up with duplicate tasks." Source: https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html — primary.
- **Idempotency:** with `acks_late`, "the task may be executed multiple times should the worker crash in the middle of execution. Make sure your tasks are idempotent." `autoretry_for`, `retry_backoff`, `retry_jitter`, `retry_backoff_max` (10 min cap). Source: https://docs.celeryq.dev/en/stable/userguide/tasks.html — primary.

### 6.4 APScheduler
- 3.x: "Job stores must never be shared between schedulers." Supports misfire handling and `coalesce`. Source: https://apscheduler.readthedocs.io/en/3.x/userguide.html — primary. Version 4 has been alpha for a long time (4.0.0a6). It is risky to build on.

### 6.5 Recommendation for 1–2 engineers (mine)
- **DBOS on the same Postgres** is the best fit. It gives one library and no extra server or Redis. It has durable multi-step workflows (crawl → audit → suggest → draft), cron schedules per site created at runtime, built-in retries and idempotency keys, and queues with concurrency limits (for example, one crawl per host).
- **Fallback:** Procrastinate (plain job queue) plus a `schedules` table and one dispatcher task.
- **Avoid:** Celery (needs Redis and a single-beat rule; more moving parts) and APScheduler 4 (alpha).
- **Rules in all cases:** every job takes `(site_id, run_id)`; writes use upserts keyed by natural keys (for example `(site_id, date, page, query)` for Search Console rows); external calls are cached by day (existing rule 4).

---

## 7. Multi-tenant SaaS patterns on Postgres

- **AWS (Prescriptive Guidance, "Multi-tenant SaaS partitioning models for PostgreSQL"):** three models. **Silo** (database per tenant): compliance, no cross-tenant impact, but cost and deployment complexity. **Bridge** (schema per tenant): a hybrid. **Pool** (shared tables + `tenant_id`): agility, lowest cost, central management, but cross-tenant impact and all-or-nothing availability. On RLS: "Row-level security (RLS) is required to maintain tenant data isolation in a pooled model". The preferred way is a runtime variable such as `current_setting('app.current_tenant')`, not one DB user per tenant. "Enable RLS on all tables that contain tenant data." Sources: https://docs.aws.amazon.com/prescriptive-guidance/latest/saas-multitenant-managed-postgresql/partitioning-models.html ; https://docs.aws.amazon.com/prescriptive-guidance/latest/saas-multitenant-managed-postgresql/rls.html — primary (cloud vendor architecture guidance; label: vendor guidance, but it is about Postgres in general).
- **Microsoft (Azure Architecture Center, "Architectural approaches for storage and data in multitenant solutions", ms.date 2026-08-21):** a shared database "provides the highest density ... lowest financial cost" and lower management overhead. Drawbacks: scale limits, noisy neighbours, per-tenant requirements. **Antipatterns:** a table per tenant, columns for one tenant only, manual schema changes. On RLS: "you need to ensure that the user's identity and tenant identity are propagated ... with each query. This approach can be complex to design, implement, test, and maintain. Many multitenant solutions don't use row-level security because of those complexities." Source: https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/storage-data — primary (vendor guidance).
- **Postgres traps (from 1.5):** owners and superusers bypass RLS. Use a non-owner app role or `FORCE ROW LEVEL SECURITY`. With connection pools, set the tenant with `SET LOCAL` inside each transaction so it cannot leak to the next request (**my note**).
- **Recommendation (mine):** **shared schema with `tenant_id` (organisation) and `site_id` on every row.** Enforce it in the app layer now (one repository/session helper that always filters). Add RLS policies when outside customers arrive. Keep a silo option (separate database) for a client that demands it. Schema-per-tenant gives little here and makes every migration N times the work.

---

## 8. LLM observability and evaluation: what changed

- **OpenTelemetry GenAI semantic conventions moved** to their own repository, `open-telemetry/semantic-conventions-genai` (repo created 5 May 2026). The old page on opentelemetry.io says "This page has moved and is no longer maintained in this repository." Status is still **"Development"** (not stable). It covers events, exceptions, metrics, inference token metrics, model spans, **agent spans**, provider-specific conventions (Anthropic, Azure AI Inference, AWS Bedrock, OpenAI) and **MCP**. No tagged release yet (changelog "Unreleased"). Python `opentelemetry-semantic-conventions` is 0.66b0 (25 Sep 2026). Sources: https://opentelemetry.io/docs/specs/semconv/gen-ai/ ; https://github.com/open-telemetry/semantic-conventions-genai (docs/gen-ai/README.md, read 5 Oct 2026) — primary.
- **Arize Phoenix licence is Elastic License 2.0 (ELv2), not open source.** "You may not provide the software to third parties as a hosted or managed service, where the service provides users with access to any substantial set of the features or functionality of the software." Self-hosting it for our own traces is allowed; offering Phoenix itself to customers is not. Latest `arize-phoenix` 20.19.0 (1 Oct 2026). Source: https://github.com/Arize-ai/phoenix/blob/main/LICENSE — primary. *(`04-research-pathways-and-design.md` calls Phoenix "free self-host with no feature gates". That is true for internal use, but the file should note ELv2.)*
- **Langfuse:** MIT, except the `ee/`, `web/src/ee/` and `worker/src/ee/` folders, which are under a separate commercial licence. Python SDK `langfuse` 4.17.0 (5 Oct 2026); the SDK is on the **v4** major line. Source: https://github.com/langfuse/langfuse/blob/main/LICENSE ; PyPI — primary.
- **Advice:** unchanged from the earlier file. Instrument with OpenTelemetry/OpenInference (`openinference-semantic-conventions` 0.1.41, Apache-2.0). Pin the semconv version, because attribute names can still change while the status is "Development".

---

## 9. Monorepo vs separate repos; naming

- **GitHub naming rule:** "The repository name must not exceed 100 characters, and can only contain ASCII letters, digits, and the characters `.`, `-`, and `_`." GitHub's docs give **no** naming style (kebab-case or another). Source: GitHub Docs, "Creating a new repository" https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository — primary. GitHub's "Best practices for repositories" covers README, security features, branch protection and Git LFS, not naming or monorepos: https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories — primary.
- **Lowercase kebab-case** (for example `seo-checker`) is a common convention, not a GitHub rule. It avoids case problems in URLs and on case-insensitive file systems. — secondary/convention, **unverified as any standard**.
- **Monorepo (well-known reference):** Potvin and Levenberg, "Why Google Stores Billions of Lines of Code in a Single Repository", *Communications of the ACM* 59(7), July 2016. Benefits: unified versioning, easy code sharing, atomic cross-project changes, large-scale refactoring. Costs: heavy tooling investment at Google's scale. — secondary (peer-reviewed magazine article; the page returned 403 in this session, so I cite it from memory: **unverified quote**).
- **Small-team view:** "Monorepos win when teams share code and deploy together; polyrepos win when teams are genuinely independent", and "you can always split later; merging repos back together is far more painful". Source: Sourcegraph, "Monorepo vs Polyrepo" https://sourcegraph.com/blog/monorepo-vs-polyrepo — vendor/secondary.
- **Advice (mine):** one new repo for the platform with `backend/` (FastAPI + workers) and `web/` (React) together, the same layout as SEOAdvisor today. Reuse the SEOAdvisor code by copying or vendoring the provider and tool modules, or later by publishing a small internal package. Do not start with a shared multi-repo setup for 1–2 engineers. Suggested names: `seo-checker` or `gurzu-seo-platform` (lowercase, hyphens).

---

## Items marked unverified
1. Service account added as a Search Console **user** for the Search Console API: widely used, but not stated in the Search Console API docs (5.1).
2. PSI API quota numbers (4.3).
3. Google not supporting IndexNow: based only on its absence from the participant list (5.4).
4. `gemini-embedding-001` default dimension of 3,072 (1.6).
5. Legal reading that an SEO SaaS may use the TimescaleDB Community Edition under TSL (1.9).
6. CACM monorepo article quotes (9).
7. CrUX data availability for these two origins (4.2).
