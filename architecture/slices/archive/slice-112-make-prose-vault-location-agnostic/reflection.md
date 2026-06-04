# Reflection: Slice 112 make-prose-vault-location-agnostic

**Date**: 2026-06-04
**Shipped**: YES

## Validated
- The `<vault>/` placeholder fits the existing `<...>` prose-placeholder idiom and resolves to `architecture/` by default — validated: `_vault_paths.VAULT_ROOT == Path("architecture")` + full suite 1613 pass with the convention live (no pre-flip behaviour change).
- The converted-file one-way ratchet is genuinely INDEPENDENT of the re-pinnable baseline (M3) — validated by mutation: `test_ratchet_independent_of_repinned_baseline` re-pins `_BASELINE_SHA256` to match the regressed corpus and the ratchet STILL fires.
- The hash-keyed `_CONVERTED_CARVEOUTS` allowlist exempts EXACTLY the 4 operational carve-outs, path-scoped + fail-closed — validated by the code-Critic executing it (no hash collision, no over-broad exemption, AC5 readiness disjointness preserved).
- Agent self-sufficiency (M-add-1) — validated: the Critic subagent's `agents/critique.md` embeds the `<vault>` note at line 10 (within its reading window); CAD-1 clean after forward-sync.

## Corrected
- **design.md "definitional → plain-prose only" → reality needs ALSO a hash-keyed carve-out allowlist** for the 3 OPERATIONAL carve-outs (diagnose-out/slice-queue/active-folder) that stay in-code inside converted files (they classify `rewrite-at-flip` and would trip the ratchet; the design under-specified this). Corrected in [[design.md]] §Components + [[decisions/ADR-105]] §"Carve-out exemption (AS-BUILT)" + build-log DEVIATION. Not an ADR supersession (ADR-105 amended in-round via AS-BUILT clauses before merge).
- **The new convention prose itself mis-classified at first run** (AP-3): "historical anchors" beside an in-code `diagnose-out/` → `needs-human` (exit 2); a plain-prose `architecture/` sharing a line with "read/write" → `rewrite-at-flip`. Corrected by authoring the definitional prose around the line-anchored classifier; recorded in build-log + validation.md.

## Discovered
- **A count-constant re-pin must fan out to the MODULE's OWN docstring narrative, not just the constants + shippability rows** — the tool's docstring kept saying "313 / 0 doc-example / all empty" after the 303 re-pin (code-Critic M1). FBCD-1 sub-mode (c) is a DESIGN-Critic check (greps the repo for count pins at design time) — but a build-time-authored docstring is structurally invisible to it; only `/code-review` (which reads the code) caught it. **N=2** (slice-111 m5 + slice-112 M1). Impact: a build-check candidate — see Step 5b. Captured in lessons-learned.
- **The pilot proves carve-out CLASSES, not just files**: the agent's `:125` (slice-queue) + `:260` (per-slice active-folder) carve-outs exercise the exact classes the DEFERRED skill-file blockers (M1 / B1) represent — so the deferral doesn't ship those classes unproven.

