# Slice 074: codify-cp-r-in-branch-2-skill

**Mode**: Standard
**Estimated work**: ~1-2 hours (SMALL — single-surface prose addition + structural-pin test + R-20 status flip + OSDG-1 sync)
**Risk retired**: R-20 (`mitigating` → `retired`) — gitignored `diagnose-out/` + `graphify-out/` cp -r tax at every BRANCH-2 slice (N=8 cumulative across two surfaces; "SEVERELY OVERDUE" per slice-073 reflection L28, L38)
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Operationalize R-20 candidate fix (a) — codify the `cp -r ../<main>/diagnose-out ../<main>/graphify-out ./` step into `skills/build-slice/SKILL.md` `## Prerequisite check ### Branch state` sub-section, immediately after `cd "$wt_base/slice-NNN-<slice-name>"`. Removes the "I forgot to cp" per-slice failure mode at /build-slice prerequisite check; structurally retires the cp -r tax that has surfaced at every post-vault-in-git BRANCH-2 slice since slice-067 (N=8 cumulative). Cheapest of the four R-20 candidate fix classes: pure prose addition + a structural-pin test + a risk-register status flip. Why now: slice-073 reflection promoted R-20 from "carried-forward observation" to "severely overdue at N=8, each subsequent slice adds cumulative pain." Doing nothing means slice-075 will be N=9.

## Acceptance criteria

1. `skills/build-slice/SKILL.md` `## Prerequisite check ### Branch state` sub-section contains `cp -r` invocations for `diagnose-out/` AND `graphify-out/`, placed AFTER the `cd "$wt_base/slice-NNN-<slice-name>"` line and BEFORE the numbered point 2 ("If the worktree already exists"), with reference to risk-register R-20 (e.g., a `# Seed gitignored derived dirs from main tree (R-20)` comment) so future readers can trace the codification's origin.
2. The codified cp -r prose handles source-dir-absence gracefully — uses the set-e-safe `if [ -d "$repo_root/<dir>" ]; then cp -r "$repo_root/<dir>" ./; fi` POSIX guard (per /critique m3 — the `&&` chained form leaks exit-status 1 on guard-skip and would fail loudly under future `set -e` hardening; `if/then/fi` is exit-status-neutral on the false branch) so a fresh project that has never run `/diagnose` or `graphify code` does NOT fail at /build-slice prerequisite check; structural-pin test asserts the `if [ -d ... ]; then cp -r` guard literal is present on each `cp -r` line.
3. OSDG-1 forward-sync verified post-edit: installed `~/.claude/skills/build-slice/SKILL.md` content-equal modulo line endings to in-repo copy; `tests/methodology/test_build_slice_skill_drift.py` PASSES against the new prose.
4. R-20 status flipped `mitigating` → `retired` in `architecture/risk-register.md`; `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status retired` includes R-20 in its output; the retiring slice cited as `slice-074-codify-cp-r-in-branch-2-skill`.

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0): each AC maps to one or more failing tests written BEFORE the SKILL.md / risk-register edits. Statuses progress PENDING → WRITTEN-FAILING → PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | structural-pin | tests/methodology/test_build_slice_skill_cp_r_step.py | test_branch_state_subsection_contains_cp_r_for_diagnose_out_and_graphify_out_after_cd | PENDING |
| 1 | structural-pin | tests/methodology/test_build_slice_skill_cp_r_step.py | test_cp_r_lines_reference_r_20_in_comment | PENDING |
| 2 | structural-pin | tests/methodology/test_build_slice_skill_cp_r_step.py | test_cp_r_lines_use_if_then_guard_for_source_dir_absence | PENDING |
| 3 | drift (existing class) | tests/methodology/test_build_slice_skill_drift.py | test_build_slice_skill_md_in_repo_byte_equal_installed | PASSING-AFTER-SYNC |
| 4 | structural-pin | tests/methodology/test_r_20_retired.py | test_r_20_status_is_retired_in_risk_register | PENDING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | cp -r prose codified | Run `tests/methodology/test_build_slice_skill_cp_r_step.py::test_branch_state_subsection_contains_cp_r_for_diagnose_out_and_graphify_out_after_cd` + `..._references_r_20_in_comment` — both must PASS. Additionally, `grep -A 20 '^### Branch state' skills/build-slice/SKILL.md \| grep -E '\bcp -r\b.*(diagnose-out\|graphify-out)' \| wc -l` reports ≥2. |
| 2 | source-dir-absence handled | Run `tests/methodology/test_build_slice_skill_cp_r_step.py::test_cp_r_lines_use_if_then_guard_for_source_dir_absence` — must PASS. Cross-check: `grep -E 'if \[ -d.*\]; then cp -r' skills/build-slice/SKILL.md` finds both occurrences. |
| 3 | OSDG-1 sync clean | After `cp skills/build-slice/SKILL.md "$env:USERPROFILE\.claude\skills\build-slice\SKILL.md"`, run `$PY -m pytest tests/methodology/test_build_slice_skill_drift.py -v` — expect 1 PASS. |
| 4 | R-20 retired | Run `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status retired \| Select-String 'R-20'` — match present. Also `$PY -m pytest tests/methodology/test_r_20_retired.py -v` — expect 1 PASS. |

