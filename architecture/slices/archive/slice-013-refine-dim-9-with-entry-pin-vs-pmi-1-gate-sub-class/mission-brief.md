# Slice 013: refine-dim-9-with-entry-pin-vs-pmi-1-gate-sub-class

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: MEDIUM — closes the entry-pin-vs-PMI-1-gate-semantics-conflation miss sub-class at promotion threshold N=2 (slice-011 N=1 surfaced at /validate-slice Step 5.5 by shippability catalog row 10 fail; slice-012 N=2 codification + empirical /design-slice + /critique + /build-slice validation via Phase 1b INSERT under NEW SECTION header + Phase 1c narrow-scope Edit + Audit 6 structural-separation pre-Edit + post-build empirical confirmation that v0.22.0..v0.26.0 entry-pin functions ALL preserved through PMI-1 supersession). The current Dim 9 sub-clauses (6 after slice-011's RSAD-1 codification) do NOT cover the Edit-scoping semantics distinction between PERSISTENT entry-pin functions (one per shipped versioned changelog entry; never deleted) and SUPERSEDABLE PMI-1 versioned-gate functions (one at a time only; replaced per slice-007 PMI-1 escape-closure pattern). Slice-013 adds a new **7th** Dim 9 sub-clause encoding this discipline as an /critique-time + /build-slice-time prose-heuristic, mirroring slice-011's RSAD-1 codification pattern.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Extend `agents/critique.md` Dimension 9 with a new **7th sub-clause** titled "Entry-pin-vs-PMI-1-gate semantics conflation" (canonical literal), placed BETWEEN the existing 6th sub-clause "Recursive self-application discipline" and the existing `### Bonus: weak graph edges` H3 — preserving the cross-clause topology (3 cross-references to Dim 1/4 surgical sub-bullets + 2 N=1 standalone sub-clauses + 1 N=3 meta-level sub-clause + 1 NEW N=2 Edit-scoping discipline sub-clause). The sub-clause encodes the Edit-discipline lesson from slice-011 (N=1) + slice-012 (N=2): **when superseding a PMI-1 versioned-gate test, the Edit `old_string` should target ONLY the gate function body + its dedicated SECTION header; never span entry-pin functions for the same or prior versions**. Two cross-slice example anchors per the slice-009/010/011 N=2 promotion convention (slice-011 build-time slip + slice-012 design-time-pre-empted success). Rule reference **EPGD-1** (Entry-Pin-Gate-Discipline; /critique-time adversarial-prompt + /build-slice-time Edit-discipline; -D suffix per slice-011 RSAD-1 -D-suffix N=2 stable confirmation — locked at /design-slice per ADR-012). Authored as a NEW rule per slice-011 precedent (RSAD-1 was its own rule at N=3 introduction), NOT as CCC-1 v1.2 (which would imply inline refinement of an existing sub-clause body per slice-009 v1.1 pattern). Per slice-012 reflection's "From slice-012 second-strongest candidate" guidance.

## Acceptance criteria

1. After this slice ships, `agents/critique.md` Dimension 9 enumerates a new **7th sub-clause** with canonical literal title `Entry-pin-vs-PMI-1-gate semantics conflation` positioned BETWEEN the existing 6th sub-clause `Recursive self-application discipline` AND the existing `### Bonus: weak graph edges` H3. The 7-sub-clause structural invariant test (`test_critique_dim_9_lists_seven_sub_clauses`) supersedes the prior 6-sub-clause invariant (`test_critique_dim_9_lists_six_sub_clauses`) per slice-011 PMI-1 structural-invariant supersession discipline (no two structural-invariant tests coexist; same supersession pattern at the prose-structure level).
2. After this slice ships, the new 7th sub-clause body carries TWO concrete cross-slice example anchors grounded in the project's reflection record. **Cross-slice anchors (strict-both)**: `["slice-011", "slice-012"]` — both MUST be present in the 7th sub-clause body. **Substantive-discipline anchors (≥2 of 4)**: `["Phase 1b INSERT", "Phase 1c narrow-scope Edit", "Audit 6 structural-separation", "SECTION header"]` — at least 2 of these 4 MUST be present in the 7th sub-clause body. Anchor list semantics formalized per slice-011 `_cites_at_least_two_cross_slice_anchors` precedent (post-M2 ACCEPTED-FIXED at /critique). Contextual narrative: slice-011 N=1 build-time slip (Edit's `old_string` spanned both the v0.25.0 entry-pin function AND the PMI-1 versioned-gate function via shared SECTION header; entry-pin silently deleted; caught at /validate-slice Step 5.5 by shippability catalog row 10 fail); slice-012 N=2 design-time-pre-empted success (Phase 1b INSERT under a NEW dedicated SECTION header + Phase 1c narrow-scope Edit on gate function body + dedicated SECTION header only + Audit 6 structural-separation empirical verification pre-Edit; all v0.22.0..v0.26.0 entry-pin functions preserved post-build). All anchor pins are case-sensitive literal substrings.
3. After this slice ships, `python -m tools.critique_agent_drift_audit --repo-root . --claude-dir $HOME/.claude` exits 0 (sha256 byte-equality holds between in-repo `agents/critique.md` and `~/.claude/agents/critique.md`). CAD-1 confirms forward-sync atomicity at slice end.
4. After this slice ships, `methodology-changelog.md` (BOTH in-repo at `methodology-changelog.md` AND installed at `~/.claude/methodology-changelog.md`) contains a new `## v0.28.0 — <YYYY-MM-DD>` entry naming **EPGD-1** as the new rule reference. The entry's Validation section names this slice's new tests AND the bidirectional changelog-pin test (`test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed`). N-surface schema-pin discipline (corrected per M3 ACCEPTED-FIXED at /critique): substantive canonical phrase `Entry-pin-vs-PMI-1-gate semantics conflation` pinned across **N=3 surfaces** (agents/critique.md Dim 9 7th sub-clause title + in-repo `methodology-changelog.md` v0.28.0 entry + installed `~/.claude/methodology-changelog.md` v0.28.0 entry) per slice-011 RSAD-1 3-surface schema-pin precedent. The 3-surface shape ratchets to N=2 instances stable at slice-013 (slice-011 RSAD-1 + slice-013 EPGD-1).
5. PMI-1 invariant atomic post-build: `VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` (installed) + `plugin.yaml.version` all equal `0.28.0`. Verified via `python -m tools.plugin_manifest_audit --root .` exit 0 AND `test_plugin_yaml_version_matches_version_file_at_0_28_0` PASSING (supersedes slice-012's `_at_0_27_0` PMI-1 versioned-gate per the N=5-events-stable supersession pattern from slice-007..012 — slice-013 ratchets to N=6 events). **The PMI-1 supersession Edit at /build-slice MUST narrow-scope to the gate function body + its dedicated `# --- PMI-1 cleanliness gate at v0.27.0 ---` SECTION header ONLY** (per the very EPGD-1 discipline this slice authors — slice's own ship is the canonical reference instance per RSAD-1 / slice-011 precedent).

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0)

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING -> PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_entry_pin_vs_pmi_1_gate_sub_clause_present | PASSING |
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_entry_pin_vs_pmi_1_gate_location_pinned | PASSING |
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_lists_seven_sub_clauses | PASSING |
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_recursive_self_application_sub_clause_present | PASSING |
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_recursive_self_application_names_both_sub_modes | PASSING |
| 1 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_entry_pin_vs_pmi_1_gate_names_both_sub_modes | PASSING |
| 2 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_entry_pin_pmi_1_paragraph_cites_slice_011_and_012 | PASSING |
| 2 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_recursive_self_application_cites_at_least_two_cross_slice_anchors | PASSING |
| 2 | unit | tests/methodology/test_critique_agent.py | test_critique_dim_9_entry_pin_vs_pmi_1_gate_cites_at_least_two_cross_slice_anchors | PASSING |
| 3 | integration | tests/methodology/test_critique_agent_drift.py | test_in_repo_and_installed_critique_agent_are_content_equal | PASSING |
| 4 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed | PASSING |
| 5 | unit | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_at_0_28_0 | PASSING |

