# Slice 054: fix-pyproject-toml-version-drift

**Mode**: Standard
**Estimated work**: 0.5 day (~1.5 hr)
**Risk retired**: none in `architecture/risk-register.md`; closes **SC-001** in `diagnose-out/backlog.md` (CRITICAL severity, topmost in `## Recommended order`)
**Test-first**: true (per BFRD-1 — failing repro established at `/repro`)
**Walking-skeleton**: false
**Exploratory-charter**: false

**Closes:** SC-001

## Intent

Bump `pyproject.toml` `[project].version` from the stale `"0.20.0"` to the canonical `VERSION` value (currently `"0.61.0"`) and pin the pyproject↔VERSION lock-step invariant behind a programmatic gate (the already-established BFRD-1 repro test at `tests/methodology/test_pyproject_version_matches_version_file.py`). PMI-1 (`tools/plugin_manifest_audit.py:207-217`) gates plugin.yaml↔VERSION only; pyproject.toml was an ungated sibling, so `pip install <repo>` silently produced `ai-sdlc-tools 0.20.0` — 41 minor versions behind the methodology semver — for every external consumer. This slice also doubles as the first end-to-end dogfood of slice-053's just-shipped BCR-1 round-trip wire (`**Closes:** SC-001` sentinel header above triggers `/reflect` to inject the `- **Addressed:** slice-054-…` line into `diagnose-out/backlog.md`).

## Acceptance criteria

1. `pyproject.toml` `[project].version` literal equals the trimmed contents of `VERSION` (the repro test `test_repro_sc001_pyproject_project_version_matches_version_file` PASSES — pre-fix FAILs with `'0.20.0' == '0.61.0'`).
2. Shippability row #54 PASSES under the slice-038 SRSC-1 runner (`$PY -m tools.shippability_runner architecture/shippability.md` returns 0 with row #54 marked PASS) — closes the SC-001 ungated stale-pip-artifact class.
3. `pyproject.toml` carries no stale `v0.20.0` literal and no `13 audit modules` / `13 tool modules` literal (current prose at lines 6, 66 is incidentally stale; slice-045 stale-prose precedent applies — either replace with `<see VERSION>` and `<see plugin.yaml>` non-literal forms, or refactor to non-version-bearing wording).
4. `/reflect` round-trips the `- **Addressed:** slice-054-fix-pyproject-toml-version-drift on YYYY-MM-DD` line into the `### SC-001` block of `diagnose-out/backlog.md` AFTER `**Evidence:**` (BCR-1 first end-to-end dogfood; triggered by the `**Closes:** SC-001` sentinel header at the top of this mission brief — M4 sentinel-anchored trigger per slice-053, NOT a bare SC-NNN mention).

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0): the SC-001 repro test was authored at `/repro` (slice-054 BFRD-1 entry) BEFORE the fix code; it currently FAILs with the bug signature and will PASS post-fix. The Inclusion-heuristic decision (Step 4a below) determines whether additional pin tests are added (if a new RULE-ID is minted: changelog `test_v_0_NN_0_<rule>_entry_present_in_repo` + `test_v_0_NN_0_<rule>_shippability_consumer_propagation` pair per slice-049/050 precedent).

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology | tests/methodology/test_pyproject_version_matches_version_file.py | test_repro_sc001_pyproject_project_version_matches_version_file | PASSING |
| 2 | catalog | tests/methodology/test_pyproject_version_matches_version_file.py | test_repro_sc001_pyproject_project_version_matches_version_file | PASSING |
| 3 | methodology | tests/methodology/test_pyproject_version_matches_version_file.py | test_pyproject_has_no_stale_0_20_0_or_count_literals | PASSING |
| 4 | methodology | tests/methodology/test_bcr_1_round_trip_end_to_end.py | test_bcr_1_sc054_round_trip_inputs_invariant | PASSING |

