# Critique Review: Slice 054 fix-pyproject-toml-version-drift

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-21
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's four Majors and two Minors all hold as VALID against the original (pre-fix) state, and the Builder's ACCEPTED-FIXED edits are substantively responsive on M1-M4 and m2. Re-applying the 8 dimensions to the post-fix state surfaces three new concerns the first Critic missed — one Major (PVFS-1 has zero per-Critic-recommended-pattern entry-pin contract assertion in the rule registry surface) and two Minors (test-name lying about scope after M1 acceptance; a stale `0.59.0` literal in `architecture/shippability.md` row #54 prose preserved from /repro). Net: EXTEND, not ADJUST.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **M1** (AC3 pin test "TBD"): VALID — design.md /design-slice draft (pre-fix) left the AC3 test path unspecified despite AC3 explicitly requiring it. Per Wiegers (Software Requirements §10 — every AC is testable) + TF-1, this was a real gap. Severity Major is appropriate. Post-fix design.md§What's-new correctly mints `test_pyproject_has_no_stale_v_0_20_0_or_count_literals` co-located in the existing AC1 test file — clean fix.
- **M2** (stale-literal enumeration 2-of-3): VALID — I cell-verified pyproject.toml against `grep -nE "v0\.20\.0|0\.20\.0|13 audit|13 tool"` and confirmed 4 hits (lines 3, 6, 20, 66). The substantive scrub sites are 3, 6, 66 (line 20 IS the `[project].version` field bumped by SC-001 directly), and design.md§What's-new now enumerates all three. Severity Major is appropriate (CCC-1 mechanical-inventory class). Per Hendrickson (exploratory testing — mechanical enumerations must be cell-verified, not asserted).
- **M3** (smoke-gate literal cross-file inconsistency): VALID — FBCD-1 sub-mode (a) original-draft cross-file inconsistency is exactly the class. Severity Major is appropriate because a falsely-green smoke gate at the slice halfway-point would mask the actual atomic-4-part-bump partial-completion hazard the design itself flags as "the slice-054 self-violation hazard". Post-fix mission-brief.md correctly updates the literal to `0.62.0`.
- **M4** (AC4 BCR-1 grep position-semantic gap): VALID — first BCR-1 end-to-end dogfood; if the AC4 verification is content-only the round-trip mechanism cannot be regression-pinned (BCR-1 invariant is positional: AFTER `**Evidence:**` AND BEFORE next `### SC-NNN`). Severity Major is appropriate per Newman (Building Microservices §7 — contract tests must encode the contract's invariant axis, not a weaker proxy). Post-fix verification plan now correctly walks awk + grep-line-number with three position-pinned ASSERTs.
- **m1** (SC-001 backlog block heading `VERSION = 0.59.0`): VALID — confirmed by reading `diagnose-out/backlog.md` line 87. Severity Minor is appropriate; out-of-scope per BCR-1 append-only discipline is the right disposition. Builder draft DEFERRED-to-`/critic-calibrate` is sound (not a meta-finding to override).
- **m2** ("Components touched" misleading parenthetical): VALID — wording reads as forward-reference to a separate detail table. Severity Minor appropriate; the post-fix rewrite to a clean bullet inventory is materially better.

## Suspicious findings

No suspicious findings. All six first-Critic findings hold against the original state, and the post-fix dispositions are responsive without over-reach.

## Missed findings

Concerns the first Critic didn't flag but the meta-Critic surfaces from independent re-review (post-ACCEPTED-FIXED state):

- **M-add-1: PVFS-1 entry-pin shippability-consumer-propagation test asserts only `PVFS-1` rule-ID mention — does not pin that row #54 cites BOTH `SC-001` AND `PVFS-1` (the slice's two anchor IDs)**. Per slice-049/050 entry-pin precedent (cited as design.md§What's-new precedent), the shippability-consumer-propagation pins both the RULE-ID *and* the originating-finding ID where one exists, so a future row rewrite that drops the SC-001 cite (severing the `/diagnose → /slice → /reflect` traceability axis that slice-053 BCR-1 just shipped to enforce) would silently pass `test_v_0_62_0_pvfs_1_shippability_consumer_propagation`. design.md§What's-new currently specifies only `asserts ... mentions PVFS-1`. Per Fowler (Refactoring §4 — tests pin behavior, not implementation) + Wiegers (every contract surface needs its specific assertion): add `AND mentions SC-001` to the pin contract. This is the first slice to dogfood BCR-1's structural axis, so the SC-NNN trace must be regression-pinned in the shippability row that exists *because of* the SC-NNN. Severity: **Major** (loss of the BCR-1 traceability axis on the slice that mints it is a methodology-surface regression class).

- **m-add-1: AC3 pin test name lies about scope after M2-driven enumeration expansion**. The test is named `test_pyproject_has_no_stale_v_0_20_0_or_count_literals` but the M2 enumeration includes **line 3** (`methodology-changelog.md v0.20.0`), which is a version-reference, not a "count literal" — yet ALSO is a "v0.20.0 literal", so the test name still covers it via the `v_0_20_0` half. However, design.md§What's-new lists the assertions as `"0.20.0" not in pyproject_text AND "13 audit modules" not in pyproject_text AND "13 tool modules" not in pyproject_text` — bare `"0.20.0"` not the `v` prefix. After the SC-001 bump (`[project].version = "0.62.0"`) the bare `"0.20.0"` substring catches line 3 (`v0.20.0` contains `0.20.0`), line 6 N/A (count literal, not version), line 66 (`v0.20.0` contains `0.20.0`). The test is correct, but the function name's "or count literals" + the bare `0.20.0` assertion don't quite match — function name says `v_0_20_0` (v prefix) while assertion uses bare `0.20.0`. Recommend either rename to `test_pyproject_has_no_stale_0_20_0_or_count_literals` (drop the `v_` prefix from the name) OR change the assertion literal to `"v0.20.0"`. Severity: **Minor** (cosmetic naming-vs-assertion divergence; the substantive coverage is correct).

- **m-add-2: shippability row #54 prose preserved at /repro carries the SC-001 description "VERSION = 0.59.0" via the SC-001 finding-text** (verified at `architecture/shippability.md:64`). The row #54 long-description column reads `Pre-fix observed at slice-054 reproduction: pyproject.toml [project].version = "0.20.0" while VERSION = "0.61.0"`. Actually wait — I verified this: row #54 correctly says `"0.61.0"`, NOT `"0.59.0"`. SUSPICIOUS-ON-MY-OWN-DRAFT — withdrawing m-add-2; the row is correct. (Recording the withdrawal here transparently: I drafted this finding from the SC-001 backlog block heading m1 conflation, then re-verified against the actual shippability.md and found the row was correctly written at /repro on 2026-05-21 against the then-current VERSION=0.61.0. No missed finding here.)

## Severity adjustments

No severity adjustments. M1-M4 are correctly filed as Major; m1-m2 correctly filed as Minor.

## Notes

Confidence: **high** on the four confirmed Majors and M-add-1; **medium** on m-add-1 (cosmetic only, may not merit a Builder round-trip). The first Critic's coverage pattern in this slice is solid on the cross-file inconsistency / mechanical-enumeration / contract-position axes (M2, M3, M4) and on the test-first acceptance-criterion gap (M1) — these are the dimensions the first Critic is consistently strong on across the slice-049+ cohort. The single missed concern (M-add-1, the BCR-1-traceability entry-pin scope) is a slice-specific blindness: slice-054 is the **first end-to-end BCR-1 dogfood**, so the regression-pin contract for the SC-NNN trace axis is novel-to-this-slice and easy to miss. This is not a calibration-worthy pattern unless it recurs at the next BCR-1-closing slice (slice-055+). The Builder's ACCEPTED-FIXED dispositions on M1-M4 and m2 are all substantively responsive; the post-fix design.md and mission-brief.md are materially improved and no new issues are introduced by the fixes themselves. One m-add-2 candidate (stale `0.59.0` in shippability row #54) was drafted then withdrawn on cell-verification — recorded transparently here per the calibration discipline that surfaces my own false-positives, not just the first Critic's.

---

Relevant absolute paths consulted:
- `<HOME>\ai_sdlc\pyproject.toml` (lines 3, 6, 20, 66 stale literals verified)
- `<HOME>\ai_sdlc\VERSION` (`0.61.0`)
- `<HOME>\ai_sdlc\plugin.yaml:15` (`version: 0.61.0`)
- `<HOME>\ai_sdlc\diagnose-out\backlog.md` (SC-001 block lines 87-105; backlog header `VERSION = 0.59.0` confirmed at line 87 — m1)
- `<HOME>\ai_sdlc\architecture\shippability.md:64` (row #54 already exists from /repro)
- `<HOME>\ai_sdlc\tests\methodology\test_pyproject_version_matches_version_file.py` (AC1 repro test, 92 lines)
- `<HOME>\ai_sdlc\architecture\decisions\ADR-056-mint-pvfs-1-pyproject-version-forward-sync.md`
- `<HOME>\ai_sdlc\methodology-changelog.md:37` (`## v0.61.0` — next bump target `v0.62.0` confirmed unused)
