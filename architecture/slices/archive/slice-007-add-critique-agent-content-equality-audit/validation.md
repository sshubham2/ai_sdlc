# Validation: Slice 007 add-critique-agent-content-equality-audit

**Date**: 2026-05-10
**Result**: PASS

## Per-criterion results

### AC1: in-repo agents/critique.md byte-equal with installed ~/.claude/agents/critique.md

- **Status**: PASS
- **Evidence**:
  - `python -m tools.critique_agent_drift_audit` exits 0 with output: `CAD-1: clean - agents/critique.md byte-equal across in-repo (<HOME>\ai_sdlc\agents\critique.md) and installed (<HOME>\.claude\agents\critique.md); sha256: af6ee94db810d717...`
  - PowerShell sha256 cross-check: `(Get-FileHash agents/critique.md).Hash` and `(Get-FileHash $env:USERPROFILE\.claude\agents\critique.md).Hash` both return `AF6EE94DB810D717FCCFBCF364813834D5BBC06E5A1B1160E9EDB300EA748C7B` (full hash)
- **Notes**: Phase 0 forensic capture confirmed byte-equality at slice start (post-slice-006 sync); Phase 4 forward-sync was a no-op for `agents/critique.md` (no edits in this slice). The audit's self-applicability is confirmed: slice's own ship runs cleanly on slice's own end-state.

### AC2: drift detection fires on artificial byte flip

- **Status**: PASS
- **Evidence**: Real subprocess invocation against tmp_path fixture (NOT real files):
  - Seeded `tmp/repo/agents/critique.md` with bytes `"version A\n"` (sha256 `fe660b75d08ad1ca...`); seeded `tmp/claude/agents/critique.md` with `"version B (drifted)\n"` (sha256 `4d781a6783ef57ae...`)
  - Ran `python -m tools.critique_agent_drift_audit --repo-root tmp/repo --claude-dir tmp/claude` → exit 1 (drift detected)
  - Output: `1 CAD-1 violation(s):\n  [Important] (content-drift)\n    content-drift between in-repo and installed agents/critique.md.\n  in-repo:   <tmp>/repo/agents/critique.md (sha256: fe660b75d08ad1ca...)\n  installed: <tmp>/claude/agents/critique.md (sha256: 4d781a6783ef57ae...)\nPer /critic-calibrate skill prose, the in-repo copy is canonical; forward-sync the in-repo content to ~/.claude/, OR (if installed has content in-repo doesn't) back-sync first per slice-005+006 bidirectional discipline.`
  - pytest `tests/methodology/test_critique_agent_drift.py::test_drift_detection_fires_on_artificial_byte_flip` PASSES
- **Notes**: must-not-defer #1 satisfied — drift output names BOTH paths AND BOTH hashes (sha256 hex prefix shown above). User can act on the failure with the information given.

### AC3: recurrence pattern structurally addressed (3 surfaces — Critic M3 expanded)

#### AC3a: skill prose at `skills/critic-calibrate/SKILL.md` instructs in-repo canonical with forward-sync

