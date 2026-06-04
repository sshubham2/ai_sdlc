# Critique: Slice 110 make-pipeline-vault-location-agnostic

**Critic reviewed**: mission-brief.md, design.md, ADR-101, ADR-102 (+ executed the freeze-cascade reload mechanism, the flip-sim suite, and the SKILL.md prose corpus against the real repo)
**Date**: 2026-06-04
**Result**: NEEDS-FIXES

## Summary

The core mechanism is **sound under execution** — the Critic verified the freeze-cascade reload works for direct consumers, there are NO unbounded transitive by-value imports of derived constants (the dominant build risk does NOT materialize), and the subprocess-env RETIRE pattern already exists (`test_slice_098_vault_routing.py:221`). The design is buildable. Three things were wrong as written: (1) the breaker count is undercounted (measured **99**, not 74); (2) the env-sim has a soundness asymmetry under-weighted for the RETIRE-class tests; (3) a hard test-count pin and the readiness-audit's Python-tokenizer-only architecture are load-bearing obstacles the design did not name.

## Findings

### Blockers (must address before /build-slice)

#### B1: AC1's binding gate is sized to a stale, undercounted breaker number (74 vs measured 99)
- **Claim under review**: mission-brief AC1 + design.md: "Today that override produces 74 methodology + 7 skills failures … ~38–74 test repoints."
- **Issue**: `AI_SDLC_VAULT_ROOT=<tmp>/architecture pytest tests/` → **99 failed, 1467 passed** (methodology **91**, not 74). Since the flip review, new consumers (`project_frame_synth` slice-106, `index_router_thinness_audit` slice-103, PCR-2a/2b, `drift_check_audit`) added sim-breakers. An inventory built to "74" misses ~17 methodology breakers; AC1's gate is then asserted against a never-complete inventory. Per Wiegers, an AC whose target quantity is wrong is not testable.
- **Evidence**: executed `99 failed`; distribution `test_state_transition_pin_audit.py` (16), `test_stranded_slice_audit.py` (8), `test_pcr_1_soft_regen_equivalence_guard.py` (8), `test_critique_review_prerequisite_audit.py` (8), `test_cross_spec_parity_audit.py` (7), `test_drift_check_audit.py` (6), + ~20 more.
- **Proposed fix**: at `/build-slice` Phase 1, re-measure the live flip-sim breaker set FIRST and treat THAT as the AC1 inventory of record; update AC1 + design.md to "~99 (re-measure at build; the count drifts)". APED-1 execute-don't-cite.
- **Builder draft**: **ACCEPTED-PENDING**. Framing corrected NOW (mission-brief AC1 + design → "~99, live-measured; `/build-slice` re-measures the live set as the inventory of record, never a copy-forward"). The actual re-measurement + the to-zero proof are the build gate.

