# Design: Slice 069 track-vault-in-git

**Date**: 2026-05-25
**Mode**: Standard

## What's new

- `.gitignore` — line 10 comment + line 11 `architecture/` rule revised: remove the `architecture/` ignore line; rewrite the line-10 comment to describe the new tracked discipline (e.g., "AI SDLC vault — tracked in git per ADR-066 to enable cross-machine parallel slice development"). Lines 16-17 (`graphify-out/`, `diagnose-out/`) UNCHANGED in this slice — only `architecture/` becomes tracked.
- `CLAUDE.md` — prose update where it asserts gitignored-ness as load-bearing. Empirical grep this slice: `CLAUDE.md` contains zero `Local-only` / `never tracked` matches; line 5 `**Vault**: \`architecture/\`` is neutral and is retained as-is. The substantive update lands in `.gitignore` line 10 comment; the CLAUDE.md side is a no-op confirmation (zero edit). AC3 verification uses `grep -n 'Local-only\|never tracked' CLAUDE.md` returning empty as the proof.
- `architecture/decisions/ADR-066-track-vault-in-git.md` — NEW philosophy ADR documenting the vault-in-git decision. Frontmatter: `id: ADR-066`, `slice: slice-069-track-vault-in-git`, `reversibility: expensive`, `status: accepted`, `supersedes: null` (with prose supersession of [[ADR-028]] §Options-#1 partial scope-out, per /critique B3 ACCEPTED-FIXED). Six standard sections (Context, Options considered (5 options, Option 1 revised to acknowledge ADR-028 §Options-#1 rejection), Decision, Consequences (8 sub-bullets including 2 new co-tracking-failure-mode + operational-scaling sub-bullets per /critique B6/M6 ACCEPTED-FIXED), Reversibility, **Reversibility taxonomy** (NEW section per /critique M1 ACCEPTED-FIXED — promotes the inline 3-class framework so subsequent ADRs can cite it; replaces the originally-fabricated "ADR-019 reversibility taxonomy" citation)). References [[ADR-028]] (BCI-1 vault-fixture-oracle — partial scope-supersession of its Option-1 rejection), [[ADR-029]] (BCI-1 deterministic gate — preserved unchanged), [[ADR-063]] (BRANCH-2 worktree-per-slice — the discipline whose N=4 recurring tax this slice retires), [[ADR-065]] (`VAULT_ROOT` constant seam — the slice-068 prereq that makes the rename-half of slice-070 tractable as a 1-line `_DEFAULT` flip).
- **BC-PROJ-8 evergreen-rule revision** (per /critique B4 ACCEPTED-PENDING — promoted into slice-069 scope): the rule's `Check` text literally asserts the vault is gitignored as the structural-impossibility premise; once slice-069 ships, that premise is false. Revise `Check` + `Rationale` + `Trigger keywords` (drop `"gitignored"`) on BOTH live `architecture/build-checks.md` AND canonical fixture `tests/methodology/fixtures/build_checks/canonical_project_checks.md`; sweep ~12 literal-constant pin references in `tests/methodology/test_build_checks_audit.py::test_bc_proj_8_has_expected_structural_identity` + integrity tests; add methodology-changelog **v0.70.0** supersession sub-bullet (rule-content revision shifts BC-PROJ-8's enforcement boundary by narrowing the trigger-keyword set — drops `gitignored` — triggering MEPD-1 **INCLUDE** posture per §MEPD-1 Inclusion-heuristic table below). The rule's *intent* (vault-targeting tools should prefer live-file reads over git-history reads for cross-machine-safety reasons) remains coherent; only the structural-impossibility framing changes.
- **STP-1 docstring stale-rationale revision** (per /critique B5 ACCEPTED-PENDING — promoted into slice-069 scope): revise `tools/state_transition_pin_audit.py:28-37` Sub-form B docstring to reframe the git-independent-standing-invariant choice as a *preference* (post-tracked-vault — fewer git-subprocess calls + works on shallow clones) rather than a *necessity* (pre-tracked-vault rationale: "architecture/ is gitignored so the merge-base form was inapplicable"); re-align methodology-changelog entry pin at `tests/methodology/test_methodology_changelog.py:3060`.
- **`skills/code-review/SKILL.md:66` `architecture/**` exclusion rationale sweep** (per /critique M5 ACCEPTED-PENDING — promoted into slice-069 scope as the highest-leverage stale-prose surface): revise exclusion rationale from `"gitignored, separate review surface via /drift-check"` to a rationale matching the new tracked-vault posture (likely: "vault content is reviewed by /critique on its own slice surfaces — design.md, ADRs, reflections — not by /code-review which scopes to executable code under tools/, tests/, skills/, agents/"); re-align skill-drift test pins at `tests/skills/code_review/test_code_review_skill.py`.
- **PII redaction sweep across `architecture/`** (per /critique B2 ACCEPTED-PENDING): mechanically substitute `<HOME>\` → `<HOME>\` (or platform-agnostic `~/`) and `<github-user>` → `<github-user>` across vault content; empirical pre-flight count: 93 unique absolute paths INCLUDING the unrelated private-project leak `<HOME>/<private-project>`, 3 `<github-user>` GitHub-handle references, several `ai_sdlc-wt/...` worktree-layout leaks. Re-verify pytest 944 baseline preserved post-redact (some redact substitutions may break load-bearing path references in test fixtures; iterate).
- **Massive content commit** of `architecture/` tree (~11MB, ~631 files per empirical `find architecture/ -type f | wc -l`, spanning `decisions/`, `slices/`, `slices/archive/`, `risk-register.md`, `methodology-changelog.md`, `lessons-learned.md`, `build-checks.md`, `shippability.md`, `concept.md`, `triage.md`, `principles.md`, `pipeline.md`, `tutorial.md`, etc.) at `/commit-slice --merge` time. This is the LARGEST single git commit in the repo's history and is the slice's load-bearing payoff. Pre-`--merge` dry-run is must-not-defer (per /critique M6 ACCEPTED-FIXED).

## What's reused

- [[ADR-063]] — BRANCH-2 worktree-per-slice discipline (slice-066); the discipline whose recurring "gitignored vault won't propagate to worktree → `cp -r architecture/` DEVIATION" tax this slice retires structurally
- [[ADR-065]] — `VAULT_ROOT` constant seam (slice-068); UNCHANGED here — the `_DEFAULT = "architecture"` stays; the flip to `".sdlc"` is slice-070 scope (slice-068's seam is what makes slice-070's rename a 1-line change after slice-069 ships)
- [[ADR-029]] — BCI-1 deterministic post-write fail-loud gate (slice-030A); the gate's contract (live `architecture/build-checks.md` ≡ canonical tracked fixture on full per-rule structural identity) is preserved unchanged — the live file simply becomes co-tracked with its fixture (the dual-source becomes git-visible at PR-review time before BCI-1 fires, which is a *better* posture, not a defeat)
- [[ADR-030]] / [[ADR-031]] — SCMD-1 machine-stable command column + incidental-decoupling invariant (slice-031); preserved unchanged — the slice-031 decoupling was specifically for *incidental* coupling (catalog-cited tests reading gitignored vault); now that the vault is tracked the runtime-invariant gate continues to pass (the cited-fns set is unchanged), and the "incidental decoupling" naming becomes a historical artifact rather than active enforcement
- `.gitignore` line-4-7 `__pycache__/` `*.pyc` `*.pyo` `.pytest_cache/` (PRESERVED) — these still need to be ignored INSIDE the soon-to-be-tracked vault tree (the must-not-defer item verifies no `__pycache__` accidentally lands in the vault commit)
- `tools/_vault_paths.py` — `VAULT_ROOT` constant module (slice-068); UNCHANGED — the `_DEFAULT = "architecture"` stays
- `tools/branch_workflow_audit.py` — BRANCH-2 worktree-mode audit; UNCHANGED — its 7 BRANCH-1 carry-forward + 4 BRANCH-2 worktree-mode violation kinds continue to enforce the discipline; the `WORKTREE=skip` escape-hatch DEVIATION line stays available for legitimate bootstrap cases but the N=4 worktree-vs-gitignored class no longer needs it

## Components touched

### `.gitignore` (modified)
- **Responsibility**: Declare which top-level paths git tracks vs ignores
- **Lives at**: `.gitignore` (modified by this slice — 1-line removal + 1-line comment rewrite)
- **Key interactions**: Read by git on every staging/commit/checkout; consulted by `tools/build_checks_integrity.py` (BCI-1) and `tools/shippability_decoupling_audit.py` (SCMD-1) only via runtime test fixtures, not via file-content parsing — those audits are unaffected by the line-removal because they assert *content* invariants on the vault files, not file-tracking status

### `architecture/decisions/ADR-066-track-vault-in-git.md` (NEW)
- **Responsibility**: Document the philosophy + motivation + consequences + reversibility of the vault-tracking decision so future contributors understand the rationale
- **Lives at**: `architecture/decisions/ADR-066-track-vault-in-git.md` (created by this slice)
- **Key interactions**: Referenced by this slice's reflection.md "lessons" entries; referenced by slice-070's design.md / ADR (when slice-070 ships the rename); discovered by `$PY -m graphify vault architecture` keyword-search future runs
- **Supersedes**: frontmatter `supersedes: null` (ADR-028 stays accepted in full). Partial scope-supersession of [[ADR-028]] §Options-#1 only (per /critique B3 ACCEPTED-FIXED), documented inline via the introductory §Supersession scope block + §Options §Option 1 (revised). ADR-028's BCI-1 core Decisions 1-3 (tracked fixtures + literal-constant oracle + full-structural-identity gate) remain accepted unchanged.

### `CLAUDE.md` (verified no-op)
- **Responsibility**: Project-level Claude Code instructions; the "Brownfield rules" + "Vault discipline" sections describe vault interaction patterns
- **Lives at**: `CLAUDE.md` (root; project instructions)
- **Key interactions**: Loaded into every Claude conversation in this repo via the `claudeMd` context window
- **This slice's change**: ZERO edits (empirical grep at `/design-slice` time confirms `CLAUDE.md` contains no `Local-only` / `never tracked` matches). AC3 verifies via grep returning empty. The substantive prose update lands in `.gitignore` line 10 comment.

### `architecture/` directory tree (becomes tracked)
- **Responsibility**: The vault — methodology archive, decisions, slice history, risk register, lessons-learned, build-checks, shippability catalog, candidate queue
- **Lives at**: `architecture/` (~11MB, ~631 files per empirical `find architecture/ -type f | wc -l`)
- **Key interactions**: Read by 14 Step-6 audits, 13+ skill files, 4 agents; written by `/slice`, `/design-slice`, `/critique`, `/critique-review`, `/build-slice`, `/validate-slice`, `/reflect`, `/diagnose`, `/risk-spike`, `/discover`, `/adopt`, `/triage`
- **This slice's change**: file-tracking status flips from gitignored → tracked. No content edit in this slice except the slice-069 folder's own artifacts (mission-brief.md, design.md, ADR-066, critique.md, critique-review.md, build-log.md, validation.md, reflection.md) which would be created during the normal slice lifecycle anyway

## Contracts added or changed

(none — this slice does not introduce new APIs / endpoints / events / schemas. The change is configuration + content commit + philosophy ADR. No code interfaces change.)

## Data model deltas

(none — this slice does not change any data model, persistence schema, or stored data layout.)

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). This slice introduces no new code modules; only a markdown ADR file and configuration edits. WIRE-1 treats markdown-only additions as out-of-scope for the wiring contract (the audit scans for new `.py` / `.ts` / `.go` consumer modules). Zero-row matrix below = clean per audit semantics.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-066]] — vault tracked in git (remove `architecture/` from `.gitignore`); enables cross-machine parallel slice development and structurally retires the N=4 cumulative worktree-vs-gitignored-vault class — reversibility: **expensive**

## Authorization model for this slice

(N/A — no auth surface change. This slice's actions are a one-time `.gitignore` flip + a `git add architecture/` + a `git commit` operation; the only authorization is the repo owner's authority to commit to master, which they already possess.)

## Error model for this slice

(N/A — no error paths introduced. The only failure modes are operational:
- **Secrets-scan-finds-leak** → STOP the slice; do NOT commit; remediate by removing the secret-containing file from `architecture/` before retry (this is the must-not-defer item, not an error path in shipped code)
- **`.git`-nested-under-architecture** → STOP the slice; should not exist (`find architecture/ -name '.git' -type d` smoke at mid-slice gate)
- **`__pycache__`-accidentally-staged** → already covered by `.gitignore` lines 4-7 which take precedence per gitignore precedence rules (later rules don't override earlier rules — the un-ignoring of `architecture/` does NOT re-ignore the `__pycache__/` pattern matches inside the tree)
- **BCI-1-fail-loud-on-first-build** → if the live `architecture/build-checks.md` happens to be drifted from the canonical fixture at slice-069 commit time, BCI-1 HALTs at `/build-slice` Step 6; remediate by reconstructing the live file from the fixture per ADR-029 protocol (this is independent of the tracking change — the gate's contract is preserved); BC-PROJ-8 revision must update live + fixture in lockstep to avoid this fail-loud at slice-069's own build
- **BCI-1-new-co-tracking-failure-modes** → two new failure modes analyzed in [[ADR-066]] §Consequences per /critique B6 ACCEPTED-FIXED: (a) corruption-on-master window if `/reflect` Step 5b drift bypasses BCI-1 via `--no-verify` (mitigation: BCI-1 stays Step-6 non-opt-out — requires DOUBLE failure), (b) parallel-branch merge-conflict on machine-generated build-checks.md (mitigation: small diff + canonical-fixture-driven mechanical resolution)

None of these are run-time error paths in shipped consumer code; they are slice-build-time operational checks.)

## Consumer-freeze cascade note (carried forward from slice-068 ADR-065)

This slice does NOT touch `tools/_vault_paths.py` — the `_DEFAULT = "architecture"` stays. The consumer-freeze cascade documented at [[ADR-065]] §Decision (downstream consumers freeze derived constants at their own import-time) is unaffected; no test-isolation change; no monkeypatch semantic shift.

## Sites EXCLUDED from this slice

(per slice-068 design.md §Sites EXCLUDED precedent — explicit non-changes belong in the design)

- **`tools/_vault_paths.py` `_DEFAULT` constant** — UNCHANGED at `"architecture"`. Flip to `".sdlc"` is slice-070.
- **All 73 prose+test files containing `architecture/` literals** (~480 occurrences) — UNCHANGED. Sweep is slice-070.
- **R-15 audit regex at `tests/methodology/test_resolve_slice_dir.py:233`** — UNCHANGED. Extension to recognize `.sdlc/` is slice-070 (the regex literally matches `REPO_ROOT\s*/\s*"architecture"\s*/\s*"slices"` — it would atrophy silently if the vault rename happened without coordinated extension; that's why slice-068 design.md §Sites EXCLUDED §(a) cited it as a slice-070 prerequisite).
- **`diagnose-out/backlog.md` exception (`!diagnose-out/backlog.md`)** — NOT added. BCR-1 still works on the local machine via the existing tracked `architecture/risk-register.md` + `architecture/slices/_index.md` + `architecture/slices/archive/*/reflection.md` sources; the backlog.md cross-machine visibility is a separate decision deferred per slice-069 mission-brief out-of-scope.
- **`graphify-out/` tracking** — NOT added. Entirely derived; regenerable via `$PY -m graphify code .` in seconds.
- **3 of the 4 less-active skill-prose surfaces mentioning "Local-only" / "gitignored" / "never tracked"** (`methodology-changelog.md` historical entries, `skills/build-slice/SKILL.md`, `skills/validate-slice/SKILL.md`, `skills/reflect/SKILL.md`) — UNCHANGED. These describe historical state at the time the corresponding slice was written. Sweep is slice-070 (or a follow-up cleanup slice). **`skills/code-review/SKILL.md:66` is PROMOTED into slice-069 scope** per /critique M5 ACCEPTED-PENDING (highest-leverage stale-prose surface; the others are softer and survive a deferral).
- **BCI-1 contract redesign** — NOT changed. The live-vs-fixture dual-source contract stays. Both files happening to be tracked now is an *improvement* (drift becomes PR-visible) not a defect; no contract redesign needed. The 2 new co-tracking failure modes (corruption-on-master + parallel-branch merge-conflict on machine-generated artifact) are analyzed in ADR-066 §Consequences per /critique B6 ACCEPTED-FIXED.

## MEPD-1 Inclusion-heuristic posture: INCLUDE (revised post-/critique B4)

**Revised** from original EXCLUDE posture: the /critique B4 ACCEPTED-PENDING promotion of BC-PROJ-8 revision into slice-069 scope shifts an existing rule's enforcement boundary (BC-PROJ-8's trigger-keyword set narrows — drops `gitignored` — so slices that would previously trigger the rule will no longer trigger it). Per MEPD-1 the 5-criterion table now yields:

| Criterion | Slice-069 verdict |
|-----------|-------------------|
| Does it introduce a new audit rule / gate? | NO |
| Does it introduce a new schema / contract / wire-format? | NO |
| Does it introduce a new methodology-changelog entry? | **YES** (BC-PROJ-8 rule-content supersession; ADR-066 philosophy entry) |
| Does it introduce a new test invariant pinning a methodology rule? | NO (re-aligned existing pins, not new) |
| Does it shift any existing rule's enforcement boundary? | **YES** (BC-PROJ-8 trigger-keyword set narrows) |

2-of-5 YES → INCLUDE. Slice-069 ships a **PMI-1 5-part atomic version bump v0.69.0 → v0.70.0**: `VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` + `~/.claude/ai-sdlc-VERSION` (installed via `tools.install_audit`) + `methodology-changelog.md` header `## v0.70.0` + new v0.70.0 body entry describing the BC-PROJ-8 rule-content revision + the ADR-066 vault-tracking philosophy decision + the /critique B3 ADR-028 §Options-#1 partial supersession. The ADR-066 philosophy is the larger lift and is the entry's primary narrative; the BC-PROJ-8 revision is a sub-bullet (one-rule content revision, not a new rule mint).

(The slice-068 + slice-067 + slice-066 precedent of ADR-without-changelog-entry applies when the ADR captures an architectural decision that mints no enforceable rule AND does not revise any existing rule's enforcement boundary. Slice-069 has BOTH: a new architectural decision AND a BC-PROJ-8 enforcement-boundary revision — INCLUDE applies.)
