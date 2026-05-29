"""PCR-2b (slice-083 / ADR-075) — `--verify-resolution` git-native detection.

APED-1 corpus check for the B2 + M-add-1 /critique fixes: a resolved Markdown
file retaining a setext `=======` heading / `=======` divider must verify CLEAN
(the substring + `git diff --cached --check` scans both false-STOP here); a real
unresolved `<<<<<<<`/`>>>>>>>` marker must STOP; an unmerged path must STOP.
"""

import subprocess

from tools.parallel_conflict_resolver import _verify_resolution_clean


def _git(tmp_path, *args, check=True):
    return subprocess.run(
        ["git", *args], cwd=tmp_path, check=check, capture_output=True, text=True
    )


def _init_repo(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "master")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    (tmp_path / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")


def test_verify_resolution_clean_on_resolved_markdown_setext(tmp_path):
    """A staged ADR/markdown resolution that retains a setext H1 underline
    (`Title\\n=======`) and a `=======` divider verifies CLEAN — the M-add-1
    fix keys on `<<<<<<<`/`>>>>>>>` openers, NOT `=======`."""
    _init_repo(tmp_path)
    adr = tmp_path / "architecture" / "decisions" / "ADR-999-x.md"
    adr.parent.mkdir(parents=True, exist_ok=True)
    adr.write_text(
        "ADR Heading\n"
        "=======\n"               # setext H1 underline (7 `=`)
        "\n"
        "## Context\n"
        "A horizontal divider follows:\n"
        "==============================\n"   # 30-`=` divider
        "\n"
        "Decision: keep the merged content.\n",
        encoding="utf-8",
    )
    _git(tmp_path, "add", ".")  # stage the resolution
    clean, reason = _verify_resolution_clean(tmp_path)
    assert clean is True, f"setext markdown false-STOPped: {reason}"
    assert reason is None


def test_verify_resolution_stop_on_real_unresolved_marker(tmp_path):
    """A staged file that still contains a real `<<<<<<<`...`>>>>>>>` marker
    triple STOPs with unresolved-markers-present."""
    _init_repo(tmp_path)
    f = tmp_path / "skills" / "x" / "SKILL.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(
        "intro\n"
        "<<<<<<< HEAD\n"
        "ours\n"
        "=======\n"
        "theirs\n"
        ">>>>>>> branchA\n"
        "tail\n",
        encoding="utf-8",
    )
    _git(tmp_path, "add", ".")
    clean, reason = _verify_resolution_clean(tmp_path)
    assert clean is False
    assert reason == "unresolved-markers-present"


def test_verify_resolution_stop_on_unmerged_path(tmp_path):
    """A rebase-in-progress with an unmerged (U) path STOPs with
    paths-still-unmerged BEFORE the marker scan."""
    _init_repo(tmp_path)
    target = tmp_path / "tools" / "foo.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("base = 0\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "base")
    _git(tmp_path, "checkout", "-q", "-b", "branchA")
    target.write_text("a = 1\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "A")
    _git(tmp_path, "checkout", "-q", "master")
    target.write_text("b = 2\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "B")
    _git(tmp_path, "checkout", "-q", "branchA")
    _git(tmp_path, "rebase", "master", check=False)  # conflict -> U path
    clean, reason = _verify_resolution_clean(tmp_path)
    assert clean is False
    assert reason is not None and reason.startswith("paths-still-unmerged")


def test_verify_resolution_stop_on_diff3_base_marker_leftover(tmp_path):
    """Per /code-review M2: a `merge.conflictStyle=diff3`/`zdiff3` user who
    removes the `<<<<<<<`/`>>>>>>>` lines but leaves the `|||||||` base-section
    separator staged must STOP — the base block is still an unresolved marker."""
    _init_repo(tmp_path)
    f = tmp_path / "tools" / "x.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    # Only the diff3 base separator remains (openers/closers already deleted).
    f.write_text("a = 1\n|||||||\nb = 2\nc = 3\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    clean, reason = _verify_resolution_clean(tmp_path)
    assert clean is False
    assert reason == "unresolved-markers-present"


def test_verify_resolution_clean_on_committed_marker_context_line(tmp_path):
    """Per /code-review m3: detection is keyed on the STAGED diff
    (`git diff --cached`), so a `<<<<<<<`-starting line that is ALREADY committed
    (unchanged vs HEAD, hence a context/absent line — never an added `+` line)
    is NOT flagged. This pins the staged-vs-HEAD keying decision so a future
    refactor to a whole-file grep is caught as an intentional contract change."""
    _init_repo(tmp_path)
    # Commit a file that legitimately contains a 7-`<` line (e.g. a doc example).
    doc = tmp_path / "docs" / "example.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("Example of a conflict marker:\n<<<<<<< HEAD\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "committed marker in doc")
    # Stage an UNRELATED change (so the cached diff is non-empty but marker-free).
    (tmp_path / "tools" / "y.py").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "tools" / "y.py").write_text("resolved = True\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    clean, reason = _verify_resolution_clean(tmp_path)
    assert clean is True, f"committed (unchanged) marker line false-STOPped: {reason}"
    assert reason is None
