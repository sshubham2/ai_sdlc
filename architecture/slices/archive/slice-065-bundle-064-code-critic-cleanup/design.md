# Design: Slice 065 bundle-064-code-critic-cleanup

**Date**: 2026-05-23
**Mode**: Standard (thin vault)

## What's new

- Programmatic STOP guard in `skills/code-review/SKILL.md` Step 1 bash block (lines L40-L42) — replaces silent fall-through to `git merge-base "" HEAD` with `exit 2` + stderr error when both default-branch resolvers return empty.
- One new test function `test_skill_md_step_1_default_branch_resolver_stops_on_empty` in existing `tests/skills/code_review/test_code_review_skill.py`.
- Two assertion tightenings inside existing test functions in the same test file:
  - `test_skill_md_step_1_diff_resolution_uses_union_of_three_sources` (Source-(iii) substring-leak fix)
  - `test_skill_md_step_1_all_three_legs_share_filter_shape` (semantic-invariant count assertion fix)
- Shippability catalog row #65.

## What's reused

- [[architecture/slices/archive/slice-064-fix-code-review-diff-resolution-falsifier/code-review.md]] — source of the M1 / m1 / m2 advisory findings being closed (cited at AC level via mission-brief Dependencies)
- [[architecture/slices/archive/slice-064-fix-code-review-diff-resolution-falsifier/reflection.md]] §Deferred (a)(b)(c) — slice-065+ bundled cleanup nomination
- [[architecture/decisions/ADR-061-mint-naw-1-new-agent-warning.md]] — canonical Python implementation of the STOP behavior at `tools/new_agent_warning_audit.py:_resolve_default_branch` (the three-step resolver pattern: `git symbolic-ref refs/remotes/origin/HEAD` → `git config init.defaultBranch` → fail-fast with `exit 2` + `default-branch-unresolvable` stderr; this slice mirrors that exact pattern into the SKILL.md bash surface — see ADR-061 §Decision for the rationale)
- [[architecture/decisions/ADR-062-extend-naw-1-pattern-to-code-review.md]] — the union-of-three-sources mechanism being hardened (no supersession; ADR-062 stays accepted, slice-065 only extends with the L40-L42 STOP guard left out of slice-064's scope)
- `skills/code-review/SKILL.md` — Step 1 bash block at L40-L42 (default-branch resolver chain) and L67-L69 (documented `default-branch-unresolvable` error case prose — the bash now matches what the prose has always promised)
- `tests/skills/code_review/test_code_review_skill.py` — `_read()` helper at L37, section-scope idiom (`step_1_idx = body.find("### Step 1: …")` + `step_2_idx = body.find("### Step 2:", step_1_idx)`) at L111-L121 (reused unchanged for the new test function)
- `tests/methodology/test_code_review_skill_drift.py::test_in_repo_and_installed_code_review_skill_md_are_content_equal` — OSDG-1 drift guard (re-runs unchanged after this slice's SKILL.md edit + installed-side forward-sync)
- `tools/shippability_runner.py` + `architecture/shippability.md` — row #65 propagation

## Components touched

### `skills/code-review/SKILL.md` (modified)

- **Responsibility**: Orchestrator prose for the `/code-review` in-loop adversarial code-Critic step (CRSI-1; ADR-059). Step 1 resolves the slice's filtered code diff via the union-of-three-sources read mechanism (ADR-062 / slice-064).
- **Lives at**: `skills/code-review/SKILL.md` (lines L40-L42 — default-branch resolver chain only; rest of file untouched)
- **Key interactions**: Read by Claude at `/build-slice` Step 6 → `/code-review` auto-advance per PCA-1. Bash block executed by Claude interactively (not by a downstream pipeline). Drift-guarded by `tests/methodology/test_code_review_skill_drift.py` (OSDG-1).
- **What changes**: insert `[ -z "$default" ] && { echo "default-branch-unresolvable: neither origin/HEAD nor init.defaultBranch resolved" >&2; exit 2; }` between current L41 (the second-resolver fallback `[ -z "$default" ] && default=$(git config init.defaultBranch …)`) and current L42 (`base=$(git merge-base "$default" HEAD)`) — i.e., AFTER both resolver attempts, BEFORE the `git merge-base` call. Pre-fix flow: silent fall-through to `git merge-base "" HEAD` → cryptic git error or undefined behavior. Post-fix flow: explicit non-zero exit + stderr message matching the L67-L69 documented `default-branch-unresolvable` error-case prose (the bash now enforces what the prose has always promised).

### `tests/skills/code_review/test_code_review_skill.py` (modified)

- **Responsibility**: Pin /code-review SKILL.md structural invariants (slice-060 CRSI-1 + slice-064 union-of-three-sources + slice-065 STOP guard).
- **Lives at**: `tests/skills/code_review/test_code_review_skill.py` (lines L142, L166 modified; new function appended after L209 inside the same `test_skill_md_step_1_all_three_legs_share_filter_shape` neighborhood, before `test_skill_md_step_1_union_aggregation_prose_pinned` at L212)
- **Key interactions**: pytest-collected; runs at `/build-slice` Step 6 + full methodology suite; `_read()` helper at L37 reused for SKILL.md file load; `_resolve_slice_dir(60)` helper at L31 not affected by this slice.
- **What changes**:

  **Canonical bash-block scoping idiom** (used by all three changes below to retire the M1 substring-leak class — slice-040 N+1 doctrine catch by /critique B1+B2):

  ```python
  step_1_idx = body.find("### Step 1: Resolve the slice's code diff")
  step_2_idx = body.find("### Step 2:", step_1_idx)
  step_1 = body[step_1_idx:step_2_idx]
  bash_start = step_1.find("```bash\n")
  bash_end = step_1.find("\n```", bash_start)
  assert bash_start >= 0 and bash_end > bash_start, (
      "skills/code-review/SKILL.md Step 1 missing ```bash-fenced block — "
      "bash-block scoping cannot bound"
  )
  bash_block = step_1[bash_start:bash_end]
  ```

  This `bash_block` slice excludes the L37 preamble prose (which contains the unflagged `git diff "$base"...HEAD` substring), the L54-L56 post-bash union-instruction prose, AND the L67-L69 documented error-case prose (which contains the `default-branch-unresolvable` literal). Assertions scoped to `bash_block` cannot be satisfied by adjacent prose — empirically verified by Critic B1+B2 against the current SKILL.md.

  1. **L142 assertion tightening** (AC#1 — M1 substring-leak retirement) — currently `assert 'git diff "$base"...HEAD' in step_1` matches both the L37 preamble prose AND the L51 bash line; tightened to scope to `bash_block` (above) AND assert against the full filter-shape literal: `assert 'git diff "$base"...HEAD --name-only --diff-filter=ACMR' in bash_block`. Double-redundant tightening (scoping alone retires the leak; the flag-tail addition catches a future regression where the filter flags are dropped from the L51 leg). Re-verified empirically against current SKILL.md: only the L51 bash command carries this literal.

  2. **L166 assertion tightening** (AC#2 — m2 forward-looking count gap retirement) — currently `assert diff_with_filter >= 2` admits a 3-leg / 2-filtered regression. Tightened to a semantic invariant scoped to `bash_block` (above): `assert diff_with_filter == bash_block.count('git diff "$base"')`. Empirically verified on current SKILL.md: `bash_block.count("--name-only --diff-filter=ACMR")` = 2 (L45 + L51), `bash_block.count('git diff "$base"')` = 2 (L45 + L51), so 2 == 2 PASS. The Critic-flagged `step_1.count('git diff "$base"')` = 3 (which included L37 preamble) is retired by the `bash_block` scoping. Diagnostic message surfaces both observed values.

  3. **New function `test_skill_md_step_1_default_branch_resolver_stops_on_empty`** (AC#3 + AC#4 — m1/exit-2 STOP-guard pin) — structural pin asserting the SKILL.md Step 1 bash block contains the STOP guard. Scoped to `bash_block` (above). Three composable assertions per Critic B2 proposed-fix (1)+(2)+(3):

     - **Count-based pin** (the STOP guard is ADDITIVE to the existing fallback-resolver `[ -z "$default" ]` at L41):
       ```python
       guard_count = bash_block.count('[ -z "$default" ]')
       assert guard_count >= 2, (
           f"skills/code-review/SKILL.md Step 1 bash block must carry the "
           f"STOP guard `[ -z \"$default\" ] && {{ ... exit 2; }}` AFTER the "
           f"second resolver — observed {guard_count} `[ -z \"$default\" ]` "
           f"occurrences in the bash block, expected >= 2 (one for the "
           f"second-resolver fallback, one for the new STOP guard)"
       )
       ```
       Distinguishes pre-fix (count == 1) from post-fix (count == 2).

     - **Canonical brace-group form** (NAW-1 parity per ADR-061; per /critique m2 — pins the canonical shape, prevents `if`/`fi`-style refactor regression):
       ```python
       assert '&& { echo "default-branch-unresolvable' in bash_block, (
           "skills/code-review/SKILL.md Step 1 bash block missing the "
           "canonical STOP-guard brace-group form `&& { echo "
           "\"default-branch-unresolvable…\" >&2; exit 2; }` mirroring "
           "NAW-1's exit-2 contract (ADR-061 §Decision)"
       )
       assert "exit 2" in bash_block, (
           "skills/code-review/SKILL.md Step 1 bash block missing `exit 2` — "
           "the STOP guard must propagate the exit-2 contract from NAW-1 "
           "(ADR-061 §Decision)"
       )
       ```

     - **Structural co-location** (STOP guard between second-resolver and `git merge-base`, per Critic B2 proposed-fix (3)):
       ```python
       fallback_idx = bash_block.find("git config init.defaultBranch")
       merge_base_idx = bash_block.find("git merge-base")
       stop_idx = bash_block.find('[ -z "$default" ] && {')
       assert fallback_idx < stop_idx < merge_base_idx, (
           f"skills/code-review/SKILL.md Step 1 bash block STOP guard not "
           f"structurally co-located between second-resolver fallback "
           f"(idx={fallback_idx}) and git merge-base (idx={merge_base_idx}); "
           f"observed stop_idx={stop_idx}"
       )
       ```
       Pins the structural relationship the AC actually wants, not just substring existence.

     Both the L41 second-resolver fallback `[ -z "$default" ]` literal and the L68 `default-branch-unresolvable` prose literal already exist pre-fix; the new bash-block scoping + count discipline + co-location pin distinguishes structural presence of the new STOP guard from accidental sibling matches in adjacent prose (per Critic B2 — empirically verified false on the current pre-fix SKILL.md before scoping).

## Contracts added or changed

None. This slice modifies an existing SKILL.md surface (`/code-review`) without changing its inputs (mission-brief.md + design.md + new-ADRs paths) or outputs (`code-review.md` artifact + auto-advance to `/validate-slice`). The only behavioral change is fail-fast on a previously-undefined-behavior corner case (clean-room repo with no `origin/HEAD` + no `init.defaultBranch`).

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1**. This slice introduces zero new modules — only an in-place SKILL.md bash edit + a new test function inside an existing test file. The new test function `test_skill_md_step_1_default_branch_resolver_stops_on_empty` is auto-collected by pytest discovery on the existing file (no consumer-wiring required — pytest IS its consumer entry point).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(Zero-row matrix — WIRE-1 audit treats as clean per design-slice template guidance.)

## Decisions made (ADRs)

**None.** Voluntary-restraint precedent (slice-037 / slice-046 / slice-050 / slice-052 / slice-055 / slice-056 / slice-057 / slice-061 — N≥8 cumulative on quality-tightening + bug-fix-without-new-mechanism classes; slice-061 R-16 born-retired INSTALL.md prose-correctness precedent applies):

- Slice mints no new RULE-ID
- Slice adds no user-facing skill capability
- Slice extends no drift-guard family (no new tool; reuses existing OSDG-1 + test_code_review_skill.py structural-pin family)
- Slice promotes no BC project
- Slice is a bug fix on a slice-064-introduced bash block plus two assertion tightenings on slice-064-introduced tests

The STOP-behavior change is mechanically equivalent to the canonical NAW-1 Python implementation at `tools/new_agent_warning_audit.py:_resolve_default_branch` (slice-063 / ADR-061 §Decision — the three-step resolver pattern: `git symbolic-ref refs/remotes/origin/HEAD` → `git config init.defaultBranch` → `None` → caller maps to `exit 2` + `_USAGE_DEFAULT_BRANCH_UNRESOLVABLE` stderr) — slice-065 only mirrors the established pattern onto the SKILL.md bash surface; no new architectural decision needs locking. The `[ -z "$default" ] && { echo "default-branch-unresolvable: …" >&2; exit 2; }` brace-group guard inherits ADR-061's reasoning by reference (per /critique m3 — semantic content inlined, not just line-number coordinates).

## Inclusion-heuristic disposition

Per **BC-PROJ-10** (`methodology-changelog.md` v0.61.0 — explicit Inclusion-heuristic classification required before /critique for any slice minting a new ADR / adding a user-facing skill capability / etc.).

**Disposition: NO methodology-changelog entry, NO VERSION bump, NO new ADR.**

**Why-none justification** (vs. the real META-1 enforcing-assertion at `tests/methodology/test_methodology_changelog.py:136` — `re.split(r"^## v\S+ — …")` checks ordering + presence; the METHODOLOGY-EVENT-PROMOTION-DOCTRINE-1 (MEPD-1) discharged-by-name verification):

- **NO new RULE-ID minted** — the STOP guard is a small bash correctness fix mirroring the established NAW-1 Python pattern at `tools/new_agent_warning_audit.py:_resolve_default_branch` (the canonical three-step resolver: `git symbolic-ref` → `git config init.defaultBranch` → return `None` → caller maps to `exit 2` + `_USAGE_DEFAULT_BRANCH_UNRESOLVABLE` stderr per ADR-061 §Decision). The bash insertion at `skills/code-review/SKILL.md` L41-L42 is a literal byte-for-byte translation of that Python contract: `[ -z "$default" ] && { echo "default-branch-unresolvable: …" >&2; exit 2; }`. No new architectural rule; no new gate; no new audit tool. The methodology-discoverability axis is already covered by ADR-061's documented STOP semantics.
- **NO user-facing skill capability added** — `/code-review`'s surface (inputs, outputs, auto-advance edge) is unchanged. The bash fail-fast is a corner-case bug fix that today never triggers in the dev environment (clean-room repo without `origin/HEAD` AND without `init.defaultBranch` configured).
- **NO drift-guard family extension** — no new tool. The new `test_skill_md_step_1_default_branch_resolver_stops_on_empty` is a sibling structural pin inside the existing slice-060/slice-064 `test_code_review_skill.py` family; the test family was established at slice-060 (CRSI-1) and extended at slice-064. Adding a sibling structural-pin function is the standard within-family operation, not a family-extension event (per slice-049/050/051/057/058 N≥5 precedent that drift-guard family extension specifically = NEW MEMBER FILE / NEW TOOL, not new test functions in an existing member).
- **NO BC project promotion** — no new BC project signal; no within-class N=2 promotion event.
- **External-contract scope check** (per /critique M3 — the AC#3 change DOES alter `/code-review`'s failure mode in the clean-room corner case from undefined behavior (exit 128 from `git merge-base "" HEAD` + cryptic stderr) to deterministic behavior (exit 2 + `default-branch-unresolvable` stderr). This is a tightening, not a widening or breaking change: pre-fix behavior was undefined, so no consumer can legitimately depend on it. Verified via `grep -rn "merge-base \"\"" .` across the repo: zero consumer call sites depend on the pre-fix undefined behavior. The new contract is mechanically the same as NAW-1's existing exit-2 contract — already widely understood per ADR-061 §Decision.
- **Class precedent (corrected per /critique M3)**: the strongest precedent is slice-064 / ADR-062 itself — which extended the union-of-three-sources mechanism from NAW-1's audit-tool surface to `/code-review`'s SKILL.md surface WITHOUT minting a new RULE-ID (ADR-062 "mints no new rule, supersedes nothing — sibling-surface application of NAW-1's pattern"). Slice-065 is the next in-family extension on the same SKILL.md surface, going one level deeper: ADR-062 mirrored NAW-1's union-of-three-sources read mechanism into SKILL.md bash; slice-065 mirrors ADR-061's exit-2 fail-fast STOP-guard contract into the same SKILL.md bash surface. Same in-family pattern, smaller scope. ADR-061 §Decision + ADR-062 §Decision are the load-bearing references; slice-061 R-16 INSTALL.md prose-correctness precedent is dropped (too weak — that class did not alter a methodology-executable contract). The slice-064 reflection's own categorization of the 3 advisories as *"single-slice test-tightness defects on the slice-064-introduced test surface … task-list items, not risk-register entries (no class signal)"* corroborates the no-bump disposition.

If /critique disputes this disposition: per BC-PROJ-10 the Critic may surface this as a finding; the Builder then either (i) escalates to mint an ADR / changelog entry / VERSION bump, or (ii) provides additional Why-none reasoning. The dispute path is explicit, not silent.

## Authorization model for this slice

N/A — `/code-review` SKILL.md is methodology surface, not user-facing or auth-bound. Bash block runs in Claude's interactive shell at slice author's machine; no privilege boundary crossed.

## Error model for this slice

Pre-fix flow (current SKILL.md L40-L42 + L67-L69 prose):
- Bash silently falls through to `git merge-base "" HEAD` when both default-branch resolvers return empty
- `git merge-base ""` errors with exit 128 + cryptic stderr; or returns garbage; bash continues to `git diff "$base"` with `$base` unset
- L67-L69 prose says "STOP with the BRANCH-1-shaped error and instruct user to re-run after default branch resolves" but the bash does NOT enforce this
- Net: Claude sees cryptic bash failures and either retries or surfaces an unhelpful error to the user

Post-fix flow:
- Bash exits 2 with stderr `default-branch-unresolvable: neither origin/HEAD nor init.defaultBranch resolved`
- Claude reads the SKILL.md prose obligation at L67-L69 AND sees the explicit exit-code; writes a clean error to `code-review.md` (or surfaces a structured-options STOP to the user) per the existing L67-L69 error-case prose
- Net: the documented error case is now executed by the bash, not merely promised by the prose

New error code introduced: bash exit code `2` from Step 1 default-branch-unresolvable path. (Exit code 2 was chosen for parity with the conventional "command misuse / setup error" range distinct from `0`/`1` test-failure semantics; matches the NAW-1 Python `ValueError` semantics → bash propagation.)

## Build phases (for /build-slice)

The slice MUST be executed in this phase order to satisfy TF-1 (test-first) + mid-slice-smoke gate semantics:

- **Phase A — Test-first authoring (new failing test + two assertion tightenings)**
  - A1: Tighten `test_skill_md_step_1_diff_resolution_uses_union_of_three_sources` Source-(iii) assertion at L142 to full filter-shape literal. Re-run the test → MUST still PASS (the current SKILL.md L51 bash command carries the full filter shape; the tightening removes the substring-leak class without breaking the currently-passing assertion).
  - A2: Tighten `test_skill_md_step_1_all_three_legs_share_filter_shape` count assertion at L166 to bash-block-scoped semantic invariant `diff_with_filter == bash_block.count('git diff "$base"')` (per /critique B1 — `step_1`-scoped form would evaluate 2 != 3 and FAIL because L37 preamble leaks into the RHS; `bash_block`-scoped form PASSes 2 == 2 on current SKILL.md). Re-run the test → MUST still PASS.
  - A3: Author new test function `test_skill_md_step_1_default_branch_resolver_stops_on_empty` after L209 (before the existing `test_skill_md_step_1_union_aggregation_prose_pinned` at L212) — using the canonical bash-block scoping idiom (per /critique B2 — section-scoped substrings `'[ -z "$default" ]' in step_1` and `'default-branch-unresolvable' in step_1` are already True pre-fix via L41 fallback resolver + L68 documented-error-case prose; only the bash-block-scoped count + brace-group + co-location assertions actually distinguish pre-fix from post-fix). Re-run → MUST FAIL (WRITTEN-FAILING) — specifically, `bash_block.count('[ -z "$default" ]')` = 1 (only the L41 fallback) AND `'exit 2' in bash_block` is False AND `'&& { echo "default-branch-unresolvable' in bash_block` is False until AC#3 SKILL.md fix lands.

- **Phase B — Mid-slice smoke gate**
  - Run the full slice-065 test set: `$PY -m pytest tests/skills/code_review/test_code_review_skill.py -v --no-header`
  - Expected: AC#1/AC#2 PASS; AC#4 FAIL (WRITTEN-FAILING); all pre-existing slice-060 + slice-064 tests PASS.
  - If anything deviates: STOP, diagnose, do not continue.

- **Phase C — Fix (SKILL.md STOP guard)**
  - Edit `skills/code-review/SKILL.md` L40-L42 to insert the `[ -z "$default" ] && { echo "default-branch-unresolvable: neither origin/HEAD nor init.defaultBranch resolved" >&2; exit 2; }` line between current L41 and L42 (after both resolver attempts, before `git merge-base`).
  - Re-run the slice-065 test set → AC#4 flips FAIL → PASS.

- **Phase D — Installed-side forward-sync (OSDG-1)**
  - `cp skills/code-review/SKILL.md ~/.claude/skills/code-review/SKILL.md` (or the platform-equivalent PowerShell `Copy-Item`).
  - Run `$PY -m pytest tests/methodology/test_code_review_skill_drift.py` → MUST PASS (OSDG-1 EOL-DRIFT-1 EOL-agnostic content-equal).

- **Phase E — Shippability row + pre-finish gate**
  - Append row #65 to `architecture/shippability.md` (see "Shippability row #65 shape" below).
  - Run `$PY -m tools.shippability_runner` → MUST exit 0 with `65/65 PASS`.
  - Run `$PY -m tools.test_first_audit architecture/slices/slice-065-bundle-064-code-critic-cleanup/mission-brief.md --strict-pre-finish` → MUST exit 0 (all 6 TF-1 rows PASSING).
  - Run the full Step 6 audit sweep (BC-1, RR-1, CAD-1, PMI-1, DR-1, TF-1, WS-1 N/A, WIRE-1, ETC-1 N/A, CSP-1, SUP-1, LINT-MOCK-1/2/3, PVFS-1, AVFS-1, MCFS-1, TVFS-1, NAW-1, OSDG-1, mini-CAD, pipeline-chain-audit, branch-workflow-audit, plugin-manifest-audit, install-audit, utf8-stdout-audit, supersede-audit, /drift-check) → MUST all exit 0.
  - Run `/code-review` self-dogfood on slice-065 (the in-loop CRSI-1 walking-skeleton v1 step) → MUST produce `architecture/slices/slice-065-bundle-064-code-critic-cleanup/code-review.md` with no NEW Blockers on the L40-L42 region.
  - Full pytest suite: MUST ≥ 898/898 PASS (slice-064 baseline + 1 net new test function = 899 expected; tolerance for any test count drift acknowledged at /validate-slice).

## Shippability row #65 shape

Per the mission brief must-not-defer #4 (BCR-1-traceability axis per slice-054 precedent — even though this is NOT a BCR-1 round-trip):

| Row | Description | Command | Expected |
|-----|-------------|---------|----------|
| 65 | slice-065-bundle-064-code-critic-cleanup; closes slice-064 code-Critic advisories (M1 substring-leak fix on `test_skill_md_step_1_diff_resolution_uses_union_of_three_sources` Source-(iii) assertion + m1 default-branch resolver STOP guard on `skills/code-review/SKILL.md` L40-L42 + m2 semantic-invariant tightening on `test_skill_md_step_1_all_three_legs_share_filter_shape` count assertion) + adds new structural pin `test_skill_md_step_1_default_branch_resolver_stops_on_empty` (AC#4 — bash-block-scoped count + brace-group + co-location, per /critique B2 fix + /critique-review m-add-1 narrative-manifest parity restoration) | `$PY -m pytest tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_diff_resolution_uses_union_of_three_sources tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_all_three_legs_share_filter_shape tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_default_branch_resolver_stops_on_empty` | exit 0 |

The Description cell cites both `slice-065` AND the closed slice-064 advisory IDs (M1 / m1 / m2) — preserves the BCR-1-traceability axis discipline (slice-054 M-add-1 → slice-056 row-#56 → slice-057 row-#57 precedent applied analogously to advisory-driven slices).

## Validation strategy

Per-AC verification mapping is in the mission brief §Verification plan. Phase E's pre-finish gate is the structural backstop; the slice does not introduce new exploratory-charter rows (mission brief `**Exploratory-charter**: false`) or walking-skeleton layers (mission brief `**Walking-skeleton**: false`).

The mid-slice smoke gate (Phase B) is the critical mid-build checkpoint — it confirms the test-first authoring is internally consistent (AC#1/AC#2 tightenings did not break the currently-passing tests; AC#4 is properly WRITTEN-FAILING and would flip when the SKILL.md fix lands). A premature PASS on AC#4 at Phase B would indicate the test is not actually pinning the STOP guard (false-positive class — the test asserts something already present in SKILL.md prose).

## Out of scope (reiterated from mission brief)

- /code-review v2 enhancements (TRI-1 routing + verdict-driven block + AI-bloat passes) — slice-066+
- SC-007 /drift-check enforcement
- R-17 BRANCH-1 clean-tree precondition codification
- R-13 OSDG-1 extension to /slice-candidates
- Multi-session / parallel-slice / worktree-per-slice execution
- New RULE-ID / ADR / methodology-changelog entry / VERSION bump (per Inclusion-heuristic disposition above)
- Refactor of the existing `_resolve_slice_dir(N)` helper or its corpus class-closure backstop (slice-056/057/062 surfaces — orthogonal to this slice)

## Pipeline position

- **predecessor**: `/slice`
- **successor**: `/critique`
- **auto-advance**: true
- **on-clean-completion**: design.md written + zero new ADRs (per Inclusion-heuristic disposition) + milestone.md updated → invoke `/critique` via the Skill tool. `critic-required: true` (touches `skills/code-review/SKILL.md` methodology surface — always-mandatory trigger).
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - None at /design-slice — the mission brief was clear; no Step 2 clarifying questions raised.

> Per PCA-1 (methodology-changelog.md v0.41.0).
