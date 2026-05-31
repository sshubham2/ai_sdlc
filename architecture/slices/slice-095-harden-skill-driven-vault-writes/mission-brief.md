# Slice 095: harden-skill-driven-vault-writes

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-32 (the SECOND / final sub-class — skill-driven Write/Edit vault-mutation). Register state (source of truth): medium × medium, score 4, status `mitigating`, reversibility cheap — NOT-yet-live (the default stays `architecture/`); it escalates only at the flip, when the vault goes shared + untracked. Closing this sub-class together with slice-094's Python-writer sub-class RETIRES R-32 — the load-bearing blocker for the external-vault flip. (Note: slice-094's brief frames R-32 as "high×high score 9"; the register itself records medium×medium / score 4 — this brief follows the register.)
**Test-first**: false  (the concurrency proof is core, but the design phase may opt into TF-1; mirrors slice-094)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

slice-093 shipped the R-32 write-safety *primitives* (`_vault_write.safe_write_text` / `safe_append_text`) and slice-094 routes the **Python-tool** vault writers through them (closing the Python-writer sub-class). The remaining R-32 sub-class is **skill-driven**: Claude editing vault files directly via the `Write` / `Edit` tools per SKILL.md prose — which never touches `_vault_write` and is invisible to slice-094's Python-only completeness audit. Under the post-flip shared-vault model (vault outside per-worktree git isolation, shared across parallel slices) two concurrent sessions editing the same vault file via `Write` / `Edit` can lose updates or tear the file, with no merge-time PCR to catch it. This slice closes that sub-class: it establishes a concurrency-safe path for skill-driven vault mutations, ships a fail-closed audit that makes an unsafe skill-driven vault write impossible to merge silently, and proves no corruption under N concurrent skill-path writers — retiring R-32 (with slice-094) and unblocking the flip.

## Acceptance criteria

1. Skill-driven vault mutations have a concurrency-safe path: the relevant `skills/*/SKILL.md` vault-mutation surfaces route through the safe mechanism the design selects (the **wrapper-tool vs. discipline+audit** choice is an ADR-worthy design decision) so a Claude-issued vault write no longer bypasses `_vault_write`'s lock + atomic-replace guarantees.
2. A new fail-closed audit (`tools/skill_vault_write_safety_audit.py` or design-equivalent) statically detects any skill surface that prescribes an **unsafe** (raw `Write` / `Edit`) mutation of a resolved-vault-root path, exits non-zero on a violation (an unclassifiable skill-driven vault write is a violation, never a silent pass), and is wired into the `/build-slice` Step-6 + `/validate-slice` gate roster + `shippability.md`.
3. A concurrency proof: N concurrent skill-path vault mutations to the same file lose **zero** data and never leave a torn / partial file (the chosen mechanism holds under contention). Non-vacuity is proven by mutation (disable the lock/guard → test FAILs → revert).
4. R-32's skill-driven sub-class is recorded **closed-with-evidence** in `architecture/risk-register.md`; the note states R-32 RETIRES (unblocking the external-vault flip) once BOTH sub-classes have merged — Python-writer (slice-094) + skill-driven (this slice). If slice-094 has already merged, R-32 moves to `retired`; otherwise it stays `open` with only the skill-driven sub-class marked closed and a retire-on-094-merge trigger.
5. The no-flip safety contract is preserved: `resolve_vault_root` default stays `architecture/`, every existing skill / tool / test behaves identically (the safe path is transparent absent contention), and the full test suite stays green.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Skill writes routed | grep the touched SKILL.md surfaces — vault mutations go through the design-selected safe mechanism, not a bare `Write` / `Edit` on a vault path; `$PY -m tools.skill_vault_write_safety_audit --repo-root .` exits 0 |
| 2 | Audit fails closed | Temporarily inject a raw skill-driven vault write into a SKILL.md → audit exits non-zero naming the surface:line; restore → exits 0. Audit listed in `/validate-slice` gate set + `shippability.md` |
| 3 | Concurrency proof | `$PY -m pytest tests/methodology/test_skill_vault_write_safety_concurrency.py` PASSES; mutation run (guard disabled) FAILs the data-loss + torn-write assertions |
| 4 | R-32 closed / retired | `$PY -m tools.risk_register_audit architecture/risk-register.md --json` shows R-32 skill-driven sub-class closed-with-evidence + retire-on-both-merged note (or `status: retired` if 094 merged); reflection records the closure |
| 5 | No-flip contract intact | Full suite green (`$PY -m pytest`); `resolve_vault_root()` with no env/config returns `Path("architecture")` unchanged; `git diff` shows zero behavioral change to existing skills/tools |

