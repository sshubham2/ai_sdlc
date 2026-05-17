# AI SDLC — Install Recipe

> **For Claude Code instances**: This file is a recipe you execute on the user's behalf.
> Read it end-to-end before starting. Be conversational. Show diffs before mutating shared
> files (global CLAUDE.md, settings.json). Ask only when truly ambiguous — don't ask about
> things you can detect.

## How a user invokes this

The user clones / downloads the AI SDLC source somewhere (any path), `cd`s into it, opens Claude Code, and says something like:

> "Install this. Read INSTALL.md and follow it."

That's it. You take it from there.

## What you're installing

The AI SDLC pipeline (methodology v0.20.0):
- **Drop-in skills** — copied to `~/.claude/skills/`
- **5 named subagents** — copied to `~/.claude/agents/`
- **4 templates** — copied to `~/.claude/templates/`
- **13 executable methodology tools** (audits, linters, validators) — installed as the `ai-sdlc-tools` Python package via `pip install`, so `$PY -m tools.<name>` resolves from `~/.claude/.venv/`
- **methodology-changelog.md + VERSION** — copied to `~/.claude/`
- Graphify integration + fork mode

Per **INST-1** (`methodology-changelog.md` v0.20.0): after install, the AI SDLC source folder can be deleted. The install is entirely self-contained under `~/.claude/` (skills, agents, templates, methodology metadata) and `~/.claude/.venv/lib/.../site-packages/tools/` (the audit tools). Nothing references the source folder at runtime.

After install, the user runs `/triage` (greenfield) or `/adopt` (brownfield) to start the workflow on any project.

## Step 0: Locate the source

The AI SDLC source directory contains this `INSTALL.md`, plus `skills/`, `agents/`, `templates/`, `README.md`, etc.

Default assumption: **the current working directory IS the source**. Verify by checking that `./skills/`, `./agents/`, `./templates/`, and `./INSTALL.md` all exist in CWD.

If they exist → bind `AI_SDLC_DIR="$(pwd)"` and proceed.

If CWD doesn't look like the AI SDLC source → ask the user: "I don't see `skills/`, `agents/`, and `templates/` in this directory — am I in the AI SDLC source dir? If not, please `cd` there or tell me the path."

Don't hardcode `~/ai_sdlc/` — users may have cloned the source anywhere.

## Step 1: Pre-flight detection (read-only)

Run a single bash block to detect current state. Show the output to the user before proceeding.

```bash
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) PY="$HOME/.claude/.venv/Scripts/python.exe"; PLATFORM=windows ;;
  Darwin)               PY="$HOME/.claude/.venv/bin/python";         PLATFORM=macos   ;;
  Linux)                PY="$HOME/.claude/.venv/bin/python";         PLATFORM=linux   ;;
esac

echo "Platform:        $PLATFORM"
echo "Claude dir:      $([ -d "$HOME/.claude" ] && echo exists || echo MISSING)"
echo "Venv:            $([ -f "$PY" ] && echo exists || echo MISSING) ($PY)"
echo "Python on PATH:  $(command -v python3 || command -v python || echo none)"
echo "Conda:           $(command -v conda >/dev/null && echo available || echo none)"
echo "Graphify:        $("$PY" -m graphify --help >/dev/null 2>&1 && echo installed || echo MISSING)"
echo "Settings.json:   $([ -f "$HOME/.claude/settings.json" ] && echo exists || echo MISSING)"
echo "Global CLAUDE.md: $([ -f "$HOME/.claude/CLAUDE.md" ] && echo exists || echo MISSING)"
echo "AI SDLC skills:  $(ls "$HOME/.claude/skills/" 2>/dev/null | grep -c '^\(triage\|adopt\|slice\|critique\|critique-review\|supersede-slice\)$' || echo 0)/6 canary skills already installed"
echo "AI SDLC agents:  $(ls "$HOME/.claude/agents/" 2>/dev/null | grep -c '^\(critique\|critic-calibrate\|critique-review\|diagnose-narrator\|field-recon\)\.md$' || echo 0)/5"
echo "AI SDLC templates: $(ls "$HOME/.claude/templates/" 2>/dev/null | grep -c '\.md$' || echo 0)/4 templates"
echo "ai-sdlc-tools:   $("$PY" -c 'import tools.build_checks_audit' 2>/dev/null && echo installed || echo MISSING)"
```

## Step 2: Resolve ambiguity

Ask the user only when needed:

- **No Python found**: "I don't see Python or conda. Install Python 3.11+ and re-run."
- **Both system Python and conda available, no venv yet**: ask which to use. Default to `python3 -m venv` if user has no preference.
- **Existing venv that doesn't have graphify**: confirm before installing into it.
- **Existing `~/.claude/CLAUDE.md` without the PY convention**: explain you'll append a `# Shared Python environment` section, show the exact text, get confirmation.
- **Existing `~/.claude/settings.json` with other keys but no `CLAUDE_CODE_FORK_SUBAGENT`**: read the file, show the user the planned merge (preserve all existing keys, add the env var to the env block), confirm.

