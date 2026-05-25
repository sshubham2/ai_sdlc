# Critique: Slice 035 rename-status-skill-to-pulse

**Critic reviewed**: mission-brief.md, design.md, ADR-035-rename-status-skill-to-pulse.md
**Date**: 2026-05-17
**Result**: BLOCKED (first-Critic verdict pre-triage) → user TRI-1 ratified all 14 dispositions ACCEPTED-FIXED → **Final verdict: CLEAN**

## Summary

The slice intent (resolve the `/status` Claude Code built-in collision) and ADR reasoning are sound. The Critic empirically grepped the repo and found the revision-1 rename inventory **materially incomplete** and containing one **factually wrong citation**: hard `skills/status/SKILL.md` filesystem-path reads mis-classified as prose (would FileNotFoundError the methodology suite), a false `agents/critique.md:194` citation, and an under-specified methodology-changelog RULE-ID/entry-pin obligation. All findings verified correct by the Builder against the codebase and fixed in design.md revision 2 + mission-brief + ADR-035.

## Findings

### Blockers (must address before /build-slice)

#### B1: Missed hard filesystem-path read in `test_risk_register_audit.py` — FileNotFoundError after directory rename
- **Claim under review**: design.md rev-1 treated `test_risk_register_audit.py` as prose-comment-only.
- **Issue**: `test_risk_register_audit.py:327` `def test_status_skill_references_rr_1()`, `:334` `(REPO_ROOT/"skills"/"status"/"SKILL.md").read_text()` — a live filesystem bind. Post-rename → FileNotFoundError → AC#4 "full suite passes" fails.
- **Evidence**: Builder independently confirmed `test_risk_register_audit.py:327-328` (`def test_status_skill_references_rr_1` + docstring `skills/status/SKILL.md must reference RR-1`).
- **Proposed fix**: enumerate as Bucket-A path bind; rename fn + repoint path; mandate pre/post-build inventory grep.
- **Builder draft**: **ACCEPTED-FIXED** — design.md rev-2 "Reference taxonomy" Bucket A row for `test_risk_register_audit.py:327/334` (fn rename + path repoint) + pre/post-build inventory grep predicate; mission-brief AC#5 + must-not-defer updated.

#### B2: `test_skill_model_dispatch.py:25` is a path-list constant, not a "Haiku-dispatch assertion"
- **Issue**: `test_skill_model_dispatch.py:25` `"skills/status/SKILL.md",` is an iterated+read COST-1 inventory tuple entry; rev-1 mischaracterized it as a string-compare assertion, risking a string-only edit.
- **Evidence**: Builder confirmed `test_skill_model_dispatch.py:25` (`"skills/status/SKILL.md",`).
- **Proposed fix**: reclassify as Bucket-A filesystem-path bind; update path constant L25 + docstring L3.
- **Builder draft**: **ACCEPTED-FIXED** — design.md rev-2 Bucket A rows for `:25` + `:3`.

#### B3: `agents/critique.md:194` is NOT a `/status` skill reference — false citation
- **Issue**: rev-1 AC#5 + design.md L50 cited `agents/critique.md:194` as a `/status` skill ref. It is the FBCD-1/PTFCD-1 phantom-test-citation clause; `status` there = TF-1 row-status term-of-art. No `/status` *skill* token exists in `agents/critique.md`. Acting on it risks corrupting an unrelated Dim-9 sub-clause + breaking CAD-1 + PTFCD-1 prose-pin tests.
- **Evidence**: Builder confirmed — `grep /status agents/critique.md` → only L194; L194 body is the PTFCD-1 sub-clause ("name-harmonization (TPHD-1), status, and cross-file consistency"). No skill reference.
- **Proposed fix**: remove `agents/critique.md:194` from scope; mark CAD-1 N/A with rationale.
- **Builder draft**: **ACCEPTED-FIXED** — removed from mission-brief AC#5; design.md rev-2 Bucket C explicitly excludes `agents/critique.md` + declares CAD-1 N/A; ADR-035 records the retraction; must-not-defer CAD-1 line → N/A.

