# Validation: Slice 063 add-build-slice-new-agent-warning

**Date**: 2026-05-23
**Result**: PASS

## Per-criterion results

### AC1: A new audit tool under `tools/` detects added files matching `agents/*.md` in the slice's git diff against the default branch and exits 0 with a structured WARN line on stdout on hit, exits 0 quietly on miss (non-blocking by design — never exit 1).

- **Status**: PASS
- **Evidence**:
  - `pytest tests/methodology/test_new_agent_warning_audit.py::test_audit_exits_0_on_no_agent_diff` → PASSED (binary clean branch: `status="clean"`, `exit_code=0`, no warnings)
  - `pytest tests/methodology/test_new_agent_warning_audit.py::test_audit_exits_0_on_new_agent_diff_with_warn_line` → PASSED (binary warn branch: `status="warn"`, `exit_code=0` ← load-bearing assertion that the audit NEVER returns exit 1)
  - Live run against current working tree (vacuous-clean self-application): `$PY -m tools.new_agent_warning_audit --json` → `{status: "clean", exit_code: 0, warnings: [], divergences: []}`
- **Notes**: Binary exit contract preserved by construction — verified by inspection (the only `result.exit_code` assignments are at L284/293/301/306 = 2 and L321/327 = 0; no code path sets exit_code to 1). The pytest assertion `result.exit_code == 0` on BOTH branches is the load-bearing pin per ADR-061 §Decision.

### AC2: `skills/build-slice/SKILL.md` Step 6 invokes the new audit as the last warn-only step in the pre-finish gate enumeration; the WARN surfaces in the user-visible Step 6 summary without halting PCA-1 auto-advance.

- **Status**: PASS
- **Evidence**:
  - `pytest tests/methodology/test_build_slice_skill.py::test_build_slice_step_6_invokes_new_agent_warning_audit` → PASSED (3 structural-anchor substrings present in `skills/build-slice/SKILL.md`: `**New-agent session-restart warning (NAW-1)**` checklist line + `#### New-agent warning audit (NAW-1)` prose sub-section heading + `tools.new_agent_warning_audit` run-line invocation)
  - PCA-1 chain audit clean at /build-slice Step 6 sweep — the new Step 6 enumeration is purely additive; canonical 9-skill chain unchanged
  - Manual SKILL.md review confirms the NAW-1 sub-section is appended after the TVFS-1 sub-section (Step 6 placement matches design.md L68-69)
- **Notes**: PCA-1 auto-advance from /build-slice → /code-review → /validate-slice → /reflect verified empirically — chain advanced cleanly through all three skill hops without halting on any NAW-1 invocation. Mini-CAD-1 forward-sync (cp `skills/build-slice/SKILL.md` → `~/.claude/skills/build-slice/SKILL.md`) completed at /build-slice Phase D1; `test_build_slice_skill_drift.py` passes.

### AC3: The WARN text names: each new agent file path, the session-restart-before-next-slice recommendation, and the explicit `R-18` risk-register cross-reference.

- **Status**: PASS
- **Evidence**:
  - `pytest tests/methodology/test_new_agent_warning_audit.py::test_warn_line_cites_agent_path_session_restart_and_r_18` → PASSED (all 3 substring anchors present in `_format_warn_line("agents/foo.md")` output: `"agents/foo.md"` + `"restart Claude Code"` + `"R-18"`)
  - Direct inspection of `_WARN_LINE_TEMPLATE` literal at `tools/new_agent_warning_audit.py:115-123` matches ADR-061 §Decision (Attributed WARN message template at ADR-061 L77)
- **Notes**: The WARN template interpolates only `{agent_path}` (which comes from git output, not raw user input) — no other user-controlled input, no shell injection vectors, no PII/secret risk surface.

### AC4: The audit has positive contrast tests covering BOTH source states a new agent file can occupy at Step 6 (untracked-new via `git ls-files --others` AND staged-uncommitted via `git diff --diff-filter=A {base}` per ADR-061 §Decision union-of-three-sources read mechanism), a negative contrast (no `agents/*.md` diff → WARN absent), AND a seam-driven self-application test using the `added_files_resolver` injection seam (per slice-059 TVFS-1 precedent) that remains regression-stable across slice-064+.

