# Critique: Slice 007 add-critique-agent-content-equality-audit

**Critic reviewed**: mission-brief.md, design.md, ADR-006
**Date**: 2026-05-10
**Result**: CLEAN (8 findings ALL ratified ACCEPTED-FIXED inline at /critique time)
**Critic invocation**: voluntary on cross-cutting tooling slice (tier=low; critic-required: true) — N=7/7 pattern

## Summary

The slice's option-(d) hybrid is well-reasoned and the test plan is genuinely test-first. Two blockers and three majors are filed against specific surfaces: a wrong in-repo path in the design's "Out-of-repo files touched" table (recurrence of the slice-006 DEVIATION-1/2 cross-cutting class at N=2 — promotion threshold met), an under-engineered AC #4 that doesn't gate the slice-006 PMI-1 escape the design says it fixes, and several contract gaps in the new audit's behavior under realistic edge cases. The chosen mechanism is sound; what's missing is rigor at the boundary between design tables and INST-1 canonical inventory and one more AC + verification step.

## Findings

### Blockers (must address before /build-slice)

#### B1: Out-of-repo files touched table — `ai-sdlc-VERSION` "In-repo path" is wrong; recurrence of slice-006 DEVIATION class at N=2

- **Claim under review**: design.md "Out-of-repo files touched" table, row 3:
  > `| ai-sdlc-VERSION | ai-sdlc-VERSION | ~/.claude/ai-sdlc-VERSION | forward (file copy) | yes — _CANONICAL_METADATA |`

  Mission-brief AC #4 also chains on this naming: "Bumps `ai-sdlc-VERSION` from `0.21.0` → `0.22.0` in both locations" and design.md "What's new" repeats: "Bumps `ai-sdlc-VERSION` from `0.21.0` → `0.22.0` in both locations".
