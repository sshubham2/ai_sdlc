# Code Review: Slice 069 track-vault-in-git

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths per slice-069's own M5 INCLUDE direction with the `:(glob)` pathspec-magic fix applied in-band)
**Date**: 2026-05-25
**Result**: FINDINGS (0B / 2M / 6m — advisory only per CRSI-1 v1 walking-skeleton; auto-advancing to /validate-slice)

## Summary

Eleven files in scope (post-fix; 10 pre-fix due to the `:(glob)`-magic-required pathspec bug the slice discovered + fixed mid-/code-review). 644 files in the wider vault-tracking flip. The substantive code/prose deltas are coherent and the slice's load-bearing self-discovered defect (M5 INCLUDE `:(exclude)architecture/*.md` → `:(glob,exclude)architecture/*.md`) was caught + fixed in-band before the code-Critic spawn.

Two **Major** findings on inconsistencies the dual-Critic stack and Step 6 audits structurally cannot reach:
1. **M1** — `_SECRET_PATTERNS` count is consistently mis-stated as **9** across the methodology-changelog v0.70.0 entry, ADR-066, and mission-brief AC4 — actual count in `tools/validate_slice_layers.py:85-107` is **10** (the slice's own build-log Phase G evidence at L70 correctly records "10 patterns"; the prose surfaces drifted).
2. **M2** — the slice declares MEPD-1 **INCLUDE** posture but ships **no** `test_v_0_70_0_*` paired entry-pin tests AND **no** `architecture/shippability.md` row 69 — breaking the BC-PROJ-10 paired-pin discipline that every prior INCLUDE-posture slice (slice-067 / slice-066 / slice-058 / slice-052) has shipped. BC-PROJ-10's own keyword-match classifier did not catch this (the classifier audits trigger-prose, not paired-pin existence).

Six minors on numeric drift (file counts / PII-redaction counts), changelog-prose density, `.gitignore` comment placement, build-log Phase H4 worktree-pattern codification, and an emergent M5-INCLUDE-enlarged BC-1 false-positive surface (build-log §Discovered #3 prose itself could re-trigger BC-GLOBAL-2 keyword-match on future scans).

Per CRSI-1 v1 walking-skeleton advisory-only discipline + the slice-064/065/066/067/068 N=5 cumulative voluntary-restraint precedent: **all findings deferred to slice-070+ bundled cleanup nomination**, not applied in-band. The bundled-cleanup backlog now accumulates: slice-066's 6 advisories + slice-067's 1 advisory + slice-068's 4 advisories + slice-069's 8 advisories = 19-finding backlog (or split: slice-068's SC-028 backlog still pending + slice-069 fresh nominations).

## Changed files (in-scope)

```
.gitignore
VERSION
architecture/slices/slice-069-track-vault-in-git/build-log.md
methodology-changelog.md
plugin.yaml
pyproject.toml
skills/code-review/SKILL.md
tests/methodology/fixtures/build_checks/canonical_project_checks.md
tests/methodology/test_build_checks_audit.py
tests/skills/code_review/test_code_review_skill.py
tools/state_transition_pin_audit.py
```

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None. The slice's load-bearing pieces (`.gitignore` flip, ADR-066, PMI-1 5-part atomic bump, BC-PROJ-8 lockstep revision live↔fixture, STP-1 docstring reframing, M5 INCLUDE SKILL.md surgical exclusions with the post-discovery `:(glob)` fix, OSDG-1 mini-CAD content-equality preserved, BCI-1 invariant preserved on BC-PROJ-8 H2 stanza) are all internally consistent and verified against working tree / installed copies / git mechanics.

### Majors

#### M1: `_SECRET_PATTERNS` is mis-counted as "9 patterns" across the methodology-changelog v0.70.0 entry, ADR-066 §Decision, and mission-brief AC4 — actual count is 10
- **Claim under review**: `methodology-changelog.md:45` "VAL-1 canonical secrets-scan via `tools/validate_slice_layers.py` `_SECRET_PATTERNS` (9 production patterns: AWS, GitHub PAT, Slack, JWT, RSA, Anthropic, OpenAI, generic-api-key, BEGIN-PRIVATE-KEY)" — and matching strings in `architecture/decisions/ADR-066-track-vault-in-git.md:49` ("9 production patterns") and `architecture/slices/slice-069-track-vault-in-git/mission-brief.md:19` ("9 production secret patterns") and the same ADR-066 line 59 ("9 VAL-1 patterns cover the threat classes most likely").
- **Issue**: `tools/validate_slice_layers.py:85-107` enumerates **10 distinct keys** in the `_SECRET_PATTERNS` dict: `aws-access-key`, `github-token-classic`, `github-token-fine`, `github-token-other`, `slack-token`, `private-key`, `anthropic-key`, `openai-key`, `jwt`, `generic-api-key`. The methodology-changelog's nine-item list elides the 3 distinct GitHub-token shapes ("GitHub PAT" stands for all three) AND collapses `private-key`-vs-`BEGIN-PRIVATE-KEY` listings. The slice's own build-log Phase G L70 correctly records "0 hits across all **10** patterns" — so the empirical run was 10-pattern but every drafted prose surface says 9. Cousin of slice-050's BC-PROJ-9 INSTALL.md inventory-count class: a count drift no audit catches, surfaced only by hand-count.
- **Evidence**: `tools/validate_slice_layers.py:85-107` shows 10 entries; build-log L70 says "0 hits across all **10** patterns"; ADR-066/mission-brief/changelog all say "9".
- **Proposed fix**: Update three sites in lockstep at slice-070+ bundled cleanup time: `methodology-changelog.md:45` (`9 production patterns` → `10`); `architecture/decisions/ADR-066-track-vault-in-git.md:49` + `:59`; `architecture/slices/slice-069-track-vault-in-git/mission-brief.md:19` and `:34`. The build-log L70 evidence is already correct; the prose surfaces need to follow.
- **Disposition**: DEFERRED to slice-070+ bundled cleanup nomination per CRSI-1 v1 walking-skeleton advisory-only discipline + slice-064-068 N=5 cumulative voluntary-restraint precedent. Note for /reflect §Discovered: this is the slice-050 BC-PROJ-9-class inventory-count drift recurring (N=2 cumulative — promote to /critic-calibrate watch-list).

#### M2: Slice declares MEPD-1 INCLUDE posture but ships no `test_v_0_70_0_*` entry-pin tests and no `architecture/shippability.md` row 69 — breaking the BC-PROJ-10 paired-pin discipline that this very repo's evergreen rule enforces
- **Claim under review**: `architecture/slices/slice-069-track-vault-in-git/design.md:102-116` (MEPD-1 Inclusion-heuristic posture: INCLUDE; 2-of-5 YES → INCLUDE) + methodology-changelog.md L39 ("MEPD-1 posture: **INCLUDE**") + mission-brief Must-not-defer #12 ("PMI-1 5-part atomic version bump v0.69.0 → v0.70.0").
- **Issue**: Per `architecture/build-checks.md` BC-PROJ-10, *every* slice that mints a new ADR OR adds a user-facing skill capability MUST carry "the conventional `test_v_0_NN_0_*_entry_present_in_repo` + `*_shippability_consumer_propagation` test pair." Slice-069 ships ADR-066 (new ADR) + a Step 1 SKILL.md M5 INCLUDE direction (user-facing scope expansion of /code-review's diff scope) + a BC-PROJ-8 rule-content supersession (existing-rule enforcement-boundary shift) — textbook BC-PROJ-10 trigger. Prior INCLUDE-posture slices (slice-067 v0.69.0 PSQ-1, slice-066 v0.68.0 BRANCH-2, slice-058 v0.62.0 BFRD-1) each carry both pinned tests AND a shippability row. Slice-069 carries neither. `grep -n "test_v_0_70_0" tests/methodology/test_methodology_changelog.py` returns nothing; `grep -nE "^\| 69 \|" architecture/shippability.md` returns nothing.
- **Evidence**: `tests/methodology/test_methodology_changelog.py:4305-4681` shows the v0.67.0 / v0.68.0 / v0.69.0 paired-pin precedent — each version carries `test_v_0_NN_0_*_entry_present_in_repo` AND `test_v_0_NN_0_*_shippability_consumer_propagation`. No `test_v_0_70_0_*` function exists. `architecture/shippability.md:77,78` show row 67 (slice-067) + row 68 (slice-068). No row 69. The slice's own design.md MEPD-1 row 4 says "Does it introduce a new test invariant pinning a methodology rule? NO (re-aligned existing pins, not new)" — but this conflates two distinct discriminations. BC-PROJ-10's paired-pin obligation is an additive *per-INCLUDE-posture-bump* discipline, NOT a "new test invariant" judgment.
- **Proposed fix**: At slice-070+ bundled cleanup: add `test_v_0_70_0_adr_066_entry_present_in_repo` + `test_v_0_70_0_adr_066_shippability_consumer_propagation` to `tests/methodology/test_methodology_changelog.py` (modeled on the v0.69.0 entry-pin pair). Add a `| 69 |` row to `architecture/shippability.md` enumerating ADR-066 + BC-PROJ-8 revision + STP-1 docstring + M5 INCLUDE direction with the canonical 6-column shape (pipe-free per BC-PROJ-7).
- **Disposition**: DEFERRED to slice-070+ bundled cleanup nomination. This is RSAD-1-class: BC-PROJ-10's own keyword-match classifier did not catch the missing paired-pin tests — the classifier audits trigger-prose, not paired-pin EXISTENCE. /critic-calibrate watch-list candidate (N=1 on the BC-PROJ-10 keyword-vs-existence gap).

### Minors

#### m1: Numeric drift on `architecture/` vault file count across artifacts
- **Claim under review**: mission-brief.md:17,19 ("~631 files"); design.md:14,48 ("~631 files"); ADR-066:17 ("hundreds of files"); methodology-changelog.md:45 ("~633 files"); build-log.md Phase E ("634 lines"); actual `find architecture/ -type f | wc -l` = 634.
- **Issue**: 631 / 633 / 634 inconsistency across artifacts — not load-bearing (mission-brief uses `~` qualifier; mid-slice smoke gate threshold is `>500 <800`), but the methodology-changelog v0.70.0 entry has "~633 files" while the build-log evidence is "634"; the cached-diff stat at Phase H2 is "644 files / 65504 insertions" (distinct count — pre-merge stat includes the slice's own folder + edits).
- **Proposed fix**: Reconcile at slice-070+ bundled cleanup; use the actual `git diff --cached --stat` figures from build-log Phase H2 as canonical.
- **Disposition**: DEFERRED to slice-070+ bundle.

#### m2: PII redaction count divergence across artifacts
- **Claim under review**: design.md:14 ("93 unique absolute paths, 3 GitHub-handle references"); methodology-changelog.md:66 ("113 unique absolute paths, 9 GitHub-handle refs, 1 private-project-name leak"); build-log.md Phase C ("36 files / 141 substitutions").
- **Issue**: Pre-/critique counts (93/95) diverge from changelog v0.70.0 entry counts (113/9/1) and build-log Phase C empirical figures (136 + 5 = 141). Sources: pre-flight vs post-redact vs different-pattern counting. The slice's actual remediation is sound (verified via post-sweep grep returning 0); the documentation drifts.
- **Proposed fix**: Reconcile changelog v0.70.0 PII-count narrative to build-log Phase C empirical figures at slice-070+ bundle, OR add a build-log Events line documenting the source of the 113/9/1 counts.
- **Disposition**: DEFERRED to slice-070+ bundle.

#### m3: methodology-changelog v0.70.0 entry's first paragraph is a 600+ word multi-clause blob mixing 4 conceptually distinct items
- **Claim under review**: methodology-changelog.md:39 — the v0.70.0 entry's first-paragraph format mixes 4 conceptually distinct items (vault-in-git + BC-PROJ-8 narrows + STP-1 docstring + M5 INCLUDE) into one continuous prose blob.
- **Issue**: Prior entries (slice-068 v0.68.0 BRANCH-2, slice-067 v0.69.0 PSQ-1, slice-058 v0.62.0 BFRD-1) all open with a single tight headline-style paragraph naming one primary rule + a parenthetical lineage note. Slice-069's bundle of 4 distinct changes degrades grep-anchorability for any of the 4 sub-items.
- **Proposed fix**: Split into primary-narrative sentence + 3 sub-bullets in the existing **Primary deliverables** section.
- **Disposition**: DEFERRED to slice-070+ bundle. /critic-calibrate watch-list candidate (changelog-entry-density discipline).

#### m4: `.gitignore` comment block at lines 10-13 forward-references the `# Build artifacts` block at lines 15-19
- **Claim under review**: `.gitignore:10-13` comment block ends with "remain ignored below" forward-reference to lines 18-19; those rules also have their own "# Build artifacts" header at line 15.
- **Issue**: Two comment blocks both comment on (or near) the build-artifact rules. Not a defect — both accurate — but creates a small readability seam.
- **Proposed fix**: Either drop the forward-reference clause OR merge the two comment blocks. Optional minor.
- **Disposition**: DEFERRED to slice-070+ bundle.

#### m5: Build-log Phase H4 N=4 verification command pattern (`--detach HEAD`) not codified for future slices
- **Claim under review**: build-log.md Phase H4 — implementation deviated from mission-brief's `git worktree add ../slice-069-verify slice/069-track-vault-in-git` to `git worktree add --detach ../slice-069-verify HEAD` because the slice branch was already checked out elsewhere.
- **Issue**: The future-slice copy of this discipline needs the `--detach HEAD` pattern, NOT the mission-brief's `<branch>` pattern. Build-log preserves the discovery for handoff but discipline-codifying surfaces (`tools/branch_workflow_audit.py` docstring, BRANCH-2 entry in methodology-changelog) don't mention it.
- **Proposed fix**: Add `--detach HEAD` pattern as documented sub-case in `tools/branch_workflow_audit.py` docstring OR the v0.70.0 changelog body.
- **Disposition**: DEFERRED to slice-070+ bundle. /reflect handoff candidate.

#### m6: M5 INCLUDE direction enlarges the BC-1 false-positive class surface — build-log §Discovered #3 prose itself could re-trigger BC-GLOBAL-2 on future scans
- **Claim under review**: build-log §Discovered #3 records "BC-GLOBAL-2 fires on ADR §Reversibility prose mentioning `git checkout`/`git restore`/`git stash`" — the build-log itself now carries these literals in its prose discussion.
- **Issue**: A future slice that touches this build-log.md (e.g., /reflect Step 5 propagation, or any slice's BC-1 application scoped to slices/*/build-log.md) could see BC-GLOBAL-2 fire on this discovery-note prose. Emergent surface created by M5 INCLUDE admitting build-log.md to /code-review scope.
- **Proposed fix**: None this slice — already a /critic-calibrate watch-list candidate per build-log §Discovered #3. Track at N=3 cumulative.
- **Disposition**: ACKNOWLEDGED as Dim 9 cross-cutting note; no fix needed.

## Dimensions checked

- [x] **Unfounded assumptions** — M1 (`_SECRET_PATTERNS` 9 vs 10 mis-claim across 3+ artifacts is a textbook unfounded-assumption defect per Wiegers — the claim "9 patterns" traces to no evidence and contradicts the actual `dict` enumeration in `tools/validate_slice_layers.py:85-107`)
- [x] **Missing edge cases** — none in this dimension (configuration / content-commit / philosophy-ADR slice; the `:(glob)` pathspec fix was the slice's own self-discovered edge case caught + fixed in-band)
- [x] **Over-engineering** — none (this slice REMOVES code surface via `.gitignore` 1-line deletion + M5 INCLUDE direction is surgical 10-exclusions-per-leg vs prior catch-all; no speculative-generality introduced)
- [x] **Under-engineering** — M2 (slice declares MEPD-1 INCLUDE posture and ships the 5-part PMI-1 atomic bump but does NOT ship the BC-PROJ-10 paired entry-pin tests + shippability row that every prior INCLUDE-posture slice has shipped — under-engineering per Wiegers AC-to-deliverable traceability law)
- [x] **Contract gaps** — none. The slice introduces no new APIs / endpoints / events / schemas (per design.md §"Contracts added or changed" explicit "none"). Function signatures preserved across STP-1's docstring-only revision (verified via `git diff` of `tools/state_transition_pin_audit.py`).
- [x] **Security** — none (OWASP Top 10 applied to slice's diff: vault-tracking flip with VAL-1 secrets-scan gate at must-not-defer; gate ran clean per build-log L70; PII-redaction sweep scoped to `architecture/**` only per /critique-review M-add-3; verbatim corpus per ADR-030 preserved). Secret-exposure-surface reframing in ADR-066 §Consequences is documented + bounded, not hidden.
- [x] **Drift from vault** — m4 (`.gitignore` comment-block placement nit) + m1 (numeric file-count drift across artifacts). No load-bearing drift between code and slice's own design.md / ADR-066.
- [x] **Web-known issues** — none discovered (the slice's `:(glob,exclude)architecture/*.md` fix is consistent with [git-scm.com/docs/gitglossary](https://git-scm.com/docs/gitglossary) documentation that default pathspec uses fnmatch *without* FNM_PATHNAME so `*` crosses `/`, and `:(glob)` adds FNM_PATHNAME to scope `*` to single segment).
- [x] **Cross-cutting conformance** — M2 (RSAD-1: slice ships a BC-PROJ-10 paired-pin trigger but does not pre-satisfy the BC-PROJ-10 paired-pin obligation; BC-PROJ-10 itself would catch if it had a hard structural-existence check on `test_v_0_NN_0_*_entry_present_in_repo`). EOL-DRIFT-1: no new byte-equality `.md` compare introduced; CRLF-normalization preserved on OSDG-1 mini-CAD pin. Phantom-import: none — `_M5_INCLUDE_EXCLUSIONS` references string literals only. Algorithm-path-conformance: M5 INCLUDE 10 surgical excludes across 3 union legs are leg-consistent (verified via diff). Tooling-doc-vs-impl parity: `tests/methodology/test_build_checks_audit.py::test_bc_proj_8_has_expected_structural_identity:1612-1614` 6-tuple matches live `architecture/build-checks.md:139` + canonical fixture `:140` verbatim.

## Sources consulted

- [Git — gitglossary Documentation](https://git-scm.com/docs/gitglossary)
- [Intro to Git's pathspec](https://kgrz.io/git-intro-to-pathspec.html)
- [Git Pathspecs and How to Use Them — CSS-Tricks](https://css-tricks.com/git-pathspecs-and-how-to-use-them/)
