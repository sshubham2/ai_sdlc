# Slice 030B: complete-shippability-decoupling

**Mode**: Standard
**Estimated work**: ~1 day (re-scoped minimal — incidental coupling only per user-ratified b-split, 2026-05-16)
**Risk retired**: [[risk-register#R-4]] **partial** — retires the *incidental*-coupling residual (archive-backtests + gitignored live build-checks). **R-4 stays `mitigating`, NOT `retired`** — the *essential*-coupling residual (~20 entry-pin rows reading untracked `~/.claude/methodology-changelog.md`) + the M-add-1 relocation hazard are chartered to **slice-030C** via a new R-4 sub-entry.
**Test-first**: true
<!-- per TF-1 — each AC maps to a failing audit/test written before the decoupling; see "## Test-first plan" -->
**Walking-skeleton**: false
**Exploratory-charter**: false

## Re-scope note (user-ratified split — 2026-05-16, TRI-1)

This slice was BLOCKED at /critique v1 (3 blockers / 4 majors / 2 minors, all VALID per /critique-review EXTEND) + meta-Critic **M-add-1**. Root cause: 030B-as-originally-scoped conflated **two categorically distinct coupling classes**:

- **Incidental coupling** (C1 checks-file + C2 archive-corpus): the test reads gitignored live `architecture/build-checks.md` / gitignored `architecture/slices/archive/**` only because it was never repointed to a byte-faithful tracked input. slice-030A's BCI-1 gate (live ≡ canonical fixture) + a verbatim tracked corpus make decoupling byte-faithful and R-4-retireable for these rows.
- **Essential coupling** (C3 entry-pin): the ~20 `test_v_0_NN_0_*_entry_present_in_repo_and_installed` fns (catalog rows 7–30) read untracked `~/.claude/methodology-changelog.md` **because that read IS the in-repo↔installed forward-sync assertion** — there is no BCI-1 analogue. Decoupling them to a tracked mirror *destroys* the invariant (M-add-1); the compensating guard either becomes the new coupled-cited-fn or escapes the audit (relocation, 4th time).

User decision (AskUserQuestion TRI-1, 2026-05-16): **(b-split)** — this slice does the incidental class only; **slice-030C** is chartered for the essential-coupling reframe (re-home the forward-sync invariant off-catalog + a catalog-derived intentional-installed allowlist) and is the path that escalates R-4 → `retired`. v1 audit trail preserved: `critique-history-v1.md`, `critique-review-history-v1.md` (triage_audit-clean, load-bearing).

## Intent

slice-030A retired R-4's *substance* (silent BC-1 degradation can't recur — BCI-1 non-opt-out gate). This slice removes the **incidental** catalog-row environment-fragility: archive-backtest *fns* stop reading gitignored live/archive state and instead read byte-faithful git-tracked inputs, the command column becomes machine-stable (killing the rows #28/#29 prose-exec footgun at the actual /validate-slice runner), and the deferred archive-backtest corpus-fidelity question is decided in an ADR. After this ships, a local `architecture/` drift can no longer false-PCA-1-HALT any **incidental-class fn**. **Granularity note (v2-B1)**: the guarantee is *per-fn*, not per-row. The `/validate-slice` runner executes a catalog row's command cell whole, and rows **#8/#12 are mixed-class** — each cites incidental archive-backtest fns AND an essential entry-pin fn (`test_v_0_23_0_*`/`test_v_0_27_0_*`) in one cell. Those two *rows* therefore remain environment-fragile *at row granularity* via their co-cited essential fn (which is correctly NOT decoupled here — that is 030C's domain). This is the honest R-4-`mitigating` boundary, NOT a 030B regression; the essential entry-pin rows remain logged as a `mitigating` R-4 residual owned by chartered slice-030C.

## Acceptance criteria

1. A new SCMD-1 audit **mechanically derives** the cited-fn set from **every** catalog row's machine-stable command cell (parsed at runtime, NOT hand-enumerated). For the **incidental** class — fns transitively reading gitignored `architecture/slices/archive/**`, gitignored `architecture/build-checks.md`, or untracked `~/.claude/build-checks.md` — every such fn is decoupled to assert only against git-tracked byte-faithful inputs (slice-030A canonical fixtures + the verbatim tracked corpus). The audit enforces a **closed-world allowlist**: each decoupled fn may reach a filesystem path ONLY via an allowlisted set of tracked-fixture-producing symbols; any other Path-producing name/call (incl. constant/cross-module indirection) is a violation.
2. Environment-independence is proven **non-vacuously at fn granularity**: with `architecture/slices/archive/` moved aside AND `~/.claude/build-checks.md` unavailable, every incidental-decoupled **fn executes its assertions** (no `if <untracked>.exists():` skip — the input is now an always-present tracked fixture, hard-assert) and PASSES; and still PASSES in the normal environment. A meta-check asserts no incidental-decoupled fn contains an `.exists()`-gated skip of its core assertion. The env-patch mechanism (monkeypatch `Path.home` + re-derive, or subprocess with patched `USERPROFILE`) is specified in design.md. **Sub-clause (v2-B1, explicit non-goal)**: mixed rows **#8/#12** are NOT made environment-independent at *row* granularity by this slice — each co-cites an essential `test_v_0_NN_0_*_entry_present_in_repo_and_installed` fn that (correctly) still reads `~/.claude/methodology-changelog.md`. AC2 success is asserted per incidental fn; the row-level guarantee for #8/#12 is explicitly **030C's** (R-4-`mitigating` boundary). AC2 must NOT claim those rows pass with the installed changelog unavailable.
3. shippability.md gains a **machine-stable command column** (the catalog is **5 columns today** → this is the **6th**; prose-free, single backtick-fenced token, grammar in design.md). `tools/shippability_path_audit.py` (PTFCD-1) is repointed to the new column with a corrected cell index + `len(cells)` guard such that a row **missing** the machine-stable command is a **SCMD-1 violation**, never a silent `continue`-skip (which would also silently disable PTFCD-1 for that row). Rows #28/#29 prose normalized. `skills/validate-slice/SKILL.md` Step 4 (and Step 5.5 re-exec) runner prose is repointed to consume the machine-stable column, pinned by a SKILL.md prose-pin test (mini-CAD class).
4. The archive-backtest corpus is a git-tracked **verbatim real** mini-corpus (ADR-030), populated by the **same runtime derivation** as AC1 — NOT a hand-listed slice set (must include slice-001, read by row #8/#12 backtests). AC2 includes a **bidirectional corpus-completeness sub-check**: (forward) every archive folder referenced by the derived incidental set has a corresponding tracked corpus fixture (no missing folder → no silent skip when the archive is unavailable); (reverse, v2-m2) no orphan corpus fixture exists for a folder no longer in the derived set (derived set ⊇ corpus fixture set — the SCPD-1 orphan-catch made concrete; dead-test-data smell).
5. Methodology propagation clean: SCMD-1 carries a `methodology-changelog.md` entry (in-repo + installed, atomic PMI-1 version bump), shippability.md catalog propagation per RPCD-1/SCPD-1, a new **R-4 sub-entry** added per RR-1 (R-4 stays `mitigating`; names the ~20 essential entry-pin rows + the M-add-1 hazard; charters slice-030C), and BCI-1 / PMI-1 / INST-1 / CAD-1 / CSP-1 / DR-1 all pass.

## Test-first plan

Per **TF-1**. Each AC maps to failing tests written BEFORE the decoupling/schema work. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish`.

Function names harmonized to the as-built tests (TPHD-1 sub-mode (c) — the pre-implementation plan names were drafted; the real functions are pinned here). All PASSING at pre-finish.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | meta/audit | tests/methodology/test_shippability_decoupling_audit.py | test_cited_fn_set_derived_from_all_rows_not_enumerated | PASSING |
| 1 | meta/audit | tests/methodology/test_shippability_decoupling_audit.py | test_no_incidental_cited_fn_remains_coupled | PASSING |
| 1 | meta/audit | tests/methodology/test_shippability_decoupling_audit.py | test_indirected_path_home_read_is_caught | PASSING |
| 1 | meta/audit | tests/methodology/test_shippability_decoupling_audit.py | test_clean_fn_reaching_only_allowlisted_symbol_is_clean | PASSING |
| 1 | meta/audit | tests/methodology/test_shippability_decoupling_audit.py | test_essential_entry_pin_fn_recognized_not_flagged | PASSING |
| 1 | meta/audit | tests/methodology/test_shippability_decoupling_audit.py | test_allowlist_membership_is_exactly | PASSING |
| 2 | meta/audit | tests/methodology/test_shippability_decoupling_audit.py | test_decoupled_incidental_fns_classify_clean | PASSING |
| 2 | meta/audit | tests/methodology/test_shippability_decoupling_audit.py | test_decoupled_incidental_fns_have_no_exists_skip_guard | PASSING |
| 3 | meta/audit | tests/methodology/test_shippability_command_column.py | test_every_row_has_machine_stable_command_or_violation | PASSING |
| 3 | meta/audit | tests/methodology/test_shippability_command_column.py | test_missing_column_is_violation_not_silent_ptfcd_skip | PASSING |
| 3 | meta/audit | tests/methodology/test_shippability_command_column.py | test_leading_bareword_prose_cell_is_violation | PASSING |
| 3 | meta/audit | tests/methodology/test_shippability_command_column.py | test_two_clean_semicolon_separated_invocations_pass | PASSING |
| 3 | meta/audit | tests/methodology/test_shippability_command_column.py | test_segment_regex_rejects_prose_accepts_clean | PASSING |
| 3 | drift-pin | tests/methodology/test_validate_slice_skill.py | test_step4_5_5_consumes_machine_stable_command | PASSING |
| 4 | meta/audit | tests/methodology/test_shippability_decoupling_audit.py | test_every_derived_archive_folder_has_tracked_corpus_fixture | PASSING |
| 5 | meta/audit | tests/methodology/test_methodology_changelog.py | test_v_0_45_0_scmd_1_entry_present_in_repo_and_installed | PASSING |
| 5 | meta/audit | tests/methodology/test_risk_register_audit_real_file.py | test_r_4_subentry_charters_030c_and_stays_mitigating | PASSING |
| 5 | meta/audit | tests/methodology/test_shippability_decoupling_audit.py | test_real_catalog_scmd1_clean | PASSING |

(Function names indicative; `/design-slice`/`/build-slice` finalize. TF-1 failing-before-fix invariant is binding.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | All-rows mechanical derivation + incidental closed-world allowlist | `$PY -m pytest tests/methodology/test_shippability_decoupling_audit.py::test_cited_fn_set_derived_from_all_rows_not_enumerated ::test_incidental_fns_closed_world_allowlist_only ::test_indirected_untracked_read_is_caught -q` — audit re-parses every row's machine-stable cell, expands cited-fn set, closed-world-checks each incidental fn |
| 2 | Non-vacuous environment independence | Move `architecture/slices/archive/` aside + make `~/.claude/build-checks.md` absent (specified env-patch) → incidental-decoupled fns execute assertions (not skip) + PASS; re-run normal → PASS; meta-check: no `.exists()`-gated core-assertion skip remains |
| 3 | Machine-stable command column + runner repoint | `$PY -m pytest tests/methodology/test_shippability_command_column.py tests/methodology/test_validate_slice_skill.py::test_step4_5_5_consumes_machine_stable_command -q`; manually confirm rows #28/#29 carry a parseable token + SKILL.md Step 4/5.5 prose says the machine-stable column |
| 4 | Corpus derived-not-listed + completeness | New ADR-030 names the runtime-derivation rule (no hand slice list); `::test_every_derived_archive_folder_has_tracked_corpus_fixture` proves slice-001 (+ all derived folders) present |
| 5 | Propagation clean + honest R-4 | `$PY -m tools.plugin_manifest_audit` ; `$PY -m tools.critique_agent_drift_audit --repo-root .` ; `$PY -m tools.build_checks_integrity` ; `$PY -m tools.risk_register_audit architecture/risk-register.md --json` (R-4 still `mitigating`, sub-entry charters 030C) ; `/drift-check` — all clean |

## Must-not-defer

- [ ] **All-rows mechanical derivation** — the cited-fn set MUST be parsed from every row's machine-stable command cell at runtime, NOT hand-enumerated. Hard-coding a row subset (the slice-030 v1/v2 + critique-v1-B1 defect) is prohibited.
- [ ] **Incidental/essential scope boundary is principled, not enumerated** — SCMD-1 polices ONLY the incidental read shapes (`…/architecture/slices/archive/…`, `…/architecture/build-checks.md`, `Path.home()/".claude"/"build-checks.md"`). It deliberately does NOT police `Path.home()/".claude"/"methodology-changelog.md"` (essential — 030C's domain). This boundary is documented in ADR-031 + the R-4 sub-entry as a *semantic class distinction*, not a row list — otherwise SCMD-1 false-positives on the ~20 entry-pin fns and blocks the catalog.
- [ ] **Closed-world allowlist, not open-world literal hunt** (M1) — the audit must fail-closed on constant/cross-module-indirected paths, not enumerate bad literal shapes.
- [ ] **Non-vacuous AC2** (M4) — decoupled fns hard-assert; no `.exists()`-gated skip; meta-checked.
- [ ] **R-4 stays `mitigating`** — escalating to `retired` while the essential rows remain coupled is the D-3 "silently weakened" failure. R-4 sub-entry charters 030C explicitly.
- [ ] Methodology propagation: changelog (in-repo+installed) + PMI-1 atomic bump + RPCD-1/SCPD-1.
- [ ] `/drift-check` clean before finish.

## Out of scope

- **Essential C3 entry-pin decoupling + forward-sync invariant re-home + catalog-derived intentional-installed allowlist + M-add-1 resolution → chartered slice-030C.** 030B MUST NOT attempt these (the M-add-1 relocation trap); R-4 → `retired` happens in 030C.
- **R-5 / D-1 CRLF-LF drift-test fragility** (`fix-skill-drift-test-crlf-normalization`) — separate backlog slice per slice-030A reflection L23.
- Un-gitignoring `architecture/` / `build-checks.md` (`.gitignore:11` stands).
- Changing `tools/build_checks_audit.py` `_parse_rules` / anchor / applicability semantics.
- Re-litigating BCI-1 or the slice-030A tracked literal-constant oracle.
- R-1 / R-2 / R-3.

## Dependencies

- Prior slice: [[slice-030-repair-build-checks-vault-and-harden-shippability]] (030A) — depends on its tracked canonical fixtures (`tests/methodology/fixtures/build_checks/canonical_{project,global}_checks.md`) + BCI-1 `live ≡ fixture` guarantee (makes C1 repoint byte-faithful).
- Vault refs: [[shippability.md]] (5-col header L7; rows #5/#8/#12 L13/L16/L20; rows #28/#29 L36/L37; rows 7–30 entry-pin citations), [[risk-register#R-4]] (stays `mitigating` + new sub-entry charters 030C).
- Code refs: `tools/shippability_path_audit.py` (L146–L152 `cells[3]`/`len<5` — repoint), `tests/methodology/test_build_checks_audit.py` (archive-backtests + L380 `_GLOBAL_BUILD_CHECKS` + `.exists()` guards), `tests/methodology/conftest.py` (`REPO_ROOT`/`read_file` cross-module), `skills/validate-slice/SKILL.md` (Step 4 L207 runner prose).
- ADRs: ADR-030 (corpus fidelity), ADR-031 (SCMD-1) — revised this round.
- **BFRD-1 disposition** (unchanged): not a defect-repro slice (R-4's bug substance reproduced+retired by 030A); test-first satisfied via the TF-1 plan above. Not routed to `/repro`.
- **Chartered follow-up**: slice-030C (essential-coupling reframe) — created by a future `/slice`; charter recorded in the R-4 sub-entry this round.

## Mid-slice smoke gate

At ~50% (cited-fn set derived from ALL rows + SCMD-1 audit written, before all incidental fns decoupled), run:
```
$PY -m pytest tests/methodology/test_shippability_decoupling_audit.py::test_cited_fn_set_derived_from_all_rows_not_enumerated -q
$PY -c "<emit the derived incidental-class fn set + their archive folders>"   # eyeball ONCE vs the catalog
```
Expected: the derived set spans **all** rows (not a subset), the incidental subset includes the slice-001 archive backtests, and the essential entry-pin fns are correctly classified essential (NOT flagged). Additionally (v2-B1) eyeball ONCE that the env-patch run of the mixed rows **#8/#12** still HALTs on a stale/absent installed `~/.claude/methodology-changelog.md` — proving the essential entry-pin fn is correctly NOT decoupled and the row-level fragility is the expected `mitigating` residual (NOT silently "fixed"). If the eyeball finds the derivation enumerating a row subset, OR mis-classifying an entry-pin fn as incidental, OR rows #8/#12 unexpectedly passing with the installed changelog absent (would mean an essential fn was wrongly decoupled here): STOP — that is the slice-030 root cause / the M-add-1 relocation recurring.

## Pre-finish gate

- [ ] All 5 ACs PASS with evidence in validation.md
- [ ] Must-not-defer fully addressed (all-rows derivation; principled incidental/essential boundary; closed-world; non-vacuous AC2; R-4 stays mitigating)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (derivation still all-rows + classification correct)
- [ ] BCI-1 / PMI-1 / INST-1 / CAD-1 / CSP-1 / DR-1 all clean
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] R-4 sub-entry applied (stays `mitigating`, charters 030C) — verified by `tools.risk_register_audit`
