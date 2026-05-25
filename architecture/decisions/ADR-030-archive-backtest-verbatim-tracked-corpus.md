---
id: ADR-030
title: BC-1 archive-backtests assert against a git-tracked verbatim real mini-corpus, derived (not hand-listed) from the cited incidental set
date: 2026-05-16
slice: slice-031-complete-shippability-decoupling
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-030: Archive-backtest corpus fidelity (meta-M1′)

## Context

slice-030A deferred the **archive-backtest synthetic-vs-real-corpus fidelity** question (meta-M1′) to 030B. The BC-1 archive-backtest functions (the *incidental*-class subset of the runtime-derived cited-fn set) call `audit_slice(slice_folder=REPO_ROOT/"architecture"/"slices"/"archive"/"slice-NNN-…")`. `architecture/` is gitignored (`.gitignore:11`), so these backtests read **gitignored** corpus — the C2 incidental coupling keeping those catalog rows environment-fragile (R-4 residual). Decoupling C2 forces a corpus-source decision.

(Re-scope note: slice-030B is the *incidental-only* slice after the user-ratified b-split. The essential entry-pin coupling is out of scope here — see [[ADR-031]] + the R-4 sub-entry chartering slice-030C.)

## Options considered

1. **Synthetic `_make_slice` briefs** — NOT real archived text; a real archived slice can trigger a BC-1 keyword/anchor false-positive a synthetic brief would not reproduce → detection-fidelity loss (the "silently weakened" outcome the charter forbids). Rejected.
2. **Keep gitignored real archive + skip-when-absent** — catalog row stays environment-fragile (R-4 residual unchanged); defeats the slice's purpose. Rejected.
3. **Git-tracked verbatim real mini-corpus, derived from the cited set** — real corpus → maximal detection fidelity; tracked → environment-independent; the corpus membership is **populated by the same runtime derivation** the SCMD-1 audit performs (the exact archive folders the cited incidental fns read), NOT a hand-listed slice set.

## Decision

**Option 3.** A git-tracked verbatim real mini-corpus at `tests/methodology/fixtures/archive_backtest_corpus/`. Critically, **the corpus membership is the runtime derivation, not a curated list**: the SCMD-1 audit emits the exact set of archive folders the cited incidental fns reference; the corpus contains precisely those, verbatim. The v1 design's hand-listed `slice-003/004/005/006/007/011` is **removed** — it was the slice-030 enumeration defect recurring inside the cure (it omitted **slice-001**, read by `test_slice_001_archive_still_fires_legitimate_rules` row #8 + `test_slice_001_archive_still_fires_proj2` row #12; ≥7 folders, not 6). AC2 carries a **bidirectional corpus-completeness sub-check**: (forward) every archive folder in the derived set has a corresponding tracked corpus fixture → no missing folder → no silent skip when the real archive is unavailable; (reverse, v2-m2) no orphan corpus fixture exists for a folder no longer in the derived set (derived set ⊇ corpus fixture set) → the SCPD-1 orphan-catch made concrete, no dead test data. The C1 checks-file inputs simultaneously repoint to the slice-030A canonical fixtures (BCI-1 guarantees byte-faithful). Result: real-corpus fidelity AND environment-independence — both halves of meta-M1′ without a fidelity/decoupling trade.

## Consequences

- New tracked fixture tree `tests/methodology/fixtures/archive_backtest_corpus/` (git-tracked — `tests/` is not gitignored), membership = the SCMD-1 runtime derivation.
- `test_build_checks_audit.py` incidental archive-backtests repoint `slice_folder` → tracked corpus, `project_checks`/`global_checks` → slice-030A canonical fixtures; `.exists()` skip guards removed (hard-assert; M4).
- SCMD-1 ([[ADR-031]]) statically forbids any catalog-cited fn reading `…/architecture/slices/archive/…` (incidental shape), structurally preventing C2 regression.
- Detection fidelity NOT weakened (the explicit meta-M1′ requirement).

## Reversibility

**cheap** — the corpus is test fixtures; the repoint is test-argument edits. Reverting = delete the fixture tree + restore the gitignored-archive args (re-introduces the incidental R-4 residual, but mechanically trivial). No production/contract/data-model surface.

## Corpus/source divergence (m1 — concrete, not asserted)

Archived folders under `architecture/slices/archive/` are gitignored and convention-frozen — "frozen" is a convention, **not an enforced invariant**, so the prior draft's "drift-cost ~0 because archived slices are immutable" was an unfounded assertion. The honest position: **the tracked corpus is the authoritative source of truth post-slice and is intentionally decoupled** from the gitignored original; divergence from the gitignored original is acceptable and expected. The concrete guard against the *real* risk (a cited fn reading an archive folder with no corpus fixture) is the AC2 corpus-completeness sub-check + SCMD-1's runtime re-derivation + SCPD-1 orphan-catch — a deterministic gate, not a frozenness assumption. Escalation: if the cited incidental set changes, SCMD-1's re-derivation flags any archive folder lacking a corpus fixture at the next gate run.
