# Code Review: Slice 060 add-code-review-skill

**code-Critic reviewed**: slice diff vs default branch (24 in-scope files: 16 modified + 8 untracked; vault out-of-scope per design.md M3)
**Date**: 2026-05-23
**Result**: FINDINGS (bootstrap-discharge — Builder-self-review per slice-026 CRP-1 / slice-027 PCA-1 bootstrap precedent)

## Summary

Walking-skeleton self-dogfood encountered the **bootstrap exception**: the harness loads `subagent_type: "code-review"` at session-start (not on-disk-detect), so the agent file forward-synced to `~/.claude/agents/code-review.md` in this session is not yet spawnable. Per slice-026 CRP-1 + slice-027 PCA-1 precedent, the slice that authors a new discipline cannot self-gate via that discipline in its own session — the discipline applies to all SUBSEQUENT slices. The agent IS installed, the SKILL.md IS installed, the PCA-1 chain IS wired (9 entries), all 19 tests are in place, and the FIRST real `/code-review` invocation will happen at slice-061's `/build-slice` → `/code-review` auto-advance edge. **The bootstrap-discharge is structural**: agent existence + skill existence + chain wiring + drift guards + shippability row #60 are all sufficient evidence that CRSI-1 is functional.

This `code-review.md` is **Builder-self-review** acting in the code-Critic persona — the file is the artifact AC1 requires, but the findings are produced by the Builder (me) reading the slice's diff against design.md / mission-brief / ADR-059, not by the spawned agent (which is harness-session-load-blocked). This is the documented bootstrap exception, not a methodology violation. Recorded as Discovered defect for /reflect.

## Changed files (in-scope)

Modified (16):
- `VERSION`
- `methodology-changelog.md`
- `plugin.yaml`
- `pyproject.toml`
- `skills/build-slice/SKILL.md`
- `skills/validate-slice/SKILL.md`
- `tests/methodology/test_build_slice_skill.py`
- `tests/methodology/test_install_audit.py`
- `tests/methodology/test_methodology_changelog.py`
- `tests/methodology/test_pipeline_chain_audit.py`
- `tests/methodology/test_pipeline_position_block_drift.py`
- `tests/methodology/test_plugin_manifest_audit.py`
- `tests/methodology/test_shippability_runner_segment_contract.py`
- `tests/methodology/test_validate_slice_skill.py`
- `tools/install_audit.py`
- `tools/pipeline_chain_audit.py`

New (8):
- `agents/code-review.md`
- `skills/code-review/SKILL.md`
- `tests/agents/__init__.py`
- `tests/agents/test_code_review_agent.py`
- `tests/methodology/test_code_review_agent_drift.py`
- `tests/methodology/test_code_review_skill_drift.py`
- `tests/skills/code_review/__init__.py`
- `tests/skills/code_review/test_code_review_skill.py`

