# Design: Slice 085 harden-pcr-1-truncated-baseline

**Date**: 2026-05-30
**Mode**: Standard

## What's new

- A baseline structural-integrity discriminator wired into PCR-1's SOFT equivalence guard (`_verify_soft_equivalence`, Invariant #1 orphan-claim branch) in `tools/parallel_conflict_resolver.py`: when a **claimed** candidate is dropped from the baseline AND the baseline is **truncation-shaped**, escalate the existing WARN-only `cross-stage-claim-drop` to a fail-closed **STOP** (claim-loss-by-corruption — the exact R-24 hole). Well-formed baselines keep the WARN-only churn semantics (no false-STOP).
- A new private helper `_baseline_is_truncation_shaped(queue_text) -> tuple[bool, str | None]` in `tools/parallel_conflict_resolver.py` that detects the truncation signature **tail-specifically** (revised per /critique M1 — NOT a whole-file completeness scan): the **last** `### <name>` block is incomplete (missing one or more of the 5 canonical on-disk PSQ-1 field labels) and/or the file does not end at a clean block boundary. A truncation cuts the tail; a complete-but-noncanonical block earlier in the file (legacy format / hand-edit) does NOT trip the gate (bounds false-STOP, matches the "truncation-shaped" name + the user's gate-breadth pick). The scan is bounded by the top-10 queue size (per /critique m2: ≤10 blocks × 5 labels per SOFT merge — trivial; re-review if a future PSQ extension lifts the top-10 cap). The helper MUST normalize CRLF (mirroring `parse_queue_text` at `slice_queue_claim.py:240`) and MUST treat an empty / `_(no candidates)_`-placeholder baseline as NOT truncation-shaped (per /critique m3 — else a legitimate empty queue false-STOPs).
- A new module constant `_RENDERED_FIELD_LABELS` (the 5 on-disk markdown field labels) in `tools/slice_queue_writer.py`, imported by the resolver. The labels are currently inline f-strings at `tools/slice_queue_writer.py:634-638` (`- **Source:**` / `- **Blast-radius:**` / `- **Parallel-safety:**` / `- **Effort:**` / `- **Risk-retired:**`). To be a **genuine** single source of truth (per /critique M3), the writer's `_format_entry` (`:631-639`) MUST render FROM the constant (not keep a parallel copy), a test pins that the emitted labels equal `_RENDERED_FIELD_LABELS` (mirrors `test_psq_2_claim_machinery.py`'s on-disk-contract pin), and design notes the relationship to the EXISTING `slice_queue_claim.py:105-117` prefix constants (`_RISK_RETIRED_PREFIX` etc.) so no fourth copy is added. `Claimed-by`/`Claimed-at` lines (`:647-648`) are NOT among the 5.
- A best-effort audit-log STOP entry variant for the claim-loss-by-corruption STOP (mirrors `_append_equivalence_stop_audit` / `_append_skew_stop_audit`).
- Test coverage in `tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py`.

## What's reused

