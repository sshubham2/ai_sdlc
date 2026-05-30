# Critique: Slice 085 harden-pcr-1-truncated-baseline

**Critic reviewed**: mission-brief.md, design.md, ADR-077 (new)
**Date**: 2026-05-30
**Result**: NEEDS-FIXES
**Reviewer**: `critique` agent (separate persona; read the 2136-line resolver + 890-line writer + slice_queue_claim before attacking)

> Provenance note: an earlier placeholder `critique.md` was main-thread self-review written before this async agent returned — it has been overwritten by this genuine agent output. The placeholder's "B2" (heading-survives-claim-truncated already STOPs at :1775-1783) was **factually wrong** and is corrected by this agent's M1.

## Summary
The slice is a well-scoped hardening of a low/low residual with a defensible discriminator design, and the Option-4 refinement is largely justified. But the truncation discriminator as wired (orphan-claim branch only) leaves a concrete claim-loss-by-truncation path uncovered (M1), the "self-healing / only-claims-durable" harm framing materially understates that the resolver commits the truncated baseline into git history (M2), and the proposed single-source-of-truth constant collides with constants that already exist in `slice_queue_claim.py` (M3). No blockers — all addressable within the chosen Option-4 architecture.

## Findings

### Blockers (must address before /build-slice)

None. No finding requires redesign or a spike.

### Majors (address this slice)

#### M1: AC-1 wiring leaves a claim-loss-by-truncation path that never enters the orphan branch
- **Claim under review**: AC-1 / design.md — discriminator called "in Invariant #1 orphan-claim branch, when a claimed candidate is dropped." ADR-077 — "STOP only when claimed-candidate-dropped AND baseline truncation-shaped."
- **Issue**: The orphan branch is `claimed_names - baseline_headings` (`resolver.py:1790`) — fires only when the candidate's `### heading` is ABSENT from the baseline. The heading-survives-but-claim-lines-truncated case does NOT enter it. Trace: `claimed_names` is built from `merged_claims` = `claims_2 ∪ claims_3` (`:1743-1744`, `:919-938`). If the baseline (`text_3`) is truncated so the heading survives but the claim lines are cut: (i) if the discarded stage `claims_2` still has the claim → `merged_claims` keeps it → overlay re-applies it → output is correct, no loss (auto-merge is right). (ii) **if the claim existed ONLY on the truncated baseline branch** → `claims_3` lost it, `claims_2` never had it → `merged_claims` lacks it → candidate not in `claimed_names` → neither the `:1775-1783` claimed-WITH-heading loop NOR the orphan discriminator considers it → **claim silently lost, no STOP**. And the block is NOT "truncation-shaped" under the 5-PSQ-1-label signature (the 5 labels survive; claim lines live AFTER `Risk-retired`, outside the 5). So AC-1 does not deliver "fail-closed on claim-loss-by-corruption" for this input class.
- **Evidence**: `resolver.py:1743-1744, 1756, 1775-1799`; `_merge_claim_dicts:919-938`; claim-line render `slice_queue_writer.py:647-648` (NOT among the 5 labels); `parse_queue_text` `slice_queue_claim.py:269-291`.
- **Proposed fix**: Either **(a)** document this sub-case (claim-only-on-a-truncated-baseline-branch, claim lines cut, heading surviving) as an additional named residual in ADR-077 §Consequences + R-24, alongside clean-block-boundary truncation — cheaper, scope-honest at low/low; OR **(b)** extend the signature so a block whose name is in `merged_claims`-as-claimed but whose baseline block lacks the claim lines counts as truncation-shaped, plus a check in the `claimed_names & baseline_headings` path — genuinely closes it. Pick one explicitly; do not leave the gap silent.
- **Builder draft**: ACCEPTED-PENDING — **recommend (a)** at low/low (the case requires a committed baseline that truncated mid-claim-block AND the claim existed only on that branch — doubly rare under the cooperative model). Surface the (a)-vs-(b) choice at TRI-1. **Separately ACCEPTED-FIXED**: my placeholder's claim that `:1775-1783` already catches "claim-line truncated" is corrected in design.md/ADR-077/AC-4 (it catches overlay-silent-drop, NOT claim-line truncation).

