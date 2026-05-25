# Design: Slice 019 — harden-diagnose-layering-evidence

**Date**: 2026-05-13
**Mode**: Standard

## What's new

- New methodology rule **LAYER-EVID-1** codified at `methodology-changelog.md` v0.33.0
- New textual-import-evidence requirement carried as prose at N=3 surfaces (the canonical phrase `textual import-evidence requirement` is pinned bidirectionally across surfaces; matches slice-016 RPCD-1 / slice-017 TPHD-1 3-surface precedent):
  - Surface 1: `skills/diagnose/passes/03f-layering.md` — Method (NEW step 4: "Grep-verify the import statement") + Severity rubric (NEW downgrade rule) + Anti-patterns (NEW negative-pin)
  - Surface 2: `skills/diagnose/SKILL.md` Step 5 — one-line cross-reference to LAYER-EVID-1 (matches the slice-002 canonical-contract cross-reference pattern; does NOT duplicate the rule body)
  - Surface 3: `methodology-changelog.md` v0.33.0 / LAYER-EVID-1 entry (in-repo AND installed copy)
- New regression fixtures + integration test:
  - `tests/skills/diagnose/fixtures/parallel_types_no_import/` — synthetic codebase with parallel same-name type files but zero cross-tier imports (the F-LAYER-bca9c001 shape)
  - `tests/skills/diagnose/fixtures/parallel_types_real_import/` — positive-control synthetic codebase with a real cross-tier import (so we can prove the rule doesn't suppress true-positives)
  - `tests/skills/diagnose/test_layering_pass_textual_evidence.py` — drives both fixtures through a test-local helper `_grep_textual_import(target_dir, evidence_file, bypassed_layer_path) -> bool` that implements the rule's grep semantics (TypeScript + Python patterns); asserts no-match → no HIGH finding, match → HIGH finding stands
- New prose-pin tests extending `tests/skills/diagnose/test_skill_md_pins.py`:
  - `test_skill_md_step5_documents_textual_evidence_rule` — Step 5 contains the LAYER-EVID-1 cross-reference
  - `test_layering_pass_template_emits_textual_evidence_rule` — 03f-layering.md contains the rule body
  - `test_textual_evidence_rule_byte_equal_across_n_3_surfaces` — canonical phrase appears at all 3 surfaces (in-repo) and at all 3 installed surfaces (bidirectional sha256 byte-equal)
- New mini-CAD tests at `tests/skills/diagnose/test_diagnose_skill_drift.py` (per B3 single-file convention, slice-007 CAD-1 + slice-010 mini-CAD precedent; this slice's first introduction of mini-CAD for `/diagnose`):
  - `test_in_repo_and_installed_diagnose_skill_md_are_content_equal` — `skills/diagnose/SKILL.md` byte-equal
  - `test_in_repo_and_installed_diagnose_03f_layering_md_are_content_equal` — `skills/diagnose/passes/03f-layering.md` byte-equal
- New methodology-changelog entry-pin tests + slice-018 sibling-scoping inheritance test (per M4 + the "## Test-scoping inheritance" section below):
  - `test_v_0_33_0_layer_evid_1_entry_present_in_repo_and_installed`
  - `test_v_0_33_0_layer_evid_1_entry_names_textual_import_evidence_canonical_phrase`
  - `test_v_0_33_0_layer_evid_1_sibling_scoping_rejects_stripped_v033_body` (regression test mirroring slice-018 L1010-1060 pattern; uses new `_extract_v033_body` helper)
  - `test_adr_017_exists_and_names_layer_evid_1_canonical_phrase`
- New risk-register entry **R-3** (RR-1 schema) + audit test `test_r_3_added_post_slice_019_with_graphify_symbol_conflation_class`
- New `ADR-017-textual-evidence-requirement-for-diagnose-boundary-findings.md`
- Version bump: `VERSION` + `plugin.yaml` atomic bump to `0.33.0` (PMI-1 v1.1 version-agnostic gate; 5th atomic bump post slice-014 retirement of supersession pattern)
- New shippability.md row 19 (SCPD-1 sub-mode (b) proactive-application BEFORE `/validate-slice` Step 5.5)

## What's reused

- `skills/diagnose/passes/03f-layering.md` Method / Severity rubric / Anti-patterns sections — EXTENDED, not replaced
- `skills/diagnose/SKILL.md` Step 5 dispatch table — gains the LAYER-EVID-1 cross-reference paragraph; the dispatch table itself is unchanged (no new pass added, no model reassignment)
- `skills/diagnose/schema/finding.yaml` — UNCHANGED. The rule operates on the subagent's emit-decision logic, not the YAML shape. The optional `note:` field in `evidence[].note` is used to record downgrade rationale (existing field; no schema change)
- `tests/skills/diagnose/test_skill_md_pins.py` — EXTENDED with new prose-pin tests (matches slice-016 / slice-017 prose-pin discipline)
- `tests/methodology/test_methodology_changelog.py` — EXTENDED with new entry-pin section `# --- Slice-019 / LAYER-EVID-1 entry pinning ---` matching slice-017 TPHD-1 precedent
- `tests/methodology/test_risk_register_audit_real_file.py` — EXTENDED with new R-3 audit row
- [[ADR-001-diagnose-subagent-io-contract]] — base contract; this slice does NOT touch ADR-001 (no I/O contract change; subagent tool envelope unchanged)
- [[slice-007 CAD-1]] + [[slice-010 mini-CAD for slice/SKILL.md]] — mini-CAD bidirectional-byte-equality pattern reused for `/diagnose` SKILL.md + 03f-layering.md
- [[slice-014 PMI-1 v1.1]] — version-agnostic gate; this slice's 0.33.0 bump uses the post-retirement atomic-bump shape
- [[slice-015 SCPD-1]] sub-mode (b) — proactive shippability.md propagation BEFORE catalog run
- [[slice-016 RPCD-1]] sub-modes (a) + (b) — NEW pytest function names declared in TF-1 plan (verify exist on-disk at /build-slice Phase 6); _ALLOWED_STATUSES-style allowlists N/A (no new audit module)
- [[slice-017 TPHD-1]] all 3 sub-modes — applies during /critique + /critique-review fix-prose if function names or AC #N row references change

## Step 5 dispatch enumeration (per AC #1 + must-not-defer #1; resolves /critique B1 + M3 + /critique-review M-add-1)

Per AC #1's must-not-defer commitment to enumerate the propagation surface from `skills/diagnose/SKILL.md:124-135` dispatch table, each of the 11 passes is reviewed below for LAYER-EVID-1 applicability. The ground-truth grep `grep -h '^- \`category\`:' skills/diagnose/passes/*.md` returns exactly ONE match — `passes/03f-layering.md:47` carries `category: layering-violation`. The schema enum at `schema/finding.yaml:21-32` enumerates ALL valid category values: `dead-code | duplicate | size-outlier | half-wired | contradiction | layering-violation | dead-config | test-gap | ai-bloat`. No `boundary-violation`, `cross-tier`, or `import-violation` enum exists — these are speculative shorthand in the original mission-brief, retired at /build-slice per /critique-review M-add-1.

| Pass | Category emitted | LAYER-EVID-1 applies? | Rationale |
|------|------------------|----------------------|-----------|
| 01-intent | (none — no findings YAML; intent-reconstruction prose only) | NO | Per `passes/01-intent.md` Block contents: section + summary blocks only, no findings YAML. Out of scope by emission shape. |
| 02-architecture | (none — `findings: []` explicit per `passes/02-architecture.md:69-71`) | NO | Method step 5 ("Where the code disagrees with itself") explicitly defers code-level bypass findings to 03f. Architectural prose may narrate bypass patterns but the YAML is empty by contract. R-3 escalation path covers prose-narrative regression. |
| 03a-dead-code | `dead-code` | NO | Reachability-based; cites absence of import-edges, not their misclassification. Different evidence shape. |
| 03b-duplicates | `duplicate` | NO | Flags shape-equivalence across modules (same function logic in 2 files); evidence is content-similarity, not import-edge. Parallel-type-file pattern WOULD legitimately flag here as a duplicate (true-positive); the rule's textual-evidence requirement doesn't apply because nothing about duplicate-detection turns on whether an import edge exists. |
| 03c-size-outliers | `size-outlier` | NO | Distribution-statistics based; cites line counts, not import-edges. |
| 03d-half-wired | `half-wired` | NO | UI↔backend endpoint-existence checks ("button posts to nonexistent endpoint"). Evidence is endpoint-registration absence, not phantom import-edges. Different failure surface; R-3 escalation path covers if symbol-conflation-class issues surface here. |
| 03e-contradictions | `contradiction` | NO | Uses graphify `shortest_path` between modules (per `passes/03e-contradictions.md:28-36`) but for cross-module assumption-divergence (e.g., same entity validated differently in two places), not import-boundary violations. R-3 escalation path covers theoretical exposure. |
| 03f-layering | `layering-violation` (sole emitter) | **YES** | The witness pass for F-LAYER-bca9c001. Apply LAYER-EVID-1 in Method step 4 + Severity rubric + Anti-patterns per the "Modified — `skills/diagnose/passes/03f-layering.md`" subsection below. |
| 03g-dead-config | `dead-config` | NO | Config-registry vs consumer cross-reference; cites unused config keys, not import-edges. |
| 03h-test-coverage | `test-gap` | NO | Reachability + test-import cross-reference; cites absence of test coverage on production code, not import-boundary violations. |
| 04-ai-bloat | `ai-bloat` | NO | Cross-references `findings/03b-duplicates.yaml` + `findings/03d-half-wired.yaml`; cites AI-implementation-pattern signatures (multiple impls, stale scaffolding). Different evidence shape. |

**Summary**: 1 pass IN (03f-layering), 10 passes OUT with rationale grounded in emission shape + category-enum membership. R-3 explicit escalation criteria — if `/critic-calibrate` flags symbol-conflation false-positives in ANY of the 10 OUT passes (N≥2 distinct slices required for promotion), extend LAYER-EVID-1 via follow-on slice OR fix graphify symbol-resolution upstream (option A from ADR-017). The propagation surface materially is the same set already targeted in "Components touched" below.

## Components touched

### Modified — `skills/diagnose/passes/03f-layering.md`

- **Responsibility**: Pass template for the layering-violation subagent. Now requires textual-import-evidence verification before HIGH-severity emission.
- **Lives at**: `skills/diagnose/passes/03f-layering.md` (modified by this slice)
- **Key interactions**: Read by `skills/diagnose/SKILL.md` Step 3 (template-load); embedded into subagent prompt at Step 5 dispatch; subagent uses Grep/Read/Glob (per canonical contract) to apply the rule against `$TARGET` files
- **Changes** (mechanical):
  - **Method section** gains a NEW step 4 (after existing step 3 "Distinguish intentional from accidental bypass") carrying the full LAYER-EVID-1 rule body. Per /critique B2 + M1, the prose enumerates ALL language-syntactic variants the rule must cover, including the variants the witnessed F-LAYER-bca9c001 used (`@/*` alias-resolved imports). The regex strings are byte-equal to those in `_grep_textual_import` (test-local helper at `tests/skills/diagnose/test_layering_pass_textual_evidence.py`) — visual byte-equality at codification time is the prose-pin equivalent of CAD-1 byte-equality at the rule-content level. Body (proposed; locked at Phase 3):

```
4. **Grep-verify the import statement before emitting a HIGH-severity finding** (LAYER-EVID-1, methodology-changelog.md v0.33.0). For each candidate finding, grep $TARGET for an actual textual import statement matching the alleged bypass. Multi-line semantics: use `re.DOTALL` / ripgrep `--multiline` to span newlines (TypeScript codebases routinely break long named-import lists across lines).

   **TypeScript / JavaScript (5 import variants + 3 re-export variants)**:
   - `^\s*import\s+\w+\s+from\s+['"]<bypassed-path>['"]`                    # default import: `import X from "..."`
   - `^\s*import\s+\{[^}]*\}\s+from\s+['"]<bypassed-path>['"]`              # named import: `import { X, Y } from "..."` (multi-line via DOTALL)
   - `^\s*import\s+\*\s+as\s+\w+\s+from\s+['"]<bypassed-path>['"]`         # namespace import: `import * as X from "..."`
   - `^\s*import\s+type\s+\{[^}]*\}\s+from\s+['"]<bypassed-path>['"]`       # type-only named import: `import type { X } from "..."`
   - `^\s*import\s+['"]<bypassed-path>['"]\s*;?\s*$`                        # side-effect import (no `from`): `import "..."`
   - `^\s*export\s+\{[^}]*\}\s+from\s+['"]<bypassed-path>['"]`              # re-export named: `export { X } from "..."`
   - `^\s*export\s+\*\s+from\s+['"]<bypassed-path>['"]`                     # re-export all: `export * from "..."`
   - `^\s*export\s+type\s+\{[^}]*\}\s+from\s+['"]<bypassed-path>['"]`       # re-export type-only: `export type { X } from "..."`
   - `require\(\s*['"]<bypassed-path>['"]\s*\)`                             # CommonJS: `require("...")`
   - `\bimport\(\s*['"]<bypassed-path>['"]\s*\)`                            # dynamic: `import("...")`

   **Alias-aware grep** (load-bearing — the witnessed F-LAYER-bca9c001 used `@/*` alias resolution): if `<bypassed-path>` is repo-relative (e.g., `src/workflow/adapters/types.ts`) AND `$TARGET` has `tsconfig.json` or `jsconfig.json` with non-empty `compilerOptions.paths` or `compilerOptions.baseUrl`, the subagent MUST also grep for the alias-resolved logical name (e.g., if `paths` maps `@/*` → `src/*`, also grep for `from ['"]@/workflow/adapters/types['"]`). Failing to check both forms means the rule fails closed on the alias-pattern that produced the original witness.

   **Python**:
   - `^\s*from\s+<module>\s+import\s+`                                       # `from module import X`
   - `^\s*import\s+<module>(\s|$|\.)`                                        # `import module` / `import module.sub`

   **Rust**: `\buse\s+[\w:]*<module-name>(::|;|\s)` (e.g., `use crate::backend::types;`).
   **Go**: `^\s*import\s+(\(\s*)?["']<path>["']` (single or block form).
   **Java**: `^\s*import\s+(static\s+)?<fqn>(\.\*)?\s*;` (single import, optionally static, optionally `*`).
   **Other languages**: fall back to grepping the bypassed-layer path string anchored within 1-3 tokens of any of `import|from|use|include|require` keywords.

   If zero textual matches exist in the evidence file across all applicable variants, the graphify edge is a phantom (often from cross-file same-name symbol collapse) — DOWNGRADE the finding to severity `low` with `evidence[].note: "downgraded: no textual import grep-match (LAYER-EVID-1)"`, OR skip emission entirely if no other layering signal supports it (e.g., no dynamic-import via string literal, no test-gap on alleged boundary).
```
  - **Severity rubric** gains a NEW final bullet: `- **Downgrade rule (LAYER-EVID-1)**: any candidate \`high\` or \`critical\` finding whose alleged import is not textually grep-verifiable in the evidence file is downgraded to \`low\` (or skipped). Phantom graphify edges from cross-file same-name symbol collapse are the witnessed failure mode (slice-019, F-LAYER-bca9c001 false-positive).`
  - **Anti-patterns** gains a NEW negative-pin bullet: `- **Don't trust graphify edges for HIGH-severity boundary findings without textual import-evidence verification.** Cross-file same-name symbols (e.g., parallel type files defining identically-named enums) can collapse into phantom edges. Apply LAYER-EVID-1's grep-verification before emitting.`

### Modified — `skills/diagnose/SKILL.md`

- **Responsibility**: Top-level skill orchestration prose. Now cross-references LAYER-EVID-1 at Step 5 dispatch.
- **Lives at**: `skills/diagnose/SKILL.md` (modified by this slice)
- **Key interactions**: Read by Claude main thread when `/diagnose` is invoked; orchestrates pass dispatch
- **Changes** (mechanical): NEW paragraph appended to Step 5 between the existing "Subagent contract (canonical line — embed verbatim in subagent prompts)" subsection and the existing "After each subagent returns" subsection. Paragraph text (canonical phrase pinned bidirectionally):
  > **Pass-specific evidence requirement (LAYER-EVID-1)**: per methodology-changelog v0.33.0, the `03f-layering` pass subagent MUST apply the **textual import-evidence requirement** before emitting any HIGH-severity layering / cross-tier / import-violation finding. The rule body lives in `passes/03f-layering.md` Method step 4 + Severity rubric downgrade rule + Anti-patterns negative-pin. The subagent's Grep/Read/Glob tool envelope (per the canonical contract above) is sufficient — no new tools required.

### New — `tests/skills/diagnose/test_layering_pass_textual_evidence.py`

- **Responsibility**: Integration test driving the synthetic regression fixtures; verifies the LAYER-EVID-1 grep-semantics produce zero HIGH findings on the F-LAYER-bca9c001 fixture shape and DO produce a HIGH finding on a real cross-tier import.
- **Lives at**: `tests/skills/diagnose/test_layering_pass_textual_evidence.py` (created by this slice)
- **Key interactions**: Reads fixture trees from `tests/skills/diagnose/fixtures/`; private helper `_grep_textual_import(target_dir, evidence_file, bypassed_layer_path) -> bool` implements the rule semantics inline (test-local; not exported; not added to `tools/`); no production-code dependency
- **Rationale for test-local helper (vs. new tools/ module)**: the rule is operationally executed by the subagent at runtime via its own Grep tool. The test's job is to verify the rule's *logic* against fixtures, not to export a callable. Promoting the helper to `tools/` would add a PMI-1 manifest entry + install_audit entry without changing what the subagent does (the subagent reads prose; it doesn't import a Python module). Defer until N≥3 distinct test files would benefit from the helper.
- **Test-local helper rationale + drift risk (per /critique M1 ACCEPTED-PENDING)**: the helper `_grep_textual_import` re-implements the LAYER-EVID-1 grep semantics for fixture verification. The test asserts the helper's behavior against synthetic fixtures, NOT the subagent's actual runtime grep against arbitrary codebases. **Known limitation**: if the subagent at /diagnose runtime applies a different grep regex than the helper (e.g., misreads the pass-template prose, drops an import variant, ignores `re.DOTALL` semantics), the test would not catch the drift. **Mitigation at v1**: the regex strings in pass-template Method step 4 prose are byte-equal to the helper's pattern constants — visual byte-equality is the prose-pin equivalent of CAD-1 byte-equality at the rule-content level (subagent and helper read the same regex strings). **Deferral**: a v2 audit `tools/layer_evid_1_drift_audit.py` (extracting the regex strings from both surfaces and asserting sha256 equality) is deferred per TPHD-1 / RSAD-1 / RPCD-1 N≥3-violations-deferral precedent — promote at N≥3 if drift surfaces at /critic-calibrate (e.g., subagent emits a HIGH layering finding on a codebase where the test's helper would have grep-matched the import, OR vice versa).

### New — `tests/skills/diagnose/fixtures/parallel_types_no_import/`

- **Responsibility**: Synthetic mini-codebase reproducing F-LAYER-bca9c001 shape: backend `src/types.ts` defines `enum NodeType { A, B, C }`; frontend `lib/types.ts` defines `enum NodeType { A, B, C }` (independent definition with same symbol name); `frontend/components/Foo.tsx` imports `NodeType` from `../lib/types` (frontend-local, no cross-tier). `tsconfig.json` (frontend) maps `@/*` → `./*` rooted at `frontend/` (physically prevents `@/`-alias from reaching `src/`).
- **Lives at**: `tests/skills/diagnose/fixtures/parallel_types_no_import/` (created by this slice)
- **Key interactions**: Read by `test_layering_pass_textual_evidence.py`; not packaged; not installed; never executed as code (just file content)

### New — `tests/skills/diagnose/fixtures/parallel_types_real_import/`

- **Responsibility**: Positive-control synthetic codebase. Same backend `src/types.ts`. Frontend `components/Bar.tsx` actually imports from `../../src/types` (a real cross-tier import that LAYER-EVID-1 must NOT suppress).
- **Lives at**: `tests/skills/diagnose/fixtures/parallel_types_real_import/` (created by this slice)
- **Key interactions**: Same as above; positive control for the rule.

## Contracts added or changed

No HTTP/API/event contracts added. The only contract surfaces touched are:

- **Subagent contract (existing, slice-001 ADR-001)** — UNCHANGED. The canonical contract line at SKILL.md Step 5 ("Do NOT call Write to produce output files...") stays byte-identical; this slice extends Step 5 with a new *additional* paragraph but does not modify the canonical contract line. The 12-site byte-equality test (slice-002) continues to pass.
- **Subagent emit-decision rule (new, this slice)** — pass-template-level prose contract. The 03f-layering subagent now MUST grep-verify imports before HIGH emission. This is a runtime behavioral contract embedded in pass-template prose, not an API contract.
- **Finding schema (existing, slice-001 ADR-001 + `schema/finding.yaml`)** — UNCHANGED. The `severity` enum still accepts low/medium/high/critical; the `evidence[].note` field (already optional) is used to record the LAYER-EVID-1 downgrade reason when applicable. No schema migration needed.

## Data model deltas

None. This slice is methodology + prose + tests; no runtime data model, no DB schema, no migration.

## Wiring matrix

Per WIRE-1. This slice introduces zero new production modules. The two new artifacts under `tests/` (the integration test + two fixture trees) are test infrastructure; per WIRE-1 convention (test files map to the module they exercise, which here is pass-template prose, not a module), and per the empty-matrix convention from slice-017 ("zero-row matrices are clean"), the matrix is intentionally empty.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(Zero rows — no new production modules. The new test file + fixtures are test infrastructure exercising pass-template prose, not code.)

## Decisions made (ADRs)

- [[ADR-017]] — Textual import-evidence requirement at `/diagnose` pass-template level (LAYER-EVID-1), not at graphify symbol-resolution level — reversibility: **cheap**

## Authorization model for this slice

N/A. This slice modifies methodology prose + adds test infrastructure. No runtime code paths handle user data, sessions, tokens, or auth.

## Error model for this slice

The 03f-layering subagent's NEW grep-verification step has three outcomes per candidate finding:

| Grep result | Finding action | Note recorded |
|-------------|----------------|---------------|
| ≥1 textual import match in evidence file | Emit at originally-determined severity (no change) | No LAYER-EVID-1 note |
| 0 matches AND no other layering signal | Skip emission entirely | (finding never emitted) |
| 0 matches BUT another layering signal exists (e.g., dynamic-import via string literal, test-gap on alleged boundary) | Downgrade to severity `low` | `evidence[].note: "downgraded: no textual import grep-match (LAYER-EVID-1)"` |

The third row's recorded note enables `/slice-candidates` and the owner-annotator to audit the downgrade decision (per slice-019 mission-brief.md must-not-defer #9 "Logging").

No new error codes, no new exception types, no new failure modes at the orchestrator level. The grep operation uses the existing subagent tool envelope; failure modes (Grep tool unavailable, fixture-file unreadable) are already covered by ADR-001 + slice-002's re-spawn-cap (3 attempts) and degraded-pass `.failed.raw` artifact handling.

## Test-first plan (cross-reference)

The full TF-1 plan with all 10 rows is in [mission-brief.md](mission-brief.md) — not duplicated here per TPHD-1 sub-mode (a) (single source of truth for TF-1 plan; any rename or AC #N renumbering during /critique fix-prose must harmonize mission-brief.md AND this design.md reference together).

This design.md introduces NO new test function names beyond what mission-brief.md already enumerates. If /critique fix-prose proposes a rename, harmonize both files in the same fix block.

## Test-scoping inheritance (slice-018 sibling pattern N=2 cumulative; resolves /critique M4)

Per /critique M4 ACCEPTED-PENDING + slice-018 reflection (DEVIATION-1 N=1 promotion-eligible at N≥2; slice-019 makes this the SECOND instance): slice-019's v0.33.0 methodology-changelog entry-pin tests + ADR-017 entry-pin test MUST scope their assertions to the v0.33.0 entry body, NOT the raw file content. The slice-016 RPCD-1 sibling-test scoping flaw (silently masking false-positives via global-substring `in content` checks) was retired at slice-018 via `_extract_v031_body` helper between `## v0.31.0` and `## v0.30.0` boundaries.

**Implementation (Phase 2-3)**:

1. Introduce module-level helper `_extract_v033_body(content: str) -> str` in `tests/methodology/test_methodology_changelog.py` (mirroring slice-018 L1086-1094 `_extract_v031_body` pattern at the PATTERN level, NOT literal-code level per slice-018 /critique-review m-add-2 Audit 3 refinement). Helper finds the section between `## v0.33.0` and `## v0.32.0` heading markers; raises AssertionError with surface_name context if either marker absent (preserves slice-017 L1088-1090 diagnostic pattern surface-context-aware).

2. Scope `test_v_0_33_0_layer_evid_1_entry_present_in_repo_and_installed` + `test_v_0_33_0_layer_evid_1_entry_names_textual_import_evidence_canonical_phrase` to `v033_body = _extract_v033_body(content)`; assertions reference `v033_body`, not raw `content`. Bidirectional check applies to BOTH in-repo `methodology-changelog.md` AND installed `~/.claude/methodology-changelog.md` per N=15 forensic capture.

3. Add NEW regression test `test_v_0_33_0_layer_evid_1_sibling_scoping_rejects_stripped_v033_body` (mirroring slice-018 L1010-1060 canonical regression pattern): call `_extract_v033_body` on synthetic content with v0.32.0 markers retained + v0.33.0 body markers stripped; assert the regression-test PASSES on synthetic (proving the helper would have caught the global-substring fallacy if the entry-pin sibling test had been written without the helper). Single-code-path discipline per slice-018 /critique M2 ACCEPTED-FIXED: regression-test-passes ↔ sibling-test-fails-on-stripped-fixture link established by execution, not code-reading.

**Helper-extraction asymmetry mitigation (per /critique-review DR-1 class (b) catch on slice-018 m-add-2)**: this slice's `_extract_v033_body` is the SECOND v0.NN entry-body helper (after slice-018's `_extract_v031_body`). N=2 = promotion threshold per slice-018 reflection (more aggressive than Fowler rule-of-three's N=3). At this slice, both `_extract_v031_body` (lives at slice-018 location) and `_extract_v033_body` (introduced here) coexist as siblings; a v2 generalization `_extract_version_body(content: str, version: str) -> str` is deferred until N=3 (next codification slice's entry-pin tests).

## Methodology-changelog entry (v0.33.0 / LAYER-EVID-1)

The entry codifies the rule using the canonical phrase `textual import-evidence requirement` as the in-repo + installed byte-equal anchor. Entry body (proposed; locked at /build-slice):

```markdown
## v0.33.0 — 2026-05-13

**Textual import-evidence requirement codified at `/diagnose` 03f-layering pass-template level** as **LAYER-EVID-1** — the 03f-layering subagent MUST grep-verify a textual import statement in the cited evidence file before emitting any HIGH-severity layering / cross-tier / import-violation finding. Patterns: TypeScript/JavaScript `^\s*import\s+.*from\s+['"]<path>['"]` / `require\(['"]<path>['"]\)` / dynamic `import\(['"]<path>['"]\)`; Python `^\s*from\s+<module>\s+import` / `^\s*import\s+<module>`. Zero textual matches → downgrade to `low` (with `evidence[].note: "downgraded: no textual import grep-match (LAYER-EVID-1)"`) or skip emission. Witnessed failure mode (slice-019, finding ID F-LAYER-bca9c001): graphify symbol-resolution collapsed cross-file same-name symbols (parallel type files defining identically-named enums) into phantom edges, causing the layering pass to flag a HIGH "frontend bypasses HTTP boundary by importing backend types" finding when zero textual imports existed. Codification at N=1 cumulative evidence (proactive ratchet ahead of N=2 promotion threshold; aligns with slice-017 TPHD-1 pattern of codifying high-impact false-positive classes at N=1). Fix lives at pass-template prose layer (NOT graphify level) — reversibility cheap; supersession path via R-3 if graphify symbol-conflation is later fixed upstream.

### Added

- **LAYER-EVID-1 — Textual import-evidence requirement for /diagnose layering findings**
  Pass-template prose at `skills/diagnose/passes/03f-layering.md` Method step 4 + Severity rubric downgrade rule + Anti-patterns negative-pin; cross-referenced at `skills/diagnose/SKILL.md` Step 5 with one-line paragraph. Canonical phrase `textual import-evidence requirement` pinned bidirectionally across 3 surfaces (in-repo) and 3 installed surfaces (mini-CAD byte-equal). Witnessed at slice-019 F-LAYER-bca9c001 false-positive (parallel type files with identical enum names).
  - **Rule reference**: LAYER-EVID-1
  - **Defect class**: false-positive HIGH-severity layering findings emitted from graphify symbol-edges without textual import-verification; erodes `/diagnose` user trust and pollutes `/slice-candidates` backlog
  - **Validation**: `tests/skills/diagnose/test_skill_md_pins.py::test_skill_md_step5_documents_textual_evidence_rule` + `::test_layering_pass_template_emits_textual_evidence_rule` + `::test_textual_evidence_rule_byte_equal_across_n_3_surfaces`; `tests/skills/diagnose/test_diagnose_skill_drift.py` (mini-CAD bidirectional byte-equality); `tests/skills/diagnose/test_layering_pass_textual_evidence.py` (synthetic fixture integration); `tests/methodology/test_methodology_changelog.py::test_v_0_33_0_layer_evid_1_*` (entry pins)
  - **Limitations**: prose-heuristic discipline applied by the 03f-layering subagent at /diagnose runtime; no audit-enforced gate (the rule operates inside the subagent's reasoning loop, not as a separate Python module). If the subagent ignores the rule prose, only manual review at `/slice-candidates` would surface the regression. A v2 `tools/layer_evid_1_audit.py` is deferred until N≥3 violations recur (matches slice-017 TPHD-1 / slice-011 RSAD-1 prose-heuristic precedent).
```

## Risk-register entry (R-3)

```markdown
## R-3 — Graphify symbol-resolution may conflate same-name cross-file symbols into phantom edges

**Likelihood**: medium
**Impact**: medium
**Status**: mitigating
**Reversibility**: cheap
**Discovered**: slice-019-harden-diagnose-layering-evidence (2026-05-13)

Graphify's symbol-resolution apparently collapses cross-file same-name symbol references (e.g., two files independently defining `enum NodeType` — a parallel type file pattern common in monorepos with backend + frontend) into a single graph node, creating phantom import edges between them. Witnessed at `/diagnose` F-LAYER-bca9c001 false-positive: graphify-out reported "45 frontend files import src/workflow/adapters/types.ts" when zero frontend files textually import from `src/`; the actual pattern was 17 frontend files importing `NodeType` from a *parallel* frontend-local `frontend/lib/workflow/types.ts` (537 LOC, hand-maintained copy with identically-named enums).

**Impact in practice**: medium — wherever a graphify consumer interprets edges as import-edges without textual verification, the same false-positive class can fire. `/diagnose` 03f-layering is the witnessed instance; other passes (`02-architecture` "where the code disagrees" references, `03d-half-wired` UI↔backend edge detection) MAY also be affected but no instance has been observed yet. Other consumers (`/architect`, `/validate`, `/discuss`, `/sprint-runner`, `/codebase-analysis`, etc.) are theoretically exposed; no evidence of impact in those yet.

**Mitigation (in place)**: slice-019 codifies LAYER-EVID-1 at the `/diagnose` 03f-layering pass-template level — subagent MUST grep-verify imports before HIGH-severity emission. This closes the witnessed false-positive class at the consumer layer rather than the graphify layer. Status: `mitigating` (not `retired`) because the root cause in graphify is untouched.

**Escalation criteria**: if `/critic-calibrate` flags additional symbol-conflation false-positives in other `/diagnose` passes OR in other graphify consumers (N≥2 distinct slices reporting similar phantom-edge issues), promote a follow-on slice to either (a) extend LAYER-EVID-1 to those passes or (b) fix graphify symbol-resolution upstream. Choice (b) is reversibility=cheap at the graphify code level but has broad blast radius (all graphify consumers); choice (a) replicates the LAYER-EVID-1 surgical pattern per affected consumer.

**Notes**: The fix surface choice (pass-level vs graphify-level) is documented in [[ADR-017]]. R-3 is the explicit tracker for the broader-class concern.
```

## Audit gates this slice exercises

Per slice-016 RPCD-1 + slice-018 cleanup pattern, this slice should expect all audits clean at pre-finish:

- **TF-1** (`tools/test_first_audit.py --strict-pre-finish`): all 10 TF-1 rows transition PENDING → WRITTEN-FAILING → PASSING
- **WIRE-1** (`tools/wiring_matrix_audit.py`): zero-row matrix accepted as clean
- **BC-1** (`tools/build_checks_audit.py`): slice-019 design.md + mission-brief.md should NOT fire BC-PROJ-1/2 or BC-GLOBAL-1 (BC-PROJ-2 negative-anchor migration from slice-012 covers the methodology-vocabulary class this slice uses)
- **RR-1** (`tools/risk_register_audit.py`): R-3 entry parses cleanly (correct heading format `## R-3 — <title>` with required fields)
- **PMI-1 v1.1** (`tools/plugin_manifest_audit.py`): version 0.33.0 atomic bump; `plugin.yaml.version == VERSION` invariant holds (no new skill/agent/tool added)
- **CAD-1** (`tools/critique_agent_drift_audit.py --repo-root .`): preserved at slice-017 ship hash `f34c967eaaa34413` (no Critic-agent edit)
- **Mini-CAD for `/diagnose`** (NEW this slice, `tests/skills/diagnose/test_diagnose_skill_drift.py`): `skills/diagnose/SKILL.md` AND `skills/diagnose/passes/03f-layering.md` byte-equal in-repo ↔ installed
- **SCPD-1** (slice-015): shippability.md row 19 propagated BEFORE `/validate-slice` Step 5.5 catalog run
- **TPHD-1** (slice-017): self-application at all 3 sub-modes — (a) at /critique fix-prose (b) at /critique-review fix-prose (c) at /build-slice Prerequisite check
- **Bidirectional sha256 forensic capture (slice-018 N=14 stable → slice-019 N=15 stable)**: `agents/critique.md` preserved at slice-017 ship hash `f34c967eaaa34413` (NO Critic-agent edit this slice). `methodology-changelog.md` NEW ship hash will be captured at /build-slice Phase 2c forward-sync (replaces slice-017 hash `06ce0c442874f0aa` — slice-019 adds the v0.33.0 entry, so the hash MUST change; the forensic counter ratchets to N=15 stable). `skills/diagnose/SKILL.md` + `skills/diagnose/passes/03f-layering.md` NEW ship hashes captured at the same forward-sync (first introduction of mini-CAD for /diagnose — these enter the forensic capture list at N=15 as new entries; the per-file hash list extends from {agents/critique.md, methodology-changelog.md} to {agents/critique.md, methodology-changelog.md, skills/diagnose/SKILL.md, skills/diagnose/passes/03f-layering.md}).
