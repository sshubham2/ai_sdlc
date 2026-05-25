# Design: Slice 029 make-diagnose-dispatch-sequential

**Date**: 2026-05-16
**Mode**: Standard

## What's new

- **SKILL.md frontmatter** (`skills/diagnose/SKILL.md`): `argument-hint` extended to document the optional `--parallel` flag alongside the existing `[path-to-repo]` arg.
- **SKILL.md Step 1 — exact bash rewrite (B3 fix)**: the existing `TARGET="${1:-$PWD}"` block (SKILL.md:27–30) is replaced so the flag is stripped **before** TARGET resolution. New block (shape):

  ```bash
  PARALLEL=0
  ARGS=()
  for a in "$@"; do
    case "$a" in
      --parallel)  PARALLEL=1 ;;
      --*)         echo "WARNING: unknown flag '$a' ignored (running sequential default)" >&2 ;;
      *)           ARGS+=("$a") ;;
    esac
  done
  TARGET="${ARGS[0]:-$PWD}"
  OUT="$TARGET/diagnose-out"
  ```
  (TRI-1-ratified option **(B)**, per /critique-review M-add-1: a `--`-prefixed token that is not `--parallel` is an **unknown flag → warned + ignored, never treated as the path**. So a flag typo like `--paralll` never becomes TARGET and never aborts — TARGET falls back to `$PWD`, sequential default. Only a *non-flag-shaped* bad path arg can reach the pre-existing `:41` abort.)

  **Target shell / portability (per /critique-review M-add-1)**: `/diagnose`'s bash runs under `MINGW*|MSYS*|CYGWIN*` (Git-Bash) on this Windows platform — SKILL.md:86 already branches on `case "$(uname -s)"`. The existing SKILL.md uses **zero bash arrays**; this snippet introduces `ARGS=()`/`"$@"`. Git-Bash ships bash ≥4.x (arrays supported), so the construct is portable — **build-slice MUST dry-run this exact snippet under Git-Bash and record the result in build-log.md** (unverified-runtime-construct on the must-not-defer fail-safe path is not a "trust me").

  Consequence (corrected per /critique-review M-add-1 — the enforcing abort is SKILL.md:41, the `cd "$TARGET" … || { echo "TARGET does not exist"; exit 1; }` line, **not** the :25 prose): `/diagnose --parallel` (no path) → `ARGS` empty → `TARGET=$PWD` (never `--parallel`, never the `:41` abort). A flag typo like `--paralll` matches the `--*` case → warned + ignored → also never becomes TARGET, `TARGET=$PWD` sequential, **never aborts** (TRI-1-ratified option B — fully honors the literal must-not-defer "unrecognized/garbled argument → sequential default, never a mid-run abort"). Only a *non-flag-shaped* token that is a genuinely bad path can reach the pre-existing `:41` `cd`-fails abort — that is unchanged correct path-validation behavior, not a flag-induced abort.
- **SKILL.md Step 5 — dispatch-coupled prose inventory (B1 fix)**: the rewrite is **not** "body byte-unchanged". The following dispatch-coupled sentences are intentionally rewritten dispatch-mode-aware (enumerated so the diff is auditable, not hand-waved):
  - `## Step 5 — Fan out the analysis passes (parallel)` heading → `## Step 5 — Dispatch the analysis passes (sequential by default; --parallel opt-in)`.
  - `**Parallel batch (run in a single message with multiple Agent tool calls).**` (≈:120) → split into a **default-sequential loop** paragraph + a clearly-delimited **`--parallel` opt-in batch** paragraph (the opt-in paragraph carries the original "single message, multiple Agent tool calls" wording verbatim).
  - `For each completed subagent (process them as they finish — order doesn't matter)` (:170) → made mode-aware: sequential default = "after each Agent returns, immediately run the writer flow below, then spawn the next; in `--parallel` mode, process them as they finish — order doesn't matter".
  - `Wait for all 10 to finish (and for write_pass.py to have run on each) before Step 6.` (:187) → "Whether dispatched sequentially (default) or as a `--parallel` batch, all 10 passes MUST have returned and had `write_pass.py` run before Step 6."
  - **Step 5.5** (:191) `After the parallel batch completes, check that every pass produced its three files` → `After all 10 passes have been dispatched and written (sequentially by default, or after the --parallel batch), check that every pass produced its three files`. Plus an **early-exit clause**: "If the sequential loop did not reach all 10 passes (orchestrator interrupted), the unspawned passes are *missing*, not *failed* — Step 5.5's 'do not proceed to Step 6 with gaps' applies identically: re-spawn the missing pass(es) before Step 6; never silently skip."
  - The COST-1.1 model-routing table and the **single shared subagent-contract subsection** (SKILL.md:149–162, M3 fix) are **referenced by both branches, emitted exactly once** — the `--parallel` opt-in paragraph does NOT re-emit the contract subsection or the table (single-source, same rule already applied to COST-1.1). This protects CSP-1 byte-equality and the LAYER-EVID-1 N=6 pin from accidental duplication.
