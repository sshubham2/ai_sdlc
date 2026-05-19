# Build checks (global / cross-project) — CANONICAL FIXTURE

> **Git-tracked canonical oracle for the BC-1 global rule set (slice-030A, ADR-028).**
> The untracked `~/.claude/build-checks.md` is byte-reconstructed FROM this file.
> BCI-1 asserts the live global file matches this fixture on full per-rule
> structural identity. Per-rule literal-constant tuples in
> `tests/methodology/test_build_checks_audit.py` are the tracked oracle this
> fixture is asserted *against*. Recovery provenance + best-effort residual:
> slice-030A design.md M3 table + build-log.md task-1 recovery record.

Global evergreen rules (apply across all projects, not just this one). Same
schema as the project file.

Per BC-1 (`methodology-changelog.md` v0.10.0). Promotion is manual at `/reflect`
Step 5b (global promotion is the optional cross-project tier).

## Schema

Each rule is an H2 `## BC-GLOBAL-NNN — <title>` followed by `**Field**: value`
lines. Fields: **Severity** (Critical | Important), **Applies to** (`always:
true` OR comma-separated globs), **Promoted from**, **Trigger keywords**
(matched case-insensitively via **word-boundary** regex), optional **Trigger
anchors** (subset of Trigger keywords; keyword path fires only if ≥1 anchor
matches), optional **Negative anchors** (a **final filter** — a rule that would
otherwise fire is suppressed when ≥1 negative anchor word-boundary-matches the
slice text; must not overlap the rule's own positive Trigger keywords/anchors).
Then **Check**, **Rationale**, **Validation hint**.

## Rules

## BC-GLOBAL-1 — LLM structured-output / fence parsing must handle nesting + malformation

**Severity**: Important
**Applies to**: **
**Promoted from**: ai_sdlc slice-001-diagnose-orchestration-fix; slice-005 DEVIATION-1 changed `Applies to: always: true` → `**` so the anchor final-filter is effective (always:true short-circuits before the anchor path)
**Trigger keywords**: parse, fence, code-block, llm, structured-output, fenced, output
**Trigger anchors**: fence, code-block, llm, structured-output
**Negative anchors**: defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync

**Check**: Any code consuming LLM-produced structured / fenced / code-block output MUST handle nested triple-backtick fences, missing closing fences, and language-tag variance, and MUST NOT assume a single well-formed fence or strictly-valid JSON. Validate/repair before parse.

**Rationale**: Generic across any project that consumes LLM structured output: malformed and nested fences are an invariant property of LLM generation, not an incidental bug. High value because a silent parse failure degrades downstream analysis without an obvious error.

**Validation hint**: Grep for fenced/structured-output parsing across the codebase; confirm nested-fence + missing-close + language-tag-variance handling plus tests for each failure mode.

## BC-GLOBAL-2 — Never use `git checkout`/`git restore`/`git stash` to revert files with uncommitted work-in-progress

**Severity**: Critical
**Applies to**: always: true
**Promoted from**: ai_sdlc slice-028-refactor-utf8-rollup-sentinel-version-agnostic (2026-05-16) — destructive git-level revert of an uncommitted in-progress refactor produced a false-green that nearly shipped total loss of the work
**Trigger keywords**: revert, rollback, scratch edit, temporary change, demo, restore, git checkout, git stash, cleanup

**Check**: When a process temporarily mutates a tracked file and must undo the mutation, undo it by the inverse edit, a saved temp copy, or a test-framework fixture (e.g. pytest `monkeypatch`/`tmp_path`) — not by `git checkout -- <path>`, `git restore <path>`, or `git stash`. Git-level reverts target the last commit and will silently destroy any uncommitted work on that path (common in feature-branch / branch-per-change workflows where work-in-progress is intentionally uncommitted for long stretches). Bracket any mutate-then-revert with a content-hash equality check; never trust "the tests still pass" as proof of correct restoration (the previously committed version frequently passes for the wrong reason).

**Rationale**: Generic across any VCS-tracked project with a workflow that keeps work uncommitted while iterating (feature branches, stacked PRs, long-lived task branches). The hazard is structural, not incidental: git revert verbs are defined relative to HEAD/index, never relative to "the change I just made in memory," so they cannot safely undo an uncommitted scratch mutation without collateral loss. The false-green failure mode makes it high-severity: the damage is silent and survives a naive re-test.

**Validation hint**: Grep automation/CI/validation scripts for `git checkout --`, `git restore`, `git stash` near file-mutation logic; require in-place/temp/fixture reversion plus a pre/post hash assertion.

## BC-GLOBAL-3 — Load-bearing external-platform behavior must be verified against official docs before design lock

**Severity**: Important
**Applies to**: **
**Promoted from**: ai_sdlc slice-047-add-two-scope-install (2026-05-19) — a full design→critique→critique-review→TRI-1 cycle was spent discovering the slice's load-bearing premise (Claude Code skill vs subagent install-scope precedence) was false; a 10-minute design-time WebFetch against official docs would have caught it pre-design, and the precedence proved asymmetric across artifact classes (skills personal>project; subagents project>user)
**Trigger keywords**: third-party, external, platform, sdk, api, quota, rate-limit, deprecation, precedence, resolution
**Trigger anchors**: third-party, external, sdk, quota, deprecation
**Negative anchors**: calibration, disposition, aggregated lessons, false positive, meta-discussion, methodology-changelog

**Check**: When a slice's PREMISE or value proposition depends on an external-platform / third-party / SDK behavior (resolution order, precedence, quota, rate limit, deprecation, API contract), that behavior MUST be verified against the official current documentation at /design-slice (or established via /risk-spike) BEFORE the design is locked — never asserted from prior belief and deferred to /critique to catch. If the behavior spans more than one artifact/resource class, verify EACH class independently: platform precedence is not guaranteed symmetric (e.g. Claude Code skills resolve personal>project while subagents resolve project>user — the inverse). Cite the doc URL plus the verifying fetch in design.md.

**Rationale**: Generic across any project building on a third-party platform / SDK / API. A false load-bearing external assumption is not an incidental bug — it invalidates the slice's entire reason to exist, and it is cheapest to refute at design time (a single doc fetch) and most expensive to refute after design→critique→review→triage has been spent. The asymmetry corollary is the high-value, non-obvious part: verifying one resource class's behavior and generalizing to a sibling class is a recurring blind spot the first Critic exhibited in slice-047 (caught only by the meta-Critic).

**Validation hint**: Grep the slice's design.md / ADRs for claims of the form "rides/uses/relies on <external platform> <behavior>"; require an accompanying official-doc URL plus a record that the behavior was fetched/verified this slice (not assumed), and — for multi-class platform behaviors — a per-class verification line.
