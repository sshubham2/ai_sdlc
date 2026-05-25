# Critique: Slice 032 add-query-design-skill

**Critic reviewed**: mission-brief.md, design.md, ADR-032 (verified against install_audit.py, plugin_manifest_audit.py, pipeline_chain_audit.py, cross_spec_parity_audit.py, test_install_audit.py, test_methodology_changelog.py, test_pipeline_position_block_drift.py, test_shippability_command_column.py, test_shippability_decoupling_audit.py, shippability.md, INSTALL.md, skills/status/SKILL.md)
**Date**: 2026-05-17
**Result**: NEEDS-FIXES
**Critic agent**: spawned via Agent tool, subagent_type=critique (two-persona separation preserved)

## Summary

Lockstep-site enumeration was materially incomplete: design missed the INSTALL.md hard-count prose, the SCMD-1 6-column shippability-row grammar contract, and the SCMD-1 decoupling classification of the new `Path.home()`-reading drift test. Plus a slice-022 self-violation — the read-only-discipline slice's own central AC4 was an undisciplined manual dry-run with no pass/fail predicate. 7/8 findings ACCEPTED-FIXED at this step; m2 OVERRIDDEN with verified evidence.

## Findings

### Blockers (must address before /build-slice)

#### B1: New shippability row must satisfy SCMD-1 6-column Machine-cmd grammar
- **Claim under review**: design.md "One new shippability catalog row … with SCMD-1 Machine-cmd column"
- **Issue**: shippability.md is a 6-column table (verified L7); `test_shippability_command_column.py` + `test_shippability_decoupling_audit.py` assert ZERO violations on EVERY row and derive the cited-fn set from every `Machine-cmd` cell. The design treated the column as an addendum, never stated the prose-free `_SEGMENT_RE` grammar.
- **Evidence**: shippability.md L7-8; test_shippability_command_column.py L28-38; test_shippability_decoupling_audit.py L50-61
- **Proposed fix**: specify the exact 6-cell row + prose-free interpreter-anchored `Machine-cmd`; add decoupling-audit to mid-slice gate.
- **Builder draft**: ACCEPTED-FIXED — design.md new section "Shippability row grammar (SCMD-1)" specifies the exact 6-cell row + `Machine-cmd` invocation; mission-brief mid-slice gate + must-not-defer updated.

#### B2: New drift test reads `Path.home()` — SCMD-1 decoupling audit may classify it incidental/coupled
- **Claim under review**: design.md "test_query_design_skill_drift.py … mirroring test_slice_skill_drift.py"
- **Issue**: copying the `Path.home()` per-file drift pattern without verifying WHY existing such tests are SCMD-1-clean is exactly the "audit's own parse rules are a design-stage blind spot" lesson (N+3). Once cited in the new row (B1), the exemption assumption becomes load-bearing and unverified.
- **Evidence**: test_slice_skill_drift.py L53-54; test_shippability_decoupling_audit.py L213-222, L50-61
- **Proposed fix**: state the verified exemption predicate before writing the test; gate at mid-slice smoke.
- **Builder draft**: ACCEPTED-FIXED — design.md new section "SCMD-1 decoupling classification of the new drift test" makes the `& $PY -m tools.shippability_decoupling_audit` inspection a build-time prerequisite gated at mid-slice smoke; allowlist-edit ruled out of scope.

#### B3: AC4 not deterministically verifiable — slice-022 self-violation
- **Claim under review**: mission-brief AC4 + verification row 4 ("dry-run /query-design …")
- **Issue**: the slice whose value prop is disciplined grounded behavior defined its own central AC as an LLM-output dry-run with no pass/fail predicate; pre-finish "all 5 ACs PASS with evidence" cannot be mechanically met for AC4. Textbook slice-022 self-violation (N≈8).
- **Evidence**: mission-brief AC4; aggregated lessons "slice-022 self-violation law N≈8"
- **Proposed fix**: convert AC4 to a deterministic SKILL.md-prose structural pin (`tests/methodology/test_query_design_skill.py`).
- **Builder draft**: ACCEPTED-FIXED — AC4 reworked to a deterministic pytest prose-pin (grounding + delegation + 3 error-model clauses); design.md What's new + wiring matrix add `test_query_design_skill.py`; manual dry-run retained as non-gating sanity note only.

