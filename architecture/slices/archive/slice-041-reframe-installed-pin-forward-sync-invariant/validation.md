# Validation: Slice 041 reframe-installed-pin-forward-sync-invariant

**Date**: 2026-05-18
**Result**: PASS

> Tooling/audit slice — "real environment" = running the actual shipped tools/audits against the real repo artifacts (the slice's deliverables ARE executable controls; this is the BC-PROJ-4 dogfood class). Every AC validated by executing the real artifact, not by reasoning.

## Per-criterion results

### AC1: A non-catalog forward-sync control ships (content-equal modulo EOL, non-opt-out gate, regression-tested)
- **Status**: PASS
- **Evidence**: `$PY -m tools.methodology_changelog_forward_sync` → `MCFS-1 … PASS — in-repo methodology-changelog.md is content-equal modulo line endings to the installed copy`. `pytest test_methodology_changelog_forward_sync.py` → **8 passed** (synced→0 / divergent→1 / installed-absent→WARN 0 / CRLF-only→0 / empty-present→1 / CSP-1 normalization-parity / M-add-1 relocation-proof). Non-opt-out wiring present: `grep -c methodology_changelog_forward_sync skills/build-slice/SKILL.md` = 2 (Step-6 checklist line + ungated subsection), `skills/reflect/SKILL.md` = 1 (NEW Step 5b-fs, NOT folded into rule-promotion-gated Step 5b).
- **Notes**: BCI-1-shaped; local 1-line CRLF→LF norm, CSP-1 behaviour-parity-pinned to `tests/skill_drift_equality.py::_normalized_sha256` (no tools→tests import).

### AC2: The new control is provably NOT a shippability-catalog-cited fn (M-add-1 relocation guard)
- **Status**: PASS
- **Evidence**: `pytest …::test_mcfs1_module_is_non_catalog_relocation_proof` → **1 passed** — executed `scda.audit()` over the REAL catalog: MCFS-1 module ∉ any resolved qual (incidental/essential/clean); and the Machine-cmd column (6th cell) of every data row contains no `methodology_changelog_forward_sync` reference. `_TEST_PATH_RE = tests/\S+?\.py` structurally cannot match `tools/*` (DR-1-confirmed).
- **Notes**: Row #41's *Critical-path prose* legitimately names the tool (description of what the row guards); the invariant is correctly scoped to the executable Machine-cmd column, not raw catalog text.

### AC3: The audit-derived in-module essential fns no longer read untracked installed; decouple complete
- **Status**: PASS
- **Evidence**: `shippability_decoupling_audit --json` → exit 0, `violation_count=0`, `essential_registered`=[the cross-module LAYER-EVID-1 pin], `essential_unregistered`=**[]**. The 37 in-module fns (33 cited + 4 defined-but-uncited v43/45/47/48) had the installed-changelog read-leg dropped in BOTH syntactic forms (17 bare `installed_path =` + 20 inline `.read_text()`; m-add-1). `test_methodology_changelog.py` 77/77 → all in-repo assertions retained.
- **Notes**: Worklist regenerated from live `--json` `essential`, not hand-copied (m2 discharged).

### AC4: SCMD-1 essential class reframed to a closed-world non-empty registered intentional-installed allowlist
- **Status**: PASS
- **Evidence**: `pytest` (3 tests) → **3 passed**: `test_unregistered_essential_fn_is_flagged_closed_world` (self-contained synthetic installed-reader ⇒ `essential-unregistered` violation exit 1), `test_registered_essential_pin_is_accounted_for_not_flagged` (the slice-019 cross-module pin ⇒ `essential_registered`, not flagged), `test_registered_key_resolves_against_real_catalog` (V3 — every `_REGISTERED_INSTALLED_READERS` key resolves to an `essential_registered` fn over the real catalog; fail-open guard). `_REGISTERED_INSTALLED_READERS` non-empty (1 entry + rationale; ADR-043). MCFS-1 tool non-catalog by construction (AC2).
- **Notes**: This is the R-4 charter's literal "the read **registered** not **absent**"; rev-1's empty-allowlist was charter-divergent (3-revision critique convergence).

### AC5: R-4 escalated to retired; risk_register_audit reflects it; full shippability catalog no regression
- **Status**: PASS
- **Evidence**: `risk_register_audit --filter-status retired` → R-4 present (True); `--filter-status mitigating` → R-4 absent (False). `grep -c '**Retired**: slice-041' risk-register.md` = 1 (with 030A/030B/030C lineage). Shippability catalog: SCMD-1 pre-gate exit 0 (41 rows, essential_registered=2, essential_unregistered=0), PTFCD-1(b) path audit exit 0 (41 rows, 261 tokens, all exist), **canonical runner: 41 row(s), 41 PASS, 0 FAIL**.
- **Notes**: The essential-class false-PCA-1-HALT window is closed; the slice-030 split (030A→030B→030C) is complete.

## Step 5b — VAL-1 layered safety checks
- **Layer A (credential scan, Critical)**: clean
- **Layer B (dependency hallucination, Important)**: clean
- **Evidence**: `validate_slice_layers --slice … --changed-files <8 files> --imports-allowlist tests` → "Clean — both layers passed."

## Step 5c / 5d
- WS-1: N/A (`Walking-skeleton: false`)
- ETC-1: N/A (`Exploratory-charter: false`)
- TF-1: N/A (`Test-first: false`)

## Step 5.5 — Shippability catalog regression check
- **Pre-gate a (SCMD-1)**: exit 0 — clean, 41 rows, incidental=0, essential_registered=2, essential_unregistered=0
- **Pre-gate b (PTFCD-1/PTFFD-1 path audit)**: exit 0 — clean, 41 rows, 261 test-path tokens, all files + cited functions exist
- **Canonical runner** (`tools.shippability_runner`): **41 row(s), 41 PASS, 0 FAIL**
- No regression. The slice's own critical path is row #41 (cites the in-repo-only entry-pin + consumer-propagation pin only — m-add-2 negative invariant).

## Multi-instance validation
**Required?**: no (no multi-user/device/account surface — read-only audit tooling + a deterministic local-file forward-sync gate)
**Result**: not-applicable

## Reality surprises
None. The rev-3 structural-pivot design executed exactly as the rev-3 DR-1 verified by execution: post-decouple essential set = exactly the single registered cross-module pin (cardinality-1), audit exit 0, R-4 retireable. The 4 pre-finish test harmonizations (build-log 14:05) were the anticipated slice-039 same-fix-block class (the slice's own decouple/retire invalidated its own + one older pin), not surprises — all foreseen in the rev-3 critique loop.
