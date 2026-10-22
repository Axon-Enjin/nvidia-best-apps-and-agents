<!-- MATERIALIZED from docs/dsd-sentinel-node.md by scripts/materialize.py on 2026-10-22. Do not hand-edit; edit the canonical doc and re-run. -->

# Brand:

> Verbal identity, materialized from the DSD (sections 0, 0.5, 1, 2, 8, 9). Subsections 2.2-2.4 and 8.4 ride along when present in those sections.

## 0. Brand Stance

**Selected mode:** Product (task-first).

**Cultural or aesthetic reference:** A hospital records desk: paper forms, clear dividers, signed review notes and an orderly correction queue. The reference guides legibility; it does not imply hospital affiliation.

**Distinctive line:** Find discrepancies. Trace the evidence. Close the review.

**Archetypical user:** Mara, a fictional hospital claims reviewer reconciling a discharge date while the encoder prepares a replacement form.

**Category default to avoid:** A chatbot landing page with glowing gradients and financial-savings counters.

**How users appear:** Named reviewers, explicit responsibility and plain-language review notes. Show what the reviewer checked, who owes the correction and which version is current.

**Name:** Sentinel Claims. **Descriptor:** PhilHealth claim review workspace. The name has not received trademark clearance.

**Anti-references:** Consumer wellness dashboards obscure document work; trading terminals encourage alarm; insurer approval stamps imply authority the app does not have.
## 0.5 Concept Visuals

No approved concept images exist. The implemented screens are the reference: `tests/e2e/test_web_screens.py` captures sign-in, queue, intake, Import with scan confirmation, Review, correction progress and Complete at 1366x768 and 375x812 into `test-results/web/screens/`. `docs/changes/frontend-redesign/verify.md` records the visual review and its corrections.
## 1. Design Philosophy & Vision

Keep evidence near the question it answers. Use a light paper background, dark forest navigation and restrained teal actions. Amber indicates attention and red a blocking issue, always with text and icons. White space separates the source from the reviewer decision.

Voice: ?Discharge dates differ. Compare these two records.? Error: ?This file could not be read. Replace it or review a legible original.? Completion: ?Ready for final submission review.? Never imply payment approval or that absent bundle evidence proves absent care.

Identify the environment once as ?Evaluation workspace: sample patient records?; include provenance on downloads. Ordinary review screens keep infrastructure details in diagnostics.
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
## 8. Quality Gate

One batched visual review and a confirmation pass were completed on 2026-10-22 (see the frontend redesign verification record). Scores for the local prototype: accessibility 3/4 (automated checks pass; no screen-reader session yet), performance 3/4 (server-rendered pages, no remote assets; not load-tested), theming 3/4 (light theme only by design; tokens measured), responsiveness 3/4 (375px to 1366px and 200% zoom tested), implementation integrity 3/4 (typed against captured API responses; container image unbuilt). Before release, each must hold at least 3/4 with no unresolved critical or major issue.

| Surface | Do | Avoid |
|---|---|---|
| Finding | Show exact differing passages and source versions | Unexplained confidence or approval score |
| Revision | Reopen affected decisions and show previous history | Silently carrying prior completion forward |
| Metrics | Counts and elapsed time derived from events | Recovered-revenue claims |
| Sample workspace | One environment notice and export provenance | Pretending fictional records are hospital records |

Design rationale satisfies the records-desk reference. Human detail comes from reasoned reviewer notes and correction ownership. Whether these choices work for reviewers must be established in the actual UI.
## 9. Materialization

Root brand and design guides are derived from this source. Asset version 0.1.0; future approved assets belong in `docs/assets/brand/`, with descriptive names and source/license records. Yushin approves changes; retire older versions through repository history. The only implemented assets are the existing favicon and the lucide-react icon set (ISC licence), bundled into the web app.
