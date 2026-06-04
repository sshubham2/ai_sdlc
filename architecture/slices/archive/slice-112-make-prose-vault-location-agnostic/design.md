# Design: Slice 112 make-prose-vault-location-agnostic

**Date**: 2026-06-04
**Mode**: Standard
**Revised**: 2026-06-04 post dual-Critic TRI-1 (pilot reduced to CLAUDE.md + self-sufficient `agents/critique.md`; `<diagnose-out>` scoped out; carve-out taxonomy added; enforcement ratchet hardened). See critique.md / critique-review.md.

## What's new

- **The `<vault>` prose-seam convention** ([[decisions/ADR-105]]): the placeholder `<vault>/` names the vault root in operational pipeline prose; resolution rule stated once in `CLAUDE.md` (and embedded self-contained in any converted `agents/*.md`, since a subagent does not inherit CLAUDE.md — M-add-1); Claude substitutes (to `architecture/` default) when reading/running. Flip-neutral. **`<diagnose-out>` is NOT minted** (no seam — B5).
- **A converted-file one-way enforcement ratchet** in `tools/vault_flip_prose_inventory.py`: a `_CONVERTED_FILES` frozenset (forward-slash relpaths) + a `--strict` check failing closed (exit 2) on any `rewrite-at-flip` literal in a converted file, **independent of the re-pinnable baseline** (M3).
- **Pilot conversion**: `CLAUDE.md` + `agents/critique.md` (self-sufficient note + carve-outs), forward-synced (CAD-1).
- **New test** `tests/methodology/test_prose_vault_seam_convention.py` + extension of `tests/methodology/test_vault_flip_prose_inventory.py` (the ratchet + its mutation-proof).

## What's reused

- `tools/vault_flip_prose_inventory.py` (slice-107) — extended, not replaced: its `_MATCH_RE`, fence/inline-code anchoring, `_DISPOSITION`, `_BASELINE_SHA256`/`_CLASS_COUNT_FLOOR`/`EXPECTED_TOTAL` pins, CLI all carry forward. [[slice-107-inventory-vault-flip-prose-surface]]
- The `VAULT_ROOT` seam + 3-tier resolution in `tools/_vault_paths.py` (ADR-065 + ADR-085) — the rule mirrors it. The convention's analog for tests is [[slice-110-make-pipeline-vault-location-agnostic]]; for production code [[slice-106-route-project-frame-synth-via-vault-root]].
- The existing `<...>` prose-placeholder idiom in `skills/**/SKILL.md` — `<vault>` joins it.
- The MEPD-1-EXCLUDE flip-prep house style (suite-test + shippability enforced, no RULE-ID/VERSION bump) of slices 106/109/111.
- CAD-1 forward-sync + drift (`tools/critique_agent_drift_audit.py` — whole-file SHA-256, EOL-agnostic).

## Components touched

### The `<vault>` convention (documented, not a module)
- **Responsibility**: a flip-neutral way for operational prose to name the vault root, shrinking the M4 flip to a config-only move.
- **Lives at**: the rule in `CLAUDE.md` (new short subsection under `## Vault discipline`); the embedded self-sufficient copy in `agents/critique.md`; the decision + carve-out taxonomy in `ADR-105`.

