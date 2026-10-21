"""Content-derived checks for Sentinel's internal bundle contract, not PhilHealth certification."""

import re
from datetime import date
from decimal import Decimal, InvalidOperation

from defusedxml import ElementTree

RULE_VERSION = "sentinel-bundle/1.0"
FIELDS = {
    "ClaimId": "claim_id", "PatientId": "patient_id", "AdmissionDate": "admission_date",
    "DischargeDate": "discharge_date", "Diagnosis": "diagnosis", "ClaimAmount": "amount",
}


def audit_bundle(xml: str, chart: str, chart_error: str | None = None) -> dict:
    findings = []
    checks = []
    result = {"rule_version": RULE_VERSION, "fields": {}, "findings": findings, "checks": checks,
              "outcome": "incomplete", "model_status": "not_requested", "model_name": None}

    def flag(code, title, explanation, category="structure", claim_quote="", chart_quote="", blocking=False):
        findings.append({"id": code, "code": code, "title": title, "explanation": explanation,
                         "category": category, "severity": "blocking" if blocking else "review",
                         "claim_quote": claim_quote, "chart_quote": chart_quote, "rule": RULE_VERSION})

    try:
        root = ElementTree.fromstring(xml, forbid_dtd=True, forbid_entities=True, forbid_external=True)
    except Exception:
        flag("unreadable_xml", "Claim XML could not be read", "Repair the XML. DTDs and entities are not supported.", blocking=True)
        return result
    if root.tag != "SentinelClaim" or root.attrib.get("version") != "1":
        flag("unsupported_format", "Unsupported claim format", "Upload SentinelClaim version 1. Official CF4/eClaims schemas are not supported by this prototype.", blocking=True)
        return result
    if any(len(root.findall(key)) > 1 for key in FIELDS):
        flag("duplicate_fields", "Conflicting duplicate fields", "Each bundle field must occur once. Remove duplicate elements before auditing.", blocking=True)
        return result

    fields = result["fields"]
    for tag, name in FIELDS.items():
        fields[name] = (root.findtext(tag) or "").strip()
    diagnosis = root.find("Diagnosis")
    fields["diagnosis_code"] = diagnosis.get("code", "").strip() if diagnosis is not None else ""
    fields["chart_file"] = (root.findtext("ChartFile") or "").strip()
    for key, label in [("claim_id", "claim identifier"), ("patient_id", "patient identifier"),
                       ("admission_date", "admission date"), ("discharge_date", "discharge date"),
                       ("diagnosis_code", "diagnosis code"), ("diagnosis", "diagnosis description")]:
        if not fields[key]:
            flag("required_" + key, f"Missing {label}", f"The internal bundle requires a {label}. Correct the source XML and rerun.",
                 chart_quote=next((line for line in chart.splitlines() if label.split()[0] in line.lower()), ""),
                 blocking=key in {"claim_id", "patient_id"})
    dates = {}
    for key in ("admission_date", "discharge_date"):
        if fields[key]:
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields[key]):
                    raise ValueError
                dates[key] = date.fromisoformat(fields[key])
            except ValueError:
                flag("invalid_" + key, "Invalid " + key.replace("_", " "), "Use an actual calendar date in YYYY-MM-DD format.", claim_quote=fields[key])
    if len(dates) == 2 and dates["discharge_date"] < dates["admission_date"]:
        flag("date_order", "Discharge precedes admission", "Confirm the confinement dates in the source record.", claim_quote=f"{fields['admission_date']} / {fields['discharge_date']}")
    try:
        amount = Decimal(fields["amount"])
        if not amount.is_finite() or not 0 <= amount <= 1_000_000_000 or amount.as_tuple().exponent < -2:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        flag("invalid_amount", "Claim amount needs correction", "Use a non-negative amount with at most two decimal places, up to PHP 1 billion.", claim_quote=fields["amount"])
    checks.append({"label": "Internal XML contract", "status": "flagged" if findings else "passed"})

    associated = False
    if chart_error or not chart.strip():
        flag("unreadable_chart", "Chart review is incomplete", chart_error or "Upload a readable supporting chart.", category="completeness", blocking=True)
    else:
        patient_match = re.search(r"^Patient ID:\s*(\S[^\r\n]*)", chart, re.I | re.M)
        if not patient_match:
            flag("chart_identity_missing", "Cannot match the chart to this claim", "The supported chart template needs a Patient ID line. Match records before comparing their content.", category="completeness", blocking=True)
        elif patient_match.group(1).strip() != fields["patient_id"]:
            flag("patient_mismatch", "Chart belongs to a different patient identifier", "Resolve the document association before reviewing clinical content.", category="cross_document", claim_quote=fields["patient_id"], chart_quote=patient_match.group(0), blocking=True)
        else:
            associated = True
        claim_match = re.search(r"^Claim ID:\s*(\S[^\r\n]*)", chart, re.I | re.M)
        if claim_match and claim_match.group(1).strip() != fields["claim_id"]:
            associated = False
            flag("claim_mismatch", "Chart references another claim", "Confirm the encounter and claim association.", category="cross_document", claim_quote=fields["claim_id"], chart_quote=claim_match.group(0), blocking=True)
    checks.append({"label": "Chart association", "status": "passed" if associated else "incomplete"})
    if associated:
        comparisons = [("Admission date", "admission_date"), ("Discharge date", "discharge_date"), ("Diagnosis code", "diagnosis_code")]
        for label, key in comparisons:
            match = re.search(r"^" + re.escape(label) + r":\s*([^\r\n]+)", chart, re.I | re.M)
            if match and fields[key] and match.group(1).strip().casefold() != fields[key].casefold():
                flag("mismatch_" + key, label + " differs across documents", "The explicitly recorded values differ. Review both sources; this check does not select the correct value.", category="cross_document", claim_quote=fields[key], chart_quote=match.group(0))
        checks.append({"label": "Explicit chart fields", "status": "flagged" if any(f["category"] == "cross_document" for f in findings) else "passed"})
    result["outcome"] = outcome_for(findings)
    return result


def outcome_for(findings: list[dict]) -> str:
    if any(f["severity"] == "blocking" for f in findings):
        return "incomplete"
    return "needs_review" if findings else "no_findings"
