# Critique: Slice 012 bc-proj-2-negative-anchor-migration

**Critic reviewed**: mission-brief.md, design.md, ADR-011-bc-proj-2-negative-anchor-migration.md
**Date**: 2026-05-13
**Result**: CLEAN (all 5 findings dispositioned ACCEPTED-FIXED in-round)

## Summary

The Critic verified the design's empirical claims hold end-to-end (Audit 1 disjointness, Audit 2 slice-001 backward-compat, Audit 5 self-application all reproduced against the live `tools/build_checks_audit.py`). Findings concentrate on three classes: (1) **B1** — AC #4's test specification is structurally unable to produce TF-1 genuine PENDING → WRITTEN-FAILING because all 9 negative-anchor tokens already exist file-globally on BC-PROJ-1's `architecture/build-checks.md:20` line from slice-008's migration; (2) **M1** — ADR-011 Reversibility + design.md Phase 1b under-specified the entry-pin-vs-PMI-1-gate structural separation discipline per slice-011's NEW Dim 9 sub-class N=1 lesson; (3) **M2** — Audit 3's empirical numbers were inflated (claimed 7/47, actual 5/8 distinct-token matches). All 5 findings ACCEPTED-FIXED in-round; design.md + mission-brief.md + ADR-011 updated; ADR-011 renamed to shorter slug. **B1 is itself a recursive-self-application catch** — slice-012 encoding "data-only migration of a Negative anchors line" couldn't enforce that BC-PROJ-2 specifically receives the data because the slice's own naive verification approach would pass against slice-008's data already in place.

## Findings

### Blockers (must address before /build-slice)

#### B1: AC #4 test-first row is structurally unable to produce a genuine PENDING → WRITTEN-FAILING transition unless scoped to the parsed BC-PROJ-2 rule

- **Claim under review**: mission-brief.md test-first row 4 (`test_bc_proj_2_has_methodology_vocabulary_negative_anchors`) + verification plan row 4 ("pytest reads `architecture/build-checks.md`; locates BC-PROJ-2 rule section; asserts `Negative anchors:` line present; asserts all 9 canonical tokens present"); design.md § "Components touched" — "1 new test function `test_bc_proj_2_has_methodology_vocabulary_negative_anchors`".
- **Issue**: All 9 canonical tokens (`defer-with-rationale`, `aggregated lessons`, `false positive`, `meta-discussion`, `vocabulary`, `Critic-MISSED`, `back-sync`, `Dim 9`, `forward-sync`) are **already present in `architecture/build-checks.md` pre-migration** because slice-008 wrote them on BC-PROJ-1's Negative-anchors line at L20. A test that only asserts file-level token presence + the literal substring `Negative anchors:` (present anywhere in the file, including the L20 BC-PROJ-1 line) would **PASS pre-migration** — violating TF-1's PENDING → WRITTEN-FAILING genuine-failure discipline (N=8 stable per slice-011 reflection).
- **Evidence**: Live grep on `architecture/build-checks.md` L20 confirms BC-PROJ-1 already has `**Negative anchors**: defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync`. Empirically: pre-migration each of the 9 tokens has `count == 1` file-globally; post-migration each has `count == 2`. Only a per-rule-scoped test distinguishes them. The slice-008 template at `tests/methodology/test_build_checks_audit.py::test_migrated_rules_have_expected_negative_anchors` (L1054-L1120) uses `_parse_rules(text, source='project', path=...)` + `by_id['BC-PROJ-1'].negative_anchors == expected_tuple` to anchor on the parsed `BuildCheckRule` dataclass.
- **Proposed fix**: Pin the AC #4 test implementation discipline in design.md (and the must-not-defer TF-1 bullet) to use `_parse_rules` + `by_id['BC-PROJ-2'].negative_anchors == expected_negative_anchors`. Add a pinned failure signal to the TF-1 row 4 status: `AssertionError: BC-PROJ-2 negative_anchors mismatch: got (), expected (...)`.
- **Builder draft**: ACCEPTED-FIXED — design.md L12 "Components touched / tests/methodology/test_build_checks_audit.py" updated to require `_parse_rules` + `by_id['BC-PROJ-2'].negative_anchors == expected_negative_anchors` per-rule scoping with explicit citation of slice-008's `test_migrated_rules_have_expected_negative_anchors` template at L1054; mission-brief.md TF-1 Notes bullet updated with pinned failure signal `AssertionError: BC-PROJ-2 negative_anchors mismatch: got (), expected (...)`; design.md AC trace table row 4 explicitly references `_parse_rules` + `by_id` shape and rejects "Markdown line content matching" as the verification mode.

