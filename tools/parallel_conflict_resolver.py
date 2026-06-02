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
                  methodology-changelog.md/etc. STOP via resolve_hard_conflict;
                  gate-on-hand-resolve (code-review agent + TRI-RESOLVE-1)
                  orchestrated by skills/commit-slice/SKILL.md sub-step 2.5
                  (PCR-2b / slice-083 / ADR-075). Never auto-merged.
  MIXED         - SOFT + non-SOFT coexist. STOP via resolve_hard_conflict;
                  routed through the HARD gate-on-hand-resolve path
                  (atomicity - never partially auto-resolve the SOFT portion).
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
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple, NoReturn

from tools import _stdout
from tools._vault_git import vault_is_external
from tools._vault_paths import VAULT_ROOT


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_SOFT_FILE_SET: frozenset[str] = frozenset({
    "architecture/slice-queue.md",  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
    "architecture/shippability.md",  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
})
"""SOFT-class file-set - 2 canonical files, forward-slash-keyed.

Per ADR-069 / Critic B3 ACCEPTED-FIXED: _index.md dropped (Haiku-LLM-
dispatched by /archive skill per COST-1, not deterministic).
Per /design-slice Step 2 clarifying answer: methodology-changelog.md
dropped (PMI-1 5-leg atomic-bump risk on concurrent bumps).

Pinned by test_soft_file_set_is_two_canonical_files_forward_slash_keyed.
"""

_AUDIT_LOG_PATH: Path = VAULT_ROOT / "parallel-conflict-resolution-log.md"  # slice-098/ADR-089 Class-A ROUTE
"""Append-only audit log path (lazy-created on first append). slice-098/ADR-089:
composed from VAULT_ROOT (frozen-at-import). Consumed as ``repo_root / _AUDIT_LOG_PATH``
at 5 sites — byte-identical no-flip because VAULT_ROOT is the relative default
(pathlib discards ``repo_root`` if VAULT_ROOT is ever absolute/external)."""

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

_CLOCK_SKEW_TOLERANCE_SECONDS: int = 300
"""PCR-2a clock-skew guard tolerance (slice-084 / ADR-076).

A strict-newer VAULT_CLAIM winner whose ``Claimed-at`` exceeds the resolver's own
wall-clock by MORE than this many seconds is judged clock-skew-suspicious (its
claiming machine's clock runs ahead → the strict-newer win is untrustworthy) and
fails closed to a STOP that escalates to the PCR-2b gate. 300 s (5 min) absorbs
benign NTP jitter + in-flight claim->merge delay while staying well below R-23's
minutes-to-hours skew regime. Tunable; see ADR-076 for the over-trigger/under-detect
tradeoff. Pinned by test_tolerance_boundary_at_30{0,1}s_* (strict ``>``).
"""

_CONFLICT_MARKER_OPENER_RE = re.compile(r"(?m)^[ +-]?(?:<{7,}|>{7,}|\|{7,})(?:\s|$)")
r"""PCR-2b (slice-083 / ADR-075) HARD-resolution leftover-marker detector.

Per the B2 + M-add-1 /critique fixes: keys on the line-anchored ``<<<<<<<``
opener / ``>>>>>>>`` closer (runs of ``<``/``>``), which have NO legitimate
Markdown/source analog — DELIBERATELY NOT ``=======`` (the merge separator),
because a 7-or-more ``=`` run also matches a Markdown setext H1 underline and
``=======`` dividers, and ``git diff --cached --check`` inherits that same
``>=7-=`` false-positive heuristic. HARD U-files ARE markdown (ADR / SKILL.md /
changelog), so a ``=======``-based scan would false-STOP correct resolutions.

Per the slice-083 /code-review M2 fix: the run quantifier is ``{7,}`` (git's
own rule — a marker is SEVEN OR MORE of the char, not exactly seven), and the
``diff3`` / ``zdiff3`` base-section separator ``|||||||`` (``\|{7,}``) is in the
alternation — a user with ``merge.conflictStyle=diff3`` who removes the
``<<<<<<<`` / ``>>>>>>>`` lines but leaves the ``|||||||`` base block staged
would otherwise pass verify CLEAN with a leftover base-marker block. ``|||||||``
(7+ consecutive pipes) has no legitimate Markdown/source analog either (a
Markdown table separator is ``| --- | --- |``, never a 7-pipe run).

The optional leading ``[ +-]`` consumes the single ``git diff`` body column so a
marker on an added/context line (``+<<<<<<<`` / `` <<<<<<<``) is detected; diff
meta lines (``+++ b/…`` / ``--- a/…`` / ``@@ …``) do not match because the
char after the column is not a 7+-run of ``<``/``>``/``|``.
"""


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
    # True when a slice-queue.md conflict stage was PRESENT but non-UTF-8
    # (a _StageDecodeError during diagnose_conflict's stage reads). The claim
    # history can no longer be trusted, so classify_conflict fails closed to
    # UNKNOWN -> resolve_soft_conflict STOPs (R-30 residual #1 / ADR-083).
    # Defaulted so the existing 3-arg construction sites + synthetic-test
    # constructors stay valid (frozen+slots -> set via the constructor call,
    # never post-construction mutation).
    claim_extraction_degraded: bool = False


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
    claim_extraction_degraded = False
    if "architecture/slice-queue.md" in u_files:  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
        try:
            # Both stage reads are wrapped: an undecodable EITHER stage (2 or 3)
            # must degrade the diagnostic (m-add-2 — symmetric, not stage-2-only).
            text_2 = _git_show_stage(repo_root, 2, "architecture/slice-queue.md")  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
            text_3 = _git_show_stage(repo_root, 3, "architecture/slice-queue.md")  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
        except _StageDecodeError as exc:
            # A present-but-non-UTF-8 stage (R-30 residual #1 / ADR-083): the
            # claim history cannot be trusted, so mark the diagnostic degraded
            # -> classify_conflict fails closed to UNKNOWN -> resolve STOPs,
            # NEVER a silent auto-resolve that drops the claim. Record a
            # best-effort breadcrumb naming the undecodable stage + path; a
            # breadcrumb write failure must NEVER mask the fail-closed signal.
            claim_extraction_degraded = True
            try:
                _append_decode_stop_audit(repo_root, exc.stage, exc.path, str(exc))
            except Exception as audit_exc:  # noqa: BLE001 - best-effort by design
                print(
                    f"parallel-conflict-resolver: decode-STOP audit append "
                    f"failed (non-blocking): {audit_exc!r}",
                    file=sys.stderr,
                )
        else:
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
        claim_extraction_degraded=claim_extraction_degraded,
    )


def classify_conflict(diag: ConflictDiagnostic) -> ConflictClass:
    """Classify the conflict per ADR-069 5-class taxonomy.

    VAULT_CLAIM gate (per /critique B4 ACCEPTED-FIXED): if sole U-file
    is slice-queue.md AND any candidate name appears in BOTH branches'
    claim dicts with DIFFERENT Claimed-by values, returns VAULT_CLAIM.

    UNKNOWN gate (per /critique M4 ACCEPTED-FIXED): if rebase state is
    empty / unparseable, returns UNKNOWN. Fail-closed; NEVER silent-
    default to SOFT.

    DECODE-DEGRADED gate (R-30 residual #1 / ADR-083): if a slice-queue.md
    conflict stage was present-but-non-UTF-8 (diag.claim_extraction_degraded),
    the claim history is untrustworthy -> UNKNOWN. Same fail-closed channel as
    unparseable state; NEVER silent-default to SOFT on a degraded diagnostic.
    """
    if diag.claim_extraction_degraded:
        return ConflictClass.UNKNOWN

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
        if u_files_set == {"architecture/slice-queue.md"}:  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
            return ConflictClass.VAULT_CLAIM
        # SOFT (shippability.md) + VAULT_CLAIM (slice-queue.md) -> MIXED
        # (per /critique M4 disambiguation; atomicity prevails).
        return ConflictClass.MIXED

    return ConflictClass.SOFT


