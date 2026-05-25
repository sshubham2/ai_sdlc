# Slice 067: add-parallel-slice-queue-output

**Mode**: Standard
**Estimated work**: 1 day (medium)
**Risk retired**: none directly; **unblocks** slice-068 (`add-slice-queue-claim-state-machine`) + slice-069 (`add-rebase-and-conflict-discipline`) — the 4-slice BRANCH-2 parallel-slice family (slice-066 / 067 / 068 / 069) reaches Slice A milestone
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Extend `/slice` Step 6 so that, immediately after writing `mission-brief.md` + `milestone.md`, it ALSO writes a persistent side-output `architecture/slice-queue.md` containing the **top-10 parallel-safe candidates** discovered during Step 1's source-fan-out (sources #1-8). Each queue entry tags the candidate's blast-radius file set (from graphify) and a `Parallel-safety` flag (`NON-OVERLAPPING` vs `OVERLAPS-WITH-slice-NNN`) computed against the union of blast-radius file sets for currently-active slices. The queue is a multi-session-visible artifact future Claude sessions can read to pick a parallel-safe next-slice without re-running discovery from scratch. Slice-067 ships the OUTPUT only — claim semantics (`Claimed-by/-at`, `/slice --claim`, force-claim escape) are slice-068's scope; rebase/conflict discipline is slice-069's scope. This slice is the structural raison d'être of the BRANCH-2 family: without the queue, the worktree mechanics from slice-066 are physically usable but discoverability-blind — a second session has no machine-readable list of safe candidates to pick from.

## Acceptance criteria

1. `/slice` Step 6.5 (NEW per PSQ-1; inserted between current Step 6 and `## Critical rules`) writes `architecture/slice-queue.md` (or overwrites existing) immediately after writing `mission-brief.md` + `milestone.md`, containing the top-10 parallel-safe candidates from Step 1's source-fan-out (sources #1-8 of the existing `/slice` skill — risk-register / deferrals / discoveries / concept-scope / aggregated-lessons / user-intent / diagnose-out-backlog).
2. Each queue entry is a `### <candidate-name>` block with mandatory fields: `**Source:**` (which of the 8 sources surfaced it), `**Blast-radius:**` (file set from graphify or `unknown` if graphify unavailable or candidate has no hint files), `**Parallel-safety:**` (`NON-OVERLAPPING` | `OVERLAPS-WITH-slice-NNN[, slice-MMM]` | `UNKNOWN-NO-HINT-FILES` | `UNKNOWN-NO-GRAPH` — 4-value enum), `**Effort:**` (SMALL/MEDIUM/LARGE per Step 2 scoring), `**Risk-retired:**` (HIGH/MEDIUM/LOW/NONE per Step 2 scoring).
3. Parallel-safety computation: for each candidate, derive its expected blast-radius file set (from graphify blast-radius query against the candidate's hint files, OR empty set if no hint files derivable, OR `unknown` set if graphify unavailable); flag conflicts against the union of expected blast-radius file sets for every currently-active slice (active slices read from `architecture/slices/_index.md` `## Active` table — for each, read its `design.md` if present to extract declared touched files, OR fall back to `mission-brief.md`'s `## Dependencies` cite). Classification precedence: `UNKNOWN-NO-GRAPH` (graph missing) > `UNKNOWN-NO-HINT-FILES` (candidate has empty hint_files set) > `OVERLAPS-WITH-slice-NNN` (non-empty intersection with one or more active slices) > `NON-OVERLAPPING` (non-empty hint_files, empty intersection).
4. Four edge cases handled deterministically: (a) zero candidates discovered → queue file written with `_(no candidates)_` placeholder body + provenance line; (b) zero active slices → candidates with non-empty `hint_files` flagged `NON-OVERLAPPING` (empty intersection); candidates with empty `hint_files` still flagged `UNKNOWN-NO-HINT-FILES` regardless of active-slice set (per AC3 precedence); (c) missing `graphify-out/graph.json` → queue file written with each entry's `**Blast-radius:** unknown` + `**Parallel-safety:** UNKNOWN-NO-GRAPH` + one top-of-file `_WARN: graphify graph missing — blast-radius enrichment skipped; rebuild with `$PY -m graphify code .`_` line; (d) candidate with empty `hint_files` set (no source-cited file paths derivable) → entry classified `UNKNOWN-NO-HINT-FILES` + `**Blast-radius:** unknown` (surfaces honestly that we don't know — symmetric to UNKNOWN-NO-GRAPH).
5. Queue write is **idempotent overwrite** (not append): every `/slice` invocation regenerates the file from scratch with a `_Generated: <ISO-8601 timestamp> by /slice during slice-NNN definition_` provenance line; consecutive runs produce equivalent content modulo timestamp.
6. PSQ-1 methodology-changelog entry `## v0.69.0` is structurally pinned per the canonical BC-PROJ-10 paired-pin schema (`test_v_0_69_0_psq_1_entry_present_in_repo` + `test_v_0_69_0_psq_1_shippability_consumer_propagation` — mirroring slice-066 v0.68.0 BRANCH-2 entry-pin pair at `tests/methodology/test_methodology_changelog.py:4433` + `:4513`) AND `architecture/shippability.md` row #67 cites PSQ-1's audit-rule + consumer propagation reference back to the changelog entry (RPCD-1 / SCPD-1 paired-pin).

