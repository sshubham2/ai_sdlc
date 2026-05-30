---
id: ADR-077
title: Scope the PCR-1 baseline-integrity gate to claim-loss-by-corruption (discriminate the orphan-claim exemption by baseline truncation-shape), not a blanket truncation STOP
date: 2026-05-30
slice: slice-085-harden-pcr-1-truncated-baseline
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-077: Scope the PCR-1 baseline-integrity gate to claim-loss-by-corruption

## Context

[[ADR-074]] (slice-082) added the PCR-1 SOFT-regen equivalence guard `_verify_soft_equivalence`. Its Invariant #1 (queue claim-preservation, CLAIMED-subset) exempts **orphan claims** — a claimed candidate present in a discarded rebase stage but absent from the baseline — from STOP, because at the candidate-name level that pattern is the COMMON, legitimate case (the rebase-target's top-10 queue churned and a stale candidate fell off). Instead of STOPping it emits a loud `cross-stage-claim-drop` stderr WARN.

R-24 (risk-register) names the residual hole: at the candidate-name level this legitimate churn-drop is **indistinguishable** from a pathological case where the baseline blob is itself truncated/corrupt and lost the candidate by corruption rather than churn. slice-082 deliberately chose WARN-not-STOP (the `/critique` M2 + meta-Critic confirmed that STOPping on every cross-stage drop would false-STOP nearly every real SOFT merge, defeating the auto-resolve mechanism). R-24 was carved out OPEN as the tracked residual.

This slice (085) closes the hole by adding a **discriminating signal** the name-level comparison lacked: the baseline blob's **structural integrity**. The decision facing this slice: **how aggressively should the new integrity signal escalate a SOFT auto-merge to STOP?**

### The reframing that bounds the harm (corrected per /critique B1)

PCR-1's SOFT path regenerates `slice-queue.md` by taking the rebase-target baseline (stage 3) verbatim and overlaying merged claims (`_regen_slice_queue` / `_overlay_claims_on_queue_text`).

- The candidate **list** is ephemeral — `/slice` regenerates the full top-10 on every run, so a truncation dropping only *unclaimed* candidates **self-heals**.
- A **claim** (`Claimed-by`/`Claimed-at`, PSQ-2 ownership) does **NOT** self-heal: `_overlay_claims_on_queue_text` (`parallel_conflict_resolver.py:941-1032`) emits a claim only for a candidate that still has a `### ` heading in the baseline; a claimed candidate truncated out of the baseline is silently dropped (lines 1017-1018) and the short queue is written (line 392) + committed.

Therefore the only **non-self-healing** harm a truncated/corrupt baseline causes is **claim-loss** — the load-bearing fact for the decision below. (The earlier draft of this ADR wrongly called the entire no-claim-loss condition "self-healing"; corrected here — only the *list* self-heals, never a dropped *claim*.)

## Options considered

### 1. Targeted-undiscriminated (orphan-branch, no new signal)
Keep the orphan-branch but STOP whenever a claimed candidate drops and it was a heading in the discarded stage.
- **Pros**: minimal code.
- **Cons**: this IS the fix slice-082 already rejected — the discarded-stage-heading condition fires on *legitimate* churn too (a claimed candidate that churned off the top-10 was a heading in the discarded stage by definition). It would false-STOP normal churn. **Rejected** (re-litigates the settled slice-082 M2 decision).

### 2. Broad (every-field, every merge)
Run a full well-formedness check on every SOFT merge; STOP if ANY entry block is missing ANY of its 5 on-disk field labels, regardless of claim-loss.
- **Pros**: maximal corruption detection; strongest fail-closed posture.
- **Cons**: highest false-STOP — any legacy or hand-edited queue with a single slightly-noncanonical entry blocks **every** parallel merge until a human fixes it. Directly defeats PCR-1's auto-resolve value (the slice-082 M2 / meta-Critic concern). Also over-broad vs the harm model: STOPs on truncations that drop only unclaimed candidates (self-healing → no harm). **Rejected** (false-STOP cost ≫ correctness gain; the register explicitly rejected the analogous "baseline sanity-floor" as "arbitrary threshold, false-STOP risk on a legitimate large-churn cycle").

