// Type-checked, never imported by the app: each captured real response must be
// assignable to its wire type. tests/e2e/test_web_contract.py keeps the samples
// in step with the live API.
import type {
  AppConfig,
  BundleDetail,
  BundleReceipt,
  CaseRecord,
  ClaimDetail,
  ConfirmResult,
  QueuePage,
  QueueStats,
  ReportList,
  ReportRecord,
  ReviewState,
  SessionState,
} from "./api-types";
import bundleSample from "./contract-samples/bundle.json";
import receiptSample from "./contract-samples/bundle-receipt.json";
import caseSample from "./contract-samples/case.json";
import claimSample from "./contract-samples/claim.json";
import configSample from "./contract-samples/config.json";
import confirmationSample from "./contract-samples/confirmation.json";
import queueSample from "./contract-samples/queue.json";
import reportSample from "./contract-samples/report.json";
import reportsSample from "./contract-samples/reports.json";
import reviewStateSample from "./contract-samples/review-state.json";
import sessionSample from "./contract-samples/session.json";
import statsSample from "./contract-samples/stats.json";

export const contractSamples: {
  bundle: BundleDetail;
  receipt: BundleReceipt;
  case: CaseRecord;
  claim: ClaimDetail;
  config: AppConfig;
  confirmation: ConfirmResult;
  queue: QueuePage;
  report: ReportRecord;
  reports: ReportList;
  reviewState: ReviewState;
  session: SessionState;
  stats: QueueStats;
} = {
  bundle: bundleSample,
  receipt: receiptSample,
  case: caseSample,
  claim: claimSample,
  config: configSample,
  confirmation: confirmationSample,
  queue: queueSample,
  report: reportSample,
  reports: reportsSample,
  reviewState: reviewStateSample,
  session: sessionSample,
  stats: statsSample,
};
