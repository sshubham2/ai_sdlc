# Code Review: Slice 099 create-worktree-at-slice-pick

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-06-02
**Result**: FINDINGS

## Summary

The code is well-engineered and the core mechanism is sound: `_worktree_paths.py` is a clean single-source helper, the `branch_workflow_audit.py` refactor is genuinely byte-behavior-identical, the `## Pick log` read-tail/re-append preservation is correct and well-tested (candidate-named-heading false-match and CRLF edges both verified), and the fail-visible `record_pick` contract is wired correctly. The full suite is green (1455 passed) and PMI-1/TVFS-1 are clean at 0.81.0. **However**, the slice's own `build-log.md` fails `branch_workflow_audit` with a reproducible `worktree-skip-malformed` Important violation, and the build-log's own attestation that BRANCH-1 is "all clean" is false — a RSAD-1 self-application failure that pytest cannot see (no test runs the audit against the live slice folder). One internal contradiction in the accepted ADR-090 (PCR clause) is a drift Minor.

## Changed files (in-scope)

tools/_worktree_paths.py
tests/methodology/test_worktree_paths.py
tests/methodology/test_slice_queue_pick_log.py
skills/slice/SKILL.md
skills/build-slice/SKILL.md
tools/branch_workflow_audit.py
tools/slice_queue_writer.py
tests/methodology/test_build_slice_skill_cp_r_step.py
tests/methodology/test_build_slice_skill_branch_state_preamble.py
tests/methodology/test_skill_parse_helpers.py
tests/methodology/test_methodology_changelog.py
CLAUDE.md
methodology-changelog.md
VERSION
plugin.yaml
pyproject.toml
architecture/slices/slice-099-create-worktree-at-slice-pick/build-log.md

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

#### B1: Slice's own build-log.md fails `branch_workflow_audit` (worktree-skip-malformed) — and the build-log falsely attests BRANCH-1 clean

- **Claim under review**: `build-log.md:45` — "Step-6 audit battery: ... BRANCH-1 ... — all clean." and `build-log.md:26` — "BRANCH-1 initially red ... reworded the event prose → clean."
- **Issue**: Running the actual audit against the slice folder reproducibly emits an **Important** violation:
  ```
  $PY -m tools.branch_workflow_audit architecture/slices/slice-099-create-worktree-at-slice-pick
  → worktree-skip-malformed: build-log.md Events contains `WORKTREE=skip` but doesn't
    conform to canonical shape ...
  → "clean": false  (violation_count: 1)
  ```
  Root cause: `branch_workflow_audit.py:421` does a bare-substring check `if "WORKTREE=skip" in content` over the **entire** build-log.md (despite the docstring at `:406` claiming it scans "Events"). `build-log.md:50` (the pre-finish-gate must-not-defer line) contains the contiguous literal token: `"...ClaimUsageError); WORKTREE=skip honored by /slice + /build-slice..."`. The slice was built in a **real** worktree (`escape_hatch_used: false`, real `slice/099-*` branch), so there is no canonical `WORKTREE=skip` DEVIATION line to satisfy the matcher — the prose mention alone trips it. The Builder deliberately broke the token on lines 26 and 59 (writing `` `WORKTREE`=skip ``) but **missed line 50**, where it remains contiguous.
