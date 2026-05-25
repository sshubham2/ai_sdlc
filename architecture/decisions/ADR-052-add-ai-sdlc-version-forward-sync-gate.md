---
id: ADR-052
title: Ship the ai-sdlc-VERSION forward-sync gate as a standalone MCFS-1 analogue, minting AVFS-1 via the ADR-051 4-part-bump path
date: 2026-05-19
slice: slice-050-add-ai-sdlc-version-forward-sync-gate
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-052: Standalone `ai-sdlc-VERSION` forward-sync gate (AVFS-1)

## Context

The PMI-1 atomic version bump has four legs: in-repo `VERSION`, installed
`~/.claude/ai-sdlc-VERSION`, `plugin.yaml.version`, and the forward-synced
`~/.claude/methodology-changelog.md`. Three legs have deterministic gates:
PMI-1 itself audits `VERSION`==`plugin.yaml`; MCFS-1 (slice-041) guards the
installed changelog leg. The installed `~/.claude/ai-sdlc-VERSION` leg has
**no deterministic gate** — PMI-1 never reads the installed file. It drifted
silently twice: slice-035 DEVIATION-2, and slice-048 (latent, surfaced only at
slice-049 when installed was `0.55.0` while in-repo `VERSION` was `0.56.0`).
slice-049's reflection + `_index.md` aggregated lessons twice flagged an
"MCFS-1-analogue gate for `ai-sdlc-VERSION`" as a strong next-slice candidate
with a known cheap fix-shape.

Two sub-decisions are needed: (1) standalone module vs fold the VERSION leg
into MCFS-1's whole-file gate; (2) whether minting this gate is a
methodology-surface behavior change requiring the 4-part PMI-1 bump.

## Options considered

1. **Standalone MCFS-1 analogue module** — a new
   `tools/ai_sdlc_version_forward_sync.py` cloned 1:1 from MCFS-1 with two path
   constants swapped. Pros: lowest blast radius (MCFS-1 untouched, its
   regression suite + the slice-041 R-4-retirement guarantees unperturbed);
   the clone is mechanically auditable against the proven precedent; cheap to
   delete if ever consolidated. Cons: two near-identical modules (mitigated by
   the CSP-1 comparator-parity pin and the verbatim-clone discipline).
2. **Fold into MCFS-1 as a combined whole-file multi-target gate** — extend
   `methodology_changelog_forward_sync.py` to also check `VERSION`. Pros: one
   module. Cons: changes a load-bearing slice-041 gate (R-4 retirement,
   m-add-1 relocation proof, the closed-world `_REGISTERED_INSTALLED_READERS`
   allowlist) — large blast radius for a 0.5-day cut; renames/repurposes a
   shipped audit; risks regressing the changelog-leg guarantee. Rejected for
   this slice (a future consolidation slice may revisit; recorded as
   out-of-scope in the mission brief).
3. **No new gate; keep the per-slice-manual M2 pre-sync-diff control** — the
   status quo. Rejected: it is exactly the human-dependent control that failed
   N=2; slice-049 explicitly nominated the gate.

On sub-decision (2): per **ADR-051** (slice-049 / Critic-B2 resolution), a
drift-guard / methodology-surface audit-gate addition whose slice has no
*other* bump reason **is itself a methodology-surface behavior change** — it
takes the minted-RULE-ID + `## vN.N.0` changelog entry + atomic 4-part PMI-1
bump + entry-pin path, NOT the slice-019/021 rode-an-existing-bump non-path.
This is binding precedent, not a fresh judgment.

## Decision

