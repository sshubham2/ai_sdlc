# Design: Slice 025 add-test-file-existence-check-for-non-pytest-rows

**Date**: 2026-05-15
**Mode**: Standard

## What's new

- **`tools/test_first_audit.py` — new test-path-existence check** (modification): at `--strict-pre-finish` only, for every parsed `TestFirstRow` **whose `row.status == "PASSING"`**, if the resolved `test_path` does not exist on disk, emit a new violation `kind="missing-test-path-file"`. Covers pytest AND non-pytest rows (`grep-verification` / `catalog-verification` / `git-diff-verification`). The `row.status == "PASSING"` gate (M1) is load-bearing: the existing strict loop at `tools/test_first_audit.py:352-365` iterates **all** `result.rows` (PENDING rows are not removed), so an unconditional existence loop would double-flag a still-PENDING missing-file row (`non-passing-pre-finish` + `missing-test-path-file`). Gating on PASSING means a PENDING/WRITTEN-FAILING row's missing file is reported exactly once (by the pre-existing `non-passing-pre-finish` loop) — the mission-brief must-not-defer "False-positive avoidance" reduces to this single predicate.
- **`tools/shippability_path_audit.py` — new tool** (created): parses `architecture/shippability.md`, and for each row extracts only the **test-path tokens that appear after the `pytest` keyword in the `Command` cell and match `tests/\S+\.py`** (repo-relative test paths). For each token: strip surrounding markdown backticks, split on `::` to drop the pytest selector, resolve repo-root-relative, flag if the file does not exist. Interpreter path (`*.exe`), `-m`, `pytest`, `-q`, `--no-header` and any non-`tests/`-rooted token are NOT treated as test-file paths (M2). CLI exit `0` clean / `1` violations / `2` usage. Defaults stdout to UTF-8 via `from tools import _stdout; _stdout.reconfigure_stdout_utf8()` (UTF8-STDOUT-1, slice-023).
- **`agents/critique.md` Dim 9 — new 11th sub-clause** `Phantom test-file citation discipline` (rule ID `PTFCD-1`), inserted between the FBCD-1 10th sub-clause (ends current L192) and `### Bonus: weak graph edges` (current L194). Forward-synced byte-equal to installed `~/.claude/agents/critique.md` (CAD-1).
- **`methodology-changelog.md` v0.39.0 entry** for PTFCD-1 + **ADR-023**.
- **`plugin.yaml` + `tools/install_audit.py` + version triple** (B2): register the new tool and bump the atomic version triple — see the dedicated component entries below.
- **`skills/validate-slice/SKILL.md` Step 5.5** (M3): wire `shippability_path_audit` as a pre-catalog gate — see component entry below.
- **`architecture/shippability.md`** (M3 / RPCD-1 / SCPD-1): append PTFCD-1 row 25 — see component entry below.
- **`tests/methodology/test_shippability_path_existence.py`** (new test file) + new functions in `tests/methodology/test_test_first_audit.py` + `tests/methodology/test_critique_agent.py` + `tests/methodology/test_methodology_changelog.py`.

## What's reused

- `tools/test_first_audit.py` parse path: `audit_brief_file()` → `TestFirstRow` (`tools/test_first_audit.py:74`, `:332`); strict gate at `tools/test_first_audit.py:352`. The existence check appends after the existing strict `non-passing-pre-finish` loop.
- `tools/_stdout.py::reconfigure_stdout_utf8()` — UTF-8 stdout helper ([[slice-023-audit-tools-default-utf8-stdout]], ADR-021).
- `tools/_parse_table_cells`-style markdown table parsing pattern (`tools/test_first_audit.py:191`) — reused conceptually in the new shippability audit (own parser; no cross-import to avoid coupling two audits).
- `agents/critique.md` Dim 9 sub-clause shape (`- **<Name>** — N=X sub-clause (...); peer cross-reference: ...; <body>` + optional sub-modes + `When reviewing ... the Critic SHOULD: (1)... ` + `Proposed rule-ID: ...`) — FBCD-1 at `agents/critique.md:188` is the structural template.
- CAD-1 forward-sync + byte-equality audit: `tools/critique_agent_drift_audit.py`; existing drift test `tests/methodology/test_critique_agent_drift.py`.
- PMI-1 / INST-1 canonical inventories: `plugin.yaml` tools list + `tools/install_audit.py` `_CANONICAL_TOOLS`.
- `/build-slice` Step 6 already invokes `tools/test_first_audit.py --strict-pre-finish` — AC1's check rides this existing consumer with no new wiring.
- `/validate-slice` Step 5.5 shippability catalog runner — AC2's new tool wires here as a pre-catalog-execution gate.

