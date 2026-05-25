# Slice 020: codify-bug-fix-repro-prelude-at-slice

**Mode**: Standard
**Estimated work**: 0.5 day (~60-90 min + ~20 min /critique M5 helper-generalization addition; SMALL-to-MEDIUM mirroring slice-010 MCT-1 prose-codification scope at 1 skill surface)
**Risk retired**: No R-N retired (methodology-internal discipline codification; no risk-register entry — latent class discovered at slice-020 codification time per /critique M3 ACCEPTED-FIXED). Class description: bug-fix slices defined without a pre-existing failing repro test. CLAUDE.md "Tests-first for bug fixes" rule names `/repro` but `/slice` itself never enforces the prerequisite, so the discipline is exercise-on-the-honor-system. A bug-fix slice that skips `/repro` ships either (a) a passing-test-on-buggy-code mirage or (b) no regression guard at all, allowing silent recurrence.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Codify **BFRD-1** (Bug-Fix Repro Discipline-1, -D suffix per slice-011 RSAD-1 / slice-013 EPGD-1 / slice-015 SCPD-1 / slice-016 RPCD-1 / slice-017 TPHD-1 convention N=5 stable) as a 1-surface skill-prose discipline at `skills/slice/SKILL.md`. The rule: when the chosen slice candidate is a bug fix (name begins with `fix-`, or the user/candidate-source identifies it as a defect), `/slice` MUST verify a failing test reproducing the bug exists BEFORE writing the mission brief. If no such test exists, `/slice` STOPS and instructs the user to run `/repro <issue>` first; on `/repro` completion, the user re-invokes `/slice` and the failing-test path is cited under `Dependencies` with one AC asserting "the repro test PASSES at slice end".

This makes `/slice` the single entry point for both new-feature and bug-fix slices, with `/repro` invoked as a hard prerequisite rather than a parallel skill the user might forget. The discipline preserves `/repro`'s ordering invariant (failing test exists BEFORE slice exists) while reducing entry-point ambiguity.

## Acceptance criteria

1. `methodology-changelog.md` v0.34.0 entry exists in-repo AND in installed copy (`~/.claude/plugins/ai-sdlc/methodology-changelog.md`) with sha256 byte-equality; entry names BFRD-1 canonical phrase `bug-fix repro prelude discipline` + both detection modes ((a) name-shape fast-path covering `fix-*` prefix + `*-fix` suffix + `bugfix-*` / `hotfix-*` / `defect-*` / `repair-*` / `patch-*` / `harden-*-bug` variants per /critique B1 ACCEPTED-FIXED + (b) PRIMARY candidate-source signal) + STOP-and-route-to-`/repro` behavior + verification-mechanism canonical phrase `shippability.md grep verification` per /critique B2 ACCEPTED-FIXED + ADR-018 pin + Limitations note acknowledging prose-heuristic semantics (no audit-enforced gate; v2 `tools/bfrd_1_audit.py` deferred until N≥3 violations recur post-codification per slice-011 RSAD-1 / slice-016 RPCD-1 / slice-017 TPHD-1 prose-heuristic precedent) + slice-001 witnessed false-negative anchor for mode (a) prefix-only naïve detection (per /critique B1 ACCEPTED-FIXED) + operational violation-detector definition per /critique m2 ACCEPTED-FIXED.

2. `skills/slice/SKILL.md` carries a NEW `### Step 3c: Bug-fix prelude (BFRD-1)` section placed between existing Step 3b ("If user has their own idea") and Step 4 ("Define the slice"). Section names BOTH detection modes (mode (a) name-shape fast-path with regex variants + mode (b) PRIMARY candidate-source signal), the verification mechanism (grep `architecture/shippability.md` for /repro-added row signature per /critique B2 ACCEPTED-FIXED), the STOP semantics when no repro test exists, the re-invoke path after `/repro`, and the mission-brief consequences (failing-test path under Dependencies + one AC asserting "repro test PASSES"). Section is location-pinned between Step 3b and Step 4 anchors.

3. `architecture/decisions/ADR-018-bfrd-1-bug-fix-repro-prelude-discipline.md` exists; reversibility=cheap with magnitude justification ~11 sites (1 skill file + sync mirror + methodology-changelog + sync mirror + 3 version files (VERSION + ai-sdlc-VERSION + plugin.yaml.version) + 2 test files (test_slice_skill.py + test_methodology_changelog.py) + shippability row + ADR file itself — recount per /critique B3 ACCEPTED-FIXED resolves prior 11-vs-~8-10 count drift); supersedes=null; extends ADR-016 (TPHD-1) at the cross-cutting-tooling skill-prose-discipline layer per slice-017 calibration-trail convention; canonical phrase `bug-fix repro prelude discipline` pinned in title or body.

