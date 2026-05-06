---
name: repro
description: "Bug-fix discipline: establish a FAILING test that reproduces the issue BEFORE the fix slice begins. Codifies the 'tests-first for bug fixes' rule from brownfield CLAUDE.md. Writes the reproduction test, confirms it fails with the expected signature, adds it to shippability.md (so the bug can never silently return), then hands off to /slice for the fix. Trigger phrases: '/repro', 'reproduce this bug', 'failing test first', 'repro <issue>', 'establish repro'."
user_invokable: true
argument-hint: <issue description>
---

# /repro — Reproduction-First Bug Fix

You establish a FAILING test that reproduces a bug before any fix code is written. This is the classic TDD-for-bugs discipline, formalized as a pipeline step.

## Where this fits

Runs BEFORE `/slice` when fixing a non-trivial bug. After `/repro` completes, you run `/slice "fix <issue>"` with the reproduction test already in the shippability catalog; the fix slice's acceptance criteria include "make the shippability entry pass."

For trivial bugs (typo, one-line): skip `/repro`, just fix. The CLAUDE.md "what does NOT need a slice" list still applies.

## Why this exists

Without `/repro`:
- Fix goes in without a test. Same bug regresses later; you fix it again. Cycle repeats.
- The "failing test first" discipline is in CLAUDE.md but easy to skip.
- Shippability catalog grows slice-by-slice but doesn't reliably include regression tests for KNOWN bugs that get fixed.

With `/repro`:
- Reproduction test exists and is verified failing BEFORE fix code is written.
- Test lives in shippability catalog permanently — this bug can't silently return.
- Fix slice has unambiguous acceptance criterion: "make the failing test pass."

## Prerequisite check

- `architecture/shippability.md` must exist (created by `/reflect` after first completed slice; if not: `/repro` will create it)
- An active slice folder should NOT exist. `/repro` creates test infrastructure, not a slice yet — if another slice is active, finish or abandon it first

## Your task

### Step 1: Understand the issue

Parse the argument — the user's issue description. If vague, ask 2-3 clarifying questions ONE AT A TIME:

- **Exact reproduction steps**: what does the user / request look like that triggers the bug?
- **Expected behavior**: what should happen?
- **Actual behavior**: what actually happens?
- **Environment**: any specific conditions (browser, device, account state, data shape)?

Don't accept vague descriptions. "It's slow" is not actionable; "P95 latency on POST /receipts exceeds 30s for HEIC files >5MB" is actionable.

### Step 2: Query the graph for context

Before writing the test, understand the buggy code area:

```bash
$PY -m graphify reachable --from="<relevant-module>"   # what this module depends on
$PY -m graphify blast-radius --from="<relevant-module>" # what depends on it
$PY -m graphify query "<area-keyword>"                  # keyword match on graph labels (substring, not semantic)
```

If graphify surfaces a past slice with a similar bug: check its reflection. This might be a regression of a previously-fixed bug (in which case the shippability catalog itself is incomplete — note that).

### Step 3: Write the failing test

Write an actual test in the project's test framework (pytest / jest / go test / etc.). The test must:

- Be RUNNABLE from project root with a single command
- Specifically target the bug's trigger, not adjacent surface
- Complete in <10 seconds (shippability runtime budget)
- Have a clear assertion that would pass when the bug is fixed

Example:

```python
# tests/bugs/test_receipt_upload_heic_timeout.py
"""
Bug: POST /receipts returns 500 for HEIC files >5MB (slice-XXX candidate)
Expected: returns 201 within 10s
Actual: returns 500 (timeout) after 30s
"""
def test_heic_large_upload_succeeds():
    resp = client.post(
        "/transactions/test-001/receipt",
        files={"file": ("sample.heic", open("tests/fixtures/5mb.heic", "rb"))},
    )
    assert resp.status_code == 201
    assert resp.json()["receipt_url"]
```

Put the test in a dedicated location: `tests/bugs/` or project's convention for bug-fix tests.

### Step 4: Confirm the test actually FAILS

Critical: run the test BEFORE claiming reproduction. It must fail with the expected signature.

```bash
pytest tests/bugs/test_receipt_upload_heic_timeout.py -v
# Expected output: FAILED (500 != 201)
```

If the test passes (bug doesn't reproduce): STOP. Either:
- The issue description is wrong / already fixed
- The environment doesn't match the bug's trigger
- The test isn't targeting the right path

Do NOT proceed to fix a bug you can't reproduce. Loop back with the user: "the test I wrote passes — can you confirm the reproduction steps?"

### Step 5: Add to shippability catalog

Append a new entry to `architecture/shippability.md`:

```markdown
| <next-#> | <bug-ID or future slice name> | <issue one-liner> | `<test command>` | <runtime> |
```

Example:
```markdown
| 23 | slice-024-fix-heic-timeout | POST /receipts HEIC >5MB returns 201 within 10s | `pytest tests/bugs/test_receipt_upload_heic_timeout.py` | ~4s |
```

Note: the slice number is a placeholder ("slice-024-fix-heic-timeout") — user will confirm when `/slice` runs. If they name it differently, update the shippability row.

### Step 6: Hand off to /slice

Output:

```
Reproduction established.

Test: tests/bugs/test_receipt_upload_heic_timeout.py
Status: FAILING as expected (500 != 201)
Added to shippability.md as entry #23.

Run `/slice "fix HEIC >5MB upload timeout"` next. The slice's mission brief should include:
- Acceptance criterion: pytest tests/bugs/test_receipt_upload_heic_timeout.py passes
- Out of scope: broader upload refactor (separate slice if needed)

After the fix slice completes and /validate-slice passes, this bug can't silently return — the shippability catalog will catch it in every subsequent /validate-slice run.
```

## Critical rules

- NEVER proceed if the test passes. A non-reproducing "repro" is worse than none.
- NEVER write the fix in this skill. Fix code is the slice's job; /repro only establishes the test.
- TESTS must be fast (<10s) — shippability catalog runs every slice, latency compounds.
- DOCUMENT the bug in the test docstring (expected / actual / slice reference).
- ONE bug per /repro. Don't bundle multiple bugs into one reproduction.

## What /repro is NOT

- Not for feature work. Features go straight to `/slice` with user-story ACs.
- Not for performance regressions without clear signal. "Feels slow" isn't a bug; "P95 > 2s measured" is.
- Not for typos or trivial fixes. Those are on the CLAUDE.md "skip pipeline" list.

## For brownfield specifically

The brownfield CLAUDE.md already says "tests-first for bug fixes." This skill is that rule made concrete. When adopting AI SDLC onto an existing codebase, `/repro` is often the first skill run after `/adopt` — every known bug gets a reproduction added to shippability before any fix slice.

## Principle alignment

- Reinforces **Iterate per slice** (Principle 1): fix slice has a concrete AC (make test pass)
- Builds the regression protection layer: every fixed bug stays fixed because shippability catalog runs every /validate-slice

## Next step

`/slice "fix <short issue name>"` — the fix slice. Its mission brief will include the reproduction test as an AC.
