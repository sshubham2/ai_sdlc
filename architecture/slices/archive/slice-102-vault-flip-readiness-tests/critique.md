# Critique: Slice 102 vault-flip-readiness-tests

**Critic reviewed**: mission-brief.md, design.md, ADR-092 (verified against the real `tools/vault_flip_readiness_audit.py` + `tests/methodology/test_vault_flip_readiness_audit.py` **by execution**)
**Date**: 2026-06-02
**Result**: NEEDS-FIXES (0 blockers, 2 majors, 3 minors)

## Summary
The core mechanics are sound and empirically verified: the `write_text`/`write_bytes` content-arg fix leaves the production `_BASELINE` byte-identical (4 sites, executed), and the tests-surface `needs-human` set drives to ∅ after the fixtures exclusion + `write_text` fix + surface remap (executed: 0 residual). Two real issues: (M1) the blanket `unmarked-collection-pathspec → test-update-at-flip` remap mislabels ~49 git-pathspec/Class-B-mirror literals as "will update at flip" when they will NOT — a loss of ADR-091 loud-vs-silent fidelity in the exact artifact the flip-execute slice consumes; (M2) AC4's `--strict` "combined baseline" clause contradicts the design's production-scoped `baseline_tuple()`.

## Findings

### Blockers (must address before /build-slice)

**None.** The two load-bearing correctness claims were **verified by execution**, not reasoning:
- `audit_root(repo)` with the `write_text` content-arg rule still yields `baseline_tuple() == sorted(_BASELINE)`, len 4 (the 4 `project_frame_synth.py` `/`-BinOp sites are untouched by the rule).
- Tests surface (fixtures excluded) under the `write_text` fix + surface remap: residual `needs-human` = **0**.

### Majors (address this slice)

