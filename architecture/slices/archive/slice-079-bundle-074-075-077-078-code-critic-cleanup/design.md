# Design: Slice 079 bundle-074-075-077-078-code-critic-cleanup

**Date**: 2026-05-29
**Mode**: Standard

## What's new

- Surgical fixes to N=19 in-scope code-Critic v1 advisory findings (slice-074 M1+m1-m5 / slice-075 m1 / slice-077 M2+m3-m6+m8+m9 / slice-078 m1-m3+m5 + P3.10) landed across live methodology surfaces.
- One NEW shared test-helper module `tests/methodology/_skill_parse_helpers.py` (extracts the byte-identical `_branch_state_section` duplicated between `test_build_slice_skill_cp_r_step.py` + `test_build_slice_skill_dirty_tree_resolution.py` per slice-074 m4).
- One NEW data constant inside an existing module: `tools/pulse_worktree_resolver._UNKNOWN_REASON_WARN_TEMPLATES: Mapping[str, str]` (slice-077 m5 design→code translation gap closure — MAP-ONLY shape per /critique B1 + M1 ACCEPTED-FIXED; no new public helper; no JSON state-dict shape change; the SKILL.md Drift & flags consumer reads the constant per slice-077 m5 option (a) Haiku-side prose interpretation). One inside-module signature change: `tools/parallel_conflict_resolver._format_vault_claim_audit_entry` signature extended with explicit `winner`/`loser` parameters (slice-078 m1 DRY).
- N=6 findings DEFERRED-with-rationale (5 archive-immutability + 1 extraction-trigger-slice + 1 conformance-not-defect — split across the two): documented in §"Decisions made (deferrals)" below per AC#3 carve-out.

## What's reused

- [[skills/build-slice/SKILL.md]] — Branch state section variable assignments + Phase E recipe (modified in this slice)
- [[skills/commit-slice/SKILL.md]] — Step 5b sub-step 2.1/2.5 anchor block (slice-075 m1 line-start anchor fix in the test pin, not the prose)
- [[tools/pulse_worktree_resolver.py]] — slice-077's PWA-1 helper (modified)
- [[tools/parallel_conflict_resolver.py]] — slice-076 PCR-1 + slice-078 PCR-2a helpers (modified)
- [[tools/slice_queue_writer.py]] — slice-067 PSQ-1 helper + slice-072 PSQ-2 helper (modified for P3.10)
- [[architecture/shippability.md]] — single-source-of-truth catalog; new rows per finding cluster
- [[architecture/risk-register.md]] — no risk transitions (cleanup-discharge class; no R-NN retired)
- [[architecture/critic-calibration-log.md]] — 2026-05-29 entry already recorded; APED-1 self-application clause-5 already applied to `agents/critique.md` (CAD-1 clean)
- [[ADR-019]] / [[ADR-046]] / [[ADR-063]] — BRANCH-1 / split-slice-folder / BRANCH-2 govern slice-079's branch + worktree layout
- [[ADR-024]] — CRP-1 bootstrap exception (slice-079 is N+1 first-governed-slice of /critic-calibrate Proposal 1 applied 2026-05-29)
- Per CLAUDE.md: code is truth; deviations need an ADR; refactors need a slice — slice-079 IS the dedicated cleanup slice per voluntary-restraint N=18 cumulative pattern (slice-038 / slice-046 / slice-071 precedent for bundled-cleanup-at-N+1 with 0 ADRs and no methodology-changelog entry).

## Components touched

### `skills/build-slice/SKILL.md` (modified)

