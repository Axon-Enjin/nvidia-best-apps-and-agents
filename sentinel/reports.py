"""Transactional closeout and escaped exports of immutable internal review records."""
import csv
import io
import json
import time
from html import escape

from fastapi import HTTPException
from sqlalchemy import select

from sentinel.accounts import require_case_access, visible_claims
from sentinel.bundles import ordered_documents
from sentinel.db import AccessEvent, Claim, ReportSnapshot, ReviewEvent
from sentinel.profile import RULE_VERSION
from sentinel.review import fence_case, review_state

PROVENANCE = "Synthetic patient records; internal sample profile; no payer approval."
READY = "Ready for final submission review"


def report_public(report, case):
    return {"id":report.id, "case_id":report.claim_id, "bundle_id":report.bundle_id,
            "revision":report.revision, "created_at":report.created_at, "snapshot":report.snapshot,
            "stale":report.revision != case.revision or report.bundle_id != case.current_bundle_id or report.rule_version != RULE_VERSION}


def finalize_review(db, actor, case_id, bundle_version, rule_version, expected_revision):
    with db.session() as session:
        case = session.get(Claim, case_id)
        require_case_access(actor, case)
        if not actor.id or rule_version != RULE_VERSION:
            raise HTTPException(409, "Named reviewer and current rules are required.")
        if case.state == READY:
            raise HTTPException(409, "This review already has a final record. Open it from reports.")
        # The write lock/CAS is acquired before reading guards and retained through publication.
        fence_case(session, actor, case, expected_revision, bundle_version)
        state = review_state(session, case)
        if not state["can_finalize"]:
            raise HTTPException(409, {"message":"Resolve current-version blockers before completing review.", "blockers":state["blockers"]})
        for check in state["checks"]:
            if any(a["bundle_id"] != case.current_bundle_id for a in check["anchors"]):
                raise HTTPException(409, "Evidence belongs to another source version.")
        state["checks"][9].update(status="passed", blocking_reasons=[])
        snapshot = {"case_id":case.id, "claim_ref":case.reference, "patient_id":case.patient_id,
                    "bundle_id":case.current_bundle_id, "bundle_version":state["bundle_version"], "rule_version":RULE_VERSION,
                    "revision":case.revision, "actor_id":actor.id, "actor":actor.username, "completed_at":time.time(),
                    "provenance":PROVENANCE, "outcome":READY, "checks":state["checks"], "coverage":state["coverage"],
                    "model_status":state["model_status"], "findings":state["findings"], "events":state["events"], "tasks":state["tasks"],
                    "documents":[{"id":d.id, "type":d.declared_type, "sha256":d.source_hash} for d in ordered_documents(session, case.current_bundle_id)]}
        report = ReportSnapshot(claim_id=case.id, bundle_id=case.current_bundle_id, rule_version=RULE_VERSION,
                                revision=case.revision, actor_id=actor.id, snapshot=snapshot)
        session.add(report)
        case.state = READY
        session.add(ReviewEvent(claim_id=case.id, bundle_id=case.current_bundle_id, rule_version=RULE_VERSION,
                                revision=case.revision, actor_id=actor.id, actor_name=actor.username,
                                action="finalized", payload={"reason":"Current source/rule checks and correction tasks resolved."}))
        session.flush()
        result = report_public(report, case)
        session.commit()
        return result


def get_report(db, actor, report_id):
    with db.session() as session:
        report = session.get(ReportSnapshot, report_id)
        require_case_access(actor, session.get(Claim, report.claim_id) if report else None)
        return report_public(report, session.get(Claim, report.claim_id))


def csv_cell(value):
    text = str(value)
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r", "\n")) else text


def export_report(db, actor, report_id, format):
    with db.session() as session:
        report = session.get(ReportSnapshot, report_id)
        case = session.get(Claim, report.claim_id) if report else None
        require_case_access(actor, case)
        if report_public(report, case)["stale"]:
            raise HTTPException(409, "This historical record is stale. Complete the current review before exporting.")
        snapshot = report.snapshot
        if format == "csv":
            output = io.StringIO(newline="")
            writer = csv.writer(output)
            writer.writerow(["record", "field", "value"])
            for key, value in snapshot.items():
                if not isinstance(value, (list, dict)):
                    writer.writerow(["review", csv_cell(key), csv_cell(value)])
            for check in snapshot["checks"]:
                writer.writerow(["check", check["id"], csv_cell(json.dumps(check, ensure_ascii=False))])
            for event in snapshot["events"]:
                writer.writerow(["event", event["action"], csv_cell(event["payload"].get("reason", ""))])
            for doc in snapshot["documents"]:
                writer.writerow(["source", doc["id"], csv_cell(json.dumps(doc))])
            content = output.getvalue().encode("utf-8-sig")
        elif format == "html":
            # No active content or external assets. Browser Print exports this standalone record.
            content = ("<!doctype html><html lang='en'><meta charset='utf-8'><title>Sentinel Claims internal review</title>"
                       "<h1>Internal review record</h1><p>Use your browser’s Print command to print this record.</p>"
                       f"<p>{escape(PROVENANCE)}</p><h2>{escape(snapshot['claim_ref'])}</h2>"
                       f"<p>{escape(READY)}</p><pre>{escape(json.dumps(snapshot, indent=2, ensure_ascii=False))}</pre></html>").encode()
        else:
            raise HTTPException(422, "Choose CSV or printable HTML.")
        session.add(AccessEvent(actor_id=actor.id, action="report_exported", resource_id=report.id, detail={"format":format}))
        session.commit()
        return content


def metrics(db, actor):
    with db.session() as session:
        cases = session.scalars(select(Claim).where(visible_claims(actor, Claim))).all()
        ids = [c.id for c in cases]
        events = session.scalars(select(ReviewEvent).where(ReviewEvent.claim_id.in_(ids)).order_by(ReviewEvent.created_at)).all()
        opened = {e.id:e for e in events if e.action == "correction_created"}
        resolved = {e.payload.get("task_id"):e for e in events if e.action == "correction_resolved"}
        hours = [(e.created_at - opened[id].created_at)/3600 for id,e in resolved.items() if id in opened]
        return {"case_denominator":len(cases), "completed_cases":sum(c.state == READY for c in cases),
                "completion_event_count":sum(e.action == "finalized" for e in events),
                "correction_denominator":len(opened), "resolved_corrections":len(resolved),
                "duration_denominator":len(hours), "mean_correction_hours":sum(hours)/len(hours) if hours else None,
                "queue_cases":sum(c.state != READY for c in cases)}
