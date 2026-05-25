# Critique: Slice 062 extend-r15-corpus-class-closure-scope

**Critic reviewed**: mission-brief.md, design.md, ADR-060
**Date**: 2026-05-23
**Result**: NEEDS-FIXES → all 6 findings ACCEPTED-FIXED in same fix block (verdict reduces to CLEAN at TRI-1)

## Summary

The slice's core mechanism (option 3: extract helper + 3 per-corpus tests + 1 aggregated whitelist-integrity test + lazy `_resolve_slice_dir(60)` repoint) is structurally sound; cross-package import and `_resolve_slice_dir(60)` resolution both verified empirically by the Critic. The Critic surfaced one Blocker (B1: 4-part PMI-1 bump enumeration missed PVFS-1 / `pyproject.toml` — a direct re-introduction of the slice-060 B2 defect class that would FAIL PVFS-1 at /build-slice Step 6), one Major (M1: slice-060 reflection L37 nominated slice-062 for TRI-1 gate, which slice-062 silently re-deferred), and four Minors (m1 fabricated citation in ADR-060 §Decision; m2 EPGD-1 section-header reminder; m3 TPHD-1 sub-mode (a) TF-1 table harmonization gap mission-brief 4 rows vs design.md 7 rows; m4 R-15 historical-prose framing). All 6 findings VALIDATED at empirical re-grounding; all 6 ACCEPTED-FIXED in same fix block per TPHD-1 sub-mode (a) harmonization discipline.

## Findings

### Blockers (must address before /build-slice)

#### B1: PMI-1 bump enumeration omits `pyproject.toml [project].version` — slice will FAIL PVFS-1 at Step 6

- **Claim under review**: design.md "What's new" PMI-1 bullet + ADR-060 Consequences bullet 4: *"4-part PMI-1 atomic version bump 0.64.0 → 0.65.0 (`VERSION` + `~/.claude/ai-sdlc-VERSION` per AVFS-1 + `plugin.yaml.version` per PMI-1 + `methodology-changelog.md` forward-synced per MCFS-1)"*.
- **Issue**: PVFS-1 was minted at v0.62.0 / slice-054 / ADR-056 as a sibling gate of PMI-1; it asserts `pyproject.toml [project].version == VERSION`. slice-060's v0.64.0 entry explicitly says *"5-part PMI-1 atomic bump 0.63.0 → 0.64.0 (VERSION + plugin.yaml.version + pyproject.toml [project].version + ## v0.64.0 header + installed ~/.claude/ai-sdlc-VERSION)"* and the entry-pin at `tests/methodology/test_methodology_changelog.py:3989` asserts the substring `"5-part PMI-1 atomic bump"` in the v0.64.0 body. A 4-part bump per the slice-062 design would leave `pyproject.toml` at `0.64.0` while `VERSION` moves to `0.65.0` → PVFS-1's `test_repro_sc001_pyproject_project_version_matches_version_file` FAILS at Step 6 with `'0.64.0' == '0.65.0'`. slice-060 reflection L50 records exactly this catch ("**B2** PMI-1 4-part vs 5-part: VALIDATED — ACCEPTED-FIXED"). slice-062 design.md was re-introducing the slice-060 B1 defect class verbatim.
- **Evidence**: `tests/methodology/test_pyproject_version_matches_version_file.py:126-148`; `methodology-changelog.md:43` v0.64.0 entry; `methodology-changelog.md:85` v0.62.0 PVFS-1 mint; `architecture/decisions/ADR-056-mint-pvfs-1-pyproject-version-forward-sync.md`; slice-060 reflection L50.
- **Proposed fix**: Rewrite design.md "What's new" PMI-1 bullet AND ADR-060 Consequences bullet 4 to 5-part shape verbatim matching slice-060; update mission-brief Pre-finish gate to name PVFS-1 explicitly; add design.md "CSP-1 cross-spec parity check" row asserting the v0.65.0 entry-pin includes substring `"5-part PMI-1 atomic bump"`.
- **Builder draft**: **ACCEPTED-FIXED** — applied at design.md "What's new" item 5 (5-part shape verbatim + reasoning), design.md Components-touched section header (`VERSION + plugin.yaml + pyproject.toml + ~/.claude/ai-sdlc-VERSION`), design.md Build-sequencing Phase C step 12 (5-part bump command list with pyproject.toml leg), design.md Phase D step 17 (PVFS-1 test added to audit stack), design.md CSP-1 cross-spec parity table (new 5-part-bump row), ADR-060 Consequences bullet 4 (5-part shape + slice-060 L50 evidence citation), mission-brief Pre-finish gate audit enumeration (PVFS-1 named explicitly with the "would FAIL Step 6" justification). FBCD-1 sub-mode (a) cross-file consistency satisfied — all 7 propagation sites updated in the same fix block.

