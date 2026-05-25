# Design: Slice 060 add-code-review-skill

**Date**: 2026-05-23
**Mode**: Standard

## What's new

- **`skills/code-review/SKILL.md`** — new in-loop orchestrator skill, sits between `/build-slice` and `/validate-slice` in the canonical PCA-1 chain; spawns the `code-review` agent against the slice's code diff and writes findings to `architecture/slices/slice-NNN-<name>/code-review.md`.
- **`agents/code-review.md`** — new adversarial Critic-stance agent applying the 9 `/critique` dimensions to CODE (slice diff) rather than DESIGN; read-only tool set; output format mirrors `agents/critique.md`'s blockers/majors/minors structure (NO Triage section in v1 — TRI-1 gate deferred to slice-062).
- **`architecture/decisions/ADR-059-add-code-review-skill.md`** — main ADR establishing RULE-ID **CRSI-1** (Code-Review Skill Insertion); records (a) the in-loop position decision, (b) the walking-skeleton scope choice, (c) the deferred classes (AI-bloat passes / TRI-1 / verdict-driven block), (d) the read-only agent stance, (e) reversibility tag.
- **`tests/skills/code_review/test_code_review_skill.py`** — pins the new skill's `## Pipeline position` block + `successor: /validate-slice` declaration + self-dogfood end-to-end produces `code-review.md` on slice-060.
- **`tests/agents/test_code_review_agent.py`** — pins the new agent's 9-dimensions-vs-code prompt + read-only tools declaration + specificity rule (`path/to/file.py:line`).
- **`tests/methodology/test_code_review_skill_drift.py`** — OSDG-1 family member-add (follows slice-049/051 lineage); reuses `tests/skill_drift_equality.py::assert_md_forward_synced` (EOL-agnostic per EOL-DRIFT-1 / ADR-033).
- **`tests/methodology/test_code_review_agent_drift.py`** — agent-drift sibling guard following the same lineage; reuses `assert_md_forward_synced`.
- **`tests/methodology/test_methodology_changelog.py::test_v_0_64_0_crsi_1_entry_present_in_repo`** — new entry-pin under the existing META-1 test module (no new module). Per slice-051 / slice-058 / slice-059 content-bearing-pin discipline, asserts **8 substring presences** in the v0.64.0 entry: (a) `## v0.64.0` header, (b) `CRSI-1` rule ID, (c) `ADR-059` reference, (d) full rule-name expansion `Code-Review Skill Insertion`, (e) `mints a new rule` + `supersedes nothing` lineage clauses, (f) `5-part PMI-1 atomic bump` (per critique B2 5-part-bump fix), (g) `Rule reference` literal (META-1 enforcing-assertion at `tests/methodology/test_methodology_changelog.py:136` requires this in each `## v…` section), (h) OSDG-1 / CAD-1 lineage anchor. Name shape matches slice-059 precedent (`test_v_0_NN_0_<rule>_entry_present_in_repo`).
- **`tests/methodology/test_methodology_changelog.py::test_v_0_64_0_crsi_1_shippability_consumer_propagation`** — **paired propagation pin** (per /critique-review M-add-2 — BC-PROJ-10 verbatim at `architecture/build-checks.md:173` requires "the conventional `test_v_0_NN_0_*_entry_present_in_repo` + `*_shippability_consumer_propagation` test pair"; N≥17 instances of the pair stable across the live test module; missing it was a meta-Critic-caught fan-out undercount). Asserts: (a) `architecture/shippability.md` contains the literal `CRSI-1` (BCR-1 traceability axis); (b) the catalog contains a `tools.shippability_runner` consumer reference for row #60 OR a pytest-based equivalent (the slice's shippability row #60 IS the row being propagated); (c) the catalog references the literal `code_review_skill_drift` AND `code_review_agent_drift` test modules (SCPD-1 axis — row #60 silently regresses if a future slice renames these test modules). Per Newman *Building Microservices* consumer-driven-contracts + BCR-1 / SCPD-1 lineage.
- **`tests/methodology/test_shippability_runner_segment_contract.py::test_code_review_dogfood_row_runs_clean`** — pins new shippability row #60 under the existing SRSC-1 test module (no new module). See "## Shippability catalog row #60 design" below for the row's Command-cell pytest selector list + tripwire description.
- **`tests/agents/__init__.py`** (NEW empty package init — per /critique B3 PTFCD-1 phantom-path remediation; created BEFORE any `tests/agents/*.py` so pytest can collect the subpackage).
- **`tests/skills/code_review/__init__.py`** (NEW empty package init — per /critique B3; created BEFORE any `tests/skills/code_review/*.py`).

## What's reused

