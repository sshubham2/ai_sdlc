---
type: adoption-record
adopted: 2026-05-13
mode: STANDARD
opener-skill: /adopt
greenfield-triage: false
---

# Triage (brownfield adoption)

This vault was adopted into an existing codebase via `/adopt`, not opened greenfield via `/triage`. The pipeline was already in active use against this repo before the formal opener artifacts (this file, `concept.md`, root `CLAUDE.md`) were written — adoption was documentation-after-the-fact.

## Mode: Standard

**Rationale**: solo maintainer, established public-facing codebase (Claude Code plugin, v0.32.0), no compliance constraints, but the project itself defines and exercises adversarial Critic + meta-Critic discipline (DR-1) — heavier than Minimal warrants. Heavy mode would over-fit (no regulated/audited deliverables, no comprehensive upfront vault needed).

## Adoption-time scan (code-derived facts)

- **Stack**: Python 3.10+ (audit tools); markdown-as-code (skills, agents, templates)
- **Distribution**: pip-installable package (`tools/`) + cp-shipped skills/agents/templates (per INSTALL.md)
- **Code corpus**: 79 source files, 1,348 graph nodes, 1,642 edges, 64 communities (graphify code scan at adoption)
- **Vault corpus**: substantial — `lessons-learned.md` (~121KB), `shippability.md` (~45KB), `critic-calibration-log.md` (~38KB), `methodology-changelog.md` (~215KB)
- **Slices shipped**: 18 (all archived; no active slice at adoption time)
- **ADRs accepted**: 16
- **Open risks**: 2 (R-1, R-2 — both `/diagnose`-related, low-priority)

## /diagnose: skipped

**Reason for skip**: this is a self-aware codebase — the maintainer is the methodology author, and every component, contract, and decision is already documented in the existing vault. A forensic pass would compete with vault documentation rather than complement it, and the 564k-word corpus makes semantic extraction expensive. The `/adopt` rule is "trust code over docs" because docs lie in typical brownfield; here, the docs *are* the code (skill markdown is the executable contract), and they're maintained under drift-check discipline (CAD-1, PMI-1, BC-1). The trust hierarchy collapses cleanly.

**Consequence**: risk register entries (Step 6 of `/adopt`) derive from the existing `risk-register.md` (R-1, R-2 already captured firsthand at slice-001/slice-002). No backlog.md generated; new slice candidates emerge from `methodology-changelog.md` pending discipline refinements + `critic-calibration-log.md` pending categories.

## Historical ADRs: not retro-authored

The 16 existing ADRs (ADR-001 through ADR-016) were authored firsthand at the slice that produced each decision. The `/adopt` rule is "firsthand-only or skip" — there is no firsthand context unavailable at slice-time that adoption could now retroactively capture. Skip.

## What this adoption produced

- `architecture/triage.md` (this file)
- `architecture/concept.md` — concept reverse-engineered from code reality
- `CLAUDE.md` (project root) — brownfield-aware pipeline rules

## What this adoption did NOT touch

- `architecture/risk-register.md` — already current (R-1, R-2 open)
- `architecture/decisions/ADR-*.md` — 16 ADRs preserved as authored
- `architecture/slices/_index.md` + `archive/` — 18-slice history preserved
- `architecture/lessons-learned.md` — preserved
- `architecture/shippability.md` — preserved
- `architecture/critic-calibration-log.md` — preserved
- `architecture/build-checks.md` — preserved
- All source code under `skills/`, `agents/`, `tools/`, `templates/`, `tests/` — analysis-only adoption, no code edits

## Next step

No queued slice candidate at adoption time. When new work emerges (next discipline refinement, next Critic-calibration finding, next user-reported pipeline pain point), run `/slice` to define slice-019.

If any of R-1 / R-2 escalates from low-impact to user-blocking, run `/risk-spike` instead.
