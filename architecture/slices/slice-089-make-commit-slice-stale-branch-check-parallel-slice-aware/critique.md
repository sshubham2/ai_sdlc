# Critique: Slice 089 make-commit-slice-stale-branch-check-parallel-slice-aware

**Critic reviewed**: mission-brief.md, design.md, ADR-081, project-frame.md
**Date**: 2026-05-31
**Result**: BLOCKED (Critic self-assessment; final verdict computed at TRI-1 from dispositions)

## Summary

The core idea (worktree-backing as the stale-vs-active discriminator) is sound and reuses the right subsystem. But the design had a load-bearing correctness defect: it built the orphan set by subtracting the *filtered* `detect_active_worktrees()`, which silently drops worktree-backed branches (prunable, no-name-suffix, detached) into the refuse set; the current slice's own worktree was not reliably excluded; the CLI exit contract diverged from the cited sibling; and the methodology-changelog (MEPD-1) obligation was undischarged. All findings accepted; most fixed in design at this step, two carried to build.

## Findings

### Blockers (must address before /build-slice)

#### B1: Current slice's OWN worktree is in `detect_active_worktrees()` output — exclusion mechanism mismatched and unverified
- **Claim under review**: design.md "Computed by reusing `detect_active_worktrees()` … returns the set of non-main BRANCH-2 slice worktrees" + "`git symbolic-ref --short HEAD` (current branch to exclude)".
- **Issue**: `detect_active_worktrees()` (pulse_worktree_resolver.py:308-309) filters only the MAIN worktree (`blocks[1:]`); it returns the current slice's own worktree too. Under BRANCH-2, `--merge` runs from the slice's own worktree, so the slice-being-committed would appear in its own parallel-set. Exclusion-by-branch-name is inconsistent with the path-keyed data source and depends on an unwritten ordering assumption (the classifier must run at pre-flight, before sub-step 3's `cd` to main — else HEAD is `master` and excludes nothing).
- **Evidence**: pulse_worktree_resolver.py:308-309; SKILL.md:167 (pre-flight) vs :221 (sub-step 3 cd); CLAUDE.md BRANCH-2.
- **Proposed fix**: Self-exclude by worktree PATH (`git rev-parse --show-toplevel`, normalized `\`→`/`) path-equality against the worktree-backed set, plus defense-in-depth current-branch exclusion. Document the pre-`cd` ordering invariant. Add a test: current-slice-worktree + one peer → `parallel_slices` contains only the peer.
- **Builder draft**: ACCEPTED-FIXED at design.md § Core design decision + § Components touched (path-based self-exclusion via `git rev-parse --show-toplevel`; explicit pre-flight ordering invariant; folded into B3's switch to a raw-porcelain worktree-backing query).

#### B2: APED-1 — worktree classification reasoned, not executed against real porcelain
- **Claim under review**: design.md § Error model "deterministic binary from git worktree list"; prompt concern (e).
- **Issue**: Per APED-1 (slice-087 B1, slice-085 "battery author ≠ regex author"), the allow/refuse classification was never executed on a repo that has BOTH a worktree-backed peer AND a worktree-less orphan. Executing `detect_active_worktrees(Path('.'))` returns `[]` here (no slice worktrees registered) — the set-difference orphan logic is unobserved on a populated repo.
- **Evidence**: Critic executed `detect_active_worktrees(Path('.'))` → `[]`; slice-087 B1 lesson.
- **Proposed fix**: Build a real two-worktree fixture (`git worktree add` a peer `slice/NNN-name` + a worktree-less `git branch slice/999-orphan`), run the classifier, paste observed `parallel_slices`/`orphan_branches`/`verdict` into design.md or build-log.md; code-Critic (second APED-1 author) independently re-runs at `/code-review`.
- **Builder draft**: ACCEPTED-PENDING — executed at `/build-slice` kickoff (becomes the mid-slice smoke evidence) with the real two-worktree fixture; code-Critic re-runs as second APED-1 author. The classifier code does not exist yet, so the populated-repo execution is a build-time obligation, pinned here so it is not skipped.

#### B3: `detect_active_worktrees` filter cascade silently reclassifies worktree-backed branches as orphans → false-refuse (R-7 violation)
- **Claim under review**: ADR-081 "worktree-less always refuses"; design.md "a worktree-less `slice/*` branch is a genuine orphan".
- **Issue**: Building `orphan_branches` by subtracting `detect_active_worktrees` output is wrong: that function filters worktree-backed branches for reasons unrelated to orphan-ness — **prunable** (L313), **`slice/NNN` without `-name` suffix** (`_SLICE_BRANCH_RE` L320-322), **detached HEAD**, **bare repo** (L305-307 returns `[]`), **path-gone** (L328). A worktree-backed `slice/077` (no name) IS returned by `git for-each-ref refs/heads/slice/` but NOT by `detect_active_worktrees` → false orphan → false STOP. Silent misclassification via a detection-filter quirk violates must-not-defer #3 (R-7).
- **Evidence**: pulse_worktree_resolver.py:305-307, :313, :320-322, :328 (all confirmed on disk); mission-brief must-not-defer #3.
- **Proposed fix**: Determine worktree-backing by parsing `git worktree list --porcelain` **branch lines directly** (reuse the raw `_parse_worktree_porcelain`, NOT the slice-name-filtered `detect_active_worktrees`), so backing is independent of the name-suffix regex. Surface a distinct conservative note for a worktree-backed but non-canonically-named branch ("`slice/077` has a worktree but a non-canonical name — refusing conservatively; rename per ADR-063").
- **Builder draft**: ACCEPTED-FIXED at design.md § What's reused + § Components touched + § Error model — switch the worktree-backing query from `detect_active_worktrees` to the raw `_parse_worktree_porcelain` (extract every `branch refs/heads/slice/*` line, prefix-stripped), independent of `_SLICE_BRANCH_RE`. This is the single most important fix and resolves B1's path-keying too.

### Majors (address this slice)

#### M1: CSP-1 exit-code parity break — design uses 0/2, both cited siblings use 0/1/2
- **Claim under review**: design.md "CSP-1 parity … exit 0 success / 2 malformed-or-usage-failure".
- **Issue**: `pulse_worktree_resolver.py:26` documents and implements **0 success / 1 runtime error / 2 malformed args** (confirmed on disk). Collapsing git-unavailable/not-a-repo into exit 2 breaks parity AND mis-triggers the skill bootstrap-fallback (a runtime git error would not match an "exit 2" trigger).
- **Evidence**: pulse_worktree_resolver.py:26, :591/:596/:611.
- **Proposed fix**: Adopt 0 success / 1 runtime (git unavailable, not-a-repo, git cmd failure) / 2 malformed args. Update skill bootstrap-fallback to trigger on exit ∈ {1,2} OR `ModuleNotFoundError`.
- **Builder draft**: ACCEPTED-FIXED at design.md § Components touched (CLI) + § Error model + sub-step 5 bootstrap-fallback (trigger on exit∈{1,2} OR import failure).

#### M2: `--merge` and `--push` not structurally symmetric + `--push`→`--sync-after-pr` window
- **Claim under review**: AC #2 "symmetric … no divergence"; design.md "both surfaces, identical shape".
- **Issue**: (1) The stale check sits at different positions (`--merge` sub-step 1; `--push` pre-flight #2 of 4) — two near-identical prose blocks invite a stale-edit at one site (BC-PROJ-14 / FBCD-1). (2) After `--push` the slice branch KEEPS its worktree (SKILL.md:260) until `--sync-after-pr`; such a worktree-backed post-push branch is neither active-peer nor orphan.
- **Evidence**: SKILL.md:167, :242, :260.
- **Proposed fix**: (a) State the two blocks are byte-identical; add a parity test asserting the stale-check prose at the two sites matches. (b) Resolve the `--push` window: B1 self-exclusion covers the *current* pushed branch; a *prior*-pushed peer with a worktree correctly surfaces as a benign parallel note. Write it down.
- **Builder draft**: ACCEPTED-FIXED at design.md (byte-identical statement + `--push` window resolution) + ACCEPTED-PENDING for the FBCD-1 prose-parity test (authored at `/build-slice`).

#### M3: Bootstrap-fallback "no weaker than today" incomplete — must also self-exclude current branch; legacy "non-current" mechanism is unwritten
- **Claim under review**: design.md sub-step 5 "legacy flag-all (STOP if any non-current slice/* ref)".
- **Issue**: Confirmed on disk: shipped SKILL.md:167 says "if any **non-current** slice/* branches return, STOP" but shows NO exclusion mechanism. Under BRANCH-2 the current branch IS `slice/*`; a literal flag-all fallback would STOP on the current slice's own branch and `--merge` could never run.
- **Evidence**: SKILL.md:167 (confirmed — "non-current" asserted, no mechanism shown).
- **Proposed fix**: Specify that BOTH the classifier and the bootstrap-fallback exclude the current branch (`git symbolic-ref --short HEAD`) before evaluating remaining `slice/*` refs; make the legacy fallback explicitly `for-each-ref minus current`. Note the inherited prose ambiguity is being resolved (the new prose makes the exclusion explicit).
- **Builder draft**: ACCEPTED-FIXED at design.md sub-step 5 (both paths self-exclude current; legacy fallback = for-each-ref minus current-branch, explicit).

### Minors (log; address if cheap)

#### m1: ADR-081 reversibility "revert to flag-all is one line" is optimistic
- **Issue**: Reverting touches two SKILL.md blocks + deletes a tool + test + re-pins OSDG-1 drift. Not one line.
- **Proposed fix**: Reword to "cheap — revert the two SKILL.md prose blocks to the legacy `for-each-ref` check and delete the helper; the bootstrap-fallback already IS the legacy check."
- **Builder draft**: ACCEPTED-FIXED at ADR-081 § Reversibility.

#### m2: `for-each-ref` orphan-source format not pinned
- **Issue**: Orphan set depends on the exact `for-each-ref` format; must strip `refs/heads/` to compare against the porcelain `branch` lines (already prefix-stripped at L319). Format mismatch → false orphans.
- **Proposed fix**: Pin `--format='%(refname:short)'` (or document the strip) in design.md; assert branch-name normalization matches the porcelain branch set in the test.
- **Builder draft**: ACCEPTED-FIXED at design.md § Components touched (pin `%(refname:short)` + normalization assertion in the test plan).

#### MEPD-1: methodology-changelog obligation undischarged (raised by Critic under Dim 7 / Cross-cutting)
- **Issue**: The slice changes behaviour on a methodology surface (`skills/commit-slice/SKILL.md`) but design.md/ADR-081 name no minted RULE-ID, changelog entry, PMI-1 bump, NOR a documented-why-none rationale — risks failing MEPD-1 at pre-finish.
- **Proposed fix**: Add an explicit MEPD-1 **EXCLUDE** rationale: this is a behaviour-refining fix-slice with an ADR (ADR-081) and **no new RULE-ID** (it refines the existing BRANCH-2/PSQ-family guardrail), matching the documented EXCLUDE precedent N≥6 (077/079/082/084/085/086/087). No methodology-changelog/VERSION bump; forward-sync gates no-op.
- **Builder draft**: ACCEPTED-FIXED at design.md § MEPD-1 disposition (EXCLUDE with N≥6 precedent citation).

## Dimensions checked
- [x] Unfounded assumptions — B1, B2, M3
- [x] Missing edge cases — B3 (prunable / no-name / detached / bare / path-gone), M2.2 (`--push`→`--sync-after-pr` window)
- [x] Over-engineering — none (minimal read-only helper reusing an existing parser)
- [x] Under-engineering — AC #3 "genuine" qualifier not delivered without the B3 fix
- [x] Contract gaps — M1 (exit-code parity), m2 (for-each-ref format)
- [x] Security — none (read-only git inspection; narrows a refusal set; `.resolve()`d Path; no injection)
- [x] Drift from vault — Dim-7 strategic-fit: ALIGNS with PSQ/BRANCH/PCR trajectory; MEPD-1 obligation flagged (now EXCLUDE-rationalized)
- [x] Web-known issues — skipped (local read-only git; porcelain ordering invariant already pinned)
- [x] Cross-cutting conformance — M1 (CSP-1), B3 (pre-existing-filter-domination class), m2 (parser-parity normalization), MEPD-1

## Triage

**Triaged by**: user
**Date**: 2026-05-31
**Final verdict**: NEEDS-FIXES

Reconciles BOTH passes (first Critic critique.md + meta-Critic critique-review.md EXTEND). User ratified all dispositions as drafted (TRI-1, 2026-05-31). No OVERRIDDEN/DEFERRED/ESCALATED. Verdict NEEDS-FIXES because B2 + the M2 FBCD-1 parity test are ACCEPTED-PENDING (discharged during /build-slice).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md path-based self-exclusion (`git rev-parse --show-toplevel`) + pre-flight ordering invariant |
| B2 | Blocker | ACCEPTED-PENDING | real two-worktree fixture executed at /build-slice kickoff (mid-slice smoke); code-Critic second APED-1 author |
| B3 | Blocker | ACCEPTED-FIXED | switch worktree-backing query to raw `_parse_worktree_porcelain` (independent of name-suffix regex) |
| B-add-1 | Blocker | ACCEPTED-FIXED | meta-Critic: algorithm now strips `refs/heads/`→short-form before set ops; `test_worktree_backing_uses_short_form_not_raw_refname` asserts vs real porcelain |
| M1 | Major | ACCEPTED-FIXED | exit 0/1/2 sibling parity; bootstrap-fallback triggers on exit∈{1,2} OR import failure |
| M2 | Major | ACCEPTED-FIXED | byte-identical prose stated + `--push` window resolved; FBCD-1 parity test ACCEPTED-PENDING at build |
| M3 | Major | ACCEPTED-FIXED | both classifier + fallback self-exclude current branch; legacy fallback = for-each-ref minus current |
| M-add-1 | Major | ACCEPTED-FIXED | meta-Critic: self-exclusion correct IFF path-OR-branch fires; Windows case/separator mismatch test variant |
| m1 | Minor | ACCEPTED-FIXED | ADR-081 reversibility reworded |
| m2 | Minor | ACCEPTED-FIXED | pin `%(refname:short)` + normalization assertion |
| m-add-1 | Minor | ACCEPTED-FIXED | meta-Critic: boundary cases (zero-slice-refs, worktree-on-default) enumerated in design + suite |
| MEPD-1 | Minor | ACCEPTED-FIXED | EXCLUDE rationale (N≥6) + behaviour-boundary reservation sentence added to design.md |
