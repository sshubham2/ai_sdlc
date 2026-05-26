"""Repro: tools/slice_queue_writer.py leaks raw graphify-node dict-strings.

Bug: SC-027 — see ``diagnose-out/backlog.md:558-576``.

When ``graphify blast-radius --format json`` returns a JSON LIST of node
OBJECTS (the current graphify output shape), ``_call_graphify_blast_radius``
stringifies each element verbatim via ``{str(x) for x in data}`` (lines 246 +
250). For dict elements ``x`` with the empirically-verified shape
``{"id": "<id>", "label": "<label>", "type": "", "path": ""}`` (per
``~/.claude/packages/graphify/graphify/__main__.py:1009-1014`` — ``"path":
data.get("path", "")`` always empty in this repo; ``name`` key absent;
``id`` is the only universally-populated key), ``str(x)`` yields a literal
dict-string containing the characters ``{``, ``'``, ``:`` that any downstream
consumer parsing the rendered ``Blast-radius:`` cell as a comma-separated
path list will trip on.

The leak is empirically visible in committed ``architecture/slice-queue.md``
at lines 18, 34, 42 (post-slice-069 queue write). The fix builds an
``{id → repo-relative source_file}`` map from ``graph.json`` (the underlying
node carries the real path in its ``source_file`` field) and resolves a
node-dict's ``id`` against this map.

Expected post-fix behavior: ``_call_graphify_blast_radius`` returns a set
of path-shaped strings ONLY (no ``{``, ``'``, ``:`` characters; positive-
shape regex satisfied).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from tools.slice_queue_writer import _call_graphify_blast_radius


# Empirically-verified graphify-in-this-repo blast-radius output shape:
# list of node-dicts with {"id", "label", "type":"", "path":""} — `type` and
# `path` are STRUCTURALLY EMPTY (per __main__.py:1013 — `"path":
# data.get("path", "")`); `name` key is ABSENT from the schema entirely;
# `id` is the only universally-populated key. The real file path lives in
# `graph.json`'s `source_file` field under matching `id`.
_REAL_GRAPHIFY_NODE_LIST_JSON = json.dumps([
    {
        "id": "slice_queue_writer_rationale_1",
        "label": "Parallel-slice queue writer (PSQ-1).",
        "type": "",
        "path": "",
    },
    {
        "id": "branch_workflow_audit_rationale_1",
        "label": "Branch workflow audit (BRANCH-1).",
        "type": "",
        "path": "",
    },
])

# The id → source_file map that `_build_id_to_path_map` would construct
# from a graph.json containing these two nodes' source_file fields.
_EXPECTED_ID_TO_PATH = {
    "slice_queue_writer_rationale_1": "tools/slice_queue_writer.py",
    "branch_workflow_audit_rationale_1": "tools/branch_workflow_audit.py",
}


def _fake_subprocess_run(*args, **kwargs):
    return SimpleNamespace(
        returncode=0,
        stdout=_REAL_GRAPHIFY_NODE_LIST_JSON,
        stderr="",
    )


def test_blast_radius_resolves_real_graphify_node_shape_via_id_lookup():
    """SC-027 repro: when graphify returns the real-shape node list with
    empty `path` and absent `name`, `_call_graphify_blast_radius` must
    resolve each node's `id` via the `_build_id_to_path_map` lookup and
    return the mapped repo-relative source_file paths — NOT stringify the
    dicts.

    Pre-fix: code does `{str(x) for x in data}` → returns dict-strings
    like ``"{'id': '...', 'label': '...', 'type': '', 'path': ''}"`` which
    contain `{`, `'`, `:` and are not path-shaped.

    Post-fix: code calls `_build_id_to_path_map(graph_path)` once at entry,
    then resolves each node-dict's `id` against the map. Result set is
    exactly ``{"tools/slice_queue_writer.py",
    "tools/branch_workflow_audit.py"}``.

    This test mocks BOTH `subprocess.run` (so we don't actually run
    graphify) AND `_build_id_to_path_map` (so we don't need a real
    graph.json fixture). The fix's id-lookup precedence is what makes the
    test pass.
    """
    with patch.object(subprocess, "run", side_effect=_fake_subprocess_run), \
         patch(
             "tools.slice_queue_writer._build_id_to_path_map",
             return_value=_EXPECTED_ID_TO_PATH,
             create=True,  # helper doesn't exist pre-fix; created at /build-slice
         ):
        result = _call_graphify_blast_radius(
            Path("graphify-out/graph.json"),
            "tools/slice_queue_writer.py",
        )
    assert result, "wrapper returned an empty set (graphify call appeared to fail)"
    leaky_chars = {"{", "'", ":"}
    offenders = [r for r in result if any(c in r for c in leaky_chars)]
    assert offenders == [], (
        f"Blast-radius cell would contain dict-string leak(s): {offenders!r}. "
        "Expected path-shaped strings only."
    )
    assert result == {
        "tools/slice_queue_writer.py",
        "tools/branch_workflow_audit.py",
    }, f"Expected id-lookup-resolved path set; got {result!r}"


# ---------------------------------------------------------------------
# AC#2 supplemental — multi-shape coverage
# ---------------------------------------------------------------------


_LEGACY_LIST_OF_STRINGS_JSON = json.dumps(
    ["tools/foo.py", "tools/bar.py"]
)


def test_blast_radius_handles_legacy_list_of_strings_shape():
    """AC2 shape (a): legacy list-of-strings input — path-shaped strings
    returned verbatim. No id-lookup needed; the `id_to_path` map is
    unused (and can be empty since the strings are already path-shaped)."""

    def _fake_run(*args, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=_LEGACY_LIST_OF_STRINGS_JSON,
            stderr="",
        )

    with patch.object(subprocess, "run", side_effect=_fake_run), \
         patch(
             "tools.slice_queue_writer._build_id_to_path_map",
             return_value={},
             create=True,
         ):
        result = _call_graphify_blast_radius(
            Path("graphify-out/graph.json"),
            "tools/slice_queue_writer.py",
        )
    assert result == {"tools/foo.py", "tools/bar.py"}, (
        f"Path-shaped legacy strings must be preserved verbatim; got {result!r}"
    )


_MIXED_LEGACY_STRINGS_JSON = json.dumps([
    "tools/foo.py",
    "opaque_identifier",
    "another_id_no_separator",
])


def test_blast_radius_drops_non_path_strings_from_legacy_shape():
    """AC2 shape (a) negative: legacy list-of-strings with mixed path-shaped
    and ID-only strings — only path-shaped survive. Mirrors
    `_parse_text_nodes`'s "/" filter discipline at L255."""

    def _fake_run(*args, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=_MIXED_LEGACY_STRINGS_JSON,
            stderr="",
        )

    with patch.object(subprocess, "run", side_effect=_fake_run), \
         patch(
             "tools.slice_queue_writer._build_id_to_path_map",
             return_value={},
             create=True,
         ):
        result = _call_graphify_blast_radius(
            Path("graphify-out/graph.json"),
            "tools/slice_queue_writer.py",
        )
    assert result == {"tools/foo.py"}, (
        f"Only path-shaped strings should survive; got {result!r}"
    )


