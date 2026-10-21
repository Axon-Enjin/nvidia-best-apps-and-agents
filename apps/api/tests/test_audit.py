import pytest

from sentinel.audit import audit_bundle
from sentinel.documents import extract_chart
from sentinel.inference import validate_model_findings


def claim_xml(**changes):
    values = {
        "ClaimId": "SYN-001", "PatientId": "SYN-P001", "AdmissionDate": "2026-10-01",
        "DischargeDate": "2026-10-04", "Diagnosis": "Pneumonia", "ClaimAmount": "18000.00",
    } | changes
    elements = []
    for key, value in values.items():
        attributes = ' code="J18.9"' if key == "Diagnosis" else ""
        elements.append(f"<{key}{attributes}>{value}</{key}>")
    return '<SentinelClaim version="1">' + "".join(elements) + "</SentinelClaim>"


CHART = """SYNTHETIC RECORD - NOT A PATIENT
Claim ID: SYN-001
Patient ID: SYN-P001
Admission date: 2026-10-01
Discharge date: 2026-10-04
Diagnosis code: J18.9
Documented diagnosis: Pneumonia
Course: Treated with antibiotics. Improved at discharge.
"""


def test_matching_bundle_reports_local_coverage_without_claiming_clinical_approval():
    result = audit_bundle(claim_xml(), CHART)
    assert result["outcome"] == "no_findings"
    assert result["findings"] == []
    assert result["model_status"] == "not_requested"
    assert result["fields"]["claim_id"] == "SYN-001"


def test_missing_discharge_is_a_content_derived_finding():
    result = audit_bundle(claim_xml(DischargeDate=""), CHART)
    assert result["outcome"] == "needs_review"
    finding = next(f for f in result["findings"] if f["code"] == "required_discharge_date")
    assert finding["category"] == "structure"
    assert "2026-10-04" in finding["chart_quote"]


@pytest.mark.parametrize("xml", ["<broken", '<!DOCTYPE x [<!ENTITY a SYSTEM "file:///etc/passwd">]><SentinelClaim version="1">&a;</SentinelClaim>'])
def test_malformed_or_entity_xml_cannot_be_cleared(xml):
    result = audit_bundle(xml, CHART)
    assert result["outcome"] == "incomplete"
    assert result["findings"][0]["code"] == "unreadable_xml"


def test_unsupported_official_xml_is_explicitly_incomplete():
    result = audit_bundle("<CF4><Patient>Example</Patient></CF4>", CHART)
    assert result["outcome"] == "incomplete"
    assert result["findings"][0]["code"] == "unsupported_format"


def test_patient_mismatch_prevents_chart_comparison():
    result = audit_bundle(claim_xml(), CHART.replace("SYN-P001", "SYN-P999"))
    assert result["outcome"] == "incomplete"
    assert "patient_mismatch" in [f["code"] for f in result["findings"]]
    assert not any(f["code"].startswith("mismatch_") for f in result["findings"])


def test_missing_chart_identity_is_incomplete():
    result = audit_bundle(claim_xml(), "A clinical narrative without a patient identifier.")
    assert result["outcome"] == "incomplete"
    assert "chart_identity_missing" in [f["code"] for f in result["findings"]]


def test_explicit_diagnosis_codes_are_compared_without_inventing_a_diagnosis():
    result = audit_bundle(claim_xml().replace('code="J18.9"', 'code="A09"'), CHART)
    finding = next(f for f in result["findings"] if f["code"] == "mismatch_diagnosis_code")
    assert "A09" in finding["claim_quote"]
    assert "J18.9" in finding["chart_quote"]
    assert finding["category"] == "cross_document"


def test_discharge_before_admission_is_flagged():
    result = audit_bundle(claim_xml(DischargeDate="2026-09-30"), CHART)
    assert "date_order" in [f["code"] for f in result["findings"]]


def test_duplicate_fields_cannot_hide_conflicting_values():
    xml = claim_xml().replace("</SentinelClaim>", "<PatientId>OTHER</PatientId></SentinelClaim>")
    result = audit_bundle(xml, CHART)
    assert result["outcome"] == "incomplete"
    assert "duplicate_fields" in [f["code"] for f in result["findings"]]


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-1", "1e9999"])
def test_invalid_monetary_values_are_not_accepted(value):
    result = audit_bundle(claim_xml(ClaimAmount=value), CHART)
    assert "invalid_amount" in [f["code"] for f in result["findings"]]


def test_text_extraction_rejects_invalid_encoding_and_invalid_pdf():
    with pytest.raises(ValueError):
        extract_chart(b"\xff\xfe\x00", "chart.txt")
    with pytest.raises(ValueError):
        extract_chart(b"not a pdf", "chart.pdf")


def test_model_findings_require_verbatim_evidence_in_both_documents():
    response = {"findings": [{"title": "Diagnosis needs review", "explanation": "Check the diagnosis.",
                              "claim_quote": "Pneumonia", "chart_quote": "Treated with antibiotics."}]}
    findings = validate_model_findings(response, claim_xml(), CHART)
    assert findings[0]["category"] == "model"
    response["findings"][0]["chart_quote"] = "A fabricated sentence"
    with pytest.raises(ValueError, match="evidence"):
        validate_model_findings(response, claim_xml(), CHART)


def test_invalid_or_unbounded_model_output_fails_closed():
    with pytest.raises(ValueError):
        validate_model_findings({"findings": "none"}, claim_xml(), CHART)
    with pytest.raises(ValueError):
        validate_model_findings({"findings": [{}] * 21}, claim_xml(), CHART)
