# Slice 063: add-build-slice-new-agent-warning

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-18 (mitigating → retired) — Newly-installed Claude Code subagents not hot-loaded into the running session
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

R-18 has recurred N=2 across consecutive slices (slice-061 + slice-062 both hit `/code-review` AGENT-UNSPAWNABLE because slice-060 shipped the agent in the same session). Slice-062's reflection explicitly promoted R-18 from watch-list to **active mitigation nomination** for slice-063, with candidate fix (a) — a methodology-side warning at `/build-slice` Step 6 when the slice diff includes a new `agents/*.md` file — named as cheapest + most generalizable.

This slice ships candidate fix (a): a new audit-tool that detects newly-added agent files in the slice's diff and emits a non-blocking WARN at `/build-slice` Step 6 advising the user to restart Claude Code before invoking the next slice's chain. The mitigation is methodology-side only (no Claude Code platform changes); candidate fix (b) (/code-review error-semantic widening) and (c) (platform hot-reload) remain out of scope.

## Acceptance criteria

1. A new audit tool under `tools/` detects added files matching `agents/*.md` in the slice's git diff against the default branch and exits 0 with a structured WARN line on stdout on hit, exits 0 quietly on miss (non-blocking by design — never exit 1).
2. `skills/build-slice/SKILL.md` Step 6 invokes the new audit as the last warn-only step in the pre-finish gate enumeration; the WARN surfaces in the user-visible Step 6 summary without halting PCA-1 auto-advance.
3. The WARN text names: each new agent file path, the session-restart-before-next-slice recommendation, and the explicit `R-18` risk-register cross-reference.
4. The audit has positive contrast tests covering BOTH source states a new agent file can occupy at Step 6 (untracked-new via `git ls-files --others` AND staged-uncommitted via `git diff --diff-filter=A {base}` per ADR-061 §Decision union-of-three-sources read mechanism), a negative contrast (no `agents/*.md` diff → WARN absent), AND a seam-driven self-application test using the `added_files_resolver` injection seam (per slice-059 TVFS-1 precedent) that remains regression-stable across slice-064+.
5. R-18 status flips `mitigating → retired` in `architecture/risk-register.md` (RR-1 `**Status**:` field-line) with a retirement paragraph citing the new audit as the structural mechanism, preserving slice-061 / slice-062 prior prose verbatim per slice-040 R-10 retirement-precedent.

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0), each AC maps to ≥1 failing test written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_new_agent_warning_audit.py | test_audit_exits_0_on_no_agent_diff | PASSING |
| 1 | unit | tests/methodology/test_new_agent_warning_audit.py | test_audit_exits_0_on_new_agent_diff_with_warn_line | PASSING |
| 2 | structural | tests/methodology/test_build_slice_skill.py | test_build_slice_step_6_invokes_new_agent_warning_audit | PASSING |
| 3 | unit | tests/methodology/test_new_agent_warning_audit.py | test_warn_line_cites_agent_path_session_restart_and_r_18 | PASSING |
| 4 | unit | tests/methodology/test_new_agent_warning_audit.py | test_audit_positive_contrast_synthetic_tmp_repo_untracked | PASSING |
| 4 | unit | tests/methodology/test_new_agent_warning_audit.py | test_audit_positive_contrast_synthetic_tmp_repo_staged | PASSING |
| 4 | unit | tests/methodology/test_new_agent_warning_audit.py | test_audit_negative_contrast_no_diff | PASSING |
| 4 | unit | tests/methodology/test_new_agent_warning_audit.py | test_self_application_audit_against_real_repo_is_clean_or_warn_with_known_agents | PASSING |
| 5 | structural | tests/methodology/test_risk_register_audit_real_file.py | test_r_18_retired_post_slice_063 | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Audit detects added `agents/*.md` and exits 0 with WARN; exits 0 quietly otherwise | `pytest tests/methodology/test_new_agent_warning_audit.py::test_audit_exits_0_on_new_agent_diff_with_warn_line` PASSES; `pytest …::test_audit_exits_0_on_no_agent_diff` PASSES |
| 2 | Step 6 invokes the audit; PCA-1 auto-advance not halted | `pytest tests/methodology/test_build_slice_skill.py::test_build_slice_step_6_invokes_new_agent_warning_audit` PASSES (asserts SKILL.md Step 6 enumerates the audit name); manual review of Step 6 output during dogfood at /build-slice Step 6 |
| 3 | WARN text cites agent path + session-restart + R-18 | `pytest …::test_warn_line_cites_agent_path_session_restart_and_r_18` PASSES (substring assertions on all three anchors) |
| 4 | Positive contrast (untracked + staged) + negative contrast + seam-driven self-application | four pytest tests above PASS — `test_audit_positive_contrast_synthetic_tmp_repo_untracked` (covers `git ls-files --others` source) + `test_audit_positive_contrast_synthetic_tmp_repo_staged` (covers `git diff --diff-filter=A {base}` working-tree-vs-base source) + `test_audit_negative_contrast_no_diff` + `test_self_application_audit_against_real_repo_is_clean_or_warn_with_known_agents` (uses `added_files_resolver` injection seam with controlled fixture set per slice-059 TVFS-1 precedent) |
| 5 | R-18 status flipped to retired | `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open` does NOT list R-18; `… --filter-status retired` lists R-18 with the new audit cited; new `test_r_18_retired_post_slice_063` in `tests/methodology/test_risk_register_audit_real_file.py` PASSES (slice-041 R-4 retirement-precedent housing) |

