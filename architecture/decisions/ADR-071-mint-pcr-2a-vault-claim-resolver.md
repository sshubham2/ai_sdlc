---
id: ADR-071
title: Mint PCR-2a — vault-claim auto-resolution via strict-newer Claimed-at timestamp-winner plus read-only loser-replacement suggestion
date: 2026-05-29
slice: slice-078-add-pcr-2a-vault-claim-resolver
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-071: Mint PCR-2a — vault-claim auto-resolution via strict-newer `Claimed-at` timestamp-winner plus read-only loser-replacement suggestion

## Context

[[ADR-069]] (slice-076; PCR-1) minted the 5-class parallel-conflict-resolution taxonomy {SOFT, VAULT_CLAIM, HARD, MIXED, UNKNOWN} and shipped auto-resolution for the SOFT class only. The remaining four classes return `ResolutionResult(action="STOP", ...)` and fall through to a SOAD-1 3-option ask block in `/commit-slice --merge` sub-step 2.5.

The **VAULT_CLAIM** class fires for the simplest concurrent-claim scenario: two parallel sessions claim the same candidate from `architecture/slice-queue.md` at different times via `tools.slice_queue_claim --claim <name>`. Today's PCR-1 behavior is to detect this collision in two places (the upstream `classify_conflict` gate at lines 200-213, and the defense-in-depth `_regen_slice_queue` gate at lines 627-637), then STOP and hand off to the user. The handoff is unnecessary friction: both `Claimed-at` timestamps are ISO-8601 UTC, comparable, and the cooperative-not-adversarial threat model carried from [[ADR-067]] makes "trust the newer timestamp" a safe default.

PCR-2 (the full follow-on rule on the parallel-conflict-resolution axis) was nominated in [[ADR-069]] § Forward references to cover both VAULT_CLAIM (timestamp-winner + light Critic) AND HARD (full design-Critic + meta-Critic stack on proposed merge resolution) AND TRI-RESOLVE-1 (user triage gate mirroring TRI-1). At slice-078 definition (2026-05-28), the user picked "Split: 078 = vault-claim only" per /slice Step 5 hard-limit discipline (≤5 ACs, ≤1 day, system shippable after). PCR-2a is the vault-claim leg; PCR-2b (slice-079) ships HARD + TRI-RESOLVE-1.

