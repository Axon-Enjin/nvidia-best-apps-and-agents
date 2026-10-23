# Design: Hackathon hosted evaluation

**Date:** 2026-10-23
**Status:** Draft

## Hackathon requirements that shape the design

- The app must run on Nebius Token Factory or AI Cloud and use at least one NVIDIA open model. "Runs on" means a runtime call to the Token Factory inference API, or deployment on AI Cloud compute (Serverless Jobs, Serverless Endpoints, DevPods). A plain virtual machine is not named. Other model hosts do not count; the rest of the app can be hosted anywhere.
- Promo credits are for Token Factory only. There is no AI Cloud credit grant.
- Bonus Best Use of Tavily needs a functional runtime Tavily call.
- Submission: demo URL with logins in the testing instructions; public MIT repository with README; public YouTube video under 3 minutes with audio explaining Token Factory and Nemotron, no third-party trademarks; mandatory feedback. The site stays free and unrestricted until Dec 15. No changes after the deadline.

## Blocker

The Philippines is missing from Token Factory's billing country list. Staff said on Oct 9 that cards from some countries are not accepted and that an expansion request needs approvals with no timeline; on Oct 23 they said the card requirement stays and manual verification is not feasible. The Devpost $25 code and the Builders Program credit cannot be applied until an account passes onboarding.

Plan: (1) the owner replies in the existing Discord thread and messages staff; (2) a legitimate teammate abroad owns the Token Factory account with their own card and invites the owner (unconfirmed that invited members skip billing; the teammate must be on the Devpost submission); (3) build against a stand-in meanwhile; (4) backup: run Nemotron on an AI Cloud GPU serverless endpoint (unpriced, no credits, billing country unverified). The last safe day for a working key is about Oct 26.

Test doubles are test-only. With no real Token Factory account the live site shows "Not run" and the manual fallback, never invented Nemotron output.

## Technical approach

**One client for every Nemotron call** (`apps/api/src/sentinel`, replacing the old adapter in `inference.py`). It reads model IDs and the base URL from settings, uses structured output by the method the probe confirms, sets timeouts, finite retries and size caps, writes every call to a spend ledger (additive migration), and refuses when the ledger reaches $45 or when `NETWORK_MODE` is not `online`. AI-04, AI-05 and AI-07 are tested once at this client. Nemotron never receives secrets or another case's data.

**Models.** Super: `nvidia/nemotron-3-super-120b-a12b` (the current `NEBIUS_MODEL` default in `config.py`). Nano: `nvidia/nemotron-3-nano-30b-a3b`, with the `nvidia/` prefix assumed from Super's form and unconfirmed until the probe lists it. Nebius removed Nemotron 3 Nano Omni and Llama-3.1 Nemotron Ultra 253B on Aug 31, 2026, so IDs stay settings and the probe call confirms both. The API base URL is `https://api.tokenfactory.nebius.com/v1/`.

**Intake sorting.** Files dropped by the reviewer go to Nano, which proposes the document type of each file and the claim identifiers. Nothing is saved until the reviewer confirms. If the budget is gone or the call fails, the confirm screen appears with empty choices and the reviewer selects types by hand.

**P07.** Up to four Super calls per case version. Each question quotes both documents; the server checks each quote word for word against the cited page of the current version. Unverifiable output is discarded and counted as a coverage gap. A person decides every question; a new version reopens earlier decisions.

**Correction drafts.** Nano drafts the note to medical records, citing the PhilHealth reference when one is verified. The draft pre-fills the existing note field, so the reviewer edits it and records the handoff as today. Draft text renders as inert text; CSV export keeps its formula-injection guard (`reports.py:78`).

**PhilHealth references (Tavily).** One fixed query per check type, written by us, with no case data, restricted to philhealth.gov.ph. Applies to P02 to P09; a check with no verified passage shows nothing. Nano picks the exact passage from the search results, the server verifies it word for word, and a miss yields no reference. Web pages are untrusted: Nemotron gets no tools, and the display is plain text. The reference appears on the finding and in the correction draft, is labelled "Related PhilHealth rule" with "found by Tavily on philhealth.gov.ph, checked <time>", never changes a check result and never enters the export. A Check again button (any signed-in user, once per check type per 10 minutes) re-runs the search. Free plan, pay-as-you-go off, 7-day cache, cached copy shown at the limit, no in-app counter. Tavily passage picking counts toward the $45 stop.