## Must-not-defer

- [ ] PMI-1 multi-surface fan-out per **BC-PROJ-9** (slice-050) for the new `tools/*.py` module: `plugin.yaml` tool path + `tools/install_audit.py` `_CANONICAL_TOOLS` + `INSTALL.md` "N executable methodology tools" count (×2) + `tests/methodology/test_utf8_stdout_regression.py` `_ROOT_ONLY_TOOLS` argv-cp1252 list + shippability row
- [ ] Pipe-free shippability row per **BC-PROJ-7** (slice-044) — no raw `|` in Description text
- [ ] Methodology-changelog `## v0.66.0` entry + ADR-061 per **MEPD-1 Inclusion heuristic** — slice mints a NEW RULE-ID (NAW-1) per ADR-061's Route A selection; the slice-049/050/054/059/060 new-RULE-ID precedent applies (not the slice-062 N=6 cumulative scope-extension precedent — that is a sibling discipline, not this slice's posture)
- [ ] **5-part PMI-1 atomic bump** 0.65.0 → 0.66.0 per ADR-061 §Decision (slice ships a new `tools/*.py` → matches slice-060 / slice-062 5-part shape, NOT slice-059 4-part shape; TVFS-1 leg required via `$PY -m pip install --upgrade .`)
- [ ] AVFS-1 + MCFS-1 + TVFS-1 forward-syncs (installed `~/.claude/ai-sdlc-VERSION` + installed `~/.claude/methodology-changelog.md` + installed venv `ai-sdlc-tools` 0.66.0) after VERSION bump
- [ ] Non-blocking-by-construction: audit exits 0 on BOTH branches; explicit pytest assertion that `subprocess.run(['$PY', '-m', 'tools.new_agent_warning_audit', '--root', tmp_repo])` returns `returncode == 0` AND a WARN line on stdout when an `agents/foo.md` addition is present (covers both the untracked-file source and the working-tree-vs-base source per ADR-061 §Decision union-of-three-sources read mechanism)
- [ ] Real-corpus self-application per **BC-PROJ-4** / **BC-PROJ-8**: audit runs against slice-063's own diff at Phase B mid-slice smoke and confirms quiet exit (vacuous-pass — slice-063 adds no `agents/*.md`)
- [ ] Audit-vs-real-artifact discipline per **slice-037 law**: empirically run the audit against a synthetic positive fixture before declaring the implementation done

## Out of scope

- **R-18 candidate fix (b)**: `/code-review` SKILL.md `agent-unspawnable` error-semantic widening from "exit 1 HALT" to "WARN + auto-advance with declarative skip". Mentioned in slice-062 reflection L40 as mid-cost alternative; this slice picks ONLY fix (a). If R-18 recurs post-slice-063, slice-064+ can ship fix (b) as additional defense-in-depth.
- **R-18 candidate fix (c)**: Claude Code platform-level agent registry hot-reload. Lives outside this project's surfaces; not actionable from the AI SDLC repo.
- **/code-review v2** (TRI-1 routing + verdict-driven block on /validate-slice + AI-bloat passes): explicitly nominated in slice-060 reflection L37 + slice-062 reflection L38 deferral as the "highest-priority" next slice-063+ candidate, but slice-063 picks R-18 mitigation first because /code-review v2's own /code-review step would hit AGENT-UNSPAWNABLE without R-18 closed first.
- **R-17 BRANCH-1 clean-tree precondition**: separate pipeline-hygiene slice candidate (slice-064+ nomination per slice-062 reflection L39).
- **R-13 OSDG-1 extension to `/slice-candidates`**: lower-priority drift-guard family extension; defer to slice-064+.
- The detection mechanism's choice (git diff vs git status vs cached prior-merge-base diff) — `/design-slice` decides; mission brief specifies WHAT (detection of new `agents/*.md` in slice diff vs default branch), not HOW.

