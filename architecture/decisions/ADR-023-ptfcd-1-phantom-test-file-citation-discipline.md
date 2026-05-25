---
id: ADR-023
title: Codify the phantom-test-file-citation discipline (PTFCD-1) via a strict-pre-finish existence check in test_first_audit.py, a new shippability_path_audit.py, and an agents/critique.md Dim 9 11th sub-clause
date: 2026-05-15
slice: slice-025-add-test-file-existence-check-for-non-pytest-rows
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-023: Codify the phantom-test-file-citation discipline (PTFCD-1)

## Context

The Critic stack reviews TF-1 plan `Test path` cells and shippability `Command`-cell pytest targets for name-harmonization, status, and cross-file consistency (TPHD-1, FBCD-1, SCPD-1, RPCD-1) but **no surface verifies the cited test file actually exists on disk**. This produced a recurring phantom-test-file-citation class:

- **slice-023 B4** — `tests/methodology/test_row_*.py` convention cited; no such file/convention exists. Caught at /critique.
- **slice-024** — `tests/methodology/test_shippability_catalog.py` cited at 3 sibling sites; no such file exists. Survived 19 Critic-stack findings + both Critic layers (/critique + /critique-review) and died only at `/validate-slice` Step 5.5 real-command execution.

slice-023 lesson 5 explicitly foreshadowed this and named the recurrence sites ("verify shippability row Command-cell test paths, ADR-pin test names"), so the project's "promote at N=2 when a lesson named the future codification target AND its recurrence site at N=1" convention (aggregated-lessons) is met. slice-024 reflection classified it as developer-process calibration, not a `risk-register.md` project risk.

## Options considered

1. **Run `/critic-calibrate` only (the alternative disposition named in slice-024 discovery)** — pros: zero code; cons: calibration tunes the Critic *prompt* but the class provably survives the static Critic layer (19 findings + 2 layers missed it); a prompt nudge alone would not have caught slice-024. Insufficient.
2. **Single audit surface (test_first_audit.py only)** — pros: smallest change; cons: leaves the shippability `Command`-cell surface (the actual slice-024 witness site) unguarded; the TF-1 plan was not where slice-024's phantom citation lived.
3. **Three coordinated surfaces (chosen)** — strict-pre-finish existence check in `test_first_audit.py` (rides existing /build-slice Step 6 invocation) + new `shippability_path_audit.py` wired into /validate-slice Step 5.5 as a pre-catalog gate (the exact slice-024 witness surface) + a Dim 9 11th sub-clause so the Critic prompt also carries the discipline. Pros: closes the class at the two mechanical surfaces AND the human-review layer, matching the canonical RPCD-1/FBCD-1 codification pattern; cons: more LOC + a new tool requiring PMI-1/INST-1 registration.

## Decision

Adopt option 3. Codify PTFCD-1 across three surfaces in one slice: (a) `tools/test_first_audit.py` emits `missing-test-path-file` at `--strict-pre-finish` for any row whose resolved `test_path` does not exist (backtick-strip + `::`-split + repo-root-relative resolution; non-strict runs unaffected so PENDING test-first rows never false-positive); (b) new `tools/shippability_path_audit.py` flags non-existent test-file tokens in `architecture/shippability.md` `Command` cells (markdown-backtick strip before resolution), wired into `/validate-slice` Step 5.5 BEFORE catalog execution; (c) `agents/critique.md` Dim 9 gains an 11th sub-clause `Phantom test-file citation discipline` between the FBCD-1 10th sub-clause and `### Bonus: weak graph edges`, forward-synced byte-equal to the installed copy (CAD-1). Recorded as `methodology-changelog.md` v0.39.0; atomic version triple bumped to 0.39.0; new tool registered in `plugin.yaml` + `tools/install_audit.py` `_CANONICAL_TOOLS` (PMI-1/INST-1).

## Consequences

- Phantom test-file citations are caught at `/build-slice` Step 6 (TF-1 plan paths) and at `/validate-slice` Step 5.5 pre-catalog (shippability paths) instead of leaking to ship.
- A new audit tool enters the PMI-1/INST-1 inventory and the shippability catalog (RPCD-1/SCPD-1: the new rule propagates its consumer reference into `architecture/shippability.md`, row 25).
- The Critic-prompt sub-clause count goes 10 → 11; PMI-1 structural invariant `_lists_ten` → `_lists_eleven` superseded; the SCPD-1 consumer-reference-propagation discipline applies to that rename within this slice's /build-slice block.
- Recursive-self-application (RSAD-1) expectation: this codification slice may itself commit the phantom-citation class in its own drafts — design-time verification at the TF-1 plan path-lock table shows it does not (the single absent path is the slice's own new test file, legitimately PENDING).

## Reversibility

**cheap**. The existence check in `test_first_audit.py` is a strict-only loop appended after the existing strict gate (reverting = deleting the loop + the violation kind). `shippability_path_audit.py` is a standalone tool (reverting = deleting the file + its plugin.yaml/install_audit/shippability rows + the Step 5.5 wiring line). The Dim 9 sub-clause is append-only prose between two stable anchors (reverting = deleting the sub-clause + re-syncing the installed copy). No data model, contract, or runtime-behavior change; total revert is well under one hour.
