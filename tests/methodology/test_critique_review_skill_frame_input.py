"""PFS-1 structural pin: `/critique-review` hands the project-frame to the
meta-Critic agent (slice-088; [[ADR-080]]).

BC-PROJ-14 compliant: line-anchored heading seam (`^### Step 2:` — the
agent-prompt-body seam), the unique `# project-frame.md` paste-block header,
line-anchored shape assertion.

Rule reference: PFS-1 (slice-088; ADR-080).
"""
import re

from tests.methodology.conftest import REPO_ROOT

SKILL = REPO_ROOT / "skills" / "critique-review" / "SKILL.md"


def _step2_seam(text: str) -> str:
    m = re.search(r"(?m)^### Step 2:", text)
    assert m, "### Step 2: heading not found in critique-review/SKILL.md"
    rest = text[m.end():]
    nxt = re.search(r"(?m)^### ", rest)
    return rest[: nxt.start()] if nxt else rest


def test_critique_review_inputs_include_project_frame():
    seam = _step2_seam(SKILL.read_text(encoding="utf-8"))
    assert re.search(r"(?m)^# project-frame\.md\s*$", seam), (
        "critique-review Step 2 agent-prompt body must include a "
        "`# project-frame.md` block"
    )
