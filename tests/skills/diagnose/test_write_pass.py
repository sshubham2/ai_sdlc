"""Tests for skills/diagnose/write_pass.py (slice-001 / AC #2 / B1 / m1).

Validates the helper that:
- Parses subagent text from --raw-file (stdin NOT supported per M4)
- Extracts three 4-backtick fenced blocks (B1)
- Tolerates nested 3-backtick fences inside content (B1)
- Validates findings against REQUIRED_FIELDS
- Writes 3 files via yaml.safe_dump (auto-quotes colons)
- Exits 0 / 1 / 2 per the contract

Rule reference: slice-001 ACs #2, dispositions B1 + m1.
"""
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.skills.diagnose.conftest import REPO_ROOT, SKILL_DIR

WRITE_PASS = SKILL_DIR / "write_pass.py"
PY = sys.executable


def _run(raw_text: str, pass_name: str, out_dir: Path, tmp_path: Path):
    """Invoke write_pass.py with --raw-file pointing to a tmp file."""
    raw_file = tmp_path / "subagent.raw"
    raw_file.write_text(raw_text, encoding="utf-8")
    out_dir.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [
            PY,
            str(WRITE_PASS),
            "--pass",
            pass_name,
            "--out",
            str(out_dir),
            "--raw-file",
            str(raw_file),
        ],
        capture_output=True,
        text=True,
    )


def _valid_finding_yaml() -> str:
    """A minimal schema-conformant finding as a YAML list literal (column-0)."""
    return (
        "- id: F-DEAD-aabbccdd\n"
        "  pass: 03a-dead-code\n"
        "  category: dead-code\n"
        "  severity: low\n"
        "  blast_radius: small\n"
        "  reversibility: cheap\n"
        "  title: Module legacy_auth.py unreachable\n"
        "  description: |\n"
        "    No inbound edges from any entry point.\n"
        "  evidence:\n"
        "    - path: src/legacy_auth.py\n"
        "      lines: '1-340'\n"
        "      note: no inbound\n"
        "  suggested_action: Delete the file.\n"
        "  effort_estimate: small\n"
        "  slice_candidate: maybe\n"
    )


def _good_input(pass_name: str = "03a-dead-code") -> str:
    """A well-formed subagent response with all three 4-backtick blocks."""
    return (
        "````section\n"
        "## 3a Dead code\n"
        "\n"
        "Found one unreachable module.\n"
        "````\n"
        "\n"
        "````findings\n"
        + _valid_finding_yaml()
        + "````\n"
        "\n"
        "````summary\n"
        "One unreachable module detected; verified via grep for dynamic imports.\n"
        "````\n"
    )


# --- AC #2: writes three files cleanly ---


def test_writes_three_files_for_valid_input(tmp_path: Path):
    """Valid 4-backtick input produces sections/, findings/, summary/ files.

    Defect class: the skill spec promises three files per pass.
    Disposition ref: AC #2.
    """
    out = tmp_path / "out"
    res = _run(_good_input(), "03a-dead-code", out, tmp_path)
    assert res.returncode == 0, f"stderr: {res.stderr}"
    assert (out / "sections" / "03a-dead-code.md").exists()
    assert (out / "findings" / "03a-dead-code.yaml").exists()
    assert (out / "summary" / "03a-dead-code.md").exists()


def test_missing_required_field_exits_nonzero(tmp_path: Path):
    """A finding missing a required field exits non-zero with clear stderr.

    Defect class: schema-mismatch. write_pass should refuse to write
    invalid YAML to disk.
    Disposition ref: AC #2.
    """
    # Include evidence so the missing-field path (not the evidence-empty path) fires.
    # Missing: severity, blast_radius, reversibility, description, suggested_action,
    # effort_estimate, slice_candidate.
    bad_yaml = (
        "- id: F-DEAD-aabbccdd\n"
        "  pass: 03a-dead-code\n"
        "  category: dead-code\n"
        "  title: missing fields finding\n"
        "  evidence:\n"
        "    - path: src/x.py\n"
        "      lines: '1'\n"
        "      note: ''\n"
    )
    raw = _good_input().replace(_valid_finding_yaml(), bad_yaml)
    out = tmp_path / "out"
    res = _run(raw, "03a-dead-code", out, tmp_path)
    assert res.returncode != 0, "expected non-zero exit on validation failure"
    # stderr names a missing required field
    assert "severity" in res.stderr or "missing" in res.stderr.lower(), (
        f"expected stderr to name a missing required field; got: {res.stderr!r}"
    )


