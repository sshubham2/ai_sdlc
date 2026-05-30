# Critique Review: Slice 084 harden-pcr-2a-clock-skew-winner

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-30
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's six findings are all VALID with correct severities, and the Builder's fix-deltas
hold up against ground truth — verified the three load-bearing claims against actual code
(offset-conditional emission at `slice_queue_writer.py:589-594`, the `>=3.10` floor at
`pyproject.toml:24`, and the `+00:00`-not-`Z` canonical writer at `slice_queue_claim.py:629`). The
post-fix parse logic does NOT introduce a new defect. Surfaces one genuinely-missed Minor (dead
`loser` param in the heuristic signature) and one missed Minor verification gap (audit `now`
serialization unspecified).

## Confirmed findings

- **B1** (naive-vs-aware `TypeError` mid-rebase): confirmed; Blocker appropriate. Reachability
  premise verified — `slice_queue_writer.py:591-594` emits the offset only when `tzinfo is not None`,
  so offset-less `claimed_at` is reachable on non-adversarial data. Fix order sound: the `tzinfo is
  None` gate returns STOP *before* the `parsed > now` compare, so no naive value reaches the compare;
  the `except (ValueError, TypeError)` wrap is correct belt-and-suspenders. **No new defect in the fix.**
- **B2** (`Z`-suffix unparseable on 3.10): confirmed; Blocker appropriate. `requires-python = ">=3.10"`
  verified; `fromisoformat` Z-support is 3.11+. The `s[:-1] + "+00:00"` normalization round-trips
  (matches the canonical writer's exact format). The "normalize-Z-then-naive crashes" concern is a
  non-issue: an offset-less value never matches `endswith("Z")`, parses naive, and is caught by the
  `tzinfo is None` gate. No corpus row the fix mishandles.
- **M1** (retired → narrowed): confirmed; Major appropriate. Reframe is consistent across all three
  sites (mission-brief AC-4, design.md §Heuristic, ADR-076 §Consequences) — same residual named,
  same "open (downgraded)" status. Narrowing still justifies the slice (egregious sub-case →
  fail-closed STOP + corrigibility hook).
- **M2** (resolver-now trust by fiat): confirmed; Major appropriate. ADR-076 now documents the
  merger-clock-is-reference assumption + degradation modes; design.md mirrors it.
- **m1** (tolerance boundary not pinned): confirmed; Minor appropriate. 300s/301s TF rows pin it.
- **m2** (FBCD-1 reframe propagation): confirmed; Minor appropriate. Three-site parity verified.

## Suspicious findings

None. Every first-Critic finding is grounded in the design and in ground truth; the Builder's
fix-deltas do not over-correct.

## Missed findings

- **m-add-1: dead `loser` param in `_winner_clock_skew_suspect`** — signature is
  `_winner_clock_skew_suspect(winner, loser, now, tolerance_seconds)` but the body reads only
  `winner.claimed_at`, `now`, `tolerance_seconds`; `loser` is never referenced. `loser` IS
  legitimately used by the *separate* `_append_skew_stop_audit(..., winner, loser, now)` (records
  BOTH claims per AC-2), so the data is needed at the call site — but not inside the detector. Per
  Fowler "Remove Dead Parameter" / Speculative Generality. **Fix**: drop `loser` from
  `_winner_clock_skew_suspect`'s signature (call site already holds the pair and passes `loser`
  straight to the audit helper), OR docstring-note it as retained for symmetry. Severity: **Minor**.
- **m-add-2: audit `now` rendering format unspecified** — `_append_skew_stop_audit` records "the
  resolver-now signal" but neither design.md nor the error model pins how the injected `now` datetime
  is serialized. The slice-082 mirror derives its own `.isoformat()` timestamp rather than taking an
  injected one, so the precedent doesn't cover an injected-`now` render path. A forensic field whose
  serialization is unspecified risks a non-round-trippable record. **Fix**: specify `now` rendered via
  `.isoformat()` (aware, `+00:00`) into the skew-STOP section, matching the canonical `Claimed-at`
  format so the audit row is directly comparable. Severity: **Minor**.

## Severity adjustments

None. All six first-Critic severities correctly filed.

## Notes

Confidence high — each B-fix traced against actual source, not the design's self-description; the
parse-order logic (normalize → parse → naive-gate → compare, each guarded) has no path to a
`naive > aware` comparison. Tie-path interaction is a non-issue: `_select_timestamp_winner` returns
`None` on tie at Step 2 (`:1146-1155`), STOPped before the Step 2.5 guard runs, so the guard only
sees a real winner. Audit-append concurrency is a non-issue (single-process, rebase-in-progress,
mirrors accepted slice-082 precedent). First-Critic calibration this slice: strong on correctness,
claim-accuracy, and test-pinning; small blind spot on signature/serialization hygiene (both Minor,
neither threatens shippability). EXTEND (not ACCEPT) because two real Minor concerns surface — both
belong in TRI-1 as Builder cleanup items, not finish-blockers.
