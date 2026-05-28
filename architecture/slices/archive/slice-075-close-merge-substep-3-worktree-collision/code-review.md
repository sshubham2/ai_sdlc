# Code Review: Slice 075 close-merge-substep-3-worktree-collision

**code-Critic reviewed**: slice diff vs default branch (skills/commit-slice/SKILL.md + 2 new test modules + shippability row #74 + build-log.md + source-pending-items.txt; in-scope per /code-review skill filter)
**Date**: 2026-05-28
**code-Critic agent**: `~/.claude/agents/code-review.md` (subagent_type: code-review; agent ID a9769bfa6bdb9b715)
**Result**: FINDINGS (0 Blockers / 0 Majors / 2 Minors — both v1-advisory per CRSI-1 walking-skeleton; both DEFERRED to slice-076+ bundle per voluntary-restraint discipline N=16 cumulative)

## Summary

The slice's 3-edit prose surgery at `skills/commit-slice/SKILL.md` Step 5b is technically sound: APED-1 execution against the live `git worktree list --porcelain` confirms the canonical first-worktree AWK extraction returns the main-tree path correctly; byte-level cross-spec parity check on all 3 awk-with-worktree sites in SKILL.md confirms identical `/^worktree /` regex anchors with divergent AWK actions as designed (no `2>/dev/null` drift class from slice-073); TF-1 WRITTEN-FAILING verified via stash-and-rerun — all 4 new tests fail against pre-fix SKILL.md and pass against post-fix; SCMD-1 in-repo↔installed parity holds; sub-step 5's specific-branch awk extraction still works correctly from the post-`cd "$main_tree"` cwd context. The 6 dispositions from the dual-Critic stack (M1+M2+m1+m2+M-add-1+M-add-2) + 2 build-time RSAD-1 defects are all faithfully resolved in code. Two latent test-pinning weaknesses surface that the dual-Critic stack and build-time RSAD-1 sweep did NOT catch (they're in the code-Critic's structural-analysis lane); both Minor.

## Changed files (in-scope)

- skills/commit-slice/SKILL.md
- tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py
- tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py
- architecture/shippability.md
- architecture/slices/slice-075-close-merge-substep-3-worktree-collision/build-log.md
- architecture/slices/slice-075-close-merge-substep-3-worktree-collision/source-pending-items.txt

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None.

### Majors

None.

### Minors

#### m1: `_extract_substep_2_1_block` helper uses unanchored `find("2.1.")` substring — block extraction widens to include the L169 narration paragraph; latent regression vector lets the narration satisfy AC#4's `silent-WT-discard` intent literal

- **Claim under review**: `tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py:82` `two_one_pos = section.find("2.1.")` (and L89's bounded `section.find("2.5.", two_one_pos)`).
- **Issue**: Per APED-1 empirical execution on post-fix SKILL.md, `section.find("2.1.")` returns offset **1131** (the narration paragraph at L169 — "lifted out of pre-flight to new sub-step **2.1.** post-commit guardrail below"), NOT offset **1812** which is the real ordered-list marker `\n2.1. **WT-clean check (post-commit guardrail)**`. The extracted `two_one_block` spans 1764 chars instead of the intended ~1080-char sub-step body — it includes the 681-char narration paragraph + `Then the 5-step merge flow:` line + sub-step 1 + sub-step 2 body + the actual sub-step 2.1. body. Empirical: `block.count("silent-WT-discard") == 2` (one in narration prefix, one in actual sub-step body). If a future refactor removes the silent-WT-discard intent literal from the actual sub-step 2.1. body but leaves the L169 narration paragraph intact, `test_wt_clean_preflight_preserves_silent_wt_discard_protection_intent` would still PASS — the test misses the regression.
- **Class**: RSAD-1 annotation-literal-pollution sub-class N=3 cumulative on this slice (2 caught at build-time smoke FINDING events + this 1 latent post-finish); structurally same class the build resolved for `git status --porcelain` + `git checkout` literals but the resolution didn't generalize to `silent-WT-discard` / the `2.1.` substring anchor itself.
- **Proposed fix** (defer to slice-076+ bundle): anchor extraction on LINE-START list marker, not substring. Two equivalent shapes:
  - `re.search(r'^2\.1\.\s', section, re.MULTILINE).start()` for `two_one_pos` + corresponding for `two_five_pos`
  - Or simpler: `section.find("\n2.1. ") + 1` and `section.find("\n2.5. ", two_one_pos) + 1` (leading newline + trailing space anchors on the list-marker shape)
  - Add explicit `assert block.count("silent-WT-discard") == 1, "narration leakage detected"` post-extraction guard
- **Disposition**: **DEFERRED to slice-076+ `slice-NNN-bundle-075-code-critic-cleanup`** per CRSI-1 v1 walking-skeleton advisory-only + voluntary-restraint precedent **N=16 cumulative** (slice-037/046/050/052/055/056/057/061/065/067/070/071/072/073/074/075).

#### m2: Source-document move (`enable-parallel-slice-pending-items.txt` repo-root → `architecture/slices/slice-075-.../source-pending-items.txt`) NOT propagated to in-vault references — 5 authored stale path references remain in mission-brief.md (L5, L66, L72, L81) + design.md (L6)

- **Claim under review**: build-log.md L92 "Files changed" lists the move; mission-brief.md Notes L94 documented recommendation (a) "move to `architecture/slices/slice-075-.../source-pending-items.txt`".
- **Issue**: Per TPHD-1 sub-mode (a) stale-anchor sweep + Sommerville traceability discipline: the move was executed but the references to the source-document anchor in the slice's own vault surfaces were NOT swept to the new path. Grep `enable-parallel-slice-pending-items.txt` returns:
  - `mission-brief.md:5` "**Risk retired**: P1.2 + P2.4 from `enable-parallel-slice-pending-items.txt`"
  - `mission-brief.md:66` "**The uncommitted source file `enable-parallel-slice-pending-items.txt` at repo root** — disposition deferred"
  - `mission-brief.md:72` "Source-document anchor: `enable-parallel-slice-pending-items.txt`"
  - `mission-brief.md:81` "the source document `enable-parallel-slice-pending-items.txt` uses 'Defect:' for P1.2 + P2.4"
  - `design.md:6` "**Source-document anchor**: `enable-parallel-slice-pending-items.txt` P1.2 + P2.4"
  - Plus 6 generated references in `architecture/slice-queue.md` — OUT-OF-SCOPE (generated artifact; refreshes from upstream input)
  - Plus L95 in mission-brief Notes recommendation — INTENDED historical context (describes pre-decision state)
- **Class**: TPHD-1 sub-mode (a) "file-move-but-anchor-not-swept" sub-class variant (vs the prior "edit-but-mirror-not-swept" class); adds to N=7 cumulative TPHD-1 baseline as a sub-class variant.
- **Proposed fix** (defer to slice-076+ bundle): sweep mission-brief.md L5/L66/L72/L81 + design.md L6 — replace bare `enable-parallel-slice-pending-items.txt` with new path `architecture/slices/slice-075-close-merge-substep-3-worktree-collision/source-pending-items.txt` (or `source-pending-items.txt (this slice's scaffold)` shorthand). Leave mission-brief.md L95 (Notes recommendation describing decision-time state) intact as historical context.
- **Disposition**: **DEFERRED to slice-076+ `slice-NNN-bundle-075-code-critic-cleanup`** per voluntary-restraint precedent.

## Dimensions checked

- [x] **Unfounded assumptions** — none on SKILL.md prose (git-worktree porcelain ordering invariant empirically verified). Narration claim at L169 "preserved at the new post-commit position" is true (intent literal present in actual sub-step 2.1. body per APED-1 count check). One findable narration-vs-code annotation hazard logged as m1.
- [x] **Missing edge cases** — none missed. design.md §Error model enumerates 3 STOP paths (main_tree-resolution-empty + cd-failure + WT-non-empty-post-commit). PSQ-3 re-entry vacuous-on-clean-WT verified by construction. Sub-step 5 awk extraction post-cd-to-main-tree verified empirically — returns slice-075 worktree path correctly. ADR-063 §Decision sub-step ordering preserved.
- [x] **Over-engineering** — none. 3-edit minimal prose surgery; no speculative generality; helper has exactly 2 callers (well-scoped). 2-module test split deliberately mirrors AC#1+#3 / AC#2+#4 grouping.
- [x] **Under-engineering** — none on AC coverage. All 5 ACs map to deterministic structural pins; TF-1 WRITTEN-FAILING empirically verified via stash-and-rerun. 16+ Step 6 audits all CLEAN.
- [x] **Contract gaps** — none. Each test function carries docstring with AC mapping + pre-fix-state + post-fix-expected-PASS. Both helpers documented. SCMD-1 pinned.
- [x] **Security** — N/A — skill-prose surgery only; no new authn/authz/data-exposure paths; no `subprocess.run(shell=True)`; no eval; no hardcoded credentials; `main_tree` resolved from git-controlled trusted path.
- [x] **Drift from vault** — none on ADR claims (ADR-063 sub-step 5+6 ordering preserved; ADR-068 §Re-entry semantics preserved; ADR-020 §3-mode taxonomy unchanged). MEPD-1 EXCLUDE confirmed — PMI-1 v0.72.0 unchanged. **m2 above is technically drift-from-vault** — source-pending-items.txt move created stale anchors in slice's own vault surfaces. Filed Minor because it doesn't block functionality, just degrades audit-trail readability.
- [x] **Web-known issues** — `git worktree list --porcelain` ordering invariant confirmed at /critique web-search; no platform-version restrictions on awk shape (POSIX-compliant; works under Git for Windows' bundled MSYS bash); cd-to-resolved-path is shell builtin not git command, no version drift class.
- [x] **Cross-cutting conformance** — APED-1 executed empirically on:
  1. Canonical AWK extraction against live `git worktree list --porcelain` → returns `C:/Users/sshub/ai_sdlc` (main tree) ✓
  2. Sub-step 5 specific-branch AWK extraction post-`cd "$main_tree"` → returns slice worktree path (ADR-063 ordering preserved) ✓
  3. Byte-level cross-spec parity across all 3 awk-with-worktree fragments in SKILL.md → identical `/^worktree /` regex anchors, divergent AWK actions as designed (slice-073 `2>/dev/null` drift class N=2 cumulative NOT recurring — clean) ✓
  4. TF-1 WRITTEN-FAILING via stash-and-rerun against pre-fix SKILL.md → all 4 new tests fail at expected assertion sites ✓
  5. Post-fix full pytest methodology tests PASS; shippability runner 74/74 PASS; SCMD-1 commit-slice drift PASS ✓
  6. Python 3.12+ SyntaxWarning class check (slice-004 lineage) — `-W error::SyntaxWarning` import of both new test modules → clean ✓
  7. Line-start vs substring anchor analysis on `2.1.` → finds latent narration-leakage m1 above
  
  RSAD-1 (recursive-self-application): slice authors structural-pin tests AND its own pins have latent narration-leakage class (m1) — same class as build-time RSAD-1 findings the slice resolved (annotation literals polluting tests). Resolution targeted 2 specific literals but discipline didn't generalize to `silent-WT-discard` / the `2.1.` substring anchor itself.

Sources cited (APED-1 + web):
- [Git - git-worktree Documentation](https://git-scm.com/docs/git-worktree) — main-worktree-listed-first porcelain ordering invariant
- Empirical: `git worktree list --porcelain | awk '/^worktree / {print $2; exit}'` from this worktree returns `C:/Users/sshub/ai_sdlc` ✓
- Empirical: 4 new tests FAIL pre-fix (stashed SKILL.md) at expected assertion sites, PASS post-fix ✓

## Calibration signals (for /critic-calibrate proposal)

- **RSAD-1 annotation-literal-pollution sub-class N=3 cumulative on this slice** (2 caught at build-time smoke + 1 latent post-finish m1 above) — supports critique-review.md L60's calibration-signal proposal text for `/critic-calibrate` to strengthen agents/critique.md RSAD-1 sub-clause with explicit APED-1-against-pre-fix-prose enforcement language.
- **Cross-spec parity at byte level (slice-073 N=2 class)** — NOT recurring on slice-075; class N=2 stable.
- **TPHD-1 sub-mode (a) source-document-move stale-anchor sweep miss** (m2 above) — adds to N=7 cumulative TPHD-1 baseline as new sub-class variant ("file-move-but-anchor-not-swept" vs prior "edit-but-mirror-not-swept").
- **Voluntary-restraint discipline N=16 cumulative** (slice-037/046/050/052/055/056/057/061/065/067/070/071/072/073/074/**075**) — pattern structurally stable across 16 cycles.
- **3-Critic stack value-validation extends to N=11 cumulative** (slice-063 → slice-075 inclusive) — code-Critic surfaced 2 structural-analysis-lane findings (test-pin latent weakness + file-move stale anchor) NEITHER reachable by the design-Critic stack (which read mission-brief + design.md but doesn't run APED-1 against post-fix prose at substring-vs-line-start anchor granularity).
