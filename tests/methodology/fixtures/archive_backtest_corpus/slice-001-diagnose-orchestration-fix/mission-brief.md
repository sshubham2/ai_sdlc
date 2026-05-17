# Slice 001: diagnose-orchestration-fix

**Mode**: Standard
**Risk tier**: low — internal tooling, no user-data or external-integration changes
**Critic required**: false (low tier; no auth/contracts/data model/multi-device/external-integration/security triggers — the "contract" introduced is internal between skill orchestrator and its analysis subagents)
**Estimated work**: 1 day
**Risk retired**: regression discovered in the 2026-05-09 session — `/diagnose` fails when subagent permissions are narrower than parent, schema mismatches when subagents can't read the schema file, and YAML parse errors when LLM-written strings contain unquoted colons
**Test-first**: true
<!-- the new `write_pass.py` helper is a clean Python module amenable to TF-1 -->

**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Restructure the `/diagnose` skill so analysis subagents do **analysis only** — they return findings/prose/summary as inline fenced blocks in their result message. The main thread reads pass templates + schema once, runs graphify, and after each subagent returns, invokes a new `write_pass.py` helper that parses the result, normalizes common LLM mis-formattings (dict-wrapped findings, flat-string evidence, malformed IDs), validates against the schema, and writes the three pass output files via `yaml.safe_dump`. This makes `/diagnose` robust to subagent permission boundaries (issue 1), eliminates the schema-mismatch class (issue 2), eliminates unquoted-colon YAML bugs (issue 3), and corrects the `--output`/`--out` flag mismatch (issue 4).

## Acceptance criteria

1. Subagents in `SKILL.md` Steps 5/6 return prose + findings + summary as **4-backtick fenced** text blocks in their result message; they do NOT write files. *Verification (per triage m4): capture one subagent's raw response to `$OUT/.tmp/<pass>.raw`; Grep verifies (a) the three expected 4-backtick fences are present, (b) zero `Write(` references appear, (c) `write_pass.py --raw-file ...` exits 0 and produces three files.*
2. `write_pass.py --pass <name> --out <dir> --raw-file <path>` parses the subagent's raw text, normalizes findings, validates against `assemble.py:REQUIRED_FIELDS`, and writes `sections/<name>.md` + `findings/<name>.yaml` + `summary/<name>.md`. Exits non-zero with a clear stderr error on validation failure. *Stdin support is intentionally absent (per triage M4) — `--raw-file` is the only input path.*
3. `assemble.py` exposes `normalize_finding(raw, pass_name)` that coerces: `findings: <dict>` → list (when subagents wrap), evidence as `list[str]` → list of `{path,lines,note}` dicts, ID not matching `F-<CAT>-<8hex>` → **recomputed via per-pass signature extractor table** (preserves canonical-recipe carryover per `SKILL.md:18`); drops unknown fields with a logged warning. *Per triage M1, this function is called only from `write_pass.py` at ingest-time; `load_findings()` retains current strictness.*
4. `assemble.py` YAML load failures print the offending file, line/column from `yaml.YAMLError.problem_mark` when present, and ±2 lines of surrounding context. *Per triage M2, gracefully falls back to a plain error message when `problem_mark` is absent (bare `YAMLError`).*
5. Graphify command in `SKILL.md` Step 3 uses `--out`, not `--output`; no pass template under `passes/` uses `--output` either. *Per triage M5: pass templates currently use `--graph` rather than `--output`, so this AC already trivially holds for them — only `SKILL.md:55` needs the change. The pin test is a regression guard.*

## Test-first plan

