# Critique Review: Slice 072 add-psq-2-claim-machinery

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-27
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

First Critic's 11 findings (2B + 4M + 5m) are all VALID with correct severities and the Builder fix-block applies them faithfully on the substantive axes. However the AC5→AC6 split + 12→18 TF-1-row expansion left a confirmed **TPHD-1 sub-mode (a) cross-doc harmonization gap N=6 cumulative** inside design.md itself (L18-19 contradicted L161) — exactly the pattern slice-067 reflection L92 + slice-070/071 lessons predicted. One missed Major (M-add-1) + two missed Minors (m-add-1 milestone prose; m-add-2 parse_queue_text unclaimed-entry shape) surfaced from independent re-review. All 3 missed findings ACCEPTED-FIXED in-band by Builder before TRI-1 lands.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (`_ROOT_ONLY_TOOLS` bucket mismatch) — confirmed; severity Blocker is appropriate. Independently verified at `tests/methodology/test_utf8_stdout_regression.py:76-77` + L121-129 (install_audit bespoke precedent). Builder fix-block adoption (design.md L26 + L168; ADR-067 L51) correctly mirrors install_audit pattern.
- **B2** (R-19 + ADR-064 stale session-id forward-references) — confirmed; severity Blocker is appropriate. Verified at `architecture/risk-register.md:329` ("session-id detection") + `architecture/decisions/ADR-064-...md:37` (same phrase). ADR-067 §Lineage divergence note + design.md R-19 retirement-paragraph spec correctly disambiguate via predecessor-spec-drift framing rather than supersession (ADR-064 append-only). Framework: Wiegers "Software Requirements" §17 spec-drift discipline.
- **M1** (Windows CRLF round-trip via TextIOWrapper newline=None default) — confirmed; severity Major is appropriate. Verified `tools/slice_queue_writer.py:730` uses `write_text` without `newline=`; on Windows translates `\n`→`\r\n`. Builder adds explicit `newline=""`. New TF-1 row `test_parse_queue_text_accepts_crlf_input` closes the read side. Framework: Hendrickson "Explore It!" platform-portability heuristic.
- **M2** (`--release` exit-code ambiguity) — confirmed; severity Major is appropriate. design.md L101-102 now disambiguates (present-unclaimed = exit 0; not-in-queue = exit 2). Framework: Newman "Building Microservices" CLI error-code clarity.
- **M3** (parse_queue_text forward-compat behavior) — confirmed; severity Major is appropriate. design.md L40 extends return-type with `_extra_field_lines` pass-through. Framework: Postel's robustness principle / Fowler forward-compat.
- **M4** (AC5 packs 3 ratchets — N=2 promotion of slice-067 N=1 AC-count signal) — confirmed; severity Major is appropriate. mission-brief.md AC5→AC6 split applied with documented-deviation note citing slice-067 reflection L26 + L77.
- **m1** (`_format_entry` trailing blank-line position) — confirmed; design.md L55 pins insertion at index [-2].
- **m2** (git-config absence-detection mode) — confirmed; design.md L39 specifies the 3-case mode (returncode==1 / configured-empty / git-tool-error).
- **m3** (`--queue` flag TF-1 row missing) — confirmed; new TF-1 row `test_claim_cli_uses_queue_path_override_when_provided` closes the testing-seam gap.
- **m4** (PMI-1 leg-enumeration drift) — confirmed; absorbed into M4 AC5→AC6 split.
- **m5** (BC-PROJ-9 N=8 vs N=9 framing) — confirmed; design.md L26 + ADR-067 L51 now explicitly frame the two counts as same fan-out under different scope.

## Suspicious findings

No suspicious findings — all 11 first-Critic findings are VALID with correct severity and Builder-applied fixes match the proposed remedies.

## Missed findings

Concerns the first Critic didn't flag but the meta-Critic surfaces from independent re-review:

### M-add-1 (Major): design.md §"What's new" L18-L19 carry stale pre-fix-block test-count + AC-tag — TPHD-1 sub-mode (a) cross-doc harmonization gap, intra-document this time

- **Claim under review**: design.md L18 "(~250 LOC, 10 unit tests across the 4 behavioral ACs)" + L19 "(AC5)" both contradict design.md L161 post-fix-block (~330 LOC, 15 unit tests, 18 TF-1 rows total) AND mission-brief.md TF-1 rows L47-48 (paired-pin tests tagged AC=6 after the M4 split).
- **Issue**: Builder swept the test-first-plan §L161 but missed the bullet-list §L18-19 in the same file. This is exactly the **TPHD-1 sub-mode (a) cross-doc harmonization** pattern slice-067 reflection L92 + slice-070/071 lessons logged at N=5 cumulative — slice-072 promotes this to **N=6 cumulative**. Per the slice-040 N+1 first-governed-slice doctrine extended at slice-067 L67, meta-Critic specifically catches Builder-fix-block-introduced regressions on cross-document mechanical consistency.
- **Evidence**: design.md L18-19 (pre-fix-block stale) vs L161 (post-fix-block authoritative); mission-brief.md L47-48 (AC=6 reassignment); slice-067 reflection L92 + slice-071 reflection L78 (N=5 anchor).
- **Severity**: Major (not Minor) — design.md §"What's new" is the load-bearing TL;DR developers read first; an inconsistent test count + AC tag here propagates downstream (a code-Critic reading L18-19 will under-count expected tests by 5).
- **Proposed fix**: design.md L18 → "(~330 LOC, 15 unit tests across AC1-AC4 behavioral surfaces + AC1's CRLF/forward-compat + AC2's configured-empty/--queue/cp1252 + AC3's release-on-unknown)" + add a separate bullet for the bespoke cp1252 test on AC2; L19 → "(AC6 per the AC5→AC6 split documented at mission-brief L23)".
- **Builder draft**: ACCEPTED-FIXED — design.md §"What's new" rewritten with the post-fix-block counts + AC tags; bespoke cp1252 test surfaced as its own bullet; AC6 reassignment cited.
- **Framework anchor**: Fowler "Refactoring" duplication-as-design-smell §3 + Sommerville "Software Engineering" §9 traceability.

