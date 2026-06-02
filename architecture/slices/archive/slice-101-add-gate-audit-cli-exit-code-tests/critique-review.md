# Critique Review: Slice 101 add-gate-audit-cli-exit-code-tests

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-02
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's three Majors (M1/M2/M3) and three Minors are all VALID with correct severities, and the empirically-verified Builder fixes resolve them — the meta-Critic reproduced each fix against the real tool source and confirmed every block-path and clean-path fixture lands the asserted exit code deterministically. But a second pass surfaces one missed fixture-shape gotcha on row 6 (CSP-1) that will hard-fail (false-green to exit 0) at build time if a Builder copies the audit's own docstring example, plus two calibration-grade nuances (a non-existent kind literal cited in the M1 target-kind table, and a near-vacuous kind-assert for row 2). Verdict is EXTEND for the missed CSP-1 finding.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **M1** (int can't discriminate STOP cause for multi-kind audits) — confirmed; Major appropriate. Reproduced: PMI-1 with a *complete* valid `plugin.yaml` + orphan on-disk skill yields the SOLE kind `orphan-skill` (`plugin_manifest_audit.py:239-247`), no incidental `missing-field`/`version-mismatch`. TRI-1 present-sectionless and DR-1 missing-section both isolate correctly once the fixture is a present file. The Builder's cause-discrimination + per-audit target_kind table is the right fix.
- **M2** (branch_workflow row-8 machine-fragility) — confirmed; Major appropriate. Reproduced the fix: `git init` + `git branch -M trunk` + local `git config init.defaultBranch trunk` on an unborn-HEAD repo yields `_current_branch='trunk'`, `_resolve_default_branch='trunk'` (origin/HEAD symbolic-ref fails returncode 128 → falls through to init.defaultBranch), current==default → SOLE kind `on-default-branch` → `main()` returns 1, host-independent. The exit-2 fixture (non-slice folder name) returns `usage-error` *before* default-branch resolution (`branch_workflow_audit.py:484-515`), so it is env-independent. M2 fix fully validated.
- **M3** (mock_budget + shippability fixtures under-specified) — confirmed; Major appropriate. Reproduced: stacked `@patch("requests.post")/@patch("requests.get")` → SOLE kind `mock-budget`, `--strict` exit 1, plain exit 0 (`mock_budget_lint.py:866-870`). The 6-column SCMD-1 catalog with a `tests/...test_DOESNOTEXIST.py` token in Machine-cmd → `rows_scanned=1`, kind `missing-test-file`, `main()` exit 1 (not the exit-2 missing-file path). Both fixes correct.
- **m1** (mutation proves int-dependence, not cause) — confirmed; Minor appropriate. The two-guarantees distinction the Builder documented is technically accurate.
- **m2** (`--no-carry-over` redundant for bare-tmp fixtures) — confirmed; Minor appropriate. Verified: `_slice_is_carry_over` returns False when no sibling `mission-brief.md` exists (`triage_audit.py:140-146`; identical in `critique_review_audit.py:117-123`, `wiring_matrix_audit.py:80-86`). Keeping the flag as defensive is the right call.
- **m3** (row-8 "BRANCH-1" vs live BRANCH-2/3) — confirmed; Minor appropriate. The audit's argparse self-IDs "BRANCH-1" (`branch_workflow_audit.py:679`) while the live rule family is BRANCH-2/3; the footnote is accurate.

## Suspicious findings

No suspicious findings. All six first-Critic findings reproduce against real tool source; none over-reach.

## Missed findings

- **M-add-1 (Major): Row-6 (CSP-1) item-heading separator gotcha — fixture will false-green to exit 0 if copied from the audit docstring.** `_ITEM_HEADING_RE = r"^##\s+((?:TM|REQ|NFR)-?\d+)\s+[—\-]\s+(.+?)\s*$"` (`cross_spec_parity_audit.py:70-72`) matches a heading separator of exactly ONE dash or em-dash. But the audit's own docstring (`cross_spec_parity_audit.py:21-23`) shows the example shape `## TM-NN -- <title>` with a **double** dash. Reproduced: a `## TM-1 -- test threat` heading (double-dash, copied from the docstring) produces ZERO parsed items → ZERO violations → exit 0; only `## TM-1 - test threat` (single dash) yields the `broken-ref` violation → exit 1. The design's row-6 fixture cell only says "threat-model/requirements with a parity mismatch" and the Nuance column only covers `--skip-heavy-check`; neither the Builder nor the first Critic caught that the most-natural fixture authoring (matching the docstring) silently false-greens to exit 0. **This is the same class of false-exit-0 trap the first Critic correctly caught for rows 3 and 7 (M3) — M3's coverage is incomplete by exactly one row.** Proposed fix: row-6 fixture MUST use a single-dash (or em-dash) `## TM-N - <title>` heading AND a `mitigated` status with a non-existent `**Implementation**:` path; build-log non-vacuity evidence must show the exit flips to 0 when the violation row is corrected (proving the fixture, not the heading-parse, drives the exit).

## Severity adjustments

No severity adjustments. M1/M2/M3 are correctly Major (each defeats AC3 cause-pinning or AC2 non-vacuity if unfixed); m1/m2/m3 are correctly Minor (documentation/defensive, no exit-path impact).

## Notes

High confidence — every claim was reproduced against real tool source via the shared interpreter, not inferred from prose. Two calibration-grade nuances below a fileable finding the Builder should fold into the build:

(1) **Non-existent kind literal in the M1 target_kind table (row 6).** The design writes "the CSP-1 parity-mismatch kind (confirm exact literal at build)" — but there is no `parity-mismatch` kind anywhere in `cross_spec_parity_audit.py`. The real kinds are `broken-ref`/`missing-ref`/`invalid-status`/`missing-field`/`format` (CSPViolation, lines 113-125). A literal `"parity-mismatch" in {v.kind ...}` assertion would be *always-false* → the row-6 kind-assert would fail-to-trigger. The correct literal for a broken-Implementation-path fixture is `broken-ref`. The "confirm at build" hedge for rows 4/5/7 resolves to REAL literals — row 4 = `missing-section`, row 5 = `missing-cells` (not prose "empty-cell kind"), row 7 = `missing-test-file` (not prose "missing-test-path kind") — all verified; row 6 is the one placeholder that names a non-existent kind.

(2) **Row-2 (TRI-1) kind-assert is near-vacuous; the load-bearing discriminator is `is_file()`.** A present-sectionless `critique.md` AND a *missing* `critique.md` both yield exactly `no-section` (`triage_audit.py:216-222` vs `243-254`). So the M1 kind-assert `no-section in kinds` does NOT discriminate the intended cause (sectionless present file) from the accidental cause (missing file) for this one row. The design *did* capture the real fix in the row-2 Nuance column ("assert is_file() first … fixture must exist (M1)"), so the fix is adequate — but the build-log AC2 evidence for row 2 should explicitly record that `is_file()`, not the kind-assert, is the cause-pin.

No reservations on the in-process `main(argv)` design decision: all 8 modules have zero import-time side effects (logic guarded behind `if __name__ == "__main__"`) and `_stdout.reconfigure_stdout_utf8()` is idempotent + a no-op under pytest capture (`tools/_stdout.py:30-36`), so the consolidated module importing 8 mains is safe.
