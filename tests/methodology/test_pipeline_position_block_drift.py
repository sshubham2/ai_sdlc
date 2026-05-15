"""PCA-1 / AC #5 element: byte-equality of the `## Pipeline position`
section between in-repo `skills/<name>/SKILL.md` and installed
`~/.claude/skills/<name>/SKILL.md`, for ALL 8 covered skills.

Why section-scoped (not full-file mini-CAD): only `slice` and
`build-slice` have full-file drift tests; `install_audit` only
existence-checks installed skill dirs. PCA-1 makes 6 further skills
carry a runtime-behavioral auto-advance directive — if the in-repo
block is edited but the installed copy is not forward-synced, Claude
reads a stale chain at runtime with NO existing gate catching it
(slice-026 M-add-1 watch-list, now load-bearing). This parametrized
test gives mission-brief AC #5 a 1:1 traceable verification element for
every one of the 8 touched skills (first-Critic M1 + M2).

The full-file mini-CAD generalization for the 6 un-mini-CAD'd skills
remains the deferred `add-skill-drift-audit` N>=2 follow-on (ADR-025
future-slice candidates) — out of scope here.

Rule reference: PCA-1 (methodology-changelog.md v0.41.0); slice-027
/critique M1+M2 ACCEPTED-FIXED.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.methodology.conftest import REPO_ROOT
from tools.pipeline_chain_audit import _CANONICAL_CHAIN, _extract_section

_SKILLS = [skill for skill, _succ, _auto in _CANONICAL_CHAIN]


@pytest.mark.parametrize("skill", _SKILLS)
def test_pipeline_position_block_byte_equal_in_repo_vs_installed(skill: str):
    """The `## Pipeline position` section MUST be byte-equal in-repo vs
    installed for every covered skill (forward-sync after in-repo edit).

    Defect class: stale installed `## Pipeline position` → Claude
    auto-advances on the wrong chain at runtime, undetected by any other
    gate (install_audit is existence-only; only slice/build-slice have
    full mini-CAD). PCA-1's own audit checks only the in-repo copies.
    """
    in_repo = REPO_ROOT / "skills" / skill / "SKILL.md"
    installed = Path.home() / ".claude" / "skills" / skill / "SKILL.md"

    assert in_repo.exists(), f"in-repo file missing: {in_repo}"
    assert installed.exists(), (
        f"installed file missing: {installed} — has the AI SDLC plugin been "
        f"installed? `{skill}` is enumerated in install_audit `_CANONICAL_SKILLS`"
    )

    in_repo_sec = _extract_section(in_repo.read_text(encoding="utf-8"))
    installed_sec = _extract_section(installed.read_text(encoding="utf-8"))

    assert in_repo_sec is not None, (
        f"in-repo skills/{skill}/SKILL.md has no `## Pipeline position` "
        f"section (PCA-1 requires it on all 8 covered skills)"
    )
    assert installed_sec is not None, (
        f"installed skills/{skill}/SKILL.md has no `## Pipeline position` "
        f"section — forward-sync after in-repo edit was forgotten"
    )
    assert in_repo_sec == installed_sec, (
        f"`## Pipeline position` DRIFT for skill {skill!r}:\n"
        f"  in-repo   ({in_repo})\n"
        f"  installed ({installed})\n"
        f"Forward-sync the edited SKILL.md to ~/.claude/skills/{skill}/."
    )
