"""EOL-DRIFT-1 (slice-033 / ADR-033) regression tests for the shared
forward-sync drift comparator + the guarded-surface working-tree state.

Three guarantees:
  (a) CRLF vs LF with identical normalized content is treated as EQUAL
      (the R-5 false-FAIL class is suppressed).
  (b) Genuine (non-line-ending) content divergence STILL FAILs — the
      must-not-mask-real-drift safety property the CAD-1/mini-CAD guards
      exist to protect.
  (c) Every guarded in-repo `.md` (the `.gitattributes eol=lf` surface)
      contains zero CRLF bytes in the working tree — a working-tree-STATE
      assertion (not merely `git check-attr`), the M1 fix for AC3.

Rule reference: EOL-DRIFT-1 (slice-033; ADR-033). (a)/(b) are AC2(a);
(c) is AC3.
"""
from __future__ import annotations

import pytest

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced

# The exact surface declared `text eol=lf` in the repo-root .gitattributes
# (ADR-033). Globs are resolved from REPO_ROOT; each matched in-repo file
# must be LF in the working tree post `git add --renormalize`.
_GUARDED_GLOBS = (
    "skills/**/SKILL.md",
    "skills/diagnose/passes/*.md",
    "agents/*.md",
)


def test_normalized_compare_treats_crlf_and_lf_identical_content_as_equal(
    tmp_path,
):
    """A CRLF working-tree file and an LF installed file with identical
    content (post-normalization) is CLEAN — the R-5 false-FAIL is gone.

    Defect class: Windows core.autocrlf=true checks out CRLF while the
    installed copy is LF; a raw-byte compare false-FAILs (R-5 N+2). The
    EOL-normalized comparator must treat this as equal.
    """
    content = "# Skill prose\n\nLine one.\nLine two.\n"
    in_repo = tmp_path / "in_repo.md"
    installed = tmp_path / "installed.md"
    in_repo.write_bytes(content.replace("\n", "\r\n").encode("utf-8"))  # CRLF
    installed.write_bytes(content.encode("utf-8"))  # LF

    # Must NOT raise — EOL-only difference is not drift (EOL-DRIFT-1).
    assert_md_forward_synced(in_repo, installed, label="fixture/eol_only.md")


def test_normalized_compare_still_fails_on_genuine_content_divergence(
    tmp_path,
):
    """Genuine (non-line-ending) content divergence STILL FAILs — the
    must-not-mask-real-drift property (AC2). If this passes, normalization
    has masked the very defect class the guards exist to catch.
    """
    in_repo = tmp_path / "in_repo.md"
    installed = tmp_path / "installed.md"
    # Identical line endings (LF) on both sides; only the *content* differs,
    # so this is unambiguously genuine drift, not an EOL artifact.
    in_repo.write_bytes(b"# Skill prose v1\n\nThe rule says X.\n")
    installed.write_bytes(b"# Skill prose v2\n\nThe rule says Y (stale).\n")

    with pytest.raises(AssertionError, match=r"DRIFT"):
        assert_md_forward_synced(
            in_repo, installed, label="fixture/genuine_drift.md"
        )


def test_guarded_md_files_have_no_crlf_in_working_tree():
    """Every guarded in-repo `.md` (the `.gitattributes eol=lf` surface)
    contains zero CRLF bytes in the working tree (AC3, M1).

    This is a working-tree-STATE check, NOT `git check-attr` (a declaration
    check). `.gitattributes eol=lf` alone does not rewrite already-CRLF
    checked-out files under core.autocrlf=true — the slice's targeted
    `git add --renormalize` is what delivers the LF working tree, and this
    test is its proof.
    """
    offenders: list[str] = []
    matched_any = False
    for glob in _GUARDED_GLOBS:
        for path in sorted(REPO_ROOT.glob(glob)):
            if not path.is_file():
                continue
            matched_any = True
            if b"\r\n" in path.read_bytes():
                offenders.append(str(path.relative_to(REPO_ROOT)))

    assert matched_any, (
        "no guarded .md files matched any of "
        f"{_GUARDED_GLOBS} under {REPO_ROOT} — the glob set is wrong or the "
        "guarded surface moved; AC3 would be vacuously green otherwise"
    )
    assert not offenders, (
        "guarded in-repo .md files still contain CRLF in the working tree "
        f"(AC3 / EOL-DRIFT-1 violated — run `git add --renormalize` per the "
        f"slice .gitattributes scope): {offenders}"
    )