### Majors (address this slice)

#### M1: Deferral-chain divergence — slice-060 reflection explicitly nominated slice-062 for TRI-1 gate; slice-062 silently re-defers to slice-063+ without acknowledging the slice-060 nomination

- **Claim under review**: mission-brief Out-of-scope bullet 1: *"slice-060 `/code-review` v2 enhancements (AI-bloat passes + TRI-1 + verdict-block) — slice-063+"*.
- **Issue**: `architecture/slices/archive/slice-060-add-code-review-skill/reflection.md:37` states verbatim *"TRI-1 triage gate + verdict-driven block on `/validate-slice` — **slice-062** (slice-060's findings stay advisory only in v1)"*. slice-061 reflection (more recent nominator) nominates slice-062 for the R-15 scope-extension without explicitly retracting slice-060's TRI-1 nomination. Per Wiegers requirements-design traceability discipline, when a deliberate scope inversion is made (slice-062 chosen for the R-15 scope-extension carrier and explicitly NOT the TRI-1 nominator), the design must acknowledge and justify the inversion — not silently re-defer. The current Out-of-scope bullet hides the fact that slice-060 named slice-062 by ID.
- **Evidence**: `architecture/slices/archive/slice-060-add-code-review-skill/reflection.md:37` (verbatim "slice-062" nomination); `architecture/slices/archive/slice-061-fix-install-python-detection-and-prompt-fallback/reflection.md:26,30-34` (slice-061 R-15 scope-extension nomination + "slice-062-or-later" treatment of R-17/R-18).
- **Proposed fix**: Add acknowledged-divergence note to mission-brief Out-of-scope citing slice-060 L37 + explicit justification why R-15 scope-extension takes precedence (build-time gate vs feature-level enhancement; slice-061 ranks R-15 extension primary; TRI-1 + verdict-block remains highest-priority slice-063 candidate).
- **Builder draft**: **ACCEPTED-FIXED** — applied at mission-brief Out-of-scope bullet 1; the slice-060 reflection L37 nomination is now cited explicitly with the three justifying clauses (build-time vs feature-level; slice-061 ranking; TRI-1 remains slice-063 highest-priority).

### Minors (log; address if cheap)

#### m1: ADR-060 §"Decision" attributes a quote to `architecture/lessons-learned.md` that does not exist in the repository

- **Claim under review**: ADR-060 §"Decision" paragraph 1 attributed quote *"regex pattern needs a self-test that the walker actually visits the corpus"* to lessons-learned.md.
- **Issue**: Critic ran `Grep` against the repo; the phrase does not exist anywhere. Per Wiegers / Cockburn evidence-traceability discipline: claims must trace to evidence; a fabricated attribution is a fabricated citation.
- **Evidence**: Critic's grep `walker actually visits|self-test that the walker` → 0 matches across `<HOME>\ai_sdlc`.
- **Proposed fix**: Paraphrase instead of quote; cite the actual slice-056 M-add-2 disposition + slice-057 Discovered section instead.
- **Builder draft**: **ACCEPTED-FIXED** — applied at ADR-060 §"Decision" paragraph 1; the fabricated quote replaced with paraphrased reference to slice-056 M-add-2 + slice-057 Discovered section's per-line-vs-whole-file regex iteration lesson (no quote, no fabricated attribution).

#### m2: EPGD-1 structural-separation discipline not explicitly named in design.md Phase C

- **Claim under review**: design.md "Build sequencing" Phase C step 14: *"add 2 entry-pin tests"*.
- **Issue**: Per Dim 9 EPGD-1 sub-clause (slice-011/012; design-time-pre-empted success mode): the new v0.65.0 entry-pin tests MUST be placed under a NEW dedicated SECTION header NOT shared with any other version's section. Existing pattern at `tests/methodology/test_methodology_changelog.py:3943` is `# --- Slice-060 / CRSI-1 entry pinning ---`. slice-062's INSERT should be placed AT END with its own header `# --- Slice-062 / R-15-scope-extension entry pinning ---`, NOT folded into v0.64.0's section.
- **Evidence**: `tests/methodology/test_methodology_changelog.py:3943` (existing SECTION header pattern); EPGD-1 design-time-pre-empted-success-mode discipline.
- **Proposed fix**: Add EPGD-1 placement directive to design.md Phase C step 14.
- **Builder draft**: **ACCEPTED-FIXED** — applied at design.md Phase C step 14; the directive now names the SECTION header verbatim + cites the slice-060 L3943 anchor + mirrors the SCMD-1→CRSI-1 per-slice SECTION-header separation pattern.

#### m3: TPHD-1 sub-mode (a) — mission-brief 4-row TF-1 plan vs design.md 7-row TF-1 plan harmonization gap acknowledged but not resolved