- **Status**: PASS
- **Evidence**:
  - `pytest tests/methodology/test_new_agent_warning_audit.py::test_audit_positive_contrast_synthetic_tmp_repo_untracked` → PASSED (synthetic tmp_repo with untracked `agents/foo.md` → real `git ls-files --others` returns the file → audit WARN; covers source (ii) of the union-of-three-sources)
  - `pytest tests/methodology/test_new_agent_warning_audit.py::test_audit_positive_contrast_synthetic_tmp_repo_staged` → PASSED (synthetic tmp_repo with staged-uncommitted `agents/foo.md` via `git add` → real `git diff --diff-filter=A {base}` returns the file → audit WARN; covers source (i))
  - `pytest tests/methodology/test_new_agent_warning_audit.py::test_audit_negative_contrast_no_diff` → PASSED (no `agents/*.md` changes → audit clean, quiet stdout)
  - `pytest tests/methodology/test_new_agent_warning_audit.py::test_self_application_audit_against_real_repo_is_clean_or_warn_with_known_agents` → PASSED (m3-redesigned seam-driven via `added_files_resolver` injection: empty list → clean; single-entry list → warn; regression-stable across slice-064+ per slice-059 TVFS-1 `installed_version_resolver` precedent)
- **Notes**: Real `git ls-files --others` and `git diff --diff-filter=A` empirically validated against actual git repos (synthetic tmp_repo fixture + the slice's own working tree). The B1 critique-fix mechanism behaves as documented across all 3 sources.

### AC5: R-18 status flips `mitigating → retired` in `architecture/risk-register.md` (RR-1 `**Status**:` field-line) with a retirement paragraph citing the new audit as the structural mechanism, preserving slice-061 / slice-062 prior prose verbatim per slice-040 R-10 retirement-precedent.

- **Status**: PASS
- **Evidence**:
  - `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open` → R-18 NOT in open set (open: `[R-13, R-2]` only); R-18 successfully retired
  - `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status retired` → R-18 IS in retired set
  - `pytest tests/methodology/test_risk_register_audit_real_file.py::test_r_18_retired_post_slice_063` → PASSED (structural pin: `**Status**: retired` field-line + `**Retired**: slice-063-...` provenance field-line + `slice-063` reference + `NAW-1`/`new_agent_warning_audit` mechanism cite in retirement paragraph)
  - Manual inspection of `architecture/risk-register.md:299-319` confirms: (a) Status field-line flipped `mitigating → retired` at L303 per BC-PROJ-6 single-source-of-truth discipline; (b) `**Retired**: slice-063-add-build-slice-new-agent-warning (2026-05-23)` provenance field-line at L304; (c) prior Mitigation paragraph preserved verbatim with N=2 cumulative recurrence note appended (slice-061 N=1 + slice-062 N=2 both witnessed); (d) retirement paragraph at section end citing NAW-1 / ADR-061 / v0.66.0 mechanism per slice-040 R-10 retirement-precedent shape
- **Notes**: STP-1 Sub-form B clean — the slice-063 pin `test_r_18_retired_post_slice_063` aligns with the new `retired` status (no contradictory `_stays_*` pin exists).

## Multi-instance validation

**Required?**: no
**Result**: not-applicable
**Evidence**: NAW-1 is a local-CLI audit tool — single-user, single-machine; no sharing/sync/multi-account surface. The "multi-instance" property is on the WARN's CONSUMER side (the user, who must restart Claude Code AFTER the WARN fires before the next slice's chain runs) — and that is documented in the WARN template + R-18 retirement paragraph, not a runtime check.

## Reality surprises

