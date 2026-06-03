# Reflection: Slice 103 thin-vault-index-routers-and-enforce

**Date**: 2026-06-03
**Shipped**: YES

## Validated
- The "thin" contract was prose-only-enforced and had silently re-bloated to 319.5 KB / 414.1 KB — validated by running the new audit against the real files: **121 violations** on the bloated files, **0** on the thinned (4.0 KB / 33.6 KB). The audit IS the missing enforcement.
- The dual-Critic B1 fix (standalone `action-points.md`) is structurally sound — validated by `index_router_thinness_audit` targeting it directly + the regen path (archive/reflect Step 6) physically never touching it. Preservation is now structural, not a prose directive (which is exactly the root cause this slice closes).
- Region-anchored parsing survives the real adversarial markdown — validated by execution against 914-CRLF `_index.md`, the heading-less archive catalog, inline pipes in code spans, and the fence-in-register fixture.

## Corrected
- This slice's own `design.md` first draft kept the register IN `_index.md` "preserved verbatim across regen (in prose)" — corrected to a standalone `action-points.md` after `/critique` B1 showed the cited `write_slice_queue` pattern is CODE, not prose (the design's own root-cause applied to itself). Updated `design.md` + ADR-093 (Critique amendment, pre-acceptance).
- The meta-Critic's claim that `slice`+`pulse` are not OSDG-1-guarded was wrong — corrected during build: `slice`/`critique`/`reflect`/`pulse` ALL carry drift tests; all four installed copies were forward-synced.

