# Critique: Slice 101 add-gate-audit-cli-exit-code-tests

**Critic reviewed**: mission-brief.md, design.md, project-frame.md (no new ADRs — design mints none)
**Date**: 2026-06-02
**Result**: NEEDS-FIXES

## Summary

The slice's core thesis is sound: in-process `main(argv)` genuinely exercises the `return 1 if violations else 0` regression the slice claims to guard, and every audit's exit site is exactly `sys.exit(main())` over a returning `main()` (verified at all 8 line refs in the design table). The per-audit fixture table is mostly accurate. But the slice's own #1 declared failure mode — the vacuous / wrong-cause pin (AC3) — is **structurally unmet by the chosen `_run_main → int` contract** for at least 3 of the 8 audits, because those audits emit exit 1 for multiple distinct violation kinds and an int-only assertion cannot discriminate the target cause from an incidental one. Separately, two fixture shapes (mock_budget, shippability_path) are under-specified and will silently fail to trigger their target violation unless built to the audits' exact parse shapes, and the branch_workflow row-8 fixture has a real machine-portability hazard (default-branch resolution) that the Critic reproduced.

## Findings

### Blockers (must address before /build-slice)

None. The design is buildable; the issues below are all fixable within this slice without redesign.

### Majors (address this slice)

#### M1: `_run_main → int` contract cannot discriminate the STOP cause for PMI-1, TRI-1, and DR-1 — directly defeats AC3
- **Claim under review**: design.md AC3 / Non-vacuity plan ("pin the STOP cause, not just the STOP"); "What's new": `_run_main(module_main, argv) -> int` returns the int.
- **Issue**: The Critic executed three audits and confirmed they return exit 1 for the TARGET kind AND for incidental kinds, indistinguishably at the int level:
  - **TRI-1** (`triage_audit.py:216-222` vs `:243-254`): a missing FILE emits `no-section` exit 1, and a present-file-with-no-triage-heading ALSO emits `no-section` exit 1. A typo'd fixture path passes the block-path test for the wrong reason. Reproduced: both a sectionless file and a non-existent file returned `EXIT=1 (no-section)`.
  - **PMI-1** (`plugin_manifest_audit.py:290-305`): an orphan-skill fixture returned `EXIT=1` but the violations were `missing-field` (name, description) PLUS `orphan-skill` — a malformed plugin.yaml alone would also exit 1.
  - **DR-1** (`critique_review_audit.py:288`): missing-section and missing-field both exit 1; an empty file yields both.
  An int-only assertion pins "something refused," not "the target gate fired" — exactly the vacuous/wrong-cause pin named as the #1 failure mode for pin-test slices here (slice-085 "Pin the STOP cause").
- **Evidence**: `tools/triage_audit.py:216-222,243-254`; `tools/plugin_manifest_audit.py:290-305`; `tools/critique_review_audit.py:288`; reproduced via direct CLI runs.
- **Proposed fix**: (a) the test asserts on the int AND separately calls the audit's `audit()`/`run_audit()`/`audit_*` function on the SAME fixture, asserting the target `kind` is present in `result.violations` (pins both exit code AND cause) — strongly preferred; or (b) construct each fixture so the TARGET kind is the ONLY possible non-zero source. Record the discrimination mechanism per audit.
- **Builder draft**: ACCEPTED-FIXED at design.md "What's new" + per-audit table (new **Cause-discrimination** column) + Non-vacuity plan. Adopted option (a): every block-path test pairs the `_run_main(...) == block_code` assertion with a `target_kind in {v.kind for v in audit_fn(fixture).violations}` assertion on the same fixture. The int-assert pins the exit wiring; the kind-assert pins the cause. Applied this round.