> **AC-count deviation note** (per /critique-review M-add-1 ACCEPTED-FIXED): the /slice skill's ≤5-AC rule (SKILL.md L174/L208/L295) is deliberately ridden at 6 ACs for this slice. **Rationale**: new-mechanism slices that mint a methodology-changelog rule (PSQ-1 here) carry a BC-PROJ-10 paired-pin obligation that cannot be cleanly folded into AC1-AC5 (those cover runtime queue-write behavior; AC6 covers methodology-surface entry-pin). This is a per-slice documented deviation, NOT a rule revision. **Flagged for /critic-calibrate**: if AC6-shape recurs on slice-068+ new-mechanism mints, evaluate whether to relax SKILL.md's ≤5-AC rule to "≤5 ACs (or ≤6 when AC6 is exclusively a v-section entry-pin meta-AC)".

## Test-first plan

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/skills/slice/test_slice_queue_output.py | test_slice_step_6_writes_slice_queue_md | PASSING |
| 1 | unit | tests/skills/slice/test_slice_queue_output.py | test_slice_queue_top_10_cap | PASSING |
| 2 | unit | tests/skills/slice/test_slice_queue_output.py | test_each_entry_has_required_fields | PASSING |
| 3 | unit | tests/skills/slice/test_slice_queue_output.py | test_parallel_safety_flags_overlapping_active_slice | PASSING |
| 3 | unit | tests/skills/slice/test_slice_queue_output.py | test_parallel_safety_flags_non_overlapping | PASSING |
| 4 | unit | tests/skills/slice/test_slice_queue_output.py | test_zero_candidates_writes_placeholder | PASSING |
| 4 | unit | tests/skills/slice/test_slice_queue_output.py | test_zero_active_slices_non_overlapping_for_non_empty_hint_files | PASSING |
| 4 | unit | tests/skills/slice/test_slice_queue_output.py | test_missing_graph_emits_warn_and_unknown_flags | PASSING |
| 4 | unit | tests/skills/slice/test_slice_queue_output.py | test_empty_hint_files_overrides_zero_active_slices_to_unknown_no_hint_files | PASSING |
| 5 | unit | tests/skills/slice/test_slice_queue_output.py | test_idempotent_overwrite_with_provenance_line | PASSING |
| 5 | methodology | tests/methodology/test_slice_skill_drift.py | test_in_repo_and_installed_slice_skill_md_are_content_equal | PASSING |
| 6 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_69_0_psq_1_entry_present_in_repo | PASSING |
| 6 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_69_0_psq_1_shippability_consumer_propagation | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | `/slice` Step 6.5 writes `architecture/slice-queue.md` | After `/build-slice` ships, run `/slice` in this very repo (slice-068 candidate generation); assert `architecture/slice-queue.md` exists and contains ≤10 `### `-prefixed candidate entries. |
| 2 | Each entry has required fields with 4-value Parallel-safety enum | grep the generated `slice-queue.md`: every `### ` block contains `**Source:**`, `**Blast-radius:**`, `**Parallel-safety:**` (one of `NON-OVERLAPPING` \| `OVERLAPS-WITH-slice-NNN[, slice-MMM]` \| `UNKNOWN-NO-HINT-FILES` \| `UNKNOWN-NO-GRAPH`), `**Effort:**`, `**Risk-retired:**` field lines. |
| 3 | Parallel-safety computation correct with 4-way classification + precedence | Synthesize fixture repo with one active slice declaring blast-radius `{tools/A.py, tools/B.py}` + three candidates (overlapping `{tools/A.py, tools/C.py}`, non-overlapping `{tools/D.py, tools/E.py}`, empty hint-files `{}`); assert overlapping → `OVERLAPS-WITH-slice-NNN`, non-overlapping → `NON-OVERLAPPING`, empty-hint → `UNKNOWN-NO-HINT-FILES`. Precedence: graph-missing fixture should override all to `UNKNOWN-NO-GRAPH`. |
| 4 | Edge cases handled (4-way) | Four synthesized fixtures: (a) zero candidates → placeholder text; (b) zero active slices + non-empty hint-files → `NON-OVERLAPPING`; (c) graph.json absent → top-of-file WARN line + `UNKNOWN-NO-GRAPH` flags on all entries; (d) empty hint-files (regardless of active-slice set) → `UNKNOWN-NO-HINT-FILES` flag. |
| 5 | Idempotent overwrite with provenance | Run `/slice` twice in a row in same fixture; assert second run replaces file (not appends); assert provenance line timestamp updated; assert candidate-set content equal modulo timestamp. |
| 6 | PSQ-1 v0.69.0 methodology-changelog entry pinned per BC-PROJ-10 paired-pin | Run `pytest tests/methodology/test_methodology_changelog.py::test_v_0_69_0_psq_1_entry_present_in_repo tests/methodology/test_methodology_changelog.py::test_v_0_69_0_psq_1_shippability_consumer_propagation -v`; both PASS. Also `pytest tests/methodology/test_methodology_changelog.py::test_methodology_changelog_has_rule_reference_per_section -v` (META-1 `^## v` split) PASSes against the new `## v0.69.0` section. |