def _retire_if_vault_external(repo_root: Path) -> ResolutionResult | None:
    """slice-098 / [[ADR-089]] RETIRE-when-untracked guard for the SOFT/VAULT_CLAIM
    git-rebase conflict-resolution path.

    PCR's machinery is coupled to the in-tree vault: the Class-B git pathspecs
    (``_SOFT_FILE_SET`` / ``qrel`` / ``srel`` / ``git add``) are forward-slash
    ``architecture/...`` literals, while ``out_path`` routes via ``VAULT_ROOT``.
    When the vault is flipped to an external store, an in-tree rebase conflict on
    ``architecture/slice-queue.md`` would route ``out_path`` to the external path →
    ``out_path.relative_to(repo_root)`` raises ``ValueError`` → the equivalence
    guard's ``qrel``/``srel`` comparison is silently skipped AND the resolved
    content is written to the wrong place while ``git add`` stages the still-
    conflicted in-tree file (the /critique B2 corruption).

    Gate at resolve-ENTRY, BEFORE classify / any ``out_path`` composition, on the
    store-LOCATION signal ``vault_is_external`` — NOT a per-pathspec tracked-check,
    which returns True for the still-tracked in-tree file and MISSES this state
    (the slice-098 build-time refinement ratified into [[ADR-089]]; unified with
    ``stranded_slice_audit``'s guard). RETIRE visibly with an actionable operator
    breadcrumb (NEVER a silent claim-drop — R-7 / slice-090/091). Fires ONLY when
    VAULT_ROOT is external; the no-flip default path returns None → proceed.
    """
    if not vault_is_external(repo_root):
        return None
    return ResolutionResult(
        action="STOP",
        conflict_class=ConflictClass.UNKNOWN,
        regenerated_files=(),
        reason=(
            "vault is an external/untracked store (VAULT_ROOT resolves outside the "
            "repo work tree; post-flip per ADR-089). PCR's git-rebase conflict "
            "resolution is inapplicable — an untracked vault file has no rebase "
            "stage, and routing out_path externally would corrupt the in-tree git "
            "state. RETIRE: resolve vault write-races via the _vault_write sidecar "
            "lock per the external-vault flip slice; do NOT git-merge the vault file."
        ),
    )


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

    # slice-098 / [[ADR-089]]: RETIRE-when-external at resolve-ENTRY, BEFORE
    # classify / any out_path composition (the /critique B2 guard placement).
    _retired = _retire_if_vault_external(repo_root)
    if _retired is not None:
        return _retired

    cls = classify_conflict(diag)
    # PCR-2a B3 ACCEPTED-FIXED: new VAULT_CLAIM dispatch branch ABOVE the
    # existing `if cls is not ConflictClass.SOFT:` guard. The CLI path
    # through --resolve-soft (skills/commit-slice/SKILL.md sub-step 2.5)
    # calls THIS function first; without this branch VAULT_CLAIM would
    # short-circuit at L243 to STOP before reaching the defense-in-depth
    # backstop in _regen_slice_queue.
    if cls is ConflictClass.VAULT_CLAIM:
        return resolve_vault_claim_conflict(diag, repo_root)

    # PCR-2b (slice-083 / ADR-075): HARD + MIXED dispatch to the gate-on-hand-
    # resolve path. resolve_hard_conflict returns a STOP carrying gate context;
    # it NEVER auto-merges or runs git rebase --continue. The skill
    # (skills/commit-slice/SKILL.md sub-step 2.5) drives the resolution flow.
    # MIXED routes here too (atomicity per ADR-069 MIXED row).
    if cls in (ConflictClass.HARD, ConflictClass.MIXED):
        return resolve_hard_conflict(diag, repo_root)

    if cls is not ConflictClass.SOFT:
        # Only UNKNOWN reaches here (VAULT_CLAIM / HARD / MIXED dispatched above).
        reason = (
            f"non-SOFT class ({cls.value}) - fall through to SOAD-1 STOP "
            f"per ADR-069 fail-closed (never silent-default to SOFT)"
        )
        return ResolutionResult(
            action="STOP",
            conflict_class=cls,
            regenerated_files=(),
            reason=reason,
        )

    # SOFT path: stage-then-commit atomicity (fix M2 / code-review post-Phase-G).
    # Helpers RETURN (Path, str) pairs without writing to disk. Only if ALL
    # helpers succeed do we batch-write + git add + git rebase --continue.
    # If any helper raises _SoftResolutionError mid-loop, the working tree is
    # left UNTOUCHED — preserving conflict markers + falling through to the
    # existing SOAD-1 STOP. Defeats the silent partial-resolution path where
    # slice-queue.md would be overwritten with overlay content while
    # shippability.md's HARD-escalation returns STOP.
    pending_writes: list[tuple[Path, str]] = []
    try:
        for u_file in diag.u_files:
            if u_file == "architecture/slice-queue.md":  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
                pending_writes.append(_regen_slice_queue(repo_root, diag))
            elif u_file == "architecture/shippability.md":  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
                pending_writes.append(_merge_shippability(repo_root))
    except _VaultClaimDispatch:
        # PCR-2a B3 ACCEPTED-FIXED: defense-in-depth gate in
        # _regen_slice_queue detected VAULT_CLAIM via the actual queue
        # text after upstream classify_conflict had returned SOFT (silent-
        # classify-bypass corner case). Reroute to the public VAULT_CLAIM
        # resolver — no SOFT writes occurred (the sentinel raised before
        # any pending_writes append for slice-queue.md).
        return resolve_vault_claim_conflict(diag, repo_root)
    except _SoftResolutionError as exc:
        # _regen_slice_queue or _merge_shippability surfaced a structural
        # issue (e.g., both stages missing; same-slice-number-different-
        # content escalating to HARD; same-candidate-different-identity
        # claim escalating to VAULT_CLAIM per defense-in-depth M3 gate).
        # Fall-closed STOP — NO writes occurred per stage-then-commit
        # atomicity, no staging, no rebase --continue.
        return ResolutionResult(
            action="STOP",
            conflict_class=exc.conflict_class,
            regenerated_files=(),
            reason=str(exc),
        )

    if not pending_writes:
        return ResolutionResult(
            action="STOP",
            conflict_class=ConflictClass.UNKNOWN,
            regenerated_files=(),
            reason="SOFT classification but no files regenerated - rebase state unexpected",
        )

    # ADR-074 / R-21 fix-class (b): SOFT equivalence guard. Read-only structural
    # verification that the regenerated pending content is in a deterministic
    # equivalence class against both rebase stages. Runs ONLY on the all-SOFT-
    # helpers-succeeded path (the _VaultClaimDispatch / _SoftResolutionError handlers
    # above already returned; the empty-check above already returned), strictly
    # BEFORE the first write_text / git add / git rebase --continue — so a guard-STOP
    # mutates no tracked conflict state (atomicity per ADR-069). It reuses
    # _SoftResolutionError (NOT a new exception class — m1) caught by this local
    # try/except: the original loop-try (L274-300) has already closed before the
    # empty-check, so the guard's pinned post-empty-check call-site (M3) needs its
    # own catch. _verify_soft_equivalence appends a best-effort audit-log STOP entry
    # before raising (AC-3).
    try:
        _verify_soft_equivalence(repo_root, diag, pending_writes)
    except _SoftResolutionError as exc:
        return ResolutionResult(
            action="STOP",
            conflict_class=exc.conflict_class,
            regenerated_files=(),
            reason=str(exc),
        )

    # Commit phase: all helpers succeeded — write all resolved content
    # atomically with newline="" for LF-only byte-deterministic emission
    # on Windows (mirrors tools/slice_queue_writer.py:790 +
    # tools/slice_queue_claim.py:535 PSQ-2 LF-discipline; fixes M1 /
    # EOL-DRIFT-1 / ADR-033 — default Path.write_text newline=None
    # translates \n to os.linesep on Windows producing CRLF).
    regenerated: list[str] = []
    for out_path, content in pending_writes:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8", newline="")
        regenerated.append(out_path.relative_to(repo_root).as_posix())

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
            env={**os.environ, "GIT_EDITOR": "true"},
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


class _StageDecodeError(_SoftResolutionError):
    """A conflict stage is PRESENT but its bytes are not valid UTF-8.

    Raised by ``_git_show_stage`` when ``git show :<stage>:<path>`` succeeds
    (exit 0, the blob exists) but the captured bytes fail a strict UTF-8
    decode (R-30 residual #1 / ADR-083). This is the fail-closed signal that
    REPLACES the pre-fix silent falsy return (Windows reader-thread swallow ->
    ``None``) / uncaught ``UnicodeDecodeError`` (POSIX). A non-UTF-8 stage
    cannot be trusted for claim extraction, so the claim history is degraded
    and the conflict must fall to a fail-closed UNKNOWN STOP -- NEVER a silent
    auto-resolve that re-opens the VAULT_CLAIM bypass.

    SUBCLASSES ``_SoftResolutionError`` (carrying ``ConflictClass.UNKNOWN``)
    deliberately: the existing ``except _SoftResolutionError`` handler in
    ``resolve_soft_conflict`` (the ``_regen_slice_queue`` defense-in-depth
    call site) then converts it to a ``STOP(UNKNOWN)`` with no new plumbing.
    Carries ``stage`` + ``path`` for the audit breadcrumb.
    """

    def __init__(self, message: str, stage: int, path: str):
        super().__init__(message, ConflictClass.UNKNOWN)
        self.stage = stage
        self.path = path


class _VaultClaimDispatch(Exception):
    """PCR-2a sentinel: _regen_slice_queue's defense-in-depth gate detected
    a VAULT_CLAIM collision in the actual queue text after classify_conflict
    returned SOFT (silent-classify-bypass corner case — e.g., diag's
    claim_history was constructed without parse_queue_text via ImportError).

    Raised by _regen_slice_queue (replacing the old _SoftResolutionError(
    VAULT_CLAIM) raise per AC#2). Caught by resolve_soft_conflict's
    exception loop, which reroutes to resolve_vault_claim_conflict.

    Carries no payload — the dispatch target re-collects collisions from
    diag.claim_history directly (already populated by diagnose_conflict).
    """

    # catch-order invariant (Fix R / slice-078 m5): _VaultClaimDispatch is a
    # SIBLING of _SoftResolutionError — both inherit directly from Exception, with
    # no inheritance relationship between them. The except-clause order in
    # resolve_soft_conflict's exception loop is therefore semantically INDEPENDENT
    # (not load-bearing by inheritance); a future maintainer may reorder those
    # except clauses without changing behavior.


def _collect_same_candidate_different_identity(
    claim_history: tuple[ClaimEntry, ...] | list[ClaimEntry],
) -> list[tuple[str, ClaimEntry, ClaimEntry]]:
    """Enumerate every same-candidate-different-identity collision in claim_history.

    Per PCR-2a m2 ACCEPTED-FIXED: returns the list (not just bool) so
    resolve_vault_claim_conflict can detect multi-candidate STOP at
    Resolution algorithm step 1. The PCR-1 _has_same_candidate_different_identity
    consumer (classify_conflict) is preserved as a thin bool wrapper below.

    Returns list of (candidate_name, stage_2_entry, stage_3_entry) tuples.
    """
    by_name: dict[str, dict[int, ClaimEntry]] = {}
    for entry in claim_history:
        by_name.setdefault(entry.candidate_name, {})[entry.branch_stage] = entry
    collisions: list[tuple[str, ClaimEntry, ClaimEntry]] = []
    for name, stages in by_name.items():
        e2 = stages.get(2)
        e3 = stages.get(3)
        if e2 is not None and e3 is not None and e2.claimed_by != e3.claimed_by:
            collisions.append((name, e2, e3))
    return collisions


def _has_same_candidate_different_identity(
    claim_history: tuple[ClaimEntry, ...],
) -> bool:
    """Thin bool wrapper preserving the classify_conflict consumer API
    (PCR-1 / /critique B4 ACCEPTED-FIXED). Returns True iff at least one
    same-candidate-different-identity collision is present.
    """
    return bool(_collect_same_candidate_different_identity(claim_history))


