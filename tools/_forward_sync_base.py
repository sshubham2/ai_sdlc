"""Forward-sync parallel-safety discriminators (slice-117; [[ADR-108]]).

The four forward-sync gates — CAD-1, MCFS-1, AVFS-1, TVFS-1 — compare an
in-flight slice's in-repo source against the SHARED ``~/.claude/`` install (or
venv). Under BRANCH-2/BRANCH-3 a parallel sibling slice that forward-syncs the
shared install makes an unrelated slice's gate HALT on a file it never touched
(R-28, the slice-087 incident). This leaf helper supplies the two
discriminators that let a gate emit a non-blocking ``external-drift`` WARN for a
sibling-caused divergence while still HALTing on genuine self-caused drift.

Per-gate-type (the structural property differs):

  - **Version gates** (AVFS-1, TVFS-1): :func:`installed_is_sibling_ahead` —
    semver ordering. Installed strictly-newer than in-repo ⟹ a sibling moved the
    shared install/venv ahead (external). Older/equal-but-divergent ⟹ self
    bumped-but-unsynced OR a stale venv older than the source (HALT).
    Unparseable / odd-arity ⟹ ``None`` (caller falls back to its existing strict
    compare → HALT; never mask).
  - **Content gates** (CAD-1, MCFS-1): :func:`slice_modified_source` — git
    merge-base. "Did THIS slice edit the source vs its fork point?" If not, an
    installed divergence is a sibling's forward-sync (external). Fail-closed
    ``True`` on any git failure.

**Leaf-purity invariant**: imports ONLY stdlib (never ``tools.*``) so it stays
the dependency leaf — mirrors ``tools/_vault_paths.py`` / ``tools/_stdout.py``.
The breadcrumb/banner emission (the vault write) lives in the GATES, not here —
this module only classifies; it performs no I/O beyond read-only ``git``.

**cp1252 discipline** (AP-7 / [[ADR-082]]): every ``git`` call captures BYTES
with NO ``encoding=`` and is decoded in the MAIN thread, so a non-UTF-8 path or
blob never raises ``UnicodeDecodeError`` in a subprocess reader thread on
Windows.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def _normalize_bytes(raw: bytes) -> bytes:
    """CRLF→LF normalization applied to an in-memory blob (EOL-DRIFT-1 /
    [[ADR-033]]). Behaviour-parity with
    ``tests/skill_drift_equality.py::_normalized_sha256`` (CSP-1). This is NOT
    the Path-based ``_sha256_of`` / ``_normalized_bytes`` in the gates — those
    read a file; this normalizes a ``git show`` blob already in memory
    (round-1 M3)."""
    return raw.replace(b"\r\n", b"\n")


def _semver_tuple(version: str) -> tuple[int, ...] | None:
    """Parse a version string to a 3-int tuple, or ``None``.

    **Arity-strict** (round-2 m2): accept ONLY an exactly-3-part, all-digits
    shape (``N.N.N``). A 2-part (``0.84``), 4-part (``0.84.0.1``), pre-release
    (``0.84.0.dev0``), ``v``-prefixed, or empty shape ⟹ ``None``. The strict
    arity guard makes the unequal-length int-tuple comparison quirk
    (``(0, 84) < (0, 84, 0)`` is ``True``) unreachable — odd shapes route to the
    caller's strict-HALT fallback rather than to silent (and wrong) ordering.
    The repo's ``VERSION`` is invariantly 3-part, so this only hardens an
    off-nominal input.
    """
    parts = version.strip().split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return None
    return tuple(int(p) for p in parts)


def installed_is_sibling_ahead(
    in_repo_version: str, installed_version: str
) -> bool | None:
    """Version-gate discriminator (AVFS-1, TVFS-1).

    Returns:
      ``True``  — installed is a strictly-newer semver than in-repo ⟹ a sibling
                  forward-synced the shared install/venv ahead (external-drift
                  → WARN).
      ``False`` — installed ``<=`` in-repo (self bumped-but-unsynced, OR a venv
                  older than the source) ⟹ self-caused drift (HALT).
      ``None``  — either side is not a clean 3-part ``N.N.N`` ⟹ the caller MUST
                  fall back to its existing strict compare → HALT (never mask;
                  M-add-1 / round-2 m2).
    """
    t_in = _semver_tuple(in_repo_version)
    t_inst = _semver_tuple(installed_version)
    if t_in is None or t_inst is None:
        return None
    return t_inst > t_in


def _git_bytes(repo_root: Path, args: list[str]) -> tuple[int, bytes]:
    """Run ``git -C <repo_root> <args>`` capturing BYTES (no ``encoding=``;
    AP-7). Returns ``(returncode, stdout_bytes)``; decoding happens in the main
    thread at the call site. May raise ``OSError`` (git binary absent) /
    ``subprocess.SubprocessError`` — caught by the public callers."""
    proc = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,  # BYTES — no text=/encoding= (AP-7 / ADR-082)
        check=False,
    )
    return proc.returncode, proc.stdout


def _resolve_default_sha(repo_root: Path) -> str | None:
    """Resolve the repo's default-branch NAME, then to a concrete commit SHA.

    Mirrors ``skills/build-slice`` ``### Branch state`` name resolution
    (``symbolic-ref refs/remotes/origin/HEAD`` → ``config init.defaultBranch``),
    then resolves that NAME to a SHA (round-1 B2 — a bare name is not
    merge-base-able where no local branch of that name exists). Returns the SHA,
    or ``None`` if unresolvable (caller treats ``None`` as "fall back to
    strict")."""
    name = ""
    rc, out = _git_bytes(repo_root, ["symbolic-ref", "refs/remotes/origin/HEAD"])
    if rc == 0:
        ref = out.decode("utf-8", "replace").strip()
        name = ref.rsplit("/", 1)[-1] if ref else ""
    if not name:
        rc, out = _git_bytes(repo_root, ["config", "init.defaultBranch"])
        if rc == 0:
            name = out.decode("utf-8", "replace").strip()
    if not name:
        return None
    for cand in (name, f"refs/remotes/origin/{name}", f"refs/heads/{name}"):
        rc, out = _git_bytes(
            repo_root, ["rev-parse", "--verify", "--quiet", f"{cand}^{{commit}}"]
        )
        if rc == 0 and out.strip():
            return out.decode("utf-8", "replace").strip()
    return None


def slice_modified_source(repo_root: Path, rel_path: str) -> bool:
    """Content-gate discriminator (CAD-1, MCFS-1).

    Returns ``True`` iff this slice modified ``rel_path`` relative to its git
    merge-base with the default branch (so an installed divergence is
    self-caused → HALT). Returns ``False`` iff the in-repo file is
    byte-identical (modulo EOL) to the merge-base version (the slice did not
    touch it → an installed divergence is a sibling's forward-sync →
    external-drift).

    **Fail-closed** (R-7 — never weaken the gate): any git failure, an
    unresolvable default branch, a detached / on-default-branch HEAD, or a path
    absent at the base ⟹ ``True`` (strict). The detached/at-default guard
    (round-1 M1) uses ``git symbolic-ref -q HEAD`` + a SHA compare, NOT the
    ``--abbrev-ref`` idiom (which returns the literal ``"HEAD"`` when detached).
    """
    try:
        in_repo = repo_root / rel_path
        if not in_repo.is_file():
            return True  # newly-added / absent in-repo ⟹ strict

        default_sha = _resolve_default_sha(repo_root)
        if default_sha is None:
            return True  # unresolvable default branch ⟹ strict (round-1 B2)

        # Strict guard (round-1 M1): detached/rebase HEAD, or HEAD at the
        # default tip (not a slice ahead of it) ⟹ strict — never tolerate.
        rc_sym, _ = _git_bytes(repo_root, ["symbolic-ref", "-q", "HEAD"])
        if rc_sym != 0:
            return True  # detached HEAD / rebase in progress
        rc_head, head_out = _git_bytes(repo_root, ["rev-parse", "HEAD"])
        if rc_head == 0 and head_out.decode("utf-8", "replace").strip() == default_sha:
            return True  # HEAD is the default branch (no slice delta)

        rc_mb, mb_out = _git_bytes(repo_root, ["merge-base", "HEAD", default_sha])
        if rc_mb != 0 or not mb_out.strip():
            return True  # merge-base failure ⟹ strict
        base = mb_out.decode("utf-8", "replace").strip()

        # round-1 M5: key path-absent on returncode != 0 (128 = absent OR
        # bad-rev; both fail closed to strict). Byte-mode show (round-1 M4).
        rc_show, blob = _git_bytes(repo_root, ["show", f"{base}:{rel_path}"])
        if rc_show != 0:
            return True  # path absent at base / bad-rev ⟹ strict

        return _normalize_bytes(in_repo.read_bytes()) != _normalize_bytes(blob)
    except (subprocess.SubprocessError, OSError):
        # git binary absent (FileNotFoundError ⊂ OSError) or a transient
        # BRANCH-2 shared-.git lock ⟹ fail-closed strict (round-1 M5).
        return True