- **Evidence**: `branch_workflow_audit.py:420-430` (substring scan + malformed violation); `build-log.md:50` (contiguous token); `build-log.md:26,45` (false "clean" attestation). The full pytest suite passes (1455) precisely because **no test runs `branch_workflow_audit` against the live slice-099 folder** — this gate is the Step-6 manual audit / `/validate-slice` BRANCH-1 leg, which this artifact will fail. No archived slice's build-log carries a prose-only `WORKTREE=skip` (verified across all `architecture/slices/slice-*` — this is the first), so this is net-new breakage, not a tolerated pattern. This is a Dim 9 RSAD-1 self-application failure: the slice that authors BRANCH-3 produces an artifact its own sibling audit refuses.
- **Proposed fix**: Break the contiguous token at `build-log.md:50` the same way lines 26/59 already are — e.g. `` `WORKTREE`=skip honored `` or "the worktree-skip escape-hatch honored". Then re-run `$PY -m tools.branch_workflow_audit architecture/slices/slice-099-create-worktree-at-slice-pick` and confirm `"clean": true` before the BRANCH-1 attestation at line 45 is truthful. (Secondary, out of scope but worth a backlog note: the audit's bare-substring scan over the whole file rather than the Events section is the latent substring-collision defect — APED-1 class — that makes any prose mention of the token a false positive; a follow-up could anchor the scan to the `## Events` block.)

### Majors

None.

### Minors

#### m1: ADR-090 internal contradiction — Options-considered cons clause says concurrent picks "depend on PCR", but Decision/Consequences + design + changelog all say "PCR is NOT involved"

- **Claim under review**: `ADR-090:23` (Option 3, CHOSEN, cons) — "...concurrent picks depend on **PCR** to resolve queue conflicts."
- **Issue**: This directly contradicts the same ADR's §Consequences (`ADR-090:38` — "**PCR is NOT involved** — it resolves `git rebase`-stage conflicts at `/commit-slice`, not pick-time commits"), design.md §Concurrency model (`design.md:43`), and the changelog entry (`methodology-changelog.md:44`). The **code is correct** — the pick-time path uses `_vault_write.safe_write_text`'s sidecar lock + git's index lock and never imports/invokes `parallel_conflict_resolver` (verified). So this is prose drift inside an `status: accepted`, append-only ADR (SUP-1: cannot edit in place). Per Sommerville requirements-design-code traceability, an accepted ADR carrying a self-contradicting concurrency claim is a latent trap for a future reader who quotes the cons clause as the authoritative model.
- **Evidence**: `ADR-090:23` vs `ADR-090:38`; design.md:43; methodology-changelog.md:44; absence of any PCR import in `slice_queue_writer.record_pick` / the SKILL.md Step 6.5 prose.
- **Proposed fix**: Since the ADR is append-only, do not edit line 23 in place. Add a one-line corrective erratum at the end of ADR-090 (e.g. an `## Erratum (2026-06-02)` note: "Option 3's cons clause's 'depend on PCR' is superseded by §Consequences — pick-time concurrency is serialized by `_vault_write` lock + git index lock; PCR is NOT involved"), OR record the correction in the slice's reflection.md so the contradiction is dispositioned rather than silently shipped.

#### m2: `branch_workflow_audit._check_worktree_skip_line` docstring says "Events" but scans the whole file

- **Claim under review**: `branch_workflow_audit.py:406` docstring — "Scan build-log.md **Events** for a canonical `WORKTREE=skip` line".
- **Issue**: The function reads the entire file (`build_log.read_text()` at `:413`) and matches/substring-checks against the whole content, not the `## Events` section. The docstring overstates the scope. This is the proximate enabler of B1. Per Wiegers Dim 1 (docstring drift), the comment claims a narrowing the code does not perform. (Behavior is pre-existing — slice-099 only re-imports `_SLICE_FOLDER_RE` here, it did not change this function — so this is logged as a Minor, not attributed as slice-099-introduced. But it is the latent cause B1 tripped.)
- **Evidence**: `branch_workflow_audit.py:405-431`.
- **Proposed fix**: Either narrow the scan to the `## Events` section (matching the docstring + eliminating the prose-collision FP class), or correct the docstring to "Scan build-log.md (whole file)". The former is the real fix but belongs in a follow-up since it changes audit behavior; the latter is a cheap honesty fix.

## Dimensions checked

- [x] Unfounded assumptions — m2 (docstring claims "Events" scope the code doesn't honor). Otherwise none: docstrings in `_worktree_paths.py` / `slice_queue_writer.py` match their regexes/logic (verified the `_PICK_LOG_BLOCK_RE` candidate-named-heading claim empirically — `### ## Pick log` does not false-match). No phantom imports — `_worktree_paths` exports (`canonical_worktree_path`, `slice_branch_name`, `seed_derived_dirs`, `_SLICE_FOLDER_RE`) all exist and are imported correctly by `branch_workflow_audit.py` and the tests.
- [x] Missing edge cases — none. Verified empirically: first-pick create, re-append over a realistic candidate-bearing queue, idempotent double-pick, name-boundary (slice-009 vs slice-099), candidate-literally-named-`## Pick log`, and CRLF-input (rewritten LF-faithful, EOL-DRIFT-1/ADR-033-conformant). `seed_derived_dirs` missing-source and partial-seed cases tested. The orphan-worktree (queue-commit-failed-after-worktree-add) case is honestly surfaced in SKILL.md Step 5.5 with recovery instructions, not silently lost.
- [x] Over-engineering — none. `_worktree_paths.py` is a thin, single-purpose helper; no speculative generality. The CLI emits exactly path+branch. `seed_derived_dirs`'s "skip if exists at all" accepts a documented partial-seed risk rather than building clobber-detection it doesn't need (correct YAGNI call per Beck).
- [x] Under-engineering — none. All 5 ACs have code elements: AC1 (SKILL.md Step 5.5 two-tree sequence), AC2 (`record_pick` + fail-visible `read_git_config_user`), AC3 (build-slice detect-or-create reorder), AC4 (audit refactor + ADR-090), AC5 (shared `_worktree_paths`). Methodology-audit conformance: PMI-1 clean (39 tools, underscore-prefix correctly excluded), TVFS-1 PASS, OSDG-1 drift green. **Exception flagged as B1**: BRANCH-1's own clean exit is NOT pre-satisfied by the slice's build-log.
- [x] Contract gaps — none. Public functions in `_worktree_paths.py` and the new `record_pick`/`_extract_pick_log_block`/`_iso8601_utc` carry type hints + docstrings. CLI exit codes documented (0/2). `record_pick` fail-visible contract (propagate `ClaimUsageError`, never write unattributed line) is correctly NOT wrapped in the non-fatal try/except in SKILL.md Step 6.5 — verified the structure: `write_slice_queue` is non-fatal (ADR-064), `record_pick`/`read_git_config_user` propagate.
- [x] Security — none. No new auth/input/injection surface. Pick-provenance is the existing cooperative git-identity model (ADR-067, explicitly non-security). No `shell=True`, no `eval`/`exec`, no hardcoded secrets. `shutil.copytree` is guarded by `not dst.exists()` (no clobber). git subprocesses pass `encoding="utf-8"`.
- [x] Drift from vault — m1 (ADR-090 PCR contradiction). Code-vs-design otherwise consistent: the build-time 4→5-part PMI bump correction propagated to changelog, version-sync test (`_at_v_0_81_0`), and design.md §version-bump-fan-out; all 5 version legs at 0.81.0; `branch_workflow_audit` refactor is byte-behavior-identical (verified via diff + `test_branch_workflow_audit_delegates_to_shared_helper`). MEPD-1 bump obligation fully discharged in code (not just declared).
- [x] Web-known issues — none. Verified the concurrency model's load-bearing assumption against official git docs: `git worktree add ... -b <branch> <default>` against a `<default>` already checked out in the main tree fails fail-visibly with `fatal: '<default>' is already checked out at ...` — exactly the serialization the design relies on. `shutil.copytree` / `argparse` SystemExit-code handling are stable stdlib. No deprecations or post-cutoff platform changes affect the chosen patterns.
- [x] Cross-cutting conformance — B1 (RSAD-1: slice's build-log fails its own sibling audit). APED-1: the slice-folder regex was MOVED byte-identically (not modified) — no new parse rule to adversarially battery-test, and the `_PICK_LOG_BLOCK_RE` was exercised against trailing-content, substring-collision (candidate-named-heading), empty-input, and CRLF variants (all pass). EOL-DRIFT-1: `_extract_pick_log_block` CRLF-normalizes before matching; `safe_write_text` is LF-faithful per ADR-033 — conformant. The `### Branch state` reorder composes correctly: point 1 (detect-existing, no re-seed), point 2 (create + `seed_derived_dirs`), point 4 (legacy dirty-dance, inline cp -r retained) — the test harmonization (`== 2` cp-r count + `seed_derived_dirs` presence) still trips drift, not weakened to vacuity.

## Builder disposition (TRI-1 not formalized until slice-062; recorded here for the reflection calibration loop)

- **B1 — ACCEPTED-FIXED**: reproduced (`branch_workflow_audit` exit 1 on the live slice folder; contiguous token on `build-log.md:50`). De-fanged the token; re-ran the audit → clean; the BRANCH-1 attestation is now truthful. Same descriptive-prose substring-collision FP class as the SVW-1:43 fix earlier in this build (N=3 now within slice-099). VALIDATED finding, zero false-alarm.
- **m1 — ACCEPTED-FIXED**: corrected ADR-090's Option-3 cons clause to align with §Consequences (the slice's own pre-merge ADR; the M-add-1 frontmatter fix is precedent for in-slice ADR-090 refinement). PCR-not-involved is now consistent across Options-considered + §Consequences + design + changelog.
- **m2 — ACCEPTED-DEFERRED (DISCOVERED)**: pre-existing latent defect in `branch_workflow_audit._check_worktree_skip_line` (bare whole-file substring scan vs the docstring's "Events" claim — the APED-1 substring-collision FP class that B1 and the build-time BRANCH-1/SVW-1 FPs all belong to). Out of scope for slice-099 (changing audit semantics needs its own slice + tests). Logged for a follow-up candidate (`anchor-worktree-skip-scan-to-events-section`). Recorded in reflection Discovered.
