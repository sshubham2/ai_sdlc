"""PCR-1 parallel-conflict-resolution v1.

Per PCR-1 (methodology-changelog.md v0.73.0; ADR-069; slice-076; mints
a new rule on a new family axis sibling to PSQ-N). Diagnoses + classifies
+ (for SOFT class) auto-resolves parallel-slice merge conflicts that
surface at /commit-slice --merge Step 5b sub-step 2.5 git rebase time.

5-class taxonomy (per ADR-069 Decision):

  SOFT          — all U-files in {slice-queue.md, shippability.md}.
                  Auto-regen via dispatch + git rebase --continue.
  VAULT_CLAIM   — sole U-file is slice-queue.md AND same-candidate-
                  different-identity claim collision. STOP (deferred to
                  PCR-2 for timestamp-winner + light Critic).
  HARD          — any U-file is source/ADR/SKILL.md/_index.md/
                  methodology-changelog.md/etc. STOP (deferred to PCR-2
                  for full Critic stack + TRI-RESOLVE-1).
  MIXED         — SOFT + non-SOFT coexist. STOP (deferred to PCR-2;
                  atomicity — never partially auto-resolve).
  UNKNOWN       — classify_conflict cannot determine class. STOP loud
                  (APED-1 silent-disable / default-off-on-malformed).

SOFT-class file-set is forward-slash-keyed (per /critique M1 — Windows
path normalization; git status --porcelain emits forward-slash on all
OSes per git docs).

Audit log: append-only at architecture/parallel-conflict-resolution-log.md.
Race-acceptance per ADR-067 cooperative-not-adversarial threat model
(carried forward); audit log is best-effort (write failures log to
stderr but do NOT block resolution).
"""

from __future__ import annotations

import argparse
import dataclasses
import enum
import json
import subprocess
import sys
from pathlib import Path

from tools import _stdout


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_SOFT_FILE_SET: frozenset[str] = frozenset({
    "architecture/slice-queue.md",
    "architecture/shippability.md",
})
"""SOFT-class file-set — 2 canonical files, forward-slash-keyed.

Per ADR-069 / Critic B3 ACCEPTED-FIXED: _index.md dropped (Haiku-LLM-
dispatched by /archive skill per COST-1, not deterministic).
Per /design-slice Step 2 clarifying answer: methodology-changelog.md
dropped (PMI-1 5-leg atomic-bump risk on concurrent bumps).

Forward-slash convention per /critique M1 ACCEPTED-FIXED: git
status --porcelain emits forward-slash on all OSes; str(Path) on
Windows produces backslashes and misses the frozenset. NEVER cast
Path objects to str for membership checks — use .as_posix() if
normalization is needed.

Pinned by test_soft_file_set_is_two_canonical_files_forward_slash_keyed.
"""

_AUDIT_LOG_PATH: Path = Path("architecture/parallel-conflict-resolution-log.md")
"""Append-only audit log path (lazy-created on first append)."""

_AUDIT_LOG_HEADER: str = (
    "# Parallel-conflict-resolution log\n"
    "\n"
    "Append-only audit trail of PCR-1 soft-conflict auto-resolutions. "
    "Each entry: ISO-8601 UTC timestamp + repo HEAD SHA pre-resolution "
    "+ U-files list + concerned slices + per-file resolution action. "
    "See ADR-069 § Audit log.\n"
    "\n"
)
"""Header content written once on lazy-create first append."""


# ---------------------------------------------------------------------------
# ConflictClass enum
# ---------------------------------------------------------------------------

class ConflictClass(enum.Enum):
    """5-class taxonomy per ADR-069 § Decision."""

    SOFT = "SOFT"
    VAULT_CLAIM = "VAULT_CLAIM"
    HARD = "HARD"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Frozen dataclasses
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True, slots=True)
class ConcernedSlice:
    """One slice (active or queue-candidate) involved in a conflict."""

    slice_id: str
    blast_radius: tuple[str, ...]
    mission_brief_link: str
    last_commit_iso: str | None


@dataclasses.dataclass(frozen=True, slots=True)
class ClaimEntry:
    """One PSQ-2 claim record."""

    candidate_name: str
    claimed_by: str
    claimed_at: str
    branch_stage: int  # 2 = ours/rebased, 3 = theirs/rebase-target


@dataclasses.dataclass(frozen=True, slots=True)
class ConflictDiagnostic:
    """Structured diagnostic of an in-progress rebase conflict."""

    u_files: tuple[str, ...]
    concerned_slices: dict[str, tuple[ConcernedSlice, ...]]
    claim_history: tuple[ClaimEntry, ...]


@dataclasses.dataclass(frozen=True, slots=True)
class ResolutionResult:
    """Result of resolve_soft_conflict."""

    action: str  # "APPLIED" or "STOP"
    conflict_class: ConflictClass
    regenerated_files: tuple[str, ...]
    reason: str | None


# ---------------------------------------------------------------------------
# Public library API
# ---------------------------------------------------------------------------

