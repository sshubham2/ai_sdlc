# Design: Slice 006 update-critic-with-cross-cutting-conformance-dimension

**Date**: 2026-05-10
**Mode**: Standard

## What's new

- **0. Pre-Dim-9 back-sync** (per Critic B1 + B2 + M2, /critique 2026-05-10) — **first build-time action**: back-sync the two prior /critic-calibrate 2026-05-10 ACCEPTED surgical sub-bullets from installed `~/.claude/agents/critique.md` into in-repo `agents/critique.md`. Specifically:
  - **Dim 1 sub-bullet** — insert after the existing `- "Async queue is sufficient" — but no load estimate justifies it` line (currently in-repo line 56). Content: copied verbatim from installed `~/.claude/agents/critique.md` line 57 (the "Verify by reading the implementation, not just the documentation" sub-bullet on tooling-doc-vs-implementation parity, naming TF-1, RR-1, BC-1, WIRE-1, NFR-1, VAL-1, CSP-1).
  - **Dim 4 sub-bullet** — insert after the existing `- Must-not-defer says "authorization on POST /X" — design has no authz on /X` line (currently in-repo line 87). Content: copied verbatim from installed `~/.claude/agents/critique.md` lines 89-92 (the "Methodology-audit conformance" sub-bullet with three sub-sub-bullets covering TF-1 row coverage, TF-1 PENDING→WRITTEN-FAILING genuineness with concrete accidental-PASS pitfall examples, and Algorithm-path-conformance with pre-existing branches).
  - **Build-log.md captures**: pre-back-sync sha256 + line count for in-repo `agents/critique.md`; post-back-sync sha256 + line count; the two back-synced text blocks verbatim. This makes the back-sync explicit forensic evidence per the slice-005 out-of-repo lesson, now applied bidirectionally.