- **ADR-027**: locks "sequential-by-default, `--parallel` opt-in" as the /diagnose Step-5 dispatch decision (reversibility: cheap).
- **Prose-pin tests** (`tests/skills/diagnose/test_skill_md_pins.py`): new assertions — (a) sequential-default prose present in Step 5, (b) `--parallel` opt-in prose present + documented in `argument-hint`, (c) flag-strip-before-TARGET fail-safe prose present, (d) Step 5.5 dispatch-mode-aware + early-exit clause present. Existing CSP-1 byte-equality + slice-019 LAYER-EVID-1 N=6 + mini-CAD drift tests are **NOT modified** (they must keep passing unchanged — they are the regression guard for the rewrite).
- **risk-register.md**: R-1 Status `open` → `mitigating` **plus a new RR-1 `Mitigation:` structured field** (m2 fix) citing slice-029 + ADR-027, explicitly stating the cwd-mismatch hypothesis remains open and the `--parallel` path retains full exposure (M1 — no silent over-claim).
- **methodology-changelog.md v0.43.0 (TRI-1-ratified M2 option B)**: a `### Changed`-class entry — *"`/diagnose` analysis-pass dispatch is sequential by default; prior parallel batch is an explicit `--parallel` opt-in"* — citing [[ADR-027]] + slice-029, **NO new rule-ID**. Triggers the obligatory PMI-1 lockstep: `VERSION` 0.42.0→0.43.0 + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + `tests/methodology/test_methodology_changelog.py` v0.43.0 entry-pin, applied atomically (build-slice obligation; see the M2 block's open mechanical-risk note re: rule-ID-less entry vs PMI-1/changelog audits).
- **shippability.md**: a propagation row whose **Command cell is a real runnable selector** (m1 fix) using the **exact file-selector form of existing row 1** (per /critique-review M-add-4 — zero of the 29 existing rows use a `-k "..."` substring expression; the `-k` form's survival through the Step-5.5 backtick-strip+reparse path is unexercised, a slice-024 footgun): `<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/skills/diagnose/test_skill_md_pins.py --no-header -q` (no markdown backticks inside the cell; absolute `$PY` path; `--no-header -q` per slice-024 lessons; runs the full pin file incl. the 4 new pins — no `-k`, no novel selector form).

> **M2 — RE-SCOPED per /critique-review; TRI-1-RATIFIED 2026-05-16 → option (B).**
> - **Settled**: NO `DSEQ-1` rule-ID is minted (slice-002 prose-pin-only precedent; minting an audited rule-ID for a single-surface no-audit prose behavior is ceremony).
> - **TRI-1 user decision = (B)**: a **methodology-changelog v0.43.0 entry IS added** (honoring the unconditional inclusion heuristic `methodology-changelog.md:7` — a default-dispatch behavior change qualifies regardless of the slice-002 precedent, which is treated as latent under-documentation). The entry is a `### Changed`-class entry describing the sequential-default `/diagnose` dispatch behavior change, citing [[ADR-027]] + slice-029, **with NO new rule-ID** (cross-referenced by ADR-027 + the prose-pins, not by an audited rule). Consequent **PMI-1 4-surface lockstep is obligatory**: `VERSION` 0.42.0→0.43.0 + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + the `test_methodology_changelog.py` v0.43.0 entry-pin, all atomic.
> - **Build-slice obligation / open mechanical risk**: every recent changelog entry (v0.41 PCA-1, v0.42 UTF8-STDOUT-1) carries a rule-ID bullet under `### Added|Changed|Retired`. A no-rule-ID `### Changed` entry is the user-ratified shape; **/build-slice MUST verify `tools.plugin_manifest_audit` (PMI-1) + `test_methodology_changelog.py` accept a rule-ID-less `### Changed` entry**. If an audit structurally requires a rule-ID bullet, surface it at the mid-slice smoke gate as a DEVIATION and re-triage the entry shape (e.g., a changelog-only non-audited label explicitly marked "not a gate", mirroring how v0.42.0 documents non-gate version-evolutions) — do NOT silently mint an audited rule-ID (that would reverse the settled half of M2).

## What's reused

- [[decisions/ADR-001]] — the ADR-001 subagent contract (subagent does analysis only, returns 3 fenced blocks; orchestrator writes via `write_pass.py`). Sequential dispatch reuses this **unchanged** — only *when* each Agent is spawned changes, not the per-pass contract.
- `skills/diagnose/write_pass.py` — unchanged; the per-pass write/normalize/validate flow is invoked identically, just one-at-a-time.
- The canonical subagent-contract string (`SLICE_002_CANONICAL_CONTRACT` in `tests/skills/diagnose/test_skill_md_pins.py:24`) — must remain byte-identical across SKILL.md Step 5 + all 11 `passes/*.md`. The sequential rewrite MUST NOT alter this string in either branch.
- Mini-CAD byte-equality discipline (`tests/skills/diagnose/test_diagnose_skill_drift.py`) — the installed copy `~/.claude/skills/diagnose/SKILL.md` must be forward-synced after the in-repo edit (build-slice obligation).
- **slice-019 LAYER-EVID-1 N=6 byte-equality pin (B2 fix — highest-risk casualty of a Step-5 restructure)**: the LAYER-EVID-1 cross-reference paragraph carrying the byte-locked phrase `textual import-evidence requirement` lives **inside Step 5** (SKILL.md:164–166), between the canonical-contract subsection and "After each subagent returns" — squarely in the rewrite blast radius. `test_skill_md_pins.py::test_skill_md_step5_documents_textual_evidence_rule` + `test_textual_evidence_rule_byte_equal_across_n_3_surfaces` pin it across **N=6 surfaces** (3 in-repo + 3 installed). **Constraint on the rewrite**: this paragraph is preserved *verbatim* and remains correctly positioned (it stays in Step 5, after the single shared contract subsection, ahead of the per-pass writer flow). The sequential/`--parallel` split MUST NOT relocate, reflow, or split it. Forward-sync to the installed copy is mandatory (mini-CAD + this N=6 pin both fail on partial sync — the documented slice-019 prior).
- [[slice-002-fix-diagnose-contract-and-cwd-mismatch]] — precedent: same R-1/R-2 surface, handled as prose-pin-guarded SKILL.md change, no `/repro` route **and no rule-ID / changelog entry**. This slice follows that pattern (see M2 disposition).
- COST-1.1 model-routing table (SKILL.md Step 5) — single shared block referenced by both dispatch branches; emitted once, not duplicated, not changed.

## Components touched

### `skills/diagnose/SKILL.md` (modified)
- **Responsibility**: the executable orchestration contract for `/diagnose`. WHAT changes: Step-1 arg parsing gains `--parallel` recognition; Step-5 default control flow becomes sequential (spawn→await→write→next) with a delimited opt-in parallel branch.
- **Lives at**: `skills/diagnose/SKILL.md` (modified) + forward-synced to `~/.claude/skills/diagnose/SKILL.md`.
- **Key interactions**: drives `Agent` tool dispatch; invokes `write_pass.py`. **Step *sequence* 5→5.5→6→6.5→7 is unchanged** (no step reordered/added/removed); **Step 5.5 *prose* IS rewritten dispatch-mode-aware** per "What's new" item 3 (opening clause + early-exit clause — not "untouched", per /critique-review M-add-3); Step 6 (04-ai-bloat) + Step 6.5 (narrator) bodies are untouched except literal "(parallel)" wording in cross-references (they are already single-agent).

### `tests/skills/diagnose/test_skill_md_pins.py` (modified)
- **Responsibility**: prose-pin regression guard for SKILL.md behavioral claims. WHAT changes: adds the 4 new sequential-dispatch pins (sequential-default / `--parallel`-opt-in / flag-strip-fail-safe / Step-5.5-dispatch-aware+early-exit); leaves ALL slice-001/002/019 pins (incl. CSP-1 byte-equality + LAYER-EVID-1 N=6) intact and unmodified.
- **Lives at**: `tests/skills/diagnose/test_skill_md_pins.py` (modified).
- **Key interactions**: imports `SKILL_DIR`/`PASSES_DIR` from `conftest.py`; same `_read` helper pattern as existing pins.

## Contracts added or changed

No HTTP/event contracts. The only "contract" surfaces are:
- **CLI arg contract**: `/diagnose [path-to-repo] [--parallel]` — `--parallel` is position-independent, optional, default-off. Defined in `skills/diagnose/SKILL.md` frontmatter `argument-hint` + Step 1 parse prose. No schema file (markdown-as-code).
- **Subagent contract**: unchanged — the byte-locked canonical line is preserved verbatim (CSP-1).

## Data model deltas

None. No entities, no migrations, no schema.

## Wiring matrix

Per **WIRE-1**. This slice introduces **no new modules** — it modifies existing SKILL.md prose, an existing test file, an existing changelog/risk-register/shippability, and adds one ADR (documentation artifact, not a code module with a consumer). Zero-row matrix = clean per the audit.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-027]] — `/diagnose` Step-5 analysis-pass dispatch is sequential-by-default; parallel batch is an explicit `--parallel` opt-in — reversibility: **cheap** (default is one prose branch in SKILL.md; reverting is a one-paragraph edit, no code/contract/data change).

