---
id: ADR-106
title: The vault op-gate's sink-detector is seam-aware — it matches the `<vault>` placeholder, not only `architecture/`
date: 2026-06-04
slice: slice-113-bulk-convert-remaining-skills-to-vault-seam
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-106: The vault op-gate's sink-detector is seam-aware — it matches the `<vault>` placeholder, not only `architecture/`

## Context

[[decisions/ADR-105]] (slice-112) minted the flip-neutral `<vault>/` prose convention and converted a pilot (`CLAUDE.md` + `agents/critique.md`). slice-113 completes the rollout — converting the convertible operational `architecture/…` literals across the 25 skill `SKILL.md` files to `<vault>/…`.

The in-loop write-op gate (`--op-gate`, [[decisions/ADR-104]] / [[decisions/ADR-102]], slice-111) lives in the same module (`tools/vault_flip_prose_inventory.py`). `scan_op_file` finds a write-op's **sink literal** by scanning the line with the inventory's `_MATCH_RE = (?:architecture|diagnose-out)/` — the SAME regex the location-literal inventory uses. That sharing was correct when every operational vault path was spelled `architecture/…`.

It stops being correct the moment skill prose converts to `<vault>/…`. A converted write-op — e.g. `vault_edit append <vault>/lessons-learned.md`, or a hypothetical un-routed `Write <vault>/risk-register.md` — has a sink (`<vault>/…`) that `_MATCH_RE` does **not** match. The op-gate would simply **not see** the op:

- **Today's symptom** (slice-112 finding B2): the visible op-classes shrink. With the bulk conversion, the op-gate's view collapses from 40 ops (6 routed / 11 deferred / 23 out-of-scope) to ~15 (only the carve-out sinks that stay concrete — active-folder / slice-queue / diagnose-out), tripping the `OP_OUT_OF_SCOPE ≥ 23` floor.
- **The lasting hazard** (worse than the symptom): the op-gate's whole purpose is to catch an **un-routed in-loop vault write** (`OP_UNROUTED → exit 2`). Once the convention is the house style, in-loop skills express vault writes with `<vault>/…`. An op-gate blind to `<vault>/` is **permanently fail-OPEN** for exactly the writes it exists to catch — the rollout of the convention would *defeat* the gate that protects the convention's write-safety story (R-32).

slice-112's finding B2 was triaged DEFERRED with the framing "the follow-on owns the op-gate floor re-pin (a deliberate AP-12 gate-loosening)". slice-113's grounding against the live op-gate code + the real sink map showed that framing under-sells the fix: a downward floor re-pin is not merely a loosening, it is a **silent, permanent blinding** of the gate to the new convention. The user ratified the stronger remedy at `/design-slice` (Approach A).

## Options considered

