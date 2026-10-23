# Proposal: Hackathon hosted evaluation

**Project:** Sentinel Claims
**Date:** 2026-10-23
**Status:** In Progress
**Owner:** Yushin

## Intent

Put the real product online as a hosted evaluation site, with Nemotron on Nebius Token Factory doing labelled work that a person confirms, so the Nebius x NVIDIA hackathon entry (Best Apps and Agents, bonus Best Use of Tavily) can be judged on a working app. Submission deadline: Oct 30, 2026, 10:00 AM PT; the working target is Oct 30, 18:00 PHT.

## Scope

- Hosted evaluation A from the accepted release path (decision D6): one server runs the web app, the API, the worker, PostgreSQL 17 and Caddy with HTTPS on a DuckDNS name. Synthetic records only.
- Nemotron on Token Factory in three places: Nano sorts uploaded files into the seven document types and proposes claim identifiers; Super compares narratives for P07 with every quote verified word for word against its source page; Nano drafts the correction note to medical records. A person confirms or decides every output.
- Tavily finds the PhilHealth rule behind each finding for checks P02 to P09, limited to philhealth.gov.ph, with the exact passage verified word for word by the server. Shown as "Related PhilHealth rule" and never part of a check result or an export.
- A spending stop at $45 of credits, so a model failure or exhausted budget shows "Not run" with the manual fallback.
- Administration of named accounts (list, create, disable or enable, reset password, end sessions) with MFA re-check and audit on every action.
- An overview of counts, assignments and event metrics; a public landing page; the "Working Papers" redesign applied to every screen.
- Judge access: six reviewer accounts (three cases each) and two supervisor accounts with MFA. No administrator account for judges.
- Retire the old prototype surface (static screens, single-XML import, old sample download, old Nemotron adapter, shared-password login).
- Operations: nightly encrypted backups to a private bucket, a restore drill into an empty PostgreSQL, an uptime alert.
- Hackathon deliverables: README, video, Devpost text, mandatory feedback.

## Out of scope

- Real patient data, payer submission, any claim of clinical or financial outcomes.
- A vision-language second reader (cut; Tavily takes its slot), a managed external database (cut), the Admin extras of rule-profile and health views (cut), a sign-in rework beyond inheriting the new look (cut).
- Agentic P07 (after Oct 30).
- Hosting on Vercel (only after Oct 30, as a later option).
- Changes to the judged site between submission and Dec 15, other than security and personal-data fixes.

## Approach

Keep the tested plumbing (FastAPI, Next.js, SQLAlchemy, worker, OCR, review events) and add one Token Factory client that every Nemotron call uses, with settings for model IDs, a spend ledger and an offline switch. Add features behind the existing review model so a person still decides everything. The work runs as sessions S1 to S21 in [tasks.md](tasks.md). Risk is ordered: the Token Factory account (see design.md, Blocker) first, then hosting, then features.

## PRD trace

| Feature | Contribution |
|---|---|
| PRD-F1 | Admin accounts, MFA re-check, judge isolation |
| PRD-F2 | Nano intake sorting with human confirmation |
| PRD-F3 | P07 narrative comparison with verified quotes, PhilHealth references, honest "Not run" states |
| PRD-F4 | Nano correction drafts, recorded handoff |
| PRD-F5 | Unchanged completion and export; references never exported |
| PRD-F6 | Hosted runtime, backups, restore drill, uptime alert |
