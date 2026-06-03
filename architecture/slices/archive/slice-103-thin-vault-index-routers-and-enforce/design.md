# Design: Slice 103 thin-vault-index-routers-and-enforce

**Date**: 2026-06-03
**Mode**: Standard
**Scope tag**: **MEPD-1 EXCLUDE** — no new RULE-ID, no `methodology-changelog.md` entry, no VERSION bump. The "thin router" contract is ALREADY asserted in `skills/archive/SKILL.md` (L113 "one-line summary, trimmed to one line"; L115/L120 "~10 from recent reflections"); this slice ENFORCES an existing documented contract + adds a tool, it does not mint a new methodology rule (slice-100 precedent: a new audit tool added MEPD-1 EXCLUDE, plugin.yaml/install_audit enumerated, no VERSION bump).

## What's new

- `tools/index_router_thinness_audit.py` — a new fail-closed audit that pins the thinness of the two hot index routers (per-row char cap on both index tables + a bounded, verdict-tagged action-points register + total-file-size backstops).
- `tests/methodology/test_index_router_thinness_audit.py` — paired test (real-tree clean + non-vacuity by mutation + CLI exit codes).
- A new **standalone** `architecture/slices/action-points.md` holding the synthesized cross-slice action-points register (≤25 verdict-tagged entries) — the replacement for the 631-line all-history "Aggregated lessons" dump. **(B1 fix — moved OUT of `_index.md` to its own file so the `/reflect`+`/archive` regeneration path physically never touches it; `_index.md` links to it.)**
- `architecture/decisions/ADR-093-thin-index-routers.md`.

## What's reused

- `tools/_vault_paths.py` `VAULT_ROOT` — the audit resolves both index files through it (flip-safe routing, consistent with slice-093/098/100/102 vault-routing work). `[[ADR-085]]`/`[[ADR-091]]`.
- `tools/install_audit.py` `_CANONICAL_TOOLS` + `plugin.yaml` tool list — extended additively with the new tool (PMI-1/INST-1; slice-100 precedent at `tools/install_audit.py:92` / `plugin.yaml:167`).
- `architecture/lessons-learned.md` — the durable all-history lessons store (`/reflect` Step 5 appends here; 92 slices). It REMAINS the sole home of full lesson history; the register is a synthesis derived FROM it, not a replacement of it.
- `architecture/shippability.md` — the slice-finish regression gate; the new test is added as a row (RPCD-1/SCPD-1).
- The `write_slice_queue` **pick-log-tail preservation** pattern (`tools/slice_queue_writer.py`) — the conceptual model for "regenerate the head, preserve the curated tail verbatim" applied here in prose to the register section.

## Components touched

