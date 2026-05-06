# Threat model (fixture)

## TM-1 — Unauthenticated access to receipts endpoint

**Severity**: high
**Status**: mitigated
**Implementation**: src/middleware/auth.py:require_auth
**Mitigation**: every receipts endpoint is wrapped in @require_auth which checks JWT signature against the issuer's public key.

## TM-2 — Token replay across regions

**Severity**: medium
**Status**: accepted
**Implementation**: n/a
**Mitigation**: accepted; SameSite=Strict cookies + short token TTL (5min) considered sufficient for the threat model. Re-evaluate if multi-region active-active becomes a goal.

## TM-3 — IDOR on transaction lookup

**Severity**: high
**Status**: open
**Implementation**:
**Mitigation**: open; planned for slice-027 (per-tenant guard).
