# Design: Slice 018 cleanup-slice-016-rpcd-1-sibling-test-scoping-flaw

**Date**: 2026-05-13
**Mode**: Standard
**Slice scope**: SMALL — single test file edit + one NEW regression test; no methodology version bump; no SKILL.md prose; no ADR; no `agents/critique.md` edits
**Risk-retirement target**: slice-017 reflection NEW first-Critic-MISS class at N=1 — "test-scoping-flaw-inherited-across-codification-slice-siblings"

## What's new

- **Refactor** `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed` at `tests/methodology/test_methodology_changelog.py:910-951` to scope assertions to v0.31.0 body (mirroring slice-017 TPHD-1 sibling at L1086-1094 of same file)
- **NEW** regression test `test_v_0_31_0_rpcd_1_sibling_scoping_rejects_stripped_v031_body` in the same file, inserted immediately after the refactored function (around L953)
- **Updated docstring** at L911-924 with explicit citation of slice-017 DEVIATION-1 evidence anchor + slice-017 TPHD-1 sibling canonical pattern at L1086-1094 (same file)
- **shippability.md row 16 — UNCHANGED this slice**: Per Decision L96 (preserve function name) + Audit 4 (empirical row 16 enumeration at /critique fix-prose), row 16 is unchanged. SCPD-1 proactive-application: vacuous. Conditional hedge resolved per /critique m2 ACCEPTED-FIXED.

## What's reused

- Slice-017 TPHD-1 sibling pattern at `tests/methodology/test_methodology_changelog.py:1086-1094` — canonical scoping template:
  ```python
  v032_start = content.find("## v0.32.0")
  v031_start = content.find("## v0.31.0", v032_start)
  assert v032_start != -1, ...
  if v031_start == -1:
      v032_body = content[v032_start:]
  else:
      v032_body = content[v032_start:v031_start]
  ```
  Slice-018 adapts this verbatim to v0.31.0 ↔ v0.30.0 boundaries
- Existing 5 assertions in the slice-016 RPCD-1 sibling test (preserved verbatim; only haystack changes `content` → `v031_body`)
- Existing `read_file` + `Path.home() / ".claude" / "methodology-changelog.md"` infrastructure at top of file
- Existing pytest discovery / collection mechanism — no new test infrastructure needed
- [[slice-016-refine-dim-9-with-runtime-prerequisite-completeness-sub-class]] — sibling test source
- [[slice-017-address-tf-1-plan-staleness-discipline]] — DEVIATION-1 evidence anchor + canonical scoping pattern

## Components touched

### `tests/methodology/test_methodology_changelog.py`

- **Responsibility**: pins methodology-changelog.md entries (per-version entry-pin + sub-mode + cross-slice-anchor + ADR-pin + PMI-1 invariant gate) bidirectionally between in-repo and installed `~/.claude/methodology-changelog.md`
- **Lives at**: `tests/methodology/test_methodology_changelog.py` (modified — 1 function refactor + 1 NEW function + 1 docstring update)
- **Key interactions**: imports `read_file` helper at top; reads in-repo + installed methodology-changelog.md surfaces; called by `pytest tests/methodology -q` at /validate-slice + shippability.md row 16 (RPCD-1 critical-path pytest extraction)

**Edit-locations summary**:

| Line range | Edit type | What changes |
|------------|-----------|--------------|
| L911-924 | Docstring update | Append paragraph documenting slice-017 DEVIATION-1 evidence + slice-017 TPHD-1 sibling canonical pattern at L1086-1094; preserve existing prose |
| L925-951 | Body refactor | INSERT `v031_start`/`v030_start` boundary slicing + `v031_body` construction immediately after `installed = installed_path.read_text(...)` line; substitute `content` → `v031_body` in 5 existing assertions inside the `for surface_name, content in [...]` loop |
| ~L953 | NEW function | INSERT `test_v_0_31_0_rpcd_1_sibling_scoping_rejects_stripped_v031_body` as new test function; ~30 LOC; synthetic-content construction + scoping verification |

## Contracts added or changed

None — pure test refactor + addition.

## Data model deltas

None — no schema, no migration, no Pydantic model.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Every new module/file this slice introduces must declare a consumer entry point AND a consumer test, OR carry an explicit exemption.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(Zero new modules — slice modifies one existing test file. WIRE-1 audit at /build-slice Phase 5 will see zero-row matrix as clean.)

