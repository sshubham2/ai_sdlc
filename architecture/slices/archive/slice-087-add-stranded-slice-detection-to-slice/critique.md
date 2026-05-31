# Critique: Slice 087 add-stranded-slice-detection-to-slice (RE-CRITIQUE, post 4-class reframe)

**Critic reviewed**: mission-brief.md, design.md, ADR-079 (revised 2026-05-31)
**Date**: 2026-05-31
**Result**: NEEDS-FIXES (Critic verdict; Builder drafts below; final verdict set by user at TRI-1)

> Spawned via `Agent` `subagent_type: "critique"`; per SAOF-1 written ONLY from the agent's actual returned content. The Critic EXECUTED the reused functions (`detect_active_worktrees` / `classify_worktree_state` / `_resolve_default_branch` / `parse_queue_text`) against the live two-worktree repo state.
> This is the RE-CRITIQUE after the parallel-safety reframe. The first `/critique` (1B/4M/2m) + `/critique-review` (EXTEND +2) ran against the superseded flag-all design; those dispositions are all carried into the reframe and are NOT re-litigated here.

## Summary

The reframe is sound at its core: the Critic executed the reused classifiers against the LIVE state and confirmed both `slice/087` (stage=critique) and `slice/088` (stage=design) classify as `IN_PROGRESS` → IN-PROGRESS → `halt:false` → `status:clean`. **The central parallel-safety property (AC4(c)) holds against the real repo, and the Dim-7 strategic-direction-fit concern that motivated this re-critique is genuinely addressed — no finding there.** However, the CLAIMED-BY-OTHER mechanism (precedence #1) cannot fire against the actual `slice-queue.md` (keys by candidate-name, holds backlog candidates, no in-flight branch mapping). One Blocker, three Majors, two Minors.

## Findings

### Blockers (must address before /build-slice)

#### B1: CLAIMED-BY-OTHER precedence #1 cannot fire — branch→queue-candidate mapping unspecified and structurally cannot match the live queue
- **Claim under review**: design.md Classification model row #1 + What's reused: "reuse `slice_queue_claim.parse_queue_text` on `architecture/slice-queue.md` … claim identity ≠ mine ⇒ CLAIMED-BY-OTHER (precedence #1)."
- **Issue**: Executed `parse_queue_text` against the live queue — it keys entries by `### <candidate-name>` (e.g. `add-project-frame-synthesizer`), NOT by `slice/NNN-<name>` branch; the branch→key mapping was unspecified. The live queue holds the top-10 *backlog* candidates, all `claimed_by` absent, and the in-flight branch suffix is not a key at all. So precedence-#1 — the class whose entire job is cross-session cry-wolf avoidance — never matched anything, silently. The design conflated two different non-firings (solo-dev identity-match vs lookup-key-never-resolves).
- **Evidence**: executed `parse_queue_text(...)` → keys `{add-index-md-soft-promotion-or-light-hard-path, extend-osdg-1-to-slice-candidates, add-claim-sequence-number-for-clock-skew-detection, add-psq-4-push-time-rebase, add-diagnose-cwd-mismatch-runtime-test}`, all unclaimed; `tools/slice_queue_claim.py:201,260`.
- **Builder draft**: **ACCEPTED-FIXED (option a — keep + specify + honest)** — design.md `## Classification model` gains a "Claim-resolution honesty" note; row #1 + What's new specify the `slice/NNN-<name>` → `<name>` mapping and state that **key-absent OR present-but-unclaimed ⇒ correct fall-through to #2/#3/#4, NOT a silent miss** (the live parallel-safety signal is IN-PROGRESS via the worktree, precedence #2, confirmed firing); AC4(d) reframed to mark its fixture *synthetic / code-path-proving* with production reachability gated on a real foreign claim; ADR-079 Decision gains the same scope note (class is "largely inert in solo-dev — a forward-provision, not load-bearing"). **Declinable TRI-1 alternative (option b)**: demote CLAIMED-BY-OTHER to an explicitly-deferred follow-on and ship a **3-active-class** model (STRANDED-COMPLETE/ORPHANED halt; IN-PROGRESS informational; + INDETERMINATE) — simpler, loses nothing in solo-dev. **User chooses (a) vs (b) at TRI-1.**

### Majors (address this slice)

#### M1: STRANDED-COMPLETE bare-branch vault lookup reads the WRONG tree's vault for a worktree-less branch
- **Claim under review**: design.md What's new: "A bare unmerged branch classified by the current-tree vault: `archive/slice-NNN-*` present ⇒ STRANDED-COMPLETE …".
- **Issue**: For a bare branch without a worktree, the stranded archive/milestone state lives ON the unmerged branch by definition (the slice-086 incident: built+archived on its branch, never merged). A fresh `/slice` from `master` reading only the invoking tree's `archive/` MISSES it → falls through to ORPHANED. Both halt, but the offered recovery affordance differs (STRANDED-COMPLETE → Resume-via-`/commit-slice`; ORPHANED → proceed/inspect), so the misclassification gives the wrong recovery path for the exact incident this slice exists to fix.
- **Evidence**: `ls architecture/slices/archive/` in slice-087 worktree → only `slice-086-*`; design read invoking-tree vault only, no `git show <branch>:…` cross-tree lookup.
- **Builder draft**: **ACCEPTED-FIXED** — design.md What's new + Error model + ADR-079 now specify the bare-branch lookup reads **the branch's own tree** via `git ls-tree <branch> -- …archive/slice-NNN-*` / `git show <branch>:…/milestone.md` (invoking tree only as secondary); AC4(a) extended to assert STRANDED-COMPLETE when the archive entry exists ONLY on the unmerged branch (covered by the existing `test_stranded_complete_branch_halts` row — no new TF-1 row).

#### M2: Mid-slice smoke gate fixture "998-parallel WITH a live worktree" cannot be constructed as worded → trips INDETERMINATE
- **Claim under review**: mission-brief.md Mid-slice smoke gate.
- **Issue**: `classify_worktree_state` returns IN_PROGRESS only when `milestone_path` resolves to an existing file AND `_parse_milestone_stage` yields non-None stage ≠ `reflect` (`pulse_worktree_resolver.py:359-408`). A fixture that merely makes a branch + loose dir resolves `milestone_path=None` → UNKNOWN → INDETERMINATE → `halt:true`, FAILING the "998 ⇒ in-progress(no halt)" expectation and reading as a regression-to-flag-all → spurious mid-slice STOP.
- **Evidence**: `pulse_worktree_resolver.py:359,371-376,403`.
- **Builder draft**: **ACCEPTED-FIXED** — smoke gate rewritten with the concrete construction (`git worktree add <fixture>/wt-998 -b slice/998-parallel` + write valid `milestone.md` frontmatter `stage: design` into the worktree + commit on the branch).

#### M3: `--root` alias incidental-pass risk in the cp1252 regression — verify it reaches stdout with a non-ASCII char
- **Claim under review**: design.md Inventory fan-out #4 + AC#1 (`--root` alias so `_ROOT_ONLY_TOOLS` reaches stdout).
- **Issue**: For a genuine UTF8-STDOUT-1 guard the `[-m tool, --root, REPO]` run must actually emit a non-ASCII char; an all-`clean`/empty fixture prints only ASCII → vacuous pass guarding nothing (the slice-085 incidental-pass lesson, in the aggregated lessons).
- **Evidence**: `tests/methodology/test_utf8_stdout_regression.py:118-121`; FIXTURE_DIR likely yields `status: clean` (all-ASCII).
- **Builder draft**: **ACCEPTED-FIXED (design) + ACCEPTED-PENDING (build-verify)** — design.md Output contract now states the **human-mode summary header always emits a `→`** (e.g. `stranded-slice-audit → status: clean (0 divergent)`) independent of entry count, making the cp1252 test non-vacuous on any fixture; build-time step verifies the fixture run reaches the glyph.

### Minors (log; address if cheap)

#### m1: Orphan `ahead: null` rationale slightly wrong — `rev-list --count` is defined (just not meaningful), not "undefined"
- **Issue**: `git merge-base --is-ancestor` returns exit 1 (not error) for unrelated histories → orphan correctly classifies non-ancestor→candidate→ORPHANED; `rev-list --count default..<unrelated>` does NOT error and DOES return a count. The "undefined-symmetric" wording propagates a wrong mental model.
- **Evidence**: git-merge-base / git-rev-list docs (web-verified).
- **Builder draft**: **ACCEPTED-FIXED** — design.md Error model reworded: `ahead` is "defined but not meaningful"; `ahead: null` signals "no shared base", distinct from a numeric count and distinct from INDETERMINATE (merge-base *error*).

#### m2: AC#5 INSTALL.md count 33→34 — confirm exactly two surfaces, no third
- **Issue**: L22 + L166 confirmed "33 executable methodology tools" and `_CANONICAL_TOOLS` len=33, so 33→34 is right; grep `\b33\b` near "tool" project-wide before the edit to catch any third count surface (FBCD-1 / CCC-1 multi-surface).
- **Evidence**: `INSTALL.md:22,166`; `_CANONICAL_TOOLS` len=33 (executed).
- **Builder draft**: **ACCEPTED-PENDING** — build-time grep for `\b33\b` near "tool" across INSTALL.md/README/plugin prose to confirm exactly two count surfaces before updating both.

## Dimensions checked
- [x] Unfounded assumptions — B1 (CLAIMED-BY-OTHER lookup key never resolves — executed); M1 (current-tree vault assumed to hold stranded-branch archive — disproven against live tree).
- [x] Missing edge cases — M2 (IN-PROGRESS fixture milestone-frontmatter requirement); m1 (unrelated-histories rev-list). Empty/no-slice-branches covered by AC4(e).
- [x] Over-engineering — none (reuse-heavy; 4-class justified by parallel-safety, not speculative). *(Builder note: the option-b TRI-1 alternative for B1 would trim CLAIMED-BY-OTHER if the user judges it speculative.)*
- [x] Under-engineering — AC4(d) asserts a synthetic-only path (B1); AC4(a) under-delivers cross-tree STRANDED-COMPLETE (M1). TF-1 has rows for all 8 behavioral + structural-pins + inventory-pin + reused drift.
- [x] Contract gaps — detector CLI contract fully specified; `ahead: null` semantics loosened (m1). No HTTP/event contracts.
- [x] Security — none beyond the inherited PSQ-2 cooperative-trust boundary, correctly scoped in design.md Authorization model.
- [x] Drift from vault — **Strategic-direction-fit + architectural-concurrency (Dim-7, the re-critique focus): VALIDATED as addressed** — reused classifiers executed against the LIVE two-worktree state, both in-flight branches → IN_PROGRESS → `halt:false` → `status:clean`; the rejected flag-all (ADR-079 Option 4) is correctly carved out. ADR-079 revised-in-place is legitimate (slice not shipped — still a draft). MEPD-1 EXCLUDE concurred (open-time advisory predates this slice; reframe makes the halt smarter not newer). No stale flag-all claims found across mission-brief/design/ADR.
- [x] Web-known issues — `git merge-base --is-ancestor` exit-code semantics verified (exit 1 = not-ancestor, not error → orphan classification correct, NOT INDETERMINATE — m1); `rev-list --count` for unrelated histories inconclusive in web sources, `ahead: null` defensible.
- [x] Cross-cutting conformance — APED-1 executed (parse_queue_text key-mismatch surfaced B1; classify_worktree_state IN_PROGRESS confirmed; _resolve_default_branch → `master` confirmed); `_CANONICAL_TOOLS` len=33 (M1-count sound, m2 multi-surface); recovery/* `refs/heads/slice/` glob exclusion confirmed sound; no stale flag-all claims.

**Calibration note**: B1 high-confidence (executed against live queue). M1 medium-confidence (depends on whether the stranded archive is ever committed only on the unmerged branch — the slice-086 incident says yes). M2/M3 mechanical, cheaply build-verifiable. The Dim-7 parallel-safety reframe itself is VALIDATED-correct against live state — the reframe achieved its goal; the new Dim-7 probe (`64f6ea3`) did its job by being the lens, and the residual findings are mechanism-level, not direction-level.

## Triage

**Triaged by**: user
**Date**: 2026-05-31
**Final verdict**: NEEDS-FIXES

> Reconciles BOTH passes (first Critic `critique.md` + meta-Critic `critique-review.md` EXTEND). B1 severity downgraded Blocker→Major per the meta-Critic's SEVERITY-WRONG adjustment (user-accepted); M-add-1 added as a meta-Critic missed-finding row. B1 resolved via **option-a** (keep the 4-class model) per user choice at TRI-1.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Major | ACCEPTED-FIXED | Severity downgraded Blocker→Major (meta-Critic: an inert-in-solo-dev class is over-provisioning, not a breakage; parallel-safety is carried by IN-PROGRESS). Option-a ratified: keep CLAIMED-BY-OTHER as precedence #1 with the `slice/NNN-<name>`→`<name>` mapping + the honest "key-absent OR present-but-unclaimed ⇒ correct fall-through, NOT a silent miss" note — applied to design.md §Classification-model + ADR-079 Decision + mission-brief AC4(d) |
| M1 | Major | ACCEPTED-FIXED | Bare-branch STRANDED-COMPLETE now reads the branch's OWN tree (`git ls-tree <branch>`/`git show <branch>:…/milestone.md`), invoking tree secondary — design.md §What's-new + Error model + ADR-079 + AC4(a) |
| M-add-1 | Major | ACCEPTED-FIXED | (meta-Critic missed finding) `git show <branch>:` reads committed-tip which can lag an uncommitted working milestone → could silently weaken the halt on the narrow worktree-removed-before-commit window. Error model now NAMES the staleness (committed-tip is the only source for a bare branch; fail-closed still surfaces; not assumed to be ground truth) — design.md §Error model |
| M2 | Major | ACCEPTED-FIXED | Mid-slice smoke gate rewritten with the concrete IN-PROGRESS fixture (`git worktree add -b slice/998-parallel` + committed `stage: design` milestone) so it can't trip INDETERMINATE — mission-brief §Mid-slice smoke gate |
| M3 | Major | ACCEPTED-PENDING | Design states the human-mode summary header always emits `→` (non-vacuous cp1252 guard) — design.md §What's-new; **build-time verify** the `_ROOT_ONLY_TOOLS` fixture run actually reaches that glyph |
| m1 | Minor | ACCEPTED-FIXED | `ahead: null` rationale reworded ("defined but not meaningful", not "undefined-symmetric") — design.md §Error model |
| m2 | Minor | ACCEPTED-PENDING | **build-time** grep `\b33\b` near "tool" across INSTALL.md/README/plugin prose to confirm exactly two count surfaces before 33→34 |
