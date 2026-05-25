# Design: Slice 063 add-build-slice-new-agent-warning

**Date**: 2026-05-23
**Mode**: Standard

## What's new

This slice mints **NAW-1 (New-Agent Warning)** — see [[ADR-061]] for the full decision record (options, rationale, exit-contract semantics, WARN message template, version-bump shape).

Concretely, the slice introduces:

1. **A new standalone audit tool** `tools/new_agent_warning_audit.py` — structurally clones the AVFS-1/TVFS-1 shape (CLI: `--root` / `--check` / `--json`; `CheckResult` dataclass; `tools._stdout` UTF-8 convention; `main(argv: list[str] | None = None) -> int` signature). Read mechanism is a **union of three sources** covering all states a new agent file can occupy at `/build-slice` Step 6 (B1 critique fix; `git diff <base>...HEAD` alone is commit-vs-commit only per `git-scm.com/docs/git-diff` and excludes the uncommitted working-tree where slice work lives until `/commit-slice` runs): (i) `git diff --name-only --diff-filter=A {base} -- 'agents/*.md'` for modified+staged-but-uncommitted additions (working-tree-vs-base; no `..HEAD` suffix → working-tree-aware); (ii) `git ls-files --others --exclude-standard -- 'agents/*.md'` for untracked-new agent files; (iii) `git diff --name-only --diff-filter=A {base}...HEAD -- 'agents/*.md'` for already-committed-in-branch agents (covers any `/build-slice` Step 4 intermediate commits, e.g., worktree-add path). Sets are unioned and deduplicated by path. Exit contract is **binary** (0 / 2), not tri-state — there is no "drift" branch for a discovery gate.
2. **A new pytest regression module** `tests/methodology/test_new_agent_warning_audit.py` — 7 unit tests covering the audit's documented states (clean / warn-via-untracked-source / warn-via-staged-source / negative-contrast) + WARN-message anchor pins + a seam-driven self-application test (uses `added_files_resolver` injection seam per slice-059 TVFS-1 precedent, NOT live `git diff` against slice-063's branch; regression-stable across slice-064+).
3. **`/build-slice` Step 6 wiring** — extend `skills/build-slice/SKILL.md` Step 6 checklist + prose with the new NAW-1 sub-section (after TVFS-1).
4. **R-18 retirement** in `architecture/risk-register.md` (`**Status**: mitigating` → `retired` + retirement paragraph citing NAW-1).
5. **BC-PROJ-9 multi-surface fan-out** (slice-059 precedent on the 5-inventory completeness; slice-050 AVFS-1 tool-addition precedent on the 4-inventory subset) for the new `tools/*.py` module: `plugin.yaml` (+1 tool path), `tools/install_audit.py` `_CANONICAL_TOOLS` (+1 entry, alphabetic insert), `tests/methodology/test_utf8_stdout_regression.py` `_ROOT_ONLY_TOOLS` (+1 entry), `INSTALL.md` tool-count literal `27` → `28` at L22 + L166, `architecture/shippability.md` row #63 (the slice-059 5-inventory enumeration).
6. **5-part PMI-1 atomic bump** `0.65.0` → `0.66.0` — the 5 canonical version-bearing legs per ADR-061 L85 + slice-060 v0.64.0 + slice-062 v0.65.0 precedent: (1) `VERSION`; (2) `plugin.yaml.version` (PMI-1); (3) `pyproject.toml [project].version` (PVFS-1); (4) `## v0.66.0` methodology-changelog header; (5) installed `~/.claude/ai-sdlc-VERSION` (AVFS-1 forward-sync). **Plus two separate post-bump forward-sync obligations** (not PMI-1 atomic-bump legs; bucketed under BC-PROJ-9 fan-out): installed `~/.claude/methodology-changelog.md` (MCFS-1 forward-sync via `cp`) + installed venv `ai-sdlc-tools` `0.66.0` (TVFS-1 forward-sync via `$PY -m pip install --upgrade .`). Meta-Critic M-add-1 critique fix — keeps the 5-leg count authoritative across mission-brief L56 + design.md + ADR-061 L85 + the v0.66.0 entry-pin test's `"5-part PMI-1 atomic bump"` anchor.
7. **Shippability row #63** citing BOTH `NAW-1` AND `R-18` per BCR-1 traceability axis (slice-054 first-dogfood precedent applied; this slice is risk-register-driven, not BCR-1-backlog-driven — zero `**Closes:** SC-NNN` sentinels).
8. **Methodology-changelog `## v0.66.0` entry** — pinned by paired `tests/methodology/test_methodology_changelog.py::test_v_0_66_0_naw_1_entry_present_in_repo` + `::test_v_0_66_0_naw_1_shippability_consumer_propagation` (BC-PROJ-10 paired-pin schema). **Anchor list explicitly enumerated at design-time per EPGD-1** (mirrors slice-060 v0.64.0 + slice-062 v0.65.0 entry-pin anchor sets at `tests/methodology/test_methodology_changelog.py:4060-4109` — the META-1 enforcing-assertion at `test_methodology_changelog.py:136` REQUIRES `"Rule reference"` in each `## vN.NN.0` section): the `entry_present_in_repo` test asserts substring presence of **8 anchors** — (1) `"## v0.66.0"` header literal (slice-060 + slice-062 precedent header anchor; meta-Critic M-add-2 critique fix); (2) `"NAW-1"`; (3) `"ADR-061"`; (4) `"New-Agent Warning"`; (5) `"mints a new rule"`; (6) `"supersedes nothing"`; (7) `"Rule reference"` literal (META-1 mandatory enforcing-assertion; meta-Critic M-add-2 critique fix); (8) `"5-part PMI-1 atomic bump"` (NOTE: 5-part, NOT 4-part — slice-063 ships a NEW `tools/*.py` so PMI-1 leg count matches slice-060 / slice-062 5-part precedent, not the slice-059 4-part bump that had no new tool; the anchor literal MUST be `"5-part"` to avoid the slice-062 M-add-3 stale-carry class). The `shippability_consumer_propagation` test asserts row #63 cites BOTH `"NAW-1"` AND `"R-18"` AND `"ADR-061"` (BCR-1 traceability axis per slice-054 first-dogfood + slice-056 row-#56 / slice-062 row-#62 precedents).

