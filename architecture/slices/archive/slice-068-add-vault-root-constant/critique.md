# Critique: Slice 068 add-vault-root-constant

**Critic reviewed**: mission-brief.md, design.md, ADR-065-vault-root-constant-with-env-override.md (rev-1), plus on-disk verification of all 8 (then 9) cited migration sites + pre-existing R-15 audit regex + the 41-occurrence `tests/methodology/` corpus
**Date**: 2026-05-25
**Result**: NEEDS-FIXES (post-Builder-fix-block: all Blockers and Majors ACCEPTED-FIXED; 1 Minor ACCEPTED-FIXED; 1 Minor ACCEPTED-PENDING for /reflect)

## Summary

Substantive Critic pass that found one real Blocker (a 9th filesystem-resolving site missing from the "exhaustive" allowlist — `tools/build_checks_integrity.py:78` `_PROJECT_LIVE_REL`), three real Majors (consumer-freeze cascade hazard at the read-at-import-time semantic that the design rev-1 hand-waved; a fabricated "conftest L37 precedent" citation in both ADR-065 and design.md; under-scoped prose-vs-path distinction relative to the 41-occurrence `tests/methodology/` corpus + R-15 audit regex backstop), and two Minors. All findings are accepted in this round; the test-tree migration is scoped-back to DEFERRED via the M3 fix, simplifying slice-068's blast radius. Final allowlist is **8 `tools/*.py` modules** (was 7+1 conftest; now 8 tools-only). TF-1 plan grows from 9 to 10 rows (consumer-freeze pin added).

## Findings

### Blockers (must address before /build-slice)

#### B1: 9th filesystem-resolving literal — `tools/build_checks_integrity.py:78` `_PROJECT_LIVE_REL` — was MISSING from the "exhaustive" 8-site allowlist

- **Claim under review**: ADR-065 rev-1 §Context lines 14-25 and design.md §Components touched table asserted the corroborated grep finds 8 distinct files with such literals (rev-1 also footnoted `shippability_decoupling_audit.py:91-92` as the only documented exclusion). Mission-brief AC4 claimed the 7-module allowlist is "exhaustive"; must-not-defer #8 doubled down: *"The 7-module migration allowlist is exhaustive."* Design.md §Components touched table corrected to 8 but still missed the 9th.
- **Issue**: `tools/build_checks_integrity.py:78` defines `_PROJECT_LIVE_REL = "architecture/build-checks.md"`. Consumed at L223 (`root / _PROJECT_LIVE_REL`) in `check_live()` — a genuine filesystem resolution, not a prose assertion, not an AST-pattern allowlist. The structural shape mirrors `slice_queue_writer.py`'s `_INDEX_MD_REL` constant exactly. Per fresh `Grep` for `_[A-Z_]*REL\s*=` across `tools/*.py`, this is the only un-enumerated peer of the `slice_queue_writer.py` private-constant pattern in the cited 8 sites.
- **Evidence**: `tools/build_checks_integrity.py:78` literal `_PROJECT_LIVE_REL = "architecture/build-checks.md"`; `tools/build_checks_integrity.py:222-223` actual filesystem use: `root / _PROJECT_LIVE_REL`; independent grep `Path\(["']architecture` + `^_[A-Z_]*REL\s*=` + `"architecture/` rediscovered 9 distinct files.
- **Proposed fix**: Add `tools/build_checks_integrity.py:78` as site #1 in design.md §Components touched (alphabetically — `build_checks_integrity.py` < `critique_review_prerequisite_audit.py`); update mission-brief AC4 module list to 8 (was 7); update mission-brief must-not-defer #8 (8-element allowlist); update ADR-065 §Context list to 9 distinct files initially; extend `_MIGRATION_SITE_ALLOWLIST` to 8 entries (`conftest.py` scoped-back per M3); re-run grep AFTER adding site #1 to verify count alignment.
- **Builder draft**: **ACCEPTED-FIXED** — All sweep edits applied per TPHD-1 sub-mode (a):
  - mission-brief.md AC4 updated to 8 modules + new TF-1 row 10 + must-not-defer #8 reframed as 8-element allowlist + Dependencies vault refs renumbered to 8 sites + pytest baseline 908 → 909
  - design.md §Components touched table re-keyed alphabetically with `build_checks_integrity.py` at row 1 (8 rows total; conftest.py removed per M3 fix); §Sites EXCLUDED expanded with M1/M2/M3 rationale + error-message-string class; §Site-level edge cases extends with `build_checks_integrity.py:78` `str → Path` type-change note (consumer at L222-223 unchanged — `Path / Path` composes identically to `Path / str`); §What's new updated from "9 unit tests" → "10 unit tests"; §Key interactions notes "imported by 8 migrated `tools/*.py` modules ... composition corrected per /critique B1 + M3"
  - ADR-065 §Context numbered list updated to 8 `tools/*.py` files (with B1 attribution); §Decision migration scope updated; §Reversibility count unchanged
  - Fresh post-edit `Grep` re-verification: `Path\(["']architecture|["']architecture/|^_[A-Z_]*REL\s*=` across `tools/*.py` produces exactly 8 distinct files matching the new allowlist. Closed.

