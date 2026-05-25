# Critique Review: Slice 023 audit-tools-default-utf8-stdout

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-15
**First-Critic verdict**: BLOCKED (pre-triage) — 5B + 8M + 4m = 17 findings
**Dual-review verdict**: EXTEND — 0 false positives, 6 missed findings, 0 severity miscalibrations, 4 fix-block-completeness lapses subsumed under M-add-1 through M-add-4

## Summary

Meta-Critic independently re-verified all 17 first-Critic findings against the codebase and confirms every claim was substantively VALID and correctly severitied — no false positives. However, six fix-block-completeness lapses surface from re-grepping the post-fix artifacts: Builder's `ACCEPTED-FIXED` dispositions were repeatedly applied to ONE site (the site cited in the first Critic's claim) without sweeping siblings, even when the fix-class IS cross-file consistency (M5 split, M6 helper-body change). This re-fires at N=3+ in a single post-/critique fix block — eligible for promotion to a /critic-calibrate Dim 9 sub-clause if not already.

## Confirmed first-Critic findings (no challenge)

The meta-Critic independently re-verified each of B1–B5 + M1–M8 + m1–m4 against the codebase. All hold up under re-verification. Severity tagging is correct across all 17 findings.

## Suspicious findings (false positives)

**None.** The first Critic's 17 findings all verify against the codebase under independent re-grep. No over-reach.

## Missed findings (false negatives)

### M-add-1: Mission-brief pre-finish gate says "all 16 TF-1 rows at PASSING" — post-fix TF-1 plan has 18 rows

- **Claim under review**: mission-brief.md L114 `tools.test_first_audit --strict-pre-finish PASS — all 16 TF-1 rows at PASSING`.
- **Issue**: Independent count of the TF-1 plan table (mission-brief.md L26-45) returns **18 numbered rows** (4×AC1 + 2×AC2 + 5×AC3 + 1×AC4 + 6×AC5 = 18). The pre-finish gate's `16` is stale. Per Wiegers regression-guard coverage-symmetry discipline — exactly the class B5 was flagged for, missed by first-Critic at the pre-finish-gate site (first Critic's B5 sweep enumerated 6 sibling sites but did NOT include mission-brief.md L114).
- **Evidence**: `Grep "^\| [1-9] \|" mission-brief.md` returns 18 matches in the TF-1 plan table.
- **Proposed fix**: Update L114 to "all 18 TF-1 rows at PASSING".
- **Severity**: Major — pre-finish audit refuses if any row is non-PASSING; the count mismatch is a regression-guard miss but won't itself fail the gate.
- **Builder response**: **ACCEPTED-FIXED** at mission-brief.md L114 — updated count to 18 + inline breakdown (4×AC1 + 2×AC2 + 5×AC3 + 1×AC4 + 6×AC5).

### M-add-2: Per-tool argv strategy mis-groups three tools whose argv contracts contradict the grouping

- **Claim under review**: design.md L226-227 grouped tools into "--root-only" + "no argv" buckets.
- **Issue**:
  - `install_audit` listed under "`--root`-only" — but actual flag is `--claude-dir` (verified at `tools/install_audit.py` L344).
  - `mock_budget_lint` listed under "Tools with no argv" — but requires positional `files` (nargs="+", verified at L822-825).
  - `validate_slice_layers` listed under "Tools with no argv" — but requires `--slice` (required=True, verified at L507-510).
  - Consequence: invoking these "bare" or with the wrong flag exits 2 at argparse BEFORE the audit body emits any U+2192 output. The regression test would pass vacuously per M1's exact concern. Per Hendrickson exploratory-test argv-mapping + slice-020 M-add-1 fix-block-completeness watch-list.
- **Evidence**: Read of each tool's argparse block confirms the mis-classification.
- **Proposed fix**: Re-group `install_audit` → `--claude-dir <path>`; `mock_budget_lint` → positional `files`; `validate_slice_layers` → `--slice <slice>`. Eliminate "no argv" group (no tool is invoked bare post-verification).
- **Severity**: Major — regression test would silently pass without exercising the encoding path on 3 of 17 tools.
- **Builder response**: **ACCEPTED-FIXED** at design.md "Error model" surface 3 "Per-tool argv strategy" subsection — three tools moved to correct buckets with their actual argparse contracts cited; "no tool invoked bare" line added. Reading-loop verification noted: each grouping decision now references the verified argparse line range.

### M-add-3: M6 helper-body fix incomplete at ADR-021 — short-circuit lines still present

