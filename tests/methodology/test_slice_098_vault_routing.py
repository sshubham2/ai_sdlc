"""slice-098 / [[ADR-089]] verification tests: route Class-A filesystem vault
paths through VAULT_ROOT; RETIRE-when-external (fail-visible) the git-coupled
vault-content reads in parallel_conflict_resolver + stranded_slice_audit; KEEP
git ops on tracked slice/* refs. No-flip safety contract is binding.

Covers AC1 (AST source-scan, M5 + M-add-3 def-use reach + mutation non-vacuity),
the unified RETIRE signal `vault_is_external` (incl. M1 external-but-tracked),
m1 (_AUDIT_LOG_PATH byte-identity), AC3/AC5 (external-root subprocess + RETIRE),
and M-add-1 (diagnose-time read unreachable when the vault is not a U-file).
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TOOLS = ["parallel_conflict_resolver", "stranded_slice_audit", "pulse_worktree_resolver"]
_ROUTABLE_ROOTS = {"repo_root", "scan_root"}
_VAULT_MARKER = "architecture"


# --------------------------------------------------------------------------- #
# AC1 — AST source-scan: no `architecture/...` vault literal in a Class-A
# filesystem-composition position (operand of Path.__truediv__ against a
# repo_root/scan_root-derived Path), incl. ONE-HOP def-use (M-add-3). Class-B
# git-string identities (qrel/_SOFT_FILE_SET/git add args) are NOT in div-position
# so are excluded by the predicate's STRUCTURE; docstrings/comments likewise.
# --------------------------------------------------------------------------- #


def _is_root_rooted(node: ast.AST) -> bool:
    """True if `node` is a repo_root/scan_root Name, or a `/`-chain rooted at one
    (e.g. ``repo_root / VAULT_ROOT / 'slices'``)."""
    if isinstance(node, ast.Name):
        return node.id in _ROUTABLE_ROOTS
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return _is_root_rooted(node.left)
    return False


def _has_vault_marker(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant):
        return isinstance(node.value, str) and _VAULT_MARKER in node.value
    if isinstance(node, ast.JoinedStr):  # f"architecture/slices/slice-{n}"
        return any(
            isinstance(v, ast.Constant) and isinstance(v.value, str) and _VAULT_MARKER in v.value
            for v in node.values
        )
    return False


def _find_unrouted_vault_div_literals(source: str) -> list[str]:
    """Return descriptions of any Class-A vault literal NOT routed via VAULT_ROOT.

    A Class-A position is the RIGHT operand of ``Path.__truediv__`` whose LEFT is
    repo_root/scan_root-rooted, where the right operand is (a) directly an
    `architecture/...` str/f-string Constant, OR (b) a Name bound earlier in the
    same function to such a literal (the M-add-3 one-hop def-use shape).
    """
    tree = ast.parse(source)
    findings: list[str] = []
    for func in ast.walk(tree):
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        marked_names: set[str] = set()
        for stmt in ast.walk(func):
            if (
                isinstance(stmt, ast.Assign)
                and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], ast.Name)
                and _has_vault_marker(stmt.value)
            ):
                marked_names.add(stmt.targets[0].id)
        for node in ast.walk(func):
            if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)):
                continue
            if not _is_root_rooted(node.left):
                continue
            right = node.right
            if _has_vault_marker(right):
                findings.append(f"{func.name}: direct vault literal in Path-div")
            elif isinstance(right, ast.Name) and right.id in marked_names:
                findings.append(
                    f"{func.name}: variable-mediated vault literal {right.id!r} in Path-div"
                )
    return findings


@pytest.mark.parametrize("tool", _TOOLS)
def test_no_unrouted_vault_literal_in_class_a_position(tool: str) -> None:
    src = (_REPO_ROOT / "tools" / f"{tool}.py").read_text(encoding="utf-8")
    findings = _find_unrouted_vault_div_literals(src)
    assert findings == [], f"unrouted Class-A vault literal(s) in {tool}: {findings}"


def test_scanner_non_vacuous_direct() -> None:
    bad = "def f(repo_root):\n    return repo_root / 'architecture' / 'slice-queue.md'\n"
    assert _find_unrouted_vault_div_literals(bad), "scanner missed a DIRECT Class-A vault literal"


def test_scanner_non_vacuous_variable_mediated() -> None:
    # M-add-3: the HARD real case — literal assigned to a var, then joined (L322 shape).
    bad = (
        "def f(repo_root, num, name):\n"
        "    archive_path = f'architecture/slices/archive/slice-{num}-{name}'\n"
        "    return (repo_root / archive_path).exists()\n"
    )
    assert _find_unrouted_vault_div_literals(
        bad
    ), "scanner missed a VARIABLE-MEDIATED Class-A vault literal (M-add-3 vacuity)"


# --------------------------------------------------------------------------- #
# Unified RETIRE signal — vault_is_external (PCR + stranded). Covers M1
# (external-but-tracked under the repo → NOT external → proceed).
# --------------------------------------------------------------------------- #


def test_vault_is_external_signal_logic(tmp_path: Path) -> None:
    from tools._vault_git import vault_is_external

    repo = tmp_path / "repo"
    repo.mkdir()
    # Default in-tree (relative "architecture") → NOT external.
    assert vault_is_external(repo, vault_root=Path("architecture")) is False
    # M1 external-but-tracked: an absolute path UNDER the repo work tree → NOT external.
    assert vault_is_external(repo, vault_root=repo / "vault") is False
    # A relative subdir → NOT external.
    assert vault_is_external(repo, vault_root=Path("vault")) is False
    # True external store: an absolute path OUTSIDE the repo → external → RETIRE.
    external = tmp_path / "external_vault"
    external.mkdir()
    assert vault_is_external(repo, vault_root=external) is True


# --------------------------------------------------------------------------- #
# m1 — _AUDIT_LOG_PATH no-flip byte-identity (5 consumers via repo_root / _AUDIT_LOG_PATH).
# --------------------------------------------------------------------------- #


def test_audit_log_path_no_flip_byte_identity() -> None:
    # On the default in-tree repo (env unset), the routed audit-log path must be
    # byte-identical to the pre-slice hardcoded join.
    from tools._vault_paths import VAULT_ROOT
    from tools.parallel_conflict_resolver import _AUDIT_LOG_PATH

    assert VAULT_ROOT == Path("architecture"), "this test runs on the no-flip default repo"
    repo_root = Path("/some/repo")
    assert (repo_root / _AUDIT_LOG_PATH) == (
        repo_root / "architecture" / "parallel-conflict-resolution-log.md"
    )


# --------------------------------------------------------------------------- #
# M-add-1 — the diagnose-time `_git_show_stage` reads (L216-217) are gated on the
# vault file being a U-file; an untracked vault is never a U-file, so the read is
# unreachable. Proven by a call-spy on a clean repo (no conflict → no U-files).
# --------------------------------------------------------------------------- #


def test_diagnose_time_git_show_stage_not_called_without_vault_ufile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tools.parallel_conflict_resolver as pcr

    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True, capture_output=True)

    calls: list[str] = []
    real = pcr._git_show_stage

    def _spy(repo_root: Path, stage: int, path: str) -> str:
        calls.append(path)
        return real(repo_root, stage, path)

    monkeypatch.setattr(pcr, "_git_show_stage", _spy)
    pcr.diagnose_conflict(repo)  # clean repo → no U-files → vault read never gated-in
    assert not any("slice-queue.md" in c for c in calls), (
        "diagnose-time _git_show_stage fired on the vault despite no vault U-file "
        "(M-add-1 unreachability violated)"
    )


# --------------------------------------------------------------------------- #
# AC3 / AC5 — external-root flip-readiness + RETIRE, via SUBPROCESS env-injection
# (the consumer-freeze cascade: in-process monkeypatch does NOT propagate to the
# frozen VAULT_ROOT; only a fresh process re-reads AI_SDLC_VAULT_ROOT).
# --------------------------------------------------------------------------- #

_EXTERNAL_PROBE = r"""
import sys
from pathlib import Path
from tools._vault_paths import VAULT_ROOT
from tools._vault_git import vault_is_external
from tools.pulse_worktree_resolver import _resolve_milestone_path
from tools.parallel_conflict_resolver import _retire_if_vault_external

