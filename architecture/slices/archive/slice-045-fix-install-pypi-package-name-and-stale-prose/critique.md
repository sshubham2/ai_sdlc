# Critique: Slice 045 fix-install-pypi-package-name-and-stale-prose

**Critic reviewed**: mission-brief.md, design.md (no new ADRs)
**Date**: 2026-05-18
**Result**: CLEAN (first-Critic pre-triage verdict NEEDS-FIXES; meta-Critic DR-1 ACCEPT; user-ratified final verdict CLEAN at TRI-1)

## Summary

The slice's three core factual premises are all verified-correct against live files and the live PyPI registry: `INSTALL.md:93` is genuinely the only bare `pip install graphify`, `graphifyy` is the real published distribution, the four `v0.20.0` occurrences and two `13`-tool claims are exactly as enumerated, and the repro regexes behave precisely as the design claims (Critic empirically executed them). The design is sound in substance. One Major: the MEPD-1 methodology-surface obligation was not discharged by name and the precedent was mis-cited to the wrong canonical surface. Two minors around a scope-boundary asymmetry and an AC4 wording gap.

## Findings

### Blockers (must address before /build-slice)

None.

### Majors (address this slice)

#### M1: MEPD-1 not discharged by name; precedent mis-cited to reflection.md instead of risk-register.md
- **Claim under review**: design.md — "ADRs: none (prose-only, no-VERSION-bump, slice-040/R-10 precedent: risk-retirement recorded in reflection.md not changelog)."
- **Issue**: INSTALL.md is the INST-1 install recipe — an in-house methodology surface — and this slice changes its behaviour. Per the MEPD-1 Dim-7 obligation, a behaviour-changing methodology-surface slice must discharge EXACTLY ONE branch and say which. This is a no-VERSION-bump conformance fix → branch (b) applies, but the design (i) never invoked MEPD-1 by name, and (ii) mis-stated the precedent: the slice-040/R-10 + slice-036/R-9 precedent-faithful surface for a no-VERSION-bump conformance-fix retirement is the **`risk-register.md` `**Retired**:` line**, NOT reflection.md. The design said "recorded in reflection.md" and the mission-brief said "No risk-register entry" → the retirement was recorded on *no* canonical surface.
- **Evidence**: `architecture/slices/archive/slice-040-realign-validate-slice-step-5-5-prose-pin/reflection.md:40,43`; mission-brief.md "Risk retired: No risk-register entry"; `tests/methodology/test_methodology_changelog.py:136` (META-1 `re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", ...)` — a parentless `###` would orphan-split; the no-changelog instinct is correct, only the discharge framing was missing).
- **Proposed fix**: Name MEPD-1(b); state the META-1 orphan-split rationale verified against the real assertion; record the retirement on the canonical risk-register surface (or explicitly justify no entry).
- **Builder draft**: **ACCEPTED-FIXED** — (1) design.md "Decisions made (ADRs)" now carries an explicit **MEPD-1(b) discharge** sub-section naming the rule, the META-1 `test_methodology_changelog.py:136` rationale, and no-PMI-1-bump; (2) added **R-11** to `architecture/risk-register.md` (born-retired this slice, RR-1-clean: `risk_register_audit --filter-status retired` → R-11 present, total 11, retired 8, 0 violations) as the canonical retirement surface; (3) harmonized mission-brief "Risk retired" line to `[[risk-register#R-11]]` (TPHD-1). Precedent now correctly cited to risk-register, not reflection.md.

### Minors (log; address if cheap)

