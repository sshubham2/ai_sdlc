---
id: ADR-011
title: BC-PROJ-2 negative-anchor migration completing BC-1 v1.2 rollout
date: 2026-05-13
slice: slice-012-bc-proj-2-negative-anchor-migration
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-011: BC-PROJ-2 negative-anchor migration completing BC-1 v1.2 rollout

## Context

Per [[ADR-007]] (BC-1 v1.2, slice-008, 2026-05-11), the BC-1 schema gained a per-rule optional `Negative anchors:` field acting as a **final filter** on positive applicability decisions across all three positive-applicability paths (`always: true` short-circuit / glob / keyword-anchor). Slice-008 migrated BC-PROJ-1 + BC-GLOBAL-1 with a 9-token methodology-vocabulary set (`defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync`), silencing the N=3 BC-1 false-positive class on methodology-vocabulary slices (slice-005 + slice-006 + slice-007).

Slice-008 explicitly **deferred BC-PROJ-2 migration to N=2 evidence** per Critic M1: at slice-008 time, BC-PROJ-2 had only N=1 false-positive recurrence (slice-005's bare-words `llm`, `code-block`). Slice-006 + slice-007 did NOT trigger BC-PROJ-2 because their `--changed-files` didn't match BC-PROJ-2's `Applies to: skills/**/*.py, tools/**/*.py` glob (per the rule's required subfolder structure). The N=1 evidence base did not meet BC-1's N=3 promotion threshold OR the slice-008 Critic-M1-specified BC-PROJ-2-specific N=2 threshold (deliberately lowered per Critic M1: "Defer BC-PROJ-2 migration until N=2 surfaces — i.e., a future slice modifying a file under `skills/**/*.py` or `tools/**/*.py` AND citing methodology-vocabulary anchors").

**N=2 evidence threshold MET at slice-011** (RSAD-1 codification slice, 2026-05-13): slice-011's mission-brief + design.md contain 26 BC-PROJ-2 positive-anchor matches (`fence`, `code-block`, `llm`, etc.) — sufficient to fire BC-PROJ-2 via the keyword-anchor path. The slice's text is heavy methodology-vocabulary content (47 negative-anchor matches if the migration were in place — but BC-PROJ-2 was un-migrated). Slice-011's `## Critic calibration` section + reflection record the BC-PROJ-2 fire at /critique-time as a defer-with-rationale disposition (third N=2 event per the slice-011 index entry: "BC-PROJ-2 negative-anchor migration N=2 evidence threshold MET (slice-005 + slice-011)").

The migration's intervention is **data-only** — BC-1 v1.2's schema + audit code (slice-008) supports the `Negative anchors:` field already. This slice populates the field for BC-PROJ-2 with the same 9-token set used for BC-PROJ-1 + BC-GLOBAL-1 (uniformity across BC-1 rules eliminates per-rule negative-anchor divergence; the methodology-vocabulary domain inversion is rule-agnostic). No schema change; no audit-code change.

A precision improvement is needed that:

1. Silences the confirmed N=2 false-positive class on BC-PROJ-2 (slice-005 + slice-011) without manual per-slice defer-with-rationale ritual.
2. Preserves slice-001 (canonical legitimate fence-parsing slice) firing BC-PROJ-2 — backward-compat covenant per ADR-007.
3. Stays backward-compatible — rules NOT yet migrated continue to behave with current applicability semantics (per ADR-004 / ADR-007 backward-compat covenants).
4. Composes correctly with BC-1 v1.2's algorithm-path-conformance (slice-005 lesson, N=2 stable post-slice-008): the new `Negative anchors:` line on BC-PROJ-2 must apply as final filter across ALL three positive-applicability paths uniformly.
5. Is reversible at low cost.

## Options considered

1. **Migrate BC-PROJ-2 with the same 9-token methodology-vocabulary set used for BC-PROJ-1 + BC-GLOBAL-1 (uniformity).**
   - Pros: rule-agnostic — methodology-vocabulary domain inversion applies uniformly to BC-PROJ-2 (which fires on `parse`/`fence`/`code-block`/`llm` positive anchors, just like BC-GLOBAL-1). Empirically curated against slice-001 baseline at slice-008 + re-verified against slice-001 + slice-005 + slice-011 at slice-012 design time (zero matches on slice-001; 7 + 47 matches respectively on slice-005 + slice-011 → suppression fires only where needed). Token disjointness with BC-PROJ-2's positive sets (`parse, fence, code-block, backtick, llm, agent, prompt, output, response` keywords + `fence, code-block, llm` anchors) verified Ø at design time. Zero divergence risk between BC-1 rules' negative-anchor curation. Future BC-1 v1.x refinements (e.g., morphological variants) apply uniformly.
   - Cons: none material. Curation list is revisable per-slice if over-suppression surfaces.
   - Verdict: chosen.