## Decisions made (ADRs)

None — cleanup slice. No architecture decision warrants ADR-pin convention extension. Slice-017 reflection language explicitly: "cleanup-slice... defer until N=2 if recurs at slice-018+ OR fold into next codification slice". This slice is the standalone-execution path of that deferred option at N=1. ADR-pin convention N=4 stable (ADR-013 + ADR-014 + ADR-015 + ADR-016) does NOT extend to test-quality cleanup slices.

## Authorization model for this slice

N/A — test refactor, no auth surface.

## Error model for this slice

N/A — test refactor, no runtime error paths. Test fixtures use stdlib assertions; pytest reports failures via existing exception mechanism.

---

## Decision: Test function name — preserve or rename?

**Options**:

1. **Preserve name** — keep `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed`; refactor body only.
   - **Pro**: zero churn on shippability.md row 16 pytest command; zero churn on _index.md historical reference; minimal blast radius.
   - **Pro**: EPGD-1 self-application: 0 of 15 prior entry-pin functions touched at the FUNCTION-NAME level (only BODY changes; structural separation discipline preserves the entry-pin shape).
   - **Pro**: TPHD-1 sub-mode (c) at /build-slice Prerequisite-check pre-flight harmonization stays vacuous (no rename → no TF-1 plan harmonization needed in this slice).
   - **Con**: name doesn't communicate that the test now scopes to v031_body — future readers reliant on function name alone may not realize the scoping fix; docstring covers this.

2. **Rename to `..._scopes_to_v031_body_in_repo_and_installed`** — make the scoping discipline visible in the function name.
   - **Pro**: name itself documents the scoping discipline.
   - **Con**: shippability.md row 16 pytest command needs propagation in same /build-slice block (SCPD-1 sub-mode); _index.md slice-016 reference becomes stale; TF-1 plan needs sub-mode (a) harmonization at /critique fix-prose if Critic suggests further rename; EPGD-1 self-application: 1 of 15 prior entry-pin functions SUPERSEDED (NEW + OLD names; structural separation discipline becomes non-vacuous).
   - **Con**: shippability.md row 16 was tested clean at slice-016 + slice-017 catalog runs at the preserved name; rename increases catalog-rerun risk.

