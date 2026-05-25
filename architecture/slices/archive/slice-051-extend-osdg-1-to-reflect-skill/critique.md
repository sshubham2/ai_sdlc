# Critique: Slice 051 extend-osdg-1-to-reflect-skill

**Critic reviewed**: mission-brief.md, design.md, ADR-053 (new)
**Date**: 2026-05-19
**Result**: NEEDS-FIXES

## Summary

The "near-mechanical clone of slice-049" framing is largely accurate and the load-bearing infrastructure (EOL-agnostic comparator, `.gitattributes skills/**/SKILL.md eol=lf` glob, entry-pin content-bearing shape, decoupling-audit `clean` classification, ADR-053 next-free number) all check out against the live repo. One real Major: the slice's own AC2/mid-slice perturbation procedure collides with a pre-existing test (`test_ai_sdlc_version_forward_sync.py`) that also reads `skills/reflect/SKILL.md`, creating a full-suite false-FAIL window the design does not acknowledge. Two further Majors concern the AC2 drift-test-is-not-a-content-pin gap and the shippability row-segmentation pipe-escaping discipline.

## Findings

### Blockers (must address before /build-slice)

None. Version legs consistent (VERSION = ai-sdlc-VERSION = plugin.yaml = 0.58.0, next = 0.59.0), ADR-053 is the correct next free number, no pre-existing test pins reflect's OLD unguarded state, no stale enumeration/count literal breaks.

### Majors (address this slice)

#### M1: AC2 / mid-slice perturbation of `skills/reflect/SKILL.md` collides with pre-existing `test_ai_sdlc_version_forward_sync.py` — a full-suite false-FAIL window the design does not acknowledge
- **Claim under review**: mission-brief Mid-slice smoke gate ("perturb one non-EOL byte of `skills/reflect/SKILL.md` and re-run → expect FAIL"); design.md Error model ("the only failure mode introduced is a test assertion failure: `assert_md_forward_synced` raises AssertionError").
- **Issue**: `tests/methodology/test_ai_sdlc_version_forward_sync.py::test_wired_in_build_slice_step6_and_reflect_post_write` (lines 172–196) already reads in-repo `skills/reflect/SKILL.md` and asserts substrings `tools.ai_sdlc_version_forward_sync`, `AVFS-1`, `Step 5b-avfs`. The mid-slice smoke gate scopes its perturbation re-run to *only* `test_reflect_skill_drift.py` (safe), but AC5 / pre-finish runs the **full** `pytest tests/methodology`. If the perturbation byte lands inside an AVFS-1 anchor substring, OR any full-suite run happens while the perturbation is live, that pre-existing test ALSO FAILs — a confusing second failure unrelated to the drift guard. The Error model claim of a single failure mode is incomplete: a second, pre-existing test is collateral-coupled to the same perturbed file. slice-049's triage/adopt SKILL.md had no such pre-existing content-pin co-reader; this slice's target does.
- **Evidence**: `tests/methodology/test_ai_sdlc_version_forward_sync.py:172-196`; mission-brief Mid-slice smoke gate; design.md "Error model for this slice".
- **Proposed fix**: Add an explicit constraint to design.md Error model + mission-brief Mid-slice smoke gate: the AC2 perturbation MUST (a) target a byte OUTSIDE any AVFS-1 / `Step 5b-avfs` / `tools.ai_sdlc_version_forward_sync` anchor, and (b) be reverted/re-synced BEFORE any full-suite or `/validate-slice` run. Name `test_ai_sdlc_version_forward_sync.py::test_wired_in_build_slice_step6_and_reflect_post_write` as a co-reader of the perturbed file; record in build-log.md as a known interaction.
- **Builder draft**: ACCEPTED-FIXED at design.md "Error model" + mission-brief "Mid-slice smoke gate" (perturbation-window constraint + co-reader named).