- [[agents/critique.md]] — adversarial prompt **structural template**; `agents/code-review.md` inherits stance, the 9 dimensions (with design→code substitution), the framework citations, the specificity rule, the calibration awareness, and the output-format scaffold. Tool set parity (`Read, Glob, Grep, Bash, WebSearch`) preserved — Dim 8 (Web-known issues) benefits from WebSearch on platform-API misuses just as the design Critic does.
- [[skills/critique/SKILL.md]] — orchestration **structural template**; `skills/code-review/SKILL.md` inherits Agent-tool spawn pattern (`subagent_type: "code-review"`), the "hand the agent the inputs, don't repeat the prompt body" discipline, the write-findings-to-`code-review.md` pattern, the `## Pipeline position` block shape.
- `tests/skill_drift_equality.py::assert_md_forward_synced` (slice-033 / EOL-DRIFT-1 / ADR-033) — sole comparator for both new drift tests; do NOT introduce a new byte-equality comparator (R-5 retirement preserved).
- `tools/pipeline_chain_audit.py` (slice-027 / PCA-1 / ADR-025) — extended via 2-line `_CANONICAL_CHAIN` tuple-of-tuples change at `tools/pipeline_chain_audit.py:73-82` (NOT cloned; not refactored — modified in place per CLAUDE.md "refactors need a slice"; the change is a single-tuple-add + single-tuple-edit on lines 78-79).
- `tools/plugin_manifest_audit.py` (slice-006 / PMI-1) — no code change; PMI-1 auto-discovers `skills/code-review/` + `agents/code-review.md` from `plugin.yaml` after the YAML inventory is extended.
- `tools/install_audit.py` (INST-1) — extend `_CANONICAL_SKILLS` (line 52-59) with `"code-review"` and `_CANONICAL_AGENTS` (line 61-64) with `"code-review"`. `_CANONICAL_TOOLS` (line 88) is **unchanged** — this slice introduces NO new `tools/*.py` (see "What's new" — all enforcement is via tests calling existing comparators, the slice-049/051 OSDG-1 family-add pattern, NOT the slice-007 CAD-1 dedicated-tool pattern).
- `architecture/shippability.md` — catalog format pinned by SCMD-1 / PTFCD-1 / SRSC-1; one new 6-column row appended for the self-dogfood regression guard.
- `methodology-changelog.md` — `## v0.64.0 — 2026-05-23` entry appended (META-1 `^## v…` split-format pinned at `tests/methodology/test_methodology_changelog.py:136`). Entry body includes a bridge sentence acknowledging the PCA-1 canonical chain transition from **8 → 9 covered skills** (per /critique m1, SUP-1 append-only preserves v0.41.0's historical "8 covered skills" phrasing verbatim — the bridge sentence lives in the new v0.64.0 entry, not as an in-place edit).
- `VERSION` (0.63.0 → 0.64.0), `plugin.yaml` `version:` (0.63.0 → 0.64.0), **`pyproject.toml [project].version` (0.63.0 → 0.64.0)**, installed `~/.claude/ai-sdlc-VERSION` + installed `~/.claude/methodology-changelog.md` — **5-part** PMI-1 atomic bump per slice-050 AVFS-1 + slice-054 PVFS-1 + slice-041 MCFS-1 + slice-006 PMI-1 lineage (slice-059 5-part precedent inherited; pyproject.toml leg is what /critique B2 caught as missing in the original draft).
- `architecture/shippability.md` row #27 (PCA-1 catalog row, slice-027) — **SCPD-1 sub-mode (b) consumer-reference propagation** surface: the row's Command cell references `test_clean_chain_exits_zero` literally. Slice-060 updates that test's `== 8` assertion to `== 9` (per /critique B5), keeping row #27's Command continuing to PASS without a row edit. The row prose remains historical record per SUP-1.

## Components touched

### skills/code-review (NEW)
- **Responsibility**: orchestrate adversarial code-review of the slice diff in-loop after `/build-slice`; spawn the `code-review` agent; write findings; auto-advance to `/validate-slice`. Findings are **advisory only in v1** — no verdict-driven block on the successor (TRI-1 + block deferred to slice-062).
- **Lives at**: `skills/code-review/SKILL.md` (created by this slice) + installed copy at `~/.claude/skills/code-review/SKILL.md` (forward-synced at slice build-time).
- **Key interactions**:
  - **Predecessor**: `/build-slice` PCA-1 auto-advance invokes `/code-review` on pre-finish gate clean (post-slice-060 `_CANONICAL_CHAIN`).
  - **Successor**: `/validate-slice` (auto-advance: true; advisory findings do not block).
  - **Worker**: `agents/code-review.md` (spawned via Agent tool with `subagent_type: "code-review"`).
  - **Inputs read**: active slice folder's `mission-brief.md`, `design.md`, any new ADRs, plus the slice's filtered code diff (see "Diff source contract" below).
  - **Output written**: `architecture/slices/slice-NNN-<name>/code-review.md`.

### agents/code-review (NEW)
- **Responsibility**: read-only adversarial code-review applying the 9 critique dimensions to the slice's code diff (NOT the design). Returns findings text (blockers/majors/minors with `path/to/file.py:line` specificity) to the orchestrating skill.
- **Lives at**: `agents/code-review.md` (created by this slice) + installed copy at `~/.claude/agents/code-review.md` (forward-synced at slice build-time).
- **Key interactions**:
  - Invoked ONLY by `/code-review` skill (single consumer).
  - Tool set: `Read, Glob, Grep, Bash, WebSearch` (matches `agents/critique.md` verbatim; WebSearch retained for Dim 8 platform-API misuse checks).
  - **Write tools forbidden**: NO `Write`, `Edit`, `NotebookEdit` — read-only stance preserved (must-not-defer #2).
  - **Model**: `opus` (matches `agents/critique.md`; depth of reasoning matters more than latency for adversarial review).

### tools/pipeline_chain_audit.py (MODIFY)
- **Responsibility**: PCA-1 audit, extended to validate the new `/build-slice → /code-review → /validate-slice` chain shape.
- **Lives at**: `tools/pipeline_chain_audit.py`.
- **Key interactions** — per /critique B5 the extension is NOT just a 2-line tuple change; the chain-length transition 8→9 propagates to **6 hardcoded "8" sites** that must be updated in lock-step:
  - `tools/pipeline_chain_audit.py:73-82` — `_CANONICAL_CHAIN` tuple-of-tuples: line 78 changes from `("build-slice", "/validate-slice", True),` to `("build-slice", "/code-review", True),`; a new tuple `("code-review", "/validate-slice", True),` inserts between the build-slice and validate-slice entries.
  - `tools/pipeline_chain_audit.py:56` — exit-code docstring "all 8 blocks well-formed" → "all 9 blocks well-formed"
  - `tools/pipeline_chain_audit.py:225` — error message "PCA-1 requires it on all 8 covered skills)" → "all 9 covered skills)"
  - `tools/pipeline_chain_audit.py:309` — argparse description "verify the 8-skill pipeline-chain auto-advance" → "verify the 9-skill pipeline-chain auto-advance"
  - `tools/pipeline_chain_audit.py:5-30` — Description docstring's chain-shape narrative + `[N]` reference notes: the canonical chain table grows from 8 → 9 entries; the new `/code-review` line is added between `build-slice` and `validate-slice`.
  - `tests/methodology/test_pipeline_chain_audit.py:66` — `assert len(result.skills_checked) == 8` → `== 9` (per TF-1 row 9 UPDATE; this is the SCPD-1 row #27 consumer-reference-propagation target).
  - `tests/methodology/test_pipeline_chain_audit.py:4` — docstring "all 8 covered skills" → "all 9 covered skills"
  - `tests/methodology/test_pipeline_position_block_drift.py` — docstring/message drift on "8 covered skills" → "9" (file scan during /build-slice plan-mode; per TF-1 row 10 UPDATE).
- The `_REQUIRED_FIELDS` tuple, parsing logic, `audit()` function body, and `main()` argument-parsing remain unchanged (the chain count is data not code; the structural fields don't change).

### skills/build-slice/SKILL.md (MODIFY)
- **Responsibility**: update `## Pipeline position` block's `successor:` field from `/validate-slice` to `/code-review`; update `on-clean-completion` prose to reference `/code-review` as the next-step invocation target.
- **Lives at**: `skills/build-slice/SKILL.md:547-552` (the existing Pipeline position block); installed copy at `~/.claude/skills/build-slice/SKILL.md` (forward-synced).
- **Key interactions**: PCA-1 reads `successor:` for chain-shape validation (`tools/pipeline_chain_audit.py:_parse_fields`); OSDG-1 forward-sync test (`tests/methodology/test_build_slice_skill_drift.py`) re-pins on the EOL-normalized hash.

### skills/validate-slice/SKILL.md (MODIFY)
- **Responsibility**: update `## Pipeline position` block's `predecessor:` field from `/build-slice` to `/code-review`.
- **Lives at**: `skills/validate-slice/SKILL.md:299` (the existing Pipeline position block); installed copy at `~/.claude/skills/validate-slice/SKILL.md` (forward-synced).
- **Key interactions**: PCA-1 reads `predecessor:` (informational; PCA-1 currently validates `successor:` only, but the field is structurally required by `_REQUIRED_FIELDS` and the OSDG-1 drift guard pins its content). `tests/methodology/test_validate_slice_skill.py` (new test row) pins the post-edit predecessor literal.

### tools/install_audit.py (MODIFY)
- **Responsibility**: extend INST-1 canonical inventory to enumerate `code-review` skill + `code-review` agent.
- **Lives at**: `tools/install_audit.py:52-64` + `:84` (PCA-1 comment).
- **Key interactions** — per /critique B1 alphabetical insertion points recomputed against the live file:
  - **`_CANONICAL_SKILLS`**: insert `"code-review"` **between `"build-slice"` and `"commit-slice"`** (ASCII: `code-r` < `commit-` because `o` < `o` tie then `d` < `m`).
  - **`_CANONICAL_AGENTS`**: **prepend `"code-review"`** as the FIRST entry, before `"critic-calibrate"` (ASCII: `code-r` < `critic-` because `o` < `r`).
  - **`tools/install_audit.py:84`** — PCA-1 inventory comment "verify the 8-skill pipeline-chain auto-advance loop" → "verify the 9-skill pipeline-chain auto-advance loop" (per /critique B5 chain-length transition).
  - NO change to `_CANONICAL_TOOLS` — this slice ships no new `tools/*.py`.

### plugin.yaml (MODIFY)
- **Responsibility**: extend PMI-1 plugin manifest to enumerate `code-review` skill + agent + their on-disk paths.
- **Lives at**: `plugin.yaml`.
- **Key interactions**: PMI-1 audit cross-validates plugin.yaml inventory ↔ filesystem ↔ `_CANONICAL_*` tuples ↔ `_REGISTERED_INSTALLED_READERS`. Two new entries: one under `skills:` (`- id: code-review`, `path: skills/code-review`), one under `agents:` (`- id: code-review`, `path: agents/code-review.md`). `version:` field bumped 0.63.0 → 0.64.0 in lock-step with VERSION.

### methodology-changelog.md (MODIFY)
- **Responsibility**: record CRSI-1 + ADR-059 + walking-skeleton scope + deferred classes; provide the entry-pin for the META-1 `^## v…` test.
- **Lives at**: `methodology-changelog.md` (in-repo) + `~/.claude/methodology-changelog.md` (installed, forward-synced per MCFS-1).
- **Key interactions**: appended `## v0.64.0 — 2026-05-23` section with required `Rule reference` substring (per META-1) referencing CRSI-1 + the prose body referencing ADR-059. MCFS-1 forward-sync at `/build-slice` Step 6 + `/reflect` Step 5b-fs ensures installed copy stays in lock-step.

## Contracts added or changed

### `/code-review` skill invocation contract (NEW)

- **Skill ID**: `code-review`
- **Invocation**: via the Claude Code Skill tool (`Skill { skill: "code-review" }`); also auto-invoked by `/build-slice`'s PCA-1 auto-advance on pre-finish gate clean.
- **Prerequisite reads**:
  - Find active slice folder per the standard SKILL-prose pattern (check `architecture/slices/_index.md` "Currently active slice", else stat `architecture/slices/slice-*/` for one stage-active milestone.md — same pattern as `skills/critique/SKILL.md:53`). Note: `_resolve_slice_dir` at `tests/methodology/conftest.py:20` is a pytest collection helper used ONLY in the test side (e.g., `tests/skills/code_review/test_code_review_skill.py` resolves slice-060's folder via that helper); SKILL.md runtime cannot call Python helpers. Per /critique m2 — design-time runtime/test layer separation enforced.
  - `mission-brief.md`, `design.md`, all new `ADR-NNN-*.md` files in this slice.
  - `build-log.md` — if it shows `Result: NOT-SHIPPED`: STOP with explicit message ("`/code-review` cannot review a slice that isn't built yet — run `/build-slice` first").
- **Diff source contract**:
  ```bash
  default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
  [ -z "$default" ] && default=$(git config init.defaultBranch 2>/dev/null)
  base=$(git merge-base "$default" HEAD)
  git diff "$base"...HEAD --name-only --diff-filter=ACMR -- ':(exclude)architecture/**' ':(exclude)docs/**'
  ```
  - Default-branch resolution mirrors the BRANCH-1 pattern (slice-021).
  - `--diff-filter=ACMR` includes Added/Copied/Modified/Renamed; deletions excluded (no code to review on a delete).
  - **In-scope paths** (per /critique M3 — METHODOLOGY-PROSE-AS-EXECUTABLE-CONTRACT is in scope; CLAUDE.md self-hosting-discipline: "skill prose IS executable contract"):
    - `skills/**/SKILL.md` — methodology orchestrator prose (executable contract)
    - `agents/*.md` — agent prompts (executable contract)
    - `tools/**/*.py` — audit + lint Python modules
    - `tests/**/*.py` — test modules
    - Root-level config files — `plugin.yaml`, `pyproject.toml`, `VERSION`, `methodology-changelog.md`
  - **Out-of-scope paths** — `architecture/**` (vault — gitignored, separate review surface via `/drift-check`), `docs/**` (if any — pure documentation).
  - Slice-060's self-dogfood will produce findings on the new `skills/code-review/SKILL.md` + `agents/code-review.md` prose itself — this is the load-bearing RSAD-1 self-application proof. SKILL.md / agent.md noise tolerance is a v1 advisory-only concession; slice-061 will tune AI-bloat passes to weight `.py` code higher than methodology prose.
  - On `default-branch-unresolvable`: STOP with the BRANCH-1-shaped error and instruct the user to re-run after the default branch resolves.
- **Empty-diff handling**: if the filtered diff list is empty, the skill writes a minimal `code-review.md`:
  ```markdown
  # Code review: Slice NNN <name>

  **Date**: <YYYY-MM-DD>
  **Result**: NO-CODE-CHANGES — nothing to review

  This slice's diff against the default branch contains no non-vault file changes
  (architecture/** is excluded by design). The /code-review agent was not invoked.
  ```
  and exits clean (auto-advance to `/validate-slice` proceeds). This is the operational footgun gate per must-not-defer #3.
- **Output**: `architecture/slices/slice-NNN-<name>/code-review.md` (always written, even on NO-CODE-CHANGES).
- **Auto-advance**: on clean completion (`code-review.md` written), invoke `/validate-slice` via the Skill tool without waiting for the user. NO user-input gates in v1 (advisory only).

### `code-review` agent invocation contract (NEW)

- **subagent_type**: `"code-review"`
- **Tools**: `Read, Glob, Grep, Bash, WebSearch` (5 tools — matches `agents/critique.md:4` verbatim for CSP-1 parity; the read-only stance is enforced by **omitting** Write/Edit/NotebookEdit from the agent's `tools:` frontmatter line, NOT by prose — the Claude Code subagent runtime restricts tool access to the explicit list per [Claude Code docs / Create custom subagents](https://code.claude.com/docs/en/sub-agents)).
- **Test contract for `test_agent_md_read_only_tools_pinned`** (per /critique B4 + slice-007 M2 + slice-053 M-add-4 positive-and-negative substring pattern): assert literal `tools: Read, Glob, Grep, Bash, WebSearch` is present in the agent file AND assert each of `Write`, `Edit`, `NotebookEdit` are absent from the `tools:` line. Both directions in the same test — the negative assertions catch a future `tools: Read, Glob, Grep, Bash, WebSearch, Edit` regression.
- **Model**: `opus`.
- **Input prompt body** (skill orchestrates):
  ```
  Slice: slice-NNN-<name>
  Mode: <Minimal | Standard | Heavy>
  Risk tier: <low | medium | high>

  # mission-brief.md
  <paste full contents>

  # design.md
  <paste full contents>

  # New ADRs (if any)
  <paste contents of each ADR-NNN-*.md created by this slice>

  # Changed files (code diff scope)
  <one path per line; vault paths excluded>

  # Diff content
  <git diff <base>...HEAD -- <files> output, pasted; size-limited per Claude Code prompt budget>
  ```
- **Output structure**: the agent returns markdown matching `agents/critique.md`'s output format — `## Findings` with `### Blockers` / `### Majors` / `### Minors` subsections, each finding citing `path/to/file.py:line` per the inherited specificity rule. NO `## Triage` section (slice-062's TRI-1 extension owns that). The agent MUST also include a `## Dimensions checked` footer listing each of the 9 dimensions with `findings or "none"` (calibration record).
- **Error model**:
  - Agent missing or unspawnable → skill exits 1 with explicit error, MUST NOT silently advance.
  - Agent returns empty output → skill writes a `code-review.md` with `Result: AGENT-EMPTY — re-run with verbosity` and exits 1 (do NOT auto-advance on agent empty; this is the rubber-stamp footgun from `agents/critique.md`'s failure-mode-to-watch list).
  - Agent returns malformed structure (missing required sections) → skill writes the raw output verbatim into `code-review.md` and surfaces a warning to the user, but does auto-advance (advisory mode, slice-061 hardens this).

### `/code-review` Pipeline-position block contract (NEW)

```markdown
## Pipeline position

- **predecessor**: `/build-slice`
- **successor**: `/validate-slice`
- **auto-advance**: true
- **on-clean-completion**: once `code-review.md` is written (including the NO-CODE-CHANGES path), invoke `/validate-slice` via the Skill tool without waiting for the user.
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - None in v1 — findings are advisory only. slice-062 will add a TRI-1 verdict-driven HALT-on-BLOCKED gate.

> Per PCA-1 (methodology-changelog.md v0.41.0). The `## Next step` section above is the human-readable companion; this block is the machine-actionable auto-advance directive. Manual invocation remains supported.
```

### `tools/pipeline_chain_audit.py` `_CANONICAL_CHAIN` extension (MODIFY)

Post-slice-060 canonical chain:

```python
_CANONICAL_CHAIN: tuple[tuple[str, str, bool], ...] = (
    ("slice", "/design-slice", True),
    ("design-slice", "/critique", True),
    ("critique", "/critique-review", True),
    ("critique-review", "/critique", True),
    ("build-slice", "/code-review", True),       # CHANGED: was "/validate-slice"
    ("code-review", "/validate-slice", True),    # NEW: walking-skeleton edge
    ("validate-slice", "/reflect", True),
    ("reflect", "/commit-slice", False),
    ("commit-slice", "/slice", False),
)
```

The chain length grows from 8 entries to 9. The `Description` docstring at lines 5-30 of the file MUST be updated in lock-step (the canonical chain shape narrative + `[N]` reference notes).

## Data model deltas

None. This slice introduces no persistent data model changes.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Every new module/file this slice introduces declares a consumer entry point + a consumer test, OR an exemption with explicit rationale.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `skills/code-review/SKILL.md` | `tools/pipeline_chain_audit.py` (post-extension `_CANONICAL_CHAIN` reads the skill's `## Pipeline position` block at audit-time) AND the Claude Code Skill-tool runtime (cross-loop consumer via PCA-1 auto-advance from `/build-slice`) | `tests/skills/code_review/test_code_review_skill.py::test_self_dogfood_produces_code_review_md_on_slice_060` | — |
| `agents/code-review.md` | `skills/code-review/SKILL.md` (the skill invokes the Agent tool with `subagent_type: "code-review"` — sole consumer) | `tests/agents/test_code_review_agent.py::test_agent_md_contains_nine_dimensions_against_code` | — |
| `architecture/decisions/ADR-059-add-code-review-skill.md` | `methodology-changelog.md` v0.64.0 entry (prose cross-ref) AND `architecture/slices/slice-060-.../design.md` (this file's "Decisions made" section) | — | `vault ADR file — consumer test exemption per WIRE-1 vault-file convention; ADRs are append-only doc artifacts, not source modules — rationale: ADRs are read by humans and by the LLM at audit-time via Read, never imported as code; precedent class slice-019/021/025/030/039/050/058 all carry the same exemption for their ADR files` |

Existing modules being extended (NOT new modules — WIRE-1 covers introductions, not edits): `tools/pipeline_chain_audit.py`, `tools/install_audit.py`, `skills/build-slice/SKILL.md`, `skills/validate-slice/SKILL.md`, `plugin.yaml`, `methodology-changelog.md`, `VERSION`, `architecture/shippability.md`.

## Decisions made (ADRs)

- [[ADR-059]] — Add `/code-review` as an in-loop walking-skeleton step between `/build-slice` and `/validate-slice`; new RULE-ID **CRSI-1**; findings advisory only in v1 (TRI-1 gate + AI-bloat passes + verdict-driven block deferred to slices 061/062) — **reversibility: cheap** (the chain edge is one 2-line `_CANONICAL_CHAIN` change to undo; the skill + agent are deletable; no consumers outside the methodology chain; no data model, no external contract).

## Authorization model for this slice

This slice introduces no user-facing authorization surface — `/code-review` is invoked by:
1. The Claude Code Skill tool (developer's own session — no auth model beyond the developer's machine).
2. PCA-1 auto-advance from `/build-slice` (intra-pipeline; trust boundary is the same session).

The agent's read-only tool set (no `Write`/`Edit`/`NotebookEdit`) is the **only** access-control surface — it prevents the agent from modifying source/vault/test/config files even if its prompt were adversarially compromised. This is the load-bearing safety invariant per must-not-defer #2 and ADR-059's "Read-only stance" decision.

`WebSearch` is permitted (Dim 8 needs it for platform-API misuse checks); searches are inherently outward-facing but read-only with respect to the repo.

## Error model for this slice

| Error class | Trigger | Where raised | Skill behavior |
|---|---|---|---|
| `mission-brief-missing` | `mission-brief.md` absent in active slice folder | `skills/code-review/SKILL.md` Prerequisite check | STOP with explicit user message; do NOT auto-advance |
| `design-md-missing` | `design.md` absent in active slice folder | `skills/code-review/SKILL.md` Prerequisite check | STOP with explicit user message; do NOT auto-advance |
| `build-log-not-shipped` | `build-log.md` shows `Result: NOT-SHIPPED` | `skills/code-review/SKILL.md` Prerequisite check | STOP with "run /build-slice first" message; do NOT auto-advance |
| `default-branch-unresolvable` | both `git symbolic-ref` and `git config init.defaultBranch` fail | `skills/code-review/SKILL.md` Diff source contract | STOP with BRANCH-1-shaped error; do NOT auto-advance |
| `no-code-changes` | filtered diff is empty | `skills/code-review/SKILL.md` Empty-diff handling | Write minimal `code-review.md` with `Result: NO-CODE-CHANGES`; auto-advance to `/validate-slice` (clean exit) |
| `agent-unspawnable` | Agent tool raises on `subagent_type: "code-review"` | `skills/code-review/SKILL.md` Step 2 | Exit 1 with explicit error; do NOT auto-advance |
| `agent-empty-output` | agent returns zero-length output | `skills/code-review/SKILL.md` Step 3 | Write `code-review.md` with `Result: AGENT-EMPTY`; exit 1; do NOT auto-advance |
| `agent-malformed-output` | agent returns text but required sections (Blockers/Majors/Minors/Dimensions checked) are missing | `skills/code-review/SKILL.md` Step 3 | Write raw output verbatim into `code-review.md`; surface warning to user; auto-advance (advisory mode — slice-061 hardens) |

No new error codes are introduced into any user-facing API — this is a methodology-internal surface.

## PCA-1 bootstrap-discharge (mirrors CRP-1 slice-026 / PCA-1 slice-027)

Slice-060 itself authors the new chain shape. At slice-060's own `/build-slice` Step 6 pre-finish, the PCA-1 audit (`$PY -m tools.pipeline_chain_audit`) is run against the post-slice-060 repo with:

- The updated `_CANONICAL_CHAIN` tuple-of-tuples in `tools/pipeline_chain_audit.py`.
- The new `skills/code-review/SKILL.md` carrying its `## Pipeline position` block (predecessor `/build-slice`, successor `/validate-slice`, auto-advance true).
- The updated `skills/build-slice/SKILL.md` `## Pipeline position` block (successor `/code-review`).
- The updated `skills/validate-slice/SKILL.md` `## Pipeline position` block (predecessor `/code-review`).

The audit MUST exit 0. The bootstrap-discharge is the self-application proof — slice-060's own self-gating PCA-1 run validates the chain it just authored. The mechanic is identical to CRP-1's slice-026 bootstrap (slice-026 authors CRP-1; the audit runs on slice-026's own folder and discharges via `/critique-review` having been run on slice-026 itself) and PCA-1's slice-027 bootstrap (slice-027 authors PCA-1; the audit runs on the post-slice-027 repo and discharges via the chain being internally consistent).

Every slice after slice-060 inherits a self-gating PCA-1 against the 9-entry canonical chain.

## CSP-1 cross-spec parity

Per CSP-1: the `code-review` agent inherits structural fields from `critique.md` (model, dimensions count, citation framework table, output format scaffold, calibration awareness). The cross-spec parity points:

- `tools: Read, Glob, Grep, Bash, WebSearch` — identical to `agents/critique.md:4`.
- `model: opus` — identical to `agents/critique.md:5`.
- 9 dimensions enumerated — identical names and order as `agents/critique.md` Dimension table.
- Citation framework table — verbatim from `agents/critique.md` (the frameworks apply identically to code; the substitution is "design" → "code diff" in the prose body, NOT in the framework names).
- Specificity rule — `path/to/file.py:line` per `agents/critique.md`'s specificity discipline.

A new `tests/methodology/test_code_review_agent_parity.py` is OUT OF SCOPE for slice-060 (would over-engineer; the `test_agent_md_contains_nine_dimensions_against_code` test sufficiently pins the parity). Deferred per "out of scope" — if drift between the two agents emerges in practice, slice-061/062 can add the parity audit.

## 9 dimensions reframed for code

Per /critique M1: the dimensions transfer from `agents/critique.md` (design review) to `agents/code-review.md` (code review) with these explicit substitutions. The framework citations transfer **verbatim** (Wiegers, Cockburn, Hendrickson, Fowler, Beck, Patton, Newman, Fielding, OWASP, McGraw, Sommerville, ISO/IEC/IEEE 42010, Kiczales) — the frameworks apply identically; only the input artifact and failure-mode-class examples change. The agent prose at `agents/code-review.md` MUST include these reframings; `test_agent_md_contains_nine_dimensions_against_code` is content-bearing (slice-051 / slice-037 M-add-1 discipline — substring assertions on the reframed prose, not just dimension names).

| # | Dim | Input artifact | Failure-mode class examples (code-specific) |
|---|-----|----------------|---------------------------------------------|
| 1 | Unfounded assumptions | code diff (changed `.py` / `.md` / `.yaml`) | A function comment claims "X is handled" but the code path doesn't handle X; a docstring example diverges from the regex/parser/keyword-list in the implementation file (slice-006 Dim 1 example transfers verbatim — docstring drift catches differently in code than in design.md); an error handler's `except` clause assumes a specific exception type without try-narrowing |
| 2 | Missing edge cases | code paths in the diff | Empty/null input not handled at the call site; load handling at 10× volume; network failure with no retry/timeout; concurrent invocation race; permission-denied branch; offline-mode degradation; platform-specific (iOS HEIC, Windows path separators, browser quirks) |
| 3 | Over-engineering | code structure in the diff | Single-impl interface ("for future flexibility"); single-product factory; plugin system with one plugin; configuration flag never overridden in any caller; dead parameter / unreachable branch; speculative generality (Fowler) |
| 4 | Under-engineering | mission-brief AC ↔ code traceability | An AC claims behavior X but no code path delivers it; a must-not-defer item has no implementing code; the slice's diff doesn't actually exercise the layer the mission-brief WS-1 plan claims |
| 5 | Contract gaps | new/changed function signatures + endpoints | Missing input validation at a public interface; error semantics undefined (function returns `None` on N different failure paths with no distinction); idempotency not specified for mutating operations; type hints absent on a public API; docstring absent on a non-trivial public function |
| 6 | Security | new code paths handling input / authz / secrets | OWASP Top 10 applied directly — input validation absent, IDOR (function accepts an ID without checking caller scope), injection point (raw SQL / shell), secret in a log statement, secret in a default-value, hardcoded credential in a test fixture not in the allow-list. McGraw "defense in depth": authz checked only at one layer when two layers would be cheap |
| 7 | Drift from vault | code vs design.md / ADRs / mission-brief | Code contradicts a design.md "Components touched" claim (a file is modified that design.md said wouldn't be touched, or vice-versa); code introduces a symbol absent from graphify-out/graph.json post-rebuild (suggests a stale graph or a phantom import); code implements behavior the mission-brief's "Out of scope" said is deferred to a later slice; ADR claims reversibility-cheap but the code has 3+ external consumers added making it expensive-to-revert |
| 8 | Web-known issues | new dependencies, platform APIs, framework calls | Per Critic prompt's Dim 8 (live web): official platform docs > GitHub closed-as-wontfix > recent Stack Overflow. Examples: `subprocess.run(..., shell=True)` known-bad pattern; deprecated `asyncio.get_event_loop()` post-3.10; Windows `Path.resolve()` UNC-path edge cases. **Requires WebSearch** (per agent tools); without it the agent must state "Skipped — WebSearch unavailable" under this dimension |
| 9 | Cross-cutting conformance | the slice's adherence to in-house methodology disciplines | Sub-clauses that apply to **code-as-artifact** (in-scope for `/code-review`): **RSAD-1** (recursive self-application — does the new code survive its own discipline?); **APED-1** (audit-parse-rule empirical execution — does the new audit-tool actually run against the cited real artifact?); **EOL-DRIFT-1** (any new byte-equality compare must be CRLF→LF normalized). Sub-clauses that DO NOT apply to code-as-artifact (out-of-scope for `/code-review`, handled by design `/critique`): **FBCD-1**, **SCPD-1**, **TPHD-1**, **PTFCD-1 sub-mode (a)** (phantom-test-path-in-DESIGN.md is design-meta), **PTFFD-1** (test-function-existence-in-design-prose is design-meta), **MEPD-1** — all properties of mission-brief / design / catalog row prose, not code. **Clarification per /critique-review m-add-1** (Sommerville inspection-coverage-matrix discipline): a **phantom-import in actual `.py` code under review** (e.g., a new `tests/<...>.py` module the slice writes which `import`s a non-existent symbol; a `tools/<...>.py` module that imports a renamed name) IS code-as-artifact and IS in-scope for `/code-review` — caught under Dim 1 (Unfounded assumptions — the import claims a symbol exists that doesn't) or Dim 5 (Contract gaps — the importing module has a broken contract dependency), NOT under Dim 9's PTFCD-class out-of-scope clause |

`agents/code-review.md` MUST include a footer `## Dimensions checked` listing all 9 dimensions and either findings or `none — <reason>`. The `test_agent_md_contains_nine_dimensions_against_code` test asserts: (a) each dimension name appears as a heading, AND (b) the design→code substitution prose is present (specific substrings from the table above — at minimum "code diff" / "code paths in the diff" / "mission-brief AC ↔ code traceability" / "RSAD-1 (recursive self-application")). Without (b), the test is tautologically-green per slice-037 M-add-1.

## Build-phase sequence

Per /critique M2: the slice-060 walking-skeleton self-dogfood has a phase-ordering dependency the design must enumerate. The PCA-1 / CRP-1 bootstrap precedents (slice-026, slice-027) had simpler shapes — they did NOT require a per-slice artifact write. Slice-060 does. The canonical build sequence:

| Phase | Action | Verification |
|-------|--------|--------------|
| **A** | Author `skills/code-review/SKILL.md` + `agents/code-review.md` in-repo; author all new tests in WRITTEN-FAILING state; apply all 6 hardcoded "8" → "9" edits (B5); apply `_CANONICAL_CHAIN` extension; apply `_CANONICAL_SKILLS` / `_CANONICAL_AGENTS` extension; apply `plugin.yaml` + `VERSION` + `pyproject.toml` + `methodology-changelog.md` v0.64.0 + ADR-059. Create `tests/agents/__init__.py` + `tests/skills/code_review/__init__.py`. | `git status` shows the diff; tests are collectible (no PTFCD-1 phantom paths); PCA-1 audit exits 0 |
| **B** | Forward-sync to installed copies. **Full enumeration** (per /critique-review M-add-1 — slice-049/051 OSDG-1 family-add lineage; Fowler refactoring discipline "propagate to all replicas in lock-step"; the original Phase B enumerated only the NEW skill+agent and missed the EDITED in-loop chain SKILL.md files that have their own drift guards): `cp skills/code-review/SKILL.md ~/.claude/skills/code-review/SKILL.md`; `cp agents/code-review.md ~/.claude/agents/code-review.md`; **`cp skills/build-slice/SKILL.md ~/.claude/skills/build-slice/SKILL.md`** (edited: `successor:` flipped to `/code-review`); **`cp skills/validate-slice/SKILL.md ~/.claude/skills/validate-slice/SKILL.md`** (edited: `predecessor:` flipped to `/code-review`); `cp methodology-changelog.md ~/.claude/methodology-changelog.md`; `cp VERSION ~/.claude/ai-sdlc-VERSION`; `pip install --upgrade .` (for TVFS-1 leg). | OSDG-1 + CAD-1 drift tests would PASS at this point (including `test_build_slice_skill_drift.py` + `test_validate_slice_skill_drift.py` if present + the parametrized `test_pipeline_position_block_drift.py` over all 9 `_CANONICAL_CHAIN` entries); MCFS-1 + AVFS-1 + TVFS-1 + PVFS-1 exit 0 |
| **C** | Invoke `/code-review` against slice-060 itself via the Skill tool. The skill spawns the new code-review agent (`subagent_type: "code-review"`); the agent reads the slice's mission-brief + design + ADR-059 + the slice diff; writes findings to `architecture/slices/slice-060-add-code-review-skill/code-review.md`. | The file `architecture/slices/slice-060-add-code-review-skill/code-review.md` exists with ≥1 finding (substring `### B` / `### M` / `Blockers` / `Majors`); load-bearing RSAD-1 self-application proof |
| **D** | Run TF-1 strict-pre-finish: `$PY -m tools.test_first_audit architecture/slices/slice-060-add-code-review-skill --strict-pre-finish`. All 17 TF-1 rows must be PASSING (including the artifact-existence check at row 3 which Phase C just satisfied). | All TF-1 rows PASSING; `test_first_audit` exits 0 |
| **E** | Run the full `/build-slice` Step 6 audit suite (all 16+ audits). PCA-1 bootstrap-discharges against the 9-entry chain. PMI-1 (5-leg forward-sync). BCI-1, MCFS-1, AVFS-1, TVFS-1, PVFS-1, STP-1, OSDG-1 family, CAD-1, INST-1, SRSC-1 — all exit 0. | Pre-finish gate clean; slice declares SHIPPED |

If Phase C is skipped or runs before Phase B (forward-sync), the self-dogfood test at row 3 will FAIL because either (a) the installed skill+agent don't exist yet, OR (b) `code-review.md` artifact doesn't exist. The must-not-defer item enforces the Phase B → Phase C → Phase D ordering.

## Shippability catalog row #60 design

Per /critique M5 + SCPD-1 sub-mode (b) proactive-application + PTFCD-1 + PTFFD-1 path/function existence pre-engineered: row #60 is enumerated here at design time, not guessed at build time.

**Row identity**: `60 | slice-060-add-code-review-skill | <description prose> | <Command cell> | <budget> | <Machine-cmd cell>`

**BCR-1 traceability axis** (CRSI-1 lineage anchors): the description prose cites CRSI-1, OSDG-1 family-add (skill+agent drift guard), CAD-1 family-add (agent drift guard), PCA-1 chain extension (8→9), 5-part PMI-1 atomic bump (VERSION + plugin.yaml + pyproject.toml + ai-sdlc-VERSION + methodology-changelog).

**Regression-tripwire description**: row #60 catches silent breakage of (a) the code-review skill+agent forward-sync (OSDG-1 / CAD-1 family-add); (b) the v0.64.0 entry-pin (META-1 enforcing-assertion); (c) the PCA-1 canonical chain 9-entry extension; (d) the `_CANONICAL_SKILLS` + `_CANONICAL_AGENTS` enumeration (INST-1); (e) the self-dogfood artifact at `architecture/slices/slice-060-add-code-review-skill/code-review.md` existing.

**Command-cell pytest selectors** (6 selectors per /critique-review M-add-2 paired propagation pin; PTFCD-1 verifies each `tests/<...>.py` file exists at /validate-slice Step 5.5; PTFFD-1 verifies each `::<fn>` function exists):
- `tests/methodology/test_code_review_skill_drift.py::test_in_repo_and_installed_code_review_skill_md_are_content_equal`
- `tests/methodology/test_code_review_agent_drift.py::test_in_repo_and_installed_code_review_agent_md_are_content_equal`
- `tests/methodology/test_methodology_changelog.py::test_v_0_64_0_crsi_1_entry_present_in_repo`
- `tests/methodology/test_methodology_changelog.py::test_v_0_64_0_crsi_1_shippability_consumer_propagation`
- `tests/methodology/test_pipeline_chain_audit.py::test_canonical_chain_includes_code_review_edge`
- `tests/skills/code_review/test_code_review_skill.py::test_self_dogfood_produces_code_review_md_on_slice_060`

**Expected runtime**: <3s (per <10s constraint per row; 6 selectors are all small unit-class or file-existence checks).

**Pipe-escape discipline (BC-PROJ-7 from slice-044)**: row #60's prose description must be pipe-free OR escape pipes as `\|` to avoid SCMD-1 6-column schema misalignment. Author the row at the LAST step of the build sequence (after all selectors are confirmed to exist), per the BC-PROJ-7 "sequence both LAST + read the SRSC-1 runner output" discipline.

The `test_code_review_dogfood_row_runs_clean` test at TF-1 row 16 asserts: (a) row #60 exists in `architecture/shippability.md`; (b) the row's Machine-cmd cell, when passed through SCMD-1 `_segments()` + executed via `tools.shippability_runner`, exits 0; (c) all 5 selectors resolve to existing files+functions per PTFCD-1 + PTFFD-1.
