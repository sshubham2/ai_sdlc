# Critique: Slice 061 fix-install-python-detection-and-prompt-fallback

**Critic reviewed**: mission-brief.md, design.md (no new ADRs in this slice — defect-repair class per slice-045 precedent)
**Date**: 2026-05-23
**Result**: NEEDS-FIXES (Builder dispositions applied; awaits TRI-1 ratification)

## Summary

Design is sound at the AC level (the 3 WRITTEN-FAILING repro tests + 1 PENDING regression-guard test correctly pin the defect class) and the no-VERSION-bump posture is right. But the **`$BOOT_PYTHON` capture mechanism was broken-by-construction** — Step 1's bash block runs in a different invocation than Step 3a, so the variable cannot survive without explicit persistence; the No-Python ASK had **two unbounded recovery loops the design hand-waved** (the "I'll wait" branch and the "abort-leaves-no-partial-state" claim contradicting Steps 3d/3h having already run); AC4's regression-guard was **not section-scoped** so a future relocation would silently false-green it; and the `>= 3.10` version literal was **hardcoded against `pyproject.toml`** instead of derived dynamically (the exact slice-058 / BC-PROJ-11 lesson). One Blocker (BOOT_PYTHON scope) + 8 Majors + 3 Minors = 12 findings; ALL ACCEPTED-FIXED in design.md + mission-brief.md.

## Findings

### Blockers (must address before /build-slice)

#### B1: `$BOOT_PYTHON` variable cannot survive from Step 1 to Step 3a — separate bash invocations

