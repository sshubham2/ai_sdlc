# Slice 101: add-gate-audit-cli-exit-code-tests

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: the systemic *"mandatory-gate CLI block-path is untested"* exposure — diagnose backlog SC-004 / SC-011 / SC-013 / SC-014 / SC-015 / SC-016 / SC-020 / SC-021 ("CLI exit-1 untested systemic batch"). Not a numbered risk-register entry; it is the dominant confirmed-finding theme in `diagnose-out/backlog.md`.
**Test-first**: false  (the deliverable *is* tests over already-correct production code — there is no implementation behind these tests; the exit-1 wiring already exists, it is only unverified)
**Walking-skeleton**: false
**Exploratory-charter**: false

**Closes:** SC-004, SC-011, SC-013, SC-014, SC-015, SC-016, SC-020, SC-021

## Intent

The pipeline's value proposition is "deterministic gates catch spec rot." Eight mandatory gate audits expose that guarantee through their CLI exit code — `sys.exit(main())` returning non-zero on violations — yet **that exact block path is exercised by zero tests** (per the diagnose backlog: every one of the 8 only tests the `audit()` function, never the `main()` / `-m` entrypoint that the pre-finish gate and pre-commit hooks actually consume). A regression that flips one `main()` to `return 0` on violations would silently un-block that gate and **no test would catch it**. This slice ships per-audit regression tests that invoke each CLI entrypoint on a *violating* input and assert the non-zero block exit — and proves each test non-vacuous by mutation. Pure test-coverage hardening over existing-correct code; no production behavior changes.

**Parallel context (slice-100):** runs alongside `slice-100-add-vault-flip-readiness-audit` (the vault-flip readiness audit). This slice is deliberately scoped to **existing `tests/methodology/test_*.py` files only** — disjoint from slice-100's blast radius (`tools/vault_flip_readiness_audit.py` + its *new* test file + the `plugin.yaml` / `tools/install_audit.py` / `INSTALL.md` / `shippability.md` registration surface) — and bumps **no** `VERSION`, so it incurs zero R-28 shared-`~/.claude/` forward-sync contention.

## The 8 target gate-audit CLIs

| Gate (RULE-ID) | Module | Backlog | Entry to exercise |
|----------------|--------|---------|-------------------|
| PMI-1 | `tools/plugin_manifest_audit.py` | SC-004 | `sys.exit(main())` (`:353`) — only `_list_actual_tools()` is tested today |
| TRI-1 | `tools/triage_audit.py` | SC-011 | `main()` returns 1 (`:501-505`) — tests call `audit_critique_file()` only |
| LINT-MOCK | `tools/mock_budget_lint.py` | SC-013 | `sys.exit(main())` (`:874`) — CLI called but only encoding asserted, not returncode |
| DR-1 | `tools/critique_review_audit.py` | SC-014 | `sys.exit(main())` (`:292`) — `main()` never called |
| WIRE-1 | `tools/wiring_matrix_audit.py` | SC-015 | `sys.exit(main())` (`:346`) — `main()` never called |
| CSP-1 | `tools/cross_spec_parity_audit.py` | SC-016 | `sys.exit(main())` (`:407`) — `main()` never called |
| PTFFD-1 | `tools/shippability_path_audit.py` | SC-020 | `main()` returns 1 — function-level tests only |
| BRANCH-1 | `tools/branch_workflow_audit.py` | SC-021 | `main()` exit 1/2 (`:403-444`) — tests call `audit()` directly |

> **Design-time liveness check (code-is-truth):** `diagnose-out/backlog.md` is dated 2026-05-20. `/design-slice` plan-mode MUST re-confirm each gap is still live against current code (line numbers may have drifted; a gap may have been closed by an intervening slice). Drop any already-covered audit from scope and note it; never add a redundant test on top of existing coverage.

## Acceptance criteria

