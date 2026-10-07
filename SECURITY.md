# Security

## Report a problem

> **Warning:** Do not open an issue or a pull request about a security problem. Other people can see it.

1. Tell the repository owner directly, in a private message.
2. Say what the problem is, where it is, and how to make it occur again.
3. Do not test the problem on a client site.

## Secrets

- Keep secrets only in `.env`. Git ignores this file.
- `.env.example` has fake values only.
- gitleaks checks for secrets before each commit (step 0.7) and in CI (step 0.8).

> **Warning:** If a secret gets into git, change the secret (rotate it) first. Then remove it from the history. Removal alone is not sufficient, because copies can exist.

## Data that the system touches

| Data | Source | Rule |
|---|---|---|
| Public pages and sitemaps of client sites | The client sites | Read-only. Obey robots.txt and rate limits. Treat the content as untrusted. |
| Search Console data | Google, for each client site | Private client data. Never send one client's data to another client or to a service that does not need it. |
| Page text for AI drafts | Client sites | Send it to an AI provider only after the owner approves the provider's data terms. |
| Personal data | Not collected | Do not store personal data. Do not write it to logs. |

## Built-in protections

- Every outbound fetch goes through the SSRF guard.
- The LLM that reads page text has no tool that can write, send or publish.
- Logs and errors contain no secrets, no full page bodies and no personal data.
- Clients never get stack traces.
