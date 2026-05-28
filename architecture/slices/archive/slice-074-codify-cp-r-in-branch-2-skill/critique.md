# Critique: Slice 074 codify-cp-r-in-branch-2-skill

**Critic reviewed**: mission-brief.md, design.md (no new ADRs — MEPD-1 EXCLUDE)
**Date**: 2026-05-28
**Result**: CLEAN (post-TRI-1; 10 dispositions all ACCEPTED-FIXED in-band; M4 severity adjusted Major→Minor per /critique-review SEVERITY-WRONG accepted; first-Critic body retains original Major tag for historical traceability)

## Summary

The slice is small, well-scoped, and operationalizes R-20 candidate (a) per established precedent. The proposed test regexes were executed against synthetic post-edit SKILL.md and PASS correctly. However, four issues surface: (1) a recursive-self-application bootstrap gap that mission-brief must-not-defer item #2 over-promises; (2) a latent section-extraction regex fragility to `## `-prefixed lines inside the bash codefence; (3) the `cp -r` regex over-matches on comment-only mentions; and (4) the design.md should explicitly distinguish slice-074's EXCLUDE rationale from slice-066's same-surface INCLUDE rationale.

## Findings

### Blockers (must address before /build-slice)

None.

### Majors (address this slice)

#### M1: Recursive-self-application contradiction in must-not-defer item #2 — slice-074's own /build-slice CANNOT execute the codified cp -r step

- **Claim under review**: mission-brief.md L45 — "**Recursive self-application** (slice-022 law): the slice-074 /build-slice's OWN prerequisite check must execute the new cp -r step successfully — this is the canonical N+1 first-governed-slice test for the codified step. The build-log Events line at Phase A must demonstrate the cp -r ran (e.g., `cp -r diagnose-out/ graphify-out/ to worktree (codified at slice-074 /build-slice prereq)`)."
- **Issue**: Bootstrap order — `/build-slice` reads the **installed** copy of `~/.claude/skills/build-slice/SKILL.md`, not the in-repo `skills/build-slice/SKILL.md`. At slice-074's `/build-slice` invocation (Phase A — prerequisite check fires BEFORE any test/SKILL.md edits land), the installed SKILL.md is still the pre-slice version (v0.72.0 prose, no cp -r codification). Therefore the codified step is NOT in Claude's reading at slice-074's own prereq check; the cp -r that runs at Phase A is the same MANUAL cp -r that has run at slices 067-073 — it is NOT a self-application of the newly codified prose. This is the same bootstrap problem CRP-1 explicitly carves out at slice-026 (see `skills/build-slice/SKILL.md:37` — "**Bootstrap exception (slice-026 only)**: per ADR-024, slice-026 is CRP-1 bootstrap-reference instance #1 — it authors this very sub-block, so this sub-block does not exist at slice-026's own prerequisite check and cannot self-gate that build"). slice-074 needs the same explicit bootstrap-exception framing. The N+1 first-governed-slice canonical test (per slice-040 precedent) is **slice-075's** /build-slice prereq, not slice-074's.
- **Evidence**: `skills/build-slice/SKILL.md:37` (CRP-1 bootstrap exception precedent); design.md L11 + AC-test design at L101-145 mention OSDG-1 forward-sync happens at Phase C (after Phase A prereq check); `skills/build-slice/SKILL.md:17-37` (`## Prerequisite check`) confirms prereq runs at /build-slice invocation, before any user-task work.
- **Proposed fix**: Edit mission-brief.md must-not-defer item #2 to reframe slice-074 as the BOOTSTRAP instance mirroring CRP-1 slice-026 bootstrap exception per ADR-024: the new cp -r step does NOT execute at slice-074's own Phase A; codified step is exercised manually as before; canonical first-governed-slice (N+1) demonstration is slice-075's Phase A prereq run. Add a corresponding §"Bootstrap framing" sub-section to design.md so the bootstrap exception is captured in the design contract, not just the mission brief.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief.md must-not-defer #2 reframed in-band as bootstrap exception per CRP-1/ADR-024 precedent; design.md gains a §"Bootstrap framing" sub-section. The N+1 canonical demonstration belongs to slice-075.

#### M2: Section-extraction regex `r"^### Branch state\b.*?(?=^## )"` terminates early on any future bash-codefence line beginning with `## ` — latent bear-trap