**Notes**:
- TF-1 PENDING -> WRITTEN-FAILING transitions MUST be genuine per slice-003..012 lesson N=9 stable. Pin specific failure signals:
  - AC #1 row 1: fails pre-fix with `AssertionError: 'Entry-pin-vs-PMI-1-gate semantics conflation' not in CRITIQUE` (canonical literal title not yet present in Dim 9).
  - AC #1 row 2 (location-pin): fails pre-fix because the sub-clause title is absent; pre-fix `text.find()` returns -1. Anchor uniqueness pre-verified at /design-slice (slice-009 DEVIATION-2 pre-emption — verify "Recursive self-application discipline" + "### Bonus: weak graph edges" each appear exactly once in critique.md before AC-lock).
  - AC #1 row 3 (structural invariant supersession): fails pre-fix because Dim 9 still enumerates 6 sub-clauses, not 7 — new sub-clause's canonical title not yet in the assert list. Supersedes `test_critique_dim_9_lists_six_sub_clauses` per slice-011 supersession discipline; the OLD function is DELETED in the same commit (no two structural-invariant tests coexist).
  - AC #1 row 4 (mini-CAD-1 row 3 regression-guard): PASSING → WRITTEN-FAILING → PASSING transition per slice-007/009/010/011/012 N=5 stable pattern. The slice-011 6th sub-clause's canonical-substring pin test MUST continue to PASS after slice-013's refinement (regression-guard: adding a 7th sub-clause MUST NOT delete the 6th).
  - AC #2 fails pre-fix with `AssertionError: 'slice-011' not in CRITIQUE` OR `'slice-012' not in CRITIQUE` (concrete cross-slice anchors not yet present in the new sub-clause body).
  - AC #3 fails pre-fix with `RuntimeError: sha256 mismatch` (in-repo edited; installed not yet forward-synced).
  - AC #4 fails pre-fix because v0.28.0 entry doesn't exist yet in either file.
  - AC #5 fails pre-fix because `plugin.yaml.version` and `VERSION` are still `0.27.0` (slice-012's bumped state).
