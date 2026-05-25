# Critique Review: Slice 062 extend-r15-corpus-class-closure-scope

**Reviewed by**: critique-review agent (DR-1 meta-Critic)
**Date**: 2026-05-23
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

**Disposition context** (not part of the audit-parsed verdict fields above): all 6 first-Critic findings (B1, M1, m1-m4) were ACCEPTED-FIXED at the /critique fix block; the 3 dual-review missed-findings (M-add-1, M-add-2, M-add-3) were ACCEPTED-FIXED at this /critique-review fix block; TF-1 audit clean post-fix verified empirically (`$PY -m tools.test_first_audit ... --json` exit 0, `violation_count: 0`, 8 rows across 4 ACs).

## Summary

The first Critic's 6 findings (B1, M1, m1-m4) all hold up as VALID at correct severity; all 6 ACCEPTED-FIXED edits land faithfully on disk. The meta-Critic surfaced 3 missed findings — one Blocker (M-add-1) and two Minors (M-add-2, M-add-3):

- **M-add-1 (Blocker)**: the m3 ACCEPTED-FIXED edit (replacing the mission-brief 4-row TF-1 plan with a 7-row table copied from design.md) introduced multi-AC labels `"1, 3"` and `"(audit-trace)"` markers that `tools/test_first_audit.py:_normalize_ac_label` rejects, producing 2 `ac-without-row` violations on AC#3 and AC#4 that would FAIL `/build-slice` Step 6 strict-pre-finish. **The EXACT same defect class slice-056 /critique-review M-add-1 caught and enshrined as a TF-1 anti-pattern (slice-040 N+1 doctrine; recurrence on slice-062 is N=2).** Meta-Critic ran `$PY -m tools.test_first_audit` empirically pre-fix → 2 violations confirmed.
- **M-add-2 (Minor)**: cross-document option-enumeration incoherence — ADR-060 numerals 1-4, design.md mentions "3 options / option B / option A", mission-brief lists (a)/(b)/(c) — three schemes for the same set of options + the chosen ADR option 3 was not present in the mission-brief enumeration.
- **M-add-3 (Minor)**: design.md Phase C step 11 said "4-part Inclusion-heuristic structure" — confusable with the 4-part PMI-1 bump that B1 just corrected to 5-part; the "4-part" qualifier was novel terminology not appearing elsewhere in the repo.

All 3 ACCEPTED-FIXED in the dual-review fix block. Post-fix `$PY -m tools.test_first_audit` exits 0 with `violation_count: 0` and 8 rows parsing across all 4 ACs (empirically verified at /critique-review fix block).

## Confirmed findings (first Critic was right)

| ID | Severity | Status | Notes |
|----|----------|--------|-------|
| B1 | Blocker  | VALID + correct severity | PVFS-1 enforcing test at `tests/methodology/test_pyproject_version_matches_version_file.py:126-146` re-verified; 4-part bump would deterministically FAIL Step 6. 7-site propagation fix landed cleanly. |
| M1 | Major    | VALID + correct severity | slice-060 reflection L37 nomination verbatim verified; mission-brief Out-of-scope bullet 1 acknowledged-divergence note + 3-clause justification landed. |
| m1 | Minor    | VALID + correct severity | Independent grep confirms `"walker actually visits"` / `"self-test that the walker"` 0 matches. Paraphrase + disclaimer landed at ADR-060 L47. (Side note: the new paraphrase mildly over-claims slice-057 Discovered framing as "build-time-reachable gate-caught defect" — slice-057 frames it as a positive confirmation; the disclaimer covers it. No further fix needed.) |
| m2 | Minor    | VALID + correct severity | `tests/methodology/test_methodology_changelog.py:3943` SECTION-header pattern verified; EPGD-1 placement directive landed at design.md Phase C step 14. |
| m3 | Minor    | VALID at surface level | TPHD-1 sub-mode (a) row-count harmonization landed — BUT introduced M-add-1 defect at audit-execution level (see below). |
| m4 | Minor    | VALID + correct severity | `risk-register.md:266` slice-057 prose verified; historical-record framing landed at design.md Phase C step 15. STP-1 Sub-form B (regex over Python function names per `tools/state_transition_pin_audit.py:84-86`) does NOT grep markdown prose, so the literal prose poses no STP-1 confusion risk (hot zone (g) ruled out). |

## Suspicious findings

None. Each first-Critic finding holds under independent re-grounding. Specifically checked and rejected as suspicious:
- B1's Blocker severity is not over-rated (PVFS-1 failure is build-time-deterministic, not contingent).
- m1's grep was thorough (meta-Critic re-ran across full repo + adjacent phrasings).

## Missed findings (the first Critic should have caught these)

### M-add-1 (Blocker): TF-1 strict-pre-finish gate WILL FAIL — multi-AC labels `"1, 3"` and `"(audit-trace)"` markers do not satisfy ACs #3 and #4

