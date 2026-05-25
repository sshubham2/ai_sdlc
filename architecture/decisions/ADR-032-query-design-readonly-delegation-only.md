---
id: ADR-032
title: query-design is an out-of-loop, read-only, delegation-only exploratory skill
date: 2026-05-17
slice: slice-032-add-query-design-skill
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-032: query-design is an out-of-loop, read-only, delegation-only exploratory skill

## Context

Slice-032 adds `/query-design`, a conversational skill for asking truthful questions about the *existing* codebase. The mission brief deliberately left one mechanism open: when a question surfaces a real requirement or defect, does `query-design` author a slice-candidate / backlog file itself, or delegate? This decision must be locked now because it determines the skill's core safety invariant and whether the skill participates in the PCA-1 auto-advance chain — both shape every line of the SKILL.md being written this slice.

## Options considered

1. **`query-design` directly authors a slice-candidate / `backlog.md` file** — pro: one-step from question to actionable backlog. Con: a file write directly contradicts the skill's stated value proposition ("changes nothing"); `/slice-candidates` structurally consumes an annotated `diagnosis.html` that `query-design` never produces, so it would have to invent a divergent candidate format; the moment it writes, every "read-only" guarantee in the prose is false.
2. **`query-design` is read-only and delegates by offering to invoke `/slice`** — pro: the read-only invariant is absolute and verifiable; downstream writes happen only inside `/slice` (or the `/diagnose`→`/slice-candidates` route) under that skill's own discipline; the handoff is explicit and declinable. Con: two steps from question to backlog when a requirement is found (acceptable — the skill's purpose is understanding, not authoring).
3. **`query-design` joins the PCA-1 pipeline chain and auto-advances to `/slice`** — pro: consistent with in-loop skills. Con: it is an ad-hoc exploratory entrypoint, not a pipeline stage; auto-advancing from an open-ended Q&A would force slice creation the user may not want, and a Q&A session has no deterministic "clean completion" signal. It belongs with the out-of-loop class (`/status`, `/diagnose`, `/reduce`, `/drift-check`), none of which carry a `## Pipeline position` block.

## Decision

Adopt option 2 + option 3's rejection. `/query-design` is **read-only**: it MUST NOT write, edit, or create source, vault, or candidate files; its only side effects are conversational output and — strictly on explicit user acceptance — invoking `/slice` with a distilled intent string (or recommending the `/diagnose`→`/slice-candidates` route for multiple/structural findings). It is **out-of-loop**: not a member of `tools/pipeline_chain_audit.py:_CANONICAL_CHAIN`, carries **no** `## Pipeline position` block, and never auto-advances. The handoff is always an offer the user can decline, after which the skill ends with zero side effects.

## Consequences

- **Read-only enforcement mechanism (examined, post-critique M2)**: the official Claude Code skills spec offers an `allowed-tools` SKILL.md frontmatter field as platform-native tool restriction. Verified: **zero** skills in this repo use it (including read-only peers `/status`, `/diagnose`, `/drift-check`); the project convention is `name:`+`description:` frontmatter only, and skills here execute **inline in the main thread** via the Skill tool — not as packaged-plugin restricted subagents where `allowed-tools` semantics are defined. Introducing `allowed-tools` for `query-design` alone would be an unprecedented divergent mechanism of unverified efficacy in the inline path. Decision: enforce read-only via (a) unambiguous SKILL.md prose, (b) the QD-1 changelog rule, (c) the drift test pinning that prose. This is a deliberate, examined choice — not an unexamined prose-only default. If a future platform change makes `allowed-tools` honored for inline skills, a superseding ADR may add it as defense-in-depth (cheap to revisit — see Reversibility).
- The SKILL.md must state the read-only / delegation-only / no-auto-advance invariant unambiguously (no "may edit if…" loophole) — this is the load-bearing safety property and a must-not-defer item.
- A new changelog rule **QD-1** (v0.46.0) codifies the invariant; a per-file drift test pins the SKILL.md prose against silent divergence (the contract is prose, so prose drift = contract drift).
- `query-design` is absent from `_CANONICAL_CHAIN`, so the PCA-1 pipeline-position drift test (parametrized over the chain) correctly does not require a block for it — no test change needed there.
- INST-1 / PMI-1 lockstep: adding the skill forces `_CANONICAL_SKILLS` + `plugin.yaml` + `VERSION` to move together (already in scope).
- Future flexibility preserved: if delegation proves too thin, a later slice can revise the handoff (e.g., emit a structured candidate stub) via a superseding ADR — cheap because the contract is prose, not a wired data interface.

## Reversibility

**cheap.** The decision lives entirely in SKILL.md prose + one changelog rule + one drift test. Changing the handoff model (e.g., to emit a candidate file) is a single-slice prose+test revision via a superseding ADR — no data migration, no consumer contract break, no irreversible commitment. Tagged cheap, not expensive, because nothing downstream binds to `query-design`'s behavior as a hard interface.
