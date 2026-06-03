# Validation: Slice 106 route-project-frame-synth-via-vault-root

**Date**: 2026-06-03
**Result**: PASS

This is an internal-tooling routing slice (no UI, no multi-user/device, no real-device target). "Real environment" = the live repo: the actual `vault_flip_readiness_audit` run against the real tree, the actual `project_frame_synth` frame output, and the full shippability catalog executed via the pinned SRSC-1 runner.

## Per-criterion results

### AC1: all 4 vault-path constructions in `project_frame_synth.py` resolve through `VAULT_ROOT`; no bare `"architecture"` path-construction literal remains
- **Status**: PASS
- **Evidence**: `python -m tools.vault_flip_readiness_audit --json` → `production must-rewrite count: 0`, `entries: []` (was 4, all `tools/project_frame_synth.py`). The 4 reads (`concept.md`/`triage.md`/`slice-queue.md`/`risk-register.md`) now compose `repo_root / VAULT_ROOT / "<file>"`. The 2 surviving `architecture/` literals (docstring CLI example, argparse `help=`) are prose, classified `doc-example-safe` by the audit (code-review m1 — backstopped, not silent path mis-resolves).
- **Notes**: `methodology-changelog.md` read (L157) correctly left unrouted — it lives at repo-root, not under the vault (verified `architecture/methodology-changelog.md` does not exist).

### AC2: `vault_flip_readiness_audit` reports 0 `[production] must-rewrite`; `_BASELINE` + `test_must_rewrite_baseline_pinned` updated; `--strict` exits 0
- **Status**: PASS
- **Evidence**: summary line `[production] 0 must-rewrite`; `_BASELINE = ()`; `vault_flip_readiness_audit --strict` → **exit 0** (no baseline drift); `test_must_rewrite_baseline_pinned` PASS (`live == tuple(sorted(_BASELINE))`, both empty).

### AC3: `project_frame_synth` produces byte-identical output before vs after (pure no-op under default `VAULT_ROOT`)
- **Status**: PASS
- **Evidence**: same-worktree-vault before/after isolation — pre-routing capture SHA256 `97340A02…` == post-routing == validation re-capture `97340A02…` (`AC3 byte-identical: True`). The routing changes only *which directory constant* composes the path; with `VAULT_ROOT == Path("architecture")` the resolved path is byte-identical to the old `repo_root / "architecture" / "X"`. `tests/methodology/test_project_frame_synth.py` (the standing byte-identity fixture guard) PASS.

### AC4: `project_frame_synth.py` joining `_MIGRATION_SITE_ALLOWLIST` brings it under the existing slice-068 guards; no new test file; non-vacuous by mutation
- **Status**: PASS
- **Evidence**: `tests/methodology/test_vault_root_constant.py` PASS (`test_migration_site_allowlist_pinned` — allowlist now 16 == actual VAULT_ROOT importers; `test_no_orphan_architecture_literal_in_migrated_tools` — no orphan literal; `test_full_pytest_baseline_preserved` — `test_count == 15` untouched, no new test function). Mutation non-vacuity proven by `test_new_unrouted_literal_fails_gate` (synthetic injected bare-`architecture` `/`-BinOp → MUST_REWRITE) — PASS. No new test file introduced.

### AC5: full methodology suite green; `architecture/shippability.md` unregressed; no new catalog row
- **Status**: PASS
- **Evidence**: full suite **1529 passed / 0 failed** (at `/build-slice` Step 6, re-confirmed). Shippability catalog via the pinned SRSC-1 runner: **111 rows, 111 PASS, 0 FAIL**. Pre-gates SCMD-1 / PTFCD-1 / SVW-1 all exit 0. **No new catalog row** added — the extended guard set is covered by the existing slice-068 `test_vault_root_constant.py` row (per design.md §AC4/AC5 + meta-Critic confirmation).

## Layered safety checks (VAL-1)
- **Layer A (credential scan)**: PASS — no secrets in the 5 changed `.py` files.
- **Layer B (dependency hallucination)**: PASS — the one new import `from tools._vault_paths import VAULT_ROOT` resolves to the project's own `tools` package; no hallucinated/undeclared dependency. (`validate_slice_layers … --imports-allowlist tests` → exit 0.)

## Walking-skeleton (WS-1) / Exploratory-charter (ETC-1)
- Not applicable — mission-brief declares both `false`. Audits exit 0 (clean).

## Multi-instance validation
- **Required?**: no — internal tooling; no multi-user / multi-device / multi-account surface (mission-brief Authorization model: N/A).
- **Result**: not-applicable.

## Reality surprises
- None at validation. (One enumeration gap surfaced earlier, at `/build-slice` — the 2nd VAULT_ROOT-importer count-pin in `test_external_vault_adr_and_risk.py` that neither Critic pass caught; fixed in-slice, logged as an AP-10 `/critic-calibrate` signal for `/reflect`. Not a validation-time surprise.)

## Shippability regressions
- None. 111/111 PASS.
