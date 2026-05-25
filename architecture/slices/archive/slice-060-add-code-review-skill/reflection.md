# Reflection: Slice 060 add-code-review-skill

**Date**: 2026-05-23
**Shipped**: YES-WITH-DEFERRALS (CRSI-1 walking-skeleton fully delivered; M1+M2 self-discovered → slice-061; bootstrap-discharge per slice-026/027 precedent)

## Validated

- **9 dimensions reframed for CODE work as designed**: `agents/code-review.md` carries all 9 dimensions with content-bearing substring anchors per slice-051 / slice-037 M-add-1 discipline; `test_agent_md_contains_nine_dimensions_against_code` passes with 11 reframe anchors verified.
- **PCA-1 chain extension is functional**: `_CANONICAL_CHAIN` extended from 8 → 9 entries; live audit exits 0 (`PCA-1 audit: clean. 9 skills checked; pipeline chain matches canonical loop`); the chain wiring is `build-slice → /code-review → /validate-slice` with auto-advance: true throughout.
- **5-part PMI-1 atomic bump works in lock-step**: VERSION + plugin.yaml + pyproject.toml + `~/.claude/ai-sdlc-VERSION` + `~/.claude/methodology-changelog.md` all at 0.64.0 verified by AVFS-1 + MCFS-1 + TVFS-1 + PVFS-1 all exit 0; INST-1 reports `methodology v0.64.0` across 26/26 skills + 6/6 agents + 4/4 templates + 27/27 tool modules.
- **OSDG-1 + CAD-1 family-add pattern extends cleanly to slice-060**: `tests/methodology/test_code_review_skill_drift.py` + `test_code_review_agent_drift.py` both reuse `tests/skill_drift_equality.py::assert_md_forward_synced` verbatim (no new byte-equality comparator; EOL-DRIFT-1 / R-5 retirement preserved); both PASS post-Phase B forward-sync.
- **6-selector shippability row #60 validates**: SCMD-1 (`60 row(s); 542 cited fn(s) — incidental=0`), PTFCD-1/PTFFD-1 (`60 row(s), 319 test-path token(s) — all files and cited functions exist`), SRSC-1 runner (`60/60 PASS`).
- **Bootstrap-discharge per slice-026 / slice-027 precedent N=3**: agent file + skill file installed + chain wired + drift guards + tests + shippability row provide structural discharge; the FIRST real `/code-review` invocation will land at slice-061's `/build-slice` → `/code-review` auto-advance edge.

## Corrected

- **5-part vs 4-part PMI-1 atomic bump** (drafted 4-part, corrected to 5-part) — first Critic B2 caught the missing `pyproject.toml [project].version` leg; PVFS-1 (slice-054) was not in the original draft's bump enumeration. Updated in mission-brief AC #5 + design.md "What's reused" + ADR-059 Consequences before /build-slice.
- **TF-1 row count 18 → 19** — meta-Critic M-add-2 caught the missing BC-PROJ-10:173 paired `_shippability_consumer_propagation` test (N≥17 pair-precedent stable across the changelog test module). Updated mission-brief TF-1 plan + design.md "What's new" + shippability row #60 Command-cell selector list (5 → 6 selectors).
- **Phase B forward-sync list incomplete** — meta-Critic M-add-1 caught omission of `cp skills/build-slice/SKILL.md` + `cp skills/validate-slice/SKILL.md` from Phase B. Without these, the parametrized `test_pipeline_position_block_byte_equal_in_repo_vs_installed` over 9 `_CANONICAL_CHAIN` skills would have FAILed for build-slice + validate-slice at Phase D/E. Fix applied: design.md "## Build-phase sequence" Phase B expanded to enumerate all 4 SKILL.md cp ops.
- **Alphabetical insertion points stated incorrectly** — first Critic B1 caught: `code-review` < `commit-slice` (ASCII `d` < `m`), so insert between `build-slice` and `commit-slice`, NOT between `commit-slice` and `critic-calibrate`. For `_CANONICAL_AGENTS`, `code-review` < `critic-calibrate` (ASCII `o` < `r`), so prepend as first entry. Recompute-don't-trust on lexical ordering applied.

## Discovered

