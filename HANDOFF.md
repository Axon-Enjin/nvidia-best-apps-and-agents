# Sentinel Node: project flow and session handoff

Last updated: **2026-10-21**. Read this at the beginning of a new session.

## Current instruction

**Reconcile the approved product baseline into FMD. Application development is paused.**

The owner's latest direction is: "proceed with the FMD reconciliation. Proceed with the changes that you recommend to the earlier proposal, then write or populate the FMD". This authorizes adopting the recommended product/experience changes and writing the FMD artifacts through the required engine. The earlier instruction to settle the product before starting application development remains in force.

The owner first delegated the remaining decisions, then approved proceeding with the recommendations after receiving the report. [PILOT-DECISIONS.md](PILOT-DECISIONS.md) records the accepted baseline, supported by [PILOT-WORKFLOW-RESEARCH.md](PILOT-WORKFLOW-RESEARCH.md). [PRODUCT.md](PRODUCT.md) and [DESIGN.md](DESIGN.md) now summarize it. The owner subsequently requested a checklist of work that can be built without the FMD engine; [BUILD-CHECKLIST.md](BUILD-CHECKLIST.md) contains that assessment and recommended order. Creating the checklist did not resume implementation. Do not restart the product interview or ask again whether these recommended changes may be adopted. Existing code, mockups, and earlier research do not establish completed implementation or hospital readiness.

## Read context in this order

1. [AGENTS.md](AGENTS.md): repository instructions, including the FMD v3.0.1 engine requirement.
2. This handoff: recent owner instructions, context map, and the next discussion.
3. [docs/state.md](docs/state.md): FMD operating position, decisions, assumptions, and milestone.
4. [docs/idea-sentinel-node.md](docs/idea-sentinel-node.md): the brief to fill through product discussion.
5. [docs/scrutiny-sentinel-node.md](docs/scrutiny-sentinel-node.md): the current gate, gaps, and questions.
6. [docs/index.md](docs/index.md) and [docs/log-sentinel-node.md](docs/log-sentinel-node.md): artifact status and historical actions.
7. [PILOT-DECISIONS.md](PILOT-DECISIONS.md): the accepted product baseline dated 2026-10-21, authorized for FMD reconciliation. [PILOT-WORKFLOW-RESEARCH.md](PILOT-WORKFLOW-RESEARCH.md) records the hospital workflow evidence. These are records outside FMD, not reconciled suite artifacts or application build authorization.
8. [BUILD-CHECKLIST.md](BUILD-CHECKLIST.md): feasible implementation work independent of the engine, with dependencies, completion evidence, and external release prerequisites. All build boxes are unchecked; it records readiness to implement, not implementation progress.

Use the following references when the discussion needs them; a new session need not reread all research before asking the next useful question:

- [HACKATHON.md](HACKATHON.md): event constraints, submission requirements, and recorded deadline. Recheck the official rules before making a current eligibility or deadline claim.
- [docs/sentinel-node-claims-interoperability-research.md](docs/sentinel-node-claims-interoperability-research.md): claim-bundle boundaries, export/encryption constraints, existing vendor validation, and the limits of hospital compatibility. This file was local and untracked at handoff time; it may be absent from a fresh clone.
- [docs/sentinel-node-walkthrough.html](docs/sentinel-node-walkthrough.html): an interactive explanation with fictional examples, not a working auditor or an approved design. Also local and untracked at handoff time.
- [Hackathon-AI-Agent-Research.md](Hackathon-AI-Agent-Research.md): original opportunity research. Treat its recommendation, scores, market sizes, pricing, cost estimates, and architecture as hypotheses.
- [ORG.md](ORG.md) and [PROMPT.md](PROMPT.md): sponsor background and the original research instructions. These do not override the owner's product decisions.
- [LICENSE](LICENSE): MIT license already present in the repository.

## Authority and reconciliation

Apply the owner's latest explicit instructions first. Use STATE for the current operating position, IDEA for the approved problem/user/scope once filled, SCRUTINY for the recorded assessment, and LOG for history. Use this handoff to find those sources and recover conversation context, not as a competing permanent product specification.

The FMD documents were last reconciled on **2026-10-12**. This conversation continued afterward. Preserve their history, but reconcile the following before relying on them as current:

- STATE says there is no app code or backend. Unfinished local scaffolding now exists; it is paused and provisional.
- STATE records Sentinel Node as the product name. The accepted audience-facing name is now Sentinel Claims; the technical slug remains `sentinel-node`.
- IDEA and SCRUTINY leave the claims-auditor direction unconfirmed. The owner has since confirmed the user/job, delegated the remaining decisions, and authorized the recommended product changes. Reconcile against PILOT-DECISIONS.md, not the entire original research report.
- Local `PRODUCT.md` and `DESIGN.md` originally came from the premature build. They were replaced on 2026-10-21 with summaries of the accepted baseline; previous versions were backed up. The plan under `docs/superpowers/` and provisional app code remain historical proposals to reassess later.

