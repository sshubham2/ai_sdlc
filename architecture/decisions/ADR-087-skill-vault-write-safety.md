---
id: ADR-087
title: Harden skill-driven vault writes via a wrapper CLI (vault_edit append) for the append class plus a fail-closed lexical SKILL.md audit (SVW-1), deferring the read-modify-write/lost-update class to the flip slice
date: 2026-06-01
slice: slice-095-harden-skill-driven-vault-writes
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-087: Harden skill-driven vault writes (SVW-1)

## Context

R-32 (concurrent-write lost-update / atomic-rename-EPERM corruption on a shared mutable vault) has two writer sub-classes:

1. **Python-tool writers** — `tools/*.py` that write vault files directly. Closed by slice-094 (route through `_vault_write.safe_write_text`/`safe_append_text` + the VWS-1 AST audit, [[ADR-086]]).
2. **Skill-driven writers** — Claude editing vault files via the harness `Write`/`Edit` tools per SKILL.md prose. These never touch `_vault_write` and are invisible to VWS-1's Python-only AST scan.

This ADR addresses sub-class 2. It only matters once the vault is shared + untracked (the slice-094 flip): until then git + PCR mediate vault-file collisions loudly. R-32 is the load-bearing blocker for that flip — both writer sub-classes must be closed before the vault can leave git's conflict-resolution safety net.

Slice-093 already shipped the primitive (`safe_append_text`: `O_APPEND` under a sidecar `.lock` — non-clobbering, the append-class structural replacement for PCR-on-vault-files). Its docstring already names the skill-path append targets (`risk-register.md`, `_index.md`, ADRs, the PCR log). What is missing for the skill path: (a) a channel Claude can actually invoke (the `Write`/`Edit` tools cannot take a lock), and (b) a gate that stops a future SKILL.md edit from silently re-introducing an unsafe raw vault write.

A grounding scan confirmed **zero** `skills/*/SKILL.md` route through any safe primitive today — the entire skill-driven sub-class is unrouted. The genuinely-concurrent mutators (fire at slice-end under the parallel-slice model) are `/reflect` and `/archive`; project-open skills (`/triage`, `/discover`, `/risk-spike`) write the risk-register single-shot and are not a parallel concurrency hazard.

A second, deeper fact shaped the decision: the skill-driven writes split into an **append class** (new R-NN entries, lessons bullets, shippability rows, changelog sections, ADR files — non-clobbering) and a **read-modify-write / rewrite class** (`_index.md` recent-10 table; in-place risk-status flips mitigating→retired). A per-call wrapper can make the append class fully safe, but it **cannot** close the rewrite class's lost-update window — that needs a lock held across Claude's read+edit+write, which an LLM-driven flow cannot span.

## Options considered

1. **Wrapper CLI + fail-closed static audit** (chosen). Ship `tools/vault_edit.py append` over `safe_append_text` for the append class; rewrite the append-class skill prose to call it; ship `tools/skill_vault_write_safety_audit.py` (SVW-1) that fail-closed-detects any SKILL.md prose prescribing an unsafe raw mutation of a shared-aggregate vault file. Defer the rewrite class (exempt-marked, visible residual) to the flip slice.
   - **Pros**: gives Claude a real safe channel for LLM-authored shared-vault content (per-slice-isolation + commit-time PCR cannot — the content is generated, not mechanical); the audit keeps the prose honest so drift can't silently re-open the hole; mirrors slice-094's VWS-1 INCLUDE shape (sibling consistency); honest about what it does/doesn't close.
   - **Cons**: the audit is lexical prose-detection (false-positive risk → APED-1 obligation); runtime obedience is not enforced (static-prose scope); two new PMI-1 tools (doubled count-fan-out).
