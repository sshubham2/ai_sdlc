# Code Review: Slice 065 bundle-064-code-critic-cleanup

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-23
**Result**: FINDINGS

## Summary

Code changes are minimal, well-scoped, and empirically verified PASS (all 8 tests in `tests/skills/code_review/test_code_review_skill.py` green at Phase B mid-slice smoke gate and Phase C SKILL.md fix verification). The bash_block scoping idiom soundly retires the M1/m1/m2 substring-leak class on the three slice-064 assertions; the canonical 3-composable-assertion shape (count + brace-group + co-location) properly distinguishes pre-fix from post-fix; the SKILL.md L42 STOP-guard insertion is POSIX-portable across bash/dash/sh (code-Critic empirically verified). One Minor surfaces from independent pass: the slice's own m3 fix (coordinate-vs-semantic ADR-061 citation, fixed in design.md by the design-Critic stack) has a residual sibling drift in `skills/code-review/SKILL.md:37` where the same `ADR-061 §Decision L60-67` coordinate-only pin survives. Three additional Minors (m2 DRY duplication N=3 across test functions, m3 SKILL.md L69 prose vs bash format parity drift, m4 design.md "byte-for-byte" overclaim) are advisory observations. **All 4 advisories DECLINED in-band per CRSI-1 v1 walking-skeleton + slice-063/064 precedent (N=2 cumulative declined-in-band)** — slice-066+ bundled cleanup nomination preserves the walking-skeleton boundary; CRSI-1 v1 advisory-only discipline holds. Calibration signal: the design-Critic stack's m-add-1 catch (shippability row narrative drift) + code-Critic's m1 catch (SKILL.md L37 sibling coordinate-pin) together exhibit the slice-040 N+1 doctrine signature — a Critic finding canonical drift in N-1 cells frequently leaves residual sibling drift in N's own artifacts.

## Changed files (in-scope)

```
skills/code-review/SKILL.md
tests/skills/code_review/test_code_review_skill.py
```

(Note: `architecture/shippability.md` was modified but is OUT-OF-SCOPE per the `':(exclude)architecture/**'` pathspec; surfaced informationally in m4 as a parallel cross-reference for /reflect deferral list.)

## Findings

### Blockers (advisory in v1 — slice-062+ will add verdict-driven block on /validate-slice)

None.

### Majors

None.

### Minors

#### m1: Cross-surface drift between design.md m3 fix and `skills/code-review/SKILL.md:37` — sibling-cell `ADR-061 §Decision L60-67` coordinate-pin survives

