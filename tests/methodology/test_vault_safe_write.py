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
    O_APPEND + lock path does not (M2 / field-recon.md:28,30).

    NOTE (slice-094 m1): this is a basic non-clobbering SMOKE only — THREADS +
    tiny (9-byte) payloads, no lock-stripped mutation arm, so it is in the
    GIL-masked / small-payload regime and CANNOT prove the R-32 append
    lost-update hazard. The AUTHORITATIVE append-concurrency proof is
    `test_vault_write_safety_concurrency.py` (multiprocessing-spawn + mp.Barrier
    + lock-stripped mutation arm — verified non-vacuous)."""
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


# ─── /code-review M1: import-time cp1252-stderr safety on non-ASCII path ──


def test_vault_paths_import_survives_cp1252_stderr_with_non_ascii_path(tmp_path: Path) -> None:
    """M1 regression: importing tools._vault_paths with a non-ASCII
    AI_SDLC_VAULT_ROOT under a cp1252-wrapped sys.stderr must NOT raise
    UnicodeEncodeError — the observability prints fire at import and must be
    encoding-safe (the repo's documented Windows cp1252 footgun)."""
    repo_root = Path(__file__).resolve().parents[2]
    code = (
        "import sys, io\n"
        "sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='cp1252', errors='strict')\n"
        "import importlib, tools._vault_paths as v\n"
        "importlib.reload(v)\n"
        "assert str(v.VAULT_ROOT)\n"  # resolved (non-empty) — the non-ASCII path lives here
        "sys.stdout.write('OK')\n"  # ASCII only: cp1252 stdout must not be the failure source
    )
    env = {**os.environ, "AI_SDLC_VAULT_ROOT": str(tmp_path / "vault-中文-Müller")}
    r = subprocess.run(
        [sys.executable, "-c", code],
        env=env,
        capture_output=True,
        encoding="utf-8",
        cwd=str(repo_root),
    )
    assert r.returncode == 0, (
        f"import crashed under cp1252 stderr + non-ASCII path:\nSTDERR: {r.stderr}"
    )
    assert "OK" in r.stdout


# ─── /code-review m2: safe_append_text EPERM-retry (symmetry with write) ──


def test_append_retries_on_mocked_eperm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """m2: safe_append_text retries os.open on PermissionError (held-handle
    EPERM), symmetric with safe_write_text's os.replace retry."""
    target = tmp_path / "append-eperm.md"
    target.write_text("seed\n", encoding="utf-8")
    real_open = os.open
    calls = {"n": 0}

    def flaky_open(path, flags, *a, **k):
        if str(path) == str(target):  # flake only on the append target, not the sidecar lock
            calls["n"] += 1
            if calls["n"] <= 2:
                raise PermissionError(13, "Access is denied (simulated held handle)")
        return real_open(path, flags, *a, **k)

    monkeypatch.setattr(os, "open", flaky_open)
    safe_append_text(target, "appended\n")

    assert calls["n"] == 3, "expected 2 EPERM failures then 1 success on os.open"
    assert "appended" in target.read_text(encoding="utf-8")


# ─── slice-094 B1 / m-add-1: byte-faithfulness (LF-only, no CRLF) ──────────
# Two-layer per slice-090: nt-skipif behavioral byte-identity + a cross-platform
# structural guard, so the LF-fix is pinned even when the suite runs on POSIX
# (where the CRLF bug cannot manifest).


@pytest.mark.skipif(
    os.name != "nt", reason="CRLF translation is a Windows-only hazard (os.linesep == '\\r\\n')"
)
def test_primitives_are_lf_byte_faithful_on_windows(tmp_path: Path) -> None:
    """B1: both primitives MUST emit LF byte-identical to the canonical
    newline='' writer — NOT CRLF. Pre-fix, safe_write_text (Path.write_text
    text-mode default) AND safe_append_text (os.open text-mode default on
    Windows) both translated \\n -> \\r\\n. Pins BOTH a small ASCII payload AND
    a >1024-byte multibyte (non-ASCII UTF-8) payload (m-add-1) — the CRLF fix
    interacts with both newline position AND the 1024-byte Windows write
    boundary; a CRLF surviving past byte 1024 or a multibyte sequence straddling
    the split would pass a small-ASCII test yet corrupt a real vault file."""
    small = "alpha\nbeta\ngamma\n"
    big = ("café-Müller-中文-" * 80) + "\n" + ("Ω≈ç√∫-行 " * 80) + "\n"
    assert len(big.encode("utf-8")) > 1024, "the large-payload case must exceed the 1024B boundary"

    for label, payload in [("small-ascii", small), ("large-multibyte", big)]:
        # canonical reference: the exact pattern the seam writers use
        canon = tmp_path / f"canon-{label}.md"
        canon_tmp = canon.with_name(canon.name + ".tmp")
        canon_tmp.write_text(payload, encoding="utf-8", newline="")
        os.replace(canon_tmp, canon)
        canon_bytes = canon.read_bytes()

        w = tmp_path / f"write-{label}.md"
        safe_write_text(w, payload)
        assert w.read_bytes() == canon_bytes, f"safe_write_text not LF-faithful ({label})"
        assert b"\r\n" not in w.read_bytes(), f"safe_write_text emitted CRLF ({label})"

        a = tmp_path / f"append-{label}.md"
        safe_append_text(a, payload)
        assert a.read_bytes() == canon_bytes, f"safe_append_text not LF-faithful ({label})"
        assert b"\r\n" not in a.read_bytes(), f"safe_append_text emitted CRLF ({label})"


def test_byte_faithfulness_structural_guard() -> None:
    """slice-090 two-layer discipline: a platform-independent structural guard
    complementing the nt-skipif behavioral test — pins the LF-fix even when the
    suite runs on POSIX. safe_write_text MUST pass newline='' to write_text;
    safe_append_text MUST OR in O_BINARY on os.open."""
    import inspect

    sw = inspect.getsource(_vault_write.safe_write_text)
    sa = inspect.getsource(_vault_write.safe_append_text)
    assert 'newline=""' in sw, "safe_write_text lost its newline='' LF-faithfulness (B1)"
    assert "O_BINARY" in sa, "safe_append_text lost its O_BINARY LF-faithfulness (B1)"


def test_safe_append_preserves_append_semantics(tmp_path: Path) -> None:
    """B1 guard: O_BINARY must NOT disturb O_APPEND — a second safe_append_text
    appends, does not truncate. Cross-platform."""
    target = tmp_path / "append-twice.md"
    safe_append_text(target, "first\n")
    safe_append_text(target, "second\n")
    assert target.read_bytes() == b"first\nsecond\n"
