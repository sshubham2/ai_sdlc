# Design: Slice 002 — fix-diagnose-contract-and-cwd-mismatch

**Date**: 2026-05-09
**Mode**: Standard

> **Triage corrections applied (2026-05-09 evening, post-/critique):**
> - **M1**: SKILL.md Step 1 cwd-warning prose softens the causal claim — cwd-mismatch is one *hypothesis*, not confirmed; cross-references claude-code #57037 (parallel-spawn cascade-failure) as an alternative explanation. Risk-register R-1's prose gets the same #57037 cross-reference.
> - **M2**: pre-selected contract wording (byte-equal across 12 sites): `**Do NOT call Write to produce output files (the orchestrator handles that). You MAY use Bash/python for graphify queries within $OUT/graphify-out/, and Read/Grep/Glob for source files within $TARGET.**`. Reserved the four-line breakdown as once-only human-readable preamble in SKILL.md Step 5 above the contract bullet. New byte-equality prose-pin: `test_pass_templates_match_skill_md_step5_contract`.
> - **M3**: AC #5 demoted to "deferred-explicitly". New risk **R-2** added to risk-register: "no programmatic test ensures orchestrator emits cwd-mismatch warning at runtime; relies on prose-pin + manual smoke."
> - **M4**: pre-flight note — chosen wording must preserve "Do NOT call Write" substring (case-insensitive) so existing `test_skill_md_subagents_instructed_no_write` continues to pass. M2's pre-selected wording satisfies this.
> - **m1**: explicit 11-file enumeration in "Components touched" subsection.
> - **m2**: explanation of `_FIELD_RE` single-line behavior; commit to sub-bullets after field block (NOT folded into Notes).
> - **m3**: explicit before/after diff table for the risk-register format conversion.
> - **m4**: dropped `score: 6, band: high` over-specification from "Validation check"; integration test asserts `≥1 risk + zero violations` only.

## What's new

This is a cleanup slice. **No new code modules, no new ADRs, no new contracts.** Pure prose edits to existing files plus 6 new tests.

- `skills/diagnose/SKILL.md` Step 1 — gain a "cwd-must-match-TARGET" subsection + an at-spawn warning instruction (when TARGET ≠ `$PWD`, the orchestrator must emit a clear warning before continuing)
- `skills/diagnose/SKILL.md` Step 5 — relax the over-strict subagent contract from "Do NOT call Write, Bash, or python" to a permission-by-permission breakdown (`Read/Grep/Glob` for in-`TARGET` source code; `Bash/python` for graphify queries within `$OUT/graphify-out/`; `Write` is the only forbidden tool — orchestrator handles output)
- `skills/diagnose/passes/*.md` — 11 pass templates' "Output format" sections — same relaxed contract
- `architecture/risk-register.md` — format-converted to the RR-1 H2-structured schema. R1's substantive content (description, three fix candidates, status) preserved; structural metadata (Likelihood, Impact, Status, Reversibility, Discovered) made explicit per the audit's required fields.
- `tests/skills/diagnose/test_skill_md_pins.py` — 5 new prose-pin tests (3 positive, 1 negative, 1 for the cwd-mismatch warning string)
- `tests/methodology/test_risk_register_audit_real_file.py` — new integration test that runs `tools.risk_register_audit` against the project's real risk-register.md and asserts ≥1 risk + zero violations

## What's reused