- **Issue**: mission-brief.md Acceptance criteria L16-19 enumerates 4 numbered ACs → `_find_acs()` yields `["1","2","3","4"]`. The 7-row TF-1 plan (L25-33, freshly minted by the m3 ACCEPTED-FIXED harmonization edit) used AC cells `"1, 3"` (rows 1-3), `"1"` (row 4), `"2"` (row 5), `"(audit-trace)"` (rows 6-7). `tools/test_first_audit.py:_normalize_ac_label` does `s.lower().replace("ac","").replace("#","").replace(" ","")` — applied to `"1, 3"` it yields `"1,3"` (comma is NOT stripped) which doesn't match bare `"3"`; applied to `"(audit-trace)"` it yields `"(audit-tre)"` (note `.replace("ac","")` strips the inner `ac`) which doesn't match bare `"4"`. The audit then checks `if ac not in rows_by_ac` for each AC in `acs_in_brief`.
- **Empirical pre-fix run** (meta-Critic):
  ```
  $ $PY -m tools.test_first_audit architecture/slices/slice-062-extend-r15-corpus-class-closure-scope --json
  → violation_count: 2
  → AC#3 is declared in the brief but has no test-first row
  → AC#4 is declared in the brief but has no test-first row
  ```
- **Framework**: Hendrickson TF-1 gate semantics + Sommerville bidirectional AC↔test traceability. TF-1 strict-pre-finish runs at `/build-slice` Step 6; non-zero exit halts the slice.
- **Why first Critic missed**: the first Critic verified table-shape harmonization between mission-brief and design.md (sub-mode (a)) but did not run `tools/test_first_audit.py` against the rendered mission-brief. This is the EXACT defect class slice-056 /critique-review M-add-1 caught + ACCEPTED-FIXED (see `architecture/slices/archive/slice-056-fix-bcr1-round-trip-test-archive-paths/critique-review.md:35-48`, including the explicit Builder note "the canonical multi-row-per-AC fix path that actually passes TF-1 strict-pre-finish"). slice-040 N+1 doctrine: discipline lesson minted in slice N (056) is blind-spot on slice N+M (062); **N=2 recurrence on the TF-1-multi-AC-label sub-class specifically**.
- **Severity**: Blocker. Build-time-deterministic Step 6 HALT.
- **Builder draft**: **ACCEPTED-FIXED** in same dual-review fix block. Applied at mission-brief.md L25-35 (TF-1 plan table rewritten to 8 rows with bare-numeric AC labels per slice-056 multi-row-per-AC precedent) and design.md L162-174 (mirrored harmonization per TPHD-1 sub-mode (b)). New shape: 4 rows for AC#1 (3 per-corpus + 1 orphan-check); 1 row for AC#2 (lazy-repoint); 1 row for AC#3 (test-first sequencing proof — reuses the `tests_skills_corpus` test where the mid-slice smoke FAIL→PASS is observed); 2 rows for AC#4 (v0.65.0 entry-pin + shippability-propagation). Empirically re-run at /critique-review fix block: `$PY -m tools.test_first_audit ... --json` → `violation_count: 0`, exit 0, 8 rows parsing cleanly across all 4 ACs.

### M-add-2 (Minor): cross-document option-enumeration incoherence (3 schemes for the same set of ADR options)

- **Issue**: ADR-060 §"Options considered" enumerates 4 options as numerals (1, 2, 3, 4); §"Decision" picks "**Option 3**" (correct: extract helper + per-corpus tests + aggregated integrity test). But design.md L58 said "3 options weighed; option B selected"; L181 said "ADR-060 Decision (option B rationale)"; L189 said "rejected (option A from /design-slice ASK)"; and mission-brief.md L52 must-not-defer #5 enumerated (a)/(b)/(c) — only 3 options, and (a)=ADR-option-1, (b)=ADR-option-2, (c)=ADR-option-4 — meaning the chosen ADR option 3 literally did not appear in the mission-brief enumeration.
- **Framework**: Wiegers requirements-design traceability + Fowler refactoring naming consistency; FBCD-1 sub-mode (a) cross-file consistency.
- **Why first Critic missed**: the first Critic focused on substantive technical findings (B1 PVFS-1, M1 deferral chain) and didn't pattern-match the option-label drift across 3 documents.
- **Severity**: Minor (cross-document cosmetic; the build-time gates do not parse option labels).
- **Builder draft**: **ACCEPTED-FIXED** in same dual-review fix block. Pick ONE scheme: ADR-060's numeric 1-4. Updates landed at: design.md L58 ("3 options weighed; option B selected" → "4 options considered in ADR-060 §Options-considered; option 3 selected"); design.md L181 ("option B rationale" → "option 3 rationale"); design.md L189 ("option A from /design-slice ASK" → "ADR-060 option 2 — the in-place body extension + rename variant; presented in the /design-slice ASK as option A"); mission-brief.md L52 must-not-defer #5 rewritten to defer to ADR-060 as authoritative enumeration ("ADR-060 weighs 4 candidate shapes; option 3 selected").

### M-add-3 (Minor): design.md Phase C step 11 "4-part Inclusion-heuristic structure" — novel terminology + stale-carry reading risk adjacent to step 12's 5-part PMI-1

