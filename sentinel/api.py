import hashlib
import hmac
import json
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, select, text, update
from sqlalchemy.exc import IntegrityError
from starlette.concurrency import run_in_threadpool
from starlette.middleware.trustedhost import TrustedHostMiddleware

from sentinel.accounts import (
    Actor,
    authenticate,
    csrf_token,
    require_actor,
    require_case_access,
    require_clinical,
    resolve_actor,
    revoke_session,
    visible_claims,
)
from sentinel.bundles import (
    MAX_BUNDLE_BYTES,
    MAX_BUNDLE_FILES,
    MAX_SOURCE_BYTES,
    CaseInput,
    bundle_receipt,
    case_public,
    create_case,
    document_public,
    import_bundle,
    ordered_documents,
    read_source,
)
from sentinel.config import Settings, migrate
from sentinel.confirmations import ConfirmationInput, confirm_extraction
from sentinel.db import AccessEvent, Account, Bundle, Claim, Database, Job, ReportSnapshot, Review
from sentinel.documents import MAX_FILE_BYTES, extract_chart
from sentinel.reports import export_report, finalize_review, get_report, metrics, report_public
from sentinel.review import ReviewAction, record_review, review_state
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
        maximum = MAX_BUNDLE_BYTES + 2 * 1024 * 1024 if scope.get("path", "").endswith("/bundles") else self.maximum
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body = message.get("body", b"")
            size += len(body)
            if size > maximum:
                response = JSONResponse({"detail": "Upload exceeds the supported request size."}, status_code=413)
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
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=1, max_length=128)
    otp: str = Field(default="", max_length=8)


class LegacyLoginInput(BaseModel):
    token: str = Field(max_length=512)


class AssignmentInput(BaseModel):
    assignee_id: str = Field(min_length=32, max_length=32)