4. Prose-pin tests written test-first per TF-1 plan covering: methodology-changelog v0.34.0 entry-pin (entry present + both detection modes named + verification-mechanism phrase named + ADR-018 pin + STOP-and-route prose) AND `skills/slice/SKILL.md` BFRD-1 prose (`_present` substring + `_location_pinned` scoped-find between Step 3b and Step 4 anchors per slice-009 M1 + slice-017 N=5 stable `_present` + `_location_pinned` duality precedent + `_verification_mechanism_present` substring per /critique B2 ACCEPTED-FIXED). PMI-1 v1.1 version-agnostic gate passes unchanged through atomic version bump 0.33.0 → 0.34.0 (retirement-proof atomic-bump count N=5 → N=6 stable per /critique m5 ACCEPTED-FIXED disambiguation).

5. `architecture/shippability.md` row 20 added enumerating BFRD-1 critical-path tests (~5 pytest commands across `test_methodology_changelog.py` + `test_slice_skill.py` + `test_slice_skill_drift.py` for mini-CAD bidirectional byte-equality on `skills/slice/SKILL.md`); full shippability catalog (20/20 rows) PASSES at `/validate-slice` Step 5.5 in <2 min aggregate; no rows 1-19 regressed by slice-020 changes. SCPD-1 stays at N=3 stable (slice-020 has NO Dim 9 sub-clause supersession event, so SCPD-1 proactive-application is vacuously satisfied — row 20 added as NEW row with no prior-row touch needed).

## Test-first plan

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING -> PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_34_0_bfrd_1_entry_present_in_repo_and_installed | PASSING |
| 1 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_34_0_bfrd_1_entry_names_both_detection_modes | PASSING |
| 1 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_34_0_bfrd_1_entry_names_stop_and_route_behavior | PASSING |
| 1 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_34_0_bfrd_1_entry_names_verification_mechanism | PASSING |
| 2 | methodology | tests/methodology/test_slice_skill.py | test_slice_skill_md_bfrd_1_prelude_present | PASSING |
| 2 | methodology | tests/methodology/test_slice_skill.py | test_slice_skill_md_bfrd_1_prelude_location_pinned | PASSING |
| 2 | methodology | tests/methodology/test_slice_skill.py | test_slice_skill_md_bfrd_1_verification_mechanism_present | PASSING |
| 2 | methodology | tests/methodology/test_slice_skill_drift.py | test_in_repo_and_installed_slice_skill_md_are_content_equal | PASSING |
| 3 | methodology | tests/methodology/test_methodology_changelog.py | test_adr_018_exists_and_names_bfrd_1_canonical_phrase | PASSING |
| 4 | methodology | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_invariant | PASSING |
| 5 | (verified at /validate-slice) | architecture/shippability.md | row 20 added; 20/20 catalog rows PASS | PASSING |

Total: 11 TF-1 rows post-/critique fix-prose harmonization (was 9; +2 added at /critique B2 ACCEPTED-FIXED — `test_v_0_34_0_bfrd_1_entry_names_verification_mechanism` + `test_slice_skill_md_bfrd_1_verification_mechanism_present`). 7 PENDING → WRITTEN-FAILING → PASSING (was 5 + 2 B2 new) + 1 mini-CAD-1 PASSING → WRITTEN-FAILING → PASSING transition per slice-007/009/010/011/012/013/015/016/017/019 row precedent N=10 stable + PMI-1 v1.1 invariant + catalog-level row deferred to /validate-slice. Slimmer than slice-017 (12 rows) because BFRD-1 spans 1 skill file vs TPHD-1's 3 skill files; expansion to 11 rows tracks /critique B2 verification-mechanism pin addition (TPHD-1 sub-mode (a) self-application N=3 → N=4 stable: TF-1 plan harmonized in same /critique fix block as design.md Step 3c content structure).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | methodology-changelog v0.34.0 entry | `pytest tests/methodology/test_methodology_changelog.py -k v_0_34_0_bfrd_1 -q` returns 0 (3 tests PASS); bidirectional sha256 forensic capture in /build-slice Phase 2 confirms byte-equality at single hash value (N=15 → N=16 stable) |
| 2 | `/slice` skill carries BFRD-1 prose | `pytest tests/methodology/test_slice_skill.py -k bfrd_1 -q` returns 0 (2 tests PASS); mini-CAD bidirectional byte-equality preserved via `test_slice_skill_drift.py` |
| 3 | ADR-018 exists | `pytest tests/methodology/test_methodology_changelog.py::test_adr_018_exists_and_names_bfrd_1_canonical_phrase -q` returns 0; manual file existence check |
| 4 | Test-first audit clean | `python -m tools.test_first_audit architecture/slices/slice-020-codify-bug-fix-repro-prelude-at-slice/mission-brief.md --strict-pre-finish` returns 0; PMI-1 v1.1 atomic version bump 0.33.0 → 0.34.0 with zero gate-body modification |
| 5 | Shippability row 20 + full catalog | `architecture/shippability.md` has row 20 with BFRD-1 critical-path tests; manual run at /validate-slice Step 5.5 → 20/20 PASS in <2 min |

