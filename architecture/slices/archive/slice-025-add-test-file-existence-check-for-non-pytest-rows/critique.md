# Critique: Slice 025 add-test-file-existence-check-for-non-pytest-rows

**Critic reviewed**: mission-brief.md, design.md, ADR-023
**Date**: 2026-05-15
**Result**: CLEAN (post-triage — all findings ACCEPTED-FIXED at /critique time)

## Summary

The core design (strict-only existence check in `test_first_audit.py` + new `shippability_path_audit.py` + Dim 9 11th sub-clause) is sound and line-anchor-verified. The slice — a codification slice authoring a cross-file-consistency discipline — committed the exact rule-ID drift class its sibling FBCD-1 discipline catches (recursive-self-application, expected per Dim 9), and under-specified the PMI-1/INST-1/WIRE-1 edits its own AC4 requires. All 2 Blockers + 3 Majors + 2 Minors were valid and fixed in mission-brief.md / design.md before triage.

## Findings

### Blockers (must address before /build-slice)

#### B1: Rule-ID drift `PTFC-1` vs `PTFCD-1` across slice-authoring files
- **Claim under review**: mission-brief.md AC4 "rule ID `PTFC-1`" + Risk-retired "(PTFC) class" + TF-1 row `test_v_0_39_0_ptfc_1_*` vs design.md / ADR-023 / ADR filename `PTFCD-1`.
- **Issue**: Rule ID is the load-bearing identifier propagated into the changelog entry, Dim 9 sub-clause, ADR ID, and TF-1 test-function names; must be byte-identical at every site. Exactly the FBCD-1 sub-mode (a) original-draft cross-file-consistency class, in a slice codifying a sibling discipline (recursive-self-application, agents/critique.md L168-172 Design-time mode).
- **Evidence**: mission-brief.md AC4 / Risk-retired / Intent / TF-1 row AC4 fn name; design.md + ADR-023 frontmatter; ADR file on disk.
- **Proposed fix**: Adopt `PTFCD-1` everywhere (-D-suffix convention `RSAD-1/EPGD-1/SCPD-1/RPCD-1/FBCD-1`; ADR file already `ptfcd-1`); grep `PTFC` across all slice files, confirm zero non-D residue.
- **Builder draft**: ACCEPTED-FIXED — `replace_all` PTFC→PTFCD + ptfc→ptfcd in mission-brief.md; verified zero non-D residue across {mission-brief.md, design.md, milestone.md, ADR-023} via regex scan (FBCD-1 sub-mode (a) site enumeration).

#### B2: PMI-1 / INST-1 file edits not enumerated — slice's own AC4 would fail pre-finish
- **Claim under review**: design.md "What's reused" lists `plugin.yaml` + `tools/install_audit.py` `_CANONICAL_TOOLS`, never under "What's new"/"Components touched".
- **Issue**: New tool `tools/shippability_path_audit.py` requires `_CANONICAL_TOOLS` insertion (`tools/install_audit.py:72-90`, frozen alphabetical 18-tuple) + matching `plugin.yaml` entry + version-triple bump; AC4 + pre-finish gate require PMI-1/INST-1 clean. CCC-1 v1.1 positive-inclusion-surface class.
- **Evidence**: `tools/install_audit.py:72-90`; `plugin.yaml:15`; mission-brief.md AC4 + pre-finish gate; design.md "Components touched" (omitted both).
- **Proposed fix**: Add both files + version triple to "What's new"/"Components touched" with exact insertion points (`"tools.shippability_path_audit"` between `risk_register_audit` and `supersede_audit`).
- **Builder draft**: ACCEPTED-FIXED — added dedicated component entry "`plugin.yaml` + `tools/install_audit.py` — new-tool registration + version triple" with the alphabetical insertion point, canonical `path:`/`rule:` entry shape, and 0.38.0→0.39.0 triple bump; added to "What's new".

### Majors (address this slice)

#### M1: Existence-check loop gating predicate unpinned — "never false-positives" claim unfounded
- **Claim under review**: design.md "existence never false-positives on a row that hasn't reached PASSING"; insertion "after `:365`".
- **Issue**: Existing strict loop (`test_first_audit.py:352-365`) iterates ALL `result.rows`; PENDING rows are not removed. An unconditional new loop double-flags a still-PENDING missing-file row (`non-passing-pre-finish` + `missing-test-path-file`). Claim rests on an unstated `row.status == "PASSING"` assumption.
- **Evidence**: `tools/test_first_audit.py:352-365`; design.md.
- **Proposed fix**: Pin `row.status == "PASSING"` predicate explicitly; add a TF-1 test asserting a PENDING+missing-file row under strict emits exactly one violation.
- **Builder draft**: ACCEPTED-FIXED — design.md "What's new" now states the `row.status == "PASSING"` gate is load-bearing and explains the double-flag failure mode; added TF-1 row `test_pending_row_missing_file_emits_exactly_one_violation` (AC1).

