# Verify: Frontend redesign

**Date:** 2026-10-22
**Overall:** FAIL (in progress)

Implementation is in progress. Sections below record the baseline and are completed as each slice lands.

## Completeness

- BASELINE (commit `11331ad`, before this change): `./scripts/verify.ps1` ran sync, Ruff (pass) and the API suite: 169 passed, 1 skipped (PostgreSQL, no `TEST_DATABASE_URL`), 2 warnings (Starlette's HTTPX test-client deprecation; a Pydantic `alias` attribute warning) in 293 s. The browser session then had 2 timing failures (`test_offline_acceptance` waiting for "Version 2", `test_review_workspace` waiting for source text) while a dependency install and a test collection ran on the same machine. Rerun alone: 5 passed in 60 s. The static UI's 5-second waits are sensitive to machine load; the new browser tests wait on real states instead.
- Collected test IDs: 170 API (`apps/api/tests`) and 5 browser (`tests/e2e`).
- PENDING: tasks 1.1 to 5.4 in [tasks.md](tasks.md).

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

## Correctness

- PENDING.

## Coherence

- PENDING.

## Review quality

- PENDING.

## Findings

- None yet.
