# Design: Slice 001 — diagnose-orchestration-fix

**Date**: 2026-05-09
**Mode**: Standard

> **Reflection-corrected (2026-05-09 evening, post-AC#6)**: the contract phrasing in this design and in the corresponding `SKILL.md` Step 5 + 11 pass-template "Output format" sections — "**Do NOT call Write, Bash, or python**" — was over-strict. The intent was "subagents do not produce output files via Write; the orchestrator handles that." Reality showed (during the AC #6 /diagnose run on `ReportManager_v4`) that pass templates' Method sections REQUIRE Bash/python for graphify queries against `$OUT/graphify-out/`, so blanket-forbidding those tools makes the slice contradict itself. The orchestrator's per-prompt contract during AC #6 had to override this with "no Write to produce output files; Bash/python ALLOWED for graphify queries within OUT". Slice-002 candidate: relax the wording in SKILL.md + 11 pass templates to match. This design is otherwise correct as-shipped.

## What's new

- New python module `skills/diagnose/write_pass.py` (~150 LOC) — parses subagent result text (three **4-backtick** fenced blocks for `section`, `findings`, `summary` per triage B1), normalizes findings, validates against schema, writes three pass output files via `yaml.safe_dump`. CLI: `python skills/diagnose/write_pass.py --pass <name> --out <dir> --raw-file <path>`. **Stdin path was dropped per triage M4** — `--raw-file` is the only input.
- New `normalize_finding(raw, pass_name)` function in `skills/diagnose/assemble.py` — coerces common LLM mis-formattings into schema shape (dict-wrapped findings list, evidence as flat strings, ID not in `F-CAT-hash` form → recomputed via **per-pass signature extractor table** per triage B2). Logs warnings for unknown fields and recoverable mistakes; returns `None` only when the entry is irrecoverable (e.g., no evidence at all). **Per triage M1, this function is called only from `write_pass.py` at ingest-time, not from `load_findings()` — load remains strict.**
- Improved YAML parse error in `assemble.py` `load_findings()` — catches `yaml.YAMLError`, prints the offending file path, `problem_mark.line`/`column`, and ±2 lines surrounding context.
- Restructured `skills/diagnose/SKILL.md` Steps 3, 5, 5.5, 6, 6.5: main thread reads pass templates + schema once, runs graphify (with `--out`, not `--output`), embeds template + schema in subagent prompts, expects fenced text blocks back, invokes `write_pass.py` per pass.
- Pass templates `skills/diagnose/passes/01-intent.md` through `04-ai-bloat.md` (11 files) updated: a new "Output format" section instructs the subagent to return three fenced blocks; the prior "Output files" section is rewritten to reflect that the orchestrator (not the subagent) writes files.
- Tests in new `tests/skills/diagnose/` — 13 tests across 4 test files (write_pass, normalize_finding, assemble_errors, skill_md_pins).

## What's reused

- `skills/diagnose/assemble.py:REQUIRED_FIELDS` — `write_pass.py` imports this directly; single source of truth for the schema field list.
- `skills/diagnose/schema/finding.yaml` — read once by main thread per /diagnose run, embedded in subagent prompts. The schema file itself is unchanged.
- `~/.claude/agents/diagnose-narrator.md` — narrator agent unchanged; still spawned in Step 6.5 with its existing Read/Glob/Grep/Write allowlist (it worked in the failing run).
- `tools/test_first_audit.py` — `/build-slice` already runs this; the same `--strict-pre-finish` gate enforces the Test-first plan.
- `tools/install_audit.py` (INST-1) — re-run after edits to confirm canonical inventory still matches.

## Components touched

### `skills/diagnose/write_pass.py` (NEW)

- **Responsibility**: Take raw subagent text, extract three fenced blocks, normalize + validate findings, write three pass output files via `yaml.safe_dump`. CLI helper invoked once per pass after the subagent returns.
- **Lives at**: `C:\Users\sshub\ai_sdlc\skills\diagnose\write_pass.py` (created by this slice)
- **Key interactions**:
  - Imports `REQUIRED_FIELDS`, `normalize_finding` from `skills/diagnose/assemble.py`
  - Imports `yaml` for `safe_dump`
  - CLI invoked from `SKILL.md` Step 5 via `$PY skills/diagnose/write_pass.py --pass <name> --out $OUT --raw-file <tmp>` (one call per pass; tmp file holds the subagent's raw response text)
- **`--raw-file` contract**: subagent text containing three **4-backtick** fenced blocks demarcated by `` ````section `` ... `` ```` `` , `` ````findings `` ... `` ```` `` , `` ````summary `` ... `` ```` ``. CommonMark length-distinguished closing fence: an opening of N backticks (N≥4) is closed by a line of ≥N backticks. Inner content may freely contain 3-backtick fences (` ```bash `, ` ```yaml `, ` ```markdown ` etc.) without collision. Order doesn't matter; missing blocks → exit 2 with stderr message naming which fence is missing.
- **Exit codes**:
  - `0` — all three files written cleanly
  - `1` — validation failure (missing required field even after normalization, empty `section` or `summary` block)
  - `2` — parse failure (missing fence, malformed YAML inside `findings` fence)

### `skills/diagnose/assemble.py` (MODIFIED)

- **Responsibility**: Existing — composes `diagnose-out/diagnosis.html`. This slice adds two narrow capabilities, no architectural change.
- **Lives at**: `C:\Users\sshub\ai_sdlc\skills\diagnose\assemble.py` (modified)
- **Key interactions**:
  - `normalize_finding(raw, pass_name) -> dict | None` — used by `load_findings()` (existing path) AND by `write_pass.py` (new caller). Single source of normalization.
  - `load_findings()` — now wraps `yaml.safe_load` in try/except, prints actionable error on `yaml.YAMLError` with file + line/column + context.
- **Public surface added**: `normalize_finding` and `_signature_extractors` (private dict mapping pass-name → callable that extracts the canonical signature from a finding dict; default is `lambda f: f["title"]`; `03b-duplicates` overrides to use the lexicographically smallest evidence path). No other module-level changes.
- **M1 scope**: `normalize_finding` is **only called by `write_pass.py`**. `load_findings()` retains its existing strict validation (REQUIRED_FIELDS check; reject unknown structures). This prevents normalization from silently mutating already-validated YAMLs from prior runs.

### `skills/diagnose/SKILL.md` (MODIFIED)

- **Responsibility**: Existing skill orchestrator prose; Steps 3, 5, 5.5, 6, 6.5 restructured to push I/O to main thread.
- **Lives at**: `C:\Users\sshub\ai_sdlc\skills\diagnose\SKILL.md` (modified)
- **Key changes**:
  - **Step 3** — graphify command: `--output` → `--out`. Add: "Read pass templates and the finding schema into memory now (Read tool); they're embedded into subagent prompts in Step 5."
  - **Step 5** — replace "Each subagent receives the template content + paths and writes 3 files" with "Each subagent receives template + schema + paths embedded in its prompt and returns three fenced text blocks (`section`, `findings`, `summary`) in its final message; it does NOT call Write." Add: "After each subagent returns, save its raw text to a tmp file under `$OUT/.tmp/<pass>.raw`, then run `$PY skills/diagnose/write_pass.py --pass <name> --out $OUT --raw-file $OUT/.tmp/<pass>.raw`. The helper writes the three pass files, validates, and exits non-zero on failure (re-spawn that pass)."
  - **Step 5.5** — verification semantics unchanged (still `ls $OUT/sections $OUT/findings $OUT/summary`); the gate now also checks `write_pass.py` exit codes from Step 5.
  - **Step 6** — same restructure for the cross-reference pass (04-ai-bloat). It still reads `findings/03b-duplicates.yaml` and `findings/03d-half-wired.yaml` from disk (those exist after Step 5.5), but its own output flows through `write_pass.py` like the other passes.
  - **Step 6.5** — narrator unchanged; explicit note added that the narrator agent's existing pattern is preserved.

### `skills/diagnose/passes/*.md` (11 files, MODIFIED)

- **Responsibility**: Each pass template gains a new "Output format" section telling the subagent to return three **4-backtick** fenced blocks (per triage B1); the prior "Output files" section is shortened to "the orchestrator writes these from your fenced blocks (don't write them yourself)." Each template also embeds a **5-line schema crib sheet** (per triage m2) instead of the full 3KB schema — saving ~33KB across 11 prompts per /diagnose run.
- **Lives at**: `C:\Users\sshub\ai_sdlc\skills\diagnose\passes\*.md`
- **Key interactions**: Read by main thread once per /diagnose run in `SKILL.md` Step 5 / 6; embedded into the subagent prompt.
- **Note on AC #5 scope (per triage M5)**: pass templates currently use `--graph` rather than `--output` for their graphify invocations. AC #5's "no pass template uses `--output`" already trivially holds for these files; the only file actually changed for AC #5 is `SKILL.md:55`. The pass-template prose-pin test serves as a regression guard, not a fix target.

## Contracts added or changed

### Subagent I/O contract (internal to /diagnose)

This is an **internal** contract — between the main thread orchestrator and its analysis subagents within a single /diagnose invocation. Not a public API.

- **Format**: Three **4-backtick** fenced code blocks in the subagent's final message (per triage B1; 4-backtick outer fences avoid collision with subagent prose containing nested 3-backtick fences for ` ```bash ` / ` ```yaml ` / ` ```markdown ` etc.):
  `````
  ````section
  <markdown prose for sections/<pass>.md — may freely contain ```bash ``` or ```yaml ``` blocks>
  ````

  ````findings
  <YAML list conforming to schema/finding.yaml; or `[]` if no findings>
  ````

  ````summary
  <one-paragraph markdown for summary/<pass>.md>
  ````
  `````
- **Parser contract**: matches `^\`{4,}(section|findings|summary)\s*$` for openers; closes on any line of `^\`{N,}\s*$` where N matches the opener length (per CommonMark §4.5).
- **Defined in code at**: `skills/diagnose/write_pass.py` (parser is the runtime contract); `skills/diagnose/passes/*.md` (subagent's view of the contract — what to produce)
- **Auth model**: N/A (in-process)
- **Error cases**:
  - Missing fence → `write_pass.py` exits 2; main thread re-spawns the pass
  - Empty `findings` block → treat as `[]` (some passes legitimately produce zero findings — pass 01)
  - Empty `section` or `summary` block → exit 1 (every pass must produce prose + summary)
  - Findings YAML doesn't parse → exit 2 with `problem_mark` line/column
  - Findings entry irrecoverable after `normalize_finding` (e.g., zero evidence entries) → exit 1 naming the entry index

### CLI contract for `write_pass.py`

- **Endpoint**: `python skills/diagnose/write_pass.py --pass <name> --out <dir> --raw-file <path>`
- **Defined in code at**: `skills/diagnose/write_pass.py` (argparse)
- **Reads from**: `--raw-file <path>` (required; per triage M4, stdin is intentionally not supported — the orchestrator always passes a file path)
- **Writes to**: `<out>/sections/<pass>.md`, `<out>/findings/<pass>.yaml`, `<out>/summary/<pass>.md` — overwrites if files exist (re-spawn semantics)

## Data model deltas

None. The `finding.yaml` schema is unchanged. `normalize_finding()` adapts to the schema; it doesn't extend it.

## Wiring matrix

Per **WIRE-1**.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `skills/diagnose/write_pass.py` | `skills/diagnose/SKILL.md` Step 5 (Bash invocation per pass; pinned by `test_skill_md_invokes_write_pass`) | `tests/skills/diagnose/test_write_pass.py::test_writes_three_files_for_valid_input` | — |

The new `normalize_finding` function in `assemble.py` doesn't appear as a separate row — it's an additive function within an existing module, not a new module. Its consumer-test wiring is `tests/skills/diagnose/test_normalize_finding.py` (4 tests) and its consumers are `assemble.py:load_findings` (existing) and `write_pass.py` (new).

## Decisions made (ADRs)

- [[ADR-001]] — Diagnose subagent I/O contract: text-only subagent results, main-thread file I/O via `write_pass.py` helper. Reversibility: cheap.

(No further ADRs. The `assemble.py` additions and `write_pass.py` creation are tactical implementations of ADR-001's pattern, not separate architectural decisions.)

## Authorization model for this slice

N/A. /diagnose is a local CLI skill operated by the developer. No multi-user surface introduced or changed.

## Error model for this slice

| Where | Trigger | Behavior |
|-------|---------|----------|
| `write_pass.py` parse | Missing one of the three fenced blocks | Exit 2; stderr names the missing fence + pass name |
| `write_pass.py` parse | YAML inside `findings` fence doesn't parse | Exit 2; stderr prints `yaml.YAMLError.problem_mark` (line, column) + ±2 lines context |
| `write_pass.py` validate | Finding missing required field after `normalize_finding` attempt | Exit 1; stderr names the finding (id/title) + missing field |
| `write_pass.py` validate | Empty `section` or `summary` block | Exit 1; stderr names which fence is empty |
| `assemble.py` load | `yaml.YAMLError` on a `findings/*.yaml` | Print actionable error (file + line + column + context); abort assembly |
| `SKILL.md` Step 5 | `write_pass.py` exits non-zero for any pass | Re-spawn that pass (extends Step 5.5's existing "missing files → re-spawn" semantics to cover non-zero exit) |
| `SKILL.md` Step 5 | Subagent doesn't include any of the fenced blocks at all (e.g., refused / errored / truncated) | `write_pass.py` exits 2 → re-spawn |
