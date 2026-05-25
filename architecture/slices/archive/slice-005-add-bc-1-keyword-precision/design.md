# Design: Slice 005 add-bc-1-keyword-precision

**Date**: 2026-05-10
**Mode**: Standard

## What's new

- **Word-boundary keyword matching** in `tools.build_checks_audit._rule_applies` (replaces case-insensitive substring `kw in haystack` with `re.search(rf"\b{re.escape(kw)}\b", haystack, re.IGNORECASE)`).
- **New optional `Trigger anchors:` field** in build-checks rule schema. Comma-separated subset of `Trigger keywords`. If specified, the rule fires on the keyword-applicability path only when ≥1 anchor matches the slice text (word-boundary). If absent, the rule fires when ≥1 keyword matches (preserves backward-compat for rules that don't migrate).
- **Migration**: the three existing rules (BC-PROJ-1 in `architecture/build-checks.md`, BC-PROJ-2 in `architecture/build-checks.md`, BC-GLOBAL-1 in `~/.claude/build-checks.md`) get anchors added in this slice — these are the rules whose false positives motivated the slice.
- **New parse-violation kind** `anchor-not-in-keywords`: if `Trigger anchors:` lists a value that isn't in `Trigger keywords`, audit emits an Important violation (mirrors how `missing-field` / `invalid-severity` are reported today).
- **Schema documentation pin (TWO surfaces, per Critic M3)**: top-of-file description in `architecture/build-checks.md` AND `~/.claude/build-checks.md` is updated to mention BOTH the word-boundary semantics AND the optional `Trigger anchors:` field. **Two prose-pin assertions** (one per surface): (a) literal substring `Trigger anchors` appears in both files; (b) literal substring `word-boundary` appears in both files. The canonical schema-prose phrasing locks both substrings byte-equal across the two files at /build-slice time.
- **Module docstring + `_rule_applies` docstring** updated to describe the new precision rule. (Not test-pinned individually — covered by the existing methodology-conformance pattern of "behavior changes carry docstring updates"; if drift becomes a problem, a future slice promotes a docstring-pin like slice-004 did for RR-1.)

## What's reused

- `tools/build_checks_audit.py` — `_RULE_HEADING_RE`, `_FIELD_RE`, `_REQUIRED_FIELDS`, `_ALLOWED_SEVERITIES`, `_ALWAYS_SENTINEL_RE`, `BuildCheckRule`, `BuildCheckViolation`, `AuditResult`, `_parse_rules`, `audit_slice`, `main`, `_format_human` — all unchanged in interface; only `_rule_applies` body changes + `BuildCheckRule` gets a new `trigger_anchors: tuple[str, ...]` field (default `()`).
- Existing 18 BC-1 tests in `tests/methodology/test_build_checks_audit.py` — must continue to pass without modification.
- [[slice-001-diagnose-orchestration-fix]] — the slice that introduced BC-PROJ-1 + BC-PROJ-2; its mission-brief.md is the canonical "legitimate fence-parsing slice" backtest fixture (anchor `llm` + supporting keywords fire heavily).
- [[slice-003-add-val-1-imports-allowlist]] — first false-positive instance (slice-003 mission-brief / design contain `parse_declared_deps`, `tomllib`-parses, `ast`-parses; word-boundary alone silences these).
- [[slice-004-fix-rr1-audit-docstring-or-regex]] — second false-positive instance (slice-004 mission-brief / design contain bare-word `parse`, `backtick`, `output` in regex/markdown/CLI contexts; needs anchors to silence).
- [[ADR-002]] precedent: lenient API / strict CLI asymmetry — the same posture applies here (anchor field validation is strict at parse time; absence is accepted as backward-compat).
- Methodology: `methodology-changelog.md` v0.10.0 BC-1 v1 limitations explicitly contemplated this kind of precision improvement; this slice is the v1.1 enhancement.

## Components touched

### `tools/build_checks_audit.py` (modified)

- **Responsibility**: parse build-checks.md, score rule applicability against a slice's changed files + mission-brief / design text. This slice tightens applicability scoring to reduce false-positive noise on the `Trigger keywords` path.
- **Lives at**: `tools/build_checks_audit.py` (modified)
- **Key interactions**: read by `skills/build-slice/SKILL.md` Step 6 (BC-1 audit invocation); reads `architecture/build-checks.md` + `~/.claude/build-checks.md`; emits JSON or human-readable output.
- **Surface change**:
  - `BuildCheckRule` dataclass adds `trigger_anchors: tuple[str, ...]` field (default `()` — the empty tuple).
  - `_parse_rules` reads optional field `Trigger anchors:` (case-insensitive header match), splits on commas, lowercases, dedupes, validates membership in `trigger_keywords`. If validation fails, emits `BuildCheckViolation(kind="anchor-not-in-keywords")`.
  - `_rule_applies` keyword-path logic:

    ```python
    # New body (replaces 'if kw in haystack' substring check):
    if rule.trigger_keywords and slice_text:
        haystack = slice_text.lower()
        matched = {
            kw for kw in rule.trigger_keywords
            if re.search(rf"\b{re.escape(kw)}\b", haystack)
        }
        if not matched:
            return False
        if rule.trigger_anchors:
            return any(a in matched for a in rule.trigger_anchors)
        return True
    ```
  - `to_dict` exposes `trigger_anchors` as a list (mirrors `applies_to`, `trigger_keywords`).
- **Backward-compat**: rules without `Trigger anchors:` keep firing on any keyword match (with word-boundary). The only behavior change for un-migrated rules is "substring → word-boundary" — confirmed safe across all existing fixtures + production rules (none of the existing keyword vocabulary has substring-only intent).

### `architecture/build-checks.md` (modified)

- **Responsibility**: project-level evergreen rules.
- **Lives at**: `architecture/build-checks.md`
- **Surface change**:
  - L3 schema-description prose updated to mention word-boundary semantics + `Trigger anchors:` field.
  - BC-PROJ-1 gets `Trigger anchors: subagent, fan-out` (anchors are domain-specific to subagent fan-out concerns; supporting keywords like `agent`, `parallel`, `spawn`, `orchestrate` may be incidental).
  - BC-PROJ-2 gets `Trigger anchors: fence, code-block, llm` (anchors are domain-specific to LLM-fence-parsing; supporting keywords like `parse`, `backtick`, `output`, `prompt`, `response`, `agent` may appear in unrelated contexts — the N=2 false-positive class).

### `~/.claude/build-checks.md` (modified, **outside repo — user's home**)

- **Responsibility**: global cross-project evergreen rules.
- **Lives at**: `~/.claude/build-checks.md` (user's home directory; not in this repo).
- **Surface change**:
  - L3 schema-description prose updated to mention word-boundary semantics + `Trigger anchors:` field.
  - BC-GLOBAL-1 gets `Trigger anchors: fence, code-block, llm, structured-output` (anchors mirror BC-PROJ-2 plus the global-only `structured-output` term).
  - **Design deviation logged at /build-slice T5 (2026-05-10)**: BC-GLOBAL-1's `Applies to:` changed from `always: true` → `**` (universal-glob-on-any-changed-file). Reason: `always: true` short-circuits before the anchor filter (`_rule_applies` returns True immediately), making AC #1+#2 unachievable as-written ("0 applications of BC-GLOBAL-1 on slice-003+004 archive backtests" requires the rule to NOT fire — but always-true bypasses anchors). Three options considered: (1) change `Applies to:` to a language-glob list — rejected, hardcoding extensions is brittle and forgets new languages; (2) extend `_rule_applies` to apply anchors to always-true path — rejected, breaks "always" semantics; (3) change `Applies to:` to `**` (any changed file) — chosen, language-agnostic, satisfies AC #1+#2 because backtests don't pass `--changed-files`. Real-world `/build-slice` invocations always pass `--changed-files`, so BC-GLOBAL-1 fires identically on every real slice (same effective behavior). Only difference: archive-folder backtests without `--changed-files` now correctly fall through to the anchors-filtered keyword path. **Empirical verification table in this design.md is unchanged** — the table only enumerated anchor-match counts; the silencing claim was always premised on "anchors filter the keyword path" which is now true for BC-GLOBAL-1 too.
- **Out-of-repo edit caveat**: this file lives in the user's home, not the repo. The slice's git diff won't show it; build-log.md MUST capture the edit at /build-slice T-final. The schema-pin test (AC #5) reads `Path.home() / ".claude" / "build-checks.md"` and accepts a skip-marker when the file isn't present in the test environment (e.g., CI without the home file) — see Test #4 below.

### `tests/methodology/test_build_checks_audit.py` (modified)

- **Responsibility**: BC-1 audit test home.
- **Lives at**: `tests/methodology/test_build_checks_audit.py` (existing 18 tests preserved; 4 new tests added per TF-1).
- **Surface change (per Critic M1+M2+M3)**: 7 new tests per the TF-1 plan in mission-brief.md (was 4 before Critic):
  - test_slice_003_archive_backtest_no_bc_proj_2_or_global_1_applications (AC #1)
  - test_slice_004_archive_backtest_no_bc_proj_2_or_global_1_applications (AC #2)
  - test_legitimate_llm_fence_brief_still_triggers_bc_proj_2_and_global_1 (AC #3)
  - test_build_checks_schema_documents_trigger_anchors_field_name (AC #5 surface a)
  - test_build_checks_schema_documents_word_boundary_semantics (AC #5 surface b — added per Critic M3)
  - test_migrated_rules_have_expected_anchors (added per Critic M1 — pins BC-PROJ-1 / BC-PROJ-2 anchor tuples by reading `architecture/build-checks.md` via `_parse_rules`; skip-if-not-present for `~/.claude/build-checks.md`'s BC-GLOBAL-1)
  - test_anchor_not_in_keywords_yields_violation (added per Critic M2 — promoted from OPTIONAL to mandatory; the new `anchor-not-in-keywords` parse-violation kind closes the must-not-defer "Input validation on any new schema field" loop).

## Contracts added or changed

### `Trigger anchors:` field (new — optional in build-checks.md schema)

- **Defined in code at**: `tools/build_checks_audit.py` — `_parse_rules` reads it; `BuildCheckRule.trigger_anchors` stores it; `_rule_applies` consumes it.
- **Auth model**: N/A (offline tooling).
- **Validation**:
  - Presence: optional. Absence = empty tuple = current behavior (any keyword match fires; word-boundary applied).
  - Format: comma-separated names. Each name MUST appear in `Trigger keywords` for the SAME rule (case-insensitive comparison after `.strip().lower()`). Names not in trigger_keywords → parse violation `anchor-not-in-keywords`.
  - Empty value (`Trigger anchors:` with nothing after the colon) → empty tuple, treated as "absent".
- **Error cases**: parse violation `anchor-not-in-keywords` (Important severity) if any anchor isn't in trigger_keywords. Rule still parsed otherwise; surfaces alongside other violations.

### `_rule_applies(rule, changed_files, slice_text) -> bool` (modified — internal)

- **Defined in code at**: `tools/build_checks_audit.py::_rule_applies` (per Critic m3 — symbol reference, not line range)
- **Behavior change**: keyword-path matching switches from case-insensitive substring (`if kw in haystack`) to case-insensitive word-boundary (`re.search(rf"\b{re.escape(kw)}\b", haystack)`); anchor filter applied when `rule.trigger_anchors` is non-empty.
- **Backward-compat**: rules with `Trigger keywords` but no `Trigger anchors`: behavior is "any word-boundary keyword match → fires" (matches today modulo substring → word-boundary).

## Data model deltas

None. This slice is config-schema + tool-logic only; no DB / persistence layer touched.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Empty matrix is accepted — this slice introduces no new modules. The change is logic + schema enhancement to existing module `tools/build_checks_audit.py` and schema-prose updates to existing markdown files.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(Empty — no new modules.)

## Decisions made (ADRs)

- [[ADR-004]] — BC-1 keyword precision via word-boundary + Trigger anchors — **reversibility: cheap** (single function change in `_rule_applies` + optional schema field; existing rules without anchors continue to fire on word-boundary keyword matches; reverting to substring is a 5-line change, reverting anchor field is `git rm` of 3 added lines across the build-checks.md files).

## Authorization model for this slice

N/A — offline methodology tooling. No auth surface, no user-facing actions.

## Error model for this slice

- New parse violation: `anchor-not-in-keywords` (Important severity, kind="anchor-not-in-keywords"). Emitted when a rule's `Trigger anchors:` lists a value not present in `Trigger keywords:` for the same rule. Rule is still parsed (other fields read normally); the violation surfaces alongside `missing-field` / `invalid-severity` in the audit's output. **Applicability behavior with invalid anchors** (per Critic m1 — clarification, no algorithm change): the algorithm checks ALL anchors as parsed (`any(a in matched for a in rule.trigger_anchors)`). Invalid anchors silently never match because `matched` is a subset of `trigger_keywords` and an invalid anchor is by definition not in `trigger_keywords` — so the invalid anchor's `a in matched` is always False. The audit user is notified via the parse violation (separate channel from the `applicable` array). Exit code 1 from CLI when violations exist (existing semantic, unchanged).
- No new behavior for `audit_slice` callers: missing `Trigger anchors:` field is a non-event (interpreted as empty).
- Existing error paths (missing-field, invalid-severity, missing files) preserved unchanged.

## Empirical verification (per slice-004 B1 + slice-003 m1 lessons)

Before /critique submits this design, the precision algorithm was empirically verified against the three production slices (slice-001 = legitimate match; slice-003 + slice-004 = false-positive cases). Results:

| Slice | Anchor matches (BC-PROJ-2: fence/code-block/llm) | Rule fires post-precision? | Today (substring)? | Expected |
|-------|--------------------------------------------------|----------------------------|--------------------|----------|
| slice-001 mission-brief.md | llm=3 | YES (fires) | YES | YES (legitimate match) |
| slice-001 design.md | fence=8, llm=1 | YES (fires) | YES | YES (legitimate match) |
| slice-003 mission-brief.md | 0 | **NO** (silenced) | YES (false-positive on `parse_declared_deps`) | NO (false positive eliminated) |
| slice-003 design.md | 0 | **NO** (silenced) | YES (false-positive) | NO |
| slice-004 mission-brief.md | 0 | **NO** (silenced) | YES (false-positive on `parses`/bare `parse`) | NO |
| slice-004 design.md | 0 | **NO** (silenced) | YES (false-positive) | NO |
| Synthetic positive: "Parse the LLM agent's fenced output for nested triple-backtick code-block sections" | llm=1, code-block=1 (fence=0; `\bfence\b` doesn't match `fenced`) | YES (fires) | YES | YES |
| Synthetic neg: "Add unit tests for the parser regex" (no anchors, only `parse`) | 0 | NO (silenced) | YES (false-positive) | NO |

(Verified via `re.findall(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE)` against each file's contents at /design-slice time. Confirmed cost: ~30 seconds — N=4 across slices for empirical-verification-at-design-time discipline.)

## Out of scope (re-iteration of mission-brief)

- Auto-detecting recurring patterns from `lessons-learned.md` (deferred to `/critic-calibrate` v2).
- Brace-expansion / negation / `?` single-char globs (deferred per BC-1 v1 limitations).
- Morphological variant expansion of trigger keywords (e.g., adding `parses, parsed, parsing` to BC-PROJ-2 alongside `parse`). Synthetic positive-case test uses bare anchor words (`fence`, `llm`); real-world morphological coverage is deferrable. If a future slice's brief mentions only `fenced` (not bare `fence`), it'll defer-with-rationale, same as today, but the slate is now clean.
- `add-csp-1-docstring-or-regex` — sibling tooling slice; independent of this slice; carries forward.
- `/critic-calibrate` invocation — unblocked by archiving this slice (≥5 archived slices threshold).
- Promoting BC-1 to v0.21.x in `methodology-changelog.md` — `/reflect` decides at slice-end.

## Builder notes

- The existing 18 BC-1 tests must pass — the only behavioral change for existing fixtures is `kw in haystack` → `re.search(rf"\b{re.escape(kw)}\b", haystack)`. All existing fixtures use bare-word keywords matching bare-word text → word-boundary and substring agree. (Specifically verified: `keyword_only.md` BC-PROJ-3 keyword `auth` against test text `"Rework JWT token refresh handling for the auth flow."` — bare `auth` word-boundary matches; all 4 BC-PROJ-3 keywords are bare-word matches.)
- Migration is in scope: BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1 each get a `Trigger anchors:` line added. Without migration, AC #1 + #2 backtests still fail (because un-migrated rules fire on any word-boundary keyword match — `output` in slice-004 mission-brief still triggers BC-PROJ-2).
- The `~/.claude/build-checks.md` edit is outside the repo. Capture in build-log.md at T-final (before-after diff). The slice's git diff won't show it. Schema-pin tests (AC #5 surfaces a + b) read the file via `Path.home() / ".claude" / "build-checks.md"` and degrade gracefully when the file isn't present (skip-marker — pytest `pytest.skip` with reason). The project-level pins are the canonical ones for CI.

  **CI gap acknowledged (per Critic m4)**: when the global file is skipped in CI, the global file's prose pins are not exercised. If `~/.claude/build-checks.md` diverges silently (e.g., a future maintenance pass drops `Trigger anchors` from the global file's schema description but leaves it in the project file), CI passes but the global file is wrong. Mitigations: (1) /validate-slice T-final runs the global-file pins MANUALLY locally and captures pass/fail in `validation.md` evidence section (per Critic m4); (2) the global-file edit is committed in build-log.md as forensic evidence; (3) future slice could promote the global pins to a separate test-suite that runs only locally. Current design is acceptable; the gap is documented, not closed.
- Test fixture for `anchor-not-in-keywords` parse violation (the new violation kind, **promoted to TF-1 per Critic M2**): construct in test as inline `tmp_path` text + write to a local `.md`; no new permanent fixture file needed under `tests/methodology/fixtures/build_checks/` (mirrors how `multi_rules.md` fixture is organized).
- Test for migrated rule anchor lists (**added per Critic M1**): `test_migrated_rules_have_expected_anchors` reads the actual `architecture/build-checks.md` via `_parse_rules` and asserts BC-PROJ-1.trigger_anchors == ('subagent', 'fan-out') AND BC-PROJ-2.trigger_anchors == ('fence', 'code-block', 'llm'). Equivalent for `~/.claude/build-checks.md`'s BC-GLOBAL-1 with `pytest.skip` if the file isn't present. Closes the migration-typo gap.
- TF-1 PENDING → WRITTEN-FAILING genuineness (per slice-003 lesson): each backtest test should fail BEFORE implementation in a way that distinguishes "fix not applied" from "fix doesn't exist". Pre-fix: `audit_slice(slice-003-archive)` returns BC-PROJ-2 in `applicable` (substring match on `parse`). Post-fix: `audit_slice(slice-003-archive)` returns BC-PROJ-2 in `skipped` (anchor `fence/llm/code-block` doesn't match). Assertion shape: `BC-PROJ-2 not in {r.rule_id for r in result.applicable}` AND `BC-PROJ-2 in {r.rule_id for r in result.skipped}`. The "in skipped" half-assertion makes the failure mode unambiguous.
- Per slice-001 cross-shell lesson: any test commands using `$PY` should be single-line PowerShell-friendly (no Bash `\` continuation).
- Per slice-004 Python 3.12+ lesson: avoid literal `\-` or other unrecognized escape sequences in any docstring or comment added in this slice. The regex pattern `rf"\b{re.escape(kw)}\b"` is fine — `\b` IS a recognized regex escape; the f-string-with-r-prefix protects the literal `\b` from Python's string-escape parser.