1. **Make the op-gate sink-detector seam-aware (CHOSEN).** Give the op-gate its own sink matcher `_OP_SINK_RE = (?:architecture|diagnose-out)/ | <vault>/` (+ a token form), used by `scan_op_file` in place of the inventory `_MATCH_RE`. Converted write-ops stay visible; all 40 ops remain classified; `_OP_CLASS_FLOOR` stays `{0, 11, 23}` (no loosening); only the 3 `_OP_ALLOWLIST` entries whose lines convert are re-hashed. **Pro**: the gate gains permanent, forward-looking protection for the convention — an un-routed `<vault>/` write is caught exactly like an un-routed `architecture/` write; zero gate-loosening; the write-safety invariant survives the flip. **Con**: touches the op-gate classifier code (a new regex pair) → mandatory `/code-review` (AP-4: a new/changed classifier verb-set is a code-Critic concern the design+meta stack can't reach); the inventory `_MATCH_RE` and the op-gate `_OP_SINK_RE` are now deliberately distinct (must not be accidentally re-merged).
2. **Convert the sinks and re-pin the floors downward (slice-112 B2's anticipated path).** Leave the op-gate code untouched; accept that converted sinks vanish; re-pin `OP_OUT_OF_SCOPE` 23 → ~4 and lose `OP_ROUTED` visibility as a deliberate AP-12 loosening. **Pro**: smaller diff, no classifier-code change. **Con**: the op-gate goes ~blind to the convention and is **permanently fail-open** for future un-routed `<vault>/` writes in in-loop skills — a real, lasting protection regression dressed as a count re-pin. Rejected.
3. **Do not convert op-bearing sinks (carve them all out, keep them concrete).** Add every op-sink literal to `_CONVERTED_CARVEOUTS`. **Pro**: op-gate untouched. **Con**: leaves the op-sinks as un-converted flip-residual (defers the work to the physical move), bloats the carve-out allowlist, and STILL leaves the gate `architecture/`-only (blind to any future `<vault>/` write). Strictly worse than (1) on completeness and on protection. Rejected.

## Decision

The op-gate gets a **dedicated, seam-aware sink matcher** — `_OP_SINK_RE` (and a token-capture form `_OP_SINK_TOKEN_RE`) matching `(?:architecture|diagnose-out)/` **or** `<vault>/` — used by `scan_op_file`. The location-literal inventory's `_MATCH_RE` is **unchanged** (it must keep *not* matching `<vault>/`, so a converted literal correctly disappears from the inventory baseline + the converted-file ratchet). The op-gate's classification sub-regexes (`_ACTIVE_FOLDER_RE`, `_ARCHIVE_DEST_RE`, `_UNDECIDED_DISPOSITION_RE`, `_SEAM_TOKEN_RE`) are prefix-agnostic and unchanged — they classify a `<vault>/…` sink identically to an `architecture/…` sink.

Consequently the bulk conversion does **not** shrink the op-floors: all 40 ops stay visible, `_OP_CLASS_FLOOR` is unchanged, and the only op-gate re-pin is re-hashing the `_OP_ALLOWLIST` entries whose lines convert (`build-slice:407`, `commit-slice:216`, `design-slice:240`; `slice:264` is an active-folder carve-out and is unchanged).

**Governance**: ADR-only / **MEPD-1 EXCLUDE** — no new RULE-ID, no `VERSION` bump, no `methodology-changelog` entry. This extends ADR-104's existing op-gate; it mints no rule. Matches the flip-prep house style (slices 106/109/111/112).

## Consequences

- The op-gate protects the `<vault>` convention surface from day one of the rollout: an un-routed in-loop `<vault>/` write reds (`OP_UNROUTED → exit 2`) exactly as an `architecture/` one does. The write-safety invariant (R-32) survives the convention rollout intact, with **no gate-loosening** (the slice-112 B2 "downward floor re-pin" is superseded by "keep floors stable via seam-awareness").
- **The value EXTRACTOR moves in lockstep with the matcher (B2 — slice-113 `/critique`, dual-Critic-confirmed; load-bearing, NOT cosmetic).** `_classify_op` keys on the op's extracted SINK VALUE (`_ACTIVE_FOLDER_RE.search(sink)`, `_UNDECIDED_DISPOSITION_RE.search(sink)`), and `scan_op_file` extracts that value via a token regex (`_PATH_TOKEN_RE` today, which returns `None` at a `<vault>/` column → the value would silently collapse to bare `"<vault>/"` and every sub-regex `.search` would miss). So `scan_op_file` MUST extract with `_OP_SINK_TOKEN_RE` (the `<vault>/…`-capable token form) **in lockstep with** `_OP_SINK_RE` as the matcher — widening the matcher alone is vacuous. Both are required for the "sub-regexes are prefix-agnostic, no change needed" claim to hold. Non-vacuity is pinned by three new `<vault>/`-sink op-gate tests (a `<vault>/slices/slice-NNN/…` in-loop write → `OP_DEFERRED_TO_FLIP`; a `<vault>/slice-queue.md` → `OP_OUT_OF_SCOPE`; an un-routed in-loop `<vault>/risk-register.md` → `OP_UNROUTED`), since `test_vault_flip_op_gate.py` previously carried zero `<vault>/`-sink fixtures (a value-extractor miss would have passed the suite vacuously — AP-5).
- `_MATCH_RE` (inventory) and `_OP_SINK_RE` (op-gate) are now deliberately distinct; the module docstring + a code comment pin *why* they must not be re-merged (the inventory must drop converted literals; the op-gate must keep seeing them). A future maintainer who "unifies" them would silently re-break one of the two halves — a `/code-review`-visible trap, called out in the comments.
- The op-gate now recognizes a sink with no concrete vault root at all (`<vault>/…`) — correct for a location-agnostic gate, and the precondition for the physical flip to be a config-only move on the op-gate axis.
- When a `<diagnose-out>` seam is eventually minted (deferred — B5/ADR-105 class 7), `_OP_SINK_RE` gains a third alternative the same way; the pattern is established here.

## Reversibility

**cheap.** `_OP_SINK_RE` is a one-line regex; reverting to `_MATCH_RE`-only is a mechanical edit (it would re-introduce the blindness, so it won't be done, but nothing is locked). No data / schema / contract lock-in; the op-gate JSON shape and exit codes are unchanged; the floors are unchanged. The only coupled artifacts are the 3 re-hashed `_OP_ALLOWLIST` entries, themselves re-derivable from the corpus.