- **Claim under review**: mission-brief TF-1 plan section: 4 rows + a NOTE saying design.md supersedes.
- **Issue**: TF-1 audit reads the mission-brief table as the primary TF-1 plan parsed surface; the audit will see 4 rows, not 7. The slice-017 TPHD-1 lesson is exactly this class.
- **Evidence**: mission-brief.md Test-first plan section (4 rows + NOTE); design.md Test-first plan section (7 rows); TPHD-1 sub-mode (a) discipline at Dim 9 sub-clause "Fix-block-completeness discipline".
- **Proposed fix**: Update mission-brief's TF-1 plan table to match design.md's 7-row table verbatim, removing the NOTE.
- **Builder draft**: **ACCEPTED-FIXED** — applied at mission-brief.md Test-first plan section; replaced the 4-row table + NOTE with the 7-row table verbatim from design.md (extracted-helper wrapper + 2 per-corpus tests + aggregated integrity test + lazy-repoint + 2 entry-pin tests) and updated the trailing paragraph to explain rows 1-3 walk-proof structure + rows 6-7 EPGD-1 SECTION-header separation.

#### m4: R-15 risk-register annotation will leave stale `tests/methodology/*.py` scope claim in prior paragraphs

- **Claim under review**: design.md Phase C step 15 + mission-brief AC4: *"R-15 entry annotated with a post-retirement scope-extension paragraph"*.
- **Issue**: The slice-057 retirement paragraph at `architecture/risk-register.md:266` contains prose *"no R-15-class literal-path-RHS may land anywhere under `tests/methodology/*.py` without tripping a loud audit-fail"*. After slice-062 ships, this prose becomes structurally stale (scope is now broader). Future readers will see two conflicting scope claims unless the slice-062 paragraph explicitly frames the slice-057 prose as historical-record per the slice-040 R-10 retirement-precedent (preserve prior prose verbatim).
- **Evidence**: `architecture/risk-register.md:266` (slice-057 paragraph); slice-040 R-10 retirement-precedent.
- **Proposed fix**: Add explicit historical-record framing instruction to design.md Phase C step 15 naming the slice-057 paragraph as describing the pre-slice-062 state.
- **Builder draft**: **ACCEPTED-FIXED** — applied at design.md Phase C step 15; the new paragraph's verbatim opening text is specified (cites slice-040 R-10 retirement-precedent + names `risk-register.md:266` + frames slice-057 prose as describing pre-slice-062 state) — makes the slice-057 paragraph's `tests/methodology/*.py` claim explicitly historical, not contradictory.

## Dimensions checked

