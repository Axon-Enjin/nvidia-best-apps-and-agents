# Organize the Sentinel Claims repository

Act as a senior software engineer responsible for a maintainable repository containing a Next.js frontend and FastAPI backend. Reorganize this repository around clear ownership and predictable paths while preserving its working behavior, private data and reproducible verification.

Use `.cursor/rules/repository-structure.mdc` as the placement policy. Read root AGENTS.md, HANDOFF.md, docs/state.md and the active change's tasks.md and verify.md before planning any moves. Read the existing frontend redesign prompt, if available at `output/sentinel-claims-redesign-prompt.md`, so this work supports the intended Next.js App Router, React, strict TypeScript and Tailwind CSS frontend. FastAPI remains the backend.

This assignment is repository organization. Execute it in small, reviewable increments. Keep product behavior, database revision identities and the installed dependency versions stable except where packaging changes require an explicitly recorded adjustment. Verify each increment before continuing. Keep runtime checks that cannot execute visibly pending.

## Establish the current facts

Inventory tracked files, untracked user material, manifests, lockfiles, application entry points, tests, fixtures, scripts, CI, deployment configuration, documentation and generated artifacts. Use `git status --short`, `git ls-files` and focused `rg` searches. Do not read private credentials or source records to determine folder ownership.

At prompt creation, the application package is `sentinel/` at the root. Python configuration is in root `pyproject.toml` and `uv.lock`; Alembic is in root `migrations/` and `alembic.ini`. The static UI is in `sentinel/static/`, and Python/browser tests share root `tests/`. A Next.js application has been requested but has not been implemented. Recheck these facts before running the migration.

Several paths are coupled to the existing layout:

- `sentinel/config.py` resolves Alembic configuration and migration resources relative to its own file.
- `sentinel/api.py` serves package-local static assets.
- `scripts/install_ocr.py` resolves private OCR binaries under root `data/tools` and adjusts its import path.
- Tests resolve fixtures using parent directories and import shared helpers through `tests.*`.
- The disconnected browser test launches `tests.offline_server` as a real subprocess.
- Dockerfile, `.dockerignore`, Compose, CI and local scripts assume root Python/application paths.
- `.gitattributes` preserves exact fixture bytes, including CRLF in hashed source manifests.

Identify additional dependencies from the actual files. Produce an old-path to new-path map before moving them. Include the command, import, resource lookup or document link affected by each group of moves. Explicitly list root files that remain because tools or documentation materialization expect them there.

## Use this target layout

The following tree describes ownership. Create a directory only when actual files belong in it.

```text
apps/
  web/
    src/
      app/                 # Next.js routes and route composition
      features/            # Auth, claims and review modules as needed
      components/ui/       # Genuinely shared UI primitives
      lib/                 # Typed API transport and server/client infrastructure
    public/                # Public brand/UI assets only
    tests/                 # App-level frontend tests
    package.json
    pnpm-lock.yaml         # One app-local JS lockfile; retain another manager if established
    next.config.ts
    tsconfig.json
    postcss.config.mjs
  api/
    src/sentinel/          # Preserve the Python package name
    migrations/            # Preserve existing Alembic history
    tests/                 # Backend unit/integration tests and owned helpers
    scripts/               # API-only maintenance/install commands
    pyproject.toml
    uv.lock
    alembic.ini
    Dockerfile
tests/
  e2e/                     # Cross-app browser/workflow acceptance
  fixtures/                # Shared synthetic fixtures and locked manifests
scripts/                   # Cross-app startup and verification commands
infra/                     # Shared deployment configuration when needed
docs/                      # Existing canonical docs and change records
prompts/                   # Reusable engineering/design prompts
.cursor/rules/             # Persistent project rules
.github/workflows/         # CI
compose.yaml               # Local multi-service entry point
data/                      # Ignored private runtime state; preserve in place
output/                    # Generated outputs; preserve existing user material
```

Keep required root entry points such as README.md, LICENSE, AGENTS.md, CLAUDE.md, HANDOFF.md, PRODUCT.md and materialized brand/design guides at their required locations. Keep repository-wide ignores and attributes at the root. The tree is a target, not a claim that every app or tool already exists.

Each app owns its dependency manifest and lockfile. Default to independent app projects; add a JavaScript workspace only when real shared packages or tooling justify one. If a package manager or workspace has already been introduced, preserve it rather than producing competing lockfiles. A Python app does not need a package.json merely because it lives under apps/.

## Execute the migration

1. **Establish a baseline.** Run the current documented lint/tests and relevant setup checks. Record actual results, including unavailable runtime gates. Capture the tracked fixture and dependency state so later changes can be assessed. Identify any active local server using paths that will move; stop only task-owned processes that require it.

2. **Record the structural change.** Follow the project's FMD change workflow. Use a focused change record/task list for the migration rather than silently rewriting completed offline-prototype evidence. Propagate changes to canonical build/architecture guidance where needed. The external documentation engine is read-only; run its scripts against this project's docs with `PYTHONDONTWRITEBYTECODE=1`. Preserve user-owned untracked research and historical plans.