Don't ask about things you can detect deterministically (paths, platform, etc.).

## Step 3: Execute install (idempotent)

Each step skips itself if already satisfied. Show the user what you're doing as you go.

### 3a: Venv

If `$PY` exists → skip.

Else: `python3 -m venv ~/.claude/.venv` (or conda equivalent if the user picked that). Then upgrade pip in the venv.

### 3b: Graphify

If `$PY -m graphify --help` works → skip.

Else: install from `~/.claude/packages/graphify/` (editable) if that path exists, otherwise `$PY -m pip install graphify`.

Verify: `$PY -m graphify --help` runs cleanly.

### 3c: Register graphify Claude Code skill

Run `$PY -m graphify install`. This creates `~/.claude/skills/graphify/SKILL.md`. Idempotent.

### 3d: Global CLAUDE.md — PY convention

Check `~/.claude/CLAUDE.md` for a `# Shared Python environment` heading. If present → skip.

Else: append this block (substitute actual paths). Show user first, get confirmation:

````
# Shared Python environment

Use `<VENV_PATH>` for any Python work — analysis, scripting, skill pipelines.
Do not create per-project venvs unless a project explicitly needs its own.

Never activate. Call the interpreter by absolute path:

```bash
PY=<PY_PATH>
$PY -m <package> <args>
```

Installed: `graphify` (queryable knowledge graph used by the AI SDLC pipeline).
````

`<VENV_PATH>` and `<PY_PATH>` should be in the OS-native form the user will see when running commands (Windows: `C:\Users\name\...`; Unix: `/home/name/...` or `~/.claude/...`).

### 3e: Settings.json — fork env var

Read `~/.claude/settings.json`. Use the **update-config skill** (which knows the schema and merge rules) — don't write JSON by hand.

Tell update-config: `set CLAUDE_CODE_FORK_SUBAGENT=1 in user settings (global)`.

If update-config isn't available in this session, manually merge: read existing JSON, add `"CLAUDE_CODE_FORK_SUBAGENT": "1"` to the `env` block (creating the block if absent), preserve all other keys.

### 3f: Copy AI SDLC skills + agents + templates + methodology files

```bash
mkdir -p ~/.claude/skills ~/.claude/agents ~/.claude/templates
cp -r "$AI_SDLC_DIR/skills/"* ~/.claude/skills/
cp -r "$AI_SDLC_DIR/agents/"* ~/.claude/agents/
cp -r "$AI_SDLC_DIR/templates/"* ~/.claude/templates/
cp "$AI_SDLC_DIR/methodology-changelog.md" ~/.claude/methodology-changelog.md
cp "$AI_SDLC_DIR/VERSION" ~/.claude/ai-sdlc-VERSION
```

Report counts: `N skills, M agents, K templates, methodology v<cat ~/.claude/ai-sdlc-VERSION>`.

Do NOT copy other root MDs (`README.md`, `pipeline.md`, `principles.md`, `tutorial.md`, `graphify-integration.md`, `INSTALL.md`, `plugin.yaml`, `pyproject.toml`) or `tutorial-site/` — those are project-source artifacts, not installed runtime files. The exceptions are `methodology-changelog.md` and `VERSION` (above) — those are runtime artifacts `/pulse` reads. Skills and agents must be self-contained; the templates are the only auxiliary markdown artifacts they reference. The executable tools (`tools/`) install via pip in Step 3g, NOT via cp.

### 3g: Install ai-sdlc-tools as a pip package

The 13 executable methodology tools (audit modules in `tools/`) ship as a proper Python package so `$PY -m tools.<name>` resolves from the shared venv's site-packages — source-independent. Per **INST-1**.

```bash
$PY -m pip install --upgrade "$AI_SDLC_DIR"
```

Important details:
- **NOT** `pip install -e` — editable installs leave the package pointing back at the source folder. Non-editable copies the package contents into site-packages.
- `--upgrade` ensures re-runs pick up new versions (idempotent: pip detects same-version no-op cleanly).
- The pyproject.toml at AI SDLC root declares only the `tools` package; skills/agents/templates/tests are explicitly excluded from the wheel.
- After this step, the user can `rm -rf "$AI_SDLC_DIR"` and `$PY -m tools.build_checks_audit` still works.

Verify the package landed:

```bash
$PY -c "import tools.build_checks_audit; print('ai-sdlc-tools OK')"
```

If the import fails with `ModuleNotFoundError`: the install didn't complete; check pip output. Common cause: `pyproject.toml` missing from `$AI_SDLC_DIR` (older source folder pre-v0.20.0 won't have it; tell the user to update the source).

