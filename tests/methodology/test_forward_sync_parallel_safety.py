"""Forward-sync parallel-safety tests (slice-117; [[ADR-108]]; TF-1).

Pins the per-gate-type hybrid that makes the four forward-sync gates parallel-
safe under BRANCH-2/BRANCH-3 (R-28, the slice-087 incident):

  - Version gates (AVFS-1, TVFS-1): ``installed_is_sibling_ahead`` — semver
    ordering. Installed strictly-newer ⟹ sibling-ahead (external/WARN);
    older/equal-divergent ⟹ self/stale (HALT); odd-arity/unparseable ⟹ None
    (strict-HALT fallback).
  - Content gates (CAD-1, MCFS-1): ``slice_modified_source`` — git merge-base.
    Unmodified-vs-base ⟹ external (WARN); modified ⟹ HALT; fail-closed True on
    any git/HEAD-state failure.

**Isolation (round-2 M-add-3)**: the git-shelling tests build an ISOLATED
``tmp_path`` git repo (same pattern as
``tests/methodology/test_branch_workflow_audit._init_repo_on_default_branch``)
and NEVER invoke the helper against the live worktree ``.git`` / ``~/.claude``
— the parallel-safety test must itself be parallel-safe (it must not observe
the concurrent slice-116 state).

Rule reference: R-28 / ADR-108. Test-first per TF-1.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import ai_sdlc_tools_version_forward_sync as tvfs
from tools import ai_sdlc_version_forward_sync as avfs
from tools import critique_agent_drift_audit as cad
from tools import methodology_changelog_forward_sync as mcfs
from tools._forward_sync_base import (
    _semver_tuple,
    installed_is_sibling_ahead,
    slice_modified_source,
)

_CRITIQUE_REL = "agents/critique.md"


# --------------------------------------------------------------------------
# Version-gate discriminator — installed_is_sibling_ahead (AVFS-1 / TVFS-1)
# --------------------------------------------------------------------------

class TestInstalledIsSiblingAhead:
    def test_installed_strictly_newer_is_sibling_ahead(self):
        # AC1: a sibling forward-synced the shared install/venv ahead → external.
        assert installed_is_sibling_ahead("0.84.0", "0.85.0") is True
        assert installed_is_sibling_ahead("0.84.0", "0.84.1") is True
        assert installed_is_sibling_ahead("0.84.0", "1.0.0") is True

    def test_installed_older_is_self_or_stale_halt(self):
        # AC2 (+ M-add-2 TVFS-1 stale-venv): installed behind in-repo → HALT.
        assert installed_is_sibling_ahead("0.84.0", "0.83.0") is False
        assert installed_is_sibling_ahead("0.84.0", "0.20.0") is False  # stale venv
        assert installed_is_sibling_ahead("0.84.0", "0.84.0") is False  # equal

    def test_lexical_trap_uses_numeric_ordering(self):
        # The whole reason a string compare is wrong: 0.10.0 > 0.9.0 numerically.
        assert installed_is_sibling_ahead("0.9.0", "0.10.0") is True
        assert installed_is_sibling_ahead("0.10.0", "0.9.0") is False

    def test_crlf_and_whitespace_stripped(self):
        # VERSION is read as b"0.84.0\r\n"; strip before parse.
        assert installed_is_sibling_ahead("0.84.0\r\n", "0.85.0\n") is True
        assert installed_is_sibling_ahead("  0.84.0  ", "0.85.0") is True

    def test_unparseable_returns_none_for_strict_fallback(self):
        # M-add-1: non-numeric / pre-release / v-prefixed → None → caller HALTs.
        assert installed_is_sibling_ahead("0.84.0", "0.85.0.dev0") is None
        assert installed_is_sibling_ahead("v0.84.0", "0.85.0") is None
        assert installed_is_sibling_ahead("0.84.0", "") is None
        assert installed_is_sibling_ahead("0.84.0", "not-a-version") is None

    def test_odd_arity_version_falls_back_to_strict(self):
        # round-2 m2: the unequal-length int-tuple quirk ((0,84) < (0,84,0))
        # is unreachable — odd-arity → None → strict-HALT fallback.
        assert _semver_tuple("0.84") is None       # 2-part
        assert _semver_tuple("0.84.0.1") is None    # 4-part
        assert _semver_tuple("0.84.0") == (0, 84, 0)
        assert installed_is_sibling_ahead("0.84", "0.84.0") is None
        assert installed_is_sibling_ahead("0.84.0", "0.84.0.1") is None


# --------------------------------------------------------------------------
# Content-gate discriminator — slice_modified_source (CAD-1 / MCFS-1)
# --------------------------------------------------------------------------

def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """git -C <repo> ... with a deterministic identity (no reliance on the
    host's global git config); bytes-safe."""
    return subprocess.run(
        [
            "git", "-C", str(repo),
            "-c", "user.name=t", "-c", "user.email=t@t",
            "-c", "commit.gpgsign=false",
            *args,
        ],
        capture_output=True, check=True,
    )


@pytest.fixture
def isolated_repo(tmp_path: Path) -> Path:
    """An ISOLATED tmp git repo on default branch ``master`` with the four
    gated sources committed (round-2 M-add-3 — never the live ``.git``). Mirrors
    ``test_branch_workflow_audit._init_repo_on_default_branch``."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "master")
    # Pin the default-branch name LOCALLY so _resolve_default_sha does not
    # depend on the host's global git config (deterministic isolation).
    _git(repo, "config", "init.defaultBranch", "master")
    # CAD-1 _check_sanity sentinels (so run_audit treats this as a source root).
    (repo / "plugin.yaml").write_text("name: ai-sdlc\n", encoding="utf-8")
    (repo / "INSTALL.md").write_text("# INSTALL\n", encoding="utf-8")
    (repo / "VERSION").write_text("0.84.0\n", encoding="utf-8")
    (repo / "agents").mkdir()
    (repo / "agents" / "critique.md").write_text("# critique — base\n", encoding="utf-8")
    (repo / "methodology-changelog.md").write_text("# changelog — base\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "base")
    return repo


def _seed_claude_dir(tmp_path: Path, critique_content: str) -> Path:
    """A fake ~/.claude/ with a (possibly divergent) installed agents/critique.md."""
    claude = tmp_path / "claude"
    (claude / "agents").mkdir(parents=True)
    (claude / "agents" / "critique.md").write_text(critique_content, encoding="utf-8")
    return claude


def test_content_gate_unmodified_vs_base_is_external(isolated_repo: Path):
    # AC1: on a slice branch that did NOT touch the source → not-modified →
    # an installed divergence is a sibling's forward-sync (external/WARN).
    _git(isolated_repo, "switch", "-c", "slice/117-x")
    # slice edits something ELSE, not critique.md
    (isolated_repo / "other.txt").write_text("slice work\n", encoding="utf-8")
    _git(isolated_repo, "add", "-A")
    _git(isolated_repo, "commit", "-m", "slice work, untouched critique")
    assert slice_modified_source(isolated_repo, _CRITIQUE_REL) is False


def test_content_gate_slice_edited_source_is_strict(isolated_repo: Path):
    # AC2 must-not-mask: the slice DID edit the source vs base → self-caused → HALT.
    _git(isolated_repo, "switch", "-c", "slice/117-x")
    (isolated_repo / "agents" / "critique.md").write_text(
        "# critique — EDITED by this slice\n", encoding="utf-8"
    )
    _git(isolated_repo, "add", "-A")
    _git(isolated_repo, "commit", "-m", "slice edits critique")
    assert slice_modified_source(isolated_repo, _CRITIQUE_REL) is True


def test_content_gate_on_default_branch_is_strict(isolated_repo: Path):
    # round-1 M1 guard: on the default branch (no slice) → strict True, so a
    # real install divergence on master still HALTs (never masked).
    assert slice_modified_source(isolated_repo, _CRITIQUE_REL) is True


def test_content_gate_detached_head_is_strict(isolated_repo: Path):
    # round-1 M1: detached HEAD (rebase / commit-slice --merge) → strict True.
    head = subprocess.run(
        ["git", "-C", str(isolated_repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    _git(isolated_repo, "checkout", head)  # detach
    assert slice_modified_source(isolated_repo, _CRITIQUE_REL) is True


def test_content_gate_path_absent_at_base_is_strict(isolated_repo: Path):
    # round-1 M5: a source newly added on the slice branch (absent at base) →
    # rc!=0 from `git show <base>:<path>` → strict True.
    _git(isolated_repo, "switch", "-c", "slice/117-x")
    (isolated_repo / "brand-new.md").write_text("new\n", encoding="utf-8")
    _git(isolated_repo, "add", "-A")
    _git(isolated_repo, "commit", "-m", "add new file")
    assert slice_modified_source(isolated_repo, "brand-new.md") is True


def test_content_gate_non_git_dir_fails_closed(tmp_path: Path):
    # round-1 M5: not a git repo (git fails) → fail-closed strict True.
    plain = tmp_path / "plain"
    plain.mkdir()
    (plain / "agents").mkdir()
    (plain / "agents" / "critique.md").write_text("x\n", encoding="utf-8")
    assert slice_modified_source(plain, _CRITIQUE_REL) is True


def test_content_gate_unmodified_with_crlf_only_diff_is_external(isolated_repo: Path):
    # EOL-DRIFT-1: a CRLF-only working-tree difference vs an LF base is NOT a
    # slice modification (normalize both) → external, not strict.
    _git(isolated_repo, "switch", "-c", "slice/117-x")
    (isolated_repo / "other.txt").write_text("w\n", encoding="utf-8")
    _git(isolated_repo, "add", "-A")
    _git(isolated_repo, "commit", "-m", "slice work")
    # rewrite critique.md with CRLF but identical content
    (isolated_repo / "agents" / "critique.md").write_bytes(b"# critique \xe2\x80\x94 base\r\n")
    assert slice_modified_source(isolated_repo, _CRITIQUE_REL) is False


def test_non_ascii_blob_byte_mode(isolated_repo: Path):
    # round-1 M4 / AP-7: a non-ASCII source (em-dash) must not crash the
    # byte-mode `git show` decode path; unmodified → external.
    _git(isolated_repo, "switch", "-c", "slice/117-x")
    (isolated_repo / "other.txt").write_text("w\n", encoding="utf-8")
    _git(isolated_repo, "add", "-A")
    _git(isolated_repo, "commit", "-m", "slice work")
    # base agents/critique.md already contains an em-dash ("—"); leave it
    # byte-identical on the slice branch.
    assert slice_modified_source(isolated_repo, _CRITIQUE_REL) is False


# --------------------------------------------------------------------------
# Gate integration — CAD-1 (content gate): external-drift vs HALT
# --------------------------------------------------------------------------

def test_cad1_sibling_drift_is_external_warn(isolated_repo: Path, tmp_path: Path):
    # AC1 + AC3: on a slice branch that did NOT edit critique.md, an installed
    # divergence (a sibling forward-synced ~/.claude/) → external-drift WARN,
    # exit 0, NO blocking violation.
    _git(isolated_repo, "switch", "-c", "slice/117-x")
    (isolated_repo / "other.txt").write_text("slice work\n", encoding="utf-8")
    _git(isolated_repo, "add", "-A")
    _git(isolated_repo, "commit", "-m", "work, critique untouched")
    claude = _seed_claude_dir(tmp_path, "# critique — SIBLING forward-synced newer\n")
    result = cad.run_audit(repo_root=isolated_repo, claude_dir=claude)
    assert result.external_drift is True
    assert result.violations == []


def test_cad1_self_drift_still_halts(isolated_repo: Path, tmp_path: Path):
    # AC2 must-not-mask: the slice EDITED critique.md but the installed copy
    # differs (forgot to forward-sync) → self-caused content-drift HALT.
    _git(isolated_repo, "switch", "-c", "slice/117-x")
    (isolated_repo / "agents" / "critique.md").write_text(
        "# critique — EDITED by this slice\n", encoding="utf-8"
    )
    _git(isolated_repo, "add", "-A")
    _git(isolated_repo, "commit", "-m", "slice edits critique")
    claude = _seed_claude_dir(tmp_path, "# critique — base\n")  # installed = stale base
    result = cad.run_audit(repo_root=isolated_repo, claude_dir=claude)
    assert result.external_drift is False
    assert any(v.kind == "content-drift" for v in result.violations)


def test_cad1_clean_when_in_repo_equals_installed(isolated_repo: Path, tmp_path: Path):
    # No divergence → neither external-drift nor a violation (byte-equal).
    _git(isolated_repo, "switch", "-c", "slice/117-x")
    (isolated_repo / "other.txt").write_text("w\n", encoding="utf-8")
    _git(isolated_repo, "add", "-A")
    _git(isolated_repo, "commit", "-m", "work")
    claude = _seed_claude_dir(tmp_path, "# critique — base\n")  # == in-repo
    result = cad.run_audit(repo_root=isolated_repo, claude_dir=claude)
    assert result.external_drift is False
    assert result.violations == []


# --------------------------------------------------------------------------
# Gate integration — AVFS-1 (version gate): version-ordering
# --------------------------------------------------------------------------

def test_avfs1_installed_newer_is_external(isolated_repo: Path, tmp_path: Path):
    # AC1: installed ai-sdlc-VERSION strictly newer than in-repo → external WARN.
    installed = tmp_path / "ai-sdlc-VERSION"
    installed.write_text("0.85.0\n", encoding="utf-8")
    r = avfs.check(isolated_repo, installed=installed)
    assert r.status == "external-drift"
    assert r.exit_code == 0


def test_avfs1_installed_older_still_halts(isolated_repo: Path, tmp_path: Path):
    # AC2: installed older than in-repo → self bumped-but-unsynced → HALT.
    installed = tmp_path / "ai-sdlc-VERSION"
    installed.write_text("0.83.0\n", encoding="utf-8")
    r = avfs.check(isolated_repo, installed=installed)
    assert r.status == "drift"
    assert r.exit_code == 1


def test_avfs1_unparseable_installed_halts(isolated_repo: Path, tmp_path: Path):
    # M-add-1: a non-semver installed value → None → strict HALT (never mask).
    installed = tmp_path / "ai-sdlc-VERSION"
    installed.write_text("not-a-version\n", encoding="utf-8")
    r = avfs.check(isolated_repo, installed=installed)
    assert r.status == "drift"
    assert r.exit_code == 1


# --------------------------------------------------------------------------
# Gate integration — TVFS-1 (version gate): version-ordering via resolver seam
# --------------------------------------------------------------------------

def test_tvfs1_installed_newer_is_external(isolated_repo: Path):
    # AC1: venv package strictly newer than in-repo VERSION → external WARN.
    r = tvfs.check(isolated_repo, installed_version_resolver=lambda: "0.85.0")
    assert r.status == "external-drift"
    assert r.exit_code == 0


def test_tvfs1_stale_venv_older_still_halts(isolated_repo: Path):
    # AC2 + M-add-2: a stale venv OLDER than the source must HALT (must-not-mask).
    r = tvfs.check(isolated_repo, installed_version_resolver=lambda: "0.20.0")
    assert r.status == "drift"
    assert r.exit_code == 1


# --------------------------------------------------------------------------
# Gate integration — MCFS-1 (content gate): merge-base
# --------------------------------------------------------------------------

def test_mcfs1_sibling_drift_is_external(isolated_repo: Path, tmp_path: Path):
    # AC1: slice didn't edit the changelog; installed differs (sibling) → external.
    _git(isolated_repo, "switch", "-c", "slice/117-x")
    (isolated_repo / "other.txt").write_text("w\n", encoding="utf-8")
    _git(isolated_repo, "add", "-A")
    _git(isolated_repo, "commit", "-m", "work, changelog untouched")
    installed = tmp_path / "changelog.md"
    installed.write_text("# changelog — SIBLING forward-synced newer\n", encoding="utf-8")
    r = mcfs.check(isolated_repo, installed=installed)
    assert r.status == "external-drift"
    assert r.exit_code == 0


def test_mcfs1_self_edit_still_halts(isolated_repo: Path, tmp_path: Path):
    # AC2: slice edited the changelog but didn't forward-sync → HALT.
    _git(isolated_repo, "switch", "-c", "slice/117-x")
    (isolated_repo / "methodology-changelog.md").write_text(
        "# changelog — EDITED by this slice\n", encoding="utf-8"
    )
    _git(isolated_repo, "add", "-A")
    _git(isolated_repo, "commit", "-m", "slice edits changelog")
    installed = tmp_path / "changelog.md"
    installed.write_text("# changelog — base\n", encoding="utf-8")  # stale base
    r = mcfs.check(isolated_repo, installed=installed)
    assert r.status == "drift"
    assert r.exit_code == 1


# --------------------------------------------------------------------------
# AC3 / AC4 roll-ups
# --------------------------------------------------------------------------

def test_all_four_gates_apply_mechanism():
    # AC3 (WIRE-1 consumer test): each gate routes through its discriminator —
    # content gates → slice_modified_source; version gates → installed_is_sibling_ahead.
    import inspect
    assert "slice_modified_source" in inspect.getsource(cad)
    assert "slice_modified_source" in inspect.getsource(mcfs)
    assert "installed_is_sibling_ahead" in inspect.getsource(avfs)
    assert "installed_is_sibling_ahead" in inspect.getsource(tvfs)


def test_exit_code_contract_preserved(isolated_repo: Path, tmp_path: Path):
    # AC4: external-drift → exit 0; self-drift → exit 1; synced → exit 0.
    newer = tmp_path / "newer"; newer.write_text("0.85.0\n", encoding="utf-8")
    older = tmp_path / "older"; older.write_text("0.83.0\n", encoding="utf-8")
    same = tmp_path / "same"; same.write_text("0.84.0\n", encoding="utf-8")
    assert avfs.check(isolated_repo, installed=newer).exit_code == 0   # external WARN
    assert avfs.check(isolated_repo, installed=older).exit_code == 1   # self-drift HALT
    assert avfs.check(isolated_repo, installed=same).exit_code == 0    # synced


# --------------------------------------------------------------------------
# Breadcrumb sink (round-2 M1) — recoverability to the external store
# --------------------------------------------------------------------------

def test_breadcrumb_emits_to_external_store(tmp_path: Path, monkeypatch):
    # round-2 M1: external-drift writes a recoverable breadcrumb to a
    # VAULT_ROOT-rooted sink (NOT a worktree-relative/gitignored path). Patch the
    # module's own VAULT_ROOT binding (frozen-at-import) to an isolated tmp dir.
    from tools import _forward_sync_breadcrumb as bc

    monkeypatch.setattr(bc, "VAULT_ROOT", tmp_path)
    bc.emit_external_drift("CAD-1", "agents/critique.md", "sibling forward-synced newer")
    sink = tmp_path / "forward-sync-external-drift-log.md"
    assert sink.exists()
    content = sink.read_text(encoding="utf-8")
    assert "CAD-1" in content
    assert "agents/critique.md" in content
    assert "external-drift" in content


# --------------------------------------------------------------------------
# TF-1 flip-straggler fix (slice-117 / ADR-108): test_first_audit._find_repo_root
# resolves an EXTERNAL-vault slice folder to the cwd worktree repo (parity with
# BRANCH-1/CRP-1/DCE-1's slice-115 resolve_repo_root_for_slice migration).
# --------------------------------------------------------------------------

def test_tf1_find_repo_root_external_vault_fallback(tmp_path: Path, monkeypatch):
    from tools import _vault_git
    from tools import test_first_audit as tfa

    # An external vault store (NO .git/VERSION anywhere above the slice folder).
    ext_vault = tmp_path / "ext_vault"
    slice_dir = ext_vault / "slices" / "slice-999-x"
    slice_dir.mkdir(parents=True)
    brief = slice_dir / "mission-brief.md"
    brief.write_text("# brief\n", encoding="utf-8")
    # A worktree repo, used as the invocation cwd.
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)

    monkeypatch.setattr(_vault_git, "VAULT_ROOT", ext_vault)
    monkeypatch.chdir(repo)

    # Pre-flip walk-up finds no sentinel → the new fallback maps the external
    # slice folder to the cwd worktree repo (NOT the old slice-dir fallback).
    assert tfa._find_repo_root(brief) == repo.resolve()


def test_tf1_find_repo_root_in_repo_unchanged(tmp_path: Path):
    from tools import test_first_audit as tfa

    # A normal in-repo slice (has a .git ancestor) resolves to that repo —
    # the fallback must not change pre-flip / tmp-fixture behavior.
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    slice_dir = repo / "architecture" / "slices" / "slice-1-x"
    slice_dir.mkdir(parents=True)
    brief = slice_dir / "mission-brief.md"
    brief.write_text("# brief\n", encoding="utf-8")
    assert tfa._find_repo_root(brief) == repo.resolve()