### Majors (address this slice)

#### M1: Read-at-import-time semantics creates a real test-isolation hazard that rev-1 hand-waved; subprocess test alone is insufficient backstop

- **Claim under review**: design.md rev-1 §Components touched: *"In-process unit tests that need to vary the value use `monkeypatch.setattr(tools._vault_paths, "VAULT_ROOT", Path("/tmp/foo"))`"*. ADR-065 rev-1 §Decision repeated this. Mission-brief Mid-slice smoke gate: *"likely cause: env var read at module-load not preserved across subprocess; fix by re-reading at attribute-access time via property"*.
- **Issue**: The `monkeypatch.setattr(tools._vault_paths, 'VAULT_ROOT', ...)` mitigation works for `tools._vault_paths.VAULT_ROOT` itself, but does NOT propagate to the 8 downstream consumers whose module-level constants captured VAULT_ROOT at THEIR import time. Concretely:
  - `tools/slice_queue_writer.py:79` post-migration `_INDEX_MD_REL = VAULT_ROOT / "slices" / "_index.md"` is FROZEN at the value VAULT_ROOT held when `slice_queue_writer` was first imported.
  - `tools/risk_register_audit.py:381` `default=VAULT_ROOT / "risk-register.md"` argparse default evaluates at module-import.
  - pytest collection imports modules in unpredictable order — first test to trigger a `from tools.slice_queue_writer import _INDEX_MD_REL` chain freezes the value session-wide.
- **Evidence**: Empirically demonstrated freeze with `python -c "..."` showing captured value at import is NOT updated by subsequent env mutation. Web-searched documented anti-pattern: GitHub pytest-dev/pytest issue #4226 + discussion #10027.
- **Proposed fix**: Either (a) switch to lazy `vault_root() -> Path`; OR (b) document the freeze contract explicitly + add a TF-1 row pinning the freeze semantic. Update ADR-065 §Options-considered §3 to acknowledge the consumer-freeze cascade is NOT illusory.
- **Builder draft**: **ACCEPTED-FIXED** — Option (b) selected (keep module-level constant, document the freeze contract as production-correctness semantic, add empirical regression-pin):
  - design.md §Consumer-freeze cascade NEW sub-section added under §Components touched — pins the freeze as deliberate production semantic (env read once at process start); names subprocess fixtures as the cross-process test path; names `monkeypatch.setattr` as the in-module-only path with explicit warning that frozen downstream constants don't propagate; cites GitHub pytest-dev/pytest #4226 + #10027 as documented anti-pattern references
  - design.md §Test-first plan finalization adds row 10 `test_consumer_constants_are_frozen_at_first_import` — empirical pin: import `tools.slice_queue_writer`, capture `_INDEX_MD_REL`, `monkeypatch.setattr(tools._vault_paths, "VAULT_ROOT", ...)`, assert `_INDEX_MD_REL` UNCHANGED
  - design.md §Error model gains argparse-default-eval-freeze sentence (subsumes m1)
  - ADR-065 §Options-considered §3 rewritten to acknowledge the freeze cascade is real and option 3 would avoid it; still choose option 2 with explicit freeze contract documentation rather than dismissing option 3
  - ADR-065 §Decision §Read-at-import semantics + consumer-freeze cascade sub-bullet rewritten to make the freeze contract a first-class deliverable, not an implicit assumption
  - mission-brief.md AC4(d) added documenting the freeze pin; TF-1 plan row 10 added; pytest baseline 908 → 909. Closed.

