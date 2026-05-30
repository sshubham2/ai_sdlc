# Critique: Slice 086 harden-agent-spawn-skills-await-real-output

**Critic reviewed**: mission-brief.md, design.md, ADR-078
**Date**: 2026-05-30
**Result**: NEEDS-FIXES (dual-review EXTEND; user-triaged 2026-05-30)

> Provenance: produced by the `critique` subagent (Agent tool, `subagent_type: "critique"`) — NOT main-thread self-review. This slice exists precisely to forbid the latter; B1/B2 below were independently verified against disk by the Builder before drafting dispositions.

## Summary
The enforcement mechanism (single canonical-literal structural-pin test across three SKILL.md files) is sound and correctly applies the slice-085 "pin a unique-to-invocation literal" lesson. However, the design rests on two factually wrong vault claims about the OSDG-1 guarded set and a non-existent test file (`test_critique_skill_drift.py`), and there is an em-dash-vs-hyphen consistency hazard in the canonical literal that — given this is a single-literal verbatim-match pin — can silently break the test or leave the guard unverified. The R-25 closure logic is otherwise correct.

## Findings

### Blockers (must address before /build-slice)

#### B1: AC-3 and design.md "What's reused" cite a test file that does not exist — `test_critique_skill_drift.py`
- **Claim under review**: mission-brief AC-3: "the existing OSDG-1 drift tests for `critique` (`tests/methodology/test_critique_skill_drift.py` family) and `code-review` (`test_code_review_skill_drift.py`) stay green (content-equal modulo EOL)." design.md "What's reused": "its existing per-skill drift tests: test_critique_skill_drift.py and test_code_review_skill_drift.py (these two ALREADY in the OSDG-1 guarded set)."
- **Issue**: There is no `tests/methodology/test_critique_skill_drift.py` in the repo. The critique-related tests present are prose-pin / agent-drift tests, none of which is an in-repo↔installed SKILL.md content-equality test. So critique SKILL.md is **not actually drift-guarded against its installed copy at all.** The verification plan AC-3 row will fail at collection on a non-existent path (PTFCD-1 phantom-citation class).
- **Evidence**: `tests/methodology/test_critique_skill.py:1` (prose-pin, not a drift test); `CLAUDE.md:42` names `critique` with "their respective `*_skill_drift.py`" — but that file is missing on disk. Builder-verified: `Glob tests/methodology/*skill_drift*.py` → build_slice, commit_slice, query_design, slice, adopt, triage, reflect, code_review, pulse — **no critique, no diagnose**.
- **Proposed fix**: Correct AC-3 and design.md to name tests that actually exist. For `critique`, drop the claim that an existing drift test guards it and treat the new AC-2 pin test as the sole guard for critique's guard-literal (as the slice already treats critique-review). Keep `test_code_review_skill_drift.py` for code-review.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md AC-3 + design.md "What's reused"/"Components touched" — verified against disk; phantom `test_critique_skill_drift.py` removed; critique now documented as having no installed-copy drift test today, with AC-2's pin test as its sole guard-literal enforcement.

