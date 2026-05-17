# Slice 007: add-critique-agent-content-equality-audit

**Mode**: Standard
**Estimated work**: 0.5 day (~30–90 min per slice-006 reflection)
**Risk retired**: NEW structural class — in-repo↔installed content drift on `agents/critique.md`. Identified at slice-006 Critic B1: every `/critic-calibrate` ACCEPTED proposal that follows current `skills/critic-calibrate/SKILL.md:108-109` prose creates this drift class. Not in `risk-register.md` because it's a methodology/tooling gap, not a project risk; tracked instead in `architecture/critic-calibration-log.md` and slice-006's reflection.md `Discovered` section.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Close the in-repo↔installed drift loop for `agents/critique.md` so that a future `/critic-calibrate` ACCEPTED proposal cannot silently leave the in-repo canonical source out of sync with the installed working copy. Slice-006's B1 catch was a fatal save against a Dim 9 cross-reference catastrophe; that catch was incidental — voluntary Critic happened to read implementation, not docs. The methodology should not depend on incidental human-Critic discipline for a structural defect that is N=1 visible (slice-006) and N=∞ projected (every future calibration run).

The slice's chosen mechanism (option a: standalone audit / option b: INST-2 extension / option c: skill-prose update / option d: hybrid) is a `/design-slice` decision; this mission brief is option-agnostic about the HOW and pins only the WHAT: drift between in-repo `agents/critique.md` and installed `~/.claude/agents/critique.md` is structurally prevented or detected going forward.

## Acceptance criteria

