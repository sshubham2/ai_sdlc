"""Parallel-slice queue writer (PSQ-1).

Per **PSQ-1** (`methodology-changelog.md` v0.69.0; slice-067; [[ADR-064]];
mints a new rule; supersedes nothing). PSQ-1 is the first rule on the
parallel-slice family axis (adjacent to BRANCH family — BRANCH-2 makes
parallel work physically possible, PSQ-1 makes it discoverable; PSQ-2 /
PSQ-3 will make it coordinated at slice-068 / slice-069).

`/slice` Step 6.5 (NEW) writes ``architecture/slice-queue.md`` containing
the top-10 parallel-safe candidates from Step 1's source-fan-out (sources
#1-8). Each entry tags the candidate's blast-radius file set (from
graphify) and a 4-value ``Parallel-safety`` enum computed against the
union of expected blast-radius file sets for currently-active slices.

**Parallel-safety enum precedence** (highest priority first; per ADR-064
+ design.md L80):

  ``UNKNOWN-NO-GRAPH``       > graphify graph missing entirely
  ``UNKNOWN-NO-HINT-FILES``  > candidate has empty ``hint_files`` set
  ``OVERLAPS-WITH-slice-NNN[, slice-MMM]``  > non-empty intersection
  ``NON-OVERLAPPING``        > non-empty hint_files, empty intersection

**Atomicity** (must-not-defer #1): writes via ``.tmp`` sibling +
``os.replace()``. Crash-durability via ``os.fsync()`` is OUT OF SCOPE
(queue is regenerable on every ``/slice`` invocation).

**Bootstrap (slice-067 only)**: slice-067 authors PSQ-1 + this very helper.
The helper does NOT exist at slice-067's own ``/slice`` time (the slice
that authors the helper cannot self-apply its own deliverable). Bootstrap-
reference instance #1 per slice-066 ``WORKTREE=skip-bootstrap`` precedent.
The queue file is first written at slice-067's ``/build-slice`` Phase E
mid-slice smoke. Every slice after 067's ``/slice`` invocation routinely
writes the queue via Step 6.5 + the SKILL.md ImportError guard.

Usage::

    # Library API (preferred; called from /slice Step 6.5 prose)
    from tools.slice_queue_writer import write_slice_queue
    write_slice_queue(
        repo_root=Path('.'),
        candidates=[{'name': 'add-foo', 'source': 'risk-register R-13',
                     'hint_files': ['tools/foo.py'],
                     'effort': 'SMALL', 'risk_retired': 'LOW'}],
        active_slice_num=67,
        graph_path=Path('graphify-out/graph.json'),
    )

    # CLI (used by tests + integration check)
    python -m tools.slice_queue_writer \\
        --candidates-json <path> --active-slice 67 \\
        --output architecture/slice-queue.md \\
        --graph graphify-out/graph.json --root .

Exit codes::

    0  queue file written (clean OR degraded with WARN per AC4-(c))
    2  usage error (bad args, missing input file, JSON parse error, etc.)

Never exit 1 — queue-write success is not a slice-regression class
(symmetric to NAW-1's binary exit contract per ADR-061 §"BINARY exit
contract by construction").
"""
from __future__ import annotations

import argparse
import functools
import json
import os
import re
import subprocess
import sys
import types
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from tools import _stdout
from tools._vault_paths import VAULT_ROOT
from tools._vault_write import safe_write_text  # slice-094 VWS-1: R-32-safe routed write


_TOP_N = 10
_QUEUE_FILENAME = "slice-queue.md"
_INDEX_MD_REL = VAULT_ROOT / "slices" / "_index.md"  # VAULT_ROOT-routed (slice-068)
_SLICES_DIR_REL = VAULT_ROOT / "slices"  # VAULT_ROOT-routed (slice-068)
_GRAPH_DEFAULT_REL = Path("graphify-out") / "graph.json"

# Path-shape regex (slice-071 M2 FIX per /critique B1 ACCEPTED-FIXED).
# Verbatim from tests/bugs/test_psq_1_blast_radius_dict_leak.py:291-295
# (slice-070 build minted; uses negated `[^\s`]` classes which avoid the
# `]\-` ambiguity that broke the originally-drafted three-alternative regex).
# Accepts: tokens with path separator (a/b), `.alphanum{1,8}` extension
# (file.HTML, file.cfg), or leading-dot dotfile (.gitignore, .env).
# Rejects: bare letter-only opaque identifiers (unknown, Makefile, abc).
_PATH_SHAPED_RE = re.compile(
    r"^(?:[^\s`]*[/\\][^\s`]+"          # has path separator
    r"|[^\s`]*\.[A-Za-z0-9]{1,8}"       # ends with .ext (1-8 alphanum)
    r"|\.[A-Za-z][A-Za-z0-9_.-]*)$"     # leading-dot dotfile
)

# Forward-compat key probe order for `_node_to_path` dict input
# (slice-071 m5 FIX per slice-070 code-Critic m5: extract magic tuple to
# module-level constant; docstring + `_node_to_path` reference it).
# Order is semantic: `path` first (most-likely future surface), `source_file`
# (graphify's current internal field), `name` (legacy fallback).
_FORWARD_COMPAT_PATH_KEYS: tuple[str, ...] = ("path", "source_file", "name")

