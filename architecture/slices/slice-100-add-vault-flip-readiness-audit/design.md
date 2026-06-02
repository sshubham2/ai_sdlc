# Design: Slice 100 add-vault-flip-readiness-audit

**Date**: 2026-06-02
**Mode**: Standard

## What's new

- **`tools/vault_flip_readiness_audit.py`** — a deterministic, **read-only** audit that scans the production-code surface (`tools/**/*.py` + skill-helper `skills/**/*.py`) for `architecture/` / `diagnose-out/` path literals and classifies each occurrence via Python `ast` + `tokenize` into the 4-class taxonomy of [[ADR-091]]. CLI: `--json` (full inventory), `--strict` (also gate on baseline drift), default (gate on `needs-human-classification`). cp1252-safe stdout via `tools._stdout.reconfigure_stdout_utf8()`.
- **`tests/methodology/test_vault_flip_readiness_audit.py`** — TF-1 test module: classification correctness across the ordered ruleset, determinism (byte-identical re-run), fail-closed (parse-error / dynamic-fragment / unmarked-git-pathspec → `needs-human`), the **baseline pin keyed on `(relpath, ast.Constant.value, klass)`** (line-number-independent, full constant value not a line-snippet — M2) of the `must-rewrite-before-flip` + `needs-human-classification` sets, CLI exit codes, **non-vacuity by two mutations** (inject a real seam *path-construction* literal → MUST enter `must-rewrite`; inject an error-*message* vault literal → MUST NOT enter `must-rewrite` — M2 proves the B1 fix holds), and the AC5 capability-without-flip invariant.
- **`architecture/shippability.md`** — a new row asserting the baseline pin never silently regresses (SCPD-1 / RPCD-1).
- **`tools/parallel_conflict_resolver.py`** — adds the [[ADR-089]] Class-B marker to the `_SOFT_FILE_SET` **definition** (lines 60-61), closing the slice-098 marker-coverage gap (B2). The only edit to an existing production module; **adds `parallel_conflict_resolver.py` to the slice blast radius** (note for merge ordering vs the parallel in-flight slice-101).
- **Registration** — `plugin.yaml` tools list + `tools/install_audit.py` `_CANONICAL_TOOLS` + `INSTALL.md` tool count (PMI-1 / INST-1 / BC-PROJ-9 fan-out; full five-site grep at build per m2; see §MEPD-1).

## What's reused

- `tools/_vault_paths.py` — `VAULT_ROOT` / `VAULT_ROOT_IS_DEFAULT` ([[ADR-065]] / [[ADR-085]]): the seam that *defines* "routed". The `already-seam-routed` class recognizes `VAULT_ROOT`-derived sites; **AC5 asserts the default stays `Path("architecture")`**.
- The slice-098 / [[ADR-089]] **Class-B marker convention** — the trailing comment `# … NOT VAULT_ROOT-routed (slice-068) -- Class-B git identity (ADR-089)` (21 occurrences in `tools/parallel_conflict_resolver.py`, plus the `# slice-098/ADR-089 Class-A ROUTE` companion). Recognized as `already-seam-routed`: deliberate, retire-guarded git-string literals — **not** breakage.
- `tools/_vault_git.py` (`vault_is_external`, `vault_pathspec_is_tracked`) — context for *why* Class-B literals are safe (retire via the store-location guard at flip). The audit references the model; the flip-execute slice consumes the functions.
- `tools/_stdout.py` `reconfigure_stdout_utf8()` — UTF8-STDOUT-1 (cp1252 class N≥8).
- Structural template: `tools/skill_vault_write_safety_audit.py` + `tools/vault_write_safety_audit.py` — CLI / `--json` / exit-code / frozen-dataclass conventions to mirror.
- Repo-root resolution: VWS-1's `Path(__file__).resolve().parent.parent` default + a `--repo-root` override (the structural template this audit mirrors). **NOT** `tools/_pyfn.py` — that is the PTFFD-1 test-function-resolution helper and has no `_find_repo_root` (m1 correction).

## Components touched

### `tools/vault_flip_readiness_audit.py` (new)
- **Responsibility**: produce the deterministic, classified inventory of in-tree-vault-location path literals on the production-code surface, so (a) the flip-execute slice has a complete checklist and (b) the test suite guards against new unrouted literals. **Read-only — never mutates source.**
- **Lives at**: `tools/vault_flip_readiness_audit.py` (created by this slice).
- **Key interactions**: reads `tools/**/*.py` + `skills/**/*.py` via `ast` + `tokenize`; imports `VAULT_ROOT` for the routed-site notion; recognizes the [[ADR-089]] Class-B marker + the slice-068 error-message-prose marker; performs **≤1-hop usage analysis** (path-construction-context detection à la VWS-1 `_resolve_target`) so a path the code *resolves* is distinguished from a vault path *mentioned* in a message string (the B1/M1 context-aware classification); emits JSON/text to stdout; exit codes for gating.

