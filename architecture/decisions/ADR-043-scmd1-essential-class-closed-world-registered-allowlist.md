---
id: ADR-043
title: Reframe SCMD-1's essential class to a closed-world non-empty catalog-registered intentional-installed allowlist (registers exactly the cross-module slice-019 LAYER-EVID-1 pin)
date: 2026-05-18
slice: slice-041-reframe-installed-pin-forward-sync-invariant
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-043: SCMD-1 essential class → closed-world non-empty registered intentional-installed allowlist

## Context

> **Rev-3** (post 2× BLOCKED + TRI-1 re-ratification). rev-1's `_REGISTERED_INSTALLED_READERS = frozenset()` ("empty post-041; re-home everything") was a **deviation from the literal R-4 charter** (`risk-register.md` L90: *"a catalog-derived intentional-installed allowlist, the read **registered** not **absent**"*) and was empirically falsified — the cross-module slice-019 LAYER-EVID-1 pin `tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces` provably stays `essential` after any leg-drop that retains its in-repo changelog surface (DR-1 executed `classify_fn`; both rev-1 reviewers had only reasoned about `_ESSENTIAL_SHAPES`). The honest classification of that pin's installed-changelog read is **intentional and protective** (part of an N=6-surface byte-equality assertion), i.e. exactly the "essential" the charter says to *register*, not eliminate.

`tools/shippability_decoupling_audit.py` `audit()` currently does, for any cited fn reaching `~/.claude/methodology-changelog.md`: `result.essential.append(qual)  # recognized, NOT flagged` — a passive silent pass. M-add-1 (slice-030B meta-Critic, carried here): a future compensating guard, if catalog-cited and essential, would be silently absorbed — relocation invisible.

## Options considered

1. **Keep passive recognition** — the dual-Critic stack provably cannot reach this audit-vs-artifact interaction (slice-031/033 law; demonstrated again here — both rev-1 reviewers false-confirmed). Rejected.
2. **Empty allowlist, hard-fail all essential** — empirically impossible (the LAYER-EVID-1 pin cannot be made non-essential without destroying its in-repo protection); also charter-divergent. Rejected (rev-1, falsified).
3. **Closed-world non-empty registered allowlist** — `_REGISTERED_INSTALLED_READERS` registers exactly the genuinely-intentional reader(s) with rationale; a cited fn classified `essential` whose qualname ∉ the set ⇒ `Violation(reason="essential-unregistered")` exit 1; ∈ ⇒ *accounted-for* (exit-0-eligible). The read is **registered, not absent** — the charter's literal wording. DR-1-verified by execution: post-decouple essential set = exactly `{the cross-module pin}` (cardinality 1); registering that one qualname ⇒ exit 0 ⇒ R-4 retireable; the closed-world rule HALTs any *future* unregistered essential (relocation-proof). Chosen.

## Decision

Add `_REGISTERED_INSTALLED_READERS: frozenset[str] = frozenset({"tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces"})` (1 element + inline rationale comment: *slice-019 LAYER-EVID-1 N=6-surface byte-equality pin; its installed-methodology-changelog read is an intentional cross-surface forward-sync assertion, not incidental coupling; registered per R-4 charter "registered not absent"; do not add entries without an ADR + rationale*). Key form = the exact audit-emitted file-path-qualified `::`-selector (DR-1 flag — a typo'd key silently fails-open; V3 regression test asserts the key resolves against the real catalog). In `audit()`, an `essential`-classified cited fn ∈ the set is recorded `essential_registered` (not a violation); ∉ ⇒ `Violation(reason="essential-unregistered")` exit 1. `to_dict`/`_format_human` report `essential_registered` + `essential_unregistered`. `classify_fn`/`_ESSENTIAL_SHAPES`/`_reachable_path_segments` **unchanged** (their semantics are correct; rev-2 B1 was a design misread, not an audit bug — changing them is out of scope). With [[ADR-042]]'s decouple landed, the essential set = the sole registered member ⇒ exit 0; R-4 → `retired`.

## Consequences

- The essential-coupling relocation surface is **closed-world policed**: any future catalog-cited fn reaching installed methodology-changelog HALTs unless deliberately registered with rationale + ADR — M-add-1 discharged structurally.
- SCMD-1 reported semantics change (`essential=N (recognized, 030C)` → `essential_registered` + `essential_unregistered`; unregistered is exit 1) — a real behaviour change driving the MCFS-1 RULE-ID + v0.53.0 + 4-part PMI-1 obligation.
- `tests/methodology/test_shippability_decoupling_audit.py` gains: registered-member→exit-0, deliberately-unregistered-fixture→exit-1, and the V3 key-resolution regression.
- The allowlist is intentionally minimal (1 entry); growth requires an ADR — it must not become a silent escape hatch.

## Reversibility

**cheap**: one constant + one `audit()` branch + output-string change, regression-tested. Revert = restore the silent `result.essential.append` + drop the constant; ≤30-min mechanical. Coupled with [[ADR-042]] (both cheap) for the R-4 retirement.
