# Validation: Slice 030A repair-build-checks-vault

**Date**: 2026-05-16
**Result**: PASS (with user-approved shippability deferral)

All 5 slice ACs PASS with real-command evidence + VAL-1 clean + PTFCD-1 clean. Shippability catalog 25/29: #1/#19 = spurious Windows CRLF/LF raw-byte-comparison artifact (content byte-identical, slice-030A verifiably innocent, NOT a real drift); #28/#29 = catalog-runner prose-cell mis-parse artifacts (real pytest commands green in the 573-pass suite). **User-approved deferral at the PCA-1 validate gate (AskUserQuestion, 2026-05-16): "Approve deferral → /reflect (recommended)"** — rationale: not-slice-caused, not a real drift; the underlying drift-test CRLF/LF fragility is a separate latent bug captured as a /reflect Discovered item + standalone future-slice candidate (out of slice-030A scope per CLAUDE.md "refactors need a slice"). Aggregate = PASS; /reflect proceeds.

## Per-criterion results

### AC1: reconstruct both build-checks.md from tracked fixtures; BFRD-1 closure (17→0); 4 schema-substring pins
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_build_checks_audit.py` → **39 passed, 0 failed** (baseline `17 failed, 21 passed`). `_parse_rules` on live `architecture/build-checks.md` → `['BC-PROJ-1','BC-PROJ-2','BC-PROJ-3']`; live `~/.claude/build-checks.md` → `['BC-GLOBAL-1','BC-GLOBAL-2']`. Schema-pin tests (Trigger anchors / word-boundary / Negative anchors / final filter) green against the fixtures.

### AC2: all-5-rule literal-constant tracked oracle (incl. NEW BC-PROJ-3/BC-GLOBAL-2 pins)
- **Status**: PASS
- **Evidence**: `pytest …::test_migrated_rules_have_expected_anchors ::test_migrated_rules_have_expected_negative_anchors ::test_bc_proj_3_and_bc_global_2_have_expected_structural_identity ::test_bc_proj_2_has_methodology_vocabulary_negative_anchors` → **4 passed**. The repointed tuple tests assert the fixture against retained literal constants + new applies_to/trigger_keywords/severity pins; the new test pins the two survivor rules' full structural identity (closes v2-B3/meta-M-add-3).

### AC3: deterministic BCI-1 full-structural-identity gate + semantics + non-opt-out wiring
- **Status**: PASS
- **Evidence**: `$PY -m tools.build_checks_integrity` exit 0 (conformant — slice-030A bootstrap self-application discharge). Wiring grep: `build_checks_integrity`/`BCI-1` ×6 in `skills/build-slice/SKILL.md` (pre-finish checklist + audit subsection), ×2 in `skills/reflect/SKILL.md` (Step 5b fail-loud post-write). Semantics (full identity / absent-WARN / empty-HALT) covered by AC4.

### AC4: regression test exercises the tool
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_build_checks_integrity.py` → **7 passed** — conformant-PASS; 1-rule-truncation-HALT; single-corrupted-`applies_to`-HALT + single-corrupted-`severity`-HALT (proves meta-M-add-2 FULL identity, NOT rule-ID-set-only); absent-global-WARN/exit0; empty-present-global-HALT/exit1 (meta-M3 empty≠absent); main() exit-code + attributed message.

### AC5: new-tool propagation correct + self-clean (meta-M2 file-locations)
- **Status**: PASS
- **Evidence**: PMI-1 clean (24 skills, 5 agents, **21 tools**, version 0.44.0); INST-1 clean (24/24, 5/5, 4/4, **21/21 tool modules**, methodology v0.44.0); `test_v_0_44_0_bci_1_entry_present_in_repo_and_installed` + `test_utf8_stdout_regression.py` → 26 passed; VERSION/ai-sdlc-VERSION/plugin.yaml.version all 0.44.0 lockstep; methodology-changelog v0.44.0 in-repo + installed forward-synced.

## Multi-instance validation
**Required?**: no — methodology tooling (deterministic CLI audit + tracked fixtures + test oracle); no multi-user/device/account surface.
**Result**: not-applicable

## VAL-1 layered safety (Step 5b)
**Result**: PASS — `validate_slice_layers` on all changed `.py` (with `--imports-allowlist tests`): 0 secrets, 0 import findings, 0 suppressed. Both layers clean.

