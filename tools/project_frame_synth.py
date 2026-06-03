"""PFS-1 project-frame synthesizer.

Per **PFS-1** (`methodology-changelog.md` v0.78.0; slice-088; [[ADR-080]];
mints a new rule on the review-context axis). Emits an **ephemeral**,
**deterministic**, **tight** project-frame to **stdout** so `/design-slice`
(shift-left, Step 0.5) and both Critic layers (`/critique`,
`/critique-review`) review a slice against the project's *deliberate forward
direction* — not only its static current artifacts. The frame is the input
the already-shipped `agents/critique.md` Dim-7 strategic-direction probe
consumes.

Three required sections, synthesized (selected + compressed + ranked), NOT
concatenated:

  - **Identity**  — what this project is (`concept.md` "What it does" +
                    mode from `triage.md`).
  - **Trajectory**— where it is deliberately heading: deduped active rule
                    FAMILIES (recent `methodology-changelog.md` entry titles),
                    pending `slice-queue.md` candidate names, open
                    `risk-register.md` entries score-ranked with score shown.
  - **Impact**    — this slice's name + one-line intent + whether `design.md`
                    exists yet (degraded to mission-brief-only at Step 0.5).

Design decisions (ADR-080):
  - A **deterministic tool**, NOT an LLM `/frame` skill — judgment of
    direction-fit stays with the Critic; the tool only assembles evidence.
  - **Ephemeral stdout-only** — nothing tracked is written; regenerated each
    invocation, so it cannot drift.
  - cp1252 stdout safety via `_stdout.reconfigure_stdout_utf8()`
    (UTF8-STDOUT-1) — em-dash-laden extracted text emits safely as UTF-8;
    NO ASCII-fold (design deviation 2026-05-31, user-approved — the
    codebase-standard mechanism, consistent with all sibling tools).

Exit codes (binary contract, mirrors `slice_queue_writer` / NAW-1):
  0  frame emitted (clean OR degraded-with-stderr-WARN on a missing source)
  2  usage error (missing/invalid required `--slice-dir`)
  NEVER 1 — frame-synth failure is not a slice-regression class; the frame is
  advisory context to /design-slice + /critique, never a gate.

Usage::

    # Library (preferred; called from skill prose via Bash capture)
    from tools.project_frame_synth import synthesize_frame
    frame = synthesize_frame(Path("."), VAULT_ROOT / "slices" / "slice-NNN-x")

    # CLI
    python -m tools.project_frame_synth --repo-root . \\
        --slice-dir architecture/slices/slice-NNN-x

Rule reference: PFS-1 (slice-088; ADR-080).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from tools import _stdout
from tools._vault_paths import VAULT_ROOT  # slice-106: route vault reads through the seam

_MAX_FRAME_LINES = 40

_ATTACK_LENS = (
    "ATTACK-LENS -- use this to find where the slice fights the project's "
    "direction; do NOT nod along"
)
_TRUNCATION_MARKER = "... (frame truncated to budget)"
_NONE = "_(none)_"

# A rule-id entry-title line, e.g. ``**PFS-1 — project-frame ...``,
# ``**TRI-RESOLVE-1 — ...``, or a LETTER-SUFFIXED id ``**PCR-2b — ...`` /
# ``**PCR-2a — ...`` (the codebase actively uses these — changelog v0.77.0/v0.74.0).
# Each segment tolerates a single trailing lowercase letter (`[a-z]?`); the `\b`
# anchor is intentionally OMITTED — with it, the word-boundary between `2` and `b`
# in `PCR-2b` failed, collapsing the capture to `PCR` (no `-<digit>`) so the entry
# was silently dropped from the family scan (slice-088 /code-review M1).
_RULE_TITLE_RE = re.compile(r"^\*\*([A-Z][A-Z0-9]*(?:-[A-Z0-9]+[a-z]?)*)")
# Family = the rule id with its trailing numeric-bearing segment stripped:
# PFS-1 -> PFS, PCR-2b -> PCR, BC-PROJ-9 -> BC-PROJ, TRI-RESOLVE-1 -> TRI-RESOLVE.
_FAMILY_RE = re.compile(r"^([A-Z][A-Z-]*?)-\d")

_MAX_FAMILIES = 6
_MAX_RISKS = 3
_MAX_CANDIDATES = 6

# Bold `-<digit>` tokens that are NOT methodology rule families: decision
# records (ADR-NNN), risk ids (R-N), and diagnose candidates (SC-NNN).
_NON_RULE_FAMILIES = {"ADR", "R", "SC"}


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _rule_family(rule_id: str) -> str:
    m = _FAMILY_RE.match(rule_id)
    return m.group(1) if m else rule_id


def _first_sentence(text: str) -> str:
    text = " ".join(text.split())
    m = re.search(r"^(.*?\.)(?:\s|$)", text)
    return (m.group(1) if m else text).strip()


def _section_body(text: str, heading: str) -> str:
    """Return the body between a `## <heading>` line and the next `## ` line."""
    pat = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    m = pat.search(text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"^##\s", rest, re.MULTILINE)
    return rest[: nxt.start()] if nxt else rest


def _identity(repo_root: Path, warn) -> list[str]:
    concept = _read(repo_root / VAULT_ROOT / "concept.md")
    triage = _read(repo_root / VAULT_ROOT / "triage.md")
    one_liner = "(concept.md unavailable)"
    if concept:
        body = _section_body(concept, "What it does").strip()
        if body:
            one_liner = _first_sentence(body)
    else:
        warn("concept.md missing")
    mode = "?"
    if triage:
        fm = re.search(r"^mode:\s*(\w+)", triage, re.MULTILINE)
        if fm:
            mode = fm.group(1).capitalize()
        else:
            hm = re.search(r"^##\s*Mode:\s*(\w+)", triage, re.MULTILINE)
            if hm:
                mode = hm.group(1).capitalize()
    else:
        warn("triage.md missing")
    return ["## Identity", f"{one_liner} (Mode: {mode})"]


_VERSION_HEADER_RE = re.compile(r"^##\s+v\d")


def _active_families(repo_root: Path, warn) -> list[str]:
    """Deduped active rule FAMILIES from the recent changelog.

    Synthesis, not concatenation: takes the FIRST real rule-id entry-title per
    `## vN.N.N` version block only (ignoring the many non-title bold lines in
    each entry body, e.g. `**Mechanism**`, `**SKILL.md ...`, `**ADR-... `), maps
    each to its family, dedups preserving recency order, caps at _MAX_FAMILIES.
    A bold token is a rule-id only if it has a `-<digit>` component (`_FAMILY_RE`
    matches) — this filters body words like SKILL / SOFT / Mechanism."""
    changelog = _read(repo_root / "methodology-changelog.md")
    if not changelog:
        warn("methodology-changelog.md missing")
        return []
    lines = changelog.splitlines()
    n = len(lines)
    families: list[str] = []
    i = 0
    while i < n and len(families) < _MAX_FAMILIES:
        if not _VERSION_HEADER_RE.match(lines[i]):
            i += 1
            continue
        # Scan this entry for its first valid rule-id title line.
        j = i + 1
        while j < n and not _VERSION_HEADER_RE.match(lines[j]):
            m = _RULE_TITLE_RE.match(lines[j].strip())
            if m and _FAMILY_RE.match(m.group(1)):
                fam = _rule_family(m.group(1))
                if fam in _NON_RULE_FAMILIES:
                    break  # decision/risk/candidate ref, not a rule — skip entry
                if fam not in families:
                    families.append(fam)
                break  # only the entry title — not the body
            j += 1
        i = j
    return families


def _pending_candidates(repo_root: Path, warn) -> list[str]:
    queue = _read(repo_root / VAULT_ROOT / "slice-queue.md")
    if not queue:
        warn("slice-queue.md missing")  # m3: match the sibling sections' degrade-WARN
        return []
    names = re.findall(r"^###\s+([A-Za-z0-9][\w-]*)", queue, re.MULTILINE)
    return names[:_MAX_CANDIDATES]


def _open_risks(repo_root: Path, warn) -> list[str]:
    path = repo_root / VAULT_ROOT / "risk-register.md"
    text = _read(path)
    if not text:
        warn("risk-register.md missing")
        return []
    try:
        # m2 (acknowledged, intentional reuse per design.md): couples to the
        # private `risk_register_audit._parse_risks` + the `Risk` dataclass fields
        # (risk_id/title/score/status). The broad `except` below degrades the risk
        # line to _(none)_ + WARN if that private API ever changes, never crashing;
        # `test_open_risks_uses_parse_risks_api` pins the contract so a refactor
        # trips a red test rather than silently emptying the section.
        from tools import risk_register_audit as rra

        risks, _violations = rra._parse_risks(text, str(path))
    except Exception as exc:  # noqa: BLE001 - degrade, never crash the frame
        warn(f"risk-register parse failed ({exc})")
        return []
    open_risks = [r for r in risks if r.status == "open"]
    open_risks.sort(key=lambda r: (-r.score, r.risk_id))
    out = []
    for r in open_risks[:_MAX_RISKS]:
        title = r.title if len(r.title) <= 48 else r.title[:45] + "..."
        out.append(f"{r.risk_id} (score {r.score}) {title}")
    return out


def _trajectory(repo_root: Path, warn) -> list[str]:
    families = _active_families(repo_root, warn)
    candidates = _pending_candidates(repo_root, warn)
    risks = _open_risks(repo_root, warn)
    return [
        "## Trajectory",
        "- Active rule families: " + (", ".join(families) if families else _NONE),
        "- Pending slice-queue: " + (", ".join(candidates) if candidates else _NONE),
        "- Open risks (by score): " + ("; ".join(risks) if risks else _NONE),
    ]


def _impact(slice_dir: Path, warn) -> list[str]:
    name = slice_dir.name
    brief = _read(slice_dir / "mission-brief.md")
    intent = "(mission-brief.md unavailable)"
    if brief:
        body = _section_body(brief, "Intent").strip()
        if body:
            intent = _first_sentence(body)
    else:
        warn("mission-brief.md missing")
    design_exists = (slice_dir / "design.md").is_file()
    design_line = (
        "present" if design_exists else "mission-brief-only (design.md not yet written)"
    )
    return [
        "## Impact",
        f"- Slice: {name}",
        f"- Intent: {intent}",
        f"- Design: {design_line}",
    ]


def synthesize_frame(
    repo_root: Path, slice_dir: Path, max_lines: int = _MAX_FRAME_LINES
) -> str:
    """Synthesize the ephemeral project-frame as a markdown string.

    Deterministic: no wall-clock, no randomness, stable ordering. Degrades
    section-by-section (with a stderr WARN) on any missing source rather than
    raising. Truncates to `max_lines` with a marker."""
    warnings: list[str] = []

    def warn(msg: str) -> None:
        warnings.append(msg)

    repo_root = Path(repo_root)
    slice_dir = Path(slice_dir)

    lines: list[str] = [_ATTACK_LENS, ""]
    lines += _identity(repo_root, warn) + [""]
    lines += _trajectory(repo_root, warn) + [""]
    lines += _impact(slice_dir, warn)

    if warnings:
        # WARN to stderr (visibility per the error model); never to the frame.
        print(
            "WARN: project-frame degraded — " + "; ".join(warnings),
            file=sys.stderr,
        )

    # Clamp a degenerate budget (slice-088 /code-review M2): max_lines < 1 would
    # make `max_lines - 1` a negative slice index, dropping only the tail instead
    # of truncating — a 0/negative budget silently emitted a near-full frame,
    # the opposite of the tight-frame must-not-defer. A budget of 1 -> marker only.
    if max_lines < 1:
        max_lines = 1
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1] + [_TRUNCATION_MARKER]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="project_frame_synth",
        description="Emit the ephemeral PFS-1 project-frame to stdout.",
    )
    parser.add_argument("--repo-root", default=".", help="repo root (default: .)")
    parser.add_argument(
        "--slice-dir",
        required=True,
        help="active slice folder, e.g. architecture/slices/slice-NNN-<name>",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=_MAX_FRAME_LINES,
        help=f"line budget (default: {_MAX_FRAME_LINES})",
    )
    args = parser.parse_args(argv)  # argparse exits 2 on missing --slice-dir
    if args.max_lines < 1:
        parser.error("--max-lines must be >= 1")  # exit 2 (usage); never a budget breach

    frame = synthesize_frame(
        Path(args.repo_root), Path(args.slice_dir), max_lines=args.max_lines
    )
    print(frame)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