#### M2: ADR-065 + design.md falsely cited "conftest.py L37" as precedent for `from tools._vault_paths import ...` — the precedent does not exist

- **Claim under review**: ADR-065 rev-1 §Consequences: *"`tests/methodology/conftest.py` gains an import from `tools._vault_paths` — already-precedented at conftest L37 (`from tools.resolve_slice_dir import REPO_ROOT` or similar), so no new test-tree-to-tools-tree coupling risk."* Design.md rev-1 §Components touched row 8 echoed the same false citation.
- **Issue**: Reading `tests/methodology/conftest.py` end-to-end (109 lines) shows NO line 37 `from tools.*` import. Actual imports at L2-4: `from pathlib import Path` + `import pytest`. `REPO_ROOT` is defined LOCALLY at L6: `REPO_ROOT = Path(__file__).resolve().parents[2]`. `Grep "^(from|import) tools"` against conftest.py: 0 matches. The cited `tools.resolve_slice_dir` module doesn't exist either — the `_resolve_slice_dir` helper is DEFINED in conftest.py at L20-105, not imported from `tools/`.
- **Evidence**: `tests/methodology/conftest.py:1-50` — read end-to-end above, no `from tools.*` line anywhere. `tests/methodology/conftest.py:6` actual content `REPO_ROOT = Path(__file__).resolve().parents[2]`. `Grep "^(from|import) tools" tests/methodology/conftest.py` — 0 matches.
- **Proposed fix**: Remove the false precedent citation. State accurately that conftest.py gaining a `from tools._vault_paths import ...` would be the FIRST test-tree-to-tools-tree import for this conftest module, and document the genuine concern about pytest's conftest-collection ordering.
- **Builder draft**: **ACCEPTED-FIXED** — The false-precedent concern dissolves entirely via the M3 fix below (scope-back of conftest.py to DEFERRED → no new test-tree-to-tools-tree import is introduced by slice-068 at all):
  - ADR-065 §Consequences "tests/methodology/conftest.py gains an import from `tools._vault_paths`" bullet REWRITTEN to: *"No test-tree-to-tools-tree import dependency introduced by this slice (per /critique M2 ACCEPTED-FIXED — rev-1 falsely cited a non-existent `conftest.py L37` precedent for such an import; the actual `tests/methodology/conftest.py` has zero `from tools.*` imports, with `REPO_ROOT` defined locally at L6 `REPO_ROOT = Path(__file__).resolve().parents[2]`). The test-tree migration is DEFERRED per /critique M3, eliminating the question entirely for slice-068."*
  - design.md §Wiring matrix gains a note: *"no `tests/methodology/conftest.py` migration in this slice (DEFERRED per /critique M3); no new test-tree-to-tools-tree import dependency"*
  - design.md §Components touched table row 8 (the conftest entry) removed; replaced by `build_checks_integrity.py` per B1 with all-tools composition. Closed.

#### M3: Prose-vs-path distinction does not survive contact with the 41-occurrence `tests/methodology/` corpus; the AC2 marker convention is under-specified relative to the existing R-15 regex

