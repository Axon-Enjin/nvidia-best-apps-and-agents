# Tasks: Frontend redesign

> Execute inline in reviewable slices; each task is proven by its tests before the next. Evidence belongs in [verify.md](verify.md). Requirements are in [specs/review-workspace/spec.md](specs/review-workspace/spec.md).

## 1. Record and baseline
- [x] 1.1 Record this change, the design research and the baseline test counts; map every static-UI browser assertion to its replacement (all requirements)

## 2. Backend boundary
- [x] 2.1 Accept the configured web origin for proxied changes (requirement: Same-origin API boundary)
- [x] 2.2 Name the conflicting source values behind P04 and P05 (requirement: Review shows exact differences beside the source)

## 3. Web foundation
- [x] 3.1 Next.js app, streaming same-origin proxy, security headers and browser harness (requirement: Same-origin API boundary)
- [x] 3.2 Design tokens, workspace shell, named sign-in and sign-out (requirement: Named sign-in through the web origin)
- [x] 3.3 Typed API contract checked against captured responses (requirement: Same-origin API boundary)

## 4. Flow
- [x] 4.1 Claims queue with URL state and legacy links (requirements: Claims queue with URL state; Resume where action is needed)
- [x] 4.2 Intake with manifest matching and safe retry (requirement: Intake shows each declared document)
- [x] 4.3 Case phases, processing state and scan confirmation (requirements: Resume where action is needed; Document states stay distinct; Scan confirmation beside the original)
- [x] 4.4 Issues beside their evidence (requirement: Review shows exact differences beside the source)
- [x] 4.5 Corrections, manual reviews and draft safety (requirements: Correction progress uses real events; Manual review and separate acknowledgement; Drafts survive expiry and conflicts)
- [x] 4.6 Completion, records and full browser acceptance (requirement: Guarded completion and records)

## 5. Quality and delivery
- [x] 5.1 Keyboard, zoom, reduced motion, contrast, and one batched visual review with a confirmation pass (requirement: Offline, accessible delivery)
- [x] 5.2 Local setup, verification script, CI and Compose for the web app (requirement: Offline, accessible delivery)
- [x] 5.3 DSD, SDD, build guide, state and handoff; regenerate root guides
- [ ] 5.4 Retire the static UI after owner acceptance
