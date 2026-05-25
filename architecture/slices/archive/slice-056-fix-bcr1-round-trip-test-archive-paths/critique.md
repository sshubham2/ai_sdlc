# Critique: Slice 056 fix-bcr1-round-trip-test-archive-paths

**Critic reviewed**: mission-brief.md, design.md, new ADRs (none — slice deliberately mints zero ADRs); risk-register.md R-15 entry; tests/methodology/conftest.py; tests/methodology/test_bcr_1_round_trip_end_to_end.py; tests/methodology/test_ptffd1_no_false_positive.py; tests/methodology/test_methodology_changelog.py:127-145; architecture/shippability.md row #54
**Date**: 2026-05-21
**Result**: NEEDS-FIXES

## Summary

Design is sound at the helper-shape level and the BFRD-1 failing repro is genuinely red on master (reproduced live: `AssertionError: slice-054 mission-brief.md missing at <HOME>\ai_sdlc\architecture\slices\slice-054-fix-pyproject-toml-version-drift\mission-brief.md`). However, two material issues need addressing before /build-slice: (a) the "single-witness N=1" claim that anchors the voluntary-restraint posture is empirically wrong — `tests/methodology/test_ptffd1_no_false_positive.py:70` carries the same R-15-class archive-fragile literal path (`REPO_ROOT / "architecture" / "slices" / "archive" / "slice-034-fix-tf1-audit-field-line-regex"`) and is undisclosed in the design.md L170 corpus-scan claim; this is N=2 not N=1 and the voluntary-restraint rationale needs re-grounding; (b) AC2's contract signature `_resolve_slice_dir(NNN: int) -> Path` contradicts design.md L145's permitted `_resolve_slice_dir(slice_number: int, repo_root: Path | None = None) -> Path` alternative — the Builder's Phase-A choice between these is a contract surface, not an implementation detail. Several minors around R-15 retirement preconditions, AC3 wrapped-form, and Windows glob semantics complete the review.

## Findings

### Blockers (must address before /build-slice)

None. The two material issues below are Majors, not Blockers — design is buildable with these fixes folded into the same /critique disposition pass.

### Majors (address this slice)

#### M1: "Single-witness N=1" corpus-scan claim is empirically wrong — N=2 R-15-class instances exist

