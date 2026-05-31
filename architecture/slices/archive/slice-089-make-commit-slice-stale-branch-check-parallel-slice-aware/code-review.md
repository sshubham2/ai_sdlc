# Code Review: Slice 089 make-commit-slice-stale-branch-check-parallel-slice-aware

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths), worktree-vs-base
**Date**: 2026-05-31
**Result**: FINDINGS (no blockers; minors only)

## Summary
The diff is tight, well-traced to design.md/ADR-081, and pre-satisfies its own audits (INST-1, PMI-1, OSDG-1 commit-slice drift, the new 13-test suite — all green). The single most dangerous defect class for this slice — the meta-Critic B-add-1 raw-vs-short refname set-key mismatch — is correctly fixed in `_short_ref` and is genuinely guarded by an executing regression test. The set algorithm, `encoding="utf-8"` completeness, self-exclusion (both belts), and exit-code contract are all correct. Findings are minor only.

## Changed files (in-scope)
- tools/stale_branch_classifier.py
- tests/methodology/test_stale_branch_parallel_aware.py
- skills/commit-slice/SKILL.md
- plugin.yaml
- tools/install_audit.py
- INSTALL.md
- tests/methodology/test_utf8_stdout_regression.py
- tests/methodology/test_stranded_slice_audit_tool_inventory.py
- tests/methodology/test_pulse_worktree_resolver_tool_inventory.py
- architecture/slices/slice-089-make-commit-slice-stale-branch-check-parallel-slice-aware/build-log.md

## Findings

### Blockers (advisory in v1)

None. All seven attack vectors traced clean:
- **Vector 1 (set algorithm)**: `_short_ref` strips `refs/heads/` from the porcelain RAW branch value; `all_slice_refs` from `--format=%(refname:short)` is already short → both `∩`/`−` operands short-form. Verdict correct when orphan empty + parallel non-empty.
- **Vector 2 (encoding)**: one git helper `_run_git`, passes `encoding="utf-8"`; no bypass; encoding-less `pulse_worktree_resolver._run_git` correctly NOT reused.
- **Vector 3 (self-exclusion)**: path-equality AND branch-belt both fire; `current_branch=None` on detached HEAD guarded everywhere; current branch cannot leak.
- **Vector 4 (exit codes)**: not-a-repo / git-missing → `_GitError` → exit 1; argparse → exit 2; success → 0.
- **Vector 5 (SKILL.md)**: the two `STALE-BRANCH-CHECK` blocks byte-identical modulo EOL; bootstrap-fallback self-excludes the current branch.
- **Vector 6 (tests)**: real `git worktree add` fixtures; `test_worktree_backing_uses_short_form_not_raw_refname` genuinely catches the B-add-1 regression; branch-belt monkeypatch sound.

### Majors

None.

### Minors

#### m1: `noncanonical_backed` never influences `verdict` — confirm it earns its keep
- **Claim under review**: `tools/stale_branch_classifier.py` `_SLICE_BRANCH_RE` + population of `noncanonical_backed`; field never affects `verdict`.
- **Issue**: A field that never affects the verdict is borderline (Fowler speculative generality) — but it is NOT dead: design.md specifies it and SKILL.md consumes it for the rename hint. Deliberate, documented feature.
- **Proposed fix**: none — accept as designed. Logged for calibration completeness.
- **Builder disposition**: ACCEPTED — no change (the SKILL.md rename-hint consumer IS the justification; exercised by `test_noncanonical_named_worktree_backed_branch_allowed_not_orphan`).

#### m2: branch-belt test does not assert a peer survives while self is excluded
- **Claim under review**: `tests/methodology/test_stale_branch_parallel_aware.py` `test_self_exclusion_branch_belt_covers_path_equality_miss` creates only the self worktree (no peer).
- **Issue**: Proves the belt excludes self when path-equality is broken, but not that the belt is *surgical* (excludes only self, not a co-resident peer). The discriminating case (self + peer, path-equality broken) is a stronger oracle (Hendrickson).
- **Proposed fix**: add a peer worktree (`slice/101-foo`) to the monkeypatched test and assert `"slice/101-foo" in v.parallel_slices`. ~2 lines.
- **Builder disposition**: ACCEPTED-FIXED — applied in-slice (cheap, strengthens the oracle).

#### m3: `_norm_path` does not lowercase — case-variant Windows paths won't match by path-equality
- **Claim under review**: `tools/stale_branch_classifier.py` `_norm_path` normalizes `\`→`/` + rstrips one trailing `/`, no case-fold.
- **Issue**: Defensive observation only — both git surfaces emit forward slashes with no trailing separator; a case-variant path would miss path-equality, but the branch-belt covers exactly this (the documented load-bearing self-exclusion).
- **Proposed fix**: none — defense-in-depth (belt) neutralizes this.
- **Builder disposition**: ACCEPTED — no change (belt is the documented load-bearing mechanism; m2's fix further proves the belt is surgical).

## Dimensions checked
- [x] Unfounded assumptions — none (docstrings match impl; imports resolve)
- [x] Missing edge cases — none material (empty, detached HEAD, non-slice worktree, bare repo, CRLF all handled/tested)
- [x] Over-engineering — m1 (`noncanonical_backed`, documented, not bloat)
- [x] Under-engineering — none (all 5 ACs have code+test; survives own Step-6 audits)
- [x] Contract gaps — none (typed public surface; exit 0/1/2 honored; `_GitError` routes all git failures to exit 1)
- [x] Security — none (read-only; no `shell=True`; fixed git arg vector; no secrets; no auth surface)
- [x] Drift from vault — none (code matches design.md + ADR-081; count 35→36 propagated consistently; MEPD-1 EXCLUDE correct)
- [x] Web-known issues — none (only surface is stable git CLI porcelain/plumbing; WebSearch judged not-applicable, not skipped-for-unavailability)
- [x] Cross-cutting conformance — none (RSAD-1 INST-1/PMI-1/OSDG-1 pass; APED-1 new classifier with own 13-test battery; composes correctly by reusing only the raw parser, NOT the filtered `detect_active_worktrees`)
