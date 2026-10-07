# Slice 1, part 2a: safe fetcher (7 Oct 2026)

Part 2a of slice 1 is complete: `integrations/http_fetch/`. Part 2b (sitemap reader, page types, inventory service) is next.

## Owner decisions

1. Reuse the SEOAdvisor code (`~/projects/Gurzu/SEOAdvisor`, GitHub `raksha-gurzu/SEOAdvisor`), but only the parts that slice 1 needs, changed to our rules.
2. Packages: httpx 0.28.1, Protego 0.7.0, lxml 6.1.3 (lxml in place of defusedxml: the old sitemap parser uses it, and slice 4 needs it for HTML). All BSD-3-Clause. `mise run audit`: no known vulnerabilities.
3. Page types for MyPipit (data, not code; part 2b): `/blog` blog_index, `/blog/category/*` blog_category, `/blog/*` blog_post, `/marketplace` listing_index, `/marketplace/*` listing, `/pages/*` static, `/sellers/*` seller, others other. First match wins. Language: site default (`en`).

## Spike result (see `experiments/2026-10-07-mypipit-sitemap/README.md`)

MyPipit has no `robots.txt` (404), one `/sitemap.xml` with 58 URLs, English only.

## Files

| File | Contents | Source |
|---|---|---|
| `http_fetch/guard.py` | `ip_is_public`, `public_addresses`, `is_public_url` (http/https only), `guard_request`, `PublicOnlyBackend`, `BlockedAddressError` | SEOAdvisor `base.py`, plus the scheme check |
| `http_fetch/client.py` | `FetchConfig`, `public_client`, `bounded_get`, `gunzip_capped`, `HostRateLimiter` | SEOAdvisor `base.py`, plus the new rate limiter |
| `http_fetch/robots.py` | `robots_body`, `RobotsRules`, `SafeFetcher`, `RobotsDisallowedError` | SEOAdvisor `fetcher.py` (robots part), plus a new small class |
| `tests/integrations/` | 95 tests: guard, limits, encodings, redirects, deadline, rate limiter, robots | Ported from SEOAdvisor tests; `httpx.MockTransport` in place of `respx` |

## Changes from the SEOAdvisor code

- No test hook in production code (old `address_check`). Tests replace `socket.getaddrinfo`.
- An SSRF block stays `BlockedAddressError`. The old robots code turned every HTTP error into "robots.txt unreachable".
- Explicit http/https check.
- `FetchConfig` has no defaults. Part 2b fills it from `Settings`.
- Names: exceptions end in `Error` (ruff N818). `robots_agent` (was `robots_token`; ruff S106 thought it was a password).

## Checks

1. Tests first: collection failed before the code; after the code, 49 pass. `mise run check`: 55 tests, mypy strict, import rules kept.
2. One live request: MyPipit `robots.txt` = 404, sitemap allowed. `http://169.254.169.254/` (cloud metadata) blocked before sending.

## Security review (independent review agent, 7 Oct 2026)

`CLAUDE.md` requires a security review for fetch changes. The `security-review` skill failed (no `origin/HEAD`, changes not committed), so a separate review agent read the code and the httpx/httpcore source. It found 9 problems, most of them in the reused SEOAdvisor code. The owner chose: fix all now; ports 80 and 443 only.

| # | Finding | Fix |
|---|---|---|
| 1 High | httpx unpacks gzip before the size check, and accepts "gzip, gzip". 173 bytes became 18 MB in memory (confirmed by a local test). | `iter_raw()`, own gzip decoder with an output limit, only identity or one gzip, `Accept-Encoding: gzip`. Re-test: refused; a 200 MB bomb used no extra memory. |
| 2 High | httpx reads every redirect body fully, up to 20 hops. | `follow_redirects=False`; the redirect body is never read; at most 5 hops. |
| 3 Med-High | The time limit did not cover connect, TLS or headers. | Total deadline (`deadline_scope`); `DeadlineStream` gives each read and write only the time left. |
| 4 Medium | Redirects skipped robots.txt and the rate limit. | `SafeFetcher` follows redirects itself: robots check, rate limit and limits on every hop. |
| 5 Medium | `S.example`, `s.example:443`, `a@s.example` were 3 rate-limit keys. | `origin_key()` and `httpx.URL(...).host`: one key per site. |
| 6 Low-Med | NAT64 and other IPv6 forms of private IPv4 passed. | Check the IPv4 inside; block `::/96`, `64:ff9b:1::/48`, `fec0::/10`. |
| 7 Low | A DNS-rebinding block looked like "robots.txt could not be read". | The backend raises `BlockedAddressError`. |
| 8 Low | Ports, secrets in messages, large robots.txt, cache age, unguarded client. | Ports 80/443; messages without user info or query; first 500 KiB of robots.txt; cache max 24 h; every client has the guard. |
| 9 Tests | Tests did not use the real guard path; ranges missing. | Fake DNS + guard hook in every `SafeFetcher` test; streamed fake bodies; a test per finding and range. |

### Second review (same agent, after the fixes)

All 9 findings: FIXED, checked against the httpx and httpcore source (for example: `iter_raw` does not decode; with `follow_redirects=False` httpx returns the 3xx without reading its body; `DeadlineStream` covers h11 header reads and the TLS handshake; a pooled connection uses the deadline of the current request). It found 4 small new problems, now fixed with tests:

1. A redirect to `ftp:` or `file:` crashed with `KeyError`. Now `BlockedAddressError` (`require_web_scheme`, checked on every hop). A target that is not a valid URL (`javascript:x`) gives `httpx.InvalidURL`, because httpx checks `Location` itself. For robots.txt, an invalid target counts as unreachable (disallow).
2. The total time limit applied to each hop (worst case about 42 × `deadline_s`). Now one deadline for the whole `get()`, robots.txt reads included: an inner `deadline_scope` can only make the deadline earlier.
3. A final 3xx for robots.txt (no target, for example 304) meant "allow all". Now unreachable (disallow).
4. `max_bytes` below 1 removed the limit. Now a `ValueError`.

After the second fixes: `mise run check` passes (101 tests); `mise run audit`: no known vulnerabilities; live MyPipit sitemap still loads.

Known limit: Python's DNS lookup has no timeout of its own; the system resolver stops after a few seconds.

After the fixes: `mise run check` passes (92 tests). Live: the MyPipit sitemap loads through the full path; `169.254.169.254` and port 8080 are blocked.

## Open

- `Retry-After` and back-off for 429/503 are not built. The crawler (slice 4) needs them (R1 §3.5).
- httpx releases are slow (0.28.1, Dec 2024), and the guard uses a private httpcore hook. `test_public_client_installs_the_guard_and_the_pinned_backend` fails if an update breaks it.
- The `security-reviewer` subagent does not exist yet (step 0.9). This review used a general agent with a security prompt.

## Next

Part 2b: `features/inventory/` (sitemap reader with `recover=False`, page types from site data, `discover_pages` service, a command that prints the MyPipit page list), the fetch settings in `Settings`, and the inventory import contract.
