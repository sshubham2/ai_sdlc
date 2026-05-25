# Critique: Slice 042 realign-entry-present-pin-names-to-decoupled-shape

**Critic reviewed**: mission-brief.md, design.md, new ADRs (ADR-044, ADR-045)
**Date**: 2026-05-18
**Result**: NEEDS-FIXES

## Summary

The slice's intent and live-vs-frozen boundary (ADR-045) are sound and the "no
RULE-ID/changelog/PMI-1 obligation" claim is verified correct against the actual
META-1 / PMI-1 assertions. However, every quantitative inventory count in
design.md was carried forward from slice-041's reflection prose instead of
re-derived, and is wrong; the carve-out ADR enumeration is materially incomplete;
and ≥4 active reference sites (incl. a `tools/` source file) were undocumented.
All findings independently re-verified by the Builder via mechanical grep before
disposition (counts recomputed, not trusted — slice-032/036 discipline).

## Findings

### Blockers (must address before /build-slice)

#### B1: Def count wrong — design says 40, actual is 37; AC says "2 _entry_names", actual is 4
- **Claim under review**: design.md "40 `def` ... function definitions"; mission-brief AC #1 "the 2 `_entry_names_*` variants".
- **Issue**: Verified count = **37** (33 `_entry_present_in_repo_and_installed` + **4** `_entry_names_*_in_repo_and_installed`). The 4th variant is `test_v_0_36_0_entry_names_three_modes_in_repo_and_installed` — note `_entry_names_three_modes` (no `_sub_`, no `_<rule>_` segment); a `_entry_names_*_sub_modes` anchor would silently miss it → orphaned shippability `::`-selector (slice-035 Bucket-A hard-failure class).
- **Evidence**: `grep -cE '^def test_\w*_entry_(present|names_\w+)_in_repo_and_installed' tests/methodology/test_methodology_changelog.py` = 37; `_entry_names` defs at L802/1005/1512/1606 (last = `entry_names_three_modes`). Builder-verified.
- **Proposed fix**: Correct counts to 37 (33+4); enumerate the 4 `_entry_names` fns; anchor the rename regex on the literal `_in_repo_and_installed` suffix of the `_entry_present`/`_entry_names` family (catches the no-`_sub_` variant); fix mission-brief AC #1 to "4". Make the build-step-1 pre-edit grep the single source of truth; reconcile all narrative counts to it.
- **Builder draft**: ACCEPTED-FIXED — design.md restructured to grep-predicate-driven with a verified inventory table; ADR-044 anchor clarified to the literal suffix incl. the no-`_sub_` variant; mission-brief AC #1 corrected.

#### B2: Carve-out ADR enumeration incomplete — design says 13, actual 16; omits ADR-016/018/031
- **Claim under review**: design.md / ADR-045 "13 ADR files (ADR-009..014, 026, 033, 034, 035, 038, 039, 040)"; mission-brief AC #3 "the ADRs ... enumerated explicitly in design.md".
- **Issue**: Verified prior ADRs with the old family name (excl. in-flight ADR-042/044/045) = **16**; design omits **ADR-016, ADR-018, ADR-031**. The must-not-defer pre/post byte-identical proof is checked against a wrong baseline → carve-out not leak-proof.
- **Evidence**: `grep -rlE '_entry_present_in_repo_and_installed|_entry_names_[a-z_]+_in_repo_and_installed' architecture/decisions/*.md | grep -vE 'ADR-04[245]'` = 16 files incl. ADR-016/018/031. Builder-verified.
- **Proposed fix**: Replace the hand-typed list with a **grep predicate** ("all `architecture/decisions/ADR-*.md` except ADR-044/045") + a frozen pre-edit count snapshot, per the slice-035 inventory-grep precedent.
- **Builder draft**: ACCEPTED-FIXED — ADR-045 + design.md carve-out restated as a grep predicate with a pre-edit snapshot; no hand-enumerated list retained.

