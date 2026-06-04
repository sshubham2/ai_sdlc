# Slices Index

Active slices live in `slices/`; completed slices in [`slices/archive/`](archive/_index.md). Cross-slice patterns: [`action-points.md`](action-points.md).

## Active

(none)

## Most recent 10

| # | Slice | Shipped | One-line summary |
|---|-------|---------|------------------|
| 111 | [slice-111-route-in-loop-skill-vault-ops-via-seam](archive/slice-111-route-in-loop-skill-vault-ops-via-seam/) | 2026-06-04 | Phase-2 flip prep: routes the remaining unambiguous in-loop skill vault write-ops via the `vault_edit` seam (archive `mv`→`vault_edit move`; drift-log→`append`) + an in-loop-scoped 4-class op-gate (`--op-gate`, ADR-104/ADR-102) failing-closed on un-routed writes. M1 318→313 re-pin; ADR-103/104; MEPD-1 EXCLUDE; R-32 mitigating (R-32.a/.b → flip). |
| 110 | [slice-110-make-pipeline-vault-location-agnostic](archive/slice-110-make-pipeline-vault-location-agnostic/) | 2026-06-04 | Phase-1 external-vault flip prep: makes the test suite vault-location-agnostic so a future config-only flip is suite-neutral. Shared `tests/_vault_isolation.py` helper (setattr-pin, NOT reload — ADR-101) re-points 85 location breakers across 28 files; suite byte-identical default ≡ seeded-external flip-sim. AC2/3/4 deferred to Phase-2 follow-on. |
| 109 | [slice-109-add-post-flip-vault-conflict-safety](archive/slice-109-add-post-flip-vault-conflict-safety/) | 2026-06-04 | Routes the 3 queue/claim read-modify-write writers through the CAS channel (`safe_rewrite_text`) under a bounded fail-visible retry — the post-flip `_vault_write`-lock substitute for PCR's git-merge queue reconciliation. Closes R-32's last pre-move residual; barrier-synced 0-lost proof; capability-without-flip. ADR-098; MEPD-1 EXCLUDE. |
| 108 | [slice-108-add-fbcd-1-cardinality-fanout-sub-mode](archive/slice-108-add-fbcd-1-cardinality-fanout-sub-mode/) | 2026-06-03 | Extends FBCD-1 (Dim-9, `agents/critique.md`) with **sub-mode (c)**: on a counted-set cardinality change the design-Critic greps the WHOLE repo for sibling `== N` count pins (not just slice-authoring files), flagging a membership-pin-only plan as a Major (AP-10; slices 089/100/103/106). FBCD-1 v1.1; full 0.82.0→0.83.0 cascade. |
| 107 | [slice-107-inventory-vault-flip-prose-surface](archive/slice-107-inventory-vault-flip-prose-surface/) | 2026-06-03 | Ships tools/vault_flip_prose_inventory.py — the M4 vault-flip's THIRD surface (prose), after slice-100/102. Enumerates + classifies all 318 architecture/+diagnose-out/ prose literals (skills/agents/CLAUDE.md/INSTALL.md/README.md) → 318 rewrite-at-flip; boundary-free re.finditer + SHA-256 baseline + --strict gate; disjoint from slice-106 (AC5). BC-PROJ-17 promoted. |
| 106 | [slice-106-route-project-frame-synth-via-vault-root](archive/slice-106-route-project-frame-synth-via-vault-root/) | 2026-06-03 | Routes the last 4 production `must-rewrite` vault reads (concept/triage/slice-queue/risk-register) in `tools/project_frame_synth.py` through the `VAULT_ROOT` seam — vault-flip readiness production surface 4→0, the M1 production cut of the external-vault flip. Zero behavior change today; MEPD-1 EXCLUDE (no ADR / no VERSION bump). |
| 105 | [slice-105-decouple-slice-loop-from-diagnose-out](archive/slice-105-decouple-slice-loop-from-diagnose-out/) | 2026-06-03 | Fully decouples the AI SDLC slice loop from `diagnose-out/` in both directions: retires the worktree derived-dir seed (ADR-094 — `seed_derived_dirs`/`_DERIVED_DIRS` gone; no skill seeds/`cp -r`s; R-20 fully closed) and redefines BCR-1 consume-only (ADR-095 — `/reflect` round-trip-write retired, `/slice` source-#7 consult kept). v0.82.0; BC-PROJ-16 promoted. |
| 103 | [slice-103-thin-vault-index-routers-and-enforce](archive/slice-103-thin-vault-index-routers-and-enforce/) | 2026-06-03 | Thin the two hot vault index routers (_index.md 319.5->4.0 KB, archive/_index.md 414.1->33.6 KB) to one-liner+pointer rows + a fail-closed tools/index_router_thinness_audit.py + a standalone bounded action-points.md register; enforce the thin-router contract that was prose-only and had silently re-bloated (ADR-093; MEPD-1 EXCLUDE). |
| 104 | [slice-104-fix-record-pick-identity-format](archive/slice-104-fix-record-pick-identity-format/) | 2026-06-02 | tools/slice_queue_writer.record_pick(picker_identity: str) f-string-renders its argument directly into the pick-log line - <slice> — picked <ts> by <picker_identity>, expecting a pre-joined "<name> <email>" string |
| 102 | [slice-102-vault-flip-readiness-tests](archive/slice-102-vault-flip-readiness-tests/) | 2026-06-02 | Slice-100 shipped tools/vault_flip_readiness_audit.py — a deterministic, fail-closed inventory that classifies every in-tree vault-location literal (architecture/…, diagnose-out/…) on the production-code surface (tools/*.py + skill-helper s |
Full catalog: [`archive/_index.md`](archive/_index.md).

## Cross-slice action points

The synthesized, bounded action-points register (the pattern-recognition input for `/slice` + `/critique`) lives in [`action-points.md`](action-points.md). The full per-slice lesson history is in [`../lessons-learned.md`](../lessons-learned.md). (Relocated out of this router at slice-103 / ADR-093 so it cannot re-bloat the hot index.)
