# Project Build Guide

**Project:** Sentinel Claims
**Date:** 2026-10-21
**Version:** 0.1
**Owner:** Yushin
**Status:** Draft
**Last reconciled:** 2026-10-23
**PRD:** `docs/prd-sentinel-node.md`
**SDD:** `docs/sdd-sentinel-node.md`
**SAD:** N/A; work inline by default.

## 1. How to Build From These Docs

At session start, read root `HANDOFF.md`, `docs/state.md`, then the active change's `docs/changes/hackathon-hosted-evaluation/tasks.md` and `verify.md` (the offline prototype's `docs/changes/offline-prototype/` records the local gates that remain open). Product scope is already accepted and the owner explicitly resumed implementation on 2026-10-21. Work on `feat/offline-prototype` until the freeze; the merge to `main` happens only at the freeze. Draft release/assurance documents record pending evidence; they do not reinstate the earlier owner pause. Repository layout and path moves are recorded in `docs/changes/repository-organization/`. The Next.js frontend is the change `docs/changes/frontend-redesign/` (tasks and verification there).

For behavior use PRD and the active change's delta spec; for architecture use SDD; for UI use DSD; for tests use QAD. The task list owns progress. When a Locked artifact must change, write and propagate a Change Record. Preserve existing source/results through additive migrations.

### External documentation engine

External engine on this machine: `C:/Users/Yushin/tools/fmd-v3.0.1`, source `https://github.com/delatorrecj/fmd.git`, tag v3.0.1, commit `4979fda6435dc007a331c40a5e9e28db813eebb2`. Before docs work read that engine's `AGENTS.md` and trigger matrix; run its scripts against project `docs/` with `PYTHONDONTWRITEBYTECODE=1`.

**Owner restriction: never commit or push anything to the FMD repository.** Use the engine read-only. Commits belong in this current project repository. No push, deploy, cloud purchase or real-patient-data processing is implied by build authorization; each push, each server spend (up to the $100 ceiling) and each deploy needs the owner's go-ahead for that step.

## 2. Execution

Work inline. Test new behavior before implementing it, run the affected tests then the full suite, and commit reviewable increments. Record concrete plan deviations and test evidence in the active change's verification record. Preserve optional untracked research and the older prototype plan; they are not the active specification.

## 3. Stack Currency & Deprecations

`apps/api/uv.lock` is the exact dependency source. The versions below were observed in the installed environment on 2026-10-21, not selected from memory. Framework conventions must be checked against primary documentation before implementing a new sensitive path.