## Must-not-defer

- [ ] Input validation: rule-ID format consistency — BFRD-1 canonical-form used uniformly across mission-brief + design.md + ADR-018 + methodology-changelog + skills/slice/SKILL.md + test files. Verification: positive-form assertion `grep -c "BFRD-1" <file>` returns ≥1 hit per surface.
- [ ] Authorization check: N/A (no auth surface touched)
- [ ] Logging: N/A (no runtime code touched; pure prose codification)
- [ ] PMI-1 v1.1 atomicity: `plugin.yaml.version` 0.33.0 → 0.34.0 + `VERSION` 0.33.0 → 0.34.0 + `~/.claude/ai-sdlc-VERSION` 0.33.0 → 0.34.0 in single atomic commit per META-1 atomicity (slice-014 M1 ACCEPTED-FIXED precedent)
- [ ] CAD-1 byte-equality on `agents/critique.md` preserved through slice (slice does NOT touch agents/critique.md; bidirectional sha256 forensic capture confirms byte-equal in-repo↔installed at slice end at same hash as slice-019 ship `f34c967eaaa34413...`)
- [ ] Mini-CAD-1 byte-equality on `skills/slice/SKILL.md` — slice WILL touch this file, so the row 3 PASSING → WRITTEN-FAILING → PASSING transition pattern applies (N=10 → N=11 stable)
- [ ] Helper-extraction generalization at N=3 promotion threshold (per /critique M5 ACCEPTED-FIXED + design.md Audit 4 Option C): introduce `_extract_version_body(content: str, version: str) -> str` at `tests/methodology/test_methodology_changelog.py`; keep `_extract_v031_body` + `_extract_v033_body` as thin wrappers for backward compatibility; slice-020's 3 new entry-pin tests + 1 sibling-scoping regression test call generalized form. Slice-018 + slice-019 existing tests unchanged at call-site.
- [ ] EPGD-1 self-application: 0 of 15 prior entry-pin functions (v0.22.0..v0.33.0; v0.29.0 + v0.31.0 doublets per RPCD-1 (a)↔(b) duality = 13 singles + 2 doublets = 15 functions) touched through slice-020's NEW SECTION header insertion + narrow-scope Edit for v0.34.0 entry. Post-slice-020: 15 + 1 NEW v0.34.0 function = 16 entry-pin functions total.
- [ ] TPHD-1 self-application N=3 → N=4 stable post-codification at all 3 sub-modes — slice-020 IS canonical reference instance #4 (sub-mode (a) at /critique fix-prose harmonization if test function names change; sub-mode (b) at /critique-review fix-prose harmonization; sub-mode (c) at /build-slice Phase 0 prerequisite-check pre-flight TF-1 plan harmonization).
- [ ] SCPD-1 proactive-application: rows of shippability.md NOT touched (no Dim 9 sub-clause supersession; row 20 added at /build-slice Phase 5 BEFORE /validate-slice catalog run; SCPD-1 stays at N=3 stable)
- [ ] BFRD-1 self-application probe: slice-020 IS a NEW-feature slice (codifies a new methodology rule), not a bug-fix slice — so BFRD-1's STOP-route does NOT trigger on slice-020 itself. The discipline is exercised PROSPECTIVELY at slice-021+ on the first bug-fix slice. Document explicitly in design.md "Self-application N/A: new-feature slice".
- [ ] -D suffix convention: BFRD-1 ends in -1 with -D positioned before final integer per N=5 stable convention; rule ID stored as `BFRD-1` (capitalized) throughout
- [ ] No new TODOs / FIXMEs / debug prints in skill file or test files
- [ ] BFRD-1 prose at `skills/slice/SKILL.md` is location-pinned to the Step 3c position (between Step 3b and Step 4 anchors), NOT free-floating

## Out of scope

