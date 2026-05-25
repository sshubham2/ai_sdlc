# Slice 061: fix-install-python-detection-and-prompt-fallback

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-16 (to be born-retired in this slice — INSTALL.md python-detection brittleness; slice-045 R-11 born-retired precedent for user-reported INSTALL.md recipe defects)
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false
**Risk tier**: high
**Critic-required**: true (in-house methodology surface trigger per slice-010 MCT-1; risk-tier high mandates re-critique on any design change)

## Intent

INSTALL.md (the INST-1 install recipe Claude reads literally during installs) hardcodes `python3 -m venv ~/.claude/.venv` in Step 3a and references `python3 -m venv` as the default in Step 2's conda-ambiguity row, even though Step 1's pre-flight detects either `command -v python3` or `command -v python`. On systems where the Python interpreter is invoked as `python` (not aliased as `python3` — Windows installers don't register `python3.exe` by default; some Linux distros without `python-is-python3`; bare macOS symlinks), Step 3a's literal execution fails with `python3: command not found` / `'python3' is not recognized` even though Python IS installed. Step 2's `**No Python found**` ambiguity branch hard-fails with `Install Python 3.11+ and re-run` instead of asking the user for the interpreter path (the user may have Python installed but not on PATH, or in a non-standard location). This slice rewires INSTALL.md to use the detected interpreter end-to-end and converts the missing-Python branch into a SOAD-1 structured-options ASK gate that offers either "supply the interpreter path" or "install Python (and we'll wait)".

## Acceptance criteria

1. `tests/methodology/test_install_md_python_detection.py::test_install_md_step_3a_does_not_hardcode_python3_venv` PASSES — Step 3a uses the interpreter Step 1 detected (captured variable or inline `command -v python3 || command -v python` recompute), no bare hardcoded `python3 -m venv` literal in the Step 3a sub-section.
2. `tests/methodology/test_install_md_python_detection.py::test_install_md_step_2_no_python_branch_asks_user_for_interpreter` PASSES — Step 2's `**No Python found**` branch directs Claude to ASK the user for the Python interpreter path (or to install Python) via SOAD-1 structured options (`AskUserQuestion` / `structured options` / `ask the user` verb present in the branch body); the brittle `Install Python 3.11+ and re-run` terminal is removed or accompanied by the structured ASK.
3. `tests/methodology/test_install_md_python_detection.py::test_install_md_step_2_conda_default_does_not_hardcode_python3_venv` PASSES — Step 2's `**Both system Python and conda available**` row references the detected interpreter, not `python3 -m venv`.
4. INSTALL.md Step 1 pre-flight detection chain preserved end-to-end — the `command -v python3 || command -v python` fallback chain remains intact in Step 1 (a regression-guard test pins this so the fix cannot inadvertently narrow detection to either python3-only or python-only).
5. No regression to slice-045's `test_install_md_correctness.py` prose-pin tests — INSTALL.md continues to satisfy the 4-pin contract (PyPI package name is `graphifyy`; no stale `v0.20.0` literal; tool-count claims match `plugin.yaml`; README + tutorial HTML name `graphifyy`). Slice-061's INSTALL.md edits touch different prose sites (Step 1 detection / Step 2 ASK gate / Step 3a venv create) but the same file, so the slice-045 pins must continue passing.

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0), each AC maps to one or more failing tests written BEFORE the implementation. The 3 ACs for the repro defect are already WRITTEN-FAILING (authored at `/repro` Step 3, verified 3/3 FAIL pre-fix). AC4's regression-guard test is PENDING — must be authored test-first BEFORE the INSTALL.md edit (otherwise the test could trivially be made to pass by the same edit it pins). AC5's full-suite pass is a pre-finish whole-suite check, not a row-level test.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | prose-pin | tests/methodology/test_install_md_python_detection.py | test_install_md_step_3a_does_not_hardcode_python3_venv | PASSING |
| 2 | prose-pin | tests/methodology/test_install_md_python_detection.py | test_install_md_step_2_no_python_branch_asks_user_for_interpreter | PASSING |
| 3 | prose-pin | tests/methodology/test_install_md_python_detection.py | test_install_md_step_2_conda_default_does_not_hardcode_python3_venv | PASSING |
| 4 | regression-guard | tests/methodology/test_install_md_python_detection.py | test_install_md_step_1_preserves_python3_or_python_detection_chain | PASSING |
| 5 | regression-guard | tests/methodology/test_install_md_correctness.py | test_install_md_graphify_pip_package_is_graphifyy | PASSING |

