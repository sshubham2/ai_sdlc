"""BCR-1 round-trip end-to-end input-contract test (slice-054).

AC4 of slice-054 says: ``/reflect round-trips the **Addressed:** line into
diagnose-out/backlog.md SC-001 block AFTER **Evidence:** (BCR-1 first
end-to-end dogfood; triggered by **Closes:** SC-001 sentinel header).``

The /reflect-time OUTPUT verification (position-pinned Addressed line) is
covered at /validate-slice via the mission-brief verification-plan row 4
(awk + line-number check per /critique M4). THIS test covers the INPUT
contract that makes BCR-1 fire correctly at /reflect-time:

  (a) mission-brief.md carries the M4 sentinel ``**Closes:** SC-001``
      (NOT a bare ``SC-001`` mention — slice-053 first-Critic M4 ACCEPTED-FIXED
      mentioned-vs-closes disambiguation).
  (b) diagnose-out/backlog.md has a discoverable ``### SC-001 —`` block.
  (c) the SC-001 block has the ``**Evidence:**`` anchor BCR-1 uses for
      insertion-position resolution (slice-053 M-add-1 graceful-degradation
      uses last top-level metadata bullet as fallback ONLY when Evidence is
      absent — SC-001 has Evidence, so this is the strict path).

If all three INPUT preconditions hold, BCR-1 at /reflect-time WILL insert
the Addressed line at the correct position. If any fails, BCR-1 either
silently no-ops (sentinel absent → trigger doesn't fire) or graceful-
degrades (Evidence absent → falls back to last-metadata-bullet). Both are
slice-054 self-violations the slice should refuse at /build-slice.

Post-/reflect state (Addressed line present) does NOT break this test —
slice-053 first-Critic m5 ACCEPTED-FIXED clarifies: multiple **Addressed:**
lines per candidate are valid (APPEND, never replace). So the test is
re-runnable across the /build → /validate → /reflect → /validate boundary.

Rule reference: BCR-1 (slice-053; ADR-055) — first end-to-end dogfood at
slice-054 / PVFS-1 / ADR-056 closes SC-001.
"""

from __future__ import annotations

import re

from tests.methodology.conftest import REPO_ROOT


SLICE_054_DIR = REPO_ROOT / "architecture" / "slices" / "slice-054-fix-pyproject-toml-version-drift"
BACKLOG_PATH = REPO_ROOT / "diagnose-out" / "backlog.md"


def _read_slice_054_mission_brief() -> str:
    """Read slice-054 mission-brief.md.

    AssertionError (not FileNotFoundError) if absent — keeps pytest
    reporting consistent with the other slice-054 entry-pin tests.
    """
    path = SLICE_054_DIR / "mission-brief.md"
    assert path.exists(), (
        f"slice-054 mission-brief.md missing at {path} — "
        "BCR-1 input contract cannot be verified without the brief"
    )
    return path.read_text(encoding="utf-8")


def _read_backlog() -> str:
    """Read diagnose-out/backlog.md.

    AssertionError if absent — slice-054 closes SC-001 from this backlog,
    so its absence is itself a BCR-1 input-contract violation.
    """
    assert BACKLOG_PATH.exists(), (
        f"diagnose-out/backlog.md missing at {BACKLOG_PATH} — "
        "slice-054 closes SC-001 from this file; the BCR-1 round-trip "
        "cannot fire without it"
    )
    return BACKLOG_PATH.read_text(encoding="utf-8")


def _extract_sc_block(backlog_text: str, sc_id: str) -> str:
    """Extract the ``### <sc_id> —`` block up to the next ``### SC-NNN`` header
    or end-of-file. Used by both the input-contract test below and the
    /validate-slice position-pinned awk check at mission-brief.md
    verification-plan row 4.
    """
    pattern = re.compile(
        rf"^### {re.escape(sc_id)} —.*?(?=^### SC-\d{{3}} —|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(backlog_text)
    assert match, f"backlog.md missing `### {sc_id} —` block — BCR-1 cannot find the closed candidate"
    return match.group(0)


def test_bcr_1_sc054_round_trip_inputs_invariant():
    """BCR-1 first end-to-end dogfood — INPUT contract verification.

    Three preconditions that make /reflect-time BCR-1 round-trip fire
    correctly:

      (a) mission-brief carries ``**Closes:** SC-001`` sentinel
      (b) backlog.md has ``### SC-001 —`` block
      (c) SC-001 block has ``**Evidence:**`` anchor (BCR-1 strict-path
          insertion position; graceful-degradation only fires on absence)

    PASS pre-/reflect AND post-/reflect (slice-053 m5: multiple Addressed
    lines valid). FAIL only if the input contract is broken — a real
    slice-054 defect, not a stage-transient state.
    """
    # (a) M4 sentinel discipline (slice-053 first-Critic M4 ACCEPTED-FIXED)
    mission_brief = _read_slice_054_mission_brief()
    assert "**Closes:** SC-001" in mission_brief, (
        "slice-054 mission-brief.md missing the BCR-1 trigger sentinel "
        "`**Closes:** SC-001` — without it the /reflect round-trip "
        "silently no-ops on slice-054 (which IS the first end-to-end "
        "BCR-1 dogfood — the slice exists to exercise the wire). "
        "Per slice-053 M4: the trigger is the literal sentinel, NOT a "
        "bare `SC-001` mention; documentation-class mentions of `SC-001` "
        "elsewhere in the brief do not satisfy this assertion."
    )

    # (b) Backlog block discoverable
    backlog = _read_backlog()
    sc001_block = _extract_sc_block(backlog, "SC-001")
    assert "### SC-001 —" in sc001_block, (
        "diagnose-out/backlog.md SC-001 block extraction failed at the "
        "header level — the block has structurally drifted"
    )

    # (c) Evidence anchor for BCR-1 strict-path insertion
    assert "**Evidence:**" in sc001_block, (
        "SC-001 block in diagnose-out/backlog.md missing the "
        "`**Evidence:**` anchor — BCR-1 would graceful-degrade to "
        "last-top-level-metadata-bullet insertion (slice-053 M-add-1), "
        "which is the FALLBACK path. SC-001 has an Evidence sub-list "
        "(verified at slice-054 /design-slice M4 evidence-block "
        "enumeration); its absence here is a backlog.md structural "
        "drift, not a BCR-1-correct state for the strict-path dogfood."
    )
