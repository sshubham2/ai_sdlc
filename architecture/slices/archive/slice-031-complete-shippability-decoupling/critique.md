# Critique: Slice 030B complete-shippability-decoupling (v2 re-critique)

**Critic reviewed**: redesigned mission-brief.md, design.md, ADR-030, ADR-031, risk-register R-4 sub-entry; v1 audit trail (critique-history-v1.md, critique-review-history-v1.md)
**Date**: 2026-05-17
**Result**: NEEDS-FIXES
**Round**: v2 (post user-ratified b-split redesign; v1 BLOCKED+EXTEND preserved as `*-history-v1.md`)

## Summary

The b-split **converged** (slice-030A precedent honored): the v2 Critic confirms the all-rows mechanical derivation + per-fn read-shape predicate is genuinely semantic (not disguised enumeration), the essential class is honestly carried as a `mitigating` R-4 residual with a concrete 030C charter, M-add-1 is DEFERRED-not-swept, and the **Builder D-3 watch is PASS** (the M-add-1-driven recommendation reversal was substantive engagement). The slice-030 flaw did NOT relocate a 5th time into the new mechanisms. Two v2 Blockers + one Major + two Minors remain — all specification-precision defects addressable in-slice without redesign/spike (hence NEEDS-FIXES, not BLOCKED). Builder self-check (rubber-stamp signal): v1 BLOCKED → v2 NEEDS-FIXES = convergence, NOT the 2-consecutive-BLOCKED-all-ACCEPTED danger pattern; all v2 findings independently verified against the actual files before acceptance.

## Findings

### Blockers (must address before /build-slice)

