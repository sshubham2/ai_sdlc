"""AC#4 — Vault-claim audit-log row format + mixed-section append-only.

Two tests:
1. test_vault_claim_event_row_format: assert the 8-field markdown bold row
   shape under a `## Vault-claim resolution - <ISO>` heading (hyphen-space
   per M2 uniform separator with PCR-1 SOFT row).
2. test_log_is_append_only_across_section_types: seed a synthesized prior
   SOFT-section row; trigger a VAULT_CLAIM append; assert the prior SOFT
   row survives byte-equal AND the new VAULT_CLAIM section follows.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from tools.parallel_conflict_resolver import (
    ClaimEntry,
    ConflictClass,
    ConflictDiagnostic,
    ResolutionResult,
    _append_audit_log,
)


def _diag_for_vault_claim() -> ConflictDiagnostic:
    return ConflictDiagnostic(
        u_files=("architecture/slice-queue.md",),
        concerned_slices={},
        claim_history=(
            ClaimEntry(
                candidate_name="add-foo",
                claimed_by="alice <a@example.com>",
                claimed_at="2026-05-29T12:00:00+00:00",
                branch_stage=2,
            ),
            ClaimEntry(
                candidate_name="add-foo",
                claimed_by="bob <b@example.com>",
                claimed_at="2026-05-29T10:00:00+00:00",
                branch_stage=3,
            ),
        ),
    )


def _vault_claim_result(replacement: str | None = "add-bar") -> ResolutionResult:
    return ResolutionResult(
        action="APPLIED",
        conflict_class=ConflictClass.VAULT_CLAIM,
        regenerated_files=("architecture/slice-queue.md",),
        reason=f"vault-claim-resolved; replacement={replacement}",
    )


def _init_git(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp_path, check=True)
    (tmp_path / "architecture").mkdir(exist_ok=True)


def test_vault_claim_event_row_format(tmp_path) -> None:
    """Lazy-create + append a VAULT_CLAIM resolution event; assert section shape."""
    _init_git(tmp_path)
    diag = _diag_for_vault_claim()
    result = _vault_claim_result(replacement="add-replacement")
    _append_audit_log(tmp_path, diag, result)
    log_path = tmp_path / "architecture" / "parallel-conflict-resolution-log.md"
    text = log_path.read_text(encoding="utf-8")

    # Section heading — uniform hyphen-space per M2 ACCEPTED-FIXED
    assert re.search(
        r"^## Vault-claim resolution - \d{4}-\d{2}-\d{2}T",
        text,
        re.MULTILINE,
    ), f"Vault-claim section heading missing or off-shape; got:\n{text}"

    # 8 required field-lines (markdown bold, key-value)
    required_fields = [
        "Repo HEAD SHA pre-resolution",
        "Candidate name",
        "Winner Claimed-by",
        "Winner Claimed-at",
        "Loser Claimed-by",
        "Loser Claimed-at",
        "Loser auto-re-pick",
        "Resolution actions",
    ]
    for field in required_fields:
        assert f"**{field}**:" in text, (
            f"Vault-claim audit row missing field `**{field}**:`; got:\n{text}"
        )

    # Strict-newer winner identity preserved in audit
    assert "alice <a@example.com>" in text, "winner identity must appear in audit row"
    assert "2026-05-29T12:00:00" in text, "winner Claimed-at must appear"
    assert "bob <b@example.com>" in text, "loser identity must appear"
    assert "add-replacement" in text, "loser replacement must appear"


def test_log_is_append_only_across_section_types(tmp_path) -> None:
    """Mixed-section test: seed a prior SOFT row; append VAULT_CLAIM; assert
    prior SOFT row survives BYTE-EQUAL after the new append.

    Exercises the lazy-create-on-first-of-any-section behavior: the file is
    absent on disk before the SOFT seed; SOFT seed triggers lazy-create with
    the audit-log header; VAULT_CLAIM append must NOT rewrite the header or
    the SOFT section.
    """
    _init_git(tmp_path)

    # Seed a SOFT-section row first via the same audit-log helper
    soft_diag = ConflictDiagnostic(
        u_files=("architecture/slice-queue.md", "architecture/shippability.md"),
        concerned_slices={},
        claim_history=(),
    )
    soft_result = ResolutionResult(
        action="APPLIED",
        conflict_class=ConflictClass.SOFT,
        regenerated_files=(
            "architecture/slice-queue.md",
            "architecture/shippability.md",
        ),
        reason=None,
    )
    _append_audit_log(tmp_path, soft_diag, soft_result)
    log_path = tmp_path / "architecture" / "parallel-conflict-resolution-log.md"
    pre_append_text = log_path.read_text(encoding="utf-8")
    assert "## Soft-conflict resolution" in pre_append_text
    soft_section_bytes = pre_append_text.encode("utf-8")

    # Now append a VAULT_CLAIM section
    _append_audit_log(tmp_path, _diag_for_vault_claim(), _vault_claim_result())

    post_append_text = log_path.read_text(encoding="utf-8")
    # SOFT section + header preserved byte-equal (post text STARTS with pre)
    assert post_append_text.encode("utf-8").startswith(soft_section_bytes), (
        "Append-only contract violated: prior SOFT section did not survive "
        "byte-equal after VAULT_CLAIM append. (Lazy-create-on-first-of-each-"
        "section must NOT re-write the header or prior rows.)"
    )
    # New VAULT_CLAIM section follows
    assert "## Vault-claim resolution" in post_append_text
