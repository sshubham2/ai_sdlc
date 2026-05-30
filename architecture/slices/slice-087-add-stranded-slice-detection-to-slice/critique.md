# Critique: Slice 087 add-stranded-slice-detection-to-slice

**Critic reviewed**: mission-brief.md, design.md, ADR-079
**Date**: 2026-05-30
**Result**: NEEDS-FIXES (Critic verdict; Builder drafts below; final verdict set by user at TRI-1)

> Spawned via `Agent` `subagent_type: "critique"`; per SAOF-1, written ONLY from the agent's actual returned content after the `task-notification`. All load-bearing claims (B1/M1/M3) verified against disk before drafting dispositions.

## Summary

Well-motivated and the read-only/advisory/no-false-positive shape is sound (the `recovery/*` exclusion holds under `^slice/(\d{3})-(.+)$`). But the design substantially overlaps shipped **slice-077 / `pulse_worktree_resolver.py`** (worktree detection + `slice/*` parsing + merge-base ancestry + the `/pulse` surface) without acknowledging it, and ADR-079's inventory fan-out names 2 of the 5 canonical surfaces a new `tools/*.py` must touch. One Blocker, four Majors, two Minors.

## Findings

### Blockers (must address before /build-slice)

#### B1: New tool duplicates `pulse_worktree_resolver` worktree-detection + ancestry; design re-derives porcelain parsing instead of reusing the shipped helper
- **Issue**: `tools/pulse_worktree_resolver.py` (slice-077) ALREADY implements this: `detect_active_worktrees` (L275-345) runs `git worktree list --porcelain`, filters to the SAME `_SLICE_BRANCH_RE` (L73); `classify_worktree_state` (L348-431) runs `git merge-base --is-ancestor <head> <default>` — the identical ancestry test my design proposes. My design re-derives the porcelain idiom from `commit-slice` Step 5b prose → a THIRD copy (branch_workflow_audit + pulse_worktree_resolver + new tool).
- **Evidence**: `tools/pulse_worktree_resolver.py:73,275-345,348-431` (verified on disk).
- **Proposed fix**: REUSE `pulse_worktree_resolver.detect_active_worktrees` for the worktree side; the new tool adds only the genuinely-new **bare-unmerged-`slice/*`-branch-WITHOUT-a-worktree** case (via `for-each-ref refs/heads/slice/` + ancestry) and the `/slice`-open consult. OR document a deliberate independent copy with a why-not. A silent third re-implementation is the blocker.
- **Builder draft**: ACCEPTED-FIXED (design reshape) + ACCEPTED-PENDING (build wiring) — design.md + ADR-079 reshaped to reuse `detect_active_worktrees` + `_resolve_default_branch`; the new tool's scope narrows to the bare-branch case + the `/slice`-open consult. Actual import-reuse is build-time.

### Majors