**Hosting.** Plan A: Nebius AI Cloud `us-central1`, platform `cpu-d3`, preset `2vcpu-8gb`, Ubuntu 24.04 driverless image, a $100 ceiling through Dec 15 (about $90), used only if the account can be billed. Plan B: the Oracle free server in Singapore, chosen immediately if AI Cloud billing refuses the Philippines or at the end of Oct 24. One server runs everything, including PostgreSQL 17 from `compose.yaml`. Caddy serves HTTPS on a DuckDNS name, uvicorn runs with `--proxy-headers`, and one Caddy line sends no-index on every route except the landing page. The image is built on the server. Vercel is considered only after Oct 30.

**Database.** Migrations are tested on PostgreSQL 17 in CI; the worker keeps polling; the hosted database starts fresh.

**Backups.** A cron job runs a checkpoint, encrypts the archive and uploads it with rclone to a private bucket at the same provider each night. A restore drill restores into an empty PostgreSQL and the app reads the restored cases.

**Administration.** The admin API reuses the CLI account code. Every action re-checks MFA and writes an audit record. The MFA key is shown as text (no QR code). An admin cannot open cases. There are no rule-profile or health views.

**Judge access.** Six reviewer accounts with three cases each, and two supervisor accounts with MFA whose setup key is in the testing instructions. A seeding command makes them repeatably on a fresh database.

**Design.** Working Papers: ledger ruling, tick marks, Nemotron work in blue pencil, reviewer decisions in red, a pinned legend, index letters per document type, status by mark shape, one text size, line numbers, light theme. Always: evidence (document, page, version) on every finding; no AI confidence or approval scores; every Nemotron output labelled and human-confirmed; the sample-records notice; WCAG AA, keyboard use, 44 px targets, reduced motion. The public landing page at `/` has no invented statistics and is indexable; everything behind sign-in is no-index. Rework order: Review, Intake, Queue, Complete.

### Decisions

| Decision | Choice | Reason |
|---|---|---|
| Video and VL | Vision-language reading cut; Tavily takes the slot | Saves days; Tavily has a bonus award |
| Database host | PostgreSQL 17 on the one server | A managed external database was cut; one thing to back up |
| Models | Settings, confirmed by probe | Nebius removed Nemotron models on Aug 31 |
| Budget | App stops at $45 | $1 trial + $25 hackathon + $25 Builders credit |
| Hosting | Nebius AI Cloud if billable, else Oracle Singapore | Billing country is the unknown |
| Judge admin | No admin account for judges | An admin cannot review; keeps judge isolation |
| Never cut | $45 stop, quote verification, MFA re-check, judge isolation, accessibility, backups, redesign and landing page | Safety and the judged surface |

## Data / API impact

- Additive migration for the spend ledger and for stored Tavily references (query key, passage, source URL, retrieved time, cache expiry).
- New endpoints: intake proposal and confirm, P07 questions and decisions, correction draft, reference lookup and refresh, admin account actions, overview metrics.
- Settings: `NEBIUS_API_KEY`, `NEBIUS_MODEL`, a Nano model setting, `TAVILY_API_KEY`, spend limit, forwarded-header trust. Keys live in git-ignored `.env` and `data/deploy/production.env`.

## Risks

- Token Factory account blocked (above). Mitigation list in Blocker.
- Credits are small: Super calls and Tavily passage picking draw from $45; the spending stop is a never-cut item.
- Prompt injection from documents and web pages: no tools for Nemotron, word-for-word verification, plain-text display, AI safety tests AI-02 to AI-09.
- Host capacity or billing refusal: plan B switch point at the end of Oct 24.
- Schedule: the cuts save about three days; the redesign is the largest remaining cost.
- Unrun gates from the prototype (container build, PostgreSQL workflow, Linux OCR, CI) are exercised for the first time here.
