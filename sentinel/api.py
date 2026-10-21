import hashlib
import hmac
import json
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from starlette.middleware.trustedhost import TrustedHostMiddleware

from sentinel.config import Settings, migrate
from sentinel.db import Claim, Database, Job, Review
from sentinel.documents import MAX_FILE_BYTES, extract_chart
from sentinel.samples import bundle_zip, samples
from sentinel.service import enqueue, job_detail, job_summary, save_review
from sentinel.worker import worker_loop

STATIC = Path(__file__).parent / "static"


class BodyLimitMiddleware:
    """Bound the entire multipart body before a framework parser can spool it."""
    def __init__(self, app, maximum=6 * 1024 * 1024):
        self.app, self.maximum = app, maximum

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            return await self.app(scope, receive, send)
        parts, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body = message.get("body", b"")
            size += len(body)
            if size > self.maximum:
                response = JSONResponse({"detail": "Upload is too large. XML is limited to 256 KB and charts to 5 MB."}, status_code=413)
                return await response(scope, receive, send)
            parts.append(body)
            if not message.get("more_body"):
                break
        delivered = False

        async def bounded_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": b"".join(parts), "more_body": False}
            return await receive()
        return await self.app(scope, bounded_receive, send)


class ReviewInput(BaseModel):
    decision: str = Field(pattern="^(accepted|dismissed|pending)$")
    note: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def reason_for_dismissal(self):
        if self.decision == "dismissed" and not self.note.strip():
            raise ValueError("Explain why this finding is being dismissed.")
        return self


class LoginInput(BaseModel):
    token: str = Field(max_length=512)


