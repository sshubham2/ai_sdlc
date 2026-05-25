# Critique Review: Slice 069 track-vault-in-git

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-25
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's 6-Blocker / 6-Major / 4-minor set is largely well-grounded — every finding I re-verified is anchored to real artifact text (B1 secrets-scan ineffectiveness; B2 PII pre-flight; B3 ADR-028 §Options-#1 rejection; B4 BC-PROJ-8 literal "gitignored" trigger keyword and fixture pin; B5 STP-1 docstring; M1 fabricated ADR-019 taxonomy citation). The Builder's 9 ACCEPTED-FIXED + 7 ACCEPTED-PENDING dispositions all land on the right side. One scope-promotion (B4) is the most expensive disposition and deserves a second look — the rule's *prescription* is still coherent post-tracking but the design.md does NOT show the *revised Check text*, leaving the BC-PROJ-8 narrowing semantically unverified. I surface **3 missed concerns** (a missed third co-tracking failure mode; a missed industry-tool-survey gap on secrets scanning; a missed test-fixture-corpus blast-radius for the PII sweep) and **1 severity-adjustment-note** (M4 throwaway-worktree verification step references the unconventional `/tmp/...` path on a Windows-PowerShell host — operationally fine but inconsistent with BRANCH-2 canonical-sibling-dir doctrine; remains Major but the verification command needs portability hardening) **plus 1 partial-suspicious direction-unverified note** (M5 code-review SKILL.md sweep — finding VALID, but Builder's proposed-fix direction "keep exclusion, reframe rationale" underclaims the architecture shift; re-open at /build-slice time).

## Confirmed findings (VALID)

All 16 first-Critic findings (B1-B6, M1-M6, m1-m4) were CONFIRMED VALID at correct severity. Each is anchored to real artifact text empirically re-verified at meta-critique time. See first Critic's `critique.md` for individual finding bodies; key VALIDATION evidence:

- **B1** — `tools/validate_slice_layers.py:85-107` defines 9 production patterns (AWS `AKIA`, GitHub `ghp_/gho_/...`, Slack `xox[baprs]`, RSA/EC/OPENSSH/DSA, Anthropic `sk-ant-`, OpenAI `sk-(proj-)?...T3BlbkFJ...`, JWT `eyJ...`, generic `api[_-]?key=`). Original hand-rolled `sk-[A-Za-z0-9]{20,}` misses the OpenAI `T3BlbkFJ` infix entirely.
- **B2** — Meta-Critic re-count: 95 unique `<HOME>\...` paths (vault grew by 2 since /critique), 9 `<github-user>` total matches; `<private-project>` private-project leak confirmed present.
- **B3** — ADR-028 file name literally contains `not-gitignored-vault`; §Options-#1 explicit rejection confirmed. Builder's partial-supersession granularity (frontmatter `supersedes: null` + prose §Supersession scope block + Option 1 revision) is the right choice.
- **B4** — `tests/methodology/fixtures/build_checks/canonical_project_checks.md:134,139,143` all literally encode `gitignored`. `tests/methodology/test_build_checks_audit.py:1582-1618` pins the literal trigger-keyword tuple including `"gitignored"`. **See B4 reservation below — design doesn't validate revised text**.
- **B5** — `tools/state_transition_pin_audit.py:28-37` literally contains `"architecture/ is gitignored so the merge-base form was inapplicable"`. `tests/methodology/test_methodology_changelog.py:3060` literally encodes `"(Sub-form B re-spec — the `architecture/`-gitignored root cause)"`. Both pins must be re-aligned in lockstep.
- **B6** — Two analyzed modes are real. **See M-add-1 below for a third unanalyzed mode**.
- **M1** — ADR-019 has no `## Reversibility taxonomy` section; citation was fabricated. Builder fix (drop + promote to ADR-066's own new §Reversibility taxonomy) reinforces the "ADR fabricates citation" failure pattern as a calibration signal.
- **M2, M3, M5, M6** — all CONFIRMED VALID at correct severity (Major).
- **M3** empirical re-count: `find architecture/ -type f | wc -l` returns **632** at meta-critique time (vault grew by 1 — slice-069's critique.md). Builder's "~631" + "loosened threshold >500 <800" remains sound.
- **m1, m2, m3, m4** — all CONFIRMED VALID at correct severity (minor).

## Suspicious findings (over-reach / direction-unverified)

**No fully-suspicious findings.** All 6 Blockers + 6 Majors + 4 minors are anchored to real artifact text; the Builder's dispositions are appropriate; no over-acceptance detected.

**One direction-unverified note** (NOT a "drop the finding" recommendation):

### M5 (code-review SKILL.md sweep promotion direction) — PARTIALLY SUSPICIOUS (direction-unverified)

- **Finding itself**: VALID — `skills/code-review/SKILL.md:66` literal exclusion rationale `"architecture/** (vault — gitignored, separate review surface via /drift-check)"` is stale post-slice-069.
- **Builder's proposed-fix direction is unverified**: "keep the exclusion, reframe as 'vault reviewed by /critique on its own slice surfaces'" UNDERCLAIMS the architecture shift. Counter-argument: post-slice-069, `architecture/slices/*/{build-log,validation,reflection}.md` are tracked production content landing in every PR diff but currently have ZERO review surface (/critique reviews `design.md` at /critique time, NOT post-build artifacts; /code-review excludes the whole vault).
- **Recommendation**: re-open during /build-slice — the right answer may be **INCLUDE** `architecture/slices/*/build-log.md` + validation.md + reflection.md in /code-review scope (post-build artifacts produced by /build-slice itself) while continuing to EXCLUDE `architecture/decisions/*.md` (reviewed by /critique) + `architecture/{lessons,risk-register,methodology-changelog,etc}.md` (reviewed by /reflect / /risk-spike / /slice on their own surfaces). Newman *Building Microservices* §15 (the change-review surface should cover EVERY tracked-then-deployed artifact).
- **Builder draft**: **ACCEPTED-PENDING** — mission-brief Must-not-defer #7 updated to re-open the scope question at /build-slice time + capture rationale either way in build-log Events.

## Missed findings (first Critic didn't surface; meta-Critic adds)

### M-add-1: BCI-1 third unanalyzed co-tracking failure mode — accidental `git rm` of tracked live file

- **Issue**: design.md §Error model + ADR-066 §Consequences analyze (a) drift+bypass corruption-on-master and (b) parallel-branch merge-conflict, but miss (c) **inadvertent `git rm` of the now-tracked live `architecture/build-checks.md`** in an unrelated future slice that touches the vault. Pre-slice-069 "absent" meant "never authored / locally corrupt" (R-4 class); post-slice-069 "absent" can also mean "git-removed by accident in commit X".
- **Evidence**: `tools/build_checks_integrity.py:40-42` HALTs with exit 1 on project-live absent (correct fail-loud) — but the recovery path differs from R-4: `git revert` of the rm commit, NOT fixture-driven reconstruction. No slice ever encountered this state pre-069.
- **Proposed fix**: Add a third sub-bullet to ADR-066 §Consequences §Co-tracking failure modes.
- **Builder draft**: **ACCEPTED-FIXED** — ADR-066 §Consequences §Co-tracking failure modes expanded from "two new BCI-1 failure modes" to "three new BCI-1 failure modes"; sub-bullet 3 added documenting the `git rm` failure mode + the BCI-1 Step-6 mitigation (rm cannot reach master without bypassing Step-6 BCI-1 explicitly — failure mode is single-slice-bounded, not master-corruption).

### M-add-2: Industry-tool survey gap — secrets-scan posture is single-pattern-set / one-shot, NOT layered-defense

- **Issue**: design.md AC#4 + ADR-066 §Decision specify a one-shot VAL-1 `_SECRET_PATTERNS` invocation at `/commit-slice --merge` time, but make no note of (a) the industry-standard 150+ patterns in `gitleaks` (vs VAL-1's 9), (b) the layered-defense pattern (pre-commit hook + CI scan + periodic full-history rescan), OR (c) the "scanner that runs only once is doing about a third of the job" anti-pattern. GitGuardian 2026 SoSS reports ~28M secrets leaked to public GitHub in 2025.
- **Evidence**: VAL-1 `_SECRET_PATTERNS` is 9 patterns; gitleaks is 150+; methodology repo's choice (one-shot VAL-1, no pre-commit framework, no `git-secrets`, no `gitleaks`) is implicit, not surfaced as a trade-off. McGraw *Software Security: Building Security In* §Touchpoint 2; OWASP ASVS V14.
- **Proposed fix**: ADR-066 §Consequences gains a 1-paragraph sub-bullet acknowledging the choice + naming the trade-off + flagging the layered-defense extension as a follow-up slice nominee.
- **Builder draft**: **ACCEPTED-FIXED** — ADR-066 §Consequences gains the §"Secrets-scanning posture is single-pattern-set / one-shot, NOT layered-defense" sub-bullet naming VAL-1's 9-pattern coverage + the gitleaks 150-pattern comparison + the 3-reason trade-off rationale (this repo is methodology source not multi-dev target; 9 patterns cover threat classes most likely in vault prose; gitleaks adoption is a separate future slice with own threat-model + dependency-add decision).

### M-add-3: PII redaction sweep blast-radius — mechanical sed will break tests outside `architecture/` if scope unpinned

- **Issue**: Empirically verified: `grep -rE 'C:[/\\]Users[/\\]sshub' tests/methodology/ | wc -l` returns **110** matches across files like `tests/methodology/fixtures/archive_backtest_corpus/slice-001-*/design.md`. These are **load-bearing tracked test fixtures** that capture historical slice content verbatim per [[ADR-030]] (archive-backtest verbatim corpus discipline). The slice's PII sweep is scoped to `architecture/` only (per AC#4 + Must-not-defer #2) — technically out-of-scope for the verbatim corpus — but the design's "iterate-if-pytest-breaks" loop is a weak hedge that ratifies a sweep operating without an explicit allowlist OR an explicit fixture-scope exclusion.
- **Evidence**: `tests/methodology/fixtures/archive_backtest_corpus/slice-001-diagnose-orchestration-fix/design.md` literally contains `- **Lives at**: \`<HOME>\ai_sdlc\skills\diagnose\write_pass.py\``. ADR-030 verbatim-corpus discipline pins these as immutable. Wiegers §Verifiability + Hendrickson exploratory-tester *Edges of the Map* (sweep blast-radius is the failure-mode no Critic catches without re-running the sweep against the actual filesystem).
- **Proposed fix**: AC#4 + Must-not-defer #2 should explicitly state "sweep scope = `architecture/**` ONLY; do NOT modify `tests/methodology/fixtures/archive_backtest_corpus/**`; iterate-if-pytest-breaks applies to in-scope `architecture/**` substitutions that incidentally break tests reading vault paths". Without this explicit scope-pin, a build-time `sed -i` over `find . -name '*.md'` would corrupt the backtest corpus.
- **Builder draft**: **ACCEPTED-FIXED** — Must-not-defer #2 rewritten to PIN sweep scope to `architecture/**` ONLY; explicit DO-NOT-modify list now includes `tests/methodology/fixtures/archive_backtest_corpus/**` (with ADR-030 verbatim contract reasoning) + all `tests/`/`tools/`/`skills/`/`agents/` paths; iterate-if-pytest-breaks scope clarified to in-scope `architecture/**` only.

## Severity adjustments

### M4 (throwaway-worktree N=4 verification step) — SEVERITY CORRECT (Major), command needs portability hardening

- **Issue**: mission-brief Must-not-defer #8 prescribed `git worktree add /tmp/slice069-verify-wt slice/069-track-vault-in-git`. The `/tmp/...` path resolves via Git for Windows MSYS to `C:\Program Files\Git\tmp` — *operationally* viable IF run from Bash tool, but **off-canonical** vs the BRANCH-2 doctrine prescribing `<main-parent>/<main-name>-wt/<slice-folder>` (per `tools/branch_workflow_audit.py:280-286`). Windows-MSYS resolution is implicit and not portable to PowerShell-native invocation.
- **Evidence**: `tools/branch_workflow_audit.py:280-286` enforces canonical sibling-dir convention for all BRANCH-2 worktrees; the throwaway-worktree at `/tmp/...` would not match the convention.
- **Proposed fix**: Keep severity Major; harden the command to use the canonical sibling-dir convention with a `-verify` suffix.
- **Builder draft**: **ACCEPTED-FIXED** — Must-not-defer #8 command swapped to `git worktree add "$env:USERPROFILE/ai_sdlc-wt/slice-069-verify" slice/069-track-vault-in-git` (PowerShell-native) OR `git worktree add ../ai_sdlc-wt/slice-069-verify slice/069-track-vault-in-git` (POSIX-portable from repo root); the off-canonical `/tmp/...` path explicitly disclaimed in revised text.

## B4 reservation (separate from missed-findings)

The first Critic's B4 (BC-PROJ-8 evergreen-rule revision) is VALID and the Builder's promotion-into-slice-069-scope disposition is the right call per Critic option (a). **However**: the design.md does NOT show the *revised* Check + Rationale + Trigger-keyword text, leaving the BC-PROJ-8 narrowing semantically unverified. The slice could ship a semantically-incoherent rule (e.g., "drops `gitignored` trigger keyword" without a coherent replacement narrative for the rule's *purpose* post-tracking).

- **Builder draft**: **ACCEPTED-FIXED** — Must-not-defer #6 (BC-PROJ-8 revision) revised to require **drafting the revised Check + Rationale + Trigger-keyword text in build-log.md Events FIRST**, BEFORE the structural-identity pin re-alignment lands. Revision-direction guidance added: BC-PROJ-8's *intent* (vault-targeting tools should prefer live-file reads over git-history for cross-machine-safety) remains coherent; the cross-machine motivation transfers from "structural impossibility" to "shallow-clone / new-contributor-pull-window reasoning" (slices touching a vault file may run against a working tree where that file's git history is partially available).

## Dimensions re-applied (independently)

- [x] **Unfounded assumptions** — first-Critic B1 (secrets-grep), B4 (BC-PROJ-8 false post-slice-069), B5 (STP-1 docstring), M1 (ADR-019 taxonomy fabricated), M3 (>1000 vs 631) all CONFIRMED. **+1 missed**: M-add-2 industry-tool gap (VAL-1 9 patterns vs gitleaks 150+ — implicit assumption of sufficiency unsurfaced).
- [x] **Missing edge cases** — first-Critic B2 (PII), B6 (co-tracking failures), M6 (operational scaling) all CONFIRMED. **+1 missed**: M-add-1 third BCI-1 failure mode (accidental `git rm` of tracked live file). **+1 missed**: M-add-3 PII sweep blast-radius outside `architecture/**` into ADR-030 verbatim corpus.
- [x] **Over-engineering** — first-Critic correctly flagged none; no addition from meta-Critic.
- [x] **Under-engineering** — first-Critic M4 (no N=4 retirement verification) + B6 sub-(b) CONFIRMED. M5 direction-unverified note added.
- [x] **Contract gaps** — first-Critic correctly noted none; no addition.
- [x] **Security** — first-Critic B1 + B2 + B6 sub-(a) CONFIRMED. M-add-2 (layered-defense gap) adds a trade-off-naming concern.
- [x] **Drift from vault** — first-Critic B3 (ADR-028 supersession), B4 (BC-PROJ-8), B5 (STP-1), M5 (4 stale skill-prose surfaces) CONFIRMED. No additional drift surfaces missed.
- [x] **Web-known issues** — first-Critic honestly skipped this dimension; meta-Critic adds M-add-2 (industry secrets-scanning baselines: gitleaks 150+ patterns + layered defense; GitGuardian 2026 SoSS) as a web-search-informed missed concern.
- [x] **Cross-cutting conformance** — first-Critic CONFIRMED on RPCD-1 (B1 fix), FBCD-1 (M5 sibling-sweep), BC-1 / VAL-1 / SUP-1 surfaces. M-add-3 surfaces a new cross-cutting concern: ADR-030 verbatim-corpus discipline interacts with PII sweep scope.

## Sources consulted (per WebSearch budget)

- [Gitleaks: Open-Source Secret Scanning for Git Repos in 2026](https://dev.to/pickuma/gitleaks-open-source-secret-scanning-for-git-repos-in-2026-4ceb)
- [GitHub - gitleaks/gitleaks](https://github.com/gitleaks/gitleaks)
- [GitGuardian 2026 State of Secrets Sprawl](https://snyk.io/articles/state-of-secrets/)
- [Git Security — Pre-Commit Hooks, Secret Detection, Credential Safety](https://tutorialq.com/dev/git/git-security-secrets-detection)

## Triage feed (for /critique Step 4.5 TRI-1)

| ID | Severity | Source | Status |
|----|----------|--------|--------|
| B1–B6 + M1–M6 + m1–m4 | as filed | first-Critic | All CONFIRMED VALID at original severity; Builder dispositions all sound (9 ACCEPTED-FIXED + 7 ACCEPTED-PENDING) |
| M-add-1 | Major | /critique-review | ACCEPTED-FIXED in-band (ADR-066 §Consequences §Co-tracking failure modes 3rd sub-bullet added) |
| M-add-2 | Major | /critique-review | ACCEPTED-FIXED in-band (ADR-066 §Consequences §Secrets-scanning posture sub-bullet added) |
| M-add-3 | Blocker | /critique-review | ACCEPTED-FIXED in-band (mission-brief Must-not-defer #2 sweep scope explicitly pinned to `architecture/**` only with ADR-030 verbatim-corpus exclusion) |
| M4 severity-note | Major (unchanged) | /critique-review | ACCEPTED-FIXED in-band (Must-not-defer #8 command swapped to canonical BRANCH-2 sibling-dir path) |
| M5 direction-unverified | Major (unchanged) | /critique-review | ACCEPTED-PENDING (Must-not-defer #7 revised to re-open INCLUDE-vs-keep-exclusion scope question at /build-slice time) |
| B4 reservation | Blocker (unchanged) | /critique-review | ACCEPTED-FIXED in-band (Must-not-defer #6 expanded to require drafting revised BC-PROJ-8 text in build-log.md Events FIRST, before pin re-alignment) |