#### B4: methodology-changelog RULE-ID + `test_v_0_NN_0_*` entry-pin obligation under-specified
- **Issue**: rev-1 said "a rule entry + VERSION bump" with no RULE-ID, no target version, no entry-pin test, no installed-copy assertion — would fail `test_methodology_changelog.py` (mandated entry format L24-33; entry-pin pattern; VERSION↔changelog↔plugin.yaml invariant).
- **Evidence**: Builder confirmed `VERSION`=`0.48.0`, `plugin.yaml version: 0.48.0`, latest pin `test_v_0_48_0_tffl_1` (`test_methodology_changelog.py:2689-2732` template incl. bidirectional in-repo + `Path.home()/".claude"/"methodology-changelog.md"` assertion).
- **Proposed fix**: mint RULE-ID, target v0.49.0, add entry-pin test + atomic version triple.
- **Builder draft**: **ACCEPTED-FIXED** — minted **SRCD-1**, target `v0.49.0`, canonical anti-silent-weakening phrase, new `test_v_0_49_0_srcd_1_entry_present_in_repo_and_installed` (mirrors `test_v_0_48_0_tffl_1`), atomic `VERSION`/`plugin.yaml`/header triple — design.md rev-2 "What's new" + Contracts; ADR-035 Decision; mission-brief AC#5 + must-not-defer.

#### B5: Installed-copy reconciliation boundary incoherent
- **Issue**: rev-1 declared installed-copy reconciliation out-of-scope while AC#4/#5 require entry-pin tests that read `~/.claude/methodology-changelog.md`, and `~/.claude/skills/status/` exists with no `pulse`.
- **Evidence**: Builder confirmed `~/.claude/skills/` has `status`, no `pulse`; entry-pin template asserts installed copy.
- **Proposed fix**: state the in-slice reconciliation actually required; narrow the out-of-scope carve-out.
- **Builder draft**: **ACCEPTED-FIXED** — design.md rev-2 "Installed-copy reconciliation" section: `~/.claude/methodology-changelog.md` forward-sync + `~/.claude/skills/status/`→`pulse` + sibling installed SKILL.md refs in-scope; out-of-scope narrowed to other machines beyond INSTALL.md; mission-brief must-not-defer updated.

### Majors (address this slice)

#### M1: Vault-doc `/status` references entirely absent from inventory
- **Issue**: `architecture/concept.md:46`, `architecture/risk-register.md:170/172`, `architecture/lessons-learned.md:414` carry `/status` skill refs; rev-1 listed no vault doc — AC#5 "all cross-doc refs rewritten" unsatisfiable + Dim-7 drift (concept.md becomes a live arch description of a non-existent skill).
- **Evidence**: Critic grep of `architecture/*.md`.
- **Builder draft**: **ACCEPTED-FIXED** — design.md rev-2 Bucket B "Vault docs" per-file disposition: concept.md:46 REWRITE, risk-register.md:170/172 REWRITE, lessons-learned.md:414 FREEZE-AS-HISTORY (rationale in ADR-035); mission-brief AC#5 updated.

#### M2: tutorial-site frozen-vs-live scoping asserted without recorded evidence
- **Issue**: "no generator found" stated as fact without showing verification, vs the well-evidenced ADR-030 exclusion.
- **Builder draft**: **ACCEPTED-FIXED** — design.md rev-2 "Evidence log" records `ls tutorial-site/` + generator-grep verification supporting the hand-maintained classification.

#### M3: `build/lib/tools/` stale copies unaddressed
- **Issue**: `build/lib/tools/install_audit.py`/`risk_register_audit.py` contain `status`; scope silent on whether `build/lib/` is in/out and whether any audit globs it.
- **Builder draft**: **ACCEPTED-FIXED** — design.md rev-2 Bucket C: `build/lib/` excluded as pip artifact + Builder must verify no audit/drift-check globs `build/` (state in build-log; regenerate rather than hand-edit if it does).

