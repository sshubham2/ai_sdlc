# Code Review: Slice 082 harden-pcr-1-soft-regen-corner-case

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-29
**Result**: FINDINGS (0 blockers, 1 major, 3 minors) — all addressed in-loop

## Summary
The equivalence guard is structurally sound: genuinely read-only, runs strictly before the first `write_text`/`git add`/`git rebase --continue` (atomicity holds — `test_stop_leaves_repo_state_unmutated` re-run green), `_fail` unconditionally raises (no fall-through NameError on `pending_claims`), and no unguarded exception escapes the caller's `_SoftResolutionError`-only `except`. The code-Critic found **one real Major (M1)**: the guard's heading regex `^### (.+)$` did not `.strip()` while the canonical `parse_queue_text` rstrips — so a trailing-whitespace baseline heading would silently bypass invariant #1, defeating the exact fail-closed property R-21 demands (and violating this slice's must-not-defer #1). **M1 was fixed in-loop** (correctness defect in the slice's core deliverable, not advisory polish) plus the three minors (cheap, same code). Final state: 0 blockers, 1 major (FIXED), 3 minors (FIXED).

## Changed files (in-scope)
- tools/parallel_conflict_resolver.py
- tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py
- architecture/slices/slice-082-harden-pcr-1-soft-regen-corner-case/build-log.md

## Findings

### Blockers
None. Atomicity + fail-closed-on-error properties hold; no path writes/stages/continues before the STOP; no unguarded exception escapes the caller. Honest 0-blocker result.

### Majors

#### M1: invariant #1 heading regex did not rstrip — a trailing-whitespace baseline heading silently bypassed the fail-closed claim-preservation check (APED-1 adversarial-variant miss)
- **Claim under review**: `tools/parallel_conflict_resolver.py` invariant #1 — `baseline_headings = set(_re.findall(r"^### (.+)$", baseline_text, _re.MULTILINE))`.
- **Issue**: `claimed_names` derive from `parse_queue_text` whose header match runs after `raw_line.rstrip()` (`slice_queue_claim.py:113`), so canonical names are rstripped; the guard's `(.+)` capture was NOT. A baseline `### add-foo ` (trailing space) yields `'add-foo '`, so `claimed_names ∩ baseline_headings == ∅` and the preservation loop skipped `add-foo` — the guard PASSED even with the claim dropped. False-negative in a guard whose entire purpose (R-21 / ADR-074) is to fail-closed on exactly that silent-divergence class.
- **Disposition**: **FIXED in-loop** (required by must-not-defer #1 "fail-closed; never silent-proceed"). All three heading captures now `{m.strip() for m in _re.findall(...)}` (`baseline_headings` + `stage2_headings` + `stage3_headings`). Added adversarial test `test_trailing_whitespace_heading_still_stops` — RED pre-fix, GREEN post-fix.

### Minors

#### m1: invariant #2 is near-tautological against `_merge_shippability` — read as a round-trip backstop
- **Issue**: `_merge_shippability` builds output rows as `numbered_2 | numbered_3` by construction, so #2's key-set equality is near-tautological (meta-Critic flagged the same). Not dead — catches a lossy re-parse — but reads as dead verification without a note.
- **Disposition**: **FIXED in-loop** — added a docstring note clarifying #2 is a round-trip-STABILITY backstop (catches `_parse_shippability_rows`/`_merge_shippability` desync), with content-mutation handled by #3 (prelude) and `_merge_shippability`'s HARD escalation (same-number).

#### m2: `_fail` annotated `-> None` but never returns — a type-checker cannot prove post-`_fail` unreachability
- **Issue**: `_fail` unconditionally raises, but `-> None` lets mypy/pyright think the `except` block falls through → spurious "possibly-unbound `pending_claims`" + masks a future reorder bug.
- **Disposition**: **FIXED in-loop** — `from typing import NoReturn`; `def _fail(reason: str) -> NoReturn:`.

#### m3: M2 `discarded_headings` selection via `baseline_text == text_3` full-text equality used as a stage-identity test — fragile
- **Issue**: Re-deriving "which stage is the baseline" by full-string comparison is indirect (correct today, but a warn-only path).
- **Disposition**: **FIXED in-loop** — `baseline_is_stage3 = bool(text_3)` at selection time; `discarded_headings = stage2_headings if baseline_is_stage3 else stage3_headings`.

## Dimensions checked
- [x] Unfounded assumptions — m3 (full-text stage-identity probe) FIXED.
- [x] Missing edge cases — M1 (trailing-whitespace heading) FIXED + test added; CRLF sub-variant mitigated (`_git_show_stage` uses `text=True` universal-newline decoding); empty/asymmetric-stage handled.
- [x] Over-engineering — m1 (invariant #2 near-tautological) documented as round-trip backstop; reuse of `_SoftResolutionError` (no new class) is the simpler choice.
- [x] Under-engineering — none beyond M1. All 5 ACs have delivering code + executed-green tests (9 tests in the module).
- [x] Contract gaps — m2 (`_fail` missing `NoReturn`) FIXED. No phantom imports (verified on disk).
- [x] Security — none. No new auth/input boundary; subprocess argv list-form with fixed verbs; no `shell=True`; audit log structured non-PII.
- [x] Drift from vault — none. Diff touches exactly the 3 design-declared in-scope files; call-site at the design-pinned position; reuses `_SoftResolutionError(UNKNOWN)`; `(equivalence-guard STOP)` audit variant per AC-3.
- [x] Web-known issues — Python `re` MULTILINE `$`/CRLF behavior checked; `text=True` mitigates the CRLF sub-variant; no deprecated API (`datetime.now(timezone.utc)` not `utcnow()`).
- [x] Cross-cutting conformance — M1 was the primary APED-1 finding (new heading regex not executed against the trailing-whitespace adversarial variant; diverged from canonical `slice_queue_claim.py` rstrip parser) — FIXED + adversarial test. RSAD-1/EOL-DRIFT-1 conformant. No unguarded exception escapes the caller.
