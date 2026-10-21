"""Source-backed confirmations append history and reopen manual review."""
from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from sentinel.accounts import require_case_access
from sentinel.db import Bundle, Claim, Document, ExtractionConfirmation, ReviewEvent
from sentinel.document_parser import FIELD_NAMES
from sentinel.profile import IDENTITY, REQUIRED_FIELDS, RULE_VERSION, equivalent


class ConfirmationInput(BaseModel):
    expected_revision: int = Field(ge=0)
    anchor: dict
    value: str = Field(min_length=1, max_length=10000)
    reason: str = Field(min_length=1, max_length=2000)
    source_kind: str = Field(pattern="^printed$")


def confirmed_documents(session, documents):
    effective, requirements = [], []
    for doc in documents:
        confirmations = session.scalars(select(ExtractionConfirmation).where(ExtractionConfirmation.document_id == doc.id).order_by(ExtractionConfirmation.revision)).all()
        fields = dict(doc.extraction.get("fields", {}))
        anchored = list(doc.extraction.get("anchors", []))
        confirmed = {}
        for c in confirmations:
            fields[c.anchor["field"]] = c.value
            confirmed[c.anchor["field"]] = {"value":c.value, "confirmation_id":c.id, "actor_id":c.actor_id, "page":c.anchor["page"]}
            anchored = [a for a in anchored if a["field"] != c.anchor["field"]]
            anchored.append({"field":c.anchor["field"], "value":c.value, "page":c.anchor["page"], "confirmation_id":c.id})
        scan = doc.extraction.get("requires_confirmation", False)
        pending = (set(doc.extraction.get("fields", {})) | {"facility_id", "encounter_ref", "claim_ref", "patient_id"}) - confirmed.keys() if scan else set(doc.problems) - confirmed.keys() if doc.status == "ambiguous" else set()
        status = doc.status
        if scan:
            # Unconfirmed candidates are never inputs to blocking consistency checks.
            fields = {key:value for key,value in fields.items() if key in confirmed}
            status = "needs_confirmation" if pending else "readable"
        elif status in {"ambiguous", "unmatched"} and confirmations and not pending:
            status = "readable"
        membership = session.get(Bundle,doc.bundle_id).manifest
        if status == "readable" and any(not fields.get(key) or equivalent(fields[key]) != equivalent(membership.get(key,"")) for key in IDENTITY):
            status = "unmatched"
        effective.append({"id":doc.id,"type":doc.declared_type,"sha256":doc.source_hash,"status":status,
                          "page_count":doc.page_count,"problems":doc.problems,"extraction":{**doc.extraction,"fields":fields,"anchors":anchored}})
        requirements.append({"document_id":doc.id,"type":doc.declared_type,"status":status,"pending":sorted(pending),"confirmed":confirmed,
                             "fields":sorted(set(fields) | set(doc.extraction.get("fields", {})) | set(REQUIRED_FIELDS.get(doc.declared_type, ())) | set(IDENTITY))})
    return effective, requirements


def confirm_extraction(db, actor, document_id, anchor, value, reason, expected_revision, source_kind="printed"):
    from sentinel.review import fence_case, review_state
    with db.session() as session:
        doc = session.get(Document, document_id)
        bundle = session.get(Bundle, doc.bundle_id) if doc else None
        case = session.get(Claim, bundle.claim_id) if bundle else None
        require_case_access(actor, case)
        if not actor.id:
            raise HTTPException(403,"Named source confirmation is required.")
        fence_case(session,actor,case,expected_revision,doc.bundle_id)
        page, field = anchor.get("page"), anchor.get("field")
        if (source_kind != "printed" or not isinstance(page,int) or isinstance(page,bool) or not 1 <= page <= doc.page_count
                or field not in set(FIELD_NAMES.values()) or not value.strip() or not reason.strip()
                or doc.status in {"unreadable","unsupported","quarantined"}):
            raise HTTPException(422,"Confirm a legible printed source field and page; handwriting/unreadable content needs replacement.")
        confirmation = ExtractionConfirmation(document_id=doc.id,actor_id=actor.id,anchor={"page":page,"field":field},
                                              value=value.strip(),reason=reason.strip(),revision=case.revision)
        session.add(confirmation)
        session.flush()
        session.add(ReviewEvent(claim_id=case.id,bundle_id=bundle.id,rule_version=RULE_VERSION,revision=case.revision,
                                actor_id=actor.id,actor_name=actor.username,action="extraction_confirmed",
                                payload={"confirmation_id":confirmation.id,"document_id":doc.id,"anchor":anchor,"value":value.strip(),"reason":reason.strip()}))
        session.flush()
        result = review_state(session,case)
        session.commit()
        return {"confirmation_id":confirmation.id,"review_state":result}
