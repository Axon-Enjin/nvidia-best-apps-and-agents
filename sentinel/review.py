"""Version-bound human decisions. Sources and published check runs remain immutable."""
import time

from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, update

from sentinel.accounts import require_case_access
from sentinel.bundles import ordered_documents
from sentinel.db import Bundle, Claim, Job, ReviewEvent, new_id
from sentinel.profile import RULE_VERSION, evaluate_profile


class ReviewAction(BaseModel):
    expected_revision: int = Field(ge=0)
    bundle_id: str = Field(min_length=1, max_length=32)
    rule_version: str = Field(max_length=80)
    action: str = Field(max_length=40)
    reason: str = Field(min_length=1, max_length=2000)
    anchors: list[dict] = Field(default_factory=list, max_length=150)
    check_id: str = Field(default="", max_length=10)
    department: str = Field(default="", max_length=200)
    person: str = Field(default="", max_length=200)
    task_id: str = Field(default="", max_length=32)
    expectation_id: str = Field(default="", max_length=32)


def event_public(e):
    return {"id":e.id, "bundle_id":e.bundle_id, "rule_version":e.rule_version, "revision":e.revision,
            "actor_id":e.actor_id, "actor":e.actor_name, "action":e.action, "payload":e.payload, "created_at":e.created_at}


def events_for(session, case_id):
    return session.scalars(select(ReviewEvent).where(ReviewEvent.claim_id == case_id).order_by(ReviewEvent.revision)).all()


def review_state(session, case):
    bundle = session.get(Bundle, case.current_bundle_id) if case.current_bundle_id else None
    events = events_for(session, case.id)
    tasks, expectations = {}, {}
    for e in events:
        p = e.payload
        if e.action == "correction_created":
            tasks[e.id] = {"id":e.id, **p, "status":"open", "bundle_id":e.bundle_id, "created_at":e.created_at}
        elif e.action.startswith("correction_") and p.get("task_id") in tasks:
            tasks[p["task_id"]].update(status={"correction_handoff":"handed_off", "correction_acknowledged":"acknowledged",
                                              "correction_resolved":"resolved", "correction_cancelled":"cancelled"}[e.action], updated_at=e.created_at)
        elif e.action == "extra_expected":
            expectations[e.id] = {"id":e.id, "type":"attachment", "reason":p["reason"], "reviewed":False}
        elif e.action == "extra_withdrawn" and p.get("expectation_id") in expectations:
            expectations[p["expectation_id"]].update(withdrawn=True, role="supervisor", reason=p["reason"])
        elif e.action == "extra_reviewed" and e.bundle_id == case.current_bundle_id and e.rule_version == RULE_VERSION:
            if p.get("expectation_id") in expectations:
                expectations[p["expectation_id"]]["reviewed"] = True
    docs = ordered_documents(session, bundle.id) if bundle else []
    profile_bundle = {"id":bundle.id if bundle else "", "manifest":bundle.manifest if bundle else {},
                      "expectations":list(expectations.values()), "documents":[
                          {"id":d.id, "type":d.declared_type, "sha256":d.source_hash, "status":d.status,
                           "page_count":d.page_count, "problems":d.problems, "extraction":d.extraction} for d in docs]}
    result = evaluate_profile(profile_bundle)
    current = [e for e in events if e.bundle_id == case.current_bundle_id and e.rule_version == RULE_VERSION]
    cutoff = max((e.revision for e in current if e.action == "recheck"), default=-1)
    current = [e for e in current if e.revision > cutoff]
    p07 = next((e for e in reversed(current) if e.action == "manual_p07"), None)
    ack = next((e for e in reversed(current) if e.action == "supervisor_ack"), None)
    if p07 and ack and ack.revision > p07.revision and ack.actor_id != p07.actor_id:
        result["checks"][6].update(status="passed", blocking_reasons=[])
    if any(e.action == "manual_p08" for e in current):
        result["checks"][7].update(status="passed", blocking_reasons=[])
    for finding in result["findings"]:
        finding["resolution_status"] = next(c["status"] for c in result["checks"] if c["id"] == finding["id"])
    # New sources or rule versions never inherit prior manual decisions.
    job = session.get(Job, case.latest_job_id) if case.latest_job_id else None
    processed = bool(job and job.status == "succeeded" and job.result and job.result.get("bundle_id") == case.current_bundle_id and job.result.get("rule_version") == RULE_VERSION)
    blockers = [{"id":c["id"], "reasons":c["blocking_reasons"]} for c in result["checks"][:-1] if c["status"] != "passed"]
    if not processed:
        blockers.append({"id":"processing", "reasons":["Current sources and rule version require a completed local check run."]})
    if any(t["status"] not in {"resolved", "cancelled"} for t in tasks.values()):
        blockers.append({"id":"corrections", "reasons":["Open correction tasks must be resolved or reasonedly cancelled."]})
    return {**result, "revision":case.revision, "bundle_version":bundle.sequence if bundle else None,
            "tasks":list(tasks.values()), "expectations":list(expectations.values()), "events":[event_public(e) for e in events],
            "blockers":blockers, "can_finalize":not blockers}


def fence_case(session, actor, case, expected_revision, bundle_id):
    require_case_access(actor, case)
    assignment = True if "supervisor" in actor.roles else Claim.assignee_id == actor.id
    changed = session.execute(update(Claim).where(Claim.id == case.id, Claim.revision == expected_revision,
                              Claim.current_bundle_id == bundle_id, assignment)
                              .values(revision=Claim.revision + 1, state="In review"))
    if changed.rowcount != 1:
        raise HTTPException(409, "Case changed. Refresh before saving; your draft has not overwritten saved work.")
    session.refresh(case)


