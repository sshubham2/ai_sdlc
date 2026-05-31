# Slice 087: add-stranded-slice-detection-to-slice

**Mode**: Standard
**Estimated work**: 0.5–1 day
**Risk retired**: new **R-27** — stranded/uncommitted completed-slice work is invisible to the pipeline's vault-based active-slice detection at `/slice` open (witnessed firsthand this session at slice-086). **Relationship to R-22 (retired, slice-077)**: R-22 covered `/pulse` mis-reporting the BRANCH-2 *worktree* window and was retired by `pulse_worktree_resolver.py`. R-27 is the residual R-22 did NOT close: (i) `/slice` never consults git state at open, and (ii) the **bare unmerged `slice/*` branch WITHOUT a live worktree** (e.g. a post-`--merge` cleanup-failure / committed-but-unmerged branch) — `pulse_worktree_resolver` walks `git worktree list` only, never `for-each-ref refs/heads/slice/`.
**Test-first**: true  (structural-pin + behavioral tests, WRITTEN-FAILING first — the project's methodology-surface convention; no `tests/bugs/*` repro applies)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The pipeline decides "what slice is active" purely from the **vault** (`slices/_index.md` Active table + `milestone.stage`). When a session builds a slice to completion but dies before `/commit-slice`, the vault marks it shipped/archived while git still holds an **unmerged `slice/NNN-*` branch** — a git-vs-vault divergence invisible to every vault-based check. This bit us live this session: a prior session completed + archived slice-086 but never committed it; a new `/slice` happily redefined slice-086 from scratch and only collided deep inside `/build-slice`'s BRANCH-2 worktree setup. This slice adds a **git-vs-vault classifier** that `/slice` consults at open (and `/pulse` surfaces).

**Crucial constraint — classify, don't flag-all (parallel-safety).** "Stranded" is NOT "an unmerged `slice/*` branch exists." Under PSQ-1/PSQ-2/BRANCH-2 the project runs *multiple concurrent* unmerged `slice/*` branches by design (e.g. this very slice-087 runs in parallel with slice-088), so an existence-based detector would cry-wolf on every healthy in-flight slice and get silent-disabled (R-7). Instead the detector classifies each unmerged `slice/*` branch into a **4-class divergence model** (STRANDED-COMPLETE / ORPHANED → halt; IN-PROGRESS / CLAIMED-BY-OTHER → informational; INDETERMINATE → fail-closed halt — see design.md `## Classification model` + ADR-079) and **halts `/slice` only on genuine divergence** (vault-says-done-but-git-unmerged, or git-work-with-no-vault-story). A healthy parallel slice with its own worktree at a mid-stage is IN-PROGRESS and never halts. On a halt, the operator is offered Resume / Continue-build / Proceed-anyway.

## Acceptance criteria

1. New tool `tools/stranded_slice_audit.py` (read-only) **classifies** every unmerged `slice/*` branch into the 4-class divergence model (+ INDETERMINATE), **reusing** `pulse_worktree_resolver.detect_active_worktrees` + **`classify_worktree_state`** + `_resolve_default_branch` for any branch with a live worktree (mapping `IN_PROGRESS`→IN-PROGRESS, `BUILT_BUT_NOT_MERGED`→STRANDED-COMPLETE, `MERGED`→skip, `UNKNOWN`→INDETERMINATE) and `slice_queue_claim.parse_queue_text` for the PSQ-2 claim cross-reference, rather than re-deriving porcelain/ancestry/claim parsing (B1). Its genuinely-new detection over slice-077 is the **bare unmerged `slice/*` branch WITHOUT a live worktree** (via `git for-each-ref refs/heads/slice/` + `git merge-base --is-ancestor <branch> <default>`, ancestor⇒merged, + ahead-count), classified against the current-tree vault (`archive/` presence + milestone stage). Each entry carries `{branch, worktree_path|null, klass, halt, vault_state, claimed_by|null, ahead, dirty, reason}`; a per-branch merge-base error ⇒ `klass: indeterminate` (m2). Exit 0 + `status: clean` when no halt-worthy entries (IN-PROGRESS/CLAIMED-BY-OTHER entries are listed but do not make the run divergent); exit 0 + `status: divergent` + list when ≥1 STRANDED-COMPLETE/ORPHANED/INDETERMINATE entry (advisory, NOT a refuse; NO exit 1). Exit 2 only on usage failure. `--json` + human; accepts both `--repo-root` and a `--root` alias (so the `_ROOT_ONLY_TOOLS` cp1252 regression genuinely exercises stdout, M2); UTF8-STDOUT-1 compliant.
2. `/slice` Prerequisite check invokes the detector BEFORE Step 1 candidate-gathering; on `status: divergent` it HALTs with an `AskUserQuestion` structured-options gate (Resume via `/commit-slice` / continue that slice's `/build-slice` / proceed defining a new slice anyway), never silently proceeding; on `status: clean` with informational (IN-PROGRESS / CLAIMED-BY-OTHER) entries it surfaces a one-line note and proceeds **without a gate** (the parallel-safe path). The proceed-anyway path is always available on the gate (advisory, not blocking).
3. `/pulse` surfaces the **bare-unmerged-branch-without-worktree** signal (rendering its `klass`) in its macro-state summary (the case slice-077's existing `/pulse` worktree block does NOT cover) — placed so it does NOT perturb `test_pulse_skill_worktree_awareness.py`'s offset/window pins (verify after edit), and guarded by the EXISTING `test_pulse_skill_drift.py` (M4 — not the `/slice` drift test).
4. A behavioral test asserts the classifier: (a) **STRANDED-COMPLETE** — an archived/reflect slice with an unmerged branch ⇒ `halt: true`, `status: divergent`, **including the canonical slice-086-class case where the `archive/slice-NNN-*` entry exists ONLY on the unmerged branch** (the classifier reads it via `git ls-tree`/`git show <branch>:…`, not the invoking tree — M1), distinct from ORPHANED; (b) **ORPHANED** — an unmerged `slice/*` branch with no vault story on the branch's tree, the invoking tree, or the queue ⇒ `halt: true`; **(c) IN-PROGRESS parallel-safety pin** — a `slice/*` worktree at a mid-stage (slice…validate) ⇒ `klass: in-progress`, `halt: false`, `status: clean` (THE central reframe property — a healthy parallel slice never halts `/slice`); (d) **CLAIMED-BY-OTHER** — a branch whose queue key `<name>` carries a `slice-queue.md` claim by a different git identity ⇒ `klass: claimed-by-other`, `halt: false`. **Fixture-reachability honesty (B1)**: the fixture is *synthetic* (a queue with `### <name>` = branch suffix + a foreign `**Claimed-by:**`) and proves the *code path*; in production the queue regenerates from the backlog top-10 so an in-flight branch is frequently key-absent ⇒ the class does not fire ⇒ correct fall-through to IN-PROGRESS/STRANDED/ORPHANED (the live parallel-safety signal is IN-PROGRESS, case (c), NOT this class). If the user demotes CLAIMED-BY-OTHER at TRI-1, this case is dropped; (e) **clean** — a repo with no `slice/*` branches; (f) does NOT flag `recovery/*` or merged `slice/*` branches; (g) **INDETERMINATE** — a malformed milestone / merge-base error ⇒ per-entry `klass: indeterminate` (`halt: true`, fail-closed), NOT a whole-run exit-2; **(h)** the slice's OWN pushed-but-unmerged `slice/*` branch (vault archived) ⇒ STRANDED-COMPLETE/resumable — EXPECTED, NOT a false positive (m-add-1, reconciled under the 4-class model); and `skills/slice/SKILL.md` + `skills/pulse/SKILL.md` are OSDG-1 content-equal to their installed copies (drift tests).
5. R-27 registered in `architecture/risk-register.md` (mitigating once the detector ships, with the Relationship-to-R-22 clause); the new tool propagated across the full **BC-PROJ-9 5-surface inventory** (`plugin.yaml` + `install_audit._CANONICAL_TOOLS` + `INSTALL.md` count 33→34 at L22+L166 + `_ROOT_ONLY_TOOLS` + shippability row) — independent of any VERSION bump (M1); full pytest + all Step-6 audits pass.

## Test-first plan

(per **TF-1**) Each AC maps to tests written WRITTEN-FAILING before implementation. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish`.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | behavioral | tests/methodology/test_stranded_slice_audit.py | test_clean_when_no_slice_branches | PASSING |
| 4a | behavioral | tests/methodology/test_stranded_slice_audit.py | test_stranded_complete_branch_halts | PASSING |
| 4b | behavioral | tests/methodology/test_stranded_slice_audit.py | test_orphaned_branch_halts | PASSING |
| 4c | behavioral | tests/methodology/test_stranded_slice_audit.py | test_in_progress_parallel_slice_does_not_halt | PASSING |
| 4d | behavioral | tests/methodology/test_stranded_slice_audit.py | test_claimed_by_other_is_informational | PASSING |
| 4e | behavioral | tests/methodology/test_stranded_slice_audit.py | test_clean_when_no_slice_branches | PASSING |
| 4f | behavioral | tests/methodology/test_stranded_slice_audit.py | test_ignores_recovery_and_merged_branches | PASSING |
| 4g | behavioral | tests/methodology/test_stranded_slice_audit.py | test_malformed_milestone_is_indeterminate | PASSING |
| 4h | behavioral | tests/methodology/test_stranded_slice_audit.py | test_own_pushed_unmerged_branch_is_stranded_complete_resumable | PASSING |
| 4i | behavioral | tests/methodology/test_stranded_slice_audit.py | test_complete_stage_bare_branch_is_stranded_complete | PASSING |
| 2 | structural-pin | tests/methodology/test_slice_skill_stranded_prereq.py | test_slice_skill_has_stranded_detection_prereq | PASSING |
| 3 | structural-pin | tests/methodology/test_pulse_skill_stranded_signal.py | test_pulse_skill_surfaces_stranded_signal | PASSING |
| 4 | drift (OSDG-1) | tests/methodology/test_slice_skill_drift.py | test_in_repo_and_installed_slice_skill_md_are_content_equal | PASSING |
| 4 | drift (OSDG-1) | tests/methodology/test_pulse_skill_drift.py | test_in_repo_and_installed_pulse_skill_md_byte_equal | PASSING |
| 5 | inventory-pin | tests/methodology/test_stranded_slice_audit_tool_inventory.py | test_stranded_slice_audit_in_canonical_inventory | PASSING |

> Notes: case **4c** (IN-PROGRESS parallel slice ⇒ `status: clean`, no halt) is the binding parallel-safety pin — the regression test for the flaw the USER caught; it must fail against the rejected flag-all design and pass against the classifier. The `/slice` + `/pulse` OSDG-1 drift tests (`test_slice_skill_drift.py`, `test_pulse_skill_drift.py`) ALREADY exist — reuse, do not duplicate (M4: `/pulse`'s guard is `test_pulse_skill_drift.py`, NOT the `/slice` drift test). AC#5's inventory-pin (M1) mirrors slice-077's `test_pulse_worktree_resolver_tool_inventory.py`. After the `/pulse` edit, re-run `test_pulse_skill_worktree_awareness.py` to confirm slice-077's offset/window pins still pass (M4).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Detector classifies divergence correctly | `tests/methodology/test_stranded_slice_audit.py` (8 cases a–h) PASS; manual run against a fixture repo with both an orphan branch and a mid-flight worktree |
| 2 | `/slice` halts only on `divergent` | Structural-pin test asserts the prerequisite-block prose (halt-on-divergent + surface-informational-and-proceed) + `AskUserQuestion` gate; manual `/slice` dry-run with a planted orphan branch AND a planted IN-PROGRESS worktree (only the orphan halts) |
| 3 | `/pulse` surfaces the signal | Structural-pin test on `pulse/SKILL.md`; manual `/pulse` shows the bare-branch `klass` line |
| 4 | OSDG-1 + parallel-safety + no-false-positive | drift tests green; AC4 case (c) `test_in_progress_parallel_slice_does_not_halt` green; `test_ignores_recovery_and_merged_branches` green |
| 5 | No regression; risk + catalog | Full `pytest` green; `/validate-slice`; R-27 in register; shippability row added |

## Must-not-defer

- [ ] **Parallel-safe — classify, NOT flag-all (the binding reframe constraint)**: a healthy in-flight parallel slice (own worktree, milestone stage ∈ {slice…validate}) classifies as IN-PROGRESS and MUST NOT halt `/slice` (`status` stays `clean`). Only genuine divergence (STRANDED-COMPLETE / ORPHANED / INDETERMINATE) halts. An existence-based flag-all detector is the rejected design (ADR-079 Option 4) — it cry-wolfs on every concurrent slice and undermines PSQ. Pinned by AC4 case (c).
- [ ] **No false positives**: `recovery/*` branches, merged `slice/*` branches, IN-PROGRESS parallel slices, and the main worktree MUST NOT trigger a halt — a noisy detector that cries wolf will be ignored (it would have flagged this session's own recovery branches AND the live parallel slice-088).
- [ ] **Advisory, never blocking**: the proceed-anyway path is ALWAYS offered on the gate — the detector informs, it does not refuse. (An operator must be able to define a parallel slice deliberately.)
- [ ] **Default-branch resolution**: reuse the canonical 2-step resolution (`git symbolic-ref refs/remotes/origin/HEAD` → `git config init.defaultBranch` → STOP), not a hard-coded `master`/`main` (BRANCH-1/NAW-1 portability pin).
- [ ] **Fail-visible, not fail-silent**: if git is unavailable / default unresolvable, the detector exits non-zero with a clear stderr message; `/slice` surfaces it rather than silently skipping (the R-7 silent-disable class).
- [ ] **Reuse, don't re-implement (B1)**: import `pulse_worktree_resolver.detect_active_worktrees` + `_resolve_default_branch` for the worktree + default-resolution sides; do NOT create a 3rd copy of worktree-porcelain/ancestry parsing.
- [ ] **5-surface inventory (M1)**: a new `tools/*.py` propagates across all five BC-PROJ-9 surfaces (plugin.yaml, install_audit, INSTALL.md count ×2, _ROOT_ONLY_TOOLS, shippability) — even though no VERSION bump.
- [ ] **CAD-1/OSDG-1 untouched elsewhere**: edits limited to `skills/slice/SKILL.md`, `skills/pulse/SKILL.md`, and the new tool/tests; forward-sync installed copies (atomic at end-of-build).

## Out of scope

- Auto-resuming or auto-committing the stranded slice (the detector only *surfaces* it; resumption is the operator's explicit choice via `/commit-slice` or `/build-slice`).
- Detecting stranded work in *other* repos or remote branches (local `slice/*` + local worktrees only).
- Reworking BRANCH-2 worktree mechanics or `/commit-slice` recovery flows.
- A hard Step-6 gate refusing on stranded work (this is an open-time advisory; a blocking variant is a separate future slice if warranted).

## Dependencies

- Prior slices: [[slice-086-harden-agent-spawn-skills-await-real-output]] (the session whose stranded state motivated this), BRANCH-2 worktree workflow ([[decisions/ADR-063]]), `tools/branch_workflow_audit.py` (existing `stale-slice-branch` warning class to extend), `tools/new_agent_warning_audit.py` (git-subprocess + default-resolution precedent to model the new tool on).
- Vault refs: `skills/slice/SKILL.md` Prerequisite check, `skills/pulse/SKILL.md`, CLAUDE.md OSDG-1.
- Risk register: new R-27 (registered during this slice).

## Mid-slice smoke gate

After writing `tools/stranded_slice_audit.py` + its behavioral test (before the SKILL.md edits): create a throwaway fixture repo with (i) an unmerged `slice/999-smoke` branch with NO vault story, and (ii) an unmerged `slice/998-parallel` branch WITH a **live worktree carrying a real, well-formed milestone** (M2 — re-`/critique` finding: `classify_worktree_state` returns `IN_PROGRESS` only when the worktree's `milestone_path` resolves to an existing file AND `_parse_milestone_stage` yields a non-None stage ≠ `reflect`; a branch + a loose dir without valid frontmatter resolves `UNKNOWN`→INDETERMINATE→`halt:true` and FAILS the no-halt expectation). Construct (ii) concretely:
```
git -C <fixture> worktree add <fixture>/wt-998 -b slice/998-parallel
# write architecture/slices/slice-998-parallel/milestone.md INTO wt-998 with frontmatter:
#   ---\nslice: slice-998-parallel\nstage: design\n---  (any pre-reflect stage)
git -C <fixture>/wt-998 add -A && git -C <fixture>/wt-998 commit -m "smoke: 998 mid-flight"
$PY -m pytest tests/methodology/test_stranded_slice_audit.py -q
$PY -m tools.stranded_slice_audit --repo-root <fixture> --json
```
Expected: tests PASS; the JSON classifies `slice/999-smoke` as `orphaned` (`halt: true`) and `slice/998-parallel` as `in-progress` (`halt: false`); top-level `status: divergent` (because of 999, not 998). **Parallel-safety check**: if a fixture with ONLY the well-formed mid-flight worktree (no orphan) does not return `status: clean`, the classifier is regressing to flag-all — STOP and fix before wiring `/slice`. Also STOP if it false-flags a `recovery/*` or merged branch.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (esp. no-false-positives + advisory-not-blocking)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
