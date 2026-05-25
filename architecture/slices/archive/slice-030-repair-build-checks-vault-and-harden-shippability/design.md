# Design: Slice 030A repair-build-checks-vault (split from slice-030; v3)

**Date**: 2026-05-16
**Mode**: Standard
**Status**: v3 — **SPLIT** to the minimal-emergency 030A scope after 2 BLOCKED dual-Critic loops + a meta-Critic non-convergence signal. User decision (2026-05-16): split. Shippability-catalog decoupling + archive-backtest fidelity → **030B** (deferred; see mission-brief "Deferred to 030B"). Audit trail: `critique-history-v1.md`, `critique.md` (v2 re-critique BLOCKED), `critique-review.md` (v2 dual-review EXTEND).

## Why split (what v1→v2 taught)

Two redesigns each closed some findings but relocated the enumeration-by-example / under-scoped-fix defect one level deeper (v1: missed gitignored inputs by category; v2: caught one, missed two changelog reads, proposed two under-scoped fixes). The meta-Critic flagged non-convergence. 030A removes the relocation surface entirely by **excluding the shippability-row/archive-backtest decoupling** (the surface where the enumeration-completeness defect lives) and delivering only the bounded, verifiable core: reconstruct + a tracked literal-constant oracle for **all five** rules + a non-opt-out full-structural-identity BCI-1 gate. The deferred 030B owns the decoupling, scoped properly with a *mechanical* complete-set derivation (not category enumeration).

## What 030A delivers (and what it does NOT)

DELIVERS: R-4's *substance* is retired — silent BC-1 degradation cannot recur, because BCI-1 catches any live↔canonical drift loud at a non-opt-out `/build-slice` gate + the Step5b post-write hook, and the canonical set is pinned to a git-tracked literal-constant oracle for every rule.

DOES NOT (→ 030B): decouple shippability rows #5/#8/#12 (and the `test_methodology_changelog.py` reads they cite) from gitignored/untracked content; resolve archive-backtest synthetic-vs-real-corpus fidelity. Residual: the catalog rows still flip on local drift, but drift is now caught loudly+immediately at `/build-slice`/Step5b with a reconstruction runbook — the false-PCA-1-HALT *window* is narrowed, the *risk* (silent degradation) is retired. Accepted 030A/030B seam (mission-brief "Deferred to 030B").

## What's new

