"""Tests for tools.critique_agent_drift_audit (CAD-1) + slice-007 prose contract.

Validates that the audit correctly:
- Reports clean (exit 0) when in-repo `agents/critique.md` and installed
  `~/.claude/agents/critique.md` have matching sha256.
- Reports content-drift (exit 1) when sha256 differs, with both paths AND
  both hashes in the output (so user can act on the failure).
- Reports path-missing (exit 2) when either file is absent.
- Refuses with usage-error (exit 2) when `--repo-root` is not an AI SDLC
  source root (no plugin.yaml + INSTALL.md) — Critic M3 sanity check
  preventing accidental comparison against `build/lib/` shadow.

Plus prose pin for `skills/critic-calibrate/SKILL.md` instructing in-repo
canonical edits with forward-sync (Critic M2 substring-only contract;
positive + negative substrings).

Rule reference: CAD-1.
"""
import subprocess
import sys
from pathlib import Path

import pytest

from tests.methodology.conftest import REPO_ROOT


# --- Fixture helpers ---

def _seed_repo_root(repo: Path, critique_content: bytes) -> Path:
    """Build a fake AI SDLC source root with plugin.yaml + INSTALL.md sentinels
    plus an agents/critique.md file containing the given bytes."""
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "plugin.yaml").write_text("name: ai-sdlc\n", encoding="utf-8")
    (repo / "INSTALL.md").write_text("# INSTALL\n", encoding="utf-8")
    (repo / "agents").mkdir(parents=True, exist_ok=True)
    (repo / "agents" / "critique.md").write_bytes(critique_content)
    return repo


def _seed_claude_dir(claude: Path, critique_content: bytes) -> Path:
    """Build a fake ~/.claude/ tree with agents/critique.md."""
    (claude / "agents").mkdir(parents=True, exist_ok=True)
    (claude / "agents" / "critique.md").write_bytes(critique_content)
    return claude


def _run_audit(repo_root: Path, claude_dir: Path) -> subprocess.CompletedProcess:
    """Invoke the audit via subprocess (tests CLI surface, not just import)."""
    return subprocess.run(
        [
            sys.executable, "-m", "tools.critique_agent_drift_audit",
            "--repo-root", str(repo_root),
            "--claude-dir", str(claude_dir),
        ],
        capture_output=True, text=True, encoding="utf-8",
    )


# --- AC #1: real-repo byte-equality (post-build state) ---

