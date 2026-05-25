# Build log: Slice 061 fix-install-python-detection-and-prompt-fallback

**Date**: 2026-05-23
**Result**: SHIPPED-WITH-DEFERRALS (one user-approved deferral: pre-existing slice-060 R-15-class stale-archive-path defect in `tests/skills/code_review/test_code_review_skill.py::test_self_dogfood_produces_code_review_md_on_slice_060`; slice-062 nominated for fix + corpus-backstop scope extension)

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-05-23 14:00 BUILD: slice/061 branch created from master; one untracked file (repro test) carried across
- 2026-05-23 14:01 BUILD: TPHD-1 pre-flight clean; TF-1 plan AC#5 row added (slice-045 regression-guard); test_first_audit clean (5 rows: PASSING=1, WRITTEN-FAILING=3, PENDING=1)
- 2026-05-23 14:02 BUILD: plan approved (10 tasks; mid-slice smoke at task 6; pre-finish at task 9)
- 2026-05-23 14:05 BUILD: task 1 PASS — AC4 regression-guard test authored test-first; _step_1_section helper added; pytest pre-edit run = 3 FAIL (AC1-3) + 1 PASS (AC4 as expected — chain already at L56)
- 2026-05-23 14:10 BUILD: task 2-5 PASS — INSTALL.md edits applied: Step 1 unchanged (regression-guard pins detection chain); Step 2 No-Python row replaced with 3-option ASK gate + path-validation bash fence (dynamic MIN_PY from pyproject.toml) + retry semantics (1 retry on path validation; "I'll wait" option-removed-on-retry); Step 2 conda-default uses inline-recompute; Step 3a uses inline-recompute (+ explicit no-$BOOT_PYTHON comment)
- 2026-05-23 14:11 SMOKE: mid-slice smoke gate PASS 4/4 — AC1-3 flipped FAIL→PASS; AC4 stays PASS
- 2026-05-23 14:15 BUILD: task 7 PASS — R-16 born-retired + R-17 open-mitigating appended to risk-register.md; RR-1 audit clean (17 risks: 10 retired / 5 mitigating / 2 open / 0 accepted; violations=0)
- 2026-05-23 14:16 BUILD: task 8 PASS — TF-1 plan statuses bumped: 5/5 PASSING
- 2026-05-23 14:20 TEST: Step 6 audit batch 1 PASS — TF-1 strict-pre-finish clean (5/5 PASSING); BC-1 12 rules apply (Critical BC-PROJ-3/7 + BC-GLOBAL-2 trigger-keyword-fired but check-semantics N/A — no git-revert pattern + no new tools/*.py); BRANCH-1 clean on slice/061 branch; UTF8-STDOUT-1 clean 27/27; CRP-1 clean; PCA-1 clean 9-skill chain
- 2026-05-23 14:22 FINDING: BC-PROJ-11 surfaced — `Python 3.10 or newer` literal at INSTALL.md L73 contradicted same-sentence "never hardcoded" claim; reworded to fully-dynamic `MIN_PY=$(grep ... pyproject.toml ...)` form per slice-058 lesson; 8/8 ACs + slice-045 regression tests still PASS post-fix; INSTALL.md now has ZERO hardcoded version literals
- 2026-05-23 14:25 TEST: Step 6 audit batch 2 PASS — BCI-1 clean; MCFS-1 clean; STP-1 clean (1 file skip-with-note: permanent syntax_error.py fixture); AVFS-1 clean; TVFS-1 clean; WIRE-1 clean; PMI-1 clean (26 skills / 6 agents / 27 tools / v0.64.0); INST-1 clean (26/26 / 6/6 / 4/4 / 27/27)
- 2026-05-23 14:28 DEFERRAL: pre-existing slice-060 R-15-class stale-archive-path defect surfaced — `tests/skills/code_review/test_code_review_skill.py::test_self_dogfood_produces_code_review_md_on_slice_060` pins active-path `architecture/slices/slice-060-add-code-review-skill/code-review.md` but slice-060 was archived to `archive/slice-060-.../code-review.md`. Pre-existing on master (verified via `git log --oneline -- tests/skills/code_review/`: only commit is slice-060's `69320da`). Slice-056's `_resolve_slice_dir` helper + corpus class-closure backstop are scoped to `tests/methodology/*.py` — do NOT cover `tests/skills/**/*.py`. User-approved deferral via structured-options AskUserQuestion at TRI-1-equivalent (slice-055 precedent: "shippability dogfood surfaced a pre-existing slice-054 stale-archive-path failure ... user-approved deferral logged"). slice-062 nomination: (a) repoint this test via `_resolve_slice_dir(60)`, (b) extend slice-056 corpus class-closure backstop scope to `tests/skills/**/*.py` + `tests/agents/**/*.py`. SRSC-1 row #60 will FAIL at slice-061 /validate-slice with this single known regression (user-authorized continuation per slice-055 precedent).
- 2026-05-23 14:35 FINDING: /code-review auto-advance hit AGENT-UNSPAWNABLE — `Agent type 'code-review' not found` from runtime. `~/.claude/agents/code-review.md` exists on disk (installed by slice-060) and `agents/code-review.md` is present at HEAD, but this Claude Code session was started BEFORE slice-060 merged to master at commit 63439c6; the agent registry was loaded at session start and does NOT hot-reload on agent-file-write. The session's static available-agents list (per system-context at start): claude, claude-code-guide, critic-calibrate, critique, critique-review, diagnose-narrator, Explore, field-recon, general-purpose, Plan, statusline-setup — `code-review` absent. User-ratified skip via structured-options AskUserQuestion (Option 1: skip + AUTO-ADVANCE; rationales: /code-review v1 is advisory-only, slice-061 M-add-1 Option (b) excluded INSTALL.md from /code-review v1 scope anyway, structural coverage intact via AC1-AC4 + slice-045/058 + INST-1). R-18 candidate documented in code-review.md for /reflect promotion: "newly-installed Claude Code subagents not picked up until session restart — recurring class for any slice immediately following an agent-shipping slice in the same session". slice-061 is the witnessed N=1 (slice-060 shipped /code-review; slice-061 = N+1 in same session).

## Summary

### Plan executed (10 tasks)

| # | Task | Status |
|---|------|--------|
| 1 | Author AC4 regression-guard test (test-first) | PASS — `_step_1_section` helper added; `test_install_md_step_1_preserves_python3_or_python_detection_chain` authored; pre-edit pytest = 3 FAIL (AC1-3) + 1 PASS (AC4) |
| 2 | Edit INSTALL.md Step 1 | PASS — no change (regression-guard pins existing chain at L56 verbatim) |
| 3 | Edit INSTALL.md Step 2 No-Python row | PASS — bare hard-fail replaced with 3-option SOAD-1 ASK gate + dynamic-`pyproject.toml`-floor path-validation bash fence + retry semantics (1 retry on validation; "I'll wait" option-removed-on-retry) + version-agnostic installer suggestions |
| 4 | Edit INSTALL.md Step 2 conda-default row | PASS — `python3 -m venv` → `$(command -v python3 \|\| command -v python) -m venv` |
| 5 | Edit INSTALL.md Step 3a | PASS — `python3 -m venv ~/.claude/.venv` → `$(command -v python3 \|\| command -v python) -m venv ~/.claude/.venv` + explicit no-`$BOOT_PYTHON` comment |
| 6 | Mid-slice smoke gate | PASS 4/4 — AC1-3 flipped FAIL→PASS; AC4 stays PASS |
| 7 | Append R-16 + R-17 to risk-register.md | PASS — R-16 born-retired with Notes paragraph (broader-class coverage); R-17 open `mitigating` with candidate-fix prose; RR-1 audit clean (17 risks, 0 violations) |
| 8 | Update TF-1 plan statuses to PASSING | PASS — 5/5 PASSING |
| 9 | Pre-finish gate | PASS-with-1-deferral — 14 Step-6 audits clean; 28 install-class regression tests PASS; 874 methodology+skills+agents tests PASS; 1 deferred (slice-060 R-15-class) |
| 10 | Write build-log.md | THIS — events + summary completed |

### Mid-slice smoke gate

**Result**: PASS 4/4

**Evidence**:
```
tests/methodology/test_install_md_python_detection.py::test_install_md_step_3a_does_not_hardcode_python3_venv PASSED
tests/methodology/test_install_md_python_detection.py::test_install_md_step_2_no_python_branch_asks_user_for_interpreter PASSED
tests/methodology/test_install_md_python_detection.py::test_install_md_step_1_preserves_python3_or_python_detection_chain PASSED
tests/methodology/test_install_md_python_detection.py::test_install_md_step_2_conda_default_does_not_hardcode_python3_venv PASSED
```

### Pre-finish gate

- [x] All ACs pass with evidence — 5/5 PASSING in TF-1 plan; see validation.md (next step)
- [x] Must-not-defer addressed — 10 items: Step 3a idempotency preserved (`If $PY exists → skip`); path-validation Bash-tool routing pinned; Step 1 chain preserved (regression-guard AC4); "I'll wait" branch 1-attempt-bound (option-removed-on-retry); Python-floor dynamic via `pyproject.toml`; L71 stale `3.11+` removed; installer suggestions de-versioned; EOL/cross-machine portability (no platform-specific instructions); SOAD-1 conformance (AC2); re-run idempotency
- [x] Drift-check pass — vault graph rebuilt cleanly (551 files, 0 errors)
- [x] Smoke regression check pass — 4/4 still PASSING after BC-PROJ-11 prose harmonization
- [x] No debug code — no TODOs / FIXMEs / debug prints added
- [x] Mock-budget lint N/A — no test files in Python/TS/Go mock-lint scope changed substantively (one .py test file with no `mock` imports)
- [x] WIRE-1 clean — exemption rationale `rationale: test module — pytest is the consumer` (canonical slice-051 form)
- [x] BC-1 — 12 rules apply (3 Critical / 9 Important); ALL trigger-keyword-fired but check-semantics N/A or already-discharged: BC-PROJ-3/BC-GLOBAL-2 (no git-revert pattern in this slice); BC-PROJ-7 (no new tools/*.py); BC-PROJ-4/5/8/9 (slice doesn't change parse rules / rename / add vault tooling / add tools module); BC-PROJ-2/BC-GLOBAL-1 (no LLM-fence parsing); BC-PROJ-6 (R-16 retired correctly via `**Status**: retired` flip, RR-1 verified); BC-PROJ-10 (MEPD-1(b) discharge by name vs META-1 assertion in design.md + mission-brief.md); BC-PROJ-11 (caught at audit-time: `Python 3.10 or newer` literal at L73 removed in same edit block, INSTALL.md now has ZERO hardcoded version literals)
- [x] TF-1 strict-pre-finish — 5/5 PASSING (0 PENDING / 0 WRITTEN-FAILING)
- [x] BRANCH-1 — clean on `slice/061-fix-install-python-detection-and-prompt-fallback`
- [x] UTF8-STDOUT-1 — clean 27/27
- [x] CRP-1 — clean (critique-review.md present, audit-clean structurally)
- [x] PCA-1 — clean 9-skill canonical chain
- [x] BCI-1 — clean (live build-checks files match git-tracked canonical fixtures)
- [x] MCFS-1 — clean (in-repo methodology-changelog.md == installed, modulo line endings)
- [x] STP-1 — clean (1 file skip-with-note for permanent `syntax_error.py` fixture per ADR-037)
- [x] AVFS-1 — clean (in-repo VERSION == installed `~/.claude/ai-sdlc-VERSION`)
- [x] TVFS-1 — clean (installed `ai-sdlc-tools` pip package == in-repo VERSION)
- [x] WIRE-1 — clean
- [x] PMI-1 — clean (26 skills / 6 agents / 27 tools / v0.64.0)
- [x] INST-1 — clean (26/26 / 6/6 / 4/4 / 27/27 / methodology v0.64.0)
- [x] RR-1 — clean (17 risks, 0 violations, R-16 retired + R-17 mitigating both correctly parsed)
- [x] Full methodology + skills + agents suite — **874 passed, 1 deselected** (the deselected = user-approved deferral, documented below)

### Deferrals

**One user-approved deferral** (slice-055 precedent: shippability dogfood surfaces pre-existing prior-slice defect; user-approved at TRI-1-equivalent gate):

- **`tests/skills/code_review/test_code_review_skill.py::test_self_dogfood_produces_code_review_md_on_slice_060`** — pre-existing slice-060 R-15-class stale-archive-path defect. The test pins `architecture/slices/slice-060-add-code-review-skill/code-review.md` (active-side path) but slice-060 was archived to `archive/slice-060-.../code-review.md`. Verified pre-existing on master (`git log --oneline -- tests/skills/code_review/`: only commit is slice-060's `69320da`; slice-061 made NO changes to this file). Slice-056's `_resolve_slice_dir(N)` helper + corpus class-closure backstop are scoped to `tests/methodology/*.py` — do NOT cover `tests/skills/**/*.py` or `tests/agents/**/*.py`.
  - **User-approved**: yes (via structured-options AskUserQuestion at pre-finish, 2026-05-23).
  - **Followup**: slice-062 nomination (two coupled fixes): (a) repoint this test via `_resolve_slice_dir(60)` (using slice-056's helper), AND (b) extend the slice-056 corpus class-closure backstop's scope from `tests/methodology/*.py` to also include `tests/skills/**/*.py` + `tests/agents/**/*.py` so the R-15 class is structurally closed across ALL test trees, not just methodology. After (a)+(b) ship, SRSC-1 row #60 will green again.
  - **SRSC-1 impact**: shippability_runner row #60 FAILs at slice-061 /validate-slice with this single known regression. User-authorized continuation per slice-055 precedent.
  - **Why this isn't a slice-061 bug**: slice-061 makes no changes to `tests/skills/`, `tests/agents/`, the `/code-review` skill, or slice-060's archive. The defect was latent in slice-060's shipped state and surfaced for the first time at slice-061's pre-finish because slice-061 is the first slice AFTER slice-060's archival to run the full methodology suite.

### Design deviations

**None.** The plan executed verbatim. The BC-PROJ-11 inline-fix at task 9 was a per-rule audit-time finding (not a plan deviation) — the `Python 3.10 or newer` literal was a residual hardcoded version that the design.md's M5 fix should have flagged but didn't; caught at BC-1 audit time and fixed in the same Step 6 phase. Documented as a calibration note for /reflect (the slice's first-Critic + meta-Critic both missed this one — the same class as M5/m3 but at a sibling surface — interesting M-add candidate for `/critic-calibrate` cumulative tracking, N=1 watch-list).

### Files changed

- `INSTALL.md` (Step 1 unchanged; Step 2 No-Python branch replaced with structured-options ASK + path-validation bash fence + retry bounds + version-agnostic installer suggestions + dynamic Python-floor read; Step 2 conda-default uses inline-recompute; Step 3a uses inline-recompute + explicit no-`$BOOT_PYTHON` comment; ZERO hardcoded version literals remain)
- `tests/methodology/test_install_md_python_detection.py` (added at /repro Step 3 with 3 WRITTEN-FAILING assertions; extended at /build-slice task 1 with `_step_1_section` helper + AC4 `test_install_md_step_1_preserves_python3_or_python_detection_chain` regression-guard)
- `architecture/risk-register.md` (R-16 born-retired entry + R-17 open-mitigating entry appended; 17 risks total post-slice)
- `architecture/shippability.md` (row #61 wired at /repro Step 5 — cites `test_install_md_python_detection.py`)
- `architecture/slices/slice-061-fix-install-python-detection-and-prompt-fallback/` (mission-brief.md, design.md, critique.md, critique-review.md, milestone.md, build-log.md authored by the slice pipeline)