- **Status**: PASS
- **Evidence**: pytest `test_critic_calibrate_skill_prose_instructs_in_repo_canonical_with_forward_sync` PASSES — asserts positive substrings (`'in-repo agents/critique.md'`, `'forward-sync'`, `'tools.critique_agent_drift_audit'`) present AND negative substring (`'To apply, edit ~/.claude/agents/critique.md'` — the OLD prose's unique signature) NOT present.
- **Notes**: Negative substring tightened post-Critic-mid-slice-deviation: initial substring `"edit `~/.claude/agents/critique.md`"` (with backticks) false-positive matched the legitimate line-99 explanatory text; tightened to the OLD prose's unique-without-backticks signature.

#### AC3b: audit CLI exit-code contract (0 clean / 1 drift / 2 missing)

- **Status**: PASS
- **Evidence**: Three real subprocess invocations:
  - Clean state: identical content on both sides → exit 0 (validated above in AC #1)
  - Drift state: different content → exit 1 (validated above in AC #2)
  - Path-missing: installed agents/critique.md absent → exit 2 with `path-missing` substring in output
  - pytest `test_critique_agent_drift_audit_cli_exits_0_on_clean_1_on_drift_2_on_missing` PASSES (parametrized across all 3 states)

#### AC3c: --repo-root sanity-check refusal (Critic M3)

- **Status**: PASS
- **Evidence**: Real subprocess invocation:
  - `python -m tools.critique_agent_drift_audit --repo-root <tmp/bad_repo>` (no plugin.yaml, no INSTALL.md)
  - Exit: 2
  - Output: `1 CAD-1 violation(s):\n  [Important] (usage-error)\n    --repo-root '<tmp>/bad_repo' does not appear to be an AI SDLC source root (missing: <tmp>/bad_repo/plugin.yaml, <tmp>/bad_repo/INSTALL.md). Refusing to compare against potentially stale `build/lib/` shadow or arbitrary directory. Pass --repo-root <ai-sdlc-source> explicitly.`
  - pytest `test_repo_root_without_plugin_yaml_or_install_md_exits_usage_error` PASSES
- **Notes**: must-not-defer #7 satisfied — `--repo-root` sanity-check refusal works as designed; output names which sentinel files are missing.

### AC4: methodology-changelog v0.22.0 / CAD-1 entry present in BOTH locations + VERSION/ai-sdlc-VERSION at 0.22.0

- **Status**: PASS
- **Evidence**:
  - In-repo `methodology-changelog.md` line 37: `## v0.22.0 — 2026-05-10`; line 39: `Adds **CAD-1** — Critic Agent Drift detection.`; line 47: `- **CAD-1 — Critic Agent Drift detection**`
  - Installed `~/.claude/methodology-changelog.md` line 37 + 39 + 47: identical content (forward-synced; sha256 `FD6BBC0241F03396` both sides)
  - In-repo `VERSION`: `0.22.0`
  - Installed `~/.claude/ai-sdlc-VERSION`: `0.22.0` (file rename per `INSTALL.md:141`)
  - pytest `test_v_0_22_0_cad_1_entry_present_in_repo_and_installed` PASSES (bidirectional read)
- **Notes**: Per Critic B1 fix — in-repo file is `VERSION` (no prefix); the `ai-sdlc-` prefix is added at install. Both files at `0.22.0` post-build. Forward-sync executed in Phase 4 with sha256 MATCH verification.

### AC5: PMI-1 audit returns 0 violations post-build (slice-006 escape closed)

- **Status**: PASS
- **Evidence**:
  - Pre-slice state (verified empirically at /critique time per Critic B2): `python -m tools.plugin_manifest_audit --root .` exited 1 with `plugin.yaml version '0.20.0' does not match VERSION file '0.21.0'` — slice-006 escape was live.
  - Post-build state: `python -m tools.plugin_manifest_audit --root .` exits 0 with output: `PMI-1 plugin manifest audit: clean. 24 skill(s), 5 agent(s), 15 tool(s); version 0.22.0.`
  - pytest `test_plugin_yaml_version_matches_version_file_at_0_22_0` PASSES (asserts `plugin.yaml.version == VERSION-content == '0.22.0'`)
- **Notes**: Slice-006 escape closed atomically. `_CANONICAL_TOOLS` 14 → 15 (added `tools.critique_agent_drift_audit`); `plugin.yaml.tools` list 14 → 15 (added with rule `CAD-1`); paired test `test_canonical_tools_match_plugin_yaml` confirms parity. Per Critic B2: without AC #5 gate, the slice-006 escape would have silently persisted.

## Multi-instance validation
**Required?**: no — single-machine methodology tooling slice; no multi-user / multi-device / multi-account flows
**Result**: not-applicable
**Evidence**: slice scope is content-equality between two paths on the same machine; no concurrency, no remote calls, no shared state across machines.

## VAL-1 layered safety checks (Step 5b)

- **Layer A (credential scan)**: 0 secrets detected. Files scanned: `tools/critique_agent_drift_audit.py`, `tests/methodology/test_critique_agent_drift.py`, `tests/methodology/test_methodology_changelog.py`, `skills/critic-calibrate/SKILL.md`, `methodology-changelog.md`, `VERSION`, `plugin.yaml`, `tools/install_audit.py`, `architecture/shippability.md`. No allowlist needed.
- **Layer B (dependency hallucination)**: 0 hallucinated imports detected. With `--imports-allowlist tests` flag (per slice-003 lesson + slice-004/005/006 reuse), the check resolves all top-level imports cleanly: `subprocess`, `sys`, `pathlib`, `pytest`, `argparse`, `hashlib`, `json`, `dataclasses` (all stdlib); `yaml` (declared as `pyyaml` in pyproject.toml; resolved via aliases); `tests.methodology.conftest` (internal package, allowlisted via `--imports-allowlist tests`); `tools.install_audit` (auto-resolved via `[tool.setuptools] packages = ["tools"]` per VAL-1 Layer B's setuptools-packages auto-read).
- **"Validate using your own ship" pattern N=5 stable**: slice-003 + slice-004 + slice-005 + slice-006 + slice-007 all use the slice's own `--imports-allowlist tests` flag at /validate-slice's VAL-1 Layer B. Pattern is now standard practice.

## WS-1 walking-skeleton audit (Step 5c)

Default-off — `mission-brief.md` declares `Walking-skeleton: false`. Skipped.

## ETC-1 exploratory-charter audit (Step 5d)

Default-off — `mission-brief.md` declares `Exploratory-charter: false`. Skipped. Slice scope is internal methodology tooling with no UX surface; no exploratory missions warranted.

## Shippability catalog regression check (Step 5.5)

Catalog rows 1-7 run:

| # | Slice | Tests | Result | Runtime |
|---|-------|-------|--------|---------|
| 1 | slice-001-diagnose-orchestration-fix | 30 | PASS | 1.72s |
| 2 | slice-002-fix-diagnose-contract-and-cwd-mismatch | 4 | PASS | 0.04s |
| 3 | slice-003-add-val-1-imports-allowlist | 3 | PASS | 0.05s |
| 4 | slice-004-fix-rr1-audit-docstring-or-regex | 4 | PASS | 0.04s |
| 5 | slice-005-add-bc-1-keyword-precision | 5 | PASS | 0.09s |
| 6 | slice-006-update-critic-with-cross-cutting-conformance-dimension | 8 | PASS | 0.06s |
| 7 | slice-007-add-critique-agent-content-equality-audit | 8 | PASS | 0.99s |

**Total**: 62 tests, **62 PASS, 0 FAIL** in **3.0s** (well under 2-minute target).

No regression introduced by slice-007 against any past slice's critical path.

## Reality surprises

- **Em-dash → cp1252 byte 0x97 on Windows console** (build-time DEVIATION-2): the audit's "clean" output initially used em-dash (`—`) which Python encoded as cp1252 byte 0x97 on Windows; subprocess.run with `text=True, encoding="utf-8"` couldn't decode it and emitted `PytestUnhandledThreadExceptionWarning`. The test still passed (subprocess returncode is captured separately from stdout), but the warning is a flake-risk for CI. Replaced em-dash with regular hyphen at build time. **Generic Python-on-Windows lesson**: methodology tooling that runs under pytest with subprocess capture should emit ASCII-only output OR set `PYTHONIOENCODING=utf-8` in the subprocess env. Possible BC-1 promotion candidate if it recurs in slice-008+.

- **Prose-pin negative substring false-positive on legitimate context** (build-time DEVIATION-1): the regression-guard substring needs to be unique to the deprecated prose block, not generic enough to also match legitimate negative statements. The line at `skills/critic-calibrate/SKILL.md:99` contains the literal `edit \`~/.claude/agents/critique.md\`` as part of "skill PRODUCES proposals. It does NOT edit `~/.claude/agents/critique.md` itself" — a CORRECT statement, but my initial regression-guard substring matched it. **Generic test-pin lesson**: when writing negative-substring tests, choose substrings that are unique to the deprecated content's surrounding phrasing (e.g., "To apply, edit ..." which only appears in the OLD action block), not just the keyword that motivated the rule.

- **Slice-006 PMI-1 escape was live at slice-007 start** (Critic B2 verified): `plugin.yaml.version='0.20.0'` while `VERSION='0.21.0'` produced a `version-mismatch` violation. Slice-006's reflection.md "Vault updates made" claimed methodology v0.21.0 was synced, but the plugin.yaml.version field was missed. This is a slice-006 escape captured here (not a slice-007 problem) — slice-007 corrects it as a byproduct (atomically bumping both to `0.22.0`) AND adds AC #5 + TF-1 row to gate the fix. Worth noting in slice-007 reflection's "Discovered" + calibration log: cross-cutting-conformance Dim 9 sub-class **"plugin.yaml.version vs VERSION drift across version bumps"** is a refinement of the existing N=2 sub-class (slice-006 DEVIATION-1+2 + slice-007 Critic B1 = N=2; slice-006 PMI-1 escape adds a third occurrence of related cross-cutting class — should it be promoted?).

- **All 8 Critic findings VALIDATED at /validate-slice**: every disposition ACCEPTED-FIXED inline at /critique resolved correctly at validate-time. No FALSE-ALARM, no OVERRIDE-MISJUDGED, no NOT-YET. Voluntary-Critic ROI on cross-cutting tooling slices is now N=7/7 paid off, with 5 of 7 catching design-stage failures (added slice-007 Critic B1 in-repo `VERSION` vs `ai-sdlc-VERSION` rename mismatch fatal catch — would have failed AC #4 at /build-slice T-late OR shipped a pyproject-table contradiction across the design's reference to a nonexistent in-repo file). Methodology pattern continues hardening.
