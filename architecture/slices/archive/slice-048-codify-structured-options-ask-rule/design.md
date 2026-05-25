# Design: Slice 048 codify-structured-options-ask-rule

**Date**: 2026-05-19
**Mode**: Standard

## What's new

- **RULE-ID SOAD-1** (Structured-Options-Ask Discipline) minted in `methodology-changelog.md` as a new `## v0.56.0 — 2026-05-19` entry; `VERSION` 0.55.0→0.56.0; `plugin.yaml:version` 0.55.0→0.56.0 (lockstep, PMI-1).
- **One canonical SOAD-1 rule sentence**, reused **verbatim** (modulo a leading markdown bullet marker only) across 5 surfaces. Edits anchor on the stable `#### …template` heading + the markdown code-fence, NOT line numbers (per critique m1 — line ranges are informational only and drift on any edit):
  1. `skills/triage/SKILL.md` Step 5b **Fresh template** fenced block (≈L212–238, informational)
  2. `skills/triage/SKILL.md` Step 5b **Append template** fenced block (≈L242–253, informational)
  3. `skills/adopt/SKILL.md` Step 10 **Fresh brownfield template** fenced block (≈L360–394, informational)
  4. `skills/adopt/SKILL.md` Step 10 **Append template** fenced block (≈L398–409, informational)
  5. this repo's project-root `./CLAUDE.md` (self-hosting dogfood)
