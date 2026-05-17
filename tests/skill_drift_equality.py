"""Shared EOL-agnostic forward-sync drift comparator (RULE-ID EOL-DRIFT-1).

Per ADR-033 (slice-033) + methodology-changelog v0.47.0: the skill-drift /
mini-CAD family of guards asserts an in-repo `.md` is forward-synced to its
installed `~/.claude/...` copy — the property that guarantees Claude reads
current (not stale) prose at skill/agent runtime. The defect class is *stale
runtime prose* (a forgotten forward-sync after an in-repo content edit);
CRLF<->LF is semantically invisible to that class. A raw-byte compare is
therefore stricter than the invariant requires and, on Windows
`core.autocrlf=true`, produces only false positives (R-5, N+2 at
slices 030A/031/032).

This module is the single source of truth for that comparison: content
normalized CRLF->LF before hashing, so a CRLF working tree vs an LF installed
copy with identical content is CLEAN, while genuine (non-EOL) content
divergence still FAILs (the must-not-mask-real-drift safety property —
exercised by tests/methodology/test_skill_drift_normalization.py).

Helper-location rationale (ADR-033 M4): the consumer set spans two sibling
test subpackages (`tests/skills/diagnose/` + `tests/methodology/`); neither
subpackage's `conftest.py` is the natural home (a conftest is
pytest-fixture-scoped, not a general cross-subpackage import surface). A
neutral top-level module is the correct structural choice; `pytest.ini`
(`python_files = test_*.py`) does not collect this non-`test_`-prefixed
module as a test.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

_INSTALL_HINT = (
    "has the AI SDLC plugin been installed via INSTALL.md Step 3? The "
    "installed copy is expected to be a forward-synced copy of the in-repo "
    "source (see tools/install_audit.py canonical lists)."
)


def _normalized_sha256(path: Path) -> str:
    """sha256 of the file's content with CRLF normalized to LF.

    Normalizing before hashing is what makes the comparison EOL-agnostic
    (EOL-DRIFT-1). It does NOT weaken genuine-divergence detection: any
    non-line-ending content difference still changes the digest.
    """
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def assert_md_forward_synced(
    in_repo: Path, installed: Path, *, label: str
) -> None:
    """Assert in-repo `.md` is forward-synced to its installed copy,
    comparing content **modulo line endings** (EOL-DRIFT-1 / ADR-033).

    Raises AssertionError on: (a) in-repo file missing, (b) installed file
    missing (with the INSTALL.md hint), (c) genuine content divergence after
    CRLF->LF normalization (message names both paths + both normalized
    hashes + the label + the forward-sync fix hint). Returns None on an
    EOL-only difference or exact match — the R-5 false-FAIL class, now
    suppressed by design.

    `label` identifies the guarded file in failure output (e.g.
    "skills/diagnose/SKILL.md") so a real future drift is still actionable.
    """
    assert in_repo.exists(), f"in-repo {label} missing at {in_repo}"
    assert installed.exists(), (
        f"installed {label} missing at {installed} -- {_INSTALL_HINT}"
    )

    in_repo_hash = _normalized_sha256(in_repo)
    installed_hash = _normalized_sha256(installed)
    assert in_repo_hash == installed_hash, (
        f"{label} DRIFT (EOL-normalized content differs — this is a genuine "
        f"forward-sync miss, NOT a CRLF/LF artifact):\n"
        f"  in-repo   ({in_repo}): normalized sha256={in_repo_hash}\n"
        f"  installed ({installed}): normalized sha256={installed_hash}\n"
        f"Forward-sync after the latest in-repo edit was forgotten. /"
        f"{label} runtime would read stale prose. Fix: copy the in-repo file "
        f"over the installed copy."
    )