#### M1: ADR-079 inventory fan-out incomplete — names PMI-1 + INST-1 only, misses `_ROOT_ONLY_TOOLS`, the INSTALL.md count literal, and the shippability propagation (BC-PROJ-9 5-surface)
- **Issue**: A new `tools/*.py` touches FIVE surfaces (witnessed at slice-077's `pulse_worktree_resolver` row): (1) `plugin.yaml`, (2) `install_audit._CANONICAL_TOOLS`, (3) `INSTALL.md` count literal "33 … tools"→34 (L22 + L166), (4) `_ROOT_ONLY_TOOLS` / a cp1252 test, (5) shippability row. ADR-079 named (1)+(2).
- **Evidence**: `test_utf8_stdout_regression.py:96-108` (`_ROOT_ONLY_TOOLS` incl. `pulse_worktree_resolver`); `INSTALL.md:22,166`; verified on disk.
- **Builder draft**: ACCEPTED-FIXED — ADR-079 §Consequences + design Footprint expanded to all 5 surfaces; TF-1 plan gains a tool-inventory-presence row.

#### M2: `_ROOT_ONLY_TOOLS` bucketing is unsound for a `--repo-root` tool — the regression test invokes `--root` (incidental-pass)
- **Issue**: `_root_only_argv` invokes `[-m tool, "--root", REPO]`; my tool exposes `--repo-root`, so it would exit 2 (argparse) and the test "passes" only by tolerating non-`UnicodeEncodeError` failures — UTF8-STDOUT-1 asserted but not exercised. There's a documented gotcha at `test_utf8_stdout_regression.py:143` (slice-072 `slice_queue_claim` got a bespoke test for this).
- **Builder draft**: ACCEPTED-FIXED (design decision) — give the tool a `--root` **alias** for `--repo-root` with default-mode = detection, so the `_ROOT_ONLY_TOOLS` invocation genuinely reaches stdout (chosen over a bespoke test). Stated in design.md.

#### M3: R-26 overlaps the already-retired R-22 (slice-077) without an explicit delta — RR-1 / register coherence
- **Issue**: R-22 (retired by slice-077) = "/pulse mis-reports active-slice state during BRANCH-2 worktree window (built-but-not-merged worktree invisible)". R-26 is the same git-vs-vault divergence viewed from `/slice` open. The genuine residual R-26 closes: the `/slice`-open consult gap + the **bare-unmerged-`slice/*`-branch-without-a-worktree** case (e.g. post-`--merge` cleanup-failure) that `pulse_worktree_resolver` (walks `worktree list` only) does not enumerate.
- **Evidence**: `risk-register.md:378-403` (R-22 retired); verified on disk.
- **Builder draft**: ACCEPTED-FIXED — mission-brief Risk + ADR-079 + the R-26 register-entry plan gain an explicit "Relationship to R-22" clause naming the two residuals.

#### M4: AC#3 (`/pulse` surface) collides with slice-077's existing `/pulse` worktree block + its prose-pin/drift tests; "reuse /slice drift test" for /pulse is a phantom citation
- **Issue**: `/pulse` already carries the slice-077 worktree-awareness block (Step 1-3) pinned by `test_pulse_skill_worktree_awareness.py` (offset/window assertions) + `test_pulse_skill_drift.py`. A new line risks redundancy with the existing `BUILT_BUT_NOT_MERGED` next-action AND perturbing offset-based pins. And the /pulse OSDG-1 guard is `test_pulse_skill_drift.py`, NOT the /slice drift test (phantom citation).
- **Evidence**: `test_pulse_skill_worktree_awareness.py:104-127`; `test_pulse_skill_drift.py` exists separately; verified on disk.
- **Builder draft**: ACCEPTED-FIXED — design corrected (the /pulse drift guard is `test_pulse_skill_drift.py`); the /pulse change narrows to surfacing the **bare-branch** case (genuinely new vs slice-077), placed to not break `test_pulse_skill_worktree_awareness.py` offsets (verify after edit). ACCEPTED-PENDING for the offset-safety verification at build.

### Minors

#### m1: MEPD-1 EXCLUDE rationale should cite the N≥4 lesson + ADR-070, not the shaky slice-086 precedent
- **Builder draft**: ACCEPTED-FIXED — design.md drops the slice-086 citation; cites the N≥4 lesson (082/077/079) + ADR-070 (slice-077 MEPD-1 EXCLUDE tool-shipping, on-point).

#### m2: Exit-code contract should make a single branch's merge-base error per-entry indeterminate, not a whole-run exit 2
- **Issue**: `git merge-base --is-ancestor` returns non-zero-non-1 on error; `pulse_worktree_resolver` handles this as a per-entry `merge-base-error` UNKNOWN (L83/L118), not a whole-run failure — consistent with "advisory, never blocking".
- **Builder draft**: ACCEPTED-FIXED — design adds a per-entry indeterminate state mirroring `pulse_worktree_resolver`'s `merge-base-error`; a single bad branch does not escalate to exit 2.

## Dimensions checked
- [x] Unfounded assumptions — M2 (incidental-pass, executed against the analog), m1.
- [x] Missing edge cases — m2 (merge-base error per-entry); empty case + recovery/* guard hold; bare-branch-without-worktree is the genuinely-new case (B1/M3/M4).
- [x] Over-engineering — B1 (3rd copy where `detect_active_worktrees` exists).
- [x] Under-engineering — M1 (2-of-5 inventory surfaces; no tool-inventory TF-1 row).
- [x] Contract gaps — m2 (per-entry error contract).
- [x] Security — none (read-only; git args not user-tainted; cooperative model).
- [x] Drift from vault — B1 + M3 + M4 (overlap with shipped slice-077 / R-22 / pulse_worktree_resolver not reconciled); self-reference to slice/SKILL.md additive/monotonic, OSDG-1-synced.
- [x] Web-known issues — `git merge-base --is-ancestor` semantics confirmed (0=ancestor/merged, 1=not, other=error → m2); ancestor=merged correct for `--no-ff` BRANCH-2 merges.
- [x] Cross-cutting conformance — M1 (CCC-1 5-surface fan-out), M2 (APED-1 executed), m2 (algorithm-path), M4 (PTFCD-1 phantom /pulse drift citation).

## Meta-Critic additions (critique-review.md — DR-1 EXTEND)

All 7 first-Critic findings confirmed VALID + correctly calibrated (0 suspicious, 0 severity adjustments); reshape verified no fresh defect. 2 Minor missed findings added:

#### m-add-1 (Minor): Self-reference false-positive — the slice's own `slice/NNN` branch flags stranded on a later `/slice` run; untested
- **Builder draft**: ACCEPTED-FIXED — AC4 gains case (e) (pushed-but-unmerged branch = EXPECTED/resumable, not a false positive) + TF-1 row `test_flags_pushed_unmerged_branch_as_resumable`; design.md §Error model documents it.

#### m-add-2 (Minor): `recovery/*` exclusion mechanism undocumented + orphan-branch ahead-count undefined
- **Builder draft**: ACCEPTED-FIXED — design.md §Error model notes the `refs/heads/slice/` ref-glob is load-bearing for the `recovery/*` exclusion, and specifies `ahead: null` for a no-common-ancestor branch (distinct from `indeterminate`).

## Triage

**Triaged by**: user
**Date**: 2026-05-30
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-PENDING | Design reshaped (reuse `pulse_worktree_resolver`; new tool scoped to bare-branch + `/slice` consult); actual import-reuse wiring at build |
| M1 | Major | ACCEPTED-FIXED | ADR + mission-brief enumerate the BC-PROJ-9 5-surface inventory |
| M2 | Major | ACCEPTED-FIXED | `--root` alias (default-mode detection) so `_ROOT_ONLY_TOOLS` genuinely exercises stdout |
| M3 | Major | ACCEPTED-FIXED | Relationship-to-R-22 clause in mission-brief + ADR-079 |
| M4 | Major | ACCEPTED-FIXED | `/pulse` guard corrected to `test_pulse_skill_drift.py`; `/pulse` change narrowed to bare-branch; offset-safety verified at build (PENDING sub-item) |
| m1 | Minor | ACCEPTED-FIXED | MEPD-1 EXCLUDE cites ADR-070 + N≥4 lesson; slice-086 citation dropped |
| m2 | Minor | ACCEPTED-FIXED | Per-branch merge-base error → `indeterminate`, not run failure |
| m-add-1 | Minor | ACCEPTED-FIXED | AC4 case (e) + TF-1 row + design note: pushed-awaiting-PR is EXPECTED-stranded |
| m-add-2 | Minor | ACCEPTED-FIXED | ref-glob load-bearing note + orphan `ahead: null` spec |
