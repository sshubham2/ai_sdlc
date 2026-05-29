# Validation: Slice 082 harden-pcr-1-soft-regen-corner-case

**Date**: 2026-05-29
**Result**: PASS

Validation environment: the ACs are validated by executing the real `resolve_soft_conflict` against **real tmp-repo rebase-in-progress conflicts** (the APED-1 battery builds a git repo, commits divergent branch content, runs `git rebase`, and drives the actual resolver over the conflict stages — not mocks). This is the real environment for a git-rebase conflict-resolution tool.

## Per-criterion results

### AC1: A failing regression test demonstrates the R-21 corner case (RED before fix)
- **Status**: PASS
- **Evidence**: `test_corner_case_soft_regen_diverges_from_baseline` — at HEAD-before-guard the resolver returned `APPLIED` with `add-foo`'s claim silently dropped (stderr: "claim for candidate 'add-foo' silently dropped — missing Risk-retired line"); the test asserts the desired `STOP` → RED pre-fix, GREEN post-guard. Mid-slice smoke gate recorded this RED in build-log.md.
- **Notes**: rebase-stage inversion discovered during build (`:2:`=master, `:3:`=branchA baseline) — fixture corrected.

### AC2: structural equivalence guard, fail-closed STOP, no repo mutation
- **Status**: PASS
- **Evidence**: `test_equivalence_guard_stops_on_unprovable_equivalence` (prelude divergence → STOP), `test_trailing_whitespace_heading_still_stops` (M1 — trailing-ws heading → STOP), `test_stop_leaves_repo_state_unmutated` (U-file still carries `<<<<<<<`/`>>>>>>>` markers + rebase-merge dir present + `regenerated_files == ()` after STOP). All PASS.

### AC3: divergent case routes to STOP + logged with structured reason
- **Status**: PASS
- **Evidence**: `test_guard_stop_logged_with_structured_reason` — after a guard-STOP, `architecture/parallel-conflict-resolution-log.md` contains a `## Soft-conflict resolution (equivalence-guard STOP) - <ts>` section with `**Reason**: equivalence-guard: ...`.

### AC4: canonical SOFT happy-path preserved (guard transparent when equivalence holds)
- **Status**: PASS
- **Evidence**: `test_happy_path_equivalence_holds_guard_transparent` (mixed claimed+unclaimed → APPLIED, claim survives — M-add-1) + `test_shippability_happy_path_guard_transparent` (row-union APPLIED). Full PCR suite 161 PASS; full repo suite 1173 PASS — no regression to the proven happy path.

### AC5: shippability row pins the equivalence guard (must-never-regress)
- **Status**: PASS
- **Evidence**: `test_shippability_pins_equivalence_guard` asserts `architecture/shippability.md` row 88 cites `tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py`. R-21 flip to retired/mitigating is a `/reflect` action (Step 5.2).

## Layered safety checks (VAL-1)
- **Result**: PASS — 0 secrets, 0 import findings, 0 suppressed.

## Walking-skeleton (WS-1)
- **Required?**: no (`**Walking-skeleton**: false`) — audit skipped clean.

## Exploratory charter (ETC-1)
- **Result**: PASS — 1 charter COMPLETED with findings (5 divergence/edge cases surfaced; see mission-brief charter table). The trailing-whitespace heading bypass (finding 4) was found via this adversarial exploration + the code-Critic and FIXED in-loop.

## Multi-instance validation
- **Required?**: no — single-process git-rebase conflict-resolution tool; cooperative threat model (ADR-067). The "multi-stage" dimension (stage-2 vs stage-3) IS exercised by every fixture.
- **Result**: not-applicable.

## Shippability catalog regression check
- **SCMD-1**: clean (87 rows; Machine-cmd column present; 0 incidental couplings).
- **PTFCD-1(b)**: clean (421 test-path tokens all resolve on disk).
- **Catalog run (SRSC-1 pinned runner)**: **87 rows, 87 PASS, 0 FAIL** — no past slice regressed; the new row 88 (equivalence guard) passes.

## Reality surprises
- **Rebase-stage inversion**: `git rebase master` (on branchA) assigns stage 2 = master and stage 3 = branchA (the baseline `_regen_slice_queue` uses), and `_merge_claim_dicts` keeps the stage-2 entry when stage-3's `claimed_at` is absent. Not a defect — but it inverts the naive "ours/theirs" intuition and drove the fixture branch-side design. Captured in the test helper docstring for future PCR test authors.
- **ETC-1 vs TF-1 field-parser inconsistency**: ETC-1's enable-flag regex is `$`-anchored (`(true|false)\s*$`) and rejects a trailing parenthetical that TF-1's looser parser tolerates. Cost one round-trip. Candidate for /critic-calibrate or a future cleanup (harmonize the two field parsers). Non-blocking for this slice.
