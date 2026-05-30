# Reflection: Slice 084 harden-pcr-2a-clock-skew-winner

**Date**: 2026-05-30
**Shipped**: YES

## Validated
- Resolver-now future-dating is a sound, *available* skew signal — validated by the 13-row APED-1 battery: future stamps caught, past stamps resolve, all from a single injectable trusted clock. (Confirmed the design rationale that git-commit-date and Claim-seq are both non-signals.)
- The Step 2.5 placement (after `_select_timestamp_winner`, before Step 3 overlay) mutates no rebase state on a skew-STOP — validated by `test_suspicious_ordering_returns_stop_with_skew_reason` (STOP returns before any `_git_show_stage`/write, so no `tmp_path` rebase staging is even needed for the suspicious case).
- "No skill edit required" held — `skills/commit-slice/SKILL.md:190` already routes a `VAULT_CLAIM` STOP to SOAD-1; the code-Critic independently re-verified `resolve_vault_claim_conflict` returns `conflict_class=VAULT_CLAIM` on the skew-STOP. Single-file blast radius as the slice-queue predicted.
- Happy-path strict-newer preserved bit-for-bit — 95-test PCR regression + the APPLIED integration test; every existing dispatch-site caller (omitting `now`) is unaffected because real-now defaults and 2026 fixture stamps are historically-past.

## Corrected
- design.md / ADR-076 self-corrected mid-pipeline (no post-ship vault edit needed): the design-Critic's **B2 `Z`→`+00:00` fix was itself defective** — shipped case-sensitive (`endswith("Z")`), so a valid lowercase-`z` past stamp fail-closed STOPped (code-Critic M1). Corrected in-slice to `raw[-1:] in ("Z","z")`.
- The `# B2` comment over-claimed the gate was "version-independent" — true only for the `Z` token, NOT the broader `fromisoformat` acceptance surface (offset-no-colon / space-separated parse on 3.11+ but `ValueError` on the 3.10 floor; code-Critic M2). Corrected the comment to scope the claim + document that pre-3.11 fail-closes on relaxed forms (the safe direction).
- (No ADR superseded; no risk-register status flip — see Discovered for the R-23 narrowing.)

## Discovered
- **R-23 is NARROWED, not retired** — the future-dated-winner sub-case is now caught/escalated, but the **staler-but-past wrong-winner case** (an ahead-clock winner whose inflated stamp still precedes merge-time by less than the merge delay) is **fundamentally undetectable from a single trusted clock**. Full retirement would require a shared counter (rejected — not cross-machine comparable pre-merge) or routing *all* VAULT_CLAIM resolutions through PCR-2b adjudication (defeats PCR-2a auto-resolution). R-23 stays **open (downgraded)** with this residual recorded — see `risk-register.md` R-23 update.
- **ISO-8601 timestamp parsing is a multi-trap class**: `datetime.fromisoformat` (a) parses offset-less strings as *naive* (then `naive > aware` raises `TypeError`), (b) is case-sensitive to the user-supplied `Z`/`z` normalization, and (c) has a 3.10-vs-3.11 acceptance split. All three surfaced in ONE ~10-line helper. Impact: any future code parsing external timestamps should treat these as a checklist. Build-check promotion candidate (see Step 5b).
- The slice produced its shippability entry (row 90) at *build* time (BC-PROJ-7 discipline), not at /reflect Step 5.3 — so Step 5.3 is already discharged; no duplicate row added.

## Deferred
- **Staler-but-past skew detection** — undetectable from one clock; deferred indefinitely as the R-23 open residual. Only a shared-counter or always-adjudicate redesign could close it; neither is justified at low/low.
- **`add-claim-sequence-number-for-clock-skew-detection`** queue candidate — effectively retired-as-rejected by this slice's premise (per-machine seq not cross-machine comparable); should be dropped from the queue at next `/slice` regeneration.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` (all ACCEPTED-FIXED) + `critique-review.md` (EXTEND) + `code-review.md` (FINDINGS, all ADDRESSED-IN-SLICE) + reality observed at build/validate:

- **Design-Critic** B1 (naive crash): **VALIDATED** — executing the corpus confirmed the offset-less `TypeError` would fire mid-rebase; fix verified.
- B2 (Z on 3.10 floor): **VALIDATED** — but the *fix it prompted* was incomplete (see code-Critic M1/M2 below). The finding was right; the Builder's fix was a fresh defect.
- M1 (retired→narrowed): **VALIDATED** — the honesty reframe held; R-23 demonstrably narrows not retires.
- M2 (resolver-now trust by fiat): **VALIDATED** — documented assumption is the correct bound.
- m1/m2 (boundary tests / FBCD-1): **VALIDATED**.
- **Meta-Critic** m-add-1 (dead `loser` param) + m-add-2 (audit `now` render): **VALIDATED** — both real, both fixed; the meta-Critic's signature/serialization-hygiene lens paid off.
- **Code-Critic** M1 (lowercase `z`), M2 (`fromisoformat` cross-version + docstring over-claim), m1 (dead `diag`), m2 (build-log drift), m3 (corpus gaps): **all VALIDATED** — APED-1 execution against an adversarial corpus surfaced two real defects (M1 a genuine false-positive) that reading the design could not.

**Missed by Critic**: the design-Critic + meta-Critic (reading design.md) MISSED that the B2 `Z`-fix would ship case-sensitive and that the version-divergence was broader than the `Z` token. Caught only by the code-Critic *executing* the matcher. NOT a true escape — the in-loop code-Critic caught it before validate — but a clear instance of the design-stage stack's structural blind spot on executable-matcher behavior.

**Pattern**: **N+1 reinforcement of two standing patterns, fused**: (1) "a Critic's own fix is a fresh claim" — the design-Critic's B2 fix introduced M1/M2; (2) regex/parser-APED-1 / BC-PROJ-13 — a newly-minted parser's content-shape behavior is caught only by the code-Critic running it against an adversarial corpus in BOTH directions. Here the *same finding family* (timestamp parsing) propagated design-Critic → defective-fix → code-Critic-catch. The 3-Critic stack's complementarity held strongly: design caught the class, code caught the fix's defect. Do NOT collapse the stack.

## Lessons for next slice
- **A Critic-prompted fix to a parser/matcher is itself a parser/matcher claim — run the APED-1 corpus against the FIX, not just the original.** The B2 `Z` fix shipped case-sensitive; only executing lowercase-`z` caught it. (Reinforces BC-PROJ-13; candidate to sharpen the design-Critic prompt to demand corpus-execution of any proposed normalization.)
- **`datetime.fromisoformat` is a three-trap function** (naive-parse, `Z`/`z` case, 3.10/3.11 acceptance) — treat ISO-8601 parsing as a checklist, never a one-liner. Build-check promotion candidate.
- **Undetectable-by-design residuals are legitimate slice outcomes** — narrowing a low/low risk to its detectable sub-case + honestly documenting the open residual beats forcing a false "retired". The M1 reframe is the model.
- Queue hygiene: drop `add-claim-sequence-number-for-clock-skew-detection` at next `/slice` (rejected-as-premise).

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-23 narrowed: added a slice-084 partial-mitigation note + the staler-but-past open residual; Status stays `open` (downgraded, NOT retired).
- This slice's [[design.md]] + [[ADR-076]] — already carry the post-/critique + post-/code-review corrections (no further edit needed; build-log + code-review.md record the deltas).
- [[shippability.md]] — row 90 (added at build per BC-PROJ-7; SRSC-1 89/89).
- (No ADR superseded; no methodology-changelog/VERSION bump — MEPD-1 EXCLUDE per ADR-076.)
