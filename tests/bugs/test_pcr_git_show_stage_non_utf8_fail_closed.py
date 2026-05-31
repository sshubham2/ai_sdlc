"""Repro: tools/parallel_conflict_resolver._git_show_stage does NOT fail
closed when a conflict stage holds genuinely non-UTF-8 bytes.

Bug (R-30 residual #1, slice-090 reflection "Discovered" / "Deferred"):

    slice-090 added ``encoding="utf-8"`` to every decoding git
    ``subprocess.run`` in tools/parallel_conflict_resolver.py, closing the
    *host-locale* (cp1252) decode crash. But a residual remains: when the
    staged blob is GENUINELY non-UTF-8 (invalid bytes — not a host-locale
    artifact), the strict UTF-8 decode still fails, and ``_git_show_stage``
    handles it the WRONG way:

      * On Windows the decode raises inside subprocess's pipe-*reader thread*;
        ``subprocess.run`` swallows it and returns ``proc.stdout = None``;
        ``_git_show_stage``'s ``return proc.stdout`` (the SUCCESS path, not the
        ``except`` branch) hands back ``None`` (empirically verified on the dev
        host — see below).
      * On POSIX the decode error propagates out of ``subprocess.run`` as an
        UNCAUGHT ``UnicodeDecodeError`` — ``_git_show_stage`` only catches
        ``CalledProcessError`` / ``FileNotFoundError``, so it crashes.

    Either way the result is NOT a controlled fail-closed STOP. The silent
    ``None`` (or empty ``""``) is the dangerous one: the caller guards with
    ``parse_queue_text(text) if text else {}`` (see _extract_claim_diff /
    _git_show_stage docstring), so a falsy return DROPS the candidate's
    claim — re-admitting the exact VAULT_CLAIM silent-bypass that the whole
    082–090 hardening arc closed for the decodable case.

Unlike the cp1252 repro (tests/bugs/test_pcr_git_subprocess_cp1252_decode.py),
this one is host-locale-INDEPENDENT: the bytes are invalid UTF-8, so the
strict ``encoding="utf-8"`` decode fails on ANY platform. No skip guard.

Staging note (slice-091 /critique B1, VALIDATED): a single conflict stage
CANNOT be staged via ``git update-index --index-info`` on the dev's Windows
``git.exe`` — it prints ``Ignoring path …`` and stages nothing, so
``git show :2:<path>`` returns exit 128 ("absent") and the decode line is
never reached (the test would then exercise the *absent*-stage sentinel, not
the decode path). We therefore build a REAL rebase conflict (mirroring the
proven ``_stage_rebase`` pattern in
tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py),
committing the non-UTF-8 bytes on ``master`` so they land in **stage 2**
(``git rebase master`` while on branchA → stage 2 = master/ours, stage 3 =
branchA/theirs). Empirically confirmed: the rebase conflicts (``UU``),
``git show :2:`` returns exit 0 with the invalid bytes, and ``_git_show_stage``
returns ``None`` pre-fix.

Expected post-fix behavior: a PRESENT but non-UTF-8 stage produces a LOUD
fail-closed outcome — either a typed (non-``UnicodeDecodeError``) resolver
STOP, or losslessly-recovered content — never a falsy silent claim-drop and
never an uncaught ``UnicodeDecodeError``.
"""
from __future__ import annotations

import subprocess

import pytest

from tools.parallel_conflict_resolver import _git_show_stage


_QUEUE_REL = "architecture/slice-queue.md"

# Genuinely invalid UTF-8: 0xFF and a lone 0x80 continuation byte are never
# valid UTF-8 lead/continuation bytes, and 0xC3 0x28 is an invalid 2-byte
# sequence. Decoding these with strict UTF-8 raises on every platform. Committed
# on master so they land in conflict stage 2.
_NON_UTF8_MASTER = (
    b"### cand-evil \xff\xfe\x80 \xc3\x28 broken\n"
    b"- **Claimed-by:** Bob bob@example.com\n"
    b"- **Claimed-at:** 2026-05-31T10:00:00+00:00\n"
)

