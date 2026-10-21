# Verify: Repository organization

**Date:** 2026-10-22
**Overall:** PASS WITH OPEN RUNTIME GATES

The layout migration is executed and verified on this host. PASS WITH OPEN RUNTIME GATES means every check that can run here passed; container, PostgreSQL and hosted-CI checks are unavailable here and stay open, as they were before this change. The offline prototype's Tasks 9.4, 10.3 and 10.4 are not closed by this change.

## Completeness

- BASELINE (commit `8579db8`, before any move): 631 tracked files, 518 under `tests/fixtures/`. `uv sync --locked` passed (uv 0.11.19, Python 3.14.5). Ruff passed. `pytest -q -rs`: 168 passed, 1 skipped, 1 warning in 208.71 s; 169 test IDs collected. The skip is `tests/test_postgres.py` (no `TEST_DATABASE_URL`).
- PASS: all tasks 1 to 5 in [tasks.md](tasks.md) are done in the commits listed below.
- PASS: no tracked file was deleted. `git diff -M --name-status 8579db8 HEAD` shows renames (53 identical, the rest 62 to 99 percent similar), additions and modifications only.
- NOT APPLICABLE: the Next.js app does not exist, so frozen-lockfile install, type checking, lint, production build and web browser tests were not run. `apps/web/` is not created and the static UI is untouched.
- OPEN: container image build and start, PostgreSQL workflow and restore, Linux container OCR, OS or container egress isolation and a hosted CI run. This host has no Docker engine, WSL, Podman or PostgreSQL.

### Commits

| Commit | Content |
|---|---|
| `251d2e4` | Change record and baseline |
| `fa025ff` | Backend, migrations, manifests, backend tests, Dockerfile, Compose, CI and setup commands moved to `apps/api` |
| `66bb9e0` | Browser acceptance moved to `tests/e2e` |
| `52c7086` | Root `scripts/verify.ps1`, CI browser step |
| this record | README, HANDOFF, build guide, state, placement rule, `.gitignore`, evidence |

### Resulting tracked tree (644 files)

```text
apps/
  api/
    src/sentinel/        # 23 modules + static/ (8 UI assets)
    migrations/          # env.py + versions/0001..0007
    tests/               # 15 test modules + 5 helper files, package "tests"
    scripts/install_ocr.py
    pyproject.toml  uv.lock  alembic.ini  Dockerfile
tests/
  e2e/                   # 5 browser tests, conftest, offline_server.py, package "e2e"
  fixtures/              # 518 files, unchanged
scripts/                 # local.ps1, verify.ps1
prompts/organize-repository.md
docs/  .cursor/rules/  .github/workflows/ci.yml
compose.yaml  .dockerignore  .gitignore  .gitattributes  .env.example
README.md  AGENTS.md  CLAUDE.md  HANDOFF.md  PRODUCT.md  BRAND.md  DESIGN.md  LICENSE
LOCAL-SETUP.md  OCR-NOTICES.md  BUILD-CHECKLIST.md  HACKATHON.md  ORG.md  PROMPT.md
PILOT-DECISIONS.md  PILOT-WORKFLOW-RESEARCH.md  Hackathon-AI-Agent-Research.md
data/ (ignored)  output/ (untracked, preserved)
```

### Move map

| Old path | New path | Affected consumers |
|---|---|---|
| `sentinel/` | `apps/api/src/sentinel/` | imports unchanged (`sentinel`); wheel package discovery; Dockerfile COPY; ruff per-file ignore |
| `sentinel/static/` | `apps/api/src/sentinel/static/` | `api.py` mounts `Path(__file__).parent / "static"`; packaged in the wheel |
| `migrations/`, `alembic.ini` | `apps/api/migrations/`, `apps/api/alembic.ini` | `config.alembic_resources()`; wheel force-include as `sentinel/_alembic/`; `script_location = %(here)s/migrations`; `test_accounts` |
| `pyproject.toml`, `uv.lock` | `apps/api/pyproject.toml`, `apps/api/uv.lock` | every `uv` command uses `--project apps/api`; build backend added |
| `scripts/install_ocr.py` | `apps/api/scripts/install_ocr.py` | imports the installed `sentinel`; data root from `workspace_root()`; OCR-NOTICES and LOCAL-SETUP commands |
| `Dockerfile` | `apps/api/Dockerfile` | `compose.yaml` build context `.` with `dockerfile: apps/api/Dockerfile`; `.dockerignore` allow-list |
| `tests/test_*.py`, `tests/*_helpers.py`, `tests/__init__.py` | `apps/api/tests/` | pytest config in `apps/api/pyproject.toml`; `tests.*` imports unchanged |
| `tests/browser/*`, `tests/offline_server.py` | `tests/e2e/` | package `e2e`; own `pytest.ini` and `ruff.toml`; server launched by file path, not `-m tests.offline_server` |
| `tests/fixtures/` | `tests/fixtures/` (unchanged) | `apps/api/tests/fixture_paths.py`, `tests/e2e/fixture_paths.py`; `.gitattributes` rule still matches |
| (new) | `apps/api/tests/test_layout.py` | six tests for the data root and migration resources |
| (new) | `scripts/verify.ps1` | lint, API tests and browser acceptance from the repository root |

### Root files that remain, and why

