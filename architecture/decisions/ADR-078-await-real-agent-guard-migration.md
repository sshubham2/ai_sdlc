---
id: ADR-078
title: Enforce the await-the-real-agent guard via a canonical-literal pin test across the three spawn-skills, migrating it out of the global CLAUDE.md stopgap
date: 2026-05-30
slice: slice-086-harden-agent-spawn-skills-await-real-output
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-078: Await-the-real-agent guard — enforcement mechanism + stopgap migration

## Context

R-25 (discovered slice-085, the top open risk at score 4) is a demonstrated, load-bearing gap: the three agent-spawning skills (`/critique`, `/critique-review`, `/code-review`) tell the main thread to "write the agent's output to `<file>`" but never warn that the `Agent` tool can return an **asynchronous acknowledgment** ("Async agent launched…") rather than the finished deliverable, and never forbid self-authoring a placeholder while the agent runs. In slice-085 the main thread wrote `critique.md` from its own self-review before the real Critic returned; the real agent later refuted a fabricated "B2" finding. This silently defeats the Builder↔Critic separation those skills exist to provide.

A stopgap guard was added 2026-05-30 as the `# Spawned-agent output` section of the global `~/.claude/CLAUDE.md`. A global CLAUDE.md directive is not pipeline-enforced, does not travel with the skills, and is not drift-guarded — it is a stopgap, not the home for a load-bearing review-integrity guard. This slice moves the guard into the in-repo skill contracts and decides how to enforce it.

Two enforcement sub-decisions must be locked:
1. **What enforces the guard's presence?** The three skills are NOT uniformly covered by an in-repo↔installed content-equality drift test (Builder-verified against disk at /critique, B1/B2): only `code-review` has one (`tests/methodology/test_code_review_skill_drift.py`); `critique` and `critique-review` have **none** (there is no `test_critique_skill_drift.py` on disk, despite `critique` being named in CLAUDE.md:42's OSDG-1 set — a pre-existing inventory drift logged as the follow-up `reconcile-osdg-1-inventory-claude-md-L42`). Critically, even where a drift test DOES exist, it asserts whole-file content-equality (in-repo == installed) — it does **not** assert the guard *exists*; a guard dropped from BOTH copies passes drift. So no existing mechanism enforces the guard's presence.
2. **When is the stopgap removed?** The global directive is the only protection until the skill guard ships.

## Options considered

1. **Extend full OSDG-1 content-equality to the skills lacking it (`critique`, `critique-review`) + rely on drift tests to carry the guard** — pros: reuses existing machinery, gives all three the same in-repo↔installed sync protection. Cons (decisive): drift tests assert whole-file content-equality (in-repo == installed); they do NOT assert the guard *exists* — a guard dropped from BOTH repo and installed copies passes drift regardless of how many skills are OSDG-1-covered. So this option does not actually enforce R-25's obligation. Additionally, extending OSDG-1 to two more skills is a larger, R-13-class change (per-skill drift-test modules + install-audit wiring) — scope creep for an R-25 fix.
2. **A single canonical-literal structural-pin test across all three skills (chosen)** — one invariant guard heading literal authored verbatim into the spawn→write seam of all three SKILL.md files; one test asserts the literal is present in each. Pros: directly asserts the guard EXISTS (the actual R-25 obligation), covers all three uniformly including the un-OSDG-1-guarded `critique-review`, follows the proven SOAD-1 prose-pin precedent. Cons: pins a chosen literal (must pick a unique-to-invocation literal per the slice-075/085 lesson to avoid a narration-collision false-negative).
3. **Leave the guard in global CLAUDE.md only** — rejected: not pipeline-enforced, not drift-guarded, does not travel with the skills; this is exactly the stopgap R-25 calls out for migration.

## Decision

Adopt Option 2. Author one **canonical guard literal** — the bold heading sentence `**Await the real agent — never fabricate its output.**` plus a four-obligation block — VERBATIM at the spawn→write seam (Step 2 → Step 3) of `skills/critique/SKILL.md`, `skills/critique-review/SKILL.md`, and `skills/code-review/SKILL.md`. A new structural-pin test (`tests/methodology/test_r25_await_real_agent_guard.py`, modeled on `test_soad1_structured_options_ask_rule.py`) asserts the heading literal is present once in each of the three in-repo SKILL.md files. Re-install all three edited skills so the one existing drift test (`code-review`) stays green and the `critique` + `critique-review` installed mirrors match (the latter two have no drift test — the pin test is their sole guard-literal enforcement). Add a shippability row for the new test (RPCD-1 / SCPD-1).

Full OSDG-1 content-equality extension to `critique-review` is explicitly deferred (out of scope; queued as `extend-osdg-1-to-critique-review`).

## Consequences

- All three spawn-skills carry a uniform, drift-resistant guard; the R-25 review-integrity gap is closed at the in-repo skill-contract layer where it belongs.
- The pin test asserts the guard's *existence* (which drift tests cannot), making it the load-bearing enforcement; drift tests remain a complementary in-repo↔installed sync check.
- **Ordering is load-bearing**: the global `# Spawned-agent output` stopgap is the only protection until the skill guard is installed, so its removal MUST be the closing action — performed only after the guard literal is present in all three SKILL.md files, the pin test PASSES, and the installed mirrors are synced. Removing it earlier opens an unprotected window. The removal is recorded in `reflection.md` so the stopgap→pipeline migration is auditable.
- `critique-review` gains the guard-literal pin but not full content-equality coverage — a known, documented residual tracked by the queued `extend-osdg-1-to-critique-review` candidate.
- MEPD-1: this slice does not mint a new RULE-ID and adds no methodology-changelog rule — the guard is skill-contract content, enforced by a structural-pin test. The shippability row + this ADR + the reflection suffice (consistent with the slice-077/082/084/085 EXCLUDE precedent for risk-narrowing/closing fix-slices). No VERSION bump.

## Reversibility

Cheap. The guard is prose in three SKILL.md files + one presence test + one shippability row. Reverting is a delete of the test row and the prose blocks (and, if ever desired, restoring the global stopgap). No data, contracts, or consumers depend on it. The chosen literal can be re-tuned by editing the canonical text in all three surfaces + the test's expected literal in one place.
