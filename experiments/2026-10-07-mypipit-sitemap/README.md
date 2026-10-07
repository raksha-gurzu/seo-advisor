# Spike: what does the MyPipit sitemap contain? (7 Oct 2026)

**Question:** Can the reused SEOAdvisor safety code read the MyPipit `robots.txt` and sitemaps? How many page URLs are there, and which URL patterns show the page type and the language?

**Run** (temporary packages; the project lock does not change):

```bash
uv run --no-project --with httpx --with protego --with lxml python experiments/2026-10-07-mypipit-sitemap/spike.py
```

## Answer (run on 7 Oct 2026, 2 requests)

1. **The reused safety code works.** The host has 1 public address. The pinned client and the size limit worked. Packages: httpx, Protego, lxml (temporary).
2. **`robots.txt` does not exist (HTTP 404).** RFC 9309: no rules, so all pages are allowed. There is no `Sitemap:` line, so the spike used `/sitemap.xml`.
3. **One sitemap file, not an index:** `/sitemap.xml`, 12 KB, **58 URLs**, 1 host, no query strings, no hreflang, no image tags.
4. **URL patterns:**

| Pattern | Count | Page type |
|---|---|---|
| `/blog` | 1 | blog index |
| `/blog/category/*` | 5 | blog category |
| `/blog/*` | 30 | blog post |
| `/marketplace` | 1 | listing index |
| `/marketplace/*` | 17 | listing |
| `/pages/*` | 3 | static page |
| `/sellers/*` | 1 | seller |

5. **Language:** all English. No language prefix and no hreflang. Use the site language (`en`).
6. **`lastmod`:** 51 of 58 URLs have it. Missing on `/marketplace`, the 5 blog categories and `/sellers/my-pipit`.

## Notes for later slices

- `/marketplace/*` mixes treks, tour packages and guide profiles (for example `/marketplace/pasang-tenzing-sherpa`). The URL alone cannot separate them. Slice 4 can use the page content (title, structured data) for a finer type.
- Possible audit findings: no `robots.txt`; the home page `/` is not in the sitemap; 7 URLs have no `lastmod`.
- The research said "474 + 53 URLs". MyPipit now has 58. The 474 is probably extendmy.life.

## Fixtures

`fixtures/sitemap.xml` (the real file) and `fixtures/robots.txt` (empty, because the answer was 404). Slice 1 tests copy them.
