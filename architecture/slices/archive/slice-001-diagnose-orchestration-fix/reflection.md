# Reflection: Slice 001 diagnose-orchestration-fix

**Date**: 2026-05-09
**Shipped**: YES

## Validated

- **4-backtick fence parser handles real subagent output** — validated by AC #6 end-to-end /diagnose on `<HOME>/<private-project>`. Three subagents (01-intent, 02-architecture, 03b-duplicates) returned messages with prose preambles followed by 4-backtick fenced blocks; the parser correctly ignored the preamble and extracted all three blocks (`section`, `findings`, `summary`).
- **`yaml.safe_dump` eliminates the unquoted-colon bug class** — validated by `test_yaml_safe_dump_quotes_colons` plus the AC #6 run's `findings: []` payloads round-tripping cleanly.
- **`normalize_finding` is correctly scoped to ingest-only (M1)** — validated by `test_load_findings_unchanged_for_already_normalized_yaml`; existing findings YAMLs from any prior run remain unaffected on load.
- **Per-pass signature extractor table (B2) recomputes IDs deterministically** — validated by `test_malformed_id_recomputed_via_per_pass_extractor` (run-to-run determinism asserted).
- **`problem_mark` getattr fallback (M2) prevents AttributeError on bare `YAMLError`** — validated by `test_yaml_error_without_problem_mark_falls_back_gracefully`.
- **3-attempt retry cap with `.failed.raw` artifact (M3) — exercised in production for the first time** — pass 03a-dead-code returned no fences in AC #6; `write_pass.py` exited 2 with stderr naming the missing fences; `.failed.raw` was preserved per design; the orchestrator did not loop forever or silently produce junk. Validation evidence > unit-test evidence here.
- **Stdin-removal (M4) is correctly minimal** — orchestrator used `--raw-file` exclusively in AC #6; stdin would have been YAGNI dead code.
- **Schema crib sheet (m2) is sufficient for subagents** — Opus subagents in AC #6 produced contract-conformant `findings: []` blocks using only the 5-line crib, not the full 3 KB schema. Saves ~30 KB per /diagnose run as predicted.
- **TF-1 strict gate at 18 PASSING rows** — validated test-first discipline through the build; no row degraded between WRITTEN-FAILING and PASSING.
- **Source-independent install (INST-1) survives the new module** — `install_audit --strict` clean post-build; 24 / 5 / 4 / 14 inventory still matches.
- **Critic ROI on a low-tier slice** — running `/critique` voluntarily on a `risk-tier: low` slice paid off concretely: B1 (nested fences) and B2 (impossible ID recompute) were real blockers the design glossed over. Worth doing again on future low-tier slices that introduce non-trivial new internal contracts.

## Corrected

- **Contract over-reach: "Do NOT call Bash or python" was too strict.** This design said it; SKILL.md Step 5 says it; all 11 pass templates' Output format sections say it. But every pass template's Method section requires Bash/python for graphify queries (`$PY -m graphify orphans`, `$PY -m graphify reachable`, `$PY -m graphify topo-sort`, `$PY -c "import networkx ..."`). The contract contradicts itself. Discovered when constructing AC #6 subagent prompts — had to override per-prompt with "no Write to produce output files; Bash/python ALLOWED for graphify within OUT/graphify-out/." Annotated in this slice's [`design.md`](design.md) at the top; capturing here for the methodology trail. Fix is a slice-002 candidate (relax the wording in SKILL.md + 11 pass templates uniformly).
- **ADR-001 cost estimate "50–100 KB" was already corrected during build (M6 → 100–440 KB)** — validation confirmed the upper end is realistic. The 02-architecture pass alone produced an 11 KB section in AC #6. M6's correction is a hit.

## Discovered