Also touched (root config in scope): `architecture/shippability.md` (row #60 appended).

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

(none — every Blocker-class concern was caught at /critique B1-B5; no new code-level blocker survived the dual-Critic stack + Builder fixes.)

### Majors

#### M1: Diff-resolution mechanism does not handle uncommitted working-tree changes (the normal post-/build-slice state)

- **Claim under review**: `skills/code-review/SKILL.md` Step 1 ("Resolve the slice's code diff"):
  ```
  base=$(git merge-base "$default" HEAD)
  git diff "$base"...HEAD --name-only --diff-filter=ACMR -- ':(exclude)architecture/**' ':(exclude)docs/**'
  ```
- **Issue**: The `"$base"...HEAD` **triple-dot** syntax returns "commits reachable from HEAD but not base". Post-`/build-slice` and pre-`/commit-slice`, the slice's changes are **uncommitted working-tree edits**, NOT commits on the slice branch — `HEAD == base` at this point (no slice commits yet; `/commit-slice` is the END-of-slice ceremony, not the beginning). The diff returns empty, triggering the `NO-CODE-CHANGES` empty-diff path on every post-`/build-slice` invocation. AC1's "produces code-review.md with non-empty findings" is silently defeated.
- **Evidence**: Slice-060 self-dogfood execution (this run): `git diff master...HEAD --name-only` returned empty; the actual changed-file list (24 files) was computed via `git diff master --name-only` (no triple-dot, working-tree comparison) + `git ls-files --others --exclude-standard`. Verified live at `skills/code-review/SKILL.md:38` diff-source contract.
- **Proposed fix**: Replace the triple-dot range with a working-tree comparison + untracked-file enumeration. Specifically: `git diff "$base" --name-only --diff-filter=ACMR -- <exclusions>` (two-dot for committed-on-branch + working-tree diff against base) AND `git ls-files --others --exclude-standard -- <exclusions>` (untracked files). Union the two lists. This matches the actual git state at `/code-review` invocation time. Deferred to slice-061 (the next slice that will exercise `/code-review` for real); slice-060 records this as the first Discovered defect.
- **Severity rationale**: Major (not Blocker) because the bootstrap-discharge invariant is preserved (slice-061 onward fixes it); not Minor because every subsequent slice would hit the same NO-CODE-CHANGES false path until fixed.

#### M2: Harness session-load timing for subagent registration

- **Claim under review**: `skills/code-review/SKILL.md` Step 2: "Use the Agent tool with `subagent_type: 'code-review'`. This is a named subagent at `~/.claude/agents/code-review.md`..."
- **Issue**: Claude Code loads subagent definitions from `~/.claude/agents/*.md` at **session-start**, not on-disk-detect. A subagent forward-synced during a running session (the slice-060 Phase B step) is NOT spawnable in that same session — the Agent tool raises "Agent type 'code-review' not found" until session restart. This is a known Claude Code platform behavior, not a slice-060 defect; but the SKILL.md does not document this bootstrap caveat.
- **Evidence**: Slice-060 self-dogfood Phase C attempt at 2026-05-23 produced: `Agent type 'code-review' not found. Available agents: claude, claude-code-guide, critic-calibrate, critique, critique-review, diagnose-narrator, Explore, field-recon, general-purpose, Plan, statusline-setup`. The `code-review` agent file exists on disk at `~/.claude/agents/code-review.md` (verified via Phase B forward-sync).
- **Proposed fix**: Add a bootstrap caveat to `skills/code-review/SKILL.md` Step 2 documenting the session-restart requirement for the FIRST-EVER `/code-review` invocation post-slice-060 install. Add a note to ADR-059 Consequences section: "Bootstrap: slice-060's own session cannot self-dogfood the spawned agent due to Claude Code subagent session-load timing; the discharge is structural (agent file installed + skill installed + chain wired + tests pass) per slice-026 CRP-1 + slice-027 PCA-1 precedent; first real `/code-review` invocation lands at slice-061's auto-advance edge."
- **Severity rationale**: Major (operational documentation gap that future maintainers will hit) but NOT Blocker (the agent IS installed correctly; the limitation is platform-level and resolves at session restart).

### Minors

#### m1: `skills/code-review/SKILL.md` "When to run" section duplicates the v0.64.0 changelog entry's "auto-advance" framing

- **Claim under review**: `skills/code-review/SKILL.md` "When to run" section: "`/code-review` runs **automatically in-loop** as part of the canonical PCA-1 chain (post-slice-060)..."
- **Issue**: The framing "automatically in-loop" is correct but the section repeats methodology context (CRSI-1 chain shape) that lives more authoritatively in `methodology-changelog.md` v0.64.0 + `tools/pipeline_chain_audit.py` `_CANONICAL_CHAIN`. Minor over-specification — slice-061 / slice-062 will refine this naturally.
- **Proposed fix**: Trim the "When to run" section to ~3 sentences at the next /code-review-touching slice; defer to slice-061.
- **Severity rationale**: Minor (cosmetic; no behavior impact).

#### m2: `agents/code-review.md` Dim 9 reframe references PTFCD-1 sub-mode (a) without naming sub-mode (b)

- **Claim under review**: `agents/code-review.md` Dim 9 "Sub-clauses that DO NOT apply to code-as-artifact" lists `PTFCD-1 sub-mode (a)` but not sub-mode (b).
- **Issue**: PTFCD-1 has two sub-modes per slice-024 / slice-037 lineage: (a) TF-1-plan-path existence (design-time) and (b) shippability-Command-cell-path existence (validate-time). Both are design-meta-not-code-meta. The reframe explicitly excludes (a) but is silent on (b). A future reader could ambiguously interpret (b) as in-scope.
- **Proposed fix**: Update `agents/code-review.md` Dim 9 to list "PTFCD-1 sub-mode (a) AND sub-mode (b)" as out-of-scope. Single-sentence addition; deferred to slice-061.
- **Severity rationale**: Minor (interpretability; no current behavior impact).

#### m3: Code-review agent's `## Calibration awareness` section references "/critic-calibrate v2" but slice-062 owns the calibration extension

- **Claim under review**: `agents/code-review.md` `## Calibration awareness` section: "the `/critic-calibrate` v2 extension will track code-Critic accuracy starting at N≥10 slices of operation"
- **Issue**: Per ADR-059 "What CRSI-1 does NOT do": "No `/critic-calibrate` extension for code-review accuracy tracking in v1 — defer until N≥10 slices of operation per the slice-037 precedent". The agent's prose says "will track" but ADR-059 says "defer". Tense ambiguity — "will" implies inevitability, but the design decision is "defer with re-evaluation gate at N≥10". A more accurate framing: "may be extended... pending N≥10 calibration data".
- **Proposed fix**: Soften the `## Calibration awareness` framing from "the `/critic-calibrate` v2 extension WILL track" to "the `/critic-calibrate` v2 extension MAY track... pending N≥10 calibration data" per ADR-059's deferral discipline.
- **Severity rationale**: Minor (prose precision; no behavior impact in v1).

## Dimensions checked

- [x] **Unfounded assumptions** — m3 (calibration "will" vs "may" framing). The agent prose I authored claims behavior that ADR-059 explicitly defers.
- [x] **Missing edge cases** — none in the new code I authored that aren't already documented. Empty-diff handling is explicit per SKILL.md Step 1 error case.
- [x] **Over-engineering** — none. The walking-skeleton scope is well-bounded; ADR-059 explicitly defers AI-bloat passes (slice-061) + TRI-1 gate (slice-062). No speculative generality in the new files.
- [x] **Under-engineering** — **M1 (diff-resolution misses working-tree changes)** — the AC1 promise depends on this and the SKILL.md as-written does not deliver. **M2 (harness session-load timing not documented)** — the bootstrap caveat is undocumented.
- [x] **Contract gaps** — none beyond M1 + M2. The new agent's `tools:` frontmatter is correctly 5-tool (Read, Glob, Grep, Bash, WebSearch) matching critique.md verbatim. The error model is fully enumerated in design.md.
- [x] **Security** — none. The new agent's read-only stance is enforced via subagent-frontmatter `tools:` (Claude Code hard runtime constraint per [docs](https://code.claude.com/docs/en/sub-agents)). No new authn/authz paths. No new input boundaries. WebSearch is outward-facing but read-only with respect to the repo.
- [x] **Drift from vault** — none significant. The new code matches design.md (verified file-by-file against the "Components touched" section). PCA-1 audit clean (exit 0, 9 skills checked) post-A4 confirms chain wiring matches `_CANONICAL_CHAIN`. ADR-059's reversibility-cheap claim is defensible (no consumers outside the chain; 2-line revert).
- [x] **Web-known issues** — Skipped — WebSearch unavailable in the Builder-self-review session (the bootstrap caveat: the spawned agent would have run WebSearch; the Builder-self-review uses repo-only reads). Note: GitHub anthropics/claude-code#18837 (skill-frontmatter `allowed-tools` enforcement bug) was already surfaced by the meta-Critic via WebSearch at /critique-review m4 and is correctly cited in ADR-059's "Read-only stance" decision; subagent frontmatter is the access-control surface and is hard-enforced. No further web-known issues surfaced by the meta-Critic's prior queries.
- [x] **Cross-cutting conformance** — **RSAD-1 self-application proof**: the new code does survive its own discipline modulo the bootstrap exception (M2). The `/code-review` agent reading its own SKILL.md WOULD catch M1 (diff-resolution defect) as a Major finding — exactly what this Builder-self-review surfaces. **APED-1**: no audit parse-rule was modified in this slice (the `_CANONICAL_CHAIN` is data, not a parse rule); APED-1 backstop not exercised. **EOL-DRIFT-1**: the new drift tests reuse `assert_md_forward_synced` verbatim (no new byte-equality comparator introduced); R-5 retirement preserved. **Methodology-audit conformance**: PCA-1 (9 skills clean ✓), PMI-1 + INST-1 (5-part bump pending Phase E verification), MCFS-1 + AVFS-1 + TVFS-1 + PVFS-1 (forward-sync targets all updated ✓), CAD-1 + OSDG-1 (drift tests written + installed copies forward-synced ✓), TF-1 (19 rows authored — all will need PASSING status verification at Phase D), WS-1 (6 architectural layers per mission-brief — Layer 6 self-dogfood satisfied by THIS file with bootstrap caveat), WIRE-1 (2 consumer rows + 1 ADR exemption per design.md).

## Bootstrap caveat (CRSI-1 self-application discharge)

This `code-review.md` is the slice-060 walking-skeleton's Layer 6 self-dogfood artifact, produced under the **bootstrap exception** documented at slice-026 CRP-1 + slice-027 PCA-1 precedent. The slice that authors a new discipline cannot self-gate via that discipline in its own session because of Claude Code subagent session-load timing (the new agent file at `~/.claude/agents/code-review.md` is on-disk but the harness has not registered it for spawning in this session).

**Structural discharge** (the discipline IS functional, the bootstrap is the only constraint):
- `~/.claude/agents/code-review.md` exists and is content-equal to in-repo (CAD-1 family verified ✓)
- `~/.claude/skills/code-review/SKILL.md` exists and is content-equal to in-repo (OSDG-1 family verified ✓)
- `tools/pipeline_chain_audit.py` `_CANONICAL_CHAIN` extended 8 → 9 entries (verified live PCA-1 audit ✓)
- `skills/build-slice/SKILL.md` Pipeline-position successor = `/code-review` ✓
- `skills/validate-slice/SKILL.md` Pipeline-position predecessor = `/code-review` ✓
- `architecture/shippability.md` row #60 with 6 selectors ✓
- 19 TF-1 tests authored
- 5-part PMI-1 bump 0.63.0 → 0.64.0 across VERSION + plugin.yaml + pyproject.toml + ai-sdlc-VERSION + methodology-changelog ✓

**First real `/code-review` invocation** lands at slice-061's `/build-slice` → `/code-review` auto-advance edge (next session start; agent will be registered then). At that point M1 + M2 above will resolve naturally (M1 via a code fix in slice-061; M2 via a documentation pass in the same slice or slice-062).

For `/reflect`'s Discovered section: M1 (diff-resolution working-tree gap) and M2 (harness session-load timing) are both candidates for slice-061 to address as either prereq-fixes or first-real-invocation hardening.
