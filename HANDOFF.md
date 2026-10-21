# Sentinel Claims: session handoff

Last updated: **2026-10-21**.

## Current instruction

The owner authorized adopting the recommended product changes, reconciling/populating FMD, and committing documentation **only in this project repository**. Application development remains paused until an explicit instruction resumes it. Do not restart the product interview or interpret a checklist/pull request as application build authorization.

Latest repository instruction: retry access to `github.com/delatorrecj/fmd`; **never commit or push anything to that repository**. Access now works. The external engine is read-only for this project. No push is authorized by this documentation task.

## Reading order

1. [AGENTS.md](AGENTS.md): exact engine pointer and read-only boundary.
2. [docs/state.md](docs/state.md): current position, decisions and dependencies.
3. [docs/idea-sentinel-node.md](docs/idea-sentinel-node.md) and [docs/scrutiny-sentinel-node.md](docs/scrutiny-sentinel-node.md): settled framing and **PROCEED WITH FIXES** verdict.
4. [docs/prd-sentinel-node.md](docs/prd-sentinel-node.md): canonical behavior, P01?P10 completion contract, acceptance and rollout.
5. [docs/dsd-sentinel-node.md](docs/dsd-sentinel-node.md) and [docs/sdd-sentinel-node.md](docs/sdd-sentinel-node.md): experience and architecture, when needed.
6. [docs/qad-sentinel-node.md](docs/qad-sentinel-node.md), [docs/clr-sentinel-node.md](docs/clr-sentinel-node.md), [docs/aia-sentinel-node.md](docs/aia-sentinel-node.md), [docs/ops-sentinel-node.md](docs/ops-sentinel-node.md): pending test, protection, AI and operational evidence.
7. [docs/index.md](docs/index.md) and [docs/log-sentinel-node.md](docs/log-sentinel-node.md): generated inventory and preserved history.

[PRODUCT.md](PRODUCT.md) is the short entrypoint. [PILOT-DECISIONS.md](PILOT-DECISIONS.md) retains the dated accepted decision record; [PILOT-WORKFLOW-RESEARCH.md](PILOT-WORKFLOW-RESEARCH.md) retains source provenance. The canonical artifacts now own detailed requirements. [BRAND.md](BRAND.md) and [DESIGN.md](DESIGN.md) are generated from DSD, not independent specifications.

[BUILD-CHECKLIST.md](BUILD-CHECKLIST.md) gives feasible implementation order. All build boxes remain unchecked. Creating it did not resume application development.

## External engine: access resolved

Checkout: `C:/Users/Yushin/tools/fmd-v3.0.1`.
Source: `https://github.com/delatorrecj/fmd.git`.
Version/tag: **v3.0.1**; detached commit **4979fda6435dc007a331c40a5e9e28db813eebb2**.

Earlier authenticated/public retries returned 404. A subsequent authenticated clone and fetch succeeded on 2026-10-21; HEAD, fetched main and the peeled v3.0.1 tag matched, and the external working tree was clean. Main has no newer commit than the October 11 v3.0.1 release. The public page may still return 404 for this private repository. Do not treat the earlier access failure as current.

Read that checkout's AGENTS.md kernel and trigger matrix before docs work. Run its scripts against project documents; never copy the engine into this repository or upgrade the pinned version merely because upstream has newer commits. Fetching remote references is allowed; **commits/pushes to FMD are forbidden**.

