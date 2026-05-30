# Slice 087: add-stranded-slice-detection-to-slice

**Mode**: Standard
**Estimated work**: 0.5–1 day
**Risk retired**: new **R-26** — stranded/uncommitted completed-slice work is invisible to the pipeline's vault-based active-slice detection at `/slice` open (witnessed firsthand this session at slice-086). **Relationship to R-22 (retired, slice-077)**: R-22 covered `/pulse` mis-reporting the BRANCH-2 *worktree* window and was retired by `pulse_worktree_resolver.py`. R-26 is the residual R-22 did NOT close: (i) `/slice` never consults git state at open, and (ii) the **bare unmerged `slice/*` branch WITHOUT a live worktree** (e.g. a post-`--merge` cleanup-failure / committed-but-unmerged branch) — `pulse_worktree_resolver` walks `git worktree list` only, never `for-each-ref refs/heads/slice/`.
**Test-first**: true  (structural-pin + behavioral tests, WRITTEN-FAILING first — the project's methodology-surface convention; no `tests/bugs/*` repro applies)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The pipeline decides "what slice is active" purely from the **vault** (`slices/_index.md` Active table + `milestone.stage`). When a session builds a slice to completion but dies before `/commit-slice`, the vault marks it shipped/archived while git still holds an **unmerged `slice/NNN-*` branch + a live worktree** — a divergence invisible to every vault-based check. This bit us live this session: a prior session completed + archived slice-086 but never committed it; a new `/slice` happily redefined slice-086 from scratch and only collided deep inside `/build-slice`'s BRANCH-2 worktree setup. This slice adds a **git-state detector** that `/slice` consults at open (and `/pulse` surfaces) so a new slice is never defined on top of stranded prior work — the operator is shown the stranded slice and offered Resume / Continue-build / Proceed-anyway.

## Acceptance criteria

1. New tool `tools/stranded_slice_audit.py` (read-only) reports stranded prior slice work, **reusing** `pulse_worktree_resolver.detect_active_worktrees` + `_resolve_default_branch` rather than re-deriving porcelain/ancestry parsing (B1). Its genuinely-new detection over slice-077 is the **bare unmerged `slice/*` branch WITHOUT a live worktree** (via `git for-each-ref refs/heads/slice/` + `git merge-base --is-ancestor <branch> <default>`, ancestor⇒merged, + ahead-count). Output unions worktree-stranded (from the reused helper) and bare-branch-stranded entries: each carries branch, worktree path (or "—"), ahead-count, clean/dirty, and a per-entry `indeterminate` flag for merge-base errors (m2). Exit 0 + `status: clean` when none; exit 0 + `status: stranded` + list when found (advisory, NOT a refuse; NO exit 1). Exit 2 only on usage failure. `--json` + human; accepts both `--repo-root` and a `--root` alias (so the `_ROOT_ONLY_TOOLS` cp1252 regression genuinely exercises stdout, M2); UTF8-STDOUT-1 compliant.
2. `/slice` Prerequisite check invokes the detector BEFORE Step 1 candidate-gathering; when stranded work is found it HALTs with an `AskUserQuestion` structured-options gate (Resume via `/commit-slice` / continue that slice's `/build-slice` / proceed defining a new slice anyway), never silently proceeding. The proceed-anyway path is always available (advisory, not blocking).
3. `/pulse` surfaces the **bare-unmerged-branch-without-worktree** signal in its macro-state summary (the case slice-077's existing `/pulse` worktree block does NOT cover) — placed so it does NOT perturb `test_pulse_skill_worktree_awareness.py`'s offset/window pins (verify after edit), and guarded by the EXISTING `test_pulse_skill_drift.py` (M4 — not the `/slice` drift test).
4. A behavioral test asserts the detector: (a) flags an unmerged `slice/*` branch, (b) flags a `slice/*` worktree, (c) is clean on a repo with neither, (d) does NOT flag `recovery/*` or merged `slice/*` branches, **(e) flags a pushed-but-unmerged `slice/*` branch as stranded — an EXPECTED classification (resumable), NOT a false positive (m-add-1, the slice's own primary in-flight case)**; and `skills/slice/SKILL.md` + `skills/pulse/SKILL.md` are OSDG-1 content-equal to their installed copies (drift tests).
5. R-26 registered in `architecture/risk-register.md` (mitigating once the detector ships, with the Relationship-to-R-22 clause); the new tool propagated across the full **BC-PROJ-9 5-surface inventory** (`plugin.yaml` + `install_audit._CANONICAL_TOOLS` + `INSTALL.md` count 33→34 at L22+L166 + `_ROOT_ONLY_TOOLS` + shippability row) — independent of any VERSION bump (M1); full pytest + all Step-6 audits pass.

## Test-first plan

(per **TF-1**) Each AC maps to tests written WRITTEN-FAILING before implementation. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish`.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | behavioral | tests/methodology/test_stranded_slice_audit.py | test_flags_unmerged_slice_branch | PENDING |
| 1 | behavioral | tests/methodology/test_stranded_slice_audit.py | test_flags_slice_worktree | PENDING |
| 1 | behavioral | tests/methodology/test_stranded_slice_audit.py | test_clean_when_none | PENDING |
| 4 | behavioral | tests/methodology/test_stranded_slice_audit.py | test_ignores_recovery_and_merged_branches | PENDING |
| 4 | behavioral | tests/methodology/test_stranded_slice_audit.py | test_flags_pushed_unmerged_branch_as_resumable | PENDING |
| 2 | structural-pin | tests/methodology/test_slice_skill_stranded_prereq.py | test_slice_skill_has_stranded_detection_prereq | PENDING |
| 3 | structural-pin | tests/methodology/test_pulse_skill_stranded_signal.py | test_pulse_skill_surfaces_stranded_signal | PENDING |
| 4 | drift (OSDG-1) | tests/methodology/test_slice_skill_drift.py | test_in_repo_and_installed_slice_skill_md_are_content_equal | PENDING |
| 4 | drift (OSDG-1) | tests/methodology/test_pulse_skill_drift.py | test_in_repo_and_installed_pulse_skill_md_are_content_equal | PENDING |
| 5 | inventory-pin | tests/methodology/test_stranded_slice_audit_tool_inventory.py | test_stranded_slice_audit_in_canonical_inventory | PENDING |

> Notes: the `/slice` + `/pulse` OSDG-1 drift tests (`test_slice_skill_drift.py`, `test_pulse_skill_drift.py`) ALREADY exist — reuse, do not duplicate (M4: `/pulse`'s guard is `test_pulse_skill_drift.py`, NOT the `/slice` drift test). AC#5's inventory-pin (M1) mirrors slice-077's `test_pulse_worktree_resolver_tool_inventory.py`. After the `/pulse` edit, re-run `test_pulse_skill_worktree_awareness.py` to confirm slice-077's offset/window pins still pass (M4).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Detector reports stranded slice work | `tests/methodology/test_stranded_slice_audit.py` (4 cases) PASS; manual run against a fixture repo with an unmerged `slice/*` branch + worktree |
| 2 | `/slice` halts with options on stranded work | Structural-pin test asserts the prerequisite-block prose + `AskUserQuestion` gate; manual `/slice` dry-run with a planted stranded branch |
| 3 | `/pulse` surfaces the signal | Structural-pin test on `pulse/SKILL.md`; manual `/pulse` shows the stranded line |
| 4 | OSDG-1 + no-false-positive | drift tests green; `test_ignores_recovery_and_merged_branches` green |
| 5 | No regression; risk + catalog | Full `pytest` green; `/validate-slice`; R-26 in register; shippability row added |

## Must-not-defer

- [ ] **No false positives**: `recovery/*` branches, merged `slice/*` branches, and the main worktree MUST NOT be flagged — a noisy detector that cries wolf will be ignored (it would have flagged this session's own recovery branches).
- [ ] **Advisory, never blocking**: the proceed-anyway path is ALWAYS offered — the detector informs, it does not refuse. (An operator must be able to define a parallel slice deliberately.)
- [ ] **Default-branch resolution**: reuse the canonical 2-step resolution (`git symbolic-ref refs/remotes/origin/HEAD` → `git config init.defaultBranch` → STOP), not a hard-coded `master`/`main` (BRANCH-1/NAW-1 portability pin).
- [ ] **Fail-visible, not fail-silent**: if git is unavailable / default unresolvable, the detector exits non-zero with a clear stderr message; `/slice` surfaces it rather than silently skipping (the R-7 silent-disable class).
- [ ] **Reuse, don't re-implement (B1)**: import `pulse_worktree_resolver.detect_active_worktrees` + `_resolve_default_branch` for the worktree + default-resolution sides; do NOT create a 3rd copy of worktree-porcelain/ancestry parsing.
- [ ] **5-surface inventory (M1)**: a new `tools/*.py` propagates across all five BC-PROJ-9 surfaces (plugin.yaml, install_audit, INSTALL.md count ×2, _ROOT_ONLY_TOOLS, shippability) — even though no VERSION bump.
- [ ] **CAD-1/OSDG-1 untouched elsewhere**: edits limited to `skills/slice/SKILL.md`, `skills/pulse/SKILL.md`, and the new tool/tests; forward-sync installed copies (atomic at end-of-build).

## Out of scope

- Auto-resuming or auto-committing the stranded slice (the detector only *surfaces* it; resumption is the operator's explicit choice via `/commit-slice` or `/build-slice`).
- Detecting stranded work in *other* repos or remote branches (local `slice/*` + local worktrees only).
- Reworking BRANCH-2 worktree mechanics or `/commit-slice` recovery flows.
- A hard Step-6 gate refusing on stranded work (this is an open-time advisory; a blocking variant is a separate future slice if warranted).

## Dependencies

- Prior slices: [[slice-086-harden-agent-spawn-skills-await-real-output]] (the session whose stranded state motivated this), BRANCH-2 worktree workflow ([[decisions/ADR-063]]), `tools/branch_workflow_audit.py` (existing `stale-slice-branch` warning class to extend), `tools/new_agent_warning_audit.py` (git-subprocess + default-resolution precedent to model the new tool on).
- Vault refs: `skills/slice/SKILL.md` Prerequisite check, `skills/pulse/SKILL.md`, CLAUDE.md OSDG-1.
- Risk register: new R-26 (registered during this slice).

## Mid-slice smoke gate

After writing `tools/stranded_slice_audit.py` + its behavioral test (before the SKILL.md edits): create a throwaway fixture repo (or use a temp branch) with an unmerged `slice/999-smoke` branch and run:
```
$PY -m pytest tests/methodology/test_stranded_slice_audit.py -q
$PY -m tools.stranded_slice_audit --repo-root <fixture> --json
```
Expected: tests PASS and the JSON lists the planted stranded branch with correct ahead-count + clean/dirty. If it false-flags a `recovery/*` or merged branch: STOP, fix the detector before wiring `/slice`.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (esp. no-false-positives + advisory-not-blocking)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