(Critic-applied; abbreviated here — full per-dimension reasoning in the Critic's source output transcribed above)

- [x] **Unfounded assumptions** — m1 (fabricated lessons-learned.md citation in ADR-060 §Decision). Cross-package import claim + `_resolve_slice_dir(60)` resolution both verified empirically by the Critic.
- [x] **Missing edge cases** — none of significance. Regex behavior on `_REPO_ROOT` (vs `REPO_ROOT`) verified empirically (no `\b` boundary; substring match works). 3 corpus directories all exist on disk. Self-skip clause behavior sound across all 3 corpora.
- [x] **Over-engineering** — none. Option 3 well-justified; no speculative-generality flags.
- [x] **Under-engineering** — B1 (PMI-1 enumeration omits PVFS-1; would FAIL Step 6 — AC-class violation). m3 (TF-1 row coverage gap). Pre-finish gate enumeration missing PVFS-1 (sub-issue of B1).
- [x] **Contract gaps** — none. CSP-1 table correctly enumerates 5 surfaces (post-B1-fix: now 6 with the new 5-part-bump row).
- [x] **Security** — none. No auth, secrets, input validation, or data-exposure surfaces touched.
- [x] **Drift from vault** — m4 (stale `tests/methodology/*.py` scope claim in slice-057 retirement paragraph). No ADR contradiction (ADR-060 supersedes nothing; ADR-053 / ADR-051 / slice-007 CAD-1 lineage references all verified). No phantom path citations. STP-1 Sub-form B clean (zero `test_r_15_*_stays_retired` functions exist).
- [x] **Web-known issues** — skipped (WebSearch unavailable; slice introduces no third-party libraries or chosen-technology changes; in-house methodology test infrastructure only — low risk to skip).
- [x] **Cross-cutting conformance** — B1 (PMI-1 4-vs-5 part FBCD-1 sub-mode (a)); m2 (EPGD-1 section-header structural separation); m3 (TPHD-1 sub-mode (a) mission-brief vs design.md harmonization); m4 (R-15 historical-prose framing). All others (RSAD-1, RPCD-1, SCPD-1, APED-1, PTFCD-1/PTFFD-1, tooling-doc-vs-implementation parity, runtime-environment boundaries) checked clean.

## Triage

**Triaged by**: user
**Date**: 2026-05-23
**Final verdict**: CLEAN

| ID | Severity | Disposition (Builder draft) | Rationale |
|----|----------|-----------------------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | Applied at 7 sites in same fix block (design.md What's-new item 5 + Components-touched section header + Phase C step 12 + Phase D step 17 + CSP-1 table new row; ADR-060 Consequences bullet 4; mission-brief Pre-finish gate enumeration). Mirrors slice-060 v0.64.0 5-part-bump shape verbatim with PVFS-1 named explicitly. |
| M1 | Major    | ACCEPTED-FIXED | Applied at mission-brief Out-of-scope bullet 1; explicit slice-060 reflection L37 citation + 3-clause justification (build-time gate vs feature-level enhancement; slice-061 ranking; TRI-1 remains slice-063 highest-priority). |
| m1 | Minor    | ACCEPTED-FIXED | Applied at ADR-060 §"Decision" paragraph 1; fabricated quote replaced with paraphrased reference to slice-056 M-add-2 + slice-057 Discovered section. |
| m2 | Minor    | ACCEPTED-FIXED | Applied at design.md Phase C step 14; EPGD-1 placement directive names the SECTION header verbatim + cites the slice-060 L3943 anchor. |
| m3 | Minor    | ACCEPTED-FIXED | Applied at mission-brief.md Test-first plan section; 4-row table + NOTE replaced with 7-row table verbatim from design.md. **Note**: this fix introduced M-add-1 (Blocker) — the 7-row table used multi-AC labels `"1, 3"` + `"(audit-trace)"` markers that TF-1 audit rejects. Surfaced at /critique-review (meta-Critic ran the audit empirically and got 2 violations) and re-fixed at /critique-review fix block — see M-add-1 disposition below. |
| m4 | Minor    | ACCEPTED-FIXED | Applied at design.md Phase C step 15; verbatim opening text for the R-15 scope-extension paragraph specified (cites slice-040 R-10 retirement-precedent + frames slice-057 prose at risk-register.md:266 as pre-slice-062 historical record). |
| M-add-1 | Blocker | ACCEPTED-FIXED | Dual-review missed-finding per critique-review.md M-add-1: the m3 ACCEPTED-FIXED edit introduced multi-AC labels (`"1, 3"`) + `"(audit-trace)"` markers that `tools/test_first_audit.py:_normalize_ac_label` rejects → 2 `ac-without-row` violations on AC#3 + AC#4 → /build-slice Step 6 HALT. EXACT same defect class as slice-056 /critique-review M-add-1 (N=2 slice-040 N+1 doctrine recurrence). Applied at mission-brief.md L25-35 + design.md L162-174: TF-1 plan rewritten to 8 rows with bare-numeric AC labels per slice-056 multi-row-per-AC precedent (4 rows AC#1; 1 row AC#2; 1 row AC#3 reusing tests_skills_corpus as sequencing-proof anchor; 2 rows AC#4 for v0.65.0 entry-pin + shippability-propagation). Empirically verified at /critique-review fix block: `$PY -m tools.test_first_audit ... --json` exit 0, `violation_count: 0`, 8 rows parsing cleanly across all 4 ACs. |
| M-add-2 | Minor | ACCEPTED-FIXED | Dual-review missed-finding per critique-review.md M-add-2: 3-scheme cross-document option-enumeration incoherence (ADR-060 numerals 1-4; design.md mentions 3-options/B/A; mission-brief lists (a)/(b)/(c) — chosen ADR option 3 absent from mission-brief enumeration). Applied at design.md L58 + L181 + L189 + mission-brief.md L52: ADR-060 numeric 1-4 is now the authoritative scheme; design.md cross-references map cleanly; mission-brief #5 defers to ADR-060 as authoritative enumeration. |
| M-add-3 | Minor | ACCEPTED-FIXED | Dual-review missed-finding per critique-review.md M-add-3: design.md Phase C step 11 said "4-part Inclusion-heuristic structure" — confusable with the 4-part PMI-1 bump that B1 just corrected to 5-part; "4-part" qualifier was novel terminology not appearing elsewhere in the repo. Applied at design.md L150: rewrote step 11 to describe the v0.59.0/v0.64.0 entry-body template explicitly (summary + Rule reference + Defect class + Validation per methodology-changelog.md L17-31 format spec) + made the entry-body vs bump-shape distinction explicit ("The bump shape is 5-part PMI-1 per step 12 below — explicitly NOT 4-part"). |

If all 9 dispositions ratify ACCEPTED-FIXED → Final verdict **CLEAN** → proceed to `/build-slice`.
