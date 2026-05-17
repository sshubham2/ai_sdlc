# Design: Slice 007 add-critique-agent-content-equality-audit

**Date**: 2026-05-10
**Mode**: Standard
**Risk-tier**: low (critic-required: true — cross-cutting tooling slice per slice-006 reflection lesson #2)

## Option chosen (the decision deferred from /slice)

**Option (d) hybrid: (c) skill-prose update + (a) standalone audit.**

Rationale:
- (c) alone is insufficient — fixes the source of recurrence (skill prose telling users to edit installed copy) but doesn't catch existing drift OR drift introduced by ignored prose. Slice-006 B1's catch was incidental (voluntary Critic happened to read implementation); methodology should not depend on incidental human-Critic discipline.
- (b) INST-2 extension is over-scoped for this slice. `tools/install_audit.py` was designed for source-independence (audit can run after deleting the source folder per INST-1 `methodology-changelog.md` v0.20.0). Adding content-equality requires both copies present at audit time — that violates INST-1's core design assumption. INST-2 is a different audit class and belongs in its own slice if/when in-repo↔installed drift recurs on files other than `agents/critique.md`.
- (a) alone fixes detection but not the recurrence source — every future `/critic-calibrate` ACCEPTED proposal would still need the user to manually run the new audit; a missed run = silent drift.
- **(c)+(a) together**: prose addresses the recurrence at its source; audit catches anything the prose doesn't prevent. Both validated via tests. Effort ~45-60 min per slice-006's estimate band.

Future scope for explicit non-goal: if drift recurs on `agents/critique-review.md`, `agents/critic-calibrate.md`, or other in-repo↔installed pairs (e.g., `~/.claude/build-checks.md`), generalize via INST-2 then. Track at N=2.

## What's new

- New audit module `tools/critique_agent_drift_audit.py` — sha256 comparison between in-repo `agents/critique.md` and installed `~/.claude/agents/critique.md`. CLI mirrors `tools/install_audit.py` shape (`--claude-dir`, `--repo-root`, `--json`, `--strict`). Exit codes: 0 clean / 1 drift / 2 path missing or usage error.
- New test module `tests/methodology/test_critique_agent_drift.py` — 4 tests pinning audit behavior + the chosen mechanism's parity surfaces (see TF-1 plan in mission-brief.md).
- New methodology-changelog entry `v0.22.0 — 2026-05-10 — CAD-1 (Critic Agent Drift)` — both in-repo `methodology-changelog.md` and forward-synced `~/.claude/methodology-changelog.md`. Bumps in-repo `VERSION` from `0.21.0` → `0.22.0` (and forward-syncs to `~/.claude/ai-sdlc-VERSION` with the install-time rename per `INSTALL.md:141`). Per Critic B1 (cross-cutting conformance N=2): the in-repo file is `VERSION`, not `ai-sdlc-VERSION` — the `ai-sdlc-` prefix is added at install time, not in-repo.
- Updated `_CANONICAL_TOOLS` in `tools/install_audit.py` (14 → 15 entries) and `tools/` list in `plugin.yaml` (14 → 15 entries) — paired test `test_canonical_tools_match_plugin_yaml` re-verifies after both updates.
- Updated prose in `skills/critic-calibrate/SKILL.md:107-114` (the "Accepted. To apply..." block) — instructs editing the in-repo canonical file with manual forward-sync, AND/OR running `tools.critique_agent_drift_audit` post-edit to verify byte-equality.

## What's reused

- `tools.install_audit` shape (CLI, `--claude-dir`, `--json`, `dataclass` result + violations) — `tools/critique_agent_drift_audit.py` follows the same conventions for cross-tool consistency.
- `tests/methodology/conftest.py` `REPO_ROOT` fixture for in-repo paths.
- `hashlib.sha256` (stdlib) for byte-equality. No new dependencies.
- INST-1's `_CANONICAL_*` lists in `tools/install_audit.py` are read directly by `test_critique_agent_drift.py` to verify the audit's path mapping aligns with installed-file conventions (slice-006 cross-cutting-conformance lesson at N=1 — verified mechanically below).
- [[ADR-005]] (slice-006) — established the bidirectional sync discipline; this slice's Phase 0 sha256-checkpoint pattern reuses the slice-006 forensic-capture form.
- [[methodology-changelog#v0.20.0]] INST-1 entry — `_CANONICAL_METADATA` enumerates `methodology-changelog.md` + `ai-sdlc-VERSION` as installed metadata (both forward-sync targets in this slice).

## Components touched

### `tools/critique_agent_drift_audit.py` (new)
- **Responsibility**: detects in-repo↔installed sha256 drift on `agents/critique.md` and reports the divergent paths + hashes. Standalone audit; not coupled to `tools/install_audit.py` so INST-1's source-independence design contract is preserved.
- **Lives at**: `tools/critique_agent_drift_audit.py` (created by this slice)
- **CLI flags** (per Critic M1 — `--repo-root` is an EXTENSION beyond `install_audit.py`, not a mirror; `install_audit.py:339-352` has only `--claude-dir`, `--strict`, `--no-strict`, `--json`):
  - `--repo-root <path>` (default `Path.cwd()`) — in-repo source root containing `agents/critique.md`. Audit refuses with `usage-error` (exit 2) if `--repo-root / 'plugin.yaml'` AND `--repo-root / 'INSTALL.md'` don't both exist (sanity check per Critic M3 — prevents accidental comparison against stale `build/lib/` shadow or arbitrary directory).
  - `--claude-dir <path>` (default `Path.home() / '.claude'`) — installed root. Same convention as `install_audit.py`.
  - `--json` — machine-readable output. Same convention as `install_audit.py`.
- **Key interactions**: reads two files (in-repo `<--repo-root>/agents/critique.md`, installed `<--claude-dir>/agents/critique.md`); emits `AuditResult` dataclass with `violations: list[CritiqueDriftViolation]`. No external API calls; no graphify. Exit-code contract: `0` clean / `1` content-drift / `2` path-missing OR usage-error.

### `skills/critic-calibrate/SKILL.md` (modified)
- **Responsibility**: orchestrates `/critic-calibrate` Meta-Critic agent + presents proposals one-at-a-time + logs runs. The lines 107-114 prose currently instructs editing installed `~/.claude/agents/critique.md` only — this slice corrects it to point at in-repo `agents/critique.md` as canonical, with explicit forward-sync + audit.
- **Lives at**: `skills/critic-calibrate/SKILL.md` (in-repo) and `~/.claude/skills/critic-calibrate/SKILL.md` (installed; forward-synced post-edit)
- **Key interactions**: read by Claude main thread when `/critic-calibrate` skill is invoked; the corrected prose at lines 107-114 will appear in every future calibration run's output.

### `tools/install_audit.py` `_CANONICAL_TOOLS` (modified)
- **Responsibility**: hardcoded inventory of 14 tool modules pip-installed with `ai-sdlc-tools`; this slice adds the 15th entry `tools.critique_agent_drift_audit`.
- **Lives at**: `tools/install_audit.py:66-81` (the `_CANONICAL_TOOLS` tuple) plus the comment at line 65 ("The 14 tool modules in v0.20.0..." → "The 15 tool modules in v0.22.0...").
- **Key interactions**: paired with `plugin.yaml` `tools:` list via `test_canonical_tools_match_plugin_yaml` — both must be updated atomically.

### `plugin.yaml` (modified)
- **Responsibility**: PMI-1 plugin manifest enumerating skills, agents, tools.
- **Lives at**: `plugin.yaml` (in-repo only — NOT in INST-1's `_CANONICAL_*` per slice-006 DEVIATION-1; not forward-synced)
- **Changes**: (1) version `0.20.0` → `0.22.0` (synced with `ai-sdlc-VERSION`; PMI-1 enforces equality — note: plugin.yaml.version was lagging at 0.20.0 post-slice-006 which bumped VERSION to 0.21.0; this slice corrects both to 0.22.0); (2) tools list adds `path: tools/critique_agent_drift_audit.py / rule: CAD-1` as the 15th entry.

### `methodology-changelog.md` and `~/.claude/methodology-changelog.md` (modified — bidirectional)
- **Responsibility**: methodology rule audit trail. INST-1 keeps both copies byte-equal.
- **Changes**: prepend new dated entry `## v0.22.0 — 2026-05-10` with `### Added` section documenting CAD-1 rule, defect class (in-repo↔installed content drift on `agents/critique.md`), validation method (`tools.critique_agent_drift_audit` + `tests/methodology/test_critique_agent_drift.py`).

### `VERSION` (in-repo) and `~/.claude/ai-sdlc-VERSION` (installed) — bidirectional with install-time rename
- **Responsibility**: semver pulse for `/status` and runtime version checks. Per `INSTALL.md:141` the install step copies `VERSION` (in-repo, no prefix) to `~/.claude/ai-sdlc-VERSION` (with the `ai-sdlc-` prefix added). The in-repo file is named `VERSION`; only the installed copy carries the `ai-sdlc-` prefix. `_CANONICAL_METADATA` in `tools/install_audit.py:62` lists installed names ("`ai-sdlc-VERSION`"), not in-repo names.
- **Changes**: `0.21.0` → `0.22.0` in `VERSION` (in-repo) and `~/.claude/ai-sdlc-VERSION` (installed). Forward-sync via `cp $REPO/VERSION ~/.claude/ai-sdlc-VERSION` per the install convention. Per Critic B1: this naming was incorrectly stated as `ai-sdlc-VERSION` (in-repo) in initial design.md draft; corrected to recurrence-of-slice-006-DEVIATION class at N=2 — promoted in slice-007 reflection as Dim 9 sub-clause refinement candidate.

### `tests/methodology/test_critique_agent_drift.py` (new)
- **Responsibility**: pin audit behavior + chosen-mechanism parity surfaces.
- **Lives at**: `tests/methodology/test_critique_agent_drift.py` (created by this slice)
- **Key interactions**: imports `tools.critique_agent_drift_audit` for unit tests; reads `skills/critic-calibrate/SKILL.md` for prose-pin; reads `methodology-changelog.md` for dated-entry pin.

### `architecture/shippability.md` (modified)
- **Responsibility**: regression catalog; `/validate-slice` runs all critical-path tests at pre-finish.
- **Changes**: append slice-007 row — `tests/methodology/test_critique_agent_drift.py` full module run.

## Contracts added or changed

### `python -m tools.critique_agent_drift_audit` (new CLI)
- **Defined in code at**: `tools/critique_agent_drift_audit.py` (to be created)
- **Auth model**: filesystem read-only. No network. Reads two paths: in-repo `agents/critique.md` (resolved via `--repo-root`, default cwd) and installed `~/.claude/agents/critique.md` (resolved via `--claude-dir`, default `$HOME/.claude`).
- **Exit codes**: `0` clean / `1` drift detected / `2` either path missing or usage error.
- **Error cases**: missing in-repo path → exit 2 with `path-missing` violation; missing installed path → exit 2 with `path-missing`; both present + sha256 differ → exit 1 with `content-drift` violation including both paths and both hashes; identical sha256 → exit 0 with human-readable "clean" or `--json` `violations: []`.

(Don't duplicate the CLI flags/output schema here — they live in the module's argparse / `AuditResult` dataclass. Pattern mirrors `tools/install_audit.py:334-365` exactly except `--strict` is omitted, the audit only checks the one file pair.)

### `skills/critic-calibrate/SKILL.md` lines 107-114 (modified prose contract)
- **Defined in code at**: `skills/critic-calibrate/SKILL.md:107-114` (after edit)
- **Behavior change**: replaces "edit `~/.claude/agents/critique.md` and add the following..." with a 3-line block that names `agents/critique.md` (in-repo) as canonical, instructs forward-sync to `~/.claude/agents/critique.md`, and points at `python -m tools.critique_agent_drift_audit` for post-edit verification. Pinned via `test_critic_calibrate_skill_prose_addresses_drift` in the new test module.

## Data model deltas

None. This slice ships methodology tooling, not user-facing data.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Every new module/file declares a consumer entry point AND a consumer test, OR carries an explicit exemption.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/critique_agent_drift_audit.py` | self (CLI via `__main__`); shippability invocation | `tests/methodology/test_critique_agent_drift.py` | — |
| `tests/methodology/test_critique_agent_drift.py` | pytest collection (test discovery) | self (audit's own test module) | rationale: test module has no programmatic consumer beyond pytest itself; same shape as every other `tests/methodology/test_*.py` |

## Out-of-repo files touched

Per slice-005 + slice-006 forensic-capture discipline, the slice's git diff alone is insufficient evidence for `~/.claude/...` edits. `build-log.md` will capture sha256 before/after for each row.

| File (post-install name) | In-repo path | Installed path | Sync direction | INST-1 canonical? |
|--------------------------|--------------|----------------|----------------|-------------------|
| critic-calibrate SKILL.md | `skills/critic-calibrate/SKILL.md` | `~/.claude/skills/critic-calibrate/SKILL.md` | forward (file copy) | yes — `_CANONICAL_SKILLS` |
| methodology-changelog | `methodology-changelog.md` | `~/.claude/methodology-changelog.md` | forward (file copy) | yes — `_CANONICAL_METADATA` |
| ai-sdlc-VERSION (installed name) | `VERSION` (no prefix in-repo) | `~/.claude/ai-sdlc-VERSION` (prefix added at install) | forward (file copy WITH rename per `INSTALL.md:141`) | yes (under installed name `ai-sdlc-VERSION`) — `_CANONICAL_METADATA` |
| critique_agent_drift_audit | `tools/critique_agent_drift_audit.py` | (pip-installed via `ai-sdlc-tools`; resolved on next `pip install --upgrade`) | forward via pip | yes (post-update) — `_CANONICAL_TOOLS` |

NOT forward-synced (by design):
- `plugin.yaml` — in-repo only per slice-006 DEVIATION-1; not in any `_CANONICAL_*`
- `tools/install_audit.py` — pip-installed, auto-resolved on next `pip install --upgrade ai-sdlc-tools`
- `tests/methodology/test_critique_agent_drift.py` — test files don't ship to `~/.claude/`
- `architecture/decisions/ADR-006-*.md` — vault content, project-local
- `architecture/shippability.md` — vault content, project-local

Verification of this table per slice-006 cross-cutting-conformance lesson at N=1:
- Each "yes" row matched against `tools/install_audit.py:_CANONICAL_*` literal contents at design-time.
- `plugin.yaml` and `tools/install_audit.py` correctly excluded per slice-006 DEVIATION-1 + INST-1 design (pip-installed).

## Empirical verification at design-time (per slice-001..006 discipline N=5 stable)

Pre-design checks executed and noted here:

1. **In-repo↔installed sha256 of `agents/critique.md`**: per slice-006 Phase 5 forward-sync, both copies should be byte-equal post-slice-006. Phase 0 of build will verify this; if drift exists, that's a slice-006 regression to investigate before continuing — not a slice-007 problem to solve.

2. **In-repo↔installed sha256 of `skills/critic-calibrate/SKILL.md`**: not in slice-006 scope; status unknown. Phase 0 of build will check; if drift exists, back-sync FIRST per slice-006 Phase 1 pattern (installed→in-repo), THEN apply slice-007's edit, THEN forward-sync. The slice scope assumes byte-equality at start; back-sync is contingency.

3. **`_CANONICAL_TOOLS` count and shape vs `plugin.yaml.tools` count**: verified at design-time:
   - `tools/install_audit.py:66-81` lists 14 entries (per Critic m1, the canonical literals are): `tools.build_checks_audit`, `tools.critique_review_audit`, `tools.cross_spec_parity_audit`, `tools.exploratory_charter_audit`, `tools.install_audit`, `tools.mock_budget_lint`, `tools.plugin_manifest_audit`, `tools.risk_register_audit`, `tools.supersede_audit`, `tools.test_first_audit`, `tools.triage_audit`, `tools.validate_slice_layers`, `tools.walking_skeleton_audit`, `tools.wiring_matrix_audit`.
   - `plugin.yaml:88-116` lists 14 entries with matching paths (`tools/<short-name>.py` form).
   - `test_canonical_tools_match_plugin_yaml` (`tests/methodology/test_install_audit.py:225`) verifies parity. Both must be updated atomically; slice-007 adds the 15th entry to both with shared rule reference `CAD-1` (`tools.critique_agent_drift_audit` in `_CANONICAL_TOOLS`; `tools/critique_agent_drift_audit.py` in `plugin.yaml`).
   - **Note** (per Critic M3): `build/lib/tools/install_audit.py:62` is a stale shadow from a prior pip-install build step (`git status: ?? build/`). The new audit's `--repo-root` sanity check (refuse if no `plugin.yaml` + `INSTALL.md`) prevents accidental comparison against this shadow.

4. **`plugin.yaml.version` vs in-repo `VERSION`**: design-time read shows `plugin.yaml:15` is `0.20.0` while in-repo `VERSION` (which gets renamed to `~/.claude/ai-sdlc-VERSION` at install) is `0.21.0` (post-slice-006). PMI-1 audit (`tools/plugin_manifest_audit.py:144` reads `root / "VERSION"`) enforces equality between `plugin.yaml.version` and in-repo `VERSION` — meaning slice-006 left a PMI-1 violation behind on `plugin.yaml.version`. **Builder verified empirically post-Critic B2**: `python -m tools.plugin_manifest_audit --root .` exits 1 with `plugin.yaml version '0.20.0' does not match VERSION file '0.21.0'`. Slice-007 corrects both atomically by setting `plugin.yaml.version = 0.22.0` and `VERSION = 0.22.0`, AND adds a slice-007 AC #5 + verification-plan row + must-not-defer entry + TF-1 row that gates the fix (per Critic B2 — without the gate, the fix is unenforced). Will be captured in slice-007 reflection's "Discovered" section as a Critic-MISSED at slice-006 (`plugin.yaml.version` not co-bumped).

5. **CAD-1 rule-ID uniqueness**: grep across `methodology-changelog.md` for `CAD-1` returns no hits — rule ID is novel.

## Decisions made (ADRs)
- [[ADR-006]] — Adopt option (d) hybrid (c+a) for in-repo↔installed drift detection on `agents/critique.md`; reject INST-2 extension as over-scoped — reversibility: **cheap** (audit + prose change + 15-min mechanical revert)

## Authorization model for this slice

- The new audit reads two filesystem paths (read-only); no privilege escalation. Same model as all `tools/*_audit.py` modules.
- The skill-prose change in `skills/critic-calibrate/SKILL.md` is text content; no permission boundary.
- Out-of-repo file modifications (forward-sync) inherit the user's filesystem permissions on `~/.claude/`. This is the same access pattern slice-005 + slice-006 used.

## Error model for this slice

- **`path-missing` (exit 2)**: `agents/critique.md` (in-repo) OR `~/.claude/agents/critique.md` (installed) doesn't exist. Message names which path is missing + suggests next step (re-run INSTALL.md if installed; check cwd if in-repo).
- **`content-drift` (exit 1)**: both files present, sha256 differs. Message includes both paths AND both hashes (per must-not-defer requirement) so user can diff and decide direction. Suggests `python -m tools.critique_agent_drift_audit --json` for machine-readable output.
- **`usage-error` (exit 2) — argparse-level**: unknown flag, conflicting args. Standard argparse output.
- **`usage-error` (exit 2) — sanity check refusal** (per Critic M3): `--repo-root` doesn't contain a `plugin.yaml` AND `INSTALL.md`. Message: "`--repo-root <path>` does not appear to be an AI SDLC source root (missing `plugin.yaml` and/or `INSTALL.md`). Refusing to compare against potentially stale `build/lib/` shadow or arbitrary directory. Pass `--repo-root <ai-sdlc-source>` explicitly." Verified empirically: `git status` shows `?? build/` — the stale shadow is real.
- Clean (exit 0): one-line "CAD-1: clean — agents/critique.md byte-equal across in-repo and ~/.claude/" with optional version field if `--json`.
