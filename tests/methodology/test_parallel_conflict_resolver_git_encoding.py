"""AC#2 / ADR-082 structural recurrence guard for slice-090.

Cross-platform (runs on ALL hosts, unlike the cp1252-host-only behavioral
repro at tests/bugs/test_pcr_git_subprocess_cp1252_decode.py): AST-scan
tools/parallel_conflict_resolver.py and assert that every git
``subprocess.run`` call which **decodes** output (i.e. carries ``text=True``)
also carries ``encoding="utf-8"`` — so git's UTF-8 output is never decoded via
the host locale code page (cp1252 on Windows).

The predicate keys on ``text=True``-presence, NOT raw ``capture_output`` (per
/critique B1): the byte-mode git calls capture output WITHOUT ``text=True`` and
MUST NOT carry ``encoding=`` (that would change their byte/text contract). Two
kinds of byte-mode site (5 total post-slice-091):
  - 4 **staging** calls (``git add`` / ``git rebase --continue`` in
    ``resolve_soft_conflict`` + ``resolve_vault_claim_conflict``) — capture
    bytes for ``{exc!r}`` only and never decode stdout.
  - 1 **read-decode** call: ``_git_show_stage`` (slice-091 / ADR-083) — captures
    bytes then decodes them EXPLICITLY via ``.decode("utf-8")`` in the main
    thread (so a non-UTF-8 stage raises a catchable ``_StageDecodeError`` rather
    than the pre-fix silent reader-thread swallow). It carries no ``encoding=``
    on the ``subprocess.run`` call, so it is correctly byte-mode here.

ADR-082 reuse seam: the ``argv[0] == "git"`` AND ``text=True`` predicate below
is the reusable kernel the queued follow-up
``audit-cp1252-decode-pattern-across-tools`` should lift to a repo-wide scanner.
"""
from __future__ import annotations

import ast
from pathlib import Path

# Exact count of output-decoding (text=True) git subprocess.run sites. Count-
# pinned per /critique B1 so a new decode site that forgets encoding= breaks
# loudly. Unchanged at 9 across slice-091: _git_show_stage left the decode set
# (now byte-mode + explicit .decode), but the new _append_decode_stop_audit
# breadcrumb helper added a `git rev-parse HEAD` decode site (ADR-083) — the two
# offset, so the decode count is preserved.
_EXPECTED_DECODE_SITES = 9
# Byte-mode sites excluded from the decode-encoding invariant: 4 staging sites
# (git add / rebase --continue) + 1 read-decode site (_git_show_stage, slice-091
# /ADR-083 — decodes explicitly via .decode, carries no encoding=). All 5
# capture_output=True, no text=True, no encoding=.
_EXPECTED_BYTE_MODE_SITES = 5


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("could not locate repo root (no .git up-tree)")


def _module_path() -> Path:
    return _repo_root() / "tools" / "parallel_conflict_resolver.py"


def _kw(call: ast.Call, name: str):
    """Return the keyword node for `name`, or None."""
    for kw in call.keywords:
        if kw.arg == name:
            return kw
    return None


def _is_true(node) -> bool:
    return isinstance(node, ast.Constant) and node.value is True


def _argv_is_git(call: ast.Call) -> bool:
    """True when the first positional arg is a list literal whose first
    element is the constant string "git"."""
    if not call.args:
        return False
    argv = call.args[0]
    if not isinstance(argv, (ast.List, ast.Tuple)) or not argv.elts:
        return False
    first = argv.elts[0]
    return isinstance(first, ast.Constant) and first.value == "git"


def _collect_git_subprocess_runs() -> list[ast.Call]:
    """All `subprocess.run(["git", ...], ...)` call nodes in the module."""
    tree = ast.parse(_module_path().read_text(encoding="utf-8"))
    calls: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "run"
            and isinstance(func.value, ast.Name)
            and func.value.id == "subprocess"
            and _argv_is_git(node)
        ):
            calls.append(node)
    return calls


def _classify():
    decode_sites: list[ast.Call] = []
    byte_mode_sites: list[ast.Call] = []
    for call in _collect_git_subprocess_runs():
        text_kw = _kw(call, "text")
        capture_kw = _kw(call, "capture_output")
        if text_kw is not None and _is_true(text_kw.value):
            decode_sites.append(call)
        elif capture_kw is not None and _is_true(capture_kw.value):
            byte_mode_sites.append(call)
    return decode_sites, byte_mode_sites


def test_all_git_decode_sites_specify_utf8_encoding():
    """Every git subprocess.run that decodes output (text=True) MUST pass
    encoding="utf-8" — the ADR-082 invariant. A future decode site that omits
    it (reverting to the locale code page) fails here on every host."""
    decode_sites, _ = _classify()
    offenders = []
    for call in decode_sites:
        enc = _kw(call, "encoding")
        if enc is None or not (isinstance(enc.value, ast.Constant) and enc.value.value == "utf-8"):
            offenders.append(call.lineno)
    assert offenders == [], (
        f"git subprocess.run decode site(s) at line(s) {offenders} lack "
        'encoding="utf-8" — git UTF-8 output would be decoded via the host '
        "locale code page (cp1252 on Windows). Add encoding=\"utf-8\" per ADR-082."
    )


def test_exactly_nine_git_decode_sites_byte_mode_sites_excluded():
    """Count-pin (per /critique B1; slice-091 byte-mode 4→5): exactly 9 decode
    sites and 5 byte-mode sites (4 staging + 1 read-decode `_git_show_stage`).
    The byte-mode sites MUST NOT carry encoding= (the 4 staging sites capture
    bytes for error-repr only; `_git_show_stage` decodes explicitly via
    `.decode` — adding encoding= to any would change its contract)."""
    decode_sites, byte_mode_sites = _classify()
    assert len(decode_sites) == _EXPECTED_DECODE_SITES, (
        f"expected exactly {_EXPECTED_DECODE_SITES} git decode (text=True) sites; "
        f"found {len(decode_sites)} at lines {[c.lineno for c in decode_sites]}. "
        "If a git call was added/removed, update _EXPECTED_DECODE_SITES deliberately."
    )
    assert len(byte_mode_sites) == _EXPECTED_BYTE_MODE_SITES, (
        f"expected exactly {_EXPECTED_BYTE_MODE_SITES} byte-mode git sites (4 staging + 1 read-decode); "
        f"found {len(byte_mode_sites)} at lines {[c.lineno for c in byte_mode_sites]}."
    )
    wrongly_encoded = [
        c.lineno for c in byte_mode_sites if _kw(c, "encoding") is not None
    ]
    assert wrongly_encoded == [], (
        f"byte-mode git staging site(s) at line(s) {wrongly_encoded} carry "
        "encoding= — they capture bytes and must NOT decode (B1 exclusion)."
    )
