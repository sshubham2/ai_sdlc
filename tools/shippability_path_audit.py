"""Shippability-catalog test-path existence audit (PTFCD-1, sub-mode (b)).

Parses `architecture/shippability.md`, and for each catalog row extracts the
test-file path tokens cited in the row's `Command` cell — specifically the
`tests/<...>.py` tokens that appear AFTER the `pytest` keyword (the row's
critical-path pytest invocation). For each token: strip surrounding markdown
backticks, split on `::` to drop the pytest selector, resolve repo-root
relative, and flag any token whose file does not exist on disk.

Per PTFCD-1 (methodology-changelog.md v0.39.0). The rule's purpose: the
Critic-stack reviews shippability `Command` cells statically for name
harmonization and cross-file consistency, but no static surface verifies
"does the cited test file exist when /validate-slice Step 5.5 runs this
command". slice-024 cited a non-existent `tests/methodology/
test_shippability_catalog.py` at 3 sibling sites; it survived 19 Critic-stack
findings + both Critic layers and died only at real-command execution. This
audit, wired as a /validate-slice Step 5.5 pre-catalog gate, catches the
phantom citation as ONE clear violation before the catalog runner produces N
confusing per-row "file not found" FAILs.

Token-extraction predicate (M2 — pinned, not broad): only `tests/\\S+\\.py`
tokens appearing after the literal `pytest` keyword in the Command cell are
treated as test-file paths. The interpreter path (`*.exe`), `-m`, `pytest`,
`-q`, `--no-header`, and any non-`tests/`-rooted token are NOT treated as
test paths. Markdown backticks are stripped before resolution (slice-024
validation.md footgun: an un-stripped run produced 23 spurious FAILs).

Usage:
    python -m tools.shippability_path_audit architecture/shippability.md
    python -m tools.shippability_path_audit architecture/shippability.md --json

Exit codes:
    0  clean (or empty / zero-row catalog)
    1  one or more phantom test-path citations
    2  usage error (catalog file missing or unreadable)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tools import _pyfn, _stdout

# `tests/<...>.py` token (repo-relative test path). Backticks/quotes are
# stripped per-token before this is applied to the post-`pytest` segment.
_TEST_PATH_RE = re.compile(r"tests/\S+?\.py")


@dataclass(frozen=True)
class PhantomCitation:
    row: str           # the catalog row number cell, e.g. "24"
    token: str         # the offending test-path token as written
    resolved: str      # the absolute path that was tried
    line: int          # 1-based line in shippability.md
    # PTFFD-1 (slice-037): "missing-test-file" (pre-existing FILE-level
    # PTFCD-1 behavior — default, m1 legacy-direction pinned) |
    # "missing-test-function" (NEW function-level layer). Additive field;
    # `to_dict()` retains every prior key (additive-superset contract).
    kind: str = "missing-test-file"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    rows_scanned: int = 0
    tokens_checked: int = 0
    violations: list[PhantomCitation] = field(default_factory=list)
    # PTFFD-1 (slice-037; ADR-037 M2): visible skip-notes for tokens whose
    # cited file could not be AST-parsed — NO violation, but not silent.
    skip_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rows_scanned": self.rows_scanned,
            "tokens_checked": self.tokens_checked,
            "violations": [v.to_dict() for v in self.violations],
            "skip_notes": list(self.skip_notes),
            "summary": {
                "violation_count": len(self.violations),
            },
        }


def _find_repo_root(start: Path) -> Path:
    """Walk up from `start` for a `.git` dir or `VERSION` file sentinel."""
    cur = start.resolve()
    if cur.is_file():
        cur = cur.parent
    for cand in [cur, *cur.parents]:
        if (cand / ".git").exists() or (cand / "VERSION").exists():
            return cand
    return start.resolve().parent


def _parse_table_cells(line: str) -> list[str]:
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [cell.strip() for cell in inner.split("|")]


def _is_separator_row(line: str) -> bool:
    cells = _parse_table_cells(line)
    if not cells:
        return False
    for cell in cells:
        stripped = cell.replace(" ", "")
        if not stripped or not set(stripped) <= set("-:") or "-" not in stripped:
            return False
    return True


# A pytest `::`-selector immediately following a matched test path, e.g.
# `::TestClass::test_method` or `::test_fn[case]`. Bounded by whitespace /
# backtick / quote (the SCMD-1 Machine-cmd cell delimiters).
_SELECTOR_RE = re.compile(r"""\A(::[^\s`"']+)""")


def _extract_test_tokens(command_cell: str) -> list[tuple[str, str | None]]:
    """Return `(file_token, raw_selector|None)` pairs after the `pytest` kw.

    M2 (PTFCD-1): scope to the post-`pytest` segment so the interpreter path
    and `-m pytest` prefix are never mistaken for test paths. PTFFD-1
    (slice-037): the `::`-selector that PTFCD-1 discarded is now CAPTURED (not
    split away) so the function-level layer can verify the cited test
    function exists. The file token itself is still backtick/quote-stripped
    and `::`-free (the `_TEST_PATH_RE` `\\.py` anchor already excludes the
    selector from the match; the selector is read from the trailing segment).
    """
    idx = command_cell.find("pytest")
    if idx == -1:
        return []
    segment = command_cell[idx + len("pytest"):]
    pairs: list[tuple[str, str | None]] = []
    for m in _TEST_PATH_RE.finditer(segment):
        tok = m.group(0).strip("`").strip().strip('"').strip("'")
        tok = tok.split("::", 1)[0].strip()
        if not tok:
            continue
        sel_match = _SELECTOR_RE.match(segment[m.end():])
        selector = sel_match.group(1) if sel_match else None
        pairs.append((tok, selector))
    return pairs


def audit_catalog_file(catalog_path: Path) -> AuditResult:
    """Audit architecture/shippability.md against PTFCD-1 sub-mode (b)."""
    result = AuditResult()
    text = catalog_path.read_text(encoding="utf-8")
    repo_root = _find_repo_root(catalog_path)
    lines = text.splitlines()

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if _is_separator_row(line):
            continue
        cells = _parse_table_cells(line)
        # Catalog schema (slice-031 / SCMD-1, ADR-031): the machine-stable
        # command is the 6th column (index 5):
        #   | # | Slice | Critical path | Command | Runtime | Machine-cmd |
        # PTFCD-1 authoritatively reads `Machine-cmd`. If a data row is
        # missing it (a SCMD-1 violation that the SCMD-1 pre-catalog gate
        # surfaces), do NOT silently `continue` — that would also disable
        # phantom-path detection for the row (B3). Fall back to the legacy
        # Command cell (index 3) so PTFCD-1 coverage never silently drops.
        if len(cells) < 4:
            continue
        row_num = cells[0]
        if row_num.lower() in {"#", ""} or not any(ch.isdigit() for ch in row_num):
            continue  # header or non-data row
        command_cell = cells[5] if len(cells) > 5 else cells[3]
        result.rows_scanned += 1
        for tok, selector in _extract_test_tokens(command_cell):
            result.tokens_checked += 1
            candidate = Path(tok)
            if not candidate.is_absolute():
                candidate = repo_root / candidate
            if not candidate.exists():
                result.violations.append(PhantomCitation(
                    row=row_num,
                    token=tok,
                    resolved=str(candidate),
                    line=i,
                    kind="missing-test-file",
                ))
                continue

            # PTFFD-1 (slice-037; ADR-038): FILE exists — if the citation
            # carries a `::`-selector, additionally verify the cited test
            # FUNCTION (terminal `::`-segment, `[param-id]` stripped) exists.
            if selector is None:
                continue
            fn_name = _pyfn.selector_terminal_name(selector)
            if fn_name is None:
                continue  # no checkable terminal name → FILE-level-only
            verdict = _pyfn.function_defined_in_file(candidate, fn_name)
            if verdict is False:
                result.violations.append(PhantomCitation(
                    row=row_num,
                    token=f"{tok}{selector}",
                    resolved=str(candidate),
                    line=i,
                    kind="missing-test-function",
                ))
            elif verdict is None:
                result.skip_notes.append(
                    f"shippability.md:{i} row {row_num}: function-check "
                    f"skipped (file unparseable) for '{fn_name}' in "
                    f"'{candidate}'."
                )
    return result


def _format_human(result: AuditResult) -> str:
    # PTFFD-1 (slice-037; ADR-037 M2): unparseable cited files are skipped
    # WITH a visible note — never silent. Rendered on clean + violation paths.
    skip_block = ""
    if result.skip_notes:
        skip_block = (
            f"\n{len(result.skip_notes)} function-check skip-note(s) "
            f"(PTFFD-1; no violation — ADR-037 skip-with-note):\n"
            + "".join(f"  - {n}\n" for n in result.skip_notes)
        )

    if not result.violations:
        return (
            f"Shippability path audit (PTFCD-1/PTFFD-1): clean. "
            f"{result.rows_scanned} row(s), "
            f"{result.tokens_checked} test-path token(s) — all files and "
            f"cited functions exist.\n"
            + skip_block
        )
    out = [
        f"{len(result.violations)} phantom test-path/function citation(s) "
        f"in shippability.md (PTFCD-1/PTFFD-1 sub-mode (b)):\n\n"
    ]
    for v in result.violations:
        if v.kind == "missing-test-function":
            detail = (
                f"resolves to existing file '{v.resolved}', but the cited "
                f"test function does not exist in it (PTFFD-1)."
            )
        else:
            detail = (
                f"resolves to '{v.resolved}', which does not exist on disk "
                f"(PTFCD-1)."
            )
        out.append(
            f"  [Important] shippability.md:{v.line} row {v.row} "
            f"({v.kind}) — token '{v.token}'\n"
            f"    {detail}\n\n"
        )
    out.append(skip_block)
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="shippability_path_audit",
        description="PTFCD-1 shippability-catalog test-path existence audit",
    )
    parser.add_argument(
        "catalog", type=Path,
        help="Path to architecture/shippability.md",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args(argv)

    catalog_path: Path = args.catalog
    if not catalog_path.is_file():
        sys.stderr.write(
            f"shippability_path_audit: catalog file not found or not a file: "
            f"{catalog_path}\n"
        )
        return 2

    try:
        result = audit_catalog_file(catalog_path)
    except OSError as exc:
        sys.stderr.write(f"shippability_path_audit: cannot read catalog: {exc}\n")
        return 2

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