def diagnose_conflict(repo_root: Path) -> ConflictDiagnostic:
    """Diagnose the in-progress rebase conflict state at repo_root.

    Reads git status --porcelain to enumerate U-files; derives
    concerned-slice metadata from architecture/slice-queue.md +
    architecture/slices/slice-*-*/mission-brief.md; extracts claim
    history from both branches' versions of slice-queue.md via
    tools.slice_queue_claim.parse_queue_text.

    Returns an empty ConflictDiagnostic if rebase not in progress
    (no U-files).
    """
    raise NotImplementedError("PCR-1 v1: implemented in Phase C")


def classify_conflict(diag: ConflictDiagnostic) -> ConflictClass:
    """Classify the conflict per ADR-069 5-class taxonomy.

    VAULT_CLAIM gate (per /critique B4 ACCEPTED-FIXED): if sole U-file
    is slice-queue.md AND any candidate name appears in BOTH branches'
    claim dicts with DIFFERENT Claimed-by: values, returns VAULT_CLAIM.

    UNKNOWN gate (per /critique M4 ACCEPTED-FIXED): if rebase state is
    empty / unparseable, returns UNKNOWN. Fail-closed; NEVER silent-
    default to SOFT.
    """
    raise NotImplementedError("PCR-1 v1: implemented in Phase C")


def resolve_soft_conflict(diag: ConflictDiagnostic) -> ResolutionResult:
    """Resolve a SOFT-class conflict.

    For non-SOFT classes (VAULT_CLAIM / HARD / MIXED / UNKNOWN), returns
    ResolutionResult(action="STOP", ...) without mutating state.

    For SOFT: dispatches to _regen_slice_queue (textual claim-overlay
    per /critique-review M-add-1; no write_slice_queue round-trip) and
    _merge_shippability; stages + git rebase --continue; appends to
    audit log.
    """
    raise NotImplementedError("PCR-1 v1: implemented in Phase C")


# ---------------------------------------------------------------------------
# Private helpers (impl in Phase C)
# ---------------------------------------------------------------------------

def _extract_u_files(repo_root: Path) -> tuple[str, ...]:
    """Extract U-prefixed file paths from git status --porcelain.

    Returns forward-slash strings (NOT Path objects) per /critique M1.
    """
    raise NotImplementedError("PCR-1 v1: implemented in Phase C")


def _derive_concerned_slices(
    repo_root: Path, u_file: str
) -> tuple[ConcernedSlice, ...]:
    """Map a U-file to its concerned slices via blast-radius lookups."""
    raise NotImplementedError("PCR-1 v1: implemented in Phase C")


def _extract_claim_diff(
    text_2: str, text_3: str
) -> tuple[dict, dict]:
    """Extract claim dicts from both branches' versions via parse_queue_text.

    Returns (claims_from_stage_2, claims_from_stage_3).
    Uses tools.slice_queue_claim.parse_queue_text per /critique B1
    citation correction.
    """
    raise NotImplementedError("PCR-1 v1: implemented in Phase C")


def _regen_slice_queue(
    repo_root: Path, diag: ConflictDiagnostic
) -> tuple[str, ...]:
    """Regenerate architecture/slice-queue.md via textual claim-overlay.

    Per /critique-review M-add-1 ACCEPTED-FIXED option (2): take
    rebase-target's queue text (git show :3:) verbatim as the result
    baseline; overlay merged claims via _overlay_claims_on_queue_text;
    NO write_slice_queue round-trip (avoids the B1 phantom-parser trap).
    """
    raise NotImplementedError("PCR-1 v1: implemented in Phase C")


def _overlay_claims_on_queue_text(
    queue_text: str, merged_claims: dict
) -> str:
    """Surgically overlay Claimed-by + Claimed-at lines onto queue text.

    For each candidate in queue_text that's also in merged_claims:
      - If existing Claimed-by/Claimed-at lines present, replace them.
      - If absent, insert under the Risk-retired line.
    Candidates in merged_claims but NOT in queue_text are dropped
    (will re-surface at next /slice regen).
    """
    raise NotImplementedError("PCR-1 v1: implemented in Phase C")


def _merge_shippability(repo_root: Path) -> tuple[str, ...]:
    """Row-union merge of architecture/shippability.md by slice number."""
    raise NotImplementedError("PCR-1 v1: implemented in Phase C")


def _append_audit_log(
    repo_root: Path, diag: ConflictDiagnostic, result: ResolutionResult
) -> None:
    """Append entry to architecture/parallel-conflict-resolution-log.md.

    Lazy-create on first append. Best-effort: write failures log to
    stderr but do NOT raise (audit log is not a precondition; per
    ADR-069 § Audit log race-acceptance).
    """
    raise NotImplementedError("PCR-1 v1: implemented in Phase C")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """CLI entry point: --diagnose | --classify | --resolve-soft."""
    _stdout.reconfigure_stdout_utf8()

    parser = argparse.ArgumentParser(
        prog="python -m tools.parallel_conflict_resolver",
        description="PCR-1 parallel-conflict resolver (ADR-069).",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--diagnose", action="store_true", help="Emit ConflictDiagnostic")
    mode.add_argument("--classify", action="store_true", help="Emit ConflictClass")
    mode.add_argument("--resolve-soft", action="store_true", help="Attempt SOFT-class resolution")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repo root (default: cwd)")

    args = parser.parse_args(argv)

    # Phase C will implement the dispatch.
    print("PCR-1 v1: CLI implemented in Phase C", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
