# Critique: Slice 033 fix-skill-drift-test-crlf-normalization

**Critic reviewed**: mission-brief.md, design.md, ADR-033-md-drift-guards-eol-agnostic.md
**Date**: 2026-05-17
**Result**: NEEDS-FIXES

## Summary

The core fix (normalize CRLF→LF in a shared comparator) is sound, the namespace-package import claim is **verified true**, and the live repro fails exactly as the mission-brief asserts. But the slice changes a behavior-defining methodology rule (CAD-1/mini-CAD invariant) with **no methodology-changelog entry and no version bump**, contradicting PMI-1 discipline applied uniformly across slices 007–032; and it leaves an **active false statement in CLAUDE.md** ("MUST be byte-equal") deferred to a future /reflect rather than corrected in-slice. Several majors on AC3's renormalization gap and the CAD-1 audit's existing regression-test interaction.

## Findings

### Blockers (must address before /build-slice)

#### B1: Behavior-changing methodology rule with no changelog entry / no version bump (PMI-1 drift)
- **Claim under review**: design.md lists only ADR-033; no `methodology-changelog.md` entry / `VERSION` bump anywhere; ADR-033 says "/reflect should note the wording delta (no rule-ID change, lineage preserved like PMI-1 v1.0→v1.1)".
- **Issue**: Slice modifies a production `tools/` audit (`critique_agent_drift_audit.py::_sha256_of`, a CLAUDE.md pre-commit gate) and restates the CAD-1/mini-CAD invariant. Per the methodology-changelog Inclusion heuristic + uniform precedent slices 007–032 (VERSION + `ai-sdlc-VERSION` + `plugin.yaml.version` atomic bump + `## vX.Y.Z` entry + `test_v_X_Y_Z_*_entry_present_in_repo_and_installed` pin), the changelog+version is not optional. The "PMI-1 v1.0→v1.1 lineage preserved" analogy cuts AGAINST the design: those shipped a changelog entry + version bump; lineage-preservation = rule-ID, not skipping the changelog.
- **Evidence**: methodology-changelog atomic-bump precedent; shippability rows; CLAUDE.md "Self-hosting discipline"; ADR-033 Consequences.
- **Proposed fix**: Add to scope: (a) `methodology-changelog.md` entry `## v0.47.0` with rule-ref/defect-class/validation; (b) atomic bump `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` 0.46.0→0.47.0; (c) `test_v_0_47_0_*_entry_present_in_repo_and_installed` pin + AC + TF-1 row. Else explicitly argue a changelog exemption in design.md against the Inclusion heuristic.
- **Builder draft**: ACCEPTED-FIXED — spec gap closed now: new **AC5** (governing-surface consistency) + TF-1 rows + design.md "What's new" entries + ADR-033 analogy corrected. Mechanical changelog/version edits execute at /build-slice as normal slice work (true of every AC).

#### B2: CAD-1 wording in CLAUDE.md left actively false ("MUST be byte-equal") — deferred to /reflect
- **Claim under review**: ADR-033 Consequences defers the CLAUDE.md wording delta to /reflect; design.md "Authorization model" treats it as out-of-slice.
- **Issue**: CLAUDE.md L33 ("CAD-1 ... MUST be byte-equal") + L36 ("Mini-CAD ... MUST be byte-equal") become factually wrong after ship. A self-hosting-discipline slice that restates the invariant (ADR-033 Decision) cannot defer stating it correctly in the one document that defines it — slice-022 self-violation law at the predicted N≈9.
- **Evidence**: CLAUDE.md L33, L36; ADR-033 Consequences; aggregated lesson (self-violation law N≈9).
- **Proposed fix**: Add AC + edit CLAUDE.md L33/L36 to the precise invariant + substring regression test mirroring `test_root_claude_md_branch_per_slice_rule.py`. Else justify in ADR-033 why a false MUST-statement in the governing contract is non-blocking.
- **Builder draft**: ACCEPTED-FIXED — folded into new **AC5**: CLAUDE.md L33/L36 corrected in-slice + substring regression pin. ADR-033 Consequences rewritten (no longer defers to /reflect).

### Majors (address this slice)

