# Design: Slice 067 add-parallel-slice-queue-output

**Date**: 2026-05-25
**Mode**: Standard

## What's new

- **New methodology rule PSQ-1 (Parallel-Slice Queue)** — `/slice` Step 6.5 (NEW) writes a persistent side-output `architecture/slice-queue.md` containing the top-10 parallel-safe candidates from Step 1's source-fan-out (sources #1-8), each tagged with graphify-derived blast-radius + parallel-safety classification against currently-active slices. First rule in a 3-rule family for the BRANCH-2 parallel-slice work (PSQ-1 / future PSQ-2 claim-machinery / future PSQ-3 rebase-discipline; PSQ-2/3 are slice-068/069 nominees, NOT this slice's scope).
- **New helper module** `tools/slice_queue_writer.py` with CLI + library API:
  - `write_slice_queue(repo_root, candidates, active_slice_num, graph_path=None, now=None) -> Path` — top-level entrypoint.
  - `derive_active_slice_blast_radius(repo_root) -> dict[int, set[str]]` — reads `architecture/slices/_index.md` `## Active` table; for each active slice number, reads its `design.md` `## Wiring matrix` `New module` cells (preferred) OR its `mission-brief.md` `## Dependencies` cite (fallback) to derive declared touched-file set; calls graphify blast-radius on each declared file; unions per active slice.
  - `compute_parallel_safety(candidate_files: set[str], active_blasts: dict[int, set[str]]) -> tuple[str, list[int]]` — returns `("NON-OVERLAPPING", [])` if intersection is empty across all active blasts (and candidate_files is non-empty); `("OVERLAPS-WITH-slice-NNN[, slice-MMM]", [NNN, ...])` if non-empty intersection with one or more active slices; `("UNKNOWN-NO-HINT-FILES", [])` if `candidate_files` is empty; classification gets overridden to `UNKNOWN-NO-GRAPH` by the caller if graphify graph is missing entirely.
  - `format_queue_md(items, provenance_ts, warn_no_graph) -> str` — pure formatter.
  - `_call_graphify_blast_radius(graph_path, file_or_node) -> set[str]` — thin wrapper adapting `skills/slice-candidates/build_backlog.py:graphify_blast_radius` pattern (subprocess call with `--json` first, text-parse fallback); injection seam per slice-059 TVFS-1 / slice-063 NAW-1 precedent for deterministic regression testing.
  - CLI: `python -m tools.slice_queue_writer --candidates-json <path> --active-slice <N> --output <path> [--graph <path>]` — reads JSON candidate list from `--candidates-json`, computes parallel-safety, writes formatted markdown to `--output`. Tri-state exit: 0 clean / 2 usage / NEVER exit 1 (queue-write success is not a slice-regression class).
- **New `/slice` prose Step 6.5** at `skills/slice/SKILL.md` inserted at the precise position **after the mission-brief template's closing code-fence at SKILL.md:378-379 (the ``` ``` ``` line that closes the markdown code-fence opened at SKILL.md:276) and BEFORE the `## Critical rules` header at SKILL.md:380**. The 165-line span "between Step 6 (L214) and `## Critical rules` (L380)" contains the mission-brief template literal (L276-378) — Step 6.5 MUST NOT be inserted inside that fenced block (would corrupt the template literal AND trip OSDG-1 content-equality guard on the template's structure). The skill prose invokes the helper to write `architecture/slice-queue.md`. The `## Pipeline position` block in `skills/slice/SKILL.md` (separate from Step 6.5) is extended to note the queue-write side-effect on the existing `on-clean-completion` clause: "Step 6.5 fires here; queue-write failure is non-fatal — wrapped in try/except per ADR-064 Consequences §".
- **New TF-1 test file** `tests/skills/slice/test_slice_queue_output.py` — 9 unit tests per mission-brief TF-1 plan.
- **New ADR** `architecture/decisions/ADR-064-mint-psq-1-parallel-slice-queue.md` — mints PSQ-1; reversibility: cheap.
- **New methodology-changelog entry** `## v0.69.0 — 2026-05-25` minting PSQ-1.
- **New shippability row** `#67` PSQ-1 audit-rule + consumer-propagation pin per RPCD-1 / SCPD-1; row #67 references both BC-PROJ-10 paired-pin test functions (`test_v_0_69_0_psq_1_entry_present_in_repo` + `test_v_0_69_0_psq_1_shippability_consumer_propagation`) by canonical name.
- **New runtime artifact** `architecture/slice-queue.md` — written first at this slice's /build-slice Phase F mid-slice smoke (bootstrap-discharge instance #1 per slice-066 WORKTREE=skip-bootstrap precedent — the helper `tools/slice_queue_writer.py` does not exist at /slice time so the slice's own /slice cannot self-apply); slice-068+'s `/slice` invocations regenerate it routinely.
- **New methodology v0.69.0 PMI-1 5-part atomic bump** (0.68.0 → 0.69.0) covering all version-bearing legs per slice-059 TVFS-1 + slice-063 NAW-1 precedent.

