---
id: ADR-104
title: The vault-flip op-gate classifies in-loop skill vault write-ops structurally (routed / deferred-to-flip / out-of-scope / un-routed violation)
date: 2026-06-04
slice: slice-111-route-in-loop-skill-vault-ops-via-seam
reversibility: cheap
status: accepted
---

# ADR-104: Structural, in-loop-scoped op-gate for un-routed vault write-ops (implements ADR-102)

> **Refined at /critique-1 + /critique-review (slice-111)**:
> - rule for the deferred bucket keys on the op's **destination/sink**, NOT "any active-folder literal on the line" (B2 / AP-15).
> - **a 4th gate-visible class `OP_OUT_OF_SCOPE`** + a pinned **`_IN_LOOP_SKILLS`** allowlist were added (M-add-1, meta-Critic Blocker): the scan covers all skills, but `OP_UNROUTED` (exit 2) fires ONLY for an `_IN_LOOP_SKILLS` skill's un-routed write to a vault file slice-111 commits to routing; out-of-loop skills' un-routed shared-aggregate writes (`critic-calibrate`, `triage`, `risk-spike`, `supersede-slice`, …) + in-loop writes to files whose flip-disposition is the flip slice's to decide (e.g. the `slice-queue.md` main-tree ledger / `git add` ops) → `OP_OUT_OF_SCOPE` (gate-visible, count-floored, owner = prose-rewrite/flip slice), NOT a violation. Without this the gate could never go green (the real corpus has many out-of-scope un-routed shared-aggregate writes).
> - the `OP_DEFERRED_TO_FLIP` drain obligation + the cross-store archive-`mv` hazard are R-32.a / R-32.b (M3).
> - MEPD-1 EXCLUDE precedent verified at build (m2).

## Context

[[ADR-102]] (ratified at slice-110, implementation deferred) decided that the vault-flip readiness check must scan **SKILL.md prose** for in-tree vault references, closing the `.py`-only blind spot of `tools/vault_flip_readiness_audit.py`. The CSP-1/DRY resolution (slice-110 `/critique-review` M-add-1) was to **reuse** `tools/vault_flip_prose_inventory.py` (slice-107) — NOT a third parallel classifier.

The inventory answers "which location-*literals* must be rewritten at flip" (the 318 `rewrite-at-flip` checklist). The op-gate answers a **distinct** question: "which in-loop skill vault **write-ops** are un-routed and will silently break/mis-write at flip?" Same anchoring machinery, different concern.

Three failure modes to avoid:
- **Silent waiver** (slice-110 `/critique-review` M-add-2 / AP-12): a deliberately-deferred write must NOT vanish from the gate into a quiet baseline; it lands in a DISTINCT, gate-visible, owner-tagged bucket a contractually-required consumer drains.
- **Cheap-proxy classification** (slice-098 AP-15): a guard must key on a structural property, not a deletable marker — and not on a literal that happens to share a line with the op (B2).
- **Scope-vs-taxonomy mismatch** (slice-111 `/critique-review` M-add-1): the scan domain (all skills) is wider than what slice-111 routes (in-loop ops); the taxonomy must give out-of-scope writes a NON-violating, gate-visible home, or the gate can never go green.

## Options considered

1. **In-loop allowlist + `OP_OUT_OF_SCOPE` class (chosen)** — pin `_IN_LOOP_SKILLS`; `OP_UNROUTED` (exit 2) only for those; everything else un-routed → `OP_OUT_OF_SCOPE` (visible, count-floored). Pro: gate goes green, nothing silently excluded (AP-12), flip-readiness for out-of-scope writes stays visible (owner = prose-rewrite slice). Con: needs a pinned skill set + a deferred-op allowlist whose exact membership is APED-1 build work.
2. **Restrict the scan to in-loop skills only** — con: out-of-loop un-routed writes become INVISIBLE to the flip-readiness gate (a silent gap the flip slice trips on) — the AP-12 anti-pattern at the scan level.
3. **Route ALL skills' vault ops now** — con: scope explosion far beyond "in-loop" (a separate slice).