# Per design.md L80 + ADR-064 §Consequences: 4-value Parallel-safety enum.
_FLAG_NON_OVERLAPPING = "NON-OVERLAPPING"
_FLAG_UNKNOWN_NO_HINT = "UNKNOWN-NO-HINT-FILES"
_FLAG_UNKNOWN_NO_GRAPH = "UNKNOWN-NO-GRAPH"

_WARN_NO_GRAPH_LINE = (
    "_WARN: graphify graph missing — blast-radius enrichment skipped; "
    "rebuild with `$PY -m graphify code .`_"
)
_NO_CANDIDATES_PLACEHOLDER = "_(no candidates)_"

# slice-099 / BRANCH-3 / [[ADR-090]]: the append-only pick-provenance section.
# Preserved verbatim across queue regeneration via read-tail/re-append (a
# DISTINCT path from PSQ-2 claim-preservation). Line shape:
#   - slice-NNN-<name> — picked <ISO-8601 UTC> by <git user.name> <user.email>
_PICK_LOG_HEADING = "## Pick log"
# Anchored at line-start, exactly two hashes (a candidate is rendered `### <name>`,
# so even a candidate literally named "## Pick log" → `### ## Pick log` never
# false-matches this — the third hash breaks the `^## ` anchor).
_PICK_LOG_BLOCK_RE = re.compile(r"(?m)^## Pick log\b.*\Z", re.S)

# The 5 canonical on-disk PSQ-1 field labels, in render order. This is the
# SINGLE render source: `_format_entry` (below) emits these verbatim via zip
# (slice-085 / ADR-077 / M3) so the constant IS the contract, not a parallel
# copy. `tools/parallel_conflict_resolver._baseline_is_truncation_shaped`
# imports this tuple to detect a truncation-shaped baseline (a tail block
# missing ≥1 of these labels), keeping writer + reader on one source of truth.
# NOTE (M3, no fourth copy): element [4] ("- **Risk-retired:**") is the same
# literal as `slice_queue_claim._RISK_RETIRED_PREFIX` (:109), which exists for
# the orthogonal purpose of marking the post-Risk-retired claim-line pivot in
# `parse_queue_text`. They are kept byte-identical by intent; do not add a
# third representation of these labels.
_RENDERED_FIELD_LABELS: tuple[str, ...] = (
    "- **Source:**",
    "- **Blast-radius:**",
    "- **Parallel-safety:**",
    "- **Effort:**",
    "- **Risk-retired:**",
)


# ---------------------------------------------------------------------
# Active-slice blast-radius derivation
# ---------------------------------------------------------------------