def test_in_repo_and_installed_critique_agent_are_content_equal():
    """Post-build: real in-repo agents/critique.md == installed ~/.claude/agents/critique.md.

    Defect class (per slice-006 B1 + slice-007 CAD-1): every /critic-calibrate
    ACCEPTED proposal that follows the slice prose creates content drift between
    in-repo (canonical) and installed (working) copies. This test is the
    structural gate that catches drift in the live repo.

    Rule reference: CAD-1, AC #1.
    """
    result = subprocess.run(
        [sys.executable, "-m", "tools.critique_agent_drift_audit"],
        capture_output=True, text=True, encoding="utf-8",
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"CAD-1 audit reports drift between in-repo and installed "
        f"agents/critique.md.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# --- AC #2: drift detection fires on artificial byte flip ---

def test_drift_detection_fires_on_artificial_byte_flip(tmp_path: Path):
    """Audit reports exit 1 with content-drift when the two files differ.

    Per Critic M1: fixture isolation via tmp_path; never mutates real files.
    Per slice-005 lesson: pin specific failure signature (content-drift in
    output) — not just exit code.

    Rule reference: CAD-1, AC #2.
    """
    repo = _seed_repo_root(tmp_path / "repo", b"# critique agent v1\n")
    claude = _seed_claude_dir(tmp_path / "claude", b"# critique agent v2 (drifted)\n")

    result = _run_audit(repo, claude)
    assert result.returncode == 1, (
        f"expected exit 1 (content-drift) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "content-drift" in (result.stdout + result.stderr), (
        f"output missing 'content-drift' substring; full output:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    output = result.stdout + result.stderr
    assert str(repo / "agents" / "critique.md") in output, (
        "drift report must name the in-repo path"
    )
    assert str(claude / "agents" / "critique.md") in output, (
        "drift report must name the installed path"
    )


# --- AC #3a: prose-pin (Critic M2 substring-only, NO line-range) ---

def test_critic_calibrate_skill_prose_instructs_in_repo_canonical_with_forward_sync():
    """skills/critic-calibrate/SKILL.md prose names in-repo as canonical
    with forward-sync, AND no longer says 'edit ~/.claude/agents/critique.md'.

    Per Critic M2: substring-only assertion (NO line-range pin); positive
    AND negative substrings — the negative catches regression where a future
    edit reverts the in-repo-canonical instruction.

    Rule reference: CAD-1, AC #3a.
    """
    skill_md = (REPO_ROOT / "skills" / "critic-calibrate" / "SKILL.md").read_text(encoding="utf-8")

    # Positive substrings (corrected prose)
    assert "in-repo agents/critique.md" in skill_md, (
        "skill prose must name 'in-repo agents/critique.md' as canonical source"
    )
    assert "forward-sync" in skill_md, (
        "skill prose must instruct manual forward-sync to ~/.claude/"
    )
    assert "tools.critique_agent_drift_audit" in skill_md, (
        "skill prose must reference the new audit for post-edit verification"
    )

    # Negative substring: the unique signature of the OLD prose block that
    # caused slice-006's drift class — "To apply, edit ~/.claude/agents/critique.md"
    # (this exact phrasing appeared only in the removed prose block; it does
    # NOT appear in the line-99 explanatory text "skill PRODUCES proposals.
    # It does NOT edit `~/.claude/agents/critique.md` itself" which uses
    # backticks and a different surrounding phrasing).
    assert "To apply, edit ~/.claude/agents/critique.md" not in skill_md, (
        "skill prose still contains the OLD 'To apply, edit ~/.claude/agents/"
        "critique.md' instruction; this is the structural cause of the "
        "in-repo↔installed drift class. Post-CAD-1 prose must point at in-repo "
        "as canonical with forward-sync. Regression detected."
    )


# --- AC #3b: audit CLI exit codes (parametrized: clean / drift / missing) ---

def test_critique_agent_drift_audit_cli_exits_0_on_clean_1_on_drift_2_on_missing(tmp_path: Path):
    """Audit CLI honors the exit-code contract: 0 clean / 1 drift / 2 missing.

    Per Critic M3 expanded error model. Distinguishable failure signatures
    pinned via stdout/stderr substring assertions.

    Rule reference: CAD-1, AC #3b.
    """
    # Clean: identical content in both
    repo_clean = _seed_repo_root(tmp_path / "repo_clean", b"# v1\n")
    claude_clean = _seed_claude_dir(tmp_path / "claude_clean", b"# v1\n")
    r_clean = _run_audit(repo_clean, claude_clean)
    assert r_clean.returncode == 0, (
        f"clean state: expected exit 0 but got {r_clean.returncode}\n"
        f"{r_clean.stdout}\n{r_clean.stderr}"
    )

    # Drift: different content
    repo_drift = _seed_repo_root(tmp_path / "repo_drift", b"# v1\n")
    claude_drift = _seed_claude_dir(tmp_path / "claude_drift", b"# v2\n")
    r_drift = _run_audit(repo_drift, claude_drift)
    assert r_drift.returncode == 1, (
        f"drift state: expected exit 1 but got {r_drift.returncode}\n"
        f"{r_drift.stdout}\n{r_drift.stderr}"
    )

    # Missing installed
    repo_only = _seed_repo_root(tmp_path / "repo_only", b"# v1\n")
    claude_missing = tmp_path / "claude_missing"
    claude_missing.mkdir(parents=True)  # exists, but no agents/critique.md
    r_missing = _run_audit(repo_only, claude_missing)
    assert r_missing.returncode == 2, (
        f"path-missing state: expected exit 2 but got {r_missing.returncode}\n"
        f"{r_missing.stdout}\n{r_missing.stderr}"
    )
    assert "path-missing" in (r_missing.stdout + r_missing.stderr), (
        "path-missing exit must include 'path-missing' substring"
    )


# --- AC #3c: --repo-root sanity-check refusal (Critic M3) ---

def test_repo_root_without_plugin_yaml_or_install_md_exits_usage_error(tmp_path: Path):
    """Audit refuses when --repo-root is not an AI SDLC source root.

    Critic M3 sanity check: prevents accidental comparison against stale
    `build/lib/` shadow or arbitrary directory. Tests by pointing
    --repo-root at a tmp_path with no plugin.yaml and no INSTALL.md.

    Rule reference: CAD-1, AC #3c.
    """
    # tmp_path exists but contains neither plugin.yaml nor INSTALL.md.
    # Seed only an agents/critique.md so the failure is unambiguously the
    # sanity check (not path-missing).
    (tmp_path / "agents").mkdir(parents=True)
    (tmp_path / "agents" / "critique.md").write_bytes(b"# v1\n")
    claude = _seed_claude_dir(tmp_path / "claude", b"# v1\n")

    result = _run_audit(tmp_path, claude)
    assert result.returncode == 2, (
        f"expected exit 2 (usage-error sanity refusal) but got {result.returncode}\n"
        f"{result.stdout}\n{result.stderr}"
    )
    assert "AI SDLC source root" in (result.stdout + result.stderr), (
        f"sanity-check refusal must include 'AI SDLC source root' substring "
        f"so the user knows what's wrong; full output:\n"
        f"{result.stdout}\n{result.stderr}"
    )


# --- Slice-021 / BRANCH-1 CAD-1 vacuous-clean check ---


def test_critique_agent_drift_audit_clean_at_slice_021_ship():
    """At slice-021 ship, CAD-1 audit MUST be clean on the actual repo —
    slice-021 does NOT touch `agents/critique.md` (Critic-agent content-
    equality discipline invariant preserved at slice-017 ship hash).

    Defect class: a future slice accidentally edits agents/critique.md
    (e.g., via /critic-calibrate ACCEPTED proposal); CAD-1 byte-equality
    diverges between in-repo and installed.
    Rule reference: CAD-1 (slice-021 AC #5 + Must-not-defer).
    """
    result = subprocess.run(
        [sys.executable, "-m", "tools.critique_agent_drift_audit", "--repo-root", str(REPO_ROOT)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"CAD-1 audit returned non-zero at slice-021 ship — slice-021 must NOT "
        f"touch agents/critique.md per Must-not-defer; output:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )


# --- Slice-033 / EOL-DRIFT-1: CAD-1 is EOL-agnostic (AC2 complement) ---


def test_cad1_audit_treats_crlf_and_lf_identical_content_as_clean(
    tmp_path: Path,
):
    """CAD-1 audit reports CLEAN (exit 0) when in-repo is CRLF and installed
    is LF but the content is identical after line-ending normalization.

    Per slice-033 EOL-DRIFT-1 / ADR-033: this is the EOL-only COMPLEMENT to
    `test_drift_detection_fires_on_artificial_byte_flip` (which proves
    genuine `# v1`/`# v2` divergence still exit 1 — the must-not-mask-real-
    drift proof, AC2(b)). Together they pin both halves of the invariant:
    CRLF<->LF is not drift; genuine content divergence still is.

    Defect class (R-5): Windows core.autocrlf=true checks out
    agents/critique.md CRLF while the installed copy is LF; the pre-slice-033
    raw-byte `_sha256_of` false-FAILed (exit 1) on byte-identical content.

    Rule reference: EOL-DRIFT-1 (slice-033; ADR-033).
    """
    body = b"# critique agent\n\nDimension 1: assumptions.\nDimension 2: edges.\n"
    repo = _seed_repo_root(tmp_path / "repo", body.replace(b"\n", b"\r\n"))  # CRLF
    claude = _seed_claude_dir(tmp_path / "claude", body)  # LF

    result = _run_audit(repo, claude)
    assert result.returncode == 0, (
        f"CAD-1 must be EOL-agnostic (EOL-DRIFT-1): CRLF in-repo vs LF "
        f"installed with identical normalized content is NOT drift, expected "
        f"exit 0 but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
