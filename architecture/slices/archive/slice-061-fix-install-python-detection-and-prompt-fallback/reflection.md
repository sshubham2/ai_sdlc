# Reflection: Slice 061 fix-install-python-detection-and-prompt-fallback

**Date**: 2026-05-23
**Shipped**: YES-WITH-DEFERRALS (one user-approved deferral on pre-existing slice-060 R-15-class shippability row; one /code-review skipped due to AGENT-UNSPAWNABLE session-cache miss — both fully documented + ratified)

## Validated

- **B1 (`$BOOT_PYTHON` cross-bash-invocation persistence broken)** — validated by inspecting INSTALL.md's fenced bash blocks at L46/L115/L135/L152/L164/L196/L252; each is a separate `bash -c` invocation. The inline-recompute `$(command -v python3 || command -v python) -m venv` fix matches Step 1's pre-flight echo and works deterministically.
- **M1 (option-removed-on-retry IS the enforcement mechanism)** — validated by reading the rewritten INSTALL.md Step 2 No-Python branch: the retry-form prose explicitly removes the "I'll wait" option on re-fire (only "Provide interpreter path" + "Abort install" remain).
- **M3 (section-scoping the AC4 regression-guard via `_step_1_section`)** — validated by AC4 PASSING pre-edit (the chain IS in Step 1 at L56) and continuing to PASS post-edit. The helper mirrors the existing `_step_3a_section` / `_step_2_section` pattern (slice-049/051 OSDG-1 mini-CAD class-mirror discipline applied to test-helper idiom).
- **M5 + m3 (dynamic-pyproject-floor Python version + version-agnostic installer suggestions)** — validated by the BC-PROJ-11 grep at /build-slice task 9 returning zero hits post-fix. INSTALL.md now has ZERO hardcoded version literals.
- **M8 (MEPD-1(b) discharge-by-assertion not by precedent analogy)** — validated by `tests/methodology/test_methodology_changelog.py:136`'s `re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", changelog, flags=re.MULTILINE)` assertion: slice-061 added zero new `## v…` sections → vacuously satisfied.
- **slice-055 user-approved-deferral precedent** — validated as a stable disposition pattern (N=2 with slice-061): when shippability dogfood surfaces a PRE-EXISTING prior-slice defect, the right move is user-approved deferral with slice-NNN nomination for the structural fix.
- **slice-058 BC-PROJ-11 lesson** — validated at /build-slice task 9 (audit-time catch): the lesson L68 generalizes from VERSION literals to ALL methodology-version literals, including the Python-version floor; the inline-fix demonstrates the rule's coverage.

## Corrected

(None — design.md + mission-brief.md were updated in-place at /critique + /critique-review TRI-1 step BEFORE /build-slice. By the time the slice was built, the design was already corrected. No mid-build deviations required design.md edits.)

## Discovered

- **R-18 (NEW — mitigating)**: Newly-installed Claude Code subagents not hot-loaded into the running session. Class-signal N=1 (slice-061 hit `agent-unspawnable` for `/code-review` after slice-060 shipped the agent in the same session). Added to `[[risk-register#R-18]]`. Candidate fixes: (a) `/build-slice` post-build warning when slice's diff includes a new `agents/*.md`; (b) `/code-review` error-semantic widening to auto-skip on the recurring-class case; (c) Claude Code platform fix (registry hot-reload — out-of-scope for AI SDLC). slice-062 nomination.

- **BC-PROJ-11 calibration miss (N=1 watch-list)**: the first-Critic + meta-Critic both missed an instance of the SAME class (`Python 3.10 or newer` literal) that the M5 finding addressed at a sibling surface (the installer-guidance prose). The audit-time backstop (BC-1 fan-out at /build-slice Step 6) caught it cleanly at intended latency. Per slice-037 audit-vs-real-artifact law: no Critic dim / no BC-1 promotion at N=1 — this is a `/critic-calibrate` watch-list candidate. **Specific gap**: when fixing a hardcoded literal at one surface, the Critic stack tends to focus on the named surface and miss sibling instances of the same class in adjacent prose. If N=2 emerges, promote to a Critic-prompt dimension extension via `/critic-calibrate`-route.

