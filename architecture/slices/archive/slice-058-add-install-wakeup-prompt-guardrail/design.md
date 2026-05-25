# Design: Slice 058 add-install-wakeup-prompt-guardrail

**Date**: 2026-05-22
**Mode**: Standard

## Context recap

The mission brief asks: make the "never pass a slash-command-shaped `prompt` to `ScheduleWakeup` as a no-op label / heartbeat / fallback" lesson portable across machines, by having `INSTALL.md` seed it into the installing user's global `~/.claude/CLAUDE.md`. Today the lesson lives only in this machine's project memory (`memory/schedulewakeup-replays-prompt-literally.md`) and does not travel.

## Graphify context

The slice's entire surface is `INSTALL.md` (a markdown doc — not a node in the tree-sitter code graph), one new isolated test module, one `shippability.md` row, and one ADR. No production code module is created or modified, so `graphify blast-radius` / `reachable` have nothing meaningful to return for a doc-and-test slice. Context was gathered by reading the precedents directly: `INSTALL.md` Step 3d (`INSTALL.md:101-123`) and `tests/methodology/test_install_md_correctness.py` (slice-045).

## What's new

1. **A new install step in `INSTALL.md`** — appended as a new sub-step **`### 3h: Global CLAUDE.md — wakeup-prompt discipline`** (immediately after the current final Step 3 sub-step `3g`), modelled on Step 3d — that appends the `# Wakeup-prompt discipline` block to the installing user's global `~/.claude/CLAUDE.md`. Idempotent (skip if the heading is already present), confirmation-gated (show the planned diff, ask before writing). **Placement rationale (per `/critique-review` M-add-2)**: appended as `3h` rather than inserted as a new `3e` because INSTALL.md's "Source independence" section cross-references `Step 3f` and `Step 3g` by letter — a renumber would have to chase those cross-refs (wide-edit drift risk). The new step is order-independent (it depends on / feeds no other Step 3 sub-step), so last-position is correct. Step 4 "Verify" gains **no** new line — the step writes to global `~/.claude/CLAUDE.md`, which is not an INST-1 inventory item.
2. **The `# Wakeup-prompt discipline` block content** — the **FROZEN canonical wording** the new step appends (per `/critique-review` M-add-1 — the "Draft" label is removed: build appends this block **verbatim**, and the AC2 test anchors on phrases lifted from it, so test and text cannot drift):

   ```markdown
   # Wakeup-prompt discipline

   `ScheduleWakeup` replays its `prompt` argument **literally, as fresh user
   input**, when the scheduled time arrives — even if the work it was meant to
   track already finished.

   - Never pass a slash-command-shaped string (`/foo ...`) as a no-op label,
     heartbeat, or fallback wakeup. It is not a label — the runtime re-fires
     that command as spurious input.
   - Harness-tracked work (the Agent tool, background tasks) notifies you on
     completion; you do not need a fallback wakeup to poll it.
   - Intentional wakeup prompts — `/loop`'s own prompt, a genuine scheduled
     task — are unaffected. This rule targets only the no-op / heartbeat misuse.
   ```