def _select_timestamp_winner(
    collisions: list[tuple[str, ClaimEntry, ClaimEntry]],
) -> tuple[ClaimEntry, ClaimEntry] | None:
    """Strict-newer Claimed-at winner selection for VAULT_CLAIM resolution.

    Per PCR-2a Resolution algorithm step 2:
      - len(collisions) > 1 → caller translates to multi-candidate STOP
        (this helper returns None on that path to keep its contract simple;
        the caller checks len(collisions) BEFORE calling this helper).
      - len(collisions) == 1: select winner by strictly-newer claimed_at
        (ISO-8601 lexicographic ordering, valid for UTC RFC-3339 strings).
      - Equal claimed_at (tie) → returns None (strict-newer rule yields no winner).

    Returns (winner_entry, loser_entry) on success, or None on tie.
    """
    if len(collisions) != 1:
        return None
    _name, e2, e3 = collisions[0]
    if e2.claimed_at == e3.claimed_at:
        return None
    if e2.claimed_at > e3.claimed_at:
        return (e2, e3)
    return (e3, e2)


def _winner_clock_skew_suspect(
    winner: ClaimEntry,
    now: datetime.datetime,
    tolerance_seconds: int,
) -> str | None:
    """PCR-2a Step 2.5 clock-skew guard (slice-084 / ADR-076).

    Returns a human-readable STOP reason if the strict-newer ``winner``'s
    ``Claimed-at`` is implausible relative to ``now`` (the resolver's own trusted
    wall-clock), else ``None`` (plausible — caller proceeds to strict-newer resolution).

    Three fail-closed outcomes (per /critique B1/B2 APED-1 findings):
      - **unparseable** as ISO-8601 → STOP (cannot verify).
      - **tz-naive** (offset-less — ``fromisoformat`` parses it *successfully* as a
        naive datetime, after which ``naive > aware`` would raise ``TypeError`` mid-
        rebase) → STOP, treated identically to unparseable. NEVER a crash.
      - **future-dated** beyond ``tolerance_seconds`` (a claim is made before it is
        merged, so a winner stamped in the future of ``now`` reveals an ahead-running
        claiming clock) → STOP, the skew-suspicious case.

    Only the *selected winner* is checked: if the skewed entry is the loser, the winner
    is the genuinely-newer non-skewed claim → correct result → no flag. This catches the
    future-dated sub-case of R-23; the staler-but-past case is undetectable from a single
    trusted clock and remains an explicit R-23 residual (ADR-076 §Consequences).
    """
    raw = winner.claimed_at.strip()
    # B2: datetime.fromisoformat did not accept the RFC-3339 `Z`/`z` UTC designator until
    # Python 3.11; project floor is >=3.10 (pyproject.toml). Normalize the `Z` token so the
    # gate treats it identically on every >=3.10 interpreter. RFC-3339 §5.6 makes the
    # designator case-INsensitive, so accept lowercase `z` too (/code-review M1). Scope note
    # (/code-review M2): this normalization covers ONLY the `Z`/`z` token — it does NOT make
    # the broader `fromisoformat` acceptance surface version-uniform (3.11 relaxed parsing of
    # offset-without-colon `+0000` + space-separated stamps, cpython#115783), so on a 3.10
    # interpreter those relaxed forms hit the except branch below and fail-closed STOP. That
    # is the SAFE direction (no crash, no skewed write); PSQ-2's canonical writer emits a
    # `+00:00` second-precision stamp that parses identically on all >=3.10.
    if raw[-1:] in ("Z", "z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.datetime.fromisoformat(raw)
    except (ValueError, TypeError):
        return (
            f"clock-skew guard: winner Claimed-at unparseable as ISO-8601 "
            f"({winner.claimed_at!r}) — cannot verify against resolver-now; fail-closed "
            f"STOP, escalate to PCR-2b hand-resolve + TRI-RESOLVE-1"
        )
    # B1: an offset-less timestamp parses as a naive datetime; comparing naive > aware
    # raises TypeError. Treat naive identically to unparseable → fail-closed (no crash).
    if parsed.tzinfo is None:
        return (
            f"clock-skew guard: winner Claimed-at lacks a timezone offset "
            f"({winner.claimed_at!r}) — cannot compare against the timezone-aware "
            f"resolver-now; fail-closed STOP, escalate to PCR-2b hand-resolve + TRI-RESOLVE-1"
        )
    if parsed > now + datetime.timedelta(seconds=tolerance_seconds):
        return (
            f"clock-skew suspected: winner Claimed-at {winner.claimed_at} is future-dated "
            f"vs resolver-now {now.isoformat()} beyond {tolerance_seconds}s tolerance — the "
            f"claiming machine's clock runs ahead, so the strict-newer win is untrustworthy; "
            f"escalate to PCR-2b hand-resolve + TRI-RESOLVE-1"
        )
    return None


def _append_skew_stop_audit(
    repo_root: Path,
    reason: str,
    winner: ClaimEntry,
    loser: ClaimEntry,
    now: datetime.datetime,
) -> None:
    """Append a clock-skew guard-STOP entry to the audit log (best-effort; ADR-076 / AC-2).

    Distinct section variant ``## Vault-claim resolution (clock-skew STOP) - <ts>`` so a
    skew-STOP is recoverable from the audit trail. Records BOTH claims' Claimed-by/Claimed-at
    (R-23 corrigibility hook) + the resolver-now signal rendered via ``now.isoformat()``
    (aware `+00:00`, byte-comparable to the canonical Claimed-at format — /critique-review
    m-add-2). Mirrors ``_append_equivalence_stop_audit`` (ADR-074 / slice-082).
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
            encoding="utf-8",
            check=True,
        )
        head_sha = head_proc.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        head_sha = "(unavailable)"

    entry = (
        f"## Vault-claim resolution (clock-skew STOP) - {timestamp}\n"
        "\n"
        f"**Repo HEAD SHA pre-resolution**: {head_sha}\n"
        f"**Candidate name**: {winner.candidate_name}\n"
        f"**Winner Claimed-by**: {winner.claimed_by}\n"
        f"**Winner Claimed-at**: {winner.claimed_at}\n"
        f"**Loser Claimed-by**: {loser.claimed_by}\n"
        f"**Loser Claimed-at**: {loser.claimed_at}\n"
        f"**Resolver-now signal**: {now.isoformat()}\n"
        "**Outcome**: STOP (fail-closed, no writes) per ADR-076 PCR-2a clock-skew guard\n"
        f"**Reason**: {reason}\n\n"
    )

    needs_header = not log_path.exists()
    with log_path.open("a", encoding="utf-8", newline="") as f:
        if needs_header:
            f.write(_AUDIT_LOG_HEADER)
        f.write(entry)


def _append_decode_stop_audit(
    repo_root: Path,
    stage: int,
    path: str,
    reason: str,
) -> None:
    """Append a non-UTF-8-stage decode-failure STOP entry to the audit log.

    Best-effort (ADR-083 / R-30 residual #1) -- mirrors ``_append_skew_stop_audit``
    (ADR-076). Distinct section variant ``## Decode-failure STOP (non-UTF-8
    stage) - <ts>`` so the silent claim-drop made-visible is recoverable from
    the audit trail: it names the undecodable ``stage`` + ``path`` so an
    operator knows WHICH conflict stage could not be decoded. The caller wraps
    this in its own try/except -- a write failure here NEVER masks the
    fail-closed STOP.
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
            encoding="utf-8",
            check=True,
        )
        head_sha = head_proc.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        head_sha = "(unavailable)"

    entry = (
        f"## Decode-failure STOP (non-UTF-8 stage) - {timestamp}\n"
        "\n"
        f"**Repo HEAD SHA pre-resolution**: {head_sha}\n"
        f"**Undecodable stage**: {stage}\n"
        f"**Path**: {path}\n"
        "**Outcome**: STOP (fail-closed, no writes) per ADR-083 -- claim "
        "extraction degraded -> UNKNOWN\n"
        f"**Reason**: {reason}\n\n"
    )

    needs_header = not log_path.exists()
    with log_path.open("a", encoding="utf-8", newline="") as f:
        if needs_header:
            f.write(_AUDIT_LOG_HEADER)
        f.write(entry)


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
            encoding="utf-8",
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
            # Defensive (fix m5 / code-review): rename-with-conflict produces
            # `ORIG -> NEW` shape; rare but real with rerere or partial-
            # rename + concurrent edits. Semantics unclear for SOFT-class
            # auto-resolution — escalate to UNKNOWN per APED-1 loud-malformed
            # rather than silently corrupt the path-string match.
            if " -> " in path:
                print(
                    f"parallel-conflict-resolver: rename-with-conflict on "
                    f"{path!r} — escalating to UNKNOWN per APED-1 loud-malformed "
                    f"(semantics unclear; manual resolution required)",
                    file=sys.stderr,
                )
                return ()
            u_files.append(path)
    return tuple(u_files)


