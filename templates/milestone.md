# Milestone template

Per-slice rolling state file. Lives at `architecture/slices/slice-NNN-<name>/milestone.md`.

> **Note**: This template is the canonical shape. Each skill (`/slice`, `/design-slice`, `/critique`, `/build-slice`, `/validate-slice`, `/reflect`) updates this file at the end of its work. `/status` reads it as the primary source for active-slice state (faster + more robust than deriving stage from file existence).

Purpose: survive session death, context clear, model confusion. Any session resume = read `milestone.md` + continue.

---

## Template

```markdown
---
slice: slice-NNN-<name>
stage: slice | design | critique | build | validate | reflect | complete
updated: <YYYY-MM-DD>
next-action: <specific command or "none (slice complete)">
risk-tier: low | medium | high
critic-required: true | false (derived from risk-tier + mission-brief scan)
# OPTIONAL — omit entirely unless deliberately skipping a mandatory /critique-review:
# critique-review-skip: "skip — rationale: <text>"
---

# Milestone: slice-NNN <name>

**Stage**: <current stage>
**Next action**: <specific next step — e.g., "run /critique" or "address B1 blocker in design.md, then run /build-slice">
**Updated**: <YYYY-MM-DD>
**Risk tier**: <low | medium | high>

## Progress

- [x] /slice — <date>
- [x] /design-slice — <date>
- [ ] /critique — <date or "skipped: risk-tier=low + no mandatory triggers">
- [ ] /build-slice — <date or "in progress: N/M tasks">
- [ ] /validate-slice
- [ ] /reflect

## Current focus

<2-4 lines summarizing what's being worked on now and what would unblock or advance the slice>

## On resume

If session resumes mid-slice, this section tells Claude where to pick up:

- **Last completed action**: <what the last skill finished>
- **Current work**: <what's in progress, if anything>
- **Files being edited** (if mid-build): <list>
- **Next immediate step**: <specific, actionable>

## Phase artifacts (sources of truth)

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — <optional brief status>
- [critique.md](critique.md) — <CLEAN | NEEDS-FIXES | BLOCKED | skipped>
- [build-log.md](build-log.md) — <N/M tasks done, or "complete">
- [validation.md](validation.md) — <PASS | PARTIAL | FAIL | pending>
- [reflection.md](reflection.md) — <pending | complete>
```

---

## CRP-1 escape-hatch key (optional)

`critique-review-skip:` is an **optional** frontmatter key (absent by default). It is the CRP-1 (`methodology-changelog.md` v0.40.0) documented-skip escape-hatch: when a slice deliberately skips a mandatory `/critique-review`, set the value to `skip — rationale: <text>` and `tools/critique_review_prerequisite_audit.py` accepts the build. A present-but-off-canonical value is a hard violation. Per ADR-024 the key lives here (not `build-log.md`) so the CRP-1 prerequisite gate can read it before `build-log.md` exists; `/build-slice` Step 7b MUST preserve this key verbatim across its continuous milestone.md rewrites (treat it like `critic-required:` / `risk-tier:`, never a regenerated field).

## How each skill updates it

- **`/slice`**: creates the file; stage: `slice`, next: `/design-slice`, risk-tier from user input, checks "Progress" box for /slice
- **`/design-slice`**: stage → `design`, next → `/critique` (or `/build-slice` if critique-skip-eligible), checks /design-slice box
- **`/critique`**: stage → `critique`, writes result (CLEAN / NEEDS-FIXES / BLOCKED per TRI-1), next based on triage final verdict
- **`/build-slice`**: stage → `build`; updates "Current work" and "Files being edited" as tasks progress; N/M count updates continuously; at completion, next → `/validate-slice`
- **`/validate-slice`**: stage → `validate`, result recorded; next → `/reflect` (or "fix regression first" if shippability caught one)
- **`/reflect`**: stage → `complete`, next → `none (slice complete)`; immediately after, `/archive` moves folder (milestone.md goes with it)

## How /status uses it

`/status` reads `milestone.md` as the primary source for active-slice state:
- Stage: from frontmatter (explicit, not derived)
- Next action: from `next-action` field (explicit)
- Progress: from the checkbox list
- On-resume data: if session just resumed, this section tells Claude where to pick up

This replaces deriving stage from which files exist in the slice folder — faster, more robust, and carries mid-phase progress (like "3/5 tasks" in /build-slice).

## Worked example (mid-build)

```markdown
---
slice: slice-023-add-receipt-upload
stage: build
updated: 2026-04-22
next-action: complete remaining 2 build tasks, then run /validate-slice
risk-tier: medium
critic-required: true
---

# Milestone: slice-023 add-receipt-upload

**Stage**: build
**Next action**: Complete remaining 2 build tasks (task 4: thumbnail generation; task 5: auth check integration test), then `/validate-slice`
**Updated**: 2026-04-22
**Risk tier**: medium (touches API + data model + auth)

## Progress

- [x] /slice — 2026-04-21
- [x] /design-slice — 2026-04-21
- [x] /critique — 2026-04-22 — NEEDS-FIXES (B1, B2 ACCEPTED-PENDING per triage)
- [ ] /build-slice — in progress: 3/5 tasks complete
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Implementing the receipt upload endpoint. S3 upload + DB record done (tasks 1-3). Remaining: thumbnail generation via Pillow + integration test for auth enforcement.

## On resume

- **Last completed action**: Task 3 — DB record for uploaded receipt (src/api/receipts.py, src/db/migrations/003_receipts.sql)
- **Current work**: Task 4 — thumbnail generation (not started)
- **Files being edited**: none currently; next edit is src/services/thumbnail.py (new file)
- **Next immediate step**: create `src/services/thumbnail.py` with `generate_thumbnail(image_bytes) -> bytes` using Pillow + pyheif for HEIC

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — 5 ACs, 3 must-not-defer items
- [critique.md](critique.md) — NEEDS-FIXES; B1+B2 ACCEPTED-PENDING per triage; addressed in design v2
- [build-log.md](build-log.md) — 3/5 tasks done
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
```
