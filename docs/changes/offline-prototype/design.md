# Design: Offline first working prototype

**Date:** 2026-10-21
**Status:** Draft

## Technical approach

The approved [system design](../../sdd-sentinel-node.md) remains the architecture. Deliver its local slice in dependency order using [tasks.md](tasks.md). Use existing modules until a responsibility needs separation; retain legacy endpoints while tests protect them, then migrate the browser to the new contracts explicitly.

`NETWORK_MODE=offline` is the default. Values other than `offline` or `online` fail validation. Provider calls require `online` plus configured credentials; credentials alone cannot enable them. The API rejects an explicit remote-review request offline. The worker must also handle an already-queued remote job safely after an operator switches offline: retain local results, mark model coverage `not_run_offline`, and keep the case incomplete until the real manual-review workflow is completed. The provider adapter independently rejects offline calls before constructing a request.

The current scaffold does not yet implement manual P07 acknowledgement or P10 finalization. Adding an offline flag does not make those capabilities complete. No overall model-clearance or ready status may be inferred from disabling inference.

All browser CSS, JavaScript, fonts, icons, document viewers and OCR assets must be served locally. Use local username/password accounts and locally verifiable privileged MFA; no email delivery, external identity provider, analytics or remote policy lookup is required. Exact security-library choices are verified against primary documentation before implementing account handling.

## Data / API impact

Task 1 adds settings and configuration output only. Subsequent migrations add accounts/sessions, bundle/document versions, source confirmations, append-only review/task events and finalization snapshots. Preserve old source/result data; do not rewrite the original migration as a shortcut. Schema/API transitions must be explicit and tested against both the supported local PostgreSQL target and optional development SQLite path.

Planned service boundaries, defined in tasks before use:

- `accounts.py`: authentication, session revocation, MFA and case-access checks.
- `bundles.py` / `storage.py`: versioned membership and immutable source bytes.
- `review.py`: dispositions, correction events, manual checks and revision guards.
- `reports.py`: transactional closeout and versioned CSV/printable records.
- Existing `audit.py`, `documents.py`, `worker.py` and `api.py`: extend with the accepted profile, source anchors and guarded contracts.

## Risks

- The current UI has no `app.css` or `app.js`: build the working queue/workbench rather than treating HTML as a completed screen.
- The old shared token cannot provide named role accountability: migrate it before calling the prototype multi-user.
- Docker is not available on the current command path: container artifacts can be prepared, but PostgreSQL/container verification must be reported pending until an available local runtime is used.
- A network-mode switch controls application provider behavior; it is not an operating-system firewall. Final acceptance blocks external traffic independently and inspects browser requests.
- Local OCR requires binaries/language data installed before disconnecting. Unknown or unreadable material stays incomplete.
- File backups alone cannot recover database references: restore a coordinated database/source checkpoint and verify hashes, roles and history.

## Iteration contract

Objective: finish one task's observable behavior and acceptance tests before moving to the next.
Observation: failing/passing tests, source/version data and the task's acceptance result.
Action: make the smallest implementation change for that task.
Verification: run the named tests, then the full suite; compare real output with expected behavior.
Progress Signal: new required behavior passes without regressing prior behavior.
Retry Condition: a concrete test failure identifies a fix within the approved scope.
Stop Condition: the task is verified and committed; record it in tasks/verify before proceeding.
Escalation Condition: missing external runtime, destructive migration, real-data request or new material product choice; preserve progress and identify the specific dependency.
