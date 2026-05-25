---
id: ADR-055
title: Mint BCR-1 — when diagnose-out/backlog.md exists, /slice MUST consult it AND /reflect MUST round-trip closed SC-NNN findings
date: 2026-05-20
slice: slice-053-wire-backlog-md-into-slice-and-reflect
reversibility: cheap
status: accepted
supersedes: null
extends: BC-PROJ-10 / Inclusion-heuristic lineage (slice-052)
---

# ADR-055: Mint BCR-1 — Backlog Consume-and-Round-trip Discipline

## Context

The `/diagnose → /slice-candidates → /slice → /reflect` pipeline was designed to close the loop between forensic codebase analysis and per-slice work. `/diagnose` produces `diagnose-out/diagnosis.html`; the owner annotates it and ships back `diagnose-out/diagnosis.annotated.html`; `/slice-candidates` parses the annotated HTML and emits `diagnose-out/backlog.md` — a pipeline-agnostic, topologically-sorted backlog of slice candidates with severity × blast / effort scoring + must-do-together clusters + dependency map (slice-052 + earlier `/slice-candidates` work).

**The loop was demonstrably half-open**: at `/slice` invocation, the skill's "Gather candidates from ALL these sources" block (lines 40-54 at the time of this ADR) enumerated 6 candidate sources — risk register, recent deferrals, recent discoveries, concept scope not yet built, aggregated-lessons patterns, user-stated intent — but did NOT name `diagnose-out/backlog.md`. The skill prose Claude reads at runtime had no instruction to consult it.

The deviation surfaced empirically on the very `/slice` invocation that minted this slice (2026-05-20): a `diagnose-out/backlog.md` containing 26 owner-confirmed slice candidates existed in the repo (including the **critical-severity** `SC-001` — `pyproject.toml [project].version = 0.20.0` while `VERSION = 0.60.0`, a live `pip install` defect producing a 40-minor-version-stale artifact), yet Claude ranked candidates from internal pipeline signals alone (R-13 OSDG-1 extension, audit-recovered open/mitigating risks) and missed the entire backlog. The user had to interrupt and re-route — *and then explicitly flagged this as a major bug / deviation requiring immediate fix*.

The symmetric gap on the return path: `/reflect` Step 2 (`Update affected vault files`) names the risk register, ADRs, the concept doc, and the slice's own design.md — but does NOT name `diagnose-out/backlog.md`. So even if a slice DID address an `SC-NNN` candidate, the backlog would silently accumulate rows that say "to do" but were already shipped — a different staleness class than the consume-side gap, but the same root cause: no SKILL.md prose contract telling Claude to round-trip the file.

The decision required: how to close both halves of the loop deterministically (audit-enforced, not Claude-judgement) while keeping the contract minimal and additive.

## Options considered

