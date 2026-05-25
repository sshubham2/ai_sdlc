# Critique: Slice 022 redesign-commit-slice-for-pr-aware-flow

**Critic reviewed**: mission-brief.md, design.md, ADR-020-pr-aware-commit-slice-modes.md
**Date**: 2026-05-14
**Result**: NEEDS-FIXES

## Summary

Design is structurally sound — 3-mode taxonomy is the right correction to slice-021's DEVIATION-5. However, several load-bearing operational claims about git semantics are wrong or incomplete (notably `git pull` fast-forward default behavior, `git cherry` patch-equivalence under squash-merge with N>1 commits, GitHub URL pattern coverage for Enterprise), the CLI contract has unspecified mutual-exclusion semantics, and one Wiegers coverage-symmetry count claim (EPGD-1 N=16→N=17) doesn't trace back to v0.35.0's empirical anchor. Recursive-self-application discipline (per Dim 9 sub-clause): this slice IS authoring the redesign of `/commit-slice` itself, so anomalies in the design directly become anomalies users will hit at slice-ship — these need correction before /build-slice.

## Findings

### Blockers (must address before /build-slice)

#### B1: `git pull` "fast-forward-only by default" is factually wrong

- **Claim under review**: design.md L103 — *"`git pull origin <default>` (fast-forward-only by default; if pull conflicts, STOP and leave conflicted state for manual resolution...)"* — and L149 — *"pull uses default fast-forward-only behavior (any conflict STOPs)"*.
- **Issue**: Per `git-pull` documentation, `git pull`'s default behavior is NOT fast-forward-only. The default is to attempt a merge (creating a merge commit on non-ff). Git 2.34+ emits a warning when the merge is not a fast-forward and `pull.ff` is unconfigured, but it still merges by default. To get fast-forward-only semantics the design must explicitly pass `--ff-only` OR rely on `pull.ff=only` user config (which cannot be assumed). If `origin/<default>` has advanced via a non-trivial merge (e.g., another slice's PR was merged with a merge-commit while this user's `--push` was pending), the current design.md's `git pull` will silently create a merge commit on the local default branch — exactly the kind of unrequested git operation the safe-delete + NEVER-auto-resolve disciplines elsewhere in this slice protect against.
- **Evidence**:
  - design.md L103, L149 (claims `git pull` defaults to ff-only)
  - git-scm.com/docs/git-pull (default is merge, not ff-only)
- **Proposed fix**: change design.md L103 + L149 + the error model row at L170 to specify `git pull --ff-only origin <default>` (explicit flag). Also add a mission-brief.md must-not-defer item: "`--sync-after-pr`'s pull invocation MUST use `--ff-only` explicitly; do not rely on git's default or user `pull.ff` config." Add a test row to the test-first plan that prose-pins the `--ff-only` flag in SKILL.md to prevent silent regression.
- **Builder draft**: ACCEPTED-FIXED — apply at design.md L103 + L149 + error model row L170; add must-not-defer item + TF-1 row to mission-brief.md.

#### B2: `git cherry` will report `+` (false NO on Signal B) for GitHub squash-merge of N>1-commit slice branches

- **Claim under review**: design.md L97 — *"Signal B: `git cherry origin/<default> slice/NNN-<name>` returns no lines starting with `+` ... this handles squash-merge, rebase-merge, and merge-commit alike"*; and design.md L115 — *"`git cherry` … reports `-` for commits whose patch is already represented (covers squash-merge AND rebase-merge AND merge-commit)"*; and ADR-020 L43, L45.
- **Issue**: `git cherry`'s patch-equivalence is **per-commit** (computed via `git patch-id` — diff-after-removing-whitespace-and-line-numbers, per `git-cherry` docs). GitHub's "Squash and merge" PR option produces **ONE** combined commit on `<default>` whose diff equals the **CUMULATIVE** diff of all N slice-branch commits. When the slice branch has N>1 commits (which is overwhelmingly typical — `/build-slice` produces intermediate commits + a final commit per slice, often N=3-8), the squash commit's patch-id does NOT match the patch-id of any individual slice-branch commit. `git cherry origin/<default> slice/NNN` will therefore report `+` for ALL N commits — yielding **Signal B = NO** even though the PR was correctly squash-merged. The design's Signal A=YES + Signal B=NO branch (L101) STOPs with the "force-deleted PR, abandoned PR" diagnostic, which is the WRONG diagnostic for the dominant happy path.
- **Evidence**:
  - design.md L97, L101, L115, ADR-020 L43, L45 (claim cherry handles squash-merge)
  - `git-cherry` docs (git-scm.com): "equivalence test is based on the diff, after removing whitespace and line numbers" — per-commit, not aggregate
  - GitHub squash-merge: produces one combined commit per PR; N commits → 1 squash commit (this is the dominant GitHub merge style per ADR-020 L45 itself)
