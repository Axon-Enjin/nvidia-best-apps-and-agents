# Verify: Repository organization

**Date:** 2026-10-22
**Overall:** PENDING

PENDING means the migration is in progress. Sections below record only commands that actually ran.

## Completeness

- BASELINE (commit `8579db8`, branch `feat/offline-prototype`, before any move): 631 tracked files; 518 under `tests/fixtures/`.
- BASELINE: `uv sync --locked` succeeded with uv 0.11.19 and Python 3.14.5; `uv.lock` SHA-256 `9d59f058cbdcdbed6169a6ef370a831d886fc58e68852bfc93670e25d67beada`.
- BASELINE: `uv run --offline --locked ruff check sentinel tests migrations scripts`: all checks passed.
- BASELINE: `uv run --offline --locked pytest -q -rs`: 168 passed, 1 skipped, 1 warning in 208.71 s. The skip is `tests/test_postgres.py` (no `TEST_DATABASE_URL`). The warning is the known Starlette/HTTPX deprecation.
- BASELINE: `pytest --collect-only` lists 169 test IDs (sorted-list digest `01ada0b792b0d2c7`). Fixture manifest (`sha256sum` of all 518 files, digest `9b5ad5235df24cbc`).
- UNAVAILABLE on this host: Docker engine, WSL, Podman, PostgreSQL. These offline-prototype gates (9.4, 10.3, 10.4) stay open and are not closed by this change.

## Correctness

Pending.

## Coherence

Pending.
