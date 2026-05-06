"""
build_backlog.py — turn confirmed findings from a diagnose-out/ into backlog.md.

Reads:
  $IN/diagnosis.html              (annotated by owner; embedded JSON has
                                   findings + annotations)
  $IN/findings/*.yaml             (optional fallback; used only if the HTML
                                   has no embedded findings)
  $IN/graphify-out/graph.json     (optional, for blast-radius dependency hints)

Writes:
  $IN/backlog.md                  (slice candidates, DAG-ordered,
                                   pipeline-agnostic)

NEVER reads from or writes to the analyzed source repo. Inputs are confined
to the diagnose-out directory. Output goes back into the same directory.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}
BLAST_RANK = {"large": 3, "medium": 2, "small": 1}
EFFORT_RANK = {"large": 3, "medium": 2, "small": 1}


# ---------------------------------------------------------------------------
# Loading inputs
# ---------------------------------------------------------------------------


def parse_html_state(html_path: Path) -> dict:
    """Extract embedded JSON state from diagnosis.html."""
    if not html_path.exists():
        raise SystemExit(f"Not found: {html_path}")
    text = html_path.read_text(encoding="utf-8")
    m = re.search(
        r'<script\s+type="application/json"\s+id="diagnose-data">(.*?)</script>',
        text,
        re.DOTALL,
    )
    if not m:
        raise SystemExit(
            "diagnosis.html has no embedded findings JSON. Was it produced "
            "by /diagnose? If you opened it in a browser and saved, the "
            "save process should preserve the embedded JSON."
        )
    raw = m.group(1).strip()
    raw = raw.replace("<\\/script>", "</script>")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Embedded JSON is not valid: {exc}")


def load_findings_fallback(findings_dir: Path) -> dict[str, dict]:
    """Fallback: load findings from per-pass YAMLs."""
    by_id: dict[str, dict] = {}
    if not findings_dir.exists():
        return by_id
    for path in sorted(findings_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        except yaml.YAMLError as exc:
            raise SystemExit(f"YAML parse failure in {path}: {exc}")
        if not isinstance(data, list):
            continue
        for entry in data:
            if "id" in entry:
                by_id[entry["id"]] = entry
    return by_id


def get_findings(state: dict, fallback_dir: Path) -> dict[str, dict]:
    findings = state.get("findings") or []
    if findings:
        return {f["id"]: f for f in findings if "id" in f}
    return load_findings_fallback(fallback_dir)


def confirmed_findings(
    findings_by_id: dict[str, dict], annotations: dict[str, dict]
) -> list[dict]:
    out = []
    for fid, anno in (annotations or {}).items():
        if str(anno.get("confirmed", "")).strip().lower() != "yes":
            continue
        if fid not in findings_by_id:
            print(
                f"warning: confirmed finding {fid} has no matching entry — "
                "skipping",
                file=sys.stderr,
            )
            continue
        f = dict(findings_by_id[fid])
        f["_owner_notes"] = anno.get("notes", "")
        out.append(f)
    return out


# ---------------------------------------------------------------------------
# Dependency graph
# ---------------------------------------------------------------------------


def evidence_files(finding: dict) -> list[str]:
    return [e["path"] for e in finding.get("evidence", []) if "path" in e]


def graphify_blast_radius(graph_path: Path, node: str) -> set[str]:
    py = sys.executable
    cmd = [
        py, "-m", "graphify", "blast-radius",
        f"--from={node}",
        "--graph", str(graph_path),
        "--json",
    ]
    try:
        res = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return set()
    if res.returncode != 0:
        cmd_text = cmd[:-1]
        try:
            res = subprocess.run(
                cmd_text, capture_output=True, text=True, timeout=30, check=False,
            )
        except subprocess.TimeoutExpired:
            return set()
        if res.returncode != 0:
            return set()
        return _parse_text_nodes(res.stdout)
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


def _parse_text_nodes(text: str) -> set[str]:
    nodes: set[str] = set()
    for ln in text.splitlines():
        ln = ln.strip().lstrip("-* ").strip()
        if ln and not ln.startswith("#") and "/" in ln:
            nodes.add(ln)
    return nodes


def build_dependencies(
    candidates: list[dict], graph_path: Path | None
) -> tuple[dict[str, set[str]], bool]:
    ids = [c["id"] for c in candidates]
    edges: dict[str, set[str]] = {i: set() for i in ids}
    used_graphify = False

    files_by_id = {c["id"]: set(evidence_files(c)) for c in candidates}
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if files_by_id[a] & files_by_id[b]:
                edges[a].add(b)
                edges[b].add(a)

    if graph_path and graph_path.exists():
        unique_files: set[str] = set()
        for c in candidates:
            unique_files.update(evidence_files(c))
        cache: dict[str, set[str]] = {}
        for f in unique_files:
            br = graphify_blast_radius(graph_path, f)
            if br:
                used_graphify = True
            cache[f] = br
        for a in candidates:
            for b in candidates:
                if a is b:
                    continue
                a_files = files_by_id[a["id"]]
                for bf in evidence_files(b):
                    if cache.get(bf, set()) & a_files:
                        edges[b["id"]].add(a["id"])
                        break
    return edges, used_graphify


def detect_cycles(edges: dict[str, set[str]]) -> list[list[str]]:
    index_counter = [0]
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    sccs: list[list[str]] = []

    def strongconnect(v: str) -> None:
        indices[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)
        for w in edges.get(v, ()):
            if w not in indices:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif w in on_stack:
                lowlinks[v] = min(lowlinks[v], indices[w])
        if lowlinks[v] == indices[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                scc.append(w)
                if w == v:
                    break
            if len(scc) > 1:
                sccs.append(sorted(scc))

    for v in list(edges.keys()):
        if v not in indices:
            strongconnect(v)
    return sccs


def priority_score(c: dict) -> int:
    sev = SEVERITY_RANK.get(c.get("severity"), 0)
    blast = BLAST_RANK.get(c.get("blast_radius"), 0)
    effort = EFFORT_RANK.get(c.get("effort_estimate"), 1) or 1
    return (sev * 10) + blast - effort


def topo_with_priority(
    candidates: list[dict],
    edges: dict[str, set[str]],
    cycles: list[list[str]],
) -> list[str]:
    cycle_of: dict[str, int] = {}
    for i, scc in enumerate(cycles):
        for n in scc:
            cycle_of[n] = i

    cand_by_id = {c["id"]: c for c in candidates}

    def super_of(n: str) -> str:
        if n in cycle_of:
            return f"_C{cycle_of[n]}"
        return n

    super_edges: dict[str, set[str]] = defaultdict(set)
    super_nodes: set[str] = set()
    for n in edges:
        sn = super_of(n)
        super_nodes.add(sn)
        for m in edges[n]:
            sm = super_of(m)
            if sm != sn:
                super_edges[sn].add(sm)
                super_nodes.add(sm)

    indeg: dict[str, int] = {s: 0 for s in super_nodes}
    for s, outs in super_edges.items():
        for o in outs:
            indeg[o] = indeg.get(o, 0) + 1

    def priority(super_id: str) -> tuple[int, str]:
        if super_id.startswith("_C"):
            members = cycles[int(super_id[2:])]
            best = max(
                (priority_score(cand_by_id[m]) for m in members), default=0
            )
            return (-best, super_id)
        return (-priority_score(cand_by_id[super_id]), super_id)

    queue = sorted([s for s, d in indeg.items() if d == 0], key=priority)
    order: list[str] = []
    while queue:
        node = queue.pop(0)
        if node.startswith("_C"):
            members = cycles[int(node[2:])]
            order.extend(
                sorted(members, key=lambda m: -priority_score(cand_by_id[m]))
            )
        else:
            order.append(node)
        for o in sorted(super_edges.get(node, set()), key=priority):
            indeg[o] -= 1
            if indeg[o] == 0:
                inserted = False
                for i, q in enumerate(queue):
                    if priority(o) < priority(q):
                        queue.insert(i, o)
                        inserted = True
                        break
                if not inserted:
                    queue.append(o)
    return order


def assign_sc_ids(order: list[str]) -> dict[str, str]:
    return {fid: f"SC-{i+1:03d}" for i, fid in enumerate(order)}


def risk_profile(c: dict) -> str:
    sev = c.get("severity", "?")
    rev = c.get("reversibility", "?")
    blast = c.get("blast_radius", "?")
    return f"severity {sev}, {rev} to back out, {blast} blast radius"


def render_backlog(
    candidates: list[dict],
    edges: dict[str, set[str]],
    cycles: list[list[str]],
    order: list[str],
    sc_ids: dict[str, str],
    used_graphify: bool,
    in_dir: Path,
) -> str:
    cand_by_id = {c["id"]: c for c in candidates}
    edge_count = sum(len(v) for v in edges.values())
    parts: list[str] = []
    parts.append("# Slice candidates backlog\n\n")
    parts.append(
        f"_Generated from `{in_dir.name}/diagnosis.html` on "
        f"{datetime.now(timezone.utc).isoformat(timespec='seconds')}._\n\n"
    )
    parts.append(
        f"**{len(candidates)}** confirmed findings → "
        f"**{len(candidates)}** slice candidates. "
        f"**{edge_count}** dependency edges. "
        f"**{len(cycles)}** must-do-together clusters.\n\n"
    )
    if not used_graphify:
        parts.append(
            "_Note: graphify blast-radius was unavailable; dependencies were "
            "computed from shared-evidence overlap only._\n\n"
        )

    parts.append("## Recommended order\n\n")
    parts.append(
        "Topo-sorted by dependency, prioritized within each layer by "
        "severity × blast / effort:\n\n"
    )
    for i, fid in enumerate(order, 1):
        c = cand_by_id[fid]
        parts.append(f"{i}. **{sc_ids[fid]}** — {c['title']}\n")
    parts.append("\n")

    if cycles:
        parts.append("## Must-do-together clusters\n\n")
        parts.append(
            "These candidates have circular file overlap. Treat them as one "
            "unit of work or split carefully:\n\n"
        )
        for i, scc in enumerate(cycles, 1):
            members = ", ".join(sc_ids[m] for m in scc)
            parts.append(f"- Cluster {i}: {members}\n")
        parts.append("\n")

    parts.append("## Dependency map\n\n")
    parts.append("```\n")
    for src in order:
        for dst in sorted(edges.get(src, set())):
            if dst in sc_ids:
                parts.append(f"{sc_ids[src]} -> {sc_ids[dst]}\n")
    parts.append("```\n\n")

    parts.append("## Candidates\n\n")
    for fid in order:
        c = cand_by_id[fid]
        sc = sc_ids[fid]
        deps = sorted(
            sc_ids[d] for d, outs in edges.items() if fid in outs and d in sc_ids
        )
        blocks = sorted(sc_ids[d] for d in edges.get(fid, set()) if d in sc_ids)
        ev_lines = "\n".join(
            f"  - `{e['path']}:{e.get('lines', '')}` — {e.get('note', '')}"
            for e in c.get("evidence", [])
        )
        parts.append(f"### {sc} — {c['title']}\n\n")
        parts.append(f"- **Source finding:** {c['id']}\n")
        if c.get("_owner_notes"):
            parts.append(f"- **Owner notes:** {c['_owner_notes']}\n")
        parts.append(
            f"- **Severity:** {c.get('severity', '?')}  •  "
            f"**Blast:** {c.get('blast_radius', '?')}  •  "
            f"**Reversibility:** {c.get('reversibility', '?')}  •  "
            f"**Effort:** {c.get('effort_estimate', '?')}\n"
        )
        parts.append(f"- **Risk profile:** {risk_profile(c)}\n")
        parts.append(f"- **Dependencies:** {', '.join(deps) if deps else 'none'}\n")
        parts.append(f"- **Blocks:** {', '.join(blocks) if blocks else 'none'}\n")
        parts.append(f"- **Description:**\n\n{c.get('description', '').rstrip()}\n\n")
        rationale = (
            f"Confirmed by owner from finding {c['id']}. "
            f"{risk_profile(c).capitalize()}."
        )
        parts.append(f"- **Rationale:** {rationale}\n")
        parts.append(
            f"- **Suggested approach:** {c.get('suggested_action', '').rstrip()}\n"
        )
        parts.append(f"- **Evidence:**\n{ev_lines}\n\n")
    return "".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build slice-candidates backlog.md")
    ap.add_argument("--in", dest="in_dir", required=True, help="Path to diagnose-out")
    args = ap.parse_args()
    in_dir = Path(args.in_dir).resolve()

    diagnosis_html = in_dir / "diagnosis.html"
    findings_dir = in_dir / "findings"
    graph_path = in_dir / "graphify-out" / "graph.json"

    state = parse_html_state(diagnosis_html)
    findings_by_id = get_findings(state, findings_dir)
    annotations = state.get("annotations") or {}

    candidates = confirmed_findings(findings_by_id, annotations)

    if not candidates:
        raise SystemExit(
            "No findings have Confirmed=yes in diagnosis.html. "
            "Open the file in a browser, set the Confirmed dropdown to 'yes' "
            "for any findings to act on, click 'Save annotated HTML', then "
            "place the saved file back in diagnose-out/ and re-run."
        )

    edges, used_graphify = build_dependencies(
        candidates, graph_path if graph_path.exists() else None
    )
    cycles = detect_cycles(edges)
    order = topo_with_priority(candidates, edges, cycles)
    for c in candidates:
        if c["id"] not in order:
            order.append(c["id"])
    sc_ids = assign_sc_ids(order)

    backlog_md = render_backlog(
        candidates, edges, cycles, order, sc_ids, used_graphify, in_dir
    )
    out_path = in_dir / "backlog.md"
    out_path.write_text(backlog_md, encoding="utf-8")

    edge_count = sum(len(v) for v in edges.values())
    print(
        f"{len(candidates)} candidates, {edge_count} edges, {len(cycles)} cycles."
    )
    print(f"Wrote: {out_path}")
    if order:
        first = candidates[0]
        for c in candidates:
            if c["id"] == order[0]:
                first = c
                break
        print(f"Top candidate: {sc_ids[order[0]]} — {first['title']}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        print(f"build_backlog.py failed: {exc}", file=sys.stderr)
        sys.exit(2)
