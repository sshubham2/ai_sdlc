# Critique Review: Slice 105 decouple-slice-loop-from-diagnose-out

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-03
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is strong and well-evidenced on the surfaces it covered — B1, B2, M1, M2, M4 all VALID with correct severity, verified against the actual test-pins and shippability rows. But it exhibited **pattern blindness on the reverse-dependency axis**: it traced what the deleted tests *guard* (forward) but not what *other live tests require the deleted files to exist* (reverse). That blind spot produced one missed **Blocker** (`test_resolve_slice_dir.py` hard-requires the deleted BCR-1 test file to exist) and two missed Majors. Additionally, the Builder's own ACCEPTED-FIXED edits introduced a row-labeling defect (design.md called catalog row #53 "Row #63") and left two fix-completeness gaps.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (SUP-1 superseded-by pointer violates append-only) — VALID, Blocker. `test_adr_063_exists_and_supersedes_adr_019.py:107-112` asserts `"superseded-by" not in fm` for ADR-019; ADR-063 unmodified after ADR-090 superseded it. The fix (ADR-094:45, ADR-095:35, design.md SUP-1 §) correctly reverses the plan; no residual `superseded-by` language survives.
- **B2** (shippability row-delete breaks row-must-exist pins + PTFCD-1) — VALID, Blocker. row #54 = L64, row #56 = L66; `test_methodology_changelog.py:3747` asserts `"| 54 | slice-054-…"`, `:3759` `"SC-001"`, `:3792` `"| 56 |…"`, `:3799` `"R-15"`. Fix (edit token, never delete row) correct.
- **M1** (row #79 runs cp_r test) — VALID, Major. L87 row #79 carries 5 tokens incl. the cp_r test; 4 survivor tokens named match the row. Fix correct.
- **M2** (build-sequencing + stale row #107 narrative) — VALID, Major. cp_r test assertions + row #107 stale narrative verified; `test_v_0_81_0_branch_3_shippability_consumer_propagation:5690-5705` is row-scoped, asserts only `BRANCH-3`/`ADR-090`/`R-31`/`pick` survive — the rewrite keeps exactly those.
- **M4** (missing v0.82.0 entry-pin + Row #105) — VALID, Major. No v0.82.0 entry exists; slice-099 paired-pin precedent real at :5603/:5672; fix matches the shape.
- **M5** (/slice step-renumber cross-refs) — VALID, Major. Step 3 (Seed) deleted → Write→3, queue→4; "Step-5 (queue-commit) failure" at `slice/SKILL.md:257` must become "Step-4". Fix names the exact line.
- **m1, m2** — VALID, Minor. Both correctly applied.

## Suspicious findings

None. Every first-Critic finding survived verification against the cited evidence — no over-reach on any filed finding. (The calibration signal here is under-reach, not over-reach.)

## Missed findings

- **B-add-1 (BLOCKER)**: Deleting `test_bcr_1_round_trip_end_to_end.py` breaks a live test in a NON-deleted module. `tests/methodology/test_resolve_slice_dir.py:66-88` (`test_test_bcr_1_module_no_longer_carries_hardcoded_slice_054_dir`) does `assert (REPO_ROOT/"tests"/"methodology"/"test_bcr_1_round_trip_end_to_end.py").is_file()` at `:77`. `test_resolve_slice_dir.py` is itself cited in shippability rows #56 and #57 (both run it) → the breakage surfaces at /validate-slice Step 5.5 AND the mid-slice smoke gate. **Fix**: in the same delete batch, delete/invert that guard test; verify rows #56/#57 stay green. Must be in mission-brief + the test-touched table.
- **M-add-1 (MAJOR)**: The reflect-prose-edit ↔ reflect-test-removal pairing needs the same atomic-batch guard M2 gave the cp_r pairing — but M2 was scoped only to build-slice. `reflect/SKILL.md:59` removal deletes content five live tests anchor on (`test_bcr_1_backlog_round_trip.py` #4–#8 at `:221,:247,:296,:331,:366`). **Fix**: extend the build-sequencing note to require the reflect bullet removal + #4–#8 removal in one batch (+ OSDG-1 reflect-mirror).
- **M-add-2 (MAJOR)**: `test_worktree_paths.py:17` carries `seed_derived_dirs,` in the `from tools._worktree_paths import (...)` block. After the function is deleted, that import raises `ImportError` at collection, failing the whole module incl. the surviving path/branch tests. The design's `:53-97` line-scope misses it. **Fix**: design must explicitly remove the line-17 import.

## Severity adjustments

None. All eight first-Critic findings carry correct severities (B1/B2 Blocker, M1–M5 Major, m1/m2 Minor), verified against blocking force.

## Notes

High confidence on B-add-1 (read the exact `assert ...is_file()` at `test_resolve_slice_dir.py:77`; confirmed rows #56/#57 run that module) and M-add-2 (read the line-17 import). High-medium on M-add-1 (five anchor tests verified). **Builder-introduced labeling defect** (below Major): design.md called the `test_bcr_1_backlog_round_trip` row "Row #63" — but that is catalog **row #53** at file-line L63; "#63" is the unrelated slice-063/NAW-1 occupant. AP-2 confirmations: the B1 reversal left zero residual `superseded-by` language (clean); the row #107 `seed_derived`/`test_worktree_paths` mentions are narrative-only, not command tokens (design.md's "drop the seed-token" was imprecise — harmless). **Calibration signal**: the first Critic's pattern is consistent forward-coverage + consistent reverse-coverage blindness — every miss is a "what else requires this deleted artifact to exist" question. Calibration-log-worthy for `/critic-calibrate` if it recurs.

### Builder disposition of meta-Critic findings (drafts)

- **B-add-1** → **ACCEPTED-FIXED**: design.md "Tests touched" adds a `test_resolve_slice_dir.py` row (delete/invert the `:66-88` is_file guard in the same batch; verify rows #56/#57); mission-brief "Must-not-defer" adds the reverse-dependency-completeness item.
- **M-add-1** → **ACCEPTED-FIXED**: design.md build-sequencing note extended to three atomic prose↔test pairs (build-slice, reflect, worktree_paths/bcr).
- **M-add-2** → **ACCEPTED-FIXED**: design.md `test_worktree_paths.py` row now removes the `:17` import explicitly.
- **Label defect** → **ACCEPTED-FIXED**: design.md corrected "Row #63" → "catalog row #53 (file-line L63)"; row #107 note clarified as narrative-only.