### m-add-1 (Minor): milestone.md L29 "Current focus" prose retains AC5-packed shape contradicting Critic M4 Builder-draft commitment

- **Claim under review**: critique.md M4 Builder-draft explicitly committed "update milestone.md 'current focus' + design.md L77 references". milestone.md L29 still describes AC5-packed work without acknowledging the AC5/AC6 split or the 6-AC count.
- **Issue**: Builder-commitment-not-honored sweep gap. Prose is human-readable summary so non-load-bearing for audits, but inconsistent with the Builder draft.
- **Severity**: Minor (cosmetic).
- **Proposed fix**: milestone.md L29 gains an AC5/AC6 split sentence + cites slice-067 N=1 → slice-072 N=2 documented deviation.
- **Builder draft**: ACCEPTED-FIXED — milestone.md L29 rewritten with the AC5/AC6 split acknowledgment + meta-Critic-extend disposition count + 18 TF-1 rows + slice-067 N=1 → slice-072 N=2 citation.

### m-add-2 (Minor): design.md L40 `parse_queue_text` return-dict spec underspecifies unclaimed-entry shape

- **Claim under review**: design.md L40 says the return dict is `{candidate_name: {"claimed_by": ..., "claimed_at": ..., "_extra_field_lines": [...]}}` but does not specify whether unclaimed entries (claim keys absent) still appear in the dict.
- **Issue**: Matters for (i) the §"Pre-finish dogfood" battery 1 assertion "tests assert claim-absent state across all 10 entries" (requires all 10 to appear), (ii) `write_slice_queue`'s merge loop — if an unclaimed entry's value-dict has no `claimed_by` key, copying it would KeyError; if the dict omits unclaimed entries entirely, forward-compat `_extra_field_lines` on unclaimed entries would not be preserved across regen.
- **Severity**: Minor (resolvable at build via implementation choice, but spec ambiguity is exactly the parse-rule-precision class APED-1 promotion is supposed to catch — N=3 candidate per slice-071 reflection L76).
- **Proposed fix**: design.md L40 gains a sentence — "Returns ALL entries in the queue (claimed or not); unclaimed entries appear with `claimed_by`/`claimed_at` keys ABSENT (use `dict.get()` at consumer sites) but `_extra_field_lines` present (possibly empty list)." Also update `write_slice_queue` merge loop spec to use `.get()` to tolerate the absent-key case.
- **Builder draft**: ACCEPTED-FIXED — design.md L40 `parse_queue_text` spec extended with the all-entries-returned-with-absent-keys-on-unclaimed semantics; `write_slice_queue` merge step updated to use `.get()` per the new contract.
- **Framework anchor**: Wiegers "Software Requirements" §11 explicit-spec-of-corner-cases.

## Severity adjustments

No severity adjustments — all 11 first-Critic findings have correct severity classification. Builder fix-block dispositions (all 11 ACCEPTED-FIXED) match the proposed remedies.

## Notes

- **Confidence**: high on M-add-1 (intra-document inconsistency is empirically verifiable by direct file read; matches slice-067 N=3 + slice-070/071 N=5 TPHD-1 cumulative pattern → N=6 promotion at slice-072). Medium on m-add-1 (Builder commitment was explicit but milestone surface is non-load-bearing). Medium on m-add-2 (spec ambiguity is real but bounded to 3 implementation choices).
- **Calibration observation**: the first Critic's coverage of the substantive design surface (B1/B2/M1-M4/m1-m5) is structurally complete — every cited concern is well-grounded with file:line evidence and framework anchor. The single specialization gap matches the documented N=5 cumulative TPHD-1 sub-mode (a) cross-document harmonization pattern (first-Critic catches design-Critic substance; meta-Critic catches mechanical sweep gaps the Builder fix-block introduces). Recommend slice-073 reflection log M-add-1 as **N=6 cumulative on TPHD-1 sub-mode (a)** to keep /critic-calibrate promotion-threshold pressure on.
- **N+1 first-governed-slice doctrine**: PSQ-2 is the first slice to exercise the M4 AC-split mechanic (after slice-067's N=1 AC-count signal); the Builder fix-block's stale-anchor sweep gap at L18-19 is the canonical N+1 mechanic-specific catch surface. Pattern stable.