def _read_active_slice_nums(repo_root: Path) -> list[int]:
    """Parse ``architecture/slices/_index.md`` ``## Active`` table.

    Returns the list of slice numbers (int) currently in flight. Empty
    list if file missing, section missing, or table empty (per AC4-(b)).
    """
    index_path = repo_root / _INDEX_MD_REL
    if not index_path.exists():
        return []
    try:
        text = index_path.read_text(encoding="utf-8")
    except OSError:
        return []
    # Locate the ## Active section; tolerate any subsequent ## heading.
    m = re.search(r"^## Active\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return []
    section = m.group(1)
    # Match slice numbers in the table — accept any "slice-NNN-" reference.
    nums: list[int] = []
    for m2 in re.finditer(r"slice-(\d{3})-", section):
        n = int(m2.group(1))
        if n not in nums:
            nums.append(n)
    return nums


def _read_declared_files_for_slice(repo_root: Path, slice_num: int) -> set[str]:
    """Derive declared touched-files for an active slice.

    Prefers ``design.md`` ``## Wiring matrix`` ``New module`` cells; falls
    back to ``mission-brief.md`` ``## Dependencies`` cite. Returns the set
    of paths (strings) the slice touches.

    Empty set if neither file resolves usable content (caller treats empty
    as "no declared files" — distinct from "graph-missing" or
    "no-hint-files"; this is a per-slice signal that may legitimately be
    empty if the slice hasn't reached /design-slice yet).
    """
    slices_dir = repo_root / _SLICES_DIR_REL
    if not slices_dir.exists():
        return set()
    # Slice folder lookup — handles both "slice-NNN-<name>" + archived form.
    for child in slices_dir.iterdir():
        if not child.is_dir():
            continue
        if not child.name.startswith(f"slice-{slice_num:03d}-"):
            continue
        return _extract_files_from_slice_dir(child)
    return set()


def _extract_files_from_slice_dir(slice_dir: Path) -> set[str]:
    """Extract declared touched files from a slice folder's vault files."""
    files: set[str] = set()
    # Prefer design.md "## Wiring matrix" New module column.
    design = slice_dir / "design.md"
    if design.exists():
        try:
            text = design.read_text(encoding="utf-8")
        except OSError:
            text = ""
        m = re.search(
            r"^## Wiring matrix\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S
        )
        if m:
            section = m.group(1)
            # First column of each data row — between leading `|` and next `|`.
            for line in section.splitlines():
                if not line.startswith("|"):
                    continue
                # Skip header + separator rows.
                if line.startswith("|--") or "New module" in line:
                    continue
                cells = [c.strip() for c in line.strip("|").split("|")]
                if not cells:
                    continue
                first = cells[0]
                # Extract backtick-quoted paths from the first cell.
                for path_match in re.finditer(r"`([^`]+)`", first):
                    candidate = path_match.group(1)
                    # Filter for path-shaped strings (contain / or .).
                    if "/" in candidate or "\\" in candidate or "." in candidate:
                        files.add(candidate)
        if files:
            return files
    # Fallback: mission-brief.md "## Dependencies" cite.
    brief = slice_dir / "mission-brief.md"
    if brief.exists():
        try:
            text = brief.read_text(encoding="utf-8")
        except OSError:
            text = ""
        m = re.search(
            r"^## Dependencies\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S
        )
        if m:
            section = m.group(1)
            for path_match in re.finditer(r"`([^`]+)`", section):
                candidate = path_match.group(1)
                if "/" in candidate or "\\" in candidate or "." in candidate:
                    files.add(candidate)
    return files


# ---------------------------------------------------------------------
# Graphify blast-radius wrapper
# ---------------------------------------------------------------------


def _is_path_shaped(s: str) -> bool:
    """A string is path-shaped per the module-level ``_PATH_SHAPED_RE``.

    Single source of truth (slice-071 M2 FIX per /critique B1 ACCEPTED-FIXED):
    the regex is defined ONCE at module scope; both this predicate AND the
    test-side validator import it. Accepts tokens with path separator,
    `.alphanum{1,8}` extension, or leading-dot dotfile. Rejects bare opaque
    identifiers (`unknown`, `Makefile`, letter-only strings).
    """
    if not s:
        return False
    return _PATH_SHAPED_RE.fullmatch(s) is not None


def _discover_known_repo_roots(repo_root: Path) -> list[Path]:
    """Return all repo-root candidates for path normalization.

    Per slice-071 M1 FIX step 1 (/critique-review M3 ACCEPTED-FIXED 4-step
    algorithm): query ``git worktree list --porcelain`` for all registered
    worktrees so abs paths sourced from one tree can be normalized against
    any sibling tree. Worktree mode under BRANCH-2 produces a main tree +
    one or more sibling `<main-parent>/<main-name>-wt/slice-NNN-*` trees;
    a graph.json built from one tree may contain abs paths another tree
    needs to interpret relative-to its own root.

    Returns ``[repo_root]`` (single-entry list) on any subprocess failure or
    when git is unavailable — degrades gracefully to "no worktree
    awareness", which is the pre-slice-071 behavior.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "worktree", "list", "--porcelain"],
            capture_output=True, text=True, encoding="utf-8",
            timeout=10, check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return [repo_root]
    if result.returncode != 0:
        return [repo_root]
    roots: list[Path] = []
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            wt_path_str = line[len("worktree "):].strip()
            if wt_path_str:
                roots.append(Path(wt_path_str))
    return roots if roots else [repo_root]


def _normalize_abs_to_repo_relative(
    abs_path_str: str, repo_root: Path, candidate_roots: list[Path]
) -> str | None:
    """Normalize an absolute path to a repo-relative form (slice-071 M1 FIX).

    Per /critique M3 ACCEPTED-FIXED 4-step algorithm (steps 2-4):
      2. Try ``Path(abs).relative_to(candidate_root)`` for each candidate
         root; first success is the canonical relative form (returned as
         POSIX string).
      3. If no candidate succeeds, fall back to
         ``os.path.relpath(abs, repo_root)`` and accept only if
         ``_PATH_SHAPED_RE`` validates.
      4. If neither path succeeds, return None (caller drops the entry).
    """
    try:
        abs_path = Path(abs_path_str).resolve()
    except (OSError, RuntimeError):
        return None
    # Step 2: try relative_to against each known root.
    for candidate_root in candidate_roots:
        try:
            return abs_path.relative_to(candidate_root.resolve()).as_posix()
        except (ValueError, OSError):
            continue
    # Step 3: os.path.relpath fallback + regex validation.
    try:
        relpath = os.path.relpath(str(abs_path), str(repo_root.resolve()))
        relpath_posix = Path(relpath).as_posix()
    except (ValueError, OSError):
        return None
    if _PATH_SHAPED_RE.fullmatch(relpath_posix) is not None:
        return relpath_posix
    # Step 4: drop.
    return None


@functools.lru_cache(maxsize=4)
def _build_id_to_path_map(graph_path_str: str) -> types.MappingProxyType:
    """Build ``{node_id -> repo-relative source_file}`` from graph.json.

    The graphify blast-radius JSON CLI output emits
    ``{id, label, type:"", path:""}`` where ``type``/``path`` are
    structurally empty in this repo's graph. The underlying node dicts in
    ``graph.json`` carry the real path in ``source_file``. This map lets
    consumers resolve a returned ID to the path they actually need.

    Memoized via ``lru_cache`` (string key — ``Path`` is unhashable in some
    shapes) so multi-call enrichment within one ``/slice`` Step 6.5
    invocation reads + parses ``graph.json`` once. Cache size 4 covers the
    common case (default graph_path + a few overrides per session).

    Returns a read-only ``MappingProxyType`` view (slice-071 M4 FIX per
    slice-070 code-Critic M4): future mutating callers raise ``TypeError``,
    closing the lru_cache shared-mutable foot-gun.

    Returns an empty map on any read/parse failure — best-effort
    degradation consistent with the surrounding "graphify is best-effort,
    never block" contract from slice-067.

    Per slice-071 M1 FIX (per /critique M3 ACCEPTED-FIXED 4-step
    algorithm): abs path normalization uses ``_discover_known_repo_roots``
    (BRANCH-2 worktree-aware) + ``_normalize_abs_to_repo_relative`` (regex-
    validated fallback + drop). Entries that cannot be normalized to a
    path-shaped repo-relative form are DROPPED (the helper's pre-slice-071
    fallback to bare ``as_posix()`` of the abs path leaked worktree
    absolute paths into the id->path map, surfacing in rendered
    `Blast-radius:` cells as duplicate abs/rel entries for the same file).
    """
    try:
        data = json.loads(Path(graph_path_str).read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return types.MappingProxyType({})
    repo_root = Path.cwd().resolve()
    candidate_roots = _discover_known_repo_roots(repo_root)
    out: dict[str, str] = {}
    for n in data.get("nodes", []):
        if not isinstance(n, dict):
            continue
        nid = n.get("id")
        src = n.get("source_file")
        if not (isinstance(nid, str) and isinstance(src, str) and nid and src):
            continue
        rel = _normalize_abs_to_repo_relative(src, repo_root, candidate_roots)
        if rel is None:
            continue  # Step 4 drop — entry would have leaked unfiltered abs path
        out[nid] = rel
    return types.MappingProxyType(out)


def _node_to_path(node: object, id_to_path) -> str | None:
    """Extract a path-shaped identifier from a graphify node element.

    PRIMARY path: dict input whose ``id`` is in ``id_to_path`` map -> the
    mapped repo-relative source_file (slice-071 M3 FIX per slice-070
    code-Critic M3: PRIMARY return is wrapped with ``_is_path_shaped``
    filter for defense-in-depth consistency with forward-compat branch).
    This is the path graphify actually carries today; the blast-radius CLI
    just doesn't surface the field directly in JSON output.

    Forward-compat fallback (future graphify schemas where the CLI DOES
    surface a path-bearing key): dict input with any key in
    ``_FORWARD_COMPAT_PATH_KEYS`` (slice-071 m5 FIX: module-level constant
    replaces magic tuple per slice-070 code-Critic m5) populated AND
    path-shaped -> use that value. The constant enumerates the keys in
    semantic order: ``path`` first (most-likely future surface),
    ``source_file`` (graphify's current internal field), ``name``
    (legacy fallback).

    Legacy compat: ``str`` input that is itself path-shaped -> returned
    verbatim. ID-only strings dropped (mirrors ``_parse_text_nodes``
    discipline at L255).

    Any other shape -> returns ``None``; caller skips such items rather
    than letting ``str(node)`` leak Markdown-invalid characters into the
    rendered ``Blast-radius:`` cell (SC-027 defect class, slice-070 fix).

    ``id_to_path`` accepts ``dict[str, str]`` OR ``MappingProxyType``
    (read-only view returned by ``_build_id_to_path_map`` post-slice-071
    M4 FIX).
    """
    if isinstance(node, str):
        return node if _is_path_shaped(node) else None
    if not isinstance(node, dict):
        return None
    # PRIMARY: id-lookup via graph.json map (slice-071 M3 FIX: filtered).
    nid = node.get("id")
    if isinstance(nid, str) and nid in id_to_path:
        val = id_to_path[nid]
        if _is_path_shaped(val):
            return val
        # Fall through to forward-compat if PRIMARY value fails filter.
    # Forward-compat: dict has its own populated path-shaped key.
    # slice-071 m5 FIX: probe order is the module-level constant.
    for key in _FORWARD_COMPAT_PATH_KEYS:
        val = node.get(key)
        if isinstance(val, str) and _is_path_shaped(val):
            return val
    return None


def _call_graphify_blast_radius(
    graph_path: Path, file_or_node: str
) -> set[str]:
    """Thin wrapper invoking ``graphify blast-radius`` for a single node.

    Adapted from ``skills/slice-candidates/build_backlog.py:120-155``. Tries
    ``--file <basename>`` first (current graph node-ID shape uses basenames);
    falls back to ``--from <full-path>`` (legacy node-ID shape). Returns the
    set of affected node IDs as repo-relative paths, or empty set on any
    failure.

    Slice-070 SC-027 fix: resolves dict-node IDs via ``_build_id_to_path_map``
    (graph.json source_file lookup) instead of stringifying the dicts. See
    ``_node_to_path`` for the extraction-precedence contract.
    """
    py = sys.executable
    # Try --file with basename first (current graphify node-ID convention).
    basename = Path(file_or_node).name
    for argv_tail in (
        ["--file", basename],
        ["--from", file_or_node],
    ):
        cmd = [py, "-m", "graphify", "blast-radius"] + argv_tail + [
            "--graph", str(graph_path),
            "--format", "json",
        ]
        try:
            res = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8",
                timeout=30, check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return set()
        if res.returncode != 0:
            continue
        try:
            data = json.loads(res.stdout)
        except json.JSONDecodeError:
            return _parse_text_nodes(res.stdout)
        # slice-071 m4 FIX (per slice-070 code-Critic m4): build id->path
        # map AFTER subprocess+JSON-parse succeed, not at function entry —
        # skips wasted lru_cache work on subprocess-failure paths.
        id_to_path = _build_id_to_path_map(str(graph_path))
        if isinstance(data, list):
            return {p for x in data if (p := _node_to_path(x, id_to_path)) is not None}
        if isinstance(data, dict):
            for key in ("nodes", "blast_radius", "affected"):
                if key in data and isinstance(data[key], list):
                    return {p for x in data[key] if (p := _node_to_path(x, id_to_path)) is not None}
        return set()
    return set()


def _parse_text_nodes(text: str) -> set[str]:
    nodes: set[str] = set()
    for ln in text.splitlines():
        ln = ln.strip().lstrip("-* ").strip()
        if ln and not ln.startswith("#") and "/" in ln:
            nodes.add(ln)
    return nodes


def derive_active_slice_blast_radius(
    repo_root: Path,
    graph_path: Path | None = None,
    *,
    blast_resolver: Callable[[Path, str], set[str]] | None = None,
) -> dict[int, set[str]]:
    """Read _index.md Active table + per-slice declared files; expand via graphify.

    Returns ``{slice_num: blast_set}`` where ``blast_set`` is the union of
    graphify blast-radius queries for each declared file. Empty dict if no
    active slices. When ``graph_path`` is None or missing, declared files
    are returned verbatim (no graphify expansion) — useful for testing +
    AC4-(c) degraded-mode behaviour.

    The ``blast_resolver`` injection seam mirrors slice-059 TVFS-1 +
    slice-063 NAW-1 precedent for deterministic regression testing.
    """
    if blast_resolver is None:
        blast_resolver = _call_graphify_blast_radius
    use_graph = graph_path is not None and graph_path.exists()

    out: dict[int, set[str]] = {}
    for n in _read_active_slice_nums(repo_root):
        declared = _read_declared_files_for_slice(repo_root, n)
        if not declared:
            out[n] = set()
            continue
        if use_graph:
            blast: set[str] = set()
            for f in declared:
                blast |= blast_resolver(graph_path, f)
            # Also include the declared files themselves (a file is in its
            # own blast-radius by definition).
            blast |= declared
            out[n] = blast
        else:
            out[n] = set(declared)
    return out


# ---------------------------------------------------------------------
# Parallel-safety classification
# ---------------------------------------------------------------------


def compute_parallel_safety(
    candidate_files: set[str],
    active_blasts: dict[int, set[str]],
    *,
    graph_missing: bool = False,
) -> tuple[str, list[int]]:
    """Classify a candidate's parallel-safety against active slices.

    Returns ``(flag, overlapping_slice_nums)`` per the 4-value enum +
    precedence rule from ADR-064 + design.md L80:

      1. ``UNKNOWN-NO-GRAPH`` if ``graph_missing`` is True (caller-side
         override — applies to all candidates regardless of hint files).
      2. ``UNKNOWN-NO-HINT-FILES`` if ``candidate_files`` is empty.
      3. ``OVERLAPS-WITH-slice-NNN[, slice-MMM]`` if non-empty
         intersection with one or more active slices' blast sets.
      4. ``NON-OVERLAPPING`` otherwise (non-empty hint_files, empty
         intersection — including the zero-active-slices case per AC4-(b)).

    The empty-hint-files-vs-zero-active-slices collision (AC4-(d)) is
    explicit: precedence rule 2 fires before rule 4, so a candidate with
    empty ``hint_files`` flags ``UNKNOWN-NO-HINT-FILES`` even when
    ``active_blasts`` is empty.
    """
    if graph_missing:
        return _FLAG_UNKNOWN_NO_GRAPH, []
    if not candidate_files:
        return _FLAG_UNKNOWN_NO_HINT, []
    overlapping = sorted(
        n for n, blast in active_blasts.items()
        if candidate_files & blast
    )
    if overlapping:
        flag = "OVERLAPS-WITH-" + ", ".join(
            f"slice-{n:03d}" for n in overlapping
        )
        return flag, overlapping
    return _FLAG_NON_OVERLAPPING, []


# ---------------------------------------------------------------------
# Format markdown output
# ---------------------------------------------------------------------


def format_queue_md(
    items: list[dict],
    provenance_ts: datetime,
    *,
    warn_no_graph: bool = False,
    active_slice_num: int | None = None,
    pick_log_block: str = "",
) -> str:
    """Render the queue markdown body. Pure function (no I/O).

    ``items`` is a list of dicts with keys:
      ``name`` (str), ``source`` (str), ``blast_radius`` (set[str] | None
      where None means "unknown" e.g. graph missing), ``parallel_safety``
      (str — one of the 4 enum values), ``effort`` (str — SMALL/MEDIUM/
      LARGE), ``risk_retired`` (str — HIGH/MEDIUM/LOW/NONE).

    ``pick_log_block`` (slice-099 / BRANCH-3): the literal ``## Pick log``
    section (heading-through-EOF) carried forward verbatim from the existing
    queue, re-appended AFTER ``## Candidates``. This is the DISTINCT
    pick-log preservation path (NOT PSQ-2 claim-preservation, which keys on
    ``### entry`` headers a top-level ``## Pick log`` section lacks). Empty
    string → no pick-log section emitted (first-pick / pre-BRANCH-3 queue).
    """
    iso_ts = provenance_ts.strftime("%Y-%m-%dT%H:%M:%S")
    # Add UTC offset suffix if tzinfo present.
    if provenance_ts.tzinfo is not None:
        offset = provenance_ts.strftime("%z")
        if offset:
            iso_ts += f"{offset[:3]}:{offset[3:]}"
    provenance = (
        f"_Generated: {iso_ts} by /slice during "
        f"slice-{active_slice_num:03d} definition_"
        if active_slice_num is not None
        else f"_Generated: {iso_ts} by /slice_"
    )

    lines = [
        "# Slice queue",
        "",
        provenance,
        "",
    ]
    if warn_no_graph:
        lines.append(_WARN_NO_GRAPH_LINE)
        lines.append("")
    lines.append("## Candidates")
    lines.append("")
    if not items:
        lines.append(_NO_CANDIDATES_PLACEHOLDER)
        lines.append("")
    else:
        for item in items:
            lines.extend(_format_entry(item))
    body = "\n".join(lines).rstrip("\n") + "\n"
    # slice-099 / BRANCH-3: re-append the preserved `## Pick log` section verbatim.
    if pick_log_block:
        body = body.rstrip("\n") + "\n\n" + pick_log_block.rstrip("\n") + "\n"
    return body


def _format_entry(item: dict) -> list[str]:
    name = item["name"]
    blast = item.get("blast_radius")
    if blast is None:
        blast_cell = "`unknown`"
    elif not blast:
        blast_cell = "`unknown`"
    else:
        blast_cell = ", ".join(f"`{f}`" for f in sorted(blast))
    # Render the 5 PSQ-1 field lines FROM `_RENDERED_FIELD_LABELS` (slice-085 /
    # M3): the constant is the single render source, so the truncation-shape
    # reader and this writer can never disagree on the label set. Values are
    # zipped in the same fixed order as the labels.
    field_values = (
        item["source"],
        blast_cell,
        item["parallel_safety"],
        item["effort"],
        item["risk_retired"],
    )
    lines = [
        f"### {name}",
        "",
    ]
    lines.extend(
        f"{label} {value}"
        for label, value in zip(_RENDERED_FIELD_LABELS, field_values)
    )
    # PSQ-2 (slice-072): optional claim-line emission INSERT at [-2] before
    # the trailing empty-line separator (per Critic m1 ACCEPTED-FIXED —
    # preserves entry-block separation). Both claim keys present-or-absent
    # together per ADR-067 §Schema extension.
    claimed_by = item.get("claimed_by")
    claimed_at = item.get("claimed_at")
    if claimed_by and claimed_at:
        lines.append(f"- **Claimed-by:** {claimed_by}")
        lines.append(f"- **Claimed-at:** {claimed_at}")
    # PSQ-2 (slice-072): forward-compat unknown field lines from a future
    # PSQ-3+ extension (per ADR-067 §Consequences + Critic M3 ACCEPTED-FIXED).
    # _extra_field_lines preserved verbatim AFTER claim lines but BEFORE
    # trailing blank.
    extras = item.get("_extra_field_lines") or []
    for extra in extras:
        lines.append(extra)
    lines.append("")
    return lines


# ---------------------------------------------------------------------
# Pick log (slice-099 / BRANCH-3 / ADR-090)
# ---------------------------------------------------------------------


def _iso8601_utc(dt: datetime) -> str:
    """ISO-8601 UTC with `+00:00`-suffixed offset (matches PSQ-1/PSQ-2 format)."""
    iso = dt.strftime("%Y-%m-%dT%H:%M:%S")
    if dt.tzinfo is not None:
        offset = dt.strftime("%z")
        if offset:
            iso += f"{offset[:3]}:{offset[3:]}"
    return iso


def _extract_pick_log_block(text: str) -> str:
    """Return the literal ``## Pick log`` section (heading-through-EOF), or "".

    The pick log is ALWAYS the final section of the queue (re-appended after
    ``## Candidates``), so a single anchored match captures it verbatim. CRLF
    is normalized to LF before matching. Returns "" when no pick-log section
    exists (first pick / pre-BRANCH-3 queue) — the first-pick edge (M-add-3).
    """
    if not text:
        return ""
    norm = text.replace("\r\n", "\n")
    m = _PICK_LOG_BLOCK_RE.search(norm)
    return m.group(0).rstrip("\n") if m else ""


def record_pick(
    repo_root: Path,
    slice_name: str,
    picker_identity: str | tuple[str, str],
    now: datetime | None = None,
    *,
    out_path: Path | None = None,
) -> Path:
    """Append a pick-provenance line to ``slice-queue.md``'s ``## Pick log``.

    Line shape: ``- <slice_name> — picked <ISO-8601 UTC> by <picker_identity>``.

    - **Idempotent** (slice-099): scans the existing pick-log block for a line
      beginning ``- <slice_name> —`` (the trailing `` —`` is the name boundary,
      so ``slice-009-foo`` never matches ``slice-099-foo``); an already-recorded
      pick is a no-op.
    - **First-pick edge** (M-add-3): when no ``## Pick log`` section exists yet,
      it is created after the existing body; when present, the new line is
      appended to it.

    ``picker_identity`` is the caller-supplied ``"<git user.name> <user.email>"``
    (the cooperative git-identity model, ADR-067); the caller (``/slice``) obtains
    it via ``slice_queue_claim.read_git_config_user`` which is fail-visible on an
    unset git identity. Written via the R-32-safe ``safe_write_text``.

    A ``(name, email)`` 2-tuple — the exact shape ``read_git_config_user``
    returns — is accepted and space-joined to ``"name email"`` (slice-104), so the
    documented ``/slice`` Step 6.5 invocation cannot serialise a Python tuple repr
    (``by ('Name', 'email')``) into the pick-log line. A plain ``str`` is unchanged.
    """
    now = now or datetime.now(tz=timezone.utc)
    if out_path is None:
        out_path = repo_root / VAULT_ROOT / _QUEUE_FILENAME  # VAULT_ROOT-routed
    # slice-104: normalize the (name, email) 2-sequence read_git_config_user
    # returns so the line never serialises a tuple repr; str passes through.
    if isinstance(picker_identity, (tuple, list)):
        picker_identity = " ".join(str(part) for part in picker_identity)
    line = f"- {slice_name} — picked {_iso8601_utc(now)} by {picker_identity}"
    prefix = f"- {slice_name} —"

    text = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
    norm = text.replace("\r\n", "\n")
    block = _extract_pick_log_block(norm)

    if block:
        # Idempotent: already recorded → no-op.
        for ln in block.splitlines():
            if ln.startswith(prefix):
                return out_path
        new_block = block.rstrip("\n") + "\n" + line
        head = norm[: norm.rfind(block)].rstrip("\n")
        new_text = head + "\n\n" + new_block + "\n"
    else:
        # First-pick edge: create the `## Pick log` section after the body.
        base = norm.rstrip("\n")
        new_text = f"{base}\n\n{_PICK_LOG_HEADING}\n\n{line}\n" if base else (
            f"{_PICK_LOG_HEADING}\n\n{line}\n"
        )

    safe_write_text(out_path, new_text)
    return out_path


# ---------------------------------------------------------------------
# Top-level entrypoint
# ---------------------------------------------------------------------


def write_slice_queue(
    repo_root: Path,
    candidates: list[dict],
    active_slice_num: int,
    graph_path: Path | None = None,
    now: datetime | None = None,
    *,
    blast_resolver: Callable[[Path, str], set[str]] | None = None,
    out_path: Path | None = None,
) -> Path:
    """Write ``architecture/slice-queue.md``. Returns the output Path.

    Top-10 cap enforced. Idempotent overwrite (not append) via ``.tmp``
    sibling + ``os.replace()``.

    ``out_path`` (slice-071 / slice-067 m1 FIX per slice-067 code-Critic
    m1): when ``None`` (default), writes to the canonical
    ``architecture/slice-queue.md``; when provided (CLI ``--output
    <custom>`` path), writes to the given path. Collapses the previous
    duplicated ``main()`` custom-output branch — single source of truth for
    the candidate-loop + atomic-write sequence.
    """
    now = now or datetime.now(tz=timezone.utc)
    if out_path is None:
        out_path = repo_root / VAULT_ROOT / _QUEUE_FILENAME  # VAULT_ROOT-routed (slice-068)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # PSQ-2 (slice-072) integration: read existing queue and parse claims
    # so they survive across /slice Step 6.5 regeneration on candidates
    # whose names appear in the new top-10. Claims on dropped candidates
    # are silently discarded per AC4. Per ADR-067 §Consequences + Critic
    # B2 ACCEPTED-FIXED. Wrapped in try/except to keep PSQ-1 robust if
    # PSQ-2 module is unavailable (bootstrap safety per slice-067
    # ImportError-guard precedent).
    existing_claims: dict[str, dict[str, object]] = {}
    existing_pick_log = ""  # slice-099 / BRANCH-3: preserve `## Pick log` across regen
    if out_path.exists():
        try:
            existing_text = out_path.read_text(encoding="utf-8")
        except OSError:
            existing_text = ""
        # Pick-log extraction is independent of (and robust to) claim parsing —
        # a malformed `### Candidates` block must NOT drop the pick log.
        existing_pick_log = _extract_pick_log_block(existing_text)
        try:
            from tools.slice_queue_claim import parse_queue_text  # noqa: PLC0415
            existing_claims = parse_queue_text(existing_text)
        except Exception:
            # PSQ-2 module missing OR malformed existing queue — non-fatal
            # to PSQ-1's primary write; queue gets regenerated unclaimed.
            existing_claims = {}

    graph_missing = graph_path is None or not graph_path.exists()
    # Active slices: skip blast-radius derivation entirely when graph
    # missing (per AC4-(c) — all candidates flag UNKNOWN-NO-GRAPH).
    if graph_missing:
        active_blasts: dict[int, set[str]] = {}
    else:
        active_blasts = derive_active_slice_blast_radius(
            repo_root, graph_path, blast_resolver=blast_resolver,
        )

    # Top-10 cap.
    top = candidates[:_TOP_N]

    items: list[dict] = []
    for c in top:
        hint_files = set(c.get("hint_files") or [])
        if graph_missing:
            blast_radius: set[str] | None = None
            flag, _ = compute_parallel_safety(
                hint_files, active_blasts, graph_missing=True
            )
        else:
            # Expand candidate's hint files through graphify if available.
            if hint_files and blast_resolver is None:
                candidate_blast: set[str] = set(hint_files)
                for f in hint_files:
                    candidate_blast |= _call_graphify_blast_radius(graph_path, f)
            elif hint_files:
                candidate_blast = set(hint_files)
                for f in hint_files:
                    candidate_blast |= blast_resolver(graph_path, f)
            else:
                candidate_blast = set()
            blast_radius = candidate_blast
            flag, _ = compute_parallel_safety(
                candidate_blast, active_blasts, graph_missing=False
            )
        item = {
            "name": c["name"],
            "source": c["source"],
            "blast_radius": blast_radius,
            "parallel_safety": flag,
            "effort": c["effort"],
            "risk_retired": c["risk_retired"],
        }
        # PSQ-2 (slice-072) claim-preservation merge: copy claim metadata
        # + forward-compat extras onto the item if the candidate name
        # survived from the existing queue. Uses .get() to tolerate
        # absent claim keys on unclaimed entries per meta-Critic m-add-2
        # ACCEPTED-FIXED (parse_queue_text returns all entries; claim
        # keys absent on unclaimed).
        prev = existing_claims.get(c["name"])
        if prev is not None:
            claimed_by = prev.get("claimed_by")
            claimed_at = prev.get("claimed_at")
            if claimed_by and claimed_at:
                item["claimed_by"] = claimed_by
                item["claimed_at"] = claimed_at
            extras = prev.get("_extra_field_lines") or []
            if extras:
                item["_extra_field_lines"] = list(extras)
        items.append(item)

    body = format_queue_md(
        items, now,
        warn_no_graph=graph_missing,
        active_slice_num=active_slice_num,
        pick_log_block=existing_pick_log,  # slice-099 / BRANCH-3: preserve pick log
    )

    # slice-094 (VWS-1): routed through _vault_write.safe_write_text — the
    # R-32-safe vault writer (sidecar lock + LF-faithful newline="" + atomic
    # os.replace + bounded EPERM-retry). Byte output is IDENTICAL to the prior
    # inline .tmp + write_text(newline="") + os.replace pattern (safe_write_text
    # is LF-faithful per slice-094 B1), so PSQ-1/PSQ-2 byte-equal
    # claim-preservation round-trip assertions are preserved. NB: routing makes
    # the WRITE atomic+locked; the read-modify-write window in the caller is a
    # documented flip-residual (B2), not closed here.
    safe_write_text(out_path, body)
    return out_path


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m tools.slice_queue_writer",
        description="Write parallel-slice queue output (PSQ-1, slice-067).",
    )
    p.add_argument(
        "--candidates-json", type=Path, required=True,
        help="Path to a JSON file holding the candidates list.",
    )
    p.add_argument(
        "--active-slice", type=int, required=True,
        help="Active slice number (used in the provenance line).",
    )
    p.add_argument(
        "--output", type=Path,
        default=VAULT_ROOT / _QUEUE_FILENAME,  # VAULT_ROOT-routed (slice-068)
        help="Output queue file path (default: architecture/slice-queue.md).",
    )
    p.add_argument(
        "--graph", type=Path,
        default=_GRAPH_DEFAULT_REL,
        help="Path to graphify-out/graph.json (default).",
    )
    p.add_argument(
        "--root", type=Path, default=Path("."),
        help="Repo root (default: cwd).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2

    if not args.candidates_json.exists():
        print(
            f"PSQ-1 usage error: candidates JSON not found: "
            f"{args.candidates_json}",
            file=sys.stderr,
        )
        return 2
    try:
        candidates = json.loads(
            args.candidates_json.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as e:
        print(
            f"PSQ-1 usage error: candidates JSON parse failed: {e}",
            file=sys.stderr,
        )
        return 2
    if not isinstance(candidates, list):
        print(
            "PSQ-1 usage error: candidates JSON must be a list",
            file=sys.stderr,
        )
        return 2

    # Output path may be relative to --root if not absolute.
    out_arg = args.output
    if not out_arg.is_absolute():
        out_arg = args.root / out_arg
    # write_slice_queue expects architecture/<filename>; if --output is
    # absolute or differs, write directly via format_queue_md.
    graph_path = args.graph if args.graph.is_absolute() else args.root / args.graph
    repo_root = args.root.resolve()

    # slice-071 / slice-067 m1 FIX (per slice-067 code-Critic m1): collapse
    # the previous custom-output duplicated branch into the canonical
    # library call with `out_path=out_arg`. Both canonical-output and
    # custom-output paths now traverse the same atomic-write + candidate-
    # loop logic — single source of truth eliminates the Fowler
    # "Duplicated Code" smell.
    write_slice_queue(
        repo_root=repo_root,
        candidates=candidates,
        active_slice_num=args.active_slice,
        graph_path=graph_path if graph_path.exists() else None,
        out_path=out_arg,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
