# Critique: Slice 069 track-vault-in-git

**Critic reviewed**: mission-brief.md, design.md, ADR-066
**Date**: 2026-05-25
**Result**: NEEDS-FIXES (post-Builder-fix-block; 9 ACCEPTED-FIXED in-band + 7 ACCEPTED-PENDING for /build-slice; 0 OVERRIDDEN / DEFERRED / ESCALATED; meta-Critic EXTEND verdict added 4 more dispositions: M-add-1 + M-add-2 + M-add-3 ACCEPTED-FIXED in-band, M5 direction-unverified ACCEPTED-PENDING, M4 severity-note + B4 reservation ACCEPTED-FIXED in-band)

## Summary

Design-Critic returned BLOCKED with 6 Blockers + 6 Majors + 4 minors. Empirical verification at /critique time confirmed both load-bearing factual claims (B1 hand-rolled secrets-grep matches ZERO of VAL-1's 9 real secret patterns; B2 reveals 93 unique absolute-path leaks including an unrelated private project name `<private-project>`). Builder fix-block applied 9 ACCEPTED-FIXED edits to ADR-066 + mission-brief + design.md in-band (ADR-028 partial supersession added per B3, reversibility taxonomy promoted per M1, co-tracking failure modes + operational scaling sub-bullets added per B6/M6, Option 4 cons reordered per m3, frontmatter title shortened per m1, AC#4 verification fixed per m2, smoke gate Bash-tool note + 631-count fix per M2/M3). 7 findings are ACCEPTED-PENDING for /build-slice scope expansion: B2 (PII redaction sweep), B4 (BC-PROJ-8 evergreen-rule revision — promoted into slice-069 scope), B5 (STP-1 docstring stale-rationale sweep), M4 (throwaway-worktree N=4 retirement verification), M5 (`skills/code-review/SKILL.md:66` exclusion-rationale sweep — promoted into slice-069 scope), m4 (`/critic-calibrate` probe narrowing). MEPD-1 posture revised from EXCLUDE to **INCLUDE** post-B4 promotion (BC-PROJ-8 trigger-keyword set narrows = enforcement boundary shifts); PMI-1 5-part atomic v0.69.0 → v0.70.0 bump added to scope. Original effort estimate revised 0.5d → ~1d.

## Findings

### Blockers (must address before /build-slice)

#### B1: Pre-commit secrets-scan grep pattern is ineffective; empirically matches zero of VAL-1's nine production secret classes
- **Claim under review**: mission-brief.md AC #4 + Must-not-defer #1: hand-rolled `grep -rn -E 'api[_-]?key=[A-Za-z0-9]|password\s*=\s*[A-Za-z0-9]|sk-[A-Za-z0-9]{20,}' architecture/` is the secrets-scan gate
- **Issue**: empirically tested at /critique time against 4 real secret shapes (AWS, GitHub PAT, api_key colon-form, Anthropic sk-ant-) → ALL returned NO MATCH (exit=1). The gate's protection against ADR-066's named "effectively-irreversible" failure mode is illusory.
- **Evidence**: `tools/validate_slice_layers.py:85-107` has the 9 canonical secret patterns; the slice's hand-rolled pattern is dramatically weaker. Empirical Bash test at /critique time confirmed 0/4 real shapes matched.
- **Proposed fix**: Replace AC #4 + Must-not-defer #1 grep with explicit VAL-1 invocation: `$PY -c "from tools.validate_slice_layers import _SECRET_PATTERNS; ..."`.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief AC #4 + Must-not-defer #1 rewritten in-band to invoke `tools/validate_slice_layers.py` `_SECRET_PATTERNS` (all 9 patterns) via Python wrapper; Verification plan row 4 updated.

#### B2: 125 absolute Windows paths to user's home tree (`<HOME>\...`) will be permanently committed to public git history; ADR-066's Consequences/Reversibility doesn't mitigate
- **Claim under review**: mission-brief.md AC #4 + Must-not-defer #1; ADR-066 §Decision §Pre-commit secrets scan claim that the pre-flight grep is sufficient
- **Issue**: Critic correctly identified PII class entirely uncovered by the proposed grep. Empirical verification at /critique time: 93 unique absolute paths in `architecture/`, INCLUDING `<HOME>/<private-project>` (unrelated private project), `<github-user>` GitHub-handle references (3), and worktree-layout paths `ai_sdlc-wt/slice-068-...`. None caught by the original grep.
- **Evidence**: Empirical `grep -rohE 'C:[/\\]Users[/\\]sshub[^ "\`<>]+' architecture/ | sort -u | wc -l → 93`; head of unique-paths list shows `<private-project>` private leak.
- **Proposed fix**: Add mandatory must-not-defer PII redaction sweep before initial vault commit; mechanically substitute `<HOME>\` → `<HOME>\` and `<github-user>` → `<github-user>`, re-verify pytest baseline.
- **Builder draft**: **ACCEPTED-PENDING** — added as must-not-defer item #2 in mission-brief.md; PII redaction sweep at /build-slice time, with iterate-if-pytest-breaks loop. Adds ~0.2d to scope.

#### B3: ADR-066 fails to cite, supersede, or even acknowledge ADR-028's explicit prior REJECTION of un-gitignoring the vault as Option 1
- **Claim under review**: ADR-066 §Options-considered (5 options, ADR-028 not mentioned); ADR-066 §Supersedes: implicit "nothing"
- **Issue**: ADR-028 (slice-030A) explicitly REJECTED un-gitignoring the vault as Option 1 with rationale `"deliberate .gitignore:11; scoped out"`. ADR-066 now chooses exactly that rejected option but does NOT cite ADR-028. SUP-1 violation per CLAUDE.md "ADRs are append-only — supersede via a new ADR with `supersedes: ADR-NNN`".
- **Evidence**: `architecture/decisions/ADR-028-bc1-tests-assert-tracked-fixture-not-gitignored-vault.md:21` literal `"1. Un-gitignore the vault — rejected (deliberate .gitignore:11; scoped out)."`. ADR-066 frontmatter `supersedes:` was absent.
- **Proposed fix**: ADR-066 §Options-#1 revised to acknowledge ADR-028's rejection + reframe as scope-limited deferral now addressable on its own merits; frontmatter adds `supersedes: null` with prose supersession block explaining partial scope-supersession of ADR-028 §Options-#1 only.
- **Builder draft**: **ACCEPTED-FIXED** — ADR-066 frontmatter + introductory supersession-scope block + §Options §Option 1 (revised) all added in-band. ADR-028's BCI-1 core (Decisions 1-3) remains accepted unchanged; only §Options-#1 partial scope-supersession.

#### B4: BC-PROJ-8's `Check` text becomes factually false at slice-069 ship time; the fixture + literal-constant oracle + 12 test pins all encode the now-falsified "gitignored" premise
- **Claim under review**: design.md §Sites EXCLUDED bullet 6 (defers all "Local-only/gitignored" prose to slice-070)
- **Issue**: BC-PROJ-8 is NOT historical-state prose — it is a live, enforced, evergreen BC-1 rule with trigger keyword `gitignored` and a Check text that asserts the vault is structurally invisible to git. Once slice-069 ships, the Check is factually false and the trigger-keyword set continues firing on now-irrelevant slice prose. Pinned by ~12 references in `tests/methodology/test_build_checks_audit.py`.
- **Evidence**: `tests/methodology/fixtures/build_checks/canonical_project_checks.md:134-147` (BC-PROJ-8 body); `tests/methodology/test_build_checks_audit.py::test_bc_proj_8_has_expected_structural_identity` (the literal tuple pin). Severity confirmed `Important` (not `Critical` as Critic prompt asserted — minor Critic inaccuracy, finding validity unaffected).
- **Proposed fix**: Critic option (a): promote BC-PROJ-8 revision into slice-069 scope (+0.25d). Revise Check + Rationale + Trigger-keywords on live + fixture; re-align ~12 test pins; add methodology-changelog supersession note.
- **Builder draft**: **ACCEPTED-PENDING** — promoted into slice-069 scope per Critic option (a). Mission-brief must-not-defer item added; design.md What's new + §Sites EXCLUDED updated; MEPD-1 posture revised EXCLUDE → INCLUDE due to enforcement-boundary shift; PMI-1 5-part atomic v0.69.0 → v0.70.0 bump added.

#### B5: STP-1 Sub-form B's design rationale becomes false; the audit's docstring explicitly cites the gitignored fact as the root cause for the git-independent design
- **Claim under review**: design.md §What's reused doesn't mention `tools/state_transition_pin_audit.py` or its docstring rationale
- **Issue**: `tools/state_transition_pin_audit.py:28-37` Sub-form B docstring asserts `"architecture/ is gitignored so the merge-base form was inapplicable"` as the design rationale. Post-slice-069 the rationale is false. Future readers reasoning from the docstring would use a stale premise.
- **Evidence**: literal docstring quote in the tool source; `tests/methodology/test_methodology_changelog.py:3060` contains the methodology-changelog entry-pin asserting the gitignored root cause.
- **Proposed fix**: Sweep docstring + methodology-changelog entry pin to reframe Sub-form B's git-independent-standing-invariant choice as a *preference* (post-tracked-vault — fewer git-subprocess calls + works on shallow clones) rather than a *necessity*.
- **Builder draft**: **ACCEPTED-PENDING** — added as must-not-defer item; design.md What's new updated; ADR-066 §Consequences sub-bullet added describing the STP-1 sweep obligation as in-band fix.

#### B6: AC #5 + Must-not-defer #4's claim "BCI-1 gate continues to pass" is asserted but not verified, and the new failure mode "live file modified mid-slice via tracked-edit" is unanalyzed
- **Claim under review**: ADR-066 §Decision §"BCI-1 contract preserved" treats co-tracking as strictly beneficial; design.md §Error model doesn't analyze new failure modes
- **Issue**: Co-tracking introduces (a) corruption-on-master window if `/reflect` Step 5b drifts the live file AND BCI-1 is bypassed (e.g., `--no-verify`); (b) parallel-branch merge-conflict on machine-generated build-checks.md when two slices both invoke `/reflect` Step 5b. Pre-slice-069 these were impossible.
- **Evidence**: slice-029 validation.md §R-4 incident attributed recovery difficulty to the gitignored status (`"no in-repo history; canonical anchor spec lives in tracked test_build_checks_audit.py + archived slice-005/008/012 reflections"`). Slice-069 inverts that posture and the inversion is unanalyzed.
- **Proposed fix**: Add explicit §Consequences sub-bullet analyzing both new failure modes + their mitigations (BCI-1 stays a Step-6 non-opt-out gate; corruption-on-master requires DOUBLE failure, strictly stricter than pre-slice-069 single-failure path; parallel-branch conflict has mechanical canonical-fixture-driven resolution).
- **Builder draft**: **ACCEPTED-FIXED** — ADR-066 §Consequences gains a new 2-sub-bullet block analyzing both modes with explicit mitigations.

### Majors (address this slice)

#### M1: ADR-066 §Reversibility cites an "ADR-019 reversibility taxonomy" that does not exist
- **Claim under review**: ADR-066 §Reversibility's final paragraph cites a non-existent ADR-019 taxonomy
- **Issue**: ADR-019 has no `## Reversibility taxonomy` section; the 3-class definitions (cheap = <1 hr; expensive = downstream coordination cost; irreversible = destroys data) are fabricated prose attributed to a source that doesn't support the citation. Wiegers traceability defect.
- **Evidence**: `grep -n "taxonomy\|<1 hr" architecture/decisions/ADR-019-branch-per-slice-workflow.md` returns 0 hits.
- **Proposed fix**: Drop the citation; promote the inline 3-class definitions to a new `## Reversibility taxonomy` section in ADR-066 itself so subsequent ADRs can cite forward.
- **Builder draft**: **ACCEPTED-FIXED** — ADR-066 §Reversibility paragraph rewritten to drop ADR-019 attribution; new `## Reversibility taxonomy` section added below §Reversibility with the 3-class definitions + worked examples (ADR-013 cheap; this ADR expensive; primary-entity-shape irreversible). Closing note explicitly disclaims the originally-fabricated ADR-019 citation.

#### M2: Mid-slice smoke gate uses POSIX commands on a Windows Powershell-preferred environment without specifying the Bash tool
- **Claim under review**: mission-brief.md §Mid-slice smoke gate uses `wc -l`, `find ... -type d`, `head -5`
- **Issue**: User's CLAUDE.md prefers PowerShell on Windows; the smoke block silently relies on Git for Windows MSYS-bash. Slice-067/068 BRANCH-2 lineage already demonstrated Windows-vs-POSIX surprises.
- **Evidence**: mission-brief.md §Mid-slice smoke gate command block; CLAUDE.md user-global §Shell preference.
- **Proposed fix**: Prefix the block with "Run via the Bash tool" annotation.
- **Builder draft**: **ACCEPTED-FIXED** — annotation added: "Run via the Bash tool (POSIX commands ... Git for Windows MSYS provides them; do NOT run in PowerShell)".

#### M3: Mid-slice smoke gate's `git add -n architecture/ | wc -l` expected ">1000" is unjustified and likely wrong
- **Claim under review**: mission-brief.md §Mid-slice smoke gate expected "> 1000"
- **Issue**: Empirical vault file count is 631. The Builder would see ~631 lines and either STOP at a false alarm or silently revise the threshold.
- **Evidence**: `find architecture/ -type f | wc -l → 631`.
- **Proposed fix**: Replace with empirical "~631" + loosened "> 500 < 800" threshold + the at-/critique-time verification footprint.
- **Builder draft**: **ACCEPTED-FIXED** — count updated to "~631" with empirical confirmation comment + "loosened threshold: >500 < 800 is sane" added.

#### M4: Must-not-defer item "Document the N=4 worktree-vs-gitignored class STRUCTURAL retirement in reflection" lacks an acceptance signal
- **Claim under review**: mission-brief.md Must-not-defer #6 (original numbering — now #11 post-fix-block): structural retirement asserted without verification
- **Issue**: The slice asserts structural retirement but provides no verification that the next BRANCH-2 worktree-add will actually propagate the vault. The slice itself has a unique opportunity to verify this empirically before reflection.
- **Evidence**: Aggregated lessons §"N=4 cumulative gitignored-vault-vs-worktree conflict" calls for structural verification, not assertion.
- **Proposed fix**: Add must-not-defer verification step: create throwaway worktree at slice-069 build time, confirm vault propagates, then remove worktree.
- **Builder draft**: **ACCEPTED-PENDING** — added as must-not-defer item "N=4 retirement empirical verification" with explicit throwaway-worktree create + ls + remove sequence + validation.md capture obligation.

#### M5: Out-of-scope deferral of the 73-file / ~480-occurrence prose sweep to slice-070 leaves stale "gitignored" claims in 4 active skill-prose surfaces
- **Claim under review**: mission-brief.md §Out of scope defers the prose sweep to slice-070 indefinitely
- **Issue**: `skills/code-review/SKILL.md:66` is the most-active stale-prose surface — it explicitly excludes `architecture/**` from /code-review BECAUSE gitignored. Post-slice-069 the exclusion is unmotivated and the now-tracked vault content silently bypasses /code-review.
- **Evidence**: `skills/code-review/SKILL.md:66` literal text; the other 3 surfaces (build-slice, validate-slice, reflect) are softer.
- **Proposed fix**: Critic option (b): promote the highest-leverage surface (`skills/code-review/SKILL.md:66`) into slice-069 scope (~0.05d); defer the other 3 to slice-070.
- **Builder draft**: **ACCEPTED-PENDING** — promoted `skills/code-review/SKILL.md:66` into slice-069 scope per Critic option (b); other 3 surfaces remain in design.md §Sites EXCLUDED for slice-070; mission-brief must-not-defer + design.md What's new updated.

#### M6: Massive single-commit interaction with `/commit-slice --merge` is unanalyzed
- **Claim under review**: design.md §What's new notes the commit size but doesn't analyze scaling
- **Issue**: 3 unanalyzed scaling concerns: (a) commit-message generation context-window; (b) `/commit-slice` pre-flight audits' first encounter with tracked `architecture/`; (c) `git merge --no-ff` of 631 files into master timing + BRANCH-2 worktree-remove order.
- **Evidence**: ADR-020 (BRANCH-1 sub-mode (b)) commit-message generation flow; no operational-scaling sub-bullet in ADR-066 §Consequences.
- **Proposed fix**: Add explicit pre-`--merge` dry-run as must-not-defer; ADR-066 §Consequences sub-bullet on the operational scaling.
- **Builder draft**: **ACCEPTED-FIXED** — ADR-066 §Consequences gains a new sub-bullet on operational scaling; mission-brief must-not-defer "Pre-`/commit-slice --merge` dry-run" item added.

### Minors (log; address if cheap)

#### m1: ADR-066's frontmatter `title` field is unreadably long (~280 chars)
- **Builder draft**: **ACCEPTED-FIXED** — title shortened to "Track the AI SDLC vault (`architecture/`) in git (retire N=4 worktree-vs-gitignored class; supersedes ADR-028 §Options-#1 partial scope-out)"; full descriptive form preserved in the H1.

#### m2: AC #4 "git diff --cached --stat | tail -1 shows +1MB+ added" doesn't match `git diff --stat` output format
- **Builder draft**: **ACCEPTED-FIXED** — AC #4 verification command updated to expect "~631 files changed and >100000 insertions(+)" matching the actual `git diff --stat` format; "+1MB+" framing removed.

#### m3: ADR-066 §Options-considered §Option 4 (submodule) rejection rationale ordered operational-first vs architectural-first
- **Builder draft**: **ACCEPTED-FIXED** — Option 4 cons reordered: dogfood-premise-break leads, operational complexity follows as secondary support.

#### m4: Slice asserts the `/critic-calibrate` probe is retired but doesn't capture the probe narrowing in reflection-discovery
- **Builder draft**: **ACCEPTED-PENDING** — added as must-not-defer item at /reflect time: update aggregated-lessons probe scope from `architecture/` to `diagnose-out/` + `graphify-out/`.

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (secrets-grep ineffective), B4 (BC-PROJ-8 false post-slice-069), B5 (STP-1 docstring stale), M1 (ADR-019 taxonomy fabricated), M3 (>1000 vs empirical 631) — 5 findings ALL VALIDATED + ACCEPTED.
- [x] **Missing edge cases** — B2 (PII / absolute-path leak class), B6 (co-tracking corruption-on-master + merge-conflict), M6 (operational scaling) — 3 findings ALL VALIDATED.
- [x] **Over-engineering** — none.
- [x] **Under-engineering** — M4 (no empirical verification of N=4 retirement), B6 sub-(b) (AC #5 BCI-1 claim under-engineered re new-failure-mode analysis) — 2 findings VALIDATED.
- [x] **Contract gaps** — none.
- [x] **Security** — B1 (secrets-scan broken), B2 (PII leak), B6 sub-(a) (corruption-on-master window) — 3 findings VALIDATED.
- [x] **Drift from vault** — B3 (ADR-028 supersession gap), B4 (BC-PROJ-8 evergreen rule), B5 (STP-1 docstring), M5 (4 stale skill-prose surfaces) — 4 findings VALIDATED.
- [x] **Web-known issues** — none (honest skip per Critic; no novel external tech).
- [x] **Cross-cutting conformance** — VAL-1 / BC-1 / SUP-1 / RSAD-1 / SCMD-1 surfaces all engaged via above findings; gitignore-precedence claim verified empirically (no finding); RPCD-1 surfaces engaged via B1 fix; FBCD-1 surfaces engaged via M5 fix-block enumeration discipline.

## Triage

**Triaged by**: user
**Date**: 2026-05-25
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | mission-brief AC #4 + Must-not-defer #1 rewritten to invoke `tools/validate_slice_layers.py` `_SECRET_PATTERNS` (9 patterns) via Python wrapper; ADR-066 §Decision + §Consequences updated |
| B2 | Blocker | ACCEPTED-PENDING | mission-brief Must-not-defer #2 PII redaction sweep at /build-slice (scope pinned to `architecture/**` per meta-Critic M-add-3) |
| B3 | Blocker | ACCEPTED-FIXED | ADR-066 frontmatter `supersedes: null` + §Supersession scope block + §Options §Option 1 revised to acknowledge ADR-028 §Options-#1 partial scope-supersession |
| B4 | Blocker | ACCEPTED-PENDING | mission-brief Must-not-defer #6 BC-PROJ-8 revision PROMOTED into slice-069 scope; revised Check + Rationale + Trigger-keyword text drafted in build-log.md FIRST (per meta-Critic B4 reservation), then live + fixture + ~12 test pins re-aligned |
| B5 | Blocker | ACCEPTED-PENDING | mission-brief Must-not-defer #7 STP-1 docstring sweep PROMOTED into slice-069 scope; methodology-changelog entry pin re-aligned alongside |
| B6 | Blocker | ACCEPTED-FIXED | ADR-066 §Consequences §"Co-tracking introduces three new BCI-1 failure modes" sub-bullet block added (expanded from two to three modes per meta-Critic M-add-1) |
| M1 | Major | ACCEPTED-FIXED | ADR-066 §Reversibility citation dropped; new §Reversibility taxonomy section added (3 classes with worked examples + disclaimer of fabricated ADR-019 citation) |
| M2 | Major | ACCEPTED-FIXED | mission-brief §Mid-slice smoke gate prefixed with "Run via the Bash tool" annotation |
| M3 | Major | ACCEPTED-FIXED | mission-brief §Mid-slice smoke gate count revised to "~631" with empirical confirmation + loosened threshold (>500 <800) |
| M4 | Major | ACCEPTED-PENDING | mission-brief Must-not-defer #8 throwaway-worktree N=4 verification at /build-slice; command swapped to canonical BRANCH-2 sibling-dir per meta-Critic M4 severity-note |
| M5 | Major | ACCEPTED-PENDING | mission-brief Must-not-defer #7 `skills/code-review/SKILL.md:66` exclusion-rationale PROMOTED into slice-069 scope; direction (keep-exclusion vs INCLUDE-build-log-artifacts) re-opened at /build-slice per meta-Critic M5 direction-unverified flag |
| M6 | Major | ACCEPTED-FIXED | ADR-066 §Consequences §"Operational scaling of the largest commit in repo history" sub-bullet added; mission-brief Must-not-defer #10 pre-`--merge` dry-run added |
| m1 | minor | ACCEPTED-FIXED | ADR-066 frontmatter title shortened to "Track the AI SDLC vault (`architecture/`) in git (retire N=4 worktree-vs-gitignored class; supersedes ADR-028 §Options-#1 partial scope-out)"; full descriptive form preserved in H1 |
| m2 | minor | ACCEPTED-FIXED | mission-brief AC #4 verification command updated to "~631 files changed and >100000 insertions(+)" matching actual `git diff --stat` output format |
| m3 | minor | ACCEPTED-FIXED | ADR-066 §Options-considered §Option 4 (submodule) cons reordered: dogfood-premise lead, operational complexity secondary |
| m4 | minor | ACCEPTED-PENDING | mission-brief Must-not-defer #11 `/critic-calibrate` probe narrowing note at /reflect time |
| M-add-1 | Major | ACCEPTED-FIXED | ADR-066 §Consequences §Co-tracking failure modes expanded from 2 to 3 modes; 3rd sub-bullet documents accidental `git rm` of tracked live file + BCI-1 Step-6 mitigation |
| M-add-2 | Major | ACCEPTED-FIXED | ADR-066 §Consequences §"Secrets-scanning posture is single-pattern-set / one-shot, NOT layered-defense" sub-bullet added; VAL-1 9 patterns vs gitleaks 150+ trade-off named + 3-reason rationale for slice-069's choice |
| M-add-3 | Blocker | ACCEPTED-FIXED | mission-brief Must-not-defer #2 PII sweep scope explicitly pinned to `architecture/**` ONLY; ADR-030 verbatim-corpus exclusion enumerated + 110-match `tests/methodology/fixtures/archive_backtest_corpus/` explicitly preserved unchanged |
| B4-reservation | Blocker | ACCEPTED-FIXED | mission-brief Must-not-defer #6 expanded: draft revised BC-PROJ-8 Check + Rationale + Trigger-keyword text in build-log.md Events FIRST (before pin re-alignment); revision-direction guidance added (cross-machine motivation transfers from "structural impossibility" to "shallow-clone reasoning") |
| PMI-1-v0.70.0 | (scope addition) | ACCEPTED-PENDING | mission-brief Must-not-defer #12 PMI-1 5-part atomic v0.69.0 → v0.70.0 bump (consequence of MEPD-1 INCLUDE flip per B4 promotion); 5 surfaces + v0.70.0 body entry |
