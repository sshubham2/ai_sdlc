"""Parallel-slice queue claim machinery (PSQ-2).

Per **PSQ-2** (`methodology-changelog.md` v0.71.0; slice-072; [[ADR-067]];
mints a new rule; supersedes nothing). PSQ-2 is the second rule on the
parallel-slice family axis — PSQ-1 (slice-067) ships discoverability via
`architecture/slice-queue.md`; PSQ-2 ships coordination via per-entry
ownership recorded as additive `**Claimed-by:** <user.name> <user.email>`
+ `**Claimed-at:** <ISO-8601 UTC>` field lines after PSQ-1's existing
`**Risk-retired:**` field.

**Identity model** (per ADR-067 §"Options considered" Option 1 + §"Identity
model implications"): git-identity-only. Claim ownership = the git-
configured user identity at claim time (`git config user.name` +
`git config user.email`). No session-id, no PID, no hostname (ADR-064 L37
+ R-19 mid-2026-05 mitigation prose anticipated session-id; ADR-067
§Lineage divergence note documents this as predecessor-spec drift, NOT
supersession). Two sessions running as the same git user are by
definition the same claimant on a single candidate.

**Schema extension** (additive on PSQ-1's stable on-disk contract per
ADR-064 §Consequences "Slice-068 MAY add new field lines per entry"):

  ### <candidate-name>

  - **Source:** <existing PSQ-1 field>
  - **Blast-radius:** <existing PSQ-1 field>
  - **Parallel-safety:** <existing PSQ-1 field>
  - **Effort:** <existing PSQ-1 field>
  - **Risk-retired:** <existing PSQ-1 field>
  - **Claimed-by:** <git user.name> <git user.email>          # NEW (PSQ-2; optional)
  - **Claimed-at:** <ISO-8601 UTC timestamp>                   # NEW (PSQ-2; optional)
  - **<SomeForwardCompatField>:** <value>                      # PSQ-3+ extensibility

Either both `Claimed-by:` + `Claimed-at:` present (claimed) or both
absent (unclaimed) — partial state is malformed per `parse_queue_text`.

**Forward-compat** (per ADR-067 §Consequences + critic-review m-add-2
ACCEPTED-FIXED): unknown `**<Key>:** <value>` field lines AFTER
`**Risk-retired:**` are passed through verbatim in `_extra_field_lines:
list[str]` so a future PSQ-3+ slice can add new optional field lines
without breaking PSQ-2's pinned tests. `_format_entry` re-emits them
after the known claim lines but before the trailing empty-line entry-
separator.

**Atomicity** (must-not-defer #1; mirrors PSQ-1 at
`tools/slice_queue_writer.py:729-731`): writes via ``.tmp`` sibling +
``os.replace()`` with explicit ``newline=""`` for LF-only byte-
deterministic emission on Windows (per Critic M1 ACCEPTED-FIXED —
``Path.write_text`` default ``newline=None`` translates ``\\n`` to
``\\r\\n`` on Windows, breaking byte-equal claim-preservation round-trip
assertions; modelcontextprotocol/python-sdk#2433 + runebook.dev
TextIOWrapper docs).

**Adversarial model** (per ADR-067 §"Adversarial model"): cooperative
coordination, NOT a security boundary. A malicious local actor with
filesystem write to ``architecture/slice-queue.md`` can forge any claim
or unclaim. PSQ-2 defends only "two cooperating Claude sessions on the
same machine should not collide".

Usage::

    # CLI (primary surface)
    python -m tools.slice_queue_claim --claim <candidate-name>
    python -m tools.slice_queue_claim --release <candidate-name>
    python -m tools.slice_queue_claim --force-claim <candidate-name>
    python -m tools.slice_queue_claim --claim <name> --queue <custom-path>

    # Library API (used by tools.slice_queue_writer.write_slice_queue at
    # /slice Step 6.5 to merge existing claims onto the regenerated top-10)
    from tools.slice_queue_claim import parse_queue_text
    claims = parse_queue_text(queue_path.read_text(encoding="utf-8"))

Exit codes::

    0  success (claim / release / force-claim applied; release on
       present-but-unclaimed candidate is idempotent no-op exit 0)
    2  usage error (missing candidate / already-claimed without
       --force-claim / git config user.name|user.email unset or
       configured-empty / malformed claim block / queue file missing /
       mutually-exclusive flags / etc.)

Never exit 1 — PSQ-2 is a coordination gate, not a slice-regression
class (symmetric to NAW-1's binary exit contract per ADR-061
§"BINARY exit contract by construction").
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from tools import _stdout
from tools._vault_paths import VAULT_ROOT
from tools._vault_write import safe_write_text  # slice-094 VWS-1: R-32-safe routed write


_QUEUE_FILENAME = "slice-queue.md"
_DEFAULT_QUEUE_REL = VAULT_ROOT / _QUEUE_FILENAME  # VAULT_ROOT-routed (slice-068)

_GIT_CONFIG_TIMEOUT_SEC = 5  # Bounded subprocess to keep CLI responsive

# Schema literals. The exact prose form is part of the on-disk contract
# pinned by tests/methodology/test_psq_2_claim_machinery.py.
_CLAIMED_BY_PREFIX = "- **Claimed-by:**"
_CLAIMED_AT_PREFIX = "- **Claimed-at:**"
_RISK_RETIRED_PREFIX = "- **Risk-retired:**"

# Match an entry-header line `### <candidate-name>`. PSQ-1 emits these
# verbatim at `tools/slice_queue_writer.py:_format_entry`.
_ENTRY_HEADER_RE = re.compile(r"^### (?P<name>\S.*)$")

# Match a field-line `- **<Key>:** <value>` after `**Risk-retired:**`.
# Used for both known claim fields and unknown forward-compat lines.
_FIELD_LINE_RE = re.compile(r"^- \*\*(?P<key>[A-Za-z][A-Za-z0-9_-]*):\*\*\s*(?P<value>.*)$")


class ClaimUsageError(Exception):
    """Raised by claim/release/parse on any user-recoverable usage error.

    All instances map to CLI exit code 2 + a single-line stderr message.
    PSQ-2 never raises a different exit-code class — coordination errors
    are user-recoverable (re-claim, --force-claim, fix git config, etc.),
    NOT slice-regression class.
    """


# ---------------------------------------------------------------------
# Git config user identity
# ---------------------------------------------------------------------


def read_git_config_user() -> tuple[str, str]:
    """Read ``user.name`` + ``user.email`` from git config.

    Returns (name, email) on success.

    Raises ``ClaimUsageError`` with a per-key descriptive message when:

    - subprocess returncode == 1 (key unset — idiomatic git config absence
      per ``git-scm.com/docs/git-config``).
    - subprocess returncode == 0 but ``stdout.strip()`` is empty
      (configured-empty value treated as effectively-unset — a
      ``git config user.name ""`` configuration is semantically equivalent
      to absent for claim-ownership purposes).
    - subprocess returncode is any other non-zero value (git tool error;
      not a user-recoverable absence but still mapped to ClaimUsageError
      so the CLI exits 2 cleanly).

    Per Critic m2 ACCEPTED-FIXED — the 3-case detection is the design
    spec at design.md §"Components touched" `read_git_config_user`.
    """
    name = _read_one_git_config_key("user.name")
    email = _read_one_git_config_key("user.email")
    return name, email


def _read_one_git_config_key(key: str) -> str:
    """Read one git config key; raise ClaimUsageError on absence."""
    try:
        proc = subprocess.run(
            ["git", "config", key],
            capture_output=True,
            text=True,
            check=False,
            timeout=_GIT_CONFIG_TIMEOUT_SEC,
        )
    except FileNotFoundError as exc:
        raise ClaimUsageError(
            f"git binary not available on PATH (required to read git config {key}): {exc}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ClaimUsageError(
            f"git config {key} read timed out after {_GIT_CONFIG_TIMEOUT_SEC}s"
        ) from exc

    if proc.returncode == 1:
        raise ClaimUsageError(
            f"git config {key} not set; PSQ-2 claims require git identity"
        )
    if proc.returncode != 0:
        raise ClaimUsageError(
            f"git config {key} read failed (returncode={proc.returncode}): "
            f"{proc.stderr.strip() or '<no stderr>'}"
        )
    value = proc.stdout.strip()
    if not value:
        raise ClaimUsageError(
            f"git config {key} not set; PSQ-2 claims require git identity"
        )
    return value


# ---------------------------------------------------------------------
# Queue file parser
# ---------------------------------------------------------------------


def parse_queue_text(text: str) -> dict[str, dict[str, object]]:
    """Parse a PSQ-1 queue file into ``{candidate_name: entry_dict}``.

    Returns ALL entries in the queue (claimed or not). Per Critic m-add-2
    ACCEPTED-FIXED, unclaimed entries appear in the dict but the
    ``claimed_by`` / ``claimed_at`` keys are ABSENT (consumers MUST use
    ``dict.get(...)``); the ``_extra_field_lines`` key is ALWAYS present
    (possibly an empty list).

    Returns an empty dict ONLY when the file contains no entries
    (no ``### <name>`` headings) or is empty.

    CRLF-tolerant: ``\\r\\n`` line endings are internally normalized to
    ``\\n`` before parsing (per Critic M1 ACCEPTED-FIXED — Windows
    contributors may produce CRLF-line-ended queue files via editors
    that ignore the writer's LF-only emit).

    Raises ``ClaimUsageError`` ONLY on PARTIAL known claim block (one of
    ``Claimed-by:`` / ``Claimed-at:`` present without the other). Unknown
    forward-compat field lines (``**<UnknownKey>:** ...``) pass through
    verbatim in ``_extra_field_lines`` — they DO NOT trigger malformed
    detection per ADR-067 §Consequences (PSQ-3+ extensibility) + Critic
    M3 ACCEPTED-FIXED.

    Entry-dict shape:

    - Claimed entry: ``{"claimed_by": "<name> <email>", "claimed_at": "<iso8601>", "_extra_field_lines": [...]}``
    - Unclaimed entry: ``{"_extra_field_lines": [...]}``

    Known PSQ-1 fields (Source / Blast-radius / Parallel-safety / Effort
    / Risk-retired) are NOT returned — they're written by
    ``tools.slice_queue_writer.write_slice_queue``'s top-10 enumeration
    and are not preservation-relevant. Only claim metadata + forward-
    compat extras survive a regen.
    """
    if not text:
        return {}

    # Normalize CRLF → LF (Critic M1 ACCEPTED-FIXED).
    text = text.replace("\r\n", "\n")

    entries: dict[str, dict[str, object]] = {}
    current_name: str | None = None
    current_entry: dict[str, object] | None = None
    # `after_risk_retired` flips True once we see the Risk-retired field
    # inside the current entry — subsequent field lines (claim or
    # forward-compat) accumulate. Field lines BEFORE Risk-retired are
    # PSQ-1's own 5 fields and ignored.
    after_risk_retired = False

    for raw_line in text.split("\n"):
        line = raw_line.rstrip()

        header_match = _ENTRY_HEADER_RE.match(line)
        if header_match:
            # Flush previous entry.
            if current_name is not None and current_entry is not None:
                _validate_entry(current_name, current_entry)
                entries[current_name] = current_entry
            current_name = header_match.group("name").strip()
            current_entry = {"_extra_field_lines": []}
            after_risk_retired = False
            continue

        if current_entry is None:
            # Before the first entry — ignore header prose.
            continue

        # Detect Risk-retired pivot.
        if line.startswith(_RISK_RETIRED_PREFIX):
            after_risk_retired = True
            continue

        if not after_risk_retired:
            continue

        # Past Risk-retired: check for claim / forward-compat field lines.
        field_match = _FIELD_LINE_RE.match(line)
        if not field_match:
            # Blank line or non-field content terminates the post-
            # Risk-retired field block. Stay in the entry — subsequent
            # field lines belong to the next entry once header fires.
            after_risk_retired = False
            continue

        key = field_match.group("key")
        value = field_match.group("value").strip()
        if key == "Claimed-by":
            current_entry["claimed_by"] = value
        elif key == "Claimed-at":
            current_entry["claimed_at"] = value
        else:
            # Unknown forward-compat field line — preserve verbatim.
            extras = current_entry["_extra_field_lines"]
            assert isinstance(extras, list)
            extras.append(line)

    # Flush final entry.
    if current_name is not None and current_entry is not None:
        _validate_entry(current_name, current_entry)
        entries[current_name] = current_entry

    return entries


def _validate_entry(name: str, entry: dict[str, object]) -> None:
    """Raise ClaimUsageError on PARTIAL known claim block.

    Either both ``claimed_by`` + ``claimed_at`` present, or both absent.
    Partial state is malformed per ADR-067 §"Schema extension" + Critic
    M3 ACCEPTED-FIXED.
    """
    has_by = "claimed_by" in entry
    has_at = "claimed_at" in entry
    if has_by != has_at:
        raise ClaimUsageError(f"malformed claim block for {name}")


# ---------------------------------------------------------------------
# Claim / release / force-claim mutations
# ---------------------------------------------------------------------


def apply_claim(
    text: str,
    candidate: str,
    claim_user: str,
    claim_at: str,
    *,
    force: bool,
) -> str:
    """Apply a claim to ``candidate`` in queue ``text``; return new text.

    Inserts ``Claimed-by:`` + ``Claimed-at:`` field lines AFTER the
    candidate's ``Risk-retired:`` field (and AFTER any pre-existing
    ``_extra_field_lines`` for that entry) but BEFORE the trailing empty
    line that separates entries — preserves entry-block separation per
    Critic m1 ACCEPTED-FIXED.

    On already-claimed candidate:
        - ``force=False`` → raises ``ClaimUsageError`` directing user to
          ``--force-claim`` (bare-claim refusal per AC3).
        - ``force=True`` → overwrites the existing claim (stale-claim
          recovery escape-hatch per AC3 + ADR-067 §"Adversarial model").

    On missing candidate name → raises ``ClaimUsageError`` (typo-rejection).
    On malformed claim block → raises ``ClaimUsageError`` via
    ``parse_queue_text``.
    """
    entries = parse_queue_text(text)
    if candidate not in entries:
        raise ClaimUsageError(f"candidate {candidate} not found in queue")
    entry = entries[candidate]
    if "claimed_by" in entry and not force:
        prev_by = entry["claimed_by"]
        prev_at = entry.get("claimed_at", "<unknown>")
        raise ClaimUsageError(
            f"{candidate} already claimed by {prev_by} at {prev_at}; "
            f"use --force-claim to overwrite"
        )
    return _rewrite_entry_claim(text, candidate, claim_user, claim_at)


def apply_release(text: str, candidate: str) -> str:
    """Remove claim lines for ``candidate`` from queue ``text``.

    On candidate present + claimed → removes both `Claimed-by:` +
    `Claimed-at:` lines.
    On candidate present + already-unclaimed → idempotent no-op (returns
    ``text`` unchanged); CLI exits 0 per Critic M2 ACCEPTED-FIXED
    (release on already-released candidate is documented behavior, NOT
    an error).
    On candidate NOT in queue → raises ``ClaimUsageError`` (typo-rejection;
    symmetric with ``apply_claim``'s missing-candidate behavior per
    Critic M2 ACCEPTED-FIXED).

    Preserves ``_extra_field_lines`` (forward-compat).
    """
    entries = parse_queue_text(text)
    if candidate not in entries:
        raise ClaimUsageError(f"candidate {candidate} not found in queue")
    entry = entries[candidate]
    if "claimed_by" not in entry:
        # Idempotent: already unclaimed.
        return text
    return _rewrite_entry_release(text, candidate)


def _rewrite_entry_claim(
    text: str,
    candidate: str,
    claim_user: str,
    claim_at: str,
) -> str:
    """Rewrite the queue text inserting / overwriting claim lines.

    Strategy: split into pre/entry/post chunks at the candidate's
    ``### <candidate>`` header + the next ``### <other>`` header (or EOF);
    inside the entry block, find the trailing empty line that separates
    it from the next entry; insert Claimed-by + Claimed-at + any
    pre-existing _extra_field_lines RIGHT BEFORE that trailing empty
    line (at index [-2] in the entry's line list per Critic m1
    ACCEPTED-FIXED).
    """
    return _rewrite_entry_lines(
        text,
        candidate,
        builder=_build_claimed_block(claim_user, claim_at),
    )


def _rewrite_entry_release(text: str, candidate: str) -> str:
    """Rewrite the queue text removing claim lines for ``candidate``."""
    return _rewrite_entry_lines(text, candidate, builder=_build_unclaimed_block())


def _build_claimed_block(claim_user: str, claim_at: str):
    """Return a callable that rewrites an entry's claim-block lines."""

    def _builder(entry_lines: list[str]) -> list[str]:
        # Drop any pre-existing Claimed-by / Claimed-at lines.
        kept: list[str] = []
        for line in entry_lines:
            if line.startswith(_CLAIMED_BY_PREFIX) or line.startswith(_CLAIMED_AT_PREFIX):
                continue
            kept.append(line)
        # Find the index of the Risk-retired line.
        retired_idx = _find_risk_retired_index(kept)
        # Find the entry's trailing empty-line index (the last empty
        # element). Per Critic m1: insert AFTER Risk-retired + any
        # extras, BEFORE the trailing empty.
        insert_idx = _find_insert_index_for_claim(kept, retired_idx)
        new_lines = [
            f"{_CLAIMED_BY_PREFIX} {claim_user}",
            f"{_CLAIMED_AT_PREFIX} {claim_at}",
        ]
        return kept[:insert_idx] + new_lines + kept[insert_idx:]

    return _builder


def _build_unclaimed_block():
    """Return a callable that strips Claimed-by / Claimed-at lines."""

    def _builder(entry_lines: list[str]) -> list[str]:
        return [
            line for line in entry_lines
            if not line.startswith(_CLAIMED_BY_PREFIX)
            and not line.startswith(_CLAIMED_AT_PREFIX)
        ]

    return _builder


def _find_risk_retired_index(lines: list[str]) -> int:
    """Return the index of the Risk-retired field line in ``lines``."""
    for idx, line in enumerate(lines):
        if line.startswith(_RISK_RETIRED_PREFIX):
            return idx
    raise ClaimUsageError("malformed entry: Risk-retired field missing")


def _find_insert_index_for_claim(lines: list[str], retired_idx: int) -> int:
    """Find the insertion index AFTER any extras but BEFORE trailing blank.

    The entry block (from `### <name>` onward through the trailing blank
    line) has shape::

        ### <name>
        <blank>
        - **Source:** ...
        - **Blast-radius:** ...
        - **Parallel-safety:** ...
        - **Effort:** ...
        - **Risk-retired:** ...                              # retired_idx
        - **<ExtraForwardCompat>:** ...                      # 0..N more field lines
        <blank>                                              # trailing entry-separator

    Insert AFTER `Risk-retired:` + any extras but BEFORE the trailing
    blank — per Critic m1 ACCEPTED-FIXED.
    """
    idx = retired_idx + 1
    while idx < len(lines) and lines[idx].startswith("- **") and not (
        lines[idx].startswith(_CLAIMED_BY_PREFIX)
        or lines[idx].startswith(_CLAIMED_AT_PREFIX)
    ):
        idx += 1
    return idx


def _rewrite_entry_lines(text: str, candidate: str, *, builder) -> str:
    """Split queue text at the candidate entry, rewrite, rejoin.

    Atomic-write is the caller's responsibility (``main()`` uses
    ``.tmp`` sibling + ``os.replace()``).
    """
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")

    # Locate the entry's start (### <candidate>) + end (next ### header
    # or EOF).
    start_idx: int | None = None
    for idx, line in enumerate(lines):
        m = _ENTRY_HEADER_RE.match(line)
        if m and m.group("name").strip() == candidate:
            start_idx = idx
            break
    if start_idx is None:
        raise ClaimUsageError(f"candidate {candidate} not found in queue")

    end_idx = len(lines)
    for idx in range(start_idx + 1, len(lines)):
        if _ENTRY_HEADER_RE.match(lines[idx]):
            end_idx = idx
            break

    entry_lines = lines[start_idx:end_idx]
    new_entry_lines = builder(entry_lines)
    return "\n".join(lines[:start_idx] + new_entry_lines + lines[end_idx:])


# ---------------------------------------------------------------------
# Atomic write
# ---------------------------------------------------------------------


def _atomic_write_text(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` via the R-32-safe vault writer.

    slice-094 (VWS-1): routed through ``_vault_write.safe_write_text`` — sidecar
    lock + LF-faithful ``newline=""`` + atomic ``os.replace`` + bounded
    EPERM-retry. Byte output is IDENTICAL to the prior inline ``.tmp`` +
    ``write_text(newline="")`` + ``os.replace`` pattern (``safe_write_text`` is
    LF-faithful per slice-094 B1), so PSQ-2 byte-equal round-trip assertions are
    preserved. The wrapper is retained so its callers are unchanged. NB: the
    read-modify-write window in the callers is a documented flip-residual (B2).
    """
    safe_write_text(path, text)


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m tools.slice_queue_claim",
        description=(
            "PSQ-2 (slice-072) parallel-slice queue claim machinery. "
            "Claim, release, or force-claim a candidate on "
            "architecture/slice-queue.md using git config user identity."
        ),
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--claim", metavar="CANDIDATE",
        help="Claim CANDIDATE (refused if already claimed; use --force-claim to overwrite).",
    )
    group.add_argument(
        "--release", metavar="CANDIDATE",
        help="Release CANDIDATE (idempotent on already-unclaimed; exit 2 on missing).",
    )
    group.add_argument(
        "--force-claim", metavar="CANDIDATE",
        help="Force-claim CANDIDATE (overwrites any existing claim — stale-claim recovery).",
    )
    p.add_argument(
        "--queue", type=Path,
        default=None,
        help=f"Queue file path (default: {_DEFAULT_QUEUE_REL}).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    queue_path = args.queue if args.queue is not None else _DEFAULT_QUEUE_REL
    if not queue_path.exists():
        print(
            f"PSQ-2 usage error: queue file not found at {queue_path}; "
            f"run /slice to create it",
            file=sys.stderr,
        )
        return 2

    try:
        text = queue_path.read_text(encoding="utf-8")
        if args.claim is not None:
            name, email = read_git_config_user()
            claim_user = f"{name} {email}"
            claim_at = _now_iso8601_utc()
            new_text = apply_claim(text, args.claim, claim_user, claim_at, force=False)
            if new_text != text:
                _atomic_write_text(queue_path, new_text)
            print(f"CLAIMED {args.claim} by {claim_user} at {claim_at}")
            return 0
        if args.force_claim is not None:
            name, email = read_git_config_user()
            claim_user = f"{name} {email}"
            claim_at = _now_iso8601_utc()
            new_text = apply_claim(text, args.force_claim, claim_user, claim_at, force=True)
            _atomic_write_text(queue_path, new_text)
            print(f"FORCE-CLAIMED {args.force_claim} by {claim_user} at {claim_at}")
            return 0
        # args.release is not None
        new_text = apply_release(text, args.release)
        if new_text != text:
            _atomic_write_text(queue_path, new_text)
            print(f"RELEASED {args.release}")
        else:
            print(f"RELEASED {args.release} (already unclaimed; no-op)")
        return 0
    except ClaimUsageError as exc:
        print(f"PSQ-2 usage error: {exc}", file=sys.stderr)
        return 2


def _now_iso8601_utc() -> str:
    """Return current UTC time as ISO-8601 with +00:00 offset suffix.

    Matches PSQ-1's provenance-line timestamp format at
    ``tools/slice_queue_writer.py:format_queue_md``.
    """
    now = datetime.now(tz=timezone.utc)
    iso = now.strftime("%Y-%m-%dT%H:%M:%S")
    offset = now.strftime("%z")
    if offset:
        iso += f"{offset[:3]}:{offset[3:]}"
    return iso


if __name__ == "__main__":
    sys.exit(main())
