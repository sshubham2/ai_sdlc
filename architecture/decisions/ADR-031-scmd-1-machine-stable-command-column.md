---
id: ADR-031
title: SCMD-1 — machine-stable command column (6th) + shared token predicate with grammar enforcement layered on + incidental-decoupling closed-world invariant with a principled essential-class exclusion
date: 2026-05-16
slice: slice-031-complete-shippability-decoupling
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-031: SCMD-1 — machine-stable command column + incidental-decoupling invariant

## Context

Two slice-030A-deferred residuals share the catalog surface + a root cause (prose / environment-mutable cells):

- **D-2 prose-exec footgun** (slice-024/029 class, N+1): the `/validate-slice` runner mis-parsed rows #28/#29's narrative `Command` cells and shell-exec'd description text.
- **v2-B1 / meta-M-add-1 decoupling**: catalog-cited test fns transitively read gitignored / untracked state, so the regression check is environment-fragile (R-4 residual).

slice-030 history: the enumeration-completeness defect *relocated twice* here; /critique v1 + /critique-review (M-add-1) showed it can relocate a 3rd/4th time into (i) a hand-coded row subset and (ii) an essential-vs-incidental conflation. **Re-scoped per user-ratified b-split (TRI-1 2026-05-16): this slice handles the *incidental* class only.**

## The incidental vs essential distinction (load-bearing — defeats the M-add-1 relocation)

- **Incidental coupling**: a cited fn reads gitignored `…/architecture/slices/archive/…`, gitignored `…/architecture/build-checks.md`, or untracked `Path.home()/".claude"/"build-checks.md"` *only because it was never repointed* to a byte-faithful tracked input. slice-030A's BCI-1 gate (`live ≡ canonical fixture`) + the ADR-030 verbatim corpus make a tracked input byte-faithful → decoupling is **semantics-preserving**. **This slice's domain.**
- **Essential coupling**: the ~20 `test_v_0_NN_0_*_entry_present_in_repo_and_installed` fns (catalog rows 7–30) read untracked `Path.home()/".claude"/"methodology-changelog.md"` **because that read IS the in-repo↔installed forward-sync assertion**. There is **no BCI-1 analogue** — these fns are the only enforcers of that invariant. Decoupling them to a tracked mirror *destroys* the invariant; a compensating byte-equality guard either becomes the new coupled-cited-fn or escapes the audit (M-add-1, relocation 4th time). **Out of scope → slice-030C** (re-home the invariant off-catalog + a catalog-derived intentional-installed allowlist; the slice that escalates R-4 → `retired`).

## Options considered

1. Strict-grammar the existing `Command` column in place — destroys readability, large rewrite. Rejected.
2. Add a machine-stable column; runner + audits consume it; keep `Command` human-readable — additive, zero readability loss, backward-safe. **Chosen.**
3. Widen decoupling to ALL coupled fns (incidental + essential) in this one slice — re-introduces the M-add-1 relocation trap unless 030C's essential reframe is also done here; that exceeds ≤1-day scope and is the two-features-in-one-slice anti-pattern. Rejected at TRI-1 (user chose b-split).

## Decision

**Option 2 + one rule SCMD-1**, one tool `tools/shippability_decoupling_audit.py`, two checks:

- **(a) machine-stable command column** — a **6th** column `Machine-cmd` (the catalog is **5 columns today**, header L7 — the v1 design's "7th" was wrong). **Grammar (v2-M1/v2-m1 revised)**: `Machine-cmd` is **one or more `;`-separated grammar-conformant pytest invocations, prose-free** (NOT strictly a single token — v1's single-token mandate would have forced a lossy collapse of row #28's two distinct invocations `test_utf8_stdout_regression.py -q` ; `test_methodology_changelog.py -k v_0_42_0 -q`, either dropping a slice-028 test surface or cross-contaminating via a shared `-k`). Each invocation: `<interp> -m pytest <tests/…> [args]`, where `<interp>` is the **canonical placeholder** (the SKILL.md-prose convention) — the catalog does NOT embed the machine-specific absolute interpreter path; the bare `python` (#28) and the absolute `…/python.exe` forms both normalize to `<interp>`. The D-2 footgun being closed is *narrative prose-as-command*, NOT *multiple clean commands* — so bounded `;`-separated clean pytest invocations are permitted; any prose/narrative token (e.g. a leading `Commands:`), or a non-`tests/`-rooted target, is a violation. **The prose-rejection discriminator is net-new and concretely pinned (v2-M-add-A)**: it is NOT the shared `_TEST_PATH_RE` token predicate (which scans for `tests/…` after `pytest` and cannot reject a leading bareword). It is a full-cell validator in `tools/shippability_decoupling_audit.py` — strip fence → split on `;` → each non-empty trimmed segment must `re.fullmatch` an **interpreter-anchored** `^(<interp>|…python…) -m pytest tests/…$` shape (the leading anchor rejects `Commands:`/any prefix). Specified in design.md Data-model-deltas; regression-pinned by an AC3 TF-1 negative fixture (a leading-bareword cell MUST violate; a two-clean-`;`-separated cell MUST pass) — the discriminator is proven, not asserted. Runner (`/validate-slice` SKILL.md Step 4 + Step 5.5) and `shippability_path_audit` (PTFCD-1) repointed to consume `Machine-cmd`. `shippability_path_audit` currently hard-codes `command_cell = cells[3]` + `if len(cells) < 5: continue` (L146–L152); both change — a row **missing** `Machine-cmd` is a **SCMD-1 violation**, never a silent `continue`-skip (which would also disable PTFCD-1 for that row — B3). **Parser claim corrected (m2)**: SCMD-1 reuses `shippability_path_audit`'s *token-extraction predicate* (the `tests/\S+?\.py`-after-`pytest` regex), and **adds grammar enforcement on top of it** — it is NOT true that `shippability_path_audit` already enforces the `Machine-cmd` grammar; "single shared parser / CSP-1-class" is overstated and dropped. The shared artifact is the token predicate; the grammar is net-new.
- **(b) incidental-decoupling invariant** — re-derive the cited-fn set from **every** catalog row's `Machine-cmd` cell at every run (not a hand-coded subset — B1). Classify each resolved fn by the read-shape it statically exhibits (incidental / essential / clean — a *semantic predicate over every derived fn*, NOT a row or slice list). For each **incidental** fn enforce a **closed-world allowlist** (M1): the fn may reach a filesystem path ONLY via an allowlisted set of tracked-fixture-producing symbols (slice-030A canonical-fixture constants + the ADR-030 corpus accessor); ANY other Path-producing name/call — including constant/cross-module-indirected ones (`_GLOBAL_BUILD_CHECKS`, `REPO_ROOT`, `read_file`, conftest symbols) — is a violation (the resolver follows cross-module imports; unresolved symbol on an incidental fn ⇒ fail-closed violation, not silent-pass). **Essential** fns are *recognized and explicitly NOT flagged* — the read-shape exclusion is documented here + in the R-4 sub-entry as a semantic class with a chartered owner (030C), not enumeration.

One rule/tool/changelog-entry/gate-wiring because (a) and (b) are the same property ("the catalog is mechanically trustworthy at runtime, for the incidental class") attacked from two angles.

## Consequences

- shippability.md additive 6th column; all rows backfilled; #28/#29 normalized.
- New `tools/shippability_decoupling_audit.py` + `tests/methodology/test_shippability_decoupling_audit.py` (incl. an indirected-`Path.home()`-via-helper negative fixture proving the closed-world check catches indirection — M1).
- `shippability_path_audit.py` repointed (index + guard); `skills/validate-slice/SKILL.md` Step 4/5.5 repointed + prose-pinned.
- `methodology-changelog.md` (in-repo + installed) SCMD-1 entry; atomic PMI-1 bump; RPCD-1/SCPD-1 propagation.
- **R-4 stays `mitigating`** with a new sub-entry naming the ~20 essential entry-pin rows + the M-add-1 hazard + chartering slice-030C. Escalation to `retired` is **explicitly NOT done here** (it would be the D-3 silently-weakened failure while essential rows remain coupled).
- The slice-030 "missed a category" + critique-v1-B1 "category moved into the row filter" failure modes are structurally closed for the incidental class (all-rows derivation + read-shape predicate); the essential class is honestly carried, not silently swept.

## Reversibility

**cheap** — additive column + one tool + a shared-predicate import + repoints. Reverting = drop the column/tool/test, restore `cells[3]`/`len<5`, restore SKILL.md prose. No production/runtime/contract/data-model surface. Escalation: if the `Machine-cmd` grammar is too strict for a legitimate future row shape, widen it in one place (the grammar check) via a new append-only ADR (SUP-1).
