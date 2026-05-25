# Design: Slice 049 add-triage-adopt-skill-drift-guards

**Date**: 2026-05-19
**Mode**: Standard

## What's new

- `tests/methodology/test_triage_skill_drift.py` — one test, `test_in_repo_and_installed_triage_skill_md_are_content_equal`, asserting `skills/triage/SKILL.md` is content-equal (EOL-agnostic) to `~/.claude/skills/triage/SKILL.md` via the shared comparator.
- `tests/methodology/test_adopt_skill_drift.py` — one test, `test_in_repo_and_installed_adopt_skill_md_are_content_equal`, same shape for `skills/adopt/SKILL.md`.
- **Exactly one** new row in `architecture/shippability.md` — `| 49 | slice-049-add-triage-adopt-skill-drift-guards | OSDG-1 …` whose Critical-path covers BOTH guards (meta-Critic B-add-1: the catalog is strictly one-row-per-slice keyed `| NN | slice-NNN-name`, latest `| 48 | slice-048-…`; one row, not two — matches the slice-048 SOAD-1 row precedent and keeps the AC3 `_shippability_consumer_propagation` pin satisfiable). Makes the OSDG-1 guard's breakage visible to the catalog runner (slice-040 lesson).
- A doc-consistency edit to `CLAUDE.md` `## Self-hosting discipline` — generalize the existing single-skill "Mini-CAD for `slice` skill" bullet so the self-hosting contract names the opener skills (`triage`, `adopt`) it now guards (done in-slice, NOT deferred to `/reflect` — slice-022 self-violation-avoidance).
- **(rev-1, Critic B2)** A `## v0.57.0` `methodology-changelog.md` entry minting RULE-ID **OSDG-1** + a 4-part PMI-1 atomic bump 0.56.0→0.57.0 (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`) + `test_v_0_57_0_osdg_1_entry_present_in_repo` + `test_v_0_57_0_osdg_1_shippability_consumer_propagation` in the **existing** `tests/methodology/test_methodology_changelog.py` + new `architecture/decisions/ADR-051-*.md`.

> **rev-1 Critic dispositions reflected in this design**: B1 (phantom `test_shippability_catalog.py`) — AC4 now cites the real `tools/shippability_runner.py` + `test_shippability_runner_segment_contract.py` + `test_shippability_path_existence.py`. B2 (false slice-035 precedent) — pre-decision withdrawn, corrected analysis below, OSDG-1/v0.57.0/ADR-051 added. M1 (prose-only AC3/AC4) — AC3 folded into AC1/AC2; every TF-1 row now cites an on-disk file. M2 (forward-sync masks pre-existing drift) — new must-not-defer pre-sync EOL-normalized-diff evidence-preservation step. m1 (uncorroborated slice-019/021 claim) — deleted in the corrected analysis. m2 (WIRE-1 format) — no-op, format verified correct.
>
> **rev-2 meta-Critic (DR-1 EXTEND) dispositions reflected**: B-add-1 (shippability "two rows" violates the one-row-per-slice convention + would make the AC3 `_shippability_consumer_propagation` pin unsatisfiable) — AC4 + §"What's new" + build-sequencing now specify **exactly ONE** row `| 49 | slice-049-… | OSDG-1 …` covering both guards (slice-048 row #48 precedent). M-add-1 (the CLAUDE.md Mini-CAD edit lands in the section the `test_root_claude_md_cad1_eol_agnostic.py` prose-pin guards, but the slice's verification surface didn't name it — slice-039 class) — new AC5 + verification row #5 + must-not-defer note explicitly re-run that pin immediately after the CLAUDE.md edit. No suspicious findings, no severity adjustments — the meta-Critic confirmed all 6 first-Critic findings VALID at filed severity and the OSDG-1/v0.57.0 remediation convention-correct.

## What's reused

- `tests/skill_drift_equality.py` → `assert_md_forward_synced(in_repo, installed, *, label)` — the single EOL-agnostic forward-sync comparator (RULE-ID EOL-DRIFT-1, [[decisions/ADR-033]]). Used unchanged; zero new comparison logic.
- `tests/methodology/conftest.py` → `REPO_ROOT` — repo-root anchor (same import the 5 existing skill-drift modules use).
- The canonical per-file shape: `tests/methodology/test_slice_skill_drift.py` / `test_query_design_skill_drift.py` (MCT-1 / slice-010 mini-CAD / slice-007 [[decisions/ADR-033]] CAD-1 pattern). The two new modules are structural twins with only path/label/docstring differing.
- Governing rule lineage (all pre-existing, unchanged): CAD-1 (slice-007), mini-CAD/MCT-1 (slice-010), EOL-DRIFT-1 (slice-033, [[decisions/ADR-033]]). This slice adds **members** to that family; it introduces no new comparison rule.

## Components touched

### `tests/methodology/test_triage_skill_drift.py` (new) + `test_adopt_skill_drift.py` (new)

- **Responsibility**: regression-pin that the in-repo canonical opener-skill prose stays forward-synced to the installed copy Claude actually reads at `/triage` / `/adopt` runtime. Closes the slice-048-discovered N=1 latent exposure (the two openers were the only mini-CAD-eligible skills with repo+installed copies but no drift guard; their forward-sync was manual-must-not-defer-only).
- **Lives at**: `tests/methodology/test_triage_skill_drift.py`, `tests/methodology/test_adopt_skill_drift.py` (both created by this slice).
- **Key interactions**: import `assert_md_forward_synced` (from `tests.skill_drift_equality`) + `REPO_ROOT` (from `tests.methodology.conftest`); read `skills/{triage,adopt}/SKILL.md` and `~/.claude/skills/{triage,adopt}/SKILL.md`. No production code touched. Zero blast radius on `src`/`tools`/`skills` runtime — these are leaf test modules importing a stable shared helper (no graphify reachability impact; pytest collects them via `python_files = test_*.py`).

## Contracts added or changed

None. No endpoints, events, schemas, or audit-tool CLIs introduced or modified. `assert_md_forward_synced`'s signature/behavior is reused verbatim.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1**. The two new modules are pytest-collected test modules — their "consumer" is the test runner itself; the convention for the 5 existing sibling skill-drift modules is no WIRE-1 row (a `test_*` module IS the consumer surface, not a library needing a separate consumer). Zero-row matrix = clean per the audit.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_triage_skill_drift.py` | — | — | `pytest-collected regression test module (mirrors the 5 existing skill-drift sibling modules, none of which carry a WIRE-1 row) — rationale: a test_* module is itself the consumer surface, not a library demanding a separate consumer+test` |
| `tests/methodology/test_adopt_skill_drift.py` | — | — | `pytest-collected regression test module (same rationale as the triage twin) — rationale: a test_* module is itself the consumer surface` |

## Decisions made (ADRs)

- [[decisions/ADR-051]] — extend the mini-CAD / EOL-DRIFT-1 drift-guard family to the two pipeline-opener skills (`/triage`, `/adopt`) by minting RULE-ID **OSDG-1** (Opener-Skill Drift Guard), classified as a methodology-surface **behavior change** — reversibility: **cheap** (a rule-ID + two test modules + a changelog entry; revertible by deleting them and the version bump).

**rev-1 (post-Critic B2): the original "no new ADR / no changelog / no VERSION bump" pre-decision is WITHDRAWN.** It rested on a false precedent (see the corrected analysis below) and is reversed to the honest path the design itself had named as the bounded remediation.

## Methodology-surface obligation — CORRECTED decision (rev-1, Critic B2 ACCEPTED-FIXED)

**Decision: slice-049 IS a methodology-surface behavior change. It ships a `## v0.57.0` changelog entry minting RULE-ID OSDG-1 + a 4-part PMI-1 atomic bump 0.56.0→0.57.0 + a `test_v_0_57_0_osdg_1_entry_present_in_repo` (+`_shippability_consumer_propagation`) entry-pin + [[decisions/ADR-051]]. INST-1 unchanged (no new skill/agent/tool — only two `tests/` modules + an ADR).**

**Why the rev-0 pre-decision was wrong (recompute-don't-trust, verified against the real artifacts — the exact MEPD-1(b) law this slice's own rev-0 violated):**

- rev-0 Rationale #2 claimed *"slice-035 added two new skill-drift byte-equality tests (build_slice+commit_slice) … with no independent rule-ID or version bump."* **False on both counts**, verified: the `mini-CAD-1 N=11 → N=13 stable with 2 NEW byte-equality tests` phrase lives at `methodology-changelog.md:474` — the **v0.35.0 BRANCH-1** entry's Validation line (co-located with `test_v_0_35_0_branch_1_entry_*`), not slice-035. `git log --oneline --diff-filter=A -- tests/methodology/test_build_slice_skill_drift.py` → commit `8823c53 … slice-021 — BRANCH-1`. So those drift tests were first added by **slice-021**, and they rode slice-021/BRANCH-1's **existing** 4-part PMI-1 v0.35.0 bump. That is the *opposite* of a "no-bump member-addition" precedent: the tests rode a bump the slice already had for an independent reason. It is therefore **no precedent** that a member-addition slice with *no other bump reason* may skip the bump. rev-0 Rationale #2's `slice-019/021 diagnose` sub-claim shares this defect (Critic m1) and is deleted.
- The decisive criterion is the changelog's own **Inclusion heuristic**: *"if a slice acceptable yesterday would be refused today, it's a changelog entry."* A forgotten forward-sync on `triage`/`adopt` SKILL.md was *acceptable yesterday* (no gate caught it — exactly the slice-048-discovered exposure). After this slice it is *refused today* (the new OSDG-1 gate FAILs the methodology suite + HALTs PCA-1). By the project's own published criterion that **is** a behavior change → changelog entry + RULE-ID + 4-part PMI-1 bump are mandatory.
- The META-1 mechanics still hold and now bind the *with-bump* path: `test_version_matches_most_recent_changelog_entry` ⇒ `VERSION` 0.57.0 must equal the new `## v0.57.0` header; `test_each_changelog_entry_carries_rule_reference` ⇒ the v0.57.0 block must carry a `Rule reference: OSDG-1` line. Both are satisfied by the corrected plan.

**RULE-ID rationale**: `OSDG-1` is a plain (non-`-D`, non-`-T`) ID — it is a pytest-regression-enforced invariant like its siblings CAD-1 / MCT-1 / QD-1, not a `/critique`-time prose-heuristic (those carry `-D`) nor a `/slice`-time heuristic (`-T`). It extends — does not supersede — the CAD-1 (slice-007) / mini-CAD (slice-010) / EOL-DRIFT-1 (slice-033, [[decisions/ADR-033]]) lineage; `ADR-051.supersedes: null`.

## Authorization model for this slice

N/A — test-only addition; no runtime authorization surface.

## Error model for this slice

No new error codes. The two tests surface failures exclusively through `assert_md_forward_synced`'s existing `AssertionError` messages (file-missing-in-repo / installed-missing-with-INSTALL-hint / genuine-EOL-normalized-divergence-with-both-paths-and-hashes). EOL-only differences and exact matches return cleanly (the R-5 false-FAIL class, suppressed by the shared comparator — ADR-033).

## Build-sequencing notes (carried to /build-slice)

1. **Pre-sync evidence preservation FIRST** (must-not-defer / Critic M2): BEFORE any copy, run an EOL-normalized diff of `skills/{triage,adopt}/SKILL.md` vs their installed copies; record verbatim in build-log (expected: identical). A pre-existing **non-EOL** divergence → STOP, record in slice vault + risk-register before reconciling (the latent bug actually occurred).
2. **Forward-sync** (must-not-defer, only after step 1): copy in-repo → installed for both openers (slice-035 "reconcile the installed copy before the gate that audits it" law). Record the sync in build-log Events.
3. **Genuine-contrast for BOTH** (must-not-defer / folded AC1+AC2): for each test — write it, confirm PASS on the synced tree; append one non-EOL byte to the *installed* copy, confirm that test FAILs with the drift message; restore, confirm PASS. Capture both transitions in build-log (BC-PROJ-5; triage AND adopt).
4. **Behavior-change artifacts** (Critic B2): mint OSDG-1 — add the `## v0.57.0` `methodology-changelog.md` entry (carrying `Rule reference: OSDG-1`), the 4-part PMI-1 atomic bump 0.56.0→0.57.0, `test_v_0_57_0_osdg_1_entry_present_in_repo` + `_shippability_consumer_propagation`, and ADR-051 (created at /design-slice). Run PMI-1/INST-1/META-1 audits.
5. **Exactly ONE catalog row LAST** (must-not-defer / meta-Critic B-add-1): author the single `| 49 | slice-049-add-triage-adopt-skill-drift-guards | OSDG-1 …` row covering both guards (NOT two rows — one-row-per-slice, slice-048 #48 precedent), pipe-free / `\|`-escaped Machine-cmd cells (BC-PROJ-7 / SCMD-1 6-col schema), then run the real `tools/shippability_runner.py` SRSC-1 runner and read its output (slice-044 law).
6. **CLAUDE.md edit + immediate pin re-run** (meta-Critic M-add-1 / slice-039): generalize the `## Self-hosting discipline` Mini-CAD bullet to name the opener skills (`triage`, `adopt`) under OSDG-1; keep "content-equal modulo line endings" + "EOL-DRIFT-1" + "ADR-033", introduce NO "MUST be byte-equal". **Immediately re-run `tests/methodology/test_root_claude_md_cad1_eol_agnostic.py`** — this edit lands in the exact section that prose-pin guards.
7. **Pre-finish BC-PROJ-4 real-artifact run**: full methodology suite + CAD-1/PMI-1/INST-1/TF-1/SCPD-1/SCMD-1/META-1 audits on the real tree, read output — green required.