#### B3: Four active reference sites undocumented — incl. a `tools/` source file
- **Claim under review**: design.md "Components touched" + AC #2's "4 single-occurrence files".
- **Issue**: Undocumented active (non-frozen) family refs: `tools/methodology_changelog_forward_sync.py:58` (module docstring naming `test_v_0_53_0_mcfs_1_entry_present_in_repo_and_installed` — **live source**, leaving it stale = fresh identifier-truth/FBCD-1 defect); `architecture/critic-calibration-log.md` (1); `architecture/lessons-learned.md` (2); `architecture/slices/_index.md` (**4**, Critic said 2 — undercounted, finding strengthened). Each must be explicitly bucketed (slice-035 two-bucket discipline) or it is an unmanaged leak.
- **Evidence**: `grep -rn` per file. Builder-verified (`_index.md` = 4, not 2).
- **Proposed fix**: Classify `tools/methodology_changelog_forward_sync.py:58` as LIVE-realign (current source describing the current pin); classify `critic-calibration-log.md`, `lessons-learned.md`, `_index.md` as FROZEN historical record-prose with rationale. Update design.md touched-components + carve-out; re-derive the grep baseline.
- **Builder draft**: ACCEPTED-FIXED — design.md Components-touched gains `tools/methodology_changelog_forward_sync.py` (LIVE); carve-out predicate explicitly enumerates the 3 historical-prose vault files (corrected `_index.md`=4); bucket table added.

### Majors (address this slice)

#### M1: Shippability model imprecise — "~31 rows" wrong; actual 67 occ = 31 unique names across 28 rows
- **Claim under review**: design.md / ADR-045 "67 `::`-selector references across ~31 catalog rows (rows 7–41)".
- **Issue**: Verified: **67 occurrences = 31 unique fn names across 28 distinct rows** `[7–27, 30, 32, 35, 37, 38, 39, 41]` — not "~31 rows", not contiguous 7–41. An imprecise model risks an incomplete sweep (SCPD-1 consumer-propagation).
- **Evidence**: parsed `shippability.md` rows. Builder-verified: occ=67, unique=31, rows=28 (enumerated).
- **Proposed fix**: Restate as "67 occurrences = 31 unique names across 28 rows"; build-step-4 driven by the grep rename map; post-edit assertion: zero old-name `::`-selector survives.
- **Builder draft**: ACCEPTED-FIXED — design.md + ADR-045 restated with the exact verified row enumeration + post-edit zero-survivor assertion.

#### M2: Changelog frozen-count wrong (39 vs 43); sibling-ref enumeration internally inconsistent (4/5/6)
- **Claim under review**: design.md / ADR-045 "39 refs"; "the 6 active ... references" (lists 5 sites); AC #2 "4 single-occurrence files".
- **Issue**: Verified `methodology-changelog.md` family occurrences = **43**, not 39 — wrong frozen baseline for the byte-identical proof. The LIVE non-def realign set is stated as 4/5/6 in different places (FBCD-1 cross-file inconsistency).
- **Evidence**: `grep -c` on `methodology-changelog.md` = 43. Builder-verified.
- **Proposed fix**: Correct frozen changelog snapshot to 43 (grep-derived); reconcile the LIVE non-def realign set to one statement: 2 in-file comments (`test_methodology_changelog.py:1821`,`:2936`) + 4 sibling files (`test_critique_agent.py:1426`, `test_methodology_changelog_forward_sync.py:16`, `test_query_design_skill.py:17`, `test_shippability_decoupling_audit.py:57`) + `tools/methodology_changelog_forward_sync.py:58` (per B3) = the complete LIVE non-def set; stated identically in design.md + mission-brief.
- **Builder draft**: ACCEPTED-FIXED — single reconciled LIVE-non-def enumeration in design.md; frozen snapshot stated as grep-derived (count not hand-typed).

#### M3: ADR-044/045 self-reference the old name (RSAD-1) — must state intentionally retained
- **Claim under review**: ADR-044/ADR-045 prose cites the old family name.
- **Issue**: Borderline-acceptable (they document the rename, using `<rule>`/`<x>` placeholders), but under the B2 predicate ("all ADRs except 044/045") their own old-name citations are intentionally LIVE-but-correct; without an explicit statement a future identifier-truth slice may "fix" them.
- **Evidence**: ADR-044:16,34,36; ADR-045:15. Builder-verified.
- **Proposed fix**: One sentence in ADR-045 stating ADR-044/045's old-name citations are the canonical record of the rename and NOT identifier-truth defects.
- **Builder draft**: ACCEPTED-FIXED — sentence added to ADR-045 Consequences.