## Step 4: Verify (the same preflight `/triage` and `/adopt` use)

```bash
test -f "$PY"                              && echo "venv: OK"     || echo "venv: FAIL"
"$PY" -m graphify --help >/dev/null 2>&1    && echo "graphify: OK" || echo "graphify: FAIL"
test -f "$HOME/.claude/agents/critique.md" && test -f "$HOME/.claude/agents/critic-calibrate.md" && test -f "$HOME/.claude/agents/critique-review.md" && test -f "$HOME/.claude/agents/diagnose-narrator.md" && test -f "$HOME/.claude/agents/field-recon.md" && echo "agents: OK (5/5)" || echo "agents: FAIL"
test -f "$HOME/.claude/skills/slice/SKILL.md" && test -f "$HOME/.claude/skills/critique-review/SKILL.md" && test -f "$HOME/.claude/skills/supersede-slice/SKILL.md" && echo "skills: OK (canary)" || echo "skills: FAIL"
test -f "$HOME/.claude/templates/mission-brief.md" && test -f "$HOME/.claude/templates/milestone.md" && echo "templates: OK" || echo "templates: FAIL"
test -f "$HOME/.claude/methodology-changelog.md" && test -f "$HOME/.claude/ai-sdlc-VERSION" && echo "methodology: OK (v$(cat $HOME/.claude/ai-sdlc-VERSION))" || echo "methodology: FAIL"
"$PY" -c "import tools.build_checks_audit, tools.wiring_matrix_audit, tools.cross_spec_parity_audit, tools.supersede_audit, tools.plugin_manifest_audit" 2>/dev/null && echo "ai-sdlc-tools: OK" || echo "ai-sdlc-tools: FAIL"
"$PY" -m tools.install_audit --claude-dir "$HOME/.claude" >/dev/null 2>&1 && echo "install-parity: OK" || echo "install-parity: FAIL (run with --json for details)"
```

All eight must say `OK`. If any `FAIL`: stop, show the user, do not claim success.

The `install-parity` line runs the **INST-1** install audit (`tools/install_audit.py`) — it cross-checks `~/.claude/` against the full canonical inventory of skills, agents, templates, methodology files, and importable tool modules. This catches partial installs (e.g., new skill in source but not yet copied; tools package upgraded but skill copy stale).

## Step 5: Hand off

Tell the user:

1. **Restart Claude Code** so the new env var (and any global CLAUDE.md changes) take effect.
2. After restart: `cd` into a project and run `/triage` (greenfield) or `/adopt` (brownfield).
3. Both opener skills run a preflight check on first use. If anything regresses (corrupted venv, deleted agent, etc.), they'll fail fast and point back at this install.

## What you should NOT do

- Do **not** install Python packages besides `graphify` without asking.
- Do **not** modify the user's global CLAUDE.md without showing the diff and getting confirmation.
- Do **not** touch unrelated skills/agents (e.g. `/docx`, `/pdf`, `/diagnose`, `/skill-creator`) — only the AI SDLC ones.
- Do **not** claim success if Step 4 has any FAIL.
- Do **not** assume the user wants `~/.claude/.venv` if they tell you a different path.

## Recovery — if the user re-runs this

This file is idempotent. If the user runs it again on a machine that's already configured, every step should detect "already done" and skip. The Step 4 verify still runs and confirms green. Tell the user "everything was already installed — you're ready" rather than re-doing work.

If Step 4 verify fails on a re-run (something got deleted or corrupted), repair only what's broken. Don't rebuild what's working.

## Source independence (INST-1)

After the install completes successfully, the AI SDLC source folder is no longer required at runtime. The user can:

- Move the source folder elsewhere
- Delete it (`rm -rf "$AI_SDLC_DIR"`)
- Keep multiple copies on different machines without re-syncing

Everything the runtime needs lives under:
- `~/.claude/skills/` — markdown skill files
- `~/.claude/agents/` — markdown agent files (5)
- `~/.claude/templates/` — markdown templates (4)
- `~/.claude/methodology-changelog.md`, `~/.claude/ai-sdlc-VERSION` — runtime metadata
- `~/.claude/.venv/Lib/site-packages/tools/` (or `lib/python*/site-packages/tools/` on Unix) — the executable methodology tools, installed via pip

To **update** to a newer methodology version, the user re-acquires the source (clone / pull / download) and re-runs INSTALL.md. Step 3g's `pip install --upgrade` overwrites the old tools package; Step 3f's `cp -r` overwrites the old skill / agent / template files; methodology-changelog and VERSION update in place.

If the user wants to verify current install state without the source, they can run:

```bash
$PY -m tools.install_audit --claude-dir ~/.claude
```

The audit reports any drift from the canonical inventory baked into v0.20.0. (Future versions update the canonical list.)