- `tools/bfrd_1_audit.py` standalone audit tooling — v2 candidate per ADR-018 Cost summary; deferred until N≥3 BFRD-1 violations recur post-codification (mirrors slice-016 ADR-015 + slice-017 ADR-016 audit deferrals)
- `agents/critique.md` Dim 9 10th sub-clause for BFRD-1 — BFRD-1 is a /slice skill-prose discipline, not an adversarial-prompt content discipline; first-Critic catching bug-fix slices missing repro citation at /critique time is a separate v2 candidate if N≥3 first-Critic-MISS instances of this class recur
- Modifications to `skills/repro/SKILL.md` — `/repro` itself stays unchanged; BFRD-1 only adds the prelude check to `/slice` (one-way coupling)
- Auto-detection of bug-fix candidates from the risk register's `bug-class` flag or graphify queries — v2 candidate if explicit detection-mode (b) "user/candidate-source signal" proves too coarse at slice-021+
- Open R-1 (cwd-mismatch /diagnose) + R-2 (no programmatic /diagnose warning test) — stale risks since slice-001/002; require `/repro` first (which is exactly the discipline this slice codifies; nice irony, but they stay out-of-scope here)
- Windows cp1252 console encoding workaround (N=3 cumulative at slice-019 watch-list, promotion threshold MET but separate slice scope) — separate candidate `audit-tools-default-utf8-stdout`
- Schema-enum-vs-AC-prose-mismatch + Self-application-qualifier-coherence sub-classes (slice-019 N=1 watch-list each) — promote to Dim 9 at N=3 distinct-slice recurrence

## Dependencies

- Prior slices: [[slice-017-address-tf-1-plan-staleness-discipline]] — TPHD-1 codification at 3 surfaces is the closest precedent for slice-020's 1-surface skill-prose discipline; calibration-trail conventions inherited; [[slice-019-harden-diagnose-layering-evidence]] — most recent codification slice; bidirectional sha256 + N-surface schema-pin patterns
- Vault refs: [[methodology-changelog.md]] (entry v0.34.0 target), [[architecture/decisions/ADR-018]] (NEW), [[architecture/shippability.md]] (row 20 target), [[skills/slice/SKILL.md]] (Step 3c insertion target), [[skills/repro/SKILL.md]] (referenced but not modified)
- Risk register: no entries — bug-fix-without-repro-test is a methodology-internal latent class, not a registered risk; no risk-register changes expected this slice

## Mid-slice smoke gate

At ~50% of build (after Phase 1a-1c INSERT on `skills/slice/SKILL.md` Step 3c + methodology-changelog v0.34.0 entry + ADR-018, BEFORE writing prose-pin tests):

```
<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant tests/methodology/test_critique_agent_drift.py tests/methodology/test_slice_skill_drift.py tests/methodology/test_slice_skill.py::test_slice_skill_md_bfrd_1_prelude_present -q
```

Expected: 4 PASS (PMI-1 v1.1 invariant + CAD-1 byte-equality on agents/critique.md + mini-CAD-1 byte-equality on skills/slice/SKILL.md after install-sync + BFRD-1 prelude_present per /critique M4 ACCEPTED-FIXED — catches incomplete Step 3c insertion failure mode at smoke checkpoint). If PMI-1 fails: atomic version bump 0.33.0 → 0.34.0 not yet propagated across all 3 files. If CAD-1 fails: agents/critique.md was accidentally edited (this slice should NOT touch it). If mini-CAD-1 fails: install-sync skipped after editing skills/slice/SKILL.md. If prelude_present fails: Step 3c prose was not actually inserted into in-repo SKILL.md (false-positive green-light failure mode per /critique M4 catch — slice-016 RPCD-1 sub-mode (b) NEW-status/token allowlist-audit class).

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list (12 items) fully addressed
- [ ] `tools/test_first_audit.py --strict-pre-finish` passes on mission-brief TF-1 plan (all 5 PENDING rows transitioned to PASSING + 1 mini-CAD-1 row 3 PASSING → WRITTEN-FAILING → PASSING transition + 2 invariant rows stable + 1 catalog-level row deferred to /validate-slice)
- [ ] /drift-check passes — vault claims match code reality (skills/slice/SKILL.md + methodology-changelog + ADR-018 + shippability.md + test files all consistent)
- [ ] Mid-slice smoke still passes (PMI-1 v1.1 + CAD-1 + mini-CAD-1 all green)
- [ ] No new TODOs / FIXMEs / debug prints in any modified file
- [ ] Shippability catalog 20/20 PASS at /validate-slice Step 5.5 in <2 min aggregate (row 20 added; rows 1-19 no regression)
- [ ] Bidirectional sha256 forensic capture: methodology-changelog.md + skills/slice/SKILL.md byte-equal in-repo ↔ installed at slice end (N=15 → N=16 stable); agents/critique.md unchanged at slice-019 ship hash `f34c967eaaa34413...` (CAD-1 byte-equality preserved through slice; EPGD-1 self-application empirically confirmed at validate time)
- [ ] BFRD-1 self-application N/A documented: slice-020 is a NEW-feature slice, not a bug-fix slice, so the STOP-route does NOT trigger; first prospective application at slice-021+ when a bug-fix slice surfaces
