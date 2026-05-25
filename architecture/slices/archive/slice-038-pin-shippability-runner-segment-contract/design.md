# Design: Slice 038 pin-shippability-runner-segment-contract

**Date**: 2026-05-17
**Mode**: Standard

## Problem framing

R-8: `/validate-slice` Step 5.5 instructs Claude (item 4, `skills/validate-slice/SKILL.md` L213) to "Run each entry's **Machine-cmd** column … execute it from project root". The execution loop is **hand-rolled per slice from prose**. A naive implementation strips only the *outer* markdown fence of the whole cell; for the lone multi-segment row (#28, `` `cmdA` ; `cmdB` ``) segment 2 retains a leading backtick → `subprocess` `argv[0] = `` `<interp>… `` → `WinError 2` false-FAIL. Recurred N=2 (slice-032 secondary discovery, slice-033 LIVE at /validate) **despite** SKILL.md L213 already saying "deterministically `;`-split + interpreter-anchored". **Conclusion: a prose pin is proven insufficient — the contract must be bound by an invoked executable, not described.**

The SCMD-1 audit (`tools/shippability_decoupling_audit.py`) already implements the *correct* split-strip in `_segments()` (L179–188: split on `;`, then `.strip().strip("\`").strip()` **per segment**). It is the canonical contract. Nothing executes the catalog using it — the audit only *validates grammar*, it does not *run* the commands.

## What's new

- `tools/shippability_runner.py` (created) — reads `architecture/shippability.md`, derives each data row's `Machine-cmd` cell, splits/strips **per segment via the canonical `_segments()` reused from `tools.shippability_decoupling_audit`** (NOT re-derived), executes each segment from project root, reports per-row PASS/FAIL, exits 0 (all PASS) / 1 (≥1 FAIL) / 2 (usage error).
- `tests/methodology/test_shippability_runner_segment_contract.py` (created) — failing-first regression. `test_naive_outer_strip_runner_is_rejected` is constructed as an explicit **contrast** (per critique m2 / Must-not-defer): a local inline `_naive_outer_strip(cell)` (the historical R-8 bug: `cell.strip().strip("\`")` applied ONCE to the whole cell) is asserted to leave a leading backtick on segment 2 of real row #28 (`_naive_outer_strip(cell)[1].startswith("\`")` is True) WHILE the reused `_segments(cell)[1].startswith("\`")` is False — both branches exercised in one test so the green is load-bearing, not a tautology over the already-correct helper.
- **UTF8-STDOUT-1 propagation (per critique B1 — load-bearing recursive-self-application; mechanism CORRECTED at build)**: `tools/shippability_runner.py` has a `main()` and is auto-discovered by `tests/methodology/test_utf8_stdout_regression.py::_discovered_audit_tools()` (L278-289 — globs every `tools/*.py` non-`_`/non-`__init__` with a top-level `main` AST node) which asserts `discovered_set == covered_set` (L237/L387). That parity assertion **IS shippability row #28 segment 1** — the exact row this slice exists to fix and dogfoods at its own /validate-slice Step 5.5. **CORRECTION (build-time, recorded in build-log.md): B1's applied-fix prescribed adding `"tools.shippability_runner"` to `_POSITIONAL_SLICE_TOOLS` — this was WRONG and was NOT shipped.** `_POSITIONAL_SLICE_TOOLS` is consumed by `_positional_slice_argv = [PY, "-m", tool, str(FIXTURE_DIR)]` which passes a *slice-folder* path; `shippability_runner` takes a *catalog file* path, so a slice-folder arg errors. Its two siblings (`shippability_path_audit`, `shippability_decoupling_audit`) are deliberately **NOT** in `_POSITIONAL_SLICE_TOOLS` — they feed `covered_set` via the ADR-026 mechanism-(ii) bespoke `_assert_no_encoding_error(proc, "tools.<x>")` literal. **What shipped**: a bespoke `test_shippability_runner_survives_cp1252_with_u2192` (synthetic catalog arg) mirroring the L206-224 sibling precedent — covered_set fed via mechanism (ii); `discovered_set == covered_set` parity holds; B1's intent (runner ∈ covered_set, row #28 stays green at the dogfood) fully met. Both first-Critic AND meta-Critic blessed the `_POSITIONAL_SLICE_TOOLS` mechanism (meta-Critic explicitly "verified" it as the "correct bucket" — reasoned about `_positional_slice_argv` shape without checking the sibling precedent); caught only at build by reading the sibling tests (slice-032 "Critic reasons about the claim, not the artifact" law, N+1; the build-time artifact read is the structural backstop). See the corrected §Recursion note below — the slice-037 hazard analysis was incomplete: the real recursive hazard here is UTF8-STDOUT-1 auto-discovery firing on row #28, not AST-citation.
- `tests/methodology/test_methodology_changelog.py` (modified) — TWO paired SRSC-1 tests per the slice-037 PTFFD-1 governing precedent (L2864 `_entry_present_in_repo_and_installed` + L2915 `_shippability_consumer_propagation`): `test_v_0_51_0_srsc_1_entry_present_in_repo_and_installed` AND `test_v_0_51_0_srsc_1_shippability_consumer_propagation`. The `entry_present` test is a **CONTENT pin** (per critique M1 / slice-037 meta-Critic M-add-1 — not a tautological presence pin): it asserts a canonical anti-silent-weakening phrase (the literal `do NOT hand-roll the execution loop` AND `reuses SCMD-1 _segments()`) in BOTH in-repo and installed bodies, PLUS the ADR-039 lineage token and "supersedes nothing" (mirrors the PTFFD-1 instance L2900-2912). The `shippability_consumer_propagation` test asserts `"SRSC-1"` + `"test_shippability_runner_segment_contract.py"` are present in `architecture/shippability.md` (SCPD-1 enforcement, mirrors L2915-2941).
- `skills/validate-slice/SKILL.md` Step 5.5 (modified) — item 4 prose replaced: invoke `$PY -m tools.shippability_runner architecture/shippability.md`; explicit "do NOT hand-roll the execution loop" pin citing the canonical mechanism. The AC3 SKILL.md prose-pin test asserts the canonical-mechanism string is present at Step 5.5 (a content pin), not merely that Step 5.5 changed.
- `methodology-changelog.md` in-repo + installed (modified, forward-synced) — new rule entry **SRSC-1** at **v0.51.0**.
- `architecture/decisions/ADR-039-srsc-1-pinned-shippability-runner.md` (created).
- `architecture/shippability.md` (modified) — new catalogued row for the regression test (RPCD-1/SCPD-1).
- **4-part PMI-1 atomic bump (per critique M2 / slice-035 B-add-1, N≥3 — NOT the 3-part shorthand)**: `VERSION` 0.50.0→0.51.0 + `~/.claude/ai-sdlc-VERSION` 0.50.0→0.51.0 + `plugin.yaml` `version:` 0.50.0→0.51.0 (`plugin.yaml:15`) + `methodology-changelog.md` forward-synced to `~/.claude/methodology-changelog.md` — all four legs move together. Installed-copy reconciliation is sequenced BEFORE the INST-1 gate (it audits the installed tree).
- `plugin.yaml` + `tools/install_audit.py` (modified) — enumerate the new tool on **BOTH non-identical surfaces** (per critique m1): add `"tools.shippability_runner"` to `_CANONICAL_TOOLS` in `tools/install_audit.py` (L77-100, **22 entries → 23 after this slice**; alphabetical — insert after `tools.shippability_path_audit` L92, before `tools.supersede_audit` L93; NOT a leading-underscore helper so the `_pyfn.py`/`_stdout.py` exclusion does not apply; grep-verify the live count at build per critique-review m-add-1, do not carry a stale annotation) AND a `tools/shippability_runner.py` entry to the `plugin.yaml` tools list (L91-127); run both `plugin_manifest_audit` and `install_audit` to exit 0.
- `architecture/risk-register.md` (modified) — R-8 → `retired` citing slice-038 + ADR-039.

## What's reused

- `tools/shippability_decoupling_audit.py` `_segments()`, `_catalog_rows()`, `_machine_cmd_cell()`, `_MACHINE_CMD_IDX` — the **single canonical** split-strip + row/cell parsing. The runner imports these (it does not copy them), exactly as `shippability_decoupling_audit` itself imports `_TEST_PATH_RE` / `_parse_table_cells` from `tools.shippability_path_audit` (established CSP-1 reuse precedent in this repo).
- `tools/_stdout.reconfigure_stdout_utf8()` — same UTF-8 stdout convention as every audit (slice-023/028).
- [[decisions/ADR-031]] — SCMD-1; this slice pins the *runner consumer* of the SCMD-1 catalog, not the grammar.
- SCMD-1 / PTFCD-1 pre-catalog gates (`skills/validate-slice/SKILL.md` Step 5.5 items 3a/3b) — unchanged; the runner runs *after* both gates pass, exactly as today.

## Components touched

### `tools/shippability_runner.py` (new)
- **Responsibility**: the single canonical executor of the shippability catalog for `/validate-slice` Step 5.5 — so the per-`;`-segment backtick+ws strip contract is never re-derived ad-hoc. WHY: R-8 — hand-rolled runners false-FAIL the multi-segment row N=2.
- **Lives at**: `tools/shippability_runner.py` (created by this slice)
- **Key interactions**: imports `_segments` / `_catalog_rows` / `_machine_cmd_cell` / `_MACHINE_CMD_IDX` from `tools.shippability_decoupling_audit`; `subprocess` to execute each segment from repo root; `tools._stdout` for UTF-8. Consumed by `skills/validate-slice/SKILL.md` Step 5.5.

### `skills/validate-slice/SKILL.md` (modified)
- **Responsibility**: Step 5.5 item 4 stops describing a hand-rolled loop and instead *invokes* the canonical runner; adds an explicit no-hand-roll contract pin.
- **Lives at**: `skills/validate-slice/SKILL.md` (in-repo; forward-sync the installed `~/.claude/skills/validate-slice/SKILL.md` — EOL-agnostic per EOL-DRIFT-1).
- **Key interactions**: invokes `tools.shippability_runner`; pre-catalog gates 3a/3b unchanged.

## Contracts added or changed

### `tools.shippability_runner` CLI exit-code contract
- **Defined in code at**: `tools/shippability_runner.py` (to be created)
- **Surface**: `$PY -m tools.shippability_runner architecture/shippability.md [--json]`
- **Exit codes** (mirrors `shippability_decoupling_audit` convention): `0` all rows PASS (or empty/zero-row catalog) · `1` ≥1 row FAIL (a regression — blocks `/reflect`) · `2` usage error (catalog missing/unreadable). No HTTP/auth surface — local CLI tool.
- **Error cases**: missing catalog file → exit 2 with stderr message; a `Machine-cmd` segment exiting non-zero → that row FAIL, recorded, run continues (full catalog still executed), final exit 1.
- **Pre-condition**: SCMD-1 + PTFCD-1 pre-catalog gates already passed (Step 5.5 items 3a/3b) — the runner does NOT re-validate grammar; it trusts SCMD-1 for cell well-formedness and focuses solely on correct per-segment execution.

## Data model deltas

None. No entities, schema, migration, or persisted state. `architecture/shippability.md` gains one catalogued *row* (markdown table data), not a data-model change.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/shippability_runner.py` | `skills/validate-slice/SKILL.md` Step 5.5 item 4 (invokes `$PY -m tools.shippability_runner …`) | `tests/methodology/test_shippability_runner_segment_contract.py::test_real_row_28_both_segments_interpreter_anchored` | — |

(Methodology-tool consumer convention in this repo: a `tools.*` module is "consumed" by the SKILL.md pipeline step that invokes it — same shape as every `*_audit` tool. The Step 5.5 prose-pin + invocation IS the binding consumer; the consumer test asserts the binding behavior.)

## Decisions made (ADRs)
- [[ADR-039]] — pin Step-5.5 execution behind an invoked `tools/shippability_runner.py` that **reuses** SCMD-1's canonical `_segments()`; prose alone (proven insufficient — R-8 recurred N=2 despite SKILL.md L213) is replaced by tool-invocation. RULE-ID **SRSC-1**, methodology **v0.51.0**. — reversibility: **cheap**

## Authorization model for this slice
N/A — local developer CLI tool; no auth surface, no network, no multi-user/multi-device. Runs only what the SCMD-1-validated catalog already authorizes (`tests/…` pytest invocations), executed from project root by the developer running `/validate-slice`.

## Error model for this slice
- Catalog file missing/unreadable → exit `2`, stderr `usage error: catalog not found: <path>` (mirrors `shippability_decoupling_audit`).
- A row's `Machine-cmd` segment exits non-zero → row recorded FAIL with captured output; run continues to completion (no early abort — full regression picture); process exit `1`.
- Zero data rows / empty catalog → exit `0` (parity with Step 5.5 "catalog empty: skip").
- The runner does NOT introduce grammar/prose rejection errors — that remains SCMD-1's job at the pre-catalog gate (Step 5.5 item 3a); the runner trusts the gate (documented pre-condition, no duplicated validation = no CSP-1 divergence risk).

## Recursion / self-application note (CORRECTED per critique B1)

The original recursion analysis was **incomplete** and is superseded here. It claimed "the runner is NOT an AST-citing audit so the slice-037 three-layer hazard does not apply at full depth." That missed the real recursive hazard: the runner has a `main()`, so it is auto-discovered by UTF8-STDOUT-1's `_discovered_audit_tools()` (`test_utf8_stdout_regression.py` L278-289) into the `discovered_set == covered_set` parity assertion (L237/L387) — and **that assertion is the test behind shippability row #28 segment 1** (`test_utf8_stdout_regression.py`), the exact row this slice exists to fix and which it executes at its own /validate-slice Step 5.5 dogfood. Creating the runner without the UTF8-STDOUT-1 propagation (`_POSITIONAL_SLICE_TOOLS` membership + a cp1252 call site — see §What's new) would make this slice false-FAIL row #28 *for a real reason*, the textbook slice-022 self-violation law (the audit-tooling slice commits the defect class its own risk register documents) caught by the BC-PROJ-4 backstop, not the Critic stack — except here the Critic DID catch it.

Two distinct recursive layers therefore apply, both must be settled before the slice's own Step 5.5:
1. **UTF8-STDOUT-1 auto-discovery on the new `main()`** (the load-bearing one) — `_POSITIONAL_SLICE_TOOLS` + cp1252 call site added atomically with the runner. This is what keeps row #28 green at the dogfood.
2. **The new contract test's own catalog row** — `test_shippability_runner_segment_contract.py` is a single-segment pytest invocation → trivially SCMD-1-clean and runner-safe; appended to `architecture/shippability.md` before the slice's own /validate-slice Step 5.5 so the runner exercises its own contract test as a real catalog row (intended dogfood).

## Out of scope (restated from mission brief)
- SCMD-1 grammar / `_segments()` logic changes — already correct; reused verbatim.
- Essential-class coupling re-home (slice-030C domain).
- R-6 / R-2 / EOL-DRIFT-1 `.md` comparator (R-5, retired) — distinct concerns.