#### M1: `unmarked-collection-pathspec → test-update-at-flip` mislabels ~49 Class-B/git-pathspec mirrors as "will update at flip"
- **Claim under review**: design.md (orig.) Components-touched #4 — "the unmarked-collection-pathspec rule yield[s] TEST_UPDATE_AT_FLIP instead"; ADR-092 "collection→checklist"; mission-brief Must-not-defer "intentional test seam/migration constant is a distinct named class."
- **Issue**: Of the 209 would-be `test-update-at-flip` items, **160 are genuine path-construction** (resolve a vault path — WILL update at flip) but **49 are collection-pathspec git/Class-B mirrors that will NOT update**. E.g. `tests/skills/parallel_conflict_resolver/test_soft_file_set.py:47-51` asserts `_SOFT_FILE_SET == frozenset({"architecture/slice-queue.md","architecture/shippability.md"})`; the production `_SOFT_FILE_SET` (`tools/parallel_conflict_resolver.py:59-62`) is **Class-B git-identity marked** (stays `architecture/…` at flip, classifies `already-seam-routed`), so its test mirror also does NOT change. `test_pcr_2a_vault_claim_resolver.py:274/280/286` = `git add "architecture/slice-queue.md"` (git pathspecs). `test_build_checks_audit.py:828` mirrors a BC-1 `applies_to` pathspec. The flip-execute slice — which consumes this checklist live — is handed ~49 false "update" entries; if acted on, `_SOFT_FILE_SET == expected` FLIP-BREAKS.
- **Evidence**: executed — 209 = 160 path-construction + 49 collection-pathspec; production `needs-human` 0, `_SOFT_FILE_SET` classifies `already-seam-routed`. `tools/parallel_conflict_resolver.py:59-62`; `tests/skills/parallel_conflict_resolver/test_soft_file_set.py:47-51`; `tests/methodology/test_pcr_2a_vault_claim_resolver.py:274-286`.
- **Proposed fix**: split the tests collection class out of the update checklist — `test-update-at-flip` = path-construction only; a distinct `test-collection-pathspec` for collection-member git-pathspec/Class-B mirrors (review-at-flip, not the checklist).
- **Builder draft**: **ACCEPTED-FIXED** — applied this round. Introduced a second tests-surface class `test-collection-pathspec` (the `unmarked-collection-pathspec` rule routes here on the tests surface; path-construction → `test-update-at-flip`). Updated design.md (What's-new, Evidence table, Components #3/#4, AC→mechanism map), ADR-092 (Options 3, Decision, Consequences), mission-brief AC2. The audit classifies by the structural path-vs-collection signal (already computed by the ruleset); it does NOT cross-reference the production Class-B set to *prove* mirror-ship (over-assertion; left to flip-execute). Implementation lands at `/build-slice`.

#### M2: AC4's `--strict` "combined baseline unchanged" contradicts the production-scoped `baseline_tuple()`
- **Claim under review**: mission-brief AC4 (orig.) "under `--strict`, the **combined baseline is unchanged**" vs design.md Components #6 "`baseline_tuple()` scoped to `surface == 'production'`" + Tests-surface-regression-strategy "`--strict` drift-guards only the stable production 4-set."
- **Issue**: mutually exclusive. The ratified Option B (ADR-092 option 4) production-scopes `--strict`; AC4's combined-baseline clause has no delivering design element → would surface at TF-1 strict-pre-finish.
- **Evidence**: mission-brief.md AC4; design.md Components #6 + regression-strategy section.
- **Proposed fix**: amend AC4 to the ratified Option B (`--strict` gates the production 4-set; tests gate-covered by `needs-human`-empty + floors).
- **Builder draft**: **ACCEPTED-FIXED** — applied this round. Rewrote mission-brief AC4 (production-scoped `--strict`; both surfaces gate-covered; tests via `needs-human`-empty + per-class floors). Harmonized the TF-1 plan rows (AC4 maps to the preserved production `--strict` test + the tests `needs-human`-empty test).

#### M-add-1 (meta-Critic / critique-review.md): `test-collection-pathspec` is heterogeneous — a genuine path-resolve that is a collection-display member is silently demoted off the checklist AND escapes the fail-closed net
- **Source**: `/critique-review` EXTEND (missed by the first Critic — the "a Critic's own fix is a fresh claim" pattern one level up: my M1 fix moved the *whole* collection bucket off the gate).
- **Issue**: `test-collection-pathspec` is a purely structural signal (collection-member). A genuine path-resolve that is a bare list/tuple member a test loops over and opens (executed: `for rel in ["architecture/slice-queue.md", …]: (tmp/rel).write_text(...)`) is classified `test-collection-pathspec` → review-at-flip, off-checklist, exit 0 — even though it breaks LOUDLY at flip. The identical signal is fail-closed `needs-human` (exit 2) on the production surface. **Latent, not live**: all 49 of today's collection members are genuine git-pathspec/Class-B/git-status mirrors (meta-Critic inspected), so the slice ships correctly now; but the design's "mostly stays" prose implies a structural invariant that isn't guaranteed, and the per-class FLOOR_B can't catch a genuine-resolve being absorbed (count goes UP).
- **Evidence**: audit `_is_collection_member` (L279) + rule 4 (L361); design.md§What's-new / Evidence-table / regression-strategy; ADR-092 Consequences (omits this residual). Frameworks: McGraw (fail-closed degrade-safe) + Wiegers (AC2's "unclassifiable → needs-human, never dropped" is contradicted by dropping a genuine-resolve into a non-gating bucket).
- **Proposed fix**: (a) stronger — make `test-collection-pathspec` a non-zero "review-required" disposition flip-execute must acknowledge; or (b) cheap honest-contract — a pinned documented-residual test + downgrade the "mostly stays" prose to a current-corpus observation naming the heterogeneity + make the flip-execute "process BOTH lists" contract explicit.
- **Builder draft**: **ACCEPTED-PENDING via (b)** *(recommended; user chooses (a) vs (b) at TRI-1)*. Rationale the meta-Critic's "fail-closed waiver" concern actually resolves to: on the **tests** surface a mis-bucketed genuine-resolve breaks **LOUDLY** at flip-execute (a failing test), NOT a silent mis-resolve — that is the ADR-091 loud-vs-silent rationale, and it makes a non-fail-closed *review* bucket acceptable **provided flip-execute processes both lists**. So (b) is sufficient and (a) is belt-and-suspenders gold-plating over a zero-instance case (over-engineering watch). At build: add `test_collection_member_genuine_resolve_is_review_residual` (pins the heterogeneity + the flip-execute-reviews-both contract); downgrade design.md + ADR-092 "mostly stays" → current-corpus observation + the loud-breakage justification + explicit "flip-execute MUST consume the `test-collection-pathspec` review list, not only the `test-update-at-flip` checklist."

### Minors (log; address if cheap)

#### m1: The checklist FLOOR catches "scan empty" but not a silent drop of one sub-class
- **Issue**: a single aggregate floor (live 209) set to e.g. 150 passes even if the 49-member collection sub-class silently drops (209→160). Floor proves "non-empty," not "complete per sub-population."
- **Proposed fix**: per-class floors / band assertion; or document the floor is an emptiness guard.
- **Builder draft**: **ACCEPTED-PENDING** — at build, `test_tests_surface_class_floors` asserts BOTH `test-update-at-flip` ≥ FLOOR_A **and** `test-collection-pathspec` ≥ FLOOR_B (each below its measured live count). The M1 split makes this natural. Recorded in design regression-strategy #3 + ADR-092 Consequences.