| Layer | Installed version | Verified date | Primary reference |
|---|---|---|---|
| Python | 3.14.5; declared support >=3.12,<3.15 | 2026-10-21, local interpreter | [Python documentation](https://docs.python.org/3.14/) |
| uv | 0.11.19 | 2026-10-21 | [Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) |
| FastAPI / Starlette | 0.156.4 / 1.9.0 | 2026-10-21 | [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/) |
| SQLAlchemy / Alembic | 2.0.55 / 1.20.0 | 2026-10-21, installed metadata | [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/), [Alembic](https://alembic.sqlalchemy.org/en/latest/) |
| Uvicorn / HTTPX | 0.54.0 / 0.28.1 | 2026-10-21, installed metadata | [Uvicorn settings](https://www.uvicorn.org/settings/), [HTTPX transports](https://www.python-httpx.org/advanced/transports/) |
| pytest / Ruff / Playwright | 9.1.1 / 0.17.1 / 1.64.0 | 2026-10-21, installed metadata | [pytest](https://docs.pytest.org/), [Ruff](https://docs.astral.sh/ruff/), [Playwright Python](https://playwright.dev/python/docs/intro) |
| pypdf | 6.21.1 | 2026-10-21, installed metadata | [pypdf](https://pypdf.readthedocs.io/en/stable/) |
| Node.js / pnpm | 25.4.0 local (engines `>=20.9.0`); CI and image 24.22.1 LTS / pnpm 11.10.0 | 2026-10-22, nodejs.org release index, npm registry | [Next.js installation](https://nextjs.org/docs/app/getting-started/installation) |
| Next.js / React | 16.4.2 / 19.3.1 | 2026-10-22, `apps/web/pnpm-lock.yaml` | [Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components) |
| TypeScript / ESLint / eslint-config-next | 6.0.3 / 9.39.5 / 16.4.2 | 2026-10-22, peer ranges checked | [typescript-eslint](https://typescript-eslint.io/) |
| Tailwind CSS / lucide-react | 4.3.3 / 1.57.0 | 2026-10-22 | [Tailwind with Next.js](https://tailwindcss.com/docs/installation/framework-guides/nextjs) |
| Nebius Token Factory API | Base URL `https://api.tokenfactory.nebius.com/v1/`, OpenAI-compatible; Super `nvidia/nemotron-3-super-120b-a12b`; Nano ID unconfirmed | 2026-10-23, Token Factory docs quickstart and public model pages; Nano and prices unconfirmed until the probe | [Token Factory docs](https://docs.tokenfactory.nebius.com/) |
| Nebius AI Cloud | `cpu-d3` `2vcpu-8gb`; image `ubuntu24.04-driverless` 0.2.1108; region `us-central1` | 2026-10-23, Nebius CLI 0.12.294 (run in WSL) | [Nebius docs](https://docs.nebius.com/) |
| Tavily | Search API; CLI `tvly` 0.1.8; domain restriction to philhealth.gov.ph; `--include-raw-content true` (not `text`) | 2026-10-23, live test | [Tavily docs](https://docs.tavily.com/) |

The hosted build adds, unverified until S8: Caddy for HTTPS, uvicorn `--proxy-headers`, rclone for backups, and PostgreSQL 17 from `compose.yaml` on the server. Windows printed OCR is verified with Tesseract 5.5.3.20260724 and English tessdata_fast 4.1.0 (pinned SHA-256 in OCR-NOTICES.md). Pillow 12.3.0 and pypdfium2 5.14.0 are locked. Container artifacts pin Python 3.14.5, PostgreSQL 17.11 image digests and Debian Tesseract 5.5.0-1+b1, but those images have not run. Docker engine, WSL, Podman and PostgreSQL remain unavailable on this host. Compose 5.6.1 configuration validation passes; this is not container/database acceptance.

| Trap | Current rule | Evidence |
|---|---|---|
| Unresolvable `httpx2>=0.22,<1` development constraint | Remove that invalid constraint and use the existing locked test environment | `uv sync --locked` succeeds; baseline tests run |
| Starlette TestClient warns about deprecated HTTPX support | Record the warning; verify a supported migration before adding a different transport package | One deprecation warning in the 37-test run; no warning suppression |
| Assuming `uv --offline` blocks application traffic | It controls package operations only; test application provider guards and independently block egress for final acceptance | Offline change design and Task 10 |
| TypeScript 7.0 and ESLint 10 look current | `typescript-eslint` peers `typescript <6.1.0`; React, jsx-a11y and import lint plugins peer ESLint 9 | npm peer ranges, 2026-10-22 |
| Next.js `proxy.ts` on upload routes | When proxy runs, request bodies over 10 MB are silently truncated; the matcher excludes `/api` | Next.js `proxyClientMaxBodySize` docs; `test_large_original_passes_through_the_proxy_intact` |
| pnpm 11 build scripts | Ignored scripts fail install; `apps/web/pnpm-workspace.yaml` denies `unrs-resolver`'s download fallback | `pnpm install --frozen-lockfile` exit 0 |
| Token Factory model removals | Nebius removed Nemotron 3 Nano Omni and Llama-3.1 Nemotron Ultra 253B on Aug 31, 2026; keep model IDs in settings and confirm them with the probe | Owner report, Discord, 2026-10-23 |
| Token Factory billing country | The Philippines is not on the billing list; no spending cap exists on the account, so the app enforces its own $45 stop | Hackathon FAQ and staff replies, 2026-10-09 and 2026-10-23 |
| Nebius CLI on Windows | Does not run natively; use WSL, and the Nebius MCP launcher that pins Python 3.13 and `pydantic<2.13` | Friction log |
| Python text writes on Windows | Default encoding is cp1252; pass `encoding="utf-8"` when scripting edits to source files | Silent non-match on `·` during this change |

## 4. Golden-Path Patterns

Web app, verified 2026-10-22: pure modules are tested with `node --test` (relative `.ts` imports, no aliases); interaction is tested in real Chromium through `tests/e2e/test_web_*.py`, whose `web_stack` fixture starts FastAPI and the built app (`next start`) behind a loopback-only Node network guard. Run `pnpm --dir apps/web build` before those tests.

Verified 2026-10-21 against the installed stack: use `TestClient(create_app(settings, database))` as a context manager so lifespan runs; inject a temporary database/settings explicitly. The real examples are `apps/api/tests/test_workflow.py` and `apps/api/tests/test_offline.py`.

For remote adapters, test the transport boundary with `httpx.MockTransport` and assert no request was sent offline. Test doubles are test-only; never expose their output as runtime findings. Runtime retains explicit unavailable AI coverage. P07 uses source-backed manual comparison and a different supervisor acknowledgement; no fabricated automated result is substituted.

## 5. Conventions & Guardrails

When creating, moving or renaming files, read `.cursor/rules/repository-structure.mdc`. It owns file placement, naming and migration safeguards. The FastAPI app, migrations, Python manifests and backend tests live under `apps/api/` (installed from `apps/api/src/sentinel`); browser acceptance is `tests/e2e/`; shared synthetic evidence is `tests/fixtures/`. `apps/web/` holds the Next.js app (routes in `src/app`, features in `src/features`, shared primitives in `src/components/ui`, infrastructure in `src/lib`). Relative `data/...` settings resolve against the workspace root (`WORKSPACE_ROOT`, else the repository root), so root and app-directory starts share one private data directory. Use `prompts/organize-repository.md` for the full reorganization procedure.

Use existing focused modules; introduce account, bundle/storage, review and report modules only as their tasks require. Server transactions own case revisions and completion. UI state cannot authorize operations. Original evidence and published review snapshots are immutable; decisions append events.

Synthetic patient records only. Keep the environment indication and export provenance. Credentials alone cannot enable remote calls; `NETWORK_MODE=online` is an explicit opt-in. Keep all core UI assets local and default server binding to loopback. Named authorization, encrypted credentials/secrets, bounded uploads and reliable coverage remain necessary even for an offline prototype.

Closeout re-verifies encrypted original hashes in the same transaction as the current-version guards/snapshot. Review actions and extraction confirmations append events and fence the current revision. Retired cases stay denied after restoration with the newest authenticated tombstone ledger.

Task verification:

```powershell
uv sync --project apps/api --locked
uv run --project apps/api --offline --locked pytest apps/api/tests/test_offline.py -q
pnpm --dir apps/web test
pnpm --dir apps/web typecheck
pnpm --dir apps/web lint
./scripts/verify.ps1
git diff --check
```

Run the task-specific tests in `tasks.md` when they exist. A passing legacy suite cannot establish role, OCR, report or UI features that have not been implemented. Full lint, real browser correction/restart and encrypted SQLite restore checks now exist. The PostgreSQL test explicitly skips without TEST_DATABASE_URL. CI is prepared but has not executed. See LOCAL-SETUP.md and the active verification record for the open runtime gates.

## 5.1 Change Workflow

The active product change is `docs/changes/hackathon-hosted-evaluation/` (hosted evaluation for the hackathon; tasks are sessions S1 to S21). `docs/changes/offline-prototype/` keeps the local gates; `docs/changes/repository-organization/` records the layout migration and `docs/changes/frontend-redesign/` the Next.js frontend. Neither closes the offline prototype's runtime gates. Keep proposal, design, tasks, delta spec and verification coherent. Validate using the external engine's `scripts/change.py validate <slug> docs/`. Archive only after the change is actually verified; uncompleted tasks remain unchecked.

## 5.2 Public Surface and Crawler Policy

The hosted evaluation site is public by design and holds synthetic records only. Local installs stay offline-first and bind to loopback. Hosted rules:

- HTTPS through Caddy on a DuckDNS name; uvicorn runs with `--proxy-headers`; the app trusts forwarded headers only from the proxy.
- The landing page at `/` is indexable. Every route behind sign-in sends a no-index directive (one Caddy line). A crawler directive is never an access-control mechanism; authorization stays in FastAPI.
- No CDN, analytics or runtime policy fetch. Outbound calls are limited to Token Factory and Tavily, both opt-in through `NETWORK_MODE=online` and keys.
- Keys live in git-ignored `.env` and `data/deploy/production.env`; never in chat, logs or commits.
- The site stays free and unrestricted until Dec 15; after submission it changes only for security and personal-data fixes.
- Seven release gates are listed in the change's tasks.md; none is claimed until `verify.md` records its evidence.

## 5.3 Engineering Maturity

L1 is required by multiple contributors; actual established practice is local verification, with no working CI/preview/deploy pipeline claimed until the CI run in S2 and the live check in S17 are recorded. The hosted build adds a nightly encrypted backup, a restore drill into an empty PostgreSQL and an uptime alert as release gates; they are designed, not rehearsed, until `verify.md` says so. Branches and local commits are not deployments.

## 6. Materialization

This guide is canonical for the root build instructions. Run the external engine's `scripts/materialize.py docs/` after editing; it preserves the root FMD pointer. The external engine path and owner restriction above must remain in the generated instructions. Do not create additional platform files unless needed.

## Self-Check

- [x] Read order, authorized scope, exact installed versions, commands and owner restrictions recorded.
- [x] Current test evidence is distinguished from future prototype acceptance.
- [ ] PostgreSQL/OCR packaging, CI, browser acceptance and restore rehearsal completed.
