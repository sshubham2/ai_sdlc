# Validation: Slice 045 fix-install-pypi-package-name-and-stale-prose

**Date**: 2026-05-19
**Result**: PASS

## Per-criterion results

### AC1: Every graphify `pip install` invocation in INSTALL.md targets `graphifyy`; module/CLI `graphify` unchanged
- **Status**: PASS
- **Evidence**: `INSTALL.md:93` = `…otherwise \`$PY -m pip install graphifyy\`.` (only bare-pip line, now correct). `graphifyy` appears exactly once in INSTALL.md (line 93). All module/CLI refs intact and unchanged: `$PY -m graphify --help` (L58, L91, L95, L174), `$PY -m graphify install` (L99). No `-m graphifyy` / `import graphifyy` anywhere. Backed by `test_install_md_graphify_pip_package_is_graphifyy` (PASSING).
- **Notes**: must-not-defer "no collateral rename of graphify module/CLI" satisfied with evidence.

### AC2: No stale `v0.20.0` literal in INSTALL.md; version prose reflects current VERSION, labelled against VERSION
- **Status**: PASS
- **Evidence**: `v0.20.0` literal count in INSTALL.md = **0** (was 4 at lines 18/26/168/232). `INSTALL.md:18` now `The AI SDLC pipeline (methodology v0.54.0 — see \`VERSION\`):` (current value + source-of-truth label per AC2 "labelled against VERSION"). :26 → `Per **INST-1**:` (rule ID stable anchor); :168 → `…predating the \`pyproject.toml\` packaging…` (factually equivalent — pyproject.toml was the INST-1/v0.20.0 change, confirmed via git log at meta-Critic); :232 → `…drift from its canonical inventory.` (no literal, no over-claimed "current" — Critic m1). Backed by `test_install_md_has_no_stale_v0_20_0_literal` (PASSING).

### AC3: Every "N executable methodology tools" claim equals plugin.yaml's enumerated tool count
- **Status**: PASS
- **Evidence**: INSTALL.md claims (lines 22, 150) both = `25`; `plugin.yaml` `- path: tools/` entries = `25`. Match. Backed by `test_install_md_tool_count_matches_plugin_yaml` (PASSING) — the standing structural re-drift guard (shippability #45).

### AC4: README.md:69 + tutorial HTML:1050 name the PyPI package `graphifyy` precisely
- **Status**: PASS
- **Evidence**: `README.md:69` = `…if present, else the \`graphifyy\` PyPI package)`. `tutorial-site/Hybrid AI SDLC Pipeline.html:1050` = `…if present, else the <code>graphifyy</code> PyPI package).</li>` (markup preserved). Backed by the build-added `test_readme_and_tutorial_name_graphifyy_package` (PASSING) — authored test-first with genuine FAIL→PASS contrast (README/HTML reverted → FAIL → re-applied → PASS), strictly strengthening the Critic-m2 ACCEPTED-FIXED disposition.

### AC5: The repro tests transition FAIL→PASS and shippability #45 runs green
- **Status**: PASS
- **Evidence**: FAIL contrast captured twice (at `/repro`: 3 FAILED; and at the AC4 test-first step: 1 FAILED against reverted README/HTML). PASS now: `pytest tests/methodology/test_install_md_correctness.py` → **4 passed**. Shippability #45 executed via the canonical SRSC-1 runner inside the full catalog (below) — PASS.

## Multi-instance validation
**Required?**: no (documentation/prose slice — no multi-user/device/account surface)
**Result**: not-applicable

## Layered safety checks (VAL-1)
- **Layer A (credentials)**: 0 secrets — clean
- **Layer B (dependency hallucination)**: 0 import findings (only changed `.py` is the test module; imports `re`, `pathlib`, `tests.methodology.conftest` — resolved via `--imports-allowlist tests`)
- Invocation: `validate_slice_layers --slice … --changed-files INSTALL.md README.md "tutorial-site/Hybrid AI SDLC Pipeline.html" tests/methodology/test_install_md_correctness.py --imports-allowlist tests` → clean, both layers passed

## WS-1 / ETC-1
- Walking-skeleton: false → WS-1 default-off (n/a, not a walking-skeleton slice)
- Exploratory-charter: false → ETC-1 default-off (n/a, no charter declared)

## Shippability catalog regression check (Step 5.5)
- **SCMD-1 pre-gate**: clean — 45 rows; 465 cited fns; incidental=0, essential_registered=2, essential_unregistered=0
- **PTFCD-1 pre-gate**: clean — 45 rows, 275 test-path tokens, all files + cited functions exist (incl. the new AC4 test function)
- **SRSC-1 canonical runner** (`tools.shippability_runner architecture/shippability.md`): **45 row(s), 45 PASS, 0 FAIL** — no past slice regressed by slice-045; #45 PASS
- No "Shippability regressions" section needed.

## Reality surprises
- None. The only mid-build surprise was the TF-1 `ac-without-row` gate (AC4/AC5 unmapped) — not a reality surprise about the slice's domain but a methodology-plan completeness gap, resolved during build by adding a real AC4 test (strengthening) and mapping AC5 to its three constituent tests. No impact on next slice; no risk-register entry warranted.
