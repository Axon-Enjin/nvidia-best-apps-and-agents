# Tasks: Hackathon hosted evaluation

> Source of truth for the hackathon build. Execute in sessions; each is proven by its tests before the next. Evidence belongs in [verify.md](verify.md). Requirements are in [specs/hosted-evaluation/spec.md](specs/hosted-evaluation/spec.md). Schedule is in PHT and is not locked. Deadline: Oct 30, 2026, 10:00 AM PT; target submit Oct 30, 18:00 PHT.
>
> Rules: no push, deploy, spending or real patient data without the owner's go-ahead for that step. The FMD engine is read-only. Keys live only in git-ignored `.env` and `data/deploy/production.env`.

## Oct 22-23: Foundation

- [ ] S1 Record the decisions: this change record, `docs/state.md`, build guide §3 and §5 (regenerate `AGENTS.md`), `.gitignore`, `output/hackathon/` files (all requirements)
- [ ] S2 Push, CI, probe: scan unpushed commits for secrets, push `feat/offline-prototype`, watch CI with the PostgreSQL 17 test running; one Token Factory probe for Nano and Super (structured-output method, token count, cost); start the friction log. Needs the owner's "push approved" and a working Token Factory key (requirement: Nemotron output is labelled and human-confirmed)
- [ ] S3 Retire the old prototype: static screens, single-XML import and routes, old sample download, old Nemotron adapter and worker call, shared-password login, their tests; close frontend-redesign task 5.4; tables stay
- [ ] S4 Hosted settings: migrations tested on PostgreSQL 17 in CI; trust forwarded headers behind the proxy; `NETWORK_MODE=online` with model IDs from settings; no-index on every route except the landing page; restore command accepts an empty PostgreSQL target (requirements: Public landing page and indexing; Backups and restore)
- [ ] S5 New look and app shell, Working Papers: design contract, tokens, tick marks, index letters, role navigation (Claims, Import, Overview, Admin), applied to every screen; token contrast test updated; screenshots at 1366 and 375 px

## Oct 24: Nemotron core and first deploy

- [ ] S6 Token Factory client and spending stop, built against a stand-in until the account works: structured output, settings, timeouts, finite retries, size caps, spend ledger migration, $45 stop, offline sends nothing, data boundary; AI-06 and AI-09 (requirements: Spending stop; Nemotron output is labelled and human-confirmed)
- [ ] S7 P07 narrative comparison backend: up to four Super calls per version, word-for-word quote verification, discard and gap count, reviewer decision, reopen on new version; AI-02 to AI-05, AI-07, AI-08 (requirement: Narrative questions quote their sources)
- [ ] S8 First deploy, needs the owner's go-ahead: plan A Nebius AI Cloud `cpu-d3` `2vcpu-8gb` if the account can be billed; plan B Oracle Singapore, decided at the end of Oct 24 at the latest; production Compose with Caddy and the DuckDNS updater, server firewall, `production.env` copied without display, Linux OCR smoke test, current app live over HTTPS

## Oct 25: Nemotron features in the new design

- [ ] S9 Review screen rework with P07: working-paper spread, Nemotron questions in blue pencil with verified quotes, reviewer decisions in red, coverage gaps and "Not run" visible
- [ ] S10 Intake sorting with Nano and Intake rework: drop, propose, confirm or correct, import; fallback confirm screen with empty choices (requirement: Nemotron output is labelled and human-confirmed)
- [ ] S11 Correction drafts with Nano: draft pre-fills the note field, inert rendering, CSV safety at `reports.py:78`; AI-04, AI-07, AI-08 for drafts

## Oct 26-27: Tavily, Admin, Overview, landing, judges

- [ ] S12a Tavily PhilHealth references (built between S11 and S17): fixed query per check type P02-P09, restricted to philhealth.gov.ph, Nano picks the passage, server verifies word for word, 7-day cache, Check again limit, shown on finding and draft, never in export; AI-04 and AI-06 cover Tavily (requirement: Related PhilHealth rule references)
- [ ] S12b Admin API and screen: list, create, disable or enable, reset password, end sessions; MFA re-check and audit on every action; MFA key as text; admin cannot open cases (requirement: Account administration)
- [ ] S13 Overview, Queue and Complete rework: counts, assignments and event metrics from existing stats
- [ ] S14 Landing page and sign-in look: public `/` with no invented statistics, sample-records notice, sign-in button; app routes no-index (requirement: Public landing page and indexing)
- [ ] S15 Judge accounts and sample sets: seeding command for six reviewers (three cases each) and two supervisors with MFA; sample sets are the existing evaluation fixtures zipped and served as downloads; draft testing instructions (requirement: Judge isolation)

## Oct 28: Operations and live check

- [ ] S16 Backups, restore drill, uptime alert: nightly encrypted backup via cron, checkpoint and rclone to a private bucket; restore into an empty PostgreSQL; free uptime monitor that emails once on a test outage (requirement: Backups and restore)
- [ ] S17 Full live check, gates 1 to 7: scripted check against the HTTPS site reusing `test_web_acceptance.py`; sign-in with MFA, intake sorting, P07, correction draft, completion and export, second-account denial, admin create and disable; spending stop against a lowered test limit; AI-02 to AI-09 green in CI

## Oct 29-30: Finish and submit

- [ ] S19 Fixes, design review, freeze (Oct 29, 18:00 target): fixes from S17; one design review at 1366 and 375 px; deferred documents (PRD, SDD, AIA, QAD, OPS, CLR, DSD, `PRODUCT.md`, `HACKATHON.md`, older change records); close verification records; DSD rewrite from built screens
- [ ] S20 Video (Oct 29 evening): update `video-script.md` to the built screens; owner records on the live site, uploads to YouTube as public, under 3 minutes
- [ ] S21 Submission (Oct 30, by 18:00 PHT): README Nemotron and Token Factory section with live URL, Devpost text, testing instructions, feedback drafted from the friction log, pull request; owner merges; tag, deploy the tag, final live check; owner submits

S18 (vision-language second reader) was cut; Tavily replaced it.

## Gates

1. CI.
2. Server, including Linux OCR, against the hosted database.
3. Scripted live check.
4. Restore drill.
5. AI safety tests AI-02 to AI-09 (AI-01 is measured, not a gate).
6. Spending stop.
7. Uptime alert.
