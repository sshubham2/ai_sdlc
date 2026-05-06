# Build checks (project-specific)

## Rules

## BC-PROJ-6 — Always-applicable rule

**Severity**: Important
**Applies to**: always: true
**Check**: Always applies regardless of file types touched.

## BC-PROJ-7 — Glob-only rule

**Severity**: Critical
**Applies to**: src/payments/**
**Trigger keywords**:
**Check**: Applies only when payment-path files are modified.

## BC-PROJ-8 — Keyword-only rule

**Severity**: Important
**Applies to**:
**Trigger keywords**: migration, schema, alembic
**Check**: Applies only when slice mentions migrations/schema in mission brief.