- **9th Critic dimension** `### 9. Cross-cutting conformance` body in `agents/critique.md` (in-repo canonical source, installed to `~/.claude/agents/critique.md`). Inserted between Dim 8 body and the existing `### Bonus: weak graph edges` section. Body enumerates 5 sub-clauses with concrete cross-slice examples drawn from slices 001–005.
- **Reference frameworks table** (`agents/critique.md` table at lines 32–41) gains a Dimension 9 row. Citation choice: **Kiczales et al. (1997, *Aspect-Oriented Programming*) for terminology** ("cross-cutting concerns" is the canonical AOP term and is the dimension's vocabulary anchor) **+ explicit honest-out for evidence basis** (no peer-level evidence-framework cited; basis is operational/empirical — cross-slice accumulation per `architecture/critic-calibration-log.md` 2026-05-10 run, 10 sub-class hits across 5 distinct slices). This threads the 2026-05-10 Meta-Critic's three decline reasons: vocabulary anchor addresses reason #3 partially; honest-out preserves epistemic accuracy and mirrors Dim 8's existing pattern.
- **Frontmatter description** in `agents/critique.md` line 3 updated from "8 fixed dimensions" enumeration to "9 fixed dimensions" with `cross-cutting conformance` added to the parenthetical list.
- **Header line** `## Review along these 8 dimensions` (line 47) updated to `## Review along these 9 dimensions`.
- **Output format checklist** (in `agents/critique.md` `## Output format` example, currently 8 `- [x]` lines under `## Dimensions checked`) expanded to 9 items with `Cross-cutting conformance` as the 9th line.
- **Seven in-repo prose-parity updates** (`s/8 dimensions/9 dimensions/` mechanical):
  - `agents/AUTHORING.md` line 152 — agent inventory description
  - `agents/critic-calibrate.md` line 67 — Meta-Critic instructions reference
  - `skills/critic-calibrate/SKILL.md` line 109 — accepted-proposal template prose
  - `skills/critique/SKILL.md` lines 71, 268, 284 — three references in skill orchestration prose
  - `plugin.yaml` line 78 — agent manifest description
  - `tutorial-site/Hybrid AI SDLC Pipeline.html` line 520 — user-facing pipeline overview (also extends framework list to mention Kiczales for the new dimension)
  - **NOT updated**: `methodology-changelog.md` line 191 (the `DR-1` v0.X.0 entry references "the 8 dimensions" describing the *historical state* the DR-1 slice operated on; methodology-changelog is an append-only historical record per its own inclusion heuristic, not a current-state doc).
- **`architecture/critic-calibration-log.md`** gains a new dated entry `## User override — 2026-05-10` recording the slice-006 override of the 2026-05-10 Meta-Critic decline of the 9th-dimension proposal. Entry shape: 5-section template (override target with file:line ref to lines 41–44; slice + ADR; user rationale; Meta-Critic-reason disposition with three sub-items mapping to the prior decline's three reasons; success criterion for the next /critic-calibrate run).
- **`architecture/decisions/ADR-005-add-cross-cutting-conformance-9th-critic-dimension.md`** — new ADR locking the user-override decision (reversibility: **expensive**; status: accepted).
- **`methodology-changelog.md` v0.21.0 entry** with rule ID `CCC-1` (Cross-Cutting Conformance dimension v1) per the file's own format. Defect class: cross-cutting conformance findings previously had no consistent home (scattered across surgical Dim 1 / Dim 4 sub-bullets + lessons-learned + N=1 misses without a home); CCC-1 unifies under a 9th dimension. Validation method: prose-pin tests in `tests/methodology/test_critique_agent.py`.
- **`VERSION` bump** 0.20.0 → 0.21.0 (gated by `tests/methodology/test_methodology_changelog.py::test_version_matches_most_recent_changelog_entry`).
- **Test additions** in `tests/methodology/test_critique_agent.py` (existing file, extended):
  - **Rename** `test_critique_lists_eight_dimensions` → `test_critique_lists_nine_dimensions`; add `assert "9. Cross-cutting conformance" in CRITIQUE`. **Per Critic m2 — also update the docstring** (currently uses literal "all eight review dimensions" / "the eight named dimensions" on lines 42 and 44) to "all nine review dimensions" / "the nine named dimensions" so the docstring doesn't contradict the function name post-rename.
  - **New** `test_critique_dim_1_has_tooling_doc_vs_impl_parity_sub_bullet` (per Critic B1) — assert the back-synced Dim 1 sub-bullet is present in-repo: `assert "Verify by reading the implementation" in CRITIQUE` AND `assert "TF-1, RR-1, BC-1, WIRE-1, NFR-1, VAL-1, CSP-1" in CRITIQUE`.
  - **New** `test_critique_dim_4_has_methodology_audit_conformance_sub_bullet` (per Critic B1) — assert the back-synced Dim 4 sub-bullet is present in-repo: `assert "Methodology-audit conformance" in CRITIQUE` AND `assert "TF-1 row coverage" in CRITIQUE` AND `assert "Algorithm-path-conformance with pre-existing branches" in CRITIQUE`.
  - **New** `test_critique_dim_9_lists_five_sub_clauses` — assert all 5 sub-clause titles substring-present.
  - **New** `test_critique_dim_9_cross_references_resolve` (per Critic B2) — assert each "see Dimension N sub-bullet" pointer in Dim 9's body is paired with the actual existence of the referenced sub-bullet text within the same file: `assert "see Dimension 4 sub-bullet" in CRITIQUE` AND `assert "Methodology-audit conformance" in CRITIQUE` (both must hold); plus `assert "see Dimension 1 sub-bullet" in CRITIQUE` AND `assert "Verify by reading the implementation" in CRITIQUE` (both must hold). Catches independent-side drift if either Dim 9 cross-reference text or the Dim 1/4 surgical sub-bullet is removed in the future.
  - **New** `test_critique_dim_9_citation_is_deliberate` — assert `"Kiczales" in CRITIQUE` (vocabulary anchor) AND (`"no peer-level evidence-framework" in CRITIQUE` OR `"no specific evidence-framework" in CRITIQUE`) (honest-out for evidence basis).
  - **New** `test_critique_output_format_lists_nine_dimensions` — assert exactly 9 `- [x]` lines under the `## Dimensions checked` example block in the `## Output format` section; assert `Cross-cutting conformance` is among them.
  - **New** `test_no_in_repo_drift_on_eight_dimensions_phrase` — parity check across `agents/`, `skills/`, `plugin.yaml`, `tutorial-site/`. Asserts none of these contain the literal substring `8 dimensions` (excludes `methodology-changelog.md` + `architecture/` vault — historical content). Catches drift from the 7 prose-parity update sites.
- **Out-of-repo sync** of installed copies under `~/.claude/` (per slice-005 forensic-capture pattern): `~/.claude/agents/critique.md`, `~/.claude/agents/AUTHORING.md`, `~/.claude/agents/critic-calibrate.md`, `~/.claude/skills/critique/SKILL.md`, `~/.claude/skills/critic-calibrate/SKILL.md`, `~/.claude/plugin.yaml`, `~/.claude/methodology-changelog.md`. Build-log.md captures before/after sha256 + line counts + Dim 9 body block + Reference-frameworks table-row delta.

## What's reused

- `agents/critique.md` existing 8 dimensions and "Reference frameworks" table — unchanged in body and intent. **Important correction (per Critic B1, /critique 2026-05-10)**: the two surgical sub-bullets that the prior /critic-calibrate 2026-05-10 ACCEPTED (Dim 1 tooling-doc-vs-implementation parity; Dim 4 methodology-audit conformance + algorithm-path-conformance) currently exist **only** in the installed copy `~/.claude/agents/critique.md` (lines 57 and 89-92), NOT in the in-repo canonical source. The slice MUST back-sync these into in-repo as a prerequisite (see "What's new" item 0 below) before Dim 9 cross-references can resolve. Once back-synced, those sub-bullets remain as the cross-reference targets Dim 9 sub-clauses 1-3 point at. Slice is purely additive — no rewording, no removal.
- [[slice-005-add-bc-1-keyword-precision]] — provides the canonical pattern for editing out-of-repo files: forensic capture of before/after sha256 + line counts in build-log.md at T-final, schema/prose-pin tests that read the file via `Path.home()` and degrade gracefully when the file is absent in the test environment.
- [[slice-005-add-bc-1-keyword-precision]] reflection — is the `architecture/critic-calibration-log.md:Pattern summary` row "Cross-cutting conformance miss-class hardens to N=5 distinct slices, 10 sub-class hits" — the evidence basis the 9th dimension addresses.
- [[slice-001 through slice-004]] — provide the 10 individual sub-class hits (cwd-mismatch tool denial, RR-1 docstring-vs-regex, BC-1 trigger-keyword false positives, TF-1 PENDING→WRITTEN-FAILING genuineness via argparse exit-code-2, R-NN literal-match, Python 3.12+ docstring escape sequences, BC-GLOBAL-1 always-true short-circuit, etc.) that the Dim 9 body cites as concrete examples.
- `architecture/critic-calibration-log.md` 2026-05-10 calibration run (lines 12–60) — existing dated entry being **overridden**, not modified. The override is recorded as a new dated entry; the prior decline remains as the historical record being explicitly disagreed with. Per TRI-1 vocabulary, this is a user-override of meta-critique (distinct from Critic-MISSED or Critic-FALSE-ALARM).
- `tests/methodology/test_critique_agent.py` — existing file with `test_critique_lists_eight_dimensions` etc. Extended in this slice; not replaced.
- `tests/methodology/test_methodology_changelog.py::test_version_matches_most_recent_changelog_entry` — already enforces the VERSION ↔ changelog header pin; we satisfy it by bumping VERSION + adding the v0.21.0 entry in the same commit.
- `tests/methodology/conftest.py::read_file` — existing helper for reading in-repo files relative to repo root; reused by all new prose-pin tests.
- INST-1 install path (`methodology-changelog.md` v0.20.0): canonical agents are copied from `agents/` to `~/.claude/agents/` at install time. The in-repo source is canonical; the installed copy is the live working copy. This slice manually re-syncs the affected installed files at build time so the Critic in this conversation operates on the new dimension immediately (not after a future full re-install). **Known gap (per Critic m3, /critique 2026-05-10)**: `tools/install_audit.py` checks file existence only, not content equality. Once `/critic-calibrate` ACCEPTED edits modify the installed file (per `skills/critic-calibrate/SKILL.md:108-109` instructions to edit the installed copy), the in-repo source silently drifts and no audit detects it — this is the structural cause of the back-sync requirement (B1 + M2). Future slice candidate: `INST-2` content-equality check OR `tools/critique_agent_drift_audit.py` OR update `/critic-calibrate` skill prose to instruct in-repo edits. Out of scope for slice-006 itself; tracked in /reflect Discovered.

## Components touched

### `agents/critique.md` (modified — additive only)

- **Responsibility**: the adversarial Critic agent system prompt — stance, dimensions, specificity/honesty rules, output format, calibration awareness. Load-bearing artifact (per `tests/methodology/test_critique_agent.py` docstring: "the most adversarially-load-bearing artifact in the pipeline").
- **Lives at**: `agents/critique.md` (in-repo canonical source); installed to `~/.claude/agents/critique.md`.
- **Key interactions**: read by `skills/critique/SKILL.md` Step 2 (Agent tool spawn with `subagent_type: "critique"`); read by `skills/critic-calibrate/SKILL.md` Step 4 + `agents/critic-calibrate.md:67` (Meta-Critic instructions reference the dimension structure when generating proposals).
- **Surface change**:
  - Frontmatter `description` field (line 3) — extends parenthetical from 8 → 9 named dimensions
  - Header `## Review along these 8 dimensions` (line 47) → `## Review along these 9 dimensions`
  - Reference frameworks table (lines 32–41) — adds row for Dimension 9 (Kiczales + honest-out)
  - New dimension body section `### 9. Cross-cutting conformance` inserted between current Dim 8 body and `### Bonus: weak graph edges`
  - Output format `## Dimensions checked` example block — adds `- [x] Cross-cutting conformance — <findings or "none because ...">` as the 9th line
- **Dim 9 body shape** (5 sub-clauses; first 3 cross-reference, last 2 standalone):

  ```markdown
  ### 9. Cross-cutting conformance

  Slices commonly fail not in their own internal logic but in their **conformance to upstream constraints / pre-existing systems / in-house audits / runtime environment / language version / pre-existing algorithm branches**. These miss-classes have empirically accumulated across slices 001–005 (10 sub-class hits per `architecture/critic-calibration-log.md` 2026-05-10 calibration run); two were promoted to surgical sub-bullets under Dimensions 1 and 4 at that run, three were left as N=1 watch-listed. This dimension is the unified home for all five sub-classes; it overlaps Dimensions 1 and 4 deliberately (cross-references below), but provides the cross-cutting view that asks "is this slice conforming to constraints external to its own scope".

  Per the Meta-Critic's 2026-05-10 decline note, this dimension's evidence basis is operational/empirical — there is no peer-level evidence-framework cited. Vocabulary follows the **Aspect-Oriented Programming** body of work originating with Kiczales et al. (1997, ECOOP), where "cross-cutting concerns" became a frozen term-of-art within ~2-3 years of the original paper (the original 1997 paper introduced "aspects" with the verb "cross-cut"; the noun phrase crystallized in the subsequent AOP literature).

  - **Methodology-audit conformance** — see Dimension 4 sub-bullet for full examples (TF-1 row coverage, TF-1 PENDING→WRITTEN-FAILING genuineness, algorithm-path-conformance with pre-existing branches). Listed here as the cross-cutting view: this is how methodology conformance fails as a *class* across in-house audits (TF-1, RR-1, BC-1, WIRE-1, NFR-1, VAL-1, CSP-1), not just per-AC. Concrete miss: slice-005 BC-GLOBAL-1 `always: true` short-circuit, missed at design time because pseudocode review didn't trace through pre-existing branches.

  - **Tooling-doc-vs-implementation parity** — see Dimension 1 sub-bullet for full examples. Listed here as the cross-cutting view: in-house audits' docstrings/prose drift away from their regex/parser/keyword-list implementations across the codebase, not in any single audit. Concrete misses: slice-002 RR-1 docstring vs `_RISK_HEADING_RE` regex; slice-003 BC-1 trigger-keyword false positives.

  - **Algorithm-path-conformance with pre-existing branches** — see Dimension 4 sub-bullet for full body. Listed here as cross-cutting because the same shape recurs whenever a slice adds a new branch to existing logic — not specific to BC-1. Concrete miss: slice-005 BC-GLOBAL-1 `always: true` short-circuit dominating the new anchor filter.

  - **Runtime-environment / cwd / tool-permission boundaries** — N=1 sub-clause (slice-001 cwd-mismatch tool denial for spawned subagents in /diagnose); no peer cross-reference. The Critic should ask: when this slice runs in a real environment (cwd, permissions, parallel-spawn cascade, network), are the assumptions in design.md's verification plan still true? Concrete miss: slice-001 — Critic reviewed design and didn't flag that subagents might lose tools when TARGET ≠ parent cwd; the failure mode was hidden behind a context switch only visible at end-to-end runtime.

  - **Language-version conformance** — N=1 sub-clause (slice-004 Python 3.12+ docstring escape-sequence SyntaxWarnings); no peer cross-reference. The Critic should ask: does the slice's code use language features whose semantics changed in recent runtime versions (Python 3.12+ string-escape-sequence warnings; Node ESM transitions; deprecated module replacements)? Concrete miss: slice-004 — `\-` literal in docstring under Python 3.12+ emits SyntaxWarning; not flagged by the Critic.
  ```

### `architecture/critic-calibration-log.md` (modified — append override entry)

- **Responsibility**: append-only audit trail of `/critic-calibrate` runs AND now of user-overrides of those runs.
- **Lives at**: `architecture/critic-calibration-log.md`
- **Surface change**: append a new dated entry following the 2026-05-10 calibration run section. Entry header: `## User override — 2026-05-10`. Entry sections (5 in order):
  1. **Override target** — file:line reference (`architecture/critic-calibration-log.md:41–44`, the `## Decision on a 9th "Cross-cutting conformance" dimension` block)
  2. **Slice + ADR** — `slice-006-update-critic-with-cross-cutting-conformance-dimension` + `ADR-005`
  3. **User rationale** — pattern-unification preference (10 sub-class hits across 5 slices is the strongest evidence base in the project; scattering across Dim 1/4 + N=1 lessons obscures the unified shape); accepts citation-anchor thinness as honest-out trade-off
  4. **Disposition of Meta-Critic's three reasons** — three sub-items, one per reason:
     - Reason 1 (existing-dimension homes): **partially-acknowledged** — surgical sub-bullets remain at Dim 1/4 as cross-reference targets; Dim 9 adds the unified view, doesn't duplicate
     - Reason 2 (N=1 sub-clauses being thin): **acknowledged with watch-list** — runtime-environment + language-version sub-clauses are explicitly N=1 in Dim 9 body with promotion criterion (more hits in slices 6-15 strengthens; recurrence drops drop them)
     - Reason 3 (citation-anchor purity): **partially-overridden** — Kiczales cited for terminology; honest-out for evidence basis (mirrors Dim 8's existing pattern)
  5. **Success criterion for next /critic-calibrate run** — the cross-cutting-conformance miss class drops to ≤2 misses across slices 6-15 (currently averaging ~2 per slice = 10 across slices 1-5). If the rate doesn't drop, the dimension's wording or examples need refinement (or revert via a future slice).

### `methodology-changelog.md` (modified — prepend v0.21.0 entry; do NOT touch line 191)

- **Responsibility**: behavior-changing rule index per the file's inclusion heuristic ("if a slice acceptable yesterday would be refused today, it's a changelog entry").
- **Lives at**: `methodology-changelog.md` (in-repo); installed to `~/.claude/methodology-changelog.md`.
- **Surface change**: prepend new entry header `## v0.21.0 — 2026-05-10` with `### Added` block carrying `**CCC-1 — Cross-Cutting Conformance dimension v1**` rule reference, defect class, and validation method. The v0.20.0 entry below remains unchanged.
- **Why behavior change**: future `/critique` runs will produce findings under a 9th bucket (`Cross-cutting conformance`); slices that conformance-fail to upstream constraints can now be flagged as Major/Blocker findings under a single named dimension. A slice that would not have been flagged yesterday under the 8-dimension Critic may now be flagged.

### `agents/AUTHORING.md`, `agents/critic-calibrate.md`, `skills/critic-calibrate/SKILL.md`, `skills/critique/SKILL.md`, `plugin.yaml`, `tutorial-site/Hybrid AI SDLC Pipeline.html` (modified — prose parity)

- **Responsibility**: each carries a load-bearing reference to the Critic's dimension count or list. Drift from `agents/critique.md`'s actual dimension count would be a doc-truth-vs-implementation parity issue (the same class as Dim 1's surgical sub-bullet on tooling-doc-vs-impl parity).
- **Surface change**: mechanical `s/8 dimensions/9 dimensions/` per file. The tutorial-site HTML additionally extends the framework list cell to mention Kiczales as the new framework anchor.
- **Why included**: pin via `test_no_in_repo_drift_on_eight_dimensions_phrase`. Without the parity update, the new dimension would land but multiple authoritative-looking files would still claim "8 dimensions", which is exactly the doc-vs-implementation drift the dimension-1 surgical sub-bullet catches in tooling. The Critic itself would (correctly) flag a slice that left this drift in place.

### `tests/methodology/test_critique_agent.py` (modified — extended)

- **Responsibility**: pin load-bearing prose in `agents/critique.md`.
- **Lives at**: `tests/methodology/test_critique_agent.py`
- **Surface change** (1 rename + 4 new tests):
  - Rename `test_critique_lists_eight_dimensions` → `test_critique_lists_nine_dimensions`; extend with `assert "9. Cross-cutting conformance" in CRITIQUE`.
  - Add `test_critique_dim_9_lists_five_sub_clauses` — five `assert "<title>" in CRITIQUE` for the five sub-clause titles.
  - Add `test_critique_dim_9_citation_is_deliberate` — assert `"Kiczales" in CRITIQUE` (vocabulary anchor) AND `"no specific framework" in CRITIQUE OR "no peer-level evidence-framework" in CRITIQUE` (honest-out for evidence basis); both must hold to defend against a future drift that drops one half.
  - Add `test_critique_output_format_lists_nine_dimensions` — count `- [x]` lines in the `## Output format` example block (between the example's `# Critique:` opening and closing) and assert exactly 9; assert `"Cross-cutting conformance"` substring is present in the same block.
  - Add `test_no_in_repo_drift_on_eight_dimensions_phrase` — globs `agents/`, `skills/`, `plugin.yaml`, `tutorial-site/Hybrid AI SDLC Pipeline.html`; asserts `8 dimensions` does NOT appear in any. Excludes `methodology-changelog.md` (historical record), `architecture/` (vault), `tests/` (this file's defensive grep).

### `VERSION` (modified)

- **Responsibility**: canonical methodology version, mirrored at the head of `methodology-changelog.md`.
- **Lives at**: `VERSION`
- **Surface change**: `0.20.0` → `0.21.0` (single line).

## Contracts added or changed

No new external endpoints, events, or APIs. The Critic agent prompt is an internal contract between the `/critique` skill and the spawned `critique` subagent — see the Components touched section above for the surface change to `agents/critique.md`. The output-format checklist's expansion from 8 → 9 items is the only contract-shape change visible to downstream consumers (`/critic-calibrate` skill parses critique.md output structure when mining "Missed by Critic" entries; the parser is robust to extra dimensions because it scans `### \d+\.` headings rather than hardcoding 8).

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(Empty matrix — slice introduces no new Python modules. All edits are markdown / YAML / HTML / VERSION text + extensions to existing test file. Per the audit's own behavior, zero-row matrices are clean.)

## Decisions made (ADRs)

- [[ADR-005]] — Add 9th Critic dimension (Cross-cutting conformance) overriding the 2026-05-10 /critic-calibrate decline — reversibility: **expensive**

## Authorization model for this slice

N/A — methodology-tooling slice; no auth surface.

## Error model for this slice

N/A — methodology-tooling slice; no new error codes. The new prose-pin tests fail with standard pytest `AssertionError` when their substring check fails (existing pattern for the file).

## Empirical verification at design-time (per slice-001…005 N=4 stable lesson)

Following the slice-005 algorithm-path-conformance lesson explicitly: the citation-choice claim (Kiczales for vocabulary + honest-out for evidence basis) is empirically grounded at design time, not just asserted.

**Verification ran**:
1. **Kiczales 1997 paper exists and uses "cross-cutting concerns" terminology**: confirmed via prior knowledge — Kiczales et al., "Aspect-Oriented Programming", ECOOP 1997 (https://www.cs.ubc.ca/~gregor/papers/kiczales-ECOOP1997-AOP.pdf), introduced the term. The Critic does NOT need to look this up at runtime; the citation is a retrieval key per the existing Reference frameworks pattern.
2. **The 5 sub-clauses map cleanly to the calibration log evidence**: cross-checked Dim 9 body sub-clauses against `architecture/critic-calibration-log.md:18-29` Pattern summary table. Methodology-audit conformance ↔ row 1 (3 misses). Tooling-doc-vs-impl parity ↔ row 2 (3 misses). Algorithm-path-conformance ↔ row 3 (1 miss, folded into Proposal 2). Runtime-environment ↔ row 4 (1 miss, watching). Language-version ↔ row 5 (1 miss, watching). All 10 sub-class hits accounted for; no orphaned evidence; no manufactured sub-clause.
3. **Cross-references to Dim 1 / Dim 4 surgical sub-bullets won't double-fire at /critique time**: the surgical sub-bullets (post-back-sync at in-repo `agents/critique.md` Dim 1 + Dim 4 bodies; previously only at installed `~/.claude/agents/critique.md` lines 57 and 89-92) are written as instructions to the Critic agent ("Verify by reading the implementation, not just the documentation"; "TF-1 row coverage"). Dim 9's cross-references are written as **pointers, not duplicate instructions** ("see Dim 4 sub-bullet … listed here as the cross-cutting view"). The Critic reading both *should* surface the same finding once (under whichever dimension framing is more salient for the specific slice) — not twice. **Per Critic M1 (/critique 2026-05-10), this claim is now ACCEPTED-PENDING — to be empirically exercised at /build-slice T-late, NOT settled by mental simulation**: spawn 1 Critic re-critique of slice-005's archived `architecture/slices/archive/slice-005-add-bc-1-keyword-precision/design.md` against the new 9-dim Critic; capture finding count + per-finding dimension framing in build-log.md. ONE finding (Dim 4 OR Dim 9 framing) → empirical confirmation of no-double-fire claim. TWO findings (one Dim 4 + one Dim 9 on the same underlying miss) → escalate as validate-time blocker; revise Dim 9 cross-reference structure (likely toward Option C from B1's analysis: drop cross-references and inline). Plus add a calibration-log signal note for tracking double-firing across slices 6-8 to feed the next /critic-calibrate run.

**Algorithm-path-conformance check on critique.md's structure**: the `/critic-calibrate` skill reads `agents/critique.md` ("Review along these 8 dimensions" section per `agents/critic-calibrate.md:67`) when mining proposal patterns. After this slice the section header is "Review along these 9 dimensions". `agents/critic-calibrate.md` line 67's text reference must be updated in lock-step OR /critic-calibrate's own pattern-mining will attempt to read a non-existent header. Verified: design.md's "What's new" prose-parity update list covers this.

## Out-of-repo files touched — bidirectional sync sequence (per slice-005 forensic-capture lesson + Critic M2 in-repo↔installed gap)

Per Critic M2 (/critique 2026-05-10), naive in-repo→installed re-sync would OVERWRITE the only correct copy of the surgical Dim 1 + Dim 4 sub-bullets in `~/.claude/agents/critique.md`. The build sequence MUST be **bidirectional** with installed→in-repo back-sync FIRST (for the affected portions of `agents/critique.md`), THEN forward-sync after all in-repo edits land. Build-log.md captures sha256 + line counts at FOUR points for `agents/critique.md` specifically (T-pre-back-sync, T-post-back-sync, T-post-Dim-9-edit, T-post-final-resync) and at TWO points for the other files (T-before, T-after).

**Phase 1 — Back-sync (T-early, before any in-repo Dim 9 edit)**: installed → in-repo for `agents/critique.md` only; restores the Dim 1 + Dim 4 surgical sub-bullets to the in-repo canonical source.

| Direction | Source | Target | Scope | Rationale |
|-----------|--------|--------|-------|-----------|
| installed → in-repo | `~/.claude/agents/critique.md` (lines 57 + 89-92 only) | `agents/critique.md` (Dim 1 + Dim 4 bodies) | Two surgical sub-bullets | Restores prior /critic-calibrate ACCEPTED edits to canonical source per Critic B1 |

**Phase 2 — Forward-sync (T-final, after all in-repo edits land + tests pass)**: in-repo → installed for all affected files. **CORRECTED post-build per DEVIATION-1 + DEVIATION-2 in build-log.md**: removed `plugin.yaml` from sync targets (INST-1 do-not-copy list per `methodology-changelog.md` v0.20.0); added `ai-sdlc-VERSION` (INST-1 installed metadata file).

| In-repo source | Installed copy | Scope |
|----------------|----------------|-------|
| `agents/critique.md` | `~/.claude/agents/critique.md` | Full file (now contains restored surgical sub-bullets + Dim 9 + count updates) |
| `agents/AUTHORING.md` | `~/.claude/agents/AUTHORING.md` | Line 152 prose update |
| `agents/critic-calibrate.md` | `~/.claude/agents/critic-calibrate.md` | Line 67 prose update |
| `skills/critique/SKILL.md` | `~/.claude/skills/critique/SKILL.md` | Lines 71, 268, 284 prose updates |
| `skills/critic-calibrate/SKILL.md` | `~/.claude/skills/critic-calibrate/SKILL.md` | Line 109 prose update |
| `methodology-changelog.md` | `~/.claude/methodology-changelog.md` | Prepended v0.21.0 / CCC-1 entry |
| `VERSION` | `~/.claude/ai-sdlc-VERSION` | 0.20.0 → 0.21.0 (per INST-1 installed metadata; added at /build-slice DEVIATION-2 — design original missed this) |

(`tutorial-site/Hybrid AI SDLC Pipeline.html` is project-side documentation, not installed to `~/.claude/`. `plugin.yaml` is in-repo only — INST-1 explicitly puts it on the do-not-copy list; design original incorrectly listed it as a sync target — DEVIATION-1 logged at /build-slice; in-repo plugin.yaml retains canonical line-78 prose update.)

**Discovered class** (per Critic M2 + m3, tracked for /reflect → slice-007+ candidate): every future `/critic-calibrate` ACCEPTED proposal that follows `skills/critic-calibrate/SKILL.md:108-109`'s instruction to "edit `~/.claude/agents/critique.md`" creates this same in-repo↔installed drift. Structural fix candidates:
1. **Update `/critic-calibrate` skill prose** at line 108-109 to instruct editing in-repo `agents/critique.md` (with manual or automated forward-sync to installed).
2. **Add `tools/critique_agent_drift_audit.py`** content-equality check (sha256 in-repo vs installed) — runnable independently OR added to `tools/install_audit.py` as INST-2.
3. **Both 1 + 2** — defense in depth.

Out of scope for slice-006 itself; addressing the Discovered class is a separate slice (~30-60 min for 1; ~1-2 hours for 2; ~2 hours for both).

## Builder notes

- **Build sequence atomicity** (revised per Critic B1+B2+M2):
  1. **T-early — Phase 1 back-sync**: installed → in-repo for `agents/critique.md` Dim 1 + Dim 4 surgical sub-bullets. Build-log.md captures pre + post sha256 + line counts. Mid-build `pytest tests/methodology/test_critique_dim_1_has_tooling_doc_vs_impl_parity_sub_bullet test_critique_dim_4_has_methodology_audit_conformance_sub_bullet` should PASS (these tests are written first against the back-synced state).
  2. **T-mid — Dim 9 + parity edits**: add Dim 9 body, update line-3/47 headers, update Reference frameworks table row, update output-format checklist, update 7 prose-parity sites, bump VERSION + add methodology-changelog v0.21.0 entry, write override entry in critic-calibration-log.md, write the remaining new tests.
  3. **T-mid-2 — Mid-slice smoke** (per mission-brief): heading count + Dim 9 heading + table row 9 + prose-parity sweep (no `8 dimensions` substring in agents/skills/plugin.yaml/tutorial-site/) + `pytest test_version_matches_most_recent_changelog_entry`. If any fail: STOP and diagnose.
  4. **T-late — M1 empirical exercise** (ACCEPTED-PENDING): spawn 1 Critic re-critique against slice-005's archived design.md; capture finding count + framing in build-log.md.
  5. **T-final — Phase 2 forward-sync**: in-repo → installed for all 7 files; build-log.md captures sha256 + line counts before+after.
  - **All in one commit** so `test_version_matches_most_recent_changelog_entry` doesn't fail mid-sequence (VERSION 0.21.0 without changelog v0.21.0 entry would be a refusal).
- **`/critique` invocation order**: at /critique time, `~/.claude/agents/critique.md` still has 8 dimensions (this slice hasn't built yet). The Critic spawned for slice-006 used its current 8 dimensions — and caught the in-repo↔installed drift via Dim 7 (Drift from vault) without needing Dim 9. The new dimension is the *subject* of the slice, not the *lens* for reviewing it. No meta-bootstrapping issue.
- **Re-sync timing**: Phase 2 forward-sync runs only after all in-repo edits validated AND mid-slice smoke passes AND M1 empirical exercise completes (or escalates). If forward-sync runs before in-repo content is final, the installed Critic prompt will get an inconsistent intermediate state.
- **Test renaming impact**: `test_critique_lists_eight_dimensions` → `test_critique_lists_nine_dimensions` may break a `--lf`/`-k` invocation that targeted the old name. Acceptable for a per-test-file rename; CI doesn't pin test names. Per Critic m2 — also update the docstring (currently "all eight review dimensions" / "the eight named dimensions") to match the new function name.