#### M2: branch_workflow row-8 fixture is machine-portability-fragile — default-branch resolution can flip to exit 2 (`default-branch-unresolvable`) or a wrong-cause exit-1 (`slice-branch-mismatch`)
- **Claim under review**: design.md row 8 fixture "tmp git repo with HEAD on the default branch … pin both [1 and 2]".
- **Issue**: `_resolve_default_branch` (`branch_workflow_audit.py:168-187`) tries `git symbolic-ref refs/remotes/origin/HEAD` (no origin in tmp → fails) then `git config init.defaultBranch`; unset everywhere → `None` → `default-branch-unresolvable` (`:534-546`) → exit 2, NOT the target exit-1 `on-default-branch`. If the tmp repo's init branch (`_current_branch`, `:190-196`) differs from the resolved default (init→`main` but config says `master`), `current != default` and doesn't start with `slice/` → `slice-branch-mismatch` (`:660-672`, exit 1) — wrong-cause exit 1. Passes on THIS machine only because system gitconfig carries `init.defaultBranch=master` and `git init` also yields `master` — coincidence not holding on CI/contributors (modern Git defaults `main`; CI often unset).
- **Evidence**: Reproduced — `git config --show-origin --get-all init.defaultBranch` → `file:C:/Program Files/Git/etc/gitconfig master`; `--global` unset. `tools/branch_workflow_audit.py:168-187,190-196,531-547,660-672,708-714`. (slice-091 "execute repros against the REAL runtime".)
- **Proposed fix**: make the fixture self-contained/deterministic regardless of ambient config: after `git init`, set repo-LOCAL `git config init.defaultBranch <name>` AND `git branch -M <name>` so `_current_branch == _resolve_default_branch` is guaranteed → `on-default-branch` exit 1. For the exit-2 case use a non-`slice-NNN-` folder name → `usage-error` → exit 2 (deterministic), NOT `default-branch-unresolvable` (env-dependent).
- **Builder draft**: ACCEPTED-FIXED at design.md row 8 + a new "branch_workflow fixture recipe" note. Adopted the `git branch -M trunk` + local `init.defaultBranch trunk` self-contained recipe for the exit-1 case, and folder-name `usage-error` for the exit-2 case. Applied this round.

#### M3: mock_budget and shippability_path violating fixtures are under-specified — naive shapes scan/count zero and yield exit 0
- **Claim under review**: design.md rows 3 and 7; header asserts the table is "build-ready".
- **Issue**: Both more shape-sensitive than the prose implies; both reproduced failing:
  - **mock_budget** (`mock_budget_lint.py:765-783`): two bare `MagicMock()`/`patch(...)` expressions did NOT trip the >1-mock count — `EXIT=0` even with `--strict`. The counting heuristic keys on the stacked `@patch("…")` decorator form used by `tests/methodology/fixtures/mock_budget_too_many.py`.
  - **shippability_path**: a 3-column markdown table scanned 0 rows → `EXIT=0`. The parser requires the SCMD-1 6-column shape with the test-path token in the `Machine-cmd` column (col 6), per `tests/methodology/test_ptffd1_shippability_path_audit.py:16-30`.
- **Evidence**: Reproduced — inline 2-`MagicMock` fn → `EXIT=0`; 3-column phantom catalog → `EXIT=0 "0 row(s)"`. Known-good: `tests/methodology/fixtures/mock_budget_too_many.py:9-11`, `tests/methodology/test_ptffd1_shippability_path_audit.py:16-30`.
- **Proposed fix**: design row 3 → "reuse the stacked-`@patch` shape from `fixtures/mock_budget_too_many.py`"; row 7 → "build a 6-column SCMD-1 catalog (`| # | Slice | Critical path | Command | Runtime | Machine-cmd |`) with a `pytest tests/methodology/test_DOESNOTEXIST.py` token in Machine-cmd, mirroring `test_ptffd1_shippability_path_audit.py::_catalog`."
- **Builder draft**: ACCEPTED-FIXED at design.md rows 3 & 7. Updated both fixture cells to reference the known-good shapes (and aligned with "What's reused" which already said reuse existing fixture shapes). Applied this round.

### Minors (log; address if cheap)

#### m1: AC2 mutation plan does not specify discrimination by kind — mutation proves int-dependence, not cause-pinning
- **Issue**: If M1 weren't addressed, the `return 0` mutation makes even a wrong-cause test fail (any exit-1→0 fails `== 1`), so the mutation would report "non-vacuous" while still pinning the wrong cause. Mutation proves int-dependence; it does not prove cause.
- **Proposed fix**: With M1's kind-assertion added, mutation covers cause too. State in build-log that mutation proves int-dependence and the kind-assertion proves cause-pinning.
- **Builder draft**: ACCEPTED-FIXED at design.md Non-vacuity plan — added the explicit "mutation proves int-dependence; the paired kind-assertion proves cause-pinning; record both in build-log" clarification. Applied this round.

