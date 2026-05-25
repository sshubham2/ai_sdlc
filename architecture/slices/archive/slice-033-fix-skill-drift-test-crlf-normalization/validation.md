# Validation: Slice 033 fix-skill-drift-test-crlf-normalization

**Date**: 2026-05-17
**Result**: PASS

## Per-criterion results

### AC1: 5 skill-drift modules + CAD-1 audit normalize EOL; diagnose repro PASSES under autocrlf=true
- **Status**: PASS
- **Evidence**: `pytest` of all 5 skill-drift modules + `test_critique_agent_drift.py` with `git config core.autocrlf` = `true` → **13 passed**. The pre-existing failing repro `test_in_repo_and_installed_diagnose_skill_md_are_content_equal` (WRITTEN-FAILING at /slice: in-repo `971e2326…` vs installed `aaab3190…`) now PASSES. Deeper EOL-agnostic proof: synthetic CRLF vs LF file → `_normalized_sha256` equal = **True** (comparator is line-ending-agnostic independent of the actual working-tree state).
- **Notes**: working tree is LF post-renormalize (T6); the EOL-agnostic property holds regardless (proven by the synthetic-CRLF probe + AC2 fixtures), so the fix is environment-independent as designed.

### AC2: Real-drift detection preserved on BOTH surfaces
- **Status**: PASS
- **Evidence**: **4 passed** — (a) `test_normalized_compare_still_fails_on_genuine_content_divergence` (shared comparator still raises on non-EOL divergence); (b) existing `test_drift_detection_fires_on_artificial_byte_flip` + CLI exit-code-matrix still exit 1 on `# v1`/`# v2` (CAD-1-side must-not-mask proof); plus new `test_cad1_audit_treats_crlf_and_lf_identical_content_as_clean` EOL-only complement → exit 0.
- **Notes**: the must-not-mask-real-drift safety property is preserved on both the skill-drift comparator and the CAD-1 audit.

### AC3: `.gitattributes` + targeted renormalize → guarded `.md` no CRLF in working tree
- **Status**: PASS
- **Evidence**: `test_guarded_md_files_have_no_crlf_in_working_tree` → **1 passed** (zero `\r\n` in every guarded in-repo `.md`: 10 skill SKILL.md + 11 diagnose passes + 6 agents/*.md). `git check-attr eol` reports `lf` for `skills/slice/SKILL.md`, `agents/critique.md`, `skills/diagnose/passes/03f-layering.md`. Working-tree-STATE check, not merely the declaration.
- **Notes**: `git add --renormalize` produced an empty index diff (blobs already LF — ADR-033 claim verified); a scoped `rm + git checkout --` re-materialized the LF working tree. `git diff HEAD -- skills/ agents/` EMPTY confirms zero content change (line endings only).

### AC4: Catalog rows #1/#19 PASS as a property of the AC1 fix (cp-state-independent)
- **Status**: PASS
- **Evidence**: shippability row #1 (`pytest tests/skills/diagnose/`) → **41 passed**; row #19 (`test_layering_pass_textual_evidence.py test_diagnose_skill_drift.py …`) → **4 passed**. Green because the AC1 comparator is EOL-agnostic — equality no longer depends on byte-identical line endings, so the slice-030A masking-by-cp anti-pattern is structurally impossible to reintroduce. This is a property of the fix, not a "no prior cp" manual procedure.

### AC5: Governing-surface consistency (RULE-ID EOL-DRIFT-1)
- **Status**: PASS
- **Evidence**: `VERSION` = `~/.claude/ai-sdlc-VERSION` = `plugin.yaml` version = **0.47.0** (atomic 4-part bump from 0.46.0). `test_v_0_47_0_eol_drift_1_entry_present_in_repo_and_installed` + `test_root_claude_md_cad1_eol_agnostic.py` → **2 passed** (changelog v0.47.0 EOL-DRIFT-1 entry present in both in-repo + installed surfaces with canonical phrase `content-equal modulo line endings` + ADR-033; CLAUDE.md L33/L36 no longer say "MUST be byte-equal"). Changelog in-repo↔installed v0.47.0 synced (diff empty). PMI-1 audit clean at 0.47.0.

## Multi-instance validation
**Required?**: no — test/tooling change, no multi-user/device/account surface.
**Result**: not-applicable

## VAL-1 layered safety (Step 5b)
**Result**: PASS — 0 secret(s) (Layer A), 0 import finding(s) (Layer B), 0 suppressed. `--imports-allowlist tests`.

## WS-1 / ETC-1 (Steps 5c/5d)
Not applicable — mission-brief `**Walking-skeleton**: false`, `**Exploratory-charter**: false`.

## Shippability catalog regression check (Step 5.5)
- **Pre-gates**: SCMD-1 clean (32 rows; 352 cited fns; incidental=0, essential=32, clean=320); PTFCD-1 clean (219 test-path tokens all exist).
- **Catalog result**: **32/32 rows PASS** (33 Machine-cmd segments). Rows #1–#27 + #29–#32 PASS via deterministic `;`-split; row #28 (the lone multi-segment row) PASSES under SCMD-1-correct **per-segment** backtick-strip (both segments: 26 passed + 2 passed). No regression introduced by slice-033 — including the R-5 rows #1 (41 passed) and #19 (12 passed).

## Reality surprises
- **Ad-hoc-runner `;`-split footgun reproduced LIVE (R-5 secondary discovery / slice-032 N+1)**: a naive catalog runner that strips only the OUTER backticks of the Machine-cmd cell (not per-`;`-segment) false-FAILs row #28 — segment 2's leading `` ` `` becomes argv[0] → `WinError 2`. This is exactly the slice-032 secondary discovery recorded in R-5; it is NOT a slice-033 regression (row #28 PASSES under SCMD-1-correct parsing). Fresh corroborating evidence for the deferred **R-8** (`shippability Step-5.5 runner ;-split contract unpinned`) to be opened at `/reflect` (m2 ACCEPTED-FIXED handle).
- **R-7 silent-bypass reproduced LIVE at /build-slice pre-finish (N+1 since slice-031)**: the mission-brief `**Test-first**: true` trailing annotation broke `test_first_audit.py`'s `\s*$`-anchored regex → TF-1 silently default-off-bypassed; caught only by reading the gate's real output ("not enabled" on a test-first slice). Fixed in-slice (bare field-line + HTML comment). Fresh R-7 recurrence evidence for `/reflect`.