- **Claim under review**: `skills/code-review/SKILL.md:37` reads: *"Compute the slice's filtered code diff vs the default branch using the **union-of-three-sources** read mechanism (per [[ADR-062]], mirroring the slice-063 NAW-1 / [[ADR-061]] §Decision L60-67 pattern)."* The slice's own design-Critic stack flagged this exact "coordinate-without-semantic-content" pattern as `/critique` m3 against design.md and ACCEPTED-FIXED it at two design.md cite sites (`What's reused` + `Decisions made (ADRs)`).
- **Issue**: The m3 fix harmonized design.md's two cite sites with the semantic three-step resolver pattern but did NOT harmonize the third sibling cite site at `skills/code-review/SKILL.md:37` — the very file the slice's AC#3 modifies. The slice-064 SKILL.md edit introduced the `L60-67` coordinate pin; slice-065 modified that same SKILL.md but left the pin intact. Per Wiegers (consistency between requirement narrative and implementation manifest) + FBCD-1 sub-mode (a) cross-cell completeness — when a slice fixes a class on N-1 cells but leaves an N+1th cell carrying the same drift, the fix is incomplete. The meta-Critic at `/critique-review` caught one such residual sibling drift (m-add-1 shippability row), but this SKILL.md sibling drift was not surfaced. Slice-040 N+1 doctrine signature: a Critic finding the canonical drift in N-1 cells frequently leaves residual sibling drift in N's own artifacts.
- **Evidence**: `skills/code-review/SKILL.md:37` literally contains `[[ADR-061]] §Decision L60-67 pattern` (verified empirically via Grep). `tools/new_agent_warning_audit.py` (the canonical Python implementation) also carries an `ADR-061 §Decision L60-67` coordinate pin in its docstring. Per SUP-1, ADRs are append-only so the line numbers are durable — but the pin is reader-hostile (forces a fetch of ADR-061 to learn what's there) and asymmetric with the design.md fix.
- **Proposed fix**: Edit `skills/code-review/SKILL.md:37` to replace `[[ADR-061]] §Decision L60-67 pattern` with the semantic three-step resolver phrase used in design.md: `[[ADR-061]] §Decision pattern (three-step default-branch resolver: git symbolic-ref refs/remotes/origin/HEAD → git config init.defaultBranch → fail-fast with exit 2 + default-branch-unresolvable stderr)`. Then re-run `cp skills/code-review/SKILL.md ~/.claude/skills/code-review/SKILL.md` for OSDG-1 forward-sync. (Defer fix at `tools/new_agent_warning_audit.py` docstring to a future slice — out of slice-065's in-scope set.)

#### m2: New `test_skill_md_step_1_default_branch_resolver_stops_on_empty` and the two tightened tests re-derive `step_1_idx`/`step_2_idx`/`bash_start`/`bash_end` via duplicated literal find() chains — speculative DRY opportunity

- **Claim under review**: `tests/skills/code_review/test_code_review_skill.py` carries the same 6-line bash_block scoping idiom block three times (existing test at L111-L138 AC#1 tightening; existing test at L187-L201 AC#2 tightening; new test at L293-L309 AC#4 STOP-guard pin). Plus the same `assert bash_start >= 0 and bash_end > bash_start` guard.
- **Issue**: Per Fowler refactoring smell "duplicated code", the canonical bash_block scoping idiom is now duplicated 3× across `tests/skills/code_review/test_code_review_skill.py`. Future refactor risk: a Step 1 heading rename or bash-fence change would require synchronized edits in all 3 places; partial-fix drift is a foreseeable failure class (and would surface as test-suite divergence, not a single coherent failure). This is the same DRY-opportunity class the slice's design surfaced at the helper-derivation pattern but did not extract (per design.md "helper hoist deferred to slice-066+ for minimalism").
- **Evidence**: The canonical idiom appears verbatim at three sites in the post-slice-065 test file:
  - `tests/skills/code_review/test_code_review_skill.py:111-138` (Source-(iii) tightening)
  - `tests/skills/code_review/test_code_review_skill.py:187-201` (count tightening)
  - `tests/skills/code_review/test_code_review_skill.py:293-309` (new STOP guard test)
- **Proposed fix**: Extract a module-level helper `def _resolve_step_1_bash_block(body: str) -> str:` that performs the find chain + assertions + returns the `bash_block` slice. Each test function then becomes a 1-line call. Defer if the test count stabilizes at 3 (acceptable carrying cost); flag as candidate for slice-066+ test-helper extraction if N≥4 future tests reuse the idiom. Voluntary-restraint per slice-061 R-16 precedent for small-N duplication is also a defensible disposition.

#### m3: `skills/code-review/SKILL.md:69` error-case prose says "STOP with the BRANCH-1-shaped error" but the bash exit-2 message uses `default-branch-unresolvable:` (no "BRANCH-1" string) — narrative-vs-implementation parity drift

- **Claim under review**: `skills/code-review/SKILL.md:69` reads: *"`default-branch-unresolvable` (neither `git symbolic-ref` nor `git config init.defaultBranch` resolves): STOP with the **BRANCH-1-shaped error** and instruct user to re-run after default branch resolves."* The new bash insertion at L42 emits stderr `default-branch-unresolvable: neither origin/HEAD nor init.defaultBranch resolved` — no `BRANCH-1` substring.
- **Issue**: The L69 prose was written when Claude was the intended STOP-emitter (Claude reads prose at runtime, acts on it). The slice-065 AC#3 fix moves the STOP into the bash itself — but the bash's stderr message format doesn't carry the `BRANCH-1` qualifier the L69 prose references. A user (or future Claude) hitting the new bash exit-2 path sees a `default-branch-unresolvable` error and won't immediately connect it to "BRANCH-1-shaped". Lower importance than m1 because (a) the L69 prose's "BRANCH-1-shaped error" phrasing is itself informal (not a literal class identifier the user is expected to grep for), and (b) Claude reading the prose post-bash-exit would still derive the connection.
- **Evidence**: `skills/code-review/SKILL.md:69` carries the literal "BRANCH-1-shaped error" string. The new L42 bash echo carries no "BRANCH-1" substring. NAW-1's Python equivalent at `tools/new_agent_warning_audit.py:_USAGE_DEFAULT_BRANCH_UNRESOLVABLE` similarly omits "BRANCH-1" from its stderr — design.md's "mechanically equivalent to canonical NAW-1 Python implementation" parity claim is class-level (the kebab string `default-branch-unresolvable` IS the conceptual class identifier), not byte-for-byte.
- **Proposed fix**: Either (a) edit `skills/code-review/SKILL.md:69` to drop the "BRANCH-1-shaped error" qualifier and rephrase as "STOP and propagate the `default-branch-unresolvable` exit-2 error" — aligns prose with the actual emitted message, AND avoids implying a BRANCH-1-specific format the bash doesn't actually produce; OR (b) leave as-is and accept that "BRANCH-1-shaped" is informal Claude-readable narrative referring to the class-level pattern (NOT a literal substring discipline). Disposition discretion at Builder.

#### m4: Design.md's "mechanically equivalent to the canonical NAW-1 Python implementation … byte-for-byte translation" overclaims parity — the bash and Python error messages differ in body content

- **Claim under review**: `design.md` "Decisions made (ADRs)" cell and `design.md` "Inclusion-heuristic disposition" cell both claim the SKILL.md L42 bash insertion is *"mechanically equivalent to the canonical NAW-1 Python implementation at `tools/new_agent_warning_audit.py:_resolve_default_branch`"* and is a *"literal byte-for-byte translation of that Python contract"*.
- **Issue**: Empirically false on the message-body axis. NAW-1's Python `_USAGE_DEFAULT_BRANCH_UNRESOLVABLE` produces stderr `"NAW-1 usage error: default branch unresolvable (neither \`git symbolic-ref refs/remotes/origin/HEAD\` nor \`git config init.defaultBranch\` returned a value). Configure an \`origin/HEAD\` ref or set \`init.defaultBranch\`."` — a 4-clause structured message with rule-ID prefix + remediation. The SKILL.md bash echoes `"default-branch-unresolvable: neither origin/HEAD nor init.defaultBranch resolved"` — a 1-clause message with no rule-ID prefix and no remediation. They share (a) exit code 2, (b) stderr stream, (c) the kebab-case class identifier `default-branch-unresolvable`. They differ on (a) rule-ID prefix (`NAW-1 usage error:` vs absent), (b) remediation hint ("Configure an `origin/HEAD` ref or set `init.defaultBranch`" vs absent). Per Wiegers (assumptions must trace to evidence) — "byte-for-byte translation" is the overclaim; "class-level equivalence" would be the accurate framing.
- **Evidence**: `tools/new_agent_warning_audit.py:_USAGE_DEFAULT_BRANCH_UNRESOLVABLE` Python message body vs `skills/code-review/SKILL.md:42` bash echo string. Diff confirmed empirically.
- **Proposed fix**: Edit design.md's two overclaim sites to *"**class-level equivalent** to the canonical NAW-1 Python implementation … sharing the exit-2 contract + the `default-branch-unresolvable` kebab class identifier + stderr stream; the message bodies intentionally diverge — the Python form carries `NAW-1 usage error:` rule-ID prefix + a remediation clause, the bash form is condensed for orchestrator-prose readability."*

NOTE: design.md is in `architecture/**` which is OUT-OF-SCOPE per the `:(exclude)architecture/**` pathspec — surfaced here for code-Critic's parallel `/drift-check`-style cross-reference; in-scope to slice-065's reflection deferral list rather than slice-065's diff itself.

## Dimensions checked

- [x] **Unfounded assumptions** — m4 (NAW-1 parity overclaim in design.md "byte-for-byte translation" cells; the slice's own M3 fix in design.md still carries the residual overclaim — design.md is out-of-scope per pathspec exclusion, surfaced as parallel cross-reference). Empirically refuted via Python message-body diff against `tools/new_agent_warning_audit.py:_USAGE_DEFAULT_BRANCH_UNRESOLVABLE`.
- [x] **Missing edge cases** — Probed and verified safe:
  - Empty/null/zero (`$default=""` at both resolver returns): STOP guard fires correctly with `exit 2`.
  - POSIX portability (bash + dash + sh): all three shells exit 2 with stderr message (empirically verified).
  - CRLF vs LF: `skills/code-review/SKILL.md` is LF-only on disk; `Path.read_text(encoding='utf-8')` does universal-newline normalization; bash_block scoping idiom is line-ending agnostic.
  - Happy path (`$default="master"`): STOP guard short-circuits via `&&`; `git merge-base` proceeds; exit 0.
  - Missing closing fence (`bash_end=-1`): assertion `bash_end > bash_start` correctly fails.
  - Missing opening fence (`bash_start=-1`): assertion `bash_start >= 0` correctly fails.
  - Co-location with `stop_idx=-1` (pre-fix simulation): `fallback_idx < -1 < merge_base_idx` short-circuits False correctly.
  - **Edge case identified but NOT flagged**: second `bash` block in Step 1 silently invisible to assertions — `bash_start = step_1.find('```bash\n')` returns FIRST occurrence; future Step 1 refactor adding a second bash block (e.g., a "## Advanced usage" subsection) would carry regressions invisible to all three slice-065 assertions. Disposition: low probability (Step 1 is a single-prose-flow section; user discipline catches the case at /critique). Not filed as Minor because (a) hypothetical, (b) the broader `bash_block.count(...)` discipline would catch shape divergences within the first block.
- [x] **Over-engineering** — m2 (3× duplication of canonical bash_block scoping idiom across test functions) — speculative DRY opportunity per Fowler "duplicated code" smell. Not a Blocker or Major because (a) the duplication is small (6 lines × 3), (b) it's clearly factored as a self-documenting idiom in each test, (c) carrying cost at N=3 is acceptable. Flag for slice-066+ extraction if N≥4.
- [x] **Under-engineering** — none. All 5 ACs have backing code/test elements; mid-slice smoke gate Phase B math checks out (verified via running the suite — 8/8 PASS). Mutation tests confirm the 3 composable assertions distinguish pre-fix from post-fix correctly.
- [x] **Contract gaps** — none. The new bash exit-2 contract is well-formed (POSIX-portable brace group with trailing `;` before `}` per gnu.org/software/bash reference; `>&2` stream redirect is portable across all POSIX shells); the new test function signature carries a docstring + named composable assertions (a)/(b)/(c) with reference to specific /critique findings.
- [x] **Security** — none. The `echo "default-branch-unresolvable: …" >&2` message contains no external input (`$default` is by construction empty at the STOP guard point — verified by the upstream `[ -z "$default" ]` test); no shell-metacharacter injection vector. No new authn/authz/secrets/input-validation paths. SKILL.md change is a defensive fail-fast improvement (defense in depth — replacing silent fall-through with explicit failure surface).
- [x] **Drift from vault** — m1 (sibling-cell coordinate-pin drift at `skills/code-review/SKILL.md:37` — slice's own m3 fix harmonized design.md's two cells but missed this SKILL.md cell; canonical FBCD-1 sub-mode (a) cross-cell completeness gap, same class the meta-Critic caught at m-add-1 for shippability). m3 (SKILL.md L69 prose vs bash error-message format parity drift — informal "BRANCH-1-shaped error" prose vs literal `default-branch-unresolvable:` bash echo). Per Sommerville (requirements-design-code traceability): the slice fixes the bash-as-implementation but leaves two sibling SKILL.md prose surfaces (L37, L69) describing the same behavior in pre-fix terms.
- [x] **Web-known issues** — Verified POSIX brace-group semantics via gnu.org/software/bash/manual + BashGuide CompoundCommands references. Trailing `;` before `}` is required and present. Brace group does NOT create subshell, so `exit 2` propagates to the parent shell (intended behavior). `>&2` redirect is POSIX-portable. No findings — code choice is correctly idiomatic for POSIX shells circa 2026 (no deprecations, no quotas, no platform-version regressions affect this idiom).
- [x] **Cross-cutting conformance** —
  - **RSAD-1 (recursive self-application)**: The slice's design-Critic stack caught textbook RSAD-1 (B1 + B2 substring-leak class on slice's OWN fix block — slice-040 N+1 doctrine fired on first governed slice per slice-065 lineage). The fix is sound (canonical bash_block scoping idiom). Code-Critic's independent pass surfaces ONE residual sibling-cell drift (m1 SKILL.md L37 `L60-67` coordinate pin) — same RSAD-1 class the design-Critic caught + meta-Critic extended, but on a third sibling cell the stack didn't enumerate. Calibration note: when a slice fixes a coordinate-vs-semantic citation pattern in design.md, the cross-cell completeness check should enumerate ALL artifacts citing the same coordinate (design.md cells + SKILL.md prose + tool docstrings + ADR back-references).
  - **APED-1 (audit-parse-rule empirical-execution)**: Slice does NOT modify any `tools/**` audit parse rule. Code-Critic applied execute-don't-reason discipline to test assertions instead — empirically ran each of the 8 tests + simulated mutation tests on the bash_block (second-bash-block edge case, missing-fence cases, STOP-guard-in-comment mutation). All confirm the assertion math holds.
  - **EOL-DRIFT-1**: No new byte-equality compare on `.md` content; existing `_read()` helper uses `read_text(encoding='utf-8')` which normalizes universal newlines.
  - **Phantom-import in code**: None. All imports in the modified test file (`pathlib.Path`, `tests.methodology.conftest._resolve_slice_dir`) resolve to real symbols.
  - **NAW-1 mirror parity**: m4 surfaces the overclaim (design.md "byte-for-byte translation" is class-level equivalent, not literal byte-for-byte). Functional contract (exit code + class identifier + stream) is sound — only the narrative framing in design.md overclaims.
  - **Tooling-doc-vs-implementation parity**: New test function docstring at `tests/skills/code_review/test_code_review_skill.py` accurately describes the three composable assertions (a)/(b)/(c) and their distinguishing power — no docstring/code drift.

## Builder advisory disposition (CRSI-1 v1 — advisory only; not user-ratified TRI-1)

Per CRSI-1 v1 walking-skeleton + slice-063 N=1 / slice-064 N=2 cumulative precedent (all code-Critic advisories DECLINED in-band, nominated for next-slice bundled cleanup):

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| m1 | Minor    | DECLINED in-band, NOMINATED slice-066+ bundled cleanup | SKILL.md L37 sibling coordinate-pin — valid FBCD-1 cross-cell drift; small targeted fix on same file slice already modified (would also require re-running OSDG-1 forward-sync); slice-066+ bundled cleanup preserves walking-skeleton CRSI-1 v1 boundary and matches slice-063/064 precedent (all advisories declined in-band → bundled cleanup). |
| m2 | Minor    | DECLINED in-band, voluntary-restraint at N=3 carrying cost | 3× duplication of canonical bash_block scoping idiom is acceptable at small N; helper extraction defensible at N≥4. Per design.md "helper hoist deferred to slice-066+ for minimalism" — slice's own explicit deferral. |
| m3 | Minor    | DECLINED in-band, NOMINATED slice-066+ bundled cleanup | SKILL.md L69 prose vs bash format drift — narrative-vs-implementation parity gap; informal "BRANCH-1-shaped error" prose is not literal-substring discipline. Disposition Option (a) (rephrase L69 to align with actual bash format) preferred at slice-066+. |
| m4 | Minor    | DECLINED in-band, NOMINATED slice-066+ bundled cleanup | design.md "byte-for-byte translation" overclaim — out-of-scope per `:(exclude)architecture/**` pathspec but surfaced for /reflect deferral list; class-level equivalent IS correct framing. Fix at slice-066+ alongside m1/m3 SKILL.md sibling-cell fixes. |

**Pattern signature**: slice-066+ has now accumulated 7 nominated bundled cleanup items (slice-064 advisories: 3 deferred [substring-leak in BFRD-1 repro test + default-branch resolver no-programmatic-STOP + count assertion forward-looking gap, all retired this slice]; slice-065 advisories: 4 nominated [m1 SKILL.md L37 sibling coordinate-pin + m2 DRY duplication + m3 L69 prose drift + m4 design.md overclaim]). The slice-064 reflection said "All three findings cluster on the same SKILL.md / test file surfaces — bundled cleanup is the right shape" — slice-065's 4 advisories ALSO cluster on the same SKILL.md / test file / design.md surfaces. Continues to validate the bundled-cleanup discharge pattern.

**Calibration note for /reflect**: CRSI-1 v1 walking-skeleton ADVISORY-ONLY discipline holds at N=3 cumulative (slice-063 + slice-064 + slice-065 all declined-in-band). The slice-066 nomination for `/code-review` v2 (TRI-1 routing + verdict-driven block + AI-bloat passes) should preserve this advisory-only default for forward-looking quality findings (m2-m4 class), but consider elevating sibling-cell drift findings (m1 class) to verdict-block class — they're empirically grounded and structurally identical to the design-Critic stack's m-add-1 / RSAD-1 catch class.

## Sources

- [Command Grouping (Bash Reference Manual)](https://www.gnu.org/software/bash/manual/html_node/Command-Grouping.html)
- [BashGuide/CompoundCommands - Greg's Wiki](https://mywiki.wooledge.org/BashGuide/CompoundCommands)