## Contracts added or changed

### CLI: `python -m tools.vault_flip_readiness_audit`
- **Args**: `[--json] [--strict] [--repo-root PATH]`.
- **Exit codes**: `0` = no `needs-human-classification` (and, under `--strict`, baseline unchanged); `2` = ≥1 `needs-human-classification` OR `--strict` baseline drift; `1` = usage error (bad args / unreadable repo-root) → stderr (R-7 fail-visible, never a silent skip).
- **Output**: default = human summary (per-class counts + the `must-rewrite` and `needs-human` lists with `path:line`); `--json` = full inventory `[{path, line, col, snippet, klass, reason}]` **sorted by (path, line, col)** (determinism).
- **No** network, **no** writes, **no** auth surface.

## Data model deltas

None (no persistent store). The 4-class taxonomy ([[ADR-091]]) is the only "model" — encoded as module-level string constants + a frozen dataclass per occurrence.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/vault_flip_readiness_audit.py` | `architecture/shippability.md` row (runs `$PY -m tools.vault_flip_readiness_audit --strict`) + CLI `main()` | `tests/methodology/test_vault_flip_readiness_audit.py::test_cli_strict_nonzero_on_baseline_drift` + `::test_must_rewrite_baseline_pinned` | — |

## Decisions made (ADRs)

- [[ADR-091]] — vault-flip-readiness 4-class classification model + production-`.py` scan scope + Class-B marker recognition — reversibility: **cheap**.

## Authorization model for this slice

N/A — a read-only local CLI audit. No auth/authz, no network, no writes.

## Error model for this slice

Classification follows the **context-aware ordered ruleset** of [[ADR-091]] §Decision (prose-context → routed → path-construction → fail-closed-ambiguous → prose-mention default), with the explicit match rule (bare-or-slashed segment; **context** decides the class, B-add-1) + one documented residual (a fully-dynamic path with no `architecture`/`diagnose-out` string-literal segment). Specific fail-closed cases:

- **Unparseable `.py`** (`SyntaxError`) → one `needs-human-classification` entry per file (reason `parse-error`). Never a silent skip.
- **Unmarked git-pathspec** literal (git-subprocess arg / git-pathspec `frozenset`/`tuple`/`list` member with no Class-B marker — e.g. PCR `_SOFT_FILE_SET` before the B2 marker edit) → `needs-human-classification` (reason `unmarked-git-pathspec`); the human decides rewrite-vs-Class-B.
- **Dynamic-fragment** (only a fragment is a constant — composed via f-string / `+` / `.format()` — and it flows into a path/git context) → `needs-human-classification` (reason `dynamic-fragment`).
- **Plain message/prose string** matching the pattern but in no path/git context → `doc-example-safe` (reason `prose-mention`); at worst cosmetically stale post-flip, never a silent path mis-resolve (the B1 fix).
- **Repo-root unresolvable / not a directory** → exit 1 usage error on stderr (R-7 fail-visible).
- **cp1252 stdout** → `reconfigure_stdout_utf8()` at `main()` entry before any print.

## MEPD-1 (disposition deferred to /reflect)

New **public** tool → PMI-1 / INST-1 / BC-PROJ-9 inventory updates are **required** (plugin.yaml + `install_audit._CANONICAL_TOOLS` + INSTALL.md count) regardless of MEPD-1. Tentative MEPD-1 **EXCLUDE**: this is a flip-prep *utility*, not a pipeline-wide enforced RULE-ID; **no VERSION / methodology-changelog bump anticipated** (so MCFS-1 / AVFS-1 / TVFS-1 forward-sync gates no-op). Final call at `/reflect`.

## Scope boundary (settled at /design-slice — see ADR-091 §Scope)

In-scope surface: `tools/**/*.py` + `skills/**/*.py` (3 helpers: `assemble.py`, `write_pass.py`, `build_backlog.py`). **Out**: `tests/**/*.py` (loud breakage; intentional seam constants) and contract-prose (`SKILL.md` / `agents` / `CLAUDE.md` / `INSTALL.md` — bulk-rewritten atomically at flip-execute, AI-hard to auto-classify) → deferred follow-ups. Excluded dirs: `architecture/slices/archive/**`, `.git/`, `graphify-out/`, `diagnose-out/`, `.venv/`, and the audit's own module/baseline.
