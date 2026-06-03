# Validation: Slice 107 inventory-vault-flip-prose-surface

**Date**: 2026-06-03
**Result**: PASS

This slice is a read-only CLI inventory tool — "real environment" = executing the actual tool against the **real prose corpus** (not synthetic fixtures) + the real `readiness_audit` disjointness proof + the full test suite + VAL-1 + the shippability catalog.

## Per-criterion results

### AC1: new tool enumerates all 318 prose vault-literals (boundary-free, all-matches-per-line)
- **Status**: PASS
- **Evidence**: `python -m tools.vault_flip_prose_inventory --json` over the real repo →
  `total 318  counts {'rewrite-at-flip': 318, 'historical-anchor': 0, 'doc-example': 0, 'needs-human': 0}`.
  Intra-line proof: `code-review.md:103` yields **5** matches with distinct columns `[10, 390, 461, 583, 633]` (M-add-1 `re.finditer` all-matches-per-line — a single `re.search` would report 1 here and undercount the corpus 318→286).
- **Notes**: 318 == raw `grep -rohE "(architecture|diagnose-out)/"` count (verified at build); CLI flags `--json`/`--strict`/`--repo-root` + exit-code contract (0/2/1) mirror `readiness_audit`.

### AC2: context ruleset; `doc-example` reserved for plain prose; `needs-human` fail-closed
- **Status**: PASS
- **Evidence**: distribution 318/0/0/0 — every operational prose reference goes stale at flip → all `rewrite-at-flip`. The /code-review M1 fix moved the last 2 frontmatter paths (`Reads`/`Produces … architecture/…`) ON the checklist. `doc-example` is 0 (reserved, exercised by `test_doc_example_reserved_for_plain_prose` with a genuine plain-prose fixture); `needs-human` fail-closed bucket exercised by `test_anchor_plus_incode_routes_needs_human_exit_2` (anchor+in-code → exit 2) and the disposition mechanism by `test_disposition_override_fires_and_is_column_keyed`.
- **Notes**: B2's goal (operational paths never silently off the M4 checklist) is delivered — the off-checklist `doc-example` bucket is empty on this corpus.

### AC3: pinned in-module SHA-256 baseline + `--strict` drift gate + per-class count floor
- **Status**: PASS
- **Evidence**: `python -m tools.vault_flip_prose_inventory --strict` → **exit 0** (live multiset hash == `_BASELINE_SHA256`). Non-vacuous: `test_strict_drift_on_new_literal` injects a synthetic literal into a tmp corpus → `--strict` exit 2 with `DRIFT` (the hash differs). Count-floor wired (verified by the code-Critic against a simulated shrink).

### AC4: non-vacuous-by-mutation classifier + collision-free 5-tuple disposition key
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_vault_flip_prose_inventory.py` → **16 passed**. Includes `test_classifier_mutation_flips_class` (AP-5 — same literal flips class with context), `test_no_ambiguous_duplicate` (cross-line, M2), `test_no_intra_line_ambiguous_multimatch` (intra-line, M-add-1, `code-review.md:103` fixture), `test_disposition_override_fires_and_is_column_keyed` (ADR-097 override on a non-empty table — /code-review M2).

### AC5: disjointness — no new production `must-rewrite` literal into slice-106's readiness baseline
- **Status**: PASS
- **Evidence**: `python -m tools.vault_flip_readiness_audit --strict` → **exit 0** (production `must-rewrite` unchanged at 4; the SHA-256 baseline keeps `tools/vault_flip_prose_inventory.py` free of slashed collection-member literals that rule-4 would flag). `test_disjoint_no_new_production_must_rewrite` pins this. PMI-1 + INST-1 + shippability row 113 wired; INSTALL.md 41→42; cp1252 coverage +1; full methodology suite **1405 passed**.

## Layered safety checks (VAL-1)
- **Layer A (credentials)**: PASS — no secrets in the changed files.
- **Layer B (dep hallucination)**: PASS — the new tool imports stdlib (`re`/`json`/`argparse`/`hashlib`/`sys`/`collections`/`dataclasses`/`pathlib`) + internal `tools._stdout`; all resolve. `validate_slice_layers … --imports-allowlist tests` exit 0.

## Walking-skeleton / Exploratory-charter
- Not applicable (`Walking-skeleton: false`, `Exploratory-charter: false`).

## Multi-instance validation
- **Required?**: no (single read-only local CLI tool; no multi-user / multi-device / sync surface).
- **Result**: not-applicable.

## Shippability catalog regression
- Pre-catalog gates: SCMD-1 / PTFCD-1 / SVW-1 all exit 0.
- Catalog runner (`tools.shippability_runner`): **112 row(s), 112 PASS, 0 FAIL** — no past slice broken; the new row 113 (slice-107 prose inventory) is included and passes. No regressions introduced.

## Reality surprises
- None at validation. (The substantive surprises were caught earlier and resolved in-loop: the build-time corpus mis-calibration of the B2 ruleset → user-ratified recalibration; the AC5-forced SHA-256 baseline; the /code-review verb-gap M1.)
