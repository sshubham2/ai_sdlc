---
id: ADR-007
title: BC-1 negative-context anchors via final-filter Negative anchors per-rule field
date: 2026-05-10
slice: slice-008-refine-bc-1-anchors-with-negative-context
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-007: BC-1 negative-context anchors via final-filter `Negative anchors:` per-rule field

## Context

Per BC-1 v1.1 / [[ADR-004]] (slice-005, 2026-05-10), the BC-1 keyword-applicability mechanism uses case-insensitive word-boundary regex matching plus an optional `Trigger anchors:` per-rule field that requires ≥1 anchor (subset of `Trigger keywords`) to match for the rule to fire on the keyword path. This silenced the original N=2 BC-1 false-positive class on substring-of-longer-word matches (slice-003 + slice-004's `parse_declared_deps`).

A new false-positive class has now reached the BC-1 promotion threshold (N=3) per slice-007 reflection (2026-05-10): **methodology-vocabulary slices that discuss BC-1 / agents / fences as the slice's TOPIC trigger BC-PROJ-1 + BC-GLOBAL-1 false-positively**. Confirmed recurrences:

- **slice-005** (2026-05-10) — keyword-path: bare-words `subagent`, `fan-out`, `fence`, `code-block`, `llm` all match because slice-005's mission-brief literally enumerates these as anchor terms in the BC-1 schema.
- **slice-006** (2026-05-10) — keyword-path on BC-PROJ-1 (`subagent` matches; CCC-1 9th-dimension prose discusses subagent fan-out as a Critic dimension); glob-path on BC-GLOBAL-1 (changed `agents/critique.md`; `Applies to: **` matches everything when --changed-files non-empty).
- **slice-007** (2026-05-10) — glob-path on both BC-PROJ-1 (`agents/**/*.md` matches `agents/critique.md` modifications) and BC-GLOBAL-1 (`**` matches).

In all three slices, the slice's actual TOPIC is the methodology rule itself, not the rule's domain (subagent fan-out implementation, LLM-fence parsing implementation). Each slice deferred-with-rationale per BC-1 v0.10.0 contract — the disposition is correct, but the ritual is noise. Per the BC-1 rationale ("Recurring patterns silently re-surface across slices..."), the noise trains the builder to ignore BC-1 surfacing — which defeats the lessons-learned-to-builder-feedback-loop the rule exists to close.

Critically, **slice-005's `Trigger anchors:` mechanism only filters the keyword path**; the glob path (`Applies to:` patterns) and the `always: true` short-circuit still fire regardless. This is the slice-005 algorithm-path-conformance lesson generalized: "When the design adds a new branch to existing logic, trace through ALL pre-existing branches." Slice-005's tightening was necessary but insufficient — it covered the keyword path that surfaced in slice-003/004's substring-match precedent, but not the glob-path firings that surface in slice-006/007's --changed-files scenarios.

A precision improvement is needed that:

1. Silences the confirmed N=3 false positives without manual per-slice defer-with-rationale ritual.
2. Composes correctly with ALL three positive-applicability paths (`always: true`, glob, keyword) per the slice-005 algorithm-path-conformance lesson.
3. Preserves legitimate matches (slice-001's mission-brief + design MUST continue to fire BC-PROJ-1 + BC-PROJ-2 + BC-GLOBAL-1; slice-001 is the canonical legitimate slice for both rules).
4. Stays backward-compatible — un-migrated rules continue to behave with current applicability semantics (per ADR-004 backward-compat covenant).
5. Is reversible at low cost.

## Options considered

1. **Refine existing `Trigger anchors:` of BC-PROJ-1 + BC-GLOBAL-1 to be more discriminating** (option (a) from slice-007 deferred description).
   - Pros: zero schema change.
   - Cons: empirically insufficient. The methodology-vocabulary slices use the SAME positive-anchor terms (`subagent`, `fence`, `code-block`, `llm`) as legitimate fence-parsing slices — they're literally enumerating the rule's anchor vocabulary. There is no positive-anchor refinement that discriminates "discussing the rule" from "implementing the rule's domain." Verdict: rejected — root cause is that positive anchors alone cannot capture topic exclusion.

2. **Hardcode a methodology-vocabulary suppression list inside `_rule_applies` with rule-ID conditionals** (option (a) variant).
   - Pros: works for the 3 known rules.
   - Cons: not declarative; ad hoc; doesn't generalize to future rules; requires audit-code edits for future BC-N rules. Verdict: rejected — violates BC-1's own design principle ("authors curate rules in markdown, not in audit code").

3. **Add a per-rule `Negative anchors:` schema field with case-insensitive word-boundary semantics; act as final filter on positive applicability decisions** (option (b) from slice-007 deferred description).
   - Pros: declarative; backward-compatible; mirrors slice-005's `Trigger anchors:` shape (same parsing + word-boundary semantic; just suppressive instead of inclusionary); composes uniformly across all three positive-applicability paths; generalizes to future BC-N rules.
   - Cons: schema change (one new optional field) + per-rule curation (one-time cost, manual). Risk of over-suppression if anchors are too broad — mitigated by the empirical-curation discipline (test against slice-001 baseline).
   - Verdict: chosen.

4. **Per-keyword negative-context (e.g., `parse: {requires: domain-keyword}`)** (option (a) variant from ADR-004's option 5).
   - Pros: maximal precision per keyword.
   - Cons: same schema-explosion concern flagged in ADR-004; v1 over-engineering.
   - Verdict: rejected — same intent achieved more cleanly by rule-level negative anchors.

5. **Move BC-GLOBAL-1's `Applies to: **` back to a more restrictive pattern (e.g., `Applies to: skills/**/*.py, tools/**/*.py`)** to reduce glob-path firings.
   - Pros: zero new schema field; reuses existing `Applies to:` mechanism.
   - Cons: BC-GLOBAL-1's intent (per slice-005 DEVIATION-1 rationale) is "fires on every real /build-slice with --changed-files" — restricting the glob defeats this. Would also miss legitimate cases (e.g., a slice that adds Python parsers in non-conventional paths). Verdict: rejected — the glob's intent is correct; the right intervention is at topic-exclusion level, not file-pattern level.

6. **Promote BC-1 false-positive class to a "BC-N defer-rationale auto-supply" mechanism** (auto-generate the defer-with-rationale prose at /build-slice when BC-1 fires false-positively on methodology-vocabulary slices).
   - Pros: lossless (no rules silenced; just less ritual).
   - Cons: requires LLM judgement at build time to decide what's "methodology-vocabulary"; introduces an auto-explanation that could be wrong; doesn't fundamentally reduce the noise floor (BC-1 still surfaces, just with auto-prose).
   - Verdict: rejected — over-engineered for the noise level; lossless precision improvement (option 3) is simpler.

## Decision

Adopt **Option 3**: extend BC-1 schema with a per-rule optional `Negative anchors:` field (case-insensitive, word-boundary semantics, comma-separated tokens) acting as a **final filter** on positive applicability decisions. The new mechanism applies UNIFORMLY across all three positive-applicability paths:

```python
def _negative_anchor_match(rule, slice_text):
    if not rule.negative_anchors or not slice_text:
        return False
    haystack = slice_text.lower()
    return any(re.search(rf"\b{re.escape(na)}\b", haystack) for na in rule.negative_anchors)


# In _rule_applies, every existing positive-return branch is wrapped:
if rule.applies_to == ("always",):
    return not _negative_anchor_match(rule, slice_text)

for pattern in rule.applies_to:
    for changed in changed_files:
        if _matches_glob(changed, pattern):
            return not _negative_anchor_match(rule, slice_text)

# (keyword path's existing positive-decision similarly wrapped)
```

Migrate **BC-PROJ-1 and BC-GLOBAL-1** with the same 9-token negative-anchor list (the domain inversion is rule-agnostic):

```
**Negative anchors**: defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync
```

**BC-PROJ-2 is NOT migrated in this slice** (per Critic M1 dispositional ratification). Empirical evidence shows BC-PROJ-2 fires false-positively only on slice-005 (N=1; the original BC-1 anchors-precision slice). Slice-006 + slice-007 do NOT trigger BC-PROJ-2 because their changed-files don't match the rule's `Applies to: skills/**/*.py, tools/**/*.py` glob (per the glob's required subfolder structure). N=1 does NOT meet the BC-1 promotion threshold (N=3 per slice-007 reflection's promotion convention used by this same slice). Defer BC-PROJ-2 migration until N=2 surfaces in a future slice.

Add a new parse-violation kind `negative-anchor-overlaps-positive` for rules whose negative anchors overlap with `Trigger keywords` OR `Trigger anchors` — overlap is contradictory (the rule would never fire when its keyword/anchor is present, defeating the rule's domain). Mirrors slice-005's `anchor-not-in-keywords`.

Update schema-description prose (top-of-file) in both `architecture/build-checks.md` AND `~/.claude/build-checks.md` to mention the `Negative anchors:` field semantics + the universal "final filter" framing. Add a prose-pin test asserting both files contain the literal substring `Negative anchors`.

## Consequences

- **Eliminates the confirmed N=3 false-positive class** (slice-005, slice-006, slice-007 backtest + build-time scenarios). Future methodology-vocabulary slices stop generating defer-with-rationale ritual on BC-PROJ-1 + BC-GLOBAL-1.
- **Extends noise reduction to slice-003 BC-GLOBAL-1 build-time** (slice-003 contains `defer-with-rationale, aggregated lessons` — both negative anchors). This is desirable per slice-005's noise-reduction rationale; the existing slice-003 test `test_slice_003_archive_backtest_no_bc_proj_2_or_global_1_applications` is unaffected (it asserts BC-PROJ-2 + BC-GLOBAL-1 NOT in applicable, which is the post-slice-008 behavior on the keyword path; slice-005's anchors filter already blocks).
- **Backward-compatible** for un-migrated rules: rules without `Negative anchors:` field have empty `negative_anchors` tuple; `_negative_anchor_match` returns False; behavior identical to pre-slice-008. The substring -> word-boundary tightening from slice-005 is preserved.
- **Adds one optional schema field**. Authors don't need to use it. The schema description in both build-checks.md files mentions it (prose-pin test enforces).
- **Adds one new parse-violation kind** (`negative-anchor-overlaps-positive`). Mirrors `missing-field` / `invalid-severity` / `anchor-not-in-keywords` reporting. Doesn't change exit-code semantics.
- **Empirical-verification-at-design-time discipline ratchets to N=7 across slices** (added slice-008's empirical curation against slice-001..007 baseline, including running the audit with representative `--changed-files` to surface glob-path firings that the keyword-only backtest mode misses).
- **The `~/.claude/build-checks.md` edit is outside the repo** — same posture as slice-005 + slice-006 + slice-007. Bidirectional sha256 forensic capture in `build-log.md` per the N=2 stable lesson; the slice's git diff alone is insufficient evidence.
- **Methodology-changelog version bump** (v0.22.0 -> v0.23.0) with PMI-1 atomic-version invariant maintained (in-repo `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all bump to 0.23.0).
- **Future deferred work (not in this slice)**: morphological-variant expansion of negative anchors (`Critic-MISSED` / `critic-misses` / `Critic miss` variants); per-keyword-vocabulary auto-promotion at /critic-calibrate; auto-detection of new false-positive classes by mining defer-with-rationale entries across recent reflections. All deferred until a recurring noise pattern justifies the v2 lift.
- **Future deferred work (not in this slice; per Critic M1 dispositional ratification)**: BC-PROJ-2 migration when N=2 surfaces. Today: BC-PROJ-2 has N=1 false-positive recurrence (slice-005 only — keyword-path on bare-words `llm`, `code-block`); slice-006 + slice-007 BC-PROJ-2 status is `skipped` because their changed-files don't match the rule's `Applies to: skills/**/*.py, tools/**/*.py` glob. Promote at the BC-1 N=3 threshold (or earlier if a future slice's --changed-files match BC-PROJ-2's glob AND the slice's text cites methodology-vocabulary anchors; that would be N=2).

## Reversibility

**cheap** — reverting to pre-slice-008 behavior is:

1. Revert `_rule_applies` to its slice-005 form (~5-line change: remove the `_negative_anchor_match` wrapping of every positive-return branch).
2. Remove `negative_anchors` field from `BuildCheckRule` dataclass + `to_dict()` (or simply leave it unread; harmless).
3. Remove `_parse_rules` parsing of `**Negative anchors**:` field + `negative-anchor-overlaps-positive` violation emission (~10 lines).
4. Remove the schema-prelude TWO sentences (field-name + final-filter semantic) from both `architecture/build-checks.md` + `~/.claude/build-checks.md` plus the cross-project-applicability sentence in `~/.claude/build-checks.md` (~5 lines each file).
5. Remove `**Negative anchors**:` field lines from BC-PROJ-1 + BC-GLOBAL-1 (~3 lines each; can also be left in place — un-read by the un-extended audit, harmless). Note: BC-PROJ-2 is NOT migrated in this slice per Critic M1, so no rollback needed there.
6. Delete the 4 new test functions added at /critique-time (`test_slice_005..007_archive_no_longer_fires_proj1_or_global1`, `test_slice_001_archive_still_fires_legitimate_rules`, `test_negative_anchors_schema_documents_*` × 2, `test_negative_anchor_overlaps_positive_yields_violation`, `test_migrated_rules_have_expected_negative_anchors`, `test_always_true_rule_with_negative_anchor_match_is_skipped`) — 9 tests total per the post-Critic TF-1 plan.

Estimated revert cost: ~30 minutes (per Critic m2 — original "~15 minutes" estimate understated the test-cleanup cost; 9 test functions to delete or rollback). Backward-compat is preserved either way: projects that don't migrate continue to work; projects that do migrate but later wish to revert can leave the markdown intact.

The new schema field is **additive** — projects that author un-curated rules continue to work without change. Removing the field would be a soft deprecation (markdown stays valid; field becomes unread), not a breaking change. Same posture as slice-005's `Trigger anchors:` field (per ADR-004 reversibility).

The negative-anchor curation list is **revisable per-slice** — if a future slice surfaces over-suppression (e.g., a legitimate fence-parsing slice that uses one of the negative anchors in non-meta context), the curation list can be tightened by editing the rule's markdown without touching audit code or schema. This is intentionally a rule-author-level lever, not a schema-author-level decision.