## What's reused

- [[ADR-058]] / `tools/ai_sdlc_tools_version_forward_sync.py` (TVFS-1, slice-059) — structural template for the new tool's CLI + `CheckResult` dataclass + UTF-8 convention + `main()` argv contract.
- [[ADR-052]] / `tools/ai_sdlc_version_forward_sync.py` (AVFS-1, slice-050) — 2-point/1-point wiring shape decision precedent (TVFS-1 took 2-point AVFS-1 parity; NAW-1 takes 1-point because the read has no `/reflect` Step 5b parallel state — see [[ADR-061]] §Decision).
- `tools/branch_workflow_audit.py` (BRANCH-1, slice-027) — default-branch resolution logic (`git symbolic-ref refs/remotes/origin/HEAD` → `git config init.defaultBranch` → `None` ⇒ NAW-1 returns `usage` exit 2 per BRANCH-1's `default-branch-unresolvable` semantics at `tools/branch_workflow_audit.py:127-146` + L329-341; `_resolve_default_branch` does NOT have a "main" fallback in the implementation — Critic M3 critique fix).
- `tools/_stdout.py` (UTF8-STDOUT-1, slice-022) — `_stdout.reconfigure_stdout_utf8()` for first-statement-of-`main()`.
- `tools/install_audit.py` `_CANONICAL_TOOLS` (PMI-1 / INST-1 inventory) — alphabetic-insert pattern.
- `tests/methodology/test_utf8_stdout_regression.py` `_ROOT_ONLY_TOOLS` (UTF8-STDOUT-1 parametrize harness) — append-pattern.
- `tests/methodology/test_methodology_changelog.py` BC-PROJ-10 paired entry-pin schema (slice-049 / `entry_present_in_repo` + `shippability_consumer_propagation` pair).
- `architecture/shippability.md` row schema (6-col: # / Slice / What it guards / Command / Limits / Machine-cmd).
- `skills/build-slice/SKILL.md` Step 6 prose-block pattern (BC-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1 sub-sections all share the same heading + `## Run:` block + refusal-semantics-list + bootstrap-clause structure).
- `architecture/risk-register.md` R-10 / R-11 / R-15 retirement paragraph shape (BC-PROJ-6 — flip `**Status**:` field-line; preserve prior prose verbatim; append retirement paragraph at section end).

## Components touched

### `tools/new_agent_warning_audit.py` (new)

- **Responsibility**: Compute the union of three `git`-derived sets — (i) `git diff --name-only --diff-filter=A {base} -- 'agents/*.md'` (working-tree-vs-base; covers modified+staged uncommitted additions), (ii) `git ls-files --others --exclude-standard -- 'agents/*.md'` (untracked-new agents), (iii) `git diff --name-only --diff-filter=A {base}...HEAD -- 'agents/*.md'` (already-committed-in-branch agents). Deduplicate by path. Emit a NAW-1 WARN line per matched added file naming the agent path + session-restart recommendation + R-18 reference. Exit 0 on both clean (no matches) and warn (≥1 match) branches. Exit 2 only on usage errors (repo root unresolvable, `git` unavailable, default-branch resolution returned `None` per BRANCH-1's `default-branch-unresolvable`, any of the three `git` subprocess calls non-zero).
- **Lives at**: `tools/new_agent_warning_audit.py` (created by this slice).
- **Key interactions**:
  - `tools/_stdout` — `_stdout.reconfigure_stdout_utf8()` first statement of `main()` (UTF8-STDOUT-1).
  - `subprocess.run(["git", ...])` — three call sites: default-branch resolution, `git diff` × 2 (working-tree-vs-base + commits-vs-base), `git ls-files --others`.
  - No imports from other `tools/*.py` modules (standalone audit).
- **Public surface**: `CheckResult` dataclass (`status`, `exit_code`, `warnings: list[str]`, `divergences: list[str]`, `to_dict() -> dict`); `_resolve_default_branch(root: Path) -> str | None`; `_resolve_added_agent_files(root: Path, base: str) -> list[str]` (returns the deduplicated union of the three source sets); `check(root: Path, *, default_branch_resolver=…, added_files_resolver=…) -> CheckResult` with two injection seams for the regression suite (the `added_files_resolver` seam is load-bearing for the m3-redesigned seam-driven self-application test); `_format_human(result: CheckResult) -> str`; `_format_warn_line(agent_path: str) -> str` (the canonical WARN template per [[ADR-061]]); `main(argv: list[str] | None = None) -> int`.

### `tests/methodology/test_new_agent_warning_audit.py` (new)

- **Responsibility**: Regression-pin the audit's 4 documented states + the WARN-message anchors + the slice-063 self-application contract.
- **Lives at**: `tests/methodology/test_new_agent_warning_audit.py` (created by this slice).
- **Key interactions**:
  - `tools.new_agent_warning_audit` — imports `check`, `CheckResult`, `_format_warn_line`, `main` for unit + subprocess-style harness tests.
  - `subprocess.run` — for the wired-in-Step-6 grep-test (substring-pin on `skills/build-slice/SKILL.md`).
  - `pathlib.Path` — for the tmp_repo fixture (synthetic `agents/foo.md` add) and the in-repo self-application.
- **Test functions** (final names; AC mapping pinned in mission-brief Test-first plan):
  - `test_audit_exits_0_on_no_agent_diff` (AC1) — `added_files_resolver` returns `[]` → `result.status == "clean"`, `result.exit_code == 0`, no warnings.
  - `test_audit_exits_0_on_new_agent_diff_with_warn_line` (AC1) — `added_files_resolver` returns `["agents/foo.md"]` → `result.status == "warn"`, `result.exit_code == 0`, `result.warnings` non-empty.
  - `test_warn_line_cites_agent_path_session_restart_and_r_18` (AC3) — `_format_warn_line("agents/foo.md")` contains `"agents/foo.md"` AND `"restart Claude Code"` AND `"R-18"`.
  - `test_audit_positive_contrast_synthetic_tmp_repo_untracked` (AC4) — tmp_repo fixture with an UNTRACKED `agents/foo.md` (created on disk, not added to git) → real `_resolve_added_agent_files` runs `git ls-files --others --exclude-standard` and returns the file → audit exits 0 with WARN (covers source (ii)).
  - `test_audit_positive_contrast_synthetic_tmp_repo_staged` (AC4) — tmp_repo fixture with a STAGED-BUT-UNCOMMITTED `agents/foo.md` (`git add`-ed, no commit) → real `_resolve_added_agent_files` runs `git diff --diff-filter=A {base}` and returns the file → audit exits 0 with WARN (covers source (i)).
  - `test_audit_negative_contrast_no_diff` (AC4) — tmp_repo fixture with no `agents/*.md` changes → audit exits 0 quietly.
  - `test_self_application_audit_against_real_repo_is_clean_or_warn_with_known_agents` (AC4; m3 redesign) — uses the `added_files_resolver` injection seam (NOT live `git diff` against slice-063's branch) with a controlled fixture set: empty list → `result.status == "clean"`; single-entry list → `result.status == "warn"`. Regression-stable across slice-064+ because the test does not depend on slice-063's specific live branch state. Replaces the bootstrap-brittle `test_self_application_slice_063_diff_is_clean` per Critic m3.

### `skills/build-slice/SKILL.md` (modified)

- **Responsibility**: Step 6 pre-finish enumeration + new prose sub-section documenting the NAW-1 audit's refusal/warn semantics + bootstrap clause.
- **Lives at**: `skills/build-slice/SKILL.md` (modified).
- **Changes**:
  1. The Step 6 checklist (currently L138-155) gains a new line after the TVFS-1 row: `- [ ] **New-agent session-restart warning (NAW-1)** — see "New-agent warning audit" below`.
  2. After the existing `#### ai-sdlc-tools version forward-sync audit (TVFS-1)` sub-section (currently ending L314), append a new `#### New-agent warning audit (NAW-1)` sub-section with: rule-reference citation (NAW-1 / methodology-changelog v0.66.0 / slice-063 / [[ADR-061]]); the `$PY -m tools.new_agent_warning_audit` run-line; refusal-semantics list (`warn` exit 0 + WARN line; `clean` exit 0 quiet; `usage` exit 2 — no exit 1 by construction); the naming-class-peers prose ("NAW-1 is the first audit-enforced gate on the **discovery-gate** axis"); and the slice-063 bootstrap clause (vacuous-pass — slice-063 adds zero `agents/*.md`).
- **Forward-sync obligation**: `~/.claude/skills/build-slice/SKILL.md` must be updated at /reflect Step 5b per OSDG-1 (`tests/methodology/test_build_slice_skill_drift.py`).

### `tools/install_audit.py` (modified)

- **Responsibility**: `_CANONICAL_TOOLS` tuple — alphabetic insertion of `"tools.new_agent_warning_audit"` between `"tools.methodology_changelog_forward_sync"` and `"tools.mock_budget_lint"`.
- **Lives at**: `tools/install_audit.py` L90-118 (modified).
- **Note**: the bracket-comment at L84-89 (`# canonical chain extended from 8 to 9 covered skills at slice-060 …`) does NOT need editing — it describes a separate concern (canonical-chain-extension, not tool-set-extension).

### `tests/methodology/test_utf8_stdout_regression.py` (modified)

- **Responsibility**: `_ROOT_ONLY_TOOLS` list — append `"tools.new_agent_warning_audit",  # slice-063 / NAW-1 (--check/--json/--root, no slice arg)`.
- **Lives at**: `tests/methodology/test_utf8_stdout_regression.py` L95-104 (modified).

### `plugin.yaml` (modified)

- **Responsibility**: append a new `tools/` path entry (alphabetic insert within tool block).
- **Lives at**: `plugin.yaml` (modified — exact line range depends on current tool block ordering; the manifest_audit (PMI-1) test enforces lock-step parity with `_CANONICAL_TOOLS`).
- **Also bumps**: `version` field `0.65.0` → `0.66.0` (PMI-1 atomic-bump leg 1).

### `VERSION` (modified)

- **Responsibility**: PMI-1 atomic-bump leg 2 — single-line value `0.65.0` → `0.66.0`.
- **Lives at**: `VERSION` (modified).

### `pyproject.toml` (modified)

- **Responsibility**: PVFS-1 leg — `[project].version` `"0.65.0"` → `"0.66.0"`. PVFS-1's `test_repro_sc001_pyproject_project_version_matches_version_file` enforces.
- **Lives at**: `pyproject.toml` (modified).

### `methodology-changelog.md` (modified)

- **Responsibility**: insert a new `## v0.66.0 — 2026-05-23` entry at the top (after the existing front-matter / `# Methodology changelog` header but BEFORE the existing `## v0.65.0` entry per the append-prepend file convention — verify position by reading current head). The entry text follows the slice-059 / slice-060 / slice-062 entry shape (anchored heading + behavior-change paragraph + `## Changed`/`## Added` section + Rule-reference + Defect-class + Validation-method bullets).
- **Lives at**: `methodology-changelog.md` (modified).

### `~/.claude/ai-sdlc-VERSION` (out-of-repo, modified at install-time)

- **Responsibility**: AVFS-1 forward-sync leg — bumped from `0.65.0` → `0.66.0` via Bash (the Write tool's auto-mode classifier refuses `~/.claude/*` per the slice-054 lesson `[[ai-claude-config-files-trip-write-tool-classifier]]`-shape — fold into the Phase B Bash invocation).
- **Lives at**: `~/.claude/ai-sdlc-VERSION` (modified out-of-repo).

### `~/.claude/methodology-changelog.md` (out-of-repo, modified at install-time)

- **Responsibility**: MCFS-1 forward-sync leg — `cp methodology-changelog.md ~/.claude/methodology-changelog.md` after the in-repo bump.
- **Lives at**: `~/.claude/methodology-changelog.md` (modified out-of-repo).

### `~/.claude/skills/build-slice/SKILL.md` (out-of-repo, modified at install-time)

- **Responsibility**: OSDG-1 forward-sync leg — `cp skills/build-slice/SKILL.md ~/.claude/skills/build-slice/SKILL.md` after the in-repo edit.
- **Lives at**: `~/.claude/skills/build-slice/SKILL.md` (modified out-of-repo).

### Installed venv `ai-sdlc-tools` (modified at install-time)

- **Responsibility**: TVFS-1 forward-sync leg — `$PY -m pip install --upgrade .` after the PMI-1 bump refreshes the installed distribution metadata to `0.66.0` AND ships the new `tools/new_agent_warning_audit.py` into the venv's `site-packages/tools/` so `$PY -m tools.new_agent_warning_audit` resolves from `purelib` in adopted projects.
- **Lives at**: installed venv `site-packages/tools/`.

### `INSTALL.md` (modified)

- **Responsibility**: bump the two hard-coded tool-count literals `27` → `28` at L22 + L166.
- **Lives at**: `INSTALL.md` (modified).
- **BC-PROJ-11 sibling-coverage check at /build-slice**: scan INSTALL.md for any other "27" / "tool" / "module" / "executable" pairings; at /design-slice authoring time the grep yielded only L22 + L166 — no third hidden literal.

### `architecture/risk-register.md` (modified — R-18 retirement)

- **Responsibility**: flip `**Status**: mitigating` → `retired` at `architecture/risk-register.md:303` (BC-PROJ-6 single-source-of-truth field-line); preserve all prior Mitigation prose verbatim per slice-040 R-10 retirement-precedent; append a `**Retired**: slice-063-add-build-slice-new-agent-warning (2026-05-23)` field-line below `**Status**`; append a retirement paragraph at section end citing `tools/new_agent_warning_audit.py` (NAW-1) as the discharge mechanism.
- **Lives at**: `architecture/risk-register.md` (modified).
- **STP-1 Sub-form B**: no `test_r_18_*_stays_*` function exists in the test corpus (verified at /design-slice via `grep -rn "r_18" tests/methodology/`) — Sub-form B clean, no stale-pin realignment needed.

### `architecture/shippability.md` (modified)

- **Responsibility**: append new row #63 — `| 63 | slice-063-add-build-slice-new-agent-warning | NAW-1 (slice-063; ADR-061 mints a new rule, supersedes nothing; the first audit-enforced gate on the discovery-gate axis adjacent to the PMI-1/PVFS-1/AVFS-1/MCFS-1/TVFS-1 forward-sync family): /build-slice Step 6 emits a non-blocking WARN when the slice diff adds any agents/*.md file naming the new agent path + session-restart-before-next-slice recommendation + R-18 cross-reference. Retires R-18 (mitigating → retired) — N=2 cumulative recurrence at slice-061 + slice-062 surfaced the runtime registry session-cache-miss class methodology-discoverably. Regression = a future agent-shipping slice ships without surfacing the WARN, the audit's exit contract drifts from binary (0/2) to tri-state (0/1/2), the WARN message loses its R-18 anchor or agent-path citation, the v0.66.0 entry's NAW-1 / ADR-061 / mints a new rule / supersedes nothing / 5-part PMI-1 atomic bump / Rule reference anchors silently lost, OR the BCR-1 traceability axis (row cites BOTH NAW-1 AND R-18) silently severed. | <pytest command> | <2s | <expanded pytest command> |`. BCR-1 traceability cites BOTH `NAW-1` AND `R-18` per slice-054 first-dogfood precedent.
- **Lives at**: `architecture/shippability.md` (modified).
- **BC-PROJ-7 pipe-free discipline**: row Description text contains no raw `|` characters (the SCMD-1 parser uses naive `inner.split("|")` and doesn't honor markdown `\|` escapes); verify at /build-slice Phase D.

### `tests/methodology/test_methodology_changelog.py` (modified)

- **Responsibility**: append 2 NEW entry-pin tests under a NEW `# --- Slice-063 / NAW-1 entry pinning ---` SECTION header at end-of-file: `test_v_0_66_0_naw_1_entry_present_in_repo` (substring anchors on the v0.66.0 entry's content-bearing bullets) + `test_v_0_66_0_naw_1_shippability_consumer_propagation` (BC-PROJ-10 paired-pin — substring assertion on shippability row #63's `NAW-1` AND `R-18` AND `ADR-061` citations).
- **Lives at**: `tests/methodology/test_methodology_changelog.py` (modified).
- **EPGD-1 section-header discipline**: the NEW SECTION header anchor `# --- Slice-063 / NAW-1 entry pinning ---` mirrors the slice-062 / slice-060 / slice-059 section-header pattern (slice-062 reflection m2 ACCEPTED-FIXED EPGD-1 directive).

## Contracts added or changed

### `tools.new_agent_warning_audit` CLI (new methodology-tool contract)

- **CLI surface**: `$PY -m tools.new_agent_warning_audit [--check] [--json] [--root <repo-root>]`
- **Defined in code at**: `tools/new_agent_warning_audit.py` (to be created).
- **Auth model**: N/A (read-only local file/git CLI tool; no network, no credentials, no shared state mutation).
- **Exit-code contract** (BINARY by construction — no tri-state):
  - `0` `status: "clean"` — no added `agents/*.md` in slice diff vs default branch.
  - `0` `status: "warn"` — ≥1 added `agents/*.md`; WARN line(s) emitted on stdout (`--check` mode) or in `warnings:` list (`--json` mode).
  - `2` `status: "usage"` — repo root unresolvable, `git` binary unavailable on PATH, default-branch resolution returned `None`, OR `git diff` errored (non-zero subprocess exit).
- **Error cases**:
  - Repo root unresolvable → exit 2 + stderr message naming the resolved path that failed.
  - `git` binary missing → exit 2 + stderr message ("`git` command not found on PATH; NAW-1 cannot resolve the slice diff").
  - Default-branch resolution failure (neither `git symbolic-ref refs/remotes/origin/HEAD` nor `git config init.defaultBranch` returns a value) → exit 2 + stderr message.
  - `git diff` non-zero exit → exit 2 + stderr message including `git`'s own stderr.
  - No `--json` payload on exit 2 (stderr-only error contract per AVFS-1/TVFS-1 precedent).

## Data model deltas

(none — slice ships no new database / persistence / schema entities; all artifacts are markdown / TOML / Python source files)

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/new_agent_warning_audit.py` | `skills/build-slice/SKILL.md` Step 6 enumeration line + `#### New-agent warning audit (NAW-1)` prose sub-section | `tests/methodology/test_new_agent_warning_audit.py` (7 tests post-m3-redesign) + `tests/methodology/test_build_slice_skill.py::test_build_slice_step_6_invokes_new_agent_warning_audit` (structural-anchor pin per slice-017 TPHD-1 sub-mode (c) lineage — M4 critique fix) + `tests/methodology/test_build_slice_skill_drift.py` (Mini-CAD-1 in-repo↔installed forward-sync; passes automatically post-`cp` of edited SKILL.md to `~/.claude/skills/build-slice/SKILL.md`) + `tests/methodology/test_methodology_changelog.py::test_v_0_66_0_naw_1_entry_present_in_repo` / `::test_v_0_66_0_naw_1_shippability_consumer_propagation` | — |
| `tests/methodology/test_new_agent_warning_audit.py` | `architecture/shippability.md` row #63 (catalog-cited via shippability runner) | self-consumer (the test module IS its own consumer entry per slice-055 SRSC-1 row pattern) | — |

## Decisions made (ADRs)

- [[ADR-061]] — Mint NAW-1 (New-Agent Warning) — standalone tool gating `/build-slice` Step 6 with binary exit contract — reversibility: **cheap**.

## Authorization model for this slice

N/A. The new audit tool is local CLI-only (read-only: shells out to `git diff`; reads in-repo files; no network, no credentials, no shared-state mutation). It exposes no new API endpoint, no new event, no new RPC. The slice flips one risk-register status field and edits methodology source files — all standard repo-write operations covered by existing developer auth (filesystem permissions + git commit signing).

## Error model for this slice

This slice introduces no new code-runtime error classes for end-user-facing behavior. It introduces three audit-tool error classes (per the CLI contract above):

- **`usage` (exit 2)** — environment/setup error: repo root unresolvable, `git` missing, default-branch unresolvable, `git diff` errored. Distinct stderr message per cause; no `--json` payload (stderr-only error per AVFS-1/TVFS-1 precedent).
- **`clean` (exit 0, quiet)** — no diff matches; structural pass.
- **`warn` (exit 0, stdout)** — ≥1 diff match; informational. NEVER blocks `/build-slice` Step 6 by construction (exit 1 is not in the contract).

The binary exit contract is the **central error-model assertion** of NAW-1: any future diff that adds `agents/*.md` files SHALL surface as a WARN at Step 6, never as a HALT. A future regression that introduces an exit-1 branch into `tools/new_agent_warning_audit.py` is the load-bearing contract violation that the regression suite pins (`test_audit_exits_0_on_new_agent_diff_with_warn_line` asserts `exit_code == 0` even on the WARN branch).

## Genuine-contrast proof method

Per **BC-PROJ-5** (slice-042) / **slice-046 prose-reclassification pattern** / **slice-053 multi-site-literal contrast guidance**. Test-first ACs require non-tautological FAIL→PASS evidence. Anchor literals are pinned BEFORE the implementation lands; each test's failure mode at /build-slice Phase A is the structural contrast:

| AC | Anchor literal (positive pin) | Pre-edit FAIL signature | Post-edit PASS signature |
|----|-------------------------------|--------------------------|---------------------------|
| 1 | `tools.new_agent_warning_audit` module importable | `ImportError: No module named 'tools.new_agent_warning_audit'` | clean import; `check(tmp_repo)` returns `CheckResult` |
| 1 | exit-code contract (binary) | tool absent → test cannot collect | `result.exit_code in (0, 2)` for all 4 documented states |
| 2 | `skills/build-slice/SKILL.md` Step 6 enumeration line `New-agent session-restart warning (NAW-1)` | substring absent from SKILL.md | substring present; `test_build_slice_step_6_invokes_new_agent_warning_audit` PASSES |
| 3 | WARN line cites `agents/foo.md` AND `restart Claude Code` AND `R-18` | function `_format_warn_line` absent OR missing one anchor | all 3 substrings present in returned string |
| 4 | tmp_repo positive contrast (untracked source ii): synthetic UNTRACKED `agents/foo.md` → WARN via `git ls-files --others` | tool absent | `result.status == "warn"`, non-empty `warnings:` |
| 4 | tmp_repo positive contrast (staged source i): synthetic STAGED-UNCOMMITTED `agents/foo.md` → WARN via `git diff --diff-filter=A {base}` | tool absent | `result.status == "warn"`, non-empty `warnings:` |
| 4 | tmp_repo negative contrast: no agent diff → clean | tool absent | `result.status == "clean"`, empty `warnings:` |
| 4 | seam-driven self-application (`added_files_resolver` injection): empty → `clean`; single-entry → `warn` | tool absent | both states produce expected `result.status` (regression-stable across slice-064+) |
| 5 | R-18 retired in `risk-register.md` | `**Status**: mitigating` at L303 | `**Status**: retired` at L303; `risk_register_audit --filter-status open --json` does NOT list R-18; `--filter-status retired --json` DOES list R-18 |

## Validation strategy

Per slice's pre-finish gate in `mission-brief.md`:

1. **Test-first audit (TF-1 strict-pre-finish)**: all 9 rows of mission-brief's Test-first plan land at PASSING.
2. **Audit suite at Step 6**: 14 audits per `skills/build-slice/SKILL.md` Step 6 (L138-156 post-NAW-1) — the 13 existing audits (`branch_workflow / utf8_stdout / critique_review_prerequisite / pipeline_chain / build_checks_integrity / methodology_changelog_forward_sync / state_transition_pin / ai_sdlc_version_forward_sync / ai_sdlc_tools_version_forward_sync / mock_budget_lint / wiring_matrix / build_checks / test_first`) all exit 0, plus the NEW `new_agent_warning_audit` (NAW-1) self-application exits 0 quietly (vacuous-pass — slice-063 adds zero `agents/*.md`). Note: `plugin_manifest` (PMI-1) is enforced via paired tests + the `_CANONICAL_TOOLS`/`plugin.yaml` lock-step, NOT a Step 6 checklist line — meta-Critic M-add-3 critique fix.
3. **Shippability runner**: `$PY -m tools.shippability_runner architecture/shippability.md` — 63/63 PASS with new row #63 PASSING.
4. **Full methodology suite**: `$PY -m pytest tests/methodology/ tests/skills/ tests/agents/` — all PASS (slice-062 baseline + 7 new tests in `test_new_agent_warning_audit.py` + 1 new test in `test_build_slice_skill.py` + 1 new test in `test_risk_register_audit_real_file.py` + 2 entry-pin tests in `test_methodology_changelog.py`).
5. **OSDG-1 / CAD-1 drift suite**: all 8 guarded `.md` content-equality tests PASS post-forward-sync (slice's `~/.claude/skills/build-slice/SKILL.md` cp + `~/.claude/methodology-changelog.md` cp at Phase B).
6. **PCA-1 chain audit**: `$PY -m tools.pipeline_chain_audit` exits 0 — Step 6 extension is purely additive to the existing 9-skill chain; no `## Pipeline position` blocks edited.
7. **/drift-check**: vault and code aligned.

## Pre-finish gate (acknowledgement)

The mission-brief.md §Pre-finish gate is the canonical checklist; this design.md adds no new gate items, only crystallizes the mechanism for each.

## Pipeline position

- **predecessor**: `/slice`
- **successor**: `/critique`
- **auto-advance**: true
- **on-clean-completion**: design.md + ADR-061 written → invoke `/critique` via the Skill tool without waiting for the user. The slice's `critic-required: true` (in-house methodology surfaces trigger — `skills/build-slice/SKILL.md` + new `tools/*.py` + `methodology-changelog.md` + risk-register flip) is unchanged from the /slice-set value.
- **user-input gates** (halt auto-advance):
  - None pending — no clarifying questions surfaced at Step 2; design is unambiguous from mission-brief + slice-062 reflection L40 + R-18 entry.

> Per PCA-1 (methodology-changelog.md v0.41.0).
