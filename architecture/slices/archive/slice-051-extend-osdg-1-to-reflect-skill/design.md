# Design: Slice 051 extend-osdg-1-to-reflect-skill

**Date**: 2026-05-19
**Mode**: Standard

## What's new

- `tests/methodology/test_reflect_skill_drift.py` — a new EOL-agnostic per-file drift assertion: in-repo `skills/reflect/SKILL.md` MUST be content-equal modulo line endings to installed `~/.claude/skills/reflect/SKILL.md`. A structural twin of `tests/methodology/test_triage_skill_drift.py` / `test_adopt_skill_drift.py` (slice-049), reusing `tests/skill_drift_equality.py::assert_md_forward_synced` **verbatim** (zero new comparison logic).
- `architecture/decisions/ADR-053-extend-osdg-1-to-reflect-skill.md` — records the member-addition + its methodology-surface-behavior-change classification (the 4-part-bump path), extending the ADR-051 OSDG-1 lineage.
- A `methodology-changelog.md` `## v0.59.0` entry — an **OSDG-1 member-addition** (NOT a new RULE-ID; OSDG-1 already exists — its guarded set is extended to include the in-loop `reflect` skill).
- A `test_methodology_changelog.py` entry-pin `test_v_0_59_0_osdg_1_reflect_member_entry_present_in_repo` — content-bearing, in-repo-only body (slice-041 M3 discipline), mirroring the `test_v_0_57_0_osdg_1_entry_present_in_repo` shape.
- A new shippability catalog critical-path row for `test_reflect_skill_drift.py` (per RPCD-1 / SCPD-1 — slice-040 precedent: an uncatalogued mini-CAD pin's breakage is invisible to the catalog runner). **Row-construction constraint (M3 critique fix, slice-044/022 discipline)**: the row number is `max(existing row #)+1` **verified against the catalog tail** (currently 50 = slice-050 — NOT the slice number, which only coincidentally also reads 51 here; re-derive at build time, do not transcribe). The row is a **single physical markdown table row** with **zero unescaped `|`** in any cell (`\|`-escape any literal pipe — a raw `|` shifts the SCMD-1 6-column segmentation; slice-044/SCMD-1 mis-segment class). It carries **both** the human `Command` column and the `<interp>`-templated machine-cmd column, mirroring the slice-049 row #49 (`architecture/shippability.md:59`) shape exactly; pytest target = `tests/methodology/test_reflect_skill_drift.py` plus the v0.59.0 entry-pin selector. `$PY -m tools.shippability_decoupling_audit architecture/shippability.md` MUST report `clean` with the incremented row count at pre-finish.

## What's reused

- `tests/skill_drift_equality.py::assert_md_forward_synced` — the shared EOL-agnostic forward-sync comparator (slice-033 EOL-DRIFT-1 / ADR-033). Reused by object reference; no clone, no new comparison logic.
- `tests/methodology/conftest.py::REPO_ROOT` — repo-root anchor.
- [[decisions/ADR-051]] — OSDG-1 minted; this slice extends OSDG-1's guarded set (does not supersede ADR-051).
- [[decisions/ADR-033]] — EOL-DRIFT-1: CRLF↔LF is not drift; the comparator already honors this.
- [[slice-049-add-triage-adopt-skill-drift-guards]] — the proven clean member-addition pattern (test shape + changelog/PMI-1/entry-pin/ADR fan-out) cloned here.
- [[slice-050-add-ai-sdlc-version-forward-sync-gate]] — added the `Step 5b-avfs` block to `skills/reflect/SKILL.md` that made this surface load-bearing; its reflection Discovered nomination (M-add-1) is the source of this slice.
- CLAUDE.md "Self-hosting discipline" → "Mini-CAD / OSDG-1" bullet — the guarded-skills enumeration line (modified, not created).

## Components touched

### `tests/methodology/test_reflect_skill_drift.py` (new)
- **Responsibility**: deterministically FAIL the methodology suite (and HALT PCA-1) if in-repo `skills/reflect/SKILL.md` and the installed copy genuinely (non-EOL) diverge — closing the slice-050 M-add-1 N=1 latent exposure where the AVFS-1 `Step 5b-avfs` arm in `reflect/SKILL.md` could silently skip on a stale install.
- **Lives at**: `tests/methodology/test_reflect_skill_drift.py` (created by this slice).
- **Key interactions**: imports `assert_md_forward_synced` from `tests/skill_drift_equality.py` and `REPO_ROOT` from `tests/methodology/conftest.py`; reads in-repo `skills/reflect/SKILL.md` + `~/.claude/skills/reflect/SKILL.md`.

### CLAUDE.md "Mini-CAD / OSDG-1" bullet (modified)
- **Responsibility**: the canonical human-readable enumeration of the guarded-skill set; must list `reflect` + cite the new test so the self-hosting contract stays truthful (code-is-truth: the test is the executable contract, the bullet is its index).
- **Lives at**: `CLAUDE.md` (project instructions), "Self-hosting discipline" section.
- **Key interactions**: none executable — documentation surface; RSAD-1 surface-consistency applies (the rule must not ship beside its own counter-example).

### `methodology-changelog.md` + `tests/methodology/test_methodology_changelog.py` (modified)
- **Responsibility**: record the methodology-surface behavior change (`## v0.59.0` entry) and pin it (content-bearing entry-pin) so the OSDG-1-member-addition rationale + ADR-053 lineage are recoverable from the changelog.
- **Lives at**: `methodology-changelog.md`; `tests/methodology/test_methodology_changelog.py`.
- **Key interactions**: META-1 `^## v`-split parser; MCFS-1 whole-file gate forward-syncs the installed changelog leg; the entry-pin reads in-repo only (slice-041 M3 → `classify_fn` clean).

## Contracts added or changed

None. No endpoints, events, or runtime API surfaces. The "contract" here is the OSDG-1 in-repo↔installed content-equality invariant, extended to one additional file; it is expressed as a pytest assertion, not a wire contract.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1**. The one new module is a test; its "consumer" is the methodology suite / pytest collection itself (the established convention for `tests/methodology/test_*_skill_drift.py` — slice-049 set this exemption precedent for `test_triage_skill_drift.py` / `test_adopt_skill_drift.py`).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_reflect_skill_drift.py` | — | — | `the module IS a test collected + executed by the methodology pytest suite and the shippability Step-5.5 runner row added by this slice — rationale: a drift-guard test has no non-test consumer by construction; identical exemption shape to slice-049's test_triage_skill_drift.py / test_adopt_skill_drift.py OSDG-1 members` |

## Decisions made (ADRs)

- [[ADR-053]] — Extend the OSDG-1 guarded set to include the in-loop `reflect` skill; classify the member-addition as a methodology-surface behavior change taking the 4-part PMI-1 bump + changelog + entry-pin path (no new RULE-ID minted — OSDG-1 already exists). — reversibility: **cheap**

## Authorization model for this slice

N/A — no runtime authorization surface. The slice touches in-house methodology surfaces only (`skills/*` indirectly via the guarded reflect copy, `tests/methodology/`, `CLAUDE.md`, `methodology-changelog.md`, `plugin.yaml`, `VERSION`).

## Error model for this slice

No new runtime error codes. The only failure mode introduced by the *new test itself* is a **test assertion failure**: `assert_md_forward_synced` raises `AssertionError` containing the substring `DRIFT` when in-repo and installed `reflect/SKILL.md` genuinely (non-EOL) diverge. CRLF↔LF differences do NOT raise (EOL-DRIFT-1 / ADR-033, inherited from the reused comparator). The genuine-contrast proof (AC2) deliberately triggers this assertion on a perturbed in-repo copy, then confirms PASS once re-synced.

### M1 — collateral co-reader of the perturbed file (critique fix)

`skills/reflect/SKILL.md` is **already read by a pre-existing test**: `tests/methodology/test_ai_sdlc_version_forward_sync.py::test_wired_in_build_slice_step6_and_reflect_post_write` (lines 172–196) asserts the substrings `tools.ai_sdlc_version_forward_sync`, `AVFS-1`, `Step 5b-avfs` are present in in-repo `skills/reflect/SKILL.md`. The AC2 / mid-slice perturbation is therefore NOT a single-failure-mode operation — it is collateral-coupled to that pre-existing test. **Constraint** (binds AC2 + the mid-slice smoke gate):
1. The perturbation byte MUST land OUTSIDE any AVFS-1 anchor — not inside `AVFS-1`, `Step 5b-avfs`, or `tools.ai_sdlc_version_forward_sync` (pick a harmless prose byte, e.g. a word in a sentence with no AVFS-1 token).
2. The perturbation window is restricted to the **isolated single-test re-run only** (`pytest tests/methodology/test_reflect_skill_drift.py -q`). The file MUST be reverted/re-synced BEFORE any full-suite `pytest tests/methodology` run or any `/validate-slice` run — otherwise `test_wired_in_build_slice_step6_and_reflect_post_write` co-FAILs (a confusing, unrelated second failure).
3. build-log.md MUST record this co-reader interaction as a known/expected coupling.

### M2 — drift-test is not itself a content pin; OSDG-1-membership content is pinned on three other surfaces (critique fix, conscious disposition)

`assert_md_forward_synced` asserts only in-repo == installed (modulo EOL); it is green even if both copies were stale-but-equal (slice-037 meta-Critic M-add-1 tautological-green class). This is **consciously accepted**, not missed: the OSDG-1-membership *content* (that `reflect` is now a guarded member protecting the AVFS-1 `/reflect` arm) is content-pinned by **three** surfaces this slice ships — (i) the new `test_reflect_skill_drift.py` being **collected and executed** by the methodology pytest suite + the shippability Step-5.5 runner row (its existence-in-the-suite IS the wired contract); (ii) the **CLAUDE.md "Mini-CAD / OSDG-1" enumeration prose-pin** listing `reflect` + `test_reflect_skill_drift.py`; (iii) the **v0.59.0 content-bearing entry-pin** (asserts `OSDG-1`, `ADR-053`, `extends`, `reflect`, `supersedes nothing` in the changelog body — mirrors the `test_v_0_57_0_osdg_1_entry_present_in_repo` shape). This is exactly the slice-049 accepted treatment (its `test_triage_skill_drift.py` / `test_adopt_skill_drift.py` shipped clean under the identical structure). A bespoke content assertion inside the drift test (Critic option (b)) is rejected: it would fragment the verbatim-clone discipline (`assert_md_forward_synced` reused by reference, zero new logic) for content the three surfaces above already pin.

## PMI-1 4-part atomic bump (must not partial-leg)

This member-addition takes the bump path per the slice-049 ADR-051 / Critic-B2 resolution (a drift-guard family member-addition with no other bump reason **is** a methodology-surface behavior change — the changelog's own Inclusion heuristic: acceptable-yesterday / refused-today ⇒ entry). All four legs applied in one atomic step (the exact slice-035/048/049 leg-drift class this lineage exists to prevent; AVFS-1 from slice-050 now also deterministically guards the installed `ai-sdlc-VERSION` leg):

1. in-repo `VERSION` → `0.59.0`
2. installed `~/.claude/ai-sdlc-VERSION` → `0.59.0`
3. `plugin.yaml.version` → `0.59.0`
4. forward-sync `~/.claude/methodology-changelog.md` (MCFS-1-guarded leg)
