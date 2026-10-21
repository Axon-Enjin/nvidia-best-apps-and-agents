# Repository Organization Tasks

> Execute inline in small increments. Verify each before the next. Evidence belongs in [verify.md](verify.md). Procedure: `prompts/organize-repository.md`.

## Task 1: Baseline and change record

- [x] 1.1 Record the pre-move facts: tracked file inventory, collected test IDs (169), fixture SHA-256 list (518 files), `uv.lock` digest, lint and full-suite results with skips.
- [x] 1.2 Write this change record and validate it with the external engine's `scripts/change.py`.

## Task 2: Move and package the backend

- [x] 2.1 `git mv` `sentinel/` to `apps/api/src/sentinel/`, `migrations/`, `alembic.ini`, `pyproject.toml`, `uv.lock` and `scripts/install_ocr.py` into `apps/api/`; backend tests to `apps/api/tests/`.
- [x] 2.2 Add the Hatchling build backend, package discovery and Alembic force-include; make `config.py` resolve packaged or source-tree migrations.
- [x] 2.3 Make data-root resolution independent of the working directory; fix `install_ocr.py` and the OCR fallback path.
- [x] 2.4 Record the lock change as packaging only. Confirm no dependency version differs.
- [x] 2.5 Verify: ruff, full API suite with the same collected IDs, wheel import and `migrate` from outside the source tree.

## Task 3: Separate test ownership

- [x] 3.1 Move browser tests, their conftest and the acceptance server to `tests/e2e/` as the `e2e` package; launch the server by file path.
- [x] 3.2 Point API and e2e fixture lookup at the single `tests/fixtures/` copy.
- [x] 3.3 Verify: both sessions collect, the union equals the baseline IDs, fixture hashes are identical.

## Task 4: Operational paths

- [x] 4.1 Dockerfile to `apps/api/`, root-context build, non-editable install; update `.dockerignore`, `compose.yaml`, `.github/workflows/ci.yml`, `.env.example`, `scripts/local.ps1`.
- [x] 4.2 Verify: Compose configuration parses, the Dockerfile install sequence works in a clean copy, CI commands run locally.

## Task 5: Reconcile documentation and rule

- [x] 5.1 Update README, LOCAL-SETUP, HANDOFF, `docs/build-sentinel-node.md`, `docs/state.md`, OCR-NOTICES; re-run `materialize.py`.
- [x] 5.2 Align `.cursor/rules/repository-structure.mdc` with the executed layout; remove transitional wording.
- [x] 5.3 Record the resulting tree, move map and evidence in `verify.md`; run engine validation, `git diff --check` and final comparison against the baseline.
