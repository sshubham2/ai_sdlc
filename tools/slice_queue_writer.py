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
import json
import re
import subprocess
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from tools import _stdout


_TOP_N = 10
_QUEUE_FILENAME = "slice-queue.md"
_INDEX_MD_REL = Path("architecture") / "slices" / "_index.md"
_SLICES_DIR_REL = Path("architecture") / "slices"
_GRAPH_DEFAULT_REL = Path("graphify-out") / "graph.json"

# Per design.md L80 + ADR-064 §Consequences: 4-value Parallel-safety enum.
_FLAG_NON_OVERLAPPING = "NON-OVERLAPPING"
_FLAG_UNKNOWN_NO_HINT = "UNKNOWN-NO-HINT-FILES"
_FLAG_UNKNOWN_NO_GRAPH = "UNKNOWN-NO-GRAPH"

_WARN_NO_GRAPH_LINE = (
    "_WARN: graphify graph missing — blast-radius enrichment skipped; "
    "rebuild with `$PY -m graphify code .`_"
)
_NO_CANDIDATES_PLACEHOLDER = "_(no candidates)_"


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


def _call_graphify_blast_radius(
    graph_path: Path, file_or_node: str
) -> set[str]:
    """Thin wrapper invoking ``graphify blast-radius`` for a single node.

    Adapted from ``skills/slice-candidates/build_backlog.py:120-155``. Tries
    ``--file <basename>`` first (current graph node-ID shape uses basenames);
    falls back to ``--from <full-path>`` (legacy node-ID shape). Returns the
    set of affected node IDs as strings, or empty set on any failure.
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
        if isinstance(data, list):
            return {str(x) for x in data}
        if isinstance(data, dict):
            for key in ("nodes", "blast_radius", "affected"):
                if key in data and isinstance(data[key], list):
                    return {str(x) for x in data[key]}
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
) -> str:
    """Render the queue markdown body. Pure function (no I/O).

    ``items`` is a list of dicts with keys:
      ``name`` (str), ``source`` (str), ``blast_radius`` (set[str] | None
      where None means "unknown" e.g. graph missing), ``parallel_safety``
      (str — one of the 4 enum values), ``effort`` (str — SMALL/MEDIUM/
      LARGE), ``risk_retired`` (str — HIGH/MEDIUM/LOW/NONE).
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
    return "\n".join(lines).rstrip("\n") + "\n"


def _format_entry(item: dict) -> list[str]:
    name = item["name"]
    blast = item.get("blast_radius")
    if blast is None:
        blast_cell = "`unknown`"
    elif not blast:
        blast_cell = "`unknown`"
    else:
        blast_cell = ", ".join(f"`{f}`" for f in sorted(blast))
    return [
        f"### {name}",
        "",
        f"- **Source:** {item['source']}",
        f"- **Blast-radius:** {blast_cell}",
        f"- **Parallel-safety:** {item['parallel_safety']}",
        f"- **Effort:** {item['effort']}",
        f"- **Risk-retired:** {item['risk_retired']}",
        "",
    ]


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
) -> Path:
    """Write ``architecture/slice-queue.md``. Returns the output Path.

    Top-10 cap enforced. Idempotent overwrite (not append) via ``.tmp``
    sibling + ``os.replace()``.
    """
    now = now or datetime.now(tz=timezone.utc)
    out_path = repo_root / "architecture" / _QUEUE_FILENAME
    out_path.parent.mkdir(parents=True, exist_ok=True)

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
        items.append({
            "name": c["name"],
            "source": c["source"],
            "blast_radius": blast_radius,
            "parallel_safety": flag,
            "effort": c["effort"],
            "risk_retired": c["risk_retired"],
        })

    body = format_queue_md(
        items, now,
        warn_no_graph=graph_missing,
        active_slice_num=active_slice_num,
    )

    # Atomic write: .tmp sibling + os.replace().
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp_path.write_text(body, encoding="utf-8")
    import os as _os
    _os.replace(tmp_path, out_path)
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
        default=Path("architecture") / _QUEUE_FILENAME,
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

    # If --output is exactly <root>/architecture/slice-queue.md, use the
    # library entrypoint. Otherwise compose the write manually so users
    # can redirect output for testing/integration scenarios.
    canonical_out = repo_root / "architecture" / _QUEUE_FILENAME
    if out_arg.resolve() == canonical_out:
        write_slice_queue(
            repo_root=repo_root,
            candidates=candidates,
            active_slice_num=args.active_slice,
            graph_path=graph_path if graph_path.exists() else None,
        )
    else:
        # Direct write to custom path (rare).
        out_arg.parent.mkdir(parents=True, exist_ok=True)
        graph_missing = not graph_path.exists()
        active_blasts = (
            derive_active_slice_blast_radius(repo_root, graph_path)
            if not graph_missing else {}
        )
        items: list[dict] = []
        for c in candidates[:_TOP_N]:
            hint_files = set(c.get("hint_files") or [])
            if graph_missing:
                flag, _ = compute_parallel_safety(
                    hint_files, active_blasts, graph_missing=True
                )
                blast_radius: set[str] | None = None
            else:
                cb = set(hint_files)
                for f in hint_files:
                    cb |= _call_graphify_blast_radius(graph_path, f)
                blast_radius = cb
                flag, _ = compute_parallel_safety(
                    cb, active_blasts, graph_missing=False
                )
            items.append({
                "name": c["name"], "source": c["source"],
                "blast_radius": blast_radius, "parallel_safety": flag,
                "effort": c["effort"], "risk_retired": c["risk_retired"],
            })
        body = format_queue_md(
            items, datetime.now(tz=timezone.utc),
            warn_no_graph=graph_missing,
            active_slice_num=args.active_slice,
        )
        import os as _os
        tmp = out_arg.with_suffix(out_arg.suffix + ".tmp")
        tmp.write_text(body, encoding="utf-8")
        _os.replace(tmp, out_arg)

    return 0


if __name__ == "__main__":
    sys.exit(main())
