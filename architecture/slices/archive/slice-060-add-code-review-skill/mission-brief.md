# Slice 060: add-code-review-skill

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: none (gap-closure; no open risk tracks the missing in-loop code-review surface, but the gap is corroborated by AI-bloat signatures in `diagnose-out/backlog.md` — SC-017 / SC-022 / SC-025 — that today are only caught by heavyweight whole-repo `/diagnose`)
**Test-first**: true
**Walking-skeleton**: true
**Exploratory-charter**: false

## Intent

Insert a new in-loop step `/code-review` between `/build-slice` and `/validate-slice` as a **walking-skeleton**: every architectural layer exercised end-to-end (skill orchestrator / agent worker / PCA-1 chain edge / self-hosting drift guards / shippability catalog row / methodology surface) but **findings advisory only** — no AI-bloat passes yet, no TRI-1 triage gate yet, no verdict-driven block on `/validate-slice`. This closes the structural gap surfaced via `/query-design`: the pipeline reviews **design pre-code** (`/critique` + `/critique-review`) and **behavior/structure post-code** (`/validate-slice` + Step 6 audits), but has no **per-slice adversarial review of the just-written code**. Slice-061 follows with AI-bloat passes (multi-impls / half-wired / stale-scaffolding / session-break); slice-062 follows with TRI-1 triage gate + verdict-driven block.

## Acceptance criteria

1. **Skill end-to-end runtime + Pipeline-position block**: `skills/code-review/SKILL.md` exists and carries a well-formed `## Pipeline position` block declaring `predecessor: /build-slice`, `successor: /validate-slice`, `auto-advance: true`. On invocation the skill spawns an Agent via the Agent tool with `subagent_type: "code-review"`, passes the slice's mission-brief.md + design.md + the slice's code diff vs the default branch, and writes the agent's findings to `architecture/slices/slice-NNN-<name>/code-review.md`. Walking-skeleton verification: invoking `/code-review` against slice-060 itself produces `architecture/slices/slice-060-add-code-review-skill/code-review.md` with non-empty findings.

2. **Adversarial code-review agent — 9 dimensions vs CODE**: `agents/code-review.md` exists carrying an adversarial Critic-stance prompt applying the 9 `/critique` dimensions (unfounded assumptions, missing edge cases, over-engineering, under-engineering, contract gaps, security, drift from vault, web-known issues, cross-cutting conformance) to the slice's **code diff** (not design). Agent tools are `Read, Glob, Grep, Bash, WebSearch` (read-only — `Write`, `Edit`, `NotebookEdit` forbidden; matches `agents/critique.md` verbatim for CSP-1 parity — Dim 8 requires WebSearch). Findings reference `path/to/file.py:line` (specificity rule inherited verbatim from `agents/critique.md`). Output structure mirrors `critique.md` (blockers/majors/minors with Builder draft dispositions stubbed for slice-062's TRI-1 extension).

3. **PCA-1 canonical chain extended**: `tools/pipeline_chain_audit.py`'s `_CANONICAL_CHAIN` dict is extended — `/build-slice`'s canonical successor flips from `/validate-slice` to `/code-review`, and a new `/code-review → /validate-slice` (auto-advance: true) entry is added. `skills/build-slice/SKILL.md`'s `## Pipeline position` block updates `successor:` to `/code-review`. `skills/validate-slice/SKILL.md`'s `## Pipeline position` block updates `predecessor:` to `/code-review`. PCA-1 audit (`$PY -m tools.pipeline_chain_audit`) exits 0 on the full post-slice-060 repo.

