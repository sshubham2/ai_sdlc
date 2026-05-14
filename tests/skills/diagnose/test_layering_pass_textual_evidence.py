"""LAYER-EVID-1 regression tests (slice-019 AC #2).

Per LAYER-EVID-1 (methodology-changelog.md v0.33.0): the /diagnose
03f-layering pass MUST grep-verify a textual import statement in the
evidence file before emitting any HIGH-severity layering-violation
finding. Zero textual matches -> downgrade to `low` (with
`evidence[].note: "downgraded: no textual import grep-match (LAYER-EVID-1)"`)
or skip emission.

This file exercises the rule's GREP SEMANTICS against synthetic
fixtures:
- parallel_types_no_import: backend src/backend/types.ts + frontend
  lib/types.ts define same-named enums; frontend imports only the
  LOCAL frontend types (alias `@/lib/types` rooted at frontend/).
  No cross-tier import exists textually. The rule's grep MUST return
  False here (no HIGH layering-violation emitted).
- parallel_types_real_import: frontend Bar.tsx actually imports from
  `../../src/backend/types` via relative path (named import + multi-line
  + side-effect + re-export). The rule's grep MUST return True here
  (HIGH layering-violation stands).

Test-local helper `_grep_textual_import` re-implements the rule's
grep semantics for fixture verification. Per /critique M1
ACCEPTED-PENDING: the regex strings here are byte-equal to those
embedded in `skills/diagnose/passes/03f-layering.md` Method step 4
(visual byte-equality is the prose-pin equivalent of CAD-1 byte-equality
at the rule-content level). A v2 audit asserting sha256 equality
between the prose-embedded regex and these constants is deferred
per TPHD-1 / RSAD-1 / RPCD-1 N>=3-violations-deferral precedent.

Rule reference: LAYER-EVID-1 (slice-019 ACs #1, #2).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# ---------------------------------------------------------------------------
# Regex constants — MUST be byte-equal to skills/diagnose/passes/03f-layering.md
# Method step 4 prose (per /critique M1 mitigation: visual byte-equality
# at codification time is the prose-pin equivalent of CAD-1 byte-equality).
# ---------------------------------------------------------------------------

# TypeScript / JavaScript import variants (5 import + 3 re-export + 2 dynamic forms)
TS_IMPORT_PATTERNS = [
    r"^\s*import\s+\w+\s+from\s+['\"]<PATH>['\"]",                    # default import
    r"^\s*import\s+\{[^}]*\}\s+from\s+['\"]<PATH>['\"]",              # named import (with DOTALL for multi-line)
    r"^\s*import\s+\*\s+as\s+\w+\s+from\s+['\"]<PATH>['\"]",         # namespace import
    r"^\s*import\s+type\s+\{[^}]*\}\s+from\s+['\"]<PATH>['\"]",       # type-only named
    r"^\s*import\s+['\"]<PATH>['\"]\s*;?\s*$",                        # side-effect (no `from`)
    r"^\s*export\s+\{[^}]*\}\s+from\s+['\"]<PATH>['\"]",              # re-export named
    r"^\s*export\s+\*\s+from\s+['\"]<PATH>['\"]",                     # re-export all
    r"^\s*export\s+type\s+\{[^}]*\}\s+from\s+['\"]<PATH>['\"]",       # re-export type-only
    r"require\(\s*['\"]<PATH>['\"]\s*\)",                             # CommonJS
    r"\bimport\(\s*['\"]<PATH>['\"]\s*\)",                            # dynamic import()
]

# Python import variants
PY_IMPORT_PATTERNS = [
    r"^\s*from\s+<MODULE>\s+import\s+",
    r"^\s*import\s+<MODULE>(\s|$|\.)",
]


def _build_ts_pattern(bypassed_path: str) -> re.Pattern:
    """Combine all TS variant patterns into one alternation, with <PATH>
    substituted for the bypassed-path. Uses re.DOTALL + re.MULTILINE so
    multi-line named imports match across newlines."""
    escaped = re.escape(bypassed_path)
    alts = [p.replace("<PATH>", escaped) for p in TS_IMPORT_PATTERNS]
    combined = "|".join(f"(?:{a})" for a in alts)
    return re.compile(combined, re.MULTILINE | re.DOTALL)


def _resolve_aliases(target_dir: Path) -> dict[str, list[str]]:
    """Read frontend tsconfig.json (or jsconfig.json) and extract
    `compilerOptions.paths` (alias -> [resolved_paths]). Returns empty
    dict if no tsconfig/jsconfig or no paths configured.

    The alias-aware grep (load-bearing for the F-LAYER-bca9c001 witness):
    if the bypassed-path is repo-relative (e.g., `src/backend/types`)
    AND a frontend tsconfig has a `paths` map, the subagent must also
    grep for the alias-resolved logical name (e.g., `@/backend/types`
    if `@/*` -> `src/*`).
    """
    aliases: dict[str, list[str]] = {}
    for cfg_name in ("tsconfig.json", "jsconfig.json"):
        for cfg_path in target_dir.rglob(cfg_name):
            try:
                # Tolerate trailing commas / // comments via permissive load
                raw = cfg_path.read_text(encoding="utf-8")
                # naive: strip `//` line comments
                stripped = re.sub(r"^\s*//.*$", "", raw, flags=re.MULTILINE)
                cfg = json.loads(stripped)
            except (OSError, json.JSONDecodeError):
                continue
            paths = (cfg.get("compilerOptions") or {}).get("paths") or {}
            for alias, resolveds in paths.items():
                if isinstance(resolveds, list):
                    aliases[alias] = resolveds
    return aliases


def _alias_forms(bypassed_path: str, aliases: dict[str, list[str]]) -> list[str]:
    """Given the repo-relative bypassed path and the alias map, return
    additional grep-target forms (the alias-resolved logical names).

    Example: if bypassed_path="src/backend/types" and aliases={"@/*": ["src/*"]},
    return ["@/backend/types"] (the leading "src/" matches the resolved-prefix,
    so the alias form replaces "src/" with "@/").
    """
    forms: list[str] = []
    for alias, resolveds in aliases.items():
        # Strip the trailing /* from alias if present
        if alias.endswith("/*"):
            alias_prefix = alias[:-2]
        else:
            alias_prefix = alias
        for resolved in resolveds:
            if resolved.endswith("/*"):
                resolved_prefix = resolved[:-2]
            else:
                resolved_prefix = resolved
            # If the bypassed_path starts with the resolved-prefix, swap
            # the prefix for the alias-prefix.
            if resolved_prefix and bypassed_path.startswith(resolved_prefix + "/"):
                remainder = bypassed_path[len(resolved_prefix) + 1:]
                forms.append(f"{alias_prefix}/{remainder}")
    return forms


def _grep_textual_import(
    target_dir: Path,
    evidence_file: Path,
    bypassed_path: str,
    language: str = "typescript",
) -> bool:
    """Return True iff a textual import statement matching the alleged
    bypass exists in the evidence file.

    Implements the LAYER-EVID-1 rule's grep semantics. Searches:
    - The bypassed_path as-given
    - Any alias-resolved form (via tsconfig.json paths/baseUrl)
    - Across all variant regex patterns for the target language

    Returns True on first match (any variant, any form).
    """
    text = evidence_file.read_text(encoding="utf-8")
    paths_to_try = [bypassed_path]

    if language == "typescript":
        aliases = _resolve_aliases(target_dir)
        paths_to_try.extend(_alias_forms(bypassed_path, aliases))
        for p in paths_to_try:
            pattern = _build_ts_pattern(p)
            if pattern.search(text):
                return True
        # Also try with `.ts` / `.tsx` suffix stripped (TS modules
        # typically import without the extension).
        for p in paths_to_try:
            if p.endswith(".ts") or p.endswith(".tsx"):
                stem = p.rsplit(".", 1)[0]
                pattern = _build_ts_pattern(stem)
                if pattern.search(text):
                    return True
    elif language == "python":
        for module_path in paths_to_try:
            # Convert filesystem path to dotted module form if needed
            module = module_path.replace("/", ".").rstrip(".py").rstrip(".")
            for raw in PY_IMPORT_PATTERNS:
                pattern = re.compile(raw.replace("<MODULE>", re.escape(module)), re.MULTILINE)
                if pattern.search(text):
                    return True
    return False


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_synthetic_parallel_types_no_import_yields_zero_high_layering_findings():
    """Fixture `parallel_types_no_import` reproduces F-LAYER-bca9c001 shape:
    backend src/backend/types.ts + frontend lib/types.ts define same-named
    enums; frontend imports only the LOCAL frontend types via `@/lib/types`
    alias (rooted at frontend/, physically cannot reach src/).

    LAYER-EVID-1 grep MUST return False for any alleged cross-tier import
    from frontend/components/Foo.tsx to src/backend/types — proving the
    rule would downgrade or skip a HIGH layering-violation finding on
    this codebase.

    Rule reference: LAYER-EVID-1 (slice-019 AC #2).
    Defect class: phantom graphify edges from cross-file same-name
    symbol collapse producing false-positive HIGH boundary findings.
    """
    fixture = FIXTURES_DIR / "parallel_types_no_import"
    foo = fixture / "frontend" / "components" / "Foo.tsx"

    assert foo.exists(), f"fixture file missing: {foo}"

    # The alleged bypassed path (repo-relative from fixture root) — what
    # the layering pass would cite as the boundary-violation target.
    # Test BOTH `.ts` form and stem form. Frontend tsconfig has the
    # @/* -> ./* mapping, which is rooted at frontend/, so @/-alias
    # CANNOT reach src/backend/. The rule must conclude: no textual
    # import.
    bypassed = "src/backend/types"
    target = fixture / "frontend"
    assert _grep_textual_import(target, foo, bypassed) is False, (
        f"LAYER-EVID-1 grep falsely matched for {bypassed} in {foo} — "
        f"parallel_types_no_import fixture should have ZERO textual imports "
        f"from frontend to src/backend (the F-LAYER-bca9c001 false-positive "
        f"class). If this fails, either (a) the fixture has a real cross-tier "
        f"import that shouldn't be there, or (b) the grep helper has a false "
        f"positive that would re-create the witnessed bug."
    )


def test_synthetic_real_cross_tier_import_still_fires_high_layering_finding():
    """Fixture `parallel_types_real_import` is the positive control:
    frontend/components/Bar.tsx actually imports from `../../src/backend/types`
    via relative path (named import + multi-line + side-effect + re-export
    variants are all present).

    LAYER-EVID-1 grep MUST return True for the alleged cross-tier import —
    proving the rule does NOT suppress true-positive HIGH layering-violation
    findings.

    Rule reference: LAYER-EVID-1 (slice-019 AC #2).
    Defect class: rule over-suppression (false negative) would silently
    drop legitimate boundary-violation findings.
    """
    fixture = FIXTURES_DIR / "parallel_types_real_import"
    bar = fixture / "frontend" / "components" / "Bar.tsx"

    assert bar.exists(), f"fixture file missing: {bar}"

    # The alleged bypassed path — Bar.tsx imports this via relative path
    # AND via re-export AND via side-effect, so any of the 10 TS patterns
    # should match.
    bypassed = "../../src/backend/types"
    target = fixture / "frontend"
    assert _grep_textual_import(target, bar, bypassed) is True, (
        f"LAYER-EVID-1 grep failed to match a real cross-tier import in {bar} "
        f"for {bypassed} — the rule would falsely DOWNGRADE a true-positive "
        f"HIGH boundary finding. The fixture has named + multi-line + "
        f"side-effect + re-export variants; at least one must match."
    )