2. **Migrate BC-PROJ-2 with a BC-PROJ-2-specific (narrower) negative-anchor set.**
   - Pros: minimal blast radius — only the tokens empirically seen in slice-005 + slice-011 archives would be included.
   - Cons: per-rule divergence; future BC-1 v1.x refinements would have to apply per-rule rather than uniformly. Defeats slice-008's ratified uniformity design (Critic M1 ratification: "the domain inversion is rule-agnostic"). Adds maintenance burden — if a future methodology-vocabulary slice's text contains a token in BC-PROJ-1's negative set but not BC-PROJ-2's, BC-PROJ-2 fires false-positively while BC-PROJ-1 suppresses cleanly. Asymmetric.
   - Verdict: rejected — uniformity ratified at slice-008.

3. **Defer BC-PROJ-2 migration further (raise threshold to N=3 to align with original BC-1 promotion threshold).**
   - Pros: more evidence before locking.
   - Cons: slice-008 explicitly set the BC-PROJ-2-specific threshold at N=2 (Critic M1). N=2 is met. Deferring further would invalidate slice-008's deferral logic and require explicit policy override. Also: the noise is already happening (slice-005 + slice-011 dispositioned defer-with-rationale at /critique time); raising the threshold further compounds the noise.
   - Verdict: rejected — slice-008's N=2 threshold is met; defer-further is policy regression.

4. **Restrict BC-PROJ-2's `Applies to:` glob to a narrower pattern (e.g., remove `tools/**/*.py`) to reduce glob-path firings.**
   - Pros: zero new schema field; reuses existing `Applies to:` mechanism.
   - Cons: BC-PROJ-2's intent ("Use 4-backtick or longer outer fences when parsing LLM-emitted multi-block structured output") legitimately applies to `tools/**/*.py` — `tools.diagnose.write_pass.py` is the canonical example, and future tools that parse LLM output (audit tools, reflectors) belong here. Restricting the glob defeats this. Would also miss legitimate cases. Same rejection reason as ADR-007 Option 5.
   - Verdict: rejected — the glob's intent is correct; intervention at topic-exclusion level is the right design (and is already shipped at slice-008).

5. **Hardcode methodology-vocabulary suppression in `_rule_applies` with rule-ID conditionals.**
   - Pros: works without markdown edit.
   - Cons: not declarative; ad hoc; doesn't generalize; same rejection reason as ADR-007 Option 2 ("violates BC-1's own design principle — authors curate rules in markdown, not in audit code").
   - Verdict: rejected — slice-008 already adopted declarative `Negative anchors:` field.

## Decision

Adopt **Option 1**: migrate BC-PROJ-2 with the same 9-token methodology-vocabulary negative-anchor set used for BC-PROJ-1 + BC-GLOBAL-1 at slice-008. Edit is a single-line addition to BC-PROJ-2's rule body in `architecture/build-checks.md`:

```
**Negative anchors**: defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync
```

Append between BC-PROJ-2's existing `Trigger anchors:` line and the existing blank line before `**Check**:`. Mirrors BC-PROJ-1's structural shape exactly (per the `architecture/build-checks.md` BC-PROJ-1 rule body precedent at lines 18-21 post-slice-008).

**No code change** to `tools/build_checks_audit.py` — BC-1 v1.2 (slice-008) already parses `Negative anchors:`, applies the final-filter algorithm uniformly across all three positive-applicability paths, and emits `negative-anchor-overlaps-positive` parse violations on overlap. BC-PROJ-2's 9-token set is verified disjoint at design time (Audit 1, Ø intersection with `Trigger keywords` + `Trigger anchors`).

**No schema-prose change** to `architecture/build-checks.md` or `~/.claude/build-checks.md` — the `Negative-context anchors` paragraph (slice-008) at the top of both files already documents the mechanism. Slice-012 is rule-level data migration only.