#### B1: Intent/AC2 success claim "the incidental rows become environment-independent" is false for mixed rows #8/#12
- **Claim under review**: mission-brief Intent — "a local `architecture/` drift can no longer false-PCA-1-HALT the incidental rows"; AC2 — "every incidental-decoupled fn ... PASSES with archive + ~/.claude/build-checks.md unavailable".
- **Issue**: Classification is per-fn (correct), but `/validate-slice` executes the catalog **row's command cell whole**. Rows #8 and #12 each cite, in one cell, BOTH incidental archive-backtest fns AND an essential entry-pin fn (`test_methodology_changelog.py::test_v_0_23_0_bc_1_v_1_2_entry_present_in_repo_and_installed` for #8; `::test_v_0_27_0_bc_proj_2_entry_present_in_repo_and_installed` for #12 — verified, reads `Path.home()/".claude"/"methodology-changelog.md"`). After 030B those rows STILL false-PCA-1-HALT on stale installed changelog via the (correctly not-decoupled) essential fn. The R-4 sub-entry is honest, but the slice's *own Intent/AC2 success framing* over-claims at row granularity — the slice-030 "claimed more than delivered" class relocated into the success claim.
- **Evidence**: shippability.md row #8 / #12 command cells; test_methodology_changelog.py L206-216; test_build_checks_audit.py L929-983.
- **Builder draft**: ACCEPTED-FIXED — verified (rows #8/#12 are genuinely mixed-class). Re-scope Intent + AC2 success predicate from "the incidental rows" → "every incidental-class **fn**"; add an explicit AC2 sub-clause stating mixed rows #8/#12 remain row-level environment-fragile via their co-cited essential fn until 030C (the honest R-4-`mitigating` boundary, not a 030B regression); add a mid-slice smoke eyeball that the env-patch run of #8/#12 still HALTs on stale changelog (proving the essential fn is correctly NOT decoupled). Applied to mission-brief this round.

#### B2: AC3 SKILL.md prose-pin test mis-located to a non-existent / wrong-skill module
- **Claim under review**: TF-1 plan row `tests/methodology/test_skill_md_pins.py::test_validate_slice_step4_consumes_machine_stable_command`; design.md "mirroring existing `test_skill_md_pins.py`".
- **Issue**: `tests/methodology/test_skill_md_pins.py` does not exist (verified — absent). The only `test_skill_md_pins.py` is `tests/skills/diagnose/test_skill_md_pins.py` (wrong skill). The validate-slice prose-pin home is `tests/methodology/test_validate_slice_skill.py` (verified present). The B2-v1 Blocker's verification anchor doesn't resolve — and a phantom `tests/...py` citation is exactly the PTFCD-1 class this slice's AC3 hardens against (self-trip).
- **Evidence**: `ls` confirms absence of `tests/methodology/test_skill_md_pins.py`, presence of `tests/methodology/test_validate_slice_skill.py` + `tests/skills/diagnose/test_skill_md_pins.py`.
- **Builder draft**: ACCEPTED-FIXED — verified. Repoint the AC3 TF-1 row + design.md to `tests/methodology/test_validate_slice_skill.py` (extend the existing validate-slice prose-pin module). TPHD-1 sub-mode (a): TF-1 plan harmonized in the same fix block. Applied this round.

### Majors (address this slice)

#### M1: Row #28 "prose normalized into a single token" hand-waves a genuine two-invocation→one-token semantic change
- **Issue**: Row #28's cell is **two** semantically distinct pytest invocations (`test_utf8_stdout_regression.py -q` ; `test_methodology_changelog.py -k v_0_42_0 -q` — verified `;`-joined). SCMD-1's single-token-no-`;` grammar forces a collapse that either drops a test surface (slice-028 catalog-coverage regression) or naively merges into one `pytest` call where `-k v_0_42_0` would now also filter the *first* module's collection (likely collecting ZERO from `test_utf8_stdout_regression.py` → silently drops the UTF8 surface). The D-2 footgun being closed is *narrative prose-as-command*, NOT *multiple clean commands*.
- **Evidence**: shippability.md row #28 ("Commands: `... test_utf8_stdout_regression.py -q` ; `... test_methodology_changelog.py -k v_0_42_0 -q`").
- **Builder draft**: ACCEPTED-FIXED — correct and a genuine design improvement. **Revise the SCMD-1 grammar** (ADR-031 + design): a `Machine-cmd` cell is *one or more `;`-separated grammar-conformant pytest invocations, prose-free* (not strictly a single token). This fully closes D-2 (prose-as-command is still rejected) while preserving #28's two distinct surfaces exactly — no lossy merge, no `-k` cross-contamination. Add a mid-slice eyeball that #28's normalized token collects the same pytest node set as the pre-normalization two commands. Applied to ADR-031 + design this round.

#### M2: Closed-world allowlist membership never concretely enumerated (the v1-M3 hand-list defect recurring one level down)
- **Issue**: For an anti-enumeration slice, the one hand-maintained list — the allowlist — is left abstract ("the slice-030A canonical-fixture constants + the verbatim-corpus accessor"). Concrete members exist (`_CANONICAL_PROJECT_FIXTURE`, `_CANONICAL_GLOBAL_FIXTURE`, the ADR-030 corpus accessor) plus resolve-*through* indirection symbols (`REPO_ROOT`, `read_file`, `_GLOBAL_BUILD_CHECKS`). Fail-closed direction is safe (errs to false-positive, not missed coupling) → Major not Blocker, but the implementer must not re-derive the allowlist ad hoc.
- **Evidence**: design.md "Components touched"; test_build_checks_audit.py `_CANONICAL_*_FIXTURE` constants.
- **Builder draft**: ACCEPTED-FIXED — fair. Enumerate the initial allowlist membership concretely in design.md (`_CANONICAL_PROJECT_FIXTURE`, `_CANONICAL_GLOBAL_FIXTURE`, the named corpus accessor) + the resolved-through indirection symbols (`REPO_ROOT`, `read_file` from conftest; `_GLOBAL_BUILD_CHECKS` as a *must-be-repointed* constant, NOT an allowlist member); state the fail-closed default explicitly; assert the allowlist by a test so a fixture-constant rename trips loudly. Applied to design this round.

### Minors (log; address if cheap)

#### m1: SCMD-1 grammar `<interp>` token under-specified
- **Issue**: Catalog rows use the machine-specific absolute `<HOME>/.claude/.venv/Scripts/python.exe`; #28's prose uses bare `python`. `<interp>` is unpinned → non-deterministic runner repoint (and the absolute path embeds a user home — a coupling smell, out of scope to fully fix here).
- **Builder draft**: ACCEPTED-FIXED — pin `<interp>` in ADR-031/design to a canonical placeholder form (the `<interp>`/`$PY` convention SKILL.md prose already uses); normalize #28's bare `python` accordingly. Applied this round. (Full interpreter-path portability remains out of scope — noted.)

#### m2: AC4 corpus-completeness sub-check is one-way (no orphan-fixture reverse check)
- **Issue**: AC4/ADR-030 assert "every derived archive folder has a tracked corpus fixture" but not the reverse (no orphan corpus fixture for a folder no longer derived) — dead test data, the speculative/dead smell.
- **Builder draft**: ACCEPTED-FIXED — add the reverse sub-check (derived set ⊇ corpus fixture set) to AC4 + ADR-030 (the SCPD-1 orphan-catch ADR-030 already gestures at, made concrete). Applied this round.

### Meta-Critic added findings (DR-1 v2 / critique-review EXTEND)

#### M-add-A (Major): SCMD-1's per-segment prose-discrimination mechanism is asserted but unspecified — the M1 fix recurs "claimed-more-than-delivered" inside itself
- **Claim under review**: ADR-031 + design.md "one or more `;`-separated grammar-conformant pytest invocations, prose-free … a leading `Commands:` is a violation"; "the grammar is net-new".
- **Issue**: The net-new discriminator (split on `;`; per-segment anchored full-match; reject leading bareword) was specified nowhere — design.md only prose-described the grammar. The only concrete shared artifact, `_TEST_PATH_RE` (`shippability_path_audit.py` L50), scans for `tests/…` *after* the first `pytest` and provably does NOT reject `Commands: \`python -m pytest tests/x\`` (it ignores the prefix). So the mechanism that makes the M1 `;`-relaxation safe was asserted, not pinned — same class as v2-B1, relocated into the M1 fix's grammar claim.
- **Evidence**: `shippability_path_audit.py` L50 `_TEST_PATH_RE` + `_extract_test_tokens` L112-129 (post-`pytest`, prefix-agnostic); ADR-031 "grammar is net-new" with no locus.
- **Builder draft**: ACCEPTED-FIXED — verified (the shared predicate cannot do the discrimination; the net-new check was unpinned). Applied this round: design.md Data-model-deltas now specifies the **concrete full-cell segment validator** in `tools/shippability_decoupling_audit.py` (strip fence → split `;` → each trimmed segment `re.fullmatch` an **interpreter-anchored** `^(<interp>|…python…) -m pytest tests/…$`; leading anchor rejects any bareword prefix; zero/failing segment ⇒ violation); ADR-031 Decision (a) updated to state the discriminator is net-new + concretely located + negative-fixture-pinned; **two AC3 TF-1 negative-fixture rows added** (`test_leading_bareword_prose_cell_is_violation`, `test_two_clean_semicolon_separated_invocations_pass`) so the discriminator is proven, not asserted (TPHD-1 sub-mode (b) harmonized).

## Dimensions checked
- [x] Unfounded assumptions — M1 (#28 trivial-normalization assumption), M2 (allowlist "principled" w/o membership), M-add-A (prose-discriminator asserted not pinned)
- [x] Missing edge cases — B1 (mixed rows #8/#12 row-vs-fn granularity)
- [x] Over-engineering — none (single-tool/single-rule justified; thin-vault conformant)
- [x] Under-engineering — B2 (B2-v1 verification anchor unresolvable)
- [x] Contract gaps — schema delta adequately specified (B3-v1 resolved); residual m1 (`<interp>` grammar)
- [x] Security — none (machine-specific interp path is a portability smell m1, not secret exposure)
- [x] Drift from vault — none blocking; R-4 verified `mitigating`, sub-entry charters 030C w/ 3-step DoD, M-add-1 DEFERRED-not-closed; ADR-030/031 self-correct v1's "7th"→"6th" + single-parser overstatement
- [x] Web-known issues — deliberate skip (no external SDK/API surface; only `ast`+pytest)
- [x] Cross-cutting conformance — B1 (claimed-more-than-delivered relocated into the success claim, caught), B2 (recursive self-application: PTFCD-1-hardening slice self-cites a phantom test path), Builder D-3 watch **PASS** (substantive convergence; root honestly carried to 030C, not patched-over)

## Triage

**Triaged by**: user
**Date**: 2026-05-17
**Final verdict**: CLEAN

v2 dual-pass reconciled (first Critic NEEDS-FIXES + meta-Critic EXTEND). The b-split converged (slice-030A precedent; meta confirms NOT a 5th relocation; Builder D-3 PASS, spot-checked). All v2 findings + the meta-added M-add-A are precision-spec fixes **applied to the artifacts this round** (ACCEPTED-FIXED) — no ACCEPTED-PENDING, no ESCALATED. Verdict computed mechanically: only ACCEPTED-FIXED → **CLEAN**. v1 audit trail preserved (`critique-history-v1.md`, `critique-review-history-v1.md`). M-add-1 remains DEFERRED to chartered slice-030C (R-4 stays `mitigating`).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | Intent/AC2 re-scoped per-fn + explicit #8/#12 row-fragility non-goal + mid-slice HALT-still-fires eyeball (mission-brief) |
| B2 | Blocker | ACCEPTED-FIXED | TF-1 row + verification plan + design.md repointed to `tests/methodology/test_validate_slice_skill.py::test_step4_5_5_consumes_machine_stable_command` (TPHD-1 harmonized) |
| M1 | Major | ACCEPTED-FIXED | SCMD-1 grammar revised → `;`-separated grammar-conformant pytest invocations, prose-free (ADR-031 + design); #28 two surfaces preserved |
| M2 | Major | ACCEPTED-FIXED | design.md enumerates concrete allowlist membership + resolve-through + must-repoint + fail-closed + asserted-by-test |
| m1 | Minor | ACCEPTED-FIXED | `<interp>` pinned to canonical placeholder (ADR-031 + design); #28 bare `python` normalized |
| m2 | Minor | ACCEPTED-FIXED | AC4 + ADR-030 bidirectional corpus-completeness (reverse orphan-fixture check added) |
| M-add-A | Major (meta-Critic, DR-1 v2) | ACCEPTED-FIXED | Concrete net-new full-cell segment validator pinned in design.md + ADR-031 + 2 AC3 TF-1 negative fixtures (prose-rejection proven, not asserted) |
