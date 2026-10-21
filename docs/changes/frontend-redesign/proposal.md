# Proposal: Frontend redesign

**Project:** Sentinel Claims
**Date:** 2026-10-22
**Status:** In Progress
**Owner:** Yushin

## Intent

Give reviewers one clear path through a claim (import it, review what needs attention, complete and export) in a Next.js frontend whose design makes each issue and its source evidence easy to read side by side.

## Scope

- A Next.js App Router application in `apps/web/` (React, strict TypeScript, Tailwind CSS) that replaces the static UI in `apps/api/src/sentinel/static/`.
- A same-origin `/api/*` proxy that preserves the session cookie, CSRF header, Origin validation, uploads and authenticated document and report responses.
- Real routes for sign-in, the claims queue, new-claim intake and the three case phases (Import, Review, Complete), with deep links, queue filters in the URL and redirects for old `/#case=` links.
- Intake that groups the manifest and original files, shows each declared document's state, and keeps unreadable, unsupported and unmatched documents distinct. Printed-scan confirmation beside the original.
- Review that defaults to unresolved issues, shows exact differing values with their document, page and version, offers one primary next action, and keeps correction, manual review, supervisor acknowledgement, extra attachments, reruns, history and earlier versions as real, attributable actions.
- Completion with named responsibility, current version, coverage and exact blockers; CSV and printable records after the immutable snapshot; stale records kept inspectable.
- Two additive backend changes: a configured list of trusted web origins, and a `differences` field on checks naming the conflicting source values behind P04 and P05.
- Local setup, CI and Compose entries for the Node.js runtime and frontend build.
- The design system update in the DSD (distinctiveness 6/10, editorial archive composition, evidence marks).

## Out of scope

- Hosting, deployment, pushing, cloud purchase and the hosted-frontend plan's open decisions.
- Nemotron online mode, live model quality and any change to the offline default.
- Changes to review rules, rule version, statuses, roles, permissions, schema or stored data.
- Case assignment UI, administration screens, public registration and drag-and-drop upload.
- Closing the offline prototype's open runtime gates (container build, PostgreSQL, Linux OCR, CI execution).

## Approach

FastAPI remains authoritative for authentication, permissions, review transitions, jobs, storage and closeout. Next.js renders pages with Server Components that read through a server-only client forwarding the session cookie, and a catch-all route handler streams browser API calls to FastAPI on the same origin. Client Components own selection, forms, uploads and bounded polling. The work proceeds in reviewable slices, each proven by browser tests against the live backend; the static UI remains available until the owner accepts the new frontend. The detailed plan is the execution guide; [design.md](design.md) holds the decisions.

## PRD trace

| Feature | Contribution |
|---|---|
| PRD-F1 | Named sign-in, privileged MFA, role-aware actions and denied second-account access through the new frontend |
| PRD-F2 | Intake, coverage states and printed-scan confirmation beside the original |
| PRD-F3 | P01-P10 shown with plain labels, exact differing values and explicit offline AI status |
| PRD-F4 | Correction request, handoff, acknowledgement, corrected import and resolution as distinct events |
| PRD-F5 | Guarded completion, current and stale records, CSV and printable export |
| PRD-F6 | Reproducible local runtime with Node.js added; offline operation after installation |
