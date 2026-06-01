# Code Review: Slice 095 harden-skill-driven-vault-writes

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths), base `5f13582`
**Date**: 2026-06-01
**Result**: FINDINGS (0 blockers, 3 majors, 4 minors — advisory in CRSI-1 v1)

## Summary
Clean, honestly-scoped wrapper CLI (`vault_edit append`) + fail-closed lexical SKILL.md audit (SVW-1), with solid path-containment, a genuinely non-vacuous concurrency proof (mutation control reliably loses 23/24 updates across 20 trials), correct count-bump/version fan-out. Append routing correct (10 routed, 11 exempted, 0 violations); cp1252/RSAD-1 met. The substantive defects are in the audit's MATCHER, not the wrapper: the directive-verb lexicon is narrow enough that the "fail-closed" claim is overstated (a real class of mutation verbs passes CLEAN), the `_verdict` route-token check is a naive line-local substring that false-CLEANs on negations/cross-refs, the exemption pin is `(file,reason)` not site granularity (weaker than design.md's M3 claim), and the fence tracker ignores tilde/blockquoted fences. None break the routed corpus today; they are latent fail-open holes a future skill edit can slip through silently — precisely the regression SVW-1 exists to prevent.

## Changed files (in-scope)
tools/vault_edit.py, tools/skill_vault_write_safety_audit.py, tools/install_audit.py, tests/methodology/{test_skill_vault_write_safety_audit,test_skill_vault_write_safety_concurrency,test_vault_root_constant,test_external_vault_adr_and_risk,test_methodology_changelog,test_pulse_worktree_resolver_tool_inventory,test_stranded_slice_audit_tool_inventory,test_utf8_stdout_regression}.py, plugin.yaml, pyproject.toml, VERSION, methodology-changelog.md, INSTALL.md, skills/{reflect,archive,reduce,repro,user-test,validate-slice,discover,risk-spike,supersede-slice,build-slice}/SKILL.md, architecture/slices/slice-095-.../build-log.md

## Findings

### Blockers (advisory in v1)
None. Shippable as-is. The audit's holes are fail-open within a narrow surface, not broken-as-built, and the design honestly scopes SVW-1 to the prose surface under a cooperative model.

### Majors

#### M1: `_verdict` route-token check is a naive line-local substring — false-CLEANs on negation / cross-reference
- **Claim**: `skill_vault_write_safety_audit.py:196` — `if any(tok in line for tok in _SAFE_ROUTE_TOKENS): return ("routed", None)` (design calls this "line-local, fail-closed").
- **Issue**: Tests only whether a route token appears as a substring anywhere on the line. Executed against the live matcher: `Append to \`architecture/risk-register.md\` raw (do NOT use tools.vault_edit append here)` → `('routed', None)` — **false CLEAN on an explicitly-raw write**. Same for "predates _vault_write" / "NOT via safe_append_text". Directly undercuts AC2's "never a silent pass."
- **Proposed fix**: Require the route token to appear AFTER the file-reference (mirror the directive-verb "must govern" rule at `:181`), and/or treat a raw-write directive + a negation (`do NOT`, `never`, `not via`, `by hand`, `directly`) as VIOLATION. Add an APED-1 negation probe to the battery.

#### M2: Directive-verb lexicon is narrow — common mutation verbs pass CLEAN, weakening the fail-closed guarantee
- **Claim**: `:82-84` — `_DIRECTIVE_VERBS = ("append","add","write","update","regenerate","edit")`. Described as "fail-closed: unclassifiable → VIOLATION" (R-7 class).
- **Issue**: Fail-closed only for the 6 listed verbs, fail-OPEN for every other. Executed, ALL return `is_mutation_site == False`: `Insert a new row into ... risk-register.md`, `Replace the recent-10 table in ... _index.md by hand`, `Log/Record/Note/Set/Mark ...`, also `put/create/amend`. `test_real_corpus_is_clean` cannot catch this by construction (corpus has no unlisted-verb raw writes). This is "the audit passes because the inputs it was tuned on are the only inputs it can see."
- **Proposed fix**: (a) expand `_DIRECTIVE_VERBS` (`insert,replace,log,record,note,set,mark,put,create,amend,prepend,modify`), OR (b) INVERT the model: any non-fenced line pairing a shared-file ref with ANY imperative requires positive safety evidence to clear (the genuinely fail-closed posture). Add APED-1 cases for ≥3 unlisted-verb raw writes asserting VIOLATION.

#### M3: Exemption allowlist pin is `(file, reason)` granularity, not site granularity — weaker than design.md's M3 claim
- **Claim**: design.md M3 — "closed allowlist of exempt **site locations** ... a free-text marker next to a genuinely-unsafe append can no longer silently green the audit."
- **Issue**: Implemented as `frozenset[tuple[str,str]]` of `(skill, reason)` pairs (`:102-115`); `registered_exemption_pairs` (`:255`) collapses 11 exemption lines to 5 pairs. A future editor can add arbitrarily many NEW `<!-- vault-write-safe: deferred-rmw -->` markers to `reflect`/`archive` (pair already listed) — including next to a genuinely-unsafe append — and `test_exemption_allowlist_pinned` will NOT trip. The M3 guarantee is not delivered at the claimed granularity.
- **Proposed fix**: Pin at `(file, line, reason)` or per-`(file,reason)` COUNT (`{("reflect","deferred-rmw"):3,...}`) so adding an N+1-th marker to an already-listed file trips the regression.