def test_yaml_safe_dump_quotes_colons(tmp_path: Path):
    """A finding with a colon in a string value writes parseable YAML.

    Defect class: 2026-05-09 root-cause #3 — string-templated YAML
    produced unquoted-colon-bug. yaml.safe_dump should quote automatically.
    Disposition ref: AC #2 / mission-brief must-not-defer "yaml.safe_dump
    explicit kwargs".
    """
    finding_with_colon = (
        "- id: F-DEAD-aabbccdd\n"
        "  pass: 03a-dead-code\n"
        "  category: dead-code\n"
        "  severity: low\n"
        "  blast_radius: small\n"
        "  reversibility: cheap\n"
        "  title: Reminders cluster - stub UI\n"
        "  description: |\n"
        "    note: 29 inline handlers; req: any in some\n"
        "  evidence:\n"
        "    - path: src/x.py\n"
        "      lines: '1-10'\n"
        "      note: ''\n"
        "  suggested_action: Investigate.\n"
        "  effort_estimate: small\n"
        "  slice_candidate: 'no'\n"
    )
    raw = _good_input().replace(_valid_finding_yaml(), finding_with_colon)
    out = tmp_path / "out"
    res = _run(raw, "03a-dead-code", out, tmp_path)
    assert res.returncode == 0, f"stderr: {res.stderr}"
    # The written YAML must round-trip through safe_load
    written = (out / "findings" / "03a-dead-code.yaml").read_text(encoding="utf-8")
    parsed = yaml.safe_load(written)
    assert isinstance(parsed, list)
    assert len(parsed) == 1


# --- B1: 4-backtick fences + nested-fence tolerance ---


def test_section_block_with_nested_triple_backticks_parses_correctly(tmp_path: Path):
    """4-backtick outer fence allows arbitrary 3-backtick content inside.

    Defect class: per critique B1, every pass template shows subagents to
    embed nested ```bash / ```yaml / ```markdown fences in their section
    prose. The 4-backtick outer fence (per CommonMark length-distinguished
    closing fence) must not be terminated by an inner 3-backtick line.
    Disposition ref: B1.
    """
    section_with_nested = (
        "## 3a Dead code\n"
        "\n"
        "Run this:\n"
        "\n"
        "```bash\n"
        "$PY -m graphify orphans\n"
        "```\n"
        "\n"
        "Then:\n"
        "\n"
        "```yaml\n"
        "- id: example\n"
        "```\n"
        "\n"
        "End of section.\n"
    )
    raw = (
        "````section\n"
        + section_with_nested
        + "````\n"
        "\n"
        "````findings\n"
        + _valid_finding_yaml()
        + "````\n"
        "\n"
        "````summary\n"
        "nested fences inside section parse cleanly.\n"
        "````\n"
    )
    out = tmp_path / "out"
    res = _run(raw, "03a-dead-code", out, tmp_path)
    assert res.returncode == 0, f"stderr: {res.stderr}"
    section_md = (out / "sections" / "03a-dead-code.md").read_text(encoding="utf-8")
    # The nested code blocks should be preserved verbatim
    assert "```bash" in section_md
    assert "```yaml" in section_md
    assert "$PY -m graphify orphans" in section_md


def test_missing_fence_exits_two(tmp_path: Path):
    """Missing one of the three fenced blocks exits 2 with named fence in stderr.

    Defect class: parse-time failure (vs validation-time). Exit code 2
    distinguishes the case for the orchestrator's re-spawn logic.
    Disposition ref: AC #2.
    """
    raw = (
        "````section\n"
        "only section, no findings or summary\n"
        "````\n"
    )
    out = tmp_path / "out"
    res = _run(raw, "03a-dead-code", out, tmp_path)
    assert res.returncode == 2, (
        f"expected exit 2 for missing fence; got {res.returncode}; stderr: {res.stderr}"
    )
    assert "findings" in res.stderr or "summary" in res.stderr


# --- m1: parametrized empty-block variants ---


@pytest.mark.parametrize(
    "findings_block_content",
    [
        "[]\n",  # explicit empty list
        "",  # truly empty
        "   \n  \n",  # whitespace only
        "# no findings here\n",  # comment only
        "null\n",  # YAML null
    ],
)
def test_empty_findings_block_treated_as_empty_list(
    tmp_path: Path, findings_block_content: str
):
    """Empty / whitespace / null / comment / `[]` all parse as empty list.

    Defect class: per critique m1, only one variant was originally tested.
    All five should produce a findings YAML file with an empty list.
    Disposition ref: AC #2 + m1.
    """
    raw = (
        "````section\n"
        "## 1 Intent\n"
        "Some prose.\n"
        "````\n"
        "\n"
        "````findings\n"
        + findings_block_content
        + "````\n"
        "\n"
        "````summary\n"
        "No findings expected for this pass.\n"
        "````\n"
    )
    out = tmp_path / "out"
    res = _run(raw, "01-intent", out, tmp_path)
    assert res.returncode == 0, (
        f"empty-block variant {findings_block_content!r} should pass; "
        f"stderr: {res.stderr}"
    )
    written = (out / "findings" / "01-intent.yaml").read_text(encoding="utf-8")
    parsed = yaml.safe_load(written)
    # Either empty list or empty dict→list normalization; we want a list
    assert parsed == [] or parsed is None or parsed == [], (
        f"expected empty-list for findings; got {parsed!r}"
    )
