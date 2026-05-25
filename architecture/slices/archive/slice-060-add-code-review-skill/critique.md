# Critique: Slice 060 add-code-review-skill

**Critic reviewed**: mission-brief.md, design.md, ADR-059-add-code-review-skill.md
**Date**: 2026-05-23
**Result**: NEEDS-FIXES

## Summary

The slice is structurally sound — walking-skeleton scope is well-chosen, the bootstrap-discharge framing mirrors PCA-1/CRP-1 precedent, and the OSDG-1 family-add pattern is correct. But the design contains five concrete blocker-class errors that would break Step 6 audits at build-time: (1) the alphabetical insertion points in `_CANONICAL_SKILLS` and `_CANONICAL_AGENTS` are stated incorrectly; (2) the PMI-1 "4-part" atomic bump omits the `pyproject.toml` `[project].version` leg (PVFS-1 will FAIL); (3) `tests/agents/` directory does not exist on disk and design has no plan-step to create it (PTFCD-1 phantom-path-convention); (4) the mission-brief and design contradict each other on the agent's tool count (4 vs 5 — WebSearch in/out); (5) the design's "all other code unchanged" claim for `tools/pipeline_chain_audit.py` ignores six hardcoded "8" references (lines 56, 225, 309 + `tools/install_audit.py:84` + `tests/methodology/test_pipeline_chain_audit.py:4,66` + `tests/methodology/test_pipeline_position_block_drift.py`) that will break `test_clean_chain_exits_zero` and the audit's own error messages. Plus the agent prose itself (the 9-dimensions-vs-CODE reframe) is not designed — only asserted.

## Findings

### Blockers (must address before /build-slice)

#### B1: Alphabetical insertion points in `_CANONICAL_SKILLS` and `_CANONICAL_AGENTS` are stated incorrectly

- **Claim under review** (design.md:72): "append `'code-review'` to `_CANONICAL_SKILLS` (preserving alphabetical order: between `'commit-slice'` and `'critic-calibrate'`) and append `'code-review'` to `_CANONICAL_AGENTS` (preserving alphabetical order: between `'critic-calibrate'` and `'critique'`)"
- **Issue**: Per ASCII lexical ordering, `'code-review'` (c-o-d) < `'commit-slice'` (c-o-m), so `code-review` should sort BEFORE `commit-slice`, not between `commit-slice` and `critic-calibrate`. Same for agents: `'code-review'` (c-o-d) < `'critic-calibrate'` (c-r-i), so `code-review` should be the FIRST entry in `_CANONICAL_AGENTS`. If the Builder follows the design literally, the resulting tuples won't be alphabetical.
- **Evidence**: `tools/install_audit.py:52-64` — current tuples ARE alphabetical (`adopt, archive, build-slice, commit-slice, critic-calibrate, ...` and `critic-calibrate, critique, critique-review, diagnose-narrator, field-recon`). **Recompute verified** (2026-05-23 against the live file): correct insertion points are skills — between `'build-slice'` and `'commit-slice'`; agents — first entry, before `'critic-calibrate'`.
- **Proposed fix**: Update design.md "Components touched / tools/install_audit.py (MODIFY)" line to: "append `'code-review'` to `_CANONICAL_SKILLS` (alphabetical: between `'build-slice'` and `'commit-slice'`)" and "prepend `'code-review'` to `_CANONICAL_AGENTS` (alphabetical: first entry, before `'critic-calibrate'`)".
- **Builder draft**: **ACCEPTED-FIXED** at design.md "Components touched / tools/install_audit.py (MODIFY)" — Critic recompute-verified against the live file; lexical ordering is unambiguous.

#### B2: PMI-1 "4-part atomic bump" omits the `pyproject.toml` `[project].version` leg (PVFS-1 will FAIL)

