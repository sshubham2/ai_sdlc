---
name: reduce
description: "AI SDLC maintenance. Complexity budget enforcer. Audits vault + code for over-engineering, speculative generality, dead claims. Proposes a simplification slice. Use when vault exceeds component count threshold, before major releases, or when complexity feels off. Trigger phrases: '/reduce', 'reduce complexity', 'simplify the design', 'check for over-engineering', 'complexity audit'."
user_invokable: true
argument-hint: [--force]
---

# /reduce — Complexity Budget Enforcer

You audit the vault and code for over-engineering, then propose a simplification slice. AI has no natural bias toward "less" — left alone, specs grow, components proliferate, abstractions accumulate. This skill is the counterweight.

## Where this fits

Maintenance skill. Runs:
- When vault exceeds component count threshold (auto-suggested by `/reflect`)
- Before major releases as a cleanup pass
- When `/drift-log` accumulates >5 unresolved entries
- Periodically in Heavy mode (every ~5 slices)
- On-demand when complexity feels off

## Argument modes

- `/reduce` — audit + suggestions (no commitment)
- `/reduce --force` — proceed to a mandatory simplification slice (skip "are you sure")

## Your task

### Step 1: Determine thresholds for this project

Read `architecture/triage.md` for mode. Apply mode-specific thresholds:

| Mode | Component cap | Contract cap | ADR cap | Files / total cap |
|------|--------------|--------------|---------|-------------------|
| Minimal | 8 | 10 | 15 | ~50 |
| Standard | 15 | 25 | 30 | ~100 |
| Heavy | 25 | 50 | 60 | ~200 |

### Step 2: Measure current complexity

Vault metrics:
- Component file count
- Contract count
- ADR count (vs. how many are referenced elsewhere)
- Total vault file count
- Average wikilinks per file (low = islands; high = healthy graph)

Code metrics (use $PY -m graphify code if available):
- Source file count
- Average file length
- Max function length
- Dependency depth

### Step 3: Identify reduction candidates

Use graphify for systematic detection:

```bash
# Orphans — nodes with no inbound edges (possibly dead)
$PY -m graphify orphans

# God nodes (highest in/out degree) — read GRAPH_REPORT.md, the build already lists them
cat graphify-out/GRAPH_REPORT.md | head -60

# Layer-cake detection — shortest path between caller and implementation
# (CLI lacks `path`; use graphify-as-library)
$PY -c "
import json, networkx as nx
G = nx.node_link_graph(json.load(open('graphify-out/graph.json')), edges='links')
try:
    p = nx.shortest_path(G, '<external-caller>', '<actual-implementation>')
    print(' -> '.join(p), f'({len(p)-1} hops)')
except Exception as e: print(f'no path: {e}')
"
# If the path passes through layers that just forward without added logic: candidate for inlining
```

Then walk the vault + code looking for:

- **Components with <50 lines of doc + <100 lines of impl** → consolidate?
- **ADRs never referenced after creation** (`grep -r "ADR-NNN" architecture/` returns only the ADR itself) → obsolete?
- **Contracts with single caller** (graph shows 1 inbound edge) → inline?
- **Speculative interfaces** (1 implementation, 1 caller, abstracted "for flexibility") — graphify shows `interface → 1 impl → 1 caller` = over-engineered
- **Configuration sprawl** (env vars / settings / flags that nothing reads — orphan config nodes in graph)
- **Dead vault entries** (components removed from code but doc still exists — vault node with no code-side counterpart)
- **Layer-cake** (pass-through layers that add no value)
- **Premature ADRs** (decisions documented for trivial choices like naming convention)
- **Duplicated patterns** across slices (sparingly — three similar files is OK)

### Step 4: Tag candidates by severity

- **Reduce now** — clear win, no risk
- **Reduce next slice** — needs a small refactor
- **Watch** — at threshold; if grows further, reduce

### Step 5: Present audit

Show the user:

