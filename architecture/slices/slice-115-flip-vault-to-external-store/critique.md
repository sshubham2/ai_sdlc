# Critique: Slice 115 flip-vault-to-external-store

**Critic reviewed**: mission-brief.md, design.md, ADR-107 (+ project-frame.md, cross-slice action-points)
**Date**: 2026-06-05
**Result**: BLOCKED (Critic severity) — Builder drafts below; TRI-1 final verdict computed at triage

## Summary
The readiness arc (093→114) is genuinely complete and the high-level approach (Option A, plain dir, `vault_is_external` guard) is sound. But the design has three execution-level defects that would break or silently corrupt the flip at build time: (B1) the migration sequence loses the slice's own ADR-107 and any other non-slice-folder vault artifact authored on the branch; (B2) AC3's "`OP_DEFERRED_TO_FLIP` → ∅" is not achievable by the described prose-conversion mechanism — empirically the 11 deferred ops stay deferred after `<vault>/` conversion (AP-12 re-route-not-resolve); and (B3) the byte-faithful verify is a 3-file sample, not a verify of the 1091-file move it guards. Each is fixable in-slice but each requires a design change before `/build-slice`.

## Findings

### Blockers (must address before /build-slice)

#### B1: Migration step 3 loses ADR-107 (and any non-slice-folder vault artifact authored on slice/115)
- **Claim under review**: design.md §The flip sequence step 3 — "Copy `<main>/architecture/*` → `<external>/` byte-faithfully … THEN overlay this slice's active scaffold … (`<wt>/architecture/slices/slice-115/`). The external store now = master-tip shared vault + slice-115 active folder."
- **Issue**: The migration source is master-tip's `architecture/` UNION the worktree's `slices/slice-115/` subtree only. But `git diff --name-only master slice/115 -- architecture/` shows branch-only files OUTSIDE `slices/slice-115/`: `architecture/decisions/ADR-107-flip-vault-to-external-store.md` (on the branch, not master, not in the overlaid folder). After the flip + step-5 removal of `<wt>/architecture/`, **ADR-107 exists in no copy** — the decision record that justifies the entire flip is lost, violating "No data loss on the move."
- **Evidence**: `git diff --name-only master slice/115 -- architecture/`; ADR-107 present in worktree, absent on master (`git ls-files`).
- **Proposed fix**: Migrate the **full slice/115 branch tree's** `architecture/` (every branch-authored vault file — ADR-107, the R-32-retired risk-register edit, any lessons-learned append), not master + a single subtree overlay. Add ADR-107 to the verify sample (→ B3).
- **Builder draft**: ACCEPTED-FIXED — design.md §The flip sequence step 3 redesigned: **rebase slice/115 onto master first** (brings the queue-pick commit current so the branch tree is a strict superset of master), then migrate the **entire branch `architecture/` tree** wholesale (captures ADR-107 + scaffold + current slice-queue + the R-32 risk-register edit). The "master + single overlay" framing is removed.