AC5's row cites one canonical assertion from slice-045's 4-pin file as the regression-guard anchor; the file's other 3 pin functions (`test_install_md_has_no_stale_v0_20_0_literal`, `test_install_md_tool_count_matches_plugin_yaml`, `test_readme_and_tutorial_name_graphifyy_package`) run alongside it in the methodology suite + via shippability row #45, so the broader 4-pin contract is enforced even though TF-1 only requires one row per AC (slice-045 reflection lesson at `_index.md` L130: "fold it into a tested AC, give it a real regression test ... or don't number it as a separate AC" — picked option 2: real regression test).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Step 3a uses detected interpreter | `$PY -m pytest tests/methodology/test_install_md_python_detection.py::test_install_md_step_3a_does_not_hardcode_python3_venv` → PASS |
| 2 | No-Python branch asks via SOAD-1 | `$PY -m pytest tests/methodology/test_install_md_python_detection.py::test_install_md_step_2_no_python_branch_asks_user_for_interpreter` → PASS |
| 3 | Conda-default uses detected interpreter | `$PY -m pytest tests/methodology/test_install_md_python_detection.py::test_install_md_step_2_conda_default_does_not_hardcode_python3_venv` → PASS |
| 4 | Step 1 detection chain preserved | `$PY -m pytest tests/methodology/test_install_md_python_detection.py::test_install_md_step_1_preserves_python3_or_python_detection_chain` → PASS (new test authored test-first) |
| 5 | No regression | `$PY -m tools.shippability_runner` → 61/61 PASS; `$PY -m pytest tests/methodology/test_install_md_correctness.py tests/methodology/test_install_audit.py tests/methodology/test_soad1_structured_options_ask_rule.py` → all PASS; `/build-slice` Phase F audits all clean |

## Must-not-defer

- [ ] Step 3a's idempotency preserved — `If $PY exists → skip` short-circuit stays; the interpreter-detection rewire only affects the create-path
- [ ] Error handling for user-supplied interpreter path — if Claude asks for the path and the user provides a bogus one (file doesn't exist / not an executable / not a Python interpreter / Python < `pyproject.toml`-derived floor), INSTALL.md prose MUST tell Claude how to validate via the **Bash tool** (Git-Bash on Windows; M4 fix — bash-shell-dialect-consistent with the rest of INSTALL.md's preflight) and re-ask once on failure (1-retry bound; abort on second failure)
- [ ] Step 1 pre-flight detection chain stays `command -v python3 || command -v python` **inside the `## Step 1:` section** — the fix propagates detection downstream, never narrows it (AC4 pins this, section-scoped via the new `_step_1_section` helper; M3 fix)
- [ ] **"I'll wait" branch bounded to exactly one attempt** (M1 fix) — on re-detection-still-failed, the No-Python ASK re-fires with the "I'll wait" option **REMOVED**; retry-form has only "Provide interpreter path" + "Abort install"
- [ ] **Python-version floor read dynamically from `pyproject.toml` `requires-python`** — NEVER hardcoded as a literal `3.10` / `3.11` / etc. in INSTALL.md (M5 + m3 fix; slice-058 / BC-PROJ-11 lesson at aggregated-lessons L68)
- [ ] **INSTALL.md L71 stale `Install Python 3.11+ and re-run` literal removed** in the same edit block as the new structured-options ASK gate (FBCD-1 sibling-drift; pyproject.toml floor is `>=3.10`, not `>=3.11`, so the existing prose already drifted)
- [ ] **Installer-suggestion prose drops minor-version literals** (`python@3.13` / `Python.Python.3.13`) — rewords to `winget install Python.Python.3` / `brew install python` (version-agnostic; m3 fix)
- [ ] EOL-DRIFT-1 / cross-machine portability — INSTALL.md is plain markdown, no shell-script-with-shebang concerns, but the prose must read identically on Windows / macOS / Linux Claude Code instances (no platform-specific instructions in the No-Python ASK branch; the path-validation prose is platform-agnostic when routed through the Bash tool)
- [ ] SOAD-1 conformance — the No-Python ASK uses structured options (`AskUserQuestion` verbiage referenced or implied), not a bare free-text prompt
- [ ] INSTALL.md remains idempotent end-to-end — re-running the install after a successful first install must still skip Step 3a cleanly

## Out of scope

