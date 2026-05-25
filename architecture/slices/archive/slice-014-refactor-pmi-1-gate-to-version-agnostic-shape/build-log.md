# Build log: Slice 014 refactor-pmi-1-gate-to-version-agnostic-shape

**Date**: 2026-05-13
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-05-13 17:00 BUILD: Phase 0 — sha256 baseline captured (methodology-changelog byte-equal in-repo↔installed at `03df671c2ccd4251...`; VERSION = ai-sdlc-VERSION = "0.28.0" at `a80bff70...`; test_methodology_changelog.py at `8fa2207c...`; plugin.yaml at `0757853d...`); bidirectional sha256 forensic capture N=9 → N=10 stable baseline established
- 2026-05-13 17:02 BUILD: Phase 1a — empirical pre-Edit audit; grep confirms 7 entry-pin SECTIONs (Slice-007/008/009/010/011/012/013) + 7 entry-pin functions (v0.22.0..v0.28.0) + 1 PMI-1 gate SECTION at L433 + 1 PMI-1 gate function `_at_0_28_0` at L435; EPGD-1 self-application baseline established
- 2026-05-13 17:03 BUILD: Phase 1a' — imports preamble Edit applied (added `import ast` + `import pytest` to test_methodology_changelog.py top of file; PEP-8 stdlib→third-party→first-party grouping preserved); post-/critique-review M-add-1 ACCEPTED-FIXED prerequisite
- 2026-05-13 17:05 BUILD: Phase 1b — v0.29.0 entry-pin SECTION INSERTED between v0.28.0 function close and PMI-1 gate SECTION header; 2 new functions added (`test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed` + `test_v_0_29_0_entry_names_supersession_pattern_retired`); WRITTEN-FAILING (changelog v0.29.0 entry doesn't yet exist)
- 2026-05-13 17:08 BUILD: Phase 1c — PMI-1 gate Edit narrow-scoped to `_at_0_28_0` function body + SECTION header ONLY (lines 433-487 of pre-Edit file replaced); new SECTION header `# --- PMI-1 cleanliness gate (version-agnostic, slice-014 refactor; PMI-1 v1.1 per methodology-changelog.md v0.29.0) ---` + new `_invariant` function body; 3 new SECTIONs INSERTED below gate (structural meta-tests + regression test + ADR-013 pin) with 4 new test functions
- 2026-05-13 17:09 SMOKE: Phase 1d mid-slice smoke gate — initial run 3/4 PASS, 1/4 FAIL on regression test
- 2026-05-13 17:09 FINDING: DEVIATION-1 surfaced — regression test fails with `DID NOT RAISE <class 'AssertionError'>`; `monkeypatch.setattr("tests.methodology.test_methodology_changelog.REPO_ROOT", tmp_path)` dotted-string form did not take effect on the running test's REPO_ROOT
- 2026-05-13 17:11 BUILD: diagnostic — manually reproduced gate execution outside pytest succeeds (gate DOES raise AssertionError when `M.REPO_ROOT = tmp_path` directly); manually-instantiated `_pytest.monkeypatch.MonkeyPatch` with dotted-string-form also succeeds; failure mode is pytest-fixture-specific
- 2026-05-13 17:13 BUILD: diagnostic — sys.audit hook trace reveals gate reads BOTH tmp's VERSION/plugin.yaml AND the REAL repo VERSION/plugin.yaml (2 read opens to real files); monkeypatch patched a DIFFERENT module instance than the running test
- 2026-05-13 17:14 BUILD: diagnostic — debug-print probe inside the failing test reveals `__name__ = methodology.test_methodology_changelog` (bare key) but `sys.modules['tests.methodology.test_methodology_changelog'].REPO_ROOT` is the (correctly) patched tmp_path; **root cause: pytest's namespace-package import-mode** (with `tests/` lacking `__init__.py` while `tests/methodology/__init__.py` exists) places the running module in sys.modules under `methodology.test_methodology_changelog` (the bare key per `tests/` being a namespace package), NOT under `tests.methodology.test_methodology_changelog`; dotted-string monkeypatch fetches a SEPARATE importlib copy of the module under the dotted key
- 2026-05-13 17:16 BUILD: DEVIATION-1 fix applied — regression test now uses `monkeypatch.setattr(sys.modules[__name__], "REPO_ROOT", tmp_path)` (object form anchored on running module via sys.modules dict)
- 2026-05-13 17:17 SMOKE: Phase 1d re-run — 4/4 PASS
- 2026-05-13 17:18 BUILD: Phase 2 — atomic commit: methodology-changelog.md v0.29.0 entry written + forward-synced to ~/.claude/ + VERSION 0.28.0 → 0.29.0 + ~/.claude/ai-sdlc-VERSION 0.28.0 → 0.29.0 + plugin.yaml.version 0.28.0 → 0.29.0; ADR-013 already exists from /design-slice; full test suite NOT run between these steps per META-1 atomicity discipline
- 2026-05-13 17:19 TEST: Phase 3 — full methodology suite: 379 passed in 1.88s
- 2026-05-13 17:20 BUILD: Phase 4 — sha256 post-edit captured (methodology-changelog byte-equal in-repo↔installed at `7aa14cf5...`; VERSION = ai-sdlc-VERSION at `a68641c6...` both 0.29.0; test_methodology_changelog.py at `04a1a59e...`; plugin.yaml at `7eff6b20...`); EPGD-1 self-application empirical verification — 8 entry-pin SECTIONs + 9 entry-pin function definitions (v0.22.0..v0.29.0 + supersession-retired prose-pin) + 1 new PMI-1 gate SECTION + 1 new `_invariant` function + 3 new SECTIONs (structural meta-tests + regression test + ADR-013 pin); **0 of 7 prior entry-pin function names changed**
- 2026-05-13 17:22 FINDING: slice-013 N=1 watch-list class `shippability-catalog-consumer-reference-propagation-after-PMI-1-structural-invariant-supersession` recurs at slice-014 — row 13 pytest command referenced deleted `_at_0_28_0`; **N=2 promotion threshold MET** at slice-014; caught proactively at Phase 4 (vs slice-013 caught at /validate-slice Step 5.5)
- 2026-05-13 17:23 BUILD: shippability.md row 13 updated to reference `_invariant` (consumer-reference propagation per slice-013 generic methodology lesson); row 14 ADDED for slice-014 with 7 pytest commands
- 2026-05-13 17:25 TEST: TF-1 strict-pre-finish initial run — 8 violations (AC#5 ac-without-row + 7 PENDING rows); brief amended (split row 1 into AC #1 + AC #5; all 8 rows flipped to PASSING); re-run clean (8 PASSING / 0 WRITTEN-FAILING / 0 PENDING)
- 2026-05-13 17:26 TEST: WIRE-1 clean (zero-row matrix accepted); BC-1 clean (zero rules apply — negative anchors did their job on methodology-vocabulary)
- 2026-05-13 17:27 TEST: shippability row 14 (slice-014 critical path) — 7/7 PASS in 0.08s
- 2026-05-13 17:27 TEST: shippability row 13 (slice-013 critical path with propagated _invariant rename) — 2/2 PASS in 0.04s
- 2026-05-13 17:28 TEST: full methodology suite final — 379 passed in 1.86s at v0.29.0
- 2026-05-13 17:28 TEST: PMI-1 plugin_manifest_audit clean; INST-1 install_audit clean (24/24 skills, 5/5 agents, 4/4 templates, 15/15 tool modules; methodology v0.29.0); CSP-1 skipped (not Heavy mode); CAD-1 byte-equal on agents/critique.md

## Summary

### Plan executed

8-phase plan from design.md `## Phase plan` followed in order:

- **Phase 0** — sha256 forensic capture (pre-edit baseline) — DONE
- **Phase 1a** — empirical pre-Edit audits (Audit 3 grep verification) — DONE; 7 entry-pin functions + 1 PMI-1 gate confirmed pre-build
- **Phase 1a'** — imports preamble Edit (`import ast` + `import pytest` added per /critique-review M-add-1) — DONE
- **Phase 1b** — INSERT v0.29.0 entry-pin SECTION + 2 entry-pin / prose-pin functions — DONE
- **Phase 1c** — PMI-1 gate Edit (delete `_at_0_28_0` + add `_invariant` + 2 AST meta-tests + regression test + ADR-pin + 3 new SECTIONs) — DONE with DEVIATION-1 surfaced at Phase 1d (see below)
- **Phase 1d** — mid-slice smoke gate — initially 3/4 PASS due to DEVIATION-1; re-run 4/4 PASS after fix
- **Phase 2** — ATOMIC commit (changelog v0.29.0 entry + forward-sync + 3 version bumps + ADR-013) — DONE
- **Phase 3** — full test suite — 379/379 PASS at v0.29.0
- **Phase 4** — sha256 post-edit + EPGD-1 self-application diff verification — DONE; 0 of 7 prior entry-pin functions touched

### Mid-slice smoke gate

**Result**: PASS (after DEVIATION-1 fix)
**Evidence**:

```
$PY -m pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant tests/methodology/test_methodology_changelog.py::test_pmi_1_gate_function_is_version_agnostic_shape tests/methodology/test_methodology_changelog.py::test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge tests/methodology/test_methodology_changelog.py::test_no_per_version_pmi_1_gate_functions_remain -v
============================== 4 passed in 0.09s ==============================
```

Initial run: 3/4 PASS, 1/4 FAIL on regression test with `Failed: DID NOT RAISE <class 'AssertionError'>`. Diagnosis traced through 4 audit-hook reads (2 tmp + 2 real) → `__name__ = methodology.test_methodology_changelog` → root cause = pytest namespace-package import-mode + dotted-string monkeypatch fetching separate importlib copy. Fix: object-form `monkeypatch.setattr(sys.modules[__name__], "REPO_ROOT", tmp_path)`. Diagnostic time: ~10 min.

### Pre-finish gate

- [x] All ACs PASS with evidence — see validation.md (forthcoming)
  - AC #1: 7-row mission-brief table covers it; `_invariant` exists, `_is_version_agnostic_shape` confirms no version literal in body, no `_at_0_NN_0` function remains
  - AC #2: `_fails_with_pinned_message_when_version_files_diverge` PASSES with "PMI-1" + "slice-006 escape" substrings asserted independently
  - AC #3: `_no_per_version_pmi_1_gate_functions_remain` PASSES
  - AC #4: v0.29.0 entry-pin + supersession-retired prose-pin + ADR-013 pin all PASS; canonical phrase `version-agnostic PMI-1 cleanliness gate` pinned across N=3 surfaces empirically verified
  - AC #5: VERSION = plugin.yaml.version = ai-sdlc-VERSION = "0.29.0"; `_invariant` PASSES at v0.29.0 with ZERO code change vs Phase 1c form (empirical proof of supersession-pattern retirement)
- [x] Must-not-defer addressed (12 items including META-1 atomicity per /critique M1; EPGD-1 self-application; bidirectional sha256 N=10; N-surface schema-pin N=3 instances stable; shippability row 14; RSAD-1 discipline; no TODOs/FIXMEs/debug prints)
- [x] TF-1 strict-pre-finish PASSES (8 rows PASSING / 0 WRITTEN-FAILING / 0 PENDING)
- [x] WIRE-1 PASSES (zero-row matrix accepted)
- [x] BC-1 PASSES (zero rules apply — negative anchors did their job on methodology-vocabulary)
- [x] INST-1 PASSES (24/24 skills, 5/5 agents, 4/4 templates, 15/15 tool modules at methodology v0.29.0)
- [x] PMI-1 plugin_manifest_audit PASSES (24/5/15 enumeration; version 0.29.0)
- [x] CAD-1 PASSES (agents/critique.md byte-equal in-repo↔installed at sha256 `0346d39ef988fa61...`)
- [x] Smoke regression check PASS (mid-slice still passes after Phase 2 atomic commit)
- [x] Full methodology suite: 379 passed at v0.29.0
- [x] Shippability row 14 (slice-014 critical path): 7/7 PASS in 0.08s
- [x] Shippability row 13 (slice-013 critical path with propagated `_invariant` rename): 2/2 PASS in 0.04s
- [x] No new TODOs / FIXMEs / debug prints (the temporary debug-print probe at DEVIATION-1 diagnosis was removed before Phase 1d re-run)

### Deferrals (if any)

None. All 6 Critic findings (5 first-Critic + 1 meta-Critic M-add-1) ACCEPTED-FIXED in slice-014's own execution; no items DEFERRED.

### Design deviations (if any)

**DEVIATION-1: pytest namespace-package import-mode defeats `monkeypatch.setattr` dotted-string-form target**

- **Where design.md said X**: `## Regression test fixture spec` pinned the monkeypatch target as `"tests.methodology.test_methodology_changelog.REPO_ROOT"` (dotted-string form) per /critique M2 ACCEPTED-FIXED.
- **Code reality requires Y**: The running test module's actual sys.modules key is `methodology.test_methodology_changelog` (bare key) — NOT the fully-qualified dotted path. With `tests/` lacking `__init__.py` (namespace package) while `tests/methodology/__init__.py` exists, pytest's default import-mode places the test module under the bare key. `monkeypatch.setattr` with the dotted-string form imports a SEPARATE copy under the dotted key, leaving the running test's REPO_ROOT untouched.
- **Fix applied at /build-slice**: object-form anchored on `sys.modules[__name__]` — `monkeypatch.setattr(sys.modules[__name__], "REPO_ROOT", tmp_path)`. Inline docstring updated to explain the name-resolution semantics.
- **Updated in design.md? yes** — the canonical fixture spec subsection's docstring + fixture-contract bullet pinning explicitly cite the slice-014 build-time DEVIATION-1 origin and the namespace-package import-mode root cause.
- **New Dim 9 sub-class candidate at N=1**: `pytest-namespace-package-import-mode-defeats-dotted-string-monkeypatch-target`. Same root-cause family as VAL-1 Layer B `tests` namespace-package class (N=11 cumulative recurrence pre-slice-014). Promote at N=2 if recurs at slice-015+.
- **Critic-stack accountability**: 3 layers came close — first /critique M2 pinned the bare-vs-conftest name-resolution; /critique-review M-add-1 added the imports-prerequisite class; /build-slice empirical smoke gate caught the namespace-package import-mode interaction. Calibration signal for /critic-calibrate.

**Slice-013 N=1 watch-list class `shippability-catalog-consumer-reference-propagation-after-PMI-1-structural-invariant-supersession` recurs at slice-014 — N=2 promotion threshold MET.** Row 13 pytest command referenced the deleted `_at_0_28_0`. Caught PROACTIVELY at Phase 4 (vs slice-013 caught reactively at /validate-slice Step 5.5) because the slice-013 reflection generic methodology lesson was applied. Row 13 command updated to reference `_invariant`; row 14 added. Promote to Dim 9 sub-class refinement at slice-015 — N=2 evidence is the established threshold. Mission-brief Phase 5 (shippability.md updates) should explicitly call out "scan ALL existing rows for any superseded test name AND propagate the rename" in future slices' must-not-defer lists.

### Files changed

- `tests/methodology/test_methodology_changelog.py` — imports block + 7 new test functions across 4 new SECTIONs + 1 narrow-scoped Edit removing legacy `_at_0_28_0` gate function + its SECTION header
- `methodology-changelog.md` — v0.29.0 entry added at top of version-entries list
- `~/.claude/methodology-changelog.md` — forward-synced (byte-equal at `7aa14cf5...`)
- `VERSION` — 0.28.0 → 0.29.0
- `~/.claude/ai-sdlc-VERSION` — 0.28.0 → 0.29.0
- `plugin.yaml` — `version: 0.28.0` → `version: 0.29.0`
- `architecture/shippability.md` — row 13 command updated (consumer-reference propagation); row 14 added (slice-014 critical path)
- `architecture/slices/slice-014-refactor-pmi-1-gate-to-version-agnostic-shape/mission-brief.md` — TF-1 table split row 1 into separate AC #1 + AC #5 rows; all 8 rows flipped PENDING → PASSING

(ADR-013 already created during /design-slice; not modified during /build-slice.)