- `skills/diagnose/SKILL.md` — the slice-001 orchestration shape (Steps 3, 5, 5.5, 6, 6.5) is unchanged; only the *contract wording* in Step 5 + Step 1 cwd doc changes
- `skills/diagnose/passes/*.md` — the slice-001 "Output format" sections gain corrected wording; structure (4-backtick fences, schema crib sheet, block contents, block template) unchanged
- `skills/diagnose/write_pass.py` — unchanged (the helper's contract is the same; only the human-facing prose changes)
- `tools/risk_register_audit.py` — used as-is to validate AC #3
- `tests/skills/diagnose/conftest.py` — reused for the new prose-pin tests
- `tests/skills/diagnose/test_skill_md_pins.py:_read()`, `SKILL_MD`, `PASSES_DIR` — reused as test fixtures
- ADR-001 (subagent I/O contract) — stays accepted; the wording cleanup is a *correction* of how that contract was *expressed*, not a change to the contract itself

## Components touched

### `skills/diagnose/SKILL.md` (MODIFIED)

- **Responsibility**: Existing — the /diagnose skill orchestrator prose. This slice adds a cwd-doc subsection in Step 1 and corrects the contract wording in Step 5.
- **Lives at**: `C:\Users\sshub\ai_sdlc\skills\diagnose\SKILL.md`
- **Key changes**:
  - **Step 1** — add a subsection (or paragraph) titled "If you're invoking with an explicit path, cd to it first" that explains the slice-001 / R1 finding: subagents lose tool access when TARGET ≠ parent thread's cwd, so users (and Claude when invoking the skill) should `cd $TARGET` before running. Add prose telling the orchestrator: "If `$TARGET` resolves to a path outside `$PWD`, emit a clear warning to the user *before* fanning out subagents — explain the cwd-mismatch and recommend re-invocation after `cd`'ing. The user may proceed anyway (the run will produce a degraded diagnosis with mostly empty findings); just don't pretend everything's fine."
  - **Step 5** — replace the "Explicit subagent contract" bullet's wording. Old: "Do NOT call Write, Bash, or python. Do not read any file outside TARGET." New: a four-line permission breakdown:
    1. **Write**: forbidden — the orchestrator writes the three pass output files via `write_pass.py`
    2. **Read / Grep / Glob**: allowed within `$TARGET` (including `$TARGET/diagnose-out/graphify-out/`); allowed for files in the subagent's cwd; not needed (and may not work) for paths outside cwd, hence templates+schema are embedded in this prompt
    3. **Bash / python**: allowed for graphify queries against `$OUT/graphify-out/graph.json` (per each pass template's Method section)
    4. **Output**: return three 4-backtick fenced blocks (`section`, `findings`, `summary`) in your final message; the orchestrator parses + writes
- **No code change** — this is pure prose. The runtime behavior (orchestrator saving raw to `.tmp/` + invoking `write_pass.py`) is already in slice-001 and unchanged.

### `skills/diagnose/passes/*.md` (11 files, MODIFIED)

- **Responsibility**: existing pass templates; this slice corrects their "Output format" sections' contract wording to match SKILL.md Step 5's new wording.
- **Lives at** (11 files total — explicit enumeration per triage m1): `01-intent.md`, `02-architecture.md`, `03a-dead-code.md`, `03b-duplicates.md`, `03c-size-outliers.md`, `03d-half-wired.md`, `03e-contradictions.md`, `03f-layering.md`, `03g-dead-config.md`, `03h-test-coverage.md`, `04-ai-bloat.md`.
- **Key change** (per triage M2 — wording locked, byte-equal across 12 sites): replace `**Do NOT call Write, Bash, or python.**` with the canonical contract string:

  ```
  **Do NOT call Write to produce output files (the orchestrator handles that). You MAY use Bash/python for graphify queries within $OUT/graphify-out/, and Read/Grep/Glob for source files within $TARGET.**
  ```

  This exact string appears in: SKILL.md Step 5's "Explicit subagent contract" bullet + each of the 11 pass templates' Output format section + `01-intent.md` Hard rules line 12 (which also still has the legacy phrase from slice-001 Phase 7). Total: 13 occurrences of the byte-equal string. The `test_pass_templates_match_skill_md_step5_contract` test asserts byte-equality across the 11 templates' contract lines vs. SKILL.md's contract bullet.
- **Pre-flight note (per triage M4)**: this wording preserves the substring "Do NOT call Write" (case-insensitive), so existing `test_skill_md_subagents_instructed_no_write` continues to pass without modification.

### `architecture/risk-register.md` (MODIFIED — format conversion + R-2 added)

- **Responsibility**: existing project-level risk register; this slice converts it from the slice-001 ad-hoc format to the RR-1 H2-structured schema, and adds R-2 (per triage M3).
- **Lives at**: `C:\Users\sshub\ai_sdlc\architecture\risk-register.md`

#### Format conversion of R-1 (per triage m3 — explicit diff table)

```
REMOVE:  **Severity**: Important
ADD:     **Likelihood**: medium
ADD:     **Impact**: high
REPLACE: **Status**: ACTIVE → **Status**: open
KEEP:    **Reversibility**: cheap (already valid)
ADD:     **Discovered**: slice-001-diagnose-orchestration-fix (2026-05-09)
RENAME:  ### R1 — Cwd-mismatch... → ## R-1 -- Cwd-mismatch... (H3 → H2; em-dash → double-dash)
PRESERVE: all existing prose (Surfaced by, Description, Impact, Workaround, Fix candidates) as sub-bullets AFTER the field block — NOT folded into Notes
```

**`_FIELD_RE` single-line caveat (per triage m2)**: `tools/risk_register_audit.py:59` `_FIELD_RE` regex is single-line; folding multi-line prose into a `**Notes**:` field would silently truncate to first line. Therefore, do **not** use Notes for the R-1 description / fix-candidates prose. Keep them as plain markdown sub-bullets after the field block — the audit's parser walks line-by-line and stops collecting fields once non-field-pattern content begins (so trailing prose is ignored without violation).

**Per triage M1 — also add to R-1's prose:** a one-line cross-reference to claude-code GitHub issue #57037 (parallel-spawn cascade-failure as alternative root-cause hypothesis), so future risk-spike work has both leads.

#### New entry: R-2 (per triage M3)

```
## R-2 -- No programmatic test ensures /diagnose emits cwd-mismatch warning at runtime

**Likelihood**: medium
**Impact**: low
**Status**: open
**Reversibility**: cheap
**Discovered**: slice-002-fix-diagnose-contract-and-cwd-mismatch (2026-05-09)

(prose: cwd-mismatch warning is delivered by SKILL.md Step 1 prose telling the orchestrator [Claude main thread] to detect TARGET ≠ $PWD and emit a warning. The prose-pin tests guard the prose's existence, but nothing programmatically verifies the orchestrator actually emits the warning at runtime. This is acknowledged-fragile per slice-002 critique M3. Programmatic verification deferred to a future slice if real regressions surface.)
```

#### Validation check (per triage m4 — drop over-specification)

After conversion, `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open` must return ≥1 risk in the `risks` array with zero parse violations. (No assertion on specific score / band — those are not load-bearing for AC #3, and over-specifying would brittle-couple the test to one risk's rating.)

### `tests/skills/diagnose/test_skill_md_pins.py` (MODIFIED)

- **Responsibility**: existing prose-pin test file from slice-001; this slice adds 5 new tests for the corrections.
- **Lives at**: `C:\Users\sshub\ai_sdlc\tests\skills\diagnose\test_skill_md_pins.py`
- **New test functions** (6 tests; was 5, +1 byte-equality test from triage M2):
  - `test_skill_md_step1_documents_cwd_constraint` — assert SKILL.md contains a phrase like "cd to TARGET" or "cwd must match" or equivalent in the Step 1 region
  - `test_skill_md_step1_emits_cwd_mismatch_warning` — assert SKILL.md contains a phrase telling the orchestrator to emit a warning when TARGET ≠ $PWD (e.g., search for "warning" within Step 1's vicinity, plus a substring like "TARGET" / "PWD" / "cwd")
  - `test_skill_md_step5_allows_bash_for_graphify` — assert SKILL.md Step 5 contains the canonical contract string (with "Bash" + "graphify" anchors)
  - `test_pass_templates_allow_bash_for_graphify` — assert each of the 11 pass templates' Output format section contains the canonical contract string
  - `test_no_legacy_no_bash_no_python_phrase` — negative pin: the literal string "Do NOT call Write, Bash, or python" must NOT appear anywhere in `skills/diagnose/SKILL.md` or `skills/diagnose/passes/*.md` (a regression guard)
  - `test_pass_templates_match_skill_md_step5_contract` — **byte-equality** pin (per triage M2): the canonical contract string must appear byte-for-byte across all 12 sites (SKILL.md Step 5 contract bullet + 11 pass templates). Drift = test fails.
- **Reuses**: existing `_read()`, `SKILL_MD`, `PASSES_DIR` module-level helpers

### `tests/methodology/test_risk_register_audit_real_file.py` (NEW)

- **Responsibility**: integration test that runs the RR-1 audit against the project's real `architecture/risk-register.md` and asserts the file is audit-clean.
- **Lives at**: `C:\Users\sshub\ai_sdlc\tests\methodology\test_risk_register_audit_real_file.py` (new file)
- **Key interactions**: imports `run_audit` from `tools.risk_register_audit`; reads `REPO_ROOT / "architecture" / "risk-register.md"` (REPO_ROOT from `tests/methodology/conftest.py`)
- **Test functions** (one is enough for AC #3):
  - `test_project_risk_register_audit_clean` — runs the audit; asserts `len(result.risks) >= 1` (at least R-1) AND `result.violations == []` (no parse errors). This is a *meta* test on the project's vault — when future slices add risks, the test still passes as long as the format is clean.

## Contracts added or changed

None. The slice doesn't introduce or modify any code-level contracts (HTTP endpoints, events, data shapes). The only "contract" affected is the *human-facing wording* of slice-001's existing subagent I/O contract — that wording is being corrected, not the contract itself. ADR-001 stays accepted as the authoritative contract decision.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1**.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(Empty matrix. This slice introduces no new code modules — only modified existing prose files + new test functions in existing/new test files. WIRE-1 audit accepts zero-row matrices as clean.)

## Decisions made (ADRs)

None. The corrections in this slice are *implementations* of slice-001's ADR-001, not new architectural decisions. ADR-001 already determined "subagents do analysis only; orchestrator writes via helper" — slice-001 implemented it with one over-strict wording mistake and one missed environmental case; slice-002 corrects both.

## Authorization model for this slice

N/A. /diagnose is a local CLI skill operated by the developer. No multi-user surface introduced or changed.

## Error model for this slice

| Where | Trigger | Behavior |
|-------|---------|----------|
| `SKILL.md` Step 1 | TARGET resolves to a path outside `$PWD` | Orchestrator emits a one-paragraph warning to the user before fanning out subagents: explains the cwd-mismatch, names the slice-001 / R1 finding, recommends re-invocation after `cd $TARGET`. User may proceed anyway (will produce degraded diagnosis); orchestrator does NOT abort. |
| `SKILL.md` Step 5 / pass templates | Subagent receives the relaxed contract | No new error paths. Subagent uses Read/Grep/Glob/Bash/python within their permitted scopes; Write is still forbidden (orchestrator handles output via `write_pass.py`). The slice-001 retry-cap (3 attempts) and `.failed.raw` artifact path remain in place unchanged. |
| `risk_register_audit` integration test | Future risk added with malformed fields | Audit returns parse violations; test fails; the slice that added the risk is forced to fix the format before /reflect can land. (Indirect benefit — not a new error path created by *this* slice.) |
