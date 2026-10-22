"use client";

import { useEffect, useId, useRef, useState, type FormEvent, type ReactNode } from "react";

import { describedBy, Field } from "@/components/ui/field";
import { documentLabel } from "@/features/case/labels";
import { DISCARD_DRAFT } from "@/features/session/use-draft-guard";
import type { EvidenceRef } from "@/lib/api-types";

import { EvidencePicker, type EvidenceOptions } from "./evidence-picker";
import { selectionAnchors, type EvidenceSelection } from "./evidence-selection";
import { useActionForm, type ActionContext, type ActionPayload } from "./use-action-form";

export type ActionFields = { reason: string; department: string; person: string; anchors: EvidenceRef[] };

const CONFLICT = "This case changed since you opened it. Your draft is kept. Load the latest version, then save again.";

/**
 * One review action: optionally revealed behind its primary button, with only
 * the fields that action needs. Values survive every recoverable error.
 */
export function ActionForm({
  context,
  revealLabel,
  emphasis = "primary",
  intro,
  reasonLabel,
  submitLabel,
  owner = false,
  evidence,
  build,
  savedMessage,
  onDirtyChange,
  onSaved,
}: {
  context: ActionContext;
  revealLabel?: string;
  emphasis?: "primary" | "secondary";
  intro?: ReactNode;
  reasonLabel: string;
  submitLabel: string;
  owner?: boolean;
  evidence?: EvidenceOptions;
  build: (fields: ActionFields) => ActionPayload;
  savedMessage: string;
  onDirtyChange?: (dirty: boolean) => void;
  onSaved?: () => void;
}) {
  const prefix = useId().replace(/:/g, "");
  const { pending, conflict, refreshing, error, submit, loadLatest } = useActionForm(context);
  const summary = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(!revealLabel);
  const [reason, setReason] = useState("");
  const [department, setDepartment] = useState("");
  const [person, setPerson] = useState("");
  const [selection, setSelection] = useState<EvidenceSelection>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const dirty = Boolean(reason || department || person || Object.values(selection).some((choice) => choice.checked));

  const report = useRef(onDirtyChange);
  useEffect(() => {
    report.current = onDirtyChange;
  });
  useEffect(() => {
    report.current?.(dirty);
  }, [dirty]);
  useEffect(() => () => report.current?.(false), []);

  useEffect(() => {
    if (Object.keys(errors).length) summary.current?.focus();
  }, [errors]);

  function reset() {
    setReason("");
    setDepartment("");
    setPerson("");
    setSelection({});
    setErrors({});
    if (revealLabel) setOpen(false);
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const found: Record<string, string> = {};
    if (!reason.trim()) found.reason = `Enter the ${reasonLabel.toLowerCase()}.`;
    if (owner && !department.trim()) found.department = "Name the responsible department.";
    if (owner && !person.trim()) found.person = "Name the responsible person.";
    let anchors: EvidenceRef[] = [];
    if (evidence) {
      const chosen = selectionAnchors(selection, evidence.documents);
      anchors = chosen.anchors;
      Object.assign(found, chosen.errors);
      const types = new Set(evidence.documents.filter((document) => selection[document.id]?.checked).map((document) => document.type));
      const missing = [...new Set(evidence.required)].filter((type) => !types.has(type));
      if (!anchors.length && !Object.keys(chosen.errors).length) found.evidence = "Select at least one document you compared.";
      else if (missing.length) found.evidence = `Also select ${missing.map((type) => documentLabel(type)).join(", ")}.`;
    }
    setErrors(found);
    if (Object.keys(found).length) return;
    const saved = await submit(build({ reason: reason.trim(), department: department.trim(), person: person.trim(), anchors }), savedMessage);
    if (saved) {
      reset();
      onSaved?.();
    }
  }

  if (!open) {
    return (
      <div className="grid gap-3">
        {intro}
        <button type="button" className={`btn ${emphasis === "primary" ? "btn-primary" : "btn-secondary"} justify-self-start`} onClick={() => setOpen(true)}>
          {revealLabel}
        </button>
      </div>
    );
  }

  const messages = Object.entries(errors);
  return (
    <form onSubmit={save} noValidate className="grid gap-4">
      {intro}
      {messages.length ? (
        <div ref={summary} role="alert" tabIndex={-1} className="border-l-4 border-blocking bg-blocking-tint px-4 py-3">
          <p className="font-semibold text-blocking">Check these before saving:</p>
          <ul className="mt-1 list-disc pl-5 text-sm">
            {messages.map(([key, message]) => (
              <li key={key}>{message}</li>
            ))}
          </ul>
        </div>
      ) : null}
      <Field id={`${prefix}-reason`} label={reasonLabel} required error={errors.reason}>
        <textarea
          id={`${prefix}-reason`}
          className="input"
          value={reason}
          maxLength={2000}
          required
          autoFocus={Boolean(revealLabel)}
          aria-invalid={errors.reason ? "true" : undefined}
          aria-describedby={describedBy(`${prefix}-reason`, { error: errors.reason })}
          onChange={(event) => setReason(event.currentTarget.value)}
        />
      </Field>
      {owner ? (
        <div className="grid gap-4 sm:grid-cols-2">
          <Field id={`${prefix}-department`} label="Responsible department" required error={errors.department}>
            <input
              id={`${prefix}-department`}
              className="input"
              value={department}
              maxLength={200}
              required
              aria-invalid={errors.department ? "true" : undefined}
              aria-describedby={describedBy(`${prefix}-department`, { error: errors.department })}
              onChange={(event) => setDepartment(event.currentTarget.value)}
            />
          </Field>
          <Field id={`${prefix}-person`} label="Responsible person" required error={errors.person}>
            <input
              id={`${prefix}-person`}
              className="input"
              value={person}
              maxLength={200}
              required
              aria-invalid={errors.person ? "true" : undefined}
              aria-describedby={describedBy(`${prefix}-person`, { error: errors.person })}
              onChange={(event) => setPerson(event.currentTarget.value)}
            />
          </Field>
        </div>
      ) : null}
      {evidence ? (
        <div className="grid gap-1">
          <EvidencePicker idPrefix={prefix} options={evidence} selection={selection} errors={errors} onChange={setSelection} />
          {errors.evidence ? <p className="field-error">{errors.evidence}</p> : null}
        </div>
      ) : null}
      {conflict ? (
        <div role="alert" className="grid gap-2 border-l-4 border-attention bg-attention-tint px-4 py-3">
          <p className="font-semibold text-attention">{CONFLICT}</p>
          <button type="button" className="btn btn-secondary justify-self-start" onClick={loadLatest}>
            Load latest
          </button>
        </div>
      ) : null}
      {error ? (
        <p role="alert" className="border-l-4 border-blocking bg-blocking-tint px-4 py-3 font-semibold text-blocking">
          {error}
        </p>
      ) : null}
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="submit"
          className={`btn ${emphasis === "primary" ? "btn-primary" : "btn-secondary"}`}
          aria-disabled={pending ? "true" : undefined}
          disabled={conflict || refreshing}
        >
          {pending ? "Saving…" : refreshing ? "Loading latest…" : submitLabel}
        </button>
        {revealLabel ? (
          <button
            type="button"
            className="link-button"
            onClick={() => {
              if (!dirty || window.confirm(DISCARD_DRAFT)) reset();
            }}
          >
            Cancel
          </button>
        ) : null}
      </div>
    </form>
  );
}
