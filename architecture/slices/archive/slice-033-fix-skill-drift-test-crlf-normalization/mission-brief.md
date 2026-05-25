# Slice 033: fix-skill-drift-test-crlf-normalization

**Mode**: Standard
**Estimated work**: 0.5–1 day (AC5 changelog/version/CLAUDE.md surface is mechanical + well-precedented across slices 007–032)
**Risk retired**: [[risk-register#R-5]] (skill-drift tests CRLF/LF-fragile under Windows `core.autocrlf=true` — spurious in-repo↔installed false-FAIL; HIGH likelihood, open, N+2 recurrence at slice-030A/031/032)
**Test-first**: true
<!-- per TF-1: failing repro pre-exists (verified live at /slice); the must-not-mask-real-drift property is naturally test-first. Field-line kept BARE per R-7 — a trailing annotation on this line breaks test_first_audit.py's `\s*$`-anchored regex and silently default-off-bypasses the entire TF-1 gate (slice-031 remedy). -->
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Every Windows contributor with `core.autocrlf=true` hits a spurious FAIL on the
skill-drift byte-equality tests because the in-repo working-tree copy is checked
out CRLF while the installed `~/.claude/.../SKILL.md` copy is LF — even when the
content is byte-identical after line-ending normalization. This has produced a
false PCA-1 HALT on three consecutive innocent slices (030A/031/032). This slice
makes the skill-drift (and sibling CAD-1/mini-CAD) `.md` byte-equality
comparisons line-ending-agnostic, adds a `.gitattributes` durability guard so
future `.md` equality guards don't regress on Windows, and proves the fix does
**not** weaken real-drift detection (the CAD-1/mini-CAD self-hosting safety
property).

## Acceptance criteria

1. All five `test_*_skill_drift.py` comparisons (`tests/skills/diagnose/test_diagnose_skill_drift.py`, `tests/methodology/test_slice_skill_drift.py`, `test_build_slice_skill_drift.py`, `test_commit_slice_skill_drift.py`, `test_query_design_skill_drift.py`) **and** the CAD-1 audit (`tools/critique_agent_drift_audit.py::_sha256_of`) normalize line endings (CRLF→LF) before equality via the shared `tests/skill_drift_equality.py` comparator (skill-drift) / inline normalization (CAD-1); the pre-existing failing repro `tests/skills/diagnose/test_diagnose_skill_drift.py::test_in_repo_and_installed_diagnose_skill_md_are_content_equal` PASSES under `core.autocrlf=true` with a CRLF working tree and LF installed copy whose content is normalized-identical.
2. Real-drift detection is preserved on BOTH surfaces: (a) a NEW regression test asserts genuinely divergent content (a real forward-sync miss, not just line endings) STILL FAILs the shared skill-drift comparator; (b) the EXISTING CAD-1 genuine-divergence tests (`test_critique_agent_drift.py::test_drift_detection_fires_on_artificial_byte_flip` + the CLI exit-code matrix `test_critique_agent_drift_audit_cli_exits_0_on_clean_1_on_drift_2_on_missing`) STILL PASS (exit 1 on `# v1` vs `# v2`) post-normalization, bound here as the CAD-1-side must-not-mask proof; a new CAD-1 EOL-only test is the complement (CRLF vs LF identical → exit 0).
3. A `.gitattributes` entry declares the guarded `.md` surface (`skills/**/SKILL.md`, `skills/diagnose/passes/*.md`, `agents/*.md`) `text eol=lf`, AND the slice runs a targeted `git add --renormalize -- <those globs>` so the guarded in-repo files contain no `\r\n` in the working tree; verified by a test that asserts each guarded in-repo file contains zero `\r\n` bytes (working-tree-state check, NOT merely `git check-attr`).
4. AC4 is a *property of the AC1 fix*, not a procedure: because the AC1 comparator is line-ending-agnostic, shippability catalog rows #1 (`slice-001`, via `tests/skills/diagnose/`) and #19 (`slice-019`) PASS post-fix on a CRLF working tree **independent of cp-state** (the slice-030A masking-by-cp anti-pattern is structurally impossible to reintroduce — equality no longer depends on byte-identical line endings). validation.md records this as a property, not a "no prior cp" manual step.
5. Governing-surface consistency for the restated invariant, under minted RULE-ID **EOL-DRIFT-1** (m-add-1): (a) `methodology-changelog.md` carries a new `## v0.47.0` entry headed `**EOL-DRIFT-1 — .md forward-sync drift guards are EOL-agnostic**` (rule-ref + defect-class + validation-method) forward-synced in-repo↔installed; (b) atomic version bump `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml` `version` 0.46.0 → 0.47.0; (c) `CLAUDE.md` L33/L36 "MUST be byte-equal" corrected to the precise invariant ("MUST be content-equal modulo line endings (EOL-agnostic per ADR-033 / EOL-DRIFT-1)"); each pinned by a regression test (`test_methodology_changelog.py::test_v_0_47_0_eol_drift_1_entry_present_in_repo_and_installed` — name derives from the RULE-ID per the v0.46.0 `qd_1` precedent — + a CLAUDE.md substring pin mirroring `test_root_claude_md_branch_per_slice_rule.py`).

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0). The repro for AC1 already
exists and fails live (verified at `/slice`: in-repo `971e2326…` vs installed
`aaab3190…`, `norm equal: True`) — its row starts WRITTEN-FAILING. New tests
start PENDING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | drift-guard | tests/skills/diagnose/test_diagnose_skill_drift.py | test_in_repo_and_installed_diagnose_skill_md_are_content_equal | PASSING |
| 1 | drift-guard | tests/methodology/test_slice_skill_drift.py | test_in_repo_and_installed_slice_skill_md_are_content_equal | PASSING |
| 2 | unit | tests/methodology/test_skill_drift_normalization.py | test_normalized_compare_treats_crlf_and_lf_identical_content_as_equal | PASSING |
| 2 | unit | tests/methodology/test_skill_drift_normalization.py | test_normalized_compare_still_fails_on_genuine_content_divergence | PASSING |
| 2 | regression-bind | tests/methodology/test_critique_agent_drift.py | test_drift_detection_fires_on_artificial_byte_flip | PASSING |
| 2 | regression-bind | tests/methodology/test_critique_agent_drift.py | test_critique_agent_drift_audit_cli_exits_0_on_clean_1_on_drift_2_on_missing | PASSING |
| 2 | unit | tests/methodology/test_critique_agent_drift.py | test_cad1_audit_treats_crlf_and_lf_identical_content_as_clean | PASSING |
| 3 | config-guard | tests/methodology/test_skill_drift_normalization.py | test_guarded_md_files_have_no_crlf_in_working_tree | PASSING |
| 4 | regression-bind | tests/skills/diagnose/test_diagnose_skill_drift.py | test_in_repo_and_installed_diagnose_skill_md_are_content_equal | PASSING |
| 5 | changelog-pin | tests/methodology/test_methodology_changelog.py | test_v_0_47_0_eol_drift_1_entry_present_in_repo_and_installed | PASSING |
| 5 | claude-md-pin | tests/methodology/test_root_claude_md_cad1_eol_agnostic.py | test_claude_md_cad1_mini_cad_states_eol_agnostic_invariant | PASSING |

(Final test-module name/paths are advisory — `/build-slice` plan-mode locks the exact shape against the actual enforcing audits; the AC-coverage mapping is the contract. Rows marked PASSING are pre-existing tests bound as regression guards — they must remain green post-normalization, not be written failing-first.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Skill-drift tests + CAD-1 audit CRLF-agnostic + repro passes | `<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/skills/diagnose/test_diagnose_skill_drift.py tests/methodology/test_slice_skill_drift.py tests/methodology/test_build_slice_skill_drift.py tests/methodology/test_commit_slice_skill_drift.py tests/methodology/test_query_design_skill_drift.py tests/methodology/test_critique_agent_drift.py -q` → all PASS with `git config core.autocrlf` = `true` and the in-repo `.md` files CRLF in the working tree (the diagnose repro started WRITTEN-FAILING) |
| 2 | Real drift still caught on BOTH surfaces | (a) new `test_normalized_compare_still_fails_on_genuine_content_divergence` PASSES; (b) existing `test_drift_detection_fires_on_artificial_byte_flip` + CLI exit-code-matrix STILL exit 1 post-normalization; (c) a temporary genuine 1-char (non-EOL) edit to an in-repo SKILL.md makes its skill-drift test FAIL; revert |
| 3 | Guarded `.md` working tree is LF (state, not declaration) | `test_guarded_md_files_have_no_crlf_in_working_tree` PASSES (asserts zero `\r\n` bytes in every guarded in-repo file post-`git add --renormalize`); `git check-attr eol -- <guarded globs>` reports `lf` as a secondary signal only |
| 4 | Catalog rows #1/#19 green as a *property of AC1* | With CRLF working tree, run row #1 + row #19 `Command` cells from `architecture/shippability.md`; both PASS regardless of cp-state (validation.md records this as cp-state-independent, not a "no prior cp" manual step) |
| 5 | Governing-surface consistency (RULE-ID EOL-DRIFT-1) | `test_v_0_47_0_eol_drift_1_entry_present_in_repo_and_installed` PASSES (changelog entry in-repo↔installed); `VERSION` = `~/.claude/ai-sdlc-VERSION` = `plugin.yaml` version = `0.47.0`; `test_claude_md_cad1_mini_cad_states_eol_agnostic_invariant` PASSES (CLAUDE.md L33/L36 no longer say "MUST be byte-equal"); PMI-1 audit clean |

## Must-not-defer

- [ ] Normalization MUST NOT mask real drift — explicit regression test that genuine (non-line-ending) content divergence still FAILs every patched skill-drift comparator AND the existing CAD-1 drift-detection tests still exit 1 (the CAD-1/mini-CAD correctness property; B2/M2).
- [ ] All five skill-drift tests + CAD-1 audit patched **uniformly** via the shared comparator / one-line audit normalization — no partial fix leaving a latent CRLF-fragile sibling (slice-030A's masking-by-cp lesson).
- [ ] The comparator change preserves a meaningful failure message (path + which side diverged) so a real future drift is still actionable, not silently swallowed.
- [ ] No weakening of the equality intent for non-`.md` artifacts (normalization scoped to text/`.md` comparisons, not a blanket binary-insensitive compare).
- [ ] Governing-surface consistency (B1/B2): the slice does NOT ship a restated CAD-1/mini-CAD invariant while `CLAUDE.md` still says "MUST be byte-equal" or while `methodology-changelog.md`/`VERSION` lack the v0.47.0 surface — these are corrected in-slice, not deferred to `/reflect`.

## Out of scope

- Whole-*vault* `.md` working-tree renormalization (`git add --renormalize .`) — large blast radius across the vault. **In scope (M1 ACCEPTED-FIXED)**: targeted `git add --renormalize` of the AC3 guarded globs only (`skills/**/SKILL.md`, `skills/diagnose/passes/*.md`, `agents/*.md`) — bounded, the git blobs are already LF so the index diff is empty.
- The `/validate-slice` Step-5.5 shippability-catalog runner `;`-split contract (slice-032 secondary discovery in R-5). Distinct SCMD-1-adjacent runner-parsing concern, not a `.md` byte-compare normalization issue. **Concrete deferral handle (m2 ACCEPTED-FIXED)**: a new risk-register entry `R-8 — shippability Step-5.5 runner ;-split contract unpinned` to be opened at `/reflect` (tracked, not a bare prose mention).
- Changing CAD-1's `tools/critique_agent_drift_audit.py` *exit-code / CLI* contract — only its equivalence relation becomes EOL-agnostic (the one-line `_sha256_of` normalization); exit 0/1/2 semantics unchanged.
- Any change to skill/agent `.md` *content* (line endings only; the renormalize is byte-faithful — git blobs already LF).

## Dependencies

- Failing repro (BFRD-1, pre-satisfied & verified live at `/slice`): `tests/skills/diagnose/test_diagnose_skill_drift.py::test_in_repo_and_installed_diagnose_skill_md_are_content_equal` — FAILs now under `core.autocrlf=true` (in-repo `971e2326…` vs installed `aaab3190…`; `norm equal: True` confirms CRLF-only, not real drift).
- Risk register: [[risk-register#R-5]] (chartered fix candidate `fix-skill-drift-test-crlf-normalization`; N+2 at slices 030A/031/032).
- Prior slices: [[slice-007-add-critique-agent-content-equality-audit]] (CAD-1 byte-equality pattern), [[slice-010-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic]] (mini-CAD for `slice/SKILL.md`), [[slice-019-harden-diagnose-layering-evidence]] (mini-CAD for `/diagnose`), [[slice-030-repair-build-checks-vault-and-harden-shippability]] (masking-by-cp anti-pattern; R-5 first recorded).
- Vault refs: [[shippability.md]] rows #1, #19; CLAUDE.md "Self-hosting discipline" (CAD-1 / mini-CAD).

## Mid-slice smoke gate

At ~50% of build (shared comparator + skill-drift tests patched, regression test written), run:
```
<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/skills/diagnose/test_diagnose_skill_drift.py::test_in_repo_and_installed_diagnose_skill_md_are_content_equal tests/methodology/test_skill_drift_normalization.py tests/methodology/test_critique_agent_drift.py -q
```
Expected: (1) the repro now PASSES (CRLF-agnostic); (2) the new real-drift regression test PASSES (genuine divergence still FAILs the shared comparator); (3) the EXISTING CAD-1 drift-detection tests STILL PASS (genuine `# v1`/`# v2` divergence still exit 1 post-normalization); (4) the diagnose-subpackage import of `tests.skill_drift_equality` resolves under the sys.path-mutating `tests/skills/diagnose/conftest.py` (M3 — assert explicitly, do not extrapolate from the `tests/methodology/` precedent). If the repro passes but any real-drift test does not catch divergence: STOP — the fix is masking the defect class, not normalizing it.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] TF-1 audit (`tools/test_first_audit.py --strict-pre-finish`) all rows PASSING
- [ ] CAD-1 / mini-CAD byte-equality still meaningfully enforced (real-drift regression test green)