**Methodology-changelog version bump v0.26.0 → v0.27.0** with PMI-1 atomic-version invariant maintained (in-repo `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all bump). New v0.27.0 entry names BC-PROJ-2 explicitly, the 9-token methodology-vocabulary set verbatim, AND the N=2 cross-slice evidence anchors (`slice-005` + `slice-011`).

## Consequences

- **Eliminates the confirmed N=2 false-positive class** on BC-PROJ-2 (slice-005 + slice-011 backtest scenarios). Future methodology-vocabulary slices modifying `skills/**/*.py` or `tools/**/*.py` AND citing methodology-meta vocabulary stop generating defer-with-rationale ritual.
- **Completes the BC-1 v1.2 rollout** — all three project-relevant BC-1 rules (BC-PROJ-1, BC-PROJ-2, BC-GLOBAL-1) now carry the uniform 9-token methodology-vocabulary negative-anchor set. Rule-level negative-anchor curation is symmetric across BC-1.
- **Backward-compatible** for slice-001 (canonical legitimate fence-parsing slice): empirical Audit 2 confirms zero matches of the 9 tokens in slice-001's mission-brief + design.md → negative-anchor filter cannot suppress → BC-PROJ-2 continues to fire. Backward-compat covenant per [[ADR-007]] preserved.
- **Backward-compatible** for un-migrated future BC-N rules (e.g., new BC rules added at future slices): such rules without the `Negative anchors:` field have empty `negative_anchors` tuple → `_negative_anchor_match` returns False → behavior identical to pre-slice-008 substring-anchors model. Per ADR-007 backward-compat covenant.
- **Zero schema change, zero audit-code change** — slice-008's BC-1 v1.2 infrastructure is reused verbatim. Slice-012's edit is one line in `architecture/build-checks.md` + bidirectional methodology-changelog entry + atomic version bump + 5 new tests + 1 PMI-1 versioned-gate supersession.
- **Empirical-verification-at-design-time discipline N=10 → N=11 ratchet** at slice-012 (added Audit 1 disjointness + Audit 2 slice-001 backward-compat + Audit 3 slice-005/011 suppression-fire prediction + Audit 4 algorithm-path-conformance trace + Audit 5 self-application over-determination = 5 design-time audits). All 5 predictions VALIDATED at design time; pre-empt build-time DEVIATIONs.
- **Validate-using-your-own-ship N=9 → N=10 ratchet** at slice-012 Phase 4 — the slice's own mission-brief + design.md will be audited against BC-PROJ-2 post-migration; per Audit 5, 9-of-9 negative-anchor tokens present in slice-012's artifacts → BC-PROJ-2 suppression is over-determined; cannot fail Phase 4 self-application audit even under arbitrary /critique fix prose additions or removals (per RSAD-1 build-time recursive-self-application sub-mode anticipation).
- **PMI-1 versioned-gate supersession N=4 → N=5 events ratchet** at slice-012 (slice-007 introduced `_at_0_22_0` → slice-008/009/010/011 superseded → slice-012 fifth-superseded with `_at_0_27_0`). Friction threshold N≥4 met at slice-011; per-bump cost remains ~1 min trivial; refactor candidate (`refactor-pmi-1-gate-to-version-agnostic-shape`) still deferable; defer one more cycle.
- **Slice-011 NEW Dim 9 sub-class candidate validation** (entry-pin-vs-PMI-1-gate-semantics-conflation, N=1 promoted from slice-011): slice-012 explicitly scopes the PMI-1 versioned-gate Edit `old_string` to ONLY the gate function body, NOT a wider section block. If slice-012 ships clean (v0.26.0 entry-pin function `test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed` preserved AND PMI-1 gate superseded), the discipline is empirically validated at N=2 — would meet promotion threshold for Dim 9 sub-class refinement at slice-013+.
- **Cross-cutting-conformance Dim 9 catch rate trajectory at slice-012**: 0% (slices 1-5) → 25% (slice-006) → 60% (slice-007) → 100% (slice-008) → 60% (slice-009) → 87.5% (slice-010) → 80% (slice-011) → ? (slice-012). Range-bound 60-100% on N=6 evidence stable; slice-012 is the first slice to exercise BC-PROJ-2's negative-anchor migration on the slice's own ship — Phase 4 result feeds the N=7 trajectory point.
- **Bidirectional sha256 forensic capture N=7 → N=8 ratchet** at slice-012 Phase 0 + Phase 4 (in-repo + installed `methodology-changelog.md`). `architecture/build-checks.md` is in-repo only; no installed counterpart for BC-PROJ-2 (BC-PROJ-2 is project-specific; BC-GLOBAL-1 in `~/.claude/build-checks.md` is the global-only rule).
- **Future deferred work** (not in this slice):
  - Morphological-variant expansion of negative anchors (`Critic-MISSED` / `critic-misses` / `Critic miss` variants) — still no recurrence at slice-011; defer to v2.
  - Per-keyword-vocabulary auto-promotion at `/critic-calibrate` — BC-1 v2 deferred from v0.10.0 release notes; out of scope.
  - Auto-detection of new false-positive classes by mining defer-with-rationale entries across recent reflections — out of scope.
  - `refactor-pmi-1-gate-to-version-agnostic-shape` — friction threshold N=4 met at slice-011, N=5 ratcheted at slice-012; per-bump cost remains trivial; defer one more cycle to slice-013+.
  - RSAD-1 v2 audit tooling (`tools/rsad_1_audit.py`) — deferred at slice-011.
  - MCT-1 v2 audit tooling (`tools/mct_1_audit.py`) — deferred at slice-010.

## Reversibility

**cheap** — reverting BC-PROJ-2 migration is:

1. Remove the single `**Negative anchors**: defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync` line from BC-PROJ-2's rule body in `architecture/build-checks.md` (1-line edit). The line can also be left in place harmlessly — un-migrated rules have empty `negative_anchors` tuple, but BC-PROJ-2 with the line populated behaves correctly under BC-1 v1.2; rollback to pre-slice-012 behavior requires actual line removal.
2. Delete the 4 new audit test functions: `test_slice_005_archive_no_longer_fires_proj2`, `test_slice_011_archive_no_longer_fires_proj2`, `test_slice_001_archive_still_fires_proj2`, `test_bc_proj_2_has_methodology_vocabulary_negative_anchors`.
3. Delete the 1 new entry-pin test (`test_v_0_27_0_bc_proj_2_entry_present_in_repo_and_installed`) ONLY. **Per /critique M1 ACCEPTED-FIXED**: prior versions' entry-pin functions (v0.22.0 / v0.23.0 / v0.24.0 / v0.25.0 / v0.26.0) are NOT touched — entry-pin functions persist across ALL versions; only PMI-1 versioned-gate tests supersede latest-only. Slice-011 NEW Dim 9 sub-class (N=1, entry-pin-vs-PMI-1-gate-semantics-conflation) explicitly distinguishes these two function classes. Also delete the `# --- Slice-012 / BC-PROJ-2 entry pinning ---` SECTION header introduced for this function.
4. Revert the PMI-1 versioned-gate supersession: rename `test_plugin_yaml_version_matches_version_file_at_0_27_0` back to `_at_0_26_0` + update internal assertion to `"0.26.0"` + revert the `# --- PMI-1 cleanliness gate at v0.27.0 ---` SECTION header back to v0.26.0. **Per /critique M1 ACCEPTED-FIXED**: the revert Edit targets ONLY the gate function body + its dedicated SECTION header — NOT any sibling entry-pin function or entry-pin SECTION header.
5. Remove the v0.27.0 entry from both `methodology-changelog.md` (in-repo) AND `~/.claude/methodology-changelog.md` (installed).
6. Revert atomic version bump: `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all 0.27.0 → 0.26.0.
7. Revert `architecture/shippability.md` row 12 deletion + row 11 PMI-1 versioned-gate supersession note edit.

Estimated revert cost: ~10 minutes (per slice-008 ADR-007 precedent: "~15 minutes" for 9 test functions + schema-prose + algorithm change; slice-012 is rule-level data migration only with no schema-prose / no algorithm change, so revert cost is lower).

The migration is **additive** — projects that don't migrate continue to work; projects that do migrate but later wish to revert can leave the markdown intact (`Negative anchors:` line becomes dead-but-correct data; audit reads it and applies the filter; if rollback to pre-migration applicability is needed, the line must be removed).

Per slice-011 RSAD-1 codification: BC-PROJ-2's curation list is rule-author-level lever (revisable per-slice by editing markdown). Future slices may tighten the list if over-suppression surfaces on a legitimate fence-parsing slice that uses one of the negative anchors in non-meta context — historical precedent: ADR-004 / ADR-007 both call out this revisability path.