#### m2: TRI-1/WIRE-1/DR-1 `--no-carry-over` is defensive but redundant for bare-tmp-dir fixtures
- **Issue**: `_slice_is_carry_over` (`wiring_matrix_audit.py:80-86` and TRI-1/DR-1 equivalents) returns `False` when no `mission-brief.md` exists in the fixture's parent — so a bare tmp-dir fixture never triggers carry-over regardless of the flag. Keep the flag (future-proofs a fixture that includes a stale-mtime mission-brief); just don't rely on it as the thing that makes the fixture work. Not a defect.
- **Proposed fix**: Optionally note in the design table.
- **Builder draft**: ACCEPTED-FIXED at design.md rows 2/4/5 nuance — added the one-line clarification that carry-over wouldn't fire on a mission-brief-less fixture anyway (flag retained as defensive). Applied this round.

#### m3: design table row-8 says "BRANCH-1" while the live family is BRANCH-2/BRANCH-3
- **Issue**: The audit module self-IDs as "BRANCH-1 audit" (`branch_workflow_audit.py:679`), so citing BRANCH-1 is defensible as the audit's own rule; the live methodology family is BRANCH-2/BRANCH-3 per CLAUDE.md. Labeling nicety, no behavioral impact.
- **Proposed fix**: Optional footnote.
- **Builder draft**: ACCEPTED-FIXED at design.md row 8 — footnoted "BRANCH-1 = the audit's historical self-ID (`branch_workflow_audit.py:679`); the live family is BRANCH-2/BRANCH-3." Applied this round.

## Dimensions checked
- [x] Unfounded assumptions — M3 (fixture-shape assumptions contradicted by executing the real tools); all 8 `main()`-returns-int line refs verified accurate.
- [x] Missing edge cases — M2 (default-branch resolution under unset/`main`-vs-`master` config — reproduced); M1 (multi-kind exit-1 ambiguity). Concurrency/network N/A (test-only, in-process).
- [x] Over-engineering — none. Consolidated single-module + tiny `_run_main` helper are minimal; "no subprocess" correctly justified against the exact regression.
- [x] Under-engineering — M1 (AC3 "pin the cause" had no design element delivering it given the int-only helper); M3 (AC1 rows 3/7 lacked a working fixture shape).
- [x] Contract gaps — none new. Slice pins an existing implicit contract; exit-2 paths correctly identified.
- [x] Security — none. Test-only; tmp fixtures only.
- [x] Drift from vault — none. Standard mode (no Heavy component files). AC4 parallel-safety with slice-100 verified disjoint (filenames + edited files both disjoint). project-frame trajectory not contradicted.
- [x] Web-known issues — skipped (pure stdlib pytest + in-process calls + local git; the one runtime-divergence risk covered empirically under M2).
- [x] Cross-cutting conformance — APED-1: executed every audit's real exit-code path (commands+outputs quoted), surfacing M2/M3 that static reading would miss. No phantom test-file citation (the slice creates `test_gate_audit_cli_exit_codes.py`; reused fixture builders all exist on disk).

## Builder draft summary

Net: 0 blockers, 3 majors, 3 minors — **all six ACCEPTED-FIXED this round** (design-spec corrections applied to design.md before triage). No overrides, no escalations, no deferrals. The design's central architectural bet (in-process `main(argv)` int-assertion) survives; the fixes make each fixture cause-pinned (M1, m1), machine-deterministic (M2), and constructible (M3). Projected post-triage verdict: **CLEAN**.

## Triage

**Triaged by**: user
**Date**: 2026-06-02
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | design.md "What's new" + per-audit target_kind table + Non-vacuity plan — paired int-assert with kind-assert |
| M2 | Major | ACCEPTED-FIXED | design.md row 8 + branch_workflow fixture recipe — deterministic `branch -M trunk` + local init.defaultBranch; exit-2 via usage-error folder name |
| M3 | Major | ACCEPTED-FIXED | design.md rows 3 & 7 — reference known-good `@patch`-stacked + 6-column SCMD-1 fixture shapes |
| m1 | Minor | ACCEPTED-FIXED | design.md Non-vacuity plan — two-guarantees distinction (mutation=int-dependence; kind-assert=cause) |
| m2 | Minor | ACCEPTED-FIXED | design.md rows 2/4/5 nuance — carry-over won't fire on mission-brief-less fixture; flag kept as defensive |
| m3 | Minor | ACCEPTED-FIXED | design.md row 8 footnote — BRANCH-1 = audit self-ID; live family BRANCH-2/3 |
| M-add-1 | Major | ACCEPTED-FIXED | meta-Critic missed-finding (reconciled at TRI-1): design.md row 6 — single-dash heading + `broken-ref`; corrected the non-existent `parity-mismatch` kind literal in the M1 table to `broken-ref` |
