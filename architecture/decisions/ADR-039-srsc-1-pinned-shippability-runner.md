---
id: ADR-039
title: SRSC-1 — pin the /validate-slice Step-5.5 catalog runner behind an invoked tools/shippability_runner.py that reuses SCMD-1's canonical per-segment split-strip, replacing the proven-insufficient prose pin
date: 2026-05-17
slice: slice-038-pin-shippability-runner-segment-contract
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-039: SRSC-1 — pinned shippability runner (reuses SCMD-1 `_segments()`)

## Context

R-8 (open, discovered slice-032, formally opened slice-033): the `/validate-slice` Step 5.5 catalog-execution loop is hand-rolled per slice from `skills/validate-slice/SKILL.md` prose (item 4, L213). SCMD-1 (ADR-031) defines a `Machine-cmd` cell as one or more **individually backtick-wrapped** ` ; `-separated segments; correct execution requires splitting on `;` **then stripping backticks + whitespace PER segment**. A naive runner that strips only the *outer* fence of the whole cell mangles segment 2 of the lone multi-segment row (#28) into `argv[0] = `` `<interp>… `` → `WinError 2` false-FAIL.

Critically: this recurred **N=2** (slice-032 secondary discovery; slice-033 LIVE at /validate) **even though SKILL.md L213 already said** "deterministically `;`-split + interpreter-anchored; SCMD-1-enforced". The prose pin was already present and was already insufficient — a hand-rolled loop derived from prose does not inherit the contract. SCMD-1's `tools/shippability_decoupling_audit.py` *already contains* the correct split-strip (`_segments()`, L179–188) but only *validates grammar*; it never *executes* the catalog.

## Options considered

1. **Prose-only pin (R-8 option b)** — assert each `;`-segment is independently backtick-wrapped (an audit) + strengthen the SKILL.md prose. *Rejected*: the SKILL.md prose pin already exists and R-8 recurred N=2 anyway. A grammar audit hardens the *catalog* but the *runner* is still hand-rolled from prose — the exact failure surface is untouched. Prose binds nothing executable.
2. **Inline the runner into SKILL.md as a copy-paste snippet** — *Rejected*: a copy-pasted loop is still re-derived/mutable per slice and drifts from `_segments()`; reproduces the CSP-1 divergence the audit reuse pattern exists to prevent.
3. **Invoked canonical runner reusing SCMD-1 `_segments()` (R-8 option a)** — `tools/shippability_runner.py` imports `_segments` / `_catalog_rows` / `_machine_cmd_cell` from `tools.shippability_decoupling_audit` (the established CSP-1 reuse precedent: `shippability_decoupling_audit` itself imports `_TEST_PATH_RE` from `shippability_path_audit`). SKILL.md Step 5.5 *invokes* it; the contract is bound by execution, not description. **Chosen.**

## Decision

**Option 3 + one rule SRSC-1**, methodology **v0.51.0**:

- New `tools/shippability_runner.py`: reads `architecture/shippability.md`, re-derives each data row's `Machine-cmd` cell and splits/strips **per segment via the imported canonical `_segments()`** (single source of truth — NOT re-derived, NOT copied), executes each segment from repo root, records per-row PASS/FAIL, exits `0` (all PASS / empty) / `1` (≥1 FAIL — blocks `/reflect`) / `2` (usage error). Mirrors `shippability_decoupling_audit`'s exit-code + UTF-8-stdout conventions.
- `skills/validate-slice/SKILL.md` Step 5.5 item 4: replace the hand-rolled-loop instruction with `$PY -m tools.shippability_runner architecture/shippability.md` + an explicit "do NOT hand-roll the execution loop; the per-`;`-segment backtick+ws strip is owned by `tools.shippability_runner` (which reuses SCMD-1 `_segments()`)" pin. Pre-catalog gates 3a (SCMD-1) / 3b (PTFCD-1) unchanged; the runner runs strictly *after* both pass and trusts them (no duplicated grammar validation → no CSP-1 divergence).
- A catalogued regression test (`tests/methodology/test_shippability_runner_segment_contract.py`) is added to `architecture/shippability.md` (RPCD-1/SCPD-1): it FAILS pre-fix (naive outer-strip mangles row-#28 seg 2) and PASSES post-fix, making the false-FAIL class environment-independently non-silently-recurrable. The negative case is a load-bearing contrast (inline naive-strip vs reused `_segments()` on real row #28), not a tautology over the already-correct helper.
- **UTF8-STDOUT-1 propagation (load-bearing — caught by /critique B1)**: the runner's `main()` is auto-discovered by `test_utf8_stdout_regression.py::_discovered_audit_tools()` into the `discovered_set == covered_set` parity assertion, which IS shippability row #28 segment 1 — the row this slice fixes and dogfoods. The slice MUST atomically add `"tools.shippability_runner"` to `_POSITIONAL_SLICE_TOOLS` and a `test_shippability_runner_survives_cp1252_with_u2192` cp1252 call site, else it false-FAILs row #28 at its own /validate-slice (slice-022 self-violation law).
- The SRSC-1 changelog entry gets the canonical **paired** changelog tests per the slice-037 PTFFD-1 governing precedent: `test_v_0_51_0_srsc_1_entry_present_in_repo_and_installed` (a CONTENT pin asserting the anti-silent-weakening phrases `do NOT hand-roll the execution loop` + `reuses SCMD-1 _segments()` + ADR-039 lineage + "supersedes nothing", in-repo AND installed) AND `test_v_0_51_0_srsc_1_shippability_consumer_propagation` (SCPD-1 enforcement).
- `methodology-changelog.md` in-repo + installed forward-synced. **PMI-1 atomic bump is 4-part** (per slice-035 B-add-1, N≥3 — NOT the 3-part shorthand): `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml` `version:` + forward-synced `~/.claude/methodology-changelog.md`, all 0.50.0→0.51.0 together; installed-copy reconciliation sequenced BEFORE INST-1. INST-1/PMI-1 enumerate the new tool on BOTH non-identical surfaces (`_CANONICAL_TOOLS` in `tools/install_audit.py` AND the `plugin.yaml` tools list). R-8 → `retired` citing slice-038 + this ADR.

SRSC-1 is a **new** non-`-D` audit/runner-gate-class RULE-ID with a `vN.N` version (per the slice-037 naming-lineage lesson: `vN.N` labels the non-`-D` gate class; `-D` IDs are exclusively for `-D`-family refinements). It does not supersede or refine SCMD-1 — SCMD-1 owns catalog *grammar*; SRSC-1 owns catalog *execution*. They share the `_segments()` artifact (CSP-1), not the rule identity.

## Consequences

- Step-5.5 execution is no longer re-derived; the per-segment contract is bound by an invoked tool, not folklore. The R-8 false-PCA-1-HALT class is structurally closed for the runner surface.
- New `tools/shippability_runner.py` + `tests/methodology/test_shippability_runner_segment_contract.py`; `skills/validate-slice/SKILL.md` Step 5.5 repointed + prose-pinned; PMI-1/INST-1/RPCD-1/SCPD-1 propagation atomic; changelog in-repo+installed; R-8 retired.
- `_segments()` becomes a cross-consumed canonical artifact (SCMD-1 audit + SRSC-1 runner). Any future change to the split-strip contract is a single-point edit in `shippability_decoupling_audit._segments` consumed by both — by design.
- The runner trusting (not re-validating) SCMD-1's grammar means a hypothetical SCMD-1 bypass would reach the runner; acceptable because Step 5.5 enforces 3a as a hard STOP gate *before* the runner, and duplicating validation would itself be the CSP-1 divergence this ADR avoids.

## Reversibility

**cheap** — additive tool + a one-line import + a SKILL.md prose/invocation edit + one catalog row + a changelog entry. Reverting = delete `tools/shippability_runner.py` + its test + catalog row, restore SKILL.md L213 prose, drop the changelog entry, un-retire R-8. No production/runtime/contract/data-model/network surface. Escalation: if a future legitimate row shape needs different execution semantics, extend the runner in one place via a new append-only ADR (SUP-1).