def _git_show_stage(repo_root: Path, stage: int, path: str) -> str:
    """Read `git show :<stage>:<path>` for the named conflict stage.

    Three outcomes (ADR-083 — R-30 residual #1 hardened):

    - **Stage absent** (subprocess failure — e.g. a file added on only one
      branch, ``git show`` exits non-zero): returns ``""``. The caller handles
      the asymmetric-stage case via the documented falsy guard.
    - **Stage present and decodable**: returns the UTF-8-decoded blob content.
    - **Stage present but NON-UTF-8**: raises ``_StageDecodeError(stage, path)``
      (a ``_SoftResolutionError(UNKNOWN)``). It does NOT return a falsy value
      and does NOT let a raw ``UnicodeDecodeError`` escape.

    Implementation: capture git's output as **bytes** (NOT ``text=True`` — the
    pre-fix text-mode decode happened in subprocess's pipe-reader thread, which
    swallowed a ``UnicodeDecodeError`` to ``stdout=None`` on Windows and
    propagated it uncaught on POSIX) and decode it explicitly with strict
    UTF-8 in the main thread, where the failure is catchable and converts to a
    controlled fail-closed STOP. A non-UTF-8 stage is therefore never silently
    dropped into the caller's ``parse_queue_text(text) if text else {}`` guard
    (which would re-open the VAULT_CLAIM claim-drop bypass).

    This is a byte-mode ``subprocess.run`` site that decodes EXPLICITLY -- it
    deliberately carries NO ``encoding=`` (the decode is the ``.decode`` call
    below), so the slice-090 / ADR-082 "byte-mode git sites carry no encoding="
    invariant still holds for it.
    """
    try:
        proc = subprocess.run(
            ["git", "show", f":{stage}:{path}"],
            cwd=str(repo_root),
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    try:
        return proc.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _StageDecodeError(
            f"git show :{stage}:{path} produced non-UTF-8 bytes -- the conflict "
            f"stage is present but cannot be decoded; claim extraction is "
            f"untrustworthy, fail-closed to UNKNOWN STOP (ADR-083): {exc}",
            stage,
            path,
        ) from exc


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
    slices_dir = repo_root / VAULT_ROOT / "slices"  # slice-098/ADR-089 Class-A ROUTE
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
            mission_brief_link=f"architecture/slices/{name}/mission-brief.md",  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
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
            encoding="utf-8",
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
        from tools.slice_queue_claim import (  # noqa: PLC0415
            ClaimUsageError,
            parse_queue_text,
        )
    except ImportError as exc:
        print(
            f"parallel-conflict-resolver: slice_queue_claim.parse_queue_text "
            f"unavailable: {exc!r}",
            file=sys.stderr,
        )
        return ({}, {})

    # Narrowed exception (fix m2 / code-review): parse_queue_text's
    # documented contract per tools/slice_queue_claim.py:218 raises
    # ClaimUsageError ONLY on partial known claim block. Broader catches
    # (AttributeError, etc.) would mask programming errors in parse_queue_text
    # itself + silently compound with the M3 VAULT_CLAIM gate (silent failure
    # here → claim_history empty → upstream classify gate misses → VAULT_CLAIM
    # collision silently auto-resolves). The M3 in-helper gate in
    # _regen_slice_queue is the defense-in-depth backstop; this narrowing is
    # the upstream fix at root cause.
    try:
        claims_2 = parse_queue_text(text_2) if text_2 else {}
    except ClaimUsageError as exc:
        print(
            f"parallel-conflict-resolver: stage 2 queue parse failed "
            f"(ClaimUsageError, partial claim block): {exc!r}",
            file=sys.stderr,
        )
        claims_2 = {}
    try:
        claims_3 = parse_queue_text(text_3) if text_3 else {}
    except ClaimUsageError as exc:
        print(
            f"parallel-conflict-resolver: stage 3 queue parse failed "
            f"(ClaimUsageError, partial claim block): {exc!r}",
            file=sys.stderr,
        )
        claims_3 = {}
    return (claims_2, claims_3)


def _regen_slice_queue(
    repo_root: Path, diag: ConflictDiagnostic
) -> tuple[Path, str]:
    """Regenerate architecture/slice-queue.md via textual claim-overlay.

    Per /critique-review M-add-1 ACCEPTED-FIXED option (2): take
    rebase-target's queue text (git show :3:) verbatim as the result
    baseline; overlay merged claims via _overlay_claims_on_queue_text;
    NO write_slice_queue round-trip (avoids the B1 phantom-parser trap).

    Returns (out_path, resolved_content) — does NOT write to disk.
    Caller (resolve_soft_conflict) accumulates returns from all helpers
    + batch-writes only if ALL succeed (stage-then-commit atomicity per
    fix M2 / code-review).
    """
    text_2 = _git_show_stage(repo_root, 2, "architecture/slice-queue.md")  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
    text_3 = _git_show_stage(repo_root, 3, "architecture/slice-queue.md")  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)

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

    # Defense-in-depth VAULT_CLAIM gate (fix M3 / code-review; per
    # design.md L136 Resolution algorithm step 3 of 5 + critique.md B4
    # fix (c) ACCEPTED-FIXED). classify_conflict's upstream gate via
    # _has_same_candidate_different_identity(diag.claim_history) can be
    # bypassed if (a) _extract_claim_diff failed silently (partial-claim
    # ClaimUsageError), or (b) diag was constructed from stale state
    # (CLI piping --diagnose JSON into separate classify). The design
    # explicitly mandates this in-helper re-validation:
    # "defense-in-depth defeats this here". Same-candidate-different-
    # identity → VAULT_CLAIM (deferred to PCR-2 / slice-077 for
    # timestamp-winner + light Critic); never silently auto-resolve.
    for name in set(claims_2) & set(claims_3):
        cb2 = claims_2[name].get("claimed_by")
        cb3 = claims_3[name].get("claimed_by")
        if cb2 and cb3 and cb2 != cb3:
            # PCR-2a B3 ACCEPTED-FIXED: raise _VaultClaimDispatch sentinel
            # (was: _SoftResolutionError(VAULT_CLAIM)). The defense-in-depth
            # gate detected a collision the upstream classify_conflict
            # missed (silent-classify-bypass corner case — e.g., diag's
            # claim_history was empty due to ImportError in
            # _extract_claim_diff). resolve_soft_conflict catches the
            # sentinel and reroutes to resolve_vault_claim_conflict.
            # The UNKNOWN-class raise leg at L605-609 is UNCHANGED.
            raise _VaultClaimDispatch()

    merged_claims = _merge_claim_dicts(claims_2, claims_3)

    overlaid = _overlay_claims_on_queue_text(baseline_text, merged_claims)

    out_path = repo_root / VAULT_ROOT / "slice-queue.md"  # slice-098/ADR-089 Class-A ROUTE
    return (out_path, overlaid)


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
    # Fix m3 / code-review: track candidates seen + candidates with claim
    # actually inserted. If a candidate's block omits the canonical
    # `Risk-retired:` line (malformed PSQ-1 5-field shape), the post-emit
    # insertion hook never fires and the claim is silently dropped. Warn
    # loudly per APED-1 loud-malformed criterion at end-of-walk.
    candidates_seen: set[str] = set()
    claim_inserted_for: set[str] = set()

    for line in lines:
        # ### <name> heading -> update tracking, emit line.
        if line.startswith("### "):
            current_candidate = line[4:].strip()
            candidates_seen.add(current_candidate)
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
                claim_inserted_for.add(current_candidate)

    # Fix m3 / code-review: warn on silently-dropped claims. A candidate
    # present in queue_text + in merged_claims but with no `Risk-retired:`
    # line in its block → claim metadata silently lost. Per APED-1 loud-
    # malformed: surface to stderr rather than silent drop. Orphan claims
    # (in merged_claims but candidate not in queue_text at all) remain the
    # documented behavior per design.md L137 ("dropped — will re-surface
    # at next /slice regen") and are NOT warned about here.
    dropped_due_to_malformed_block = (
        set(merged_claims) & candidates_seen
    ) - claim_inserted_for
    for name in sorted(dropped_due_to_malformed_block):
        print(
            f"parallel-conflict-resolver: claim for candidate {name!r} "
            f"silently dropped — candidate block in queue_text is missing the "
            f"`- **Risk-retired:**` line (post-emit insertion hook never fired). "
            f"Per APED-1 loud-malformed: this indicates a non-canonical "
            f"PSQ-1 5-field entry shape; manual review recommended.",
            file=sys.stderr,
        )

    return "\n".join(result_lines)


class _QueueCandidate(NamedTuple):
    """One parsed slice-queue candidate: (name, parallel_safety, is_claimed).

    A NamedTuple (Fix P / slice-078 m2): tuple-compatible (existing equality-based
    tests + ``_pick_loser_replacement``'s positional unpacking are unaffected) while
    also exposing ``.name`` / ``.parallel_safety`` / ``.is_claimed`` attribute access.
    """

    name: str
    parallel_safety: str
    is_claimed: bool


def _parse_queue_candidates_for_replacement(
    text: str,
) -> list[_QueueCandidate]:
    """Parse slice-queue.md text → ordered (name, parallel_safety, is_claimed) list.

    Per PCR-2a B1 ACCEPTED-FIXED: tools/slice_queue_writer.py exposes no
    public parser, and tools.slice_queue_claim.parse_queue_text explicitly
    strips Parallel-safety (docstring at slice_queue_claim.py:230-234).
    This file-local helper fills the gap with a regex-based, file-order-
    preserving parser scoped to (name, parallel_safety, is_claimed).

    File order = priority (top of queue = highest priority candidate).
    A candidate is `is_claimed=True` iff its block contains a
    `- **Claimed-by:**` line; `claimed_at` is not surfaced (replacement
    logic only needs unclaimed-detection).
    """
    if not text:
        return []
    import re as _re

    out: list[_QueueCandidate] = []
    current_name: str | None = None
    current_safety: str | None = None
    current_claimed: bool = False

    def _flush() -> None:
        nonlocal current_name, current_safety, current_claimed
        if current_name is not None:
            out.append(_QueueCandidate(
                current_name,
                # Fix P (slice-078 m2): a missing `**Parallel-safety:**` field gets the
                # distinct `MISSING-FIELD` sentinel — NOT `UNKNOWN-NO-GRAPH`, which is a
                # real PSQ-1 enumeration value (overloading it conflated two states).
                current_safety if current_safety is not None else "MISSING-FIELD",
                current_claimed,
            ))
        current_name = None
        current_safety = None
        current_claimed = False

    for line in text.split("\n"):
        if line.startswith("### "):
            _flush()
            current_name = line[4:].strip()
            current_safety = None
            current_claimed = False
            continue
        m = _re.match(r"- \*\*Parallel-safety:\*\* (\S+)", line)
        if m and current_name is not None:
            current_safety = m.group(1)
            continue
        if current_name is not None and line.startswith("- **Claimed-by:**"):
            current_claimed = True
    _flush()
    return out


def _pick_loser_replacement(
    queue_text: str,
    exclude_names: set[str],
) -> str | None:
    """Return highest-priority unclaimed NON-OVERLAPPING candidate name, or None.

    Per PCR-2a M-add-2 ACCEPTED-FIXED: reads ONLY the in-memory queue_text
    arg — does NOT take repo_root, does NOT read from disk. The caller
    (Resolution algorithm step 4) passes the post-overlay in-memory text
    from step 3; disk-read during VAULT_CLAIM rebase-in-progress would
    encounter git's <<<<<<< conflict markers around slice-queue.md (the
    U-file) and silently parse only the non-conflicted portion → return
    None even when valid candidates exist.

    Filter: `Parallel-safety: NON-OVERLAPPING` AND `Claimed-by:` absent
    AND name not in `exclude_names`.

    Returns the first satisfying candidate name (file order = priority),
    or None when no candidate satisfies (audit-row sentinel `none-available`).
    """
    for name, safety, is_claimed in _parse_queue_candidates_for_replacement(queue_text):
        if name in exclude_names:
            continue
        # Fix P (slice-078 m2): reject everything outside the NON-OVERLAPPING allow-set —
        # this rejects `MISSING-FIELD`, `UNKNOWN-NO-GRAPH`, `UNKNOWN-NO-HINT-FILES`, and
        # `OVERLAPS-WITH-*` identically (semantically equivalent reject; observability gain
        # from distinguishing the sentinels upstream).
        if safety not in {"NON-OVERLAPPING"}:
            continue
        if is_claimed:
            continue
        return name
    return None


