"""Tests for tools/_vault_write.py — the C2 concurrent-write/append-safety
primitive (slice-093 / ADR-085; R-32 mitigation).

AC2 coverage:
- test_concurrent_writers_no_lost_update     — whole-file atomicity under contention
- test_concurrent_appenders_no_lost_update   — append non-clobbering (the field-recon hazard)
- test_write_retries_on_mocked_eperm         — Windows EPERM-on-held-handle retry (mocked, cross-platform)
- test_inline_and_helper_config_readers_agree — m2 config-reader parity (SSoT)
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from tools import _stdout

_stdout.reconfigure_stdout_utf8()

from tools import _vault_write  # noqa: E402
from tools._vault_write import (  # noqa: E402
    read_vault_root_config,
    safe_append_text,
    safe_write_text,
    write_vault_root_config,
)


# ─── AC2: whole-file concurrent writers — no torn/truncated file ────────


def test_concurrent_writers_no_lost_update(tmp_path: Path) -> None:
    """N threads each write a DISTINCT full payload to the same target via
    safe_write_text. The final file MUST equal exactly one writer's COMPLETE
    payload — never a truncated or interleaved mix (atomic os.replace under the
    sidecar lock)."""
    target = tmp_path / "shared.md"
    n = 12
    payloads = [f"writer-{i}-" + ("x" * 5000) + f"-end-{i}\n" for i in range(n)]
    barrier = threading.Barrier(n)

    def write(i: int) -> None:
        barrier.wait()  # maximise contention
        safe_write_text(target, payloads[i])

    with ThreadPoolExecutor(max_workers=n) as ex:
        list(ex.map(write, range(n)))

    final = target.read_text(encoding="utf-8")
    assert final in payloads, (
        "final content is not any single writer's complete payload — "
        "a torn/interleaved write slipped past the lock + atomic replace"
    )


# ─── AC2: append-only concurrent — no lost append (the field-recon hazard) ──


def test_concurrent_appenders_no_lost_update(tmp_path: Path) -> None:
    """N threads each append a UNIQUE line via safe_append_text. ALL N lines
    MUST survive — a whole-file read-modify-write would lose appends here; the
    O_APPEND + lock path does not (M2 / field-recon.md:28,30)."""
    target = tmp_path / "append-log.md"
    target.write_text("", encoding="utf-8")
    n = 30
    barrier = threading.Barrier(n)

    def append(i: int) -> None:
        barrier.wait()
        safe_append_text(target, f"line-{i:04d}\n")

    with ThreadPoolExecutor(max_workers=n) as ex:
        list(ex.map(append, range(n)))

    lines = [ln for ln in target.read_text(encoding="utf-8").splitlines() if ln]
    assert sorted(lines) == sorted(f"line-{i:04d}" for i in range(n)), (
        f"lost or duplicated append: got {len(lines)} lines, expected {n}"
    )


# ─── AC2: EPERM-on-held-handle retry (mocked — deterministic, cross-platform) ──


def test_write_retries_on_mocked_eperm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The retry loop is exercised by patching os.replace to raise
    PermissionError for the first N attempts, then delegate to the real
    os.replace. A real held-handle EPERMs only on Windows (POSIX rename-over-open
    succeeds) — so the mock is the deterministic cross-platform exercise (M3)."""
    target = tmp_path / "eperm.md"
    real_replace = os.replace
    calls = {"n": 0}

    def flaky_replace(src, dst, *a, **k):
        calls["n"] += 1
        if calls["n"] <= 2:
            raise PermissionError(13, "Access is denied (simulated held handle)")
        return real_replace(src, dst, *a, **k)

    monkeypatch.setattr(os, "replace", flaky_replace)
    safe_write_text(target, "survived the EPERM retries\n")

    assert calls["n"] == 3, "expected 2 EPERM failures then 1 success"
    assert target.read_text(encoding="utf-8") == "survived the EPERM retries\n"


def test_write_raises_after_eperm_budget_exhausted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If os.replace EPERMs past the retry budget, safe_write_text raises a typed
    PermissionError naming the held-handle cause — never silently corrupts."""
    target = tmp_path / "eperm-fatal.md"

    def always_eperm(src, dst, *a, **k):
        raise PermissionError(13, "Access is denied (simulated)")

    monkeypatch.setattr(os, "replace", always_eperm)
    with pytest.raises(PermissionError, match="held by another process"):
        safe_write_text(target, "never lands\n")


# ─── AC2 / m2: config-reader parity (the two-parser SSoT pin) ───────────


def test_inline_and_helper_config_readers_agree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """_vault_paths's inline reader (_read_common_dir_config) and
    _vault_write.read_vault_root_config MUST return the same value for a config
    written into a real git common-dir — they parse the one-line contract from
    the SHARED _CONFIG_REL constant (m2; no divergence)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    common_dir = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        cwd=repo,
        capture_output=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()

    external = str(tmp_path / "external-vault")
    write_vault_root_config(common_dir, external)

    helper_val = read_vault_root_config(common_dir)

    # Inline reader resolves the common-dir itself via git in cwd=repo.
    from tools import _vault_paths

    with monkeypatch.context() as m:
        m.delenv("AI_SDLC_VAULT_ROOT", raising=False)
        m.chdir(repo)
        inline_val = _vault_paths._read_common_dir_config()

    assert helper_val == inline_val == external, (
        f"reader divergence: helper={helper_val!r} inline={inline_val!r} "
        f"expected={external!r}"
    )