#### M1: AC3 `.gitattributes` does not normalize the already-CRLF working tree; test only checks the declaration
- **Issue**: Confirmed via Git docs: `.gitattributes eol=lf` does NOT rewrite already-CRLF-checked-out files under `core.autocrlf=true` — requires `git add --renormalize`. AC3's test (`git check-attr eol`) only verifies the declaration, not working-tree bytes. ADR-033 promises "renormalization scoped to those guarded files only" — a step absent from design.md "What's new" + AC3 verification.
- **Evidence**: `git check-attr eol -- skills/diagnose/SKILL.md` → unspecified; git-scm gitattributes docs; ADR-033 Decision.
- **Proposed fix**: (a) add explicit `git add --renormalize -- <guarded globs>` to design + commit, strengthen AC3 test to assert guarded in-repo files contain no `\r\n` (working-tree-state check); OR (b) rescope AC3 to "durability for future checkouts only; AC1 is the active fix".
- **Builder draft**: ACCEPTED-FIXED — option (a): design.md "What's new" + AC3 now include targeted `git add --renormalize` of the guarded globs; AC3 test strengthened to a no-`\r\n` working-tree-state assertion (not just `check-attr`).

#### M2: CAD-1 `_sha256_of` normalization must preserve existing drift-detection tests — not bound as AC2 evidence
- **Issue**: `test_critique_agent_drift.py::test_drift_detection_fires_on_artificial_byte_flip` + the CLI exit-code matrix seed genuinely-divergent LF content → still exit 1 post-normalization (should survive), but design binds AC2's CAD-1 half only to ONE new EOL-only test. TF-1 row-coverage gap for AC2's audit side.
- **Evidence**: `tests/methodology/test_critique_agent_drift.py:86-113`, `:157-194`, `:230-251`.
- **Proposed fix**: Bind existing `test_drift_detection_fires_on_artificial_byte_flip` + CLI exit-code matrix as CAD-1-side genuine-divergence proof; new CAD-1 EOL-only test is the complement.
- **Builder draft**: ACCEPTED-FIXED — AC2 + TF-1 plan + verification plan now bind the existing CAD-1 drift-detection tests as the audit-side must-not-mask proof; new EOL-only test added as complement.

#### M3: namespace-import proof cites wrong subpackage precedent (verified true empirically; design's evidence wrong)
- **Issue**: design.md proves cross-subpackage import via `tests/methodology/` precedent, but the at-risk consumer is `tests/skills/diagnose/` (sys.path-mutating conftest, no `tests.` import today). Critic empirically verified the import DOES resolve from both (644 tests collect) → NOT a blocker, but the design's evidence is the wrong precedent.
- **Evidence**: `tests/skills/diagnose/conftest.py`; `test_diagnose_skill_drift.py:25`; empirical probe (644 collected).
- **Proposed fix**: Replace design.md proof sentence with the correct evidence (import resolves from `tests/skills/diagnose/` specifically — verified); add mid-slice smoke assertion the diagnose drift module imports under the sys.path-mutating conftest.
- **Builder draft**: ACCEPTED-FIXED — design.md proof sentence corrected to the empirically-verified fact; mid-slice smoke gate now asserts the diagnose-subpackage import resolves.

#### M4: `tests/skill_drift_equality.py` top-level non-`test_*` module vs established conftest-sharing convention — needs ADR rationale
- **Issue**: Repo convention shares test code via `conftest.py`/`__init__.py`; this is the first top-level non-test importable module in `tests/`. Per Brownfield rule "deviations need an ADR", ADR-033 must justify the location (or relocate). Collection-shape verified safe (644 collected, not collected as a test). Sub-concern (b) INST/PMI manifest surface — verified cleared.
- **Evidence**: `pytest.ini` (`testpaths=tests`, `python_files=test_*.py`); repo convention; Brownfield rule.
- **Proposed fix**: Justify the top-level shared-module location in ADR-033 (one sentence) or relocate to conftest-sharing.
- **Builder draft**: ACCEPTED-FIXED — ADR-033 gains a location-rationale: the consumer set spans two sibling subpackages (`tests/skills/diagnose/` + `tests/methodology/`), so neither subpackage's `conftest.py` (pytest-fixture-scoped, not a general import surface) is the natural home; a neutral top-level shared module is the correct structural choice. Convention break is now written.

### Minors (log; address if cheap)

#### m1: AC4 cp-masking-avoidance asserted procedurally; precedent validated not just cited
- **Issue**: Per slice-032 lesson, Critic verified R-5 (L94/L108/L110) firsthand — precedent VALIDATED. But AC4 verification relies on a tester remembering "no prior cp"; procedural, not enforced. Low severity — AC1 makes the result cp-independent.
- **Proposed fix**: Note in validation.md that AC4 is auto-satisfied by AC1's comparator (cp-state-independent), turning a manual-procedure AC into a property-of-the-fix AC.
- **Builder draft**: ACCEPTED-FIXED — AC4 reworded to a property-of-AC1 statement (cp-state-independent); validation.md note will record it as such.

