// Wire types for the FastAPI review service. Field names and nullability follow
// the Python response builders (api.py, bundles.py, service.py, review.py,
// confirmations.py, reports.py, profile.py) and are checked against captured
// real responses in contract-check.ts. Server enums stay `string` so an
// unknown value renders generically instead of breaking the page.

export const CHECK_STATUSES = ["passed", "incomplete", "flagged", "unsupported"] as const;
export const DOCUMENT_STATUSES = ["readable", "needs_confirmation", "unreadable", "unsupported", "unmatched", "ambiguous", "quarantined"] as const;
export const TASK_STATUSES = ["open", "handed_off", "acknowledged", "resolved", "cancelled"] as const;
export const JOB_STATUSES = ["queued", "running", "succeeded", "failed"] as const;
export const READY_STATE = "Ready for final submission review";

export type Actor = {
  id: string | null;
  username: string;
  roles: string[];
};

export type SessionState = {
  authenticated: boolean;
  protected: boolean;
  auth_mode: string;
  actor: Actor | null;
  csrf_token: string | null;
};

export type AppConfig = {
  model_configured: boolean;
  network_mode: string;
  model: string;
  protected: boolean;
  auth_mode: string;
  format: string;
  rule_version: string;
};

export type QueueItem = {
  id: string;
  reference: string;
  patient_id: string;
  sample: boolean;
  created_at: number;
  assignee_id: string | null;
  revision: number;
  current_bundle_id: string | null;
  state: string;
  job_id: string | null;
  status: string | null;
  outcome: string;
  finding_count: number;
  pending_count: number;
  model_status: string | null;
  use_model: boolean | null;
};

export type QueuePage = { items: QueueItem[]; total: number; limit: number; offset: number };

export type QueueStats = { all: number; needs_review: number; incomplete: number; no_findings: number; processing: number };

export type CaseRecord = {
  id: string;
  facility_id: string;
  encounter_ref: string;
  claim_ref: string;
  patient_id: string;
  revision: number;
  current_bundle_id: string | null;
  assignee_id: string | null;
  state: string;
};

export type CoverageEntry = { document_id: string; type: string; status: string; problems?: string[] };

export type BundleReceipt = {
  case_id: string;
  bundle_id: string;
  version: number;
  revision: number;
  import_job_id: string;
  coverage: CoverageEntry[];
};

export type JobSummary = {
  id: string;
  claim_id: string;
  status: string;
  created_at: number;
  finished_at: number | null;
  attempts: number;
  use_model: boolean;
  xml_name: string;
  chart_name: string | null;
  result: unknown;
  error: string | null;
};

export type ClaimDetail = CaseRecord & {
  reference: string;
  sample: boolean;
  bundles: BundleReceipt[];
  latest: JobSummary | null;
  history: JobSummary[];
};

export type Anchor = {
  field: string;
  value: string;
  page: number;
  line?: number;
  path?: string;
  confirmation_id?: string;
};

export type Extraction = {
  /** Keyed by field name; a field may be absent. */
  fields: Partial<Record<string, string>>;
  anchors: Anchor[];
  pages: string[];
  extractor: string;
  requires_confirmation?: boolean;
};

export type SourceDocument = {
  id: string;
  type: string;
  filename: string;
  sha256: string;
  byte_count: number;
  content_type: string;
  page_count: number;
  status: string;
  problems: string[];
  extraction: Extraction;
};

export type ManifestMember = { type: string; filename: string; sha256: string };

export type BundleDetail = BundleReceipt & {
  manifest: { facility_id: string; encounter_ref: string; claim_ref: string; patient_id: string; documents: ManifestMember[] };
  manifest_hash: string;
  status: string;
  profile_version: string;
  documents: SourceDocument[];
};

export type CheckAnchor = Anchor & { bundle_id: string; document_id: string; sha256?: string };

export type DifferenceSource = { document_id: string; type: string; bundle_id: string; value: string; page: number | null };

export type Difference = { field: string; expected: string | null; sources: DifferenceSource[] };

export type Check = {
  id: string;
  label: string;
  status: string;
  blocking_reasons: string[];
  anchors: CheckAnchor[];
  differences: Difference[];
};

export type Finding = {
  id: string;
  code: string;
  title: string;
  severity: string;
  explanation: string;
  anchors: CheckAnchor[];
  rule: string;
  resolution_status: string;
};

export type EvidenceRef = { document_id: string; page: number };

export type CorrectionTask = {
  id: string;
  check_id: string;
  department: string;
  person: string;
  reason: string;
  anchors: EvidenceRef[];
  status: string;
  bundle_id: string;
  created_at: number;
  updated_at?: number;
};

export type Expectation = {
  id: string;
  type: string;
  reason: string;
  reviewed: boolean;
  withdrawn?: boolean;
  role?: string;
};

export type ReviewEventPayload = {
  reason?: string;
  anchors?: EvidenceRef[];
  check_id?: string;
  department?: string;
  person?: string;
  task_id?: string;
  expectation_id?: string;
  confirmation_id?: string;
  document_id?: string;
  anchor?: { page: number; field: string };
  value?: string;
};

export type ReviewEvent = {
  id: string;
  bundle_id: string;
  rule_version: string;
  revision: number;
  actor_id: string;
  actor: string;
  action: string;
  payload: ReviewEventPayload;
  created_at: number;
};

export type ConfirmedValue = { value: string; confirmation_id: string; actor_id: string; page: number };

export type ConfirmationRequirement = {
  document_id: string;
  type: string;
  status: string;
  pending: string[];
  confirmed: Partial<Record<string, ConfirmedValue>>;
  fields: string[];
};

export type Blocker = { id: string; reasons: string[] };

export type ReviewState = {
  rule_version: string;
  bundle_id: string;
  profile_status: string;
  model_status: string;
  outcome: string;
  checks: Check[];
  findings: Finding[];
  fields: Record<string, string | null>;
  coverage: CoverageEntry[];
  revision: number;
  bundle_version: number | null;
  tasks: CorrectionTask[];
  expectations: Expectation[];
  events: ReviewEvent[];
  blockers: Blocker[];
  can_finalize: boolean;
  confirmations: ConfirmationRequirement[];
};

export type ConfirmResult = { confirmation_id: string; review_state: ReviewState };

export type ReportSnapshot = {
  case_id: string;
  claim_ref: string;
  patient_id: string;
  bundle_id: string;
  bundle_version: number;
  rule_version: string;
  revision: number;
  actor_id: string;
  actor: string;
  completed_at: number;
  provenance: string;
  outcome: string;
  checks: Check[];
  coverage: CoverageEntry[];
  model_status: string;
  findings: Finding[];
  events: ReviewEvent[];
  tasks: CorrectionTask[];
  documents: { id: string; type: string; sha256: string }[];
};

export type ReportRecord = {
  id: string;
  case_id: string;
  bundle_id: string;
  revision: number;
  created_at: number;
  snapshot: ReportSnapshot;
  stale: boolean;
};

export type ReportList = { items: ReportRecord[] };

/** Body of POST /api/claims/{id}/review-events. */
export type ReviewActionBody = {
  expected_revision: number;
  bundle_id: string;
  rule_version: string;
  action: string;
  reason: string;
  anchors?: EvidenceRef[];
  check_id?: string;
  department?: string;
  person?: string;
  task_id?: string;
  expectation_id?: string;
};
