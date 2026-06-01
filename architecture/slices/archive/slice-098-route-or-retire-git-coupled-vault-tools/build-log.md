# Build log: Slice 098 route-or-retire-git-coupled-vault-tools

**Date**: 2026-06-01 (build completed 2026-06-02)
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c)

- 2026-06-01 23:30 BUILD: worktree slice/098 verified; CRP-1 clean; R-20 seed (diagnose-out + graphify-out) restored from main tree (worktree-at-/slice dropped it)
- 2026-06-01 23:31 BUILD: plan approved (6 tasks); new shared helper tools/_vault_git.py (underscore, no PMI-1 bump); mid-slice smoke after Task 2 (pulse)
- 2026-06-01 23:40 BUILD: Task 1 done — tools/_vault_git.vault_pathspec_is_tracked + VAULT_ROOT_IS_DEFAULT on _vault_paths.py; test_vault_pathspec_tracked.py 3/3 PASS
- 2026-06-01 23:45 BUILD: Task 2 done — pulse_worktree_resolver._resolve_milestone_path Class-A ROUTE via VAULT_ROOT (L217/L220)
- 2026-06-01 23:46 SMOKE: MID-SLICE GATE PASS — 50 pulse tests green (no-flip); external-root subprocess resolves milestone under AI_SDLC_VAULT_ROOT. Core routing+tracked-check pattern validated; proceeding to stranded + PCR
- 2026-06-01 23:55 FINDING: architecture/ IS git-tracked here (918 files; slice-queue.md tracked rc=0) — slice-044 "gitignored" note stale/inapplicable. So git ls-files tracked-check is sound for the real repo.
- 2026-06-01 23:56 FINDING: 4 stranded tests FAIL with the representative-file tracked-check — their fixtures commit stranded content ONLY to branches; the invoking tree has NO tracked vault content, so `git ls-files --error-unmatch architecture/slice-queue.md` → rc1 → guard over-RETIREs in the in-tree case. Design-vs-reality gap (slice-079 "committed test wins"). HALT to surface deviation: stranded needs a store-LOCATION signal (is VAULT_ROOT external to repo work tree), PCR keeps per-U-file tracked-check.
- 2026-06-02 00:05 DEVIATION: per-tool RETIRE-signal split (USER-APPROVED). PCR keeps per-pathspec `git ls-files --error-unmatch` (sound: conflicted files are in the rebase index in-tree). stranded uses new `_vault_git.vault_is_external(repo_root)` (VAULT_ROOT resolves outside repo work tree). Outcomes unchanged (RETIRE-when-external, no-flip-by-construction, M1 external-but-tracked handled). ADR-089 §Decision/§Residual to be amended.
- 2026-06-02 00:06 BUILD: Task 3 done — stranded ROUTE (_load_claims, slices_dir, fallbacks) + RETIRE via vault_is_external (M4 both git-tree helpers) + M-add-2 dual-class split; 26 stranded/pulse/helper tests PASS
- 2026-06-02 00:20 DEVIATION: UNIFIED RETIRE signal on vault_is_external for BOTH tools (USER-APPROVED, supersedes the earlier per-tool split). Deeper B2 analysis: per-pathspec tracked-check returns True for the still-tracked in-tree file in the external-abs-VAULT_ROOT state → misses B2 corruption. vault_pathspec_is_tracked RETAINED as a tested primitive (future flip slice). ADR-089/design to be amended.
- 2026-06-02 00:22 BUILD: Task 4 done — PCR Class-A ROUTE (_AUDIT_LOG_PATH, out_path x3, slices_dir) + _retire_if_vault_external guard at resolve_soft + resolve_vault_claim entry (before out_path/relative_to, B2). 142 PCR tests PASS (no-flip).
- 2026-06-02 00:30 BUILD: Task 5 done — test_slice_098_vault_routing.py 9/9 PASS: AC1 AST scan (3 tools clean + direct+variable-mediated mutation non-vacuity, M5/M-add-3); vault_is_external logic (M1 external-but-tracked); m1 _AUDIT_LOG_PATH byte-identity; M-add-1 call-spy unreachability; AC3/AC5 external-root subprocess (pulse resolves external + stranded + PCR RETIRE)
- 2026-06-02 00:45 TEST: FULL SUITE 1450 PASS (env unset → AC4 no-flip). Fixed 2 expected state-transition pins: _MIGRATION_SITE_ALLOWLIST 11→14; slice-093 AC4 "migrate-NONE" test → 14 + positive migration asserts. Marked 21 PCR Class-B literals with slice-068 NOT-VAULT_ROOT-routed convention (orphan-literal audit clean).
- 2026-06-02 00:55 TEST: Step-6 audits PASS — WIRE-1/BRANCH(+1 benign stale-branch warn for parallel slice/099)/UTF8/CRP-1/PCA-1/BCI-1/DCE-1/SVW-1/STP-1/NAW-1/MCFS-1/AVFS-1/TVFS-1/mock-budget all exit 0.
- 2026-06-02 01:10 CODE-REVIEW: code-Critic FINDINGS 0B/2M/4m (advisory v1). All 8 high-value targets cleared (vault_is_external edges; B2 guard before out_path; M-add-1 call-spy non-vacuous; 21 markers correct; byte-identity 305 tests). M1 (AST-scanner narrower than claim — joinpath/2-hop false-neg) ACCEPTED-FIXED via design.md claim-narrow + named residual. M2 (M-add-2 pathspec VAULT_ROOT-derived not verbatim) ACCEPTED-FIXED via design.md amend (the derivation is MORE correct — handles external-but-tracked). m3 (relabel vault-external) ACCEPTED-FIXED in code. m4 (no audit-log breadcrumb) DISPOSITIONED (surfaced via stdout/JSON; log path routes external). m1/m2 (unconsumed primitives) ACKNOWLEDGED (flip-slice). 49 affected tests re-PASS after m3.
- 2026-06-02 00:58 BC-1: applicable Critical = [BC-PROJ-3, BC-PROJ-7, BC-GLOBAL-2]. Attestations: BC-PROJ-3/BC-GLOBAL-2 — the ONLY `git stash` use was `stash push -u` + `stash pop` to MOVE the slice scaffold from master to the worktree (verified non-lossy: worktree retained all files, master clean); NO destructive `git checkout --`/`reset --hard`/`stash drop` of uncommitted work. BC-PROJ-7 — new module `tools/_vault_git.py` is underscore-prefixed → excluded from PMI-1/INST-1/INSTALL.md/cp1252 inventory counts (the slice-093 `_vault_paths`/`_vault_write` precedent); NO count-literal fan-out; full suite (1450 PASS) confirms zero inventory drift.

