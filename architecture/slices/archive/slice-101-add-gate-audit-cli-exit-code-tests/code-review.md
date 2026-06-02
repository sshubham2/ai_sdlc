# Code Review: Slice 101 add-gate-audit-cli-exit-code-tests

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-06-02
**Result**: FINDINGS (no blockers, no majors; 3 minors + 1 nit)

## Summary

A well-constructed test-only slice. The code-Critic verified all 18 tests against the real source of all 8 audits, ran the module from clean bytecode (18 passed), and independently re-ran PTFCD-1 / BRANCH-1 / LINT-MOCK / WIRE-1 probes to confirm non-vacuity and exit-code dependence rather than trusting the build-log mutation table. Every cause-assert pins the SOLE non-zero kind on its fixture; every clean test forces `--no-carry-over` so exit 0 reflects a real parse, not a carry-over short-circuit; the BRANCH-1 deterministic recipe resolves host-independently. Findings are all minor.

## Changed files (in-scope)

```
tests/methodology/test_gate_audit_cli_exit_codes.py
architecture/slices/slice-101-add-gate-audit-cli-exit-code-tests/build-log.md
```

## Findings

### Blockers (advisory in v1)
None. No test false-passes (each block test's `main()==1` is genuinely violation-dependent; clean paths confirmed return 0 with zero violations) and no test contradicts an ACCEPTED ADR.

### Majors
None. The M1 cause-pinning design is sound on every row (SOLE-kind verified against each fixture, not merely the int-assert).

### Minors

#### m1: PTFCD-1 clean test depends on the OS temp dir NOT being nested under a `.git`/`VERSION` ancestor — latent false-FAIL on misconfigured runners  [DISPOSITION: ACCEPTED-FIXED in-slice]
- **Claim under review**: `test_gate_audit_cli_exit_codes.py` `test_ptfcd1_cli_clean_on_existing_test_path` seeds `tmp_path/tests/methodology/test_known.py` + a catalog, asserting `main([str(cat)]) == 0`.
- **Issue**: `audit_catalog_file` resolves cited test paths via `_find_repo_root(catalog_path)` (`tools/shippability_path_audit.py:90-98`) — walks up for `.git`/`VERSION`, falling back to `tmp_path` only if NO ancestor has either sentinel. On this machine the OS temp dir has no such ancestor → resolves to `tmp_path` → exit 0. But under `pytest --basetemp=<inside-repo>` (or `TMPDIR` under a checkout), `_find_repo_root` resolves to the OUTER repo → seeded file looked up there → not found → `missing-test-file` → clean test FALSE-FAILS. The block test is immune (expects a phantom path regardless of root).
- **Proposed fix**: seed a `VERSION` sentinel at `tmp_path` so `_find_repo_root` deterministically anchors there.
- **Disposition**: **ACCEPTED-FIXED in-slice** — added `(tmp_path / "VERSION").write_text("0.0.0\n", …)` to `_scmd1_catalog` (anchors BOTH block + clean PTFCD-1 tests to `tmp_path`, removing the runner-config env-dependence). Re-verified: module 18/18 from clean bytecode. This is a genuine flaky-test risk in the slice's own new code (the slice-090/091 env-dependence class), so fixed now rather than deferred.

#### m2: LINT-MOCK / DR-1 / WIRE-1 block tests' int-assert `==1` is broader than the cause-assert  [DISPOSITION: DEFERRED — bundled cleanup]
- **Issue**: `main()` returns 1 on ANY violation kind; the paired kind-assert is what pins the target. The fixtures currently emit ONLY the target kind (verified), so the tests are correct — but they're reused fixtures this module doesn't own; a future edit adding a second defect would be masked. Optional hardening: `assert kinds == {"<target>"}` for the single-kind-invariant audits.
- **Disposition**: DEFERRED to bundled cleanup (advisory; current behavior correct). Routed to /reflect.

#### m3: `_run_main` is a thin pass-through wrapper  [DISPOSITION: OVERRIDDEN — intentional doc-anchor seam]
- **Issue**: `_run_main(main_fn, argv): return main_fn(argv)` is one-line indirection. The code-Critic itself notes the docstring carries load-bearing rationale (why in-process is sound vs subprocess) + provides a single future seam (e.g. `pytest.raises(SystemExit)` handling) — files it as minor-not-defect.
- **Disposition**: OVERRIDDEN — the wrapper is a deliberate documentation anchor + change seam; keeping it is the right call. No action.

#### nit (n1): build-log mutation table is not repo-reproducible (throwaway harness, deleted)  [DISPOSITION: noted]
- **Issue**: `_mutation_harness.tmp.py` was deleted/not committed, so the AC2 table can't be re-run from the repo. Inherent to throwaway-harness AC2; the code-Critic independently re-confirmed non-vacuity by probe. The stale-bytecode incident writeup is accurate.
- **Disposition**: noted for /reflect. Future reproducible-AC2 idea: a committed `pytest.mark.skip`-gated `monkeypatch.setattr(module, "main", lambda argv: 0)` mutation test (sidesteps the `.pyc`-staleness class). Out of scope for this slice.

## Dimensions checked
- [x] Unfounded assumptions — none. All docstring claims verified against source (in-process main-returns-int ×8; no import-time side effects; M-add-1 em-dash regex). No phantom imports/symbols.
- [x] Missing edge cases — m1 (PTFCD-1 clean repo-root resolution; FIXED). Both exit-2 usage paths correctly distinguished from exit-1 (verified by probe).
- [x] Over-engineering — m3 (`_run_main` thin pass-through; mitigated by docstring; OVERRIDDEN).
- [x] Under-engineering — none. All 4 ACs have delivering code (block-path ×8, non-vacuity, cause-pinned + clean-discriminating, parallel-safe — `git diff tools/` empty verified).
- [x] Contract gaps — none. `audit_design_file` returns a `list` (not a result object); the test iterates it directly without `.violations` (correct — a real copy-paste trap avoided).
- [x] Security — none. Test-only; `_run_git` uses an arg list (no `shell=True`) + `encoding="utf-8"` (BC-GLOBAL-5). No hardcoded secrets (test git identity is a fixture).
- [x] Drift from vault — none. Code matches design.md exactly (in-process, consolidated module, paired kind-asserts, deterministic branch recipe, reused fixtures). No `tools/`/VERSION/plugin.yaml change; no slice-100 files touched.
- [x] Web-known issues — none. Only post-cutoff-sensitive surface is Python `.pyc` staleness (mtime+size), already diagnosed correctly in build-log. No external SDK/API in the diff.
- [x] Cross-cutting conformance — none. RSAD-1 self-passes (18/18 clean bytecode); APED-1 N/A (zero `tools/` parse-rule change); EOL-DRIFT-1 N/A (no byte-equality `.md` compare). BRANCH-1 recipe composes correctly with the audit's `_resolve_default_branch` fallback (traced all 3 branches).
