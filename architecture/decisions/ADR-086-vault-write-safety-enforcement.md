---
id: ADR-086
title: Enforce vault-write-safety via a fail-closed per-write-target AST audit (VWS-1) over a closed-world tools/ scan, with a rationale-bearing scoped-out allowlist; fix _vault_write byte-faithfulness as the prerequisite
date: 2026-05-31
slice: slice-094-harden-vault-write-safety
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-086: Vault-write-safety enforcement (VWS-1)

> **Revised 2026-06-01 (flip-readiness redesign, pre-build).** The v1 of this ADR (VAULT_ROOT-import tripwire + literal-vault-path secondary; "isolates EXACTLY the 3 real writers"; "_vault_write signatures unchanged") was BLOCKED at `/critique` on three execution-verified blockers and revised in place — a same-slice, unshipped, pre-build decision evolving, NOT a SUP-1 supersession of a merged ADR. The id/slice/reversibility are unchanged; the detection model, scope, and the primitive-contract claim are corrected below.

## Context

slice-093 ([[ADR-085]]) shipped the R-32 write-safety *primitives* (`tools/_vault_write.py`: `safe_write_text`, `safe_append_text`) but left `tools/*.py` vault writers writing files directly. Two facts, both established by executing against the real code at `/critique`, shape this decision:

1. **The primitives are not byte-faithful** (B1). On Windows both emit CRLF — `safe_write_text` via `Path.write_text`'s default text-mode newline translation; `safe_append_text` via `os.open`'s **text-mode default** (no `O_BINARY`). Every existing vault writer uses `newline=""` → LF. So routing a writer through a primitive as-shipped would corrupt that file's newlines (EOL-DRIFT-1 / ADR-033 class). Byte-faithfulness must be fixed FIRST, or routing is a regression.

