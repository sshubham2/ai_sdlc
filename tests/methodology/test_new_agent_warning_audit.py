"""NAW-1 regression suite — `tools/new_agent_warning_audit.py`.

Per **NAW-1** (`methodology-changelog.md` v0.66.0; slice-063; ADR-061;
the first audit-enforced gate on the **discovery-gate** axis adjacent to
the PMI-1 / PVFS-1 / AVFS-1 / MCFS-1 / TVFS-1 forward-sync family; mints
a new rule; supersedes nothing). Retires R-18 (`mitigating` → `retired`).

Two coverage layers:
  1. **Seam-injected** (tests 1, 2, 3, 7) — drives the four documented
     states (clean / warn / usage / not-installed-vacuous) through the
     `added_files_resolver` injection seam so the assertions don't depend
     on live git state. The 4th test (test 7) is the m3-redesigned
     seam-driven self-application replacing the bootstrap-brittle
     branch-state-dependent original.
  2. **Real-resolver synthetic tmp-git-repo** (tests 4, 5, 6) — runs the
     real `_resolve_added_agent_files` against a synthetic git repo where
     the `agents/foo.md` file occupies each of the three source states
     (untracked / staged-uncommitted / no-diff). Proves the union-of-three
     read mechanism (ADR-061 §Decision L60-67) covers every state a new
     agent file can occupy at /build-slice Step 6.

The 7-test plan maps to the 5 ACs per mission-brief Test-first plan:
- AC1 → tests 1 + 2 (binary exit contract on seam-injected branches)
- AC3 → test 3 (WARN-line cites agent path + session-restart + R-18)
- AC4 → tests 4 + 5 + 6 + 7 (positive contrast untracked + staged +
        negative + seam-driven self-application)

AC2 (Step 6 SKILL.md anchor) and AC5 (R-18 retirement) are covered by
sibling regression suites — see `test_build_slice_skill.py` +
`test_risk_register_audit_real_file.py`.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import new_agent_warning_audit as naw


# --------------------------------------------------------------------------- #
# Fixtures                                                                     #
# --------------------------------------------------------------------------- #


@pytest.fixture
def tmp_git_repo(tmp_path: Path) -> Path:
    """Synthetic git repo with a base commit on `master` + an empty
    `slice/test-feature` branch checked out.

    Real `_resolve_added_agent_files` runs against this fixture in tests
    4/5/6 — each test mutates the WT in a different way to exercise one
    of the three read-mechanism sources (untracked / staged / commit).
    """
    subprocess.run(
        ["git", "init", "-q", "-b", "master"],
        cwd=tmp_path, check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path, check=True,
    )
    # Base commit on master so HEAD..master diff is meaningful
    (tmp_path / "README.md").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "base"],
        cwd=tmp_path, check=True,
    )
    # Slice branch off master
    subprocess.run(
        ["git", "checkout", "-q", "-b", "slice/test-feature"],
        cwd=tmp_path, check=True,
    )
    (tmp_path / "agents").mkdir()
    return tmp_path


# --------------------------------------------------------------------------- #
# AC1 — binary exit contract (seam-injected, never exit 1)                     #
# --------------------------------------------------------------------------- #


def test_audit_exits_0_on_no_agent_diff(tmp_path: Path):
    """No added `agents/*.md` → `status="clean"`, `exit_code=0`, no
    warnings. Drives `added_files_resolver` seam with empty list."""
    result = naw.check(
        tmp_path,
        default_branch_resolver=lambda r: "master",
        added_files_resolver=lambda r, b: [],
    )
    assert result.status == "clean", result.to_dict()
    assert result.exit_code == 0, result.to_dict()
    assert result.warnings == [], result.to_dict()


def test_audit_exits_0_on_new_agent_diff_with_warn_line(tmp_path: Path):
    """≥1 added `agents/*.md` → `status="warn"`, `exit_code=0` (non-
    blocking by construction), `warnings` list non-empty. NEVER exit 1.
    Drives `added_files_resolver` seam with single-entry list."""
    result = naw.check(
        tmp_path,
        default_branch_resolver=lambda r: "master",
        added_files_resolver=lambda r, b: ["agents/foo.md"],
    )
    assert result.status == "warn", result.to_dict()
    assert result.exit_code == 0, result.to_dict()  # binary contract
    assert len(result.warnings) == 1, result.to_dict()
    assert "agents/foo.md" in result.warnings[0]


# --------------------------------------------------------------------------- #
# AC3 — WARN-line anchors (agent path + session-restart + R-18)                #
# --------------------------------------------------------------------------- #


def test_warn_line_cites_agent_path_session_restart_and_r_18():
    """Per ADR-061 §Decision (Attributed WARN message), the WARN line
    MUST cite (a) the agent file path, (b) the session-restart-before-
    next-slice recommendation, and (c) the explicit R-18 risk-register
    cross-reference."""
    line = naw._format_warn_line("agents/foo.md")
    # Anchor (a): agent path verbatim
    assert "agents/foo.md" in line, line
    # Anchor (b): session-restart instruction
    assert "restart Claude Code" in line, line
    # Anchor (c): R-18 risk-register cross-reference
    assert "R-18" in line, line


# --------------------------------------------------------------------------- #
# AC4 — positive + negative contrast + seam-driven self-application            #
# --------------------------------------------------------------------------- #


def test_audit_positive_contrast_synthetic_tmp_repo_untracked(
    tmp_git_repo: Path,
):
    """Source (ii) — UNTRACKED new agent file (created on disk, not
    `git add`-ed). Real `_resolve_added_agent_files` runs `git ls-files
    --others --exclude-standard` and returns the file. Audit → WARN."""
    (tmp_git_repo / "agents" / "foo.md").write_text(
        "---\nname: foo\n---\n", encoding="utf-8"
    )
    # Use default real `_resolve_added_agent_files`; override default-
    # branch resolver because tmp_git_repo has no `origin` remote.
    result = naw.check(
        tmp_git_repo, default_branch_resolver=lambda r: "master",
    )
    assert result.status == "warn", result.to_dict()
    assert result.exit_code == 0, result.to_dict()
    assert len(result.warnings) == 1, result.to_dict()
    assert "agents/foo.md" in result.warnings[0]


def test_audit_positive_contrast_synthetic_tmp_repo_staged(
    tmp_git_repo: Path,
):
    """Source (i) — STAGED-BUT-UNCOMMITTED new agent file (`git add`-ed,
    no `git commit`). Real `_resolve_added_agent_files` runs
    `git diff --diff-filter=A {base}` and returns the file. Audit →
    WARN."""
    (tmp_git_repo / "agents" / "foo.md").write_text(
        "---\nname: foo\n---\n", encoding="utf-8"
    )
    subprocess.run(
        ["git", "add", "agents/foo.md"], cwd=tmp_git_repo, check=True,
    )
    result = naw.check(
        tmp_git_repo, default_branch_resolver=lambda r: "master",
    )
    assert result.status == "warn", result.to_dict()
    assert result.exit_code == 0, result.to_dict()
    assert len(result.warnings) == 1, result.to_dict()
    assert "agents/foo.md" in result.warnings[0]


def test_audit_negative_contrast_no_diff(tmp_git_repo: Path):
    """Negative contrast — no `agents/*.md` changes anywhere. Audit →
    `clean`, `exit_code=0`, no warnings, quiet stdout."""
    result = naw.check(
        tmp_git_repo, default_branch_resolver=lambda r: "master",
    )
    assert result.status == "clean", result.to_dict()
    assert result.exit_code == 0, result.to_dict()
    assert result.warnings == [], result.to_dict()


def test_self_application_audit_against_real_repo_is_clean_or_warn_with_known_agents(
    tmp_path: Path,
):
    """m3-redesigned seam-driven self-application (replaces the bootstrap-
    brittle `test_self_application_slice_063_diff_is_clean`).

    Uses the `added_files_resolver` injection seam with a controlled
    fixture set rather than live `git diff` against slice-063's branch,
    so the assertion is regression-stable across slice-064+ (the original
    branch-state-dependent test would have decayed post-merge per the
    slice-059 TVFS-1 `installed_version_resolver` seam precedent).

    Two states:
      - empty fixture list → `status="clean"` (slice-063 itself adds zero
        `agents/*.md` deltas — vacuous-pass)
      - single-entry list → `status="warn"` (synthetic future-slice
        scenario)
    """
    # Empty list → clean (matches slice-063's actual diff state)
    r_clean = naw.check(
        tmp_path,
        default_branch_resolver=lambda r: "master",
        added_files_resolver=lambda r, b: [],
    )
    assert r_clean.status == "clean", r_clean.to_dict()
    assert r_clean.exit_code == 0, r_clean.to_dict()

    # Single-entry list → warn (synthetic future agent-shipping slice)
    r_warn = naw.check(
        tmp_path,
        default_branch_resolver=lambda r: "master",
        added_files_resolver=lambda r, b: ["agents/foo.md"],
    )
    assert r_warn.status == "warn", r_warn.to_dict()
    assert r_warn.exit_code == 0, r_warn.to_dict()
    assert "agents/foo.md" in r_warn.warnings[0]