*Notes (per TF-1 enum-strict Status column — annotations moved out of the cells per build-time TF-1 audit feedback at slice-054 Phase F):*
- AC2 (catalog): row #54 points at AC1 + AC3 tests + the 2 entry-pin tests + the BCR-1 input-contract test; shippability runner exercises the row at /validate-slice Step 5.5.
- AC3: minted in this slice per /critique M1; name harmonized to bare `0_20_0` per /critique-review m-add-1 — assertion literal is bare `"0.20.0"` so the function name drops the `v_` prefix to match.
- AC4: input-contract sub-axis (sentinel + backlog block + Evidence anchor; verifies all 3 preconditions BCR-1 needs to fire correctly at /reflect-time). The /reflect-time OUTPUT sub-axis (position-pinned Addressed line) is covered at /validate-slice via the verification-plan row 4 awk + line-number check per /critique M4 — runs after /reflect injects the Addressed line.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | pyproject version matches VERSION | `$PY -m pytest tests/methodology/test_pyproject_version_matches_version_file.py::test_repro_sc001_pyproject_project_version_matches_version_file -v` exits 0; manual `grep -nE '^version' pyproject.toml` returns the matching literal |
| 2 | Shippability row #54 PASSES | `$PY -m tools.shippability_runner architecture/shippability.md` exits 0; row #54 reports PASS |
| 3 | No stale `v0.20.0` / `13 audit modules` literals in pyproject.toml | `grep -nE "v0\.20\.0\|13 audit modules\|13 tool modules" pyproject.toml` returns no matches; the new pin test (AC3 row above) PASSES |
| 4 | BCR-1 round-trip injected the Addressed line **at the BCR-1-mandated position** (per /critique M4 — position-pinned, not content-only) | After `/reflect` runs: (a) extract the SC-001 block via `awk '/^### SC-001 —/{f=1} /^### SC-002 —/{f=0} f' diagnose-out/backlog.md > /tmp/sc001.txt`; (b) capture `evidence_last_line=$(grep -n "^  - " /tmp/sc001.txt \| tail -1 \| cut -d: -f1)`; (c) capture `addressed_line=$(grep -n "^- \*\*Addressed:\*\*.*slice-054-fix-pyproject-toml-version-drift" /tmp/sc001.txt \| head -1 \| cut -d: -f1)`; (d) ASSERT `addressed_line > evidence_last_line` (BCR-1: Addressed AFTER Evidence sub-list); (e) ASSERT the SC-002 header appears AFTER the addressed line in the original file (BCR-1: Addressed BEFORE next `### SC-NNN`); (f) SC-001 block's existing 6 metadata bullets + Evidence sub-list preserved verbatim above the new line. If the position-pinned awk pattern proves brittle at /build-slice, mint dedicated `tests/methodology/test_bcr_1_backlog_round_trip_end_to_end.py::test_sc001_addressed_position_after_evidence_before_sc002` (allowed scope expansion). |

## Must-not-defer

- [ ] Inclusion-heuristic classification recorded in `design.md` per **MEPD-1** (`agents/critique.md` Dim 7): either (a) born-retired conformance class à la slice-045 (no rule-ID / no methodology-changelog entry / no VERSION bump — discharged-by-name against the real META-1 `## v…`-split assertion) OR (b) new RULE-ID + ADR + methodology-changelog entry + VERSION bump + shippability consumer propagation pin pair per slice-049/050 precedent. Decision must cite precedent by name, not assert it.
- [ ] If route (b) chosen: 4-part PMI-1 atomic bump (VERSION + plugin.yaml `version:` field + methodology-changelog `## vN.N` header + the installed `~/.claude/ai-sdlc-VERSION` leg per AVFS-1).
- [ ] BCR-1 mission-brief.md `**Closes:** SC-001` sentinel header present at the top of THIS file (verified above — M4 sentinel discipline, NOT a bare SC-001 mention elsewhere).
- [ ] Pre-finish suite green: PMI-1 / INST-1 / drift-check / BC-1 / SCMD-1 / PTFCD-1 / PTFFD-1 / STP-1 / OSDG-1 / SOAD-1 / AVFS-1 / MCFS-1 / BCR-1 / TF-1 / WS-1 / ETC-1 / RR-1 / LAYER-EVID-1 / CSP-1 / SUP-1 / LINT-MOCK-1/2/3 / branch-workflow / pipeline-chain.
- [ ] `/critique` runs (critic-required: true — methodology-surface Inclusion-heuristic ride) and any blockers ACCEPTED-FIXED before `/build-slice`.

## Out of scope

