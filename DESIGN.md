<!-- MATERIALIZED from docs/dsd-sentinel-node.md by scripts/materialize.py on 2026-10-23. Do not hand-edit; edit the canonical doc and re-run. -->

# Design:

> Visual language, materialized from DSD §2-§8.

## 2. Brand Primitives

### 2.0 Token Architecture

Use primitive values, semantic meanings and component aliases, for example primitive forest `#174A3B` to `--color-forest` to `.btn-primary`. The implemented tokens live in the `@theme` block of `apps/web/src/app/globals.css`; `apps/web/src/app/tokens.test.ts` measures every text and indicator pairing from that file.

### 2.1 Colors

| Token | Value |
|---|---|
| `--color-bg` | `#F7F6F2` |
| `--color-surface` | `#FFFFFF` |
| `--color-border` (`--color-rule`) | `#7A8780` (was `#8A9790`, which measured 2.81:1 on paper; boundaries need 3:1) |
| `--color-primary` | `#174A3B` |
| `--color-primary-hover` | `#10382C` |
| `--color-accent` | `#176B68` |
| `--color-text` | `#172B24` |
| `--color-text-muted` | `#52635A` |
| `--color-success` | `#245B3D` |
| `--color-warning` | `#825000` |
| `--color-error` | `#A32D2D` |
| Tints (passed, attention, blocking, teal) | `#E7EEE8`, `#FBF1DC`, `#FBE9E7`, `#E3EFEC` |
| Evidence highlight | `#FFE3A0` with an amber underline |
| Faint divider (decorative only) | `#DCDFD8` |

White action text on primary/accent; text and muted text on paper/white. Verify actual combinations and states before release. Borders convey boundaries; avoid relying on pale fills for actionable states.

### 2.2 Logo System

Text wordmark ?Sentinel Claims? for the initial release; no approved pictorial logo exists. Keep one cap-height clear space, minimum 16px wordmark, forest on paper or white on forest. No hospital/PhilHealth seals or invented endorsement marks.

### 2.3 Typography

| Role | Font | Weight / size / line height |
|---|---|---|
| H1 / H2 / H3 | System UI | 650 / 28, 22, 18px / 1.25 |
| Body | System UI | 400 / 16px / 1.5 |
| Caption and dense rows | System UI | 400 / 14px / 1.4 |
| Document references | System monospace | 400 / 13px / 1.5 |
| Archive labels (eyebrows) | System UI | 600 / 12px, uppercase, 0.08em tracking |
| Claim reference (page title) | System monospace | 600 / 24px |

Use Segoe UI where installed, then system-ui/sans-serif; monospace uses ui-monospace/Consolas/monospace. No downloaded fonts or font redistribution. Use tabular numerals for counts, dates and amounts.

### 2.4 Imagery & Illustration

Evidence documents and source crops do the visual work. No stock clinicians, generated patient portraits or invented signature imagery. Synthetic forms use clearly fictional acknowledgement marks. No new illustration asset is needed.

### 2.5 Elevation & Depth

Inline panels use borders without shadows. Floating menus: `0 4px 16px #172B2414`; modal: `0 12px 40px #172B2426`. No decorative glass or oversized gradients.
## 3. Layout & Spatial System

Base unit 4px; scale 4, 8, 12, 16, 24, 32, 48px. Desktop target 1366x768; page padding 24px (16px below 768px). No sidebar: the case header is two compact lines and the phases (Import, Review, Complete) are one line of tabs, so task content starts about 250px from the top. Review is an asymmetric three-column composition at 1280px and wider: a compact issue list (about 18rem, sticky with its own scroll), the selected issue with its next action (about 27rem) and a generous source-reading column (the rest, sticky with its own scroll). From 1024px the source column moves under the selected issue.

Below 1024px everything stacks in one column with a focusable "View source" jump. At 375px no horizontal page overflow; large document pages may pan within a labelled viewer. Use 16px narrow-screen padding.
## 4. Core Component Specs

Buttons: 6px radius, 10px 16px padding, 600 weight, minimum 44px target. Primary uses forest, hover darker forest; secondary uses forest outline/text; destructive uses red. All use a visible 2px teal focus ring with 2px offset. Disabled uses explicit explanation and prevents activation, not just opacity.

