# Verify: Frontend redesign

**Date:** 2026-10-22
**Overall:** PASS WITH WARNINGS

Tasks 1.1 to 5.3 are implemented and verified on this host. Task 5.4 (retire the static UI) waits for the owner's acceptance of the new frontend. Container, Compose start and hosted CI runs remain unexecuted here, as for the offline prototype; this change does not close those gates.

## Completeness

- BASELINE (commit `11331ad`, before this change): `./scripts/verify.ps1` ran sync, Ruff (pass) and the API suite: 169 passed, 1 skipped (PostgreSQL, no `TEST_DATABASE_URL`), 2 warnings (Starlette's HTTPX test-client deprecation; a Pydantic `alias` attribute warning) in 293 s. The browser session then had 2 timing failures (`test_offline_acceptance` waiting for "Version 2", `test_review_workspace` waiting for source text) while a dependency install and a test collection ran on the same machine. Rerun alone: 5 passed in 60 s. The static UI's 5-second waits are sensitive to machine load; the new browser tests wait on real states instead.
- Collected test IDs: 170 API (`apps/api/tests`) and 5 browser (`tests/e2e`).
- PASS: tasks 1.1 to 5.3 in [tasks.md](tasks.md) are done (commits `a7645bc` to the documentation commit of task 5.3).
- OPEN: task 5.4 retires the static UI after owner acceptance; until then both frontends run and the static UI's browser tests stay green.

### Parity matrix

Each assertion of the static-UI browser suite and the test that replaces it in the new frontend. The static tests keep running until task 5.4.

| Static-UI test and assertion | Replacement |
|---|---|
| `test_login`: unauthenticated `/` reaches `/login` | `test_web_login::test_sign_in_is_responsive_keyboard_operable_and_local` |
| `test_login`: wrong password shows a focused alert and keeps the typed value | same |
| `test_login`: no horizontal overflow at 1366 and 375 | same |
| `test_login`: correct sign-in opens the workspace with a named session | same |
| `test_login`: no request leaves the local origin | same, plus the Node network guard in every `test_web_*` test |
| `test_review_workspace`: import through the browser | `test_web_intake::test_intake_lists_manifest_documents_and_blocks_until_matched` |
| `test_review_workspace`: search the queue and open the claim | `test_web_queue::test_filters_live_in_the_url_and_survive_opening_a_claim` |
| `test_review_workspace`: P05 detail names the conflicting discharge date | `test_web_review::test_date_discrepancy_shows_both_values_with_exact_sources` |
| `test_review_workspace`: discharge page 1 source text shows 2026-10-15 | same |
| `test_review_workspace`: source appears above the review form | `test_web_review::test_date_discrepancy_shows_both_values_with_exact_sources` (evidence precedes the next action) |
| `test_review_workspace`: "Version 1" label | `test_web_review` and `test_web_acceptance` (`Source version`) |
| `test_review_workspace`: 1366, 375 and 2x layouts, keyboard focus, no page errors, assets load | `test_web_review::test_review_is_keyboard_operable_and_responsive`, `test_web_accessibility` |
| `test_corrections_workspace`: correction saved, handoff recorded, reload keeps both, history lists the handoff | `test_web_corrections::test_correction_request_handoff_and_acknowledgement_persist` |
| `test_evidence_pages`: manual comparison records a page-2 anchor | `test_web_corrections::test_manual_comparison_records_a_second_page_anchor` |
| `test_offline_acceptance`: import, discrepancy source, correction handoff and acknowledgement, corrected import, resolve, manual P07/P08, different supervisor acknowledgement, guarded completion, CSV and printable record, denied second account, process restart, loopback-only network | `test_web_acceptance::test_full_review_through_the_web_frontend_with_restart_and_network_guards` |

### Visual review (one batch, one confirmation pass)

Screens: `tests/e2e/test_web_screens.py` writes sign-in, queue, intake, Import with scan confirmation, review (date discrepancy and narrative agreement), correction progress, Complete (blocked and done) and the supervisor acknowledgement view at 1366x768 and 375x812 to `test-results/web/screens/`. Reviewed against the brief and the design skill's checklist (its native-app items such as safe areas and Dynamic Type do not apply to this web app; dark mode is a deliberate departure because the DSD defines a light theme only).

| Finding | Severity | Correction |
|---|---|---|
| F1: case header and phase tabs took about 410 px of a 768 px screen; the next action and source text fell below the fold | Material | Header compressed to two lines (identity, inline metadata including AI status); phase tabs one line each; about 250 px |
| F3: checks that cite whole documents (required documents, values, narrative) highlighted every labelled field | Material | Only checks whose anchors name fields (P01, P04, P05, P08) highlight values; others list the cited pages; covered by `evidence.test.ts` |
| F4: on a blocked Complete page the exact blockers sat below the full summary | Material | Remaining blockers render directly under the blocked Complete button |
| F6: at 375 px the documents table broke words inside document names | Material | Status moves under the document on phones; filenames break safely |
| F7: on phones the scanned original appeared after an 18-row value list, far from the form | Material | Order on phones: form, original, value list; desktop keeps the original beside both |
| F5: header read "reviewer · reviewer" | Minor | Role shown capitalized after the username |
| Live region above the site header (found in Task 12) | Material | Rendered at the top of the content column |

Confirmation pass: all screens recaptured after the corrections; every browser test passed afterwards (43 web tests).

## Correctness

- PASS: `./scripts/verify.ps1` (2026-10-22, this host): sync, Ruff, API tests 181 passed and 1 skipped (PostgreSQL, no `TEST_DATABASE_URL`), web install from the lockfile, 70 web unit tests, type check, lint, production build, then 48 browser tests passed (43 against the new frontend, 5 against the static UI). After the final review: 51 browser tests passed (46 new frontend, 5 static UI), adding double-activation and queue-prefetch regressions, 1 warning (Starlette's HTTPX test-client deprecation).
- PASS: web unit tests (`node --test`, 70 tests): proxy header rules, API error mapping without retries, safe return paths, token contrast from `globals.css`, queue parameters, manifest matching, import retry reusing the created case, labels and plain reasons, phase resolution, bounded polling that drops late answers, evidence marks and highlights, next-action rules, evidence page parsing.
- PASS: `pnpm --dir apps/web typecheck`, `lint` and `build` (Next.js 16.4.2, Turbopack); every page renders per request.
- PASS: API suite including the new `test_proxy_boundary.py` (trusted origin allowed; foreign origin denied with "Cross-origin changes are not allowed."; bare HTTPS origins enforced in production) and `test_differences.py` (P05 names each source value and page; P04 shows the case value; unconfirmed scan readings never appear; other checks empty).
- PASS: contract. `tests/e2e/test_web_contract.py` captures real responses (session, config, case, receipt, claim, bundle, review state with a confirmation, correction task and expectation, queue, stats, report, reports) and compares their shape with the committed samples; `contract-check.ts` assigns each sample to its wire type during the type check. Adding a key the API never sends fails the type check (checked).
- PASS: browser acceptance through the new frontend (`test_web_acceptance.py`): named sign-in; supervisor MFA; import through intake with real processing state; the P05 discrepancy with both dates and their documents, pages and version; correction request, handoff and acknowledgement as separate events; corrected-version import as version 2; resolution after recheck; manual P07 and P08 with required evidence; a different supervisor's acknowledgement; guarded completion with "Ready for final submission review"; CSV and printable record; a second reviewer denied through page and proxy (claim, original, report export, queue); a real restart of the review service with state, sources and record intact; a re-run that marks the record stale while it stays inspectable. The review service's Python socket guard, the Next.js server's Node guard and the browser's request router recorded no request beyond loopback.
- PASS: Review Focus items. 12 MiB original through the proxy (`test_large_original_passes_through_the_proxy_intact`); double activation records one event (`test_double_click_save_records_one_event`); a failed upload retry reuses the case and key (`test_retry_after_failed_upload_reuses_case_and_key`); unsafe `next` values return to `/claims` (`safe-next.test.ts`, `test_unsafe_next_falls_back_to_claims`); unconfirmed scan readings are not evidence (`test_differences.py`, `test_scan_readings_are_not_shown_as_evidence`).
- PASS: drafts. Stale revision keeps the draft, "Load latest" holds Save until the refreshed revision arrives, then saves once; an expired session opens sign-in over the page, nothing is saved or replayed until the reviewer saves again; leaving with unsaved input is guarded (headless Chromium cannot show the native prompt, so the test checks that the guard cancels a dispatched `beforeunload`).
- PASS: accessibility and layout (`test_web_accessibility.py`): keyboard-only path through each phase action; 2px focus never covered; no horizontal overflow at 375px, 1366px and 683px at 2x; reduced motion removes transitions; status always has text; rendered text contrast at least 4.5:1; one live region per page; no polling on the queue.
- PASS: the static UI's five browser tests still pass alongside the new frontend.
- PASS: Compose 5.6.1 `config --quiet` accepts the `frontend` service. This is configuration parsing only.

## Coherence

- PASS: FastAPI keeps authentication, permissions, revisions, jobs, storage and closeout; the web app renders what the service allows and never decides authorization. Backend changes are limited to `TRUSTED_ORIGINS` and the additive `differences` field; no rule version, status, migration or stored data changed.
- PASS: placement follows `.cursor/rules/repository-structure.mdc` (routes in `src/app`, features in `src/features`, primitives in `src/components/ui`, infrastructure in `src/lib`, browser flows in `tests/e2e`).
- PASS: canonical documents updated through the engine: DSD (identity, tokens, layout, composition, motion, audit, visual settings 6/1/6), SDD (web tier, proxy boundary, CI), build guide (stack, traps, commands), state (D10, A10), HANDOFF; `materialize.py` regenerated AGENTS.md, DESIGN.md and BRAND.md.

## Review quality

- PASS: security. Same-origin proxy with header allow-lists, `no-store` on every proxied response, nonce CSP and frame denial on pages, no tokens or drafts in browser storage, server-only `BACKEND_URL`, trusted origins validated, CSRF and case authorization unchanged in FastAPI.
- PASS: every requirement in the delta spec has a browser or unit test named above.
- WARN: login throttling sees the web server's address for every browser (acceptable on one machine; hosting needs trusted forwarded headers).
- N/A: AI paths. Remote inference stays off; the interface states "AI comparison: not run (offline)".

## Findings

- FIXED (final review): queue rows prefetched every claim page, costing three API reads per row per queue view; rows now load on demand (`test_queue_does_not_render_every_claim_in_advance`).

- WARNING: the frontend container image, Compose start and CI run have not executed on this host (no Docker engine, no hosted CI run).
- WARNING: no session with a real screen reader; automated semantics checks only.
- WARNING: this host runs Node.js 25.4.0 (non-LTS); CI and the image pin 24.22.1.
- SUGGESTION: browser Back inside the app is not intercepted while a draft is unsaved; the draft is kept only while the page stays open.
- OPEN: task 5.4 (retire the static UI) waits for the owner's acceptance of the new frontend.
