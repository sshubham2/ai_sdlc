# Critique: Slice 041 reframe-installed-pin-forward-sync-invariant (REV-2 RE-CRITIQUE)

**Critic reviewed**: mission-brief.md (rev-2), design.md (rev-2), ADR-042 (rev-2), ADR-043 (rev-2), critique-v1.md, critique-review-v1.md
**Date**: 2026-05-18
**Result**: BLOCKED
**Context**: Critic advisory; final verdict at TRI-1 — 2nd consecutive BLOCKED with flaw relocation (rev-1 B1 → rev-2 B1)

## Summary

Rev-2 correctly discharged ~80% of the rev-1 loop — the audit-derived population (37 raw / 34 unique / 28 `_entry_present` / 6 non / 0 incidental / `v_0_42_0` essential-but-uncited / 4 defined-but-uncited) is **empirically exact** (Critic re-derived; Builder independently re-confirmed via `_index_module`/`classify_fn`), and M2/M3/M4/m1-wiring/m2/M-add-1-literal-sites/CAD-1-MEPD-1-non-circularity are all soundly resolved. **But the rev-1 B1/B2 flaw RELOCATED rather than resolved**: the load-bearing re-home soundness claim ("drop L349 ⇒ cross-module pin reclassifies `clean`, allowlist stays empty") is **empirically false** — `classify_fn` is an *unordered cross-expression subset test*, so `.claude` (retained `Path.home()/".claude"/"skills"/"diagnose"` L348) + `methodology-changelog.md` (retained in-repo surface L354) keep the fn `essential`. **Builder independently reproduced this** (`segs=['.claude','diagnose','methodology-changelog.md','skills']` → `classify: essential`). Both the rev-1 first-Critic recommendation AND the rev-1 DR-1 "independently verified mechanically sound" carried the same untraced subset-semantics assumption (reasoned, not executed — slice-032 law violated by the reviewers themselves). Per the **slice-030A/031 non-convergence discipline** (2 consecutive BLOCKED loops, flaw relocating each time ⇒ stop patching, surface a structural decision; don't wait for the meta-Critic to force it), the Builder is NOT attempting a rev-3 patch — see the structural pivot below.

## Findings

### Blockers (must address before /build-slice)

#### B1: Re-home soundness claim empirically false — cross-module pin stays `essential` after leg-drop (flaw relocated from rev-1 B1)
- **Claim under review**: design.md rev-2 ("dropping solely L349 re-classifies it `clean`; DR-1-confirmed"), ADR-042/043 rev-2 ("no hidden contradiction"), AC3/AC4 ("zero remaining essential", `_REGISTERED_INSTALLED_READERS = frozenset()`).
- **Issue**: `classify_fn` (`shippability_decoupling_audit.py:393-415`) computes `set(shape) <= _reachable_path_segments(fn)`, an **unordered set over ALL path-segment strings the fn reaches** — tokens need not co-originate. For `test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces`, dropping `installed_changelog` (L349) + its L357 surface entry leaves `.claude` (L348 `Path.home()/".claude"/"skills"/"diagnose"`, retained, unrelated) and `methodology-changelog.md` (L354 in-repo `REPO_ROOT/"methodology-changelog.md"` surface, **retained by design per m2/AC3**). `{'.claude','methodology-changelog.md'} ⊆ {'.claude','diagnose','skills','methodology-changelog.md'}` = TRUE ⇒ stays `essential` ⇒ `essential-unregistered` exit 1 ⇒ AC3/AC4/AC5/V1 + full catalog FAIL.
- **Evidence**: Builder executed `_index_module(test_skill_md_pins.py)` + `classify_fn` → `essential`; `segs=['.claude','diagnose','methodology-changelog.md','skills']`. `_ESSENTIAL_SHAPES=(('.claude','methodology-changelog.md'),)`. Contrast: the in-`test_methodology_changelog.py` `_entry_present_*` fns derive `.claude` ONLY from the installed-changelog leg (in-repo leg is `read_file("methodology-changelog.md")`, no `.claude`) → leg-drop genuinely yields `clean` for THOSE (the defect is isolated to the cross-module pin which uniquely contributes both tokens from two unrelated retained expressions).
- **Builder response**: **ACCEPTED — structural pivot (NOT a rev-3 leg-drop patch)**. The leg-drop approach provably cannot reclassify the cross-module pin `clean` while retaining its in-repo changelog surface (which AC3/m2 require). The charter-faithful resolution is the one the R-4 sub-entry literally describes — *"define SCMD-1's essential-class invariant as accounted-for (a catalog-derived **intentional-installed allowlist, the read registered not absent**)"* — i.e. a **non-empty `_REGISTERED_INSTALLED_READERS`** that registers the genuinely-intentional cross-module slice-019 LAYER-EVID-1 pin with rationale (it IS a protective N=6-surface forward-sync byte-equality assertion, not incidental coupling). Decouple only the in-`test_methodology_changelog.py` essential fns (leg-drop → genuinely `clean`, verified). This dissolves B1 (the cross-module pin need not become `clean` — it is *registered*) and resolves rev-1 B2 honestly (allowlist non-empty was always the charter intent; rev-1's "empty post-041" / ADR-043 was an over-simplification). **Surfaced to TRI-1 as a redesign-direction change requiring re-ratification** — the user's rev-1 branch-(1) ("re-home, keep empty") was ratified on the now-empirically-falsified "re-home ⇒ clean" premise.

### Majors (address this slice)

#### M1: Frozen-history carve-out misses 41 old-suffix occurrences in the forward-synced `methodology-changelog.md` + 17 ADRs/lessons/index
- **Claim under review**: design.md rev-2 / mission-brief V7: post-rename grep scoped to `tests/ agents/ skills/`; whitelist = `fixtures/archive_backtest_corpus/**` + `archive/**`.
- **Issue**: `grep -rn "_entry_present_in_repo_and_installed"` repo-wide returns 41 occurrences in **`methodology-changelog.md`** (historical `**Validation**:` lines of shipped v0.22.0–v0.52.0 entries — append-only history MCFS-1 itself forward-syncs), plus 27 in `architecture/shippability.md`, plus 17 ADRs + risk-register/lessons/index. The design's `tests/ agents/ skills/` grep scope structurally cannot see these. Not a hard Blocker (no structural test asserts the `**Validation**:` test-name text — Critic verified entry-pins assert RULE-ID/canonical-phrase/ADR-lineage only), but post-rename it leaves phantom citations in the canonical forward-synced artifact and creates an append-only-history-vs-rewrite tension the design does not address.
- **Builder response**: **ACCEPTED — scope-cut (per slice-030A/031 "split beats patch when it's actually multiple features")**. The `_entry_present_*`→`_entry_present` **rename is pure identifier-truth (slice-035) and is NOT required to retire R-4** (R-4 retirement = essential reads *accounted-for* via decouple-or-register, independent of the test-fn *names*). Its frozen-history blast radius (41 append-only shipped changelog lines + 17 ADRs + 27 shippability rows) is orthogonal scope. **Recommend deferring the rename to a separate identifier-truth slice** and removing it from slice-041 — keeping slice-041 focused on the R-4-retiring essential-decouple + MCFS-1 + non-empty registered allowlist. Surfaced to TRI-1 (overturns the rev-1 rename ratification).

### Minors (log; address if cheap)

#### m1: design.md "L1426 error-message string" pointer imprecise (literal spans L1425-1427)
- **Issue**: cosmetic precision; moot if the rename is scope-cut (M1).
- **Builder response**: ACCEPTED-FIXED — moot under the M1 scope-cut (no rename ⇒ no `test_critique_agent.py` literal edit). If the user keeps the rename in-scope, design.md will say "L1425-1427 literal (old-suffix token at L1426)".

## Dimensions checked
- [x] Unfounded assumptions — **B1** (re-home⇒clean false; executed-reproduced by Critic AND Builder; rev-1 reviewers reasoned not executed). Population numbers re-verified exact (founded).
- [x] Missing edge cases — **M1** (repo-wide frozen-history re-grep: 41 changelog + 17 ADR sites outside design's grep scope). M3 ordering sound (final-catalog pre-finish run; but B1 fn hard-fails it ⇒ fix at design time).
- [x] Over-engineering — none (empty `frozenset()` was the *wrong* default — non-empty registered IS the charter design; B1 pivot corrects this).
- [x] Under-engineering — B1 (no design element delivers `essential=∅`/registered for the cross-module pin), M1 (rename-completeness verification missing 41+17 sites).
- [x] Contract gaps — none beyond B1/M1; MCFS-1 CLI + SCMD-1 `essential-unregistered` contracts BCI-1-faithful and well-specified.
- [x] Security — none. MCFS-1-tool relocation guard (`_cited()` unreachable for non-`Machine-cmd` `tools/*`) verified sound (independent of B1, which is about a test fn).
- [x] Drift from vault — R-4 `mitigating` w/ slice-030C charter; v0.53.0 correct next; ADR-042/043 append-only/supersede-nothing (SUP-1 OK); ADR-033 home untouched. M1 surfaces an append-only-history tension the design must resolve consciously.
- [x] Web-known issues — none (in-house AST tooling).
- [x] Cross-cutting conformance — B1 = APED-1 audit-parse executed-not-reasoned (the rev-1 reviewers' own miss); CAD-1/MEPD-1 self-reference verified non-circular (L1424 prefix-only, rename-safe; MEPD-1 substance unchanged); m1-wiring verified (build-slice Step 6 genuinely ungated; reflect Step 5b rule-promotion-gated → rev-2's new-dedicated-step correct); M2 sibling-scoping disposition proportionate. **Non-convergence signal**: 2 consecutive BLOCKED loops, flaw relocating (rev-1 B1 → rev-2 B1) ⇒ slice-030A/031 discipline invoked — structural pivot + scope-cut surfaced proactively, not a rev-3 patch.

## Triage

**Triaged by**: user
**Date**: 2026-05-18
**Final verdict**: CLEAN

> rev-2 reconciliation (first-Critic BLOCKED #2 + DR-1 ACCEPT). Per the slice-030A/031 non-convergence discipline (2 BLOCKED loops, flaw relocating) the resolution is a **structural pivot + scope-cut**, NOT a rev-3 patch — both DR-1-verified by execution. User re-ratified (overturning the rev-1 ratifications made on the now-falsified "re-home ⇒ clean" premise): (1) **adopt the charter-faithful non-empty registered allowlist** — `_REGISTERED_INSTALLED_READERS = frozenset({"tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces"})` with rationale; decouple all in-`test_methodology_changelog.py` essential fns (DR-1: 0/37 stay essential); rewrite ADR-043 (empty→non-empty registered, closed-world) + ADR-042 L35 + AC4 + design.md; (2) **scope-cut**: defer the `_entry_present_*`→`_entry_present` rename + its 41-changelog/27-shippability/~17-ADR frozen-history blast radius to a SEPARATE identifier-truth slice (DR-1-verified orthogonal to R-4). Verdict CLEAN (all ACCEPTED-FIXED, no ESCALATED/PENDING) — high-tier ⇒ mandatory rev-3 re-`/critique` of the pivoted design follows; **no auto-advance to `/build-slice`**.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | Structural pivot ratified: non-empty registered allowlist (register exactly the cross-module slice-019 LAYER-EVID-1 pin; DR-1-verified registered cardinality=1, R-4 retireable, charter-faithful). Decouple all in-`test_methodology_changelog.py` essentials (0/37 stay essential). ADR-043 rewritten empty→non-empty; ADR-042 L35 + AC4 + design.md de-falsified. |
| M1 | Major | ACCEPTED-FIXED | Scope-cut ratified: the rename is deferred to a separate identifier-truth slice (DR-1-verified orthogonal to R-4 — no test-fn-name dependency, breaks no structural enforcer). Removes the 41+27+~17 frozen-history blast radius from slice-041. |
| m1 | Minor | ACCEPTED-FIXED | Moot under the M1 scope-cut (no rename ⇒ no `test_critique_agent.py`/`agents/critique.md` literal edits in slice-041). |
