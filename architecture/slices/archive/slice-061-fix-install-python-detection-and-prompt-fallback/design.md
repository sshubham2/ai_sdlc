# Design: Slice 061 fix-install-python-detection-and-prompt-fallback

**Date**: 2026-05-23
**Mode**: Standard
**Risk tier**: high
**Critic-required**: true (in-house methodology surface + high tier)

## What's new

- **INSTALL.md Step 1 (pre-flight detection)** — the existing `command -v python3 || command -v python` fallback chain stays verbatim in the pre-flight bash block (AC4 regression-guard pins this, section-scoped). Detection is NOT captured into a shell variable for cross-step reuse — see "Detection-flow mechanism" decision below.
- **INSTALL.md Step 2 (`**No Python found**` branch)** — bare hard-fail "Install Python 3.11+ and re-run" replaced with a SOAD-1 structured-options ASK gate. **First fire (no prior failed install)** offers three choices: **(a) Provide interpreter path** (user pastes absolute path to a working Python they have installed off-PATH), **(b) Install Python now — I'll wait** (user installs via OS package manager, confirms via a single-option follow-up `AskUserQuestion` `"I've installed Python — re-detect"`; INSTALL.md then re-runs Step 1 detection), **(c) Abort install** (clean halt). **On retry (re-detection after picking 'I'll wait' still finds no Python)** the ASK gate is re-fired with TWO options only: **(a) Provide interpreter path** + **(c) Abort install** — the 'I'll wait' option is removed on retry to enforce SOAD-1 / BFRD-1 one-attempt-bound shape (M1 fix: 'I'll wait' is bounded to exactly one attempt; further failure must route through the explicit-path subflow or abort).
- **INSTALL.md Step 2 path-validation prose** — when the user picks "Provide interpreter path", INSTALL.md tells Claude to validate via existence + version probe, executed via the **Bash tool** (Git-Bash on Windows, system bash on macOS/Linux; the INSTALL.md preflight already uses Git-Bash idioms — `case "$(uname -s)" in MINGW*`). The validation is wrapped in a bash fence in INSTALL.md so Claude routes through the Bash tool, not PowerShell. **Python-version floor is read dynamically from `pyproject.toml`'s `requires-python`** — NEVER hardcoded as a literal `3.10` / `3.11` / etc. (slice-058 / BC-PROJ-11 lesson at aggregated-lessons line 68). Validation bash block shape:
  ```bash
  MIN_PY=$(grep -E '^requires-python' "$AI_SDLC_DIR/pyproject.toml" | sed -E 's/.*"[><=!]*([0-9]+\.[0-9]+).*/\1/')
  test -x "$user_path" && "$user_path" -c "import sys; req=tuple(int(x) for x in '$MIN_PY'.split('.')); sys.exit(0 if sys.version_info[:2] >= req else 1)"
  ```
  On failure → re-ask once (bounded to 1 retry per SOAD-1 / BFRD-1 confirm-once discipline; ADR-048 one-attempt-bound shape). On second failure → abort with diagnostic naming the path tried + the failing check + the resolved `$MIN_PY` floor.
