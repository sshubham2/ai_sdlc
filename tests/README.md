# Methodology self-tests

Structural grep tests that verify load-bearing prose in skill and agent files hasn't drifted. Each test pins a canonical phrase from a SKILL.md or agent file; if a refactor paraphrases that phrase away, the test fails and the methodology rule is shown to have rotted.

## Why this exists

Rule **META-2** (`methodology-changelog.md` v0.2.0): every behavior-changing rule introduced in a slice must have a corresponding self-test that pins its prose. Without this, prose drifts silently — a Critic instructed to "be thoughtful" produces different work than one instructed to "assume the design is wrong until proven right."

## Setup

Tests use the shared Python venv at `~/.claude/.venv/` (per the user's CLAUDE.md convention). Install pytest there once:

```bash
# Windows
$HOME/.claude/.venv/Scripts/python.exe -m pip install pytest

# macOS / Linux
$HOME/.claude/.venv/bin/python -m pip install pytest
```

## Run

From the repo root:

```bash
# Windows
$HOME/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/ -v

# macOS / Linux
$HOME/.claude/.venv/bin/python -m pytest tests/methodology/ -v
```

## Adding tests for a new rule

When a slice introduces a new load-bearing rule (one that, if paraphrased away, would change AI behavior in a way that violates the rule's intent):

1. Pick the canonical phrase from the SKILL.md or agent file
2. Add a test in the appropriate `test_<area>.py` file (or create a new one)
3. Use this template:

```python
def test_<area>_<rule_name>():
    """<One-line description of what the rule enforces>.

    Defect class: <what bad behavior this prevents>
    Rule reference: <RULE-ID from methodology-changelog.md>
    """
    assert "<canonical phrase>" in <FILE_CONTENT_FIXTURE>
```

4. Add the rule entry to `methodology-changelog.md` referencing the test path

## CI hook (optional)

To run on every push and pull request, drop this at `.github/workflows/methodology-tests.yml`:

```yaml
name: Methodology self-tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pytest
      - run: pytest tests/methodology/ -v
```

The repo doesn't ship this file by default; CI is opt-in. The tests themselves run anywhere pytest does.

## What these tests do NOT cover

- Runtime behavior of skills (these are static prose checks)
- Whether the rules themselves are correct (that's `/critique`'s job)
- Whether load-bearing phrases are the *right* phrases (that's editorial judgment, captured in slice mission briefs)

If a phrase changes intentionally (e.g., a slice deliberately reword a rule), the test for it must be updated as part of that same slice — failing tests are the discipline that surfaces the change for review.