3. **`tests/methodology/test_install_md_wakeup_guardrail.py`** — new regression test module pinning the step + block content + the shippability row.
4. **`architecture/shippability.md`** — new row #58.
5. **`architecture/decisions/ADR-057-*.md`** — the placement decision (see below). Already authored on disk; build must NOT recreate or renumber it (`/critique` m1).
6. **`INSTALL.md` stale-version-literal cleanup** (per `/critique` B2) — `INSTALL.md:18` carries a stale `methodology v0.54.0` literal while `VERSION` is `0.62.0` (slice-045 set it as a hard literal that re-drifted across the 048–054 bumps). `/critique-review` independently verified that `INSTALL.md:18` is the **sole** stale current-version literal (every other version reference in `INSTALL.md` already resolves dynamically from `VERSION` / `ai-sdlc-VERSION` or speaks generically). Since this slice edits `INSTALL.md`, build rewords that single line **drift-proof** — drop the hard `v0.54.0` literal, reference `VERSION` instead (the slice-045 test docstring's own recommendation) — then re-greps `INSTALL.md` to confirm no other `v0.5x`/`v0.6x`-shaped non-`VERSION` literal remains. The new regression test is **not** generalized to pin version literals — declined as scope creep; the drift-proof reword needs no test by construction (nothing left to drift).

## What's reused

- `INSTALL.md` Step 3d (`INSTALL.md:101-123`) — the structural model for the new step: heading-check skip, diff-show, confirmation ask. The new step is its twin.
- `INSTALL.md:198` ("Do not modify the user's global CLAUDE.md without showing the diff and getting confirmation") — the existing rule the new step is governed by; no conflict, the new step complies by construction.
- `tests/methodology/test_install_md_correctness.py` (slice-045, shippability #45) — the regression-test pattern: `from tests.methodology.conftest import REPO_ROOT`, read `INSTALL.md`, regex assertions.
- [[ADR-049]] — install scope is global-only (decided slice-047); the precedent establishing that INSTALL.md-time concerns target global `~/.claude/`.
- `memory/schedulewakeup-replays-prompt-literally.md` — the existing project memory whose wording the appended block mirrors. Read-only reference; **not modified** (out of scope).

## Components touched

### `INSTALL.md` (modified)
- **Responsibility**: the INST-1 install recipe a Claude Code instance executes verbatim to install the pipeline. This slice adds one step to it AND rewords its stale current-version literal(s) drift-proof (per `/critique` B2 — see "What's new" item 6).
- **Lives at**: `INSTALL.md` (repo root).
- **Key interactions**: the new step writes to the installing user's `~/.claude/CLAUDE.md`. No other artifact. `tools/install_audit.py` (INST-1) is unaffected — it enumerates installed skills/agents/templates/methodology-files, none of which change; a global-CLAUDE.md append is not an INST-1 inventory item.

### `tests/methodology/test_install_md_wakeup_guardrail.py` (created)
- **Responsibility**: pin the new INSTALL.md step + block content against drift; pin the shippability row's presence.
- **Lives at**: `tests/methodology/test_install_md_wakeup_guardrail.py` (created by this slice).
- **Key interactions**: reads `INSTALL.md` and `architecture/shippability.md` via `REPO_ROOT` from `tests/methodology/conftest.py`. Consumed by pytest collection and shippability row #58.

## Contracts added or changed

None. No endpoints, events, or schemas. The slice changes install-recipe prose and adds a test.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1**. The slice introduces one new file; it is a test module (a leaf test artifact, not a production module requiring downstream wiring).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_install_md_wakeup_guardrail.py` | pytest collection + `architecture/shippability.md` row #58 | self (the module IS the test; its `test_shippability_row_58_present_and_cites_install_wakeup_guardrail` pins the row) | test module is a leaf test artifact — rationale: a methodology regression-test module is consumed by pytest collection and the shippability runner; it has no production downstream consumer to wire, same class as `test_install_md_correctness.py` (slice-045) |

## Test design notes

(Added per `/critique` M1 + M2.)

All three AC tests are **prose-existence pins** (the slice-045 `test_install_md_correctness.py` class): they assert that the required text is present in `INSTALL.md` / `architecture/shippability.md`. They are **R-2-class** — they guard prose *existence*, NOT runtime *behavior*. No test can verify that a Claude Code instance executing the new install step actually produces the right result on a real machine, because the step runs only at install time. This is an accepted, recorded limitation, not a gap — a behavioral test is infeasible here, exactly as for slice-045 and the `/diagnose` SKILL.md prose-pins.

- **AC1 — `test_install_md_has_idempotent_wakeup_discipline_step`**: asserts the new step's prose contains, as **discrete** checks, (a) an append to `~/.claude/CLAUDE.md`, (b) the `# Wakeup-prompt discipline` heading literal, (c) a skip-if-heading-already-present instruction, (d) a diff-show + confirmation-ask instruction — so a partial regression is caught. The test anchors on the step's **heading text** (`Global CLAUDE.md — wakeup-prompt discipline`), **not** the `3h` step letter — the letter is positional (a future slice adding a Step 3i could shift it); the heading text is stable.
- **AC2 — `test_wakeup_block_states_load_bearing_facts`**: asserts **four discrete** content checks against the appended block — never one loose heading-only assertion that could pass tautologically. The test reads `INSTALL.md`, **collapses whitespace runs to a single space** (so the block's line-wrapping is irrelevant), then asserts these four phrases lifted **verbatim** from the frozen block in "What's new" item 2 (per M-add-1): (a) literal-replay — `literally, as fresh user input`; (b) never-as-no-op — `no-op label, heartbeat, or fallback wakeup`; (c) `/loop` carve-out — both `/loop` and `are unaffected`; (d) harness-notifies context — `notifies you on completion`. Each is a separate `assert`; the mid-slice smoke gate verifies each FAILs **individually** against pre-edit `INSTALL.md`. The four phrases are ASCII-only — no em-dash / ellipsis — so the asserts are encoding-robust.
- **AC3 — `test_shippability_row_58_present_and_cites_install_wakeup_guardrail`**: AC3 is delivered by **exactly one** test function (canonical name above — byte-identical in the mission-brief test-first plan, the mission-brief verification plan, and the wiring matrix). It makes two assertions in the one function: (i) `architecture/shippability.md` contains a row numbered 58, and (ii) that row cites `slice-058-add-install-wakeup-prompt-guardrail` and runs `tests/methodology/test_install_md_wakeup_guardrail.py`. There is no second, separately-named consumer-presence test.

## Decisions made (ADRs)

- [[ADR-057]] — Seed the wakeup-prompt guardrail via an `INSTALL.md` → global `~/.claude/CLAUDE.md` append, not via per-project `/triage`+`/adopt` CLAUDE.md generation — reversibility: **cheap**.

## Inclusion-heuristic classification (BC-PROJ-10 — mandatory pre-`/critique`)

This slice mints an ADR (ADR-057), so an explicit Inclusion-heuristic classification is required before `/critique`.

**Classification: NO `methodology-changelog.md` entry, NO `VERSION` bump, NO new RULE-ID, NO `plugin.yaml` change, NO entry-pin tests.** This slice is the slice-045 INSTALL.md-prose / no-pipeline-behavior-change conformance class.

Rationale:
1. The slice mints and extends **no RULE-ID** — no new pipeline rule, gate, audit, or discipline. (Distinguishes it from slice-049's OSDG-1 extension, slice-050's AVFS-1.)
2. The slice changes **no pipeline skill's capability** — no `/`-command behaves differently. (Distinguishes it from slice-052's `/slice-candidates --obo`.)
3. The content seeded is a **harness-tool-usage guardrail** (`ScheduleWakeup` is a Claude Code harness tool, not a pipeline operation) written to the user's **global** `~/.claude/CLAUDE.md`. It is not a pipeline methodology rule; the methodology's rule/skill/gate/audit set is unchanged.
4. INSTALL.md changes that do not change *pipeline* behavior are the established no-VERSION-bump class — slice-045 changed INSTALL.md with no bump; [[ADR-049]] confirms INSTALL.md changes outside pipeline behavior are the no-behavior-change conformance class.
5. `MEPD-1(b)` to be discharged **by name** at `/build-slice` against the real META-1 enforcing assertion at `tests/methodology/test_methodology_changelog.py:136` (the slice-032 false-precedent guard) — not on precedent citation alone.

> **Flagged for `/critique` — highest-uncertainty decision of this slice.** The counter-position is real: slice-049 B2 + slice-052 (N=2) establish that *methodology-surface behavior additions* attract a changelog entry + 4-part PMI-1 bump, and adding a new step to the INST-1 install recipe *is* a behavior addition to a methodology surface. The Critic should adjudicate. If reclassified upward, the bump is a **clean additive** — a `## v0.63.0` changelog entry + 4-part PMI-1 bump (`VERSION` + `plugin.yaml` + changelog header + `~/.claude/ai-sdlc-VERSION`) + two entry-pin tests — that restructures nothing already designed here.

## Authorization model for this slice

N/A — the slice adds install-recipe prose and a regression test. No runtime authorization surface. The one privileged action (the new step writing to the user's global `~/.claude/CLAUDE.md`) is governed by the existing `INSTALL.md:198` confirmation rule: the step shows the diff and asks before writing — the user authorizes each run.

## Error model for this slice

The new INSTALL.md step's prose must specify these cases (mirroring Step 3d):
- **`# Wakeup-prompt discipline` heading already present in `~/.claude/CLAUDE.md`** → skip (idempotent re-run; no duplicate append).
- **`~/.claude/CLAUDE.md` absent** → the append creates it (consistent with Step 3d, which appends and does not pre-require the file).
- **User declines the confirmation** → skip the append, note it, continue the install (the block is advisory; declining does not fail the install).

The regression test introduces no runtime error surface; assertion failures are pytest failures with actionable messages naming the missing step / block / row.