FMD's recorded verdict remains **DO NOT BUILD YET**. The owner's explicit pause independently remains in force.

### External FMD engine

AGENTS.md points to **FMD v3.0.1**, whose engine must remain outside this repo. The pointer supplies no engine location. The latest main and original PR #2 also contain only the pointer and populated inception documents; no engine/kernel is included. Broader local searches, including hidden/ignored files in the workspace, OneDrive, skills, and tooling directories, did not find the exact kernel or scripts. An older Matrix project's pointer identifies `https://github.com/delatorrecj/fmd` at v1.28.1, but Git/gh return repository not found with current access; do not substitute that older version. The owner has been asked for the exact v3.0.1 path, accessible repository, or download. FMD checks have **not run**.

Before editing FMD artifacts, locate the external engine, read its kernel, and use its prescribed templates/scripts against this repo's `docs/`. Do not substitute another version, copy engine files into the repo, manually regenerate its index, or claim an engine validation passed. If the engine remains unavailable, report the limitation and continue the owner's discussion or maintain this standalone handoff without representing that as FMD reconciliation.

Access retry on 2026-10-21: at the owner's request, retried `git ls-remote --tags https://github.com/delatorrecj/fmd.git`, GitHub repository lookup/API, and the public repository page. Git returned repository not found; the API authenticated as `nanashi2802` returned HTTP 404, as did the public page. The URL may be private, renamed, or unavailable; this result does not establish which. No clone was obtained and no FMD files were changed. The owner explicitly forbids **commits or pushes to the FMD repository** and authorizes commits only to this current repository. Keep any future engine checkout external and use it read-only.

## What the owner has already established

- Build independently first; a billing-manager collaboration is not a prerequisite for starting the eventual prototype.
- Settle product behavior, features, brand, and preliminary decisions **before resuming implementation**.
- Keep local setup easy while preserving the capability to deploy and scale. Local-only architecture is insufficient.
- Preserve the repository's existing work while reviewing it.
- The FMD standing data decision is **synthetic data only**. Any later use of personal or health records requires an explicit new decision and appropriate handling arrangements.

The primary user is confirmed below. The assistant made the remaining choices under delegation and the owner subsequently authorized proceeding with the recommendations and FMD reconciliation. External dependencies and unverified readiness remain explicit. Do not infer completed capabilities from the existence of code. The dated discussion entries below preserve the earlier sequence; the current instruction above takes precedence.

### Owner decision: first-release priority (2026-10-21)

- **Hospital pilot readiness leads first-release tradeoffs.** The owner requires a ready application that is deployed.
- Fixed sample data is acceptable. The owner's wording was: "Datas can be static but must not be stated as static. Treat as if they are actual data."
- This does not authorize obtaining real patient records or revoke the standing synthetic-data boundary. The assistant proposed realistic sample records in the normal workflow, without repeated "static" labels, with the environment identified as a demo. That presentation proposal has not yet been confirmed by the owner; do not represent fictional records as actual hospital records.
- Deployment is a confirmed requirement; the hosting environment, access model, persistence, and pilot acceptance criteria remain open. Application development is still paused until explicit authorization to resume.
- **Primary user and job confirmed:** a hospital PhilHealth claims reviewer checking a prepared claim against supporting records before submission. The owner answered "yes" to this specific user/job proposal. This confirms the claims-review product direction, but does not approve the entire research proposal or its features.
- Next decision: establish the reviewer's core pain moment and the outcome the first release should improve. Cross-document inconsistencies and missing supporting evidence are candidates, not yet confirmed priorities.
- FMD reconciliation remains pending: a read-only search under `C:/Users/Yushin/orca` and `C:/Users/Yushin/.agents/skills` did not locate the v3.0.1 kernel or its scripts. This standalone handoff records the discussion; no FMD validation was run.

### Delegated product baseline (2026-10-21)

