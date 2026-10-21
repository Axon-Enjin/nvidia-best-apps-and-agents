"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState, type FormEvent } from "react";

import { describedBy, Field } from "@/components/ui/field";
import { useStatus } from "@/components/ui/notice";
import { StatusText, type Tone } from "@/components/ui/status-text";
import { documentLabel } from "@/features/case/labels";
import { useSession } from "@/features/session/session-provider";
import { errorText, SessionExpiredError } from "@/lib/api-client";
import type { CaseRecord } from "@/lib/api-types";

import { formatBytes, sha256Hex } from "./file-hash";
import { identityMismatches, IDENTITY_FIELDS, matchFiles, parseManifest, type Manifest, type RowStatus } from "./manifest";
import { ImportFailure, submitImport } from "./submit-import";

type HashedFile = { file: File; name: string; sha256: string };
type ManifestState = { manifest: Manifest } | { error: string } | null;

const MAX_FILE = 25 * 1024 * 1024;
const MAX_VERSION = 100 * 1024 * 1024;
const MAX_FILES = 30;

const ROW_STATUS: Record<RowStatus, { tone: Tone; text: string }> = {
  selected: { tone: "passed", text: "Selected" },
  missing: { tone: "neutral", text: "Missing" },
  hash_mismatch: { tone: "blocking", text: "Does not match the manifest's SHA-256" },
  duplicate: { tone: "blocking", text: "Selected twice" },
};

function StepHeading({ id, step, nested, children }: { id: string; step: string; nested: boolean; children: string }) {
  const Heading = nested ? "h3" : "h2";
  return (
    <Heading id={id} className={`flex items-baseline gap-3 pt-3 ${nested ? "border-t border-rule text-base" : "border-t border-ink text-lg"}`}>
      <span className="doc-ref text-ink-muted">{step}</span>
      {children}
    </Heading>
  );
}

type IntakeProps = ({ mode: "new" } | { mode: "replace"; claim: CaseRecord }) & {
  /** Inside the Import phase the form sits under its own heading and is not the page's primary action. */
  nested?: boolean;
};

