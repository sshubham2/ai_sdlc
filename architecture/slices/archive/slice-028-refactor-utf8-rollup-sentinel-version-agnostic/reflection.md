# Reflection: Slice 028 refactor-utf8-rollup-sentinel-version-agnostic

**Date**: 2026-05-16
**Shipped**: YES

## Validated
- The slice-014/ADR-013 3-part template (derive-real-invariant + AST meta-test + failure-path regression) transfers cleanly to the UTF-8 rollup sentinel — validated: 561 methodology tests pass; the version-agnostic-shape meta-test + counter-anchor + bidirectional failure-path test all green.
- Observed coverage-parity genuinely protects the invariant (not weakened) — validated by real fake-tool smoke: `tools/aaa_ac2_fake_audit.py` with `main()` and no coverage → sentinel RED naming it; coverage added at a real call site (sentinel body untouched) → GREEN; removal → GREEN with zero ledger edit.
- Rule-ID lineage preserved (UTF8-STDOUT-1 v1.1, not a new ID) — validated: v0.42.0 entry-pin + ADR-026 pin pass; PMI-1 atomic bump 0.41.0→0.42.0 across all three surfaces; in-repo↔installed changelog byte-equal.
- N=5 maintenance-tax retired — validated structurally: adding/removing a tool now requires only a real coverage call-site edit, never a count literal / ledger bump.

## Corrected
- (none) — reality confirmed the post-critique design exactly. No ADR superseded, no risk-register change, no design.md correction. The observed-covered-set design behaved as ADR-026 predicted in all three behavioral directions.

## Discovered
- **Destructive-`git checkout`-on-uncommitted-slice-work hazard.** During AC2/AC3 behavioral demo, the validation harness used `git checkout -- <test file>` to revert demo mutations. Under branch-per-slice (BRANCH-1) the slice's work is *uncommitted* until `/commit-slice`, so `git checkout --` silently reverted the **entire slice refactor** to pre-slice HEAD; the post-revert "1 passed" was the OLD `== 20` sentinel — a *false-green that nearly masked total loss of the slice's work*. Caught by a sentinel-file hash mismatch + the harness's own change-notification. Impact: process discipline — promoted to build-checks (BC-PROJ-3 + BC-GLOBAL-2). Not a risk-register R-ID (execution/process, not product/tech risk).
- The mission-brief's smoke example used a `_`-prefixed fake-tool name; the B1 discovered-set rule correctly *excludes* leading-`_`, so the real smoke required a NON-`_` name. Minor — design.md discovered-set rule was correct; the brief's example pre-dated the B1 precision. No vault change needed (noted in build-log).

## Deferred
- function-level-PTFCD-1 extension — explicitly out of scope per mission-brief; N=3 corroboration standing (slice-025/026/027) — strongest standing deferred candidate, now alongside no competing sentinel-refactor (this slice retired that one). Lands in: next `/slice` candidate set.
- Generalizing the version-agnostic-sentinel pattern to other count-asserting tests — out of scope; only the UTF-8 rollup sentinel was in scope.

## Critic calibration

Scored from `critique.md` `## Triage` + reality observed during build/validate:

- **B1** (discovered-set inconsistent glob vs main()-filtered): **VALIDATED** — ACCEPTED-FIXED; reality confirmed `_find_main_function` semantics == `tools_with_main`; the precise rule was load-bearing.
- **B2** (declaration-registry self-referential → invariant weakened): **VALIDATED** — ACCEPTED-FIXED; the smoke test concretely proved option-3 would have shipped a false-green; option-4 closed it.
- **M1** (bespoke coverage not uniformly derivable): **VALIDATED** — ACCEPTED-FIXED; option-(a) AST-scan reconciled the out-of-scope tension.
- **M2** (AC3 removal circular for declaration-registry): **VALIDATED** — ACCEPTED-FIXED; AC3 validation confirmed observed-covered-set makes removal genuinely zero-edit.
- **M3** (entry-pin enumeration + independent-counter knowledge): **VALIDATED** — ACCEPTED-FIXED; entry-pins pass, independent-counter note relocated and intact.
- **m1** (ADR number unverified): **VALIDATED** — ACCEPTED-FIXED; ADR-026 correct (highest was ADR-025).
- **m2** (canonical-phrase uniqueness): **VALIDATED** — ACCEPTED-PENDING; build-time grep confirmed unique; discharged.
- **B-add-1** (meta-Critic; helper-extraction defeats AST meta-test, fail-OPEN): **VALIDATED** — the single highest-value finding of the slice. The first Critic checked the 3 template parts in isolation and missed the part2×part3 interaction; the meta-Critic (EXTEND) caught it pre-build. Implemented in-body + scan-scope-widened + counter-anchor; the counter-anchor itself caught two of my own implementation false-positives before they shipped.
- **M-add-1** (meta-Critic; covered-set walk fail-OPEN on non-literal shapes): **VALIDATED** — fail-closed loud-diagnostic implemented; correct defensive posture.
- **B2-adj** (meta-Critic; "observed not declared" over-claim): **VALIDATED** — tempered honestly (parametrize=execution-bound, bespoke=source-presence proxy) per ADR-013 honesty convention.

