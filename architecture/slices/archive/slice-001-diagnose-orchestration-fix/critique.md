# Critique: Slice 001 diagnose-orchestration-fix

**Critic reviewed**: mission-brief.md, design.md, ADR-001-diagnose-subagent-io-contract.md
**Date**: 2026-05-09
**Result**: NEEDS-FIXES (pending user triage)

## Summary

Diagnosis of the underlying problem and choice of Option 3 are sound. Test-first plan has good coverage. But the **fenced-block parsing scheme is brittle in ways the design under-acknowledges** — every existing pass template emits prose containing nested triple-backtick fences (markdown tables, YAML examples, bash commands), and `\`\`\`section` / `\`\`\`findings` / `\`\`\`summary` will collide. Two further issues need design clarification before /build-slice writes code: (1) `normalize_finding`'s "drop unknown fields" silently changes `load_findings()` semantics, and (2) the "ID not matching `F-<CAT>-<8hex>` → recomputed" rule can't be implemented faithfully because the schema's hash recipe is per-pass-specific and the orchestrator doesn't know each pass's `signature` definition.

## Findings

### Blockers (must address before /build-slice)

#### B1: Fenced-block delimiters will collide with subagent prose containing nested fences

- **Claim under review**: design.md "Subagent I/O contract" specifies three blocks delimited by ` ```section `, ` ```findings `, ` ```summary `.
- **Issue**: Every existing pass template under `skills/diagnose/passes/` shows the subagent that its prose output should contain nested triple-backtick fences. `passes/02-architecture.md:42-82` shows the section template wrapped in ` ```markdown `. `passes/01-intent.md:38-58` does the same. `passes/03e-contradictions.md:28-36` instructs the subagent to embed inline ` ```bash ... ``` ` snippets in its prose. A subagent following the template will produce a `section` block whose first line is ` ``` ` — the parser treating ` ``` ` as the closing fence will truncate output to empty.

  Independently corroborated by openai/chatkit-js#89, langchain-ai/langchain#8357, continuedev/continue#5427 — nested triple-backticks are a well-documented LLM-output failure class. The `normalize_finding` tolerance is orthogonal (it addresses *findings YAML shape* mistakes, not *fence delimiter collisions*). "Exit 2 → re-spawn" doesn't help: the LLM will deterministically emit nested fences again because the pass templates still contain them.
- **Evidence**: `skills/diagnose/passes/02-architecture.md:42-82`, `passes/01-intent.md:38-58, 62-64`, `passes/03e-contradictions.md:28-36`. design.md "Components touched / passes/*.md" rewrites the "Output files" section but does not remove the embedded fences within the prose template the subagent fills in.
- **Proposed fix**: Pick one of three concrete strategies and pin it in `write_pass.py`'s parser, `passes/*.md` "Output format" sections, and ADR-001 Consequences:
  1. **Length-distinguished outer fences**: outer delimiters are ` ````section ` (4 backticks); content can include normal ` ```bash ` (3 backticks) without conflict (CommonMark: closing fence ≥ opening length).
  2. **Sentinel-line delimiters**: `<<<DIAGNOSE_BLOCK section>>>` / `<<<END_BLOCK>>>` markers — non-markdown — so nested fences inside content are irrelevant.
  3. **Single-block JSON envelope**: subagent returns one ` ```json ` block whose JSON has `{"section": ..., "findings": [...], "summary": ...}`.

  Add a unit test `test_section_block_with_nested_triple_backticks_parses_correctly` covering this case.
- **Builder draft**: ACCEPTED-PENDING — recommend **Option 1 (4-backtick outer fences)**: cheapest, no schema change, parser regex `^\`{4,}(section|findings|summary)\s*$ ... ^\`{4,}\s*$` with backreferenced length. Update design.md "Subagent I/O contract" to specify 4-backtick outer fences. Update all 11 pass templates' "Output format" sections. Update ADR-001 "Consequences" with the choice + nested-fence test added. Open to Option 2 or 3 if you prefer them.

#### B2: `normalize_finding` "ID not matching `F-<CAT>-<8hex>` → recomputed" cannot be faithfully recomputed by the orchestrator

- **Claim under review**: mission-brief AC #3 / design.md: `normalize_finding(raw, pass_name)` recomputes IDs that don't match the schema shape.
- **Issue**: Per `schema/finding.yaml:11-15`, the canonical ID recipe is `F-<CAT>-sha1(category + primary_evidence_path + signature)[:8]`. The `signature` is **per-pass-specific**:
  - `passes/03a-dead-code.md:14`: signature = "the function/class/module name being flagged"
  - `passes/03b-duplicates.md:12`: signature = "the lexicographically smallest path among the duplicates"
  - `passes/03e-contradictions.md:12`: signature = "concept" (a domain entity name)
  - `passes/03c-size-outliers.md:13`: signature = "symbol"
  - `passes/03h-test-coverage.md:12`: signature = "capability"

  With only `raw` + `pass_name`, the function cannot deterministically reproduce the same ID a different subagent (or same subagent on re-run) would produce — `signature` is a free-text string the subagent picked from a per-pass rule. This violates `SKILL.md:18` Hard Rule 4 (stable content-derived IDs for owner-annotation carryover).
