# Mission brief template

> **Note**: This template is also embedded inline in [`../skills/slice/SKILL.md`](../skills/slice/SKILL.md). The skill is the live source; this file is a standalone reference for humans reading the docs.

Per-slice brief. Lives in `architecture/slices/slice-NNN-<name>/mission-brief.md`.

Designed to be ~1 page (~60 lines max). Replaces the 500-line handoff-ai sprint file.

---

## Template

```markdown
# Slice NNN: <verb-object name>

**Mode**: [Minimal | Standard | Heavy]
**Risk tier**: [low | medium | high] — controls whether `/critique` is skippable
**Critic required**: [true | false] — true if slice touches auth/contracts/data model/multi-device/external integrations/security; else derived from tier (low=false, medium/high=true)
**Estimated work**: [<1 day | 1 day | split needed]
**Risk retired**: <which risk(s) from register this slice validates>

## Intent

<2–3 sentences: what user-visible behavior ships with this slice, and why now>

## Acceptance criteria

Each criterion must be:
- Testable (a real check produces pass/fail)
- Observable (a human or tool can see the result)
- Small (one sentence)

1. <criterion 1>
2. <criterion 2>
3. <criterion 3>
4. (max 5)

## Verification plan

For each acceptance criterion, how it'll actually be checked:

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | ... | `curl <url>` returns 200 with <schema> |
| 2 | ... | Open <page> in real browser, click <button>, observe <outcome> |

## Must-not-defer

Items that must be in this slice, not punted:

- [ ] Input validation on <endpoint>
- [ ] Error handling for <failure mode>
- [ ] Authorization check on <protected action>
- [ ] Logging at <critical path>
- [ ] <other security/observability/data-integrity item>

## Out of scope

Explicit non-goals (prevents scope creep):

- <thing this slice deliberately won't do>
- <thing that's a different slice>

## Dependencies

- Prior slices: [[slice-NNN-name]] — <what we depend on>
- Vault refs: [[components/X]], [[decisions/ADR-NNN]]
- Risk register: [[risk-register#R1]]

## Mid-slice smoke gate

At ~50% of build, run:

```
<specific command or manual steps>
```

Expected: <outcome>

If this fails: STOP, diagnose, don't continue building on a broken base.

## Pre-finish gate

Before declaring done:

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
```

---

## How to use

1. `/slice` generates this file
2. `/design-slice` reads it to scope design
3. `/critique` reads it to know what to evaluate against
4. `/build-slice` reads it as the execution contract
5. `/validate-slice` reads it for the verification plan
6. `/reflect` reads it to score what was promised vs delivered

## Worked example

```markdown
# Slice 003: add-receipt-upload

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R3 (image storage cost), R5 (HEIC support uncertainty)

## Intent

Users can upload a receipt image when entering a transaction. Image is stored in object storage with a thumbnail generated for the list view. This retires the image-storage cost question by exercising the actual flow at typical sizes.

## Acceptance criteria

1. POST /transactions/:id/receipt accepts JPEG, PNG, HEIC up to 10MB
2. Original stored in S3 at `receipts/{transaction_id}/{uuid}.{ext}`
3. Thumbnail (200×200 WebP) generated and stored alongside
4. GET /transactions/:id returns receipt URL + thumbnail URL
5. Files >10MB return 413; unsupported formats return 415

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Upload accepted | `curl -F "file=@sample.heic" .../receipt` returns 201 |
| 2 | Stored in S3 | `aws s3 ls receipts/<txn>/` shows file |
| 3 | Thumbnail created | Same `aws s3 ls` shows .webp file |
| 4 | URLs returned | `curl .../transactions/<id>` JSON includes both URLs |
| 5 | Limits enforced | `curl -F "file=@huge.jpg" .../receipt` returns 413 |

## Must-not-defer

- [ ] Authorization: only transaction owner can upload to that transaction
- [ ] MIME type validation (don't trust extension)
- [ ] Size check before reading full body into memory
- [ ] Logging on upload failure (which step failed)

## Out of scope

- Receipt OCR / data extraction (separate slice)
- Multiple receipts per transaction (single receipt for now)
- Receipt deletion (separate slice)

## Dependencies

- [[slice-001-create-transaction]] — transaction must exist
- [[components/storage-service]] — to be created this slice
- [[decisions/ADR-005-object-storage-s3]] — already locked

## Mid-slice smoke gate

```
curl -F "file=@samples/receipt.heic" -H "Auth: <token>" \
  http://localhost:3000/transactions/test-001/receipt
```

Expected: 201 + JSON with receipt_url, thumbnail_url. Open both URLs in browser, both render.

## Pre-finish gate

- [ ] All 5 ACs PASS in validation.md
- [ ] Authorization enforced (verified by attempting upload as different user → 403)
- [ ] MIME validation rejects renamed .exe → 415
- [ ] /drift-check passes
- [ ] No console.log left in upload handler
```
