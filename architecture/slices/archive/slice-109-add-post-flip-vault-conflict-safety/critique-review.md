# Critique Review: Slice 109 add-post-flip-vault-conflict-safety

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-04
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary
The first Critic's review is strong and execution-grounded: all five findings (B1, M1, M2, m1, m2) are VALID with correct severities, the round-1 fixes applied to mission-brief/design/ADR-098 are sound, and I independently reproduced B1's CRLF byte-divergence (verified, not asserted). I am EXTENDING with two missed findings the first Critic did not surface: a real fail-visibility asymmetry where a retry-exhaustion `StaleVaultBaseError` is swallowed for `write_slice_queue` but propagates for `record_pick` at `/slice` Step 6.5, and a missing AC2-coverage pin for the empty-base first-pick create-race.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1: AC4 byte-identity false on CRLF on-disk queue** — confirmed; Blocker is appropriate. Independently reproduced: against a CRLF-seeded queue, `safe_write_text` → 0 CRLF (LF-faithful, `tools/_vault_write.py:162` `newline=""`), `safe_rewrite_text` → 4 CRLF (EOL-preserving, `tools/_vault_write.py:244-251`), `byte-identical: False`. `.gitattributes` confirmed (only `skills/**/SKILL.md`, `agents/*.md`, `skills/diagnose/passes/*.md` — no `architecture/**`). The fix is sound and complete. Note: bare `eol=lf` (without explicit `text`) is sufficient — `eol=lf` implicitly sets `text`, so the omission is NOT a fix gap.

- **M1: base-capture/read TOCTOU + graphify-in-window livelock** — confirmed; Major appropriate. Verified two-read hazard: `read_text()` at `tools/slice_queue_writer.py:848`, graphify spawn at `:868` BEFORE write at `:940`. Applied fix (single `read_bytes()` per attempt, graphify `active_blasts` hoisted out, claim re-run on re-read) closes it. Graphify-hoist claim is TRUE: `active_blasts` (`:866-870`) depends only on `repo_root`/`graph_path`/`blast_resolver`, NOT queue bytes.

- **M2: record_pick is a genuine RMW, unexercised in AC2** — confirmed; Major appropriate. `record_pick` reads `:782`, writes `:801` — real RMW; the BRANCH-3/ADR-090 pick-log is per-pick provenance, so a lost line is silent provenance corruption. Applied fix (new TF-1 row + AC2-must-exercise + re-scan note) sound.

- **m1: VWS-1 `_ROUTED_FUNCS` widening admits `expected_base=b""`** — confirmed; Minor appropriate. `_is_routed_call` (`tools/vault_write_safety_audit.py:401-408`) matches by name only. Fix (require `expected_base=` keyword present) closes the constant-base CAS-defeat; bounding correct (`expected_base` keyword-only required, `tools/_vault_write.py:207`).

- **m2: ADR-098 / ADR-089 residual framing** — confirmed; Minor appropriate. ADR-089 §Residual (`ADR-089.md:59`) names the deferred substitute; ADR-098 §Context now carries the framing sentence with `supersedes: null` retained. ADR-098 is next free (master tops ADR-097). ACCEPTED-FIXED accurate.

## Suspicious findings

No suspicious findings. Every first-Critic finding is grounded in executed or directly-verifiable source behavior; none over-reaches. A notably clean, evidence-led first-Critic pass.

## Missed findings

- **M-add-1: Retry-exhaustion fail-visibility is ASYMMETRIC across the two Step 6.5 writers — the design's "exhaustion RAISES (loud)" contract is silently swallowed for `write_slice_queue` but propagates for `record_pick`.** The must-not-defer #1 + error model (design.md:68) state retry exhaustion RAISES and "the degrade path must be loud." But at `skills/slice/SKILL.md` Step 6.5, `write_slice_queue` is wrapped in `try/except Exception as e: print('WARN: PSQ-1 queue regen failed (non-fatal)')` (`:456-457`) — a raised `StaleVaultBaseError` after retry exhaustion is **caught and downgraded to a non-fatal WARN**. By contrast `record_pick` (`:464-472`) has NO surrounding `except`, so its raised error propagates loudly (correct). The design should either (a) state that `write_slice_queue` exhaustion-loudness is intentionally subordinate to ADR-064's "PSQ-1 regen is non-fatal" (queue is regenerable, so swallowing IS right here — but then the must-not-defer's blanket "loud" is overstated and should be scoped to `record_pick`), or (b) make Step 6.5's `except Exception` discriminate `StaleVaultBaseError`. **Proposed fix**: add a design.md sentence reconciling the two and scope the "loud" must-not-defer to the un-wrapped provenance writer (`record_pick`). Documentation/scoping gap, not an implementation defect — but the unqualified "never silent" is materially imprecise about what the production caller does with the raise.

- **M-add-2: The empty-base first-pick create-race (`expected_base=b""`) is named in the error model but has no AC2/TF-1 coverage pin.** design.md error model (:69) asserts the create-race is covered by CAS; mechanically correct (`safe_rewrite_text` normalizes `b""` → mismatch → raise, `tools/_vault_write.py:238-243`). But `record_pick`'s first-pick path (`tools/slice_queue_writer.py:794-799`, the `## Pick log`-creation branch) is the empty-base case, and two concurrent FIRST picks on a fresh queue is a real BRANCH-3 state. No TF-1 row pins "two concurrent first-pick `record_pick` against an empty/no-pick-log base → both create-and-merge, 0 lost." **Proposed fix**: add a TF-1 row `test_concurrent_first_pick_empty_base_both_create` (two `record_pick` against a queue with NO `## Pick log` section under `mp.Barrier`). Low cost; closes the asserted-but-unpinned boundary.

## Severity adjustments

No severity adjustments. All five first-Critic severities (B1=Blocker, M1=Major, M2=Major, m1=Minor, m2=Minor) are correctly calibrated.

## Notes

High confidence. Executed the byte-identity reproduction (B1 verified real), traced all four contended write sites (`slice_queue_writer.py:801,940`, `slice_queue_claim.py:602/610/616`), verified the `_is_routed_call` name-only match + `_ROUTED_FUNCS` pin (`sites_routed >= 4`, no `== 2` literal — FBCD-1 sub-mode-c note correct). On the three brief-flagged probes: (a) the deferred `/commit-slice` RETIRE no-op is correctly out-of-scope — PCR's queue write (`parallel_conflict_resolver.py:480`) is a git-rebase-time, pre-flip, tracked-path writer that RETIREs under `vault_is_external` post-flip, so it is the writer being retired, NOT a missed 4th post-flip contended writer; (b) NO un-accounted 4th post-flip queue writer (PCR's `write_text` at `:480`/`:1602` both pre-flip git-rebase-coupled); (c) graphify-hoist independence is true. First-Critic calibration: disciplined, execution-first, no manufactured findings and no over-reach. One reservation: M-add-1 may be triaged OVERRIDDEN if the user judges ADR-064's "PSQ-1 regen non-fatal" already implicitly scopes the must-not-defer — in which case the fix is a one-sentence clarification, not a behavior change.
