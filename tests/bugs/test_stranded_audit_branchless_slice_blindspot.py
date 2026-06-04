"""Bug repro (R-31): stranded_slice_audit is blind to BRANCHLESS in-flight slices.

Bug (slice-092 candidate `fix-stranded-audit-branchless-blindspot`):
    `tools/stranded_slice_audit.classify_branches` enumerates ONLY
    (a) branches with a live worktree (`detect_active_worktrees`) and
    (b) bare `slice/NNN-<name>` branches (`for-each-ref refs/heads/slice/`).
    A slice that has been `/slice`+`/design`'d but NOT yet branched — the normal
    pre-`/build-slice` state, where the scaffold (`mission-brief.md` +
    `milestone.md`, stage pre-`build`) lives UNTRACKED in the main working tree
    with NO matching `slice/NNN-*` ref — is structurally invisible. The detector
    returns no entry for it and `compute_status` reports `clean`.

Real incident (R-31, discovered slice-090): at slice-090's `/slice` prereq the
    stranded consult returned `status: clean` while an in-flight slice-089
    (stage=design) sat uncommitted in the main tree. Re-confirmed at slice-091/092
    definition: slice-091 sits as an untracked `architecture/slices/slice-091-*/`
    folder with no `slice/091` branch, and `stranded_slice_audit --json` returns
    `{"status": "clean", "entries": []}` — a false all-clear for the branchless case.

Expected (post-fix): an untracked/uncommitted `architecture/slices/slice-NNN-*/`
    folder whose milestone stage is pre-`build` and which has no `slice/NNN-*`
    branch is surfaced as an INFORMATIONAL "branchless in-flight slice" entry
    (NOT a halt — same parallel-safety discipline as ADR-079; the cooperative
    model, NOT a security boundary). `compute_status` stays `clean`.
Actual (pre-fix): no entry is produced; `classify_branches` returns `[]`.

This test asserts the BEHAVIORAL contract (an entry naming the branchless slice
must surface, informational, status clean) WITHOUT pinning the exact new
DivergenceClass value or field — `/design-slice` for slice-092 finalizes that.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py
import tools._vault_git as _vgit
import tools.pulse_worktree_resolver as _pwr
import tools.stranded_slice_audit as _ssa

# slice-110 / [[ADR-101]]: location-agnostic VAULT_ROOT pin — detector +
# _vault_git (vault_is_external) + pulse_worktree_resolver (classify_worktree_state).
_pin_vault = vi.autouse_pin(_vgit, _pwr, _ssa)

from tools.stranded_slice_audit import classify_branches, compute_status


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )


def _init_repo(repo_root: Path) -> None:
    """Init a git repo at `repo_root` on master with one commit + an identity."""
    repo_root.mkdir(parents=True, exist_ok=True)
    _git("init", "-b", "master", str(repo_root), cwd=repo_root.parent)
    _git("config", "user.name", "test", cwd=repo_root)
    _git("config", "user.email", "test@example.com", cwd=repo_root)
    _git("config", "init.defaultBranch", "master", cwd=repo_root)
    (repo_root / "README.md").write_text("init\n", encoding="utf-8")
    _git("add", "README.md", cwd=repo_root)
    _git("commit", "-m", "initial", cwd=repo_root)


def _milestone(slice_id: str, stage: str, next_action: str) -> str:
    return (
        f"---\nslice: {slice_id}\nstage: {stage}\n"
        f"next-action: {next_action}\nrisk-tier: medium\ncritic-required: true\n---\n\n"
        f"# Milestone: {slice_id}\n"
    )


def _entry_mentions(entry, needle: str) -> bool:
    """True if `needle` appears in any stringy field of a StrandedEntry."""
    for val in (
        entry.branch,
        entry.worktree_path,
        entry.vault_state,
        entry.reason,
    ):
        if val and needle in str(val):
            return True
    return False


def test_branchless_in_flight_slice_is_surfaced_informationally(tmp_path: Path):
    """R-31: a `/slice`+`/design`'d-but-not-branched slice (untracked scaffold in
    the main tree, NO `slice/NNN` ref, milestone stage pre-`build`) MUST be
    surfaced as an informational entry — not silently reported `clean`/empty.

    Pre-fix: `classify_branches` returns `[]` (no worktree, no `slice/*` ref) →
    this test FAILS (no entry names the branchless slice). Post-fix: an
    informational, non-halting entry naming `slice-220-branchless` is produced
    and `compute_status` stays `clean`.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)

    # The branchless in-flight slice: scaffold written into the MAIN working tree,
    # UNTRACKED (never `git add`ed), with NO `slice/220-*` branch created.
    slice_dir = repo / "architecture" / "slices" / "slice-220-branchless"
    slice_dir.mkdir(parents=True, exist_ok=True)
    (slice_dir / "milestone.md").write_text(
        _milestone("slice-220-branchless", "design", "run /critique"),
        encoding="utf-8",
    )
    (slice_dir / "mission-brief.md").write_text(
        "# Slice 220: branchless\n", encoding="utf-8"
    )

    # Sanity: there is genuinely no slice/* branch for it.
    branches = _git("branch", "--list", "slice/220-*", cwd=repo).stdout.strip()
    assert branches == "", f"fixture invalid: an unexpected slice branch exists: {branches!r}"

    entries = classify_branches(repo)

    surfaced = [e for e in entries if _entry_mentions(e, "slice-220-branchless")]
    assert surfaced, (
        "branchless in-flight slice was NOT surfaced — the R-31 blindspot. "
        f"classify_branches returned {entries!r} (no entry names slice-220-branchless). "
        "A `/slice`+`/design`'d folder with no slice/* branch must be reported as an "
        "informational entry, not a silent clean."
    )

    e = surfaced[0]
    assert e.halt is False, (
        "a branchless in-flight slice is a HEALTHY parallel-safe state (ADR-079 "
        f"cooperative model) and must be informational, not a halt; got halt={e.halt!r} "
        f"klass={e.klass!r} reason={e.reason!r}"
    )
    assert compute_status(entries) == "clean", (
        "surfacing a branchless in-flight slice must NOT make /slice divergent — "
        f"it is informational only; entries={entries!r}"
    )
