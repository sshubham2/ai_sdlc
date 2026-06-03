# Slices Index

Active slices live in `slices/`; completed slices in [`slices/archive/`](archive/_index.md). Cross-slice patterns: [`action-points.md`](action-points.md).

## Active

(none)

## Most recent 10

| # | Slice | Shipped | One-line summary |
|---|-------|---------|------------------|
| 103 | [slice-103-thin-vault-index-routers-and-enforce](archive/slice-103-thin-vault-index-routers-and-enforce/) | 2026-06-03 | Thin the two hot vault index routers (_index.md 319.5->4.0 KB, archive/_index.md 414.1->33.6 KB) to one-liner+pointer rows + a fail-closed tools/index_router_thinness_audit.py + a standalone bounded action-points.md register; enforce the thin-router contract that was prose-only and had silently re-bloated (ADR-093; MEPD-1 EXCLUDE). |
| 104 | [slice-104-fix-record-pick-identity-format](archive/slice-104-fix-record-pick-identity-format/) | 2026-06-02 | tools/slice_queue_writer.record_pick(picker_identity: str) f-string-renders its argument directly into the pick-log line - <slice> — picked <ts> by <picker_identity>, expecting a pre-joined "<name> <email>" string |
| 102 | [slice-102-vault-flip-readiness-tests](archive/slice-102-vault-flip-readiness-tests/) | 2026-06-02 | Slice-100 shipped tools/vault_flip_readiness_audit.py — a deterministic, fail-closed inventory that classifies every in-tree vault-location literal (architecture/…, diagnose-out/…) on the production-code surface (tools/*.py + skill-helper s |
| 101 | [slice-101-add-gate-audit-cli-exit-code-tests](archive/slice-101-add-gate-audit-cli-exit-code-tests/) | 2026-06-02 | The pipeline's value proposition is "deterministic gates catch spec rot." Eight mandatory gate audits expose that guarantee through their CLI exit code — sys.exit(main()) returning non-zero on violations — yet that exact block path is exerc |
| 100 | [slice-100-add-vault-flip-readiness-audit](archive/slice-100-add-vault-flip-readiness-audit/) | 2026-06-02 | The external-vault flip (relocate architecture/ + diagnose-out/ to a shared external store, flip the _vault_paths default, git-untrack) is now fully unblocked, but it must land atomically: every hardcoded in-tree-vault-location literal (arc |
| 99 | [slice-099-create-worktree-at-slice-pick](archive/slice-099-create-worktree-at-slice-pick/) | 2026-06-02 | BRANCH-2 (slice-066 / ADR-063) made /build-slice run in a filesystem-isolated worktree, but the worktree is not created until /build-slice — so every prior step (/slice writing the mission brief + milestone, /design-slice writing design.md |
| 98 | [slice-098-route-or-retire-git-coupled-vault-tools](archive/slice-098-route-or-retire-git-coupled-vault-tools/) | 2026-06-02 | The external-shared-vault initiative is now unblocked on write-safety (slices 094/095/097 closed all three R-32 write-safety sub-classes) |
| 97 | [slice-097-harden-skill-driven-vault-rewrites](archive/slice-097-harden-skill-driven-vault-rewrites/) | 2026-06-01 | slice-094 (VWS-1, Python-writer) and slice-095 (SVW-1, skill-driven *append*) closed two of R-32's three write-safety sub-classes; both have merged |
| 96 | [slice-096-add-slice-candidates-drift-guard](archive/slice-096-add-slice-candidates-drift-guard/) | 2026-06-01 | The OSDG-1 / mini-CAD self-hosting discipline pins every methodology skill's in-repo SKILL.md to be content-equal (modulo EOL) to its installed ~/.claude/... copy, so Claude never reads stale prose at skill runtime |
| 95 | [slice-095-harden-skill-driven-vault-writes](archive/slice-095-harden-skill-driven-vault-writes/) | 2026-06-01 | slice-093 shipped the R-32 write-safety *primitives* (_vault_write.safe_write_text / safe_append_text) and slice-094 routes the Python-tool vault writers through them (closing the Python-writer sub-class) |

Full catalog: [`archive/_index.md`](archive/_index.md).

## Cross-slice action points

The synthesized, bounded action-points register (the pattern-recognition input for `/slice` + `/critique`) lives in [`action-points.md`](action-points.md). The full per-slice lesson history is in [`../lessons-learned.md`](../lessons-learned.md). (Relocated out of this router at slice-103 / ADR-093 so it cannot re-bloat the hot index.)

