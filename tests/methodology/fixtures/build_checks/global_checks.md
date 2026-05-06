# Build checks (global — applies across all projects)

## Rules

## BC-GLOBAL-1 — All secrets via environment variables, never in code

**Severity**: Critical
**Applies to**: always: true
**Trigger keywords**: secret, password, api key, token
**Check**: No literal secret values (passwords, API keys, signing keys) in source code or committed fixtures. Use environment variables or a secrets manager.

**Rationale**: Cross-project pattern; secrets in code are a recurring AI-assist failure mode.

**Validation hint**: `git diff --cached | grep -E "(password|secret|api_key)\\s*=" -i` must return no real values.