**Missed by Critic**: the destructive-`git checkout`-on-uncommitted-slice-work hazard. NEITHER Critic flagged it — but it is **out of typical Critic design-review scope** (the Critic reviews design.md/ADRs, not the validation/demo execution harness). Classed as MISSED-OUT-OF-SCOPE, not a design-dimension blind spot. Worth a `/critic-calibrate` note only if a *design*-expressible variant recurs (e.g., a slice whose design.md proposes a mutate-then-`git checkout` validation step — that WOULD be in scope).

**Pattern**: dual-Critic stack was **10/10 VALIDATED, 0 FALSE-ALARM, 0 OVERRIDE-MISJUDGED** on design-scope findings. The meta-Critic's EXTEND added one genuine Blocker (B-add-1) the first Critic missed via *composition-blindness* (3-part-template parts checked in isolation, interaction missed) — directly corroborates the slice-027 lesson "budget the full /critique→/critique-review depth for audit-adjacent codification slices" and the slice-022 self-violation law (the codification slice committed its discipline's defect class at two layers — option-3 B2 and option-4 B-add-1 — both dual-Critic-caught pre-build).

## Lessons for next slice
- **Validation/demo harnesses must NEVER use `git checkout -- <path>` / `git restore` / `git stash` on files carrying uncommitted slice work** (branch-per-slice ⇒ slice work is uncommitted until `/commit-slice`). Revert demo mutations via in-place reverse edits or temp copies. A false-green from a silent full-slice revert nearly shipped. Promoted: BC-PROJ-3 + BC-GLOBAL-2.
- **The slice-022 self-violation law now N≈8** and fired the *deepest yet* on an audit-adjacent codification slice: defect class committed at design-time (option-3 B2) AND at fix-design-time (option-4 B-add-1), each caught one Critic layer deeper. For 3-part-template refactor slices specifically, the part-interaction (not just per-part correctness) is the meta-Critic's highest-yield target.
- **A self-written AST meta-test will false-positive on its own defensive code** (my int-Compare check caught the helper's `len(args) >= 2` arity guard; my counter-anchor caught the guard tests' own introspection `ast.parse`). slice-014 fidelity = defect-class-precise scoping, not blanket structural bans. Budget one debug iteration for meta-test self-false-positives on any AST-shape-pin slice.
- function-level-PTFCD-1 (N=3) is now the uncontested strongest standing deferred candidate — the competing sentinel-refactor candidate is retired by this slice.

## Vault updates made (thin vault — small list)
- [[lessons-learned.md]] — appended Slice 028 entry
- [[build-checks.md]] — BC-PROJ-3 (destructive-git-on-uncommitted-slice-work); also [[~/.claude/build-checks.md]] BC-GLOBAL-2 (cross-project generic)
- [[shippability.md]] — row 28 (added during /build-slice Task 4; serves as the slice-028 critical-path entry)
- [[methodology-changelog.md]] — v0.42.0 UTF8-STDOUT-1 v1.1 (in-repo + installed byte-equal)
- [[decisions/ADR-026-version-agnostic-utf8-rollup-sentinel]] — created (reversibility: cheap; RSAD-1 self-stress section)
- No ADR superseded; no risk-register change; no design.md correction (reality confirmed design).
