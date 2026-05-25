# Critique Review: Slice 066 add-worktree-per-slice-discipline

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-24
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

> Disposition context: first-Critic produced 5B/5M/4m; Builder drafts ratified 13 ACCEPTED-FIXED + m4 ACCEPTED-PENDING pre-meta-review. Builder mechanical verdict pending user TRI-1.

## Summary

The first Critic's 14 findings are substantively sound — B1 in particular was load-bearing and would have shipped an ADR-063 superseding the wrong ADR. However, the Builder's ACCEPTED-FIXED disposition for B1 ("Global ADR-021 → ADR-019 rename across mission-brief / design / ADR-063") missed one residual instance in `mission-brief.md` L152. The first Critic also missed three concrete dimension-specific concerns: design.md TF-1 count drift introduced by the very B3/B4 fixes (16 vs 20 in two callsites within design.md); shell-portability assumption (`awk` + `grep -E`) in design.md L56/L59/L83 that violates the user's PowerShell-on-Windows preference; and an empirical-audit-execution gap (APED-1) the first Critic explicitly skipped without falsifying the new `_WORKTREE_SKIP_LINE_RE` regex against the canonical sample. Severities of existing findings appear correctly calibrated. The first Critic's recursive-self-application observation ("this slice's BRANCH-2 ADR is meant to defend against exactly the FBCD-1 class B1/B4/M2/m1/m3 just instantiated") is reinforced by the misses below — the class is still firing within the post-fix design.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1 (ADR-021/ADR-019 conflation)** — VALID, severity Blocker is correct. ADR-019 verified as BRANCH-1 home at `ADR-019-branch-per-slice-workflow.md` L11; ADR-021 verified as utf8-stdout-1 (unrelated). The catch was structurally load-bearing — `tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py` would have asserted on the wrong ADR otherwise. **However**, see missed M-add-1 below: a residual ADR-021 instance escaped the global rename.
- **B2 (Windows path-comparison semantics)** — VALID, severity Blocker is correct. The microsoft/vscode#101244 evidence + git-worktree's "path recorded as-supplied" semantics confirm this would have produced silent false-negatives on Windows symlinked/junctioned worktrees. The post-fix path-comparison paragraph (design.md L96) is structurally sound.
- **B3 (3 audit call-shape enumeration)** — VALID, severity Blocker is correct. The pre-fix `worktree-cwd-mismatch` design left the canonical "Claude forgot to `cd`" detection structurally undefined. The post-fix 3-shape enumeration (design.md L97-100) closes this. The first Critic's call to expand AC3 from 4 to 7 rows is appropriate per WS-1 dimension coverage.
- **B4 (cross-spec parity test not in TF-1 plan)** — VALID, severity Blocker is correct. The classic FBCD-1 sub-mode (a) class — exactly what this slice mints BRANCH-2 to defend against (recursive-self-application observation N≈9). Adding `test_worktree_skip_grammar_pinned_across_three_surfaces` as a TF-1 row closes it. **However**, see M-add-2 below: the B4 fix introduced a NEW count drift inside design.md (16 vs 20 in two lines) that the first Critic's check didn't notice.
- **B5 (bootstrap discharge under-specified for /commit-slice)** — VALID, severity Blocker is correct. Without the idempotent guard, slice-066's own `/commit-slice --merge` would have hit `git worktree remove` on a non-existent worktree. The Builder's option (ii) choice (design.md L59 + L83) is the structurally cheaper + future-friendly fix.
- **M1 (CLAUDE.md L65 → L32)** — VALID, severity Major is correct.
- **M2 (3 prior-slice link names paraphrased)** — VALID, severity Major is correct. Re-verified mission-brief.md L99 against archive `_index.md` — all three canonical names now present.
- **M3 (Mode-interaction matrix)** — VALID, severity Major is correct. See M-add-4 below for an additional row the matrix didn't enumerate.
- **M4 (ADR-019 N-surface schema-pin / prospective application / v1 carveout dispositions)** — VALID, severity Major is correct.
- **M5 (parent-dir-writable enumeration)** — VALID, severity Major is correct.
- **m1 (count drift "three" → "four" violation kinds)** — VALID, severity minor is correct.
- **m2 (N=2 partial-supersession pattern note)** — VALID, severity minor is correct.
- **m3 (test function `_and_installed` suffix)** — VALID, severity minor is correct.
- **m4 (graphify CLI node-name-convention)** — VALID disposition (ACCEPTED-PENDING is correct), severity minor is correct. Re-surfacing in reflection.md as /critic-calibrate watch-list is the right call at N=1.