### Majors (address this slice)

#### M1: INSTALL.md hard-codes "24 skills" — silent prose drift, not test-pinned
- **Issue**: INSTALL.md:185 hard-codes the canonical inventory counts; adding query-design makes it 25; no audit pins it (`test_install_audit.py` asserts only substrings).
- **Evidence**: INSTALL.md:185; test_install_audit.py L249-262
- **Proposed fix**: add INSTALL.md to What's modified; prefer count-agnostic phrasing (slice-027 lesson); explicit checklist item.
- **Builder draft**: ACCEPTED-FIXED — design.md What's modified += INSTALL.md (count-agnostic rewrite, also retires pre-existing stale "13 tool modules"); mission-brief must-not-defer adds the explicit ungated-prose checklist item.

#### M2: Read-only invariant ignores platform-native `allowed-tools` frontmatter
- **Issue**: official skills spec supports `allowed-tools`; design enforces read-only via prose only (advisory). Critic's own fallback: if existing skills deliberately don't use it, document the decision.
- **Evidence**: Claude Code Skills docs; ADR-032 Consequences
- **Builder draft**: ACCEPTED-FIXED (documented-decision path) — VERIFIED: `grep -rl allowed-tools skills/` → 0; no skill in this repo uses it (incl. read-only /status, /diagnose, /drift-check); skills run inline in the main thread via Skill tool, not as restricted plugin subagents where `allowed-tools` semantics apply. Adding it for query-design alone = unprecedented divergent mechanism of unverified inline-path efficacy. ADR-032 Consequences + design.md now record this as an examined, deliberate choice (prose + QD-1 + drift test), with a superseding-ADR path if the platform later honors it inline.

#### M3: PCA-1 out-of-loop safety asserted by analogy, not verified mechanism
- **Issue**: conclusion correct but design said "parallels /status…" instead of the verified iteration boundary; Builder might defensively add a block.
- **Evidence**: pipeline_chain_audit.py L200; test_pipeline_position_block_drift.py L31
- **Builder draft**: ACCEPTED-FIXED — design.md replaces the analogy with the verified mechanism (`audit()` iterates `_CANONICAL_CHAIN` only; `_SKILLS` derived from it) + explicit "Builder MUST NOT add a `## Pipeline position` block"; mirrored in mission-brief must-not-defer.

### Minors (log; address if cheap)

#### m1: QD-1 is prose-only — entry-pin test pattern not enumerated
- **Builder draft**: ACCEPTED-FIXED — design.md "Changelog entry note" states QD-1 is prose-only; generic gates cover it; no bespoke `test_v_0_46_0_*` pin added (over-build is the failure mode).

#### m2: ADR-032 `supersedes: null` sentinel convention
- **Builder draft**: OVERRIDDEN — VERIFIED: most recent ADR (ADR-031, header L8) uses exactly `supersedes: null`; ADR-032 already conforms; SUP-1 (`tools/supersede_audit.py`) parses this sentinel. No change needed. Rationale: empirically confirmed against the most recent ADR header — the flagged risk does not exist.

