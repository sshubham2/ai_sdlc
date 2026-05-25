---
id: ADR-037
title: PTFCD-1 function-level check skips (no violation) when the cited test file is unparseable / non-Python
date: 2026-05-17
slice: slice-037-extend-ptfcd-1-to-test-function-level
reversibility: cheap
status: accepted
---

# ADR-037: PTFCD-1 function-level check skips (no violation) on an unparseable cited test file

## Context

Slice-037 extends PTFCD-1 from FILE-level (does the cited test *file* exist) to
function-level (does the cited test *function* exist inside it). The
function-level check requires parsing the cited file's AST. A cited file can
exist on disk yet fail `ast.parse` (genuine syntax error, partial WIP commit,
non-Python file mistakenly cited, encoding failure). The audit must have a
single, pre-decided disposition for that case — decided here at `/design-slice`
against the enforcing audits, not adjudicated late at `/reflect` (per
`_index.md:48` discipline; the slice-032 DEVIATION-1 anti-pattern is
auto-blessing such a decision without an ADR).

## Options considered

1. **Fail-CLOSED — emit a violation on parse failure** (e.g. `unparseable-test-file`).
   - Pro: a phantom function cannot hide behind a deliberately broken file.
   - Con: a syntax error is a *different* defect class than a phantom citation;
     conflating them muddies the PTFCD-1 signal. Worse: it converts a transient
     parse failure into a hard pipeline-gate FAIL (`/build-slice` Step 6 /
     `/validate-slice` Step 5.5), blocking the slice on something the FILE-level
     check already passed and that PTFCD-1 was never scoped to police. A false
     FAIL that halts the pipeline is the strictly worse failure mode for an
     audit gate than a missed niche sub-case.
2. **Skip-with-note — return tri-state `None`, emit NO violation.**
   - Pro: FILE-level guarantee is unchanged (the file demonstrably exists); the
     function-level layer is purely *additive* and degrades to FILE-level-only
     exactly as it does for empty `test_function` sentinels and no-`::`-selector
     rows. No new false-FAIL surface. Matches the project's audit-gate
     conservatism (false FAIL > missed niche).
   - Con: a phantom function in a file that *also* happens to be unparseable
     escapes detection. Bounded: requires two simultaneous defects; the parse
     error itself is loud at first `pytest` collection and is caught by the
     ordinary test run, so the phantom cannot survive to ship undetected.
3. **Skip silently with zero observability.** Rejected: violates the
   "actionable / observable" must-not-defer — a maintainer should be able to see
   the function-check was skipped.

## Decision

Adopt **Option 2 (skip-with-note)**. `tools/_pyfn.function_defined_in_file`
returns a tri-state: `True` (defined), `False` (parsed, not defined → violation),
`None` (could not parse / not Python / unreadable → function-level check skipped,
NO violation). `_pyfn` internally swallows `SyntaxError`, `OSError`,
`ValueError`, `UnicodeDecodeError` and returns `None` — it never raises into the
audit. Observability requirement: when `None` is returned for a row that *did*
carry a concrete function name, the audit's human formatter notes
`function-check skipped (file unparseable)` for that row so the skip is visible,
not silent.

## Consequences

- The two enforcing audits gain a `missing-test-function` violation ONLY on a
  definitive `False` (file parsed cleanly, function provably absent). Exit-code
  and JSON contracts extend additively (new violation kind / new `kind` field);
  no existing behavior changes when the function-level layer is not entered.
- FILE-level PTFCD-1 (slice-025) is untouched and remains the lower bound.
- **Observability is delivered, not asserted (M2)**: the `function-check
  skipped (file unparseable)` note is a design element (`_format_human` delta
  in both audits, tracked via an `AuditResult` skip-note list) AND a test-first
  row (`test_unparseable_file_emits_skip_note_in_human_output`). Option 3
  (silent skip) is therefore genuinely rejected, not rejected-in-name-only.
- **Function-name precedence (M3)**: the function-level layer resolves the
  name function-column-first, then falls back to the raw `test_path` `::`-tail
  when the function column is not a checkable identifier. This closes the
  `path::fn`-in-path-column + empty-function-column escape that the
  `_resolve_test_path` L294 `::`-strip would otherwise open (the codebase's own
  L286-288 docstring documents that shape as a real occurrence). The B2
  checkable-name discriminator gates BOTH sources. When BOTH the function
  column and the `test_path` `::`-tail carry checkable-but-different names
  (m-add-2), the function column wins and the path-column selector is not
  separately validated — the `Test function` column is the authoritative TF-1
  field; this is the conservative choice (it never under-checks the
  authoritative source) and is a stated decision, not an omission.
- If the bounded escape (phantom-fn-in-unparseable-file) is ever observed in
  practice, escalating to Option 1 is a cheap one-branch change — hence
  `reversibility: cheap`.

## Reversibility

**cheap** — the disposition is a single tri-state branch in `tools/_pyfn.py`
plus the audits' handling of `None`. Flipping to fail-closed is a localized
edit with a regression test; no contract consumer outside the two audits, no
data migration, no external API. Cost to change ≈ 1 hour.