def validate_anchors(session, bundle_id, anchors, required_types=()):
    if not anchors:
        raise HTTPException(422, "Source evidence is required.")
    covered = set()
    for a in anchors:
        doc = next((d for d in ordered_documents(session, bundle_id) if d.id == a.get("document_id")), None)
        page = a.get("page")
        if not doc or not isinstance(page, int) or isinstance(page, bool) or not 1 <= page <= doc.page_count:
            raise HTTPException(422, "Evidence must reference a page of the current bundle.")
        if doc.status != "readable":
            raise HTTPException(422, "Inspect, confirm or replace unreadable/unmatched evidence first.")
        covered.add(doc.declared_type)
    if not set(required_types) <= covered:
        raise HTTPException(422, "Compare every required source before recording this manual review.")


def record_review(db, actor, case_id, expected_revision, action):
    if not actor.id:
        raise HTTPException(403, "Named responsibility is required.")
    with db.session() as session:
        case = session.get(Claim, case_id)
        require_case_access(actor, case)
        if not action.get("bundle_id") or action.get("rule_version") != RULE_VERSION:
            raise HTTPException(409, "Source and rule versions must be current.")
        fence_case(session, actor, case, expected_revision, action["bundle_id"])
        before = review_state(session, case)
        kind, reason = action.get("action"), action.get("reason", "").strip()
        if not reason or len(reason) > 2000:
            raise HTTPException(422, "A specific reason is required.")
        payload = {k:v for k,v in action.items() if k not in {"expected_revision", "action", "bundle_id", "rule_version"}}
        payload["reason"] = reason
        if kind in {"manual_p07", "manual_p08", "dismissed", "correction_created", "extra_reviewed"}:
            required = {"manual_p07":("cf2", "cf4", "cf5", "discharge"), "manual_p08":("cf2", "cf4", "cf5", "csf"), "extra_reviewed":("attachment",)}.get(kind, ())
            validate_anchors(session, case.current_bundle_id, action.get("anchors", []), required)
        if kind == "manual_p08":
            for doc in ordered_documents(session, case.current_bundle_id):
                if doc.declared_type in {"cf2", "cf4", "cf5", "csf"} and any(not doc.extraction.get("fields", {}).get(key) for key in ("mark", "printed_name", "signed_date")):
                    raise HTTPException(409, "Missing mark, printed signatory or date requires a completed source.")
        elif kind == "supervisor_ack":
            if "supervisor" not in actor.roles:
                raise HTTPException(403, "A separate supervisor acknowledgement is required.")
            manual = next((e for e in reversed(before["events"]) if e["action"] == "manual_p07" and e["bundle_id"] == case.current_bundle_id and e["rule_version"] == RULE_VERSION), None)
            if not manual or manual["actor_id"] == actor.id:
                raise HTTPException(409, "A different named reviewer must record the current manual comparison first.")
        elif kind == "dismissed":
            if action.get("check_id") != "P07":
                raise HTTPException(422, "Deterministic source blockers cannot be dismissed. Correct extraction or obtain revised sources.")
        elif kind == "correction_created":
            if action.get("check_id") not in {f"P{i:02}" for i in range(1, 10)} or not action.get("department", "").strip() or not action.get("person", "").strip():
                raise HTTPException(422, "Identify the check, responsible department and person.")
        elif kind in {"correction_handoff", "correction_acknowledged", "correction_resolved", "correction_cancelled"}:
            task = next((t for t in before["tasks"] if t["id"] == action.get("task_id")), None)
            if not task or task["status"] in {"resolved", "cancelled"}:
                raise HTTPException(409, "Correction task is absent or already closed.")
            required_status = {"correction_handoff":"open", "correction_acknowledged":"handed_off", "correction_resolved":"acknowledged"}.get(kind)
            if required_status and task["status"] != required_status:
                raise HTTPException(409, "Record handoff and acknowledgement before resolving.")
            if kind == "correction_resolved" and (task["bundle_id"] == case.current_bundle_id or not next(c for c in before["checks"] if c["id"] == task["check_id"])["status"] == "passed"):
                raise HTTPException(409, "Import and recheck corrected sources before resolving this discrepancy.")
        elif kind in {"extra_withdrawn", "extra_reviewed"}:
            if not any(e["id"] == action.get("expectation_id") and not e.get("withdrawn") for e in before["expectations"]):
                raise HTTPException(422, "Expected extra attachment not found.")
            if kind == "extra_withdrawn" and "supervisor" not in actor.roles:
                raise HTTPException(403, "Only a supervisor may withdraw a mistakenly expected extra attachment.")
        elif kind == "recheck":
            job_id = new_id()
            session.add(Job(id=job_id, claim_id=case.id, bundle_id=case.current_bundle_id, xml_name="", xml_text="", xml_hash=""))
            case.latest_job_id = job_id
        elif kind not in {"manual_p07", "manual_p08", "extra_expected"}:
            raise HTTPException(422, "Unknown review action.")
        event = ReviewEvent(claim_id=case.id, bundle_id=case.current_bundle_id, rule_version=RULE_VERSION,
                            revision=case.revision, actor_id=actor.id, actor_name=actor.username, action=kind, payload=payload, created_at=time.time())
        session.add(event)
        session.flush()
        result = review_state(session, case)
        session.commit()
        return result