- The owner subsequently delegated the remaining decisions. The selected audience-facing name is **Sentinel Claims**, keeping `sentinel-node` as the technical slug. The positioning is a PhilHealth claim review workspace.
- Start with one hospital/team and adult general medical inpatient claims before initial submission. Core loop: import a versioned bundle, inspect evidence-linked findings, assign corrections, reimport revised sources, rerun, and record internal review completion before submission through the existing hospital system.
- The selected first-release scope includes printed-scan OCR, named roles/assignments, coverage reporting, correction handoffs, history, real content-derived checks, operational metrics, and a deployed persistent web app. It excludes submission automation, autonomous coding, and reimbursement guarantees.
- Fixed fictional records use the normal workflow with one environment-level sample-record indication and provenance on exports. They must not be passed off as actual hospital records. The behavior and saved actions must be real.
- Delivery baseline retains Python/FastAPI, with PostgreSQL, separate web/worker processes, private document storage, and a hosted container deployment. The detailed hosting, evaluation targets, and release boundaries are in PILOT-DECISIONS.md; they are not completed capabilities.
- Distinguish a deployed workflow evaluation with sample records from an operational hospital pilot. The latter requires a qualified hospital export, approved processing/hosting arrangements, and reviewer validation. No actual partner, integration, accuracy result, or deployment has been established.
- Additional FMD searches under `.codex`, Documents, and Downloads found no matching engine. No `docs/` artifact was edited and no FMD validation ran. The standalone decision/research records preserve progress pending reconciliation.
- Next action: review the consolidated baseline and recommended changes; do not repeat settled preference questions. Application implementation remains paused pending explicit owner authorization.

### Adoption and reconciliation request (2026-10-21)

- The owner authorized proceeding with the recommended changes and populating the FMD. PRODUCT.md and DESIGN.md now reflect Sentinel Claims, the adult medical inpatient scope, versioned bundles, printed-scan OCR, named roles, correction handoff, reviewed completion, and the deployed evaluation/operational-pilot distinction.
- PILOT-DECISIONS.md now records the baseline as accepted. The exact external engine is the remaining prerequisite to formal FMD work; no extra product-approval question is needed.
- Pre-edit copies of PRODUCT.md, DESIGN.md, PILOT-DECISIONS.md, and HANDOFF.md are at `C:/Users/Yushin/AppData/Local/Temp/sentinel-fmd-reconciliation-1e3c68be7320431bb05b5ae6a43ce208` on this machine.
- Pending: obtain v3.0.1, read its kernel/templates, update STATE/IDEA/SCRUTINY, follow the resulting gate and triggers for downstream artifacts, generate INDEX/LOG using the engine, and run its checks. Do not invent a cleared gate or validation result.
- Application code, dependencies, and deployment remain unchanged. Do not use this documentation approval to resume implementation.

## Product flow: work through these decisions

This is a discussion sequence, not authorization to implement later stages automatically. Ask concise questions, explain material tradeoffs, distinguish recommendations from decisions, and record the owner's answers.

### 1. Frame the goal and primary user

Settle the first-release priority, the primary user, the task they are doing, their current workaround, and the concrete outcome the app should improve. Confirm whether the PhilHealth claim-review direction is the product to pursue.

**Done when:** IDEA contains a specific problem, primary user, pain moment, success outcome, and repeatable one-line description, with owner confirmation. Record the milestone/decision in STATE and LOG through FMD.

### 2. Define the core workflow and feature cut

Walk through the user's trigger, inputs, checks/actions, result, review decision, and next action. Separate must-have capabilities from later ideas and explicit exclusions. Decide what the app can establish and where human judgment remains necessary.

The current candidate is: upload a draft claim plus chart, run documented checks, inspect evidence-linked discrepancies, record a review decision, correct the source, and rerun. This is an option to assess, not a fixed specification.

**Done when:** the owner confirms the minimum end-to-end workflow, first-release features, exclusions, and one demonstrable success case in IDEA. Re-run SCRUTINY after material changes; a framing pass is not proof of market demand or model accuracy.

### 3. Settle the brand and experience

Decide the name, audience-facing positioning, product promise, voice, terminology, and visual direction. Check that the brand explains the agreed job and does not imply guaranteed acceptance, autonomous medical judgment, or proven financial recovery.

**Done when:** the owner explicitly confirms the brand decisions and the main user journey. Put them in the applicable FMD artifact when its trigger/gate permits; keep unresolved choices visible rather than inventing agreement.

### 4. Decide evidence, data, and delivery boundaries

Agree on supported input formats, synthetic demo data, the division between deterministic rules and AI, evidence requirements, error/incomplete states, and evaluation criteria. Define local setup and the intended deployed environment, access controls, persistence, worker needs, and scale target. Choose technology after these constraints are understood.

**Done when:** the owner has approved checkable acceptance criteria and delivery constraints, with assumptions and unresolved external dependencies recorded. Independent development still cannot establish hospital interoperability or customer demand.

### 5. Review the gate and authorize implementation

Review the updated IDEA and SCRUTINY with the owner. Resolve blockers or explicitly record accepted limits. Create downstream requirements, design, architecture, evaluation, and operations artifacts only when the FMD kernel says their triggers and prerequisites are satisfied.