- **Claim under review**: Mission-brief AC2 + must-not-defer #2: prose-asserting matchers are NOT migrated. Design.md L139 TF-1 row planned `test_methodology_changelog_test_fixtures_preserve_literal` for the regression-pin.
- **Issue**: Grep found `"architecture"` in 26 distinct `tests/` files; further filtering with `REPO_ROOT / "architecture"` returned 42 occurrences across 16 files. Many are FILESYSTEM-RESOLVING (e.g., `test_methodology_changelog.py:657` `decisions_dir = REPO_ROOT / "architecture" / "decisions"` reads ADR files from disk). The prose-vs-path distinction works for true prose matchers (BC-1 keyword tests) but conflates two test categories under "preserve literal". Also: the pre-existing `_R15_LITERAL_PATH_RE` regex at `tests/methodology/test_resolve_slice_dir.py:233` scans for `REPO_ROOT\s*/\s*"architecture"\s*/\s*"slices"` patterns — if conftest's slice-068 migration replaces literals with `REPO_ROOT / VAULT_ROOT / "slices"`, the audit's regex misses the new shape, silently bypassing R-15 enforcement.
- **Evidence**: `Grep "REPO_ROOT / \"architecture\"" tests/ -c` → 42 matches across 16 files. `tests/methodology/test_methodology_changelog.py:657`. `tests/methodology/test_resolve_slice_dir.py:233` pre-existing regex.
- **Proposed fix**: Document explicit per-file disposition for all 16 `tests/` files OR extend `_R15_LITERAL_PATH_RE` to ALSO match the VAULT_ROOT-routed shape.
- **Builder draft**: **ACCEPTED-FIXED via scope-back** — chose neither sub-option; chose simpler third path: scope `tests/methodology/conftest.py` (and all other test-tree migration) OUT of slice-068 entirely, DEFER to a follow-on slice that can address tests/ as a coherent unit:
  - design.md §Sites EXCLUDED from migration gains the `tests/methodology/conftest.py` and 15-other-files DEFERRED entry with 4-part rationale: (a) R-15 audit regex would silently atrophy without coordinated extension; (b) per-file prose-vs-path disposition needs documentation across 16 files; (c) scope-back avoids opening the first test-tree-to-tools-tree import dependency (subsumes M2); (d) the slice-069 follow-on can address tests/ as a coherent unit, or even more cleanly tests/ migration may not be needed at all if `AI_SDLC_VAULT_ROOT` is never set during test runs
  - mission-brief.md AC4 module list updated: conftest.py removed; the 8-element allowlist is now pure `tools/*.py`
  - mission-brief.md must-not-defer #8 reframed: 7-module → 8-module exhaustive
  - mission-brief.md Dependencies vault refs renumbered: 7 sites → 8 sites, with `tests/methodology/conftest.py` moved to DEFERRED list
  - design.md §Components touched table: row 8 (conftest) removed; replaced by `build_checks_integrity.py` per B1
  - design.md §Wiring matrix gains "no test-tree migration" note
  - design.md TF-1 plan: row 5 renamed from `test_methodology_changelog_test_fixtures_preserve_literal` to `test_shippability_decoupling_audit_tuples_preserve_literal` (the test-tree-fixture pin was the prose-vs-path concern that the scope-back retired; the surviving regression-pin is for the in-tools AST-pattern allowlist that MUST stay literal)
  - **R-15 audit regex `_R15_LITERAL_PATH_RE` is UNCHANGED** — no migration in `tests/methodology/` means no audit regex disturbance, no silent atrophy. R-15 backstop preserved. Closed.

### Minors (log; address if cheap)

#### m1: `tools/risk_register_audit.py:381` argparse `default=` evaluates at import-time — design names this correctly but doesn't surface the consumer-freeze interaction

- **Claim under review**: design.md rev-1 §Site-level edge cases: *"both env-var override and import-time evaluation flow through correctly"*.
- **Issue**: The "flow through correctly" claim is technically true but interacts with M1's consumer-freeze cascade. Worth surfacing in design.md §Error model.
- **Evidence**: same as M1, plus argparse documented behavior at python.org/3/library/argparse.html#default.
- **Proposed fix**: Add a sentence to design.md §Error model noting argparse default-eval interacts with VAULT_ROOT freeze.
- **Builder draft**: **ACCEPTED-FIXED** — subsumed by M1's fix:
  - design.md §Error model gains the argparse-default-eval-freeze sentence explicitly
  - Cross-references M1's §Consumer-freeze cascade for the full contract. Closed.

#### m2: discovered slice-067 PSQ-1 defect is correctly out-of-scope; reflection.md round-tripping should also create a `diagnose-out/backlog.md` SC-NNN candidate so BCR-1 round-trip can close it later

