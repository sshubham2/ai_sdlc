# Threat model with broken references (fixture)

## TM-1 — Authentication bypass

**Severity**: critical
**Status**: mitigated
**Implementation**: src/auth/nonexistent_file.py:does_not_exist
**Mitigation**: claimed mitigation, but the referenced file doesn't exist.
