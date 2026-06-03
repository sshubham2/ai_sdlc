---
id: ADR-093
title: The two hot vault index routers are thin (bounded per-row + bounded verdict-tagged action-points register), enforced by an audit
date: 2026-06-03
slice: slice-103-thin-vault-index-routers-and-enforce
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-093: Thin index routers, enforced

## Context

`architecture/slices/_index.md` (read on every `/slice`, `/critique`, `/design-slice` per `skills/archive/SKILL.md:185-187`) had grown to 319.5 KB / 666 lines, and `archive/_index.md` to 414.1 KB (avg 3,925 chars/line, longest 13,720). Two regions drove it:

1. **Most recent 10** rows — the spec (`skills/archive/SKILL.md:113`) says "one-line summary, trimmed to one line"; reality was 1,250–2,265-char paragraphs.
2. **Aggregated lessons** — the spec (L115/L120) says "~10 from recent reflections"; reality was a 631-line all-history log of ~95 slices.

Both regions duplicate content that already lives durably elsewhere: the per-slice `mission-brief.md`/`reflection.md` in each `archive/slice-NNN/` folder, and `architecture/lessons-learned.md` (the 426.9 KB durable lessons store `/reflect` Step 5 appends to). **Root cause**: the "thin" contract was asserted in prose but enforced by nothing, so each `/reflect`→`/archive` regeneration accumulated instead of bounding, and it compounded silently.

## Options considered

1. **Thin the files once, no enforcement** — pro: trivial; con: re-bloats on the next regeneration (this is exactly what happened repeatedly). Rejected.
2. **Move the lessons/register to separate files, link from `_index.md`** — pro: regen can't clobber them; con: extra files + extra reads for the pattern-recognition consumers (`/slice`, `/critique`) that already read `_index.md`. Deferred (a `## section` preserved-across-regen is simpler for consumers).
3. **Thin both files to one-liner+pointer rows, replace the all-history dump with a bounded curated action-points register, AND add a fail-closed audit that pins the thinness** — pro: closes the enforcement gap that caused the drift; the register preserves the pattern-recognition job better than 95 verbose summaries; con: a new tool + two SKILL.md spec edits. **Chosen.**

## Decision

`tools/index_router_thinness_audit.py` enforces, region-anchored:
- every `## Most recent 10` (in `_index.md`, ≤ `_MAX_RECENT_ROWS`=10 rows) and catalog (in `archive/_index.md`) data row ≤ `_MAX_ROW_CHARS` (500);
- the standalone `architecture/slices/action-points.md` register with `1 ≤ entries ≤ _MAX_ACTION_POINTS` (25), each carrying exactly one verdict tag ∈ {`already-a-gate`, `build-check-candidate`, `critic-calibrate-probe`, `cultural`};
- total-file-size backstops.

The all-history lesson record stays in `architecture/lessons-learned.md` (unchanged; `/reflect` Step 5 keeps appending). The register lives in its own `architecture/slices/action-points.md` so the `/reflect`+`/archive` `_index.md` regeneration never touches it (B1 — preservation is structural, removing the LLM from the loop, NOT a prose directive). `skills/archive/SKILL.md` + `skills/reflect/SKILL.md` regen specs emit thin rows; `_index.md` links to `action-points.md`. The reader consumers `/slice` + `/critique` + `/pulse` are repointed at `action-points.md` (M-add-1); installed copies forward-synced for the OSDG-1-guarded `reflect` + `critique`.

**Critique amendment (2026-06-03, pre-acceptance)**: the first draft kept the register as a `## Cross-slice action points` section IN `_index.md`, "preserved verbatim across regen (the `write_slice_queue` pick-log-tail pattern, in prose)." `/critique` B1 (Blocker) showed that pattern is CODE with no LLM, while the `_index.md` regen is a Haiku-subagent + `vault_edit rewrite` path — so "preserve in prose" is the unenforced-prose root cause this ADR diagnoses. Resolved by the standalone `action-points.md` (Option 2). `/critique-review` M-add-1 (Major) added the consumer-contract consequence (repoint `/slice`+`/critique`+`/pulse` readers). Both folded in. Amended pre-acceptance within the authoring slice; SUP-1 append-only applies once shipped.

**MEPD-1 EXCLUDE**: enforcing an already-documented prose contract + adding a tool mints no new methodology RULE-ID, changelog entry, or VERSION bump (slice-100 precedent for a new audit tool added without a bump).

## Consequences

- The two hot routers collapse from ~734 KB combined to a few KB; every `/slice`/`/critique`/`/design-slice` run reads a lean router.
- A future regeneration cannot silently re-bloat — the audit fails the slice-finish regression gate (shippability) if a row exceeds the cap, the register exceeds 25 / loses a verdict tag, the register goes missing, or either file exceeds its size backstop.
- The register is not auto-refreshed; it goes mildly stale between manual syntheses (acceptable — full history is always in `lessons-learned.md`). Automating register re-synthesis is a deferred follow-up.
- `plugin.yaml` + `tools/install_audit.py::_CANONICAL_TOOLS` gain the new tool (PMI-1/INST-1, additive, no VERSION change).

## Reversibility

**cheap** — the format is markdown + a self-contained audit. Reverting means removing the audit from the gate roster + plugin.yaml/install_audit and (if ever wanted) regenerating verbose rows; no data is lost because the durable detail lives in `lessons-learned.md` + the per-slice archive folders throughout.
