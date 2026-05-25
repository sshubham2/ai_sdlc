---
id: ADR-050
title: Generalize ADR-048's gate-specific structured-options-ask requirement into a pipeline-wide skill-ask discipline (SOAD-1)
date: 2026-05-19
slice: slice-048-codify-structured-options-ask-rule
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-050: Generalize the structured-options-ask requirement to a pipeline-wide discipline (SOAD-1)

## Context

ADR-048 (slice-046, `methodology-changelog.md` v0.55.0) established — for the **single** BFRD-1 Step 3c confirm gate — that the user prompt MUST be presented as `AskUserQuestion` structured options, explicitly because "a free-text question does NOT surface a user notification". That reasoning is **not gate-specific**: it is a property of the Claude Code platform. Any pipeline skill that pauses on a bare free-text question blocks silently — the user is never notified the skill is waiting, so the pipeline stalls invisibly until the user happens to look.

This recurred enough to be captured as a standing user directive: user memory `ask-via-structured-options.md` ("free-text questions don't trigger the user notification; always use option lists") and `repro-confirm-then-auto-invoke.md`. The 2026-05-19 user request asks that this be promoted from a single-gate rule + a personal memory into a first-class pipeline discipline written into the project-root `CLAUDE.md` that `/triage` and `/adopt` emit into every adopted/triaged project.

`/triage` Step 5b and `/adopt` Step 10 each emit a deliberately tiny (~15–25 line) project-root `CLAUDE.md` (fresh + append variants — 4 template blocks total). That file is the only pipeline artifact loaded into the orchestrator every session, so it is the correct home for a cross-cutting interaction discipline.

## Options considered

1. **Leave it gate-specific (status quo).** Pros: zero work. Cons: every non-BFRD-1 skill ask remains free to block silently; the platform-UX gap the user repeatedly hit stays uncodified; the practice survives only as a personal memory (not portable to other pipeline adopters, not self-hosting-auditable).
2. **Codify SOAD-1 in the `/triage` + `/adopt` CLAUDE.md templates + this repo's CLAUDE.md, regression-pinned (CHOSEN).** A new RULE-ID, one canonical sentence reused verbatim across 5 surfaces, a genuine-contrast prose-pin test, methodology-changelog + VERSION/plugin.yaml bump. Pros: portable to every pipeline project; self-hosting-auditable; cheap; bounded ≤1 day. Cons: a CLAUDE.md contract governs behavior but does not mechanically force each skill's prose into the options form (mitigated: future per-skill retrofit / lint audit is an explicit out-of-scope follow-up).
3. **Also retrofit all 24 skills' ask-the-user prose now.** Pros: maximal enforcement. Cons: >1 day, would need splitting; the CLAUDE.md contract already governs orchestrator behavior without per-skill edits. User-decided out of scope.

## Decision

Adopt Option 2. Mint **SOAD-1** (Structured-Options-Ask Discipline) — a discipline/contract rule (no standing executable audit tool; enforced by a prose-pin regression test). One canonical sentence is written verbatim into the `/triage` Step 5b fresh+append templates, the `/adopt` Step 10 fresh+append templates, and this repository's own project-root `CLAUDE.md`. `methodology-changelog.md` gains a `v0.56.0` entry; `VERSION` and `plugin.yaml:version` bump 0.55.0→0.56.0 in lockstep.

SOAD-1 mandates structured options **as the primary/default ask form**, not an absolute ban: the ADR-048 verbal-claim-with-path escape hatch (where `AskUserQuestion` genuinely cannot model the input) remains legitimate.

This ADR **does not supersede ADR-048**. ADR-048 remains the authority for the BFRD-1 Step 3c gate specifically; SOAD-1 is the pipeline-wide superset of which that gate is now one instance.

## Consequences

- Every future `/triage`- or `/adopt`-opened project ships a CLAUDE.md carrying SOAD-1 — orchestrators are told, every session, to ask via structured options.
- This repo dogfoods the rule (self-hosting discipline): its own CLAUDE.md carries SOAD-1, regression-pinned.
- A new genuine-contrast test (`tests/methodology/test_soad1_structured_options_ask_rule.py`) + shippability catalog row prevent silent removal of the rule from any of the 5 surfaces.
- No runtime/contract/data-model surface; no new tool, skill, or agent → INST-1 canonical lists and `plugin.yaml` artifact enumeration are unchanged (only `version` moves).
- Out of scope (explicit follow-ups, not blockers): a per-skill prose retrofit; an executable lint that scans skill prose for free-text-ask anti-patterns; the user's personal `~/.claude/CLAUDE.md`.

## Reversibility

**cheap** — reverting is deleting one sentence from 5 prose surfaces, removing the v0.56.0 changelog entry, reverting VERSION/plugin.yaml, and deleting one test (~1 hour, no downstream code consumers, no data migration, no contract break).