### Minors

#### m1: Fence tracker ignores tilde fences + blockquoted/indented-content fences — parity can invert
- `:117` `_FENCE_RE = r"^\s*```"` matches backtick fences only, not `~~~` (valid CommonMark) nor `> ```` `. An indented ``` ` ``` may be CONTENT of an open fence → blind toggle can invert parity → real prose treated as fenced (sites silently dropped). The `/triage` unclosed-fence bug (audit comment) confirms the model is fragile. Corpus uses only backtick fences today. Fix: `^\s*(?:```|~~~)` + track opener indent/char/length per CommonMark; add a `~~~` APED-1 case.

#### m2: `vault_edit append` accepts any in-vault path — typo silently creates a phantom vault file/dir
- `vault_edit.py:42-52` + `safe_append_text` `mkdir(parents=True)`. `--file brand/new/deep/nope.md` → rc=0, creates the tree. Containment is sound; but a `--file` typo materializes a phantom file instead of erroring. Fix: optionally require the target to already exist (exit 2 if absent — the aggregate targets all pre-exist) or a basename allowlist. Low priority (cooperative model bounds blast radius).

#### m3: `--file .` / `--file ""` resolves to the vault-root directory and is not rejected by the containment check
- `vault_edit.py:47` — `target != root` is False for `.`/`""`, so the guard doesn't fire; accepted, then `safe_append_text(<dir>)` → `IsADirectoryError ⊂ OSError` → caught at `:103` → exit 2. Fail-VISIBLE (good) but via incidental downstream error, not intentional rejection. Fix: add `target == root` (+ empty `file_arg`) to the explicit reject with an actionable message.

#### m4: Empty-content append is a silent success no-op
- `vault_edit.py:55-58`. Empty `--content-file` → rc=0, appends nothing. If an upstream step silently produced an empty temp-file, `vault_edit` reports success with no data. Acceptable (append of "" is a legit no-op) but worth a guard given the R-7 "never a silent no-op" posture. Fix: warn-to-stderr (exit 0) or exit 2 on empty content. Lowest priority.

## Dimensions checked
- [x] Unfounded assumptions — M3 (pin granularity ≠ design's "site locations"). Docstrings otherwise match impl; no phantom imports.
- [x] Missing edge cases — M2 (unlisted verbs), m1 (tilde/blockquote fences), m3 (vault-root-itself), m4 (empty content). Path-escape vectors (`..`, absolute POSIX+Windows, drive letters, mixed) all correctly REJECT — verified by execution.
- [x] Over-engineering — none (`append`-only by deliberate scope; no dead params / single-impl abstractions; `--stdin` genuinely used).
- [x] Under-engineering — M1, M2 (AC2 "never a silent pass" not fully delivered). AC1/AC3/AC4/AC5 delivered.
- [x] Contract gaps — none material. Both CLIs: docstrings + type hints + documented exit codes; `except (OSError, TimeoutError)` correctly covers `PermissionError ⊂ OSError` + lock `TimeoutError`; mutually-exclusive-required group correct.
- [x] Security — none. Cooperative data-integrity control (ADR-067); path containment sound vs traversal; no `shell=True`/`eval`/injection/secrets. m2 is a robustness footgun, not an escape.
- [x] Drift from vault — M3 (code weaker than design M3 claim). Otherwise matches design (append-only, closed enum, ADR-*.md excluded, 10 routed + 11 exempted, 0.79.0 synced, install_audit/INSTALL 36→38 consistent, archive-glob fix correct, importer-count 10→11 honest). No scope creep.
- [x] Web-known issues — `flock`/`msvcrt` over a sidecar: the per-open-file-description caveat does NOT apply (the positive concurrency test exercises the lock across distinct SUBPROCESSES, the correct cross-process scenario; threads only launch subprocesses). No finding.
- [x] Cross-cutting conformance — RSAD-1 met (both tools call `reconfigure_stdout_utf8()`; cp1252 list covers both; bespoke vault_edit cp1252 test added). APED-1 PARTIALLY met: battery covers documented FP shapes + routed/exempted/unknown-reason, but has NO case for the M1 negated-route line, the M2 unlisted-verb class, or the m1 `~~~` fence — exactly the three holes above. RSAD-1 self-application: own routed corpus passes (10 routed, 0 violations) — verified.

## Calibration note (for /reflect)
code-Critic 0B/3M/4m. Complementarity held: the design+meta Critics (B1 ADR-029 scope, B2/M-add enumeration) reasoned about the matcher's INTENT; the code-Critic EXECUTED adversarial inputs and found the matcher's fail-OPEN holes (M1 negated-route, M2 unlisted-verb, M3 pin-granularity) that the design stack + the green suite structurally cannot reach. The "execute the regex against adversarial inputs, not just the corpus" lesson (regex-APED-1 / BC-PROJ-13) recurs: my own APED-1 battery tested the documented FP shapes but not the FN-via-unlisted-verb class.