#### B2: AC3 "`OP_DEFERRED_TO_FLIP` → ∅" is not delivered by the class-4/5/6 prose conversion — the 11 deferred ops stay deferred
- **Claim under review**: AC3 + design.md — "The flip drives `OP_DEFERRED_TO_FLIP` → ∅"; class 5 = "`architecture/slices/slice-NNN/…` → `<vault>/slices/slice-NNN/…`".
- **Issue** (APED-1, executed not reasoned): `tools/vault_flip_prose_inventory._classify_op` routes by the sink VALUE via `_ACTIVE_FOLDER_RE = re.compile(r"slices/slice-(?:\d+|NNN)")` (L585/L679), which matches `slices/slice-NNN` in BOTH `architecture/slices/slice-NNN/…` AND `<vault>/slices/slice-NNN/…`; `_OP_SINK_RE` is seam-aware. So `<vault>/` conversion leaves all 11 active-folder write-ops `OP_DEFERRED_TO_FLIP` unchanged. The only exit is `OP_ROUTED` (a `vault_edit`/`VAULT_ROOT` token AFTER the verb) — a BEHAVIORAL change to 11 sites across 11 skills, not prose-only (design flags only 2 as behavioral). Also `_OP_CLASS_FLOOR[OP_DEFERRED_TO_FLIP] = 11` (L638): `--strict` exits 2 the moment the count drops below 11 **unless the floor is re-pinned to 0** (design never mentions this). And the op-gate is wired into NO skill (`grep skills/ for op-gate` is empty) — AC3 has no enforcing consumer (AP-12: a gate-visible bucket is sound only if a contractually-required consumer drains it).
- **Evidence**: `python -c` execution of `_classify_op`; `tools/vault_flip_prose_inventory.py` L579–688, floor L636–640; live `--op-gate --json` shows `op-deferred-to-flip: 11`, floor 11.
- **Proposed fix**: Decide + document the actual drain: either route all 11 → `OP_ROUTED` (enumerate all 11 as behavioral), OR change the classifier so a post-flip active-folder write (per-slice, non-contended, safe direct write to external `<vault>/`) is no longer `DEFERRED`; re-pin `_OP_CLASS_FLOOR` to 0 with a non-vacuity proof; name the AC-bound consumer that runs `--op-gate --strict` at pre-finish + add a shippability row (AP-18).
- **Builder draft**: ACCEPTED-FIXED (design) + ACCEPTED-PENDING (impl) — the active-folder writes are **per-slice, non-contended** (two worktrees never write the same slice folder), so they are SAFE as direct writes to the external store and do NOT need CAS routing. The `_ACTIVE_FOLDER_RE → DEFERRED` rule was a pre-flip holding pattern. The flip **reclassifies** post-flip active-folder writes OUT of `DEFERRED` (to `OP_OUT_OF_SCOPE` / a dedicated non-gating class), re-pins `_OP_CLASS_FLOOR[OP_DEFERRED_TO_FLIP]` to 0 with a mutation-proven non-vacuity test (AP-5), AND wires `--op-gate --strict` into `/build-slice` Step 6 + `/validate-slice` pre-finish + a shippability row. AC3 reworded from "→ ∅ by conversion" to "→ ∅ by classifier-reclassification + floor re-pin + wired consumer." This is the genuine R-32.a drain (mission-brief AC3 + design updated together — AP-17). Implementation lands at build (the classifier edit + the non-vacuity proof are code, executed against the real corpus — AP-3).

#### B3: "Byte-faithful verify before deleting" is a 3-file sample of a 1091-file move
- **Claim under review**: design.md Invariant — "verify byte-faithful (hash sample of `_index.md` / `risk-register.md` / an ADR) → only then untrack/remove"; must-not-defer "byte-faithful verify before deleting in-tree copy".
- **Issue**: The move is 1091 tracked files (`git ls-files architecture/ | wc -l` = 1091) + untracked artifacts. A 3-file hash sample does not verify the move; a partial-copy failure (interrupted `shutil`, a MAX_PATH overflow on a deeply-nested archive folder, an AV-locked handle — the very C3 hazard this initiative dodges) passes the sample, then the in-tree copy is deleted → silent loss of unsampled files.
- **Evidence**: `git ls-files architecture/` = 1091; design.md Invariant + Error model.
- **Proposed fix**: Complete file-set + per-file hash comparison (count match AND byte/hash match for every file); STOP-before-delete on ANY mismatch or count delta. Keep the 3-file sample only as a fast pre-check.
- **Builder draft**: ACCEPTED-FIXED (design) + ACCEPTED-PENDING (impl) — design Invariant + Error model rewritten to a **full manifest hash walk** (enumerate every source file, assert count equality + per-file SHA-256 match at the destination) before any untrack/delete; `_vault_flip` implements + returns the manifest; the WIRE-1 test asserts count equality (→ m2). Cheap (a hash walk).

### Majors (address this slice)

#### M1: `~/.claude/ai-sdlc-vault-base` resolution is internally contradictory and the file is absent on the build machine
- **Issue**: design.md L34 says `_vault_flip` "reads `~/.claude/ai-sdlc-vault-base` (base, **default `~/.aisdlc`**)"; Error model L82 says "Base/path unresolvable (`~/.claude/ai-sdlc-vault-base` **absent** …) → **STOP** loudly." These contradict. The file is ABSENT on this machine (this repo adopted 2026-05-13, pre-ADR-085 install enhancement), so the ambiguity fires at build.
- **Evidence**: `ls ~/.claude/ai-sdlc-vault-base` → ABSENT; ADR-085 L41; design.md L34 vs L82.
- **Proposed fix**: absent base file → default `~/.aisdlc` (do NOT STOP); STOP only if the *resolved* base is unwritable / OneDrive / AV-aggressive (C3). Align L82 with L34. Test the absent-base path.
- **Builder draft**: ACCEPTED-FIXED — Error model corrected: absent base file is the NORMAL path → default `~/.aisdlc` (silent, documented value); STOP reserved for a *resolved* base that is unwritable / on OneDrive / AV-aggressive (C3). The reused-component note + error model now agree. A `test_absent_base_defaults` case added to the WIRE-1 test plan.