export function IntakeForm(props: IntakeProps) {
  const nested = props.nested ?? false;
  const router = useRouter();
  const { request } = useSession();
  const { announce } = useStatus();
  const form = useRef<HTMLFormElement>(null);
  const errorRef = useRef<HTMLParagraphElement>(null);
  const blockedRef = useRef<HTMLParagraphElement>(null);
  const selection = useRef(0);
  const [manifestState, setManifestState] = useState<ManifestState>(null);
  const [files, setFiles] = useState<HashedFile[]>([]);
  const [hashing, setHashing] = useState(false);
  const [pending, setPending] = useState(false);
  const [stage, setStage] = useState<string | null>(null);
  const [error, setError] = useState<{ text: string; attempt: number } | null>(null);
  const [createdCaseId, setCreatedCaseId] = useState<string | undefined>(undefined);
  // One key per selection: a retry of the same selection reuses it, so the service never stores the version twice.
  const [idempotencyKey, setIdempotencyKey] = useState(() => crypto.randomUUID());

  useEffect(() => {
    if (error) errorRef.current?.focus();
  }, [error]);

  const manifest = manifestState && "manifest" in manifestState ? manifestState.manifest : null;
  const match = manifest ? matchFiles(manifest, files) : null;
  const totalBytes = files.reduce((sum, item) => sum + item.file.size, 0);
  const mismatched = manifest && props.mode === "replace" ? identityMismatches(manifest, props.claim) : [];

  let blocked: string | null = null;
  if (!manifestState) blocked = "Choose the manifest first.";
  else if ("error" in manifestState) blocked = manifestState.error;
  else if (mismatched.length) blocked = `This manifest names a different ${mismatched.join(", ")}. A corrected version keeps the claim's identity.`;
  else if (hashing) blocked = "Checking files…";
  else if (files.some((item) => item.file.size > MAX_FILE)) blocked = "Each original must be 25 MB or smaller.";
  else if (totalBytes > MAX_VERSION || files.length > MAX_FILES) blocked = "A version holds at most 30 files and 100 MB.";
  else if (match && (match.extras.length || match.rows.some((row) => row.status === "hash_mismatch" || row.status === "duplicate")))
    blocked = "Replace or remove the files marked above, then continue.";
  else if (!match?.ready) blocked = "Select every document named in the manifest to continue.";

  async function chooseManifest(input: HTMLInputElement) {
    const file = input.files?.[0];
    const next = file ? parseManifest(await file.text()) : null;
    const previous = manifest;
    setManifestState(next);
    setIdempotencyKey(crypto.randomUUID());
    const sameIdentity =
      previous && next && "manifest" in next && IDENTITY_FIELDS.every(([key]) => previous[key] === next.manifest[key]);
    if (!sameIdentity) setCreatedCaseId(undefined);
  }

  async function chooseOriginals(input: HTMLInputElement) {
    const chosen = Array.from(input.files ?? []);
    const token = ++selection.current;
    setHashing(true);
    const hashed = await Promise.all(chosen.map(async (file) => ({ file, name: file.name, sha256: await sha256Hex(file) })));
    if (token !== selection.current) return; // A newer selection replaced this one.
    setFiles(hashed);
    setIdempotencyKey(crypto.randomUUID());
    setHashing(false);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    if (blocked || !manifest) {
      blockedRef.current?.focus();
      return;
    }
    setPending(true);
    setError(null);
    setStage(`Uploading ${files.length} originals (${formatBytes(totalBytes)})…`);
    try {
      const result = await submitImport(
        {
          manifest,
          files: files.map((item) => item.file),
          idempotencyKey,
          createdCaseId,
          existing: props.mode === "replace" ? { id: props.claim.id, revision: props.claim.revision } : undefined,
        },
        request,
      );
      announce("Originals saved. Local checks are queued.");
      if (props.mode === "new") {
        router.push(`/claims/${result.caseId}/import`);
        return;
      }
      form.current?.reset();
      setManifestState(null);
      setFiles([]);
      setIdempotencyKey(crypto.randomUUID());
      setStage(null);
      setPending(false);
      router.refresh();
    } catch (failure) {
      if (failure instanceof ImportFailure) setCreatedCaseId(failure.caseId);
      const cause = failure instanceof ImportFailure ? failure.reason : failure;
      const text =
        cause instanceof SessionExpiredError
          ? "Your session ended. Sign in again, then select Import and check."
          : `${errorText(cause)} Your files are still selected. Select Import and check to try again.`;
      setError((previous) => ({ text, attempt: (previous?.attempt ?? 0) + 1 }));
      setStage(null);
      setPending(false);
    }
  }

  return (
    <form ref={form} onSubmit={submit} className="grid max-w-3xl gap-8" noValidate>
      <section aria-labelledby="step-manifest" className="grid gap-4">
        <StepHeading id="step-manifest" step="01" nested={nested}>
          Manifest
        </StepHeading>
        <p className="text-ink-muted">
          The manifest names the claim and each original by type, filename and SHA-256. It follows the internal sample
          profile, not an official eClaims schema.
        </p>
        <Field id="manifest-file" label="Manifest (JSON)" error={manifestState && "error" in manifestState ? manifestState.error : null}>
          <input
            id="manifest-file"
            type="file"
            accept=".json,application/json"
            className="file-input"
            onChange={(event) => void chooseManifest(event.currentTarget)}
            aria-describedby={describedBy("manifest-file", { error: manifestState && "error" in manifestState ? "y" : null })}
          />
        </Field>
        {manifest ? (
          <dl className="grid grid-cols-[max-content_1fr] gap-x-6 gap-y-1 text-sm">
            {IDENTITY_FIELDS.map(([key, label]) => (
              <div key={key} className="contents">
                <dt className="text-ink-muted">{label}</dt>
                <dd className="doc-ref">{manifest[key]}</dd>
              </div>
            ))}
          </dl>
        ) : null}
      </section>

      <section aria-labelledby="step-originals" className="grid gap-4">
        <StepHeading id="step-originals" step="02" nested={nested}>
          Originals
        </StepHeading>
        <Field id="original-files" label="Original documents" help="Limits: 25 MB per file, 100 MB per version, 150 pages, 30 files.">
          <input
            id="original-files"
            type="file"
            multiple
            className="file-input"
            onChange={(event) => void chooseOriginals(event.currentTarget)}
            aria-describedby={describedBy("original-files", { help: "y" })}
          />
        </Field>
      </section>

      {manifest && match ? (
        <section aria-labelledby="step-check" className="grid gap-3">
          <StepHeading id="step-check" step="03" nested={nested}>
            Check the selection
          </StepHeading>
          <ul aria-label="Documents named in the manifest" className="divide-y divide-rule-faint border-y border-rule bg-surface">
            {match.rows.map((row) => (
              <li key={`${row.type}-${row.filename}`} className="grid gap-1 px-4 py-3 sm:grid-cols-[1fr_auto] sm:items-center sm:gap-6">
                <div>
                  <p className="font-semibold">{documentLabel(row.type, row.filename)}</p>
                  <p className="doc-ref text-ink-muted">{row.filename}</p>
                </div>
                <StatusText tone={ROW_STATUS[row.status].tone}>{ROW_STATUS[row.status].text}</StatusText>
              </li>
            ))}
            {match.extras.map((name) => (
              <li key={`extra-${name}`} className="grid gap-1 px-4 py-3 sm:grid-cols-[1fr_auto] sm:items-center sm:gap-6">
                <p className="doc-ref">{name}</p>
                <StatusText tone="blocking">Not named in the manifest</StatusText>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <div className="grid gap-3 border-t border-ink pt-4">
        {error ? (
          <p ref={errorRef} role="alert" tabIndex={-1} className="border-l-4 border-blocking bg-blocking-tint px-4 py-3 font-semibold text-blocking">
            {error.text}
          </p>
        ) : null}
        <div className="flex flex-wrap items-center gap-4">
          <button
            type="submit"
            className={`btn ${nested ? "btn-secondary" : "btn-primary"}`}
            aria-disabled={blocked || pending ? "true" : undefined}
            aria-describedby={blocked ? "import-blocked" : undefined}
          >
            {pending ? "Importing…" : "Import and check"}
          </button>
          {blocked && !pending ? (
            <p id="import-blocked" ref={blockedRef} tabIndex={-1} className="text-sm font-semibold text-ink-muted">
              {blocked}
            </p>
          ) : null}
          {stage ? <p className="text-sm text-ink-muted">{stage}</p> : null}
        </div>
      </div>
    </form>
  );
}
