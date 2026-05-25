# Design: Slice 046 add-conditional-repro-auto-advance

**Date**: 2026-05-19
**Mode**: Standard

## What's new

- `skills/slice/SKILL.md` Step 3c: the **STOP-and-route behavior** sub-block is reclassified to a **conditional confirm-then-auto-invoke** flow. Section title (`### Step 3c: Bug-fix prelude (BFRD-1)`), opening canonical phrase (`bug-fix repro prelude discipline`), detection sub-modes (a)/(b), and the `shippability.md grep verification` mechanism are all PRESERVED verbatim. Only the terminal "STOP and tell the user to run `/repro` themselves, then re-invoke `/slice`" instruction is replaced.
- `skills/slice/SKILL.md` `## Pipeline position` block: the BFRD-1 user-input-gate line changes from "HALT and route the user to `/repro` first" to "HALT only at the confirm/modify-the-bug-description prompt; on confirm, auto-invoke `/repro` and continue".
- New canonical phrase **`conditional confirm-then-auto-invoke`** pinned across N=3 surfaces (slice-013 EPGD-1 / slice-020 BFRD-1 N-surface schema-pin precedent): (1) `skills/slice/SKILL.md` Step 3c prose, (2) in-repo `methodology-changelog.md` v0.55.0 entry, (3) `architecture/decisions/ADR-048-*.md`.
- New ADR-048 — partial-supersedes ADR-018 (the unconditional STOP-route decision only).
- `methodology-changelog.md` v0.55.0 entry (in-repo + installed, forward-synced) carrying a `Rule reference:` line.
- 1 new prose-pin test in `tests/methodology/test_slice_skill.py` (new section `# --- Slice-046 / BFRD-1 conditional confirm-then-auto-invoke reclassification ---`).
- 1 new entry-pin test in `tests/methodology/test_methodology_changelog.py` (`test_v_0_55_0_bfrd_1_reclassification_entry_present_in_repo` + naming pin), per the consumer-propagation convention every changelog-entry slice follows.
- `architecture/shippability.md` row 46 enumerating this slice's critical-path test(s).
- 4-part atomic version bump `0.54.0 → 0.55.0` (`VERSION`, `~/.claude/ai-sdlc-VERSION`, `plugin.yaml:version`, + installed changelog forward-sync).

## What's reused