## What's reused

- [[skills/slice/SKILL.md]] — the surface this slice extends; current Step 6 stays unchanged; new Step 6.5 inserts.
- [[skills/slice-candidates/build_backlog.py]] `graphify_blast_radius()` at `build_backlog.py:120-155` — the existing pattern for subprocess-invoking graphify blast-radius with `--json`-then-text-fallback; `tools/slice_queue_writer.py` adapts it verbatim into a thin wrapper (no module dependency — slice-candidates is a `skills/` artifact, not importable from `tools/`).
- [[tests/skill_drift_equality.py]] `assert_md_forward_synced` — reused by `tests/methodology/test_slice_skill_drift.py` (OSDG-1) to guard `skills/slice/SKILL.md` content-equality (already in place; this slice adds prose so the existing test transitively guards the new anchors).
- [[ADR-019]] (BRANCH-1, partial-superseded by ADR-020 + ADR-063) — historical anchor for the branch-per-slice lineage.
- [[ADR-063]] (BRANCH-2 worktree-per-slice) — the prerequisite this slice depends on; BRANCH-2 makes parallel-slice work physically possible, PSQ-1 makes it discoverable.
- [[ADR-033]] (EOL-DRIFT-1) — content-equality is EOL-agnostic for all forward-sync checks; the new prose anchors are guarded modulo line endings.
- [[ADR-051]] (OSDG-1 generalization that decoupled the "Opener-Skill" historical label from scope) — the existing OSDG-1 guard on `skills/slice/SKILL.md` covers the Step-6.5 prose addition without any new test wiring needed.
- [[ADR-059]] (CRSI-1 walking-skeleton v1) — `/code-review` will fire on this slice's code diff; advisory only per v1.
- [[ADR-061]] (NAW-1 + union-of-three-sources read mechanism) — this slice ships zero new `agents/*.md`, so NAW-1 fires zero-warn at `/build-slice` Step 6.
- `tools/risk_register_audit.py` — already-shipped Source #1 helper; `/slice` Step 1 already calls it; Step 6.5 inherits the resulting candidate list.
- `tools/test_first_audit.py --strict-pre-finish` — pins the 9-row TF-1 plan at `/build-slice` Step 6.
- `tools/branch_workflow_audit.py` — BRANCH-2 11-violation-kind enforcement at `/build-slice` Step 6; this slice runs in `<HOME>\ai_sdlc-wt\slice-067-add-parallel-slice-queue-output` on `slice/067-add-parallel-slice-queue-output`.
- `tools/install_audit.py` `_CANONICAL_TOOLS` — extend with `slice_queue_writer.py` (INST-1 propagation; slice-050 BC-PROJ-9 5-inventory fan-out).
- `tests/methodology/test_utf8_stdout_regression.py` `_ROOT_ONLY_TOOLS` — extend with `slice_queue_writer.py` (BC-PROJ-9).
- `INSTALL.md` "N executable methodology tools" count literals (×2 sites L22 + L166 per slice-066 evidence) — bump from 28 → 29.
- `plugin.yaml` `tools:` enumeration — append `tools/slice_queue_writer.py`; bump `version:` 0.68.0 → 0.69.0.

## Components touched

### `tools/slice_queue_writer.py` (NEW)

