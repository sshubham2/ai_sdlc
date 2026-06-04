---
id: ADR-105
title: Operational pipeline prose references the vault root via a flip-neutral `<vault>` placeholder
date: 2026-06-04
slice: slice-112-make-prose-vault-location-agnostic
reversibility: cheap
status: accepted
---

# ADR-105: Operational pipeline prose references the vault root via a flip-neutral `<vault>` placeholder

## Context

The external-shared-vault flip (R-32 / M4) relocates `architecture/` + `diagnose-out/` to a shared external store. Every code surface is already flip-ready (slices 100/102/106/098/109/110). The **prose surface** is the last holdout — 313 hardcoded operational `architecture/`/`diagnose-out/` literals across `skills/**/SKILL.md`, `agents/*.md`, and `CLAUDE.md`, inventoried by slice-107 but never rewritten. slice-107/R-32 originally bundled this rewrite into the flip; the user re-scoped (slice-112 `/slice` gate) to a location-**agnostic** pre-flip pass — the prose analog of slice-110's `make-pipeline-vault-location-agnostic` — so the flip shrinks to a config-only move.

A naive "rewrite the literals to `~/.aisdlc/<project>/`" is rejected: the vault is still physically at `architecture/`, so concrete-new-path prose would be wrong today. The convention must be **flip-neutral** — correct both pre- and post-flip.

This ADR was hardened by a dual-Critic pass (slice-112 `/critique` + `/critique-review`, both grounded against live code). Two findings reshaped it: the placeholder is **not** flip-neutral for composed `<wt_path>/architecture/…` paths (they need a structural prefix-drop, not a token sub — B1), and a Critic SUBAGENT does **not** inherit the project `CLAUDE.md`, so a converted `agents/*.md` can't resolve `<vault>` unless it carries the rule itself (M-add-1). Both are reflected in the Decision + the carve-out taxonomy below.

## Options considered

1. **`<vault>/` placeholder + resolution rule stated once in CLAUDE.md, Claude substitutes (CHOSEN).** Fits the existing `<...>` prose-placeholder idiom (`<wt_path>`, `<main>`, `<default>`, `slice-NNN-<name>`); pure prose edit; default-resolves to `architecture/` ⇒ zero pre-flip behaviour change. Cons: ~24 fenced shell commands + the code-review git-pathspec need Claude to substitute before running (the LLM-resolution tax, the same discipline used for every other `<placeholder>`); a literal `<vault>` is not human copy-paste-runnable (mitigated: these are Claude-executed skill commands; a bare `<vault>` fails loud).
2. **`$AI_SDLC_VAULT_ROOT/` shell-style variable everywhere.** Not exported in the shell by default → resolves empty unless a layer sets it; reads awkwardly in 224 inline refs; doesn't match the `<...>` idiom.
3. **Hybrid: `<vault>/` for refs, commands rely on each tool's internal `VAULT_ROOT` default (omit the path arg).** Requires tool changes across `tools/*.py`; expands beyond the pilot.

## Decision

Operational pipeline prose references the vault root via the flip-neutral placeholder **`<vault>/`**. Its resolution rule — `<vault>` = the vault root, `architecture/` by default, or `$AI_SDLC_VAULT_ROOT` / the git-common-dir config if set (mirroring `tools/_vault_paths.py::_resolve_vault_root`, ADR-065 + ADR-085) — is stated **once** in `CLAUDE.md`. Claude substitutes it when reading a vault file or running a command, as it already does for every other `<placeholder>`.

**The `<diagnose-out>` token is NOT minted** (B5): `tools/_vault_paths.py` has no `diagnose-out` seam, so its post-flip resolution is undefined. `diagnose-out/` literals stay **concrete** (carve-out class 7) until a `<diagnose-out>` seam is defined (a later slice / the flip).

**Resolver-context scope (load-bearing — M-add-1).** The convention applies only where the *resolver* (the `<vault>` rule) is in context:
- **CLAUDE.md + `skills/**/SKILL.md` prose** — read by the MAIN agent, which carries the project `CLAUDE.md`. ✓ convention applies.
- **`agents/*.md`** — a subagent's *system prompt*; a Task-spawned subagent does **NOT** inherit the project `CLAUDE.md`. A converted agent applies the convention ONLY IF it **embeds a self-contained `<vault>` resolution note** in its own prompt (the slice-112 pilot does this for `agents/critique.md`). An agent that does not embed the note keeps its literals concrete (a carve-out).

**Carve-out taxonomy (stay concrete `architecture/`; NEVER token-converted; the gate keys on `rewrite-at-flip` only, so these classes are never flagged):**
1. **User-facing root docs** — `INSTALL.md` + `README.md` (read by a human before the pipeline/CLAUDE.md/vault exist; descriptive refs to the concrete default).
2. **Definitional literals** — the resolution rule's own `architecture/` default. Resolved as **plain prose (no backticks) → `doc-example`** (M2 + M-add-2), NOT a `_DISPOSITION` 5-tuple entry: the disposition key embeds the line text (`disposition_key` = `(path, norm_line, fenced, ordinal, col)`), so a future reword of the rule line would silently drop the exemption and re-red the gate. Plain-prose `doc-example` is durable against rewording.
3. **Historical anchors** — `[[ADR-NNN]]`, changelog version refs, `archive/slice-*` Glob-discoverability anchors (slice-107 carve-out, preserved).
4. **Worktree-composed `<wt_path>/architecture/…` paths** (B1) — `<vault>` resolves to the FULL root (post-flip an ABSOLUTE external path, ADR-085), so `<wt_path>/<vault>/…` is malformed post-flip. These need a structural **prefix-drop** at flip (`<wt_path>/architecture/…` → `<vault>/…`), which a token sub cannot encode. Stay concrete; flagged `rewrite-at-flip` (structural-rewrite class) for the flip slice.
5. **Per-slice ACTIVE-folder refs** — `architecture/slices/slice-NNN-…` (NOT `archive/`). Whether per-slice active folders live worktree-local or in the external store post-flip is the **R-32.a** decision the flip slice owns; converting them pre-decides it. Stay concrete.
6. **`slice-queue.md`** — the main-tree coordination ledger ADR-090 pins to the default branch; its tracked-vs-external fate is the flip slice's call (slice-111 `_UNDECIDED_DISPOSITION`). Stay concrete (M1).
7. **`diagnose-out/…`** — no seam yet (B5). Stay concrete until a `<diagnose-out>` seam exists.

