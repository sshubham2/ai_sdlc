# Slice 068: add-vault-root-constant

**Mode**: Standard
**Estimated work**: 0.5 day (small)
**Risk retired**: none directly; **unblocks** slice-069 (`rename-architecture-to-sdlc-and-track-in-git`) — the cross-machine-parallel-development chain surfaced during `/query-design` 2026-05-25 cannot proceed without a single seam to route every `"architecture/"` literal through
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Introduce a single `VAULT_ROOT: Path` constant in a new `tools/vault_paths.py` module (default `Path("architecture")`, overridable via env var `AI_SDLC_VAULT_ROOT`) and route every filesystem-resolving `"architecture/"` / `"architecture\\"` literal in `tools/*.py` through it. **Pure refactor — zero behavior change.** The slice ships the seam only, not the rename — so the planned slice-069 (`rename-architecture-to-sdlc-and-track-in-git`) becomes a 1-line config change instead of a chaotic global find/replace across 14 Python files. Without this prerequisite, slice-069's blast radius is unmanageable; with it, the rename is a constant-default flip + a `.gitignore` edit.

## Acceptance criteria

1. New `tools/vault_paths.py` module exports `VAULT_ROOT: Path` defaulting to `Path("architecture")`, overridable via env var `AI_SDLC_VAULT_ROOT` (when set, `VAULT_ROOT == Path(os.environ["AI_SDLC_VAULT_ROOT"])`); the module is the single source of truth for vault-relative path construction in `tools/`.
2. Every filesystem-resolving `Path("architecture")` / `"architecture/..."` / `"architecture\\..."` literal in `tools/*.py` routes through `VAULT_ROOT`. Migration is **scoped to filesystem-resolving literals only** — methodology test-fixtures and audit-tools that grep changelog/skill prose for the literal string `"architecture/"` (e.g. `tests/methodology/test_methodology_changelog.py` rule-reference matchers, BC-1 keyword-precision tests) are **NOT migrated** — they assert on prose text, not paths. **Two-marker convention** (per /critique-review M-add-1 ACCEPTED-FIXED): migrated sites carry `# VAULT_ROOT-routed (slice-068)` inline; the 5 enumerated error-message-string EXCLUDED sites (`cross_spec_parity_audit.py:335`, `state_transition_pin_audit.py:374,388,400`, `validate_slice_layers.py:521`) carry `# NOT VAULT_ROOT-routed (slice-068) — error-message prose` inline. Both marker forms are accepted by the `test_no_orphan_architecture_literal_in_migrated_tools` audit (design.md TF-1 row 4) so future readers can audit the scope cleanly without false flags on the deliberately-preserved error-message-prose class.
3. No behavior change: full pytest suite passes at slice end with byte-equivalent stdout/stderr modulo timestamps (baseline preserved per current 899/899 pass count from slice-067); idempotent — running the migration step a second time produces an empty diff. The constant-routing refactor MUST NOT alter any observable behavior, error message, or audit-tool exit code.
4. New unit test `tests/methodology/test_vault_root_constant.py` asserts: (a) `VAULT_ROOT == Path("architecture")` by default; (b) `AI_SDLC_VAULT_ROOT=/tmp/foo` env override resolves to `Path("/tmp/foo")` via subprocess fixture (env-var injection at process boundary, not in-process monkeypatch — env vars are read at module import); (c) a deterministic grep-style audit asserts every `tools/*.py` module previously hardcoding `Path("architecture")` now imports `VAULT_ROOT` from `tools._vault_paths` (pinned `_MIGRATION_SITE_ALLOWLIST` of **8 `tools/*.py` modules** — corrected per /critique B1 ACCEPTED-FIXED to add `build_checks_integrity.py:78` (missed by rev-1 grep) and per /critique M3 ACCEPTED-FIXED to scope back `tests/methodology/conftest.py` to DEFERRED for a follow-on slice; the final 8-element allowlist: `build_checks_integrity.py`, `critique_review_prerequisite_audit.py`, `cross_spec_parity_audit.py`, `risk_register_audit.py`, `slice_queue_writer.py`, `state_transition_pin_audit.py`, `supersede_audit.py`, `validate_slice_layers.py`); (d) **NEW per /critique M1 ACCEPTED-FIXED** — `test_consumer_constants_are_frozen_at_first_import` empirical regression-pin verifies that `tools.slice_queue_writer._INDEX_MD_REL` does NOT update after in-process `monkeypatch.setattr(tools._vault_paths, "VAULT_ROOT", ...)` — documents the production-correctness freeze contract as load-bearing semantic, not a defect.

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0). Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_vault_root_constant.py | test_vault_root_module_exports_constant | PASSING |
| 1 | unit | tests/methodology/test_vault_root_constant.py | test_vault_root_default_equals_path_architecture | PASSING |
| 2 | unit | tests/methodology/test_vault_root_constant.py | test_all_tools_modules_import_vault_root | PASSING |
| 2 | unit | tests/methodology/test_vault_root_constant.py | test_no_orphan_architecture_literal_in_migrated_tools | PASSING |
| 2 | unit | tests/methodology/test_vault_root_constant.py | test_shippability_decoupling_audit_tuples_preserve_literal | PASSING |
| 3 | regression | tests/methodology/test_vault_root_constant.py | test_full_pytest_baseline_preserved | PASSING |
| 3 | unit | tests/methodology/test_vault_root_constant.py | test_migration_is_idempotent | PASSING |
| 4 | unit | tests/methodology/test_vault_root_constant.py | test_env_var_override_via_subprocess | PASSING |
| 4 | unit | tests/methodology/test_vault_root_constant.py | test_migration_site_allowlist_pinned | PASSING |
| 4 | unit | tests/methodology/test_vault_root_constant.py | test_consumer_constants_are_frozen_at_first_import | PASSING |

