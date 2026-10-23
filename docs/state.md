# Project State: Sentinel Claims

**Project slug:** `sentinel-node`
**Owner:** Yushin
**Last updated:** 2026-10-23

## 1. Position

**Current milestone:** Implement the hosted evaluation for the Nebius x NVIDIA hackathon (active change `docs/changes/hackathon-hosted-evaluation/`, entered 2026-10-23); the offline prototype stays in Verify with its runtime gates open. **Next milestone:** Submit by Oct 30, 2026, 10:00 AM PT (target Oct 30, 18:00 PHT), then hold the judged site unchanged until Dec 15 except security and personal-data fixes.
**Exit condition (hosted evaluation):** the seven gates in the change's tasks.md pass on the live site. **Exit condition (offline prototype):** Complete the local import, evidence review, correction, revised-source review, guarded closeout/export, local OCR and recovery tasks; execute disconnected browser acceptance.
**Current blocker:** The Philippines is missing from Token Factory's billing country list, so no Token Factory account or key exists; staff gave no timeline (Oct 9, Oct 23). Last safe day for a working key is about Oct 26. Plan in the change's design.md. Earlier: Docker engine, WSL, Podman and PostgreSQL are unavailable on this host. Local implementation and SQLite browser/recovery tests run; container build, PostgreSQL workflow/restore, Linux OCR, OS/container isolation and hosted CI execution remain unverified. No owner pause remains.
**Product:** Hospital PhilHealth reviewers reconcile prepared adult medical inpatient claims and source corrections before submission through the existing hospital system.
**Frontend:** The Next.js review workspace in `apps/web` (change `frontend-redesign`) is implemented and verified locally; the static UI stays available until the owner accepts the new frontend.
**Engagement:** Hospital readiness first; local offline prototype before hosted evaluation. **Vault status:** none.

## 2. Active signals

| Signal | Evidence | Consequence |
|---|---|---|
| S1 / S2 / S4 | Approved UI, backend/auth/data and workflow | PRD, DSD, SDD |
| S5 | Owner explicitly resumed the build | BUILD guide; task-by-task implementation |
| S7 / S9 / S12 / S20 | Eventual hosted release, named accounts and remote model path | QAD, CLR, AIA, OPS remain release dependencies; offline core has no provider dependency |
| S11 / S16 | Public repository and multiple contributors | Reader-facing status and L1 practices required |
| S22 / S27 / S29 | Hackathon context, time box and claims activity | Pitch deferred; no delivery-date promise; CLR postures retained |
| S23 | Scaffold checkpointed and tested against existing PRD/SDD | CHANGE: offline-prototype |
| S30 | Hackathon deadline Oct 30; hosted evaluation A pulled forward; judges need a live demo | Active CHANGE: hackathon-hosted-evaluation; hosted release gates in tasks.md |
| S31 | Token Factory billing excludes the Philippines | Blocker; teammate-abroad account or AI Cloud endpoint as fallback; stand-in client meanwhile |

The hosted evaluation uses synthetic records only. No production deploy, real patient data, pricing, named buyer or investment decision exists. No SAD or new RFC is justified. The existing conventional architecture is retained.

## 3. Operating frameworks

Milestones. Work inline on `feat/offline-prototype` in the existing isolated worktree.
L1 is required by multiple contributors; current evidence is local tests only, no CI/preview/deploy pipeline. Packaging task adds CI. Do not claim the required level already exists.

## 4. Open assumptions

| ID | Assumption / uncertainty | Risk / resolution |
|---|---|---|
| A1 | Build rate uncalibrated | Yushin; no date promise until measured |
| A2 | Reviewer benefit and OCR/model quality unmeasured | QAD evaluation before readiness claim |
| A3 | Synthetic patient records only; staff/account data can be real PII | Local protection before invitations; new decision before patient records |
| A4 | One team, five users/two audits, 100 imports/day, 10k metadata | Load test before capacity claim |
| A5 | Hospital export/profile can be qualified later | Mandatory before operational pilot |
| A6 | Cloud provider/region/terms/cost and OCR/database container versions unresolved | Plan A Nebius AI Cloud `us-central1` `cpu-d3` `2vcpu-8gb` (about $90 through Dec 15, only if the account can be billed); plan B Oracle free server, Singapore; decided by the end of Oct 24 |
| A7 | Current design defaults remain reversible | Tests and reviewer evidence govern refinement |
| A8 | Yushin operates supervised evaluation | Uptime alert emails the owner (gate 7); judges are invited by the Devpost submission |
| A9 | Offline means local server after dependency/image installation, without external runtime calls | Not an air-gapped installer or cross-device synchronization; final task independently blocks egress |
| A10 | This host runs Node.js 25.4.0, an odd-numbered release | CI and the frontend image pin 24.22.1 LTS; install an LTS Node locally before long-term use |

No further product approval is required to continue the already authorized tasks. External runtime or data-scope changes still require the applicable facts/authorization.

## 5. Decisions