- BRANCH-1 / clean-tree-precondition / `git worktree` discipline for `/build-slice` prerequisite check — surfaced during this slice's `/slice` invocation as a real methodology gap (uncommitted slice-A WIP could contaminate a fresh slice-B branch), but deserves its own design + Critic pass. **R-17 is appended directly to `architecture/risk-register.md` (open `mitigating`) in this slice's `/build-slice` Phase A** — NOT deferred to `/reflect`, per the canonical-filing-surface lesson (risk-register.md is the single source of truth for risks; slice-045/057 precedent at aggregated-lessons L131). The candidate fix (extend BRANCH-1 prerequisite check; offer `git worktree add` path on dirty tree) is nominated as a next-slice candidate but NOT implemented here.
- Other INSTALL.md Step 2 ambiguity rows (`Existing venv that doesn't have graphify`, `Existing ~/.claude/CLAUDE.md without the PY convention`, `Existing ~/.claude/settings.json with other keys but no CLAUDE_CODE_FORK_SUBAGENT`) — they already use the ASK-then-confirm pattern; not part of the python-detection defect class.
- `/triage` and `/adopt` opener-skill preflight checks — they call `INSTALL.md`'s install path but don't carry the `python3 -m venv` literal themselves; their preflight uses `$PY -m graphify --help` which assumes the venv already exists. Out of scope for this slice.
- methodology-changelog version bump — slice-045 precedent (`R-11 born-retired`, INSTALL.md prose-correctness class, MEPD-1(b) discharged by name vs META-1 `^## v…`-split assertion at `test_methodology_changelog.py:136`); INSTALL.md is the INST-1 install recipe = in-house methodology surface, but a defect-repair edit with no rule-mint / no audit-tool change / no ADR-decision-recording is a no-VERSION-bump class. **No new methodology-changelog entry, no VERSION bump, no plugin.yaml bump.**
- No new ADR — no new design decision is being recorded; this slice is pure defect repair to INSTALL.md prose. (Slice-045's INSTALL.md fix similarly had no ADR.)

## Dependencies

- Prior slices: [[slice-045-fix-install-pypi-package-name-and-stale-prose]] — established the `test_install_md_correctness.py` precedent for INSTALL.md prose-correctness pinning; this slice extends the same pattern to python-detection.
- Prior slices: [[slice-048-codify-structured-options-ask-rule]] — established SOAD-1 (`AskUserQuestion` / structured options for skill-ask gates); the No-Python branch's new ASK conforms to SOAD-1.
- Vault refs: [[INSTALL.md]] (the INST-1 install recipe), [[tools/install_audit.py]] (INST-1 audit), [[skills/triage/SKILL.md]] + [[skills/adopt/SKILL.md]] (opener preflight consumers).
- Risk register: [[risk-register#R-16]] (born in this slice — python-detection brittleness; retired in same slice per slice-045 R-11 precedent).
- Repro test (FAILING 3/3 pre-fix): `tests/methodology/test_install_md_python_detection.py` — authored at `/repro` Step 3, verified at Step 4. Shippability row #61 already cites this file.

## Mid-slice smoke gate

At ~50% of build (after the INSTALL.md edits land but before the AC4 regression-guard test is added):

```bash
$PY = "$HOME/.claude/.venv/Scripts/python.exe"
$PY -m pytest tests/methodology/test_install_md_python_detection.py -v --no-header
```

Expected: 3/3 PASS (the 3 WRITTEN-FAILING assertions now pass after the edit; AC4's PENDING row is not yet written).

If any of the 3 still FAIL: STOP, diagnose the INSTALL.md edit (wrong section anchor? regex still matches `python3 -m venv`?), do NOT continue. Do NOT rewrite the test to make it pass — that's the slice-040 stale-test antipattern.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (idempotency / bogus-path handling / detection chain / EOL / SOAD-1 conformance / re-run idempotency)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (3/3 + AC4 PASS = 4/4)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Full methodology suite pass (`$PY -m pytest tests/methodology/ tests/skills/ tests/agents/ --no-header -q`)
- [ ] `$PY -m tools.shippability_runner` → 61/61 PASS
- [ ] All Step-6 audits clean (BC-1 / RR-1 / CAD-1 / PMI-1 / DR-1 / TF-1 / WS-1 / WIRE-1 / ETC-1 / CSP-1 / SUP-1 / LINT-MOCK-1/2/3 / INST-1 / SOAD-1 / OSDG-1 / EOL-DRIFT-1 / STP-1 / BCR-1 / PCA-1 / BRANCH-1 / PVFS-1 / MCFS-1 / AVFS-1 / TVFS-1 / SCMD-1 / PTFCD-1 / SRSC-1 / RPCD-1 / SCPD-1 / EPGD-1 / RSAD-1 / MCT-1 / CCC-1 / TPHD-1 / FBCD-1 / META-1 / MEPD-1)
- [ ] Critic (mandatory per high tier + in-house methodology surface trigger) ACCEPTED-FIXED on all findings; meta-Critic DR-1 ACCEPT or EXTEND-all-VALIDATED; TRI-1 user-ratified CLEAN

## Next step

`/design-slice` — turn this mission brief into a just-enough spec (the design.md). Design must specify: (a) the exact INSTALL.md edits (Step 1 capture mechanism, Step 3a interpreter reference, Step 2 No-Python ASK structured-options form, Step 2 conda default), (b) AC4's regression-guard test design (which prose pattern pins the chain), (c) the bogus-path handling prose contract (validate-and-re-ask loop bounds).

## Pipeline position

- **predecessor**: `/repro` (auto-invoked by `/slice` Step 3c BFRD-1 confirm gate; one-attempt edge per ADR-048)
- **successor**: `/design-slice`
- **auto-advance**: true
- **on-clean-completion**: once the mission brief + milestone.md are written, invoke `/design-slice` via the Skill tool without waiting for the user (candidate was settled via the BFRD-1 confirm gate; no further user-input gate is pending).
- **user-input gates** (halt auto-advance):
  - Risk-tier picked (HIGH) — answered.
  - Worktree-scope decided (out of scope) — answered.
  - BFRD-1 confirm gate — discharged at the `/repro` invocation.

> Per PCA-1 (methodology-changelog.md v0.41.0).