1. **Mint BCR-1 as a prose-contract + anchor-presence-audit rule (this ADR's choice).**
   - Pros: zero new tools (no `tools/backlog_round_trip.py` helper for a v1 contract); minimal surface (two SKILL.md anchor inserts + one audit module + one changelog entry + one shippability row); reuses the SOAD-1 multi-surface anchor-presence audit pattern (slice-048) + the BFRD-1 position-pin pattern (slice-046); both surfaces are already OSDG-1-guarded so the installed↔in-repo forward-sync of the new anchors is free; aligns with the project's "prose IS executable contract" philosophy (CLAUDE.md brownfield rules); reversibility cheap (delete the anchor lines + the audit module + the changelog entry → rule retired).
   - Cons: prose contract performance depends on Claude reading the SKILL.md prose at runtime — the audit pins the prose, not the runtime behavior. Mitigated by the OSDG-1 family + the BCR-1 anchor-presence test running at /build-slice Step 6 pre-finish; mitigated further by the fact that this is the SAME enforcement shape every other in-loop skill behavior contract uses (BFRD-1, SOAD-1, AVFS-1's wiring blocks, etc.). The human-judgement axis (Claude could read the prose and still ignore it) is NOT closed by this ADR — captured as a future-slice candidate (`/critic-calibrate` proposal) and tracked as the R-14 mitigating-status risk.

2. **Build a `tools/slice_candidate_sources_audit.py` that statically parses `/slice`'s SKILL.md and asserts `backlog.md` is enumerated.**
   - Pros: pure-code enforcement, no prose-reading dependency.
   - Cons: a tool that only asserts "prose X is in file Y" is a less-readable, less-maintainable shape than the existing `test_*_skill.py` anchor-presence pattern this project already has 4+ precedents for (test_slice_skill.py BFRD-1, test_soad1_*.py SOAD-1, test_root_claude_md_*.py CAD-1 variants). YAGNI — the audit-module shape IS the test pattern; minting a tool here adds drift surface (PMI-1 / INST-1 enumeration, another mock-budget-lint surface, etc.) for zero deterministic gain.

3. **Build a `tools/backlog_round_trip.py` helper that programmatically updates `diagnose-out/backlog.md` from /reflect.**
   - Pros: deterministic update mechanic (no Claude-judgement on edit shape).
   - Cons: v1 over-engineering. The backlog.md file is gitignored (per the `.gitignore` addition early in this session); the update is an additive `**Addressed:** slice-NNN-<name> on YYYY-MM-DD` line under each closed candidate block — well within Claude's standard Edit-tool capability. A tool would multiply the surface area (tool source, tests, PMI-1/INST-1 enumeration, mock-budget-lint, an audit row, drift-protection) for a single additive line write. Future-slice candidate IF prose-contract drift emerges; not now.

4. **Defer until after slice-054 (= SC-001 fix-pyproject-toml-version-drift) ships, on the grounds that SC-001 is more urgent.**
   - Pros: zero delay on the live `pip install` defect.
   - Cons: the user explicitly flagged the missing-wire as the major deviation, NOT SC-001 (which they explicitly characterized as "queued"). Shipping slice-054 first means /slice would have to re-encounter the same channel-missing pattern Claude just self-demonstrated; the deviation would silently recur on every subsequent `/slice` invocation until the channel is wired. The honest meta-fix sequencing is channel-first, payload-second: slice-053 (channel) → slice-054 (SC-001) → the remaining 25 candidates flow through.

## Decision

**Mint BCR-1 (Backlog Consume-and-Round-trip discipline) as Option 1**: a prose-contract on both `/slice` and `/reflect` SKILL.md surfaces, pinned by a new anchor-presence audit module (`tests/methodology/test_bcr_1_backlog_round_trip.py`), backed by a `## v0.61.0` methodology-changelog entry with a content-bearing entry-pin, enumerated in CLAUDE.md's self-hosting-discipline section alongside CAD-1 / PMI-1 / INST-1 / Mini-CAD / OSDG-1 / SOAD-1, and tracked by a new shippability catalog row (#53). The 4-part PMI-1 atomic bump is applied (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`), 0.60.0 → 0.61.0, per the slice-049/052 Inclusion-heuristic + BC-PROJ-10 law for slices that mint a new rule-ID + change behavior contracts on OSDG-1-guarded surfaces.

The contract has two halves:

**Consume side (`/slice`)**: when `diagnose-out/backlog.md` exists, it is a mandatory candidate source in the "Gather candidates from ALL these sources" block. Absent file → no-op clean (consultation skipped silently). The `/slice` skill prose names the file literally, defines reading guidance (the file's recommended-order list is topo-sorted by dependency × severity / effort and is a primary input), and positions the source after #6 ("User-stated intent") + before the "Use graphify queries" anchor.

**Round-trip side (`/reflect`)**: when a just-completed slice's `mission-brief.md` OR `reflection.md` carries an explicit `**Closes:** SC-\d{3}[, SC-\d{3}, …]` sentinel header (grep-able, not Claude-judgement; mirrors GitHub closes-issue convention; mentioned-vs-closes disambiguation per /critique M4), `/reflect` Step 2 MUST update `diagnose-out/backlog.md` with an in-place additive `- **Addressed:** slice-NNN-<name> on YYYY-MM-DD` line at the END of each closed candidate block — AFTER the `**Evidence:**` sub-bullet list, BEFORE the next `### SC-NNN` header (or end-of-file). This places the `Addressed:` line at a structurally stable seam — at the END of the candidate block, separate from the existing top-of-block fixed-position metadata bullets (per /critique B1 rejection of the previously-proposed mid-metadata insert position). Absent backlog.md → no-op clean. No `**Closes:** SC-NNN` sentinel found → no-op clean (bare mentions of SC-NNN elsewhere in the prose do NOT trigger). `**Closes:**` sentinel present but the candidate block missing from backlog.md → log a warning; no audit failure (the diagnose→slice-candidates→backlog.md pipeline owns SC inventory). SC-NNN block already carries one or more `**Addressed:**` lines (prior-slice double-shipment per /critique m5) → APPEND a new `**Addressed:**` line below the existing one(s); never replace. Multiple `Addressed:` lines are valid — the candidate's history shows every slice that touched it.

Both halves are pinned by anchor-presence + position-pin tests (7 in the new audit module — bumped from 6 to add the M4 closes-sentinel grammar pin — plus 2 entry-pins in `test_methodology_changelog.py`).

## Consequences

- Closes the open `/diagnose → /slice → /reflect` loop deterministically on the structural axis. Future `/slice` invocations will reliably surface backlog candidates without manual intervention; future `/reflect` invocations will round-trip closed `SC-NNN` rows when the slice carries a `**Closes:** SC-NNN` sentinel.
- The next slice (slice-054) is queued as `SC-001 fix-pyproject-toml-version-drift` — the live `pip install` defect — and will automatically flow through the now-wired channel; slice-054's mission-brief.md will carry a literal `**Closes:** SC-001` sentinel.
- The OSDG-1 family transitively guards the new anchor inserts (no additional drift-test wiring needed): a future forward-sync of `skills/slice/SKILL.md` or `skills/reflect/SKILL.md` that loses the BCR-1 anchor fails BOTH the BCR-1 anchor-presence audit AND the OSDG-1 EOL-agnostic byte-equality audit.
- Future skill edits to either surface (`/slice` or `/reflect`) must preserve the BCR-1 anchor; the position-pin tests catch anchor-displacement (insertion or removal that shifts the source-#7 / Step-2-bullet position).
- The human-judgement axis remains open: even with the SKILL.md prose pinned, Claude reading the prose could still elect not to consult `backlog.md` (the slice-052 N=2 missed-by-Critic class adjacent to BC-PROJ-10's deterministic backstop). A `/critic-calibrate` proposal to add a Critic-prompt dimension closing this axis is a future-slice candidate; tracked as risk-register entry R-14 (status: mitigating, reversibility: cheap, discovered: slice-053).
- **R-13 producer-side cross-skill dependency (M2-disclosed per /critique)**: BCR-1's `**Closes:** SC-\d{3}` trigger grammar depends on the upstream `/slice-candidates` skill (specifically `skills/slice-candidates/build_backlog.py`) emitting candidates with the `SC-\d{3}` identifier syntax. `skills/slice-candidates/SKILL.md` is NOT yet in the OSDG-1 guarded set (R-13 OPEN per `architecture/risk-register.md:225`, deliberately deferred by slice-051/052 own-slice-precedent). A future producer-side edit that renames SC-IDs to a different shape (e.g. `BL-001`, `CAND-001`, `SC-1234`) would silently no-op BCR-1's consumer-side trigger on every subsequent /reflect. Mitigation: design.md Test #6 pins the literal `SC-\d{3}` regex grammar in the SKILL.md consumer prose, so a future producer rename forces a same-time consumer update (the audit FAILs until both sides agree on the new grammar). Closing this exposure structurally requires extending OSDG-1 to `/slice-candidates` (the R-13 open risk's documented retirement path) — slice-053 deliberately does NOT do this extension (own-slice precedent), but the risk-register entry minted at /reflect (R-14 / sibling entry) will record the BCR-1↔R-13 link explicitly so a future maintainer reading R-13 sees the slice-053 consumer dependency.
- Self-bootstrap: slice-053 itself does NOT carry a `**Closes:** SC-NNN` sentinel in mission-brief.md (the literal `**Closes:**` header is absent — verified by grep; the `**SC-001**` bold-emphasis mentions in Risk-retired / Out-of-scope are NOT sentinel-anchored), so its own /reflect Step 2 correctly no-ops on the round-trip side. The first round-trip will fire on slice-054 (which WILL carry `**Closes:** SC-001`).
- The 4-part PMI-1 bump 0.60.0 → 0.61.0 follows the slice-048/044/050/038 new-rule-ID minting precedent. Future audits / readers of methodology-changelog.md will find BCR-1 named under `## v0.61.0` with the ADR-055 lineage line + extends-BC-PROJ-10/Inclusion-heuristic clause + content-bearing two-surface body.

## Reversibility

**Cheap**. The rule's full surface area:
- One prose anchor in `skills/slice/SKILL.md` (~1 paragraph / ~5 lines) + lock-step in `~/.claude/skills/slice/SKILL.md`.
- One prose bullet in `skills/reflect/SKILL.md` (~1 bullet / ~3 lines) + lock-step in `~/.claude/skills/reflect/SKILL.md`.
- One new audit module (~150 lines, SOAD-1 / BFRD-1 precedent shape).
- One `## v0.61.0` entry in `methodology-changelog.md` (~12 lines) + forward-sync.
- Two entry-pin tests in `test_methodology_changelog.py` (~80 lines combined).
- One shippability catalog row.
- One new bullet in CLAUDE.md's self-hosting-discipline section.

Removal cost: delete the anchor lines, delete the audit module, delete the shippability row, delete the changelog entry + entry-pins, delete the CLAUDE.md bullet, bump VERSION 0.61.0 → 0.62.0 with a supersession entry citing ADR-055 (per the append-only ADR discipline; the ADR-055 file itself stays + gets a `superseded-by: ADR-NNN` field). No code-side migration, no contract consumers outside this repo (the `/diagnose → /slice-candidates → backlog.md` upstream is unchanged — slice-053 wires a consumer; removing the consumer leaves the upstream emit-side untouched). No data migration (backlog.md is gitignored and additive-only).

Lineage: extends the BC-PROJ-10 / Inclusion-heuristic lineage (slice-052) — slice-053 is the second slice to discharge BC-PROJ-10 by name (slice-052 minted it; slice-053 applies it explicitly in mission-brief.md + design.md + this ADR). Supersedes nothing.
