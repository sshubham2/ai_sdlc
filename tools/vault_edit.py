"""vault_edit — skill-path safe-append CLI (SVW-1 / slice-095 / [[ADR-087]]).

Gives Claude (per SKILL.md prose) a concurrency-safe channel to APPEND
LLM-authored content to a shared-aggregate vault file, so a skill-driven
append no longer bypasses ``_vault_write``'s lock + the R-32 mitigation.
The complement of slice-094's Python-writer routing (VWS-1) on the
skill-driven write path.

Ships ``append`` ONLY (the closed append sub-class). ``rewrite`` is
deliberately NOT exposed: ``safe_write_text`` is torn-write-safe but NOT
lost-update-safe for a read-modify-write, so a per-call rewrite wrapper would
give false confidence for the deferred RMW class (``_index.md`` recent-10 /
in-place risk-status flips — the flip slice owns it).

Usage::

    python -m tools.vault_edit append --file risk-register.md --content-file entry.md
    python -m tools.vault_edit append --file slices/_index.md --stdin < entry.md

``--file`` is resolved against ``VAULT_ROOT`` (``tools/_vault_paths.py``); a
path escaping the vault root (absolute, or via ``..``) is a usage error
(exit 2). Content comes from ``--content-file`` (robust on Windows-PowerShell
where multi-line piping is fragile) or ``--stdin``.

Exit codes:
    0  appended
    2  usage error — bad/escaping ``--file``, missing content, or an append
       failure (fail-VISIBLE per the R-7 silent-disable class; never a silent
       no-op). There is no exit 1 (this is a writer, not an auditor).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools import _stdout
from tools._vault_paths import VAULT_ROOT
from tools._vault_write import safe_append_text


def _resolve_in_vault(file_arg: str) -> Path:
    """Resolve ``file_arg`` against ``VAULT_ROOT``; raise ``ValueError`` on a
    path that resolves outside the vault root (absolute or ``..``-escape)."""
    root = VAULT_ROOT.resolve()
    target = (VAULT_ROOT / file_arg).resolve()
    if target != root and root not in target.parents:
        raise ValueError(
            f"--file {file_arg!r} resolves outside the vault root "
            f"({target} is not under {root})"
        )
    return target


def _read_content(args: argparse.Namespace) -> str:
    if args.content_file is not None:
        return Path(args.content_file).read_text(encoding="utf-8")
    return sys.stdin.read()


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="vault_edit",
        description=(
            "Skill-path safe-append CLI (SVW-1): append LLM-authored content to "
            "a shared-aggregate vault file under VAULT_ROOT via the _vault_write "
            "lock (R-32). Append-only by design."
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
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--content-file", default=None,
        help="read the content block from this file (robust on Windows)",
    )
    source.add_argument(
        "--stdin", action="store_true",
        help="read the content block from stdin",
    )
    args = parser.parse_args(argv)

    # argparse guarantees args.command == "append" (subparser required=True).
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


if __name__ == "__main__":
    sys.exit(main())