def _format_vault_claim_audit_entry(
    diag: ConflictDiagnostic,
    result: ResolutionResult,
    timestamp: str,
    head_sha: str,
    winner: ClaimEntry | None,
    loser: ClaimEntry | None,
) -> str:
    """Build the 8-field VAULT_CLAIM audit-log section.

    Per PCR-2a AC#4 + M2 ACCEPTED-FIXED: section heading is
    ``## Vault-claim resolution - <ISO-8601 UTC>`` (UNIFORM hyphen-space
    separator with PCR-1 SOFT row; section-type distinguished at the
    prefix word `Vault-claim` vs `Soft-conflict`).

    Winner/loser are PASSED IN by the single computation site in
    `_append_audit_log` (Fix O / slice-078 m1 DRY): the formatter no longer
    re-derives them from `diag.claim_history` via
    `_collect_same_candidate_different_identity` + `_select_timestamp_winner`.
    A future selection-semantic change then updates one site, not two. (The R-23
    clock-skew corner case was addressed at slice-084 / ADR-076 NOT by a PSQ-2
    `Claim-seq` tiebreaker — rejected: a per-machine seq is not cross-machine
    comparable — but by a resolver-now future-dating guard at Step 2.5 that STOPs
    *before* this APPLIED-path formatter runs.) `diag` is retained as
    the conflict context for call-site uniformity + future use. Replacement is
    parsed from result.reason via the canonical `replacement=<name>` token;
    absent → audit-row sentinel `none-available`.
    """
    import re as _re

    candidate_name = winner.candidate_name if winner is not None else "(unknown)"
    if winner is not None and loser is not None:
        winner_by = winner.claimed_by
        winner_at = winner.claimed_at
        loser_by = loser.claimed_by
        loser_at = loser.claimed_at
    else:  # pragma: no cover
        # Defensive fallback: preserves robustness to None inputs for callers
        # outside the canonical SOFT/VAULT_CLAIM resolve loop. No current caller
        # exercises this branch (the resolver always passes a well-formed
        # single-collision strict-newer winner/loser pair), but the defensive
        # shape documents the contract that the helper IS robust to None inputs.
        winner_by = winner_at = loser_by = loser_at = "(unavailable)"

    # Replacement encoded by resolve_vault_claim_conflict in result.reason
    # as `replacement=<name>` (or `replacement=none-available`).
    replacement = "none-available"
    if result.reason:
        m = _re.search(r"replacement=(\S+)", result.reason)
        if m:
            replacement = m.group(1)

    action_lines: list[str] = []
    for f in result.regenerated_files:
        if f == "architecture/slice-queue.md":  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
            action_lines.append(
                f"- `{f}` - winner identity preserved via strict-newer Claimed-at "
                "+ _overlay_claims_on_queue_text"
            )
        else:
            action_lines.append(f"- `{f}` - regenerated")

    return (
        f"## Vault-claim resolution - {timestamp}\n"
        "\n"
        f"**Repo HEAD SHA pre-resolution**: {head_sha}\n"
        f"**Candidate name**: {candidate_name}\n"
        f"**Winner Claimed-by**: {winner_by}\n"
        f"**Winner Claimed-at**: {winner_at}\n"
        f"**Loser Claimed-by**: {loser_by}\n"
        f"**Loser Claimed-at**: {loser_at}\n"
        f"**Loser auto-re-pick**: {replacement}\n"
        f"**Resolution actions**:\n"
        + ("\n".join(action_lines) if action_lines else "(none)")
        + "\n\n"
    )


def resolve_vault_claim_conflict(
    diag: ConflictDiagnostic,
    repo_root: Path | None = None,
    now: datetime.datetime | None = None,
) -> ResolutionResult:
    """Resolve a VAULT_CLAIM-class conflict via strict-newer timestamp-winner.

    Per PCR-2a (slice-078 / ADR-071) + the slice-084 / ADR-076 clock-skew guard,
    Resolution algorithm per design.md §Resolution algorithm:

      1. Collect collisions; STOP on multi or empty (caller misuse).
      2. Select strict-newer winner; STOP on tie.
      2.5. Clock-skew guard (ADR-076): if the winner's Claimed-at is future-dated
         vs the resolver's own wall-clock (``now``) beyond tolerance, or is
         unparseable / tz-naive, STOP fail-closed + escalate to PCR-2b. ``now``
         defaults to the real UTC wall-clock; injectable for tests.
      3. Read stage 2/3 baselines; overlay winner identity onto baseline;
         defensive post-overlay regex verifies the winner's claim landed
         (M-add-1: catches `_overlay_claims_on_queue_text` silent-drop on
         malformed candidate blocks).
      4. Read-only loser-replacement from in-memory overlaid text
         (M-add-2: NOT disk-read during VAULT_CLAIM rebase-in-progress).
      5. Atomic write + git add + git rebase --continue.
      6. Best-effort audit-log append.
      7. Return APPLIED.

    Step 5 atomicity note (Fix Q / slice-078 m3): this path writes the resolved
    slice-queue.md inline (single ``write_text`` + ``git add`` + ``git rebase
    --continue``) rather than batching through PCR-1's pending_writes accumulator.
    Single-file scope → an inline write is acceptable here; PCR-1's pending_writes
    batching addressed multi-file partial-resolution windows (the SOFT path
    regenerates slice-queue.md AND shippability.md) that do not apply to the
    single-file VAULT_CLAIM path.
    """
    import re as _re

    if repo_root is None:
        repo_root = Path.cwd()
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)

    # slice-098 / [[ADR-089]]: RETIRE-when-external at resolve-ENTRY (defense-in-depth
    # for direct calls; resolve_soft_conflict already guards the CLI dispatch path).
    _retired = _retire_if_vault_external(repo_root)
    if _retired is not None:
        return _retired

    # Step 1: Collect collisions
    collisions = _collect_same_candidate_different_identity(diag.claim_history)
    if len(collisions) > 1:
        return ResolutionResult(
            action="STOP",
            conflict_class=ConflictClass.VAULT_CLAIM,
            regenerated_files=(),
            reason=(
                "multi-candidate VAULT_CLAIM collision — sequential auto-"
                "resolution deferred to PCR-2b"
            ),
        )
    if len(collisions) == 0:
        return ResolutionResult(
            action="STOP",
            conflict_class=ConflictClass.UNKNOWN,
            regenerated_files=(),
            reason=(
                "VAULT_CLAIM dispatch without same-candidate-different-"
                "identity claim collision — diag/class disagree, fail-closed"
            ),
        )

    # Step 2: Select winner; STOP on tie
    winner_loser = _select_timestamp_winner(collisions)
    if winner_loser is None:
        return ResolutionResult(
            action="STOP",
            conflict_class=ConflictClass.VAULT_CLAIM,
            regenerated_files=(),
            reason=(
                "claimed_at-tie deferred to PCR-2b — strict-newer rule "
                "yields no winner"
            ),
        )
    winner, loser = winner_loser
    candidate_name = collisions[0][0]

    # Step 2.5: Clock-skew guard (slice-084 / ADR-076). Runs strictly BEFORE the Step 3
    # overlay/write so a skew-STOP mutates no rebase state (atomicity per ADR-069). A winner
    # future-dated vs the resolver's trusted wall-clock (or unparseable / tz-naive) is NOT
    # auto-resolved — fail-closed STOP escalating to the PCR-2b gate (the existing
    # commit-slice SKILL.md VAULT_CLAIM-STOP → SOAD-1 fall-through surfaces it). Best-effort
    # audit entry recording both claims + resolver-now is appended first (R-23 corrigibility).
    skew_reason = _winner_clock_skew_suspect(winner, now, _CLOCK_SKEW_TOLERANCE_SECONDS)
    if skew_reason is not None:
        try:
            _append_skew_stop_audit(repo_root, skew_reason, winner, loser, now)
        except Exception as exc:  # noqa: BLE001 - best-effort by design (mirrors L1249-1257)
            print(
                f"parallel-conflict-resolver: skew-STOP audit append failed "
                f"(non-blocking): {exc!r}",
                file=sys.stderr,
            )
        return ResolutionResult(
            action="STOP",
            conflict_class=ConflictClass.VAULT_CLAIM,
            regenerated_files=(),
            reason=skew_reason,
        )

    # Step 3: Read stage baselines + overlay winner identity onto baseline.
    # Defense-in-depth (slice-091 /code-review m1): mirror the SOFT path's
    # _StageDecodeError net so a non-UTF-8 stage on the VAULT_CLAIM path ALSO
    # fails closed and LOUD (UNKNOWN STOP), never an uncaught traceback. This
    # case is structurally pre-empted upstream (a non-UTF-8 stage degrades
    # diagnose_conflict -> classify_conflict returns UNKNOWN, not VAULT_CLAIM),
    # so the guard covers only the diagnose->resolve TOCTOU window (the ADR-067
    # cooperative-race regime) — making the "non-UTF-8 stage always fails
    # closed" invariant total rather than path-dependent.
    try:
        text_3 = _git_show_stage(repo_root, 3, "architecture/slice-queue.md")  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
        text_2 = _git_show_stage(repo_root, 2, "architecture/slice-queue.md")  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
    except _StageDecodeError as exc:
        try:
            _append_decode_stop_audit(repo_root, exc.stage, exc.path, str(exc))
        except Exception as audit_exc:  # noqa: BLE001 - best-effort by design
            print(
                f"parallel-conflict-resolver: decode-STOP audit append "
                f"failed (non-blocking): {audit_exc!r}",
                file=sys.stderr,
            )
        return ResolutionResult(
            action="STOP",
            conflict_class=ConflictClass.UNKNOWN,
            regenerated_files=(),
            reason=str(exc),
        )
    baseline_text = text_3 if text_3 else text_2
    if not baseline_text:
        return ResolutionResult(
            action="STOP",
            conflict_class=ConflictClass.UNKNOWN,
            regenerated_files=(),
            reason=(
                "slice-queue.md: both stage 2 and stage 3 missing — "
                "rebase state unexpected"
            ),
        )

    overlaid = _overlay_claims_on_queue_text(
        baseline_text,
        {
            candidate_name: {
                "claimed_by": winner.claimed_by,
                "claimed_at": winner.claimed_at,
            },
        },
    )

    # Step 3 (M-add-1): defensive post-overlay verification — silent-drop
    # protection. If the candidate block in baseline_text lacks the
    # canonical `- **Risk-retired:**` pivot, _overlay_claims_on_queue_text
    # logs to stderr but still returns the unchanged baseline → the winner's
    # claim is silently dropped. Fail-closed STOP rather than ship a stale
    # claim.
    verify_pattern = _re.compile(
        rf"### {_re.escape(candidate_name)}.*?Claimed-by:\*\* "
        rf"{_re.escape(winner.claimed_by)}",
        _re.DOTALL,
    )
    if not verify_pattern.search(overlaid):
        return ResolutionResult(
            action="STOP",
            conflict_class=ConflictClass.VAULT_CLAIM,
            regenerated_files=(),
            reason=(
                "overlay-silently-dropped — candidate block missing "
                "Risk-retired pivot; manual intervention required"
            ),
        )

    # Step 4: Read-only loser-replacement from in-memory overlaid text.
    replacement = _pick_loser_replacement(
        queue_text=overlaid,
        exclude_names={candidate_name},
    )

    # Step 5: Atomic write + git add + git rebase --continue.
    out_path = repo_root / VAULT_ROOT / "slice-queue.md"  # slice-098/ADR-089 Class-A ROUTE
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(overlaid, encoding="utf-8", newline="")
    try:
        subprocess.run(
            ["git", "add", "architecture/slice-queue.md"],  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
            cwd=str(repo_root),
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "rebase", "--continue"],
            cwd=str(repo_root),
            check=True,
            capture_output=True,
            env={**os.environ, "GIT_EDITOR": "true"},
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return ResolutionResult(
            action="STOP",
            conflict_class=ConflictClass.VAULT_CLAIM,
            regenerated_files=("architecture/slice-queue.md",),  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
            reason=(
                "git stage + rebase --continue failed post vault-claim "
                f"resolution: {exc!r}"
            ),
        )

    result = ResolutionResult(
        action="APPLIED",
        conflict_class=ConflictClass.VAULT_CLAIM,
        regenerated_files=("architecture/slice-queue.md",),  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
        # Encode replacement in reason for _format_vault_claim_audit_entry.
        reason=f"vault-claim-resolved; replacement={replacement or 'none-available'}",
    )

    # Step 6: Best-effort audit-log append (mirrors SOFT path L338-344).
    try:
        _append_audit_log(repo_root, diag, result)
    except Exception as exc:  # noqa: BLE001 - best-effort by design
        print(
            f"parallel-conflict-resolver: audit log append failed "
            f"(non-blocking): {exc!r}",
            file=sys.stderr,
        )

    # Step 7: Return APPLIED.
    return result


