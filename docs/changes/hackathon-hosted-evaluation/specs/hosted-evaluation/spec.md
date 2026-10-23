# Delta for Hosted Evaluation

**Project:** Sentinel Claims
**Version:** 0.1
**Status:** Draft
**Last reconciled:** 2026-10-23

## ADDED Requirements

### Requirement: Nemotron output is labelled and human-confirmed

Every Nemotron output SHALL be labelled as Nemotron work, carry no confidence or approval score, and take effect only after a person confirms or decides it. When Nemotron is unavailable the system SHALL show "Not run" with the manual fallback and SHALL NOT display invented output.

#### Scenario: Intake sorting needs confirmation
- GIVEN a reviewer drops seven files into intake
- WHEN Nano proposes document types and claim identifiers
- THEN nothing is saved until the reviewer confirms or corrects each choice

#### Scenario: Model unavailable
- GIVEN the Token Factory call times out or the spending stop has been reached
- WHEN the reviewer opens intake
- THEN the confirm screen appears with empty choices and the reviewer selects the types by hand

### Requirement: Narrative questions quote their sources

P07 SHALL show a narrative question only when every quote in it matches its cited page of the current case version word for word. Output that fails verification SHALL be discarded and counted as a coverage gap, and a person SHALL decide each question.

#### Scenario: Altered quote
- GIVEN Super returns a question whose quote differs by one word from the cited page
- WHEN the server verifies the quote
- THEN the question is discarded and the coverage shows one gap

#### Scenario: New version reopens decisions
- GIVEN a reviewer decided a question on version 1
- WHEN version 2 is imported
- THEN the question is reopened for decision against version 2

### Requirement: Spending stop

The application SHALL record the cost of every Nemotron and Tavily-assisted call in a ledger and SHALL stop making paid calls when the ledger reaches $45.

#### Scenario: Budget reached
- GIVEN the ledger total equals the $45 limit
- WHEN a reviewer starts P07
- THEN no request is sent to Token Factory and the screen shows "Not run" with the manual comparison

### Requirement: Related PhilHealth rule references

For checks P02 to P09 the application SHALL show a reference only when its passage came from philhealth.gov.ph and matches the search result word for word. References SHALL NOT change a check result and SHALL NOT appear in an export. Queries SHALL contain no case data.

#### Scenario: Unverified passage
- GIVEN Nano proposes a passage that does not occur in the retrieved page
- WHEN the server verifies it
- THEN no reference is shown for that check

#### Scenario: Check again limit
- GIVEN a signed-in user pressed Check again for a check type
- WHEN any user presses it again within 10 minutes
- THEN the cached reference is shown and no new search is made

### Requirement: Account administration

An administrator SHALL be able to list, create, disable, enable and reset the password of named accounts and to end their sessions. Each action SHALL re-check the administrator's MFA and write an audit record, and an administrator SHALL NOT open cases.

#### Scenario: Disable an account
- GIVEN an administrator signed in with MFA
- WHEN the administrator disables a reviewer account
- THEN the reviewer's sessions end, an audit record is written, and the reviewer can no longer sign in

#### Scenario: Administrator opens a case
- GIVEN an administrator session
- WHEN the administrator requests a case
- THEN access is denied

### Requirement: Judge isolation

Judge reviewer accounts SHALL see only their own three cases. Supervisor judge accounts SHALL require MFA. No administrator account SHALL be given to judges.

#### Scenario: Other reviewer's case
- GIVEN reviewer A and reviewer B each have three cases
- WHEN reviewer A requests a case of reviewer B through the page or the API
- THEN access is denied

### Requirement: Public landing page and indexing

The application SHALL serve a public landing page at `/` that states what the product does and how Nemotron is used, shows the sample-records notice, and invents no statistics. Every route behind sign-in SHALL send a no-index directive.

#### Scenario: Visitor without a session
- GIVEN no session
- WHEN a visitor opens `/`
- THEN the landing page renders and offers sign-in
- AND an application route answers with a no-index header

### Requirement: Backups and restore

The hosted site SHALL back up its data nightly in encrypted form to a private bucket, and a restore into an empty PostgreSQL SHALL return the cases to a readable state.

#### Scenario: Restore drill
- GIVEN a nightly backup exists
- WHEN the archive is restored into an empty PostgreSQL
- THEN the application reads the restored cases and their original documents
