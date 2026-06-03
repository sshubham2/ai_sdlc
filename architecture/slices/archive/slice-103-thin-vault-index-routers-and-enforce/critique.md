# Critique: Slice 103 thin-vault-index-routers-and-enforce

**Critic reviewed**: mission-brief.md, design.md, ADR-093, project-frame.md
**Date**: 2026-06-03
**Result**: NEEDS-FIXES

## Summary
The core idea is sound and the char-cap is genuinely non-vacuous against real data (longest lines today 13,871 / 2,289 chars vs a 400 cap). But three load-bearing claims are under-specified or contradict the vault: (1) "preserve the register verbatim across regen" is prose-to-an-LLM — the exact failure mode that caused the bloat, and unlike the `slice_queue_writer` pattern it cites, there is no code that extracts/re-splices the register; (2) MEPD-1 EXCLUDE collides with the changelog's INCLUDE convention for "new audit-enforced gate wired into the Step-6 roster", and AC4's "gate roster" wording is inconsistent with the shippability-only wiring the design chose; (3) the AC2 data-loss check verifies 542 lessons with no programmatic mechanism. Plus parser-robustness edge cases.

## Findings

### Blockers (must address before /build-slice)

#### B1: "Preserve the register verbatim across regen" is unenforceable prose — the same failure mode that caused the bloat
- **Claim under review**: design.md / ADR-093 — the register is "preserved-across-regen ... the `write_slice_queue` pick-log-tail pattern, applied **in prose** to the register section."
- **Issue**: The `write_slice_queue` pick-log-tail pattern is **code** (`tools/slice_queue_writer.py:127 _PICK_LOG_BLOCK_RE`, `:727 _extract_pick_log_block`, `:658-660` re-append) — no LLM in the loop. This slice's `_index.md` regen goes through a **Haiku subagent** (`skills/archive/SKILL.md:60-68`) + main-thread `vault_edit rewrite`. "Preserve the register verbatim" is a natural-language directive to that pipeline — exactly the prose-not-enforced root cause ADR-093 itself diagnoses. The `register-missing` check catches total loss, but NOT silent entry-dropping or content rewrite within the 1≤n≤25 bound.
- **Evidence**: `tools/slice_queue_writer.py:120-133, 658-660, 727`; `skills/archive/SKILL.md:60-68`; `skills/reflect/SKILL.md:321`; ADR-093 self-diagnosed root cause.
- **Proposed fix**: (a) code the extraction/re-splice as a deterministic helper; OR (b) move the register to a separate `architecture/slices/action-points.md` linked from `_index.md` so the regen physically cannot clobber it (ADR-093's rejected Option 2); OR (c) prose-only + downgrade the claim + follow-up + residual risk.
- **Builder draft**: **ACCEPTED-FIXED** — adopt fix (b): the register moves to a standalone `architecture/slices/action-points.md` (linked from `_index.md`); `/reflect`+`/archive` regen never touch it (the Haiku/`vault_edit rewrite` path only rewrites `_index.md`'s Active+recent-10 + prepends to `archive/_index.md`), so it is robust by construction, not by prose. The audit targets `action-points.md` for the ≤25 + verdict-tag checks. `/slice`+`/critique` read `action-points.md` for pattern-recognition (one extra read; they already read multiple vault files). Will update design.md + ADR-093 (flip Option 2 from "deferred" to "chosen") + AC2 on user ratification.

### Majors (address this slice)

#### M1: MEPD-1 EXCLUDE vs the changelog's INCLUDE-for-gate convention; AC4 "gate roster" wording contradicts shippability-only wiring
- **Issue**: `methodology-changelog.md:51,69` reserves "audit-enforced gate wired into the Step-6 roster" for INCLUDE+RULE-ID+VERSION bump (VWS-1/SVW-1). slice-100's flip-readiness audit was EXCLUDE because it is shippability-only (NOT in `skills/build-slice/SKILL.md:181-199` Step-6 roster). The design chose shippability-only wiring — consistent with EXCLUDE — but AC4/mission-brief say "wired into the slice-finish **gate roster**", the phrase reserved for the Step-6/INCLUDE case.
- **Evidence**: `methodology-changelog.md:51,69`; `skills/build-slice/SKILL.md:181-199`; design Wiring matrix; shippability row 108 (slice-100 EXCLUDE precedent).
- **Proposed fix**: Pick a lane and make AC4+design+ADR consistent.
- **Builder draft**: **ACCEPTED-FIXED** — keep shippability-only (matches slice-100, lighter); reword mission-brief AC4 + design from "wired into the slice-finish gate roster" → "added as an `architecture/shippability.md` regression-catalog row (RPCD-1/SCPD-1), run at `/validate-slice` pre-finish; NO Step-6 `####` roster entry." MEPD-1 EXCLUDE then stands. Will apply on ratification (TPHD-1: harmonize the AC wording across mission-brief + design in the same edit).

#### M2: Data-loss verification (AC2 must-not-defer) over 542 lessons has no specified mechanism
- **Issue**: The "Aggregated lessons" region holds **542** bullets; "verify every lesson is in `lessons-learned.md`" by hand is infeasible → silently becomes "spot-checked a few."
- **Evidence**: 542 bullets (awk); `lessons-learned.md` 2,141 lines; sample-match confirmed, no full diff.
- **Proposed fix**: A throwaway build script: extract each aggregated bullet's normalized text, assert a substring/fuzzy match in `lessons-learned.md`, report orphans; capture orphan-count=0 as AC2 evidence; port any orphans into `lessons-learned.md` BEFORE cutting.
- **Builder draft**: **ACCEPTED-PENDING** — specify this orphan-diff mechanism in the design build plan now; execute it at `/build-slice` and quote the output (orphan count) in validation.md as AC2 evidence; port orphans before the cut if any.

#### M3: `archive/_index.md` region-anchoring is undefined — the file has NO `## ` heading
- **Issue**: `_index.md` anchors on `## Most recent 10`, but `archive/_index.md` is H1 + prose + one table, no `## ` headings. The design demands "region-anchored, not whole-file token scan" but never states the archive-catalog anchor; a bare `^\|` filter is effectively a whole-file pipe-scan (fine today, fragile if intro prose ever contains a pipe).
- **Evidence**: `archive/_index.md` L1-6 (no `## `); mission-brief Must-not-defer (slice-099/100 N=4).
- **Proposed fix**: Specify the anchor: "the contiguous block of `^\|` lines following the `| # | Slice | Shipped | ... |` header row, terminated at the first non-pipe line or EOF; header + `|---|` separator excluded." Add a fixture test where a `|`-containing prose line OUTSIDE the table is NOT counted.
- **Builder draft**: **ACCEPTED-FIXED** — add the precise archive-catalog anchor spec to design.md + the negative fixture test to the test plan. Folds in the Critic's APED-1 build-time obligation (below). Apply on ratification.

#### M4: Editing reflect/archive regen prose risks breaking SVW-1 routing + OSDG-1 — not addressed
- **Issue**: `skills/reflect/SKILL.md:321` (the edited line) carries the SVW-1 `vault_edit rewrite` route token for `_index.md` (a shared-aggregate, `:143`); the prose rewrite must retain it or `skill_vault_write_safety_audit` fires `channel-mismatch`/unrouted at Step 6. Same for `skills/archive/SKILL.md:65,76`. `reflect` is OSDG-1-guarded (forward-sync, EOL-normalized).
- **Evidence**: `skills/reflect/SKILL.md:143,321`; SVW-1 audit clean today; `tests/methodology/test_reflect_skill_drift.py`.
- **Proposed fix**: Build-plan note: retain `vault_edit rewrite` (CAS) routing for both index files through the edits; run `$PY -m tools.skill_vault_write_safety_audit` (exit 0) + forward-sync `~/.claude/skills/reflect/SKILL.md`.
- **Builder draft**: **ACCEPTED-PENDING** — add the explicit SVW-1-retention + OSDG-1-forward-sync obligations to the design build plan now; execute + verify at `/build-slice` (skill_vault_write_safety_audit exit 0; reflect drift test green).

#### M5: New tool must satisfy the slice-100/102 vault-flip-readiness audit — no un-routed `architecture` literal
- **Issue**: `vault_flip_readiness_audit` globs ALL `tools/**/*.py`; an un-routed bare-`"architecture"` path literal classifies `must-rewrite-before-flip` and trips the AC3 baseline pin (shippability 108/109, run at validate). The design asserts VAULT_ROOT routing but doesn't call out flip-readiness as a gate the new tool must pass.
- **Evidence**: shippability 108/109; `tools/_vault_paths.py` VAULT_ROOT; slice-100/102 lineage.
- **Proposed fix**: Build-plan note: route all vault paths via `VAULT_ROOT` subpaths; after creating the tool run `$PY -m tools.vault_flip_readiness_audit --strict`, confirm zero NEW `must-rewrite`/`needs-human`; any doc/error-message `architecture` literal carries the slice-068 two-marker comment.
- **Builder draft**: **ACCEPTED-PENDING** — add the flip-readiness build-time obligation to design; execute + verify at `/build-slice`.

### Minors (log; address if cheap)

#### m1: Recent-10 currently has 20 data rows, not 10 — thinning must also fix the count
- **Issue**: `## Most recent 10` holds **20** rows (082-102). AC1 caps per-row chars but not count → 20 thin rows would pass yet violate the section's name.
- **Builder draft**: **ACCEPTED-FIXED** — AC1/design state the thinned recent-10 is exactly the 10 most recent rows; the audit gains a cheap `recent-10-too-many` check (count ≤ 10). Apply on ratification.

#### m2: A code fence lives inside the cut region — confirm no dangling fence
- **Issue**: `_index.md:286` (in the cut region) has a `` ``` `` fence; ensure the wholesale replacement strands no half-fence (the SVW-1 fence tracker, slice-095 m1).
- **Builder draft**: **ACCEPTED-PENDING** — build-time: after cutting, grep the new `_index.md` + `action-points.md` for balanced fences; confirm fence-free.

#### m3: Char cap 400 — confirm headroom against the WORST legitimate thin row
- **Issue**: longest folder name (`slice-089-make-commit-slice-stale-branch-check-parallel-slice-aware`, 64 chars) appears twice in the link (text+href) ≈ 140 chars + intent; a 64-char intent ≈ 280, a longer one could approach 400.
- **Builder draft**: **ACCEPTED-FIXED** — raise `_MAX_ROW_CHARS` to **500** (still ~5x below today's 1,250–13,871 bloat; safe headroom for the worst folder-name + a full one-liner). Apply on ratification.

## Dimensions checked
- [x] Unfounded assumptions — B1 (register "preserved by prose" citing a code pattern), M2 (data-loss "verify every lesson" with no mechanism), M5 (VAULT_ROOT flip-safety asserted, not gated).
- [x] Missing edge cases — M3 (archive file has no `## ` heading), m1 (recent-10 is 20 rows), m2 (fence inside cut region), m3 (worst-case folder-name vs cap). Concurrency: regen already uses `vault_edit rewrite` CAS — covered.
- [x] Over-engineering — none. Size-backstop + constants-as-SSoT are justified, not gold-plating.
- [x] Under-engineering — M1 (AC4 asks for a gate-roster entry the design doesn't deliver), B1 (register-preservation AC has no enforcement element). TF-1 N/A; paired test + mutation non-vacuity satisfy "non-vacuity by mutation".
- [x] Contract gaps — M1 (audit role gate-roster vs shippability ambiguous; exit-code 0/1/2 + --json is fine). `register-missing` fail-closed specified; the gap is what the audit does NOT catch (entry-dropping in bound) — B1.
- [x] Security — none. Local audit + vault edits; no auth/input/secrets surface.
- [x] Drift from vault — M1 (MEPD-1 EXCLUDE vs changelog INCLUDE-for-gate), M4 (SVW-1 + OSDG-1 drift on edited regen lines), M5 (slice-100/102 flip-readiness consumes the new tool). ADR-093 additive (supersedes: null), reuses ADR-085/088 correctly.
- [x] Web-known issues — GFM pipe-in-inline-code ambiguity (a `|` inside backticks is a column delimiter unless escaped) does NOT break the design because the audit uses a physical-line char cap, not column counting. Logged as confirmation, not a finding. Sources: github.github.com/gfm, github/markup#1078.
- [x] Cross-cutting conformance — **APED-1**: the region-anchored parser runs over adversarial markdown (914 CRLF in `_index.md`, em-dashes, inline pipes in code spans, a fence at L286, multi-table, heading-less archive) — design-time reasoning is insufficient; the build MUST execute the parser against (a) real CRLF `_index.md`, (b) heading-less `archive/_index.md`, (c) a `|`-prose-line-outside-table fixture, (d) a fence-in-register fixture, quoting output in validation.md (folded into M3). **MEPD-1**: correctly branch (b) documented-why-none (EXCLUDE) — but the rationale rests on slice-100 which M1 shows diverges from the changelog INCLUDE convention; reconcile per M1. **RSAD-1**: the slice's own design/mission-brief are large-but-bounded, not in the audited routers — no self-violation. **PTFCD-1**: confirm `tests/methodology/test_index_router_thinness_audit.py` + cited functions exist before the shippability row goes live.

## Dual review (DR-1)

A second meta-Critic pass (`critique-review.md`, verdict **EXTEND**) confirmed B1 + M1–M5 + m1/m3 as VALID with correct severities, re-stated m2 (SUSPICIOUS — `_index.md:286` is an inline triple-backtick literal, NOT a block fence; a naive substring fence-grep would false-positive), and added one missed Major:

#### M-add-1 (Major, meta-Critic): register rename/relocation orphans the READER prose
- **Issue**: The design replaces `## Aggregated lessons` with the register (+ the B1 fix moves it to a separate `action-points.md`), but four reader surfaces point at the old section by name and are NOT in the design's edit set: `skills/critique/SKILL.md:67,93-94` (incl. the Critic-input template), `skills/slice/SKILL.md:28,68,71`, `skills/pulse/SKILL.md:43,236`. Consumer-driven-contract break — after the cut, `/slice`+`/critique` read a section that no longer exists, silently degrading pattern-recognition input. Same class as M4 but on the read side; the B1 fix makes it larger (adopts the very Option-2 the ADR rejected for this reason).
- **Proposed fix**: enumerate the reader-prose edits (/slice 3 sites, /critique 2 sites incl. input-template, /pulse 2 sites) in the design scope + AC set; forward-sync `/critique` (OSDG-1-guarded — extends M4's obligation to a 2nd skill); `/slice`+`/pulse` are not OSDG-1-guarded; confirm `slice/SKILL.md:221` updates or stays a historical anchor.
- **Builder draft**: **ACCEPTED-PENDING** — accept M-add-1; enumerate the reader surfaces in design now, execute the edits + forward-syncs at `/build-slice`.

## Triage

**Triaged by**: user
**Date**: 2026-06-03
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | Move the register to a standalone `architecture/slices/action-points.md` the regen never touches — removes the LLM from the preservation loop (robust by construction, not prose). design.md + ADR-093 updated. |
| M1 | Major | ACCEPTED-FIXED | Keep shippability-only wiring; reword AC4 "wired into the slice-finish gate roster" → "added as a shippability regression-catalog row, run at /validate-slice". MEPD-1 EXCLUDE stands (meta-confirmed; no VERSION bump). |
| M2 | Major | ACCEPTED-PENDING | Orphan-diff script at /build-slice: each aggregated bullet must substring/fuzzy-match in lessons-learned.md; capture orphan-count=0 as AC2 evidence; port any orphans before the cut. |
| M3 | Major | ACCEPTED-FIXED | Specify the archive-catalog region anchor precisely (contiguous `^\|` block after the `\| # \| Slice \| ...` header, header+separator excluded, terminated at first non-pipe/EOF) + negative fixture (a `\|`-prose line outside the table not counted) + APED-1 adversarial-battery execution at build. |
| M4 | Major | ACCEPTED-PENDING | Retain the `vault_edit rewrite` (CAS) route token through the reflect/archive regen edits; run `skill_vault_write_safety_audit` (exit 0); forward-sync `~/.claude/skills/reflect/SKILL.md` (OSDG-1). |
| M5 | Major | ACCEPTED-PENDING | After creating the tool, run `vault_flip_readiness_audit --strict`; confirm zero NEW must-rewrite/needs-human; route all vault paths via VAULT_ROOT subpaths; any doc/error `architecture` literal carries the slice-068 two-marker comment. |
| M-add-1 | Major | ACCEPTED-PENDING | Edit reader prose: `skills/slice/SKILL.md` (3 sites), `skills/critique/SKILL.md` (2 sites incl. input-template), `skills/pulse/SKILL.md` (2 sites) → point at `action-points.md`; forward-sync `/critique` (OSDG-1); enumerate in design scope now, execute at build. |
| m1 | Minor | ACCEPTED-FIXED | Recent-10 thinned to exactly the 10 most recent rows; audit gains a `recent-10-too-many` count check (≤10). |
| m2 | Minor | ACCEPTED-PENDING | Re-stated per meta: post-cut fence verification uses a LINE-ANCHORED `^\`\`\`` check (NOT a substring scan, which would false-positive on the inline literal at L286 — the slice-099/100 whole-line-scan anti-pattern). |
| m3 | Minor | ACCEPTED-FIXED | Raise `_MAX_ROW_CHARS` to 500 (safe vs worst-case folder-name row; still ~3–27x below today's bloat). |