ext = Path(sys.argv[1])
repo = Path(sys.argv[2])
assert VAULT_ROOT == ext, f"VAULT_ROOT not external: {VAULT_ROOT}"

# AC3: pulse Class-A ROUTE resolves milestone under the external root.
ms = _resolve_milestone_path(repo, "098", "route-or-retire-git-coupled-vault-tools")
assert ms is not None and str(ext) in str(ms), f"pulse did not resolve under external root: {ms}"

# AC5: stranded + PCR RETIRE visibly when the vault is external.
assert vault_is_external(repo) is True, "stranded signal: vault_is_external should be True"
res = _retire_if_vault_external(repo)
assert res is not None and res.action == "STOP" and "external" in res.reason.lower(), (
    f"PCR did not RETIRE visibly under external vault: {res}"
)
print("EXTERNAL_PROBE_OK")
"""


def test_external_root_flip_readiness_and_retire(tmp_path: Path) -> None:
    ext = tmp_path / "external_vault"
    (ext / "slices" / "slice-098-route-or-retire-git-coupled-vault-tools").mkdir(parents=True)
    (
        ext / "slices" / "slice-098-route-or-retire-git-coupled-vault-tools" / "milestone.md"
    ).write_text("stage: build\n", encoding="utf-8")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True, capture_output=True)

    env = {**_os_environ(), "AI_SDLC_VAULT_ROOT": str(ext)}
    proc = subprocess.run(
        [sys.executable, "-c", _EXTERNAL_PROBE, str(ext), str(repo)],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0, f"external probe failed:\nSTDOUT:{proc.stdout}\nSTDERR:{proc.stderr}"
    assert "EXTERNAL_PROBE_OK" in proc.stdout


def _os_environ() -> dict[str, str]:
    import os

    return dict(os.environ)