- **Claim under review**: design.md L113 — `m = re.search(r"^### Branch state\b.*?(?=^## )", text, re.MULTILINE | re.DOTALL)`
- **Issue**: APED-1 execution — Critic ran the proposed regex against a synthetic input where the bash codefence inside `### Branch state` contains a comment line `## This is not a heading but starts with ## at line start`. The regex's `(?=^## )` lookahead with `re.MULTILINE` matches ANY line-start `## ` — including INSIDE code fences. The section truncates at 34 chars instead of including the rest. Current slice-074-proposed prose uses single-`#` comments (`# Seed gitignored derived dirs from main tree (R-20)`), so the test PASSES today. But the section's existing bash codefence at `skills/build-slice/SKILL.md:45-51` already uses `#` comments — any future Builder who switches to `## `-prefixed shell comments (a legitimate stylistic choice — `##` is a common shell-convention for "section-marker" comments) would silently invalidate the section extraction. The structural-pin would then report misleading failures (e.g., "diagnose-out cp -r line missing" when it's actually present, but truncated out of the section).
- **Evidence**: Empirical test executed via `re.search` against synthetic input; result: section length 34 instead of expected ~3986 (truncated at the `## ` codefence comment).
- **Proposed fix**: Tighten section-extraction regex to `r"^### Branch state\b.*?(?=^## [A-Z])"` (require capital letter — markdown headings convention; shell `## ` comments are typically lowercase or arbitrary). Update design.md L113 + the corresponding test body at L101-115. Document the choice in a brief inline docstring so future Builders don't revert it.
- **Builder draft**: **ACCEPTED-FIXED** — regex tightened to `r"^### Branch state\b.*?(?=^## [A-Z])"` (markdown-H2-capital-letter convention) at design.md test-contract section; docstring annotation preserves rationale.

#### M3: `cp -r [^\n]*diagnose-out` regex over-matches on comment-only mentions

- **Claim under review**: design.md L126-127 — `diagnose_match = re.search(r"cp -r [^\n]*diagnose-out", section)` / `graphify_match = re.search(r"cp -r [^\n]*graphify-out", section)`
- **Issue**: APED-1 execution — a comment line such as `# WARNING: do NOT use cp -r diagnose-out outside the worktree` matches the regex (`cp -r diagnose-out` is a literal substring). The test would PASS even if the actual functional `cp -r ... diagnose-out` line were removed but replaced by a comment mentioning it. Combined with the position-check (`cd_idx < match.start() < point2_idx`), this is exploitable as a silent regression: a Builder who refactors the codified prose into a "see comment for context" placeholder while accidentally deleting the actual executable line would still pass the test.
- **Evidence**: Empirical regex match: `re.search(r'cp -r [^\n]*diagnose-out', '# WARNING: do NOT use cp -r diagnose-out outside ...')` → match found at span (48, 66).
- **Proposed fix**: Anchor the regex to a non-comment line by requiring the `if [ -d ... ]; then cp -r ...` guard prefix (option (a) from Critic — cross-pins AC#1 + AC#2 in the same regex shape). Combined with m3's switch from `&&` to `if/then/fi` form, the AC#1 test becomes `r'^\s*if \[ -d[^\n]*\]\s*;\s*then\s+cp -r [^\n]*diagnose-out'` (MULTILINE).
- **Builder draft**: **ACCEPTED-FIXED** — AC#1 regex anchored to the `if [ -d ... ]; then cp -r` guard prefix; this cross-pins AC#1 + AC#2 in a single shape and forecloses the comment-substring leak.

#### M4: design.md MEPD-1 EXCLUDE rationale conflates slice-074 with slice-068/070/071 precedent without distinguishing slice-066's same-surface INCLUDE precedent

- **Claim under review**: design.md L91 — "Matches slice-068 (VAULT_ROOT constant introduction — MEPD-1 EXCLUDE), slice-070 (PSQ-1 blast-radius dict-leak fix — MEPD-1 EXCLUDE), slice-071 (bundle-066-to-070 code-Critic cleanup — MEPD-1 EXCLUDE) precedent for 'refactor / fix / operationalize that does NOT mint a new methodology rule.'"
- **Issue**: Critic verified via grep across all four precedent slices: slice-068, slice-070, slice-071 are confirmed EXCLUDE. But slice-066 — which TOUCHED THE SAME SKILL.md `### Branch state` SURFACE — was INCLUDE (minted BRANCH-2 / v0.68.0 methodology entry / ADR-063). The differentiating factor for slice-074 is "operationalizes existing R-20 candidate; adds no new rule," NOT "amends a CAD-1/OSDG-1 guarded surface" (slice-066 also amended the same guarded surface and was INCLUDE). The design.md's stated rationale is correct in conclusion but the precedent comparison is misleading — slice-068's surface was Python module / VAULT_ROOT constant; slice-070's was Python source; slice-071 was cleanup-only. None amended the BRANCH-2 SKILL.md surface itself. A Critic reading this in 6 months would be unable to tell whether the precedent applies because the surface-class differs. When claiming precedent, name the specific axis the precedent matches on (rule-mint axis, NOT surface-class axis).
- **Evidence**: Grep across `architecture/slices/archive/slice-{066,068,070,071}-*/design.md` for `MEPD-1`/`INCLUDE`/`EXCLUDE`/`v0.68`/`new methodology`: slice-066 confirmed INCLUDE (mints BRANCH-2, v0.68.0 entry, ADR-063); slice-068/070/071 confirmed EXCLUDE.
- **Proposed fix**: Edit design.md §"MEPD-1 stance: EXCLUDE" to add one explicit sentence distinguishing the axis: slice-066 amended this same SKILL.md `### Branch state` SURFACE and was MEPD-1 INCLUDE because it MINTED BRANCH-2 + ADR-063. slice-074 is EXCLUDE because it operationalizes an existing R-20 candidate without minting a new rule — differentiating axis is 'mints-a-new-rule' (slice-066 = yes, slice-074 = no), not 'amends-a-CAD-1-surface' (both = yes).
- **Builder draft**: **ACCEPTED-FIXED** — design.md §"MEPD-1 stance: EXCLUDE" gains an explicit rule-mint-vs-surface-class differentiating-axis sentence citing slice-066's same-surface INCLUDE.

### Minors (log; address if cheap)

#### m1: Test count delta arithmetic — design.md L170 says +4 but TF-1 plan rows are 5

- **Claim under review**: design.md L170 — "Test count delta: +4 tests (3 structural-pin + 1 retired-status)."
- **Issue**: Mission-brief TF-1 plan (L25-31) has 5 rows. Row #4 is `existing OSDG-1 drift test (re-runs against updated prose)` with status `PASSING-AFTER-SYNC` — it's an existing test, not a new one, so +4 is correct. But TF-1 plan readers count 5 rows. Add one parenthetical so the discrepancy is foreclosed.
- **Evidence**: mission-brief.md L25-31 (5 rows); design.md L170 (says +4).
- **Proposed fix**: Edit design.md L170 to clarify "+4 NEW tests (3 structural-pin + 1 retired-status); 5 TF-1 plan rows total (row 4 = existing `test_build_slice_skill_md_in_repo_byte_equal_installed` re-running against updated prose, no count delta)."
- **Builder draft**: **ACCEPTED-FIXED** — design.md L170 clarified with "+4 NEW; 5 TF-1 rows total" framing.

#### m2: `## v0.73.0 header` referenced in mission-brief L96 PMI-1 contingency is anachronistic — slice-074 is at v0.72.0

- **Claim under review**: mission-brief.md L96 — "if MEPD-1 INCLUDE stance chosen at /design-slice → 5-part atomic bump 0.72.0 → 0.73.0 (VERSION + plugin.yaml + pyproject.toml + `## v0.73.0` header + installed `~/.claude/ai-sdlc-VERSION`)"
- **Issue**: VERSION file currently is 0.72.0 (verified via slice-073 commit citing methodology v0.72.0). The contingency bump-target 0.73.0 is correct IF slice-074 were INCLUDE; since EXCLUDE is the chosen stance, this is just a contingency narrative and is fine. But the pre-finish gate item at L96-L99 is conditional on the EXCLUDE decision — make it clearer this is the "if EXCLUDE chosen → no bump" branch by phrasing as "EXCLUDE is the chosen stance per design.md MEPD-1 stance" rather than leaving both branches open.
- **Evidence**: mission-brief.md L96-99; design.md L84-98 (MEPD-1 EXCLUDE chosen).
- **Proposed fix**: Edit mission-brief.md pre-finish gate item to reflect the EXCLUDE choice has been made (now post-/design-slice); move the INCLUDE branch into a parenthetical "(if Critic disagrees and re-opens EXCLUDE choice at /critique)".
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief.md pre-finish gate item reframed as post-decision; INCLUDE branch demoted to parenthetical contingency.

#### m3: The `[ -d ... ] && cp -r` guard is functionally adequate but loses the `cp -r` exit code on guard-skip — verify this is intentional

- **Claim under review**: design.md L57-58 — "`$repo_root/diagnose-out` absent on main tree (fresh project, never `/diagnose`'d) → `[ -d ... ]` guard short-circuits the `&& cp -r`; line exits 0 silently. No `cp` invocation, no error."
- **Issue**: This is intentional graceful behavior per AC#2, but the chained form `[ -d "$X" ] && cp -r "$X" ./` returns the exit status of the LAST executed command. If `[ -d ... ]` is false, the line returns the test's exit (1) — which under `set -e` would terminate the codefence. The current SKILL.md bash codefences do not set `set -e`, so this works. But if a future Builder adds `set -e` for safety (common in bash hardening), the absent-source-dir case would FAIL LOUDLY instead of silently skipping. The defensible fix is `[ -d "$X" ] && cp -r "$X" ./ || true` (suppress non-zero from the test failure) OR `if [ -d "$X" ]; then cp -r "$X" ./; fi`.
- **Evidence**: design.md L17 (AC#2 guard); POSIX shell semantics.
- **Proposed fix**: Switch to the `if [ -d "$X" ]; then cp -r "$X" ./; fi` form — slightly more verbose but eliminates the latent fragility under future `set -e` hardening. Update SKILL.md insertion plan + design.md test contracts (M3's AC#1 regex update is co-impacted — both fixes share the `if-then` prefix anchor).
- **Builder draft**: **ACCEPTED-FIXED** — switched to `if [ -d "$X" ]; then cp -r "$X" ./; fi` per-line form. AC#1 + AC#2 regexes updated to match (co-impact with M3 in single fix block).

#### m4: TF-1 plan test path for AC#3 uses prose `existing OSDG-1 drift test (re-runs against updated prose)` rather than the function name — PTFFD-1 brittleness avoided but readers must cross-check

- **Claim under review**: mission-brief.md L30 — `| 3 | drift (existing class) | tests/methodology/test_build_slice_skill_drift.py | existing OSDG-1 drift test (re-runs against updated prose) | PASSING-AFTER-SYNC |`
- **Issue**: Per PTFFD-1 (slice-037 / ADR-038): "a non-identifier / prose value (e.g. slice-034's real `(full existing module — non-regression)` TF-1 row) is NOT a checkable name and degrades to FILE-level-only — never a false-positive." This row degrades to FILE-level only — fine, intentional. But the actual function name is `test_build_slice_skill_md_in_repo_byte_equal_installed` (verified by Critic at `tests/methodology/test_build_slice_skill_drift.py:24`). Citing the prose is conventionally acceptable but adds friction for a /validate-slice reviewer who must grep to find the actual function. Cheap fix: cite the function name.
- **Evidence**: `tests/methodology/test_build_slice_skill_drift.py:24` defines `test_build_slice_skill_md_in_repo_byte_equal_installed`.
- **Proposed fix**: Edit mission-brief.md L30 row 4 `Test function` cell to: `test_build_slice_skill_md_in_repo_byte_equal_installed` (drop the prose; the row already documents the test is existing via the `PASSING-AFTER-SYNC` status).
- **Builder draft**: **ACCEPTED-FIXED** — TF-1 row 4 cites the actual function name `test_build_slice_skill_md_in_repo_byte_equal_installed`.

## Dimensions checked

- [x] **Unfounded assumptions** — M1 (recursive-self-application bootstrap claim is unfounded; the cp -r at Phase A is the OLD manual one because installed SKILL.md isn't synced yet). `$repo_root` correctness post-cd verified by tracing shell-variable binding at `skills/build-slice/SKILL.md:57` → still points at main tree after L60 cd. AC discharge requires evidence; the recursive-self-application AC over-states what is verifiable.
- [x] **Missing edge cases** — m3 (set -e hardening edge case). Partially-populated `diagnose-out/` from interrupted /diagnose run: `cp -r` overwrites file-by-file, which is the design's stated semantics — acceptable. cp -r race with concurrent main-tree /diagnose write: extremely unlikely in single-user workflow; not a blocker. Symlink loops: not present in diagnose-out/graphify-out content per design L61. /tmp-style worktree on macOS: BRANCH-2 canonical path is `<main-parent>/<main-name>-wt/...`; macOS /tmp is irrelevant unless user manually overrides via `WORKTREE=skip` escape-hatch, which is already documented out-of-scope.
- [x] **Over-engineering** — none. The 3-line addition (1 comment + 2 guarded cp -r) is the minimum-mechanism fix. The structural-pin test count of 3 (one per AC sub-claim: presence+position, R-20 reference, guard) is justified per slice-067 paired-pin precedent.
- [x] **Under-engineering** — M1 (recursive-self-application claim over-promises and must be reframed). Methodology-audit conformance — BC-1 verified clean (executed `tools.build_checks_audit --slice ...` → 0 violations). TF-1 row coverage — 5 rows cover 4 ACs; AC#3 is the existing-test row; coverage adequate. The slice does NOT codify the "switch-commit-switch-worktree" sister-pattern (N=4 cumulative per slice-073) — that's deferred per attack-focus suggestion and out-of-scope is correct per slice-022 codify-only-what-reality-demands.
- [x] **Contract gaps** — none material. The SKILL.md prose contract is clearly scoped to "inside the numbered point 1 bash codefence, after cd, before point 2"; AC#1's position assertion enforces this mechanically.
- [x] **Security** — none. `cp -r` source is constrained to `$repo_root/diagnose-out` + `$repo_root/graphify-out` (no user-controlled path); dest is cwd (worktree). `diagnose-out/` HTML content is plain files — `cp -r` does NOT interpret/execute file contents. No symlink escape because diagnose-out/graphify-out generators don't emit symlinks (per design.md L61). No privilege escalation — runs as same user. Note: on Windows, MSYS `cp -r` follows symlinks per POSIX default; if a malicious actor planted a symlink in main-tree diagnose-out/, cp -r would follow it and copy whatever it points to into the worktree — but the threat model requires "attacker who can write to user's main tree diagnose-out/", at which point the attacker already has filesystem write access and has worse attack surfaces.
- [x] **Drift from vault** — M4 (precedent claim conflates rule-mint axis with surface-class axis). MEPD-1 EXCLUDE stance defensible on rule-mint axis. R-20 entry in risk-register.md (L340-360) verified; status flip mitigation→retired follows STP-1 / slice-072 R-19 retirement pattern. ADR-063 / BRANCH-2 contract not contradicted — this slice extends sub-mode (a) build-time worktree-create with a new derived-dir-seed step but does NOT change the core worktree-create-cd-ready contract.
- [x] **Web-known issues** — skipped — WebSearch deemed not applicable; the slice's mechanic is POSIX `cp -r` invoked from Git for Windows MSYS bash, which is decades-stable.
- [x] **Cross-cutting conformance** — Methodology-audit conformance verified for BC-1 (0 violations executed). APED-1 execution discipline applied: regex-shape executed against real artifacts surfaced M2 + M3. SCPD-1 / FBCD-1 cross-file consistency: mission-brief vs design.md test bodies are byte-identical for the cd_marker / point2_marker / regex shapes. PTFCD-1 / PTFFD-1: cited test paths `tests/methodology/test_build_slice_skill_cp_r_step.py` + `tests/methodology/test_r_20_retired.py` are NEW (slice-074 creates them) — legitimate PENDING per audit; the AC#3 existing test `tests/methodology/test_build_slice_skill_drift.py` was verified to exist on disk. RSAD-1 recursive-self-application discipline: see M1 — slice-074 fails the recursive-self-application stress test because the bootstrap order prevents codified prose from being read at its own Phase A.

## Triage

**Triaged by**: user
**Date**: 2026-05-28
**Final verdict**: CLEAN

10 dispositions total (8 first-Critic + 2 meta-Critic missed) reconciled from BOTH passes per DR-1. All ACCEPTED-FIXED in-band on mission-brief.md + design.md before /build-slice. M4 severity adjusted Major→Minor per /critique-review SEVERITY-WRONG accepted at TRI-1 (disposition unchanged; calibration-only adjustment per Wiegers severity-discrimination framework — "produces correct output via opaque reasoning" is Minor, not Major).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | mission-brief.md must-not-defer #2 reframed as bootstrap exception; design.md §"Bootstrap framing" added per CRP-1 / ADR-024 slice-026 precedent |
| M2 | Major | ACCEPTED-FIXED | design.md section-extraction regex tightened to `(?=^## [A-Z])`; docstring annotation preserves rationale |
| M3 | Major | ACCEPTED-FIXED | design.md AC#1 regex anchored to `^\s*if \[ -d ...\]; then cp -r` guard prefix; cross-pins AC#1 + AC#2 (forecloses comment-substring leak) |
| M4 | Minor (was-Major-per-first-Critic; meta-Critic SEVERITY-WRONG accepted at TRI-1) | ACCEPTED-FIXED | design.md §"MEPD-1 stance: EXCLUDE" gains explicit rule-mint-vs-surface-class differentiating-axis sentence citing slice-066 same-surface INCLUDE precedent |
| m1 | Minor | ACCEPTED-FIXED | design.md L170 framed as "+4 NEW tests; 5 TF-1 rows total (row 4 = existing `test_build_slice_skill_md_in_repo_byte_equal_installed`)" |
| m2 | Minor | ACCEPTED-FIXED | mission-brief.md pre-finish gate reframed as post-EXCLUDE-decision; INCLUDE branch demoted to contingency parenthetical |
| m3 | Minor | ACCEPTED-FIXED | switched `[ -d ...] && cp -r` to `if [ -d ...]; then cp -r ...; fi` per-line form (set-e-safe); AC#2 test function renamed `_use_dash_d_guard_` → `_use_if_then_guard_`; co-impact with M3 handled in single fix block |
| m4 | Minor | ACCEPTED-FIXED | mission-brief.md TF-1 row 4 cites actual function `test_build_slice_skill_md_in_repo_byte_equal_installed` |
| m-add-1 | Minor | ACCEPTED-FIXED | design.md test docstring of `test_cp_r_lines_use_if_then_guard_for_source_dir_absence` gains explicit single-line-form-pinned constraint citing RSAD-1 byte-exact-match discipline |
| m-add-2 | Minor | ACCEPTED-FIXED | design.md §"Bootstrap framing" gains Phase-A/B/C-to-Step-1-7 glossary + slice-075 sequencing-confirmation paragraph |

---

# /critique pass 2 — EXPANSION DELTA (AC#5+AC#6)

**Critic reviewed**: mission-brief.md AC#5+AC#6 + TF-1 plan rows 6+7, design.md §"What's new" switch-commit-switch codification + test contracts for `test_build_slice_skill_dirty_tree_resolution.py`, in-repo `skills/build-slice/SKILL.md` (current pre-edit state at L67-71)
**Date**: 2026-05-28
**Result**: NEEDS-FIXES (1B / 2M / 2m; all 5 findings ACCEPTED-FIXED in-band — pending TRI-1-EXT ratification)

## Summary (pass 2)

APED-1 execution against synthetic post-edit prose surfaced **one Blocker** and **two Majors** on the new `test_build_slice_skill_dirty_tree_resolution.py` test contracts. The AC#6 no-`-b` regex is falsified by the canonical codified prose itself (`# no -b; branch exists` trailing comment contains literal `-b`, defeating the `(?!.*-b)` lookahead). The AC#5 order-token search passes on prose-only narrative without the actual codefence. The `_point_4_block` regex has no upper boundary. Two Minors on under-engineering (no cross-reference to slice-070 reflection L127, NO-auto-stash discipline-preservation not structurally pinned). The original AC#1-AC#4 clearance from pass 1 is preserved untouched.

## Findings (pass 2)

### Blockers

#### B1: AC#6 no-`-b` regex falsified by the canonical codified prose's own trailing comment `# no -b; branch exists`

- **Claim under review**: design.md §"test_both_worktree_create_forms_documented_dash_b_and_no_dash_b" — `point_4_no_dash_b_pattern = re.compile(r'git worktree add\s+(?!.*-b)[^\n]*slice/NNN-<slice-name>', re.MULTILINE)`, paired with the canonical codified line: `git worktree add "$wt_base/slice-NNN-<slice-name>" slice/NNN-<slice-name>   # no -b; branch exists`.
- **Issue**: APED-1 execution — the negative lookahead `(?!.*-b)` forbids `-b` ANYWHERE later on the line. The canonical line's trailing comment `# no -b; branch exists` embeds literal `-b`. AC#6 will FAIL at Phase A red-test verification AND mid-slice smoke AND /validate-slice — no path to PASSING with both the prose AND regex co-existing as drafted.
- **Evidence**: APED-1 execution via Critic's `re.compile(...).search(...)` on the literal design.md codefence line — match = None.
- **Proposed fix**: Tighten the no-`-b` lookahead to scope ONLY across operands BEFORE the `#` comment delimiter: `r'git worktree add\s+(?!(?:[^#\n]*?)-b\s)[^#\n]*slice/NNN-<slice-name>'` (excludes the comment from both the lookahead-scope and body match; requires `-b\s` with trailing whitespace to forbid only the actual flag form).
- **Builder draft**: **ACCEPTED-FIXED** — design.md test contract for AC#6 updated to use `[^#\n]` to scope before-comment + `-b\s` flag-shape; comment-aware negative lookahead forecloses the false-negative.

### Majors

#### M1: AC#5 order-token search PASSES on prose-only narrative without any codefence — token-presence ≠ codefence-presence

- **Claim under review**: design.md §"test_point_4_contains_switch_commit_switch_worktree_sequence_in_order" — uses `point_4.find("git switch -c slice/")` / `point_4.find("git commit", ...)` / `point_4.find('git switch "$default"', ...)` / `point_4.find("git worktree add", ...)`.
- **Issue**: APED-1 execution — a synthetic point-4 narrative that mentions all 4 tokens in order WITHOUT a `` ```bash ... ``` `` codefence PASSES. A future Builder who reverts point 4 to "STOP, ask user to commit or stash" while keeping a paragraph that NARRATES the sequence as a "this is what you should manually do" warning would still pass AC#5 — the codified contract (an executable bash codefence) would be silently lost. Same failure-mode-class as pass 1's M3 (comment-substring leak; ACCEPTED-FIXED for AC#1/AC#2 but NOT propagated to the new AC#5).
- **Evidence**: APED-1 execution outputs (Critic CHECK 1: `all tokens found in order: True` against prose-only synthetic; CHECK 2: `all tokens found in order: True` against pre-edit-STOP-prose + warning narrative).
- **Proposed fix**: Scope AC#5 token-search to INSIDE a `` ```bash ... ``` `` codefence within point 4. Compose with M2's fix by redefining `_point_4_block` to extract ONLY the bash codefence body. Also add the scaffolding-commit body shape `git commit -m "scaffold(slice-NNN):` as a 5th anchor so the assertion discriminates "`git commit` mentioned in narrative" from "`git commit -m \"scaffold(...)\"` inside the codified recipe".
- **Builder draft**: **ACCEPTED-FIXED** — `_point_4_block` redefined to extract bash codefence body only (composes with M2); 5th anchor token `git commit -m "scaffold(slice-NNN):` added to AC#5 order-token search.

#### M2: `_point_4_block` regex has no upper boundary — currently swallows the `WORKTREE=skip` paragraph and would pollute AC#5 token search if a future point-5 / point-N is added

- **Claim under review**: design.md §"_point_4_block" — `m = re.search(r"^4\. \*\*If working tree is dirty\b.*", section, re.MULTILINE | re.DOTALL)`, with docstring claim "no point 5 exists today; extract to end-of-section".
- **Issue**: APED-1 execution on the actual SKILL.md — `_point_4_block` extracts 780 chars and INCLUDES the `WORKTREE=skip escape-hatch line shape` paragraph at L71. The docstring claim "no point 5 exists today" is true but brittle. A future point 5 (e.g., stale-branch handling) OR a rewrite of the `WORKTREE=skip` paragraph that mentions `git switch`/`git commit`/`git worktree add` would silently satisfy AC#5 via material OUTSIDE point 4.
- **Evidence**: APED-1 execution on actual SKILL.md (Critic confirmed: `point_4 length: 780; point_4 contains 'WORKTREE=skip': True`).
- **Proposed fix**: Redefine `_point_4_block` to extract ONLY the bash codefence WITHIN point 4 (composes with M1's fix; shared mechanism — one regex change covers both). Specifically: `re.search(r"^4\. \*\*If working tree is dirty\b.*?```bash\b(.*?)```", section, re.MULTILINE | re.DOTALL)` returns the codefence body. Add docstring note that the upper boundary IS the codefence close — future point-5 additions outside the codefence cannot pollute AC#5.
- **Builder draft**: **ACCEPTED-FIXED** — `_point_4_block` redefined to extract bash codefence body via `re.search(r"^4\. \*\*If working tree is dirty\b.*?```bash\b(.*?)```", ...)`; docstring documents the codefence-close as the upper boundary. One mechanism, two findings closed (M1 + M2).

### Minors

#### m1: No cross-reference to slice-070's empirical-provenance reflection L127 in the codified SKILL.md prose comment

- **Claim under review**: design.md §"What's new" — switch-commit-switch codefence comment: `# (N=5 cumulative slice-070/071/072/073/074; post-vault-in-git scaffolding-by-design class)`.
- **Issue**: The R-20 codification (AC#1) comment cites the risk-register entry as the codification origin. The switch-commit-switch codification comment cites a slice range but no permalink to where the pattern was first articulated. A future Builder wanting to understand "why these 4 specific steps" has to grep N=5 reflection files.
- **Evidence**: design.md test contract for AC#5 (docstring claims "slice-070 reflection L127's user-ratified pattern") — the design knows the canonical origin but the codified prose doesn't carry it.
- **Proposed fix**: Edit the codefence comment to include `slice-070 reflection L127` (or equivalent canonical origin). No test change needed.
- **Builder draft**: **ACCEPTED-FIXED** — design.md codified comment updated to `# (N=5 cumulative slice-070/071/072/073/074; canonical origin: slice-070 reflection L127; post-vault-in-git scaffolding-by-design class)`.

#### m2: NO-auto-stash discipline preservation is documented in out-of-scope (mission-brief.md L75) but NOT structurally pinned

- **Claim under review**: mission-brief.md L75 — "the codified sequence preserves this discipline by requiring the Builder to explicitly stage + commit the scaffolding (not silently shelve it via `git stash`)."
- **Issue**: AC#5 token search asserts the 4 tokens are present in order, but does NOT assert that `git stash` is ABSENT. A future Builder who "improves" the recipe by inserting `git stash` between `git switch -c` and `git commit` would satisfy AC#5 but violate the discipline declared at mission-brief.md L75. If the discipline is load-bearing enough to declare in out-of-scope, it should be load-bearing enough to pin structurally (slice-022 codify-empirical-discipline axis; cf. AC#1's M3 ACCEPTED-FIXED guard-prefix anchor from pass 1).
- **Evidence**: mission-brief.md L75 declaration; design.md test contract for AC#5 has no `git stash` exclusion.
- **Proposed fix**: Add a 3rd structural-pin test to `test_build_slice_skill_dirty_tree_resolution.py`: `test_point_4_codefence_does_not_contain_git_stash` (asserts `"git stash" not in codefence_body` using the M2-fixed `_point_4_block`). Add one new TF-1 plan row tied to AC#5 (multi-test-per-AC permitted; AC#1 already has 2 rows). No new AC needed (the no-stash assertion is a sub-claim of AC#5's discipline-preservation).
- **Builder draft**: **ACCEPTED-FIXED** — 3rd structural-pin test `test_point_4_codefence_does_not_contain_git_stash` added to `test_build_slice_skill_dirty_tree_resolution.py`; TF-1 plan gains one new row tied to AC#5; test count delta updates from +6 → +7; TF-1 row count from 7 → 8.

## Dimensions checked (pass 2)

- [x] **Unfounded assumptions** — none for the expansion delta. `git switch` (2.23+) + `git worktree add <path> <branch>` positional form both universal on Git for Windows (installed git 2.52.0).
- [x] **Missing edge cases** — partially addressed: "NOT idempotent by design" clause correctly addresses session-death-mid-scaffolding-commit. Partial-stage failure not addressed but acceptable on bootstrap-grade slice; codify-exactly-what-reality-demanded.
- [x] **Over-engineering** — none. AC#6 separation from AC#5 is correctly carved-out per slice-072 reflection L97. 2-test split (now 3-test post-m2 fix) in dirty-tree-resolution module gives clearer failure attribution.
- [x] **Under-engineering** — m1 (no slice-070 reflection L127 citation) and m2 (NO-auto-stash discipline not structurally pinned). TF-1 row coverage: 7 rows for 6 ACs pre-m2-fix; 8 rows post-m2-fix.
- [x] **Contract gaps** — minor concern (not raised as Major): switch-commit-switch bypasses BRANCH-2 audit's dirty-tree branch by leaving main tree clean before `git worktree add`. Empirically correct (slices 070-074 all followed this path; no WORKTREE=skip documented). Codify-exactly-what-reality-demanded.
- [x] **Security** — none. `git switch -c slice/NNN-<slice-name>` is constrained-shape; no injection vector.
- [x] **Drift from vault** — none. MEPD-1 EXCLUDE preserved for the expansion (operationalizes N=5 empirical pattern; no new rule). Rule-mint-vs-surface-class differentiating axis from pass 1's M4 still applies.
- [x] **Web-known issues** — skipped — `git switch` + positional `git worktree add` both 6+ years stable.
- [x] **Cross-cutting conformance** — APED-1 execution discipline applied to all 4 new regex shapes — surfaced B1 + M1 + M2 (three findings static-reasoning would have missed). PTFFD-1 / PTFCD-1: new test paths legitimate PENDING. SCPD-1 / FBCD-1 cross-file: mission-brief AC#5+AC#6 anchor strings byte-equal across mission-brief + design.md test contracts. RSAD-1 byte-exact-match correctly cited.

## Triage (pass 2 — EXPANSION DELTA)

**Triaged by**: user (TRI-1-EXT)
**Date**: 2026-05-28
**Final verdict (pass 2)**: CLEAN
**Combined verdict (pass 1 + pass 2)**: CLEAN — slice-074 expanded scope (AC#1-AC#6) fully Critic-cleared.

5 pass-2 dispositions reconciled from BOTH pass-2 Critic + pass-2 meta-Critic per DR-1. All ACCEPTED-FIXED in-band on mission-brief.md + design.md before /build-slice execution. Meta-Critic ACCEPT verdict (0 suspicious / 0 missed / 0 severity adjustments) — calibration on pass-2 first-Critic was exemplary.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md AC#6 test contract: no-`-b` lookahead tightened to `(?!(?:[^#\n]*?)-b\s)[^#\n]*` (comment-aware + `-b\s` flag-shape); APED-1-verified by meta-Critic against 10 synthetic edge cases including tab + path-with-`-b` variants |
| M1 | Major | ACCEPTED-FIXED | design.md AC#5 test contract: `_point_4_block` redefined as `_point_4_codefence_body` (extracts bash codefence body only); 5th anchor token `git commit -m "scaffold(slice-NNN):` added; forecloses prose-only-narrative false-pass |
| M2 | Major | ACCEPTED-FIXED | design.md `_point_4_codefence_body` redefinition (shared mechanism with M1; one regex change, two findings closed); upper boundary IS the codefence close, forecloses future point-5/WORKTREE=skip pollution |
| m1 | Minor | ACCEPTED-FIXED | design.md codified codefence comment updated to include `canonical origin: slice-070 reflection L127`; symmetric with R-20 codification's risk-register-citation pattern |
| m2 | Minor | ACCEPTED-FIXED | design.md new 3rd structural-pin test `test_point_4_codefence_does_not_contain_git_stash`; mission-brief.md TF-1 plan gains 1 new row tied to AC#5; test count delta +6→+7; TF-1 row count 7→8; pre-finish gate pytest target 1001→1002 |
