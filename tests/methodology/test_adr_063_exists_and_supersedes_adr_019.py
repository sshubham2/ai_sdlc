"""Pin ADR-063 frontmatter `supersedes: ADR-019` + ADR-019 append-only invariant.

Per slice-066 /critique AC #4 + Builder draft ACCEPTED-FIXED for B1 (ADR identifier corrected
from rev-1's incorrect `ADR-021` — which is utf8-stdout-1, unrelated — to the actual BRANCH-1
home `ADR-019`). ADR-063 is the **N=2 application of the slice-022 [[ADR-020]] partial-supersession
encoding pattern** (single `supersedes:` frontmatter slot + body-level scope enumeration;
ADR-019 stays unmodified per append-only). ADR-020 was the N=1 application (partial-superseded
ADR-019 sub-mode (b)). ADR-063 supersedes sub-mode (a) build-time branch-create + EXTENDS
sub-mode (c) audit-time refusal in place via 4 new violation kinds; the append-only rule holds
across N=2 supersessions.

Rule reference: BRANCH-2 (slice-066; ADR-063; partial-supersedes ADR-019; methodology v0.68.0).
"""
from __future__ import annotations

from pathlib import Path

import pytest
from tools._vault_paths import VAULT_ROOT

REPO_ROOT = Path(__file__).resolve().parents[2]
ADR_063_PATH = REPO_ROOT / VAULT_ROOT / "decisions" / "ADR-063-worktree-per-slice.md"
ADR_019_PATH = REPO_ROOT / VAULT_ROOT / "decisions" / "ADR-019-branch-per-slice-workflow.md"
ADR_021_PATH = REPO_ROOT / VAULT_ROOT / "decisions" / "ADR-021-utf8-stdout-1-default-utf8-stdout-in-audit-tools.md"


def _parse_frontmatter(path: Path) -> dict[str, str]:
    """Parse the YAML-ish frontmatter at the head of an ADR file.

    Returns a dict of key -> value strings. Empty dict if no frontmatter block.
    Hand-rolled parser (no PyYAML dep) — handles the simple `key: value` shape
    used by this repo's ADRs.
    """
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}
    end = content.find("\n---", 4)
    if end < 0:
        return {}
    block = content[4:end]
    result: dict[str, str] = {}
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        result[key.strip()] = value.strip()
    return result


def test_adr_063_present_with_supersedes_adr_019_frontmatter() -> None:
    """ADR-063 frontmatter must declare `supersedes: ADR-019` (NOT ADR-021).

    Defect class: rev-1 mission-brief + design.md + ADR-063 all conflated ADR-021 (utf8-stdout-1)
    with ADR-019 (BRANCH-1). Shipping ADR-063 with `supersedes: ADR-021` would have asserted
    append-only on the wrong ADR + made a structurally meaningless supersession claim against
    an unrelated active ADR. /critique B1 ACCEPTED-FIXED applied the global rename;
    /critique-review M-add-1 ACCEPTED-FIXED closed the residual L152 rename gap.

    Per slice-066 /critique B1 + slice-022 partial-supersession encoding pattern (N=2 application).
    """
    assert ADR_063_PATH.exists(), (
        f"ADR-063 must exist at {ADR_063_PATH} (created by /design-slice for slice-066)"
    )
    fm = _parse_frontmatter(ADR_063_PATH)
    assert fm.get("id") == "ADR-063", (
        f"ADR-063 frontmatter `id` must be `ADR-063`; got: {fm.get('id')!r}"
    )
    assert fm.get("supersedes") == "ADR-019", (
        f"ADR-063 frontmatter must declare `supersedes: ADR-019` (NOT `ADR-021` — that's utf8-stdout-1, "
        f"unrelated); got: supersedes={fm.get('supersedes')!r}. Per slice-066 /critique B1 ACCEPTED-FIXED "
        f"+ slice-022 [[ADR-020]] partial-supersession encoding pattern N=2 application."
    )
    # Anti-anchor: the body MUST acknowledge ADR-019 is already-once-superseded by ADR-020.
    body = ADR_063_PATH.read_text(encoding="utf-8")
    assert "ADR-020" in body, (
        "ADR-063 body must reference ADR-020 (the N=1 partial supersession of ADR-019; "
        "ADR-063 is N=2 — body must enumerate the lineage per /critique-review M4 ACCEPTED-FIXED)"
    )
    assert "N=2" in body or "second partial" in body.lower(), (
        "ADR-063 §Scope of supersession opening must note this is the N=2 application of the "
        "slice-022 partial-supersession encoding pattern (per /critique m2 ACCEPTED-FIXED)"
    )


