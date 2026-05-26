# Code Review: Slice 070 fix-psq-1-blast-radius-dict-leak

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-26
**Result**: FINDINGS (0 Blockers + 6 Majors + 5 Minors — all advisory per CRSI-1 v1 walking-skeleton; bundled to slice-071+ `bundle-066-to-070-code-critic-cleanup` candidate per voluntary-restraint precedent N=11 cumulative)

## Summary

code-Critic surfaced six Majors and five Minors against the 3 in-scope files. No Blockers. The standout catch is M1 — code-Critic argues that the worktree absolute-path leak in regenerated `architecture/slice-queue.md` cells silently re-opens the overlap-detection-correctness defect class that slice-070's own `design.md:84` calls "the more serious defect class". Builder partially disputes M1's framing (the substantive impact is theoretical today because graphify-out/ is single-source-per-process; today's `candidate_files & blast` intersection still resolves via the relative form) but ACCEPTS the underlying observation that `_build_id_to_path_map`'s `.relative_to()` fallback is fragile. M2/M3 highlight genuine cross-contract drift between `_is_path_shaped` and AC#3 regex + missing defense-in-depth on the PRIMARY id-lookup branch. M4 catches a real `lru_cache` shared-mutable foot-gun. M5/M6 are local test-quality concerns. All 11 findings deferred to slice-071+ bundle per documented v1 walking-skeleton + voluntary-restraint precedent.

## Changed files (in-scope)

```
tools/slice_queue_writer.py
tests/bugs/test_psq_1_blast_radius_dict_leak.py
architecture/slices/slice-070-fix-psq-1-blast-radius-dict-leak/build-log.md
```

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None.

### Majors

#### M1: Worktree absolute-path leak in `_build_id_to_path_map` fallback re-opens overlap-detection-silent-corruption surface (theoretical today, real under multi-graph scenarios)

- **Claim under review**: `tools/slice_queue_writer.py:257-261` `_build_id_to_path_map`'s `.relative_to(repo_root)` fallback uses bare `as_posix()` on the absolute path; `architecture/slice-queue.md` cells at 6/10 candidates carry both `C:/Users/sshub/ai_sdlc/tools/foo.py` AND `tools/foo.py` for the same file.
- **Builder partial-acknowledge**: The substantive impact is bounded today. `compute_parallel_safety` at `tools/slice_queue_writer.py:434-437` does `candidate_files & blast` where `candidate_files` comes from candidate hint_files (always repo-relative form like `tools/foo.py`) and `blast` is the union of graphify-derived + declared-files. The intersection `{"tools/foo.py"} ∩ {"tools/foo.py", "C:/.../tools/foo.py"}` is `{"tools/foo.py"}` — NON-EMPTY. So today's single-graph-source scenario still correctly resolves overlap. The silent-corruption surface code-Critic identifies is REAL but conditional: it would manifest if two active slices' blast sets came from differently-built graph instances (e.g., one worktree-built, one main-tree-built) such that the same file appears only in non-canonical-form on each side. Code-Critic's framing "the slice ships with that 'more serious defect class' intact" overstates the current-state regression but correctly flags the latent fragility.
- **Evidence**:
  - `architecture/slice-queue.md` (6/10 candidates) show mixed abs/rel forms
  - `tools/slice_queue_writer.py:434-437` overlap intersection mechanics (string equality)
  - design.md L84 (slice's own design text identifying overlap-silent-break as the more serious class)
- **Proposed fix**: In `_build_id_to_path_map` (`tools/slice_queue_writer.py:257-261`), when `.relative_to(repo_root)` raises, try alternate prefix-stripping against known-repo-parent variants (worktree path → main tree path mapping) before fallback to `as_posix()`. As a last resort, `os.path.relpath` gives a `..`-prefixed canonical form. Validate the final string with `_is_path_shaped` and drop on failure.
- **Builder draft disposition**: **DEFERRED to slice-071+ bundle** (`bundle-066-to-070-code-critic-cleanup`). Rationale: today's runtime is single-source-graphify, so the silent-corruption is latent not active. Voluntary-restraint precedent (slice-064/065/066/067/068/069/070 N=11 cumulative) supports bundling. The bundle slice will fix M1 alongside the absolute-path normalization issue noted in build-log Discovered #3.

#### M2: `_is_path_shaped` vs AC#3 regex contract drift on dotfiles + uppercase extensions + non-canonical-extension classes

- **Claim under review**: `tools/slice_queue_writer.py:212-222` `_is_path_shaped`'s `endswith((".py", ".md", ".json", ".toml", ".yaml", ".txt"))` is case-sensitive + finite. `tests/bugs/test_psq_1_blast_radius_dict_leak.py:291-295` `_PATH_SHAPED_TOKEN_RE` accepts any `.alphanum{1,8}` extension + leading-dot dotfiles. Tokens like `.gitignore`, `.env`, `file.PY`, `file.HTML`, `file.cfg`, `config.lock` pass the regex but fail `_is_path_shaped`.
- **Issue**: Wiegers IEEE 830 §4.3 internal-consistency — two functions encoding the "path-shaped" contract MUST agree. The DEVIATION that widened AC#3 didn't propagate to `_is_path_shaped`. The asymmetry is currently masked because the PRIMARY id-lookup path bypasses `_is_path_shaped` (per M3); if a future graphify schema starts emitting `.gitignore` via the dict-own-`path` key (the forward-compat branch the DEVIATION claims to have widened for), `_node_to_path` would DROP it and AC#3 would never see it.
- **Evidence**:
  - `tools/slice_queue_writer.py:212-222` — `endswith` tuple (case-sensitive + finite)
  - `tests/bugs/test_psq_1_blast_radius_dict_leak.py:291-295` — three-alternative regex
  - build-log.md DEVIATION L13-14 claims to widen for `.gitignore` but only widens validator-side
- **Proposed fix**: Replace `_is_path_shaped`'s endswith tuple with a regex (single source of truth — extract module-level constant, import in test). Add 4 unit cases pinning `.gitignore`, `.env`, `file.HTML`, `file.cfg` are accepted post-fix.
- **Builder draft disposition**: **DEFERRED to slice-071+ bundle**. Same rationale as M1 — bundled with the absolute-path normalization fix; the single-source-of-truth refactor pairs naturally with the M1 path-normalization work.

#### M3: Map-lookup PRIMARY path returns `id_to_path[nid]` unfiltered — no `_is_path_shaped` defense-in-depth

- **Claim under review**: `tools/slice_queue_writer.py:290-292`:
  ```python
  nid = node.get("id")
  if isinstance(nid, str) and nid in id_to_path:
      return id_to_path[nid]
  ```
- **Issue**: McGraw defense-in-depth — the forward-compat branch enforces `_is_path_shaped(val)` before returning; the PRIMARY branch enforces nothing. If `graph.json` carries a node with `source_file` that's a directory like `/some/dir/`, a string with no separator AND no recognizable extension (e.g., `Makefile`), or an absolute Windows path the `.relative_to` fallback couldn't normalize, the PRIMARY path returns it unfiltered. The `_build_id_to_path_map:255` guard excludes empty/non-str but allows other classes through.
- **Evidence**:
  - `tools/slice_queue_writer.py:290-292` — map lookup verbatim, no filter
  - `tools/slice_queue_writer.py:294-297` — forward-compat branch is filtered (demonstrates inconsistency)
- **Proposed fix**: Wrap return with path-shape filter; on filter-fail, fall through to dict-own-keys forward-compat. Makes the contract uniform.
- **Builder draft disposition**: **DEFERRED to slice-071+ bundle**. Bundled alongside M2 (uniform `_is_path_shaped` contract).

#### M4: `lru_cache` returns shared-by-reference mutable dict — cache-poisoning foot-gun if any caller mutates the result

- **Claim under review**: `tools/slice_queue_writer.py:225-262` `@functools.lru_cache(maxsize=4) def _build_id_to_path_map(...) -> dict[str, str]:`
- **Issue**: `functools.lru_cache` returns the same object on cache hit. Today no caller mutates, but any future "while I'm here, also memo dict-own-`path` fallbacks" optimization would poison the cache for subsequent callers in the same process. Brittle test isolation: tests sharing the same process can see leaked mutations.
- **Evidence**: `tools/slice_queue_writer.py:225` — `@functools.lru_cache(maxsize=4)` on dict-returning function; code-Critic verified shared-by-reference behavior empirically.
- **Proposed fix**: Return `types.MappingProxyType(out)` — read-only view; mutation raises. OR drop `lru_cache`, memoize manually with explicit `dict(...)` copy on read. Either tightens contract; `MappingProxyType` is simpler.
- **Builder draft disposition**: **DEFERRED to slice-071+ bundle**. Legitimate cross-cutting hardening; appropriate bundled-cleanup target.

#### M5: AC#3 live-artifact test FAILS the moment `format_queue_md` renders `` `unknown` `` cell — routine degraded state, not an SC-027 regression

- **Claim under review**: `tools/slice_queue_writer.py:499-507` `_format_entry` renders `Blast-radius: ` + `` `unknown` `` when `blast_radius` is None or empty. Token `unknown` matches none of the three AC#3 regex alternatives. Today's `architecture/slice-queue.md` happens to have zero `unknown` cells (all 10 candidates resolved against the cp'd graphify-out/), masking the fragility.
- **Issue**: AC4-(b) / AC4-(c) of slice-067's design explicitly support the `unknown` degraded state. A vault-only slice or a graphify-missing scenario would re-render `unknown` cells, and the AC#3 test would fail with a misleading "SC-027 regression" message.
- **Evidence**:
  - `tools/slice_queue_writer.py:499-507` — `unknown` sentinel render
  - `tests/bugs/test_psq_1_blast_radius_dict_leak.py:315-353` — regex doesn't except `unknown`
  - slice-067 design AC4 documents the degraded state as legitimate
- **Proposed fix**: At `tests/bugs/test_psq_1_blast_radius_dict_leak.py:340-ish`, skip `unknown` as a documented sentinel:
  ```python
  if token == "unknown":
      continue
  ```
  Add a unit test pinning `unknown` cell as not-an-offender. Alternative: change `_format_entry` to render empty-set as `*unknown*` italics (no backticks → no token extraction); wider change.
- **Builder draft disposition**: **DEFERRED to slice-071+ bundle**. Latent failure mode; today's slice-queue happens to have all-resolved candidates. The fix is a 3-LOC test-side amendment; pairs naturally with other test-quality work in the bundle.

#### M6: `patch.object(subprocess, "run", ...)` patches global `subprocess.run` for all callers — should be `patch("tools.slice_queue_writer.subprocess.run", ...)` for proper test isolation

- **Claim under review**: `tests/bugs/test_psq_1_blast_radius_dict_leak.py:98, 143, 177, 227, 263` use `patch.object(subprocess, "run", ...)`.
- **Issue**: Patching `subprocess.run` at the module-attribute level affects any code path that calls `subprocess.run` while the patch is active (e.g., transitive deps, pytest plugins). The idiomatic isolation form patches the SUT's binding: `patch("tools.slice_queue_writer.subprocess.run", ...)`. Pattern propagates by example — future tests copying this idiom inherit broader-than-intended scope.
- **Evidence**: 5 occurrences in the test file; none use the bound-via-module form.
- **Proposed fix**: Replace all 5 occurrences with `patch("tools.slice_queue_writer.subprocess.run", ...)`. No semantic change to assertions; just tightens scope.
- **Builder draft disposition**: **DEFERRED to slice-071+ bundle**. Same shape as M5 (test-quality refinement); bundle-friendly.

### Minors

#### m1: `_build_id_to_path_map.cache_clear()` never called in test setup — cross-test state-leak possible

- **Claim under review**: No `cache_clear()` in any test or conftest fixture in this slice.
- **Proposed fix**: Autouse fixture in `tests/bugs/test_psq_1_blast_radius_dict_leak.py` that calls `_build_id_to_path_map.cache_clear()` before each test.
- **Builder draft disposition**: **DEFERRED to slice-071+ bundle**. Pairs naturally with M4's lru_cache contract tightening.

#### m2: `--from` fallback retry branch at `tools/slice_queue_writer.py:323` never exercised by any test

- **Claim under review**: All 5 fake subprocess responses ignore argv — first (`--file`) call always succeeds, fallback branch dead from test perspective.
- **Proposed fix**: Add one test where `_fake_run` returns `returncode=2` on the first call and the real shape on the second. Pins the retry branch.
- **Builder draft disposition**: **DEFERRED to slice-071+ bundle**. Test-quality hardening; same shape as m1.

#### m3: build-log.md dismisses absolute-path duplication as "not a defect this slice introduced" — but `_build_id_to_path_map` IS slice-070

- **Claim under review**: `build-log.md:18`/`:81` "not a defect this slice introduced". The helper being analyzed IS slice-070 code.
- **Proposed fix**: Reword `build-log.md:18` and `:81` to "introduced by this slice's `_build_id_to_path_map` fallback path; deferred to slice-071+".
- **Builder draft disposition**: **ACCEPTED-FIXED at /reflect** (build-log honesty correction is appropriate to do at /reflect time, alongside lessons-learned write — not a code change, just prose correction).

#### m4: `_build_id_to_path_map` builds eagerly at function entry — wasted work on subprocess-failure paths

- **Claim under review**: `tools/slice_queue_writer.py:318` builds the id→path map before the subprocess call.
- **Proposed fix**: Move id_to_path build to just before the comprehensions, after JSON parse succeeds.
- **Builder draft disposition**: **DEFERRED to slice-071+ bundle**. Minor perf wart; bundle-friendly.

#### m5: `_node_to_path` forward-compat key order `("path", "source_file", "name")` is a magic tuple — easy to silently drift from docstring

- **Claim under review**: `tools/slice_queue_writer.py:294` vs docstring at `:273-275`.
- **Proposed fix**: Extract `_FORWARD_COMPAT_PATH_KEYS` module constant; reference in docstring.
- **Builder draft disposition**: **DEFERRED to slice-071+ bundle**. Cosmetic cross-doc consistency hardening.

## Dimensions checked

- [x] Unfounded assumptions — M3 (id-lookup PRIMARY trusts unvalidated map values); m3 (build-log "not a defect" claim); m5 (docstring-vs-tuple ordering)
- [x] Missing edge cases — M5 (`unknown` cell breaks AC#3); m1 (lru_cache cross-test state); m2 (`--from` retry branch untested)
- [x] Over-engineering — m4 (eager id-map build before subprocess success); no Major-class instances
- [x] Under-engineering — M1 (overlap-detection silent-corruption surface latent via abs/rel duplication)
- [x] Contract gaps — M2 (`_is_path_shaped` vs AC#3 regex disagree); M3 (PRIMARY path unfiltered); M5 (AC#3 missing `unknown` exception)
- [x] Security — none. No auth/PII boundaries; `subprocess.run` uses argv list (no shell=True / injection vector); local-only filesystem reads.
- [x] Drift from vault — none new (post-meta-Critic-sweep clean; M-add-1/2/3 already addressed all stale-precedence drift)
- [x] Web-known issues — Skipped — WebSearch not invoked. API surface (functools.lru_cache, pathlib, subprocess.run) is stdlib + stable across Python 3.10-3.13.
- [x] Cross-cutting conformance — M6 (subprocess-patching scope); M4 (lru_cache shared-mutable); EOL-DRIFT-1 not applicable (no byte-equality compares on .md content in this diff).

## Bundling note

All 11 findings (6M + 5m) deferred to slice-071+ candidate `bundle-066-to-070-code-critic-cleanup`. Cumulative bundled-cleanup backlog now stands at:
- slice-066 advisories: 6
- slice-067 advisories: 1
- slice-068 advisories: 4
- slice-069 advisories: 8
- slice-070 advisories: 11 (this review)
- **Total: 30 findings**

The bundle has crossed the "explicit /slice scope decision" threshold noted in slice-069's aggregated lessons. Recommend nominating the bundled-cleanup slice as the next slice candidate after slice-070 ships (it's already #1 in `architecture/slice-queue.md`'s ranking).

## Builder calibration note

The code-Critic stack delivered another high-signal review (N=7 cumulative slice-063 → slice-070). M1 in particular is sharply argued and identifies a real fragility (even if its current-runtime impact is bounded). The build-log's "cosmetic, deferred" framing for the absolute-path duplication was Builder-side under-engineering recognition — code-Critic correctly elevates it to a Major. Builder will tighten future build-log disposition rationale per m3's prose-honesty correction (apply at /reflect).
