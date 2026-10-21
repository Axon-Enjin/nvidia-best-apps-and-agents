"""Isolated PDF rasterization and local Tesseract subprocess, never URL input."""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image

from sentinel.document_parser import detect_type, extract, restrict_parser
from sentinel.ocr import ENGLISH_SHA256

MAX_PIXELS = 40_000_000
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


def run(source, binary, expected_version):
    binary = str(Path(binary).resolve())
    restrict_parser(allowed_executable=binary)
    version = subprocess.run([binary,"--version"],executable=binary,capture_output=True,timeout=5,check=True).stdout.decode().splitlines()[0]
    if not re.search(r"\bv?"+re.escape(expected_version)+r"(?:\.|\s|$)",version):
        raise ValueError("OCR binary does not match pinned version.")
    # The model is pinned independently of an installer or Linux package.
    model_dir = Path(__import__('os').environ.get("TESSDATA_PREFIX", str(Path(binary).parent/"tessdata")))
    if hashlib.sha256((model_dir/"eng.traineddata").read_bytes()).hexdigest() != ENGLISH_SHA256:
        raise ValueError("English model differs from the pinned traineddata.")
    kind = detect_type(source)
    pdf = None
    if kind == "application/pdf":
        import pypdfium2
        pdf = pypdfium2.PdfDocument(source)
        count = len(pdf)
    else:
        count = 1
    if not 1 <= count <= 20:
        raise ValueError("Printed OCR supports at most 20 pages per document; no truncation.")
    pages = []
    with tempfile.TemporaryDirectory(prefix="sentinel-ocr-") as temp:
        for i in range(count):
            bitmap = page = None
            if pdf is not None:
                page = pdf[i]
                width,height = page.get_size()
                if width*height*(200/72)**2 > MAX_PIXELS:
                    raise ValueError("Raster pixel limit exceeded.")
                bitmap = page.render(scale=200/72)
                raster = bitmap.to_pil()
            else:
                raster = Image.open(BytesIO(source))
            if raster.width*raster.height > MAX_PIXELS:
                raise ValueError("Raster pixel limit exceeded.")
            path = Path(temp)/"page.png"
            raster.convert("RGB").save(path)
            text = subprocess.run([binary,str(path),"stdout","--tessdata-dir",str(model_dir),"-l","eng","--psm","6"],
                                  executable=binary,capture_output=True,timeout=10,check=True).stdout.decode("utf-8")
            if not text.strip():
                raise ValueError("No legible printed text.")
            pages.append(text)
            if sum(map(len,pages)) > 1_000_000:
                raise ValueError("OCR text limit exceeded.")
            raster.close()
            if bitmap:
                bitmap.close()
            if page:
                page.close()
    if pdf:
        pdf.close()
    result = extract("\f".join(pages).encode())
    result["content_type"] = kind
    result["extraction"]["extractor"] = "tesseract/"+version.replace("tesseract ","").lstrip("v")
    result["extraction"]["requires_confirmation"] = True
    result["extraction"]["english_sha256"] = ENGLISH_SHA256
    if not result["extraction"]["fields"] or result["status"] != "readable":
        raise ValueError("Printed source fields are not reliably located.")
    result["status"] = "needs_confirmation"
    result["problems"] = ["Confirm legible printed values against the original. Handwriting is unsupported."]
    return result


if __name__ == "__main__":
    data = sys.stdin.buffer.read(25*1024*1024+1)
    sys.stdout.write(json.dumps(run(data,sys.argv[1],sys.argv[2])))