## Deferred
- **Bulk skill-prose conversion** (297 literals across ~24 skill files) + the **op-gate floor re-pin** + the **BCR-1 anchor repoint** — reason: TRI-1 pilot reduction (B1/B2/B3/M1 confined to skill files). Lands in: `bulk-convert-remaining-skills-to-vault-seam` (registered in `slice-queue.md`).
- **`<diagnose-out>` token + seam** — reason: no `diagnose-out` seam in `_vault_paths.py` (B5). Lands in: a later slice that defines the seam, or the flip.
- **m2 (bare-arg residual handling)** — `graphify vault <bare-arg>` flip-handling + pinning `_RESIDUAL` line-numbers to live content. Lands in: the skill-conversion follow-on.
- **R-32 physical flip** — move + git-untrack + the remaining prose rewrite + `/commit-slice` RETIRE no-op + draining R-32.a/R-32.b. Lands in: the flip slice.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` + `critique-review.md` (EXTEND) + reality at build/validate/code-review:

- **B1** (worktree-composed flip-neutrality): **NOT-YET** — DEFERRED to the skill follow-on; but the *class* (active-folder) was VALIDATED in-pilot via the agent `:260` carve-out (the post-flip prefix-drop concern is real).
- **B2** (op-gate floor/allowlist breakage): **VALIDATED** — DEFERRED, but verified real: converting an op-gate-scanned skill WOULD shrink the floors; sidestepped by the CLAUDE.md/agents-only pilot (op-gate 6/11/23/0 unchanged, confirmed).
- **B3** (BCR-1 anchor): **NOT-YET** — DEFERRED; the follow-on repoints `test_bcr_1_backlog_round_trip.py` in the same slice it converts `slice`.
- **B4** (shippability "313" fan-out): **VALIDATED** — ACCEPTED-FIXED; the count-pin sprawl was real (rows 113/117 + the M1 docstring confirmed it spans more surfaces than the 3 constants).
- **B5** (`<diagnose-out>` no seam): **VALIDATED** — ACCEPTED-FIXED; zero diagnose-out seam confirmed; scoped out cleanly.
- **M1** (slice-queue undecided): **NOT-YET** — DEFERRED; class VALIDATED in-pilot via agent `:125`.
- **M2** (definitional non-deterministic) + **M-add-2** (disposition line-key brittleness): **VALIDATED** — ACCEPTED-FIXED; plain-prose `doc-example` chosen; the AP-3 build recalibration confirmed the definitional handling is load-bearing; the code-Critic m1 confirmed the brittleness exists (scoped).
- **M3** (ratchet separator + baseline-independence): **VALIDATED** — ACCEPTED-FIXED; both load-bearing, mutation-proven non-vacuous.
- **M-add-1** (agent runtime-resolution gap): **VALIDATED** — ACCEPTED-FIXED; the self-sufficient note was genuinely required + the code-Critic confirmed it's complete/early. The meta-Critic's headline catch.
- **m1** (CAD-1 note): **VALIDATED**; **m2** (exact remainder): **VALIDATED** — pinned 297 at build.

**Missed by Critic**:
- Neither the design-Critic NOR the meta-Critic caught the **carve-out-in-converted-file problem** (operational carve-outs trip the ratchet) — surfaced at build PLANNING (the Builder caught it pre-code). Design-time reasoning about "the gate keys on rewrite-at-flip only" glossed that operational carve-outs ARE rewrite-at-flip.
- Neither caught the **prose-classification bugs** in the new convention text — surfaced only at build EXECUTION (AP-3).
- The **code-Critic caught M1** (stale docstring) that the design+meta stack structurally could not (build-time code).

**Pattern**: 3-Critic complementarity (AP-19) confirmed again, cleanly non-overlapping: design-Critic → scope/sequencing blockers (B1-B5/M1); meta-Critic → consumption-axis gaps (M-add-1 agent-context, M-add-2 durability); code-Critic → build-time-artifact drift (M1 docstring). For a classifier/convention slice, design-time review (even dual-Critic) validates STRUCTURE but is blind to (a) corpus-classification calibration of the slice's OWN new prose and (b) build-time-authored count narratives — both execution-only (AP-3, N-th confirmation).

## Lessons for next slice
- **AP-3 again, twice**: executing the new prose/classifier against the real corpus caught 2 classification bugs AND the stale docstring — design-time reasoning (even dual-Critic-ratified) is not proof for a slice that authors classifier-visible prose.
- **Build-check candidate (M1, N=2)**: when re-pinning a counted-set constant, grep the MODULE's OWN docstring/comments for the OLD value — FBCD-1(c) (design-time) can't see build-time-authored docstrings.
- **Scope reduction at TRI-1 was the right call**: the CLAUDE.md+self-sufficient-agent pilot sidestepped 4 skill-file blockers while still proving every carve-out class via the agent's 2 carve-outs.
- **Value-keyed > line-keyed allowlists**: the hash-keyed `(path, sha256(value))` carve-out is durable against rewording where a `_DISPOSITION` 5-tuple line-key (M-add-2) is brittle.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-32: added the slice-112 progress paragraph (prose convention + pilot ship; prose-rewrite residual partially drained; status stays `mitigating`).
- This slice's [[design.md]] + [[decisions/ADR-105]] — AS-BUILT (hash-keyed carve-out allowlist + build-time prose recalibration).
- [[architecture/shippability.md]] — rows 113/117 re-pinned 313→303 + new row 118 (slice-112 convention + ratchet); the tool docstring fixed to 301/0/2/0 (M1).
- [[architecture/drift-log.md]] — slice-112 DCE-1 marker (via `vault_edit append`).
- [[architecture/lessons-learned.md]] — appended (Step 5).
- No methodology-changelog / VERSION change (MEPD-1 EXCLUDE).