- Per slice-007..012 PMI-1 versioned-gate supersession pattern (slice-007 introduced `_at_0_22_0`; slice-008/009/010/011/012 superseded; N=5 events stable post-slice-012); slice-013 ratchets to N=6 events. The supersession ACT itself is justified by slice-012's in-repo VERSION file monotonicity invariant + the EPGD-1 discipline this slice authors (slice's own ship IS the canonical reference instance per RSAD-1 self-application). Delete old `_at_0_27_0` test row; add new `_at_0_28_0`. No two version-gates coexist.
- Per slice-011 NEW Dim 9 sub-class entry-pin-vs-PMI-1-gate-semantics-conflation discipline (N=1 at slice-011 build time + N=2 at slice-012 design-time-pre-empted success): the PMI-1 supersession Edit at slice-013's /build-slice MUST narrow-scope to the gate function body + its dedicated SECTION header ONLY. NEVER span entry-pin functions. The entry-pin functions for v0.22.0 / v0.23.0 / v0.24.0 / v0.25.0 / v0.26.0 / v0.27.0 all persist untouched post-supersession.
- TF-1 plan starts at 8 rows. May grow at /design-slice (Critic majors typically generate additional must-not-defer rows; slice-008 grew 5→7→9 across mission-brief → design → post-Critic).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Dim 9 new 7th sub-clause present + located + 7-sub-clause invariant + 6-sub-clause regression-guard | `pytest tests/methodology/test_critique_agent.py::test_critique_dim_9_entry_pin_vs_pmi_1_gate_sub_clause_present` PASS; `_location_pinned` PASS; `_lists_seven_sub_clauses` PASS; `_recursive_self_application_sub_clause_present` PASS (regression-guard: 6th sub-clause preserved) |
| 2 | Two concrete cross-slice example anchors present (slice-011 + slice-012) + ≥2-of-4 substantive-discipline anchors | `pytest tests/methodology/test_critique_agent.py::test_critique_dim_9_entry_pin_pmi_1_paragraph_cites_slice_011_and_012` PASS; asserts strict-both `["slice-011", "slice-012"]` AND ≥2-of-4 from `["Phase 1b INSERT", "Phase 1c narrow-scope Edit", "Audit 6 structural-separation", "SECTION header"]` all present (per M2 ACCEPTED-FIXED at /critique; mirrors slice-011 `_cites_at_least_two_cross_slice_anchors` precedent) |
| 3 | CAD-1 byte-equality audit clean | `python -m tools.critique_agent_drift_audit --repo-root . --claude-dir $HOME/.claude` exits 0; `pytest tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal` PASS |
| 4 | v0.28.0 EPGD-1 entry pinned bidirectionally | `pytest tests/methodology/test_methodology_changelog.py::test_v_0_28_0_epgd_1_entry_present_in_repo_and_installed` PASS; asserts in-repo + installed `methodology-changelog.md` both contain `## v0.28.0 —`, the locked rule ID `EPGD-1`, AND substantive canonical phrase `Entry-pin-vs-PMI-1-gate semantics conflation` |
| 5 | PMI-1 atomic at 0.28.0 | `python -m tools.plugin_manifest_audit --root .` exits 0; `pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_at_0_28_0` PASS; slice-012's `_at_0_27_0` test removed in the same commit (no two version-gates coexist per PMI-1 N=6 supersession pattern); entry-pin functions v_0_22_0 through v_0_27_0 all PASS unchanged (verified at /build-slice Phase 4 empirically per the EPGD-1 discipline) |

