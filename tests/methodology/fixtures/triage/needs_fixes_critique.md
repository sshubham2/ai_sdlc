# Critique: Slice 999 example-needs-fixes

**Critic reviewed**: mission-brief.md, design.md
**Date**: 2026-05-06
**Result**: NEEDS-FIXES

## Findings

### Blockers

#### B1: Authorization claim is unsubstantiated

- **Claim under review**: design.md says "endpoint enforces authorization"
- **Issue**: design doesn't specify HOW.
- **Evidence**: design.md§endpoints
- **Proposed fix**: Add an Authorization subsection.
- **Builder draft**: ACCEPTED-PENDING — will add subsection during /build-slice

### Majors

#### M1: Thumbnail size hardcoded

- **Claim under review**: "200x200 WebP"
- **Issue**: hardcoded; no rationale.
- **Builder draft**: OVERRIDDEN — sufficient for v1; configurable in slice-027

### Minors

#### m1: Cache TTL not specified

- **Claim**: Cache for receipts.
- **Issue**: TTL unspecified.
- **Builder draft**: DEFERRED — backlog BL-014

## Dimensions checked

- [x] Unfounded assumptions — B1
- [x] Missing edge cases — none

## Triage

**Triaged by**: user
**Date**: 2026-05-06
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-PENDING | Will add Authorization subsection during build |
| M1 | Major | OVERRIDDEN | Inline auth check sufficient for v1; full RBAC in slice-027 |
| m1 | Minor | DEFERRED | Captured as backlog item BL-014 |
