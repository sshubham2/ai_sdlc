"""vault_edit — skill-path safe vault-write CLI (SVW-1 / slice-095 / [[ADR-087]];
rewrite + read added slice-097 / [[ADR-088]]).

Gives Claude (per SKILL.md prose) concurrency-safe channels to mutate a
shared-aggregate vault file, so a skill-driven write no longer bypasses
``_vault_write``'s lock + the R-32 mitigation. The complement of slice-094's
Python-writer routing (VWS-1) on the skill-driven write path.

Subcommands:

- ``append`` (slice-095) — append LLM-authored content (``O_APPEND`` under the
  sidecar lock; non-clobbering, lost-update-safe for the append class).
- ``rewrite`` (slice-097) — compare-and-swap whole-file rewrite for the
  read-modify-write class (``_index.md`` recent-10 regen, in-place risk-status
  flips). Writes only if the on-disk bytes still match the ``--base-file`` the
  skill read (EOL-NORMALIZED compare — the CRLF ``_index.md`` vs an LF base must
  not false-conflict; EOL-PRESERVING write — no CRLF→LF churn). A stale base →
  exit **3** (the retryable signal): the skill re-reads + re-applies + retries
  (bounded in skill prose). This is the channel slice-095 deliberately deferred
  ("``rewrite`` is NOT exposed") — slice-097 exposes it via CAS, which is
  lost-update-safe without holding a lock across an LLM read+edit.
- ``read`` (slice-097) — emit the target's current RAW bytes to stdout (binary,
  no EOL normalization) so the skill can capture a byte-exact CAS base WITHOUT
  the ``Read`` tool's ``cat -n``/EOL-normalized framing (critique M2).

Usage::

    python -m tools.vault_edit append  --file risk-register.md --content-file entry.md
    python -m tools.vault_edit read     --file slices/_index.md > base.bin
    python -m tools.vault_edit rewrite  --file slices/_index.md --base-file base.bin --content-file new.md

``--file`` is resolved against ``VAULT_ROOT`` (``tools/_vault_paths.py``); a path
escaping the vault root (absolute, or via ``..``) is a usage error (exit 2).

Exit codes:
    0  success (appended / rewritten / read-emitted)
    2  usage error — bad/escaping ``--file``, missing content/base, or a write
       failure (fail-VISIBLE per the R-7 silent-disable class; never a silent no-op)
    3  ``rewrite`` ONLY — compare-and-swap CONFLICT (the on-disk file changed since
       ``--base-file`` was read; the retryable signal, DISTINCT from usage exit 2)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools import _stdout
from tools._vault_paths import VAULT_ROOT
from tools._vault_write import StaleVaultBaseError, safe_append_text, safe_rewrite_text


def _resolve_in_vault(file_arg: str) -> Path:
    """Resolve ``file_arg`` against ``VAULT_ROOT``; raise ``ValueError`` on a
    path that is empty, resolves to the vault-root directory ITSELF, or escapes
    the vault root (absolute or ``..``-escape).

    m3 (slice-095 code-review): ``--file .`` / ``--file ""`` previously slipped
    past the containment check (``target == root`` made the old guard False) and
    only failed downstream as an incidental ``IsADirectoryError``. It is now an
    INTENTIONAL rejection with an actionable message (fail-VISIBLE on purpose,
    not by accident — the R-7 posture)."""
    root = VAULT_ROOT.resolve()
    if not file_arg.strip():
        raise ValueError("--file must name a vault file (got an empty path)")
    target = (VAULT_ROOT / file_arg).resolve()
    if target == root:
        raise ValueError(
            f"--file {file_arg!r} resolves to the vault root directory itself, "
            f"not a file under it — name a file (e.g. risk-register.md)"
        )
    if root not in target.parents:
        raise ValueError(
            f"--file {file_arg!r} resolves outside the vault root "
            f"({target} is not under {root})"
        )
    return target


def _read_content(args: argparse.Namespace) -> str:
    """Read the NEW content (append/rewrite) as text. EOL handling is the
    primitive's job: ``safe_append_text`` is byte-faithful; ``safe_rewrite_text``
    re-applies the target's detected EOL. (The CAS BASE is read separately in
    binary — see ``_read_base_bytes`` — so the compare is exact.)"""
    if args.content_file is not None:
        return Path(args.content_file).read_text(encoding="utf-8")
    return sys.stdin.read()


def _read_base_bytes(base_file: str) -> bytes:
    """Read the CAS base in BINARY (critique M2): the base must be byte-exact to
    what was on disk when the skill read it — NOT universal-newline-normalized by
    ``read_text``. The EOL-normalized compare in ``safe_rewrite_text`` then makes a
    CRLF-disk vs LF-base pair compare equal without a forced byte match."""
    return Path(base_file).read_bytes()


def _cmd_append(args: argparse.Namespace) -> int:
    try:
        target = _resolve_in_vault(args.file)
    except ValueError as exc:
        sys.stderr.write(f"vault_edit: {exc}\n")
        return 2
    try:
        content = _read_content(args)
    except OSError as exc:
        sys.stderr.write(f"vault_edit: cannot read content: {exc}\n")
        return 2
    try:
        safe_append_text(target, content)
    except (OSError, TimeoutError) as exc:
        # PermissionError (EPERM after retries) / TimeoutError (lock) / OSError.
        # Fail-VISIBLE (R-7): a write failure is loud + non-zero, never silent.
        sys.stderr.write(
            f"vault_edit: append to {target} failed (fail-visible per R-7): {exc}\n"
        )
        return 2
    return 0


def _cmd_rewrite(args: argparse.Namespace) -> int:
    try:
        target = _resolve_in_vault(args.file)
    except ValueError as exc:
        sys.stderr.write(f"vault_edit: {exc}\n")
        return 2
    try:
        base = _read_base_bytes(args.base_file)
    except OSError as exc:
        sys.stderr.write(f"vault_edit: cannot read --base-file: {exc}\n")
        return 2
    try:
        content = _read_content(args)
    except OSError as exc:
        sys.stderr.write(f"vault_edit: cannot read content: {exc}\n")
        return 2
    try:
        safe_rewrite_text(target, content, expected_base=base)
    except StaleVaultBaseError as exc:
        # exit 3 — DISTINCT from usage(2): the file changed since base was read.
        # The retryable signal; the skill re-reads + re-applies + retries (bounded).
        sys.stderr.write(f"vault_edit: rewrite CONFLICT (exit 3) — {exc}\n")
        return 3
    except (OSError, TimeoutError) as exc:
        sys.stderr.write(
            f"vault_edit: rewrite of {target} failed (fail-visible per R-7): {exc}\n"
        )
        return 2
    return 0


def _cmd_read(args: argparse.Namespace) -> int:
    """Emit the target's current RAW bytes (binary) — the byte-exact CAS base. A
    missing target emits nothing (the create-case base = empty).

    Prefer ``--out-file`` (Python writes the raw bytes itself): shell redirection
    `> base.bin` is NOT byte-safe on the project's default shell — PowerShell's
    `>` is `Out-File`, which re-encodes stdout as UTF-16LE+BOM and corrupts the
    base, guaranteeing a CAS false-conflict/livelock (slice-097 /code-review B1).
    Without ``--out-file`` the bytes go to ``sys.stdout.buffer`` (raw, bypassing
    the UTF-8 text wrapper) — safe only if the caller captures stdout in BINARY
    (e.g. a real ``subprocess`` pipe), never a PowerShell `>` redirect."""
    try:
        target = _resolve_in_vault(args.file)
    except ValueError as exc:
        sys.stderr.write(f"vault_edit: {exc}\n")
        return 2
    try:
        data = target.read_bytes() if target.exists() else b""
    except OSError as exc:
        sys.stderr.write(f"vault_edit: cannot read {target}: {exc}\n")
        return 2
    if args.out_file is not None:
        try:
            Path(args.out_file).write_bytes(data)  # raw — shell-redirection-free (B1)
        except OSError as exc:
            sys.stderr.write(f"vault_edit: cannot write --out-file: {exc}\n")
            return 2
        return 0
    sys.stdout.buffer.write(data)  # RAW bytes — bypass the UTF-8 text wrapper
    sys.stdout.buffer.flush()
    return 0


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="vault_edit",
        description=(
            "Skill-path safe vault-write CLI (SVW-1): append / compare-and-swap "
            "rewrite / raw-read of a shared-aggregate vault file under VAULT_ROOT "
            "via the _vault_write lock (R-32)."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ap = sub.add_parser(
        "append", help="append content to a vault file (sidecar-lock + O_APPEND)"
    )
    ap.add_argument(
        "--file", required=True,
        help="vault-relative path (resolved under VAULT_ROOT; ..-escape rejected)",
    )
    src_a = ap.add_mutually_exclusive_group(required=True)
    src_a.add_argument(
        "--content-file", default=None,
        help="read the content block from this file (robust on Windows)",
    )
    src_a.add_argument(
        "--stdin", action="store_true", help="read the content block from stdin",
    )

    rw = sub.add_parser(
        "rewrite",
        help="compare-and-swap whole-file rewrite (R-32 RMW class; exit 3 on conflict)",
    )
    rw.add_argument(
        "--file", required=True,
        help="vault-relative path (resolved under VAULT_ROOT; ..-escape rejected)",
    )
    rw.add_argument(
        "--base-file", required=True,
        help="file holding the BASE bytes the skill read (CAS precondition; read binary)",
    )
    src_rw = rw.add_mutually_exclusive_group(required=True)
    src_rw.add_argument(
        "--content-file", default=None,
        help="read the NEW whole-file content from this file (robust on Windows)",
    )
    src_rw.add_argument(
        "--stdin", action="store_true", help="read the NEW whole-file content from stdin",
    )

    rd = sub.add_parser(
        "read", help="capture the target's current RAW bytes (CAS base) — prefer --out-file"
    )
    rd.add_argument(
        "--file", required=True,
        help="vault-relative path (resolved under VAULT_ROOT; ..-escape rejected)",
    )
    rd.add_argument(
        "--out-file", default=None,
        help="write the raw bytes to this file (byte-safe; AVOIDS shell `>` "
             "redirection which corrupts bytes under PowerShell — B1). Omit to "
             "emit to stdout.buffer (safe only with a binary subprocess pipe).",
    )

    args = parser.parse_args(argv)
    if args.command == "append":
        return _cmd_append(args)
    if args.command == "rewrite":
        return _cmd_rewrite(args)
    if args.command == "read":
        return _cmd_read(args)
    parser.error(f"unknown command {args.command!r}")  # unreachable (required=True)
    return 2


if __name__ == "__main__":
    sys.exit(main())