(Rejected at /critique-review: option 2 by the user's TRI-1 choice; option 3 as out-of-scope.)

## Decision

Add an **`--op-gate` mode** to `tools/vault_flip_prose_inventory.py` (reusing `_iter_scan_files` over `skills/**/SKILL.md`, `_in_inline_code` + fence-tracking, and the `--strict` baseline machinery). A line is an op-candidate iff it carries a **write-op verb** (`mv`/`move`/`cp`/`copy`/`rm`/`delete`/`write`/`edit`/`create`/`append` + the `git add` bigram; detection set documented as a superset of the classification set — AP-16/m1) AND a vault location-literal in an anchored region. Reads are NOT gated (a read breaking at flip fails LOUD; the R-32 hazard is the SILENT mis-write).

A pinned **`_IN_LOOP_SKILLS`** allowlist names the slice-loop skills (the PCA-1 chain + its in-loop maintenance: `slice`, `design-slice`, `critique`, `critique-review`, `build-slice`, `code-review`, `validate-slice`, `reflect`, `commit-slice`, `archive`, `drift-check`). Membership is pinned + count-floored (FBCD-1); a member add/remove is a deliberate, pinned change.

Candidates classify in order (first wins), keyed on the op's **destination/sink** (for `mv`/`cp` the last path arg; for `Write`/`Edit`/`create`/`append` the target path; for `git add` each path arg). An op whose sink cannot be determined defaults to `OP_UNROUTED` (fail-safe, never a silent pass):

1. **`OP_ROUTED`** — the op's anchored region carries a seam token (`vault_edit` / `VAULT_ROOT`). Informational.
2. **`OP_DEFERRED_TO_FLIP`** — destination resolves to a per-slice ACTIVE folder (`slices/slice-NNN…`, excluding `slices/archive/`). Gate-visible, count-floored, owner = flip slice (**R-32.a**). NOT a violation.
3. **`OP_OUT_OF_SCOPE`** — un-routed write whose owning skill ∉ `_IN_LOOP_SKILLS`, OR an in-loop write to a vault file whose flip-disposition is the flip slice's to decide (the `slice-queue.md` main-tree coordination ledger; `git add` of git-tracked vault paths). A pinned, count-floored, owner-tagged (prose-rewrite/flip slice) allowlist whose **exact membership is finalized at build via APED-1** (run the gate against the real corpus; every entry is enumerated, never a silent baseline). NOT a violation.
4. **`OP_UNROUTED`** — un-routed write, owning skill ∈ `_IN_LOOP_SKILLS`, destination = a shared aggregate vault file slice-111 commits to routing (the archive `mv` dest `slices/archive/`, `drift-log.md`) → **gate violation** (exit 2).

The op-gate is **enforced via its suite test** (`tests/methodology/test_vault_flip_op_gate.py::test_real_corpus_op_gate_green`, which runs in the pre-finish full suite and fails on any new in-loop `OP_UNROUTED`) **+ a shippability row** — NOT a `/build-slice` Step-6 RULE-ID gate. This follows the m2-verified flip-prep precedent: slice-100's `vault_flip_readiness_audit` + slice-107's `vault_flip_prose_inventory` are not Step-6-wired either; they are suite-test + shippability enforced, MEPD-1 EXCLUDE, no RULE-ID. Proven against the real corpus (APED-1) with an AP-4 code-Critic pass:
- **Non-vacuity**: a synthetic in-loop un-routed `mv slices/foo slices/archive/` (no seam token) → `OP_UNROUTED`/exit 2.
- **Dual-literal non-vacuity (B2)**: a synthetic in-loop un-routed `mv slices/slice-NNN slices/archive/` → `OP_UNROUTED` (the `slices/slice-NNN` SOURCE literal does NOT buy a deferral — only an active-folder *destination* does).
- **OP_OUT_OF_SCOPE non-vacuity (M-add-1)**: an out-of-loop skill's un-routed `Append to architecture/<aggregate>` (e.g. `critic-calibrate`) → `OP_OUT_OF_SCOPE`, exit 0 (visible, not a violation); a NEW in-loop un-routed shared-aggregate write → `OP_UNROUTED` (the gate still bites in-loop).
- **Non-over-flag**: the ~244 bare prose mentions + read-references (no write-op verb, or no vault literal) → not flagged.
- **DEFERRED auto-classify**: a write whose destination is `slices/slice-NNN/<file>` (e.g. `/reflect` reflection.md) → `OP_DEFERRED_TO_FLIP`, exit 0.
- **Detection⊇classification (AP-16, m1)**: every `git add architecture/...` form (`-A`, `--all`, multi-flag, multi-path) is detected; no plain-prose "add"/"write" line without a vault literal is flagged.

## Consequences

- After AC1 routing, the real corpus yields **0 `OP_UNROUTED`** (gate green) with: in-loop routed writes → `OP_ROUTED`; in-loop per-slice writes → `OP_DEFERRED_TO_FLIP`; out-of-loop + undecided-disposition writes → `OP_OUT_OF_SCOPE`.
- **Contractual consumers (M3 / AP-12)**: `OP_DEFERRED_TO_FLIP` is drained by the flip slice per risk-register **R-32.a** (un-drained at flip = violation, not silent waiver). `OP_OUT_OF_SCOPE` is owned by the prose-rewrite/flip slice (the same destination-rewrite work that owns the 318 `rewrite-at-flip` literals). Both buckets are `--strict` count-floored (a silent shrink — quietly deleting a deferred op to dodge the gate — trips exit 2).
- A future skill that adds an un-routed in-loop shared-aggregate write fails the slice-finish gate (the silent-regression class is closed for in-loop skills); out-of-loop additions surface in `OP_OUT_OF_SCOPE` (visible, not blocking).
- The `_IN_LOOP_SKILLS` allowlist + the `OP_OUT_OF_SCOPE` deferred allowlist are FBCD-1 counted sets — their counts are pinned + fan-out-grepped on any membership change.
- OSDG-1 re-sync set: `{/reflect}` — the ONLY guarded edited skill (archive `mv` routing). build-slice/validate-slice are NOT edited (the op-gate is suite-test-enforced, above). `/archive`, `/drift-check` are unguarded (no `*_skill_drift.py`) — their installed copies are **hand-synced** with a documented residual (m-add-5). `/design-slice` is NOT edited (B1).
- MEPD-1 determination: **EXCLUDE** — implements the already-minted [[ADR-102]] (consistent with flip-prep family slice-106/109/110); precedent **verified at build (m2)**: slice-100's readiness audit + slice-107's prose inventory are suite-test + shippability enforced, carry no RULE-ID, and are NOT `/build-slice` Step-6 gates — so the op-gate following suit (no RULE-ID, no changelog entry, no VERSION bump) is the verified-correct precedent, not an asserted one. Shippability row still propagates (RPCD-1/SCPD-1) for discoverability.

## Reversibility

**Cheap** — an additive mode on an existing tool + a wiring line in two skills + in-module pinned sets (re-derivable). A revert removes the gate with no data or contract migration.
