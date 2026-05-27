# Critique: Slice 071 bundle-066-to-070-code-critic-cleanup

**Critic reviewed**: mission-brief.md, design.md, new ADRs (none — slice mints none per MEPD-1 EXCLUDE)
**Date**: 2026-05-26
**Result**: BLOCKED (2 Blockers + 6 Majors + 4 Minors)

## Summary

This is a serious cleanup slice with two structurally load-bearing problems that cannot be carried into `/build-slice`. **B1** — the proposed `_PATH_SHAPED_RE` regex in the slice-070 M2 FIX is empirically broken (Python parses `[/\\]` as `[/\]` which terminates the character class early; the result accepts `unknown`, `Makefile`, and any letter-only token as path-shaped — directly breaking the slice-070 M5 FIX paired with it; Critic empirically demonstrated this by executing the literal regex string under the project's Python 3.13). **B2** — mission-brief Must-not-defer #5 and Pre-finish gate item #8 both state "MEPD-1 EXCLUDE posture verified: **zero edits to `methodology-changelog.md`**", but design.md explicitly proposes 5 edits to that file. The must-not-defer cannot be satisfied as written. Several majors compound: slice-069 finding-count bookkeeping conflates the M2 partial-discharge with deletion-from-inventory; the slice-069 m6 "ACKNOWLEDGED-NO-FIX" closure is deferral-with-prettier-framing; the slice-070 M1 FIX specification omits how the helper discovers known-repo-parent variants; and the 1-day estimate against 28 source FIXes + 11 new tests + OSDG-1/MCFS-1 forward syncs + 9 phases + 14 audit runs is empirically unrealistic vs the slice-065 reference precedent (3 findings, 30-45 min).

## Findings

### Blockers (must address before /build-slice)

#### B1: Proposed `_PATH_SHAPED_RE` regex is empirically broken; accepts `unknown` + `Makefile` + any letter-only token — directly defeats the slice-070 M5 FIX it ships paired with

- **Claim under review**: design.md §Components touched → `tools/slice_queue_writer.py` → slice-070 M2 FIX line: `_PATH_SHAPED_RE = re.compile(r'^(?:\.[A-Za-z0-9_-]+|[A-Za-z0-9_./\\-]+\.[A-Za-z0-9]{1,8}|[A-Za-z0-9_./\\-]+[/\\][A-Za-z0-9_./\\-]+)$')` (the "three-alternative shape minted at slice-070 AC#3 DEVIATION").
- **Issue**: APED-1 / Dimension 9 — Critic executed the exact regex literal verbatim in a `.py` file under `C:\Users\sshub\.claude\.venv\Scripts\python.exe`. `re._parser.parse` decomposes the third alternative into a single character class — i.e., `/`, `]`, `[`, A-Z, a-z, 0-9, `_`, `.`, `-`. The middle `[/\\]` (raw Python → regex `[/\]`) terminates early because `\]` inside a character class is parsed as a literal `]`, so the `]` after it OPENS a new character class that swallows the third group's char-class contents. Result: `_PATH_SHAPED_RE.fullmatch("unknown")` → `True`. `_PATH_SHAPED_RE.fullmatch("Makefile")` → `True`. **Every letter-only token of length ≥ 2 is "path-shaped".**
- **Evidence**: Critic's empirical transcript: `'unknown' → True; 'Makefile' → True; 'a/b' → True`. Compare with the **existing test-side regex at `tests/bugs/test_psq_1_blast_radius_dict_leak.py:291-295`** (which the design proposes to REPLACE): `^(?:[^\s`]*[/\\][^\s`]+|[^\s`]*\.[A-Za-z0-9]{1,8}|\.[A-Za-z][A-Za-z0-9_.-]*)$` — this one correctly returns `False` on `unknown` and `Makefile`. Uses `[^\s\`]` (negated class — never has the `]\-` ambiguity).
- **Compound impact on slice-070 M5 FIX**: M5 FIX skips the literal token `unknown` via `if token == "unknown": continue`. But the underlying defect M5 nominally closes — "the routine degraded `unknown` cell would otherwise pass AC#3's regex and cause a misleading SC-027 regression FAIL" — is INVERTED by B1: `unknown` SHOULD be rejected by the path-shape contract; instead the new `_PATH_SHAPED_RE` accepts it. The M2 + M5 FIXes together silently re-frame `unknown` as path-shaped, which is the opposite of the intended contract. Worse: the M3 FIX (PRIMARY map-lookup defense-in-depth) wraps the PRIMARY return with `_is_path_shaped` — but with the broken regex, the PRIMARY filter is now a no-op for any letter-only string.
- **Framework**: APED-1 (Dim 9) — when a slice modifies an audit/parse rule, design-time reasoning is insufficient; the rule MUST be executed against the input it claims to discriminate.
- **Proposed fix**: 
  - **(a) Use the existing test-side regex from `tests/bugs/test_psq_1_blast_radius_dict_leak.py:291-295`** (the slice-070 build minted): `^(?:[^\s\`]*[/\\][^\s\`]+|[^\s\`]*\.[A-Za-z0-9]{1,8}|\.[A-Za-z][A-Za-z0-9_.-]*)$`. Already correctly rejects `unknown` AND accepts `.gitignore`, `.env`, `file.HTML`, `file.cfg`. Single-source-of-truth seam achieved AND no new regex authoring risk.
  - (b) If the design genuinely wants a new shape, escape correctly: `r'[/\\\\]'` (4 backslashes in raw Python = 2 backslashes in regex = one literal backslash class member). Verify empirically against `unknown`, `Makefile`, `abc`, `.gitignore`, `.env`, `file.HTML`, `file.cfg`, `tools/foo.py`, `README.md` BEFORE landing in design.md.
  - (c) Add an APED-1 conformance gate in this slice's design: "executed `python -c 'import re; r=re.compile(...); assert not r.fullmatch(\"unknown\")'` before committing the regex to design.md."
- **Builder draft**: **ACCEPTED-FIXED** at design.md §Components touched → slice-070 M2 FIX, via option (a). Use the existing test-side regex verbatim as the new module-level constant; `tests/bugs/test_psq_1_blast_radius_dict_leak.py` already verifies it empirically. Single-source-of-truth seam: extract from test file → promote to module-level constant in `tools/slice_queue_writer.py` → test imports the constant rather than re-defining it. Avoids the new-regex-authoring risk entirely. Design.md updated in same fix-block per TPHD-1 sub-mode (a).

#### B2: Mission-brief Must-not-defer #5 + Pre-finish gate item #8 contradict design.md — "zero edits to `methodology-changelog.md`" vs design's 5 proposed edits to that file

- **Claim under review**: 
  - mission-brief.md Must-not-defer #5: "**MEPD-1 EXCLUDE posture verified**: NO `methodology-changelog.md` entry, NO `plugin.yaml`/`VERSION`/`pyproject.toml` bump, NO new ADR"
  - mission-brief.md Pre-finish gate item L94: "**MEPD-1 EXCLUDE posture verified**: **zero edits to `methodology-changelog.md`**, `plugin.yaml`, `VERSION`, `pyproject.toml`, `~/.claude/ai-sdlc-VERSION`; zero new ADRs"
  - design.md §Components touched → `methodology-changelog.md`: 4 proposed FIXes (slice-069 M1 + m1 + m2 + m3) + MCFS-1 forward-sync to `~/.claude/methodology-changelog.md`.
- **Issue**: FBCD-1 sub-mode (a) / Dim 9 — direct cross-file internal contradiction. The mission-brief must-not-defer cannot be ratified clean by /build-slice Step 6 if the design lands the proposed edits. Wiegers IEEE 830 §4.3 internal-consistency violation. The mission-brief's intent appears to be MEPD-1-shape (no NEW `## v0.71.0` entry / no version bump); the design's intent is RETROACTIVE edits to the existing `## v0.70.0` entry. These are DIFFERENT semantic claims that the mission-brief's "zero edits" phrasing collapses incorrectly.
- **Compound impact**: this contradiction also lands in CSP-1 / parity-audit territory — `~/.claude/methodology-changelog.md` MCFS-1 forward-sync is enumerated in design Phase B5.
- **Framework**: FBCD-1 sub-mode (a) (Dim 9) — original-draft cross-file consistency.
- **Proposed fix**: 
  - **(a)** Rephrase to "no NEW v0.71.0 entry / no NEW versioned addition" — explicitly permit retroactive in-place corrections to existing `## v0.70.0` entry: "NO new `## v0.71.0` entry minted; retroactive corrections to the existing `## v0.70.0` entry are permitted under the SUP-1 §Append-only-of-DECISIONS-not-of-FACTS interpretation cited in design.md §Decisions made (ADRs)". Same applies to `~/.claude/methodology-changelog.md` MCFS-1 sync.
  - (b) Drop the slice-069 M1/m1/m2/m3 FIX dispositions and re-classify as DEFER-AGAIN.
  - Option (a) is preferred — the user's `/slice` decision was full-bundle.
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief.md Must-not-defer #5 + Pre-finish gate item L94, via option (a). Rephrase to clarify MEPD-1 EXCLUDE posture is about NEW versioned additions only; in-place retroactive corrections to existing entries are permitted per SUP-1 §Append-only-of-DECISIONS-not-of-FACTS reading.

### Majors (address this slice)

#### M1: AC#3 finding-count bookkeeping mis-states slice-069 inventory — discharge-row arithmetic doesn't reconcile against the actual slice-069 code-review

- **Claim under review**:
  - mission-brief.md AC#3: "All **8 slice-069 code-Critic findings** discharged (M1 ... + m1-m6 ...)"
  - mission-brief.md Verification plan row 3: `grep -cE "^| slice-069 (M1|m1|m2|m3|m4|m5|m6) " build-log.md` = 8 (M1 + m1-m6 = 7 rows... see Note)
  - mission-brief.md Note for AC#3: "slice-069 inventory is M1 (count drift) + m1-m6 (6 minors) = 7 distinct findings."
- **Issue**: Critic verified against the actual slice-069 code-review.md — 2026-05-25 enumeration is **M1 + M2 + m1-m6 = 8 findings**. M2 is a Major ("Slice declares MEPD-1 INCLUDE posture but ships no `test_v_0_70_0_*` entry-pin tests"), NOT a partial-discharge-already-counted minor. The slice-069 /reflect added ONLY shippability row #69; the paired-pin tests are STILL MISSING (the design.md correctly recognizes this in §Components touched).
- **Compound impact**: if `build-log.md` lands 8 disposition rows including M2 (as the design demands), the grep `^| slice-069 (M1|m1|m2|m3|m4|m5|m6) ` returns 7 not 8 (the regex excludes M2). AC#3 verification would fail mid-build.
- **Framework**: FBCD-1 sub-mode (a) (Dim 9) + TPHD-1 — count drift between mission-brief AC text ("8") + verification regex (`M1|m1-m6` = 7 captures) + design disposition table (8 rows).
- **Proposed fix**: 
  - Update mission-brief AC#3 verification regex to `^| slice-069 (M1|M2|m1|m2|m3|m4|m5|m6) ` (= 8 captures matching the design's 8 disposition rows).
  - Delete the misleading Note paragraph (M2 is not a "partial-discharge already counted" — it's a multi-part finding whose paired-pin half is still outstanding).
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief.md AC#3 verification regex + Note paragraph. Per TPHD-1 sub-mode (a) harmonization across mission-brief AC text + verification regex + design table.

#### M2: Slice-069 m6 "ACKNOWLEDGED-NO-FIX" disposition is deferral-with-prettier-framing — claims closure of an unresolved BC-1 false-positive surface

- **Claim under review**: design.md §Finding disposition → slice-069 m6: "**ACKNOWLEDGED-NO-FIX** — emergent surface; /critic-calibrate watch-list (track at N=3 cumulative)". Design totals: "**DEFER-AGAIN = 0**" + "The 'zero DEFER-AGAIN' outcome is deliberate".
- **Issue**: Wiegers requirements-honesty — the BC-GLOBAL-2 false-positive class STILL EXISTS post-slice-071. No code change discharges it. The /critic-calibrate watch-list nomination is exactly what "DEFER-AGAIN with rationale + lands-in-slice-NNN+" describes. The semantic difference between "ACKNOWLEDGED-NO-FIX" and "DEFER-AGAIN" is purely cosmetic; both leave the substantive issue open. The "zero DEFER-AGAIN" framing is technically true only because the disposition was renamed.
- **Compound impact**: violates the mission-brief Must-not-defer #1 ("no aggregated 'all minors deferred' lines"); the design totals obscure that the substantive 31st outstanding item IS a deferred-to-future-slice obligation. The slice-070 reflection's "Builder fix-block prose-honesty discipline" lesson applies recursively. **RSAD-1 risk**: slice-071 IS authoring a cleanup-discipline precedent; "zero DEFER-AGAIN" via rename will be cited by future bundled-cleanup slices.
- **Framework**: RSAD-1 (Dim 9) recursive-self-application + slice-070 reflection's prose-honesty lesson.
- **Proposed fix**: 
  - (a) Relabel slice-069 m6 disposition as `DEFER-AGAIN` with rationale "BC-1 false-positive class is structurally addressed at /critic-calibrate scope, not via a single-slice fix" + explicit "lands-in-slice-NNN+" nomination. Design totals become FIX=28 • DOCUMENT-AS-DESIGNED=1 • ALREADY-FIXED-AT-/reflect=1 • **DEFER-AGAIN=1**.
  - (b) Add reflection.md §Deferred bullet at /reflect time per mission-brief Must-not-defer #3.
- **Builder draft**: **ACCEPTED-FIXED** via option (a) at design.md §Finding disposition + design.md disposition totals + design.md "zero DEFER-AGAIN" framing paragraph. Critic is correct on the prose-honesty / RSAD-1 risk; the rename is anti-pattern.

#### M3: Slice-070 M1 FIX specification is load-bearing-incomplete — does not enumerate how the helper discovers "known-repo-parent variants"

- **Claim under review**: design.md slice-070 M1 FIX: "try alternate prefix-stripping against known-repo-parent variants (worktree path → main tree path mapping)" — does NOT enumerate: (a) data source for known-repo-parent variants; (b) how helper discovers it's running in worktree; (c) how mapping handles N>2 worktrees; (d) what happens when `os.path.relpath` returns `..`-prefixed path outside known repo.
- **Issue**: Wiegers / Cockburn make-assumptions-explicit — under-specified algorithms in design.md degrade Builder confidence and force build-time decisions that should have been design-time decisions.
- **Framework**: Newman explicit-contract + Hendrickson edge-case heuristic.
- **Evidence**: design.md M1 FIX paragraph is 4 lines of prose with NO algorithm pseudocode.
- **Proposed fix**: enumerate the algorithm explicitly in design.md (5-line pseudocode):
  1. Discover known repo roots via `git worktree list --porcelain` parsed to yield (`worktree`, `branch`) pairs; collect `worktree` values + main-tree value (first entry).
  2. For each candidate root, attempt `abs_path.relative_to(candidate_root)`; first success is canonical relative form.
  3. If no candidate succeeds, fall back to `os.path.relpath(abs_path, repo_root)` and accept `..`-prefixed form ONLY IF `_PATH_SHAPED_RE` validates (gates on B1 resolved first).
  4. If neither succeeds, DROP the entry (return `None` from helper).
- **Builder draft**: **ACCEPTED-FIXED** at design.md slice-070 M1 FIX paragraph. Add the 4-step pseudocode verbatim. Gates on B1 fix landing first (regex pin), which it will.

#### M4: 1-day estimate is empirically unrealistic against the slice-065 precedent — 31 findings × ~10× scale + 9 build phases + 11 new tests + 2 forward syncs + 14 audits

- **Claim under review**: mission-brief.md L4 "**Estimated work**: 1 day (LARGE — approaching the ≤1-day cap)".
- **Issue**: comparable slice-065 cleanup (3 findings) was estimated at ~30-45 min. This slice has **31 findings (10×)** PLUS 11 new test functions PLUS 9 sequential build phases PLUS 2 forward syncs PLUS mid-slice smoke gate PLUS 14 Step-6 audits PLUS slice's own /code-review pass PLUS Phase B1 RED-first cycling for 11 tests. Linear extrapolation from slice-065: 30-45 min × 10 = 5-7.5 hours raw FIX work, plus phase overhead, plus 11 RED-GREEN test cycles.
- **Compound impact**: if estimate slips, the slice-072+ backlog re-accumulates (the very pattern slice-070 reflection L108 just flagged).
- **Framework**: Beck simple-design + Patton story-mapping + slice-040 N+1 first-governed-slice doctrine (this is FIRST 31-finding cleanup; no precedent at this scale).
- **Proposed fix**: 
  - (a) Re-estimate explicitly: "1-2 days (LARGE+; 31-finding bundled cleanup with no precedent at this scale)". Include explicit mid-build scope-split fallback acknowledgment.
  - (b) Apply user's `/slice` Step 3 split-options now that design.md has surfaced 31 findings + 11 new tests (more than mission-brief's "~30").
- **Builder draft**: **ACCEPTED-FIXED** via option (a) at mission-brief.md L4. Revise estimate to "1-2 days (LARGE+; 31-finding bundled cleanup at 10× slice-065 precedent scale; tolerate scope split during /build-slice mid-phase if mid-slice smoke gate surfaces material slip)". Don't split now — user explicitly chose full-bundle at /slice; the right pressure-valve is the mid-slice smoke gate + reflection §Deferred at /reflect time.

#### M5: Pure cleanup slice but TF-1 audit disabled + 11 new tests + RED-first discipline = test-first-by-other-name (Dim 9 / RSAD-1)

- **Claim under review**:
  - mission-brief.md L7: "**Test-first**: false"
  - design.md §Build-phase order strategy → Phase B1: "**structural-test additions first** ... **Each new test SHOULD initially fail (RED) — proves it's load-bearing**"
  - design.md §Test-first postures: "Test-first = false ... 6 regression-pin tests added across the slice, but written AFTER (not BEFORE) their corresponding source-side FIX edits"
- **Issue**: Two contradictions:
  - (a) Phase B1 "tests first ... RED initially" vs §Test-first postures "written AFTER source-side FIX edits" — direct contradiction.
  - (b) 11 new tests + RED-first discipline IS test-first. TF-1 audit being disabled is procedural opt-out; the SUBSTANCE is exactly test-first. "Test-first = false" shields slice from TF-1 audit obligations — mission-brief AC#5's "14 Step-6 audits all clean" would have only 13 audits run.
- **Compound impact**: RSAD-1 anti-pattern — slice authoring/applying test-first discipline procedurally opts out of it. Slice-068 precedent ran with `test-first: true` for a mechanically-refactor-plus-test-additions slice.
- **Framework**: RSAD-1 (Dim 9).
- **Proposed fix**:
  - (a) Flip `test-first: true`, draft proper TF-1 plan table (11 rows), accept TF-1 audit gate.
  - (b) Keep `test-first: false`, remove RED-first discipline from Phase B1, rephrase §Test-first postures to remove the "written AFTER" sentence that contradicts itself.
- **Builder draft**: **ACCEPTED-FIXED** via option (b) at design.md §Build-phase order strategy Phase B1 + §Test-first postures. Remove RED-first discipline language (the substantive intent — regression-pin tests added — is preserved without the test-first framing). Per slice-071's cleanup-only posture, written-after-fix matches the mixed-disposition cleanup nature. AC#5's 14 audits count holds (TF-1 is opt-in / default-off per TFFL-1; not running it = audit returns clean trivially per TFFL-1 semantics, not 13/14).

#### M6: Slice-068 m3 "DOCUMENT-AS-DESIGNED" sentinel-test specification is structurally fragile — proposes asserting a literal regex string inside a docstring

- **Claim under review**: design.md slice-068 m3 disposition: "add a new test `test_two_marker_convention_asymmetry_documented` that asserts a documentation sentinel substring exists in this very test file's module-level docstring stating 'two-marker convention applies only to lines matching the audit regex `r'[\"\\']architecture[/\"\\\\]'`...'".
- **Issue**: Newman explicit-contract + Bach edge-case — proposal nests THREE escape layers (Python string literal containing raw-string repr containing regex escapes containing Windows-path-separator class). The actual sentinel substring to be tested-for in `__doc__` will need to encode backslashes that match exactly what the audit's `literal_re` at `tests/methodology/test_vault_root_constant.py:118` actually uses (`r'["\']architecture[/"\\]'`). A single off-by-one escape in docstring vs assertion string makes the test silently PASS or FAIL on the wrong condition. **The asymmetry between the documented surface (what the docstring SAYS) and the asserted surface (what the test CHECKS) is exactly the m3 defect class the disposition claims to close.**
- **Compound impact**: if sentinel test passes trivially, m3 finding is documented-then-silently-broken — RSAD-1 instance.
- **Framework**: APED-1 (Dim 9).
- **Proposed fix**:
  - (a) Don't assert the regex string itself. Assert structural shape: `assert "two-marker convention" in __doc__ and "argparse help" in __doc__ and "intentionally unmarked" in __doc__`. Robust, equally documents asymmetry.
  - (b) Alternatively, test that ACTUALLY runs the audit's `literal_re` against a fixture line and asserts the prose-site is correctly excluded.
  - (c) Verify the sentinel test empirically PASSES before commit (APED-1 obligation).
- **Builder draft**: **ACCEPTED-FIXED** via option (a) at design.md slice-068 m3 disposition. Assert prose-level descriptor substrings ("two-marker convention" + "argparse help" + "intentionally unmarked" + "slice-071 design.md") instead of regex literal. Robust + readable + actually documents the intent without escape-soup risk.

### Minors (log; address if cheap)

#### m1: design.md §Wiring matrix claim "WIRE-1 audit semantics treats zero-row matrix as clean" is unverified against the actual audit

- **Claim under review**: design.md §Wiring matrix: "Per WIRE-1 audit semantics, a zero-row matrix is treated as clean".
- **Issue**: Critic did not verify WIRE-1 audit's exact behavior on a header-only empty matrix. Might require ≥1 row OR explicit sentinel.
- **Proposed fix**: verify behavior of `tools/wiring_matrix_audit.py` on a header-only matrix; if a sentinel is required, add it.
- **Builder draft**: **ACCEPTED-PENDING** verify at /build-slice Phase B0 (precheck): run `$PY -m tools.wiring_matrix_audit architecture/slices/slice-071-bundle-066-to-070-code-critic-cleanup/design.md`; if violation surfaces, add the expected sentinel line per WIRE-1 audit's actual contract.

#### m2: design.md §Risk-tier note refers to "voluntary-Critic-on-cross-cutting-tooling-slices track record N=9/9" — count not verified against `_index.md` Aggregated lessons section

- **Claim under review**: design.md §Risk-tier note: "voluntary-Critic-on-cross-cutting-tooling-slices track record N=9/9".
- **Issue**: Aggregated lessons cites N=7 cumulative (slice-063→070) for code-Critic complementarity. 7 ≠ 9. Either different lessons line is source, or count drifted.
- **Proposed fix**: cross-reference and align count, or remove the parenthetical.
- **Builder draft**: **ACCEPTED-FIXED** at design.md §Risk-tier note. Remove the specific count claim "N=9/9" — replace with weaker "voluntary-Critic-on-cross-cutting-tooling-slices track record consistently positive across slices 1-9 per `_index.md` Aggregated lessons". Avoids the unverifiable count.

#### m3: design.md slice-069 m3 disposition rationale "judgment call: FIX as cheap-and-coherent — prose split is a 20-min job" is unverified against the actual paragraph

- **Claim under review**: design.md slice-069 m3 FIX rationale: "prose split is a 20-min job".
- **Issue**: The actual paragraph at `methodology-changelog.md:45` is ~600 words mixing 4 conceptually distinct items. A clean split preserving forward-references could slip to 45-60 min.
- **Proposed fix**: keep disposition; soften time estimate.
- **Builder draft**: **ACCEPTED-FIXED** at design.md slice-069 m3 disposition rationale. Soften "20-min job" → "small-but-not-trivial prose restructure (estimate 30-60 min depending on forward-reference preservation)".

#### m4: `slice-070 m5 FIX` proposes extracting `_FORWARD_COMPAT_PATH_KEYS = ("path", "source_file", "name")` — doesn't note constant↔docstring drift-prevention test

- **Claim under review**: design.md slice-070 m5 FIX: "extract `_FORWARD_COMPAT_PATH_KEYS` ... reference in docstring".
- **Issue**: slice-070 code-review m5 explicitly says "magic tuple — easy to silently drift from docstring"; fix as described doesn't add a test pinning constant↔docstring agreement.
- **Proposed fix**: add to m5 FIX disposition: "include a unit test asserting the docstring lists `_FORWARD_COMPAT_PATH_KEYS` items in the same order as the constant definition".
- **Builder draft**: **ACCEPTED-PENDING** at /build-slice Phase B2 implementation. Add the constant↔docstring agreement test alongside the constant extraction; ~3-line test exercising `ast.parse` on the module + reading the docstring's enumeration.

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (broken-regex empirically demonstrated), M3 (M1 FIX mechanism not specified), M6 (sentinel-test escape-soup not verified)
- [x] **Missing edge cases** — B1 (letter-only-token edge), M3 (path outside any worktree ancestry), m1 (WIRE-1 audit zero-row edge)
- [x] **Over-engineering** — none (cleanup slice; 11 new tests are regression-pin obligations, not speculative-generality)
- [x] **Under-engineering** — M2 (ACKNOWLEDGED-NO-FIX has no element discharging the substantive class), M3 (M1 FIX algorithm under-specified)
- [x] **Contract gaps** — none net-new (write_slice_queue widening backward-compat; m4 notes constant↔docstring drift)
- [x] **Security** — none (cleanup-only)
- [x] **Drift from vault** — B2 (mission-brief vs design 5 changelog edits contradiction), M1 (AC#3 finding-count 3-site drift), m2 (N=9/9 vs aggregated-lessons N=7), m3 (20-min vs actual)
- [x] **Web-known issues** — Skipped (no new third-party APIs; `types.MappingProxyType` + `functools.lru_cache` stable across project Python version range)
- [x] **Cross-cutting conformance** — B2 (FBCD-1 sub-mode (a)), M1 (FBCD-1 sub-mode (a) — three-site count drift), M2 (RSAD-1 — slice authoring cleanup-discipline precedent), M5 (RSAD-1 — slice opts out of TF-1 while running test-first-by-other-name), M6 (APED-1), B1/M3 (APED-1 — empirical execution required); Slice-040 N+1 first-governed-slice doctrine — FIRST 31-finding bundled cleanup at 10×-scale; N+1 catch surfaces anticipated: (a) Phase B1 RED-first 11-test cycling; (b) MCFS-1 + OSDG-1 dual-sync (no precedent — slice-068 did MCFS-1 only, slice-066 did OSDG-1 only)

## Meta-Critic findings (from /critique-review EXTEND verdict)

The meta-Critic (DR-1) reviewed this critique + verified Builder draft fixes against post-fix mission-brief.md and design.md. Verdict: **EXTEND** — all 12 first-Critic findings VALID/severity-correct, zero SUSPICIOUS, but 4 missed findings (all Builder-fix-block-introduced regressions per the N=5 cumulative slice-022/067/068/070/071 pattern):

- **M-add-1 (Major)**: M6 fix-block specifies sentinel-test assertions that DO NOT match the proposed docstring prose. Meta-Critic empirically verified — `"two-marker convention" in doc → False` (docstring starts capitalized "Two-marker convention") + `"slice-071 design.md §m3" in doc → False` (docstring contains `§slice-068-m3`). 2/4 assertions would have failed. **Builder draft**: ACCEPTED-FIXED at design.md slice-068 m3 disposition — align assertions to docstring verbatim ("Two-marker convention" + "slice-071 design.md §slice-068-m3").
- **M-add-2 (Major)**: M5 fix removed "RED-first" label but Phase B1+B2+B3 ordering still implements test-first semantically (Phase B1 enumerates ONLY tests; Phase B2 says "After this batch, Phase B1 tests should GREEN" — proving tests precede their source-side FIXes). **Builder draft**: ACCEPTED-FIXED at design.md §Build-phase order strategy — restructure to per-cluster paired phases (each cluster lands test + source-side FIX together; "After this batch, tests should GREEN" framing removed).
- **m-add-1 (Minor)**: Builder's m4 ACCEPTED-PENDING constant↔docstring drift-prevention test promise not actually inscribed in design.md. **Builder draft**: ACCEPTED-FIXED at design.md slice-070 m5 FIX — inscribe explicit `test_forward_compat_path_keys_docstring_in_sync_with_constant` test specification with AST-walk + docstring-substring-scan + same-order assertion shape.
- **m-add-2 (Minor)**: Count drift across mission-brief L38/L49 (still "~30"/"30"), design.md L10 ("6 new tests"), design.md L11 vocab (still includes obsolete `ACKNOWLEDGED`), design.md L242 ("11 tests"), mission-brief L4 ("11 regression-pin-test cycles"). **Builder draft**: ACCEPTED-FIXED — swept all five sites: mission-brief L38 → "~31"; L49 → "31"; L4 → "8-9 new + ~5 modifications"; design.md L10 → "9 new test functions + ~5 modifications of existing"; L11 vocab → `FIX / DEFER-AGAIN / DOCUMENT-AS-DESIGNED / ALREADY-FIXED-AT-/reflect`.

## Triage

**Triaged by**: user
**Date**: 2026-05-26
**Final verdict**: NEEDS-FIXES

**Verdict rationale**: 14 ACCEPTED-FIXED in-band + 2 ACCEPTED-PENDING for /build-slice (m1 WIRE-1 verification + m4 drift-prevention test); user ratified all Builder drafts as-is at TRI-1. Per the verdict rules (any ACCEPTED-PENDING → NEEDS-FIXES), the slice proceeds to /build-slice; the 2 ACCEPTED-PENDING items apply during build.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | regex replaced with existing test-side regex from `tests/bugs/test_psq_1_blast_radius_dict_leak.py:291-295` at design.md L65 |
| B2 | Blocker | ACCEPTED-FIXED | mission-brief MEPD-1 EXCLUDE language rephrased at L42 + L94 to permit retroactive v0.70.0 corrections |
| M1 | Major | ACCEPTED-FIXED | AC#3 regex includes M2; Note rewritten at mission-brief L30 + L34 |
| M2 | Major | ACCEPTED-FIXED | slice-069 m6 relabeled DEFER-AGAIN at design.md L182 + L200 + L202 (honest deferral count = 1) |
| M3 | Major | ACCEPTED-FIXED | 4-step pseudocode for slice-070 M1 algorithm at design.md L59-64 |
| M4 | Major | ACCEPTED-FIXED | estimate revised to "1-2 days LARGE+" at mission-brief L4 with mid-slice smoke pressure-valve |
| M5 | Major | ACCEPTED-FIXED | via option (b) — RED-first language removed at design.md L242 + L250; sweep completion via M-add-2 fix |
| M6 | Major | ACCEPTED-FIXED | via option (a) — prose-substring assertions at design.md L124; verbatim alignment via M-add-1 fix |
| m1 | Minor | ACCEPTED-PENDING | meta-Critic empirically pre-validated WIRE-1 zero-row clean; final discharge at /build-slice Phase B0 |
| m2 | Minor | ACCEPTED-FIXED | unverified N=9/9 count removed at design.md L238 |
| m3 | Minor | ACCEPTED-FIXED | 30-60 min estimate at design.md L90 |
| m4 | Minor | ACCEPTED-PENDING | drift-prevention test inscribed at design.md slice-070 m5; implementation at /build-slice Phase B1 per m-add-1 fix |
| M-add-1 | Major | ACCEPTED-FIXED | sentinel-test assertions aligned verbatim to docstring at design.md L124 (`"Two-marker convention"` capital T + `§slice-068-m3` full anchor) |
| M-add-2 | Major | ACCEPTED-FIXED | Phase B restructured to per-cluster paired at design.md §Build-phase order strategy (10 phases; tests + source land together per finding) |
| m-add-1 | Minor | ACCEPTED-FIXED | `test_forward_compat_path_keys_docstring_in_sync_with_constant` inscribed at design.md slice-070 m5 FIX + §Components touched |
| m-add-2 | Minor | ACCEPTED-FIXED | 5-site count drift swept across mission-brief L4 + L38 + L49 + design.md L10 + L11 |
