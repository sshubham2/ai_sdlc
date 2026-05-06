# Critique report template

> **Note**: This template is also embedded inline in [`../skills/critique/SKILL.md`](../skills/critique/SKILL.md). The skill is the live source; this file is a standalone reference.

Per-slice critique from the Critic persona. Lives in `architecture/slices/slice-NNN-<name>/critique.md`.

---

## Template

```markdown
# Critique: Slice NNN <name>

**Critic reviewed**: mission-brief.md, design.md, new ADRs
**Date**: <date>
**Result**: [CLEAN | NEEDS-FIXES | BLOCKED]

## Summary

<1–2 sentences: overall assessment>

## Findings

### Blockers (must address before /build-slice)

#### B1: <short title>

- **Claim under review**: <quote from design or ADR>
- **Issue**: <what's wrong>
- **Evidence**: <vault ref / spec ref / empirical observation>
- **Proposed fix**: <concrete change>
- **Builder response**: [pending | fix applied at <ref> | disputed with rationale | deferred with risk acceptance]

#### B2: ...

### Majors (address this slice, not blocking)

#### M1: <short title>

(same structure as blockers)

### Minors (log; address if cheap)

#### m1: <short title>

(same structure)

## Dimensions checked

- [ ] Unfounded assumptions
- [ ] Missing edge cases (load, empty, network fail, concurrent, permission denied, offline)
- [ ] Over-engineering (speculative generality)
- [ ] Under-engineering (acceptance criterion without design element)
- [ ] Contract gaps (errors, pagination, auth, versioning)
- [ ] Security (input validation, authorization, secret handling, injection)
- [ ] Drift from existing vault

## No issues in dimension X

If a dimension was checked and produced nothing: explicit statement here. "Critic checked authorization paths and found no gaps because slice doesn't introduce new authz surface."

Absence of finding ≠ absence of check.
```

---

## How to use

- Populated by `/critique` (Agent invocation with adversarial prompt)
- Builder responds inline by editing the file (changes the "Builder response" line on each finding)
- Read by `/build-slice` to know what constraints the design now has
- Read by `/reflect` to score Critic accuracy (Critic calibration section in reflection)

## Worked example

```markdown
# Critique: Slice 003 add-receipt-upload

**Critic reviewed**: mission-brief.md, design.md, ADR-008-object-storage-thumbnails.md
**Date**: 2026-04-19
**Result**: NEEDS-FIXES

## Summary

Two blockers around authorization and MIME validation. Otherwise design is sound. Recommendation: address B1 + B2 before build, log m1 for next slice.

## Findings

### Blockers

#### B1: Authorization claim is unsubstantiated

- **Claim under review**: design.md says "endpoint enforces authorization"
- **Issue**: design doesn't specify HOW. Mission brief must-not-defer #1 says "only transaction owner can upload" — design needs to specify the check (DB lookup of transaction.user_id == auth_user.id).
- **Evidence**: design.md§endpoints, mission-brief.md must-not-defer #1
- **Proposed fix**: Add an "Authorization" subsection to design.md§endpoints listing the exact check.
- **Builder response**: pending

#### B2: MIME validation strategy unspecified

- **Claim under review**: ADR-008 says "validate file types"
- **Issue**: HEIC sniffing is non-trivial — `python-magic` doesn't recognize HEIC by default, must use `pyheif` for header check. ADR doesn't specify which library or approach.
- **Evidence**: ADR-008, must-not-defer #2
- **Proposed fix**: Add to ADR-008 the chosen MIME-detection approach + library + reversibility tag (cheap; can swap libs).
- **Builder response**: pending

### Majors

(none)

### Minors

#### m1: Thumbnail size is hardcoded

- **Claim**: design says "200×200 WebP"
- **Issue**: hardcoded in design; no reasoning. Other thumbnail sizes might be needed (mobile vs web). Not blocking — easy to change later.
- **Proposed fix**: Defer to next slice if mobile UI emerges.
- **Builder response**: noted

## Dimensions checked

- [x] Unfounded assumptions — found B1 (authz claim)
- [x] Missing edge cases — covered in mission brief; design matches
- [x] Over-engineering — none; thumbnail strategy is minimal
- [x] Under-engineering — found B1 + B2 (auth + MIME unspecified)
- [x] Contract gaps — checked endpoint signatures, error codes match
- [x] Security — found B1, B2, m1; recommend B1 + B2 before build
- [x] Drift from vault — checked ADR-005 alignment, no drift
```
