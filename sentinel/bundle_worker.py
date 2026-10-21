"""Extract committed quarantined originals, then publish under the worker lease."""
import time

from fastapi import HTTPException
from sqlalchemy import update

from sentinel.bundles import MAX_BUNDLE_PAGES, REQUIRED_TYPES, ordered_documents
from sentinel.db import Bundle, Claim, Document, Job
from sentinel.documents import extract_original
from sentinel.storage import PrivateStorage


def process_bundle_job(db, settings, job_id, token):
    with db.session() as session:
        job = session.get(Job, job_id)
        bundle = session.get(Bundle, job.bundle_id)
        case = session.get(Claim, bundle.claim_id)
        documents = ordered_documents(session, bundle.id)
    extracted = []
    storage = PrivateStorage(settings)
    for document in documents:
        try:
            content = storage.read(document.object_key, document.source_hash)
            result = extract_original(content)
        except HTTPException:
            result = {"status": "unreadable", "content_type": "application/octet-stream", "page_count": 0,
                      "problems": ["Original source is missing or damaged; recovery is required."],
                      "extraction": {"fields": {}, "anchors": [], "pages": []}}
        if result["status"] == "readable":
            mismatches = [field for field, value in {"facility_id": case.facility_id, "encounter_ref": case.encounter_ref,
                         "claim_ref": case.reference, "patient_id": case.patient_id}.items()
                          if result["extraction"]["fields"].get(field) != value]
            if mismatches:
                result["status"] = "unmatched"
                result["problems"] = mismatches
        extracted.append((document, result))
    over_limit = sum(result["page_count"] for _, result in extracted) > MAX_BUNDLE_PAGES
    coverage_complete = (not over_limit and set(REQUIRED_TYPES) <= {doc.declared_type for doc in documents}
                         and all(result["status"] == "readable" for _, result in extracted))
    result = {"rule_version": "SAMPLE-ADULT-MEDICAL-1/pending", "bundle_id": bundle.id,
              "fields": {"claim_id": case.reference, "patient_id": case.patient_id},
              "model_status": "not_run_offline" if settings.network_mode == "offline" else "not_requested",
              "profile_status": "not_evaluated", "outcome": "incomplete", "findings": [],
              "checks": [{"id": "P02", "label": "Bundle content coverage", "status": "passed" if coverage_complete else "incomplete"}],
              "coverage": [{"document_id": doc.id, "type": doc.declared_type, "status": parsed["status"],
                            "problems": parsed["problems"]} for doc, parsed in extracted]}
    with db.session() as session:
        published = session.execute(update(Job).where(Job.id == job_id, Job.status == "running", Job.lease_token == token)
                                    .values(status="succeeded", result=result, finished_at=time.time(),
                                            lease_token=None, lease_until=None))
        if published.rowcount:
            for document, parsed in extracted:
                session.execute(update(Document).where(Document.id == document.id).values(**parsed))
            session.execute(update(Bundle).where(Bundle.id == bundle.id).values(
                status="limits_exceeded" if over_limit else "processed" if coverage_complete else "incomplete"))
        session.commit()