def test_adr_019_unmodified_per_append_only_rule() -> None:
    """ADR-019 must remain append-only: no `superseded-by:` field; supersession is one-directional.

    Defect class: the ADR family convention (per slice-022 + CLAUDE.md "ADRs are append-only —
    supersede via a new ADR with `supersedes: ADR-NNN`, never edit in place") REQUIRES that
    supersession be encoded ONLY at the successor ADR's `supersedes:` frontmatter slot. Adding
    a `superseded-by:` field to ADR-019 would violate append-only AND isn't supported by the
    ADR family convention.

    This test holds across N≥2 partial supersessions: ADR-020 supersedes ADR-019 sub-mode (b);
    ADR-063 supersedes sub-mode (a). ADR-019 itself is never edited.

    Per slice-022 ADR-020 partial-supersession encoding precedent + CLAUDE.md vault discipline.
    """
    assert ADR_019_PATH.exists(), (
        f"ADR-019 must exist at {ADR_019_PATH} (the BRANCH-1 mint; slice-021)"
    )
    fm = _parse_frontmatter(ADR_019_PATH)
    assert "superseded-by" not in fm, (
        f"ADR-019 must NOT carry a `superseded-by:` field per append-only ADR family convention "
        f"(slice-022 ADR-020 partial-supersession encoding precedent — supersession is encoded "
        f"ONLY at the successor ADR's `supersedes:` frontmatter slot, never reverse-linked from "
        f"the superseded ADR). Got frontmatter keys: {sorted(fm.keys())}"
    )
    # ADR-019's frontmatter `supersedes` field must remain `null` (it doesn't supersede anything).
    # (Reading the ADR-019 frontmatter in this repo shows `supersedes: null`.)
    supersedes_value = fm.get("supersedes", "null")
    assert supersedes_value in ("null", ""), (
        f"ADR-019 `supersedes` field must remain `null` (slice-021 mint; ADR-019 doesn't supersede "
        f"any prior ADR); got: {supersedes_value!r}"
    )


def test_adr_021_is_utf8_stdout_not_branch_per_slice() -> None:
    """ADR-021 is `utf8-stdout-1` (slice-023), NOT BRANCH-1 — anti-anchor for /critique B1.

    Defect class: rev-1 mission-brief / design / ADR-063 conflated ADR-021 with BRANCH-1.
    This anti-anchor test asserts the actual ADR-021 identity to make the conflation defect
    permanently catchable: any future drift that re-introduces `ADR-021` as BRANCH-1 would
    fail this anchor.

    Per slice-066 /critique B1 ACCEPTED-FIXED + /critique-review M-add-1 residual-rename closure.
    """
    assert ADR_021_PATH.exists(), (
        f"ADR-021 must exist at {ADR_021_PATH} (the utf8-stdout-1 mint; slice-023)"
    )
    fm = _parse_frontmatter(ADR_021_PATH)
    title = fm.get("title", "")
    assert "UTF8-STDOUT-1" in title or "utf-8 stdout" in title.lower() or "utf8" in title.lower(), (
        f"ADR-021 title must reference UTF8-STDOUT-1 / utf-8 stdout (slice-023; methodology v0.37.0); "
        f"got: title={title!r}. If this fails, BRANCH-1 may have been re-conflated with ADR-021 — "
        f"per slice-066 /critique B1 ACCEPTED-FIXED anti-anchor."
    )
