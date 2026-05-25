# Design: Slice 050 add-ai-sdlc-version-forward-sync-gate

**Date**: 2026-05-19
**Mode**: Standard

## What's new

- `tools/ai_sdlc_version_forward_sync.py` — the **AVFS-1** gate. A near-verbatim structural clone of `tools/methodology_changelog_forward_sync.py` (MCFS-1, slice-041), retargeted from `methodology-changelog.md` → `VERSION` and `~/.claude/methodology-changelog.md` → `~/.claude/ai-sdlc-VERSION`. Same `CheckResult` dataclass, same four-way status (`synced`/`drift`/`warn`/`usage`), same exit-code contract, **the verbatim `_normalized_bytes` comparator — CRLF→LF ONLY, NOT trailing-whitespace/newline tolerant** (B3), same attributed HALT message shape.
- **Two test artifacts, exactly the MCFS-1 shape (M2 — no third file):**
  - `tests/methodology/test_ai_sdlc_version_forward_sync.py` — the AVFS-1 regression suite (MCFS-1 suite analogue). Holds synced / CRLF-tolerant / CSP-1-parity / usage / installed-absent-WARN / divergent-HALT / empty-present-HALT / whitespace-only-present-HALT, the relocation/non-catalog proof (`test_avfs1_module_is_non_catalog_relocation_proof`, the AVFS-1 analogue of `test_mcfs1_module_is_non_catalog_relocation_proof`), AND the AVFS-1-specific 2-point SKILL.md-wiring assertion (`test_wired_in_build_slice_step6_and_reflect_post_write` — reads in-repo SKILL.md only → classifies `clean`). The suite reads the installed copy in its synced/divergent cases → **NOT shippability-catalog-cited** (see "What's reused" for the corrected, recomputed rationale). NB: the SKILL.md-wiring assertion is an **AVFS-1 addition**, not an MCFS-1 precedent (MCFS-1 discharges WIRE-1 by "suite existing+passing" and has no wiring-assertion test).
  - `tests/methodology/test_methodology_changelog.py` — `test_v_0_58_0_avfs_1_entry_present_in_repo` (**content-bearing** in-repo-only entry-pin asserting `AVFS-1`, `ADR-052`, `supersedes nothing`, the canonical "NOT a slice regression" attribution phrase, and the "standalone clone, not folded into MCFS-1" decision — STP-1/MCFS-1 entry-pin depth, NOT a thin presence check, B1) + `test_v_0_58_0_avfs_1_shippability_consumer_propagation` (RPCD-1/SCPD-1 propagation pin for catalog row #50, asserts row presence + the `test_ai_sdlc_version_forward_sync` module is absent from every Machine-cmd cell).
- `methodology-changelog.md` — new `## v0.58.0 — 2026-05-19` entry minting **AVFS-1** (new minted NON-`-D` audit-gate; refines nothing; supersedes nothing — the slice-044/STP-1 entry is the format template).
- `architecture/shippability.md` — new catalog row #50 (verified next-free: max existing row = #49 / slice-049) citing ONLY the two in-repo-only `test_methodology_changelog.py` pins (MCFS-1 row #41 is the exact precedent shape).
- `architecture/decisions/ADR-052-add-ai-sdlc-version-forward-sync-gate.md` — locks the standalone-analogue (vs fold-into-MCFS-1) decision + the ADR-051 methodology-surface-behavior-change → 4-part-bump path.

## What's reused

- `tools/methodology_changelog_forward_sync.py` — the verbatim structural template (module shape, exit-code semantics, `_ATTRIB` message, `_normalized_bytes` comparator — **CRLF→LF only**). AVFS-1 is MCFS-1 with two path constants swapped.
- `tools/_stdout.py` — `reconfigure_stdout_utf8()` called in `main()` (slice-023 UTF8-STDOUT-1 obligation; MCFS-1 line 186 precedent).
- `tests/skill_drift_equality.py::_normalized_sha256` — the canonical EOL-DRIFT-1 comparator; AVFS-1's local `_normalized_bytes` is CSP-1 behaviour-parity-pinned to it (MCFS-1 `test_csp1_normalization_parity_with_skill_drift_equality` precedent). This pin is the reason the comparator MUST stay CRLF→LF-only (B3): any trailing-whitespace tolerance would break the parity to `_normalized_sha256` (which is also CRLF→LF-only).
- `tools.shippability_decoupling_audit` — the closed-world cited-fn resolver the relocation-proof test runs against the real catalog. **Recomputed non-catalog rationale (M3, corrected):** `_ESSENTIAL_SHAPES = ((".claude", "methodology-changelog.md"),)` (`shippability_decoupling_audit.py:95-97`) and `classify_fn` explicitly classifies *other* `~/.claude/...` reads — including `~/.claude/ai-sdlc-VERSION` — as `clean`, NOT `essential` (`:421-432`, prose `:27-34`). Therefore the AVFS-1 regression suite would **NOT** trip `essential-unregistered` and the MCFS-1 m-add-2 mechanism does **not** transfer. The suite is non-catalog for the *correct* reason: it reads the untracked, **environment-mutable** installed `~/.claude/ai-sdlc-VERSION`, and a shippability `Machine-cmd` must not depend on environment-mutable/untracked state (slice-029/030A discipline — aggregated lesson "rows must not depend on gitignored/environment-mutable state"). The relocation-proof test asserts module-absence from every Machine-cmd cell on that environment-state ground.
- [[decisions/ADR-051]] — establishes that a drift-guard / methodology-surface audit-gate addition with no other bump reason IS a methodology-surface behavior change → minted-RULE-ID + `## vN.N.0` + 4-part PMI-1 bump path (not the rode-an-existing-bump non-path).
- [[decisions/ADR-042]] + [[decisions/ADR-043]] — MCFS-1 lineage (the forward-sync-via-deterministic-downstream-gate pattern, slice-030A/ADR-029 rationale).
- [[decisions/ADR-033]] — EOL-DRIFT-1: CRLF↔LF is not drift; genuine content divergence still HALTs.
- `tests/methodology/test_utf8_stdout_regression.py::_ROOT_ONLY_TOOLS` — AVFS-1 is `--check/--json/--root` with no slice arg → joins this list (MCFS-1 is its immediate list-neighbor at line 100).

## Components touched

### `tools/ai_sdlc_version_forward_sync.py` (created by this slice)
- **Responsibility**: deterministically assert in-repo `VERSION` is content-equal modulo line endings (CRLF↔LF) only to installed `~/.claude/ai-sdlc-VERSION`, so the 4th leg of the PMI-1 atomic bump (currently guarded only by per-slice-manual M2 pre-sync-diff) cannot silently drift (N=2: slice-035 DEVIATION-2, slice-048→049).
- **Lives at**: `tools/ai_sdlc_version_forward_sync.py`
- **Key interactions**: reads `<root>/VERSION` + `Path.home()/".claude"/"ai-sdlc-VERSION"`; emits via `tools._stdout`; invoked by `skills/build-slice/SKILL.md` Step 6 + `skills/reflect/SKILL.md` post-write step.
- **Public surface**: `check(root: Path, installed: Path | None = None) -> CheckResult`, `main(argv=None) -> int`, `CheckResult` dataclass, `_normalized_bytes(path) -> bytes` (CSP-1-pinned). Mirrors MCFS-1's surface 1:1.

### `skills/build-slice/SKILL.md` (modified)
- **Responsibility**: add AVFS-1 to the Step 6 pre-finish gate checklist + a dedicated audit subsection, structurally parallel to the existing "Methodology-changelog forward-sync audit (MCFS-1)" block (SKILL.md L152 + L241). Ungated — runs every slice, not gated on rule promotion.
- **Self-hosting note (Mini-CAD)**: `build-slice/SKILL.md` is OSDG-1/mini-CAD-guarded; the in-repo edit must be forward-synced to the installed copy in the same fix block (the `/build-slice` skill-drift test will FAIL otherwise).

### `skills/reflect/SKILL.md` (modified)
- **Responsibility**: add a dedicated post-write AVFS-1 step parallel to the existing `### Step 5b-fs: Methodology-changelog forward-sync gate (MCFS-1)` block (SKILL.md L221). Explicitly a NEW dedicated step — **NOT** folded into the rule-promotion-gated Step 5b (else the gate silently never runs on a version-bumping-but-no-rule-promoted slice — the R-7/slice-022 class MCFS-1 explicitly avoided).
- **Self-hosting note (Mini-CAD) — M-add-1, corrected**: `reflect/SKILL.md` is NOT in the OSDG-1/mini-CAD guarded set, so a stale installed `~/.claude/skills/reflect/SKILL.md` whose AVFS-1 post-write step was added in-repo but never forward-synced would make `/reflect` silently skip the AVFS-1 step at runtime — the **exact R-7/slice-022 "gate silently never runs" class** this slice invokes elsewhere. AVFS-1 cannot self-detect this (it gates the `ai-sdlc-VERSION` value leg, not SKILL.md prose). Manual forward-sync + the post-build AVFS-1 self-run is therefore **NOT sufficient** (it does not close the unguarded-reflect-leg hole). Scoped mitigation this slice (not a fold-into-OSDG-1, which is larger blast radius → out of scope): (1) a must-not-defer requiring the installed `reflect/SKILL.md` AVFS-1 block be hand-verified against the in-repo copy at this slice's own `/reflect` post-write step; (2) the slice records an explicit Discovered-gap entry at `/reflect` nominating `reflect/SKILL.md` for a future OSDG-1-extension slice (the honest slice-049→050 nomination pattern applied to the analogous leg this slice itself opens — it does not silently close leg N while opening leg N+1).

## Contracts added or changed

No HTTP/event contracts. The "contract" is the CLI + exit-code surface of the new audit tool, defined entirely in `tools/ai_sdlc_version_forward_sync.py` and identical to MCFS-1's:

- `python -m tools.ai_sdlc_version_forward_sync [--check] [--json] [--root <path>]`
- Exit `0`: synced (content-equal modulo line endings, CRLF→LF only) OR installed-absent WARN (distinct stdout).
- Exit `1`: HALT — installed present but content-divergent after CRLF→LF (incl. empty-present AND whitespace-only-present).
- Exit `2`: usage — in-repo `VERSION` missing/unreadable, or repo root unresolvable.

## Data model deltas

None. `VERSION` and `~/.claude/ai-sdlc-VERSION` are pre-existing single-line semver files; this slice adds a gate over them, no schema change.

## Wiring matrix

Per **WIRE-1**. Two test artifacts only (the exact MCFS-1 shape — M2; the invented third `_wiring.py` is dropped). The gate module's WIRE-1 consumer-test obligation is discharged by its regression suite existing + passing; that suite reads the **untracked, environment-mutable** installed copy and is therefore intentionally NOT cataloged (slice-029/030A environment-state discipline — NOT m-add-2/essential-unregistered, which provably does not apply to the `ai-sdlc-VERSION` path; M3) — only the two in-repo-only `test_methodology_changelog.py` pins carry shippability row #50.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/ai_sdlc_version_forward_sync.py` | `skills/build-slice/SKILL.md` Step 6 pre-finish + `skills/reflect/SKILL.md` post-write step | `tests/methodology/test_ai_sdlc_version_forward_sync.py` (regression suite — exercises `check()`/`main()`, holds the relocation-proof + the AVFS-1 SKILL.md-wiring assertion) | — |
| `tests/methodology/test_ai_sdlc_version_forward_sync.py` | — | — | `installed-reading regression suite, NOT shippability-cited — rationale: it reads the untracked environment-mutable ~/.claude/ai-sdlc-VERSION; a Machine-cmd must not depend on environment-mutable/untracked state (slice-029/030A discipline). essential-unregistered does NOT apply (_ESSENTIAL_SHAPES is changelog-path-only, shippability_decoupling_audit.py:95-97). WIRE-1 discharged by the suite existing + passing; the two in-repo-only test_methodology_changelog.py pins carry row #50.` |

## Decisions made (ADRs)
- [[ADR-052]] — ship the `ai-sdlc-VERSION` forward-sync gate as a standalone MCFS-1 analogue (not folded into MCFS-1's whole-file gate), minting AVFS-1 with the ADR-051-mandated `## v0.58.0` + 4-part PMI-1 bump path — reversibility: **cheap**.

## Authorization model for this slice

N/A — a local audit tool with no auth surface. It reads two local files (in-repo `VERSION`, installed `~/.claude/ai-sdlc-VERSION`) and emits a verdict. No network, no writes, no privileged action.

## Error model for this slice

Identical to MCFS-1 (parity is a hard must-not-defer):

- **exit 2 / `usage`**: in-repo `VERSION` missing/unreadable, or repo root unresolvable — the repo is malformed, NOT vault drift. Fail-closed, never silent exit 0.
- **exit 0 / `warn`**: installed `~/.claude/ai-sdlc-VERSION` **absent** — untracked/environment-dependent; a machine that hasn't installed the plugin must not HALT `/build-slice` (slice-030A meta-M3 parity).
- **exit 1 / `drift`**: installed **present but content-divergent after CRLF→LF** (incl. empty-present — empty ≠ absent, so the R-4-class is not silently reopened) — HALT with the attributed message stating this is NOT a slice regression and to re-run the PMI-1 4-part forward-sync.
- **exit 0 / `synced`**: content-equal modulo line endings — pass.
