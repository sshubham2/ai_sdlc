# Design: synthetic-fixture-for-utf8-stdout-regression

Synthetic fixture with U+2192 (`→`) and U+2014 (`—`) for cp1252 regression test.

## Wiring matrix

Per **WIRE-1**.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/fixtures/utf8_stdout/synthetic.py` | — | — | rationale: synthetic fixture file (not invoked); test infrastructure only — exempt per slice-018 convention |

Transition arrow → for U+2192 exercise.
