# Validation: Slice 002 fix-diagnose-contract-and-cwd-mismatch

**Date**: 2026-05-09
**Result**: PASS (3/3 ACs PASS with evidence; deferred manual smoke also exercised cleanly)

## Per-criterion results

### AC #1: SKILL.md Step 1 documents cwd-must-match-TARGET pattern + emits at-spawn warning

- **Status**: PASS
- **Evidence (prose-pin)**:
  - `tests/skills/diagnose/test_skill_md_pins.py::test_skill_md_step1_documents_cwd_constraint` PASSED — Step 1 region contains "cd to TARGET" / "cwd must match" / similar phrase
  - `tests/skills/diagnose/test_skill_md_pins.py::test_skill_md_step1_emits_cwd_mismatch_warning` PASSED — Step 1 contains "warning" + TARGET/PWD/cwd context
- **Evidence (deferred manual smoke, formerly AC #5)**: ran the SKILL.md Step 1 cwd-check bash directly with TARGET set to a path outside `$PWD`:
  - With `TARGET="<HOME>"` (parent of `$PWD`), the warning fired with full prose: "WARNING: TARGET resolves to a path outside the current directory." + slice-001 / claude-code #57037 context + recommendation to `cd $TARGET` and re-invoke.
  - With `TARGET="$(pwd)"` (happy path), no warning (silent — correct behavior).
- **Notes**: per slice-002 critique M3 + R-2, runtime emission is acknowledged-fragile because it depends on Claude (orchestrator) executing the SKILL.md prose at runtime. The bash check itself is verified-correct via the manual smoke above; the orchestrator's adherence to SKILL.md Step 1 prose remains a soft contract.

### AC #2: Canonical contract wording locked across SKILL.md Step 5 + 11 pass templates (byte-equal)

- **Status**: PASS
- **Evidence (4 prose-pin tests, all PASSED)**:
  - `test_skill_md_step5_allows_bash_for_graphify` — SKILL.md Step 5 contains canonical contract string
  - `test_pass_templates_allow_bash_for_graphify` — all 11 pass templates contain canonical contract string
  - `test_no_legacy_no_bash_no_python_phrase` — legacy phrase "Do NOT call Write, Bash, or python" absent across SKILL.md + 11 templates
  - `test_pass_templates_match_skill_md_step5_contract` — byte-equality verified: canonical string appears at all 12+ sites
- **Evidence (manual count via Python)**: canonical string occurs **13 times total** — 1 in SKILL.md Step 5 contract bullet + 11 in pass templates' Output format intros + 1 extra in `01-intent.md` Hard rules line 12. Matches design's "12 sites" count plus the documented extra in 01-intent's Hard rules.

### AC #3: risk-register.md conforms to RR-1 schema

- **Status**: PASS
- **Evidence (RR-1 audit)**:
  - `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open --top 5` returned:
    - **R-1** "Cwd-mismatch tool denial..." — likelihood: medium, impact: high, status: open, **score: 6, band: high** (matches the slice-002 ranking that selected this risk)
    - **R-2** "No programmatic test ensures /diagnose emits cwd-mismatch warning at runtime" — likelihood: medium, impact: low, status: open, **score: 2, band: low**
    - **0 violations** in audit output
- **Evidence (integration test)**: `tests/methodology/test_risk_register_audit_real_file.py::test_project_risk_register_audit_clean` PASSED — asserts ≥1 risk + zero violations against the project's real risk-register.md.
- **Notes**: heading format used em-dash (`## R-1 — title`); the audit's `_RISK_HEADING_RE` accepts em-dash or single-hyphen (the `--` double-dash shown in the audit's docstring example doesn't actually match the regex — discovered during build, switched to em-dash). Recorded as Discovered in reflection.

## Multi-instance validation

**Required?**: no
**Result**: not-applicable
**Evidence**: slice modifies prose + format conversion; no multi-user / multi-device / sync surface.

## VAL-1 layered safety checks

### Layer A — Credential scan (Critical)

- **Result**: 0 secrets detected
- **Evidence**: `tools.validate_slice_layers` ran on 15 changed files; zero Layer A findings.

### Layer B — Dependency hallucination check (Important)

- **Result**: 3 findings, all DEFERRED with rationale (same intentional-internal-imports class as slice-001)
- **Evidence**:
  ```
  3 import finding(s):
    tests/skills/diagnose/test_skill_md_pins.py:15 — `from tests.skills.diagnose.conftest import ...`
    tests/methodology/test_risk_register_audit_real_file.py:16 — `from tests.methodology.conftest import ...`
    tests/methodology/test_risk_register_audit_real_file.py:17 — `from tools.risk_register_audit import ...`
  ```
- **Disposition**: DEFERRED — Layer B v1 has no per-project import allowlist; same disposition as slice-001 validation:
  - **`tests`**: project's own pytest tree; discovered via conftest, not via pip install
  - **`tools`**: the `ai-sdlc-tools` package per `pyproject.toml [tool.setuptools] packages = ["tools"]`. Layer B reads `[project.dependencies]` (external dependencies), not the project's own declared package list. So `tools` is the project's package, not a hallucination.
  - **Followup candidate** (carried from slice-001): `--imports-allowlist` flag on `tools.validate_slice_layers` so projects shipping scripts-not-packages can declare known-internal imports. Same recurrence as slice-001 confirms this is a methodology gap, not slice-specific.

## Reality surprises

**Audit's heading-format docstring is misleading.** RR-1 audit's docstring shows `## R-NN -- <title>` (double-dash) as a valid format, but the actual `_RISK_HEADING_RE` regex accepts only single em-dash OR single hyphen (one character). My initial format-conversion used `--` which produced a silent zero-risks audit. Switched to em-dash; audit now sees both R-1 and R-2.

**Implication**: future slices that add risks to risk-register.md should use em-dash heading separator, not double-dash. The audit's docstring should be corrected — that's a tooling-cleanup candidate (small slice or risk-spike, not a /reflect priority).

**Slice-001's defer carried over**: the VAL-1 Layer B internal-imports issue surfaces every slice that touches tests/. This is now confirmed-recurring across two slices — graduates from "one-off finding" to "real methodology gap". Worth adding to `lessons-learned.md` under slice-002's entry as a pattern.

## Shippability catalog regression check

**Status**: PASS

| # | Slice | Critical path | Command | Result | Runtime |
|---|---|---|---|---|---|
| 1 | slice-001-diagnose-orchestration-fix | /diagnose orchestration | `pytest tests/skills/diagnose/` | **30/30 PASS** | 1.7s |

No regression — slice-002's prose edits to SKILL.md and 11 pass templates did not break any of slice-001's foundation tests.

## WS-1 + ETC-1 audits

- **WS-1** (Walking-skeleton): not enabled per mission-brief (opt-in false). Audit returned silent, gate passes.
- **ETC-1** (Exploratory-charter): not enabled per mission-brief (opt-in false). Audit returned silent, gate passes.
