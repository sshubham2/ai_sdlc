# Validation: Slice 031 complete-shippability-decoupling (split-label 030B)

**Date**: 2026-05-17
**Result**: PARTIAL — all 5 slice ACs PASS with evidence; shippability catalog 29/31 PASS with 2 FAILs that are a SINGLE pre-existing R-5/D-1 CRLF artifact (slice-031-innocent), requiring user-approved deferral per Step 5.5 (slice-030A precedent).

## Per-criterion results

### AC1: all-rows mechanical derivation + incidental decoupled + closed-world allowlist
- **Status**: PASS
- **Evidence**: `$PY -m tools.shippability_decoupling_audit architecture/shippability.md` → *"SCMD-1 audit: clean. 31 row(s); 343 cited fn(s) — incidental=0 essential=31 (recognized, 030C) clean=312."* (derivation spans all 31 rows, not a hand-coded subset). `pytest test_shippability_decoupling_audit.py::{test_cited_fn_set_derived_from_all_rows_not_enumerated, test_no_incidental_cited_fn_remains_coupled, test_indirected_path_home_read_is_caught, test_allowlist_membership_is_exactly}` → 4 passed.
- **Notes**: closed-world catches constant + same-module-helper indirection; allowlist pinned by identity (rename trips loudly).

### AC2: non-vacuous environment-independence (fn granularity; #8/#12 explicit non-goal)
- **Status**: PASS
- **Evidence**: `pytest ::test_decoupled_incidental_fns_classify_clean ::test_decoupled_incidental_fns_have_no_exists_skip_guard` → 2 passed. The 10 decoupled `test_build_checks_audit.py` backtests + `test_validate_slice_layers.py::test_slice_002_archive_replay` classify `clean` and contain no `if _GLOBAL_BUILD_CHECKS.exists():` skip guard (hard-assert; M4). Mixed rows #8/#12 documented in mission-brief as an explicit per-row non-goal (essential entry-pin co-citation → 030C).

### AC3: machine-stable command column + runner/PTFCD-1 repoint
- **Status**: PASS
- **Evidence**: `pytest test_shippability_command_column.py test_validate_slice_skill.py::test_step4_5_5_consumes_machine_stable_command` → 6 passed (incl. M-add-A leading-bareword-prose=violation + two-clean-`;`=pass + interpreter-anchored segment regex). shippability.md header = 6 columns; `shippability_path_audit` reads `cells[5]` with non-silent fallback (B3); SKILL.md Step 5.5 runner + SCMD-1 non-opt-out pre-catalog gate + PTFCD-1-reads-Machine-cmd prose pinned.

### AC4: ADR-030 verbatim corpus derived-not-listed + bidirectional completeness
- **Status**: PASS
- **Evidence**: `pytest ::test_every_derived_archive_folder_has_tracked_corpus_fixture` → 1 passed. Corpus = 8 folders (slice-001/002/003/004/005/006/007/011) verbatim mission-brief+design; membership = the runtime derivation (slice-001 included — the M3 fix); forward (no missing) + reverse (no orphan, v2-m2) both asserted.

### AC5: methodology propagation clean
- **Status**: PASS
- **Evidence**: `pytest test_methodology_changelog.py::test_v_0_45_0_scmd_1_entry_present_in_repo_and_installed test_risk_register_audit_real_file.py::test_r_4_subentry_charters_030c_and_stays_mitigating` → 2 passed. `$PY -m tools.plugin_manifest_audit` → *"clean. 24 skill(s), 5 agent(s), 22 tool(s); version 0.45.0."* INST-1/BCI-1/CAD-1/CSP-1(n/a Std)/DR-1/UTF8-STDOUT-1/PCA-1/BRANCH-1/CRP-1/WIRE-1/TF-1(18/18 PASSING) all green (build-log Pre-finish gate). R-4 verified `mitigating` (NOT retired); R-4 sub-entry charters slice-030C + carries M-add-1; changelog v0.45.0 in-repo + installed forward-synced.

## VAL-1 layered safety (Step 5b)
`$PY -m tools.validate_slice_layers --slice … --changed-files … --imports-allowlist tests` → *"0 secret(s), 0 import finding(s), 0 suppressed. Clean — both layers passed."* exit 0.