#### M2: the "only claims durable / candidate list self-heals" harm model omits that the resolver COMMITS the truncated baseline to git history
- **Claim under review**: design.md / ADR-077 — "only CLAIMS are durable; candidate list self-heals on next /slice; the only harm is claim-loss."
- **Issue**: On AUTO_MERGE the resolver writes the truncated baseline verbatim (`:392`) then `git add` + `git rebase --continue` (`:396-398`) — committing the short/corrupt queue into history. It self-heals only at the *next* `/slice`; until then the committed queue is the corrupt one, and any intervening `/slice` claim or parallel-session read operates on the truncated candidate set. "Self-healing" is eventually-consistent, not nil-harm. The narrowing to claim-loss-only is still defensible at low/low, but the design asserts nil harm, overstating the safety.
- **Evidence**: `resolver.py:383-398` (write_text → git add → rebase --continue); AC-3.
- **Proposed fix**: Restate the harm model: "truncation-but-no-claim commits a transiently-corrupt queue into history, self-healing only at the next /slice regen; the WARN is the corrigibility hook. Accepted at low/low because the list is regenerable and no durable claim is lost." Keep Option 4 but stop asserting nil harm; ratify the Hybrid→Option-4 narrowing at TRI-1 with this corrected statement.
- **Builder draft**: ACCEPTED-FIXED — corrected the harm model in ADR-077 §Context/§Consequences + design.md reframing to "transiently-corrupt committed queue, eventually-consistent self-heal," not nil-harm.

#### M3: `_RENDERED_FIELD_LABELS` "single source of truth" duplicates label knowledge already in `slice_queue_claim.py`
- **Claim under review**: AC-5 / design.md — "New constant `_RENDERED_FIELD_LABELS` … single source of truth."
- **Issue**: It is a *third* representation. `slice_queue_claim.py:105-117` already defines `_RISK_RETIRED_PREFIX` etc. (pinned by `test_psq_2_claim_machinery.py`); the writer's f-strings `:634-638` are the render source. A hand-listed tuple in `slice_queue_writer.py` that the writer does NOT actually render from is SSoT-in-name-only — the discriminator could pass while the writer emits a renamed label.
- **Evidence**: `slice_queue_claim.py:105-117`; `slice_queue_writer.py:634-638` (render), `:647-648` (claim lines, not among the 5).
- **Proposed fix**: (1) Have `_format_entry` (`:631-639`) consume `_RENDERED_FIELD_LABELS` directly so the constant IS the render source. (2) Add a test pin asserting emitted labels == `_RENDERED_FIELD_LABELS` (mirror `test_psq_2_claim_machinery.py`). (3) Note the relationship to the existing `slice_queue_claim` prefix constants so no fourth copy is added.
- **Builder draft**: ACCEPTED-FIXED (design) + ACCEPTED-PENDING (build) — design.md + ADR-077 updated to require `_format_entry` to render FROM the constant + a render-parity pin + a note on the `slice_queue_claim` prefixes; the wiring + pin land at /build-slice.

### Minors (log; address if cheap)

#### m1: user chose "Hybrid"; Builder shipped Option 4 — ratify at triage, don't auto-bless
- **Issue**: Option 4 is a legitimate, strictly-narrower refinement (the Hybrid no-claim-loss STOP would re-litigate the slice-082 M2 false-STOP rejection), but it is a unilateral narrowing of an explicit user gate-answer; per SOAD-1/TRI-1 it must be surfaced for ratification, not absorbed into an ADR.
- **Evidence**: ADR-077 NOTE; CLAUDE.md Ask discipline / SOAD-1; risk-register.md:435.
- **Proposed fix**: Present Hybrid-vs-Option-4 as a structured-options ratification at TRI-1 (recommend Option 4 with the M2-corrected harm statement).
- **Builder draft**: ACCEPTED-PENDING — surfaced at TRI-1 below (this is the M2 the placeholder also flagged); ADR-077 Decision already marked PROVISIONAL.

#### m2: "truncation-shaped" check is O(blocks × labels) over the whole baseline per SOFT merge — confirm bounded
- **Issue**: Trivially bounded at top-10 today; a future PSQ extension lifting the cap would silently make it O(n).
- **Proposed fix**: One sentence in design.md noting the ≤10-block bound; flag for re-review if the cap is lifted.
- **Builder draft**: ACCEPTED-FIXED — bound note added to design.md.

#### m3: discriminator parse-failure → STOP needs an APED-1 *executed* battery, not reasoned
- **Issue**: Per APED-1 (Dim 9), the new parse rule MUST be executed against an adversarial battery at build: CRLF baseline (`parse_queue_text` normalizes CRLF at `slice_queue_claim.py:240`; the new helper must too), trailing-space heading (`### add-foo `), and especially **empty baseline** (`text_3 == ""` → falls to `text_2`; `_baseline_is_truncation_shaped("")` must NOT classify the legitimate empty/placeholder queue as truncation-shaped → false STOP), plus a forward-compat extra field.
- **Evidence**: `resolver.py:1745-1746`; `slice_queue_claim.py:240`; `_NO_CANDIDATES_PLACEHOLDER` writer:614.
- **Proposed fix**: Add empty-queue + CRLF as explicit TF-1 rows; execute the discriminator against them at build (quote command + output per APED-1).
- **Builder draft**: ACCEPTED-FIXED (plan) + ACCEPTED-PENDING (build) — added empty-baseline + CRLF + trailing-space-heading TF-1 rows; APED-1 execution at /build-slice.

