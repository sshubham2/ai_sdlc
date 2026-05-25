---
id: ADR-008
title: Refine CCC-1 Dim 9 sub-clause 2 with design.md mechanical tables / canonical inventories / install-time renames sub-class
date: 2026-05-11
slice: slice-009-refine-dim-9-with-design-md-tables-sub-clause
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-008: Refine CCC-1 Dim 9 sub-clause 2 with design.md mechanical tables / canonical inventories / install-time renames sub-class

## Context

Per CCC-1 v1 / [[ADR-005]] (slice-006, 2026-05-10), the Critic agent (`agents/critique.md`) carries a 9th dimension named "Cross-cutting conformance" with 5 sub-clauses: (1) Methodology-audit conformance — cross-references Dim 4 surgical sub-bullet; (2) Tooling-doc-vs-implementation parity — cross-references Dim 1 surgical sub-bullet; (3) Algorithm-path-conformance with pre-existing branches — cross-references Dim 4; (4) Runtime-environment / cwd / tool-permission boundaries — N=1 standalone (slice-001); (5) Language-version conformance — N=1 standalone (slice-004). The dimension's evidence basis is operational/empirical (honest-out); vocabulary anchor is Kiczales et al. 1997 ECOOP.

The current Dim 1 surgical sub-bullet (line 58 of `agents/critique.md`) covers **source-code-level drift**: "the tool's docstring / prose says format X — but the actual regex / parser / keyword-list in the implementation file accepts a different shape ... open the tool source (the `.py` file under `tools/`) and confirm the docstring example actually matches the regex/keyword-list." Dim 9 sub-clause 2 cross-references this with a one-sentence lift ("see Dimension 1 sub-bullet for full examples").

A **new sub-class** has now reached the BC-1 refinement promotion threshold (N=2) per slice-007 reflection's explicit promotion language ("Refine Dim 9 sub-clause 'Tooling-doc-vs-implementation parity' to include 'design.md mechanical tables vs methodology canonical references / install-time renames'"):