## Dimensions checked
- [x] Unfounded assumptions — B2, M3
- [x] Missing edge cases — B1, B2
- [x] Over-engineering — none (thin-vault respected; correctly declined _CANONICAL_TOOLS membership)
- [x] Under-engineering — B3, M2
- [x] Contract gaps — M2
- [x] Security — M2 (read-only is the slice's security boundary; no auth/secrets/injection surface)
- [x] Drift from vault — M1, m2
- [x] Web-known issues — M2 (`allowed-tools` frontmatter, official spec)
- [x] Cross-cutting conformance — B1/B2 (SCMD-1 grammar+decoupling), B3 (slice-022 self-violation), M1 (unguarded INSTALL.md prose). Lockstep completeness: design covered _CANONICAL_SKILLS+plugin.yaml+VERSION+changelog+drift test+PMI-1/INST-1; MISSED INSTALL.md prose, SCMD-1 row grammar, SCMD-1 decoupling classification — all now fixed.

## Triage

**Triaged by**: user
**Date**: 2026-05-17
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md "Shippability row grammar (SCMD-1)" section — exact 6-cell row + prose-free interpreter-anchored Machine-cmd; mid-slice gate + must-not-defer updated |
| B2 | Blocker | ACCEPTED-FIXED | design.md "SCMD-1 decoupling classification" section — decoupling-audit verification a build-time prereq gated at mid-slice; meta-Critic empirically confirmed clean (0 incidental, 0 violations) |
| B3 | Blocker | ACCEPTED-FIXED | AC4 reworked to deterministic `test_query_design_skill.py` prose-pin; manual dry-run demoted non-gating; meta-Critic confirmed not slice-022 theater (prose IS the executed artifact) |
| M1 | Major | ACCEPTED-FIXED | INSTALL.md count-agnostic rewrite; scope broadened by M-add-1 to all three sites |
| M2 | Major | ACCEPTED-FIXED | Documented-decision: verified 0 repo skills use `allowed-tools`; skills run inline (not restricted plugin subagents); ADR-032 Consequences records examined choice + superseding-ADR path |
| M3 | Major | ACCEPTED-FIXED | design.md replaced analogy with verified iteration boundary (`pipeline_chain_audit` L200 / `_SKILLS` L31) + "Builder MUST NOT add Pipeline position block" |
| m1 | Minor | ACCEPTED-FIXED | design.md "Changelog entry note" — QD-1 prose-only, generic gates cover it, no bespoke `test_v_0_46_0` pin (over-build is the failure mode) |
| m2 | Minor | OVERRIDDEN | Verified: most recent ADR (ADR-031 header L8) uses identical `supersedes: null`; ADR-032 already conforms; SUP-1 parses the sentinel — the flagged convention risk does not exist |
| M-add-1 | Major | ACCEPTED-FIXED | critique-review missed-finding: INSTALL.md hard-codes count at 3 sites (L19/L185/L218), not 1; design "What's modified" + mission-brief must-not-defer broadened to all three + pre-finish stale-count grep guard added |

> Dual-review (DR-1) verdict: **EXTEND** — see [critique-review.md](critique-review.md). M-add-1 reconciled into this table per the meta-Critic's missed-finding. 0 suspicious, 0 severity adjustments.

### Triage — v2 delta (DEVIATION-1 re-critique; user-ratified 2026-05-17)

Triggered at `/build-slice` plan-mode design-is-wrong gate (user chose "correct design + re-run /critique on delta"). v1 rows above are unchanged. Delta artifacts: [critique-v2.md](critique-v2.md) + [critique-review-v2.md](critique-review-v2.md). v2 dual-review verdict: **EXTEND**.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1-v2 | Major | ACCEPTED-FIXED | "mirrors scmd_1" specified 2 of scmd_1's 4 assertions (slice-022 self-violation in the correction). design.md "Exact pin shape" now specifies full 4-assertion per-surface list + `_V046`/`_QD1_PHRASE` constant pair + `_extract_version_body` body-scoping + `ADR-032` lineage |
| M2-v2 | Major | ACCEPTED-FIXED | QD-1 is a minted rule-ID → rule-ID-BEARING bci_1/scmd_1 shape, NOT rule-ID-less v0.43.0 (which asserts "no rule-ID", actively wrong). design.md states this explicitly + MUST-NOT assert "no rule-ID" prose |
| m1-v2 | Minor | ACCEPTED-FIXED | v0.46.0 entry must be format-conformant (`### Added`+Rule reference+Defect class+Validation); only Rule reference generically gated. mission-brief must-not-defer adds the item |
| M-add-v2-1 | Major | ACCEPTED-FIXED | (critique-review-v2 missed-finding) the M1-v2 fix made `_QD1_PHRASE` an N≥3 obligation but pinned only the changelog body — SKILL.md occurrence unguarded (silent-prose-drift class, N=2 of v1 M-add-1). Fixed: pin reduced to exactly 2 test-pinned sites; `test_query_design_skill.py` now asserts `_QD1_PHRASE` in SKILL.md; N≥2-vs-3 inconsistency corrected |

**v2 final verdict**: all dispositions ACCEPTED-FIXED (no ESCALATED, no ACCEPTED-PENDING) → **CLEAN**. Combined slice verdict (v1 CLEAN + v2 CLEAN) → **CLEAN**.
