# Code Review: Slice 098 route-or-retire-git-coupled-vault-tools

**code-Critic reviewed**: slice diff vs default branch `4ebfbd5` (filtered to in-scope paths), worktree `C:/Users/sshub/ai_sdlc-wt/slice-098-route-or-retire-git-coupled-vault-tools`
**Date**: 2026-06-02
**Result**: FINDINGS (0 Blockers, 2 Majors, 4 Minors — all advisory in v1)

## Summary
A disciplined, well-traced slice: the two-literal-class model is implemented faithfully, the B2 guard placement is provably correct (RETIRE fires before any `out_path`/`relative_to` composition in both resolve entries), `vault_is_external` is correct across every edge case probed, and the no-flip byte-identity contract holds (305 related tests pass, including the explicit `_AUDIT_LOG_PATH` byte-identity pin). The findings are about the AST scanner's predicate being narrower than the design's "Class-A absence" claim implies (latent future-regression gap, not an active defect) and a defined-never-consumed primitive. No code path is broken or unsafe.

## Changed files (in-scope)
- tools/_vault_git.py  (NEW)
- tools/_vault_paths.py
- tools/parallel_conflict_resolver.py
- tools/pulse_worktree_resolver.py
- tools/stranded_slice_audit.py
- tests/methodology/test_vault_pathspec_tracked.py  (NEW)
- tests/methodology/test_slice_098_vault_routing.py  (NEW)
- tests/methodology/test_external_vault_adr_and_risk.py
- tests/methodology/test_vault_root_constant.py
- architecture/slices/slice-098-route-or-retire-git-coupled-vault-tools/build-log.md

## Findings

### Blockers (advisory in v1)

None. All 8 high-value targets attacked and cleared:
- **vault_is_external correctness**: default-relative, abs-under-repo (M1), abs-outside, `vault_root=.`, `vault_root==repo_root`, parent-of-repo — all correct. `resolved != root and root not in resolved.parents` is the robust PurePath-ancestry idiom, immune to the `str.startswith` sibling-prefix bug.
- **B2 reachability**: `_retire_if_vault_external` is the FIRST statement after the `repo_root is None` default in `resolve_soft_conflict` (`tools/parallel_conflict_resolver.py:369`) and `resolve_vault_claim_conflict` (`:1457`), strictly before `classify_conflict`/`out_path`/`relative_to`.
- **M-add-1 call-spy**: non-vacuous — `diagnose_conflict` IS reached (runs `_extract_u_files` on a clean repo, empty U-files, the `"architecture/slice-queue.md" in u_files` gate at `:214` false), so the spy genuinely proves unreachability.
- **21 Class-B markers** all land on correct lines (no broken continuation/multi-line literal); **M-add-2** dual-derivation is two separate objects, byte-identical on default; no new git subprocess lacks encoding handling; `_AUDIT_LOG_PATH` byte-identity pinned + passing.

### Majors

#### M1: AST scanner (AC1) has two false-negative shapes — the "Class-A absence" guarantee is narrower than design.md claims
- **Claim under review**: design.md §AST-predicate "absence … only in Class-A positions"; `tests/methodology/test_slice_098_vault_routing.py:56` `_find_unrouted_vault_div_literals`.
- **Issue**: the predicate only recognizes Class-A via `ast.BinOp(op=ast.Div)`. It misses (a) `repo_root.joinpath("architecture", ...)` and (b) a two-hop variable chain (`a = "architecture/x"; b = a; repo_root / b`). Executed against both + `os.path.join` → all `[]`. The M-add-3 def-use reach is one-hop only (`marked_names`, `:70-77`). The 3 tools use NEITHER shape (Grep-verified), so AC1 holds for this diff — but a future regression via `joinpath`/2-hop would silently pass.
- **Proposed fix**: (a) narrow the design.md claim to "no `Path / 'architecture'` div-form, one-hop alias"; or (b) extend to `joinpath` Calls + transitive `marked_names`.
- **Builder disposition**: **ACCEPTED-FIXED (a)** — design.md AST-predicate claim narrowed to the one-hop div-form + documented `joinpath`/2-hop as a named residual. Latent-not-active; the durable scanner extension is a flip-slice/bundled-cleanup candidate.

#### M2: M-add-2 git pathspec is VAULT_ROOT-derived (`.as_posix()`), not the "preserved verbatim" forward-slash literal design.md specifies
- **Claim under review**: design.md §M-add-2 "preserved verbatim for the git pathspec"; as-built `tools/stranded_slice_audit.py:311-312` derives `(VAULT_ROOT / "slices" / "archive" / f"slice-{num}-{name}").as_posix()`.
- **Issue**: the pathspec is computed FROM `VAULT_ROOT`, not a pure Class-B literal. Byte-identical on default; the `vault_is_external` guard at `:328` returns before these reads whenever VAULT_ROOT is absolute/external — so a backslash/absolute pathspec can never reach git. Behavior is correct, but safety now depends on guard ORDERING rather than the literal being structurally forward-slash; design and code disagree on a load-bearing invariant.
- **Proposed fix**: keep the verbatim literal, OR amend design.md to the as-built reality.
- **Builder disposition**: **ACCEPTED-FIXED (amend design.md)** — kept the VAULT_ROOT-derived `.as_posix()` form (it is MORE correct than the verbatim literal: for the external-but-tracked `<repo>/vault/` case the guard does NOT fire and the content genuinely lives at `vault/slices/...`, which the derivation reads correctly and a verbatim `architecture/...` literal would miss). design.md M-add-2 amended to state the as-built derivation + why it is sound (relative VAULT_ROOT → valid forward-slash pathspec; absolute external → guard RETIREs first).

