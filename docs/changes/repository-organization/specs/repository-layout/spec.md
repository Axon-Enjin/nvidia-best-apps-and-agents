# Delta for Repository Layout

**Project:** Sentinel Claims
**Version:** 0.1
**Status:** Draft
**Last reconciled:** 2026-10-22

## ADDED Requirements

### Requirement: Single ownership per path

The repository SHALL place each file in the directory of the one app, shared test area or tool that owns it, and SHALL keep one authoritative copy of every fixture and migration.

#### Scenario: Backend runs from an installed package
- GIVEN the API package built from `apps/api/`
- WHEN it is installed into a clean environment and imported from outside the source tree
- THEN `sentinel` imports, its CLI starts and migrations apply to a fresh database
- AND static assets are served from the installed package

#### Scenario: Fixtures are unchanged
- GIVEN the tracked fixtures before the move
- WHEN the move completes
- THEN every fixture file has the same SHA-256 digest at the same path under `tests/fixtures/`

### Requirement: Working-directory independent data

The application SHALL select the same private data directory whether started from the repository root or an app directory, unless a workspace root is set explicitly.

#### Scenario: App directory start
- GIVEN the default settings and no workspace override
- WHEN the settings are loaded with the working directory set to `apps/api/`
- THEN the database, key file and source storage paths resolve under the repository's `data/` directory
