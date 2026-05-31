"""Repro: tools/parallel_conflict_resolver.py crashes on Windows (cp1252)
because its git subprocess calls decode git output with the host's locale
preferred encoding instead of UTF-8.

Bug (slice-090 candidate; user-reported during a SOFT slice-queue.md
conflict, post-slice-088):

    Every git ``subprocess.run(...)`` in tools/parallel_conflict_resolver.py
    is invoked with ``text=True`` and NO ``encoding=`` argument. In text
    mode with no explicit encoding, CPython decodes the child's stdout pipe
    using ``locale.getpreferredencoding(False)`` -- which on Windows is
    ``cp1252``. When git output contains a UTF-8 byte that is *undefined* in
    cp1252 (0x81 / 0x8D / 0x8F / 0x90 / 0x9D -- e.g. the bytes of an emoji
    like U+1F3C6 = ``F0 9F 8F 86`` or Devanagari U+0901 = ``E0 A4 81``), the
    decode raises ``UnicodeDecodeError``. The raise happens inside
    subprocess's pipe-*reader thread* (``Thread-N (_readerthread)``), so
    ``subprocess.run`` does NOT re-raise it -- it returns ``stdout=None`` /
    truncated, and the helper hands back ``None``/garbage to a resolver that
    then mis-resolves the conflict or crashes downstream.

    NOTE: em-dash / arrow / ellipsis (the chars that *saturate* the vault)
    decode to mojibake under cp1252 but do NOT raise. The crash requires a
    byte in the cp1252-undefined set. The user hit it on real git output
    (a conflicted file / commit / diff containing such a char).

The exact buggy line on the user's path: ``diagnose_conflict`` (L185) reads
``_git_show_stage(repo_root, 2, "architecture/slice-queue.md")`` (L204-205);
``_git_show_stage`` (L713-722) is the ``subprocess.run(..., text=True)`` git
call with no ``encoding=``.

Expected post-fix behavior: every git subprocess call passes
``encoding="utf-8"`` so git's UTF-8 output round-trips losslessly on any
host locale -- ``_git_show_stage`` returns the exact decoded content and
``diagnose_conflict`` completes without raising.

Skip-guard: the bug can only manifest when the host's preferred encoding
cannot decode UTF-8 bytes (Windows cp1252, some legacy POSIX locales). On a
UTF-8 host the bug is genuinely absent, so the behavioral repro is skipped
there (skip != pass -- it does not mask a regression on the platform where
it matters). This repo's shippability catalog runs on the dev's Windows
(cp1252) machine, where this test executes for real.
"""
from __future__ import annotations

import locale
import subprocess

import pytest

from tools.parallel_conflict_resolver import diagnose_conflict, _git_show_stage


# A character whose UTF-8 encoding contains a cp1252-UNDEFINED byte (0x8F),
# so decoding its UTF-8 bytes as cp1252 raises UnicodeDecodeError. U+1F3C6
# ("trophy") is realistic -- this pipeline literally emits it in /slice
# output and it can land in commit messages / docs / conflicted content.
_CRASHER = "\U0001F3C6"  # bytes F0 9F 8F 86 -> 0x8F undefined in cp1252

_QUEUE_REL = "architecture/slice-queue.md"


def _claimed_queue(claimer: str) -> str:
    """A valid PSQ-1/PSQ-2 slice-queue.md with one CLAIMED candidate whose
    title carries the cp1252-crasher byte. The ``Claimed-by`` / ``Claimed-at``
    lines are clean ASCII so parse_queue_text extracts the claim *iff* the
    stage text was decoded losslessly (i.e. only post-fix)."""
    return (
        "# Slice queue\n\n## Candidates\n\n"
        f"### cand-shared {_CRASHER}\n\n"
        "- **Source:** risk-register R-99\n"
        "- **Blast-radius:** `tools/foo.py`\n"
        "- **Parallel-safety:** NON-OVERLAPPING\n"
        "- **Effort:** SMALL\n"
        "- **Risk-retired:** LOW\n"
        f"- **Claimed-by:** {claimer}\n"
        "- **Claimed-at:** 2026-05-31T10:00:00+00:00\n"
    )


# Stage-2 (ours / rebased-onto-base) and stage-3 (theirs / replayed-commit)
# content, each carrying the crasher byte so BOTH _git_show_stage calls in
# diagnose_conflict (L204-205) are exercised, and each carrying a valid claim.
_OURS = _claimed_queue("Alice alice@example.com")
_THEIRS = _claimed_queue("Bob bob@example.com")


def _host_decodes_utf8_natively() -> bool:
    """True when the host's locale preferred encoding can decode the
    crasher's UTF-8 bytes -- i.e. the bug cannot manifest on this host."""
    preferred = locale.getpreferredencoding(False)
    try:
        _CRASHER.encode("utf-8").decode(preferred)
        return True
    except (UnicodeDecodeError, LookupError):
        return False


