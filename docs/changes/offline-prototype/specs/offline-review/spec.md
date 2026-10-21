# Delta for Offline Review

**Project:** Sentinel Claims
**Version:** 0.1
**Status:** Draft
**Last reconciled:** 2026-10-21
**PRD links:** PRD-F1, PRD-F2, PRD-F3, PRD-F4, PRD-F5, PRD-F6

## ADDED Requirements

### Requirement: Offline by default

The system SHALL disable remote inference by default, even when provider credentials are present.

#### Scenario: Credentials do not override offline operation
- GIVEN a configured provider credential and offline operation
- WHEN a reviewer requests remote analysis
- THEN the request is rejected before enqueue or network transmission
- AND local deterministic review remains available

#### Scenario: Pending remote work after disconnect
- GIVEN a remote-review job queued before switching offline
- WHEN a worker processes it offline
- THEN local results are retained without a provider call
- AND remote coverage remains explicitly not run and incomplete

### Requirement: Named local responsibility

The system SHALL authenticate named users locally and enforce reviewer assignment and supervisor/admin responsibilities without an external identity service.

#### Scenario: Direct document access is checked
- GIVEN a reviewer assigned to one case
- WHEN requesting another reviewer's source, job or report
- THEN the server denies access
- AND administrator status alone grants no clinical review permission

### Requirement: Immutable local bundle evidence

The system SHALL preserve original source bytes and versioned membership for every imported case revision.

#### Scenario: Corrected bundle retains prior evidence
- GIVEN an imported case with a reviewed discrepancy
- WHEN corrected sources are imported
- THEN a new bundle version is created
- AND the old source, finding and reviewer history remain inspectable

### Requirement: Honest offline coverage

The system SHALL distinguish deterministic checks, manual review, unsupported content and unavailable AI under the accepted P01-P10 profile.

#### Scenario: Manual narrative comparison
- GIVEN remote inference is unavailable
- WHEN the reviewer records source-backed manual P07 comparison and a supervisor acknowledges it
- THEN the manual requirement can be resolved
- AND the AI result remains not run or failed rather than completed

### Requirement: Correction workflow persistence

The system SHALL retain reasoned dispositions, correction responsibility, handoff, acknowledgement and resolution across refresh and restart.

#### Scenario: Stale decision cannot overwrite a revision
- GIVEN a reviewer editing an earlier case revision
- WHEN a newer source or decision revision exists
- THEN the stale write is rejected with a refresh path
- AND committed history is preserved

### Requirement: Guarded local completion and exports

The system SHALL complete and export an internal review only for the current resolved bundle and rule version.

#### Scenario: Unresolved requirements block completion
- GIVEN a missing required artifact, unresolved finding, open task or stale source/rule version
- WHEN a reviewer requests completion
- THEN completion is denied with the specific blockers

#### Scenario: Download identifies its evidence version
- GIVEN a completed current review
- WHEN exporting CSV or a printable report
- THEN the export includes source/rule versions, actor, coverage and sample provenance
- AND a later revision marks that report stale in the workspace

### Requirement: Printed scans remain local

The system SHALL process supported printed scans locally and require source confirmation for uncertain critical values.

#### Scenario: Unreadable source cannot clear a check
- GIVEN a scan with unreadable required content
- WHEN extraction cannot establish a reliable value
- THEN the required check remains incomplete with a manual/source replacement path
- AND no external OCR request is made

### Requirement: Recoverable disconnected operation

The system SHALL retain case evidence, review history and permissions through local restart and verified backup restoration without external services.

#### Scenario: Complete a disconnected correction loop
- GIVEN dependencies and local assets are installed and external traffic is blocked
- WHEN users import, review, request correction, reimport, finalize, export, restart and reopen the case
- THEN every supported action completes locally
- AND history and document hashes are preserved without fabricated model output