#### M2: AC2 genuine-contrast proves the comparator works, NOT that the OSDG-1 extension is present (slice-037 M-add-1 tautological-green class)
- **Claim under review**: mission-brief AC2; design.md deliverable "closing the slice-050 M-add-1 N=1 latent exposure".
- **Issue**: `assert_md_forward_synced` only asserts in-repo == installed (modulo EOL). It passes whether or not `reflect/SKILL.md` contains the AVFS-1 `Step 5b-avfs` block — if both copies were stale-but-equal, the drift test is green. AC2 proves the *comparator* detects divergence; it does NOT pin that the deliverable (reflect now guarded, protecting the AVFS-1 arm) is meaningfully wired. This is the slice-037 meta-Critic M-add-1 lesson ("a content-bearing AC needs a CONTENT pin, not a byte-equality/forward-sync pin"). AC4's changelog entry-pin IS correctly content-bearing; the slice's *primary* deliverable (the drift guard) has no content pin. slice-049's identical structure shipped clean, so this is a methodological completeness gap, not a proven defect.
- **Evidence**: `tests/skill_drift_equality.py:49-80`; `tests/methodology/test_methodology_changelog.py:3219-3260`; slices/_index.md aggregated lesson (slice-037 meta-Critic M-add-1).
- **Proposed fix**: (a) accept explicitly with rationale in design.md naming the three surfaces that DO content-pin the OSDG-1-membership (the new test collected in the suite + the CLAUDE.md enumeration prose-pin + the v0.59.0 content-bearing entry-pin), explicitly the slice-049 accepted treatment; OR (b) add a string-presence assertion. Document which so the calibration loop records this class was consciously dispositioned.
- **Builder draft**: ACCEPTED-FIXED via option (a) at design.md "Error model" — conscious-disposition note naming the three OSDG-1-membership content surfaces + the slice-049 precedent. Option (b) rejected as over-engineering against the slice-049 precedent (a drift test gaining a bespoke content assertion fragments the verbatim-clone discipline; the three existing surfaces already content-pin membership).