# A conflicting, decodable UTF-8 change to the SAME file on branchA, so the
# rebase genuinely conflicts (and stage 3 holds decodable content — a control).
_UTF8_BRANCHA = (
    "### cand-other\n"
    "- **Claimed-by:** Alice alice@example.com\n"
    "- **Claimed-at:** 2026-05-31T09:00:00+00:00\n"
)


def _git(tmp_path, *args, check=True):
    return subprocess.run(
        ["git", *args], cwd=tmp_path, check=check,
        capture_output=True, text=True, encoding="utf-8",
    )


def _stage_rebase_non_utf8(tmp_path, rel_path):
    """Build an in-progress rebase conflict on ``rel_path`` whose **stage 2**
    (master / ours) holds genuinely non-UTF-8 bytes.

    Mirrors ``_stage_rebase`` in
    tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py,
    except the master-side write uses ``write_bytes`` (``write_text`` cannot
    emit invalid UTF-8).
    """
    target = tmp_path / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    _git(tmp_path, "init", "-q", "-b", "master")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    target.write_text("# stub\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")
    _git(tmp_path, "checkout", "-q", "-b", "branchA")
    target.write_text(_UTF8_BRANCHA, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "A")
    _git(tmp_path, "checkout", "-q", "master")
    target.write_bytes(_NON_UTF8_MASTER)
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "B")
    # Rebase branchA onto master -> conflict; stage 2 = master (non-UTF-8),
    # stage 3 = branchA (decodable control).
    _git(tmp_path, "checkout", "-q", "branchA")
    _git(tmp_path, "rebase", "master", check=False)


def test_git_show_stage_fails_closed_on_non_utf8_stage(tmp_path):
    """A present-but-non-UTF-8 conflict stage must not silently drop to a
    falsy claim-drop, and must not let a raw ``UnicodeDecodeError`` escape.

    Pre-fix:
      * Windows — ``_git_show_stage`` returns a falsy value (empirically
        ``None`` on the dev host via the swallowed reader thread) -> the
        assertion below fails.
      * POSIX   — ``_git_show_stage`` raises an uncaught ``UnicodeDecodeError``
        -> ``pytest.fail`` below fires.

    Post-fix (either is acceptable): a typed resolver STOP exception (NOT a
    ``UnicodeDecodeError``), or losslessly-recovered truthy content.
    """
    _stage_rebase_non_utf8(tmp_path, _QUEUE_REL)

    # Guard: confirm the fixture actually populated stage 2 with the invalid
    # bytes (exit 0), so a future git-behaviour change cannot silently turn this
    # into an absent-stage test (the B1 failure mode).
    raw = subprocess.run(
        ["git", "show", f":2:{_QUEUE_REL}"], cwd=tmp_path, capture_output=True,
    )
    assert raw.returncode == 0 and b"\xff" in raw.stdout, (
        "fixture did not populate conflict stage 2 with the non-UTF-8 bytes "
        f"(rc={raw.returncode!r}); the rebase conflict failed to materialise — "
        "this test would otherwise vacuously exercise the absent-stage path."
    )

    try:
        result = _git_show_stage(tmp_path, 2, _QUEUE_REL)
    except UnicodeDecodeError as exc:
        pytest.fail(
            "_git_show_stage let a raw UnicodeDecodeError escape (uncaught "
            "crash, not a controlled fail-closed STOP) on a non-UTF-8 stage: "
            f"{exc!r}"
        )
    except Exception:  # noqa: BLE001 — a typed, non-decode STOP is acceptable.
        # The fix may convert the decode failure into a resolver STOP. Any
        # exception that is NOT a UnicodeDecodeError satisfies "loud
        # fail-closed", so this is a PASS.
        return

    # Success path: must not be the silent claim-drop. The caller guards with
    # ``parse_queue_text(text) if text else {}`` — so ANY falsy value (None
    # OR "") silently drops the claim. A present stage must not collapse to it.
    assert result, (
        "_git_show_stage returned a falsy value (None or '') for a PRESENT "
        "but non-UTF-8 stage -> the caller's `parse_queue_text(text) if text "
        "else {}` guard drops the claim -> the VAULT_CLAIM silent-bypass "
        "re-opens (R-30 residual #1). Expected a loud fail-closed STOP "
        "(typed exception) or losslessly-recovered content, never a silent "
        f"falsy drop. Got: {result!r}"
    )