## Authorization model for this slice

N/A — `/diagnose` is a local read-only analysis skill with no auth surface. Dispatch sequencing does not introduce any privilege boundary. (Listed explicitly per the must-include rule; genuinely empty.)

## Error model for this slice

No new error codes. Three failure-handling obligations carried by the design:
1. **Flag-strip fail-safe (B3)**: `--parallel` is stripped from args *before* TARGET resolution, so a flag-shaped token never becomes the path and never triggers the `:41` flag-induced abort. The pre-existing `:25` empty/bad-path check is unchanged and still fires for a genuinely bad path (that is correct existing behavior, not a regression).
2. **Sequential silent-gap preservation (B1)**: Step 5.5's "every pass produced its 3 files; do not proceed to Step 6 with gaps" holds in the sequential loop. Two sub-cases, both handled: (a) a pass *failing* the 3-attempt cap is recorded `.failed.raw` + marked degraded exactly as today, and the sequential loop continues to the next pass (one degraded pass does not abort the rest); (b) the loop *not reaching* all 10 (orchestrator interrupted) leaves unspawned passes *missing* — Step 5.5 re-spawns the missing pass(es) before Step 6, never silently skips. Pinned by the new Step-5.5 dispatch-aware + early-exit pin.
3. **No-duplication invariant (M3)**: the single shared subagent-contract subsection + COST-1.1 table are emitted once and referenced by both branches, so CSP-1 byte-equality and the LAYER-EVID-1 N=6 pin cannot be broken by branch duplication.

