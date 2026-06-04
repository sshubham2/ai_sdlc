---
id: ADR-102
title: SKILL.md-prose op-gate REUSES the existing vault_flip_prose_inventory (slice-107) — not a new classifier in the readiness audit; un-routed in-loop write-ops gated, deferred writes held gate-visible (DEFERRED_TO_FLIP)
date: 2026-06-04
slice: slice-110-make-pipeline-vault-location-agnostic
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-102: Readiness audit scans SKILL.md prose, not just .py

> **Implementation status (slice-110 Phase-1-only ship, 2026-06-04):** this decision is **ratified** but its **implementation is DEFERRED to the Phase-2 follow-on slice**. slice-110 shipped Phase 1 (the location-agnostic test suite, AC1+AC5) and deferred AC2/AC3/AC4 at the design-sanctioned Phase 1→2 split. The op-gate (AC3) — extending `tools/vault_flip_prose_inventory.py` with an operational-op gate mode + the `DEFERRED_TO_FLIP` class + shippability propagation — lands in the follow-on. The decision text below stands as the ratified design the follow-on implements.

## Context

`tools/vault_flip_readiness_audit.py` (`_iter_scan_files`, `:488-507`) globs only `tools/*.py` + `skills/**/*.py` + `tests/**/*.py`. It does NOT scan `SKILL.md` prose. The slice-110 flip review's meta-Critic surfaced (M-add-1/B3) that the **dominant** in-loop break post-flip is in SKILL.md prose, not `.py`: `/reflect`'s archive step is the literal shell op `mv architecture/slices/slice-NNN-<name>/ architecture/slices/archive/` (`skills/reflect/SKILL.md:320`), with the same break in `/archive:51` and literal `Write`-target paths in `/validate-slice:83`, `/drift-check:109`, `/slice:267-268`. Because the audit is `.py`-only, the AC2 "readiness gate clean" gave **false flip-safety** — the audit was structurally blind to the class of break that actually matters most for the in-loop pipeline.

This slice routes those SKILL.md vault ops through the seam (AC2); this ADR makes that routing **enforced** so a future un-routed SKILL.md vault write is caught as a regression — the only deterministic guard for the prose-routing (SKILL.md prose is not executed in pytest).

## Options considered

1. **Leave the audit `.py`-only; rely on review.** Con: the exact gap that hid `/reflect:320`; an un-routed prose write silently breaks the in-loop pipeline post-flip with a green gate. **Rejected.**
2. **A separate new audit tool for SKILL.md prose.** Con: a new tool ⇒ PMI-1/INST-1 fan-out; duplicates the readiness audit's classifier + baseline machinery. **Rejected.**
3. **Extend the existing readiness audit** (chosen): add `skills/**/SKILL.md` to the scan surface with a prose classifier for literal in-tree `architecture/`/`diagnose-out/` shell ops (`mv`/`cp`/`git add`) + literal `Write`-tool-target paths; re-baseline. One tool, one baseline, the existing `--strict` gate.

## Decision

**Superseded by `/critique-review` M-add-1 (the readiness audit is the WRONG home — REUSE the existing tool):** `tools/vault_flip_readiness_audit.py` is Python-`tokenize`/`ast`-based (`:459`/`:477`) and cannot ingest Markdown (`/critique` B3 — a SKILL.md collapses to one `NEEDS_HUMAN(parse-error)`). But a **distinct new classifier in it would duplicate** `tools/vault_flip_prose_inventory.py` (slice-107), which ALREADY scans `skills/**/SKILL.md`, region-anchors on `in_code` + `_OP_VERB_RE` (`:211`), classifies `rewrite-at-flip` vs `doc-example`, and is gate-capable (`--strict` exit 2). **Decision: extend `vault_flip_prose_inventory` with an operational-op GATE MODE** (or share its region-anchoring helper), NOT a third parallel classifier (CSP-1/DRY). The semantic split is explicit: the inventory flags ALL 318 location-literals (everything goes stale at flip); the op-gate flags only **un-routed in-loop write-OPS** — `mv`/`cp`/`git add`/`Write`-target inside an anchored region. A bare prose mention OUTSIDE those regions (244 across 24 SKILL.md files, ~16:1 noise:signal) → never gated (AP-1). Proven BOTH non-vacuous (synthetic un-routed `Write architecture/...` flagged) AND non-over-flagging (the 244 NOT flagged) by EXECUTION at build (APED-1) + a **code-Critic pass** (AP-4 — parser change). **Deferred writes stay gate-visible (`/critique-review` M-add-2 / AP-12):** the per-slice active-folder write-ops deferred to the flip slice (AC2) are NOT folded into a silent `DOC_EXAMPLE_SAFE` / baseline — they land in a DISTINCT **`DEFERRED_TO_FLIP`** class tagged with their owner (the flip slice), which the flip slice's pre-finish MUST drive to ∅. Never empty a fail-closed bucket via a silent waiver. **Shippability (M-add-3 / RPCD-1/SCPD-1):** the op-gate capability propagates into `architecture/shippability.md` rows 108/109.

## Consequences

- The AC2 "readiness gate clean" becomes a *real* guard for in-loop-skill flip-safety, not a `.py`-only proxy.
- The 318-prose-rewrite slice + the flip slice inherit a gate that catches an un-routed in-loop vault write.
- Risk: a lexical SKILL.md classifier can over-flag a legitimate prose mention; the classifier must region-anchor (shell-op / `Write`-target context), not bare-substring (AP-1) — proven non-vacuous AND non-over-flagging against the real corpus at `/build-slice` (APED-1).

## Reversibility

**Cheap.** An additive scan surface + classifier on an existing audit; `git revert` removes it. No data model, schema, or contract lock beyond the audit's own baseline (re-derivable).
