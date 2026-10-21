import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from sentinel.document_parser import extract
from sentinel.profile import evaluate_profile

ROOT = Path(__file__).parent/"fixtures"/"evaluation"
LOCK = json.loads((ROOT/"locked-manifest.json").read_text())


def load_profile(path):
    manifest = json.loads((path/"manifest.json").read_text())
    documents = []
    for i,member in enumerate(manifest["documents"]):
        source = (path/member["filename"]).read_bytes()
        assert hashlib.sha256(source).hexdigest() == member["sha256"]
        documents.append({"id":str(i),"type":member["type"],"sha256":member["sha256"],**extract(source)})
    return evaluate_profile({"id":path.name,"manifest":manifest,"documents":documents})


def test_locked_set_has_independent_labels_and_expected_distribution():
    assert Counter(c["label"] for c in LOCK["cases"]) == {"discrepancy":20,"clean":10,"incomplete_adversarial":10}
    assert len({c["manifest_sha256"] for c in LOCK["cases"]}) == 40


@pytest.mark.parametrize("case",LOCK["cases"],ids=lambda c:c["id"])
def test_heldout_content_findings_anchors_and_corrected_pairs(case):
    path = ROOT/case["id"]
    assert hashlib.sha256((path/"manifest.json").read_bytes()).hexdigest() == case["manifest_sha256"]
    result = load_profile(path)
    checks = {c["id"]:c for c in result["checks"]}
    for expected in case["expected"]:
        assert checks[expected["id"]]["status"] == expected["status"]
    manifest = json.loads((path/"manifest.json").read_text())
    for evidence in case["evidence"]:
        index = next(i for i,d in enumerate(manifest["documents"]) if d["type"] == evidence["document_type"])
        assert any(a["document_id"] == str(index) and a["field"] == evidence["field"] and a["value"] == evidence["value"] and a["page"] == evidence["page"]
                   for check in result["checks"] for a in check["anchors"])
    assert result["outcome"] == "incomplete" and result["model_status"] == "not_run_offline"
    if case["corrected_path"]:
        assert hashlib.sha256((ROOT/case["corrected_path"]/"manifest.json").read_bytes()).hexdigest() == case["corrected_manifest_sha256"]
        revised = load_profile(ROOT/case["corrected_path"])
        assert all(c["status"] == "passed" for c in revised["checks"][:6])
        assert revised["checks"][6]["status"] == "incomplete"


def test_heldout_text_and_actual_printed_equivalents_keep_identical_candidates():
    from sentinel.ocr import extract_document
    case = next(c for c in LOCK["cases"] if c["id"] == "heldout-30")
    for scan in case["scan_equivalents"]:
        source = (ROOT/case["id"]/scan["filename"]).read_bytes()
        assert hashlib.sha256(source).hexdigest() == scan["sha256"]
        result = extract_document(source)
        assert result["status"] == "needs_confirmation"
        assert result["extraction"]["fields"]["patient_id"] == "FICTION-0030"
        assert result["extraction"]["fields"]["discharge_date"] == "2026-08-17"