Per /critique M1 ACCEPTED-FIXED: row 10 added — empirical regression-pin documenting the production-correctness freeze contract (in-process monkeypatch of `tools._vault_paths.VAULT_ROOT` does NOT propagate to already-frozen downstream consumer constants like `tools.slice_queue_writer._INDEX_MD_REL`). Per /critique B1 + M3 ACCEPTED-FIXED: row 5 renamed from `test_methodology_changelog_test_fixtures_preserve_literal` to `test_shippability_decoupling_audit_tuples_preserve_literal` (the test-tree-fixture pin was DEFERRED with the rest of tests/ migration; the surviving regression-pin is for the in-tools AST-pattern allowlist that MUST stay literal).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | `tools/vault_paths.py` exports `VAULT_ROOT` + env override | `python -c "from tools.vault_paths import VAULT_ROOT; print(VAULT_ROOT)"` prints `architecture`; `AI_SDLC_VAULT_ROOT=/tmp/x python -c "..."` prints `/tmp/x`. |
| 2 | All filesystem-resolving literals migrated; prose-asserting tests untouched | `grep -rn 'Path("architecture")\|"architecture/' tools/` returns only `tools/_vault_paths.py` (the constant definition) + 8 sites carrying the `# VAULT_ROOT-routed (slice-068)` marker + 5 enumerated EXCLUDED error-message-string sites carrying the `# NOT VAULT_ROOT-routed (slice-068) — error-message prose` marker (per /critique-review M-add-1 ACCEPTED-FIXED two-marker convention) + `shippability_decoupling_audit.py:91-92` AST-pattern allowlist tuples (preserved verbatim, pinned by `test_shippability_decoupling_audit_tuples_preserve_literal`). `tests/methodology/test_methodology_changelog.py` literal-string matchers UNCHANGED (verified by diff; all `tests/` migration DEFERRED per /critique M3 ACCEPTED-FIXED). |
| 3 | No behavior change | `$PY -m pytest -x` exits 0 with same pass count as slice-067 baseline (899) + slice-068 added 10 tests per /critique M1 ACCEPTED-FIXED = 909/909 target; re-running the migration helper on the already-migrated tree produces empty git diff. |
| 4 | Test suite asserts seam + allowlist | `$PY -m pytest tests/methodology/test_vault_root_constant.py -v` — all **10** tests PASS (per /critique M1 ACCEPTED-FIXED adding the freeze-pin row); subprocess env-var test runs on Windows + POSIX. |