## Discovered
- **R-35 (index-router-bloat drift class)** — the "thin router" contract asserted in `skills/archive/SKILL.md` prose was enforced by nothing, so the two hot routers silently re-bloated on every `/reflect`→`/archive` regeneration (319.5 KB / 414.1 KB; AP-3 "should-be-a-check" recurred). DISCOVERED-AND-RETIRED this slice — `tools/index_router_thinness_audit.py` (ADR-093, shippability #111) makes re-bloat fail the slice-finish gate. Added to risk-register as R-35 (retired).
- **D1 — a real past `/reflect`-omission**: slices 063 and 073 had their lessons appended to `_index.md`'s "Aggregated lessons" but NOT to `lessons-learned.md` (no `## Slice 063/073` heading), making those lessons **sole-copy** in the very file this slice deletes. The AC2 data-loss orphan-diff caught it; the 6+8 distinctive bullets were ported to `lessons-learned.md` before the cut. Impact: the must-not-defer prevented real data loss; the updated `/reflect` spec (lessons → `lessons-learned.md`; `_index.md` carries only a pointer) reduces this class going forward.

## Deferred
- Automating `action-points.md` re-synthesis on each archival — out of scope per the mission brief; a future slice if the register staleness becomes a problem (full history is always in `lessons-learned.md`).
- Thinning the cold append-only ledgers (changelog, risk-register, shippability, calibration-log, drift-log, build-checks) — deliberately out of scope; they are audit trails, a separate riskier question.
- code-review m3 (`AuditResult.repo_root == ""` in fixture mode) — OVERRIDDEN as cosmetic; lands nowhere.

## Critic calibration

Design-Critic (`critique.md`) + meta-Critic (`critique-review.md`) + code-Critic (`code-review.md`), per the TRI-1 dispositions + reality:

- **B1** (prose-preservation circularity): **VALIDATED** — ACCEPTED-FIXED; the standalone-file fix removed the LLM from the preservation loop; the regen path provably never touches it.
- **M1** (AC4 "gate roster" wording / MEPD-1): **VALIDATED** — ACCEPTED-FIXED; shippability-only wiring stands, no VERSION bump (PMI-1/MCFS-1/AVFS-1/TVFS-1 all PASS).
- **M2** (data-loss, no mechanism): **VALIDATED** — ACCEPTED-PENDING; reality confirmed HARD — the orphan-diff found slices 063/073 genuinely sole-copy. The single most valuable finding of the slice.
- **M3** (heading-less archive anchor): **VALIDATED** — ACCEPTED-FIXED; the archive catalog genuinely has no `## ` heading; the explicit pipe-block anchor + negative fixture were needed.
- **M4** (SVW-1/OSDG-1 on regen edits): **VALIDATED** — ACCEPTED-PENDING; SVW-1 caught my OWN archive:182 edit (a negative directive read as an unrouted mutation).
- **M5** (flip-readiness on the new tool): **VALIDATED** — ACCEPTED-PENDING; the new tool is a genuine 15th VAULT_ROOT importer; flip-readiness `--strict` clean.
- **M-add-1** (meta-Critic — orphaned reader prose): **VALIDATED** — the readers WERE orphaned; `slice`/`critique`/`pulse` repointed. The reader/writer asymmetry the meta-Critic named was real, and the B1 fix made it larger (adopting the very Option-2 the ADR had rejected).
- **m1** (recent-10 = 20 rows): **VALIDATED**. **m2** (fence mis-stated): **VALIDATED** — the meta-Critic correctly re-stated it; a naive substring fence-grep WOULD have false-positived (the slice-099/100 anti-pattern). **m3** (cap headroom): **VALIDATED** — 500 was needed (longest real row 428).
- **code-review M1** (fail-OPEN empty-region): **VALIDATED** — executed PROBE6 confirmed a heading-without-table passed silently; fixed fail-closed with a fresh-project carve-out.
- **code-review M2** (whole-line verdict scan = RSAD-1): **VALIDATED** — the slice's own detector violated the slice's own AP-1 `marker in line_text` rule; fixed leading-anchored.

**Missed by Critics**: the design-Critic + meta-Critic stack MISSED both code-review M1 (fail-OPEN) and M2 (whole-line scan) — execution-level defects the design stack structurally cannot reach (it reads design.md/ADRs, not the `.py`). The slice-100 lesson ("the code-Critic is mandatory for a new AST/parser/classifier tool") recurred, N+1. Also MISSED by every Critic layer: the new-public-tool **inventory fan-out** — adding one tool tripped 6 inventory-pin tests (migration-allowlist + importer-count + cp1252-coverage + 2 INSTALL-count `*_tool_inventory.py` + INSTALL.md L22/L166), all caught only by the full suite. The slice-100 fan-out lesson recurred, N+1.

**Pattern**: the 3-Critic stack stayed non-overlapping + zero-false-alarm again — design-Critic (B1 architecture), meta-Critic (M-add-1 consumer-contract), code-Critic (M1/M2 execution). Do NOT collapse the stack on a new-parser-tool slice.

## Lessons for next slice
- **Before a destructive cut of an aggregate file, run a programmatic orphan-diff against the durable store** — the must-not-defer "no lesson is sole-copy" caught a real past `/reflect`-omission (063/073). A "verify-no-data-loss-before-cut" build-check is a strong candidate (it just earned its keep with real data).
- **The new-public-tool inventory fan-out is wider than any checklist (N+1 on slice-100)** — adding a `tools/*.py` ripples into the migration-allowlist, the VAULT_ROOT-importer count, the cp1252-coverage list, AND every hardcoded INSTALL.md tool-count literal in `tests/methodology/test_*_tool_inventory.py`. Grep EVERY count literal across `tests/` on a new tool.
- **A negative directive in SKILL.md prose (`DO NOT regenerate X`) trips SVW-1** — the negation lexicon knows `never`/`don't`, not `DO NOT`; reword a non-mutation constraint with a non-mutation verb (`stays`/`carries`/`leaves`) so the lexical audit doesn't read it as an unrouted mutation site.
- **A region-anchored parser must distinguish "structure absent" (fail-closed) from "structure present, 0 rows" (legitimately empty)** — code-review M1: flagging an empty-but-present table would false-fail a greenfield adopter's slice-1.

## Vault updates made (thin vault)
- [[risk-register.md]] — added R-35 (index-router-bloat drift class; retired by ADR-093 + the audit).
- [[lessons-learned.md]] — slice-103 entry (Step 5) + the earlier 063/073 back-fill (M2).
- This slice's [[design.md]] + [[decisions/ADR-093]] — register relocated to standalone `action-points.md` (B1 amendment).
- [[shippability.md]] — row #111 (added at build).
- [[skills/archive/SKILL.md]] + [[skills/reflect/SKILL.md]] + [[skills/slice/SKILL.md]] + [[skills/critique/SKILL.md]] + [[skills/pulse/SKILL.md]] — thin-router spec.