## Summary (filled at slice end)

**Result**: SHIPPED

### Plan executed
- Task 1: `tools/_vault_git.py` (`vault_is_external` + `vault_pathspec_is_tracked` + `VaultGitUnavailable`) + `VAULT_ROOT_IS_DEFAULT` on `_vault_paths.py` + `test_vault_pathspec_tracked.py` — DONE (3/3 PASS)
- Task 2: `pulse_worktree_resolver.py` Class-A ROUTE (`_resolve_milestone_path` L217/220) — DONE; MID-SLICE SMOKE GATE **PASS**
- Task 3: `stranded_slice_audit.py` Class-A ROUTE (`_load_claims`, `slices_dir`, dual-class fallbacks) + RETIRE-when-external via `vault_is_external` (M4: BOTH `_branch_tree_has_path`+`_branch_tree_file`, INDETERMINATE halt) + M-add-2 two-derivation split + KEEP `slice/*` enumeration — DONE
- Task 4: `parallel_conflict_resolver.py` Class-A ROUTE (`_AUDIT_LOG_PATH`, `out_path`×3, `slices_dir`) + `_retire_if_vault_external` resolve-entry guard (resolve_soft + resolve_vault_claim, before `out_path`/`relative_to` — B2) + M-add-1 (diagnose-time reads left protected by U-file-absence→UNKNOWN, no redundant guard) + 21 Class-B literals slice-068-marked — DONE (142 PCR PASS)
- Task 5: `test_slice_098_vault_routing.py` (AC1 AST scan + M5/M-add-3 def-use + mutation non-vacuity; `vault_is_external` logic incl. M1; m1 `_AUDIT_LOG_PATH` byte-identity; M-add-1 call-spy; AC3/AC5 external-root subprocess) — DONE (9/9 PASS)
- Task 6: pre-finish gate (drift-check full + all Step-6 audits + full suite env-unset) — DONE (all green)

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: 50 pulse tests green (env unset, no-flip); external-root subprocess resolved milestone under `AI_SDLC_VAULT_ROOT`. Core routing + signal pattern validated before the deeper tools.

