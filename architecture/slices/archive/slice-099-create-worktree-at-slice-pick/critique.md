# Critique: Slice 099 create-worktree-at-slice-pick

**Critic reviewed**: mission-brief.md, design.md, ADR-090 (new). Grounded against `tools/slice_queue_writer.py`, `tools/slice_queue_claim.py`, `tools/branch_workflow_audit.py`, `tools/parallel_conflict_resolver.py`, `tools/stranded_slice_audit.py`, `tools/pulse_worktree_resolver.py`, `skills/slice/SKILL.md`, `skills/build-slice/SKILL.md`, `methodology-changelog.md` (v0.80.0), `VERSION` (0.80.0).
**Date**: 2026-06-01
**Result**: BLOCKED (Critic's own assessment; final verdict computed at TRI-1 from dispositions)

## Summary

The intent is sound and the worktree-at-pick reorder is the right root-cause fix for R-31/R-17 pre-build residual. But two load-bearing mechanism claims are false against the actual code: (B1) PCR is a `git rebase`-stage SOFT resolver wired only into `/commit-slice --merge` — it does not and cannot resolve a direct `git commit` race on `master`; and (B2) a `## Pick log` top-level section provably does NOT survive `format_queue_md` regeneration (executed), and the "same mechanism as PSQ-2 claim-preservation" justification is structurally inapplicable. Plus an MEPD-1 version-bump fan-out is entirely unacknowledged (B3), the WORKTREE=skip-at-pick escape-hatch has no recording surface the build-time audit can read (B4), and the abandoned-pick "detectable as stranded" claim is overstated (M1).

## Findings

### Blockers (must address before /build-slice)

#### B1: "Route concurrent picks through PCR" does not hold — PCR is a rebase-stage resolver, not a direct-commit-on-master resolver
- **Claim under review**: design.md / ADR-090: "the per-pick queue commit on master reuses [PCR] for two-sessions-pick-at-once conflicts".
- **Issue**: `parallel_conflict_resolver.py` only auto-resolves the SOFT class by inspecting `git status --porcelain` for `U`-prefixed paths produced **during a `git rebase`**, invoked exclusively from `commit-slice` Step 5b sub-step 2.5. `skills/slice/SKILL.md` contains zero PCR/rebase/commit wiring. "Route through PCR" describes a code path that does not exist.
- **Evidence**: `parallel_conflict_resolver.py:1-34,57-69`; `commit-slice/SKILL.md:187-216`; `slice/SKILL.md` (no matches). Two worktrees cannot both check out `master` (git refuses), so the real race is either same-repo interleave or cross-clone push non-fast-forward — neither is the PCR SOFT path.
- **Proposed fix**: Pick one coherent model and trace its full git flow: (a) commit queue in the *main tree* + `git pull --rebase` → then PCR on the resulting `slice-queue.md` conflict (must be wired into slice SKILL.md); or (b) keep the queue write local at pick, defer the durable provenance commit to the next `/commit-slice` (already PCR-guarded).
- **Builder draft**: **ACCEPTED-FIXED** — the Critic is right; "route through PCR" is wrong. Fix in design.md + ADR-090: PSQ-2 is the **same-machine cooperative** model (ADR-067), so there is exactly ONE main tree with `master`; the per-pick queue write goes through `_vault_write.safe_write_text` (R-32 sidecar lock) and the queue-only commit on master is serialized by git's index lock — no rebase, no PCR. Cross-clone/multi-machine is explicitly out of scope (ADR-067 same-machine boundary). Remove every PCR reference for this path; fail-visible on lock contention.

#### B2: `## Pick log` does NOT survive `format_queue_md` regeneration — claim is empirically false
- **Claim under review**: design.md/ADR-090: "`format_queue_md` emits a preserved `## Pick log`; carries forward across regeneration (same mechanism as PSQ-2 claim-preservation); survives regeneration."
- **Issue**: (1) "same mechanism as PSQ-2" is structurally wrong — claim-preservation re-attaches `claimed_by`/`claimed_at` to surviving `### <name>` entry keys (`slice_queue_writer.py:729-801`); a `## Pick log` is a top-level `##` section with NO `### entry` key, invisible to `parse_queue_text` (`slice_queue_claim.py:114,252-264`). (2) `format_queue_md` rebuilds body as `header + ## Candidates` only (`slice_queue_writer.py:622-639`) — no pick-log emission. Executed and confirmed: a populated `## Pick log` is dropped on regeneration.
- **Evidence**: executed `parse_queue_text` + `format_queue_md` round-trip → `## Pick log present in regenerated body? False`.
- **Proposed fix**: Specify a NEW, distinct preservation path: (a) before regen, read the literal `## Pick log\n...EOF` tail; (b) re-append it verbatim after `## Candidates`; (c) `record_pick` idempotent by scanning the block for an existing `- slice-NNN-<name> —` prefix. Add a regression test for pick-log survival. Correct the "same mechanism" wording.
- **Builder draft**: **ACCEPTED-FIXED** (design spec) + **ACCEPTED-PENDING** (implementation at build) — correct the wording now; specify the distinct read-tail/re-append preservation path + idempotency-by-prefix-scan in design.md; the `slice_queue_writer.py` code + survival regression test land at `/build-slice`.

#### B3: MEPD-1 / forward-sync + entry-pin + 4-part PMI-1 bump obligation entirely unacknowledged
- **Claim under review**: design.md: "ADR-090 (NEW) + methodology-changelog.md BRANCH-3 entry" — and nothing else about the version-bump fan-out.
- **Issue**: Mints a new RULE-ID (BRANCH-3) on methodology surfaces → must discharge: changelog entry under its own section, `test_v_0_81_0_branch_3_entry_present...` entry-pin, atomic 4-part PMI-1 bump (`VERSION` 0.80.0→0.81.0 + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced installed changelog), MCFS-1 + both version forward-sync legs, and re-sync the two OSDG-1-guarded installed SKILL.md copies. None is in design or the pre-finish gate.
- **Evidence**: `VERSION`=0.80.0; changelog `## v0.80.0`; forward-sync tools present; `test_methodology_changelog.py` entry-pin convention; `test_slice_skill_drift.py` + `test_build_slice_skill_drift.py` both exist.
- **Proposed fix**: Add a "Methodology version-bump fan-out" subsection + pre-finish gate items enumerating all of the above; plan the entry-pin INSERT structurally separate from any PMI-1 gate Edit (slice-014 discipline).
- **Builder draft**: **ACCEPTED-FIXED** (design + pre-finish gate enumerate the fan-out now) + execution at `/build-slice`. Valid — I noted the VERSION bump but did not spec the legs.

#### B4: WORKTREE=skip-at-pick has no recording surface the build-time audit can read
- **Claim under review**: must-not-defer + design.md: pick-time WORKTREE=skip "writes scaffold to main tree + records the rationale for build-time".
- **Issue**: The skip escape-hatch is a `build-log.md` Events line read by `branch_workflow_audit` (`:398-424`). At `/slice` pick-time there is no `build-log.md`. So a pick-time-skipped slice with scaffold on master, but no canonical line, trips `on-default-branch` Important at build (`:600-638`). The design never says who writes the canonical line or where.
- **Evidence**: `branch_workflow_audit.py:398-424,600-638`; `slice/SKILL.md` Step 6 writes only mission-brief + milestone.
- **Proposed fix**: Define the surface concretely — (a) `/slice` pre-creates `build-log.md` with the canonical `<YYYY-MM-DD HH:MM> DEVIATION: WORKTREE=skip — rationale: <text>` Events line at pick (build-time audit reads it unchanged); add a test that a pick-skipped slice passes the audit at build.
- **Builder draft**: **ACCEPTED-FIXED** — adopt option (a): `/slice` pre-creates a `build-log.md` Events stub carrying the canonical WORKTREE=skip line when a pick-time skip is requested; existing audit reads it unchanged (no audit-logic change). Spec in design.md now; stub-write code + test at build.

### Majors (address this slice)

#### M1: Abandoned-pick is IN_PROGRESS (informational), not stranded — "detectable as stranded" overstated
- **Issue**: A freshly-picked worktree has `stage: slice` → `classify_worktree_state` returns IN_PROGRESS (`pulse_worktree_resolver.py:403-407`) → `stranded_slice_audit` maps to `halt: false` informational (`:452-453,485-488`); `slice/SKILL.md:50` PROCEEDs without a gate. An abandoned pick is listed but never surfaces as an anomaly — and BRANCH-3 raises the abandon rate (worktree created before build-commitment).
- **Proposed fix**: (a) downscope the must-not-defer to "abandoned picks appear as IN_PROGRESS informational; no new detection class this slice; full distinction deferred"; or (b) specify a real discriminator (own slice).
- **Builder draft**: **ACCEPTED-FIXED** — adopt (a): honestly downscope the must-not-defer + ADR Consequences; note the BRANCH-3-raises-abandon-rate concern as a follow-up candidate (an `abandoned-pick-detection` slice). Do not claim detectability the code doesn't deliver.

#### M2: "branch_workflow_audit timing-agnostic / no violation-logic change" — cwd-mismatch now has live in-flight instances
- **Issue**: The `worktree-cwd-mismatch` check fires when the slice branch is in a worktree AND cwd is the main tree (`:600-620`). Under BRANCH-3 the worktree exists from pick onward, so any main-tree-cwd audit invocation during `/design-slice`/`/critique`/mid-slice-smoke now fires where it was dormant before. The mission-brief mid-slice smoke runs the audit directly — from which cwd?
- **Proposed fix**: Trace every pre-finish audit invocation's cwd; require they `cd` into the worktree (or carve out the new normal in-flight state). Reword "no violation-logic change".
- **Builder draft**: **ACCEPTED-FIXED** — reword the claim to "end-state validation unchanged; the dormant cwd-mismatch branch now has live in-flight instances"; specify that all pre-finish/mid-slice audit invocations run from within the worktree (cwd = worktree), so cwd-mismatch stays correct (worktree-cwd, not main-tree-cwd). No audit-logic change needed.

#### M3: Two worktrees cannot both check out `master` — per-worktree pick-commit model is impossible as drawn; two-tree dance + partial-failure unspecified
- **Issue**: The queue commit MUST happen in the **main tree** (where `master` is checked out), not the worktree (on `slice/NNN`). The design says both "write artifacts into the worktree" AND "commit on the default branch" without spelling out the two-tree sequence or partial-failure (worktree-add OK → queue-commit fail → orphan worktree + no/partial pick-log).
- **Proposed fix**: Add an explicit ordered sequence: compute paths → `git worktree add` + seed → write scaffold into worktree → `git -C <main-tree>` regenerate queue + append pick-log + commit ONLY slice-queue.md on master; document failure/rollback at each boundary (tie orphan-worktree to M1).
- **Builder draft**: **ACCEPTED-FIXED** — add the explicit ordered two-tree sequence + per-step failure/rollback to design.md; the queue write/commit is `git -C <main-tree>` on master while scaffold goes to the worktree. This is the concrete realization of the Q1 shared-ledger choice.

### Minors (log; address if cheap)

#### m1: `seed_derived_dirs` idempotency "absent/empty" underspecified (partial-seed)
- **Builder draft**: **ACCEPTED-FIXED** — define "already seeded" = target dir exists at all → skip (accept partial-seed risk, low likelihood); add a `test_seed_derived_dirs_idempotent` partial/pre-existing-dir case.

#### m2: AC5 "single source of truth" undercut by legacy point-4/point-2 prose still hand-writing the convention
- **Builder draft**: **ACCEPTED-FIXED** — narrow AC5 wording to "the *primary* (non-legacy) create path uses the shared helper; legacy escape-hatch prose retains inline convention for self-containment."

#### m3: `branch_workflow_audit` re-export "for back-compat" over-stated — nothing external imports the moved fns
- **Builder draft**: **ACCEPTED-FIXED** — drop the "back-compat" justification (replace with "internal audit use"); verify the audit's two internal call sites (`:477`, `:583`) are rewired to the imported names.

## Dimensions checked
- [x] Unfounded assumptions — B1 (PCR resolves master-commit race — false), B2 (pick-log "same mechanism" — false, executed), M3 (two worktrees both on master — impossible), M2 (audit "timing-agnostic" — partial).
- [x] Missing edge cases — B1 (two-session master-commit race), M3 (worktree-add OK → queue-commit fail → orphan), m1 (partial-seed).
- [x] Over-engineering — none material (shared helper + CLI justified).
- [x] Under-engineering — B3 (version-bump fan-out absent), B4 (pick-time skip no recording surface), M1 (abandoned-pick detectability overstated).
- [x] Contract gaps — pick-log line format specified; record_pick idempotency unspecified (B2); pick-commit partial-failure semantics unspecified (M3).
- [x] Security — none new (cooperative git-identity, fail-visible-on-unset reuses read_git_config_user).
- [x] Drift from vault — ADR-090 append-only/supersede prose OK; strategic-direction tension (per-pick master-commit vs parallel-slice family) = B1/M3.
- [x] Web-known issues — none decision-relevant (git worktree + local markdown).
- [x] Cross-cutting conformance — APED-1 executed (B2); MEPD-1 (B3); runtime-env/cwd (M2); OSDG-1 (both SKILL.md drift-guarded — re-sync required).

## Triage

**Triaged by**: user
**Date**: 2026-06-02
**Final verdict**: CLEAN

Incorporates both Critic passes: critique.md (first Critic, BLOCKED) + critique-review.md (meta-Critic, EXTEND — added M-add-1..4). All findings ratified ACCEPTED-FIXED; abandoned-pick detection deferred to a follow-up slice.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md §Concurrency model + ADR-090 Consequences: PCR removed; same-machine `_vault_write` lock + git index/ref lock serialization; cross-clone out of scope |
| B2 | Blocker | ACCEPTED-FIXED | design.md §slice_queue_writer Edge + ADR-090 Decision: distinct read-tail/re-append path (not PSQ-2 claim mech) + prefix-scan idempotency; code+test at /build-slice |
| B3 | Blocker | ACCEPTED-FIXED | design.md §Methodology version-bump fan-out + mission-brief pre-finish gate: BRANCH-3 @ v0.81.0 + entry-pin + 4-part PMI-1 + forward-sync; executes at /build-slice |
| B4 | Blocker | ACCEPTED-FIXED | design.md §skills/slice Edges + error model: `/slice` pre-creates `build-log.md` Events stub with canonical `- ` bullet |
| M1 | Major | ACCEPTED-FIXED | mission-brief must-not-defer + design §Post-critique-resolution #4: honest downscope to IN_PROGRESS informational; `abandoned-pick-detection` deferred follow-up |
| M2 | Major | ACCEPTED-FIXED | design.md §branch_workflow_audit: end-state unchanged; all pre-finish/mid-slice audits run from within the worktree |
| M3 | Major | ACCEPTED-FIXED | design.md §Pick-time sequence: explicit ordered two-tree dance + per-step failure/rollback |
| m1 | Minor | ACCEPTED-FIXED | design.md §_worktree_paths Public surface: "already seeded" = dir exists → skip; partial-seed test |
| m2 | Minor | ACCEPTED-FIXED | mission-brief AC5 + design §AC5 scope: shared helper on the primary path; legacy escape-hatch prose self-contained |
| m3 | Minor | ACCEPTED-FIXED | design.md §_worktree_paths Key interactions: "internal audit use" (not back-compat); rewire `:477`/`:583` call sites |
| M-add-1 | Major | ACCEPTED-FIXED | (meta-Critic) ADR-090 frontmatter `supersedes: null` → `supersedes: ADR-063`; resolves verification-plan AC4 self-contradiction |
| M-add-2 | Minor | ACCEPTED-FIXED | (meta-Critic) design.md: WORKTREE=skip stub written with leading `- ` bullet (regex `^- ` anchor) |
| M-add-3 | Minor | ACCEPTED-FIXED | (meta-Critic) design.md §slice_queue_writer Edge: first-pick (absent `## Pick log`) → create-section; both cases tested |
| M-add-4 | Minor | ACCEPTED-FIXED | (meta-Critic) design.md §Pick-time sequence step 5: `write_slice_queue(repo_root=<main-tree root>)`, not `Path('.')` |
