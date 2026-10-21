# Delta for Review Workspace

**Project:** Sentinel Claims
**Version:** 0.1
**Status:** Draft
**Last reconciled:** 2026-10-22

## ADDED Requirements

### Requirement: Named sign-in through the web origin

The web application SHALL sign reviewers in through the same-origin API boundary, keep the session in the HttpOnly SameSite=Strict cookie, require an authenticator code for privileged accounts, and return only to in-app paths after sign-in.

#### Scenario: Supervisor signs in
- GIVEN a supervisor account with local TOTP enrollment
- WHEN the supervisor submits a correct password without a code
- THEN sign-in fails with "Sign-in failed." and the entered password remains
- AND with a valid code the supervisor reaches the claims queue

#### Scenario: Unsafe return path
- GIVEN the sign-in URL carries `next=//evil.example`
- WHEN sign-in succeeds
- THEN the browser opens `/claims`

### Requirement: Same-origin API boundary

The web application SHALL forward API requests to the review service with the cookie, CSRF token, Origin, upload body and download headers intact, SHALL mark every proxied response `Cache-Control: no-store`, and the review service SHALL accept changes only from its own origin or a configured trusted origin.

#### Scenario: Large original
- GIVEN a 12 MiB original named in a manifest with its SHA-256
- WHEN it is uploaded through the web origin
- THEN the version is accepted and the stored byte count equals the original

#### Scenario: Foreign origin
- GIVEN a signed-in session
- WHEN a change request carries Origin `http://evil.example`
- THEN the review service answers 403 "Cross-origin changes are not allowed."

### Requirement: Claims queue with URL state

The queue SHALL keep its view, search and page in the URL, show the status of each claim in text, preserve the last opened claim when the reviewer returns, and explain the next action when empty.

#### Scenario: Return from a claim
- GIVEN the reviewer filtered the queue to "Needs review" and searched "SYN"
- WHEN the reviewer opens a claim and returns through the wordmark
- THEN the same filter and search are applied and the opened claim is marked current

### Requirement: Resume where action is needed

Opening a claim SHALL lead to Import when no current version exists, checks are processing or scan values await confirmation; to Complete when completion is allowed or done; and otherwise to Review. Old `/#case=<id>` links SHALL open the claim.

#### Scenario: Returning reviewer
- GIVEN a claim whose current version is processed and has open discrepancies
- WHEN the reviewer opens `/claims/<id>`
- THEN the Review phase opens

### Requirement: Intake shows each declared document

Intake SHALL list every document named in the manifest with Selected, Missing, SHA-256 mismatch, duplicate or not-in-manifest status, SHALL keep import unavailable with an explanation until every named document matches, and SHALL reuse the created case and idempotency key when an upload is retried.

#### Scenario: Wrong file content
- GIVEN a manifest naming `cf2.txt` with a SHA-256
- WHEN the reviewer selects a different file named `cf2.txt`
- THEN its row reads "Does not match the manifest's SHA-256" and import stays unavailable

#### Scenario: Retry after a failed upload
- GIVEN the first upload attempt fails after the case was created
- WHEN the reviewer retries
- THEN one case with one version exists

### Requirement: Document states stay distinct

The Import phase SHALL show readable, scan-awaiting-confirmation, unreadable, unsupported, identity-mismatch and internally conflicting documents with distinct text, and SHALL show real processing states without percentages.

#### Scenario: Unreadable and unsupported
- GIVEN a version with an unreadable scan and an unsupported attachment
- WHEN processing completes
- THEN their rows read "Unreadable" and "Unsupported format"

### Requirement: Scan confirmation beside the original

Each printed-scan value SHALL be confirmed one field at a time beside the original image, with a page, a reason and an explicit statement that the source is legible. Unconfirmed readings SHALL NOT appear as evidence or differing values.

#### Scenario: Unconfirmed scan in review
- GIVEN a CF2 scan with unconfirmed values
- WHEN the reviewer opens an issue that cites the CF2
- THEN its panel says the scan needs confirmation and highlights no values

### Requirement: Review shows exact differences beside the source

Review SHALL list unresolved checks first with plain labels and secondary check IDs, keep passed checks behind a labelled disclosure, and for a selected issue show each differing value with its document, page and version, the reasons it blocks completion, the source text with the value highlighted, and one primary next action. Opening a source SHALL record no review event.

#### Scenario: Discharge date discrepancy
- GIVEN the CF2 claim summary says 2026-10-14 and the discharge summary says 2026-10-15
- WHEN the reviewer selects "Dates and discharge status"
- THEN both values appear with "page 1 · version 1" and the same letter marks the discharge value in the table and in the source text

### Requirement: Correction progress uses real events

A correction request SHALL require a reason, responsible department and person, and evidence. Its progress SHALL offer only the next valid step (handoff, acknowledgement, corrected import, resolution after recheck) and a reasoned cancellation, each recorded as its own event.

#### Scenario: Corrected version
- GIVEN an acknowledged correction for P05
- WHEN a corrected version is imported and P05 passes
- THEN "Resolve after recheck" becomes available and its use records a resolution event

### Requirement: Manual review and separate acknowledgement

P07 SHALL require a named source-backed manual comparison and an acknowledgement by a different supervisor; P08 SHALL require a presence review backed by sources with actual marks, printed names and dates. The interface SHALL show who must act next.

#### Scenario: Same supervisor
- GIVEN a supervisor recorded the P07 comparison
- WHEN the same supervisor views P07
- THEN acknowledgement is not offered and the page says a different supervisor must acknowledge

### Requirement: Drafts survive expiry and conflicts

Unsaved input SHALL remain when a save fails for an expired session, a stale revision or validation, SHALL never be resubmitted automatically, and leaving a page with unsaved input SHALL ask for confirmation. A repeated activation of a save button SHALL record one event.

#### Scenario: Session expires mid-edit
- GIVEN a reviewer filled a correction request
- WHEN the session has expired and the reviewer saves
- THEN a sign-in dialog opens, nothing is saved, and after signing in the draft is intact until the reviewer saves again

### Requirement: Guarded completion and records

Complete SHALL show the claim, current version, rule version, coverage, named responsibility and exact remaining blockers; SHALL enable completion only when the review service allows it; SHALL show "Ready for final submission review" after completion; and SHALL offer CSV and printable records for the current snapshot while keeping stale records inspectable.

#### Scenario: Later change
- GIVEN a completed review
- WHEN checks are re-run on the current version
- THEN the earlier record reads "Stale after later changes" and remains inspectable

### Requirement: Offline, accessible delivery

The web application SHALL serve every script, style, icon and font itself, make no runtime request beyond loopback, meet WCAG AA text contrast, keep focus visible and unobscured, work by keyboard alone, fit 375 px and 200 percent zoom without horizontal scrolling, give status meaning in text, and remove transitions under reduced motion.

#### Scenario: Narrow screen
- GIVEN a 375 px wide viewport
- WHEN the reviewer opens a discrepancy
- THEN the page has no horizontal scroll and "View source" moves focus to the source evidence