**Decision**: **Option 1 — preserve name**. Rationale:
- Slice scope is cleanup-only; minimal blast radius preferred.
- Docstring update (AC #3) communicates the scoping discipline; function name doesn't need to.
- EPGD-1 self-application stays vacuous at the function-name level (0 of 15 touched); preserves discipline.
- SCPD-1 proactive-application stays vacuous (no Dim 9 sub-clause supersession; no shippability row propagation needed).
- TPHD-1 self-application stays vacuous on this slice (no Critic-fix-prose function-name changes expected; if Critic suggests one, harmonize TF-1 plan in same fix block per TPHD-1 sub-mode (a)).

This decision is encoded into the design and AC framing. /critique should challenge if a renaming case is stronger — the design is open to revision.

## Regression test design

**Per /critique M2 ACCEPTED-FIXED**: original design was partially tautological — the regression test constructed synthetic content + asserted properties of that self-constructed content, exercising the boundary-slicing logic in isolation but failing to prove the refactored sibling test's CALL to that logic would correctly fail on real-world drift. The link between regression-test-passes and sibling-test-fails-on-stripped-fixture would have been established only by code-reading, not execution.

**Resolution**: extract `_extract_v031_body(content: str) -> str` helper at module level. Both the refactored sibling test AND the new regression test call this single helper. The regression test then directly exercises the same code path the sibling uses — `assert "Sub-mode (a)" not in _extract_v031_body(synthetic)` empirically proves the discipline.

**Helper signature + location**:

```python
# Module-level helper, inserted near `read_file` definition at top of test_methodology_changelog.py

def _extract_v031_body(content: str) -> str:
    """Extract methodology-changelog.md v0.31.0 entry body, scoped between
    `## v0.31.0` and `## v0.30.0` boundaries.

    Returns rest-of-file from `## v0.31.0` start if `## v0.30.0` is absent
    (fallback branch retained for symmetry with slice-017 TPHD-1 sibling
    canonical pattern at L1091-1094, though triggers only if v0.30.0 entry
    is deleted — an extraordinary regression beyond this slice's threat
    model per /critique m1 ACCEPTED-FIXED).

    Pre-validation contract: caller MUST have already asserted
    `"## v0.31.0" in content` and emitted a surface-context-aware error
    message at the call site (per /critique-review m-add-1 ACCEPTED-FIXED —
    surface_name interpolation preserves slice-017 L1088-1090 diagnostic
    pattern). Helper returns empty/garbage if `## v0.31.0` is absent, so
    downstream assertions will fail; but the surface-context error message
    must come from the caller. Helper does NOT re-assert.

    Used by both `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed`
    (refactored sibling test reading real methodology-changelog.md) AND
    `test_v_0_31_0_rpcd_1_sibling_scoping_rejects_stripped_v031_body`
    (regression test verifying scoping discipline on synthetic content).
    Single code path under test — per /critique M2 ACCEPTED-FIXED.
    """
    v031_start = content.find("## v0.31.0")
    v030_start = content.find("## v0.30.0", v031_start) if v031_start != -1 else -1
    if v030_start == -1:
        return content[v031_start:] if v031_start != -1 else ""
    return content[v031_start:v030_start]
```

**Refactored sibling test** (`tests/methodology/test_methodology_changelog.py:910-951` — body refactored):

```python
def test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed():
    """methodology-changelog v0.31.0 / RPCD-1 entry must name ALL THREE
    sub-modes (a)/(b)/(c) bidirectionally, scoped strictly to the v0.31.0
    entry body (NOT global file substring).

    Scoping fix vs original slice-016 implementation: the original test
    used global substring check, which would false-positive pass on any
    later entry's markers (e.g., v0.32.0+ entries retaining Sub-mode
    markers while v0.31.0 body had them stripped). This slice-018 fix
    scopes to the v0.31.0 body specifically (between `## v0.31.0` and
    `## v0.30.0` boundaries via `_extract_v031_body` helper) — proper
    methodology-pin discipline.

    Evidence anchor: slice-017 DEVIATION-1 (N=1 first-Critic-MISS at
    /critique + /critique-review; surfaced at /build-slice Phase 2b
    empirical pytest behavior analysis). Canonical pattern: slice-017
    TPHD-1 sibling at `test_methodology_changelog.py:1086-1094`.

    Sub-mode anchors per slice-016 design.md Audit 1-3 canonical body,
    scoped to the v0.31.0 entry body (not global file):
      - Sub-mode (a) NEW-symbol import-audit
      - Sub-mode (b) NEW-status/token allowlist-audit (`_ALLOWED_STATUSES`)
      - Sub-mode (c) NEW-anchor sibling-grep audit (`sibling`)

    Rule reference: RPCD-1 (slice-016 AC #1 — sub-mode pin) +
    slice-018 (test-scoping discipline restoration).
    """
    in_repo = read_file("methodology-changelog.md")
    installed_path = Path.home() / ".claude" / "methodology-changelog.md"
    installed = installed_path.read_text(encoding="utf-8")

    for surface_name, content in [("in-repo", in_repo), ("installed", installed)]:
        # Surface-context-aware pre-validation per /critique-review m-add-1
        # ACCEPTED-FIXED (preserves slice-017 L1088-1090 diagnostic pattern):
        # assert lives at call site so error message can interpolate
        # surface_name; helper assumes pre-validated input.
        assert "## v0.31.0" in content, (
            f"{surface_name} methodology-changelog.md missing v0.31.0 entry — "
            f"entry-pin broken (slice-016 RPCD-1 surface)"
        )
        v031_body = _extract_v031_body(content)

        # Sub-mode markers must appear in v0.31.0 body (scoped via helper)
        assert "Sub-mode (a)" in v031_body, (
            f"{surface_name} methodology-changelog.md v0.31.0 body missing "
            f"'Sub-mode (a)' marker — three-sub-mode pin broken"
        )
        assert "Sub-mode (b)" in v031_body, (
            f"{surface_name} methodology-changelog.md v0.31.0 body missing "
            f"'Sub-mode (b)' marker — three-sub-mode pin broken"
        )
        assert "Sub-mode (c)" in v031_body, (
            f"{surface_name} methodology-changelog.md v0.31.0 body missing "
            f"'Sub-mode (c)' marker — three-sub-mode pin broken"
        )
        assert "_ALLOWED_STATUSES" in v031_body, (
            f"{surface_name} methodology-changelog.md v0.31.0 body missing "
            f"'_ALLOWED_STATUSES' substring — sub-mode (b) discipline "
            f"anchor broken"
        )
        assert "sibling" in v031_body, (
            f"{surface_name} methodology-changelog.md v0.31.0 body missing "
            f"'sibling' substring — sub-mode (c) discipline anchor broken"
        )
```

**Regression test** (`tests/methodology/test_methodology_changelog.py` — NEW function inserted at ~L953):

```python
def test_v_0_31_0_rpcd_1_sibling_scoping_rejects_stripped_v031_body():
    """Regression test: prove the v0.31.0 scoping discipline (via
    `_extract_v031_body` helper) catches stripped sub-mode markers within
    v0.31.0 body even when v0.32.0+ entries retain them.

    Defect class (slice-017 DEVIATION-1, N=1 first-Critic-MISS):
    the original slice-016 `_names_three_sub_modes` test pattern used
    global substring check. If a future slice strips Sub-mode (a)/(b)/(c)
    markers from the v0.31.0 entry body while v0.32.0+ retains them,
    the global check would false-positive PASS — methodology pin
    silently broken.

    Single-code-path discipline (per slice-018 /critique M2 ACCEPTED-FIXED):
    both the refactored sibling test AND this regression test call the
    SAME `_extract_v031_body` helper. So this test's assertion empirically
    proves the sibling's scoping would catch real-world v0.31.0-body
    marker stripping (not just self-constructed synthetic content).

    Rule reference: slice-018 AC #2 + slice-017 DEVIATION-1 evidence.
    """
    synthetic = (
        "## v0.32.0\n"
        "Sub-mode (a) /critique post-fix-prose harmonization\n"
        "Sub-mode (b) /critique-review post-fix-prose harmonization\n"
        "Sub-mode (c) /build-slice Prerequisite-check pre-flight\n"
        "\n"
        "## v0.31.0\n"
        "[markers stripped — regression fixture]\n"
        "_ALLOWED_STATUSES kept\n"
        "sibling kept\n"
        "\n"
        "## v0.30.0\n"
        "earlier entry\n"
    )
    v031_body = _extract_v031_body(synthetic)

    # The scoping discipline (same helper the sibling uses) catches the
    # stripped markers in v0.31.0 body
    assert "Sub-mode (a)" not in v031_body, (
        "regression: _extract_v031_body failed to isolate v0.31.0 body — "
        "the slice-016 RPCD-1 sibling test would silently PASS on stripped "
        "markers if this helper drifted"
    )
    # But the marker IS present file-globally — proves the global-substring
    # fallacy the scoping fix defends against
    assert "Sub-mode (a)" in synthetic, (
        "regression-test fixture malformed: v0.32.0 must retain marker for "
        "the test to demonstrate the global-substring fallacy"
    )
```

**Single-code-path guarantee**: both the refactored sibling test (real file) AND the regression test (synthetic content) call `_extract_v031_body`. If a future regression breaks the helper's scoping logic, the regression test fails AND the sibling test silently mis-pins simultaneously — they fail-coherently. Per /critique M2 ACCEPTED-FIXED: regression-test-passes ↔ sibling-test-fails-on-stripped-fixture link established by execution, not code-reading.

**Insertion order at build time**:
1. `_extract_v031_body` helper inserted at module top (near `read_file`)
2. `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed` body refactored at L910-951 to call helper
3. `test_v_0_31_0_rpcd_1_sibling_scoping_rejects_stripped_v031_body` inserted at ~L953 (after refactored sibling, before `# --- ADR-015 pin (slice-016) ---` SECTION at L954)

## Design-time audits

### Audit 1: Empirical confirmation that ONLY slice-016 RPCD-1 sibling has the flaw

Performed at /design-slice (this slice). Confirmed:
- `tests/methodology/test_methodology_changelog.py:910` `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed` — HAS flaw (uses `content` raw)
- `tests/methodology/test_methodology_changelog.py:1055` `test_v_0_32_0_tphd_1_entry_names_three_sub_modes_in_repo_and_installed` — clean (uses `v032_body` scoped, L1086-1094 canonical pattern)
- `tests/methodology/test_critique_agent.py:690` `test_critique_dim_9_runtime_prerequisite_completeness_names_three_sub_modes` — clean (uses `start_anchor`/`end_anchor` scoping at L707-713; targets `agents/critique.md` Dim 9 sub-clause body, NOT methodology-changelog version body — different scoping discipline, also correct)

**Result**: only ONE test needs refactoring. Mission brief's "Out of scope: Updating any OTHER `_names_N_sub_modes` test" assertion empirically validated.

### Audit 2: Entry-pin function count empirical verification

Performed at /design-slice (this slice). Confirmed:
- `grep -c "^def test_v_0_" tests/methodology/test_methodology_changelog.py` returns **15** functions:
  - L76 (v0.22.0 CAD-1) + L111 (v0.23.0 BC-1 v1.2) + L152 (v0.24.0 CCC-1 v1.1) + L202 (v0.25.0 MCT-1) + L250 (v0.26.0 RSAD-1) + L304 (v0.27.0 BC-PROJ-2) + L370 (v0.28.0 EPGD-1) + L437 (v0.29.0 PMI-1 v1.1 entry-pin) + L499 (v0.29.0 supersession-pattern-retired duality) + L747 (v0.30.0 SCPD-1) + L844 (v0.31.0 RPCD-1 entry-pin) + L910 (v0.31.0 RPCD-1 three-sub-modes duality) + L988 (v0.32.0 TPHD-1 entry-pin) + L1055 (v0.32.0 TPHD-1 three-sub-modes duality) + L1124 (v0.32.0 TPHD-1 cross-slice-anchor duality)
  - = 8 singles + 2 doublets (v0.29.0 + v0.31.0) + 1 triplet (v0.32.0) = 15 functions
- Mission brief said "15 entry-pin functions total" — empirically VALIDATED.
- EPGD-1 self-application: 0 of 15 prior entry-pin functions touched at the FUNCTION-NAME level. The L910 function's BODY changes; the function NAME is preserved (per "Decision: preserve name" above). Structural separation discipline holds.

**Result**: EPGD-1 self-application vacuous at the function-name level — no NEW SECTION header insertion needed; no Phase 1b NEW SECTION discipline (which is for codification slices adding new version entries). This is a body-only edit to one existing function + a sibling-function append.

### Audit 3: Slice-017 TPHD-1 sibling canonical pattern empirically present

Performed at /design-slice (this slice). Confirmed at L1086-1094:
- `v032_start = content.find("## v0.32.0")` ✓
- `v031_start = content.find("## v0.31.0", v032_start)` ✓
- `assert v032_start != -1, ...` ✓
- `if v031_start == -1: v032_body = content[v032_start:]` ✓
- `else: v032_body = content[v032_start:v031_start]` ✓

Pattern reproduces verbatim for v0.31.0 ↔ v0.30.0 boundaries at the **boundary-slicing-pattern level** (find anchors + assert + fallback). Three substantive elements: (1) `content.find` from `v031_start` to anchor the search to AFTER v0.31.0 header; (2) `assert v031_start != -1` for fail-fast on missing v0.31.0 entry — at the CALL site, surface-context-aware (per /critique-review m-add-1 ACCEPTED-FIXED); (3) `if v030_start == -1` fallback to rest-of-file for boundary-not-found edge case.

**Post-M2 fix nuance** (per /critique-review m-add-2 ACCEPTED-FIXED): the literal-code form is NOT verbatim — slice-018 wraps the boundary slicing in `_extract_v031_body` helper, while slice-017 inlines at L1086-1094. Symmetry is preserved at the **pattern level** (anchors + assert + fallback), not the **literal-code level**. See Audit 7 for explicit foreshadowing-decline of generic `_extract_version_body(content, start_marker, end_marker)` helper.

**Result**: canonical pattern verified at the pattern level; slice-018 adapts the boundary-slicing discipline 1-to-1 with helper-wrap added per M2.

### Audit 4: Shippability.md row 16 empirical enumeration

Performed at /critique fix-prose (per M4 ACCEPTED-FIXED — must-not-defer L63 said verify at /design-slice but was deferred until /critique surfaced the unverified claim).

Empirical inspection of `architecture/shippability.md` row 16 (file line 24, slice-016-refine-dim-9-with-runtime-prerequisite-completeness-sub-class):

- Row 16 contains ~12 pytest commands in a single bash-pipeline-style line
- One of them is `tests/methodology/test_methodology_changelog.py::test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed`
- The remaining ~11 commands reference: `_lists_nine_sub_clauses`, `_sub_clause_present`, `_location_pinned`, `_paragraph_cites_slice_013_014_015`, `_cites_substantive_discipline_anchors`, `test_critique_agent_drift`, `test_v_0_31_0_rpcd_1_entry_present_in_repo_and_installed`, `test_adr_015_exists_and_names_rpcd_1_canonical_phrase`, `test_plugin_yaml_version_matches_version_file_invariant`
- The preserved function name `_entry_names_three_sub_modes_in_repo_and_installed` is referenced **exactly once** in row 16

**Result**: Per Decision (preserve name), row 16 is unchanged this slice. SCPD-1 sub-mode (b) proactive-application: vacuous. No /build-slice Phase 5 propagation Edit needed.

### Audit 5: BC-1 self-application empirical verification

Performed at /critique fix-prose (per m3 ACCEPTED-FIXED).

Command run from repo root:
```
$PY -m tools.build_checks_audit --slice architecture/slices/slice-018-cleanup-slice-016-rpcd-1-sibling-test-scoping-flaw --changed-files architecture/slices/slice-018-cleanup-slice-016-rpcd-1-sibling-test-scoping-flaw/mission-brief.md architecture/slices/slice-018-cleanup-slice-016-rpcd-1-sibling-test-scoping-flaw/design.md
```

Literal output:
```
No build-checks rules apply to this slice.
```

**Result**: BC-PROJ-2 negative-anchor migration from slice-012 successfully silences slice-018's methodology vocabulary at design-time. Zero BC-PROJ-2 + zero BC-GLOBAL-1 fires. Defends the must-not-defer L59 claim with empirical evidence (not assumption). Recurrence of slice-005/006/007/010/011 methodology-vocabulary false-positive class **NOT** observed at slice-018 (N=5 cumulative stable; no ratchet).

### Audit 6: Boundary-find inline-prose collision — defer to /reflect watch-list

Performed at /critique fix-prose (per M3 ACCEPTED-FIXED option (b)).

**Edge case considered**: `content.find("## v0.31.0")` matches first occurrence; if a future later-version body (e.g., v0.40.0) carries `"## v0.31.0"` as quoted narrative (e.g., inside a code block or retrospective reference), `find()` returns the wrong boundary.

**Empirical state of `methodology-changelog.md` at slice-018 start**:
- `## v0.31.0` and `## v0.30.0` are unique heading-only occurrences in BOTH in-repo + installed surfaces (verified at /critique-review fix-prose per m-add-3 ACCEPTED-FIXED):
  - `grep -c "^## v0.30.0" <HOME>/.claude/methodology-changelog.md` → **1** (installed)
  - `grep -c "^## v0.30.0" <HOME>/ai_sdlc/methodology-changelog.md` → **1** (in-repo)
  - Both surfaces have v0.30.0 + v0.31.0 + v0.32.0 entry headings present uniquely
- The codebase frequently uses retrospective references like "post-slice-013/014/015", "v0.29.0 doubled", "supersession N=N stable" — but NEVER as exact heading literals (`## v0.NN.0` form)
- Today's file has no inline-prose collision (bidirectional empirical confirmation)

**Defer-not-tighten decision**: option (b) chosen per /critique M3 ACCEPTED-FIXED rationale:
- (1) No inline-prose collision in today's file → no current regression risk
- (2) Tightening to `\n## v0.31.0` would break symmetry with slice-017 TPHD-1 sibling canonical pattern at L1086 (design.md Audit 3 "Pattern reproduces verbatim" assertion would become false; canonical-pattern symmetry across slice-017 + slice-018 is structurally load-bearing for /reflect future-pattern recognition)
- (3) Cleanup-slice scope should not retrofit slice-017 (would expand scope from 1 test refactor to 2)

**Watch-list candidate registered at N=1**: "boundary-find inline-prose collision tightening" added to mission-brief.md out-of-scope as future cleanup-slice candidate. Promote at N=2 if inline-prose collision actually surfaces (i.e., a future codification slice adds prose containing `## v0.NN.0` literal inside a body).

**Result**: limitation explicitly acknowledged + deferred. The slice ships with the design's symmetric-with-slice-017 pattern; the limitation is documented for future scope.

### Audit 7: Helper-extraction asymmetry vs slice-017 — explicit foreshadowing-decline of generic `_extract_version_body`

Performed at /critique-review fix-prose (per m-add-2 ACCEPTED-FIXED).

**Asymmetry observed post-M2 fix**: `_extract_v031_body(content: str) -> str` introduced for v0.31.0 only; v0.32.0 sibling at `tests/methodology/test_methodology_changelog.py:1086-1094` keeps boundary-slicing inline. Asymmetric design between slice-018 + slice-017 sibling tests at the literal-code level.

**Generic helper foreshadowing**: `_extract_version_body(content: str, start_marker: str, end_marker: str) -> str` would parameterize the boundary slicing and unify both v0.31.0 + v0.32.0 (and future vNN) sibling tests. Reachable as a 5-minute refactor at any future slice.

**Decision — DECLINE foreshadowing at slice-018**:
- (1) **Fowler rule-of-three**: only N=1 helper instance at slice-018 (just v0.31.0). Refactor to generic helper requires N≥2 instances per Fowler's rule. Slice-017's inline pattern is N=1 (v0.32.0); they're not yet "the same pattern repeated 3 times" by Fowler's discipline.
- (2) **YAGNI** (Beck): no current slice or future planned slice needs `_extract_version_body` generalization. Adding it speculatively inflates the surface area without immediate value.
- (3) **Cleanup-slice scope**: slice-018 is a narrow cleanup of slice-016's scoping flaw; retrofitting slice-017's inline pattern into the helper expands scope from "1 test refactor" to "2 test refactors + new generic helper + migration of slice-017 to use it".
- (4) **Slice-017 canonical pattern symmetry**: tightening slice-017 would itself require Critic stack review (cross-cutting tooling slice per MCT-1); deferring keeps slice-018 narrow.

**Watch-list registration at N=1**: "generic `_extract_version_body` helper" added to mission-brief.md implicit watch-list as a future cleanup-slice candidate. Promote at N≥2 if a future codification slice introduces a third `_extract_vNN_body` need (slice-018 + slice-017 inline + future slice = N=3 hits per Fowler rule-of-three).

**Result**: helper-extraction asymmetry explicitly acknowledged + decline rationale documented. Audit 3 updated to reflect post-M2 pattern-level (NOT literal-code-level) symmetry framing.

## Risk profile

- **Latent-regression risk retired**: HIGH — silent false-positive on a methodology pin is a methodology-correctness regression (worse than a code regression because methodology-correctness underpins the test-discipline foundation of all subsequent slices)
- **Slice introduces NEW risk**: LOW — boundary slicing edge cases (v0.30.0 absent, v0.31.0 absent) covered by fallback logic + regression test
- **Slice blast radius**: small — single test file edit; full methodology suite re-run + shippability catalog re-run at /validate-slice catches any unintended regression
- **EPGD-1 self-application**: vacuous (0/15 function-name level)
- **CAD-1 byte-equality on agents/critique.md**: preserved (slice doesn't touch the file)
- **PMI-1 v1.1 invariant**: preserved (no version bump; gate stays at 0.32.0)
- **BC-1 self-application**: methodology-vocabulary slices recur with negative-anchor false-positive class; slice-018 should be silenced by BC-PROJ-2 negative-anchor migration from slice-012

## Mid-slice smoke gate (from mission brief)

After refactoring the slice-016 RPCD-1 sibling test BUT BEFORE writing the regression test:

```
<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/test_methodology_changelog.py::test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant tests/methodology/test_critique_agent_drift.py -q
```

Expected: 3 PASS. Failure modes:
- Refactored sibling test fails: scoping boundary slicing has a bug (e.g., `v030_start` lookup misses because methodology-changelog.md doesn't have `## v0.30.0` for some reason → verify file at /design-slice).
- PMI-1 fail: version files accidentally touched (this slice should NOT bump versions).
- CAD-1 fail: `agents/critique.md` was accidentally edited.

**Pre-smoke verification**: Confirm `## v0.30.0` exists in `methodology-changelog.md` (both in-repo + installed). If absent, the regression test's fallback branch is the actual code path, AND the refactored sibling test's `v031_body` becomes the full rest-of-file — which still works correctly (defense-in-depth) but design.md should call out the actual case.

## Lessons applied from recent reflections

- **TPHD-1 (slice-017)**: this slice's TF-1 plan in mission-brief.md harmonized BEFORE /design-slice complete — sub-mode (c) /build-slice Prerequisite-check pre-flight harmonization vacuous at /slice→/design-slice (no function-name changes between /slice and /design-slice). At /critique fix-prose, if Critic suggests function rename, TPHD-1 sub-mode (a) requires harmonizing TF-1 plan + verification-plan in same fix block.
- **RPCD-1 (slice-016)**: design-time audits performed for sub-mode (c) NEW-anchor sibling-grep (Audit 1 above empirically confirms ONLY one sibling has the flaw, not multiple).
- **SCPD-1 (slice-015)**: shippability catalog row 16 pytest command stays unchanged this slice (function name preserved per "Decision" above); SCPD-1 proactive-application vacuous.
- **EPGD-1 (slice-013)**: 0 of 15 entry-pin functions touched at the function-name level (Audit 2 above); structural separation discipline preserved.
- **RSAD-1 (slice-011)**: design.md docs the actual scope (single file, single function refactor + sibling append), not aspirational scope (no Dim 9 promotion, no codification).
- **MCT-1 (slice-010)**: slice-018 NOT in MCT-1 trigger glob (`tests/methodology/test_methodology_changelog.py` is not in `skills/*/SKILL.md` / `agents/*.md` / `tools/**/*.py` / `methodology-changelog.md`); critic-required=true is VOLUNTARY per slice-017 reflection N=9/9 ROI on methodology-tooling-adjacent slices.
- **CCC-1 v1.1 (slice-009)**: design.md mechanical tables (this file's "Edit-locations summary") empirically cross-checked against actual L910-951 + L1086-1094 content via Read (Audit 3 above).

## Cumulative counter touchpoints

This slice is **expected to NOT ratchet** any of the following counters (cleanup-only):
- N=15 entry-pin functions stable (no NEW entry-pin)
- ADR-pin convention N=4 stable (no NEW ADR)
- -D suffix rule-ID convention N=5 stable (no NEW rule)
- N-surface schema-pin 3-surface shape N=6 stable (no NEW schema-pin)
- methodology-changelog version stays at 0.32.0 (no version bump)
- VAL-1 Layer B intra-repo `tests` namespace-package N=15 → **N=16 cumulative** if Layer B audit fires again (likely; tracked at /validate-slice)
- 100% Critic-disposition accuracy streak: N=12 → **N=13 cumulative** IF /critique catches no SUSPICIOUS / SEVERITY-WRONG / OVERRIDE-MISJUDGED (target)

This slice **IS expected to retire**:
- Slice-017 NEW first-Critic-MISS class `test-scoping-flaw-inherited-across-codification-slice-siblings` at N=1 — formally retired inline at this slice via the refactor (no Dim 9 promotion needed)
- Latent regression risk on slice-016 RPCD-1 pin (silent false-positive failure mode)

## Open questions / Critic-fodder

(None expected — design is intentionally minimal. /critique should flag any of the following if they apply):
- Should the refactored test ALSO update its docstring section "Sub-mode anchors per slice-016 design.md Audit 1-3 canonical body" to reference v0.31.0 body explicitly? (Currently the docstring is unchanged in body except for the appended scoping-fix paragraph.)
- Should the regression test ALSO cover the `_ALLOWED_STATUSES` + `sibling` sub-mode (b)/(c) discipline anchors (not just `Sub-mode (a)`)? Current design covers only `Sub-mode (a)` to keep regression-test minimal; if Critic wants exhaustive coverage, expand.
- Should the boundary-not-found fallback (when `## v0.30.0` is absent) be its OWN regression test? Current design relies on the synthetic-content regression test alone covering both branches by construction.

These are open for /critique to challenge.
