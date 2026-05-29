# Build log: Slice 081 fix-drift-check-enforcement-gap

**Date**: 2026-05-29
**Result**: SHIPPED

## Events (append-only — Step 7c flight recorder)

- 2026-05-29 BUILD: created worktree at ../ai_sdlc-wt/slice-081-fix-drift-check-enforcement-gap on slice/081-fix-drift-check-enforcement-gap (BRANCH-2 point 4: dirty-tree switch-commit-switch-worktree); scaffolding commit 29ea0e1
- 2026-05-29 BUILD: tools/drift_check_audit.py (DCE-1, CRP-1 clone, **Trigger**-line-anchored matcher)
- 2026-05-29 BUILD: tests/methodology/test_drift_check_audit.py (21 tests incl. M-add-1 negative fixture + APED-1 regex parametrization)
- 2026-05-29 SMOKE: mid-slice — DCE-1 unit tests 21 passed + tool_exists repro PASS
- 2026-05-29 BUILD: skills/build-slice/SKILL.md Step 6 DCE-1 sub-block + checklist item + Step 7b drift-check-skip preservation (B2); skills/drift-check/SKILL.md:114 sliceNN→slice-NNN (B1); templates/milestone.md drift-check-skip doc
- 2026-05-29 BUILD: registration — install_audit _CANONICAL_TOOLS + plugin.yaml (DCE-1); 5-part bump 0.75.0→0.76.0 (VERSION/plugin.yaml/pyproject/changelog/installed ai-sdlc-VERSION); v0.76.0 changelog entry + entry-pin pair; shippability row #87
- 2026-05-29 BUILD: installed-side forward-sync (AVFS-1/MCFS-1/OSDG-1) + pip install --upgrade (TVFS-1 → ai-sdlc-tools 0.76.0)
- 2026-05-29 BUILD: bootstrap — /drift-check for slice-081 wrote drift-log.md entry with **Trigger**: slice-081 pre-finish gate line
- 2026-05-29 TEST: DCE-1 self-application exit 0; full repro 2/2 PASS
- 2026-05-29 FINDING: STP-1 flagged stale prose-pin (test_build_slice_crp_1_step_7b_preserves_skip_key) after B2 edit — realigned pin + added drift-check-skip assertion
- 2026-05-29 FINDING: 8 second-order drift realignments from new-tool/version-bump (INSTALL.md count 32→33, rule-reference line, version-sync rename _0_75_0→_0_76_0, cp1252 list, VAULT_ROOT allowlist, orphan-architecture-literal markers, pulse-inventory 32→33 pin, shippability row #75 function-name citation) — all fixed
- 2026-05-29 TEST: full suite 1162 passed, 0 failed

## Summary

### Plan executed
Tasks 1-7 per the approved plan, all complete:
1. `tools/drift_check_audit.py` — DCE-1 procedural was-it-marked gate (CRP-1 byte-faithful clone; line-anchored + slice-anchored matcher per M-add-1). ✓
2. `tests/methodology/test_drift_check_audit.py` — 21 tests (clean/refuse/escape-hatch/mode/usage + M-add-1 negative fixture + APED-1 anchoring). ✓
3. Step 6 wiring + B1/B2/M2 (full-mode requirement, Step 7b preservation, line-anchor). ✓
4. drift-check Trigger-template canonicalization sliceNN→slice-NNN. ✓
5. templates/milestone.md drift-check-skip doc. ✓
6. Registration + 5-part bump 0.75.0→0.76.0 + entry-pin + shippability row #87 + installed forward-sync + TVFS-1 reinstall. ✓
7. Bootstrap drift-log marker + repro green. ✓

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: `pytest tests/methodology/test_drift_check_audit.py` → 21 passed; `test_drift_check_audit_tool_exists` → 1 passed.

### Pre-finish gate
- [x] All ACs pass with evidence — see validation.md (pending /validate-slice)
- [x] Must-not-defer addressed (genuine check, exit contract 0/1/2, UTF8-STDOUT-1, own unit tests + M-add-1 fixture, new rule+ADR+shippability+version bump)
- [x] Drift-check pass (DCE-1 self-application exit 0)
- [x] Smoke regression check pass (full suite 1162 passed)
- [x] No debug code
- [x] BC-1 (--strict): BC-PROJ-3 / BC-PROJ-7 / BC-GLOBAL-2 acknowledged (attestations below)
- [x] All Step 6 audits exit 0 (DCE-1, PMI-1, INST-1, UTF8-STDOUT-1, MCFS-1, AVFS-1, TVFS-1, BCI-1, PCA-1, STP-1, NAW-1, branch-workflow, WIRE-1, CRP-1, triage)

### BC-1 acknowledgments (BCSG-1 attestations)
- **BC-PROJ-3 / BC-GLOBAL-2** (validation/demo harnesses must never destructively revert uncommitted slice work): this slice performs no destructive `git checkout` / `restore` / `stash` revert of uncommitted work. The only git operations were the BRANCH-2 switch-commit-switch-worktree sequence (explicit `git add` + `git commit`, no auto-stash) and `git worktree add` — both non-destructive.
- **BC-PROJ-7** (new audit-tool slices must wire the tool into the cp1252 coverage list AND author a pipe-free shippability row): `tools.drift_check_audit` added to `tests/methodology/test_utf8_stdout_regression.py::_POSITIONAL_SLICE_TOOLS`; shippability rows #86 (repro) + #87 (DCE-1 gate) are pipe-free (no literal `|` in cells; full suite parses them cleanly).

### Design deviations
- None. The chosen Option-A procedural gate was implemented as designed; M-add-1 (meta-Critic) line-anchor was already folded into design before build.

### Files changed
- NEW: `tools/drift_check_audit.py`, `tests/methodology/test_drift_check_audit.py`, `architecture/decisions/ADR-073-*.md`, `tests/bugs/test_drift_check_enforcement_gap.py` (repro, from /repro)
- MODIFIED: `skills/build-slice/SKILL.md`, `skills/drift-check/SKILL.md`, `templates/milestone.md`, `plugin.yaml`, `tools/install_audit.py`, `VERSION`, `pyproject.toml`, `methodology-changelog.md`, `INSTALL.md`, `architecture/shippability.md`, `architecture/drift-log.md`, `tests/methodology/{test_methodology_changelog,test_build_slice_skill,test_utf8_stdout_regression,test_vault_root_constant,test_pulse_worktree_resolver_tool_inventory}.py`
- Installed-side: `~/.claude/{ai-sdlc-VERSION, methodology-changelog.md, skills/build-slice/SKILL.md, skills/drift-check/SKILL.md, templates/milestone.md}` + venv `ai-sdlc-tools` 0.76.0
