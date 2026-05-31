# Build log: Slice 089 make-commit-slice-stale-branch-check-parallel-slice-aware

**Date**: 2026-05-31
**Result**: SHIPPED

## Events (append-only)

- 2026-05-31 12:5x SETUP: CRP-1 clean; on master (default); discovered PARKED PARALLEL sibling slice-090-fix-pcr-git-subprocess-cp1252-decode (mission-brief+milestone+tests/bugs repro+shippability #95) from a prior session — user-confirmed build slice-089 in isolation.
- 2026-05-31 BUILD: BRANCH-2 dirty-tree path — `git switch -c slice/089-…`, scaffolding-commit (explicit pathspec: slice-089 folder + ADR-081 + slice-queue.md + _index.md ONLY; slice-090 files + shippability.md left on master), worktree add at `…-wt/slice-089-…`.
- 2026-05-31 BUILD: tools/stale_branch_classifier.py written — reuses RAW `_parse_worktree_porcelain` (not `detect_active_worktrees`); all git via local `_run_git` with `encoding="utf-8"` (heeds slice-090 cp1252 class); strips `refs/heads/`→short (B-add-1); path+branch self-exclusion (B1/M-add-1).
- 2026-05-31 SMOKE: `pytest test_stale_branch_parallel_aware.py -k "not prose"` → 11/11 PASS against REAL git worktree fixtures (B2 APED-1 discharged).
- 2026-05-31 BUILD: SKILL.md Step 5b sub-step 1 + Step 5c pre-flight #2 rewritten with byte-identical `<!-- STALE-BRANCH-CHECK -->` block; "Stale-slice-branch check" label preserved; installed copy synced (OSDG-1).
- 2026-05-31 TEST: full test_stale_branch_parallel_aware.py → 13/13 PASS (incl. prose byte-identical parity).
- 2026-05-31 BUILD: plugin.yaml + install_audit.py register stale_branch_classifier (PMI-1/INST-1 → 36 tools); `pip install --force-reinstall` so module resolves from venv site-packages (closes R-29 invisible-tool class).
- 2026-05-31 FINDING: count-bump fan-out (slice-088 lesson) — INSTALL.md L22/L166 `35→36`; cp1252 coverage parametrize list + 2 sibling tool-inventory tests (`stranded_slice_audit`, `pulse_worktree_resolver`) pinned `35`/`l22`/`l166` → bumped to `36`; added `--root` alias to classifier for cp1252 parity harness.
- 2026-05-31 TEST: full suite → 1282 PASS, 0 FAIL.
- 2026-05-31 16:20 PCR-2b MIXED resolved + applied (commit-slice --merge rebase onto slice-090) — see architecture/parallel-conflict-resolution-log.md; code-review NO FINDINGS, TRI-RESOLVE-1 Apply.

## Summary

### Plan executed
- **Worktree setup** (BRANCH-2 dirty-tree): ✅ isolated; slice-090's parallel-sibling files preserved untouched on master.
- **Task 1** `tools/stale_branch_classifier.py`: ✅ — `classify_stale_branches()` + `main()` (exit 0/1/2); `_stdout.reconfigure_stdout_utf8()` first; `encoding="utf-8"` on every git call; reuses only the pure-string `_parse_worktree_porcelain`; `refs/heads/`-strip → short form; path-equality + current-branch self-exclusion; `noncanonical_backed` flagging.
- **Task 2** `tests/methodology/test_stale_branch_parallel_aware.py`: ✅ 13 tests, REAL `git worktree add` fixtures (B2) — incl. short-form (B-add-1), branch-belt-covers-path-miss (M-add-1), boundary cases (m-add-1), CLI 0/2.
- **Task 3** SKILL.md byte-identical block at both guardrail surfaces + OSDG-1 sync + FBCD-1 prose-parity test: ✅.
- **Task 4** PMI-1/INST-1 registration + venv reinstall: ✅ (36/36 tools).

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: `pytest tests/methodology/test_stale_branch_parallel_aware.py -k "not prose and not symmetric"` → 11 passed; live CLI `python -m tools.stale_branch_classifier --repo-root . --json` from the slice/089 worktree → `verdict: allow` (current slice self-excluded, no peers as branches).

### Pre-finish gate
- [x] All ACs pass with evidence — see validation.md (TF-1: 9/9 PASSING)
- [x] Must-not-defer addressed: genuine-stale (worktree-less) refusal preserved (`test_orphan_slice_branch_still_refused`); cross-platform worktree porcelain (reuses `_parse_worktree_porcelain` + `encoding="utf-8"`); observability one-line note (never silent); R-26 coordination (stranded-complete = worktree-less → refuse); no auto-delete/auto-resolve (read-only).
- [x] Drift-check full mode → drift-log.md `**Trigger**: slice-089` marker; DCE-1 clean.
- [x] Mid-slice smoke still passes
- [x] No new TODO/FIXME/debug prints (the `main()` stdout writes ARE the CLI deliverable)
- [x] All Step-6 audits green: PMI-1, INST-1, BCI-1, MCFS-1, AVFS-1, TVFS-1, STP-1, DCE-1, BRANCH-2, BCSG-1, TF-1, NAW-1, UTF8-STDOUT-1, WIRE-1, CRP-1, PCA-1; LINT-MOCK clean.

### BC-1 / BCSG-1 attestations
- **BC-PROJ-3 / BC-GLOBAL-2** (Critical, acked): the new classifier is read-only (no destructive `git checkout/restore/stash` of uncommitted work); the build's `git switch`/`commit`/`worktree add` performed NO revert — slice-090's uncommitted files were explicitly preserved via explicit-pathspec staging.
- **BC-PROJ-4** (Important): every affected gate exercised on the real artifact — classifier run against real `git worktree add` fixtures + live repo; OSDG-1 drift + anchor tests run on the real SKILL.md.
- **BC-PROJ-5** (Important): no identifier rename; the frozen set (existing SKILL.md messages, sibling tools) proven untouched by the green anchor + OSDG-1 + full-suite run.
- **BC-PROJ-11** (Important): SKILL.md edits reference ADR-081/slice-089, never a hard-coded methodology VERSION literal.

### Deferrals
- None.

### Design deviations
- None — built exactly to the post-dual-Critic design.md. (ACCEPTED-PENDING items B2 + M2-parity-test were discharged here: B2 via the real-worktree fixtures; M2 via `test_merge_and_push_stale_check_prose_byte_identical`.)

### Parallel-slice note
- slice-090 (cp1252 git-subprocess fix) remains parked on master (stage=slice). My queued rebase follow-up renumbers to 091 (090 taken). `_index.md` Active now lists both 089 + 090.

### Files changed
- `tools/stale_branch_classifier.py` (new)
- `tests/methodology/test_stale_branch_parallel_aware.py` (new)
- `skills/commit-slice/SKILL.md` (Step 5b sub-step 1 + Step 5c pre-flight #2 rewritten) + installed `~/.claude/skills/commit-slice/SKILL.md` (OSDG-1 sync)
- `plugin.yaml`, `tools/install_audit.py` (register new tool)
- `INSTALL.md` (tool count 35→36, L22 + L166)
- `tests/methodology/test_utf8_stdout_regression.py` (cp1252 coverage list + `--root` alias)
- `tests/methodology/test_stranded_slice_audit_tool_inventory.py`, `tests/methodology/test_pulse_worktree_resolver_tool_inventory.py` (count-pin 35→36)
- `architecture/slices/slice-089-…/{mission-brief,design,critique,critique-review,milestone}.md`, `architecture/decisions/ADR-081-*.md`, `architecture/drift-log.md`, `architecture/slices/_index.md`, `architecture/slice-queue.md`