2. **R-32's hazard is not live until the flip** (B3). R-32's register entry: the concurrent-process lost-update "becomes live only at the slice-094 flip (vault untracked + shared)… the default stays `architecture/` (no flip), so the vault remains git-tracked and PCR still resolves vault-file conflicts loudly." All vault files are git-tracked today. So this slice is correctly scoped as **flip-readiness** — not R-32 retirement — and `parallel_conflict_resolver.py` (git-coupled, "retires at the flip" per slice-093's migration map) is scoped OUT, not routed.

The codebase forbids prose-only methodology rules (every load-bearing rule has a runnable audit). So "every governed writer routes through the primitives" must be a *machine-checked invariant*. The design question is HOW the audit decides a write is "a vault write that bypassed the primitives" — without (a) missing a writer that doesn't import the seam (the v1 PCR miss) and (b) false-positiving on the ~37 reader modules that merely *name* vault files.

## Options considered

1. **Runtime path-dataflow analysis** — fully resolve each write target `Path` and check it lands under `VAULT_ROOT`. *Pros*: precise. *Cons*: paths are runtime-composed; static resolution is undecidable → false-negatives or a fragile abstract interpreter. Over-engineered for a ≤1-day slice.
2. **Honour-system convention** — a CLAUDE.md rule, no audit. Rejected: violates the "no prose-only rule" discipline; the first forgetful tool silently re-opens R-32.
3. **VAULT_ROOT-import tripwire + literal-vault-path secondary (v1 — REJECTED at /critique)** — a module is a candidate writer iff it imports `VAULT_ROOT`; a secondary flags any raw write whose target literal names a vault file. *Cons proven fatal*: PCR imports neither `VAULT_ROOT` nor `_vault_paths`, so the primary tripwire never fires on the largest writer (B2); the secondary "module names a vault literal" false-positives on 37 readers (`git show`/`read_text`/error-prose), forcing the undecidable per-target analysis it was meant to avoid (M1).
4. **Per-write-target AST audit over a closed-world `tools/` scan, with a rationale-bearing scoped-out allowlist (CHOSEN)** — AST-walk `tools/*.py`; for each *write-op node* (`.write_text`/`.write_bytes`, `open`/`Path.open` in a write mode, `os.open` with write flags, `os.replace`) resolve the **write target** through a **bounded, decidable** depth — (i) ≤1 intra-function `Name` assignment AND (ii) module-level `Path(...)`/string constants; **NO** interprocedural / container-element / fixpoint resolution — and treat it as a vault write iff the resolved target is a vault-name/`architecture/` literal OR a `VAULT_ROOT`-derived expression. A vault write is CLEAN iff a call to a safe primitive, EXEMPT iff in `_vault_write.py`, CLEAN-SCOPED-OUT iff in the explicit allowlist (carrying a rationale), else a VIOLATION. *Pros*: catches the **1-hop-literal-assignment shape** (`var = root / "architecture" / "x.md"; var.write_text(...)`) that all 4 real writers AND **6 of PCR's 7 ops** use (the v1 import-tripwire missed PCR entirely); never matches a reader (a `read_text`/subprocess-arg is not a write op) — the M1 fix; fail-closed; relocation-proof; mirrors slice-041 `_REGISTERED_INSTALLED_READERS` + slice-095 SVW-1's COUNT-pinned exemption allowlist. The bounded depth is decidable (no fixpoint) — it is deliberately NOT Option-1's undecidable dataflow. *Cons*: a write target needing deeper resolution — a container element (PCR `:430`'s `pending_writes` loop-var) or a fully opaque runtime path — escapes the bound; **accepted, documented residual** (PCR is module-name scoped-out regardless; cooperative model = data-integrity, not adversarial bypass). (M2: the v2-draft pro "catches PCR — it has vault-literal write targets" was false — PCR's targets are 1-hop variables, not literals at the write node; this is the corrected, precise claim.)

## Decision

Adopt **Option 4**. Concretely:

- **Fix `_vault_write` byte-faithfulness first** (the prerequisite): `safe_write_text` → `write_text(..., newline="")`; `safe_append_text` → `os.open(... | getattr(os, "O_BINARY", 0))`. Empirically verified LF-faithful + `O_APPEND` preserved. Pin with an `nt`-guarded byte-identity test vs the canonical `newline=""` writer.
- **Route only the 2 seam whole-file writers** through `safe_write_text`: `slice_queue_writer.py:819-820`, `slice_queue_claim.py:535-536` (`_atomic_write_text`). Byte output unchanged (transparency, now true).
- **Scope `parallel_conflict_resolver.py` OUT** (git-coupled; retires at the flip per slice-093's map) — recorded in the audit's scoped-out allowlist with a rationale, COUNT-pinned against silent scope creep.
- Ship `tools/vault_write_safety_audit.py` implementing the per-write-target, fail-closed model; wire it into `/build-slice` Step 6 + `/validate-slice` + `architecture/shippability.md`. Mint RULE-ID **VWS-1** (MEPD-1 INCLUDE — BCI-1/SRSC-1 gate-wired-audit shape).

## Consequences

- A new `tools/*.py` that writes a vault file (by any recognized write op to a vault-name/`architecture/`/`VAULT_ROOT`-derived target, resolved through the bounded ≤1-hop + module-const depth) and forgets the primitive is caught at `/build-slice` Step 6 — R-32's Python-writer sub-class cannot silently regress, **including** writers that don't import the seam (the v1 import-tripwire PCR-miss is closed for the 1-hop-literal shape; the container-element/opaque-runtime-path residual is documented in Option 4 cons).
- **The `_vault_write` primitives' byte-output contract changes** (CRLF→LF on Windows), correcting them to match the established `newline=""` convention. This is the slice's only behavioral change to existing code, and it makes routing byte-transparent. (Corrects v1's false "signatures unchanged" — M4.)
- **R-32 is NOT retired by this slice** — it stays `mitigating` and retires at the flip. This slice delivers flip-readiness (byte-faithful primitives + 2 seam writers routed + enforcement audit + concurrency proof). PCR + `stranded_slice_audit` + `pulse_worktree_resolver` (git/worktree-coupled) + the physical move + the prose rewrite are the flip's residual; the skill-driven sub-class shipped in slice-095.
- The audit is a newly-minted AST parser → bound by BC-PROJ-13 (APED-1): the build EXECUTES it against the real `tools/` corpus + an adversarial battery — planted-raw VIOLATION, routed CLEAN, **reader-with-non-vault-write CLEAN** (the M1 guard), error-prose CLEAN, PCR CLEAN-SCOPED-OUT, primitive EXEMPT.
- The scoped-out allowlist is a single named module with a rationale, COUNT-pinned (not per-line suppression) — keeping the exception set auditable and singular.
- New-tool count fan-out (N≥3): `tools/install_audit.py:92` `_CANONICAL_TOOLS`, `plugin.yaml` tools list + `version`, `VERSION` (+ forward-synced `~/.claude/ai-sdlc-VERSION`), `INSTALL.md` count, `methodology-changelog.md`, `architecture/shippability.md` (row #102), the cp1252 parametrize list — all enumerate the new audit; the build greps EVERY count literal.

## Reversibility

**Cheap.** VWS-1 is an additive audit + a 2-line primitive byte-fix + two transparent call-site swaps. Removing it = delete the audit, unwire the SKILL.md gate lines, drop the shippability row; the byte-fix stays (it is a strict correctness improvement matching the existing convention). The routed writers keep working unchanged. No contract consumers, no data migration, no persisted state depends on it.
