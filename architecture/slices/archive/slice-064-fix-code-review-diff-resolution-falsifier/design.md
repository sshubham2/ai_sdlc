# Design: Slice 064 fix-code-review-diff-resolution-falsifier

**Date**: 2026-05-23
**Mode**: Standard

## What's new

- `skills/code-review/SKILL.md` Step 1 rewritten — replace the single `git diff "$base"...HEAD --name-only --diff-filter=ACMR -- ':(exclude)architecture/**' ':(exclude)docs/**'` line with a union-of-three-sources block mirroring `tools/new_agent_warning_audit.py:_resolve_added_agent_files` shape (NAW-1 / ADR-061 §Decision L60-67).
- `skills/code-review/SKILL.md` Step 2 prompt-template `# Diff content` block aligned with Step 1's resolution — for each in-scope file emitted by Step 1, the agent receives the WT-vs-base diff (`git diff "$base" -- <file>`) which observes uncommitted edits, NOT the stale `git diff <base>...HEAD -- <files>` form that would re-introduce the falsifier downstream.
- 4 new prose-pin tests in `tests/skills/code_review/test_code_review_skill.py` (one is BFRD-1 WRITTEN-FAILING from /repro; three more PENDING):
  - `test_skill_md_step_1_diff_resolution_uses_union_of_three_sources` (WRITTEN-FAILING — AC 2)
  - `test_skill_md_step_1_all_three_legs_share_filter_shape` (PENDING — AC 1; pins identical `--diff-filter=ACMR --name-only` shape + matching architecture/docs path exclusions across the two `git diff` legs; the `git ls-files` leg only takes `--exclude-standard --others`)
  - `test_skill_md_step_1_union_aggregation_prose_pinned` (PENDING — AC 1 sibling; per /critique M2, pins SKILL.md Step 1 carries an explicit "union the three outputs by path; deduplicate" prose instruction AFTER the three bash commands — Claude's runtime aggregation obligation is prose-pinned, not ADR-only)
  - `test_skill_md_step_2_diff_content_block_aligned_with_step_1` (PENDING — AC 3; pins the Step 2 prompt-template references `git diff "$base"` per file rather than `git diff <base>...HEAD`)
- [[ADR-062]] — mirror NAW-1's union-of-three-sources read mechanism onto /code-review's SKILL.md Step 1; mints no new rule; supersedes nothing; reversibility: cheap. Inclusion-heuristic firing on scope-extension precedent (N=8 cumulative inclusive of slice-064; slice-049/050/051/057/058/059/062 + this).
- methodology-changelog `## v0.67.0 — 2026-05-23` entry (Inclusion heuristic — extending the slice-063 NAW-1 union-of-three-sources pattern to the `/code-review` SKILL.md surface).
- 5-part PMI-1 atomic bump 0.66.0 → 0.67.0: `VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` (PVFS-1) + `## v0.67.0` methodology-changelog header + installed `~/.claude/ai-sdlc-VERSION` (AVFS-1 forward-sync).
- 1 entry-pin pair in `tests/methodology/test_methodology_changelog.py`: `test_v_0_67_0_naw_extend_entry_present_in_repo` (EPGD-1 8-anchor list pinning the v0.67.0 header + Rule reference + NAW-1 + "Extend NAW-1 union-of-three-sources to /code-review" rule-name expansion + ADR-062 + 5-part PMI-1 + /code-review-surface + ("mints no new rule" AND "supersedes nothing") compound lineage clause; the lineage pair is a SINGLE compound `and` assertion treated as one anchor per slice-063 v0.66.0 entry-pin precedent at `test_methodology_changelog.py::test_v_0_66_0_naw_1_entry_present_in_repo`) + `test_v_0_67_0_naw_extend_shippability_consumer_propagation` (BCR-1 shippability traceability axis). Per /critique-review M-add-2 + M-add-3 fix: standardized to 8 anchors (compound lineage clause) matching ADR-062 §Consequences "8-anchor" wording, AND added the rule-name-expansion anchor ("Extend NAW-1 union-of-three-sources to /code-review") per slice-063 anchor (d) precedent — slice-064 is the first scope-extension-class entry that doesn't mint a new rule, so the rule-name expansion disambiguates "extends NAW-1" vs "is a NAW-1 surface" for future readers parsing the changelog alone.
- Shippability row #64 — extends the /repro-authored stub to cite the full BCR-1-traceability axis (cites BOTH ADR-062 AND NAW-1 ADR-061 AND R-18 (retired)).
- OSDG-1 mini-CAD forward-sync: `cp skills/code-review/SKILL.md ~/.claude/skills/code-review/SKILL.md` (EOL-DRIFT-1 EOL-agnostic per ADR-033).

## What's reused

- `tools/new_agent_warning_audit.py:_resolve_added_agent_files` (slice-063 / ADR-061 §Decision L60-67) — canonical union-of-three-sources shape; this slice mirrors the SAME three commands into SKILL.md prose:
  - **Source (i)** working-tree-vs-base: `git diff --name-only --diff-filter=ACMR "$base" -- <pathspec>`
  - **Source (ii)** untracked: `git ls-files --others --exclude-standard -- <pathspec>`
  - **Source (iii)** commits-vs-base: `git diff --name-only --diff-filter=ACMR "$base"...HEAD -- <pathspec>`
- `tests/methodology/test_code_review_skill_drift.py` (slice-060 OSDG-1 mini-CAD; slice-062 R-15 scope-extension) — drift-guard already enforces the in-repo↔installed forward-sync invariant on `skills/code-review/SKILL.md`. This slice REUSES it for AC 4 via the existing function `test_in_repo_and_installed_code_review_skill_md_are_content_equal` (verified at `tests/methodology/test_code_review_skill_drift.py:26`) — no new drift-guard member-addition. Per /critique B1 fix: the drift-guard file lives in `tests/methodology/` (the OSDG-1 family convention), NOT `tests/skills/code_review/`.
- `tools/pipeline_chain_audit.py` `_CANONICAL_CHAIN` (slice-060 / ADR-059 / CRSI-1 9-entry chain) — `/code-review`'s chain-shape block at SKILL.md's tail is untouched by this slice; the predecessor/successor/auto-advance edges are preserved verbatim.
- `tools/test_first_audit.py` (TF-1 / TFFL-1 / slice-034) — strict-pre-finish gate runs at /build-slice Step 6 on the mission-brief Test-first plan table.
- BCR-1 traceability axis (slice-053 / ADR-055) — no `SC-\d{3}` closure declared (the closest backlog candidate SC-006/007 documented-but-unenforced-gate cluster is a different class; no `**Closes:** SC-NNN` sentinel header in this slice).
- INST-1 install audit + PMI-1 plugin-manifest audit — no `tools/*.py` module added by this slice → `_CANONICAL_TOOLS` / `_ROOT_ONLY_TOOLS` / `plugin.yaml` tools-block all UNCHANGED (BC-PROJ-9 fan-out does NOT fire here — see "Why-none" note below).

## Components touched

### `skills/code-review/SKILL.md` (modified)

- **Responsibility**: orchestrator prose for `/code-review` — Claude reads this SKILL.md at runtime, executes the bash in Step 1, then hands the result file-set to the code-Critic agent in Step 2.
- **Lives at**: `skills/code-review/SKILL.md` (existing — slice-060)
- **Key interactions**: invoked in-loop by `/build-slice`'s auto-advance per PCA-1 chain; spawns `subagent_type: "code-review"` agent at `agents/code-review.md`; writes findings to `architecture/slices/slice-NNN-<name>/code-review.md`. Forward-synced to `~/.claude/skills/code-review/SKILL.md` per OSDG-1 mini-CAD.

### `tests/skills/code_review/test_code_review_skill.py` (modified)

- **Responsibility**: structural-anchor tests for `/code-review` SKILL.md prose — pin invariants Claude relies on at runtime (PCA-1 chain shape, walking-skeleton self-dogfood artifact, Step 1 union-of-three-sources read mechanism).
- **Lives at**: `tests/skills/code_review/test_code_review_skill.py` (existing — slice-060, repointed at slice-062)
- **Key interactions**: imports `tests.methodology.conftest._resolve_slice_dir` (slice-056 R-15 helper); reads `skills/code-review/SKILL.md` directly. No subprocess / Agent spawn — pure prose-pin assertions.

## Contracts added or changed

None. This slice does NOT add a new CLI, endpoint, event, or API contract. It modifies the `/code-review` SKILL.md prose (an executable contract for Claude at runtime). The runtime contract change is described entirely by ACs 1, 3 (Step 1 union shape + Step 2 prompt-template alignment) and pinned by the three prose-pin tests.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). This slice introduces NO new modules (no `tools/*.py`, no `skills/*/SKILL.md`, no `agents/*.md`). Mission-brief AC 1 names `skills/code-review/SKILL.md` as a **modified** surface, not a **new** module. Per WIRE-1's documented scope ("Every new module/file this slice introduces"), the matrix is empty by construction — the audit treats zero-row matrices as clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-062]] — mirror NAW-1 union-of-three-sources read mechanism onto `/code-review` SKILL.md Step 1; mints no new rule; supersedes nothing; reversibility: **cheap**.

