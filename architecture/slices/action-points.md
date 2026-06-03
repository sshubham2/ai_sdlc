# Cross-slice action points

A **bounded, curated** synthesis of the recurring, actionable patterns mined across the project's reflections. The **full per-slice lesson history lives in [`architecture/lessons-learned.md`](../lessons-learned.md)** — this file is NOT that store; it is the pattern-recognition input `/slice` + `/critique` + `/pulse` read instead of re-scanning 95 verbose summaries.

Each entry carries exactly one **promotion verdict**:
- `already-a-gate` — codified as an audit/rule; named here so reviewers know it's enforced.
- `build-check-candidate` — recurs; a `/reflect` Step 5b build-check or new audit would close the class.
- `critic-calibrate-probe` — a Critic blind-spot / calibration signal; feed `/critic-calibrate`.
- `cultural` — a discipline to hold, not (yet) mechanizable.

Bounded at ≤25 entries; enforced thin by `tools/index_router_thinness_audit.py` (ADR-093). Refresh this register when a new pattern crosses the N≥3 promotion threshold (a periodic synthesis, cadence akin to `/critic-calibrate`).

## Register

- **AP-1** [build-check-candidate] A control-token / marker detector must be **region-anchored**, never `marker in line_text` (whole-file substring scan) — false-positives on any descriptive mention (slices 099, 100; N=4).
- **AP-2** [critic-calibrate-probe] **A Critic's (or Builder's) own fix is a fresh claim** — the fix-delta recurses through every review layer; re-attack each applied fix, including on the classification-boundary axis (slices 089, 097, 100, 102, 103).
- **AP-3** [build-check-candidate] **APED-1**: execute a freshly-minted OR freshly-extended audit/parser/classifier against the REAL corpus + trace the ACTUAL call graph at build time — design-time reasoning (even dual-Critic-ratified) is not proof (slices 087, 091, 098, 100, 102).
- **AP-4** [critic-calibrate-probe] **The code-Critic is mandatory for a new AST/parser/classifier tool** — it catches silent-breakage false-negatives the design+meta stack structurally cannot reach (slices 088, 100).
- **AP-5** [cultural] **Prove a guard-test non-vacuous by mutation** — a passing test on already-correct inputs proves nothing; mutation also catches the Builder's OWN fix-regression live (slices 092, 094, 100, 101).
- **AP-6** [cultural] **Barrier-synchronize concurrency proofs** — un-barriered spawn workers start skewed and never contend, giving false-negative "0 loss"; only `mp.Barrier`-synchronized workers surface lost-updates (slice 094).
- **AP-7** [already-a-gate] **subprocess text capture must pass `encoding="utf-8"`** — Windows decodes git/tool UTF-8 output as cp1252 → `UnicodeDecodeError` swallowed in the reader thread → silent drop (slice 090; BC-GLOBAL-5; cp1252 class N=7).
- **AP-8** [already-a-gate] **Audit tool stdout must call `_stdout.reconfigure_stdout_utf8()`** first (UTF8-STDOUT-1) — non-ASCII `print()` crashes on cp1252 consoles (slices 007, 016, 018, 020, 021, 022, 023).
- **AP-9** [build-check-candidate] **Shell `>` redirection is NOT byte-safe** — PowerShell `>` = `Out-File` = UTF-16LE+BOM; capture binary/byte-exact data via a tool `--out-file`, never `>` (slice 097).
- **AP-10** [build-check-candidate] **A versioned test RENAME orphans every by-name citation; the count-literal fan-out is wider than any checklist** — before finishing a version bump, grep the OLD versioned-test name repo-wide AND every `"NN"` count literal (slices 094, 100).
- **AP-11** [build-check-candidate] **`.pyc` cache trap**: a byte-length-IDENTICAL source mutation after `git checkout` serves STALE mutated bytecode (`(mtime,size)` match) — clear `__pycache__`, use a byte-length-changing mutation, or `monkeypatch.setattr` instead of editing source (slice 101).
- **AP-12** [critic-calibrate-probe] **When a fix makes a fail-closed bucket go empty, ask: was the ambiguity RESOLVED or merely RE-ROUTED off the gate?** — moving an exit-2 sub-population into a non-gating class is a waiver, sound only if the downstream consumer is contractually required to process the new bucket (slice 102).
- **AP-13** [build-check-candidate] **Consumer-driven contract**: renaming/relocating a producer's published artifact orphans every by-name reader — enumerate + repoint ALL consumers in the same slice (slice 103 / M-add-1: a section rename left `/slice`+`/critique`+`/pulse` reading a vanished section).
- **AP-14** [build-check-candidate] **When a documented snippet glues two functions with mismatched types, pin the guarantee in the CONSUMER, not the prose** — prose carries no test; harden the called function to accept the real caller's shape (slice 104 / R-34: `read_git_config_user()` tuple → `record_pick(str)` emitted a tuple repr).
- **AP-15** [critic-calibrate-probe] **A guard deciding "is X applicable" must key on the structural property, not a cheap proxy** — store-LOCATION not per-file git-tracked-ness; both design-Critic AND meta-Critic ratified the unsound proxy, only EXECUTION found it (slice 098).
- **AP-16** [build-check-candidate] **A lexical audit's DETECTION verb-set and CLASSIFICATION verb-set must be a consistent pair** — a verb in the op-class set but not the detection set silently skips the site (slice 097; pin the detection⊇classification invariant).
- **AP-17** [already-a-gate] **Scope-narrowing in design.md MUST be back-propagated to mission-brief in the SAME fix block** (TPHD-1 sub-mode a) — leave nothing stale for `/critique` to catch (N=7: slices 062/064/067/070/071/072/073).
- **AP-18** [already-a-gate] **Every new audit rule propagates its consumer references into `architecture/shippability.md`** (RPCD-1/SCPD-1) — a new gate that isn't a shippability row can silently regress.
- **AP-19** [cultural] **Do NOT collapse the 3-Critic stack** — design-Critic (mission-brief/design/ADR prose) + meta-Critic (fix-delta + enumeration drift) + code-Critic (runtime/execution) catch non-overlapping defect classes; complementarity stable N≥13 (slices 063→102).
- **AP-20** [cultural] **Voluntary Critic on cross-cutting tooling slices pays off** — N=9/9 VALIDATED findings, zero false-alarms; methodology surfaces (`skills/*`, `tools/*`, `agents/*`) trigger mandatory Critic regardless of tier.
- **AP-21** [critic-calibrate-probe] **`/critic-calibrate` is overdue** — multiple calibration signals (TPHD-1 sub-mode-a Builder-fix-introduces-regression; the "Critic's own fix is a fresh claim" recursion; reader/writer asymmetry on rename slices) sit past the N≥3 promotion threshold; run the meta-pass.
- **AP-22** [cultural] **Forward-sync / content-equality audits are fragile under parallel version-bumping slices** (R-28, open) — a sibling slice forward-syncing the shared `~/.claude/` flips another slice's CAD-1/MCFS-1/AVFS-1/TVFS-1 to DRIFT; sequence version bumps or expect user-approved deferrals.
