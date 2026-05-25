# Validation: Slice 001 diagnose-orchestration-fix

**Date**: 2026-05-09
**Result**: PASS (all 6 ACs verified with evidence; AC #6 confirmed by end-to-end /diagnose run on `<HOME>/<private-project>`)

## Per-criterion results

### AC #1: Subagents return text-only as 4-backtick fenced blocks; do NOT call Write

- **Status**: PASS
- **Evidence**:
  - 5 prose-pin tests in `tests/skills/diagnose/test_skill_md_pins.py` all pass:
    - `test_skill_md_uses_out_not_output` — `--output` absent, `--out` present
    - `test_skill_md_invokes_write_pass` — `write_pass.py` + `--raw-file` referenced in Step 5
    - `test_skill_md_subagents_instructed_no_write` — phrase "do not call Write" present, "writes 3 files" absent
    - `test_skill_md_caps_respawn_attempts` — "3 attempts" + ".failed.raw" pinned
    - `test_no_pass_template_uses_output_flag` — regression guard
  - Spot-check of `skills/diagnose/SKILL.md` Step 5 confirms the contract reads: "Each subagent receives template + schema + paths embedded in its prompt and returns three 4-backtick fenced text blocks (`section`, `findings`, `summary`) in its final message; it does NOT call Write, Bash, or python."
- **Notes**: AC #1's verification pattern (grep-for-no-Write, exit code, 3 fence presence) is exercised end-to-end against a real subagent only in AC #6's smoke run.

### AC #2: write_pass.py parses, normalizes, validates, writes 3 files via yaml.safe_dump; non-zero exit on failure

- **Status**: PASS
- **Evidence**:
  - 10 unit tests in `tests/skills/diagnose/test_write_pass.py` all pass:
    - `test_writes_three_files_for_valid_input` — full happy path
    - `test_missing_required_field_exits_nonzero` — exits 1 with "missing" in stderr
    - `test_yaml_safe_dump_quotes_colons` — strings with colons round-trip cleanly
    - `test_section_block_with_nested_triple_backticks_parses_correctly` — 4-backtick outer fence (B1) + nested 3-backtick content
    - `test_missing_fence_exits_two` — parse-time exit code 2
    - `test_empty_findings_block_treated_as_empty_list` — parametrized over 5 input variants (m1)
  - Manual smoke from build phase (recorded in `build-log.md`): hand-crafted valid 4-backtick raw → `write_pass.py` exit 0 → 3 files written under `<tmp>/sections/`, `<tmp>/findings/`, `<tmp>/summary/`.
- **Notes**: stdin path was intentionally dropped per triage M4; only `--raw-file` is supported. CLI `--help` confirms.

### AC #3: assemble.normalize_finding coerces dict-wrap, flat-string evidence, malformed IDs; ingest-only

- **Status**: PASS
- **Evidence**:
  - 7 unit tests in `tests/skills/diagnose/test_normalize_finding.py` all pass:
    - `test_dict_wrapped_findings_unwrapped` — unwraps `{finding: {...}}`
    - `test_flat_string_evidence_normalized` — flat `[str]` → list of `{path, lines, note}` dicts
    - `test_malformed_id_recomputed_via_per_pass_extractor` — recompute deterministic across calls; ID matches `^F-[A-Z]+-[a-f0-9]{8}$` (B2)
    - `test_unknown_field_dropped_with_warning` — `confidence`/`recommendation` dropped; warnings logged (caplog)
    - `test_load_findings_unchanged_for_already_normalized_yaml` — load path stays strict; normalize_finding NOT called by load_findings (M1)
    - `test_signature_extractors_default_uses_title` — default extractor
    - `test_signature_extractor_03b_duplicates_uses_smallest_evidence_path` — 03b override
- **Notes**: M1's "ingest-only" scoping was explicitly verified; if a future edit accidentally couples normalize_finding to load_findings, the test fails.

### AC #4: assemble.py YAML errors include file + line/column + ±2 lines context; problem_mark fallback

- **Status**: PASS
- **Evidence**:
  - 2 unit tests in `tests/skills/diagnose/test_assemble_errors.py` all pass:
    - `test_yaml_error_includes_file_line_context` — feeds an unquoted-colon YAML; assert stderr contains the file path AND a line-number indicator
    - `test_yaml_error_without_problem_mark_falls_back_gracefully` — monkeypatched `yaml.safe_load` raises bare `YAMLError` (no problem_mark); assert no `AttributeError` and a sensible fallback message
- **Notes**: M2's defensive `getattr(exc, 'problem_mark', None)` confirmed; bare-YAMLError path produces "(line/column unknown)" rather than crashing.

### AC #5: SKILL.md uses --out (not --output); no pass template uses --output

- **Status**: PASS
- **Evidence**:
  - 2 prose-pin tests pass (covered in AC #1's test suite)
  - Direct grep: `Grep("--output", path="skills/diagnose")` returns zero files. Confirmed empty result on 2026-05-09 during validation.
- **Notes**: M5's clarification is reflected — pass templates were already using `--graph`, not `--output`; the only file actually changed for AC #5 was `SKILL.md:55`.

### AC #6: End-to-end smoke — /diagnose on a real target; slice-001 orchestration handles real subagent output correctly

- **Status**: PASS
- **Target**: `<HOME>/<private-project>` (227 source files, full-stack FastAPI/PostgreSQL/Celery + React/TS/Vite, 9 alembic migrations)
- **Evidence**: 4 of 11 analysis subagents launched (01-intent, 02-architecture, 03a-dead-code, 03b-duplicates) before the user halted the run for cost reasons (the orchestration was validated; the remaining 6 + 04 + narrator would be redundant validation evidence). Of the 4 returned:

  | Pass | Subagent outcome | `write_pass.py` | Files written |
  |---|---|---|---|
  | 01-intent | Opus, well-formed 4-backtick fenced blocks despite tool-denial; improvised with Glob | exit 0 | sections/01-intent.md (9602B), findings/01-intent.yaml (4B = `[]\n`), summary/01-intent.md (720B) |
  | 02-architecture | Opus, comprehensive analysis with all 3 fenced blocks | exit 0 | sections/02-architecture.md (11008B), findings/02-architecture.yaml (4B), summary/02-architecture.md (757B) |
  | 03b-duplicates | Opus, contract-compliant honest-empty response under tool-denial | exit 0 | sections/03b-duplicates.md (2951B), findings/03b-duplicates.yaml (4B), summary/03b-duplicates.md (403B) |
  | 03a-dead-code | Sonnet gave up; no fenced blocks in result | **exit 2** with stderr naming missing fences | none — degraded; raw saved to `.tmp/03a-dead-code.failed.raw` |

  **Slice-001's orchestration validated end-to-end on real subagent output:**
  - 4-backtick fence parser correctly extracts blocks from messages with prose preamble (the agents wrote a paragraph of explanation before the fences; the parser ignored the preamble and matched the 4-backtick openers correctly).
  - `yaml.safe_dump` produced parseable YAML for all three success cases (each `findings: []` round-trips cleanly).
  - The retry-cap / degraded-pass path worked as designed: `write_pass.py` exit 2 + `.failed.raw` artifact rather than silently writing junk or looping forever.
  - File counts in the per-pass output match the design (3 files per successful pass).

- **Notes**: The user's prior failing-/diagnose run (2026-05-09 morning) reported "Read denied for `~/.claude/skills/...`" — slice-001 fixed that by embedding templates in subagent prompts. This validation run reproduced the same outcome envelope (subagents had narrow tool allowlists) but with an additional twist not addressed by slice-001 — see "Reality surprises" below.

## Multi-instance validation

**Required?**: no
**Result**: not-applicable
**Evidence**: slice changes a local CLI skill's orchestration; no multi-user / multi-device / sync surface.

## VAL-1 layered safety checks

### Layer A — Credential scan (Critical)

- **Result**: 0 secrets detected
- **Evidence**: `tools.validate_slice_layers` ran on 21 changed files; zero Layer A findings.

### Layer B — Dependency hallucination check (Important)

- **Result**: 6 findings, all DEFERRED with rationale
- **Evidence**:
  ```
  6 import finding(s):
    skills/diagnose/write_pass.py:38 — `from assemble import ...`
    tests/skills/diagnose/test_normalize_finding.py:16, 151 — `from assemble import ...`
    tests/skills/diagnose/test_write_pass.py:20 — `from tests.skills.diagnose.conftest import ...`
    tests/skills/diagnose/test_assemble_errors.py:14 — `from assemble import ...`
    tests/skills/diagnose/test_skill_md_pins.py:11 — `from tests.skills.diagnose.conftest import ...`
  ```
- **Disposition**: DEFERRED — both flagged "packages" are intentional internal references, not pip packages.
  - **`assemble`**: sibling script in `skills/diagnose/`; resolved via `sys.path.insert(0, str(Path(__file__).resolve().parent))` at write_pass.py top + the same insert in `tests/skills/diagnose/conftest.py`. This is the standard pattern for Claude Code skill scripts (which aren't pip packages by design — they're invoked via `python skills/<name>/<script>.py`).
  - **`tests`**: the project's own test tree; pytest discovers it via `tests/skills/diagnose/__init__.py` + `conftest.py`. Not a pip package.

  Both are project-internal references the project knows about. Layer B v1 has no per-project import allowlist (only secret allowlist exists); the canonical resolution per the LINT-MOCK Important pattern is "surface + defer with rationale." Recorded here.

  **Followup candidate (slice-N+):** add a `--imports-allowlist` flag to `tools.validate_slice_layers` so projects can declare known internal imports (e.g., script-style sibling modules). The need surfaced here on /diagnose's own toolchain; will recur for any project that ships scripts-not-packages.

## Reality surprises

**Cwd-mismatch tool denial for spawned subagents** — discovered during AC #6's end-to-end /diagnose run on <private-project>. The slice-001 build was done with TARGET = parent thread's cwd (`<HOME>/ai_sdlc` for the unit-test suite + `mid-slice manual smoke`). For the validation run, TARGET = `<HOME>/<private-project>` — a path *outside* the parent's cwd. Spawned `general-purpose` subagents lost Read, Grep, Bash, and PowerShell access entirely; only Glob remained.

Slice-001 fixed:
- Write denied → orchestrator writes ✓
- Out-of-cwd Read of `~/.claude/templates/...` denied → embed in prompt ✓
- Bash/python denied (for graphify) → known overreach in our contract; relaxed in this run's prompts ✓

Slice-001 did **not** fix:
- **All-tool denial when TARGET ≠ parent cwd.** Subagents cannot Read code files in TARGET when TARGET is a sibling/cousin directory. This is a separate failure mode from the original 2026-05-09 morning regression (which was TARGET = parent cwd, with Write/out-of-cwd-Read/Bash denied).

**Impact on verdict**: AC #6 still PASSES — the slice-001 orchestration *itself* (fence parsing, write_pass.py, retry cap, .failed.raw) handled real subagent output correctly. What the orchestration cannot fix is *what the subagent has access to* in the first place. The validation run produced 3 successful passes (Opus subagents improvised with Glob alone) and 1 cleanly-degraded pass (Sonnet gave up; orchestrator preserved raw + degraded the pass without crashing).

**Slice-002 candidate** (recorded for /reflect): "diagnose on out-of-cwd target" — investigate the cwd-mismatch tool-denial pattern. Possible fixes:
1. Documented constraint: /diagnose must be invoked with cwd = TARGET (matches the SKILL.md Step 1 pattern `TARGET="${1:-$PWD}"` — the default-to-PWD behavior already supports this; we'd just document that explicit-path invocation from a different cwd has known degradation).
2. Pre-cd in the orchestrator: `cd $TARGET` before spawning subagents (Bash's cwd inheritance). Untested whether subagent permissions follow.
3. Pre-compute analysis upfront in the parent thread (graphify queries, file listings, code excerpts) and embed in subagent prompts. Removes subagent tool dependency entirely. Bigger change.

(Recording in validation.md per the validate-slice "Reality surprises" rule. /reflect captures and the user decides whether slice-002 takes this on or it lives in `architecture/risk-register.md` as a known constraint.)

## Shippability catalog regression check

**Status**: skipped — `architecture/shippability.md` does not exist (this is the first slice in this repo's `architecture/`); per skill rule "If the file doesn't exist (first slice, catalog empty): skip this step; `/reflect` will create the catalog."