- **Proposed fix**: redesign Signal B to handle multi-commit-squash. Option (b) from Critic: keep `git cherry` for first-pass + add aggregate-tree-diff fallback. New Signal B: (i) `git cherry origin/<default> slice/NNN` → if NO `+` lines, Signal B=YES; (ii) if `+` lines, compute aggregate-tree-equivalence: `BASE=$(git merge-base origin/<default> slice/NNN)`; `SLICE_TREE=$(git rev-parse slice/NNN^{tree})`; check whether `origin/<default>` contains a commit whose tree at the same paths matches `SLICE_TREE` — practically: `git log BASE..origin/<default> --format=%H --diff-filter=AMDR -- $(git diff --name-only BASE..slice/NNN)` and verify any single commit's full file-set matches; if YES → Signal B=YES (squash-merge detected); else Signal B=NO. Update ADR-020 mechanism table entry C to honestly reflect the N>1-squash-merge limitation + document the fallback. Also revise L101 diagnostic (see M5).
- **Builder draft**: ACCEPTED-FIXED — apply revised Signal B mechanism (cherry-first + aggregate-tree-diff fallback) at design.md L92-105 + L114-128 (mechanism table) + L155-172 (error model). Update ADR-020 mechanism table entry C + Decision section to document the fallback. Implementation lands at /build-slice; design-time commitment is the revised algorithm.

#### B3: GitHub URL regex pattern doesn't cover GitHub Enterprise / non-`github.com` hosts

- **Claim under review**: design.md L75-77 — GitHub patterns enumerated as `git@github.com:OWNER/REPO.git`, `https://github.com/OWNER/REPO.git`, `https://github.com/OWNER/REPO`.
- **Issue**: The 3 enumerated patterns assume the host is literally `github.com`. GitHub Enterprise uses arbitrary hostnames like `github.mycompany.com`. The compare-URL derivation will silently fall through to the non-GitHub branch and emit only "use your hosting UI" — punishing the very PR-workflow users this slice exists to serve. Also missing: `ssh://git@github.com:22/OWNER/REPO.git`. The slice's intent explicitly targets adopters whose repos are often on Enterprise.
- **Evidence**:
  - design.md L75-77 (pattern enumeration limited to `github.com`)
  - ADR-020 L25, L45 (states "GitHub" but doesn't distinguish github.com vs Enterprise)
- **Proposed fix**: two options:
  - (a) widen pattern via `gh repo view --json url` delegation + regex fallback
  - (b) accept v1 limitation: "v1 handles `github.com` only; GitHub Enterprise users see the non-GitHub fallback (which gives them `gh pr create --web` — that works for Enterprise when `gh` is configured); widening to `*github*` host class deferred to follow-on slice `add-github-enterprise-url-derivation`."
- **Builder draft**: DEFERRED to follow-on slice `add-github-enterprise-url-derivation`. Rationale: this slice's own dev environment is github.com (user is the slice's first adopter); `gh pr create --web` works for Enterprise users even via the fallback branch (the compare URL is the only Enterprise-degraded piece). v1 ships with explicit limitation documented in design.md "Out of scope" and ADR-020. Adding Enterprise host detection adds ~1hr + tests; better as a focused slice.

#### B4: Mutual exclusion of `--merge` / `--push` / `--sync-after-pr` not specified