#### m1: install_audit.py code still says "v0.20.0" — INSTALL.md:232 reword must not assert currency
- **Claim under review**: design.md EDIT-2 — INSTALL.md:232 → "drift from the current canonical inventory"; `install_audit.py` inventory refactor is Out of scope.
- **Issue**: `tools/install_audit.py:4,8,42` still hardcodes `v0.20.0`; the original :232 sentence is in fact still accurate about the code's frozen inventory. Rewording to "current canonical inventory" makes the doc *vaguer than and over-claiming vs* the code's actual (non-current) state — violates brownfield "code is truth".
- **Evidence**: `tools/install_audit.py:4,8,42`; INSTALL.md:232.
- **Proposed fix**: Reword :232 to drop the literal *without* asserting currency (e.g. "The audit reports any drift from its canonical inventory.").
- **Builder draft**: **ACCEPTED-FIXED** — design.md EDIT-2 table row for :232 updated to the no-literal, no-"current" phrasing "The audit reports any drift from its canonical inventory." with the m1 rationale cited inline.

#### m2: AC4 targets are prose, not pip commands — pin the exact resulting phrase
- **Claim under review**: AC4 / EDIT-4 — README.md:69 + tutorial HTML:1050 "else PyPI" → name `graphifyy`.
- **Issue**: Both targets are prose; "name `graphifyy`" is under-specified and a sloppy reword is invisible to shippability #45 (test reads only INSTALL.md, `test_install_md_correctness.py:32-38`).
- **Evidence**: README.md:69; `tutorial-site/Hybrid AI SDLC Pipeline.html:1050`; test reads `INSTALL_MD` only.
- **Proposed fix**: Specify the exact resulting phrase for both sites.
- **Builder draft**: **ACCEPTED-FIXED** — design.md EDIT-4 now pins the exact phrase: `…if present, else the \`graphifyy\` PyPI package)` for both README.md:69 and the HTML line (markup style preserved on the HTML line), with the m2 rationale and the test-blind-spot note inline.

## Dimensions checked
- [x] Unfounded assumptions — none (Critic empirically verified all factual claims against live files: INSTALL.md:93-only-bare ✓, 4×v0.20.0 ✓, 2×"13" ✓, plugin.yaml=25 ✓, repro regex behaviour executed ✓)
- [x] Missing edge cases — none material (mid-slice smoke correctly placed; `graphify(?!y)` would catch `graphify[` but no such occurrence exists — noted, not a finding)
- [x] Over-engineering — none (EDIT-3 structural-guard-not-templating is the correct call for static markdown)
- [x] Under-engineering — none (every AC maps to a concrete EDIT; TF-1 3 repro tests catalogued #45)
- [x] Contract gaps — none (no new endpoint/event; graphify module/CLI name verified unchanged)
- [x] Security — none (docs-only; the package-name fix *improves* posture — removes a typosquat vector)
- [x] Drift from vault — M1 (MEPD-1/precedent surface) + m1 (INSTALL.md:232 vs still-v0.20.0 code); both fixed
- [x] Web-known issues — verified `graphifyy` is the live official PyPI distribution (double-y), CLI stays `graphify`, Python 3.10+, extras `graphifyy[video]`. Pre-existing INSTALL.md:71 "Python 3.11+" vs official "3.10+" mismatch noted by Critic but out of scope / not introduced by this slice — not filed.
- [x] Cross-cutting conformance — MEPD-1 → M1 (Dim-7 separate pass); sibling-test conformance checked clear (`test_install_audit.py:247-289` prose pins survive EDIT-1/EDIT-2); shippability #45 consumer reference verified present + executable (SCPD-1/PTFCD-1)

## Triage

**Triaged by**: user
**Date**: 2026-05-18
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major    | ACCEPTED-FIXED | MEPD-1(b) discharge added to design.md + R-11 born-retired in risk-register.md (RR-1-clean) + mission-brief harmonized; precedent corrected to risk-register surface. Meta-Critic DR-1: VALID. User-ratified 2026-05-18. |
| m1 | Minor    | ACCEPTED-FIXED | design.md EDIT-2 :232 reworded to drop literal without asserting currency (respects install_audit.py still-frozen code). Meta-Critic DR-1: VALID. User-ratified 2026-05-18. |
| m2 | Minor    | ACCEPTED-FIXED | design.md EDIT-4 exact resulting phrase pinned for both README:69 + HTML:1050. Meta-Critic DR-1: VALID. User-ratified 2026-05-18. |