- `tools/parallel_conflict_resolver.py::_verify_soft_equivalence` — the SOFT equivalence guard (slice-082 / [[ADR-074]]) whose Invariant #1 orphan-claim exemption (lines 1755–1793) is the precise gap being closed.
- `_git_show_stage`, `_extract_claim_diff`, `_merge_claim_dicts` — existing helpers; the discriminator reuses the already-computed `baseline_q` / `merged_q` / `discarded_stage_headings`.
- `tools/slice_queue_writer.py` — the on-disk field-label contract source ([[slice-067-add-psq-1-parallel-slice-queue]] / PSQ-1).
- [[ADR-074]] (PCR-1 SOFT equivalence guard), [[ADR-069]] (PCR taxonomy), [[ADR-067]] (cooperative threat model), [[ADR-076]] (slice-084 partial-mitigation-with-residual precedent for R-23).
- Risk register [[risk-register#R-24]].

## The reframing that drives the scope (read first)

PCR-1's SOFT path regenerates `slice-queue.md` by taking the rebase-target baseline (stage 3) **verbatim** and overlaying merged claims (`_regen_slice_queue` / `_overlay_claims_on_queue_text`).

Two distinct durability facts (corrected per /critique B1 — the earlier draft wrongly called the whole condition "self-healing"):
- The candidate **list** is ephemeral — `/slice` regenerates the full top-10 on every run, so a truncation that drops only *unclaimed* candidates **does self-heal** (next `/slice` restores the list).
- A **claim** (`Claimed-by`/`Claimed-at`, PSQ-2 ownership) does **NOT** self-heal. `_overlay_claims_on_queue_text` (`tools/parallel_conflict_resolver.py:941-1032`) only emits a claim for a candidate that still has a `### ` heading in the baseline; a claimed candidate truncated *out* of the baseline is **silently dropped** (lines 1017-1018) and the short queue would be written (line 392) + committed. The loser's ownership marker is gone until a human notices the stderr WARN.

Consequence: the only **non-self-healing** harm a truncated/corrupt baseline causes is **claim-loss** — which is exactly why claim-loss-by-corruption must STOP. **TRI-1 ratified Option 4** (m1): a truncation-shaped baseline that drops a *provable* claim (orphan branch) → STOP; a no-claim-loss truncation → auto-merge+WARN (the list self-heals; M2 caveat: a transiently-corrupt short queue is committed, self-healing at next `/slice`). The invisible-claim **M1 case is a documented residual** (disposition (a), ratified) — see [[ADR-077]] §Decision.

## Components touched

### `tools/parallel_conflict_resolver.py` (modified)
- **Responsibility**: PCR-1/2a/2b parallel-conflict diagnosis + classification + (SOFT/VAULT_CLAIM) auto-resolution at `/commit-slice --merge` rebase time.
- **Change (ratified — Option 4, orphan-gated)**: (1) new `_baseline_is_truncation_shaped` helper (tail-specific: last block missing ≥1 of 5 labels OR file not ending at a clean block boundary; CRLF-normalized; empty/placeholder → not suspect); (2) in `_verify_soft_equivalence` Invariant #1's **orphan-claim branch**, when a claimed candidate is dropped: baseline truncation-shaped → `_fail(...)` (STOP via `_SoftResolutionError(reason, ConflictClass.UNKNOWN)`, audit first); well-formed → existing WARN; (3) no provable claim-drop (orphan branch empty) → auto-merge (Option 4). The M1 invisible-claim case is a **documented residual** (disposition (a)); (b) was declined — see ADR-077 §Decision.
- **Key interactions**: imports `_RENDERED_FIELD_LABELS` from `tools/slice_queue_writer.py`; reuses `_append_equivalence_stop_audit` for the STOP audit row.

### `tools/slice_queue_writer.py` (modified)
- **Responsibility**: PSQ-1 queue writer — renders the canonical `slice-queue.md` candidate blocks.
- **Change**: extract the 5 on-disk field labels (currently inline f-strings at lines 634-638) into a module constant `_RENDERED_FIELD_LABELS: tuple[str, ...]` and render the candidate block from it (so writer + reader share one source of truth).
- **Key interactions**: consumed by `parallel_conflict_resolver._baseline_is_truncation_shaped`.

## Contracts added or changed

None — no endpoints/events/CLI-surface changes. The `parallel_conflict_resolver` CLI (`--resolve-soft`) behavior is unchanged except that a previously-WARN-then-AUTO_MERGE claim-loss-on-truncated-baseline now returns `action="STOP"`. This is a **behavior change** (a SOFT merge acceptable yesterday is refused today) → recorded via [[ADR-077]] + the R-24 `**Narrowed:**` annotation; **MEPD-1 EXCLUDE** per ADR-077 §Consequences (risk-narrowing fix-slice, no new RULE-ID, in-place edit to the already-manifested `parallel_conflict_resolver.py` — NO methodology-changelog entry, NO VERSION bump, NO PMI-1 manifest bump). _(Corrected per /code-review M2 — the earlier "methodology-changelog entry + ADR" clause was a stale draft remnant predating the /critique-review m-add-2 EXCLUDE determination.)_

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1**. This slice introduces no new *module/file* — it adds a private helper + a constant to existing modules and wires them into an existing call path. Zero-row matrix (clean).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| (none — helper `_baseline_is_truncation_shaped` added to existing `parallel_conflict_resolver.py`) | `_verify_soft_equivalence` (same module) | `tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py` | `no new module — intra-module helper wired into existing _verify_soft_equivalence call path — rationale: WIRE-1 governs new files; this is an additive helper + constant on existing modules with direct test coverage` |

## Decisions made (ADRs)

- [[ADR-077]] — Scope the PCR-1 baseline-integrity gate to **claim-loss-by-corruption** (discriminate the orphan-claim exemption by baseline truncation-shape), NOT a blanket truncation STOP — reversibility: **cheap** (one branch + one helper; revert restores WARN-only).

## Authorization model for this slice

N/A — no auth surface. Cooperative-not-adversarial threat model carried from [[ADR-067]]: not a security boundary (a local actor can edit the queue directly regardless). The guard protects *cooperating* sessions from a *corrupt committed baseline*, not from malice.

## Error model for this slice

- **New STOP (Option 4, orphan-gated — RATIFIED)**: in `_verify_soft_equivalence` Invariant #1's orphan-claim branch (`claimed_names - baseline_headings`), when a claimed candidate is dropped from the baseline AND `_baseline_is_truncation_shaped(baseline)` → `_fail(...)` → `_SoftResolutionError(reason, ConflictClass.UNKNOWN)` → `resolve_soft_conflict` returns `ResolutionResult(action="STOP", conflict_class=UNKNOWN, ...)`. NO writes (atomicity: runs before any `write_text`/`git add`/`git rebase --continue`, `:374` before the write loop `:389-392`). A best-effort audit row is appended first. The `/commit-slice` SKILL.md SOAD-1 STOP fall-through surfaces it for hand-resolution.
- **Pre-existing STOP preserved (corrected per /critique M1 — must NOT regress)**: the `:1775-1783` claimed-WITH-heading loop STOPs when a candidate claimed in `merged_claims` with a surviving baseline heading does NOT carry its claim in the **regenerated output** — the **overlay-silent-drop** case (a malformed block whose `Risk-retired` pivot is missing so `_overlay_claims_on_queue_text` couldn't re-emit the claim). It does NOT catch "the baseline's claim *lines* were truncated" by itself, because `merged_claims` re-applies the claim from the *other* stage. This slice does NOT touch that loop; AC-4(a) asserts the overlay-silent-drop STOP stays unchanged. (My earlier placeholder claim that `:1775-1783` catches claim-line-truncation was wrong — see M1.)
- **M1 case — documented residual (disposition (a), RATIFIED)**: a claim that existed ONLY on the truncated baseline branch (claim lines cut) is invisible to `merged_claims` → never enters `claimed_names` or the orphan branch → NOT detected. Carried as a named R-24 residual, NOT closed. **(b) declined** at low/low (doubly-rare precondition); the meta-Critic's proposed per-claim (b) mechanism was anyway flawed (it would false-STOP the normal insert-new overlay path — see ADR-077 §Decision). Distinct from `Claimed-by` *value-garbled* (b-ii), genuinely out of scope.
- **Fail-closed on uncertainty** (must-not-defer): if `_baseline_is_truncation_shaped` itself cannot parse the baseline (raises), treat as suspect → STOP in the claim-threatened branch (never silently auto-merge an uncheckable baseline that already dropped a claim).
- **Preserved WARN / auto-merge (Option 4 happy path)**: an orphan claim dropped from a **well-formed** baseline → existing `cross-stage-claim-drop` stderr WARN + auto-merge (legitimate top-10 churn, no false-STOP — AC-2); a no-provable-claim-drop truncation → auto-merge (AC-3). **M2 caveat**: a no-claim-loss truncation auto-merge commits a transiently-corrupt (short) queue that self-heals at the next `/slice` — accepted at low/low (list regenerable; no durable claim lost).
- **Documented residuals** (per [[ADR-077]], mirroring [[ADR-076]]/R-23): R-24 is **narrowed, not retired**. Detected (STOP): claim-loss where a claimed candidate's whole block is truncated out of a tail-truncation-shaped baseline (orphan-branch-gated, Option 4). Residuals (undetected, low/low): (i) a baseline truncated **exactly at a clean block boundary** (last surviving block complete) → indistinguishable from churn; (ii) the **M1 case** — a claim only on the truncated branch, claim lines cut, invisible to `merged_claims` (disposition (a): documented, not closed); (iii) **VAULT_CLAIM sibling path** (per /critique-review m-add-1) — `resolve_vault_claim_conflict` carries the same baseline-truncation claim-loss exposure (no `_verify_soft_equivalence`, no truncation check), OUT of scope here, deferred to a future PCR-2a hardening.