## Dependencies

- Prior slices:
  - [[slice-060-add-code-review-skill]] — shipped the `/code-review` agent that triggered R-18's first observation
  - [[slice-061-fix-install-python-detection-and-prompt-fallback]] — R-18 minted with three candidate fixes (a/b/c); witnessed N=1
  - [[slice-062-extend-r15-corpus-class-closure-scope]] — R-18 N=2 cumulative recurrence empirically confirmed; explicit "ACTIVE slice-063 nomination" promotion from watch-list (reflection.md L40 + L78)
  - [[slice-050-add-avfs1-version-forward-sync-gate]] — BC-PROJ-9 multi-surface fan-out precedent for new `tools/*.py` modules
  - [[slice-059-add-tools-package-version-gate]] — TVFS-1 standalone-tool pattern reusable for the new audit's shape
- Vault refs:
  - [[risk-register.md#R-18]] — risk to retire
  - [[skills/build-slice/SKILL.md]] Step 6 — host surface for new audit invocation
  - [[methodology-changelog.md]] — MEPD-1 Inclusion-heuristic entry
- Risk register: [[risk-register#R-18]] (target retirement)
- Diagnose backlog: zero `SC-NNN` candidates closed by this slice (risk-register-driven, not BCR-1-driven; no `**Closes:** SC-NNN` sentinel)

## Mid-slice smoke gate

At ~50% of build, run:

```
$PY -m pytest tests/methodology/test_new_agent_warning_audit.py -x
$PY -m tools.<new_audit_name>  # against slice-063's own diff
```

Expected: positive + negative pytest contrast tests PASS; running the audit against slice-063's own diff exits 0 quietly (vacuous-pass, no `agents/*.md` in diff). If FAILs: STOP, diagnose, do NOT continue to PMI-1 bump + multi-surface fan-out.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] `tools/test_first_audit.py --strict-pre-finish` PASSES on this slice's mission-brief.md (all rows PASSING)
- [ ] PMI-1 / PVFS-1 / AVFS-1 / MCFS-1 / TVFS-1 audits PASS (per N-part bump decision at /design-slice)
- [ ] BC-1 / BC-PROJ-7 / BC-PROJ-9 audits PASS
- [ ] `tests/methodology/test_build_slice_skill_drift.py` (Mini-CAD-1 / OSDG-1 build_slice variant) PASSES post-SKILL.md edit + forward-sync to `~/.claude/skills/build-slice/SKILL.md` (NOTE: CAD-1 per slice-007/ADR-019 guards `agents/critique.md` content-equality and is NOT relevant to this slice; the build_slice variant is in the Mini-CAD-1 family per slice-021 / slice-007 CAD-1 hybrid lineage)
- [ ] Shippability runner `$PY -m tools.shippability_runner architecture/shippability.md` — 63/63 PASS with new row #63 PASSING
- [ ] PCA-1 chain audit `$PY -m tools.pipeline_chain_audit` PASSES (Step 6 enumeration extended cleanly)
- [ ] `tools/branch_workflow_audit.py` PASSES (slice/063-add-build-slice-new-agent-warning branch matches active slice)
- [ ] Full methodology suite (`$PY -m pytest tests/methodology/ tests/skills/ tests/agents/`) all PASS
- [ ] No new TODOs / FIXMEs / debug prints

## Pipeline position

- **predecessor**: `/reflect` (slice-062)
- **successor**: `/design-slice`
- **auto-advance**: true
- **on-clean-completion**: mission-brief + milestone.md written with candidate confirmed (user picked #1 from ranked structured-options menu at /slice Step 3) → invoke `/design-slice` via Skill tool without waiting for the user.
- **user-input gates** (halt auto-advance):
  - None pending — candidate confirmed at Step 3; no BFRD-1 gate (not a bug fix — risk-register-driven mitigation slice).

> Per PCA-1 (methodology-changelog.md v0.41.0).
