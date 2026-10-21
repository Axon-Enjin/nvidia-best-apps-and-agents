# Design: Frontend redesign

**Date:** 2026-10-22
**Status:** Draft

## Technical approach

**Two processes, one origin.** The browser talks only to the Next.js server. Pages are Server Components that call FastAPI directly with the reviewer's `sentinel_session` cookie (`apps/web/src/lib/backend.ts`, server-only, `cache: 'no-store'`). Browser calls go to `/api/*`, a route handler that streams method, body and an allow-list of headers to `BACKEND_URL` and returns status, body, `Set-Cookie` and download headers with `Cache-Control: no-store`. FastAPI accepts mutations whose Origin equals its own or appears in `TRUSTED_ORIGINS`; the CSRF token and SameSite=Strict cookie are unchanged. FastAPI rechecks the session and case access on every request.

**Pages and phases.** Routes: `/login`, `/claims` (queue; view, search and page in the URL), `/claims/new` (intake), `/claims/<id>` (redirects to the phase that needs action), `/claims/<id>/import`, `/claims/<id>/review?issue=P05`, `/claims/<id>/complete`. `/` forwards old `#case=<id>` links. Phase resolution: no current version, processing, or scan values awaiting confirmation lead to Import; completion allowed or already completed leads to Complete; anything else leads to Review.

**Security headers.** `src/proxy.ts` sets a per-request nonce CSP, frame denial, nosniff and same-origin referrer policy on pages. Its matcher excludes `/api`, because Next.js buffers and silently truncates request bodies above 10 MB on routes where proxy runs; uploads reach 25 MB per file.

**State.** No client state library. Review selection lives in the URL (`replaceState`). Drafts live in component state and stay mounted across refreshes while dirty. A 401 during an edit opens a sign-in dialog over the page; a 409 shows a conflict notice and a `Load latest` action. Neither replays the request. Processing status polls at 1.5 s for at most 80 polls and aborts on navigation.

**Contract.** FastAPI returns plain dicts, so OpenAPI has no response schemas. TypeScript wire types are written from the Python builders and checked by assigning captured real responses (`apps/web/src/lib/contract-samples/`) to them at type-check time; `tests/e2e/test_web_contract.py` fails when a live response's shape drifts from the committed sample.

**Design.** Minimalism and Swiss style with an editorial archive composition: a compact issue list beside a generous source-reading column, mono document labels (`CF2 claim summary · page 1 · version 1`), lettered evidence marks shared by the What differs table, the document tab and the highlighted source text. DSD colors, system fonts, lucide icons, 120 ms color and 150 ms selection transitions, none under reduced motion.

### Decisions

| Decision | Choice | Reason |
|---|---|---|
| Boundary | Route handler proxy plus `TRUSTED_ORIGINS` | Explicit header control; FastAPI otherwise rejects the web origin. |
| TypeScript | 6.0.3 | `typescript-eslint` peers `typescript <6.1.0`; 7.0.2 is unsupported. |
| ESLint | 9.39.5 | React, jsx-a11y and import plugins peer ESLint 9. |
| Node.js | `engines >=20.9.0`; CI and Docker 24.22.1 LTS | Next.js 16 minimum; LTS for reproducible builds. Host runs 25.4.0. |
| Unit tests | `node --test` with type stripping | Pure modules only; no extra framework. |
| Browser tests | Python Playwright (`tests/e2e/test_web_*.py`) | Reuses the installed stack and loopback guards. |
| Icons and fonts | lucide-react; system fonts | One local SVG family; no font files. |
| Not built | Drag-and-drop, assignment UI, legacy XML import screens | Not needed for the flow; the brief forbids unrelated admin features. |

### Design research

ui-ux-pro-max (commit 3eccfd8) was queried on 2026-10-22. Its general recommendation (hero with testimonials, neumorphism, cyan palette, remote Google Fonts, GSAP scroll reveal) was rejected as a marketing pattern that breaks offline use. Adopted: Minimalism and Swiss Style (grid, single accent, clear hierarchy), Editorial Grid (asymmetric columns, print-like labels; drop caps, pull quotes, parallax and serif body rejected), focus-not-obscured, focusable error summary, never color alone, reduced motion, Server Components by default, semantic `@theme` tokens. Rejected: "reduce opacity" disabled states, in favour of explanations beside blocked actions. Progressive disclosure and master-detail queries found no database match; those patterns come from the brief and DSD.

## Data / API impact

- `Settings.trusted_origins` (`TRUSTED_ORIGINS`): bare `http(s)://host[:port]` values; HTTPS only in production.
- Each check gains `differences`: `[{field, expected, sources: [{document_id, type, bundle_id, value, page}]}]`, filled for P04 (expected is the case value) and P05 (expected is null). Statuses, reasons, anchors and the rule version are unchanged. Unconfirmed scan readings never appear.
- No schema, migration or stored-data change.

## Risks

- Next.js proxy truncation of large bodies: matcher excludes `/api`; a 12 MiB upload test guards it.
- Two server processes locally: setup docs, `verify.ps1`, CI and Compose start both; the login page names an unreachable review service.
- Login throttling sees the proxy's address for every user. Acceptable for one local machine; hosting needs trusted proxy headers first.
- Node 25.4.0 on the host is not an LTS release; CI and Docker pin 24.22.1.
- Container image, Compose start and CI remain unrun on this host.