_DICT_WITH_NODES_KEY_JSON = json.dumps({
    "nodes": [
        {
            "id": "slice_queue_writer_rationale_1",
            "label": "Parallel-slice queue writer (PSQ-1).",
            "type": "",
            "path": "",
        },
        {
            "id": "validate_slice_layers_rationale_1",
            "label": "Validate slice layers.",
            "type": "",
            "path": "",
        },
    ]
})


def test_blast_radius_handles_dict_with_nodes_key_of_node_dicts():
    """AC2 shape (c): graphify returns a JSON object with `nodes`-keyed
    list-of-dicts (the second leaky comprehension at the original L250
    path). Same id-lookup precedence as the list-of-dicts shape — the fix
    must thread `id_to_path` into both comprehensions."""

    def _fake_run(*args, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=_DICT_WITH_NODES_KEY_JSON,
            stderr="",
        )

    id_to_path = {
        "slice_queue_writer_rationale_1": "tools/slice_queue_writer.py",
        "validate_slice_layers_rationale_1": "tools/validate_slice_layers.py",
    }
    with patch.object(subprocess, "run", side_effect=_fake_run), \
         patch(
             "tools.slice_queue_writer._build_id_to_path_map",
             return_value=id_to_path,
             create=True,
         ):
        result = _call_graphify_blast_radius(
            Path("graphify-out/graph.json"),
            "tools/slice_queue_writer.py",
        )
    assert result == {
        "tools/slice_queue_writer.py",
        "tools/validate_slice_layers.py",
    }, f"Expected id-lookup-resolved path set; got {result!r}"


_FORWARD_COMPAT_DICT_LIST_JSON = json.dumps([
    {"id": "unknown_id_path", "path": "tools/foo.py"},
    {"id": "unknown_id_source_file", "source_file": "tools/bar.py"},
    {"id": "third_unknown", "name": "opaque_no_separator"},
])


