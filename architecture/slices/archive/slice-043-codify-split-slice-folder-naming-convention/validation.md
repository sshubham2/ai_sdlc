# Validation: Slice 043 codify-split-slice-folder-naming-convention

**Date**: 2026-05-18
**Result**: PASS

## Per-criterion results

### AC1: split-slice folder/branch naming convention stated once, canonically, in a discoverable durable location
- **Status**: PASS
- **Evidence**: `CLAUDE.md` Brownfield rules → Branch-per-slice bullet now carries the convention sub-clause. Programmatic check: `split-slice follow-up` ✓, `prose lineage label only` ✓, `ADR-046` cited ✓ (all within the Branch-per-slice bullet of the Brownfield rules section). Pinned by `test_branch_workflow_split_slice_folder_convention.py::test_root_claude_md_branch_per_slice_bullet_states_split_slice_convention` (PASS) — extends, does not modify, the existing `test_root_claude_md_branch_per_slice_rule.py` substring contract (also PASS). No implicit "numeric-folder, letter-label-in-prose-only" trap remains: it is now an explicit, regression-pinned statement.
- **Notes**: ADR-046 is the locked decision record; the convention text is the single authoritative statement.

### AC2: branch_workflow_audit behavior on a split-slice follow-up is deterministic and intentional (actionable rejection naming the convention + the fix)
- **Status**: PASS
- **Evidence**: real CLI runs against synthetic fixtures —
  - `slice-030B-complete-x` (uppercase split shape) → exit 2 `usage-error`: *"split-slice follow-up folder name not accepted: 'slice-030B-complete-x'. Per ADR-046 / BRANCH-1, split-slice follow-up folders are numeric `slice-NNN-`; the `NNNx` letter (here `030B`) is a prose lineage label only … Rename to the next free numeric slice number …"* — names the convention + the next-free-number remedy + cites ADR-046/BRANCH-1.
  - `slice-030misc-x` (lowercase non-convention) → exit 2 generic `slice folder name does not match slice-NNN-<name> pattern` (m1 precision guard: uppercase-only `_SPLIT_SLICE_FOLDER_RE` correctly does NOT route lowercase to the split-specific message).
  - Mid-slice smoke (build-log) confirmed the real exit code is 2 (unchanged `usage-error` kind). Strict `_SLICE_FOLDER_RE` accept regex is untouched (numeric-only accept preserved — behavior-preserving).
- **Notes**: deterministic across the three documented input classes (numeric-accept / uppercase-split-reject-actionable / generic-reject-verbatim).

### AC3: regression test pins the decided BRANCH-1 behavior, non-tautological
- **Status**: PASS
- **Evidence**: `tests/methodology/test_branch_workflow_split_slice_folder_convention.py` — post-impl `5 passed`. Genuine contrast proven at build time (build-log Events 2026-05-18 TEST): the same module run against the UNMODIFIED audit produced `3 failed (ii convention-message, iii next-free-number-remedy, v CLAUDE.md prose-pin) + 2 passed (i canonical-accept, iv lowercase→generic)`. The 3 FAIL→PASS transition on the same assertions is the non-tautology proof; (i)/(iv) guard the unchanged strict-accept + generic-fallthrough paths so the diagnostic cannot over-reach.
- **Notes**: catalogued as shippability row 43 (m2) so its regression is caught by the Step 5.5 runner — closes the slice-038→R-10 ~5-slice detection-latency class for this slice's own pin.

### AC4: R-6 transitions open → retired via the `**Status**:` field flip + `**Retired**:` line
- **Status**: PASS
- **Evidence**: `tools.risk_register_audit architecture/risk-register.md --json` → `R-6 status: retired`. R-6 absent from `--filter-status open` (was present pre-slice — genuine contrast, BC-PROJ-4 in build-log). `by_status` retired 6→7, open 2→1. The `**Status**: open` field line was flipped to `**Status**: retired` AND a verbose `**Retired**: slice-043-… (2026-05-18; [[ADR-046]])` line added (R-4/R-5 precedent shape; M2 mechanic). R-6 went open→retired directly (no `mitigating` intermediate).
- **Notes**: M1/M2 ACCEPTED-FIXED at TRI-1 were correctly applied — the `mitigating` filter axis was dropped; the parsed-status surface (`**Status**:`) was the one flipped.

## Multi-instance validation
**Required?**: no
**Result**: not-applicable
**Evidence**: slice-043 modifies a local read-only audit's rejection message + a project doc + a test. No multi-user / multi-device / multi-account surface.

## VAL-1 layered safety checks
- **Layer A (credential scan, Critical)**: clean — no secrets in changed files (`tools/branch_workflow_audit.py`, `CLAUDE.md`, the new test module).
- **Layer B (dependency hallucination, Important)**: clean — no hallucinated imports (`--imports-allowlist tests`; the test module imports `tools.branch_workflow_audit` + `tests.methodology.conftest`, both resolve).

## Shippability catalog regression check
- **SCMD-1 pre-gate**: clean — 43 rows; 436 cited fns; incidental=0, essential_registered=2, essential_unregistered=0. New row 43's tests are not incidental-coupled.
- **PTFCD-1 sub-mode (b) pre-gate**: clean — 43 rows, 269 test-path tokens, all files + cited functions exist (row 43's cited modules resolve).
- **Catalog runner** (`tools.shippability_runner`, canonical): **43 rows, 43 PASS, 0 FAIL**. No past slice broken by slice-043; the new row 43 passes alongside all 42 prior rows.

## Reality surprises
- None. The `.gitignore:11` discovery (entire `architecture/` vault gitignored — local-only by design) was anticipated by the repo model (R-4 entry documented the same for build-checks.md); not a surprise, recorded in build-log for clarity. The tracked slice deliverable is 3 files; vault artifacts are local working memory.