- **INSTALL.md Step 2 `**Both system Python and conda available**` row** — `python3 -m venv` literal replaced with the inline `$(command -v python3 || command -v python) -m venv` form so the prose default tracks the Step 3a execution. No `$BOOT_PYTHON` variable is referenced (the variable cannot survive across separate bash invocations — INSTALL.md prose Claude reads step-by-step routes each step through a distinct Bash tool call; B1 fix).
- **INSTALL.md Step 3a** — `python3 -m venv ~/.claude/.venv` literal replaced with `$(command -v python3 || command -v python) -m venv ~/.claude/.venv` (inline-recompute pattern; B1 fix). The `If $PY exists → skip` short-circuit and the conda-equivalent branch stay verbatim. **Detection runs once per execution site** — design accepts the trivial cost of two `command -v` calls (Step 1's pre-flight echo + Step 3a's inline recompute) to avoid the cross-bash-invocation persistence problem entirely.
- **INSTALL.md L71 sibling-literal drop** — the existing prose `Install Python 3.11+ and re-run` already disagrees with `pyproject.toml`'s `>=3.10` floor (FBCD-1 sibling-drift). This slice removes the `3.11+` literal from L71 in the same edit block as the new structured-options ASK so the harmonized N-surface fix doesn't leave a stale sibling (slice-058 lesson on harmonized-but-missed-sibling pattern).
- **INSTALL.md Step 2 "I'll wait" installer suggestions** — drop hardcoded minor-version literals `python@3.13` / `Python.Python.3.13`; reword to "Python 3.10 or newer" + version-agnostic installer commands (`winget install Python.Python.3` / `brew install python` / distro `apt install python3 python3-venv` / `dnf install python3`). m3 fix.
- **AC4 regression-guard test** — new `test_install_md_step_1_preserves_python3_or_python_detection_chain` appended to `tests/methodology/test_install_md_python_detection.py` (authored test-first per TF-1 before the INSTALL.md edits). Asserts the literal substring `command -v python3 || command -v python` is present **inside the `## Step 1:` section** (section-scoped via a new `_step_1_section` helper matching `## Step 1:.*?(?=## Step 2:)`, mirroring the existing `_step_3a_section` / `_step_2_section` pattern at the file's L58–L81). **M3 fix**: a bare `assert "command -v python3 || command -v python" in install_md_text` would silently false-green if a future edit moved the chain out of Step 1 and into a misleading comment elsewhere; the section-scoped assertion pins the chain to its actual contract surface (FBCD-1 / canonical-phrase-placement discipline applied to AC4).
- **risk-register.md R-16 entry** — mint born-retired R-16 "INSTALL.md install-recipe python-detection brittleness" (slice-045 R-11 born-retired precedent; user-reported defect class; immediately retired by this slice's INSTALL.md edit). **R-16 carries a `**Notes**:` paragraph** explicitly naming the graceful-fallback ASK gate as covering the broader class ("Python installed but `command -v` doesn't find it" — conda-only environments, NixOS shell-PATH injection, Termux, Docker images with non-standard interpreter paths). A second-platform report that falls outside BOTH the detection chain AND the ASK gate's recovery is a NEW entry, not a re-open of R-16. (M7 fix; slice-057/R-15 Notes-paragraph pattern for born-retired classes with adjacent open exposures.)
- **risk-register.md R-17 entry** — mint open `mitigating` R-17 "BRANCH-1 prerequisite check does not verify a clean working tree before `/build-slice` creates the `slice/NNN-` branch" with candidate-fix prose naming the BRANCH-1 extension scope (require clean tree OR offer `git worktree add` path at `## Prerequisite check ### Branch state` sub-section). **R-17 is appended directly to `architecture/risk-register.md` in THIS slice's `/build-slice` Phase A** (NOT deferred to `/reflect`), per slice-045/slice-057 canonical-filing-surface precedent (aggregated-lessons L131: "record any … on the canonical `risk-register.md` `**Retired**:` surface — NEVER reflection.md" — generalizes to ALL risk-register surfaces, retired or open). M6 fix.

## What's reused

- `tests/methodology/test_install_md_python_detection.py` — created at `/repro` Step 3; 3 assertions WRITTEN-FAILING verified 2026-05-23.
- `tests/methodology/test_install_md_correctness.py` — slice-045 regression-guard for INSTALL.md prose-correctness (PyPI name `graphifyy`, no stale `v0.20.0` literal, tool-count matches plugin.yaml, README + tutorial HTML name `graphifyy`). MUST continue to pass — the python-detection fix touches different prose sites and must not regress slice-045's assertions.
- `tests/methodology/test_soad1_structured_options_ask_rule.py` — SOAD-1 prose-pin tests on opener template blocks + root CLAUDE.md. The new INSTALL.md ASK gate is SOAD-1 conformant in spirit but is NOT under SOAD-1's tested-surface set (SOAD-1's structural assertions target opener-skill template blocks + root CLAUDE.md `## Ask discipline`, not INSTALL.md prose). No new SOAD-1 surface assertion in this slice — INSTALL.md SOAD-1 conformance is checked via the AC2 prose-pin (`test_install_md_step_2_no_python_branch_asks_user_for_interpreter`).
- `tests/methodology/test_install_audit.py` — INST-1 canonical inventory tests (skills/agents/tools/templates byte-equal to plugin.yaml). Unaffected by this slice (no new module added; INSTALL.md prose edits don't touch the canonical inventory).
- [[CLAUDE.md#Ask discipline]] — SOAD-1 canonical sentence ("Ask discipline: when a skill needs user input, present it as structured options (with a recommended choice) via the `AskUserQuestion` tool — never a bare free-text prompt"). The INSTALL.md No-Python ASK gate IS the canonical pattern this section requires.
- [[risk-register#R-11]] — slice-045 born-retired precedent ("INSTALL.md install-recipe factual drift"). R-16 follows the same shape: defect repair → mint + retire in same slice → no separate retirement slice needed.

## Components touched

### INSTALL.md (the INST-1 install recipe)

- **Responsibility**: prose contract Claude reads literally during AI SDLC installs. Steps are sequential bash + ASK + edit operations that Claude executes on the user's behalf.
- **Lives at**: `INSTALL.md` (root) — modified by this slice.
- **Key interactions**:
  - Read by Claude during install (when user says "install this").
  - Audited by `tests/methodology/test_install_md_correctness.py` (slice-045 prose-pins) and now `tests/methodology/test_install_md_python_detection.py` (this slice's prose-pins).
  - Referenced by `tools/install_audit.py` indirectly (the audit checks `~/.claude/` post-install state; INSTALL.md is the install recipe).
  - Referenced by `skills/triage/SKILL.md` + `skills/adopt/SKILL.md` preflight ("If anything regresses, fail fast and point back at this install").

### tests/methodology/test_install_md_python_detection.py

- **Responsibility**: prose-pin tests for INSTALL.md python-detection correctness. Pre-staged by `/repro` (3 assertions); this slice appends one AC4 regression-guard assertion (`test_install_md_step_1_preserves_python3_or_python_detection_chain`).
- **Lives at**: `tests/methodology/test_install_md_python_detection.py` — created by `/repro`, extended by this slice.
- **Key interactions**:
  - Consumed by `architecture/shippability.md` row #61 (already wired pre-build).
  - Consumed by the methodology test suite at `/build-slice` Phase F + `/validate-slice`.

### architecture/risk-register.md

- **Responsibility**: project risk catalog, audited by RR-1 / `tools/risk_register_audit.py`. R-16 entry appended in this slice (born-retired).
- **Lives at**: `architecture/risk-register.md` — appended (one new section).
- **Key interactions**: RR-1 audit at `/build-slice` Phase 6 + `/validate-slice`.

## Contracts added or changed

No new endpoints, events, schemas, or data model deltas. INSTALL.md IS the contract; this slice modifies the prose contract Claude reads.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). This slice's only new module is the regression-guard test function (AC4) inside an existing `/repro`-authored file; no new source-graph module is introduced.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_install_md_python_detection.py` (file created by `/repro`; AC4 function `test_install_md_step_1_preserves_python3_or_python_detection_chain` appended this slice) | `architecture/shippability.md` row #61 | self | `rationale: test module — pytest is the consumer` |

## Decisions made (ADRs)

**None.** This slice is pure defect repair to INSTALL.md prose. The user-input ASK design choices — the 3-option ASK form, the existence + version probe, the 1-retry bound on path validation, the 1-attempt bound on the "I'll wait" branch (option-removed-on-retry mechanism) — are **bounded parametric refinements within SOAD-1** (option-list shape — `AskUserQuestion` structured options for skill-asks) **+ BFRD-1 / ADR-048** (one-attempt-bound shape — applied analogously to the ambiguity-resolution gate, generalizing from the confirm-gate origin). No new architectural commitment is recorded. m2 fix.

**MEPD-1(b) discharge-by-name verified against META-1 enforcing assertion** (not by precedent analogy alone — slice-040 / slice-045 / slice-053 lineage): the META-1 enforcing assertion at `tests/methodology/test_methodology_changelog.py:136` reads `sections = re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", changelog, flags=re.MULTILINE)` followed by per-section `Rule reference` substring check. Slice-061 adds **zero new `## v…` sections** to `methodology-changelog.md`, so the assertion is **vacuously satisfied** — no new section that could fail the per-section `Rule reference` check, so no new entry is required. Slice-045 (`R-11` born-retired; INSTALL.md prose-correctness fix) is the precedent that corroborates this discharge but is NOT the discharge mechanism. M8 fix.

## Authorization model for this slice

N/A. INSTALL.md is a prose install recipe; no auth surface is touched. The new "user pastes interpreter path" interaction surface DOES introduce a path-validation prose contract (must exist + must be a Python ≥ 3.10 interpreter), but that's input validation, not authorization.

## Error model for this slice

Three new error paths introduced by the No-Python ASK:

1. **User picks "Provide interpreter path" + provides invalid path** (file doesn't exist, isn't executable, isn't a Python interpreter, or is Python < the `pyproject.toml`-derived floor):
   - INSTALL.md prose directs Claude to **run the validation via the Bash tool** (Git-Bash on Windows; the INSTALL.md preflight L47–L51 already uses `case "$(uname -s)" in MINGW*` Git-Bash idioms, so the validation is internally consistent with the rest of the recipe). The validation prose is wrapped in a `\`\`\`bash` fence in INSTALL.md so Claude routes through the Bash tool, NOT PowerShell — M4 fix: under PowerShell, `test -x` does not exist as a built-in and the bash-style variable expansion `"$user_path"` is differently quoted; routing through the Bash tool keeps the validation shell-dialect-consistent.
   - **`$user_path` and `$AI_SDLC_DIR` binding mechanism** (m-add-1 fix per meta-Critic dual review): `$user_path` is bound by Claude **substituting the user's structured-options response into the bash command before invocation** — same prose-templating pattern as the existing `$AI_SDLC_DIR` references at INSTALL.md L137–L141 / L153 (`cp -r "$AI_SDLC_DIR/skills/"* …` works across separate Bash tool invocations because Claude tracks `AI_SDLC_DIR` as conversational state from Step 0 and substitutes the resolved path at each invocation site). Neither `$user_path` nor `$AI_SDLC_DIR` is a cross-bash-invocation shell-variable channel — that's the B1-class concern, deliberately avoided by both the inline-recompute pattern (for the Step 3a interpreter) and the Claude-templating pattern (for `$user_path` and `$AI_SDLC_DIR`).
   - On failure: print a diagnostic naming the path tried + the failing check (existence vs version) + the resolved `$MIN_PY` floor; then re-ask via the same structured-options ASK gate (bounded to **one retry** per SOAD-1 confirm-once discipline — `[[ADR-048]]` BFRD-1 one-attempt-bound shape).
   - On second invalid path: print diagnostic + abort install with non-zero exit status (semantically; INSTALL.md doesn't `exit 1` itself but tells Claude to stop and surface the failure to the user).

2. **User picks "Install Python now — I'll wait"**:
   - INSTALL.md prose suggests version-agnostic installer commands (Windows: `winget install Python.Python.3` or [python.org installer](https://python.org/downloads/); macOS: `brew install python` or [python.org installer](https://python.org/downloads/); Linux: distro package manager — `apt install python3 python3-venv`, `dnf install python3`, etc.). Floor requirement stated as "Python 3.10 or newer" (sourced from `pyproject.toml` `requires-python` — never a hardcoded minor-version literal; m3 + M5 fix).
   - Claude then asks a single-option follow-up `AskUserQuestion` ("I've installed Python — re-detect"); on confirm, re-runs the Step 1 detection bash block.
   - **If re-detection still finds no Python** (the user's install didn't put it on PATH, or they hit a different platform-conditional issue): re-fire the No-Python ASK gate **with the 'I'll wait' option REMOVED** — the retry-form offers only **(a) Provide interpreter path** + **(c) Abort install**. This **bounds 'I'll wait' to exactly one attempt** (SOAD-1 / BFRD-1 / ADR-048 one-attempt shape applied to the ambiguity-resolution gate). M1 fix: the original "bounded to one retry" claim was asserted but unenforced — the retry-form's reduced option list IS the enforcement mechanism.
   - The "Provide interpreter path" subflow (recovery 1 above) still has its own bounded retry (1 retry on invalid path → abort), independent of the 'I'll wait' bound — these compose: user can install + retry 'Provide path' once + abort. Maximum interactive turns at the No-Python gate: 4 (ASK → install-wait → ASK-retry → path-retry → terminus).

3. **User picks "Abort install"**:
   - INSTALL.md prose directs Claude to print a clean halt message ("Install aborted — re-run INSTALL.md once Python is available") and stop.
   - **No NEW partial-install artifact** is left behind by an abort at Step 2 — Steps 3a–3h have not yet run in the current invocation. **Pre-existing `~/.claude/` state from prior install attempts (if any) is unchanged** — the abort path must NOT clean up pre-existing state (would be destructive; slice-051 git-restore-class precedent for "do not undo state the slice did not create"). M2 fix: the original wording "No partial-install artifact is left behind because Step 3a is the FIRST step that mutates `~/.claude/`" was qualified-true for THIS invocation but misleadingly implied a stronger guarantee than it has on re-runs (INSTALL.md L227 "Recovery — if the user re-runs this" explicitly contemplates partial-config carry-over).

These three paths together replace the single brittle "Install Python 3.11+ and re-run" terminus.

## Validation strategy

5 ACs map to 4 test functions + 1 whole-suite pre-finish check:

- **AC1 / AC2 / AC3**: existing `/repro`-authored WRITTEN-FAILING tests flip to PASS on the INSTALL.md edits.
- **AC4**: new regression-guard test `test_install_md_step_1_preserves_python3_or_python_detection_chain` authored test-first BEFORE the INSTALL.md edits (so the test cannot be tautologically passed by the same edit it pins). Asserts: `assert "command -v python3 || command -v python" in install_md_text` (literal substring presence in Step 1 pre-flight).
- **AC5**: `tools.shippability_runner` 61/61 PASS + full methodology suite green + all Step-6 audits clean (no regression to slice-045, no INST-1 / SOAD-1 / PMI-1 / CAD-1 / OSDG-1 / EOL-DRIFT-1 drift).

Mid-slice smoke gate runs the 4 row-level tests after the INSTALL.md edits land + AC4 test is authored: expected 4/4 PASS.

## Risk register additions

Both R-16 and R-17 are appended to `architecture/risk-register.md` **in this slice's `/build-slice` Phase A** (NOT deferred to `/reflect`). The canonical filing surface for risks is `risk-register.md` per aggregated-lessons L131 (slice-045/057 precedent: "record any … on the canonical `risk-register.md` `**Retired**:` surface — NEVER reflection.md" — generalizes to all risk-register surfaces, retired or open). M6 fix.

**R-16 (new — born-retired in this slice)**: INSTALL.md install-recipe python-detection brittleness (Step 3a hardcoded `python3` even though Step 1 detected `python3 || python`; Step 2 No-Python branch hard-failed instead of asking). Follows slice-045 R-11 born-retired shape.

`**Notes**:` paragraph (M7 fix) — The graceful-fallback ASK gate covers the **broader class** of "Python installed but `command -v` doesn't find it" (conda-only environments where `python` exists in env but unactivated `command -v python` returns nothing; NixOS shell-PATH-injection where python is in a per-shell PATH only; Termux on Android where `command -v` semantics differ; Docker images where the python binary is at `/usr/bin/python3.11` only and neither `python3` nor `python` is on PATH). A second-platform report falling outside BOTH the detection chain AND the ASK gate's recovery is a NEW R-NN entry, not a re-open of R-16. Pattern: slice-057/R-15 Notes-paragraph shape for born-retired classes with adjacent open exposures.

**R-17 (new — open `mitigating`)**: BRANCH-1's `## Prerequisite check ### Branch state` sub-section in `/build-slice` does not verify a clean working tree before creating the `slice/NNN-` branch. Uncommitted slice-A WIP could be carried into a fresh slice-B branch on creation, silently contaminating slice-B's commit history with slice-A's incomplete diff. Witnessed during slice-061's own `/slice` invocation as an adjacent class (a stale-snapshot-induced false conflict; BRANCH-1 itself was not violated, but the gap was surfaced; see `[[verify-git-status-before-declaring-conflict]]` memory). **Mitigating because** `/build-slice` does run an existing branch-state preflight that catches some cases (`tools/branch_workflow_audit.py`); the gap is the un-pinned cleanliness invariant. **Candidate fix**: extend BRANCH-1 (or mint a sibling rule) so `/build-slice` Prerequisite check requires a clean tree before branch-create, OR offers a `git worktree add` path when the tree is dirty. NOT a slice-061 deliverable (out of scope per `/slice` decision); strong next-slice candidate (slice-062 nomination on the standing pipeline-hygiene track).

## Out of scope (restated from mission brief)

- BRANCH-1 / clean-tree-precondition / `git worktree` discipline (filed as R-17 above).
- Other INSTALL.md Step 2 ambiguity rows (already ASK-then-confirm conformant).
- `/triage` and `/adopt` opener-skill preflight (no `python3` literal in their preflight code).
- methodology-changelog version bump (no-VERSION-bump conformance class; slice-045 precedent).
- New ADR.
- **`/code-review` prose-contract review of INSTALL.md** — INSTALL.md is the slice's primary artifact-of-change but is **OUT-OF-SCOPE for `/code-review` v1** (M-add-1 Option (b) user-ratified at TRI-1, 2026-05-23). The `/code-review` skill is walking-skeleton v1 advisory-only per slice-060 / CRSI-1 / ADR-059 (`v1 advisory only — findings written to architecture/slices/slice-NNN-/code-review.md but DO NOT block /validate-slice`); its in-scope paths at `skills/code-review/SKILL.md:48-55` enumerate `skills/**/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `tests/**/*.py`, and root-level `plugin.yaml | pyproject.toml | VERSION | methodology-changelog.md` — INSTALL.md is deliberately not on this list for slice-061. **Structural review surfaces relied on instead**: (1) AC1–AC3 prose-pin tests at `tests/methodology/test_install_md_python_detection.py` (this slice's repro), (2) AC4 regression-guard test (section-scoped detection chain pin), (3) slice-045's `tests/methodology/test_install_md_correctness.py` (PyPI name + version-literal + tool-count + README/tutorial pins), (4) slice-058's `tests/methodology/test_install_md_wakeup_guardrail.py` (Step 3h structural pin), (5) INST-1 audit at `tools/install_audit.py` (canonical inventory cross-check). Together these 5 surfaces provide deterministic structural coverage of INSTALL.md without /code-review v1's adversarial review. **slice-062 nomination**: if a future slice substantively expands INSTALL.md (new step, new ambiguity row, new install path), nominate a /code-review in-scope-list extension at that slice's design-time. The standing nomination is recorded but NOT a slice-061 deliverable.

## Pipeline position

- **predecessor**: `/slice`
- **successor**: `/critique`
- **auto-advance**: true
- **on-clean-completion**: design.md written + no new ADRs + no real ambiguity remaining → invoke `/critique` via the Skill tool without waiting for the user.
- **user-input gates**: clarifying questions answered (3/3 recommended options); no further design ambiguity.

> Per PCA-1 (methodology-changelog.md v0.41.0).