### Majors (address this slice)

#### M1: ADR-011 § Reversibility under-counts the supersession surface; Phase 1b INSERT discipline + Phase 1c narrow-scope discipline were under-specified

- **Claim under review**: ADR-011 § Reversibility — "delete 4 audit tests + 1 entry-pin test; revert PMI-1 versioned-gate"; design.md § Implementation order, Phase 1c — "Edit `old_string` MUST scope to ONLY the gate function body".
- **Issue**: ADR-011's reversibility prose lumped "5 new tests" together without distinguishing entry-pin functions (persist across all versions; v0.22.0..v0.26.0 entry-pins must NEVER be touched in a v0.27.0 revert) from PMI-1 versioned-gate functions (latest-only supersession). Slice-011's L29 lesson explicitly distinguishes these — the slice-011 build-time slip was that the Edit's `old_string` accidentally spanned a SECTION header containing both function classes. Slice-012's Phase 1b was silent on INSERT discipline (where + under what SECTION header to insert the new entry-pin function); Phase 1c described the narrow-scope Edit correctly but didn't tie it to the file's actual structure (`# --- PMI-1 cleanliness gate at v0.26.0 ---` SECTION already separate from entry-pin SECTIONs).
- **Evidence**: Critic verified empirically that `tests/methodology/test_methodology_changelog.py` L300 has the PMI-1 gate under its own `# --- PMI-1 cleanliness gate at v0.26.0 ---` SECTION header — separate from each entry-pin function's `# --- Slice-NNN / RULE entry pinning ---` SECTION header. The structural separation already exists; slice-012's discipline must preserve it.
- **Proposed fix**: (a) design.md Phase 1b explicitly: insert under NEW `# --- Slice-012 / BC-PROJ-2 entry pinning ---` SECTION header containing ONLY the new function; (b) design.md Phase 1c explicitly: `old_string` targets ONLY the gate function body + its dedicated SECTION header (separate Edit); (c) ADR-011 Reversibility — clarify entry-pin function distinction; (d) add Audit 6 confirming the structural separation pre-Edit.
- **Builder draft**: ACCEPTED-FIXED — design.md Phase 1b updated with explicit INSERT discipline + NEW SECTION header naming; Phase 1c updated with explicit narrow-scope Edit discipline tied to the verified structural separation; Audit 6 added to design.md § "Design-time empirical verification" confirming `# --- PMI-1 cleanliness gate at v0.26.0 ---` SECTION header is separate from entry-pin SECTION headers in the current file; ADR-011 § Reversibility step 3 updated to clarify entry-pin functions for v0.22.0..v0.26.0 are NOT touched (only the v0.27.0 entry-pin); step 4 updated to clarify the revert Edit also targets only the gate's dedicated SECTION header. **N=2 promotion probe**: if slice-012 ships clean, the entry-pin-vs-PMI-1-gate-conflation Dim 9 sub-class candidate (slice-011 N=1) ratchets to N=2 → promote at slice-013+.

#### M2: Audit 3 inflated empirical counts (claimed 7/47, actual 5/8 distinct-token matches)

- **Claim under review**: design.md § "Design-time empirical verification" — Audit 3: "slice-005: 7 matches ... slice-011: 47 matches".
- **Issue**: The Critic ran the exact 9-token word-boundary regex over the union of slice-011's mission-brief.md + design.md and got **8 distinct negative-anchor TOKEN matches**, not 47. Slice-005's claimed "7 matches" is actually **5** by the same measurement. The 47 figure conflated per-occurrence count with distinct-token-match count. Per Wiegers (every claim traces to evidence) and slice-008's Wiegers AC-trace sub-class + slice-009/010/011 N=10-stable empirical-verification-at-design-time discipline, design.md numbers should match what the actual verifier produces.
- **Evidence**: Live audit via `re.search(rf'\b{re.escape(na)}\b', text.lower())` over the union: slice-005 → 5 distinct tokens (`defer-with-rationale`, `aggregated lessons`, `false positive`, `meta-discussion`, `vocabulary`); slice-011 → 8 distinct tokens (`defer-with-rationale`, `aggregated lessons`, `meta-discussion`, `vocabulary`, `Critic-MISSED`, `back-sync`, `Dim 9`, `forward-sync`).
- **Proposed fix**: Replace Audit 3's prose numbers with the actual reproducible distinct-token-match counts (5 / 8), with explicit measurement definition.
- **Builder draft**: ACCEPTED-FIXED — design.md Audit 3 updated: slice-005 count corrected 7→5; slice-011 count corrected 47→8; explicit measurement definition added ("distinct token = 1 if `re.search(rf'\b{re.escape(tok)}\b', text.lower())` matches at least once across mission-brief.md + design.md union"). ≥1 distinct token still suffices for suppression — AC #1 + AC #2 outcomes unchanged.

