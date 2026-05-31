# Design: Slice 094 harden-vault-write-safety

**Date**: 2026-05-31
**Mode**: Standard

## What's new

- `tools/vault_write_safety_audit.py` (NEW) — the **VWS-1** enforcement audit: a fail-closed AST scan that proves every `tools/*.py` vault write routes through the `_vault_write` safe primitives. Exit 0 clean / 1 violations / 2 usage-error (fail-visible).
- `tests/methodology/test_vault_write_safety_audit.py` (NEW) — VWS-1 contract + APED-1 adversarial battery (both false-positive and false-negative directions, executed against the real `tools/` corpus).
- `tests/methodology/test_vault_write_safety_concurrency.py` (NEW) — the R-32 concurrency proof: N parallel `safe_append_text` lose zero lines + N parallel `safe_write_text` never tear; non-vacuity proven by mutation.
- A new methodology rule **VWS-1** (MEPD-1 **INCLUDE** — non-underscore PMI-1-enumerated audit tool wired into gates; mirrors the BCI-1 / SRSC-1 precedent): methodology-changelog entry + VERSION bump + 5-part PMI-1 atomic bump + shippability row.
- `.gitignore` entries for the `_vault_write` sidecars/temp files (`*.lock` + the `*.<pid>.tmp` shape) — discharges the slice-093 code-Critic **m3** `.lock`-accumulation deferral (flagged in `tools/slice_queue_claim.py:226`).

## What's reused

