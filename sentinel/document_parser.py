"""Private subprocess entry point. Never serves or executes source content."""
import json
import os
import re
import sys
from io import BytesIO

from defusedxml import ElementTree
from pypdf import PdfReader

MAX_TEXT = 1_000_000
MAX_PAGES = 150
MAX_NODES = 10_000
FIELD_NAMES = {
    "facilityid": "facility_id", "encounterref": "encounter_ref", "claimref": "claim_ref",
    "claimid": "claim_ref", "patientid": "patient_id", "dob": "dob", "dateofbirth": "dob",
    "admissiondate": "admission_date", "dischargedate": "discharge_date", "diagnosis": "diagnosis",
    "diagnosiscode": "diagnosis_code", "disposition": "disposition", "scope": "scope",
    "admissionreason": "admission_reason", "course": "course", "treatment": "treatment", "outcome": "outcome",
    "currency": "currency", "total": "total", "printedname": "printed_name", "mark": "mark", "signeddate": "signed_date",
}


def detect_type(content):
    if content.startswith(b"%PDF-"):
        return "application/pdf"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    try:
        text = content.decode("utf-8-sig")
        if "\x00" in text:
            return "application/octet-stream"
    except UnicodeError:
        return "application/octet-stream"
    return "application/xml" if text.lstrip().startswith("<") else "text/plain"


def extract(content):
    kind = detect_type(content)
    result = {"content_type": kind, "status": "unreadable", "page_count": 0, "problems": [],
              "extraction": {"fields": {}, "anchors": [], "pages": [], "extractor": "local-text/1"}}
    extraction = result["extraction"]
    anchors = extraction["anchors"]

    def anchor(label, value, page, **location):
        field = FIELD_NAMES.get(re.sub(r"[^a-z0-9]", "", label.lower()))
        if field:
            if len(anchors) >= MAX_NODES or len(value) > 10000:
                raise ValueError("Extracted field/anchor limit exceeded; source was not truncated.")
            anchors.append({"field": field, "value": value.strip(), "page": page, **location})

    try:
        if len(content) > 25 * 1024 * 1024:
            raise ValueError("Source exceeds the 25 MB limit.")
        if kind == "application/pdf":
            reader = PdfReader(BytesIO(content), strict=True)
            if reader.is_encrypted:
                raise ValueError("Encrypted PDFs require an authorized readable replacement.")
            result["page_count"] = len(reader.pages)
            if result["page_count"] > MAX_PAGES:
                raise ValueError("PDF exceeds the 150-page version limit.")
            pages, length = [], 0
            for page in reader.pages:
                stream = page.get_contents()
                if stream is not None and len(stream.get_data()) > 8 * 1024 * 1024:
                    raise ValueError("PDF page content exceeds the extraction limit.")
                text = page.extract_text() or ""
                length += len(text)
                if length > MAX_TEXT:
                    raise ValueError("Text extraction limit exceeded; source was not truncated.")
                pages.append(text)
        elif kind == "application/xml":
            text = content.decode("utf-8-sig")
            if len(text) > MAX_TEXT:
                raise ValueError("XML text limit exceeded; source was not truncated.")
            result["page_count"] = 1
            root = ElementTree.fromstring(text, forbid_dtd=True, forbid_entities=True, forbid_external=True)
            elements = list(root.iter())
            if len(elements) > MAX_NODES:
                raise ValueError("XML element limit exceeded.")

            def walk(element, path, depth=0):
                if depth > 64:
                    raise ValueError("XML nesting limit exceeded.")
                if not len(element):
                    anchor(element.tag, element.text or "", 1, path=path)
                counts = {}
                for child in element:
                    counts[child.tag] = counts.get(child.tag, 0) + 1
                    walk(child, f"{path}/{child.tag}[{counts[child.tag]}]", depth + 1)
            walk(root, "/" + root.tag)
            extraction["xml_root"] = root.tag
            if root.tag == "SampleESOA" and root.get("version") == "1":
                extraction["financial"] = {"currency": root.findtext("Currency"), "total": root.findtext("Total"),
                                           "lines": [{"gross": item.findtext("Gross"), "discount": item.findtext("Discount")}
                                                     for item in root.findall("./Lines/Line")]}
            pages = [text]
        elif kind == "text/plain":
            text = content.decode("utf-8-sig")
            pages = text.split("\f")
            result["page_count"] = len(pages)
            if len(text) > MAX_TEXT or len(pages) > MAX_PAGES:
                raise ValueError("Text/page limit exceeded; source was not truncated.")
        else:
            result["status"] = "unsupported"
            result["page_count"] = 1 if kind.startswith("image/") else 0
            result["problems"] = ["No supported local extraction for this content type."]
            return result
        extraction["pages"] = pages
        if not any(page.strip() for page in pages):
            raise ValueError("No readable text; printed scans require local OCR and confirmation.")
        if kind != "application/xml":
            for page_number, text in enumerate(pages, 1):
                for line_number, line in enumerate(text.splitlines(), 1):
                    label, separator, value = line.partition(":")
                    if separator:
                        anchor(label, value, page_number, line=line_number)
        for field in {item["field"] for item in anchors}:
            values = {item["value"] for item in anchors if item["field"] == field}
            if len(values) == 1:
                extraction["fields"][field] = next(iter(values))
            else:
                result["problems"].append(field)
        result["status"] = "ambiguous" if result["problems"] else "readable"
    except Exception:
        # Neither parser exceptions nor malformed source values leave this child.
        result["status"] = "unreadable"
        result["problems"] = ["Cannot extract within supported limits. Inspect or replace the original."]
        extraction["fields"] = {}
        extraction["anchors"] = []
        extraction["pages"] = []
    return result


