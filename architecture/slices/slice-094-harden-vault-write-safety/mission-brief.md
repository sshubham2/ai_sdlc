# Slice 094: harden-vault-write-safety

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-32 (NARROWED — Python-tool-writer sub-class retired; high×high, score 9, reversibility expensive). R-32 is the load-bearing blocker for the external-vault flip.
**Test-first**: false  (the concurrency proof is core but the design phase may opt into TF-1; the safe primitives already exist + pass)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

slice-093 shipped the R-32 write-safety *primitives* (`tools/_vault_write.py`: `safe_write_text` = atomic `os.replace` + sidecar `.lock`; `safe_append_text` = `O_APPEND` + lock) but the ~30 `write_text` / `open(...,'w'|'a')` call sites across `tools/*.py` still write vault files directly — so R-32 stays `mitigating`, and the flip (writing a tier-2 vault-root config so two parallel slices share one vault) MUST NOT land until concurrent writes are proven safe. This slice routes the **Python-tool** vault writers through the safe primitives, ships a fail-closed completeness audit that makes a bypass impossible to merge silently, and proves no corruption under N parallel writers — narrowing R-32 to its remaining (skill-driven Write/Edit) sub-class.

## Acceptance criteria

1. Every vault-writing call site in `tools/*.py` routes through `_vault_write.safe_write_text` (whole-file rewrite class: e.g. slice-queue.md) or `safe_append_text` (append-log class: e.g. risk-register / methodology-changelog / lessons-learned) — no `tools/*.py` writes a resolved-vault-root file via raw `write_text` / `open(...,'w'|'a')`.
2. A new fail-closed completeness audit (`tools/vault_write_safety_audit.py`) statically detects any `tools/*.py` write to a vault path that bypasses the safe primitives, exits non-zero on a violation (a write it cannot classify as safe is a violation, never a silent pass), and is wired into the `/build-slice` Step-6 + `/validate-slice` gate roster.
3. A concurrency test proves no corruption under N parallel writers: N concurrent `safe_append_text` writers lose **zero** lines (the slice-093 "pure `O_APPEND` loses 26/30 lines" failure mode does not recur), and N concurrent `safe_write_text` writers never leave a torn/partial file (final content is always exactly one writer's complete payload). Non-vacuity is proven by mutation (disable the lock → test FAILs → revert).
4. R-32 is narrowed in `architecture/risk-register.md`: the Python-tool-writer sub-class is recorded retired-with-evidence; the **skill-driven Write/Edit mutation** sub-class is documented as the explicit remaining residual that still gates the flip (re-sequenced to a later slice), with a pointer to its follow-up (slice-095 candidate).
5. The no-flip safety contract is preserved: `resolve_vault_root` default is unchanged (`architecture/`), and the full test suite stays green — every existing tool/test/skill behaves identically (the routing is transparent when there is no contention).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Writers routed | `$PY -m tools.vault_write_safety_audit --repo-root .` exits 0; grep confirms the previously-raw vault writers (slice_queue_writer / slice_queue_claim / parallel_conflict_resolver regen paths, etc.) now call `safe_write_text`/`safe_append_text` |
| 2 | Audit fails closed | Temporarily revert one routed writer to a raw `write_text` → audit exits non-zero naming the file:line; restore → exits 0. Audit is listed in `/validate-slice` gate set + shippability.md |
| 3 | Concurrency proof | `$PY -m pytest tests/methodology/test_vault_write_safety_concurrency.py` PASSES; mutation run (lock disabled) FAILs the append-loss + torn-write assertions |
| 4 | R-32 narrowed | `$PY -m tools.risk_register_audit architecture/risk-register.md --json` shows R-32 with the Python sub-class evidence + residual note; reflection records the narrowing |
| 5 | No-flip contract intact | Full suite green (`$PY -m pytest`); `resolve_vault_root()` with no env/config returns `Path("architecture")` unchanged; `git diff` shows zero behavioral change to existing tools |

## Must-not-defer

- [ ] New audit rule (AC2) propagates a shippability.md row per RPCD-1 / SCPD-1 — write-safety enforcement must never silently regress.
- [ ] The audit is cp1252-safe (UTF8-STDOUT-1 stdout + defensive stderr-at-import) — slice-093 RSAD-1: a vault-infra tool nearly shipped its own cp1252 crash.
- [ ] The completeness audit fails CLOSED — an unclassifiable vault write is a violation, not a silent skip (the R-7 silent-disable class).
- [ ] The concurrency test is non-vacuous — proven by mutation (break the lock, see it FAIL, revert), per the slice-092 mutation-proof discipline.
- [ ] New-tool count-bump fan-out (N≥3 lesson): `plugin.yaml` (PMI-1), `tools/install_audit.py` + `INSTALL.md` counts (INST-1), the cp1252 parametrize list, AND any per-tool inventory-pin test all enumerate `vault_write_safety_audit.py`.
- [ ] Routing must not change file content/encoding/newline of any vault file (transparent pass-through; `safe_write_text` keeps `newline="\n"`).

## Out of scope

- The **skill-driven Write/Edit vault-mutation** sub-class (Claude editing vault files directly per SKILL.md prose, bypassing Python) — its own follow-up slice (slice-095 candidate); the wrapper-tool-vs-discipline+audit choice is an open design decision (ADR-worthy).
- The **flip** itself (writing a tier-2 `<git-common-dir>/aisdlc/vault-root` config / physically moving the vault) — re-sequenced to a later slice, gated on BOTH R-32 writer sub-classes closing.
- R-30 worktree / multi-root resolver edge cases — separate residual, closes at the flip.
- A migration command for existing projects' in-repo `architecture/` → external vault — later in the initiative.
- Non-vault writes in `tools/*.py` (graphify-out / diagnose-out / temp / tool-own-output) — out of the audit's scope by construction (vault-path-targeted only).

## Dependencies

- Prior slices: [[slice-093-add-external-vault-support]] — ships `tools/_vault_write.py` (the safe primitives) + `tools/_vault_paths.py` (`resolve_vault_root`, the seam).
- Vault refs: [[decisions/ADR-085]] (external-vault capability, no-flip), [[decisions/ADR-065]] (resolver seam).
- Risk register: [[risk-register#R-32]] (the risk this narrows — load-bearing flip blocker), [[risk-register#R-30]] (sibling resolver residual).

## Mid-slice smoke gate

At ~50% of build (writers routed + audit exists), run:
```
$PY -m tools.vault_write_safety_audit --repo-root .          # expect exit 0
# revert ONE routed writer to a raw write_text, re-run            # expect exit non-zero, names file:line
# restore it
$PY -m pytest tests/methodology/test_vault_write_safety_concurrency.py
```
Expected: audit clean on the routed tree, loud on a reverted writer; concurrency test PASSES. If the audit passes on a known-raw write (fails open) or the concurrency test is vacuous: STOP, fix the audit/test before continuing.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Ran in a real BRANCH-2 worktree (NOT WORKTREE=skip — per the slice-090/093 directive; slice-093 used WORKTREE=skip for entangled scaffolds, 094 must isolate)