#### M3: design.md does not address shippability catalog row pipe-escaping / segmentation (slice-044 row-construction discipline)
- **Claim under review**: design.md "What's new" / mission-brief must-not-defer (shippability row added).
- **Issue**: Design names *that* a row is added, not *how*. The catalog is a markdown table; a new row must take the next free row number (catalog tail = 50 = slice-050; verify `max(existing)+1`, not slice-number coincidence), contain zero unescaped `|` in any cell, and carry both human `Command` and `<interp>`-templated machine-cmd per slice-049 row #49. A malformed row breaks SCMD-1 parsing / the catalog runner. "Verbatim clone" does not cover catalog-row construction (slice-049's row is one physical row this slice must replicate exactly).
- **Evidence**: `architecture/shippability.md:59` (slice-049 row #49 shape); SCMD-1 audit "clean. 50 row(s)"; aggregated slice-022/044 row-construction precedent.
- **Proposed fix**: Add a one-line design.md constraint: row = `max(existing)+1` verified against catalog tail (not slice number), single physical table row, zero unescaped `|` in description/Command/machine-cmd cells, dual Command + `<interp>`-templated machine-cmd mirroring row #49, pytest target `test_reflect_skill_drift.py` + the v0.59.0 entry-pin selector; SCMD-1 must report `clean` with the incremented row count at pre-finish.
- **Builder draft**: ACCEPTED-FIXED at design.md "What's new" — shippability-row construction constraint added (row = max(existing)+1 verified vs catalog tail; single physical row; pipe-escaped; dual columns mirroring #49; SCMD-1 clean at pre-finish).

### Minors (log; address if cheap)

#### m1: ADR-053 "~6-surface inventory fan-out" enumeration is approximate and not cross-checked against the canonical fan-out surfaces
- **Claim under review**: ADR-053 Consequences parenthetical.
- **Issue**: The ADR mixes the version-bump fan-out with the content fan-out loosely; harmless but slightly imprecise for a calibration artifact. The "no `tools/*.py` ⇒ INSTALL.md count / `_CANONICAL_TOOLS` / `_ROOT_ONLY_TOOLS` N/A" reasoning is itself sound and verified.
- **Evidence**: ADR-053 Consequences; slices/_index.md slice-050 aggregated lesson.
- **Proposed fix**: Tighten the parenthetical to separate "PMI-1 version legs" / "content legs" / "N/A (no tool added)".
- **Builder draft**: ACCEPTED-FIXED at ADR-053 Consequences (parenthetical split into version-legs / content-legs / N/A groups). Pre-ship same-slice artifact edited in the /critique fix round (append-only applies to shipped ADRs; this is the slice's own un-shipped ADR).

## Dimensions checked

- [x] Unfounded assumptions — M2 (AC2 proves comparator, asserted to prove deliverable); changelog entry-pin claim verified backed.
- [x] Missing edge cases — M1 (concurrent co-reader of the perturbed file during a full-suite run). EOL/CRLF handled by reused comparator + `.gitattributes:8 skills/**/SKILL.md text eol=lf` (already covers `skills/reflect/SKILL.md` — no new gitattributes entry needed).
- [x] Over-engineering — none (deliberate verbatim reuse; ADR Option 2 correctly rejected; no speculative generality).
- [x] Under-engineering — M2 + M3. AC→design traceability otherwise complete.
- [x] Contract gaps — none (no wire contract; decoupling-audit `clean`, the new `Path.home()`-reading test classifies `clean` same as slice-049 members).
- [x] Security — none (no runtime auth/input/secret surface).
- [x] Drift from vault — none (ADR-053 `extends: ADR-051`, `supersedes: null`, next free number; no pre-existing test pins reflect's OLD state; `test_root_claude_md_cad1_eol_agnostic.py` section-scoped pin preserved by adding `reflect` to the bullet).
- [x] Web-known issues — not applicable (self-hosting methodology slice; no external technology/library/API/web-platform surface).
- [x] Cross-cutting conformance — M1 (collateral co-reader), M3 (shippability row-construction RPCD-1/SCPD-1). MEPD-1 RULE-ID obligation discharged via branch (a) verified against the actual `test_v_0_57_0` enforcing assertion shape.

## Triage

**Triaged by**: user
**Date**: 2026-05-19
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major   | ACCEPTED-FIXED | design.md "Error model §M1" + mission-brief "Mid-slice smoke gate": perturbation byte constrained outside AVFS-1 anchors, window isolated to single-test re-run, revert before any full-suite/`/validate-slice`, co-reader `test_ai_sdlc_version_forward_sync.py::test_wired_in_build_slice_step6_and_reflect_post_write` named, build-log records the coupling. Meta-Critic VALID/Major. |
| M2 | Major   | ACCEPTED-FIXED | design.md "Error model §M2": option (a) conscious disposition — OSDG-1-membership content pinned by 3 surfaces (new test collected+executed by suite + shippability runner row; CLAUDE.md "Mini-CAD / OSDG-1" enumeration prose-pin; v0.59.0 content-bearing entry-pin); slice-049 precedent. Option (b) rejected as fragmenting the verbatim-clone discipline. Meta-Critic explicitly held Major (not downgraded). |
| M3 | Major   | ACCEPTED-FIXED | design.md "What's new" row-construction constraint: row # = max(existing)+1 verified vs catalog tail (not slice number), single physical row, `\|`-escaped cells, dual Command + `<interp>` machine-cmd columns mirroring shippability.md:59 (row #49), SCMD-1 `clean` at pre-finish. Meta-Critic VALID/Major. |
| m1 | Minor   | ACCEPTED-FIXED | ADR-053 Consequences parenthetical split into PMI-1-version-legs (4) / content-legs (3) / N/A-no-tool-added (verified) groups. Meta-Critic VALID/Minor. |