- **Pre-existing slice-060 R-15-class scope gap (N=1 watch-list → likely slice-062)**: the slice-056 corpus class-closure backstop (`test_no_new_archive_fragile_literals_in_methodology_corpus`) scopes only `tests/methodology/*.py` — does NOT cover `tests/skills/**/*.py` or `tests/agents/**/*.py`. slice-060's `tests/skills/code_review/test_code_review_skill.py` shipped with an active-path literal that broke when slice-060 was archived. The slice-061 deferral is the operational outcome; the structural fix is to extend the backstop's scope. Coupled with R-15's existing retired-but-class-still-open status (the corpus backstop's class-closure mechanism IS sound for `tests/methodology/`; the extension is to widen scope, not redesign).

## Deferred

- **slice-062 nomination — extend R-15 corpus class-closure backstop scope to `tests/skills/**/*.py` + `tests/agents/**/*.py`** + repoint `tests/skills/code_review/test_code_review_skill.py::test_self_dogfood_produces_code_review_md_on_slice_060` via `_resolve_slice_dir(60)`. Two coupled fixes; same slice. User-approved deferral logged at /build-slice Step 6 + /validate-slice.

- **slice-062-or-later nomination — R-17 BRANCH-1 clean-tree precondition fix** (extend `tools/branch_workflow_audit.py` with pre-create cleanliness invariant OR offer `git worktree add` path in /build-slice Prerequisite check). Discovered as adjacent class during slice-061 /slice + /build-slice; design.md + mission-brief.md explicitly out-of-scope (committed at TRI-1 as a separate slice's work, not slice-061's). Strong slice-062+ candidate on the pipeline-hygiene track.

- **slice-062-or-later nomination — R-18 mitigation** (one of the (a)/(b)/(c) candidate fix classes from risk-register R-18). Likely (a) `/build-slice` post-build new-agent warning is the cheapest + most generalizable.

- **`/critic-calibrate` watch-list ratchet** — BC-PROJ-11 sibling-coverage class (N=1; needs N=2 before promotion). The current /critic-calibrate skill processes "Missed by Critic" entries; this slice contributes one such entry.

## Critic calibration

Per TRI-1 + the disposition in `critique.md` `## Triage` table + reality observed during build/validate:

**First-Critic findings** (all 12 dispositioned ACCEPTED-FIXED at TRI-1):

- **B1** (`$BOOT_PYTHON` cross-bash): **VALIDATED** — bug confirmed by grep'ing INSTALL.md bash-fences at /build-slice; the inline-recompute fix was the only sound mechanism.
- **M1** (unbounded "I'll wait" loop): **VALIDATED** — the option-removed-on-retry IS the only mechanism that bounds the loop; without it the prose claim was unenforced.
- **M2** (abort-path wording): **VALIDATED** — the qualified-true-but-misleading wording was correctly identified; reworded contract is materially clearer.
- **M3** (AC4 section-scoping): **VALIDATED** — the test file's `_step_1_section` helper was the cleanest implementation; mirrors existing pattern.
- **M4** (PowerShell routing risk): **VALIDATED** — Bash-fence + Bash-tool routing is load-bearing; the user's global CLAUDE.md PowerShell-preference made the routing ambiguity material (APED-1-verified by the first-Critic executing `test -x` against the venv python.exe).
- **M5** (`>= 3.10` hardcoded): **VALIDATED** — dynamic-pyproject-grep is the right fix; verified at BC-PROJ-11 grep.
- **M6** (R-17 canonical filing surface): **VALIDATED** — R-17 lives in risk-register.md (not reflection.md) per aggregated-lessons L131; correctly applied at /build-slice task 7.
- **M7** (R-16 broader class): **VALIDATED** — Notes paragraph correctly anchors second-platform reports as NEW R-NN entries; slice-057/R-15 pattern.
- **M8** (MEPD-1(b) discharge-by-assertion): **VALIDATED** — verified by reading `test_methodology_changelog.py:136`; vacuous-satisfaction is the correct discharge for zero-`## v…`-section slices.
- **m1** (WIRE-1 honor-system): **VALIDATED** — canonical slice-051 form is cleaner + audit-format-compliant.
- **m2** (ADR criteria mechanical): **VALIDATED** — strengthened SOAD-1 + BFRD-1 framing is the right tightening.
- **m3** (installer minor-version literals): **VALIDATED** — same class as M5 at sibling surface; de-versioning correct.

