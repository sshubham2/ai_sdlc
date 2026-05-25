# Validation: Slice 008 refine-bc-1-anchors-with-negative-context

**Date**: 2026-05-10
**Result**: PASS

## Per-criterion results

### AC #1: slice-005 archive — BC-PROJ-1 + BC-GLOBAL-1 NOT in applicable

- **Status**: PASS
- **Evidence**: real-environment subprocess invocation of audit CLI:
  ```
  python -m tools.build_checks_audit \
    --slice architecture/slices/archive/slice-005-add-bc-1-keyword-precision \
    --project-checks architecture/build-checks.md \
    --changed-files tools/build_checks_audit.py architecture/build-checks.md \
    --no-carry-over --json
  ```
  Output: `applicable: ['BC-PROJ-2']`, `skipped: ['BC-GLOBAL-1', 'BC-PROJ-1']`. BC-PROJ-1 + BC-GLOBAL-1 absent from applicable → silenced ✓.
- **Notes**: BC-PROJ-2 still in applicable on slice-005 — acceptable per Critic M1 (BC-PROJ-2 not migrated; N=1 below promotion threshold). AC #1 only gates BC-PROJ-1 + BC-GLOBAL-1, NOT BC-PROJ-2. The pytest-secondary `test_slice_005_archive_no_longer_fires_proj1_or_global1` PASSING corroborates.

### AC #2: slice-006 archive — BC-PROJ-1 + BC-GLOBAL-1 NOT in applicable

