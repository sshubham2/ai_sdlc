# Critique: Slice 053 wire-backlog-md-into-slice-and-reflect

**Critic reviewed**: mission-brief.md, design.md, ADR-055, plus on-disk verification of skills/slice/SKILL.md, skills/reflect/SKILL.md, methodology-changelog.md, plugin.yaml, VERSION, ~/.claude/ai-sdlc-VERSION, architecture/shippability.md, architecture/build-checks.md, architecture/risk-register.md, diagnose-out/backlog.md, tests/skill_drift_equality.py, tests/methodology/conftest.py, tests/methodology/test_methodology_changelog.py, tests/methodology/test_slice_skill.py, .gitignore.
**Date**: 2026-05-20
**Result**: NEEDS-FIXES

## Summary

The slice is well-precedented (SOAD-1 multi-surface + BFRD-1 position-pin + slice-049/051 OSDG-1-member-addition shape + slice-052 BC-PROJ-10 dischargement), the Inclusion-heuristic posture is correctly stated, the 4-part PMI-1 bump path is right, and ADR-055 is content-bearing. However, the design has two concrete defects that will materialize at /build-slice and one ambiguity that will block deterministic enforcement: (B1) the round-trip insert anchor specified in design.md ("directly under the existing `- **Risk profile:** …` row") is structurally wrong — inserting between `Risk profile:` and `Dependencies:` is mid-metadata-block, not at a stable position; (M1) two of the six new audit tests (#3 and #6) defer the canonical literal to /build-slice — TF-1 PENDING genuineness theater; (M2) R-13's unresolved producer-side OSDG-1 gap means the `SC-\d{3}` trigger grammar is unpinned across the consumer/producer surfaces; (M3) the mid-slice smoke gate's perturbation recipe is under-specified (slice-051 save-bytes-then-restore mechanic not echoed in design.md); (M4) the "self-bootstrap: no" decision is empirically wrong — slice-053's own mission-brief.md cites `SC-001` literally, so under the bare `SC-\d{3}` trigger the slice WOULD round-trip itself, contradicting the design's claim that it correctly no-ops. Plus 5 minors.

## Findings

### Blockers (must address before /build-slice)

#### B1: Round-trip insert anchor "directly under `- **Risk profile:** …`" is structurally fragile

- **Claim under review**: design.md "diagnose-out/backlog.md in-place additive write contract" — *"The line goes directly under the existing `- **Risk profile:** …` row (preserves block ordering; doesn't disrupt downstream tooling that may read fixed-position metadata bullets)."* And ADR-055 — *"in-place additive `- **Addressed:** slice-NNN-<name> on YYYY-MM-DD` line directly under the `- **Risk profile:** …` row of each closed candidate block."*
- **Issue**: Every backlog.md candidate-block has the metadata sequence `**Source finding:**` → `[optional **Owner notes:**]` → `**Severity:**` → `**Risk profile:**` → `**Dependencies:**` → `**Blocks:**` → `**Description:**` → `**Rationale:**` → `**Suggested approach:**` → `**Evidence:**` (verified all 26 of 26 blocks). Inserting *directly under* `Risk profile:` shoves `**Addressed:**` BETWEEN `Risk profile:` and `Dependencies:` — i.e., *in the middle of the metadata bullets*. This actively DOES disrupt the "fixed-position metadata bullets" the design claims it preserves — self-contradictory. The prose-contract relies on Claude getting the position right at /reflect runtime; anchoring on `Risk profile:` was chosen explicitly over more stable alternatives (none considered in design.md "Open ambiguities").
- **Evidence**:
  - `diagnose-out/backlog.md` candidate-block shape: lines 89-105 (SC-001), lines 109-124 (SC-002) — structural sequence verified.
  - `design.md` "diagnose-out/backlog.md in-place additive write contract" subsection: insert location claim.
  - ADR-055 "Decision" subsection: same claim.
- **Proposed fix**: Change the insert location to a structurally stable anchor — option (b): immediately AFTER the `- **Evidence:**` block of the candidate (between the last `Evidence:` sub-bullet and the next `### SC-NNN` header — fully separate from existing metadata, additive-at-end of the candidate block). Update design.md "diagnose-out/backlog.md in-place additive write contract" + ADR-055 "Decision" accordingly.
- **Builder draft**: ACCEPTED-FIXED — fix at design.md `### \`diagnose-out/backlog.md\` in-place additive write contract` subsection (changed insert location to after `**Evidence:**` block) + ADR-055 "Decision" subsection (same change) + design.md "Open ambiguities" item 3 (recipe updated).

### Majors (address this slice)

#### M1: Tests #3 and #6 ("mandatory consumption phrase" / "round-trip canonical phrase") cannot be authored at design-time — defers test-genuineness to /build-slice

- **Claim under review**: design.md "Test inventory" rows 3 + 6 — *"Literal canonical phrase pin (e.g. `when this file exists` or similar — final wording locked at /build-slice; the test uses two short literal tokens to minimize prose-coupling per slice-008 N-substring discipline)"*.
- **Issue**: If the canonical phrase is only finalized at /build-slice, the test literal is chosen AFTER the prose is written — inverting the test-first contract (test should FAIL before implementation, then PASS after). The design's "Genuine-contrast proof method" *"perturb the named substring → FAIL"* fails because the named substring doesn't exist at design lock. The test-author at /build-slice will pick literals matching the prose they just wrote — the slice-037 M-add-1 tautological-green class. Sub-issue: "slice-008 N-substring discipline" is misremembered — that discipline is about pinning the canonical literal across N surfaces, not about minimizing specificity at one surface. SOAD-1 / BFRD-1 use the FULL canonical phrase (`bug-fix repro prelude discipline`, `conditional confirm-then-auto-invoke`).
- **Evidence**:
  - `design.md` "Test inventory" table rows 3 + 6.
  - `tests/methodology/test_slice_skill.py:359` — BFRD-1 precedent pins full canonical phrase `bug-fix repro prelude discipline`.
  - aggregated-lesson row 7 / slice-051: content-bearing pin defeats tautological-green class only with full literal.
- **Proposed fix**: Lock both canonical phrases NOW, at design time, in design.md + ADR-055:
  - Test #3 (consume side): `MUST consult diagnose-out/backlog.md as a mandatory candidate source when it exists`.
  - Test #6 (round-trip side): `append **Addressed:** slice-NNN-<name> on YYYY-MM-DD under each closed candidate block`.
  /build-slice Phase 1 SKILL.md edits MUST emit these exact phrases verbatim.
- **Builder draft**: ACCEPTED-FIXED — locked both canonical phrases in design.md "Test inventory" rows 3 + 6, mirrored in ADR-055 "Decision" subsection. The /build-slice SKILL.md edits must emit the exact phrases verbatim.

#### M2: BCR-1 pins only the consume + round-trip prose, not the upstream `/slice-candidates` SC-NNN identifier grammar; R-13 is the producer-side drift gap that BCR-1 does not close

- **Claim under review**: design.md "Open ambiguities" item 2 + ADR-055 — *"when a just-completed slice's `mission-brief.md` OR `reflection.md` contains at least one `SC-\d{3}` token (grep-able, not Claude-judgement)"*.
- **Issue**: The trigger identifier `SC-\d{3}` is produced by `skills/slice-candidates/build_backlog.py`. `skills/slice-candidates/SKILL.md` is NOT OSDG-1-guarded (R-13 OPEN per risk-register:225, deferred by slice-051 precedent + slice-052 nomination). A future producer-side edit could change SC-IDs to `SC-001a` / `BL-001` / `CAND-001` / `SC-1234` — and the BCR-1 round-trip would silently no-op on all those backlogs. The "grep-able, not Claude-judgement" objectivity claim is unfounded under producer-side rename. Plus: design.md Test #6 pins `Addressed:` + `SC-` literals in the *consumer's* SKILL.md prose, but does NOT pin the trigger grammar `SC-\d{3}` regex anywhere.
- **Evidence**:
  - `architecture/risk-register.md:225` — R-13 open.
  - `skills/slice-candidates/build_backlog.py` — backlog generation local-to-tool, ungated.
  - ADR-055 "Consequences" — enumerates 7 consequences; none mentions R-13 producer-side dependency.
- **Proposed fix**: (a) Add explicit ADR-055 Consequences bullet naming BCR-1↔R-13 producer-side dependency. (b) Extend Test #6 to also pin the literal `SC-\d{3}` grammar / regex shape in the SKILL.md prose, so a future producer-side rename forces a same-time consumer-side update. (c) Flag the R-14 risk-register entry to be split or sibling'd at /reflect to track this dependency.
- **Builder draft**: ACCEPTED-FIXED — added a new bullet to ADR-055 "Consequences" naming the BCR-1↔R-13 producer-side dependency; extended design.md Test inventory row 6 to also pin the literal `SC-\d{3}` regex grammar; added a note to design.md "Open ambiguities" item 2 about producer-side drift; planned R-14 entry at /reflect will record this dependency explicitly.

#### M3: Mid-slice perturbation recipe under-specified — design.md does not echo the slice-051 save-bytes-then-restore mechanic

- **Claim under review**: design.md "Test inventory" → "Genuine-contrast proof method" — *"perturb the named substring in `skills/slice/SKILL.md` (one non-EOL byte OUTSIDE any other anchor) → FAIL. Restore. PASS."*
- **Issue**: The mission-brief correctly names slice-051's gotcha (co-FAIL during full-suite run + the `git checkout`-trips-BC-PROJ-3/BC-GLOBAL-2 hazard), but design.md "Genuine-contrast proof method" is silent on the **save-bytes-then-restore-via-content-hash-assertion** mechanic. Per slice-051 aggregated lesson: *"A mid-slice genuine-contrast perturbation of a git-tracked file MUST restore via saved-temp-bytes / inverse-edit + a pre/post content-hash assertion from the START — NEVER `git checkout -- <path>` / `git restore` / `git stash`"*. Both `skills/slice/SKILL.md` and `skills/reflect/SKILL.md` are git-tracked — slice-051 hazard applies directly.
- **Evidence**:
  - aggregated-lesson row 6 / slice-051 verbatim quote.
  - `git ls-files skills/slice/SKILL.md skills/reflect/SKILL.md` — both git-tracked.
- **Proposed fix**: Add to design.md "Genuine-contrast proof method" the explicit 6-step recipe: (1) read file as bytes, hash via `hashlib.sha256`, save bytes; (2) perturb via Edit tool / Python file write; (3) run isolated test, assert FAIL; (4) restore by writing saved bytes back; (5) re-hash + assert restored hash equals saved hash; (6) NEVER `git checkout` / `git restore` / `git stash`. Echo in build-log.md per mid-slice smoke gate prose.
- **Builder draft**: ACCEPTED-FIXED — added explicit 6-step save-bytes-then-restore-via-hash-assertion recipe to design.md "Genuine-contrast proof method" subsection, with explicit `NEVER git checkout/restore/stash` clause echoing slice-051 lesson.

#### M4: The "Self-bootstrap: no" decision is empirically wrong — slice-053's mission-brief.md DOES cite `SC-\d{3}` literally; the bare-grep trigger needs sentinel-anchoring

- **Claim under review**: design.md "Open ambiguities" item 4 — *"Self-bootstrap: should slice-053 itself round-trip backlog.md? Decision: no. slice-053 doesn't cite any `SC-\d{3}` in mission-brief.md … the BCR-1 trigger correctly no-ops."*
- **Issue**: Empirically check-able and FALSE. The slice-053 mission-brief.md cites `SC-001` literally in the Risk-retired paragraph: *"missed the 26 owner-confirmed /diagnose backlog candidates (incl. **SC-001** — `pyproject.toml [project].version = 0.20.0` vs `VERSION = 0.60.0` …)"*. Out-of-scope section also names `SC-001 through SC-026` and `SC-001` again. ADR-055 Context cites `SC-001` twice. Under the trigger rule "any `SC-\d{3}` in mission-brief.md OR reflection.md", THIS slice triggers — but the design says it should NOT round-trip. Contract says "MUST update" but slice plans to NOT. Either (a) the "doesn't cite any SC-\d{3}" claim is empirically wrong (it does), OR (b) the trigger needs a nuance distinguishing *mentioned* from *addressed*, but no such nuance is in design.md or ADR-055.
- **Evidence**:
  - mission-brief.md Risk-retired paragraph (literal `**SC-001**`).
  - mission-brief.md Out of scope (`SC-001 through SC-026`).
  - ADR-055 Context paragraph (literal `SC-001`).
  - design.md "Open ambiguities" item 4 claim.
- **Proposed fix**: Refine the trigger rule in ADR-055 + design.md: distinguish "merely *mentioned*" (no round-trip) from "*addressed*" (round-trip required). Add a structured sentinel to mission-brief.md / reflection.md: literal `**Closes:** SC-NNN[, SC-MMM, …]` header (mirrors GitHub closes-issue convention). Trigger regex becomes `\*\*Closes:\*\* SC-\d{3}` rather than bare `SC-\d{3}`. Add a 7th test row to the new audit module: `test_reflect_skill_md_bcr_1_closes_sentinel_grammar_pinned` asserting the SKILL.md prose names the literal closes-sentinel grammar.
- **Builder draft**: ACCEPTED-FIXED — refined trigger grammar to `**Closes:** SC-NNN` sentinel-anchored regex; updated ADR-055 "Decision" round-trip side, design.md "Open ambiguities" items 2 + 4, design.md "BCR-1 prose contract on /reflect SKILL.md" Auth model / Error cases, design.md "Test inventory" (added 7th test for closes-sentinel grammar pin; bumped audit module to 7 tests). slice-053 self-bootstrap is now correctly no-op under the new trigger (its mission-brief.md has no `**Closes:**` sentinel — verified).

### Minors (log; address if cheap)

#### m1: design.md "Components touched" line numbers ("currently lines 40-54", "currently lines 51-77") drift the moment the file is edited

- **Issue**: Line-number citations in design.md become stale after the first edit. Anchor citations are sufficient.
- **Proposed fix**: Strike parenthetical line numbers from design.md "Components touched" subsection; anchor-citations sufficient (slice-046/048 precedent).
- **Builder draft**: ACCEPTED-FIXED — stripped line-number citations from design.md "Components touched" subsections for `skills/slice/SKILL.md` and `skills/reflect/SKILL.md`.

#### m2: Inclusion-heuristic dischargement names BC-PROJ-10 but does not cite the canonical META-1 `## v` split assertion

- **Issue**: Per aggregated-lesson row 1 (slice-052): the Inclusion-heuristic posture should be evidence-anchored to "the META-1 enforcing-assertion grep". The current dischargement names precedent slices but doesn't show the META-1-assertion-level evidence.
- **Proposed fix**: Add a one-liner to "Inclusion-heuristic classification" paragraph citing the canonical META-1 assertion in `test_methodology_changelog.py`.
- **Builder draft**: ACCEPTED-FIXED — added META-1 enforcing-assertion citation to design.md "Inclusion-heuristic classification" section.

#### m3: design.md cites the `architecture/` gitignore status only implicitly; clarify test read-path semantic

- **Issue**: `architecture/` is gitignored — existing entry-pin tests work in the dogfood scenario (tests read against local checkout). Worth a one-liner noting the precedent.
- **Proposed fix**: Add one sentence to design.md "Components touched" → `tests/methodology/test_bcr_1_backlog_round_trip.py` Key interactions clarifying the `read_file` resolves to local checkout, not git-blob.
- **Builder draft**: ACCEPTED-FIXED — added one-sentence clarification.

#### m4: Test naming convention drifts from precedent

- **Issue**: SOAD-1 / BFRD-1 precedent uses `_present` / `_in_step2`; the proposed `_named_in_<section>` is a redundant suffix. Cosmetic.
- **Proposed fix**: Rename `test_slice_skill_md_bcr_1_backlog_md_named_in_candidate_sources` → `_consume_anchor_present`; `test_reflect_skill_md_bcr_1_backlog_md_named_in_step2` → `_round_trip_anchor_present`.
- **Builder draft**: ACCEPTED-FIXED — renamed tests 1 + 4 in design.md "Test inventory" to mirror BFRD-1 `_present` precedent.

#### m5: Already-annotated candidate-block edge case not covered

- **Issue**: design.md "Error cases" touches missing-block ("emit a warning") but not already-annotated (prior-slice double-shipment) — Builder M-add-1 territory if not caught now.
- **Proposed fix**: Add to "diagnose-out/backlog.md in-place additive write contract" → Error cases: SC-NNN block already carries one or more `Addressed:` lines → APPEND new line below existing one(s); never replace. Multiple `Addressed:` lines are valid (candidate's history shows every slice that touched it).
- **Builder draft**: ACCEPTED-FIXED — added the double-shipment append-never-replace error-case clause to design.md.

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (insert preserves block ordering — false), M2 (grep-able-objectivity claim unfounded under producer-side R-13 drift), M4 (slice-053 doesn't cite SC-NNN — false). Plus m2 (META-1 enforcing-assertion citation missing).
- [x] **Missing edge cases** — m5 (already-annotated candidate-block edge case). Other edge cases (no SC-NNN cited, backlog.md absent, backlog.md present + SC-NNN cited but candidate-block missing, concurrent /reflect race) all handled or N/A.
- [x] **Over-engineering** — none. Option 1 (prose-contract) over Option 3 (tools/backlog_round_trip.py helper) was correctly chosen; 6+2-test count tight.
- [x] **Under-engineering** — M1 (deferred canonical phrases break TF-1 genuineness). Every AC has a design element; methodology-audit conformance covered (PMI-1, INST-1, CAD-1, RR-1, MCFS-1, AVFS-1, BC-1, BRANCH-1, pipeline-chain).
- [x] **Contract gaps** — B1 (insert-point structural fragility), M2 (producer-side R-13 dependency under-declared), M4 (trigger grammar mentioned-vs-closes semantic gap).
- [x] **Security** — none. No new auth, no new endpoint, no new IDOR, no new injection. backlog.md writes confined to local-only gitignored content.
- [x] **Drift from vault** — MEPD-1 dischargement clean (RULE-path taken); 4-part PMI-1 bump enumerated; CAD-1 / OSDG-1 / Mini-CAD: agents/critique.md not touched (correct, CAD-1 N/A); supersedes nothing (clean lineage). Plus m1 (line-number citations) and m3 (gitignore framing).
- [x] **Web-known issues** — Skipped — WebSearch unavailable in Critic session; design choices not checked against post-training-cutoff platform changes. Practical risk low (no external SDK/API surface). Flagged per honest-out discipline.
- [x] **Cross-cutting conformance** — TF-1 row coverage N/A (Test-first: false); recursive self-application defect = M4; EPGD-1 sub-mode (b) design-time pre-empted success; SCPD-1 sound (row #53 + 2 entry-pin refs); FBCD-1 consistency clean across mission-brief / design / ADR; PTFCD-1 / PTFFD-1 clean (new file + new functions pending, file path exists for entry-pins); APED-1 N/A (no existing audit's parse rule modified).

## Triage

**Triaged by**: user
**Date**: 2026-05-21
**Final verdict**: CLEAN

Per TRI-1 ratification: all 13 findings (10 first-Critic + 3 meta-Critic missed) ACCEPTED-FIXED with edits applied to design.md + ADR-055 before triage. No ESCALATED, no ACCEPTED-PENDING, no OVERRIDDEN. Final verdict computes to CLEAN per /critique Step 4.5 mechanical rules.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md§"in-place additive write contract" + ADR-055§Decision + Open ambiguities item 3 — insert relocated from "under Risk profile:" to "after Evidence: block" (end-of-candidate-block seam) |
| M1 | Major | ACCEPTED-FIXED | design.md Test inventory rows 3 + 6 + ADR-055§Decision — both canonical phrases locked verbatim at design time |
| M2 | Major | ACCEPTED-FIXED | ADR-055§Consequences R-13-bullet + design.md Test #7 (`_sc_grammar_pinned` post-M-add-2 split) — consumer-side `SC-\d{3}` grammar pin |
| M3 | Major | ACCEPTED-FIXED | design.md§Genuine-contrast proof method — 6-step save-bytes-then-restore-via-hash-assertion recipe; explicit NEVER git checkout/restore/stash clause |
| M4 | Major | ACCEPTED-FIXED | ADR-055§Decision (round-trip side) + design.md Open ambiguities items 2 + 4 — refined trigger to `**Closes:** SC-\d{3}` sentinel-anchored regex; Test #8 closes-sentinel grammar pin; self-bootstrap now correctly no-op |
| m1 | Minor | ACCEPTED-FIXED | design.md§Components touched — line-number citations stripped |
| m2 | Minor | ACCEPTED-FIXED | design.md§Inclusion-heuristic classification — META-1 enforcing-assertion citation added (`test_methodology_changelog.py::test_methodology_changelog_has_versioned_entries` / line 136) |
| m3 | Minor | ACCEPTED-FIXED | design.md§Components touched — `read_file` resolves-to-local-checkout semantic clarification |
| m4 | Minor | ACCEPTED-FIXED | design.md Test inventory rows 1 + 4 — tests renamed `_consume_anchor_present` / `_round_trip_anchor_present` per BFRD-1 `_prelude_present` precedent |
| m5 | Minor | ACCEPTED-FIXED | design.md§"in-place additive write contract" + "BCR-1 prose contract on /reflect SKILL.md" Error cases — append-never-replace clause for double-shipment |
| M-add-1 | Minor | ACCEPTED-FIXED | design.md§"in-place additive write contract" Error cases — empty-Evidence-list edge case + Sommerville graceful-degradation clause |
| M-add-2 | Minor | ACCEPTED-FIXED | design.md§Test inventory — Test #6 split into 6 (canonical-phrase) + 7 (SC-\d{3} grammar); closes-sentinel renumbered #7→#8; audit module bumped 7→8 tests; entry-pins are #9 + #10 |
| M-add-3 | Minor | ACCEPTED-FIXED | design.md§per-test contrast plan Tests #9+#10 — MCFS-1 isolation parenthetical added (do NOT run MCFS-1 during v0.61.0-entry perturbation window; isolated pytest only) |