- **M1: Diff-resolution working-tree gap in `skills/code-review/SKILL.md` Step 1** — `git diff "$base"...HEAD` triple-dot syntax returns empty when slice has no commits yet (the normal post-`/build-slice` and pre-`/commit-slice` state). Triggers `NO-CODE-CHANGES` empty-diff path on every post-/build-slice invocation, silently defeating AC1's "non-empty findings" promise. **Action**: nominated for slice-061 to fix as part of its first-real-invocation hardening (single-Phase code change to SKILL.md: replace triple-dot with two-dot working-tree + `git ls-files --others --exclude-standard` untracked enumeration). Cited in code-review.md M1 + build-log Deferrals.

- **M2: Harness session-load timing (bootstrap exception)** — Claude Code loads `subagent_type` definitions at session-start, not on-disk-detect. The slice that authors a new agent cannot spawn it in its own session. The agent IS correctly installed (`~/.claude/agents/code-review.md` exists, CAD-1 drift guard PASS); the harness just hasn't registered it for spawning until session restart. **Action**: documentation pass at slice-061 / slice-062 — add a "Bootstrap caveat" note to `skills/code-review/SKILL.md` Step 2 + ADR-059 Consequences section. NOT a code defect; platform-behavior constraint. Bootstrap-discharge per slice-026/027 precedent applies.

- **Test path bug — `parents[2]` vs `parents[3]`** — `tests/skills/code_review/test_code_review_skill.py` initial `_REPO_ROOT = Path(__file__).resolve().parents[2]` resolved to `tests/`, not repo root. Caught at first pytest run (3/31 FAILED → 31/31 PASSED after `parents[3]` fix). One-roundtrip miss caught by Phase D test run; NOT a systemic class — no calibration signal needed beyond "run pytest before marking PENDING→PASSING".

- **WS-1 bulk-sed over-replacement** — bulk `sed 's/| PENDING |/| PASSING |/g'` over the TF-1 plan also touched the Walking-skeleton table (which uses EXERCISED token, not PASSING). WS-1 audit caught it (`status 'PASSING' not in ['EXERCISED', 'PENDING']`). Fixed via targeted `re.search` on Walking-skeleton block only. NOT a Critic miss — Builder execution error; the audit gate functioned exactly as designed (catch-during-Phase-E).

- **BCI-1 local-machine pre-existing drift** — `~/.claude/build-checks.md` carried non-canonical rules `BC-GLOBAL-4` / `BC-GLOBAL-5` per the canonical fixture. Per BCI-1 attribution ("LOCAL VAULT DRIFT — reconstruct from canonical fixture; this is NOT a slice regression"), reconstructed in-line during Phase E. Pre-existing machine state, NOT a slice-060 introduction. The R-4 retirement attribution mechanic worked exactly as ADR-028/029 designed.

## Deferred

