"""Bounded local OCR. Every recognized scan field remains a source-confirmation candidate."""
import json
import os
import shutil
import subprocess
import sys

from sentinel.config import workspace_root
from sentinel.document_parser import detect_type
from sentinel.documents import extract_original

ENGLISH_SHA256 = "7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2"


def ocr_binary():
    return os.getenv("OCR_BINARY") or shutil.which("tesseract") or str(workspace_root() / "data" / "tools" / "tesseract" / "tesseract.exe")


def extract_document(source, limits=None, *, binary=None, expected_version=None):
    kind = detect_type(source)
    parsed = extract_original(source)
    if kind not in {"image/png", "image/jpeg", "application/pdf"}:
        return parsed
    if kind == "application/pdf" and parsed["status"] == "readable" and all(p.strip() for p in parsed["extraction"]["pages"]):
        return parsed
    failed = {"content_type":kind, "page_count":parsed["page_count"], "status":"unreadable",
              "problems":["Local printed OCR failed or exceeded limits. Inspect or replace the original; no remote fallback."],
              "extraction":{"fields":{}, "anchors":[], "pages":[], "extractor":"tesseract/not_run"}}
    try:
        result = subprocess.run([sys.executable, "-m", "sentinel.ocr_worker", binary or ocr_binary(),
                                 expected_version or os.getenv("OCR_EXPECTED_VERSION", "5.5.3")], input=source,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=90, check=True)
        if len(result.stdout) > 8*1024*1024:
            return failed
        return json.loads(result.stdout)
    except (subprocess.SubprocessError, OSError, ValueError):
        return failed
