# Build checks (project-specific)

## Rules

## BC-PROJ-3 — JWT signature must be verified, not just claims

**Severity**: Critical
**Applies to**: src/auth/**/*.py
**Promoted from**: slice-014-token-refresh (2026-04-25)
**Trigger keywords**: jwt, token, refresh, auth

**Check**: When verifying a JWT, the signature MUST be checked against the issuer's public key. Decoding claims without signature verification (e.g., `jwt.decode(token, options={"verify_signature": False})`) is forbidden in production paths.

**Rationale**: A previous slice shipped with `verify_signature=False` for "testing convenience" and the flag wasn't reverted. Caught only in security review. Permanent rule.

**Validation hint**: `grep -rn "verify_signature" src/auth/ | grep -i "false"` must be empty in production paths.