1. **R-18 did NOT recur at slice-063's own /code-review** — the `subagent_type: code-review` agent spawned cleanly in this Claude Code session. Slice-061 (N=1) + slice-062 (N=2) both hit `Agent type 'code-review' not found`; here it did not. The agent registry session-cache miss is NON-DETERMINISTIC across sessions. NAW-1's methodology-side mitigation (surface the WARN BEFORE the next slice's chain runs) remains structurally correct regardless of runtime non-determinism — but the empirical observation is worth a /reflect lesson: R-18 retirement is methodology-discoverability, NOT runtime guarantee.

2. **/code-review SKILL.md v1 carries the SAME B1 falsifier class that slice-063 retired for NAW-1** — `git diff <base>...HEAD` is commit-vs-commit only, and at /build-slice end slice work is uncommitted in WT (commits at /commit-slice per PCA-1 HARD-STOP terminal contract). The empty-diff path normally writes `Result: NO-CODE-CHANGES` and auto-advances; user-ratified SOAD-1 augmentation at /code-review Step 1 routed around the falsifier with a WT-aware file list. **Slice-064+ candidate**: mirror NAW-1's union-of-three-sources fix to /code-review's own diff resolution. This is a meta-irony — the slice fixing the read-mechanism falsifier on NAW-1's surface immediately surfaced the SAME defect class on /code-review's own surface.

3. **Code-Critic m1 finding** (advisory; not fixed in-band per CRSI-1 v1) — `_resolve_default_branch` at `tools/new_agent_warning_audit.py:177-178` has a SECOND unreachable `try/except FileNotFoundError` block, plus a UX wart where genuinely-missing-`git` environment surfaces `_USAGE_DEFAULT_BRANCH_UNRESOLVABLE` ("Configure an `origin/HEAD` ref or set `init.defaultBranch`") instead of `_USAGE_GIT_MISSING` ("`git` command not found on PATH"). The fix is option (b): drop BOTH `try/except FileNotFoundError` blocks from `_resolve_default_branch` and let propagation handle it via `check()`'s explicit L299-303 handler. Documented for slice-064+ alongside reality surprise #2.

4. **PTFCD-1 `(extended)` recurrence at /build-slice Phase D4** — the slice-054 lesson recurrence (TF-1 + PTFCD-1 Test-path cell must resolve to a real file on disk; `(extended)` annotation suffix breaks resolution). Corrected in-band by removing the suffix from AC#2 + AC#5 Test-path cells per slice-054 lesson. The discipline now: never use parenthesized annotations in TF-1 plan Test-path cells; cite the bare file path; put annotations in Notes section below the table.

## Layered safety checks (VAL-1)

**Layer A — Credential scan**: PASS — 0 secrets detected across 13 changed files (`tools/new_agent_warning_audit.py`, `tests/methodology/test_new_agent_warning_audit.py`, `skills/build-slice/SKILL.md`, `tools/install_audit.py`, `tests/methodology/test_utf8_stdout_regression.py`, `plugin.yaml`, `VERSION`, `pyproject.toml`, `methodology-changelog.md`, `INSTALL.md`, `tests/methodology/test_build_slice_skill.py`, `tests/methodology/test_risk_register_audit_real_file.py`, `tests/methodology/test_methodology_changelog.py`).

**Layer B — Dependency hallucination check**: PASS — 0 import findings. The new audit `tools/new_agent_warning_audit.py` imports only stdlib (`argparse`, `json`, `subprocess`, `sys`, `collections.abc`, `dataclasses`, `pathlib`) + project-internal `tools._stdout`. Test module imports only stdlib + `pytest` + project-internal `tools.new_agent_warning_audit`. Invocation: `--imports-allowlist tests` (per slice-003 ADR-002 convention for pytest namespace test roots).

**Layer C — Walking-skeleton audit (WS-1)**: SKIPPED — slice's mission-brief.md declares `**Walking-skeleton**: false` (NAW-1 is not a walking-skeleton slice; it's a discovery-gate mechanism, not a thin end-to-end vertical).

**Layer D — Exploratory-charter audit (ETC-1)**: SKIPPED — slice's mission-brief.md declares `**Exploratory-charter**: false` (no exploratory testing required for a binary-exit discovery gate).

## Shippability catalog regression check (SRSC-1)