- **Evidence**: `schema/finding.yaml:11-15`; per-pass signature definitions in 5 different pass templates; `SKILL.md:18` stable-ID rule.
- **Proposed fix**: Three options:
  1. **Validate-only**: AC #3 changes to "ID malformed → reject; main thread re-spawns the pass". Loses tolerance.
  2. **Per-pass signature extractor table**: small dict `{pass_name: callable(finding) -> str}` in `assemble.py`. ~5 lines of code (most passes use `lambda f: f["title"]`; only 03b needs special logic for "smallest evidence path"). Preserves canonical-recipe carryover.
  3. **Fallback recipe**: drop `signature` when recomputing; use `category + primary_evidence_path + title`. Document in `schema/finding.yaml`. Loses canonical-recipe consistency (recomputed IDs differ from subagent-correct IDs across runs).
- **Builder draft**: ACCEPTED-PENDING — recommend **Option 2 (per-pass signature extractor)**: cheapest preservation of the canonical-recipe carryover guarantee. Add `_signature_extractors: dict[str, Callable[[dict], str]]` to `assemble.py` with default `lambda f: f["title"]` and 1–2 overrides. Rename test `test_malformed_id_recomputed` → `test_malformed_id_recomputed_via_per_pass_extractor`. Add fixture verifying recompute is deterministic across calls. Open to Option 1 (validate-only) if you want simpler error-flow.

### Majors (address this slice)

#### M1: `normalize_finding` "drops unknown fields with logged warning" silently changes `load_findings()` semantics

- **Claim under review**: design.md says `normalize_finding` is shared between `load_findings()` (existing) and `write_pass.py` (new).
- **Issue**: Current `assemble.py:load_findings()` (lines 77-99) enforces minimum schema (REQUIRED_FIELDS) but doesn't reject extra fields. Sharing `normalize_finding` means existing `findings/*.yaml` files with extra fields produce warnings on every load. More worryingly, the carryover path round-trips owner annotations via the embedded JSON in `diagnosis.html`; if `normalize_finding` drops fields it doesn't know, owner annotations could be silently discarded.
- **Evidence**: `assemble.py:77-99`; `SKILL.md:9, 161` owner-annotation-carryover model.
- **Proposed fix**: Only call `normalize_finding` from `write_pass.py` (ingest-time), not from `load_findings` (load-time). Load remains strict. Add test `test_load_findings_unchanged_for_already_normalized_yaml`.
- **Builder draft**: ACCEPTED-PENDING — apply the proposed fix. Update design.md "Components touched / assemble.py" to clarify: `normalize_finding` is ingest-only; `load_findings` retains current strictness.

#### M2: AC #4 "±2 lines context" cannot be produced from `yaml.YAMLError.problem_mark` for all subtypes

- **Claim under review**: AC #4 says yaml load failures print line/column from `yaml.YAMLError.problem_mark`.
- **Issue**: `problem_mark` is on `MarkedYAMLError`, not bare `yaml.YAMLError`. Some subtypes don't set it. Naive `exc.problem_mark` raises `AttributeError`, masking the real YAML error.
- **Evidence**: PyYAML `yaml/error.py` — `MarkedYAMLError(YAMLError)` defines `problem_mark`; not every `YAMLError` does.
- **Proposed fix**: Gate access on `getattr(exc, 'problem_mark', None)`; fallback message when missing. Add second test `test_yaml_error_without_problem_mark_falls_back_gracefully`.
- **Builder draft**: ACCEPTED-PENDING — apply the proposed fix.

#### M3: Re-spawn loop has no bounded retries

