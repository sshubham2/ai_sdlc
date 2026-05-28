# Code Review: Slice 074 codify-cp-r-in-branch-2-skill (expanded)

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-28
**Result**: FINDINGS (0B / 1M / 5m; CRSI-1 v1 advisory — does NOT block /validate-slice; all 6 findings DEFERRED to slice-075+ bundled cleanup per voluntary-restraint discipline N=15 cumulative)

## Summary

The slice cleanly codifies R-20 candidate (a) at point 1 and the N=5 switch-commit-switch pattern at point 4, with 7 new tests all passing. The 3 cp-r structural pins (point 1) and the R-20 retirement audit are tight. The switch-commit-switch codefence at point 4 (expansion scope) has **one real semantic defect** (Major): three load-bearing shell variables (`$wt_base`, `$repo_root`, `$default`) are referenced inside point 4's codefence body but are defined ONLY inside point 1's codefence body, which by definition has NOT executed in the dirty-tree branch — a Builder copy-pasting the recipe verbatim hits unbound variables. Two key Minors round it out: the `<scaffolding files>` placeholder is dangerously vague (users will type literal `git add .` or worse), and the cp-r seed at point 4's codefence duplicates point 1's logic, setting up a TPHD-1 sub-mode (a) recurrence trap.

## Changed files (in-scope)

```
skills/build-slice/SKILL.md
architecture/slices/slice-074-codify-cp-r-in-branch-2-skill/build-log.md
tests/methodology/test_build_slice_skill_cp_r_step.py
tests/methodology/test_build_slice_skill_dirty_tree_resolution.py
tests/methodology/test_r_20_retired.py
```

## Findings

### Blockers (advisory in v1)

None. The defect that initially appeared near-blocker (variable-scope failure at point 4) reduces to Major because: (a) the failure mode is loud not silent (bash will emit `cp: ./: not a target directory` on unset `$repo_root`, or worse, evaluate to literal `/diagnose-out`), (b) a competent Builder will notice immediately, and (c) the inherited convention in point 1 informally establishes that the Builder is running inside the same shell session where prior shell-resolution lines were executed.

### Majors

#### M1: Point 4's codefence references `$wt_base`, `$repo_root`, `$default` — all defined only inside point 1's codefence (which the dirty-tree branch did NOT execute)

- **Claim under review**: `skills/build-slice/SKILL.md:80-85`:
  ```bash
  git switch "$default"                           # back to clean default
  git worktree add "$wt_base/slice-NNN-<slice-name>" slice/NNN-<slice-name>   # no -b; branch exists
  cd "$wt_base/slice-NNN-<slice-name>"
  if [ -d "$repo_root/diagnose-out" ]; then cp -r "$repo_root/diagnose-out" ./; fi
  if [ -d "$repo_root/graphify-out" ]; then cp -r "$repo_root/graphify-out" ./; fi
  ```