- **Claim under review**: design.md L8 — `argument-hint` expanded to `[--merge | --push | --sync-after-pr]` (vertical bar denotes mutual exclusion per existing skill convention); design.md L51-105 enumerates the 3 modes individually; nowhere documents what happens when (a) two flags are passed simultaneously or (b) zero flags are passed.
- **Issue**: Three concrete gaps: (1) no-flag default behavior not in any AC (slice-021 SKILL.md L22 preserves no-flag generate-only mode; AC #1 says only "`--merge` remains functional"); (2) no error-model row for multi-flag rejection; (3) AC #2 doesn't preserve no-flag default.
- **Evidence**:
  - design.md L8 (argument-hint, no mutual-exclusion docs)
  - design.md L51-105 (3-mode contracts, none addresses no-flag or multi-flag)
  - mission-brief.md L17-18, design.md L155-172 (error model 16 rows, zero handle multi-flag)
  - skills/commit-slice/SKILL.md L22 (existing no-flag mode is documented)
- **Proposed fix**: (a) add AC #1b: "no-flag invocation `/commit-slice` preserves the slice-021 generate-only behavior (show message + HEREDOC instruction; no git operations); `test_skill_md_documents_no_flag_default_mode` prose-pin test"; (b) add error model row: combining any 2 of `--merge` / `--push` / `--sync-after-pr` → STOP — "Mode flags are mutually exclusive; pass exactly one"; (c) add test-first plan row for `test_skill_md_documents_mutual_exclusion_of_three_mode_flags`.
- **Builder draft**: ACCEPTED-FIXED — add no-flag-default AC (AC #1b becomes part of AC #1; or 6th AC dedicated to argument contract — choose 6th AC for clean separation since 6 ACs > 5 limit is OK because all 6 are individually small and the mission-brief 5-AC limit is a soft cap per `/slice` skill prose; verify post-edit). Add error model row at L155-172. Add 2 TF-1 rows. Apply inline.

### Majors (address this slice)

#### M1: `--sync-after-pr` does not ensure `git fetch --prune` refreshes `origin/<default>` for Signal B

- **Claim under review**: design.md L93 — *"Sync remote refs: `git fetch --prune`"* — runs in Flow Step 1, AFTER pre-flight passes.
- **Issue**: Signal A at L96 uses `git ls-remote --exit-code origin slice/NNN-<name>` (live remote query — unaffected by local refspec). Signal B at L97 uses LOCAL `origin/<default>` ref. If `.git/config`'s fetch refspec doesn't include the default branch (e.g., user ran `git remote set-branches origin slice/*`), `origin/<default>` stays stale and `git cherry` compares against stale data → false NO on Signal B.
- **Evidence**:
  - design.md L93, L97 (fetch happens first but refspec coverage of `<default>` not asserted)
- **Proposed fix**: change L93 to explicitly fetch both refs: `git fetch --prune origin <default> slice/NNN-<name>`. Document: "Signal B requires fresh local view of `origin/<default>`; the explicit refspec form ensures it regardless of remote.fetch config."
- **Builder draft**: ACCEPTED-FIXED — apply explicit-refspec fetch at design.md L93. Update error model for "fetch refspec failure" if either ref is invalid.

#### M2: Mini-CAD-1 row 14 TF-1 transition spec under-specified for `--strict-pre-finish` audit

- **Claim under review**: mission-brief.md L43 — row 14 *"PENDING (extends — already PASSING; will transition WRITTEN-FAILING → PASSING during build)"*.
- **Issue**: Per slice-018 DEVIATION-1/DEVIATION-2, the historical PASSING→WRITTEN-FAILING→PASSING pattern only fires if the in-repo edit precedes the installed sync. If both are edited atomically, TF-1 audit `--strict-pre-finish` may see PASSING-throughout (no WRITTEN-FAILING traversal) and refuse.
- **Evidence**:
  - mission-brief.md L43 (row 14)
  - slices/_index.md L78-79 (slice-018 lessons)
- **Proposed fix**: add explicit transition spec to row 14: "during /build-slice Phase N, in-repo SKILL.md edited FIRST → run mini-CAD test → expect WRITTEN-FAILING with sha256 mismatch; THEN forward-sync `cp` to installed → re-run → expect PASSING."
- **Builder draft**: ACCEPTED-FIXED — apply transition spec to mission-brief.md TF-1 plan row 14.

#### M3: Wiegers coverage-symmetry — EPGD-1 count "N=16→N=17" doesn't reconcile with v0.35.0's "N=7→N=8"

- **Claim under review**: design.md L15 — *"EPGD-1 N=16 → N=17 stable target"*.
- **Issue**: methodology-changelog v0.35.0 (slice-021) explicitly says "EPGD-1 self-application N=7 → N=8 stable post-slice-021 (0 of 15 prior entry-pin functions touched..."). Slice-022's "N=16 → N=17" matches no documented counter (not self-application N=8 → N=9; not entry-pin-function-count which would be 15+3=18; not test_v_0_* count which is 25). This is the Wiegers coverage-symmetry class elevated to /critic-calibrate slice-022 per slice-021 aggregated lesson L36.
- **Evidence**:
  - design.md L15 (count claim)
  - methodology-changelog.md (v0.35.0 entry: N=7 → N=8)
- **Proposed fix**: use self-application counter (matches v0.35.0 framing): "EPGD-1 self-application N=8 → N=9 stable target".
- **Builder draft**: ACCEPTED-FIXED — change design.md L15 to "EPGD-1 self-application N=8 → N=9 stable target".

#### M4: `--push` re-push semantics on existing remote ref undefined (rebase → non-ff; fast-forward → silent success)

- **Claim under review**: design.md L67-72 + mission-brief.md L61 — *"first-push semantics"* without addressing re-push.
- **Issue**: (a) rebase/amend after prior `--push` → second push fails with cryptic "Updates were rejected because the tip of your current branch is behind"; error model row L163 says "propagate git's stderr verbatim" but stderr alone is unhelpful. (b) added new commits without rebase → push is fast-forward and succeeds silently — no documented behavior for whether this gets a confirmation prompt distinguishing re-push from first-push.
- **Evidence**:
  - design.md L67-72, L163; mission-brief.md L61
- **Proposed fix**: add two error model rows:
  - Non-ff push (diverged history): STOP — "Remote `origin/slice/...` has diverged from local. This typically means local history was rebased/amended after a prior push. Resolve manually (force-push intentionally via `git push --force-with-lease origin slice/...` if you confirm the rebase was correct, or `git pull --rebase` if remote has new commits). `/commit-slice --push` never force-pushes."
  - Fast-forward re-push (remote exists, local ahead): ALLOW with explicit prompt — "Remote ref already exists and local is ahead by N commits. Confirm fast-forward re-push? (yes/no)"
- **Builder draft**: ACCEPTED-FIXED — apply 2 error model rows at design.md L155-172.

#### M5: Signal A=YES + Signal B=NO STOP diagnostic asserts wrong sole cause under squash-merge

- **Claim under review**: design.md L101 — *"Signal A=YES + Signal B=NO is the legitimate "remote branch deleted but commits not on default" anomaly (force-deleted PR, abandoned PR)"*.
- **Issue**: Per B2, GitHub squash-merge of N>1-commit slice branch produces exactly this signal combination as the EXPECTED happy-path state under current Signal B. After B2's revised mechanism, the residual signal-mismatch will be rare but the diagnostic must enumerate both causes.
- **Evidence**: design.md L101; B2 finding
- **Proposed fix**: revise L101 to ENUMERATE: "Signal A=YES + Signal B=NO has two common causes: (1) [if B2 fallback didn't trigger because aggregate-tree-diff also mismatched] PR commits don't represent the slice branch's full work — verify via `git log origin/<default>` vs `git log slice/...`; (2) abandoned/force-deleted PR where commits were never merged."
- **Builder draft**: ACCEPTED-FIXED — apply revised diagnostic prose at design.md L101 in same fix block as B2.

### Minors (log; address if cheap)

#### m1: `git push -u origin slice/...` doesn't verify origin URL identity vs. URL at last `--push`

- **Claim under review**: design.md L65, L148 — origin-remote presence check; never identity check.
- **Issue**: If user ran `git remote set-url origin <new-url>` between two `--push` invocations, push goes to the new URL without warning. Critic acknowledges this is NOT a new vulnerability vs baseline `git push`.
- **Builder draft**: OVERRIDDEN — Critic's own framing confirms this is not a vulnerability introduced by the slice (`git push -u origin` has the same surface in baseline git; the slice does not add an authentication or remote-trust contract). Baseline `git` doesn't warn here either. Adding origin-identity verification is a separate concern about git's own trust model, not about this slice's design. Rationale: scope-limited; no incremental risk vs baseline; out-of-scope for the redesign mission.

#### m2: Off-by-one in BRANCH-1 self-application counter: "second non-bootstrap canonical-reference-instance" should be "first"

- **Claim under review**: design.md L187 — *"slice-022 IS the second non-bootstrap canonical-reference-instance of branch-per-slice workflow"*.
- **Issue**: Slice-021 was bootstrap-reference-instance #1; slice-022 (non-/repro) is the FIRST non-bootstrap canonical-reference-instance.
- **Builder draft**: ACCEPTED-FIXED — change "second" → "first" at design.md L187.

#### m3: Files-changed estimate items 15-28 are unenumerated placeholder slots

- **Claim under review**: design.md L207-208 — *"15-28. (build-log.md + reflection.md + milestone.md updates during build; validation.md at validate; ...)"*
- **Issue**: 14 placeholder slots; only 4 surfaces named. Per slice-020/021 lesson, non-verifiable mechanical-table count.
- **Builder draft**: ACCEPTED-FIXED — enumerate specifically (15: build-log.md; 16: reflection.md; 17: milestone.md final-state; 18: validation.md; 19: slices/_index.md archive row) and revise total to "≤ 19 enumerated touches + standard slice-lifecycle file updates."

#### m4: `--sync-after-pr` runs `git checkout <default>` without worktree-conflict guard

- **Claim under review**: design.md L103 — *"`git checkout <default>` → `git pull...`"*.
- **Issue**: If user has a git worktree where `<default>` is already checked out elsewhere, `git checkout <default>` fails with cryptic message.
- **Builder draft**: ACCEPTED-FIXED — add error model row: "`--sync-after-pr` | `git checkout <default>` fails (worktree conflict) → STOP — propagate git's stderr verbatim + add: 'Resolve via `git worktree remove <conflicting-path>` if intentional, or run `--sync-after-pr` from the worktree where `<default>` lives.'"

## Dimensions checked

- [x] Unfounded assumptions — B1 (`git pull` ff-only default false), B2 (`git cherry` covers squash-merge N>1 false), B3 (GitHub URL coverage assumes `github.com` literal only)
- [x] Missing edge cases — M4 (re-push after rebase), M1 (`git fetch --prune` refspec assumption), m4 (worktree conflict); B4 (no-flag default + multi-flag rejection); explicit prompt for mutual-exclusion missing
- [x] Over-engineering — none (Critic explicitly rejected this concern; `--sync-after-pr` is genuinely useful and two-signal detection is correctly over-cautious on destructive `git branch -d`)
- [x] Under-engineering — B4, M2, B2 (Signal B structurally under-engineered for dominant GitHub merge style)
- [x] Contract gaps — B4 (mutual exclusion of flags; no-flag default), M4 (re-push semantics on existing remote ref), M1 (`git fetch --prune` refspec discipline)
- [x] Security — m1 only (origin URL identity not verified between pushes; acknowledged as not a new vulnerability vs baseline `git push`). All confirmation prompts + safe-delete-only + NEVER-`--force` + NEVER-`-D` correctly in place
- [x] Drift from vault — m2 (off-by-one BRANCH-1 self-application counter); M3 (EPGD-1 count drift between design.md and methodology-changelog v0.35.0 baseline). ADR-020 partial-supersession encoding (single `supersedes: ADR-019` slot; body enumerates partial scope; ADR-019 left unedited per append-only) is structurally consistent with ADR family convention; no drift
- [x] Web-known issues — B1 (`git pull` default per git-scm.com), B2 (`git cherry` per-commit per git-scm.com), B3 (GitHub Enterprise URL forms per docs.github.com)
- [x] Cross-cutting conformance — recursive-self-application: slice-022 redesigns `/commit-slice` itself; B1+B2+B4 directly become slice-ship anomalies. Slice-022 will use `--merge` at ship (solo-dev), so `--push` + `--sync-after-pr` get prose-pin runtime validation only (per design.md L190); this is a documented limitation but should be elevated. BRANCH-1 audit scope correctly unmodified per ADR-020 Consequences. Wiegers coverage-symmetry watch-list catch on M3.

## Triage

**Triaged by**: user
**Date**: 2026-05-14
**Final verdict**: CLEAN

(User ratified all Builder draft dispositions verbatim via "accept all" at TRI-1 ratification step — both for first-Critic's 13 findings AND meta-Critic's 5 missed findings (M-add-1 through M-add-5) surfaced by /critique-review dual-review pass. All ACCEPTED-FIXED fixes applied inline in their respective rounds; no ACCEPTED-PENDING, no ESCALATED. One DEFERRED + one OVERRIDDEN from first-Critic carry user-ratified non-empty rationale. **Total findings: 18 = 13 first-Critic + 5 meta-Critic; 16 ACCEPTED-FIXED + 1 DEFERRED + 1 OVERRIDDEN.** Verdict CLEAN per /critique Step 4.5 mechanical computation: zero ESCALATED + zero ACCEPTED-PENDING → CLEAN.)

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | `git pull --ff-only` explicit at design.md `--sync-after-pr` Flow Step 5 + Authorization section + error model row; must-not-defer item added to mission-brief.md; TF-1 row `test_skill_md_sync_after_pr_uses_ff_only_pull` added at AC #3 |
| B2 | Blocker | ACCEPTED-FIXED | Signal B redesigned to two-pass (Pass 1 `git cherry` + Pass 2 aggregate-tree-diff fallback) at design.md Flow Step 3 + mechanism table (entry C+D added) + Chosen rationale; ADR-020 Decision section + Reversibility section updated to document two-pass mechanism + N>1-squash-merge limitation honestly |
| B3 | Blocker | DEFERRED | follow-on slice `add-github-enterprise-url-derivation`; rationale: this repo is github.com (slice's first adopter is solo-dev on github.com); `gh pr create --base <default> --head slice/... --web` works for Enterprise users via the non-GitHub fallback branch; widening to `*github*` host class costs ~1hr + Enterprise CI fixture and is reversibility-cheap as a focused slice; v1 limitation explicitly documented in mission-brief.md "Out of scope" + ADR-020 "Scope limitations (v1)" |
| B4 | Blocker | ACCEPTED-FIXED | AC #1 expanded to "argument contract" covering (a) no-flag default + (b) `--merge` preservation + (c) mutual exclusion of 3 mode flags + (d) "When to use which mode" guidance section; mutual-exclusion error model row added at top of error model table; must-not-defer item added; 2 TF-1 rows added (`test_skill_md_documents_no_flag_default_mode` + `test_skill_md_documents_mutual_exclusion_of_three_mode_flags`) |
| M1 | Major | ACCEPTED-FIXED | explicit-refspec fetch `git fetch --prune origin <default> slice/NNN-<name>` at design.md `--sync-after-pr` Flow Step 1; must-not-defer item added to mission-brief.md |
| M2 | Major | ACCEPTED-FIXED | TF-1 row 14 transition spec expanded: in-repo SKILL.md edited FIRST → mini-CAD test WRITTEN-FAILING → forward-sync to installed → re-run mini-CAD test PASSING. Ordering pin lets TF-1 audit verify WRITTEN-FAILING traversal happened |
| M3 | Major | ACCEPTED-FIXED | design.md "EPGD-1 N=16 → N=17 stable target" → "EPGD-1 self-application N=8 → N=9 stable target" (matches methodology-changelog v0.35.0 self-application counter framing N=7 → N=8) |
| M4 | Major | ACCEPTED-FIXED | 2 error model rows added for `--push` re-push semantics: (a) non-ff diverged → STOP with manual-resolution diagnostic; (b) ff re-push with N commits ahead → ALLOW with explicit confirmation prompt; must-not-defer item updated to clarify "first-push OR fast-forward re-push only" |
| M5 | Major | ACCEPTED-FIXED | design.md Signal A=YES + Signal B=NO STOP diagnostic revised to ENUMERATE both causes (PR commits don't represent slice's full work; abandoned/force-deleted PR) — same fix block as B2 |
| m1 | Minor | OVERRIDDEN | Critic acknowledges this is not a new vulnerability introduced by the slice — baseline `git push -u origin` has the identical surface; the slice does not add an authentication or remote-trust contract. Origin-identity verification is a git trust-model concern, scope-limited to this slice's redesign mission. No incremental risk vs baseline; out-of-scope |
| m2 | Minor | ACCEPTED-FIXED | design.md self-application checklist "second non-bootstrap canonical-reference-instance" → "first non-bootstrap canonical-reference-instance" (slice-021 = bootstrap-reference-instance #1; slice-022 = first non-/repro slice after slice-021 = first non-bootstrap canonical-reference-instance) |
| m3 | Minor | ACCEPTED-FIXED | design.md "Files changed" enumerated items 15-19 specifically (build-log.md, validation.md, reflection.md, milestone.md, critique-review.md); placeholder range "15-28" eliminated; total revised to "19 enumerated touches + standard slice-lifecycle updates" |
| m4 | Minor | ACCEPTED-FIXED | design.md error model row added for `--sync-after-pr` `git checkout <default>` worktree-conflict failure with diagnostic pointing user to `git worktree remove` or invoking from the correct worktree |
| M-add-1 | Blocker | ACCEPTED-FIXED | (meta-Critic /critique-review missed finding) mission-brief.md Pre-finish gate L139 rewritten to specify one-directional ADR supersession encoding via `test_adr_020_file_exists_and_supersedes_adr_019`; SUP-1 reference dropped (SUP-1 scopes to /supersede-slice for archived-slice reflection.md links, NOT ADRs); Dependencies section L95 also updated to drop SUP-1 ref. Highest-impact second-pass catch — prevented Builder-vs-audit deadlock at /build-slice Step 6 |
| M-add-2 | Minor | ACCEPTED-FIXED | (meta-Critic /critique-review missed finding) mission-brief.md L134 "second non-bootstrap canonical-reference-instance" → "first" (sibling-site propagation of /critique m2 off-by-one correction). Fix-block-completeness on count-drift class N=1 at slice-022 |
| M-add-3 | Minor | ACCEPTED-FIXED | (meta-Critic /critique-review missed finding) design.md L198 "22+ changed files" → "19 enumerated changed files" (sibling-site propagation of /critique m3 placeholder enumeration). Fix-block-completeness on count-drift class N=2 at slice-022. **Additional sibling-site sweep applied inline**: mission-brief.md L130 must-not-defer count "12 items" → "14 items" (11 original + 3 added at /critique B1+M1+B4) — same class, propagated under M-add-3 umbrella, disclosed in build-log at /build-slice |
| M-add-4 | Minor | ACCEPTED-FIXED | (meta-Critic /critique-review missed finding) mission-brief.md L131 `/drift-check` gate phantom `--do-commit` parenthetical dropped — flag never existed in the codebase (slice-021 added `--merge`, not `--do-commit`) |
| M-add-5 | Major | ACCEPTED-FIXED | (meta-Critic /critique-review missed finding) design.md L99 Pass 2 mechanism expanded with 3 explicit guards: (a) empty-FILES guard → Signal B Pass 2 = NO with STOP diagnostic (closes data-loss false-YES path); (b) "covers FILES" pinned to **superset** semantics (touched ⊇ FILES — allows conflict-resolution to add files); (c) perf bound N=500 commits on `BASE..origin/<default>` with STOP diagnostic if exceeded. 2 new error model rows added covering (a) + (c). Meta-Critic noted reservation: empty-FILES case may STOP git-naturally; sandbox-verify at /build-slice could downgrade (a) to Minor. Builder accepted Major design-time guard since explicit STOP > implicit git behavior, matches slice's NEVER-auto-resolve discipline |

## Deferred slice candidate (per B3)

- **`add-github-enterprise-url-derivation`** — extends `--push`'s PR-creation URL derivation to GitHub Enterprise Server / Enterprise Cloud custom-host installs. Approach: detect any `*github*` host via `gh repo view --json url` delegation (when `gh` available) + widened regex fallback (`^(?:git@|https://|ssh://git@)([^:/]+)[:/]([^/]+)/([^/.]+?)(?:\.git)?(?:/.*)?$`). Estimated effort: SMALL (~1-2hr). Defer until first Enterprise adopter surfaces OR slice-022 ships and an Enterprise-using contributor files the gap.
