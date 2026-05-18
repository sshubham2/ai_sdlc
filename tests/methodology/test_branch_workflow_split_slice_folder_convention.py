"""Regression pins for the split-slice folder-naming convention (slice-043 / ADR-046 / R-6).

R-6: `tools/branch_workflow_audit.py`'s strict `_SLICE_FOLDER_RE` (`^slice-(\\d{3})-(.+)$`)
rejects a letter-suffixed split-slice folder (e.g. `slice-030B-...`) with a *generic*
`slice folder name does not match slice-NNN-<name> pattern` message that gives no guidance
toward the (previously implicit) convention. slice-031 paid a mid-build folder+branch+id
rename for this; slice-041 ("030C") was a latent repeat.

ADR-046 option (a): keep the strict accept regex UNCHANGED (numeric-only accept preserved)
and add a diagnostic-only `_SPLIT_SLICE_FOLDER_RE` (uppercase-only, per Critic m1) so the
existing `usage-error` (kind + exit-code 2 unchanged) emits a convention-naming, actionable
message for the letter-suffixed split-slice shape — while a non-split / lowercase malformed
name still gets the generic message verbatim.

These tests are the regression pin (mission-brief AC3): cases (ii)/(iii)/(v) FAIL against the
pre-slice generic-message behavior (genuine contrast) and PASS post-slice; (i)/(iv) guard the
unchanged strict-accept + generic-fallthrough paths so the diagnostic cannot over-reach.

The folder-name `usage-error` is emitted by `audit()` *before* any git plumbing
(`branch_workflow_audit.py` `_slice_branch_name` returns "" on strict-regex miss → the
`if not expected:` early-return at :271-282), so an explicit `repo_root` (no `.git` needed)
is sufficient to exercise it.
"""
from __future__ import annotations

from pathlib import Path

from tools import branch_workflow_audit as bwa
from tests.methodology.conftest import read_file

_GENERIC_STEM = "slice folder name does not match"
# Canonical convention phrases the enriched message must carry (slice-043 / ADR-046).
_CONVENTION_PHRASE = "split-slice follow-up folders are numeric"
_LINEAGE_LABEL_CLAUSE = "prose lineage label only"
_RENAME_REMEDY = "next free numeric slice number"


def _make_folder(tmp_path: Path, name: str) -> Path:
    folder = tmp_path / "architecture" / "slices" / name
    folder.mkdir(parents=True)
    (folder / "mission-brief.md").write_text("# fixture\n", encoding="utf-8")
    return folder


def _folder_name_violation(folder: Path, tmp_path: Path) -> bwa.BranchViolation | None:
    """Return the folder-name-pattern usage-error violation, or None.

    `repo_root=tmp_path` (no `.git`) is passed explicitly so the audit returns the
    folder-name `usage-error` immediately on a strict-regex miss, before git plumbing.
    """
    result = bwa.audit(slice_folder=folder, repo_root=tmp_path)
    for v in result.violations:
        if v.kind == "usage-error" and "slice folder name" in v.message or (
            v.kind == "usage-error" and _CONVENTION_PHRASE in v.message
        ):
            return v
    return None


# --- (i) canonical numeric folder: strict-accept path unchanged (PASSES pre + post) ---


def test_canonical_numeric_folder_not_rejected_by_folder_name_pattern(tmp_path: Path) -> None:
    """A canonical numeric `slice-NNN-<name>` folder must NOT trip the folder-name
    `usage-error` (strict `_SLICE_FOLDER_RE` accept preserved — no convention rejection)."""
    folder = _make_folder(tmp_path, "slice-099-some-feature")
    result = bwa.audit(slice_folder=folder, repo_root=tmp_path)
    folder_name_errors = [
        v for v in result.violations
        if v.kind == "usage-error" and (
            _GENERIC_STEM in v.message or _CONVENTION_PHRASE in v.message
        )
    ]
    assert not folder_name_errors, (
        "Canonical numeric folder must not emit any folder-name-pattern usage-error; "
        f"got: {[v.message for v in folder_name_errors]}"
    )


