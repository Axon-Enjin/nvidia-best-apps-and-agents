"""Internal synthetic contract. This is not an official payer validation schema."""
from datetime import date
from decimal import Decimal, InvalidOperation

from sentinel.bundles import REQUIRED_TYPES

RULE_VERSION = "SAMPLE-ADULT-MEDICAL-1/1"
IDENTITY = ("facility_id", "encounter_ref", "claim_ref", "patient_id")
REQUIRED_FIELDS = {
    "cf2": (*IDENTITY, "scope", "dob", "admission_date", "discharge_date", "diagnosis", "disposition"),
    "cf4": (*IDENTITY, "admission_reason", "course", "treatment", "outcome"),
    "cf5": (*IDENTITY, "diagnosis", "diagnosis_code", "disposition"),
    "esoa": (*IDENTITY, "currency", "total"),
    "discharge": (*IDENTITY, "dob", "admission_date", "discharge_date", "diagnosis", "disposition"),
    "csf": IDENTITY, "eligibility": IDENTITY,
}


def equivalent(value):
    return " ".join(str(value).split()).casefold()


def mark_problems(fields):
    absent = {"", "none", "no", "n/a", "not present", "missing", "absent", "unknown"}
    problems = [key for key in ("mark", "printed_name") if equivalent(fields.get(key, "")) in absent]
    try:
        date.fromisoformat(fields.get("signed_date", ""))
    except (ValueError,TypeError):
        problems.append("signed_date")
    return problems


