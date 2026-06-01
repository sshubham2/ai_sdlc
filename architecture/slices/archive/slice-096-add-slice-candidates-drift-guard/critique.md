# Critique: Slice 096 add-slice-candidates-drift-guard

**Critic reviewed**: mission-brief.md, design.md, milestone.md (worktree); verified against master tree: `tests/skill_drift_equality.py`, `tests/methodology/test_query_design_skill_drift.py`, `test_skill_drift_normalization.py`, `test_methodology_changelog.py`, `test_shippability_command_column.py`, `test_shippability_path_existence.py`, `CLAUDE.md`, `architecture/shippability.md`, `skills/slice-candidates/SKILL.md`, `tools/parallel_conflict_resolver.py`; slice-094 + slice-095 designs
**New ADRs**: none (MEPD-1 = EXCLUDE)
**Date**: 2026-06-01
**Result**: CLEAN (first-Critic raw verdict NEEDS-FIXES → resolved to CLEAN after all majors+minors applied as ACCEPTED-FIXED / DEFERRED and user TRI-1 ratification; see ## Triage)

## Summary

The slice is small, correct in shape, and the MEPD-1 = EXCLUDE disposition is the right call — but the design defended it with a **factually false precedent** (leg 2) that the Critic's framework specifically forbids rubber-stamping, and it carried two **stale/optimistic mechanical claims**: the shippability `#`-id (`101` is already taken on master by slice-093 — next free is `102`) and the characterization of the 3-way `shippability.md` overlap as a soft "additive append" when `_merge_shippability` actually **HARD-STOPs** on same-id/different-content. No blockers — the disposition itself is safe against every enforcing test — but three claims needed correction before build. **All three majors + minor m1 fixed at this Step (ACCEPTED-FIXED); m2 deferred (out of scope).**

## Findings

### Blockers (must address before /build-slice)

None. The EXCLUDE disposition was verified against the actual enforcing assertions in `tests/methodology/test_methodology_changelog.py`: no assertion fires on a missing slice-096 changelog entry, no count-pin exists on the guarded-skill set, and `test_version_files_synchronized_at_v_0_78_0` stays green at `0.78.0` under EXCLUDE (an INCLUDE bump would instead have to supersede it). The slice's own artifacts collide with nothing in 094/095's edit sets.

### Majors (address this slice)

#### M1: MEPD-1=EXCLUDE leg 2 rests on a false precedent — correct the rationale (keep the verdict)

- **Claim under review**: design.md §Sub-decisions leg 2 — *"Adding `slice-candidates` is the rule applied to one more member… The 17 prior members each landed as a per-skill test extension, not as a new RULE-ID."*
- **Issue**: The "landed as a per-skill test extension [only]" framing is false against the vault. **slice-051** added the `reflect` member to the *same* open-ended OSDG-1 set and shipped a methodology-changelog entry (**v0.59.0**), **ADR-053**, **shippability row #51**, and two entry-pin tests. **slice-088** recorded its OSDG-1 guarded-set extension as the *"OSDG-1 guarded-set extended"* "M3a discharge" inside the v0.78.0 PFS-1 entry. So OSDG-1 member-adds have in fact been changelog-recorded. The verdict (EXCLUDE) is still correct — but for a reason the design does not state: in each prior case the changelog entry was driven by a *co-occurring* event (049 minted the rule; 051 carried the ADR-053 "Opener-Skill name → historical label, not a scope boundary" semantic re-scope; 088 minted PFS-1). **slice-096 carries no co-occurring semantic decision** — it is a pure member-add within scope that 051/ADR-053 already settled. The Critic's Dimension-7 framework explicitly flags resting an EXCLUDE on a Builder-asserted "slice-NNN did/didn't X" precedent *without confirming it against the enforcing artifact* — the slice-032 m1 false-precedent anti-pattern.
- **Evidence**: `tests/methodology/test_methodology_changelog.py:3380-3467` (slice-051 v0.59.0 entry-pin + row-#51 pin); `:5410-5453` (slice-088 v0.78.0 "OSDG-1 guarded-set extended" pin); `architecture/shippability.md` rows #49, #51 present on master.
- **Proposed fix**: Rewrite leg 2 to the accurate basis (prior member-adds WERE recorded but each rode a co-occurring rule event; slice-096 has none → nothing new to record). Add the explicit "verified against the enforcer" sentence.
- **Builder draft**: **ACCEPTED-FIXED** — leg 2 rewritten at `design.md` §Sub-decisions (MEPD-1 leg 2) to the co-occurring-event basis + the "verified against `test_methodology_changelog.py` / version-gate stays 0.78.0" sentence. The Critic's evidence (slice-051 v0.59.0/ADR-053/row#51; slice-088 v0.78.0) is accurate; the false-precedent framing is removed.

#### M2: shippability `#`-id 101 is stale — already taken by slice-093 on master; next free id is 102

- **Claim under review**: design.md L10 / L34 / L61 + mission-brief "row 101" — *"one new catalog row (next id **101**)"* / *"append after current row 100"* / *"this slice writes the next free id (**101**)"*.
- **Issue**: On master (`architecture/shippability.md`), the catalog has 100 rows with `#`-ids running 1–101 (id 76 absent), **max id = 101**, and **row 101 already belongs to slice-093** (`| 101 | slice-093-add-external-vault-support`). slice-093 merged recently (commit e4acd9a). The design's "row 100 is the tail / 101 is next" was computed against a pre-slice-093 tree. The actual next free id is **102**.
- **Evidence**: `architecture/shippability.md` — verified by Builder re-grep: `max id 101, num rows 100, missing [76]`; row `| 101 | slice-093-…`.
- **Proposed fix**: Change all three sites to **id 102**; re-confirm `max+1` at build (094/095 merging first would shift it).
- **Builder draft**: **ACCEPTED-FIXED** — Builder independently re-verified max `#`-id = 101 = slice-093; updated all three design sites + the ledger to **102** with a "re-confirm `max(existing #-id)+1` at build" note. See M3 for why the exact id is secondary.

#### M3: 3-way `shippability.md` overlap is mischaracterized as soft "additive append" — `_merge_shippability` HARD-STOPs on same-id/different-content

- **Claim under review**: design.md §Parallel-safety + "shippability row id at merge" — *"additive append — the documented PCR-resolvable parallel-safe overlap, NOT a code collision"*; *"whichever merges first keeps 101; later ones renumber … the PCR machinery owns it."*
- **Issue**: `_merge_shippability` (`tools/parallel_conflict_resolver.py:1785`) does a row-union keyed on the **`#`-id integer** (`_parse_shippability_rows` regex `^\|\s*(\d+)\s*\|`). Its defense-in-depth check (`:1814-1822`) raises `_SoftResolutionError(..., ConflictClass.HARD)` when *the same id appears on both branches with different content*. If 094/095/096 each compute the same "next id" and append a *different-content* row there, the 2nd/3rd `/commit-slice --merge` hits exactly that condition → **HARD escalation = STOP**, requiring manual renumber. Not a silent additive auto-merge. The *outcome* the design names ("later ones renumber") is right; the *mechanism* (automatic/soft) is wrong.
- **Evidence**: `tools/parallel_conflict_resolver.py:1814-1822` (HARD escalation), `:1842-1857` (`#`-id keying), `:1827-1832` (union).
- **Proposed fix**: Correct the prose — it is a cheap, manual one-line renumber at merge, not an automatic PCR resolution; drop "NOT a code collision."
- **Builder draft**: **ACCEPTED-FIXED** — both the "shippability row `#`-id at merge" sub-decision and the Parallel-safety ledger row rewritten to: cheap **manual-renumber merge collision** on the `#`-id surface; `_merge_shippability` HARD-STOPs (`parallel_conflict_resolver.py:1816`) on same-id/different-content; "NOT a code collision" removed. m2's accurate "#-id" term used.

### Minors (log; address if cheap)

#### m1: AC2 "no enforced-but-undocumented member" parity is overstated — `pulse` and `code-review` are already enumeration gaps

- **Claim under review**: mission-brief AC2 / design L9 — updating the CLAUDE.md OSDG-1 enumeration so *"no enforced-but-undocumented member"* remains true.
- **Issue**: The OSDG-1 `Guarded skills:` enumeration in `CLAUDE.md:42` already omits two skills that DO have drift tests: `pulse` (`test_pulse_skill_drift.py`) and `code-review` (`test_code_review_skill_drift.py`). Adding `slice-candidates` is correct and in-scope, but the AC's claim of restoring full prose↔reality parity over-claims. There is **no test pinning the enumeration to the drift-test set** (Claim 4 = confirmed absent), so AC2 is a courtesy-parity edit, not an enforced one.
- **Evidence**: `CLAUDE.md:42`; `test_pulse_skill_drift.py`, `test_code_review_skill_drift.py` exist; no count/parity assertion found.
- **Proposed fix**: Soften AC2 to scope it to the R-13 gap + note pulse/code-review remain out of scope.
- **Builder draft**: **ACCEPTED-FIXED** — AC2 softened in `mission-brief.md` to "courtesy-parity edit closing the R-13-specific gap"; explicitly records pulse + code-review remain out of scope and that no enumeration↔drift-test pin exists.

#### m2: `_parse_shippability_rows` docstring says "slice number" but keys on `#`-id — pre-existing, but relevant to M3's accuracy

- **Claim under review**: (not slice-096's code) — `tools/parallel_conflict_resolver.py:1845` docstring *"keyed by slice number"*.
- **Issue**: The keying is on the `#`-id integer, not the slice number; the docstring is misleading and likely seeded the design's mischaracterization in M3. Out of scope to fix here (not slice-096's file; "refactors need a slice").
- **Evidence**: `tools/parallel_conflict_resolver.py:1845` vs `:1853` regex.
- **Proposed fix**: Log only; the M3 fix prose should say "`#`-id", not "slice number".
- **Builder draft**: **DEFERRED** — pre-existing docstring in `tools/parallel_conflict_resolver.py` (slice-094's file; not slice-096's edit set). Out of scope per CLAUDE.md "refactors need a slice." The M3 fix prose now uses the accurate "`#`-id" term and notes the mislabel. Backlog target: fold into a future PCR-touching slice (or slice-094, which already owns this file).

## Dimensions checked

- [x] **Unfounded assumptions** — M1 (false-precedent rationale for EXCLUDE), M2 (stale "next id 101"), M3 ("additive append, not a collision"). Verified by reading implementations, not prose.
- [x] **Missing edge cases** — none beyond M3 (the live 3-way concurrent-merge edge). CRLF: `skills/slice-candidates/SKILL.md` confirmed zero-CRLF in working tree. Empty/missing-installed: inherited from the shared helper. PTFCD-1 path-existence resolves (file created same build).
- [x] **Over-engineering** — none. Byte-clone of the established 17-member pattern; no speculative generality. Standard mode — no per-component file duplication.
- [x] **Under-engineering** — none. Every AC maps to a design element. TF-1 N/A (`test-first: false`). MEPD-1 disposition explicitly decided + verified against the enforcer.
- [x] **Contract gaps** — none. No endpoints/events/schemas; the only interface (pytest pass/fail + inherited `AssertionError`) is unchanged.
- [x] **Security** — none. Test-only methodology tooling; no auth/authz/input/secret/PII surface. Cooperative model (ADR-067).
- [x] **Drift from vault** — M1 is load-bearing here (EXCLUDE rationale's precedent claim contradicted the vault; verdict does not). Independence from 094/095 confirmed empirically: slice-095 design touches no CLAUDE.md/OSDG-1/slice-candidates; `/slice-candidates` writes only `diagnose-out/` (0 `architecture/` refs).
- [x] **Web-known issues** — N/A: zero external technology/API/third-party pattern (pytest + in-house comparator only).
- [x] **Cross-cutting conformance** — APED-1 (no minted regex/glob in this slice — reuses unchanged `assert_md_forward_synced`); PTFCD-1 (new row's cited path created same build); version-gate semantics (EXCLUDE keeps `test_version_files_synchronized_at_v_0_78_0` untouched); SCPD-1/RPCD-1 (new audit row propagated into shippability per AC4). M3 = the architectural-concurrency finding (id-keyed HARD-STOP under the active parallel-slice trajectory).

## Triage

**Triaged by**: user
**Date**: 2026-06-01
**Final verdict**: CLEAN

Reconciles both passes (first Critic + meta-Critic EXTEND). The meta-Critic's missed finding (m-add-1) is added as a triage row per the DR-1 reconciliation rule. M1 severity kept Major (user declined the meta-Critic's optional Major→Minor downgrade).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | design.md §Sub-decisions MEPD-1 leg 2 rewritten to the co-occurring-rule-event basis + "verified against `test_methodology_changelog.py` / version-gate stays 0.78.0" line |
| M2 | Major | ACCEPTED-FIXED | design.md L10 / shippability-component / merge-sub-decision + ledger → next free `#`-id **102** (row 101 = slice-093), with "re-confirm `max+1` at build" |
| M3 | Major | ACCEPTED-FIXED | design.md shippability-merge sub-decision + Parallel-safety ledger row → "cheap manual-renumber HARD-STOP (`parallel_conflict_resolver.py:1816`), NOT a silent union"; dropped "not a code collision" |
| m1 | Minor | ACCEPTED-FIXED | mission-brief.md AC2 softened to a courtesy-parity edit (R-13 gap only; pulse + code-review remain out of scope; no enumeration↔drift-test pin exists) |
| m2 | Minor | DEFERRED | pre-existing docstring mislabel in `tools/parallel_conflict_resolver.py` (slice-094's file, not slice-096's edit set); out of scope per CLAUDE.md "refactors need a slice"; fold into a future PCR-touching slice (or slice-094, which owns the file). M3 fix prose uses the accurate "`#`-id" term |
| m-add-1 | Minor | ACCEPTED-FIXED | (meta-Critic missed finding) design.md shippability-component note gains the SCMD-1 (ADR-031) requirement: clone row 101's full 6-column shape incl. the `Machine-cmd` cell; `test_shippability_command_column.py` is a HARD validate-gate |