- **New ADR-050** — generalizes ADR-048's gate-specific decision to a pipeline-wide discipline (does NOT supersede ADR-048).
- **New per-version changelog entry-pin pair** `test_v_0_56_0_soad_1_entry_present_in_repo` + `test_v_0_56_0_soad_1_shippability_consumer_propagation` in `tests/methodology/test_methodology_changelog.py`, modeled on the v0.54.0 STP-1 shape (`L3024`/`L3068`) — see "## Changelog entry-pin plan" below (critique B1).
- **New regression test** `tests/methodology/test_soad1_structured_options_ask_rule.py` (genuine-contrast prose-pin for the 5 SOAD-1 surfaces) + shippability catalog row (number = `max(existing)+1`; currently 48 — confirm at /reflect Step 5.3 against the then-current max, per critique m2).
- **Hard-rule-ASK self-consistency reword** (critique M-add-1, user-ratified option (a) at TRI-1): the existing hard-rule ASK line in the SAME 5 surfaces is reworded from a bare free-text ask to a structured-options ask so the shipped artifact does not self-violate SOAD-1 (RSAD-1 recursive-self-application / slice-022 self-violation law). Pattern: `**ASK** the user:` → `**ASK** the user via structured options (per the Ask discipline below):` (and the terser Append variants' `**ASK** the user —`/`**ASK** —` get the equivalent "via structured options" qualifier). Exact wording finalized at /build-slice; the hard rule's semantics (check active slice; if none, ask; wait for answer) are preserved unchanged — only the ask *form* is made SOAD-1-compliant. The AC5 pin literal (the SOAD-1 sentence) is unaffected by this reword.

### Canonical SOAD-1 sentence (the verbatim pinned literal)

ONE sentence, used **verbatim** in all 5 surfaces (a single markdown bullet — fits the ~8-line Append templates as one added bullet line, ≈9 lines, acceptable; line length is not the Append size constraint, line count is):

> **Ask discipline**: when a skill needs user input, present it as structured options (with a recommended choice) via the `AskUserQuestion` tool — never a bare free-text prompt. A bare prose ask is legitimate only where `AskUserQuestion` genuinely cannot model the input. Rationale: Claude Code notifies the user only on options prompts; a free-text question blocks silently.

**AC5 test spec** (resolves critique M1 — no global `.count()`): the test asserts the **full canonical sentence literal verbatim** (above) appears INSIDE each of the four fenced template code-blocks **independently** (triage Fresh, triage Append, adopt Fresh, adopt Append — located by `#### …template` heading → next ` ``` `-delimited fence) AND in `./CLAUDE.md`, modeled on the slice-021 section-scoped precedent `tests/methodology/test_root_claude_md_branch_per_slice_rule.py` (`content.find(section)` → bounded slice → substring assert), NOT a repo-global occurrence count. Because the single sentence carries both mechanic and rationale and is reused verbatim everywhere, one pinned literal covers all 5 surfaces and both must-not-defer items 1 (rationale present) and 2 (both Fresh AND Append) hold by construction. Verified ABSENT in all 5 target surfaces pre-edit (genuine-contrast guaranteed; build-log T0 captures the pre-edit FAIL).

### Escape-hatch wording (critique M2)

The canonical sentence's escape-hatch clause names the genuinely **notification-less** case (ADR-048's verbal-claim-with-path bare-prose fallback used when `AskUserQuestion` cannot model the input) — NOT the tool's *built-in* free-text option, which is itself an options-prompt path that DOES notify. This aligns the shipped rule text with ADR-050 §Decision and mission-brief must-not-defer item 4 (structured options primary/default, not an absolute ban) and avoids teaching readers the false simplification "any tool-fallback free-text is fine".

## What's reused

- [[decisions/ADR-048]] — slice-046's gate-specific "structured options, not free-text" decision for the single BFRD-1 confirm gate. SOAD-1 is its pipeline-wide superset; ADR-048 remains the authority for the BFRD-1 gate specifically.
- User memory `ask-via-structured-options.md` + `repro-confirm-then-auto-invoke.md` — originating user rationale (informational; not a vault artifact).
- `skills/triage/SKILL.md` Step 5b, `skills/adopt/SKILL.md` Step 10 — the existing 4 CLAUDE.md template blocks (edited in place; structure and size discipline preserved).
- `tests/methodology/test_root_claude_md_branch_per_slice_rule.py` — the precedent shape for the AC3 / AC5 root-CLAUDE.md prose-pin (slice-021); the new test models on it (`conftest.read_file` / `REPO_ROOT` helpers).
- `methodology-changelog.md` META-1 generic header-split test + MCFS-1 whole-file forward-sync gate — cover the v0.56.0 entry's *installed↔in-repo* parity generically. **This does NOT replace the per-version in-repo entry-pin** (critique B1): the established convention (v0.53.0/MCFS-1 L2921+L2980, v0.54.0/STP-1 L3024+L3068, v0.55.0/BFRD-1 L3097 — all post-MCFS-1) adds an in-repo `_entry_present_in_repo` pin per versioned entry. SOAD-1 follows it (see "## Changelog entry-pin plan").

## Components touched

### `skills/triage/SKILL.md` (modified)
- **Responsibility**: emits the project-root CLAUDE.md (greenfield opener). Gains the SOAD-1 sentence in both Step 5b template blocks.
- **Lives at**: `skills/triage/SKILL.md`
- **Key interactions**: read by the Claude orchestrator at `/triage`; emits `./CLAUDE.md` into the target project.

### `skills/adopt/SKILL.md` (modified)
- **Responsibility**: emits the brownfield-aware project-root CLAUDE.md. Gains the SOAD-1 sentence in both Step 10 template blocks.
- **Lives at**: `skills/adopt/SKILL.md`
- **Key interactions**: read by the orchestrator at `/adopt`; emits `./CLAUDE.md`.

### `./CLAUDE.md` (modified — this repo)
- **Responsibility**: keeps the orchestrator on the pipeline for THIS repo. Gains the SOAD-1 sentence (self-hosting dogfood).
- **Lives at**: `CLAUDE.md` (project root)

### `tests/methodology/test_soad1_structured_options_ask_rule.py` (created)
- **Responsibility**: regression-pins the full canonical SOAD-1 sentence verbatim inside EACH of the 4 fenced opener template blocks independently (triage Fresh, triage Append, adopt Fresh, adopt Append — section-scoped via `#### …template` heading → fence, NOT global `.count()`) + `./CLAUDE.md` (critique M1; slice-021 precedent shape).
- **Lives at**: `tests/methodology/test_soad1_structured_options_ask_rule.py`
- **Key interactions**: pytest collection; `/validate-slice` Step 5.5 shippability catalog runner.

### `tests/methodology/test_methodology_changelog.py` (modified — append two functions)
- **Responsibility**: per-version entry-pin convention conformance for the new v0.56.0/SOAD-1 entry (critique B1).
- **What's added**: `test_v_0_56_0_soad_1_entry_present_in_repo` (in-repo-only body — `read_file` only, no `Path.home()`, so `shippability_decoupling_audit.classify_fn` → `clean`, per slice-041 M3 discipline) + `test_v_0_56_0_soad_1_shippability_consumer_propagation` (RPCD-1/SCPD-1 — asserts the v0.56.0/SOAD-1 shippability catalog row exists). Modeled on the v0.54.0 STP-1 pair shape (`test_methodology_changelog.py` L3024 / L3068).

## Contracts added or changed

None. No endpoints, events, or schemas. SOAD-1 is a prose/behavioral discipline contract enforced by a prose-pin test, **not** an executable runtime contract.

## Data model deltas

None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_soad1_structured_options_ask_rule.py` | — | — | `methodology regression test — rationale: it IS the consumer/verification surface; consumed by pytest collection + /validate-slice Step 5.5 shippability catalog row max(existing)+1 (currently 48; confirm at /reflect)` |

## Decisions made (ADRs)

- [[ADR-050]] — Generalize ADR-048's gate-specific structured-options-ask requirement into pipeline-wide RULE-ID SOAD-1; codified in the `/triage` + `/adopt` CLAUDE.md templates + this repo's CLAUDE.md — reversibility: **cheap**.

## Design corrections to the mission brief

Per CLAUDE.md vault discipline ("design deviations → update the active slice's design.md, don't carry forward stale design claims"):

- **Mission-brief must-not-defer "CAD-1 / mini-CAD in-repo↔installed parity for skills/triage/SKILL.md + skills/adopt/SKILL.md" is REFINED**: there is **no** `test_triage_skill_drift.py` / `test_adopt_skill_drift.py` mini-CAD guard (drift guards exist only for `build_slice` / `commit_slice` / `critique` / `query_design` / `slice` + `agents/critique.md` CAD-1; verified via `tests/` enumeration). Editing triage/adopt SKILL.md therefore **cannot** FAIL a drift gate. The real obligation is narrower: **forward-sync the installed copies** `~/.claude/skills/triage/SKILL.md` and `~/.claude/skills/adopt/SKILL.md` so a user running `/triage`/`/adopt` in another project reads the SOAD-1-bearing template at runtime. This is a runtime-correctness should (not a gate-enforced must), done at `/build-slice`, recorded here so the must-not-defer is not over-claimed.
- **~~No per-version changelog-entry test~~ — REVERSED by critique B1**: the original draft claimed MCFS-1/slice-041 "retired the per-version coupling", so no `test_v_0_56_0_*` was planned. This was a **false-precedent error** (slice-032 m1 / MEPD-1 class). MCFS-1 retired only the per-version *installed-copy forward-sync reads*; the in-repo `_entry_present_in_repo` pin convention is unbroken across v0.53.0 (L2921/L2980), v0.54.0 (L3024/L3068), v0.55.0 (L3097) — all post-MCFS-1. SOAD-1 follows the convention; see "## Changelog entry-pin plan".

## Changelog entry-pin plan

Per critique B1, append to `tests/methodology/test_methodology_changelog.py` (after the v0.55.0 block ≈L3097+), modeled on the v0.54.0 STP-1 pair (L3024 / L3068):

- **`test_v_0_56_0_soad_1_entry_present_in_repo`** — in-repo-only body (`read_file("methodology-changelog.md")`, no `Path.home()` → `classify_fn` `clean`, slice-041 M3 discipline). Asserts: `## v0.56.0` header present; `_extract_version_body(in_repo, "0.56.0")` contains `SOAD-1`, `ADR-050`, and the lineage literal that SOAD-1 **generalizes ADR-048 / supersedes nothing** (mirrors the v0.54.0 "refines nothing, supersedes nothing" pin, adjusted to SOAD-1's actual lineage: *generalizes* ADR-048's gate-specific decision, mints a new rule, supersedes nothing).
- **`test_v_0_56_0_soad_1_shippability_consumer_propagation`** — in-repo-only; asserts `architecture/shippability.md` contains the v0.56.0/SOAD-1 catalog row (`| <N> | slice-048-codify-structured-options-ask-rule`) and the `SOAD-1` rule reference (RPCD-1/SCPD-1; the slice-040 lesson — an uncatalogued pin's breakage is invisible to the catalog runner).

Both functions ship in this slice's fix block (must-not-defer #5 RPCD-1/SCPD-1 propagation). The v0.56.0 changelog entry's **Validation** line names both pin functions + the shippability row number (mirrors the v0.55.0 entry's "Validation method" naming convention).

## Authorization model for this slice

N/A — no runtime surface, no actors, no protected actions. Documentation/methodology-prose only.

## Error model for this slice

N/A — no new error codes or failure paths. The only "failure" surface is the AC5 regression test FAILing if any of the 5 SOAD-1 surfaces loses the pinned literal (the intended regression guard).
