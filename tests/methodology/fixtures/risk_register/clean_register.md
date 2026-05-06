# Risk register

## R1 — OCR confidence below threshold on real-world receipts

**Likelihood**: high
**Impact**: high
**Status**: open
**Reversibility**: expensive
**Mitigation**: spike-002 to validate OCR confidence calibration; fallback path planned for slice-014
**Discovered**: triage (2026-04-10)

## R2 — S3 PUT timeout at 5MB+ files

**Likelihood**: medium
**Impact**: medium
**Status**: mitigating
**Reversibility**: cheap
**Mitigation**: bumped timeout to 60s in slice-008; monitor P95 over 30 days
**Discovered**: slice-008-receipt-upload (2026-04-15)

## R3 — Token rotation invalidates active sessions

**Likelihood**: low
**Impact**: high
**Status**: retired
**Reversibility**: cheap
**Mitigation**: spike-001 confirmed graceful re-auth path
**Discovered**: triage (2026-04-10)
**Notes**: Verified across iOS Safari, Chrome desktop, and Edge.

## R4 — Multi-device sharing has stale-cache issue

**Likelihood**: low
**Impact**: low
**Status**: open
