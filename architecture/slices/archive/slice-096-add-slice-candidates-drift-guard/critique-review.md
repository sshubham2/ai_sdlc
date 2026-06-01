# Critique Review: Slice 096 add-slice-candidates-drift-guard

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-01
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is substantively sound: all three Majors (M1 false-precedent, M2 stale id, M3 merge-mischaracterization) and m1 are VALID on their original merits, verified against the actual enforcing artifacts, and the Builder's ACCEPTED-FIXED edits are accurate. The EXCLUDE disposition is genuinely safe — I independently confirmed no methodology-changelog enforcer, count-pin, parity test, or version-sync gate trips on an EXCLUDE slice-096. One Minor surfaces that the first Critic missed (the SCMD-1 6-column / `Machine-cmd` requirement on the new shippability row), and there is a single calibration observation on M1's Major/Minor boundary that I do not file as a severity change.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **M1: false-precedent in MEPD-1 leg 2 — VALID, Major appropriate.** The original leg-2 framing ("member-adds never get a changelog entry / landed as a per-skill test extension only") is factually false against the vault. Confirmed at `tests/methodology/test_methodology_changelog.py:3380` (slice-051 v0.59.0 OSDG-1 reflect-member entry-pin + ADR-053 + row #51) and `:5446` (slice-088 v0.78.0 "OSDG-1 guarded-set extended"). Both prior OSDG-1 member-adds WERE changelog-recorded. The Builder's rewrite to the co-occurring-rule-event basis (design.md §Sub-decisions leg 2) is accurate, and the "verified against `test_methodology_changelog.py` / version-gate stays 0.78.0" sentence is now present and correct. Major is defensible: this is a verifiability defect (Wiegers) in a must-not-defer gated artifact, and the slice-032 m1 false-precedent anti-pattern is explicitly in-framework. (See Notes for the Major/Minor boundary.)

- **M2: stale shippability id 101 — VALID, Major appropriate.** Independently verified `architecture/shippability.md` on master: 100 rows, max `#`-id = 101, only id 76 missing, and `| 101 | slice-093-add-external-vault-support` is the tail. The original "next id 101" was computed against a pre-slice-093 tree and would have *duplicated slice-093's id at base time* — a correctness defect, not merely a merge-time concern. The Builder's fix to 102 (+ "re-confirm `max+1` at build") at all three design sites (L10/L34/L61) is correct.

- **M3: shippability merge mischaracterization — VALID, Major appropriate.** Confirmed `_merge_shippability` (`tools/parallel_conflict_resolver.py:1814-1822`) raises `_SoftResolutionError(..., ConflictClass.HARD)` on same-`#`-id/different-content, keyed on the `#`-id integer via `_parse_shippability_rows` regex `^\|\s*(\d+)\s*\|` (`:1853`). The original "additive append, NOT a code collision / PCR machinery owns it" framing was wrong on the *mechanism*. The HARD-STOP is genuinely reachable: both in-flight slices (094 VWS-1, 095 SVW-1) are INCLUDE slices that each append a shippability row, so three concurrent appends WILL collide on the `#`-id. The Builder's rewrite ("cheap manual-renumber HARD-STOP, not silent union") is accurate, not an overcorrection.

- **m1: AC2 parity over-claim — VALID, Minor appropriate.** Confirmed `CLAUDE.md:42` already omits `pulse` and `code-review` from the OSDG-1 enumeration despite both having drift tests, and no enumeration↔drift-test parity pin exists (see Missed-findings note on why this is structurally true). The Builder's softening to "courtesy-parity, R-13 gap only" is accurate.

- **m2: docstring mislabel — VALID, Minor, DEFER appropriate.** `_parse_shippability_rows` docstring (`:1786`, `:1845`) does say "slice number" while the regex keys on the `#`-id integer. Out-of-scope to fix here (slice-094's file; "refactors need a slice") is the correct disposition.

## Suspicious findings

No suspicious findings. I specifically probed for over-reach on M2 and M3 per the task brief:

- **M2 is not inflated to Major.** Although M3's manual-renumber-at-merge makes the *exact* id secondary at merge time, M2 stands on its own at base time: id 101 would duplicate slice-093's existing row immediately, independent of any parallel merge. Major holds.
- **M3 is not a phantom risk.** The HARD-STOP is reachable in this slice's actual trajectory (094 + 095 both append rows). Major holds.

## Missed findings

- **m-add-1: New shippability row #102 must carry the 6th `Machine-cmd` column (SCMD-1), not just a valid Command — Minor.** The catalog header is `| # | Slice | Critical path | Command | Runtime | Machine-cmd |` (6 columns; verified row 101 has 7 pipes / 6 cells). `tests/methodology/test_shippability_command_column.py::test_every_row_has_machine_stable_command_or_violation` runs against the *real* catalog (SCMD-1, ADR-031) and FAILs with `missing-machine-cmd` / `prose-segment` if the new row omits or malforms the `Machine-cmd` cell. design.md L35 says only "the row's Command must be a valid, green pytest invocation"; the critique's Cross-cutting-conformance dimension names PTFCD-1, SCPD-1/RPCD-1 but not SCMD-1. Framework: Newman (contract test — the catalog's column grammar is an enforced contract on every new row). Proposed fix (build-mechanics note, not a design change): the Builder must clone the full 6-column shape from row 101 — both the `<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/test_slice_candidates_skill_drift.py --no-header -q` Command cell AND the `<interp> -m pytest ...` `Machine-cmd` cell. Low risk (cloning row 101 yields this automatically), but it belongs in the design's cross-cutting list alongside PTFCD-1 because SCMD-1 is a hard validate-gate, not a soft one.

No other missed findings. I verified the four false-negative vectors the task flagged and found EXCLUDE genuinely safe:
- **No changelog enforcer trips**: no assertion in `test_methodology_changelog.py` fires on a missing slice-096 entry; the only version-sync gate is `test_version_files_synchronized_at_v_0_78_0` (`:5496`), which asserts `VERSION == "0.78.0"` exactly — EXCLUDE keeps it green; an INCLUDE bump would break it absent a rename/supersede. The first Critic's blocker-section reasoning is correct.
- **No guarded-skill count-pin / drift-test-set enumeration exists**: searched all of `tests/`; the only set-level guard is `test_skill_drift_normalization.py::_GUARDED_GLOBS` which uses the blanket glob `skills/**/SKILL.md` (already matches `slice-candidates`), requiring no update. The CLAUDE.md↔drift-test parity claimed in m1 is genuinely unpinned.
- **BCR-1 R-13 references are docstring-only**: `test_bcr_1_backlog_round_trip.py:337/358` mention "R-13 deferred OSDG-1 extension to /slice-candidates" only as rationale prose; the assertions pin `skills/reflect/SKILL.md` content (`SC-\d{3}`, `**Closes:** SC-`), which slice-096 does not touch. Closing R-13 does NOT trip them — no false negative.
- **The new test collects and passes day-one**: installed copy exists (`~/.claude/skills/slice-candidates/SKILL.md`, 11567 bytes); EOL-normalized content-equal to in-repo (both normalize to 11479 chars); conftest `REPO_ROOT = parents[2]` resolves; the file is LF-clean in the working tree (zero CRLF/CR), so it also stays green under `test_guarded_md_files_have_no_crlf_in_working_tree`.

## Severity adjustments

No severity adjustments. I considered downgrading M1 to Minor (it changes no code, no AC, no disposition — only rationale prose, and the EXCLUDE verdict was independently correct). I declined: M1 corrects a *factually false* precedent inside a must-not-defer gated artifact, and the first Critic's own slice-032 anti-pattern framework treats unverified "slice-NNN did/didn't X" precedents as a calibration-grade defect (rubber-stamp risk), not cosmetics. Major is defensible. See Notes.

## Notes

Confidence in this review is high — every load-bearing claim was verified against the real master tree (shippability ids, `_merge_shippability` HARD-STOP logic, the two changelog entry-pins, the version-sync gate, the installed SKILL copy, EOL-normalized equality, and the absence of any count/parity pin), not against prose. Calibration observation on the first Critic's pattern in this slice: the three Majors are all *mechanical-accuracy* findings (a false precedent, a stale id, a mischaracterized merge) caught by reading implementations rather than rubber-stamping the design's prose — exactly the Critic's intended mode, and a healthy pattern (no pattern-blindness; the one Blocker-candidate, the EXCLUDE disposition, was correctly cleared, not missed). My only reservation is a mild one: the first Critic's "Contract gaps — none" and "Cross-cutting conformance" dimensions enumerated PTFCD-1/SCPD-1/RPCD-1 but skipped SCMD-1's 6-column requirement on the new row (m-add-1) — a small coverage gap in the catalog-contract dimension, not a calibration failure. The single Major/Minor boundary on M1 is a judgment call I'd flag to the user at TRI-1 if they prefer a strict "no build/disposition impact ⇒ Minor" rule, but I do not file it as SEVERITY-WRONG.
