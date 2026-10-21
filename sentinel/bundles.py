"""Transactional bundle versions and their immutable original-source membership."""
import hashlib
import json
import re

from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError

from sentinel.accounts import require_case_access, require_clinical
from sentinel.db import AccessEvent, Bundle, Claim, Document, Job, new_id
from sentinel.storage import PrivateStorage

REQUIRED_TYPES = ("cf2", "cf4", "cf5", "esoa", "discharge", "csf", "eligibility")
MAX_SOURCE_BYTES = 25 * 1024 * 1024
MAX_BUNDLE_BYTES = 100 * 1024 * 1024
MAX_BUNDLE_FILES = 30
MAX_BUNDLE_PAGES = 150


class CaseInput(BaseModel):
    facility_id: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")
    encounter_ref: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")
    claim_ref: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")
    patient_id: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")


def safe_filename(name):
    name = name.replace("\\", "/").rsplit("/", 1)[-1]
    return "".join(c for c in name if c.isprintable() and c not in {'"', ';'})[:200] or "source"


def case_public(case):
    return {"id": case.id, "facility_id": case.facility_id, "encounter_ref": case.encounter_ref,
            "claim_ref": case.reference, "patient_id": case.patient_id, "revision": case.revision,
            "current_bundle_id": case.current_bundle_id, "assignee_id": case.assignee_id, "state": case.state}


def create_case(db, actor, values):
    require_clinical(actor)
    if actor.id is None:
        raise HTTPException(403, "Named accounts are required for the versioned workflow.")
    with db.session() as session:
        case = Claim(facility_id=values.facility_id.strip(), encounter_ref=values.encounter_ref.strip(),
                     reference=values.claim_ref.strip(), patient_id=values.patient_id.strip(), assignee_id=actor.id)
        session.add(case)
        session.flush()
        session.add(AccessEvent(actor_id=actor.id, action="case_created", resource_id=case.id))
        session.commit()
        return case_public(case)


def document_public(document):
    return {"id": document.id, "type": document.declared_type, "filename": document.filename,
            "sha256": document.source_hash, "byte_count": document.byte_count, "content_type": document.content_type,
            "page_count": document.page_count, "status": document.status, "problems": document.problems,
            "extraction": document.extraction}


def ordered_documents(session, bundle_id):
    return session.scalars(select(Document).where(Document.bundle_id == bundle_id).order_by(Document.position)).all()


def bundle_receipt(session, bundle):
    documents = ordered_documents(session, bundle.id)
    return {"case_id": bundle.claim_id, "bundle_id": bundle.id, "version": bundle.sequence,
            "revision": bundle.imported_revision, "import_job_id": bundle.import_job_id,
            "coverage": [{"document_id": doc.id, "type": doc.declared_type, "status": "quarantined"} for doc in documents]}


def import_bundle(db, settings, actor, case_id, files, manifest, expected_revision, idempotency_key):
    if not actor.id:
        raise HTTPException(403, "Named accounts are required for the versioned workflow.")
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,100}", idempotency_key):
        raise HTTPException(422, "Supply an Idempotency-Key of 1-100 letters, digits, periods, underscores or hyphens.")
    if not 1 <= len(files) <= MAX_BUNDLE_FILES or sum(len(content) for _, content in files) > MAX_BUNDLE_BYTES:
        raise HTTPException(413, "A version supports 1-30 files and up to 100 MB.")
    if any(len(content) > MAX_SOURCE_BYTES for _, content in files):
        raise HTTPException(413, "Each original must be 25 MB or smaller.")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("documents"), list) or len(manifest["documents"]) != len(files):
        raise HTTPException(422, "Manifest membership must match every uploaded file in order.")
    for member, (filename, content) in zip(manifest["documents"], files, strict=True):
        if (not isinstance(member, dict) or member.get("type") not in {*REQUIRED_TYPES, "attachment"}
                or member.get("filename") != filename or member.get("sha256") != hashlib.sha256(content).hexdigest()):
            raise HTTPException(422, "Manifest type, filename and SHA-256 must match the uploaded original.")
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    with db.session() as session:
        case = session.get(Claim, case_id)
        require_case_access(actor, case)
        if any(manifest.get(key) != value for key, value in {
            "facility_id": case.facility_id, "encounter_ref": case.encounter_ref,
            "claim_ref": case.reference, "patient_id": case.patient_id}.items()):
            raise HTTPException(409, "Manifest identifiers do not match the case; names cannot establish encounter membership.")
        existing = session.scalar(select(Bundle).where(Bundle.claim_id == case_id, Bundle.idempotency_key == idempotency_key))
        if existing:
            if existing.request_hash != digest:
                raise HTTPException(409, "That idempotency key belongs to a different bundle.")
            return bundle_receipt(session, existing)
        bundle_id, job_id = new_id(), new_id()
        assignment = True if "supervisor" in actor.roles else Claim.assignee_id == actor.id
        updated = session.execute(update(Claim).where(Claim.id == case_id, Claim.revision == expected_revision, assignment)
                                  .values(revision=Claim.revision + 1, current_bundle_id=bundle_id,
                                          latest_job_id=job_id, state="In review"))
        if updated.rowcount != 1:
            session.rollback()
            # A concurrent identical request can have committed while we waited.
            existing = session.scalar(select(Bundle).where(Bundle.claim_id == case_id, Bundle.idempotency_key == idempotency_key))
            if existing and existing.request_hash == digest:
                return bundle_receipt(session, existing)
            raise HTTPException(409, "Case changed. Refresh before importing a new version.")
        sequence = (session.scalar(select(func.max(Bundle.sequence)).where(Bundle.claim_id == case_id)) or 0) + 1
        bundle = Bundle(id=bundle_id, claim_id=case_id, sequence=sequence, import_job_id=job_id,
                        manifest=manifest, manifest_hash=digest, request_hash=digest, idempotency_key=idempotency_key,
                        created_by=actor.id, imported_revision=expected_revision + 1)
        session.add(bundle)
        session.flush()
        storage = PrivateStorage(settings)
        for position, (member, (name, content)) in enumerate(zip(manifest["documents"], files, strict=True)):
            key = storage.put(content, case_id)
            session.add(Document(bundle_id=bundle_id, position=position, declared_type=member["type"], filename=safe_filename(name),
                                 source_hash=member["sha256"], object_key=key, byte_count=len(content)))
        session.add(Job(id=job_id, claim_id=case_id, bundle_id=bundle_id, xml_name="", xml_text="",
                        xml_hash=hashlib.sha256(b"").hexdigest()))
        session.add(AccessEvent(actor_id=actor.id, action="bundle_imported", resource_id=case_id,
                                detail={"bundle_id": bundle_id, "version": sequence}))
        try:
            session.commit()
        except IntegrityError as exc:
            raise HTTPException(409, "Another bundle was imported. Refresh and retry with the same key.") from exc
        return bundle_receipt(session, bundle)


def read_source(db, settings, actor, document_id):
    with db.session() as session:
        document = session.get(Document, document_id)
        bundle = session.get(Bundle, document.bundle_id) if document else None
        require_case_access(actor, session.get(Claim, bundle.claim_id) if bundle else None)
        content = PrivateStorage(settings).read(document.object_key, document.source_hash)
        session.add(AccessEvent(actor_id=actor.id, action="source_read", resource_id=document.id,
                               detail={"bundle_id": bundle.id}))
        session.commit()
        return document.filename, content