- **Claim under review**: design.md rev-1 §Scope discipline reminder: discovered defect noted for reflection only.
- **Issue**: If `diagnose-out/backlog.md` exists (per BCR-1), canonical surface for "future candidate" is an SC-NNN entry there with `**Closes:**` semantics, not just a reflection note. Otherwise the defect lives in slice-068 reflection where future `/slice` may not surface it as a candidate.
- **Evidence**: BCR-1 in CLAUDE.md: *"when `diagnose-out/backlog.md` exists in the repo, `/slice` MUST consult it as a primary candidate source"*. Verified `diagnose-out/backlog.md` exists at session start.
- **Proposed fix**: At reflection.md authoring time, add an SC-NNN entry to `diagnose-out/backlog.md` naming the slice_queue_writer raw-dict-leak defect with provenance pointer to `architecture/slice-queue.md:18,34,42`.
- **Builder draft**: **ACCEPTED-PENDING** — `diagnose-out/backlog.md` exists (verified at /slice time); per BCR-1 this is the canonical "future candidate" surface, not reflection.md prose. At slice-068's `/reflect` Step 5b-avfs (OSDG-1-guarded), add SC-NNN entry naming the slice-067 PSQ-1 raw-dict-leak with: `**Title:**` "Fix slice_queue_writer blast-radius renderer leaking raw graphify node dicts"; `**Severity:** medium` (per /critique-review m2 severity adjustment ACCEPTED-FIXED — multi-consumer-artifact rule: PSQ-1's premise is multi-session shared visibility per ADR-064, and a parsing defect against shared multi-session state is by definition Medium not Low); `**Blast:** medium` (per same adjustment — downstream consumers across N sessions, not 1); `**Reversibility:** cheap`; `**Effort:** small`; `**Description:**` cites `architecture/slice-queue.md:18,34,42` as the symptom + `tools/slice_queue_writer.py` `_call_graphify_blast_radius` (or its rendering caller) as the suspected fault location; `**Evidence:**` quotes the leaked dict-string from the queue file; `**Suggested approach:**` extract the `path` field from graphify node objects before passing to the renderer, or convert node→str at the call boundary. Reflection MUST also note the BCR-1 entry as a backlog round-trip target (NOT a `**Closes:**` for slice-068 itself — slice-068 only DISCOVERS it; a future slice CLOSES it). Will action at /reflect.

## Dimensions checked

- [x] **Unfounded assumptions** — Two findings: (1) M2 — false "conftest L37 precedent" citation in both ADR-065 and design.md; cited line does not exist and import pattern is not precedented in conftest. (2) Implicit assumption that the "exhaustive 7-module grep" was actually exhaustive — disproven by B1.
- [x] **Missing edge cases** — One finding (M1): read-at-import-time semantics with consumer-constant freeze cascade. Web search confirms well-known production anti-pattern. Other edges covered: empty env var, whitespace, invalid path — called out in design §Error model.
- [x] **Over-engineering** — None. Leaf-utility shape with `tools/_stdout.py` precedent is appropriate; env-var override is justified by slice-069 → slice-070 chain. ADR-065 §Options-considered correctly rejects options 4 and 5 as over-engineered.
- [x] **Under-engineering** — One finding (B1): AC4 said allowlist is exhaustive but missing a peer site. Also: mission-brief AC4 (7) vs design.md table (8) asymmetry — TPHD-1 sub-mode (a) sweep miss.
- [x] **Contract gaps** — None. No new endpoints, events, schemas, or external contracts. The "VAULT_ROOT export" contract is just "name + type + default + override-env-var", all documented.
- [x] **Security** — None. No new authn/authz, no input-validation surface added. Env-var injection of paths is a classic path-traversal vector in untrusted contexts, but this codebase runs as single-developer tool with no untrusted env input; threat model unchanged.
- [x] **Drift from vault** — None directly. ADR-065 supersedes nothing (correctly). MEPD-1 EXCLUDE posture correctly applied. The `architecture/` gitignore convention is preserved.
- [x] **Web-known issues** — One finding folded into M1: GitHub pytest-dev/pytest issue #4226 + discussion #10027 confirm the module-level-env-var-read-at-import-time gotcha as well-known production hazard.
- [x] **Cross-cutting conformance** — Three findings: (1) Slice-067 first-governed-slice probe applied — B1 surfaces the missed-sibling-site class. (2) TPHD-1 sub-mode (a) + FBCD-1 sub-mode (a) — count "7" in mission-brief AC4 vs "8" in design.md table vs "8" in ADR-065 §Context is a 3-site count-drift (exactly the slice-067 M-add-2/3/4 fix-block-completeness class). (3) Tooling-doc-vs-implementation parity — design.md table's "8 sites" claim was verifiable by mechanical grep; verification produces 9 (now 8 after M3 scope-back).

