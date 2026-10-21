"""Bounded extraction. Image-only PDFs remain incomplete; no pretend OCR."""

from io import BytesIO

from pypdf import PdfReader

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_TEXT_CHARS = 80_000
MAX_PDF_PAGES = 30


def extract_chart(content: bytes, filename: str) -> str:
    if not content:
        raise ValueError("The chart is empty. Upload a text chart or a text-based PDF.")
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("Each file must be 5 MB or smaller.")
    if filename.lower().endswith(".txt"):
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("Save the chart as UTF-8 text and upload it again.") from exc
        if "\x00" in text:
            raise ValueError("The chart contains binary data. Upload UTF-8 text or a PDF.")
    elif filename.lower().endswith(".pdf"):
        try:
            reader = PdfReader(BytesIO(content), strict=True)
            if reader.is_encrypted:
                raise ValueError("The PDF is encrypted. Export an authorized readable copy.")
            if len(reader.pages) > MAX_PDF_PAGES:
                raise ValueError("Charts are limited to 30 PDF pages in this prototype.")
            parts = []
            length = 0
            for page in reader.pages:
                part = page.extract_text() or ""
                length += len(part)
                if length > MAX_TEXT_CHARS:
                    raise ValueError("The chart exceeds the 80,000-character extraction limit.")
                parts.append(part)
            text = "\n\n".join(parts)
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError("The PDF could not be read. Export a text-based PDF or UTF-8 chart.") from exc
    else:
        raise ValueError("Charts must be .txt or .pdf files.")
    if not text.strip():
        raise ValueError("No readable text was found. Scanned PDFs need OCR before upload.")
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError("The chart exceeds the 80,000-character extraction limit.")
    return text.strip()