- **Claim under review** (mission-brief AC #5 + design.md "What's reused" + ADR-059 Consequences): "4-part PMI-1 atomic version bump 0.63.0 → 0.64.0 (VERSION + plugin.yaml + installed `~/.claude/ai-sdlc-VERSION` + installed `~/.claude/methodology-changelog.md`)"
- **Issue**: Per **PVFS-1** (slice-054 / ADR-056), `pyproject.toml` `[project].version` MUST equal trimmed `VERSION`. Verified live: `pyproject.toml:20` = `version = "0.63.0"`. After this slice bumps VERSION to 0.64.0 but leaves pyproject.toml at 0.63.0, PVFS-1 will FAIL at Step 6. Slice-059 was a 5-part bump (VERSION + plugin.yaml + pyproject.toml + ai-sdlc-VERSION + methodology-changelog). Mission-brief + design + ADR omit pyproject.toml.
- **Evidence**: `pyproject.toml:20`; PVFS-1 test pinning `pyproject.toml [project].version == trimmed VERSION`.
- **Proposed fix**: Update mission-brief AC #5 to "**5-part** PMI-1 atomic version bump 0.63.0 → 0.64.0 (VERSION + plugin.yaml.version + **pyproject.toml `[project].version`** + installed `~/.claude/ai-sdlc-VERSION` + installed `~/.claude/methodology-changelog.md`)". Update design.md "What's reused" line to add pyproject.toml leg. Update ADR-059 Consequences item 10. Add verification step for pyproject.toml to TF-1 plan (or rely on existing PVFS-1 catalog row firing).
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief AC #5 + design.md "What's reused" + ADR-059 Consequences — PVFS-1 leg verified live; consistent with slice-059 precedent.

#### B3: `tests/agents/` directory does not exist — phantom path convention (PTFCD-1 class)

- **Claim under review** (mission-brief AC #2 + design.md "What's new" + TF-1 plan rows 4-6): "`tests/agents/test_code_review_agent.py`"
- **Issue**: Verified live: `tests/agents/` does NOT exist on disk. `tests/skills/code_review/` also does not exist (parent `tests/skills/` exists but carries only `diagnose/` subpackage). TF-1 plan cites three test functions under `tests/agents/test_code_review_agent.py` but no plan-step creates the directory + `__init__.py`. Per Aggregated lessons "Plan-mode ls/stat of every cited new test directory must be the FIRST plan-mode action" (slice-027-B1, slice-037 N=2) — this is exactly the phantom-path-convention class.
- **Evidence**: `ls tests/agents/` → "No such file or directory"; `ls tests/skills/` → only `__init__.py`, `__pycache__`, `diagnose/`.
- **Proposed fix**: Add explicit plan steps to design.md "Components touched" enumerating: (a) `tests/agents/__init__.py` (NEW); (b) `tests/skills/code_review/__init__.py` (NEW). Add to mission-brief "What's new" + TF-1 plan a pre-row noting both `__init__.py` creations are prerequisite. Stat both in `/build-slice` Phase 1 plan mode before any work in those subpackages.
- **Builder draft**: **ACCEPTED-FIXED** at design.md "Components touched" + mission-brief "What's new" + TF-1 plan — phantom directories verified absent; per the slice-027-B1 / slice-037 N=2 phantom-path lineage.

#### B4: Mission-brief and design contradict on agent tool count (4 vs 5 — WebSearch in/out)

- **Claim under review**:
  - mission-brief AC #2: "Agent tools are restricted to `Read, Glob, Grep, Bash`" (4 tools)
  - mission-brief must-not-defer #2: "Agent tools restricted to read-only set (`Read, Glob, Grep, Bash`)" (4 tools)
  - design.md agent invocation contract + "What's reused" + CSP-1 parity: "`Read, Glob, Grep, Bash, WebSearch`" (5 tools)
- **Issue**: 3-site cross-file drift (FBCD-1 sub-mode (a) original-draft cross-file consistency). The agent's Dim 8 (Web-known issues) per the inherited critique.md prompt REQUIRES WebSearch — without it the agent must skip Dim 8 entirely on every code review. The correct tool count is **5** (matches `agents/critique.md:4` verbatim for CSP-1 parity). Mission-brief is wrong at two sites; design is right.
- **Evidence**: `agents/critique.md:4` — `tools: Read, Glob, Grep, Bash, WebSearch`; design.md "CSP-1 cross-spec parity" section: "`tools: Read, Glob, Grep, Bash, WebSearch` — identical to `agents/critique.md:4`".
- **Proposed fix**: Update mission-brief AC #2 + must-not-defer #2 to: "Agent tools are `Read, Glob, Grep, Bash, WebSearch` (read-only — `Write`, `Edit`, `NotebookEdit` forbidden; matches `agents/critique.md` verbatim for CSP-1 parity)". Spec the `test_agent_md_read_only_tools_pinned` test contract in design.md: assert literal `tools: Read, Glob, Grep, Bash, WebSearch` is present AND each of `Write`, `Edit`, `NotebookEdit` are absent from the tools line (positive-and-negative substring pattern per slice-007 M2 + slice-053 M-add-4 precedent).
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief AC #2 + must-not-defer #2 + design.md (test contract spec) — 3-site cross-file drift caught; correct value is 5 (matches critique.md verbatim).

#### B5: `tools/pipeline_chain_audit.py` extension is wider than "2-line tuple change" — 6 hardcoded "8" references will FAIL or mislead

- **Claim under review** (design.md "Components touched / tools/pipeline_chain_audit.py"): "extended via 2-line `_CANONICAL_CHAIN` tuple-of-tuples change at `tools/pipeline_chain_audit.py:73-82` (NOT cloned; not refactored — modified in place per CLAUDE.md 'refactors need a slice'; the change is a single-tuple-add + single-tuple-edit on lines 78-79)" and "**All other code (`_REQUIRED_FIELDS`, parsing, `audit()`, `main()`) unchanged.**"
- **Issue**: Verified live — six existing hardcoded "8" references will be stale or break after the chain grows to 9:
  - `tools/pipeline_chain_audit.py:56` exit-code docstring "all 8 blocks well-formed"
  - `tools/pipeline_chain_audit.py:225` error message "PCA-1 requires it on all 8 covered skills)"
  - `tools/pipeline_chain_audit.py:309` argparse description "verify the 8-skill pipeline-chain auto-advance"
  - `tools/install_audit.py:84` comment "PCA-1 — verify the 8-skill pipeline-chain auto-advance loop"
  - `tests/methodology/test_pipeline_chain_audit.py:66`: `assert len(result.skills_checked) == 8` — **will HARD-FAIL** after chain grows to 9
  - `tests/methodology/test_pipeline_chain_audit.py:4` docstring "all 8 covered skills"
  - `tests/methodology/test_pipeline_position_block_drift.py` (file exists per verification; expected docstring/message drift on "8 covered skills" — Critic-cited but pending grep)

  Per SCPD-1 (slice-013/014) consumer-reference propagation: shippability.md row #27 Command cell references `test_clean_chain_exits_zero` literally (verified). When that test FAILs, row #27 FAILs.
- **Evidence**: `grep -n "8-skill\|8 covered\|8 blocks\|== 8"` over `tools/` + `tests/methodology/` returns the 6 verified sites. shippability.md row #27 Command cell verified as quoted in critique.
- **Proposed fix**: Update design.md "Components touched / tools/pipeline_chain_audit.py (MODIFY)" to enumerate ALL hardcoded "8" sites needing update to "9": file lines 56, 225, 309 + `tools/install_audit.py:84` + `tests/methodology/test_pipeline_chain_audit.py:4` (docstring) + `:66` (assertion) + `tests/methodology/test_pipeline_position_block_drift.py` (docstring/message). Add to TF-1 plan two new rows: (a) update `test_clean_chain_exits_zero` from `== 8` to `== 9`; (b) update `test_pipeline_position_block_byte_equal_in_repo_vs_installed` docstring/message (file scan at /build-slice plan mode). Per SCPD-1: enumerate shippability.md row #27 in design.md "What's reused" as a consumer-reference-propagation surface — its Command continues to pass because the underlying `test_clean_chain_exits_zero` is updated in lock-step (NOT a row edit; the row prose remains historical).
- **Builder draft**: **ACCEPTED-FIXED** at design.md "Components touched / tools/pipeline_chain_audit.py" + mission-brief TF-1 plan (add 2 rows) + design.md "What's reused" (add row #27 SCPD-1 propagation note) — 6 sites verified live via grep; SCPD-1 sub-mode (b) proactive-application required to keep shippability row #27 passing.

### Majors (address this slice)

#### M1: The 9-dimensions-vs-CODE reframe is asserted but not designed — agent prose is hand-waved

- **Claim under review** (design.md "CSP-1 cross-spec parity" + ADR-059 Decision): "9 dimensions enumerated — identical names and order as `agents/critique.md` Dimension table"; "same 9 dimensions (reframed for code, not design)"
- **Issue**: Multiple of the 9 dimensions don't translate cleanly from design-review to code-review:
  - **Dim 7 (Drift from vault)** — for design, catches "design contradicts an ADR / references components that don't exist". For CODE, what's the analog? Code contradicts design.md? Code references symbols absent from graphify? Without concrete rewording, the agent will produce nonsense findings using design-framework language.
  - **Dim 9 (Cross-cutting conformance)** — heavily SDLC-process-meta (TF-1, PCA-1, SCPD-1, FBCD-1, RPCD-1, etc.). Most are properties of slice mission-brief/design, NOT code diff. Some (RSAD-1, APED-1) DO apply when code is the artifact.
  - **Dim 5 (Contract gaps)** — for design, missing pagination/auth/error-codes in NEW endpoints. For CODE: missing docstrings? Missing type hints? Untested error path? Translation undefined.
- The TF-1 row `test_agent_md_contains_nine_dimensions_against_code` cannot reasonably check more than "the 9 dimension names appear in the markdown" — tautologically-green per the slice-037 M-add-1 / slice-051 content-bearing-pin discipline.
- **Evidence**: design.md provides zero concrete reframing prose; every reframing decision deferred to "agent prose drafting at build time".
- **Proposed fix**: Add to design.md a new section "## 9 dimensions reframed for code" with one paragraph per dimension specifying the design→code substitution: input artifact (slice code diff vs slice design.md), failure-mode class examples, framework citation (mostly transfers verbatim). For Dim 9, decide which sub-clauses apply to code-as-artifact (RSAD-1, APED-1) and which don't (FBCD-1, SCPD-1, TPHD-1, PTFCD-1 — design-meta). Pin `test_agent_md_contains_nine_dimensions_against_code` with substring assertions covering the reframed prose, not just dimension names (content-bearing test per slice-051 / slice-037 M-add-1 lesson).
- **Builder draft**: **ACCEPTED-FIXED** at design.md (new "## 9 dimensions reframed for code" section) + design.md test contract spec for the dimension-content pin — slice-051 / slice-037 content-bearing-pin discipline directly applies; tautological green is the exact failure mode the lesson codifies.

#### M2: PCA-1 bootstrap-discharge sequence is not phase-planned — self-dogfood test depends on forward-sync done EARLIER in same build

- **Claim under review** (mission-brief AC #1): "Walking-skeleton verification: invoking `/code-review` against slice-060 itself produces `architecture/slices/slice-060-add-code-review-skill/code-review.md` with non-empty findings."
- **Issue**: For the self-dogfood test to PASS, the build sequence must hit:
  - Phase A: author `skills/code-review/SKILL.md` + `agents/code-review.md`
  - Phase B: forward-sync to `~/.claude/skills/` + `~/.claude/agents/`
  - Phase C: invoke `/code-review` against slice-060 (writes `architecture/slices/slice-060-.../code-review.md`)
  - Phase D: TF-1 row can PASS
  - Phase E: drift tests PASS (post-forward-sync, EOL-agnostic)
- Slice-027 PCA-1 / slice-026 CRP-1 bootstrap shapes were simpler — no per-slice artifact write required. Slice-060's bootstrap requires an ARTIFACT (`code-review.md`) that doesn't exist until skill+agent are installed AND invoked. Additionally: `test_self_dogfood_produces_code_review_md_on_slice_060` cannot drive an LLM agent from pytest — must be an artifact-existence/content check.
- **Evidence**: mission-brief Layer 6 verification requires the file with non-empty findings; no phase-plan step ties the invocation to a specific build-sequence point.
- **Proposed fix**: Add to design.md a new "## Build-phase sequence" section enumerating the 5 phases A-E. Clarify in mission-brief AC #1 + TF-1 plan that the test is an artifact-existence-and-content check (reads file at fixed path, asserts presence + ≥1 finding via substring like "Blockers" or "Majors"), NOT a pytest-driven runtime LLM invocation. Add must-not-defer item: "the `/code-review` self-invocation against slice-060 happens BETWEEN the forward-sync step and the TF-1 strict-pre-finish pytest run".
- **Builder draft**: **ACCEPTED-FIXED** at design.md (new "## Build-phase sequence" section) + mission-brief AC #1 clarification + new must-not-defer item — phase ordering is real and load-bearing; without explicit enumeration the Builder will get the sequencing wrong at build time.

#### M3: Empty-diff handling under-specifies what "code" includes for this slice's own self-dogfood

- **Claim under review** (design.md Diff source contract): "`git diff <base>...HEAD --name-only --diff-filter=ACMR -- ':(exclude)architecture/**'`"
- **Issue**: Slice-060 touches `skills/code-review/SKILL.md`, `agents/code-review.md`, multiple `tools/*.py`, `plugin.yaml`, `methodology-changelog.md`, `VERSION`, `pyproject.toml`, plus new `tests/` files. **Is `skills/*/SKILL.md` "code" for review purposes**? The exclusion `architecture/**` excludes vault but the new skill markdown is in `skills/`, not vault. SKILL.md is METHODOLOGY-PROSE-AS-EXECUTABLE-CONTRACT, neither strict code nor strict vault (per CLAUDE.md "skill prose IS executable contract"). The agent will receive a diff including ~9 files; the slice-061 AI-bloat passes make sense for `.py` but not for SKILL.md prose.
- **Evidence**: CLAUDE.md self-hosting-discipline section confirms "skill prose IS executable contract (Claude reads SKILL.md and acts)"; the load-bearing self-application proof needs SKILL.md in scope.
- **Proposed fix**: Add to design.md Diff source contract an explicit statement of in-scope paths: `skills/**/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `tests/**/*.py`, plus root config (`plugin.yaml`, `pyproject.toml`, `VERSION`, `methodology-changelog.md`). Out of scope: `architecture/**` (vault), `docs/**` if any. Document that slice-060's self-dogfood will produce findings on the new SKILL.md + agent.md prose itself (load-bearing self-application proof).
- **Builder draft**: **ACCEPTED-FIXED** at design.md Diff source contract — SKILL.md scope is load-bearing; slice-060's RSAD-1 self-application proof requires the new SKILL.md + agent.md prose to be in scope for the self-dogfood agent.

#### M4: v0.64.0 entry-pin assertion scope not specified — content-bearing pin discipline (slice-051 lesson) not budgeted

- **Claim under review** (mission-brief TF-1 row 15 + design.md "What's new"): "`test_v_0_64_0_entry_references_crsi_1_rule_id`"
- **Issue**: Per slice-051 / slice-058 / slice-059 entry-pin precedent: the entry-pin test must assert MULTIPLE content-bearing substrings, not just the rule-ID. slice-059's `test_v_0_63_0_tvfs_1_entry_present_in_repo` asserts 8 substrings: `## v0.63.0` header, `TVFS-1`, `ADR-058`, `ai-sdlc-tools Version Forward-Sync` (full rule-name expansion), `mints a new rule` + `supersedes nothing`, `4-part PMI-1 atomic bump`, `Rule reference` literal. Test naming convention: `test_v_0_NN_0_<rule>_entry_present_in_repo` (matching META-1 enforcing-assertion pattern at `test_methodology_changelog.py:136`).
- **Evidence**: slice-059 precedent shows 8 substring assertions; META-1 pattern requires `entry_present_in_repo` suffix shape.
- **Proposed fix**: Rename test to `test_v_0_64_0_crsi_1_entry_present_in_repo` (matching slice-059 precedent + META-1 pattern). Update design.md "What's new" to enumerate the substring assertions: (a) `## v0.64.0` header, (b) `CRSI-1` rule ID, (c) `ADR-059` reference, (d) full rule-name expansion `Code-Review Skill Insertion`, (e) `mints a new rule` + `supersedes nothing` lineage, (f) `5-part PMI-1 atomic bump` (per B2 fix), (g) `Rule reference` literal (META-1 obligation), (h) OSDG-1 / CAD-1 lineage anchor.
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief TF-1 plan row 15 (rename) + design.md "What's new" (substring enumeration) — per TPHD-1, the TF-1 plan rename is harmonized in the same fix block. slice-059 precedent + META-1 pattern verified.

#### M5: Catalog row #60's proposed Command set is not enumerated in design — SCPD-1 sub-mode (b) discipline not pre-engineered

- **Claim under review** (mission-brief AC #5 + design.md "What's reused"): "one new 6-column row appended"
- **Issue**: No enumeration of which specific `pytest` selectors row #60's Command cell will reference. Without enumeration in design.md, the Builder will guess at build time and the eventual catalog row + `test_code_review_dogfood_row_runs_clean` SRSC-1 test will be uncoordinated. Per PTFCD-1 (slice-024) + PTFFD-1 (slice-037): every `tests/<...>.py` token in row #60's Command cell must resolve to an existing file AND function. Design names 16 test functions across 11 test files but doesn't say which subset row #60 covers.
- **Evidence**: shippability rows #56/#57/#59 each enumerate 3-5 specific pytest selectors; `tools/shippability_path_audit.py` enforces PTFCD-1 path-existence at Step 5.5.
- **Proposed fix**: Add to design.md a new "## Shippability catalog row #60 design" sub-section: (a) BCR-1-traceability-axis claim (cite CRSI-1 + OSDG-1/CAD-1 lineage anchors); (b) regression-tripwire description (silent breakage: skill+agent forward-sync, v0.64.0 entry-pin, chain extension, install_audit canonical tuples); (c) Command-cell pytest selector list — minimum: `test_in_repo_and_installed_code_review_skill_md_are_content_equal`, `test_in_repo_and_installed_code_review_agent_md_are_content_equal`, `test_v_0_64_0_crsi_1_entry_present_in_repo`, `test_canonical_chain_includes_code_review_edge`, `test_self_dogfood_produces_code_review_md_on_slice_060`; (d) row's expected runtime <3s.
- **Builder draft**: **ACCEPTED-FIXED** at design.md (new "## Shippability catalog row #60 design" sub-section) — SCPD-1 sub-mode (b) proactive-application; PTFCD-1 + PTFFD-1 path/function existence pre-engineered.

### Minors (log; address if cheap)

#### m1: "all 8" references in v0.41.0 changelog entry are historical; future readers may be confused by chain length mismatch

- **Issue**: SUP-1 append-only forbids editing v0.41.0 in place. The new v0.64.0 entry should explicitly bridge-note the 8→9 chain transition.
- **Evidence**: `methodology-changelog.md:368, 374, 383`; SUP-1 append-only.
- **Proposed fix**: Add to v0.64.0 changelog entry body: "Extends the PCA-1 canonical chain from 8 → 9 covered skills by inserting `/code-review` between `/build-slice` and `/validate-slice`; the v0.41.0 entry's '8 covered skills' phrasing is preserved verbatim as historical record (SUP-1 append-only)."
- **Builder draft**: **ACCEPTED-FIXED** at design.md (changelog entry design spec adds bridge sentence) — single-sentence cost; preserves historical coherence per SUP-1.

#### m2: design.md conflates a pytest fixture helper (`_resolve_slice_dir`) with a runtime SKILL.md construct

- **Issue**: `_resolve_slice_dir` lives at `tests/methodology/conftest.py:20` — pytest collection helper. The /code-review SKILL.md is read by Claude at runtime; it cannot "use" a Python helper.
- **Evidence**: `tests/methodology/conftest.py:20`; `skills/critique/SKILL.md:53` shows the canonical SKILL-prose pattern ("Find active slice folder").
- **Proposed fix**: Replace design.md "Active slice folder via `_resolve_slice_dir(NNN)` pattern (slice-056 helper)" with "Find active slice folder per the standard SKILL-prose pattern (check `architecture/slices/_index.md` 'Currently active slice', else stat `architecture/slices/slice-*/` for one stage-active milestone.md)". Mention `_resolve_slice_dir` ONLY in test-side context.
- **Builder draft**: **ACCEPTED-FIXED** at design.md (Prerequisite reads sub-section) — runtime/test layer conflation eliminated.

#### m3: AI-bloat signature framing slightly oversells — SC-022/SC-025 are single-slice dead-code, not multi-slice-compounding

- **Issue**: SC-022 / SC-025 are "defined-never-called" detectable on a single slice's diff; they don't "compound silently". SC-017 is the genuinely multi-slice case.
- **Evidence**: `diagnose-out/backlog.md` lines 522, 470; SC-022/025 are single-slice dead-code defects.
- **Proposed fix**: Trim ADR-059 Context paragraph 4 to acknowledge two failure classes: (a) dead-code persists at slice of introduction (SC-022, SC-025) — per-slice review at lag 1 addresses; (b) multi-impl parallel-copy duplication compounds across slices (SC-017) — cross-slice rumination at slice-061 addresses.
- **Builder draft**: **ACCEPTED-FIXED** at ADR-059 Context — more accurate failure-class framing; preserves the slice-060/061/062 split rationale.

#### m4: WebSearch known-bug context — `allowed-tools` in skill frontmatter has open enforcement issues (Issue #18837); subagent frontmatter IS hard-enforced

- **Issue**: Per [Claude Code Issue #18837](https://github.com/anthropics/claude-code/issues/18837), skill-frontmatter `allowed-tools` enforcement has known issues. But subagent `tools:` frontmatter IS hard-enforced per Tembo's 2026 subagent guide + Claude Code docs. The design's "the **only** access-control surface" claim is load-bearing; design should cite the relevant docs.
- **Evidence**: [Claude Code docs / Create custom subagents](https://code.claude.com/docs/en/sub-agents); GitHub anthropics/claude-code#18837; [Tembo 2026 subagent guide](https://www.tembo.io/blog/claude-code-subagents).
- **Proposed fix**: Append to ADR-059 "Read-only stance" decision: "Read-only enforcement relies on Claude Code's subagent-frontmatter `tools:` field being a hard runtime constraint (per Claude Code docs / Create custom subagents; confirmed via Tembo's 2026 subagent guide). Skill-frontmatter `allowed-tools` enforcement has known issues (GitHub anthropics/claude-code#18837) — this slice uses subagent frontmatter, not skill frontmatter, for the access-control surface."
- **Builder draft**: **ACCEPTED-FIXED** at ADR-059 Decision section ("Read-only stance" sub-clause) — 2-sentence platform-evidence citation; load-bearing safety claim now has audit-trail.

## Dimensions checked

- [x] **Unfounded assumptions** — B1, B2, B3, B4, B5; M1
- [x] **Missing edge cases** — M3; m2
- [x] **Over-engineering** — none. Walking-skeleton scope is well-bounded; explicit deferrals to slices 061/062.
- [x] **Under-engineering** — M1, M2, M4, M5
- [x] **Contract gaps** — M2 (integration-test contract under-specified; cannot drive LLM from pytest)
- [x] **Security** — m4 (load-bearing read-only-tools claim should cite platform docs)
- [x] **Drift from vault** — m1 (v0.41.0 historical phrasing should be bridge-noted in v0.64.0)
- [x] **Web-known issues** — m4 (WebSearch surfaced #18837 skill-frontmatter enforcement bug; subagent frontmatter is hard-enforced per docs)
- [x] **Cross-cutting conformance** — M1, M4, M5 (methodology-audit conformance); B5 (FBCD-1 sub-mode (a) + SCPD-1 sub-mode (b)); B4 (FBCD-1 3-site cross-file drift); M2 (RPCD-1 runtime-prerequisite completeness); B3 (PTFCD-1 / PTFFD-1 phantom-path); RSAD-1 recursive self-application (the new /code-review agent will catch B4-class contradictions on future slices' diffs)

## Builder draft summary

All 14 findings drafted **ACCEPTED-FIXED** — recompute-don't-trust discharged via 7 file-grounded verifications (install_audit.py alphabetical order, pyproject.toml:20 version, tests/agents/ existence, tests/skills/code_review/ existence, 6 hardcoded "8" sites, shippability row #27 Command cell, `_resolve_slice_dir` location). Fixes apply to:
- mission-brief.md: AC #2 + AC #5 + must-not-defer #2 + TF-1 plan (rename row 15 + add 2 chain-update rows + add `__init__.py` pre-rows) + What's new
- design.md: 14 surfaces (alphabetical insertion, 5-part bump, phantom directories, tool count, 6×"8" sites + SCPD-1 row #27 propagation, new "## 9 dimensions reframed for code" section, new "## Build-phase sequence" section, diff-source in-scope enumeration, v0.64.0 entry-pin substring enumeration + test rename, new "## Shippability catalog row #60 design" sub-section, changelog bridge sentence, `_resolve_slice_dir` test-side scoping)
- ADR-059: Context para 4 trim, Consequences 5-part-bump update, "Read-only stance" platform-evidence citation

Per TPHD-1: M4 + B5 cause TF-1 plan changes (row 15 rename + 2 new rows); all TF-1 harmonization happens in the same fix block.

## Triage

**Triaged by**: user
**Date**: 2026-05-23
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md "Components touched / tools/install_audit.py (MODIFY)" — alphabetical insertion targets corrected |
| B2 | Blocker | ACCEPTED-FIXED | mission-brief AC#5 + design.md "What's reused" + ADR-059 Consequences item 10 — 5-part PMI-1 bump now enumerates pyproject.toml leg |
| B3 | Blocker | ACCEPTED-FIXED | design.md "What's new" + mission-brief "Prerequisite directory creates" — `tests/agents/__init__.py` + `tests/skills/code_review/__init__.py` plan-steps added |
| B4 | Blocker | ACCEPTED-FIXED | mission-brief AC#2 + must-not-defer #2 + design.md agent invocation contract — 5 tools (Read/Glob/Grep/Bash/WebSearch); positive+negative test contract pinned |
| B5 | Blocker | ACCEPTED-FIXED | design.md "Components touched / tools/pipeline_chain_audit.py" — all 6 hardcoded "8" sites enumerated; TF-1 plan rows 9-10 are UPDATE rows; SCPD-1 row #27 propagation noted in "What's reused" |
| M1 | Major | ACCEPTED-FIXED | design.md new "## 9 dimensions reframed for code" section — per-dimension reframing table + content-bearing test spec (slice-051 / slice-037 M-add-1 discipline) |
| M2 | Major | ACCEPTED-FIXED | design.md new "## Build-phase sequence" section A→B→C→D→E + TF-1 row 3 reclassified `integration → unit` + new must-not-defer item enforcing phase ordering |
| M3 | Major | ACCEPTED-FIXED | design.md Diff source contract — 5 in-scope path categories enumerated; `skills/**/SKILL.md` explicitly in-scope (RSAD-1 self-application proof) |
| M4 | Major | ACCEPTED-FIXED | mission-brief TF-1 row 15 + design.md "What's new" — renamed to `test_v_0_64_0_crsi_1_entry_present_in_repo` + 8 substring assertions enumerated (slice-059 precedent) |
| M5 | Major | ACCEPTED-FIXED | design.md new "## Shippability catalog row #60 design" sub-section — 6 selectors + tripwire description + runtime budget + BC-PROJ-7 pipe-escape discipline |
| m1 | Minor | ACCEPTED-FIXED | design.md "What's reused" methodology-changelog row — v0.64.0 entry will include 8→9 bridge sentence; SUP-1 preserves v0.41.0 verbatim |
| m2 | Minor | ACCEPTED-FIXED | design.md Prerequisite reads — runtime/test layer separated; `_resolve_slice_dir` cited only in test-side context |
| m3 | Minor | ACCEPTED-FIXED | ADR-059 Context para 4 — two-class framing (dead-code-persists / multi-impl-compounds) replaces oversold "compound silently" language |
| m4 | Minor | ACCEPTED-FIXED | ADR-059 "Read-only stance" — 2-sentence platform-evidence citation (subagent frontmatter hard-enforced; skill-frontmatter #18837 not applicable here) |
| M-add-1 | Major (meta) | ACCEPTED-FIXED | design.md "## Build-phase sequence" Phase B — `cp skills/build-slice/SKILL.md` + `cp skills/validate-slice/SKILL.md` added to forward-sync list (Fowler refactoring discipline; slice-049/051 OSDG-1 family-add lineage) |
| M-add-2 | Major (meta) | ACCEPTED-FIXED | mission-brief TF-1 plan + design.md "What's new" + "## Shippability catalog row #60 design" — paired `test_v_0_64_0_crsi_1_shippability_consumer_propagation` test added (BC-PROJ-10:173 verbatim; N≥17 pair-precedent) |
| m-add-1 | Minor (meta) | ACCEPTED-FIXED | design.md Dim 9 reframe entry — split clarifying PTFCD-1 sub-mode (a) [design-meta, out-of-scope] vs phantom-import-in-`.py`-code [code-as-artifact, in-scope under Dim 1 / Dim 5] |
