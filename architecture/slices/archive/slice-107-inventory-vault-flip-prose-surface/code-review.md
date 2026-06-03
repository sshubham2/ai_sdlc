# Code Review: Slice 107 inventory-vault-flip-prose-surface

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-06-03
**Result**: FINDINGS (advisory in v1 per CRSI-1) — 0 Blockers, 2 Majors, 3 Minors; **all 5 addressed in-round by the Builder** (dispositions inline)

## Summary

The code-Critic (separate `code-review` agent, 24 tool-uses, executed adversarial variants against the real corpus) confirmed the classifier is functionally sound, count is exactly 318, disjointness holds (`readiness_audit --strict` exit 0, production must-rewrite unchanged at 4), the SHA-256 baseline input is deterministic, the count-floor is wired and fires, and the wiring fan-out is complete. It surfaced 2 Majors — an incomplete `_OP_VERBS` list leaving two LIVE frontmatter paths off the M4 checklist (the exact B2 hole), and zero test coverage of the ADR-097 disposition-override mechanism — plus 3 Minors. **All were valid and fixed in-round** (the slice now classifies 318/0/0/0 with the two frontmatter paths correctly on the checklist, and the disposition mechanism is now tested on a non-empty table).

## Changed files (in-scope)

```
INSTALL.md
architecture/slices/slice-107-inventory-vault-flip-prose-surface/build-log.md
plugin.yaml
tests/methodology/test_pulse_worktree_resolver_tool_inventory.py
tests/methodology/test_stranded_slice_audit_tool_inventory.py
tests/methodology/test_utf8_stdout_regression.py
tests/methodology/test_vault_flip_prose_inventory.py
tools/install_audit.py
tools/vault_flip_prose_inventory.py
```

## Findings

### Blockers (advisory in v1)

None.

### Majors

#### M1: `_OP_VERBS` incomplete — two LIVE operational location-literals classified `doc-example` (OFF the M4 checklist), re-opening the B2/AC2 hole
- **Claim under review**: `tools/vault_flip_prose_inventory.py:94-99` (`_OP_VERBS`) + mission-brief AC2 ("a real path silently OFF the checklist is what B2 closes").
- **Issue**: `skills/design-slice/SKILL.md:3` (`Reads architecture/slices/slice-NNN/mission-brief.md`) + `skills/slice/SKILL.md:3` (`Produces … at architecture/slices/slice-NNN-<name>/mission-brief.md`) were swept to `doc-example` because `\bread\b` does not match `Reads` (trailing `s`), and `Produces`/`at` were absent — yet both are operational path references that go stale at flip. The exact B2 dangerous direction.
- **Evidence**: code-Critic executed the live corpus + verified `\bread\b` vs `Reads` fails; `skills/slice/SKILL.md:267` proves the path resolves elsewhere.
- **Builder disposition**: **ACCEPTED-FIXED** — broadened `_OP_VERBS` with the frontmatter inflections (`reads`, `produces`, `writes`, `defines`, `loads`, `emits`, `stored`, …) per B2's "generous set errs toward rewrite-at-flip, the SAFE direction". New distribution **318/0/0/0** (both paths now `rewrite-at-flip`). Re-pinned `_BASELINE_SHA256` + count-floor; design.md/mission-brief/shippability distribution updated.

#### M2: the ADR-097 `_DISPOSITION` override mechanism (the slice's flagship contract) had ZERO test coverage on a non-empty table
- **Claim under review**: `tools/vault_flip_prose_inventory.py:220-221` (the `if key in disposition:` override) + ADR-097.
- **Issue**: Every test passed `disposition={}` / the empty default `_DISPOSITION = ()`, so the override branch never executed under the suite; `test_anchor_plus_incode_routes_needs_human_exit_2` proves needs-human routing, not the disposition mechanism.
- **Evidence**: code-Critic grepped `disposition=` (only `{}`); manually exercised the override path (works) but flagged the missing automated coverage.
- **Builder disposition**: **ACCEPTED-FIXED** — added `test_disposition_override_fires_and_is_column_keyed`: asserts (a) the override fires on the exact 5-tuple key (reason `"disposition"`) and (b) a wrong-column key does NOT override (proving the M-add-1 column-offset component is load-bearing). Suite now 16 tests; TF-1 plan updated.

### Minors

#### m1: line-scoped marker detectors vs the per-match AP-1 anchoring claim
- **Issue** (`:194`/`:196`/`:201`): pathspec/anchor/verb detectors `.search()` the whole LINE (not per-match column); only `_in_inline_code` is column-anchored. Harmless on the current corpus but the docstring "every decision LINE/region-anchored" overstated per-match granularity.
- **Builder disposition**: **ACCEPTED-FIXED** — docstring clarified: in-code state is column-anchored per match; marker detectors are LINE-anchored (never whole-FILE — AP-1 satisfied). Honest documentation of actual granularity.

#### m2: `EXPECTED_TOTAL`/`_BASELINE_SHA256`/`_CLASS_COUNT_FLOOR` co-brittle magic constants without in-code provenance
- **Builder disposition**: **ACCEPTED-FIXED** — added a provenance comment at `EXPECTED_TOTAL` tying it to the `grep -rohE` count + noting the three constants move together (re-derive on corpus change; `--strict` surfaces hash/floor drift, the test surfaces count drift).

#### m3: docstring-vs-implementation verb drift (`see`/`note` in design rule-4, absent from `_OP_VERBS`)
- **Builder disposition**: **ACCEPTED-FIXED** — folded into M1; `see` + `note` added to `_OP_VERBS`, reconciling the design rule-4 vocabulary with the shipped set.

## Dimensions checked
- [x] Unfounded assumptions — m3 (verb drift, fixed); fence-toggle comment VERIFIED correct by the code-Critic (not a defect).
- [x] Missing edge cases — double-backtick inline span misclassifies (LATENT, 0 in corpus; noted); empty/unreadable file handled (exit 1); fence-toggle order verified correct.
- [x] Over-engineering — none (5-tuple key / count-floor / SHA baseline each earn their place; M2 now adds the missing disposition test to justify the empty-table mechanism).
- [x] Under-engineering — M1 + M2 (both fixed).
- [x] Contract gaps — none (CLI 0/2/1 mirrors readiness; no phantom imports).
- [x] Security — none (read-only local CLI; no network/auth/subprocess-injection/eval/secrets).
- [x] Drift from vault — none material; both build deviations documented; disjointness VERIFIED; `_RESIDUAL` line numbers VERIFIED accurate; PMI-1/INST-1/INSTALL.md/cp1252 fan-out complete.
- [x] Web-known issues — none (stdlib-only; `repr()`-of-tuple SHA input verified deterministic across CPython/platforms).
- [x] Cross-cutting conformance — UTF8-STDOUT-1 first-statement VERIFIED; APED-1 (recalibration executed against real corpus + adversarial battery); AP-1 region-anchoring clarified (m1).
