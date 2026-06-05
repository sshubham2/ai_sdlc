# Design: Slice 114 convert-agent-prose-to-vault-seam

**Date**: 2026-06-04
**Mode**: Standard

## What's new

- A self-sufficient ADR-105 `<vault>/` resolver note (the slice-112 pilot's 3-line block from `agents/critique.md:10-12`, verbatim shape) embedded in **`agents/code-review.md`** and **`agents/critic-calibrate.md`** — the two agent files that carry genuinely *convertible* vault-content refs.
- **3 operational vault-content reads** rewritten from `architecture/…` to `<vault>/…`:
  - `agents/code-review.md:44` `architecture/critic-calibration-log.md` → `<vault>/critic-calibration-log.md`
  - `agents/code-review.md:119` `architecture/.secrets-allowlist` → `<vault>/.secrets-allowlist`
  - `agents/critic-calibrate.md:22` `architecture/critic-calibration-log.md` → `<vault>/critic-calibration-log.md`
- Inventory re-pin in `tools/vault_flip_prose_inventory.py`: `_CONVERTED_FILES` += the 2 agents; `_CONVERTED_CARVEOUTS` += the 2 `code-review.md` operational carve-outs (hash-keyed); `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]` 130→**127**; `EXPECTED_TOTAL` 132→**131**; `_BASELINE_SHA256` re-pinned (APED-1-derived, not estimated); docstring provenance narrative extended with a slice-114 line.
- Test-expectation updates in `tests/methodology/test_vault_flip_prose_inventory.py` (any count/baseline/converted-files/ratchet assertions that pin 132/130/the converted set).
- **[M1-fix] NEW drift test** `tests/methodology/test_critic_calibrate_agent_drift.py` (verbatim mirror of `test_code_review_agent_drift.py`, path → `agents/critic-calibrate.md`) — brings `critic-calibrate.md` under the CRSI-1/CAD-1 content-equality family so its converted runtime prompt cannot silently drift from the installed copy. Test-only family extension → MEPD-1 EXCLUDE (OSDG-1/CRSI-1 open-set precedent).
- **Forward-sync** `agents/code-review.md` + `agents/critic-calibrate.md` to `~/.claude/agents/` — keeps **both** `test_code_review_agent_drift.py` AND the new `test_critic_calibrate_agent_drift.py` green (each edited agent is now drift-guarded; no asymmetry).
- `architecture/shippability.md`: LIVE-total fan-out 132→131 / 130→127 where rows assert the *live* count, plus a new slice-114 catalog row.

## What's reused

- [[decisions/ADR-105]] — the `<vault>/` seam convention, the 7-class carve-out taxonomy, the resolver-context scope rule (M-add-1: a subagent needs its OWN embedded note), and the one-way ratchet design. **No new ADR** — this slice applies ADR-105, decides nothing new.
- [[decisions/ADR-033]] — EOL-agnostic content-equality (CRSI-1 / CAD-1 family), via `tests/skill_drift_equality.py::assert_md_forward_synced`.
- The pilot `agents/critique.md:10-12` seam-note block — the verbatim template for the two new notes.
- `tools/vault_flip_prose_inventory.py` ratchet machinery (`_CONVERTED_FILES`, `_CONVERTED_CARVEOUTS`, `_carveout_key`, `--strict`).
- Prior slices: [[slice-112-make-prose-vault-location-agnostic]] (minted ADR-105 + the agent pilot), [[slice-113-bulk-convert-remaining-skills-to-vault-seam]] (skill bulk; deferred this surface; established the value-keyed carve-out pattern + the un-ratcheted-on-collision precedent).

## Per-file disposition (the load-bearing artifact)

Authoritative source = `vault_flip_prose_inventory --json` per-occurrence `klass`. Every occurrence below is `rewrite-at-flip` unless noted.

| File | Occ (pre-edit) | Value | Disposition | Carve-out class / rationale |
|------|----------------|-------|-------------|------------------------------|
| `agents/code-review.md` | :44 | `architecture/critic-calibration-log.md` | **CONVERT** → `<vault>/` | vault-content read (calibration evidence) |
| `agents/code-review.md` | :119 | `architecture/.secrets-allowlist` | **CONVERT** → `<vault>/` | vault-content read (secrets check) |
| `agents/code-review.md` | :25 | `architecture/**` | **CARVE-OUT** | **prose mirror** of the SKILL.md `:(exclude)architecture/...` diff-scope pathspecs (`skills/code-review/SKILL.md:47-85`). Live classifier reports `operational-reference`, **NOT** git-pathspec — `_PATHSPEC_RE` is line-local (`tools/vault_flip_prose_inventory.py:130`) and does not fire on the prose description (slice-113 Discovered #2). Stays concrete so the agent prose matches the concrete pathspecs; token-sub would diverge them post-flip (the slice-113 `/code-review` B1 / M-add-2 lesson) [M2-fix] |
| `agents/code-review.md` | :233 | `architecture/slices/slice-NNN-<name>/code-review.md` | **CARVE-OUT** | class **5-active-folder** (R-32.a) — matches the pilot `critique.md:264` treatment exactly |
| `agents/critic-calibrate.md` | :22 | `architecture/critic-calibration-log.md` | **CONVERT** → `<vault>/` | vault-content read |
| `agents/critique-review.md` | :78 | `architecture/slices/slice-NNN-<name>/critique-review.md` | **NO-OP CARVE-OUT** | class **5-active-folder** (R-32.a) — ADR-105 forbids conversion (pre-decides R-32.a); file stays note-less per M-add-1 |
| `agents/diagnose-narrator.md` | :19 | `diagnose-out/` | **NO-OP CARVE-OUT** | class **7-diagnose-out** — no `<diagnose-out>` seam minted (ADR-105 B5); stays concrete; file stays note-less |

Net: **3 conversions, 4 carve-outs.** Touched files: `code-review.md` (note + 2 convert + 2 carve-out, ratcheted), `critic-calibrate.md` (note + 1 convert, ratcheted). **Untouched: `critique-review.md`, `diagnose-narrator.md`** (their only vault refs are ADR-105-mandated-concrete classes 5/7; per M-add-1 a note-less agent legitimately keeps concrete literals — the flip slice drains them with all other carve-outs).

### Scope refinement vs mission-brief (TPHD-1 sub-mode a / AP-17 — back-propagated)

slice-113's reflection said "4 agent files … carry convertible refs." Precise per-occurrence classification shows only **2** files carry genuinely-convertible refs; the other two carry only carve-out-class refs ADR-105 mandates stay concrete. The mission brief (AC1/AC2/Intent) has been updated in lockstep: 2 files converted + note, 2 files documented no-op carve-outs. This is **not** under-delivery — converting `:78`/`:19` would violate ADR-105 (pre-decide R-32.a; use a non-existent diagnose-out seam).

## Ratchet safety: why `agents/code-review.md` IS safe to ratchet (though the *skill* `code-review/SKILL.md` was NOT)

`skills/code-review/SKILL.md` was deliberately excluded from `_CONVERTED_FILES` (`vault_flip_prose_inventory.py:348-355`) because 5 of its git-pathspec carve-out *values* equalled converted shared-aggregate values in the same file → a value-keyed carve-out would also whitelist a real same-value regression (EXPLOITABLE collision).

`agents/code-review.md` has **no such collision**: its 2 carve-out values (`architecture/**`, `architecture/slices/slice-NNN-<name>/code-review.md`) are distinct from each other and from its 2 converted refs — which lose the `architecture/` prefix entirely (`→ <vault>/…`), so post-edit nothing in the file shares a value with a carve-out key. Each carve-out value appears exactly once (inventory found 4 distinct occurrences). Therefore both files are **safely ratcheted** with full one-way protection of the converted refs. `critic-calibrate.md` has zero carve-outs (its sole ref is converted) → cleanest case.

**[M3-fix] Lockstep requirement — adding `agents/code-review.md` to `_CONVERTED_FILES` REQUIRES adding BOTH its surviving `rewrite-at-flip` carve-out values to `_CONVERTED_CARVEOUTS` or `--strict` exits 2** (`converted_file_regressions()`, `tools/vault_flip_prose_inventory.py:460-471`, flags every non-carve-out `rewrite-at-flip` in a converted file):
- `_carveout_key('agents/code-review.md', 'architecture/**')` (the :25 pathspec mirror)
- `_carveout_key('agents/code-review.md', 'architecture/slices/slice-NNN-<name>/code-review.md')` (the :233 active-folder)

Both hash keys are **APED-1-derived at build** (run the tool to emit the exact `sha256(value)`), never hand-estimated. `critic-calibrate.md` needs **zero** `_CONVERTED_CARVEOUTS` entries (its sole ref is converted). Confirm both at the mid-slice smoke gate (`--strict` exit 0).

## Enforcement re-pin (AP-10 / FBCD-1 sub-mode c fan-out — all move together)

- `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]`: 130 → **127** (−3 converted: code-review :44/:119, critic-calibrate :22).
- `EXPECTED_TOTAL`: 132 → **131** (−3 rewrite-at-flip converted; +2 plain-prose definitional `doc-example` from the two new notes → `doc-example` 2→4).
- `_CLASS_COUNT_FLOOR[DOC_EXAMPLE]`: **leave at 0** (floor = minimum; follows slice-112/113 precedent). **[m1-note]** Do NOT raise it to 4 — the definitional-line drift direction (a future edit backticks/op-verbs the `architecture/` default → demoted to `rewrite-at-flip`, doc-example drops) fails closed via `_BASELINE_SHA256` drift + the converted-file ratchet (ADR-105 line 47 "scope (code-review m1)"), NOT the floor; a floor of 4 would instead red a legitimate future skill conversion that lowers doc-example.
- `_BASELINE_SHA256`: re-pin from the **live `--json` hash** against the converted corpus (APED-1 — derive, never estimate the 131).
- **[m2-fix] Verified LIVE-count sites** (AP-10 grep, current row numbering — replaces the stale "rows 113/117" ADR-105-era reference): `tools/vault_flip_prose_inventory.py` lines ~21/47/48/51 (docstring narrative) + `:306/:308` (`_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]`) + `:332/:334` (`EXPECTED_TOTAL`); and `architecture/shippability.md` rows **122** (slice-107: "all **132**", distribution "130/0/2/0" — LIVE) + the regression-sentinel clauses on rows **126/127/128** ("OR the 132/130 re-pin reverts"). Per-row judgment: a forward-looking sentinel updates to 131/127; a phrase reading "→ 132 after slice-113 / ADR-106" is a **historical anchor** and stays. The slice-113 archive milestone/build-log/reflection + archive `_index.md` are historical provenance — **DO NOT touch**. Add a new slice-114 catalog row. Re-grep `\b(132|130)\b` repo-wide before finishing to confirm no live site missed.
- Line-shift safety: inserting the 3-line note shifts subsequent line numbers in `code-review.md`, but `_CONVERTED_CARVEOUTS` and `_BASELINE_SHA256` are **value/multiset-keyed, not line-keyed** (ADR-105's deliberate choice), and neither agent appears in `_RESIDUAL` (which is the only line-keyed structure). So line shifts are inert to enforcement.

## Wiring matrix

This slice introduces **no new modules** — it edits existing agent prose, existing inventory constants, existing tests, and the shippability catalog. Zero-row matrix = clean per WIRE-1.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

None. Rides [[decisions/ADR-105]]. **Governance: MEPD-1 EXCLUDE** — no new RULE-ID, no `methodology-changelog.md` entry, no VERSION bump. The load-bearing precedent for the M1 test-only drift-guard add is **slice-096** ("adding a member to the already open-ended set is the rule operating within its documented scope" — CLAUDE.md:42), with the prose-conversion half riding slice-113's flip-prep house style (106/109/111). The MEPD-1 EXCLUDE *call* is confirmed at `/reflect`; recorded here as the design intent.

**[m-add-1 fix] CAD-1 prose-enumeration deferral (deliberate).** Adding `test_critic_calibrate_agent_drift.py` makes `critic-calibrate.md` the **second** CAD-1-guarded agent the root `CLAUDE.md:39` CAD-1 bullet does NOT enumerate (the first being `code-review.md`, drift-guarded since slice-060 / CRSI-1 but never enumerated). This slice does **not** update the CLAUDE.md CAD-1 enumeration prose — the *tests* are the authoritative guarded-set (they gate regardless of the bullet), and a CLAUDE.md enumeration sweep (`critique` + `code-review` + `critic-calibrate`) is a separate **courtesy-parity cleanup**, explicitly out of scope here per the slice-096 precedent ("`pulse` + `code-review` have drift tests but are not yet enumerated … a separate courtesy-parity cleanup"). Recorded so a future maintainer does not mistake the CLAUDE.md CAD-1 bullet for the authoritative guarded-set.

## Authorization model for this slice

N/A. The four agents are read-only Critic/narrator subagents (`tools: Read, Glob, Grep, …`; "does not modify code or vault files"). This slice changes only prose + enforcement metadata — no auth surface, no new privileged action.

## Error model for this slice

N/A. No new runtime code path, no new error codes. The only failure modes are gate-level: a dropped/malformed seam note (subagent can't resolve `<vault>/` — M-add-1), a wrongly-converted carve-out (ratchet `--strict` exit 2), a forgotten forward-sync (now caught for **both** edited agents — `test_code_review_agent_drift.py` AND the new `test_critic_calibrate_agent_drift.py` [M1-fix], closing the prior asymmetry), or a stale count literal (`test_vault_flip_prose_inventory.py` red). All fail closed.

## Must-not-defer (carried from mission brief, design-sharpened)

- Seam note must be the **self-sufficient** pilot shape (subagent ≠ CLAUDE.md inheritor) — and its `architecture/` default MUST stay **plain prose, un-backticked, op-verb-free** so it classifies `doc-example`, not `rewrite-at-flip` (ADR-105 "scope (code-review m1)").
- Carve-out determination is **per-literal, value-keyed** — never blanket-convert; honor the pathspec-mirror distinction (L25).
- **Forward-sync** both edited agents to `~/.claude/agents/` (CRSI-1 mandatory for code-review; runtime-correctness for critic-calibrate).
- Do **not** edit `agents/critique.md` (already converted; CAD-1).
- **AP-3**: after editing, RUN `vault_flip_prose_inventory --json` + `--strict` against the real corpus to confirm the exact 131/127 and a green ratchet — design-time math is not proof.
- **AP-5 (new drift test non-vacuity)**: author `test_critic_calibrate_agent_drift.py` with a genuine FAIL→PASS contrast — before forward-syncing, prove it REDS on a mutated/absent installed copy (the `DRIFT` signature), then forward-sync and prove it greens. A passing test on an already-synced copy proves nothing (the slice-051 reflect-drift precedent required exactly this mid-slice proof).