- **Claim under review**: design.md L86-94 correctly shows the simplified helper without the short-circuit; ADR-021 L57-69 STILL shows the OLD body with `if getattr(stream, "encoding", "").lower() == "utf-8": continue`.
- **Issue**: Per Fowler "ADR is the single source of truth for the decision" — if the ADR's helper body contradicts design.md's helper body, downstream maintainers can't tell which is canonical. Per Wiegers regression-guard coverage-symmetry. First-Critic's M6 disposition said "ACCEPTED-FIXED at design.md L86-95 (helper body simplified ...)" but did NOT verify ADR-021.
- **Evidence**: ADR-021 L61-68 contains the short-circuit lines that design.md L86-94 removed.
- **Proposed fix**: Strike `if getattr(stream, "encoding", "").lower() == "utf-8": continue` from ADR-021's helper body block; add a docstring explaining why unconditional reconfigure is correct (mirrors design.md's helper).
- **Severity**: Major — cross-file canonical drift; if ADR-021's body is the prose-pinned reference, it would clash with design.md's; if design.md's body is the implementation-target, the ADR misleads.
- **Builder response**: **ACCEPTED-FIXED** at ADR-021 — helper body now matches design.md (no short-circuit) + docstring inside the helper explains the M6 + M-add-3 ACCEPTED-FIXED rationale ("stdlib reconfigure is safe to call with same kwargs; unconditional reconfigure guarantees post-call state matches the slice's required contract").

### M-add-4: M5 split-test-file fix incomplete at 3 sibling sites

