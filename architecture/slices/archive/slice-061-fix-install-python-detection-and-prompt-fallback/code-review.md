# Code Review: Slice 061 fix-install-python-detection-and-prompt-fallback

**code-Critic reviewed**: NOT EXECUTED — agent unspawnable in this session (session-cache miss)
**Date**: 2026-05-23
**Result**: AGENT-UNSPAWNABLE

## Summary

The `code-review` subagent could not be spawned in this Claude Code session. `~/.claude/agents/code-review.md` exists on disk (installed by slice-060) AND the in-repo `agents/code-review.md` is present at HEAD, but the runtime's agent registry was loaded at session start (BEFORE slice-060 merged to master at commit `63439c6`) and the static available-agents list does NOT include `code-review`. Calling the Agent tool with `subagent_type: "code-review"` raises `Agent type 'code-review' not found`. Per the `/code-review` SKILL.md error semantics, `agent-unspawnable` is an exit-1 HALT class — surfaced via structured-options AskUserQuestion at 2026-05-23 TRI-1-equivalent gate; user-ratified to skip /code-review for slice-061 with documented rationale (advisory-only + minimal in-scope surface) and auto-advance to `/validate-slice`.

## Why this is not a slice-061 quality gap

Per slice-061's TRI-1 M-add-1 Option (b) disposition (ratified 2026-05-23), **INSTALL.md is explicitly OUT-OF-SCOPE for `/code-review` v1**. The single in-scope changed file is `tests/methodology/test_install_md_python_detection.py` (4 functions, ~165 lines, pure prose-pin assertions on INSTALL.md). The structural review surfaces relied on instead, as documented in design.md:

1. **AC1–AC4 prose-pin tests** in this slice's test file (PASS 4/4 at mid-slice smoke + Step 6 pre-finish).
2. **slice-045's `tests/methodology/test_install_md_correctness.py`** (4 pins; PASS post-slice-061 edits).
3. **slice-058's `tests/methodology/test_install_md_wakeup_guardrail.py`** (Step 3h pins; PASS).
4. **INST-1 audit** via `tools/install_audit.py` (PASS — 26/26 skills, 6/6 agents, 4/4 templates, 27/27 tools, methodology v0.64.0).

Together these 4 surfaces provide deterministic structural coverage of INSTALL.md without the code-Critic's adversarial review. The test file itself (the in-scope changed code) is exercised by running its own assertions — meaningful self-review.

## Changed files (in-scope per `/code-review` SKILL.md:48-55 in-scope paths list)

- `tests/methodology/test_install_md_python_detection.py` — NEW file in this slice; created at `/repro` Step 3 with 3 prose-pin assertions (AC1, AC2, AC3); extended at `/build-slice` task 1 with a `_step_1_section` helper + AC4 regression-guard `test_install_md_step_1_preserves_python3_or_python_detection_chain`. NOT reviewed by the code-Critic this slice (agent unspawnable).

## Out-of-scope changed files (documented for context only)

- `INSTALL.md` — modified; OUT-OF-SCOPE per slice-061 TRI-1 M-add-1 Option (b) disposition (ratified 2026-05-23) AND not in `/code-review` SKILL.md's in-scope paths list.
- `architecture/risk-register.md` — modified; out-of-scope (vault `architecture/**`).
- `architecture/shippability.md` — modified; out-of-scope (vault).
- `architecture/slices/slice-061-*/*.md` — added; out-of-scope (vault).

## Discovered class — recurring footgun, R-18 candidate

The agent-unspawnable session-cache miss is a **recurring class** that fires for any slice immediately following a slice that ships a new subagent (`agents/*.md`). The class signal:

- A slice (slice-N) ships a new subagent file to `~/.claude/agents/<name>.md` via INSTALL.md / the install path.
- The same Claude Code SESSION that runs slice-N's `/build-slice` is also the session that runs slice-(N+1)'s skills.
- Claude Code's agent registry is loaded at SESSION start (not hot-reloaded on agent-file-write).
- Therefore slice-(N+1) cannot spawn slice-N's new agent until the user restarts Claude Code.
- slice-(N+1)'s `/code-review` invocation (or any other skill that spawns slice-N's new agent) hits `agent-unspawnable`.

**Witnessed**: slice-061 is the first slice after slice-060 (which shipped the `code-review` subagent); slice-061's auto-advance to `/code-review` hit `agent-unspawnable`. **N=1**.

**Mitigation classes** to record at /reflect (R-18 nomination — `mitigating` or `open`):

- (a) `/build-slice`'s pre-finish gate could add a `new-agent-this-slice` detector + WARN ("You shipped a new agent; restart Claude Code before invoking the next slice's chain") — same shape as BCI-1's reflect-step deterministic-downstream-gate pattern.
- (b) `/code-review`'s `agent-unspawnable` error semantics could be widened from "exit 1 HALT" to "WARN + skip with documented rationale" specifically for the first slice after a new-agent slice — surface the cache-miss as known + auto-advance with `AGENT-UNSPAWNABLE` result.
- (c) The INSTALL.md / install path could exec a `kill -USR1 <claude-pid>` (or equivalent platform-specific signal) after a new-agent install to force the registry to re-load — but this is platform-specific and likely out of scope for INSTALL.md prose.

For slice-061, the disposition is "skip /code-review for this slice; advance to /validate-slice" because slice-061's PRIMARY artifact (INSTALL.md) was already out-of-scope for /code-review v1 per the M-add-1 Option (b) disposition.

## Findings

None — code-Critic did not run; no findings to report. The structural surfaces named above (AC1–AC4 + slice-045 + slice-058 + INST-1) all PASS at /build-slice pre-finish.

## Dimensions checked

All 9 dimensions: NOT EXECUTED (agent unspawnable). See "Why this is not a slice-061 quality gap" above for the structural-coverage substitute.

- [ ] Unfounded assumptions — NOT EXECUTED
- [ ] Missing edge cases — NOT EXECUTED
- [ ] Over-engineering — NOT EXECUTED
- [ ] Under-engineering — NOT EXECUTED
- [ ] Contract gaps — NOT EXECUTED
- [ ] Security — NOT EXECUTED
- [ ] Drift from vault — NOT EXECUTED
- [ ] Web-known issues — NOT EXECUTED
- [ ] Cross-cutting conformance — NOT EXECUTED
