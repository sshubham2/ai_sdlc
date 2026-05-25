# Validation: Slice 049 add-triage-adopt-skill-drift-guards

**Date**: 2026-05-19
**Result**: PASS

For a methodology slice the "real environment" is the real repo tree: per the BC-PROJ-4 / slice-038 dogfood law, running the shipped guards + the full catalog against the actual tree is the decisive validation artifact (not a unit fixture).

## Per-criterion results

### AC1: `test_triage_skill_drift.py` exists + content-equal via `assert_md_forward_synced`, PASSES on synced tree, genuine-contrast non-tautology
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_triage_skill_drift.py` → passed (real tree). Non-tautology proven in build-log 2026-05-19 15:00: installed copy perturbed with a non-EOL byte → `FAILED tests/methodology/test_triage_skill_drift.py::test_in_repo_and_installed_triage_skill_md_are_content_equal`; restored → `1 passed`. Reuses the shared `assert_md_forward_synced` verbatim (2 refs, zero new comparator).
- **Notes**: structural twin of `test_slice_skill_drift.py`; EOL-agnostic per ADR-033.

### AC2: `test_adopt_skill_drift.py` same for `skills/adopt/SKILL.md`
- **Status**: PASS
- **Evidence**: `pytest …test_adopt_skill_drift.py` → passed; build-log 2026-05-19 15:00: adopt perturbed(non-EOL)→FAILED→restored→passed (independent genuine-contrast, not shared with triage).

### AC3: methodology-surface behavior change recorded — `## v0.57.0` OSDG-1 entry + 4-part PMI-1 bump + entry-pin
- **Status**: PASS
- **Evidence**: `pytest test_methodology_changelog.py::test_v_0_57_0_osdg_1_entry_present_in_repo ::test_v_0_57_0_osdg_1_shippability_consumer_propagation ::test_plugin_yaml_version_matches_version_file_invariant` → 3 passed. PMI-1 audit: clean, **version 0.57.0** (25 skills/5 agents/25 tools). MCFS-1: PASS (in-repo↔installed changelog content-equal modulo EOL). VERSION=plugin.yaml.version=`~/.claude/ai-sdlc-VERSION`=0.57.0 (4-part atomic bump complete; the pre-existing slice-048 `ai-sdlc-VERSION`=0.55.0 leg-drift was reconciled — recorded in build-log FINDING for /reflect, not a slice-049 reality surprise).

### AC4: exactly ONE shippability row #49 covering both guards; SRSC-1 runner green
- **Status**: PASS
- **Evidence**: `grep -cE '^\| 49 \| slice-049'` → **1** (one-row-per-slice; B-add-1 satisfied). `python -m tools.shippability_runner architecture/shippability.md` → **49 rows, 49 PASS, 0 FAIL** (ec 0). SCMD-1 pre-gate clean (49 rows, incidental=0, essential_unregistered=0). PTFCD-1(b) pre-gate clean (286 test-path tokens — all files+functions exist; the new `test_v_0_57_0_osdg_1_*` functions resolve).

### AC5: CLAUDE.md Mini-CAD generalization keeps the prose-pin passing (M-add-1)
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_root_claude_md_cad1_eol_agnostic.py` → 1 passed. The generalized bullet retains "content-equal modulo line endings" + "EOL-DRIFT-1" + "ADR-033" and introduces no "MUST be byte-equal"; re-run immediately after the edit per slice-039 realign-the-pin-you-touch law (build-log 2026-05-19 15:03).

## VAL-1 layered safety checks (Step 5b)
- **Layer A — credential scan**: clean (no secrets in the 3 changed `.py` files)
- **Layer B — dependency hallucination**: clean (`--imports-allowlist tests`; the new test modules import only `pathlib`, `tests.methodology.conftest`, `tests.skill_drift_equality` — all resolve)

## WS-1 / ETC-1
- Walking-skeleton: not enabled (brief `**Walking-skeleton**: false`) — default-off, clean
- Exploratory-charter: not enabled (brief `**Exploratory-charter**: false`) — default-off, clean

## Multi-instance validation
**Required?**: no
**Result**: not-applicable
**Evidence**: test-only methodology slice — no multi-user / multi-device / multi-account surface.

## Shippability regressions
None. SRSC-1 pinned runner: 49 rows / 49 PASS / 0 FAIL — this slice's row #49 is green AND all 48 prior slices' critical paths remain green (no regression introduced). Full methodology suite at /build-slice pre-finish: 730 passed.

## Reality surprises
- None novel. The one build-time discovery — pre-existing slice-048 `~/.claude/ai-sdlc-VERSION`=0.55.0 forward-sync leg-drift — was a *pre-existing latent condition* (not predicted, but not a slice-049 effect): surfaced by the M2 pre-sync evidence-preservation discipline, reconciled to 0.57.0 by this slice's mandated 4-part PMI-1 bump, and recorded in build-log as a FINDING for `/reflect` (slice-035 DEVIATION-2 / installed-VERSION-leg recurrence class — candidate /reflect note: the 4-part bump's installed-leg is a recurring forward-sync miss; MCFS-1 covers the changelog leg but no equivalent guards the `ai-sdlc-VERSION` leg).
