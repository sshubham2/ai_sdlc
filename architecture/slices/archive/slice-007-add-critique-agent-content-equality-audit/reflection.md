# Reflection: Slice 007 add-critique-agent-content-equality-audit

**Date**: 2026-05-10
**Shipped**: YES-WITH-DEFERRALS

## Validated

- **Option (d) hybrid (c+a) was the right choice over (a) / (b) / (c) alone** — empirically validated at /validate-slice. The skill-prose update at `skills/critic-calibrate/SKILL.md:107-114` (preventive) AND the standalone `tools/critique_agent_drift_audit.py` audit (detective) work in tandem: pre-slice CAD-1 self-application returns clean (all in-repo↔installed pairs byte-equal post-slice-006), drift detection on tmp_path fixture exits 1 with both paths + both hashes (must-not-defer #1 satisfied), sanity-check refusal on `--repo-root` lacking `plugin.yaml`/`INSTALL.md` exits 2 with explanatory message (must-not-defer #7 satisfied). Per ADR-006 reasoning: (c) alone insufficient (recurrence not detected); (a) alone insufficient (recurrence not prevented); (b) over-scoped vs N=1 evidence base; (d) is minimum viable.
- **Bidirectional sha256 forensic capture pattern is N=2 stable** (slice-006 first occurrence; slice-007 second). Phase 0 captured 10 sha256s; all 4 in-repo↔installed pairs were byte-equal at slice start (no back-sync needed — slice-006's bidirectional sync was effective). Phase 4 captured 3 post-sync sha256s; all 3 MATCH. Methodology pattern is load-bearing.
- **TF-1 PENDING → WRITTEN-FAILING transitions genuine** (per slice-005+006 lesson). Phase 1 wrote 7 tests; all 7 failed with specific error signatures (5 with `ModuleNotFoundError: No module named 'tools.critique_agent_drift_audit'`; 2 with `AssertionError` naming the exact missing substring). No coincidental pass.
- **"Validate using your own ship" pattern N=5 stable** (slice-003+004+005+006+007 all use the slice's own `--imports-allowlist tests` flag at VAL-1 Layer B). Pattern is now standard practice.
- **Voluntary Critic on cross-cutting tooling slices is N=7/7 paid off, with 5 of 7 catching design-stage failures that would have failed at build time** (added slice-007 Critic B1 + B2 — both fatal saves). Without B1 catch, the slice's `Out-of-repo files touched` table would have pointed at a nonexistent in-repo file (`ai-sdlc-VERSION`); without B2 catch, the slice-006 PMI-1 escape would have silently persisted. Methodology pattern is load-bearing.
- **All 8 Critic findings VALIDATED at /validate-slice** (0 FALSE-ALARM, 0 OVERRIDE-MISJUDGED, 0 NOT-YET) — slice-006 + slice-007 are now two consecutive 100% Critic accuracy slices.
- **Cross-cutting-conformance Dim 9 (CCC-1, slice-006) is empirically paying off** at /critique time. B1 + M1 + m1 are 3 Dim 9 sub-class hits surfaced during slice-007 /critique. Without Dim 9 prompting the cross-cutting check, B1 (design.md table vs canonical inventory) likely shrugged off as a typo; M1 (tooling-doc-vs-impl parity for `--repo-root`) likely missed. Slice-006-15 effectiveness target (≤2 cross-cutting misses across the window) on track: **0 cross-cutting misses at slice-007 /critique time** (3 hits, all caught + fixed before /build-slice).
- **PMI-1 audit closes the slice-006 escape** — slice-006's reflection.md "Vault updates made" claimed methodology v0.21.0 was synced, but `plugin.yaml.version` was missed (verified empirically at /critique time: pre-slice `python -m tools.plugin_manifest_audit --root .` exited 1 with `version-mismatch ('0.20.0' != '0.21.0')`). Slice-007 atomically corrects both `plugin.yaml.version` and `VERSION` to `0.22.0` AND adds AC #5 + TF-1 row + must-not-defer entry to gate the fix.
- **CAD-1 self-application clean** — `python -m tools.critique_agent_drift_audit` from project root returns exit 0 with sha256 `af6ee94db810d717...`. The slice ships and immediately verifies its own ship against the installed copy.
- **Shippability catalog regression-clean** — 7 rows, 62 tests, **62 PASS in 3.0s** (well under 2-min target). No prior slice broken by slice-007.

## Corrected

- **Initial design.md "Out-of-repo files touched" table mis-named in-repo file as `ai-sdlc-VERSION`** — corrected at /critique time per Critic B1 to `VERSION` (in-repo) → `ai-sdlc-VERSION` (installed) per `INSTALL.md:141` rename. Updated in design.md (3 sites) + mission-brief AC #4 + ADR-006 + milestone.md. The corrections were applied BEFORE /build-slice so the build executed against the corrected design. **Slice's design.md** reflects reality post-corrections.
- **ADR-006 "Implicit fix to slice-006 escape" downgraded to "Explicit fix (gated by AC #5 per Critic B2)"** — without the AC #5 gate, the design's claim to fix the escape "as a byproduct" was unenforced. Corrected at /critique time; design.md + ADR-006 + mission-brief now treat the PMI-1 closure as a gated AC, not a side-effect.
- **No ADRs superseded** — ADR-006 stands as accepted; ADR-001..005 unrelated to this slice's scope.

## Discovered

- **In-repo `VERSION` vs installed `ai-sdlc-VERSION` rename mismatch is the second occurrence of slice-006 cross-cutting-conformance DEVIATION class (N=2)** — slice-006's DEVIATION-1 (plugin.yaml on do-not-copy list per INST-1) + DEVIATION-2 (ai-sdlc-VERSION missed from sync table) was N=1; slice-007's Critic B1 (in-repo `VERSION` named as `ai-sdlc-VERSION`) is N=2. **Meets the explicit "promote to Dim 9 sub-clause when N=2" threshold from slice-006 aggregated lessons.** Slice-008+ candidate: refine Dim 9 to add a sub-clause covering "design.md mechanical tables vs methodology canonical references / install-time renames / canonical-inventory inventories".

- **BC-1 false positives on methodology-vocabulary slices is now N=3** — slice-005 + slice-006 + slice-007 all defer-with-rationale on BC-PROJ-1 (subagent fan-out) AND BC-GLOBAL-1 (4-backtick LLM-fence). Per slice-006 reflection lesson #4: "Promotion candidate at N=3". **Threshold MET.** Slice-008+ candidate: refine BC-PROJ-1 + BC-GLOBAL-1 anchors with negative-context anchor (e.g., `vocabulary`, `meta-discussion`, `defer-with-rationale`) so the rules don't fire on slices that merely *cite* the keywords as historical lesson context. Strongest slice-008 candidate by promotion-threshold-met.

- **Em-dash `—` → cp1252 byte 0x97 on Windows console** (build-time DEVIATION-2). The audit's "clean" output initially used em-dash; subprocess.run with `text=True, encoding="utf-8"` couldn't decode the cp1252 byte; pytest emitted `PytestUnhandledThreadExceptionWarning`. The test still passed (returncode captured separately) but the warning is a flake-risk for CI on Windows. **Generic Python-on-Windows lesson at N=1**: methodology tooling that runs under pytest with subprocess capture should emit ASCII-only output OR set `PYTHONIOENCODING=utf-8` in the subprocess env. **Cross-cutting-conformance sub-class candidate** under Dim 9 — language-version-conformance + runtime-environment intersection. Watch for recurrence in slice-008+; promote to BC-1 / Dim 9 sub-clause refinement at N=2.

- **Prose-pin negative-substring false-positive on legitimate context** (build-time DEVIATION-1). My initial regression-guard substring `"edit \`~/.claude/agents/critique.md\`"` (with backticks) false-positive matched the legitimate line-99 explanatory text "skill PRODUCES proposals. It does NOT edit `~/.claude/agents/critique.md` itself" — a CORRECT statement, but my generic substring matched it. **Generic test-pin lesson at N=1**: regression-guard substrings must be unique to the deprecated content's surrounding phrasing (not just keyword), so they don't false-positive match legitimate negative statements about the same topic. Tightened to `"To apply, edit ~/.claude/agents/critique.md"` (the OLD action block's unique signature). **Cross-cutting-conformance sub-class candidate** under Dim 9 — testing-discipline-conformance / regression-guard substring uniqueness. Watch for recurrence in slice-008+.

- **The 8-dim Critic at /critique time MISSED the em-dash + prose-pin-substring DEVIATIONs** — both surfaced at /build-slice mid-slice smoke gate (Phase 3), not at /critique time. Calibration class for `/critic-calibrate` (when run after slices 6-15): these are TWO new Dim 9 sub-class hits filed AFTER Dim 9 was added (slice-006 CCC-1). **Effectiveness signal**: cross-cutting-conformance miss class at slice-007 = 2 (em-dash + prose-pin substring), both surfaced at build time not /critique. The dimension's body needs sub-clauses covering Python-on-Windows console encoding AND regression-guard substring uniqueness.

- **The 9-dim Critic strict-improves over 8-dim at slice-007 /critique time** — N=2 evidence (slice-006 first occurrence with BC-GLOBAL-1 algorithm-path catch; slice-007 with B1 + M1 + m1 design.md-table-vs-canonical-references catches that the 8-dim Critic likely shrugged off). The dimension addition is functional, validating slice-006 user-override-of-Meta-Critic empirically.

- **`--repo-root` flag claim drift at design.md** (Critic M1 catch). Design said "CLI mirrors `tools/install_audit.py` shape (`--claude-dir`, `--repo-root`, `--json`, `--strict`)" — but `install_audit.py:339-352` has only `--claude-dir`, `--strict`, `--no-strict`, `--json`. `--repo-root` is an EXTENSION beyond `install_audit.py`'s flag set, not a mirror. **Cross-cutting-conformance Dim 1 sub-class hit** (tooling-doc-vs-impl parity) — caught at /critique by Dim 9 prompting the parity check. Without the catch, the design.md claim would have been a false statement of architectural inheritance.

- **Voluntary Critic ROI now hardens to N=7/7 with 5 of 7 design-stage failure catches** — methodology pattern continues hardening. The `/slice` skill could update its default heuristic to set `critic-required: true` when slice scope includes "modifies in-house audit / agent prompt / methodology rule" — i.e., `agents/`, `tools/*audit*.py`, `~/.claude/...`. **Methodology-discipline-refinement candidate**, not a code change. Track for slice-009+ if the pattern stays N/N at 100%.

## Deferred

- **`refine-bc-1-anchors-with-negative-context`** — N=3 BC-1 false-positive class (slice-005+006+007); meets BC-1 promotion threshold per slice-006 reflection lesson #4. Estimated ~30-60 min. **Strongest slice-008 candidate by promotion-threshold-met.**
- **`refine-dim-9-with-design-md-tables-sub-clause`** — N=2 (slice-006 DEVIATION + slice-007 Critic B1 `VERSION` rename). Estimated ~30 min. Add a sub-clause to Dim 9 of `agents/critique.md` covering "design.md mechanical tables vs methodology canonical references / install-time renames".
- **INST-2 generalization (general content-equality across all installed files)** — wait for N=2 evidence on drift in files other than `agents/critique.md`. Per ADR-006, defer until drift recurs on a second file (e.g., `agents/critique-review.md`, `agents/critic-calibrate.md`, `~/.claude/build-checks.md`).
- **Em-dash → cp1252 / prose-pin substring uniqueness** — both N=1 currently; watch for recurrence in slice-008+ before promoting to BC-1 / Dim 9 sub-clause.
- **From slice-006 carryover (still open)**: `add-critique-agent-content-equality-audit` — **SHIPPED in slice-007 as CAD-1**.
- **From slice-005 carryover**: `fix-bc-1-archived-slice-heuristic` (~30 min, pre-existing bug; workaround `--project-checks` acceptable).
- **From slice-004 carryover**: `add-csp-1-docstring-or-regex` (~30-60 min, sibling tooling-bug pattern).
- **R-1 deeper fix** (orchestrator pre-cd or parent-thread pre-compute for /diagnose) — risk-register HIGH-band open risk; documented-constraint workaround still acceptable per slice-002.
- **R-2 programmatic test of cwd-warning runtime emission** — risk-register LOW-band open risk; deferred until evidence of regression.

## Critic calibration

Per **TRI-1**, scoring each finding from `critique.md` `## Triage` table against build + validate reality:

- **B1** (Out-of-repo files touched table — `ai-sdlc-VERSION` "In-repo path" wrong; recurrence of slice-006 DEVIATION class at N=2): **VALIDATED** — disposition ACCEPTED-FIXED at /critique; reality confirmed empirically (`ls VERSION ai-sdlc-VERSION` shows VERSION exists; ai-sdlc-VERSION does NOT). Without B1 catch, the design's forward-sync table would have pointed at a nonexistent in-repo file; build would have either failed at the `Copy-Item` step or silently used a wrong path. **Strong VALIDATED + fatal save.** Critic was right; cross-cutting-conformance Dim 9 sub-class N=2 confirmed at design time.
- **B2** (AC #4 doesn't gate the PMI-1 cleanliness post-build that design.md claims to fix): **VALIDATED** — disposition ACCEPTED-FIXED at /critique; AC #5 added; reality confirmed at /validate-slice (pre-slice PMI-1 was failing with version-mismatch; post-build clean). Without B2 catch, slice-006 escape would have silently persisted. **Strong VALIDATED + fatal save.** Critic was right.
- **M1** (`--repo-root` flag claimed mirrored from `install_audit.py` but absent there): **VALIDATED** — disposition ACCEPTED-FIXED; design.md updated to clarify `--repo-root` is extension; reality confirmed (`install_audit.py:339-352` has only --claude-dir/--strict/--no-strict/--json; the new audit's argparse adds --repo-root explicitly). Critic was right.
- **M2** (line-range pin too brittle vs slice-006 substring-only precedent): **VALIDATED** — disposition ACCEPTED-FIXED; mission-brief TF-1 plan notes updated to substring-only with positive + negative substrings. Reality confirmed at build: substring-only assertion pattern works (`test_critic_calibrate_skill_prose_instructs_in_repo_canonical_with_forward_sync` passed). Critic was right.
- **M3** (stale `build/lib/` shadow risk; sanity-check refusal needed): **VALIDATED** — disposition ACCEPTED-FIXED; sanity-check refusal added to audit; reality confirmed at /validate-slice (`test_repo_root_without_plugin_yaml_or_install_md_exits_usage_error` PASSES; real subprocess on tmp_path with no plugin.yaml/INSTALL.md exits 2 with `'AI SDLC source root'` message). Critic was right.
- **m1** (canonical names shorthand vs `_CANONICAL_TOOLS` literals): **VALIDATED** — disposition ACCEPTED-FIXED; design.md uses `tools.X` literals. Cosmetic; preventive. Critic was right.
- **m2** (ADR-006 reversibility section thin vs ADR-005 standard): **VALIDATED** — disposition ACCEPTED-FIXED; expanded to 5 enumerated irreversibles (methodology-changelog append-only; build-log forensics; future-slice citations; git history non-monotonicity; `_CANONICAL_TOOLS` count). Critic was right.
- **m3** (Bash tool wrapper incompat on `$env:USERPROFILE`): **VALIDATED** — disposition ACCEPTED-FIXED; mission-brief AC #1 verification appended with parenthetical + agent-runnable equivalent. Reality confirmed: PowerShell direct execution worked correctly at /validate-slice. Critic was right.

**All 8 Critic findings VALIDATED. 0 FALSE-ALARM. 0 OVERRIDE-MISJUDGED. 0 NOT-YET.** Strongest tied with slice-006 (which was 11/11). Slice-007 is the second consecutive 100% Critic accuracy slice. The 8-dim Critic at /critique time caught both fatal saves (B1 + B2) — voluntary-Critic on cross-cutting tooling slices remains N=7/7 paid off with 5 of 7 design-stage failure catches.

**Missed by Critic** (the 8-dim Critic at /critique time):

- **DEVIATION-1 (prose-pin negative-substring false-positive on legitimate line-99 explanatory text)** — caught at /build-slice mid-slice smoke gate, not at /critique. Critic walked Dim 4 (Methodology-audit conformance / TF-1 row genuineness) and confirmed the substring-only pattern was correct, but didn't anticipate that even a substring-based pin can match legitimate negative statements containing the keyword. **Calibration class: cross-cutting conformance — testing-discipline / regression-guard substring uniqueness.** New sub-class hit; N=1 anecdote until promoted at N=2.

- **DEVIATION-2 (em-dash `—` → cp1252 byte 0x97 on Windows console; subprocess.run UTF-8 capture flake)** — caught at /build-slice mid-slice smoke gate. Critic walked Dim 8 (Web-known issues) + Dim 9 (Cross-cutting conformance — language-version) but didn't anticipate the Python-on-Windows console encoding intersection. **Calibration class: cross-cutting conformance — language-version-conformance + runtime-environment intersection (Python on Windows; cp1252 console default; subprocess UTF-8 capture).** New sub-class hit; N=1 anecdote until promoted at N=2.

**Pattern (cumulative across slices 001-007)**:

The cross-cutting-conformance miss-class is now **N=7 distinct slices, 14 sub-class hits**. Slice-007 sub-class hits:
- **NEW** Regression-guard substring uniqueness (testing-discipline) — N=1 (slice-007 DEVIATION-1)
- **NEW** Python-on-Windows console encoding (language-version + runtime-environment intersection) — N=1 (slice-007 DEVIATION-2)
- **STRENGTHENED** design.md mechanical tables vs canonical references — now N=2 (slice-006 DEVIATION-1+2 + slice-007 Critic B1) — **MEETS PROMOTION THRESHOLD**
- **STRENGTHENED** Tooling-doc-vs-impl parity — slice-007 M1 (`--repo-root` flag drift) — sub-class continues at N=4 across slices 002+003+006+007

**Of 14 cumulative sub-class hits, 11 are MISSED by 8-dim Critic** (slices 1-5: 8 hits, 0 caught at /critique; slice-006: 4 hits, 1 caught at /critique; slice-007: 5 hits, 3 caught at /critique). **Critic catch rate**: 0% (slices 1-5 with 8-dim Critic) → 25% (slice-006 with 8-dim Critic, post-CCC-1 surgical sub-bullets in Dim 1+4) → 60% (slice-007 with 9-dim Critic). **The 9-dim Critic is empirically strictly improving cross-cutting catch rate.**

**Voluntary Critic on cross-cutting tooling slices is now N=7/7 paid off, with 5 of 7 catching design-stage failures that would have failed at build time** (slice-003 m1 + slice-004 B1 + slice-005 B2 + slice-006 B1 + slice-007 B1+B2). Methodology pattern is load-bearing; could be promoted to /slice's default heuristic at slice-009+ if N stays at 100%.

**Effectiveness check baseline for next /critic-calibrate run** (after slices 6-15 archive, OR after slice-015 archives — whichever first): the cross-cutting miss class baseline was 10 misses across slices 1-5 per slice-006 user-override entry. Slice-006 contributed 4 hits (1 caught + 3 missed at 8-dim Critic). Slice-007 contributes 5 hits (3 caught + 2 missed at 9-dim Critic). Running total post-slice-007: **5 missed across slices 6-7 (target ≤2 across slices 6-15)** — **on track but accumulating**. If slices 8-15 continue at 1-2 misses per slice, target may be exceeded; refinement of the dimension's body (especially around design.md mechanical tables vs canonical references) would be needed.

## Lessons for next slice

- **`refine-bc-1-anchors-with-negative-context` is the strongest slice-008 candidate** by promotion-threshold-met (N=3 across slices 005+006+007). Estimated ~30-60 min. Addresses the recurring noise in BC-1 audits on methodology-vocabulary slices. Hybrid possible: refine BC-PROJ-1 + BC-GLOBAL-1 anchors AND/OR add a `negative-context anchors` schema field per BC-1 v0.10.0 conventions. **Slice-008 prerequisite question for /design-slice**: which of (a) refine existing rules' anchors with `vocabulary` / `meta-discussion` exclusions; (b) extend BC-1 schema with explicit `negative-anchors:` field; (c) hybrid.

- **Cross-cutting-conformance Dim 9 effectiveness is empirically validated at slice-007** (3 of 5 sub-class hits caught at /critique). The dimension is functional, not just structural. ADR-005's "Items that cannot be reverted" portion is empirically more load-bearing than v1 framed — reverting Dim 9 would lose a 60% catch rate improvement on cross-cutting conformance, not just the unified-pattern surface.

- **design.md mechanical tables (forward-sync, prerequisites, dependencies, install-time renames) need verification against in-house methodology rules' canonical inventories AND install-time conventions** — N=2 stable at slice-007 (slice-006 DEVIATION-1+2 + slice-007 B1). Promote to Dim 9 sub-clause refinement at slice-008+: `Refine Dim 9 sub-clause "Tooling-doc-vs-implementation parity" to include "design.md mechanical tables vs methodology canonical references / install-time renames"`.

- **Voluntary Critic on cross-cutting tooling slices is now N=7/7 paid off, with 5 of 7 design-stage failure catches.** /slice's default heuristic could be updated to set `critic-required: true` when slice scope includes "modifies in-house audit / agent prompt / methodology rule" — track for slice-009+ if N stays at 100%.

- **Bidirectional sha256 forensic capture is now N=2 stable** (slice-006 first; slice-007 second). Future slices touching `~/.claude/...` files should follow the Phase 0 + Phase 4 capture pattern. Promote to BC-1 / Dim 9 at N=3.

- **Two new Dim 9 sub-class candidates from slice-007 build deviations**: (1) Python-on-Windows console encoding (em-dash → cp1252; subprocess UTF-8 capture flake); (2) Regression-guard substring uniqueness (negative substring must be unique to deprecated content's surrounding phrasing, not just keyword). Both N=1; watch for recurrence at slice-008+.

- **Empirical-verification-at-design-time discipline is N=6 stable across slices** (added slice-007 Critic B1 empirical verification of `ls VERSION ai-sdlc-VERSION` + B2 empirical PMI-1 audit invocation as 6th instance). The cost is ~30 seconds; the savings are entire failed-design cycles.

- **TF-1 7-row plan with 2-surface AC #3 + 3-surface AC #3 (after Critic M3 added the sanity-check row) shows the schema-pin discipline scales**. Started at 4 rows in mission-brief; grew to 5 at /design-slice (option d hybrid two surfaces); grew to 7 at /critique (Critic M3 sanity check + Critic B2 PMI-1 gate). Per slice-006 lesson: schema-pin TWO-surface discipline. Slice-007 confirms it generalizes to N-surface for any AC with multi-surface coverage.

- **The slice-006 PMI-1 escape was a Critic-MISSED at slice-006** — the slice-006 8-dim Critic walked Dim 7 (Drift from vault) and caught the in-repo↔installed content drift (B1) but did NOT walk through `methodology-changelog.md` v0.20.0's PMI-1 + INST-1 invariants vs the slice's own `## Vault updates made` claims. **Calibration class: methodology-audit conformance** — already a Dim 4 sub-bullet, but the slice-006 instance shows the bullet's specificity needs sharpening on "claim made in `## Vault updates made` MUST be verifiable by running the corresponding audit". Possible refinement candidate at next `/critic-calibrate`.

## Vault updates made (thin vault)

- `architecture/lessons-learned.md` — slice-007 entry appended (see Step 5)
- `architecture/shippability.md` — slice-007 row 7 already added at /build-slice (`tests/methodology/test_critique_agent_drift.py` + 2 changelog tests + canonical-tools paired)
- `architecture/slices/slice-007-add-critique-agent-content-equality-audit/` — to be auto-archived in Step 6
- `architecture/slices/_index.md` and `architecture/slices/archive/_index.md` — to be regenerated in Step 6
- This slice's [`design.md`](design.md) — corrected at /critique time per Critic B1 (Out-of-repo table) + B2 (PMI-1 gate explicit) + M1 (`--repo-root` extension) + M3 (sanity-check refusal); reflects reality post-build
- This slice's [`mission-brief.md`](mission-brief.md) — TF-1 plan grew 4 → 5 → 7 rows across /critique + /build-slice; AC count 4 → 5 (Critic B2 added AC #5)
- This slice's [`build-log.md`](build-log.md) — Events section captures Phase 0 forensic + Phase 1 RED + Phase 2 build (with 2 mid-slice deviations) + Phase 3 smoke + Phase 4 sync + Phase 5 catalog + Phase 6 gates; Summary section finalized at slice end
- This slice's [`validation.md`](validation.md) — captures 5/5 ACs PASS + VAL-1 clean (Layer A 0 secrets + Layer B 0 hallucinated imports) + WS-1/ETC-1 default-off + shippability 7/7 (62 tests) + 3 reality surprises
- `methodology-changelog.md` (in-repo + `~/.claude/`) — v0.22.0 / CAD-1 entry added at /build-slice; sha256 FD6BBC0241F03396 both sides
- `VERSION` (in-repo) and `~/.claude/ai-sdlc-VERSION` — `0.21.0` → `0.22.0` (forward-sync with rename per `INSTALL.md:141`); sha256 464863EE696CA862 both sides
- `skills/critic-calibrate/SKILL.md` (in-repo + `~/.claude/`) — prose at lines 105-114 updated; sha256 FBABEA7045683814 both sides
- `tools/install_audit.py` — `_CANONICAL_TOOLS` 14 → 15; comment updated
- `plugin.yaml` — `version` 0.20.0 → 0.22.0 (closes slice-006 PMI-1 escape); tools list 14 → 15 (added `path: tools/critique_agent_drift_audit.py / rule: CAD-1`)
- `tests/methodology/test_critique_agent_drift.py` — NEW (5 tests, 180 lines)
- `tests/methodology/test_methodology_changelog.py` — extended with 2 tests for AC #4 + AC #5
- `tools/critique_agent_drift_audit.py` — NEW (242 lines; CAD-1 audit module; pip-installed via ai-sdlc-tools)
- `architecture/risk-register.md` — no new risks added (the 2 build-time deviations + cross-cutting-conformance sub-class hits are tooling/methodology gaps, not project risks; tracked in calibration log + this reflection)
- No ADRs superseded — ADR-006 stands as accepted; ADR-001..005 unrelated
