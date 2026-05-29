---
id: ADR-075
title: Mint PCR-2b (HARD/MIXED gate-on-hand-resolve) + TRI-RESOLVE-1 user-triage gate; Critic mechanism = the code-review agent on the resolved merge diff
date: 2026-05-29
slice: slice-083-add-pcr-2b-hard-class-conflict-resolution
reversibility: expensive
status: accepted
supersedes: null
---

# ADR-075: Mint PCR-2b — HARD/MIXED conflict resolution via gate-on-hand-resolve + TRI-RESOLVE-1

## Context

[[ADR-069]] minted PCR-1 and declared a 5-class conflict taxonomy (SOFT / VAULT_CLAIM / HARD / MIXED / UNKNOWN) at `/commit-slice --merge` sub-step 2.5. PCR-1 (slice-076) shipped the SOFT auto-regen path; slice-082 hardened it ([[ADR-074]]). PCR-2a (slice-078 / [[ADR-071]]) shipped the VAULT_CLAIM timestamp-winner path. Two classes remain bare-STOP-only:

- **HARD** — any U-file is a source/ADR/SKILL.md/`_index.md`/`methodology-changelog.md` file.
- **MIXED** — at least one SOFT U-file coexists with a non-SOFT U-file (treated as HARD for atomicity).

Today `resolve_soft_conflict` returns `action="STOP", conflict_class=HARD|MIXED` and `skills/commit-slice/SKILL.md` falls straight through to the PSQ-3 SOAD-1 3-option ask — option (b) tells the user to resolve markers and run `git rebase --continue` **outside the skill, with no Critic adjudication** on the contested resolution. ADR-069's taxonomy reserved the HARD/MIXED row for "PCR-2b": "Full Critic stack: `/critique` reviews proposed resolution; `/critique-review` meta-reviews; TRI-RESOLVE-1 user triage; only on CLEAN apply" — "**FULL stack (Critic + meta-Critic + user)**". That work was nominally assigned to "slice-079" in ADR-069/ADR-071, but slice-079 became a code-Critic cleanup bundle; PCR-2b was never built. This ADR ships it.

Two scope decisions were locked at `/slice` and `/design-slice` (2026-05-29, structured-options asks):

