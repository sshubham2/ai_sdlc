# Build checks (project-specific)

## Rules

## BC-PROJ-1 — Every endpoint must have an authentication test

**Severity**: Critical
**Applies to**: always: true
**Promoted from**: slice-005-auth-rework (2026-04-12)
**Trigger keywords**: endpoint, route, api

**Check**: For every endpoint added or modified, there must be at least one test that exercises the unauthenticated path and asserts a 401 response.

**Rationale**: Twice in the project's history an endpoint was shipped without auth coverage and the gap was caught only in production. Always-on guard.

**Validation hint**: Run `pytest -k "unauthenticated or no_auth"` on the test paths added by this slice.
