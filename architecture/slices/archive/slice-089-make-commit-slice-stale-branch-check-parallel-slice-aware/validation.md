# Validation: Slice 089 make-commit-slice-stale-branch-check-parallel-slice-aware

**Date**: 2026-05-31
**Result**: PASS

## Per-criterion results

### AC1: `--merge` stale-branch guardrail refuses ONLY on worktree-less branches; worktree-backed surfaced as informational note
- **Status**: PASS
- **Evidence**: Live run against a REAL scratch repo with a worktree-backed peer (`slice/101-foo`), a worktree-backed non-canonical branch (`slice/077`), and a worktree-less orphan (`slice/102-orphan`):
  ```
  verdict: refuse; parallel_slices: ["slice/077","slice/101-foo"]; orphan_branches: ["slice/102-orphan"]; noncanonical_backed: ["slice/077"]
  ```
  The worktree-backed peers land in `parallel_slices` (allow-class → SKILL.md surfaces the one-line note), NOT in `orphan_branches`. Unit: `test_worktree_backed_slice_branch_is_allowed`, `test_mixed_backed_and_orphan_refuses_on_the_orphan_only`.
- **Notes**: `slice/077` (non-canonical name, filtered out by `detect_active_worktrees` — the Critic B3 class) is correctly recognized as backed and flagged in `noncanonical_backed` for the rename hint.

### AC2: `--push` stale-branch guardrail applies identical parallel-awareness (symmetric, no divergence)
- **Status**: PASS
- **Evidence**: Both `skills/commit-slice/SKILL.md` guardrail surfaces embed a byte-identical `<!-- STALE-BRANCH-CHECK -->` block invoking the same `python -m tools.stale_branch_classifier`. `test_merge_and_push_guardrails_symmetric` (exactly 2 blocks, both invoke the classifier) + `test_merge_and_push_stale_check_prose_byte_identical` (the two blocks are byte-equal) both PASS. The classifier is position-independent (reads git state, not skill-step context), so the two surfaces are behaviourally identical by construction.

### AC3: A genuinely orphaned `slice/*` branch (no worktree) STILL triggers the existing STOP
- **Status**: PASS
- **Evidence**: Isolated live run — a repo with ONLY a worktree-less `slice/200-stale` branch → `verdict: refuse; orphans=['slice/200-stale']`. Unit: `test_orphan_slice_branch_still_refused`. The genuine-stale protection (the reason the guardrail exists) is preserved; a worktree-removed stranded-complete branch is worktree-less → also refuses (R-26 alignment).

### AC4: An automated test asserts both directions (worktree-backed → allow; worktree-less → refuse)
- **Status**: PASS
- **Evidence**: `tests/methodology/test_stale_branch_parallel_aware.py` — 13 tests on REAL `git worktree add` fixtures, both directions + boundary + CLI contract. `test_mixed_backed_and_orphan_refuses_on_the_orphan_only` (AC4's row) exercises backed + orphan in one repo. Full module: `13 passed`.

### AC5: in-repo `skills/commit-slice/SKILL.md` == installed `~/.claude/...` (OSDG-1, content-equal modulo EOL)
- **Status**: PASS
- **Evidence**: `tests/methodology/test_commit_slice_skill_drift.py` (the OSDG-1 drift test) PASSES after the installed-copy sync; full suite green.

## Multi-instance validation
**Required?**: no (read-only single-process git inspection; no multi-user/device/account flow). The "parallel slice" dimension is itself exercised via the multi-worktree live demo above.
**Result**: not-applicable

## Layered safety checks (VAL-1)
- **Layer A (credentials)**: 0 secrets. **Layer B (dep hallucination)**: 0 findings (`--imports-allowlist tests`). Clean.

## Shippability catalog (regression check)
- **Result**: 93 row(s), 93 PASS, 0 FAIL (`tools.shippability_runner`, exit 0). SCMD-1 + PTFCD-1 pre-catalog gates both clean. No past slice broken by this one.

## Reality surprises
- None for slice-089's own surface. (The pre-existing PARALLEL sibling slice-090 — cp1252 git-subprocess decode bug — was discovered during build setup and its intel was applied: every git call in the new classifier passes `encoding="utf-8"`, so slice-089 does not ship the bug slice-090 exists to fix.)
