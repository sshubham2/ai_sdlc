# Code Review: Slice 079 bundle-074-075-077-078-code-critic-cleanup

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths), base `524e55c`
**Date**: 2026-05-29
**Result**: FINDINGS (0 blockers, 1 major, 4 minors) — advisory in v1 (CRSI-1); 2 addressed in-loop, 1 won't-fix, 2 deferred

## Summary

A clean, well-disciplined bundled-cleanup slice. The four production-code surfaces (build-slice SKILL.md, pulse resolver, PCR resolver, critique agent) are surgically correct: Fix A genuinely closes the variable-scope footgun (APED-1-executed against the real artifact), Fix M/N are byte-correct, Fix P's NamedTuple preserves tuple-equality, Fix H converts a silent `pytest.skip` into real two-path coverage. Full suite green. The one substantive defect — Fix O's central correctness claim (formatter no longer re-derives winner/loser) was structurally pinned but not behaviorally verified (design.md row O unmet) — has been **addressed in-loop** by adding the promised behavioral discriminator test.

## Changed files (in-scope)

```
skills/build-slice/SKILL.md
tools/pulse_worktree_resolver.py
tools/parallel_conflict_resolver.py
agents/critique.md
tests/methodology/_skill_parse_helpers.py
tests/methodology/test_build_slice_skill.py
tests/methodology/test_build_slice_skill_branch_state_preamble.py
tests/methodology/test_build_slice_skill_cp_r_step.py
tests/methodology/test_build_slice_skill_dirty_tree_resolution.py
tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py
tests/methodology/test_r_20_retired.py
tests/methodology/test_pulse_tests_have_no_unused_imports.py
tests/methodology/test_pcr_2a_audit_formatter_signature.py
tests/methodology/test_pcr_2a_parse_queue_missing_field_sentinel.py
tests/methodology/test_pcr_2a_step_5_atomicity_docstring.py
tests/methodology/test_pcr_2a_vault_claim_dispatch_comment.py
tests/methodology/test_skill_parse_helpers.py
tests/methodology/test_slice_queue_writer_utf8_encoding.py
tests/skills/pulse/test_cli.py
tests/skills/pulse/test_classify_worktree_state.py
tests/skills/pulse/test_detect_active_worktrees.py
tests/skills/pulse/test_detect_active_worktrees_bare_repo.py
tests/skills/pulse/test_parse_milestone_stage_bom_tolerance.py
tests/skills/pulse/test_unknown_warn_templates.py
architecture/slices/slice-079-.../build-log.md
```

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None. The production code paths are correct and the full suite + audits are green.

### Majors

#### M1: Fix O's core DRY claim ("formatter no longer re-derives winner/loser") was structurally pinned but never behaviorally verified — design.md test-plan row O unmet

- **Claim under review**: design.md test-plan row O promised `test_winner_loser_passed_not_rederided` — a behavioral test mocking `diag.claim_history` differently than the passed winner/loser and asserting the audit-entry uses the passed values.
- **Issue**: The realized `test_pcr_2a_audit_formatter_signature.py` contained only structural pins (signature param-name check + `(unavailable)`/`pragma` source-grep). A regression re-introducing `_collect_same_candidate_different_identity(diag.claim_history)` inside the formatter body would pass all three — the structural pins cannot discriminate DRY-satisfied from DRY-violated. The headline fix's AC#4 FAIL→PASS obligation was unmet.
- **Evidence**: `grep _format_vault_claim_audit_entry\( tests/` → no behavioral caller existed.
- **Disposition**: **ADDRESSED in-loop.** Added `test_formatter_uses_passed_winner_loser_not_diag_claim_history` — constructs `diag` with empty `claim_history`, passes explicit winner/loser, asserts the rendered entry shows `add-foo`/`alice`/`bob` (passed values) and NOT `(unknown)`/`(unavailable)` (the re-derive-from-empty-history outcome). Genuine discriminator; passes on current code, fails on a re-derive regression. Full suite 1125 pass.

### Minors

#### m1: `_format_vault_claim_audit_entry`'s `diag` parameter is now dead (speculative-generality retention)

