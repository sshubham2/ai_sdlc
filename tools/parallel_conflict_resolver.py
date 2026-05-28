"""PCR-1 parallel-conflict-resolution v1.

Per PCR-1 (methodology-changelog.md v0.73.0; ADR-069; slice-076; mints
a new rule on a new family axis sibling to PSQ-N). Diagnoses + classifies
+ (for SOFT class) auto-resolves parallel-slice merge conflicts that
surface at /commit-slice --merge Step 5b sub-step 2.5 git rebase time.

5-class taxonomy (per ADR-069 Decision):

  SOFT          - all U-files in {slice-queue.md, shippability.md}.
                  Auto-regen via dispatch + git rebase --continue.
  VAULT_CLAIM   - sole U-file is slice-queue.md AND same-candidate-
                  different-identity claim collision. STOP (deferred to
                  PCR-2 for timestamp-winner + light Critic).
  HARD          - any U-file is source/ADR/SKILL.md/_index.md/
                  methodology-changelog.md/etc. STOP (deferred to PCR-2
                  for full Critic stack + TRI-RESOLVE-1).
  MIXED         - SOFT + non-SOFT coexist. STOP (deferred to PCR-2;
                  atomicity - never partially auto-resolve).
  UNKNOWN       - classify_conflict cannot determine class. STOP loud
                  (APED-1 silent-disable / default-off-on-malformed).

SOFT-class file-set is forward-slash-keyed (per /critique M1 - Windows
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
import datetime
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
"""SOFT-class file-set - 2 canonical files, forward-slash-keyed.

Per ADR-069 / Critic B3 ACCEPTED-FIXED: _index.md dropped (Haiku-LLM-
dispatched by /archive skill per COST-1, not deterministic).
Per /design-slice Step 2 clarifying answer: methodology-changelog.md
dropped (PMI-1 5-leg atomic-bump risk on concurrent bumps).

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
    "See ADR-069 section Audit log.\n"
    "\n"
)
"""Header content written once on lazy-create first append."""


# ---------------------------------------------------------------------------
# ConflictClass enum
# ---------------------------------------------------------------------------

