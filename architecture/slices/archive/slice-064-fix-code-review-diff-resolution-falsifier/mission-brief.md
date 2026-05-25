# Slice 064: fix-code-review-diff-resolution-falsifier

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: B1 falsifier class N=2 cumulative (NAW-1 retired the class on its own audit-tool surface at slice-063; this slice retires it on the `/code-review` SKILL.md surface — the second known surface)
**Test-first**: true  <!-- BFRD-1 prelude established the failing repro at /repro (2026-05-23); 1 PENDING regression-guard test + 1 prose-pin already WRITTEN-FAILING -->
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`/code-review` SKILL.md Step 1 currently resolves the slice diff with a single `git diff "$base"...HEAD --name-only` command — commit-vs-commit only. At `/build-slice` Step 6 (where `/code-review` auto-advances from per the canonical PCA-1 chain), slice work is uncommitted in the working tree because commits land at `/commit-slice` per the PCA-1 HARD-STOP terminal contract. The single-command resolution returns EMPTY, the `no-code-changes` branch silently writes `Result: NO-CODE-CHANGES — nothing to review`, and auto-advance proceeds — every governed slice's in-loop code review is a silent false-positive on the clean-tree-from-Step-6 invocation.

Mirror slice-063 NAW-1 / ADR-061 §Decision's union-of-three-sources read mechanism (working-tree-vs-base + `git ls-files --others --exclude-standard` + commits-vs-base) onto `/code-review`'s Step 1 so every state slice work can occupy at `/build-slice` Step 6 is observable. The `no-code-changes` branch then fires only on a genuinely empty slice (e.g., a methodology-changelog-only edit reverted before Step 6) instead of false-positive-ing on every governed slice.

## Acceptance criteria

1. `skills/code-review/SKILL.md` Step 1 carries all three union-of-three-sources commands: working-tree-vs-base (`git diff "$base" --name-only`), untracked (`git ls-files --others --exclude-standard`), and commits-vs-base (`git diff "$base"...HEAD`); identical filter / exclusion shape on each leg (`--diff-filter=ACMR --name-only` and the architecture/docs path exclusions where applicable).
2. The BFRD-1 repro test `tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_diff_resolution_uses_union_of_three_sources` PASSES (currently WRITTEN-FAILING on the master baseline).
3. `skills/code-review/SKILL.md` Step 2 prompt-template `# Diff content` block is consistent with Step 1's resolution — no stale `git diff <base>...HEAD -- <files>` language that contradicts the union-of-three-sources scope (Step 2 must reference the SAME file set Step 1 emitted, not re-run a different command).
4. OSDG-1 / mini-CAD drift guard clean: in-repo `skills/code-review/SKILL.md` content-equal modulo EOL to installed `~/.claude/skills/code-review/SKILL.md` (EOL-DRIFT-1 EOL-agnostic per ADR-033); `tests/methodology/test_code_review_skill_drift.py` passes.
5. Methodology-rules bookkeeping: methodology-changelog v-entry + paired entry-pin tests + ADR + atomic PMI-1 version bump shape decided at `/design-slice` (Inclusion-heuristic vs no-VERSION-bump conformance class judgement is `/design-slice` scope per MEPD-1(b)). At minimum, the v-entry/ADR/bump decision is recorded with a `Why-none` justification if no-bump is chosen, and the existing slice-063 shippability row #63's `Regression =` clause is NOT silently altered by this slice (regression class preservation per slice-040 R-10 precedent).

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0). BFRD-1 prelude pre-established the failing repro at `/repro` (slice-064 confirm-then-auto-invoke); the prose-pin row is already WRITTEN-FAILING on the master baseline. Status rows progress PENDING → WRITTEN-FAILING → PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 2 | structural | tests/skills/code_review/test_code_review_skill.py | test_skill_md_step_1_diff_resolution_uses_union_of_three_sources | PASSING |
| 1 | structural | tests/skills/code_review/test_code_review_skill.py | test_skill_md_step_1_all_three_legs_share_filter_shape | PASSING |
| 1 | structural | tests/skills/code_review/test_code_review_skill.py | test_skill_md_step_1_union_aggregation_prose_pinned | PASSING |
| 3 | structural | tests/skills/code_review/test_code_review_skill.py | test_skill_md_step_2_diff_content_block_aligned_with_step_1 | PASSING |
| 4 | drift-guard | tests/methodology/test_code_review_skill_drift.py | test_in_repo_and_installed_code_review_skill_md_are_content_equal | PASSING |
| 5 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_67_0_naw_extend_entry_present_in_repo | PASSING |
| 5 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_67_0_naw_extend_shippability_consumer_propagation | PASSING |