- **AI-bloat passes** (multi-impls / half-wired modules / stale scaffolding / session-break inconsistency) — slice-061 strong candidate (port `/diagnose`'s pass templates scoped to slice diff).
- **TRI-1 triage gate + verdict-driven block on `/validate-slice`** — slice-062 (slice-060's findings stay advisory only in v1).
- **M1 fix (diff-resolution working-tree gap)** — slice-061 first task (1-line code change in `skills/code-review/SKILL.md` Step 1).
- **M2 documentation pass (harness session-load timing)** — slice-061 or slice-062.
- **m1, m2, m3** (minor prose/clarity fixes in SKILL.md + agent.md) — bundled to slice-061.
- **`/code-review --force` flag, risk-tier-based skip, mandatory-trigger detection** — defer until walking-skeleton proves value (slice-061+ if N≥3 vault-only slices accumulate).
- **`/critic-calibrate` v2 extension for code-Critic accuracy tracking** — defer to N≥10 slices of `/code-review` operation per slice-037 precedent.

## Critic calibration

Per TRI-1, score each finding via the disposition in `critique.md` `## Triage` table + reality observed during build/validate:

**First-Critic findings (5B + 5M + 4m = 14):**
- **B1** (alphabetical insertion): **VALIDATED** — ACCEPTED-FIXED; recompute-don't-trust verified `code-review` < `commit-slice` < `critic-calibrate`; `_CANONICAL_SKILLS` + `_CANONICAL_AGENTS` insertions at correct positions verified at INST-1 audit (clean 26/26 + 6/6).
- **B2** (PMI-1 4-part vs 5-part): **VALIDATED** — ACCEPTED-FIXED; PVFS-1 leg added; without this fix, `pyproject.toml [project].version` would have stayed at 0.63.0 and PVFS-1 test would have FAILed at Phase E.
- **B3** (tests/agents/ + tests/skills/code_review/ phantom paths): **VALIDATED** — ACCEPTED-FIXED; both `__init__.py` files created at Phase A1 (Phase A1 was sequenced FIRST per the prerequisite-directory-creates note).
- **B4** (4-vs-5 tool count drift): **VALIDATED** — ACCEPTED-FIXED; positive+negative substring pin caught in `test_agent_md_read_only_tools_pinned`.
- **B5** (6 hardcoded "8" sites): **VALIDATED** — ACCEPTED-FIXED; all 6 sites updated; SCPD-1 row #27 consumer-propagation pin preserved; PCA-1 audit clean at 9 skills.
- **M1** (9-dim reframe asserted but not designed): **VALIDATED** — ACCEPTED-FIXED; design.md "## 9 dimensions reframed for code" section added.
- **M2** (Build-phase sequence not enumerated; integration test cannot drive LLM from pytest): **VALIDATED** — ACCEPTED-FIXED; "## Build-phase sequence" section + TF-1 row 3 reclassified `integration → unit` (artifact-existence check). The "cannot drive LLM from pytest" insight is exactly correct.
- **M3** (empty-diff in-scope path enumeration): **VALIDATED** — ACCEPTED-FIXED; SKILL.md Step 1 explicit in-scope path list (skills/**/SKILL.md + agents/*.md + tools + tests + root config; vault + docs out-of-scope).
- **M4** (v0.64.0 entry-pin substring scope; test rename): **VALIDATED** — ACCEPTED-FIXED; 8 substring assertions all PASS; renamed to `test_v_0_64_0_crsi_1_entry_present_in_repo` matching slice-059 precedent.
- **M5** (catalog row #60 Command cell SCPD-1 sub-mode (b)): **VALIDATED** — ACCEPTED-FIXED; "## Shippability catalog row #60 design" sub-section + 6 selectors enumerated; PTFCD-1 verified all selectors resolve.
- **m1** (v0.41.0 "8 covered skills" bridge sentence): **VALIDATED** — ACCEPTED-FIXED; v0.64.0 entry includes "8 → 9 covered skills" bridge sentence; SUP-1 append-only preserved.
- **m2** (`_resolve_slice_dir` runtime/test layer conflation): **VALIDATED** — ACCEPTED-FIXED; SKILL.md Prerequisite reads section corrected.
- **m3** (AI-bloat framing oversells SC-022/SC-025): **VALIDATED** — ACCEPTED-FIXED; ADR-059 Context para 4 trimmed to two-class framing.
- **m4** (WebSearch surfaced #18837 platform-evidence citation): **VALIDATED** — ACCEPTED-FIXED; ADR-059 "Read-only stance" 2-sentence citation added.

**Meta-Critic (DR-1) missed findings — all surfaced in Builder's own /critique fix-prose:**
- **M-add-1** (Phase B forward-sync omitted edited build-slice + validate-slice SKILL.md): **VALIDATED** — ACCEPTED-FIXED; without this fix, `test_pipeline_position_block_byte_equal_in_repo_vs_installed` would have FAILed for build-slice + validate-slice at Phase D/E. Caught reality EXACTLY.
- **M-add-2** (TF-1 plan omitted paired `_shippability_consumer_propagation` test): **VALIDATED** — ACCEPTED-FIXED; BC-PROJ-10:173 verbatim N≥17 pair-precedent. Without this fix, BC-PROJ-10 trigger would have fired at Phase E.
- **m-add-1** (Dim 9 reframe elides code-side PTFCD-class concerns): **VALIDATED** — ACCEPTED-FIXED; Dim 9 split clarification added.

**Missed by Critic (both layers)**:
- **M1 (diff-resolution working-tree gap)** — surfaced at Phase C self-dogfood, NOT in either Critic's findings. The Critic READ the SKILL.md prose but did not EXECUTE it against the actual git state. This is the **APED-1 (Audit-Parse-Rule Empirical-Execution Discipline)** class (slice-037) applied to skill-prose: when the slice changes an audit's or skill's parse rule, the rule must be EXECUTED, not just read. Build-time-REACHABLE class.
- **M2 (harness session-load timing)** — surfaced at Phase C agent-spawn attempt; both Critic layers missed it. The Critic dimensions don't currently cover platform-behavior constraints (when does the new agent file actually get registered?). Operational class.

**Pattern**: N=2 build-time-REACHABLE classes missed by the dual-Critic stack, both surfaced in Builder's own /critique fix-prose (the new appended "## Build-phase sequence" section + the new SKILL.md prose). This is the **slice-049 / slice-042 / slice-032 "design correction is itself an unguarded adversarial surface"** class, **N=5+ cumulative** counting this slice. Strong calibration signal for `/critic-calibrate` — the meta-Critic correctly caught 3 in fix-prose at /critique-review (M-add-1 / M-add-2 / m-add-1) but missed the build-time-EXECUTE-the-SKILL-prose class (M1) that the BC-PROJ-4 / Phase C real-artifact run was the only backstop for.

## Lessons for next slice

1. **Slice-061 first task: fix M1 (diff-resolution working-tree gap)** before any other slice-061 work — otherwise slice-061's own `/code-review` invocation will hit `NO-CODE-CHANGES` immediately. Single-phase code change in `skills/code-review/SKILL.md` Step 1: replace `git diff "$base"...HEAD` triple-dot with `git diff "$base"` two-dot + `git ls-files --others --exclude-standard` for untracked.

2. **Bootstrap-discharge pattern is now N=3** (slice-026 CRP-1, slice-027 PCA-1, slice-060 CRSI-1). For any future slice that authors a new methodology surface requiring harness session-load registration (new agent, new skill referenced in a fresh chain edge, etc.), assume bootstrap-discharge from day one — don't claim "self-exercise produces real output" as a strict-PASS gate; instead, the structural discharge IS the agent/skill file installed + tests + drift guards + shippability row. First-real-exercise lands at the NEXT slice's auto-advance edge.

3. **APED-1 applies to SKILL-prose, not just audit-parse-rules** — when a slice authors a new SKILL.md with a runtime-resolution claim ("the skill resolves the diff via X"), the Critic must EXECUTE the proposed mechanism (Bash the `git diff` command from the cited prose) against the real post-/build-slice git state, not just read the prose. The slice-037 APED-1 lineage extends from `tools/*.py` parse rules to `skills/*/SKILL.md` prose-as-executable-contract. Strong `/critic-calibrate` candidate.

4. **The "design correction is itself an unguarded adversarial surface" class is at N=5+** (slice-032 / slice-042 / slice-049 / slice-058 / slice-060). At promotion threshold for a Critic prompt dimension update via `/critic-calibrate`. Consider running `/critic-calibrate` in the next 1-2 slices to formalize.

5. **Bulk sed substitutions on the TF-1 plan are risky** — `sed 's/PENDING/PASSING/g'` is too broad; the Walking-skeleton table uses `EXERCISED` token, not `PASSING`. Use scoped Python `re.search` on the specific table block, or update rows individually. WS-1 audit IS the backstop here; the lesson is "always run WS-1 after TF-1 status edits".

## Vault updates made (thin vault — small list)

- `methodology-changelog.md` — added `## v0.64.0 — 2026-05-23` entry referencing CRSI-1 + ADR-059 (8 substring anchors + 8→9 chain bridge sentence + 5-part PMI-1 bump anchor); forward-synced to `~/.claude/methodology-changelog.md` (MCFS-1 PASS).
- `architecture/decisions/ADR-059-add-code-review-skill.md` — new ADR; reversibility: cheap; status: accepted; mints CRSI-1.
- `architecture/shippability.md` — row #60 appended (BCR-1 traceability axis cites CRSI-1 + ADR-059; 6 pytest selectors; runtime <3s).
- `VERSION` 0.63.0 → 0.64.0; `plugin.yaml` version + new code-review entries; `pyproject.toml [project].version` 0.63.0 → 0.64.0 (PVFS-1 leg).
- `tools/install_audit.py` `_CANONICAL_SKILLS` + `_CANONICAL_AGENTS` extended (alphabetical insertion verified).
- `tools/pipeline_chain_audit.py` `_CANONICAL_CHAIN` extended 8 → 9 entries + 4 file-internal "8"→"9" sites.
- `skills/build-slice/SKILL.md` Pipeline-position `successor: /code-review`; `skills/validate-slice/SKILL.md` Pipeline-position `predecessor: /code-review`.
- This slice's `design.md` was authored fresh (no pre-existing claims to correct).
- **No risk-register update** — M1 + M2 are slice-level discovered defects nominated for slice-061, not full risk-register entries (impact is bounded and the fixes are 1-day scope).
- **No backlog round-trip** — slice-060 did not close any `SC-\d{3}` candidate (no `**Closes:** SC-` sentinel in mission-brief.md or this reflection.md). The slice was a `/query-design`-discovered new capability, not a backlog item. BCR-1 no-op clean.