## Must-not-defer

- [ ] Codified `cp -r` step is **idempotent** (re-running on existing worktree overwrites cleanly — confirmed by POSIX `cp -r` semantics; no extra `--update` or `--no-clobber` flags needed because derived artifacts are regeneratable).
- [ ] **Recursive self-application — BOOTSTRAP exception** (per /critique M1 ACCEPTED-FIXED, mirroring CRP-1 / ADR-024 slice-026 bootstrap exception precedent): slice-074 is the BOOTSTRAP instance. At slice-074's own Phase A prerequisite check, `/build-slice` reads the INSTALLED `~/.claude/skills/build-slice/SKILL.md` which is still the pre-slice (v0.72.0) prose — the codified `if [ -d ... ]; then cp -r ...; fi` step does NOT yet exist in Claude's reading. The cp -r that runs at slice-074 Phase A is the same MANUAL cp -r that has run at slices 067-073 (R-20 N=8). The OSDG-1 forward-sync (Phase B/C) propagates the codification to the installed copy AFTER prereq check has already passed. **Canonical first-governed-slice (N+1) demonstration is slice-075's /build-slice Phase A** — the build-log Events line documenting `if/then/fi cp -r` running from the codified SKILL.md prose lives at slice-075, not slice-074. Slice-074's discharge of recursive-self-application is: (a) OSDG-1 forward-sync at Phase B/C lands the prose in the installed copy; (b) the 3 structural-pin tests PASS against the in-repo SKILL.md; (c) the manual Phase A cp -r still works as it has for slices 067-073.
- [ ] Mid-slice smoke gate (~50% of build) verifies the structural-pin test ASSERTIONS match the SKILL.md prose byte-for-byte (no whitespace-stripping mismatch; cf. slice-071 M6 sentinel-test docstring/assertion verbatim mismatch class — RSAD-1 prevention).
- [ ] Windows compatibility verified — `cp -r` works under Git for Windows MSYS bash per the existing SKILL.md L62 convention; structural-pin test asserts the POSIX `cp -r` literal (NOT PowerShell `Copy-Item -Recurse`) so the codification stays consistent with the surrounding shell-bash prose.
- [ ] OSDG-1 forward-sync runs in the SAME slice (not deferred) — installed copy MUST land via `cp skills/build-slice/SKILL.md "$env:USERPROFILE\.claude\skills\build-slice\SKILL.md"` before /commit-slice; AVFS-1 / MCFS-1 / TVFS-1 audits all pass.

## Out of scope

- **R-20 candidate (b) symlink discipline** — Windows junction/symlink fragility per slice-066 critique-review B2 lineage; cross-platform symlink-creation requires elevated privileges on Windows pre-Developer-Mode. Deferred unless the codified cp -r approach later proves inadequate.
- **R-20 candidate (c) un-gitignore `graphify-out/` + `diagnose-out/`** — violates derived-artifacts-shouldn't-be-tracked principle (~5-15MB churn per `/diagnose` run; environment-dependent graph state). ADR-066 vault-in-git philosophy explicitly excludes derived artifacts.
- **R-20 candidate (d) audit gate that auto-runs cp -r** — escalation reserved for the case where the codified-prose approach surfaces N≥3 additional "I forgot to read the SKILL.md" failures. The codified prose with explicit graceful-absence guards is sufficient unless empirical use refutes it.
- **Changes to `/commit-slice` Step 5b worktree-teardown** — worktree-remove already removes the cp-r'd dirs cleanly; no asymmetric teardown step needed.
- **Audit module to ENFORCE the cp -r ran on disk** — Phase E mid-slice smoke gate ALREADY catches a missing-diagnose-out/-graphify-out via existing BCR-1 test failures (e.g., slice-071 surfaced this exact way); structural codification at /build-slice prerequisite is the structural fix.
- **Extending the codification to other gitignored-derived directories beyond `diagnose-out/` + `graphify-out/`** — these are the only two surfaced in R-20's N=8 cumulative observations; adding speculative directories now would violate slice-022 "codify exactly what reality has demanded" pattern.
- **Retroactive cp -r in BRANCH-1 fallback path** — BRANCH-1 single-tree-only path doesn't have a worktree-vs-main-tree gap; cp -r is moot there.