### Pre-finish gate
- [x] All 5 ACs covered with evidence (verification tests + full suite; per-criterion reality-check is /validate-slice's job)
- [x] Must-not-defer addressed (fail-visible RETIRE before out_path; actionable breadcrumb; concurrency invariants intact on default path; encoding discipline — `_vault_git` captures bytes, never decodes; no-flip binding; RETIRE decisions surface in audit output)
- [x] /drift-check full (DCE-1 marker written; CLEAN)
- [x] Mid-slice smoke still passes (full suite 1450 PASS)
- [x] No new TODO/FIXME/debug prints; temp files removed
- [x] Full suite green with `AI_SDLC_VAULT_ROOT` unset (1450 PASS — AC4)
- [x] All Step-6 audits PASS (WIRE-1, BC-1 strict-ack, mock-budget, BRANCH-2, UTF8-STDOUT-1, CRP-1, PCA-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1, NAW-1, DCE-1, SVW-1)

### Deferrals (if any)
- None. (Out-of-scope by design: the actual external-vault flip + the post-flip `_vault_write`-based PCR conflict-resolution replacement = slice-099+; per ADR-089 §Residual.)

### Design deviations (if any)
- **Binding RETIRE signal: `vault_is_external` (store-location), NOT the r2 per-pathspec `git ls-files` tracked-check** — USER-RATIFIED across two surfacings (per-tool split → unify). The tracked-check missed PCR's B2 external-abs-but-still-tracked corruption AND over-RETIRED stranded's branch-only-content fixtures. `vault_pathspec_is_tracked` retained as a tested primitive for the flip slice. Documented in ADR-089 §Decision/§Consequences/§Residual + design.md AS-BUILT banner + drift-log entry. (updated in design.md + ADR-089? yes)
- **Per-tool RETIRE-signal split (intermediate, superseded)** — first surfaced as PCR-tracked-check + stranded-`vault_is_external`; superseded by the unified `vault_is_external` above after the deeper B2 analysis.

### Files changed
- `tools/_vault_git.py` (NEW — underscore helper, excluded from PMI-1/INST-1/UTF8-STDOUT-1)
- `tools/_vault_paths.py` (+ `VAULT_ROOT_IS_DEFAULT`)
- `tools/parallel_conflict_resolver.py` (Class-A ROUTE + resolve-entry RETIRE guard + 21 Class-B markers)
- `tools/stranded_slice_audit.py` (Class-A ROUTE + RETIRE guard + M-add-2 split)
- `tools/pulse_worktree_resolver.py` (Class-A ROUTE)
- `tests/methodology/test_vault_pathspec_tracked.py` (NEW), `tests/methodology/test_slice_098_vault_routing.py` (NEW)
- `tests/methodology/test_vault_root_constant.py`, `tests/methodology/test_external_vault_adr_and_risk.py` (migration-pin transitions 11→14)
- `architecture/decisions/ADR-089-route-or-retire-git-coupled-vault-tools.md` (NEW), slice vault artifacts, `architecture/drift-log.md`, `architecture/slice-queue.md`