The slice-076 reflection (Discovered #1 — registered as R-21) carved out the "SOFT auto-regen produces semantically-different content from a manual-resolve baseline at a corner case" risk. PCR-2a inherits the same risk-acceptance shape for VAULT_CLAIM: the auto-resolution may differ at corner cases (claimed_at-tie, multi-collision, audit-log append failure) from what a human-with-Critic-stack would produce. The design's Error model returns `action="STOP"` for those corner cases, preserving fall-closed atomicity.

## Options considered

1. **Strict-newer `Claimed-at` timestamp-winner with read-only loser-replacement suggestion (chosen)** — `resolve_vault_claim_conflict` selects the entry with the strictly-newer `Claimed-at`; reads `architecture/slice-queue.md` to suggest the loser's next-priority unclaimed NON-OVERLAPPING candidate (audit log records the suggestion); does NOT auto-claim the replacement on the loser's behalf. Behaviorally additive on the existing SOFT auto-resolution code path (same stage-then-commit atomicity, same `_append_audit_log` reuse).
   - Pros: minimal blast-radius (one new public function + 4 file-local helpers + one prose edit in SKILL.md); reuses PCR-1's atomicity infra; the strict-newer rule maps cleanly to ISO-8601 lexicographic order (no timezone math; ISO-8601 UTC is already what PSQ-2 writes); read-only loser-replacement avoids the auto-claim race window with the loser's actual session.
   - Cons: claimed_at-tie corner case falls-closed to SOAD-1 STOP — NOT rare given `tools/slice_queue_claim.py:630` `_now_iso8601_utc()` writes second-precision (`%Y-%m-%dT%H:%M:%S`, no `%f` microseconds) timestamps, a ~1-second wall-clock tie window for racing claims. Deferring ties to PCR-2b is acceptable not because ties are rare but because the strict-newer rule auto-resolves the dominant non-tie case (the common "first session claims, second session sees the new candidate seconds-to-minutes later, both attempt-to-claim before fully syncing" scenario), while explicitly punting genuinely-ambiguous same-second ties to user triage. Multi-candidate collision in one diag also falls-closed (deferred to PCR-2b).

2. **Auto-claim the loser's replacement** — write `Claimed-by:` + `Claimed-at:` for the suggested replacement on the loser's behalf, using the `Claimed-by:` value parsed from the loser's existing entry.
   - Pros: closes the loser-out-of-sync window faster; loser sees a complete resolution rather than a suggestion.
   - Cons: introduces race window with the loser's actual session, where the loser may have CONCURRENTLY claimed a different candidate or released the original claim. PCR-2a would need to invoke `tools.slice_queue_claim --claim <name>` with the loser's identity, which the existing CLI does not support (identity is derived from `git user.email`, not passed as arg). Deferred to PCR-2b where the broader Critic stack can adjudicate.

3. **Earlier-`Claimed-at` wins (first-claim-wins)** — preserve the older claim instead of the newer one.
   - Pros: rewards first-mover.
   - Cons: contradicts existing PSQ-2 `_merge_claim_dicts` semantics at lines 648-666 of `parallel_conflict_resolver.py`, which explicitly states "newest-Claimed-at-wins" for same-Claimed-by collisions during SOFT regen. Different-Claimed-by VAULT_CLAIM was gated upstream precisely to defer this decision; now that we make it, consistency with the same-Claimed-by case strongly suggests newest-wins.

4. **Full design-Critic + meta-Critic stack on the proposed VAULT_CLAIM resolution** — promote VAULT_CLAIM to the same heavyweight resolution path as HARD; spawn Critic agents on the proposed timestamp-winner result.
   - Pros: methodologically consistent with the rest of the pipeline; surfaces edge cases (e.g., claim-by-stale-machine-clock) that auto-resolution may mishandle.
   - Cons: 10×+ effort blow-up for a class whose resolution is mechanical; defeats the user's slice-split choice at /slice; LARGE effort fits PCR-2b's HARD-conflict scope where Critic-stack overhead is justified.

5. **Status quo (defer all VAULT_CLAIM resolution to PCR-2b)** — keep VAULT_CLAIM returning STOP; ship only PCR-2b in slice-079.
   - Pros: zero PCR-2a code.
   - Cons: leaves the simplest concurrent-claim collision class manual indefinitely; PCR-2b's HARD-class Critic-stack infra is the bigger build, so prepending PCR-2a buys VAULT_CLAIM auto-resolution at fractional cost.

## Decision

**Option 1** — ship `resolve_vault_claim_conflict` with strict-newer `Claimed-at` timestamp-winner + read-only loser-replacement suggestion. Wire it into BOTH dispatch sites: (a) the CLI-facing `resolve_soft_conflict()` wrapper at L242-253 (new VAULT_CLAIM branch above the existing `if cls is not ConflictClass.SOFT:` guard — without this the CLI path short-circuits VAULT_CLAIM to STOP before reaching the defense-in-depth backstop) AND (b) `_regen_slice_queue()`'s defense-in-depth gate at L627-638 (raise → dispatch swap). Preserve the UNKNOWN-class raise leg at L605-609 verbatim. Update `skills/commit-slice/SKILL.md` sub-step 2.5 dispatch prose with APED-1-executed structural pins: L185 dispatch paragraph gains a VAULT_CLAIM-in-APPLIED-context sentence; L192 closing summary DROPS `VAULT_CLAIM` from the fall-closed-to-SOAD-1 enumeration. Extend `architecture/parallel-conflict-resolution-log.md`'s section-shape with a sibling `## Vault-claim resolution - <ISO-8601>` row format (UNIFORM hyphen-space separator — section-type distinguished by prefix word `Vault-claim` vs `Soft-conflict`, NOT by trailing dash decoration; avoids Windows smart-dash autocorrect fragility). Defer HARD-conflict resolution + TRI-RESOLVE-1 user triage + claim-on-behalf to PCR-2b (slice-079).

## Consequences

- The simplest VAULT_CLAIM scenario (two sessions claim same candidate at different times) auto-resolves without user STOP — closes a known friction surface and reduces R-21's residual corner-case window (the VAULT_CLAIM auto-resolution becomes one more PCR-1-equivalent class with the same corner-case risk shape).
- The HARD-conflict resolution path remains unchanged: VAULT_CLAIM and HARD have decoupled implementations; PCR-2b's HARD work does not retroactively affect VAULT_CLAIM behavior.
- PCR-1's same-candidate-different-identity defense-in-depth gate at `_regen_slice_queue` lines 627-638 is reshaped (one raise → one dispatch) but the UNKNOWN-class raise leg at 605-609 is preserved verbatim — pinned by AC#2's UNKNOWN-still-fail-closed test.
- `architecture/parallel-conflict-resolution-log.md` now has two section-types (`## Soft-conflict resolution -` and `## Vault-claim resolution -`); uniform hyphen-space separator across section-types. Future PCR rules will add additional section-types as they ship (PCR-2b: `## Hard-conflict resolution -`; tentative — same uniform separator discipline).
- The mini-CAD drift-guard family (OSDG-1) now guards one more SKILL.md prose surface (`skills/commit-slice/SKILL.md` sub-step 2.5 prose-pin) — pinned by AC#3's two tests.
- methodology-changelog rules family grows by one: `PCR-2a` refines `PCR-1`'s class taxonomy without superseding it; subsequent `PCR-2b` will mint at slice-079; the v0.74.0 entry adds bidirectional pins per RPCD-1.
- Cooperative-not-adversarial threat model carried forward from [[ADR-067]] / [[ADR-069]] — explicitly NO adversarial backdating mitigation, NO claim-by-machine-clock-skew defense; sessions that backdate `Claimed-at` to game the strict-newer winner are out-of-scope.

## Reversibility

**Cheap** — three localized changes (one new function + helpers in `tools/parallel_conflict_resolver.py`; one prose edit in `skills/commit-slice/SKILL.md`; one new section-type in `architecture/parallel-conflict-resolution-log.md`) plus their test modules. Reverting is a `git revert` on the slice-078 merge commit; pre-PCR-2a behavior (VAULT_CLAIM → STOP → SOAD-1 b-option manual resolution) is fully restorable. The audit log's accumulated vault-claim section rows are inert if the function is removed — they remain as historical record without breaking the SOFT row schema. No data migration required; no contract change to the `ResolutionResult` dataclass; no removal of fields from `_append_audit_log`'s SOFT-row shape.

PCR-1's broader risk (R-21: SOFT auto-regen produces semantically-different content from manual-resolve baseline at corner cases) inherits to PCR-2a with the same defenses-in-depth (APED-1 battery on minted predicates; defensive fail-closed `_regen_slice_queue` UNKNOWN-class raise leg preserved; audit-log append-only). Anticipated failure modes specific to PCR-2a (per /critique-review m5 ACCEPTED-PENDING precedent from slice-076): (a) machine-clock-skew producing an apparent "newer" `Claimed-at` that is actually older real-time; (b) the loser-replacement read-only suggestion becoming stale within seconds of the audit log being written. Both are accepted residuals — corrigible in PCR-2b's Critic-stack adjudication if recurrence emerges.
