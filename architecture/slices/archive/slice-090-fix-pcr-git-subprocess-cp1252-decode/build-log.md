# Build log: Slice 090 fix-pcr-git-subprocess-cp1252-decode

**Date**: 2026-05-31
**Result**: SHIPPED (pre-finish gate PASS; 2 sibling-induced full-suite failures deferred per R-28 — not slice-090 regressions)

## Summary

### Plan executed
1. Added `encoding="utf-8"` to all 9 `text=True` git `subprocess.run` decode sites in `tools/parallel_conflict_resolver.py` (uniform 3-line-block replace_all). DONE.
2. Wrote `tests/methodology/test_parallel_conflict_resolver_git_encoding.py` (2 AST tests); executed against the real module — lands on exactly 9 decode + 4 byte-mode (APED-1). DONE.
3. Added shippability row #96 (AST guard); updated #95 slice-name 089→090. DONE.
4. Risk registration (cp1252 + strict-decode residual + CI-coverage + detector-gap) deferred to /reflect per triage. PENDING (/reflect).

### Mid-slice smoke gate
**Result**: PASS — `pytest tests/bugs/test_pcr_git_subprocess_cp1252_decode.py` → 2 passed.

### Pre-finish gate
- [x] All ACs pass — AC#1 repro 2 passed; AC#2 AST 2 passed; AC#3 PCR no-regression 18 passed.
- [x] Must-not-defer addressed — 9 sites encoded; strict errors (no `errors=`); except fall-throughs preserved; AST-test shippability row added; risk reg deferred to /reflect (designated venue).
- [x] /drift-check full mode + DCE-1 marker — clean.
- [x] Smoke regression — repro still 2 passed.
- [x] No new TODOs/FIXMEs/debug prints — additive kwargs + 2 clean test files.
- [x] All 16 Step-6 audit gates green (BC-1 --strict 3 Criticals ack'd; LINT-MOCK; WIRE-1; TF-1; BRANCH WORKTREE=skip; UTF8-STDOUT-1; CRP-1; PCA-1; BCI-1; MCFS-1; STP-1; AVFS-1; TVFS-1; NAW-1; DCE-1).

### Deferrals
- 2 full-suite failures (commit-slice drift) — SIBLING-INDUCED by in-flight slice-089's installed-but-uncommitted commit-slice SKILL.md edit (R-28); `git diff HEAD` empty for that file. User-approved deferral class; reconcile at slice-089 commit. Zero slice-090 regressions.

### Design deviations
- WORKTREE=skip (user-approved) — built in main tree, not an isolated worktree. Rationale in Events L1.

### Files changed
- `tools/parallel_conflict_resolver.py` (9 `encoding="utf-8"` kwargs added)
- `tests/methodology/test_parallel_conflict_resolver_git_encoding.py` (new — AST guard)
- `tests/bugs/test_pcr_git_subprocess_cp1252_decode.py` (new — behavioral repro, from /repro)
- `architecture/shippability.md` (rows #95, #96)
- vault: mission-brief/design/critique/critique-review/ADR-082/drift-log/milestone

## Events (append-only — written DURING build per Step 7c)

- 2026-05-31 00:00 DEVIATION: WORKTREE=skip — rationale: parallel uncommitted slice-089 + slice-090 scaffolds interleaved in the main tree (plus shared slice-queue.md/_index.md/shippability.md); a worktree cut from HEAD would carry neither scaffold, and selectively committing only slice-090 paths would entangle slice-089's in-flight files. User-approved at the post-critique-review build gate.
- 2026-05-31 00:01 BUILD: confirmed 9 identically-formatted text=True git subprocess.run sites (L626/669/716/790/1511/1526/1595/1940/1983) + 4 byte-mode staging sites (no text=True) to exclude.
- 2026-05-31 00:05 BUILD: added encoding="utf-8" to all 9 decode sites via uniform 3-line-block replace_all; verified count (16 total = 9 new subprocess + 7 pre-existing file-I/O).
- 2026-05-31 00:06 TEST: repro tests/bugs/test_pcr_git_subprocess_cp1252_decode.py — 2 passed (mid-slice smoke PASS).
- 2026-05-31 00:08 TEST: AST guard tests/methodology/test_parallel_conflict_resolver_git_encoding.py — 2 passed (APED-1: executed against real module, lands on exactly 9 decode + 4 byte-mode).
- 2026-05-31 00:10 TEST: PCR no-regression suite (log-hard/log-vault-claim/truncated-baseline/tool-inventory + new) — 18 passed.
- 2026-05-31 00:12 BUILD: BC-PROJ-3 / BC-GLOBAL-2 (Critical): this slice performs NO destructive `git checkout`/`restore`/`stash` revert of uncommitted work (only file edits + tests/audits; commit deferred to /commit-slice).
- 2026-05-31 00:12 BUILD: BC-PROJ-7 (Critical): this slice adds NO new `tools/*.py` module with `main()` — it modifies existing parallel_conflict_resolver.py + adds a test file (no main()). Obligation (1) cp1252-coverage-list wiring N/A (UTF8-STDOUT-1 audit clean 35/35). Obligation (2) pipe-free shippability rows SATISFIED — new rows #95/#96 each have exactly 7 unescaped pipes.
- 2026-05-31 00:14 TEST: Step 6 audits all PASS — TF-1 (6 PASSING), WIRE-1, BRANCH (WORKTREE=skip recognized), UTF8-STDOUT-1 (35/35), PCA-1, BCI-1, STP-1, MCFS-1, AVFS-1, TVFS-1, NAW-1, CRP-1, DCE-1, BC-1 --strict (3 Criticals ack'd), LINT-MOCK.
- 2026-05-31 00:16 TEST: full suite — 1270 passed, 2 FAILED.
- 2026-05-31 00:17 DEFERRAL: the 2 failures (test_commit_slice_skill_drift::test_commit_slice_skill_md_in_repo_byte_equal_installed + test_commit_slice_skill_vault_claim_dispatch::test_in_repo_and_installed_forward_synced) are SIBLING-INDUCED (R-28), NOT a slice-090 regression. Evidence: slice-090's changeset = {parallel_conflict_resolver.py, 2 test files}; `git diff HEAD -- skills/commit-slice/SKILL.md` is EMPTY. The installed ~/.claude/skills/commit-slice/SKILL.md (404 lines) carries the in-flight slice-089's ADR-081 stale-branch-classifier edits (installed-but-uncommitted-to-repo); in-repo committed copy is 390 lines. Per R-28 procedure: documented deferral, NEVER clobber the shared install; reconcile when slice-089 commits its in-repo commit-slice SKILL.md. Zero slice-090 regressions.