## Must-not-defer

- [ ] Atomic write of `slice-queue.md` (write to `.tmp` sibling then `os.replace()`-style rename — no half-written file visible to a concurrent session-2 reader)
- [ ] Path resolution works on Windows + POSIX (use `pathlib.Path`, not string concat; no hardcoded separators)
- [ ] Graphify graph-file presence check before query (no Python exception bubbled to user; missing-graph → AC4 sub-(c) WARN path)
- [ ] `skills/slice/SKILL.md` prose update drift-guarded by OSDG-1 (`tests/methodology/test_slice_skill_drift.py` — existing test enforces in-repo↔installed equality modulo EOL per ADR-033)
- [ ] Forward-sync to installed `~/.claude/skills/slice/SKILL.md` (manual MUST-NOT-DEFER in `/build-slice` Phase D; OSDG-1 catches if forgotten)
- [ ] Shippability catalog row added per RPCD-1 / SCPD-1 (new audit rule → consumer reference)
- [ ] BCR-1 round-trip discipline: this slice is NOT closing a `**Closes:** SC-NNN` sentinel — risk-register-driven (slice-066 nomination), not backlog-driven; reflection MUST explicitly note "NOT a BCR-1 round-trip"

## Out of scope

- **Slice B (claim state machine)** — `slice-queue.md` `Claimed-by/-at/Force-claim` schema, `/slice --claim`, `/slice --force-claim`, session-id detection — separate slice (`add-slice-queue-claim-state-machine`, slice-068 nominee), depends on this slice's queue file format being shipped.
- **Slice D (rebase + conflict discipline)** — `/commit-slice` rebases default before merge + structured-options ASK on conflict — separate slice (`add-rebase-and-conflict-discipline`, slice-069 nominee), depends on slice-066 worktree mechanics + this slice's parallel-safety classification.
- **Auto-claim of top candidate** — slice-067 surfaces the queue; humans/Claude sessions read it manually. Auto-claim machinery is slice-068.
- **Live-update / watch mode** — queue is regenerated only on `/slice` invocation. No file-watcher or daemon.
- **Filtering by user-supplied criteria** — `/slice --filter=<tag>` or similar is out of scope; the queue ships unfiltered top-10.
- **Cross-repo / monorepo parallel queues** — single-repo scope only.
- **Pruning superseded entries** — every `/slice` invocation regenerates from scratch; no stale-entry pruning logic needed (idempotent overwrite handles it).

## Dependencies

- Prior slices: [[slice-066-add-worktree-per-slice-discipline]] — worktree filesystem isolation (BRANCH-2 / ADR-063) is the physical-isolation prerequisite that makes multi-session parallel-slice work safe; this slice ships the discoverability layer on top.
- Vault refs: [[skills/slice/SKILL.md]] (the surface this slice extends), [[architecture/decisions/ADR-063]] (BRANCH-2 worktree-per-slice), [[architecture/decisions/ADR-019]] (BRANCH-1 branch-per-slice — preserved as historical anchor per ADR-063 §Scope of supersession 4th-surface inheritance).
- Risk register: no direct R-NN retirement; this slice opens the door to discoverability-class risks (e.g., stale queue file misleading a session) that will be tracked in `/design-slice` as candidate R-NN entries if /critique flags them.
- Diagnose backlog: NOT a BCR-1 round-trip (zero `**Closes:** SC-NNN` sentinels — risk-register-driven, not backlog-driven).
- Graphify dependency: requires `graphify-out/graph.json` for blast-radius enrichment (AC3); AC4 sub-(c) handles missing-graph case gracefully.