## Must-not-defer

- [ ] TF-1 PENDING -> WRITTEN-FAILING genuine transitions per slice-003..012 N=9 stable. Pin specific failure signals (substring absent, sha256 mismatch, version mismatch); no coincidental passes (slice-009 DEVIATION-2 `.find()`-collision lesson + slice-010 anchor-uniqueness pre-emption).
- [ ] 7-sub-clause structural invariant. The slice adds exactly ONE new sub-clause (7th); does NOT modify existing 6 sub-clauses' bodies; does NOT add an 8th. `test_critique_dim_9_lists_seven_sub_clauses` supersedes `_lists_six_sub_clauses` (delete old, add new — slice-011 supersession pattern). Any temptation to refactor existing sub-clauses is a design-stage red flag — refuse and keep scope narrow.
- [ ] Mini-CAD-1 row 3 regression-guard: `test_critique_dim_9_recursive_self_application_sub_clause_present` (slice-011's 6th-sub-clause-substring-pin) continues PASSING throughout the slice. Adding a 7th sub-clause MUST NOT delete or alter the 6th sub-clause's canonical literal title.
- [ ] EPGD-1 self-application: slice-013's OWN `/build-slice` Phase 1c PMI-1 supersession Edit (`_at_0_27_0` → `_at_0_28_0`) MUST narrow-scope to the gate function body + its dedicated `# --- PMI-1 cleanliness gate at v0.27.0 ---` SECTION header ONLY. Verified empirically post-build: all 6 entry-pin functions (v_0_22_0 + v_0_23_0 + v_0_24_0 + v_0_25_0 + v_0_26_0 + v_0_27_0) continue to PASS. **Slice's own ship is the canonical reference instance of the EPGD-1 discipline** (RSAD-1 self-application N=5 cumulative). Failure here = slice fails its own discipline at build time = invalidates EPGD-1's design-time pre-emption claim from slice-012.
- [ ] TWO-surface schema-pin discipline atomically: changes to `agents/critique.md` AND `~/.claude/agents/critique.md` ship in the same slice. Bidirectionally synced via CAD-1 byte-equality audit (slice-007 ground; sha256 forensic capture N=8 stable lesson per slice-005..012).
- [ ] EPGD-1 entry appended to `methodology-changelog.md` (in-repo) AND `~/.claude/methodology-changelog.md` atomically. Claim made in `## Vault updates made` MUST be verifiable by audit (`tools.plugin_manifest_audit` + `tools.critique_agent_drift_audit`).
- [ ] PMI-1 audit clean post-build (`python -m tools.plugin_manifest_audit --root .` exits 0). Atomic version bump: `VERSION` + `ai-sdlc-VERSION` + `plugin.yaml.version` all to `0.28.0`. Slice-012's `_at_0_27_0` PMI-1 versioned-gate test replaced (NOT additive) by `_at_0_28_0` per N=5-events-stable supersession pattern from slice-007..012; slice-013 ratchets to N=6 events.
- [ ] Bidirectional sha256 forensic capture in `build-log.md` for `~/.claude/agents/critique.md` + `~/.claude/methodology-changelog.md` + `~/.claude/ai-sdlc-VERSION` (Phase 0 + Phase 4 pattern, N=8 stable lesson per slice-005..012). Capture in-repo + installed sha256 BEFORE and AFTER the edits. Slice's git diff alone is insufficient evidence for out-of-repo edits.
- [ ] Backward-compat covenant: existing 23+ tests in `tests/methodology/test_critique_agent.py` (per slice-009's count of 16 + slice-010's growth + slice-011's growth + slice-012's growth) continue to PASS unchanged. The slice adds 4 new tests (canonical-substring + location-pin + 7-sub-clause invariant + cross-slice anchors); it MUST NOT modify or delete any existing test (except the structural-invariant supersession `_six` → `_seven` AND the PMI-1 supersession `_at_0_27_0` → `_at_0_28_0`).
- [ ] No regression on the broader methodology suite (`pytest tests/methodology/ -q` clean). The slice's surface is narrow (prompt-prose addition + changelog entry + version bump); broader breakage indicates an unintended scope creep.
- [ ] Cross-reference / topology preserved: the existing 6 sub-clauses' cross-references (Dim 9 → Dim 1, Dim 9 → Dim 4) are NOT removed or weakened. The new 7th sub-clause is ADDITIVE; topology unchanged. The new sub-clause's body has no cross-reference to Dim 1 or Dim 4 (Edit-discipline is a phase-level methodology concern, not a dimension-overlap concern — same shape as slice-011's RSAD-1 sub-clause).
- [ ] Shippability catalog row 13 added at `architecture/shippability.md` naming this slice's critical path (Dim 9 new 7th sub-clause + CAD-1 byte-equality + v0.28.0 EPGD-1 entry + PMI-1 0.28.0 invariant + EPGD-1 self-application empirical verification). Row 12's slice-012 reference updated to note slice-013 supersession of the `_at_0_27_0` PMI-1 versioned-gate (mirrors slice-012's row 11 update for slice-011's `_at_0_26_0` gate).
- [ ] Self-application BC-1 check: this slice's own mission-brief.md + design.md mention methodology-vocabulary anchors that BC-PROJ-1 + BC-PROJ-2 + BC-GLOBAL-1 carry as positive anchors but ALSO as Negative anchors (per slice-008 + slice-012 migrations: `aggregated lessons`, `Dim 9`, `back-sync`, `forward-sync`, `vocabulary`, `Critic-MISSED`, `meta-discussion`, `defer-with-rationale`, `false positive`). BC-1 v1.3's negative-anchor mechanism (slice-008 + slice-012 — uniform 9-token set across all three project-relevant rules) MUST silence BC-PROJ-1 + BC-PROJ-2 + BC-GLOBAL-1 cleanly without manual defer-with-rationale. Validates BC-1 v1.3's "validate using your own ship" pattern N=10 → N=11 ratchet + closes the noise loop at slice-013. Self-application result captured in `build-log.md` Phase 4.

## Out of scope

- **`/critic-calibrate` invocation** — explicitly out of scope at slice-013. The strongest #1 candidate per slice-012 reflection (cumulative cross-cutting misses 10 across slices 6-12 = 5× the ≤2 target across slices 6-15; 3 slices remaining in window). Deferred to slice-014+ per the user's choice at /slice to do EPGD-1 codification FIRST. **Acknowledge**: deferring /critic-calibrate one more slice while a sub-class IS codified inline here (slice-013) is a reasonable trade — sub-class codification is part of what /critic-calibrate would propose anyway. **Slice-014 candidate**: `/critic-calibrate` at slice-014 boundary.
- **Adding an 8th Dim 9 sub-clause** — explicitly out of scope. The slice adds exactly ONE new sub-clause (7th).
- **Modifying existing 6 sub-clauses' bodies or cross-references** — out of scope. Slice is purely additive.
- **`refactor-pmi-1-gate-to-version-agnostic-shape`** — N=5 events at slice-012, ratchets to N=6 at slice-013; per-bump cost still ~1 min trivial; defer one more cycle unless friction crosses meaningful threshold. **Watch slice-014+ for friction escalation**: at N=6 supersession events, the version-gate function's existence-in-name-only feels increasingly mechanical; if /critic-calibrate (slice-014+) flags it as recurring noise, promote to dedicated slice.
- **`fix-val-1-layer-b-intra-repo-tests-namespace-via-pytest-testpaths`** — N=10 cumulative recurrence at slice-012; deferred indefinitely until friction crosses meaningful threshold or /critic-calibrate flags as recurring noise pattern.
- **Wiegers AC-trace sub-class promotion** — N=1 at slice-008 (M1), no recurrence at slices 009-012; remain at N=1; defer to N=2.
- **Case-sensitivity canonical-literal pin discipline** (slice-009 DEVIATION-1 carryover) — pre-empted at slice-010/011/012 via design-time prose-structure discipline; remains N=1; defer to N=2.
- **`.find()`-collision in location-pin test discipline** (slice-009 DEVIATION-2 carryover) — pre-empted at slice-010/011/012 via anchor-uniqueness verification + scoped `.find()`; remains N=1; defer to N=2.
- **R-1 deeper fix for /diagnose cwd-mismatch** — risk-register HIGH-band open; documented-constraint workaround acceptable per slice-002; needs `/risk-spike` first to disambiguate cwd vs parallel-spawn-cascade hypotheses.
- **R-2 programmatic test for /diagnose cwd-mismatch warning runtime emission** — LOW impact; deferred per slice-002 reflection.
- **INST-2 generalization** — N=1 evidence; still defer to N=2.
- **Adding a Dim 9 sub-clause for `-D` / `-T` suffix convention as a rule-naming meta-discipline** (slice-011 B5 + slice-010 B5 carryover) — N=2 stable but cross-class meta-rule; not appropriate as a Dim 9 sub-clause (its level of abstraction differs from the other 7); defer indefinitely.
- **`refine-dim-9-with-bc-proj-2-recursive-self-application-build-time` sub-class** — slice-010 DEVIATION-3 carryover; pre-empted at slices 011/012 via RSAD-1 codification; remains N=1 standalone post-RSAD-1; defer to N=2 cross-slice.

## Dependencies

- Prior slices:
  - [[slice-006-update-critic-with-cross-cutting-conformance-dimension]] — Dim 9 baseline (CCC-1 v1; the 6 sub-clauses this slice extends by adding a 7th)
  - [[slice-007-add-critique-agent-content-equality-audit]] — CAD-1 byte-equality audit + skill-prose forward-sync ground + PMI-1 escape-closure pattern (the very pattern this slice's EPGD-1 discipline refines)
  - [[slice-008-refine-bc-1-anchors-with-negative-context]] — BC-1 v1.2 negative-anchor mechanism that silences methodology-vocabulary false positives on this slice's own ship
  - [[slice-009-refine-dim-9-with-design-md-tables-sub-clause]] — Dim 9 refinement template (analogous slice; CCC-1 v1.1 pattern)
  - [[slice-010-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic]] — MCT-1 default mandatory-Critic trigger (auto-sets `critic-required: true` for slice-013 per agents/*.md + methodology-changelog.md trigger glob match)
  - [[slice-011-promote-recursive-self-application-discipline-to-critique-skill-prose]] — RSAD-1 6th sub-clause + the canonical N=1 build-time slip surfacing the entry-pin-vs-PMI-1-gate-conflation sub-class
  - [[slice-012-bc-proj-2-negative-anchor-migration]] — N=2 design-time-pre-empted success codifying Phase 1b INSERT discipline + Phase 1c narrow-scope Edit discipline + Audit 6 structural-separation empirical verification (the cross-slice anchors for AC #2)
- Vault refs:
  - [[agents/critique.md]] Dimension 9 body lines 152-172 (current 6-sub-clause structure; slice-013 appends 7th)
  - [[decisions/ADR-005-add-cross-cutting-conformance-9th-critic-dimension]] (CCC-1 v1; EPGD-1 is additive sibling under same Dim 9, not superseding ADR-005)
  - [[decisions/ADR-010-promote-recursive-self-application-discipline-to-critique-skill-prose]] (RSAD-1; EPGD-1 is sibling sub-clause; same N-evidence-threshold-met-by-cross-slice-recurrence promotion pattern)
  - [[architecture/critic-calibration-log.md]] for the slice-013 success-criterion data point
  - [[methodology-changelog.md]] v0.21.0 (CCC-1 v1) + v0.24.0 (CCC-1 v1.1) + v0.26.0 (RSAD-1) + upcoming v0.28.0 (EPGD-1)
- Risk register: none (slice doesn't retire R-1 or R-2)
- Tooling:
  - `agents/critique.md` (Dim 9 new 7th sub-clause body)
  - `~/.claude/agents/critique.md` (Phase 2 forward-sync target)
  - `methodology-changelog.md` + `~/.claude/methodology-changelog.md` (v0.28.0 entry + entry-pin)
  - `VERSION` + `~/.claude/ai-sdlc-VERSION` (atomic bump to 0.28.0)
  - `plugin.yaml` (version field bump)
  - `tests/methodology/test_critique_agent.py` (add 3 new tests + supersede `_lists_six` → `_lists_seven`)
  - `tests/methodology/test_methodology_changelog.py` (add `_v_0_28_0_epgd_1_entry_present_in_repo_and_installed`; supersede `_at_0_27_0` → `_at_0_28_0` with NARROW-SCOPE Edit per EPGD-1 self-application)
  - `architecture/shippability.md` (add row 13)
- ADR: ADR-012 (analogous to ADR-008/010; reversibility: cheap; supersedes: null; extends ADR-010 by adding a sibling sub-clause to Dim 9 under the same N-evidence-promotion pattern)
- No code-tooling logic changes (no `.py` audit module modified); the slice is a prompt-prose addition + changelog entry + version bump.

## Mid-slice smoke gate

At ~50% of build (after `agents/critique.md` is edited in-repo and the 4 new test functions are added/superseded, but BEFORE Phase 2 forward-sync to `~/.claude/agents/critique.md`):

```
<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/test_critique_agent.py -q
```

Expected:
- All current tests (existing 23+) PASS unchanged
- The 3 new pin tests (`_entry_pin_vs_pmi_1_gate_sub_clause_present` + `_location_pinned` + `_paragraph_cites_slice_011_and_012`) PASS against in-repo (in-repo is edited)
- `_lists_seven_sub_clauses` PASS (new structural invariant)
- `_lists_six_sub_clauses` is DELETED (no longer in the file; pytest collection succeeds without it)
- `_recursive_self_application_sub_clause_present` PASS (mini-CAD-1 row 3 regression-guard — slice-011's 6th-sub-clause-substring-pin unaffected)

CAD-1 drift audit (`python -m tools.critique_agent_drift_audit`) reports `content-drift` exit 1 (in-repo edited; installed not yet forward-synced) — this is EXPECTED at this gate; CAD-1 must report clean exit 0 only at pre-finish gate after Phase 2 forward-sync.

If any existing test breaks (especially the 6 existing sub-clause structural / cross-reference tests): STOP, diagnose. Likely root causes:
- Accidentally modified an existing sub-clause body — revert that hunk; refine ONLY by appending the 7th.
- Removed or weakened the 6th sub-clause "Recursive self-application discipline" body — re-add; 7th sub-clause is purely additive.
- Edited a Dim 1 sub-bullet or Dim 4 sub-bullet body that broke a cross-reference target — revert; refine only Dim 9.
- The 7th sub-clause body inadvertently used substring `Recursive self-application discipline` as a literal title in a way that breaks the slice-011 `_recursive_self_application_sub_clause_present` substring-pin's location-pin sibling (if any) — adjust prose to avoid colliding with slice-011's location anchors.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed (TF-1 genuineness, 7-sub-clause invariant, mini-CAD-1 regression-guard, EPGD-1 self-application narrow-scope Edit, TWO-surface pin, EPGD-1 changelog entry, PMI-1 clean at 0.28.0, sha256 forensic capture, backward-compat on existing tests, no methodology-suite regression, topology preserved, shippability row 13, self-application BC-1 clean)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] PMI-1 audit clean: `python -m tools.plugin_manifest_audit --root .` exits 0
- [ ] CAD-1 audit clean at slice end: `python -m tools.critique_agent_drift_audit --repo-root . --claude-dir $HOME/.claude` exits 0
- [ ] Existing 23+ `test_critique_agent.py` tests still pass; new 3 tests + 1 superseded structural-invariant test all PASSING
- [ ] Methodology suite clean: `<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/ -q` exits 0 (no regression on the broader suite)
- [ ] Shippability catalog clean: row 13 added; row 12's slice-012 reference updated to note slice-013 supersession of the `_at_0_27_0` PMI-1 versioned-gate (mirrors slice-012's row 11 update for slice-011's `_at_0_26_0` gate)
- [ ] **EPGD-1 self-application verified empirically**: after the Phase 1c PMI-1 supersession Edit, run `pytest tests/methodology/test_methodology_changelog.py -k "v_0_2 and entry_present" -q` — ALL six entry-pin tests (v_0_22_0 / v_0_23_0 / v_0_24_0 / v_0_25_0 / v_0_26_0 / v_0_27_0) PASS unchanged. ZERO entry-pin functions deleted by the supersession Edit. Captured in `validation.md` AC #5 evidence row.
- [ ] Self-application BC-1 check: post-slice-013 BC-1 audit on THIS slice's own mission-brief.md + design.md does NOT fire BC-PROJ-1, BC-PROJ-2, or BC-GLOBAL-1 (negative-anchor mechanism silences them; closes the noise loop on the slice's own ship). Result captured in `build-log.md` Phase 4.
