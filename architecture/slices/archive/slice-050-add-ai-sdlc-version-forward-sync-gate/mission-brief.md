# Slice 050: add-ai-sdlc-version-forward-sync-gate

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: recurring N=2 silent-drift class on the PMI-1 4-part bump's installed `~/.claude/ai-sdlc-VERSION` leg (slice-035 DEVIATION-2; slice-048 leg-drift surfaced at slice-049). Not a registered risk ID (impact low, no audit consumes the installed file) — but an explicitly twice-flagged "strong next-slice candidate" in slice-049's reflection + `_index.md` aggregated lessons.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The atomic PMI-1 version bump has four legs: in-repo `VERSION`, `~/.claude/ai-sdlc-VERSION`, `plugin.yaml.version`, and the forward-synced `~/.claude/methodology-changelog.md`. MCFS-1 (slice-041) deterministically guards only the changelog leg; PMI-1 audits `VERSION`==`plugin.yaml` but never the installed `ai-sdlc-VERSION` file, which has drifted silently twice (N=2). This slice ships an MCFS-1-analogue forward-sync gate for the `~/.claude/ai-sdlc-VERSION` leg — same semantics, same two enforcement points — converting a per-slice-manual control into a deterministic one. Per ADR-051 / the slice-049 resolution, a new drift-guard / methodology-surface audit gate with no other bump reason **is itself a methodology-surface behavior change**: it takes the minted-RULE-ID + `## vN.N.0` changelog entry + 4-part PMI-1 bump + entry-pin path (not the rode-an-existing-bump non-path).

## Acceptance criteria

