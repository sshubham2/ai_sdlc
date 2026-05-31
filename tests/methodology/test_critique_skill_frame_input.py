"""PFS-1 structural pin: `/critique` hands the project-frame to the Critic agent
(slice-088; [[ADR-080]]).

BC-PROJ-14 compliant: line-anchored heading seam (`^### Step 2:` — the
agent-prompt-body seam), a unique-to-invocation literal (the `# project-frame.md`
paste-block header, which appears nowhere else in the file), line-anchored shape
assertion (not a bare `.find("project-frame")`, which a value-line substring
would mask).

Rule reference: PFS-1 (slice-088; ADR-080).
"""
import re

from tests.methodology.conftest import REPO_ROOT

SKILL = REPO_ROOT / "skills" / "critique" / "SKILL.md"


def _step2_seam(text: str) -> str:
    m = re.search(r"(?m)^### Step 2:", text)
    assert m, "### Step 2: heading not found in critique/SKILL.md"
    rest = text[m.end():]
    nxt = re.search(r"(?m)^### ", rest)
    return rest[: nxt.start()] if nxt else rest


def test_critique_inputs_include_project_frame():
    seam = _step2_seam(SKILL.read_text(encoding="utf-8"))
    # Shape: the `# project-frame.md` paste-block header on its own line within
    # the Step-2 agent-prompt body (mirrors the `# mission-brief.md` /
    # `# design.md` block headers the Critic agent is handed).
    assert re.search(r"(?m)^# project-frame\.md\s*$", seam), (
        "critique Step 2 agent-prompt body must include a `# project-frame.md` block"
    )
