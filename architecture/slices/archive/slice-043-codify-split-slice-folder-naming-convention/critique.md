# Critique: Slice 043 codify-split-slice-folder-naming-convention

**Critic reviewed**: mission-brief.md, design.md, ADR-046
**Date**: 2026-05-18
**Result**: NEEDS-FIXES

## Summary

The core decision (option (a): codify convention + enrich the rejection message, keep the strict `\d{3}` accept regex) is sound, behavior-preserving, well-evidenced, and the methodology-surface "no rule-ID/no bump" pre-decision is correct against the *actual* enforcing assertions (Critic verified META-1 + PMI-1 by execution). Two Majors: AC4 verification command targets the wrong status filter (`mitigating`, but R-6 is `open`), and the design under-specified the RR-1 retirement mechanic (`**Status**:` line flip, not just a `**Retired**:` prose line). Two Minors: regex over-match on lowercase, and the new test module not catalogued in shippability.md. All findings execution-verified by the Critic against the real repo.

## Findings

### Blockers (must address before /build-slice)

None. The central design decision is correct and the methodology-obligation pre-decision verifies against the real enforcing artifacts.

### Majors (address this slice)

#### M1: AC4 / Verification-plan #4 / mid-slice command target the wrong status filter — R-6 is `open`, not `mitigating`
- **Claim under review**: mission-brief Verification plan #4: `--filter-status mitigating` ... "R-6 ... no longer surfaces as open/mitigating".
- **Issue**: Critic ran `tools.risk_register_audit --json` on the real file: R-6's parsed status is `open` (risk-register.md:116/120), NOT `mitigating`. `--filter-status mitigating` returns `['R-1','R-3']` — R-6 is absent from that filter *before* the slice acts, so the command is vacuously satisfied and proves nothing. R-6 goes `open → retired` directly. Correct falsifiable check: `--filter-status open` must NOT contain R-6 post-slice (it currently does).
- **Evidence**: `architecture/risk-register.md:116-128` (`**Status**: open`); live `risk_register_audit --json` showing `{'risk_id':'R-6','status':'open','line':116}`; `--filter-status mitigating` → `['R-1','R-3']`.
- **Proposed fix**: AC4 / Verification #4 / pre-finish assert R-6 absent from `--filter-status open` (and `status: retired`) post-slice, FAILs pre-slice; drop the `mitigating` filter.
- **Builder draft**: ACCEPTED-FIXED — mission-brief AC4 + Verification plan #4 rewritten to `--filter-status open` exclusion + `status == "retired"` (genuine pre/post contrast); design.md "Build-time pre-grep obligations" gained an explicit M1/M2 BC-PROJ-4 pre-finish step; `mitigating` axis removed.

