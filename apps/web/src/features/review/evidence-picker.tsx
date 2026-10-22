"use client";

import { documentLabel } from "@/features/case/labels";
import type { SourceDocument } from "@/lib/api-types";

import { parsePages, type EvidenceSelection } from "./evidence-selection";

export type EvidenceOptions = {
  documents: SourceDocument[];
  /** Documents cited by the selected issue, listed first; never preselected. */
  suggested: Record<string, number[]>;
  /** Document types the review service requires for this action. */
  required: string[];
  /** Effective status per document id; only readable documents can be cited. */
  statuses: Record<string, string>;
  version: number;
};

export function evidenceSummary(selection: EvidenceSelection, documents: SourceDocument[]): string {
  const parts = documents.flatMap((document) => {
    const choice = selection[document.id];
    if (!choice?.checked) return [];
    const pages = parsePages(choice.pages, document.page_count);
    const label = documentLabel(document.type, document.filename);
    return [typeof pages === "string" ? `${label} (check pages)` : `${label} page${pages.length > 1 ? "s" : ""} ${pages.join(", ")}`];
  });
  return parts.length ? parts.join("; ") : "none";
}

/** Evidence the reviewer compared, chosen explicitly; opening a source never selects it. */
export function EvidencePicker({
  idPrefix,
  options,
  selection,
  errors,
  onChange,
}: {
  idPrefix: string;
  options: EvidenceOptions;
  selection: EvidenceSelection;
  errors: Record<string, string>;
  onChange: (next: EvidenceSelection) => void;
}) {
  const order = [...options.documents].sort((a, b) => {
    const rank = (document: SourceDocument) =>
      options.required.includes(document.type) ? 0 : options.suggested[document.id] ? 1 : 2;
    return rank(a) - rank(b);
  });
  const requiredLabels = [...new Set(options.required)].map((type) => documentLabel(type));

  return (
    <fieldset className="grid gap-2" aria-describedby={`${idPrefix}-evidence-help`}>
      <legend className="label">Evidence from version {options.version}</legend>
      <p id={`${idPrefix}-evidence-help`} className="help">
        Select the documents and pages you compared.
        {requiredLabels.length ? ` Required for this review: ${requiredLabels.join(", ")}.` : ""}
      </p>
      <ul className="divide-y divide-rule-faint border-y border-rule-faint">
        {order.map((document) => {
          const id = `${idPrefix}-doc-${document.id}`;
          const label = documentLabel(document.type, document.filename);
          const choice = selection[document.id] ?? { checked: false, pages: (options.suggested[document.id] ?? [1]).join(", ") };
          const readable = (options.statuses[document.id] ?? document.status) === "readable";
          const tag = options.required.includes(document.type) ? "Required" : options.suggested[document.id] ? "In this issue" : null;
          return (
            <li key={document.id} className="grid grid-cols-[auto_minmax(0,1fr)] items-center gap-x-3 gap-y-1 py-2 sm:grid-cols-[auto_minmax(0,1fr)_7rem]">
              <input
                id={id}
                type="checkbox"
                className="size-5 accent-forest"
                checked={choice.checked}
                disabled={!readable}
                onChange={(event) => onChange({ ...selection, [document.id]: { ...choice, checked: event.currentTarget.checked } })}
              />
              <div className="min-w-0">
                <label htmlFor={id} className="font-semibold">
                  {label}
                </label>
                {tag ? <span className="ml-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">{tag}</span> : null}
                {!readable ? <p className="text-sm text-ink-muted">Not readable; it cannot be cited until it is confirmed or replaced.</p> : null}
                {errors[document.id] ? <p className="field-error">{errors[document.id]}</p> : null}
              </div>
              <input
                aria-label={`Pages for ${label}`}
                className="input col-start-2 min-h-10 w-28 py-1.5 sm:col-start-3 sm:w-full"
                value={choice.pages}
                disabled={!choice.checked}
                inputMode="numeric"
                onChange={(event) => onChange({ ...selection, [document.id]: { ...choice, pages: event.currentTarget.value } })}
              />
            </li>
          );
        })}
      </ul>
      <p className="text-sm">
        <span className="font-semibold">Selected evidence:</span> {evidenceSummary(selection, options.documents)}
      </p>
    </fieldset>
  );
}