def test_blast_radius_forward_compat_extracts_populated_path_or_source_file():
    """AC2 shape (d): forward-compat — dicts whose `id` is absent from
    `id_to_path` map fall through to dict-own-keys `path` / `source_file`
    / `name`, provided the value is path-shaped. Non-path-shaped values
    are dropped per the `_is_path_shaped` filter."""

    def _fake_run(*args, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=_FORWARD_COMPAT_DICT_LIST_JSON,
            stderr="",
        )

    with patch.object(subprocess, "run", side_effect=_fake_run), \
         patch(
             "tools.slice_queue_writer._build_id_to_path_map",
             return_value={},
             create=True,
         ):
        result = _call_graphify_blast_radius(
            Path("graphify-out/graph.json"),
            "tools/slice_queue_writer.py",
        )
    assert result == {"tools/foo.py", "tools/bar.py"}, (
        f"Forward-compat path-shape extraction must drop non-path `name`; "
        f"got {result!r}"
    )


# ---------------------------------------------------------------------
# AC#3 — live-artifact positive-shape pin
# ---------------------------------------------------------------------


import re as _re

# Per /critique M1 fix + /build-slice 2026-05-26 DEVIATION widening:
# positive-shape regex accepts tokens that (a) contain a path separator,
# (b) end with a `.alphanum` extension, OR (c) are leading-dot dotfiles
# like `.gitignore` / `.env`. Rejects bare opaque identifiers, dict-string
# leaks, empty tokens, and other non-path corruption classes.
_PATH_SHAPED_TOKEN_RE = _re.compile(
    r"^(?:[^\s`]*[/\\][^\s`]+"          # has path separator
    r"|[^\s`]*\.[A-Za-z0-9]{1,8}"       # ends with .ext (1-8 alphanum)
    r"|\.[A-Za-z][A-Za-z0-9_.-]*)$"     # leading-dot dotfile
)

# Matches a `Blast-radius:` cell line and captures its value portion.
_BLAST_RADIUS_LINE_RE = _re.compile(
    r"^-\s*\*\*Blast-radius:\*\*\s*(.+?)\s*$", _re.MULTILINE
)

# Matches each backtick-quoted token in the cell value.
_BACKTICK_TOKEN_RE = _re.compile(r"`([^`]+)`")


def _project_root() -> Path:
    """Resolve repo-root (walks up for `.git`)."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("could not locate repo root (no .git up-tree)")


def test_committed_slice_queue_md_blast_radius_cells_contain_only_path_shaped_tokens():
    """AC3 live-artifact pin: every backtick-quoted token in every
    `Blast-radius:` cell value of the committed `architecture/slice-queue.md`
    must match the positive-shape regex — contain a path separator OR end
    with a known file extension.

    This catches SC-027's dict-string leak AND the wider opaque-identifier
    leak class (per /critique M1 fix — IDs without `/`/`\\`/known-extension
    FAIL even though they contain no `{`/`'`/`:` characters).

    Failure means the committed file was NOT regenerated after the fix
    OR the fix regressed. The slice's /build-slice Phase C is responsible
    for regenerating the live file post-fix.
    """
    root = _project_root()
    queue_path = root / "architecture" / "slice-queue.md"
    assert queue_path.exists(), (
        f"architecture/slice-queue.md not present at {queue_path}; "
        "PSQ-1 helper has never been invoked or file was deleted"
    )
    text = queue_path.read_text(encoding="utf-8")
    cells = _BLAST_RADIUS_LINE_RE.findall(text)
    assert cells, (
        "No `Blast-radius:` cells found in slice-queue.md — "
        "format may have changed; verify PSQ-1 invariant"
    )
    offenders: list[tuple[int, str, str]] = []
    for line_idx, cell_value in enumerate(cells):
        for token in _BACKTICK_TOKEN_RE.findall(cell_value):
            if not _PATH_SHAPED_TOKEN_RE.match(token):
                offenders.append((line_idx, cell_value[:80], token))
    assert offenders == [], (
        f"Non-path-shaped tokens in `Blast-radius:` cells (SC-027 regression "
        f"OR /build-slice Phase C regenerate skipped):\n"
        + "\n".join(
            f"  cell #{idx}: token={tok!r} (in cell starting {cell[:60]!r}...)"
            for idx, cell, tok in offenders[:10]
        )
    )