`README.md`, `LICENSE`, `AGENTS.md`, `CLAUDE.md`, `HANDOFF.md`, `PRODUCT.md`, `BRAND.md`, `DESIGN.md` (entry points and materialized guides); `compose.yaml`, `.dockerignore`, `.gitignore`, `.gitattributes`, `.env.example` (repository-wide tooling); `LOCAL-SETUP.md` (setup entry point, referenced by README); `OCR-NOTICES.md` (copied into the image from the root context). `BUILD-CHECKLIST.md`, `HACKATHON.md`, `ORG.md`, `PROMPT.md`, `PILOT-*.md` and `Hackathon-AI-Agent-Research.md` stay in place: README links to them, and relocating `BUILD-CHECKLIST.md` into `docs/` was tried in a scratch copy and produced 17 new voice and trace failures in the FMD check, so it needs a content rewrite, not a move. Its existing "not inside a docs/ folder" finding is unchanged from the baseline.

## Correctness

- PASS: `uv lock --offline` changed one line of `apps/api/uv.lock`: the project source `virtual = "."` became `editable = "."`. No dependency version changed. This is the packaging-only lock change and is separate from any upgrade.
- PASS: collected tests. API session 170 + e2e session 5 = 175. Every baseline ID is present (`tests/browser/...` is now `tests/e2e/...`); the six additions are `apps/api/tests/test_layout.py`.
- PASS: `./scripts/verify.ps1` from the repository root: sync, Ruff over API and `tests/e2e`, API tests 169 passed and 1 skipped (PostgreSQL), browser acceptance 5 passed. Total 174 passed, 1 skipped, matching the baseline's 168 passed, 1 skipped plus six new tests.
- PASS: fixture integrity. `sha256sum` of all 518 files under `tests/fixtures/` is identical to the baseline list.
- PASS: Alembic revision identities `0001` to `0007` are unchanged (checked by `test_layout.py` and by a fresh migration to `0007`).
- PASS: installed-package check. A wheel built with `uv build --wheel` holds 43 files, including 7 migration revisions and 8 static assets. Installed with the locked runtime dependencies into a clean virtual environment and run with `python -I` from an unrelated directory: `sentinel` imports from `site-packages`; `alembic_resources()` returns the packaged copy; a fresh SQLite database migrates 0001 to 0007 (13 tables); `/static/app.js`, `app.css`, `login.js` and `index.html` return 200; `python -m sentinel --help` lists the CLI.
- PASS: Dockerfile install sequence rehearsal. In a copy holding only the files `.dockerignore` allows, `uv sync --locked --no-dev --no-install-project` then `uv sync --locked --no-dev --no-editable` install a non-editable wheel; `python -I` from `/` imports it from `site-packages`; `python -m sentinel migrate` reaches 0007. This is not an image build.
- PASS: data root. `Settings.from_env()` run from the repository root and from `apps/api/` resolves the database, key and source storage to the same `data/` directory; `WORKSPACE_ROOT` overrides it. Covered by `test_layout.py`.
- PASS: official Compose 5.6.1 `config --quiet` accepts the updated `compose.yaml`; the resolved build is context `.` and `apps/api/Dockerfile`. Configuration parsing is not an image or database test.
- PASS: offline provider guards, role and assignment checks, correction and manual-review flows, report exports, OCR lookup, recovery and restore, and browser restart persistence run inside the suites above (`test_offline`, `test_accounts`, `test_corrections`, `test_closeout`, `test_local_ocr`, `test_recovery`, `tests/e2e/test_offline_acceptance.py`).
- PASS: `git diff --check` is clean.
- OBSERVED, NOT REPRODUCED: during the first full API run after the backend move, `tests/browser/test_offline_acceptance.py` timed out waiting for the P07 button after the server restart step, while a wheel build and package installs ran concurrently. It passed alone, in the next full run, and again in the final run. The concurrent CPU and disk load is the likely cause; no code path involved in that step changed. Treat as a watch item.

## Coherence

- PASS: `change.py validate` reports 0 failures and 0 warnings for both changes; `change.py verify repository-organization` passes the structure check.
- PASS: `materialize.py docs/` regenerated `AGENTS.md` from `docs/build-sentinel-node.md` (the FMD pointer line is preserved; BRAND.md and DESIGN.md are unchanged). Engine scripts ran with `PYTHONDONTWRITEBYTECODE=1`; the engine repository was not modified.
- PASS: `check.py` on the tracked tree gives the same single finding before and after (`BUILD-CHECKLIST.md` outside `docs/`); the untracked research and walkthrough files were not part of the tracked snapshot and are untouched.
- PASS: `.cursor/rules/repository-structure.mdc` now states the executed layout; its transitional wording is removed. `prompts/organize-repository.md` is unchanged because it is the reusable procedure.
- PASS: `output/`, `docs/sentinel-node-claims-interoperability-research.md`, `docs/sentinel-node-walkthrough.html` and `docs/superpowers/` are untracked and untouched. `data/` was not modified: no database moved, no key regenerated.
- NOTE: a preview server started in an earlier session (`tests.offline_server` on port 8000, using the old root `.venv`) is still running. It is not owned by this task and was left alone. It serves `/static` from the old `sentinel/static` path, which no longer exists, so restart it from `apps/api` when the preview is needed again. The old root `.venv` is now unused and ignored.
- NOTE: the historical `docs/changes/offline-prototype/` records, `BUILD-CHECKLIST.md` and `prompts/organize-repository.md` keep the paths that were true when they were written.

## Known limits

- Hatchling is downloaded at first build. A cold offline machine needs it in the uv cache; it was cached here by the first online build.
- The image has not been built, so the Dockerfile's `apt-get` and tessdata steps are unchanged but unexercised on this host.
- CI was edited but has not executed.