- **Claim under review**: design.md L170 — "Corpus scan at design-time confirmed `test_bcr_1_round_trip_end_to_end.py:43` is the SOLE actual code-surface match (other matches in `test_branch_workflow_audit.py:60` + `test_shippability_runner_execution.py:2` are prose docstrings — not actionable)." AND mission-brief.md line 5 — "class signal N=1 → mitigating-to-retired on slice-056 ship".
- **Issue**: a fresh corpus grep for `REPO_ROOT / "architecture" / "slices"` against `tests/methodology/` returns THREE code-surface (non-docstring) hits, not one. The undisclosed third is `tests/methodology/test_ptffd1_no_false_positive.py:70`:
  ```python
  slice034 = (
      REPO_ROOT / "architecture" / "slices" / "archive"
      / "slice-034-fix-tf1-audit-field-line-regex" / "mission-brief.md"
  )
  ```
  This is structurally identical to the R-15 class (hard-coded slice-NNN-fullname path on a specific slice's archived location) — it just happens to ALREADY use the archive path. If slice-034 is ever renamed, moved, or restructured, this breaks the same way slice-054's literal broke. The design.md corpus-scan enumeration of "non-actionable" matches names `test_branch_workflow_audit.py:60` and `test_shippability_runner_execution.py:2` but omits `test_ptffd1_no_false_positive.py:46+70` — the latter is NOT a docstring; it's executable code building a Path.
- **Evidence**: live grep `REPO_ROOT / \"architecture\" / \"slices\"` against `tests/methodology/` (results: 3 hits — `test_bcr_1_round_trip_end_to_end.py:43`, `test_ptffd1_no_false_positive.py:46`, `test_ptffd1_no_false_positive.py:70`). Slice-034 archive lives at `architecture/slices/archive/slice-034-fix-tf1-audit-field-line-regex/` — confirmed by file existence. design.md L170 enumeration vs. real corpus.
- **Why this matters**: the voluntary-restraint discipline justifying zero-ADR + zero-rule rests on N=1. If N=2 today, the discipline still says "helper + tests is right" — but the design's "first-and-currently-only consumer migration" claim is false, and the choice to NOT retrofit slice-034 within this slice should be explicit. The "if N=2 emerges" framing assumes N=2 hasn't emerged yet. It has.
- **Proposed fix**: edit design.md L170 + mission-brief.md L5 + R-15 mitigation section to (1) acknowledge `test_ptffd1_no_false_positive.py:70` as the second N=2 instance; (2) explicitly decide whether to retrofit in this slice (recommended: defer with rationale — it's already archive-side, not breaking today, latent under slice-034 rename pressure only); (3) update the Out-of-scope hedge "if N=2 emerges" → "N=2 has emerged; explicit scope decision recorded".
- **Builder draft**: **ACCEPTED-FIXED** — at /critique-disposition. Applied in this round:
  - mission-brief.md "Risk retired" line: now reads "class signal **N=2** as of /critique-time corpus re-scan ... the second instance is `tests/methodology/test_ptffd1_no_false_positive.py:70` which is already on the archive side and not breaking today, latent under slice-034 rename pressure only".
  - mission-brief.md Out-of-scope: NEW bullet explicitly defers the slice-034 retrofit with rationale (a) archive-side already, NOT breaking today; (b) PTFFD-1 corpus regression test class is structurally distinct from BCR-1 input-axis invariants; (c) retrofitting expands slice scope. Nominates the slice-034 retrofit as the FUTURE slice that satisfies R-15's part-(b) retirement criterion (per m2 ACCEPTED-FIXED below).
  - design.md "Defensive / out-of-scope branches" L170: corpus-scan claim corrected to N=2; both instances enumerated; the deferred slice-034 retrofit explicitly named.

#### M2: AC2 helper-signature contract is ambiguous between two designs that differ at the public-API surface

- **Claim under review**: mission-brief AC2 — "A reusable `_resolve_slice_dir(NNN: int) -> Path` helper exists in `tests/methodology/conftest.py`". AND design.md L62-65 (same signature). AND design.md L145 — "Alternative (decided at build-time): if monkeypatching `REPO_ROOT` proves awkward..., the helper can accept an optional `repo_root: Path | None = None` parameter (default `None` → use module-level `REPO_ROOT`). The Builder picks at /build-slice Phase A. EITHER approach satisfies AC2".
- **Issue**: AC2 pins the signature literally as `_resolve_slice_dir(NNN: int) -> Path`. Design.md L145 permits an alternative signature `_resolve_slice_dir(NNN: int, repo_root: Path | None = None) -> Path`. These are NOT signature-equivalent — one has arity 1, the other has arity 2. AC2's wording does not encompass both. Per Newman / Fielding contract-stability: a public test helper imported by other test modules has its arity as part of its contract. The design treats this as an implementation detail it is not.
- **Evidence**: mission-brief.md AC2 + design.md L62-65 + design.md L145 (alternative).
- **Why this matters**: at /build-slice the Builder will pick one. If pick = 1-arg, the AC4b active-branch test must monkeypatch `tests.methodology.conftest.REPO_ROOT` AND the helper must read `REPO_ROOT` at function-call-time. If pick = 2-arg, the AC4b test passes `repo_root=tmp_path` explicitly. The Builder may pick differently from what the /critique stack reviewed.
- **Proposed fix**: settle the signature at /critique-disposition time. Recommended pick: 1-arg with module-globals read at call-time (Python's natural binding makes monkeypatch work). Update design.md L145 to remove the "Builder picks at Phase A" optionality and pin the 1-arg form.
- **Builder draft**: **ACCEPTED-FIXED** — at /critique-disposition. Applied in this round:
  - mission-brief.md AC2: now explicitly pins single-arg `(slice_number: int) -> Path` (per /critique M2 ACCEPTED-FIXED); helper reads `REPO_ROOT` at function-call-time via module-globals (Python's natural binding) so `monkeypatch.setattr` works for AC4b.
  - design.md helper signature block: 1-arg form pinned; "no 2-arg `repo_root` variant" explicitly stated; docstring carries the call-time-binding semantics + the rejected-2-arg-alternative rationale.
  - design.md "Helper-test fixture choices" L145: prior "Builder picks at /build-slice Phase A" alternative REMOVED + REJECTED rationale recorded (AC2 literal contract + KISS + avoid future-drift on a kwarg).

### Minors (log; address if cheap)

#### m1: AC3 structural-pin claim has a contract-vs-evidence asymmetry the design partially defuses but doesn't fully reconcile

- **Claim under review**: mission-brief AC3 — "`SLICE_054_DIR` removal is structural evidence of the fix"; design.md L154 — "the test pins absence of the LITERAL-PATH form, not absence of the constant name"; design.md L46 — "`SLICE_054_DIR` constant DELETED (or — equivalent — replaced by `SLICE_054_DIR = _resolve_slice_dir(54)` to preserve any local literal references; choose the cleaner option at build-time)".
- **Issue**: AC3 says SLICE_054_DIR REMOVAL is the structural evidence. Design.md L46 + L154 permit retaining `SLICE_054_DIR = _resolve_slice_dir(54)`. The AC3 prose "SLICE_054_DIR removal" is misleading in isolation; a downstream reader could legitimately interpret it as "the symbol must be gone".
- **Evidence**: mission-brief.md AC3 vs verification-plan row 3 vs design.md L46+154.
- **Proposed fix**: harmonize AC3's wording to "the archive-fragile literal-path RHS is removed from `SLICE_054_DIR`'s definition (or `SLICE_054_DIR` is removed entirely); the test pins absence of the literal `REPO_ROOT / "architecture" / "slices" / "slice-054` substring".
- **Builder draft**: **ACCEPTED-FIXED** — at /critique-disposition. Applied in this round:
  - mission-brief.md AC3: rewritten to explicitly name the archive-fragile literal-path RHS as the target of removal; both equivalent forms (a) symbol removed + helper called inline, (b) symbol retained as `SLICE_054_DIR = _resolve_slice_dir(54)` accepted; structural pin asserts absence of the literal substring `REPO_ROOT / "architecture" / "slices" / "slice-054`, NOT absence of the symbol name.
  - mission-brief.md verification-plan row 3: rewritten to assert via `grep -F` on the archive-fragile literal substring (not the symbol name).
  - design.md AC3 test design: harmonized with same wording.

#### m2: R-15 retirement criteria in risk-register.md L259 are NOT fully met by this slice alone

- **Claim under review**: mission-brief L5 — "R-15 (archive-aware vault-test discipline; class signal N=1 → mitigating-to-retired on slice-056 ship)"; pre-finish gate L100 — "R-15 transition: `architecture/risk-register.md` R-15 entry has `**Status**: retired`".
- **Issue**: the R-15 entry in `architecture/risk-register.md:259` explicitly states the retirement gate is TWO-part: "Status escalates to `retired` when (a) slice-056 ships the fix + the resolver helper AND (b) a future slice authoring a similar vault-pin test demonstrably uses the helper (positive evidence the discipline propagated)." Part (b) cannot be satisfied by this slice — by definition it requires a SUBSEQUENT slice to demonstrably use the helper. The mission-brief's "mitigating-to-retired on slice-056 ship" wording elides this.
- **Evidence**: risk-register.md L259.
- **Proposed fix**: preserve R-15 as `mitigating` after this slice ships, with an updated `**Mitigation**:` line recording slice-056 as part (a); flip to `retired` in the next slice that demonstrably uses `_resolve_slice_dir` (probably the slice-034 retrofit per M1 deferral).
- **Builder draft**: **ACCEPTED-FIXED** — at /critique-disposition. Applied in this round:
  - mission-brief.md "Risk retired" line: rewritten to record R-15 STAYS `mitigating` after slice-056 ships; part-(a) DONE / part-(b) pending future slice.
  - mission-brief.md pre-finish gate "R-15 transition" item: now says R-15 entry STAYS `**Status**: mitigating` (NOT `retired`); `**Mitigation**:` line updated to record part-(a) DONE; flip to `retired` in the future slice that satisfies part-(b).
  - design.md "What's new" R-15 mutation bullet: rewritten to reflect `mitigating` stays (NOT `mitigating → retired`); explicitly cites m2 path-(i) choice over path-(ii).

#### m3: AC5 shippability row #56 — slice-054 row #54 also depends on this fix, but the slice doesn't claim it

- **Claim under review**: design.md L22 — "Repointing it makes shippability row #54 PASS again ... currently FAILs slice-055-innocently on master"; pre-finish gate — "row 56 PASS; slice-054 row #54 — which cites this same test — also PASS-flipped from FAIL by this fix".
- **Issue**: this is correctly noted in the pre-finish gate, but the AC5 wording in mission-brief.md and AC enumeration says only "the shippability catalog adds row #56". The verification plan row 5 only checks row #56. Row #54 PASS-flip is load-bearing but unstated in AC5.
- **Evidence**: shippability.md L64 (row #54) vs. mission-brief AC5 vs. verification-plan row 5.
- **Proposed fix**: extend AC5 to claim row #54 also PASS-flips from FAIL to PASS post-fix; add verification-plan row 5b.
- **Builder draft**: **ACCEPTED-FIXED** — at /critique-disposition. Applied in this round:
  - mission-brief.md AC5: now claims "shippability row #54 (which already cites the same BCR-1 test) PASS-flips from FAIL to PASS post-fix as a side effect — row #54's continued PASS is itself part of the regression contract".
  - mission-brief.md verification-plan: NEW row 5b explicitly verifies row #54 PASSes during the same runner invocation as row 5.

#### m4: Helper docstring + diagnostic-message contract — diagnostic message format is honour-system, not test-enforced strictly enough

- **Claim under review**: design.md L88 AssertionError format; AC4c assertion that both glob patterns appear as forward-slash substrings.
- **Issue**: `pathlib.Path.__str__` on Windows produces backslash-separated text. If the helper formats glob patterns via `str(Path(...))`, the AC4c forward-slash substring assertion will FAIL on Windows. The design REASONS about format; it doesn't EXECUTE format.
- **Evidence**: design.md L88 + L149-150 + Windows `WindowsPath` behavior.
- **Proposed fix**: helper formats glob patterns as raw f-strings (no `Path` round-trip); test asserts forward-slash literals; design-time dry-run check: `python -c "print(f'architecture/slices/slice-{0:03d}-*')"` produces `architecture/slices/slice-000-*`.
- **Builder draft**: **ACCEPTED-FIXED** — at /critique-disposition. Applied in this round:
  - mission-brief.md AC2: now explicitly pins "diagnostic-message format is platform-neutral ... glob patterns are formatted as raw forward-slash strings (`f\"architecture/slices/slice-{n:03d}-*\"`), not via `str(Path(...))`".
  - design.md helper resolution algorithm: NEW "Diagnostic-message format pin" section showing the literal f-string template + warning against `str(Path(...))` formatting + design-time dry-run check verifying the forward-slash format.
  - design.md AC4c test design: rewritten to explicitly cite "FORWARD-SLASH strings" in the substring assertion + reference the helper's no-Path-round-trip format pin.

#### m5: `pathlib.Path.glob` on Windows is case-INSENSITIVE — design treats this as a non-issue but doesn't verify

- **Claim under review**: design.md L25/L89 — pathlib glob usage without case-sensitivity acknowledgment.
- **Issue**: `Path.glob` is case-insensitive on Windows (NTFS), case-sensitive on POSIX. Latent issue if folder casing varies cross-platform. BRANCH-1 enforces lowercase, so this delta is theoretical; the design should document.
- **Evidence**: Python docs `pathlib.PurePath.match`; well-known platform delta.
- **Proposed fix**: 2-line note in design.md acknowledging platform delta + BRANCH-1 mitigation.
- **Builder draft**: **ACCEPTED-FIXED** — at /critique-disposition. Applied in this round:
  - design.md helper resolution algorithm: NEW "Cross-platform glob semantics note" appended after the diagnostic-message format pin, citing the Windows-NTFS vs POSIX delta + the BRANCH-1 lowercase enforcement that keeps the delta latent.

#### m6: MEPD-1(b) discharge by name is correctly grounded against META-1 — verification only, no action

- **Claim under review**: design.md L114 "Verified against the real META-1 enforcing assertion at `tests/methodology/test_methodology_changelog.py:136`".
- **Issue**: none — Critic verified the citation is accurate. Listed for completeness.
- **Evidence**: live read of test_methodology_changelog.py L127-145 confirms the `re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", ...)` at L136 + MEPD-1(b) discharge semantics.
- **Proposed fix**: none.
- **Builder draft**: **ACCEPTED-FIXED** — informational; no design change needed. Recorded for the disposition table.

## Dimensions checked

- [x] **Unfounded assumptions** — M1 (single-witness N=1 wrong; N=2); m4 (diagnostic format reasoned, not executed); m6 (MEPD-1(b) grounding verified correct)
- [x] **Missing edge cases** — m5 (Windows-vs-POSIX glob case sensitivity); range-checks + neither-found covered
- [x] **Over-engineering** — none (helper is single-purpose, minimal, voluntary-restraint applied)
- [x] **Under-engineering** — M2 (signature contract ambiguity); m1 (AC3 prose-vs-evidence asymmetry); m3 (row #54 PASS-flip uncited)
- [x] **Contract gaps** — M2 (arity 1 vs 2); m4 (diagnostic message format)
- [x] **Security** — none (bounded int input, no network/DB/I/O surface, no path-traversal exposure)
- [x] **Drift from vault** — m2 (R-15 retirement criteria contradiction with risk-register.md:259)
- [x] **Web-known issues** — m5 (pathlib glob case sensitivity)
- [x] **Cross-cutting conformance** — M1 (corpus-scan vs implementation parity); m4 (APED-1 audit-parse empirical-execution); FBCD-1 multi-site fix propagation applied (mission-brief + design.md harmonized in same fix block per TPHD-1 sub-mode (a))

## Triage

**Triaged by**: user
**Date**: 2026-05-21
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | mission-brief.md "Risk retired" + Out-of-scope + design.md "Defensive / out-of-scope branches" updated: N=2 corpus re-scan recorded (second instance `tests/methodology/test_ptffd1_no_false_positive.py:70`); slice-034 retrofit explicitly DEFERRED with rationale (archive-side already, PTFFD-1 class structurally distinct, scope-expansion); slice-034 retrofit nominated as FUTURE slice satisfying R-15 part-(b) retirement criterion |
| M2 | Major | ACCEPTED-FIXED | mission-brief AC2 + design.md helper signature block + design.md "Helper-test fixture choices" L145 updated: 1-arg signature `(slice_number: int) -> Path` PINNED; helper reads `REPO_ROOT` at function-call-time via module-globals (Python natural binding) so `monkeypatch.setattr` works for AC4b; 2-arg `repo_root: Path | None = None` alternative EXPLICITLY REJECTED with rationale (AC2 literal contract + KISS + avoid future-drift on a kwarg) |
| m1 | Minor | ACCEPTED-FIXED | mission-brief AC3 + verification-plan row 3 + design.md AC3 test design harmonized: structural pin asserts absence of LITERAL substring `REPO_ROOT / "architecture" / "slices" / "slice-054`, NOT absence of `SLICE_054_DIR` symbol name; wrapped form `SLICE_054_DIR = _resolve_slice_dir(54)` ACCEPTED |
| m2 | Minor | ACCEPTED-FIXED | mission-brief "Risk retired" + pre-finish gate + design.md "What's new" R-15 mutation bullet updated: R-15 STAYS `mitigating` after slice-056 ships (NOT `retired`); part-(a) of risk-register.md:259 retirement gate DONE; part-(b) pending future slice (likely slice-034 retrofit) per the safer-dogfood-of-the-R-15-entry path-(i) over override-precondition path-(ii) |
| m3 | Minor | ACCEPTED-FIXED | mission-brief AC5 + verification-plan row 5b added: row #54 PASS-flip from FAIL to PASS post-fix claimed as part of regression contract; both rows verified in same shippability-runner invocation at /validate-slice |
| m4 | Minor | ACCEPTED-FIXED | mission-brief AC2 + design.md helper resolution algorithm "Diagnostic-message format pin" + design.md AC4c test design updated: glob patterns formatted as raw forward-slash f-strings `f"architecture/slices/slice-{n:03d}-*"` (NOT `str(Path(...))` which backslashes on Windows); AC4c assertion: substring check on FORWARD-SLASH literals; design-time dry-run check documented. (Meta-Critic m4 severity-escalation suggestion to Major LEFT AS MINOR per meta-Critic's own recommendation — first-Critic calibration sound.) |
| m5 | Minor | ACCEPTED-FIXED | design.md helper resolution algorithm "Cross-platform glob semantics note" added: 2-line acknowledgment of pathlib `Path.glob` Windows-NTFS-case-insensitive vs POSIX-case-sensitive delta + BRANCH-1 lowercase folder naming mitigation |
| m6 | Informational | ACCEPTED-FIXED | META-1 grounding verified — `re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", ...)` confirmed at `tests/methodology/test_methodology_changelog.py:136`; MEPD-1(b) discharge correctly grounded; no design change needed |
| M-add-1 | Major | ACCEPTED-FIXED | (meta-Critic missed finding) TF-1 strict-pre-finish gate WILL fail pre-fix (`ac-without-row AC#4`, verified empirically). Fix: mission-brief TF-1 plan table AC cells `4a/4b/4c` → plain `4` (multi-row-per-AC canonical shape — `rows_by_ac["4"]` accumulates as a list); test-function names retain sub-branch disambiguation; notes block documents `_AC_ITEM_RE = r"^\s*(\d+)\.\s+\S"` integer-only constraint. design.md "Components touched" / "Test design" updated to `(AC4 row N)` references. Post-fix verified: `$PY -m tools.test_first_audit ...` reports CLEAN (8 rows). (Meta-Critic option (a) recommendation to split body AC4 into `4a./4b./4c.` would NOT have worked at the regex layer — Builder verified empirically + chose the canonical multi-row-per-AC path.) |
| M-add-2 | Major | ACCEPTED-FIXED | (meta-Critic missed finding) corpus class-closure backstop added: mission-brief AC4 expanded from 3 to 4 helper regression tests; new test `test_no_new_archive_fragile_literals_in_methodology_corpus` greps `tests/methodology/*.py` for `REPO_ROOT / "architecture" / "slices" / ("archive" / )?"slice-\d{3}-` literal-path-RHS, asserts subset of whitelist `{tests/methodology/test_ptffd1_no_false_positive.py:70}`. Whitelist-shrinkage on slice-034 retrofit = structural mechanism for R-15 part-(b) retirement. TF-1 plan adds row 4 (AC=`4`) for the new test; design.md "Components touched" + "Helper-test fixture choices" sections updated with full test specification. |
| M-add-3 | Minor | ACCEPTED-FIXED | (meta-Critic missed finding) mission-brief.md Pipeline-position predecessor `/reflect` → `/commit-slice (canonical chain per PCA-1 tools/pipeline_chain_audit.py:80-81)`. design.md Pipeline-position predecessor `/slice` already correct. Internal-doc-fidelity fix; not gated by `pipeline_chain_audit.py` (which scans `skills/*/SKILL.md` only). |
