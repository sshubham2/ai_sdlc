"""Layered /validate-slice safety checks (VAL-1).

Adds two defensive layers to the per-slice validation flow:

Layer A — Credential scan (regex-based)
    Walks --changed-files for known secret patterns: AWS access keys,
    GitHub PATs (classic + fine-grained + bot tokens), Slack tokens,
    JWTs, PEM private keys, Anthropic / OpenAI API keys, generic
    `api_key = "..."` literals. Each detected secret is a Critical
    finding (cannot defer). An optional allowlist file
    (`architecture/.secrets-allowlist`) holds regex patterns; matches
    that satisfy any allowlist pattern are silently suppressed.

Layer B — Dependency hallucination check (Python only in v1)
    For every Python import in --changed-files, verifies the top-level
    package is one of:
      - Standard library (sys.stdlib_module_names, Python 3.10+)
      - Declared in pyproject.toml [project.dependencies] or
        [tool.poetry.dependencies] or [project.optional-dependencies.*]
      - Declared in pyproject.toml [tool.setuptools] packages = [...]
        (the explicit-list form; auto-discovery `find` is v2)
      - Declared in requirements.txt (legacy projects)
      - A known alias of a declared package (e.g. import yaml when
        pyyaml is declared)
      - Listed via --imports-allowlist (repeatable; for non-pip-
        installed conventional roots like 'tests', 'scripts', 'docs')
    Otherwise emits an Important finding (`hallucinated-import`). AI
    implementations have a chronic problem with importing packages
    that don't exist; the check catches them at validate time.

Per VAL-1 (methodology-changelog.md v0.14.0).

NFR-1 carry-over: slices whose mission-brief.md mtime predates the
release date `_VAL_1_RELEASE_DATE` are exempt automatically.

Usage:
    python -m tools.validate_slice_layers --slice <slice-folder> \\
        --changed-files <files...>
    python -m tools.validate_slice_layers --slice <slice-folder> \\
        --changed-files <files...> --skip-secrets
    python -m tools.validate_slice_layers --slice <slice-folder> \\
        --changed-files <files...> --skip-deps
    python -m tools.validate_slice_layers --slice <slice-folder> \\
        --changed-files <files...> --json
    python -m tools.validate_slice_layers --slice <slice-folder> \\
        --changed-files <files...> --secrets-allowlist <path>
    python -m tools.validate_slice_layers --slice <slice-folder> \\
        --changed-files <files...> --pyproject <path> --requirements <path>
    python -m tools.validate_slice_layers --slice <slice-folder> \\
        --changed-files <files...> --imports-allowlist tests \\
        --imports-allowlist scripts

Exit codes:
    0  clean (or carry-over exempt; or no changed files)
    1  findings (Critical or Important)
    2  usage error
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import sys as _sys_module
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from tools import _stdout

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore

# Date this rule shipped. NFR-1 carry-over.
_VAL_1_RELEASE_DATE: date = date(2026, 5, 6)

# Standard library module names — frozenset(stdlib) in Python 3.10+.
_STDLIB: frozenset[str] = getattr(_sys_module, "stdlib_module_names", frozenset())

# --- Layer A: secret patterns ---

_SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "aws-access-key": re.compile(r"\b(AKIA[0-9A-Z]{16})\b"),
    "github-token-classic": re.compile(r"\b(ghp_[A-Za-z0-9]{36,255})\b"),
    "github-token-fine": re.compile(r"\b(github_pat_[A-Za-z0-9_]{60,255})\b"),
    # `p` excluded — it's covered by github-token-classic (ghp_...)
    "github-token-other": re.compile(r"\b(gh[orsu]_[A-Za-z0-9]{36,255})\b"),
    "slack-token": re.compile(r"\b(xox[baprs]-[A-Za-z0-9-]{10,})\b"),
    "private-key": re.compile(
        r"(-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----)"
    ),
    "anthropic-key": re.compile(r"\b(sk-ant-[A-Za-z0-9_-]{40,})\b"),
    "openai-key": re.compile(
        r"\b(sk-(?:proj-)?[A-Za-z0-9_-]{20,}T3BlbkFJ[A-Za-z0-9_-]{20,})\b"
    ),
    "jwt": re.compile(
        r"\b(eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})\b"
    ),
    "generic-api-key": re.compile(
        r"(?i)(?:api[_-]?key|apikey|api[_-]?token|access[_-]?token|"
        r"secret[_-]?key|password)\s*[:=]\s*"
        r"['\"]([A-Za-z0-9_+/=\-]{20,})['\"]"
    ),
}

# --- Layer B: known aliases (import name -> package name as in pyproject) ---

_KNOWN_ALIASES: dict[str, str] = {
    "yaml": "pyyaml",
    "PIL": "pillow",
    "bs4": "beautifulsoup4",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "skimage": "scikit-image",
    "magic": "python-magic",
    "dateutil": "python-dateutil",
    "Crypto": "pycryptodome",
    "OpenSSL": "pyopenssl",
    "git": "gitpython",
    "jwt": "pyjwt",
    "lxml": "lxml",
    "pkg_resources": "setuptools",
    "tree_sitter_typescript": "tree-sitter-typescript",
    "tree_sitter_go": "tree-sitter-go",
}


@dataclass(frozen=True)
class SecretFinding:
    path: str
    line: int
    pattern_name: str
    snippet: str
    kind: str       # "secret-detected"
    severity: str   # "Critical"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ImportFinding:
    path: str
    line: int
    import_name: str
    kind: str       # "hallucinated-import"
    severity: str   # "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LayersResult:
    secret_findings: list[SecretFinding] = field(default_factory=list)
    import_findings: list[ImportFinding] = field(default_factory=list)
    suppressed_secrets: int = 0
    declared_deps: list[str] = field(default_factory=list)
    carry_over_exempt: bool = False

    def to_dict(self) -> dict:
        return {
            "secret_findings": [f.to_dict() for f in self.secret_findings],
            "import_findings": [f.to_dict() for f in self.import_findings],
            "suppressed_secrets": self.suppressed_secrets,
            "declared_deps": list(self.declared_deps),
            "carry_over_exempt": self.carry_over_exempt,
            "summary": {
                "critical_count": sum(
                    1 for f in self.secret_findings if f.severity == "Critical"
                ),
                "important_count": sum(
                    1 for f in self.import_findings if f.severity == "Important"
                ),
                "total_findings": (
                    len(self.secret_findings) + len(self.import_findings)
                ),
            },
        }


def _slice_is_carry_over(slice_folder: Path) -> bool:
    brief = slice_folder / "mission-brief.md"
    if not brief.exists():
        return False
    mtime_date = datetime.fromtimestamp(brief.stat().st_mtime).date()
    return mtime_date < _VAL_1_RELEASE_DATE


def _read_allowlist(path: Path | None) -> list[re.Pattern[str]]:
    """Read allowlist regex patterns from a file (one per line; # comments)."""
    if path is None or not path.exists():
        return []
    patterns: list[re.Pattern[str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            patterns.append(re.compile(line))
        except re.error:
            continue  # skip malformed entries silently
    return patterns


def scan_secrets(
    file_paths: list[Path],
    allowlist_patterns: list[re.Pattern[str]],
) -> tuple[list[SecretFinding], int]:
    """Walk files for secret patterns. Returns (findings, suppressed_count)."""
    findings: list[SecretFinding] = []
    suppressed = 0
    for path in file_paths:
        if not path.exists() or path.is_dir():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for name, pattern in _SECRET_PATTERNS.items():
                for m in pattern.finditer(line):
                    snippet = m.group(0)
                    is_allowed = any(p.search(snippet) for p in allowlist_patterns)
                    if is_allowed:
                        suppressed += 1
                        continue
                    short = snippet[:80] + ("..." if len(snippet) > 80 else "")
                    findings.append(SecretFinding(
                        path=str(path), line=line_no,
                        pattern_name=name,
                        snippet=short,
                        kind="secret-detected",
                        severity="Critical",
                        message=(
                            f"possible {name} detected at line {line_no}. "
                            f"Critical (cannot defer). If this is a false "
                            f"positive (test fixture, public-docs example), "
                            f"add a regex to architecture/.secrets-allowlist."
                        ),
                    ))
    return findings, suppressed


def _extract_pkg_name(spec: str) -> str:
    """Extract a package name from a dep spec like 'anthropic>=0.34.0[extras]'."""
    cleaned = spec.split("#", 1)[0].strip()
    if not cleaned or cleaned.startswith("-"):
        return ""
    # Take everything up to the EARLIEST separator (extras `[`, version `>=`,
    # marker `;`, URL `@`, whitespace). Iterating without tracking the earliest
    # index would pick the first separator in the iteration order, not the
    # one that actually appears first in the string.
    earliest = len(cleaned)
    for sep in ("<", ">", "=", "!", "~", "[", ";", " ", "@"):
        idx = cleaned.find(sep)
        if 0 <= idx < earliest:
            earliest = idx
    return cleaned[:earliest].strip()


def _normalize_pkg(name: str) -> str:
    """PEP 503 normalization: lowercase, hyphens/underscores/dots -> single underscore."""
    return re.sub(r"[-_.]+", "_", name.strip().lower())


def parse_declared_deps(
    pyproject_path: Path | None,
    requirements_path: Path | None,
) -> set[str]:
    """Parse declared dependencies from pyproject.toml + requirements.txt."""
    deps: set[str] = set()

    if pyproject_path and pyproject_path.exists() and tomllib is not None:
        try:
            data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, OSError):
            data = {}

        # PEP 621
        project = data.get("project", {})
        for spec in project.get("dependencies", []) or []:
            name = _extract_pkg_name(spec)
            if name:
                deps.add(_normalize_pkg(name))
        opt_deps = project.get("optional-dependencies", {}) or {}
        for group in opt_deps.values():
            for spec in group:
                name = _extract_pkg_name(spec)
                if name:
                    deps.add(_normalize_pkg(name))

        # Poetry
        poetry_deps = (
            data.get("tool", {}).get("poetry", {}).get("dependencies", {}) or {}
        )
        for name in poetry_deps:
            if name == "python":
                continue
            deps.add(_normalize_pkg(name))
        poetry_dev = (
            data.get("tool", {}).get("poetry", {}).get("dev-dependencies", {}) or {}
        )
        for name in poetry_dev:
            deps.add(_normalize_pkg(name))

        # setuptools — explicit-list form only (`[tool.setuptools] packages =
        # ["pkg"]`). The `[tool.setuptools.packages.find]` auto-discovery
        # variant is intentionally not handled in v1 (see ADR-002). Lives
        # inside this `if pyproject_path ...` branch because `data` is only
        # defined here.
        setuptools_packages = (
            data.get("tool", {}).get("setuptools", {}).get("packages", [])
        )
        if isinstance(setuptools_packages, list):
            for name in setuptools_packages:
                if isinstance(name, str) and name:
                    deps.add(_normalize_pkg(name))

    if requirements_path and requirements_path.exists():
        for raw in requirements_path.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or line.startswith("-"):
                continue
            name = _extract_pkg_name(line)
            if name:
                deps.add(_normalize_pkg(name))

    return deps


def _check_import_resolves(
    import_top: str,
    declared: set[str],
) -> bool:
    """True if the import resolves to stdlib, declared dep, or known alias."""
    if not import_top:
        return True
    if import_top in _STDLIB:
        return True
    if _normalize_pkg(import_top) in declared:
        return True
    alias = _KNOWN_ALIASES.get(import_top)
    if alias and _normalize_pkg(alias) in declared:
        return True
    return False


def scan_imports(
    file_paths: list[Path],
    declared_deps: set[str],
) -> list[ImportFinding]:
    """ast-parse Python files; flag imports not in stdlib/declared/aliases."""
    findings: list[ImportFinding] = []
    seen: set[tuple[str, int, str]] = set()
    for path in file_paths:
        if path.suffix != ".py" or not path.exists() or path.is_dir():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".", 1)[0]
                    if _check_import_resolves(top, declared_deps):
                        continue
                    key = (str(path), node.lineno, top)
                    if key in seen:
                        continue
                    seen.add(key)
                    findings.append(ImportFinding(
                        path=str(path), line=node.lineno,
                        import_name=top,
                        kind="hallucinated-import",
                        severity="Important",
                        message=(
                            f"`import {alias.name}` references package "
                            f"'{top}' not declared in pyproject.toml or "
                            f"requirements.txt. Possible AI hallucination — "
                            f"if real, add to project deps."
                        ),
                    ))
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0 or node.module is None:
                    continue  # relative or `from . import x`
                top = node.module.split(".", 1)[0]
                if _check_import_resolves(top, declared_deps):
                    continue
                key = (str(path), node.lineno, top)
                if key in seen:
                    continue
                seen.add(key)
                findings.append(ImportFinding(
                    path=str(path), line=node.lineno,
                    import_name=top,
                    kind="hallucinated-import",
                    severity="Important",
                    message=(
                        f"`from {node.module} import ...` references package "
                        f"'{top}' not declared in pyproject.toml or "
                        f"requirements.txt. Possible AI hallucination — "
                        f"if real, add to project deps."
                    ),
                ))
    return findings


def run_layers(
    slice_folder: Path,
    changed_files: list[Path],
    secrets_allowlist: Path | None = None,
    pyproject: Path | None = None,
    requirements: Path | None = None,
    skip_secrets: bool = False,
    skip_deps: bool = False,
    skip_if_carry_over: bool = True,
    imports_allowlist: list[str] | None = None,
) -> LayersResult:
    """Run both VAL-1 layers against the changed files.

    `imports_allowlist`: optional list of additional package names to
    treat as resolved by Layer B (alongside stdlib + declared deps +
    aliases + setuptools-packages). Lenient: entries that name-normalize
    to empty are silently skipped (be liberal in what you accept
    programmatically). The CLI is the strict boundary that rejects
    empties via parser.error.
    """
    result = LayersResult()

    if skip_if_carry_over and _slice_is_carry_over(slice_folder):
        result.carry_over_exempt = True
        return result

    if not skip_secrets:
        allowlist = _read_allowlist(secrets_allowlist)
        secrets, suppressed = scan_secrets(changed_files, allowlist)
        result.secret_findings = secrets
        result.suppressed_secrets = suppressed

    if not skip_deps:
        declared = parse_declared_deps(pyproject, requirements)
        for name in imports_allowlist or []:
            normalized = _normalize_pkg(name)
            if normalized:
                declared.add(normalized)
        result.declared_deps = sorted(declared)
        result.import_findings = scan_imports(changed_files, declared)

    return result


def _format_human(result: LayersResult) -> str:
    if result.carry_over_exempt:
        return (
            "VAL-1 layered safety checks: slice is carry-over exempt "
            "(mission-brief.md predates rule release).\n"
        )

    out: list[str] = []
    out.append(
        f"VAL-1 layered safety checks: "
        f"{len(result.secret_findings)} secret(s), "
        f"{len(result.import_findings)} import finding(s), "
        f"{result.suppressed_secrets} suppressed (allowlisted).\n\n"
    )

    if result.secret_findings:
        out.append("Critical (Layer A — credential scan):\n")
        for f in result.secret_findings:
            out.append(
                f"  [{f.severity}] {f.path}:{f.line} "
                f"({f.pattern_name}) snippet={f.snippet}\n"
                f"    {f.message}\n"
            )
        out.append("\n")

    if result.import_findings:
        out.append("Important (Layer B — dependency hallucination):\n")
        for f in result.import_findings:
            out.append(
                f"  [{f.severity}] {f.path}:{f.line} "
                f"({f.kind}) `{f.import_name}`\n"
                f"    {f.message}\n"
            )
        out.append("\n")

    if not result.secret_findings and not result.import_findings:
        out.append("Clean — both layers passed.\n")

    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="validate_slice_layers",
        description="VAL-1 layered /validate-slice safety checks",
    )
    parser.add_argument(
        "--slice", type=Path, required=True,
        help="Path to the slice folder (for carry-over check)",
    )
    parser.add_argument(
        "--changed-files", nargs="*", default=[], type=Path,
        help="Files changed by this slice (Layer A walks these; Layer B parses .py)",
    )
    parser.add_argument(
        "--secrets-allowlist", type=Path, default=None,
        help=(
            "Path to .secrets-allowlist regex file (default: "
            "architecture/.secrets-allowlist if it exists)"
        ),
    )
    parser.add_argument(
        "--pyproject", type=Path, default=None,
        help="Path to pyproject.toml (default: ./pyproject.toml if exists)",
    )
    parser.add_argument(
        "--requirements", type=Path, default=None,
        help="Path to requirements.txt (default: ./requirements.txt if exists)",
    )
    parser.add_argument(
        "--skip-secrets", action="store_true",
        help="Disable Layer A (credential scan)",
    )
    parser.add_argument(
        "--skip-deps", action="store_true",
        help="Disable Layer B (dependency hallucination check)",
    )
    parser.add_argument(
        "--imports-allowlist", action="append", default=None,
        metavar="NAME",
        help=(
            "Additional package name to treat as resolved by Layer B "
            "(repeatable). Useful for non-pip-installed conventional "
            "roots like 'tests'. Values are name-normalized. Empty / "
            "whitespace-only values are rejected at parse time."
        ),
    )
    parser.add_argument(
        "--no-carry-over", action="store_true",
        help="Disable mtime-based carry-over exemption",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output result as JSON",
    )
    args = parser.parse_args(argv)

    # Strict CLI boundary: reject empty / whitespace-only --imports-allowlist
    # values. The Python API's run_layers stays lenient (silently skips
    # empty-after-normalize) per ADR-002.
    if args.imports_allowlist is not None:
        cleaned = [s.strip() for s in args.imports_allowlist]
        if any(not c for c in cleaned):
            parser.error(
                "--imports-allowlist requires a non-empty package name"
            )
        args.imports_allowlist = cleaned

    slice_folder: Path = args.slice
    if not slice_folder.exists():
        sys.stderr.write(f"slice folder not found: {slice_folder}\n")
        return 2

    secrets_allowlist = args.secrets_allowlist
    if secrets_allowlist is None:
        candidate = Path("architecture/.secrets-allowlist")
        if candidate.exists():
            secrets_allowlist = candidate

    pyproject = args.pyproject
    if pyproject is None:
        candidate = Path("pyproject.toml")
        if candidate.exists():
            pyproject = candidate

    requirements = args.requirements
    if requirements is None:
        candidate = Path("requirements.txt")
        if candidate.exists():
            requirements = candidate

    result = run_layers(
        slice_folder=slice_folder,
        changed_files=list(args.changed_files),
        secrets_allowlist=secrets_allowlist,
        pyproject=pyproject,
        requirements=requirements,
        skip_secrets=args.skip_secrets,
        skip_deps=args.skip_deps,
        skip_if_carry_over=not args.no_carry_over,
        imports_allowlist=args.imports_allowlist,
    )

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    has_findings = bool(result.secret_findings or result.import_findings)
    return 1 if has_findings else 0


if __name__ == "__main__":
    sys.exit(main())