### Minors (log; address if cheap)

#### m1: `test_status_*` function names persist after file rename (semantic drift)
- **Builder draft**: **ACCEPTED-FIXED** — design.md rev-2 Bucket A makes the 6 `test_status_*`→`test_pulse_*` function renames in `test_status_cadence_enforcement.py` (+ the `test_risk_register_audit.py` fn) in-scope; build must grep shippability.md for any `::test_status_` pin.

#### m2: `tutorial.md` in-repo-only vs installed not annotated
- **Builder draft**: **ACCEPTED-FIXED** — design.md rev-2 Bucket B splits cross-docs into Installed-runtime (forward-sync) vs In-repo-only (per `INSTALL.md:146`); `tutorial.md`/`pipeline.md`/`README.md`/`INSTALL.md` marked in-repo-only.

## Dimensions checked
- [x] Unfounded assumptions — B3 (false citation, verified), M2 (asserted not evidenced) — FIXED
- [x] Missing edge cases — B1/B2 (path-bind vs prose edge), M3 (build artifacts) — FIXED
- [x] Over-engineering — none (pure mechanical rename, zero-row wiring matrix)
- [x] Under-engineering — B1/B2/B4/M1 (ACs with no delivering design element) — FIXED
- [x] Contract gaps — none beyond the SRCD-1 changelog-entry-format contract (B4) — FIXED
- [x] Security — none (`/pulse` inherits read-only invariant verbatim)
- [x] Drift from vault — M1 (concept.md ISO-42010 consistency), changelog drift (B4) — FIXED
- [x] Web-known issues — N/A (internal identifier rename, no external tech surface) — stated explicitly
- [x] Cross-cutting conformance — B4/B5 (methodology-audit conformance + installed-copy boundary), B1/B2 (design-table-vs-repo cell verification); self-violation law landed (an inventory-completion slice shipped an incomplete inventory) — FIXED via rev-2 + post-edit grep backstop

## Triage

**Triaged by**: user
**Date**: 2026-05-17
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md rev-2 Bucket A + inventory grep |
| B2 | Blocker | ACCEPTED-FIXED | design.md rev-2 Bucket A reclassification |
| B3 | Blocker | ACCEPTED-FIXED | scope retraction + CAD-1 N/A (ADR-035) |
| B4 | Blocker | ACCEPTED-FIXED | SRCD-1 mint + v0.49.0 triple + entry-pin test |
| B5 | Blocker | ACCEPTED-FIXED | installed-copy reconciliation section |
| M1 | Major | ACCEPTED-FIXED | vault-doc per-file dispositions |
| M2 | Major | ACCEPTED-FIXED | evidence log recorded |
| M3 | Major | ACCEPTED-FIXED | build/lib/ excluded + verify-no-glob |
| m1 | Minor | ACCEPTED-FIXED | function-name harmonization in-scope |
| m2 | Minor | ACCEPTED-FIXED | installed vs in-repo annotation |
| B-add-1 | Blocker | ACCEPTED-FIXED | (meta-Critic missed-finding) 4-part atomic bump — `~/.claude/ai-sdlc-VERSION` added; "triple"→"4-part" everywhere |
| M-add-1 | Major | ACCEPTED-FIXED | (meta-Critic) `methodology-changelog.md:11-15` REWRITE + :1365 REWRITE + :1178 FREEZE |
| M-add-2 | Major | ACCEPTED-FIXED | (meta-Critic) SRCD-1 shippability row added (not exempt — #33/#34 precedent) |
| m-add-1 | Minor | ACCEPTED-FIXED | (meta-Critic) README.md:149 filename rewrite + post-edit grep extended |
