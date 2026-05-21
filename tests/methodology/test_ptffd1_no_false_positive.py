"""PTFFD-1 (slice-037) AC3: zero false positives on the real repo corpus.

The decisive real-artifact guard (BC-PROJ-4 class, `_index.md:54`): the
function-level layer must not false-positive on the LIVE shippability catalog
or on real archived-brief prose `Test function` values. Scoped deliberately:
the live `architecture/shippability.md` (the operative surface) must be
function-level-clean, and the B2 discriminator must reject EVERY prose
`Test function` value harvested from the archived brief corpus (including
slice-034's named `(full existing module — non-regression)` row) so the
function layer degrades to FILE-level-only rather than false-flagging.

Rule reference: PTFFD-1 (slice-037; AC3; B2 zero-false-positive linchpin).
"""
import re

from tests.methodology.conftest import REPO_ROOT, _resolve_slice_dir
from tools._pyfn import is_checkable_function_name
from tools.shippability_path_audit import audit_catalog_file


def test_real_shippability_and_full_tf1_corpus_clean_under_func_level():
    """The LIVE architecture/shippability.md is function-level-clean:
    every `tests/...py::fn` selector across all real rows resolves to an
    existing file AND an existing function. Zero violations, zero
    skip-notes (no unparseable cited test files).

    Rule reference: PTFFD-1 (AC3).
    """
    catalog = REPO_ROOT / "architecture" / "shippability.md"
    result = audit_catalog_file(catalog)
    assert result.violations == [], (
        "live shippability.md must be function-level-clean; got "
        f"{[(v.kind, v.row, v.token) for v in result.violations]}"
    )
    assert result.skip_notes == [], (
        f"no cited test file should be unparseable; got {result.skip_notes}"
    )
    assert result.tokens_checked > 0, "sanity: tokens were actually checked"


def _archived_brief_test_function_cells() -> list[str]:
    """Every `Test function` cell value across all archived + active
    mission-brief TF-1-plan tables (5-col `| AC | type | path | fn | st |`).
    """
    vals: list[str] = []
    slices_root = REPO_ROOT / "architecture" / "slices"
    for brief in slices_root.rglob("mission-brief.md"):
        for line in brief.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s.startswith("|"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) == 5 and cells[0].lower() not in {"ac", "----"}:
                # 4th cell is Test function; skip separator rows
                if set(cells[0]) <= set("-: "):
                    continue
                vals.append(cells[3])
    return vals


def test_slice034_prose_test_function_is_not_false_positive():
    """slice-034's real archived TF-1 row carries the prose
    `(full existing module — non-regression)` in the Test function
    column. The B2 discriminator MUST reject it (not checkable) so the
    function layer degrades to FILE-level-only — no false-positive.

    Rule reference: PTFFD-1 (AC3; B2 named regression fixture).
    """
    slice034 = _resolve_slice_dir(34) / "mission-brief.md"
    assert slice034.is_file(), f"expected archived slice-034 brief at {slice034}"
    text = slice034.read_text(encoding="utf-8")
    assert "(full existing module" in text, (
        "regression anchor missing — slice-034's prose Test function row "
        "was expected in the archived brief"
    )
    assert not is_checkable_function_name("(full existing module — non-regression)")


def test_archived_corpus_prose_function_values_all_rejected_by_discriminator():
    """Corpus-validated B2: every NON-identifier `Test function` value in
    the real archived/active brief corpus is rejected by the discriminator
    (so the function layer never false-positives on real prose), while
    plain identifiers are accepted.

    Rule reference: PTFFD-1 (AC3; B2 corpus validation).
    """
    ident_re = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\[.*\])?")
    cells = _archived_brief_test_function_cells()
    assert cells, "sanity: harvested at least one Test function cell"
    for val in cells:
        looks_like_identifier = ident_re.fullmatch(val.strip()) is not None
        checkable = is_checkable_function_name(val)
        if looks_like_identifier:
            assert checkable, f"real identifier wrongly rejected: {val!r}"
        else:
            assert not checkable, (
                f"prose value wrongly accepted (would false-positive): {val!r}"
            )