## Components touched

### `tools/test_first_audit.py` (modified)
- **Responsibility**: extend TF-1 audit so a PASSING row citing a non-existent test file is caught at the `/build-slice` Step 6 strict gate instead of leaking to `/validate-slice` or shipping.
- **Lives at**: `tools/test_first_audit.py` (add path resolution + a strict-only existence loop after `:365`; add violation kind `missing-test-path-file`).
- **Key interactions**: invoked by `skills/build-slice/SKILL.md` Step 6 (`--strict-pre-finish`); no new callers.
- **Path resolution rule**: skip rows whose `test_path` is in the existing `_EMPTY_SENTINELS` set (`tools/test_first_audit.py:71` — `{"", "—", "-", "n/a", "none", "(none)"}`; m1: reference the constant, do not restate it); strip surrounding backticks; resolve relative to repo root discovered by walking up from `brief_path` for a `.git` directory or `VERSION` file sentinel. The `::`-split is **defensive-only** on the TF-1 surface (m2): the TF-1 table has separate `Test path` and `Test function` columns (`tools/test_first_audit.py:287-315`, `_REQUIRED_COLUMNS=5`) so a `test_path` cell does not normally carry a `::` selector — the split is load-bearing on the `shippability_path_audit` Command-cell surface (where `path::fn` is the real format) and harmless-defensive here.

### `tools/shippability_path_audit.py` (created)
- **Responsibility**: verify every test-file path cited in `architecture/shippability.md` `Command` cells exists on disk, so the phantom-citation class (slice-024) is caught BEFORE the catalog runner produces confusing per-row FAILs.
- **Lives at**: `tools/shippability_path_audit.py` (new).
- **Key interactions**: invoked by `skills/validate-slice/SKILL.md` Step 5.5 as a pre-catalog gate; reads `architecture/shippability.md`; uses `tools._stdout`.
- **Backtick-strip**: every extracted token is `.strip("\`")`-equivalent before resolution (slice-024 validation.md footgun — produced 23 spurious FAILs without it).

### `agents/critique.md` (modified — Dim 9)
- **Responsibility**: close the structural blind spot at the Critic-prompt layer — the class survived 19 Critic-stack findings + 2 Critic layers at slice-024 and only died at real-command execution; codifying it as a Dim 9 sub-clause is the canonical mitigation (same pattern as RPCD-1/FBCD-1).
- **Lives at**: `agents/critique.md` Dim 9, new 11th sub-clause between L192 and L194.
- **Key interactions**: read by the `/critique` Critic agent; byte-equality enforced by CAD-1.

### `plugin.yaml` + `tools/install_audit.py` — new-tool registration + version triple (modified) — B2
- **Responsibility**: keep PMI-1 / INST-1 canonical inventories complete so the slice's own AC4 ("PMI-1 / INST-1 ... clean") and pre-finish gate pass.
- **Lives at**:
  - `tools/install_audit.py` `_CANONICAL_TOOLS` (`:72-90`, frozen alphabetical 18-tuple): insert `"tools.shippability_path_audit"` between `"tools.risk_register_audit"` (`:82`) and `"tools.supersede_audit"` (`:83`) — alphabetical order preserved.
  - `plugin.yaml` tools list: add the matching `- path: tools/shippability_path_audit.py / rule: PTFCD-1` entry (canonical entry shape per slice-023 M3 precedent — `path:` + `rule:`, NOT `id:`).
  - **Version triple bump 0.38.0 → 0.39.0** (currently all three at 0.38.0 on disk): `VERSION`, installed `~/.claude/ai-sdlc-VERSION` (install-time-rename surface — in-repo name is `VERSION`), and `plugin.yaml` `version:` field. PMI-1 `test_plugin_yaml_version_matches_version_file_invariant` enforces the triple equality (version-agnostic gate per PMI-1 v1.1 / slice-014).
- **Key interactions**: `tools/plugin_manifest_audit.py` (PMI-1) + `tools/install_audit.py` (INST-1) read both; the methodology-changelog v0.39.0 entry-pin test asserts the triple.

### `skills/validate-slice/SKILL.md` — Step 5.5 pre-catalog gate wiring (modified) — M3 / WIRE-1
- **Responsibility**: make `shippability_path_audit` a real consumer (not a slice-018-class latent dead module) by invoking it BEFORE the Step 5.5 shippability catalog execution; a non-zero exit aborts the slice before the catalog runs (phantom citation reported clearly instead of as confusing per-row pytest "file not found" FAILs).
- **Lives at**: `skills/validate-slice/SKILL.md` Step 5.5 — insert a `$PY -m tools.shippability_path_audit architecture/shippability.md` invocation as the first action of Step 5.5, gating the catalog run on exit 0.
- **Key interactions**: this is the WIRE-1 consumer entry point declared in the wiring matrix; `tests/methodology/test_validate_slice_skill.py` (or a new prose-pin) asserts the Step 5.5 invocation line is present.

