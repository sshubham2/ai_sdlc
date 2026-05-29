# Code Review: Slice 081 fix-drift-check-enforcement-gap

**code-Critic reviewed**: slice diff vs default branch (71c7fff), filtered to in-scope paths, in worktree `C:\Users\sshub\ai_sdlc-wt\slice-081-fix-drift-check-enforcement-gap`
**Date**: 2026-05-29
**Result**: FINDINGS (3 Minor; 0 Blocker, 0 Major)

> v1 advisory. m1 + m2 were applied in-band during this slice (see Disposition under each); m3 requires no change.

## Summary

A high-quality, tightly-scoped audit-gate mint. `tools/drift_check_audit.py` is a faithful CRP-1 clone (`_SKIP_VALUE_RE` em-dash, `_frontmatter_*`, `_resolve_mode` ladder, exit-code mapping all byte-match), the line-anchored + slice-anchored matcher behaves correctly against the producer template and the M-add-1 false-ACCEPT surface, Step 6 wiring orders `/drift-check` full-mode BEFORE the audit, the escape-hatch lifecycle is complete, and self-application discharges clean (exit 0). 23/23 unit + repro tests pass; PMI-1/INST-1/TVFS-1 green; version bump consistent across all five surfaces. All findings Minor.

## Changed files (in-scope)
```
tools/drift_check_audit.py
tests/methodology/test_drift_check_audit.py
tests/bugs/test_drift_check_enforcement_gap.py
skills/build-slice/SKILL.md
skills/drift-check/SKILL.md
templates/milestone.md
tools/install_audit.py
plugin.yaml
pyproject.toml
VERSION
methodology-changelog.md
INSTALL.md
tests/methodology/test_build_slice_skill.py
tests/methodology/test_methodology_changelog.py
tests/methodology/test_pulse_worktree_resolver_tool_inventory.py
tests/methodology/test_utf8_stdout_regression.py
tests/methodology/test_vault_root_constant.py
architecture/slices/slice-081-fix-drift-check-enforcement-gap/build-log.md
```

## Findings

### Blockers (advisory in v1)
None. The gate performs a genuine non-stub check, fails closed, self-applies clean, contradicts no accepted ADR.

### Majors
None.

### Minors

#### m1: Slice-number regex has no LEFT anchor — `xslice-081` / `subslice-081` would false-ACCEPT
- **Claim under review**: `tools/drift_check_audit.py:208` — `slice_re = re.compile(rf"slice[- ]?0*{n}\b")`. The docstring + SKILL.md claim "slice-anchored"; the RIGHT side is anchored (`\b` + `0*` rejects `slice-0810`/`slice-081x`/`slice-810`), the LEFT side is not.
- **Issue**: `slice` matched as a bare substring; `aslice-081`/`subslice-081`/`xslice81` return True for n=81. Gated to `**Trigger**:` lines (real exposure ~zero — Trigger lines only carry `slice-NNN`), but the "slice-anchored" claim overstates the regex. The `test_marker_regex_anchoring` battery parametrizes only RIGHT-side collisions — left-prefix unpinned.
- **Proposed fix**: `rf"\bslice[- ]?0*{n}\b"` + add `("xslice-081", False)` / `("subslice-081", False)` rows.
- **Disposition**: **FIXED in-band** — regex left-anchored at `tools/drift_check_audit.py` `_drift_marker_present` + docstring updated; 2 left-prefix rows added to `test_marker_regex_anchoring`.

#### m2: AC5 says "4-part atomic bump"; the implementation correctly shipped 5-part
- **Claim under review**: `mission-brief.md` AC5 listed 4 bump surfaces; ADR-073 / changelog / drift-log all describe 5 (adding the venv `ai-sdlc-tools` TVFS-1 leg). Code is correct (all 5 = 0.76.0, TVFS-1 green); AC5 wording stale.
- **Disposition**: **FIXED in-band** — AC5 reworded to "5-part" naming the venv `ai-sdlc-tools` (TVFS-1) leg.

#### m3: `escape-hatch-malformed` short-circuits before the marker check
- **Claim under review**: `tools/drift_check_audit.py:315-331` — a malformed `drift-check-skip:` refuses even when a valid drift-log marker exists.
- **Issue**: intentional byte-for-byte CRP-1 parity (`critique_review_prerequisite_audit.py:264-280` short-circuits identically); fail-closed is the safe direction (McGraw defense-in-depth). No behavior change warranted.
- **Disposition**: **NO CHANGE** (intentional CRP-1 fidelity; fail-closed correct). Log-only.

## Dimensions checked
- [x] Unfounded assumptions — m1 (docstring "slice-anchored" stronger than the no-left-anchor regex delivered; fixed in-band).
- [x] Missing edge cases — none material; zero-pad/no-dash/space/right-collision/transposed/adjacent all resolve correctly; missing/empty drift-log → refuse; off-shape folder/missing milestone/mode-unresolvable map to documented exits; `splitlines()` EOL-agnostic (EOL-DRIFT-1 untriggered).
- [x] Over-engineering — none. `_ENFORCED_MODES` consumed; no dead params; minimal CRP-1 specialization.
- [x] Under-engineering — none. Every AC maps to a code element; repro 2/2 pass; touched Step 6 audits pre-satisfy clean.
- [x] Contract gaps — none. Type hints + docstrings; exit-code contract 0/1/2 documented + implemented; stable `rule: "DCE-1"` JSON envelope; idempotent read-only.
- [x] Security — none. Read-only; no subprocess/shell/eval/exec; no network/secrets; inputs validated via `_SLICE_FOLDER_RE` + `.exists()`.
- [x] Drift from vault — m2 (AC5 "4-part" vs 5-part shipped; code correct, AC reworded). ADR-073 ↔ code exact; self-entry present + read; shippability rows 86/87 propagated.
- [x] Web-known issues — none. Python stdlib + two in-repo modules; no third-party/deprecated/SyntaxWarning surface (`\b` inside `rf"..."` raw string).
- [x] Cross-cutting conformance — RSAD-1 (slice authored DCE-1, own tree passes DCE-1 exit 0); APED-1 (matcher executed against adversarial battery; M-add-1 fixture genuinely discriminates via the `_TRIGGER_LINE_RE` gate); byte-faithfulness vs CRP-1 confirmed; phantom-import check passes.