- **Responsibility**: write the parallel-slice queue file. Pure helper — invoked by `/slice` Step 6.5 prose; no user-facing CLI flags beyond the documented surface; never blocks `/slice` (best-effort write; missing graph → WARN-and-degrade per AC4-(c); zero candidates → placeholder per AC4-(a)).
- **Lives at**: `tools/slice_queue_writer.py` (created by this slice; ~150-200 LOC).
- **Key interactions**: subprocess-calls `graphify blast-radius` (existing CLI at `~/.claude/.venv/Scripts/python.exe -m graphify`); reads `architecture/slices/_index.md` (active-slice extraction); reads each active slice's `design.md` + `mission-brief.md` (touched-file derivation); writes `architecture/slice-queue.md` atomically (`.tmp` + `os.replace()`).

### `skills/slice/SKILL.md` (MODIFIED — adds Step 6.5)

- **Responsibility**: `/slice` runtime contract. Step 6.5 ADDED inserts between current Step 6 (mission brief + milestone) and `## Critical rules`; invokes the helper.
- **Lives at**: `skills/slice/SKILL.md` (modified; +~25 lines for Step 6.5 prose + a `## Pipeline position` rev-N update to note the queue-write side-effect).
- **Key interactions**: read by Claude Code skill runtime at every `/slice` invocation; mirrored to `~/.claude/skills/slice/SKILL.md` via forward-sync (OSDG-1).

### `tests/skills/slice/test_slice_queue_output.py` (NEW)

- **Responsibility**: 9 unit tests per mission-brief TF-1 plan, pinning the queue-writer's behavior axes (file write, top-10 cap, required fields, parallel-safety, edge cases, idempotent overwrite).
- **Lives at**: `tests/skills/slice/test_slice_queue_output.py` (created by this slice; ~250-300 LOC test code with fixtures).
- **Key interactions**: imports `tools.slice_queue_writer` directly (library API); uses `tmp_path` pytest fixture for isolated repo-shape fixtures; mocks/stubs the graphify blast-radius subprocess via the `_call_graphify_blast_radius` injection seam.

### `architecture/decisions/ADR-064-mint-psq-1-parallel-slice-queue.md` (NEW)

- **Responsibility**: records the PSQ-1 minting decision + Options-considered + Reversibility tag (cheap).
- **Lives at**: `architecture/decisions/ADR-064-mint-psq-1-parallel-slice-queue.md`.
- **Key interactions**: cross-referenced from `methodology-changelog.md` v0.69.0 entry; cited in `architecture/shippability.md` row #67.

## Contracts added or changed

### `/slice` Step 6.5 — write parallel-slice queue (NEW behavior contract)

