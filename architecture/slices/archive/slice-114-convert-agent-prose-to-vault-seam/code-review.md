# Code Review: Slice 114 convert-agent-prose-to-vault-seam

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-06-05
**Result**: FINDINGS (0 blockers, 0 majors, 2 minors — advisory in v1)

## Summary
A tight, correct prose-conversion + audit-constant re-pin slice. Every load-bearing claim was verified by executing the real classifier against a reconstructed post-edit corpus: the two carve-out value-hashes are correct `sha256` of the exact tokens the matcher extracts; the seam-note `architecture/` default genuinely classifies `doc-example` (un-backticked, op-verb-free); the 127/131 counts reproduce exactly; the re-pinned `_BASELINE_SHA256` matches the post-edit baseline byte-for-byte; the converted-file ratchet has zero regressions; the new drift test mirrors the existing one with valid imports. No blockers, no majors. Two minors about a residual self-sufficiency inconsistency the conversion made newly salient.

## Changed files (in-scope)
agents/code-review.md
agents/critic-calibrate.md
tools/vault_flip_prose_inventory.py
tests/methodology/test_critic_calibrate_agent_drift.py
architecture/slices/slice-114-convert-agent-prose-to-vault-seam/build-log.md

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)
None.

### Majors
None.

### Minors

#### m1: `agents/critic-calibrate.md` bare `critic-calibration-log.md` ("read it" line) left inconsistent with the now-converted `<vault>/critic-calibration-log.md`
- **Issue**: After this slice the converted `:22` (now `:26`) uses `<vault>/critic-calibration-log.md`, but the operational "read it" instruction (committed `:76`, post-note `:80`) referenced the same artifact as a bare relative filename a subagent (which does not inherit CLAUDE.md) cannot resolve — a self-sufficiency wart the conversion itself made salient (Wiegers: one canonical reference form within a self-contained prompt). Zero inventory impact (a bare filename never matched the matcher; `<vault>/` does not match either).
- **Builder disposition**: **ACCEPTED-FIXED** — converted the `:80` "read it" operational instruction to `<vault>/critic-calibration-log.md`. Re-forward-synced `critic-calibrate.md`; `--strict` re-confirmed unchanged (131; 127/0/4/0; baseline identical) and the drift + behavioral tests stay green. The two remaining bare mentions (`:109` proposal-output template label, `:154` effectiveness-section description) are descriptive output-format references, NOT path-resolution instructions — left as-is, consistent with the inventory's own bare-filename scope.

#### m2: confirm the docstring count-provenance reconciles the "+ the 2 doc-example" tail, not just the headline counts
- **Issue**: the docstring block (tool `:47-56`) updates the headline (130→127, 132→131) and the doc-example enumeration; the code-Critic asked to confirm the dependent "+ the 2 doc-example)" tail + "116 carve-outs" clause are reconciled.
- **Builder disposition**: **VERIFIED — already reconciled.** The docstring tail now reads "+ the 4 doc-example)" (tool `:56`) and "the 4 doc-example are the CLAUDE.md + 3 agent-note (critique / code-review / critic-calibrate)" (`:57`). The "116 carve-outs" figure sits in the slice-113 historical segment (unchanged — slice-114 converted shared-aggregate operational refs, not carve-outs, so 116 stays literally true). The lone remaining "+ the 2 doc-example stay" at the `EXPECTED_TOTAL` comment `:343` is the slice-113 historical-provenance line (accurate for that transition), with the slice-114 line (`doc-example 2→4`) appended directly after it. No stale LIVE count.

## Dimensions checked
- [x] **Unfounded assumptions** — none behaviorally. `sha256("architecture/**")` = `0a69ee77…` ✓ and `sha256("architecture/slices/slice-NNN-<name>/code-review.md")` = `46e2f7eb…` ✓, exactly the values the matcher extracts from the live carve-out lines; value-keyed so the +line-shift to :29/:237 is irrelevant (ratchet stays clean — confirmed).
- [x] **Missing edge cases** — none. Pure markdown conversion + constant re-pin; no new code branches. CRLF/LF handled by the shared CRLF→LF-normalizing comparator (EOL-DRIFT-1 / ADR-033). Line-shift safety (value/multiset-keyed, not line-keyed) confirmed real.
- [x] **Over-engineering** — none. Two frozenset appends + constant/docstring edits + one mirror test. `critic-calibrate.md` correctly gets NO `_CONVERTED_CARVEOUTS` entry (its sole survivor is `doc-example`, which the `klass == REWRITE_AT_FLIP` ratchet filter never reaches) — minimal correct set.
- [x] **Under-engineering** — none. Every AC has a delivering element; AC2/AC3/AC4 reproduced against the real classifier. RSAD-1: the slice's own re-pinned constants pass the tool's own `--strict` gate (executed, not asserted).
- [x] **Contract gaps** — none. The new test imports `REPO_ROOT` (real) + `assert_md_forward_synced` (real); signature matches the helper + mirrors `test_code_review_agent_drift.py:31` verbatim. No phantom imports.
- [x] **Security** — none. No authn/authz/input/secrets/injection surface. The converted `<vault>/.secrets-allowlist` is a documentation pointer, not a secret or a read path.
- [x] **Drift from vault** — none material. Per-file disposition matches design.md (full `agents/*.md` scan). MEPD-1 EXCLUDE correctly honored (inventory constants, not a methodology entry-pin bump). The `architecture/**` carve-out (operational-reference, prose mirror of the SKILL.md git `:(exclude)` pathspec) is a defensible stay-concrete.
- [x] **Web-known issues** — none applicable. No external API/SDK/framework; methodology-internal markdown + in-house audit constants (stdlib `hashlib`/`re` only). WebSearch available but no external code choice to check.
- [x] **Cross-cutting conformance** — none blocking. APED-1: no parse-rule change (data-constant re-pin only); nonetheless executed the unchanged classifier → 127/4/131 + baseline `44b22876…` + zero converted-file regressions. Algorithm-path-conformance: the seam-note `architecture/` line reaches ruleset branch 5 (`doc-example`) — not in-code, no op-verb — exactly as required.
