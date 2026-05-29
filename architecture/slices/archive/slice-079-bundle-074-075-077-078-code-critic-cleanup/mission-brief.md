# Slice 079: bundle-074-075-077-078-code-critic-cleanup

**Mode**: Standard
**Estimated work**: 1.5 days (MEDIUM-LARGE; bumped from "1 day" per /critique m5 ACCEPTED-FIXED — 16 new/extended tests across 12-14 files + 6 SKILL.md prose edits with OSDG-1 lock-step sync + parameterized tests for 8 UNKNOWN reasons + synthetic git fixtures for bare-repo + structural-pin AST walker for UTF-8 encoding realistically lands ~8-12 hours of focused work; slice-071's 31-finding precedent confirms 19-finding bundled scope is mid-range viable but only with realistic effort estimate)
**Risk retired**: voluntary-restraint deferrals N=18 cumulative (slice-074 m1–m5 + slice-075 m1–m2 + slice-077 13 code-Critic findings + slice-078 m1–m5 + P1.1 build-slice point-4 variable-scope footgun + P3.10 `tools/slice_queue_writer.py` cp1252 mojibake)
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Bundled clearance of accumulated code-Critic v1 advisory findings from slices 074, 075, 077, 078 (N=18 cumulative voluntary-restraint deferrals). No new methodology axis is opened; every change is a surgical fix to existing methodology surfaces (`skills/build-slice/SKILL.md`, `skills/commit-slice/SKILL.md`, `skills/pulse/SKILL.md`, `tools/slice_queue_writer.py`) with a regression test pinning the fix. Lands BEFORE slice-080's LARGE PCR-2b work so PCR-2b inherits a clean baseline. Codified bundled-cleanup-at-N+1 pattern (precedent: slice-038, slice-046, slice-071) extended to N+4-slice fan-in.

## Acceptance criteria

1. Slice-074 code-Critic findings m1–m5 each have a fix landed + regression test (the test FAILs on pre-fix, PASSEs on post-fix) catalogued in `architecture/shippability.md`.
2. Slice-075 code-Critic findings m1–m2 each have a fix landed + regression test catalogued in `architecture/shippability.md`.
3. Slice-077 12 actionable code-Critic findings (m11 is positive observation per slice-077 code-review.md L117, NOT counted; per /critique m4 ACCEPTED-FIXED) each have a fix landed + regression test (or a documented "DEFER with rationale" for any finding determined non-actionable, with the rationale captured in design.md §"Decisions made (deferrals)" audit trail).
4. Slice-078 code-Critic findings m1–m5 each have a fix landed + regression test catalogued in `architecture/shippability.md`.
5. `source-pending-items.txt` entries P1.1 + P3.10 each have a fix or honest reframe landed + regression test; both entries' current text removed from `source-pending-items.txt`. P1.1 (build-slice Phase E point-4 variable-scope footgun — variable accidentally leaks out of conditional branch) ships full fix per Fix A. P3.10 (`tools/slice_queue_writer.py` mojibake) reframed per /critique B2+M3 ACCEPTED-FIXED: empirical APED-1 verification at /critique time demonstrated the helper is already UTF-8 explicit at all 9 encoded-I/O sites; Slice-079 ships a structural-pin regression-guard test (Fix S — asserts no encoded-I/O site lacks `encoding=` kwarg; FAIL→PASS contrast via fixture-mutation); the actual mojibake-source-finding work routes to a future slice as new source-pending entry P3.10' `find-real-mojibake-source` (likely upstream — `tools/slice_pick.py` subprocess invocations / `PYTHONIOENCODING` env defaults / `/slice` skill's own subprocess invocation).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | slice-074 m1–m5 cleared | Each finding ID has a paired commit hash + a `tests/methodology/test_bundle_079_slice_074_<finding-id>.py` (or co-located equivalent) in `architecture/shippability.md`; `$PY -m pytest tests/methodology -k "slice_074"` PASSES. |
| 2 | slice-075 m1–m2 cleared | Same shape; `$PY -m pytest tests/methodology -k "slice_075"` PASSES. |
| 3 | slice-077 13 findings cleared | Each finding has either a fix+test OR a DEFER-rationale row in design.md's cleanup catalog; cleared findings show FAIL→PASS contrast on pre/post-fix. |
| 4 | slice-078 m1–m5 cleared | Same shape; `$PY -m pytest tests/methodology -k "slice_078"` PASSES. |
| 5 | P1.1 + P3.10 cleared | `source-pending-items.txt` no longer contains either current-text entry; regression tests pin both: P1.1 — structural-pin against `skills/build-slice/SKILL.md` Phase E point-4 asserting variable assignments live in shared pre-amble outside any numbered point's codefence (Fix A). P3.10 — structural-pin against `tools/slice_queue_writer.py` asserting every `Path.{read,write}_text` / `open()` / `subprocess.run(text=True, ...)` call carries `encoding="utf-8"` kwarg (Fix S structural-pin; AST walker; FAIL→PASS contrast via fixture-mutation per design.md §Test plan row S). P3.10' (mojibake-source root-cause investigation) routed to source-pending as a NEW separate entry for a future slice. |

## Must-not-defer

- [ ] Regression test for EVERY fixed finding (FAIL→PASS contrast) catalogued in `architecture/shippability.md` with a new row per cluster (per RPCD-1 / SCPD-1).
- [ ] `tools/slice_queue_writer.py` UTF-8 structural-pin regression-guard (REFRAMED per /critique B2+M3 ACCEPTED-FIXED): empirical APED-1 verification at /critique time confirmed all 9 encoded-I/O sites in the helper already carry `encoding="utf-8"`; slice-079 adds a structural-pin AST-walker test that asserts no future regression deletes the kwarg from any site; the actual mojibake-source root-cause work is routed to a new source-pending entry P3.10' `find-real-mojibake-source` for a future slice. UTF8-STDOUT-1 audit clean.
- [ ] OSDG-1 forward-sync in lock-step: any `skills/*/SKILL.md` edit also updated at `~/.claude/skills/*/SKILL.md` in the same fix block; mini-CAD drift audits CLEAN.
- [ ] PMI-1 + INST-1 + CAD-1 + BCI-1 + STP-1 audits CLEAN at `/build-slice` pre-finish.
- [ ] PCA-1 chain audit CLEAN — no new auto-advance gates added inadvertently.
- [ ] BC-PROJ-4 discipline applied to EVERY audit affected by an edited SKILL.md: run the audit on the real post-fix artifact at pre-finish and read its output (not just pytest exit code).
- [ ] No new RULE-IDs minted; no new methodology-changelog entries; this is a no-VERSION-bump conformance / cleanup-discharge class per MEPD-1(b) (precedent: slice-040, slice-043, slice-045, slice-057). Why-none MUST be verified against the actual META-1 enforcing assertion at `tests/methodology/test_methodology_changelog.py:136`.

## Out of scope

- Slice-079 does NOT mint new methodology rules, ADRs, or methodology-changelog entries (conformance / cleanup-discharge class; precedent slice-040/043/045/057).
- PCR-2b HARD-conflict Critic stack — slice-080+ candidate (queue #1 post-079).
- SP-1 slice-pick auto-pick via /slice no-arg — slice-080+ candidate (queue #2).
- parallel-slice-family-parity-audit, close-psq-3, add-psq-4, bcr-1-dual-tree-replication, cross-worktree-race-hardening — all deferred queue candidates.
- Any finding determined non-actionable after on-the-ground investigation may be DEFERRED with rationale captured in design.md's cleanup catalog; deferral preserves the finding's audit trail and routes it to slice-080+'s code-Critic backlog.

## Dependencies

- Prior slices: [[slice-074-codify-cp-r-in-branch-2-skill]] + [[slice-075-close-merge-substep-3-worktree-collision]] + [[slice-077-enhance-pulse-with-worktree-awareness]] + [[slice-078-add-pcr-2a-vault-claim-resolver]] — source slices whose code-Critic findings are being cleared.
- Vault refs: [[skills/build-slice/SKILL.md]], [[skills/commit-slice/SKILL.md]], [[skills/pulse/SKILL.md]], [[tools/slice_queue_writer.py]], [[architecture/shippability.md]], [[source-pending-items.txt]]
- Risk register: no R-NN retirement (voluntary-restraint deferrals are tracked via aggregated lessons N=18 cumulative, not via risk-register entries).
- Precedent: bundled-cleanup-at-N+1 pattern from [[slice-038]], [[slice-046]], [[slice-071-bundle-066-to-070-code-critic-cleanup]]; no-VERSION-bump conformance class from [[slice-040]], [[slice-043]], [[slice-045-fix-install-pypi-package-name-and-stale-prose]], [[slice-057-retire-r15-via-slice-034-resolve-slice-dir-retrofit]].

## Mid-slice smoke gate

At ~50% of build (after slice-074 + slice-075 + half of slice-077 findings landed), run:

```
$PY -m pytest tests/methodology -x
$PY -m tools.shippability_runner architecture/shippability.md
```

Expected: full methodology suite PASSES; shippability runner reports all rows including newly-added bundled-cleanup rows PASS; no regressions in `tests/methodology/` baseline. If FAILS: STOP, diagnose, don't continue to slice-078 findings (root-cause the regression first; bundled work amplifies pre-existing bugs).

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with per-finding evidence catalogued in `validation.md`
- [ ] Must-not-defer list fully addressed (regression tests for each + UTF-8 explicit + OSDG-1 lock-step sync + PMI-1/INST-1/CAD-1/BCI-1/STP-1 audits CLEAN + BC-PROJ-4 discipline applied + no new RULE-IDs minted)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression introduced by later-phase work)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] `tools/branch_workflow_audit.py` BRANCH-2 audit CLEAN (worktree-mode discipline at Step 6)
- [ ] `tools/new_agent_warning_audit.py` NAW-1 audit CLEAN
- [ ] Full pytest suite PASSES (slice-078 baseline 1072/1072; slice-079 expected = 1072 + N where N = sum of regression tests added; report exact count)
- [ ] MEPD-1(b) discharge documented in design.md "Decisions made" — why-none verified by name against the META-1 `^## v…`-split assertion at `tests/methodology/test_methodology_changelog.py:136` (precedent: slice-040/043/045/057)
