---
id: ADR-035
title: Rename the /status skill to /pulse to resolve the Claude Code built-in /status collision; no backward-compat alias
date: 2026-05-17
slice: slice-035-rename-status-skill-to-pulse
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-035: Rename /status skill to /pulse

## Context

The AI SDLC pipeline ships a skill `name: status` (`plugin.yaml:65`, `skills/status/SKILL.md:2`) whose trigger `/status` collides with Claude Code's built-in `/status` command. The collision makes the skill ambiguously invocable for users. The skill's own documentation already calls it "Project Pulse / Macro State" (`SKILL.md:8`) and declares `pulse` as a trigger phrase — so a rename to `pulse` is a near-zero-semantic-drift change rather than new vocabulary.

The rename crosses several parity-audited surfaces (PMI-1 plugin manifest, INST-1 install canon, CSP-1 cross-spec parity) plus the methodology test suite, so the decision and its boundaries need recording.

## Options considered

1. **Rename `/status` → `/pulse`, no alias** — pros: resolves collision cleanly, reuses the skill's existing conceptual name, single source of truth. Cons: any external muscle-memory / docs referencing `/status` must be updated (in-repo only; controlled).
2. **Keep `/status`, add a `/pulse` alias** — pros: backward compatible. Cons: the `/status` alias *re-introduces the exact collision* being fixed; defeats the purpose.
3. **Rename to a different name (`/orient`, `/macro`)** — pros: also resolves collision. Cons: invents new vocabulary; higher doc churn; the skill already self-identifies as "pulse".
4. **Do nothing, document the collision** — pros: zero work. Cons: skill stays unreliably invocable; not acceptable.

## Decision

Adopt Option 1: rename the skill to `pulse` with **no backward-compat `/status` alias**. Propagate the rename atomically across `plugin.yaml` (incl. `version: 0.49.0`), `tools/install_audit.py` canonical list, the referencing test modules (Bucket-A executable path binds + Bucket-B prose per design.md taxonomy), consumer-reference prose, vault docs, and cross-docs.

Mint methodology rule **SRCD-1** (Skill-Rename Collision-resolution Discipline) at `methodology-changelog.md` `## v0.49.0` with the mandated entry format and the canonical anti-silent-weakening phrase *"user-invocable skill names MUST NOT collide with Claude Code built-in command names"*, forward-synced to the installed copy and pinned by a new `test_v_0_49_0_srcd_1_entry_present_in_repo_and_installed` (mirrors the `test_v_0_48_0_tffl_1` template).

The version move is the **4-part PMI-1 atomic bump** `0.48.0`→`0.49.0` (per the meta-Critic B-add-1; revision-2's "atomic triple" wording was wrong): `VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` (installed) + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`, all in lockstep — the pattern every prior entry documents (`methodology-changelog.md:89,105,121,139,155,179`) and the slice-006 DEVIATION-2 / slice-007-B1 recurrence class.

Per project CLAUDE.md RPCD-1/SCPD-1 ("every new audit rule MUST propagate its consumer references into the shippability catalog"), SRCD-1 gets a new `architecture/shippability.md` row pinning `test_v_0_49_0_srcd_1_entry_present_in_repo_and_installed` as its durable guard, mirroring the slice-033 EOL-DRIFT-1 (#33) / slice-034 TFFL-1 (#34) precedent. SRCD-1 is NOT judged catalog-exempt: although it is a naming-policy rule, its entry-pin test is a concrete regression artifact of exactly the kind rows #33/#34 catalog, so consistency with precedent governs.

**Frozen-as-history exclusions** (NOT rewritten — rewriting falsifies a historical record):
- `tests/methodology/fixtures/archive_backtest_corpus/slice-004…/design.md`, `…/slice-007…/design.md` — verbatim backtest baseline per [[ADR-030-archive-backtest-verbatim-tracked-corpus]]; rewriting corrupts the backtest.
- `architecture/lessons-learned.md:414` — historical reflection text recording what a past slice did when `/status` was the live name; the lesson's truth is anchored to the name at that time. Same reasoning class as the ADR-030 exclusion.

**Not in scope because no reference exists** (B3): `agents/critique.md` contains no `/status` *skill* reference (its only `status` at L194 is the FBCD-1/PTFCD-1 TF-1-row-status term-of-art) — therefore CAD-1 is N/A this slice; the revision-1 `agents/critique.md:194` citation was a false (unverified) propagation and is retracted.

## Consequences

- Users invoke `/pulse`; `/status` resolves only to Claude Code's built-in (collision gone).
- PMI-1, INST-1, CSP-1 and the methodology suite must be green at slice finish — they are the regression guard for an incomplete rename.
- The verbatim backtest corpus retains `/status` strings legitimately; future readers must not "fix" them (cross-referenced from this ADR and design.md).
- `/pulse` remains an out-of-loop peer skill (no `## Pipeline position` block, not in the PCA-1 chain) — unchanged from `/status`.
- Methodology version bumps; downstream consumers that name the skill in prose now say `/pulse`.

## Reversibility

**Cheap.** The rename is a mechanical identifier change; reverting is the same operation in reverse with no data migration, no contract consumers, and no irreversible state. The no-alias sub-decision is equally cheap to revisit (an alias could be added later if ever justified), though doing so would re-open the collision and is not anticipated.
