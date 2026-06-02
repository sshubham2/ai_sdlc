# Design: Slice 101 add-gate-audit-cli-exit-code-tests

**Date**: 2026-06-02
**Mode**: Standard

## What's new

- One new test module `tests/methodology/test_gate_audit_cli_exit_codes.py` holding the CLI **block-path** (exit-1) and **clean-path** (exit-0) regression tests for all 8 untested gate-audit CLIs, plus the two distinct **exit-2** usage cases (`shippability_path`, `branch_workflow`).
- A small in-module shared helper `_run_main(module_main, argv) -> int` that calls the audit's `main(argv)` **in-process** and returns the int (the exit code) — no subprocess.
- **Cause-discrimination (M1 fix):** because several audits emit the **same** non-zero exit for *multiple* violation kinds, the int alone cannot prove the *target* gate fired. Every block-path test therefore pairs **two** assertions on the **same** fixture: (1) `_run_main(main, argv) == <block_code>` (pins the exit wiring) AND (2) `<target_kind> in {v.kind for v in <audit_fn>(fixture).violations}` (pins the cause), where `<audit_fn>` is the audit's already-tested `audit()`/`run_audit()`/`lint_files()`/`audit_*` function. This is what makes AC3 ("pin the STOP cause, not just the STOP") structurally true rather than aspirational.
- No production code changes whatsoever. No new tool, no `VERSION` bump, no `plugin.yaml` / `INSTALL.md` / `shippability.md` edit.

## What's reused

- The 8 audit entrypoints, all verified `def main(argv: list[str] | None = None) -> int` that **return** the code (the module-level `sys.exit(main())` is the only exit site): `tools/plugin_manifest_audit.py:329`, `tools/triage_audit.py:468`, `tools/mock_budget_lint.py:815`, `tools/critique_review_audit.py:258`, `tools/wiring_matrix_audit.py:301`, `tools/cross_spec_parity_audit.py:362`, `tools/shippability_path_audit.py:267`, `tools/branch_workflow_audit.py:677`.
- Each audit's existing test module already constructs a *violating* fixture and calls `audit()`/`run_audit()`/`lint_files()`; the new tests reuse the **same fixture shapes** (built locally in the new module — no cross-test-module imports) and only change the assertion target to `main(argv)`'s returned int.
- Established cross-cutting-contract test precedent: `tests/methodology/test_utf8_stdout_audit.py` + `test_utf8_stdout_regression.py` test ONE contract (UTF8-STDOUT-1) across ALL tools in a dedicated module rather than per-tool — this slice mirrors that for the CLI exit-code contract.
- `diagnose-out/backlog.md` SC-004/011/013/014/015/016/020/021 (closed by this slice).

## Components touched

### `tests/methodology/test_gate_audit_cli_exit_codes.py` (new)
- **Responsibility**: pin the CLI exit-code contract of every mandatory gate audit — `main(argv)` returns the non-zero **block** code on a violating input and `0` on a conforming input — so a regression that flips any `main()` to `return 0` on violations is caught.
- **Lives at**: `tests/methodology/test_gate_audit_cli_exit_codes.py` (created by this slice)
- **Key interactions**: imports each audit's `main` and calls it in-process; builds violating/conforming fixtures via pytest `tmp_path` (and tmp git repos via `subprocess` for `branch_workflow`, mirroring `test_branch_workflow_audit.py::_run_git`).

## Per-audit invocation spec (build-ready)

The central correctness concern is **"pin the STOP cause, not just the STOP"** (slice-085 lesson): several audits exit non-zero for *non-target* reasons, so each fixture must trigger the audit's **real** violation and the argv must defeat any masking exemption.

