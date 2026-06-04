# Reflection: Slice 113 bulk-convert-remaining-skills-to-vault-seam

**Date**: 2026-06-04
**Shipped**: YES-WITH-DEFERRALS (agent-prose surface deferred to a named follow-on)

## Validated
- **The seam-aware op-gate (ADR-106) preserves write-op protection across the convention rollout** — validated: `--op-gate --strict` exit 0 with breakdown `{6,11,23,0}` (no floor loosening); the 3 `<vault>/`-sink tests classify DEFERRED/OUT_OF_SCOPE/UNROUTED correctly. The code-Critic confirmed by mutation that reverting the extractor breaks classification — the matcher+extractor lockstep is real.
- **The carve-out classes are sound at scale** — validated: 116 carve-outs (pathspec/worktree-composed/active-folder/slice-queue/diagnose-out) stay concrete; `converted_file_regressions` = 0 un-sanctioned regressions; the per-value ratchet protects 22 files.
- **Filename-keyed audits are NOT blinded by the prefix conversion** — validated: SVW-1 stayed clean (20 routed / 3 exempted) because it keys on the shared-aggregate *filename*, not the `architecture/` prefix. Only the op-gate (which matched the prefix to find sinks) needed seam-awareness.
- **The 13-skill OSDG-1 roster is disk-derived, not prose-derived** — validated: `-k skill_drift` 18 passed; the on-disk `*_skill_drift.py` set is the authority (the M-add-1 fix).

## Corrected
- **The active-folder discriminator regex was too narrow** (`slices/slice-(\d+|NNN)`) → reality: it missed wildcard/placeholder/ellipsis active-folder forms (`slices/*/`, `slices/<slice-id>/`, `slices/slice-*/`, `slices/…`). Corrected at build (AP-3): broadened to "`architecture/slices/X` carves UNLESS X is `_index.md`/`action-points.md`/`archive`/bare." Recorded in build-log + design AS-BUILT (the discriminator table).
- **The git-pathspec carve-out missed PROSE mirrors of pathspecs** (B1, caught by /code-review) → reality: a pathspec described in prose without `:(exclude)` *on its own line* is invisible to `_PATHSPEC_RE`, so 3 `code-review.md` bullets were wrongly converted. Corrected: reverted to concrete; re-pin cascade 129→132 / 127→130.
- **[[risk-register.md]] R-32** — the prose-rewrite residual is now drained for the SKILL surface; the remaining residual is updated to the physical move + the **agent-prose surface** (4 agent files). (Rewritten in place via `vault_edit rewrite`.)

## Discovered
- **`git worktree add` checks out CRLF even when the main tree + `.gitattributes eol=lf` are LF** — a BRANCH-3 worktree-environment artifact. Failed `test_guarded_md_files_have_no_crlf_in_working_tree`. Impact: every BRANCH-3 slice editing eol=lf-pinned files must normalize the worktree to LF (git stores LF, so no spurious diff). Worth a build-check candidate if it recurs (N=1 so far).
- **The discriminator's pathspec detection is line-local, not block-aware** (B1 root cause) — `_PATHSPEC_RE` matches `:(exclude)` syntax on the literal's own line, but a prose *description* of a pathspec elsewhere in the same block has no such marker. A latent gap for any conversion that must distinguish "command literal" from "prose mirror of a command literal." Documented.

