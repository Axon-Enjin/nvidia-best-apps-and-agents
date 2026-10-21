# Sentinel Claims interface

Updated: 2026-10-21. Accepted product/experience direction following the owner's instruction to proceed with the recommended changes. This replaces the earlier implementer proposal. It describes intended behavior, not completed screens. The formal FMD design artifact remains pending access to the required external engine.

Detailed scope and acceptance criteria: [PILOT-DECISIONS.md](PILOT-DECISIONS.md). Product entrypoint: [PRODUCT.md](PRODUCT.md).

## Brand and language

Name: **Sentinel Claims**. Descriptor: **PhilHealth claim review workspace**. Promise: **Find discrepancies. Trace the evidence. Close the review.** Keep `sentinel-node` as the technical slug.

Use direct, calm language: Claim, Supporting records, Finding, Request correction, Needs review, Review history. Completion means **Ready for final submission review**, an internal hospital workflow state. Never imply payer approval or guaranteed payment.

## Main surfaces

- **Review queue:** claim reference, discharge date, assignee, age in queue, completeness, and review state. Filter by assignee/state and sort by age. Show filing deadlines only from explicit supplied values or verified applicable rules.
- **Case workbench:** coverage and document membership, findings alongside original evidence, source location and version, reasoned dispositions, and manual checklist items. Preserve selection and focus while moving between findings.
- **Corrections and history:** responsible person/department, handoff and acknowledgement, revised document versions, prior findings, reopened decisions, and final review records. Export a correction sheet for use through the hospital's existing channels.
- **Administration:** accounts/permissions, supported profile and rule versions, retention, and operational diagnostics. Keep infrastructure details here unless a limitation changes the reviewer's next action.

## Evidence and interaction rules

Every finding opens its correct document version/page/field. OCR text appears beside the original scan; critical identifiers, dates, and amounts require source-backed confirmation. Extraction corrections remain attributable and separate from the original document.

Check coverage uses **Completed / Needs review / Not run / Unsupported / Failed**. Case workflow uses **Received / In review / Awaiting correction / Ready for final submission review / Archived**. Show processing progress separately so a completed background job cannot be mistaken for a finished review.

Required missing inputs and unresolved issues block completion according to checklist P01–P10. Dismissals require reasons; the sole initial noncritical exception is a supervisor withdrawing an incorrectly declared additional attachment requirement. Technical failures stay visible even when a documented manual review provides a fallback.

Show source/rule changes as requiring renewed review. Protect against stale concurrent updates and flag old reports. Provide explicit loading, empty, incomplete, unsupported, failure, and unavailable-inference states. A retry must not duplicate a case or hide earlier results.

## Visual direction and accessibility

Use a light warm-paper workspace, dark forest navigation, restrained teal actions, amber attention states, and red for blocking issues. Pair state colors with text/icons. Use readable sans-serif type, tabular numerals, fine rules, generous document margins, and consistent icons.

Desktop-first at 1366×768, with keyboard navigation and visible focus. On narrow screens, stack queue, findings, and evidence without losing the selected case. Format operational timestamps in Asia/Manila and financial amounts in the source currency, normally PHP. Show explicit dates rather than ambiguous numeric date formats.

## Evaluation presentation

Show realistic fictional records in the ordinary workflow. Use one **Evaluation workspace — sample patient records** indicator and provenance on exports. Do not repeat "static data" badges or imply the records came from an actual hospital. Metrics must derive from stored cases/actions; exclude invented recovery amounts, testimonials, and hospital partnerships.

Existing walkthroughs and provisional screens are reference material. This update creates no mockup, product code, or deployment.
