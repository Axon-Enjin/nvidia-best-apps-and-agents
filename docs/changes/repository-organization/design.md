# Design: Repository organization

**Date:** 2026-10-22
**Status:** Draft

## Technical approach

Target tree and ownership live in `.cursor/rules/repository-structure.mdc`; the executed tree and move map are recorded in [verify.md](verify.md). This design records the decisions that the moves force.

**Packaging.** `apps/api/pyproject.toml` gains an explicit Hatchling build backend with `src/sentinel` as the wheel package. Alembic resources keep one authoritative copy at `apps/api/migrations` and `apps/api/alembic.ini`; the wheel force-includes them under `sentinel/_alembic/`. `sentinel.config` resolves the packaged copy when present and the source-tree copy otherwise, so development, installed wheels and the image use the same code path. `alembic.ini` uses `%(here)s` so it no longer depends on the working directory.

**Data root.** Relative `data/...` defaults and relative settings resolve against a workspace root that does not depend on the working directory: the `WORKSPACE_ROOT` environment variable, else the repository root when running from a source checkout, else the current directory (installed or container use, where paths are absolute). Starting the API from the repository root or from `apps/api/` therefore selects the same private `data/` state. Absolute settings are untouched.

**Tests.** Backend tests keep the `tests` package under `apps/api/` with an explicit `pythonpath`. Browser acceptance is the `e2e` package under `tests/e2e/` with its own `pytest.ini`; the two suites run as separate pytest sessions so the names cannot collide. The acceptance server is launched by file path, not by module name. E2E tests run in the API project's environment because they drive the real FastAPI package and Playwright; a future web app adds its own lockfile without changing that.

**Container.** The API Dockerfile lives in `apps/api/` and builds from the repository root context so root `LICENSE` and `OCR-NOTICES.md` are available. It installs a non-editable wheel, which makes the image exercise the packaged resources.

## Risks

- Hatchling is a build-time download. A cold offline machine needs it cached; recorded in verify.md.
- The container image cannot be built on this host (no Docker engine). The Dockerfile install sequence is reproduced locally with `uv sync --no-editable` and verified from outside the source tree; the image build stays pending.
- Moving files while tests run corrupts a run. Each increment is verified against a quiescent tree.
