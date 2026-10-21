import hashlib
import time

from fastapi import HTTPException
from sqlalchemy import select, update

from sentinel.audit import audit_bundle
from sentinel.db import Claim, Job, Review, new_id


def enqueue(session, xml_text, xml_name, chart_text="", chart_name="", chart_blob=None,
            chart_error=None, use_model=False, claim_id=None, sample_key=None, actor_id=None):
    preview = audit_bundle(xml_text, chart_text, chart_error)
    reference = preview["fields"].get("claim_id") or xml_name
    patient_id = preview["fields"].get("patient_id", "")
    job_id = new_id()
    if claim_id:
        claim = session.get(Claim, claim_id)
        if not claim:
            raise HTTPException(404, "Claim not found.")
        previous = session.get(Job, claim.latest_job_id)
        if previous and previous.status in {"queued", "running"}:
            raise HTTPException(409, "An audit is already queued or running for this claim.")
        if previous and previous.result:
            previous_fields = previous.result.get("fields", {})
            if any(previous_fields.get(key) and preview["fields"].get(key) and
                   previous_fields[key] != preview["fields"][key] for key in ("claim_id", "patient_id")):
                raise HTTPException(409, "The claim or patient identifier changed. Import this bundle as a new claim.")
        updated = session.execute(update(Claim).where(Claim.id == claim.id,
                                                      Claim.latest_job_id == claim.latest_job_id).values(latest_job_id=job_id))
        if updated.rowcount != 1:
            raise HTTPException(409, "Another audit was started. Refresh the claim and try again.")
    else:
        claim = Claim(id=new_id(), reference=reference[:200], patient_id=patient_id[:200],
                      latest_job_id=job_id, sample_key=sample_key, assignee_id=actor_id)
        session.add(claim)
        session.flush()
    job = Job(id=job_id, claim_id=claim.id, xml_text=xml_text, xml_name=xml_name, chart_text=chart_text,
              chart_name=chart_name, chart_blob=chart_blob, chart_error=chart_error, use_model=use_model,
              xml_hash=hashlib.sha256(xml_text.encode()).hexdigest(),
              chart_hash=hashlib.sha256(chart_blob).hexdigest() if chart_blob else None)
    session.add(job)
    session.commit()
    return {"id": claim.id, "job_id": job_id}


def job_summary(job):
    return {"id": job.id, "claim_id": job.claim_id, "status": job.status, "created_at": job.created_at,
            "finished_at": job.finished_at, "attempts": job.attempts, "use_model": job.use_model,
            "xml_name": job.xml_name, "chart_name": job.chart_name, "result": job.result, "error": job.error}


def job_detail(session, job):
    reviews = session.scalars(select(Review).where(Review.job_id == job.id)).all()
    return {**job_summary(job), "xml_text": job.xml_text, "chart_text": job.chart_text,
            "xml_hash": job.xml_hash, "chart_hash": job.chart_hash,
            "reviews": {r.finding_id: {"decision": r.decision, "note": r.note, "updated_at": r.updated_at, "actor_id": r.actor_id}
                        for r in reviews}}


def save_review(session, job_id, finding_id, decision, note, actor_id=None):
    job = session.get(Job, job_id)
    if not job or not job.result or not any(f["id"] == finding_id for f in job.result["findings"]):
        raise HTTPException(404, "Finding not found in this audit.")
    review = session.get(Review, (job_id, finding_id))
    if review is None:
        review = Review(job_id=job_id, finding_id=finding_id)
        session.add(review)
    review.decision, review.note, review.updated_at = decision, note.strip(), time.time()
    review.actor_id = actor_id
    session.commit()
    return {"decision": review.decision, "note": review.note, "updated_at": review.updated_at}