- **Claim under review**: design.md "pre-flight bash block captures the detected interpreter into a shell variable `BOOT_PYTHON` so downstream steps reference a single source of truth" + `$BOOT_PYTHON -m venv ~/.claude/.venv`.
- **Issue**: INSTALL.md is prose Claude reads step-by-step and executes via separate bash tool invocations (Step 1 is bash fence at INSTALL.md L46–L65; Step 3a's command is unfenced prose at L87 — they are not the same shell process). Claude executes each fenced bash block as an independent `bash -c` invocation. There is no shell process that persists across Step 1 → Step 3a, so a bare `$BOOT_PYTHON -m venv ~/.claude/.venv` in Step 3a expands to literally `-m venv ~/.claude/.venv` (empty variable). The design names neither (a) an explicit persistence channel, nor (b) a "recompute inline" fallback.
- **Evidence**: INSTALL.md bash-fence locations at L46, L115, L135, L152, L164, L196, L252. Step 3a's command at L87 is plain prose, NOT inside a bash fence. Per Wiegers, every claim must trace to a mechanism; "BOOT_PYTHON captures" had no execution mechanism described.
- **Proposed fix**: Switch to **Pattern A — inline recompute**: Step 3a prose becomes `$(command -v python3 || command -v python) -m venv ~/.claude/.venv`. Same pattern for Step 2's conda-default row. Detection runs twice (Step 1 echo + Step 3a inline) — trivial cost, eliminates the cross-bash-invocation persistence problem entirely.
- **Builder draft**: ACCEPTED-FIXED at design.md "What's new" → Step 3a entry and Step 2 conda-default entry; new `## What's new` text explicitly states "Detection is NOT captured into a shell variable for cross-step reuse" + names the inline-recompute pattern as the canonical mechanism. All `$BOOT_PYTHON` references removed from design.md.

### Majors (address this slice)

#### M1: "Install Python — I'll wait" branch is an unbounded recovery loop the design doesn't terminate

- **Claim under review**: design.md "Claude waits for user confirmation … then re-runs the Step 1 detection bash block. If re-detection still finds no Python: re-fire the original No-Python ASK gate (bounded to **one retry** of the whole post-install detection — user might have installed Python that's not on PATH; falls into the 'Provide interpreter path' subflow on retry)."
- **Issue**: The "bounded to one retry" claim was asserted but the mechanism did not enforce it — the second No-Python ASK had the same three options including "I'll wait" again, so a user could choose "I'll wait" repeatedly. "Claude waits" is also not a defined operation — Claude can't actually block; it can only re-ASK at each turn.
- **Evidence**: design.md (pre-fix) Error model item 2 — the retry-form was identical to the first-fire form. SOAD-1 / BFRD-1 one-attempt-bound shape invoked by name but not implemented.
- **Proposed fix**: On re-detection-still-failed, the No-Python ASK re-fires with the **"I'll wait" option REMOVED** — retry-form has only "Provide interpreter path" + "Abort install". The reduced option list IS the enforcement mechanism (M1 fix; pinned in design.md "What's new" Step 2 entry + Error model recovery path 2).
- **Builder draft**: ACCEPTED-FIXED at design.md Error model recovery path 2; mission-brief must-not-defer adds "'I'll wait' branch bounded to exactly one attempt".

#### M2: "Abort path leaves no partial state" is contradicted by Steps 3d / 3h ordering

- **Claim under review**: design.md "No partial-install artifact is left behind because Step 3a is the FIRST step that mutates `~/.claude/` (Steps 0/1/2 are read-only / ASK-only)."
- **Issue**: Qualified-true for ordering relative to 3a, but misleadingly worded re-runs (INSTALL.md L227 "Recovery — if the user re-runs this" explicitly contemplates a re-run on a partially-configured machine — under which the design's "Steps 0/1/2 are read-only" claim is misleading because the existing partial state from a prior run already exists).
- **Evidence**: INSTALL.md L102 (Step 3d global CLAUDE.md append), L125 (Step 3e settings.json), L170 (Step 3h CLAUDE.md append) — all post-3a mutations.
- **Proposed fix**: Reword to "No NEW partial-install artifact is left behind by an abort at Step 2 — Steps 3a–3h have not yet run in the current invocation. Pre-existing `~/.claude/` state from prior install attempts (if any) is unchanged" + add "abort path must NOT clean up pre-existing state".
- **Builder draft**: ACCEPTED-FIXED at design.md Error model recovery path 3.

#### M3: AC4 regression-guard is not section-scoped — vulnerable to literal-elsewhere false-green (slice-058 lesson)

- **Claim under review**: design.md "Asserts: `assert "command -v python3 || command -v python" in install_md_text` (literal substring presence in Step 1 pre-flight)."
- **Issue**: Exact slice-058 FBCD-1 / canonical-phrase-placement failure. A future edit could remove the chain from Step 1 and insert it into a misleading comment elsewhere and AC4 would silently pass. The pre-staged test file already demonstrates the section-scoping helper pattern; AC4 should reuse it with a `_step_1_section` helper.
- **Evidence**: `tests/methodology/test_install_md_python_detection.py:58–81` already has `_step_3a_section` and `_step_2_section` helpers — same pattern trivially available for Step 1.
- **Proposed fix**: AC4 test asserts `assert "command -v python3 || command -v python" in _step_1_section(_install_text())` where `_step_1_section` matches `## Step 1:.*?(?=## Step 2:)`.
- **Builder draft**: ACCEPTED-FIXED at design.md "What's new" AC4 entry; mission-brief must-not-defer adds "inside the `## Step 1:` section" qualifier.

#### M4: Path-validation prose under-specifies shell dialect — PowerShell routing risk

- **Claim under review**: design.md "validate via existence + version probe: `test -x "$user_path"` AND `"$user_path" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"`".
- **Issue**: `test -x` works under Git-Bash for `.exe` files (empirically verified — APED-1) but is not a PowerShell built-in. INSTALL.md's existing bash blocks all assume Git-Bash on Windows (Step 1 uses `case "$(uname -s)" in MINGW*` detection), so internally consistent IF Claude routes the validation through the Bash tool. **Risk**: the path-validation prose was described in design.md but not wrapped in a bash fence in INSTALL.md spec — Claude reading prose might attempt the validation via PowerShell tool on Windows.
- **Evidence**: APED-1 executed verification on the running machine confirms `test -x` works under Git-Bash; the user's CLAUDE.md instructs PowerShell as the Windows shell preference, creating routing ambiguity. INSTALL.md L47–L51 `case "$(uname -s)" in MINGW*` proves the Git-Bash idiom.
- **Proposed fix**: design.md path-validation prose specifies the bash fence wrap in INSTALL.md + adds explicit "Run via the Bash tool" instruction so Claude doesn't accidentally route through PowerShell.
- **Builder draft**: ACCEPTED-FIXED at design.md "What's new" path-validation entry + Error model recovery path 1.

#### M5: `>= 3.10` is hardcoded against `pyproject.toml` — slice-058 / BC-PROJ-11 lesson re-applies

- **Claim under review**: design.md "`sys.exit(0 if sys.version_info >= (3, 10) else 1)` (matches `pyproject.toml` `requires-python = ">=3.10"`)".
- **Issue**: Exact slice-058 lesson at aggregated-lessons L68: "Recipe / methodology docs must reference VERSION dynamically — never hard-code a methodology version literal … Promoted to BC-PROJ-11." The Python-version-floor `3.10` is the same drift class. `pyproject.toml:24` is the authoritative source; hardcoding `3.10` in INSTALL.md will re-drift the next time pyproject's floor bumps. INSTALL.md L71's existing `Install Python 3.11+ and re-run` already drifted from pyproject.toml's `>=3.10`.
- **Evidence**: `pyproject.toml:24` `requires-python = ">=3.10"`. INSTALL.md L71 `Install Python 3.11+ and re-run` — drifted. Aggregated lessons L68 / BC-PROJ-11.
- **Proposed fix**: Validation bash block reads pyproject dynamically: `MIN_PY=$(grep -E '^requires-python' "$AI_SDLC_DIR/pyproject.toml" | sed -E 's/.*"[><=!]*([0-9]+\.[0-9]+).*/\1/')` then probes against `$MIN_PY`. Also remove the stale `3.11+` from L71 (sibling-drift FBCD-1) in the same edit block.
- **Builder draft**: ACCEPTED-FIXED at design.md "What's new" path-validation entry (Option A: dynamic pyproject grep) + new "INSTALL.md L71 sibling-literal drop" entry; mission-brief must-not-defer adds "Python-version floor read dynamically from `pyproject.toml`" + "INSTALL.md L71 stale `3.11+` literal removed".

#### M6: R-17 (BRANCH-1 clean-tree precondition) deferral lacks a concrete filing point

- **Claim under review**: design.md "R-17 (new — open; deferred / discovered): … Out of scope for slice-061 per `/slice` decision; filed here so `/reflect` carries it forward." + mission-brief "Filed as a Discovered item in slice-061's reflection.md; risk-register entry (likely R-17) authored at `/reflect`."
- **Issue**: The canonical filing surface for a discovered risk is `risk-register.md`, not reflection.md (aggregated-lessons L131: slice-045 lesson generalizes). design.md "Risk register additions" lists R-17 as additional (implies it WILL be in risk-register.md after this slice); but design.md L109 says "/reflect carries it forward" — internal contradiction.
- **Evidence**: Aggregated lessons L131 (slice-045 lesson, explicit). risk-register.md schema: `/reflect` appends new entries on Discovery (but the canonical surface is risk-register.md, not reflection.md).
- **Proposed fix**: Option A: R-17 appended to risk-register.md at `/build-slice` Phase A in this slice. Mission-brief reworded to drop the "reflection.md" phrasing.
- **Builder draft**: ACCEPTED-FIXED at design.md "Risk register additions" header + R-17 body + mission-brief Out of scope (Option A picked — R-17 lands in risk-register.md in this slice, not deferred).

#### M7: R-16 same-slice mint+retire — is "python-detection brittleness" a class that could recur?

- **Claim under review**: mission-brief "R-16 (to be born-retired in this slice)" + design.md.
- **Issue**: Slice-045's R-11 class was a closed class of factual literals; R-16's class is more open — more platforms exist than the 3 named (Windows / macOS / Linux): WSL, Termux, conda-only, NixOS, Docker images with non-standard paths. The fix solves the witnessed cases but the class is broader.
- **Evidence**: The fix's effective coverage extends to the ASK-gate graceful-fallback for off-PATH Python, but the risk-register entry's prose should acknowledge the broader class.
- **Proposed fix**: Keep R-16 born-retired BUT add a `**Notes**:` paragraph explicitly stating the graceful-fallback ASK gate covers the broader class; second-platform reports falling outside both the detection chain AND the ASK gate's recovery are NEW R-NN entries, not re-opens. Slice-057/R-15 Notes-paragraph pattern.
- **Builder draft**: ACCEPTED-FIXED at design.md "Risk register additions" R-16 entry — Notes paragraph appended verbatim per Critic spec.

#### M8: MEPD-1(b) discharge cited by name, but not verified against the META-1 assertion's actual semantics in design.md

- **Claim under review**: mission-brief "MEPD-1(b) discharged by name vs META-1 `^## v…`-split assertion at `test_methodology_changelog.py:136`".
- **Issue**: Mission-brief names the assertion line correctly. design.md "Decisions made (ADRs)" only cited "slice-045 (similar INSTALL.md-prose-correctness fix) also had no ADR" — that's precedent-analogy, not assertion-grep (slice-040/045/053 lessons).
- **Evidence**: `tests/methodology/test_methodology_changelog.py:136` is `re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", changelog, flags=re.MULTILINE)` followed by per-section `Rule reference` substring assertion. Slice adds zero new `## v…` sections, so vacuously satisfied — correct discharge.
- **Proposed fix**: Add one sentence to design.md "Decisions made (ADRs)" with the explicit vacuous-satisfaction phrasing (same shape as risk-register.md L257).
- **Builder draft**: ACCEPTED-FIXED at design.md "Decisions made (ADRs)" section — explicit META-1 vacuous-satisfaction paragraph added.

### Minors (log; address if cheap)

#### m1: WIRE-1 exemption rationale is honor-system but audit-format-compliant

- **Claim under review**: design.md WIRE-1 row's verbose rationale.
- **Issue**: `tools/wiring_matrix_audit.py:63` `_RATIONALE_MARKER = "rationale:"` accepts any cell with `rationale:` substring — does NOT validate content. The verbose rationale was precedent-analogy, not audit-enforcing.
- **Evidence**: `wiring_matrix_audit.py:275–284` parses for the substring only.
- **Proposed fix**: Shorten to canonical slice-051 form `rationale: test module — pytest is the consumer`.
- **Builder draft**: ACCEPTED-FIXED at design.md wiring matrix row.

#### m2: "No new ADR" justification could cite ADR-criteria mechanically

- **Claim under review**: design.md "Decisions made (ADRs)" justification.
- **Issue**: Mild over-claim. The 3-option ASK form + 1-retry bound are slice-level choices bounded by SOAD-1 + BFRD-1, not new architectural commitments — but the prose argument was thinner than it could be.
- **Evidence**: SOAD-1 is generic for option-list shape; BFRD-1 documents one-attempt-bound shape for confirm-gates (applied here analogously to ambiguity-resolution gate).
- **Proposed fix**: Strengthen design.md to: "bounded parametric refinements within SOAD-1 (option-list shape) + BFRD-1 (one-attempt-bound shape); no new architectural commitment is recorded".
- **Builder draft**: ACCEPTED-FIXED at design.md "Decisions made (ADRs)" — strengthened wording applied alongside M8.

#### m3: "I'll wait" branch installer suggestions hardcode platform-specific minor-version literals

- **Claim under review**: design.md "Windows: `winget install Python.Python.3.13` or python.org installer; macOS: `brew install python@3.13`".
- **Issue**: Same drift class as M5 — hardcoded `3.13` literal will overshoot/drift.
- **Evidence**: pyproject.toml floor is 3.10; design.md prose suggested 3.13. Aggregated lesson L68 / BC-PROJ-11 generalises.
- **Proposed fix**: Reword installer suggestions to version-agnostic commands (`winget install Python.Python.3` / `brew install python`) + "Python 3.10 or newer".
- **Builder draft**: ACCEPTED-FIXED at design.md "What's new" Step 2 "I'll wait" installer suggestions entry + Error model recovery path 2.

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (BOOT_PYTHON capture mechanism not specified), M2 (no-partial-state claim qualified-true but misleadingly worded), M8 (MEPD-1(b) discharge by precedent), m1 (WIRE-1 exemption-class claim precedent-only). Per Wiegers + Cockburn.
- [x] **Missing edge cases** — M1 (unbounded "I'll wait" loop), M4 (shell-dialect under-specified), M7 (R-16 class breadth). Per Hendrickson + Bach.
- [x] **Over-engineering** — none. Per Fowler/Beck YAGNI: 3-option ASK form bounded by SOAD-1; version-probe is one-liner; no speculative generality.
- [x] **Under-engineering** — B1 (AC #1 requires Step 3a uses detected interpreter; `$BOOT_PYTHON` mechanism didn't deliver), M3 (AC #4 loose substring doesn't enforce section-scoped preservation). TF-1 row coverage: all 5 ACs have rows or explicit out-of-scope.
- [x] **Contract gaps** — INSTALL.md IS the prose contract; M1 (No-Python branch retry semantics unbounded) per Newman idempotency, M4 (validation prose under-specifies shell dialect).
- [x] **Security** — none beyond input validation. The user-paste-interpreter-path surface IS a new input boundary; design correctly handles as input validation not authorization. OWASP A03 (Injection): `-c` is a Python flag, path is single argv arg not interpolated — no shell injection. ✓
- [x] **Drift from vault** — M6 (R-17 filing point contradicts aggregated-lessons L131), M8 (MEPD-1(b) discharge by precedent vs assertion-grep). Mission-brief Step-6 audit enumeration comprehensive ✓. Per Sommerville + ISO/IEC/IEEE 42010.
- [x] **Web-known issues** — Skipped; the design introduces no new external technology dependencies. Platform-specific concerns (Windows `python3` vs `python` PATH, `command -v` semantics, Git-Bash `test -x` on `.exe`) are in-house verifiable; APED-1 executed on this machine confirms `test -x` works under Git-Bash. One forward note: Python.org Windows installer's stance on registering `python3.exe` has shifted across releases (3.11+ optionally registers via Store-version aliases), but the fallback chain `python3 || python` handles both states.
- [x] **Cross-cutting conformance** — M3 (FBCD-1 sub-mode (a): AC4 substring-pin not section-scoped — same class as slice-058 M-add-1). M5 (BC-PROJ-11 / slice-058 lesson: `3.10` hardcoded; recipe-doc-must-reference-source-dynamically). M8 (MEPD-1(b) discharge-by-name not by analogy — slice-040/045/053 lineage). m1 (WIRE-1 exemption rationale honor-system but precedent-compliant). **APED-1 executed**: ran `test -x` against the venv python.exe (passed) and the version-probe one-liner (exit 0). No RSAD-1 self-application finding (slice does NOT mint a new rule). No PTFCD-1/PTFFD-1 finding (TF-1 row cites a file present on disk with 3 functions + 1 PENDING).

## Calibration note

The slice falls into the slice-045/057 born-retired defect-repair class but introduces a NEW input-boundary surface (user-pasted interpreter path) that's a genuine design choice — the design correctly recognised this but under-specified the execution mechanism (B1) and recovery-loop bounds (M1). The N≥10 codification-class precision streak (slice-037 audit-vs-real-artifact law) DOES apply here in the negative sense: this slice is NOT a codification-class slice (no rule mint, no audit-tool change), so the Critic IS expected to find substantive design defects rather than just structural codification compliance. B1 rests on executed verification (grep'd INSTALL.md bash fences + read the prose) — APED-1 discipline applied. The Builder applied ALL 12 dispositions as ACCEPTED-FIXED (no overrides, no deferrals); the cumulative N=12 zero-override outcome reinforces the slice-040 N+1 doctrine reading: this is the slice-058 lesson's first governed slice on the recipe-doc-version-literal class (M5 + m3), and the Critic correctly caught it.

## Triage

**Triaged by**: user
**Date**: 2026-05-23
**Final verdict**: CLEAN

User-ratified all 14 findings (12 first-Critic + 2 meta-Critic missed) as ACCEPTED-FIXED via structured-options TRI-1 gate. M-add-1 resolved with Option (b): INSTALL.md prose review explicitly OUT-OF-SCOPE for `/code-review` v1; structural coverage delegated to AC1–AC4 prose-pin tests + slice-045 `test_install_md_correctness.py` + slice-058 `test_install_md_wakeup_guardrail.py` + INST-1 audit. slice-062 nomination recorded for future formal extension of `/code-review` in-scope list. m-add-1 ACCEPTED-FIXED via one-sentence design.md addition naming the Claude-substitutes-the-path templating mechanism for `$user_path` + `$AI_SDLC_DIR`. Zero overrides, zero deferrals, zero escalations.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | design.md "What's new" Step 3a / Step 2 conda-default entries rewritten to inline-recompute pattern `$(command -v python3 || command -v python) -m venv`; all `$BOOT_PYTHON` references removed |
| M1 | Major    | ACCEPTED-FIXED | design.md Error model recovery path 2 specifies "'I'll wait' option REMOVED on retry"; mission-brief must-not-defer adds the bound |
| M2 | Major    | ACCEPTED-FIXED | design.md Error model recovery path 3 reworded to "no NEW partial-install artifact" + "pre-existing state unchanged" + "abort path must NOT clean up pre-existing state" |
| M3 | Major    | ACCEPTED-FIXED | design.md AC4 entry specifies `_step_1_section` helper + section-scoped assertion; mission-brief must-not-defer adds "inside the `## Step 1:` section" |
| M4 | Major    | ACCEPTED-FIXED | design.md path-validation entry pins bash-fence + Bash-tool routing + Git-Bash idiom consistency with INSTALL.md preflight |
| M5 | Major    | ACCEPTED-FIXED | design.md path-validation entry switches to dynamic pyproject.toml grep (`MIN_PY` resolved at runtime); new "INSTALL.md L71 sibling-literal drop" entry removes stale `3.11+`; mission-brief must-not-defer adds both items |
| M6 | Major    | ACCEPTED-FIXED | design.md "Risk register additions" header pinned to "appended in `/build-slice` Phase A (NOT deferred to `/reflect`)"; mission-brief Out of scope reworded to drop reflection.md phrasing |
| M7 | Major    | ACCEPTED-FIXED | design.md R-16 entry gains `**Notes**:` paragraph naming the broader class coverage (conda-only/NixOS/Termux/Docker) per slice-057/R-15 Notes-pattern |
| M8 | Major    | ACCEPTED-FIXED | design.md "Decisions made (ADRs)" gains explicit META-1 vacuous-satisfaction paragraph (`re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", ...)` + zero new sections = vacuously satisfied) |
| m1 | Minor    | ACCEPTED-FIXED | design.md WIRE-1 row shortened to canonical slice-051 form `rationale: test module — pytest is the consumer` |
| m2 | Minor    | ACCEPTED-FIXED | design.md "Decisions made (ADRs)" strengthened to "bounded parametric refinements within SOAD-1 + BFRD-1; no new architectural commitment" |
| m3 | Minor    | ACCEPTED-FIXED | design.md "What's new" Step 2 "I'll wait" installer-suggestions entry drops minor-version literals (`Python.Python.3` / `brew install python`); mission-brief must-not-defer adds the bullet |
| M-add-1 | Major | ACCEPTED-FIXED | Meta-Critic missed-finding (DR-1 EXTEND). User-ratified Option (b) at TRI-1 (2026-05-23): INSTALL.md prose review explicitly OUT-OF-SCOPE for `/code-review` v1; design.md "Out of scope" section gains new bullet naming the 5 structural review surfaces relied on instead (AC1–AC4 prose-pin tests + slice-045 + slice-058 install_md_* tests + INST-1 audit); slice-062 nomination recorded for future formal extension of `/code-review` in-scope list |
| m-add-1 | Minor | ACCEPTED-FIXED | Meta-Critic missed-finding (DR-1 EXTEND). design.md Error model recovery path 1 gains one-sentence naming the Claude-substitutes-the-path templating mechanism for `$user_path` and `$AI_SDLC_DIR` (same prose-templating pattern as existing INSTALL.md L137–L141 / L153 uses of `$AI_SDLC_DIR`; not a cross-bash-invocation shell-variable channel) |