## Must-not-defer

- [ ] **Idempotency of migration**: running the constant-routing transformation twice produces an empty diff. Migration must be a fixed-point. (Documented at the helper site if scripted; if hand-edited, the test_migration_is_idempotent test pins this by re-applying the migration and asserting no change.)
- [ ] **Distinguish filesystem-paths from prose-assertions** (two-marker convention per /critique-review M-add-1 ACCEPTED-FIXED): `tests/methodology/test_methodology_changelog.py` greps for the literal STRING `"architecture/"` in changelog/skill prose — those literals MUST NOT be migrated (and the entire test-tree migration is DEFERRED per /critique M3 ACCEPTED-FIXED, so they remain untouched). The two-marker convention is load-bearing: every migrated `tools/*.py` site carries `# VAULT_ROOT-routed (slice-068)`; the 5 enumerated EXCLUDED error-message-string sites (`cross_spec_parity_audit.py:335`, `state_transition_pin_audit.py:374,388,400`, `validate_slice_layers.py:521`) carry `# NOT VAULT_ROOT-routed (slice-068) — error-message prose`. A missed `# VAULT_ROOT-routed` marker on a migrated site is a slice-068 violation; a missed `# NOT VAULT_ROOT-routed` marker on an EXCLUDED error-message-string site will fail `test_no_orphan_architecture_literal_in_migrated_tools` (design.md TF-1 row 4 accepts EITHER marker form per the two-marker convention).
- [ ] **Windows + POSIX path semantics**: use `pathlib.Path`, not string concat; env-var override must resolve correctly on both `C:\Users\...` and `/tmp/...` shapes. Subprocess test covers the env-var-at-import edge.
- [ ] **No new circular imports**: `tools/vault_paths.py` MUST NOT import from other `tools/` modules (it is the leaf). Verified by an explicit `ast.parse` test asserting the module's imports are stdlib-only.
- [ ] **Forward-sync SKILL.md prose UNTOUCHED**: SKILL.md files reference `architecture/` in user-facing documentation prose (e.g. `architecture/slices/_index.md`, `architecture/risk-register.md`). Those are NOT migrated — they're docs describing the default layout, not code resolving paths. Drift-guards OSDG-1 / mini-CAD remain quiescent.
- [ ] **No SKILL.md edits at all** — this slice changes zero skill markdown. Confirmed pre-finish by `git diff --stat skills/ agents/` returning empty.
- [ ] **CAD-1 + PMI-1 + OSDG-1 audits remain quiescent** — no agent edits, no SKILL.md edits, no plugin.yaml changes; VERSION bump posture deferred to /design-slice per MEPD-1 Inclusion-heuristic (likely NO bump — pure mechanical refactor, no rule mint, no new audit surface).
- [ ] **The 8-module migration allowlist is exhaustive** (corrected per /critique B1 ACCEPTED-FIXED from rev-1's "7" — `build_checks_integrity.py:78` was missed by the original grep; per /critique M3 ACCEPTED-FIXED `tests/methodology/conftest.py` is scoped-back to DEFERRED for a follow-on slice) — the `test_migration_site_allowlist_pinned` test asserts every existing `tools/*.py` module hardcoding `Path("architecture")` is in the 8-element allowlist `{build_checks_integrity.py, critique_review_prerequisite_audit.py, cross_spec_parity_audit.py, risk_register_audit.py, slice_queue_writer.py, state_transition_pin_audit.py, supersede_audit.py, validate_slice_layers.py}`. New tool modules added after slice-068 inherit the same constraint via this test (it greps fresh). The /critique B1 lesson: a pre-slice-068 grep that produced "7" missed `build_checks_integrity.py:78`'s `_PROJECT_LIVE_REL = "architecture/build-checks.md"` private-constant pattern; the rev-2 design grep used `Path\(["']architecture` plus `["']architecture/` plus `^_[A-Z_]*REL\s*=` and rediscovered 9 sites (later corrected to 8 after dropping conftest). This test makes the "8 is the correct count" claim machine-verifiable going forward.

## Out of scope

- **Renaming `architecture/` → `.sdlc/`**: explicitly deferred to slice-069 (`rename-architecture-to-sdlc-and-track-in-git`). This slice ships the seam ONLY; the rename is a 1-line `VAULT_ROOT = Path(".sdlc")` change PLUS a `.gitignore` edit PLUS the philosophy ADR — all in slice-069's scope.
- **Un-gitignoring the vault** (flipping `.gitignore:10-11`): slice-069's scope.
- **Cross-machine claim semantics**: slice-070+ (`remote-cross-machine-slice-claim-semantics`); needs `/risk-spike` first to pick coordinator (git-rebase loop / GitHub Issues / external lock service / pre-partitioned slice-number blocks).
- **Rescoping/renaming the original slice-068 nominee** (`add-slice-queue-claim-state-machine` per slice-067 plan): user-intent candidate #4 from query-design 2026-05-25; sequence depends on slice-070 outcome.
- **Migrating SKILL.md user-facing prose path references**: docs describing the default layout are NOT code; out of scope (would trigger 24 SKILL.md drift-guard fan-out for zero behavior benefit).
- **Migrating test-fixture archive references** (`tests/methodology/fixtures/archive_backtest_corpus/*/mission-brief.md`): frozen historical snapshots; preserve verbatim per ADR-030 (`archive-backtest-verbatim-tracked-corpus`).
- **Migrating `graphify-out/` or `diagnose-out/` path references**: out of scope (different output trees; would be addressed by an analogous `GRAPHIFY_OUT_ROOT` / `DIAGNOSE_OUT_ROOT` constant in slice-069 or later if warranted — judgement deferred).
- **methodology-changelog v0.70.0 entry / PMI-1 bump**: lock posture at `/design-slice` per MEPD-1 Inclusion-heuristic. Strong default: NO bump, NO entry — this is a pure mechanical refactor minting no new rule, no new audit surface, no consumer-propagation obligation. If `/design-slice` discovers otherwise, that's documented there.

## Dependencies

- Prior slices: [[slice-067-add-parallel-slice-queue-output]] — slice-067 ships `tools/slice_queue_writer.py` which is one of the 7 modules this slice migrates; [[slice-066-add-worktree-per-slice-discipline]] — worktree mechanics carry forward unchanged (this slice runs in its own worktree per BRANCH-2).
- Vault refs (corrected per /critique B1 + M3 ACCEPTED-FIXED): [[tools/build_checks_integrity]] (NEW per B1 — missed by rev-1 grep), [[tools/critique_review_prerequisite_audit]], [[tools/cross_spec_parity_audit]], [[tools/risk_register_audit]], [[tools/slice_queue_writer]], [[tools/state_transition_pin_audit]], [[tools/supersede_audit]], [[tools/validate_slice_layers]] — the **8 migration sites** (exhaustive allowlist per AC4). NOT migrated (excluded with rationale per design.md §Sites EXCLUDED): [[tools/shippability_decoupling_audit]] (AST-pattern allowlist semantics), error-message-string sites (user-facing prose). DEFERRED to a follow-on slice per /critique M3: [[tests/methodology/conftest]] and ~15 other `tests/methodology/*.py` files (~42 occurrences of `REPO_ROOT / "architecture"`).
- Risk register: no direct R-NN retirement.
- User-intent chain (recorded in `architecture/slice-queue.md` per PSQ-1 at Step 6.5): slice-069 `rename-architecture-to-sdlc-and-track-in-git` (LARGE, depends on this slice) → slice-070 `remote-cross-machine-slice-claim-semantics` (LARGE, needs `/risk-spike`) → slice-071 `rescope-or-rename-claim-state-machine` (rename/rescope, depends on slice-070 outcome).
- Graphify dependency: none (no graph queries in this slice's runtime).

## Mid-slice smoke gate

At ~50% of build (after `tools/vault_paths.py` lands + test_vault_root_constant.py rows 1+2 flip to PASSING, before migrating the 7 sites):

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -c "from tools.vault_paths import VAULT_ROOT; from pathlib import Path; assert VAULT_ROOT == Path('architecture'), f'unexpected VAULT_ROOT={VAULT_ROOT}'; print('OK default')"
$env:AI_SDLC_VAULT_ROOT = '/tmp/smoke'
& $PY -c "from tools.vault_paths import VAULT_ROOT; from pathlib import Path; assert VAULT_ROOT == Path('/tmp/smoke'), f'unexpected VAULT_ROOT={VAULT_ROOT}'; print('OK override')"
Remove-Item env:AI_SDLC_VAULT_ROOT
```

Expected: both prints output `OK default` / `OK override`. If fails: STOP, diagnose the module-import semantics (likely cause: env var read at module-load not preserved across subprocess; fix by re-reading at attribute-access time via property).

## Pre-finish gate

- [ ] All 4 acceptance criteria PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Full pytest suite passes (baseline 899/899 from slice-067 + 10 new tests from this slice — per /critique M1 ACCEPTED-FIXED adding `test_consumer_constants_are_frozen_at_first_import` — = 909/909 target; locked at /design-slice + corrected at /critique)
- [ ] BRANCH-2 audit (`tools/branch_workflow_audit.py`) clean: slice ran in canonical worktree `<main-parent>/<main-name>-wt/slice-068-add-vault-root-constant` on `slice/068-add-vault-root-constant` branch
- [ ] `git diff --stat skills/ agents/` returns empty (this slice does NOT edit skill or agent markdown — confirms the no-OSDG-1-fan-out scope discipline)
- [ ] `$PY -m tools.plugin_manifest_audit` clean (PMI-1 unaffected — no manifest changes)
- [ ] `$PY -m tools.critique_agent_drift_audit --repo-root .` clean (CAD-1 unaffected — no agent edits)
- [ ] `$PY -m tools.test_first_audit --strict-pre-finish` exit 0 (all 9 TF-1 rows PASSING)

## Pipeline position

- **predecessor**: `/reflect` (loop entry from slice-067 → slice-068; in this run, `/query-design` 2026-05-25 surfaced the user-intent chain that triggered `/slice`)
- **successor**: `/design-slice`
- **auto-advance**: true
- **on-clean-completion**: mission brief + milestone.md written + slice-queue.md regenerated via Step 6.5; user supplied explicit intent (`add-vault-root-constant` — query-design handoff); auto-invoke `/design-slice` via Skill tool without further prompt.
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - Candidate selection — DISCHARGED (user explicit pick from query-design handoff: candidate #1 of the 4-slice user-intent chain).
  - BFRD-1 bug-fix confirm gate — N/A (this is `add-*` additive feature work, not a bug fix; no `tests/bugs/*` row needed).

> Per PCA-1 (`methodology-changelog.md` v0.41.0). The `## Next step` section below is the human-readable companion; this block is the machine-actionable auto-advance directive read at skill-completion.

## Next step

`/design-slice` — turn this mission brief into a just-enough spec covering: `tools/vault_paths.py` module API shape (module-level constant vs lazy property — env-var-at-import-vs-access decision is load-bearing for the subprocess test), the exhaustive 7-module migration allowlist (and the `# VAULT_ROOT-routed (slice-068)` inline marker convention), the prose-vs-path distinction discipline (which existing `tests/methodology/test_methodology_changelog.py` matchers count as prose-assertions and stay untouched), MEPD-1 Inclusion-heuristic posture lock (recommended: EXCLUDE — pure mechanical refactor, no rule mint), and the 9-row TF-1 test plan finalization with concrete test bodies.