- **Claim under review**: design.md "Error model" — `write_pass.py` non-zero → re-spawn (extends Step 5.5's existing semantics). No retry cap.
- **Issue**: If subagent deterministically emits malformed output (e.g., B1's fence collision), `/diagnose` loops forever.
- **Evidence**: `SKILL.md:115`; design.md "Error model" — neither names a cap.
- **Proposed fix**: SKILL.md Step 5 prose: "re-spawn at most twice (3 total attempts); if still failing, save raw to `$OUT/.tmp/<pass>.failed.raw` and continue with degraded findings. Pass-level degradation noted in `assemble.py` output." Add prose-pin test `test_skill_md_caps_respawn_attempts`.
- **Builder draft**: ACCEPTED-PENDING — apply the proposed fix.

#### M4: AC #2 stdin path is part of contract but no test covers stdin

- **Claim under review**: AC #2 says `write_pass.py` reads from stdin OR `--raw-file`. Test-first plan has no stdin test.
- **Issue**: SKILL.md Step 5's actual invocation uses `--raw-file` only. Stdin support is untested code. YAGNI + contract gap.
- **Evidence**: mission-brief Test-first plan; design.md "CLI contract".
- **Proposed fix**: Drop stdin support. `--raw-file` is the only path the orchestrator uses. Update mission-brief AC #2 + design.md "CLI contract" to specify `--raw-file` only.
- **Builder draft**: ACCEPTED-PENDING — apply the proposed fix (drop stdin). YAGNI confirmed.

#### M5: AC #5 prose vs actual fix scope mismatch

- **Claim under review**: AC #5 says "no pass template under `passes/` uses `--output` either".
- **Issue**: Pass templates currently use `--graph`, not `--output`, in their graphify invocations. Only `SKILL.md:55` uses `--output`. The "no pass template uses `--output`" prose-pin test passes trivially today; the Builder might mistakenly edit 11 pass templates believing AC #5 requires it.
- **Evidence**: Grep `--output` in `skills/diagnose/`: only `SKILL.md:55` matches.
- **Proposed fix**: Add to design.md "Pass templates" section: "AC #5 already holds for `passes/*.md` (none use `--output`); only `SKILL.md` Step 3 line 55 needs the change."
- **Builder draft**: ACCEPTED-PENDING — apply the doc clarification to design.md as part of build.

#### M6: ADR-001 "main-thread context grows by ~50–100KB" — unsourced, likely under-counted

- **Claim under review**: ADR-001 Consequences cites 5–10KB per pass × 11 passes = 50–100KB.
- **Issue**: Realistic Opus-quality output for 02-architecture's section alone is 8–25KB; 03b-duplicates can emit 30+ findings × ~250 bytes = 7-10KB just in findings YAML. Realistic upper bound is 200–400KB. Schema embed (m2) doubles the cost. Under-counting in ADR weakens calibration loop.
- **Evidence**: `passes/02-architecture.md:42-82` (size of expected output); ADR-001 Consequences.
- **Proposed fix**: Widen estimate to "10–40KB per pass × 11 = 100–440KB; acceptable but worth measuring at first run". Add measurement task to slice-002 or mission-brief: instrument subagent result-text byte counts; record in reflection.md.
- **Builder draft**: ACCEPTED-PENDING — apply the widened estimate + measurement task. Also add the Critic's "Option 4 (declare subagent tool needs at spawn time so user is prompted up-front)" to ADR-001 "Options considered" for completeness, even though rejected.

### Minors (log; address if cheap)

#### m1: Empty-block test under-specified

- **Issue**: Only one test (`test_empty_findings_block_treated_as_empty_list`) covers the empty case. Doesn't cover whitespace-only, `null`, comment-only, `[]` literal.
- **Proposed fix**: Parametrize the test with 5 input variants. Cheap.
- **Builder draft**: ACCEPTED-PENDING — apply the parametrization.

#### m2: Schema embed is duplicated 11× across pass prompts

- **Issue**: Schema is ~3KB; embedding in 11 subagent prompts wastes ~30KB tokens per /diagnose run. A 5-line crib sheet (~500 bytes) would do.
- **Proposed fix**: Replace full-schema embed with a 5-line crib sheet naming required fields with one example.
- **Builder draft**: ACCEPTED-PENDING — apply the crib sheet swap. Reduces M6's context cost.

#### m3: AC #1 prose-pin needs a negative-assertion test

- **Issue**: Current pin test asserts SKILL.md *invokes* `write_pass.py`. Doesn't verify SKILL.md tells subagents NOT to use Write. A subagent prompt saying "use Write AND return fenced blocks" would still pass.
- **Proposed fix**: Add `test_skill_md_subagents_instructed_no_write` — assert phrase like "do NOT call Write" appears in Step 5 prose, AND substring "writes 3 files" does NOT appear (it's there today at SKILL.md:97-101).
- **Builder draft**: ACCEPTED-PENDING — apply the new test.

#### m4: AC #1 verification "inspecting" is unspecific

- **Issue**: "Verified by inspecting one subagent invocation end-to-end" — what does the inspector look for, in what artifact, with what pass/fail?
- **Proposed fix**: Reword to scriptable form: "Capture one subagent's raw response to `$OUT/.tmp/<pass>.raw`; Grep verifies (a) exactly the three expected fences, (b) zero `Write(` references, (c) `write_pass.py --raw-file ...` exits 0 and produces three files."
- **Builder draft**: ACCEPTED-PENDING — apply the reworded AC #1 verification.

## Dimensions checked

- [x] **Unfounded assumptions** — B2 (recompute), M2 (`problem_mark` always present), M6 (50-100KB estimate unsourced)
- [x] **Missing edge cases** — B1 (nested fences), M3 (no retry cap), m1 (empty-block variants)
- [x] **Over-engineering** — M4 (untested stdin path; YAGNI), m2 (full-schema embed × 11)
- [x] **Under-engineering** — m3 (no negative-assertion test for AC #1), M5 (prose vs scope mismatch)
- [x] **Contract gaps** — B1 (delimiter contract unsafe), B2 (ID-recompute contract impossible), M4 (untested CLI path)
- [x] **Security** — none. Slice strictly *reduces* subagent permissions
- [x] **Drift from vault** — none. ADR-001 is the first ADR; design.md correctly references code (thin vault)
- [x] **Web-known issues** — corroborated B1 (openai/chatkit-js#89, langchain-ai/langchain#8357, continuedev/continue#5427); confirmed ADR-001 premise via Claude Code subagent permission docs; surfaced Option 4 (explicit tool-needs at spawn time) for ADR completeness

Sources cited by Critic:
- https://github.com/openai/chatkit-js/issues/89
- https://github.com/langchain-ai/langchain/issues/8357
- https://github.com/continuedev/continue/issues/5427
- https://github.com/anthropics/claude-code/issues/57037
- https://code.claude.com/docs/en/sub-agents
- https://platform.claude.com/docs/en/agent-sdk/permissions

## Triage

**Triaged by**: user
**Date**: 2026-05-09
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-PENDING | Apply Option 1 (4-backtick outer fences) during /build-slice. Update design.md "Subagent I/O contract" + 11 pass templates' "Output format" sections + ADR-001 Consequences. Add nested-fence parser test. |
| B2 | Blocker | ACCEPTED-PENDING | Apply Option 2 (per-pass signature extractor) during /build-slice. Add `_signature_extractors` dict to `assemble.py` with default `lambda f: f["title"]` + override for 03b-duplicates. Update mission-brief AC #3 + design.md normalize_finding spec + test name. |
| M1 | Major | ACCEPTED-PENDING | Call `normalize_finding` only from `write_pass.py` (ingest-time); `load_findings()` retains current strictness. Update design.md "Components touched / assemble.py". Add `test_load_findings_unchanged_for_already_normalized_yaml`. |
| M2 | Major | ACCEPTED-PENDING | Use `getattr(exc, 'problem_mark', None)` fallback in `assemble.py:load_findings()` exception handler. Add `test_yaml_error_without_problem_mark_falls_back_gracefully`. |
| M3 | Major | ACCEPTED-PENDING | SKILL.md Step 5: cap re-spawn at 3 attempts; on terminal failure save raw to `$OUT/.tmp/<pass>.failed.raw` and degrade pass. Add `test_skill_md_caps_respawn_attempts` prose-pin. |
| M4 | Major | ACCEPTED-PENDING | Drop stdin support from `write_pass.py`; `--raw-file` only. Update mission-brief AC #2 + design.md "CLI contract for write_pass.py". |
| M5 | Major | ACCEPTED-PENDING | Add note to design.md "Pass templates": pass templates use `--graph`, not `--output`; AC #5 already trivially holds for them; only SKILL.md:55 needs the flag change. |
| M6 | Major | ACCEPTED-PENDING | Widen ADR-001 cost estimate to 100-440KB + add measurement task to reflection.md. Also append Critic's "Option 4 (declare subagent tool needs at spawn time)" to ADR-001 "Options considered". |
| m1 | Minor | ACCEPTED-PENDING | Parametrize `test_empty_findings_block_treated_as_empty_list` with 5 inputs: empty string, whitespace-only, `[]` literal, comment-only, `null`. |
| m2 | Minor | ACCEPTED-PENDING | Replace full-schema embed (~3KB × 11) with a 5-line crib sheet (~500 bytes) in pass templates. Reduces M6 cost. |
| m3 | Minor | ACCEPTED-PENDING | Add `test_skill_md_subagents_instructed_no_write` — assert phrase "do NOT call Write" appears in Step 5 AND substring "writes 3 files" does NOT. |
| m4 | Minor | ACCEPTED-PENDING | Reword mission-brief AC #1 verification to scriptable form: capture raw response, Grep for fences + zero `Write(` references + `write_pass.py` exit 0 + 3 files produced. |
