"""Verify cost-optimized model dispatch (COST-1) in the three Haiku-suitable skills.

Per COST-1 (methodology-changelog.md v0.4.0), /commit-slice, /pulse, and
/archive (index regeneration) explicitly dispatch their template-filling
or rendering work to a Haiku subagent rather than running entirely on the
main thread's model.

A skill's SKILL.md must name `model: haiku` AND reference `subagent_type:
"general-purpose"` in its dispatch step. Without these markers the
optimization is invisible to executors and silently doesn't happen.

Rule reference: COST-1.
"""
import re
from pathlib import Path

import pytest

from tests.methodology.conftest import REPO_ROOT


# Skills with COST-1 Haiku dispatch directives
COST_1_SKILLS = [
    "skills/commit-slice/SKILL.md",
    "skills/pulse/SKILL.md",
    "skills/archive/SKILL.md",
]


@pytest.mark.parametrize("skill_path", COST_1_SKILLS, ids=lambda p: Path(p).parent.name)
def test_skill_explicitly_names_haiku(skill_path: str):
    """COST-1 skills must explicitly name `model: haiku` in their dispatch step.

    Defect class: Skills that don't explicitly name the model run on whatever
    the user has set globally — typically Opus. The cost optimization sits
    unused without an explicit directive in the SKILL.md.
    Rule reference: COST-1.
    """
    text = (REPO_ROOT / skill_path).read_text(encoding="utf-8")
    assert re.search(r"`?model:\s*haiku`?", text, re.IGNORECASE), (
        f"{skill_path}: no explicit `model: haiku` dispatch directive found"
    )


@pytest.mark.parametrize("skill_path", COST_1_SKILLS, ids=lambda p: Path(p).parent.name)
def test_skill_uses_general_purpose_subagent(skill_path: str):
    """COST-1 skills dispatch via general-purpose subagent type.

    Defect class: Without naming the subagent type, the dispatch route is
    ambiguous. `general-purpose` is the right type for one-off
    template/extraction work on Haiku (a named subagent would be overkill
    for these patterns).
    Rule reference: COST-1.
    """
    text = (REPO_ROOT / skill_path).read_text(encoding="utf-8")
    assert re.search(r'subagent_type:\s*[\"\']?general-purpose', text), (
        f"{skill_path}: no `subagent_type: \"general-purpose\"` reference found"
    )


@pytest.mark.parametrize("skill_path", COST_1_SKILLS, ids=lambda p: Path(p).parent.name)
def test_skill_documents_why_haiku(skill_path: str):
    """COST-1 skills explain why Haiku is appropriate for the dispatched work.

    Defect class: Without rationale, future edits may revert the dispatch
    "to be safe" or escalate to Opus thinking the work is more complex than
    it is. The "Why Haiku" justification documents the cognitive-shape
    analysis so future maintainers don't undo the optimization unaware.
    Rule reference: COST-1.
    """
    text = (REPO_ROOT / skill_path).read_text(encoding="utf-8")
    assert "Why Haiku" in text, (
        f"{skill_path}: missing 'Why Haiku' rationale section in dispatch step"
    )


@pytest.mark.parametrize("skill_path", COST_1_SKILLS, ids=lambda p: Path(p).parent.name)
def test_skill_references_cost_1_rule(skill_path: str):
    """COST-1 skills reference the rule by ID for cross-link to the changelog.

    Defect class: Rule changes that aren't traceable can't be evaluated for
    impact. A `COST-1` reference in the SKILL.md prose lets readers trace
    the rule back to methodology-changelog.md for full rationale.
    Rule reference: COST-1.
    """
    text = (REPO_ROOT / skill_path).read_text(encoding="utf-8")
    assert "COST-1" in text, (
        f"{skill_path}: no `COST-1` rule reference found in dispatch step"
    )