#### M2: diagnose-out/ left in-tree contradicts ADR-085's stated move scope — coherence gap
- **Issue**: ADR-085 (the anchor ADR) twice states scope as "relocate the vault `architecture/` **+ `diagnose-out/`**" (L17, L53). The flip narrows to architecture/-only without reconciling against that text. Per "deviations need an ADR," a scope narrowing from a prior ADR needs a written reason in ADR-107.
- **Evidence**: ADR-085 L17 + L53; `.gitignore:20` (diagnose-out already untracked); ADR-107 §Consequences (no reconciliation).
- **Proposed fix**: Add a sentence to ADR-107 noting ADR-085's "+`diagnose-out/`" scope is deliberately NOT inherited because diagnose-out/ is already gitignored (no R-32 shared-mutable-git-conflict class) and slice-105 decoupled it — so it does not block R-32 retirement.
- **Builder draft**: ACCEPTED-FIXED — ADR-107 §Consequences gains an explicit diagnose-out reconciliation sentence (already-gitignored → no R-32 conflict class; slice-105 decoupled the round-trip; relocating it is a separate future slice, not an R-32 residual).

#### M3: the flip is unsafe if any other slice branch is in-flight (architectural concurrency, Dim 7b)
- **Issue**: The flip git-untracks `architecture/` on slice/115 + merges to master. Under BRANCH-2/PSQ (N concurrent worktrees = normal), another in-flight `slice/*`: (a) its `/commit-slice --merge` would re-introduce tracked `architecture/` (its branch predates the untrack), silently un-doing the flip; (b) its in-tree vault writes never reached the external store. The design's bootstrap reasoning is single-slice and never states the precondition "no other slice in-flight."
- **Evidence**: CLAUDE.md BRANCH-2/PSQ; design.md §The flip sequence (single-slice framing); no quiesce must-not-defer.
- **Proposed fix**: Add a must-not-defer + pre-flip guard: zero other active slice branches (`git branch --list 'slice/*'` minus self == empty) OR documented manual quiesce; any slice branched before the flip must rebase onto post-flip master before merge.
- **Builder draft**: ACCEPTED-FIXED — mission-brief gains a must-not-defer ("flip requires zero other in-flight `slice/*` branches at flip time, else a documented quiesce; pre-flip guard `git branch --list 'slice/*'` minus self == ∅"); design §The flip sequence gains this as a step-0 precondition. (Currently satisfiable — the slice-115 `stranded_slice_audit` at `/slice` was clean; no other slice is in-flight. The precondition is stated + guarded, not assumed.)

#### M4: reversibility tagged "cheap" understates a 1091-file move + wide-prose + git-untrack
- **Issue**: The tag leans entirely on the rollback tool. Rollback must move 1091 files back, reverse `git rm --cached` (re-track 1091), remove gitignore, unset config, `git revert` prose/guard — across two trees, after a no-ff merge, AND after post-flip slices may have written external-only content with no in-tree home. "No data loss" on rollback holds only BEFORE post-flip writes diverge; the design doesn't bound that window.
- **Evidence**: ADR-107 §Reversibility; design.md step 6 (post-flip artifacts external immediately); 1091-file count.
- **Proposed fix**: Downgrade to "moderate" OR make the bounded window a hard precondition (rollback cheap only within the same build, before post-flip external writes accumulate; after, rollback must reconcile external-only content). Pin the round-trip test to assert the COMPLETE file set restores (couples B3).
- **Builder draft**: ACCEPTED-FIXED — ADR-107 §Reversibility keeps `cheap` but makes the bounded window a HARD precondition: cheap within the same build (scripted inverse, no divergence); once post-flip external writes accumulate, rollback additionally reconciles external-only content (no longer a pure inverse). Round-trip test asserts complete-file-set restore (couples B3/m2).

