# Code Review: Slice 083 add-pcr-2b-hard-class-conflict-resolution

**code-Critic reviewed**: slice diff vs default branch `master` (filtered to in-scope paths)
**Date**: 2026-05-30
**Result**: FINDINGS (0 blockers, 2 majors, 4 minors) — v1 advisory; all 5 actionable findings ACCEPTED-FIXED in-loop, m4 ACKNOWLEDGED (no action).

## Summary

Solid, defensively-engineered slice — the core safety invariant (HARD/MIXED never auto-merge; `resolve_hard_conflict` returns STOP; rebase left in-progress) holds and is exercised by real tmp-repo `git rebase` fixtures (APED-1). No blockers. The code-Critic empirically verified `_CONFLICT_MARKER_OPENER_RE` against an adversarial battery and surfaced one genuine safety false-negative (M2 — diff3 base markers) and one real contract-consumption gap (M1 — `--verify-resolution` exit-1 unconsumed), plus ADR-authoring drift (m1/m2) and a missing edge-case pin (m3). All fixed this slice; full suite 1192 passed post-fix.

## Changed files (in-scope)
- tools/parallel_conflict_resolver.py
- skills/commit-slice/SKILL.md
- methodology-changelog.md
- plugin.yaml
- pyproject.toml
- VERSION
- tests/methodology/test_commit_slice_skill_tri_resolve_gate.py
- tests/methodology/test_methodology_changelog.py
- tests/methodology/test_parallel_conflict_resolution_log_hard.py
- tests/methodology/test_pcr_2b_hard_conflict_dispatch.py
- tests/methodology/test_pcr_2b_mixed_routes_to_hard.py
- tests/methodology/test_pcr_2b_repro_hard_gate_closed.py
- tests/methodology/test_pcr_2b_verify_resolution.py
- architecture/slices/slice-083-add-pcr-2b-hard-class-conflict-resolution/build-log.md

## Findings

### Blockers (advisory in v1)
None. The fail-closed safety contract is intact and tested; the resolver never runs `git rebase --continue` for HARD/MIXED.

### Majors

#### M1: SKILL.md step 4 cannot distinguish `--verify-resolution` exit-1 (git-state-unreadable) from a re-resolvable STOP
- **Issue**: the CLI emits `action: "STOP"` for ALL non-clean outcomes (only `git-state-unreadable` sets exit 1); SKILL.md step 4 keyed only on `action: STOP` and routed broken git state to "return to step 3" instead of fail-closed abort. Contract error-semantics unconsumed by the sole caller (Newman).
- **Disposition**: **ACCEPTED-FIXED** — `skills/commit-slice/SKILL.md` step 4 now branches on exit code FIRST: `exit 1` (`git-state-unreadable`) → SOAD-1 abort (mirrors the `--resolve-soft` exit-1 handling); `exit 0 + STOP` → re-resolve; `exit 0 + CLEAN` → proceed. Installed copy re-synced (OSDG-1).

#### M2: `_CONFLICT_MARKER_OPENER_RE` `{7}`-exact quantifier + missing diff3 `|||||||` base marker
- **Issue**: `{7}`-exact missed ≥8-char runs; and a `merge.conflictStyle=diff3`/`zdiff3` user who deletes `<<<<<<<`/`>>>>>>>` but leaves the `|||||||` base block staged would pass `--verify-resolution` CLEAN — a real safety false-negative (Hendrickson boundary heuristic).
- **Disposition**: **ACCEPTED-FIXED** — regex broadened to `(?m)^[ +-]?(?:<{7,}|>{7,}|\|{7,})(?:\s|$)` (git's own ≥7 rule + diff3 base separator; `|||||||` has no legitimate markdown analog — table separators are `| --- |`, never 7 consecutive pipes). New test `test_verify_resolution_stop_on_diff3_base_marker_leftover` pins it. (Docstring made a raw string to clear the `\|` SyntaxWarning.)

### Minors

#### m1: ADR-075 "Options considered / B" numbering-corrupted (orphaned duplicate `2.`/`3.`)
- **Disposition**: **ACCEPTED-FIXED** — deleted the orphaned pre-revision residue (lines 47-50); the authoritative option set is the post-M-add-2 list (B-1 = `code-review` agent, chosen).

#### m2: ADR-075 Decision step 3 still referenced the rejected `=======` marker
- **Disposition**: **ACCEPTED-FIXED** — Decision step 3 reworded to the opener-keyed (`<<<<<<<`/`>>>>>>>`/`|||||||`, NOT `=======`) detection, consistent with the M-add-1 fix the same ADR documents.

#### m3: Documented committed-marker-context false-negative (staged-vs-HEAD keying) unpinned
- **Disposition**: **ACCEPTED-FIXED** — added `test_verify_resolution_clean_on_committed_marker_context_line` asserting a `<<<<<<<` line unchanged vs HEAD verifies CLEAN, pinning the `git diff --cached` keying so a future refactor to whole-file grep is caught as an intentional contract change.

#### m4: `resolve_hard_conflict` re-runs `classify_conflict(diag)` (redundant recompute)
- **Disposition**: **ACKNOWLEDGED — no action**. `classify_conflict` is a pure deterministic function of the frozen `diag`, so the recompute cannot disagree with the caller's `cls`; it is intentional defense-in-depth (catches direct external callers passing a non-HARD diag, pinned by `test_resolve_hard_conflict_returns_gate_context_stop`). Not a defect.

## Dimensions checked
- [x] Unfounded assumptions — m2 (ADR Decision claimed `=======` detected; code did not) — FIXED.
- [x] Missing edge cases — M2 (diff3 `|||||||` + ≥7 runs) — FIXED; m3 (committed-marker-context) — FIXED (pinned).
- [x] Over-engineering — none (m4 recompute is justified defense-in-depth).
- [x] Under-engineering — M2 (leftover-marker detector under-covered marker variants) — FIXED.
- [x] Contract gaps — M1 (`--verify-resolution` exit-1 unconsumed by the sole caller) — FIXED.
- [x] Security — none. Cooperative-not-adversarial (ADR-067); list-form argv (no shell), no secrets/injection; TRI-RESOLVE-1 user gate is apply authority; resolver never auto-continues.
- [x] Drift from vault — m1 (ADR option numbering) + m2 (ADR vs code marker-set) — both FIXED. Code-vs-design "Components touched" match; MEPD-1 5-part bump present.
- [x] Web-known issues — Skipped beyond local verification (methodology-internal git-orchestration; no external API/SDK). The git conflict-marker format + `merge.conflictStyle` surface verified empirically; the diff3 base-marker gap (M2) filed from direct repro.
- [x] Cross-cutting conformance — APED-1 satisfied (the marker regex executed against an adversarial battery incl. the new diff3 fixture); EOL-DRIFT-1 (`newline=""` preserved); RSAD-1 (slice's own tests green — full suite 1192 post-fix).
