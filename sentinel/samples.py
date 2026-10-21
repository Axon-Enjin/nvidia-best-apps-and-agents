"""Synthetic source data. All findings are computed by the actual audit engine."""

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile


def samples():
    examples = [
        ("SYN-1042", "SYN-P042", "Pneumonia", "J18.9", "J18.9", "", "2026-10-17", "Missing discharge date", 18000),
        ("SYN-1043", "SYN-P043", "Gastroenteritis", "A09", "J18.9", "2026-10-16", "2026-10-16", "Diagnosis code differs", 14000),
        ("SYN-1044", "SYN-P044", "Pneumonia", "J18.9", "J18.9", "2026-10-15", "2026-10-15", "Matching source documents", 21000),
        ("SYN-1045", "SYN-P045", "Pneumonia", "J18.9", "J18.9", "2026-10-18", "2026-10-18", "Chart identity needs attention", 18000),
    ]
    bundles = []
    for reference, patient, diagnosis, code, chart_code, discharge, chart_discharge, label, amount in examples:
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<SentinelClaim version="1">
  <ClaimId>{reference}</ClaimId>
  <PatientId>{patient}</PatientId>
  <AdmissionDate>2026-10-12</AdmissionDate>
  <DischargeDate>{discharge}</DischargeDate>
  <Diagnosis code="{code}">{diagnosis}</Diagnosis>
  <ClaimAmount>{amount}.00</ClaimAmount>
  <ChartFile>chart.txt</ChartFile>
</SentinelClaim>'''
        chart_patient = "SYN-P999" if reference == "SYN-1045" else patient
        chart = f'''SYNTHETIC RECORD - NOT A PATIENT
Claim ID: {reference}
Patient ID: {chart_patient}
Admission date: 2026-10-12
Discharge date: {chart_discharge}
Diagnosis code: {chart_code}
Documented diagnosis: Pneumonia

Clinical summary
Fictional adult admitted with fever, cough, and an infiltrate described on a chest radiograph.
Treated with antibiotics. Condition improved before discharge.
These authored examples demonstrate software behavior; they are not clinical guidance.
'''
        bundles.append({"key": reference, "label": label, "xml": xml, "chart": chart,
                        "corrected_xml": xml.replace(f"<DischargeDate>{discharge}</DischargeDate>", f"<DischargeDate>{chart_discharge}</DischargeDate>")
                        .replace(f'<Diagnosis code="{code}">{diagnosis}</Diagnosis>', f'<Diagnosis code="{chart_code}">Pneumonia</Diagnosis>'),
                        "corrected_chart": chart.replace(chart_patient, patient)})
    return bundles


def bundle_zip() -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        archive.writestr("README.txt", "SYNTHETIC EXAMPLES ONLY. Upload each folder's claim.xml and chart.txt.\nCorrected files are included to exercise the rerun workflow.\n")
        for bundle in samples():
            folder = bundle["key"]
            archive.writestr(f"{folder}/claim.xml", bundle["xml"])
            archive.writestr(f"{folder}/chart.txt", bundle["chart"])
            archive.writestr(f"{folder}/corrected/claim.xml", bundle["corrected_xml"])
            archive.writestr(f"{folder}/corrected/chart.txt", bundle["corrected_chart"])
    return buffer.getvalue()
def development_bundle(label="complete"):
    """Seven-artifact internal sample contract; never official eClaims compatibility."""
    import hashlib
    from xml.etree.ElementTree import Element, SubElement, tostring

    anchors = {"facility_id": "SYN-FACILITY", "encounter_ref": "SYN-ENCOUNTER-1", "claim_ref": "SYN-CLAIM-1", "patient_id": "SYN-PATIENT-1"}
    common = {"Facility ID": anchors["facility_id"], "Encounter Ref": anchors["encounter_ref"],
              "Claim Ref": anchors["claim_ref"], "Patient ID": anchors["patient_id"],
              "Scope": "adult medical inpatient", "DOB": "1980-04-12", "Admission Date": "2026-10-10",
              "Discharge Date": "2026-10-14", "Diagnosis": "Synthetic pneumonia", "Diagnosis Code": "J18.9",
              "Disposition": "Discharged", "Admission Reason": "Synthetic fever", "Course": "Improved",
              "Treatment": "Sample treatment", "Outcome": "Improved", "Mark": "Fictional sample mark",
              "Printed Name": "Sample Signatory", "Signed Date": "2026-10-14"}
    files, members = [], []
    for kind in ("cf2", "cf4", "cf5", "esoa", "discharge", "csf", "eligibility"):
        values = dict(common)
        if label == "discrepant" and kind == "discharge":
            values["Discharge Date"] = "2026-10-15"
        if label == "incomplete" and kind == "cf4":
            values.pop("Course")
        if kind == "esoa":
            root = Element("SampleESOA", version="1")
            for name, value in values.items():
                SubElement(root, name.replace(" ", "")).text = value
            SubElement(root, "Currency").text = "PHP"
            line = SubElement(SubElement(root, "Lines"), "Line")
            SubElement(line, "Gross").text = "100.00"
            SubElement(line, "Discount").text = "10.00"
            SubElement(root, "Total").text = "90.00"
            name, content = "esoa.xml", tostring(root)
        else:
            name, content = f"{kind}.txt", "".join(f"{key}: {value}\n" for key, value in values.items()).encode()
        files.append((name, content))
        members.append({"type": kind, "filename": name, "sha256": hashlib.sha256(content).hexdigest()})
    return files, {**anchors, "documents": members}

