# Build checks (project-specific) — CANONICAL FIXTURE

> **Git-tracked canonical oracle for the BC-1 project rule set (slice-030A, ADR-028).**
> The gitignored live `architecture/build-checks.md` is byte-reconstructed FROM this
> file. BCI-1 (`tools/build_checks_integrity.py`) asserts the live file matches this
> fixture on full per-rule structural identity. The per-rule literal-constant tuples
> in `tests/methodology/test_build_checks_audit.py` are the tracked oracle this
> fixture is asserted *against* (fixture = subject, literal constant = oracle).
> Recovery provenance + best-effort residual for the 3 lost rules: see slice-030A
> design.md M3 table + build-log.md task-1 recovery record.

Evergreen rules promoted from lessons-learned. `/build-slice` reads the live copy
at Step 6. Rules whose `Applies to` glob matches changed files, or whose
`Trigger keywords` appear in this slice's mission-brief.md / design.md, are
surfaced for the builder to address.

Per BC-1 (`methodology-changelog.md` v0.10.0). Promotion is manual at `/reflect`
Step 5b.

## Schema

Each rule is an H2 `## BC-PROJ-NNN — <title>` followed by `**Field**: value`
lines. Fields: **Severity** (Critical | Important), **Applies to** (`always:
true` OR comma-separated globs), **Promoted from**, **Trigger keywords**
(comma-separated; matched case-insensitively against mission-brief.md /
design.md via **word-boundary** regex — slice-005/ADR-004, was bare substring
pre-slice-005), optional **Trigger anchors** (comma-separated subset of Trigger
keywords; when present the keyword path fires only if ≥1 anchor word-boundary-
matches), optional **Negative anchors** (comma-separated tokens acting as a
**final filter** — slice-008/ADR-007, BC-1 v1.2: a rule that would otherwise
fire via any positive path is suppressed when ≥1 negative anchor word-boundary-
matches the slice text; negative anchors must not overlap the rule's own
Trigger keywords/anchors). Then **Check**, **Rationale**, **Validation hint**.

## Rules

## BC-PROJ-1 — Subagent fan-out concerns must be reviewed before parallel dispatch

**Severity**: Important
**Applies to**: agents/**/*.md
**Promoted from**: ai_sdlc slice-001-diagnose-orchestration-fix — parallel subagent fan-out exposed a permission cascade-failure mode; recurring class across diagnose-orchestration slices
**Trigger keywords**: subagent, fan-out, agent, parallel, spawn, orchestrate
**Trigger anchors**: subagent, fan-out
**Negative anchors**: defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync

**Check**: When a slice dispatches subagents in a fan-out (multiple `Agent` calls), verify the dispatch is sequential-by-default OR the parallel path is an explicit opt-in, and that subagent tool-permission cascade-failure ([claude-code #57037](https://github.com/anthropics/claude-code/issues/57037)) is mitigated. Do not assume parallel subagent spawn inherits parent permissions.

**Rationale**: Permanent because the AI-SDLC pipeline structurally fans out subagents (Critic, meta-Critic, diagnose passes); the parallel-spawn permission cascade is an invariant exposure of that architecture, not a one-off bug (R-1; recurred slice-001/002/029).

**Validation hint**: Grep slice dispatch code for multiple `Agent(` calls in one message; confirm sequential-by-default or documented `--parallel` opt-in.

## BC-PROJ-2 — LLM-fence / structured-output parsing must handle nested + malformed fences

**Severity**: Important
**Applies to**: skills/**/*.py, tools/**/*.py
**Promoted from**: ai_sdlc slice-001-diagnose-orchestration-fix — LLM-fence parsing of subagent output is a recurring failure surface across diagnose/critique passes
**Trigger keywords**: fence, code-block, llm, parse, structured-output, fenced, output
**Trigger anchors**: fence, code-block, llm
**Negative anchors**: defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync

**Check**: Any code parsing LLM-produced fenced / code-block / structured output MUST handle nested triple-backtick fences, missing closing fences, and language-tag variance. Do not assume a single well-formed fence.

**Rationale**: Permanent because the pipeline routinely parses LLM-generated fenced output (subagent results, diagnose passes); malformed/nested fences are an invariant property of LLM output, not a one-off (recurred slice-001/004).

**Validation hint**: Grep for fence/code-block parsing; confirm nested-fence + missing-close + language-tag-variance handling and tests covering each.

## BC-PROJ-3 — Validation/demo harnesses must never destructively revert files carrying uncommitted slice work

**Severity**: Critical
**Applies to**: always: true
**Promoted from**: slice-028-refactor-utf8-rollup-sentinel-version-agnostic (2026-05-16) — a `git checkout -- <test file>` to revert AC2/AC3 demo mutations silently reverted the ENTIRE uncommitted slice refactor to pre-slice HEAD; the post-revert green was the OLD sentinel passing (false-green that nearly masked total loss of the slice's work)
**Trigger keywords**: validate, demo, revert, fixture, mutate, git checkout, git restore, git stash, scratch

**Check**: Any validation/build/demo step that mutates a source file and then reverts it MUST revert via an in-place reverse edit, a temp-copy swap, or `monkeypatch` — NEVER `git checkout -- <path>`, `git restore <path>`, or `git stash` on a path that may carry uncommitted slice work. Under branch-per-slice (BRANCH-1) the slice's work is uncommitted until `/commit-slice`, so any git-level revert of a slice-touched path destroys the slice. After any such mutate-then-revert sequence, assert the file's pre/post content hash is identical to the intended state (not merely "tests pass" — a stale/old version may pass for the wrong reason).

**Rationale**: Permanent because branch-per-slice (BRANCH-1) structurally guarantees slice work is uncommitted through /build-slice and /validate-slice. `git checkout`/`restore`/`stash` operate against the last commit, not the in-progress slice, so they are always destructive to uncommitted slice work — this is not a one-off bug but an invariant of the workflow. The failure is especially dangerous because a silent full-revert often yields a false-GREEN (the prior committed code passes its own old tests), which a casual re-run will not catch.

**Validation hint**: Grep slice harness/validation code for `git checkout --`, `git restore`, `git stash` operating on source paths; for any mutate-then-revert block, confirm the revert is in-place/temp/monkeypatch and that a content-hash equality assertion brackets the sequence.
## BC-PROJ-4 — Methodology-gate slices must exercise every affected gate on the real artifact (audit field-line / folder-name / classifier blind spots)

**Severity**: Important
**Applies to**: tools/**/*.py, skills/**/*.md
**Promoted from**: slice-031-complete-shippability-decoupling (2026-05-17) — N+3 of the slice-024/029/030A "design-stage Critics cannot see tooling-interaction defects" class: a trailing annotation on `**Test-first**: true` silently disabled the TF-1 gate (R-7); a letter-suffixed slice folder broke BRANCH-1's numeric `slice-NNN-` regex (R-6); the SCMD-1 AST classifier's false-positive surface (synthetic tmp trees, unrelated home reads) was invisible until the real-corpus mid-slice smoke gate
**Trigger keywords**: audit, gate, regex, field-line, branch, methodology, prerequisite, pre-finish, skill, classifier, ast

**Check**: When a slice changes an audit/gate's own parse rules (field-line / heading / folder-name regexes), a `skills/*/SKILL.md` gate-prose contract, or an AST/text classifier, you MUST run every affected gate against the ACTUAL slice artifact (real mission-brief / real folder name / real catalog / real codebase) at BOTH the /build-slice prerequisite check AND pre-finish — never only against unit fixtures. Read the gate's human output: "not enabled" / "usage-error" / "carry-over exempt" / "0 rows" on a slice that SHOULD engage the gate is a silent-bypass alarm, not a pass. For AST/text classifiers, a real-corpus smoke gate at ~50% is mandatory — design-stage reasoning cannot enumerate the false-positive surface.

**Rationale**: Permanent because the AI-SDLC pipeline is self-hosting: slices routinely modify the very audits/gates that police them, and a gate's own parse rules (regex anchors, folder-name patterns, default-off semantics, classifier shape-matching) are structurally invisible to design-stage Critics that review intent, not the audit-vs-artifact interaction. The failure mode is silent (default-off / usage-error / vacuous-pass yields a GREEN), so it cannot be caught by "tests pass" — only by executing the real gate on the real artifact and reading its output. Recurred slice-024 / slice-029 / slice-030A / slice-031 (R-6, R-7).

**Validation hint**: For the changed gate, run `$PY -m tools.<gate>_audit <real slice/artifact path>` (not a tmp fixture) at prerequisite + pre-finish; assert the gate reports ENGAGED (e.g. TF-1 "N row(s)" not "not enabled"; BRANCH-1 "clean" not "usage-error"); for classifiers, diff the classification against a hand-eyeballed real-corpus sample at the mid-slice smoke gate.