- **slice-006 DEVIATION-1 + DEVIATION-2** (2026-05-10) — slice-006's design.md "Out-of-repo files touched" table listed `plugin.yaml` (which lives on `INSTALL.md` Step 3f's "do not copy" exclusion list per `methodology-changelog.md` v0.20.0 line 157 — per Critic M2, this is the **negative-exclusion** canonical surface, distinct from `tools/install_audit.py:_CANONICAL_*` positive-inclusion tuples) AND missed `ai-sdlc-VERSION` (which IS in INST-1's `_CANONICAL_METADATA` tuple — the **positive-inclusion** canonical surface). Both surfaced at /build-slice Phase 5 as build-time DEVIATIONs requiring mid-build fix. The 8-dim Critic at /critique time walked Dim 7 (Drift from vault) but did NOT walk through design.md's mechanical table cell-by-cell against EITHER canonical inventory surface. Filed in slice-006 reflection's "Missed by Critic" as a Dim 9 sub-class candidate at N=1. **Recursive self-application note (slice-009)**: slice-009's own design.md originally conflated these two surfaces in its draft prose; Critic M2 caught it; correction recursive-self-applies the discipline this slice is encoding.
- **slice-007 Critic B1** (2026-05-10) — slice-007's design.md "Out-of-repo files touched" table named in-repo file `ai-sdlc-VERSION` (which doesn't exist in-repo — it's the **installed renamed copy** of in-repo `VERSION`). The install-time rename inversion was caught by Critic at /critique time (the **9-dim** Critic — Dim 9 was active by slice-007). Per slice-007 reflection: "STRENGTHENED design.md mechanical tables vs canonical references — now N=2 (slice-006 DEVIATION-1+2 + slice-007 Critic B1) — **MEETS PROMOTION THRESHOLD**".

The sub-class is also reinforced empirically by slice-008's Critic findings (per slice-008 reflection):
- **slice-008 M1 (Wiegers AC-trace)** — design.md's migration tables (BC-PROJ-2 row) had no driving AC. New Dim 9 sub-class candidate at N=1; same family (design-doc-level vs canonical-AC-inventory drift).
- **slice-008 M2 (TWO-surface schema-pin → N-surface generalization)** — N-substring discipline for any AC with multi-surface coverage. Pre-existing Dim 9 sub-class hardening; reinforces the design-doc-level family.

**Defect class summary**: Slices that author design.md mechanical tables (forward-sync targets, prerequisites, install-time renames, dependencies) commonly fail to verify each row against the corresponding methodology rule's canonical inventory in its implementation source. This is **structurally distinct** from the source-code-level drift covered by Dim 1's surgical sub-bullet:

| Dimension | Drift surface | Where the drift lives | Example |
|-----------|---------------|------------------------|---------|
| Dim 1 surgical sub-bullet | Source-code-level | `.py` file: docstring vs regex/parser/keyword-list | slice-002 RR-1 `_RISK_HEADING_RE` docstring vs regex |
| **Dim 9 sub-clause 2 (this slice's extension)** | **Design-doc-level** | **`design.md` mechanical table vs canonical inventory across multiple surfaces** | slice-006 DEVIATION-1: `plugin.yaml` on `INSTALL.md` Step 3f do-not-copy list (**negative-exclusion** surface) mistakenly in design.md table; slice-006 DEVIATION-2: `ai-sdlc-VERSION` in INST-1 `_CANONICAL_METADATA` (**positive-inclusion** surface) missed from design.md table; slice-007 B1: in-repo `VERSION` vs installed `ai-sdlc-VERSION` (**install-time-rename** surface) inverted |

Both belong to the same family ("Tooling-doc-vs-implementation parity") — the design-doc-level surface is the **cross-cutting view** of the source-code-level surface. Dim 9 is the appropriate dimension home (per CCC-1's defining ethos: cross-cutting view of constraints external to a slice's own scope).

A precision improvement is needed that:

1. Closes the N=2 promoted miss class without creating a dangling-pointer drift in Dim 9.
2. Preserves the 5-sub-clause structural invariant of CCC-1 v1 (pinned by `test_critique_dim_9_lists_five_sub_clauses`).
3. Preserves the existing Dim 9 → Dim 1 cross-reference text (pinned by `test_critique_dim_9_cross_references_resolve`).
4. Maintains the Dim 9 example-anchor convention (each sub-clause carries concrete slice-NNN examples — slice-001, slice-002, slice-003, slice-004, slice-005).
5. Reversibility: cheap, with the minor irreversible portion that ADR-005 already calibrated for (append-only changelog + cumulative slice-009-N Critic outputs influenced by v1.1 framing).

## Options considered

1. **Add a NEW 6th sub-clause to Dim 9 titled "Design.md mechanical tables vs canonical inventories"**
   - Pros: maximal salience; new sub-clause has its own slot.
   - Cons: violates the 5-sub-clause structural invariant pinned by current `test_critique_dim_9_lists_five_sub_clauses`. The new sub-clause is structurally a SUB-CASE of "Tooling-doc-vs-implementation parity" (design-doc-level surface of the same family); splitting them obscures the family relationship and forces test refactor (rewrite from `_five_sub_clauses` to `_six_sub_clauses`). Sub-clause proliferation is a slippery slope — at N=2 for design.md-tables, N=1 for Wiegers AC-trace (slice-008 M1 — currently watch-list), N=1 for slice-008 M2 N-surface generalization, the Dim 9 enumeration could balloon to 8-10 sub-clauses across slice-009 → slice-015.
   - Verdict: rejected — over-engineered for the conceptual scope; breaks the existing structural invariant.

2. **Refine Dim 1's surgical sub-bullet body to include design.md mechanical tables (instead of Dim 9)**
   - Pros: keeps Dim 9 unchanged.
   - Cons: Dim 1's surgical sub-bullet is intentionally narrow (source-code-level: docstring vs regex/parser/keyword-list in `.py` modules). Stuffing design-doc-level cases into Dim 1 widens the sub-bullet's scope and dilutes the "Verify by reading the implementation" framing (which is source-code-level by design). The cross-cutting nature of design.md mechanical tables (touching forward-sync, prerequisites, install-time renames — all cross-cutting concerns by CCC-1's defining ethos) belongs in Dim 9 by dimension assignment.
   - Verdict: rejected — wrong dimension for the design-doc-level sub-class.

3. **Refine Dim 9 sub-clause 2 "Tooling-doc-vs-implementation parity" body inline by extending it with the design-doc-level sub-case** (chosen)
   - Pros: preserves the 5-sub-clause structural invariant (existing tests stay green); keeps the source-code-level cross-reference to Dim 1 unchanged; adds the design-doc-level extension where it belongs (cross-cutting view); the existing slice-NNN-example-anchor convention is maintained (the new paragraph carries slice-006 + slice-007 concrete examples); mirrors how Dim 8 (Web-known issues) refined its body across CCC-1 (no separate sub-clauses, refinements happen within the dimension body).
   - Cons: the bullet body grows from ~3 lines to ~6-8 lines. Slight readability cost — but Dim 8's body is similarly multi-paragraph, so the precedent exists. The refined sub-clause now mixes two surfaces (source-code-level via cross-reference + design-doc-level inline); explicit framing in the prose names them as siblings to mitigate the muddy-scope risk.
   - Verdict: chosen.

4. **Add a NEW rule CCC-2 covering "design.md mechanical tables vs canonical inventories" with its own Validation surface**
   - Pros: separate rule = separate calibration tracking.
   - Cons: scope creep — CCC-1's bottom-up calibration design treats cross-cutting conformance as a single dimension with sub-classes; introducing CCC-2 fragments the calibration. The defect class doesn't have a distinct enforcement surface (the audit is reading-prose-during-critique, same as the rest of Dim 9); naming it as a separate rule is presentational, not structural.
   - Verdict: rejected — over-engineered for the conceptual scope.

5. **Defer N=2 until N=3 stronger evidence accumulates**
   - Pros: more cautious.
   - Cons: slice-007 reflection explicitly named the promotion at N=2 (matching the BC-1 v1.1 → v1.2 refinement threshold convention from slice-005 → slice-008, where N=3 was the original-rule promotion threshold but N=2 is the existing-rule refinement threshold). Continued deferral leaves the cross-cutting view incomplete and trains the Critic to miss the recurring sub-class. Slice-008 M1 + M2 already reinforce at N=1 each as related family-members; cumulative signal is stronger than raw N=2.
   - Verdict: rejected — N=2 with two reinforcing N=1 patterns at slice-008 is sufficient signal under the existing-rule refinement threshold.

## Decision

Adopt **Option 3**: refine `agents/critique.md` Dim 9 sub-clause 2 "Tooling-doc-vs-implementation parity" body inline by appending sentences to the existing bullet's paragraph that:

- Name the design-doc-level surface ("design.md mechanical tables vs methodology canonical inventories") as the sibling of the source-code-level surface that Dim 1 surgical sub-bullet covers.
- Enumerate the concrete canonical inventory anchors the Critic should verify against: `tools/install_audit.py` `_CANONICAL_*` lists (INST-1); `methodology-changelog.md` versioned-entry conventions (PMI-1); `plugin.yaml` plugin manifest entries; `VERSION` vs `ai-sdlc-VERSION` install-time rename.
- Carry the two concrete cross-slice examples at N=2: slice-006 DEVIATION-1 + DEVIATION-2 (INST-1 inventory drift) and slice-007 Critic B1 (install-time rename inversion).

Tag the rule as `CCC-1 v1.1` in `methodology-changelog.md` (mirrors BC-1 v1.0 → v1.1 → v1.2 versioning convention from slice-005 → slice-008). PMI-1 atomic version bump: `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all to `0.24.0`.

Cross-reference structure preserved: Dim 9 sub-clause 2 continues to say "see Dimension 1 sub-bullet for full examples" (source-code-level cross-reference); the new design-doc-level extension is **additive** inline, not replacing.

## Consequences

- **Dim 9 sub-clause 2 body grows by ~5 sentences** — names the design-doc-level surface, the canonical inventory anchors, and the two concrete cross-slice examples. The bullet's title ("Tooling-doc-vs-implementation parity") is unchanged.
- **The 5-sub-clause structural invariant remains stable** — `test_critique_dim_9_lists_five_sub_clauses` continues to PASS unchanged. The refinement is body-level, not enumeration-level.
- **Existing Dim 9 cross-reference tests remain stable** — `test_critique_dim_9_cross_references_resolve` continues to PASS (the "see Dimension 1 sub-bullet" pointer + "Verify by reading the implementation" target text are both unchanged); `test_critique_dim_9_citation_is_deliberate` continues to PASS (Kiczales + honest-out untouched); `test_critique_output_format_lists_nine_dimensions` continues to PASS (output-format block untouched).
- **`methodology-changelog.md` gains a `## v0.24.0 — 2026-05-11` entry** documenting CCC-1 v1.1. Format follows the BC-1 v1.1 → v1.2 versioning precedent.
- **Atomic version bump**: `VERSION` 0.23.0 → 0.24.0; `~/.claude/ai-sdlc-VERSION` 0.23.0 → 0.24.0; `plugin.yaml.version` 0.23.0 → 0.24.0. PMI-1 invariant maintained.
- **Shippability catalog row 9 added** at `architecture/shippability.md` naming the Dim 9 v1.1 refinement critical path + CAD-1 byte-equality + v0.24.0 changelog entry + PMI-1 0.24.0 supersession.
- **PMI-1 versioned-gate test supersession** — slice-008's `test_plugin_yaml_version_matches_version_file_at_0_23_0` is REPLACED by slice-009's `_at_0_24_0`. Per Critic M5: slice-007 introduced `_at_0_22_0`; slice-008 first-superseded with `_at_0_23_0` = N=1 supersession event; slice-009 ratchets to N=2 supersession events on completion. The supersession ACT is justified by slice-008 reflection's explicit choice + VERSION-file monotonicity invariant — NOT by N=2 stability of supersession-events (slice-009 itself creates the N=2). No two version-gates coexist.
- **Future cross-cutting tooling slices' /critique invocations** get explicit prompt-level retrieval for the design-doc-level Tooling-doc-vs-impl parity sub-class. The expected effectiveness signal is reduced design.md-tables miss rate in slices 9-15 (compared to the slice-006 + slice-007 baseline of 1-per-slice).
- **Next /critic-calibrate run** measures the v1.1 refinement effectiveness as part of the cross-cutting miss-rate target (≤2 across slices 6-15 per the 2026-05-10 user-override entry). Slice-009 is data point #4 in the window.

## Reversibility

**Tag: cheap** (with minor irreversible portion — same shape as ADR-005 but smaller magnitude).

### Magnitude justification for `cheap` tag (per slice-009 Critic M4)

ADR-005 (CCC-1 v1) was tagged `reversibility: expensive` because v1 introduced an entire new dimension to the Critic prompt: the 9th dimension itself + 5 sub-clauses + Kiczales vocabulary anchor + honest-out evidence basis citation + 7 prose-parity site updates across in-repo (`agents/AUTHORING.md`, `agents/critic-calibrate.md`, `skills/critic-calibrate/SKILL.md`, `skills/critique/SKILL.md`, `plugin.yaml`, `tutorial-site/Hybrid AI SDLC Pipeline.html`) + critique-output-format extension (`- [x] Cross-cutting conformance` added to the `## Dimensions checked` block). Mechanical revert touches 8+ files and ~30+ substring sites.

ADR-008 (CCC-1 v1.1) refines the BODY TEXT of ONE existing sub-clause inline. Mechanical revert touches:
- `agents/critique.md` + `~/.claude/agents/critique.md` — 1 paragraph append/revert per file (~5 sentences).
- `methodology-changelog.md` + `~/.claude/methodology-changelog.md` — 1 entry append/revert per file (~15-30 lines).
- `tests/methodology/test_critique_agent.py` — 3 test functions add/delete (~30 lines).
- `tests/methodology/test_methodology_changelog.py` — 1 test function add + 1 test function delete (single-function supersession).
- `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml` — single-line version bump.
- `architecture/shippability.md` — 1 row add/delete.

Total surface area: ~30-40 substring sites across 9 files, vs. ADR-005's 8+ files and 30+ sites of new structural surface. The "smaller magnitude" claim is quantitative: revert cost scales linearly with surface-area introduced; v1.1's surface-area is approximately 1/3 of v1's. The asymmetric magnitude justifies the `cheap` tag despite the same conceptual shape of irreversibility (append-only changelog + cumulative slice-N Critic outputs influenced by the version's framing).

Per the slice-008 N=2 BC-1 v1.1 → v1.2 precedent (also `cheap` despite refining an existing rule's body): incremental body-refinement ADRs are systematically tagged `cheap` regardless of their parent ADR's tag. This slice-009 ADR follows that precedent.

### What can be reverted (mechanical, ~30 min)

- Revert `agents/critique.md` Dim 9 sub-clause 2 body to pre-slice-009 wording (remove the ~5 appended sentences).
- Forward-sync the revert to `~/.claude/agents/critique.md`; verify via `tools.critique_agent_drift_audit`.
- Delete the 2 new tests in `tests/methodology/test_critique_agent.py`:
  - `test_critique_dim_9_tooling_doc_vs_impl_parity_covers_design_md_tables`
  - `test_critique_dim_9_design_md_tables_paragraph_cites_slice_006_and_007`
- Revert the `## v0.24.0 — 2026-05-11` entry from `methodology-changelog.md` (both in-repo and `~/.claude/`). NOTE: appending a new revert-superseding entry is the canonical recovery path per the file's append-only inclusion heuristic; mechanical deletion is in tension with the append-only nature.
- Revert atomic version bump 0.24.0 → 0.23.0 in `VERSION`, `~/.claude/ai-sdlc-VERSION`, `plugin.yaml.version`.
- Revert PMI-1 versioned-gate test supersession (`_at_0_24_0` → `_at_0_23_0`).
- Revert shippability catalog row 9.
- Revert this ADR-008 to `status: superseded` with a pointer to the reverting decision.
- Total: ~30 min mechanical work in the slice's affected files.

### Items that cannot be reverted (irreversible portion)

- **`methodology-changelog.md` append-only nature**: a v0.24.0 entry, once added, is canonically retracted via a later superseding entry. Mechanical deletion is possible but inconsistent with the file's stated inclusion heuristic. The clean retraction pattern is "v0.25.0 supersedes v0.24.0" rather than file-edit.
- **Cumulative slice-009-N Critic outputs influenced by v1.1 framing**: any /critique invocation between slice-009 and the revert filed under Dim 9 v1.1 will have considered the design-doc-level sub-class. Those archived critique.md outputs stay filed and influence pattern-recognition at future /critic-calibrate runs. Net-zero impact is impossible after ~3-5 slices under v1.1.
- **`architecture/critic-calibration-log.md`** if a calibration-log entry is created for slice-009's v1.1 effectiveness data: append-only by the file's design.

These are the same shape as ADR-005's irreversible portion (CCC-1 v1), with smaller magnitude (v1.1 is an incremental body refinement; v1 was the dimension addition itself).

## Cost summary

Prefer **refinement over revert** if the effectiveness check at slices 9-15 shows weak signal:

- Refinement path: edit the Dim 9 sub-clause 2 body to tighten language or add more concrete examples; takes ~15-30 min per refinement; no version bump needed (CCC-1 v1.1 → v1.2 would be a separate slice with separate ADR).
- Revert path: ~30 min mechanical work + an append-superseding methodology-changelog entry + an inability to fully retract cumulative Critic-output influence.

The asymmetry strongly favors refinement. The effectiveness check methodology already exists (`/critic-calibrate` cross-cutting miss-rate measurement in slices 6-15 per the 2026-05-10 user-override entry); a v1.1 → v1.2 refinement slice can be authored on the same template as slice-009 once the data accumulates.

## Cross-references

- [[ADR-005-add-cross-cutting-conformance-9th-critic-dimension]] — original CCC-1 v1 decision; slice-009 refines, does not supersede.
- [[ADR-006-critique-agent-drift-detection-via-hybrid-prose-and-audit]] — CAD-1 byte-equality audit; this slice exercises it as AC #3 / pre-finish gate.
- [[ADR-007-bc-1-negative-context-anchors-via-final-filter]] — BC-1 v1.2 negative-anchor mechanism; this slice's mission-brief + design contain methodology-vocabulary anchors and BC-1 v1.2 silences BC-PROJ-1 + BC-GLOBAL-1 cleanly (empirically verified at design-time, pre-build).
- `architecture/critic-calibration-log.md` 2026-05-10 calibration run + user-override — defines the cross-cutting miss-rate effectiveness target (≤2 across slices 6-15); slice-009 is data point #4 in the window.
- `methodology-changelog.md` v0.21.0 (CCC-1 v1 origin); v0.24.0 (CCC-1 v1.1 — authored by this slice).