#### M3: ADR-007 vault-ref filename drift; ADR-011 filename overly long

- **Claim under review**: mission-brief.md § Dependencies — "Vault refs: ... [[decisions/ADR-007-bc-1-v1-2-negative-context-anchors]]"; ADR-011 filename `ADR-011-bc-proj-2-negative-anchor-migration-completing-bc-1-v1-2-rollout.md` (75 chars before `.md`).
- **Issue**: Mission-brief.md cites `[[decisions/ADR-007-bc-1-v1-2-negative-context-anchors]]` but the actual filename is `ADR-007-bc-1-negative-context-anchors-via-final-filter.md`. The vault-ref does not resolve. ADR-011's filename is unusually long — most ADRs in the repo cap around 60 chars (ADR-007 is 51 chars).
- **Evidence**: `Glob architecture/decisions/ADR-007*` returns exactly `ADR-007-bc-1-negative-context-anchors-via-final-filter.md` (single match). Mission-brief's slug is a different filename.
- **Proposed fix**: (a) Update mission-brief.md vault-ref to correct filename. (b) Shorten ADR-011 filename to e.g., `ADR-011-bc-proj-2-negative-anchor-migration.md` (45 chars).
- **Builder draft**: ACCEPTED-FIXED — (a) mission-brief.md Dependencies vault-ref corrected to `[[decisions/ADR-007-bc-1-negative-context-anchors-via-final-filter]]` matching actual filename; also added back the missing `~/.claude/build-checks.md` vault-ref. (b) ADR-011 file renamed from `ADR-011-bc-proj-2-negative-anchor-migration-completing-bc-1-v1-2-rollout.md` (75 chars) → `ADR-011-bc-proj-2-negative-anchor-migration.md` (45 chars); milestone.md vault-ref updated to match.

### Minors (log; address if cheap)

#### m1: methodology-changelog v0.27.0 entry should pin a substantive canonical phrase per N-surface schema-pin discipline

- **Claim under review**: mission-brief AC #5 — pins `BC-PROJ-2` + 9-token set + cross-slice anchors; design.md § "What's new" — same.
- **Issue**: Per slice-008 M2 + slice-009 M3 + slice-010 M3 + slice-011 N-surface schema-pin discipline (N=3 stable), the substantive canonical phrase pinned by the entry-pin test should map to a single load-bearing PHRASE. Prior slices used `Negative anchors` (slice-008), `design.md mechanical tables` (slice-009), `In-house methodology surfaces` (slice-010), `Recursive self-application discipline` (slice-011). Slice-012's design.md doesn't propose a canonical phrase — only rule-ID + cross-slice tokens.
- **Evidence**: `test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed` (L248) pins three things: `## v0.26.0`, `RSAD-1`, AND substantive canonical phrase `Recursive self-application discipline`. Slice-012's entry-pin should follow the same 3-pin shape.
- **Proposed fix**: Pick `BC-PROJ-2 negative-anchor migration` (the changelog entry title) as the canonical phrase; have `test_v_0_27_0_bc_proj_2_entry_present_in_repo_and_installed` assert all three: `## v0.27.0`, `BC-PROJ-2`, AND `BC-PROJ-2 negative-anchor migration` in BOTH files. Maintains N=3 → N=4 N-surface schema-pin discipline.
- **Builder draft**: ACCEPTED-FIXED — mission-brief AC #5 updated to require the canonical phrase `BC-PROJ-2 negative-anchor migration`; design.md Phase 3 updated to require the phrase in the v0.27.0 entry; design.md Phase 1b updated to require the entry-pin test asserts 3 pins; design.md AC trace table row 5 updated to reflect the 3-pin shape; mission-brief TF-1 Notes bullet updated with pinned failure signal `AssertionError: 'BC-PROJ-2 negative-anchor migration' not in <file>`. N=3 → N=4 N-surface schema-pin discipline ratchet at slice-012.

