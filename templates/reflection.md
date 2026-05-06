# Reflection template

> **Note**: This template is also embedded inline in [`../skills/reflect/SKILL.md`](../skills/reflect/SKILL.md). The skill is the live source; this file is a standalone reference.

Per-slice reflection. Lives in `architecture/slices/slice-NNN-<name>/reflection.md`.

---

## Template

```markdown
# Reflection: Slice NNN <name>

**Date**: <date>
**Shipped**: [YES | YES-WITH-DEFERRALS | NO]

## Validated

Design claims that reality confirmed:

- <claim> — validated by <what (test, manual check, user observation)>
- <claim> — validated by <what>

## Corrected

Design claims that reality refuted (vault updated):

- <claim> → reality is <actual> — updated in [[file]]
- <claim> → reality is <actual> — superseded by [[ADR-NNN]]

## Discovered

Things we didn't know to spec:

- <discovery> — impact: <what changes for next slices>
- <discovery> — added to risk register as [[R-NN]]

## Deferred

Things not done this slice:

- <item> — reason: <why deferred> — lands in: <next slice name | backlog>
- <item> — reason: <user approved deferral, see build-log> — lands in: <next slice>

## Critic calibration

Critic findings from critique.md — which ones reality validated?

- B1 (<title>): VALIDATED — bug appeared exactly as flagged during build
- B2 (<title>): VALIDATED — caught during validation, fix worked
- M1 (<title>): FALSE ALARM — turned out to be a non-issue because <reason>
- m1 (<title>): NOT YET — deferred, will validate when relevant

**Missed by Critic**: <things that surfaced during build/validate that Critic didn't flag>

**Pattern**: <any observation about Critic accuracy to improve future prompts>

## Lessons for next slice

- <actionable insight>
- <actionable insight>

## Vault updates made

Files modified during reflection:

- [[risk-register.md]] — added R7 (HEIC encoding edge case)
- [[components/storage-service.md]] — corrected behavior (sync upload, not async)
- [[decisions/ADR-008.md]] — marked finalized with library choice
```

---

## How to use

- Populated by `/reflect` after `/validate-slice` completes
- Each slice's reflection feeds the next `/slice`:
  - Discovered risks influence next slice ordering
  - Deferred items become candidates for next slice
  - Lessons inform `/design-slice` choices
- Aggregated insights appended to `architecture/lessons-learned.md`
- Critic calibration accumulates over time; informs Critic prompt tuning across projects

## Honesty discipline

The reflection is not a victory lap. It explicitly records:

- Things that didn't work
- Assumptions that were wrong
- Where we got lucky (succeeded for reasons other than the design)
- Where we're still guessing

Glossing over failures defeats the purpose. The discoveries section in particular — if it's empty across multiple slices, either you're not learning or you're not capturing.

## Worked example

```markdown
# Reflection: Slice 003 add-receipt-upload

**Date**: 2026-04-20
**Shipped**: YES

## Validated

- POST /transactions/:id/receipt accepts JPEG/PNG/HEIC up to 10MB — validated by curl tests on sample files of each format
- Thumbnails generate at 200×200 WebP — validated by visual inspection in browser
- Authorization rejects non-owners — validated by manual check with second user account
- 413 returned for oversized files — validated by curl with 15MB file

## Corrected

- Design claimed thumbnails generate "asynchronously"; in implementation we did sync because the async queue setup was a separate slice — updated [[components/storage-service.md]] to "sync, async planned in slice-006"

## Discovered

- HEIC files from real iPhones often have EXIF orientation data; without honoring it, thumbnails appeared sideways. Added EXIF rotation in build. Lesson: image-handling slices need EXIF awareness — added to [[risk-register.md]] as R7 for future image features.
- S3 PUT latency at 5MB+ exceeded the 30s timeout we had. Bumped timeout to 60s. Real cost implication: P95 upload time is 8s, may need progress UI in frontend slice.

## Deferred

- Multiple receipts per transaction — out of scope per mission brief
- OCR — separate slice (slice-007 candidate)
- Receipt deletion — separate slice (slice-008 candidate)

## Critic calibration

- B1 (auth claim unsubstantiated): VALIDATED — Builder added the explicit check; tests confirmed it works
- B2 (MIME validation strategy): VALIDATED — pyheif was the right call; python-magic alone failed on HEIC
- m1 (hardcoded thumbnail size): NOT YET — no mobile UI exists yet to challenge it

**Missed by Critic**: EXIF orientation issue. Reasonable miss — Critic doesn't have iPhone-specific knowledge. Future slices touching images: add EXIF to Critic dimensions checked.

**Pattern**: Critic is reliable on auth and contract specificity; weak on platform-specific quirks (iPhone HEIC, Android FileProvider, etc.). For platform-specific slices, supplement Critic with a `/risk-spike` of the platform behavior.

## Lessons for next slice

- For any image feature: enumerate accepted formats AND EXIF handling in mission brief explicitly
- Upload features need progress feedback in UI — slice 004 should consider this
- S3 PUT timeout default (30s) is too aggressive for files >5MB

## Vault updates made

- [[risk-register.md]] — added R7 (EXIF orientation), R8 (S3 timeout sensitivity)
- [[components/storage-service.md]] — corrected sync/async claim, added EXIF handling note
- [[decisions/ADR-008.md]] — finalized with library choices (pyheif + Pillow)
```
