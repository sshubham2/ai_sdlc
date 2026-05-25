---
id: ADR-028
title: BC-1 canonical rule set is pinned by an all-5-rule literal-constant tracked oracle + tracked fixtures; live-file integrity is enforced by a non-opt-out deterministic full-structural-identity tool (BCI-1)
date: 2026-05-16
slice: slice-030-repair-build-checks-vault-and-harden-shippability
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-028: All-5-rule literal-constant oracle + non-opt-out full-structural-identity BCI-1

> **v3 / 030A.** v1 proposed fixture-repoint-only (BLOCKED: archive-backtest gitignored inputs unenumerated). v2 added BCI-1 but specced it rule-ID-set-only and left BC-PROJ-3/BC-GLOBAL-2 with no tracked oracle (BLOCKED: meta-M-add-2/3 + non-convergence). User chose **split**: this ADR is now the 030A core; the shippability-catalog decoupling moved to 030B and is NO LONGER claimed here. In-slice revision of an uncommitted draft (not SUP-1). Audit trail: `critique-history-v1.md`.

## Context

R-4: both `architecture/build-checks.md` and `~/.claude/build-checks.md` were truncated to only the slice-028 survivors (`BC-PROJ-3`/`BC-GLOBAL-2`), silently degrading BC-1 coverage. The entire `architecture/` vault is gitignored (`git ls-files architecture/` → 0); `~/.claude/build-checks.md` is untracked. The canonical rule set therefore had **no git-tracked oracle**: the migrated-rules tests pinned BC-PROJ-1/2/BC-GLOBAL-1 anchor tuples as literal constants, but BC-PROJ-3/BC-GLOBAL-2 (the very rules the truncation *left behind*) were pinned nowhere, and any fixture sourcing their bodies from the live file would be a circular oracle. `/reflect` Step 5b (the suspected corruptor) is LLM-executed prose with no deterministic source ([[ADR-029]]).

## Options considered

1. Un-gitignore the vault — rejected (deliberate `.gitignore:11`; scoped out).
2. Fixture-repoint only (v1) — rejected (archive-backtest gitignored inputs unenumerated; BLOCKED).
3. Fixture + rule-ID-set BCI-1 + opt-out guard (v2) — rejected (ID-set passes anchor/severity/applies_to corruption = R-4 substance; BC-PROJ-3/BC-GLOBAL-2 oracle still circular; non-convergence).
4. **All-5-rule literal-constant tracked oracle + tracked fixtures + a non-opt-out deterministic FULL-structural-identity BCI-1 gate, with the shippability-catalog decoupling split to 030B** — **chosen**. Removes the relocation surface (the catalog/archive-backtest enumeration completeness problem) from this slice entirely; delivers a bounded, fully-verifiable R-4-substance retirement.

## Decision

1. New tracked fixtures `canonical_{project,global}_checks.md` hold the full 5-rule set; schema preamble recovered from the git-tracked `tools/build_checks_audit.py` module docstring L1–63.
2. The tracked test file `tests/methodology/test_build_checks_audit.py` is the **oracle**: the migrated-rules tests retain their hard-coded literal tuple constants, **extended to also pin `applies_to` + `trigger_keywords`** for BC-PROJ-1/2/BC-GLOBAL-1 (B2), and assert the *fixture* against them (fixture = subject); a NEW test pins BC-PROJ-3 + BC-GLOBAL-2 full structural identity as literal constants. Source for BC-PROJ-3/BC-GLOBAL-2 (M1, honest framing — replaces the retracted "lossless" claim): **best-recoverable** — survived R-4's last-rule truncation but **not provably byte-lossless** (R-4's whole-file-regeneration mechanism could have subtly altered the survivor); cross-corroborated against the slice-028 promotion record (`reflection.md` L16/L43 — prose only, not the structural body; the dual-review's "from slice-028 archive" mandate is unmeetable, hence the cross-corroborated surviving live body is the best available origin). Residual (no pre-R-4 byte-tracked oracle for any rule's lost/uncertain fields) is accepted because BCI-1 makes any *future* drift loud at a non-opt-out gate. Once authored, the test-file literal constant is itself the git-tracked oracle (`tests/` is tracked; the gitignored `architecture/slices/archive/` is best-effort recovery *input*, NOT a tracked oracle). Chain: `live ← fixture ← literal-constant tracked oracle`, closed for **all five** rules; recovery-input residual named, not hidden.
3. `tools/build_checks_integrity.py` (BCI-1) asserts, per rule, **full structural identity** `(rule_id, severity, applies_to, trigger_keywords, trigger_anchors, negative_anchors)` + non-empty `check` of live vs fixture — never rule-ID-set-only. Absent global file ⇒ WARN (non-HALT); present-and-non-conformant incl. empty ⇒ HALT with the attributed reconstruction message. Wired non-opt-out at `/build-slice` pre-finish + a fail-loud `/reflect` Step 5b post-write instruction.
4. The shippability-row #5/#8/#12 (and cited `test_methodology_changelog.py`) decoupling + archive-backtest fidelity are **NOT in this slice** (→ 030B). This ADR makes no decoupling claim.

`tools/build_checks_audit.py`/`_parse_rules`/BC-1 semantics are unchanged (BCI-1 uses it read-only).

## Consequences

- R-4's substance retired: silent BC-1 degradation cannot recur — BCI-1 catches any live↔canonical structural drift (anchors, severity, applies_to, keywords, empty check) loud at a non-opt-out gate + Step5b, attributed and with a reconstruction path. "Corruption is loud" is accurate (M2 fixed) because the check is full-structural-identity, not ID-set.
- The canonical set (all 5 rules incl. the survivors) has a durable git-tracked literal-constant oracle independent of the suspect live file (meta-M-add-3 closed).
- Manual fixture→live reconstruction runbook with no automated executor — an ongoing process cost (m2), mitigated by BCI-1 making any drift loud.
- Residual (→ 030B, accepted seam): shippability rows #5/#8/#12 still flip on local drift; the false-PCA-1-HALT *window* is narrowed (drift caught loud at next `/build-slice`/`/reflect`) but not eliminated until 030B decouples them.
- New tool ⇒ propagation (install_audit `_CANONICAL_TOOLS`, `test_utf8_stdout_regression._ROOT_ONLY_TOOLS`, plugin.yaml/PMI-1/atomic VERSION, methodology-changelog) — file-locations corrected per meta-M2 in design.md's checklist.

## Reversibility

**Cheap.** Revert = delete 2 fixtures + 1 tool + the new literal-constant test + the BCI-1 regression test; un-repoint the tuple tests; remove BCI-1 wiring from 2 SKILL.md files + plugin.yaml. No parser/contract/schema/data/external/runtime change; single developer; no migration. 030B layers on 030A with no 030A rollback.
