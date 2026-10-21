import copy

import pytest

from sentinel.document_parser import extract


def profile(label="complete"):
    from sentinel.samples import development_bundle
    files, manifest = development_bundle(label)
    docs = [{"id": str(i), "type": member["type"], "sha256": member["sha256"], **extract(content)}
            for i, (member, (_, content)) in enumerate(zip(manifest["documents"], files, strict=True))]
    return {"id": "bundle-1", "manifest": manifest, "documents": docs}


def evaluate(bundle):
    from sentinel.audit import evaluate_profile
    return evaluate_profile(bundle, {}, "SAMPLE-ADULT-MEDICAL-1/1")


def checks(bundle):
    return {c["id"]: c for c in evaluate(bundle)["checks"]}


def test_complete_content_still_requires_real_manual_review_and_closeout():
    bundle = profile()
    result = evaluate(bundle)
    assert {c["id"] for c in result["checks"]} == {f"P{i:02}" for i in range(1, 11)}
    states = checks(bundle)
    assert all(states[f"P{i:02}"]["status"] == "passed" for i in (1, 2, 3, 4, 5, 6, 9))
    assert all(states[f"P{i:02}"]["status"] == "incomplete" for i in (7, 8, 10))
    assert result["model_status"] == "not_run_offline"
    assert all(a["bundle_id"] == bundle["id"] and a["document_id"] for c in result["checks"] for a in c["anchors"])


@pytest.mark.parametrize("check,document,field,value", [
    ("P01", 0, "dob", "2015-01-01"), ("P01", 0, "scope", "outpatient"),
    ("P03", 1, "course", ""), ("P03", 2, "diagnosis_code", ""),
    ("P04", 4, "patient_id", "OTHER"), ("P05", 0, "discharge_date", "2026-10-01"),
    ("P05", 4, "disposition", "Transferred"), ("P08", 5, "mark", ""),
])
def test_content_rules_cannot_be_cleared_by_readable_status(check, document, field, value):
    bundle = profile()
    bundle["documents"][document]["extraction"]["fields"][field] = value
    assert checks(bundle)[check]["status"] != "passed"


@pytest.mark.parametrize("kind", ["cf2", "cf4", "cf5", "esoa", "discharge", "csf", "eligibility"])
def test_no_core_artifact_waiver(kind):
    bundle = profile()
    bundle["documents"] = [doc for doc in bundle["documents"] if doc["type"] != kind]
    bundle["expectations"] = [{"type": kind, "withdrawn": True, "role": "supervisor", "reason": "mistake"}]
    assert checks(bundle)["P02"]["status"] == "incomplete"


@pytest.mark.parametrize("total,status", [("90.01", "passed"), ("90.02", "flagged"), ("NaN", "unsupported"), ("Infinity", "unsupported")])
def test_php_tolerance_is_decimal_and_unknown_semantics_do_not_pass(total, status):
    bundle = profile()
    bundle["documents"][3]["extraction"]["financial"]["total"] = total
    assert checks(bundle)["P06"]["status"] == status


def test_ambiguity_blocks_and_p09_only_accepts_reasoned_supervisor_withdrawal():
    bundle = profile()
    bundle["documents"][0]["status"] = "ambiguous"
    assert checks(bundle)["P02"]["status"] == "incomplete"
    bundle = profile()
    bundle["expectations"] = [{"type": "attachment", "withdrawn": True, "role": "reviewer", "reason": "mistake"}]
    assert checks(bundle)["P09"]["status"] == "incomplete"
    bundle["expectations"][0]["role"] = "supervisor"
    assert checks(bundle)["P09"]["status"] == "passed"


def test_fixtures_have_expected_seeded_results():
    assert checks(profile("discrepant"))["P05"]["status"] == "flagged"
    assert checks(profile("incomplete"))["P03"]["status"] == "incomplete"
    assert checks(profile("corrected"))["P05"]["status"] == "passed"
    bundle = copy.deepcopy(profile())
    bundle["documents"][3]["extraction"]["financial"]["currency"] = "USD"
    assert checks(bundle)["P06"]["status"] == "unsupported"
