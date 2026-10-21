"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { describedBy, Field } from "@/components/ui/field";
import { ExternalLink } from "@/components/ui/icons";
import { useStatus } from "@/components/ui/notice";
import { documentLabel, fieldLabel } from "@/features/case/labels";
import { useSession } from "@/features/session/session-provider";
import { errorText } from "@/lib/api-client";
import type { ConfirmationRequirement, ConfirmResult, SourceDocument } from "@/lib/api-types";

import { originalHref } from "./documents-table";

export type ScanItem = { document: SourceDocument; requirement: ConfirmationRequirement };

/**
 * Printed-scan values are confirmed one field at a time beside the original.
 * Each confirmation is an explicit, reasoned, attributable event; the OCR
 * reading itself is kept unchanged.
 */
export function ConfirmScans({ revision, items }: { revision: number; items: ScanItem[] }) {
  const router = useRouter();
  const { request } = useSession();
  const { announce } = useStatus();
  const [documentIndex, setDocumentIndex] = useState(0);
  const [chosenField, setChosenField] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [pending, setPending] = useState(false);

  const item = items[Math.min(documentIndex, items.length - 1)];
  if (!item) return null;
  const { document, requirement } = item;
  const field = chosenField && requirement.pending.includes(chosenField) ? chosenField : requirement.pending[0];
  if (!field) return null;
  const reading = document.extraction.fields[field] ?? "";
  const anchorPage = document.extraction.anchors.find((anchor) => anchor.field === field)?.page ?? 1;
  const label = documentLabel(document.type, document.filename);
  const image = document.content_type === "image/png" || document.content_type === "image/jpeg";

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending || !field) return;
    const data = new FormData(event.currentTarget);
    const value = String(data.get("value") ?? "").trim();
    const reason = String(data.get("reason") ?? "").trim();
    const page = Number(data.get("page"));
    const found: Record<string, string> = {};
    if (!value) found.value = "Enter the value printed on the source.";
    if (!reason) found.reason = "Say how you confirmed this value.";
    if (!Number.isInteger(page) || page < 1 || page > document.page_count) found.page = `Choose a page from 1 to ${document.page_count}.`;
    if (data.get("legible") !== "on") found.legible = "Confirm that you can read this printed source.";
    setErrors(found);
    if (Object.keys(found).length) return;
    setPending(true);
    try {
      await request<ConfirmResult>(`/api/documents/${document.id}/confirm`, {
        method: "POST",
        json: { expected_revision: revision, anchor: { page, field }, value, reason, source_kind: "printed" },
      });
      announce(`Confirmed ${fieldLabel(field)} on ${label}. The original reading is kept.`);
      setChosenField(null);
      router.refresh();
    } catch (failure) {
      setErrors({ form: errorText(failure) });
    } finally {
      setPending(false);
    }
  }

  return (
    <section aria-labelledby="confirm-heading" className="grid gap-4">
      <div className="border-t border-ink pt-3">
        <h2 id="confirm-heading" className="text-lg">
          Confirm scanned values
        </h2>
        <p className="mt-1 max-w-3xl text-ink-muted">
          Compare each reading with the printed original and confirm it. Only legible printed values can be confirmed;
          handwritten or unreadable content needs a corrected original. Confirmations reopen manual review.
        </p>
      </div>

      {items.length > 1 ? (
        <div role="group" aria-label="Scanned documents" className="flex flex-wrap gap-2">
          {items.map((entry, index) => (
            <button
              key={entry.document.id}
              type="button"
              aria-pressed={index === documentIndex}
              onClick={() => {
                setDocumentIndex(index);
                setChosenField(null);
              }}
              className="btn btn-secondary aria-pressed:bg-teal-tint"
            >
              {documentLabel(entry.document.type, entry.document.filename)}
            </button>
          ))}
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-[minmax(18rem,26rem)_minmax(0,1fr)]">
        <div className="grid content-start gap-4">
          <form onSubmit={submit} noValidate className="panel grid gap-4 p-4">
            <p className="font-semibold">
              {fieldLabel(field)}
              <span className="doc-ref ml-2 font-normal text-ink-muted">reading: {reading || "not read"}</span>
            </p>
            <Field id="confirm-value" label="Confirmed value" required error={errors.value}>
              <input
                key={`${document.id}-${field}-value`}
                id="confirm-value"
                name="value"
                className="input doc-ref"
                defaultValue={reading}
                maxLength={10000}
                required
                aria-invalid={errors.value ? "true" : undefined}
                aria-describedby={describedBy("confirm-value", { error: errors.value })}
              />
            </Field>
            <Field id="confirm-page" label="Page" error={errors.page}>
              <input
                key={`${document.id}-${field}-page`}
                id="confirm-page"
                name="page"
                type="number"
                min={1}
                max={document.page_count}
                defaultValue={anchorPage}
                className="input w-28"
                aria-invalid={errors.page ? "true" : undefined}
                aria-describedby={describedBy("confirm-page", { error: errors.page })}
              />
            </Field>
            <Field id="confirm-reason" label="Confirmation reason" required error={errors.reason}>
              <textarea
                id="confirm-reason"
                name="reason"
                className="input"
                maxLength={2000}
                required
                aria-invalid={errors.reason ? "true" : undefined}
                aria-describedby={describedBy("confirm-reason", { error: errors.reason })}
              />
            </Field>
            <div className="grid gap-1">
              <label className="flex min-h-11 items-center gap-3 font-semibold">
                <input
                  key={`${document.id}-${field}-legible`}
                  type="checkbox"
                  name="legible"
                  className="size-5 accent-forest"
                  aria-invalid={errors.legible ? "true" : undefined}
                />
                I can read this printed source
              </label>
              {errors.legible ? <p className="field-error">{errors.legible}</p> : null}
            </div>
            {errors.form ? (
              <p role="alert" className="field-error">
                {errors.form}
              </p>
            ) : null}
            <button type="submit" className="btn btn-primary justify-self-start" disabled={pending}>
              Confirm value
            </button>
          </form>
          <div>
            <p className="eyebrow">Values to confirm on {label}</p>
            <ul aria-label="Scan values" className="mt-2 divide-y divide-rule-faint border-y border-rule bg-surface">
              {requirement.pending.map((key) => (
                <li key={key}>
                  <button
                    type="button"
                    aria-pressed={key === field}
                    onClick={() => setChosenField(key)}
                    className="flex w-full min-h-11 items-baseline justify-between gap-4 px-3 py-2 text-left transition-colors hover:bg-teal-tint aria-pressed:bg-teal-tint aria-pressed:shadow-[inset_3px_0_0_var(--color-teal)]"
                  >
                    <span className="font-semibold">{fieldLabel(key)}</span>
                    <span className="doc-ref text-ink-muted">{document.extraction.fields[key] ?? "not read"}</span>
                  </button>
                </li>
              ))}
            </ul>
            <p className="mt-2 text-sm text-ink-muted">
              {Object.keys(requirement.confirmed).length} confirmed · {requirement.pending.length} to confirm
            </p>
          </div>

        </div>

        <figure className="grid content-start gap-2">
          <figcaption className="doc-ref flex flex-wrap items-center justify-between gap-2 border-b border-ink pb-2 uppercase">
            <span>
              {label} · page {anchorPage} · original
            </span>
            <a href={originalHref(document)} target="_blank" rel="noopener" className="inline-flex items-center gap-1 normal-case">
              Open original
              <ExternalLink aria-hidden="true" className="size-4" />
            </a>
          </figcaption>
          {image ? (
            // Authenticated same-origin preview of the stored original; next/image would add an optimizer hop.
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={`/api/documents/${document.id}/preview`}
              alt={`Original ${label}, page 1`}
              className="max-h-[42rem] w-full border border-rule bg-surface object-contain object-top"
            />
          ) : (
            <p className="panel p-4">This original is a PDF. Open it to compare each value.</p>
          )}
        </figure>
      </div>
    </section>
  );
}
