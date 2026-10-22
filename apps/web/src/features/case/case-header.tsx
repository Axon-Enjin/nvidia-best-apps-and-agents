import { ArrowLeft } from "@/components/ui/icons";
import { StatusText } from "@/components/ui/status-text";
import { QueueLink } from "@/features/session/queue-memory";
import { READY_STATE, type AppConfig, type ClaimDetail, type ReviewState } from "@/lib/api-types";

function Meta({ label, children, mono = false }: { label: string; children: React.ReactNode; mono?: boolean }) {
  return (
    <div className="flex items-baseline gap-1.5">
      <dt className="text-ink-muted">{label}</dt>
      <dd className={mono ? "doc-ref" : ""}>{children}</dd>
    </div>
  );
}

/** The claim's identity and current version in two compact lines above every phase. */
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
    <section aria-label="Claim summary" className="border-b border-ink pb-3">
      <div className="flex flex-wrap items-center justify-between gap-x-6">
        <QueueLink className="inline-flex min-h-11 items-center gap-1.5 text-sm font-semibold no-underline">
          <ArrowLeft aria-hidden="true" className="size-4" />
          Claims
        </QueueLink>
        <StatusText tone={ready ? "passed" : "neutral"}>{claim.state}</StatusText>
      </div>
      <div className="flex flex-wrap items-baseline gap-x-8 gap-y-2">
        <h1 className="doc-ref text-[1.5rem] font-semibold tracking-tight">{claim.reference}</h1>
        <dl className="flex flex-wrap gap-x-5 gap-y-1 text-sm">
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
          {offline ? <Meta label="AI comparison">not run (offline)</Meta> : null}
        </dl>
      </div>
    </section>
  );
}