4. **Self-hosting drift guards extended** (CAD-1 + OSDG-1 + PMI-1 + INST-1): `plugin.yaml` enumerates `skills/code-review/` + `agents/code-review.md` + (if any new `tools/*.py` are introduced) the tool path; `tools/install_audit.py`'s `_CANONICAL_SKILLS` and `_CANONICAL_AGENTS` tuples include `code-review`; `tests/methodology/test_code_review_skill_drift.py` exists, reuses `tests/skill_drift_equality.py::assert_md_forward_synced` (EOL-agnostic per EOL-DRIFT-1 / ADR-033), and pins in-repo↔installed equality for the new skill; `tests/methodology/test_code_review_agent_drift.py` (or the existing `tools/critique_agent_drift_audit.py` extended) pins the same equality for the new agent; all four audits (`$PY -m tools.plugin_manifest_audit`, `$PY -m tools.install_audit`, `$PY -m pytest tests/methodology/test_code_review_skill_drift.py tests/methodology/test_code_review_agent_drift.py -q`) exit 0.

5. **Methodology surface change + shippability catalog row**: **5-part** PMI-1 atomic version bump 0.63.0 → 0.64.0 (VERSION + plugin.yaml.version + **pyproject.toml `[project].version`** + installed `~/.claude/ai-sdlc-VERSION` + installed `~/.claude/methodology-changelog.md`); `methodology-changelog.md` gains a `## v0.64.0 — <YYYY-MM-DD>` entry referencing new RULE-ID **CRSI-1** (Code-Review Skill Insertion) + ADR-059 authored under `architecture/decisions/`; `architecture/shippability.md` gains a new row asserting the walking-skeleton self-dogfood (Machine-cmd column SCMD-1 + PTFCD-1 + SRSC-1 clean); PVFS-1, AVFS-1, MCFS-1, BCI-1, STP-1 all exit 0.

## Test-first plan

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING through the slice lifecycle. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish`.

**Prerequisite directory creates** (per /critique B3, slice-027-B1 / slice-037 N=2 phantom-path lineage): the following `__init__.py` files MUST be created BEFORE any TF-1 row tests are collectible by pytest. Plan-mode `ls`/stat of each cited new test directory is the FIRST plan-mode action at /build-slice:
- `tests/agents/__init__.py` (NEW; empty or one-line docstring per `tests/methodology/__init__.py` pattern)
- `tests/skills/code_review/__init__.py` (NEW; empty)

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/skills/code_review/test_code_review_skill.py | test_skill_md_pipeline_position_block_present | PASSING |
| 1 | unit | tests/skills/code_review/test_code_review_skill.py | test_skill_md_successor_is_validate_slice | PASSING |
| 1 | unit | tests/skills/code_review/test_code_review_skill.py | test_self_dogfood_produces_code_review_md_on_slice_060 | PASSING |
| 2 | unit | tests/agents/test_code_review_agent.py | test_agent_md_contains_nine_dimensions_against_code | PASSING |
| 2 | unit | tests/agents/test_code_review_agent.py | test_agent_md_read_only_tools_pinned | PASSING |
| 2 | unit | tests/agents/test_code_review_agent.py | test_agent_md_specificity_rule_path_line_present | PASSING |
| 3 | unit | tests/methodology/test_pipeline_chain_audit.py | test_canonical_chain_includes_code_review_edge | PASSING |
| 3 | integration | tests/methodology/test_pipeline_chain_audit.py | test_audit_exits_zero_on_post_slice_060_repo | PASSING |
| 3 | unit | tests/methodology/test_pipeline_chain_audit.py | test_clean_chain_exits_zero | PASSING |
| 3 | unit | tests/methodology/test_pipeline_position_block_drift.py | test_pipeline_position_block_byte_equal_in_repo_vs_installed | PASSING |
| 3 | unit | tests/methodology/test_build_slice_skill.py | test_build_slice_successor_is_code_review | PASSING |
| 3 | unit | tests/methodology/test_validate_slice_skill.py | test_validate_slice_predecessor_is_code_review | PASSING |
| 4 | unit | tests/methodology/test_code_review_skill_drift.py | test_in_repo_and_installed_code_review_skill_md_are_content_equal | PASSING |
| 4 | unit | tests/methodology/test_code_review_agent_drift.py | test_in_repo_and_installed_code_review_agent_md_are_content_equal | PASSING |
| 4 | unit | tests/methodology/test_plugin_manifest_audit.py | test_plugin_yaml_enumerates_code_review_skill_and_agent | PASSING |
| 4 | unit | tests/methodology/test_install_audit.py | test_canonical_skills_and_agents_include_code_review | PASSING |
| 5 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_64_0_crsi_1_entry_present_in_repo | PASSING |
| 5 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_64_0_crsi_1_shippability_consumer_propagation | PASSING |
| 5 | unit | tests/methodology/test_shippability_runner_segment_contract.py | test_code_review_dogfood_row_runs_clean | PASSING |

**TF-1 row 9 + row 10 are UPDATE rows** (per /critique B5, SCPD-1 sub-mode (b)): `test_clean_chain_exits_zero` updates `assert len(result.skills_checked) == 8` → `== 9`; `test_pipeline_position_block_byte_equal_in_repo_vs_installed` updates docstring + message strings to "9 covered skills". Both PRE-EXIST on master; the TF-1 plan tracks the EDIT, not creation. Per TPHD-1 sub-mode (a), this harmonization happens in this /critique fix block.

**TF-1 row 3 (`test_self_dogfood_produces_code_review_md_on_slice_060`) reclassified `integration` → `unit`** (per /critique M2): the test is an artifact-existence-and-content check (reads `architecture/slices/slice-060-add-code-review-skill/code-review.md` at fixed path; asserts file presence + ≥1 finding via substring like `Blockers` / `Majors` / `### B` / `### M`). It does NOT drive an LLM agent from pytest; the `/code-review` self-invocation against slice-060 is a manual build-step (Build-phase C — see design.md "Build-phase sequence").