1. After this slice ships, the in-repo `agents/critique.md` and the installed `~/.claude/agents/critique.md` are byte-equal (sha256 match) — verifiable via a single command documented in the slice's deliverable.
2. A new test in `tests/methodology/` fires an explicit failure when in-repo↔installed `agents/critique.md` content drift is artificially introduced (single-byte flip in a fixture-controlled environment); the test passes with a distinguishable PASS message when content is equal.
3. The recurrence pattern (every `/critic-calibrate` ACCEPTED proposal creates drift) is structurally addressed by the chosen mechanism — verifiable by a prose-pin test against the chosen surface (skill prose AND audit script per `/design-slice` option (d) hybrid; see ADR-006).
4. `~/.claude/methodology-changelog.md` and the in-repo `methodology-changelog.md` carry a new dated entry with rule reference `CAD-1` recording the drift-prevention rule and its validation method. In-repo `VERSION` and installed `~/.claude/ai-sdlc-VERSION` (the install-time-renamed counterpart) both carry `0.22.0` (per Critic B1 — the in-repo file is `VERSION`, not `ai-sdlc-VERSION`; the prefix is added at install per `INSTALL.md:141`).
5. **PMI-1 audit returns 0 violations post-build** — `python -m tools.plugin_manifest_audit --root .` exits 0 with no violations. Closes the slice-006 escape (per Critic B2: pre-slice `plugin.yaml.version='0.20.0'` vs `VERSION='0.21.0'` produces a `version-mismatch` violation; slice-007 atomically bumps both to `0.22.0` AND gates the fix via this AC). Without this AC the design's claim to "fix the slice-006 escape as a byproduct" is unenforced and indistinguishable from another slice-006-style miss.

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0). Statuses progress PENDING -> WRITTEN-FAILING -> PASSING. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish`.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | structural | tests/methodology/test_critique_agent_drift.py | test_in_repo_and_installed_critique_agent_are_content_equal | PASSING |
| 2 | structural | tests/methodology/test_critique_agent_drift.py | test_drift_detection_fires_on_artificial_byte_flip | PASSING |
| 3 | prose-pin | tests/methodology/test_critique_agent_drift.py | test_critic_calibrate_skill_prose_instructs_in_repo_canonical_with_forward_sync | PASSING |
| 3 | structural | tests/methodology/test_critique_agent_drift.py | test_critique_agent_drift_audit_cli_exits_0_on_clean_1_on_drift_2_on_missing | PASSING |
| 3 | structural | tests/methodology/test_critique_agent_drift.py | test_repo_root_without_plugin_yaml_or_install_md_exits_usage_error | PASSING |
| 4 | structural | tests/methodology/test_methodology_changelog.py | test_v_0_22_0_cad_1_entry_present_in_repo_and_installed | PASSING |
| 5 | structural | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_at_0_22_0 | PASSING |

Notes:
- AC #2's "artificial byte flip" must be done via a `tmp_path` fixture: `tmp_path / 'repo' / 'agents' / 'critique.md'` and `tmp_path / 'claude' / 'agents' / 'critique.md'`, invoked via `subprocess.run([..., '--repo-root', str(tmp_path/'repo'), '--claude-dir', str(tmp_path/'claude')])`. NEVER mutate real files. Per Critic M1: `--repo-root` is an EXTENSION beyond `install_audit.py`'s flag set (which has only `--claude-dir`, `--strict`, `--no-strict`, `--json`), not a mirror — design.md Components touched section pins this explicitly. Fixture must seed both paths with synthetic minimal `agents/critique.md` files AND a synthetic `plugin.yaml` + `INSTALL.md` at `tmp_path/repo` (so the new sanity-check refusal doesn't fire on legitimate fixture setup).
- AC #3 has THREE surfaces (option d locked at /design-slice — see design.md ADR-006 + Critic M3 sanity check): (a) the skill prose at `skills/critic-calibrate/SKILL.md` AND (b) the new audit's CLI exit-code contract AND (c) the sanity-check refusal when `--repo-root` lacks `plugin.yaml`+`INSTALL.md`. Per slice-006 schema-pin TWO-surface discipline + Critic M3 third surface, three test rows; all three must PASS for AC #3 to pass.
- Per slice-005 + slice-006 lessons: PENDING -> WRITTEN-FAILING transitions must be genuine (specific error signature pinned, not coincidental exit codes). For row #3a (prose-pin) — per Critic M2, content-based assertion only (NO line-range pin per slice-006 prose-pin precedent): assert positive substrings `'in-repo agents/critique.md'`, `'forward-sync'`, `'tools.critique_agent_drift_audit'` present in `skills/critic-calibrate/SKILL.md` (full file content read); assert NEGATIVE: `'edit ~/.claude/agents/critique.md'` (the OLD prose) NOT present (regression guard against future revert). For row #3b (audit CLI): assert exit codes 0/1/2 distinguishable via subprocess; pin canonical error message in stderr (e.g., `'content-drift'`, `'path-missing'`). For row #3c (sanity-check refusal): assert `subprocess.run([..., '--repo-root', str(tmp_path)])` (tmp_path has no plugin.yaml/INSTALL.md) returns exit 2 with `'AI SDLC source root'` substring in stderr.
- AC #5 (PMI-1 cleanliness): `test_plugin_yaml_version_matches_version_file_at_0_22_0` reads both files via `tests/methodology/conftest.py REPO_ROOT` and asserts `yaml.safe_load(plugin.yaml)['version'] == (REPO_ROOT/'VERSION').read_text().strip() == '0.22.0'`. Distinguishable failure signature per slice-006 lesson: AssertionError naming both observed values.
- Implicit guards (existing tests stay green after the slice): `test_canonical_tools_match_plugin_yaml` (14 → 15 entry); existing PMI-1 audit (`plugin.yaml.version` ↔ in-repo `VERSION` equality at `0.22.0`) — pre-existing test in `tests/methodology/test_plugin_manifest_audit.py` assumed (verify at /build-slice T0). Not new TF-1 rows.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | sha256 byte-equality | `(Get-FileHash agents/critique.md).Hash -eq (Get-FileHash $env:USERPROFILE\.claude\agents\critique.md).Hash` returns `True` (run from a PowerShell session, not via Claude Code's Bash tool wrapper which mishandles `$env:USERPROFILE` expansion). Agent-runnable equivalent: `python -m tools.critique_agent_drift_audit && echo CLEAN`. |
| 2 | drift detection fires | pytest `tests/methodology/test_critique_agent_drift.py::test_drift_detection_fires_on_artificial_byte_flip` PASSES (i.e., the audit/test correctly flags drift in fixture using `tmp_path` per Critic M1 fixture contract — never mutates real files) |
| 3 | recurrence addressed | (a) prose-pin: pytest reads `skills/critic-calibrate/SKILL.md` full content and asserts canonical positive substrings present + canonical negative substring absent (per Critic M2 substring-only contract); (b) audit-CLI: pytest asserts the new audit's `--help` text and exit-code contract via subprocess; (c) sanity-check refusal: pytest asserts `--repo-root` pointed at non-AI-SDLC directory exits 2 with `'AI SDLC source root'` in stderr |
| 4 | changelog entry + version | Both `~/.claude/methodology-changelog.md` and in-repo `methodology-changelog.md` show new dated entry with rule reference `CAD-1`; in-repo `VERSION` and `~/.claude/ai-sdlc-VERSION` both contain `0.22.0` (per Critic B1: file is `VERSION` in-repo, renamed to `ai-sdlc-VERSION` at install per `INSTALL.md:141`). pytest asserts the rule ID appears in both methodology-changelog files. |
| 5 | PMI-1 clean post-build | `python -m tools.plugin_manifest_audit --root .` exits 0 with no violations. Pre-build state: exits 1 with `version-mismatch` (slice-006 escape verified empirically). Post-build: must exit 0 — slice-007 corrects both `plugin.yaml.version` and `VERSION` to `0.22.0` atomically. Plus pytest `test_plugin_yaml_version_matches_version_file_at_0_22_0` PASSES. |

## Must-not-defer

- [ ] Drift detection error message MUST name the drifted file path AND show the divergent sha256 (so the user can act on the failure)
- [ ] The chosen mechanism's invocation (audit command OR skill-prose instruction) MUST be self-applicable: running it on the slice's own end-state returns clean
- [ ] Any new audit script MUST be added to the shippability catalog so future slices catch regressions
- [ ] Bidirectional out-of-repo sync discipline (per slice-005 + slice-006 lesson): if this slice modifies `~/.claude/agents/critique.md`, `~/.claude/methodology-changelog.md`, `~/.claude/ai-sdlc-VERSION`, or `~/.claude/skills/critic-calibrate/SKILL.md`, capture sha256 before/after in `build-log.md`
- [ ] Per slice-006 cross-cutting-conformance lesson (now hardening to N=2 per Critic B1 — the in-repo `VERSION` vs installed `ai-sdlc-VERSION` rename mismatch): when `design.md` writes mechanical tables (forward-sync targets, prerequisites), verify each row against canonical references (INST-1 `_CANONICAL_*` lists, INSTALL.md install-time renames, methodology-changelog "do not copy" lists). DEVIATION-1 + DEVIATION-2 at slice-006 + slice-007 B1 establish the precedent at N=2 — promote to Dim 9 sub-clause refinement at slice reflection.
- [ ] **PMI-1 audit MUST exit 0 post-build** (per Critic B2 — without this gate, the slice-006 escape silently persists). Pre-build state: `python -m tools.plugin_manifest_audit --root .` exits 1 with `version-mismatch ('0.20.0' != '0.21.0')`. Post-build: must exit 0 with `plugin.yaml.version == VERSION == 0.22.0`. Verified at /build-slice mid-slice smoke gate AND pre-finish gate.
- [ ] **`--repo-root` sanity-check refusal** (per Critic M3): the new audit must refuse with exit 2 if `--repo-root` doesn't contain `plugin.yaml` AND `INSTALL.md`. Prevents accidental comparison against `build/lib/` shadow (verified `git status: ?? build/`). Tested via TF-1 row 3c.

## Out of scope

- General-purpose drift detection across ALL installed files (option b INST-2 may extend coverage; broader refactor is out)
- Refactoring `tools/install_audit.py` beyond what option b strictly needs
- Drift detection for vault files (`architecture/...`) — that's `/drift-check`'s domain
- Updating `/critic-calibrate` skill to do automatic forward-sync (only updating prose to instruct correct sync direction; automation is out)
- Retroactive fix of historical calibration runs' drift (slice-006 already back-synced the only known historical drift)

## Dependencies

- Prior slices: [[slice-006-update-critic-with-cross-cutting-conformance-dimension]] — established the in-repo↔installed drift class; performed first bidirectional out-of-repo sync; recorded `tools/install_audit.py` content-equality gap in slice-006 mission-brief Out-of-scope as the deferred structural fix
- Vault refs: `methodology-changelog.md` v0.20.0 INST-1 entry (canonical install conventions); v0.21.0 CCC-1 entry (Cross-Cutting Conformance dimension); `architecture/critic-calibration-log.md` 2026-05-10 User-override entry; `skills/critic-calibrate/SKILL.md:108-109` (the drift-causing prose)
- Risk register: this slice does NOT retire R-1 or R-2 (those remain open); it adds no new risk-register entries (the structural class is methodology-tooling, tracked in calibration log + reflections)

## Mid-slice smoke gate

At ~50% of build, run:

```
$PY = "C:\Users\sshub\.claude\.venv\Scripts\python.exe"
& $PY -m pytest tests/methodology/test_critique_agent_drift.py -v
(Get-FileHash agents/critique.md).Hash
(Get-FileHash $env:USERPROFILE\.claude\agents\critique.md).Hash
```

Expected:
- pytest test_in_repo_and_installed_critique_agent_are_content_equal PASSES (no drift between in-repo and installed)
- pytest test_drift_detection_fires_on_artificial_byte_flip is PENDING or PASSING depending on phase
- The two sha256 hashes are identical

If fails: STOP, diagnose, don't continue. Likely cause: the build accidentally left in-repo and installed out of sync, OR the audit isn't seeing the right paths.

## Pre-finish gate

- [ ] All 4 acceptance criteria PASS with evidence captured in `validation.md`
- [ ] All TF-1 plan rows progressed PENDING -> WRITTEN-FAILING -> PASSING with genuine (non-coincidental) failure signatures
- [ ] Must-not-defer list fully addressed (drift error message specificity, self-applicability, shippability catalog entry, sha256 before/after capture, design.md-table-vs-canonical verification)
- [ ] `/drift-check` passes (vault claims still align with code)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Shippability catalog has slice-007's critical-path test added
- [ ] Bidirectional sync evidence (sha256 before/after for `~/.claude/agents/critique.md` and `~/.claude/methodology-changelog.md`) captured in `build-log.md`
- [ ] If `/design-slice` adds further out-of-repo edits beyond the two listed above, those are also captured per the slice-005 forensic-capture discipline
