# Design: Slice 030B complete-shippability-decoupling (re-scoped: incidental-only)

**Date**: 2026-05-16 (redesigned post-/critique v1 BLOCKED + /critique-review EXTEND; user-ratified b-split TRI-1)
**Mode**: Standard
**Risk tier**: high (in-house methodology surface + catalog-schema change; re-critique mandated after this material scope rewrite — v2 loop)

## Scope (re-scoped per user-ratified b-split)

**IN**: the *incidental* coupling class only — catalog-cited fns reading gitignored `architecture/slices/archive/**`, gitignored `architecture/build-checks.md`, or untracked `~/.claude/build-checks.md`, where slice-030A's BCI-1 gate + a verbatim tracked corpus make a git-tracked input **byte-faithful** (decoupling is semantics-preserving).

**OUT → slice-030C** (chartered via the R-4 sub-entry): the *essential* coupling class — the ~20 `test_v_0_NN_0_*_entry_present_in_repo_and_installed` fns (catalog rows 7–30) whose read of untracked `~/.claude/methodology-changelog.md` **is** the in-repo↔installed forward-sync assertion (no BCI-1 analogue). Decoupling these to a tracked mirror destroys the invariant (M-add-1). 030C re-homes that invariant off-catalog + adds a catalog-derived intentional-installed allowlist, and is the slice that escalates R-4 → `retired`.

## Why the boundary is principled, not enumeration (anti-relocation, B1 + M-add-1)

The slice-030 / critique-v1-B1 defect is *hand-enumerating a row subset*. This design does NOT do that. SCMD-1 derives the cited-fn set from **all** catalog rows at runtime, then **classifies each fn by the read-shape it statically exhibits**:

- **Incidental** ⇔ the fn reaches `…/architecture/slices/archive/…`, `…/architecture/build-checks.md`, or `Path.home()/".claude"/"build-checks.md"`. → must be decoupled (this slice).
- **Essential** ⇔ the fn reaches `Path.home()/".claude"/"methodology-changelog.md"`. → recognized, NOT flagged, NOT decoupled here (030C's domain).
- **Clean** ⇔ neither. → no action.

The boundary is a *semantic read-shape predicate evaluated against every derived fn*, not a list of rows or slices. A future row that introduces an incidental read in ANY row is caught; the essential class is a named read-shape exclusion documented in ADR-031 + the R-4 sub-entry (rationale: it is the load-bearing forward-sync invariant with no byte-faithful tracked equivalent — 030C's chartered reframe). This is the only formulation that (a) honors "mechanically derived, not enumerated", (b) does not false-positive-block the ~20 entry-pin rows, and (c) does not relocate the flaw into the audit's filter.

## What's new

- `tools/shippability_decoupling_audit.py` — **SCMD-1** audit. Two checks:
  - **(a) machine-stable command**: every catalog row carries a prose-free single-token machine-stable command (grammar below); a row missing it is a **violation**, not a silent skip.
  - **(b) incidental-decoupling invariant**: re-derive the cited-fn set from **every** row's machine-stable command cell (shared token predicate from `shippability_path_audit`, extended to capture the `::selector` + glob-expand prefix selectors). Classify each resolved fn by read-shape (above). For each **incidental** fn: enforce a **closed-world allowlist** — the fn may reach a filesystem path ONLY via an allowlisted set of tracked-fixture-producing symbols (the slice-030A canonical-fixture constants + the verbatim-corpus accessor); ANY other Path-producing name/call, including constant/cross-module-indirected ones (`_GLOBAL_BUILD_CHECKS`, `REPO_ROOT`, `read_file`, conftest symbols), is a violation. **Essential** fns are recognized and explicitly NOT flagged. Emits the derived archive-folder set for AC4 corpus-completeness.
- `tests/methodology/test_shippability_decoupling_audit.py` — TF-1 failing-first behavioral + consumer tests, incl. a deliberately-indirected `Path.home()`-via-helper negative fixture proving the closed-world check catches indirection (M1).
- `tests/methodology/test_shippability_command_column.py` — machine-stable-column + missing-column-is-violation tests (B3).
- `tests/methodology/fixtures/archive_backtest_corpus/` — git-tracked **verbatim** mini-corpus, populated by the SAME runtime derivation as SCMD-1 (b) (NOT a hand-listed slice set; includes slice-001 — read by row #8 `test_slice_001_archive_still_fires_legitimate_rules` L929/L960 + row #12 `test_slice_001_archive_still_fires_proj2` L1314). ADR-030.
- Decoupling edits in `tests/methodology/test_build_checks_audit.py`: archive-backtest fns repoint `project_checks`/`global_checks` → slice-030A canonical fixtures and `slice_folder` → the tracked corpus; **remove the `if _GLOBAL_BUILD_CHECKS.exists():` skip guards** on these fns (input is now an always-present tracked fixture → hard-assert; M4) — and the inline `project_path = REPO_ROOT/"architecture"/"build-checks.md"; .read_text()` at L949–950 likewise repointed. No assertion-semantics change (BCI-1 guarantees fixture ≡ live).
- `shippability.md`: add the machine-stable command column (the **6th** column — the catalog is 5 columns today, header L7); backfill every row incl. the rows #28/#29 prose footgun.
- `tools/shippability_path_audit.py`: repoint from `cells[3]` (Command) to the machine-stable column index; change `if len(cells) < 5: continue` so a row missing the machine-stable column is surfaced (not silently `continue`-skipped — that would also disable PTFCD-1 for the row). The token-extraction predicate is unchanged and shared with SCMD-1.
- `skills/validate-slice/SKILL.md`: Step 4 ("Run each entry's **Command** column" L207) + Step 5.5 re-exec prose repointed to consume the machine-stable column; pinned by a prose-pin test added to the **existing validate-slice prose-pin module `tests/methodology/test_validate_slice_skill.py`** (v2-B2 correction: NOT `tests/methodology/test_skill_md_pins.py` — that module does not exist; `tests/skills/diagnose/test_skill_md_pins.py` is diagnose-scoped, wrong skill). New fn `test_step4_5_5_consumes_machine_stable_command` (mini-CAD prose-pin class).
- `architecture/decisions/ADR-030-*`, `ADR-031-*` — revised this round.
- `methodology-changelog.md` (in-repo + installed): SCMD-1 entry; atomic PMI-1 bump.
- `architecture/risk-register.md`: new R-4 sub-entry (stays `mitigating`; names the ~20 essential entry-pin rows + M-add-1; charters slice-030C). RR-1 schema.

## What's reused

- slice-030A `tests/methodology/fixtures/build_checks/canonical_{project,global}_checks.md` + BCI-1 `live ≡ fixture` (`tools/build_checks_integrity.py`) — makes C1 repoint byte-faithful (the *reason* incidental decoupling is semantics-preserving and essential is not).
- `tools/shippability_path_audit.py` token predicate (`_TEST_PATH_RE`, post-`pytest`, backtick-strip, `::`-split) — SCMD-1 imports the *token-extraction* predicate; SCMD-1 *adds grammar enforcement on top* (it is NOT the case that `shippability_path_audit` already enforces the grammar — m2).
- `tests/methodology/conftest.py` `REPO_ROOT`/`read_file` (these are exactly the cross-module indirection the closed-world check must see through — M1).
- WIRE-1, RPCD-1, SCPD-1, PMI-1, CAD-1, BCI-1, PTFCD-1.

## Components touched

### tools/shippability_decoupling_audit.py (new)
- **Responsibility**: enforce SCMD-1 — (a) catalog is machine-parseable (prose-free command field) and (b) no catalog-cited fn carries *incidental* environment coupling (closed-world). Essential coupling is recognized + scoped to 030C, not policed here.
- **Lives at**: `tools/shippability_decoupling_audit.py`
- **Key interactions**: imports the token-extraction predicate from `tools/shippability_path_audit.py`; `ast`-parses cited test modules **and transitively the conftest/module-level symbols they reference** (closed-world resolver — M1); reads `architecture/shippability.md`; `tools._stdout` rollup. Consumed by `/validate-slice` Step 5.5 pre-catalog gate + `/build-slice` Step 6.
- **Closed-world allowlist — concrete membership (v2-M2, not abstract)**: an incidental fn may reach a filesystem path ONLY via these **allowlisted tracked-fixture-producing symbols**: `_CANONICAL_PROJECT_FIXTURE`, `_CANONICAL_GLOBAL_FIXTURE` (slice-030A canonical fixtures, `tests/methodology/test_build_checks_audit.py`), and the new ADR-030 corpus accessor (`_ARCHIVE_BACKTEST_CORPUS` / its accessor fn — name finalized at build). **Resolve-through (NOT allowlist members; the resolver must follow them transitively)**: `REPO_ROOT`, `read_file` (from `tests/methodology/conftest.py`). **Must-be-repointed, explicitly NOT an allowlist member**: `_GLOBAL_BUILD_CHECKS` (= `Path.home()/".claude"/"build-checks.md"`, L380) — any incidental fn still reaching it is a violation. **Fail-closed default**: any Path-producing name/call on an incidental fn that is neither allowlisted nor a resolve-through symbol ⇒ violation (errs to false-positive, never missed coupling). The allowlist is itself **asserted by a test** (`test_allowlist_membership_is_exactly`) so a slice-030A fixture-constant rename trips loudly rather than silently widening the allowed surface (prevents the v1-M3 hand-list defect recurring one level down).

### tools/shippability_path_audit.py (modified)
- **Responsibility**: unchanged (PTFCD-1 phantom-path detection); only the column the command is read from (was `cells[3]`, now the machine-stable column) + the `len(cells)` guard (missing machine-stable column ⇒ surfaced, not silent skip — coordinated with SCMD-1's violation).

### tests/methodology/test_build_checks_audit.py (modified)
- Archive-backtest fns: `project_checks`/`global_checks` → slice-030A canonical fixtures; `slice_folder` → tracked corpus; `.exists()` skip guards removed (hard-assert — M4); inline L949–950 live read repointed. No assertion-semantics change (BCI-1).
- **NOT touched**: the ~20 `test_v_0_NN_0_*_entry_present_in_repo_and_installed` fns in `test_methodology_changelog.py` — essential class, 030C. (No naming-lie / split introduced here — M2 resolved by not touching them.)

### skills/validate-slice/SKILL.md (modified)
- Step 4 + Step 5.5 runner prose repointed to the machine-stable column. Pinned (mini-CAD prose-pin).

## Contracts added or changed
None (no endpoints/events). Catalog **schema** changes — Data model deltas.

## Data model deltas

### shippability.md — machine-stable command column (the 6th column)
- **Defined in**: `architecture/shippability.md` (header + every row); schema enforced by `tools/shippability_decoupling_audit.py`.
- **What's new**: the catalog is **5 columns today** (`# | Slice | Critical path | Command | Runtime`, header L7). This adds a **6th** column `Machine-cmd`: exactly one backtick-fenced command token, no prose, no `;`-joined narrative. `Command` (human-readable) retained; **the runner + `shippability_path_audit` + SCMD-1 authoritatively consume `Machine-cmd`**. Rows #28/#29 prose normalized into a single token.
- **Validation/constraints (v2-M1 + v2-m1 revised grammar)**: a `Machine-cmd` cell is **one or more `;`-separated grammar-conformant pytest invocations, prose-free** — NOT strictly a single token. Each invocation MUST match `<interp> -m pytest <tests/…> [args]` where `<interp>` is the **canonical placeholder `<interp>`** (the SKILL.md-prose convention; the runner substitutes the resolved interpreter — the catalog does NOT embed the machine-specific absolute path; the absolute `<HOME>/.claude/.venv/Scripts/python.exe` form is normalized to `<interp>`). Allowing bounded `;`-separated *clean* invocations fully closes the D-2 footgun (the footgun is *narrative prose-as-command*, NOT multiple clean commands) **and** preserves row #28's two distinct surfaces (`test_utf8_stdout_regression.py -q` ; `test_methodology_changelog.py -k v_0_42_0 -q`) exactly — no lossy single-`pytest` merge, no `-k` cross-module contamination. Forbidden: any narrative/prose token, a bare leading word like `Commands:`, or a non-`tests/`-rooted target. Empty / missing / prose ⇒ **SCMD-1 violation**.

**Concrete segment validator (v2-M-add-A — the net-new discriminator, pinned not asserted)**: the shared `shippability_path_audit` artifact is ONLY the token-extraction predicate (`_TEST_PATH_RE`, L50) — it finds `tests/…` tokens after the first `pytest` and provably does NOT reject a leading `Commands:` prefix. SCMD-1's prose-rejection is therefore a **net-new full-cell validator** in `tools/shippability_decoupling_audit.py`, specified here: (1) strip the outer markdown backtick fence; (2) split the cell on `;`; (3) every non-empty `.strip()`-ed segment MUST **full-match** (anchored `^…$`, `re.fullmatch`) `(<interp>|python|\S+python(\.exe)?)\s+-m\s+pytest\s+(tests/\S+\.py(::\S+)?|tests/\S+)(\s+\S+)*` — the **leading anchor is what rejects a `Commands:` (or any) bareword prefix**, since a prose cell does not start with the interpreter token; (4) zero segments, or any segment failing full-match, ⇒ SCMD-1 violation. This discriminator — not the shared token predicate — is what makes the `;`-relaxation safe; it lives in `shippability_decoupling_audit.py` and is regression-pinned by the AC3 negative fixture below. `shippability_path_audit` reads this column at the corrected index; a row missing it is surfaced as a violation, never a silent `continue` (which would also disable PTFCD-1 for that row — B3-v1). Build-time check (mid-slice eyeball): #28's normalized cell collects the same pytest node set as the pre-normalization two commands.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/shippability_decoupling_audit.py` | `skills/validate-slice/SKILL.md` Step 5.5 pre-catalog gate + `skills/build-slice/SKILL.md` Step 6 pre-finish | `tests/methodology/test_shippability_decoupling_audit.py::test_incidental_fns_closed_world_allowlist_only` + `::test_every_row_has_machine_stable_command_or_violation` | — |
| `tests/methodology/fixtures/archive_backtest_corpus/**` | `tests/methodology/test_build_checks_audit.py` archive-backtest fns | `tests/methodology/test_build_checks_audit.py::test_slice_001_archive_still_fires_legitimate_rules` (+ the full derived incidental set) | — |

## Decisions made (ADRs)
- [[ADR-030]] — meta-M1′ corpus fidelity: git-tracked verbatim real mini-corpus, **derived (not hand-listed)** from the cited incidental set; immutability claim backed by a concrete SCPD-1/SCMD-1 orphan-catch (not bare assertion) — reversibility: **cheap**
- [[ADR-031]] — SCMD-1: machine-stable command column (6th) + shared token-extraction predicate with grammar enforcement layered on top + incidental-decoupling closed-world invariant with a *principled essential-class read-shape exclusion* (030C-chartered) — reversibility: **cheap**

## Authorization model for this slice
N/A — analogue is gate wiring: SCMD-1 non-opt-out at `/validate-slice` Step 5.5 + `/build-slice` Step 6, mirroring BCI-1; no `BRANCH=skip`-style escape hatch.

## Error model for this slice
`tools/shippability_decoupling_audit.py` (mirrors `shippability_path_audit`): `0` clean (or empty catalog) / `1` ≥1 SCMD-1 violation (prose/missing/multi-token Machine-cmd, OR an *incidental* cited fn reaching a path via a non-allowlisted symbol — message attributes row # + fn + offending symbol/read-shape) / `2` usage error (catalog missing/unreadable, or a cited module / its referenced conftest fails `ast.parse`). Fail-closed: unresolved cross-module symbol on an incidental fn ⇒ violation (not silent-pass) — closed-world.

## Anti-recurrence ledger (every v1 finding mapped)
- **B1** (scope) → all-rows derivation + principled read-shape classification; R-4 stays `mitigating`, 030C chartered.
- **M-add-1** (essential ≠ incidental, relocation) → essential class explicitly out-of-scope + recognized-not-flagged; 030C owns the reframe.
- **B2** (runner) → SKILL.md Step 4/5.5 repointed + prose-pin.
- **B3** (5→6 col, parser index/guard) → corrected; missing-column = violation, not silent PTFCD-1 skip.
- **M1** (AST incompleteness) → closed-world allowlist + indirected negative fixture.
- **M2** (naming lie) → resolved by NOT touching the essential entry-pin fns here.
- **M3** (corpus enumeration) → corpus derived from the cited set (incl. slice-001); AC2 completeness sub-check.
- **M4** (vacuous AC2) → `.exists()` guards removed on decoupled fns + no-skip-guard meta-check + env-patch specified.
- **m1** (immutability asserted) → ADR-030 reworded + concrete orphan-catch in AC2.
- **m2** (single-parser overstated) → ADR-031 reworded ("shared token-extraction predicate; grammar enforcement layered on top").