- **Claim under review**: Builder's M5 ACCEPTED-FIXED said the split was applied. Re-grep finds 3 surviving references to the OLD path `test_utf8_stdout_audit.py::test_every_audit_tool_survives_cp1252_stdout_with_u2192_input`:
  1. `design.md` L194 (Wiring matrix consumer-test cell)
  2. `mission-brief.md` L54 (Verification plan AC #4 cell)
  3. `ADR-021.md` L73 (Behavioural regression reference)
- **Issue**: Per slice-020 M-add-1 fix-block-completeness watch-list + Wiegers regression-guard coverage-symmetry. Tests at the published invocation surfaces would fail with "test not found".
- **Evidence**: `Grep "test_utf8_stdout_audit\.py::test_every_audit_tool_survives_cp1252"` returns 3 matches across the three files.
- **Proposed fix**: Update all 3 sites to `test_utf8_stdout_regression.py::test_every_audit_tool_survives_cp1252_stdout_with_u2192_input`.
- **Severity**: Major — published test invocation paths must resolve, or shippability row 23's command-cell fails.
- **Builder response**: **ACCEPTED-FIXED** across all 3 sites:
  - design.md L194 (Wiring matrix consumer test cell) — path updated + per-M5+M-add-4 disposition tag inline
  - mission-brief.md L54 (Verification plan AC #4) — path updated + new assertion shape pinned (`UnicodeEncodeError not in stderr`, NOT exit-code-0)
  - ADR-021 L73 (Behavioural regression reference) — path updated + per-tool argv strategy cross-referenced + parent-side subprocess decoding kwargs enumerated

### M-add-5: design.md says "13 first-Critic findings" but enumerated breakdown sums to 17

- **Claim under review**: design.md L251 + L257 + L260 + L374 (post-/critique block) referenced "13 first-Critic findings".
- **Issue**: 5 Blockers + 8 Majors + 4 Minors = 17 (not 13). The Builder appears to have implicitly excluded Minors but enumerated all three classes inline. Internally contradictory.
- **Evidence**: Critique header L5 reads "5 Blockers + 8 Majors + 4 Minors = 17 findings" (arithmetic correct).
- **Proposed fix**: Replace all "13 first-Critic" with "17 first-Critic" across L251, L257, L260, L374.
- **Severity**: Minor — informational/scoring; doesn't gate /build-slice.
- **Builder response**: **ACCEPTED-FIXED** at design.md "Post-/critique actual" (L251) + "Recursive-self-application impact at slice-023" (L260) + the related Cumulative-Critic-influence note paragraphs. New paragraph added describing the post-/critique-review state: 17 first-Critic + 6 meta-Critic = 23 cumulative findings — approaching slice-021's HWM of 28.

### M-add-6: SUP-1 verification — `supersedes: null` is technically correct but the implicit shell-side workaround is undocumented

- **Claim under review**: ADR-021 L8 `supersedes: null`. Discovery trail at L17-24 enumerates N=6 prior slices that applied the `$env:PYTHONIOENCODING = "utf-8"` workaround as an inline DEVIATION. Per SUP-1 (slice-014 / methodology-changelog v0.19.0), `supersedes:` should name any prior ADR-codified discipline this ADR retires.
- **Issue**: The shell-side workaround was a DEVIATION pattern, not an ADR-codified convention. `supersedes: null` is technically correct (no prior ADR to supersede). Informational only.
- **Evidence**: No prior ADR codifies the shell-side workaround; it lives only as DEVIATION entries in archived build-logs.
- **Proposed fix**: None required — flagging for the meta-Critic's record.
- **Severity**: Informational (Minor).
- **Builder response**: **ACCEPTED — NO ACTION**. `supersedes: null` retained as correct per SUP-1 scope (slice-supersession via /supersede-slice for archived-slice reflection.md links + ADR-supersession for prior ADR-codified disciplines). The shell-side workaround is neither — it's a DEVIATION recurrence pattern. ADR-021's body Context section L17-24 already documents the N=6 workaround trail explicitly.

## Severity adjustments

- **B2 sub-recommendation**: meta-Critic flagged that the proposed test "covering both `__init__.py` and a fixture `tools/_helper.py`" needs TWO assertions — (a) real `_stdout.py` IS filtered out when run against the real repo; (b) synthetic `_helper.py` IS filtered when run against a tmp_path fixture. Severity stays Blocker; refinement noted for /build-slice.
- **Builder response**: **ACCEPTED-PENDING** at /build-slice — `test_list_actual_tools_filters_leading_underscore_helpers` will carry two assertions:
  1. `_list_actual_tools(real_repo_root)` does NOT include `"tools/_stdout.py"` (post-slice-023 ship state).
  2. `_list_actual_tools(tmp_path_with_synthetic_helper)` does NOT include `"tools/_helper.py"`.

## Fix-block-completeness lapses subsumed

M-add-1 / M-add-2 / M-add-3 / M-add-4 are all instances of the same class — Builder's ACCEPTED-FIXED disposition applied to ONE site (the site named in the first Critic's claim) without sweeping siblings. The class breakdown:

- **M-add-1**: B5 swept 6 sibling sites for count, missed mission-brief L114 pre-finish gate.
- **M-add-2**: M1 enumerated per-tool argv but mis-classified 3 tools without reading their argparse blocks.
- **M-add-3**: M6 simplified design.md's helper body but didn't propagate to ADR-021's.
- **M-add-4**: M5 split-test-file at design.md L42-43 + Files-changed but missed 3 cross-file references at design.md L194 + mission-brief L54 + ADR-021 L73.

This is the slice-020 M-add-1 "Fix-block-completeness on count-drift Blockers" watch-list class generalized — re-fires at **N=4 within a single post-/critique fix block** at slice-023. Per Builder's own note in critique.md "Cross-mission-brief-vs-design-consistency-checking" cumulative count: this class is **eligible for promotion to a /critic-calibrate Dim 9 sub-clause at slice-024**.

## Dual-review verdict

**EXTEND** — first-Critic's 17 findings are all valid and correctly severitied; meta-Critic's 5 missed findings (M-add-1 through M-add-5; M-add-6 informational only) all ACCEPTED-FIXED inline this round; B2 sub-recommendation carries forward to /build-slice via ACCEPTED-PENDING.

Final verdict to compute at TRI-1 user triage step: **CLEAN** is now achievable iff all ACCEPTED-PENDING items have a defensible plan (which they do — B2's two-assertion test is concrete; M1's per-tool argv strategy now reflects verified contracts; M7's citation strengthening is done; M8 informational). Otherwise NEEDS-FIXES.

## Notes

Total Critic-stack pressure at slice-023: **23 cumulative findings** (17 first-Critic + 6 meta-Critic) — well above slice-022's 18 and approaching slice-021's HWM of 28. Codification-slice precedent holds: more vault-claim density = more Dim 9 sub-clause 2 / fix-block-completeness recurrence.

Recommended /critic-calibrate slice-024+ promotions (or escalations if already proposed):
1. **Fix-block-completeness sub-clause** — Dim 9 sub-clause; class re-fires at N=4 within a single post-/critique fix block at slice-023.
2. **Cross-mission-brief-vs-design-consistency-checking** — already eligible at N=3+ per Builder; meta-Critic catch demonstrates the class structurally extends to ADR-021 as a 3rd cross-file surface.
3. **Verify-Builder-self-reported-fix-completeness** — the meta-Critic's primary value-add at slice-023; the first Critic doesn't re-grep after Builder's ACCEPTED-FIXED; this gap is the class meta-Critic uniquely closes.