AC 1 carries two rows: the filter-shape pin + the runtime-union-aggregation prose pin (per /critique M2 — Claude's runtime obligation to union + deduplicate the three command outputs must be SKILL.md-prose-pinned, not ADR-only). AC 5 carries two rows: the entry-pin + the paired shippability-consumer-propagation pin (per /critique B2 / slice-060 M-add-2 N≥17 BC-PROJ-10:173 precedent). Bare-numeric AC labels per slice-056 + slice-062 N=2 TF-1 multi-AC-label sub-class lesson — never `"1, 3"` or `"(audit-trace)"` annotations (TF-1 `_normalize_ac_label` rejects).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Step 1 union-of-three-sources | Read `skills/code-review/SKILL.md` Step 1 section; grep for all three commands; assert identical filter shape across legs |
| 2 | Repro test passes | `$PY -m pytest tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_diff_resolution_uses_union_of_three_sources` exits 0 |
| 3 | Step 2 prompt-template aligned | Read Step 2 section; assert no contradiction with Step 1's resolution (the file-set passed to the agent matches what Step 1 emits) |
| 4 | OSDG-1 drift clean | `$PY -m pytest tests/methodology/test_code_review_skill_drift.py` exits 0 after `cp skills/code-review/SKILL.md ~/.claude/skills/code-review/SKILL.md` forward-sync |
| 5 | Methodology bookkeeping | If Inclusion-heuristic fires: `$PY -m pytest tests/methodology/test_methodology_changelog.py -k v_0_67_0` exits 0; PMI-1 audit clean. If no-bump conformance: `Why-none` justification recorded in design.md vs the real META-1 `re.split(r"^## v\S+ — …")` assertion at `tests/methodology/test_methodology_changelog.py:136` (slice-040/043/045/056/057 precedent) |

## Must-not-defer

- [ ] Step 1 union-of-three-sources fix shape MUST be identical to NAW-1's `_resolve_added_agent_files` union shape (working-tree-vs-base + ls-files-others + commits-vs-base) — same canonical pattern, same de-duplication, same ordering rationale; cross-referenced from `tools/new_agent_warning_audit.py:_resolve_added_agent_files`.
- [ ] Step 2 prompt-template `# Diff content` block updated in the same fix block as Step 1 (do not ship a Step 1 fix with a Step 2 prompt that re-runs a stale commit-vs-commit diff command and re-introduces the falsifier downstream).
- [ ] OSDG-1 mini-CAD forward-sync to installed `~/.claude/skills/code-review/SKILL.md` (every SKILL.md edit per CLAUDE.md self-hosting discipline).
- [ ] PCA-1 chain wiring: `## Pipeline position` block at end of SKILL.md preserved verbatim (predecessor `/build-slice`, successor `/validate-slice`, auto-advance true). The fix is internal to Step 1 / Step 2; do NOT touch the chain-shape block.
- [ ] BCR-1 SC-NNN sentinel handling: if this slice closes any `diagnose-out/backlog.md` SC-\d{3} candidate, mission-brief.md OR reflection.md carries the explicit `**Closes:** SC-NNN` sentinel header so `/reflect` round-trips the backlog row. (Per current backlog read — no candidate matches this exact defect; the closest is `SC-006`/`SC-007` (documented-but-unenforced gate cluster) which is a different class. No SC-NNN closure declared at /slice time; revisit at /design-slice.)

## Out of scope

- `/code-review` v2 enhancements: TRI-1 routing, verdict-driven block on `/validate-slice`, AI-bloat passes (originally nominated for slice-061/062/063; deferred to slice-065+ per slice-063 reflection L44). This slice is a falsifier fix only; the walking-skeleton v1 advisory-only disposition is unchanged.
- slice-063 code-Critic m1 cleanup (drop dead `try/except FileNotFoundError` blocks from `tools/new_agent_warning_audit.py::_resolve_default_branch`). Different file, different defect class, different fix surface. Slice-063 reflection L42 explicitly framed this as "bundled cleanup OR separate trivial slice" — declining the bundle to keep slice-064 focused (CLAUDE.md "no while-I'm-here cleanups"). Slice-065+ trivial-cleanup candidate.
- R-17 BRANCH-1 clean-tree precondition (standing slice-061/062/063 deferral on pipeline-hygiene track). Separate `tools/branch_workflow_audit.py` audit-shape change; not a `/code-review` surface.
- R-13 OSDG-1 extension to `/slice-candidates` (standing slice-052/063 deferral, R-13 open low-band). Different SKILL.md surface; separate drift-guard family member-addition slice per slice-049/051 precedent.

## Dependencies

- Prior slices: [[slice-063-add-build-slice-new-agent-warning]] — canonical NAW-1 union-of-three-sources shape at `tools/new_agent_warning_audit.py:_resolve_added_agent_files`; ADR-061 §Decision L60-67 documents the read-mechanism rationale; this slice mirrors that pattern onto the `/code-review` SKILL.md surface.
- Prior slices: [[slice-060-add-code-review-skill]] — `/code-review` skill + agent + canonical PCA-1 chain extension; CRSI-1 walking-skeleton v1 advisory-only discipline.
- Vault refs: [[decisions/ADR-061]] (NAW-1 union-of-three-sources read mechanism), [[decisions/ADR-059]] (CRSI-1 walking-skeleton v1), CLAUDE.md `Self-hosting discipline` (skill prose IS executable contract — OSDG-1 mini-CAD applies).
- Risk register: B1 falsifier class — slice-063 retired on NAW-1 surface; this slice retires on `/code-review` SKILL.md surface (N=2 cumulative class signal, slice-063 reflection L94).

## Mid-slice smoke gate

At ~50% of build, run:

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m pytest tests/skills/code_review/test_code_review_skill.py::test_skill_md_step_1_diff_resolution_uses_union_of_three_sources tests/methodology/test_code_review_skill_drift.py -v --no-header
```

Expected: the Step-1 union-of-three-sources test PASSES (SKILL.md prose fix landed); the drift-guard test PASSES (forward-sync to installed copy completed in same fix block). If either FAILs: STOP, diagnose, do not continue.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (Step 1 union shape mirrors NAW-1; Step 2 prompt-template aligned; OSDG-1 forward-sync done; PCA-1 chain-shape block untouched; BCR-1 SC-NNN handling decided)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] TF-1 audit strict-pre-finish clean (`$PY -m tools.test_first_audit --strict-pre-finish` exits 0; all 5 rows PASSING or auditably-PENDING per AC 5's Inclusion-heuristic vs no-bump decision)
- [ ] CSP-1 / OSDG-1 / PMI-1 audits clean (skill-drift family + plugin-manifest + cross-spec parity per BC-PROJ-9 fan-out)
- [ ] NAW-1 audit clean (slice does NOT ship a new `agents/*.md` — should exit clean, NOT warn; if it does warn, the slice scope is wrong)