**Meta-Critic findings** (both VALIDATED at TRI-1):

- **M-add-1** (INSTALL.md not in /code-review in-scope list): **VALIDATED** — user-ratified Option (b) (out-of-scope for v1) at TRI-1; the disposition held during /code-review (skipped via AGENT-UNSPAWNABLE auto-advance with no quality regression because the structural review surfaces named in Option (b) all PASSed).
- **m-add-1** (`$user_path` / `$AI_SDLC_DIR` prose-templating mechanism unnamed): **VALIDATED** — one-sentence design.md addition + INSTALL.md inline explanation correctly anchors the templating mechanism without breaking the inline-recompute pattern (B1's choice).

**Missed by Critic** (BOTH first-Critic AND meta-Critic):

- **BC-PROJ-11 sibling-coverage gap** — the M5 fix specified dynamic-pyproject-grep for the path-validation surface, but the installer-suggestions prose carried a `Python 3.10 or newer` literal that BOTH Critic layers passed. The audit-time backstop (BC-1 fan-out at /build-slice Step 6) caught it; fixed in same Step 6 phase. **Class**: when fixing a hardcoded literal at one named site, the Critic stack tends to focus on the named site and miss sibling instances of the same class in adjacent prose. **Per slice-037 law**: build-time-reachable + gate-caught → no Critic dim / no BC-1 promotion at N=1; `/critic-calibrate` watch-list candidate (track if N=2 emerges).

- **R-18 cross-slice agent-loading interaction** — neither first-Critic, meta-Critic, nor code-Critic could have caught this; the trigger condition is a cross-slice (slice-060 → slice-061) interaction with the Claude Code runtime's agent-loading model, invisible to single-slice review. Surfaced at the auto-advance hop itself. Per slice-037 law: the right tooling is methodology-side warning + risk-register tracking, NOT a Critic-prompt dimension.

**Pattern (slice-061-specific)**:

- The zero-false-alarm dual-Critic streak holds at **N=12 cumulative** on codification-class slices (slice-046/048/050/051/052/053/054/055/056/057/058/061). All 12 first-Critic findings + both meta-Critic missed findings VALIDATED, ZERO false-alarms, ZERO override-misjudged.
- The slice-040 N+1 "discipline rule minted in N is blind-spot in N+1; DR-1 meta-Critic is the structural backstop" doctrine extends to **N=12 cumulative**. slice-060 minted /code-review + the CRSI-1 in-loop adversarial code-review surface; slice-061 was its first governed slice; the meta-Critic caught M-add-1 (INSTALL.md not in /code-review's in-scope list) — the canonical N+1 first-governed-slice catch on a fresh-surface scope-list class. Pattern holds.
- **NEW class signal — cross-slice runtime-state interactions** (N=1): R-18 is the canonical example. Both Critic layers cannot reach into runtime-state characteristics of the Claude Code harness itself. Build-time + runtime-time gates are the structural backstop. If N=2 emerges, consider a `/critic-calibrate` dimension for "cross-slice runtime-state interactions" or a methodology-side warning.

## Lessons for next slice

- **When a slice ships a new subagent (`agents/*.md`), the SAME Claude Code session running the next slice cannot spawn it.** The agent registry is loaded at session start; mid-session file writes are invisible. Mitigation: (a) restart Claude Code between agent-shipping slices, OR (b) accept the auto-advance to /code-review will hit `AGENT-UNSPAWNABLE` and route through user-ratified skip per slice-061's documented disposition. Long-term: methodology-side warning at /build-slice when slice diff includes a new `agents/*.md`.

- **When the slice-N+1 inherits a prior-slice's archive-fragile path test, the right disposition is user-approved deferral + slice-N+2 nomination for the structural fix.** slice-055 → slice-056 set this precedent for `tests/methodology/`; slice-061 → slice-062 extends it for `tests/skills/**/*.py` + `tests/agents/**/*.py`.

- **BC-PROJ-11 sibling-coverage gap is a real Critic blind spot.** When a slice fixes a hardcoded literal at one surface, scan the entire artifact for sibling instances of the same class in adjacent prose AT DESIGN TIME (during /design-slice Step 2 or /critique Step 4) — the Critic stack will miss them otherwise. Build-time BC-PROJ-11 grep at /build-slice Step 6 IS the structural backstop, but moving the catch earlier saves an audit-time fix block.

- **The slice-060 → slice-061 N+1 governed-slice pattern is now confirmed for the /code-review skill axis.** Future slices auto-advancing to /code-review on the slice-060-shipped chain extension will encounter the agent-registry session-cache issue until the user restarts. Either accept this as a known quirk, or ship the (a) candidate-fix in slice-062.

## Vault updates made

- `architecture/risk-register.md` — **R-16** born-retired (INSTALL.md python-detection brittleness; with `**Notes**:` paragraph for broader-class coverage); **R-17** open-mitigating (BRANCH-1 clean-tree precondition); **R-18** open-mitigating (newly-installed Claude Code subagents not hot-loaded). 18 risks total post-slice (10 retired / 6 mitigating / 2 open). RR-1 audit clean.
- `architecture/shippability.md` — row **#61** added at /repro Step 5 (citing `tests/methodology/test_install_md_python_detection.py`).
- `INSTALL.md` — Step 1 unchanged (regression-guard pins); Step 2 No-Python branch rewritten as 3-option SOAD-1 ASK gate with dynamic-pyproject-floor path-validation bash fence + bounded retries + version-agnostic installer suggestions; Step 2 conda-default uses inline-recompute; Step 3a uses inline-recompute. ZERO hardcoded version literals remain.
- `tests/methodology/test_install_md_python_detection.py` — NEW file (created at /repro with 3 prose-pin assertions; extended at /build-slice task 1 with `_step_1_section` helper + AC4 regression-guard).
- `architecture/slices/slice-061-.../` — full phase artifact set (mission-brief.md, design.md, critique.md, critique-review.md, build-log.md, code-review.md AGENT-UNSPAWNABLE, validation.md, reflection.md, milestone.md).
- **NO** methodology-changelog.md entry, **NO** VERSION bump, **NO** plugin.yaml bump, **NO** ADRs (defect-repair conformance class; slice-045 R-11 precedent; MEPD-1(b) discharged-by-name vs META-1 assertion at `tests/methodology/test_methodology_changelog.py:136`; vacuously satisfied — zero new `## v…` sections).

## BCR-1 round-trip status

NO-OP CLEAN. Slice-061 is a user-reported INSTALL.md defect-repair, NOT a backlog candidate. Neither mission-brief.md nor reflection.md carries a `**Closes:** SC-\d{3}` sentinel header. `diagnose-out/backlog.md` exists in the repo (23 SC candidates remain post slice-057) but is not touched by this slice. The BCR-1 trigger correctly no-ops per the slice-053 ADR-055 mention-vs-application disambiguation.
