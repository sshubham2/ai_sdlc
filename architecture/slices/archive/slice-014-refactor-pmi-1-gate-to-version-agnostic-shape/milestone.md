---
slice: slice-014-refactor-pmi-1-gate-to-version-agnostic-shape
stage: complete
updated: 2026-05-13
next-action: none (slice complete)
risk-tier: medium
critic-required: true
---

# Milestone: slice-014 refactor-pmi-1-gate-to-version-agnostic-shape

**Stage**: complete
**Next action**: none (slice complete)
**Updated**: 2026-05-13
**Risk tier**: medium — Critic required: yes (MCT-1 trigger: slice modifies `methodology-changelog.md` which is in MCT-1's "In-house methodology surfaces" trigger glob per slice-010 codification; auto-set per MCT-1 default)

## Progress

- [x] /slice — 2026-05-13
- [x] /design-slice — 2026-05-13
- [x] /critique — 2026-05-13 — CLEAN (0 blockers, 2 majors, 3 minors; all 5 findings ACCEPTED-FIXED inline at design-stage)
- [x] /critique-review — 2026-05-13 — EXTEND (5 first-Critic VALIDATED + 1 MISSED M-add-1 added; ACCEPTED-FIXED inline; DR-1 N=2 stable)
- [x] /build-slice — 2026-05-13 — SHIPPED (8-phase plan executed; 1 DEVIATION-1 surfaced + resolved at Phase 1d mid-slice smoke gate; all 8 TF-1 rows PASSING; full methodology suite 379/379 PASS at v0.29.0; all 6 audits clean; EPGD-1 self-application empirically VALIDATED — 0 of 7 prior entry-pin functions touched; bidirectional sha256 N=9 → N=10 stable; N-surface schema-pin N=2 → N=3 instances stable; PMI-1 versioned-gate supersession-event counter terminates at N=6)
- [x] /validate-slice — 2026-05-13 — PASS (all 5 ACs PASS with real-environment evidence; 0 PARTIAL, 0 FAIL; VAL-1 Layer A + B clean; WS-1 + ETC-1 silent-skip per opt-in defaults; shippability catalog 14/14 PASS with 114 underlying tests in ~8.5s aggregate; row 13 propagated `_invariant` rename confirmed in shippability run; no new reality surprises beyond DEVIATION-1 already captured at /build-slice)
- [x] /reflect — 2026-05-13 (reflection.md written; lessons-learned.md appended; PMI-1 versioned-gate supersession-event counter TERMINATED at N=6; DR-1 dual-review N=2 stable; RSAD-1 N=6 cumulative; N-surface schema-pin 3-surface shape N=3 instances stable; auto-archived to slices/archive/)

## Current focus

Build SHIPPED. PMI-1 v1.1 version-agnostic gate live at methodology v0.29.0. Slice-014 retired the per-version PMI-1 versioned-gate supersession pattern empirically — the gate function name is now `test_plugin_yaml_version_matches_version_file_invariant` (no version literal in body); 2 AST meta-tests + 1 regression test defend the new shape. Atomic version bump 0.28.0 → 0.29.0 across VERSION + plugin.yaml + ai-sdlc-VERSION; methodology-changelog v0.29.0 entry codifies PMI-1 v1.1 across N=3 surfaces.

**1 build-time DEVIATION**:
- **DEVIATION-1 (Phase 1d smoke gate)**: `monkeypatch.setattr` dotted-string-form `"tests.methodology.test_methodology_changelog.REPO_ROOT"` silently no-ops because pytest's namespace-package import-mode (`tests/` lacks `__init__.py`) places the running module under `methodology.test_methodology_changelog` (bare key) — dotted-string monkeypatch imports separate copy. Fix: object form `monkeypatch.setattr(sys.modules[__name__], "REPO_ROOT", tmp_path)`. **Critic-stack accountability**: /critique M2 pinned name-resolution; /critique-review M-add-1 added imports-prerequisite class; build-time smoke gate caught the namespace-package interaction. NEW Dim 9 sub-class candidate N=1: `pytest-namespace-package-import-mode-defeats-dotted-string-monkeypatch-target` — promote at N=2 if recurs at slice-015+. Same root-cause family as VAL-1 Layer B `tests` namespace-package class.

**1 slice-013 N=1 watch-list class N=2 promotion threshold MET**:
- `shippability-catalog-consumer-reference-propagation-after-PMI-1-structural-invariant-supersession` — slice-013 caught its N=1 reactively at /validate-slice Step 5.5; slice-014 caught its N=2 PROACTIVELY at Phase 4 (applied slice-013 generic methodology lesson scanning shippability.md for any existing rows referencing the superseded test name). Row 13 command updated to reference `_invariant`; row 14 added. Promote to Dim 9 sub-class refinement at slice-015 — N=2 evidence is the established threshold.

**Pattern-recognition signals (cumulative post-slice-014)**:
- All 6 Critic findings (5 first-Critic + 1 meta-Critic) ACCEPTED-FIXED; 0 OVERRIDDEN, 0 DEFERRED, 0 ESCALATED, 0 NOT-YET
- Critic-disposition accuracy projected post-/validate-slice: 73/73 across slices 6-14 IF all 6 findings VALIDATE empirically
- Cross-Critic-stack first-Critic catch rate within dual-review denominator = 5 of 6 (83.3%) — within range-bound 60-100% on N=9 evidence stable
- Recursive-self-application N=5 → N=6 cumulative post-RSAD-1 codification (slice-014 is canonical reference instance of EPGD-1 at the discipline-retirement level — (a) ↔ (b) duality)
- DR-1 dual-review catching pattern-blindness N=1 → N=2 stable post-slice-013 codification
- PMI-1 versioned-gate supersession-event counter: N=6 stable at slice-013 → **TERMINATED at slice-014** (does NOT continue to ratchet)
- Bidirectional sha256 forensic capture: N=9 → **N=10 stable**
- N-surface schema-pin 3-surface shape: N=2 → **N=3 instances stable** (RSAD-1 v0.26.0 + EPGD-1 v0.28.0 + PMI-1-v1.1 v0.29.0)
- Empirical-verification-at-design-time: N=12 → **N=13 stable** (3 Audits all VALIDATED at /build-slice — audit predictions held)
- Validate-using-your-own-ship: N=11 → **N=12 stable**
- Mini-CAD-1 row 3 PASSING→WRITTEN-FAILING→PASSING transition: N=6 stable (no row 3 transition needed at slice-014; not applicable — no pre-existing test was flipped)
- VAL-1 Layer B intra-repo `tests` package class: N=11 → **N=12 cumulative recurrence** at slice-014 (DEVIATION-1 root-cause is same family)
- Cumulative cross-cutting Critic misses at /critique-time first-Critic-only: 5 of 6 findings caught at /critique; 1 (M-add-1) caught at /critique-review (DR-1); 1 (DEVIATION-1) caught at /build-slice empirical smoke gate. Cumulative slices 6-14 catch rate stays range-bound 60-100% with margin.

**8 Phase plan executed in order** (post-/critique M1 + m2 fixes): Phase 0 → 1a → 1a' → 1b → 1c → 1d → 2 → 3 → 4. All phases completed successfully.

**All audits clean at slice-014 ship**:
- TF-1 strict-pre-finish: 8 rows PASSING / 0 WRITTEN-FAILING / 0 PENDING
- WIRE-1: zero-row matrix accepted
- BC-1: zero rules apply (negative-anchors did their job on methodology-vocabulary)
- INST-1: 24/24 skills + 5/5 agents + 4/4 templates + 15/15 tool modules at methodology v0.29.0
- PMI-1 plugin_manifest_audit: 24/5/15 enumeration; version 0.29.0
- CAD-1: agents/critique.md byte-equal in-repo↔installed at `0346d39ef988fa61...`
- Shippability row 14 (slice-014 critical path): 7/7 PASS in 0.08s
- Shippability row 13 (slice-013 critical path post-propagation): 2/2 PASS in 0.04s
- Full methodology suite: 379 passed in 1.86s at v0.29.0

## On resume

- **Last completed action**: /validate-slice (PASS — all 5 ACs PASS with real-environment evidence; VAL-1 Layer A+B clean; shippability catalog 14/14 PASS with 114 underlying tests; no new reality surprises)
- **Current work**: none
- **Next immediate step**: run `/reflect`

## Current focus

Dual-review (DR-1) complete. /critique CLEAN verdict + /critique-review EXTEND verdict. 5 first-Critic findings all VALIDATED by meta-Critic with correct severities (0 SUSPICIOUS, 0 SEVERITY-WRONG); 1 meta-Critic MISSED finding M-add-1 added and ACCEPTED-FIXED inline at design-stage. Final reconciled TRI-1 verdict CLEAN with 6 findings.

**First-Critic findings + fixes applied (post-/critique)**:
- **M1 (Major)** — META-1 transient breakage window from unpinned Phase ordering. Fix: design.md `## Phase plan` Phase 0..4; Phase 2 as single atomic-commit step. Mission-brief META-1 atomicity must-not-defer added.
- **M2 (Major)** — Regression test monkeypatch target name-resolution ambiguity. Fix: design.md `## Regression test fixture spec` subsection with full canonical function body inline + pinned monkeypatch target string.
- **m1 (Minor)** — ADR-013 frontmatter vs body reversibility wording. Fix: option (c) — preserves single-token frontmatter convention.
- **m2 (Minor)** — Phase labels scattered. Fix: combined with M1 at `## Phase plan`.
- **m3 (Minor)** — TF-1 row count divergence (11 vs 7). Fix: mission-brief table consolidated to 7 rows.

**Meta-Critic finding + fix applied (post-/critique-review DR-1 EXTEND)**:
- **M-add-1 (Major)** — `import pytest` + `import ast` not in current test file imports block. Canonical regression-test body uses `pytest.raises`; 2 AST meta-tests need `ast.parse`/`ast.walk`. Without imports, Phase 1d smoke gate rows 2+3+4 NameError — misdiagnosed as EPGD-1 violation per design.md diagnostic guidance (10-15 min cost). Fix: design.md Phase 1a' (between empirical-audit Phase 1a and INSERT Phase 1b) — narrow-scoped Edit on imports block adding `import ast` (stdlib) + `import pytest` (third-party) with PEP-8 grouping. 30-second Edit retiring entire risk class.

**DR-1 N=2 stable post-slice-013 codification** — slice-013 was first instance of dual-review catching pattern-blindness (M-add-1 there: body-bound widening defect class on sibling tests); slice-014 is second instance with a structurally distinct catch (runtime-prerequisite imports completeness). Meta-Critic noted in critique-review.md `## Notes`: "Two slices in a row now show 'the first Critic catches the design-semantic issue at the canonical body but misses the runtime-prerequisite at the canonical body's surrounding context'" — candidate pattern for `/critic-calibrate` aggregation at slice-015 (would propose codifying "canonical-body imports-and-fixtures completeness check" as Dim 9 sub-clause refinement under structural-prerequisites).

**Pattern-recognition signal**: 0 Critic findings OVERRIDDEN, 0 DEFERRED, 0 ESCALATED, 0 NOT-YET across both passes. All 6 ACCEPTED-FIXED inline at design-stage. Cumulative Critic-disposition accuracy projected: 67/67 (slices 6-13) + 6 at slice-014 = 73/73 IF all 6 findings VALIDATE at /validate-slice. Cross-Critic-stack rate at slice-014 = 5 of 6 (83.3%) for first-Critic catch rate within the dual-review denominator — within established range-bound 60-100% on N=9 evidence stable post-slice-014.

**Recursive-self-application N=6 cumulative post-RSAD-1 codification** (slices 009..014). RSAD-1 stress-test PASSES at design time. Empirical validation at /build-slice + /validate-slice pending.

**8 Phase plan canonical at design.md `## Phase plan`**: Phase 0 (sha256 capture) → 1a (empirical audits) → 1a' (imports preamble Edit — post-DR-1 M-add-1) → 1b (v0.29.0 entry-pin SECTION INSERT) → 1c (PMI-1 gate Edit narrow-scoped) → 1d (mid-slice smoke gate) → 2 (atomic commit — changelog + 3 version bumps + ADR-013) → 3 (full test suite) → 4 (sha256 capture post-edit + EPGD-1 self-application diff verification).

## On resume

- **Last completed action**: /critique-review (EXTEND verdict — 5 first-Critic findings VALIDATED, 1 MISSED M-add-1 added; both fixes applied inline; reconciled TRI-1 verdict CLEAN with 6 findings; critique_review_audit + triage_audit both PASS)
- **Current work**: none
- **Next immediate step**: run `/build-slice`

**Rule-ID convention picked**: PMI-1 v1.1 (preserves rule-ID lineage per BC-1 v1.x evolution precedent; introducing PMI-2 would falsely signal a structurally new rule — the methodology rule IS still "VERSION and plugin.yaml.version must bump atomically").

**Canonical phrase for 3-surface schema-pin**: `version-agnostic PMI-1 cleanliness gate` (substantive, 5 words, unique to slice-014; pinned across ADR-013 + in-repo methodology-changelog v0.29.0 entry + installed methodology-changelog v0.29.0 entry — N=2 instances stable → N=3 stable at slice-014).

**Components touched**: `tests/methodology/test_methodology_changelog.py` (1 narrow-scoped Edit removing legacy gate function + its SECTION header; 5 new functions in 3 new SECTIONs + 1 new v0.29.0 entry-pin SECTION with 2 functions = 7 new functions total). `methodology-changelog.md` (in-repo + installed) v0.29.0 entry. `VERSION` + `plugin.yaml` + `~/.claude/ai-sdlc-VERSION` (atomic bump 0.28.0 → 0.29.0). `architecture/shippability.md` (row 14, 8 pytest commands). `architecture/decisions/ADR-013-*.md` (created).

**TF-1 plan**: 7 rows (consolidated from mission brief's 11 rows — AC #4's 5-test plan condensed to 3 entry/prose/adr-pin tests; mission brief's optional mini-CAD-1 row dropped per design-slice scope decision). All PENDING.

**3 design-time empirical audits run**: (1) version-literal absence in proposed gate function body — PASS; (2) pinned error-message substring presence — PASS; (3) Edit narrow-scope verification on current file content — PASS pending Phase 1a pre-Edit re-confirmation. EPGD-1 self-application empirical verification path documented.

**RSAD-1 stress-test PASSES at design time** (3 Qs each pass — no internal version-literal pin inconsistencies, no transitive dependency on retired discipline, canonical reference instance status documented). RSAD-1 cumulative evidence post-codification: N=5 at slice-013 → N=6 at slice-014.

**Pre-emptive Critic concerns addressed**:
- EPGD-1 self-application narrow-scope: explicit Edit boundaries documented (`old_string`/`new_string` ranges enumerated).
- Wiegers AC-trace: full forward + reverse trace table in design.md; no design element lacks a driving AC; no AC lacks covering design elements.
- N-surface schema-pin discipline ratchet (N=2 → N=3 stable): canonical phrase pinned across 3 surfaces enforced by rows 5 + 7 of TF-1 plan.
- Algorithm-path-conformance (slice-005 lesson): 2 of 3 pre-existing branches (`assert == "0.NN.0"` literal pins) intentionally dropped; design.md justifies via 3-way META-1 + entry-pin + checklist composition.
- PMI-1 v2 source-of-truth migration: documented as out-of-scope with rationale; not load-bearing at slice-014 scope.

## On resume

- **Last completed action**: /design-slice (design.md + ADR-013 + milestone.md updated)
- **Current work**: none
- **Next immediate step**: run `/critique`

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [../../decisions/ADR-013-refactor-pmi-1-gate-to-version-agnostic-shape.md](../../decisions/ADR-013-refactor-pmi-1-gate-to-version-agnostic-shape.md)
- [critique.md](critique.md) — CLEAN (0 blockers, 2 majors, 3 minors; all ACCEPTED-FIXED)
- [critique-review.md](critique-review.md) — EXTEND (5 first-Critic findings VALIDATED + 1 MISSED M-add-1 added; all ACCEPTED-FIXED inline)
- [build-log.md](build-log.md) — SHIPPED (1 DEVIATION-1 surfaced + resolved at Phase 1d)
- [validation.md](validation.md) — PASS (5/5 ACs PASS; shippability catalog 14/14 PASS)
- [reflection.md](reflection.md) — YES shipped