- **Issue**: `$wt_base` and `$repo_root` are assigned **inside** point 1's codefence at `skills/build-slice/SKILL.md:57-58` (`repo_root="$(git rev-parse --show-toplevel)"; wt_base="$(dirname "$repo_root")/$(basename "$repo_root")-wt"`). `$default` is assigned at L47. The four numbered points are **mutually-exclusive branches** ("If on default branch" / "If the worktree already exists" / "If on any other branch" / "If working tree is dirty"). A Builder entering the point-4 branch did NOT execute point 1's codefence — its variable assignments never ran. The dirty-tree branch's recipe will fail on the first `$wt_base` expansion (unset → empty → `git worktree add  slice/NNN-<slice-name>` → `fatal: missing path`), or on `$repo_root` (cp -r `/diagnose-out` ./ — root-anchored path, wrong source). Per Wiegers + Cockburn (Dim 1): the codified recipe makes implicit assumptions about prior-line execution context that the branching prose contradicts. Per Bach/Hendrickson (Dim 2): the load-bearing case is "Builder hit dirty-tree path on first invocation" — the most common case for the new codification.
- **Evidence**:
  - L47 (point 1's pre-codefence): `default=$(git symbolic-ref refs/remotes/origin/HEAD ...)` (only in the `default` resolution block at L45-51)
  - L57-58 (inside point 1's codefence): `repo_root="$(git rev-parse --show-toplevel)"; wt_base="$(dirname "$repo_root")/$(basename "$repo_root")-wt"`
  - L80-85 (inside point 4's codefence): references `$default`, `$wt_base`, `$repo_root` with no local re-derivation
  - The four numbered points are branches of `if/elif/else` semantics (one fires per invocation), not sequential phases
  - Slice-071 M2/m4 history at L67 explicitly notes the prior code-Critic finding about `wt_base` scope/derivation — this slice introduces a structurally identical scope gap at a sibling branch
- **Proposed fix**: Either (a) extract the variable assignments out of point 1's codefence into a shared pre-amble before the numbered list (e.g., add them to the `default=...` block at L45-51 or right before "1. **If on default branch**" at L55), OR (b) re-derive them at the top of point 4's codefence as the first three lines. Recommend (a) — cleaner (DRY). Add a regression test asserting the variable assignments appear OUTSIDE any numbered point's codefence.
- **Disposition**: **DEFERRED to slice-075+ `slice-NNN-bundle-074-code-critic-cleanup`** per CRSI-1 v1 walking-skeleton advisory-only + voluntary-restraint discipline **N=15 cumulative** (slice-037/046/050/052/055/056/057/061/065/067/070/071/072/073/074). The defect is bounded — empirical evidence is N=0 (no Builder has yet hit slice-074's codified point-4 recipe; slice-074 itself used the manual switch-commit-switch sequence at /build-slice prereq). slice-075 will be the first slice whose Phase A prereq potentially exercises the codified point-4 recipe if the slice ships dirty-on-default — fix-block-at-slice-075-bundle preferred over fix-block-at-slice-074 to maintain per-slice atomic-fix discipline.

### Minors

#### m1: `git add <scaffolding files>` placeholder is dangerously underspecified

- **Claim under review**: `skills/build-slice/SKILL.md:78`: `git add <scaffolding files>                     # explicit staging — no auto-stash`
- **Issue**: The placeholder `<scaffolding files>` is prose-only and ambiguous. A Builder reading the recipe literally has three reasonable interpretations: (a) type the placeholder verbatim (yields `fatal: pathspec '<scaffolding files>' did not match`), (b) substitute `git add .` (stages everything in cwd including any stray `.DS_Store`, editor backups, untracked `__pycache__/`, accidentally-created exploration scripts), or (c) substitute `git add -A` (worse — includes deletions outside cwd too). The mission-brief at L17 enumerates the canonical scaffolding set explicitly (`mission-brief.md + design.md + critique.md + critique-review.md + milestone.md + regenerated slice-queue.md`), so a more concrete pathspec is available.
- **Evidence**: Mission-brief.md L17 enumerates the exact scaffolding set; the recipe placeholder loses this precision
- **Proposed fix**: Replace `git add <scaffolding files>` with `git add architecture/slices/slice-NNN-<slice-name>/ architecture/slice-queue.md` (concrete, matches the actual scaffolding set), OR keep the placeholder but add a one-line prose follow-on. Add a structural-pin test asserting the codefence does NOT contain bare `git add .` or `git add -A`.
- **Disposition**: **DEFERRED to slice-075+ bundle** per voluntary-restraint.

#### m2: Point 4's cp-r seed duplicates point 1's logic — TPHD-1 sub-mode (a) recurrence trap

- **Claim under review**: `skills/build-slice/SKILL.md:84-85` (point 4 codefence tail) is byte-identical to `skills/build-slice/SKILL.md:62-63` (point 1's cp-r seed). The point 4 comment at L83 (`# Then seed gitignored derived dirs per point 1's R-20 step`) explicitly acknowledges the duplication.
- **Issue**: Per Fowler (Dim 3) — DRY violation with a slow-burn cost. If a future slice extends R-20 (e.g., adds `coverage-out/`, or changes cp-r flags, or hardens with `set -e`), the Builder must edit BOTH locations. Slice-073 reflection L29 ("TPHD-1 sub-mode (a) Builder-fix-block-introduces-N+1-regressions pattern extends to N=7 cumulative") is precisely this class — the meta-Critic catches single-surface fixes that miss peripheral copies. The cp-r structural-pin tests (`test_cp_r_lines_use_if_then_guard_for_source_dir_absence`) assert `>=2` matches across the entire `### Branch state` section, so they will pass whether the cp-r appears once or twice — the duplication itself is unguarded.
- **Evidence**: L62-63 ≡ L84-85 byte-for-byte; `test_cp_r_lines_use_if_then_guard_for_source_dir_absence` uses `findall` with `>= 2` assertion
- **Proposed fix**: Tighten the test to assert EXACTLY the number expected (`assert len(matches) == 4` if duplication is intentional). Cheaper than removing the duplication and breaks "self-contained recipe" property.
- **Disposition**: **DEFERRED to slice-075+ bundle** per voluntary-restraint.

#### m3: AC#6 test's no-`-b` regex is comment-position-fragile (re-readable concern, not a real defect)

- **Claim under review**: `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py:156-160` — `point_4_no_dash_b_pattern = re.compile(r'git worktree add\s+(?!(?:[^#\n]*?)-b\s)[^#\n]*slice/NNN-<slice-name>', re.MULTILINE)`
- **Issue**: On re-read the regex IS correct (the `[^#\n]*?` lookahead bound cannot cross `#`, so the comment is safely excluded). But the regex is hard to read; future Builders refactoring it may inadvertently weaken the comment-exclusion.
- **Evidence**: Test passes verifiably; regex is correct under the canonical prose
- **Proposed fix**: Add a docstring example explaining the negative-lookahead's "before `#`" scope, OR strip comments before matching: `code_only = re.sub(r'#[^\n]*', '', codefence); assert re.search(r'git worktree add\s+(?!-b\s)\S+\s+slice/NNN-<slice-name>', code_only)`.
- **Disposition**: **DEFERRED to slice-075+ bundle** per voluntary-restraint.

#### m4: `_branch_state_section` helper duplicated verbatim in two test modules — promote to shared helper

- **Claim under review**:
  - `tests/methodology/test_build_slice_skill_cp_r_step.py:28-41` (function `_branch_state_section`)
  - `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py:35-44` (function `_branch_state_section`)
- **Issue**: The two helpers are byte-equivalent. Per Fowler (Dim 3) — extract method / shared util. If a future slice adjusts the section-extraction regex (e.g., when point 5 is added and the `## [A-Z]` lookahead needs tightening), both copies must update.
- **Evidence**: Both functions have identical regex + identical assertion + similar docstring acknowledging the cross-reference
- **Proposed fix**: Promote to `tests/methodology/_skill_parse_helpers.py` (private leaf module per WIRE-1 exemption pattern), OR to `tests/methodology/conftest.py` as a fixture.
- **Disposition**: **DEFERRED to slice-075+ bundle** per voluntary-restraint.

#### m5: `test_r_20_retired.py` uses `check=True` on subprocess — masks audit-internal errors as `CalledProcessError`

- **Claim under review**: `tests/methodology/test_r_20_retired.py:20-34` — `subprocess.run([...], ..., check=True)` followed by `data = json.loads(proc.stdout)`.
- **Issue**: `check=True` raises `CalledProcessError` on non-zero exit, but doesn't tell the test reader WHY the audit failed. If `tools.risk_register_audit` exits non-zero for a parse error / schema mismatch / renamed flag, the `CalledProcessError` traceback shows only the command, not stderr.
- **Evidence**: L33 `check=True`; L34 immediate `json.loads(proc.stdout)` with no stderr inspection
- **Proposed fix**: Replace `check=True` with explicit returncode assertion that includes stderr in the failure message.
- **Disposition**: **DEFERRED to slice-075+ bundle** per voluntary-restraint.

## Dimensions checked

- [x] **Unfounded assumptions** — M1 (variable-scope assumption at point 4); m3 noted but determined to be a false alarm on re-read
- [x] **Missing edge cases** — M1 (dirty-tree-branch-on-fresh-session is THE load-bearing edge); m1 (Builder copy-pastes the placeholder literally)
- [x] **Over-engineering** — m2 (cp-r seed duplicated at point 4); m4 (`_branch_state_section` helper duplicated)
- [x] **Under-engineering** — None additional. AC#1-#6 all have code; mid-slice smoke gate test all pass (verified 7/7 PASS); R-20 status flip + Retired paragraph land correctly at `architecture/risk-register.md:344-347`
- [x] **Contract gaps** — m1 (placeholder underspecification); m5 (subprocess error surface); test `>=2` assertion permits silent count divergence (m2)
- [x] **Security** — None. The cp -r prose properly quotes `$repo_root/diagnose-out` and `$repo_root/graphify-out`. The `git commit -m "scaffold(slice-NNN): ..."` double-quoted message is shell-safe. No new auth surface, no new input boundary, no command-injection vector
- [x] **Drift from vault** — None. R-20 cp-r N=9 cumulative arithmetic verified against slice-073 reflection L29 (N=8) → slice-074 +1 = N=9 (matches build-log.md). BC-GLOBAL-2 N=6 cumulative verified against slice-073 reflection (N=5 cumulative) → slice-074 +1 = N=6. Switch-commit-switch N=5 cumulative matches design.md enumeration. MEPD-1 EXCLUDE stance honored
- [x] **Web-known issues** — None. `git worktree add <path> <branch-name>` (no -b) is canonical per git-worktree(1). POSIX `if [ -d ... ]; then ...; fi` form is universal (Git for Windows MSYS bash). `git switch -c <branch>` standard since Git 2.23
- [x] **Cross-cutting conformance** — None additional. All 3 test modules' `Path(__file__).resolve().parents[2] / "skills" / "build-slice" / "SKILL.md"` correctly resolves (verified by 7/7 tests passing). Build-log.md matches slice-073's Events + Summary shape. /critique pass-1 vs pass-2 finding IDs consistently disambiguated. APED-1 + RSAD-1 satisfied

## Voluntary-restraint disposition (N=15 cumulative)

All 6 findings (M1 + m1-m5) deferred to slice-075+ `slice-NNN-bundle-074-code-critic-cleanup` per CRSI-1 v1 walking-skeleton advisory-only + voluntary-restraint precedent **N=15 cumulative** (slice-037 / 046 / 050 / 052 / 055 / 056 / 057 / 061 / 065 / 067 / 070 / 071 / 072 / 073 / 074). The class is structurally stable across 15 cycles; bundled-cleanup-at-N+1 disposition shape is the canonical post-CRSI-1-v1 mechanism until v2 ships (TRI-1 + verdict-driven block + AI-bloat passes deferred to slice-062+).

**Slice-075+ candidate**: `slice-NNN-bundle-074-code-critic-cleanup` (6-finding backlog: M1 variable-scope at point 4 + m1 placeholder + m2 duplication + m3 regex docstring + m4 helper extraction + m5 subprocess error surface). All 6 are bounded-scope cleanups; ~1-2 hours estimated.