### `architecture/shippability.md` — PTFCD-1 row 25 (modified) — M3 / RPCD-1 / SCPD-1
- **Responsibility**: propagate the new audit rule's consumer reference into the shippability catalog (RPCD-1 / SCPD-1 must-not-defer); the row's `Command` cell self-applies the new `shippability_path_audit` + the AC1 `test_first_audit` strict check as the slice's critical-path regression guard.
- **Lives at**: `architecture/shippability.md` — append row `| 25 | slice-025-... | PTFCD-1 phantom-test-file-citation guard | <pytest command targeting tests/methodology/test_shippability_path_existence.py + test_test_first_audit.py new fns> | <runtime> |`.
- **Key interactions**: run by `/validate-slice` Step 5.5 catalog; this row's own paths must pass the new `shippability_path_audit` (AC5 recursive-self-application closure).

## Contracts added or changed

None. No endpoints/events. `tools/shippability_path_audit.py` exposes a CLI contract only (exit codes `0`/`1`/`2`, optional `--json`), mirroring the established audit-tool CLI convention (`tools/test_first_audit.py:401`, `tools/risk_register_audit.py`).

## Data model deltas

None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/shippability_path_audit.py` | `skills/validate-slice/SKILL.md` Step 5.5 (pre-catalog-execution gate) | `tests/methodology/test_shippability_path_existence.py::test_flags_phantom_command_cell_test_path` | — |

(`tools/test_first_audit.py` is modified, not new — existing consumer `skills/build-slice/SKILL.md` Step 6; no WIRE-1 row required. The Dim 9 sub-clause is prose, not a module.)

## TF-1 plan path lock (TPHD-1 sub-mode (c))

Mission-brief TF-1 plan paths verified against disk at design time:

| AC | Test path | On-disk | Note |
|----|-----------|---------|------|
| 1 | `tests/methodology/test_test_first_audit.py` | EXISTS | add functions |
| 2 | `tests/methodology/test_shippability_path_existence.py` | MISSING | NEW file created by this slice — PENDING→PASSING; legitimately absent until /build-slice (test-first); existence checked only at strict-pre-finish by which point it exists |
| 3 | `tests/methodology/test_critique_agent.py` | EXISTS | add prose-pin function |
| 3 | `tests/methodology/test_critique_agent_drift.py` | EXISTS | reuse existing byte-equality function (no new fn needed) |
| 4 | `tests/methodology/test_methodology_changelog.py` | EXISTS | add v0.39.0 entry-pin + ADR-023 function |
| 5 | `architecture/shippability.md` | EXISTS | catalog-verification; row 25 appended |

No phantom citation in this slice's own TF-1 plan — the single MISSING path is the slice's own new test file (test-first PENDING). RSAD-1 self-application: clean.

## Decisions made (ADRs)

- [[ADR-023]] — codify the phantom-test-file-citation discipline (PTFCD-1) across three surfaces: `test_first_audit.py` strict-pre-finish existence check + new `shippability_path_audit.py` + `agents/critique.md` Dim 9 11th sub-clause — reversibility: **cheap**

## Authorization model for this slice

N/A — no runtime authorization surface. The slice modifies developer-process audit tooling and the Critic prompt only.

## Error model for this slice

- `tools/test_first_audit.py`: new violation `kind="missing-test-path-file"`, `severity="Important"`, message naming the row's AC + the unresolved path; emitted only when `strict_pre_finish` is True. Exit code unchanged (`1` if any violations).
- `tools/shippability_path_audit.py`: exit `0` clean, `1` one-or-more phantom paths (each reported with row #, the offending token, the resolved absolute path tried), `2` usage error (catalog file missing/unreadable). Empty/zero-row catalog → clean (exit `0`), mirroring `test_first_audit` zero-row tolerance.
- False-positive guards (must-not-defer): non-strict `test_first_audit` runs never emit `missing-test-path-file`; backtick-wrapped real paths in shippability `Command` cells resolve cleanly after strip; non-path tokens in `Command` cells (`-m`, `pytest`, `-q`, the python exe path) are not treated as test-file paths (match only `\S+\.py` tokens, then filter to repo-relative-resolvable).