class ConflictClass(enum.Enum):
    """5-class taxonomy per ADR-069 section Decision."""

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
    concerned-slice metadata from architecture/slices/slice-*/mission-brief.md;
    extracts claim history from both branches' versions of slice-queue.md
    via tools.slice_queue_claim.parse_queue_text.

    Returns an empty-shape ConflictDiagnostic if rebase not in progress
    (no U-files); caller can pass to classify_conflict which will return
    UNKNOWN.
    """
    u_files = _extract_u_files(repo_root)
    concerned_slices: dict[str, tuple[ConcernedSlice, ...]] = {}
    for u_file in u_files:
        concerned_slices[u_file] = _derive_concerned_slices(repo_root, u_file)

    claim_history: tuple[ClaimEntry, ...] = ()
    if "architecture/slice-queue.md" in u_files:
        text_2 = _git_show_stage(repo_root, 2, "architecture/slice-queue.md")
        text_3 = _git_show_stage(repo_root, 3, "architecture/slice-queue.md")
        claims_2, claims_3 = _extract_claim_diff(text_2, text_3)
        entries = []
        for stage, claim_dict in ((2, claims_2), (3, claims_3)):
            for name, data in claim_dict.items():
                claimed_by = data.get("claimed_by")
                claimed_at = data.get("claimed_at")
                if claimed_by and claimed_at:
                    entries.append(ClaimEntry(
                        candidate_name=name,
                        claimed_by=str(claimed_by),
                        claimed_at=str(claimed_at),
                        branch_stage=stage,
                    ))
        claim_history = tuple(entries)

    return ConflictDiagnostic(
        u_files=u_files,
        concerned_slices=concerned_slices,
        claim_history=claim_history,
    )


def classify_conflict(diag: ConflictDiagnostic) -> ConflictClass:
    """Classify the conflict per ADR-069 5-class taxonomy.

    VAULT_CLAIM gate (per /critique B4 ACCEPTED-FIXED): if sole U-file
    is slice-queue.md AND any candidate name appears in BOTH branches'
    claim dicts with DIFFERENT Claimed-by values, returns VAULT_CLAIM.

    UNKNOWN gate (per /critique M4 ACCEPTED-FIXED): if rebase state is
    empty / unparseable, returns UNKNOWN. Fail-closed; NEVER silent-
    default to SOFT.
    """
    if not diag.u_files:
        return ConflictClass.UNKNOWN

    u_files_set = set(diag.u_files)
    soft_in_u = u_files_set & _SOFT_FILE_SET
    non_soft = u_files_set - _SOFT_FILE_SET
    has_vault_claim = _has_same_candidate_different_identity(diag.claim_history)

    if non_soft:
        # Any non-SOFT path present -> HARD or MIXED.
        if soft_in_u or has_vault_claim:
            return ConflictClass.MIXED
        return ConflictClass.HARD

    # All U-files are in the SOFT-set.
    if has_vault_claim:
        if u_files_set == {"architecture/slice-queue.md"}:
            return ConflictClass.VAULT_CLAIM
        # SOFT (shippability.md) + VAULT_CLAIM (slice-queue.md) -> MIXED
        # (per /critique M4 disambiguation; atomicity prevails).
        return ConflictClass.MIXED

    return ConflictClass.SOFT


def resolve_soft_conflict(
    diag: ConflictDiagnostic,
    repo_root: Path | None = None,
) -> ResolutionResult:
    """Resolve a SOFT-class conflict.

    For non-SOFT classes (VAULT_CLAIM / HARD / MIXED / UNKNOWN), returns
    ResolutionResult(action="STOP", ...) without mutating state.

    For SOFT: dispatches to _regen_slice_queue (textual claim-overlay
    per /critique-review M-add-1; no write_slice_queue round-trip) and
    _merge_shippability; stages + git rebase --continue; appends to
    audit log.

    The repo_root kwarg is optional (defaults to Path.cwd()) and exists
    primarily for testability - the prose-invoked CLI uses cwd by
    convention; tests can inject tmp_path-rooted fixtures.
    """
    if repo_root is None:
        repo_root = Path.cwd()

    cls = classify_conflict(diag)
    if cls is not ConflictClass.SOFT:
        reason = (
            f"non-SOFT class ({cls.value}) - deferred to PCR-2; "
            f"fall through to SOAD-1 STOP per ADR-069 atomicity"
        )
        return ResolutionResult(
            action="STOP",
            conflict_class=cls,
            regenerated_files=(),
            reason=reason,
        )

    # SOFT path: regen each SOFT U-file, stage, continue rebase, log.
    regenerated: list[str] = []
    try:
        for u_file in diag.u_files:
            if u_file == "architecture/slice-queue.md":
                regenerated.extend(_regen_slice_queue(repo_root, diag))
            elif u_file == "architecture/shippability.md":
                regenerated.extend(_merge_shippability(repo_root))
    except _SoftResolutionError as exc:
        # _regen_slice_queue or _merge_shippability surfaced a structural
        # issue (e.g., both stages missing, or same-slice-number with
        # different content escalating to HARD per design.md edge cases).
        # Fall-closed STOP without staging or continuing the rebase.
        return ResolutionResult(
            action="STOP",
            conflict_class=exc.conflict_class,
            regenerated_files=(),
            reason=str(exc),
        )

    if not regenerated:
        return ResolutionResult(
            action="STOP",
            conflict_class=ConflictClass.UNKNOWN,
            regenerated_files=(),
            reason="SOFT classification but no files regenerated - rebase state unexpected",
        )

    # Stage + continue. Failures here STOP fall-closed per design.md error model.
    try:
        subprocess.run(
            ["git", "add", *regenerated],
            cwd=str(repo_root),
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "rebase", "--continue"],
            cwd=str(repo_root),
            check=True,
            capture_output=True,
            env={**__import__("os").environ, "GIT_EDITOR": "true"},
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return ResolutionResult(
            action="STOP",
            conflict_class=ConflictClass.SOFT,
            regenerated_files=tuple(regenerated),
            reason=(
                "git stage + rebase --continue failed post soft-resolution - "
                f"rebase state may have additional conflicts: {exc!r}"
            ),
        )

    result = ResolutionResult(
        action="APPLIED",
        conflict_class=ConflictClass.SOFT,
        regenerated_files=tuple(regenerated),
        reason=None,
    )

    # Audit log is best-effort per design.md error model.
    try:
        _append_audit_log(repo_root, diag, result)
    except Exception as exc:  # noqa: BLE001 - best-effort by design
        print(
            f"parallel-conflict-resolver: audit log append failed (non-blocking): {exc!r}",
            file=sys.stderr,
        )

    return result


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

class _SoftResolutionError(Exception):
    """Internal signal for soft-resolution structural failure.

    Carries a ``conflict_class`` (typically HARD or UNKNOWN) to surface to
    the caller's STOP result. Per design.md Edge-cases column:
    shippability.md same-slice-number with different content escalates to
    HARD; slice-queue.md both-stages-missing escalates to UNKNOWN.
    """

    def __init__(self, message: str, conflict_class: ConflictClass):
        super().__init__(message)
        self.conflict_class = conflict_class


def _has_same_candidate_different_identity(
    claim_history: tuple[ClaimEntry, ...],
) -> bool:
    """Walk claim_history for any candidate-name claimed by different
    identities across the two branch stages.

    Per /critique B4 ACCEPTED-FIXED: the VAULT_CLAIM gate fires only when
    the SAME candidate name appears in BOTH stage 2 and stage 3 claim
    dicts with DIFFERENT Claimed-by values. Same-candidate-same-identity
    (mere claim refresh) is NOT VAULT_CLAIM.
    """
    by_name: dict[str, dict[int, str]] = {}
    for entry in claim_history:
        by_name.setdefault(entry.candidate_name, {})[entry.branch_stage] = entry.claimed_by
    for stages in by_name.values():
        if 2 in stages and 3 in stages and stages[2] != stages[3]:
            return True
    return False


def _extract_u_files(repo_root: Path) -> tuple[str, ...]:
    """Extract U-prefixed file paths from git status --porcelain.

    Returns forward-slash strings (NOT Path objects) per /critique M1.
    git status --porcelain emits forward-slash on all OSes per git docs.

    Returns empty tuple on subprocess failure (no rebase in progress,
    git binary unavailable, etc.) - caller's classify_conflict will
    return UNKNOWN.
    """
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ()

    u_files: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        # Unmerged states per `git status` porcelain v1:
        #   DD, AU, UD, UA, DU, AA, UU (all "X != ' '" with X or Y == 'U'
        #   plus DD/AA).
        x, y = line[0], line[1]
        if x == "U" or y == "U" or (x == "A" and y == "A") or (x == "D" and y == "D"):
            path = line[3:].strip()
            # Strip surrounding quotes if git quoted the path (rare).
            if path.startswith('"') and path.endswith('"'):
                path = path[1:-1]
            u_files.append(path)
    return tuple(u_files)


def _git_show_stage(repo_root: Path, stage: int, path: str) -> str:
    """Read `git show :<stage>:<path>` for the named conflict stage.

    Returns empty string on subprocess failure (stage absent - e.g., file
    added on only one branch). Caller handles the asymmetric-stage case.
    """
    try:
        proc = subprocess.run(
            ["git", "show", f":{stage}:{path}"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    return proc.stdout


def _derive_concerned_slices(
    repo_root: Path, u_file: str
) -> tuple[ConcernedSlice, ...]:
    """Map a U-file to its concerned slices via active-slice mission-brief scan.

    Walks ``architecture/slices/slice-*-*/`` (active slices; NOT
    ``archive/``). For each active slice, reads ``mission-brief.md`` and
    treats it as a concerned slice if the U-file path string appears
    anywhere in the brief (typically in Blast-radius / Dependencies /
    edit-site sections).

    Last-commit ISO is best-effort via ``git log -1 --format=%cI`` on
    the slice's branch (``slice/NNN-<name>``); on failure the field is
    ``None``.

    Lightweight v1 - does NOT consult ``architecture/slice-queue.md``
    candidate-blast-radii (deferred to a future revision per design.md
    out-of-scope "Graphify-derived blast-radius for active slices").
    """
    slices_dir = repo_root / "architecture" / "slices"
    if not slices_dir.is_dir():
        return ()

    matches: list[ConcernedSlice] = []
    for entry in sorted(slices_dir.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        if not name.startswith("slice-") or name == "archive":
            continue
        brief_path = entry / "mission-brief.md"
        if not brief_path.is_file():
            continue
        try:
            brief_text = brief_path.read_text(encoding="utf-8")
        except OSError:
            continue
        if u_file not in brief_text:
            continue

        last_commit_iso = _last_commit_iso_for_slice(repo_root, name)
        matches.append(ConcernedSlice(
            slice_id=name,
            blast_radius=(u_file,),
            mission_brief_link=f"architecture/slices/{name}/mission-brief.md",
            last_commit_iso=last_commit_iso,
        ))
    return tuple(matches)


def _last_commit_iso_for_slice(repo_root: Path, slice_dir_name: str) -> str | None:
    """Best-effort: last-commit ISO for a slice's branch.

    Reads ``git log -1 --format=%cI`` for ``slice/NNN-<name>``; returns
    None on failure (branch absent, git unavailable). Slice dir naming
    convention per ADR-046: ``slice-NNN-<name>`` -> branch ``slice/NNN-<name>``.
    """
    # slice-NNN-<name> -> slice/NNN-<name>
    if not slice_dir_name.startswith("slice-"):
        return None
    branch = "slice/" + slice_dir_name[len("slice-"):]
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%cI", branch],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    out = proc.stdout.strip()
    return out or None


def _extract_claim_diff(
    text_2: str, text_3: str
) -> tuple[dict, dict]:
    """Extract claim dicts from both branches' queue text via parse_queue_text.

    Returns (claims_from_stage_2, claims_from_stage_3). Each dict is
    keyed by candidate name with claim metadata (claimed_by / claimed_at)
    plus _extra_field_lines per slice_queue_claim contract.
    """
    # Import lazily so a slice_queue_claim import failure doesn't break
    # classify_conflict (which is import-time-evaluated when classify is
    # called on a synthetic ConflictDiagnostic in tests).
    try:
        from tools.slice_queue_claim import parse_queue_text  # noqa: PLC0415
    except ImportError as exc:
        print(
            f"parallel-conflict-resolver: slice_queue_claim.parse_queue_text "
            f"unavailable: {exc!r}",
            file=sys.stderr,
        )
        return ({}, {})

    try:
        claims_2 = parse_queue_text(text_2) if text_2 else {}
    except Exception:  # noqa: BLE001 - parser raises ClaimUsageError on partial blocks
        claims_2 = {}
    try:
        claims_3 = parse_queue_text(text_3) if text_3 else {}
    except Exception:  # noqa: BLE001
        claims_3 = {}
    return (claims_2, claims_3)


def _regen_slice_queue(
    repo_root: Path, diag: ConflictDiagnostic
) -> tuple[str, ...]:
    """Regenerate architecture/slice-queue.md via textual claim-overlay.

    Per /critique-review M-add-1 ACCEPTED-FIXED option (2): take
    rebase-target's queue text (git show :3:) verbatim as the result
    baseline; overlay merged claims via _overlay_claims_on_queue_text;
    NO write_slice_queue round-trip (avoids the B1 phantom-parser trap).
    """
    text_2 = _git_show_stage(repo_root, 2, "architecture/slice-queue.md")
    text_3 = _git_show_stage(repo_root, 3, "architecture/slice-queue.md")

    if not text_2 and not text_3:
        raise _SoftResolutionError(
            "slice-queue.md: both stage 2 and stage 3 missing - "
            "rebase state unexpected",
            ConflictClass.UNKNOWN,
        )

    # Baseline: prefer rebase-target stage (text_3); if absent, fall back
    # to text_2 verbatim per design.md edge case (a).
    baseline_text = text_3 if text_3 else text_2

    claims_2, claims_3 = _extract_claim_diff(text_2, text_3)
    merged_claims = _merge_claim_dicts(claims_2, claims_3)

    overlaid = _overlay_claims_on_queue_text(baseline_text, merged_claims)

    out_path = repo_root / "architecture" / "slice-queue.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(overlaid, encoding="utf-8")
    return ("architecture/slice-queue.md",)


def _merge_claim_dicts(claims_2: dict, claims_3: dict) -> dict:
    """Newest-Claimed-at-wins union of two claim dicts.

    Per PSQ-2 semantics: when both branches claim the same candidate
    (with the same Claimed-by - same-identity-different-timestamp; the
    different-identity case is gated upstream as VAULT_CLAIM), the newer
    Claimed-at wins.
    """
    merged: dict = {}
    for name, data in claims_2.items():
        merged[name] = dict(data)
    for name, data in claims_3.items():
        if name not in merged:
            merged[name] = dict(data)
            continue
        existing_at = merged[name].get("claimed_at")
        new_at = data.get("claimed_at")
        if existing_at and new_at and str(new_at) > str(existing_at):
            merged[name] = dict(data)
    return merged


def _overlay_claims_on_queue_text(
    queue_text: str, merged_claims: dict
) -> str:
    """Surgically overlay Claimed-by + Claimed-at lines onto queue text.

    Walks queue_text line-by-line tracking the current ``### <name>``
    candidate. For each candidate that's also in ``merged_claims``:

      - Emits the existing ``- **Risk-retired:** <value>`` line as-is,
        then immediately appends the merged Claimed-by + Claimed-at
        lines (insert-new path).
      - Skips any pre-existing ``- **Claimed-by:**`` / ``- **Claimed-at:**``
        lines under that candidate (replace-existing path - the new
        lines were already emitted after Risk-retired).

    Candidates in ``merged_claims`` whose names are NOT present in
    ``queue_text`` are silently dropped (will re-surface at next
    ``/slice`` regen - documented behavior per design.md L137).
    """
    if not queue_text:
        return queue_text

    lines = queue_text.split("\n")
    result_lines: list[str] = []
    current_candidate: str | None = None

    for line in lines:
        # ### <name> heading -> update tracking, emit line.
        if line.startswith("### "):
            current_candidate = line[4:].strip()
            result_lines.append(line)
            continue

        # Skip existing Claimed-by / Claimed-at under a candidate getting
        # an overlay (replace-existing path; new lines emitted after Risk-
        # retired above).
        if (
            current_candidate is not None
            and current_candidate in merged_claims
            and (
                line.startswith("- **Claimed-by:**")
                or line.startswith("- **Claimed-at:**")
            )
        ):
            continue

        result_lines.append(line)

        # After emitting Risk-retired for a candidate getting an overlay,
        # immediately append the new Claimed-by + Claimed-at lines.
        if (
            current_candidate is not None
            and current_candidate in merged_claims
            and line.startswith("- **Risk-retired:**")
        ):
            claim = merged_claims[current_candidate]
            claimed_by = claim.get("claimed_by")
            claimed_at = claim.get("claimed_at")
            if claimed_by and claimed_at:
                result_lines.append(f"- **Claimed-by:** {claimed_by}")
                result_lines.append(f"- **Claimed-at:** {claimed_at}")

    return "\n".join(result_lines)


def _merge_shippability(repo_root: Path) -> tuple[str, ...]:
    """Row-union merge of architecture/shippability.md by slice number.

    Per design.md Resolution algorithm: parse both stages' tables, key
    rows by leading ``| <NN> |`` slice number, union, sort ascending,
    preserve header + non-numeric rows verbatim. Same-slice-number with
    different content escalates to HARD per design.md Edge-cases column.
    """
    text_2 = _git_show_stage(repo_root, 2, "architecture/shippability.md")
    text_3 = _git_show_stage(repo_root, 3, "architecture/shippability.md")

    if not text_2 and not text_3:
        raise _SoftResolutionError(
            "shippability.md: both stage 2 and stage 3 missing - "
            "rebase state unexpected",
            ConflictClass.UNKNOWN,
        )

    rows_2 = _parse_shippability_rows(text_2) if text_2 else ({}, [])
    rows_3 = _parse_shippability_rows(text_3) if text_3 else ({}, [])

    numbered_2, prelude_2 = rows_2
    numbered_3, prelude_3 = rows_3

    # Defense-in-depth: same-slice-number with different content -> HARD.
    for slice_num, row in numbered_2.items():
        if slice_num in numbered_3 and numbered_3[slice_num].strip() != row.strip():
            raise _SoftResolutionError(
                f"shippability.md row #{slice_num}: same slice number with "
                f"different content on both branches - escalating to HARD "
                f"per design.md Edge-cases column",
                ConflictClass.HARD,
            )

    # Prelude: prefer text_3 (rebase-target); fall back to text_2.
    prelude_lines = prelude_3 if prelude_3 else prelude_2

    merged_rows = dict(numbered_2)
    merged_rows.update(numbered_3)

    output_lines = list(prelude_lines)
    for slice_num in sorted(merged_rows.keys()):
        output_lines.append(merged_rows[slice_num])

    output_text = "\n".join(output_lines)
    if not output_text.endswith("\n"):
        output_text += "\n"

    out_path = repo_root / "architecture" / "shippability.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output_text, encoding="utf-8")
    return ("architecture/shippability.md",)


def _parse_shippability_rows(text: str) -> tuple[dict[int, str], list[str]]:
    """Parse shippability.md into (numbered_rows, prelude_lines).

    ``numbered_rows``: dict[int, str] keyed by slice number, value is the
    raw row line. ``prelude_lines``: non-numbered lines (header, blank
    lines, table separator, footer) in original order, with the
    placeholder for sorted-numeric-row insertion at the end implicit.
    """
    import re  # noqa: PLC0415
    numbered: dict[int, str] = {}
    prelude: list[str] = []
    row_re = re.compile(r"^\|\s*(\d+)\s*\|")
    for line in text.split("\n"):
        m = row_re.match(line)
        if m:
            numbered[int(m.group(1))] = line
        else:
            prelude.append(line)
    return (numbered, prelude)


def _append_audit_log(
    repo_root: Path, diag: ConflictDiagnostic, result: ResolutionResult
) -> None:
    """Append entry to architecture/parallel-conflict-resolution-log.md.

    Lazy-create on first append (writes _AUDIT_LOG_HEADER). Best-effort:
    write failures should be caught by caller; this function may raise
    OSError per the design.md error model (caller logs to stderr but
    does NOT block resolution).
    """
    log_path = repo_root / _AUDIT_LOG_PATH
    log_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        head_proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
        head_sha = head_proc.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        head_sha = "(unavailable)"

    u_files_csv = ", ".join(diag.u_files) if diag.u_files else "(none)"
    concerned_ids = sorted({
        cs.slice_id
        for u in diag.u_files
        for cs in diag.concerned_slices.get(u, ())
    })
    concerned_csv = ", ".join(concerned_ids) if concerned_ids else "(none)"

    action_lines: list[str] = []
    for f in result.regenerated_files:
        if f == "architecture/slice-queue.md":
            action_lines.append(
                f"- `{f}` - regenerated via _overlay_claims_on_queue_text "
                "with merged-claims union"
            )
        elif f == "architecture/shippability.md":
            action_lines.append(
                f"- `{f}` - row-union merge by slice number"
            )
        else:
            action_lines.append(f"- `{f}` - regenerated")

    entry = (
        f"## Soft-conflict resolution - {timestamp}\n"
        "\n"
        f"**Repo HEAD SHA pre-resolution**: {head_sha}\n"
        f"**U-files resolved**: {u_files_csv}\n"
        f"**Concerned slices**: {concerned_csv}\n"
        f"**Resolution actions**:\n"
        + ("\n".join(action_lines) if action_lines else "(none)")
        + "\n\n"
    )

    if not log_path.exists():
        log_path.write_text(_AUDIT_LOG_HEADER + entry, encoding="utf-8")
    else:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(entry)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _to_jsonable(obj):
    """Convert dataclasses / enums / tuples to JSON-serializable dicts."""
    if isinstance(obj, ConflictClass):
        return obj.value
    if dataclasses.is_dataclass(obj):
        return {k: _to_jsonable(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    return obj


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
    repo_root = args.repo_root.resolve()

    diag = diagnose_conflict(repo_root)

    if args.diagnose:
        if args.json:
            payload = {
                "action": "DIAGNOSE",
                "diagnostic": _to_jsonable(diag),
            }
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"U-files: {list(diag.u_files)}")
            for u in diag.u_files:
                concerned = diag.concerned_slices.get(u, ())
                print(f"  {u}: {len(concerned)} concerned slice(s)")
                for cs in concerned:
                    print(
                        f"    - {cs.slice_id} (last-commit: {cs.last_commit_iso}; "
                        f"mission-brief: {cs.mission_brief_link})"
                    )
            print(f"Claim history: {len(diag.claim_history)} entry/entries")
        return 0

    if args.classify:
        cls = classify_conflict(diag)
        if args.json:
            payload = {"action": "CLASSIFY", "conflict_class": cls.value}
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"ConflictClass: {cls.value}")
        return 0

    if args.resolve_soft:
        result = resolve_soft_conflict(diag, repo_root=repo_root)
        if args.json:
            payload = {
                "action": result.action,
                "conflict_class": result.conflict_class.value,
                "regenerated_files": list(result.regenerated_files),
                "reason": result.reason,
            }
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"Action: {result.action} (class: {result.conflict_class.value})")
            if result.regenerated_files:
                print(f"Regenerated: {list(result.regenerated_files)}")
            if result.reason:
                print(f"Reason: {result.reason}")
        # Exit semantics per design.md:
        #   0 on success (APPLIED or STOP with coherent classification)
        #   1 on UNKNOWN (resolver could not classify; defer to SOAD-1)
        if result.conflict_class is ConflictClass.UNKNOWN:
            return 1
        return 0

    # argparse's mutually_exclusive_group(required=True) prevents this.
    return 2


if __name__ == "__main__":
    sys.exit(main())