| ID | Decision | Evidence class / revisit |
|---|---|---|
| D1 | Sentinel Claims audience name; sentinel-node technical slug | Accepted human decision |
| D2 | Adult medical inpatient scope and P01-P10 | Accepted baseline; PRD owns behavior |
| D3 | Synthetic patients, environment notice and export provenance | Human decision; explicit new authorization for real records |
| D4 | External FMD v3.0.1 at 4979fda, read-only | Never commit/push to engine repository |
| D5 | MIT project license and public repository | Project canonical |
| D6 | Local prototype precedes deployed evaluation A and operational pilot B | Human direction; later release gates retained |
| D7 | Owner resumed implementation and authorized project commits/branch on 2026-10-21 | Latest explicit instruction supersedes pause |
| D8 | Offline default; online inference requires explicit opt-in plus credentials | Agent implementation choice under offline-first instruction; tests in Task 1 |
| D9 | Two-app layout: `apps/api` executed, `apps/web` reserved; shared fixtures and browser acceptance at the repository root | Human direction in `prompts/organize-repository.md`; record in `docs/changes/repository-organization/` |
| D10 | Next.js frontend in `apps/web` behind a same-origin `/api` proxy; FastAPI keeps authentication, permissions, transitions, jobs, storage and closeout; FastAPI accepts configured `TRUSTED_ORIGINS`; checks gain an additive `differences` field | Owner brief (2026-10-22) with agent implementation choices recorded in `docs/changes/frontend-redesign/design.md`; static UI retired only after owner acceptance |
| D11 | Oct 30 entry is the real product on a hosted site, synthetic records only (evaluation A); after submission the site stays unchanged until Dec 15 except security and personal-data fixes | Human decision, 2026-10-23 |
| D12 | Nemotron on Token Factory: Nano sorts intake files and drafts correction notes; Super compares narratives for P07; every quote is verified word for word and a person decides; vision-language reading cut | Human decision |
| D13 | Models are settings: Super `nvidia/nemotron-3-super-120b-a12b`, Nano `nvidia/nemotron-3-nano-30b-a3b` (unconfirmed until the probe); the app stops paid calls at $45 of credits | Probe confirms; Nebius removed Nemotron models on Aug 31 |
| D14 | Tavily finds the PhilHealth rule behind findings for P02-P09: fixed queries, philhealth.gov.ph only, server-verified passage, never in exports or check results | Human decision; tested 2026-10-23 |
| D15 | One server runs everything including PostgreSQL 17; Caddy HTTPS on DuckDNS; nightly encrypted backups to a private bucket | Plan A Nebius AI Cloud, plan B Oracle Singapore |
| D16 | Retire the old prototype surface; keep tables; admin, overview, landing page and Working Papers redesign in scope | Human decision |
| D17 | Judge access: six reviewer accounts (three cases each) and two MFA supervisors; no admin account for judges | Human decision |
| D18 | Never cut: $45 stop, quote verification, MFA re-check, judge isolation, accessibility, backups, redesign and landing page | Human decision |

D8 now reads: offline is the default for local installs; the hosted site sets `NETWORK_MODE=online` explicitly.

## 6. Context exclusions

The old nightly/revenue proposal and old prototype plan are historical. Keep local research untouched. Scaffold is now committed, not a completed app; shared-token access and single-XML/chart assumptions remain to replace. Canonical requirements and active change govern.

## 7. Next actions

Hosted evaluation (this week):

1. Owner: reply in the Token Factory Discord thread and message staff; find a teammate abroad who can own the Token Factory account; check AI Cloud billing at console.nebius.com (stop before entering a card).
2. Say "push approved" when ready; S2 scans, pushes and watches CI, then probes Nano and Super.
3. Work S3, S5 and S6 against a stand-in meanwhile. Decide plan A or B for hosting by the end of Oct 24.
4. Keep `output/hackathon/friction-log.md` for the mandatory feedback.

Offline prototype (still open):

1. Start a working Linux-container runtime and execute the commands in LOCAL-SETUP.md, including PostgreSQL correction, OCR and isolated restore acceptance. Compose configuration alone does not pass this gate.
2. Execute the prepared CI workflow before claiming established L1 practice. No push or hosted run occurred in this session.
3. Repeat browser acceptance with OS/container egress isolation and inspect traffic. The current test independently blocks browser external origins and Python server non-loopback sockets; it is not a whole-machine firewall.
4. Retain hosted release, live-model quality and hospital qualification as later gates.
5. Owner review of the new frontend (screens in `test-results/web/screens/`); after acceptance, retire the static UI (frontend-redesign task 5.4). Hosting the frontend needs the owner's choice of host, cost limit and permission to push.

Tasks 1-8 are implemented and verified. Tasks 4-8 added the bounded profile, evidence workspace, correction/manual review events, guarded reports and real printed OCR. Task 9 adds encrypted checkpoints, isolated SQLite restore, retirement-ledger reconciliation, bounded worker retries and container/CI artifacts. Its PostgreSQL/container gate remains open.

Task 10 locks 40 independently authored evaluation cases (20 discrepancies, 10 clean, 10 incomplete/adversarial), 20 corrected pairs and printed equivalents. A real browser exercises import through correction, manual comparison, separate privileged acknowledgement, export and process restart, including denied second-account access. This is deterministic synthetic acceptance, not a clinical/model benchmark or hospital study.

Five concurrent named readers exercised 10,000 synthetic metadata rows with assignment isolation and bounded pagination. The observed five-request sample is not a throughput or service-level claim. Exact test results and known limits live in the active change verification record.

Preserve the local encryption key, private sources, generated container password and separate recovery key. Retire denies access and preserves an authenticated tombstone; physical retention deletion/scheduling remain later work. Optional untracked research and old plans remain untouched.

## 8. Self-Check

- [x] Latest owner instruction, current branch, verified progress and remaining tasks recorded.
- [x] App verification is distinguished from future prototype, hosted and hospital gates.