- **Status**: PASS
- **Evidence**: subprocess invocation:
  ```
  python -m tools.build_checks_audit \
    --slice architecture/slices/archive/slice-006-update-critic-with-cross-cutting-conformance-dimension \
    --project-checks architecture/build-checks.md \
    --changed-files agents/critique.md \
    --no-carry-over --json
  ```
  Output: `applicable: []`, `skipped: ['BC-GLOBAL-1', 'BC-PROJ-1', 'BC-PROJ-2']`. All three rules silenced (BC-PROJ-2 silenced incidentally because slice-006's `agents/critique.md` glob match doesn't match BC-PROJ-2's `skills/**/*.py, tools/**/*.py`).
- **Notes**: pytest-secondary `test_slice_006_archive_no_longer_fires_proj1_or_global1` PASSING corroborates.

### AC #3: slice-007 archive — BC-PROJ-1 + BC-GLOBAL-1 NOT in applicable

- **Status**: PASS
- **Evidence**: subprocess invocation:
  ```
  python -m tools.build_checks_audit \
    --slice architecture/slices/archive/slice-007-add-critique-agent-content-equality-audit \
    --project-checks architecture/build-checks.md \
    --changed-files agents/critique.md skills/critic-calibrate/SKILL.md \
    --no-carry-over --json
  ```
  Output: `applicable: []`, `skipped: ['BC-GLOBAL-1', 'BC-PROJ-1', 'BC-PROJ-2']`. All three silenced.
- **Notes**: This is the slice that closed the BC-1 promotion threshold (N=3 across slice-005..007). Verified as silenced. pytest-secondary `test_slice_007_archive_no_longer_fires_proj1_or_global1` PASSING corroborates.

### AC #4: slice-001 archive — BC-PROJ-1 AND (BC-PROJ-2 OR BC-GLOBAL-1) ARE in applicable (backward-compat covenant)

- **Status**: PASS
- **Evidence**: subprocess invocation:
  ```
  python -m tools.build_checks_audit \
    --slice architecture/slices/archive/slice-001-diagnose-orchestration-fix \
    --project-checks architecture/build-checks.md \
    --changed-files skills/diagnose/SKILL.md skills/diagnose/write_pass.py skills/diagnose/passes/01-intent.md \
    --no-carry-over --json
  ```
  Output: `applicable: ['BC-GLOBAL-1', 'BC-PROJ-1', 'BC-PROJ-2']`. All three legitimate fence-parsing + subagent-fan-out rules continue to fire. ADR-004 backward-compat covenant honored.
- **Notes**: Critic m1's over-suppression risk concern is empirically refuted by this AC — slice-001 contains zero of the negative-anchor tokens, so the final filter doesn't suppress. Robust preservation. pytest-secondary `test_slice_001_archive_still_fires_legitimate_rules` PASSING corroborates.

### AC #5a: `Negative anchors` field-name pinned in BOTH project + global build-checks files

- **Status**: PASS
- **Evidence**: PowerShell substring grep of both files:
  - `architecture/build-checks.md` contains `Negative anchors`: True
  - `~/.claude/build-checks.md` contains `Negative anchors`: True
- **Notes**: pytest-secondary `test_negative_anchors_schema_documents_field_name_in_both_files` PASSING corroborates. TWO-surface (project + global) schema-pin discipline per slice-005 + Critic M2 generalization.

### AC #5b: `final filter` semantics phrase pinned in BOTH files (case-insensitive)

- **Status**: PASS
- **Evidence**: PowerShell substring grep on lowered content:
  - `architecture/build-checks.md` contains `final filter`: True
  - `~/.claude/build-checks.md` contains `final filter`: True
- **Notes**: pytest-secondary `test_negative_anchors_schema_documents_final_filter_semantics` PASSING corroborates. The `final filter` phrase encodes the universal post-applicability framing — pinning prevents doc-refactor drift losing the cross-path-uniformity semantic. Critic M2 generalization from slice-005's `Trigger anchors` + `word-boundary` two-pin pattern.

### Bonus: Must-not-defer parse-violation channel

(not a numbered AC; per Critic M3 + input-validation must-not-defer; verified for completeness)

- **`negative-anchor-overlaps-positive` violation kind**: synthetic fixture with rule whose `Trigger keywords: alpha`, `Trigger anchors: alpha`, `Negative anchors: alpha` (overlap) → `_parse_rules` emits 1 violation:
  ```
  kind: 'negative-anchor-overlaps-positive'
  message: "rule BC-PROJ-99: Negative anchor 'alpha' overlaps with positive Trigger keywords/anchors. Negative anchors must be exclusionary (no overlap with positive vocabulary)."
  ```
- **`always: true` + negative-anchor interaction**: pytest `test_always_true_rule_with_negative_anchor_match_is_skipped` PASS — the algorithm-path-conformance gap caught by Critic M3 is now closed at the audit-level (not just at fixture-level).
- **Migration-tuple integrity**: pytest `test_migrated_rules_have_expected_negative_anchors` PASS — BC-PROJ-1 + BC-GLOBAL-1 carry the canonical 9-token tuple as written in design.md / ADR-007.

## Multi-instance validation

**Required?**: NO — slice modifies a methodology audit + schema files (no multi-user / multi-device / multi-account dimension).

**Result**: not-applicable.

## Reality surprises

**None unanticipated.** Empirical findings during /design-slice (per slice-005..007 N=6 ratchet to N=7 at slice-008) pre-discovered the actual N=3 false-positive class behavior including:

- Pre-slice-008: slice-005 fires BC-PROJ-1 + BC-PROJ-2 + BC-GLOBAL-1 (kw path; methodology-vocabulary discussion); slice-006 fires BC-PROJ-1 + BC-GLOBAL-1 (glob path on agents/**/*.md); slice-007 fires BC-PROJ-1 + BC-GLOBAL-1 (same).
- BC-PROJ-2 N=1 (slice-005 only) — surfaced at /critique by Critic M1 → ACCEPTED-FIXED disposition (drop BC-PROJ-2 from migration scope).
- Algorithm-path-conformance gap on `always: true` short-circuit — surfaced at /critique by Critic M3 → ACCEPTED-FIXED disposition (added must-not-defer test row 9).
- Cross-project applicability of AI-SDLC-internal tokens in global build-checks — surfaced at /critique by Critic m1 → ACCEPTED-FIXED disposition (cross-project sentence added to global file's schema-prelude).

All discoveries were captured pre-build via Critic findings; build executed against the corrected design with zero build-time DEVIATIONs.

## VAL-1 layered safety checks

**Layer A (credential scan)**: 0 secret(s) detected across changed files. CLEAN.
**Layer B (dependency hallucination)**: 0 import finding(s); 0 suppressed (allowlisted). CLEAN.

```
$PY -m tools.validate_slice_layers \
  --slice architecture/slices/slice-008-refine-bc-1-anchors-with-negative-context \
  --changed-files tools/build_checks_audit.py tests/methodology/test_build_checks_audit.py tests/methodology/test_methodology_changelog.py architecture/build-checks.md methodology-changelog.md VERSION plugin.yaml architecture/shippability.md \
  --imports-allowlist tests
# VAL-1 layered safety checks: 0 secret(s), 0 import finding(s), 0 suppressed (allowlisted). Clean — both layers passed.
```

## WS-1 walking-skeleton audit

**Skipped (default-off)**: mission-brief declares `**Walking-skeleton**: false` → audit returns clean silently. Slice is a refinement/precision improvement, not a new vertical-slice introducing a new architectural layer.

## ETC-1 exploratory-charter audit

**Skipped (default-off)**: mission-brief declares `**Exploratory-charter**: false` → audit returns clean silently. Slice is methodology-tooling work with concrete numbered ACs; no UX-centric exploratory mission.

## Shippability catalog regression check

**8 rows** (slice-001..008), **69 tests total**, **69 PASS** in **2.84 seconds** (well under 2-min target).

Per-row breakdown:
- Row 1 (slice-001): /diagnose orchestration tests — PASS
- Row 2 (slice-002): /diagnose contract + RR-1 schema — PASS
- Row 3 (slice-003): VAL-1 imports allowlist — PASS
- Row 4 (slice-004): RR-1 docstring + regex examples — PASS
- Row 5 (slice-005): BC-1 keyword precision (anchors v1.1) — PASS
- Row 6 (slice-006): Critic agent 9-dim CCC-1 — PASS
- Row 7 (slice-007): CAD-1 byte-equality audit + slice-006 PMI-1 escape closure (with stale 0.22.0 test ref dropped per slice-008 supersession) — PASS
- Row 8 (slice-008): BC-1 v1.2 negative-context anchors (this slice) — PASS

No regressions. Slice-008 has not silently broken any past slice's critical path.

## TF-1 strict-pre-finish

**9 rows, 9 PASSING, 0 WRITTEN-FAILING, 0 PENDING**. CLEAN.

## PMI-1 invariant

**CLEAN**. `python -m tools.plugin_manifest_audit --root .` exit 0. 24 skills, 5 agents, 15 tools, version 0.23.0. `VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` (installed) + `plugin.yaml.version` all 0.23.0 atomic.

## install_audit (INST-1)

**CLEAN**. 24/24 skills, 5/5 agents, 4/4 templates, 15/15 tool modules; methodology v0.23.0.

## Bidirectional sha256 forensic

`methodology-changelog.md` byte-equal in-repo (`0A7AA6CA04E372FB`) ↔ installed (`0A7AA6CA04E372FB`). `VERSION` + `~/.claude/ai-sdlc-VERSION` byte-equal (`D1994E4942B06EC3`). `architecture/build-checks.md` (`B46329E445D7A58B`) and `~/.claude/build-checks.md` (`2D21B76751452FC7`) intentionally different (project vs global file with different rule sets — BC-PROJ-1 vs BC-GLOBAL-1 — same schema-prelude TWO-sentence structure + cross-project sentence in global file).

## Verdict summary

| AC | Status | Evidence |
|----|--------|----------|
| #1 | PASS | slice-005 archive subprocess invocation: BC-PROJ-1 + BC-GLOBAL-1 silenced ✓ |
| #2 | PASS | slice-006 archive subprocess invocation: applicable=[] ✓ |
| #3 | PASS | slice-007 archive subprocess invocation: applicable=[] ✓ |
| #4 | PASS | slice-001 archive subprocess invocation: BC-PROJ-1 + BC-PROJ-2 + BC-GLOBAL-1 still fire ✓ |
| #5a | PASS | `Negative anchors` substring in both project + global build-checks files ✓ |
| #5b | PASS | `final filter` substring in both files (case-insensitive) ✓ |

**6 / 6 ACs PASS. 0 FAIL. 0 PARTIAL.** Shippability catalog 69/69. VAL-1 clean. PMI-1 clean. TF-1 PASSING=9.

**Slice ready for /reflect.**