#### m2: deferred `;`-split runner concern has no concrete tracked handle
- **Issue**: R-5 L110 + slice-032 lesson say the CRLF-fix slice "should also pin the Step-5.5 runner `;`-split contract". Deferral is acceptable scoping, but no R-id / candidate-slice name → same N+2 silent-recurrence risk that necessitated THIS slice.
- **Proposed fix**: Name the concrete deferral artifact (risk-register entry or chartered candidate slice).
- **Builder draft**: ACCEPTED-FIXED — design.md "Out of scope" now names a concrete handle: a new risk-register entry `R-8 — shippability Step-5.5 runner ;-split contract unpinned` to be opened at /reflect.

## Dimensions checked
- [x] Unfounded assumptions — M3 (wrong-precedent evidence; verified true empirically), B1 (changelog/version omission inconsistent with stated PMI-1 analogy). Live repro + import resolution verified sound.
- [x] Missing edge cases — M1 (already-CRLF tree not normalized by `.gitattributes` alone — confirmed via Git docs).
- [x] Over-engineering — M4(a) un-ADR'd top-level-module convention deviation. Shared-helper consolidation is appropriately YAGNI.
- [x] Under-engineering — B1, B2, M2 (AC2's CAD-1 half lacked a regression-test binding).
- [x] Contract gaps — none beyond M2; CAD-1 exit-code contract verified unchanged (`critique_agent_drift_audit.py:245-252`).
- [x] Security — none (line-ending normalization in test/audit comparators; no authn/authz/input-boundary surface).
- [x] Drift from vault — B1/B2 (CLAUDE.md + methodology-changelog left inconsistent with shipped behavior). ADR-033 well-formed, `supersedes: null` correct.
- [x] Web-known issues — M1 confirmed via git-scm/GitHub docs (`eol=lf` not retroactive; `--renormalize` required).
- [x] Cross-cutting conformance — B1 (PMI-1 uniform 007–032), B2 + M4(a) (recursive self-application / slice-022 self-violation law N≈9).

## Triage

**Triaged by**: user
**Date**: 2026-05-17
**Final verdict**: CLEAN

Reconciles BOTH passes (first Critic + DR-1 meta-Critic). Meta-Critic verdict ADJUST: M3 severity recalibrated Major→Minor (disposition unchanged); m-add-1 added as a new disposition row; m-add-2 informational (no disposition — TF-1 `PASSING` status verified correct, logged to prevent re-litigation).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | new AC5 governing-surface-consistency (changelog v0.47.0 + atomic version bump + entry-pin); ADR-033 analogy corrected |
| B2 | Blocker  | ACCEPTED-FIXED | CLAUDE.md L33/L36 corrected in-slice + substring pin (folded into AC5); ADR-033 no longer defers to /reflect |
| M1 | Major    | ACCEPTED-FIXED | targeted `git add --renormalize` of guarded globs added to design + AC3; AC3 test → no-`\r\n` working-tree-state check |
| M2 | Major    | ACCEPTED-FIXED | existing CAD-1 drift-detection tests bound as AC2 audit-side proof; new EOL-only test as complement |
| M3 | Minor    | ACCEPTED-FIXED | severity recalibrated Major→Minor (DR-1: technical risk empirically disproven, citation-only); design.md proof corrected; mid-slice smoke asserts diagnose-subpackage import |
| M4 | Major    | ACCEPTED-FIXED | ADR-033 gains top-level-shared-module location rationale (consumer set spans two sibling subpackages) |
| m1 | Minor    | ACCEPTED-FIXED | AC4 reworded as property-of-AC1 (cp-state-independent) |
| m2 | Minor    | ACCEPTED-FIXED | concrete handle named: R-8 to be opened at /reflect (already in R-5 "Secondary discovery") |
| m-add-1 | Minor | ACCEPTED-FIXED | DR-1 missed-finding: minted RULE-ID `EOL-DRIFT-1`; pin renamed `test_v_0_47_0_eol_drift_1_…`; TF-1/Verification/design.md/ADR-033 harmonized (TPHD-1 sub-mode b) |

_m-add-2 (DR-1, informational): TF-1 `PASSING` status for the two bound pre-existing CAD-1 regression tests verified correct against `tools/test_first_audit.py` `_ALLOWED_STATUSES` — no disposition required._