- **Responsibility**: governs /build-slice prereq + Phase E recipe; the canonical Branch state codefence
- **Lives at**: `skills/build-slice/SKILL.md` (forward-synced to `~/.claude/skills/build-slice/SKILL.md` per OSDG-1 in lock-step)
- **Key interactions**: read by Claude at runtime; pinned by `tests/methodology/test_build_slice_skill_*.py` modules
- **This slice's edits**:
  - Fix A (slice-074 M1 / P1.1): extract `default=`, `repo_root=`, `wt_base=` variable assignments from point 1's codefence into a shared pre-amble ABOVE the numbered list (chosen over option (b) re-derive-in-point-4 because it's DRY + works for points 2/3/4 alike, not just point 4). The numbered points become true branches that all consume the pre-amble's variables.
  - Fix B (slice-074 m1): replace `git add <scaffolding files>` placeholder at L78 with the concrete pathspec `git add architecture/slices/slice-NNN-<slice-name>/ architecture/slice-queue.md` (the canonical scaffolding set per the mission-brief's documented enumeration).

### `tests/methodology/_skill_parse_helpers.py` (NEW)

- **Responsibility**: shared helpers for parsing structural sections of `skills/*/SKILL.md` files in test pins
- **Lives at**: `tests/methodology/_skill_parse_helpers.py` (created by this slice; per WIRE-1 exemption pattern for internal test helpers — see Wiring matrix)
- **Key interactions**: consumed by `test_build_slice_skill_cp_r_step.py` + `test_build_slice_skill_dirty_tree_resolution.py`
- **Public surface**: one function `_branch_state_section(skill_md_text: str) -> str` returning the `### Branch state` section body extracted from `skills/build-slice/SKILL.md`'s prose. Implementation: byte-equivalent to the duplicated function bodies removed from the two test modules (slice-074 m4).

### `tests/methodology/test_build_slice_skill_cp_r_step.py` + `test_build_slice_skill_dirty_tree_resolution.py` (modified)

- **Responsibility**: pin BRANCH-2 + R-20 codified prose against silent regression
- **This slice's edits**:
  - Fix C (slice-074 m2): tighten `test_cp_r_lines_use_if_then_guard_for_source_dir_absence`'s assertion from `len(matches) >= 2` to `len(matches) == 4` (2 source dirs × 2 codefences; intentional duplication pinned exactly). Codifies the prior implicit `>=2`-tolerated count divergence as a deterministic invariant.
  - Fix D (slice-074 m3): add a 2-line docstring example to `point_4_no_dash_b_pattern`'s definition naming the negative-lookahead's "before `#`" comment-exclusion scope, so a future Builder refactoring the regex preserves the comment-safety.
  - Fix E (slice-074 m4): replace both modules' local `_branch_state_section` definitions with `from tests.methodology._skill_parse_helpers import _branch_state_section`.

### `tests/methodology/test_r_20_retired.py` (modified)

- **This slice's edit**:
  - Fix F (slice-074 m5): replace `subprocess.run(..., check=True)` with explicit `proc = subprocess.run(..., capture_output=True, text=True); assert proc.returncode == 0, f"audit failed: stderr={proc.stderr!r}"` shape (audits debuggability — stderr surfaces on failure instead of bare CalledProcessError).

### `tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py` (modified)

- **This slice's edit**:
  - Fix G (slice-075 m1): replace `section.find("2.1.")` substring extraction with line-start anchor extraction (`re.search(r'^2\.1\.\s', section, re.MULTILINE).start()` for `two_one_pos`; same shape for `two_five_pos`). Add post-extraction guard `assert block.count("silent-WT-discard") == 1, "narration leakage detected"`. Pre-fix: block extraction widens to include L169 narration paragraph (`block.count == 2`); post-fix: deterministic single-occurrence (the actual sub-step 2.1. body only). Closes the RSAD-1 annotation-literal-pollution sub-class for this anchor.

### `tools/pulse_worktree_resolver.py` (modified, slice-077 PWA-1 helper)

- **Responsibility**: BRANCH-2 worktree-aware /pulse classifier (slice-077; ADR-070)
- **This slice's edits**:
  - Fix K (slice-077 m5 — design→code translation gap closure; MAP-ONLY shape per /critique B1 + M1 ACCEPTED-FIXED): add module-level constant `_UNKNOWN_REASON_WARN_TEMPLATES: Mapping[str, str]` mapping each of the **canonical 8 UNKNOWN sub-reasons** verified empirically at `tools/pulse_worktree_resolver.py:77-86` `_UNKNOWN_REASONS` tuple — `fresh-worktree-no-milestone` / `milestone-missing-in-active-and-archive` / `milestone-frontmatter-malformed` / `detached-head` / `dirty-worktree` / `merge-base-error` / `head-unresolvable` / `slice-folder-name-drift` → its canonical WARN string template. **NO new public helper; NO new `"unknown_warn"` state-dict field; NO change to CLI text-mode emission shape.** The mapping is pure data exposed at module scope so the `skills/pulse/SKILL.md` Drift & flags section can `Read` `tools/pulse_worktree_resolver.py` + perform an `_UNKNOWN_REASON_WARN_TEMPLATES.get(reason, fallback)` lookup at Haiku-side prose-interpretation time (slice-077 m5 option (a), preserved as the canonical consumer). Closes slice-077 design.md L181-191 / ADR-070 contractual promise via the option-(a) data-not-dispatch path; preserves MEPD-1 EXCLUDE posture (no new public surface to ADR; no JSON contract widening). Test plan row K (below) parameterizes over the 8 canonical reason-keys with the empirical `_UNKNOWN_REASONS` tuple as the byte-equal anchor.
  - Fix L (slice-077 m6 — AND-logic per /critique m2 ACCEPTED-FIXED): `_parse_worktree_porcelain` detects bare-repo by `"bare"` field present in first-block (per slice-077 code-review m6 original prescription `"bare" in block[0]`); `detect_active_worktrees` returns `tuple()` for bare-repo case + logs WARN to stderr (`"bare repo detected; no active worktrees applicable"`). No behavior change for non-bare (this repo). Tightened from the prior "OR (no worktree key)" draft because git's porcelain output guarantees `worktree <path>` as first line for non-bare; widening to OR introduces an impossible-state branch.
  - Fix M (slice-077 m8): `_parse_milestone_stage` strips UTF-8 BOM (`﻿` prefix) before `text.startswith("---")` check — covers PowerShell-saved milestone.md files. Three-line addition; no behavior change for BOM-less files.
  - Fix N (slice-077 m9): replace `stripped.startswith("stage:")` prefix-match with `stripped.split(":", 1)[0].strip() == "stage"` exact-key match — tightens against hypothetical `stage_owner:` / `stage-history:` keys. Behavior-preserving today; hardening only.

### `tests/skills/pulse/test_cli.py` (modified)

- **This slice's edit**:
  - Fix H (slice-077 M2): drop the `pytest.skip("classify returned error...")` branch at L90-105. Configure the synthetic repo's default branch deterministically via `_git("config", "init.defaultBranch", "master", cwd=repo_root)` + `_git("symbolic-ref", "HEAD", "refs/heads/master", cwd=repo_root)` + `_git("update-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/master", cwd=repo_root)` at the test fixture (or via a `@pytest.fixture(autouse=True)` helper). Assertion shape becomes: `assert proc.returncode == 0`, `data = json.loads(proc.stdout)`, `assert data["state"] in {valid-state-set}`. ADD a separate explicit test `test_cli_classify_returns_error_on_unresolvable_default_branch` exercising the stderr/exit-1 fallback path (no `init.defaultBranch` configured → `_resolve_default_branch` returns None → exit 1 with `"default-branch-unresolvable"` stderr token).

### `tests/skills/pulse/test_classify_worktree_state.py` + `test_detect_active_worktrees.py` (modified)

- **This slice's edits**:
  - Fix I (slice-077 m3): drop unused `import pytest` from both modules.
  - Fix J (slice-077 m4): drop unused `WorktreeStateClassification` from `test_classify_worktree_state.py`'s import tuple.

### `tools/parallel_conflict_resolver.py` (modified, slice-076 PCR-1 + slice-078 PCR-2a helper)

- **Responsibility**: parallel-conflict-resolution machinery for SOFT/VAULT_CLAIM auto-resolve + HARD-stop
- **This slice's edits**:
  - Fix O (slice-078 m1 — DRY at signature boundary; pragma:no-cover discipline per /critique M2 ACCEPTED-FIXED; signature shape corrected per /critique-review M-add-1 ACCEPTED-FIXED): extend `_format_vault_claim_audit_entry`'s signature from the actual pre-fix 4-arg `(diag, result, timestamp, head_sha) -> str` (per code reality at `tools/parallel_conflict_resolver.py:923-928`) to 6-arg `(diag, result, timestamp, head_sha, winner: ClaimEntry | None, loser: ClaimEntry | None) -> str`. Single-source-of-computation lives in `_append_audit_log` (existing scope near L1270-1277 where `timestamp` + `head_sha` are already computed; adding `winner`/`loser` computation in the same scope is a small additive change): the dispatch at L1277 becomes `_format_vault_claim_audit_entry(diag, result, timestamp, head_sha, winner, loser)`. Formatter body no longer re-derives via `_collect_same_candidate_different_identity` + `_select_timestamp_winner`. `_append_audit_log`'s public 3-arg surface UNCHANGED — resolver call sites continue to invoke `_append_audit_log(repo_root, diag, result)` verbatim. The `(unavailable)` defensive fallback is **kept with a `# pragma: no cover` marker + a docstring line naming the rationale** ("preserves robustness to None inputs for callers outside the canonical SOFT/VAULT_CLAIM resolve loop; no current caller exercises this branch but the defensive shape documents the contract that the helper IS robust"). Future selection-semantic changes (e.g., R-23 clock-skew tiebreaker via PSQ-2 `Claim-seq`) update one site, not two. Test plan row O (below) parameterizes over both branches: "winner/loser used when passed" + "(unavailable) rendered when passed None".
  - Fix P (slice-078 m2): `_parse_queue_candidates_for_replacement._flush()` default changes from `"UNKNOWN-NO-GRAPH"` to a new `"MISSING-FIELD"` sentinel (distinct from PSQ-1's enumeration). Downstream filter at `_pick_loser_replacement` is updated: `if safety not in {"NON-OVERLAPPING"}: continue` (rejects both `"MISSING-FIELD"` and `"UNKNOWN-NO-GRAPH"` + `"UNKNOWN-NO-HINT-FILES"` + `"OVERLAPS-WITH-*"` — semantically equivalent reject; observability gain). New test exercises a candidate block with `### name` header + body but NO `**Parallel-safety:**` field-line.
  - Fix Q (slice-078 m3): add a 5-line docstring block to `resolve_vault_claim_conflict`'s Step 5 acknowledging the inversion vs SOFT path's pending_writes batching pattern + naming the single-file blast-radius argument ("Single-file scope → inline write acceptable; PCR-1's pending_writes batching addressed multi-file partial-resolution windows that don't apply here"). Pin via structural-pin test asserting the docstring contains the substring `"Single-file scope"` + `"PCR-1's pending_writes"`.
  - Fix R (slice-078 m5): add a 2-line inline comment after `_VaultClaimDispatch`'s docstring: `# Sibling to _SoftResolutionError; both inherit directly from Exception — catch-order in resolve_soft_conflict's exception loop is independent (not load-bearing by inheritance)`. Structural-pin test asserts the comment present.

### `tools/slice_queue_writer.py` (modified, slice-067 PSQ-1 helper)

- **This slice's edit**:
  - Fix S (P3.10 cp1252 mojibake — REFRAMED to structural-pin only per /critique B2 + M3 ACCEPTED-FIXED): empirical APED-1 verification at /critique time (B2 evidence) demonstrated all 9 encoded-I/O sites in `tools/slice_queue_writer.py` (L134, 183, 214, 266, 351, 450, 703, 790, 847) **already use explicit `encoding="utf-8"`** — the slice-074 mojibake observed at /slice Step 6.5 was NOT caused by this helper. Slice-079's contribution at this surface is a **structural-pin regression-guard test**: assert no `Path.{read,write}_text(...)` or `open(...)` call in `tools/slice_queue_writer.py` lacks the `encoding=` keyword argument. FAIL→PASS contrast: synthetic mutation (test-fixture removes `encoding="utf-8"` from one site) → test FAILS; restore → test PASSES. The actual mojibake-source-finding work (likely upstream — `tools/slice_pick.py` subprocess invocations, `PYTHONIOENCODING` env defaults at Windows console codepage layer, or the `/slice` skill's own subprocess invocation of `tools.slice_queue_writer`) is **DEFERRED to source-pending-items as P3.10' `find-real-mojibake-source` candidate** for a future slice once root cause is identified. AC#5's "regression tests pin both" obligation is honestly met by the structural-pin (P3.10 is now a regression-guard not a fix; the encoding=utf-8 pattern is structurally enforced going forward).

## Contracts added or changed

### `tools/pulse_worktree_resolver._UNKNOWN_REASON_WARN_TEMPLATES: Mapping[str, str]` (NEW data constant — MAP-ONLY per /critique B1 + M1 ACCEPTED-FIXED)

- **Defined in code at**: `tools/pulse_worktree_resolver.py` (added by this slice as a module-level constant near `_UNKNOWN_REASONS`)
- **Surface shape**: pure-data mapping; one entry per canonical `_UNKNOWN_REASONS` member (8 keys at L77-86); each value is a single-line WARN template string per slice-077 design.md L181-191. **No new public helper. No new JSON state-dict key. No change to CLI text-mode emission.** The data is consumed Haiku-side at `skills/pulse/SKILL.md` Drift & flags prose-interpretation time via a Read+lookup pattern.
- **Auth model**: N/A — pure data constant.
- **Error cases**: caller-side `.get(reason, fallback)` lookup is the canonical access pattern (the constant itself never raises).
- **Contract narrowing rationale**: slice-077 m5 enumerated two options (a) Haiku-side prose interpretation vs (b) code-side helper dispatch. Slice-079 picks (a) — the constant is the data anchor; the consumer (SKILL.md prose) is the dispatcher. Preserves slice-077's existing JSON state-dict shape + CLI text-mode shape (no widening; MEPD-1 EXCLUDE preserved; no ADR needed).

### `tools/parallel_conflict_resolver._format_vault_claim_audit_entry` (signature extended)

- **Defined in code at**: `tools/parallel_conflict_resolver.py:923-928` (modified by this slice; current pre-fix signature verified empirically per /critique-review M-add-1 ACCEPTED-FIXED)
- **Signature change**: old `_format_vault_claim_audit_entry(diag: ConflictDiagnostic, result: ResolutionResult, timestamp: str, head_sha: str) -> str` (the actual 4-arg pre-fix signature at L923-928, not the 2-arg shape the pre-fix design.md mis-cited per /critique-review M-add-1 catch) → new `_format_vault_claim_audit_entry(diag: ConflictDiagnostic, result: ResolutionResult, timestamp: str, head_sha: str, winner: ClaimEntry | None, loser: ClaimEntry | None) -> str` (6-arg post-fix shape)
- **Caller-site change**: `_append_audit_log(repo_root, diag, result)` PUBLIC SURFACE UNCHANGED. Inside `_append_audit_log` (the existing internal scope at `tools/parallel_conflict_resolver.py` near L1270-1277 where `timestamp` + `head_sha` are already computed before the dispatch), winner/loser are computed via `_collect_same_candidate_different_identity(diag.claim_history)` + `_select_timestamp_winner(...)` BEFORE the VAULT_CLAIM-branch dispatch at L1277, then passed to `_format_vault_claim_audit_entry(diag, result, timestamp, head_sha, winner, loser)`. Single computation site preserved (the DRY goal of Fix O); `_append_audit_log` external surface preserved.
- **Compatibility**: this is a private helper (leading underscore); no external consumers; same-slice signature update is contract-internal. `_append_audit_log` itself remains a 3-arg public-ish helper, no signature change at its boundary.

### `tools/parallel_conflict_resolver._parse_queue_candidates_for_replacement` default sentinel

- **Surface change**: missing `**Parallel-safety:**` field default `"UNKNOWN-NO-GRAPH"` → `"MISSING-FIELD"`.
- **Compatibility**: downstream filter rejects both equivalent (semantic-preserving change; observability gain only).
- **Test**: new test exercises candidate block without `**Parallel-safety:**` line.

## Data model deltas

None. No DB / schema / Pydantic-model changes.

## Wiring matrix

Per **WIRE-1**.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/_skill_parse_helpers.py` | `tests/methodology/test_build_slice_skill_cp_r_step.py` + `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py` (both import `_branch_state_section`) | `tests/methodology/test_skill_parse_helpers.py::test_branch_state_section_returns_section_body` pins the helper's contract directly; the sibling `test_helper_defined_only_once_in_test_corpus` test in the same file is a **global test-corpus structural invariant** (greps all `tests/methodology/*.py` for duplicate `_branch_state_section` defs), not a module-consumer test — exempt-by-categorization per /critique m1 ACCEPTED-FIXED. rationale: corpus-grep tests guard the test corpus itself, not the helper module; per WIRE-1's documented exemption pattern for global structural invariants | — |

No other new modules. All other fixes edit existing files in-place.

## Decisions made (ADRs)

**Zero new ADRs.** Per **MEPD-1(b)** discharge: this slice is a no-VERSION-bump conformance / cleanup-discharge class.

**MEPD-1(b) why-none verification**: confirmed against the actual META-1 enforcing assertion at `tests/methodology/test_methodology_changelog.py:136` — `re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", changelog, flags=re.MULTILINE)` + `Rule reference` substring check on each split section. Slice-079 adds zero new `## v…` sections → vacuously satisfies the assertion (there is no new section that could fail the Rule-reference check). Precedent class (cumulative N=7 including slice-079): slice-040 (R-10 retirement) + slice-043 (R-6 retirement) + slice-045 (R-11 born-retired) + slice-057 (R-15 part-b) + slice-061 (R-16/R-17/R-18 surfacing without minting rules) + slice-071 (bundle-066-070 cleanup, same shape) = N=6 prior + slice-079 = N=7.

**Rationale for no rule-IDs**: each of the 19 in-scope fixes discharges a previously-deferred finding with its own regression test as the durable structural backstop. The corpus of fixes is conformance-to-existing-discipline (DRY / RSAD-1 / TPHD-1 / EOL-DRIFT-1 / OSDG-1 / SCMD-1 / APED-1 / FBCD-1 family already minted), not introduction of new methodology axis. Codifying a "bundled-cleanup discipline" rule-ID would be premature speculative generality — the voluntary-restraint + bundled-cleanup-at-N+1 pattern is N=18 cumulative empirical without a rule-ID and is working.

## Decisions made (deferrals — DEFER-with-rationale per AC#3 / #1 / #2 / #4 carve-out)

N=6 findings DEFERRED in this slice. Per mission-brief AC carve-out ("a documented 'DEFER with rationale' for any finding determined non-actionable"). Audit trail captured here:

### DEFER-1 — slice-075 m2: archived mission-brief.md L5/L66/L72/L81 + design.md L6 stale `enable-parallel-slice-pending-items.txt` anchors

- **Disposition**: DEFERRED — non-actionable per archive-immutability convention.
- **Rationale**: slice-075 is archived; its `mission-brief.md` + `design.md` are HISTORICAL records. Editing in-place violates the slice-040 R-10 retirement-precedent (BC-PROJ-6) "no edit-in-place of prior risk-register prose" applied transitively to all archived slice scaffolding. The stale anchors point to a file that moved during slice-075 build; the historical reference describes the slice's then-current state. Future readers grepping `enable-parallel-slice-pending-items.txt` will land on the archived slice-075 surfaces by design — that's the historical anchor. Slice-queue.md's generated references regenerate on every `/slice` run from current input.
- **Captured class**: TPHD-1 sub-mode (a) "file-move-but-anchor-not-swept" variant — generic lesson already in aggregated lessons (slice-075 reflection §Lessons). No new test needed.

### DEFER-2 — slice-077 M1 + m1: extraction-trigger slice is `parallel-slice-family-parity-audit`

- **Disposition**: DEFERRED — fix-surface owner is a different slice.
- **Rationale**: slice-077 M1 (cross-spec parity action-case lowercase vs UPPERCASE) + m1 (`INSTALLED_SURFACES` inline vs module-level) both require an architectural decision spanning the 6-member parallel-slice family (BRANCH-2 + PSQ-1/2/3 + PCR-1/2a). Per slice-077 reflection L93 + critique disposition, the canonical fix-surface is the queued `parallel-slice-family-parity-audit` slice (currently slice-queue.md #3 post-079), where the uppercase/lowercase decision lands canonically across all parallel-family helpers in one fix block. Bundling here would (a) require touching 6 helpers' JSON-output shapes simultaneously, and (b) pre-empt the parity-audit slice's own design decisions on module-level constant extraction conventions. **NOT** in archive-immutability class (the files are live); deferred for fix-surface-ownership reasons.
- **Captured class**: extraction-trigger N=2 cumulative on this finding-shape — design→code translation gap, design-Critic-reachable. No additional structural-pin needed pre-parity-audit slice.

### DEFER-3 — slice-077 m2 + m10: archived design.md L73 + build-log.md L64 phantom test name `test_step_1_documents_pulse_worktree_resolver_dispatch`

- **Disposition**: DEFERRED — non-actionable per archive-immutability convention.
- **Rationale**: slice-077 is archived; its design.md + build-log.md are HISTORICAL records. The phantom test name in WIRE-1 row L73 (design.md) + L64 (build-log.md) was pinned at slice-077 build-time; the actual implemented test functions are `test_step_1_documents_git_worktree_list_pre_read` etc. The phantom-test-name discrepancy is preserved in the historical record as the audit trail of slice-077's mid-build WIRE-1 row drift (PTFFD-1 class) — fixing in-place would erase that audit trail. The drift is captured by AGGREGATED LESSONS in slice-077 reflection (TPHD-1 sub-mode (a) "phantom-test-citation-in-design-meta" sub-class N=1 watch-list).
- **Note**: the PTFFD-1 audit `tools/test_first_audit.py` runs at /build-slice Step 6 and would catch this class for slice-079's own TF-1 plan if it occurred again — that's the live structural backstop.

### DEFER-4 — slice-077 m7: archived `aped_1_battery.py::detect_stale_prunable` evidence misattribution split

- **Disposition**: DEFERRED — non-actionable per archive-immutability convention.
- **Rationale**: slice-077's `aped_1_battery.py` is in archived slice scaffolding (`architecture/slices/archive/slice-077-…/aped_1_battery.py`). The misattribution (path-missing filter vs prunable-flag filter producing observed-equals-expected for the wrong reason chain) is a slice-077-specific APED-1 case audit-trail; the underlying behavior in `tools/pulse_worktree_resolver._parse_worktree_porcelain` is correctly handled by the bare-repo Fix L in this slice. Splitting the archived APED-1 case file would alter the historical audit trail without behavioral consequence.
- **Captured class**: APED-1 case-split discipline — generic lesson logged in aggregated lessons. Future APED-1 batteries (in live slices) should split path-missing vs prunable-flag cases at authoring time (slice-079's own APED-1 cases for Fix L observe this discipline).

### DEFER-5 — slice-078 m4: archived design.md AC#1 `4 tests` claim stale vs actual 20 test functions

- **Disposition**: DEFERRED — non-actionable per archive-immutability convention.
- **Rationale**: slice-078 is archived; its design.md is a HISTORICAL record. The TF-1 plan grew from 18 → 20 mid-build (recorded in slice-078 build-log.md Design deviations section as Conformance class); the design.md count was not re-synced. Build-log.md's Conformance-deviation entry IS the audit trail — fixing design.md in-place would erase that. Per slice-060 Dim 9 design-meta TPHD-1 + PTFFD-1: design.md drift is out-of-scope for /code-review (the Critic acknowledged this in its m4 disposition).
- **Captured class**: TPHD-1 sub-mode (a) design.md-vs-realized-count drift — generic lesson; live structural backstop is the TF-1 plan + audit gate at /build-slice Step 6 for slice-079 itself.

## Authorization model for this slice

N/A — bundled cleanup; no auth/authz changes. No new user-input boundaries; no new subprocess shell-injection vectors; no new credential surfaces. All edits are pure refactors / prose tightenings / contract conformance.

## Error model for this slice

No new error codes. Behavior-preserving observability improvements only:

- **Fix F** (subprocess.run check=True → explicit returncode + stderr): test-suite debugging quality; no production error path.
- **Fix K** (UNKNOWN WARN-text generation): fulfills slice-077 design.md L181-191 contract. UNKNOWN remains an existing return state; new WARN strings are advisory text, not new error codes. Graceful degradation: `format_unknown_warn` returns a generic "unknown" template when reason key is not in `_UNKNOWN_REASON_WARN_TEMPLATES`.
- **Fix L** (bare-repo detection): `detect_active_worktrees` for bare-repo returns `tuple()` + WARN to stderr (existing observability path); does NOT raise.
- **Fix M** (BOM tolerance) + Fix N (`stage:` exact-key match): widen / tighten existing successful-parse paths; no new error code.
- **Fix P** (MISSING-FIELD sentinel): renames an existing sentinel; downstream filter behavior preserved.
- **Fix S** (cp1252 mojibake): silent corruption → silent correctness. No error code change; behavior change is byte-correct UTF-8 output.

## AC mapping to fixes

| AC | Source slice findings | In-scope fixes | DEFER-with-rationale |
|----|----------------------|----------------|---------------------|
| 1 (slice-074 m1-m5) | M1+m1+m2+m3+m4+m5 (6 findings; M1 is duplicate of P1.1) | Fix A (M1/P1.1), B (m1), C (m2), D (m3), E (m4), F (m5) | — |
| 2 (slice-075 m1-m2) | m1+m2 (2 findings) | Fix G (m1) | DEFER-1 (m2 archive-immutability) |
| 3 (slice-077 12 actionable findings + 1 positive observation m11 per /critique m4 ACCEPTED-FIXED) | M1+M2+m1-m10 (m11 is positive observation, NOT an actionable finding) | Fix H (M2), I (m3), J (m4), K (m5), L (m6), M (m8), N (m9) | DEFER-2 (M1 + m1 extraction-trigger), DEFER-3 (m2+m10 archive-immutability), DEFER-4 (m7 archive-immutability) |
| 4 (slice-078 m1-m5) | m1+m2+m3+m4+m5 (5 findings) | Fix O (m1), P (m2), Q (m3), R (m5) | DEFER-5 (m4 archive-immutability) |
| 5 (P1.1 + P3.10) | P1.1 (dup of slice-074 M1) + P3.10 | Fix A (P1.1 covered above); Fix S (P3.10 REFRAMED to structural-pin only per /critique B2+M3 ACCEPTED-FIXED — root-cause investigation deferred to a future slice-NNN `find-real-mojibake-source` candidate) | P3.10' mojibake-source investigation routed to source-pending-items for future slice |

Total: 19 in-scope fixes (A–S) + 6 DEFER entries (DEFER-1 through DEFER-5; DEFER-2 covers 2 findings) + 1 in-source-pending forward-reference (P3.10' root-cause). 24 actionable findings + 1 positive observation across the 4 source slices + 2 source-pending items.

## Test plan summary (no separate TF-1 plan — test-first not declared)

Test-first is `false` for this slice (per mission-brief frontmatter). Each fix gets at least one regression test per the canonical FAIL→PASS contrast pattern. Approximate plan (final test file naming + function naming locked at /build-slice Phase A):

| Fix | Regression test | FAIL→PASS contrast |
|-----|-----------------|---------------------|
| A (SKILL.md var-scope) | `test_build_slice_skill_branch_state_preamble.py::test_default_repo_root_wt_base_assigned_outside_numbered_codefences` | pre-fix: vars only inside point 1 codefence body → regex finds them inside `\n[1234]\. ` numbered block → assertion fails. post-fix: vars in shared pre-amble → assertion passes. |
| B (placeholder) | extend existing `test_build_slice_skill_dirty_tree_resolution.py` with `test_branch_state_no_bare_git_add` | pre-fix: prose contains `git add <scaffolding files>` placeholder → regex matches → assertion fails. post-fix: concrete pathspec → assertion passes. |
| C (cp-r exact-count) | tighten existing `test_cp_r_lines_use_if_then_guard_for_source_dir_absence` | pre-fix `>=2`-tolerant → adding a 5th cp-r line silently passes. post-fix `==4` → 5th line trips assertion. |
| D (regex docstring) | structural-pin test in `test_build_slice_skill_dirty_tree_resolution.py` asserts docstring substring | pre-fix: no docstring → assertion fails. post-fix: docstring present → assertion passes. |
| E (helper extraction) | `test_skill_parse_helpers.py::test_branch_state_section_returns_section_body` + `::test_helper_defined_only_once_in_test_corpus` | pre-fix: 2 definitions across 2 modules → corpus grep finds 2 → assertion fails. post-fix: 1 definition in shared helper → corpus grep finds 1 → assertion passes. |
| F (subprocess stderr) | structural-pin test in `test_r_20_retired.py` itself: `test_audit_failure_surfaces_stderr` runs the audit with a deliberately-broken arg + asserts stderr substring in the AssertionError message | pre-fix: `check=True` → CalledProcessError no stderr → assertion fails. post-fix: explicit stderr capture → stderr in failure message → assertion passes. |
| G (line-start anchor) | extend `test_commit_slice_skill_merge_wt_clean_preflight_ordering.py::test_wt_clean_preflight_preserves_silent_wt_discard_protection_intent` | pre-fix: `block.count("silent-WT-discard") == 2` (narration leakage) → tighter assertion fails. post-fix: line-start anchor → `count == 1` → assertion passes. |
| H (pytest.skip drop) | replace existing `test_cli_classify_json_returns_state_for_given_slice`'s pytest.skip branch + ADD `test_cli_classify_returns_error_on_unresolvable_default_branch` | pre-fix: synthetic repo on a fresh shell → pytest.skip silently → existing test passes by skip. post-fix: configured default → assertion runs on real output. plus new explicit test for stderr path. |
| I+J (unused imports) | `tests/methodology/test_pulse_tests_have_no_unused_imports.py::test_classify_worktree_state_imports` + sibling | pre-fix: `pytest` / `WorktreeStateClassification` imported but never used → AST walker finds unused → assertion fails. post-fix: clean. |
| K (UNKNOWN WARN-template constant — MAP-ONLY) | new `tests/skills/pulse/test_unknown_warn_templates.py::test_template_constant_covers_canonical_reasons` (parameterized over the 8 canonical `_UNKNOWN_REASONS` from `pulse_worktree_resolver.py:77-86` — `fresh-worktree-no-milestone` / `milestone-missing-in-active-and-archive` / `milestone-frontmatter-malformed` / `detached-head` / `dirty-worktree` / `merge-base-error` / `head-unresolvable` / `slice-folder-name-drift`) + `::test_constant_keys_are_byte_equal_to_unknown_reasons_tuple` (asserts `set(_UNKNOWN_REASON_WARN_TEMPLATES.keys()) == set(_UNKNOWN_REASONS)` — the byte-equal anchor) | pre-fix: constant does not exist → ImportError. post-fix: 8 canonical templates present + keys-equal-`_UNKNOWN_REASONS` invariant. |
| L (bare-repo) | new `tests/skills/pulse/test_detect_active_worktrees_bare_repo.py::test_bare_repo_returns_empty_tuple_with_warn` (synthetic `git init --bare` fixture) | pre-fix: `detect_active_worktrees` on bare-repo crashes or mis-classifies. post-fix: returns `tuple()` + WARN on stderr. |
| M (BOM) | new test in `test_classify_worktree_state.py::test_parse_milestone_stage_tolerates_utf8_bom` | pre-fix: milestone.md with BOM returns malformed-UNKNOWN. post-fix: parses correctly. |
| N (`stage:` exact-key) | new test `::test_parse_milestone_stage_rejects_stage_owner_key` | pre-fix: `stage_owner: foo` matches prefix → returns `foo`. post-fix: exact-key match → no match → returns None. |
| O (DRY winner/loser + pragma:no-cover branch) | new `tests/methodology/test_pcr_2a_audit_formatter_signature.py::test_winner_loser_passed_not_rederived` (mocks `diag.claim_history` differently than passed winner/loser; asserts audit-entry uses passed values) + `::test_unavailable_branch_rendered_when_winner_loser_none` (asserts pragma:no-cover branch fires when both args are None — returns audit-entry with `(unavailable)` placeholder) | pre-fix: rederives from claim_history → mocked-empty claim_history → audit shows None. post-fix: uses passed-in → audit shows passed values; defensive None-branch documented + tested. |
| P (MISSING-FIELD) | new `tests/methodology/test_pcr_2a_parse_queue_missing_field_sentinel.py::test_candidate_without_parallel_safety_line_returns_missing_field` | pre-fix: returns `"UNKNOWN-NO-GRAPH"`. post-fix: returns `"MISSING-FIELD"`. |
| Q (atomicity docstring) | structural-pin test asserts docstring contains `"Single-file scope"` + `"PCR-1's pending_writes"` substrings | pre-fix: docstring absent. post-fix: present. |
| R (`_VaultClaimDispatch` comment) | structural-pin test asserts file contains the canonical comment | pre-fix: absent. post-fix: present. |
| S (UTF-8 encoding structural-pin — REFRAMED per /critique B2+M3) | new `tests/methodology/test_slice_queue_writer_utf8_encoding.py::test_no_encoded_io_site_lacks_encoding_kwarg` (AST-walks `tools/slice_queue_writer.py` for every `Path.{read,write}_text`, `open(...)`, and `subprocess.run(..., text=True, ...)` call; asserts each carries `encoding="utf-8"` keyword arg) | pre-fix synthetic mutation: test-fixture stashes the module, deletes `encoding="utf-8"` from one site (e.g., L790 tmp_path.write_text), re-imports → AST walker flags the missing-encoding site → test FAILS. post-fix (canonical): all 9 sites carry the kwarg → test PASSES. Empirical FAIL→PASS contrast via fixture-mutation rather than codebase mutation (the codebase is already correct per APED-1 grep at /critique B2). |

Approximate count: 16 new/extended tests across 12-14 test files. Shippability catalog adds one row per fix cluster (~6-8 new rows).

## Shippability catalog impact

Per RPCD-1 / SCPD-1: every new audit rule MUST propagate consumer references into the shippability catalog. This slice introduces no NEW audit rules (all fixes are conformance to existing rules), but adds N=~6-8 new catalog rows pinning the regression tests. Exact row count + Machine-cmd content locked at /build-slice Phase A.

Catalog row shape per cluster:
- Row for SKILL.md build-slice prose fixes (A+B+C+D+E): `pytest tests/methodology/test_build_slice_skill_*.py + tests/methodology/test_skill_parse_helpers.py`
- Row for SKILL.md commit-slice prose fix (G): `pytest tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py`
- Row for pulse helper fixes (H+I+J+K+L+M+N): `pytest tests/skills/pulse/ + tests/methodology/test_pulse_tests_have_no_unused_imports.py + tests/skills/pulse/test_unknown_warn_templates.py`
- Row for PCR-2a fixes (O+P+Q+R): `pytest tests/methodology/test_pcr_2a_audit_formatter_signature.py + test_pcr_2a_parse_queue_missing_field_sentinel.py + structural-pin tests`
- Row for cp1252 (S): `pytest tests/methodology/test_slice_queue_writer_utf8_encoding.py`
- Row for `_skill_parse_helpers.py` itself: `pytest tests/methodology/test_skill_parse_helpers.py`

## Audit gates expected CLEAN at /build-slice Step 6

- **PCA-1**: chain wiring clean — slice-079 mission-brief + design hand off to /critique → /critique-review → /build-slice → /code-review → /validate-slice → /reflect.
- **PMI-1**: no plugin.yaml change (in-place SKILL.md / tools/ edits — no new skill / agent / tool files; `_skill_parse_helpers.py` is a test helper, not in plugin.yaml inventory per INST-1 convention). VERSION unchanged at 0.74.0.
- **INST-1**: canonical inventory unchanged (no new skill / agent / tool added).
- **CAD-1**: critique.md byte-equality preserved (already verified clean post-clause-5 application 2026-05-29).
- **OSDG-1**: forward-sync any `skills/build-slice/SKILL.md` + `skills/pulse/SKILL.md` edits to installed copies in lock-step at /build-slice Phase F.
- **MCFS-1**: no methodology-changelog edit (MEPD-1 EXCLUDE per slice-040/043/045/057/071 precedent).
- **AVFS-1 / PVFS-1 / TVFS-1**: VERSION unchanged → installed VERSION / pyproject.toml / venv reinstall all preserve current 0.74.0.
- **TF-1**: not enabled (Test-first false in mission-brief frontmatter).
- **WS-1**: not enabled.
- **ETC-1**: not enabled.
- **WIRE-1**: 1 new module entry (`_skill_parse_helpers.py` with consumer + test; see Wiring matrix above).
- **BC-1**: no new build-checks rule promotion. BC-GLOBAL-2 prose-vs-automation regression watched (slice-074 reflection N=7 cumulative; recorded in critic-calibration-log as routed-out per `tools/build_checks.py` negative-anchor filtering candidate).
- **STP-1**: no R-NN status flip without a paired test contradicting; this slice has no risk-register transitions.
- **RR-1**: no risk-register edit (no R-NN retired / opened).
- **NAW-1**: no new agent file; warning audit clean.
- **BRANCH-2**: slice runs in worktree at `C:\Users\sshub\ai_sdlc-wt\slice-079-bundle-074-075-077-078-code-critic-cleanup` on branch `slice/079-bundle-074-075-077-078-code-critic-cleanup`. Worktree-mode discipline at Step 6.
- **PTFCD-1 / PTFFD-1**: all cited test paths/functions resolve at slice end.
- **SCMD-1 / SRSC-1**: shippability catalog new rows follow grammar; Step 5.5 catalog runner exits 0.
- **EOL-DRIFT-1**: skill-drift comparators continue to normalize CRLF↔LF; in-repo↔installed `skills/*/SKILL.md` content-equal modulo EOL.
- **BCI-1**: build-checks integrity gate unchanged.
- **UTF8-STDOUT-1**: explicit UTF-8 in `tools/slice_queue_writer.py` (Fix S) brings the helper into compliance.
- **CSP-1**: cross-spec parity preserved (Fix O extends `_format_vault_claim_audit_entry`'s signature — same-slice consistent update across resolver + audit-formatter; no orphaned consumer).
- **CRP-1 / TPHD-1 (cross-spec propagation)**: any prose edits propagated in-repo + installed in lock-step.
- **MEPD-1**: EXCLUDE; (b) discharged-by-name per §"Decisions made (ADRs)" above.

## Dependencies graph snapshot (for /critique reviewer context)

- slice-074 → slice-079 (M1 / m1-m5 fixes)
- slice-075 → slice-079 (m1 fix; m2 DEFERRED per archive-immutability)
- slice-077 → slice-079 (M2 / m3-m6+m8+m9 fixes; M1+m1 DEFERRED to parallel-slice-family-parity-audit; m2+m7+m10 DEFERRED per archive-immutability)
- slice-078 → slice-079 (m1-m3+m5 fixes; m4 DEFERRED per archive-immutability)
- source-pending-items.txt P1.1 → covered by Fix A; P3.10 → covered by Fix S
- /critic-calibrate Proposal 1 (2026-05-29) APED-1 clause-5 applied → slice-079 is the N+1 first-governed-slice; /critique pass will be the first to operate under the extended discipline.