1. New audit module `tools/ai_sdlc_version_forward_sync.py` exposes `check(root, installed=None) -> CheckResult` and a `main()`; when in-repo `VERSION` is content-equal modulo line endings (CRLF↔LF) only to installed `~/.claude/ai-sdlc-VERSION`, it reports synced (exit 0). The comparator is the verbatim MCFS-1 `_normalized_bytes` (CRLF→LF only — NOT trailing-whitespace/newline tolerant), CSP-1 behaviour-parity-pinned to `tests/skill_drift_equality.py::_normalized_sha256`.
2. Semantics are MCFS-1-parity: in-repo `VERSION` missing/unreadable → exit 2 (usage error); installed `ai-sdlc-VERSION` **absent** → WARN, exit 0 (optional-install, not a regression); installed **present but content-divergent after CRLF→LF** (incl. empty-present AND whitespace-only-present) → HALT, exit 1, with an attributed message stating this is NOT a slice regression and to re-run the PMI-1 4-part forward-sync.
3. The gate is wired at the same two enforcement points MCFS-1 uses: `/build-slice` Step 6 pre-finish (ungated — runs every slice, not gated on rule promotion) and a `/reflect` post-write step (explicitly NOT folded into the rule-promotion-gated Step 5b).
4. A new RULE-ID (proposed `AVFS-1`) is minted with a `methodology-changelog.md` `## v0.58.0` entry, the atomic 4-part PMI-1 bump (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`) all `0.57.0 → 0.58.0` in lockstep, a **content-bearing** `test_v_0_58_0_avfs_1_entry_present_in_repo` entry-pin asserting the AVFS-1-specific literals (`AVFS-1`, `ADR-052`, `supersedes nothing`, the canonical "NOT a slice regression" attribution phrase, and the "standalone clone, not folded into MCFS-1" decision — NOT a thin `"AVFS-1" in body` presence check; MCFS-1/STP-1 entry-pin depth is the precedent), a `test_v_0_58_0_avfs_1_shippability_consumer_propagation` pin, and shippability-catalog row #50 carrying ONLY those two in-repo-only `test_methodology_changelog.py` pins (the tool's own regression suite reads the untracked, environment-mutable installed copy and is therefore non-catalog per the slice-029/030A environment-state discipline — NOT essential-unregistered, which provably keys on the changelog path only: `tools/shippability_decoupling_audit.py:95-97`).
5. UTF-8 stdout self-application is discharged: the new tool calls `_stdout.reconfigure_stdout_utf8()` and is added to `tests/methodology/test_utf8_stdout_regression.py`'s argv-classified list (the slice-038 obligation for any new `tools/*.py` with `main()`).

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0). Every AC maps to ≥1 failing test written BEFORE implementation. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish` and refuses any non-PASSING row.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_ai_sdlc_version_forward_sync.py | test_synced_when_in_repo_equals_installed | PASSING |
| 1 | unit | tests/methodology/test_ai_sdlc_version_forward_sync.py | test_crlf_only_difference_is_not_a_fail | PASSING |
| 1 | unit | tests/methodology/test_ai_sdlc_version_forward_sync.py | test_csp1_normalization_parity_with_skill_drift_equality | PASSING |
| 2 | unit | tests/methodology/test_ai_sdlc_version_forward_sync.py | test_in_repo_missing_is_usage_exit2 | PASSING |
| 2 | unit | tests/methodology/test_ai_sdlc_version_forward_sync.py | test_installed_absent_is_warn_exit0 | PASSING |
| 2 | unit | tests/methodology/test_ai_sdlc_version_forward_sync.py | test_divergent_halts_exit1_with_attribution | PASSING |
| 2 | unit | tests/methodology/test_ai_sdlc_version_forward_sync.py | test_empty_present_installed_halts | PASSING |
| 2 | unit | tests/methodology/test_ai_sdlc_version_forward_sync.py | test_whitespace_only_present_installed_halts | PASSING |
| 3 | integration | tests/methodology/test_ai_sdlc_version_forward_sync.py | test_wired_in_build_slice_step6_and_reflect_post_write | PASSING |
| 4 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_58_0_avfs_1_entry_present_in_repo | PASSING |
| 4 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_58_0_avfs_1_shippability_consumer_propagation | PASSING |
| 4 | unit | tests/methodology/test_ai_sdlc_version_forward_sync.py | test_avfs1_module_is_non_catalog_relocation_proof | PASSING |
| 5 | unit | tests/methodology/test_utf8_stdout_regression.py | test_root_only_tool_survives_cp1252_with_u2192 | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Synced path | `$PY -m tools.ai_sdlc_version_forward_sync --json` against in-sync VERSION/installed → exit 0, status `synced` |
| 2 | Failure semantics | Drive `check()` with a tmp root: missing in-repo VERSION → exit 2; `installed=` pointing at a nonexistent path → WARN exit 0; `installed=` with a divergent string → exit 1 + attributed stderr/stdout text |
| 3 | Wiring | `grep` `skills/build-slice/SKILL.md` (Step 6 pre-finish) and `skills/reflect/SKILL.md` (dedicated post-write step, not Step 5b) for the new module invocation; wiring test green |
| 4 | RULE-ID + 4-part bump | `$PY -m tools.plugin_manifest_audit` clean (VERSION==plugin.yaml==0.58.0); `test_v_0_58_0_avfs_1_entry_present_in_repo` green; shippability runner row passes |
| 5 | UTF-8 stdout | `test_utf8_stdout_regression.py` parametrized list includes the new tool; suite green |

## Must-not-defer

- [ ] HALT message attribution: explicitly states "NOT a slice regression — re-run the PMI-1 4-part forward-sync" so a future Builder is not misled into treating drift as their own breakage (MCFS-1 `_ATTRIB` parity).
- [ ] Empty-present ≠ absent: an empty installed `ai-sdlc-VERSION` is divergent → HALT, not WARN (do not silently reopen the R-4-class hole — MCFS-1 semantics parity).
- [ ] Whitespace-only-present (`\n`, ` `, `\r\n`) is the same class as empty-present → HALT, not synced. Resolved by construction under the verbatim CRLF-only comparator below (no special branch); a trailing-whitespace-tolerant comparator would false-sync `0.57.0 \n` vs `0.57.0` and is therefore rejected.
- [ ] Comparator is the verbatim MCFS-1 `_normalized_bytes` — CRLF→LF ONLY (`read_bytes().replace(b"\r\n", b"\n")`), NOT trailing-whitespace/newline tolerant and NOT value-tolerant — so `0.57.0` vs `0.58.0` HALTs AND `0.57.0\n` vs `0.57.0` HALTs. CSP-1 behaviour-parity-pinned to `tests/skill_drift_equality.py::_normalized_sha256` (a `cp` of a no-trailing-newline `VERSION` is byte-identical; tolerance would only mask corruption — B3).
- [ ] `/reflect` wiring is a DEDICATED post-write step, NOT folded into the rule-promotion-gated Step 5b (else the gate silently never runs on a version-bumping-but-no-rule-promoted slice — the R-7 / slice-022 class MCFS-1 explicitly avoided).
- [ ] Content-bearing entry-pin: `test_v_0_58_0_avfs_1_entry_present_in_repo` asserts the AVFS-1 literals (`AVFS-1`, `ADR-052`, `supersedes nothing`, the canonical "NOT a slice regression" attribution phrase, the "standalone clone, not folded into MCFS-1" decision) — NOT a tautological presence/byte-equality check (the recurring aggregated-lesson anti-pattern; MCFS-1/STP-1 entry-pin depth is the precedent).
- [ ] Non-catalog: the tool's regression suite reads the untracked, environment-mutable installed copy → it must NOT be a shippability `Machine-cmd` (slice-029/030A environment-state discipline — rows must not depend on environment-mutable/untracked state); only the two in-repo-only `test_methodology_changelog.py` pins carry row #50. NB: `essential-unregistered` does NOT apply to this path (`_ESSENTIAL_SHAPES` keys on `~/.claude/methodology-changelog.md` only — `tools/shippability_decoupling_audit.py:95-97`); the non-catalog rationale is the environment-state ground, not m-add-2.
- [ ] Self-application: shippability row pipe-free / `\|`-escaped; tool added to the cp1252 argv-classified UTF-8 regression list (slice-038 dual obligation).
- [ ] **M-add-2 (guarded build-slice leg)**: `build-slice/SKILL.md` is OSDG-1/mini-CAD-guarded — after adding the AVFS-1 Step-6 block in-repo, forward-sync the installed `~/.claude/skills/build-slice/SKILL.md` in the SAME fix block; the `/build-slice` skill-drift test (`tests/methodology/test_build_slice_skill_drift.py`) is a hard pre-finish gate and will FAIL on a stale install.
- [ ] **M-add-1 (unguarded reflect leg)**: `reflect/SKILL.md` is NOT OSDG-1-guarded. Hand-verify the installed `~/.claude/skills/reflect/SKILL.md` AVFS-1 post-write block is byte-equal (modulo EOL) to the in-repo copy at this slice's own `/reflect` post-write step (AVFS-1 cannot self-detect a stale reflect leg — R-7/slice-022 class). `/reflect` MUST record a Discovered-gap entry nominating `reflect/SKILL.md` for a future OSDG-1-extension slice (the design's "must-not-defer + self-run" is explicitly NOT sufficient for this leg).

## Out of scope

- Folding the `ai-sdlc-VERSION` leg INTO MCFS-1's existing whole-file gate as one combined module — this slice ships a standalone analogue (the `_index.md` lesson offered both; standalone is the cheaper, lower-blast-radius cut). A future consolidation slice may merge them.
- Guarding `plugin.yaml.version` drift — already covered by PMI-1's in-repo `VERSION`==`plugin.yaml` check; not this slice.
- Retroactively repairing any historical drift — the installed leg is currently in sync (`0.57.0`); this is a forward gate, not a remediation.
- Promoting the gap to a risk-register ID — slice-049 reflection already decided NOT to (impact low, no audit consumes the installed file); this slice retires the gap by gate, not by risk-tracking.

## Dependencies

- Prior slices: [[slice-041-reframe-installed-pin-forward-sync-invariant]] — MCFS-1 (`tools/methodology_changelog_forward_sync.py`) is the exact template for module shape, exit-code semantics, attribution, non-catalog-by-construction design, and the 2-point wiring.
- Prior slices: [[slice-038-pin-shippability-runner-segment-contract]] — the new-`tools/*.py`-with-`main()` self-application dual obligation (UTF-8 argv list + pipe-free shippability row).
- Vault refs: [[decisions/ADR-051]] — a drift-guard / methodology-surface audit-gate addition with no other bump reason IS a methodology-surface behavior change → minted-RULE-ID + `## vN.N.0` + 4-part PMI-1 bump path.
- Vault refs: [[decisions/ADR-042]], [[decisions/ADR-043]] (MCFS-1 lineage), [[decisions/ADR-033]] (EOL-DRIFT-1 EOL-agnostic comparison).
- Risk register: no open risk ID — this slice retires a tracked-as-discovered-gap (slice-048/049 Discovered), not a registered risk.

## Mid-slice smoke gate

At ~50% of build (module + core semantics implemented, before wiring + changelog):
```
$PY -m pytest tests/methodology/test_ai_sdlc_version_forward_sync.py -q
$PY -m tools.ai_sdlc_version_forward_sync --json
```
Expected: the core-semantics tests transition WRITTEN-FAILING → PASSING; the live `--json` run reports `status: synced`, exit 0. This validates the **pre-bump** state ONLY (in-repo `VERSION` still `0.57.0` == installed `0.57.0`) — it is a comparator/path-resolution sanity check, **NOT** a proxy for the Step-6 self-application (by Step 6 in-repo is `0.58.0` and the gate's correctness depends on the 4-part bump having forward-synced the installed leg — see M1 below). If the live pre-bump run does NOT report synced: STOP — the comparator or path resolution is wrong, diagnose before wiring.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] `tools/test_first_audit.py --strict-pre-finish` green (every TF-1 row PASSING)
- [ ] `tools/plugin_manifest_audit` green (4-part bump consistent: VERSION==plugin.yaml==0.58.0)
- [ ] **M1 bootstrap**: manually verify `~/.claude/ai-sdlc-VERSION` == `0.58.0` was forward-synced as part of this slice's own 4-part PMI-1 bump BEFORE running AVFS-1 at Step 6. A non-zero AVFS-1 at slice-050's own Step 6 is the EXPECTED signal that the installed-VERSION forward-sync was missed (exactly the N=2-drift leg this slice gates) — perform/repair the sync and re-run until exit 0; this is NOT a slice defect.
- [ ] **M-add-2**: `/build-slice` skill-drift test green — installed `~/.claude/skills/build-slice/SKILL.md` forward-synced with the AVFS-1 Step-6 block (OSDG-1/mini-CAD hard finish-gate).
- [ ] **M-add-1**: installed `~/.claude/skills/reflect/SKILL.md` hand-verified byte-equal (modulo EOL) to the in-repo AVFS-1 post-write block; `/reflect` Discovered-gap nomination of `reflect/SKILL.md` for future OSDG-1 extension recorded.
- [ ] MCFS-1 itself still green (the new gate must not perturb the changelog forward-sync)
