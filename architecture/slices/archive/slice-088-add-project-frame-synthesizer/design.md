# Design: Slice 088 add-project-frame-synthesizer

**Date**: 2026-05-31
**Mode**: Standard

## What's new

- **`tools/project_frame_synth.py`** — a deterministic extraction-and-render tool (NOT an LLM skill — see [[ADR-080]]) that synthesizes an **ephemeral project-frame**: a ≤40-line, synthesis-not-dump view of **Identity** (what this project is), **Trajectory** (where it is deliberately heading), and **Impact** (this slice's effect on the whole). Emits to **stdout** (ephemeral; nothing tracked is written). Library API `synthesize_frame(repo_root, slice_dir) -> str` + CLI `python -m tools.project_frame_synth --repo-root . --slice-dir <slice-folder>`.
- **PFS-1** (new RULE-ID, minted by [[ADR-080]]; `methodology-changelog.md` bump at build) — the project-frame consult/input discipline wired into three review surfaces.
- **`skills/design-slice/SKILL.md`** — new **Step 0.5 "Consult the project-frame BEFORE designing"** (shift-left): run the synth, read the frame, design direction-aware. **(M5 fix)** At Step 0.5 the active slice's `design.md` does NOT yet exist (written at Step 4), so the **Impact** section is **expected-degraded to mission-brief-only** and the stderr WARN is **normal, not an error** — the Step 0.5 prose states this explicitly. The "re-synthesize Impact against the drafted `design.md` at hand-off" idea is **dropped from this slice** (no consumer, no observable outcome, no test row — would be an AC with no design element); Impact = mission-brief at design-time, mission-brief + design.md whenever both exist (e.g. at `/critique` time). AC #2 is reworded to drop the hand-off re-synth claim.
- **`skills/critique/SKILL.md`** — Step 1 Inputs + Step 2 agent-prompt body gain a `# project-frame.md` block handed to the Critic agent.
- **`skills/critique-review/SKILL.md`** — Step 1 Inputs + Step 2 agent-prompt body gain the same `# project-frame.md` block handed to the meta-Critic agent.
- **`agents/critique.md`** — Dim-7 (b) "Strategic-direction fit" probe (shipped `64f6ea3`) updated: consume the **handed-over** ephemeral frame instead of re-fetching trajectory artifacts itself (CAD-1-guarded edit — existing `tests/methodology/test_critique_agent_drift.py`).
- **OSDG-1 guarded-set extension (NEW — corrects a mission-brief assumption).** `design-slice`, `critique`, and `critique-review` are **NOT** currently in the OSDG-1 guarded set (verified on disk: no `test_design_slice_skill_drift.py` / `test_critique_skill_drift.py` / `test_critique_review_skill_drift.py` exist — the brief's "reuse existing …family" footnote is factually wrong). Because this slice edits all three SKILL.md files, it **creates three new** drift tests and adds the three skills to the OSDG-1 guarded set, plus updates the OSDG-1 description in root `CLAUDE.md`. Each new test reuses `tests/skill_drift_equality.py::assert_md_forward_synced` (EOL-agnostic per ADR-033 / EOL-DRIFT-1), modeled on `tests/methodology/test_reflect_skill_drift.py`.
  - **(M3b fix) Root `CLAUDE.md` is a tracked edited surface.** It is added to this slice's edited-surfaces list. Its "Mini-CAD / OSDG-1" bullet enumerates the guarded set in prose; editing it risks the slice-086 B2 class (a contradicted OSDG-1 membership claim shipping). Enforcement: the **3 new drift tests + the inventory-pin are the load-bearing artifacts** (they make the membership real); the `CLAUDE.md` prose enumeration is **documentation forward-synced manually**, captured as a must-not-defer ("the CLAUDE.md OSDG-1 prose now names design-slice/critique/critique-review and matches the actual test set"). No new audit is minted for the prose — the test set is the truth; the prose tracks it.
- Tests: 3 behavioral on the tool, 3 structural-pins on the skill edits, **3 NEW OSDG-1 drift tests** (design-slice/critique/critique-review), CAD-1 on the agent (existing test), 1 inventory-pin.

## What's reused

- Truth-sources the synth reads (read-only, **all under `--repo-root`** so the deterministic test is fixturable — m1 fix): `architecture/concept.md`, `architecture/triage.md` (identity); the **in-repo** `methodology-changelog.md` (repo root — NOT the `~/.claude/` install copy, which is the AVFS-1/MCFS-1 forward-sync surface, not the source of truth) recent rule-family headers, `architecture/slice-queue.md` (PSQ-1 pending candidates), `architecture/risk-register.md` open entries (impact/trajectory); the active slice's `mission-brief.md` / `design.md` (impact).
- **Binary exit contract** convention from `tools/slice_queue_writer.py` (exit 0 success / 2 usage; **never exit 1** — frame-synth failure is not a slice-regression class; fail-open with a degraded-but-present frame). Same spirit as NAW-1 / ADR-061.
- **RR-1 audit** (`tools/risk_register_audit.py`) for scored open-risk extraction; the synth shells/imports it rather than re-parsing the register.
- The already-shipped Dim-7 probe in `agents/critique.md:125-127` — this slice only swaps its trajectory-source from self-fetch to handed-over frame.
- `tests/skill_drift_equality.py::assert_md_forward_synced` (the shared EOL-agnostic OSDG-1 comparison helper) — the 3 NEW drift tests reuse it; `tools/critique_agent_drift_audit.py` + existing `tests/methodology/test_critique_agent_drift.py` (CAD-1) for the agent edit.

## Components touched

### `tools/project_frame_synth.py` (new)
- **Responsibility**: synthesize a tight, ephemeral, regenerated-per-invocation project-frame so `/design-slice` and both Critic layers review a slice against the project's *deliberate forward direction*, not only its static current artifacts. Surfaces trajectory + conflicts + this-slice's-impact; does NOT judge fit (judgment stays with the Critic — see Out of scope).
- **Lives at**: `tools/project_frame_synth.py` (created by this slice).
- **Key interactions**: reads `concept.md`, `triage.md`, `methodology-changelog.md`, `slice-queue.md`, `risk-register.md` (via `risk_register_audit`), and the active slice's `mission-brief.md` / `design.md`. Writes nothing tracked; prints frame to stdout. Consumed by the 3 skills' prose invocations.
- **Section contract** (the 3 sections are required; tests pin presence): `## Identity`, `## Trajectory`, `## Impact`.
- **Anchoring guard** (must-not-defer): the frame's first line is an explicit adversarial-lens preamble: `ATTACK-LENS -- use this to find where the slice fights the project's direction; do NOT nod along` — the artifact carries its own anti-anchoring instruction.
- **Tight-budget**: module constant `_MAX_FRAME_LINES = 40`; render truncates with a `... (frame truncated to budget)` marker rather than overflowing.
- **Synthesis, not concatenation (M4 — testable property)**: the render is selective extraction + dedup + score-ranking under the hard budget, with a **behavioral guarantee a naive concatenation provably fails**: Trajectory names the **deduped active rule-FAMILY** (`PSQ` / `BRANCH-2`, extracted from changelog headers — not raw header lines), open risks **sorted by score with the score shown**, and slice-queue candidates **by name**. Pinned by `test_frame_trajectory_synthesizes_not_concatenates`.
- **Determinism**: no wall-clock, no randomness; stable ordering (risks sorted by score, rule-families by changelog order, candidates by queue order). Identical fixtures -> byte-identical frame.
- **(B1 / M-add-1 — RESOLVED via UTF8-STDOUT-1; design deviation 2026-05-31, user-approved).** cp1252 stdout safety is achieved the codebase-standard way: `main()` calls `_stdout.reconfigure_stdout_utf8()` as its FIRST statement (UTF8-STDOUT-1, mandatory for every `tools/*.py` with `main()`), reconfiguring stdout to UTF-8 `errors="replace"`. This makes the em-dash/arrow crash **impossible without transliteration** — so the dual-Critic's `_ascii_fold()` is **dropped** (redundant + inconsistent with all 20 sibling tools, none of which transliterate; `~/.claude/CLAUDE.md` prescribes UTF-8/`PYTHONUTF8`, NOT ASCII-only). Extracted source text (em-dash-laden changelog/risk headers — the M-add-1 path) emits safely as UTF-8, **preserving fidelity**. The Critics correctly flagged the cp1252 *risk* but prescribed a fix that fights the codebase's established mechanism. Guarded by the bespoke `test_project_frame_synth_survives_cp1252_with_u2192` whose fixture carries em-dash-bearing sources (M-add-2) — the regression guard is retained; only the fix mechanism changed.

### `skills/design-slice/SKILL.md` (modified)
- **Responsibility delta**: adds a shift-left Step 0.5 that consults the project-frame before any design writing; the design is direction-aware from the start.
- **Key interactions**: invokes `tools/project_frame_synth.py`; the frame is advisory context, not a gate.

### `skills/critique/SKILL.md` + `skills/critique-review/SKILL.md` (modified)
- **Responsibility delta**: each adds the project-frame to its Step 1 Inputs list and Step 2 agent-prompt body, so the spawned (meta-)Critic reviews against trajectory.

### `agents/critique.md` (modified)
- **Responsibility delta**: Dim-7 (b) reads the handed-over frame; re-fetches trajectory artifacts only to *verify* a frame claim, not as its primary source.

## Contracts added or changed

### CLI: `python -m tools.project_frame_synth`
- **Invocation**: `--repo-root <path>` (default `.`) `--slice-dir <active-slice-folder>` (required). Optional `--max-lines N` (default 40) for test override.
- **Output**: project-frame markdown to **stdout**. No file written (ephemeral by [[ADR-080]]).
- **Exit codes**: `0` frame emitted (clean OR degraded-with-WARN-to-stderr when a truth-source is missing); `2` usage error (bad/missing `--slice-dir`). **Never `1`** — fail-open.
- **Error cases**: a missing optional truth-source (e.g. no `slice-queue.md`) degrades that section to `_(none)_` + a stderr WARN, never aborts. A missing **required** `--slice-dir` is exit `2`.

## Consumption contract (B3) + structural-pin spec (M6)

**Who runs the synth and how stdout reaches the spawned agent** (the slice's core value seam — was hand-waved; now specified):

- **`/design-slice` Step 0.5**: the skill orchestrator runs `$PY -m tools.project_frame_synth --repo-root . --slice-dir architecture/slices/slice-NNN-<name>` via **Bash**, captures **stdout**, and reads it as direction context before writing `design.md`. Defensive wrapper: on non-zero exit OR empty stdout, proceed with the literal `(project-frame unavailable)` — never block design (matches the error model). Impact section is expected-degraded here (M5).
- **`/critique` Step 2** and **`/critique-review` Step 2**: same Bash capture; the captured stdout is pasted **verbatim** into the agent-prompt body under a fenced block whose header is the unique literal **`# project-frame.md`** (mirroring the existing `# mission-brief.md` / `# design.md` paste-block pattern at `skills/critique/SKILL.md:80-97`). On non-zero/empty, the block body is `(project-frame unavailable)`.

**Structural-pin spec for the 3 tests (BC-PROJ-14-compliant — M6):**

| Test | Unique-to-invocation literal pinned | Seam (heading-scoped, line-anchored) | Shape assertion |
|------|-------------------------------------|--------------------------------------|-----------------|
| `test_design_slice_consults_frame_before_design` | `tools.project_frame_synth` invocation literal + `--slice-dir` | within `(?m)^### Step 0\.5\b` … up to next `^### ` | invocation line present in the Step-0.5 seam AND the seam ordinally precedes the Step-1/design-writing seam (the "BEFORE designing" property) |
| `test_critique_inputs_include_project_frame` | the `# project-frame.md` block header | within `(?m)^### Step 2:` (the agent-prompt body) of `skills/critique/SKILL.md` | header present in the Step-2 prompt-body seam, line-anchored — NOT a bare `.find("project-frame")` (a value-line substring would mask a real omission) |
| `test_critique_review_inputs_include_project_frame` | the `# project-frame.md` block header | within `(?m)^### Step 2:` of `skills/critique-review/SKILL.md` | same shape rule |

No bare `.find()`; every pin uses a line-anchored heading scope + a literal that appears nowhere else in the file (`# project-frame.md` as a fenced-block header is unique to the new input). Resolves the BC-PROJ-14 (a)/(b)/(c) obligations.

## Data model deltas

None. No persistent entity; the frame is transient stdout.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/project_frame_synth.py` | `skills/design-slice/SKILL.md` Step 0.5 + `skills/critique/SKILL.md` Step 1/2 + `skills/critique-review/SKILL.md` Step 1/2 (prose invocations) | `tests/methodology/test_project_frame_synth.py::test_frame_has_identity_trajectory_impact` (+ the 3 structural-pin tests on the consumers) | — |

## Decisions made (ADRs)

- [[ADR-080]] — Project-frame is a deterministic extraction-and-render **tool** (not an LLM `/frame` skill), **ephemeral stdout-only**, and mints **PFS-1** (the consult-before-design + hand-to-both-Critics discipline). — reversibility: **expensive** (methodology rule wired into 3 review surfaces + entry-pin tests). The subordinate tool-vs-skill choice is independently **cheap**-reversible (a `/frame` skill wrapper could be added later without disturbing PFS-1).

## Authorization model for this slice

N/A — a read-only local synthesis tool + skill-prose edits. No auth surface, no network, no writes outside stdout.

## Error model for this slice

- Tool: degrade-and-WARN (stderr) on any missing optional truth-source; exit `2` only on missing required `--slice-dir`; never exit `1` (fail-open — a partial frame is better than no frame, and frame-synth must never block `/design-slice` or `/critique`).
- Skills: the frame is **advisory context**, never a gate — a synth failure must not halt design or critique (the consuming prose wraps the invocation defensively and proceeds with "(project-frame unavailable)" if it fails).

## Anti-anchoring (must-not-defer mirror)

- **Tight, not a dump** — `_MAX_FRAME_LINES = 40` hard budget, pinned by `test_frame_respects_tight_budget`.
- **Ephemeral / regenerated** — stdout-only; no standing `direction.md`; recomputed each invocation ⟹ cannot drift.
- **Anchoring guard** — frame carries an explicit adversarial ATTACK-LENS preamble; Dim-7 phrasing stays adversarial (reviewed at validate).
- **Shift-left** — consulted at `/design-slice` Step 0.5 (before designing), not only at critique.
- **CAD-1 / OSDG-1** — agent + 3 skill edits forward-synced; installed copies content-equal.
- **(B1 + M-add-1) cp1252-safe stdout via `_stdout.reconfigure_stdout_utf8()`** (UTF8-STDOUT-1, mandatory; design deviation from the ratified `_ascii_fold`, user-approved 2026-05-31) — em-dash-laden extracted text emits safely as UTF-8; guarded by the bespoke `test_project_frame_synth_survives_cp1252_with_u2192` whose fixture carries em-dash-bearing sources.
- **(M3b) CLAUDE.md OSDG-1 prose** — the root `CLAUDE.md` "Mini-CAD / OSDG-1" enumeration is updated to name design-slice/critique/critique-review and matches the actual new test set (no contradicted-membership claim ships — slice-086 B2 class).

## MEPD-1 disposition (rule path)

This slice changes behaviour on methodology surfaces (3 skills + 1 agent + 1 new tool) and introduces a reusable discipline → **branch (a) rule path** (per `agents/critique.md` MEPD-1): mint **PFS-1** at version **v0.78.0** (current is 0.77.0); add a `test_methodology_changelog.py::test_v_0_78_0_pfs1_entry_present_in_repo` entry-pin **(M2 fix — the real on-disk convention is `_entry_present_in_repo`, NOT `_entry_present_in_repo_and_installed`; all 66 sibling pins use it; the entry-pin must also assert the META-1 mandatory `Rule reference` literal as every sibling does)**; perform the **5-part PMI-1** atomic bump (`VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` + `## v0.78.0` changelog header + installed `~/.claude/ai-sdlc-VERSION`) at build.

**The PFS-1 v0.78.0 changelog entry MUST also record the OSDG-1 guarded-set extension (M3a):** an explicit line — `OSDG-1 guarded-set extended to design-slice + critique + critique-review (3 new drift tests)` — so the OSDG-1 scope change rides the PFS-1 entry rather than going undischarged.

## BC-PROJ-9 5-surface inventory fan-out (build-time)

New `tools/*.py` module ⟹ update in lockstep: (1) `tools/install_audit.py` `_CANONICAL_TOOLS` (alphabetical insert); (2) **(B2 fix)** `tests/methodology/test_utf8_stdout_regression.py` — do **NOT** add `project_frame_synth` to `_ROOT_ONLY_TOOLS`: that list's `_root_only_argv` passes no required positional, so the tool would hit its **required `--slice-dir`** and exit 2 (usage) before reaching the stdout-render path — silently leaving the B1 cp1252 hot-path uncovered. Instead add a **bespoke `test_project_frame_synth_survives_cp1252_with_u2192`** that invokes it with a real `--repo-root <fixture> --slice-dir <fixture-slice>` argv (mirroring the existing `test_install_audit_survives_cp1252` / `test_slice_queue_claim_survives_cp1252` carve-outs for required-arg tools). **(M-add-2)** Two non-obvious obligations the bespoke test MUST meet: (i) it calls `_assert_no_encoding_error(proc, "tools.project_frame_synth")` with that **exact literal token** — `project_frame_synth.py` has a `main()` so it lands in the rollup sentinel's `discovered_set` (`test_utf8_stdout_regression.py:450-474`); omitting the token fails `test_every_audit_tool_survives_cp1252_stdout_with_u2192_input` with an uncovered-tool parity break; (ii) the fixture `--repo-root`/`--slice-dir` MUST contain **U+2014/U+2192-bearing** changelog + risk-register source, else the test passes **vacuously** while the real M-add-1 em-dash crash ships. (3) `plugin.yaml` tools block (alphabetical); (4) `INSTALL.md` two hard-coded tool-count literals (+1 each); (5) `architecture/shippability.md` new row. Pinned by `test_project_frame_synth_tool_inventory.py`; the cp1252 coverage is the bespoke test, not `_ROOT_ONLY_TOOLS` membership.

## Parallel-slice coordination note (dogfooding)

slice-088 runs in a BRANCH-2 worktree **concurrently** with slice-087 (zero blast-radius overlap). slice-087 (unmerged) already authored **ADR-079**; a naïve `max(ADR)+1` in this worktree would have re-used 079 and collided at merge. This slice therefore takes **ADR-080**, reserving 079 for slice-087. This is a live instance of exactly the trajectory-/concurrency-awareness gap PFS-1 closes — captured here as the slice's first dogfood.

## Graphify status

Blast radius is fully enumerated by the mission brief (5 surfaces, zero overlap with slice-087); graph query not re-run for this tightly-scoped methodology slice. `graphify-out/graph.json` may be stale in this worktree — not load-bearing for this design.