- **Cwd-mismatch tool denial for spawned subagents** — when TARGET ≠ parent thread cwd, spawned `general-purpose` subagents lose Read / Grep / Bash / PowerShell access entirely; only Glob remains. Slice-001 was built and unit-tested with TARGET = parent cwd (the AI SDLC repo itself); validation was the first time TARGET pointed to a sibling directory (`<private-project>`), and the new permission boundary surfaced. **Added to risk-register.md as R1.** Three fix paths surfaced (documented constraint, orchestrator pre-cd, parent-thread pre-compute) — slice-002 candidate.
- **Opus vs Sonnet resilience differential under tool denial** — three Opus subagents (01-intent, 02-architecture, 03b-duplicates) improvised with Glob alone and produced contract-compliant output (one with rich filename-based analysis, two with honest empty-findings explanations). One Sonnet subagent (03a-dead-code) gave up entirely. This affects COST-1.1 model routing: extraction-shaped passes routed to Sonnet may be especially fragile under environmental tool restrictions. Doesn't necessarily mean re-route everything to Opus — degraded passes are the design's intended fallback — but worth flagging for slice-002 if cwd-mismatch can't be cleanly fixed.
- **Subagent prose preambles are common.** All three Opus subagents in AC #6 wrote a paragraph of explanation before the fenced blocks ("Read/Grep/Bash all denied — but Glob works..." / "Good. I now have enough evidence..."). The 4-backtick parser handles this correctly (greedy match on opener, ignores preamble), but prose preambles are now a confirmed-real-world pattern, not just a theoretical one. The fence-collision tolerance was earned, not over-engineered.
- **`textwrap.dedent` + f-string interpolation is a fixture footgun.** Build phase 4 had three test fixtures fail because `dedent` doesn't strip the outer indentation when the interpolated content has lines at column 0 (the minimum-leading-whitespace algorithm finds 0 and bails). Rewrote the fixtures with explicit string concatenation. Trivial fix once spotted; recorded as a generic Python-test-fixture anti-pattern (see lessons-learned).
- **PowerShell `@"..."@` (double-quoted here-string) eats backticks.** Build phase 4 manual smoke initially failed because the here-string treated backticks as escape characters. Fix: use single-quoted `@'...'@`. Generic Windows tooling lesson.

## Deferred

- **Slice-002 candidate: cwd-mismatch tool denial fix** — three approaches outlined in validation.md "Reality surprises". Highest-leverage discovery from this slice.
- **Slice-002 candidate: relax "no Bash/python" contract wording in SKILL.md + 11 pass templates** — addresses the design correction above. Could be folded into the cwd-mismatch fix slice if the fix involves restructuring the contract anyway.
- **Slice-002 candidate: VAL-1 Layer B `--imports-allowlist` flag** — surfaced during this slice's validate run (6 internal imports flagged: `assemble`, `tests`). Minor; only matters when a project ships scripts-not-packages, but that's exactly what skills do.
- **Full <private-project> diagnostic** — would require re-running /diagnose from inside the target's cwd (per the documented-constraint workaround). Not a slice; just a runtime task for the user when they want a real diagnosis of that codebase.

## Critic calibration

Per TRI-1, scoring each finding from `critique.md` `## Triage` against build + validate reality:

- **B1** (Fenced-block delimiters collide with nested fences): **VALIDATED** — disposition ACCEPTED-PENDING; reality (the AC #6 subagents) didn't trigger the specific collision in this run, but `test_section_block_with_nested_triple_backticks_parses_correctly` proved it would have broken under realistic subagent output. The 4-backtick design held cleanly. Critic was right; the fix earned its keep.
- **B2** (`normalize_finding` ID recompute structurally impossible): **VALIDATED** — disposition ACCEPTED-PENDING; the per-pass extractor pattern is in production. Not exercised in AC #6 (all returned subagents emitted `[]` findings, so no IDs to recompute), but unit tests confirm the design works. Critic spotted a real impossibility that would have shipped silent ID-collisions otherwise.
- **M1** (`normalize_finding` shouldn't be shared with `load_findings`): **VALIDATED** — load path strictness preserved; no warning-spam on existing YAMLs.
- **M2** (`problem_mark` may be missing on bare `YAMLError`): **VALIDATED** — defensive `getattr` fallback in production; unit test confirms the path.
- **M3** (re-spawn loop has no retry cap): **VALIDATED** — actually triggered in AC #6 when 03a-dead-code gave up. Without M3, that pass would have looped forever on a deterministic-give-up subagent. Real-world hit.
- **M4** (untested stdin path is YAGNI): **VALIDATED** — orchestrator used `--raw-file` exclusively in AC #6; stdin would have been pure dead code.
- **M5** (AC #5 prose vs scope mismatch): **VALIDATED** — design.md note prevented wasted edits to 11 pass templates "for AC #5".
- **M6** (ADR-001 cost estimate under-counted): **VALIDATED** — 02-architecture's section block alone was 11 KB; original 50–100 KB estimate would have been embarrassingly low.
- **m1** (parametrized empty-block test): **VALIDATED** — caught the trailing-newline bug in the `[]` parameter during build (would have shipped as a flaky edge case).
- **m2** (schema crib sheet vs full embed): **VALIDATED** — Opus subagents produced contract-compliant output from the crib alone in AC #6.
- **m3** (no-Write prose-pin negative assertion): **VALIDATED** — prevents regression of the very behavior this slice introduced.
- **m4** (AC #1 verification reword): **VALIDATED** — gives a concrete pass/fail.

**Missed by Critic — important:**
- **Cwd-mismatch tool denial** — the Critic reviewed slice-001 design and didn't flag that subagents might lose tools when TARGET ≠ parent cwd. The Critic's prompt has 8 dimensions; "environmental / runtime permission boundaries" doesn't map cleanly to any of them. The miss was honest — the failure mode was hidden behind a context switch (TARGET vs cwd) that's only visible at end-to-end runtime, not at design review.
- **Contract self-inconsistency** (no-Bash/python in pass-template Output sections vs Bash-required Method sections) — the Critic reviewed design.md + ADR-001 + critique-target prose. It didn't dig into all 11 pass templates to spot the contradiction. The B1/B2/m2 findings show the Critic was rigorous within the slice's *new* scope; the *legacy* contradiction in pre-existing templates slipped through.

**Missed by Critic — minor:**
- **Opus vs Sonnet resilience differential** — Critic could have flagged "the new orchestration relies on subagents being smart enough to improvise under tool denial; COST-1.1's model routing puts extraction-shaped passes on Sonnet which may be too narrow for this." Not a blocker — degraded passes are the intended fallback — but a calibration opportunity.

**Pattern**: Critic was strong on **internal technical consistency** (8/12 findings were within-slice technical issues — fence parsing, ID recompute, normalize scope, retry semantics, doc accuracy) but missed **environmental / operational concerns** that only surface at end-to-end runtime. Consider adding a "Runtime / environment / cwd / permissions" dimension to the Critic prompt — see `/critic-calibrate` candidate.

## Lessons for next slice

- **/diagnose is most useful when invoked from inside the target's cwd.** Document this as a usage constraint until slice-002 lands. The default-to-PWD behavior in SKILL.md Step 1 already supports this — just needs a callout.
- **End-to-end validation reveals a different class of bugs than unit tests.** AC #6 found two issues (contract over-reach, cwd-mismatch) that no unit test could have surfaced. For future slices that touch agent / subagent orchestration, prioritize at least one real-environment smoke as part of validation.
- **Voluntary Critic on low-tier slices is worth it** when the slice introduces a non-trivial new internal contract, even if not strictly required by methodology. The 12 findings translated to 12 real improvements; ROI was clearly positive.
- **For Python test fixtures with multi-line interpolation: use explicit string concatenation, not `textwrap.dedent` + f-string.** The minimum-leading-whitespace algorithm of `dedent` doesn't dedent correctly when interpolated content has lines at column 0.
- **For PowerShell here-strings holding LLM-protocol content (backticks): use single-quoted `@'...'@`, not double-quoted `@"..."@`.** PowerShell's escape character is the backtick; double-quoted here-strings will eat them.

## Vault updates made (thin vault)

- [`risk-register.md`](../../risk-register.md) — created; added R1 (cwd-mismatch tool denial)
- [`lessons-learned.md`](../../lessons-learned.md) — created; appended slice-001 entry
- [`shippability.md`](../../shippability.md) — created; appended this slice's critical-path test
- This slice's [`design.md`](design.md) — added a Reflection-corrected note about the contract over-reach (no edits to ADR-001; the cost-estimate correction was already part of M6 during build)
- This slice's [`build-log.md`](build-log.md) — appended deviation + finding events from AC #6
- No ADRs superseded — ADR-001 still stands as decided; the contract-wording issue is a slice-level fix in SKILL.md + pass templates, not an architectural decision change.