- BFRD-1 detection sub-modes (a)/(b) and the `shippability.md grep verification` mechanism — UNCHANGED (`skills/slice/SKILL.md:142-151`).
- The `AskUserQuestion` structured-options tool — already available; Step 3c prose directs `/slice` to use it (per memory `ask-via-structured-options`: free-text questions don't notify the user — the confirm gate MUST be structured options).
- `/repro` skill — invoked, never modified (BFRD-1's documented one-way coupling; [[skills/repro/SKILL.md]]).
- Mini-CAD-1 forward-sync test `tests/methodology/test_slice_skill_drift.py` — reused as-is (EOL-agnostic content-equality, ADR-033).
- PCA-1 `tools/pipeline_chain_audit.py` — reused as-is; it parses only `predecessor/successor/auto-advance/on-clean-completion` + the `**user-input gates**` literal, NOT the gate-list contents (`tools/pipeline_chain_audit.py:91,235`), so rewording the BFRD-1 gate line is contract-safe.
- STP-1 Sub-form A `tools/state_transition_pin_audit.py` — reused as-is; design is constructed so it stays clean (see "STP-1 Sub-form A conformance" below).

## Components touched

### `skills/slice/SKILL.md` — Step 3c body (modified)
- **Responsibility**: codifies the bug-fix repro prelude; this slice changes its terminal action from an unconditional user hand-off to a conditional confirm-then-auto-invoke `/repro` edge, aligning BFRD-1 with PCA-1 (v0.41.0) auto-advance philosophy.
- **Lives at**: `skills/slice/SKILL.md` (in-repo canonical) + `~/.claude/skills/slice/SKILL.md` (forward-synced installed copy Claude reads at runtime).
- **Key interactions**: invokes `/repro` via the Skill tool with the user-confirmed/modified description; uses `AskUserQuestion` for the confirm gate; continues into Step 4 on success.

### New Step 3c flow (replaces the "STOP-and-route behavior" sub-block)

1. Detection fires (sub-modes (a)/(b) — unchanged).
2. `shippability.md grep verification` (unchanged): a `tests/bugs/*` Command-cell row exists ⇒ failing test already established ⇒ proceed to Step 4.
3. Verbal-claim-with-path fast-path (unchanged, PRESERVED): user may paste an already-existing failing-test path (covers `/repro`'s "or project's convention for bug-fix tests" caveat).
4. **Else (no failing test) — conditional confirm-then-auto-invoke** (NEW, replaces the verbatim STOP blockquote): `/slice` distills a one-line bug description, presents it via `AskUserQuestion` structured options — **Confirm** / **Modify** / **Not a bug — cancel**:
   - **Confirm** or **Modify** ⇒ `/slice` invokes `/repro <confirmed-or-modified-description>` via the Skill tool **exactly once**, then re-runs the Step 3c verification. If the `shippability.md grep verification` now finds the `tests/bugs/*` row ⇒ continue to Step 4. **If the row is still missing** (e.g. `/repro` wrote the failing test under a non-`tests/bugs/*` path per its documented "or project's convention for bug-fix tests" caveat, `skills/repro/SKILL.md` L87) ⇒ the re-verification miss routes into the **preserved verbal-claim-with-path fallback** (step 3 above — ask the user to paste the just-created failing-test path); it does **NOT** re-invoke `/repro` and does **NOT** loop. This bounds the auto-invoke edge to a single `/repro` attempt (m-add-1 ACCEPTED-FIXED — DR-1 meta-Critic missed-finding; closes the loop-vs-fallback prose ambiguity on the slice's core new path).
   - **Not a bug — cancel** ⇒ **fail-closed**: `/slice` does NOT auto-invoke `/repro` and does NOT silently proceed; it surfaces that the candidate is not a well-formed bug fix and lets the user re-scope. (Preserves the sole legitimate reason the original gate existed: never auto-establish a test for a wrong/absent failure signature — ADR-018 Failure mode 2.)
5. Mission-brief consequences (UNCHANGED): cite the failing-test path under `Dependencies`; one AC asserts "the failing repro test PASSES at slice end".

## Contracts added or changed

No code endpoints/events. The changed contract is the BFRD-1 skill-prose discipline at `/slice` Step 3c and its PCA-1 `## Pipeline position` user-input-gate declaration. PCA-1 chain shape (`successor: /design-slice`, `auto-advance: true`) is UNCHANGED — only the bug-fix gate's *delivery* (auto-invoke vs hand-off) changes; the candidate-selection gate is unchanged.

## Data model deltas

None.

## STP-1 Sub-form A conformance (load-bearing — the slice-044 state-transition stale-pin class)

This is a prose-repoint of `skills/slice/SKILL.md`, exactly the slice-044 STP-1 Sub-form A class. STP-1 scans every `tests/**/test_*skill*.py` positive `in`-membership pin against a `read_file("skills/<x>/SKILL.md")`-bound name and refuses if the pinned literal is absent from the live SKILL.md. Conformance is achieved by **construction, not realignment**:

- `test_slice_skill_md_bfrd_1_prelude_present` pins `"bug-fix repro prelude discipline"` → **PRESERVED** in the Step 3c opener.
- `test_slice_skill_md_bfrd_1_verification_mechanism_present` pins `"shippability.md grep verification"` → **PRESERVED** in the verification-mechanism bullet.
- `test_slice_skill_md_bfrd_1_prelude_location_pinned` pins anchors `### Step 3c: Bug-fix prelude (BFRD-1)` / `### Step 3b: If user has their own idea` / `### Step 4: Define the slice` → all **PRESERVED** (rewrite stays strictly inside the Step 3c↔Step 4 anchors).
- The new positive pin `assert "conditional confirm-then-auto-invoke" in _step3c_section(SLICE)` is STP-1-governed; the literal IS the deliverable, present by construction. (Verified absent from the unmodified `skills/slice/SKILL.md` — genuine pre-edit FAIL for AC1.)
- The new negative pin asserts the **exact literal** `` re-invoke `/slice` `` is absent: `assert "re-invoke \`/slice\`" not in _step3c_section(SLICE)`. This substring is taken verbatim from the current unconditional-hand-off blockquote (`skills/slice/SKILL.md:155` — *"Then re-invoke `/slice` and cite the failing-test path under `Dependencies`."*) and is **unique to the unconditional hand-off**: the new confirm flow has `/slice` itself auto-invoke `/repro` and continue (it "re-runs Step 3c verification" — it never instructs the user to re-invoke `/slice`). The build MUST verify the rewritten Step 3c section contains NO occurrence of `` re-invoke `/slice` `` so the negative pin genuinely flips FAIL→PASS and stays PASS. As an `ast.NotIn` node it is **excluded** from STP-1 Sub-form A (slice-044 ADR-047 §"Introduced residuals" B1 / DR-1 B-add-1: `NotIn` operands are excluded). No false STP-1 violation. (M1 ACCEPTED-FIXED — exact negative-anchor literal pinned here AND in the genuine-contrast section below; the two sections agree.)

Net: STP-1 Sub-form A stays clean with **zero pre-existing test realignment**. No risk-`**Status**:` flip ⇒ STP-1 Sub-form B not implicated.

## Genuine-contrast build discipline (AC1 content pin — slice-043/045 lesson)

Mission brief sets `Test-first: false` (TF-1 strict gate not engaged). Per the slice-043/045 genuine-contrast lesson and the standing "a content-bearing AC needs a CONTENT pin, not a byte-equality/forward-sync pin" lesson (the mini-CAD drift test is tautological for content): the new `test_slice_skill.py` prose-pin is authored **test-first** — written against the unmodified `skills/slice/SKILL.md`, run to capture a genuine FAIL, THEN the SKILL.md edit lands and the same assertions flip to PASS.

**Exact pinned literals** (M1 ACCEPTED-FIXED — agrees verbatim with the STP-1 Sub-form A section above):

- **Positive pin**: `assert "conditional confirm-then-auto-invoke" in _step3c_section(SLICE)` — this literal is **absent** from the unmodified file (grep-verified zero hits in current `skills/slice/SKILL.md`), so it genuinely FAILs pre-edit.
- **Negative pin**: `assert "re-invoke \`/slice\`" not in _step3c_section(SLICE)` — the literal `` re-invoke `/slice` `` is **present** in the unmodified Step 3c section (verbatim blockquote `skills/slice/SKILL.md:155`), so the negative assertion genuinely FAILs pre-edit; after the rewrite removes the hand-off blockquote it flips to PASS and stays PASS (the new confirm-flow prose deliberately never instructs the user to re-invoke `/slice`).

Both assertions FAIL on the unmodified file and PASS only after the deliverable lands — the non-tautology FAIL→PASS evidence for AC1. The mini-CAD `test_slice_skill_drift.py` byte-equality test is NOT relied on as the AC1 content proof.

## Wiring matrix

Per WIRE-1. This slice introduces **no new modules** — only prose edits, an ADR, a changelog entry, two test functions appended to existing test files (themselves the consumer pins), and a shippability row. Zero-row matrix → clean by construction.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-048]] — Reclassify the BFRD-1 STOP-route to a conditional confirm-then-auto-invoke `/repro` edge; partial-supersedes ADR-018 (STOP-route decision only) — reversibility: **cheap**.

## Rule-ID treatment (no new ID)

This is a **refinement of BFRD-1's terminal-action semantics**, not a new audit-enforced gate (no new `tools/*.py`; reuses PCA-1 + mini-CAD + STP-1). Per the ADR-038 `-D`-vs-`vN.N` convention + ADR-047 option-4 reasoning (a new bare gate ID is reserved for a new programmatic gate), **no new rule ID is minted**. The v0.55.0 changelog entry carries `Rule reference: BFRD-1 (slice-046; ADR-048 partial-supersedes ADR-018 STOP-route decision; refines BFRD-1 terminal action, mints no new rule)` — mirroring the TFFL-1/PTFFD-1 "refines X, supersedes nothing/ADR-NNN" Rule-reference idiom already in the changelog.

**META-1 header-shape requirement (m1 ACCEPTED-FIXED)**: the v0.55.0 entry header MUST be exactly `## v0.55.0 — 2026-05-19` — **em-dash U+2014** (`—`, not an ASCII hyphen `-`) + ISO `YYYY-MM-DD` date — to match the META-1 split regex `^## v\S+ — \d{4}-\d{2}-\d{2}` at `tests/methodology/test_methodology_changelog.py:136` (the `test_each_changelog_entry_carries_rule_reference` gate). A hyphen or missing date would make the regex not recognize the block as an entry — silently passing META-1 (block uncounted) while the new entry-pin test + readers expect it. The literal `Rule reference` token (per the m1 line above) must appear in that block's body. Existing headers (`methodology-changelog.md:37,51,225`) all use `—` + ISO date — match them verbatim.

## Authorization model for this slice

N/A — methodology skill-prose + vault artifacts only; no runtime auth surface.

## Error model for this slice

Two new "error paths", both bounded (no unbounded re-entrancy on the new auto-invoke edge):

1. **Fail-closed branch**: at the confirm gate, "Not a bug — cancel" ⇒ `/slice` neither auto-invokes `/repro` nor proceeds — it surfaces the not-a-bug-fix state for user re-scoping. This is the explicit must-not-defer protection (preserves ADR-018 Failure-mode-2 mitigation: no auto-test for an unconfirmed/absent signature).
2. **`/repro`-completed-but-grep-still-misses branch** (m-add-1): a single auto-invoke of `/repro` followed by a still-missing `tests/bugs/*` row routes into the preserved verbal-claim-with-path fallback (user pastes the just-created path) — NOT a `/repro` re-invoke, NOT a loop. The auto-invoke edge is bounded to exactly one `/repro` attempt; the verbal-claim fallback (unmodified, PRESERVED) is the terminal catch for non-standard `/repro` test paths.
