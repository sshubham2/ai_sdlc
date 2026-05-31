# Code Review: Slice 088 add-project-frame-synthesizer

**code-Critic reviewed**: slice diff vs default branch `master` (base `64f6ea3`), filtered to in-scope paths, read from worktree `slice/088`
**Date**: 2026-05-31
**Result**: FINDINGS (0 Blockers, 2 Majors, 3 Minors) — **all addressed in-slice** (advisory v1; Builder elected to fix the real defects before ship rather than defer)

## Summary

The slice is solid and well-tested. The code-Critic empirically **confirmed the cp1252 deviation is sound** — it proved the em-dash/arrow text genuinely reaches stdout (the bespoke test is non-vacuous) and that `_stdout.reconfigure_stdout_utf8()` is both *necessary* (its own un-reconfigured `print()` crashed on U+2192) and *sufficient* (the subprocess path emits cleanly). The deviation does NOT reintroduce the B1/M-add-1 crash. It found one real correctness bug in the rule-family regex, one budget-contract violation, and three minor robustness gaps. **All five were fixed in-slice; full suite 1255 passed post-fix.**

## Changed files (in-scope)

```
tools/project_frame_synth.py
tests/methodology/test_project_frame_synth.py
tests/methodology/test_project_frame_synth_tool_inventory.py
tests/methodology/test_design_slice_skill_drift.py
tests/methodology/test_critique_skill_drift.py
tests/methodology/test_critique_review_skill_drift.py
tests/methodology/test_design_slice_skill_frame_consult.py
tests/methodology/test_critique_skill_frame_input.py
tests/methodology/test_critique_review_skill_frame_input.py
tests/methodology/test_utf8_stdout_regression.py
tests/methodology/test_methodology_changelog.py
tests/methodology/test_pulse_worktree_resolver_tool_inventory.py
skills/design-slice/SKILL.md
skills/critique/SKILL.md
skills/critique-review/SKILL.md
agents/critique.md
tools/install_audit.py
plugin.yaml
INSTALL.md
VERSION
pyproject.toml
methodology-changelog.md
CLAUDE.md
architecture/slices/slice-088-add-project-frame-synthesizer/build-log.md
```

## Findings

### Blockers
None.

### Majors

#### M1: `_RULE_TITLE_RE` silently drops letter-suffixed rule-ids (PCR-2a / PCR-2b) from Trajectory
- **Claim under review**: `tools/project_frame_synth.py` `_RULE_TITLE_RE = r"^\*\*([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*)\b"`.
- **Issue**: For `PCR-2b`, the trailing `\b` fails between `2` and `b` (both word chars), so `-2` backtracks away and the capture collapses to `PCR` (no `-<digit>`), which `_FAMILY_RE` then rejects → the entry contributes nothing. On the real changelog, `PCR` survived only because v0.73.0 `PCR-1` (unsuffixed) coincidentally rescued it; a family whose only recent entries are letter-suffixed would vanish. APED-1 miss class (the `-Na` variant the changelog actually contains was never executed against the regex).
- **Proposed fix**: tolerate a trailing lowercase letter + drop `\b`.
- **Disposition**: **FIXED in-slice** — `_RULE_TITLE_RE = r"^\*\*([A-Z][A-Z0-9]*(?:-[A-Z0-9]+[a-z]?)*)"` (comment cites M1). Added a `PCR-2b` block to the `test_frame_trajectory_synthesizes_not_concatenates` fixture + an `assert "PCR" in traj`. Real-repo smoke now surfaces `PFS, PCR, DCE, BCSG, PSQ, BRANCH`.

#### M2: `synthesize_frame` violates its own line budget for `max_lines <= 0` (reachable via CLI `--max-lines 0`)
- **Claim under review**: `lines = lines[: max_lines - 1] + [_TRUNCATION_MARKER]`; CLI `--max-lines` is unconstrained `type=int`.
- **Issue**: `max_lines <= 0` → `max_lines - 1` negative → negative-index slice drops only the tail; `max_lines=0` emitted 14 lines (more than `max_lines=5`), defeating "tight, not a dump".
- **Disposition**: **FIXED in-slice** — clamp `if max_lines < 1: max_lines = 1` in `synthesize_frame` (comment cites M2) + `parser.error("--max-lines must be >= 1")` at the CLI (exit 2, never a breach). Added `test_budget_clamps_degenerate_max_lines` (asserts ≤1 line for 0/-1/-10 + CLI exit 2).

### Minors

#### m1: cp1252 bespoke test asserts no-error but not positive em-dash survival
- **Disposition**: **FIXED in-slice** — appended `assert "→" in proc.stdout` (the arrow rides the R-1 risk title into Trajectory); makes the M-add-2 "fixture must carry em-dash" obligation self-documenting.

#### m2: `_open_risks` couples to `risk_register_audit._parse_risks` private API
- **Disposition**: **ADDRESSED in-slice** — added a comment documenting the intentional coupling + `test_open_risks_uses_parse_risks_api` pinning `_parse_risks` + the `Risk` fields (risk_id/title/score/status), so a future risk-audit refactor trips a red test rather than silently emptying the risk line.

#### m3: `_pending_candidates` had no degrade-WARN, unlike every other section
- **Disposition**: **FIXED in-slice** — threaded the `warn` callback through `_pending_candidates`; `warn("slice-queue.md missing")` on a missing source, matching the sibling sections' error model.

## Dimensions checked
- [x] Unfounded assumptions — M1 (regex-vs-docstring parity break). Other docstring claims verified against behavior.
- [x] Missing edge cases — M2 (`max_lines <= 0`). Empty/missing sources degrade cleanly (exit 0, WARN); budget boundary N-1/N/N+1 correct for ≥1.
- [x] Over-engineering — none (~270 lines, no speculative abstraction, no dead code).
- [x] Under-engineering — none. Every AC has a delivering element + test; OSDG-1 extended with real drift tests; BC-PROJ-9 propagated; PMI-1/INST-1 clean.
- [x] Contract gaps — M2 (CLI budget validation); exit-code contract 0/2-never-1 honored; m2 private-API coupling.
- [x] Security — none. Read-only local synthesis, no network/writes/auth/subprocess. The frame is pasted into agent prompts but renders the project's own vault text — same trust level as the `# mission-brief.md` / `# design.md` blocks already pasted; no new injection vector.
- [x] Drift from vault — none. Code matches design.md (5 surfaces); cp1252 deviation documented; MEPD-1 rule-path fully discharged (VERSION/pyproject/plugin.yaml 0.78.0, changelog header, entry-pin green).
- [x] Web-known issues — Skipped (runtime/regex behavior verified empirically under Python 3.13; standard `re` word-boundary semantics, not a platform issue).
- [x] Cross-cutting conformance — M1 is the APED-1 miss (parse rule not executed against the `-Na` variant). UTF8-STDOUT-1 conformance verified empirically (reconfigure necessary + sufficient). No phantom imports; `from __future__ import annotations` present.

## Builder note (CRSI-1 calibration input for /reflect)
3-Critic stack complementarity held: the design-Critic + meta-Critic (at /critique) caught the cp1252 *risk* and the synthesis/contract design gaps; the code-Critic — by EXECUTING the regex against the real changelog and running the tool at budget boundaries — caught two defects (M1 letter-suffix regex collapse, M2 negative-slice budget breach) that are structurally unreachable from design-time review. M1 is a fresh instance of the regex-APED-1 / BC-PROJ-13 miss class (N+1). Builder elected in-slice fix over bundled-cleanup deferral because both Majors are correctness/contract defects in the slice's core deliverable, caught pre-ship.