- `tools/_vault_write.py` — `safe_write_text` (whole-file: sidecar `.lock` + atomic `os.replace` + bounded EPERM-retry) and `safe_append_text` (`O_APPEND` + lock). The slice-093 primitives ([[ADR-085]]); this slice ROUTES the writers through them, it does not re-implement them.
- `tools/_vault_paths.py` — `VAULT_ROOT` (the resolution seam, [[ADR-065]] + [[ADR-085]]); the VWS-1 audit keys its tripwire on a module importing this.
- `tools/_stdout.py` — `reconfigure_stdout_utf8()` (UTF8-STDOUT-1) + the encoding-safe stderr pattern; the new audit MUST use it (slice-093 RSAD-1: a vault-infra tool must not ship its own cp1252 crash).
- Closed-world-allowlist enforcement precedent — slice-041 `_REGISTERED_INSTALLED_READERS` (relocation-proof, fail-closed). VWS-1 reuses the philosophy.
- Risk: [[risk-register#R-32]] (the risk this NARROWS — load-bearing flip blocker).

## The vault-writer set (code-grounded enumeration)

`grep` of `tools/*.py` for both (a) `VAULT_ROOT`/`_vault_paths` import AND (b) a raw filesystem write op yields **exactly** the writers below. The four read-only `VAULT_ROOT`-importers (`stranded_slice_audit`, `pulse_worktree_resolver`, `shippability_path_audit`, `shippability_decoupling_audit`) have **no** write op; the two non-`VAULT_ROOT` writers (`install_audit`, `build_checks_integrity`) write non-vault targets — both correctly excluded by the discriminator.

| # | Module | Raw write site (pre-slice) | Vault target | Class | Routes to |
|---|--------|----------------------------|--------------|-------|-----------|
| 1 | `tools/slice_queue_writer.py` | `:107` `out_path.write_text(...)` | `slice-queue.md` | whole-file | `safe_write_text` |
| 2 | `tools/slice_queue_claim.py` | `:232` `_write_queue → write_text` | `slice-queue.md` | whole-file | `safe_write_text` |
| 3 | `tools/parallel_conflict_resolver.py` | `:303` `_append_audit_entry → open(...,"a")` | PCR audit log (`slice-queue-conflict-log.md`) | append | `safe_append_text` |

- `parallel_conflict_resolver._regen_slice_queue` (`:312`) delegates to `slice_queue_writer.write_slice_queue` → inherits #1's routing transitively (no separate site).
- **Build-time verification (must-not-skip)**: confirm `_merge_shippability` (PCR shippability.md merge, ~`:185`) has no un-routed `write_text` — the grep found only the `:303` append, but the build MUST re-run the VWS-1 audit against the post-routing tree to prove zero raw vault writes remain (AC2 is the structural guarantee, not this enumeration).

## Components touched

### `tools/vault_write_safety_audit.py` (NEW — the VWS-1 audit)
- **Responsibility**: prove no `tools/*.py` writes a vault file by a channel other than `_vault_write.safe_write_text` / `safe_append_text`; fail closed on any unclassifiable write.
- **Lives at**: `tools/vault_write_safety_audit.py` (created by this slice).
- **Detection model** (two tripwires, fail-closed — see [[ADR-086]]):
  1. **Primary (VAULT_ROOT-import tripwire)**: a module that imports `VAULT_ROOT`/`_vault_paths` AND contains a raw write op (`Path.write_text`/`write_bytes`, `open(...,'w'|'a'|'x')`, `os.open` with write flags, `os.replace`) that is NOT a call to a safe primitive → VIOLATION.
  2. **Secondary (literal-vault-path tripwire, defense-in-depth)**: any raw write whose target string literal names a vault file (e.g. `slice-queue.md`, `risk-register.md`, `_index.md`, `methodology-changelog.md`, `shippability.md`) or contains an `architecture/` segment — catches a future writer that hardcodes a vault path WITHOUT importing `VAULT_ROOT`.
  - **Exempt**: `tools/_vault_write.py` itself (the sanctioned primitive implementation — its raw `write_text`/`os.replace`/`os.open` ARE the safe channel). Exemption is a hardcoded module-name allowlist, not a per-line suppression.
- **Key interactions**: stdlib `ast` (parse `tools/*.py`); `tools/_stdout.py` (cp1252-safe output); consumed by `/build-slice` Step 6 + `/validate-slice` gate roster (prose-invoked) + `architecture/shippability.md`.
- **APED-1 obligation**: the AST matcher is a newly-minted parser → the build MUST execute it against the real `tools/` corpus AND an adversarial battery (a planted raw vault write → caught; a routed write → clean; a non-vault write → clean; the `_vault_write.py` impl → exempt). BC-PROJ-13.

### `tools/slice_queue_writer.py` / `tools/slice_queue_claim.py` / `tools/parallel_conflict_resolver.py` (MODIFIED)
- **Responsibility (unchanged)**: generate/claim the slice-queue; resolve PCR conflicts. This slice only swaps the raw write op for the safe primitive (transparent — identical final bytes, encoding, `newline="\n"`).
- **Lives at**: the three files above (modified at the sites in the table).
- **Key interactions**: import `safe_write_text`/`safe_append_text` from `tools._vault_write`.

## Contracts added or changed

None. No endpoints, events, or schemas. The `_vault_write` function signatures are unchanged (slice-093). The VWS-1 audit's CLI contract is exit-code-only (0/1/2), the established audit-tool shape (RR-1/SRSC-1/BCI-1).

## Data model deltas

None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/vault_write_safety_audit.py` | `skills/build-slice/SKILL.md` Step 6 + `skills/validate-slice/SKILL.md` gate roster (prose-invoked, per the RR-1/SRSC-1 audit-wiring precedent) | `tests/methodology/test_vault_write_safety_audit.py::test_audit_flags_planted_raw_vault_write` | — |
| `tests/methodology/test_vault_write_safety_concurrency.py` | — | — | internal — rationale: pytest-collected concurrency proof; a test module is self-consuming, no downstream module consumer demanded |

## Decisions made (ADRs)

- [[ADR-086]] — Enforce vault-write-safety via a fail-closed closed-world AST audit (VWS-1) keyed on the VAULT_ROOT-import tripwire + a literal-vault-path secondary, rather than runtime path-dataflow or honour-system convention — reversibility: **cheap**.

### Sub-decisions (recorded here, not ADR-worthy — anti-pattern to ADR trivial choices)

- **`.lock` sidecar + `.tmp` persistence (discharges slice-093 m3)**: lock sidecars are intentionally persistent and reused across writes — deleting a `.lock` a concurrent waiter is about to acquire is a TOCTOU race (the standard file-lock-library posture). Resolution: do NOT delete them; add `*.lock` + the `*.<pid>.tmp` shape to `.gitignore` so they never pollute `git status` / the (future external) vault tree. This closes m3 without introducing a delete-race.
- **MEPD-1 INCLUDE**: this slice ships a non-underscore PMI-1-enumerated audit tool wired into gates → it mints RULE-ID **VWS-1**, a methodology-changelog entry, a VERSION bump, a 5-part PMI-1 atomic bump, and a shippability row. (Contrast slice-093's EXCLUDE — that shipped an *underscore* primitive module extending an existing seam; this ships a *gate-wired audit*, the BCI-1/SRSC-1 INCLUDE shape.)

## Authorization model for this slice

Not applicable — local audit/build tooling, no auth/authz surface. Per the cooperative-not-adversarial model ([[ADR-067]]): vault-write-safety is a **data-integrity control, NOT a security boundary**. It defends against concurrent cooperating writers (two Claude sessions / parallel slices on one machine), not a malicious actor.

## Error model for this slice

- `vault_write_safety_audit.py`: exit **0** (no violations) / **1** (≥1 violation — names each `path/to/file.py:line` + the un-routed channel) / **2** (usage error — `tools/` unreadable / unparseable; fail-VISIBLE per the R-7 silent-disable class, never a silent skip).
- Fail-closed: a write op the AST cannot classify as safe is a **violation** (exit 1), never a silent pass.
- The routed primitives inherit `_vault_write`'s existing error model (bounded EPERM-retry → loud `PermissionError` after exhaustion; `TimeoutError` on lock-acquire timeout). No change.

## R-32 narrowing (recorded at /reflect, not here)

This slice retires the **Python-tool-writer** sub-class of R-32 (the 3 writers above route through the safe primitives; the VWS-1 audit makes a bypass un-mergeable). R-32 stays `mitigating` (NOT `retired`) because the **skill-driven Write/Edit** sub-class (Claude editing vault files directly per SKILL.md prose) remains — documented as the explicit residual gating the flip, with its follow-up already queued as `harden-vault-skill-write-discipline` (slice-095 candidate). This follows the slice-084/085 "narrow, don't force-retire" pattern.
