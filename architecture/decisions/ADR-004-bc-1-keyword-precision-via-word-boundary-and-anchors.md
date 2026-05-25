---
id: ADR-004
title: BC-1 keyword precision via word-boundary regex match plus optional Trigger anchors per-rule field
date: 2026-05-10
slice: slice-005-add-bc-1-keyword-precision
reversibility: cheap
status: accepted
---

# ADR-004: BC-1 keyword precision via word-boundary + Trigger anchors

## Context

Per `methodology-changelog.md` v0.10.0, BC-1 introduced a build-checks gate that surfaces evergreen rules at `/build-slice` pre-finish based on (1) `Applies to: always: true`, (2) glob match on `--changed-files`, or (3) `Trigger keywords` substring match against mission-brief.md + design.md. The keyword-match path uses **case-insensitive substring** (`if kw in haystack`).

Slice-003 reflection (2026-05-09) and slice-004 reflection (2026-05-10) both flagged the same false-positive class: BC-PROJ-2 / BC-GLOBAL-1 (LLM-fence-parsing rules with trigger keyword `parse`) firing on slices whose briefs mention `parse_declared_deps` (slice-003) or `parses through _RISK_HEADING_RE` (slice-004). N=2 confirmed recurrences. Aggregated lessons in `architecture/slices/_index.md` flagged the precision improvement as overdue. The recurring noise trains the builder to ignore BC-1 surfacing — which defeats the lessons-learned-to-builder-feedback-loop the rule exists to close.

A precision improvement is needed that:

1. Silences the confirmed N=2 false positives without manual per-slice defer-with-rationale ritual.
2. Preserves legitimate matches (slice-001's mission-brief + design.md MUST continue to fire BC-PROJ-2 + BC-GLOBAL-1; slice-001 is the canonical legitimate fence-parsing slice).
3. Stays backward-compatible with existing rules — un-migrated rules continue to behave with current applicability semantics (modulo the substring → word-boundary tightening, which is non-controversial because no existing keyword vocabulary intends substring-only match).
4. Is reversible at low cost (cheap per ADR reversibility tag — single-function logic change + optional schema field).

## Options considered

1. **Word-boundary regex match alone** (`\bkw\b`).
   - Pros: zero schema change; one-line logic change; eliminates substring-of-longer-word false positives (e.g., `parse_declared_deps` no longer matches `parse`).
   - Cons: empirically insufficient for slice-004's case — slice-004 mission-brief contains BARE `parse`, `backtick`, `output` in regex/markdown/CLI contexts (not LLM-fence). Word-boundary alone still fires on those bare-word matches.
   - Verdict: necessary precision improvement, but insufficient on its own.

2. **Word-boundary + multi-keyword conjunction** (per-rule `Trigger requires: N` field, default 1).
   - Pros: simple numeric calibration; backward-compatible with `requires: 1` default.
   - Cons: numeric thresholds aren't well-calibrated — `requires: 2` is too lax (slice-004 mission-brief has 3 distinct keywords matching word-boundary: parse, backtick, output → still fires); `requires: 3` is too restrictive (might suppress legitimate matches with only 2 keywords). No semantic meaning; just counting.
   - Verdict: rejected — calibration requires arbitrary tuning that doesn't reflect domain semantics.

3. **Word-boundary + designated `Trigger anchors` subset** (per-rule, optional).
   - Pros: anchors are a semantic curation — domain-specific keywords that signal the rule's domain. Authors curate which subset is "must-be-present-for-domain". Empirically clean: BC-PROJ-2 anchors `{fence, code-block, llm}` give 0 matches on slice-003 + slice-004 briefs (silenced) and ≥1 match on slice-001 (fires). Backward-compatible: rules without anchors keep current behavior.
   - Cons: schema change (one new optional field) + migration of existing 3 rules. Requires the rule author to identify anchors at promotion time (one-time cost, manual).
   - Verdict: chosen.

4. **Word-boundary + machine-learning / NLP semantic similarity**.
   - Pros: handles morphological variants and synonyms transparently.
   - Cons: enormous overkill for v1 BC-1; introduces a model dependency to a methodology audit; opaque debugging.
   - Verdict: rejected — out of proportion to the problem.

5. **Per-keyword negative-context** (e.g., `parse: {requires: domain-keyword}` per-keyword config).
   - Pros: maximal precision per keyword.
   - Cons: schema explosion; v1 over-engineering; same intent achieved more cleanly by anchors.
   - Verdict: rejected.

## Decision

Adopt **Option 3**: implement word-boundary regex match (`\bkw\b`, case-insensitive) as the universal keyword-applicability mechanism in `tools.build_checks_audit._rule_applies`, AND add an optional per-rule `Trigger anchors:` schema field that, when specified, requires ≥1 anchor (subset of `Trigger keywords`) to match (word-boundary) for the rule to fire on the keyword path. Migrate the three existing rules in this same slice to use anchors:

- BC-PROJ-1 (subagent fan-out rule): `Trigger anchors: subagent, fan-out`
- BC-PROJ-2 (LLM-fence-parsing rule, project): `Trigger anchors: fence, code-block, llm`
- BC-GLOBAL-1 (LLM-fence-parsing rule, global): `Trigger anchors: fence, code-block, llm, structured-output`

Add a new parse-violation kind `anchor-not-in-keywords` for rules whose anchors aren't subsets of trigger_keywords.

Update schema description prose (top-of-file) in both `architecture/build-checks.md` and `~/.claude/build-checks.md` to mention word-boundary semantics + the optional `Trigger anchors:` field. Add a prose-pin test asserting both files contain the literal substring `Trigger anchors`.

## Consequences

- **Eliminates the confirmed N=2 false-positive class** (slice-003 + slice-004 briefs no longer trigger BC-PROJ-2 / BC-GLOBAL-1). Future slices in adjacent regex-parsing / data-parsing / CLI-output domains stop generating defer-with-rationale ritual on BC-1 noise.
- **Backward-compatible** for any project that doesn't migrate its rules: rules without `Trigger anchors:` keep firing on any keyword match (with word-boundary). The substring → word-boundary tightening is non-controversial because no existing keyword vocabulary intends substring-only match — verified across all production rules (BC-PROJ-1 keywords `subagent, agent, fan-out, parallel, general-purpose, spawn, orchestrate`; BC-PROJ-2 keywords `parse, fence, code-block, backtick, llm, agent, prompt, output, response`; BC-GLOBAL-1 same plus `structured-output`) + all 8 fixture rules in `tests/methodology/fixtures/build_checks/` (e.g., `keyword_only.md` BC-PROJ-3 keywords `jwt, token, refresh, auth` against test text `"Rework JWT token refresh handling for the auth flow."` — bare-word `auth` word-boundary matches; `multi_rules.md` BC-PROJ-8 keywords `migration, schema, alembic` are bare-word). All keywords are bare-word vocabulary; no substring-only intent. Per Critic m2 (slice-005), this evidence is now cited inline rather than asserted abstractly. The existing 18-test regression-guard provides the automated check.
- **Adds one optional schema field** to the build-checks rule format. Schema description in both build-checks.md files must mention it (prose-pin test enforces). Authors don't need to use it — un-anchored rules behave with the current "any keyword match" semantic.
- **Adds one new parse-violation kind**: `anchor-not-in-keywords`. Mirrors how `missing-field` / `invalid-severity` are reported today. Doesn't change exit-code semantics (CLI still returns 1 on any violation; existing semantics).
- **Empirical-verification-at-design-time discipline ratchets to N=4 across slices** (slice-001's contract issue post-mortem, slice-003's argparse exit-code-2 lesson, slice-004's R-NN literal-match catch, this slice's word-boundary-doesn't-suffice-alone empirical realization). The cost of running `re.findall(rf"\b{kw}\b", text)` against the actual archive folders during /design-slice was ~30 seconds and ruled out Option 1 (word-boundary alone) before locking the design.
- **The `~/.claude/build-checks.md` edit is outside the repo.** The slice's git diff won't show this edit; build-log.md at T-final captures the before-after of that file as forensic evidence. Schema-pin test reads the file via `Path.home()` and degrades gracefully (pytest skip with reason) when the file isn't present in the test environment.
- **Future deferred work (not in this slice)**: morphological-variant expansion of trigger keyword vocabularies (e.g., adding `parses, parsed, parsing` to BC-PROJ-2 alongside `parse`). Today's bare-word + word-boundary semantic is sufficient for the N=2 false positives + the legitimate slice-001 case; morphological forms can be added incrementally as / when a future slice's brief mentions only the morphological variant without the bare anchor word.
- **Future deferred work (not in this slice)**: adding morphological variants to trigger_keywords for BC-PROJ-1 (e.g., `subagents` alongside `subagent`). Slice-001 mission-brief uses `subagent`=8 (singular) → BC-PROJ-1 fires today and continues to fire post-precision. No urgency; track if a future singular-only-mention slice surfaces.

## Reversibility

**cheap** — reverting to the previous behavior is a 5-line change in `_rule_applies` (replace word-boundary regex with substring `if kw in haystack`) plus removing the `trigger_anchors` field from `BuildCheckRule` (or simply ignoring it). The `Trigger anchors:` lines added to the three migrated rules can stay in the markdown — un-read by the un-precisioned audit, harmless. The schema-description prose updates can be left in place or reverted; either is cheap. Estimated revert cost: ~15 minutes.

The new schema field is additive — projects that author un-anchored rules continue to work without change. Removing the field would be a soft deprecation, not a breaking change. (For comparison: ADR-002's `--imports-allowlist` flag has the same posture — additive, deprecatable softly.)
