---
type: concept
adoption-date: 2026-05-13
fidelity: code-derived
---

# Concept (brownfield, reverse-engineered from code at adoption)

**Date adopted**: 2026-05-13
**Mode**: Standard
**Codebase maturity**: Production (v0.32.0, distributed as Claude Code plugin)
**Forensic analysis (/diagnose)**: skipped — codebase is self-aware; maintainer authored every component; vault already documents architecture more thoroughly than `/diagnose` would (see `triage.md` for rationale)

## What it does

AI SDLC is a **spec-driven SDLC pipeline for AI implementers** distributed as a Claude Code plugin. It hybridizes phase-driven rigor (for knowable domains: compliance, regulated, large teams) with slice-driven iteration (for unknowable domains: product discovery, consumer apps), and adds two AI personas — a **Builder** that produces and a **Critic** that adversarially reviews along 9 fixed dimensions, with a **meta-Critic** (per DR-1) reviewing the first Critic per slice.

Concretely, it ships:

- **24 skills** as drop-in `~/.claude/skills/<name>/SKILL.md` markdown — invoked via `/<skill-name>` in Claude Code (e.g., `/triage`, `/slice`, `/design-slice`, `/critique`, `/build-slice`, `/validate-slice`, `/reflect`)
- **5 named subagents** as `~/.claude/agents/<name>.md` — Critic (`critique`), meta-Critic (`critique-review`), cross-slice meta-Critic (`critic-calibrate`), forensic narrator (`diagnose-narrator`), and external-tech recon (`field-recon`)
- **15 executable audit tools** as `tools/<name>.py` (pip-installable package `ai-sdlc-tools`) — every load-bearing methodology rule (BC-1, RR-1, VAL-1, PMI-1, CAD-1, DR-1, ETC-1, TF-1, WS-1, WIRE-1, INST-1, CSP-1, SUP-1, LINT-MOCK-1/2/3, TRI-1) has a runnable audit so the methodology isn't enforced by prose alone
- **Three modes** (Minimal / Standard / Heavy) picked by `/triage` (greenfield) or `/adopt` (brownfield) at project open

## Actors (inferred from code + skill invocation surface)

- **Pipeline user** (developer using Claude Code): drives the pipeline via slash commands; uses `/triage` or `/adopt` to open a project, then `/slice → /design-slice → /critique → /build-slice → /validate-slice → /reflect` per slice
- **Claude orchestrator** (main thread): reads `SKILL.md` prose and executes steps; spawns named subagents (`critique`, `critique-review`, etc.) when skills dispatch
- **Subagents** (Critic, meta-Critic, etc.): adversarial reviewers spawned by skills; produce structured findings (blockers / majors / minors) and verdicts that the user triages
- **Plugin installer** (`INSTALL.md` execution): one-time per-machine setup that copies skills/agents/templates into `~/.claude/` and pip-installs `ai-sdlc-tools`
- **Audit tooling** (CI / pre-commit / on-demand): `tools/*.py` modules that lint vault and code for drift (CAD-1 catches in-repo↔installed Critic drift; PMI-1 catches manifest↔filesystem drift; BC-1 catches build-check rule drift; etc.)

## Constraints (observed)

- **Stack**: Python 3.10+ (`pyproject.toml`); pyyaml, tree-sitter + 3 grammars (typescript, go, +ts grammar) for AST-driven lint
- **Distribution**: pip-installable Python package (`tools/`, source-independent install) + filesystem copy for skills/agents/templates (Claude Code reads these directly from `~/.claude/`)
- **Shared interpreter**: pipeline assumes a shared `~/.claude/.venv` with `graphify` installed (per `~/.claude/CLAUDE.md` convention); calls Python via absolute path, never `activate`
- **Single maintainer**: Shubhendu Shubham (solo; team-mode rationale would shift this to Heavy)
- **Self-hosted dogfooding**: the pipeline is developed using itself — slice-001 through slice-018 are all real slices that shipped under the pipeline being defined. This creates a tight self-application discipline: any methodology rule must be exercisable on the codebase that defines it (manifested in CAD-1 bidirectional content equality + PMI-1 manifest-filesystem equality)

## Domain-specific discipline (load-bearing)

Beyond the generic pipeline structure, this codebase establishes several disciplines that are unusual and worth understanding before editing:

- **Builder ↔ Critic ↔ meta-Critic separation**: `/critique` spawns an adversarial Critic agent; `/critique-review` spawns a meta-Critic that reviews the first Critic for false positives/negatives + severity miscalibrations. The user owns triage at Step 4.5 (TRI-1). Critic verdicts can be OVERRIDDEN or DEFERRED with documented rationale; nothing is silent.
- **Critic calibration as recurring meta-skill**: `/critic-calibrate` mines `Missed by Critic` entries across recent reflections (per CAL-1 cadence enforcement in `/pulse`) and *proposes* additions to the Critic agent prompt. Human-reviewed, never auto-applied.
- **Vault drift as commit-blocker**: ADRs are append-only (supersede, never edit in place per SUP-1); `/drift-check` runs vault-vs-code audits before commit. The "Thin Vault" principle (`principles.md`) holds: only what code can't carry lives in the vault (decisions, risks, slice memory). Components/contracts/schemas live in code; Heavy mode regenerates code-derived views on-demand via `/sync`.
- **Per-slice continuous validation**: `/validate-slice` runs VAL-1 (imports allowlist), WS-1 (walking skeleton), ETC-1 (exploratory charter) per slice on real environments, not mocks. "Tests pass" is not a substitute for `/validate-slice` (shippability catalog regression checks live there).

## What docs say vs. what code does

No discrepancies observed during adoption scan. README, principles.md, pipeline.md, and the skill SKILL.md files describe the system as built — the codebase has been maintained under drift-check discipline (CAD-1 bidirectional content-equality audit between in-repo and installed Critic agent, PMI-1 manifest-filesystem equality audit, BC-1 build-check rule audit) that catches doc-vs-code drift programmatically. The usual brownfield doc-lies-code-tells-truth gap is collapsed here because the docs *are* the load-bearing contracts (skill prose is executable when Claude reads it).

## First slice candidate

None queued at adoption time. Slice-018 (cleanup-slice-016-rpcd-1-sibling-test-scoping-flaw) shipped 2026-05-13; no active slice immediately follows. Next slice will emerge from:

1. New discipline refinement surfaced by `/critic-calibrate` (cross-slice Missed-by-Critic pattern mining)
2. User-reported pipeline pain point
3. R-1 or R-2 escalation (currently low-impact / open)

When the trigger fires, run `/slice` to scope slice-019.