## Suspicious findings

No suspicious findings. Every B/M/m the first Critic surfaced reflects a real concern in the rev-1 draft, and the post-fix dispositions are structurally sound.

## Missed findings

The first Critic missed concerns the meta-Critic surfaces from independent dimension re-application:

### M-add-1: Residual ADR-021 reference at mission-brief.md L152 escaped the B1 global-rename disposition

- **Claim under review**: mission-brief.md L152 (pre-meta-fix) reads: *`partial-supersession encoding (ADR-063 → ADR-021)`*. The B1 disposition claim ("Global ADR-021 → ADR-019 rename across mission-brief / design / ADR-063") is therefore incomplete by one site.
- **Evidence**: `Grep ADR-021` on the slice folder — mission-brief.md L152 (verified by Builder post-meta-Critic).
- **Framework**: Wiegers requirements-traceability — when correcting a load-bearing identifier across N citations, the rename must sweep ALL N (`/critique` Dim 7 drift-from-vault). FBCD-1 sub-mode (a) within the very B1 fix that codified the inverse discipline (recursive-self-application N=10 ratchets +1 within slice-066 itself).
- **Severity**: **Major** (would survive Builder's TPHD-1 sub-mode (a) self-catch only if explicitly grep-swept; Step 6 audits don't enforce ADR-NNN cross-reference consistency in slice-authoring docs).
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief.md L152 corrected to `(ADR-063 → ADR-019; corrected from rev-1's ADR-021 per slice-066 /critique B1 ACCEPTED-FIXED + /critique-review M-add-1 ACCEPTED-FIXED residual-rename closure)`. The fix's prose explicitly anchors both the original B1 disposition AND the M-add-1 closure to prevent a future N=11 recurrence.

### M-add-2: TF-1 row-count drift WITHIN design.md introduced by the B3+B4 fixes themselves

