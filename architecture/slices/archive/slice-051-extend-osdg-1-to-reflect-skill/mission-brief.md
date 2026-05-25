# Slice 051: extend-osdg-1-to-reflect-skill

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: N=1 latent drift exposure flagged by the slice-050 meta-Critic (M-add-1) — `reflect/SKILL.md` carries the AVFS-1 `Step 5b-avfs` block but is NOT in the OSDG-1 / mini-CAD in-repo↔installed guarded set, so its installed copy can silently drift and partially defeat the AVFS-1 gate's `/reflect` arm. Not a registered risk ID (consistent with the slice-048→049 N=1 handling that motivated OSDG-1).
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`reflect/SKILL.md` is a load-bearing pipeline surface (it owns the AVFS-1 `Step 5b-avfs` forward-sync block added in slice-050) yet has no deterministic in-repo↔installed drift guard, unlike `slice` / `build_slice` / `commit_slice` / `query_design` / `critique` / `triage` / `adopt` + `agents/critique.md` (CAD-1). This slice extends the OSDG-1 guarded set to include `reflect/SKILL.md`, repeating the clean, well-scoped member-addition pattern proven one slice ago by slice-049. Per the slice-049 ADR-051 / Critic-B2 resolution, a drift-guard family member-addition with no other bump reason **is** a methodology-surface behavior change and takes the version-bump + ADR + entry-pin path.

## Acceptance criteria

1. A new EOL-agnostic drift test `tests/methodology/test_reflect_skill_drift.py` asserts in-repo `skills/reflect/SKILL.md` is content-equal modulo line endings to the installed `~/.claude/skills/reflect/SKILL.md` (clone of the slice-049 `test_triage_skill_drift.py` / `test_adopt_skill_drift.py` shape, EOL-agnostic per ADR-033 / EOL-DRIFT-1), and PASSES on the current synced tree.
2. The new test demonstrably FAILs under a per-member genuine-contrast perturbation of `reflect/SKILL.md` (real FAIL→PASS, not tautological green), then PASSES once restored/synced.
3. CLAUDE.md "Self-hosting discipline" OSDG-1 / Mini-CAD line lists `reflect` in the guarded-skills set with the new test cited.
4. The methodology-surface behavior change is recorded: a new ADR (extending the ADR-051 OSDG-1 lineage) + a `methodology-changelog.md` version-bump entry + the corresponding `test_methodology_changelog.py` entry-pin, with the 4-part PMI-1 bump applied atomically (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`).
5. Full methodology suite + all slice-finish audits (PMI-1, INST-1, CAD-1, RR-1, SUP-1, drift-check) pass green at pre-finish.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | reflect drift test exists + passes | `$PY -m pytest tests/methodology/test_reflect_skill_drift.py -q` → green on synced tree |
| 2 | Genuine FAIL→PASS contrast | Perturb a byte in `skills/reflect/SKILL.md` (not EOL), run the test → FAIL with content-divergence message; restore/sync → PASS. Recorded in build-log.md. |
| 3 | CLAUDE.md OSDG-1 line updated | `grep` CLAUDE.md self-hosting section: `reflect` present in the guarded set + `test_reflect_skill_drift.py` cited |
| 4 | Methodology-surface change recorded | New `decisions/ADR-0NN` exists with `extends: ADR-051`; `methodology-changelog.md` has the new `## vN` entry; `test_methodology_changelog.py` entry-pin asserts it; `$PY -m tools.plugin_manifest_audit` clean (version parity); `~/.claude/ai-sdlc-VERSION` == `VERSION` |
| 5 | Suite + audits green | `/validate-slice` (VAL-1 + WS-1 + ETC-1 + shippability) + full `pytest tests/methodology` green; `$PY -m tools.critique_agent_drift_audit --repo-root .` clean |

## Must-not-defer

- [ ] EOL-agnostic comparison (CRLF↔LF is NOT drift per ADR-033 / EOL-DRIFT-1) — clone the existing normalization helper, do not raw-byte compare
- [ ] Per-member genuine-contrast proof (perturb `reflect/SKILL.md` itself — no proxy via another guarded skill)
- [ ] Forward-sync `skills/reflect/SKILL.md` → `~/.claude/skills/reflect/SKILL.md` byte/EOL-verified before pre-finish so the new test is green for the right reason
- [ ] 4-part PMI-1 bump applied atomically (no partial leg — the exact slice-035/048/049 leg-drift class this lineage exists to prevent)
- [ ] Entry-pin added to `test_methodology_changelog.py` for the new changelog version (not just the changelog text)
- [ ] Shippability catalog: add the new `test_reflect_skill_drift.py` pin as a critical-path row (per RPCD-1 / SCPD-1 — an uncatalogued mini-CAD pin's breakage is invisible to the catalog runner; slice-040 precedent)

## Out of scope

- Generalized multi-file INST-2 mini-CAD audit — slice-049 standing decided-not-discovered; this is a per-file member-addition, not a generalization
- Adding any OTHER skill to the guarded set (e.g. `discover`, `design-slice`) — out of scope; one member per slice keeps the contrast per-member
- The slice-050 INSTALL.md tool-count build-check (separate candidate #2) — different slice
- `add-soad1-lint-audit` deferred backlog item — unrelated

## Dependencies

- Prior slices: [[slice-049-add-triage-adopt-skill-drift-guards]] — OSDG-1 minted (ADR-051); the member-addition pattern + EOL-agnostic drift-test shape this slice clones. [[slice-050-add-ai-sdlc-version-forward-sync-gate]] — added the `Step 5b-avfs` block to `reflect/SKILL.md` that makes this surface load-bearing; its reflection's Discovered nomination is the source of this slice.
- Vault refs: [[decisions/ADR-051]] (OSDG-1 lineage to extend), [[decisions/ADR-033]] (EOL-DRIFT-1 — CRLF↔LF is not drift), CLAUDE.md "Self-hosting discipline"
- Risk register: no open risk ID (N=1 latent exposure, consistent with slice-048→049 handling)

## Mid-slice smoke gate

At ~50% of build (test written + reflect SKILL.md synced, before the methodology-changelog/PMI-1 bump), run:
```
$PY -m pytest tests/methodology/test_reflect_skill_drift.py -q
```
Expected: PASS on the synced tree. Then perturb **one non-EOL byte of `skills/reflect/SKILL.md` that is OUTSIDE any AVFS-1 anchor** (NOT inside `AVFS-1`, `Step 5b-avfs`, or `tools.ai_sdlc_version_forward_sync` — choose a harmless prose byte) and re-run the **isolated single test only** → expect FAIL with a content-divergence message (genuine-contrast proof). **Restore/sync the file BEFORE any full-suite `pytest tests/methodology` or `/validate-slice` run** — `tests/methodology/test_ai_sdlc_version_forward_sync.py::test_wired_in_build_slice_step6_and_reflect_post_write` (M1: a pre-existing co-reader of `skills/reflect/SKILL.md`) co-FAILs if the perturbation window leaks into a full-suite run. Record the co-reader interaction in build-log.md. If the test passes under perturbation or fails on the synced tree: STOP, diagnose (likely a wrong helper import or raw-byte compare), don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] PMI-1 / INST-1 / CAD-1 / RR-1 / SUP-1 audits green; full `pytest tests/methodology` green