Inputs: visible label, format help, border token, 6px radius, 12px padding. Errors sit next to the field and in a focusable summary. Do not erase typed values on validation errors. Required fields have text indicators.

Panels: white, 1px border, 8px radius. Dialogs require named title, constrained focus, Escape/cancel and return focus; destructive confirmations identify the affected case/version. Never put the only evidence inside a modal.

### 4.1 Composition Patterns

- Queue: compact rows with the claim reference in monospace, patient, status as icon and text, stage and import date; view, search and page live in the URL; the claim a reviewer last opened keeps a teal rule when they return.
- Intake: numbered steps (manifest, originals, check the selection); every document the manifest names is a row with Selected, Missing, SHA-256 mismatch, duplicate or not-in-manifest status; import stays unavailable with the reason beside the button.
- Phases: a claim opens where action is needed. Import shows real processing states, scan confirmation (form, then the original, then remaining values), the documents with distinct states, the corrected-version intake and earlier versions.
- Review signature: lettered evidence marks. Each distinct differing value gets a letter shown in the "What differs" table, on the document tab and on the highlighted value in the source text. Only connections the review service established get a letter; checks that cite whole documents list their pages without highlights; scans awaiting confirmation are cited without highlights.
- Next action: one primary action per selected issue, with only that action's fields revealed; correction progress shows Requested, Handed off, Acknowledged, Corrected version imported and Resolved, with the next valid step.
- Secondary: passed checks, extra attachment requirements, re-runs, history and earlier versions sit behind labelled disclosures.
- Empty state: explain the next action, such as "No claims match. Import a claim to start a review."
- Loading: real stages, no fabricated percentage. Errors keep entered values; a stale revision keeps the draft and offers "Load latest"; an expired session signs in again over the page.
- Completion: remaining blockers first when blocked, then the summary with named responsibility, current version, coverage and checks. Do not replace unresolved coverage with a green aggregate score.
## 5. Motion & Micro-interactions

Use 120ms color/focus transitions and 150ms for issue selection. No animated page transitions or spinners; progress text reflects actual work. Under reduced motion every transition is 0s (tested). Never flash a source highlight.
## 6. Accessibility

Aim for WCAG AA: text contrast at least 4.5:1, UI indicators at least 3:1. Keyboard operation and visible focus throughout; semantic headings, table headers, field labels and status announcements. Targets at least 44?44px. Provide document text where extraction exists and a labelled original viewer. Do not announce the entire queue on polling.

Implemented screens are checked by `tests/e2e/test_web_accessibility.py`: a keyboard-only path through every phase action, focus visible (2px) and not covered, no horizontal overflow at 375px, 1366px and 200% zoom, reduced motion, status text beside color, measured contrast of rendered text, and one polite live region per page. A session with a real screen reader has not been run.
## 7. Visual Settings

Design variance 6/10; motion intensity 1/10; density 6/10. An editorial records-archive composition (Minimalism and Swiss style with an asymmetric editorial grid) gives the review a recognizable identity without decoration. Settings describe intended composition, not a measured score.
## 8. Quality Gate

One batched visual review and a confirmation pass were completed on 2026-10-22 (see the frontend redesign verification record). Scores for the local prototype: accessibility 3/4 (automated checks pass; no screen-reader session yet), performance 3/4 (server-rendered pages, no remote assets; not load-tested), theming 3/4 (light theme only by design; tokens measured), responsiveness 3/4 (375px to 1366px and 200% zoom tested), implementation integrity 3/4 (typed against captured API responses; container image unbuilt). Before release, each must hold at least 3/4 with no unresolved critical or major issue.

| Surface | Do | Avoid |
|---|---|---|
| Finding | Show exact differing passages and source versions | Unexplained confidence or approval score |
| Revision | Reopen affected decisions and show previous history | Silently carrying prior completion forward |
| Metrics | Counts and elapsed time derived from events | Recovered-revenue claims |
| Sample workspace | One environment notice and export provenance | Pretending fictional records are hospital records |

Design rationale satisfies the records-desk reference. Human detail comes from reasoned reviewer notes and correction ownership. Whether these choices work for reviewers must be established in the actual UI.