pytestmark = pytest.mark.skipif(
    _host_decodes_utf8_natively(),
    reason=(
        "cp1252-decode bug only manifests when locale.getpreferredencoding "
        f"({locale.getpreferredencoding(False)!r}) cannot decode UTF-8 bytes "
        "(e.g. Windows cp1252); this host decodes them natively so the bug "
        "is genuinely absent here"
    ),
)


def _git(tmp_path, *args, check=True):
    return subprocess.run(
        ["git", *args], cwd=tmp_path, check=check, capture_output=True, text=True
    )


def _stage_rebase_conflict(tmp_path, rel_path, *, ours, theirs):
    """Build an in-progress rebase conflict on ``rel_path`` so git's
    conflict stages 2 (ours/master) and 3 (theirs/branchA) are populated.

    Mirrors the proven fixture in
    tests/methodology/test_parallel_conflict_resolution_log_hard.py.
    """
    _git(tmp_path, "init", "-q", "-b", "master")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    target = tmp_path / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# base\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")
    _git(tmp_path, "checkout", "-q", "-b", "branchA")
    target.write_text(theirs, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "A")
    _git(tmp_path, "checkout", "-q", "master")
    target.write_text(ours, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "B")
    # Rebase branchA onto master -> conflict; stage 2 = master (ours),
    # stage 3 = branchA (theirs).
    _git(tmp_path, "checkout", "-q", "branchA")
    _git(tmp_path, "rebase", "master", check=False)


def test_git_show_stage_decodes_utf8_content_on_cp1252_host(tmp_path):
    """The precise buggy line: ``_git_show_stage`` must return git's UTF-8
    output decoded losslessly, even when the host locale is cp1252.

    Pre-fix (cp1252 host): ``subprocess.run(..., text=True)`` decodes the
    stage content as cp1252; the crasher byte (0x8F) raises
    ``UnicodeDecodeError`` in the pipe-reader thread; ``subprocess.run``
    returns ``stdout=None``; ``_git_show_stage``'s ``return proc.stdout``
    (the success path — NOT the ``except`` branch's ``""``) hands back that
    ``None``. The assertion below fails (``None != _OURS``).

    Post-fix: the call passes ``encoding="utf-8"`` and the exact content
    round-trips.
    """
    _stage_rebase_conflict(tmp_path, _QUEUE_REL, ours=_OURS, theirs=_THEIRS)

    stage_2 = _git_show_stage(tmp_path, 2, _QUEUE_REL)
    stage_3 = _git_show_stage(tmp_path, 3, _QUEUE_REL)

    assert stage_2 == _OURS, (
        "stage-2 git content did not round-trip as UTF-8 -- cp1252 decode "
        f"corrupted/dropped it (got {stage_2!r}). This is the "
        "text=True-without-encoding bug in _git_show_stage."
    )
    assert stage_3 == _THEIRS, (
        "stage-3 git content did not round-trip as UTF-8 "
        f"(got {stage_3!r})."
    )
    assert _CRASHER in stage_2 and _CRASHER in stage_3, (
        "the cp1252-undefined character was lost during decode"
    )


def test_diagnose_conflict_extracts_claims_from_utf8_slice_queue_on_cp1252_host(tmp_path):
    """End-to-end, the *silent-data-loss* manifestation on the exact
    user-reported path: a SOFT slice-queue.md conflict whose stage content
    contains a cp1252-undefined char must still yield the claim history.

    This is more dangerous than a crash: ``_git_show_stage`` returns ``None``
    on the cp1252 reader-thread failure, and ``_extract_claim_diff`` collapses
    ``None`` to ``{}`` via ``parse_queue_text(text) if text else {}`` (L835/844)
    -- so the claims are *silently dropped*, ``claim_history`` is empty, and
    ``classify_conflict`` can no longer detect a VAULT_CLAIM collision (it would
    auto-resolve a genuine cross-identity claim conflict as SOFT).

    Pre-fix (cp1252 host): both stages decode to ``None`` -> ``claim_history``
    is empty -> this assertion fails.

    Post-fix (``encoding="utf-8"``): both stages decode losslessly -> the
    Alice (stage 2) and Bob (stage 3) claims on ``cand-shared`` are extracted.
    """
    _stage_rebase_conflict(tmp_path, _QUEUE_REL, ours=_OURS, theirs=_THEIRS)

    diag = diagnose_conflict(tmp_path)

    assert _QUEUE_REL in diag.u_files, (
        f"slice-queue.md missing from u_files (u_files={diag.u_files!r})"
    )
    assert diag.claim_history, (
        "claim_history is empty -- the cp1252 decode failure silently dropped "
        "the claims that exist in both stages' slice-queue.md content "
        "(the dangerous silent-VAULT_CLAIM-bypass manifestation)"
    )
    claimers = {c.claimed_by for c in diag.claim_history}
    assert {"Alice alice@example.com", "Bob bob@example.com"} <= claimers, (
        f"expected both stage claims to be decoded + extracted; got {claimers!r}"
    )
