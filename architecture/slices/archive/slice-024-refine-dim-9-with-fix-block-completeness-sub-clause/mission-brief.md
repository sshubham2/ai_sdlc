# Slice 024: refine-dim-9-with-fix-block-completeness-sub-clause

**Mode**: Standard
**Estimated work**: ~1 day (codification slice; ~3-surface schema-pin shape; Critic-stack budget high per slice-023 codification-slice density observation)
**Risk retired**: PROACTIVE — no direct risk-register entry. Informally retires "fix-block-completeness recurring as the dominant meta-Critic catch-class on codification slices" by promoting from informal Meta-Critic discipline to first-Critic-prompt-codified rule (FBCD-1). Empirical basis: **N=10 cumulative cross-instances across 4 distinct slices** (slice-020 M-add-1 N=1 + slice-021 M-add-1-rerun + M-add-2-rerun + M-add-3-rerun N=3 + slice-022 M-add-2 + M-add-3 N=2 + slice-023 M-add-1 + M-add-2 + M-add-3 + M-add-4 N=4); cumulative well past project's N=2-cross-slice proactive codification convention (EPGD-1 + SCPD-1 precedent).
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Codify a new 10th Dim 9 sub-clause **FBCD-1 — Fix-Block-Completeness Discipline** in `~/.claude/agents/critique.md` covering two sub-modes that have empirically recurred as dominant Critic-stack catch class:

- **Sub-mode (a) Original-draft cross-file consistency** — first-Critic catch at /critique time. When a slice authors a claim (file path, count, ADR ID, test function name, rule ID, anchor literal) across multiple files (mission-brief.md + design.md + ADR-NNN + milestone.md), the Critic must verify the claim is identical at every site. Concrete misses: slice-022 N=1 NEW class + slice-023 N=2 (B5 17/17/17 count drift across mission-brief AC #2 + design.md L120/121/130/131 + L225 + L344; B3 `tests/decisions/` ADR-pin path drift across mission-brief + design.md) = N=3 cumulative under sub-mode (a) per slice-023 reflection Pattern 4 enumeration.

- **Sub-mode (b) Post-ACCEPTED-FIXED sibling-sweep** — meta-Critic catch at /critique-review time. When Builder applies an ACCEPTED-FIXED fix at one site, sibling sites carrying the same claim may still carry the OLD value. Meta-Critic must grep for the anchor substring across all slice-authoring files post-fix. Concrete misses: slice-020 M-add-1 (N=1) + slice-021 M-add-1-rerun/2-rerun/3-rerun (N=3) + slice-022 M-add-2/3 (N=2) + slice-023 M-add-1/2/3/4 including M5 test-file split sibling sites at design.md L194 + mission-brief.md L54 + ADR-021 L73 (N=4) = **N=10 cumulative**.

FBCD-1 is the **temporal extension** of Dim 9 sub-clause 2 (design.md tables vs canonical inventory, CCC-1 v1.1 / slice-009). Sub-clause 2 catches mechanical-table-vs-inventory drift on the initial draft against an EXTERNAL canonical inventory; FBCD-1 catches drift WITHIN-slice across mission-brief.md + design.md + ADR-NNN + milestone.md (sub-mode a) and EXTENDS to post-ACCEPTED-FIXED sibling-site propagation (sub-mode b). The two sub-modes match the RPCD-1 / EPGD-1 / SCPD-1 multi-sub-mode codification template.

## Acceptance criteria

1. `agents/critique.md` (in-repo) carries a new 10th sub-clause titled "Fix-block-completeness discipline" under Dimension 9, positioned BETWEEN existing sub-clause 9 ("Runtime-prerequisite completeness on proposed fixes") AND `### Bonus: weak graph edges` end anchor, with body naming sub-mode (a) Original-draft cross-file consistency + sub-mode (b) Post-ACCEPTED-FIXED sibling-sweep + cross-slice citations of slices 020/021/022/023 + canonical rule-ID `FBCD-1` pinned literally.
2. `agents/critique.md` (installed at `~/.claude/agents/critique.md`) is byte-equal to in-repo per CAD-1 — `$PY -m tools.critique_agent_drift_audit --repo-root .` exits 0.
3. `methodology-changelog.md` (in-repo + installed) carries a new v0.38.0 entry codifying FBCD-1 with prose-pin anchors (rule ID `FBCD-1` + both sub-mode names + cross-slice anchors 020/021/022/023 + N=10 cumulative cross-instance citation); atomic version bump 0.37.0 → 0.38.0 with zero PMI-1 v1.1 gate-body modification (PMI-1 retirement-proof N=10 stable).
4. `architecture/decisions/ADR-022-fbcd-1-fix-block-completeness-discipline.md` created (reversibility: cheap; supersedes: null; status: accepted) with rationale citing N=10-cumulative-cross-slice empirical basis + 2-sub-mode codification design + temporal-extension-of-sub-clause-2 relationship.
5. `architecture/shippability.md` row 24 appended with inline Command cell exercising FBCD-1's critical path (critique-agent prose-pin tests + v0.38.0 entry-pin tests + ADR-022 entry-pin test + CAD-1 byte-equality + PMI-1 invariant gate).

## Test-first plan

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING -> PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | prose-pin | tests/methodology/test_critique_agent.py | test_critique_dim_9_lists_ten_sub_clauses (SUPERSEDES `test_critique_dim_9_lists_nine_sub_clauses` per PMI-1 structural-invariant supersession at structural-invariant level — N=4 cumulative supersession events pre-slice-024: slice-011 ratchet 5→6; slice-013 6→7; slice-015 7→8; slice-016 8→9; this slice 9→10 = 5th ratchet event, N=5 post-slice-024) | PASSING |
| 1 | prose-pin | tests/methodology/test_critique_agent.py | test_critique_dim_9_fix_block_completeness_sub_clause_present | PASSING |
| 1 | prose-pin | tests/methodology/test_critique_agent.py | test_critique_dim_9_fix_block_completeness_location_pinned (between "Runtime-prerequisite completeness on proposed fixes" and "### Bonus: weak graph edges") | PASSING |
| 1 | prose-pin | tests/methodology/test_critique_agent.py | test_critique_dim_9_fix_block_completeness_names_both_sub_modes | PASSING |
| 1 | prose-pin | tests/methodology/test_critique_agent.py | test_critique_dim_9_fix_block_completeness_paragraph_cites_slice_020_021_022_023 | PASSING |
| 1 | prose-pin | tests/methodology/test_critique_agent.py | test_critique_dim_9_fix_block_completeness_cites_substantive_discipline_anchors | PASSING |
| 2 | byte-equality | tests/methodology/test_critique_drift.py | (existing test_critique_agent_byte_equal_installed; covered by re-running CAD-1 audit at /build-slice Phase 4 forward-sync) | PASSING |
| 3 | entry-pin | tests/methodology/test_methodology_changelog.py | test_v_0_38_0_fbcd_1_entry_present_in_repo_and_installed | PASSING |
| 3 | entry-pin | tests/methodology/test_methodology_changelog.py | test_v_0_38_0_fbcd_1_names_both_sub_modes | PASSING |
| 3 | entry-pin | tests/methodology/test_methodology_changelog.py | test_v_0_38_0_fbcd_1_cites_slice_020_021_022_023 | PASSING |
| 3 | PMI-1 gate | tests/methodology/test_methodology_changelog.py | (existing PMI-1 v1.1 atomic version-bump invariant — v0.37.0 → v0.38.0; gate body unchanged) | PASSING |
| 4 | entry-pin | tests/methodology/test_methodology_changelog.py | test_adr_022_exists_and_names_fbcd_1_canonical_phrase | PASSING |
| 5 | shippability-row | architecture/shippability.md | row 24 inline Command cell executed via /validate-slice Step 5.5 catalog regression (NO `test_shippability_catalog.py` exists — catalog is validated by Step 5.5 command execution, not a structural pytest; corrected at /validate-slice per slice-023 B4 precedent "no per-row test-file convention exists") | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | New sub-clause in critique.md | `$PY -m pytest tests/methodology/test_critique_agent.py -v -k 'fix_block_completeness or lists_ten_sub_clauses'` returns 6 PASS |
| 2 | CAD-1 byte-equality | `$PY -m tools.critique_agent_drift_audit --repo-root .` exits 0 (in-repo ↔ installed byte-equal) |
| 3 | v0.38.0 entry + atomic bump | `$PY -m pytest tests/methodology/test_methodology_changelog.py -v -k 'v_0_38_0 or atomic_bump'` returns 4 PASS |
| 4 | ADR-022 entry-pin | `$PY -m pytest tests/methodology/test_methodology_changelog.py -v -k 'adr_022'` returns 1 PASS |
| 5 | Shippability row 24 | /validate-slice Step 5.5 executes every catalog row's Command; row 24 Command cell (FBCD-1 critical path) exits 0 AND full catalog 24/24 PASS (no regression). No `test_shippability_catalog.py` — catalog validation IS Step 5.5 command execution. |

## Must-not-defer

- [ ] **CAD-1 byte-equality** preserved post-edit — in-repo `agents/critique.md` ↔ installed `~/.claude/agents/critique.md` byte-equal at slice ship; forward-sync at /build-slice Phase 4.
- [ ] **PMI-1 v1.1 atomic version bump** 0.37.0 → 0.38.0 with zero gate-body modification (slice-007 v1.0 → slice-014 v1.1 introduction; N=10 stable post-this-slice).
- [ ] **EPGD-1 self-application** — Phase 1b v0.38.0 entry-pin INSERT (3 entry-pin functions + 1 ADR-pin function: `test_v_0_38_0_fbcd_1_entry_present_in_repo_and_installed`, `..._names_both_sub_modes`, `..._cites_slice_020_021_022_023`, `test_adr_022_exists_and_names_fbcd_1_canonical_phrase`) MUST live under a NEW dedicated SECTION header `# --- Slice-024 / FBCD-1 entry pinning ---` in `tests/methodology/test_methodology_changelog.py`. PMI-1 v1.1 versioned-gate function body (`test_plugin_yaml_version_matches_version_file_invariant`) is NOT edited this slice — atomic version-bump invariant is version-agnostic per slice-014 ADR-013. The PMI-1 structural-invariant supersession in Phase 1c (`_lists_nine_sub_clauses` → `_lists_ten_sub_clauses` in `tests/methodology/test_critique_agent.py`) is a function-name rename + canonical-literal bump (different module, different discipline class) — narrow-scoped trivially because it doesn't span any other test functions.
- [ ] **SCPD-1 self-application** — shippability row 24 added in same /build-slice block BEFORE /validate-slice catalog run; any existing rows referencing `_lists_nine_sub_clauses` propagate to `_lists_ten_sub_clauses` proactively at Phase 5 (mirrors slice-016 rows 6/11/13/15 propagation precedent).
- [ ] **RPCD-1 self-application** — all NEW symbols / tokens / anchors in test bodies (sub-mode a/b names, slice anchors 020/021/022/023, FBCD-1 literal) verified imported / accepted by audits / grep-verified for sibling-anchor uniqueness BEFORE /critique disposition triage finalizes.
- [ ] **RSAD-1 self-application** — slice's OWN mission-brief.md + design.md + ADR-022 + critique.md edits + methodology-changelog v0.38.0 entry self-checked against FBCD-1's two sub-modes (fix-block-completeness applied to the slice that codifies it). Empirically expected N≥1 FBCD-1 catch on slice's own drafts per recursive-self-application closure observed at slice-009..023.
- [ ] **TPHD-1 self-application** — every /critique disposition promising "will add test X at /build-slice" MUST be enumerated in the TF-1 plan rows above (sub-mode (c) pre-flight catches any disposition-promised test absent from TF-1 plan).
- [ ] **BRANCH-1 self-application** — slice runs on feature branch `slice/024-refine-dim-9-with-fix-block-completeness-sub-clause` created at /build-slice Prerequisite-check Branch state sub-section; /commit-slice mode flag per ADR-020 (--merge, --push, or --sync-after-pr depending on workflow).
- [ ] **UTF8-STDOUT-1 self-application** — no new audit tool planned this slice; vacuously satisfied. If any pre-flight audit emits mojibake `�` for em-dash, environment cp1252 leak — diagnose before continuing.
- [ ] **LAYER-EVID-1 self-application** — no /diagnose layering work; vacuously satisfied.

## Out of scope

- **Pattern 4 (cross-mission-brief-vs-design-consistency-checking) as a SEPARATE Dim 9 sub-clause** — folded into FBCD-1 sub-mode (a) since Pattern 4 is the temporally-earlier surface (draft time) of the same fix-block-completeness discipline (post-fix sub-mode b is the same shape applied later). Cumulative N=3 within sub-mode (a) per slice-023 reflection Pattern 4 enumeration (slice-022 N=1 + slice-023 N=2: B5 count drift + B3 ADR-pin path drift). M5 (test-file split sibling sites) belongs to sub-mode (b) post-ACCEPTED-FIXED sibling-sweep, not sub-mode (a) original-draft.
- **TPHD-1 sub-mode (c) extension** naming "disposition-promised-test-not-enumerated-in-TF-1-plan" as Dim 9 sub-clause — already covered structurally by existing TPHD-1 sub-mode (c) at /critique skill prose level + /build-slice pre-flight audit; this slice does NOT modify TPHD-1.
- **Auto-mode classifier as third-Critic-stack-layer** codification — structurally outside Critic prompt scope per slice-023 reflection's calibration analysis; lives at /build-slice + /validate-slice Builder-side tool-use layer, not in `~/.claude/agents/critique.md`. Deferred to future /critic-calibrate run OR accepted as out-of-Critic-prompt-scope.
- **Any new audit tool** or build-check rule.
- **Any change to existing 9 Dim 9 sub-clauses' bodies** — FBCD-1 is purely additive at sub-clause 10 position. The 9 existing sub-clauses remain byte-equal.
- **Modifying TPHD-1 or RPCD-1 cross-references** — FBCD-1 cross-references existing Dim 9 sub-clauses 2 + 9 via body prose, not via mutation of those sub-clauses' bodies.

## Dependencies

- **Prior slices** (codification templates):
  - [[slice-013-refine-dim-9-with-entry-pin-vs-pmi-1-gate-sub-clause]] — first Dim 9 sub-clause append template (EPGD-1; 8th sub-clause)
  - [[slice-015-refine-dim-9-with-shippability-catalog-propagation-sub-clause]] — 9th sub-clause template (SCPD-1)
  - [[slice-016-refine-dim-9-with-runtime-prerequisite-completeness-sub-clause]] — 10th sub-clause template (RPCD-1; **closest structural precedent** — multi-sub-mode codification, 3-surface schema-pin)
  - [[slice-023-audit-tools-default-utf8-stdout]] — N=4 within-slice evidence anchor + reflection promotion-eligibility tag (Pattern 3 + Pattern 4)
  - [[slice-020-codify-bug-fix-repro-prelude-at-slice]], [[slice-021-add-feature-branch-workflow-at-build-and-commit-slice]], [[slice-022-redesign-commit-slice-for-pr-aware-flow]] — N=1, N=2, N=2 cross-slice evidence for FBCD-1 sub-mode (b)
- **Vault refs**:
  - [[agents/critique.md]] Dim 9 (9 existing sub-clauses → 10 after this slice)
  - [[methodology-changelog.md]] v0.37.0 (current) → v0.38.0 (new)
  - [[decisions/ADR-013]] (EPGD-1 ADR), [[decisions/ADR-014]] (SCPD-1 ADR), [[decisions/ADR-015]] (RPCD-1 ADR) — prior Dim 9 sub-clause codification ADRs as structural templates
  - [[architecture/critic-calibration-log.md]] — calibration runs through 2026-05-13 (post-slice-015 full window); slice-024 is the FIRST codification slice WITHOUT a prior dedicated /critic-calibrate run authorizing its codification — empirically applies project's N=2-cross-slice proactive codification convention (EPGD-1 + SCPD-1 precedent). Documented at ADR-022 rationale.
  - [[architecture/shippability.md]] — 23 rows (current) → 24 rows (after this slice)
- **Risk register**: no new risks introduced; R-1 / R-2 / R-3 untouched.

## Mid-slice smoke gate

At ~50% of /build-slice (after Phase 1-3 of build plan: critique.md edited + prose-pin tests added + methodology-changelog v0.38.0 entry written, BEFORE ADR-022 and shippability row 24):

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
$env:PYTHONIOENCODING = "utf-8"
& $PY -m pytest tests/methodology/test_critique_agent.py -v -k 'fix_block_completeness or lists_ten_sub_clauses' --tb=short
& $PY -m pytest tests/methodology/test_methodology_changelog.py -v -k 'v_0_38_0 or atomic_bump' --tb=short
& $PY -m tools.critique_agent_drift_audit --repo-root .
& $PY -m tools.test_first_audit architecture/slices/slice-024-refine-dim-9-with-fix-block-completeness-sub-clause --strict-pre-finish
```

**Expected**: 6 critique-agent prose-pin tests PASS + 4 changelog tests PASS + critique-agent drift-audit exit 0 + TF-1 audit clean (all rows PASSING; intermediate WRITTEN-FAILING / PENDING transitioned correctly).

**If ANY fail**: STOP, diagnose, don't continue:
- prose-pin failure → critique.md body shape mismatch; re-read existing sub-clauses 7/8/9 for template alignment
- changelog test failure → v0.38.0 entry shape mismatch; check anchor literals against test asserts
- drift-audit failure → forward-sync to installed dropped; redo /build-slice Phase 4 (critique.md forward-sync) and Phase 3 (changelog forward-sync)
- TF-1 audit failure → row count drift OR status non-PASSING; this is exactly the class FBCD-1 codifies

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence captured in validation.md
- [ ] Must-not-defer list (10 items) fully addressed; each item's verification documented in validation.md
- [ ] `/drift-check` passes (vault claims ↔ code reality clean)
- [ ] Mid-slice smoke still passes (no regression on critique-agent + changelog tests after late-phase edits)
- [ ] No new TODOs / FIXMEs / debug prints introduced this slice
- [ ] **Critic-stack budget pre-allocation**: N≥10 first-Critic + N≥3 meta-Critic findings expected on slice's own drafts (per slice-023 codification-slice density observation: SMALL-by-LOC ≠ SMALL-by-vault-claim-density; design.md / mission-brief.md / ADR-022 / critique.md edit / changelog v0.38.0 entry = high path-count / convention-count / count-claim density expected to attract Dim 9 sub-clause 2 + FBCD-1 self-application catches at /critique stress-test).
- [ ] **FBCD-1 self-application empirical evidence captured** in reflection.md (recursive-self-application closure: how many FBCD-1 sub-mode (a) catches fired on slice's own mission-brief/design/ADR drafts at /critique; how many sub-mode (b) catches fired at /critique-review on Builder's own ACCEPTED-FIXED sweeps). Empirically expected N≥1 to confirm the codification's empirical anchor still holds.
- [ ] **PMI-1 v1.1 audit clean** post-bump (atomic 0.37.0 → 0.38.0; entry-pin functions count = 16 → 17 stable; gate function body unchanged).
- [ ] **BRANCH-1 audit clean** at /build-slice Step 6 pre-finish (`tools/branch_workflow_audit.py` verifies feature-branch shape).
- [ ] **All Dim 9 cross-references resolve** (existing `test_critique_dim_9_cross_references_resolve` still PASS post-edit — new sub-clause's cross-reference to sub-clause 2 + 9 doesn't break existing pointers).
