# Design: Slice 082 harden-pcr-1-soft-regen-corner-case

**Date**: 2026-05-29
**Mode**: Standard

## What's new

- A **SOFT equivalence guard** in `tools/parallel_conflict_resolver.py`: a new private predicate `_verify_soft_equivalence(...)` that sits between the SOFT helpers producing `pending_writes` and the commit phase in `resolve_soft_conflict`. It re-parses the *pending* regenerated content and asserts it is in a deterministic equivalence class against the input-branch (stage-2 / stage-3) versions. When equivalence cannot be proven → fail-closed `action="STOP"` with no writes (atomicity preserved, since the commit/stage/rebase phase hasn't run yet).
- The guard raises the **existing** `_SoftResolutionError(message, ConflictClass.UNKNOWN)` on an unprovable invariant (m1 ACCEPTED-FIXED — NO new exception class). This routes through the already-present `except _SoftResolutionError` clause in `resolve_soft_conflict` (`:288-300`) with **zero except-ladder change**, and the existing handler already returns `action="STOP", regenerated_files=()` with no writes. (A new `_SoftEquivalenceError` sibling was rejected: per the catch-order-invariant comment at `:371-381` siblings inherit from `Exception`, so a new class would need its own `except` clause and risks a silent fall-through if the Builder forgets it — higher blast-radius for no benefit, contradicting ADR-074's reversibility=cheap.)
- An **equivalence-guard STOP audit entry**: the guard-triggered STOP appends a `## Soft-conflict resolution (equivalence-guard STOP) - <ISO-8601 UTC>` section to `architecture/parallel-conflict-resolution-log.md` recording the divergence reason (best-effort, mirrors the existing APPLIED-path audit append).
- A new test module `tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py` — APED-1 empirical battery (executes the guard against real tmp-repo fixtures, not reasoned-about).

## What's reused

- `tools/parallel_conflict_resolver.py::resolve_soft_conflict` — the SOFT dispatch + stage-then-commit atomicity loop the guard hooks into (see `path` lines 273–320).
- `_regen_slice_queue` / `_overlay_claims_on_queue_text` / `_merge_claim_dicts` / `_extract_claim_diff` — the queue-overlay path whose silent-drop corner cases the guard backstops.
- `_merge_shippability` / `_parse_shippability_rows` — the shippability row-union path.
- `_git_show_stage` / `_extract_claim_diff` / `_merge_claim_dicts` — re-derive `merged_claims` + stage texts for invariant #1 (see §"How the guard obtains its inputs"); `tools.slice_queue_claim.parse_queue_text` — read claim presence in the pending output. (`_parse_queue_candidates_for_replacement` is NOT used by the guard — it strips claim metadata; B1.)
- `_append_audit_log` / `_AUDIT_LOG_PATH` — the audit-trail append the guard-STOP extends.
- [[decisions/ADR-069-mint-pcr-1-conflict-diagnostic-and-soft-regen]] — PCR-1, the rule being hardened.
- [[risk-register#R-21]] — the risk this slice retires (fix-class (b)).

## The corner case being closed (empirical anchor for R-21)

R-21 anticipates SOFT auto-regen emitting content semantically different from a manual-resolve baseline. Reading the current SOFT path surfaces two concrete *silent*-divergence vectors that fire **without** raising `_SoftResolutionError` (so today they pass straight to the commit phase):

1. **Queue malformed-block claim drop** (`_overlay_claims_on_queue_text`, `tools/parallel_conflict_resolver.py:830-841`): a candidate present in both `merged_claims` and the baseline queue text, but whose block is missing its `- **Risk-retired:**` line, has its claim metadata silently dropped — the code only emits a stderr warning and proceeds. A human merging both branches would preserve the claim.
2. **Shippability discarded-prelude drop** (`_merge_shippability`, `tools/parallel_conflict_resolver.py:1242`): `prelude_lines = prelude_3 if prelude_3 else prelude_2` keeps only the rebase-target stage's non-numbered lines. A non-numbered (prelude) line unique to stage-2 — e.g. a row whose first cell isn't a bare integer and so fails the `^\|\s*(\d+)\s*\|` row regex — is silently lost.

These are exactly the "structurally-valid but semantically-divergent" outputs R-21 names. AC-1's failing test reproduces vector 1 (and, charter permitting, vector 2).

## Components touched

### `tools/parallel_conflict_resolver.py` (modified)
- **Responsibility**: add a defense-in-depth equivalence gate to PCR-1's SOFT auto-regen so structurally-valid-but-semantically-divergent regen output fails closed to STOP instead of silently committing.
- **Lives at**: `tools/parallel_conflict_resolver.py` (modify `resolve_soft_conflict`; add `_verify_soft_equivalence` + verdict-signal class)
- **Key interactions**: invoked inside `resolve_soft_conflict` at the pinned call-site below (M3); **read-only** — it performs git-show reads and string parsing, never `write_text` / `git add`; raises `_SoftResolutionError(..., ConflictClass.UNKNOWN)` on an unprovable invariant (routed by the existing `except`); on STOP, appends an audit entry via `_append_audit_log`.

### Guard call-site (M3 ACCEPTED-FIXED — pinned, not "between … and …")
The guard runs **after** the `if not pending_writes: return STOP(...)` empty-check (`tools/parallel_conflict_resolver.py:302-308`) and **before** the `for out_path, content in pending_writes:` write loop (`:316-320`). Consequences this placement guarantees:
- It runs **only on the all-SOFT-helpers-succeeded path**. The `_VaultClaimDispatch` (`:280-287`) and `_SoftResolutionError` (`:288-300`) handlers `return` before reaching the guard, so a mid-loop dispatch/escalation never reaches it — no double-handling, and `diag.u_files` loop-order (git-status order, `:275`) is irrelevant because partial `pending_writes` only exist *inside* the `try`, and any exception returns before the post-loop region.
- Atomicity holds because the guard is purely read-only and sits strictly before the first `write_text` (`:319`) / `git add` (`:325`) / `git rebase --continue` (`:331`). A guard-STOP therefore mutates **no** tracked conflict state (the only side effect is the best-effort audit-log append; see Error model).

### How the guard obtains its inputs (B1 ACCEPTED-FIXED)
`_regen_slice_queue` returns only `(Path, str)` (`:666-727`) — `merged_claims` and `baseline_text` are computed inside it and discarded, and `_parse_queue_candidates_for_replacement` surfaces only `(name, parallel_safety, is_claimed)` (`:846-913`), NOT claim metadata. So the guard re-derives its inputs explicitly rather than from the field-stripping helpers:
- `text_2 = _git_show_stage(repo_root, 2, "architecture/slice-queue.md")`; `text_3 = _git_show_stage(repo_root, 3, ...)` (fresh reads, same as `_regen_slice_queue`).
- `claims_2, claims_3 = _extract_claim_diff(text_2, text_3)`; `merged_claims = _merge_claim_dicts(claims_2, claims_3)` (reuse the same derivation `_regen_slice_queue` used).
- `baseline_headings` = set of `### <name>` headings parsed directly from `baseline_text` (`text_3 if text_3 else text_2`) via a local `^### (.+)$` regex — NOT via `parse_queue_text` (which strips Parallel-safety) nor `_parse_queue_candidates_for_replacement` (no claim metadata).
- `pending_claims = parse_queue_text(<pending slice-queue text from pending_writes>)` — `parse_queue_text` IS the correct tool for reading *claim presence* in the pending output (it returns `claimed_by`/`claimed_at`; its only documented failure is `ClaimUsageError` on a partial claim block, which is itself a divergence → fail-closed STOP).

## The equivalence class (deterministic invariants the guard asserts)

The guard proves the pending content is equivalent to the inputs along three invariants; failure of any → STOP (fail-closed):

1. **Queue claim-preservation** — let `claimed_names = {name for name, d in merged_claims.items() if d.get("claimed_by")}` (M-add-1 ACCEPTED-FIXED — the domain is the **claimed** subset, NOT all `merged_claims` keys). Every name in `claimed_names` that is ALSO present as a `### <name>` heading in `baseline_text` MUST appear in `pending_claims` carrying its `claimed_by`. (Catches vector 1: the malformed-block drop emits the candidate heading but loses the claim — so it IS a `baseline_heading`, IS in `claimed_names`, but is ABSENT from `pending_claims` → STOP.)
   - *Why the domain MUST be the claimed subset (M-add-1)*: `merged_claims` is `_merge_claim_dicts(claims_2, claims_3)` (`:730-749`), which copies ALL entries from `_extract_claim_diff` → `parse_queue_text` — i.e. EVERY queue candidate, claimed AND **unclaimed** (unclaimed entries have no `claimed_by`). The `_overlay_claims_on_queue_text` overlay only emits `Claimed-by`/`Claimed-at` lines when both are truthy (`:810-821`), so an unclaimed candidate NEVER carries `claimed_by` in `pending_claims`. If invariant #1's domain were all `merged_claims` keys, every happy-path queue with even one unclaimed candidate (the normal case — the top-10 is mostly unclaimed) would false-STOP, **breaking AC-4** (byte-unchanged when equivalence holds). Restricting to `claimed_names` makes the guard transparent on the happy path. APED-1: the build battery MUST include a happy-path fixture with a MIX of claimed + unclaimed candidates asserting the guard does NOT STOP.
   - *Orphan-claim exemption + its bound (M2)*: a candidate in `merged_claims` but absent from `baseline_headings` is normally a **documented, expected** drop per ADR-069 / design.md L137 (the rebase-target's top-10 legitimately churned and the stale candidate fell off — the COMMON case in parallel work; promoting it to STOP would defeat the SOFT happy-path). **However**, the truncated/corrupt-baseline case (M2) — where `baseline_text` is itself incomplete and a candidate was lost not by legitimate churn but by corruption — is indistinguishable from legitimate churn at the name level. We do NOT STOP on cross-stage drops (that would false-STOP every legitimate top-10 churn), but we make them **non-silent**: when an orphan claim's candidate *had a `### heading` in the discarded stage* (i.e. it existed in one input and vanished from baseline), the guard emits a **loud audit-log warning** (`cross-stage-claim-drop: <name> present in stage-N, absent from baseline — verify baseline is not truncated`). The genuinely-corrupt-baseline residual remains a narrow, named R-21 residual scoped to PCR-2b's HARD path (registered at `/reflect`). *(M2 disposition: concern ACCEPTED; the Critic's literal proposed fix — STOP on cross-stage drop — was rejected because legitimate top-10 churn IS a cross-stage drop and is the common case; loud-audit-not-STOP is the happy-path-preserving remedy.)*
2. **Shippability row-completeness** — the set of numbered slice-rows in the pending output equals `set(numbered_2) | set(numbered_3)`; no numbered row dropped or duplicated. (Same-slice-number-different-content already escalates to HARD upstream at `:1232-1239`; this is the row-membership backstop.)
3. **Shippability prelude set-equality (M1 ACCEPTED-FIXED — now symmetric)** — the set of non-blank prelude lines is **equal across both stages**: `set(nonblank prelude_2) == set(nonblank prelude_3)`, and the pending output's non-blank prelude set equals that common set. This is symmetric (the original asymmetric "discarded-stage ⊆ output" check missed content-mutation that survived verbatim into the *kept* stage — M1). It catches vector 2 AND non-numbered row content-mutation in EITHER stage, including split-slice (`| 030C | … |`) / combined (`| 5,6 | … |`) rows that fall outside the `^\|\s*(\d+)\s*\|` numbered regex (`:1270`) and land in the prelude. **Tradeoff (locked)**: a benign cross-stage prelude difference (e.g. a hand-edited preamble count) → STOP. This is the correct fail-closed behavior for R-21 — a prelude that genuinely differs between branches is exactly an "equivalence-unclear" case fix-class (b) says to STOP on; better a STOP a human resolves than a silent wrong merge.

If the guard's own re-derivation/re-parse raises (e.g. `parse_queue_text` `ClaimUsageError` on a partial pending block, or `_git_show_stage` failure), that too is fail-closed → STOP (never proceed on an unreadable regen).

## Contracts added or changed

None. No CLI surface, endpoint, or public-function signature change. `_verify_soft_equivalence` is a file-private helper; `resolve_soft_conflict`'s public signature + return type (`ResolutionResult`) are unchanged. The guard only adds new STOP outcomes to an already-existing STOP-or-APPLIED contract.

## Data model deltas

None. No persisted schema change. The audit-log gains a new *section heading variant* (`(equivalence-guard STOP)`) but the log file is an append-only prose artifact, not a schema.

## Wiring matrix

Per **WIRE-1**. This slice introduces **no new module/file** in `tools/` or `src/` — the equivalence guard is a new private function inside the existing `tools/parallel_conflict_resolver.py`, and its sole consumer is `resolve_soft_conflict` in the same module. The new test module is the verification consumer.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(Zero-row matrix — no new modules introduced; the audit treats this as clean.)

## Decisions made (ADRs)

- [[ADR-074]] — Add a SOFT auto-regen equivalence guard to PCR-1 (R-21 fix-class (b)): regenerated SOFT content must be provably equivalent to both input branches along three invariants, else fail-closed STOP — reversibility: **cheap**

## Authorization model for this slice

Not applicable — `tools/parallel_conflict_resolver.py` is a local developer/CI tool invoked during `git rebase` conflict resolution. No multi-user authorization surface. (The slice touches an in-house methodology surface → Critic mandatory regardless of tier.)

## Error model for this slice

- **Guard-detected divergence** → raise `_SoftResolutionError("equivalence-guard: <which invariant> unprovable - <detail>", ConflictClass.UNKNOWN)`, caught by the existing `except` at `:288-300` which returns `ResolutionResult(action="STOP", conflict_class=UNKNOWN, regenerated_files=())`. No `write_text`, no `git add`, no `git rebase --continue`.
- **Guard re-derivation/re-parse failure** → same fail-closed STOP (treated as unprovable equivalence).
- **Scope of "repo state unmutated" (m2 ACCEPTED-FIXED)**: the must-not-defer "STOP leaves repo state unmutated" refers to **tracked git conflict state** — the U-files (`slice-queue.md` / `shippability.md`), the index, and the rebase-in-progress. The guard-STOP touches NONE of these. The one side effect is the **best-effort, non-blocking** append to `architecture/parallel-conflict-resolution-log.md` (a new section variant `## Soft-conflict resolution (equivalence-guard STOP) - <ts>`), which is explicitly EXCLUDED from the "unmutated" guarantee — consistent with the existing APPLIED-path best-effort audit contract (`:355-362`). Note the SOFT STOP paths today do NOT log (`_append_audit_log` runs only on APPLIED, `:356`); adding a guard-STOP log entry is new-but-intended behavior (AC-3). **Build-time check (m2 ACCEPTED-PENDING)**: grep `tests/` for any closed-set assertion over audit section headings before adding the third variant; if one exists, widen it in the same fix block.
- Existing `_SoftResolutionError` (HARD/UNKNOWN escalation) and `_VaultClaimDispatch` paths are **unchanged** — the guard runs only when those did NOT fire (i.e., the helpers produced pending content and the empty-check passed).