# ---------------------------------------------------------------------------
# PCR-2b: HARD + MIXED gate-on-hand-resolve (slice-083 / ADR-075)
# ---------------------------------------------------------------------------

def resolve_hard_conflict(
    diag: ConflictDiagnostic,
    repo_root: Path | None = None,
) -> ResolutionResult:
    """Dispatch target for HARD- and MIXED-class conflicts (PCR-2b).

    Per PCR-2b (slice-083 / ADR-075): HARD and MIXED conflicts are NEVER
    auto-merged (the rejected ADR-069 Option 2). This function returns a STOP
    carrying gate context; the actual resolution flow — resolve markers ->
    ``--verify-resolution`` -> the ``code-review`` agent on the resolved diff
    -> the TRI-RESOLVE-1 user gate -> ``git rebase --continue`` ->
    ``--record-hard-resolution`` — is orchestrated by ``skills/commit-slice/
    SKILL.md`` sub-step 2.5 (Python cannot spawn skill agents). This function
    NEVER mutates rebase state and NEVER runs ``git rebase --continue``.

    MIXED routes here too (atomicity per ADR-069 MIXED row — never partially
    auto-resolve the SOFT portion when a non-SOFT U-file coexists).

    Two HARD-entry paths exist (design.md M2 fix): (1) ``classify_conflict``
    returns HARD/MIXED upfront -> ``resolve_soft_conflict`` dispatches here;
    (2) ``resolve_soft_conflict`` escalates a SOFT-looking shippability conflict
    to HARD mid-loop via ``_SoftResolutionError(..., HARD)`` -> returns its own
    bare STOP with ``conflict_class=HARD`` WITHOUT passing through this function.
    ``skills/commit-slice/SKILL.md`` keys the gate-flow entry on
    (``action=="STOP"`` AND ``conflict_class in {HARD, MIXED}``) so BOTH entry
    paths are covered uniformly.
    """
    if repo_root is None:
        repo_root = Path.cwd()

    cls = classify_conflict(diag)
    if cls not in (ConflictClass.HARD, ConflictClass.MIXED):
        # Caller misuse / diag-class disagreement — fail-closed (never pretend
        # a non-HARD/MIXED conflict is gate-resolvable).
        return ResolutionResult(
            action="STOP",
            conflict_class=ConflictClass.UNKNOWN,
            regenerated_files=(),
            reason=(
                f"resolve_hard_conflict invoked on non-HARD/MIXED class "
                f"({cls.value}) — diag/class disagree, fail-closed"
            ),
        )

    return ResolutionResult(
        action="STOP",
        conflict_class=cls,
        regenerated_files=(),
        reason=(
            f"{cls.value}-class conflict — gate-on-hand-resolve via "
            "/commit-slice sub-step 2.5 (resolve markers -> --verify-resolution "
            "-> code-review agent -> TRI-RESOLVE-1 user gate -> git rebase "
            "--continue). PCR-2b never auto-merges HARD/MIXED."
        ),
    )


