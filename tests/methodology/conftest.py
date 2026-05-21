"""Shared fixtures for methodology self-tests."""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Absolute path to the AI SDLC repo root."""
    return REPO_ROOT


def read_file(relative_path: str) -> str:
    """Read a file relative to repo root as text."""
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _resolve_slice_dir(slice_number: int) -> Path:
    """Resolve a slice-NNN folder, trying active then archive locations.

    Tries ``architecture/slices/slice-{NNN}-*/`` first (active slice
    directory), falls back to ``architecture/slices/archive/slice-{NNN}-*/``
    (archived). Returns the resolved Path on first match. Raises
    AssertionError with both attempted glob patterns in the message if
    neither resolves.

    The helper reads ``REPO_ROOT`` at function-call-time via module-globals
    (Python's natural binding semantics — ``REPO_ROOT.joinpath(...)`` inside
    the function body resolves the name at each call, NOT at def-time). This
    means ``monkeypatch.setattr("tests.methodology.conftest.REPO_ROOT", tmp)``
    DOES affect subsequent calls — exploited by
    ``test_resolves_active_slice_via_tmp_vault`` (AC4b). NO second
    ``repo_root: Path | None = None`` parameter; the public contract is
    single-arg per slice-056 /critique M2 ACCEPTED-FIXED.

    Per R-15 (slice-055-discovered; mitigating after slice-056 ship per
    /critique m2 ACCEPTED-FIXED — part-(a) DONE, part-(b) pending the
    future slice that demonstrably uses this helper to retrofit
    ``test_ptffd1_no_false_positive.py:70``): a slice that authors tests
    pinning invariants on its own vault files breaks at the next /reflect's
    archival because the active path becomes an archive path. Callers
    should use this helper instead of hardcoding
    ``REPO_ROOT / "architecture" / "slices" / "slice-NNN-<name>"`` literals.

    Diagnostic-message format pin (per /critique m4 ACCEPTED-FIXED): glob
    patterns in the AssertionError are formatted as raw forward-slash
    strings via f-string templates, NOT ``str(Path(...))`` (which produces
    backslash-separated text on Windows). The AC4c forward-slash substring
    assertion holds identically on Windows and POSIX.

    Args:
        slice_number: slice number in [0, 999]. Booleans are NOT accepted
            (Python ``isinstance(True, int)`` is True; reject explicitly).

    Returns:
        Path to the resolved slice folder.

    Raises:
        ValueError: ``slice_number`` is not an int in [0, 999], or is a
            bool (booleans-are-int-subtype edge case).
        AssertionError: neither active nor archive glob matched a directory.
            Message names both attempted glob patterns + the padded slice
            number so future failures surface cause not symptom.
    """
    # Reject non-int / bool / out-of-range (slice numbers are 0..999 per BRANCH-1)
    if isinstance(slice_number, bool) or not isinstance(slice_number, int):
        raise ValueError(
            f"slice_number must be a non-negative integer in [0, 999], "
            f"got {slice_number!r}"
        )
    if slice_number < 0 or slice_number > 999:
        raise ValueError(
            f"slice_number must be a non-negative integer in [0, 999], "
            f"got {slice_number!r}"
        )

    n_padded = f"{slice_number:03d}"
    active_pattern = f"architecture/slices/slice-{n_padded}-*"
    archive_pattern = f"architecture/slices/archive/slice-{n_padded}-*"

    # Active glob first (per R-15 mitigation: try the active path BEFORE the
    # archive path so an in-flight slice resolves correctly during its own
    # /build-slice + /validate-slice phases).
    active_matches = [
        p for p in REPO_ROOT.joinpath("architecture", "slices").glob(
            f"slice-{n_padded}-*"
        )
        if p.is_dir()
    ]
    if active_matches:
        return active_matches[0]

    # Archive glob fallback (for any slice that has shipped through /reflect).
    archive_matches = [
        p for p in REPO_ROOT.joinpath("architecture", "slices", "archive").glob(
            f"slice-{n_padded}-*"
        )
        if p.is_dir()
    ]
    if archive_matches:
        return archive_matches[0]

    raise AssertionError(
        f"neither active nor archive resolution succeeded for slice-{n_padded}; "
        f"tried {active_pattern}, {archive_pattern}"
    )