def create_app(settings: Settings | None = None, database: Database | None = None):
    settings = settings or Settings.from_env()
    settings.validate()
    db = database or Database(settings.database_url)
    stop = threading.Event()

    @asynccontextmanager
    async def lifespan(_):
        if settings.auto_migrate:
            migrate(settings.database_url)
        thread = None
        if settings.embedded_worker:
            thread = threading.Thread(target=worker_loop, args=(db, settings, stop), daemon=True)
            thread.start()
        yield
        stop.set()
        if thread:
            thread.join(timeout=2)
        if database is None:
            db.engine.dispose()

    app = FastAPI(title="Sentinel Node", version="0.1.0", lifespan=lifespan,
                  docs_url=None if settings.environment == "production" else "/api/docs",
                  redoc_url=None, openapi_url="/api/openapi.json")
    app.state.db, app.state.settings = db, settings
    app.add_middleware(BodyLimitMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))

    def cookie_value():
        return hmac.new(settings.access_token.encode(), b"sentinel-workspace-session-v1", hashlib.sha256).hexdigest()

    def authorized(request):
        if not settings.access_token:
            return True
        cookie = request.cookies.get("sentinel_session", "")
        bearer = request.headers.get("authorization", "")
        return hmac.compare_digest(cookie, cookie_value()) or hmac.compare_digest(bearer, "Bearer " + settings.access_token)

    @app.middleware("http")
    async def access_and_headers(request: Request, call_next):
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            if origin:
                parsed = urlsplit(origin)
                if (parsed.scheme, parsed.netloc) != (request.url.scheme, request.url.netloc):
                    return JSONResponse({"detail": "Cross-origin changes are not allowed."}, status_code=403)
        if request.url.path.startswith("/api/") and request.url.path != "/api/session" and not authorized(request):
            return JSONResponse({"detail": "Unlock this workspace to continue."}, status_code=401)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/healthz")
    def health():
        with db.session() as session:
            session.execute(text("SELECT 1"))
        return {"status": "ok"}

    @app.get("/api/session")
    def session_status(request: Request):
        return {"authenticated": authorized(request), "protected": bool(settings.access_token)}

    @app.post("/api/session")
    def login(body: LoginInput):
        if settings.access_token and not hmac.compare_digest(body.token, settings.access_token):
            raise HTTPException(401, "Workspace token is incorrect.")
        response = JSONResponse({"authenticated": True})
        response.set_cookie("sentinel_session", cookie_value(), httponly=True, secure=settings.environment == "production",
                            samesite="strict", max_age=60 * 60 * 12)
        return response

    @app.delete("/api/session")
    def logout():
        response = JSONResponse({"authenticated": False})
        response.delete_cookie("sentinel_session", secure=settings.environment == "production", httponly=True, samesite="strict")
        return response

    @app.get("/api/config")
    def config():
        return {"model_configured": bool(settings.nebius_api_key), "model": settings.nebius_model,
                "protected": bool(settings.access_token), "format": "SentinelClaim v1",
                "rule_version": "sentinel-bundle/1.0"}

    @app.get("/api/claims")
    def list_claims(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), q: str = Query("", max_length=200),
                    view: str = Query("all", pattern="^(all|needs_review|incomplete|no_findings)$")):
        with db.session() as session:
            condition = Claim.reference.contains(q, autoescape=True) | Claim.patient_id.contains(q, autoescape=True)
            if view != "all":
                condition &= Job.result["outcome"].as_string() == view
            total = session.scalar(select(func.count()).select_from(Claim).join(Job, Claim.latest_job_id == Job.id).where(condition))
            rows = session.execute(select(Claim, Job.id, Job.status, Job.result, Job.use_model)
                                   .join(Job, Claim.latest_job_id == Job.id).where(condition)
                                   .order_by(Claim.created_at.desc(), Claim.id).offset(offset).limit(limit)).all()
            items = []
            job_ids = [row[1] for row in rows]
            all_reviews = session.scalars(select(Review).where(Review.job_id.in_(job_ids))).all() if job_ids else []
            for claim, job_id, status, result, use_model in rows:
                reviews = [review for review in all_reviews if review.job_id == job_id]
                decisions = {r.finding_id: r.decision for r in reviews}
                findings = (result or {}).get("findings", [])
                items.append({"id": claim.id, "reference": claim.reference, "patient_id": claim.patient_id,
                              "sample": bool(claim.sample_key), "created_at": claim.created_at,
                              "job_id": job_id, "status": status, "outcome": (result or {}).get("outcome"),
                              "finding_count": len(findings),
                              "pending_count": sum(decisions.get(f["id"], "pending") == "pending" for f in findings),
                              "model_status": (result or {}).get("model_status"), "use_model": use_model})
            return {"items": items, "total": total, "limit": limit, "offset": offset}

    @app.get("/api/stats")
    def stats():
        with db.session() as session:
            rows = session.execute(select(Job.status, Job.result["outcome"].as_string(), func.count())
                                   .join(Claim, Claim.latest_job_id == Job.id)
                                   .group_by(Job.status, Job.result["outcome"].as_string())).all()
            counts = {"all": 0, "needs_review": 0, "incomplete": 0, "no_findings": 0, "processing": 0}
            for status, outcome, count in rows:
                counts["all"] += count
                key = "processing" if status in {"queued", "running"} else outcome or "incomplete"
                counts[key] += count
            return counts

    @app.get("/api/claims/{claim_id}")
    def claim_detail(claim_id: str):
        with db.session() as session:
            claim = session.get(Claim, claim_id)
            if not claim:
                raise HTTPException(404, "Claim not found.")
            latest = session.get(Job, claim.latest_job_id)
            history = session.scalars(select(Job).where(Job.claim_id == claim.id).order_by(Job.created_at.desc())).all()
            return {"id": claim.id, "reference": claim.reference, "patient_id": claim.patient_id,
                    "sample": bool(claim.sample_key), "latest": job_detail(session, latest),
                    "history": [job_summary(job) for job in history]}

    async def receive_bundle(claim_file, chart_file, use_model, claim_id=None):
        if use_model and not settings.nebius_api_key:
            raise HTTPException(409, "Nebius is not configured. Use local checks or configure the server API key.")
        if not (claim_file.filename or "").lower().endswith(".xml"):
            raise HTTPException(400, "The draft claim must be an .xml file.")
        content = await claim_file.read(262145)
        if len(content) > 262144:
            raise HTTPException(413, "Claim XML must be 256 KB or smaller.")
        try:
            xml_text = content.decode("utf-8-sig")
            if "\x00" in xml_text:
                raise UnicodeError
        except UnicodeError as exc:
            raise HTTPException(400, "Claim XML must be UTF-8 text.") from exc
        if not xml_text.strip():
            raise HTTPException(400, "The claim XML is empty.")
        chart_text, chart_error, chart_blob, chart_name = "", None, None, ""
        if chart_file and chart_file.filename:
            chart_name = clean_name(chart_file.filename)
            chart_blob = await chart_file.read(MAX_FILE_BYTES + 1)
            if len(chart_blob) > MAX_FILE_BYTES:
                raise HTTPException(413, "Chart must be 5 MB or smaller.")
            if not chart_name.lower().endswith((".pdf", ".txt")):
                raise HTTPException(400, "Chart must be a PDF or UTF-8 text file.")
            try:
                chart_text = extract_chart(chart_blob, chart_name)
            except ValueError as exc:
                chart_error = str(exc)
        with db.session() as session:
            return enqueue(session, xml_text, clean_name(claim_file.filename), chart_text, chart_name,
                           chart_blob, chart_error, use_model, claim_id=claim_id)

    @app.post("/api/claims", status_code=202)
    async def import_claim(claim_file: UploadFile = File(...), chart_file: UploadFile | None = File(None),
                           use_model: bool = Form(False)):
        return await receive_bundle(claim_file, chart_file, use_model)

    @app.post("/api/claims/{claim_id}/rerun", status_code=202)
    async def rerun(claim_id: str, claim_file: UploadFile = File(...), chart_file: UploadFile | None = File(None),
                    use_model: bool = Form(False)):
        return await receive_bundle(claim_file, chart_file, use_model, claim_id)

    @app.get("/api/jobs/{job_id}")
    def get_job(job_id: str):
        with db.session() as session:
            job = session.get(Job, job_id)
            if not job:
                raise HTTPException(404, "Audit not found.")
            return job_detail(session, job)

    @app.put("/api/jobs/{job_id}/reviews/{finding_id}")
    def review(job_id: str, finding_id: str, body: ReviewInput):
        with db.session() as session:
            try:
                return save_review(session, job_id, finding_id, body.decision, body.note)
            except IntegrityError as exc:
                session.rollback()
                raise HTTPException(409, "Another reviewer saved this finding. Refresh and try again.") from exc

    @app.get("/api/jobs/{job_id}/report")
    def report(job_id: str):
        detail = get_job(job_id)
        payload = {k: v for k, v in detail.items() if k not in {"xml_text", "chart_text"}}
        return Response(json.dumps(payload, indent=2), media_type="application/json",
                        headers={"Content-Disposition": f'attachment; filename="sentinel-audit-{job_id}.json"'})

    @app.get("/api/jobs/{job_id}/source/{kind}")
    def source(job_id: str, kind: str):
        if kind not in {"claim", "chart"}:
            raise HTTPException(404, "Source not found.")
        with db.session() as session:
            job = session.get(Job, job_id)
            if not job:
                raise HTTPException(404, "Audit not found.")
            if kind == "claim":
                return Response(job.xml_text, media_type="application/xml",
                                headers={"Content-Disposition": 'attachment; filename="claim.xml"'})
            if not job.chart_blob:
                raise HTTPException(404, "No chart was attached.")
            extension = "pdf" if job.chart_name.lower().endswith(".pdf") else "txt"
            return Response(job.chart_blob, media_type="application/octet-stream",
                            headers={"Content-Disposition": f'attachment; filename="chart.{extension}"'})

    @app.post("/api/samples", status_code=202)
    def load_samples():
        identifiers = []
        for bundle in samples():
            with db.session() as session:
                existing = session.scalar(select(Claim).where(Claim.sample_key == bundle["key"]))
                if existing:
                    identifiers.append(existing.id)
                    continue
                try:
                    created = enqueue(session, bundle["xml"], "claim.xml", bundle["chart"], "chart.txt",
                                      bundle["chart"].encode(), sample_key=bundle["key"])
                    identifiers.append(created["id"])
                except IntegrityError:
                    session.rollback()
                    identifiers.append(session.scalar(select(Claim.id).where(Claim.sample_key == bundle["key"])))
        return {"ids": identifiers}

    @app.get("/api/samples/bundles.zip")
    def download_samples():
        return Response(bundle_zip(), media_type="application/zip",
                        headers={"Content-Disposition": 'attachment; filename="sentinel-synthetic-bundles.zip"'})

    @app.get("/")
    def index():
        return FileResponse(STATIC / "index.html")

    # Static sources contain no secrets or uploaded documents.
    STATIC.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


def clean_name(filename):
    return filename.replace("\\", "/").rsplit("/", 1)[-1][:200]


# Uvicorn's factory entry point avoids import-time DB or environment side effects.
def app_factory():
    return create_app()