### `tools/index_router_thinness_audit.py` (new)
- **Responsibility**: fail-closed enforcement that `_index.md` + `archive/_index.md` stay thin routers — so the prose-only "thin" contract that drifted (319.5 KB / 414.1 KB today) can't silently re-bloat.
- **Lives at**: `tools/index_router_thinness_audit.py` (created by this slice).
- **Key interactions**: reads both index files via `tools/_vault_paths.VAULT_ROOT`; CLI exit 0 (clean) / 1 (violations) / 2 (usage). `--json` for machine consumption.
- **Checks** (region-anchored — NOT whole-file token scans; heeds the slice-099/100 lesson):
  1. `_index.md` `## Most recent 10` table — every data row (a `|`-line that is not the header or the `|---|` separator) ≤ `_MAX_ROW_CHARS` → `row-too-long`.
  2. `archive/_index.md` catalog table — every data row ≤ `_MAX_ROW_CHARS` → `row-too-long`.
  3. `action-points.md` register (B1 — standalone file, NOT a `_index.md` section) — entries (`- **AP-<n>**` lines) count is `1 ≤ n ≤ _MAX_ACTION_POINTS` (file absent/empty → `register-missing`; `>25` → `register-too-many`); every entry carries exactly one `[<verdict>]` tag ∈ `_VALID_VERDICTS` (else `register-untagged`).
  3b. `_index.md` "Most recent 10" has at most `_MAX_RECENT_ROWS` (10) data rows (m1) → `recent-10-too-many`.
  4. Total-size backstop: `_index.md` ≤ `_MAX_INDEX_BYTES`, `archive/_index.md` ≤ `_MAX_ARCHIVE_BYTES` → `file-too-large` (catches a NEW bloated section the row/region checks don't anchor on — defense in depth).
- **Fail-closed**: a missing section / unparseable table / absent file is a VISIBLE violation, never a silent pass (R-7 class).
- **Module constants (SSoT — the SKILL.md prose cites these by name, not by repeating the numbers)**: `_MAX_ROW_CHARS = 500` (m3 — raised from 400 for headroom vs the worst-case folder-name row, where a 64-char name appears twice in the link markup), `_MAX_ACTION_POINTS = 25`, `_MAX_RECENT_ROWS = 10` (m1 — recent-10 must be exactly 10), `_VALID_VERDICTS = frozenset({"already-a-gate", "build-check-candidate", "critic-calibrate-probe", "cultural"})`, `_MAX_INDEX_BYTES = 65_536`, `_MAX_ARCHIVE_BYTES = 163_840`. Tunable; chosen so today's rows (1,250–13,720 chars) all fail and a genuine one-liner+markdown-wrapper (~160–280 chars) clears 500 with headroom.

### `architecture/slices/_index.md` (modified — one-time thinning + new section)
- **Responsibility**: the hot lookup router read every `/slice` / `/critique` / `/design-slice`.
- **New shape**: `## Active` (regen) + `## Most recent 10` (thin one-liner rows: `| NNN | [name](archive/slice-NNN-name/) | shipped | one-line intent |`, intent from the slice's `mission-brief.md` Intent trimmed to ≤ cap) + `## Cross-slice action points` (curated ≤25-entry verdict-tagged register, positioned where "Aggregated lessons" was).

### `architecture/slices/archive/_index.md` (modified — one-time thinning)
- **New shape**: the 8-col table (`# | Slice | Shipped | Mode | Risk-tier | Result | Critic findings | Discoveries`) collapses to a thin 4-col catalog (`# | Slice | Shipped | one-line intent`). Mode/Risk-tier/Result/Critic/Discoveries detail already lives durably in each `archive/slice-NNN/` folder (reflection.md / validation.md / build-log.md) — the catalog points, it does not copy.

### `skills/archive/SKILL.md` (modified — regeneration spec)
- Step 3 + Step 4 templates updated: emit thin one-liner rows (≤ cap) and PRESERVE the `## Cross-slice action points` section verbatim (do NOT regenerate it from recent reflections). The "Aggregated lessons (from recent reflections)" template + the "How Claude uses this index" reference are replaced with the action-points register.

### `skills/reflect/SKILL.md` (modified — Step 6 index-regen, lines ~320-322)
- The auto-archive index-regen (currently "update Aggregated lessons (pull this slice's Lessons)") is changed to: regenerate the thin recent-10 row (one-liner ≤ cap) + PRESERVE the `## Cross-slice action points` section verbatim (pick-log-tail pattern). `/reflect` Step 5 (append the slice's full lessons to `lessons-learned.md`) is UNCHANGED — the durable store keeps growing; only the `_index.md` synthesis stops being an all-history dump.
- **OSDG-1**: `reflect` IS in the OSDG-1 guarded set (`tests/methodology/test_reflect_skill_drift.py`) → the installed `~/.claude/skills/reflect/SKILL.md` MUST be forward-synced (in-repo ≡ installed). `archive` is NOT OSDG-1-guarded but its installed copy is forward-synced for correctness (the installed regenerator must produce the thin form).

## Contracts added or changed

None — no endpoints/events. The audit's CLI contract is exit 0/1/2 + `--json`, consistent with the existing audit-tool family.

## Data model deltas

None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/index_router_thinness_audit.py` | `architecture/shippability.md` row (slice-finish regression gate runs the test) + `plugin.yaml` tool enumeration + `tools/install_audit.py::_CANONICAL_TOOLS` | `tests/methodology/test_index_router_thinness_audit.py::test_real_tree_clean` (+ mutation non-vacuity tests) | — |

## Decisions made (ADRs)

- [[ADR-093]] — the two hot vault index routers are thin (bounded per-row + a bounded verdict-tagged action-points register), enforced by `tools/index_router_thinness_audit.py`; the all-history lessons stay in `lessons-learned.md`. reversibility: **cheap**.

## Register maintenance model (design decision — deferred from the mission brief)

The `## Cross-slice action points` register is a **curated, preserved-across-regen** artifact (NOT auto-regenerated from reflections each archival — that is precisely what bloated the old section). `/reflect` + `/archive` regenerate the Active + recent-10 head and re-emit the register tail verbatim (the `write_slice_queue` pick-log-tail pattern, applied in prose). `/reflect` Step 5 continues to append every slice's full lessons to `lessons-learned.md`, so no lesson is lost; the register is a periodic human/Claude synthesis (cadence akin to `/critic-calibrate`). **Out of scope**: automating register re-synthesis on each archival (a future slice if wanted) — this slice does the one-time initial synthesis and bounds it.

## Authorization model for this slice

N/A — local audit tool + vault-file edits; no auth surface.

## Error model for this slice

The audit exits 2 on usage error (file unreadable / vault root unresolvable), 1 on any thinness violation (with a per-violation kind + `path:line` locus), 0 when clean. A missing region/section/file is a VISIBLE exit-1 violation (fail-closed), never a silent skip.

## Notes on scope / size

This is a large-but-coherent single theme (thin BOTH routers + synthesize the register + enforce + fix BOTH regen specs). Per the mission brief the user explicitly chose full scope; the thinning and the enforcement are deliberately paired (the register preserves the pattern-recognition job the verbose summaries served, which is what makes cutting them safe). `/build-slice` should checkpoint at the mid-slice smoke gate (audit distinguishes thin from bloated) before the bulk one-time archive-catalog regen.

## Critique resolution (TRI-1 ratified 2026-06-03 — verdict NEEDS-FIXES)

Dual-Critic stack (critique.md + critique-review.md): 1 Blocker + 6 Majors (incl. meta-added M-add-1) + 3 Minors, all ACCEPTED. The design above is updated for the ACCEPTED-FIXED items (B1 → standalone `action-points.md`; m3 → cap 500; m1 → `_MAX_RECENT_ROWS=10` + `recent-10-too-many` check; M1 → wording, below). The ACCEPTED-PENDING items below are build obligations `/build-slice` MUST satisfy and quote evidence for in `validation.md`:

- **M1 (wording / MEPD-1 EXCLUDE)**: the audit is wired **shippability-only** (a `shippability.md` regression-catalog row run at `/validate-slice` pre-finish), NOT a `####` Step-6 gate-roster entry. MEPD-1 EXCLUDE stands (meta-confirmed; slice-100 precedent) — **no VERSION bump, no RULE-ID, no changelog entry**. mission-brief AC4 reworded away from "gate roster".
- **M-add-1 (READER-prose edits — consumer-contract completeness)**: moving/renaming the register orphans the readers. Edit ALL reader surfaces to point at `action-points.md` (and drop the old `## Aggregated lessons` section name): `skills/slice/SKILL.md` (sites ~28, ~68, ~71; confirm ~221 prose updates or is left an explicit historical anchor), `skills/critique/SKILL.md` (sites ~67 + the **Critic-input template ~93-94** `# Aggregated lessons (from slices/_index.md)`), `skills/pulse/SKILL.md` (sites ~43, ~236). **OSDG-1**: `critique` IS guarded (`test_critique_skill_drift.py`) → forward-sync its installed copy; `reflect` IS guarded (M4) → forward-sync; `slice` + `pulse` + `archive` are NOT guarded but their installed copies are synced for runtime correctness.
- **M2 (data-loss, AC2)**: throwaway build script — extract each of the 542 `## Aggregated lessons` bullets (normalized text), assert a substring/fuzzy match in `lessons-learned.md`; report orphans; **port any orphan into `lessons-learned.md` BEFORE the cut**; quote orphan-count=0 in validation.md.
- **M3 (archive region anchor + APED-1)**: the `archive/_index.md` catalog region is "the contiguous block of `^\|` lines following the `| # | Slice | Shipped | ... |` header row, terminated at the first non-pipe line or EOF; header + `|---|` separator excluded" (NOT a bare whole-file `^\|` scan). Test: a `|`-containing prose line OUTSIDE the table is NOT counted. **APED-1**: execute the parser at build against (a) real CRLF `_index.md`, (b) heading-less `archive/_index.md`, (c) the `|`-prose-outside-table fixture, (d) a fence-in-`action-points.md` fixture; quote output in validation.md.
- **M4 (SVW-1 + OSDG-1 on regen edits)**: retain the `vault_edit rewrite` (CAS) route token through the reflect/archive regen-prose edits; run `$PY -m tools.skill_vault_write_safety_audit` (expect exit 0); forward-sync `~/.claude/skills/reflect/SKILL.md`.
- **M5 (flip-readiness on the new tool)**: route all vault paths via `VAULT_ROOT` subpaths; after creating the tool run `$PY -m tools.vault_flip_readiness_audit --strict` and confirm zero NEW must-rewrite/needs-human; any doc/error-message `architecture` literal carries the slice-068 two-marker comment.
- **m2 (fence check re-stated)**: post-cut fence verification uses a LINE-ANCHORED `^```` check, NOT a substring scan (a substring scan false-positives on the inline triple-backtick literal at `_index.md:286` — the slice-099/100 whole-line-scan anti-pattern this slice itself warns against).

### Updated component: `architecture/slices/action-points.md` (new, B1)
- **Responsibility**: the curated, bounded (≤25) verdict-tagged cross-slice action-points register — the pattern-recognition input `/slice`+`/critique` consume. Standalone so the `_index.md` regen path can't clobber it.
- **Written by**: a human/Claude periodic synthesis (this slice does the initial cut from `lessons-learned.md`); NEVER by `tools/*.py` and NEVER RMW'd by the regen path → VWS-1/SVW-1 do not gate it (meta-confirmed). No `architecture` path literal → flip-readiness N/A.
- **Read by**: `_index.md` links to it; `/slice` + `/critique` + `/pulse` read it for pattern recognition (the M-add-1 reader edits).

### Updated wiring matrix row
| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `architecture/slices/action-points.md` | linked from `_index.md`; read by `/slice`,`/critique`,`/pulse` (M-add-1 edits); audited by `index_router_thinness_audit` | `tests/methodology/test_index_router_thinness_audit.py::test_register_bounds` | — (data file, not code) |