#### B2: design.md asserts code-review and critique are "ALREADY in the OSDG-1 guarded set" — contradicting the canonical OSDG-1 inventory
- **Claim under review**: design.md "What's reused": "these two ALREADY in the OSDG-1 guarded set." design.md "Components touched" calls both critique and code-review "OSDG-1 drift test."
- **Issue**: The canonical OSDG-1 guarded set in `CLAUDE.md:42` is `{slice, build_slice, commit_slice, query_design, critique, diagnose, triage, adopt, reflect}`. **`code-review` is NOT in that set.** A `test_code_review_skill_drift.py` file does exist (self-labels "OSDG-1 family member"), but the authoritative CLAUDE.md inventory does not list code-review — a doc/inventory drift the design inherits and amplifies. Building on the false premise "code-review is OSDG-1-guarded so its installed copy is enforced content-equal" risks the same blind window AC-4 is trying to close.
- **Evidence**: `CLAUDE.md:42` (code-review absent from the named set); `tests/methodology/test_code_review_skill_drift.py:1` (self-labels OSDG-1 family — itself drifted from CLAUDE.md). Builder-verified: CLAUDE.md L42 names critique+diagnose (no drift-test file on disk) and omits code-review+pulse (which DO have drift-test files) — the canonical inventory is bidirectionally drifted.
- **Proposed fix**: Reconcile against `CLAUDE.md:42` before building. State accurately: critique = no drift test today; code-review = has `test_code_review_skill_drift.py` though CLAUDE.md L42 omits it from the named set.
- **Builder draft**: ACCEPTED-FIXED at design.md (Components/What's-reused) + ADR-078 Context — claims no longer assert "ALREADY in the OSDG-1 guarded set"; accurate per-skill drift status stated. The pre-existing CLAUDE.md:42 bidirectional inventory drift (critique/diagnose listed-without-test; code-review/pulse test-without-listing) is logged as a DISCOVERED follow-up candidate (`reconcile-osdg-1-inventory-claude-md-L42`) — out of scope to fix in an R-25 slice (would expand a prose-fix slice into a methodology-inventory reconciliation).

### Majors (address this slice)

#### M1: Em-dash vs hyphen drift in the single canonical literal — the entire pin rests on one verbatim string, and the slice's own files already disagree
- **Claim under review**: design.md L57: pin test asserts `**Await the real agent — never fabricate its output.**` (em-dash U+2014). mission-brief AC-1 never quotes the heading literal.
- **Issue**: Single-literal verbatim-match test. The Builder hand-authors the SKILL.md prose; AC-1 does not fix the dash form, so there is a live risk of a hyphen-minus / en-dash / em-dash mismatch across the three files or between the files and the test's CANON constant. A dash mismatch that makes the test green on a SKILL.md missing the real guard would silently re-open R-25.
- **Evidence**: design.md L49/L57 (U+2014 confirmed via codepoint check); mission-brief AC-1 (no quoted literal).
- **Proposed fix**: (1) Pin the exact dash codepoint explicitly in design.md AND mission-brief AC-1 (U+2014 EM DASH, not U+002D, not U+2013). (2) At build time, APED-1-execute the pin: assert the byte-identical literal appears exactly once in each of the three files AND the test's CANON constant before relying on pytest. (3) Ensure the test fails distinguishably for absent vs present-but-wrong-dash.
- **Builder draft**: ACCEPTED-FIXED (doc part) at design.md + mission-brief AC-1 — explicit U+2014 codepoint annotation added as the single source of truth; the build-time byte-exact APED-1 execution is folded into AC-2's verification (ACCEPTED-PENDING for the execution step).

#### M2: AC-2 pins only the heading sentence, not any of the four obligations — a guard reduced to a bare heading with no body still passes
- **Claim under review**: design.md L57: "Asserting the heading-only ... keeps the test robust to prose tuning while still failing closed if the guard is dropped."
- **Issue**: A future edit that keeps the bold heading but deletes/guts the four-obligation body passes the pin test while leaving the main thread with a slogan and no instruction. R-25's failure mode is behavioral — the heading alone does not tell the main thread what to do. AC-2's verification becomes unobservable for the part that does the work.
- **Evidence**: design.md "The canonical guard literal" section (heading + 4 obligations) vs L57 (pins heading only).
- **Proposed fix**: Pin at minimum one unique-to-invocation literal from the operative body in addition to the heading (e.g. `the acknowledgment is NOT the deliverable` or `NEVER self-author a placeholder`), verifying uniqueness per the slice-075 lesson. Keep the heading pin for "guard exists" and add a body pin for "guard still instructs."
- **Builder draft**: ACCEPTED-FIXED at design.md AC-2 + mission-brief AC-2 — AC-2 now pins the heading literal AND one operative body literal; the build-time uniqueness check (body literal must not collide with narration) is folded into AC-2 verification.

#### M3: Mission-brief AC-1 does not contain the canonical literal it is supposed to lock — cross-file consistency gap (FBCD-1)
- **Claim under review**: mission-brief AC-1 describes the four obligations in prose but never states the canonical heading literal; design.md L49/L57 and ADR-078 do.
- **Issue**: The single most load-bearing string in this slice lives in design.md and ADR-078 but is absent from the AC that defines "done." Four-to-five sites (AC-1, design.md, ADR-078, three SKILL.md files, test CANON) must be byte-identical; AC-1 not carrying it removes the canonical anchor the others should be greppable against.
- **Evidence**: mission-brief AC-1 (prose only); design.md L49; ADR-078 §Decision.
- **Proposed fix**: Add the exact canonical literal (with the explicit dash codepoint per M1) to mission-brief AC-1 so all surfaces are greppable against one byte-identical string.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md AC-1 — canonical heading literal added verbatim with the U+2014 codepoint annotation; resolves jointly with M1.

#### M-add-1: Pin test is file-global, not seam-scoped — a relocated guard stays green while becoming inert (sourced by meta-Critic /critique-review, DR-1 EXTEND)
- **Claim under review**: AC-2 + design.md asserted the literals are "present once in each of the three SKILL.md files" (file-global), while AC-1 makes placement load-bearing ("at the spawn→write boundary, the Step 2 → Step 3 seam").
- **Issue**: A file-global+unique pin passes if a future edit MOVES the guard block out of the seam (into a footer/template section or above Step 2) — literal still present once, test green, but the main thread no longer reads it inline at the spawn→write decision point → R-25 re-opens by RELOCATION, not deletion. Internal inconsistency: design.md "What's reused" claims to reuse SOAD-1's section-scoped assertions, but the test spec was file-global. `test_soad1_structured_options_ask_rule.py:13-16,55-70` exists precisely because a repo-global `.count()` passes even when a hit lands in the wrong block (its `_fenced_block_after` helper scopes every assert).
- **Evidence**: meta-Critic independent verification; `test_soad1_structured_options_ask_rule.py:13-16,55-70`; design.md L19 "section-scoped assertions" vs the prior file-global spec.
- **Proposed fix**: Scope the pin to each skill's Step 2 → Step 3 region (assert both literals fall between the "Step 2" and "Step 3" headings), mirroring SOAD-1 `_fenced_block_after`; reconcile AC-2 + design.md with the "section-scoped" claim.
- **Builder draft**: ACCEPTED-FIXED at mission-brief AC-2 + design.md ("What's new" test bullet, the canonical-literal §, test-component Responsibility) + verification-plan row 2 — seam-scoping is confirmed-intended (AC-1 makes placement load-bearing); spec now requires Step 2→Step 3 region assertion mirroring SOAD-1's `_fenced_block_after`, plus a relocate-the-guard fixture in AC-2's verification to prove placement (not just presence) is enforced.

### Minors (log; address if cheap)

#### m1: Shippability row should pin only the single new test path with the exact selector pattern
- **Claim under review**: AC-5 / design.md: "A shippability catalog row pinning the new test (RPCD-1 / SCPD-1)."
- **Issue**: Precision note. SOAD-1 row 48 pins a changelog node too; this slice mints no changelog entry (MEPD-1 EXCLUDE, correctly justified in ADR-078), so the row should pin only `tests/methodology/test_r25_await_real_agent_guard.py`. The Command-cell target resolves only after AC-2's file exists (PTFCD-1).
- **Evidence**: `architecture/shippability.md` row 48 format; design.md "Wiring matrix".
- **Proposed fix**: Add the row with the single test path; no changelog node; confirm `shippability_path_audit` green after the test file exists.
- **Builder draft**: ACCEPTED-PENDING at /build-slice — single-path row added with no changelog node; audit confirmed green post-test-creation.

#### m2: ADR-078 "Options considered" Option 1 con is slightly overstated but lands correctly
- **Claim under review**: ADR-078 Option 1: "drift tests assert whole-file content-equality ... a guard dropped from BOTH repo and installed copies passes drift."
- **Issue**: Correct reasoning and the right reason to choose Option 2. Minor: the framing implies critique/code-review *have* such drift tests today; per B1/B2 critique does not, and code-review's is not in the canonical OSDG-1 set. The decision (Option 2) is unaffected.
- **Evidence**: ADR-078 §Options considered; CLAUDE.md:42.
- **Proposed fix**: Tweak the ADR's Option-1 con to not presuppose the drift tests exist for all three; the conclusion stands.
- **Builder draft**: ACCEPTED-FIXED at ADR-078 §Options/§Context — Option-1 con reworded to not presuppose per-skill drift coverage; harmonized with the B1/B2 corrected facts. (ADR-078 is the in-flight ADR authored this slice, not yet committed/merged — editing the draft is permitted; SUP-1 append-only applies to shipped/archived ADRs.)

## Dimensions checked
- [x] Unfounded assumptions — B2 (code-review "ALREADY in OSDG-1 set" unbacked by CLAUDE.md:42), M3 (canonical literal absent from AC-1). Design.md insertion-point line citations (L99/L75/L140) VALIDATED accurate against the live SKILL.md files.
- [x] Missing edge cases — M1 (dash-codepoint drift across hand-authored surfaces), M2 (heading-only pin lets a body-gutted guard pass). Load/concurrency/network N/A (prose+presence-test slice).
- [x] Over-engineering — none: single literal + single test is the minimal mechanism; reuses SOAD-1 prose-pin pattern. MEPD-1 EXCLUDE correctly justified against slice-077/082/084/085 precedent.
- [x] Under-engineering — B1 (verification plan AC-3 row targets a non-existent test → collection failure), M2 (AC-2 under-covers the operative body). TF-1: slice is test-first:false; AC-2 is genuinely WRITTEN-FAILING-able.
- [x] Contract gaps — none: "Contracts added or changed: None" is accurate (prose contracts only).
- [x] Security — none: R-25 is explicitly NOT a security boundary (cooperating-operator review integrity).
- [x] Drift from vault — B1 (phantom test file), B2 (OSDG-1 set membership contradicts CLAUDE.md:42). ADR-078 supersedes:null correct. R-25 register entry matches the slice intent.
- [x] Web-known issues — none: no external technology/API/platform dependency.
- [x] Cross-cutting conformance — B1 (PTFCD-1 phantom test-file citation), B2 + M3 (CCC-1 design-claim-vs-canonical-inventory + FBCD-1 cross-file literal consistency), M1 (APED-1: minted verbatim-match rule — execute dash-exact match at build, don't reason). Ordering invariant (AC-4 removal last) correctly load-bearing.

## Triage

**Triaged by**: user
**Date**: 2026-05-30
**Final verdict**: NEEDS-FIXES

Dual-review reconciliation (DR-1): meta-Critic verdict EXTEND — all first-Critic findings confirmed VALID (0 suspicious, 0 severity adjustments); 1 missed finding (M-add-1) added below. User ratified all Builder draft dispositions as-is.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | Phantom `test_critique_skill_drift.py` removed; mission-brief AC-3 + design.md "What's reused"/"Components touched" corrected to disk reality (critique has no drift test; AC-2 pin is sole guard). Builder-verified via Glob. |
| B2 | Blocker | ACCEPTED-FIXED | design.md + ADR-078 §Context no longer claim code-review/critique "ALREADY in OSDG-1 set"; reconciled against CLAUDE.md:42. Pre-existing inventory drift logged as out-of-scope follow-up `reconcile-osdg-1-inventory-claude-md-L42`. |
| M1 | Major | ACCEPTED-FIXED | U+2014 EM DASH pinned as the single byte-exact source-of-truth in mission-brief AC-1 + design.md; build-time byte-exact APED-1 check folded into AC-2 verification (normal build step). |
| M2 | Major | ACCEPTED-FIXED | AC-2 now pins heading + operative body literal `NEVER self-author a placeholder`; meta-Critic independently confirmed the body literal is unique-to-invocation (0 narration hits across all 3 skills), so no slice-085 collision. |
| M3 | Major | ACCEPTED-FIXED | Canonical heading literal added verbatim to mission-brief AC-1 with U+2014 annotation; resolves jointly with M1 (single greppable anchor across all surfaces). |
| M-add-1 | Major | ACCEPTED-FIXED | Meta-Critic EXTEND. Seam-scoping confirmed-intended (AC-1 makes placement load-bearing). Spec now requires Step 2→Step 3 region assertion mirroring SOAD-1 `_fenced_block_after`; AC-2 verification adds a relocate-the-guard fixture to prove placement (not just presence) is enforced. Reconciles the design's "section-scoped assertions" reuse claim. |
| m1 | Minor | ACCEPTED-PENDING | Shippability row pinning only `tests/methodology/test_r25_await_real_agent_guard.py` (no changelog node, MEPD-1 EXCLUDE) added at /build-slice after the test file exists; `shippability_path_audit` confirmed green then. |
| m2 | Minor | ACCEPTED-FIXED | ADR-078 §Options Option-1 con + §Context + §Decision reworded to not presuppose per-skill drift coverage; harmonized with B1/B2 corrected facts. (In-flight ADR, not yet committed — SUP-1 append-only governs shipped ADRs.) |