#### M2: `\S+\.py` token predicate broader than "test-file path" scope; negatives untested
- **Claim under review**: design.md error model "match only `\S+\.py` tokens".
- **Issue**: `\S+\.py` matches any `.py` token, not only test paths; the only false-positive guard ("filter to repo-relative-resolvable") is unpinned. Negative cases (interpreter path, `-m`, `-q`) untested — mirrors slice-024's 23-spurious-FAIL footgun.
- **Evidence**: `architecture/shippability.md:7-11`; design.md error-model.
- **Proposed fix**: Pin predicate to `tests/\S+\.py` tokens after the `pytest` keyword; strip backticks; `::`-split; exclude interpreter/`-m`/`-q`. Add negative-guard test.
- **Builder draft**: ACCEPTED-FIXED — design.md "What's new" + error model pin the post-`pytest` `tests/\S+\.py` predicate with explicit exclusions; added TF-1 row `test_interpreter_and_dash_m_dash_q_tokens_not_flagged` (AC2).

#### M3: `/validate-slice` Step 5.5 wiring + shippability row 25 not enumerated as touched components
- **Claim under review**: design.md wiring matrix asserts consumer `skills/validate-slice/SKILL.md` Step 5.5; not listed as an edited file. RPCD-1/SCPD-1 shippability row 25 also not enumerated.
- **Issue**: Unwired new tool = slice-018-class latent dead module; WIRE-1 needs an actual invocation added to the consumer prose.
- **Evidence**: design.md wiring matrix + "Components touched"; mission-brief.md must-not-defer RPCD-1/SCPD-1.
- **Proposed fix**: Add `skills/validate-slice/SKILL.md` (Step 5.5 pre-catalog invocation) + `architecture/shippability.md` (row 25) to "Components touched".
- **Builder draft**: ACCEPTED-FIXED — added two component entries: `skills/validate-slice/SKILL.md` Step 5.5 pre-catalog gate wiring + `architecture/shippability.md` PTFCD-1 row 25, both with concrete insertion descriptions.

### Minors (log; address if cheap)

#### m1: Design re-enumerates `_EMPTY_SENTINELS` instead of referencing the code constant
- **Issue**: design.md listed `(—, -, n/a, none)` omitting `""` and `"(none)"` — thin-vault drift risk vs `tools/test_first_audit.py:71`.
- **Builder draft**: ACCEPTED-FIXED — reworded to "skip rows whose `test_path` is in the existing `_EMPTY_SENTINELS` set (`tools/test_first_audit.py:71`)".

#### m2: `::`-split over-specifies the TF-1 surface
- **Issue**: TF-1 has separate Test path / Test function columns (`:287-315`); `::`-split is speculative there (Fowler), load-bearing only for shippability Command cells.
- **Builder draft**: ACCEPTED-FIXED — design.md path-resolution rule now labels `::`-split defensive-only for TF-1, load-bearing for `shippability_path_audit`.

## Dimensions checked

- [x] Unfounded assumptions — M1 (existence-loop predicate unpinned vs actual all-rows strict loop). Fixed.
- [x] Missing edge cases — covered in M1 (PENDING double-violation) + M2 (interpreter/`-m`/`-q` false-positive, backtick footgun). Fixed.
- [x] Over-engineering — m2 (`::`-split speculative on TF-1). Fixed; own-parser/no-cross-import decision appropriately scoped.
- [x] Under-engineering — B2 (PMI-1/INST-1 edits) + M3 (validate-slice Step 5.5 + shippability row 25). Fixed.
- [x] Contract gaps — none beyond M2; CLI contract mirrors established audit-tool convention.
- [x] Security — none: no runtime authz surface, no user-input boundary, no secrets/injection. Static in-repo file-existence audit.
- [x] Drift from vault — none: ADR-023 correct next number; append-only (no SUP-1); L192/L194 Dim 9 anchors verify against live `agents/critique.md`; "11th sub-clause" accurate (10 current).
- [x] Web-known issues — N/A: no external technology/SDK/platform API introduced.
- [x] Cross-cutting conformance — B1 (recursive-self-application / FBCD-1 sub-mode (a)) + B2 (CCC-1 v1.1 positive-inclusion) + M3 (WIRE-1/RPCD-1). All fixed.

## Triage

**Triaged by**: user
**Date**: 2026-05-15
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | PTFC→PTFCD across all 4 slice files; zero non-D residue verified by regex scan |
| B2 | Blocker  | ACCEPTED-FIXED | design.md component entry for plugin.yaml + install_audit.py `_CANONICAL_TOOLS` + version triple, with alphabetical insertion point |
| M1 | Major    | ACCEPTED-FIXED | `row.status == "PASSING"` gate pinned in design.md + TF-1 row `test_pending_row_missing_file_emits_exactly_one_violation` |
| M2 | Major    | ACCEPTED-FIXED | post-`pytest` `tests/\S+\.py` predicate + exclusions pinned; TF-1 row `test_interpreter_and_dash_m_dash_q_tokens_not_flagged` |
| M3 | Major    | ACCEPTED-FIXED | design.md component entries for validate-slice Step 5.5 wiring + shippability row 25 |
| m1 | Minor    | ACCEPTED-FIXED | reworded to reference `_EMPTY_SENTINELS` (`tools/test_first_audit.py:71`) |
| m2 | Minor    | ACCEPTED-FIXED | `::`-split labelled defensive-only for TF-1, load-bearing for shippability audit |
