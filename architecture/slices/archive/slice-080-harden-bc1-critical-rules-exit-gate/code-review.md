# Code Review: Slice 080 harden-bc1-critical-rules-exit-gate

**code-Critic reviewed**: slice diff vs default branch (e55750c...HEAD, filtered to in-scope paths)
**Date**: 2026-05-29
**Result**: FINDINGS (advisory v1 — does not block /validate-slice)

## Summary

Small, well-scoped, well-tested change. The code-Critic confirmed (empirically): the `if strict:` block is correctly placed after both source loops, guarded so the default path is byte-identical, captures both project- and global-source Critical rules, never double-counts; exit logic genuinely unchanged; lenient-ack surfaces a diagnostic not a silent no-op; all 5 version legs at 0.75.0. **No blockers.** 1 Major (output-honesty / contract defect in `_format_human`) + 2 Minors. M1 + m1 fixed in-band (the Major is a defect in this slice's own shipped output, not scope creep); m2 deferred (cosmetic).

## Changed files (in-scope)

```
tools/build_checks_audit.py
skills/build-slice/SKILL.md
tests/methodology/test_build_checks_audit.py
tests/methodology/test_methodology_changelog.py
tests/bugs/test_bc1_critical_rule_exit_gate.py
methodology-changelog.md
VERSION
plugin.yaml
pyproject.toml
architecture/slices/slice-080-harden-bc1-critical-rules-exit-gate/build-log.md
```

## Findings

### Blockers (advisory in v1)

None.

### Majors

#### M1: `unacknowledged-critical` violations mislabeled as "parse violation(s)" + non-path `path` field — **FIXED IN-BAND**
- **Claim under review**: `_format_human` rendered every `result.violations` entry under `"N build-checks parse violation(s):"`; the strict-append set `path=r.source` (`"project"`/`"global"`, the source label) instead of a real file path.
- **Issue**: Two coupled contract defects: (1) the strict findings printed under the "parse violation(s)" header, directly contradicting the `BuildCheckViolation` docstring this diff wrote ("an applicability-derived finding, not a parse error"); (2) `violations[].path` held a non-path source label for the new kind, inconsistent with every other violation's real `path=str(<checks-file>)`.
- **Evidence**: `tools/build_checks_audit.py` `_format_human` violations block + the strict-append `path=r.source`. Empirically: JSON `path` was `"project"`; human output began `1 build-checks parse violation(s):`.
- **Disposition**: **ACCEPTED-FIXED in-band.** (1) `_format_human` now partitions `result.violations` — the "parse violation(s)" header counts/lists only `kind != "unacknowledged-critical"`; the strict findings are surfaced solely by the BCSG-1 diagnostic block (by rule ID). (2) the strict-append now maps `r.source` → the resolved `project_checks`/`global_checks` path, so `[Critical] <real-path>:<line>` is consistent across all violation kinds. Locked by two new assertions (path-is-real-file in `test_strict_unacknowledged_project_critical_becomes_violation`; `"parse violation" not in out` in `test_format_human_strict_surfaces_unmatched_and_unacked`). 56/56 BC-1 + repro tests green post-fix.

### Minors

#### m1: `--ack-critical nargs="*"` "Place LAST" help imprecise — **FIXED IN-BAND**
- **Issue**: The greediness footgun only bites before a bareword/positional; this parser has none, so "LAST" was accurate-but-imprecise.
- **Disposition**: **ACCEPTED-FIXED in-band.** Help text tightened to "Place LAST or immediately before another --flag (nargs='*' would swallow a following bareword; this parser has none)." No functional change.

#### m2: `_format_human` recomputes applicable-Critical / acked / unacked sets the strict-append already computed — **DEFERRED**
- **Issue**: Minor duplicated predicate between the strict-append (audit_slice) and the diagnostic block (`_format_human`). Not a defect today (both compute identically); a future predicate change could drift them.
- **Disposition**: **DEFERRED** (cosmetic). The diagnostic block needs the `acknowledged` + `unmatched` sets too (not derivable from the violations list alone), so full single-sourcing isn't clean; the recomputation is the clearest form. Low value; "refactors need a slice." Nominated for a future bundled code-Critic cleanup slice (CRSI-1 voluntary-restraint precedent).

## Dimensions checked
- [x] Unfounded assumptions — M1 (docstring vs printed-header contradiction). No phantom imports.
- [x] Missing edge cases — none. Empty ack, no-applicable-Critical (exit 0), carry-over early-return (strict block unreachable), combined parse+unacked, global-source Critical — all covered/verified.
- [x] Over-engineering — m2 (minor dup) only; cosmetic.
- [x] Under-engineering — none. All 5 ACs have delivering code + tests; self-dogfood exits 0; Step-6 audits pre-satisfied.
- [x] Contract gaps — M1 (`violations[].path` semantics) — fixed in-band. New params type-hinted + defaulted; no caller breakage (only `main()` + 2 tests call `_format_human`).
- [x] Security — none (local CLI; ack IDs flow only into set membership + f-strings; no shell/eval/traversal; no secrets).
- [x] Drift from vault — none. Code matches design.md + ADR-072 (option 2, lenient ack) + MEPD-1 5-leg bump (all legs at 0.75.0). No scope creep (SC-006/007/009 + v2 auto-verification untouched).
- [x] Web-known issues — m1: argparse `nargs="*"` greediness (Python #9338/#15112) — nil runtime exposure (no positionals); help tightened.
- [x] Cross-cutting conformance — RSAD-1 (slice passes its own gate; self-dogfood exit 0). APED-1 (strict predicate exercised across 7 tests + 2 repro). EOL-DRIFT-1 (no new `.md` byte-compare).
