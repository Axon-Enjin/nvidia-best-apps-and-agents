<!-- fmd:pointer --> Built on FMD v3.0.1. Before any docs/ work, follow the FMD v3.0.1 kernel. Run that engine's scripts against docs/. Never copy engine files into this repo.

<!-- MATERIALIZED from docs/build-sentinel-node.md by scripts/materialize.py on 2026-10-22. Do not hand-edit; edit the canonical doc and re-run. -->

# Project Build Guide

**Project:** Sentinel Claims
**Date:** 2026-10-21
**Version:** 0.1
**Owner:** Yushin
**Status:** Draft
**Last reconciled:** 2026-10-22
**PRD:** `docs/prd-sentinel-node.md`
**SDD:** `docs/sdd-sentinel-node.md`
**SAD:** N/A; work inline by default.

## 1. How to Build From These Docs

At session start, read root `HANDOFF.md`, `docs/state.md`, then the active change's `docs/changes/offline-prototype/tasks.md` and `verify.md`. Product scope is already accepted and the owner explicitly resumed implementation on 2026-10-21. Work on `feat/offline-prototype`. Draft release/assurance documents record pending evidence; they do not reinstate the earlier owner pause.

For behavior use PRD and the active change's delta spec; for architecture use SDD; for UI use DSD; for tests use QAD. The task list owns progress. When a Locked artifact must change, write and propagate a Change Record. Preserve existing source/results through additive migrations.

### External documentation engine

External engine on this machine: `C:/Users/Yushin/tools/fmd-v3.0.1`, source `https://github.com/delatorrecj/fmd.git`, tag v3.0.1, commit `4979fda6435dc007a331c40a5e9e28db813eebb2`. Before docs work read that engine's `AGENTS.md` and trigger matrix; run its scripts against project `docs/` with `PYTHONDONTWRITEBYTECODE=1`.

**Owner restriction: never commit or push anything to the FMD repository.** Use the engine read-only. Commits belong in this current project repository. No push, cloud purchase or real-patient-data processing is implied by local build authorization.

## 2. Execution

Work inline. Test new behavior before implementing it, run the affected tests then the full suite, and commit reviewable increments. Record concrete plan deviations and test evidence in the active change's verification record. Preserve optional untracked research and the older prototype plan; they are not the active specification.

## 3. Stack Currency & Deprecations

`uv.lock` is the exact dependency source. The versions below were observed in the installed environment on 2026-10-21, not selected from memory. Framework conventions must be checked against primary documentation before implementing a new sensitive path.

