# Validation: Slice 061 fix-install-python-detection-and-prompt-fallback

**Date**: 2026-05-23
**Result**: PASS (with one documented user-approved deferral on a pre-existing slice-060 shippability row — NOT a slice-061 regression)

## Per-criterion results

### AC1: Step 3a uses detected interpreter (no bare hardcoded `python3 -m venv`)

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_install_md_python_detection.py::test_install_md_step_3a_does_not_hardcode_python3_venv -v` → PASSED. Section-scoped regex `\bpython3\s+-m\s+venv\b` against `_step_3a_section(INSTALL.md)` returns zero matches. The real INSTALL.md Step 3a sub-section (L83-L89) now reads `Else: $(command -v python3 || command -v python) -m venv ~/.claude/.venv` — inline-recompute pattern; the bare `python3 -m venv` literal is gone.
- **Notes**: Verified by reading INSTALL.md directly — the inline-recompute mirrors Step 1's pre-flight detection chain `command -v python3 || command -v python` so the same interpreter Step 1 detected is the one Step 3a uses to create the venv.

### AC2: Step 2 No-Python branch asks via SOAD-1 structured options

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_install_md_python_detection.py::test_install_md_step_2_no_python_branch_asks_user_for_interpreter -v` → PASSED. Regex check confirms the `**No Python found**` branch body contains `AskUserQuestion` reference. The brittle `Install Python 3.11+ and re-run` terminal is removed.
- **Notes**: The new branch (INSTALL.md L71-L83) presents 3 structured options (Provide interpreter path / Install Python — I'll wait / Abort install) with a bounded retry mechanism. Path-validation runs via Bash tool (Git-Bash on Windows) with a dynamic `MIN_PY=$(grep -E '^requires-python' "$AI_SDLC_DIR/pyproject.toml" ...)` floor read — no hardcoded version literals.

### AC3: Step 2 conda-default uses detected interpreter

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_install_md_python_detection.py::test_install_md_step_2_conda_default_does_not_hardcode_python3_venv -v` → PASSED. The conda-ambiguity row (INSTALL.md L84) now reads `Default to $(command -v python3 || command -v python) -m venv if user has no preference.`
- **Notes**: The conda default tracks the Step 3a execution prose so the prose default cannot reintroduce the bug if a future maintainer copies it.

### AC4: Step 1 detection chain preserved (section-scoped regression-guard)

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_install_md_python_detection.py::test_install_md_step_1_preserves_python3_or_python_detection_chain -v` → PASSED. New `_step_1_section` helper at the test file scopes the assertion to the `## Step 1:` section bounded by `## Step 2:` (mirrors existing `_step_3a_section` / `_step_2_section` pattern at L58-L81). Verified by reading INSTALL.md L56 — `command -v python3 || command -v python` chain is present verbatim inside Step 1.
- **Notes**: This was a meta-Critic M3 fix — without section-scoping, a future edit could move the chain out of Step 1 into a misleading comment elsewhere and AC4 would silently false-green. The scoped form pins the chain to its actual contract surface.

### AC5: No regression to slice-045's INSTALL.md prose-pin tests

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_install_md_correctness.py -v` → 4 passed (PyPI package name `graphifyy` preserved; no stale `v0.20.0` literal; tool-count claims match `plugin.yaml`'s 27; README + tutorial HTML name `graphifyy`).
- **Notes**: TF-1 plan row cites `test_install_md_graphify_pip_package_is_graphifyy` as the canonical anchor; the 3 sibling functions run alongside it in the methodology suite. All 4 pass.

## Multi-instance validation

**Required?**: No — single-machine INSTALL.md prose-correctness fix; no multi-user / multi-device behavior involved.
**Result**: not-applicable
**Evidence**: The slice's behavioral claim is single-machine (a user on a system with only `python` on PATH can complete `INSTALL.md` successfully). The validation surfaces are (a) the 4 prose-pin tests against real INSTALL.md content (PASS); (b) the slice-045 regression-guard (PASS); (c) INST-1 audit cross-check (PASS at /build-slice Step 6).

## Layered safety checks (VAL-1)

- **Layer A — Credential scan**: 0 secrets detected across 4 changed files (INSTALL.md / risk-register.md / shippability.md / test_install_md_python_detection.py). PASS.
- **Layer B — Dependency hallucination check**: 0 hallucinated imports. The test file imports `re`, `pathlib.Path` (stdlib), `tests.methodology.conftest.REPO_ROOT` (tests-allowlist). PASS.

## Shippability catalog regression check (Step 5.5)

**Pre-catalog gates**:
- SCMD-1: clean (61 rows; 546 cited fns; incidental=0; essential_unregistered=0). PASS.
- PTFCD-1 sub-mode (b): clean (61 rows; 320 test-path tokens; all files + cited functions exist). PASS.

**Catalog runner (SRSC-1)**: 1 failed, 5 passed (out of the 6 rows executed for this slice's diff scope — the runner only re-executes rows touched/relevant to the slice's changed files; row 60 happened to be one).

**Shippability regressions**:

- **Row #60 — `tests/skills/code_review/test_code_review_skill.py::test_self_dogfood_produces_code_review_md_on_slice_060`**: FAIL
  - **Output**: `AssertionError: missing <HOME>/ai_sdlc/architecture/slices/slice-060-add-code-review-skill/code-review.md`
  - **Root cause**: pre-existing slice-060 R-15-class stale-archive-path defect. The test pins the active-side path `architecture/slices/slice-060-.../code-review.md` but slice-060 was archived after shipping (the `code-review.md` is now at `architecture/slices/archive/slice-060-add-code-review-skill/code-review.md` — verified present).
  - **NOT a slice-061 regression**: verified pre-existing on master via `git log --oneline -- tests/skills/code_review/` (only commit is slice-060's `69320da`; slice-061 made NO changes to this file). The slice-056 `_resolve_slice_dir(N)` helper + corpus class-closure backstop are scoped to `tests/methodology/*.py` — do NOT cover `tests/skills/**/*.py` (this is the gap that needs to close in slice-062).
  - **Disposition**: user-approved deferral via structured-options AskUserQuestion at /build-slice Step 6 (2026-05-23, 14:28). Slice-061 ships with this single documented pre-existing-regression deferral; slice-062 is nominated to (a) repoint this test via `_resolve_slice_dir(60)` AND (b) extend the slice-056 corpus class-closure backstop's scope from `tests/methodology/*.py` to also cover `tests/skills/**/*.py` + `tests/agents/**/*.py` so the R-15 class is structurally closed across all test trees.
  - **Slice-055 precedent**: this exact disposition shape was applied at slice-055 ("shippability dogfood surfaced a pre-existing slice-054 stale-archive-path failure ... user-approved deferral logged at /build-slice TRI-1"). Slice-061's case is the N=2 instance of the same recurring pattern; the slice-062 corpus-backstop scope-extension is what structurally retires the recurrence.

## Reality surprises

Two encountered during the slice, both logged for /reflect promotion:

1. **R-18 candidate** (logged in code-review.md): newly-installed Claude Code subagents are NOT hot-loaded into the running session — the agent registry is loaded at session start. Slice-060 shipped the `/code-review` agent; slice-061's auto-advance to `/code-review` in the same Claude Code session hit `agent-unspawnable` because the registry was loaded before slice-060 merged. Witnessed N=1; recurring class for any slice immediately following an agent-shipping slice in the same session. User-ratified skip via structured-options at TRI-1-equivalent gate; structural coverage delegated to existing test surfaces (per slice-061 TRI-1 M-add-1 Option (b) — INSTALL.md was out-of-scope for /code-review v1 anyway). Candidate fixes documented in code-review.md.

2. **BC-PROJ-11 inline catch at /build-slice task 9**: the `Python 3.10 or newer` literal at INSTALL.md L73 contradicted the same sentence's "never hardcoded as a literal minor version" claim — caught by the BC-PROJ-11 grep at Step 6 BC-1 audit (NOT by the first-Critic, NOT by the meta-Critic, NOT by the M5/m3 fix block). Fixed in same Step 6 phase by rewording the prose to a fully-dynamic `MIN_PY=$(grep ... pyproject.toml ...)` form. Recorded as a `/critic-calibrate` watch-list candidate (N=1): "first-Critic + meta-Critic blind to sibling-literal-instance of a class one of their findings IS addressing — the M5 fix targeted the version-probe site but the installer-guidance prose carried an instance of the same class that neither layer surfaced." The audit-time backstop (BC-PROJ-11 + BC-1 fan-out) caught it cleanly at intended latency — slice-037 audit-vs-real-artifact law N+1 confirmation.

## Aggregate

- **Slice's own ACs**: 5/5 PASS
- **VAL-1**: clean (Layer A 0 secrets / Layer B 0 hallucinations)
- **SCMD-1 + PTFCD-1**: clean
- **Shippability catalog**: 1 user-approved-deferred pre-existing failure (slice-060 R-15-class; NOT a slice-061 regression); all other rows PASS
- **Reality surprises**: 2 captured for /reflect (R-18 candidate; BC-PROJ-11 calibration watch-list candidate)

Per PCA-1's `Result: PASS` auto-advance criterion + slice-055 user-approved-deferral precedent: aggregate **PASS**; auto-advance to `/reflect` is permitted.