**Pre-catalog gates**:
- **SCMD-1** (`shippability_decoupling_audit`): clean — 63 rows; 568 cited fns — incidental=0, essential_registered=2, essential_unregistered=0, clean=566. Every row carries a prose-free Machine-cmd 6th column.
- **PTFCD-1 sub-mode (b)** (`shippability_path_audit`): clean — 63 rows / 332 test-path tokens — all files and cited functions exist on disk.

**Catalog runner (SRSC-1)**: `$PY -m tools.shippability_runner architecture/shippability.md`

```
Shippability catalog run: 63 row(s), 63 PASS, 0 FAIL
```

**Result**: ALL PASS. No past slice's critical-path test was silently broken by slice-063. The new row #63 PASSES alongside the 62 pre-existing rows. No regressions.

## Audit sweep (Step 6 ungated forward-sync gates re-verified at /validate-slice)

All forward-sync + structural audits re-verified clean post-/build-slice:

- **PMI-1** (`plugin_manifest_audit`): clean — 28 tool modules registered (`plugin.yaml.version` 0.66.0 matches `VERSION` 0.66.0)
- **PVFS-1** (pytest pin): clean — `pyproject.toml [project].version` 0.66.0 matches `VERSION` 0.66.0
- **AVFS-1** (`ai_sdlc_version_forward_sync`): clean — installed `~/.claude/ai-sdlc-VERSION` 0.66.0 matches in-repo `VERSION` 0.66.0
- **MCFS-1** (`methodology_changelog_forward_sync`): clean — in-repo `methodology-changelog.md` content-equal modulo CRLF to installed `~/.claude/methodology-changelog.md`
- **TVFS-1** (`ai_sdlc_tools_version_forward_sync`): clean — installed venv `ai-sdlc-tools` 0.66.0 matches in-repo `VERSION` 0.66.0
- **NAW-1** (`new_agent_warning_audit`, NEW): clean — slice-063 adds zero `agents/*.md` files; audit self-application vacuous-pass
- **BRANCH-1**: clean — on `slice/063-add-build-slice-new-agent-warning`
- **UTF8-STDOUT-1**: clean — 28/28 tools conform (slice-063 added one — `new_agent_warning_audit`)
- **CRP-1**: clean — critique-review.md present
- **PCA-1**: clean — canonical 9-skill chain unchanged
- **BCI-1**: clean — live build-checks files match canonical fixtures
- **STP-1**: clean — R-18 retirement consistent with new `test_r_18_retired_post_slice_063` pin (no contradictory `_stays_*` pin exists)
- **INST-1**: clean — 26 skills / 6 agents / 4 templates / 28 tool modules / methodology v0.66.0
- **TF-1 strict-pre-finish**: clean — 9 rows / 0 violations / 9 PASSING across 5 ACs
- **WIRE-1**: clean — no wiring matrix violations
- **BC-1**: 2 rules surface (BC-PROJ-11 Important + BC-GLOBAL-2 Critical); both vacuously satisfied (BC-PROJ-11 grep `INSTALL.md` for `v?0\.[0-9]+\.[0-9]+` zero matches; BC-GLOBAL-2 session bash log contains zero `git checkout --` / `git restore` / `git stash` operations)
- **Mock-budget lint**: clean — no violations
- **Triage audit**: clean (CLEAN verdict; 13 findings all ACCEPTED-FIXED ratified by user)
- **Critique-review audit**: clean (EXTEND verdict; 3 missed findings all ACCEPTED-FIXED)

## Full pytest suite

**892 passed in 28.44s** (slice-062 baseline 880 + 12 new tests this slice: 7 in `test_new_agent_warning_audit.py` + 1 in `test_build_slice_skill.py` + 1 in `test_risk_register_audit_real_file.py` + 2 in `test_methodology_changelog.py` + 1 added entry to `test_utf8_stdout_regression.py` parametrize tally for the new tool).

## Aggregate verdict

**Result: PASS**. All 5 ACs pass with evidence; VAL-1 layered safety + SCMD-1 + PTFCD-1 + SRSC-1 + full audit sweep + full pytest suite all clean. Per PCA-1, auto-advance to `/reflect` proceeds.