| Layer | Installed version | Verified date | Primary reference |
|---|---|---|---|
| Python | 3.14.5; declared support >=3.12,<3.15 | 2026-10-21, local interpreter | [Python documentation](https://docs.python.org/3.14/) |
| uv | 0.11.19 | 2026-10-21 | [Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) |
| FastAPI / Starlette | 0.156.4 / 1.9.0 | 2026-10-21 | [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/) |
| SQLAlchemy / Alembic | 2.0.55 / 1.20.0 | 2026-10-21, installed metadata | [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/), [Alembic](https://alembic.sqlalchemy.org/en/latest/) |
| Uvicorn / HTTPX | 0.54.0 / 0.28.1 | 2026-10-21, installed metadata | [Uvicorn settings](https://www.uvicorn.org/settings/), [HTTPX transports](https://www.python-httpx.org/advanced/transports/) |
| pytest / Ruff / Playwright | 9.1.1 / 0.17.1 / 1.64.0 | 2026-10-21, installed metadata | [pytest](https://docs.pytest.org/), [Ruff](https://docs.astral.sh/ruff/), [Playwright Python](https://playwright.dev/python/docs/intro) |
| pypdf | 6.21.1 | 2026-10-21, installed metadata | [pypdf](https://pypdf.readthedocs.io/en/stable/) |

Windows printed OCR is verified with Tesseract 5.5.3.20260724 and English tessdata_fast 4.1.0 (pinned SHA-256 in OCR-NOTICES.md). Pillow 12.3.0 and pypdfium2 5.14.0 are locked. Container artifacts pin Python 3.14.5, PostgreSQL 17.11 image digests and Debian Tesseract 5.5.0-1+b1, but those images have not run. Docker engine, WSL, Podman and PostgreSQL remain unavailable on this host. Compose 5.6.1 configuration validation passes; this is not container/database acceptance.

| Trap | Current rule | Evidence |
|---|---|---|
| Unresolvable `httpx2>=0.22,<1` development constraint | Remove that invalid constraint and use the existing locked test environment | `uv sync --locked` succeeds; baseline tests run |
| Starlette TestClient warns about deprecated HTTPX support | Record the warning; verify a supported migration before adding a different transport package | One deprecation warning in the 37-test run; no warning suppression |
| Assuming `uv --offline` blocks application traffic | It controls package operations only; test application provider guards and independently block egress for final acceptance | Offline change design and Task 10 |

## 4. Golden-Path Patterns

Verified 2026-10-21 against the installed stack: use `TestClient(create_app(settings, database))` as a context manager so lifespan runs; inject a temporary database/settings explicitly. The real examples are `tests/test_workflow.py` and `tests/test_offline.py`.

For remote adapters, test the transport boundary with `httpx.MockTransport` and assert no request was sent offline. Test doubles are test-only; never expose their output as runtime findings. Runtime retains explicit unavailable AI coverage. P07 uses source-backed manual comparison and a different supervisor acknowledgement; no fabricated automated result is substituted.

## 5. Conventions & Guardrails

Use existing focused modules; introduce account, bundle/storage, review and report modules only as their tasks require. Server transactions own case revisions and completion. UI state cannot authorize operations. Original evidence and published review snapshots are immutable; decisions append events.

Synthetic patient records only. Keep the environment indication and export provenance. Credentials alone cannot enable remote calls; `NETWORK_MODE=online` is an explicit opt-in. Keep all core UI assets local and default server binding to loopback. Named authorization, encrypted credentials/secrets, bounded uploads and reliable coverage remain necessary even for an offline prototype.

Closeout re-verifies encrypted original hashes in the same transaction as the current-version guards/snapshot. Review actions and extraction confirmations append events and fence the current revision. Retired cases stay denied after restoration with the newest authenticated tombstone ledger.

Task verification:

```powershell
uv sync --locked
uv run --locked pytest tests/test_offline.py -q
uv run --offline --locked pytest -q
git diff --check
```

Run the task-specific tests in `tasks.md` when they exist. A passing legacy suite cannot establish role, OCR, report or UI features that have not been implemented. Full lint, real browser correction/restart and encrypted SQLite restore checks now exist. The PostgreSQL test explicitly skips without TEST_DATABASE_URL. CI is prepared but has not executed. See LOCAL-SETUP.md and the active verification record for the open runtime gates.

## 5.1 Change Workflow

The active change is `docs/changes/offline-prototype/`. Keep proposal, design, tasks, delta spec and verification coherent. Validate using the external engine's `scripts/change.py validate offline-prototype docs/`. Archive only after the change is actually verified; uncompleted tasks remain unchecked.

## 5.2 Public Surface and Crawler Policy

No public deployment in this milestone. Serve UI locally; private sources still require authorization. No CDN, analytics or runtime policy fetch is needed. Before eventual hosting, validate HTTPS/private access, no indexing of sensitive routes and the full release gates. A crawler directive is never an access-control mechanism.

## 5.3 Engineering Maturity

L1 is required by multiple contributors; actual established practice is local verification, with no working CI/preview/deploy pipeline claimed. Add project CI during packaging and record its executed result separately. Current backup/restore and rollback are designed, not rehearsed. Branches and local commits are not deployments.

## 6. Materialization

This guide is canonical for the root build instructions. Run the external engine's `scripts/materialize.py docs/` after editing; it preserves the root FMD pointer. The external engine path and owner restriction above must remain in the generated instructions. Do not create additional platform files unless needed.

## Self-Check

- [x] Read order, authorized scope, exact installed versions, commands and owner restrictions recorded.
- [x] Current test evidence is distinguished from future prototype acceptance.
- [ ] PostgreSQL/OCR packaging, CI, browser acceptance and restore rehearsal completed.