```
Complexity audit (mode: Standard)

Current:
- Components: 18 (cap 15) — OVER
- Contracts: 22 (cap 25) — OK
- ADRs: 28 (cap 30) — OK
- Total files: 87 (cap 100) — OK

Reduction candidates:

REDUCE NOW (clear wins):
1. components/notification-old.md — sendgrid migration done in slice-008; no longer used. Delete.
2. ADR-012 ("use kebab-case for filenames") — not load-bearing, no future variation expected. Delete.
3. components/cache-wrapper.md + components/cache.md — wrapper adds nothing. Inline into cache.

REDUCE NEXT SLICE (refactor needed):
4. contracts/notification-internal.md — single caller (NotificationDispatcher). Inline.

WATCH:
5. ADR count climbing fast — 6 added in last 3 slices. Pattern: ADRs for non-decisions. Tighten.
```

### Step 6: User decides

Without `--force`: ask user which reductions to take. Wait for selection.

With `--force`: proceed with all "REDUCE NOW" items as a slice.

### Step 7: If user agrees, propose a reduction slice

Treat the reductions as a normal slice. Run through `/slice → /design-slice → /critique → /build-slice → /validate-slice → /reflect`.

Mission brief acceptance criteria for a reduction slice are typically:
- Files X, Y, Z deleted (with justification per file)
- Components A and B merged
- Code paths C and D inlined
- All tests still pass after reductions
- No external behavior change (backward-compat preserved)

### Step 8: Append to lessons-learned.md

After the reduction slice, note the pattern that led to the over-engineering. Helps future slices avoid it.

## Critical rules

- DO NOT extract abstractions for hypothetical reuse. Three similar files is better than premature abstraction.
- DO NOT rename for cosmetic consistency. Rename has cost.
- DO NOT collapse components with different responsibilities just because they're small.
- DO NOT touch code that isn't hurting. Old code that works is asset, not debt.
- DO catch speculative generality, dead vault entries, configuration sprawl, layer-cake.
- USE `--force` carefully. It's for confidence cases (clear deletes), not "decide for me."

## Anti-patterns to specifically catch

| Pattern | Why it's bad |
|---------|--------------|
| Single-implementation interface | Abstract for no benefit |
| Single-product factory | YAGNI |
| Single-plugin plugin system | YAGNI++ |
| ADR for naming convention | Not a decision worth recording |
| Pass-through service ("UserServiceWrapper" wrapping UserService) | Adds layer, no value |
| Config flags never overridden | Inline the value |

## Healthy patterns to LEAVE ALONE

- Three similar slice folders — they may genuinely be separate concerns
- Two components with similar responsibilities — they may have different consumers / SLAs
- Multiple ADRs in same area — historical record is valuable

## Heavy mode adjustment

In Heavy mode, run `/reduce` at minimum every 5 slices (scheduled by `/triage`). Compliance environments accumulate complexity faster (audit trails, sign-offs, redundant checks) — periodic reduction is essential.

## Fork-friendly execution

Reduction audits scale with codebase + vault size. On larger projects (Standard ~80–100 files, Heavy ~200+) the graphify queries (god-node detection, orphan detection, layer-cake paths) plus the per-candidate review can take real time. Forking keeps the user moving while the audit runs.

**Requires** `CLAUDE_CODE_FORK_SUBAGENT=1` (Claude Code v2.1.117+). Forks inherit the parent conversation in full, run in the background, and report back when the audit is complete.

**When to fork**:
- **Pre-release / pre-audit cleanup** — run `/reduce` in the background before a milestone; review findings when ready
- **Heavy mode every-5-slices cadence** — kick it off automatically while continuing the next slice; receive the audit later
- **Large codebases** — Standard mode at 100+ files or Heavy at 200+; the graph traversal benefits from not blocking the main thread
- **Re-audit after a `--force` reduction slice ships** — verify the reduction worked without pausing the next slice

**When NOT to fork**:
- Small project (Minimal mode, <50 files) — audit is fast enough to run inline
- You want to make reduction decisions interactively as findings come in (some users prefer this)
- Fork env var not enabled — runs in main thread as usual

**Invocation**:

```
/fork /reduce
/fork /reduce --force
```

The fork sees the full vault, the graph, all ADRs, and recent slice history. The audit it produces is the same as a main-thread run; only the execution context differs.

**Note on `--force`**: forking a `--force` reduction means the resulting reduction *slice* will be created in the fork's context. The user still reviews + approves the reduction slice's mission brief before any code changes — `--force` skips the audit confirmation, not the slice gate.

## Next step

- Audit only (no `--force`): user picks what to reduce → if any picked, proceed via `/slice`
- With `--force`: jump to `/slice "reduce: <summary>"` then through normal slice flow