### Minors

#### m1: `vault_pathspec_is_tracked` + `VaultGitUnavailable` defined+tested but consumed by no production tool
- **Issue**: `tools/_vault_git.py:44`/`:35` — neither imported by the 2 consuming tools (both use `vault_is_external`). SC-022 "defined-never-called-by-production" shape, but rationalized in docstring + design.md ("retained as a tested primitive for the flip slice") + pinned by `test_vault_pathspec_tracked.py` → defensible YAGNI-with-named-consumer.
- **Builder disposition**: **ACKNOWLEDGED** — intentional per ADR-089 (flip-slice primitive). The flip slice wires it or retires it.

#### m2: `VAULT_ROOT_IS_DEFAULT` exported, zero consumers
- **Issue**: `tools/_vault_paths.py:176` — the AS-BUILT model uses `vault_is_external`, not the proxy; the flag has no fast-path consumer. Honestly documented as "optional/observability."
- **Builder disposition**: **ACKNOWLEDGED** — leaf-cheap, frozen-at-import, self-documented; drop in the flip slice if it stays unconsumed.

#### m3: stranded RETIRE `vault_state="vault-untracked"` label vs the "external" (location) signal
- **Issue**: `tools/stranded_slice_audit.py:330-332` — the unified signal is store-LOCATION (`vault_is_external`), so `"vault-external"` is the precise label. Cosmetic; does not affect the halt.
- **Builder disposition**: **ACCEPTED-FIXED** — relabeled `vault_state="vault-external"`.

#### m4: PCR's RETIRE STOP writes no audit-log breadcrumb (only stdout/JSON)
- **Issue**: `tools/parallel_conflict_resolver.py:334-347` `_retire_if_vault_external` returns `ResolutionResult(action="STOP", …)` without `_append_audit_log` (unlike the clock-skew/equivalence STOPs). The reason IS surfaced via the `--resolve-soft` CLI stdout (`:2388-2389`) + JSON (`:2381`), so the must-not-defer "surface in audit output" is met. Writing to `_AUDIT_LOG_PATH` when the vault is external is itself questionable (the log path routes external too).
- **Builder disposition**: **DISPOSITIONED — satisfied via stdout/JSON; audit-log breadcrumb deliberately omitted.** The RETIRE reason already names the post-flip manual-resolution path + the flip tracking slice (the must-not-defer "actionable breadcrumb"); appending to the externally-routed `_AUDIT_LOG_PATH` when the vault is external would itself fail. Recorded as a deliberate decision, not a gap.

## Dimensions checked
- [x] Unfounded assumptions — none (docstrings match impl; M-add-1 unreachability verified, not asserted; no phantom imports).
- [x] Missing edge cases — none material (vault_is_external probed across 6 path shapes incl. symlink-resolve; no new CRLF byte-compare; no new concurrency surface on default).
- [x] Over-engineering — m1 + m2 (both documented/rationalized → Minor).
- [x] Under-engineering — none (AC1–AC5 each have a delivering element + test; external-root subprocess exercises pulse ROUTE + PCR RETIRE + stranded signal end-to-end).
- [x] Contract gaps — M2 (Class-B pathspec now VAULT_ROOT-derived — drift from design's "verbatim"; resolved by amending design.md).
- [x] Security — none (local dev tooling; no shell=True/eval/secrets/new input boundary; `.parents`-membership is the robust ancestry idiom; bytes-never-decoded primitive).
- [x] Drift from vault — M2 (pathspec-derivation drift, resolved). Otherwise tight: build-log records the deviation chain, design.md AS-BUILT + ADR-089 reflect it, no-flip preserved (305 pass), migration-pin 11→14 consistent across both pin files.
- [x] Web-known issues — none (`git ls-files --error-unmatch` rc semantics confirmed; `Path.resolve()`+`.parents` is OWASP/Django-recommended; no deprecated API).
- [x] Cross-cutting conformance — APED-1 (M-add-1 execution-pinned via call-spy); EOL-DRIFT-1 (no new .md byte-compare); RSAD-1 (the slice's own AST audit passes against its 3 tools; M1 is a guarantee-scope note); algorithm-path conformance (the `vault_is_external` guard composes correctly with all pre-existing fall-through branches).

## Builder response (advisory v1 — no TRI-1 gate)
- **M1** ACCEPTED-FIXED (design.md claim narrowed + joinpath/2-hop residual named).
- **M2** ACCEPTED-FIXED (kept the more-correct VAULT_ROOT-derived pathspec; design.md M-add-2 amended to the as-built + soundness rationale).
- **m3** ACCEPTED-FIXED (relabel `vault-external`).
- **m4** DISPOSITIONED (satisfied via stdout/JSON; audit-log breadcrumb deliberately omitted — external log path).
- **m1/m2** ACKNOWLEDGED (intentional flip-slice primitive / observability flag).