def _verify_resolution_clean(repo_root: Path) -> tuple[bool, str | None]:
    """Verify a hand-resolved HARD/MIXED rebase has no unresolved conflicts.

    Per PCR-2b (slice-083 / ADR-075) B2 + M-add-1 /critique fixes. Two
    git-native + line-anchored-opener checks (NOT a ``=======`` scan, NOT
    ``git diff --cached --check`` — both inherit git's ``>=7-=`` heuristic that
    false-STOPs on Markdown setext H1 underlines; HARD U-files ARE markdown):

      (a) ``git diff --name-only --diff-filter=U`` MUST be empty (git itself
          considers every path resolved/staged), and
      (b) no line-anchored ``<<<<<<<`` opener / ``>>>>>>>`` closer survives in
          the staged resolution (``git diff --cached``) — keyed on the 7-char
          ``<``/``>`` runs that have no legitimate Markdown/source analog.

    Conservative fail-closed: a doc that legitimately starts a line with
    ``<<<<<<<`` / ``>>>>>>>`` (rare — e.g. a code-fence demonstrating a
    conflict) false-STOPs, which is SAFE (refuses to continue and routes the
    user to re-resolve/abort; it NEVER silently continues).

    Returns ``(clean, reason)``; ``reason`` is ``None`` when clean.
    """
    # (a) any path still unmerged?
    try:
        u_proc = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return (False, f"git-state-unreadable: {exc!r}")
    if u_proc.stdout.strip():
        unmerged = ", ".join(u_proc.stdout.split())
        return (False, f"paths-still-unmerged: {unmerged}")

    # (b) leftover line-anchored opener/closer in the staged resolution?
    try:
        d_proc = subprocess.run(
            ["git", "diff", "--cached"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return (False, f"git-state-unreadable: {exc!r}")
    if _CONFLICT_MARKER_OPENER_RE.search(d_proc.stdout):
        return (False, "unresolved-markers-present")

    return (True, None)


def _format_hard_audit_entry(
    diag: ConflictDiagnostic,
    timestamp: str,
    head_sha: str,
    verdict: str,
    disposition: str,
) -> str:
    """Build the HARD/MIXED audit-log section (PCR-2b / slice-083 / ADR-075).

    Section heading ``## Hard-conflict resolution - <ISO-8601 UTC>`` — UNIFORM
    hyphen-space separator (PCR-2a ADR-071 discipline); section-type
    distinguished by the prefix word ``Hard-conflict`` (vs ``Soft-conflict`` /
    ``Vault-claim``), NOT by trailing dash decoration.
    """
    u_files_csv = ", ".join(diag.u_files) if diag.u_files else "(none)"
    concerned_ids = sorted({
        cs.slice_id
        for u in diag.u_files
        for cs in diag.concerned_slices.get(u, ())
    })
    concerned_csv = ", ".join(concerned_ids) if concerned_ids else "(none)"

    return (
        f"## Hard-conflict resolution - {timestamp}\n"
        "\n"
        f"**Repo HEAD SHA pre-resolution**: {head_sha}\n"
        f"**U-files resolved**: {u_files_csv}\n"
        f"**Concerned slices**: {concerned_csv}\n"
        "**Resolution mechanism**: gate-on-hand-resolve (PCR-2b) — "
        "hand-resolved + code-review agent + TRI-RESOLVE-1 user gate\n"
        f"**code-review verdict**: {verdict}\n"
        f"**TRI-RESOLVE-1 disposition**: {disposition}\n"
        "\n"
    )


def _record_hard_resolution(
    repo_root: Path,
    diag: ConflictDiagnostic,
    verdict: str,
    disposition: str,
) -> None:
    """Append a HARD-conflict audit section. Best-effort (caller catches).

    Invoked by the ``--record-hard-resolution`` CLI mode after a ratified
    TRI-RESOLVE-1 apply, while still mid-rebase (so ``diag`` carries the U-files
    + concerned slices), immediately before ``git rebase --continue``. Reuses
    the single-open append + lazy-header pattern from ``_append_audit_log``.
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
            encoding="utf-8",
            check=True,
        )
        head_sha = head_proc.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        head_sha = "(unavailable)"

    entry = _format_hard_audit_entry(diag, timestamp, head_sha, verdict, disposition)

    needs_header = not log_path.exists()
    with log_path.open("a", encoding="utf-8", newline="") as f:
        if needs_header:
            f.write(_AUDIT_LOG_HEADER)
        f.write(entry)


def _merge_shippability(repo_root: Path) -> tuple[Path, str]:
    """Row-union merge of architecture/shippability.md by slice number.

    Per design.md Resolution algorithm: parse both stages' tables, key
    rows by leading ``| <NN> |`` slice number, union, sort ascending,
    preserve header + non-numeric rows verbatim. Same-slice-number with
    different content escalates to HARD per design.md Edge-cases column.

    Returns (out_path, resolved_content) — does NOT write to disk.
    Caller (resolve_soft_conflict) accumulates returns from all helpers
    + batch-writes only if ALL succeed (stage-then-commit atomicity per
    fix M2 / code-review).
    """
    text_2 = _git_show_stage(repo_root, 2, "architecture/shippability.md")  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
    text_3 = _git_show_stage(repo_root, 3, "architecture/shippability.md")  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)

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

    out_path = repo_root / VAULT_ROOT / "shippability.md"  # slice-098/ADR-089 Class-A ROUTE
    return (out_path, output_text)


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


def _baseline_is_truncation_shaped(queue_text: str | None) -> tuple[bool, str | None]:
    """Detect whether a `slice-queue.md` baseline blob looks tail-truncated/corrupt.

    slice-085 / R-24 / ADR-077. The discriminating signal the name-level orphan-claim
    comparison lacked: a truncation cuts the FILE TAIL, so the LAST ``### <name>`` block
    is the one that goes incomplete. Truncation-suspect iff the last candidate block is
    missing >=1 of the 5 canonical on-disk PSQ-1 field labels (which also covers a file
    cut mid-field-line — the partial label line never matches its full prefix).

    Deliberately **tail-specific** (per /critique M1): a complete-but-noncanonical block
    EARLIER in the file (legacy format / hand-edit) does NOT trip the gate — only the tail.

    The required label set is sourced FROM ``slice_queue_writer._RENDERED_FIELD_LABELS``
    (genuine SSoT per /critique M3) read at call time, so writer + reader never disagree.

    Mirrors ``slice_queue_claim.parse_queue_text`` (slice_queue_claim.py:236-240): CRLF is
    normalized and an empty / ``_(no candidates)_`` placeholder baseline (no ``### `` block)
    is NOT truncation-shaped (else a legitimate empty queue false-STOPs — /critique m3).

    Returns ``(suspect, reason)``: ``reason`` is a human-readable string when suspect,
    else ``None``. Bounded O(blocks x labels); blocks <= top-10 per SOFT merge (/critique
    m2 — re-review if a future PSQ extension lifts the top-10 cap).
    """
    import re as _re  # noqa: PLC0415

    from tools import slice_queue_writer  # noqa: PLC0415

    if not queue_text:
        return (False, None)
    text = queue_text.replace("\r\n", "\n")  # CRLF-normalize (parse_queue_text parity)

    heading_positions = [m.start() for m in _re.finditer(r"^### .+$", text, _re.MULTILINE)]
    if not heading_positions:
        # No candidate blocks at all (empty / `_(no candidates)_` placeholder / header-only)
        # — a legitimate queue shape, NOT a truncation. Fail-open here (the harm gate is
        # claim-loss, and no block means no claimed block to lose by corruption).
        return (False, None)

    last_block = text[heading_positions[-1]:]
    labels = slice_queue_writer._RENDERED_FIELD_LABELS
    missing = [
        label for label in labels
        if not _re.search("^" + _re.escape(label), last_block, _re.MULTILINE)
    ]
    if missing:
        return (
            True,
            f"last candidate block is missing field label(s) {missing} — baseline appears "
            f"tail-truncated/corrupt (file does not end at a clean PSQ-1 block boundary)",
        )
    return (False, None)


def _verify_soft_equivalence(
    repo_root: Path,
    diag: ConflictDiagnostic,
    pending_writes: list[tuple[Path, str]],
) -> None:
    """ADR-074 / R-21 fix-class (b): SOFT auto-regen equivalence guard.

    Read-only. Proves the regenerated *pending* content is in a deterministic
    equivalence class against BOTH rebase stages along three invariants; if any is
    unprovable (or a re-derivation/re-parse fails), raises
    ``_SoftResolutionError(reason, ConflictClass.UNKNOWN)`` after a best-effort
    audit-log STOP entry. The caller (``resolve_soft_conflict``) translates the raise
    into a fail-closed STOP with NO writes — closing R-21's silent-wrong-resolution class.

    Invariants (see design.md / ADR-074):
      #1 Queue claim-preservation (CLAIMED subset only, M-add-1): every CLAIMED
         candidate present as a ``### <name>`` heading in the baseline MUST carry its
         claim in the regenerated queue. Orphan claims (absent from baseline) are an
         expected top-10-churn drop and are NOT a STOP — but a claimed orphan that had a
         heading in the *discarded* stage gets a LOUD cross-stage-claim-drop warning
         (M2: truncated-baseline observability without false-STOPping legitimate churn).
      #2 Shippability row-completeness: numbered-row set == union of both stages'.
      #3 Shippability prelude set-equality (symmetric, M1): non-blank prelude lines are
         equal across both stages AND preserved in the output — catches non-numbered
         (split/combined) row content-mutation in EITHER stage.
    """
    import re as _re  # noqa: PLC0415

    pending: dict[str, str] = {}
    for out_path, content in pending_writes:
        try:
            rel = out_path.relative_to(repo_root).as_posix()
        except ValueError:  # pragma: no cover - defensive; pending paths are repo-rooted
            rel = out_path.as_posix()
        pending[rel] = content

    def _fail(reason: str) -> NoReturn:  # m2: NoReturn — always raises; lets a type-checker
        # prove the post-_fail code (e.g. the pending_claims read) is unreachable.
        try:
            _append_equivalence_stop_audit(repo_root, diag, reason)
        except Exception as exc:  # noqa: BLE001 - audit is best-effort, never blocks the STOP
            print(
                f"parallel-conflict-resolver: equivalence-guard audit append failed "
                f"(non-blocking): {exc!r}",
                file=sys.stderr,
            )
        raise _SoftResolutionError(reason, ConflictClass.UNKNOWN)

    # --- Invariant #1: queue claim-preservation -------------------------------
    qrel = "architecture/slice-queue.md"  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
    if qrel in pending:
        text_2 = _git_show_stage(repo_root, 2, qrel)
        text_3 = _git_show_stage(repo_root, 3, qrel)
        claims_2, claims_3 = _extract_claim_diff(text_2, text_3)
        merged_claims = _merge_claim_dicts(claims_2, claims_3)
        baseline_is_stage3 = bool(text_3)  # m3: explicit stage identity (not full-text ==)
        baseline_text = text_3 if baseline_is_stage3 else text_2
        # M1 (code-Critic): .strip() each captured heading to match the canonical
        # parse_queue_text parser (slice_queue_claim.py:113 rstrips before its
        # `^### (?P<name>\S.*)$` match). Without the strip, a baseline heading carrying
        # a trailing space (`### add-foo `) yields `'add-foo '`, which never intersects
        # the rstripped `claimed_names` — silently bypassing the fail-closed invariant #1.
        baseline_headings = {m.strip() for m in _re.findall(r"^### (.+)$", baseline_text, _re.MULTILINE)}
        # M-add-1: domain is the CLAIMED subset of merged_claims, NOT all keys
        # (merged_claims includes unclaimed candidates; checking them would false-STOP
        # the happy path since the overlay only emits claim lines for claimed entries).
        claimed_names = {n for n, d in merged_claims.items() if d.get("claimed_by")}

        try:
            from tools.slice_queue_claim import (  # noqa: PLC0415
                ClaimUsageError,
                parse_queue_text,
            )
            pending_claims = parse_queue_text(pending[qrel])
        except ImportError as exc:
            _fail(
                f"equivalence-guard: cannot verify invariant #1 — "
                f"slice_queue_claim.parse_queue_text unavailable: {exc!r}"
            )
        except ClaimUsageError as exc:
            _fail(
                f"equivalence-guard: invariant #1 unprovable — regenerated slice-queue.md "
                f"has a partial/unparseable claim block: {exc!r}"
            )

        for name in sorted(claimed_names & baseline_headings):
            pc = pending_claims.get(name) or {}
            if not pc.get("claimed_by"):
                _fail(
                    f"equivalence-guard: invariant #1 claim-preservation unprovable — "
                    f"claimed candidate {name!r} is present in the baseline queue but its "
                    f"claim is ABSENT from the regenerated slice-queue.md (malformed-block "
                    f"drop / semantic divergence vs manual-resolve baseline; R-21)"
                )

        # slice-085 / R-24 / ADR-077 (Option 4, orphan-gated): an orphan claim — a claimed
        # candidate ABSENT from the baseline — is normally legitimate top-10 churn (WARN, not
        # STOP; the slice-082 M2 / ADR-074 anti-false-STOP decision). But when the baseline is
        # TRUNCATION-SHAPED, the drop is claim-loss-by-corruption (the R-24 hole) → escalate to
        # a fail-closed STOP via `_fail` (best-effort audit row first). Well-formed baseline →
        # preserve the existing cross-stage-claim-drop WARN (no false-STOP on healthy churn).
        # Tail-truncation-shape is the discriminating signal the name-level check lacked.
        stage2_headings = {m.strip() for m in _re.findall(r"^### (.+)$", text_2, _re.MULTILINE)}
        stage3_headings = {m.strip() for m in _re.findall(r"^### (.+)$", text_3, _re.MULTILINE)}
        discarded_headings = stage2_headings if baseline_is_stage3 else stage3_headings
        orphan_claims = sorted(claimed_names - baseline_headings)
        if orphan_claims:
            # Fail-closed on uncertainty (mission-brief must-not-defer): if the integrity
            # check itself raises, treat the baseline as suspect → STOP in this claim-
            # threatened branch (never silently auto-merge an uncheckable baseline that
            # already dropped a claim).
            try:
                truncation_shaped, trunc_reason = _baseline_is_truncation_shaped(baseline_text)
            except Exception as exc:  # noqa: BLE001 - any parse failure → suspect → fail-closed
                truncation_shaped = True
                trunc_reason = f"baseline integrity check raised {exc!r} — treated as suspect"
            if truncation_shaped:
                dropped = ", ".join(repr(n) for n in orphan_claims)
                _fail(
                    f"equivalence-guard: claim-loss-by-corruption — claimed candidate(s) "
                    f"{dropped} dropped from a TRUNCATION-SHAPED baseline slice-queue.md "
                    f"({trunc_reason}); refusing to auto-merge a corrupt baseline that lost a "
                    f"durable claim (R-24 / ADR-077 Option 4 — hand-resolve the rebase). "
                    f"NOTE: the M1 case (a claim that existed ONLY on the truncated branch) is "
                    f"invisible to merged_claims and remains a documented R-24 residual."
                )
            # Well-formed baseline: legitimate churn → existing loud WARN, no STOP.
            for name in orphan_claims:
                if name in discarded_headings:
                    print(
                        f"parallel-conflict-resolver: cross-stage-claim-drop: claimed candidate "
                        f"{name!r} present in a discarded rebase stage but absent from a "
                        f"WELL-FORMED baseline — expected on legitimate top-10 churn (the "
                        f"baseline passed the slice-085 truncation-shape integrity check)",
                        file=sys.stderr,
                    )

    # --- Invariants #2 + #3: shippability -------------------------------------
    srel = "architecture/shippability.md"  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
    if srel in pending:
        s2 = _git_show_stage(repo_root, 2, srel)
        s3 = _git_show_stage(repo_root, 3, srel)
        numbered_2, prelude_2 = _parse_shippability_rows(s2) if s2 else ({}, [])
        numbered_3, prelude_3 = _parse_shippability_rows(s3) if s3 else ({}, [])
        numbered_out, prelude_out = _parse_shippability_rows(pending[srel])

        # #2 row-completeness. NOTE (m1 / code-Critic): this is a round-trip-STABILITY
        # backstop, NOT a stage-divergence check — `_merge_shippability` builds the output
        # as `numbered_2 | numbered_3` by construction, so the key-set equality is near-
        # tautological on the happy path. It still earns its place: it catches a lossy
        # re-parse (a future writer emitting a slice-number `_parse_shippability_rows` no
        # longer matches on `^\|\s*(\d+)\s*\|`). Same-number content-mutation is caught
        # upstream at `_merge_shippability` (HARD escalation); content-mutation lives in
        # invariant #3's prelude check for non-numbered rows.
        expected_nums = set(numbered_2) | set(numbered_3)
        if set(numbered_out) != expected_nums:
            _fail(
                f"equivalence-guard: invariant #2 row-completeness unprovable — regenerated "
                f"shippability.md numbered rows {sorted(set(numbered_out))} != union of both "
                f"stages {sorted(expected_nums)}"
            )

        # #3 symmetric prelude set-equality + output preservation
        def _nonblank(lines: list[str]) -> set[str]:
            return {ln for ln in lines if ln.strip()}

        nb2, nb3, nbo = _nonblank(prelude_2), _nonblank(prelude_3), _nonblank(prelude_out)
        if nb2 != nb3:
            _fail(
                f"equivalence-guard: invariant #3 prelude set-equality unprovable — non-numbered "
                f"shippability lines differ between rebase stages (possible non-numbered/split-row "
                f"content-mutation): {sorted(nb2 ^ nb3)}"
            )
        if nbo != nb2:
            _fail(
                f"equivalence-guard: invariant #3 prelude-preservation unprovable — regenerated "
                f"shippability prelude diverges from the input stages: {sorted(nbo ^ nb2)}"
            )


def _append_equivalence_stop_audit(
    repo_root: Path, diag: ConflictDiagnostic, reason: str
) -> None:
    """Append a guard-STOP entry to the audit log (best-effort; ADR-074 / AC-3).

    Distinct section variant ``## Soft-conflict resolution (equivalence-guard STOP) - <ts>``
    so a guard-STOP is recoverable from the audit trail. The SOFT/VAULT_CLAIM APPLIED
    section shapes (``_append_audit_log``) are unchanged.
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
            encoding="utf-8",
            check=True,
        )
        head_sha = head_proc.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        head_sha = "(unavailable)"

    u_files_csv = ", ".join(diag.u_files) if diag.u_files else "(none)"
    entry = (
        f"## Soft-conflict resolution (equivalence-guard STOP) - {timestamp}\n"
        "\n"
        f"**Repo HEAD SHA pre-resolution**: {head_sha}\n"
        f"**U-files**: {u_files_csv}\n"
        "**Outcome**: STOP (fail-closed, no writes) per ADR-074 SOFT equivalence guard\n"
        f"**Reason**: {reason}\n\n"
    )

    needs_header = not log_path.exists()
    with log_path.open("a", encoding="utf-8", newline="") as f:
        if needs_header:
            f.write(_AUDIT_LOG_HEADER)
        f.write(entry)


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
            encoding="utf-8",
            check=True,
        )
        head_sha = head_proc.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        head_sha = "(unavailable)"

    # PCR-2a: dispatch on result.conflict_class — VAULT_CLAIM gets its own
    # 8-field section type; SOFT stays on the original section shape verbatim.
    if result.conflict_class is ConflictClass.VAULT_CLAIM:
        # Fix O (slice-078 m1 DRY): compute winner/loser ONCE here — in the same scope as
        # the already-computed timestamp + head_sha — and pass them to the formatter,
        # instead of having the formatter re-derive from diag.claim_history. Defensive:
        # the resolver only invokes audit with a well-formed single-collision result; if
        # the diag carries 0 or >1 collisions at audit time, pass None (the formatter's
        # pragma:no-cover branch renders `(unavailable)` rather than crashing the
        # best-effort append).
        _vc_collisions = _collect_same_candidate_different_identity(diag.claim_history)
        _vc_winner_loser = (
            _select_timestamp_winner(_vc_collisions) if len(_vc_collisions) == 1 else None
        )
        if _vc_winner_loser is not None:
            _vc_winner, _vc_loser = _vc_winner_loser
        else:
            _vc_winner = _vc_loser = None
        entry = _format_vault_claim_audit_entry(
            diag, result, timestamp, head_sha, _vc_winner, _vc_loser
        )
    else:
        u_files_csv = ", ".join(diag.u_files) if diag.u_files else "(none)"
        concerned_ids = sorted({
            cs.slice_id
            for u in diag.u_files
            for cs in diag.concerned_slices.get(u, ())
        })
        concerned_csv = ", ".join(concerned_ids) if concerned_ids else "(none)"

        action_lines: list[str] = []
        for f in result.regenerated_files:
            if f == "architecture/slice-queue.md":  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
                action_lines.append(
                    f"- `{f}` - regenerated via _overlay_claims_on_queue_text "
                    "with merged-claims union"
                )
            elif f == "architecture/shippability.md":  # NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)
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

    # Single-open append (fix m6 / code-review): unified open("a")
    # for both lazy-create + append branches with conditional header.
    # Replaces the prior `if exists / write_text else open("a")` TOCTOU
    # pattern where two parallel writers both saw "not exists" and both
    # write_text'd (truncate) — losing the first writer's entry. O_APPEND
    # semantics on POSIX (and Win32 equivalent) preserve entries even
    # under concurrent writers; the doubled-header TOCTOU window remains
    # but doubled header is recoverable cosmetic, lost entry is not.
    # Also fixes M1 / EOL-DRIFT-1 / ADR-033: newline="" prevents Windows
    # \n → \r\n translation that the sibling PSQ-2 modules
    # (slice_queue_writer.py:790, slice_queue_claim.py:535) explicitly
    # use for LF-only byte-deterministic emission.
    needs_header = not log_path.exists()
    with log_path.open("a", encoding="utf-8", newline="") as f:
        if needs_header:
            f.write(_AUDIT_LOG_HEADER)
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
    mode.add_argument(
        "--verify-resolution",
        action="store_true",
        help="PCR-2b: verify a hand-resolved HARD/MIXED rebase has no unresolved conflicts",
    )
    mode.add_argument(
        "--record-hard-resolution",
        action="store_true",
        help="PCR-2b: append a HARD-conflict audit-log section (post-ratification, pre-continue)",
    )
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repo root (default: cwd)")
    parser.add_argument("--verdict", default=None, help="code-review verdict (--record-hard-resolution)")
    parser.add_argument("--disposition", default=None, help="TRI-RESOLVE-1 disposition (--record-hard-resolution)")

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

    if args.verify_resolution:
        # PCR-2b (slice-083 / ADR-075): git-native + line-anchored-opener check.
        clean, reason = _verify_resolution_clean(repo_root)
        action = "CLEAN" if clean else "STOP"
        if args.json:
            print(json.dumps(
                {"action": action, "reason": reason}, indent=2, ensure_ascii=False
            ))
        else:
            print(f"Action: {action}" + (f" ({reason})" if reason else ""))
        # exit 1 ONLY on unreadable git state (UNKNOWN-equivalent fail-closed);
        # a clean CLEAN or a coherent STOP (paths-still-unmerged /
        # unresolved-markers-present) is exit 0 per the design.md contract.
        if not clean and reason and reason.startswith("git-state-unreadable"):
            return 1
        return 0

    if args.record_hard_resolution:
        # PCR-2b: best-effort HARD audit append (mirrors PCR-1/PCR-2a audit
        # error model — write failure logs to stderr but NEVER blocks).
        verdict = args.verdict or "(unspecified)"
        disposition = args.disposition or "(unspecified)"
        recorded = True
        err: str | None = None
        try:
            _record_hard_resolution(repo_root, diag, verdict, disposition)
        except Exception as exc:  # noqa: BLE001 - best-effort by design
            recorded = False
            err = repr(exc)
            print(
                f"parallel-conflict-resolver: HARD audit append failed "
                f"(non-blocking): {err}",
                file=sys.stderr,
            )
        action = "RECORDED" if recorded else "RECORD-FAILED"
        if args.json:
            print(json.dumps(
                {"action": action, "reason": err}, indent=2, ensure_ascii=False
            ))
        else:
            print(f"Action: {action}")
        return 0

    # argparse's mutually_exclusive_group(required=True) prevents this.
    return 2


if __name__ == "__main__":
    sys.exit(main())