- **Contract**: every `/slice` invocation, immediately after writing `mission-brief.md` + `milestone.md` (current Step 6), writes/overwrites `architecture/slice-queue.md` containing the top-10 parallel-safe candidates from Step 1's source-fan-out. Idempotent overwrite (not append). Best-effort: graphify graph missing → degraded queue (AC4-(c)); zero candidates → placeholder (AC4-(a)); zero active slices → all candidates flagged `NON-OVERLAPPING` (AC4-(b)).
- **Defined in code at**: `tools/slice_queue_writer.py:write_slice_queue()` (library entry-point) + `tools/slice_queue_writer.py:main()` (CLI entry-point per `python -m tools.slice_queue_writer`).
- **Auth model**: not applicable — methodology-internal helper; no external surface; no auth.
- **Error cases**:
  - Missing graphify graph → `WARN` line at top of output file + per-entry `UNKNOWN-NO-GRAPH` flag (AC4-(c)); helper returns 0 (not an error class).
  - Candidate with empty `hint_files` set → entry classified `UNKNOWN-NO-HINT-FILES` (design refinement of AC2 — symmetric to UNKNOWN-NO-GRAPH; surface honestly that we don't know).
  - Zero candidates → output file with `_(no candidates)_` placeholder body (AC4-(a)); helper returns 0.
  - Active-slice `_index.md` `## Active` table absent or empty → `derive_active_slice_blast_radius()` returns `{}`; downstream `compute_parallel_safety()` flags candidates with **non-empty hint_files** as `NON-OVERLAPPING` (empty intersection) (AC4-(b)) — but candidates with **empty hint_files** still flag `UNKNOWN-NO-HINT-FILES` per precedence (AC3 + AC4-(d)). Classification precedence (highest priority first): `UNKNOWN-NO-GRAPH` (graph missing — caller-side override) > `UNKNOWN-NO-HINT-FILES` (candidate `hint_files` is empty) > `OVERLAPS-WITH-slice-NNN` (non-empty intersection with one or more active slices) > `NON-OVERLAPPING` (non-empty `hint_files`, empty intersection). The precedence is implemented as early-return guards in `compute_parallel_safety()` in graph→hint→overlap→non-overlap order.
  - JSON parse error on `--candidates-json` input → STDERR error + exit 2 (usage).
  - Disk-write failure on `architecture/slice-queue.md` → propagate exception; queue-write failure does NOT block `/slice` (Step 6.5 is wrapped in try/except in the skill prose so `/slice` completes the mission-brief + milestone deliverables regardless).

### `architecture/slice-queue.md` (NEW persistent artifact)

- **File**: `architecture/slice-queue.md` at repo root (under `architecture/`).
- **Format** (defined in `tools/slice_queue_writer.py:format_queue_md()`):

```markdown
# Slice queue

_Generated: 2026-05-25T15:30:00+00:00 by /slice during slice-NNN definition_

_WARN: graphify graph missing — blast-radius enrichment skipped; rebuild with `$PY -m graphify code .`_  (← present only when graph absent)

## Candidates

### add-some-candidate-name

- **Source:** risk-register R-13
- **Blast-radius:** `tools/slice_candidates_audit.py`, `tests/methodology/test_slice_candidates.py`
- **Parallel-safety:** NON-OVERLAPPING
- **Effort:** SMALL
- **Risk-retired:** LOW

### add-another-candidate

- **Source:** diagnose-out backlog SC-006
- **Blast-radius:** `unknown`  (← when candidate has empty hint_files set)
- **Parallel-safety:** UNKNOWN-NO-HINT-FILES
- **Effort:** MEDIUM
- **Risk-retired:** MEDIUM
```

- **Consumer**: human readers (multi-session discoverability); slice-068 `/slice --claim` machinery (future slice; PSQ-2).
- **Atomicity**: written via `.tmp` sibling + `os.replace()`; no half-written state visible to a concurrent reader (must-not-defer #1). **Crash-durability via `os.fsync()` is explicitly OUT OF SCOPE** — `os.replace()` provides atomicity vs concurrent reader (the load-bearing property), and the queue file is regenerable on every `/slice` invocation, so a post-crash zero-byte queue is not load-bearing (worst case: next `/slice` invocation refreshes it).

## Data model deltas

None. This slice ships no new persistent data model; the queue file is a derived markdown artifact regenerated on every `/slice` invocation.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/slice_queue_writer.py` | `skills/slice/SKILL.md` Step 6.5 (prose-as-executable-contract per CLAUDE.md) + `python -m tools.slice_queue_writer` CLI | `tests/skills/slice/test_slice_queue_output.py::test_slice_step_6_writes_slice_queue_md` (+ 9 sibling tests pinning library API + edge cases per the slice's TF-1 plan) | — |
| `tests/skills/slice/test_slice_queue_output.py` | `pytest` collection via `tests/` discovery | n/a (test module is itself the consumer test) | exempt — rationale: test modules are themselves the consumer-test surface for the modules they pin; demanding a recursive consumer-test would loop infinitely (no test module has its own dedicated consumer test in this codebase per slice-008/slice-051 precedent) |
| `architecture/decisions/ADR-064-mint-psq-1-parallel-slice-queue.md` | `methodology-changelog.md` v0.69.0 entry `Rule reference` line + `architecture/shippability.md` row #67 description cell | `tests/methodology/test_methodology_changelog.py::test_v_0_69_0_psq_1_entry_present_in_repo` + `::test_v_0_69_0_psq_1_shippability_consumer_propagation` (BC-PROJ-10 paired-pin schema per slice-066 v0.68.0 BRANCH-2 entry-pin precedent at `:4433` + `:4513`; META-1 `^## v` split at `:136` separately enforces the `Rule reference` line per section) | — |
| `architecture/slice-queue.md` (runtime-generated artifact) | future `/slice --claim` machinery (slice-068 PSQ-2) + human multi-session readers | `tests/skills/slice/test_slice_queue_output.py::test_idempotent_overwrite_with_provenance_line` (this slice's TF-1 plan) | exempt — rationale: runtime-generated derived artifact (NOT a tracked source module); consumer-entry-point cell already names the future-slice + human consumer; the format-pin test in column 3 IS the structural consumer-test for this artifact's shape contract |

## Decisions made (ADRs)

- [[ADR-064]] — Mint PSQ-1 (Parallel-Slice Queue) as the first rule in the BRANCH-2 parallel-slice family; `/slice` Step 6.5 writes `architecture/slice-queue.md` with top-10 candidates + graphify blast-radius non-overlap classification — reversibility: **cheap** (queue file is derived/regenerable; dropping PSQ-1 = stop writing the file + remove Step 6.5 prose; no schema migration, no consumer breakage beyond slice-068 which isn't shipped yet).

## Authorization model for this slice

Not applicable — methodology-internal helper; no external user-facing surface; no auth boundaries crossed.

## Error model for this slice

Per the Contracts §Error cases above. Summary: queue-write is best-effort; degraded states (missing graph, missing hint files, zero candidates, zero active slices) produce explicit-flag classifications instead of failures; CLI exits non-zero only on usage errors (exit 2). The Step 6.5 prose wraps the helper invocation in try/except so `/slice` always completes the mission-brief + milestone deliverables even if queue-write fails for an unforeseen reason (defensive — empirical absence of failure-class evidence yet, but Step-6.5 is a side-output, not a load-bearing deliverable).

## Genuine-contrast proof method

Per the slice-051/053/056 discipline for prose-pin and audit-presence tests, the test suite's mid-slice smoke gate must demonstrate FAIL-without-fix → PASS-with-fix for each AC. The mechanical contrasts:

- **AC1 (file write)**: pre-implementation, `architecture/slice-queue.md` does not exist in the test fixture; running `write_slice_queue()` creates it. Genuine: delete the helper's write logic → AssertionError on `Path.exists()`.
- **AC2 (required fields)**: per-entry assertion that all 5 fields (`Source`, `Blast-radius`, `Parallel-safety`, `Effort`, `Risk-retired`) appear; remove any one from the formatter → field-presence assertion fails.
- **AC3 (parallel-safety)**: fixture with one active slice (declared blast `{X, Y}`) + 3 candidates (overlapping `{X, Z}`, non-overlapping `{A, B}`, empty hint-files `{}`) → assertions on each candidate's classification. Remove the intersection check → all flagged NON-OVERLAPPING (test for overlapping case fails).
- **AC4 (edge cases)**: three independent fixtures × three sub-cases. Each FAIL-without-fix is the absence of the dedicated branch in `format_queue_md()` / `compute_parallel_safety()`.
- **AC5 (idempotent overwrite + provenance)**: run helper twice; assert second run replaces (not appends) AND provenance line timestamp updated. Remove `os.replace()` overwrite semantics → second run double-writes; remove `now=now or datetime.now(tz=timezone.utc)` injection seam → tests can't assert on stable timestamp.

## MEPD-1 Inclusion-heuristic posture

This slice **mints a new RULE-ID (PSQ-1)** + adds a NEW user-facing behavior contract on `/slice` + ships a new `tools/*.py` module + introduces a new persistent artifact (`architecture/slice-queue.md`) with a pinned format. Per the slice-049/050/051/057/058/059/060/063 precedent for new-mechanism slices, this **MUST**:

1. Add a methodology-changelog entry `## v0.69.0 — 2026-05-25` minting PSQ-1 (META-1 enforcing assertion at `tests/methodology/test_methodology_changelog.py:136` — the `^## v` split semantic — pins this).
2. Mint a new ADR-064 (this slice's design decision).
3. Execute a 5-part PMI-1 atomic version bump 0.68.0 → 0.69.0:
   - `VERSION` file
   - `plugin.yaml` `version:` field
   - `pyproject.toml` `[project].version` (PVFS-1)
   - `methodology-changelog.md` `## v0.69.0` header (MEPD-1 / META-1)
   - Installed `~/.claude/ai-sdlc-VERSION` (AVFS-1 + bootstrap)
4. MCFS-1 forward-sync `methodology-changelog.md` → `~/.claude/methodology-changelog.md`.
5. AVFS-1 forward-sync `VERSION` → `~/.claude/ai-sdlc-VERSION`.
6. TVFS-1 re-install of `ai-sdlc-tools` pip distribution via `pip install --upgrade .` (bootstrap discharge so the new `tools/slice_queue_writer.py` shows in the installed venv).
7. PMI-1 plugin manifest enumeration: append `tools/slice_queue_writer.py` to `plugin.yaml` `tools:` list.
8. INST-1 canonical-list propagation: append `slice_queue_writer.py` to `tools/install_audit.py:_CANONICAL_TOOLS`.
9. BC-PROJ-9 5-inventory fan-out for new `tools/*.py`:
   - `plugin.yaml` `tools:` (covered by #7)
   - `tools/install_audit.py:_CANONICAL_TOOLS` (covered by #8)
   - `tests/methodology/test_utf8_stdout_regression.py:_ROOT_ONLY_TOOLS`
   - `INSTALL.md` L22 tool-count literal `28 → 29`
   - `INSTALL.md` L166 tool-count literal `28 → 29`
10. Shippability catalog row #67 added per RPCD-1 / SCPD-1 (new audit-class → consumer reference); cite `architecture/shippability.md` row #67 in PSQ-1's methodology-changelog entry per slice-046 BC-PROJ-10 / Inclusion-heuristic paired-pin discipline.

This is **NOT a voluntary-restraint slice** (the voluntary-restraint discipline applies to retirement-discharge / part-(b) closure / in-family-extension slices per slice-037/046/050/052/055/056/057/061/065/066 N=9 cumulative pattern; this slice mints a new rule + new mechanism, so the full bump is mandatory per slice-049/050/051/057/058/059/060/063 N=8 cumulative new-mechanism pattern).

## Cross-slice contract with slice-068 (PSQ-2 claim machinery)

Slice-068 (`add-slice-queue-claim-state-machine`) builds on this slice's queue file with `Claimed-by/-at/Force-claim` schema + `/slice --claim` + `/slice --force-claim` + session-id detection. PSQ-1 (this slice) commits to a stable on-disk format whose `### <name>` block + field-line structure slice-068 can extend additively (e.g., adding new field lines `**Claimed-by:**` / `**Claimed-at:**` to each entry without breaking the existing 5-field contract). The cross-slice contract is:

- Slice-068 MAY add new field lines per entry (PSQ-1 field set is a minimum, not a maximum).
- Slice-068 MUST NOT modify or remove the 5 fields PSQ-1 ships (Source / Blast-radius / Parallel-safety / Effort / Risk-retired).
- Slice-068 MAY add new top-of-file sections (e.g., `## Claim activity log`) without breaking the PSQ-1 `## Candidates` section contract.

This is recorded as a contract pin in ADR-064's Consequences section.

## Risk register additions

- **R-19 (new, open, low-band — COMMITTED TO RISK-REGISTER AT /BUILD-SLICE PHASE A per /critique m3 ACCEPTED-FIXED)**: stale queue file misleads a session — if `architecture/slice-queue.md` was generated by a prior `/slice` invocation when the active-slice set was different, a future session reading it may pick a candidate that has since become OVERLAPS-WITH-newly-active-slice. Mitigation: every `/slice` invocation regenerates the queue (idempotent overwrite per AC5), so freshness window is "since last `/slice` invocation". Discoverability mitigation: provenance line `_Generated: <timestamp>_` lets a reader assess staleness manually. Likelihood: medium (multi-session workflows are explicitly the motivating use case); impact: low (worst case is one wasted candidate-pick; reader can re-run `/slice` to refresh). Score: 2 → low band. Slice-068's claim-machinery will narrow this further (the `Claimed-by` field will identify in-progress work without depending on queue freshness). Status: `mitigating` (provenance line + idempotent overwrite are the existing mitigation; slice-068 PSQ-2 claim-machinery is the planned structural close).

## What's deferred (NOT this slice)

- **Claim semantics** (`Claimed-by/-at/Force-claim` schema, `/slice --claim`, `/slice --force-claim`, session-id detection) → slice-068 (PSQ-2).
- **Rebase + conflict discipline in `/commit-slice --merge`** (rebases default before merge + structured-options ASK on conflict) → slice-069 (PSQ-3).
- **Auto-claim of top candidate** → slice-068+ scope.
- **Live-update / watch mode** → out of scope indefinitely (regenerate on `/slice` invocation is sufficient).
- **Filtering by user-supplied criteria** (`/slice --filter=<tag>`) → out of scope indefinitely.
- **Cross-repo / monorepo parallel queues** → out of scope indefinitely.
- **Slice-066 code-Critic bundled cleanup** (6 advisories: M1/M2/m1-m4) — deferred to slice-068+ bundled cleanup per user-explicit-pick ordering at slice-067 /slice invocation (the user picked "Parallel-slice-queue first" over the slice-064→065 bundle-first precedent).

## Validation strategy

- **/critique**: dual-Critic stack expected to focus on (a) the helper's API surface + injection seam design, (b) the queue file format's contract stability for slice-068, (c) the BC-PROJ-9 5-inventory fan-out completeness, (d) the MEPD-1 Inclusion-heuristic posture justification, (e) any falsifier classes in the `compute_parallel_safety()` logic (empty-intersection-vs-unknown-classification edge), (f) BRANCH-2 worktree placement validation.
- **/critique-review**: meta-Critic re-applies the 8 dimensions independently; expected catches include cross-document enumeration drift (any 5-part PMI-1 leg miscounted) + APED-1 empirical re-execution of `tools/branch_workflow_audit.py` on the slice's worktree state.
- **/build-slice**: BRANCH-2 worktree creation at `<HOME>\ai_sdlc-wt\slice-067-add-parallel-slice-queue-output` on `slice/067-add-parallel-slice-queue-output`; mid-slice smoke = AC1 helper produces a valid queue file; pre-finish = all 14+ audits pass including BC-PROJ-9 INSTALL.md count literals.
- **/code-review**: per CRSI-1 v1 walking-skeleton, advisory only; expected coverage: line-level concerns in `tools/slice_queue_writer.py` (POSIX-portability, Windows path edge cases, third-pass cross-cell drift not caught by design-Critic stack).
- **/validate-slice**: 5/5 ACs PASS evidenced via the TF-1 test suite + smoke evidence; full pytest baseline ≥899/899 + 9 new tests = 908+/908+.
- **/reflect**: capture validated/corrected/discovered/deferred per slice-067's actual experience; explicitly note "NOT a BCR-1 round-trip" (zero `**Closes:** SC-NNN` sentinels) per BCR-1 sentinel-trigger discipline; nominate slice-068 (PSQ-2 claim machinery) as the explicit next-up.

## Step 6.5 SKILL.md prose — ImportError guard contract (per /critique M2 ACCEPTED-FIXED)

The Step 6.5 prose in `skills/slice/SKILL.md` (insertion point pinned at SKILL.md:378-379 per /critique M3 ACCEPTED-FIXED) wraps the helper invocation in a `try/except ImportError` block so that any `/slice` run before `tools/slice_queue_writer.py` is installed silently no-ops (defensive for the slice-067 bootstrap window + any future PSQ-1-revert scenario). Canonical shape:

```bash
# Step 6.5: Write parallel-slice queue (PSQ-1)
$PY -c "
try:
    from tools.slice_queue_writer import write_slice_queue
    write_slice_queue(
        repo_root='.',
        candidates=<JSON-list-from-Step-3>,
        active_slice_num=<NNN>,
    )
except ImportError:
    pass  # Helper not installed yet (slice-067 bootstrap window or post-PSQ-1-revert); skip queue write
except Exception as e:
    print(f'WARN: queue write failed — {e}', file=sys.stderr)  # Non-fatal: /slice's primary deliverable (mission-brief + milestone) ships regardless
"
```

The ImportError branch is the **slice-067 bootstrap-discharge** mechanism (mirrors slice-066's `WORKTREE=skip-bootstrap` precedent — one idempotent guard covers the bootstrap window + any future skip-line scenario without needing N parallel skip-lines per skill).

## Open questions deferred to /build-slice plan-mode

- **`compute_parallel_safety()` time-complexity on large active-slice sets**: O(C × A × |hint|) where C = candidates (≤10), A = active slices (typically 0-3), |hint| = average hint-file set size. Empirically tiny; no optimization needed. Re-check at /build-slice if active-slice set grows unexpectedly.
- **Whether `derive_active_slice_blast_radius()` should fall back to `mission-brief.md` `## Wiring matrix` if `design.md` doesn't exist yet** (a slice in /slice or /design-slice stage hasn't written design.md yet) — current design says "prefer design.md, fallback to mission-brief.md `## Dependencies`"; /build-slice plan-mode will confirm against the actual `_index.md` `## Active` table shape.
- **Whether to surface the `architecture/slice-queue.md` file in `/pulse` output** (one-line "Queue freshness: <timestamp>" + top-3 NON-OVERLAPPING candidates) — likely a slice-068 deliverable; explicitly OUT of slice-067 scope.