## Deferred
- **The agent-prose surface** (4 agent files: `code-review.md`, `critic-calibrate.md`, `critique-review.md`, `diagnose-narrator.md`) carry convertible refs — reason: each needs its OWN ADR-105 embedded resolver-context note (a subagent doesn't inherit CLAUDE.md). Lands in: a new `convert-agent-prose-to-vault-seam` follow-on (surfaced as a next-slice candidate below; the next `/slice` registers it in the queue). M1 / TRI-1-ratified path (b).
- **R-32 physical move** (move `architecture/` external + git-untrack + `/commit-slice` RETIRE no-op + draining R-32.a/.b) — the dedicated `flip-vault-to-external-store` slice. R-32 stays `mitigating`; retires at the move.

## Critic calibration

Per TRI-1, scored against each `critique.md` / `critique-review.md` / `code-review.md` disposition + reality at build/validate/code-review. **This slice exercised the full 3-Critic stack (design → meta → code); all three caught real, non-overlapping defects (AP-19, N+1).**

**Design-Critic (`/critique`)**:
- **B1** (validate-slice command-arg consumer): VALIDATED — ACCEPTED-FIXED; `test_validate_slice_skill.py:65` broke at build EXACTLY as flagged → repointed.
- **B2** (op-gate value-extractor): VALIDATED — ACCEPTED-FIXED. The headline catch: the design+meta reasoning said "prefix-agnostic sub-regexes, no change needed," glossing that the EXTRACTOR feeding them was the gap. The code-Critic later confirmed by mutation that the extractor is load-bearing.
- **M1** (R-32 residual claim false): VALIDATED — ACCEPTED-FIXED; the agent surface IS a real residual (5 agent-file refs confirmed).
- **M2** (build-slice carve-out guard): VALIDATED — ACCEPTED-FIXED; the class-5/6 guard held green.
- **M3** (carve-out keying collision): VALIDATED — ACCEPTED-PENDING; the collision was REAL — code-review had 5 exploitable same-value pathspec collisions (→ un-ratcheted) + slice had the non-exploitable ellipsis.
- **M4** (slice:264 unchanged unverified): VALIDATED — ACCEPTED-FIXED; resolved cleanly (the broadened discriminator carved it → line unchanged → no 4th re-hash, verified by execution).
- **m1** (code-review:103 5-match pin): VALIDATED — ACCEPTED-FIXED (flipped to carve-out at TRI-1); the pin stayed green untouched.
- **m2** (smoke gate too narrow): VALIDATED — ACCEPTED-FIXED.

**Meta-Critic (`/critique-review`)** — dual-review verdict EXTEND:
- **M-add-1** (forward-sync roster wrong): VALIDATED — a finish-gate Blocker the first Critic missed. Disk-confirmed: 13 not 12 (`diagnose` has no drift test; `code-review`+`pulse` do). Would have RED the suite at finish.
- **M-add-2** (2nd pathspec consumer + git-consumed disposition): VALIDATED — pathspecs ARE git-consumed; carving them out kept both consumer tests green.

**Code-Critic (`/code-review`)**:
- **B1** (git-pathspec PROSE mirrors wrongly converted): VALIDATED — a real must-not-defer violation the FULL 1617-test suite missed (the consumer test pins the COMMAND, not the prose). The AP-4 code-Critic value, live.
- **m1** (3rd op-gate test vacuous against extractor-revert): VALIDATED — the test stayed green on the mutation; strengthened to be extractor-sensitive.

**Missed by ALL Critics** (caught only at EXECUTION — AP-3):
- The **active-folder discriminator calibration gap** (wildcard/placeholder/ellipsis forms) — surfaced when the FIRST conversion over-converted 10 active-folder refs. No Critic predicted it; only running `--json` against the real corpus + grepping `<vault>/slices/` for non-shared-aggregate caught it. The slice-112 "AP-3 again, twice" lesson, N-th confirmation: design-time reasoning (even triple-Critic-ratified) is not proof for a slice that authors classifier-visible prose.
- The **CRLF worktree-checkout artifact** — surfaced at test execution.

**Pattern**: the 3-Critic stack caught a clean partition of defect classes — design-Critic → classifier-mechanics (B2 extractor) + consumer-contract enumeration (B1/M2); meta-Critic → on-disk-vs-prose roster completeness (M-add-1); code-Critic → build-time conversion-correctness the suite structurally can't catch (B1 pathspec-prose). EXECUTION (AP-3) caught the two things NO Critic could (discriminator calibration + EOL). Complementarity stable N≥14.

## Lessons for next slice
- **AP-3, N-th confirmation**: a classifier/discriminator slice MUST execute its rule against the real corpus AND grep the *output* for mis-buckets (here: `<vault>/slices/` for wrongly-converted active-folder). Design-time reasoning is not proof.
- **Conversion tools must distinguish a command-literal from its PROSE MIRROR** (B1): `_PATHSPEC_RE` is line-local; a pathspec *described* in prose (no `:(exclude)` on its line) slips through. When a literal class is "concrete because a tool consumes it," verify the discriminator catches BOTH the executable form and its prose description.
- **The code-Critic is the layer that catches conversion-correctness the test suite misses** (AP-4, N+1): the consumer test pinned the command, not the prose — a 1617-green suite shipped a must-not-defer violation that only the code-Critic's read of the diff caught.
- **BRANCH-3 worktrees can check out CRLF** — normalize eol=lf-scoped files to LF before the drift tests (no spurious diff; git stores LF).

## Vault updates made (thin vault)
- [[risk-register.md]] — R-32 residual rewritten (prose-rewrite SKILL leg drained; agent-prose surface + physical move now the named residual) via `vault_edit rewrite`.
- [[lessons-learned.md]] — slice-113 entry appended (Step 5) via `vault_edit append`.
- [[architecture/shippability.md]] — rows 113/117/118 re-pinned (303/301 → 132/130) + new row 119 (added at build during the AP-10 fan-out).
- [[architecture/drift-log.md]] — slice-113 `**Trigger**` section (DCE-1).
- This slice's [[design.md]] + [[decisions/ADR-106]] — AS-BUILT (the broadened discriminator + the B1 carve-out refinement + the extractor lockstep).
- No methodology-changelog / VERSION change (MEPD-1 EXCLUDE).