#### M5: `/slice` Step 6.5 "commit slice-queue.md on master" retire spans ≥5 sites, not 1 line
- **Issue**: The queue-commit-on-master mechanic appears at `skills/slice/SKILL.md` L250, L432, L474–476, L479, L515. The design's "retires" is one line; the edit spans ≥5 sites (FBCD-1 cross-file). A leftover bare `git add architecture/slice-queue.md` on a gitignored path warns and could re-track.
- **Evidence**: `skills/slice/SKILL.md` L250, L432, L474–476, L479, L515; design.md L16.
- **Proposed fix**: Enumerate every site in the build plan; rewrite all in one block; confirm the bare `git add`/`git commit` lines are removed (not just prose); check no residual `git -C <main> add architecture/slice-queue.md` survives.
- **Builder draft**: ACCEPTED-FIXED (design enumerates the sites) + ACCEPTED-PENDING (build applies the lockstep edit + the residual-`git add` check) — design §Components touched now lists the 5 slice/SKILL.md sites; the queue WRITE (CAS regen + pick-log, slice-109) STAYS, only the git-commit-on-master is removed; build verifies no residual `git add architecture/slice-queue.md`.

### Minors (log; address if cheap)

#### m1: op-gate emits a mojibake sink value on `skills/slice/SKILL.md:264`
- **Issue**: `--op-gate --json` reports slice:264's value as `architecture/slices/�` (replacement char) — likely an ellipsis `…` mangled via cp1252, or a truncation. Not load-bearing but masks whether the conversion landed there.
- **Builder draft**: ACCEPTED-PENDING — when rewriting the slice:264/249/460 ellipsis reference for class-5, render the literal cleanly + confirm `_stdout.reconfigure_stdout_utf8()` on the op-gate JSON path (AP-8).

#### m2: WIRE-1 consumer test must exercise the FULL-tree migration, not a toy fixture
- **Issue**: `test_flip_then_rollback_roundtrip` on a few-file fixture never exercises B1 (non-slice-folder file) or B3 (sample-vs-full). Must include a `decisions/ADR` file + assert COUNT equality.
- **Builder draft**: ACCEPTED-FIXED — wiring-matrix test description updated: seed the fixture with a `decisions/ADR-XXX.md` + a non-slice-folder file; assert the ADR survives the round-trip AND file-count equality (non-vacuous against B1/B3).

## Dimensions checked
- [x] Unfounded assumptions — B2 (assumed `<vault>/` conversion drains the bucket; executed-disproven), M1 (contradictory default-vs-STOP). Verified against implementation, not docstrings.
- [x] Missing edge cases — M3 (concurrent in-flight slice branches), B3 (partial-copy passes a sampled verify; C3 AV/OneDrive hazard re-applies to the move itself).
- [x] Over-engineering — none (reuses the 093→114 substrate; one new underscore helper justified by tested-reversibility; no speculative interfaces).
- [x] Under-engineering — B1 (AC2 "no data loss" misses non-slice-folder branch files), B2 (AC3 no delivering mechanism + no enforcing consumer), B3 (sampled not full verify), M5 (one-line retire vs ≥5 sites).
- [x] Contract gaps — M5 (queue coordination contract git-commit → shared-external; git-add residual). PCR contract verified INTACT: `_retire_if_vault_external` (parallel_conflict_resolver.py L307–343, L369) short-circuits at resolve-ENTRY before any out_path composition → SOFT/VAULT_CLAIM cleanly no-op when external; nothing in PCR *breaks*. SOFT file-set confirmed `{architecture/slice-queue.md, architecture/shippability.md}` (L59–62).
- [x] Security — none (not a security boundary; ADR-085 cooperative-model; local user-owned dir).
- [x] Drift from vault — M2 (ADR-085 "+`diagnose-out/`" scope silently narrowed), B1 (ADR-107 itself would be lost — self-defeating drift); partial-supersede of ADR-090 correctly declared.
- [x] Web-known issues — confirmed `git rm --cached architecture/` on a branch + no-ff merge leaves master's working tree with untracked `architecture/` (design step-7 orphan cleanup is correct git semantics; gitignore-immediately at step 5 is correct). Sources: git-scm.com/docs/git-rm.
- [x] Cross-cutting conformance — B2 = APED-1 (executed `_classify_op`); B1/M5 = FBCD-1 cross-file fan-out; M3 = strategic-direction/architectural-concurrency (slice-087 lineage); the `_OP_CLASS_FLOOR=11` re-pin is the AP-10 count-literal fan-out the design omitted.