- **Claim under review**: design.md L179 (pre-meta-fix) said *"all 16 TF-1 rows flip PENDING → WRITTEN-FAILING"*; design.md L190 said *"TF-1 strict-pre-finish (16/16 PASSING)"*; design.md "Test coverage shape" L196 said *"20 rows post-/critique fixes"*; mission-brief.md L128 says *"all 20 TF-1 rows PASSING"*. The 16 → 20 update propagated to design.md "Test coverage shape" but not to "Critical implementation order" L179 + L190.
- **Framework**: this is the IDENTICAL m1-class count drift the first Critic caught for "three" vs "four" violation kinds in the same file — and it's INTRODUCED by the B4 fix that retired the prior drift. Recursive-self-application N=10 — the very correction that closes one FBCD-1 sub-mode (a) instance opens two more inside the same file.
- **Severity**: **minor** (doesn't change runtime semantics; TF-1 audit reads mission-brief's table, not design.md's narrative; but ships an internal inconsistency that the next /critique would re-catch).
- **Builder draft**: **ACCEPTED-FIXED** — design.md L179 + L190 both updated to "20" / "20/20" with explicit citation of /critique-review M-add-2 ACCEPTED-FIXED.

### M-add-3: Shell-portability assumption — `awk` and `grep -E` in commit-slice Step 5b/5d are POSIX-only

- **Claim under review**: design.md L56 specifies main-tree resolution via `git worktree list --porcelain | awk '...'` with acknowledgment that "On Windows, `awk` is provided via Git for Windows' bundled MSYS bash". design.md L59 + L83 specify the idempotent worktree-remove guard via `git worktree list --porcelain | grep -E ...`. Both assume POSIX shell. Per `~/.claude/CLAUDE.md` shell preference: "On Windows, prefer the PowerShell tool over the Bash tool for all shell commands."
- **Framework**: Sommerville environment-assumption critique. **However**, the existing commit-slice SKILL.md already uses bash-shell git commands extensively (the existing two-signal flow uses `git ls-remote --exit-code`-style POSIX idioms), and Claude is expected to translate between shells. The design DOES note the awk acknowledgment at L56 — acknowledged but not falsified against a real PowerShell invocation. Disposition: SURFACE-AT-BUILDER-DISCRETION — either (i) add parenthetical "(invoke via bash on Windows; Git for Windows ships MSYS bash with awk/grep)" to L59/L83 to mirror L56, OR (ii) reshape the guard to use `python -c "..."` + `subprocess.run(['git','worktree','list','--porcelain'])`-based parsing so it's shell-agnostic.
- **Severity**: **minor** (the design surfaces the dependency; Claude's tool discretion handles bash-vs-pwsh routing; but a recurrence-class watch-list candidate for /critic-calibrate at N=2).
- **Builder draft**: **ACCEPTED-FIXED (option i)** — design.md L59 + L83 (idempotent guard) gained the parenthetical mirroring L56 acknowledgment + cross-cite to /critique-review M-add-3 + flag for slice-067+ reshape to Python-side parsing if N=2 recurrence emerges across sibling /commit-slice cleanup surfaces.

### M-add-4: Mode-interaction matrix's 5 rows miss the `--push` only (no follow-up) state

- **Claim under review**: design.md L66-72 enumerates 5 sequences but all 5 assume an eventual `--merge` or `--sync-after-pr` follow-up. The matrix doesn't enumerate the standing state after `--push` alone — where the worktree is documented as "stays alive through the PR-review window".
- **Framework**: Hendrickson exploratory-testing — "what is the system's state RIGHT NOW when no action has been taken yet?" The matrix focuses on terminal states (worktree removed / intact) but doesn't pin the intermediate state. This is the most common state across a slice's lifetime in PR-based workflows.
- **Severity**: **minor** (the design.md L62 "Behavior delta — Step 5c (`--push`): UNCHANGED" implicitly covers it; matrix completeness is a nicety, not a correctness gap).
- **Builder draft**: **ACCEPTED-FIXED** — design.md Mode-interaction matrix gained the new top row `"--push only (PR pending review — no follow-up yet) | N/A | N/A | intact (expected; teardown deferred to eventual --sync-after-pr or --merge)"` with explicit citation of /critique-review M-add-4.

### M-add-5: APED-1 empirical-audit-execution gap — the new `_WORKTREE_SKIP_LINE_RE` regex was not empirically falsified against a canonical sample

- **Claim under review**: The first Critic's Dim 8 noted "skipped — byte-identical to BRANCH=skip regex". This is true. The canonical bootstrap line is `WORKTREE=skip-bootstrap — rationale: slice-066 authors…`. Does the regex's `\bWORKTREE=skip\b` boundary match `WORKTREE=skip-bootstrap`? Python `\b` is a word-character boundary; `-` is NOT a word character, so `\b` after `skip` matches at `skip-bootstrap`. So the regex matches.
- **Framework**: APED-1 (Audit-Predicate-Empirical-Demonstration) — when a new audit's predicate is "byte-identical" to a prior audit, the empirical demonstration is the prior audit's pin-tests; the new audit inherits the test discipline but should still be exercised on the NEW keyword's canonical sample at minimum once. **However**, `test_honours_canonical_worktree_skip_rationale_line` (mission-brief row 11) naturally exercises this.
- **Severity**: **minor** (the existing TF-1 row 11 likely covers it; explicit bootstrap-variant fixture would be belt-and-suspenders).
- **Builder draft**: **ACCEPTED-PENDING** — at /build-slice the row 11 test fixture explicitly uses the `WORKTREE=skip-bootstrap — rationale: …` literal (the bootstrap-canonical-form), so the boundary semantics is exercised on the actual bootstrap sample without needing a separate row. If Builder discovers at /build-slice that row 11's fixture uses a non-bootstrap form, add the explicit bootstrap-variant fixture as belt-and-suspenders (single TF-1 row insert; no AC drift). User TRI-1 to ratify or override the deferral.

### M-add-6: Sub-mode (d) of BRANCH-1 — the `BRANCH=skip` Events-line surface — is implicit in §Scope of supersession L51 but not enumerated alongside the explicit (a)/(b)/(c) sub-modes

- **Claim under review**: ADR-063 §Scope of supersession L51 mentions `BRANCH=skip` as "ADR-019's implicit claim that the `BRANCH=skip` Events-line escape-hatch is the sole skip mechanism" — treats it as an "implicit claim" not as a 4th sub-surface anchor pinned at `skills/build-slice/SKILL.md` Step 7c per ADR-019 + slice-021 /critique B1 ACCEPTED-PENDING. The first Critic's M4 fix expanded "Carried forward unchanged" with N=3 pin / prospective / v1 carveout but the BRANCH=skip line shape itself (4th-surface anchor) isn't enumerated as either superseded, extended, or carried forward.
- **Framework**: Newman explicit-versioning — when minting a successor discipline, every documented sub-surface of the predecessor should have a disposition.
- **Severity**: **minor** (the design.md L36 + ADR-063 L51 together cover this in prose; explicit enumeration in §Scope of supersession would tighten the FBCD-1 sub-mode (a) defense within the very ADR that codifies the disposition discipline; observational tightening).
- **Builder draft**: **ACCEPTED-FIXED** — ADR-063 §Scope of supersession "Carried forward unchanged" extended with explicit BRANCH=skip 4th-surface disposition (inherited as legacy parallel escape-hatch; coexists with new WORKTREE=skip; both regex literals pinned in parallel — `_BRANCH_SKIP_LINE_RE` unchanged; `_WORKTREE_SKIP_LINE_RE` new).

## Severity adjustments

No severity adjustments. All 14 first-Critic findings appear correctly calibrated:

- B1-B5 are correctly Blockers (would have shipped structural defects or compromised the slice's discipline-mint integrity).
- M1-M5 are correctly Majors (fix-or-risk-regression class; not slice-blocking but should ship inside this slice).
- m1-m4 are correctly minors (cleanup-class; m4's ACCEPTED-PENDING-with-watch-list discipline is the right calibration for an N=1 observation that doesn't yet meet the project's N=2 promotion threshold).

The Builder's mechanical verdict of **NEEDS-FIXES** (driven by m4 + M-add-5 ACCEPTED-PENDING) is correctly cautious — the meta-review adds 6 missed findings (1 Major + 5 minors). Recommendation to user at TRI-1: address M-add-1 (residual ADR-021 at mission-brief.md L152) BEFORE /build-slice (DONE per ACCEPTED-FIXED disposition above); ratify M-add-2/3/4/6 as ACCEPTED-FIXED (already applied); M-add-5 as ACCEPTED-PENDING or convert to ACCEPTED-FIXED at /build-slice if Builder discretion adds the explicit bootstrap-variant fixture.

## Notes

The meta-Critic's confidence in the post-fix design.md / mission-brief.md / ADR-063 is **HIGH on structural soundness, MEDIUM on FBCD-1 sub-mode (a) cross-citation completeness**. The first Critic earned its keep on B1 (load-bearing ADR identifier error that would have shipped a structurally meaningless `supersedes:` slot); the Builder's dispositions were substantively right; but the recursive-self-application observation the first Critic itself surfaced (Dim 9 cross-cutting conformance: "B1 / B4 / M2 / m1 / m3 all FBCD-1 sub-mode (a) class — exactly the discipline this slice's BRANCH-2 ADR is meant to defend against") proved prescient in a way the first Critic didn't anticipate: the B1 fix and the B4 fix themselves committed new instances of the class within the corrected files. M-add-1 (residual ADR-021 at L152) is the structurally most important meta-finding — the global-rename-incomplete-by-one-site pattern matches the N=9-stable codification-commits-the-class observation almost too cleanly (now N=10 within slice-066 itself). The remaining 5 missed findings are observational/cosmetic tightening; the slice is fundamentally buildable. The first Critic's transparent skip of empirical-falsification on `_WORKTREE_SKIP_LINE_RE` was reasonable (byte-identical to a tested regex) but is worth a /critic-calibrate observation: APED-1 inheritance via "byte-identical regex" should perhaps require a single-row sanity-pin even when the predicate is inherited.

## Pipeline position

- **predecessor**: `/critique`
- **successor**: `/critique` Step 4.5 (TRI-1 user-owned triage gate — HALT for user ratification of all 14 first-Critic dispositions + 6 meta-Critic missed-finding dispositions)
- **auto-advance**: true (hand-off to /critique Step 4.5)
- **user-input gates**: TRI-1 HALT (per PCA-1 v0.41.0).
