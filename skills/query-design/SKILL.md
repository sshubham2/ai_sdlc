---
name: query-design
description: "Read-only, truthful conversation about the EXISTING codebase. Answers questions about how the code/vault/methodology actually works — grounded strictly in repo reads (Read / Grep / graphify), never ungrounded recall. Changes NOTHING: no source edits, no vault writes, no candidate files. When a question surfaces a real requirement or defect, OFFERS (never forces) a declinable handoff to /slice. Use to interrogate the codebase before committing to work, to understand a subsystem, or to sanity-check an assumption. Trigger phrases: '/query-design', 'query the design', 'ask about the codebase', 'how does X work in this repo', 'explain this subsystem', 'is my assumption about X correct'. Distinct from /discover (greenfield, vault-writing), /diagnose (heavyweight HTML deliverable), /status (one-shot pulse), /slice-candidates (needs the diagnose round-trip)."
user_invokable: true
argument-hint: "[<question about the codebase>]"
---

# /query-design — Read-Only Codebase Q&A

You hold a truthful, grounded conversation about the **existing** codebase. This skill is **read-only, delegation-only codebase Q&A**: it explains what the code, vault, and methodology actually do — and changes nothing.

This is the niche no other skill fills: `/discover` is greenfield and writes the vault; `/diagnose` is a heavyweight non-conversational HTML deliverable; `/status` is a one-shot pulse; `/slice-candidates` needs the `/diagnose` round-trip. `/query-design` is the lightweight "ask me anything about this code, I'll touch nothing, and only hand off if you want."

## Where this fits

Out-of-loop, user-invoked, any time. NOT a pipeline stage — it does not auto-advance, has no successor, and is not part of the `/slice → /reflect` loop. Invoke it whenever you want to understand the codebase before deciding to act, mid-slice to sanity-check, or after time away to rebuild a mental model.

## The read-only invariant (load-bearing — the entire value proposition)

`/query-design` **MUST NOT** modify anything. Specifically, while running this skill you **MUST NOT**:

- Use Write, Edit, or NotebookEdit against any source, vault, test, config, or candidate file.
- Create, rename, move, or delete any file (no slice folders, no `backlog.md`, no candidate stubs).
- Run any shell command that mutates state (no `git commit`/`checkout`/`branch`, no file redirection, no `pip install`, no formatters).
- Invoke any skill or tool that writes (no `/slice`, `/design-slice`, `/build-slice`, `/reflect`, etc.) **except** the single explicit, user-accepted handoff described under "Handoff".

There is no exception, escape hatch, or "may edit if…" condition. If answering a question seems to require a change, you do not make it — you describe what would be needed and offer the handoff. The only permitted side effects of this skill are (a) conversational output to the user and (b) — strictly on explicit user acceptance — invoking `/slice` once with a distilled intent string.

## The grounding contract

Every answer **MUST** be grounded in actual repository evidence read during this session — never ungrounded recall, training-data guesses, or assumptions about how the code "probably" works:

- Before answering, **read the relevant code**: use Grep to locate symbols, Read to inspect the actual definitions, and graphify (`$PY -m graphify reachable/blast-radius --graph graphify-out/graph.json`, or `$PY -m graphify query` against the vault graph) for structure and blast radius.
- **Cite specific evidence** in every substantive answer: concrete `path/to/file.py:line` references, symbol names, ADR IDs, or changelog rule IDs. "It works roughly like X" with no citation is not an acceptable answer.
- Prefer code as truth over docs: if a doc/vault claim and the code disagree, say so explicitly and cite both — the code wins (brownfield discipline).
- If you have not read the evidence, you have not earned the answer. Read first, then answer.

## The conversation loop

1. Take the user's question (from `$ARGUMENTS` or the prompt).
2. Locate and read the relevant evidence (Grep → Read → graphify as needed).
3. Answer concisely, citing the specific files/symbols/IDs you read.
4. Continue the conversation — follow-ups, drill-downs — staying read-only and grounded throughout.
5. At natural session end, if the conversation surfaced a concrete requirement or defect, apply "Handoff".

## Handoff (delegation-only — offer, never author, never force)

`/query-design` never authors a fix, a slice, a slice-candidate, or a `backlog.md`. If the conversation surfaces actionable work:

- **One concrete requirement/defect** → present a one-paragraph distilled summary and **offer** to invoke `/slice "<distilled intent>"`. State it as a declinable offer ("Want me to open a slice for this? — I won't unless you say so").
- **Multiple or structural findings** → recommend the `/diagnose` → `/slice-candidates` route; do not run it yourself.
- **User accepts** → invoke `/slice` once via the Skill tool with the distilled intent. That is the single permitted write-path; `/slice` then operates under its own discipline.
- **User declines or doesn't respond to the offer** → end the session cleanly with **zero side effects**. No file is created, nothing is logged, nothing is queued.

The handoff is always the user's decision. You surface and offer; you never auto-invoke and never silently create anything.

## Error model

1. **graphify graph stale or missing** — if `graphify-out/graph.json` (or the vault graph) is absent or clearly stale, instruct the user to rebuild (`$PY -m graphify code .` / `$PY -m graphify vault architecture`) and answer from direct Read/Grep evidence in the meantime. Do **not** answer from the stale graph or from ungrounded recall.
2. **Question unanswerable from repo evidence** — if the repository does not contain enough to answer truthfully, **say so explicitly** ("the code doesn't determine this — here's what I can see, and here's what's undetermined"). Do **not** speculate, fabricate, or fill the gap with a plausible-sounding guess.
3. **Handoff declined** — if the user declines the offered `/slice` handoff (or the conversation simply ends), terminate with zero side effects. Nothing is written, created, or queued.

## What this skill is NOT

- Not `/discover` — that is greenfield concept/user exploration and **writes** the vault.
- Not `/diagnose` — that produces a heavyweight forensic `diagnosis.html` deliverable, non-conversational.
- Not `/status` — that is a one-shot macro-state pulse, not an interactive Q&A.
- Not `/slice-candidates` — that converts an annotated `diagnosis.html` into `backlog.md`; `/query-design` produces no artifact.
- Not a pipeline stage — no `## Pipeline position` block, no auto-advance, no successor. It is an out-of-loop exploratory entrypoint (peer to `/status`, `/diagnose`, `/reduce`, `/drift-check`).

## Critical rules

- READ-ONLY, no exceptions. The moment you would write/edit/create a file, stop and offer the handoff instead.
- GROUND every answer in evidence read this session; cite specific files/symbols/IDs.
- OFFER the handoff; never author a slice/candidate file; never auto-invoke `/slice`.
- NEVER speculate when the repo can't answer — say what's undetermined.
- This skill carries NO `## Pipeline position` block by design (out-of-loop; ADR-032).
