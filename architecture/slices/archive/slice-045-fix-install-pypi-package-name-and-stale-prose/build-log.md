# Build log: Slice 045 fix-install-pypi-package-name-and-stale-prose

**Date**: 2026-05-18
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-05-18 00:00 BUILD: branch slice/045-fix-install-pypi-package-name-and-stale-prose created from master (WT had only the slice's own untracked repro test tests/methodology/test_install_md_correctness.py — expected BFRD-1-prelude state, carried onto the slice branch; architecture/ is gitignored so vault edits do not appear in git status)
- 2026-05-18 00:00 BUILD: prerequisite checks clean — CRP-1 exit 0 (critique-review.md present), TPHD-1 harmonization clean (TF-1 rows reference the 3 existing repro fns, no /critique rename), critique CLEAN/user-ratified
- 2026-05-18 00:00 BUILD: plan approved by user (recommended option) — :18 realized as `(methodology v0.54.0 — see \`VERSION\`)` to honor AC2 "labelled against VERSION", explicitly signed off
- 2026-05-18 00:10 BUILD: Task 1 — 7 INSTALL.md edits applied (EDIT-1 :93; EDIT-2 :18/:26/:168/:232; EDIT-3 :22/:150)
- 2026-05-18 00:11 SMOKE: mid-slice gate — 3 repro tests PASS after INSTALL.md edits (FAIL→PASS confirmed)
- 2026-05-18 00:12 BUILD: Task 2 — README.md:69 + tutorial HTML:1050 graphifyy edits applied
- 2026-05-18 00:15 TEST: TF-1 strict FAILed (ac-without-row AC#4/AC#5) — mission-brief TF-1 plan only mapped AC1-3
- 2026-05-18 00:18 BUILD: methodology-correct remediation — added real AC4 test `test_readme_and_tutorial_name_graphifyy_package` (closes Critic-m2 test-blind gap, strict strengthening); authored test-first: reverted README/HTML via in-place Edit reverse-edits (NOT git — BC-PROJ-3/BC-GLOBAL-2 compliant)
- 2026-05-18 00:19 TEST: AC4 test FAILs against reverted README/HTML (1 failed, 3 passed) — genuine FAIL→PASS contrast established
- 2026-05-18 00:20 BUILD: Task 2 re-applied (README/HTML graphifyy) → full file 4 passed
- 2026-05-18 00:21 BUILD: mission-brief TF-1 plan expanded to 7 rows (AC1-5 mapped); shippability #45 extended to cover README/HTML naming; design.md :18 deviation recorded
- 2026-05-18 00:25 TEST: pre-finish audits — TF-1 strict clean (7/7 PASSING), BRANCH-1 clean, WIRE-1 clean, CRP-1 clean, UTF8-STDOUT-1 clean, PCA-1 clean, BCI-1 PASS, MCFS-1 PASS, STP-1 clean, LINT-MOCK-1 clean, BC-1 exit 0 (Critical rules satisfied/N-A — see Summary)

## Summary (filled at slice end)

### Plan executed
- Task 1 — INSTALL.md 7 edits (EDIT-1 :93 graphify→graphifyy; EDIT-2 :18/:26/:168/:232 v0.20.0 removal; EDIT-3 :22/:150 13→25): DONE
- Mid-slice smoke gate — 3 repro tests after Task 1: PASS (FAIL→PASS confirmed)
- Task 2 — README.md:69 + tutorial HTML:1050 (AC4 exact phrase): DONE (test-first: reverted → AC4 test FAIL → re-applied → PASS)
- TF-1 remediation — added real AC4 test + expanded mission-brief TF-1 plan to 7 rows (AC1-5): DONE
- Pre-finish gate + Step 6 audits + /drift-check: DONE — all green

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: `pytest tests/methodology/test_install_md_correctness.py` → 3 passed (after the 7 INSTALL.md edits, before AC4 README/HTML work). Final full suite: 4 passed (AC1-5).

### Pre-finish gate
- [x] All 5 ACs pass with evidence — 4-test suite (AC1/2/3/4) + AC5 = the 3 install tests + shippability #45 catalog command all green; AC4 via `test_readme_and_tutorial_name_graphifyy_package`
- [x] Must-not-defer addressed — no collateral graphify module/CLI rename (grep-verified: `graphifyy` ×1 at :93 only; 5 module/CLI refs intact); shippability #45 green via catalogued command; /drift-check clean; no new stale literal (repro tests 2/3 guard); CAD-1 + PMI-1 + INST-1 all clean
- [x] /drift-check pass — drift-log.md 2026-05-19 00:30: 0 blockers, 0 majors
- [x] Mid-slice smoke regression — final suite 4/4 still PASS
- [x] No new debug code — git diff = exactly 9+9 intended lines; the 2 `print(`/`TODO` grep hits (INSTALL.md:165, HTML:786) are pre-existing, slice-untouched
- [x] TF-1 strict clean (7/7 PASSING); BRANCH-1 / WIRE-1 / CRP-1 / UTF8-STDOUT-1 / PCA-1 / BCI-1 / MCFS-1 / STP-1 / LINT-MOCK-1 clean; BC-1 exit 0 (Critical rules satisfied/N-A)

### BC-1 Critical-rule disposition
- BC-PROJ-3 / BC-GLOBAL-2 (no git revert of uncommitted WIP): SATISFIED — test-first revert of README/HTML used in-place Edit reverse-edits, never `git checkout/restore/stash`.
- BC-PROJ-7 (new audit-tool wiring): N/A — slice adds no `tools/*.py` with main() (only a test module).
- Important BC-PROJ-4/5/6/8 + BC-GLOBAL-1: satisfied/N-A — count is plugin.yaml-anchored via shippability #45; R-11 carries a real `**Status**: retired` field line; repro test uses live on-disk reads; no LLM-fence parsing.

### Deferrals (if any)
none

### Design deviations (if any)
- :18 realized as `(methodology v0.54.0 — see \`VERSION\`)` rather than design EDIT-2's bare `(methodology v0.54.0)` — AC-faithful strengthening of design's "matches VERSION" resolution to honor mission-brief AC2's "labelled against VERSION" wording; user-approved at plan-mode gate. Not a scope change. **design.md updated** (EDIT-2 :18 row records the build deviation).
- AC4 gained a real regression test (`test_readme_and_tutorial_name_graphifyy_package`) authored test-first, beyond the Critic-m2 ACCEPTED-FIXED disposition (which only pinned the phrase in design.md). Strict strengthening, not a contradiction — permanently closes the "README/HTML invisible to shippability #45" gap. mission-brief TF-1 plan + shippability #45 updated to reflect; no re-triage needed (coverage added, nothing weakened).

### Files changed
- `INSTALL.md` (7 lines: 18, 22, 26, 93, 150, 168, 232), `README.md` (line 69), `tutorial-site/Hybrid AI SDLC Pipeline.html` (line 1050)
- `tests/methodology/test_install_md_correctness.py` (created by /repro prelude; +AC4 test `test_readme_and_tutorial_name_graphifyy_package` added this build)
- architecture/ vault (gitignored — not in git diff): mission-brief.md, design.md, critique.md, critique-review.md, milestone.md, build-log.md, drift-log.md, risk-register.md (R-11 born-retired), shippability.md (#45), slices/_index.md