## Authorization model for this slice

No authorization surface. `/code-review` is an in-loop methodology step invoked by Claude under the user's session; no multi-user / multi-tenant / external-API auth applies.

## Error model for this slice

The Step 1 error cases — `default-branch-unresolvable` and `no-code-changes` — are PRESERVED verbatim from the slice-060 baseline. The fix narrows the SET of states that legitimately produce `no-code-changes`:

- **Pre-fix**: `no-code-changes` fires for ANY slice with uncommitted Step-6 WT work (false-positive on every governed slice).
- **Post-fix**: `no-code-changes` fires ONLY for a slice whose union of (working-tree-vs-base + untracked + commits-vs-base) is genuinely empty — e.g., a methodology-changelog-only edit reverted before Step 6, or a vault-only edit excluded by the in-scope path filter.

No new error code or status added. The CRSI-1 walking-skeleton v1 advisory-only disposition (slice-060 / ADR-059) is unchanged — findings remain advisory, no verdict-driven block.

## Why-none audit-bookkeeping notes

Recorded explicitly per MEPD-1(b) discharge against the **real** META-1 enforcing assertion at `tests/methodology/test_methodology_changelog.py:136` (`re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", changelog, flags=re.MULTILINE)` + `Rule reference` substring check on each split section):

- **Inclusion heuristic FIRES** (this slice DOES warrant a methodology-changelog v0.67.0 entry + ADR-062 + 5-part PMI-1 bump + shippability row #64 pin pair). Precedent: N=8 cumulative inclusive of slice-064 on scope-extension class (slice-049 OSDG-1 mint + slice-050 AVFS-1 + slice-051 OSDG-1 member-add + slice-057 OSDG-1 + slice-058 AVFS-1 + slice-059 TVFS-1 + slice-062 R-15 scope-extension = 7 prior + slice-064 NAW-1 pattern extension to /code-review surface = **N=8 inclusive**; the slice-064 entry is a sibling-surface application of an existing read mechanism, NOT a retirement-discharge / pure-conformance shape — the voluntary-restraint posture from slice-040/043/045/056/057 N=5 retirement-discharge precedent is the WRONG precedent class here).
- **BC-PROJ-9 inventory fan-out does NOT fire** — this slice adds zero `tools/*.py` modules, zero `skills/*/SKILL.md` files (it modifies one existing), zero `agents/*.md` files. Per slice-063 shippability row #63 canonical 5-set: `install_audit._CANONICAL_TOOLS` + `test_utf8_stdout._ROOT_ONLY_TOOLS` + `plugin.yaml` tools-block + `INSTALL.md` tool-count literals (L22 + L166) + the new shippability row — for slice-064 the first 4 inventories are UNCHANGED (no new tool); the 5th (shippability row #64) IS added by this slice but does NOT trigger BC-PROJ-9 fan-out (the row exists for BCR-1 traceability + entry-pin propagation, not for new-`tools/*.py` registration). PMI-1 audit clean on master.
- **NAW-1 audit MUST exit `0` (clean, quiet) on this slice's own /build-slice Step 6 run** — the slice adds zero `agents/*.md` deltas (verified at /design-slice by inspecting the planned diff scope). If NAW-1 warns at Step 6, the slice scope has unexpectedly leaked an agent file and the slice should HALT for re-scoping.
- **No SUP-1 supersession ADR** — ADR-062 extends an existing pattern; nothing is superseded. The slice-063 NAW-1 audit + ADR-061 + R-18-retirement are all preserved verbatim (slice-040 R-10 retirement-precedent for prior-prose preservation).
- **No CAD-1 / mini-CAD member addition** — `/code-review` SKILL.md is already in the OSDG-1 guarded set (slice-060 added `test_code_review_skill_drift.py`); this slice REUSES the existing guard, does not add a new family member.
- **No PCA-1 chain edit** — the canonical chain (slice-060 9-entry chain at `tools/pipeline_chain_audit.py:73-82`) is untouched; this slice's edits are INTERNAL to Step 1 / Step 2 of `/code-review` SKILL.md, not chain-shape.

## Build-phase sequence

Per **EPGD-1** discipline (entry-pin granularity), executed in this order at /build-slice:

### Phase A — Step 1 union-of-three-sources rewrite

1. Edit `skills/code-review/SKILL.md` Step 1 bash block (L40-44): replace the single `git diff` line with the three-command union block (sources i + ii + iii); preserve the surrounding `default=$(…)` + `base=$(git merge-base …)` resolver chain verbatim.
2. Run AC 2 repro test (`test_skill_md_step_1_diff_resolution_uses_union_of_three_sources`) — assert FAIL → PASS transition. Empirical-audit-execution discipline per slice-062 /critique-review M-add-1 lesson.

### Phase B — Step 1 shape-pin test + Step 2 alignment

3. Add AC 1 test `test_skill_md_step_1_all_three_legs_share_filter_shape` (PENDING → WRITTEN-FAILING → PASSING).
4. Edit `skills/code-review/SKILL.md` Step 2 prompt-template `# Diff content` block (L84-85): change `git diff <base>...HEAD -- <files>` to `git diff "$base" -- <files>` (working-tree-vs-base, observes uncommitted edits). Aligns with Step 1 resolution.
5. Add AC 3 test `test_skill_md_step_2_diff_content_block_aligned_with_step_1` (PENDING → WRITTEN-FAILING → PASSING).

### Phase C — OSDG-1 forward-sync

6. `cp skills/code-review/SKILL.md ~/.claude/skills/code-review/SKILL.md` (the in-repo↔installed mini-CAD forward-sync).
7. Run `tests/methodology/test_code_review_skill_drift.py` — assert PASS (AC 4). Per /critique-review M-add-1 fix: the drift-guard file lives in `tests/methodology/`, NOT `tests/skills/code_review/` (the OSDG-1 family convention; the original /critique B1 fix corrected the AC#4 row + Verification plan + design.md L23 sites but missed this Phase C step + mission-brief L21 + mid-slice smoke command — TPHD-1 sub-mode (a) sweep completed at /critique-review fix block).

### Phase D — Methodology-rules bookkeeping

8. Add ADR-062 file at `architecture/decisions/ADR-062-extend-naw-1-pattern-to-code-review.md`.
9. Append `## v0.67.0 — 2026-05-23` entry to `methodology-changelog.md` (Inclusion-heuristic entry shape: header + Rule reference + ADR-062 + extends-NAW-1 + 5-part PMI-1 + Inclusion-heuristic-class).
10. Forward-sync installed `~/.claude/methodology-changelog.md` (MCFS-1).
11. 5-part PMI-1 atomic bump: bump `VERSION` (0.66.0 → 0.67.0) + `plugin.yaml.version` (matching) + `pyproject.toml [project].version` (matching) + the `## v0.67.0` header already added (step 9) + installed `~/.claude/ai-sdlc-VERSION` (AVFS-1 forward-sync — copy in-repo VERSION to installed).
12. Add entry-pin pair to `tests/methodology/test_methodology_changelog.py` — `test_v_0_67_0_naw_extend_entry_present_in_repo` (EPGD-1 8-anchor list) + `test_v_0_67_0_naw_extend_shippability_consumer_propagation` (BCR-1 traceability axis pin).
13. Add AC 5 test placeholder resolution — pin the methodology-changelog entry shape (step 9's anchors) by renaming the AC 5 PENDING test to its final name `test_v_0_67_0_naw_extend_entry_present_in_repo`.

### Phase E — Shippability row #64 finalization

14. Edit shippability.md row #64 (added at /repro Step 5 as a stub) — expand the `Description` cell to cite the full BCR-1-traceability axis (ADR-062 + NAW-1 / ADR-061 + R-18-retired), the `Regression =` clause covering the exact contract this row pins, and add the entry-pin tests to the `Command` cell.

### Phase F — TVFS-1 self-installation + final audit sweep

15. `$PY -m pip install --upgrade .` (refresh installed venv `ai-sdlc-tools` to 0.67.0 so TVFS-1 exits 0 at Step 6).
16. Run /build-slice Step 6 pre-finish gate — full audit fan-out (TF-1, PMI-1, PVFS-1, AVFS-1, MCFS-1, TVFS-1, NAW-1, OSDG-1 drift family, BC-1, WIRE-1, ETC-1, CSP-1, CAD-1, SUP-1, LINT-MOCK-1/2/3, pipeline-chain, etc.). NAW-1 exits 0 quietly (this slice adds no `agents/*.md`); all other audits clean.

## Forward-sync points

OSDG-1 mini-CAD member `skills/code-review/SKILL.md` is the SOLE *new-surface* forward-sync this slice touches (`~/.claude/skills/code-review/SKILL.md`). The standard version-bump forward-syncs (MCFS-1 methodology-changelog + AVFS-1 ai-sdlc-VERSION + PVFS-1 pyproject.toml + PMI-1 plugin.yaml.version) are mechanical copies governed by their pre-existing gates and fan out from the 5-part PMI-1 atomic bump.

## Risks specific to this slice

- **R-X1 (declined to register — too narrow)**: a future SKILL.md surface that legitimately reads `git diff <base>...HEAD` for a non-Step-6 invocation (e.g., a hypothetical post-commit batch tool reading committed history) could be incorrectly flagged by the AC 1 shape-pin test if the test is scoped beyond Step 1. Mitigation: the AC 1 test is **strictly Step 1 section-scoped** via `body.find("### Step 1:")` to `body.find("### Step 2:")` — the same section-scoping pattern slice-061 AC 4 used for the Step 1 python-detection chain pin. No false-positive surface beyond Step 1 prose.
- **R-X2 (declined to register — pattern is precedent-anchored)**: a future NAW-1 audit refactor that changes the three command argv shapes (e.g., adds a `--source` flag for testability) could cause a "shape mirror" drift between NAW-1 audit-tool and /code-review SKILL.md prose. Mitigation: this slice deliberately does NOT mint a cross-pin asserting "Step 1 prose EQUALS `_resolve_added_agent_files` shape". The two surfaces share a CONCEPTUAL pattern (union-of-three-sources) but are independent implementations (Python subprocess vs Claude-executed bash). Future drift in either direction is acceptable so long as the conceptual contract holds — the three sources cover working-tree-vs-base + untracked + commits-vs-base.
- **R-X3 watch-list — wide-slice Step 2 per-file diff token cost (N=1; /critique M3 ACCEPTED-FIXED)**: the Step 2 prompt-template change from aggregate (`git diff <base>...HEAD -- <files>`) to per-file (`git diff "$base" -- <file>`) scales O(N) in git invocations + per-file `diff --git` headers + per-command shell overhead. For a typical 5–10-file slice this is fine; for a wide-refactor slice with 30+ files (slice-060 touched ~20; slice-063 NAW-1 touched 8) the per-file form adds 30+ git invocations + headers + command overhead, increasing prompt-token surface proportionally. The existing SKILL.md L85 fallback prose ("if diff exceeds budget, list paths and let agent Read individual files") is preserved post-fix but **not load-bearing-tested at AC level**. N=1 observation this slice; if a future wide-refactor slice's `/code-review` step hits budget overflow at the per-file form, promote to a dedicated slice that pins (a) a numerical budget threshold or (b) an "aggregate per-N-files batched" fallback. Watch-list `/critic-calibrate` candidate — promote at N=2.
