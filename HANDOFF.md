# Sentinel Claims: session handoff

Last updated: **2026-10-21**.

## Current instruction

**Implementation is resumed.** The owner instructed: "proceed with a commit with appropriate message, then lets branch off and continue the build. Write the next implementation steps so we can attain our first offline first but fully working prototype".

The existing scaffold was checkpointed as `e8c0ace` on `review/fmd-product-framing`. The build branch is **`feat/offline-prototype`** in this existing isolated worktree. Foundation changes are committed as `08b0c09`. The earlier product-definition pause is superseded; do not ask again whether already authorized development may resume.

Commits belong only in this current project repository. **Never commit or push anything to the external FMD repository.** No push, cloud purchase or real-patient-record processing is implied.

## Reading order

1. Root [AGENTS.md](AGENTS.md), generated from the canonical [build guide](docs/build-sentinel-node.md).
2. [docs/state.md](docs/state.md), then the active [implementation plan](docs/changes/offline-prototype/tasks.md) and [verification record](docs/changes/offline-prototype/verify.md).
3. For the task at hand: [offline requirements](docs/changes/offline-prototype/specs/offline-review/spec.md), [change design](docs/changes/offline-prototype/design.md), [PRD](docs/prd-sentinel-node.md) and [SDD](docs/sdd-sentinel-node.md).
4. For UI/evaluation: [DSD](docs/dsd-sentinel-node.md), [QAD](docs/qad-sentinel-node.md), [protection register](docs/clr-sentinel-node.md), [AI assurance](docs/aia-sentinel-node.md) and [operations](docs/ops-sentinel-node.md).
5. [docs/index.md](docs/index.md) and [append-only log](docs/log-sentinel-node.md) provide inventory and history.

[PRODUCT.md](PRODUCT.md) is the short reader entrypoint. [BUILD-CHECKLIST.md](BUILD-CHECKLIST.md) is the broader dependency checklist; the active task plan owns current execution progress. [PILOT-DECISIONS.md](PILOT-DECISIONS.md) and [workflow research](PILOT-WORKFLOW-RESEARCH.md) retain decision/source provenance, not competing requirements.

## Offline prototype boundary

Offline means the locally hosted app completes the supported workflow with external runtime traffic blocked after installation. The browser still connects to the local server/database. Install dependencies, container images and OCR language data before disconnecting. No browser cache/PWA or synchronization between installations is assumed.

Complete named sign-in, assignment, versioned imports, coverage/evidence, correction ownership and manual handoff, revised sources/recheck, human closeout, exports, local OCR and backup/restore. All controls must have real saved behavior. P07 can use the accepted manual comparison plus separate supervisor acknowledgement; AI remains not run/failed. Do not invent canned model results or waive required checks.

PostgreSQL remains the standard local/container target. SQLite remains an optional direct-development convenience, not proof of PostgreSQL concurrency or pilot deployment suitability. Docker was not found on this machine's command path; obtain an available runtime before claiming container/database acceptance. Hosted deployment and operational hospital gates remain later work.

## Verified progress

- `e8c0ace`: checkpoint of the existing application, migrations, tests, config and lockfile; recorded as incomplete. The initial `uv run --locked pytest -q` could not resolve `httpx2>=0.22,<1`.
- `08b0c09`: removed only that invalid constraint; `uv sync --locked` succeeds without changing `uv.lock`.
- `NETWORK_MODE=offline` is now default. Explicit online mode plus credentials is needed for remote inference; API, worker and adapter enforce the boundary.
- Six new tests failed before implementation, then passed. Full `uv run --offline --locked pytest -q`: **37 passed**, one Starlette/HTTPX deprecation warning. New test file passes Ruff.
- Queued remote jobs processed offline retain local results and explicit incomplete remote coverage. This is not yet the complete manual-review/closeout implementation.
- No full browser flow, PostgreSQL/container run, printed OCR test, restore drill, live inference or hospital evaluation has occurred.

Task 2 now implements named local accounts, Argon2id passwords, encrypted TOTP for supervisors/admins, replay fencing, revocable sessions, CSRF and assigned case access. CLI provisioning/recovery and a local login page are tested. Twenty account scenarios and one real Chromium desktop/mobile login check pass. Default named mode never accepts the old shared token; explicit development migration mode requires a configured token. See README for commands and private key handling.

Task 3 now adds JSON case creation (`POST /api/cases`), versioned manifests, private encrypted originals and durable quarantined parsing jobs. Eleven bundle tests cover idempotency, immutable versions, identity, ambiguity, limits, protected source access, concurrency and damage. Case assignment advances revision. Legacy rerun cannot replace a versioned case. Worker child parsing has time/memory bounds; profile completion is not inferred from successful extraction.

Next task is **Task 4: deterministic profile and complete synthetic bundles**. Tasks 4-10 remain unchecked. The change's overall verification is FAIL because the complete prototype is unfinished. Evidence workbench assets, full correction workflow, PostgreSQL/container/OCR/restore acceptance remain pending.

## Product boundaries already accepted

Sentinel Claims serves hospital PhilHealth reviewers checking adult general medical inpatient ACR claims after discharge and before initial submission. Scope is one team. Technical slug remains `sentinel-node`.

P01-P10 in PRD govern completion. Core missing documents, identity conflicts, open correction tasks and stale versions block closeout. Sole exception: supervisor withdraws a mistakenly expected extra attachment with a reason. The existing hospital system retains submission authority.

Synthetic patient records only. One environment-level sample indication and export provenance; ordinary records need no repeated static badges. No real patient records, hospital endorsement, clinical/coding decisions, autonomous source edits or payment guarantees.

SCRUTINY remains **PROCEED WITH FIXES**. Product choices are settled; performance, reviewer benefit and hospital interoperability remain unproven.

## External engine

Checkout: `C:/Users/Yushin/tools/fmd-v3.0.1`.
Source: `https://github.com/delatorrecj/fmd.git`.
Tag/HEAD: **v3.0.1**, **4979fda6435dc007a331c40a5e9e28db813eebb2**.
On the last fetch, main matched that October 11 release. Earlier 404 access failures were resolved.

Before docs work, read the external kernel and trigger matrix. Set `PYTHONDONTWRITEBYTECODE=1` and run engine scripts against project `docs/`; never copy engine files into this repository or edit the engine. INDEX/LOG and root materializations are engine-generated. Preserve historical log rows.

The committed document set is validated separately from unchanged local untracked research/old plans, whose style/manifest findings remain visible in full-workspace checks. Do not alter unrelated local notes just to make those checks green.

## Workspace and history

Origin is `https://github.com/Axon-Enjin/nvidia-best-apps-and-agents.git`.
Previous documentation commits: `b2919bf` accepted baseline/checklist; `bc974d6` populated reconciliation. Existing main merge `51e4535` preserved local work. These are history, not reset instructions.

Application source and tests are now tracked by the checkpoint. Optional untracked material remains: `output/`, `docs/sentinel-node-claims-interoperability-research.md`, `docs/sentinel-node-walkthrough.html` and the old plan under `docs/superpowers/`. Preserve them and exclude them from application commits unless specifically relevant.

[Historical opportunity research](Hackathon-AI-Agent-Research.md), [event reference](HACKATHON.md), [sponsor context](ORG.md) and [research prompt](PROMPT.md) do not override current scope. Recheck official rules before current submission claims.
