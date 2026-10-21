# Proposal: Repository organization

**Project:** Sentinel Claims
**Date:** 2026-10-22
**Status:** In Progress
**Owner:** Yushin

## Intent

Give the repository clear ownership and predictable paths before the Next.js frontend begins: one FastAPI application under `apps/api/`, a reserved home for `apps/web/`, cross-app acceptance under `tests/e2e/`, and shared synthetic evidence at `tests/fixtures/`.

## Scope

- Move the Python package, migrations, Python manifests, backend tests, API-only scripts and the application Dockerfile under `apps/api/`, preserving history with real moves.
- Keep the `sentinel` import name, CLI behavior, Alembic revision identities, locked dependency versions, fixture bytes and private data paths.
- Separate test ownership: backend tests with the API, browser acceptance in `tests/e2e/`, one authoritative fixture copy at `tests/fixtures/`.
- Update CI, Docker, Compose, local scripts and documentation in the same slices as the moves.
- Record the `apps/web/` boundary without creating empty scaffolding or rewriting the static UI. The static surface stays packaged with the API until the separate frontend migration verifies parity.

## Out of scope

Product behavior, schema changes, dependency upgrades, a JavaScript workspace, new service layers, moving live databases, regenerating keys, pushing, paid services, and closing the offline prototype's open runtime gates (Tasks 9.4, 10.3 and 10.4).

## Approach

The procedure is `prompts/organize-repository.md`; placement policy is `.cursor/rules/repository-structure.mdc`. Work in small increments, each verified before the next: record the change, move and package the backend, split test ownership, update operational paths, then reconcile documentation and the persistent rule. The historical offline-prototype change records keep their original paths as evidence of what was true when written.
