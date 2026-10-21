# Design System Document (DSD)

**System Name:** Sentinel Claims
**Date:** 2026-10-21
**Version:** 0.1
**Owner:** Yushin
**Status:** Draft
**Last reconciled:** 2026-10-21
**PRD:** [Product requirements](prd-sentinel-node.md)

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

No approved concept images exist. The earlier walkthrough is explanatory material. Screen composition below is a design specification; screenshots and interactive audit remain pending.

## 1. Design Philosophy & Vision

Keep evidence near the question it answers. Use a light paper background, dark forest navigation and restrained teal actions. Amber indicates attention and red a blocking issue, always with text and icons. White space separates the source from the reviewer decision.

Voice: ?Discharge dates differ. Compare these two records.? Error: ?This file could not be read. Replace it or review a legible original.? Completion: ?Ready for final submission review.? Never imply payment approval or that absent bundle evidence proves absent care.

Identify the environment once as ?Evaluation workspace: sample patient records?; include provenance on downloads. Ordinary review screens keep infrastructure details in diagnostics.

## 2. Brand Primitives

### 2.0 Token Architecture

Use primitive values, semantic meanings and component aliases. For example primitive forest `#174A3B` ? `--color-primary` ? `--button-bg`. Tokens are specified here; no implemented stylesheet is claimed.

### 2.1 Colors

| Token | Value |
|---|---|
| `--color-bg` | `#F7F6F2` |
| `--color-surface` | `#FFFFFF` |
| `--color-border` | `#8A9790` |
| `--color-primary` | `#174A3B` |
| `--color-primary-hover` | `#10382C` |
| `--color-accent` | `#176B68` |
| `--color-text` | `#172B24` |
| `--color-text-muted` | `#52635A` |
| `--color-success` | `#245B3D` |
| `--color-warning` | `#825000` |
| `--color-error` | `#A32D2D` |

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

Use Segoe UI where installed, then system-ui/sans-serif; monospace uses ui-monospace/Consolas/monospace. No downloaded fonts or font redistribution. Use tabular numerals for counts, dates and amounts.

### 2.4 Imagery & Illustration

Evidence documents and source crops do the visual work. No stock clinicians, generated patient portraits or invented signature imagery. Synthetic forms use clearly fictional acknowledgement marks. No new illustration asset is needed.

### 2.5 Elevation & Depth

Inline panels use borders without shadows. Floating menus: `0 4px 16px #172B2414`; modal: `0 12px 40px #172B2426`. No decorative glass or oversized gradients.

## 3. Layout & Spatial System

Base unit 4px; scale 4, 8, 12, 16, 24, 32, 48px. Desktop target 1366?768. Sidebar 224px; page padding 24px. Workbench uses findings/decisions at roughly 40% and source at 60%, with independent scroll and visible current-version labels.

Below 1024px collapse the sidebar; below 768px stack source below the selected finding and offer a focusable ?View source? jump. At 375px no horizontal page overflow; large document pages may pan within a labelled viewer. Use 16px narrow-screen padding.

## 4. Core Component Specs

Buttons: 6px radius, 10px 16px padding, 600 weight, minimum 44px target. Primary uses forest, hover darker forest; secondary uses forest outline/text; destructive uses red. All use a visible 2px teal focus ring with 2px offset. Disabled uses explicit explanation and prevents activation, not just opacity.

Inputs: visible label, format help, border token, 6px radius, 12px padding. Errors sit next to the field and in a focusable summary. Do not erase typed values on validation errors. Required fields have text indicators.

Panels: white, 1px border, 8px radius. Dialogs require named title, constrained focus, Escape/cancel and return focus; destructive confirmations identify the affected case/version. Never put the only evidence inside a modal.

### 4.1 Composition Patterns

- Queue: compact rows with reference, assignee, discharge date, age, coverage and state; filtering retains the current selection.
- Workbench: selected finding and reasoned disposition beside its highlighted source; original/extraction toggle; explicit uncertain OCR confirmation.
- Correction form: responsible department/person, reason and evidence; separate Record handoff/Record acknowledgement actions.
- Empty state: explain the next action, such as ?Import a sample claim to start a review.?
- Loading: real stages and queue wait, no fabricated percentage. Error preserves last saved state and exposes retry or required source replacement.
- Navigation: Claims, supervisor Overview and Administration; case Review/Corrections/History tabs. Each destination rechecks permissions.
- Completion: checklist with exact blockers. Do not replace unresolved coverage with a green aggregate score.

## 5. Motion & Micro-interactions

Use 120ms color/focus transitions. Dialog appearance at most 150ms; no animated page transitions. Progress indicators reflect actual work. Respect reduced-motion preference and never flash a source highlight.

## 6. Accessibility

Aim for WCAG AA: text contrast at least 4.5:1, UI indicators at least 3:1. Keyboard operation and visible focus throughout; semantic headings, table headers, field labels and status announcements. Targets at least 44?44px. Provide document text where extraction exists and a labelled original viewer. Do not announce the entire queue on polling.

Screen-reader, 200% zoom, keyboard-only and narrow-screen audits remain pending against implemented screens.

## 7. Visual Settings

Design variance 3/10; motion intensity 1/10; density 6/10. A restrained task-focused system supports long review sessions. Settings describe intended composition, not a tool installation or measured score.

## 8. Quality Gate

No implemented-screen audit has been completed. Accessibility, performance, theming, responsiveness and implementation integrity are each unscored. Before release, each must score at least 3/4 with no unresolved critical or major issue.

| Surface | Do | Avoid |
|---|---|---|
| Finding | Show exact differing passages and source versions | Unexplained confidence or approval score |
| Revision | Reopen affected decisions and show previous history | Silently carrying prior completion forward |
| Metrics | Counts and elapsed time derived from events | Recovered-revenue claims |
| Sample workspace | One environment notice and export provenance | Pretending fictional records are hospital records |

Design rationale satisfies the records-desk reference. Human detail comes from reasoned reviewer notes and correction ownership. Whether these choices work for reviewers must be established in the actual UI.

## 9. Materialization

Root brand and design guides are derived from this source. Asset version 0.1.0; future approved assets belong in `docs/assets/brand/`, with descriptive names and source/license records. Yushin approves changes; retire older versions through repository history. No new asset files exist.

## Self-Check

- [x] Audience, voice, exact tokens, spacing, component states and constraints specified.
- [ ] Implemented tokens, UI audit, concept review and release quality demonstrated.
