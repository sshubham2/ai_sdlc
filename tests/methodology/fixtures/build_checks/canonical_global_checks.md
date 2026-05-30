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

## BC-GLOBAL-4 — Parsing external ISO-8601 / RFC-3339 timestamps must handle tz-naive, case-insensitive Z/z, and cross-version fromisoformat acceptance

**Severity**: Important
**Applies to**: **
**Promoted from**: ai_sdlc slice-084-harden-pcr-2a-clock-skew-winner (2026-05-30) — a clock-skew guard's `datetime.fromisoformat` parse shipped THREE latent traps in one ~10-line helper: an offset-less stamp parses as a naive datetime then `naive > aware` raises `TypeError` (B1); the `Z`→`+00:00` normalization was case-sensitive so a valid lowercase `z` fail-closed wrongly (code-Critic M1); and `fromisoformat`'s acceptance surface diverges across the 3.10/3.11 floor (offset-no-colon + space-separated parse on 3.11+, `ValueError` on 3.10 — code-Critic M2). The design-Critic's own `Z`-fix was itself defective, caught only by executing an adversarial corpus.
**Trigger keywords**: timestamp, datetime, iso-8601, iso8601, rfc-3339, rfc3339, fromisoformat, claimed_at, timezone
**Trigger anchors**: timestamp, datetime, iso-8601, iso8601, rfc-3339, rfc3339, fromisoformat
**Negative anchors**: calibration, disposition, aggregated lessons, false positive, meta-discussion, methodology-changelog

**Check**: When code parses an EXTERNAL / hand-editable / cross-machine ISO-8601 / RFC-3339 timestamp string (not a value it produced itself), it MUST handle three traps before comparing: (1) tz-naive — `datetime.fromisoformat` parses an offset-less string SUCCESSFULLY as a naive datetime, after which comparing it against a timezone-aware value raises `TypeError`; treat parsed-but-naive as a fail-closed error path and never reach the comparison. (2) case — the RFC-3339 `Z` UTC designator is case-INsensitive (§5.6); any `Z`→`+00:00` normalization MUST accept lowercase `z` too. (3) cross-version acceptance — `datetime.fromisoformat` was relaxed in Python 3.11 (offset-without-colon, space separator); on a `>=3.10` floor the same string parses on 3.11+ but raises on 3.10, so document the floor behavior and do not claim version-uniformity beyond what the normalization actually covers. Bracket the parse with `except (ValueError, TypeError)` and pin an adversarial corpus test exercising BOTH directions (accepted + rejected).

**Rationale**: Generic across any project parsing timestamps from an external or cross-machine source. All three traps are silent-by-default: tz-naive crashes only when the naive value is compared (not at parse), case-sensitivity rejects a valid input in the safe-looking direction, and the version split makes behavior interpreter-dependent with no error. Witnessed compounding in slice-084 where a single normalization fix introduced two of the three — and the design-stage Critic stack could not catch them because the defect is in executed parse behavior, not design prose (the BC-PROJ-13 / regex-APED-1 "execute the matcher" lineage applied to timestamp parsing).

**Validation hint**: Grep for `fromisoformat` / `strptime` / timestamp parsing of external inputs; confirm an `except (ValueError, TypeError)` guard, a `tzinfo is None` check before any aware/naive comparison, a case-insensitive `Z`/`z` normalization, and a parametrized test corpus covering offset-less, lowercase-z, offset-no-colon, space-separated, microsecond, and garbage inputs in both accept/reject directions.