**Enforcement** (M3): `tools/vault_flip_prose_inventory.py` gains a `_CONVERTED_FILES` frozenset (**forward-slash repo-relative paths**, matching `Occurrence.path`) + a `--strict` check (`converted_file_regressions`) that fails closed (exit 2) on any `rewrite-at-flip` literal in a converted file **that is not a sanctioned carve-out**. The check is a **one-way ratchet INDEPENDENT of the re-pinnable `_BASELINE_SHA256`** — it reds even if an actor re-pins the baseline to "cover" a regression; proven non-vacuous by a mutation that injects a literal into a converted file AND re-pins the baseline, asserting exit 2 survives.

**Carve-out exemption on the ratchet (AS-BUILT, build-log 2026-06-04).** An OPERATIONAL carve-out (an in-code literal of classes 5/6/7 that legitimately STAYS concrete inside a converted file — per-slice active-folder, `slice-queue.md`, `diagnose-out/`) classifies `rewrite-at-flip` and would otherwise trip the ratchet. It is exempted via a hash-keyed `_CONVERTED_CARVEOUTS` `(path, sha256(value))` allowlist — hash-keyed (NOT inlined slashed literals) so this `tools/*.py` source carries no `architecture/` literal `vault_flip_readiness_audit` would flag (slice-107 AC5 disjointness, same SHA-256 precedent), and value-keyed so it is durable against rewording of the *surrounding* prose (keyed on the literal value, not the line text — more robust than a `_DISPOSITION` line-key, the M-add-2 concern). The **definitional** literal (class 2) is plain-prose `doc-example` (never `rewrite-at-flip`), so it never enters the ratchet — no carve-out entry needed. **Scope (code-review m1)**: the plain-prose definitional exemption is durable against *value* rewording but remains sensitive to op-verb/backtick *formatting* on its physical line — a future reword that adds an `_OP_VERB` or wraps the default in backticks flips its line to `rewrite-at-flip`. This fails **CLOSED** (the AC3 ratchet test `test_pilot_files_zero_rewrite_at_flip_after_conversion` reds — it can never let a real hardcode through), but keep the resolution-rule default literal on an op-verb-free, un-fenced line (the AP-3 build-time recalibration that authored it).

**Re-pin fan-out set** (B4 / FBCD-1 sub-mode (c) / AP-10 — all move together on any conversion): `_BASELINE_SHA256`, `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]`, `EXPECTED_TOTAL`, AND `architecture/shippability.md` rows 113 + 117 (both hard-state "313"). The exact new total is **APED-1-derived** via `--json` against the converted corpus, not estimated.

**Governance**: ADR-only / **MEPD-1 EXCLUDE** (no RULE-ID / no VERSION bump / no changelog entry), matching the recent flip-prep house style (slices 106/109/111). Enforcement is suite-test + shippability pinned, not a new build-slice gate.

**Pilot**: `CLAUDE.md` + `agents/critique.md` (the latter with an embedded self-sufficient `<vault>` note + its two entangled refs — `:125` slice-queue, `:260` active-folder — carved out). Skill conversion (`slice`/`reflect`/the bulk ~17) is a **follow-on** that owns the op-gate floor re-pin + allowlist re-hash (B2) and the skill instances of carve-out classes 4–6.

## Consequences

- The M4 flip no longer carries a 313-site prose rewrite once the full operational prose surface is converted (this pilot + follow-ons) — the flip becomes `git mv` + the `VAULT_ROOT` default flip + `git rm --cached`, with the convention-domain prose already correct and the carve-out classes 4–7 handled by the flip slice (which owns their undecided dispositions).
- A converted file can never silently regress to a hardcoded operational `architecture/` (the one-way ratchet).
- A permanent small per-run substitution step on the convention surface (rides the existing `<placeholder>`-resolution discipline). For agents, the embedded self-sufficient note carries the resolver into the subagent context.
- Guarded converted files (`agents/critique.md` CAD-1) are forward-synced to `~/.claude/` in the same slice (byte-identical convert → CAD-1 EOL-agnostic equality stays green).
- The carve-out taxonomy (classes 1–7) is the **map** the skill follow-on + the flip slice consume; the pilot *proves* classes 2/4/5/6 live (CLAUDE.md definitional + agent active-folder/slice-queue carve-outs), not just documents them.
- Token spelling locked at the pilot stage, while breadth is small.

## Reversibility

**cheap.** Reversing or re-spelling the token is a mechanical find-replace across converted files + a forward-sync — no data/contract/schema lock-in; the default still resolves to `architecture/` throughout; the enforcement gate keys on the `rewrite-at-flip` class, not the token text. The only scaling cost is breadth — which is why the token is locked at the pilot before the follow-on widens it.
