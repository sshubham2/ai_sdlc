"""SVW-1 skill-path concurrency proof (slice-095 / [[ADR-087]]; AC3).

Proves the REAL skill path — N concurrent ``$PY -m tools.vault_edit append``
SUBPROCESSES to one shared vault file — loses ZERO lines and never tears the
file. This is the non-redundant end-to-end layer: slice-093 already proved
``safe_append_text`` at the FUNCTION level (``test_vault_safe_write.py``); this
proves it through the CLI subprocess boundary Claude actually invokes.

Non-vacuity (mutation): a naive read-modify-write append — exactly what a raw
skill ``Write``/``Edit`` does (read whole file, modify in memory, write back) —
loses updates under the same contention. That is the lost-update class the
wrapper's lock + ``O_APPEND`` exists to prevent; its failure here proves the
safe-path assertion is not vacuous.
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tools import _stdout

_stdout.reconfigure_stdout_utf8()

_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_concurrent_cli_appends_lose_zero_lines(tmp_path: Path) -> None:
    """N concurrent `vault_edit append` SUBPROCESSES → all N unique lines survive,
    none torn. The real skill path under contention."""
    vault = tmp_path / "vault"
    vault.mkdir()
    target_rel = "risk-register.md"
    (vault / target_rel).write_text("", encoding="utf-8")
    n = 24
    barrier = threading.Barrier(n)
    env = dict(os.environ, AI_SDLC_VAULT_ROOT=str(vault), PYTHONUTF8="1")

    def append(i: int) -> int:
        content = tmp_path / f"entry-{i:04d}.md"
        content.write_text(f"line-{i:04d}\n", encoding="utf-8")
        barrier.wait()  # maximise contention — all subprocesses fire together
        r = subprocess.run(
            [sys.executable, "-m", "tools.vault_edit", "append",
             "--file", target_rel, "--content-file", str(content)],
            env=env, cwd=str(_REPO_ROOT), capture_output=True, text=True,
        )
        return r.returncode

    with ThreadPoolExecutor(max_workers=n) as ex:
        rcs = list(ex.map(append, range(n)))

    assert all(rc == 0 for rc in rcs), f"a vault_edit subprocess failed: {rcs}"
    lines = [ln for ln in (vault / target_rel).read_text(encoding="utf-8").splitlines() if ln]
    assert sorted(lines) == sorted(f"line-{i:04d}" for i in range(n)), (
        f"lost/duplicated/torn append on the skill path: got {len(lines)} lines, expected {n}"
    )


def test_naive_read_modify_write_loses_updates(tmp_path: Path) -> None:
    """MUTATION / non-vacuity: a naive read-modify-write append (what a raw skill
    `Write`/`Edit` does — read whole file, append in memory, write back) under
    the SAME contention loses updates. This is the lost-update class the safe
    channel prevents; its failure here proves the safe-path test is not vacuous
    (cross-platform — RMW lost-update is not Windows-specific)."""
    target = tmp_path / "raw-log.md"
    target.write_text("", encoding="utf-8")
    n = 24
    barrier = threading.Barrier(n)

    def naive_append(i: int) -> None:
        line = f"line-{i:04d}\n"
        barrier.wait()
        cur = target.read_text(encoding="utf-8")  # READ whole file
        time.sleep(0.002)                          # widen the read-modify-write window
        target.write_text(cur + line, encoding="utf-8")  # WRITE whole file back

    with ThreadPoolExecutor(max_workers=n) as ex:
        list(ex.map(naive_append, range(n)))

    lines = [ln for ln in target.read_text(encoding="utf-8").splitlines() if ln]
    assert len(lines) < n, (
        "naive read-modify-write did NOT lose updates — the mutation is vacuous; "
        "the safe-path assertion would not catch a missing lock"
    )