#### M2: Design under-specified the RR-1 retirement mechanic — `**Status**: open` line must flip, not just add a `**Retired**:` line
- **Claim under review**: design.md "What's new": "R-6 `**Retired**:` line ... citing slice-043 + ADR-046." ADR-046: "R-6 transitions open → retired."
- **Issue**: RR-1 parses status from the `**Status**:` field line (verified: R-6 → `status: open` from line 120; R-7 → `status: retired` from its `**Status**: retired` line). Adding only a `**Retired**:` prose line without flipping `**Status**: open` → `**Status**: retired` leaves RR-1 reporting R-6 as `open`, failing AC4 and the M1 check. R-7 (the design's own model) has BOTH a flipped `**Status**: retired` line AND a retirement paragraph.
- **Evidence**: `architecture/risk-register.md:120` (R-6 `**Status**: open`) vs `:134` (R-7 `**Status**: retired`); live RR-1 JSON deriving status from that field.
- **Proposed fix**: design.md + ADR-046 must state the retirement edits the `**Status**:` line AND adds the `**Retired**:` line (R-7 two-part shape); add a pre-finish step asserting `R-6.status == "retired"`.
- **Builder draft**: ACCEPTED-FIXED — design.md "What's new" now has an explicit "R-6 retirement (M2 — explicit RR-1 mechanic)" bullet (flip `**Status**:` + add `**Retired**:`, R-7 two-part shape); mission-brief AC4 rewritten to name the `**Status**:` flip; ADR-046 Decision gained an "R-6 retirement mechanic (Critic M2 — explicit)" paragraph + Consequences updated.

### Minors (log; address if cheap)

#### m1: `_SPLIT_SLICE_FOLDER_RE` over-matches lowercase folder names; convention label is uppercase
- **Claim under review**: `_SPLIT_SLICE_FOLDER_RE = ^slice-(\d{3})([A-Za-z]+)-(.+)$`.
- **Issue**: Critic executed the regex: `slice-030abc-foo` matches the split shape (`[A-Za-z]+` accepts lowercase), so `slice-030misc-thing` would receive the split-specific "rename to next free number" message though it is not a split-slice lineage shape (convention label is uppercase `030A`/`030B`/`030C`). Harmless (message still actionable, accept/reject unchanged) but `[A-Z]+` matches the convention more precisely.
- **Evidence**: executed battery — `slice-030abc-foo strict=False split=True`; `slice-099B-x split=True` (correct); `slice-1234-foo split=False` (correct fall-through).
- **Proposed fix**: `^slice-(\d{3})([A-Z]+)-(.+)$`, OR document the permissiveness.
- **Builder draft**: ACCEPTED-FIXED — regex changed to uppercase-only `^slice-(\d{3})([A-Z]+)-(.+)$` in design.md + ADR-046; design.md regression-pin list gained a 4th case `(iv) lowercase non-convention name (slice-030misc-x) falls through to the generic message`; ADR-046 documents the intentional uppercase precision.

#### m2: New test module not planned into the shippability catalog (slice-040 detection-latency lesson)
- **Claim under review**: design.md adds `test_branch_workflow_split_slice_folder_convention.py`; no mention of `architecture/shippability.md`.
- **Issue**: slice-040 lesson — an uncatalogued pin's breakage is invisible to the catalog runner (slice-038→R-10 ~5-slice detection-latency class). BRANCH-1 shippability row 21 lists `test_branch_workflow_audit.py` + `test_root_claude_md_branch_per_slice_rule.py`, not the new module.
- **Evidence**: `architecture/shippability.md:29` (row 21 BRANCH-1); slice-040 aggregated lesson in `_index.md`.
- **Proposed fix**: add the new test module to `architecture/shippability.md` (extend row 21 or new row) as part of this slice; note in pre-finish gate.
- **Builder draft**: ACCEPTED-PENDING — the shippability catalog edit is a /build-slice + /reflect Step 5.3 artifact (not a design.md/ADR edit). design.md "What's new" now carries an explicit "m2 — shippability cataloguing" bullet declaring the obligation so it is not forgotten; the row is added at /build-slice and recorded at /reflect Step 5.3.

## Dimensions checked
- [x] Unfounded assumptions — verified line refs 59/62/270-282 accurate; methodology-obligation why-none verified against real META-1 (`test_each_changelog_entry_carries_rule_reference` iterates existing `## v` only) + PMI-1 (`test_plugin_yaml_version_matches_version_file_invariant` equality, no new-tool trigger); not-installed-mirrored CLAUDE.md verified. → M2.
- [x] Missing edge cases — regex battery executed: no shadowing of strict-valid folders; 4-digit malformed falls through correctly; one over-match → m1.
- [x] Over-engineering — none; minimal change for option (a); option (b) explicitly rejected with sound rationale.
- [x] Under-engineering — AC1/AC2/AC3 covered; AC4 gap → M1 + M2; genuine-contrast baseline verified live.
- [x] Contract gaps — none; CLI args/JSON/exit-codes explicitly unchanged; verified live.
- [x] Security — none; no auth/data-exposure surface; read-only local audit message change.
- [x] Drift from vault — ADR-046 conforms (accepted, supersedes:null, cheap, append-only); slice-029/ADR-027 precedent confirmed; cataloguing gap → m2; `test_root_claude_md_branch_per_slice_rule.py` substring assertion unaffected by sub-clause append (verified).
- [x] Web-known issues — N/A (in-house tooling only); stated explicitly per honesty rule.
- [x] Cross-cutting conformance — APED-1 executed (audit + proposed regex run against adversarial battery); state-transition pre-grep re-verified (no R-6-state test); RR-1-parse-rule executed → M1 + M2; recursive-self-application: slice-043's own folder strict-valid (does not trip its own diagnostic).

## Triage

**Triaged by**: user
**Date**: 2026-05-18
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | mission-brief AC4 + Verification #4 rewritten to `--filter-status open` exclusion + `status=="retired"` JSON-content assertion; design.md M1/M2 pre-finish BC-PROJ-4 step added; `mitigating` axis removed. DR-1 ACCEPT (VALID, Major correct). |
| M2 | Major | ACCEPTED-FIXED | design.md "What's new" + ADR-046 Decision/Consequences + mission-brief AC4 now require flipping `**Status**: open`→`**Status**: retired` AND adding the `**Retired**:` line (R-7 two-part shape). DR-1 ACCEPT (VALID, Major correct). |
| m1 | Minor | ACCEPTED-FIXED | `_SPLIT_SLICE_FOLDER_RE` → `^slice-(\d{3})([A-Z]+)-(.+)$` (uppercase-only) in design.md + ADR-046; 4th regression case (lowercase non-convention → generic) added. DR-1 ACCEPT (VALID, Minor correct). |
| m2 | Minor | ACCEPTED-PENDING | New test module catalogued in `architecture/shippability.md` at /build-slice + recorded at /reflect Step 5.3 (closes slice-038→R-10 detection-latency class); design.md declares the obligation now. DR-1 ACCEPT (ACCEPTED-PENDING is the right disposition). |