#### B2: `test_vault_root_constant.py:201`'s `== 15` count-pin will break if the helper lands there (FBCD-1 sub-mode (c) / AP-10)
- **Claim under review**: design.md: "A shared test vault-isolation helper (`tests/methodology/conftest.py` extension or `tests/_vault_isolation.py`)" + AC5 "green at every commit."
- **Issue**: `tests/methodology/test_vault_root_constant.py:201` hard-pins `assert test_count == 15`. If the helper or its self-tests land in that module (the design's reuse anchor), the pin goes red and AC5 is violated at that commit. The docstring shows the count already bumped 10→12→15. The design enumerated zero count-pins.
- **Evidence**: `test_vault_root_constant.py:201` (confirmed by Builder: `assert test_count == 15`); docstring L186-205.
- **Proposed fix**: decide the helper home; if anything lands in `test_vault_root_constant.py`, bump `== 15` + the docstring + grep for other citations, same commit. Recommend a new file so the pin is provably untouched.
- **Builder draft**: **ACCEPTED-FIXED**. design.md + mission-brief now place the helper in a NEW `tests/_vault_isolation.py` with self-tests in a NEW `tests/methodology/test_vault_isolation.py` — deliberately NOT `test_vault_root_constant.py`, so the `== 15` pin is provably untouched (with a documented same-commit-bump fallback if anything must land there).

#### B3: The readiness audit is Python-tokenizer-based; SKILL.md prose needs a distinct classifier subsystem, not "extend `_iter_scan_files`"
- **Claim under review**: design.md + ADR-102: "extend `_iter_scan_files` / the classifier to also scan `skills/**/SKILL.md` prose."
- **Issue**: `audit_file` harvests via Python `tokenize` + `ast` (`vault_flip_readiness_audit.py:482`); Markdown has no Python tokens → feeding a SKILL.md raises immediately. "Extend `_iter_scan_files`" is NOT additive — it requires a parallel prose-classifier with its own region-anchoring (inline-backtick, fenced blocks, Write-target lines) sharing only the `Occurrence`/baseline output type. The over-flag surface is large: **244 `architecture/` prose mentions across 24 SKILL.md files**, of which only ~3 are shell ops + ~a-dozen real Write-targets (~16:1 noise:signal). Per AP-4 a new parser ⇒ code-Critic mandatory.
- **Evidence**: `vault_flip_readiness_audit.py:482` (`tokenize.TokenError`); `:488-507` globs `*.py` only; counted 244 mentions across 24 files.
- **Proposed fix**: a distinct `_classify_skill_prose(path) -> list[Occurrence]` region-anchored on inline-code / fenced-shell / Write-target; bare prose → `DOC_EXAMPLE_SAFE`/`NEEDS_HUMAN`, never `MUST_REWRITE`. Prove non-over-flag against the real 24-file corpus at build (MUST_REWRITE = exactly the ~15 real ops, NOT 244). Add a code-Critic pass (AP-4). Mark as the dominant Phase-2 risk.
- **Builder draft**: **ACCEPTED-PENDING**. Spec corrected NOW (design.md §B3 bullet + ADR-102 §Decision → distinct `_classify_skill_prose`, region-anchored, the 244:15 magnitude, baselines the deferred prose known-deferred). The non-over-flag + non-vacuity PROOF against the real corpus + the code-Critic pass are build obligations.

### Majors (address this slice)

#### M1: The env-sim/real-flip asymmetry is understated for the RETIRE-class worktree tests; "36 RETIRE = same fix as the 38" is only PARTLY validated
- **Issue**: `test_slice_098_vault_routing.py::test_audit_log_path_no_flip_byte_identity` is a genuine no-flip invariant (fix = unset env — validates the claim). BUT `test_stranded_slice_audit.py::test_in_progress_parallel_slice_does_not_halt` fails NOT via "`vault_is_external` forced True" but via the **worktree-classification** path (`classify_worktree_state`, `stranded_slice_audit.py:482`) reading the worktree milestone via VAULT_ROOT and missing the in-tree fixture (`klass=INDETERMINATE/fresh-worktree-no-milestone`); the `vault_is_external` STOP guard (`:328`) is only on the bare-branch path. The design's single stated cause is wrong for the worktree tests; the "pin own vault root" fix still works, but the Builder reasoning from the wrong cause looks for the wrong symptom.
- **Evidence**: executed → `klass=INDETERMINATE reason='fresh-worktree-no-milestone'` (NOT a `vault-external` reason); `stranded_slice_audit.py:328` vs `:471-494`.
- **Proposed fix**: correct the cause-model; at build bucket the ~36 RETIRE tests by path (worktree-resolution-drift vs bare-branch-STOP-guard) before the uniform fix; spot-check per-test that the pinned-in-tree fix mirrors post-flip resolution.
- **Builder draft**: **ACCEPTED-FIXED**. design.md Decisions table corrected to the two failure paths (bare-branch STOP guard vs worktree fixture-path-resolution drift), both cured by pinning the test's own vault root; "bucket by path at build" recorded.

#### M2: The in-loop-skill break enumeration is incomplete / mis-scoped (`git add`, the `<wt_path>/`-prefixed `/slice` scaffold, 5 un-named graphify sites)
- **Issue**: (a) `/build-slice:88` `git add architecture/...` is a literal in-tree pathspec post-flip-broken but never traced. (b) `/slice:267-268` scaffold writes are already `<wt_path>/architecture/...` (worktree-prefixed) — blanket-routing them risks moving slice-authoring artifacts OUT of the worktree (BRANCH-3 violation). (c) `graphify vault architecture` exists at `/adopt:72, /discover:102, /heavy-architect:184, /query-design:59, /sync:176` AND `/design-slice:62` — AC4 named only `/design-slice`.
- **Evidence**: grep → `build-slice:88`, `slice:267-268` (`<wt_path>/`), 6 graphify sites, `reflect:320`/`archive:51`.
- **Proposed fix**: trace `/build-slice:88`; EXPLICITLY decide `/slice:267-268` (keep worktree-prefix, no route — flip-irrelevant) and do not blanket-route; enumerate all 6 graphify sites (or scope AC4 to `/design-slice` + defer the rest with rationale).
- **Builder draft**: **ACCEPTED-FIXED**. AC2 narrowed to the UNAMBIGUOUS ops (archive `mv` + drift-log.md + commit-slice archived reads); the bootstrap-entangled per-slice active-folder writes (`/reflect` reflection.md, `/validate` validation.md, `/slice` scaffold, `/build-slice` git add) DEFERRED to the flip slice (it owns worktree-vs-external); AC4 scoped to in-loop `/design-slice:62`, the 5 non-in-loop graphify sites deferred to the prose-rewrite slice (enumerated in Out-of-scope).

#### M3: must-not-defer "OSDG-1 re-sync for /archive" is factually wrong — /archive is NOT OSDG-1 guarded
- **Issue**: No `test_archive_skill_drift.py`; `/archive` is absent from the OSDG-1 set. Editing `/archive:51` needs no re-sync; listing it sends the Builder chasing a phantom guard.
- **Evidence**: `ls tests/methodology/*skill_drift*` → 14 files; `test_archive_skill_drift.py` absent (Builder also confirmed `/drift-check` AND `/validate-slice` unguarded).
- **Proposed fix**: list only genuinely-guarded edited skills; note unguarded edited skills as "no re-sync."
- **Builder draft**: **ACCEPTED-FIXED**. must-not-defer corrected: guarded = `/reflect`, `/commit-slice` (the only edited-AND-guarded skills in the narrowed AC2); explicitly NOT-guarded (no re-sync) = `/archive`, `/drift-check`, `/validate-slice`.

### Minors

#### m1: AC5 verification command mixes shells
- **Issue**: `git ls-files architecture | measure` mixes git + PowerShell `Measure-Object` without an explicit shell.
- **Builder draft**: **ACCEPTED-FIXED**. Verification row 5 → PowerShell `(git ls-files architecture | Measure-Object -Line).Lines`.

#### m2: WIRE-1 row right, but the readiness-audit's new prose-parser triggers AP-4 (unstated)
- **Issue**: the prose classifier is a new parser inside an existing module — no new module, but AP-4 code-Critic-on-new-parser applies.
- **Builder draft**: **ACCEPTED-FIXED**. design.md §B3 + ADR-102 §Decision now state the AP-4 code-Critic obligation explicitly.

#### m3: helper home undecided (interacts with B2)
- **Builder draft**: **ACCEPTED-FIXED**. Decided — new `tests/_vault_isolation.py` (folds into B2).

## Dimensions checked
- [x] Unfounded assumptions — **B1** (stale "74" vs measured 99), **M1** (wrong RETIRE failure cause for the worktree path), **M3** (`/archive` falsely asserted guarded). The freeze-cascade reload was EXECUTED and is SOUND (no transitive by-value imports; verified on supersede_audit, slice_queue_writer, parallel_conflict_resolver).
- [x] Missing edge cases — **M2** (incomplete enumeration: git add, `<wt_path>/`-prefixed scaffold, 5 graphify sites). Cross-test contamination: reloading a consumer does NOT reload its runtime cross-tool dependency (pcr→slice_queue_writer) — the reload set is per-call-graph; flagged for build.
- [x] Over-engineering — none. ADR-101 correctly rejects the explicit-`vault_root`-param (would change correct production) + per-test-inline (duplication).
- [x] Under-engineering — **B3** (the "extend `_iter_scan_files`" framing under-builds the prose classifier — a new parser subsystem; AC3 is the only deterministic AC2 guard), **B2** (count-pin obstacle had no design element).
- [x] Contract gaps — none new. The helper's contract ("consumer VAULT_ROOT changed before yield") is specified with a load-bearing non-vacuity assert.
- [x] Security — none (test + skill-prose + audit edits only; no auth/secrets/injection surface).
- [x] Drift from vault — none contradicting. ADR-101/102 (supersedes null, cheap) consistent with the reversible-prep intent + ADR-065/085/089. `_vault_paths` no-behavior-change pledge consistent (design consumes, never edits the seam).
- [x] Web-known issues — none applicable (in-repo Python `importlib.reload` + pytest + in-house audit; reload semantics verified empirically).
- [x] Cross-cutting conformance — B1/B2/M1/M2/M3 all cross-cutting (FBCD-1 sub-mode (c) for B2; tooling-doc-vs-implementation parity for B3; phantom-guard citation for M3; APED-1 execute-don't-cite for B1). The Critic applied APED-1 throughout (executed the reload cascade, the flip-sim suite = 99, the SKILL.md corpus = 244).

## Triage

**Triaged by**: user
**Date**: 2026-06-04
**Final verdict**: NEEDS-FIXES

> User ratified at TRI-1 (2026-06-04): accepted all dispositions as shown → **proceed to /build-slice**. The dual-review (critique-review.md, verdict EXTEND) reconciled into this triage: B1 count corrected (empty-sim 99 → seeded ~74), B2 severity Blocker→Major, and meta-Critic missed findings M-add-1/2/3 added as ACCEPTED-FIXED rows.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-PENDING | **Count CORRECTED** per `/critique-review` (first Critic's "99" was an EMPTY-vault sim; the real flip is SEEDED → ~82 full / ~74 methodology). mission-brief AC1 + design reverted to the seeded number; the "defense-in-depth superset" framing struck. `/build-slice` re-measures the live SEEDED flip-sim set as the AC1 inventory of record (APED-1; never the empty-dir number). |
| B2 | Major | ACCEPTED-FIXED | (Severity Blocker→Major per `/critique-review` SEVERITY-WRONG — a single conditional obstacle with a trivial fix.) Helper home = NEW `tests/_vault_isolation.py` + NEW `test_vault_isolation.py`; `== 15` pin provably untouched. |
| B3 | Blocker | ACCEPTED-PENDING | The audit IS tokenizer-only (can't ingest Markdown). REUSE direction adopted (see M-add-1); non-over-flag (244 NOT flagged) + non-vacuity + code-Critic (AP-4) proven at build. |
| M1 | Major | ACCEPTED-FIXED | design.md cause-model corrected to the two failure paths (bare-branch STOP vs worktree fixture-resolution drift); bucket-by-path at build. |
| M2 | Major | ACCEPTED-FIXED | AC2 narrowed to unambiguous ops; per-slice active-folder writes + non-in-loop graphify deferred to the flip slice (enumerated). |
| M3 | Major | ACCEPTED-FIXED | OSDG-1 list corrected (guarded: /reflect,/commit-slice; not-guarded: /archive,/drift-check,/validate-slice). |
| m1 | Minor | ACCEPTED-FIXED | AC5 verification → PowerShell `(... | Measure-Object -Line).Lines`. |
| m2 | Minor | ACCEPTED-FIXED | AP-4 code-Critic obligation stated in design + ADR-102. |
| m3 | Minor | ACCEPTED-FIXED | Helper home decided (new file) — folds into B2. |
| M-add-1 | Major (meta) | ACCEPTED-FIXED | Reuse existing `vault_flip_prose_inventory.py` (op-gate mode) instead of a 3rd parallel classifier (CSP-1/DRY) — design §B3 + ADR-102 + AC3 + Components updated. |
| M-add-2 | Major (meta) | ACCEPTED-FIXED | Deferred per-slice-write prose → DISTINCT gate-visible `DEFERRED_TO_FLIP` class (owner=flip slice, its pre-finish drives to ∅), NOT a silent baseline (AP-12) — AC3 + design + ADR-102 updated. |
| M-add-3 | Major (meta) | ACCEPTED-FIXED | Shippability propagation (rows 108/109 per RPCD-1/SCPD-1) added to the pre-finish gate. |
