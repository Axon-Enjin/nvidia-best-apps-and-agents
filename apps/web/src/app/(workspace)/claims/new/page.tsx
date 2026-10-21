import type { Metadata } from "next";

import { ArrowLeft } from "@/components/ui/icons";
import { IntakeForm } from "@/features/intake/intake-form";
import { QueueLink } from "@/features/session/queue-memory";

export const metadata: Metadata = { title: "Import a claim" };

export default function NewClaimPage() {
  return (
    <>
      <QueueLink className="inline-flex min-h-11 items-center gap-1.5 font-semibold no-underline">
        <ArrowLeft aria-hidden="true" className="size-4" />
        Claims
      </QueueLink>
      <div className="mb-8 mt-2 border-b border-ink pb-4">
        <p className="eyebrow">New claim</p>
        <h1 className="text-[1.75rem]">Import a claim</h1>
        <p className="mt-2 max-w-3xl text-ink-muted">
          Choose the manifest, then the originals it names. Each file is checked against the manifest before anything is
          uploaded; local checks run after import.
        </p>
      </div>
      <IntakeForm mode="new" />
    </>
  );
}
