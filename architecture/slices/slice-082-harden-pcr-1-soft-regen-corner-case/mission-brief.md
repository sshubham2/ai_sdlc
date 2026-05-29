# Slice 082: harden-pcr-1-soft-regen-corner-case

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-21 (SOFT auto-regen produces semantically-different content from manual-resolve baseline at a corner case) — top open risk, score 4, medium band
**Test-first**: true  (per TF-1 — the corner case is constructed as a failing test before the guard is written)
**Walking-skeleton**: false
**Exploratory-charter**: true  (per ETC-1 — R-21 explicitly states corner-case discovery is *empirical*; one timeboxed charter hunts the divergence case)

## Intent

PCR-1's SOFT auto-resolve (`tools/parallel_conflict_resolver.py`) silently regenerates `slice-queue.md` + `shippability.md` on a parallel-slice merge conflict. R-21 (the highest-scored open risk) anticipates a corner case where that auto-regen produces content semantically different from what a human-with-Critic-stack would have produced — a *silent wrong resolution*, the worst failure mode for a fail-closed pipeline. This slice closes R-21 by adding a structural **equivalence guard** to the SOFT path (R-21 candidate fix-class (b)): before committing the regenerated content, verify it is in a deterministic equivalence class against BOTH input-branch versions; when equivalence cannot be proven, fail-closed to `action="STOP"` (SOAD-1) instead of writing. The corner case becomes a loud STOP, never a silent divergence.

## Acceptance criteria

1. A failing regression test demonstrates the R-21 corner case: a SOFT-class conflict (both U-files in `{slice-queue.md, shippability.md}`) where the current `_regen_slice_queue` / `_merge_shippability` auto-regen emits content that semantically diverges from the manual-resolve baseline (a candidate, claim, or shippability row silently dropped / duplicated / reordered-beyond-contract that a Critic seeing both branches would have preserved). Test is RED before the fix.
2. A structural equivalence guard is added to the SOFT auto-resolution path: it verifies the regenerated content is in a deterministic equivalence class against both input-branch (stage-2 / stage-3) versions — no candidate/claim/shippability row silently lost, duplicated, or altered beyond the documented merge contract. When equivalence cannot be proven, it returns `action="STOP"` (fail-closed, SOAD-1) **without mutating repo state** (stage-then-commit atomicity preserved per ADR-069).
3. The AC-1 corner-case test now PASSES: the divergent case routes to STOP (not a silent wrong-resolution), and the event is recorded in `architecture/parallel-conflict-resolution-log.md` with a structured reason naming the equivalence-guard.
4. The canonical SOFT happy-path is preserved: the existing PCR-1 APED-1 battery + the 2-canonical-file auto-regen pass unchanged — when equivalence DOES hold, the guard is transparent (no behavioral change to the proven happy path).
5. A `shippability.md` row pins the equivalence guard (Command targets the new guard's test) so R-21's corner-class can never silently regress; R-21 is flipped to retired (or mitigating) at `/reflect` with empirical evidence.

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0)

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py | test_corner_case_soft_regen_diverges_from_baseline | PENDING |
| 2 | unit | tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py | test_equivalence_guard_stops_on_unprovable_equivalence | PENDING |
| 2 | unit | tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py | test_stop_leaves_repo_state_unmutated | PENDING |
| 3 | unit | tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py | test_guard_stop_logged_with_structured_reason | PENDING |
| 4 | unit | tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py | test_happy_path_equivalence_holds_guard_transparent | PENDING |

## Exploratory test charter

(per **ETC-1**, `methodology-changelog.md` v0.16.0)

| # | Mission | Timebox | Status | Findings |
|---|---------|---------|--------|----------|
| 1 | Explore SOFT auto-regen using adversarial `slice-queue.md` / `shippability.md` branch pairs (concurrent claim+drop, reordered candidates, near-duplicate rows, unicode/EOL-skewed cells) to find semantic-divergence cases the equivalence guard must catch | 60min | PENDING | — |

COMPLETED rows MUST have non-empty Findings. DEFERRED rows MUST carry a rationale.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Corner case demonstrated | Run `pytest tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py::test_corner_case_soft_regen_diverges_from_baseline` at HEAD-before-fix → RED with the divergence assertion |
| 2 | Equivalence guard fails-closed | Run the guard against the corner-case fixture → `ResolutionResult(action="STOP", ...)`; assert repo working tree + index unchanged (`git status` byte-identical pre/post) |
| 3 | STOP logged | Inspect `architecture/parallel-conflict-resolution-log.md` after a guard-STOP → structured entry naming the equivalence-guard + reason |
| 4 | Happy-path unchanged | Full PCR-1 APED-1 battery + existing `test_pcr_*` suite green, byte-diff the regen output for the canonical happy-path fixture pre/post-slice |
| 5 | Regression pinned | `shippability.md` grep returns a row whose Command targets `tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py` |

## Must-not-defer

- [ ] Fail-closed default: any ambiguity in equivalence → STOP, never silent-proceed (SOAD-1)
- [ ] No partial writes: STOP path leaves repo state unmutated (stage-then-commit atomicity per ADR-069)
- [ ] Audit trail: every equivalence-guard STOP logged to `parallel-conflict-resolution-log.md` with a structured reason
- [ ] Happy-path preservation: canonical SOFT auto-regen byte-unchanged when equivalence holds
- [ ] APED-1 empirical execution: the new guard predicate is exercised by an empirical-execution battery (executed, not reasoned-about)

## Out of scope

- PCR-2b HARD-class conflict resolution (separate LARGE slice)
- R-23 clock-skew / `add-claim-sequence-number` (separate slice)
- VAULT_CLAIM / MIXED / UNKNOWN class behavior changes (those already STOP)
- `--push` / `--sync-after-pr`-time rebase (deferred to PSQ-4+ per ADR-068)
- Changing SOFT file-set membership (`{slice-queue.md, shippability.md}` stays as-is)

## Dependencies

- Prior slices: [[slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen]] — the SOFT auto-regen path being hardened; [[slice-078-add-pcr-2a-vault-claim-resolver]] — sibling resolver; [[slice-070-fix-psq-1-blast-radius-dict-leak]] — `slice-queue.md` shape
- Code: `tools/parallel_conflict_resolver.py` (`_regen_slice_queue`, `_merge_shippability`, `classify_conflict`, `resolve_soft_conflict`)
- Test-first repro: `tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py`
- Vault refs: [[decisions/ADR-069-mint-pcr-1-conflict-diagnostic-and-soft-regen]], [[risk-register#R-21]]

## Mid-slice smoke gate

At ~50% of build (after AC-1's failing test exists, before the guard is wired):
```
$PY -m pytest tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py::test_corner_case_soft_regen_diverges_from_baseline -x
```
Expected: RED — the test reproduces R-21's divergence against the *current* auto-regen. If it passes (GREEN) before the fix: STOP — the corner case isn't actually reproduced, the fixture is wrong, re-derive it from the charter findings.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke corner-case test now GREEN (guard closes it); full PCR APED-1 battery green
- [ ] No new TODOs / FIXMEs / debug prints