(Critic's m2 was self-withdrawn mid-review as a non-finding — not recorded as a finding row here. Captured under Dim 8 below for transparency.)

## Dimensions checked

- [x] Unfounded assumptions — **B1** filed (AC #4 test specification structurally unable to produce TF-1 genuine PENDING → WRITTEN-FAILING because all 9 tokens already exist on BC-PROJ-1's slice-008 L20 line) + **M2** filed (Audit 3 numerical claims 5.875× inflated). Audit 1 + Audit 2 + Audit 5 disjointness/backward-compat/self-application claims VERIFIED empirically.
- [x] Missing edge cases — none. Migration is data-only on in-house audit; load/concurrency/network/offline/platform axes do not apply. Empty-text edge case handled by `_negative_anchor_match` short-circuit. Phase 4 self-application audit confirms over-determination (9 of 9 tokens present in slice-012's own ship).
- [x] Over-engineering — none. Standard-mode thin-vault preserved: no new schema; reuses slice-008's parser, audit-code, ADR-007 final-filter algorithm verbatim; reuses 9-token set verbatim. Zero speculative generality.
- [x] Under-engineering — **B1** is also a Dim 4 finding (AC #4 has a design element but the element under-specifies the test discipline → cannot deliver TF-1 strict genuine transition). All 5 ACs trace to ≥1 design element. Methodology-audit conformance: TF-1 / RR-1 / BC-1 / WIRE-1 / NFR-1 / VAL-1 / CSP-1 covered or N/A. BC-1 self-application empirically clean. PMI-1 versioned-gate supersession path documented with slice-011-lesson-aware narrow-Edit discipline (M1).
- [x] Contract gaps — none. No new endpoints, events, or API contracts. Internal `BuildCheckRule` dataclass + `_negative_anchor_match` + `negative-anchor-overlaps-positive` unchanged from slice-008.
- [x] Security — none. No authentication, authorization, secrets, or user-input surface. Edits to `~/.claude/methodology-changelog.md` + `~/.claude/ai-sdlc-VERSION` are user-scope filesystem writes per slice-005..011 N=7-stable convention.
- [x] Drift from vault — **M3** filed (vault-ref `[[decisions/ADR-007-bc-1-v1-2-negative-context-anchors]]` does not resolve; ADR-011 filename overly long). ADR-011 supersedes nothing; status `accepted`; reversibility `cheap` justified. No contradiction with prior ADRs.
- [x] Web-known issues — N/A — no novel external tech or API introduced; methodology-internal in-house tooling. Dim 8 honest-out: no anchor to query against.
- [x] Cross-cutting conformance (Dim 9, all 6 sub-clauses):
  - **Sub-clause 1 (Methodology-audit conformance)**: BC-1 self-application empirically clean. TF-1 row coverage clean. TF-1 genuine-transition discipline AT RISK on AC #4 row → **B1** (resolved). Algorithm-path-conformance: `_negative_anchor_match` final filter composes uniformly across all three positive paths per ADR-007.
  - **Sub-clause 2 (Tooling-doc-vs-implementation parity, design.md mechanical tables vs canonical inventories)**: zero-row Wiring matrix OK. **M3 covers ADR-007 filename drift** — same parity class at the vault-ref surface (resolved).
  - **Sub-clause 3 (Algorithm-path-conformance with pre-existing branches)**: see sub-clause 1.
  - **Sub-clause 4 (Runtime / cwd / tool-permission boundaries)**: no subagent fan-out; Bash + Edit + Read only; all paths absolute/relative-to-repo-root. No runtime-environment risk.
  - **Sub-clause 5 (Language-version conformance)**: no new Python source code; tests modify existing 3.12-safe modules. No SyntaxWarning risk.
  - **Sub-clause 6 (Recursive self-application discipline)**: **Design-time mode** — Critic stress-tested slice's own draft prose against the very discipline being encoded. Result: **B1** is itself a recursive-self-application catch — slice-012 encoding "data-only migration of a Negative anchors line" couldn't enforce that BC-PROJ-2 specifically receives the data because the slice's naive verification approach would pass against slice-008's data already in place. **Build-time-via-/critique-fix-prose mode** — Critic verified self-application empirically with current draft (9 of 9 negative anchors present; over-determined; no risk). Fixes for B1/M1/M2/M3 are additive prose — Phase 4 self-application audit will remain over-determined. **N=2 promotion probe** for entry-pin-vs-PMI-1-gate-conflation Dim 9 sub-class candidate (slice-011 N=1; M1 above is design-time pre-emption probe; build-time recurrence → ratchet to N=2 → promote at slice-013+).

## Triage

**Triaged by**: user (pending ratification — see "Ratification needed" below)
**Date**: 2026-05-13
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | Critic right: all 9 tokens pre-exist on BC-PROJ-1's L20 line; naive substring test would PASS pre-migration. Fix applied at design.md "Components touched" + mission-brief TF-1 Notes — test uses `_parse_rules` + `by_id['BC-PROJ-2'].negative_anchors == expected_tuple`; pinned failure signal `AssertionError: BC-PROJ-2 negative_anchors mismatch: got (), expected (...)`. |
| M1 | Major    | ACCEPTED-FIXED | Critic right: slice-011 NEW Dim 9 sub-class N=1 (entry-pin-vs-PMI-1-gate-conflation) requires Phase 1b/1c explicit narrow-scope discipline. Fix applied: design.md Phase 1b INSERT under NEW `# --- Slice-012 / BC-PROJ-2 entry pinning ---` SECTION header; Phase 1c narrow-scope Edit targets gate body + dedicated SECTION header only; Audit 6 added confirming structural separation pre-Edit; ADR-011 Reversibility steps 3+4 updated to distinguish entry-pin (v0.22.0..v0.26.0 untouched) vs PMI-1 gate. N=2 promotion probe at slice-012 build time. |
| M2 | Major    | ACCEPTED-FIXED | Critic right: Audit 3 numbers inflated (claimed 7/47, actual 5/8 distinct-token matches). Fix applied at design.md Audit 3 with explicit measurement definition. ≥1 still suffices for suppression — AC outcomes unchanged. |
| M3 | Major    | ACCEPTED-FIXED | Critic right: (a) ADR-007 vault-ref filename drift — corrected to `ADR-007-bc-1-negative-context-anchors-via-final-filter`; missing `~/.claude/build-checks.md` vault-ref restored. (b) ADR-011 filename shortened 75→45 chars, file renamed via `mv`; milestone.md vault-ref updated. |
| m1 | Minor    | ACCEPTED-FIXED | Critic right: N-surface schema-pin discipline expects 3-pin shape (heading + rule-ID + canonical phrase). Fix applied: canonical phrase `BC-PROJ-2 negative-anchor migration` pinned in AC #5 + design.md Phase 3 + Phase 1b + AC trace row 5 + TF-1 Notes failure signal. N=3 → N=4 ratchet. |

## Ratification needed

Per **TRI-1**, the user is the final triage authority. The Builder pre-applied all 5 ACCEPTED-FIXED fixes in-round; the Triage table above reflects the Builder's draft. The user can override any row before `/build-slice` runs. If no objections: verdict stands as CLEAN — proceed to `/build-slice`.

If any disposition should be OVERRIDDEN / DEFERRED / ESCALATED with rationale, say so and the Triage table will be revised before the triage_audit runs.

## Critic accuracy notes (for /reflect Critic calibration section at slice-end)

- **5 findings total** (1 Blocker + 3 Majors + 1 Minor). Critic self-withdrew m2 mid-flight as a non-finding — 5 actionable findings recorded.
- **All 5 findings ACCEPTED-FIXED in-round**. None OVERRIDDEN, DEFERRED, or ESCALATED.
- **B1 is the strongest single-finding catch** — recursive-self-application phenomenon (slice authoring data-only migration couldn't enforce its own data via naive substring because slice-008 already wrote the same tokens on BC-PROJ-1's line). Validates RSAD-1 codification at slice-011 — the canonical reference instance pattern recurs at slice-012.
- **Cross-cutting-conformance Dim 9 catch rate at slice-012 /critique**: pending /validate-slice disposition; design-time visible 4 of 5 (B1 sub-clause 1+6 recursive-self-application + M3 sub-clause 2 doc-impl-parity + m1 N-surface schema-pin sub-class). Range-bound 60-100% on N=6 evidence stable expected to hold.
- **Voluntary-Critic-on-cross-cutting-tooling N=10/10 → N=11/11** if all 5 findings VALIDATE at /validate-slice. MCT-1 self-application N=1 → N=2 stable (slice-011 was first default-operation; slice-012 second).
