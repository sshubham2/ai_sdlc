# Slice 045: fix-install-pypi-package-name-and-stale-prose

**Mode**: Standard
**Estimated work**: 0.5 day (SMALL, ~1.5hr)
**Risk retired**: [[risk-register#R-11]] — INSTALL.md install-recipe factual drift (wrong PyPI distribution name + stale version/tool-count prose). Born-retired this slice (per /critique M1 — the canonical no-VERSION-bump conformance-fix retirement surface is the risk-register, not reflection.md). MEPD-1(b) discharged in design.md.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`INSTALL.md` — the INST-1 install recipe a brand-new user executes verbatim — ships the wrong PyPI distribution name (`pip install graphify`; the published package is `graphifyy`) and stale prose ("methodology v0.20.0" while VERSION is 0.54.0; "13 executable methodology tools" while `plugin.yaml` enumerates 25). This slice corrects all three so the documented install actually works and the recipe stops lying about its own version/inventory, with the counts preferably derived so they cannot re-drift.

## Acceptance criteria

1. Every graphify `pip install` invocation in `INSTALL.md` targets the PyPI distribution `graphifyy` (no bare `pip install graphify`); the importable module / CLI name `graphify` is unchanged everywhere (`$PY -m graphify`, `import graphify`, `$PY -m graphify install`).
2. `INSTALL.md` contains no stale `v0.20.0` literal; the methodology-version prose reflects current `VERSION` (0.54.0), expressed so it cannot silently re-staleize (derived from / labelled against `VERSION`).
3. Every "N executable methodology tools" claim in `INSTALL.md` equals the number of `- path: tools/` entries `plugin.yaml` enumerates (25).
4. `README.md:69` and `tutorial-site/Hybrid AI SDLC Pipeline.html:1050` name the PyPI package precisely (`graphifyy`) instead of the vague "else PyPI".
5. The 3 repro tests in `tests/methodology/test_install_md_correctness.py` transition FAIL→PASS and shippability catalog entry #45 runs green.

## Test-first plan

The repro tests already exist (written by `/repro` before this slice, currently FAILING — the FAIL→PASS contrast is the reproduction evidence). Per **TF-1**, `/build-slice` Step 6 refuses finish if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology | tests/methodology/test_install_md_correctness.py | test_install_md_graphify_pip_package_is_graphifyy | PASSING |
| 2 | methodology | tests/methodology/test_install_md_correctness.py | test_install_md_has_no_stale_v0_20_0_literal | PASSING |
| 3 | methodology | tests/methodology/test_install_md_correctness.py | test_install_md_tool_count_matches_plugin_yaml | PASSING |
| 4 | methodology | tests/methodology/test_install_md_correctness.py | test_readme_and_tutorial_name_graphifyy_package | PASSING |
| 5 | methodology | tests/methodology/test_install_md_correctness.py | test_install_md_graphify_pip_package_is_graphifyy | PASSING |
| 5 | methodology | tests/methodology/test_install_md_correctness.py | test_install_md_has_no_stale_v0_20_0_literal | PASSING |
| 5 | methodology | tests/methodology/test_install_md_correctness.py | test_install_md_tool_count_matches_plugin_yaml | PASSING |

(AC4 gained a real regression test `test_readme_and_tutorial_name_graphifyy_package`, authored test-first during build with a genuine FAIL→PASS contrast (README/HTML reverted → test FAILs → re-applied → PASSES) — this is a strict strengthening of the Critic-m2 ACCEPTED-FIXED disposition (which only pinned the exact phrase in design.md), permanently closing the "README/HTML invisible to shippability #45" gap. AC5 = "the repro tests transition FAIL→PASS and shippability #45 runs green" → it IS rows 1-3's three functions; mapped explicitly so TF-1's per-AC `ac-without-row` rule is satisfied without inventing a synthetic function.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | graphify pip target is `graphifyy` | `pytest tests/methodology/test_install_md_correctness.py::test_install_md_graphify_pip_package_is_graphifyy` PASSES; manual grep confirms `graphify` module/CLI refs untouched |
| 2 | no stale `v0.20.0`, version current | `pytest ...::test_install_md_has_no_stale_v0_20_0_literal` PASSES; visual read of the refreshed version prose |
| 3 | tool-count matches plugin.yaml | `pytest ...::test_install_md_tool_count_matches_plugin_yaml` PASSES (claim == 25) |
| 4 | README + tutorial HTML name the package | grep `README.md:69` and the HTML line — both contain `graphifyy`, no remaining bare/vague "else PyPI" without the name |
| 5 | repro green in catalog | run the shippability #45 command end-to-end; 3 passed, 0 failed |

## Must-not-defer

- [ ] No collateral rename of the `graphify` module/CLI anywhere (regression guard — only the `pip install` *distribution* token changes; `$PY -m graphify`, `import graphify`, `graphify install` stay verbatim).
- [ ] Shippability catalog entry #45 actually executes green via its catalogued command (not just the bare test file).
- [ ] `/drift-check` clean after edits (INSTALL.md is INST-1-referenced; no new vault/code divergence introduced).
- [ ] No new stale literal or hardcoded count introduced while editing (prefer derive-from-source phrasing so AC2/AC3 stay green structurally).
- [ ] CAD-1 / PMI-1 / INST-1 self-hosting audits still pass (INSTALL.md prose change must not desync the canonical inventory wording).

## Out of scope

- Two-level (user vs project) install — that is the planned **slice-047 `add-two-scope-install`** (structural; needs design.md + ADR).
- Making `/slice` auto-advance to `/repro` for concretely-specified bugs — that is the planned **slice-046 `add-conditional-repro-auto-advance`** (methodology-surface change).
- Refactoring `tools/install_audit.py` canonical inventory or the INST-1 contract wording in `methodology-changelog.md`.
- Rewriting the tutorial HTML beyond the single package-name phrase at line 1050.
- Bumping `VERSION` or adding a methodology-changelog rule (this is a no-VERSION-bump prose-correctness fix; risk-retirement is recorded in `reflection.md`, not a parentless changelog `###` entry — per the slice-040/R-10 precedent).

## Dependencies

- Repro test (BFRD-1 prerequisite): `tests/methodology/test_install_md_correctness.py` — 3 tests, currently FAILING; one AC (AC5) asserts they PASS at slice end.
- Shippability: [[shippability]] entry #45 (added by `/repro`).
- Vault refs: INST-1 (`INSTALL.md` is the INST-1 install recipe); CAD-1 / PMI-1 self-hosting audits.
- Sibling slices (downstream, NOT prerequisites): slice-046 `add-conditional-repro-auto-advance`, slice-047 `add-two-scope-install` — both depend on a clean slice-045 INSTALL.md baseline.
- Precedent: `skills/discover/SKILL.md:105` already correctly uses `pip install graphifyy[video]` — the canonical correct form to mirror.

## Mid-slice smoke gate

At ~50% of build (after editing `INSTALL.md` only, before touching README / tutorial HTML), run:
```
<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/test_install_md_correctness.py --no-header -q
```
Expected: all 3 tests PASS (the INSTALL.md-scoped facts are fully fixed by the INSTALL.md edit alone; AC4's README/HTML edits are independent). If any still FAIL: STOP, diagnose the regex/wording mismatch, don't continue to AC4.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] TF-1: all test-first-plan rows PASSING
- [ ] Shippability #45 green in the full-catalog run