### Minors (log; address if cheap)

#### m1: Smoke-gate / build-seq "4 files" wording stale after B3/M2
- **Claim under review**: mission-brief mid-slice smoke gate "before the 4 single-occurrence files"; design.md build-seq step 4 "4 sibling refs".
- **Issue**: After B3 (adds `tools/` LIVE) + M2 (reconciled set), the "4" wording must propagate (FBCD-1 fix-block-completeness).
- **Evidence**: mission-brief smoke gate + design.md step 4. Builder-verified.
- **Proposed fix**: Update sequencing-step + smoke-gate wording in lockstep.
- **Builder draft**: ACCEPTED-FIXED — both sites updated to the reconciled LIVE-non-def set.

## Dimensions checked
- [x] Unfounded assumptions — B1/B2/M2 (counts carried from slice-041 prose, not re-derived) — all Builder-verified true
- [x] Missing edge cases — B1 sub-finding: the no-`_sub_` `entry_names_three_modes` variant
- [x] Over-engineering — none
- [x] Under-engineering — B3 (AC #2/#3 require every active ref bucketed; 4 sites unassigned)
- [x] Contract gaps — none; META-1 (`test_each_changelog_entry_carries_rule_reference`) is per-`## v`-block, does NOT cross-check fn names → renaming fns while leaving changelog Validation lines stale creates NO audit failure (brief scrutiny question answered)
- [x] Security — none
- [x] Drift from vault — M3 (RSAD-1 self-reference); "no RULE-ID/changelog/PMI-1" pre-decision VERIFIED correct against actual META-1 + PMI-1 v1.1 assertions (slice-036/040 conformance-fix precedent, MEPD-1(b) satisfied)
- [x] Web-known issues — N/A (no external dependency)
- [x] Cross-cutting conformance — B3/M1/M2 are FBCD-1/SCPD-1/RPCD-1 class; slice-022 self-violation law (~N≈10) fired (inaccurate identifier inventory in an identifier-truth slice's own design) — caught at /critique, not deferred to pre-finish

## DR-1 meta-Critic missed findings (EXTEND — added to triage scope)

The first Critic's ACCEPTED-FIXED edits replaced wrong numbers with new wrong
numbers on 5 buckets (recompute-don't-trust failure; execute-don't-reason N≥4).
All re-verified by the Builder via the authoritative ADR-044 anchor regex.

#### B-add-1: rev-1 shippability count wrong — 67/31 → actual 69/32 (28 rows)
- **Issue**: M1's "fix" introduced a fresh wrong number; `67 occ / 31 unique` → authoritative **69 occ / 32 unique** (28 `_entry_present` + 4 `_entry_names`), 28 rows. Internally falsifiable (28+4=32≠31).
- **Evidence**: `grep -oE 'test_[A-Za-z0-9_]*_entry_(present|names_[A-Za-z0-9_]+)_in_repo_and_installed' architecture/shippability.md | sort -u | wc -l` = 32; occ = 69. Builder-verified.
- **Builder draft**: ACCEPTED-FIXED — design.md table/Components + ADR-045 + mission-brief AC2 → 69/32/28.

#### B-add-2: rev-1 FROZEN changelog count wrong — 43 → actual 40
- **Issue**: M2 over-corrected 39→43; authoritative **40 occ / 32 unique**.
- **Evidence**: anchor grep on `methodology-changelog.md` = 40. Builder-verified.
- **Builder draft**: ACCEPTED-FIXED — design.md + ADR-045 → 40.

#### B-add-3: rev-1 FROZEN prior-ADR count wrong — 16-incl-ADR-016/018/031 → actual 13; named ADRs have 0 matches
- **Issue**: B2's correction named ADR-016/018/031 which contain **0** fn-name-family matches; authoritative prior-ADR count = **13** (ADR-009..014, 026, 033, 034, 035, 038, 039, 040).
- **Evidence**: anchor `grep -rl` over `architecture/decisions/*.md` excl. 042/044/045 = 13; ADR-016/018/031 = 0. Builder-verified.
- **Builder draft**: ACCEPTED-FIXED — predicate retained (leak-proof regardless of count); illustrative count → 13; false ADR-016/018/031 claim removed.

#### m-add-1: rev-1 historical-vault-prose counts wrong — _index.md 4→3; critic-calibration-log.md 1→0
- **Issue**: `_index.md` = **3** (not 4); `critic-calibration-log.md` = **0** (not 1 — bucket non-existent); `lessons-learned.md` = 2 (correct). FROZEN ⇒ cannot break build; still a false claim in an identifier-truth slice.
- **Evidence**: anchor grep per file. Builder-verified.
- **Builder draft**: ACCEPTED-FIXED — `_index.md(3)`; calibration-log bucket dropped.

#### m-add-2: mid-slice smoke-gate scope vs live `::`-selector consumers undocumented
- **Issue**: `tools/shippability_path_audit.py:199-213` (`missing-test-function`) + `tools/shippability_runner.py:144` (`subprocess.run`) resolve the 69 `::`-selectors; between step 3 (defs renamed) and step 4 (shippability realigned) they are expected-red — the smoke gate must explicitly scope to the SOT file only.
- **Evidence**: `tools/shippability_path_audit.py:199-213`, `tools/shippability_runner.py:144`. Builder-verified.
- **Builder draft**: ACCEPTED-FIXED — design build-seq step 3 scopes the smoke gate to the SOT file ONLY; path-audit/runner excluded from its green-bar claim (validated step 4/6).

#### M3-sev: M3 scope overstated (severity unchanged) — only ADR-044 cites old name, ADR-045 has 0
- **Issue**: rev-1 prose "ADR-044/045 cite old name" overstated; **ADR-044** = 1 literal occ (L44, the no-`_sub_` example), **ADR-045** = 0 (placeholders). Minor severity correct for ADR-044.
- **Evidence**: anchor grep ADR-044=1, ADR-045=0. Builder-verified.
- **Builder draft**: ACCEPTED-FIXED — ADR-045 Consequences narrowed to "ADR-044 cites once; ADR-045 zero".

## Triage

**Triaged by**: user
**Date**: 2026-05-18
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | def count → 37 (33+4); ADR-044 anchor incl. no-`_sub_` variant; AC#1 corrected; grep-verified |
| B2 | Blocker | ACCEPTED-FIXED | carve-out restated as leak-proof predicate (every ADR-*.md except 044/045) |
| B3 | Blocker | ACCEPTED-FIXED | `tools/...:58` bucketed LIVE; 3 vault files FROZEN; design Components updated |
| M1 | Major | ACCEPTED-FIXED | shippability restated; superseded by B-add-1's verified 69/32/28 |
| M2 | Major | ACCEPTED-FIXED | changelog corrected; superseded by B-add-2's verified 40; sibling enum reconciled |
| M3 | Major | ACCEPTED-FIXED | ADR-045 RSAD-1 sentence added; refined by M3-sev |
| m1 | Minor | ACCEPTED-FIXED | smoke-gate / build-seq wording propagated to reconciled LIVE set |
| B-add-1 | Blocker | ACCEPTED-FIXED | shippability 67/31 → verified 69/32/28 (ADR-044 anchor); applied design/ADR-045/mission-brief |
| B-add-2 | Blocker | ACCEPTED-FIXED | FROZEN changelog 43 → verified 40; applied design/ADR-045 |
| B-add-3 | Blocker | ACCEPTED-FIXED | prior ADRs 16→verified 13; false ADR-016/018/031 claim removed; predicate retained |
| m-add-1 | Minor | ACCEPTED-FIXED | `_index.md` 4→3; `critic-calibration-log.md` bucket dropped (0 refs) |
| m-add-2 | Minor | ACCEPTED-FIXED | smoke gate scoped to SOT file; path-audit/runner excluded from its green-bar (step 4/6) |
| M3-sev | Minor | ACCEPTED-FIXED | ADR-045 narrowed: ADR-044 cites old name 1×, ADR-045 0 (placeholders) |

Recompute-don't-trust note (for /reflect calibration): the execute-don't-reason
law fired on the Builder's OWN ACCEPTED-FIXED fix (rev-1 numbers were trusted
from non-anchored greps); DR-1 B-add-1/2/3 caught it. Durable fix applied: the
authoritative anchor command is embedded in design.md and build-step-1 grep is
declared single source of truth — narrative reconciled to grep, never
hand-edited. N≥4 with slice-032/034/041 — strong `/critic-calibrate` input.
