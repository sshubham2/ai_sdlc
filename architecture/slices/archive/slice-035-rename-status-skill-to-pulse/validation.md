# Validation: Slice 035 rename-status-skill-to-pulse

**Date**: 2026-05-17
**Result**: PASS

Methodology/CLI slice — "real environment" = the live repo state, the installed `~/.claude` tree, the audit tools, the full methodology test suite, and the live skill registry (which refreshed mid-build and now surfaces `/pulse` with the collision-free description + `query-design` pointing at `/pulse`). No device/user/multi-instance dimension.

## Per-criterion results

### AC1: `skills/pulse/SKILL.md` exists, `name: pulse`, `/status` self-refs rewritten, colliding triggers dropped, no `skills/status/`
- **Status**: PASS
- **Evidence**: `grep -m1 '^name:' skills/pulse/SKILL.md` → `name: pulse`; `ls skills/status` → absent ("PASS no skills/status/"); trigger-phrase scan for `'/status'`/`'project status'` → none ("PASS colliding triggers dropped"); registry reload shows `/pulse` with `'/pulse', 'where are we?', 'pulse', 'macro state', 'vault scan'`.
- **Notes**: provenance note "Renamed from /status (slice-035, SRCD-1)" deliberately retained in the description (intentional historical reference, not a collision trigger).

### AC2: `plugin.yaml` declares `- id: pulse`, PMI-1 passes
- **Status**: PASS
- **Evidence**: `tools.plugin_manifest_audit` → "clean. 25 skill(s), 5 agent(s), 22 tool(s); version 0.49.0."

### AC3: `tools/install_audit.py` canonical list contains `"pulse"`, INST-1 passes
- **Status**: PASS
- **Evidence**: `tools.install_audit` → "clean. 25/25 skills, 5/5 agents, 4/4 templates, 22/22 tool modules; methodology v0.49.0."

### AC4: 3 test modules renamed/updated, full suite passes, zero stale `/status` skill refs
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/ -q` → "616 passed in 10.32s". `test_pulse_cadence_enforcement.py` (renamed, 6 `test_pulse_*` fns), `test_risk_register_audit.py::test_pulse_skill_references_rr_1` (fn+path repointed), `test_skill_model_dispatch.py:25` (path constant `skills/pulse/SKILL.md`), `test_install_audit.py` (prose), `test_methodology_changelog.py::test_v_0_49_0_srcd_1_entry_present_in_repo_and_installed` (new entry-pin) all green. Post-edit inventory grep: Bucket A empty.

### AC5: Bucket-B prose + SRCD-1 + 4-part bump + entry-pin + shippability row; CSP-1 + full suite green; Bucket A empty
- **Status**: PASS
- **Evidence**: SRCD-1 `## v0.49.0` entry present in-repo + installed (entry-pin asserts both); 4-part bump verified (`VERSION`=`~/.claude/ai-sdlc-VERSION`=`plugin.yaml.version`=changelog header=`0.49.0`); shippability row #35 added (SCMD-1 + PTFCD-1 pre-gates clean, 35 rows). CSP-1: "not Heavy mode … Skipped." — this IS the green state for a Standard-mode project (CSP-1 self-skips outside Heavy; mission-brief "CSP-1 stays green" satisfied). VAL-1 layers: "0 secret(s), 0 import finding(s)" clean.

## VAL-1 layered safety checks (Step 5b)
- **Layer A (credential scan)**: PASS — 0 secrets
- **Layer B (dependency hallucination)**: PASS — 0 import findings (`--imports-allowlist tests`)

## WS-1 / ETC-1 / TF-1
- N/A — mission-brief declares `Test-first: false`, `Walking-skeleton: false`, `Exploratory-charter: false`; all three audits default-off / clean.

## Multi-instance validation
**Required?**: no (no multi-user / multi-device / multi-account surface — pure identifier rename)
**Result**: not-applicable

## Shippability catalog regression check (Step 5.5)
- **Pre-gates**: SCMD-1 clean (35 rows; incidental=0); PTFCD-1 clean (227 test-path tokens, all exist)
- **Catalog run**: **35/35 PASS**
- Row #28 initially reported FAIL under an ad-hoc outer-backtick-only runner — re-run with correct SCMD-1 per-`;`-segment backtick-strip → PASS (26 passed + 2 passed). This is the documented R-8 multi-segment-row runner footgun (slice-031/032/033 lesson), NOT a slice-035 regression. The SCMD-1 pre-gate (which passed) confirms the catalog row itself is well-formed.
- New row #35 (slice-035 SRCD-1 durable guard) PASS: 20 passed.

## Reality surprises
- None affecting the slice. Re-confirmed (not new): the ad-hoc Step-5.5 runner's outer-backtick-only strip false-FAILs the lone multi-segment row #28 — R-8, already open in the risk register, runner contract still unpinned. No new risk; no action required by this slice.
