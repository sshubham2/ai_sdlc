# Slice 065: bundle-064-code-critic-cleanup

**Mode**: Standard
**Estimated work**: 0.5 day (~3 hours)
**Risk retired**: slice-064 code-Critic advisory bundle (3 findings — M1 substring-leak + m1 default-branch resolver no-programmatic-STOP + m2 `>= 2` count assertion forward-looking gap; slice-064 reflection L-Deferred "slice-065+ bundled cleanup nomination")
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Close the three slice-064 `/code-review` advisory findings as a bundled cleanup: tighten two slice-064-introduced test assertions to remove the substring-leak + forward-looking count gap, and add programmatic STOP behavior to the `skills/code-review/SKILL.md` Step 1 default-branch resolver chain (currently silently falls through to `git merge-base "" HEAD` when both resolvers return empty — a CI clean-room corner case). This closes the slice-064 reflection's "slice-065+ bundled cleanup nomination" and the CRSI-1 v1 advisory feedback loop. NOT a BCR-1 round-trip (zero `**Closes:** SC-NNN` sentinels — slice-064 advisory-driven, not backlog-driven).

## Acceptance criteria

1. `tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_diff_resolution_uses_union_of_three_sources` Source-(iii) assertion is tightened to scope to the SKILL.md Step 1 ` ```bash `-fenced block ONLY (not the full section) — substring `'git diff "$base"...HEAD'` matching the preamble prose at L37 is no longer sufficient; deleting the L51 bash command would cause the assertion to FAIL. Realized as `'git diff "$base"...HEAD --name-only --diff-filter=ACMR' in bash_block` (full filter-shape literal; only matches L51 bash command — double-redundant with bash-block scoping).
2. `tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_all_three_legs_share_filter_shape` `>= 2` filter-shape count assertion is tightened to a semantic invariant scoped to the SKILL.md Step 1 ` ```bash `-fenced block: `bash_block.count("--name-only --diff-filter=ACMR") == bash_block.count('git diff "$base"')`. Per /critique B1 — `step_1`-scoped form would FAIL today (2 != 3, L37 preamble leaks into the RHS); `bash_block`-scoped form PASSes (2 == 2) AND admits no 3-leg / 2-filtered regression.
3. `skills/code-review/SKILL.md` Step 1 bash block at L40-L42 fails fast with `exit 2` and a `default-branch-unresolvable: …` stderr message (mirroring NAW-1's ADR-061 §Decision exit-2 contract) when both default-branch resolvers (`git symbolic-ref refs/remotes/origin/HEAD` AND `git config init.defaultBranch`) return empty — replaces the current silent fall-through to `git merge-base "" HEAD`. Exact insertion shape: `[ -z "$default" ] && { echo "default-branch-unresolvable: neither origin/HEAD nor init.defaultBranch resolved" >&2; exit 2; }` between L41 (second-resolver fallback) and L42 (`git merge-base`).
4. New structural test `tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_default_branch_resolver_stops_on_empty` pins AC#3 — scoped to the SKILL.md Step 1 ` ```bash `-fenced block, asserts (a) `bash_block.count('[ -z "$default" ]') >= 2` (the additive STOP-guard pin — distinguishes pre-fix count=1 from post-fix count=2; per /critique B2 — section-scoped `'[ -z "$default" ]' in step_1` form was already TRUE pre-fix via L41 fallback resolver), (b) `'&& { echo "default-branch-unresolvable' in bash_block` + `'exit 2' in bash_block` (canonical NAW-1 brace-group form per /critique m2), and (c) structural co-location `fallback_idx < stop_idx < merge_base_idx` within the bash block (per /critique B2 proposed-fix (3) — pins the structural relationship, not just substring existence).
5. OSDG-1 drift clean on `skills/code-review/SKILL.md` after forward-sync; `/code-review` self-dogfood passes on slice-065 (regression check vs. slice-064 union-of-three-sources fix); shippability runner 65/65 PASS with new row #65.

## Test-first plan

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING -> PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | structural-tightening | tests/skills/code_review/test_code_review_skill.py | test_skill_md_step_1_diff_resolution_uses_union_of_three_sources | PASSING |
| 2 | structural-tightening | tests/skills/code_review/test_code_review_skill.py | test_skill_md_step_1_all_three_legs_share_filter_shape | PASSING |
| 3 | structural | tests/skills/code_review/test_code_review_skill.py | test_skill_md_step_1_default_branch_resolver_stops_on_empty | PASSING |
| 4 | structural | tests/skills/code_review/test_code_review_skill.py | test_skill_md_step_1_default_branch_resolver_stops_on_empty | PASSING |
| 5 | drift-guard | tests/methodology/test_code_review_skill_drift.py | test_in_repo_and_installed_code_review_skill_md_are_content_equal | PASSING |
| 5 | shippability | tests/methodology/test_shippability_runner_execution.py | test_main_returns_0_on_all_pass | PASSING |

> Note for /design-slice: AC#3 and AC#4 share the same test function (`test_skill_md_step_1_default_branch_resolver_stops_on_empty`) — AC#3 is the SKILL.md code change; AC#4 is the structural pin. TF-1 multi-row-per-AC pattern per slice-056/062 precedent.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Substring-leak retired (bash-block scoped) | `$PY -m pytest tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_diff_resolution_uses_union_of_three_sources` exits 0 on current SKILL.md; mutation check: replace `git diff "$base"...HEAD` bash line at SKILL.md L51 with a no-op `: # placeholder` line → assertion FAILS (bash_block no longer carries the full filter-shape literal `git diff "$base"...HEAD --name-only --diff-filter=ACMR`; L37 preamble alone is insufficient since it lacks the flag tail AND is outside `bash_block`) → revert |
| 2 | Count-assertion tightening (bash-block scoped semantic invariant) | `$PY -m pytest tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_all_three_legs_share_filter_shape` exits 0 on current SKILL.md (2 == 2 inside `bash_block`); mutation check: drop `--diff-filter=ACMR` from L45 (working-tree-vs-base leg) → assertion FAILS (`bash_block` filter count=1, `git diff "$base"` leg count=2 — semantic invariant breaks) → revert |
| 3 | SKILL.md STOP behavior (ancillary POSIX-parity check, NOT load-bearing) | Inline bash script: `default=""; [ -z "$default" ] && default=$(echo); [ -z "$default" ] && { echo "default-branch-unresolvable" >&2; exit 2; }; echo unreachable` exits 2 with non-empty stderr containing `default-branch-unresolvable` (NOT 128 from `git merge-base "" HEAD`, NOT the `echo unreachable` post-guard line). **NOTE per /critique m1**: this verifies the bash IDIOM is POSIX-portable, NOT that Claude obeys the STOP prose at runtime. SKILL.md prose is read by Claude (not exec'd as bash); the load-bearing runtime check is AC#4's structural pin + AC#5's `/code-review` self-dogfood + the methodology-discoverability axis (Claude reading SKILL.md prose at /code-review invocation time). The POSIX check is included for parity with the NAW-1 Python implementation's exit-2 contract, NOT to substitute for the runtime check. |
| 4 | STOP-behavior test pin (bash-block scoped, count + brace-group + co-location) | `$PY -m pytest tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_default_branch_resolver_stops_on_empty` exits 0; structural assertions inside `bash_block` confirm (a) count `[ -z "$default" ]` >= 2 (additive STOP-guard pin), (b) canonical brace-group form `&& { echo "default-branch-unresolvable` + `exit 2` literals, (c) co-location `fallback_idx < stop_idx < merge_base_idx` within the bash block |
| 5 | OSDG-1 + shippability + self-dogfood | `$PY -m pytest tests/methodology/test_code_review_skill_drift.py` exits 0 after `cp skills/code-review/SKILL.md ~/.claude/skills/code-review/SKILL.md` forward-sync; `$PY -m tools.shippability_runner` exits 0 with `65/65 PASS`; `/code-review` self-dogfood on slice-065 produces a `code-review.md` with no NEW Blockers on the L40-L42 region |

## Must-not-defer

- [ ] OSDG-1 drift guard clean: in-repo `skills/code-review/SKILL.md` content-equal modulo EOL to installed `~/.claude/skills/code-review/SKILL.md` (EOL-DRIFT-1 EOL-agnostic per ADR-033)
- [ ] BC-PROJ-10 Inclusion-heuristic classification: explicit `## Inclusion-heuristic disposition` block in design.md BEFORE /critique (this slice is forward-looking quality tightening + minor SKILL.md correctness — voluntary-restraint precedent N=8 cumulative — but the classification MUST be explicit to satisfy BC-PROJ-10:173)
- [ ] TF-1 strict-pre-finish: every AC row has a resolvable Test path + function (PTFCD-1 / PTFFD-1 pre-catalog gate clean)
- [ ] Shippability row #65 added citing both `slice-065` AND the slice-064 advisory IDs being closed (BCR-1-traceability axis per slice-054 precedent — even though this is NOT a BCR-1 round-trip)
- [ ] No regression on slice-064 union-of-three-sources fix: the 3 pre-existing assertions covering Source (i)/(ii)/(iii) continue PASSING after tightening
- [ ] PCA-1 chain wiring: `/code-review` self-dogfood at slice-065's /build-slice Step 6 → /code-review must succeed (no AGENT-UNSPAWNABLE; if R-18 recurrence: user-ratified skip per slice-061/062 precedent via SOAD-1 structured options)

## Out of scope

- `/code-review` v2 enhancements (TRI-1 routing + verdict-driven block + AI-bloat passes) — slice-066+ standing nomination per slice-060→061→062→063→064 chain; slice-064 reflection L-Deferred (b)
- SC-007 `/drift-check` enforcement (HIGH severity backlog SC) — separate slice
- R-17 BRANCH-1 clean-tree precondition codification — separate slice
- R-13 OSDG-1 extension to `/slice-candidates` — separate slice; standing slice-052/063 deferral
- Multi-session / parallel-slice / worktree-per-slice execution — backlog candidate
- New RULE-ID / ADR for the L40-L42 STOP behavior — likely no-bump-no-ADR per voluntary-restraint discipline (slice-037/046/050/052/055/056/057 N≥7 cumulative; classification deferred to /design-slice + Inclusion-heuristic discussion)
- Methodology-changelog entry / VERSION bump (PMI-1 / PVFS-1 / AVFS-1 / MCFS-1 / TVFS-1) — tentatively no per voluntary-restraint; final decision at /design-slice per BC-PROJ-10

## Dependencies

- Prior slices: [[slice-064-fix-code-review-diff-resolution-falsifier]] — introduced the SKILL.md Step 1 union-of-three-sources bash block + the 3 test assertions being tightened
- Vault refs:
  - [[architecture/slices/archive/slice-064-fix-code-review-diff-resolution-falsifier/code-review.md]] — source of M1 substring-leak + m1 default-branch resolver + m2 count-assertion advisories
  - [[architecture/slices/archive/slice-064-fix-code-review-diff-resolution-falsifier/reflection.md]] — Deferred section "slice-065+ bundled cleanup nomination"
  - [[architecture/decisions/ADR-062-extend-naw-1-pattern-to-code-review.md]] — the union-of-three-sources mechanism being hardened
  - [[architecture/decisions/ADR-061-mint-naw-1-new-agent-warning.md]] — canonical Python implementation reference for `_resolve_default_branch` STOP behavior (slice-063)
- Source files touched:
  - `skills/code-review/SKILL.md` L40-L42 (AC#3 STOP behavior)
  - `tests/skills/code_review/test_code_review_skill.py` L142 + L166 (AC#1 + AC#2 tightenings) + new `test_skill_md_step_1_default_branch_resolver_stops_on_empty` (AC#4)
- Risk register: no entries (slice-064 reflection categorized as task-list items, not risk-register entries — confirmed by /risk_register_audit returning zero open-high)

## Mid-slice smoke gate

At ~50% of build (after AC#1 + AC#2 tightenings landed + the new AC#4 test authored as WRITTEN-FAILING, BEFORE AC#3 SKILL.md fix), run:

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m pytest tests/skills/code_review/test_code_review_skill.py -v --no-header
```

Expected:
- `test_skill_md_step_1_diff_resolution_uses_union_of_three_sources` PASS (tightened, still PASS on current SKILL.md)
- `test_skill_md_step_1_all_three_legs_share_filter_shape` PASS (tightened, still PASS on current SKILL.md)
- `test_skill_md_step_1_default_branch_resolver_stops_on_empty` **FAIL** (WRITTEN-FAILING — AC#3 SKILL.md fix not yet landed)
- All other slice-064 tests in the module PASS unchanged (no regression)

If any test PASSes when expected to fail OR FAILs when expected to pass: STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes after AC#3 SKILL.md fix lands (the FAILing test now PASSes)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] TF-1 strict-pre-finish: `$PY -m tools.test_first_audit architecture/slices/slice-065-bundle-064-code-critic-cleanup/mission-brief.md --strict-pre-finish` exits 0 (all 6 rows PASSING)
- [ ] OSDG-1 drift clean: `$PY -m pytest tests/methodology/test_code_review_skill_drift.py` exits 0 after installed-side forward-sync
- [ ] `/code-review` self-dogfood on slice-065 produces `code-review.md` with no NEW Blockers on the L40-L42 region (regression check: the union-of-three-sources fix from slice-064 remains intact)
- [ ] Shippability row #65 present in `architecture/shippability.md` + 65/65 PASS via `$PY -m tools.shippability_runner`
- [ ] Full pytest suite ≥ 898/898 PASS (slice-064 baseline + new `test_skill_md_step_1_default_branch_resolver_stops_on_empty`)

## Pipeline position

- **predecessor**: `/reflect` (slice-064)
- **successor**: `/design-slice`
- **auto-advance**: true
- **on-clean-completion**: mission brief + milestone.md written; user explicitly picked candidate #1 via structured-options gate; BFRD-1 confirm gate cleared (user pick: "Not a bug — cancel" — proceed to Step 4 without /repro per the option semantics) → invoke `/design-slice` via the Skill tool.

> Per PCA-1 (methodology-changelog.md v0.41.0).