Per **TF-1**. The Python helper + assembler additions are test-first; `SKILL.md` restructure is verified by prose-pin tests + a smoke run.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 2 | unit | tests/skills/diagnose/test_write_pass.py | test_writes_three_files_for_valid_input | PASSING |
| 2 | unit | tests/skills/diagnose/test_write_pass.py | test_missing_required_field_exits_nonzero | PASSING |
| 2 | unit | tests/skills/diagnose/test_write_pass.py | test_yaml_safe_dump_quotes_colons | PASSING |
| 2 | unit | tests/skills/diagnose/test_write_pass.py | test_missing_fence_exits_two | PASSING |
| 2 | unit | tests/skills/diagnose/test_write_pass.py | test_empty_findings_block_treated_as_empty_list | PASSING |
| 2 | unit | tests/skills/diagnose/test_write_pass.py | test_section_block_with_nested_triple_backticks_parses_correctly | PASSING |
| 3 | unit | tests/skills/diagnose/test_normalize_finding.py | test_dict_wrapped_findings_unwrapped | PASSING |
| 3 | unit | tests/skills/diagnose/test_normalize_finding.py | test_flat_string_evidence_normalized | PASSING |
| 3 | unit | tests/skills/diagnose/test_normalize_finding.py | test_malformed_id_recomputed_via_per_pass_extractor | PASSING |
| 3 | unit | tests/skills/diagnose/test_normalize_finding.py | test_unknown_field_dropped_with_warning | PASSING |
| 3 | unit | tests/skills/diagnose/test_normalize_finding.py | test_load_findings_unchanged_for_already_normalized_yaml | PASSING |
| 4 | unit | tests/skills/diagnose/test_assemble_errors.py | test_yaml_error_includes_file_line_context | PASSING |
| 4 | unit | tests/skills/diagnose/test_assemble_errors.py | test_yaml_error_without_problem_mark_falls_back_gracefully | PASSING |
| 5 | prose-pin | tests/skills/diagnose/test_skill_md_pins.py | test_skill_md_uses_out_not_output | PASSING |
| 5 | prose-pin | tests/skills/diagnose/test_skill_md_pins.py | test_no_pass_template_uses_output_flag | PASSING |
| 1 | prose-pin | tests/skills/diagnose/test_skill_md_pins.py | test_skill_md_invokes_write_pass | PASSING |
| 1 | prose-pin | tests/skills/diagnose/test_skill_md_pins.py | test_skill_md_subagents_instructed_no_write | PASSING |
| 1 | prose-pin | tests/skills/diagnose/test_skill_md_pins.py | test_skill_md_caps_respawn_attempts | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Subagents return text-only | Read transcript of one subagent invocation; confirm 3 fenced blocks present; confirm no Write calls |
| 2 | write_pass helper works | Unit tests above + manual: `echo "<sample>" \| $PY skills/diagnose/write_pass.py --pass 03a-dead-code --out /tmp/d` produces 3 files |
| 3 | Normalizer tolerates common LLM mistakes | 4 unit tests above |
| 4 | YAML errors are actionable | Feed assemble.py a findings YAML with an unquoted colon; assert stderr matches expected pattern |
| 5 | Graphify flag fixed | Grep `--output` in `skills/diagnose/SKILL.md` and `skills/diagnose/passes/` returns nothing |
| 6 | End-to-end smoke (manual) | Run `/diagnose` on a small target repo; verify `diagnose-out/` contains 11×3 + 1 (overview) = 34 files; assemble.py succeeds; `diagnosis.html` opens in browser |

## Must-not-defer

- [ ] `write_pass.py` validates **every** field in `REQUIRED_FIELDS`, not a subset
- [ ] `write_pass.py` uses `yaml.safe_dump(..., sort_keys=False, allow_unicode=True, default_flow_style=False)` — explicit, no surprises
- [ ] `SKILL.md` call-out: `~/.claude/skills/diagnose/` is the install path; edits go to `C:\Users\sshub\ai_sdlc\skills\diagnose\` and require an INSTALL.md re-run to take effect (consistent with INST-1)
- [ ] `write_pass.py` handles empty findings (`[]`) cleanly — pass 01 produces no findings and must still write a parseable YAML file
- [ ] Re-run `tools.install_audit --strict` post-INSTALL.md to confirm canonical inventory still clean

## Out of scope

- Framework-aware orphan filter for pass 03a (slice-002)
- Changes to `~/.claude/agents/diagnose-narrator.md` (it worked; leave it alone)
- HTML styling / `assemble.py` rendering changes
- New analysis passes
- Migrating existing `diagnose-out/` from prior runs (re-runs regenerate everything; only `diagnosis.html` carries state across runs and that's untouched)
- Adding `write_pass.py` to `tools/install_audit.py` canonical tool list (it lives under `skills/`, not `tools/`; install_audit only validates `tools/`)

## Dependencies

- INST-1 (skill source-vs-install separation) — must edit source, re-run INSTALL.md after
- `assemble.py:REQUIRED_FIELDS` — `write_pass.py` imports this, NOT a separate copy (prevents drift)
- `~/.claude/skills/diagnose/schema/finding.yaml` — read once by main thread, embedded in subagent prompts

## Mid-slice smoke gate

After write_pass.py + its unit tests pass, before tackling SKILL.md restructure:

```powershell
$PY = "C:/Users/sshub/.claude/.venv/Scripts/python.exe"
& $PY -m pytest tests/skills/diagnose/ -v
# Manual: feed write_pass.py a hand-crafted "good" subagent output via --raw-file (stdin not supported per M4)
"<good 4-backtick fenced output>" | Out-File -Encoding utf8 $env:TEMP\diag-good.txt
& $PY skills/diagnose/write_pass.py --pass 01-intent --out $env:TEMP\diag-test --raw-file $env:TEMP\diag-good.txt
ls $env:TEMP\diag-test\sections, $env:TEMP\diag-test\findings, $env:TEMP\diag-test\summary
```

Expected: all unit tests pass; both manual runs succeed/fail as expected.

If this fails: STOP. The helper contract is wrong; restart helper design before touching SKILL.md.

## Pre-finish gate

- [ ] All 5 ACs PASS with evidence in validation.md
- [ ] Test-first audit passes: `$PY -m tools.test_first_audit --strict-pre-finish`
- [ ] Must-not-defer list fully addressed
- [ ] Source files updated in `C:\Users\sshub\ai_sdlc\skills\diagnose\` (NOT in `~/.claude/skills/`)
- [ ] INSTALL.md re-run; `python -m tools.install_audit --strict` clean
- [ ] End-to-end `/diagnose` smoke run on a small target repo produces complete `diagnose-out/`
- [ ] `git diff` clean of debug prints, TODOs, FIXMEs
