# Reflection: Slice 092 fix-stranded-audit-branchless-blindspot

**Date**: 2026-05-31
**Shipped**: YES

## Validated
- **B2 dedup-key construction** (design §Dedup design) — `seen_keys = {b[len("slice/"):] for b in worktree_branches} | {f"{num}-{name}" for bare_tuples}` is correct against the real `WorktreeInfo` shape. Validated three ways: (1) the non-vacuous 4n unit test, (2) a **mutation proof** (swapping to the `wt.slice_name`-bare-name mis-key made 4n FAIL `2==1`, reverted), (3) the code-Critic independently re-deriving the key against `pulse_worktree_resolver.py:319`.
- **Context-2 self-dedup** (design §Self-surfacing) — validated LIVE: `stranded_slice_audit --repo-root .` from the worktree reported slice/092 (and a concurrent slice/093) each EXACTLY ONCE via the worktree branch, **zero `branchless-in-flight` entries** — the invoking tree's own foldered+branched slice is correctly suppressed.
- **Never-halt invariant** (ADR-084) — `BRANCHLESS_IN_FLIGHT ∉ _HALT_CLASSES`; `compute_status` unchanged; informational entries keep status `clean` on both synthetic (4j) and the real multi-slice tree.
- **Terminal-folder skip** — production vocab `stage: complete` / `next-action: none (slice complete)` not mis-surfaced (4l).
- **Fail-open edges** — absent/unreadable/stage-less milestone + stray dirs + archive all skipped (4m/4o), no raise.

## Corrected
- None substantive. The design pre-stated the implementation accurately (the dogfooding property: this `/slice`→`/design` run produced the very branchless folder the fix surfaces). One **benign naming note** (not a correction): the helper parameter is `seen_keys` where design prose said "the full `slice/*` ref set" — same semantics, internal name only; recorded in `drift-log.md`.

## Discovered
- **Parallel-slice branch-staleness** (added to risk register as [[R-33]]) — a slice worktree branched off pre-sibling-merge master shows non-regression full-suite failures at the `/build-slice` pre-finish gate: slice-092 (off `68a7817`) was missing slice-091's merged test file + an out-of-band triage/adopt template edit, producing 3 FAILs that all pass on master. Impact for next slices: sync master into the parallel branch BEFORE the pre-finish full-suite, or expect sibling-absence failures until `/commit-slice --merge`. Mitigated this slice by merge `b88d739` (disjoint radii → one additive `shippability.md` row-append conflict, resolved keep-both). Candidate methodology refinement (document or auto-sync at the gate).
- **The classifier's own real-artifact run is the best multi-parallel-slice validation** — a concurrent `slice/093-add-external-vault-support` worktree appeared mid-validation; the tool classified TWO live parallel worktree'd slices correctly (both informational `in-progress`, neither double-reported). Got this coverage "for free" from the live tree.

## Deferred
- ADR-084 §Consequences residuals (out of scope, accepted — cooperative-model scope): (a) a branchless folder living in a *different* worktree than the invoking one is not cross-scanned; (b) an archived-but-never-branched folder (`archive/slice-NNN/` with no `slice/*` ref) is surfaced by neither pass. Lands in: backlog (only if a real need surfaces; the cooperative model assumes archival follows merge).

## Critic calibration

Per TRI-1, scored against the `critique.md` §Triage dispositions + reality observed in build/validate:

- **B1** (self-surfacing): **VALIDATED** — ACCEPTED-FIXED (design+ADR disambiguation) + ACCEPTED-PENDING (4n). The real-artifact run confirmed the three runtime contexts behave as documented; context-2 dedup is genuine, not assumed.
- **B2** (dedup key mis-key vs real `WorktreeInfo`): **VALIDATED** — ACCEPTED-FIXED. The mutation proof + code-Critic re-derivation confirmed the `wt.slice_name`-alone key would double-report; the pinned construction is correct. The single highest-value finding of the slice.
- **M1** (`/pulse` closed-enumeration render gap): **VALIDATED** — ACCEPTED-PENDING applied. The "reused unchanged" claim was provably false; render path + `test_pulse_skill_stranded_signal.py` pin landed, OSDG-1 green.
- **M2** (under-pinned repro): **VALIDATED** — ACCEPTED-PENDING applied. 4j–4o WRITTEN-FAILING before impl + `assert len(...)==1` + production terminal vocab.
- **m1** (`vault_state` prefix unpinned): **VALIDATED** — ACCEPTED-PENDING applied (4j `startswith("folder:")` + stage-named pin).
- **m2** (ADR residual asymmetry): **VALIDATED** — ACCEPTED-FIXED (ADR §Consequences self-folder rationale).
- **M-add-1** (meta-Critic; 4n risks passing vacuously): **VALIDATED** — the concern was real and is the single most important catch of the dual stack: without it, the strongest dedup invariant would have shipped unverified. Resolved by invoking `classify_branches` from the worktree + the mutation proof. *Calibration nuance*: the meta-Critic's concrete example ("slice-091 has a worktree + branch") was factually wrong at the time (slice-091 was a parked branchless scaffold then) — meta-Critic was **right on substance, wrong on a contingent example**. Net: trust the substance, sanity-check cited examples.
- **m-add-2** (meta-Critic; stage-None → `folder:None`): **VALIDATED** — ACCEPTED-FIXED (skip stage-None) + 4o pin.

**code-Critic (`/code-review`)**: FINDINGS minor-only (0 blockers, 0 majors; m1 accepted-no-change, m2 applied — comment). Appropriate for a small, well-designed diff the dual design-Critic stack had already hardened; the code-Critic added value as defense-in-depth by independently re-verifying B2 on the real tree.

**Missed by Critic**: the **parallel-branch-staleness full-suite interaction** (R-33) was flagged by NEITHER the design-Critic NOR the code-Critic — it surfaced only at the `/build-slice` pre-finish full-suite. Neither Critic reviews the slice branch's *currency vs master* (design-Critic reads design+ADRs; code-Critic reads the slice diff). This is a process/integration dimension outside both Critics' scope. Candidate for `/critic-calibrate` (or a methodology note) — but arguably belongs to the pre-finish gate's definition, not a Critic prompt.

**Pattern**: the dual design-Critic (critique + critique-review) was highly effective on this cross-cutting tooling slice — 8 findings, ALL VALID, zero FALSE-ALARM; the meta-Critic caught the 4n-vacuity that would otherwise have shipped an unverified dedup. The code-Critic then re-verified the load-bearing B2 dedup on the real tree. N+1 evidence (continuing the slices 1-9 record) for voluntary/mandatory Critic on in-house methodology surfaces.

## Lessons for next slice
- **Sync a parallel slice branch with master before the pre-finish full-suite** (R-33). A branch cut before a sibling merged will show sibling-absence FAILs that are NOT regressions — `git merge master` (disjoint radii → additive conflicts only) makes the gate reflect integration reality and de-risks `/commit-slice --merge`.
- **Prove non-vacuity of a guard test by mutation** — when a test exists to pin a dedup/guard, briefly break the guard and confirm the test fails, then revert. The meta-Critic's M-add-1 was exactly this; the mutation proof turned "looks pinned" into "is pinned."
- **Trust meta-Critic substance over its contingent examples** — M-add-1's example was stale but its concern was the slice's most valuable catch.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-31 open→mitigating (ADR-084 mitigation + residuals); added [[R-33]] (parallel-branch-staleness, mitigating)
- [[decisions/ADR-084]] — finalized (accepted) at /design-slice/critique; no supersession this slice
- This slice's [[design.md]] / [[mission-brief.md]] — TF-1 table 8/8 PASSING; no design correction (impl matched design)
- [[drift-log.md]] — slice-092 full-mode CLEAN entry (DCE-1 trigger)
- [[shippability.md]] — row #99 (branchless repro) already added by `/repro`; merge resolved row 98/99/100 ordering (slice-091 + slice-092)

## BCR-1 round-trip
- No-op: no `diagnose-out/backlog.md` present, and neither mission-brief.md nor reflection.md carries a `**Closes:** SC-NNN` sentinel. Nothing to round-trip.