## Critic dispositions applied (slice-029 /critique round 1 — NEEDS-FIXES)

All findings ACCEPTED-FIXED in this design round (see `critique.md` for full text + Builder drafts; user ratifies at TRI-1):

- **B1** (Step-5.5 "byte-unchanged" over-claim) → dispatch-coupled prose **inventory** added under "What's new"; verification-plan #3 in mission-brief reworded from "byte-unchanged" to "enumerated intentional edits"; early-exit silent-gap clause added.
- **B2** (slice-019 LAYER-EVID-1 N=6 pin in blast radius) → added to "What's reused" with verbatim-preserve + correct-position constraint; mid-slice smoke gate now names `test_textual_evidence_rule_byte_equal_across_n_3_surfaces` explicitly.
- **B3** (`--parallel`-only vs `${1:-$PWD}` abort) → exact Step-1 flag-strip-before-TARGET bash rewrite specified; mission-brief gains `--parallel`-no-path and `--paralll`-typo verification rows.
- **M1** ("retired" vs "mitigating" inconsistency) → mission-brief header → "Risk mitigated (not retired)"; AC #5 locked to "→ mitigating"; R-1 rationale states residual exposure.
- **M2** (DSEQ-1 + v0.43.0 ceremony) → **DROPPED** (no rule-ID, no changelog entry, no PMI-1 version bump) per slice-002 prose-pin-only precedent. *User-overrideable at TRI-1.*
- **M3** (contract-subsection single-source) → single shared block invariant asserted (No-duplication invariant above + "What's new").
- **m1** (shippability prose vs real command) → exact runnable Command cell specified.
- **m2** (RR-1 Mitigation field) → R-1 gains a structured `Mitigation:` field, not only free-form prose.