- **`tests/methodology/fixtures/build_checks/canonical_project_checks.md`** (tracked) — header + schema preamble (recovered from the git-tracked `tools/build_checks_audit.py` module docstring L1–63: `word-boundary` L8, `Trigger anchors` L11, `Negative anchors` L19, `final filter` L21 — verified present) + `## Rules` + BC-PROJ-1/2/3 full bodies.
- **`tests/methodology/fixtures/build_checks/canonical_global_checks.md`** (tracked) — same schema preamble + BC-GLOBAL-1/2.
- **All-5-rule literal-constant oracle in `tests/methodology/test_build_checks_audit.py`** (the tracked oracle — closes v2-B3 / meta-M-add-3):
  - Existing tuple-pin tests (`test_migrated_rules_have_expected_anchors`/`_negative_anchors`, `test_bc_proj_2_has_methodology_vocabulary_negative_anchors`) **retain their hard-coded literal tuple constants** and are repointed to assert the **fixture** against those literals (fixture = subject, literal constant = oracle). NOT derive-from-fixture.
  - **NEW** `test_bc_proj_3_and_bc_global_2_have_expected_structural_identity` — literal-constant pins for BC-PROJ-3 + BC-GLOBAL-2 `(severity, applies_to, trigger_keywords, trigger_anchors, negative_anchors)`. Authoritative source: the **surviving uncorrupted live bodies** (R-4's truncation *kept* these two — they are the most authoritative available text), authored as literal constants and corroborated against the slice-028 promotion record. This gives the two survivor rules a tracked non-live oracle for the first time.
- **`tools/build_checks_integrity.py`** (tracked, rule **BCI-1**) — deterministic. Parses tracked fixtures + live files via `tools.build_checks_audit._parse_rules` (read-only). Asserts **full per-rule structural identity** (meta-M-add-2): for every rule, live `(rule_id, severity, applies_to, trigger_keywords, trigger_anchors, negative_anchors)` equals fixture's, AND `check` is non-empty. Semantics (meta-M3): `~/.claude/build-checks.md` **absent** ⇒ exit 0 + `WARN: global build-checks file absent at <path> — install for full BC-1 coverage`; **present-and-non-conformant including empty** ⇒ exit 1 + `LOCAL VAULT DRIFT — reconstruct from tests/methodology/fixtures/build_checks/<file>; this is NOT a slice regression`. `--json`; exit 2 usage. `_stdout.reconfigure_stdout_utf8()`; top-level `main`.
- **`test_build_checks_integrity_*`** (NEW regression test) — exercises BCI-1: conformant⇒exit0; 1-rule truncation⇒exit1+attributed; single corrupted `Applies to:`/`Severity` field⇒exit1 (proves full-identity not ID-only); absent-global⇒WARN/exit0; empty-global⇒HALT/exit1.
- **`skills/reflect/SKILL.md` Step 5b** — append a fail-loud post-write instruction: after writing build-checks.md, run `$PY -m tools.build_checks_integrity --check-live`; non-zero ⇒ STOP + report.
- **`skills/build-slice/SKILL.md`** pre-finish — add BCI-1 to the non-opt-out audit gate list.
- **Local reconstruction** of both gitignored `build-checks.md` = byte-copy from the tracked fixtures.

## What's reused

- `tools/build_checks_audit.py` `_parse_rules` — **read-only, unchanged** (BC-1 semantics out of scope).
- Canonical tuples (authoritative spec, already literal constants in test): BC-PROJ-1 `(subagent,fan-out)`; BC-PROJ-2 `(fence,code-block,llm)`; BC-GLOBAL-1 `(fence,code-block,llm,structured-output)`; 9-token negative-anchor tuple on BC-PROJ-1/2/BC-GLOBAL-1.
- `tools/build_checks_audit.py` module docstring L1–63 — git-tracked schema-preamble recovery source (v1-B3, verified).
- Surviving live BC-PROJ-3/BC-GLOBAL-2 bodies — best-recoverable content for their NEW literal-constant pins (survived R-4's last-rule truncation; see M1 — not provably byte-lossless).
- `tools/_stdout`, `skills/validate-slice` Step 5.5; `[[risk-register#R-4]]`, `[[slice-028-refactor-utf8-rollup-sentinel-version-agnostic]]` (promotion record — corroborates BC-PROJ-3/BC-GLOBAL-2 trigger *intent + keywords* only; reflection.md L16/L43 is prose, NOT the structural rule body — see M1/m2), `[[slice-029-make-diagnose-dispatch-sequential]]` (R-4 discovery).

## M3 per-rule recovery-source table (honest; B2 source-premise corrected)

**Tracked oracle = the test-file literal constant** (`tests/` is git-tracked). The `architecture/slices/archive/` build-logs/designs are **gitignored** (`git ls-files architecture/` → 0) — they are best-effort *recovery input* for authoring the literal constants, NOT themselves tracked oracles (B2: the v3-Critic mis-labelled the archive "git-tracked"; corrected here). Recovery-input priority per rule:

| Rule | Tracked oracle | Recovery input for authoring the literal (priority order) |
|------|----------------|------------------------------------------------------------|
| BC-PROJ-1 | NEW test-file literals: anchors (extend existing L584) + `severity`/`applies_to`/`trigger_keywords` | slice-008 archive design.md L107-109 (verbatim glob `agents/**/*.md`) > slice-005 archive design > prose |
| BC-PROJ-2 | NEW test-file literals (extend L591/L1290) + `severity`/`applies_to`/`keywords` | slice-005/012 archive verbatim body > prose |
| BC-GLOBAL-1 | NEW test-file literals (extend L618/L1116) + `applies_to`/`keywords` | slice-005 archive build-log.md L69-70 (verbatim before/after body incl. `Applies to: **` DEVIATION-1) > prose |
| BC-PROJ-3 | **NEW** test-file literal pin | surviving live body (best-recoverable) cross-corroborated vs slice-028 reflection.md L16/L43 + shippability.md L43 |
| BC-GLOBAL-2 | **NEW** test-file literal pin | surviving live body (best-recoverable) cross-corroborated vs slice-028 reflection.md L43 |

**M1 honest framing (replaces "lossless")**: BC-PROJ-3/BC-GLOBAL-2 are **best-recoverable** — they survived R-4's last-rule truncation, but R-4's whole-file-regeneration mechanism (ADR-029) could have subtly altered the survivor; no byte-level pre-R-4 oracle exists for any of the 5 rules' lost/uncertain fields. **Deviation acknowledged**: critique-review.md M-add-3 mandated sourcing these pins "from slice-028 archive (non-live origin)"; verified the slice-028 archive holds only *prose* (reflection.md L16/L43), insufficient for a structural pin — hence the surviving live body (cross-corroborated) is the best available origin. Residual accepted because BCI-1 makes any *future* drift loud at a non-opt-out gate. Reflection MUST record this residual as a known-open item, not a closed hole.

## Components touched

### `tools/build_checks_integrity.py` (new)
- **Responsibility**: deterministic non-opt-out full-structural-identity assertion of live build-checks files vs the tracked fixtures; the loud-at-the-gate R-4 detector (M2/meta-M-add-2/meta-M3).
- **Key interactions**: imports `tools.build_checks_audit._parse_rules` (read-only); consumed by `/build-slice` pre-finish + `/reflect` Step 5b post-write.

### `tests/methodology/test_build_checks_audit.py` (modified — bounded)
- **Responsibility**: 030A touches ONLY (a) repoint the tuple-pin/schema tests to assert the *fixture* against retained literal constants, (b) add the BC-PROJ-3/BC-GLOBAL-2 literal-constant test, (c) add the BCI-1 regression test. It does **NOT** touch the archive-backtest functions or rows #5/#8/#12 (→ 030B).

### `tests/methodology/fixtures/build_checks/canonical_{project,global}_checks.md` (new) / `skills/reflect/SKILL.md` Step5b + `skills/build-slice/SKILL.md` pre-finish (modified)
- As described in "What's new".

## Contracts added or changed

No runtime contracts. New internal tool CLI: `build_checks_integrity [--check-live] [--json]`; exit 0 clean-or-WARN(absent-global) / 1 non-conformant(incl empty) / 2 usage. Documented in tool docstring + methodology-changelog BCI-1 entry.

## Data model deltas
None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/build_checks_integrity.py` | `skills/build-slice/SKILL.md` pre-finish gate + `skills/reflect/SKILL.md` Step 5b post-write | `tests/methodology/test_build_checks_audit.py::test_build_checks_integrity_*` | — |
| `tests/methodology/fixtures/build_checks/canonical_project_checks.md` | repointed tuple/schema tests | `tests/methodology/test_build_checks_audit.py::test_migrated_rules_have_expected_anchors` | — |
| `tests/methodology/fixtures/build_checks/canonical_global_checks.md` | repointed global tests | `tests/methodology/test_build_checks_audit.py::test_migrated_rules_have_expected_negative_anchors` | — |

(No shippability catalog row for BCI-1 in 030A — that wiring + the rows #5/#8/#12 repoint is 030B. 030A wires BCI-1 only at the non-opt-out `/build-slice` pre-finish + Step5b, which fully delivers R-4-substance retirement without touching the catalog.)

## New-tool propagation checklist (meta-M2 — file-locations CORRECTED; RPCD-1/SCPD-1 + N=5 lesson)

- `tools/install_audit.py` `_CANONICAL_TOOLS` — add `build_checks_integrity`. **No count comment exists in that file — do NOT invent one.**
- `tests/methodology/test_utf8_stdout_regression.py` `_ROOT_ONLY_TOOLS` (L95) — add `tools.build_checks_integrity` (it is `--check-live`/`--json`, no positional slice arg → root-only). **Mandatory**: the sentinel auto-*discovers* via AST top-level-`main` scan but **fails-closed on coverage** — without this list edit `test_every_audit_tool_survives_cp1252_stdout_with_u2192_input` goes RED at /validate-slice. (`_POSITIONAL_SLICE_TOOLS` is NOT touched — tool has no slice arg.)
- `plugin.yaml` — enumerate tool + rule **BCI-1**; atomic `VERSION` + `plugin.yaml.version` bump.
- `methodology-changelog.md` — BCI-1 entry with a `Rule reference` line; pre-check the enforcing changelog test's literal expectation before editing (slice-029 lesson).
- `tools/install_audit.py` ↔ `plugin.yaml` parity (INST-1).
- UTF8-STDOUT-1 sentinel is version-agnostic since slice-028 (no count to bump — verified-true by v2 re-critique); coverage edit above is the only required sentinel action.
- Pre-suite: `$PY -m tools.build_checks_integrity` against THIS repo BEFORE the full suite (slice-027 canonical-constant self-violation gate).

## Decisions made (ADRs)

- [[ADR-028]] — **revised v3 (030A)**: tracked canonical fixtures + an all-5-rule **literal-constant** structural-identity oracle in the tracked test file (BC-PROJ-3/BC-GLOBAL-2 newly pinned from their surviving bodies); BCI-1 enforces **full per-rule structural identity** (not rule-ID-set) at a non-opt-out gate. The shippability-row decoupling claim is REMOVED from ADR-028 (→ 030B). Reversibility: cheap.
- [[ADR-029]] — **updated**: `/reflect` Step 5b has no deterministic source; BC-1 integrity enforced by the deterministic downstream BCI-1 gate, asserting **full structural identity** (not rule-ID-set). Reversibility: cheap.

## Authorization model
N/A — methodology tooling; no runtime/auth/secrets surface.

## Error model
No runtime codes. BCI-1 CLI: exit 0 = conformant OR absent-global-WARN (distinct stdout message); exit 1 = present-and-non-conformant incl. empty (attributed "NOT a slice regression" + fixture reconstruction path); exit 2 = usage. m1: fixtures use the `clean_project_checks.md` header paragraph + `## Rules` heading but REPLACE the `(none yet…)` placeholder with the reconstructed rules.

## Scope check (per /slice Step 5)
5 ACs ✅. 030A is now genuinely ~0.5–1 day (no shippability repoint, no archive fixturization, no 7-slice corpus). Coupling: fixtures + all-5-rule literal oracle + BCI-1 + reconstruction are tightly coupled (BCI-1 needs the fixture; the fixture needs the literal oracle; reconstruction needs the fixture) — correctly ONE slice. Propagation is the low-coupling/high-risk seam (slice-022/027 hotspot) — the pre-suite self-run gate is the mitigation. System shippable after 030A (additive tool + bounded test edits + local repair; no runtime surface). 030B is a clean follow-up with no 030A rollback.

## Out of scope (030A)
- Shippability rows #5/#8/#12 + `test_methodology_changelog.py` decoupling, archive-backtest fidelity → **030B**.
- `_parse_rules`/BC-1 semantics unchanged. No `.gitignore`/vault-tracking change. No Step 5b "source defect" fix (B2/ADR-029). R-1/R-2/R-3 untouched.