**Done when:** the owner approves the product scope and explicitly asks to resume building. Then assess the provisional code against the approved decisions; retain useful parts, revise others, and obtain direction before discarding work. Passing a document gate alone does not revoke the owner's pause.

### 6. Build, verify, and package the submission

Only after stage 5: implement the approved workflow, test failure/incomplete cases and evidence behavior, verify local setup and deployment, then prepare the demo, setup instructions, model/platform explanation, video, and feedback required by the current rules.

**Done when:** the approved acceptance criteria have verification evidence and the required submission artifacts exist. Describe untested live integrations and deployment limits honestly.

## Research concerns to carry forward

These were identified in the earlier repository review. They are historical review findings to revisit as relevant, not newly verified facts from this handoff session:

- The report's September 2025 amnesty sales hook is stale: [official advisory](https://www.philhealth.gov.ph/advisories/2025/PA2025-0037.pdf).
- The stated private Level 2/3 hospital denominator differed substantially from [PhilHealth's accreditation table](https://www.philhealth.gov.ph/partners/providers/facilities/status.php). Refresh the table before calculating a market scenario.
- Existing and announced validation overlaps with the proposal; see [Circular 2026-0012](https://www.philhealth.gov.ph/circulars/2026/PC-2026-0012.pdf) and the [government AI pre-validation announcement](https://pco.gov.ph/news_releases/philhealth-to-implement-ai-enabled-pre-validation-system-to-prevent-fraudulent-claims/). An announcement does not prove deployment.
- A claim is a versioned bundle, not simply a CF4 PDF. Read the interoperability note before claiming current schema or vendor compatibility.
- Returned claims, delayed payments, permanent denials, and late filing are distinct problems; finding a discrepancy does not prove revenue recovered.
- A folder auditor cannot see encounters that never produce an exported claim unless it also receives an encounter/expected-claims manifest.
- Synthetic examples can demonstrate software behavior; they cannot establish clinical accuracy, hospital fit, or willingness to pay.

## Workspace handoff

The latest fetched `origin/main` is `3ce104b`, with the same tracked tree as the previous local FMD commit `582a3bd`. It was merged into `review/fmd-product-framing` as local commit `51e4535`; hashes confirmed the local modified/untracked files were preserved. Nothing was pushed. The previous branch `nanashi2802/codex-statusline` was preserved because remote history had been rewritten. These are historical coordinates, not instructions to switch or reset a future checkout.

Start with read-only checks:

```powershell
git status --short
git branch -vv
git log -5 --oneline
```

Unfinished local files include `sentinel/`, `tests/`, `migrations/`, `pyproject.toml`, `uv.lock`, `alembic.ini`, `.env.example`, `.gitignore`, `PRODUCT.md`, `DESIGN.md`, and an implementer-written prototype plan. Some research/PDF files are also untracked. Inspect current status; preserve these files without assuming they are committed, available remotely, or approved.

The prototype is incomplete: browser CSS/JavaScript and deployment packaging were not finished. The last dependency sync failed after a development dependency change. Earlier test runs are historical only; do not describe the current tree as installed, deployable, or passing without fresh verification after implementation is authorized.

The owner authorized committing the accepted root-level product documents, build checklist, research note, and handoff in this repository after the FMD access retry. The provisional application code and the optional untracked research/walkthrough files under `docs/` remain local and are not included in that documentation commit. A fresh clone will not receive those local-only files. No app execution or push was performed for this retry/documentation work.

## Next-session starting point

After reading the context, continue the authorized FMD reconciliation. The product choices and recommended changes have been accepted; do not restart the product interview. Obtain the exact external engine if access has now been provided, read its kernel, and apply its workflow. Application implementation remains paused.

The FMD engine location/access remains requested for formal reconciliation. The engine-independent BUILD-CHECKLIST.md is also ready for the owner's next direction. No further product preference or permission question is required to perform the already authorized documentation work. A request to create the checklist alone does not resume application development.

Copy this into a new session:

> Read AGENTS.md and HANDOFF.md, then follow the linked context. The recommended product baseline in PILOT-DECISIONS.md is accepted and FMD reconciliation is authorized. Locate/read the exact external FMD v3.0.1 engine, populate the appropriate artifacts through its workflow, and run its scripts against docs/. Preserve existing local work. Application implementation remains paused until I explicitly authorize it.

## Keep the handoff useful

At the end of a product-definition session, record confirmed decisions, unresolved questions, and the next action in the appropriate FMD sources using its engine. Update this handoff's date and continuation context if the pause, reading order, or next action changes. Keep historical test results and research separate from current verification. When implementation is authorized, replace the pause notice with that dated owner decision and point to the approved specification and plan.
