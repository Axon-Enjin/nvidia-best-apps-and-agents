import { ArrowLeft } from "@/components/ui/icons";
import { StatusText } from "@/components/ui/status-text";
import { QueueLink } from "@/features/session/queue-memory";
import { READY_STATE, type AppConfig, type ClaimDetail, type ReviewState } from "@/lib/api-types";

function Meta({ label, children, mono = false }: { label: string; children: React.ReactNode; mono?: boolean }) {
  return (
    <div className="grid gap-0.5">
      <dt className="eyebrow">{label}</dt>
      <dd className={mono ? "doc-ref" : ""}>{children}</dd>
    </div>
  );
}

/** The claim's identity and current version, shown above every phase. */
export function CaseHeader({
  claim,
  version,
  review,
  config,
}: {
  claim: ClaimDetail;
  version: number | null;
  review: ReviewState | null;
  config: AppConfig;
}) {
  const ready = claim.state === READY_STATE;
  const offline = (review?.model_status ?? "not_run_offline") === "not_run_offline" || config.network_mode === "offline";
  return (
    <section aria-label="Claim summary" className="border-b border-ink pb-5">
      <QueueLink className="inline-flex min-h-11 items-center gap-1.5 font-semibold no-underline">
        <ArrowLeft aria-hidden="true" className="size-4" />
        Claims
      </QueueLink>
      <div className="mt-1 flex flex-wrap items-end justify-between gap-x-6 gap-y-2">
        <div>
          <p className="eyebrow">Claim</p>
          <h1 className="doc-ref text-[1.75rem] font-semibold tracking-tight">{claim.reference}</h1>
        </div>
        <StatusText tone={ready ? "passed" : "neutral"} className="text-base">
          {claim.state}
        </StatusText>
      </div>
      <dl className="mt-4 flex flex-wrap gap-x-10 gap-y-3 text-sm">
        <Meta label="Patient" mono>
          {claim.patient_id}
        </Meta>
        <Meta label="Encounter" mono>
          {claim.encounter_ref}
        </Meta>
        <Meta label="Facility" mono>
          {claim.facility_id}
        </Meta>
        <Meta label="Source">
          <span aria-label="Source version" className="doc-ref font-semibold">
            {version ? `Version ${version}` : "No version yet"}
          </span>
        </Meta>
        <Meta label="Rules" mono>
          {review?.rule_version ?? config.rule_version}
        </Meta>
      </dl>
      {offline ? (
        <p className="mt-3 text-sm text-ink-muted">
          AI comparison: not run (offline). Narrative agreement uses a named manual comparison.
        </p>
      ) : null}
    </section>
  );
}