## WS-1 / ETC-1
Not applicable — mission-brief declares `**Walking-skeleton**: false`, `**Exploratory-charter**: false`.

## Multi-instance validation
**Required?**: no (methodology-tooling slice; no multi-user/device/account surface).
**Result**: not-applicable.

## Shippability catalog regression (Step 5.5)

Pre-catalog gates: SCMD-1 clean (incidental=0) ✓; PTFCD-1 clean (31 rows, 216 tokens exist) ✓.

**Catalog run: 31 rows, 29 PASS, 2 FAIL.**

### Shippability regressions
Both FAILs (row #1 slice-001, row #19 slice-019) are the **same single test**:
`tests/skills/diagnose/test_diagnose_skill_drift.py::test_in_repo_and_installed_diagnose_skill_md_are_content_equal`

- **Cause**: **reality surprise / pre-existing environment artifact — R-5 / D-1** (NOT an implementation bug, NOT a slice-031 regression).
- **slice-031 innocence (proven)**:
  - `skills/diagnose/SKILL.md` is **git-untouched** by slice-031 (`git status --porcelain` — not in the changed set; slice-031 touched `validate-slice/SKILL.md`, never `diagnose/SKILL.md`).
  - `skills/diagnose/SKILL.md`: raw bytes in-repo ≠ installed (sha256 differs) BUT **CRLF-normalized content is byte-identical** (`a.replace(b"\r\n",b"\n") == b`); in-repo has CRLF (Windows working-tree autocrlf), installed has LF. The drift test does a raw-byte sha256 compare with no line-ending normalization → spurious FAIL on a Windows checkout.
  - This is the **exact R-5 signature** discovered in slice-030A (reflection D-1/R-5) and the **exact rows #1/#19 + exact test** slice-030A **user-approved-deferred** ("spurious CRLF/LF artifact, content byte-identical, slice-030A verified innocent; not a real regression. Tracked by R-5/D-1").
- **In scope?**: NO. slice-031 mission-brief "Out of scope" explicitly excludes R-5/D-1 CRLF normalization ("`fix-skill-drift-test-crlf-normalization` … separate backlog slice … 030B MUST NOT absorb it; doing so re-creates the scope-creep the user-approved split deliberately prevented"). The R-5 exclusion was ratified at the slice-031 TRI-1.
- **Action**: requires **explicit user-approved deferral** at this PCA-1 validate gate (Step 5.5; mirrors slice-030A's handling exactly). Tracked by risk-register **R-5**. Followup: standalone backlog slice `fix-skill-drift-test-crlf-normalization`. **Do NOT fix here** (scope discipline — the very flaw-relocation the b-split prevented).

## Reality surprises
- None new. The R-5 CRLF false-FAIL is a **known, tracked, recurring** artifact (risk-register R-5, slice-030A D-1) — not a new surprise. Its recurrence on rows #1/#19 is N+1 evidence for the chartered `fix-skill-drift-test-crlf-normalization` backlog slice (normalize line endings in all `test_*_skill_drift.py` raw-byte compares, or `.gitattributes` `*.md text eol=lf`).

## Aggregate disposition
slice-031's own deliverable is **fully validated** (5/5 ACs PASS with evidence; VAL-1 clean; all Step-6 audits green). The only catalog non-PASS is the pre-existing, slice-innocent, mission-brief-out-of-scope, slice-030A-precedented R-5 CRLF artifact. **Result = PARTIAL** at the catalog layer; slice-031-deliverable disposition = PASS.

## User-approved deferral (PCA-1 validate gate, 2026-05-17)
**Triaged by**: user. **Decision**: APPROVE R-5 deferral → proceed to /reflect.
Rationale ratified: slice-031 is innocent (diagnose SKILL.md git-untouched; content byte-identical CRLF-normalized); R-5 is pre-existing, tracked, and explicitly out-of-scope per the TRI-1-ratified mission-brief; identical rows #1/#19 + test were user-approved-deferred at slice-030A. The R-5 CRLF normalization is chartered to the standalone backlog slice `fix-skill-drift-test-crlf-normalization` (NOT absorbed here — preserves the b-split's anti-relocation discipline). `/reflect` records the deferral + R-5 N+1 recurrence evidence. Gate resolved; auto-advance to `/reflect` permitted.
