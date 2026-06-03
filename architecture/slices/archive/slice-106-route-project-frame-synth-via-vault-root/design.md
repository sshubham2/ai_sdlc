# Design: Slice 106 route-project-frame-synth-via-vault-root

**Date**: 2026-06-03
**Mode**: Standard

## What's new

A pure-routing change (no new behavior, no new module). Four hardcoded vault-path literals in `tools/project_frame_synth.py` move onto the existing `VAULT_ROOT` seam, taking the vault-flip readiness audit's production `must-rewrite` set from 4 → 0. The edits form one coupled chain across **3 files + 1 test file** (the consequence set is wider than the mission brief's "readiness-audit baseline" alone — see §Consequence chain):

1. **`tools/project_frame_synth.py`** (modified)
   - Add `from tools._vault_paths import VAULT_ROOT` (after the existing `from tools import _stdout`, L59) — the **exact** import string the allowlist drift guard greps for (`test_vault_root_constant.py:304`).
   - Route the 4 sites `repo_root / "architecture" / "<file>"` → `repo_root / VAULT_ROOT / "<file>"` at L121 (`concept.md`), L122 (`triage.md`), L185 (`slice-queue.md`), L194 (`risk-register.md`). This mirrors the established idiom at `tools/slice_queue_writer.py:774` (`repo_root / VAULT_ROOT / _QUEUE_FILENAME`).
   - Rephrase the **module-docstring example** at L44 (`Path("architecture/slices/slice-NNN-x")`) so it no longer carries a quote-prefixed `"architecture/` literal (model `VAULT_ROOT`/`<slice_dir>` instead) — otherwise it becomes an orphan-literal violation once the file joins the allowlist (see §Consequence chain #2).

2. **`tests/methodology/test_vault_root_constant.py`** (modified)
   - Add `"tools/project_frame_synth.py"` to `_MIGRATION_SITE_ALLOWLIST` (L45-63) with a `# slice-106` provenance comment — required so `test_migration_site_allowlist_pinned` (AC4, the bidirectional drift guard) stays green once project_frame_synth becomes an actual `VAULT_ROOT` importer.
   - Correct the stale count narrative: the comment (L41) + the `test_migration_site_allowlist_pinned` docstring (L291) say **"14-element"**, but the live set is already **15** (slice-103 added `index_router_thinness_audit.py` without bumping the prose); slice-106 makes it **16**. Since this slice edits that exact region, repoint the count in the same block (AP-13 consumer-citation hygiene).

3. **`tools/vault_flip_readiness_audit.py`** (modified)
   - `_BASELINE` (L162-171): remove the 4 `("tools/project_frame_synth.py", "architecture", "must-rewrite-before-flip")` tuples → `_BASELINE = ()`. Reword the comment: the production-`.py` `must-rewrite` set is now **empty** (the silent-breakage surface is clean); the classifier's non-vacuity is still proven by the synthetic checks in `test_must_rewrite_baseline_pinned`.

4. **`tests/methodology/test_vault_flip_readiness_audit.py`** (modified — **one real assertion change** + narrative)
   - **(B1, /critique) `test_emits_classified_inventory_with_evidence` (L38-49)** asserts `MUST_REWRITE in classes` against the **real repo** via `audit_root(REPO_ROOT)`. The only 4 real-repo `MUST_REWRITE` occurrences ARE the 4 `project_frame_synth.py` sites this slice routes (the tests surface remaps to `TEST_UPDATE_AT_FLIP`, never `MUST_REWRITE`), so once production must-rewrite → 0 that assertion is `False` and the test **fails** — breaking AC2/AC5 and (via shippability rows running this module) the catalog. **Fix**: move the `MUST_REWRITE`-presence proof onto a **synthetic injected-literal fixture** (mirror the existing `test_new_unrouted_literal_fails_gate` tmp-file pattern) so it stays **non-vacuous** after the real-repo set empties; keep the `ALREADY_SEAM_ROUTED` / `DOC_EXAMPLE_SAFE` real-repo presence asserts (both stay populated).
   - `test_must_rewrite_baseline_pinned` (L81-85) asserts `live == tuple(sorted(_BASELINE))` — stays correct with both sides empty (no assertion change). Reword its in-test narrative that says "4 project_frame_synth sites" to the now-empty production baseline. The non-vacuity sub-asserts (L90-99: a synthetic bare-`architecture` `/`-BinOp still classifies `must-rewrite`; an error-message literal does not) are independent of project_frame_synth and stay green.
   - **(M2 narrative) `test_production_baseline_unchanged_vs_slice100` (L220-229)** still passes (both sides empty) but its name/comment assert "unchanged" — reword the comment to note slice-106 deliberately emptied the production baseline (do not rely on the name reading as accurate).

## What's reused

- `tools/_vault_paths.VAULT_ROOT` — the seam (`[[slice-068-add-vault-root-constant]]`, `[[ADR-065]]`). Default `Path("architecture")` ⇒ **zero behavior change on this repo today**; the routing is a no-op until a flip sets `VAULT_ROOT` elsewhere. Consume-only; this slice does **not** touch `_vault_paths.py` resolution logic.
- The `repo_root / VAULT_ROOT / "<file>"` composition idiom — `tools/slice_queue_writer.py:774,834` (precedent). `pathlib` absolute-RHS-reset makes it flip-correct: when `VAULT_ROOT` is absolute (external store), `repo_root / VAULT_ROOT` collapses to `VAULT_ROOT`; when relative, it stays `repo_root/architecture`.
- The slice-068 migration convention machinery in `tests/methodology/test_vault_root_constant.py` (`_MIGRATION_SITE_ALLOWLIST` import test, two-marker no-orphan-literal test, bidirectional allowlist-pin) — this slice **joins** that machinery rather than inventing a new regression guard.
- `tools/vault_flip_readiness_audit.py` `_BASELINE` + its `--strict` gate (`[[slice-100-add-vault-flip-readiness-audit]]`, `[[ADR-091]]`).

## Components touched

### `tools/project_frame_synth.py` (modified)
- **Responsibility**: synthesize the ephemeral PFS-1 project-frame (Identity / Trajectory / Impact) read at `/design-slice` Step 0.5 and handed to both Critic layers at `/critique`. Reads four vault files (`concept.md`, `triage.md`, `slice-queue.md`, `risk-register.md`).
- **Lives at**: `tools/project_frame_synth.py` (modified — routing + docstring + import only; no logic change).
- **Key interactions**: consumers of its *stdout* are the `design-slice` + `critique` skills (PFS-1). Consumers of its *path logic* are internal. Output MUST stay byte-identical (AC3) — the routing is observably a no-op under the default `VAULT_ROOT`.

### `tools/vault_flip_readiness_audit.py` (modified)
- **Responsibility**: classify every in-tree vault-location literal on the production-`.py` surface; `--strict` is the flip's pre-flight gate.
- **Lives at**: `tools/vault_flip_readiness_audit.py` (modified — `_BASELINE` data + comment only; no classifier-logic change).
- **Key interactions**: pinned by `test_vault_flip_readiness_audit.py`; its `--strict` baseline is the M4 flip gate.

## Contracts added or changed

None. No endpoints, events, schemas, or CLI surface change. `project_frame_synth`'s `--repo-root` / `--slice-dir` CLI and `synthesize_frame(repo_root, slice_dir)` signature are unchanged; `vault_flip_readiness_audit`'s CLI/exit-code contract is unchanged.

## Data model deltas

None.

## Consequence chain (why the blast radius is 3 files, not 1)

The mission brief named the `_BASELINE` re-pin; design surfaces **three** further coupled consequences of making project_frame_synth a `VAULT_ROOT` importer and driving production must-rewrite to 0:

1. **Allowlist drift guard** — `test_migration_site_allowlist_pinned` asserts `_MIGRATION_SITE_ALLOWLIST == {tools/*.py importing VAULT_ROOT}`. Adding the import without adding the allowlist entry = "drift IN" failure. ⇒ must bump the allowlist (15→16).
2. **Orphan-literal guard** — once in the allowlist, `test_no_orphan_architecture_literal_in_migrated_tools` (regex `["\']architecture[/"\\]`) scans the file. The 4 routed sites lose their literal (safe). L48 (`--slice-dir architecture/...`) and L304 (argparse `help=`) are **space-prefixed**, not quote-prefixed ⇒ not matched. Only the **L44 docstring example** `Path("architecture/slices/...")` is quote-prefixed and is NOT excluded by the test's `startswith('"'/"'")` heuristic (the line starts with `frame =`) ⇒ it WOULD be flagged. ⇒ must rephrase L44.
3. **(B1, /critique — verified by execution) Real-repo `MUST_REWRITE`-presence assertion** — `test_emits_classified_inventory_with_evidence` (`test_vault_flip_readiness_audit.py:38-49`) asserts `MUST_REWRITE in classes` against `audit_root(REPO_ROOT)`. The repo's ONLY `MUST_REWRITE` occurrences are the 4 project_frame_synth sites; routing them to 0 flips that assertion to `False` ⇒ the test reds (and, via shippability rows that run this module, reds the catalog). ⇒ must move the `MUST_REWRITE` proof onto a synthetic injected-literal fixture (see §"What's new" item 4). This is the APED-1 lesson live: design-time reasoning about `_BASELINE` did not trace the *sibling* real-repo assertion in the same module — only executing `audit_root` surfaced it.

Consequences 1–2 are *pre-existing* guards that newly apply once the file is migrated; consequence 3 is a real assertion that newly **fails** when the must-rewrite set empties. Missing any reds the suite.

## Wiring matrix

This slice introduces **no new module** (it modifies existing files only). Per WIRE-1, a zero-row matrix is clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

**None.** This slice locks no new decision — it *applies* the existing `[[ADR-065]]` `VAULT_ROOT` seam and the `[[ADR-091]]` readiness baseline to the last unrouted production file. Minting an ADR for a convention-following routing change would be the ADR-for-trivial anti-pattern. (If `/critique` judges the docstring-rephrase or count-correction to be a convention change, it is already covered by the slice-068 two-marker convention — no new ADR.)

**(m2, /critique) MEPD-1 EXCLUDE posture** — this is pure application of the existing ADR-065 seam + ADR-091 baseline: it mints no rule, adds no audit surface, bumps no VERSION, and changes no observable behavior. Under the project's "deviations need an ADR" rule, mechanical routing that follows an established convention is NOT a deviation — the slice-068 (seam mint) and slice-098 (Class-A routing of the git-coupled tools) precedents both routed files onto `VAULT_ROOT` without minting per-file ADRs. So: no new ADR.

## Authorization model for this slice

N/A — internal tooling; no auth/authz surface.

## Error model for this slice

Unchanged. `project_frame_synth._read()` keeps its `except OSError → None` degrade (a missing vault file emits the existing `warn(...)` + `_(none)_`); routing does not alter which paths can fail or how. No silent fallback to a hardcoded `"architecture"` is introduced — `VAULT_ROOT` is the only source.

## AC4 / AC5 satisfaction — no new test, no new catalog row (M1, /critique)

AC4's "a regression test pins that project_frame_synth resolves via VAULT_ROOT" is satisfied by the **existing** `test_vault_root_constant.py` machinery that begins guarding `project_frame_synth.py` the moment it joins `_MIGRATION_SITE_ALLOWLIST`: `test_migration_site_allowlist_pinned` (the import must persist) + `test_no_orphan_architecture_literal_in_migrated_tools` (no hardcoded `"architecture"` path-literal may return). **No new test file is introduced**, so per the project's "add a row only if a genuinely new test is introduced" convention, **AC5 adds no new shippability row** — the existing slice-068 catalog row that runs `test_vault_root_constant.py` already covers the extended guard set. AC4's mutation non-vacuity (AP-5) is met: reverting one routed site to `"architecture"` reds `test_no_orphan_architecture_literal_in_migrated_tools` (orphan literal) **and** `test_must_rewrite_baseline_pinned` (a 5th must-rewrite reappears, drifting from `_BASELINE = ()`). Mission-brief AC4/AC5 were reworded to this effect in the same fix block (TPHD-1 / AP-17).

## Build-time checks the routing must honor (must-not-defer for /build-slice)

- **Count-literal fan-out (AP-10 / AP-13) — enumerated stale-narrative sites to repoint** (the design names these explicitly so they are not "discovered" at build):
  - `architecture/shippability.md` slice-100 row — prose "the 4 bare-`"architecture"` `/`-BinOp … sites in project_frame_synth.py classify must-rewrite" is stale post-routing.
  - `architecture/shippability.md` slice-102 row — prose "leave the production `_BASELINE` (4 `/`-BinOp sites) byte-identical" is stale (`_BASELINE` is now `()`).
  - `tools/vault_flip_readiness_audit.py:163-170` — the `_BASELINE` in-module comment "The 4 bare-'architecture' path-construction sites in project_frame_synth.py" → reword to "empty; the production must-rewrite surface was fully routed at slice-106."
  - `tests/methodology/test_vault_flip_readiness_audit.py` — `test_production_baseline_unchanged_vs_slice100` comment (covered in §"What's new" item 4).
  - Convention check for the two shippability rows: confirm whether the project edits catalog-row prose in place (slice-105 edited rows via Edit) vs treats them as append-only; if in-place editing is the norm, correct the stale prose; otherwise add the accurate statement in slice-106's own row. Resolve at build, don't guess silently.
- **m1 (FBCD-1) two-numbers-in-one-file trap**: in `test_vault_root_constant.py` the allowlist **membership** size goes 15→16 (edit the L41 comment + L291 docstring narrative that wrongly say "14"). The **test-function count** pin `assert test_count == 15` (`test_full_pytest_baseline_preserved`, ~L199) stays **15** — this slice adds **no new test function** to that module (only edits the allowlist set + comments). Do NOT reflexively bump the `==15` pin alongside the allowlist edit.
- **Shippability (RPCD-1/SCPD-1)**: per §"AC4/AC5 satisfaction" above — no new row; confirm the existing readiness-baseline rows + slice-068 allowlist row still pass post-change (the B1 test rework is what keeps them green).
- **Behavior-preservation (AC3)**: capture `python -m tools.project_frame_synth --repo-root <wt> --slice-dir <slice>` stdout before vs after; assert byte-identical. The existing `tests/methodology/test_project_frame_synth.py` fixtures are the standing guard.
- **Mutation non-vacuity (AP-5)**: reverting one routed site to `"architecture"` must red ≥1 guard (orphan-literal test + baseline-pin) — confirm live, don't assume.
