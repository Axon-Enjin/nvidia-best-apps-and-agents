"""Durable leased jobs. Run separately to scale audit throughput independently of the API."""

import logging
import threading
import time
import uuid

from sqlalchemy import and_, or_, select, update

from sentinel.audit import audit_bundle, outcome_for
from sentinel.config import Settings
from sentinel.db import Claim, Database, Job
from sentinel.inference import review_with_nebius

log = logging.getLogger(__name__)
LEASE_SECONDS = 300


def claim_job(db: Database) -> tuple[str, str] | None:
    now = time.time()
    eligible = or_(Job.status == "queued", and_(Job.status == "running", Job.lease_until < now))
    with db.session() as session:
        candidate = session.scalar(select(Job.id).where(eligible).order_by(Job.created_at).limit(1))
        if candidate is None:
            return None
        token = uuid.uuid4().hex
        updated = session.execute(update(Job).where(Job.id == candidate, eligible).values(
            status="running", lease_token=token, lease_until=now + LEASE_SECONDS, attempts=Job.attempts + 1))
        session.commit()
        return (candidate, token) if updated.rowcount == 1 else None


def process_one(db: Database, settings: Settings) -> bool:
    lease = claim_job(db)
    if lease is None:
        return False
    job_id, token = lease
    with db.session() as session:
        job = session.get(Job, job_id)
        if job.bundle_id:
            from sentinel.bundle_worker import process_bundle_job
            process_bundle_job(db, settings, job_id, token)
            return True
        result = None
        error = None
        try:
            result = audit_bundle(job.xml_text, job.chart_text, job.chart_error)
            if job.use_model:
                if settings.network_mode != "online":
                    result["model_status"] = "not_run_offline"
                    result["outcome"] = "incomplete"
                    result["checks"].append({"label": "Remote evidence review", "status": "incomplete"})
                    result["findings"].append({"id": "model_offline", "code": "model_offline",
                                              "category": "completeness", "severity": "blocking",
                                              "title": "Remote review did not run offline",
                                              "explanation": "Local checks are saved. No automated narrative clearance was issued.",
                                              "claim_quote": "", "chart_quote": "", "rule": "offline-coverage/1.0"})
                elif result["outcome"] == "incomplete":
                    result["model_status"] = "skipped_incomplete"
                else:
                    try:
                        model_findings, metadata = review_with_nebius(job.xml_text, job.chart_text, settings)
                        result["findings"].extend(model_findings)
                        result["model_status"] = "completed"
                        result["model_name"] = metadata["model"]
                        result["model_usage"] = metadata["usage"]
                        result["outcome"] = outcome_for(result["findings"])
                        result["checks"].append({"label": "Nemotron evidence review", "status": "flagged" if model_findings else "passed"})
                    except Exception:
                        # Never log source text, credentials, or raw provider response bodies.
                        result["model_status"] = "failed"
                        result["model_name"] = settings.nebius_model
                        result["outcome"] = "incomplete"
                        result["checks"].append({"label": "Nemotron evidence review", "status": "incomplete"})
                        result["findings"].append({"id": "model_unavailable", "code": "model_unavailable",
                                                  "category": "completeness", "severity": "blocking",
                                                  "title": "Requested model review did not complete",
                                                  "explanation": "Local checks are preserved. Check provider configuration or retry the audit; no semantic clearance was issued.",
                                                  "claim_quote": "", "chart_quote": "", "rule": "nemotron-review/1.0"})
                        log.warning("Model review failed for job %s", job_id)
        except Exception:
            error = "Audit could not complete. Retry with readable source files."
            log.error("Audit failed for job %s", job_id)
        # Conditional publication fences a worker whose expired lease was reassigned.
        updated = session.execute(update(Job).where(Job.id == job_id, Job.lease_token == token,
                                                    Job.status == "running").values(
            status="failed" if error else "succeeded", result=result, error=error,
            finished_at=time.time(), lease_token=None, lease_until=None))
        if updated.rowcount and result:
            fields = result["fields"]
            values = {}
            if fields.get("claim_id"):
                values["reference"] = fields["claim_id"][:200]
            if fields.get("patient_id"):
                values["patient_id"] = fields["patient_id"][:200]
            if values:
                session.execute(update(Claim).where(Claim.id == job.claim_id, Claim.latest_job_id == job_id).values(**values))
        session.commit()
    return True


def worker_loop(db: Database, settings: Settings, stop: threading.Event):
    while not stop.is_set():
        try:
            if not process_one(db, settings):
                stop.wait(0.5)
        except Exception:
            log.error("Worker could not reach the queue; retrying.")
            stop.wait(2)


def main():
    logging.basicConfig(level=logging.INFO)
    settings = Settings.from_env()
    db = Database(settings.database_url)
    stop = threading.Event()
    try:
        worker_loop(db, settings, stop)
    except KeyboardInterrupt:
        stop.set()
    finally:
        db.engine.dispose()


if __name__ == "__main__":
    main()
