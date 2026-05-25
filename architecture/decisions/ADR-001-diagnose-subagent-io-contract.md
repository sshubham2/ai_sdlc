---
id: ADR-001
title: Diagnose subagent I/O — text-in-result + main-thread file writes
date: 2026-05-09
slice: slice-001-diagnose-orchestration-fix
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-001: Diagnose subagent I/O contract

## Context

The `/diagnose` skill spawns 11 parallel subagents to do code-analysis passes, each previously expected to write three output files (under `diagnose-out/sections/`, `findings/`, `summary/`). In a real `/diagnose` run on this machine on 2026-05-09, 8 of 10 spawned `general-purpose` subagents had Read denied for paths outside the target repo (specifically `~/.claude/skills/diagnose/...`), Write denied entirely, Bash/PowerShell denied, and the venv python denied. They could only Read inside the target repo and Grep/Glob.

The pattern is consistent with `general-purpose` subagents getting a narrower permission allowlist than the parent thread on at least some configurations of Claude Code. The failure mode may not reproduce on every machine, but it's a real production risk we hit. We need the skill to work regardless of whether subagents inherit parent permissions.

A second, related symptom: the one subagent that did write its YAML used a non-conformant shape (`findings: <dict>` instead of a list, wrong field names like `confidence`+`recommendation`, evidence as flat strings, IDs not in `F-CAT-hash` form). Root cause: it couldn't read `~/.claude/skills/diagnose/schema/finding.yaml` either, so it guessed the schema from training-data conventions.

A third symptom: when the main thread fell back to writing YAML itself via string templating, it produced YAML with unquoted strings containing colons, breaking `yaml.safe_load`.

These three symptoms share a root structural issue: **the skill's I/O surface assumes subagents can read out-of-cwd files and write inside the target.** When that assumption fails, every part of the pipeline breaks.

## Options considered

### Option 1 — Switch general-purpose subagents to forks

`Agent` without `subagent_type` creates a fork that inherits parent context.

- **Pros**: forks share parent's prompt cache; carry parent context.
- **Cons**: empirically uncertain whether forks inherit *permissions* (the system prompt only documents context inheritance, not permission inheritance); forks share parent's *model* so per-pass model routing (COST-1.1) breaks; forks carry the full parent context which is wasteful for narrow analysis tasks.
- **Verdict**: regresses COST-1.1 model routing (a real cost lever) for an uncertain permission gain. Rejected.

### Option 4 — Declare subagent tool needs at spawn time

Surface the subagent's required tool allowlist explicitly when calling Agent, so Claude Code prompts the user up-front for any missing permission grants.

- **Pros**: aligns with the documented Claude Code permission model (parent-restrictive inheritance + per-spawn prompts); transparent — user sees the permission ask up-front.
- **Cons**: depends on the harness actually surfacing a usable prompt for each subagent (10+ prompts in one fan-out is poor UX); doesn't help when the user's environment denies the permission outright; doesn't prevent the *schema-mismatch* root cause in §Context — even if subagents could Read out-of-cwd, they'd still need the schema embedded to author conformant YAML.
- **Verdict**: helpful as a complementary mitigation but doesn't address the slice's failure modes structurally. Rejected as primary, noted for completeness.

### Option 2 — Convert each pass into a named subagent

Create `~/.claude/agents/diagnose-pass-01-intent.md`, `diagnose-pass-03a-dead-code.md`, etc. Each named agent declares its own tool allowlist explicitly (the existing `diagnose-narrator` does this and it worked in the failing run).

- **Pros**: precedent works (narrator pattern); named agents respect their declared tool list, including Write.
- **Cons**: 11 new agent files duplicating most of the pass-template prose; tighter coupling between skill and agents (changing a pass means editing both `passes/*.md` and `agents/diagnose-pass-*.md`); inflates the canonical inventory in `tools/install_audit.py` significantly; less reusable since pass logic is now half in skill / half in agents.
- **Verdict**: viable but high maintenance cost. Rejected.

### Option 3 — Restructure: subagents return text in result message; main thread does all I/O (chosen)