1. **Resolution mechanism = gate-the-human-resolved-diff** (NOT auto-propose). The resolution itself is produced by the user (or by Claude at the user's instruction); PCR-2b's job is to *gate* that proposed resolution through a Critic stack + user triage before `git rebase --continue`. Auto-proposing a HARD merge (3-way / LLM driver) for the Critic to review is explicitly rejected (it is ADR-069 Option 2, rejected there for silent-regression risk).
2. **R-23 (clock-skew) / R-24 (truncated-baseline) remediation = out-of-scope / emergent-only.** PCR-2b is the *venue* both risks name for remediation, but no dedicated detection code is added; both stay OPEN with their own SMALL queue candidates.

A third decision (the Critic-mechanism shape) was locked at `/design-slice`: see Options below.

## Options considered

### A. Resolution mechanism (locked at /slice — gate-on-hand-resolve)
1. **Gate the human-resolved diff** *(chosen)* — user/Claude resolves markers; PCR-2b runs the Critic stack + TRI-RESOLVE-1 on the resolved working-tree diff before continue.
   - Pros: bounded (≤1 day); no silent semantic regression (a human authored the resolution; the Critic + user only adjudicate it); faithful to ADR-069's "Critic reviews proposed resolution; only on CLEAN apply" wording; fail-closed at every leg.
   - Cons: still requires a human in the loop per HARD conflict (acceptable — HARD conflicts are low-frequency high-judgment by the ADR-069 taxonomy rationale).
2. **Auto-propose + adjudicate** — PCR-2b generates a merge resolution for the Critic to review.
   - Cons: this is ADR-069 Option 2 (rejected); large surface, high silent-regression risk, ≥multi-slice. Rejected.

### B. Critic mechanism (locked at /design-slice as two-pass named agents; REVISED at TRI-1 to the `code-review` agent — M-add-2)
1. **The `code-review` agent (single pass) on the resolved diff** *(chosen — TRI-1 M-add-2 decision, 2026-05-29)* — spawn `subagent_type: "code-review"` (`agents/code-review.md`, slice-060 / [[ADR-059]]) on the resolved merge diff. The agent is ALREADY diff-calibrated (its 9 dimensions are the `/critique` dimensions reframed for a code/content diff), exists, and reviews exactly a code/content diff. Inputs: `git diff --cached` of the U-file set + the `--diagnose` JSON + both rebase stages. Output captured inline; no design-folder audit; TRI-RESOLVE-1 is the gate; any blocker finding → BLOCKED → STOP.
   - Pros: actually buildable (the named `critique`/`critique-review` agents fail-stop on missing slice artifacts — M-add-2); no new agent file / no CAD-1 / PMI-1 / INST-1 surface; the artifact (a diff) matches the agent's calibration.
   - Cons: single adversarial pass — the meta-Critic leg is dropped; recovered by the TRI-RESOLVE-1 user gate (the actual apply authority) + the standing DR-1 discipline. This was the /design-slice *non-chosen* option B; promoted at TRI-1 once option-1-as-stated proved unbuildable.
2. **Two-pass named `critique` + `critique-review` subagents on the diff** *(chosen at /design-slice; REJECTED at TRI-1 — M-add-2)* — would reuse the named subagents with a custom merge-resolution preamble.
   - Why rejected: `agents/critique.md` + `agents/critique-review.md` front-matter demand slice artifacts ("expects slice artifacts as input… if missing, say so and stop") and bake the design-oriented dimensions (TF-1/PMI-1/MEPD-1) into the system prompt — a user preamble cannot override that, so the agents fail-stop on a merge diff. The contradiction the B1 finding flagged at the skill layer simply moves to the agent layer. Unbuildable as stated.
3. **New dedicated diff-calibrated two-pass agent** *(considered at TRI-1; not chosen)* — author a `merge-resolution-critic` (+ meta) agent.
   - Why not: preserves the true two-pass but expands scope (new agent file + CAD-1 drift guard + PMI-1/INST-1 inventory + agent-count bump) — tips the slice past 1 day; deferred as a future option if single-pass proves insufficient.
4. **Inline SKILL.md-prose review (no agent)** *(considered; not chosen)* — tightest scope but sacrifices two-persona separation; weakest.

### C. Where the Critic + user orchestration lives
1. **SKILL.md prose drives the Critic agents + TRI-RESOLVE-1; Python resolver provides only the structural pre/post hooks** *(chosen)* — Python cannot spawn skill agents, so the resolver ships a `--verify-resolution` structural preflight (no remaining conflict markers) + `resolve_hard_conflict` STOP-dispatch + `--record-hard-resolution` audit-append; the Critic-pass + TRI-RESOLVE-1 gate are prose in `skills/commit-slice/SKILL.md` sub-step 2.5, pinned by skill-drift + prose-structural tests (mirrors PCR-2a's L185/L192 pin discipline).
   - Pros: matches the actual capability boundary (agents are skill-spawned); keeps the testable Python surface focused (marker-scan, dispatch, audit format); OSDG-1 drift-pins protect the prose.
   - Cons: the orchestration logic is prose, not unit-testable as code — mitigated by skill-prose structural pins + the cooperative threat model.

## Decision

**Mint PCR-2b** as the HARD + MIXED resolution sub-mechanism on the PCR-N family axis, and **TRI-RESOLVE-1** as the user-owned triage gate (sibling to TRI-1), via the **gate-on-hand-resolve** flow:

At `/commit-slice --merge` sub-step 2.5, when the resolver classifies HARD or MIXED, the skill (instead of the bare SOAD-1 fall-through):
1. surfaces the existing full-detail STOP diagnostic;
2. lets the user — or Claude at the user's instruction — resolve the conflict markers in the working tree;
3. runs `python -m tools.parallel_conflict_resolver --verify-resolution` (STOP if any path is still unmerged OR a line-anchored `<<<<<<<`/`>>>>>>>` opener/closer or `|||||||` diff3 base-marker survives in the staged resolution — keyed on the openers, deliberately NOT `=======`, which false-STOPs on Markdown setext H1 underlines per the B2/M-add-1 fix);
4. spawns the **`code-review` agent** (`subagent_type: "code-review"`, single pass) against the *resolved merge diff* + conflict context (the named `critique`/`critique-review` agents were rejected at TRI-1 — M-add-2 — for fail-stopping on missing slice artifacts);
5. presents **TRI-RESOLVE-1** — a SOAD-1 structured-options user-triage gate (apply / re-resolve / abort) making the user the sole apply authority;
6. **only on explicit user apply with a non-blocking Critic verdict** → `git rebase --continue` + `--record-hard-resolution` audit append. Any other outcome (verify STOP, Critic BLOCKED, non-apply triage, unanswered) → STOP, no continue.

Using the `code-review` agent against the resolved diff (rather than the `/critique` skills against a design) is a **refinement** of ADR-069's "/critique + /critique-review reviews proposed resolution" wording — ADR-069 used those names loosely for "the full Critic stack" before the resolution-artifact shape (a merge diff, not a slice design) was concrete, and before the meta-Critic established (M-add-2) that the named critique agents fail-stop on a missing `design.md`. The `code-review` agent is the diff-calibrated member of the Critic family (slice-060) and is the correct reviewer for a merge-resolution diff. This ADR does not supersede ADR-069 and **does not edit it**: ADR-069 is left byte-unchanged (its HARD/MIXED "Shipped in" cells still read "slice-077 (PCR-2)"); ADR-075 supersedes-via-refinement the HARD/MIXED resolution-path cell, and readers follow the forward link from ADR-069 to here. (m1 fix — "annotate, not edit" was self-contradictory for an append-only file; nothing in ADR-069 is rewritten.)

The Python resolver gains `resolve_hard_conflict` (thin STOP-dispatch, mirrors `resolve_vault_claim_conflict`), `_verify_resolution_clean` (marker scan) behind `--verify-resolution`, `_format_hard_audit_entry` + an `_append_audit_log` HARD dispatch leg behind `--record-hard-resolution`. The audit section heading is `## Hard-conflict resolution - <ISO-8601 UTC>` (uniform hyphen-space separator; section-type distinguished by the prefix word `Hard-conflict`, per PCR-2a ADR-071 discipline).

## Consequences

- **`skills/commit-slice/SKILL.md`**: sub-step 2.5 STOP handling grows the HARD/MIXED gate branch; the existing SOAD-1 3-option ask is preserved as the bootstrap-fallback and the abort/cancel surface. OSDG-1 / mini-CAD byte-equality: installed copy forward-synced.
- **`tools/parallel_conflict_resolver.py`**: HARD/MIXED route through `resolve_hard_conflict`; two new CLI modes; new audit section-type. The `resolve_soft_conflict` SOFT + VAULT_CLAIM + UNKNOWN behavior is byte-unchanged.
- **Audit log** `architecture/parallel-conflict-resolution-log.md` now carries three section-types (`Soft-conflict` / `Vault-claim` / `Hard-conflict`), uniform separator.
- **`methodology-changelog.md`**: v0.77.0 entry mints PCR-2b + TRI-RESOLVE-1 with entry-pins; 5-part PMI-1 atomic bump 0.76.0 → 0.77.0 + forward-sync (MCFS-1 / AVFS-1 / OSDG-1 commit-slice / TVFS-1 / PVFS-1).
- **PCR-N taxonomy is now complete** — every non-UNKNOWN class has a resolution path (SOFT auto-regen / VAULT_CLAIM timestamp-winner / HARD+MIXED gate-on-hand-resolve). UNKNOWN remains the deliberate fail-closed escape.
- **M4 fix — HARD is NOT uniformly low-frequency**: `architecture/slices/_index.md` conflicts on essentially every parallel merge (every slice regenerates it via `/archive`'s Haiku-dispatch; it can never be SOFT per ADR-069:72) and methodology-minting slices conflict on `methodology-changelog.md`. So the dominant *real* HARD conflict (`_index.md`-sole) is high-frequency, and routing it through the `code-review` agent + user gate re-introduces latency ADR-069:37 flagged for blanket-Critic. This slice deliberately does **not** add a lighter path (gate-on-hand-resolve only, per /slice scope). Mitigations: (a) for `_index.md`-sole HARD the canonical hand-resolution is "re-run `/archive`" (ADR-069:72), surfaced in the skill's STOP diagnostic; (b) AC #5's APED-1 battery exercises the `_index.md`-sole case; (c) a lighter-path follow-up `add-index-md-soft-promotion-or-light-hard-path` is added to `slice-queue.md` (deterministic `_index.md` regen or Critic-skip for `_index.md`-sole conflicts). The "low-frequency" framing is withdrawn.
- **R-23 / R-24**: a remediation venue now exists (the `code-review` agent on the HARD resolution can flag unexpected orderings / baseline-shrink as a finding), but no dedicated detection ships this slice; both risks stay OPEN.
- **TRI-RESOLVE-1 as a reusable gate**: a second user-triage gate alongside TRI-1; future conflict-resolution surfaces (PSQ-4 push-time rebase) may reuse it.
- **`/code-review` scope**: `tools/parallel_conflict_resolver.py` already in-scope; the new functions are covered.

## Reversibility

**Expensive** (per [[ADR-066]] 3-class taxonomy — cheap / **expensive** / irreversible). Same shape as ADR-069/ADR-071: reverting requires restoring the pre-PCR-2b SKILL.md sub-step 2.5 prose, removing the new resolver functions + CLI modes, SUP-1-superseding the v0.77.0 changelog entry via a new entry (never edit in place), and forward-syncing all installed copies. The HARD/MIXED bare-STOP behavior would return — strictly no data-model or identity change, so reversible but multi-surface. Unlikely in practice: the gate-on-hand-resolve flow is well-bounded and strictly additive over the existing SOAD-1 STOP (it can only *add* review before a continue that the user previously did unguarded).