3. **Move and package the backend.** Move `sentinel/` to `apps/api/src/sentinel/`, and its owned configuration/migrations/tests into `apps/api/`. Retain the `sentinel` import name and executable CLI behavior. Configure an explicit build backend and package discovery so the src layout installs correctly through uv. Include required package assets and make Alembic resources available in both development and the deployed image. Preserve existing dependency resolutions; record packaging-specific lock changes separately from dependency upgrades. Verify imports from outside the source directory so repository-root imports cannot conceal a broken package.

4. **Separate test ownership.** Place backend tests and their helpers with the API, frontend tests with the web app, and full browser acceptance under `tests/e2e/`. Keep shared synthetic evidence at `tests/fixtures/` with one authoritative copy. Update fixture lookup, helper imports, subprocess module names and pytest discovery together. Resolve `tests` package collisions explicitly instead of making success depend on import order or global PYTHONPATH changes. Preserve locked fixture bytes, hashes and Alembic revision IDs. Test collection and scenario coverage must remain accounted for after the move.

5. **Establish the frontend boundary.** Put the Next.js application under `apps/web/` when it is created or migrate an existing frontend there. Keep route files thin; feature components, state, hooks and types live with their owning feature. Reserve `components/ui` for shared primitives and `lib` for focused infrastructure. Keep server-only session/API code out of browser imports. If frontend implementation has not begun, record this target without creating empty app scaffolding or rewriting the static UI. Keep the current static surface packaged with the API until the separate frontend migration verifies parity.

6. **Update operational paths.** Update CI working directories, lint/test discovery, Docker COPY/build paths, `.dockerignore`, Compose configuration, local scripts and command examples. Keep a small documented root entry point for cross-app development and verification. Preserve private data, OCR binaries, account keys, recovery keys, originals and backups under their existing stable locations. Review how working directories affect relative settings; selecting a project with `uv run --project` must not accidentally select a different runtime data directory. Root startup and app-directory startup should resolve the documented same state or require an explicit data-root setting. Do not move live databases or regenerate keys as part of this task.

7. **Organize supporting files deliberately.** Place new reusable prompts under `prompts/`. Keep app-only scripts with their app and cross-app commands under root `scripts/`. Relocate tracked supporting notes only after checking references and the documentation engine's expected paths. Preserve existing untracked `output/`, research, walkthroughs and historical plans. Generated screenshots, caches, local tools and build outputs stay outside application source and out of commits; runtime and build-directory ignore patterns must cover their new locations.

8. **Reconcile and verify.** Update README/local setup, HANDOFF, canonical build guidance and affected documentation links with the actual new commands. Re-run materialization for generated root guides. Keep the persistent structure rule aligned with the executed layout and remove its transitional wording only after the migration passes verification. Record the resulting tree and exact migration evidence in the active migration's verification record.

## Keep boundaries small

Preserve focused Python modules during the move. A folder reorganization alone does not justify new controller/service/repository layers, microservices, domain packages or parallel API implementations. Add shared packages only after actual consumers require them. Keep helpers with their feature until real reuse exists. Keep domain logic in the authoritative FastAPI backend rather than duplicating completion or authorization rules in TypeScript.

Use descriptive filenames and exports according to the structure rule. Retain framework-required filenames, published import paths, canonical/generated document names and fixture names. Prefer a real move, preserving history, over copying application code into a second authoritative location. Remove an obsolete duplicate only after verifying its replacement and accounting for every consumer.

## Completion evidence

Verify installed Python imports and CLI entry points, fresh database migrations, fixture hashes, offline provider guards, role/assignment checks, correction and manual-review flows, report exports, OCR resource lookup, recovery/restore and browser restart persistence. Run affected tests followed by the available full suite. Run the real PostgreSQL checks when a disposable database is available; retain explicit skips otherwise.

If the Next.js frontend exists, run its frozen-lockfile install, type checking, lint, production build and applicable browser tests. If it does not exist, report those checks as not applicable to this organization task. Validate updated Compose/build configuration and execute available runtime checks; configuration parsing alone is not an image or database test.

Use the external FMD validation/materialization scripts for affected documentation. Run `git diff --check`, inspect renamed/deleted files, and compare collected scenarios and fixture hashes with the baseline. Report any unavailable PostgreSQL, container, CI or hosted checks accurately. Do not close the existing offline prototype's unrelated acceptance gates as a side effect of this work.

Deliver the actual resulting tree, a concise move map, updated reproducible commands, the persistent rule and executed verification results. A tree diagram alone does not complete this migration. Commit reviewable increments in this project repository without pushing or provisioning paid services.

## Primary references

These document framework/tool behavior; the two-app layout and ownership boundaries above are project choices.

- [Next.js project structure and organization](https://nextjs.org/docs/app/getting-started/project-structure)
- [Python Packaging: src layout versus flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [uv project configuration and packaging](https://docs.astral.sh/uv/concepts/projects/config/)