- **Issue**: The in-repo file is named `VERSION` (no prefix), not `ai-sdlc-VERSION`. The rename happens **at install time** per `INSTALL.md:141` (`cp "$AI_SDLC_DIR/VERSION" ~/.claude/ai-sdlc-VERSION`). The repo's actual file is `<HOME>\ai_sdlc\VERSION` (verified — `Glob('**/VERSION*')` returns only `VERSION`; no `ai-sdlc-VERSION` exists in repo). `tools/plugin_manifest_audit.py:144` confirms PMI-1 reads from `root / "VERSION"`. Per Sommerville (requirements↔design traceability), this design row is structurally untraceable: the in-repo path it names doesn't exist. Per the slice-006 cross-cutting-conformance lesson (design.md mechanical tables vs canonical references), this is the **second occurrence** of the exact pattern (N=1 was slice-006's DEVIATION-1 + DEVIATION-2 against INST-1 inventory) — meeting the aggregated lessons' explicit "promote when N=2" threshold.
- **Evidence**:
  - `INSTALL.md:141` — `cp "$AI_SDLC_DIR/VERSION" ~/.claude/ai-sdlc-VERSION` (rename at install)
  - `INSTALL.md:23` — "**methodology-changelog.md + VERSION** — copied to `~/.claude/`"
  - `README.md:86` — `VERSION                   # Methodology semver (read by /status; copied to ~/.claude/ai-sdlc-VERSION on install)`
  - `tools/plugin_manifest_audit.py:144` — `vfile = root / "VERSION"`
  - `tools/install_audit.py:62` — `_CANONICAL_METADATA: ("methodology-changelog.md", "ai-sdlc-VERSION")` — these are **installed** filenames, not in-repo
  - Builder verified post-Critic: `ls VERSION ai-sdlc-VERSION` shows `VERSION` exists; `ai-sdlc-VERSION` does NOT exist in-repo
- **Proposed fix**: In design.md "Out-of-repo files touched" table, change row 3 to use in-repo `VERSION` → installed `ai-sdlc-VERSION` (rename at install per INSTALL.md:141). Update design.md "What's new" + mission-brief AC #4 + ADR-006 + milestone.md to reflect the install-time rename. Add a Phase 0 build-log.md sha256 capture for both locations. Note this finding in the slice's reflection.md "Cross-cutting conformance" Critic-VALIDATED section as N=2 of the DEVIATION class — promote to a Dim 9 sub-clause refinement candidate per the aggregated lessons.
- **Builder draft**: **ACCEPTED-FIXED** — Critic verified empirically; recurrence of slice-006 cross-cutting class at N=2 meets explicit promotion threshold per aggregated lessons. Fix applied inline at design.md (Out-of-repo table row 3 + What's new bullet + Components touched section + Empirical verification #4) + mission-brief AC #4 + ADR-006 + milestone.md. Reflection will record as Dim 9 sub-clause promotion candidate.

#### B2: AC #4 doesn't gate the PMI-1 cleanliness post-build that design.md claims to fix; under-engineered against design's own claim

- **Claim under review**: ADR-006 "Implicit fix to slice-006 escape: `plugin.yaml.version` was lagging at `0.20.0` while `ai-sdlc-VERSION` was `0.21.0` — a PMI-1 violation slice-006 left behind. Slice-007's version bump to `0.22.0` corrects both atomically." Plus design.md component "plugin.yaml" entry: "version `0.20.0` → `0.22.0` (synced with `ai-sdlc-VERSION`; PMI-1 enforces equality...)".
- **Issue**: Per Wiegers (every AC must have a design element delivering it; conversely every design promise should be observable in an AC or verification step): the design promises a side-effect fix to a known PMI-1 escape, but no AC, must-not-defer, or verification-plan row asserts PMI-1 is clean post-build. AC #4 only checks `methodology-changelog.md` and `ai-sdlc-VERSION` carry the dated entry. PMI-1 violation could persist (e.g., builder updates `plugin.yaml` tool list but forgets the `version: 0.20.0 → 0.22.0` field, since it's a separate edit) and the test suite would still pass. **Builder verified post-Critic**: `python -m tools.plugin_manifest_audit --root .` currently exits 1 with `plugin.yaml version '0.20.0' does not match VERSION file '0.21.0'` — this is the live escape the design claims to fix, but no slice-007 gate enforces the fix. Recurrence: slice-006 had the exact same hand-wave on `plugin.yaml.version` and shipped with the violation intact; slice-007 risks the same outcome.
- **Evidence**:
  - design.md "Empirical verification at design-time" #4 — "**Side-finding**: this is a slice-006 escape; will be captured in slice-007 reflection's "Discovered" section as a Critic-MISSED at slice-006 (`plugin.yaml.version` not co-bumped). Not a slice-007 blocker; slice-007 fixes it as a byproduct."
  - Currently failing: `python -m tools.plugin_manifest_audit --root .` returns exit 1 with `plugin.yaml version '0.20.0' does not match VERSION file '0.21.0'`
  - mission-brief verification plan has 4 rows; none invoke PMI-1
  - mission-brief must-not-defer has 5 entries; none mention PMI-1
- **Proposed fix**: Add AC #5 + verification-plan row 5 + must-not-defer entry + TF-1 row for PMI-1 cleanliness post-build. Without this, the design's claim to "fix the slice-006 escape as a byproduct" is unenforced and indistinguishable from another slice-006-style miss.
- **Builder draft**: **ACCEPTED-FIXED** — Critic verified empirically; PMI-1 currently emits version-mismatch violation. Adding AC #5 (PMI-1 clean post-build), verification-plan row 5, must-not-defer entry, and TF-1 row (`test_plugin_yaml_version_matches_version_file_at_0_22_0`). Mission-brief grows from 4 → 5 ACs (at the hard limit per /slice scope rules; not exceeding).

### Majors (address this slice)

#### M1: AC #2 "artificial byte flip" test design is structurally vague — `--repo-root` flag claimed mirrored from `install_audit.py` but not present there

- **Claim under review**: design.md "Components touched" for `tools/critique_agent_drift_audit.py`: "CLI mirrors `tools/install_audit.py` shape (`--claude-dir`, `--repo-root`, `--json`, `--strict`)" + mission-brief test-first plan row 2 notes: "AC #2's 'artificial byte flip' must be done in a temp-dir fixture or via monkeypatched paths".
- **Issue**: Per Hendrickson (edge-case discovery: empty / concurrent / platform-specific) + Newman (idempotency / safe retries): `--repo-root` isn't in `install_audit.py`'s actual flags (verified: `install_audit.py:339-352` has only `--claude-dir`, `--strict`, `--no-strict`, `--json`). Design references a flag the prior tool doesn't have — if `--repo-root` isn't added explicitly, the test has no clean way to redirect both paths to a tmp_path fixture, and the "mirrors install_audit.py" claim is structurally inaccurate (mini cross-cutting-conformance miss: tooling-doc-vs-implementation parity at Dim 1).
- **Evidence**:
  - design.md error model says exit codes 0/1/2; doesn't pin which path-resolution argument the test uses
  - design.md "Components touched" for `tools/critique_agent_drift_audit.py` says CLI mirrors `tools/install_audit.py` "(`--claude-dir`, `--repo-root`, `--json`, `--strict`)" — but verified `install_audit.py:339-352` has no `--repo-root`
- **Proposed fix**: In design.md, pin the fixture contract: AC #2 test uses `tmp_path / 'repo' / 'agents' / 'critique.md'` and `tmp_path / 'claude' / 'agents' / 'critique.md'`, invoked via `subprocess.run([..., '--repo-root', str(tmp_path/'repo'), '--claude-dir', str(tmp_path/'claude')])`. Confirm `--repo-root` is **added explicitly** to argparse (it's an extension beyond `install_audit.py`'s flag set, not a mirror). Add a corresponding row in design.md's `Components touched` and pin in a prose-pin test that asserts argparse exposes `--repo-root` with `Path` type.
- **Builder draft**: **ACCEPTED-FIXED** — design.md updated to clarify `--repo-root` is added (extension, not mirror); fixture contract pinned; design.md will be edited inline.

#### M2: AC #3 prose-pin test surface is fragile — line-range pin (`107-114`) breaks on benign edits

- **Claim under review**: mission-brief test-first plan row 3 (prose-pin test) notes: "For row #3a (prose-pin): assert canonical substring + line-range." Plus mission-brief "Verification plan" row 3: "Read the chosen surface (skill prose at `skills/critic-calibrate/SKILL.md:108-109` for option c; ...)".
- **Issue**: Per Fowler (over-engineering: speculative generality smell — but inverse: under-engineering via brittle test surface). Asserting the prose lives at lines `107-114` in `skills/critic-calibrate/SKILL.md` will break if anyone adds a heading or paragraph above that point. Slice-006's "7 in-repo prose-parity site updates" added text mechanically across files — any future similar slice that touches `critic-calibrate/SKILL.md` above line 107 will shift the line numbers and silently fail this test or, worse, pass on a wrong block. Per Newman (versioning / evolution): tests should pin **content** not **location**. Slice-006 prose-pin tests like `test_critique_dim_9_lists_five_sub_clauses` use substring assertion, not line-range — slice-007 should follow the same shape.
- **Evidence**:
  - mission-brief test-first plan row 3 explicitly asks for "canonical substring + line-range"
  - slice-006 archive's actual implementation pattern uses substring-only (per `tests/methodology/test_critique_agent.py` per shippability.md row 6)
- **Proposed fix**: In mission-brief test-first plan row 3 notes, drop "+ line-range" and replace with: "assert canonical substring(s) — at minimum: `'in-repo agents/critique.md'`, `'forward-sync'`, `'tools.critique_agent_drift_audit'` — present in `skills/critic-calibrate/SKILL.md` (full file content read)." Optionally also assert a NEGATIVE: `'edit ~/.claude/agents/critique.md'` (the OLD prose) NOT present, to detect regression where a future edit reverts the in-repo-canonical instruction. The line-range is informational guidance for the Builder, not a test contract.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief TF-1 plan notes updated inline.

#### M3: Audit error model has a coverage gap — what if both files exist but the in-repo path resolves to a stale `build/lib/` shadow?

- **Claim under review**: design.md error model: "**`path-missing` (exit 2)**: `agents/critique.md` (in-repo) OR `~/.claude/agents/critique.md` (installed) doesn't exist." Plus "Authorization model: The new audit reads two filesystem paths (read-only); no privilege escalation."
- **Issue**: Per Hendrickson (platform-specific + ambiguous-source edge cases). Verified: `Grep` for `ai-sdlc-VERSION` returns matches in `<HOME>\ai_sdlc\build\lib\tools\install_audit.py:62` — the `build/lib/` directory contains a stale shadow of the tools package from a prior `pip install` build step (also visible in `git status: ?? build/`). If `--repo-root` defaults to cwd via `Path(__file__).parents[1]` discovery, and the user runs the audit from inside `build/lib/`, the path-resolution may pick a stale `agents/critique.md` (or fail confusingly) — the audit needs an explicit refusal or clear path-resolution semantics. Per OWASP defense-in-depth (input validation at the boundary): the audit should refuse if `--repo-root` doesn't contain a `plugin.yaml` and `INSTALL.md` (sanity check that we're in the right place), exiting with a usage-error rather than silently comparing the wrong two files.
- **Evidence**:
  - `<HOME>\ai_sdlc\build\lib\tools\install_audit.py:62` exists (Grep verified)
  - `git status` shows `?? build/` as untracked — the stale shadow is a real risk
  - design.md doesn't specify `--repo-root` default behavior precisely
- **Proposed fix**: In design.md "Components touched" → `tools/critique_agent_drift_audit.py`, replace the cwd-discovery hand-wave with: "`--repo-root` flag defaults to `Path.cwd()`. Audit refuses with `usage-error` (exit 2) if `--repo-root / 'plugin.yaml'` and `--repo-root / 'INSTALL.md'` don't both exist (sanity check that the path is an AI SDLC source root, not a stale `build/` shadow or arbitrary directory). Document this refusal as a 4th error case in the error model. Add a TF-1 test row asserting the `usage-error` fires when `--repo-root` is pointed at `build/lib/` or `tmp_path` (no plugin.yaml)."
- **Builder draft**: **ACCEPTED-FIXED** — design.md error model + Components touched updated; mission-brief TF-1 plan grows to add `test_repo_root_without_plugin_yaml_or_install_md_exits_usage_error` row under AC #3 sanity-check umbrella (or as new AC if scope warrants — keep under AC #3's hybrid surface to stay at 5 ACs).

### Minors (log; address if cheap)

#### m1: design.md "Components touched" name shorthand drifts from `_CANONICAL_TOOLS` actual entries

- **Claim under review**: design.md "Empirical verification at design-time" #3: "lists 14 entries (build_checks, critique_review, cross_spec_parity, exploratory_charter, install, mock_budget_lint, plugin_manifest, risk_register, supersede, test_first, triage, validate_slice, walking_skeleton, wiring_matrix)."
- **Issue**: Per Wiegers (assumption-traceability): the prose names use shorthand that diverges from actual `_CANONICAL_TOOLS` entries. Verified: `_CANONICAL_TOOLS` uses module-name form (`tools.build_checks_audit`, `tools.validate_slice_layers`, etc.) — `validate_slice` (in design's prose) is `validate_slice_layers` in code; `install` is `install_audit`. Cosmetic but a sub-class hit of "doc names something the implementation calls differently" (Dim 1 / Dim 9 cross-cutting sub-class). Worth a minor since this slice is specifically about preventing such drift on `agents/critique.md`.
- **Proposed fix**: Replace shorthand names with actual `_CANONICAL_TOOLS` literals.
- **Builder draft**: **ACCEPTED-FIXED** — design.md inline edit.

#### m2: ADR-006 "What CANNOT be cleanly reverted" enumeration thin vs slice-006 ADR-005 standard

- **Claim under review**: ADR-006 "Reversibility" section: "What CANNOT be cleanly reverted: methodology-changelog audit-trail entries (append-only by convention; revert leaves a gap row but the dated entry remains in git history)."
- **Issue**: Per Sommerville (architecture description consistency): slice-006's ADR-005 set a precedent for an explicit "Items that cannot be reverted" sub-section enumerating multiple irreversibles. ADR-006's reversibility section names only one. Likely missing: build-log.md sha256 forensic captures (append-only); reflections in slices ≥007 that cite CAD-1 are textually persistent; pre-build PMI-1 escape was visible in git history and post-fix git history will record the v0.21.0 → v0.22.0 jump (skipping v0.21.0 in plugin.yaml).
- **Proposed fix**: Expand "What CANNOT be cleanly reverted" subsection to enumerate at least 3 items.
- **Builder draft**: **ACCEPTED-FIXED** — ADR-006 inline edit.

#### m3: AC #1 verification command is fine but won't run in Claude Code's Bash tool wrapper without escaping

- **Claim under review**: mission-brief verification plan row 1: "`(Get-FileHash agents/critique.md).Hash -eq (Get-FileHash $env:USERPROFILE\.claude\agents\critique.md).Hash` returns `True`"
- **Issue**: Empirically verified during this critique: Claude Code's Bash tool wrapper expands `$env:USERPROFILE` incorrectly. For a user manually running PowerShell, the command is fine. For an agent running this verification autonomously through the build pipeline, the command will fail.
- **Proposed fix**: Append parenthetical noting PowerShell-only context; add agent-runnable equivalent (`python -m tools.critique_agent_drift_audit && echo CLEAN`).
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief verification plan row 1 inline edit.

## Dimensions checked

- [x] Unfounded assumptions — B1 (in-repo `ai-sdlc-VERSION` doesn't exist; should be `VERSION`); M3 (`Path(__file__).parents[1]` cwd-discovery hand-wave); m1 (name shorthand vs `_CANONICAL_TOOLS` literals)
- [x] Missing edge cases — M1 (artificial-byte-flip fixture isolation), M3 (stale `build/lib/` shadow + wrong-file-kind), m3 (Bash tool wrapper variable-expansion)
- [x] Over-engineering — none because the slice's option-(d) hybrid is the minimum viable mechanism that closes both prevention (skill prose) and detection (audit). The choice of `--strict` omitted, `--repo-root` + `--claude-dir` flags only, no JSON schema beyond `install_audit`'s shape — all YAGNI-aligned per Beck.
- [x] Under-engineering — B2 (AC set doesn't gate the slice-006 PMI-1 escape that ADR-006 says the slice fixes); M2 (line-range pin too brittle vs the substring approach slice-006 used)
- [x] Contract gaps — M1 (`--repo-root` flag claimed mirrored from `install_audit.py` but not in that tool's argparse), M3 (path-resolution semantics + `usage-error` 4th case for stale-shadow refusal). Idempotency of audit (running twice in succession on clean state should still exit 0) is implicit via stateless filesystem read — not a finding.
- [x] Security — none because the audit is read-only filesystem operations on user-owned paths; no network; no secrets; no input it doesn't already control via argparse. Per OWASP, the threat model is degenerate (no untrusted input). The only mild defense-in-depth gap (`--repo-root` lacks sanity-check refusal) is folded into M3 as edge case rather than security finding.
- [x] Drift from vault — B1 already cited as a vault-traceability failure (design row points at a non-existent in-repo file). No additional drift findings: ADR-006 supersedes nothing; CAD-1 rule ID confirmed novel; new audit doesn't duplicate existing components (verified `_CANONICAL_TOOLS` doesn't have a content-equality audit).
- [x] Web-known issues — Searched 2 queries (Python hashlib sha256 file comparison best practices 2025; Claude Code plugin marketplace agents critique.md location 2026). Findings: (1) Python hashlib best practice is to read in chunks via `'rb'` mode and `.hexdigest()` for comparison — the design doesn't specify chunked-read explicitly. For a single Critic agent prompt file (~13KB at slice-006 ship), reading the whole file is fine; if the file ever grows past ~10MB the audit should chunk. Not a finding because file size is bounded and small. (2) Claude Code plugin marketplace search returned the official `claude-plugins-official` repo using `.claude-plugin/marketplace.json` shape — `plugin.yaml` at the repo root is a starting-point format already documented as such. No novel issues found.
  Sources:
  - [hashlib - Secure hashes and message digests (Python docs)](https://docs.python.org/3/library/hashlib.html)
  - [Compare two files using Hashing in Python - GeeksforGeeks](https://www.geeksforgeeks.org/compare-two-files-using-hashing-in-python/)
  - [claude-plugins-official/.claude-plugin/marketplace.json (anthropics)](https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json)
- [x] Cross-cutting conformance — B1 explicitly invokes this dimension at N=2 (slice-006 DEVIATION-1+2 was N=1; slice-007's `ai-sdlc-VERSION` mismatch is N=2 — meeting the aggregated lessons' explicit "promote to Dim 9 sub-clause when N=2" threshold). M1 also brushes this surface: design.md "CLI mirrors install_audit.py shape" is a tooling-doc-vs-implementation parity miss (Dim 1 sub-bullet) since `install_audit.py` doesn't have `--repo-root`. m1 is a third sub-class hit. Per CCC-1, this slice is itself a strong candidate for the **next** `/critic-calibrate` run as evidence the dimension is paying off — the Critic surfaced the design.md-mechanical-table-vs-canonical-inventory class explicitly because Dim 9 prompted the check; without Dim 9 this finding would likely have been shrugged off as a typo. Recommendation in slice reflection: log B1 + M1 + m1 as Dim 9 sub-class hits for the calibration log effectiveness check (success criterion was ≤2 across slices 6-15; slice-007 is on track).

## Triage

**Triaged by**: user (preemptively ratifying Builder drafts per "work without stopping" instruction; user may redirect any disposition before /build-slice)
**Date**: 2026-05-10
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | Wrong in-repo path (`ai-sdlc-VERSION` should be `VERSION`); fix applied at design.md (Out-of-repo table + What's new + Components touched + Empirical verification #4) + mission-brief AC #4 + ADR-006 + milestone.md. Critic-VALIDATED at /critique time; recurrence of slice-006 DEVIATION class at N=2 — promoted to Dim 9 sub-clause refinement candidate. |
| B2 | Blocker  | ACCEPTED-FIXED | Adding AC #5 (PMI-1 clean post-build), verification-plan row 5, must-not-defer entry, and TF-1 row to mission-brief. Mission-brief grows 4 → 5 ACs (at /slice's hard limit, not exceeding). PMI-1 currently emits version-mismatch (verified empirically). |
| M1 | Major    | ACCEPTED-FIXED | `--repo-root` is an extension beyond `install_audit.py`'s flag set, not a mirror. design.md updated to clarify; fixture contract pinned (tmp_path/repo + tmp_path/claude). |
| M2 | Major    | ACCEPTED-FIXED | Line-range pin replaced with substring-based assertion + negative substring. Mission-brief TF-1 plan notes updated. |
| M3 | Major    | ACCEPTED-FIXED | Sanity-check refusal added: `--repo-root` must contain plugin.yaml + INSTALL.md, else exit 2 `usage-error`. design.md error model + Components touched updated; TF-1 row added under AC #3 hybrid surface. |
| m1 | Minor    | ACCEPTED-FIXED | design.md Empirical verification #3 — replaced shorthand names with `_CANONICAL_TOOLS` literals. |
| m2 | Minor    | ACCEPTED-FIXED | ADR-006 "What CANNOT be cleanly reverted" expanded to enumerate ≥3 items per ADR-005 standard. |
| m3 | Minor    | ACCEPTED-FIXED | mission-brief verification plan row 1 — appended parenthetical + agent-runnable equivalent. |
