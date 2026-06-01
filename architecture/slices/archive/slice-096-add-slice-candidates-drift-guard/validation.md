# Validation: Slice 096 add-slice-candidates-drift-guard

**Date**: 2026-06-01
**Result**: PARTIAL

> All 5 acceptance criteria PASS with evidence and VAL-1 is clean — the slice's own deliverable is fully validated. The aggregate is PARTIAL **only** because the shippability catalog caught **one** pre-existing regression (`test_reflect_skill_drift`) that is **NOT attributable to slice-096** — it is risk **R-28** (parallel `~/.claude/`-install contention from the in-flight slice-095). This needs a user-approved deferral decision (Step 5.5) before `/reflect`.

## Per-criterion results

### AC1: New per-skill drift test asserts content-equality via the shared `assert_md_forward_synced`
- **Status**: PASS
- **Evidence**: `tests/methodology/test_slice_candidates_skill_drift.py` created; `pytest …test_slice_candidates_skill_drift.py` → `1 passed in 0.07s`. Imports resolve (`tests.methodology.conftest.REPO_ROOT`, `tests.skill_drift_equality.assert_md_forward_synced`); collects cleanly; consumes the shared comparator unchanged.

### AC2: CLAUDE.md OSDG-1 enumeration names `slice-candidates` + its test
- **Status**: PASS
- **Evidence**: `CLAUDE.md:42` now reads "Extended at slice-096 (R-13) to **`slice-candidates`** (`tests/methodology/test_slice_candidates_skill_drift.py`) — the **last named-but-unguarded member of THIS OSDG-1 family**, NOT a total-skill-coverage claim …" (narrowed per /code-review m1). `Select-String` confirms the skill + test are co-enumerated on the OSDG-1 bullet.

### AC3: The drift test PASSES + is non-vacuous (proven by mutation)
- **Status**: PASS
- **Evidence**: BC-PROJ-3-compliant non-vacuity demo (temp-copy swap, NOT git checkout): mutate in-repo `skills/slice-candidates/SKILL.md` → `1 failed` (exit 1; genuine-drift AssertionError naming both EOL-normalized sha256 hashes); restore from temp-copy → `1 passed` (exit 0); `Get-FileHash` pre==post = **True** (byte-exact restore). Re-run at validation time, same result.

### AC4: Guard wired into the gate roster + shippability row (RPCD-1 / SCPD-1)
- **Status**: PASS
- **Evidence**: row #102 in `architecture/shippability.md` (full 6-column SCMD-1 shape). `shippability_decoupling_audit` (SCMD-1) → clean (101 rows, 0 incidental coupling). `shippability_path_audit` (PTFCD-1) → clean (447 path tokens, the new test among them, all resolve). The test runs under the `tests/methodology/` suite `/validate-slice` invokes.

### AC5: No regression; the 13 existing guards behave identically; MEPD-1 decided + recorded; no unintended RULE-ID / VERSION churn
- **Status**: PASS
- **Evidence**: `tests/methodology/` → **1176 passed** (the 13 existing per-skill drift guards behave identically). MEPD-1 = EXCLUDE recorded in design.md §Sub-decisions. `git diff` confirms `VERSION` / `methodology-changelog.md` / `plugin.yaml` / `tools/install_audit.py` are **UNCHANGED** (EXCLUDE held — no version/changelog churn). The lone methodology-suite failure (`test_external_vault_adr_and_risk`) is pre-existing on master (slice-093 archival stale path), unrelated — see build-log D1.

## VAL-1 layered safety checks (Step 5b)
- **Layer A (credential scan)**: 0 secrets. PASS.
- **Layer B (dependency hallucination)**: 0 import findings (the test's `tests.*` imports resolve via `--imports-allowlist tests`). PASS.
- Command: `validate_slice_layers --slice … --changed-files test_slice_candidates_skill_drift.py CLAUDE.md shippability.md --imports-allowlist tests` → "Clean — both layers passed."

## Multi-instance validation
- **Required?**: no (test-only methodology guard; no multi-user / multi-device / sync surface).
- **Result**: not-applicable.

## Shippability catalog (Step 5.5)

**Run**: `shippability_runner architecture/shippability.md` → **100 PASS, 1 FAIL** of 101 rows.

### Shippability regressions
- **`test_reflect_skill_drift.py::test_in_repo_and_installed_reflect_skill_md_are_content_equal` — FAIL.**
  - **Cause classification**: reality surprise → **R-28 (parallel `~/.claude/`-install contention)**, NOT a slice-096 regression.
  - **Evidence (hash attribution)**: in-repo `skills/reflect/SKILL.md` is byte-identical across master, the slice-096 worktree, AND the slice-094 worktree (sha256 `CEF4B3CC…`) — slice-096 does not touch reflect. The **installed** `~/.claude/skills/reflect/SKILL.md` (sha256 `F435D06B…`) matches **only the slice-095 worktree's** reflect SKILL.md. So the in-flight, unmerged **slice-095** (`harden-skill-driven-vault-writes`, which edits reflect's vault-mutation surface) forward-synced its version into the shared global install, making every other slice's reflect content-equality row report drift. The row **also FAILs on clean master** (verified by isolated run in the main repo) — proving it is not introduced by slice-096.
  - **Why slice-096 must NOT fix it**: forward-syncing reflect from slice-096 would overwrite slice-095's in-flight installed copy and touch a SKILL.md surface outside slice-096's scope — breaking the independence this slice was scoped to preserve. The drift self-resolves when slice-095 merges (master's reflect becomes `F435D0…` and the row matches the install) or when the install is reconciled to master.
  - **Disposition**: **deferral APPROVED by user (2026-06-01)** per Step 5.5. The reflect-drift FAIL is R-28 (slice-095's shared-install forward-sync), not a slice-096 regression; it self-resolves when slice-095 merges. `/reflect` will register this as a fresh witnessed occurrence of R-28 (the risk has now bitten a third slice's validation) and route the reflect install reconciliation to slice-095's merge. slice-096's own deliverable is fully validated (5/5 ACs PASS).

## Reality surprises
- **R-28 materialized during slice-096 validation** — a parallel slice's forward-sync of the shared `~/.claude/` install caused a false drift signal on an unrelated skill (reflect) in slice-096's shippability run. Strengthens the case for the R-28 mitigation (per-worktree install isolation, or content-equality against the slice's own base rather than the shared global install). Impact on next slice: the external-vault flip + any forward-sync-bearing slice should account for shared-install contention while N parallel slices are in flight.
