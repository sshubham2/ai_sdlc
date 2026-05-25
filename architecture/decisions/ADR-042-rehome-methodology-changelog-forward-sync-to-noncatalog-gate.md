---
id: ADR-042
title: Re-home the per-version in-repo↔installed methodology-changelog forward-sync to one non-catalog whole-file EOL-agnostic gate (MCFS-1); register the cross-module LAYER-EVID-1 pin rather than re-home it
date: 2026-05-18
slice: slice-041-reframe-installed-pin-forward-sync-invariant
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-042: Re-home methodology-changelog forward-sync to a non-catalog MCFS-1 gate

## Context

> **Rev-3** (post 2× BLOCKED + slice-030A/031 non-convergence pivot + TRI-1 re-ratification). rev-1 ("essential = the 32 `_entry_present_*`; empty allowlist") and rev-2 ("leg-drop the cross-module pin → clean") were both empirically falsified by *executing* `tools.shippability_decoupling_audit`. The DR-1 meta-Critic re-executed and verified the rev-3 design: post-leg-drop the essential set is **exactly one fn** (the cross-module LAYER-EVID-1 pin); registering it makes R-4 retireable; no relocation.

A family of `tests/methodology/test_methodology_changelog.py` fns (28 `_entry_present_in_repo_and_installed` + 5 `_entry_names_*`/`_supersession`, audit-derived) plus one cross-module pin `tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces` read the **untracked** `~/.claude/methodology-changelog.md`. For the in-`test_methodology_changelog.py` fns this read IS the forward-sync assertion with no BCI-1 analogue (R-4's essential-class residual; false-PCA-1-HALT window). For the cross-module pin the read is part of a slice-019 LAYER-EVID-1 N=6-surface byte-equality protection — intentional, not incidental. `classify_fn` is an unordered cross-expression subset test over `{".claude","methodology-changelog.md"}`: the in-`test_methodology_changelog.py` fns get `.claude` *only* from the installed read-leg (their in-repo leg is `read_file(...)` — no `.claude`), so leg-drop genuinely yields `clean`; the cross-module pin additionally reaches `.claude` via a retained `Path.home()/".claude"/"skills"/"diagnose"` line and `methodology-changelog.md` via a retained in-repo surface, so leg-drop provably cannot reclassify it `clean` without destroying the LAYER-EVID-1 in-repo protection.

## Options considered

1. **Per-fn tracked installed-mirror fixture** — relocates the flaw (rev-1 M-add-1). Rejected.
2. **Empty allowlist / re-home everything (rev-1)** — empirically impossible: the cross-module pin cannot be made `clean` by leg-drop while retaining its LAYER-EVID-1 in-repo surface (DR-1-executed). Rejected (falsified).
3. **Re-home the in-`test_methodology_changelog.py` legs to a non-catalog whole-file MCFS-1 gate AND register the cross-module pin as intentional (non-empty allowlist)** — whole-file in-repo≡installed equality is strictly stronger than ~33 per-version substring reads and is the sound deterministic downstream control for the non-deterministic PMI-1 forward-sync (BCI-1/slice-030A precedent). The cross-module pin's installed read is genuinely intentional, so it is *registered* (the R-4 charter's literal "intentional-installed allowlist, the read **registered** not **absent**"). DR-1-verified mechanically exact (registered cardinality = 1; 0/37 in-module fns stay essential post-leg-drop). Chosen.
4. **Tighten `classify_fn` to ordered/contiguous matching** — out of scope per mission-brief; own audit-semantics blast radius. Rejected.

## Decision

Create `tools/methodology_changelog_forward_sync.py` (RULE-ID **MCFS-1**), a BCI-1-shaped deterministic gate asserting in-repo `methodology-changelog.md` is content-equal **modulo line endings** (EOL-DRIFT-1 / [[ADR-033]] semantics, CSP-1-parity-pinned to `tests/skill_drift_equality.py::_normalized_sha256`) to installed `~/.claude/methodology-changelog.md` — installed-absent → WARN exit 0, present-divergent → HALT exit 1 (attributed), wired non-opt-out at `/build-slice` Step 6 (verified ungated — runs every slice, not rule-promotion-gated) + a NEW dedicated `/reflect` post-write step (NOT folded into the rule-promotion-gated Step 5b). **Decouple** = drop only the `Path.home()/".claude"/"methodology-changelog.md"` read-leg from the audit-derived in-`test_methodology_changelog.py` essential set (∪ the 4 defined-but-uncited `_entry_present_*`); retain every in-repo content/canonical-phrase assertion (m2). The **cross-module pin is registered, not modified** (see [[ADR-043]]). **No rename** (TRI-1 scope-cut — orthogonal to R-4; separate identifier-truth slice). The slice's own `v0.53.0` MCFS-1 entry-pin keeps the existing naming convention with an **in-repo-only body** (M3), sequenced LAST (slice-037).

## Consequences

- Post-rev-3 essential set = exactly the registered cross-module pin ⇒ SCMD-1 exit 0 ⇒ the essential-class false-PCA-1-HALT window closes; R-4 escalates to `retired` (with [[ADR-043]]).
- Forward-sync enforced more strongly (whole-file) and in one place; new methodology versions no longer each add a coupled fn.
- The decoupled `_entry_present_in_repo_and_installed` fns' names temporarily over-claim (no longer read installed) — consciously accepted (slice-035: decided, not discovered); the chartered follow-up rename slice realigns all uniformly. `agents/critique.md:123` MEPD-1 prose stays accurate for the as-yet-unrenamed fns and is NOT edited this slice.
- No `tools/`→`tests/` import inversion: local 1-line CRLF→LF normalization + CSP-1 behaviour-parity regression test ([[ADR-033]] home untouched).

## Reversibility

**cheap**: `audit()` essential-disposition + one constant + a new tool + skill-wiring + per-fn read-leg removal, all regression-tested. Revert = restore the read-legs + delete the tool/constant/wiring; ≤1-hour mechanical. No schema/contract/external-consumer impact; coupled with [[ADR-043]] (both cheap) for the R-4 retirement.
