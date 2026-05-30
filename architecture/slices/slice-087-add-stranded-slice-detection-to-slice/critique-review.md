# Critique Review: Slice 087 add-stranded-slice-detection-to-slice

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-30
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

> Spawned via `Agent` `subagent_type: "critique-review"`; per SAOF-1 written ONLY from the agent's actual returned content.

## Summary

The first Critic's review is sound and well-calibrated — all seven findings (B1, M1–M4, m1, m2) are VALID at correct severities, and the Builder's ACCEPTED-FIXED reshapes are disk-verified correct, NOT TPHD-1 self-fix regressions. Two Minor missed findings surface, both rooted in the slice's self-referential nature (it edits the very `/slice` skill run to define it).

## Confirmed findings

All seven first-Critic findings VALID + correct severity, disk-verified:
- **B1** — confirmed; the bare-unmerged-branch-without-worktree case IS genuinely new (`detect_active_worktrees` L295 walks `worktree list` only + filters to on-disk paths L328; a bare branch never appears). Builder's reuse-worktree-half + add-bare-branch-half decomposition is correct.
- **M1** — confirmed; INSTALL.md has exactly two "33" surfaces (L22+L166), both in AC5's `33→34`.
- **M2** — confirmed; `--root` alias fix sound (`_root_only_argv` L76-77 passes `--root`; `_assert_no_encoding_error` L56-64 checks UnicodeError only, not exit code → without the alias, vacuous pass). Does NOT mask a coverage gap.
- **M3** — confirmed; Relationship-to-R-22 clause correctly partitions worktree-window (R-22, closed) from open-time + bare-branch (R-26, new).
- **M4** — confirmed; `/pulse` guard is the existing `test_pulse_skill_drift.py`.
- **m1** — confirmed; MEPD cite now ADR-070 (slice-077 tool-shipping precedent).
- **m2** — confirmed; per-branch merge-base error → `indeterminate`, not run-failure.

## Suspicious findings

None. Two candidate over-reaches tested and both failed (first Critic was right): (1) `WorktreeInfo` return-shape leakage — design uses a DISTINCT union record `{branch, worktree_path|null, ahead, dirty, indeterminate}` for the bare-branch half, so reuse is scoped to the worktree half only (reuse is fit because half-scoped); (2) `default-branch-unresolvable` is explicitly routed to exit 2. Neither filed.

## Missed findings

- **m-add-1 (Minor): Self-reference false-positive — the active slice's own `slice/NNN` branch can register as stranded on a later `/slice` run; no test pins this.** Under BRANCH-2, `/build-slice` creates `slice/NNN` for this slice; after `/commit-slice --push` (happy path, awaiting PR) or a `--merge` worktree-remove failure (both live states per risk-register L384/389), that branch becomes a bare-unmerged-`slice/*`-branch-without-worktree → flagged stranded on the NEXT `/slice`. That's partly intended, but the must-not-defer "no false positives" list enumerates only `recovery/* + merged + main worktree`, and AC4's four cases have NO "legitimately-in-flight slice branch awaiting its own PR merge" case. **Proposed fix**: add a 5th AC4 behavioral case (pushed-but-unmerged `slice/*` branch); document in design.md §Error model that "pushed-awaiting-PR / in-flight" is an EXPECTED stranded classification (the Resume/Continue-build options frame it correctly), NOT a false positive. (Advisory-never-blocking caps blast to an extra prompt — Minor — but it's the slice's own primary use case, untested.)
- **m-add-2 (Minor): `recovery/*` exclusion mechanism undocumented + orphan-branch ahead-count undefined.** (a) `recovery/*` is excluded because `for-each-ref refs/heads/slice/` only enumerates that glob (robust — current `recovery/slice-086-*` live at `refs/heads/recovery/...`, outside it) — but the design states the exclusion as an OUTCOME without naming the MECHANISM (ref-glob, load-bearing; a maintainer widening to `refs/heads/` would silently break it). (b) `git rev-list --count <default>..<branch>` ahead-count is undefined for an orphan branch sharing no merge-base; `pulse_worktree_resolver` never computes ahead-count, so no reuse precedent. **Proposed fix**: design.md note that `recovery/*` exclusion is enforced by the `refs/heads/slice/` ref-glob (load-bearing); specify ahead-count on a no-common-ancestor branch (`ahead: null` or count-from-root, Builder's call).

## Severity adjustments

None. All seven first-Critic findings correctly filed (B1 Blocker, M1–M4 Major, m1–m2 Minor); both meta-additions correctly Minor.

## Notes

High confidence — every load-bearing claim disk-verified (reuse targets, `WorktreeInfo` fields, `_ROOT_ONLY_TOOLS`/`_root_only_argv`/`_assert_no_encoding_error` oracle, R-22 retirement, INSTALL.md count surfaces, live repo state = clean). verify-(d) TPHD-1: no fresh defect in the reshape (checked the two highest-risk seams — return-shape leakage + `--root` alias — both clean). Calibration observation: the first Critic caught the oracle-integrity flaw in the REUSED test (M2) but didn't re-apply "test the tool on itself" to the NEW tool given the self-referential nature — m-add-1 is that gap. Both meta-additions Minor, reconcilable at TRI-1; neither blocks build.
