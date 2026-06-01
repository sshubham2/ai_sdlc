"""Vault git-tracked-check helper (slice-098 / [[ADR-089]]).

``vault_pathspec_is_tracked(repo_root, pathspec)`` is the binding signal for the
RETIRE-when-untracked decision: a git-tree read of vault CONTENT — the
``git show :N:<pathspec>`` rebase-stage reads in
``tools/parallel_conflict_resolver.py`` and the ``git show <branch>:<pathspec>``
/ ``git ls-tree`` bare-branch reads in ``tools/stranded_slice_audit.py`` — only
makes sense while the vault file is git-tracked. Once the vault relocates to an
untracked external store (the external-shared-vault flip; [[ADR-065]] /
[[ADR-085]]), those reads are inapplicable and MUST fail VISIBLY, never silently
mis-resolve (the R-32 silent-corruption class; the slice-090/091
silent-claim-drop family).

This is the PRECISE signal [[ADR-089]] adopts in place of the
``VAULT_ROOT_IS_DEFAULT`` resolution proxy (which conflated "resolution fell
through to default" with "git-untracked" and over-RETIREd an external-but-tracked
transitional config). It fires exactly when no git rebase/branch conflict can
arise (an untracked file has no rebase stage and is absent from a branch tree),
so it never strands a real conflict in the env-set-but-still-tracked window.

NOT in ``tools/_vault_paths.py``: that module is the dependency leaf (stdlib
only, no ``repo_root``); the tracked-check needs a ``repo_root`` + a git
subprocess, so it lives here. We capture bytes and NEVER decode (only the
return code is read), so there is no cp1252 decode hazard — distinct from
stranded's text-mode ``_run_git`` (BC-GLOBAL-5 / slice-090).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from tools._vault_paths import VAULT_ROOT


class VaultGitUnavailable(RuntimeError):
    """Raised when ``git`` cannot be spawned to answer the tracked-check.

    Truly exceptional (git binary missing / not spawnable). Callers surface this
    VISIBLY — it is NOT silently treated as an untracked verdict, which would
    mis-RETIRE on the default in-tree path (fail-visible, never silent).
    """


def vault_pathspec_is_tracked(repo_root: Path, pathspec: str) -> bool:
    """Return True iff ``pathspec`` (a forward-slash repo-relative git pathspec)
    is tracked in ``repo_root``'s git index/tree.

    Uses ``git ls-files --error-unmatch -- <pathspec>`` (rc 0 = tracked; rc != 0
    = untracked / not in index). Bytes-captured, NEVER decoded — only the return
    code is read, so there is no decode hazard. Raises ``VaultGitUnavailable`` on
    git-spawn failure (fail-visible, never a silent untracked verdict).
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "--error-unmatch", "--", pathspec],
            capture_output=True,  # bytes; never decoded (only returncode is used)
            check=False,
        )
    except OSError as exc:  # git binary missing / not spawnable
        raise VaultGitUnavailable(
            f"git unavailable for tracked-check of {pathspec!r} in {repo_root}: {exc}"
        ) from exc
    return proc.returncode == 0


def vault_is_external(repo_root: Path, vault_root: Path | None = None) -> bool:
    """Return True iff the resolved vault root points OUTSIDE ``repo_root``'s
    working tree — i.e. the vault has been flipped to an external (untracked)
    store.

    This is the RETIRE-when-untracked signal for ``stranded_slice_audit``'s
    bare-branch git-tree reads, where the per-pathspec ``vault_pathspec_is_tracked``
    check is UNSOUND: a stranded slice's vault content lives only on its unmerged
    BRANCH, never in the invoking tree's index, so ``git ls-files`` would return
    "untracked" and over-RETIRE every legitimate in-tree stranded slice (the
    slice-098 build-time deviation, ratified into [[ADR-089]] — its 4 existing
    test fixtures encode exactly this branch-only-content reality). The
    store-LOCATION question — is the vault inside this repo (git-managed) or in
    an external store — is the precise RETIRE precondition for the bare-branch case.

    ``parallel_conflict_resolver`` keeps the per-pathspec ``vault_pathspec_is_tracked``
    check instead: its conflicted ``slice-queue.md``/``shippability.md`` ARE in
    the rebase index when in-tree, so the precise per-file check is sound there.

    In-tree default (``VAULT_ROOT == Path("architecture")``, relative) and the
    external-but-tracked case (``VAULT_ROOT == <repo>/vault``, [[ADR-089]] M1)
    both resolve UNDER ``repo_root`` → not external → proceed. A flip to an
    absolute path outside the repo → external → RETIRE. Fail-open to in-tree on a
    resolve glitch (never spuriously RETIRE the no-flip path).
    """
    vr = VAULT_ROOT if vault_root is None else vault_root
    try:
        resolved = (repo_root / vr).resolve()
        root = repo_root.resolve()
    except OSError:
        return False  # resolve glitch → fail-open to in-tree (never spurious RETIRE)
    return resolved != root and root not in resolved.parents