- **Issue**: Post-Fix-O the formatter body no longer references `diag`; retained only in the signature + docstring ("retained for call-site uniformity + future use").
- **Disposition**: **WON'T-FIX (documented).** Renaming to `_diag` would break the pinned `test_format_vault_claim_audit_entry_signature_is_6_arg` (`assert "diag" in params`); dropping it would change the 6-arg signature the same test pins (`len(params) == 6`). The docstring already flags the intentional non-use. No linter (ruff `ARG001`) is wired in this repo, so no gate fails. Accepted as documented intentional retention.

#### m2: Fix L returned `tuple()` from a function annotated `-> list[WorktreeInfo]` (annotation/return-type inconsistency)

- **Issue**: Bare-repo branch returned `tuple()` while the other return paths return `list`; the test pinned `result == () or result == tuple()`, coupling the corpus to the tuple type. mypy/pyright would flag the mismatch (no static-type gate wired today, so runtime-harmless — both callers only iterate/`len()`).
- **Disposition**: **ADDRESSED in-loop.** Changed `return tuple()` → `return []` at the bare-repo branch (matches the annotation + the sibling empty-return path) and relaxed the test assertion to `list(result) == []` (container-agnostic). Suite green.

#### m3: Fix B concrete `git add` pathspec is a fixed two-path enumeration that will silently miss any future scaffolding file outside those paths

- **Issue**: `skills/build-slice/SKILL.md` point-4 `git add architecture/slices/slice-NNN-<slice-name>/ architecture/slice-queue.md` is correct for today's `/slice` scaffold set (folder glob captures mission-brief/design/critique/critique-review/milestone + in-folder ADRs; queue captured), but a future `/slice` change writing a scaffolding file elsewhere would be silently omitted before `git commit`.
- **Disposition**: **DEFERRED (latent, low).** Current `/slice` writes only the slice folder + queue (verified); the pathspec is in-scope of present behavior. The proposed hardening (a post-`git add` `git status --porcelain` clean-assert in the recipe) would change executable-contract prose + require OSDG-1 re-sync + a new prose-pin — out of proportion to a latent risk with no current trigger. Routed to a future hardening candidate; noted for /reflect.

#### m4: Fix S fixture-mutation has a fragile fallback that could raise SyntaxError instead of asserting cleanly if site ordering changes

- **Issue**: `test_slice_queue_writer_utf8_encoding.py` mutation `source.replace(', encoding="utf-8"', "", 1)` with a bare-token fallback works today (first site has the `, ` prefix), but an interior-kwarg position under the fallback path could yield unparseable source → test *error* rather than the intended offender-detection.
- **Disposition**: **DEFERRED (latent, low).** The primary (comma-prefixed) branch fires today and the test passes; the fallback is dead on the current source. Hardening (target a known site / guard SyntaxError as skip) is a test-robustness nicety with no active failure. Noted for /reflect.

## Dimensions checked
- [x] Unfounded assumptions — none (BOM literal verified single U+FEFF; `"bare" in blocks[0]` correct dict-key membership; Fix A APED-1-executed against the real post-restructure SKILL.md).
- [x] Missing edge cases — M1 (Fix O behavioral discriminator, now ADDRESSED). Tie/`(unavailable)` branch genuinely unreachable via resolver — `# pragma: no cover` justified.
- [x] Over-engineering — m1 (dead `diag` param, WON'T-FIX/documented).
- [x] Under-engineering — M1 (ADDRESSED). All other fixes have real FAIL→PASS pins; 5/5 ACs test-supported.
- [x] Contract gaps — none. Fix P NamedTuple preserves tuple-equality + positional unpacking; `_append_audit_log` 3-arg surface preserved. m2 (annotation mismatch, ADDRESSED).
- [x] Security — none. No new input boundaries / `shell=True` / credentials; subprocess calls list-form.
- [x] Drift from vault — none. VERSION 0.74.0 unchanged (MEPD-1(b)); zero new ADRs; CAD-1 + OSDG-1 clean; no scope creep.
- [x] Web-known issues — none. Only stdlib-version-sensitive usages (`str.removeprefix` 3.9+, `NamedTuple` class syntax) are safe at the `requires-python = ">=3.10"` floor.
- [x] Cross-cutting conformance — m4 (Fix S fixture fragility, DEFERRED). APED-1 clause-5 self-application satisfied; RSAD-1 / EOL-DRIFT-1 clean; full suite 1125 pass.
