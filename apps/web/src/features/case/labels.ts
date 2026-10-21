// Plain-language names for technical identifiers. Identifiers stay visible as
// secondary references wherever they matter (check IDs, action codes).

const DOCUMENT_LABELS: Record<string, string> = {
  cf2: "CF2 claim summary",
  cf4: "CF4 clinical summary",
  cf5: "CF5 supplementary summary",
  esoa: "Statement of account (eSOA)",
  discharge: "Discharge summary",
  csf: "CSF signature form",
  eligibility: "Eligibility evidence",
};

export function documentLabel(type: string, filename?: string): string {
  if (type === "attachment") return filename ? `Attachment ${filename}` : "Attachment";
  return DOCUMENT_LABELS[type] ?? type.toUpperCase();
}
