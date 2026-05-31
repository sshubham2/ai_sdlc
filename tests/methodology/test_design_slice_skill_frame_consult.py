"""PFS-1 structural pin: `/design-slice` consults the project-frame BEFORE
designing (slice-088; [[ADR-080]]).

BC-PROJ-14 compliant: line-anchored heading seam (`^### Step 0.5`), a
unique-to-invocation literal (the `tools.project_frame_synth ... --slice-dir`
invocation), shape assertion (the invocation LINE shape, not a bare substring),
AND the ordinal "before designing" property (Step 0.5 precedes Step 1).

Rule reference: PFS-1 (slice-088; ADR-080).
"""
import re

from tests.methodology.conftest import REPO_ROOT

SKILL = REPO_ROOT / "skills" / "design-slice" / "SKILL.md"


def _seam_after(text: str, heading_re: str) -> tuple[int, str]:
    m = re.search(heading_re, text, re.MULTILINE)
    assert m, f"heading {heading_re!r} not found in design-slice/SKILL.md"
    rest = text[m.end():]
    nxt = re.search(r"(?m)^### ", rest)
    return m.start(), (rest[: nxt.start()] if nxt else rest)


def test_design_slice_consults_frame_before_design():
    text = SKILL.read_text(encoding="utf-8")
    step05_start, seam = _seam_after(text, r"(?m)^### Step 0\.5\b")

    # Shape: the project-frame invocation LINE (module + required --slice-dir
    # flag) lives within the Step 0.5 seam — not a bare 'project-frame' mention.
    assert re.search(
        r"(?m)^\$PY -m tools\.project_frame_synth\b.*--slice-dir", seam
    ), "Step 0.5 must invoke `$PY -m tools.project_frame_synth ... --slice-dir`"

    # Ordinal "BEFORE designing": Step 0.5 precedes Step 1 (Identify what's new).
    m1 = re.search(r"(?m)^### Step 1\b", text)
    assert m1, "### Step 1 heading not found"
    assert step05_start < m1.start(), "Step 0.5 must precede Step 1 (shift-left)"
