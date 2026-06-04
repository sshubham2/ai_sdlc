"""PSQ-2 claim machinery tests (slice-072; ADR-067; methodology v0.71.0).

Covers AC1-AC4 of slice-072-add-psq-2-claim-machinery: schema additivity
(claimed/unclaimed/CRLF/forward-compat), CLI git-config + atomic write +
configured-empty + --queue override + cp1252, release + force-claim
semantics + bare-claim refusal + release-on-unknown typo-rejection,
/slice Step 6.5 claim-preservation merge + drop-on-removal.

Per TF-1 plan in mission-brief.md L26-48 (18 rows total = 15 here + 1 in
test_utf8_stdout_regression.py + 2 in test_methodology_changelog.py).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tools import slice_queue_claim
from tools.slice_queue_claim import (
    ClaimUsageError,
    apply_claim,
    apply_release,
    parse_queue_text,
    read_git_config_user,
)
import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py
import tools.slice_queue_writer as _sqw
from tools.slice_queue_writer import write_slice_queue

# slice-110 / [[ADR-101]]: pin VAULT_ROOT (in-tree relative) + re-derive the frozen
# index/slices constants so write_slice_queue writes each test's own
# <repo>/architecture/slice-queue.md under default AND an external AI_SDLC_VAULT_ROOT
# override (the flip simulation).
_pin_vault = vi.autouse_pin(
    _sqw,
    derived=[
        (_sqw, "_INDEX_MD_REL", lambda vr: vr / "slices" / "_index.md"),
        (_sqw, "_SLICES_DIR_REL", lambda vr: vr / "slices"),
    ],
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture
def isolated_git_env(tmp_path, monkeypatch):
    """Set up a tmp git repo with controllable user.name + user.email.

    Per design.md §"Test seams": uses GIT_CONFIG_NOSYSTEM to ignore the
    machine's global git config, then creates a tmp repo with --local
    config that the test can control.
    """
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("HOME", str(tmp_path))  # neutralize ~/.gitconfig
    monkeypatch.setenv("USERPROFILE", str(tmp_path))  # Windows analogue
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "nonexistent"))
    repo = tmp_path / "fake-repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    subprocess.run(["git", "init", "-q"], check=True)
    return repo


def _set_local_git_user(name: str | None, email: str | None) -> None:
    if name is not None:
        subprocess.run(["git", "config", "--local", "user.name", name], check=True)
    if email is not None:
        subprocess.run(["git", "config", "--local", "user.email", email], check=True)


def _make_queue(claimed: bool = False, extras: bool = False) -> str:
    """Build a small queue fixture text."""
    head = (
        "# Slice queue\n"
        "\n"
        "_Generated: 2026-05-27T00:00:00+00:00 by /slice during slice-072 definition_\n"
        "\n"
        "## Candidates\n"
        "\n"
    )
    entry_a_lines = [
        "### candidate-a",
        "",
        "- **Source:** test fixture",
        "- **Blast-radius:** `tools/foo.py`",
        "- **Parallel-safety:** NON-OVERLAPPING",
        "- **Effort:** SMALL",
        "- **Risk-retired:** LOW",
    ]
    if claimed:
        entry_a_lines.extend([
            "- **Claimed-by:** Alice <alice@example.com>",
            "- **Claimed-at:** 2026-05-27T12:00:00+00:00",
        ])
    if extras:
        entry_a_lines.append("- **Claim-rationale:** future-extra-field-line")
    entry_a_lines.append("")
    entry_b_lines = [
        "### candidate-b",
        "",
        "- **Source:** test fixture B",
        "- **Blast-radius:** `tools/bar.py`",
        "- **Parallel-safety:** NON-OVERLAPPING",
        "- **Effort:** MEDIUM",
        "- **Risk-retired:** MEDIUM",
        "",
    ]
    return head + "\n".join(entry_a_lines) + "\n" + "\n".join(entry_b_lines) + "\n"


# ---------------------------------------------------------------------
# AC1: Schema additivity + CRLF + forward-compat
# ---------------------------------------------------------------------


def test_schema_appends_claim_fields_after_risk_retired_when_claimed():
    text = _make_queue(claimed=False)
    new = apply_claim(text, "candidate-a", "Bob <bob@example.com>", "2026-05-27T13:00:00+00:00", force=False)
    # Find Risk-retired + Claimed-by + Claimed-at ordering for candidate-a.
    lines = new.split("\n")
    header_idx = lines.index("### candidate-a")
    # Find Risk-retired within the entry (before next ### header).
    retired_idx = next(
        i for i in range(header_idx, len(lines))
        if lines[i].startswith("- **Risk-retired:**")
    )
    # Claimed-by should be retired_idx + 1; Claimed-at retired_idx + 2.
    assert lines[retired_idx + 1] == "- **Claimed-by:** Bob <bob@example.com>"
    assert lines[retired_idx + 2] == "- **Claimed-at:** 2026-05-27T13:00:00+00:00"
    # Followed by blank (entry separator).
    assert lines[retired_idx + 3] == ""


def test_schema_omits_claim_fields_when_unclaimed():
    text = _make_queue(claimed=False)
    entries = parse_queue_text(text)
    assert "candidate-a" in entries
    assert "claimed_by" not in entries["candidate-a"]
    assert "claimed_at" not in entries["candidate-a"]
    assert entries["candidate-a"]["_extra_field_lines"] == []


def test_parse_queue_text_accepts_crlf_input():
    """Critic M1 ACCEPTED-FIXED: CRLF tolerance."""
    text_lf = _make_queue(claimed=True)
    text_crlf = text_lf.replace("\n", "\r\n")
    entries_lf = parse_queue_text(text_lf)
    entries_crlf = parse_queue_text(text_crlf)
    assert entries_crlf == entries_lf
    assert entries_crlf["candidate-a"]["claimed_by"] == "Alice <alice@example.com>"


def test_parse_queue_text_preserves_unknown_field_lines_on_roundtrip():
    """Critic M3 ACCEPTED-FIXED: forward-compat _extra_field_lines pass-through."""
    text = _make_queue(claimed=True, extras=True)
    entries = parse_queue_text(text)
    extras = entries["candidate-a"]["_extra_field_lines"]
    assert any("Claim-rationale" in line for line in extras), \
        f"expected Claim-rationale in extras, got {extras!r}"


def test_parse_queue_text_returns_all_entries_including_unclaimed():
    """Meta-Critic m-add-2 ACCEPTED-FIXED: all entries appear; unclaimed have absent claim keys."""
    text = _make_queue(claimed=False)
    entries = parse_queue_text(text)
    assert set(entries.keys()) == {"candidate-a", "candidate-b"}
    for name in ("candidate-a", "candidate-b"):
        assert "_extra_field_lines" in entries[name]
        assert "claimed_by" not in entries[name]


def test_parse_queue_text_partial_claim_block_raises_malformed():
    """Critic M3 + design L150: PARTIAL known claim block → ClaimUsageError."""
    text = _make_queue(claimed=False)
    # Insert only Claimed-by, not Claimed-at.
    text = text.replace(
        "- **Risk-retired:** LOW\n",
        "- **Risk-retired:** LOW\n- **Claimed-by:** Alice <alice@x.com>\n",
    )
    with pytest.raises(ClaimUsageError, match="malformed claim block for candidate-a"):
        parse_queue_text(text)


# ---------------------------------------------------------------------
# AC2: CLI / git config / atomic write / --queue / cp1252
# ---------------------------------------------------------------------


def test_claim_cli_writes_user_name_and_email_from_git_config(isolated_git_env, tmp_path):
    """AC2: claim CLI uses git config user.name + user.email."""
    _set_local_git_user("CLITest", "cli@example.com")
    queue_path = tmp_path / "q.md"
    queue_path.write_text(_make_queue(claimed=False), encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [PY, "-m", "tools.slice_queue_claim", "--claim", "candidate-a", "--queue", str(queue_path)],
        capture_output=True, text=True, cwd=str(isolated_git_env), env=env,
    )
    assert proc.returncode == 0, f"expected exit 0, got {proc.returncode}: {proc.stderr}"
    text = queue_path.read_text(encoding="utf-8")
    assert "- **Claimed-by:** CLITest cli@example.com" in text
    assert "- **Claimed-at:** " in text


def test_claim_cli_exits_2_on_missing_user_name_or_user_email(isolated_git_env, tmp_path):
    """AC2: absent git config user.name OR user.email → exit 2."""
    _set_local_git_user(None, "only@email.com")  # name unset
    queue_path = tmp_path / "q.md"
    queue_path.write_text(_make_queue(), encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [PY, "-m", "tools.slice_queue_claim", "--claim", "candidate-a", "--queue", str(queue_path)],
        capture_output=True, text=True, cwd=str(isolated_git_env), env=env,
    )
    assert proc.returncode == 2
    assert "user.name" in proc.stderr


def test_claim_cli_exits_2_on_configured_empty_user_name(isolated_git_env, tmp_path):
    """Critic m2 ACCEPTED-FIXED: configured-empty `user.name = ""` → exit 2."""
    _set_local_git_user("", "only@email.com")  # name configured-empty
    queue_path = tmp_path / "q.md"
    queue_path.write_text(_make_queue(), encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [PY, "-m", "tools.slice_queue_claim", "--claim", "candidate-a", "--queue", str(queue_path)],
        capture_output=True, text=True, cwd=str(isolated_git_env), env=env,
    )
    assert proc.returncode == 2
    assert "user.name" in proc.stderr


def test_claim_cli_atomic_write_via_tmp_sibling_and_os_replace(
    isolated_git_env, tmp_path, monkeypatch,
):
    """AC2: atomic write via .tmp sibling + os.replace (mid-call crash leaves original intact)."""
    _set_local_git_user("Test", "t@x.com")
    queue_path = tmp_path / "q.md"
    original = _make_queue(claimed=False)
    queue_path.write_text(original, encoding="utf-8")
    # Monkeypatch os.replace to raise mid-call.
    real_replace = os.replace

    def raising_replace(src, dst):
        raise OSError("simulated mid-call failure")

    monkeypatch.setattr("tools.slice_queue_claim.os.replace", raising_replace)
    name, email = "Test", "t@x.com"
    with pytest.raises(OSError):
        slice_queue_claim._atomic_write_text(queue_path, "MUTATED")
    # Original file unchanged.
    assert queue_path.read_text(encoding="utf-8") == original


def test_claim_cli_uses_queue_path_override_when_provided(isolated_git_env, tmp_path):
    """Critic m3 ACCEPTED-FIXED: --queue routes writes to the override path, not default."""
    _set_local_git_user("UserA", "ua@x.com")
    custom_queue = tmp_path / "custom_queue.md"
    custom_queue.write_text(_make_queue(claimed=False), encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [PY, "-m", "tools.slice_queue_claim", "--claim", "candidate-a", "--queue", str(custom_queue)],
        capture_output=True, text=True, cwd=str(isolated_git_env), env=env,
    )
    assert proc.returncode == 0
    assert "Claimed-by:" in custom_queue.read_text(encoding="utf-8")


# ---------------------------------------------------------------------
# AC3: Release / force-claim / bare-claim refusal
# ---------------------------------------------------------------------


def test_release_removes_both_claim_field_lines():
    text = _make_queue(claimed=True)
    new = apply_release(text, "candidate-a")
    assert "- **Claimed-by:**" not in new
    assert "- **Claimed-at:**" not in new
    # Risk-retired still present.
    assert "- **Risk-retired:** LOW" in new


def test_release_on_unknown_candidate_exits_2(isolated_git_env, tmp_path):
    """Critic M2 ACCEPTED-FIXED: --release on missing candidate → exit 2 typo-rejection."""
    _set_local_git_user("Test", "t@x.com")
    queue_path = tmp_path / "q.md"
    queue_path.write_text(_make_queue(claimed=True), encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [PY, "-m", "tools.slice_queue_claim", "--release", "typo-candidate", "--queue", str(queue_path)],
        capture_output=True, text=True, cwd=str(isolated_git_env), env=env,
    )
    assert proc.returncode == 2
    assert "typo-candidate" in proc.stderr or "not found" in proc.stderr


def test_force_claim_overwrites_existing_claim():
    text = _make_queue(claimed=True)
    new = apply_claim(text, "candidate-a", "Carol <carol@y.com>", "2026-05-28T00:00:00+00:00", force=True)
    assert "- **Claimed-by:** Carol <carol@y.com>" in new
    assert "- **Claimed-at:** 2026-05-28T00:00:00+00:00" in new
    # Old claim removed.
    assert "Alice <alice@example.com>" not in new


def test_bare_claim_on_already_claimed_exits_2():
    text = _make_queue(claimed=True)
    with pytest.raises(ClaimUsageError, match="already claimed"):
        apply_claim(text, "candidate-a", "Dave <dave@z.com>", "2026-05-29T00:00:00+00:00", force=False)


# ---------------------------------------------------------------------
# AC4: /slice Step 6.5 claim-preservation merge
# ---------------------------------------------------------------------


def test_slice_step_6_5_regen_preserves_existing_claims(tmp_path):
    """AC4: claim survives across write_slice_queue regen byte-equal."""
    repo = tmp_path / "fake-repo"
    architecture = repo / "architecture"
    architecture.mkdir(parents=True)
    queue = architecture / "slice-queue.md"
    queue.write_text(_make_queue(claimed=True), encoding="utf-8")
    candidates = [
        {"name": "candidate-a", "source": "test fixture",
         "hint_files": [], "effort": "SMALL", "risk_retired": "LOW"},
        {"name": "candidate-b", "source": "test fixture B",
         "hint_files": [], "effort": "MEDIUM", "risk_retired": "MEDIUM"},
    ]
    write_slice_queue(
        repo_root=repo,
        candidates=candidates,
        active_slice_num=72,
        graph_path=None,
    )
    new_text = queue.read_text(encoding="utf-8")
    assert "- **Claimed-by:** Alice <alice@example.com>" in new_text
    assert "- **Claimed-at:** 2026-05-27T12:00:00+00:00" in new_text


def test_r_19_retired_in_risk_register():
    """AC5: R-19 status flipped mitigating → retired in risk-register.md.

    Per PSQ-2 / ADR-067 — claim machinery makes queue freshness a hint
    not a load-bearing collision-safety signal; R-19's Mitigating status
    is closed structurally. Verifies the R-19 entry carries
    `**Status**: retired` (NOT `mitigating`) AND a `**Retired**:` field-
    line citing slice-072.
    """
    risk_register = (REPO_ROOT / "architecture" / "risk-register.md").read_text(encoding="utf-8")
    r19_idx = risk_register.find("## R-19 ")
    assert r19_idx >= 0, "risk-register.md missing R-19 section"
    next_section = risk_register.find("\n## R-", r19_idx + 1)
    r19_section = (
        risk_register[r19_idx:next_section] if next_section > 0
        else risk_register[r19_idx:]
    )
    assert "**Status**: retired" in r19_section, (
        "R-19 status MUST be 'retired' post-slice-072 — PSQ-2 retires R-19 "
        "structurally per ADR-067 §Decision"
    )
    assert "**Status**: mitigating" not in r19_section, (
        "R-19 still carries the pre-slice-072 'mitigating' status — flip "
        "to 'retired' per slice-072 PSQ-2 retirement"
    )
    assert "**Retired**:" in r19_section, (
        "R-19 missing the **Retired**: field-line citing slice-072 + ADR-067"
    )
    assert "slice-072" in r19_section, (
        "R-19 retirement citation must reference slice-072"
    )
    assert "ADR-067" in r19_section, (
        "R-19 retirement citation must reference ADR-067 (the new ADR "
        "minting PSQ-2)"
    )


def test_claims_on_dropped_candidates_are_silently_discarded(tmp_path):
    """AC4: claim on a candidate NOT in the new top-10 is silently dropped."""
    repo = tmp_path / "fake-repo"
    architecture = repo / "architecture"
    architecture.mkdir(parents=True)
    queue = architecture / "slice-queue.md"
    queue.write_text(_make_queue(claimed=True), encoding="utf-8")
    # Regen with candidate-a dropped (only candidate-b survives).
    candidates = [
        {"name": "candidate-b", "source": "test fixture B",
         "hint_files": [], "effort": "MEDIUM", "risk_retired": "MEDIUM"},
    ]
    write_slice_queue(
        repo_root=repo,
        candidates=candidates,
        active_slice_num=72,
        graph_path=None,
    )
    new_text = queue.read_text(encoding="utf-8")
    # candidate-a should be gone entirely (incl. its claim).
    assert "### candidate-a" not in new_text
    assert "Alice <alice@example.com>" not in new_text
    # candidate-b survives unclaimed.
    assert "### candidate-b" in new_text