## Dependencies

- Prior slices:
  - [[slice-066-add-worktree-per-slice-discipline]] — minted BRANCH-2 / ADR-063; provides the `## Prerequisite check ### Branch state` sub-section being amended.
  - [[slice-069-track-vault-in-git]] — minted ADR-066 vault-in-git philosophy; established the derived-artifacts-stay-gitignored principle that R-20 documents and that this slice operationalizes within.
  - [[slice-071-bundle-066-to-070-code-critic-cleanup]] — promoted R-20 from recurring-class observation (N=6) to risk-register tracked entry with 4 candidate fix classes.
  - [[slice-073-add-rebase-and-conflict-discipline]] — R-20 N=8 cumulative; "SEVERELY OVERDUE" nomination text (reflection L28, L38).
- Vault refs:
  - [[architecture/risk-register#R-20]] — the cp-r tax risk this slice retires.
  - [[architecture/decisions/ADR-063]] — BRANCH-2 contract being extended.
  - [[architecture/decisions/ADR-066]] — vault-in-git philosophy that constrains the fix to candidate (a) over (c).
  - [[skills/build-slice/SKILL.md#Branch state]] — surface being amended.
- Risk register:
  - [[risk-register#R-20]] — `mitigating` → `retired` is AC#4.

## Mid-slice smoke gate

At ~50% of build (after TF-1 Phase A RED tests authored + Phase B SKILL.md prose edit landed, BEFORE Phase C OSDG-1 sync + R-20 status flip):

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m pytest tests/methodology/test_build_slice_skill_cp_r_step.py -v
```

Expected: 3 PASS (the 3 cp-r-related structural-pin tests). If any FAIL: STOP, inspect SKILL.md prose vs test assertions for byte-level mismatch (whitespace, comment-marker drift, regex-vs-literal substring). Do not proceed to Phase C until all 3 PASS — the canonical RSAD-1 prevention pattern from slice-071 M6.

Additionally, demonstrate the codified cp -r step actually works in a real worktree context — Phase A's /build-slice prerequisite check for slice-074 itself ran the codified step (recursive self-application per slice-022 law); the build-log Events line documents this with a timestamp + cwd context.

## Pre-finish gate

- [ ] All 4 acceptance criteria PASS with evidence in validation.md
- [ ] All 5 must-not-defer items addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression in the 3 cp-r structural-pin tests)
- [ ] OSDG-1 audit on `build-slice` SKILL.md clean post-sync (no CRLF/LF false-positives; EOL-agnostic per ADR-033)
- [ ] BC-1 Step 6 audit run; any false-positives documented as defer-with-rationale per N=5 cumulative BC-GLOBAL-2 prose-vs-automation class (slice-073 reflection L29)
- [ ] PMI-1 audit clean — **MEPD-1 EXCLUDE is the chosen stance** per design.md §"MEPD-1 stance: EXCLUDE" (post-/design-slice decision; ships at v0.72.0 unchanged; no PMI-1 bump; no BC-PROJ-10 paired-pin obligation; no shippability row #74). (Contingency: if /critique re-opens the EXCLUDE choice and demands INCLUDE — verdict not BLOCKED, but a Major demanding stance reversal — fall back to the 5-part atomic bump 0.72.0 → 0.73.0 + BC-PROJ-10 paired-pin path; m2 ACCEPTED-FIXED at /critique demoted this branch to a frozen contingency.)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Full pytest **>= 995/995 PASS** post-slice (slice-073 baseline was 995/995; this slice adds ~4 new tests → expect ~999/999 PASS)
- [ ] Shippability runner clean (post-row-add if MEPD-1 INCLUDE; otherwise 73/73 PASS unchanged)