Each subagent receives in its prompt: the pass template content + the finding schema content + TARGET/OUT paths. It returns its output as three fenced blocks (`section`, `findings`, `summary`) in its final message — no Read of out-of-cwd files, no Write, no Bash, no python invocation. After the subagent returns, the main thread invokes a new `skills/diagnose/write_pass.py` helper with the subagent's raw text. The helper extracts the blocks, normalizes the findings, validates against the schema imported from `assemble.py`, and writes the three pass files via `yaml.safe_dump`.

- **Pros**: solves permissions universally (subagents need only Read inside cwd + Grep/Glob); main thread enforces schema validation in one place (`normalize_finding`); YAML-quoting bug class disappears (yaml.safe_dump quotes strings with colons automatically); pass templates stay where they are; preserves COST-1.1 model routing (still spawn `general-purpose` with `model: opus|sonnet`); narrator agent unchanged.
- **Cons**: main-thread context grows by ~5–10KB per pass × 11 passes = ~50–100KB per /diagnose run (acceptable; far below context budget); subagents must comply with the fenced-block format (mitigated by `normalize_finding` tolerance + clear re-spawn on parse failure).
- **Verdict**: lowest blast radius, highest leverage. Chosen.

## Decision

Option 3. Subagents are analysis-only: they receive (in their prompt) the pass template content + the finding schema content + TARGET/OUT paths, and return their output as three fenced blocks in their final message. The main thread, after each subagent returns, invokes `skills/diagnose/write_pass.py` with the subagent's raw text — that helper extracts the blocks, normalizes the findings, validates against the schema imported from `assemble.py`, and writes the three pass files via `yaml.safe_dump`.

The narrator (`diagnose-narrator` named subagent) keeps its existing Read/Write pattern. It worked in the 2026-05-09 failing run, has a narrow declared tool list, and writes only `sections/00-overview.md`. No reason to change it.

## Consequences

- **Permission boundary irrelevant for analysis subagents.** They never need Write, Bash, python, or out-of-cwd Read. The diagnose skill works on machines where `general-purpose` subagents have the narrowest possible allowlist.
- **Schema mismatch becomes impossible at the file level.** The main thread is the only writer of `findings/*.yaml`; it imports `REQUIRED_FIELDS` from `assemble.py` and validates before write. A non-conformant subagent output produces a clear `write_pass.py` error (re-spawn), not a corrupt file that crashes assembly later.
- **YAML colon-quoting bug class disappears.** `yaml.safe_dump()` quotes strings containing colons automatically. The Python writer never round-trips through string templates.
- **Main thread context grows by ~100–440KB per /diagnose run** to hold subagent results (revised upward per critique M6 — the original 50–100KB estimate under-counted realistic Opus-quality output; pass 02-architecture's section alone can be 8–25KB, 03b-duplicates' findings YAML can be 7–10KB). Acceptable — still well below context-window budget for one /diagnose invocation, and forks/named-subagents would cost more in tokens overall. The 5-line schema crib sheet (m2) saves ~30KB on the embed side. **Measurement task carried to reflection.md**: instrument subagent result-text byte counts on the first /diagnose run after this slice ships; record actual per-pass and aggregate sizes so the next iteration can falsify or refine this estimate.
- **The fenced-block format is a soft contract.** Subagents are LLMs; they may occasionally deviate. `write_pass.py` is tolerant where it can be (`normalize_finding` for shape mistakes) and loud where it can't (missing fence → exit 2 → re-spawn).
- **Pattern is reusable.** Other diagnose-style skills could adopt the same pattern: subagents return structured text in fenced blocks; main thread parses + validates + writes. Recorded here for future reference; not committed to as a methodology rule.

## Reversibility

Cheap. The change is contained to the diagnose skill (`SKILL.md`, `assemble.py`, new `write_pass.py`, 11 pass-template tweaks). Reverting means restoring the prior SKILL.md and pass templates, deleting `write_pass.py`, removing `normalize_finding()` from `assemble.py`. No data migration, no contract break with downstream consumers (the `diagnose-out/` file layout is unchanged), no commitment from other skills to this pattern.

The decision could be revisited if:
- A future Claude Code release guarantees subagent permission inheritance, making Option 1 or 2 viable without their current downsides.
- The fenced-block convention proves too unreliable in practice (subagents miss the format >5% of the time after `normalize_finding` tolerance).
- Main-thread context bloat from subagent results becomes a real cost driver (unlikely at current scale).