### 3. Hybrid (truncation-shape, every merge, claim-independent)
Run a truncation-shape check on every SOFT merge; STOP if the baseline is truncation-shaped, **independent of claim-loss**. (This was the author's initial recommendation.)
- **Pros**: catches a truncated baseline even when set-equal; bounded vs Option 2 (only truncation-shape, not every-field).
- **Cons**: still STOPs the self-healing case (truncation that drops only unclaimed candidates) — a false-STOP for zero correctness gain, because the next `/slice` regenerates the full list and no durable state was lost. **Rejected** once the claim-loss harm model is applied: the only durable state is claims, so a claim-independent STOP over-fires.

### 4. Claim-loss-discriminated truncation gate (CHOSEN)
Wire the baseline truncation-shape signal into Invariant #1's **orphan-claim branch only**. When a claimed candidate is dropped from the baseline:
- baseline **truncation-shaped** → STOP (claim-loss-by-corruption — the R-24 scenario), with an audit row;
- baseline **well-formed** → existing WARN (legitimate churn-drop, happy path preserved).
Additionally, when the baseline is truncation-shaped but **no claim is threatened**, emit a loud non-blocking WARN (upstream-corruption observability) and auto-merge (self-healing).
- **Pros**: STOPs exactly where harm is real (a claim lost to corruption) and nowhere else; **zero new false-STOP on healthy churn** (well-formed baseline → WARN unchanged) → respects the slice-082 M2 / meta-Critic constraint and the register's rejection of arbitrary thresholds; uses an *intrinsic structural* signal (truncation-shape), not a count threshold or the fragile mid-rebase `git HEAD` comparison the mission brief first proposed; minimal, cheaply-reversible surface.
- **Cons**: does NOT detect a baseline truncated **exactly at a block boundary** (clean N-block prefix) that drops a claimed block N+1 — structurally indistinguishable from churn. Documented residual (see Consequences); R-24 stays **narrowed-open**, not retired.

## Decision

> **RATIFIED at TRI-1 (2026-05-30): Option 4 (m1) + (a) document M1 as residual.** The user ratified **Option 4** for the gate-breadth fork (m1) and **(a) document-as-residual** for the M1 claim-loss gap (NOT (b) close-it). The discriminator stays **orphan-gated** (Option 4); M1's invisible-claim case is carried as a named R-24 residual.

**Add `_baseline_is_truncation_shaped(queue_text) -> (bool, reason)`** to `tools/parallel_conflict_resolver.py`. **Tail-specific** signature (per /critique M1, NOT a whole-file completeness scan): truncation-suspect iff the **last** `### <name>` block is incomplete (missing ≥1 of the 5 canonical on-disk PSQ-1 field labels) OR the file does not end at a clean block boundary (ends mid-field-line). Source the 5 labels from a new `_RENDERED_FIELD_LABELS` constant in `tools/slice_queue_writer.py` that `_format_entry` renders FROM (genuine SSoT per M3); CRLF-normalize and treat empty / `_(no candidates)_` baselines as NOT suspect (per m3).

**Wiring (Option 4, orphan-gated):**
- In `_verify_soft_equivalence` Invariant #1's **orphan-claim branch** (`claimed_names - baseline_headings`), when a claimed candidate is dropped from the baseline: baseline **truncation-shaped** → **STOP** (claim-loss-by-corruption), best-effort audit row first; baseline **well-formed** → existing **WARN** (legitimate top-10 churn; preserves the slice-082 M2 / ADR-074 anti-false-STOP decision).
- **No provable claim-drop** (orphan branch empty) — including a tail-truncated baseline that dropped only *unclaimed* candidates → **auto-merge** (Option 4). M2 caveat retained: this commits a transiently-corrupt (short) queue that self-heals at the next `/slice`; accepted at low/low (list regenerable, no durable claim lost).
- If `_baseline_is_truncation_shaped` cannot parse the baseline → suspect → STOP in the claim-threatened branch (fail-closed on uncertainty). The pre-existing overlay-silent-drop STOP at `:1775-1783` is untouched (per M1 correction).

**M1 = documented residual (disposition (a), ratified).** The claim-only-on-a-truncated-baseline case (claim lines cut, heading surviving) is invisible to `merged_claims` (= `claims_2 ∪ claims_3`) → it never enters `claimed_names` or the orphan branch → NOT closed. Carried as a named R-24 residual. **(b) declined at low/low**: the precondition is doubly-rare under the cooperative model (a genuinely-committed corrupt baseline AND the claim existing only on that branch), and the meta-Critic's *proposed* (b) mechanism was anyway flawed — the overlay's normal insert-new path adds claims to baseline blocks that lack claim lines, so "flag a `merged_claims`-claimed candidate whose baseline block lacks claim lines" would false-STOP every insert-new claim; the only sound (b) signal would be a general claim-independent tail-truncation precondition, which over-STOPs vs the ratified Option-4 scope.

## Consequences

- **Behavior change, but MEPD-1 EXCLUDE** (determined per /critique-review m-add-2 + the slice-082/084 precedent): a SOFT merge that previously WARN-then-AUTO_MERGEd a claim-dropping truncated baseline now STOPs (a SOFT merge over a *well-formed* baseline is unchanged). Although behavior shifts, slice-085 is a **risk-narrowing fix-slice with an ADR and NO new RULE-ID** — the project's operative MEPD-1 interpretation (N=3: slice-077/079/082, re-applied slice-084) is **EXCLUDE** for this class: ADR-077 + the R-24 `**Narrowed:**` annotation + reflection ARE the audit trail; **no `methodology-changelog.md` entry, no VERSION bump, no PMI-1 manifest bump** (PMI-1's inventory is unchanged — this is an in-place logic edit to the already-manifested `parallel_conflict_resolver.py`, not a new file). The pre-finish gate records this determination explicitly so it is gated, not silently skipped. (If the user rules INCLUDE at TRI-1, the changelog entry + atomic version bump are added instead.)
- **R-24 narrowed, not retired** (mirrors [[ADR-076]]/R-23 precedent). `/reflect` annotates R-24: `**Narrowed:** slice-085 — claim-loss where a claimed candidate's whole block is truncated out of a tail-truncation-shaped baseline now STOPs (orphan-branch-gated, Option 4). Residuals (undetected, low/low): (i) a baseline truncated EXACTLY at a clean block boundary (last surviving block complete) → indistinguishable from legitimate churn; (ii) the M1 case — a claim that existed only on the truncated baseline branch, claim lines cut, invisible to merged_claims (disposition (a): documented, not closed); (iii) the VAULT_CLAIM sibling path (resolve_vault_claim_conflict, deferred to future PCR-2a hardening).` Status stays open-downgraded (low/low).
- **Surviving-heading claim cases, corrected (per /critique M1 — supersedes the placeholder's mistaken "B2 already-STOPs" claim)**: the `:1775-1783` claimed-WITH-heading loop STOPs only the **overlay-silent-drop** case (claim in `merged_claims`, heading survives, but the regenerated output lacks the claim because the block's `Risk-retired` pivot is malformed). It does NOT catch claim-*line* truncation per se, because `merged_claims = claims_2 ∪ claims_3` re-applies the claim from the other stage. AC-4(a) pins this overlay-drop STOP as unchanged. The **M1 case** — a claim that existed ONLY on the truncated baseline branch, claim lines cut → absent from `merged_claims` → invisible to every claim-level check (never enters `claimed_names` or the orphan branch) — is **a documented residual (disposition (a), TRI-1-ratified)**, NOT closed. It is folded into the R-24 residual list above. (b-ii) `Claimed-by` **value present but garbled** stays genuinely **out of scope**.
- **Harm model is NOT nil for no-claim-loss truncation (per /critique M2)**: even when no durable claim is lost, AUTO_MERGE writes the truncated baseline verbatim (`:392`) + `git add` + `git rebase --continue` (`:396-398`), committing a transiently-corrupt queue into history that self-heals only at the next `/slice`; an intervening claim / parallel read sees the short set. Accepted at low/low (list regenerable, no durable claim lost) — but this is the real substance of the Hybrid-vs-Option-4 tradeoff, ratified at TRI-1, not a nil-cost narrowing.
- **Single source of truth — only if wired correctly (per /critique M3)**: `_RENDERED_FIELD_LABELS` is SSoT ONLY if the writer's `_format_entry` (`:631-639`) renders FROM it (not a parallel copy) AND a test pins emitted-labels == constant (mirror `test_psq_2_claim_machinery.py`). Note the existing `slice_queue_claim.py:105-117` prefix constants (`_RISK_RETIRED_PREFIX` etc.) — `_RENDERED_FIELD_LABELS` is the *render* contract for the 5 PSQ-1 labels; do NOT add a fourth copy. A hand-listed tuple that the writer does not render from would relocate drift, not remove it.
- **VAULT_CLAIM sibling residual (per /critique-review m-add-1)**: the same baseline-truncation claim-loss exposure exists in `resolve_vault_claim_conflict` (`:1218-1421`) — it overlays only the collision *winner's* claim onto a verbatim baseline (`:1323`), its post-overlay regex (`:1351-1365`) STOPs only when the *winner's* claim fails to land, and it never runs `_verify_soft_equivalence` (SOFT-path only, `:374`). A truncated baseline dropping a *third* claimed candidate's lines in the VAULT_CLAIM path is committed silently. This is OUT of scope for slice-085 (mission-brief scopes to PCR-1 SOFT), but the "claim-loss must STOP" principle is asymmetric until a future PCR-2a hardening extends the truncation check to the VAULT_CLAIM path — recorded here as an explicit sibling residual (queue candidate nominee).
- No CLI/contract/data-model surface change; no auth surface. Cooperative threat model unchanged.

## Reversibility

**cheap** — the change is one new helper + one constant + one branch inside an existing guard. Reverting restores the pre-085 WARN-only orphan-claim behavior with no migration (the queue file format is unchanged; `_RENDERED_FIELD_LABELS` is a pure refactor of an existing literal). No persisted state depends on the new STOP.