# --- (ii) letter-suffixed split folder: enriched convention message (FAILS pre-slice) ---


def test_split_slice_letter_suffixed_folder_gets_convention_message(tmp_path: Path) -> None:
    """`slice-030B-...` must be rejected WITH the convention-naming message (not the
    generic one) — kind stays `usage-error`."""
    folder = _make_folder(tmp_path, "slice-030B-complete-shippability-decoupling")
    v = _folder_name_violation(folder, tmp_path)
    assert v is not None, "Expected a folder-name usage-error for slice-030B-..."
    assert v.kind == "usage-error", f"kind must stay usage-error; got {v.kind!r}"
    assert _CONVENTION_PHRASE in v.message, (
        f"split-slice folder message must name the convention "
        f"({_CONVENTION_PHRASE!r}); got: {v.message!r}"
    )
    assert _LINEAGE_LABEL_CLAUSE in v.message, (
        f"message must state the NNNx letter is a prose lineage label only; got: {v.message!r}"
    )
    assert "ADR-046" in v.message and "BRANCH-1" in v.message, (
        f"message must cite ADR-046 / BRANCH-1; got: {v.message!r}"
    )


# --- (iii) the message names the next-free-number remedy (FAILS pre-slice) ---


def test_split_slice_message_names_next_free_number_remedy(tmp_path: Path) -> None:
    folder = _make_folder(tmp_path, "slice-041C-some-followup")
    v = _folder_name_violation(folder, tmp_path)
    assert v is not None
    assert _RENAME_REMEDY in v.message, (
        f"message must name the next-free-numeric-slice-number remedy "
        f"({_RENAME_REMEDY!r}); got: {v.message!r}"
    )


# --- (iv) lowercase non-convention name: generic message, NOT split-specific (m1 guard) ---


def test_lowercase_non_convention_name_falls_through_to_generic_message(tmp_path: Path) -> None:
    """`slice-030misc-x` (lowercase letters — NOT the uppercase `030A/B/C` convention)
    must get the GENERIC message, not the split-slice-specific one (Critic m1 precision)."""
    folder = _make_folder(tmp_path, "slice-030misc-x")
    v = _folder_name_violation(folder, tmp_path)
    assert v is not None, "Expected a folder-name usage-error for slice-030misc-x"
    assert _GENERIC_STEM in v.message, (
        f"lowercase non-convention name must get the generic message; got: {v.message!r}"
    )
    assert _CONVENTION_PHRASE not in v.message, (
        "lowercase non-convention name must NOT get the split-slice-specific message "
        f"(m1 over-match guard); got: {v.message!r}"
    )


# --- (v) CLAUDE.md prose-pin: convention sub-clause on the Branch-per-slice bullet ---


def test_root_claude_md_branch_per_slice_bullet_states_split_slice_convention() -> None:
    """Root CLAUDE.md's Branch-per-slice bullet must carry the explicit split-slice
    folder-naming convention sub-clause (the R-6 root cause was its absence).

    Extends — does not modify — `test_root_claude_md_branch_per_slice_rule.py`'s
    presence-based `Branch-per-slice` substring contract.
    """
    content = read_file("CLAUDE.md")
    assert "Branch-per-slice" in content, "Root CLAUDE.md must retain the Branch-per-slice bullet"
    brownfield_start = content.find("## Brownfield rules")
    assert brownfield_start >= 0, "CLAUDE.md must retain ## Brownfield rules"
    next_section = content.find("\n## ", brownfield_start + 1)
    block = content[brownfield_start:next_section] if next_section > 0 else content[brownfield_start:]
    bullet_idx = block.find("Branch-per-slice")
    bullet = block[bullet_idx:]
    assert "split-slice follow-up" in bullet, (
        "Branch-per-slice bullet must state the split-slice folder-naming convention"
    )
    assert "prose lineage label only" in bullet, (
        "convention sub-clause must state the NNNx letter is a prose lineage label only"
    )
    assert "ADR-046" in bullet, "convention sub-clause must cite ADR-046"