## Architectural layers exercised

Walking-skeleton verification: each architectural layer must be EXERCISED at runtime, not just unit-tested in isolation. `/validate-slice` Step 5c runs `tools/walking_skeleton_audit.py --strict-pre-finish`.

| # | Layer | Component | Verification | Status |
|---|-------|-----------|--------------|--------|
| 1 | Skill (orchestrator) | skills/code-review/SKILL.md | invoking `/code-review` reaches Step 1 prerequisite check (active slice found, mission-brief.md read) | EXERCISED |
| 2 | Agent (worker) | agents/code-review.md | Agent-tool spawn with `subagent_type: "code-review"` succeeds; agent returns findings text | EXERCISED |
| 3 | Pipeline chain | tools/pipeline_chain_audit.py + /build-slice + /validate-slice SKILL.md | PCA-1 audit exits 0 on the new shape; `_CANONICAL_CHAIN` contains the code-review edge | EXERCISED |
| 4 | Drift guards | CAD-1 (agent) + OSDG-1 (skill) + PMI-1 (plugin.yaml) + INST-1 (install_audit) | all four audits exit 0 with code-review enrolled | EXERCISED |
| 5 | Catalog + methodology surface | architecture/shippability.md (new row) + methodology-changelog.md (## v0.64.0) + architecture/decisions/ADR-NNN | SRSC-1 runner passes the new row; META-1 changelog test passes; ADR-NNN exists with `status: accepted` | EXERCISED |
| 6 | End-to-end self-dogfood | full chain on slice-060 itself | `architecture/slices/slice-060-add-code-review-skill/code-review.md` artifact created with non-empty findings | EXERCISED |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Skill end-to-end runtime + Pipeline-position block | Run `$PY -m pytest tests/skills/code_review/test_code_review_skill.py -q`; expect 3/3 PASS. Manually invoke `/code-review` against slice-060 itself; observe `architecture/slices/slice-060-add-code-review-skill/code-review.md` written with ≥1 finding |
| 2 | Adversarial code-review agent (9 dims vs CODE) | Run `$PY -m pytest tests/agents/test_code_review_agent.py -q`; expect 3/3 PASS. Visual inspection of agent output on the slice-060 self-dogfood: findings cite `path/to/file:line`, all 9 dimensions are present in the "Dimensions checked" footer |
| 3 | PCA-1 canonical chain extended | Run `$PY -m tools.pipeline_chain_audit`; expect exit 0. Run `$PY -m pytest tests/methodology/test_pipeline_chain_audit.py tests/methodology/test_build_slice_skill.py tests/methodology/test_validate_slice_skill.py -q`; expect all PASS |
| 4 | Self-hosting drift guards extended | Run `$PY -m tools.plugin_manifest_audit && $PY -m tools.install_audit && $PY -m pytest tests/methodology/test_code_review_skill_drift.py tests/methodology/test_code_review_agent_drift.py tests/methodology/test_plugin_manifest_audit.py tests/methodology/test_install_audit.py -q`; expect every step exit 0 |
| 5 | Methodology surface + shippability row | Run the 4-part PMI-1 atomic bump command sequence; then `$PY -m tools.shippability_runner architecture/shippability.md`, `$PY -m tools.methodology_changelog_forward_sync`, `$PY -m tools.ai_sdlc_version_forward_sync`, `$PY -m tools.build_checks_integrity`, `$PY -m tools.state_transition_pin_audit`; expect every step exit 0 |

## Must-not-defer

- [ ] Adversarial agent prompt includes ALL 9 critique dimensions applied to CODE (no abbreviated subset; reuse the verbatim dimension wording from `agents/critique.md` with the design→code substitution)
- [ ] Agent tools are `Read, Glob, Grep, Bash, WebSearch` (matches `agents/critique.md` verbatim for CSP-1 parity — Dim 8 requires WebSearch) — `Write`, `Edit`, `NotebookEdit` forbidden — pinned by `test_agent_md_read_only_tools_pinned` (positive substring assertion on the literal 5-tool list AND negative substring assertions on each of `Write`, `Edit`, `NotebookEdit` per slice-007 M2 + slice-053 M-add-4 precedent)
- [ ] Empty-diff handling: skill returns clean "no code changes detected — nothing to review" rather than crashing or spawning the agent against an empty diff (operational footgun if `/code-review` runs on a slice that authored only vault markdown)
- [ ] PCA-1 bootstrap-discharge clause (mirrors CRP-1 slice-026 / PCA-1 slice-027 precedent): slice-060 itself authors the new chain; the PCA-1 audit run at slice-060's own Step 6 MUST exit 0 against the post-slice-060 chain shape. Document the bootstrap in the slice's `design.md` + the methodology-changelog v0.64.0 entry
- [ ] CAD-1 + OSDG-1 EOL-agnostic comparison preserved (`tests/skill_drift_equality.py::assert_md_forward_synced` reused verbatim — do NOT introduce a new byte-equality comparator; R-5 retirement / EOL-DRIFT-1 / ADR-033)
- [ ] Findings cite `path/to/file.py:line` — specificity rule from `agents/critique.md` inherited verbatim; pinned by `test_agent_md_specificity_rule_path_line_present`
- [ ] No silent default-off: a malformed `## Pipeline position` block in `/code-review` SKILL.md MUST raise PCA-1 `malformed-block` (Important, exit 1) — the R-7 footgun class. Verified by adding `/code-review` to the existing `_REQUIRED_FIELDS` coverage in PCA-1 audit
- [ ] Walking-skeleton end-to-end self-dogfood MUST run on slice-060 itself before declaring done — `architecture/slices/slice-060-add-code-review-skill/code-review.md` exists with non-empty findings (BC-PROJ-4 audit-vs-real-artifact discipline)
- [ ] **Build-phase sequence respected** (per /critique M2): the `/code-review` self-invocation against slice-060 happens BETWEEN the forward-sync step (Phase B) and the TF-1 strict-pre-finish pytest run (Phase D); otherwise `test_self_dogfood_produces_code_review_md_on_slice_060` stays PENDING and Step 6 fails. See design.md "## Build-phase sequence" for the canonical A→B→C→D→E ordering.

## Out of scope

- **AI-bloat passes** (multi-impls / half-wired modules / stale scaffolding / session-break inconsistency) — port relevant `/diagnose` pass templates to scope-on-diff. **Deferred to slice-061**.
- **TRI-1-style user triage gate** (mirroring `/critique` Step 4.5 — Builder draft dispositions → user ratification → final verdict). **Deferred to slice-062**.
- **Verdict-driven block on `/validate-slice`** — slice-060 findings are advisory; `/validate-slice` proceeds unconditionally. **Deferred to slice-062**.
- **`/code-review --force` flag, risk-tier-based skip, mandatory-trigger detection** — defer until the skeleton proves value; slice-060 always runs (no skip path).
- **`/critic-calibrate` extension to track code-review accuracy** — defer to N≥10 slices of operation per the slice-037 precedent ("don't add Critic dimensions for build-time-reachable classes; the gates work — accumulate evidence first").
- **Migration of past slices to retroactively run `/code-review`** — slice-060 onward only; archived slices unaffected.
- **Changes to `/critique` or `/critique-review`** — those review DESIGN; `/code-review` reviews CODE. Separate concerns, separate agents. No edits to the design-Critic surfaces.

## Dependencies

- Prior slices:
  - [[slice-007]] — CAD-1 Critic-agent content-equality (structural pattern source for the new `code-review` agent drift guard)
  - [[slice-010]] — OSDG-1 / mini-CAD skill-drift content-equality (structural pattern source for the new `/code-review` skill drift guard)
  - [[slice-027]] — PCA-1 pipeline-chain audit (the audit being extended; bootstrap-discharge precedent)
  - [[slice-049]] / [[slice-051]] — OSDG-1 member-addition lineage (the canonical 4-surface budget: equality test + content-bearing v-entry-pin + prose-pin enumeration + collected test, per slice-051 lessons-learned)
- Vault refs:
  - [[agents/critique.md]] — adversarial prompt structural template (9 dimensions, specificity rule, output format)
  - [[skills/critique/SKILL.md]] — orchestration structural template (Agent-tool spawn pattern, write-findings pattern, Pipeline-position block)
  - [[skills/critique-review/SKILL.md]] — dual-review pattern reference (note: slice-060 does NOT introduce a second-pass code-review meta-Critic; that's deferable to slice-062 alongside TRI-1)
- Risk register: none retired (gap-closure not risk retirement). Discovery: this slice may surface latent classes once active — track via `/reflect`.

## Mid-slice smoke gate

At ~50% of build (after authoring `skills/code-review/SKILL.md` + `agents/code-review.md` + extending `tools/pipeline_chain_audit.py` + writing the failing tests):

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m tools.pipeline_chain_audit
& $PY -m tools.plugin_manifest_audit
& $PY -m pytest tests/skills/code_review/ tests/agents/test_code_review_agent.py tests/methodology/test_code_review_skill_drift.py tests/methodology/test_code_review_agent_drift.py tests/methodology/test_pipeline_chain_audit.py -q
```

Expected: PCA-1 + PMI-1 exit 0; all newly-authored tests PASS (post-implementation; pre-implementation they are WRITTEN-FAILING per TF-1).

Then manually invoke `/code-review` via the Skill tool against slice-060 itself; confirm `architecture/slices/slice-060-add-code-review-skill/code-review.md` is created with non-empty findings (walking-skeleton layer 6).

If smoke fails: STOP, diagnose, don't continue. Often the right move is to revise the plan (per `/build-slice` Step 5).

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed (all 8 items above)
- [ ] `/drift-check` passes (vault and code aligned)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints / `console.log`s
- [ ] Standard `/build-slice` Step 6 audit suite all exit 0 (BC-1, PCA-1, BRANCH-1, UTF8-STDOUT-1, CRP-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1, TF-1, WS-1, WIRE-1, LINT-MOCK-1/2/3, PMI-1)
- [ ] Walking-skeleton self-dogfood verified: `architecture/slices/slice-060-add-code-review-skill/code-review.md` exists with ≥1 finding from the new code-review agent
