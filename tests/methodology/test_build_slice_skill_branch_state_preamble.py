"""Pin slice-079 Fix A (slice-074 M1 / P1.1): variable assignments live OUTSIDE numbered codefences.

Slice-074 M1: point-4 codefence references $default / $repo_root / $wt_base, but these vars
were defined ONLY inside point-1 codefence body. The 4 numbered points are mutually-exclusive
branches; the dirty-tree branch did NOT execute point-1 codefence, so a Builder hits unbound vars.

Fix A extracts the assignments to a shared pre-amble ABOVE the numbered list.
"""
from __future__ import annotations

import re
from pathlib import Path

from tests.methodology._skill_parse_helpers import _branch_state_section

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_MD = REPO_ROOT / "skills" / "build-slice" / "SKILL.md"


def _numbered_codefences(section: str) -> list[str]:
    """Extract the bash codefence bodies attached to each numbered list item (1./2./3./4.)."""
    pattern = re.compile(
        r"^\d+\. \*\*[^*]+\*\*[^\n]*\n.*?```bash\n(.*?)```",
        re.DOTALL | re.MULTILINE,
    )
    return pattern.findall(section)


def test_var_assignments_appear_in_shared_preamble_above_numbered_list() -> None:
    """Fix A: repo_root= / wt_base= / default= live in shared pre-amble above numbered list.

    Pre-fix: assignments inside point-1 codefence only -> dirty-tree branch (point 4) hits unbound vars.
    Post-fix: pre-amble executes regardless of which numbered branch fires.
    """
    section = _branch_state_section(SKILL_MD.read_text(encoding="utf-8"))
    list_start = re.search(r"^1\. \*\*If on default branch\*\*", section, re.MULTILINE)
    assert list_start is not None, "Numbered list (point 1) not found"
    preamble = section[: list_start.start()]
    assert 'repo_root="$(git rev-parse --show-toplevel)"' in preamble, (
        "Fix A regression: repo_root= not in shared pre-amble — still scoped inside point-1 codefence body"
    )
    assert 'wt_base="$(dirname "$repo_root")/$(basename "$repo_root")-wt"' in preamble, (
        "Fix A regression: wt_base= not in shared pre-amble"
    )
    assert "default=$(git symbolic-ref" in preamble, (
        "Fix A regression: default= not in shared pre-amble (was at L47 prose)"
    )


def test_numbered_point_codefences_do_not_redefine_shared_vars() -> None:
    """Fix A: numbered point codefences must NOT redefine the shared-pre-amble vars."""
    section = _branch_state_section(SKILL_MD.read_text(encoding="utf-8"))
    codefences = _numbered_codefences(section)
    assert len(codefences) >= 3, f"Expected ≥3 numbered codefences, got {len(codefences)}"
    for i, code in enumerate(codefences, start=1):
        assert 'repo_root="$(git rev-parse --show-toplevel)"' not in code, (
            f"Fix A regression: point {i} codefence redefines repo_root= "
            f"(must be in shared pre-amble only)"
        )
        assert 'wt_base="$(dirname "$repo_root")' not in code, (
            f"Fix A regression: point {i} codefence redefines wt_base="
        )
