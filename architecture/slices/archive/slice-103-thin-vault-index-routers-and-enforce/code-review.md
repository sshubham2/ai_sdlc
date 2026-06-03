# Code Review: Slice 103 thin-vault-index-routers-and-enforce

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-06-03
**Result**: FINDINGS (0 Blockers / 2 Majors / 3 Minors) — all Majors + m1/m2 ADDRESSED-IN-SLICE; m3 OVERRIDDEN (cosmetic)

## Summary
A clean, well-tested slice. The code-Critic executed the parsers against the real CRLF tree + adversarial fixtures (PROBE-driven). It found two real defects — both ADDRESSED in-slice: a fail-OPEN hole where a region heading present but no table beneath it passed silently (M1, contradicting the design's fail-closed promise), and a whole-line verdict-tag scan that re-introduced the `marker in line_text` anti-pattern AP-1 itself warns against (M2). All inventory wiring (PMI-1/INST-1/flip-readiness/SVW-1/OSDG-1) verified clean.

## Changed files (in-scope)
```
INSTALL.md
architecture/slices/action-points.md
architecture/slices/slice-103-thin-vault-index-routers-and-enforce/build-log.md
plugin.yaml
skills/{archive,critique,pulse,reflect,slice}/SKILL.md
tests/methodology/{test_external_vault_adr_and_risk,test_index_router_thinness_audit,test_pulse_worktree_resolver_tool_inventory,test_stranded_slice_audit_tool_inventory,test_utf8_stdout_regression,test_vault_root_constant}.py
tools/index_router_thinness_audit.py
tools/install_audit.py
```

## Findings

### Blockers
None.

### Majors

#### M1: Fail-OPEN — a `## Most recent 10` heading present but NO table beneath it passed silently (contradicts the fail-closed contract)
- **Issue**: `check_recent_10` fired `recent-10-section-missing` only when the heading was ABSENT; a heading present with a pointer/prose but no table → `_data_rows_after` returned `[]`, `0 > 10` False, returned `(0, [])` clean. The regen-failure mode the slice exists to catch (regen emits heading + pointer, loses the table) passed the gate. (`check_archive_catalog` header-None was already caught.)
- **Builder response**: **ACCEPTED-FIXED**. `_data_rows_after` now returns `(table_header_found, rows)`; `check_recent_10` fails closed when `not found_header` (`tools/index_router_thinness_audit.py`). **Boundary**: a present-but-empty table (header + separator + 0 rows) is a LEGITIMATE fresh-project state (0 archived slices) and is deliberately NOT flagged — only a wholly-absent table is fail-closed (else the audit would false-fail a greenfield adopter's slice-1). Two paired tests added: `test_recent10_heading_without_table_is_fail_closed` (the PROBE6 case → violation) + `test_recent10_empty_table_with_header_is_clean` (fresh-project boundary → clean).

#### M2: `_VERDICT_TAG_RE` whole-line scan re-introduced the `marker in line_text` anti-pattern — a future descriptive re-synthesis self-trips `register-untagged`
- **Issue**: the verdict-tag check counted EVERY `[valid-verdict]` substring on the entry line (incl. inside a markdown link / inline code / a descriptive prose mention). An entry with one leading tag + a bracketed verdict word later in its prose → `len(tags) == 2` → false-fail. The register is explicitly RE-SYNTHESIZED periodically (design §maintenance), so the next descriptive synthesis self-trips the gate. This is the same line-text-substring class as AP-1's own rule (slice-099/100, N=4) — RSAD-1: the slice's own detector violated the slice's own register entry.
- **Builder response**: **ACCEPTED-FIXED**. Replaced `_VERDICT_TAG_RE` (whole-line) with `_AP_LEADING_TAG_RE` anchored to the leading `- **AP-n** [verdict]` position; `check_register` validates the single leading captured token. Paired tests: `test_register_descriptive_bracketed_verdict_in_prose_is_clean` (PROBE2 — leading tag + `[cultural]`/`[the doc](already-a-gate)`/`` `[critic-calibrate-probe]` `` in prose → clean) + `test_register_non_leading_tag_is_untagged`.

### Minors

#### m1: `str.splitlines()` splits on exotic Unicode boundaries (`\v \f U+2028 …`) — a row with one could evade the per-row cap
- **Builder response**: **ACCEPTED-FIXED**. Added `_lines()` (split on `\n` + `rstrip("\r")` only) replacing the 3 `splitlines()` calls; CRLF-aware, no exotic-boundary splitting. Test `test_exotic_unicode_boundary_row_still_capped` (a 601-char row with an embedded `chr(0x2028)` is measured as ONE >500 row → flagged; `splitlines()` would have fragmented it under-cap). Low likelihood + byte-backstop mitigated, but cheap to close exactly.

#### m2: archive catalog has no row-COUNT bound — only per-row + byte backstop
- **Builder response**: **ACCEPTED-FIXED (documented intent)**. This is intentional — the archive catalog is a newest-first chronological ledger that grows by one thin row per slice (unlike the fixed-window recent-10). Added a comment in `check_archive_catalog` noting the deliberate absence of `_MAX_ARCHIVE_ROWS` (only per-row cap + `_MAX_ARCHIVE_BYTES` apply).

#### m3: `AuditResult.repo_root == ""` in explicit-path (test) mode — cosmetic JSON field
- **Builder response**: **OVERRIDDEN** — purely cosmetic (no functional impact; loci use explicit path labels; no consumer reads `repo_root` from the JSON in fixture mode). Not worth the change.

## Dimensions checked
- [x] Unfounded assumptions — M1 (docstring/shippability "fail-closed on unparseable table" contradicted by empty-table silent-pass) + m1 (test docstring `splitlines()` claim). Reader/writer prose claims verified TRUE by execution (vault_edit-rewrite routing retained in archive/reflect; readers repointed; the 2 remaining "Aggregated lessons" mentions are deliberate root-cause / negative prose). No phantom imports.
- [x] Missing edge cases — M1 (empty table under valid heading) + m1 (Unicode boundaries). CRLF verified clean; boundary cases (11 rows, 25 entries, section-bleed, prose-pipe-outside-table, fence-in-register, no-separator) verified correct by probe.
- [x] Over-engineering — none.
- [x] Under-engineering — M1 (AC4/design fail-closed promise not delivered on the empty-table path) — fixed.
- [x] Contract gaps — none material (CLI exit 0/1/2 + --json implemented + tested).
- [x] Security — none (reads 3 repo-local md via VAULT_ROOT; no shell=True/eval/secrets).
- [x] Drift from vault — M1 (impl drifted from design.md fail-closed claim) — fixed. M5 verified (no bare `architecture` literal; flip-readiness --strict clean). Inventory drift clean (plugin.yaml ADR-093, _CANONICAL_TOOLS alphabetical, 41 tools, INSTALL count 41, MEPD-1 EXCLUDE — no VERSION bump).
- [x] Web-known issues — none (argparse/re/pathlib.parents/json/dataclasses stable 3.13). Only the `splitlines()` Unicode-breadth note → m1.
- [x] Cross-cutting conformance — M2 (RSAD-1: the slice's own verdict detector violated its own AP-1 `marker in line_text` rule) — fixed. APED-1: parsers executed against the real CRLF tree + adversarial battery; the two missed variants (empty-region M1, double-verdict-prose M2) are now covered by added tests, closing the APED-1 completeness gap. EOL-DRIFT-1: no new byte-equality `==` on .md content (measures lengths/counts). SSoT: SKILL.md prose cites constants by name; values match the module — consistent.