1. **Block-path coverage** — every one of the 8 gate-audit CLI entrypoints (PMI-1, TRI-1, LINT-MOCK, DR-1, WIRE-1, CSP-1, PTFFD-1, BRANCH-1) has a regression test that invokes its CLI entrypoint (`main()` directly, or `python -m tools.<x>` via subprocess) on a **violating** input and asserts the non-zero **block** exit code (`1`; plus the `2` usage path for `branch_workflow_audit` where its contract distinguishes it).
2. **Non-vacuity by mutation** — each new block-path test is proven non-vacuous: temporarily force the audit's `main()` to `return 0` on violations → the test FAILS → revert. The mutation result is recorded in `build-log.md` for every audit (per the project's "prove non-vacuity by MUTATION" discipline).
3. **Cause-pinned, pass-discriminating** — each test's violating fixture triggers the audit's *real target* violation (not an incidental `FileNotFoundError`/usage error that exits non-zero for the wrong reason — "pin the STOP *cause*, not just the STOP"); and each audit also has a conforming-input case asserting exit `0`, so the test discriminates block-vs-pass.
4. **Parallel-safe & green** — the diff touches **only** `tests/methodology/test_*.py` (plus, at most, a local `_`-prefixed test helper); `tools/**`, `skills/**`, `plugin.yaml`, `INSTALL.md`, `architecture/shippability.md`, and `VERSION` are unchanged. `$PY -m pytest tests/methodology -q` and `$PY -m tools.shippability_runner` both stay green.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Block-path coverage | `$PY -m pytest tests/methodology -q -k "exit or main or cli or returncode"` (or the new test ids) → all 8 block-path tests present and PASS; inspect each asserts `returncode == 1` (BRANCH-1 also `== 2` on usage). |
| 2 | Non-vacuity by mutation | For EACH audit: edit its `main()` to `return 0` on the violating branch → run that audit's new test → FAILS; `git checkout` the tool → PASSES. `build-log.md` carries an 8-row mutation-evidence table. |
| 3 | Cause-pinned + pass-discriminating | Inspect each violating fixture asserts on the audit's specific violation (e.g. PMI-1 plugin.yaml missing a real skill; TRI-1 critique.md missing the triage section); run the conforming-input case → exit `0`. |
| 4 | Parallel-safe & green | `git -C <wt> diff --name-only master` lists only `tests/methodology/*.py`; `Get-Content VERSION` unchanged; `$PY -m pytest tests/methodology -q` + `$PY -m tools.shippability_runner` both green. |

## Must-not-defer

- [ ] **Non-vacuity proof by mutation for EVERY new test** — a block-path test that still passes when `main()` is forced to `return 0` pins nothing (the project's single highest-value pin-test discipline; do not skip any of the 8).
- [ ] **Pin the STOP cause** — the violating fixture must fire the *target* gate's violation, not an incidental error path that happens to exit non-zero (slice-085 lesson).
- [ ] **cp1252-safe stdout capture** — any subprocess CLI invocation that captures output MUST pass `encoding="utf-8"` (BC-GLOBAL-5); several of these audits print non-ASCII (`→`, `—`). A bare `text=True` capture is a silent-data-loss site on Windows.
- [ ] **Parallel-safety** — do NOT touch `tools/install_audit.py`, `plugin.yaml`, `INSTALL.md`, `architecture/shippability.md` (slice-100's surface) or bump `VERSION`. No new tool, no new RULE-ID (MEPD-1 EXCLUDE).
- [ ] **No new public surface** — if a shared test helper is introduced, keep it local to the test module or a `_`-prefixed test-only module so it stays out of INST-1 / PMI-1 inventory.

## Out of scope

- **High-CC function decomposition** of the same audits (SC-003 `run_audit`, SC-010 `audit_critique_file`, SC-012 `_lint_go`/`_lint_typescript`) — production refactors; separate slices. This slice adds tests only, changes no production code.
- **Implementing missing gate *enforcement*** (SC-006 / SC-007 `/drift-check`; SC-008 already addressed by slice-080) — those concern gates that don't block *at all*; this slice tests audits whose exit-1 wiring already exists.
- **The vault-flip work** — owned by slice-100 and the queued `execute-vault-flip`.
- Any new tool, `VERSION` bump, or `methodology-changelog.md` entry.
- The remaining backlog dedup / size / dead-code items (SC-017/019/022/023/024/025/026).

## Dependencies

- Prior slices: none hard — the 8 audit modules and their existing `tests/methodology/test_*.py` files already exist; this slice extends them.
- Vault refs: `diagnose-out/backlog.md` (SC-004/011/013/014/015/016/020/021); the gate RULE-IDs PMI-1, TRI-1, LINT-MOCK, DR-1, WIRE-1, CSP-1, PTFFD-1, BRANCH-1 ([[CLAUDE.md]] "Audits are not optional").
- Risk register: none directly (backlog-theme-sourced, not a numbered open risk).
- Parallel slice: [[slice-100-add-vault-flip-readiness-audit]] — disjoint file set (coordination only, no dependency).

## Mid-slice smoke gate

At ~50% of build (≈4 of 8 audits covered), run:
```
$PY -m pytest tests/methodology -q -k "<the new test ids so far>"
```
Then run ONE mutation check immediately (don't wait for pre-finish): force one covered audit's `main()` to `return 0` on violations → its new test MUST fail.
Expected: the written tests PASS against current code, AND the mutation makes the corresponding test FAIL. If a block-path test passes EVEN with `main()` forced to `return 0` → the test is **vacuous** — STOP, fix the fixture (pin the real violation), don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md (incl. the 8-row mutation-evidence table)
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] `git diff --name-only master` confirms only `tests/methodology/*.py` changed (parallel-safety with slice-100 held)