| # | RULE-ID | Module | `main(argv)` | Violating fixture | Block | Clean | Nuance to pin (the *cause*) |
|---|---------|--------|--------------|-------------------|:----:|:----:|-----------------------------|
| 1 | PMI-1 | `plugin_manifest_audit` | `["--root", str(tmp)]` | tmp root with a **complete valid** `plugin.yaml` (`name`/`description`/`version` present, `version`==tmp `VERSION`) that omits an on-disk skill → `orphan-skill` is the SOLE non-zero source | 1 | 0 | default `--root` is cwd → MUST pass tmp; supply all required fields so `missing-field` can't co-fire (M1) |
| 2 | TRI-1 | `triage_audit` | `[str(crit_md), "--no-carry-over"]` | a **present** `critique.md` (assert `path.is_file()` first) missing the triage section → `no-section` | 1 | 0 | `--no-carry-over` is defensive (carry-over wouldn't fire on a mission-brief-less tmp dir anyway, m2); a missing file ALSO yields `no-section` → fixture must exist (M1) |
| 3 | LINT-MOCK | `mock_budget_lint` | `["--strict", str(test_py)]` | reuse the **stacked-`@patch` decorator** shape from `tests/methodology/fixtures/mock_budget_too_many.py:9-11` (>1 mock in one test fn) | 1 | 0 | **plain over-budget returns 0**; exit 1 needs `--strict` OR a Critical seam finding. Bare inline `MagicMock()` calls do NOT trip the count (M3) |
| 4 | DR-1 | `critique_review_audit` | `[str(review_md), "--no-carry-over"]` | a **present** `critique-review.md` (assert exists) missing a required section | 1 | 0 | `--no-carry-over` defensive (m2); fixture must exist (missing file co-fires, M1) |
| 5 | WIRE-1 | `wiring_matrix_audit` | `[str(design_md), "--no-carry-over"]` | `design.md` with a wiring row that has empty cells + no `rationale:` exemption | 1 | 0 | `--no-carry-over` defensive (carry-over needs a sibling mission-brief to fire — won't on a bare tmp dir, m2) |
| 6 | CSP-1 | `cross_spec_parity_audit` | `["--root", str(tmp), "--skip-heavy-check"]` | a threat-model with a **single-dash** `## TM-1 - <title>` item heading + `**Status**: mitigated` + a non-existent `**Implementation**:` path → `broken-ref` | 1 | 0 | `--skip-heavy-check` forces the run outside Heavy (else no-ops → 0). **Heading-separator trap (M-add-1):** `_ITEM_HEADING_RE` (`cross_spec_parity_audit.py:70-72`) matches a SINGLE dash/em-dash; the audit's own docstring uses a DOUBLE dash (`## TM-NN -- title`) which parses **0 items → exit 0** (false green). Use single-dash, NOT the docstring shape; build-log must show exit flips to 0 when the violation row is corrected |
| 7 | PTFCD-1 / PTFFD-1 | `shippability_path_audit` | `[str(catalog_md)]` | a **6-column SCMD-1** catalog (`\| # \| Slice \| Critical path \| Command \| Runtime \| Machine-cmd \|`) with a `pytest tests/methodology/test_DOESNOTEXIST.py` token in the **Machine-cmd** column, mirroring `tests/methodology/test_ptffd1_shippability_path_audit.py:16-30::_catalog` | 1 | 0 **and 2** | a 3-column table scans **0 rows → exit 0** (M3); exit **2** is the *missing-file* usage path — the fixture MUST be a real file with a bad row to get 1, not 2 |
| 8 | BRANCH-1 [†] | `branch_workflow_audit` | `[str(slice_folder), "--root", str(repo)]` | **self-contained** tmp git repo (see recipe below) where current branch == resolved default → `on-default-branch` | 1 | 0 **and 2** | exit **1**: `on-default-branch` via the deterministic recipe (NOT ambient-config-dependent, M2). exit **2**: a non-`slice-NNN-` folder name → `usage-error` (deterministic), NOT `default-branch-unresolvable` (env-dependent) |

> **Liveness confirmed (2026-06-02):** all 8 gaps verified live against current code — 5 test modules have zero CLI-exercising patterns; `branch_workflow`'s `subprocess` is git-fixture-only; `mock_budget`'s CLI is invoked only by `test_utf8_stdout_regression.py` which asserts encoding, not returncode. No gap has been closed since the 2026-05-20 backlog. (Note the PTFCD-1/PTFFD-1 rule-id spelling mismatch between `shippability_path_audit.py` and its test file — pre-existing, NOT reconciled by this slice.)

> **[†] BRANCH-1 label**: the audit self-IDs as "BRANCH-1 audit" in its argparse `description` (`tools/branch_workflow_audit.py:679`), so the row cites BRANCH-1; the live methodology family is now BRANCH-2 / BRANCH-3 per CLAUDE.md (m3).

### Per-audit target kind (M1 cause-discrimination)

The block-path test for each audit asserts the int exit code AND that this exact `kind` is present in the audit-function's violations on the same fixture:

| # | Audit fn to call for kind-assert | `target_kind` |
|---|----------------------------------|---------------|
| 1 | `run_audit(project_root=tmp)` | `orphan-skill` |
| 2 | `audit_critique_file(crit_md, skip_if_carry_over=False)` | `no-section` (on a present, sectionless file) |
| 3 | `lint_files([test_py], frozenset())` | `mock-budget` |
| 4 | `audit_review_file(review_md, skip_if_carry_over=False)` | `missing-section` (meta-Critic-verified) |
| 5 | `audit_design_file(design_md, skip_if_carry_over=False)` | `missing-cells` (meta-Critic-verified; NOT the prose "empty-cell kind") |
| 6 | `run_audit(project_root=tmp, skip_heavy_check=True)` | `broken-ref` — **NOT** `parity-mismatch` (no such kind exists; real kinds are `broken-ref`/`missing-ref`/`invalid-status`/`missing-field`/`format`, `cross_spec_parity_audit.py:113-125`) [meta-Critic note 1] |
| 7 | `audit_catalog_file(catalog_md)` | `missing-test-file` (meta-Critic-verified; NOT the prose "missing-test-path kind") |
| 8 | `audit(slice_folder, repo_root=repo)` | `on-default-branch` (exit 1) / `usage-error` (exit 2) |

All 8 `kind` literals are now resolved against the real audit source (the dataclass `kind` field) — the meta-Critic verified rows 4/5/7 and corrected row 6 from the non-existent `parity-mismatch` to `broken-ref`. The contract is "assert the specific target kind," not a placeholder. **Row-2 caveat (meta-Critic note 2):** for TRI-1 the `no-section` kind-assert is near-vacuous (a missing file ALSO yields `no-section`); the **load-bearing cause-pin for row 2 is the `is_file()` precondition**, not the kind-assert. build-log AC2 evidence for row 2 must record `is_file()` as the discriminator.

### branch_workflow fixture recipe (M2 — deterministic, ambient-config-independent)

```
git init <repo>                       # may produce 'main' OR 'master' depending on host
git -C <repo> branch -M trunk         # force current branch to a known name
git -C <repo> config init.defaultBranch trunk   # repo-LOCAL → resolved default == 'trunk'
# now _current_branch == _resolve_default_branch == 'trunk' → 'on-default-branch' (exit 1), host-independent
```
The exit-**2** case uses a slice folder whose name is NOT `slice-NNN-<name>` → `usage-error` (deterministic), avoiding the env-dependent `default-branch-unresolvable` path.

## Design decisions (cheap/reversible — no ADR, per `/design-slice` anti-pattern "no ADRs for trivial/non-deviating choices")

1. **In-process `main(argv)` int-assertion, not subprocess.** The regression these tests guard is `main()` returning `0` (pass) when violations exist — that logic lives entirely in `main()`'s `return 1 if … else 0`. The module-level `sys.exit(main())` is unbreakable Python glue (if `main()` returns 1, the process exits 1 — not our code). In-process is faster, deterministic, and avoids subprocess stdout-capture cp1252 fragility. The AC2 mutation (force `main()` → `return 0`) targets exactly this surface. *Reversible:* swapping to `python -m` subprocess is a localized test-module change. *(This pre-empts the obvious "you didn't test the real process exit" objection — the real exit code is `sys.exit(int)`, which has no logic to regress.)*
2. **One consolidated cross-cutting module, not 8 per-audit edits.** The subject is the *shared* CLI exit-code contract, cross-cutting by nature — directly analogous to `test_utf8_stdout_audit.py` testing UTF8-STDOUT-1 across all tools in one module. Keeps the diff to a single new file (smaller merge surface vs slice-100), centralizes the `_run_main` helper, and groups the 8 fixtures + nuance comments in one readable place. *Reversible:* re-homing a test into its per-audit module is a copy-paste.

## Contracts added or changed

None. This slice introduces no new production contract. It **pins an existing implicit contract** — "each mandatory gate audit's `main()` returns a non-zero block code on violations" — that was previously unverified. No endpoint/event/schema added.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1**. This slice introduces **no new production module** — only a new test module (its consumer is the pytest runner, not a production entry point). The single row below carries the explicit exemption the audit requires; the audit treats it as clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_gate_audit_cli_exit_codes.py` | — | — | `pytest-collected test module — it IS the consumer test; no production entry point exists or is demanded — rationale: a test module's consumer is the test runner, mirroring tests/methodology/test_utf8_stdout_audit.py` |

## Decisions made (ADRs)

None — see "Design decisions" above (both cheap/reversible, no convention deviation). Parallel slice-100 holds ADR-091; this slice mints no ADR (so no ADR-number contention).

## Non-vacuity plan (AC2)

For EACH of the 8 audits, at build time: temporarily edit the tool's `main()` final `return 1 if … else 0` (or `mock_budget`'s `return 1` branch) to `return 0`, run that audit's new block-path test → it MUST FAIL; then `git checkout -- tools/<audit>.py` to revert. An 8-row evidence table (audit | mutation applied | test FAILED? | reverted?) is recorded in `build-log.md`. This is a **build-time discipline**, not a committed mutation harness — the discipline proves the pin is non-vacuous (a test that passes under the mutation pins nothing).

**Two distinct guarantees (m1):** the `return 0` mutation proves the test **depends on the int return** — it does NOT prove the test depends on the *target cause* (any exit-1→0 flip fails an `== 1` assert, even a wrong-cause one). Cause-pinning is delivered separately by the M1 kind-assertion (`target_kind in {v.kind for v in audit_fn(fixture).violations}`). `build-log.md` records both, labelled — mutation evidence ≠ cause-pinning evidence.

## Authorization model for this slice

N/A — test-only; no protected actions, no auth surface.

## Error model for this slice

N/A — adds no production error paths. The tests *assert on* existing exit codes (0 / 1 / 2); they introduce none.