## Shippability catalog regression (Step 5.5)

PTFCD-1 pre-catalog path audit: **clean** (27 rows, 206 test-path tokens, all exist). Catalog run: **25/29 PASS, 4 FAIL** — classified:

### #1 + #19 — SPURIOUS (Windows CRLF/LF test artifact; content byte-identical; NOT slice-030A; NOT a real drift)
- **Failing test**: `tests/skills/diagnose/test_diagnose_skill_drift.py::test_in_repo_and_installed_diagnose_skill_md_are_content_equal`
- **Cause classification (after investigation, user-requested)**: **reality surprise — spurious Windows CRLF/LF line-ending artifact + latent test bug**. NOT implementation bug, NOT slice-030A regression, NOT even a real content drift.
- **Root-cause evidence**: `git config core.autocrlf` = `true`. Line-ending census: working-tree `skills/diagnose/SKILL.md` = **303 CRLF** / 0 LF-only, sha `971e2326…`, 25901 bytes; git `master` blob = **0 CRLF / 303 LF**, sha `aaab3190…`, 25598 bytes; installed `~/.claude/skills/diagnose/SKILL.md` = **0 CRLF / 303 LF**, sha `aaab3190…`, 25598 bytes. **CRLF-normalized content of working-tree == installed → `True`** (identical text; the only difference is `\r\n` vs `\n`). `git diff master -- skills/diagnose/SKILL.md` = **0 lines** and `git status --porcelain` empty (git normalizes per autocrlf; sees NO change). slice-030A's only `skills/` edits = `build-slice/SKILL.md` +18, `reflect/SKILL.md` +11 — zero diagnose surface (re-confirmed).
- **Why the test fails**: `test_diagnose_skill_drift.py` does a **raw-byte** equality of in-repo working-tree (CRLF, via `autocrlf=true` checkout) vs installed (LF) with no line-ending normalization → spurious mismatch on any Windows checkout whose installed copy is LF. `test_build_slice_skill_drift` PASSES here only because slice-030A `cp`'d the CRLF working-tree → installed (coincidentally CRLF-matching), masking the identical latent fragility.
- **Class note**: NEW discovered class for /reflect — **drift tests using raw-byte comparison are CRLF/LF-fragile under Windows `core.autocrlf=true`** (affects diagnose + latently build-slice/reflect/commit-slice/slice drift tests). Distinct from but adjacent to the R-4/slice-029 environment-false-HALT class; reinforces 030B's catalog-robustness charter and is a standalone future-slice candidate (normalize line endings in the drift-test comparisons).
- **Action**: do NOT fix inside slice-030A — out of scope (touches `tests/skills/diagnose/`, a different concern from R-4/BC-1; per CLAUDE.md "refactors need a slice, no while-I'm-here"). slice-030A is verifiably innocent AND the "drift" is not real (content byte-identical). Recommended: user-approved deferral (spurious not-slice-caused CRLF/LF artifact) → /reflect proceeds; capture the drift-test line-ending fragility as a /reflect Discovered item + new slice candidate.

### #28 + #29 — NOT real failures (catalog-runner prose-cell mis-parse artifacts)
- **Cause**: the ad-hoc catalog runner's heuristic picked the row's prose *description* cell (rows #28/#29 have long narrative Command-adjacent cells) and tried to shell-exec it ("'UTF8-STDOUT-1' is not recognized" / "'/diagnose' is not recognized"). The rows' actual pytest commands (`test_utf8_stdout_regression.py`, `test_skill_md_pins.py`, `test_methodology_changelog.py -k v_0_42_0`) all PASS — covered green by the full methodology suite (573 passed, 0 failed) run at /build-slice pre-finish.
- **Class note**: this is the slice-024 "strip backticks / Runtime-cell-as-command footgun" + slice-029 #28/#29 ad-hoc-runner fragility — itself part of what 030B's "machine-stable command column" addresses.
- **Action**: no slice regression; informational. (A robust catalog runner is 030B scope.)

## Reality surprises
- **Pre-existing local working-tree drift in `skills/diagnose/SKILL.md`** (971e vs master/installed aaab) surfaced by the shippability catalog — independent of slice-030A. Fresh N+1 instance of the R-4/slice-029 environment-drift-false-HALT class; reinforces 030B's charter (catalog decoupling + machine-stable command column). Logged here; user decides remediation at the PCA-1 HALT.