def restrict_parser():
    """Apply a process memory cap before a potentially explosive PDF/XML parse."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        class BasicLimits(ctypes.Structure):
            _fields_ = [("process_time", ctypes.c_longlong), ("job_time", ctypes.c_longlong),
                        ("flags", wintypes.DWORD), ("minimum", ctypes.c_size_t), ("maximum", ctypes.c_size_t),
                        ("active", wintypes.DWORD), ("affinity", ctypes.c_size_t),
                        ("priority", wintypes.DWORD), ("scheduling", wintypes.DWORD)]

        class IoCounters(ctypes.Structure):
            _fields_ = [(name, ctypes.c_ulonglong) for name in ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]

        class ExtendedLimits(ctypes.Structure):
            _fields_ = [("basic", BasicLimits), ("io", IoCounters), ("process_memory", ctypes.c_size_t),
                        ("job_memory", ctypes.c_size_t), ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t)]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.restype = wintypes.HANDLE
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        job = kernel.CreateJobObjectW(None, None)
        limits = ExtendedLimits()
        limits.basic.flags = 0x100  # JOB_OBJECT_LIMIT_PROCESS_MEMORY
        limits.process_memory = 512 * 1024 * 1024
        if not job or not kernel.SetInformationJobObject(job, 9, ctypes.byref(limits), ctypes.sizeof(limits)) or not kernel.AssignProcessToJobObject(job, kernel.GetCurrentProcess()):
            raise RuntimeError("Cannot establish parser memory isolation.")
        # The anonymous job's handle stays open until process exit.
    else:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_CPU, (10, 10))

    def audit(event, args):
        if event in {"socket.connect", "socket.getaddrinfo", "subprocess.Popen"}:
            raise PermissionError("Parser network and subprocess access is disabled.")
    sys.addaudithook(audit)


if __name__ == "__main__":
    restrict_parser()
    original = sys.stdin.buffer.read(25 * 1024 * 1024 + 1)
    sys.stdout.buffer.write(json.dumps(extract(original), ensure_ascii=True).encode())