class FinalizeInput(BaseModel):
    expected_revision: int = Field(ge=0)
    bundle_id: str = Field(min_length=1, max_length=32)
    rule_version: str = Field(max_length=80)


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

    @app.exception_handler(RequestValidationError)
    async def safe_validation_error(request, exc):
        # Pydantic's default error payload includes raw inputs, including passwords
        # and whole submitted bodies in union errors. Never reflect those values.
        errors = [{"type": error["type"], "loc": error["loc"], "msg": error["msg"]} for error in exc.errors()]
        return JSONResponse({"detail": errors}, status_code=422)

    def cookie_value():
        return hmac.new(settings.access_token.encode(), b"sentinel-workspace-session-v1", hashlib.sha256).hexdigest()

    def legacy_authorized(request):
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
        raw = request.cookies.get("sentinel_session", "")
        if settings.auth_mode == "legacy":
            actor = Actor(None, "Legacy migration", frozenset({"supervisor", "reviewer"}), True) if legacy_authorized(request) else None
        else:
            actor = await run_in_threadpool(resolve_actor, db, settings, raw)
        request.state.actor = actor
        if request.url.path.startswith("/api/"):
            if request.url.path != "/api/session" and not actor:
                return JSONResponse({"detail": "Sign in to continue."}, status_code=401)
            if (settings.auth_mode == "named" and actor and request.method in {"POST", "PUT", "PATCH", "DELETE"}
                    and not (request.url.path == "/api/session" and request.method == "POST")
                    and not hmac.compare_digest(request.headers.get("x-csrf-token", ""), csrf_token(raw))):
                return JSONResponse({"detail": "Refresh your session before saving (CSRF token required)."}, status_code=403)
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
        actor = request.state.actor
        return {"authenticated": bool(actor), "protected": True, "auth_mode": settings.auth_mode,
                "actor": actor.public() if actor else None,
                "csrf_token": csrf_token(request.cookies.get("sentinel_session", "")) if actor else None}

    @app.post("/api/session")
    def login(request: Request, body: LoginInput | LegacyLoginInput):
        if settings.auth_mode == "legacy":
            if not isinstance(body, LegacyLoginInput):
                raise HTTPException(422, "Legacy migration requires a workspace token.")
            if not hmac.compare_digest(body.token, settings.access_token):
                raise HTTPException(401, "Sign-in failed.")
            raw = cookie_value()
            payload = {"authenticated": True, "auth_mode": "legacy"}
        else:
            if not isinstance(body, LoginInput):
                raise HTTPException(422, "Named username/password sign-in is required.")
            actor, raw = authenticate(db, settings, body.username, body.password, body.otp,
                                      request.client.host if request.client else "local",
                                      request.cookies.get("sentinel_session", ""))
            payload = {"authenticated": True, "actor": actor.public(), "csrf_token": csrf_token(raw)}
        response = JSONResponse(payload)
        response.set_cookie("sentinel_session", raw, httponly=True, secure=settings.secure_cookies,
                            samesite="strict", max_age=settings.session_hours * 3600)
        return response

    @app.delete("/api/session")
    def logout(request: Request):
        if settings.auth_mode == "named":
            revoke_session(db, request.cookies.get("sentinel_session", ""))
        response = JSONResponse({"authenticated": False})
        response.delete_cookie("sentinel_session", secure=settings.secure_cookies, httponly=True, samesite="strict")
        return response

    @app.get("/api/config")
    def config():
        return {"model_configured": settings.network_mode == "online" and bool(settings.nebius_api_key),
                "network_mode": settings.network_mode, "model": settings.nebius_model,
                "protected": True, "auth_mode": settings.auth_mode, "format": "SentinelClaim v1",
                "rule_version": "sentinel-bundle/1.0"}

    @app.get("/api/claims")
    def list_claims(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), q: str = Query("", max_length=200),
                    view: str = Query("all", pattern="^(all|needs_review|incomplete|no_findings)$"),
                    actor: Actor = Depends(require_actor)):
        with db.session() as session:
            condition = Claim.reference.contains(q, autoescape=True) | Claim.patient_id.contains(q, autoescape=True)
            condition &= visible_claims(actor, Claim)
            if view != "all":
                condition &= Job.result["outcome"].as_string() == view
            total = session.scalar(select(func.count()).select_from(Claim).outerjoin(Job, Claim.latest_job_id == Job.id).where(condition))
            rows = session.execute(select(Claim, Job.id, Job.status, Job.result, Job.use_model)
                                   .outerjoin(Job, Claim.latest_job_id == Job.id).where(condition)
                                   .order_by(Claim.created_at.desc(), Claim.id).offset(offset).limit(limit)).all()
            items = []
            job_ids = [row[1] for row in rows]
            all_reviews = session.scalars(select(Review).where(Review.job_id.in_(job_ids))).all() if job_ids else []
            for claim, job_id, status, result, use_model in rows:
                reviews = [review for review in all_reviews if review.job_id == job_id]
                decisions = {r.finding_id: r.decision for r in reviews}
                findings = (result or {}).get("findings", [])
                items.append({"id": claim.id, "reference": claim.reference, "patient_id": claim.patient_id,
                              "sample": bool(claim.sample_key), "created_at": claim.created_at, "assignee_id": claim.assignee_id,
                              "revision": claim.revision, "current_bundle_id": claim.current_bundle_id, "state": claim.state,
                              "job_id": job_id, "status": status, "outcome": (result or {}).get("outcome"),
                              "finding_count": len(findings),
                              "pending_count": sum(decisions.get(f["id"], "pending") == "pending" for f in findings),
                              "model_status": (result or {}).get("model_status"), "use_model": use_model})
            return {"items": items, "total": total, "limit": limit, "offset": offset}

    @app.get("/api/stats")
    def stats(actor: Actor = Depends(require_actor)):
        with db.session() as session:
            rows = session.execute(select(Job.status, Job.result["outcome"].as_string(), func.count()).select_from(Claim)
                                   .outerjoin(Job, Claim.latest_job_id == Job.id)
                                   .where(visible_claims(actor, Claim))
                                   .group_by(Job.status, Job.result["outcome"].as_string())).all()
            counts = {"all": 0, "needs_review": 0, "incomplete": 0, "no_findings": 0, "processing": 0}
            for status, outcome, count in rows:
                counts["all"] += count
                key = "processing" if status in {"queued", "running"} else outcome or "incomplete"
                counts[key] += count
            return counts

    @app.get("/api/claims/{claim_id}")
    def claim_detail(claim_id: str, actor: Actor = Depends(require_actor)):
        with db.session() as session:
            claim = session.get(Claim, claim_id)
            require_case_access(actor, claim)
            latest = session.get(Job, claim.latest_job_id) if claim.latest_job_id else None
            history = session.scalars(select(Job).where(Job.claim_id == claim.id).order_by(Job.created_at.desc())).all()
            return {**case_public(claim), "reference": claim.reference,
                    "bundles": [bundle_receipt(session, b) for b in session.scalars(select(Bundle).where(Bundle.claim_id == claim.id).order_by(Bundle.sequence.desc()))],
                    "sample": bool(claim.sample_key), "assignee_id": claim.assignee_id,
                    "latest": job_detail(session, latest) if latest else None,
                    "history": [job_summary(job) for job in history]}

    @app.post("/api/cases", status_code=201)
    def new_case(body: CaseInput, actor: Actor = Depends(require_actor)):
        return create_case(db, actor, body)

    @app.get("/api/claims/{claim_id}/review-state")
    def current_review(claim_id: str, actor: Actor = Depends(require_actor)):
        with db.session() as session:
            case = session.get(Claim, claim_id)
            require_case_access(actor, case)
            return review_state(session, case)

    @app.post("/api/claims/{claim_id}/finalize", status_code=201)
    def finalize(claim_id: str, body: FinalizeInput, actor: Actor = Depends(require_actor)):
        return finalize_review(db, actor, claim_id, body.bundle_id, body.rule_version, body.expected_revision)

    @app.get("/api/claims/{claim_id}/reports")
    def case_reports(claim_id: str, actor: Actor = Depends(require_actor)):
        with db.session() as session:
            case = session.get(Claim, claim_id)
            require_case_access(actor, case)
            return {"items":[report_public(r, case) for r in session.scalars(select(ReportSnapshot).where(ReportSnapshot.claim_id == claim_id).order_by(ReportSnapshot.revision.desc()))]}

    @app.get("/api/reports/{report_id}")
    def report_snapshot(report_id: str, actor: Actor = Depends(require_actor)):
        return get_report(db, actor, report_id)

    @app.get("/api/reports/{report_id}/export")
    def report_export(report_id: str, format: str = Query(pattern="^(csv|html)$"), actor: Actor = Depends(require_actor)):
        content = export_report(db, actor, report_id, format)
        return Response(content, media_type="text/csv" if format == "csv" else "text/html",
                        headers={"Content-Disposition":f'{"attachment" if format == "csv" else "inline"}; filename="sentinel-review-{report_id}.{format}"'})

    @app.get("/api/metrics")
    def event_metrics(actor: Actor = Depends(require_actor)):
        return metrics(db, actor)

    @app.post("/api/claims/{claim_id}/review-events")
    def review_event(claim_id: str, body: ReviewAction, actor: Actor = Depends(require_actor)):
        return record_review(db, actor, claim_id, body.expected_revision, body.model_dump())

    @app.post("/api/claims/{claim_id}/bundles", status_code=202)
    async def upload_version(request: Request, claim_id: str, files: list[UploadFile] = File(...),
                             manifest: str = Form(..., max_length=100000), expected_revision: int = Form(..., ge=0),
                             actor: Actor = Depends(require_actor)):
        with db.session() as session:
            require_case_access(actor, session.get(Claim, claim_id))
        if not 1 <= len(files) <= MAX_BUNDLE_FILES:
            raise HTTPException(413, "A bundle supports up to 30 original files.")
        originals, total = [], 0
        for file in files:
            content = await file.read(MAX_SOURCE_BYTES + 1)
            total += len(content)
            if len(content) > MAX_SOURCE_BYTES or total > MAX_BUNDLE_BYTES:
                raise HTTPException(413, "Limit: 25 MB per file and 100 MB per bundle version.")
            originals.append((unquote(file.filename or "source"), content))
        try:
            def unique_keys(pairs):
                result = {}
                for key, value in pairs:
                    if key in result:
                        raise ValueError("Duplicate manifest field.")
                    result[key] = value
                return result
            parsed = json.loads(manifest, object_pairs_hook=unique_keys)
        except (ValueError, TypeError) as exc:
            raise HTTPException(422, "Manifest must contain valid JSON with unique fields.") from exc
        return await run_in_threadpool(import_bundle, db, settings, actor, claim_id, originals, parsed,
                                        expected_revision, request.headers.get("idempotency-key", ""))

    @app.get("/api/claims/{claim_id}/bundles/{version}")
    def get_bundle(claim_id: str, version: int, actor: Actor = Depends(require_actor)):
        with db.session() as session:
            require_case_access(actor, session.get(Claim, claim_id))
            bundle = session.scalar(select(Bundle).where(Bundle.claim_id == claim_id, Bundle.sequence == version))
            if not bundle:
                raise HTTPException(404, "Bundle version not found.")
            return {**bundle_receipt(session, bundle), "manifest": bundle.manifest, "manifest_hash": bundle.manifest_hash,
                    "status": bundle.status, "profile_version": bundle.profile_version,
                    "coverage": [{"document_id": doc.id, "type": doc.declared_type, "status": doc.status,
                                  "problems": doc.problems} for doc in ordered_documents(session, bundle.id)],
                    "documents": [document_public(doc) for doc in ordered_documents(session, bundle.id)]}

    @app.get("/api/documents/{document_id}/content")
    def document_content(document_id: str, actor: Actor = Depends(require_actor)):
        filename, original = read_source(db, settings, actor, document_id)
        return Response(original, media_type="application/octet-stream",
                        headers={"Content-Disposition": f"attachment; filename=source; filename*=UTF-8''{quote(filename, safe='')}"})

    @app.post("/api/documents/{document_id}/confirm")
    def confirm_source(document_id: str, body: ConfirmationInput, actor: Actor = Depends(require_actor)):
        return confirm_extraction(db, actor, document_id, body.anchor, body.value, body.reason, body.expected_revision, body.source_kind)

    @app.get("/api/documents/{document_id}/preview")
    def preview_source(document_id: str, actor: Actor = Depends(require_actor)):
        from sentinel.document_parser import detect_type
        _, content = read_source(db, settings, actor, document_id)
        kind = detect_type(content)
        if kind not in {"image/png", "image/jpeg", "application/pdf"}:
            raise HTTPException(422,"Preview supports PNG, JPEG and PDF. Download other originals.")
        return Response(content, media_type=kind)

    @app.get("/api/assignees")
    def assignees(actor: Actor = Depends(require_actor)):
        if "supervisor" not in actor.roles:
            raise HTTPException(403, "A supervisor role is required.")
        with db.session() as session:
            return {"items": [{"id": a.id, "username": a.username} for a in session.scalars(select(Account).where(Account.enabled.is_(True)))
                              if set(a.roles) & {"reviewer", "supervisor"}]}

    @app.put("/api/claims/{claim_id}/assignment")
    def assign(claim_id: str, body: AssignmentInput, actor: Actor = Depends(require_actor)):
        if "supervisor" not in actor.roles:
            raise HTTPException(403, "A supervisor role is required.")
        with db.session() as session:
            claim = session.get(Claim, claim_id)
            require_case_access(actor, claim)
            target = session.get(Account, body.assignee_id)
            if not target or not target.enabled or not set(target.roles) & {"reviewer", "supervisor"}:
                raise HTTPException(422, "Assign an enabled reviewer or supervisor.")
            old = claim.assignee_id
            session.execute(update(Claim).where(Claim.id == claim.id)
                            .values(assignee_id=target.id, revision=Claim.revision + 1))
            session.add(AccessEvent(actor_id=actor.id, action="case_assigned", resource_id=claim.id,
                                   detail={"previous": old, "assignee_id": target.id}))
            session.commit()
            return {"id": claim.id, "assignee_id": target.id}

    def authorized_job(session, job_id, actor):
        require_clinical(actor)
        job = session.get(Job, job_id)
        require_case_access(actor, session.get(Claim, job.claim_id) if job else None)
        return job

    async def receive_bundle(actor, claim_file, chart_file, use_model, claim_id=None):
        require_clinical(actor)
        if claim_id:
            with db.session() as session:
                claim = session.get(Claim, claim_id)
                require_case_access(actor, claim)
                if claim.current_bundle_id:
                    raise HTTPException(409, "Import a versioned bundle to revise this case.")
        if use_model and settings.network_mode != "online":
            raise HTTPException(409, "Remote review is disabled offline. Local checks remain available.")
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
            if claim_id:
                require_case_access(actor, session.get(Claim, claim_id))
            return enqueue(session, xml_text, clean_name(claim_file.filename), chart_text, chart_name,
                           chart_blob, chart_error, use_model, claim_id=claim_id, actor_id=actor.id)

    @app.post("/api/claims", status_code=202)
    async def import_claim(claim_file: UploadFile = File(...), chart_file: UploadFile | None = File(None),
                           use_model: bool = Form(False), actor: Actor = Depends(require_actor)):
        return await receive_bundle(actor, claim_file, chart_file, use_model)

    @app.post("/api/claims/{claim_id}/rerun", status_code=202)
    async def rerun(claim_id: str, claim_file: UploadFile = File(...), chart_file: UploadFile | None = File(None),
                    use_model: bool = Form(False), actor: Actor = Depends(require_actor)):
        return await receive_bundle(actor, claim_file, chart_file, use_model, claim_id)

    @app.get("/api/jobs/{job_id}")
    def get_job(job_id: str, actor: Actor = Depends(require_actor)):
        with db.session() as session:
            job = authorized_job(session, job_id, actor)
            return job_detail(session, job)

    @app.put("/api/jobs/{job_id}/reviews/{finding_id}")
    def review(job_id: str, finding_id: str, body: ReviewInput, actor: Actor = Depends(require_actor)):
        with db.session() as session:
            job = authorized_job(session, job_id, actor)
            if job.bundle_id:
                raise HTTPException(409, "Use the versioned review workflow for this bundle.")
            try:
                return save_review(session, job_id, finding_id, body.decision, body.note, actor_id=actor.id)
            except IntegrityError as exc:
                session.rollback()
                raise HTTPException(409, "Another reviewer saved this finding. Refresh and try again.") from exc

    @app.get("/api/jobs/{job_id}/report")
    def report(job_id: str, actor: Actor = Depends(require_actor)):
        detail = get_job(job_id, actor)
        with db.session() as session:
            if session.get(Job, job_id).bundle_id:
                raise HTTPException(409, "Complete the current versioned review before exporting a final record.")
            session.add(AccessEvent(actor_id=actor.id, action="legacy_report_exported", resource_id=job_id))
            session.commit()
        payload = {k: v for k, v in detail.items() if k not in {"xml_text", "chart_text"}}
        return Response(json.dumps(payload, indent=2), media_type="application/json",
                        headers={"Content-Disposition": f'attachment; filename="sentinel-audit-{job_id}.json"'})

    @app.get("/api/jobs/{job_id}/source/{kind}")
    def source(job_id: str, kind: str, actor: Actor = Depends(require_actor)):
        if kind not in {"claim", "chart"}:
            raise HTTPException(404, "Source not found.")
        with db.session() as session:
            job = authorized_job(session, job_id, actor)
            session.add(AccessEvent(actor_id=actor.id, action="source_read", resource_id=job_id, detail={"kind": kind}))
            session.commit()
            if kind == "claim":
                return Response(job.xml_text, media_type="application/xml",
                                headers={"Content-Disposition": 'attachment; filename="claim.xml"'})
            if not job.chart_blob:
                raise HTTPException(404, "No chart was attached.")
            extension = "pdf" if job.chart_name.lower().endswith(".pdf") else "txt"
            return Response(job.chart_blob, media_type="application/octet-stream",
                            headers={"Content-Disposition": f'attachment; filename="chart.{extension}"'})

    @app.post("/api/samples", status_code=202)
    def load_samples(actor: Actor = Depends(require_actor)):
        require_clinical(actor)
        identifiers = []
        for bundle in samples():
            with db.session() as session:
                key = f"{actor.id}:{bundle['key']}" if actor.id else bundle["key"]
                existing = session.scalar(select(Claim).where(Claim.sample_key == key))
                if existing:
                    require_case_access(actor, existing)
                    identifiers.append(existing.id)
                    continue
                try:
                    created = enqueue(session, bundle["xml"], "claim.xml", bundle["chart"], "chart.txt",
                                      bundle["chart"].encode(), sample_key=key, actor_id=actor.id)
                    identifiers.append(created["id"])
                except IntegrityError:
                    session.rollback()
                    existing = session.scalar(select(Claim).where(Claim.sample_key == key))
                    require_case_access(actor, existing)
                    identifiers.append(existing.id)
        return {"ids": identifiers}

    @app.get("/api/samples/bundles.zip")
    def download_samples(actor: Actor = Depends(require_actor)):
        require_clinical(actor)
        return Response(bundle_zip(), media_type="application/zip",
                        headers={"Content-Disposition": 'attachment; filename="sentinel-synthetic-bundles.zip"'})

    @app.get("/")
    def index(request: Request):
        if not request.state.actor:
            from fastapi.responses import RedirectResponse
            return RedirectResponse("/login", status_code=303)
        return FileResponse(STATIC / "index.html")

    @app.get("/login")
    def login_page():
        return FileResponse(STATIC / "login.html")

    # Static sources contain no secrets or uploaded documents.
    STATIC.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


def clean_name(filename):
    return filename.replace("\\", "/").rsplit("/", 1)[-1][:200]


# Uvicorn's factory entry point avoids import-time DB or environment side effects.
def app_factory():
    return create_app()