#### m2: `audit_file` surface derivation depends on a forward-slash, `tests/`-prefixed `rel`
- **Issue**: `audit_root` normalizes backslashes before calling `audit_file` (correct in the real scan — the `test_`-named production tool stays production), but a direct unit-test caller passing `"tests\\foo.py"` would mis-derive surface.
- **Proposed fix**: derive surface from a normalized rel (`rel.replace("\\","/").startswith("tests/")`).
- **Builder draft**: **ACCEPTED-PENDING** — at build, normalize the rel inside `audit_file` before the surface check (recorded in design Components #2). Cheap defense-in-depth.

#### m3: `fixtures/**` exclusion is a silent residual
- **Issue**: today no `.py` fixture carries a vault literal (grep empty across 17 fixtures); the exclusion only drops the deliberate `syntax_error.py` parse-error. But a future `.py` fixture resolving a real vault path would be invisible — a silent residual, like the fully-dynamic-path case.
- **Proposed fix**: add a pinned residual-documenting test mirroring `test_documented_residual_fully_dynamic_path_invisible`.
- **Builder draft**: **ACCEPTED-PENDING** — at build, add `test_fixtures_dir_vault_literal_out_of_scope` (pins the documented residual, slice-095 honest-contract pattern). Added to the TF-1 plan.

## Dimensions checked
- [x] **Unfounded assumptions** — VERIFIED by execution: write_text fix leaves production `_BASELINE` unchanged (4 sites); tests `needs-human` → ∅ (0 residual); probe counts (287/160/49/1/1/2) reproduced exactly. No finding.
- [x] **Missing edge cases** — load (215 files), empty (floor, see m1), parse-error (fail-closed except fixtures-excluded, m3), Windows backslash rel (m2), `test_`-named production tool false-bucket (correctly handled), 3.12+ tokenizer (already wrapped). The collection-class heterogeneity → M1.
- [x] **Over-engineering** — none. Reuses the slice-100 ruleset; minimal surface field + classes; no speculative interface. (The M1 fix deliberately stops short of cross-surface Class-B mirror-proving to avoid over-asserting.)
- [x] **Under-engineering** — M2 (AC4 combined-baseline had no delivering element); M1 facet (must-not-defer "distinct named class" asserted but the Class-B-mirror sub-case wasn't distinguished — now fixed).
- [x] **Contract gaps** — CLI change additive (`surface` + new counts); production `(path,value,klass)` identity holds; exit codes unchanged. M2 was the only `--strict`-semantics gap.
- [x] **Security** — none. Read-only static analysis; `_vault_paths` default untouched (`VAULT_ROOT == Path("architecture")`).
- [x] **Drift from vault** — Standard mode; MEPD-1 EXCLUDE correct (extends existing tool, no new module/RULE-ID/VERSION); ADR-092 supersedes nothing (extends ADR-091, append-only respected); shippability row 108 update committed; PTFCD-1 catalog target exists. No finding.
- [x] **Web-known issues** — Python 3.12/3.13 tokenizer stricter (PEP 701); existing `generate_tokens` wrap + AST fail-close handle it; the `fixtures/**` exclusion (not 3.12 fragility) removes the lone parse-error fixture. Sources: cpython #105549, #105238; tokenize 3.13 docs; pathlib docs. No novel issue.
- [x] **Cross-cutting conformance** — APED-1: Critic executed the proposed rules against the real corpus (production stable; tests `needs-human` ∅; 209 = 160 + 49). Traced the ordered ruleset (rule 2 path-construction precedes rule 4 collection; tests mirrors lack the Class-B marker so they fell to rule 4 → the M1 root cause). PTFCD-1 function-level verified at build.

## Triage

**Triaged by**: user
**Date**: 2026-06-02
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | Split `test-collection-pathspec` out of the checklist; applied to design.md (What's-new/Evidence/Components #3-4/AC-map), ADR-092 (Options 3/Decision/Consequences), mission-brief AC2. |
| M2 | Major | ACCEPTED-FIXED | AC4 rewritten production-scoped (`--strict` guards the 4-set; tests gate-covered via needs-human-empty + floors); TF-1 plan harmonized (TPHD-1). |
| M-add-1 | Major | ACCEPTED-PENDING | User chose fix (b) honest-contract residual. At build: add `test_collection_member_genuine_resolve_is_review_residual`; downgrade "mostly stays" prose → current-corpus observation + loud-breakage justification (a mis-bucketed resolve breaks LOUDLY at flip, not silently) + explicit "flip-execute consumes BOTH lists" contract. (a) declined as gold-plating over a zero-instance case. |
| m1 | Minor | ACCEPTED-PENDING | At build: `test_tests_surface_class_floors` asserts per-class floors (FLOOR_A on test-update-at-flip AND FLOOR_B on test-collection-pathspec). |
| m2 | Minor | ACCEPTED-PENDING | At build: normalize rel (`rel.replace("\\","/")`) inside `audit_file` before the surface check. |
| m3 | Minor | ACCEPTED-PENDING | At build: add `test_fixtures_dir_vault_literal_out_of_scope` pinning the documented residual. |