## Sources

- [Way to isolate tests from existing environment variables? - pytest-dev/pytest issue #4226](https://github.com/pytest-dev/pytest/issues/4226)
- [Setting environment variables which are accessed at import time - pytest-dev/pytest discussion #10027](https://github.com/pytest-dev/pytest/discussions/10027)
- [pytest-env on PyPI](https://pypi.org/project/pytest-env/)
- [argparse - Python 3 docs (default-eval semantics)](https://docs.python.org/3/library/argparse.html#default)

## Triage

**Triaged by**: user
**Date**: 2026-05-25
**Final verdict**: NEEDS-FIXES

Both passes reconciled per /critique Step 4.5. User ratified all 7 dispositions as Builder-drafted (single-batch "ratify all 7 as drafted" structured-options ratification per SOAD-1).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | 9th site `tools/build_checks_integrity.py:78` added; mission-brief AC4 + must-not-defer #8 + Dependencies + design.md §Components-touched + ADR-065 §Context all swept to 8-element allowlist (TPHD-1 sub-mode (a)). Re-grep empirically verified post-fix. |
| M1 | Major | ACCEPTED-FIXED | Consumer-freeze cascade pinned as deliberate production semantic; new TF-1 row 10 `test_consumer_constants_are_frozen_at_first_import`; design.md §Consumer-freeze cascade sub-section + §Error model argparse-default-eval sentence; ADR-065 §Options-considered §3 rewritten to acknowledge option 3 benefit is not illusory; ADR-065 §Decision §Read-at-import-semantics expanded with freeze contract as first-class deliverable. |
| M2 | Major | ACCEPTED-FIXED | False "conftest.py L37 precedent" citation removed from both ADR-065 §Consequences and design.md §Components-touched; the concern is dissolved entirely by the M3 scope-back (no test-tree-to-tools-tree import is introduced by this slice). |
| M3 | Major | ACCEPTED-FIXED | Scope-back: `tests/methodology/conftest.py` + all other tests/ migration DEFERRED to a follow-on slice with 4-part rationale (R-15 audit regex preserved, per-file disposition needed across 16 files, avoids first test-tree-to-tools-tree import, slice-069 follow-on can address tests/ coherently). R-15 audit regex `_R15_LITERAL_PATH_RE` at `tests/methodology/test_resolve_slice_dir.py:233` UNCHANGED. Subsumes M2's concern. |
| m1 | Minor | ACCEPTED-FIXED | argparse default-eval freeze interaction surfaced in design.md §Error model; subsumed by M1's broader freeze-contract documentation. |
| m2 | Minor | ACCEPTED-PENDING | Will add SC-NNN entry to `diagnose-out/backlog.md` at /reflect Step 5b-avfs per BCR-1 (canonical "future candidate" surface for the discovered slice-067 PSQ-1 raw-dict-leak); SC-NNN scoring per /critique-review m2 severity adjustment: `Severity: medium`, `Blast: medium` (was `low`/`small` — multi-consumer-artifact rule applies because PSQ-1's premise is multi-session shared visibility per ADR-064). |
| M-add-1 | Major (meta-Critic missed finding) | ACCEPTED-FIXED | Two-marker convention asymmetry between mission-brief AC2 + must-not-defer #2 + Verification-plan row 2 (one-marker) and design.md TF-1 row 4 (two-marker). Builder swept three sibling-cell sites in second fix-block: mission-brief AC2 rewritten to enumerate both `# VAULT_ROOT-routed (slice-068)` AND `# NOT VAULT_ROOT-routed (slice-068) — error-message prose` markers with the 5 EXCLUDED-site enumeration inline; mission-brief must-not-defer #2 rewritten similarly; mission-brief Verification-plan row 2 rewritten to enumerate the two-marker convention + name `shippability_decoupling_audit.py:91-92` AST-pattern allowlist + cite the DEFERRED tests/ migration. Pattern signal: strengthens slice-067 N=3 → N=4 cumulative meta-Critic observation that *"Builder applies multi-finding fixes without sweeping all sibling-cell sites"*; candidate `/critic-calibrate` input. |