### `tools/vault_flip_prose_inventory.py` (modified)
- **`_CONVERTED_FILES: frozenset[str]`** — repo-relative **forward-slash** paths (matching `Occurrence.path`, which is `.replace("\\","/")`-normalized at `:272`); this slice: `{"CLAUDE.md", "agents/critique.md"}`. A `\`-form would silently never match → a load-bearing negative test pins the separator convention (M3).
- **`_CONVERTED_CARVEOUTS: frozenset[tuple[str, str]]`** ⚠ **AS-BUILT (build-log 2026-06-04; design refinement, user-approved at plan-mode)** — the design under-specified how an OPERATIONAL carve-out (in-code, classifies `rewrite-at-flip`) that legitimately remains in a converted file is exempted from the ratchet. As-built: a hash-keyed `(path, sha256(value))` allowlist (the 4 operational carve-outs — `diagnose-out/backlog.md`, `diagnose-out/`, `architecture/slice-queue.md`, `architecture/slices/slice-NNN-<name>/critique.md`). Hash-keyed (NOT inlined slashed literals) so this `tools/*.py` source carries no `architecture/` literal `vault_flip_readiness_audit` would flag (slice-107 AC5 disjointness; same SHA-256 precedent as `_BASELINE_SHA256` + slice-111's `_OP_ALLOWLIST`). Value-keyed → robust to rewording (satisfies M-add-2's durability concern MORE than a `_DISPOSITION` line-key). The **definitional** literal (class 2) is plain-prose `doc-example` per M2/M-add-2 (NOT in this allowlist — it is not `rewrite-at-flip`).
- **`--strict` ratchet** (`converted_file_regressions(result)`): `[o for o in occurrences if o.path in _CONVERTED_FILES and o.klass == REWRITE_AT_FLIP and _carveout_key(o.path, o.value) not in _CONVERTED_CARVEOUTS]`; non-empty → exit 2 with a distinct `CONVERTED-FILE REGRESSED: <path>:<line>:<col>` message. **INDEPENDENT of `_BASELINE_SHA256`** (M3): the existing baseline-drift gate (`:329`) also trips on any multiset change, so the ratchet's distinct value is catching a converted-file regression EVEN IF the actor re-pins the baseline to match. The mutation-proof (`test_ratchet_independent_of_repinned_baseline`) injects a literal into a converted file AND re-pins the baseline, asserting exit 2 still fires.
- ⚠ **AS-BUILT build-time recalibration (AP-3)**: executing the gate against the real corpus (not design-time reasoning) caught two prose-classification bugs in the new convention text — a "historical anchors" marker beside an in-code `diagnose-out/` literal routed it to `needs-human` (exit 2), and a plain-prose `architecture/` default sharing a physical line with "read/write" op-verbs routed it to `rewrite-at-flip`. Fixed by re-wording so each definitional literal sits on a line free of anchor-markers + op-verbs → `doc-example`. (The classifier is line-anchored; the new prose had to be authored around it.)
- **Re-pin fan-out set** (B4 / FBCD-1 (c) / AP-10 — move together): `_BASELINE_SHA256`, `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]`, `EXPECTED_TOTAL`, `architecture/shippability.md` row 113, `architecture/shippability.md` row 117. The exact post-conversion total is **APED-1-derived** via `--json` at build (NOT estimated). The op-gate floors are **untouched** (CLAUDE.md + agents are not op-gate-scanned — `_skill_of` returns None at `:473`, verified).

### `CLAUDE.md` (modified)
- New resolution-rule subsection (the `architecture/` default stated as **plain prose, no backticks → `doc-example`** so the gate never flags the definitional literal — M2 + M-add-2; NOT a `_DISPOSITION` line-key entry).
- Its operational `architecture/` refs → `<vault>/`. **Carve-outs (stay concrete)**: the definitional default (above); the `diagnose-out/backlog.md` ref at `:43` (B5 — `<diagnose-out>` not minted); any `slice-queue.md` / active-folder ref (classes 5/6) if present. Exact convertible-vs-carve-out split APED-1-derived at build.

### `agents/critique.md` (modified — CAD-1 guarded)
- Add a one-line **self-sufficient `<vault>` resolution note** near the top (so the Critic subagent, which lacks CLAUDE.md, can resolve the token — M-add-1). Its `architecture/` default in that note is plain-prose `doc-example` (M-add-2).
- Convert the vault-internal file refs (`:42`/`:160` `critic-calibration-log.md`, `:186`/`:188`/`:190`/`:203` `shippability.md`, `:256` `triage.md`) → `<vault>/…`. **Carve-outs (stay concrete)**: `:125` `architecture/slice-queue.md` (class 6 — undecided ledger, M1) and `:260` `architecture/slices/slice-NNN-<name>/critique.md` (class 5 — per-slice active-folder, R-32.a). Exact split APED-1-derived.
- **Forward-sync** to `~/.claude/agents/critique.md` (byte-identical convert → CAD-1 EOL-agnostic equality stays green); m1 — note the conversion makes the Critic self-resolve its own read/write paths via the embedded note.

## Contracts added or changed

### The `<vault>` token (convention contract)
- **Defined in**: `CLAUDE.md` + the embedded agent note + `ADR-105`. Resolution mirrors `_vault_paths._resolve_vault_root`; default → `architecture/` ⇒ no pre-flip behaviour change.
- **Scope**: operational prose where the resolver is in context — `CLAUDE.md` + `skills/**/SKILL.md` (main agent) + a self-sufficient `agents/*.md`. Carve-out taxonomy = ADR-105 classes 1–7 (INSTALL/README; definitional; historical anchors; worktree-composed paths; per-slice active-folder; slice-queue.md; diagnose-out/). The gate keys on `rewrite-at-flip` only.

### Enforcement-gate exit contract (extended)
- **Defined in code at**: `tools/vault_flip_prose_inventory.py::main`.
- **Exit codes**: 0 clean · 2 (needs-human OR `--strict` baseline-drift OR count-floor-shrink OR **new: converted-file `rewrite-at-flip` regression**) · 1 usage.

## Data model deltas

None. The tool's pinned constants change: `_CONVERTED_FILES` (new), `_BASELINE_SHA256` / `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]` / `EXPECTED_TOTAL` (re-pinned downward against the converted corpus), shippability rows 113/117 (narrative re-pin). The definitional literals are plain-prose `doc-example` (no `_DISPOSITION` entry). All exact values APED-1-derived at build.

## Wiring matrix

No new consumed module (extends a tool, edits prose, adds an ADR + a test file). Zero-row ⇒ clean per WIRE-1.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)
- [[ADR-105]] — operational prose references the vault root via the flip-neutral `<vault>` placeholder; resolver-context scope (CLAUDE.md + SKILL.md + self-sufficient agents); 7-class carve-out taxonomy; `<diagnose-out>` not minted; ADR-only / MEPD-1 EXCLUDE — reversibility: **cheap**.

## Authorization model for this slice
No authorization surface (methodology prose + a read-only audit-tool extension + tests; no runtime/network/user auth).

## Error model for this slice
The only error surface is the gate's exit codes (above). The converted-file regression is the new fail-closed condition (R-7 silent-disable class), proven non-vacuous by mutation targeting ratchet-independence (AP-5). No silent-disable path: the gate runs in the methodology suite (VAL-1 at `/validate-slice` + the build Step-6 full-suite) — the same suite-test + shippability enforcement slice-107/111 use; NOT a new build-slice RULE-ID gate.

## Deferred to the skill-conversion follow-on (TRI-1 dispositions)
- **B1** (worktree-composed `<wt_path>/architecture/…` paths in `slice/SKILL.md:249,264,267,268`), **B2** (op-gate floor re-pin + `_OP_ALLOWLIST` re-hash — the follow-on converts op-gate-scanned skills and OWNS this deliberate gate-loosening per AP-12), **B3** (`slice/SKILL.md:73` `diagnose-out/backlog.md` BCR-1 anchor — the follow-on repoints `test_bcr_1_backlog_round_trip.py:108,186` in the SAME slice per AP-13, OR carves it out), **M1** (`slice-queue.md` refs in `slice/SKILL.md:250,430,475`). All four are confined to the skill files this pilot does not touch; their carve-out CLASSES (4/5/6) are proven live in this pilot via the agent/CLAUDE.md carve-outs.
