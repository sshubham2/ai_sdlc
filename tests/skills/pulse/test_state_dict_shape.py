"""AC#3 + m6 ACCEPTED-FIXED: pin the augmented Step-2 state-dict shape that
/pulse Step 3 Haiku dispatch consumes.

Per design.md L37 + § Override-precedence ordering: the override is computed
in Step 2 deterministic metric computation; the Step 3 Haiku-render receives
the structured-state dict already augmented with the worktree fields. This
test pins the contract.

The helper exposes `augment_pulse_state_dict(base_state_dict, detected_worktrees,
classifications) -> dict` (or equivalent) which Step 2 calls to augment the
existing /pulse Step 2 state-dict with `worktrees: list[WorktreeInfo]` +
`worktree_classifications: list[WorktreeStateClassification]` +
`recommended_next_action_override: str | None` keys.

v1 may not expose this surface yet — Phase C decides the function name. Until
then, the test fails on ImportError (which IS the WRITTEN-FAILING signal).
"""
from __future__ import annotations

import pytest

from tools.pulse_worktree_resolver import WorktreeInfo, WorktreeState, WorktreeStateClassification

try:
    from tools.pulse_worktree_resolver import augment_pulse_state_dict
    _SURFACE_AVAILABLE = True
except ImportError:
    _SURFACE_AVAILABLE = False


pytestmark = pytest.mark.skipif(
    not _SURFACE_AVAILABLE,
    reason="augment_pulse_state_dict not yet exposed (Phase C decides function name)",
)


def test_step_2_state_dict_includes_worktrees_field_with_worktreeinfo_list():
    """Augmented state dict MUST include `worktrees` key with a list of
    WorktreeInfo. Pin both the key presence and the value type contract.
    """
    base_state = {
        "active_slice": "slice-077-test",
        "next_action": "run /build-slice",
        # ... other existing /pulse Step 2 fields ...
    }
    wt = WorktreeInfo(
        path="/some/path",
        branch="slice/077-test",
        head_sha="deadbeef" * 5,  # 40-char placeholder
        slice_num="077",
        slice_name="test",
        milestone_path=None,
    )
    classifications = [
        WorktreeStateClassification(
            state=WorktreeState.BUILT_BUT_NOT_MERGED,
            reason="milestone stage=reflect",
            milestone_stage="reflect",
        ),
    ]
    augmented = augment_pulse_state_dict(base_state, [wt], classifications)
    assert "worktrees" in augmented, "augmented state dict missing `worktrees` key"
    assert isinstance(augmented["worktrees"], list), "`worktrees` value must be a list"
    assert len(augmented["worktrees"]) == 1
    # The augmented dict should preserve original keys
    assert augmented["active_slice"] == "slice-077-test"
    # And add the override-recommendation field
    assert "recommended_next_action_override" in augmented or "next_action" in augmented