From this project root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python C:/Users/Yushin/tools/fmd-v3.0.1/scripts/check.py docs/ --strict
python C:/Users/Yushin/tools/fmd-v3.0.1/scripts/record.py docs/ --action "Describe the actual documentation change" --check
python C:/Users/Yushin/tools/fmd-v3.0.1/scripts/materialize.py docs/
```

If this local path is unavailable on another machine, obtain the authorized exact tag externally. Do not substitute an older engine or fabricate a validation result. INDEX/LOG are engine-generated; preserve historical log rows.

## Settled product decisions

- Audience-facing **Sentinel Claims**, technical slug `sentinel-node`; PhilHealth claim review workspace.
- Hospital readiness leads over prize optimization. Deliver a functional deployed app, not mocked behavior.
- One team, adult general medical inpatient ACR, after discharge and before initial submission.
- Versioned document bundles, printed-scan OCR with source confirmation, coverage, evidence-linked checks, named roles/assignment, correction handoff, reimport/recheck and retained history.
- Human internal completion only; hospital's existing system performs final checks and submission. No coding, clinical advice, HIS writes or reimbursement guarantees.
- Synthetic patient records remain the authorized boundary. Use normal workflow presentation with one ?Evaluation workspace: sample patient records? indication and export provenance. Do not pass fictional records off as actual hospital data.
- First deliverable A is a deployed sample workflow evaluation; operational pilot B additionally needs a sponsor, qualified export/check profile, explicit real-data authorization, approved processing arrangements and reviewer validation.
- Python/FastAPI, PostgreSQL, separate web/worker, private document storage, CPU hosting and remote inference. Exact versions/endpoint/account terms/region/quota/cost remain to verify.
- No cloud purchase, live deployment, benchmark, hospital agreement or completed control is established.

The old DO NOT BUILD YET verdict arose from an empty IDEA. Reconciliation fills it from accepted decisions and records PROCEED WITH FIXES. The independent owner pause still applies. Artifacts remain Draft because implementation/evaluation reconciliation has not occurred; do not confuse this with unsettled product preferences.

## Verification boundary

The engine checks document integrity, not application completeness. The committed documentation set is validated separately from pre-existing local untracked research/plan files. Full-workspace checks can also report those files' historical style/manifest issues. Preserve them; do not promote them into the approved suite or silently rewrite them to obtain a clean check.

No application tests, dependency installation, cloud provisioning or deployment verification were performed for this reconciliation. QAD, CLR, AIA and OPS explicitly retain unmet release evidence. Consult the newest LOG row for the exact documentation-check scope/result.

## Preserve local work

Current project remote: `https://github.com/Axon-Enjin/nvidia-best-apps-and-agents.git`; branch at reconciliation: `review/fmd-product-framing`. Prior main merge `51e4535` preserved local work; accepted root documents/checklist were committed as `b2919bf`. These are historical coordinates, not reset instructions.

Untracked provisional files include `sentinel/`, `tests/`, `migrations/`, `pyproject.toml`, `uv.lock`, `alembic.ini`, `.env.example`, `.gitignore`, `output/`, and local research/walkthrough/old plans under `docs/`. They are not included in the reconciliation commit and may be absent from a fresh clone.

The old prototype has single-XML/chart assumptions and shared-token access. Its browser CSS/JavaScript and deploy packaging were incomplete; prior dependency sync failed. Assess it against the canonical requirements when implementation resumes. Do not call it installed, deployable or passing from historical tests.

Optional historical local references:
- `docs/sentinel-node-claims-interoperability-research.md`: export/form research, not compatibility proof.
- `docs/sentinel-node-walkthrough.html`: fictional explanation, not the working app.
- `docs/superpowers/plans/2026-10-21-sentinel-prototype.md`: earlier implementation proposal, superseded by the accepted scope.

[Hackathon-AI-Agent-Research.md](Hackathon-AI-Agent-Research.md), [HACKATHON.md](HACKATHON.md), [ORG.md](ORG.md) and [PROMPT.md](PROMPT.md) provide historical/event context. Recheck official rules before a current submission claim. Research prices, market sizes and automation assumptions are not product facts.

## Next session

Read the current state and canonical requirements. FMD access and product reconciliation are no longer blockers. Wait for an explicit instruction to resume application work; then verify build choices, assess the scaffold and implement the correction loop in checklist order. Missing hospital access does not block synthetic-only development; it does block claiming an operational hospital pilot.