Ship a **standalone** `tools/ai_sdlc_version_forward_sync.py` as a verbatim
MCFS-1 structural clone (Option 1), retargeted to `VERSION` ↔
`~/.claude/ai-sdlc-VERSION`. Mint **AVFS-1** as a new NON-`-D` audit-gate
rule (refines nothing, supersedes nothing — the slice-044/STP-1 minting shape
is the format template) with a `methodology-changelog.md` `## v0.58.0` entry
and the atomic 4-part PMI-1 bump (`VERSION` + `~/.claude/ai-sdlc-VERSION` +
`plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`)
all `0.57.0 → 0.58.0` in lockstep, a **content-bearing** in-repo-only
`test_v_0_58_0_avfs_1_entry_present_in_repo` entry-pin (asserts `AVFS-1`,
`ADR-052`, `supersedes nothing`, the canonical attribution phrase, and the
standalone-not-folded decision — STP-1/MCFS-1 depth, not a thin presence
check; B1), and a shippability catalog row #50 (verified next-free: max
existing row = #49) carrying the in-repo-only entry-pin + consumer-propagation
pin ONLY. The comparator is the verbatim MCFS-1 `_normalized_bytes` — CRLF→LF
only, NOT trailing-whitespace/newline tolerant (B3), preserving the CSP-1
parity to `_normalized_sha256`.

Wiring is the MCFS-1 2-point shape: `/build-slice` Step 6 pre-finish (ungated,
every slice) + a dedicated `/reflect` post-write step (NOT folded into the
rule-promotion-gated Step 5b).

## Consequences

- The 4th PMI-1 leg gains a deterministic downstream gate; the per-slice-manual
  M2 pre-sync-diff control is retired as the sole protection.
- This slice self-applies, but the bootstrap is **conditional and weaker than
  MCFS-1's** (M1): at slice-050's own Step 6 in-repo `VERSION` is `0.58.0`, so
  AVFS-1 exits 0 ONLY IF this slice's own 4-part PMI-1 bump correctly
  forward-synced installed `~/.claude/ai-sdlc-VERSION` → `0.58.0`. That leg is
  precisely the N=2-drift-prone manual step AVFS-1 exists to gate (unlike
  MCFS-1, whose changelog leg is reliably forward-synced every recent slice).
  Therefore a **non-zero AVFS-1 at slice-050's own Step 6 is the EXPECTED
  signal to perform/repair the installed-VERSION forward-sync — NOT a slice
  defect**; re-run until exit 0. The mid-slice smoke (`0.57.0==0.57.0`) tests
  the pre-bump state only and is not a Step-6 self-application proxy. The
  pre-finish gate carries an explicit "manually verify installed == 0.58.0
  before the AVFS-1 Step-6 run" line. Every slice after 050 inherits a
  self-gating AVFS-1 (which from slice-051 onward behaves exactly like MCFS-1's
  bootstrap, since the bump leg is then a routine part of any version-bumping
  slice).
- `skills/build-slice/SKILL.md` (OSDG-1/mini-CAD-guarded) and
  `skills/reflect/SKILL.md` gain wiring blocks; their installed copies must be
  forward-synced in the same fix block.
- Two near-identical forward-sync modules now exist; the CSP-1 comparator
  behaviour-parity pin keeps them from silently diverging. A future
  consolidation into one multi-target gate remains open (out of scope here).
- AVFS-1's regression suite reads the **untracked, environment-mutable**
  installed copy → it is non-catalog because a shippability `Machine-cmd` must
  not depend on environment-mutable/untracked state (slice-029/030A
  discipline). The MCFS-1 m-add-2/`essential-unregistered` mechanism does NOT
  transfer (M3, recomputed): `_ESSENTIAL_SHAPES` keys on
  `~/.claude/methodology-changelog.md` only
  (`tools/shippability_decoupling_audit.py:95-97`); `classify_fn` classifies
  other `~/.claude/...` reads as `clean`. Only the two in-repo-only
  `test_methodology_changelog.py` pins carry row #50.

## Reversibility

**cheap.** The gate is one self-contained module + two SKILL.md prose blocks +
one changelog entry + one ADR + catalog row #50. Reversal (per SUP-1 — ADRs
are append-only, never deleted): delete the module + its tests, revert the two
SKILL.md prose blocks + the v0.58.0 changelog entry + catalog row #50, and
supersede ADR-052 via a new ADR. No data model, no contract consumer, no
irreversible lock — the version-bump *convention* it guards already existed;
this only makes a pre-existing manual invariant deterministic. The
RULE-ID/version mint follows the established slice-044 convention and carries
no novel commitment.