## Must-not-defer

- [ ] New audit rule (AC2) propagates a `shippability.md` row per RPCD-1 / SCPD-1 — skill-driven write-safety enforcement must never silently regress.
- [ ] The audit is cp1252-safe (UTF8-STDOUT-1 stdout + defensive stderr-at-import) — RSAD-1: a vault-infra tool must not ship its own cp1252 crash (the self-applying class, N≥8).
- [ ] The completeness audit fails CLOSED — an unclassifiable skill-driven vault write is a violation, not a silent skip (the R-7 silent-disable class).
- [ ] The concurrency test is non-vacuous — proven by mutation (break the guard, see it FAIL, revert), per the slice-092 / slice-094 mutation-proof discipline.
- [ ] New-tool count-bump fan-out (N≥3 lesson): `plugin.yaml` (PMI-1), `tools/install_audit.py` + `INSTALL.md` counts (INST-1), the cp1252 parametrize list, AND any per-tool inventory-pin test all enumerate the new audit.
- [ ] OSDG-1 forward-sync: any edited `skills/*/SKILL.md` under the OSDG-1 guarded set stays content-equal (modulo EOL) to its installed copy + passes its drift test.

## Out of scope

- The **flip** itself (writing the tier-2 external vault-root config / physically moving the vault) — its own later slice, now unblocked once R-32 retires (094 + 095 merged).
- The **Python-tool-writer** sub-class — slice-094 owns it (this slice mirrors its model for the skill path).
- A migration command for existing projects' in-repo `architecture/` → external vault — later in the initiative.
- Non-vault skill writes (Claude editing source / test / docs files via `Write` / `Edit`) — out of the audit's scope by construction (vault-path-targeted only).
- R-30 broader cp1252 audit across all tools, R-13 OSDG-1-for-slice-candidates — separate queued candidates.

## Dependencies

- Prior slices: [[slice-094-harden-vault-write-safety]] — the Python-writer sub-class + the `_vault_write` routing model this slice mirrors for the skill path. **Sequencing**: R-32 retirement is gated on BOTH 094 and 095 merging; 095 can be designed/built in a parallel worktree but shares coordination files (`risk-register.md`, `shippability.md`, gate-roster SKILL.md) with 094 — additive, PCR-resolvable overlap, **NOT cleanly non-overlapping**. [[slice-093-add-external-vault-support]] — the `_vault_write` primitives + the `resolve_vault_root` seam.
- Vault refs: [[decisions/ADR-085]] (external-vault capability, no-flip), [[decisions/ADR-065]] (resolver seam). A NEW ADR will record the wrapper-vs-discipline mechanism decision.
- Risk register: [[risk-register#R-32]] (the risk this closes — the load-bearing flip blocker).

## Mid-slice smoke gate

At ~50% of build (safe path wired + audit exists), run:
```
$PY -m tools.skill_vault_write_safety_audit --repo-root .          # expect exit 0
# inject ONE raw skill-driven vault write into a SKILL.md, re-run     # expect exit non-zero, names the surface:line
# restore it
$PY -m pytest tests/methodology/test_skill_vault_write_safety_concurrency.py
```
Expected: audit clean on the routed tree, loud on an injected raw write; concurrency test PASSES. If the audit passes on a known-unsafe write (fails open) or the concurrency test is vacuous: STOP, fix the audit/test before continuing.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Ran in a real BRANCH-2 worktree (NOT WORKTREE=skip) — per the slice-090/093/094 directive; isolate slice-095 from the parallel slice-094 worktree.