## Mid-slice smoke gate

At ~50% of build (after the queue-write helper + skill prose update are in, before the drift-guard test run), execute in the slice's worktree:

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -c "from tools.slice_queue_writer import write_slice_queue; write_slice_queue(repo_root='.', active_slice_num=67)"
ls architecture/slice-queue.md
```

(Helper name/signature tentative; `/design-slice` locks the API.) Expected: `architecture/slice-queue.md` exists; contains `_Generated: <timestamp>` provenance line; contains ≥1 `### ` candidate block with `**Source:**` + `**Blast-radius:**` + `**Parallel-safety:**` fields. If fails: STOP, diagnose the helper or graphify wiring, don't continue to drift-guard work.

## Pre-finish gate

- [ ] All 6 acceptance criteria PASS with evidence in `validation.md` (AC1-AC5 runtime queue behavior + AC6 v0.69.0 entry-pin meta-AC; AC-count deviation rationale documented after AC6)
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (queue file generates cleanly in slice's own worktree)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] OSDG-1 drift-guard (`tests/methodology/test_slice_skill_drift.py`) PASSES — in-repo `skills/slice/SKILL.md` content-equal modulo EOL to installed `~/.claude/skills/slice/SKILL.md`
- [ ] PMI-1 atomic bump (likely 0.68.0 → 0.69.0) covers all version-bearing legs per slice-059 TVFS-1 + slice-063 NAW-1 5-part bump precedent (VERSION + plugin.yaml.version + pyproject.toml [project].version + `## v0.69.0` header + installed `~/.claude/ai-sdlc-VERSION`) — locked in `/design-slice` based on MEPD-1 Inclusion-heuristic posture
- [ ] BRANCH-2 audit (`tools/branch_workflow_audit.py`) clean: slice ran in canonical worktree `<main-parent>/<main-name>-wt/slice-067-add-parallel-slice-queue-output` on `slice/067-add-parallel-slice-queue-output` branch
- [ ] Shippability catalog row #67 added (if MEPD-1 posture warrants — likely yes given new user-facing behavior on `/slice`)
- [ ] Full pytest suite passes (baseline 899/899 from slice-065; slice-066's `/reflect` likely advanced this — verify at /validate-slice time)

## Pipeline position

- **predecessor**: `/reflect` (slice-066's `/reflect` was the loop entry into this slice)
- **successor**: `/design-slice`
- **auto-advance**: true
- **on-clean-completion**: once mission-brief.md + milestone.md are written AND the user-supplied intent (`add-parallel-slice-queue-output`) is settled, invoke `/design-slice` via the Skill tool without waiting for the user. **Bootstrap-discharge note**: slice-067's own `/slice` invocation did NOT write `architecture/slice-queue.md` — the helper `tools/slice_queue_writer.py` does not exist yet at /slice time (the slice that authors the helper cannot self-apply its own deliverable). Bootstrap-reference instance #1 for PSQ-1, mirroring slice-066's `WORKTREE=skip-bootstrap` precedent. The queue file is first written at /build-slice Phase F mid-slice smoke (dogfood seed); slice-068+'s `/slice` invocations regenerate it routinely.
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - Candidate-ordering decision (Step 3 / Step 3b) — ALREADY RESOLVED via `AskUserQuestion` structured-options at this `/slice` invocation: user picked "Parallel-slice-queue first (your invoked pick)" over the slice-064→065 bundle-first precedent. Gate consumed; auto-advance proceeds.
  - BFRD-1 bug-fix confirm gate — NOT APPLICABLE (this slice is `add-*` additive feature work, not `fix-*`/`bugfix-*`/etc.; candidate source is slice-066 nomination, not bug-class).

> Per PCA-1 (`methodology-changelog.md` v0.41.0). The `## Next step` section below is the human-readable companion; the block above is the machine-actionable auto-advance directive read at skill-completion.

## Next step

`/design-slice` — turn this mission brief into a just-enough spec covering: the queue-writer helper API + module location (`tools/slice_queue_writer.py` candidate), the graphify blast-radius query shape, the active-slice blast-radius derivation (read `_index.md` `## Active` table → read each active slice's `design.md` `## Components touched` section, fallback to `mission-brief.md` `## Dependencies` cite), MEPD-1 Inclusion-heuristic posture decision (new RULE-ID `PSQ-1` or in-family-extension), 5-part PMI-1 bump scope, OSDG-1 drift-guard touchpoint enumeration, and the cross-slice contract with slice-068 (claim-machinery hooks).