def evaluate_profile(bundle, confirmed_extractions=None, rule_version=RULE_VERSION):
    # Overrides are constructed only from stored, source-backed confirmations by the service.
    docs = bundle["documents"]
    fields = {d["id"]: {**d.get("extraction", {}).get("fields", {}),
                          **(confirmed_extractions or {}).get(d["id"], {})} for d in docs}
    by_type = {kind: [d for d in docs if d["type"] == kind] for kind in REQUIRED_TYPES}
    checks = []

    def anchors(selected=None, names=None):
        return [{**a, "bundle_id": bundle["id"], "document_id": d["id"], "sha256": d.get("sha256", "")}
                for d in (docs if selected is None else selected) for a in d.get("extraction", {}).get("anchors", [])
                if names is None or a["field"] in names]

    def add(id, label, problems, status="incomplete", selected=None, names=None, differences=()):
        checks.append({"id": id, "label": label, "status": status if problems else "passed",
                       "blocking_reasons": problems, "anchors": anchors(selected, names),
                       "differences": list(differences)})

    def source(doc, key):
        # Only values that count for the checks are listed; the page comes from a matching anchor or stays unknown.
        value = fields[doc["id"]][key]
        page = next((a["page"] for a in doc.get("extraction", {}).get("anchors", [])
                     if a["field"] == key and equivalent(a["value"]) == equivalent(value)), None)
        return {"document_id": doc["id"], "type": doc["type"], "bundle_id": bundle["id"], "value": value, "page": page}

    primary = fields[by_type["cf2"][0]["id"]] if len(by_type["cf2"]) == 1 else {}
    scope_problems = []
    try:
        dob, admission = date.fromisoformat(primary["dob"]), date.fromisoformat(primary["admission_date"])
        age = admission.year - dob.year - ((admission.month, admission.day) < (dob.month, dob.day))
        if age < 18 or equivalent(primary.get("scope")) != "adult medical inpatient":
            scope_problems.append("This profile requires adult general medical inpatient scope.")
    except (KeyError, ValueError, TypeError):
        scope_problems.append("Confirm the birth and admission dates against source.")
    if any(not primary.get(key) for key in IDENTITY):
        scope_problems.append("Facility, encounter, claim and patient anchors are required.")
    add("P01", "Adult medical inpatient scope", scope_problems, names=(*IDENTITY, "scope", "dob", "admission_date"))
    coverage = [f"Require exactly one readable matched {kind}." for kind in REQUIRED_TYPES
                if len(by_type[kind]) != 1 or by_type[kind][0]["status"] != "readable"]
    if sum(d.get("page_count", 0) for d in docs) > 150:
        coverage.append("Bundle exceeds 150 pages; content was not truncated.")
    add("P02", "Seven core artifacts", coverage)
    missing = [f"{d['type']}: missing {key}" for d in docs for key in REQUIRED_FIELDS.get(d["type"], ())
               if not fields[d["id"]].get(key, "").strip()]
    missing += [f"Missing {kind}." for kind in REQUIRED_TYPES if not by_type[kind]]
    add("P03", "Required source values", missing)
    conflicts = [f"{key} differs from case membership." for d in docs for key in IDENTITY
                 if fields[d["id"]].get(key) and equivalent(fields[d["id"]][key]) != equivalent(bundle["manifest"].get(key, ""))]
    identity_differences = []
    for key in IDENTITY:
        expected = bundle["manifest"].get(key, "")
        differing = [d for d in docs if fields[d["id"]].get(key) and equivalent(fields[d["id"]][key]) != equivalent(expected)]
        if differing:
            identity_differences.append({"field": key, "expected": expected, "sources": [source(d, key) for d in differing]})
    add("P04", "Patient and encounter agreement", conflicts, "flagged", names=IDENTITY, differences=identity_differences)
    chronology, date_differences = [], []
    for key in ("dob", "admission_date", "discharge_date", "disposition"):
        holders = [d for d in docs if fields[d["id"]].get(key)]
        values = [fields[d["id"]][key] for d in holders]
        if len({equivalent(value) for value in values}) > 1:
            chronology.append(f"Conflicting {key} values across sources.")
            date_differences.append({"field": key, "expected": None, "sources": [source(d, key) for d in holders]})
        if key != "disposition":
            for value in values:
                try:
                    date.fromisoformat(value)
                except (ValueError, TypeError):
                    chronology.append(f"Ambiguous {key}; use a confirmed ISO date.")
    for d in docs:
        f = fields[d["id"]]
        try:
            if f.get("discharge_date") and date.fromisoformat(f["discharge_date"]) < date.fromisoformat(f["admission_date"]):
                chronology.append("Discharge precedes admission.")
            if f.get("dob") and date.fromisoformat(f["dob"]) > date.fromisoformat(f["admission_date"]):
                chronology.append("Birth follows admission.")
        except (ValueError, KeyError, TypeError):
            pass  # Missing values remain blocked by P03.
    add("P05", "Dates and disposition", chronology, "flagged", names=("dob", "admission_date", "discharge_date", "disposition"),
        differences=date_differences)
    finance = []
    finance_status = "unsupported"
    try:
        esoa = by_type["esoa"][0]
        contract = esoa["extraction"]["financial"]
        if contract["currency"] != "PHP" or not contract["lines"]:
            raise ValueError
        def amount(value):
            number = Decimal(value)
            if not number.is_finite() or number < 0 or number > Decimal("1000000000000"):
                raise ValueError
            return number
        net = sum((amount(line["gross"]) - amount(line["discount"]) for line in contract["lines"]), Decimal(0))
        if abs(net - amount(contract["total"])) > Decimal("0.01"):
            finance.append("Gross lines less explicit discounts differ from net total by more than PHP 0.01.")
        finance_status = "flagged"
    except (KeyError, IndexError, ValueError, TypeError, InvalidOperation):
        finance.append("Require supported SampleESOA v1 PHP lines, explicit discounts and total.")
    add("P06", "Sample eSOA arithmetic", finance, finance_status, selected=by_type["esoa"])
    add("P07", "Narrative agreement", ["Record source-backed manual comparison and separate supervisor acknowledgement."])
    marks = [f"{d['type']}: missing/unknown {key}" for d in docs if d["type"] in {"cf2", "cf4", "cf5", "csf"}
             for key in mark_problems(fields[d["id"]])]
    add("P08", "Marks, printed signatory and date", marks + ["Named manual presence review is required."], names=("mark", "printed_name", "signed_date"))
    extra = []
    for expectation in bundle.get("expectations", []):
        waived = (expectation.get("type") == "attachment" and expectation.get("withdrawn")
                  and expectation.get("role") == "supervisor" and expectation.get("reason", "").strip())
        if not waived and not expectation.get("reviewed"):
            extra.append("Review the expected extra attachment or obtain a reasoned supervisor withdrawal.")
    add("P09", "Expected extra attachments", extra)
    add("P10", "Current-version closeout", ["Resolve P01-P09 and correction tasks before completing the review."])
    findings = [{"id": c["id"], "code": c["id"], "title": c["label"], "severity": "blocking",
                 "explanation": " ".join(c["blocking_reasons"]), "anchors": c["anchors"], "rule": rule_version}
                for c in checks if c["status"] != "passed" and c["id"] != "P10"]
    return {"rule_version": rule_version, "bundle_id": bundle["id"], "profile_status": "evaluated",
            "model_status": "not_run_offline", "outcome": "incomplete", "checks": checks, "findings": findings,
            "fields": {"claim_id": bundle["manifest"].get("claim_ref"), "patient_id": bundle["manifest"].get("patient_id")},
            "coverage": [{"document_id": d["id"], "type": d["type"], "status": d["status"], "problems": d.get("problems", [])} for d in docs]}