- **Issue**: design.md L150 read *"Append `## v0.65.0 — 2026-05-23` methodology-changelog entry (4-part Inclusion-heuristic structure following the v0.59.0 / v0.64.0 templates)"*. The phrase "4-part Inclusion-heuristic structure" appears nowhere else in the repo (verified by grep). Adjacent to step 12's correctly-stated **5-part PMI-1 atomic bump** (and given the slice was just touched by B1's "4-part → 5-part" correction), a future Builder/reader could plausibly mis-read "4-part" here as a stale carry from the pre-B1-fix design and propagate a 4-part PMI-1 bump.
- **Framework**: Fowler naming consistency; FBCD-1 sub-mode (a) cross-file consistency on its own ACCEPTED-FIXED fix block (slice-022 self-violation law).
- **Why first Critic missed**: the first Critic verified the bump-shape correction landed at the 5 enumerated propagation sites (B1 fix block) but didn't verify step 11's prose didn't carry a confusable "4-part" qualifier.
- **Severity**: Minor (CSP-1 row at design.md L185 structurally pins the 5-part discipline via the v0.65.0 entry-pin substring assertion, so the LIVE BEHAVIOR is safe — but cheap to disambiguate).
- **Builder draft**: **ACCEPTED-FIXED** in same dual-review fix block. Applied at design.md L150 Phase C step 11; rewrote to "Append `## v0.65.0 — 2026-05-23` methodology-changelog entry following the v0.59.0 / v0.64.0 entry-body template (one-paragraph summary + ### Added/### Changed block + Rule reference line + Defect class line + Validation line, per the methodology-changelog.md L17-31 format spec). The **bump shape is 5-part PMI-1** per step 12 below — explicitly NOT 4-part. The v0.65.0 entry body MUST contain the substring `"5-part PMI-1 atomic bump"` (asserted by the new entry-pin test per the CSP-1 cross-spec parity table)." Removes the ambiguous "4-part" qualifier + makes the entry-body vs bump-shape distinction explicit.

## Severity adjustments

None. The first Critic's B1/M1/m1-m4 severities are appropriate.

## Calibration signal (for `/critic-calibrate` + slice's `/reflect`)

- **Slice-040 N+1 doctrine recurrence on the TF-1-multi-AC-label sub-class**: N=2 cumulative (slice-056 /critique-review M-add-1; slice-062 /critique-review M-add-1). Per slice-037 audit-vs-real-artifact law, build-time-reachable classes (TF-1 gate at Step 6) are typically left to the gate itself — but N=2 promotion candidate via `/critic-calibrate` is now active: *"if the slice edits a TF-1 plan table (mission-brief.md or design.md), run `$PY -m tools.test_first_audit <slice-folder> --strict-pre-finish` against the post-edit mission-brief AS A /critique SURFACE CHECK (not just a /build-slice Step 6 deferred check)."* Recommend appending to slice-062's `reflection.md` Pattern section.
- **First-Critic pattern in slice-062**: 5/6 findings on cross-document coherence + naming + citation hygiene; 1/6 on substantive technical correctness (B1 PVFS-1). Suggests the first-Critic-pass is reliably catching prose-and-citation drift but under-reaching on build-time-gate-reachable defects in its own fix-block edits — N=2 calibration signal (slice-056 + slice-062) for the meta-Critic to retain a structural role as the "post-fix-block empirical re-check" layer.
- **Self-violation of m3 fix-block**: the m3 ACCEPTED-FIXED edit itself introduced M-add-1 — a slice-022 RSAD-1 self-violation pattern (the fix codifying a discipline self-violates the same discipline). Worth noting in `/reflect`'s "Discovered" section as the slice-022 RSAD-1 lineage extending to the dual-Critic stack's same-fix-block edits.

## Files relevant to this review

- `<HOME>\ai_sdlc\architecture\slices\slice-062-extend-r15-corpus-class-closure-scope\mission-brief.md`
- `<HOME>\ai_sdlc\architecture\slices\slice-062-extend-r15-corpus-class-closure-scope\design.md`
- `<HOME>\ai_sdlc\architecture\decisions\ADR-060-extend-r15-corpus-backstop-scope.md`
- `<HOME>\ai_sdlc\tools\test_first_audit.py` (the TF-1 audit M-add-1 trips pre-fix; empirically verified clean post-fix)
- `<HOME>\ai_sdlc\tests\methodology\test_pyproject_version_matches_version_file.py` (PVFS-1 enforcing test cited by B1)
- `<HOME>\ai_sdlc\tests\methodology\test_methodology_changelog.py` (slice-060 entry-pin SECTION header at L3943 cited by m2/B1)
- `<HOME>\ai_sdlc\architecture\slices\archive\slice-056-fix-bcr1-round-trip-test-archive-paths\critique-review.md` (slice-056 M-add-1 precedent — N=1 of the N+1 doctrine for M-add-1 here)
- `<HOME>\ai_sdlc\architecture\slices\archive\slice-060-add-code-review-skill\reflection.md:37` (verbatim slice-062 TRI-1 nomination cited by M1)
- `<HOME>\ai_sdlc\architecture\slices\archive\slice-060-add-code-review-skill\reflection.md:50` (verbatim "B2 PMI-1 4-part vs 5-part: VALIDATED" cited by B1)
