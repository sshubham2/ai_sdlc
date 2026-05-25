# Validation: Slice 042 realign-entry-present-pin-names-to-decoupled-shape

**Date**: 2026-05-18
**Result**: PASS

Real-environment validation for a methodology-surface rename = running the changed
audits/suite on the **real** repo artifacts (not fixtures) — done at /build-slice
T4/T5 and re-confirmed here via the Step-5.5 canonical sequence.

## Per-criterion results

### AC1: All 37 active `test_\w*_entry_(?:present|names_\w+)_in_repo_and_installed` defs in test_methodology_changelog.py renamed to drop `_and_installed` (anchor catches the no-`_sub_` `test_v_0_36_0_entry_names_three_modes_*`; never matches the CAD-1 `test_in_repo_and_installed_*_are_content_equal` family)
- **Status**: PASS
- **Evidence**: T1 — `grep -coE` family-literal in SOT before=37, after=0; 37 new-shape defs present; 4 `_entry_names` incl. L1606 `test_v_0_36_0_entry_names_three_modes_in_repo` confirmed. Full methodology suite collected + passed the 37 renamed defs (673 passed, T5). CAD-1 family structurally excluded by the `_entry_(present|names_)` infix anchor (0 matches in `test_*_drift.py`).
- **Notes**: `:2936` (the v0.53.0 pin's own docstring) was a *semantic* rewrite, not mechanical — it had asserted "no rename this slice"; now states slice-042 performed the realign. `:1821` mechanically realigned (describes "the family").

### AC2: Complete LIVE non-def set + all shippability `::`-selectors realigned
- **Status**: PASS
- **Evidence**: T3 — 7 LIVE files 0 old-literal residual; `architecture/shippability.md` 0 old `::`-selectors / 69 new-shape; `test_critique_agent.py:1426` `<rule>`-placeholder form realigned via literal replace. Step-5.5 `shippability_runner` 41/41 PASS proves every realigned selector resolves + executes.
- **Notes**: `test_shippability_decoupling_audit.py:57` (synthetic-row f-string) + `tools/methodology_changelog_forward_sync.py:58` (docstring) realigned in lockstep.

### AC3: FROZEN carve-out NOT renamed, byte-identical
- **Status**: PASS
- **Evidence**: T4 — regex-independent **sha256 byte-identical** across all 7 FROZEN surfaces (methodology-changelog.md, _index.md, lessons-learned.md, critic-calibration-log.md, ADR-009..040 tree, fixtures tree, archive tree); pre-baseline at `.frozen-snapshot.json`. Append-only shipped history provably untouched.
- **Notes**: Regex-count proof was abandoned mid-build (measurement-fragile: `grep -c` lines≠occ; Python `(?:)` vs ERE `grep`) — replaced with sha256, which is the stronger guarantee.

### AC4: Full methodology suite green; no orphaned `::`-consumer
- **Status**: PASS
- **Evidence**: T5 — `pytest tests/methodology` = **673 passed**. `shippability_path_audit` clean (41 rows, 261 tokens, all cited fns resolve). `shippability_runner` 41/41 PASS. SCMD-1 clean (incidental=0 — no gitignored coupling introduced). No orphaned consumer in `tools/**` / other `tests/**`.

### AC5: Exactly 1 anchored family-literal repo-wide outside FROZEN (ADR-044's documenting example); design.md/ADR-045 record the FROZEN set as a predicate
- **Status**: PASS
- **Evidence**: T3/T4 — anchored grep: ADR-044=1 (intentional `entry_names_three_modes` example), ADR-045=0, all 7 LIVE files=0. ADR-045's carve-out is a leak-proof predicate ("every ADR-*.md except ADR-044/045"). The 4 anchored refs in the slice-042 vault folder are intentional rename-describing documentation (gitignored, the slice's own record — same category as ADR-044).
- **Notes**: An own-/critique-fix self-contradiction (M3-sev had re-introduced 1 literal into ADR-045 while it claimed "ZERO") was caught at T0 and fixed in-slice — slice-032 design-correction-is-unguarded class, RSAD-1.

## Step 5b — VAL-1 layered safety
- **Layer A (credentials)**: PASS — 0 secrets across 6 changed files.
- **Layer B (dep hallucination)**: PASS — 0 import findings (`--imports-allowlist tests`).

## Step 5c/5d — WS-1 / ETC-1
Not applicable — `Walking-skeleton: false`, `Exploratory-charter: false` (audits return clean silently).

## Step 5.5 — Shippability catalog regression check
- **Pre-gate (a) SCMD-1**: clean — 41 rows; 417 cited fns; incidental=0, essential_registered=2, essential_unregistered=0.
- **Pre-gate (b) PTFCD-1 path audit**: clean — 41 rows, 261 test-path tokens, all files + cited functions exist.
- **Catalog (SRSC-1 canonical `shippability_runner`)**: **41 rows, 41 PASS, 0 FAIL**.
- **Regressions**: none. No past slice's critical path broken by this rename (the rename kept renamed defs ↔ renamed `::`-selectors coherent end-to-end).

## Multi-instance validation
**Required?**: no (test/catalog/docstring identifier rename; no multi-user/device/account surface)
**Result**: not-applicable

## Reality surprises
- **The FROZEN-integrity proof method itself was fragile** (regex-count: `grep -c` lines vs occurrences; Python `(?:...)` non-capturing group silently mismatched under ERE `grep`). Switched to a regex-independent sha256 tree-hash snapshot. Lesson for any future carve-out/identifier slice: prove "frozen set untouched" by content hash, never by regex count.
- **A `/critique` fix-prose edit re-introduced the very literal it was correcting** (M3-sev → ADR-045), caught only by the build-time T0 anchored grep. Recompute-don't-trust / design-correction-is-unguarded fired on the Builder's own fixes (execute-don't-reason N≥4 with slice-032/034/041) — strong `/reflect` + `/critic-calibrate` calibration input.