## Dimensions checked
- [x] Unfounded assumptions — M2 (nil-harm contradicted by the write+commit sequence); m1 (user-gate override absorbed without ratification)
- [x] Missing edge cases — M1 (heading-survives/claim-only-on-baseline never STOPs); m3 (empty-baseline + CRLF must not false-STOP); parallel-session read of the transiently-committed truncated queue (M2)
- [x] Over-engineering — M3 (`_RENDERED_FIELD_LABELS` claims SSoT but is a third parallel copy unless wired into `_format_entry`)
- [x] Under-engineering — M1 (AC-1 "fail-closed on claim-loss-by-corruption" has no design element for the heading-survives sub-case)
- [x] Contract gaps — M3's label-contract pin; STOP error model reuses `_SoftResolutionError(reason, UNKNOWN)` + caller translation `:373-381`, unchanged + adequate
- [x] Security — none; cooperative-not-adversarial per ADR-067 (risk-register.md:419/437); no new input-trust/authz/secret surface
- [x] Drift from vault — none; ADR-077 correctly narrows-not-retires R-24, mirrors ADR-076/R-23, preserves slice-082 M2/ADR-074 warn-not-STOP happy path. MEPD-1 changelog obligation (behavior change) flagged in ADR-077 — verify build discharges versioned-entry + PMI-1 bump (tools/** surface)
- [x] Web-known issues — none novel; git `show :N:<path>` returns a complete staged blob (no partial-read class), reinforcing R-24's low likelihood (truncation requires a genuinely-committed corrupt queue). Sources: git-scm rebase docs; resolving-conflicts-during-rebase
- [x] Cross-cutting conformance — APED-1 (m3 executed battery required at build, esp. empty-baseline + CRLF); MEPD-1 (Dim 7); FBCD-1 (verify "5 field labels" byte-identical across AC-5/design/ADR-077); PTFCD-1/PTFFD-1 (verify cited TF-1 test paths/functions exist at strict-pre-finish)

## Triage

**Triaged by**: user
**Date**: 2026-05-30
**Final verdict**: NEEDS-FIXES

Reconciles BOTH passes (critique.md first Critic + critique-review.md meta-Critic). User ratified at TRI-1: **m1 → Option 4** (orphan-gated); **M1 → (a) document as residual** (NOT (b) close-it).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | DEFERRED | User ratified **(a) document as residual**. The claim-only-on-a-truncated-baseline case (invisible to merged_claims) is carried as a named R-24 residual, NOT closed — doubly-rare precondition at low/low; the meta-Critic's proposed per-claim (b) mechanism was also flawed (false-STOPs the insert-new overlay path). ADR-077/design/mission reconciled to Option-4-orphan-gated. |
| M2 | Major | ACCEPTED-FIXED | Harm model corrected in ADR-077 §Context/§Consequences + design.md — commits a transiently-corrupt queue, eventually-consistent self-heal, not nil-harm. |
| M3 | Major | ACCEPTED-PENDING | Design requires `_format_entry` to render FROM `_RENDERED_FIELD_LABELS` + a render-parity pin + a note on the existing `slice_queue_claim` prefixes; code + pin land at /build-slice. |
| m1 | Minor | ACCEPTED-FIXED | User ratified **Option 4**; ADR-077 §Decision finalized (orphan-on-well-formed WARN); (b) overrides Option-4 only for the no-claim-loss tail-truncation case (documented). |
| m2 | Minor | ACCEPTED-FIXED | ≤10-block bound + re-review-if-cap-lifted note added to design.md. |
| m3 | Minor | ACCEPTED-PENDING | TF-1 rows added (empty/placeholder baseline not-suspect; CRLF + trailing-space heading); APED-1 executed battery at /build-slice. |
| m-add-1 | Minor | ACCEPTED-FIXED | VAULT_CLAIM sibling truncation exposure recorded as an explicit deferred residual in ADR-077 §Consequences + design.md residuals (queue-candidate nominee). |
| m-add-2 | Minor | ACCEPTED-FIXED | MEPD-1 determination = **EXCLUDE** per the slice-082/084 risk-narrowing-fix-with-ADR-no-new-RULE-ID precedent (no changelog/VERSION/PMI-1 bump; in-place edit, inventory unchanged); recorded in ADR-077 + a pre-finish gate row so it's gated, not skipped. |