- **SC-002** (tomllib used in `validate_slice_layers.py` but not declared — VAL-1 Layer B silently disabled on Python 3.10) — separate slice in Cluster 1.
- **SC-003** (`run_audit` CC=32 refactor in `plugin_manifest_audit.py`) — separate slice in Cluster 1.
- **SC-004** (`plugin_manifest_audit` CLI exit-1 path untested) — separate slice in Cluster 1.
- **SC-024** (`install_audit.py` header carries stale `v0.20.0` / `13 tool modules` narrative) — sibling but different file; separate slice (kept out to preserve focus + AC count discipline).
- **Extending PMI-1 to also gate pyproject.version** (the SC-001 "Suggested approach" alternative — make `tools/plugin_manifest_audit.py` read pyproject.toml and emit a `version-mismatch` violation analogous to its existing plugin.yaml↔VERSION gate). The cheapest path is the standalone `tests/methodology/test_pyproject_version_matches_version_file.py` test, which already exists and already enforces the invariant. `/design-slice` decides whether to extend PMI-1 (heavier, but unifies the gate surface) or keep the standalone test (lighter, AC1-as-shipped). Default to the lighter path unless the design surfaces a concrete reason to unify.
- **Bumping `pyproject.toml requires-python` to >=3.11** (SC-002 territory; out of scope here).
- **Removing the pyproject.toml `[tool.setuptools.package-data]` comment's `v0.20.0` reference** at line 66 (`# The tools package itself has no non-Python data files in v0.20.0.`) is IN scope per AC3 if the chosen approach is "scrub all `v0.20.0` literals from the file" (slice-045 INSTALL.md precedent); /design-slice confirms.

## Dependencies

- Prior slices: [[slice-053-wire-backlog-md-into-slice-and-reflect]] — BCR-1 wire that AC4 dogfoods end-to-end for the first time; [[slice-045-fix-install-pypi-package-name-and-stale-prose]] — born-retired conformance-class precedent + stale-`v0.20.0`-literal scrub precedent (different file but same scrub-class).
- Vault refs: [[diagnose-out/backlog.md#SC-001]] (the closed candidate this slice retires), [[tools/plugin_manifest_audit.py#L207-217]] (PMI-1 plugin.yaml↔VERSION gate, the pattern the new test mirrors), [[architecture/shippability.md#54]] (the row /repro just added).
- Risk register: none directly; R-14 (BCR-1 deterministic axis closed) is incidentally exercised on the round-trip side at AC4.
- Failing repro test: `tests/methodology/test_pyproject_version_matches_version_file.py::test_repro_sc001_pyproject_project_version_matches_version_file` (WRITTEN-FAILING; per BFRD-1 verbal-claim-with-path fallback discharged at slice-054 `/slice` Step 3c — the test lives under the project convention `tests/methodology/` per slice-036 `test_repro_r9_*` / slice-045 `test_install_md_correctness` precedent, not under `tests/bugs/` which does not exist in this repo).

## Mid-slice smoke gate

At ~50% of build (after the **atomic 4-part PMI-1 bump** — VERSION + plugin.yaml + ai-sdlc-VERSION + pyproject.toml all on **0.62.0** — but before any prose scrub):

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m pytest tests/methodology/test_pyproject_version_matches_version_file.py::test_repro_sc001_pyproject_project_version_matches_version_file -v
```

Expected: PASS (`assert '0.62.0' == '0.62.0'`) post-Route-B atomic 4-part bump. If FAIL (e.g., `'0.20.0' == '0.62.0'` or `'0.62.0' == '0.61.0'`), the bump literal is wrong OR a leg lags (typo, wrong VERSION read, wrong table, out-of-order partial bump) — STOP, diagnose, do NOT continue to the prose-scrub or AC3 work. *See design.md §"Mid-slice smoke gate (operational expansion)" for the atomic-bump-order rationale (M3 cross-link).*

## Pre-finish gate

- [ ] All 4 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (Inclusion-heuristic classification recorded; if route (b), 4-part PMI-1 atomic bump complete)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Shippability runner `$PY -m tools.shippability_runner architecture/shippability.md` returns 0 (54/54 PASS)
- [ ] Full methodology test suite green (`$PY -m pytest tests/ --no-header -q` exits 0)
- [ ] All Step 6 audits green (BC-1, PMI-1, INST-1, CAD-1, DR-1, TF-1, WS-1, ETC-1, CSP-1, SUP-1, LINT-MOCK-1/2/3, branch-workflow, pipeline-chain, STP-1, OSDG-1, SOAD-1, AVFS-1, MCFS-1, BCR-1, PTFCD-1, PTFFD-1)
- [ ] AC4 (BCR-1 round-trip) verified: after `/reflect` runs, `diagnose-out/backlog.md` SC-001 block carries the `- **Addressed:** slice-054-fix-pyproject-toml-version-drift on YYYY-MM-DD` line in correct position (AFTER `**Evidence:**`, BEFORE `### SC-002`).