2. **Discipline + audit only (no wrapper)**. No new CLI; route LLM-authored shared content through per-slice-isolated files merged by the existing PCR at commit-time; the audit enforces "no direct skill mutation of shared files."
   - **Pros**: lighter tool surface; leans on the existing PCR architecture.
   - **Cons**: no safe channel for an in-step LLM-authored append (e.g. a `/reflect` risk entry) — forces a much larger skill-flow rewrite (every append becomes write-to-temp + register-for-merge); PCR's merge-time path does not cover the write-time append window.
3. **Close the rewrite class now too** (held vault-lease / serialize `/reflect`+`/archive`) so 094+095 fully RETIRE R-32.
   - **Pros**: R-32 fully retired in one pair of slices, matching the brief as originally written.
   - **Cons**: a held cross-step lease over an LLM read-modify-write is a substantial mechanism; pushes slice-095 past 1 day / forces a split; the rewrite class is not-yet-live (only post-flip), so the mechanism naturally belongs with the flip that removes git mediation — building it now is speculative.

## Decision

Adopt **Option 1**. Ship a `vault_edit append`-only wrapper CLI over `safe_append_text` and route the append-class skill prose (`/reflect`, `/reduce`, `/archive` append sites) through it. Ship the fail-closed lexical **SVW-1** audit (`tools/skill_vault_write_safety_audit.py`) over `skills/*/SKILL.md`, scoped to the shared-aggregate vault file set, with an inline `<!-- vault-write-safe: <reason> -->` exemption marker for the deferred rewrite class and the project-open single-shot writers. Wire the audit into `/build-slice` Step 6 + `/validate-slice` + `shippability.md`. Defer the read-modify-write/lost-update class to the flip slice.

The wrapper exposes **`append` only** — not `rewrite` — because `safe_write_text` (torn-write-safe) does not close the lost-update window for read-modify-write, and offering it would invite unsafe use.

## Consequences

- **R-32 narrows, not retires.** 094 (Python writers) + 095 (skill appends) close the write/append axis. A skill-driven read-modify-write/lost-update residual remains (`_index.md` recent-10; in-place risk-status flips), explicitly exempt-marked and owned by the flip slice (which must serialize `/reflect`+`/archive` rewrites as part of removing git mediation). At `/reflect`, R-32 stays `mitigating` with the append sub-class closed-with-evidence. This **amends slice-095's mission-brief AC4/Intent** ("retire" → "narrow") per the user's design-time decision.
- **Two new PMI-1 tools** (`vault_edit.py`, `skill_vault_write_safety_audit.py`) → MEPD-1 INCLUDE: methodology-changelog `## v0.80.0` entry, VERSION bump, PMI-1 atomic bump (plugin.yaml + install_audit.py + INSTALL.md counts), shippability row, cp1252-parametrize-list + inventory-pin enumeration of both tools. Doubled count-fan-out.
- **The audit is static.** It proves the prose prescribes the safe channel; it cannot prove Claude obeys at runtime (the R-2 class). Documented as a known limitation, acceptable under the cooperative-not-adversarial model ([[ADR-067]]).
- **Parallel-slice-094 coordination.** 095 takes ADR-087 (094 holds ADR-086) and plans v0.80.0 (094 plans v0.79.0) to avoid merge collisions; RULE-ID SVW-1 is disjoint from 094's VWS-1. Shared coordination files reconcile via PCR / `git merge master` before pre-finish.
- **Future flexibility.** The wrapper can grow a `rewrite` (lease-backed) subcommand at the flip without breaking the `append` contract; the SVW-1 audit's shared-file set + verb lexicon are module constants the flip slice extends additively.

## Reversibility

**Cheap.** Both tools are leaf CLIs with exit-code-only contracts; the skill-prose edits are additive (swap a raw-write directive for a `vault_edit append` call + keep an exemption marker). Reverting = delete the two tools + their tests, revert the routed prose to raw `Write`/`Edit`, drop the SVW-1 changelog/shippability/PMI entries. No data migration, no schema, no consumer contract beyond the gate-roster prose. The `safe_append_text` primitive it wraps is unchanged (slice-093).
